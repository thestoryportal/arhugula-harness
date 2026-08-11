# Implementation Plan: Control Plane — v2.50 (delta over v2.49)

*v2.50 absorbs CP spec v1.117's B-144 venue-A §24.1.B re-table into the plan's execution
authority. ONE existing unit, U-CP-54, has its inherited acceptance figures superseded;
no new unit, cluster, DAG node, dependency edge, or CXA row is introduced. Every other
U-CP-54 acceptance criterion, the signature block, the rollback boundary, and all other
units are PRESERVED VERBATIM.*

**Status:** Proposed

## §0 Change-note (v2.49 → v2.50)

### §0.1 The defect (out-of-family review round 1 at PR #1311)

U-CP-54's acceptance criteria at `Implementation_Plan_Control_Plane_v2_1.md:3113-3138`
were authored against spec v1.2's §24.1.B figures and were never re-pinned by any delta
through v2.49 — stale across two ratified supersessions and the v1.117 re-table:

- criterion #3 pins `retry.*` at **4 attrs** (v1.3 replaced the set wholesale — 6) and
  `harness.breaker.*` at **7 attrs** (OD v1.32 grew the C-OD-07 §7.1 canonical schema — 9);
- criterion #6 totals **63** (34 + 25 + 4);
- the test roster names `test_total_attribute_count_sixty_three`.

The as-built manifest and its test moved 63 → 65 at the OD v1.32 absorption (register
row B-126 recomputed the subtotals) and 65 → 67 at CP v1.117, so plan-driven
conformance work reading v2_1's figures would expect retired values.

### §0.2 The amendment (U-CP-54, acceptance-figure re-pin only)

Superseding v2_1's U-CP-54 rows at the named sites — everything else in the unit
PRESERVED VERBATIM:

1. **Criterion #3** `retry.*` row now reads: `retry.*` (**6 attrs** per C-CP-03 §3.5
   v1.3) → U-CP-07 → `OD_PLAN_SESSION_4_D6_SECTION_1_4`.
2. **Criterion #3** `harness.breaker.*` row now reads **9 attrs** (canonical schema at
   OD C-OD-07 §7.1 as amended at OD v1.32, B-19-BREAKER-AMBIENT-ATTRS); the
   `SUBSTRATE_ANCHORED_OUTSIDE_CP` posture clause unchanged.
3. **Criterion #6** now reads: Total attribute count:
   (3 + 10 + 7 + 4 + 7 + 3) + (9 + 6 + 5 + 9) + (4) = 34 + 29 + 4 = **67 CP-axis
   attributes** exported to OD plan Session 4 D6 §1.2 + §1.4 + §1.5, per C-CP-24
   §24.1 as re-tabled at spec v1.117.
4. **Test roster:** `test_total_attribute_count_sixty_three` is superseded by
   `test_total_attribute_count_sixty_seven` (the as-built name at
   `harness-cp/tests/test_cp_namespace_export_manifest.py`); all other listed test
   names unchanged.

### §0.3 What this delta is NOT

Not a unit re-open: U-CP-54 landed at PR #905-era consumption and its as-built manifest
already carries the live figures — this is the plan-authority re-pin owed under the
same venue-A decision (spec + plan must agree; root `CLAUDE.md` §1.3 chain). The
hitl.*/Attribute-count column-semantics question stays out of scope here exactly as at
spec v1.117 §0.5 — criterion #2's `hitl.*` (4 attrs) row is deliberately NOT touched;
its adjudication is register row **B-153**.

**Authority:** CP spec v1.117 (clearance
`spec-control-plane-v1-117-cleared-2026-08-11.md`); fork doc
`class_1_fork_b144_cp_24_1b_stale_retable.md`; out-of-family review round 1 at PR
#1311 (the P2 that surfaced the plan gap).

*End of v2.50 delta. All prior plan bodies preserved verbatim per the delta-only-file
convention.*
