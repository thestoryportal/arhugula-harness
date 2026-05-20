"""U-RT-17 — `AnthropicAdapter` + `construct_anthropic_adapter` tests.

ACs per Phase 2 Session 3 Track A plan v2.1 §L4 U-RT-17:
- Client constructs (with resolved secret).
- Async ping succeeds; close idempotent and awaitable.
- Structural conformance to `ProviderClient` Protocol.

Failure modes (spec §5 lines 367-371) — covered:
- `RT-FAIL-SECRET-MISSING` → `ProviderSecretMissingError`.
- `RT-FAIL-TRANSIENT`      → `ProviderTransientError`.
- `RT-FAIL-PROVIDER-AUTH`  → `ProviderAuthError`.

Test convention notes:
- No live network calls. The SDK constructor and the async ping are both
  injected per the workspace pyright-strict-clean fake convention; matches
  `test_lifecycle_mcp_host.py` (placeholder primitive, no real FastMCP).
- The `_FakeKeyring` backend fixture is duplicated from
  `test_config_provider_secrets.py` to keep test modules self-contained.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path
from typing import cast

import keyring
import pytest
from anthropic import (
    APIConnectionError,
    AsyncAnthropic,
    AuthenticationError,
)
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.topology_pattern import TopologyPattern
from harness_runtime.config.provider_secrets import (
    KeyringSecretResolver,
    make_keyring_resolver,
)
from harness_runtime.lifecycle.providers import (
    ANTHROPIC_KEYRING_NAME,
    AnthropicAdapter,
    ProviderAuthError,
    ProviderSecretMissingError,
    ProviderTransientError,
    construct_anthropic_adapter,
)
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderClient,
    ProviderSecretsConfig,
    RuntimeConfig,
)
from keyring.backend import KeyringBackend

# ---------------------------------------------------------------------------
# Lightweight subclasses that satisfy `isinstance(exc, AuthenticationError)`
# / `isinstance(exc, APIConnectionError)` without going through the SDK's
# heavyweight `__init__` (which expects a real `httpx.Response` /
# `httpx.Request`). The adapter only does an isinstance check.
# ---------------------------------------------------------------------------


class _FakeAuthError(AuthenticationError):
    def __init__(self, message: str = "fake 401") -> None:
        Exception.__init__(self, message)


class _FakeConnectionError(APIConnectionError):
    def __init__(self, message: str = "fake connection refused") -> None:
        Exception.__init__(self, message)


# ---------------------------------------------------------------------------
# Fixtures — in-memory keyring + minimal RuntimeConfig.
# ---------------------------------------------------------------------------


class _FakeKeyring(KeyringBackend):
    """In-memory keyring backend (mirrors `test_config_provider_secrets.py`)."""

    priority = 1  # type: ignore[assignment]

    def __init__(self) -> None:
        self.store: dict[tuple[str, str], str] = {}

    def get_password(self, service: str, username: str) -> str | None:
        return self.store.get((service, username))

    def set_password(self, service: str, username: str, password: str) -> None:
        self.store[(service, username)] = password

    def delete_password(self, service: str, username: str) -> None:
        self.store.pop((service, username), None)


@pytest.fixture
def fake_keyring() -> Iterator[_FakeKeyring]:
    """Install an in-memory keyring for the duration of one test."""
    backend = _FakeKeyring()
    original = keyring.get_keyring()
    keyring.set_keyring(backend)
    try:
        yield backend
    finally:
        keyring.set_keyring(original)


def _runtime_config(tmp_path: Path) -> RuntimeConfig:
    """Minimal `RuntimeConfig` for adapter-construction tests.

    Adapter construction at U-RT-17 doesn't consume `config` beyond
    signature symmetry; the value is only meaningful at U-RT-18/19 (Ollama
    host + optional flag). Built here so the U-RT-17 test signature
    matches what U-RT-18/19 will exercise.
    """
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )


def _resolver_with_anthropic_key(value: str = "sk-ant-fake-test") -> KeyringSecretResolver:
    """Seed a keyring entry for `anthropic_key` and return a resolver.

    Caller must hold the `fake_keyring` fixture so the backend is installed.
    """
    keyring.set_password("harness", ANTHROPIC_KEYRING_NAME, value)
    return make_keyring_resolver(ProviderSecretsConfig())


# ---------------------------------------------------------------------------
# Fake SDK client — minimal surface to satisfy adapter construction + close.
# ---------------------------------------------------------------------------


class _FakeAsyncAnthropic:
    """Fake `AsyncAnthropic` for tests; records construction + close-count.

    Surfaces only the `.close()` coroutine the adapter calls. The ping is
    injected separately via `ping_override`, so this fake doesn't need
    `.models.list()`.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.close_count = 0

    async def close(self) -> None:
        self.close_count += 1


def _factory(records: list[str]) -> Callable[[str], AsyncAnthropic]:
    """Build a `client_factory` callable that records the api_key it receives.

    Returns an `AsyncAnthropic`-typed object via `cast` to satisfy the
    `client_factory: Callable[[str], AsyncAnthropic]` parameter type. The
    real `AsyncAnthropic` is duck-equivalent at the `.close()` call site,
    which is all the adapter uses post-construction at U-RT-17.
    """

    def factory(api_key: str) -> AsyncAnthropic:
        records.append(api_key)
        return cast(AsyncAnthropic, _FakeAsyncAnthropic(api_key=api_key))

    return factory


