# Implementation Plan — Information Substrate (IS axis) — v2.2

*Revision-pass amendment to v2.1. Authored at Phase 6.5 Session 3 (ζ) — F3-02 IS-axis Revision Pass. Skill: `implementation-planner` SKILL.md §8 revision-pass sub-mode.*

---

## §0 Change-note

### §0.1 Predecessor

`Implementation_Plan_Information_Substrate_v2_1.md` (v2.1 baseline; canonical at Phase 6 close per `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md`).

### §0.2 Revision scope

v2.1 → v2.2: F3-02 absorption per Phase 6.5 Session 3 (ζ) operator decision (Segment 1, 2026-05-15): **Form A — citation precision**. No new IS-axis atomic unit; no signature changes; no coverage matrix changes; no dependency-graph changes. Substantive absorption work occurs at `Implementation_Plan_Operational_Discipline_v2_4.md` U-OD-20 acceptance #11 `Depends on` field, resolving `U-IS-NN (C-IS-10 §10.2)` to canonical carrier `U-IS-12` per the IS plan v2.1 §2.6 U-IS-17 substrate seam exports manifest.

This file emits as a discoverable IS-side closure record for F3-02. All atomic-unit content, signatures, dependency graph, and coverage matrix carry forward verbatim from v2.1.

### §0.3 Sections preserved verbatim from v2.1

| Section | Status |
|---|---|
| §1 Spec inventory (C-IS-01 through C-IS-10 mapping) | Preserved verbatim |
| §1.2 Cluster decomposition realized (17 units across 6 clusters) | Preserved verbatim |
| §1.3 Substrate-version citation alignment (IS spec v1.2; ADR latest-version body-citations) | Preserved verbatim |
| §2 Atomic-unit decomposition (U-IS-01 through U-IS-17) | Preserved verbatim |
| §3 Dependency graph + within-axis edges + acyclicity verification + backref reconciliations | Preserved verbatim |
| §4 Coverage matrix | Preserved verbatim |
| §5 Filing footer (v2.1 prose) | Superseded by §6 filing footer below |

### §0.4 Sections revised

None at the atomic-unit body level. The v2.2 emission consists entirely of this change-note (§0) and an updated filing footer (§6).

### §0.5 Coverage matrix delta

None. All 17 atomic units preserved verbatim from v2.1; coverage matrix unchanged.

### §0.6 Dependency-graph delta

None. Within-axis DAG (17 nodes, 9 topological levels) unchanged. Acyclic invariant preserved.

OD→IS cross-axis edge cardinality reduces from 6 (per OD plan v2.3 §4.5.1) to 4 (per OD plan v2.4 §4.5.1) per C3-15 Path (i-refined) absorption. This drift is recorded at IS plan side as informational; CXA v2.1 §2.3.5 remains canonical at 6-edge enumeration per Phase 6.5 Session 3 (ζ) Kickoff §2.2 (CXA preserved at v2.1; out-of-scope at this session). Class 3 informational item surfaced at Session 3 close handoff (see §0.9).

### §0.7 F3-02 closure record

| Field | Value |
|---|---|
| Finding ID | F3-02 |
| Source | `Adversarial_Review_6_iter4.md` Class 3 disposition (P6-CK Iteration 4) |
| Defect | OD plan v2.3 U-OD-20 acceptance #11 cross-axis dependency cited `U-IS-NN` placeholder for C-IS-10 §10.2 IDEMPOTENCY_KEY_JOIN_EXPORT consumption; canonical IS-plan carrier unit unresolved at v2.3. |
| Form selected | **Form A — Citation precision** (operator decision Phase 6.5 Session 3 Segment 1, 2026-05-15) |
| Substrate analysis | IS plan v2.1 §2.6 U-IS-17 manifest enumerates C-IS-10 §10.2 carriers as `U-IS-07` (entry-shape carrier) + `U-IS-12` (read-contract / join carrier). Every other cross-axis consumer of C-IS-10 §10.2 binds to U-IS-12 (CP plan v2.3: U-CP-30 → U-IS-12, U-CP-55 → U-IS-12; AS plan v1: U-AS-19 → U-IS-12 per CXA v2.1 §2.3.1). Canonical carrier for OD-side U-OD-20 consumption: **U-IS-12**. |
| Absorption site | OD plan v2.4 U-OD-20 `Depends on` field + acceptance #11 prose (per `Implementation_Plan_Operational_Discipline_v2_4.md` §0.4.1 + §3.4) |
| IS-side change at v2.2 | None at atomic-unit body. Change-note-only emission. |
| Status | **CLOSED** at IS plan v2.2 + OD plan v2.4 cascade |

