---
artifact: design-substrate/Spec_Control_Plane_v1_89.md
version: v1.89
cleared_at: 2026-07-10T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/arc-ledger.yaml (B-18-3C-PREWARM-DEFAULT-ON entry)
  - design-substrate/Spec_Control_Plane_v1_88.md (prerequisite COHORTKEY delta)
  - ADR-D4 v1.1 §1.8(f) "required at fan-out cap > 1"
merge_commit: pending (pre-merge at filing time)
reviewer_chain:
  - ADR-D4 §1.8(f) authority (foundational; no re-litigation required)
  - B-18-3C-PREWARM-COHORTKEY (v1.88) prerequisite verification — CohortKeyCapable oracle live
  - Safety argument: non-CohortKeyCapable dispatchers → predicate False → byte-identical baseline
  - Phase 7 impl grounding pass (workflow_manifest_entry.py + workflow_manifest_loader.py default flip)
  - just codex-review pre-merge (§13.1 out-of-family review)
supersedes: spec-control-plane-v1-88-cleared-2026-07-10.md
---

# Clearance — `Spec_Control_Plane v1.89`

v1.89 is the B-18-3C-PREWARM-DEFAULT-ON absorption arc: `WorkflowManifestEntry.concurrent_cache_warmup` default flipped from `False` to `True` per ADR-D4 §1.8(f) "required at fan-out cap > 1." The companion TOML/YAML loader field (`_WorkflowSectionFields.concurrent_cache_warmup`) mirrors the flip so absent manifest keys inherit the new default. The `D4MultiplicativeTunable` model field and the `d4_tunable()` function-parameter default remain `False` (non-PARALLELIZATION callers omit the argument; the function default correctly keeps warmup off for those paths).

The flip is safe because v1.88 (B-18-3C-PREWARM-COHORTKEY) delivered the `CohortKeyCapable` dispatcher-oracle: a non-CohortKeyCapable dispatcher causes `_same_prefix_cohort()` to return False → `_warmup_gate=False` → all-concurrent baseline, byte-identical to the pre-flip state. Warmup fires only when every branch dispatcher is CohortKeyCapable and every branch returns the same non-None cohort key. At MVP, `frozen_tool_superset is None` → `RuntimeLLMDispatcher.cohort_key()` returns None → predicate False → no warmup — correct machine-attestation, not a regression.

Four new/updated witnesses land with this arc: `test_workflow_manifest_entry_default_concurrent_cache_warmup_is_true`, `test_workflow_manifest_entry_accepts_explicit_opt_out`, an updated `test_optional_field_absent_uses_pydantic_carrier_default` assertion, and a `@pytest.mark.e2e` skipif skeleton. B-18-3C-PREWARM-CASCADE (warmup on CASCADE_CANCEL + PAUSE paths), B-18-EPOCH-PARTITION (heterogeneous partition), and B-18-3C-PREWARM-TIMEOUT-LEDGER (audit-visibility gap on phase-1 timeout) remain registered and open.

## Notes

- Phase 7 consumers may rely on this version (v1.89) as canonical for the `concurrent_cache_warmup` default-on discipline.
- The §25.15 `_same_prefix_cohort()` predicate and §25.16 `CohortKeyCapable` Protocol are unchanged from v1.88; v1.89 is additive only (§25.17 new section).
- See `.harness/clearance/README.md` for marker discipline.
