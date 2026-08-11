# Spec: Operational Discipline — v1.40 (delta over v1.39)

*Delta-only file. The v1.39 body + the entire C-OD-01 … C-OD-34 contract body are
PRESERVED VERBATIM (delta-only-spec-file convention). This delta carries exactly ONE
amendment — **C-OD-05 §5.1 row 9 (`engine.*`)'s `Attribute count` cell moves 3 → 4**,
carrying the CP v1.3 C-CP-09 §9.1 supersession this row's own citations already point
at. §5.1's fourteen other rows, the 15-row roster, every other C-OD contract, and all
sampling/ingestion disciplines are UNTOUCHED and PRESERVED VERBATIM.*

**Filed:** 2026-08-11
**Authoring authority:** The row's own `Ingest verbatim` posture + cross-axis citation
(C-CP-09 §9.1), which has declared FOUR attributes since CP spec v1.3 (the §9.1 table
gained `engine.replay_disposition`, ADR-D1 v1.2 §1.1.1; the v1.3 change-note reads
"Contract surface revised from 3 attributes to 4 attributes"). Applied as the OD leg
of the `B-144` venue-A re-table (CP v1.117, PR #1311; out-of-family review rounds 4-5
surfaced the OD ingestion carry), per workspace `CLAUDE.md` §4.3 back-flow + §4.5
clearance discipline. Fork doc `class_1_fork_b144_cp_24_1b_stale_retable.md`.
**Predecessor:** `Spec_Operational_Discipline_v1_39.md` (v1.39 — the `B-123`-family
§9.2.1 term-3 retraction leg; cleared 2026-08-09)
**Revision shape:** Delta-only spec file. v1.40 carries this change-note + exactly ONE
amendment cell. **ZERO new contract numbers**; **ZERO roster change** (§5.1 stays at
15 rows); **ZERO new namespace**; **ZERO new attribute minted** (the 4th `engine.*`
attribute was minted at ADR-D1 v1.2 / CP v1.3 — this delta only carries the count);
**ZERO emission-site change**; **ZERO head-sampler change**; **ZERO Runtime delta**;
**ZERO CXA rows**; **ZERO hash impact**.

---

## Change-note (v1.39 → v1.40)

### §0.1 The defect

C-OD-05 §5.1 row 9 (`Spec_Operational_Discipline_v1_2.md:337`) commits `engine.*` at
"3 (`engine.class`, `engine.event_history.tier`, `engine.event.id`)" under an
`Ingest verbatim` posture whose source declaration site is C-CP-09 §9.1. CP spec v1.3
extended §9.1 to FOUR attributes (+`engine.replay_disposition`) and no OD delta
through v1.39 carried the count — the same ratified-supersession-never-carried class
as the CP-side §24.1 rows re-tabled at CP v1.117. The as-built ingestion surface
(`harness-od/src/harness_od/namespace_map.py` `engine.` row) tracked the stale 3
while citing §9.1 as its own `source_contract_ref`.

### §0.2 The amendment

C-OD-05 §5.1 row 9's `Attribute count` cell is superseded:

> 3 (`engine.class`, `engine.event_history.tier`, `engine.event.id`)

becomes

> 4 (`engine.class`, `engine.event_history.tier`, `engine.event.id`,
> `engine.replay_disposition`) per C-CP-09 §9.1 (v1.3 amendment; ADR-D1 v1.2 §1.1.1)

Every other cell of row 9 (source declaration site, cross-axis citation including the
C-IS-05/C-IS-10 F2-join note, ingestion posture) and every other §5.1 row — including
row 6's `hitl.*` "11 attributes across 4 span names" cell, which is register row
`B-153`'s scope — PRESERVED VERBATIM.

### §0.3 Same-PR cascade

`harness-od/src/harness_od/namespace_map.py` `engine.` row 3 → 4 and
`harness-od/tests/test_cp_source_namespace_verification.py` (dict + docstring) land in
the same PR (#1311, bundled absorption per root `CLAUDE.md` §11.4) — the code half
this delta authorizes. No OD-side aggregate sums the map's counts; the OD plan does
not re-state the §5.1 per-row counts (verified by sweep at HEAD).

*End of v1.40 delta. All other content of the C-OD chain preserved verbatim.*