### §0.8 Backref reconciliation (Pattern P2 self-audit)

- All IS spec v1.2 citations preserved verbatim from v2.1; no version bump (IS spec unchanged at v1.2 per operator decision — C3-15 Path (i-refined) does not extend IS spec).
- All ADR citations preserved verbatim from v2.1 (F1 v1.2, F2 v1.2, F3 v1.1, D1 v1.1, D2 v1.1, D3 v1.2, D4 v1.1, D5 v1.3, D6 v1.1).
- F3-02 closure record cites `U-IS-12` (canonical at v2.1 §2.4 Cluster 4 — C2-pole selective bounded read contract) and `U-IS-17` (canonical at v2.1 §2.6 Cluster 6 — substrate seam exports manifest). Both citations resolve against v2.1 substrate.
- Cross-reference to OD plan v2.4 §0.4.1 + §3.4 (forward-citation — verified at OD plan v2.4 emission within Phase 6.5 Session 3 Segment 2; co-emission preserves cross-axis citation discipline).

### §0.9 Class 3 informational items surfaced at v2.2

| Item | Description | Routing |
|---|---|---|
| CXA-OD-IS-EDGE-DRIFT | CXA v2.1 §2.3.5 enumerates 6 OD→IS edges (per v2.1 baseline against OD plan v2.3 §4.5.1). OD plan v2.4 §4.5.1 enumerates 4 OD→IS edges per C3-15 Path (i-refined) deletions. Cardinality drift between CXA v2.1 and OD plan v2.4. | Route to future composition-document revision pass (Class 3 informational; non-blocking). Per Phase 6.5 Session 3 (ζ) Kickoff §2.2, CXA v2.1 is preserved at this session; no v2.2 emission of CXA. |

---

## §1 Spec inventory

[Preserved verbatim from `Implementation_Plan_Information_Substrate_v2_1.md` §1.]

## §2 Atomic-unit decomposition

[Preserved verbatim from `Implementation_Plan_Information_Substrate_v2_1.md` §2. All 17 units U-IS-01 through U-IS-17 unchanged at v2.2.]

## §3 Dependency graph

[Preserved verbatim from `Implementation_Plan_Information_Substrate_v2_1.md` §3. Within-axis DAG topology, cluster ordering, acyclicity verification, and backref reconciliations (RC-IS-1, RC-IS-2 if any) unchanged.]

## §4 Coverage matrix

[Preserved verbatim from `Implementation_Plan_Information_Substrate_v2_1.md` §4. 10 contracts × 17 units coverage matrix unchanged.]

## §5 [v2.1 filing footer preserved-by-reference; superseded by §6 at v2.2.]

---

## §6 Filing footer (v2.2)

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Information_Substrate_v2_2.md` |
| Version | v2.2 |
| Status | Proposed (v2.2 revision-pass close pending Phase 6.5 Session 3 ζ exit-criteria verification) |
| Date | 2026-05-15 |
| Predecessor | `Implementation_Plan_Information_Substrate_v2_1.md` (v2.1 canonical at Phase 6 close) |
| Authoring discipline | `implementation-planner` SKILL.md §8 revision-pass sub-mode |
| Revision scope | F3-02 absorption per Form A (operator decision Phase 6.5 Session 3 Segment 1, 2026-05-15) |
| Companion artifact | `Implementation_Plan_Operational_Discipline_v2_4.md` (substantive absorption site for F3-02 + C3-15) |
| Filing destination | `/mnt/user-data/outputs/Implementation_Plan_Information_Substrate_v2_2.md` → operator pushes to `/mnt/project/` |

---

*End of Implementation Plan — Information Substrate (IS axis) — v2.2.*
