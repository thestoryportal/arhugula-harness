# Spec: Control Plane — v1.89 (delta over v1.88)

*Delta-only file. The v1.88 body + the entire C-CP-01 … C-CP-29 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). This delta records the B-18-3C-PREWARM-DEFAULT-ON bundled-absorption arc: flipping `WorkflowManifestEntry.concurrent_cache_warmup` default from `False` to `True` per ADR-D4 §1.8(f) "required at fan-out cap > 1," now safe because the `CohortKeyCapable` dispatcher-oracle (v1.88 §25.16) provides machine-checkable cacheability attestation.*

## Change-note (v1.88 → v1.89)

**What this materializes.** ADR-D4 §1.8(f) states: *"Concurrent-prompt-cache warm-up protocol is required at fan-out cap > 1."* The v1.87/v1.88 implementation shipped with `concurrent_cache_warmup: bool = False` (opt-in) pending the `CohortKeyCapable` dispatcher-oracle that would make the default flip safe. B-18-3C-PREWARM-COHORTKEY (v1.88) delivered that oracle. B-18-3C-PREWARM-DEFAULT-ON flips the default from `False` to `True` at the user-facing manifest layer, fulfilling the ADR requirement.

**Safety argument.** The flip is safe because `_same_prefix_cohort()` is now machine-attested:

- A dispatcher that does NOT implement `CohortKeyCapable` → predicate returns False → `_warmup_gate=False` → all-concurrent baseline, byte-identical to the pre-flip state.
- A `CohortKeyCapable` dispatcher returning `None` from `cohort_key()` (memory_runtime bound, frozen_tool_superset absent, or any unstable condition) → predicate returns False → same all-concurrent baseline.
- Warmup fires ONLY when every branch dispatcher is `CohortKeyCapable` AND every branch returns the same non-None cohort key.

**Scope of revision.**

**§25.17 (NEW) — Default-on discipline for `concurrent_cache_warmup`:**

The `WorkflowManifestEntry` field changes from `concurrent_cache_warmup: bool = False` to `concurrent_cache_warmup: bool = True`. The TOML/YAML manifest schema carrier (`_WorkflowSection` in `workflow_manifest_loader.py`) mirrors this change: an absent `concurrent_cache_warmup` key in a manifest file now defaults to `True` (rather than `False`).

The `D4MultiplicativeTunable.concurrent_cache_warmup` field default and the `d4_tunable()` factory parameter default are UNCHANGED at `False`. These are internal resolved-value holders threaded from the WME via `d4_tunable(..., concurrent_cache_warmup=manifest_entry.concurrent_cache_warmup)`. Non-PARALLELIZATION topology strategies call `d4_tunable()` without specifying `concurrent_cache_warmup` and correctly inherit the function-parameter default of `False` (warmup is irrelevant outside PARALLELIZATION).

**Explicit opt-out.** Operators may set `concurrent_cache_warmup: false` in their manifest TOML/YAML to disable warmup for a specific workflow. This is the mechanism for opting out when a non-`CohortKeyCapable` dispatcher is intentionally used and the operator prefers the all-concurrent baseline regardless of future dispatcher upgrades.

**Manifest round-trip.** An absent `concurrent_cache_warmup` key in an existing manifest file now enables warmup (via `_WorkflowSection` Pydantic default) rather than disabling it. For manifests consumed by workflows with non-`CohortKeyCapable` dispatchers, this is byte-identical at the executor level — the `_same_prefix_cohort()` predicate gate prevents any behavioral change.

**`D4MultiplicativeTunable` default note.** The `D4MultiplicativeTunable` model-level default remains `False`. This default is load-bearing ONLY for direct construction without the `d4_tunable()` factory, which does not occur in production paths. The `d4_tunable()` function parameter default `False` correctly serves non-PARALLELIZATION callers that omit the argument.

**Invariants preserved.** NO §5.2 IS-hash change. NO new contract / ADR / enum / fail-class / CXA edge. The field-level flip is an additive-optional default change per the §6.1 "additional per-workload fields" extension clause (mirrors v1.20 `default_gate_level`, v1.63 `fanout_timeout_disposition`, v1.87 `concurrent_cache_warmup` additive-optional precedents). Existing manifests with explicit `concurrent_cache_warmup: true/false` are unaffected. The behavior change is gated entirely behind the `CohortKeyCapable` predicate.

**New witnesses.** Three test additions:

- `test_workflow_manifest_entry_default_concurrent_cache_warmup_is_true` — verifies WME default is True with no explicit setting (harness-cp/tests/test_workflow_manifest_entry.py)
- `test_workflow_manifest_entry_accepts_explicit_opt_out` — verifies explicit `False` is accepted (same file)
- `test_optional_field_absent_uses_pydantic_carrier_default` — updated assertion: `concurrent_cache_warmup is True` when absent from manifest (harness-runtime/tests/test_workflow_manifest_loader.py)
- `test_warmup_default_on_live_cache_hit` — @pytest.mark.e2e skipif skeleton gated on ANTHROPIC_API_KEY; documents future cache-instrumented live acceptance path (harness-cp/tests/test_workflow_driver_parallelization_warmup.py)

**Registered follow-ons (SPINE `B-*`) — updated status.**

| Follow-on | Scope | Status |
|---|---|---|
| `B-18-3C-PREWARM-COHORTKEY` | Dispatcher-oracle `CohortKeyCapable` Protocol | **CLOSED** (v1.88) |
| `B-18-3C-PREWARM-DEFAULT-ON` | Flip to required-at-cap>1 per ADR §1.8(f) | **CLOSED** (this arc) |
| `B-18-3C-PREWARM-CASCADE` | warm-up on CASCADE_CANCEL + PAUSE paths | Registered, open |
| `B-18-EPOCH-PARTITION` | version_sha cohort HASH + heterogeneous partition | Registered, open |
| `B-18-3C-PREWARM-TIMEOUT-LEDGER` | Audit-visibility gap when asyncio deadline fires during phase-1 warm-up (M2) | Registered, open |

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_89.md` (delta over v1.88) |
| Arc | B-18-3C-PREWARM-DEFAULT-ON — flip `concurrent_cache_warmup` default to True per ADR-D4 §1.8(f) |
| Committed source | ADR-D4 v1.1 §1.8(f) "required at fan-out cap > 1"; B-18-3C-PREWARM-COHORTKEY (v1.88) prerequisite met |
| Disposition | Default flip at WME + TOML loader; 4 new/updated witnesses; `D4MultiplicativeTunable` default unchanged |
| Decorrelated review | Pending `just codex-review` pre-merge (§13.1) |
| IS / OD / AS / ADR | UNCHANGED. CXA v2.20 UNCHANGED. |
| Runtime spec | UNCHANGED |
| Follow-on status | B-18-3C-PREWARM-DEFAULT-ON CLOSED; B-18-3C-PREWARM-CASCADE + B-18-EPOCH-PARTITION + B-18-3C-PREWARM-TIMEOUT-LEDGER remain open |
