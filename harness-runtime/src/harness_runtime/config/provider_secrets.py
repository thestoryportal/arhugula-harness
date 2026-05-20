"""U-RT-06 — keyring-backed secret resolver driver.

Per `Spec_Harness_Runtime_v1.md` v1.1 §3 (C-RT-03 `provider_secrets` field)
and Phase 2 Session 3 plan v2.1 §2 L1, this module:

- Provides the typed runtime-side secret resolver bound to `python-keyring`.
- Enforces C-AS-06 §6.2 allowlist intersection when a `ToolContract` is
  supplied at fetch time.
- Maps keyring misses to typed `SecretResolutionError` carrying the C-AS-07
  `SecretFailClass` for downstream C5/C9 routing.

Implementation-discretion choices (per AS spec C-AS-05 §5.4):
- Keyring library: `python-keyring` (committed at `Target_Stack_Commitment_v1`
  §5.1 + ADR-F5 v1.1).
- Service-name discipline: configured at `ProviderSecretsConfig.keyring_service`;
  default `"harness"`.
- `secret_unknown` (keyring miss) → permanent C5 / no-retry C9 per C-AS-07
  §7.1 row 1 (`SECRET_UNKNOWN` → `PERMANENT_FAIL` / `NO_RETRY_ROUTE_TO_HITL`).

Audit-event composition (`SecretFetchEvent`) lives at the FETCH CALL SITE
(per U-AS-26 separation), not in this driver. The driver returns `SecretRef`
on success; the caller composes the audit event with its `actor` / `timestamp`
/ `thread_id` / `step_id` context and routes through the IS state-ledger
writer once that lands (L2+ wiring at U-RT-12 / U-RT-32).

NOT in scope for U-RT-06 (deferred):
- Tier-aware resolution mechanism (`SecretResolutionMechanism` per
  C-AS-05 §5.2). The keyring path is the LOCAL_DEVELOPMENT /
  SELF_HOSTED_SERVER tier mechanism; MANAGED_CLOUD tiers use the in-sandbox
  HTTP bootstrap-token mechanism per AS spec §5.2 row 4, wired at L4
  (U-RT-17..U-RT-20) when provider clients exist.
- Per-backend breaker placement (C-AS-07 §7.3). Wired at U-RT-24
  (retry/breaker registry).
"""

from __future__ import annotations

from dataclasses import dataclass

import keyring
from harness_as.sandbox_tier import SandboxTier
from harness_as.secret_allowlist import AllowlistDecision, check_secret_allowlist
from harness_as.secret_fail_class import SecretFailClass
from harness_as.secret_fetch import SecretRef, SecretScope
from harness_as.tool_contract import ToolContract

from harness_runtime.types import ProviderSecretsConfig

__all__ = [
    "KeyringSecretResolver",
    "SecretAllowlistDeniedError",
    "SecretResolutionError",
    "make_keyring_resolver",
]


class SecretResolutionError(Exception):
    """Raised when keyring resolution fails. Carries the C-AS-07 fail class."""

    def __init__(self, fail_class: SecretFailClass, name: str) -> None:
        super().__init__(f"{fail_class.value}: {name}")
        self.fail_class = fail_class
        self.name = name


class SecretAllowlistDeniedError(Exception):
    """Raised when the allowlist intersection denies the request (C-AS-06 §6.2)."""

    def __init__(self, decision: AllowlistDecision, name: str, scope: SecretScope) -> None:
        super().__init__(f"{decision.value}: name={name!r} scope={scope.name!r}")
        self.decision = decision
        self.name = name
        self.scope = scope


@dataclass(frozen=True)
class KeyringSecretResolver:
    """Runtime keyring-backed secret resolver.

    Construct via `make_keyring_resolver(config)`. The resolver is frozen
    (dataclass `frozen=True`); reconfiguration requires building a new
    instance from an updated `ProviderSecretsConfig`.
    """

    keyring_service: str
    operator_allowlist: frozenset[object]
    """Stored as `frozenset[object]` to dodge `SecretAllowlistEntry` hashability
    fragility (Pydantic v2 frozen models are hashable only with `frozen=True`
    AND no mutable fields); the set is consumed by `check_secret_allowlist`
    which casts via `set(...)` internally.

    NOTE: at L1 the operator-allowlist intersection is exercised through the
    AS-landed `check_secret_allowlist` function; this driver does not
    re-implement allowlist semantics."""

    def resolve(
        self,
        name: str,
        scope: SecretScope,
        tier: SandboxTier,
        *,
        tool: ToolContract | None = None,
    ) -> SecretRef:
        """Resolve a secret reference; raises on miss or allowlist denial.

        Parameters
        ----------
        name :
            The secret identifier (per `SecretRef.name`).
        scope :
            Credential-dimension session key.
        tier :
            Sandbox tier of the call site (lifetime-bound anchor).
        tool :
            Tool contract for allowlist intersection (C-AS-06 §6.2). When
            `None`, allowlist intersection is skipped — used by runtime
            self-tests + bootstrap-only fetches before tools are registered.

        Returns
        -------
        SecretRef
            Opaque handle bound to `(name, scope, tier)`.

        Raises
        ------
        SecretAllowlistDeniedError
            Tool was provided AND intersection denied the request.
        SecretResolutionError
            Keyring returned `None` for `(keyring_service, name)`.
        """
        if tool is not None:
            decision = check_secret_allowlist(
                tool=tool,
                requested_name=name,
                requested_scope=scope,
                operator_policy_override=self.operator_allowlist,  # type: ignore[arg-type]
            )
            if decision is not AllowlistDecision.PERMITTED:
                raise SecretAllowlistDeniedError(decision, name, scope)

        value = keyring.get_password(self.keyring_service, name)
        if value is None:
            raise SecretResolutionError(SecretFailClass.SECRET_UNKNOWN, name)

        return SecretRef(name=name, scope=scope, tier=tier)


def make_keyring_resolver(config: ProviderSecretsConfig) -> KeyringSecretResolver:
    """Build a `KeyringSecretResolver` from a `ProviderSecretsConfig`."""
    return KeyringSecretResolver(
        keyring_service=config.keyring_service,
        operator_allowlist=frozenset(config.operator_allowlist),
    )
