"""Provider SDK lifecycle — stage 3a CP_CLIENTS (U-RT-17/18/19/20).

Per `Spec_Harness_Runtime_v1.md` v1.1 §5 (C-RT-05) and Phase 2 Session 3
Track A plan v2.1 §L4. The runtime owns construction, lifetime, and close
of three async provider clients (`anthropic.AsyncAnthropic`,
`openai.AsyncOpenAI`, `ollama.AsyncClient`) wrapped behind the
`ProviderClient` Protocol (concretized at U-RT-17).

Spec §5 line 346: "Runtime wraps each in a thin adapter (per-provider module
under `harness_runtime/lifecycle/providers.py`) so all three satisfy
`ProviderClient.aclose()` uniformly. Adapters are runtime-defined; the
Protocol is the canonical contract."

Per-unit landing posture:
- **U-RT-17** (this commit): `AnthropicAdapter` + `construct_anthropic_adapter`
  + the typed fail-mode taxonomy (`ProviderSecretMissingError`,
  `ProviderAuthError`, `ProviderTransientError`,
  `ProviderDegradedWarning`).
- **U-RT-18**: `OpenAIAdapter` + `construct_openai_adapter`.
- **U-RT-19**: `OllamaAdapter` + `construct_ollama_adapter` (with the
  `RT-FAIL-PROVIDER-DEGRADED` branch when `ollama_optional=True`) +
  `materialize_provider_clients_stage` aggregating the three.
- **U-RT-20**: capability-aware binding (engine-class → providers lookup)
  consuming `harness_cp.engine_class_candidate.ENGINE_CLASS_CANDIDATES`.

Ping-mechanism injection. Per the spec §5 line 373 "Deferred to
implementation discretion" — async ping mechanism is a callable injected on
the adapter rather than a hard-wired SDK method call. This (a) keeps unit
tests free of live network calls (matches the workspace convention of
pyright-strict-clean fakes; see `test_lifecycle_mcp_host.py`) and (b)
isolates the ping surface from per-SDK version drift. Operator-driven
integration tests bind real SDK methods (`client.models.list()` for
Anthropic/OpenAI, `client.list()` for Ollama).

Idempotent close. Per C-RT-05 §5 line 343 (`aclose()` docstring "Idempotent")
+ C-RT-10 reverse-shutdown contract: every adapter tracks a `_closed` flag
and short-circuits subsequent `aclose()` calls. The underlying SDK's
`close()` is invoked exactly once.

Failure-mode taxonomy (spec §5 lines 367-371):

| Adapter exception                | RT-FAIL-* spec class                |
|----------------------------------|-------------------------------------|
| `ProviderSecretMissingError`     | `RT-FAIL-SECRET-MISSING` (permanent)|
| `ProviderTransientError`         | `RT-FAIL-TRANSIENT`     (transient) |
| `ProviderAuthError`              | `RT-FAIL-PROVIDER-AUTH` (permanent) |
| `ProviderDegradedWarning`        | `RT-FAIL-PROVIDER-DEGRADED` (deg.)  |

Bounded-retry policy (max 3 per stage policy per spec line 369) is wired by
the stage-3a materialize function (U-RT-19) which sits above the adapter
construction calls — adapters themselves raise once and let the materialize
loop decide retry vs. escalation.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Final

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from harness_runtime.config.provider_secrets import (
    KeyringSecretResolver,
    SecretResolutionError,
)
from harness_runtime.types import ProviderClient, RuntimeConfig

__all__ = [
    "ANTHROPIC_KEYRING_NAME",
    "OPENAI_KEYRING_NAME",
    "AnthropicAdapter",
    "OpenAIAdapter",
    "ProviderAuthError",
    "ProviderDegradedWarning",
    "ProviderSecretMissingError",
    "ProviderTransientError",
    "construct_anthropic_adapter",
    "construct_openai_adapter",
]


# ---------------------------------------------------------------------------
# Keyring entry names (per spec §5 lines 352-353; bootstrap-only lookup).
# ---------------------------------------------------------------------------
ANTHROPIC_KEYRING_NAME: Final[str] = "anthropic_key"
"""Keyring entry name for the Anthropic API key per spec §5 line 352
(`AsyncAnthropic(api_key=keyring_resolve('anthropic_key'), ...)`)."""

OPENAI_KEYRING_NAME: Final[str] = "openai_key"
"""Keyring entry name for the OpenAI API key per spec §5 line 353
(`AsyncOpenAI(api_key=keyring_resolve('openai_key'), ...)`)."""


# ---------------------------------------------------------------------------
# Typed exceptions — one per spec §5 fail-mode row.
# ---------------------------------------------------------------------------
class ProviderSecretMissingError(Exception):
    """Stage-3a `RT-FAIL-SECRET-MISSING` (permanent; spec §5 line 368).

    Raised when a provider-required keyring entry is absent. Carries the
    provider identity per "Construction errors surface as stage 3a failure
    with provider identity attached" (spec §5 line 360).
    """

    def __init__(self, provider: str, keyring_name: str) -> None:
        super().__init__(f"provider={provider!r}: keyring entry {keyring_name!r} not found")
        self.provider = provider
        self.keyring_name = keyring_name


class ProviderTransientError(Exception):
    """Stage-3a `RT-FAIL-TRANSIENT` (transient; spec §5 line 369).

    Raised when the adapter's async ping fails with a network-ish error.
    The stage-3a materialize loop (U-RT-19) bounds retry at 3 attempts;
    persistent transient → escalate to `ProviderAuthError` or
    `ProviderTransientError` re-raised as permanent.
    """

    def __init__(self, provider: str, cause: BaseException) -> None:
        super().__init__(f"provider={provider!r}: transient ping failure: {cause}")
        self.provider = provider
        self.cause = cause


class ProviderAuthError(Exception):
    """Stage-3a `RT-FAIL-PROVIDER-AUTH` (permanent; spec §5 line 370).

    Raised when the adapter's async ping fails with an auth-class error
    (401 / 403). No retry; surface typed and naming the provider.
    """

    def __init__(self, provider: str, cause: BaseException) -> None:
        super().__init__(f"provider={provider!r}: auth failure: {cause}")
        self.provider = provider
        self.cause = cause


class ProviderDegradedWarning(Warning):
    """Stage-3a `RT-FAIL-PROVIDER-DEGRADED` (degraded; spec §5 line 371).

    Surfaced (not raised) when Ollama is unreachable AND
    `RuntimeConfig.ollama_optional == True`. The materialize loop logs this
    and continues with a 2-provider context per the spec's "stage continues
    with 2-provider context" disposition. Wired at U-RT-19; declared at
    U-RT-17 to keep the fail-mode taxonomy in one place.
    """

    def __init__(self, provider: str, cause: BaseException) -> None:
        super().__init__(f"provider={provider!r}: degraded (unreachable): {cause}")
        self.provider = provider
        self.cause = cause


# ---------------------------------------------------------------------------
# AnthropicAdapter — U-RT-17.
# ---------------------------------------------------------------------------
# Type aliases for the ping-callable surface. The async ping returns `None`
# on success; on failure it raises an exception that the adapter classifies
# as transient vs. auth. Keeping the callable generic across providers lets
# tests inject deterministic fakes without monkeypatching SDK internals.
AsyncPing = Callable[[], Awaitable[None]]


def _default_anthropic_ping(client: AsyncAnthropic) -> AsyncPing:
    """Build the default ping callable for an `AsyncAnthropic` client.

    Uses `client.models.list()` per spec §5 line 373 suggestion ("low-cost
    `count_tokens` or model-list call per provider"). The default ping is
    only invoked when the operator does not inject a custom one — tests
    always inject; production code paths use this default.
    """

    async def ping() -> None:
        await client.models.list()

    return ping


@dataclass
class AnthropicAdapter:
    """Stage-3a Anthropic adapter — U-RT-17.

    Wraps an `anthropic.AsyncAnthropic` client behind the `ProviderClient`
    Protocol. Holds the client + a ping callable + a `_closed` flag for
    idempotent `aclose()`.

    Not frozen (vs. the L3 dataclass pattern) because `_closed` is mutated
    on shutdown. The instance handle is immutable post-construction except
    for the close-flag transition.
    """

    client: AsyncAnthropic
    ping: AsyncPing
    _closed: bool = field(default=False)

    async def aclose(self) -> None:
        """Idempotent close. Calls `client.close()` exactly once."""
        if self._closed:
            return
        self._closed = True
        await self.client.close()


def _classify_anthropic_ping_failure(exc: BaseException) -> Exception:
    """Map a ping-call exception to the typed fail class.

    Anthropic SDK raises `anthropic.AuthenticationError` (401) and
    `anthropic.PermissionDeniedError` (403) for auth failures, both
    subclasses of `anthropic.APIStatusError`. Network errors raise
    `anthropic.APIConnectionError`. Anything else is treated as transient
    (the stage-3a retry loop will re-attempt; persistent → permanent).

    Import is local so the import cost is paid once per construction call,
    not at module load time, and so the classifier is testable with
    fakes that mimic the auth-class duck shape.
    """
    # Local import: avoids paying the cost at module load (consistent
    # with the workspace convention of lazy-importing SDK error classes).
    from anthropic import AuthenticationError, PermissionDeniedError

    if isinstance(exc, AuthenticationError | PermissionDeniedError):
        return ProviderAuthError("anthropic", exc)
    return ProviderTransientError("anthropic", exc)


async def construct_anthropic_adapter(
    config: RuntimeConfig,
    resolver: KeyringSecretResolver,
    *,
    ping_override: AsyncPing | None = None,
    client_factory: Callable[[str], AsyncAnthropic] | None = None,
) -> AnthropicAdapter:
    """Construct + ping-verify an `AnthropicAdapter` for stage 3a.

    Steps:
    1. Resolve the Anthropic API key via the keyring (bootstrap path).
    2. Construct `AsyncAnthropic(api_key=...)`.
    3. Invoke the (injected or default) async ping. Auth-class exception →
       `ProviderAuthError`; anything else → `ProviderTransientError`.
    4. Return the adapter; caller (materialize loop, U-RT-19) decides retry
       vs. escalate on transient failure.

    Parameters
    ----------
    config :
        Frozen `RuntimeConfig`. Not consumed here (Anthropic SDK construction
        needs only the API key) but kept on the signature for symmetry with
        `construct_openai_adapter` / `construct_ollama_adapter` (U-RT-18/19,
        which read `ollama_host` / `ollama_optional`).
    resolver :
        `KeyringSecretResolver` built at stage 0 PREAMBLE (U-RT-06).
        Provides the bootstrap-only `resolve_bootstrap_value` path.
    ping_override :
        Test-injection point. When `None`, the default ping calls
        `client.models.list()`. Tests pass a deterministic awaitable.
    client_factory :
        Test-injection point for the SDK constructor. When `None`, calls
        `AsyncAnthropic(api_key=key)`. Tests pass a fake that records the
        key + returns a stub satisfying the close-method shape.

    Returns
    -------
    AnthropicAdapter
        Ready adapter; `_closed=False`; ping has succeeded.

    Raises
    ------
    ProviderSecretMissingError
        Keyring lookup for `anthropic_key` returned `None`.
    ProviderAuthError
        Ping raised an Anthropic auth-class error.
    ProviderTransientError
        Ping raised any other exception (network, timeout, unexpected).
    """
    # `config` is accepted for cross-adapter signature symmetry (U-RT-18/19
    # read fields from it). Anthropic itself needs only the API key.
    _ = config
    try:
        api_key = resolver.resolve_bootstrap_value(ANTHROPIC_KEYRING_NAME)
    except SecretResolutionError as exc:
        raise ProviderSecretMissingError("anthropic", ANTHROPIC_KEYRING_NAME) from exc

    if client_factory is None:
        client = AsyncAnthropic(api_key=api_key)
    else:
        client = client_factory(api_key)

    ping = ping_override if ping_override is not None else _default_anthropic_ping(client)
    try:
        await ping()
    except (ProviderAuthError, ProviderTransientError):
        # Already typed — propagate. (Allows test-injected ping callables
        # to raise the typed errors directly without re-classification.)
        raise
    except BaseException as exc:
        raise _classify_anthropic_ping_failure(exc) from exc

    return AnthropicAdapter(client=client, ping=ping)


# Protocol conformance assertion — surfaces at module load time. If the
# AnthropicAdapter ever drifts from the `ProviderClient` shape, mypy /
# pyright will flag the assignment line below.
_ANTHROPIC_PROTOCOL_CHECK: type[ProviderClient] = AnthropicAdapter
del _ANTHROPIC_PROTOCOL_CHECK


# ---------------------------------------------------------------------------
# OpenAIAdapter — U-RT-18.
# Same shape as AnthropicAdapter. Per-SDK error-class import is local to the
# classifier so the import cost is paid once per construction call. OpenAI's
# AuthenticationError + PermissionDeniedError share the same APIStatusError
# parent as Anthropic's; the classification logic is symmetric.
# ---------------------------------------------------------------------------


def _default_openai_ping(client: AsyncOpenAI) -> AsyncPing:
    """Build the default ping callable for an `AsyncOpenAI` client.

    Uses `client.models.list()` per spec §5 line 373 suggestion. Symmetric
    with `_default_anthropic_ping`.
    """

    async def ping() -> None:
        await client.models.list()

    return ping


@dataclass
class OpenAIAdapter:
    """Stage-3a OpenAI adapter — U-RT-18.

    Wraps an `openai.AsyncOpenAI` client behind the `ProviderClient` Protocol.
    Same idempotent-close discipline as `AnthropicAdapter`.
    """

    client: AsyncOpenAI
    ping: AsyncPing
    _closed: bool = field(default=False)

    async def aclose(self) -> None:
        """Idempotent close. Calls `client.close()` exactly once."""
        if self._closed:
            return
        self._closed = True
        await self.client.close()


def _classify_openai_ping_failure(exc: BaseException) -> Exception:
    """Map an OpenAI ping exception to the typed fail class.

    OpenAI SDK raises `openai.AuthenticationError` (401) and
    `openai.PermissionDeniedError` (403) for auth failures. Network errors
    raise `openai.APIConnectionError`. Symmetric with Anthropic classifier.
    """
    from openai import AuthenticationError, PermissionDeniedError

    if isinstance(exc, AuthenticationError | PermissionDeniedError):
        return ProviderAuthError("openai", exc)
    return ProviderTransientError("openai", exc)


async def construct_openai_adapter(
    config: RuntimeConfig,
    resolver: KeyringSecretResolver,
    *,
    ping_override: AsyncPing | None = None,
    client_factory: Callable[[str], AsyncOpenAI] | None = None,
) -> OpenAIAdapter:
    """Construct + ping-verify an `OpenAIAdapter` for stage 3a.

    Steps + parameters + fail-mode contract mirror `construct_anthropic_adapter`
    — see that function's docstring for the canonical narrative. The only
    per-provider variance is the keyring name (`openai_key`), the SDK class
    (`AsyncOpenAI`), and the error-class set the classifier checks.

    Raises
    ------
    ProviderSecretMissingError
        Keyring lookup for `openai_key` returned `None`.
    ProviderAuthError
        Ping raised an OpenAI auth-class error.
    ProviderTransientError
        Ping raised any other exception.
    """
    _ = config
    try:
        api_key = resolver.resolve_bootstrap_value(OPENAI_KEYRING_NAME)
    except SecretResolutionError as exc:
        raise ProviderSecretMissingError("openai", OPENAI_KEYRING_NAME) from exc

    if client_factory is None:
        client = AsyncOpenAI(api_key=api_key)
    else:
        client = client_factory(api_key)

    ping = ping_override if ping_override is not None else _default_openai_ping(client)
    try:
        await ping()
    except (ProviderAuthError, ProviderTransientError):
        raise
    except BaseException as exc:
        raise _classify_openai_ping_failure(exc) from exc

    return OpenAIAdapter(client=client, ping=ping)


_OPENAI_PROTOCOL_CHECK: type[ProviderClient] = OpenAIAdapter
del _OPENAI_PROTOCOL_CHECK
