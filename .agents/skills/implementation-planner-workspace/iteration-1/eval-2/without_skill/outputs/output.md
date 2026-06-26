# C-AS-05 §5 — `fetch_secret` Contract: Implementation-Unit Breakdown

**Source contract:** `design-substrate/Spec_Action_Surface_v1.md` §5 C-AS-05 — `fetch_secret(name, scope) -> SecretRef` signature.
**Scope:** §5.1 function signature; §5.2 tier-aware resolution; §5.3 negative-observation invariant; §5.4 `SecretRef` opaque-type discipline.
**Stack:** Python 3.12+, Pydantic v2, `asyncio`, `pytest` + `pytest-asyncio` per `Target_Stack_Commitment_v1.md`.

This breakdown decomposes C-AS-05 §5 into four atomic implementation units along the contract's four sub-section seams. Each unit is independently testable, has a clean rollback boundary, and traces back to specific spec sub-sections.

---

## Dependency graph

```
U-FS-1 (signature + opaque type)   ──┬──> U-FS-2 (tier-aware resolution)
                                     ├──> U-FS-3 (negative-observation invariants)
                                     └──> U-FS-4 (SecretRef lifetime discipline)
```

`U-FS-1` is the foundational unit; the other three depend only on it and may be implemented in parallel after it lands. Topological order: `U-FS-1` → {`U-FS-2`, `U-FS-3`, `U-FS-4`}.

---

## U-FS-1 — Declare `fetch_secret` signature, `SecretScope`, and `SecretRef` opaque type

**Implements:** C-AS-05 §5.1 (function signature); §5.4 row 1 (opaque-type, no value-accessor).

**Depends on:** Sandbox-tier enum (`SandboxTier`, 4-tier, from C-AS-01) — assumed present.

**Inputs:** Secret identifier `name: str`; `scope: SecretScope`; resolved sandbox tier at call site.

**Files affected (logical):** `secret-fetch-type-declarations`; `secret-fetch-api-surface`.

**Signatures:**

```
class SecretScope(BaseModel):        # Pydantic v2; credential-dimension session key
    ...                              # serialization format deferred to impl discretion

class SecretRef:                     # opaque handle — NO method returning the value as str
    ...                              # value reached only via tier-specific resolution (U-FS-2)

def fetch_secret(name: str, scope: SecretScope) -> SecretRef
```

**Acceptance criteria:**
1. `fetch_secret(name, scope)` signature matches §5.1 verbatim — `name: str`, `scope: SecretScope`, returns `SecretRef`. (The runtime `tier` argument is injected by the sandbox call site, not part of the public §5.1 surface.)
2. `name` is treated as structure-not-content metadata — the value is fetched opaquely, never embedded in the `name`.
3. `SecretRef` exposes **no** API surface that returns the secret value as a string (§5.4 row 1). Verified by introspection: no public attribute or method yields a `str`-typed secret value.
4. `SecretScope` is a distinct type from ADR-F1's routing-dimension session key — credential-dimension is orthogonal (§5.1 table row 2).

**Tests:**
- `test_fetch_secret_signature_matches_spec_5_1`
- `test_secret_ref_has_no_value_accessor_api`
- `test_secret_scope_distinct_from_routing_session_key`
- `test_fetch_secret_returns_secret_ref_instance`

**Rollback boundary:** Revert `SecretScope` + `SecretRef` + `fetch_secret` declarations. All other C-AS-05 units lose their foundational surface; the secrets subsystem is invalidated.

---

## U-FS-2 — Tier-aware resolution mechanism table + resolution dispatch

**Implements:** C-AS-05 §5.2 (tier-aware resolution; 4-row table; T-perm-2 pole expression).

**Depends on:** U-FS-1.

**Inputs:** Resolved `SandboxTier` for the call site; `SecretRef` from `fetch_secret`.

**Files affected (logical):** `tier-aware-secret-resolution-table`; `secret-resolution-dispatch`.

**Signatures:**

