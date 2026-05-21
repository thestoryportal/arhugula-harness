# Phase A — Iteration 1 → 2 Log

**Filed:** 2026-05-21 (Remaining-Work Closure Arc, Phase B iteration-1 → Phase A iteration-2 transition)

## Phase B iteration-1 outcome

`.harness/Spec_Phase_B_Adversarial_Review_v1.md` produced:
- 0 Class 3 findings (severe — phase re-opening)
- 7 Class 2 findings (moderate — current-phase revision)
- 3 Class 1 findings (minor — drift)

## Phase A iteration-2 dispositions applied

| Finding | Disposition | Apply site |
|---|---|---|
| F2-01 (subprocess terminology leak) | Spec amended | Runtime spec v1.13 §14.9.1 transport-neutral terminology block added; §14.9.6 invariant 1 + invariant 5 rephrased |
| F2-02 (Pattern-P1 alignment gap) | Spec amended | OD spec v1.8 §C-OD-29.1 attribute table: added `step.id` + `validator.escalation.parent_hitl_span_id` + `validator.escalation.fail_class`; count updated 8 → 11 across 4 span sites |
| F2-03 (ValidatorOutcome mapping) | Spec amended + operator-ratified | CP spec v1.10 §25.2: explicit mapping table added; OPERATOR_BURDEN_EXCEEDED → ESCALATE_HITL per operator ratification 2026-05-21 |
| F2-04 (workflow.envelope shape) | Operator confirmed single-envelope default | OD spec v1.8 §C-OD-25 unchanged; marker retained as resolved (no spec edit owed) |
| F2-05 (validator cost-meter) | Operator confirmed CPU-meter default | OD spec v1.8 §C-OD-26.2 unchanged; marker retained as resolved |
| F2-06 (Decimal serialization) | Spec amended + operator-ratified | OD spec v1.8 §C-OD-28.4 invariant 3 (NEW) added: string-serialization at OTel span attribute boundary |
| F2-07 (Phase E scope-enumeration) | Routed to Phase E | Phase E handoff artifact authoring scope; not a Phase A defect |
| F1-01 (4-attr vs 8-attr framing) | Spec amended | OD change-note "4-attribute" → "11-attribute" framing corrected; §C-OD-29.1 closing paragraph updated |
| F1-02 (CXA v2.6 §NN placeholders) | Spec amended | CXA v2.6 §2.3.7 rows 3-7 back-patched with resolved section refs (§C-OD-32 / §C-OD-33 / §C-OD-29 / §C-OD-30 / §C-OD-31) |
| F1-03 (namespace vs span name) | Spec amended | Runtime spec §14.10.3 Burden namespace clarification added |

## Files edited at iteration 2

- `design-substrate/Spec_Harness_Runtime_v1.md` (3 edits — F2-01 transport-neutral terminology block + invariant 1 + §14.10.3 namespace note)
- `design-substrate/Spec_Control_Plane_v1_10.md` (1 edit — F2-03 ValidatorOutcome mapping table)
- `design-substrate/Spec_Operational_Discipline_v1_8.md` (3 edits — F2-02 attribute table + F2-06 invariant 3 + F1-01 change-note count)
- `design-substrate/Cross_Axis_Composition_Document_v2_6.md` (1 edit — F1-02 §2.3.7 row back-patch)
- `.harness/Spec_Phase_A_Iteration_1_Log.md` (this file)

## Iteration 2 readiness

All 10 findings addressed. Iteration-2 adversarial review file owed at `.harness/Spec_Phase_B_Adversarial_Review_v2.md`.
