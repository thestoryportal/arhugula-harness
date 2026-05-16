# Class 1 Tension — U-OD-13 topological-level misplacement / unmet dependency

**Filed:** 2026-05-16
**Sub-phase:** 7b — OD axis-stream, Level 2 batch
**Unit:** U-OD-13 — Declare per-cell cardinality budget + Pattern P1 discipline anchor
**Fork class:** Class 1 (halt-execution)
**Routing target:** Phase 6 plan revision — `Implementation_Plan_Operational_Discipline` §4.2 (Kahn level decomposition)

## Defect

U-OD-13 was dispatched as a Level 2 unit (per `.harness/od_axis_worklist.md`
§"Topological levels" line 22, and `Implementation_Plan_Operational_Discipline_v2_1.md`
§4.2 line 2474). The L2 batch is asserted to depend only on landed L0+L1 units
(U-OD-00/01/04/05/15/18).

But U-OD-13's own unit body — `Implementation_Plan_Operational_Discipline_v2_1.md`
§3.4.3 (preserved verbatim through v2.5 / v2.6 per v2.6 §3 pointer table line 156)
— declares:

> **Depends on:** [U-OD-01, U-OD-05, **U-OD-11**]

and the plan's own §4.3 within-axis edge enumeration confirms the edge:

> `| U-OD-11 → | U-OD-12, U-OD-13, U-OD-25, U-OD-32, U-OD-33 | 5 |`  (v2.1 line 2498)

**U-OD-11 is placed at Level 4** by the same §4.2 table (v2.1 line 2476:
`| L4 | U-OD-10, U-OD-11, U-OD-21 | 3 |`).

A unit at L2 cannot depend on a unit at L4: in a Kahn topological sort the
consuming unit's level must be strictly greater than every dependency's level.
U-OD-13's level is bounded below by `level(U-OD-11) + 1`. With U-OD-11 at L4,
U-OD-13's correct level is **≥ L5**, not L2.

The §4.2 level table and the §4.3 edge enumeration are mutually inconsistent for
U-OD-13. The plan's §4.4 Kahn-acyclicity proof is sound for the declared edges
(the graph is acyclic), but the §4.2 *level assignment* for U-OD-13 is wrong:
it does not respect the `U-OD-11 → U-OD-13` edge the plan itself enumerates.

## Why this is a halt, not an absorb

U-OD-11 (Declare per-deployment-surface sampling-mode envelope — `SamplingMode`,
`PerDeploymentSurfaceSamplingMode`, `ALWAYS_SAMPLED_EVENT_CLASSES`) is **not
landed** (worklist places it at L4, status `pending`). U-OD-13's `Inputs` and
acceptance criteria do not visibly consume a U-OD-11 surface, so the edge may be
a stale or over-broad `Depends on` declaration — but resolving that is a plan
question, not an execution-time call. Implementing U-OD-13 now would mean either
(a) silently dropping a declared `Depends on` edge (X-AL-3 / I-2 violation), or
(b) building against a dependency the plan says is required but is absent.

## Recommended resolution (operator decides)

A single `implementation-planner` revision-pass on `Implementation_Plan_Operational_Discipline`,
one of:

- **Option A — re-level.** If the `U-OD-11 → U-OD-13` edge is real, correct the
  §4.2 table: move U-OD-13 to L5 (and re-verify the cascade — U-OD-13's
  consumers U-OD-14/17/31 may shift). U-OD-13 then lands in a later batch after
  U-OD-11.
- **Option B — drop the edge.** If U-OD-13 does not in fact consume any U-OD-11
  surface (its §3.4.3 `Inputs` cite only OD spec §11.1 / §11.4, and its
  signatures — `PerCellCardinalityBudget`, `PER_CELL_CARDINALITY_BUDGET`,
  `PATTERN_P1_DISCIPLINE_ANCHOR` — reference `CellID` (U-OD-01) only), strike
  `U-OD-11` from §3.4.3 `Depends on` and from the §4.3 `U-OD-11 →` row. U-OD-13
  then legitimately sits at L2 (deps U-OD-01 L0, U-OD-05 L1) and can land in
  this batch on a re-clear.

Option B is the likely-correct reading on the evidence (U-OD-13's body shows no
U-OD-11 consumption), but the determination is a plan-authority call.

## Disposition

U-OD-13 **skipped** in the first L2 batch; resolved below.

## RESOLUTION (2026-05-16, determinate plan conform-to-self)

**Option B — strike the stale `U-OD-11` edge.** Verified against the canonical
U-OD-13 body (`v2_1.md` §3.4.3, preserved verbatim through v2.6):

- `Implements: [C-OD-11 §11.1, §11.4]` — cardinality budget + Pattern P1; no
  sampling surface.
- `Inputs:` cite only OD spec §11.1 + §11.4.
- Signatures: `PerCellCardinalityBudget` / `PER_CELL_CARDINALITY_BUDGET` /
  `PATTERN_P1_DISCIPLINE_ANCHOR` — reference only `CellID` (U-OD-01).
- All 6 acceptance criteria + all 6 tests: AC #5 references U-OD-05/06/07,
  AC #6 references U-OD-31. **None references U-OD-11.**
- U-OD-11 exports `SamplingMode` / `PerDeploymentSurfaceSamplingMode` /
  `PER_DEPLOYMENT_SURFACE_SAMPLING` / `ALWAYS_SAMPLED_EVENT_CLASSES` —
  U-OD-13 consumes **none** of them.

The `U-OD-11` entry in §3.4.3 `Depends on` and the §4.3 `U-OD-11 → … U-OD-13`
row are a stale/over-broad edge. The §4.2 Kahn table (U-OD-13 at L2) is
correct; the §4.3 edge enumeration carries the spurious edge. This is a plan
self-contradiction with one provably-wrong statement — determinate, no design
choice. U-OD-13's effective dependency set is `[U-OD-01, U-OD-05]`; it lands at
L2. Plan-file correction (strike the edge in §3.4.3 + §4.3) tracked as OD-plan
revision debt; build proceeds against the corrected dependency set.

**Status:** RESOLVED — U-OD-13 cleared to land at L2 with `Depends on:
[U-OD-01, U-OD-05]`.