```
class TPerm2Pole(Enum):              # C2_WITHIN_TURN_SNAPSHOT | C3_ACROSS_TURN_FRESH_FETCH
class SecretResolutionMechanism(Enum):
    ENV_VAR_AT_SANDBOX_STARTUP
    CONTAINER_ENV_VAR_WITH_KEYRING_HANDLES
    IN_SANDBOX_HTTP_BOOTSTRAP_TOKEN
    IN_SANDBOX_HTTP_WITH_ROTATION_REFRESH

class TierResolution(BaseModel):
    tier: SandboxTier
    mechanism: SecretResolutionMechanism
    pole: TPerm2Pole

TIER_RESOLUTION_TABLE: tuple[TierResolution, ...]   # exactly 4 entries

def resolution_for(tier: SandboxTier) -> TierResolution
```

**Acceptance criteria:**
1. `TIER_RESOLUTION_TABLE` has exactly 4 entries, one per sandbox tier, matching §5.2 row-by-row:
   - `tier-1-process` → `ENV_VAR_AT_SANDBOX_STARTUP` → pole `C2`
   - `tier-2-container` → `CONTAINER_ENV_VAR_WITH_KEYRING_HANDLES` → pole `C2`
   - `tier-3-microvm` → `IN_SANDBOX_HTTP_BOOTSTRAP_TOKEN` → pole `C3`
   - `tier-4-full-vm` → `IN_SANDBOX_HTTP_WITH_ROTATION_REFRESH` → pole `C3`
2. `resolution_for` is total over `SandboxTier` — every tier resolves.
3. Both T-perm-2 poles are expressed across the table (C2 by tiers 1-2; C3 by tiers 3-4). Tier choice picks the pole; closure is structural composition with F4, not a C2-vs-C3 choice (§5.2 closing note).
4. tier-4-full-vm resolution is rotation-aware: refresh within sandbox lifetime is supported by the mechanism.

**Tests:**
- `test_tier_resolution_table_cardinality_four`
- `test_tier_resolution_mechanism_per_spec_row_by_row`
- `test_tier_1_and_2_express_c2_pole`
- `test_tier_3_and_4_express_c3_pole`
- `test_resolution_for_total_over_sandbox_tier`
- `test_tier_4_mechanism_is_rotation_aware`

**Rollback boundary:** Revert the resolution table + dispatch. `fetch_secret` from U-FS-1 still type-checks but cannot resolve a value at any tier; downstream sandbox tiers fall back to no-secret operation.

**Deferred to implementation discretion** (per §5.4): specific keyring-library binding (`python-keyring`); in-sandbox HTTP client implementation (tiers 3-4); bootstrap-token issuance protocol (AWS STS / Vault wrapped / GCP Workload Identity); `pass`/`gpg` headless fallback.

---

## U-FS-3 — Negative-observation invariant enforcement

**Implements:** C-AS-05 §5.3 (absence in prompts, logs, ledger; sole-resolution-path).

**Depends on:** U-FS-1.

**Inputs:** Prompt-cache static prefix; OTel span attributes; audit-ledger entry; secret-arrival site descriptor.

**Files affected (logical):** `secret-negative-observation-validator`; `secret-sole-resolution-path-guard`.

**Signatures:**

```
class NegativeObservationViolation(BaseModel): ...

def validate_no_secret_in_static_prefix(prefix: str) -> NegativeObservationViolation | None
def validate_no_secret_in_span_attributes(attrs: Mapping) -> NegativeObservationViolation | None
def validate_no_secret_in_audit_ledger_entry(entry) -> NegativeObservationViolation | None
def verify_sole_resolution_path(arrival_site) -> NegativeObservationViolation | None
```

**Acceptance criteria:**
1. Secret values are rejected from the static prompt-cache prefix — cache-prefix integrity per ADR-F2 §Rationale (b)(ii) preserved (§5.3 row 1).
2. Secret values are rejected from span attributes / log records / any observability content-attribute capture surface; composes with the C-AS-15 `SENSITIVE_DATA_EXCLUSIONS` set (§5.3 row 2).
3. Secret values are rejected from audit-ledger entries; only the structure-not-content fingerprint per C-AS-08 may appear (§5.3 row 3).
4. `verify_sole_resolution_path` confirms `fetch_secret` is the **only** path by which a secret reaches a sandbox; arrival via manifest, prompt, log, or ledger is reported as a contract violation (§5.3 row 4).
5. Each validator returns `None` on a clean input and a populated `NegativeObservationViolation` on a dirty one.

