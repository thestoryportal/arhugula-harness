---
artifact: design-substrate/Spec_Control_Plane_v1_26.md
version: v1.26
cleared_at: 2026-05-29T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - .harness/class_1_tension_u_cp_74_entrypayload_field_set_drift.md
  - .harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md
  - PR #37
merge_commit: ec4a2f7
reviewer_chain:
  - operator AskUserQuestion ratification 2026-05-29 Q-set (A + β.i + Q-β.i-1(a) + Q-β.i-3(b))
  - architect recommendation (systems-architect skill) at `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md`
  - spec-writer apply pass authoring v1.25 → v1.26 §16.5 amendments
  - impl-time grounding pass at force-push pre-merge revision (PR #37) — verified type field-set against IS HEAD
---

# Clearance — `Spec_Control_Plane v1.26`

CP spec amended from v1.25 → v1.26 absorbing the β.i resolution of nested fork `class_1_tension_u_cp_74_entrypayload_field_set_drift.md`, operator-ratified 2026-05-29 via AskUserQuestion Q-set (A + β.i + Q-β.i-1(a) + Q-β.i-3(b)). v1.26 rewrites §16.5.3 EntryPayload field set to match IS HEAD at `harness-is/src/harness_is/state_ledger_write.py:62-75`; relocates outcome-bytes semantic to the `idempotency_key` derivation suffix per §16.5.4 (appends `|| sha256(outcome_canonical_bytes).hex()` per row, preserving v1.25 disambiguators verbatim); reframes §16.5.5 chapeau as outcome-bytes scheme consumed by `idempotency_key`, not by `response_hash`.

Cross-axis impact: ZERO IS-axis cascade (β.i is structural mirror of the parent fork's sibling-variant). ZERO cross-axis cascade verified at IS / OD / AS / runtime spec / CXA — all unchanged at this clearance arc. The CP plan v2.28 → v2.29 cascade was co-published at PR #38 (U-CP-74..79 ACs + signatures re-authored against the corrected EntryPayload + idempotency-key suffix).

Carve-outs and deferrals: none at v1.26. The `[[impl-time-grounding-pass-pre-merge-revision]]` workspace pattern was sharpened at this arc — grounding MUST verify type field-sets when design substrate enumerates per-field semantics for externally-defined types (v1.25 grounding caught module/symbol existence + 3 naming mismatches but missed EntryPayload field-set drift; v1.26 closure fixed that).

## Notes

- Phase 7 consumers may rely on v1.26 as canonical until a successor marker is filed.
- The companion CP plan version cleared in tandem with this spec is `Implementation_Plan_Control_Plane_v2_29.md`. A separate clearance marker will be filed for the plan when this convention's retroactive scope is expanded (see `README.md` "Retroactive markers" section). For now, the implicit clearance applies: v2.29 merged to main at PR #38 (commit pending verification against current main HEAD).
- See `.harness/clearance/README.md` for marker discipline.
