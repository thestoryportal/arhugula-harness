# Binding fix: `KeyringSecretResolver` env-var fallback for headless modes

**Status:** ✅ APPLIED 2026-05-28 at PR #16 (commit `f374747`). Operator AskUserQuestion ratified §3 (a)-(e) + §4 production binding + §5 tests. Verified at HEAD: `_KEYRING_TO_ENV_VAR` mapping + `_lookup()` helper present at `harness-runtime/src/harness_runtime/config/provider_secrets.py:58-126`; both `resolve()` (`:173`) and `resolve_bootstrap_value()` (`:212`) route through `_lookup`; all 6 §5 tests at `harness-runtime/tests/test_config_provider_secrets.py`; daemon e2e un-skipped behind `ANTHROPIC_API_KEY` env gate at `test_cli_daemon.py:296`. Status refresh at workflow §7.4.7.3.B audit 2026-05-31 (sub-species 3 `resolved-but-carry-stale-inherited`).

**Original status (preserved for lineage):** PROPOSING 2026-05-28 — fork-doc-only commit lands first; impl gated on operator AskUserQuestion ratify-and-apply per workspace discipline.

**Shape:** Binding fix + discretion record. NOT a Class 1 fork — ADR-F5 v1.1 §(b)(i) already canonicalizes env-var fallback at "Headless modes use `pass` / `gpg` or environment-pre-seeded values where a user session is unavailable." Production binding catches up to spec authority. Mirrors `[[tenant-id-binding-lift-cp-v1-22]]` precedent (advisor pre-substantive consultation foreclosed Class 1 ceremony).

---

## 1. The gap

`harness-runtime/src/harness_runtime/config/provider_secrets.py:141 + :180` (both `resolve` and `resolve_bootstrap_value`) call `keyring.get_password(self.keyring_service, name)` with **no env-var fallback**. When the keyring returns `None`:

- `SecretResolutionError(SecretFailClass.SECRET_UNKNOWN, name)` raises.
- At stage 3a CP_CLIENTS, this surfaces as `ProviderSecretMissingError` per `lifecycle/providers.py:330 + :440`.
- With `anthropic_optional=True` + `openai_optional=True` + `ollama_optional=True`, every provider degrades → `ProviderNoneConfiguredError` per `lifecycle/providers.py:762`.

Operators with `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` already exported (the canonical vendor convention) cannot run the harness without first authoring a keyring entry. This blocks:

- `harness-runtime/tests/test_cli_daemon.py::test_ac1_e2e_daemon_subprocess_binds_socket_and_shuts_down` (currently skipped).
- Subprocess variants of mech-α AC #5 (SIGINT drain) + AC #6 (daemon-concurrent).
- Production daemon mode for operators without keyring entries.

## 2. Authority

ADR-F5 v1.1 §Decision is explicit at process tier: "process tier within-turn-snapshot via **env vars at startup**" — env-var sourcing is the blessed shape at this tier.

ADR-F5 v1.1 §(b)(i) headless-mode framing: "Headless modes use `pass` / `gpg` or **environment-pre-seeded values** where a user session is unavailable."

When keyring returns `None` the operator IS effectively in headless mode for that secret. Keyring-first-env-fallback approximates the §(b)(i) framing structurally.

## 3. Discretion choices recorded

| # | Choice | Rationale |
|---|---|---|
| (a) | **Vendor-canonical env var naming** — `ANTHROPIC_API_KEY` for `"anthropic_key"`, `OPENAI_API_KEY` for `"openai_key"` | What operators already have set (twelve-factor + vendor SDK conventions). ADR-F5 §(b)(i) does not name the variable; this records the choice. |
| (b) | **Keyring-first, env-var fallback** | Preserves keyring as primary trust anchor per ADR-F5 LOCAL_DEV tier. Env-var only when keyring returns `None`. |
| (c) | **Ollama N/A** — no env-var lookup for Ollama | Ollama is credential-less per `providers.py:466-470`. `OLLAMA_API_KEY` is not a real convention. `ollama_optional` already handles the surface per `[[fork-provider-construction-allowlist-semantic]]`. |
| (d) | **Both `resolve()` and `resolve_bootstrap_value()` get the fallback** | Symmetric. Allowlist intersection at `resolve()` still gates regardless of secret-source (allowlist is access control, orthogonal to source). |
| (e) | **Mapping centralized at resolver** | `_KEYRING_TO_ENV_VAR: dict[str, str] = {"anthropic_key": "ANTHROPIC_API_KEY", "openai_key": "OPENAI_API_KEY"}`. Names without env-var mapping (future non-provider secrets) fall through to keyring-only — backward-compatible at all call sites. |