**Tests:**
- `test_static_prefix_rejects_secret_value`
- `test_static_prefix_accepts_clean_prefix`
- `test_span_attributes_validator_composes_with_sensitive_data_exclusions`
- `test_audit_ledger_entry_rejects_secret_value`
- `test_sole_resolution_path_rejects_manifest_arrival`
- `test_sole_resolution_path_accepts_fetch_secret_arrival`

**Rollback boundary:** Revert the validators + sole-resolution guard. Secrets handling loses structural prohibition at prompt/log/ledger surfaces; manifest and static-prefix secret leakage become silently permitted; compliance posture (Persona §10.4) breaks.

---

## U-FS-4 — `SecretRef` lifetime + fresh-on-restart discipline

**Implements:** C-AS-05 §5.4 rows 2-3 (lifetime-bounded; fresh-on-restart; no in-process cache).

**Depends on:** U-FS-1.

**Inputs:** `SecretRef` instances; sandbox lifecycle events (start, terminate); resumption events per ADR-F3.

**Files affected (logical):** `secret-ref-lifetime-manager`; `secret-ref-restart-guard`.

**Signatures:**

```
def bind_to_sandbox(ref: SecretRef, sandbox_id: str) -> None
def release_on_sandbox_termination(sandbox_id: str) -> None
def assert_no_cross_sandbox_use(ref: SecretRef, sandbox_id: str) -> None
def test_fetch_on_resumption(scope: SecretScope) -> bool   # per ADR-F3 resumption events
```

**Acceptance criteria:**
1. Every `SecretRef` is bound to exactly one sandbox; its lifetime is bounded by that sandbox's lifetime (§5.4 row 2).
2. On sandbox termination, every bound `SecretRef` is released; subsequent use raises (§5.4 row 2).
3. Cross-sandbox `SecretRef` sharing is prohibited — use of a ref bound to sandbox A inside sandbox B is rejected (§5.4 row 2).
4. No in-process secret cache survives a restart boundary; on resumption a fresh test-fetch is performed per ADR-F3 resumption events, per ADR-F5 v1.1 §Consequences (b) (§5.4 row 3).

**Tests:**
- `test_secret_ref_bound_to_single_sandbox`
- `test_secret_ref_released_on_sandbox_termination`
- `test_secret_ref_use_after_release_raises`
- `test_secret_ref_no_cross_sandbox_sharing`
- `test_no_in_process_secret_cache_across_restart`
- `test_fetch_on_resumption_per_adr_f3`

**Rollback boundary:** Revert the lifetime manager + restart guard. `SecretRef` instances may outlive their sandbox or leak across sandboxes; stale secret material may survive a restart. U-FS-1's opaque type still holds, but its lifetime guarantees are unenforced.

---

## Traceability summary

| Unit | Spec sub-section(s) | Contract surface |
|---|---|---|
| U-FS-1 | §5.1, §5.4 row 1 | function signature + opaque type |
| U-FS-2 | §5.2 | tier-aware resolution table + dispatch |
| U-FS-3 | §5.3 | negative-observation invariants |
| U-FS-4 | §5.4 rows 2-3 | `SecretRef` lifetime + fresh-on-restart |

All four sub-sections of C-AS-05 §5 are covered with no gaps. PRD requirement R-AS-04 (secret content never present in stored prompts or logs — fetch abstraction half) is satisfied jointly by U-FS-3 (negative observation) and U-FS-1/U-FS-2 (opaque fetch abstraction). ADR-F5 v1.1 T-perm-2 closure is satisfied by U-FS-2 (both poles expressed).

**Note on existing plan alignment:** the canonical AS plan (`Implementation_Plan_Action_Surface_v1.md` §2.5 Cluster 5) already decomposes C-AS-05 into U-AS-20 (signature + opaque type + tier table) and U-AS-21 (negative-observation invariants). This breakdown splits along the same contract seams but at finer granularity — U-AS-20 here is further factored into U-FS-1 / U-FS-2 / U-FS-4, isolating the tier-resolution table and the `SecretRef` lifetime discipline as independently rollback-able units.
