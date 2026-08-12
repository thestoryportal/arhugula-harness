# Implementation Plan: Control Plane — v2.51 (delta over v2.50)

*v2.51 absorbs CP spec v1.118's B-153 column ratification into the plan's execution
authority. ONE existing unit, U-CP-54, has its inherited acceptance figures superseded
at the two hitl-touched sites; no new unit, cluster, DAG node, dependency edge, or CXA
row is introduced. Every other U-CP-54 acceptance criterion, the signature block, the
rollback boundary, and all other units are PRESERVED VERBATIM.*

**Status:** Proposed

## §0 Change-note (v2.50 → v2.51)

### §0.1 The remaining stale site

v2.50 §0.3 deliberately left criterion #2's `hitl.*` (4 attrs) row untouched — its
adjudication was register row B-153, quarantined at spec v1.117 §0.5. Spec v1.118
ratifies the `Attribute count` column as the namespace's declared live export claim in
DISTINCT attribute keys and enumerates the hitl.* cell at **11** from C-CP-20 §20.6
(matching the standing OD commitment at C-OD-05 §5.1 row 6). The plan's inherited
figures must follow (spec + plan must agree; root `CLAUDE.md` §1.3 chain).

### §0.2 The amendment (U-CP-54, acceptance-figure re-pin only)

Superseding the U-CP-54 rows at the named sites — everything else in the unit
PRESERVED VERBATIM:

1. **Criterion #2** `hitl.*` row now reads: `hitl.*` (**11 attrs** across 4 span
   names per C-CP-20 §20.6 distinct declared keys, ratified at spec v1.118) →
   U-CP-46 → `OD_PLAN_SESSION_4_D6_SECTION_1_2`.
2. **Criterion #6** now reads: Total attribute count:
   (4 + 10 + 7 + 11 + 7 + 3) + (9 + 6 + 5 + 9) + (4) = 42 + 29 + 4 = **75 CP-axis
   attributes** exported to OD plan Session 4 D6 §1.2 + §1.4 + §1.5, per C-CP-24
   §24.1 as ratified at spec v1.118.
3. **Test roster:** `test_total_attribute_count_sixty_eight` is superseded by
   `test_total_attribute_count_seventy_five` (the as-built name at
   `harness-cp/tests/test_cp_namespace_export_manifest.py`); all other listed test
   names unchanged.

### §0.3 What this delta is NOT

Not a unit re-open: U-CP-54 landed at PR #905-era consumption; this is the
plan-authority re-pin owed under the B-153 ratification, the exact sibling of the
v2.50 re-pin under B-144 venue-A. The audit.* qualifier row is untouched — spec
v1.118 §0.4 audited it as CONFORMING under the ratified definition (7 distinct keys
at §20.4), so no plan figure changes for it.

**Authority:** CP spec v1.118 (clearance
`spec-control-plane-v1-118-cleared-2026-08-11.md`); register row `B-153` close_out
steps (1)–(3); the B-144 venue-A precedent (PR #1311).

*End of v2.51 delta. All prior plan bodies preserved verbatim per the delta-only-file
convention.*