# ---------------------------------------------------------------------------
# Happy path: construct + ping + idempotent close.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_construct_anthropic_adapter_happy_path(
    fake_keyring: _FakeKeyring, tmp_path: Path
) -> None:
    """End-to-end happy path: secret resolves → client constructs → ping passes."""
    resolver = _resolver_with_anthropic_key("sk-ant-happy")
    config = _runtime_config(tmp_path)
    captured_keys: list[str] = []
    ping_call_count = 0

    async def stub_ping() -> None:
        nonlocal ping_call_count
        ping_call_count += 1

    adapter = await construct_anthropic_adapter(
        config,
        resolver,
        ping_override=stub_ping,
        client_factory=_factory(captured_keys),  # type: ignore[arg-type]
    )

    assert isinstance(adapter, AnthropicAdapter)
    assert captured_keys == ["sk-ant-happy"]
    assert ping_call_count == 1


@pytest.mark.asyncio
async def test_anthropic_adapter_aclose_is_idempotent(
    fake_keyring: _FakeKeyring, tmp_path: Path
) -> None:
    """`aclose()` calls SDK `close()` exactly once even on repeated invocation."""
    resolver = _resolver_with_anthropic_key()
    config = _runtime_config(tmp_path)

    async def stub_ping() -> None:
        return None

    captured: list[str] = []
    adapter = await construct_anthropic_adapter(
        config,
        resolver,
        ping_override=stub_ping,
        client_factory=_factory(captured),  # type: ignore[arg-type]
    )

    # The fake client tracks close_count; downcast via the captured handle.
    fake_client = cast(_FakeAsyncAnthropic, adapter.client)
    assert fake_client.close_count == 0
    await adapter.aclose()
    assert fake_client.close_count == 1
    await adapter.aclose()  # idempotent
    await adapter.aclose()  # idempotent
    assert fake_client.close_count == 1


# ---------------------------------------------------------------------------
# Protocol conformance.
# ---------------------------------------------------------------------------


def test_anthropic_adapter_satisfies_provider_client_protocol(
    fake_keyring: _FakeKeyring,
) -> None:
    """`AnthropicAdapter` structurally satisfies `ProviderClient` (runtime check).

    Per C-RT-05 v1.1 `@runtime_checkable` Protocol — `isinstance(..., ProviderClient)`
    must be True for every adapter.
    """

    async def noop_ping() -> None:
        return None

    fake = cast(AsyncAnthropic, _FakeAsyncAnthropic(api_key="x"))
    adapter = AnthropicAdapter(client=fake, ping=noop_ping)
    assert isinstance(adapter, ProviderClient)


# ---------------------------------------------------------------------------
# Failure modes.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_missing_secret_raises_provider_secret_missing(
    fake_keyring: _FakeKeyring, tmp_path: Path
) -> None:
    """No `anthropic_key` in keyring → `ProviderSecretMissingError`."""
    # Note: do NOT seed the keyring.
    resolver = make_keyring_resolver(ProviderSecretsConfig())
    config = _runtime_config(tmp_path)

    async def unreached_ping() -> None:  # pragma: no cover — must not be invoked
        raise AssertionError("ping should not run when secret is missing")

    with pytest.raises(ProviderSecretMissingError) as excinfo:
        await construct_anthropic_adapter(
            config,
            resolver,
            ping_override=unreached_ping,
            client_factory=_factory([]),  # type: ignore[arg-type]
        )
    assert excinfo.value.provider == "anthropic"
    assert excinfo.value.keyring_name == ANTHROPIC_KEYRING_NAME


@pytest.mark.asyncio
async def test_ping_auth_failure_raises_provider_auth_error(
    fake_keyring: _FakeKeyring, tmp_path: Path
) -> None:
    """Anthropic `AuthenticationError` from ping → `ProviderAuthError` (permanent)."""
    resolver = _resolver_with_anthropic_key()
    config = _runtime_config(tmp_path)

    async def failing_ping() -> None:
        raise _FakeAuthError()

    with pytest.raises(ProviderAuthError) as excinfo:
        await construct_anthropic_adapter(
            config,
            resolver,
            ping_override=failing_ping,
            client_factory=_factory([]),  # type: ignore[arg-type]
        )
    assert excinfo.value.provider == "anthropic"


@pytest.mark.asyncio
async def test_ping_transient_failure_raises_provider_transient(
    fake_keyring: _FakeKeyring, tmp_path: Path
) -> None:
    """Connection error from ping → `ProviderTransientError` (bounded retry upstream)."""
    resolver = _resolver_with_anthropic_key()
    config = _runtime_config(tmp_path)

    async def failing_ping() -> None:
        raise _FakeConnectionError()

    with pytest.raises(ProviderTransientError) as excinfo:
        await construct_anthropic_adapter(
            config,
            resolver,
            ping_override=failing_ping,
            client_factory=_factory([]),  # type: ignore[arg-type]
        )
    assert excinfo.value.provider == "anthropic"


@pytest.mark.asyncio
async def test_ping_typed_error_propagates_unwrapped(
    fake_keyring: _FakeKeyring, tmp_path: Path
) -> None:
    """A ping that already raises `ProviderAuthError` is propagated as-is.

    Lets test-injected pings raise the typed exceptions directly without the
    adapter re-classifying them — keeps the test surface symmetric with how
    a future retry-loop wrapper might already-classified failures.
    """
    resolver = _resolver_with_anthropic_key()
    config = _runtime_config(tmp_path)
    original = ProviderAuthError("anthropic", RuntimeError("pre-classified"))

    async def already_typed_ping() -> None:
        raise original

    with pytest.raises(ProviderAuthError) as excinfo:
        await construct_anthropic_adapter(
            config,
            resolver,
            ping_override=already_typed_ping,
            client_factory=_factory([]),  # type: ignore[arg-type]
        )
    assert excinfo.value is original
