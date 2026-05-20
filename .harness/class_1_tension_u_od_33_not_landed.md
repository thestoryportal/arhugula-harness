# Class 1 Tension — U-OD-33 never landed; OD-7b is 34/35, not 35/35

**Status:** ✅ RESOLVED 2026-05-17 — U-OD-33 landed against OD plan §3.8.2 (`harness-od/src/harness_od/per_dimension_preservation_invariants.py` + 15 tests). harness-od: 599 tests green (584+15), pyright 0 introduced, ruff clean. OD-7b is now genuinely 35/35. U-OD-33's 4 cross-axis edges materialized as `cross_axis_composition_target` string references (convention-level — confirmed; CXA v2.3 §2.3.5/§2.3.6).
**Filed:** 2026-05-17, Phase 7 sub-phase 7c, OD-bucket audit.
**Detected by:** 7c cross-axis audit (`.harness/cxa_7c_audit_od_buckets.md`) — U-OD-33 has no source file.

---

## Defect

**U-OD-33 ("Compose per-dimension preservation invariants across cross-axis dimensions", OD plan §3.8.2) was never landed as code.**

Evidence:
- `harness-od/src/harness_od/` has **no file** implementing U-OD-33. 34 source files for 35 plan units (U-OD-00 + U-OD-01..34).
- U-OD-33's distinctive plan signatures — `PreservationDimension`, `PreservationInvariant`, `InvariantForm`, `EnforcementLayer`, `PRESERVATION_INVARIANTS`, `verify_per_dimension_preservation` — return **zero grep hits** in `harness-od/src`.
- U-OD-33 appears in `src` only as a *reference* inside U-OD-34's terminal manifest (`substrate_seam_exports_aggregate_manifest.py:53,253` — `source_unit="U-OD-30 + U-OD-32 + U-OD-33"`). The terminal manifest references a unit that does not exist.
- `.harness/od_axis_worklist.md` line 174: "OD-7b CLOSE — **34/35** landed; U-OD-29 FF-3 pending. Only U-OD-29 outstanding." Line 193: "✅ OD-7b COMPLETE — 35/35" after U-OD-29 landed.

## Root cause — a counting error at OD-7b close

The memory record of landed units (`phase-7-bootstrap-status`) enumerates two batches: 18 units + 16 units = **33 distinct** units. Plus U-OD-29 (FF-3, landed separately) = **34**. OD plan is 35 units. The missing 35th is **U-OD-33**, not U-OD-29.

The worklist's "34/35, only U-OD-29 outstanding" double-miscounted: it treated 33-landed as 34, so when U-OD-29 landed it declared "35/35". U-OD-33 fell through — it is an L7 unit (`od_axis_worklist.md` line 27: "L7 | U-OD-24, U-OD-29, U-OD-33 | pending") and a within-axis **leaf** (nothing in OD depends on it; only U-OD-34's manifest *references* it). Being a leaf, its absence broke no OD test and no pyright check — so "584 tests green, pyright 0" held and masked the gap.

## Impact

1. **OD-7b is 34/35, not complete.** The "Phase 7 7b COMPLETE — all 4 axis-streams" milestone is wrong.
2. **U-OD-34's terminal aggregate manifest references a non-existent source unit** (U-OD-33). The manifest is currently mis-attested.
3. **7c cannot wire U-OD-33's 4 cross-axis edges** — CXA §2.3.5 (U-OD-33 → U-AS-14/19/15, 3 edges) and §2.3.6 (U-OD-33 → U-CP-43, 1 edge) cite a consumer unit that does not exist.
4. The 7c OD→AS and OD→CP buckets cannot close until U-OD-33 lands.

## Classification

Not a design-artifact defect — OD plan §3.8.2 fully specifies U-OD-33 (signatures, acceptance criteria, dependency edges all present). This is an **execution-completeness gap**: a fully-specified unit was skipped at 7b. The fix is to **land U-OD-33** against its existing plan §3.8.2 body (a `phase-7-implementation` unit-consumption task) — no design back-flow needed. Filed Class 1 because it falsifies the 7b-complete milestone and blocks 7c.

## Resolution

1. Land U-OD-33 per OD plan §3.8.2 (`Implementation_Plan_Operational_Discipline_v2_1.md` §3.8.2, preserved verbatim through v2.11) — a leaf unit; deps U-OD-05/07/11/12/17/32 + cross-axis (all landed or 7c-wired).
2. Verify U-OD-34's terminal manifest entry for U-OD-33 is now satisfied.
3. Correct the OD-7b status record (worklist + memory) to reflect the true count.
4. Then 7c OD→AS / OD→CP buckets may wire U-OD-33's edges.

## Halt state

| Element | Value |
|---|---|
| Halt point | 7c OD-bucket wiring — blocked until U-OD-33 lands |
| Routing | `phase-7-implementation` — land U-OD-33 against OD plan §3.8.2 (no design revision) |
| Also note | OD audit (`.harness/cxa_7c_audit_od_buckets.md`) classified U-OD-33's 4 edges NEEDS-REVIEW for exactly this reason |

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** Already labeled RESOLVED 2026-05-17 (U-OD-33 landed against OD plan §3.8.2; OD-7b genuinely 35/35). Audit confirms.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
