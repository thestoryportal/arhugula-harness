# Phase C — Iteration 1 → 2 Log

**Filed:** 2026-05-21 (Remaining-Work Closure Arc, Phase D iteration-1 → Phase C iteration-2 transition)

## Phase D iteration-1 outcome

`.harness/Plan_Phase_D_Adversarial_Review_v1.md` produced:
- 0 Class 3 findings
- 5 Class 2 findings (F2-01 / F2-02 / F2-03 / F2-04 / F2-05)
- 4 Class 1 findings (F1-01 / F1-02 / F1-03 / F1-04)

## Phase C iteration-2 dispositions applied

| Finding | Disposition | Apply site |
|---|---|---|
| F2-01 (U-RT-67 conjunction → disjunction) | Plan amended | `Implementation_Plan_Harness_Runtime_v2_11.md` U-RT-67 Depends-on restructured; added "Requires at end-to-end landing: at-least-one-of {U-RT-64/65/66}" line |
| F2-02 (cost-prefix gap) | Plan amended + operator-ratified | Option 1 RATIFIED — `Implementation_Plan_Control_Plane_v2_15.md` U-CP-72: 5 → 6 new prefixes (added `cost:`); AC #1 reads "8 action_id prefixes"; AC #2 cites new cost-record AuditPayload subclass; Cross-arc note added re: CXA v2.6 → v2.7 amendment owe; U-CP-72 Depends-on extended to include U-OD-41 (cross-axis: OD) |
| F2-03 (REVALIDATE-budget untested) | Plan amended | `Implementation_Plan_Control_Plane_v2_15.md` U-CP-60 AC #6 added covering CP spec v1.10 §25.7 invariant 3 |
| F2-04 (tool-rate formulas) | Plan amended | `Implementation_Plan_Operational_Discipline_v2_14.md` U-OD-39 AC #2 expanded with explicit per-cost_kind formulas (flat / per-input-byte / per-output-byte); AC #5 amended to test all 3 cost_kind values with Decimal precision verification |
| F2-05 (cluster sub-decomposition) | Plan amended | `Implementation_Plan_Control_Plane_v2_15.md` §1 added sub-cluster decomposition (10-CP-A/B/C/D); `Implementation_Plan_Operational_Discipline_v2_14.md` §1 added sub-cluster decomposition (4-OD-A/B/C/D/E) |
| F1-01 (U-RT-65/66 AC #5 wording) | Plan amended | U-RT-65 + U-RT-66 AC #5 tightened with specific success conditions (HTTP 200 + protocol_version returned; SSE handshake event + list_tools count) |
| F1-02 (U-OD-35 AC #5 wording) | Plan amended | U-OD-35 AC #5 tightened with specific span assertions (root span + parent context propagation + status discrimination) |
| F1-03 (U-CP-65 soft-dep) | Plan amended | U-CP-65 Depends-on restructured: hard-deps [U-CP-63, U-CP-64]; soft-dep U-OD-51 (Pattern-P1-alignment-check predicate, not landing-order) |
| F1-04 (existing-landed carrier deps) | Plan amended | U-OD-43 + U-CP-71 added "Requires existing (landed at main per ...)" annotations |

## CXA v2.6 → v2.7 amendment owe (NEW at iteration-2)

Per F2-02 ratification: CXA v2.6 §2.3.7 needs a new row 8 for the cost-attribution audit-write seam. Authoring scope: ~30 lines (single row append + §2.1 aggregate matrix +1 update; CP→OD bucket grows 7 → 8; aggregate 99 → 100; genuine 29 → 30). NOT applied this iteration to preserve Phase C scope discipline (Phase C is plan authoring; CXA spec amendment is Phase A iteration-N scope). Explicitly enumerated at Phase E handoff artifact + flagged at U-CP-72 cross-arc note.

## Files edited at iteration 2

- `design-substrate/Implementation_Plan_Harness_Runtime_v2_11.md` (3 edits — F2-01 + F1-01 ×2)
- `design-substrate/Implementation_Plan_Control_Plane_v2_15.md` (5 edits — F2-02 + F2-03 + F2-05 + F1-03 + F1-04)
- `design-substrate/Implementation_Plan_Operational_Discipline_v2_14.md` (4 edits — F2-04 + F2-05 + F1-02 + F1-04)
- `.harness/Plan_Phase_C_Iteration_1_Log.md` (this file)

## Iteration 2 readiness

All 9 findings addressed. Iteration-2 adversarial review file owed at `.harness/Plan_Phase_D_Adversarial_Review_v2.md`.

## CXA owe carried to Phase E

Phase E handoff artifact MUST enumerate the CXA v2.6 → v2.7 amendment owed at Phase A iteration-N (per F2-02 operator ratification). This is a small additive patch (~30 lines) that adds the cost-attribution audit-write seam at §2.3.7 row 8.
