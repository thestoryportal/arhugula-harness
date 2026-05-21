# Class 3 Tension — `harness-cp/CLAUDE.md` + `harness-od/CLAUDE.md` cross-axis edge counts cite CXA v2.1 baseline; v2.3/v2.4 reclassification not yet absorbed

**Class:** 3 — informational; non-blocking; documented.
**Filed:** 2026-05-20 during `[[class_3_tension_cxa_v2_4_axis_back_edge]]` absorption arc.
**Status:** OPEN-FLAGGED — surfaced for operator visibility; absorbed at next CP/OD plan revision pass that touches edge counts.

---

## Finding

While absorbing `[[class_3_tension_cxa_v2_4_axis_back_edge]]` (the CP→OD back-edge added at CXA v2.4), inspection revealed that the per-axis CLAUDE.md edge counts still cite **CXA v2.1 baseline numbers**, not the v2.3 reclassification (7c-prereq) or v2.4 numbers. This pre-existed the back-edge absorption arc.

### CP-side drift

`harness-cp/CLAUDE.md` §1.1 axis-identity statement:

> CP posture per `Cross_Axis_Composition_Document_v2_1.md` §2.1: **largest cross-axis consumer** (60 outbound edges; 36 → IS + 24 → AS); …

`harness-cp/CLAUDE.md` §2.3 edge table:

| Edge direction | Edges | Source artifact (citation) |
|---|---|---|
| CP → IS (outbound) | 36 | `Cross_Axis_Composition_Document_v2_1.md` §2.3.2 |
| CP → AS (outbound) | 24 | `Cross_Axis_Composition_Document_v2_1.md` §2.3.4 |

`Cross_Axis_Composition_Document_v2_4.md` §2.1 matrix + §2.4 per-axis outbound posture summary:

| Bucket | v2.4 canonical | v2.4 genuine |
|---|---|---|
| CP → IS (§2.3.2) | 37 | 9 |
| CP → AS (§2.3.3) | 18 | 5 |
| CP → OD (§2.3.7 — NEW v2.4) | 1 | 1 |
| **CP outbound aggregate** | **56** | **15** |

Drift: harness-cp/CLAUDE.md §1.1 says **60 outbound** (36+24); v2.4 says **56** (37+18+1). harness-cp/CLAUDE.md §2.3 row counts (36 / 24) do not match v2.4 (37 / 18). The new CP→OD = 1 row added at the back-edge absorption is the only v2.4-precision row in the table.

### OD-side drift (bounded — already self-flagged at C3-15)

`harness-od/CLAUDE.md` §2.2 already self-flags the OD → IS row drift via the `CXA-OD-IS-EDGE-DRIFT` Class 3 informational item (CXA v2.1 §2.3.5 = 6 edges baseline vs OD plan v2.6 §4.5.1 = 4 edges). The OD → AS (10) and OD → CP (12) rows match CXA v2.4 §2.1 matrix exactly. No new OD-side drift surfaced.

## Why it matters

The drift is **citation-precision drift, not contract drift** — per-unit acceptance criteria, contract surfaces, and CXA v2.4 §2.3.7 typed-seam classification are unaffected. The CP-side counts at harness-cp/CLAUDE.md are out-of-date pointers to CXA, not load-bearing invariants in their own right.

However, the divergence creates two reader hazards:

1. A reader inspecting harness-cp/CLAUDE.md §1.1 + §2.3 vs CXA v2.4 §2.4 will see contradictory numbers (60 vs 56; 36 vs 37; 24 vs 18) inside the same canonical-pointer chain — violating workspace `CLAUDE.md` I-1 (canonical artifact citations resolve byte-exact).
2. Absorbing the v2.4 back-edge with "patch 60→61" would have **silently absorbed the v2.1→v2.3 reclassification drift** inside an absorption arc designed to retire drift — the worst failure mode per workspace `CLAUDE.md` §4.3 (silent absorption of design-phase defects).

The back-edge absorption arc explicitly **did NOT patch CP §1.1 / §2.3 v2.1 citations** to avoid this silent-absorption hazard. The drift is now isolated to this Class 3 record for scoped resolution.

## Why we surfaced this here, not at v2.3 reclassification time

The v2.3 7c-prereq reclassification (genuine-typed-seam / convention-level / phase-2-runtime tagging) was authored at CXA v2.3 landing but the per-axis CLAUDE.md absorption was not part of v2.3 Path scope. CXA v2.3 §0 change note documents the reclassification scope at the CXA layer; per-axis CLAUDE.md absorption was deferred to per-axis plan revision passes.

## Routing per `Project_Workflow_v1_8.md` §2.7.6

**Class 3 (informational).** Non-blocking; documented. No design extension (the underlying numbers exist at CXA v2.4 §2.4 — this is citation absorption work, not new authoring).

**Owed amendments at next CP plan revision pass that touches edge counts (Form A — citation precision only):**

| Site | Amendment |
|---|---|
| `harness-cp/CLAUDE.md` §1.1 | "60 outbound edges; 36 → IS + 24 → AS" → "56 outbound edges; 37 → IS + 18 → AS + 1 → OD" with citation to `Cross_Axis_Composition_Document_v2_4.md` §2.4 |
| `harness-cp/CLAUDE.md` §2.3 CP→IS row | 36 → 37; citation `_v2_1.md` § 2.3.2 → `_v2_4.md` §2.3.2 |
| `harness-cp/CLAUDE.md` §2.3 CP→AS row | 24 → 18; citation `_v2_1.md` §2.3.4 → `_v2_4.md` §2.3.3 (note: bucket numbering shifted at v2.3 — CP→AS moved from §2.3.4 to §2.3.3) |
| `harness-cp/CLAUDE.md` §2.3 OD→CP (inbound) row | 12 unchanged; citation `_v2_1.md` §2.3.3 → `_v2_4.md` §2.3.6 |
| `harness-cp/CLAUDE.md` §2.3 table title | "Cross-axis edge inventory (CXA v2.1)" → "Cross-axis edge inventory (CXA v2.4)" |

These amendments are NOT in scope for `[[class_3_tension_cxa_v2_4_axis_back_edge]]` absorption (which is Form A back-edge acknowledgement only).

## Filing footer

| Field | Value |
|---|---|
| Filed at | `[[class_3_tension_cxa_v2_4_axis_back_edge]]` absorption arc, 2026-05-20 |
| Filed by | front-(a) absorption arc — surfaced during CP §1.1 outbound count inspection (60 vs 56 mismatch against CXA v2.4 §2.4) |
| Class | 3 (informational) |
| Surface | Per-axis CLAUDE.md citation-precision drift (CXA v2.1 baseline vs v2.4 reclassified numbers) |
| Related | `[[class_3_tension_cxa_v2_4_axis_back_edge]]`; `Cross_Axis_Composition_Document_v2_4.md` §0.4 + §2.4; CXA v2.3 §0 reclassification change-note |
| Re-entry trigger | Next CP plan revision pass that touches edge counts (Form A absorption); alternatively, dedicated per-axis CLAUDE.md v2.4 citation-precision pass |
| Resolution | Will close when harness-cp/CLAUDE.md §1.1 + §2.3 absorb v2.4 citations end-to-end |

---

*This Class 3 record exists so the v2.1→v2.4 reclassification drift is operator-visible at filing, not discovered later when the next person reads CP §1.1 + CXA v2.4 §2.4 side-by-side. The drift is bounded (citation-precision only, no contract impact), but isolating it here keeps the back-edge absorption arc clean (Form A only) per workspace `CLAUDE.md` §4.3 silent-absorption prohibition.*