## 4. Production binding

```python
_KEYRING_TO_ENV_VAR: dict[str, str] = {
    "anthropic_key": "ANTHROPIC_API_KEY",
    "openai_key": "OPENAI_API_KEY",
}


def _lookup(self, name: str) -> str | None:
    """Keyring-first lookup with env-var fallback per ADR-F5 v1.1 §(b)(i)."""
    value = keyring.get_password(self.keyring_service, name)
    if value is not None:
        return value
    env_var = _KEYRING_TO_ENV_VAR.get(name)
    if env_var is not None:
        return os.environ.get(env_var)
    return None
```

Both `resolve()` and `resolve_bootstrap_value()` use `self._lookup(name)` instead of `keyring.get_password(...)` directly.

## 5. Tests

- `test_resolve_bootstrap_value_falls_back_to_env_var_when_keyring_returns_none` — anthropic path
- `test_resolve_bootstrap_value_env_var_openai` — openai path
- `test_resolve_bootstrap_value_keyring_wins_over_env_var` — precedence verification
- `test_resolve_bootstrap_value_no_mapping_no_fallback` — unmapped name preserves prior behavior
- `test_resolve_env_var_fallback_honors_allowlist` — allowlist still gates env-sourced secrets
- `test_resolve_bootstrap_value_neither_keyring_nor_env_raises` — SecretResolutionError still raised when both absent

Daemon e2e test `test_ac1_e2e_daemon_subprocess_binds_socket_and_shuts_down` un-skipped behind `@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"))` gate matching mech-β precedent. `anthropic_optional=False` in the fixture exercises the env-fallback at stage 3a.

## 6. Scope discipline

- **NO new keyring names.** `"anthropic_key"` / `"openai_key"` are the only mapped names; mapping is closed at this arc.
- **NO ADR-F5 spec amendment.** v1.1 §(b)(i) is canonical authority unchanged.
- **NO new fail class.** `SECRET_UNKNOWN` covers "neither keyring nor env" identically.
- **NO new audit-ledger attribute.** `secret.backend` discriminator could distinguish source per ADR-F5 Consequences (a), but ADR-F5 explicitly DEFERS the span schema to D-ADR (C7 owner); not in this arc's scope.
- **NO ADR-F2 git-boundary impact.** Env vars are out-of-git by convention; same as keyring.

## 7. Adjacent observations

(a) `secret.backend` discriminator at the OTel span could distinguish `keyring` vs `env` per ADR-F5 v1.1 §Consequences (a); deferred to C7 OTel D-ADR per ADR-F5 §(c).

(b) Linux `pass` / `gpg` headless modes per ADR-F5 §(b)(i) NOT wired at this arc; future RT D-ADR if/when needed.

(c) Non-provider secrets (general `resolve()` call with `tool=...` allowlist) have no env-var mapping at this arc; falls through to keyring-only. Future per-tool secrets could either extend the map or be intentionally keyring-only (operator authoring discipline at production tier).

## 8. Cross-axis cascade

ZERO — verified via grep at `design-substrate/`. Intra-runtime-axis binding fix.

## 9. Status posture

Per workspace discipline (operator AskUserQuestion 2026-05-28):
- **Fork doc shape:** binding-fix discretion record, not Class 1.
- **Apply now or wait:** TBD at operator ratify pass.
- **Impl scope:** sections 4 + 5 above (resolver mapping + 6 tests + daemon e2e un-skip).
