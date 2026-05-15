# Implementation Plan — Operational Discipline (OD axis) — v2.4

*Revision-pass amendment to v2.3. Authored at Phase 6.5 Session 3 (ζ) — F3-02 IS-axis Revision Pass (broadened per OD-S2-1.A). Skill: `implementation-planner` SKILL.md §8 revision-pass sub-mode.*

---

## §0 Change-note

### §0.1 Predecessor

`Implementation_Plan_Operational_Discipline_v2_3.md` (v2.3 canonical at Phase 6 close per `P6-CK_Iter4_Revision_Cycle_Close_Handoff.md`; F2-12 cascade close + F2-04 hash-chain composition absorption).

### §0.2 Revision scope

v2.3 → v2.4: Two absorptions per Phase 6.5 Session 3 (ζ) operator decisions (Segment 1, 2026-05-15).

| Finding | Form / Path | Substantive surface |
|---|---|---|
| F3-02 | Form A — Citation precision | §3.4 U-OD-20 acceptance #11 + `Depends on` field: `U-IS-NN` → `U-IS-12` |
| C3-15 | Path (i-refined) — delete + remap | §4.5.1 IS-consuming edges: 6-row enumeration → 4-row enumeration (delete rows 2+3; remap rows 4+5) |

No other sections modified. All atomic-unit decomposition, dependency graph topology (within-axis), spec-traceability matrix, and AS/CP cross-axis edge enumerations preserved verbatim from v2.3.

### §0.3 Sections preserved verbatim from v2.3

| Section | Status |
|---|---|
| §1 Spec inventory | Preserved verbatim |
| §2 Cluster topology | Preserved verbatim |
| §3.1 Cluster 1 (U-OD-01 through U-OD-06) | Preserved verbatim |
| §3.2 Cluster 2 (U-OD-07 through U-OD-12) | Preserved verbatim |
| §3.3 Cluster 3 (U-OD-13 through U-OD-19) | Preserved verbatim |
| §3.4 Cluster 4 (U-OD-20) acceptance #1–#10, #12–#15, signatures, tests, rollback boundary | Preserved verbatim from v2.3 (acceptance #11 amended per §0.4.1) |
| §3.5 Cluster 5 (U-OD-21 + U-OD-22) | Preserved verbatim |
| §3.6 Cluster 6 (U-OD-23 through U-OD-33) | Preserved verbatim |
| §3.7 (any v2.3 supplementary cluster) | Preserved verbatim |
| §3.8 U-OD-34 (terminal aggregate exporter) | Preserved verbatim |
| §4.1 through §4.4 (within-axis dependency graph, acyclicity verification, topological sort) | Preserved verbatim |
| §4.5.2 AS-consuming edges (10 edges) | Preserved verbatim |
| §4.5.3 CP-consuming edges (12 edges) | Preserved verbatim |
| §4.5.4 (terminal aggregate cross-axis references, if separately enumerated at v2.3) | Preserved verbatim |
| §5 Spec-traceability matrix | Preserved verbatim |

### §0.4 Sections revised

#### §0.4.1 §3.4 U-OD-20 acceptance #11 (F3-02 Form A absorption)

[All other acceptance criteria (#1–#10, #12–#15), signatures, internal logic, tests, and rollback boundary at U-OD-20 preserved verbatim from v2.3.]

`Depends on:` field at U-OD-20 amended from v2.3:

```
v2.3: Depends on: [U-OD-18, U-OD-19, U-IS-NN (cross-axis: IS — C-IS-10 §10.2)]
v2.4: Depends on: [U-OD-18, U-OD-19, U-IS-12 (cross-axis: IS — C-IS-10 §10.2)]
```

Acceptance #11 prose amended from v2.3:

```
v2.3 (F3-02 acknowledged-deferred at Iter 4):
"Cross-axis edge per OD-S4-3.A: Depends on: [U-IS-NN (cross-axis: IS —
C-IS-10 §10.2 unit)]. Resolution at U-OD-34 (preserved from v2.2). At
v2.3, F3-02 acknowledged-deferred per revision-cycle session-open OD:
defer to future IS-axis revision-pass; U-IS-NN remains an informational
placeholder at v2.3. The OD-side composition surface declared at this
unit's acceptance #15 (hash-chain integrity composition per OD spec
v1.3 §14.5.1) is independent of the IS-axis canonical ledger-write site
ownership and stands at v2.3 absent the IS-axis resolution. Future
IS-axis revision-pass will resolve U-IS-NN to a concrete IS-axis
ledger-schema unit; at that point this acceptance criterion's
cross-axis edge will be canonical rather than placeholder, and the
OD-side composition at #15 will gain cross-axis dependency to the
canonical IS-axis unit."

v2.4 (F3-02 CLOSED per Form A):
"Cross-axis edge per OD-S4-3.A: Depends on: [U-IS-12 (cross-axis: IS —
C-IS-10 §10.2 idempotency-key join carrier)]. Resolution at U-OD-34
(preserved from v2.2). At v2.4, F3-02 CLOSED per Phase 6.5 Session 3
(ζ) operator decision (Form A — citation precision, 2026-05-15): the
canonical IS-axis carrier for C-IS-10 §10.2 IDEMPOTENCY_KEY_JOIN_EXPORT
consumption is U-IS-12 per IS plan v2.1 §2.4 Cluster 4 (C2-pole
selective bounded read contract) + IS plan v2.1 §2.6 U-IS-17 substrate
seam exports manifest. No IS-axis new-unit revision required;
F3-02 was a citation-precision defect at OD plan v2.3, not an IS-plan
completeness defect. The OD-side composition surface declared at this
unit's acceptance #15 (hash-chain integrity composition per OD spec
v1.3 §14.5.1) gains canonical cross-axis dependency to U-IS-12
(idempotency-key join carrier) + U-IS-07 (entry shape carrier — C-IS-10
§10.1 STATE_LEDGER_ENTRY_SHAPE_EXPORT) per the same manifest."
```

No test additions at v2.4 for F3-02 absorption (citation-precision only; functional surface unchanged from v2.3).

Rollback boundary at U-OD-20 amended from v2.3 by appending one sentence at the end of the v2.3 rollback boundary:

```
v2.4 amendment to rollback boundary (appended):
"Revert v2.4 F3-02 closure — revert Depends on field U-IS-12 → U-IS-NN
and revert acceptance #11 prose to v2.3 (F3-02 acknowledged-deferred);
the cross-axis edge cardinality at this unit is preserved (1 OD→IS
edge); only the canonical-carrier identification changes. v2.3
amendment rollback boundaries (F2-04 hash-chain absorption + v2.2
dedup+orthogonality+invariance+per-attempt-cost-attribution closure
substrate) preserved verbatim from v2.3 — F3-02 revert does NOT regress
v2.3 hash-chain composition surface or v2.2 F2-12 closure substrate."
```

#### §0.4.2 §4.5.1 IS-consuming edges (C3-15 Path (i-refined) absorption)

v2.3 6-row enumeration revised at v2.4 to 4-row enumeration. Revised table:

| # | Source OD unit | Cross-axis target | Contract anchor | Aggregate manifest entry |
|---|---|---|---|---|
| 1 | U-OD-20 | U-IS-12 (idempotency-key join carrier) | C-IS-10 §10.2 | U-OD-34 export #6 |
| 2 | U-OD-30 | U-IS-11 (JSONL write contract carrier) | C-IS-10 §10.5 | U-OD-34 export #8 |
| 3 | U-OD-30 | U-IS-10 (hash-chain verification carrier) | C-IS-10 §10.3 | U-OD-34 export #8 |
| 4 | U-OD-34 | U-IS-17 (terminal aggregate exporter) | IS substrate seam exports | (terminal aggregate reference) |

**Deletion record (v2.4 amendment to v2.3 §4.5.1):**

| Deleted row (v2.3 enumeration) | v2.3 placeholder target | v2.3 cited contract | Deletion rationale |
|---|---|---|---|
| U-OD-27 → sqlite substrate | U-IS-NN | C-IS-13 §13.2 (non-resolving in IS spec v1.2) | Mis-routed: sqlite substrate residence is OD-axis internal (per OD axis decomposition; sqlite is the OD-side durable substrate, not an IS-axis primitive). U-OD-27's sqlite-related acceptance criteria within the unit body remain unchanged and within OD-internal scope. The v2.3 §4.5.1 row falsely declared an OD→IS cross-axis edge where no such edge exists. |
| U-OD-27 → ring-buffer eviction | U-IS-NN | C-IS-08 §8.4 (sub-section non-existent in IS spec v1.2) | Mis-routed: ring-buffer eviction is sqlite-internal OD-axis policy (composes on the deleted sqlite substrate row above). Same disposition. |

**Remap record (v2.4 amendment to v2.3 §4.5.1):**

| Source row (v2.3 enumeration) | v2.3 placeholder target | v2.3 cited contract | v2.4 target unit | v2.4 canonical contract | Carrier rationale |
|---|---|---|---|---|---|
| U-OD-30 → Tier-5 audit ledger durability | U-IS-NN | C-IS-14 §14.2 (non-resolving in IS spec v1.2) | **U-IS-11** (C3-pole append-only write contract per IS plan v2.1 §2.4 Cluster 4) | **C-IS-10 §10.5** (JSONL_EVENT_LEDGER_FORMAT_EXPORT) | Audit-ledger durability composes on the JSONL event ledger format export at C-IS-10 §10.5 (manifest carriers: U-IS-05, U-IS-07, U-IS-11, U-IS-12 per IS plan v2.1 §2.6 U-IS-17). For *durability* specifically — the persistent write substrate — U-IS-11 is the canonical carrier. Mirrors AS-side composition pattern at U-AS-27 → U-IS-11 for C-AS-08 §8.4 audit-ledger write surface per CXA v2.1 §2.3.1. |
| U-OD-30 → hash-chain integrity | U-IS-NN | C-IS-13 §13.5 (non-resolving in IS spec v1.2) | **U-IS-10** (chain verification primitive per IS plan v2.1 §2.3 Cluster 3) | **C-IS-10 §10.3** (HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT) | Hash-chain integrity is canonically IS-axis at C-IS-06 (4-step discipline: canonicalize → SHA-256 → prior-event chain construction → verification + tamper-evidence). Export seam at C-IS-10 §10.3 (manifest carriers: U-IS-08 canonicalize, U-IS-09 chain construction, U-IS-10 verification per IS plan v2.1 §2.6 U-IS-17). For *integrity* (verification + tamper-evidence) specifically, U-IS-10 is the canonical carrier. Mirrors AS-side composition pattern at U-AS-26 → U-IS-10 for C-AS-08 §8.3 audit-ledger chain verification per CXA v2.1 §2.3.1. |

#### §0.4.3 §6 Filing footer

Version bumped to v2.4; change-note pointer added.

### §0.5 Coverage matrix delta

None at cluster-to-contract level. All 5 §4.5.1 row dispositions preserve U-OD-20 + U-OD-27 + U-OD-30 + U-OD-34 coverage of their OD-spec contract anchors (unchanged at v2.4). The mis-routed v2.3 rows (deletions 2+3) had non-resolving IS-spec citations; their deletion does NOT regress any canonical OD-spec coverage. The remapped v2.3 rows (4+5) preserve OD-side cross-axis composition with canonical IS-spec citations replacing non-resolving citations.

### §0.6 Dependency-graph delta

Within-axis DAG: unchanged. All 34 OD units preserved verbatim; topological sort unchanged; acyclicity preserved.

Cross-axis OD→IS edge cardinality:

```
v2.3 §4.5.1: 6 OD→IS edges (1 canonical, 4 placeholder/non-resolving, 1 terminal)
v2.4 §4.5.1: 4 OD→IS edges (3 canonical, 1 terminal)
Net delta:   −2 edges (rows 2+3 mis-routed deletions)
```

Within-axis dependency graph at U-OD-20:

```
v2.3: Depends on: [U-OD-18, U-OD-19, U-IS-NN (cross-axis: IS — C-IS-10 §10.2)]
v2.4: Depends on: [U-OD-18, U-OD-19, U-IS-12 (cross-axis: IS — C-IS-10 §10.2)]
```

Within-axis dependencies (U-OD-18, U-OD-19) unchanged. Cross-axis edge cardinality at this unit unchanged (1 edge); canonical-carrier identification changes from placeholder to U-IS-12.

Within-axis dependency graph at U-OD-27 + U-OD-30: unchanged (deletions and remaps in §4.5.1 manifest the *cross-axis* edge enumeration; within-axis topology at the affected units is unaffected).

### §0.7 Finding closure record

| Finding | Form / Path | Substantive surface at v2.4 | Status |
|---|---|---|---|
| F3-02 | Form A — Citation precision | §3.4 U-OD-20 `Depends on` (U-IS-NN → U-IS-12) + acceptance #11 prose (acknowledged-deferred → CLOSED) | **CLOSED** |
| C3-15 | Path (i-refined) — delete + remap | §4.5.1 6-row → 4-row enumeration (rows 2+3 deleted as OD-internal mis-routed; rows 4+5 remapped to canonical IS contracts; row 1 placeholder canonicalized) | **CLOSED** |

Closure cascade: IS plan v2.2 (companion artifact, change-note-only emission per Form A) + OD plan v2.4 (this artifact). Both filed at Phase 6.5 Session 3 (ζ) Segment 2.

### §0.8 Backref reconciliation (Pattern P2 self-audit)

- All v2.4 §4.5.1 target IS-plan units (U-IS-10, U-IS-11, U-IS-12, U-IS-17) verified against `Implementation_Plan_Information_Substrate_v2_1.md` substrate (preserved at v2.2 per change-note §0.3).
- All v2.4 §4.5.1 cited IS-spec contracts (C-IS-10 §10.2, §10.3, §10.5) verified against `Spec_Information_Substrate_v1.md` (IS spec v1.2 canonical at Phase 6 close; unchanged at this session per C3-15 Path (i-refined) operator decision).
- v2.4 acceptance #11 prose cite to "U-IS-07 (entry shape carrier — C-IS-10 §10.1 STATE_LEDGER_ENTRY_SHAPE_EXPORT)" verified against IS plan v2.1 §2.3 Cluster 3 + §2.6 U-IS-17 manifest.
- All other v2.3 citations (OD spec v1.3 §X, ADR-D6 v1.2 §X, C-OD-NN, etc.) preserved verbatim; no version bump required.
- CXA v2.1 §2.3.5 OD→IS edge enumeration (6 edges at v2.1 baseline) NOT updated at this session per Phase 6.5 Session 3 (ζ) Kickoff §2.2 (CXA preserved at v2.1; out-of-scope). Resulting cardinality drift (CXA v2.1: 6 edges; OD plan v2.4: 4 edges) surfaced as Class 3 informational item at §0.9 below.

### §0.9 Out-of-scope items / Class 3 surfacing

| Item | Description | Class | Routing |
|---|---|---|---|
| CXA-OD-IS-EDGE-DRIFT | CXA v2.1 §2.3.5 enumerates 6 OD→IS edges (v2.1 baseline against OD plan v2.3 §4.5.1). OD plan v2.4 §4.5.1 enumerates 4 OD→IS edges per C3-15 Path (i-refined) deletions. Cardinality + per-row carrier-unit citation drift between CXA v2.1 and OD plan v2.4. | 3 | Future composition-document revision pass (non-blocking). Surfaced at Session 3 close handoff. |
| OD-INTERNAL-FORMALIZATION | The C3-15 Path (i-refined) deletion record (rows 2+3 of v2.3 §4.5.1) identifies sqlite substrate residence + ring-buffer eviction as OD-internal concerns falsely declared as OD→IS cross-axis edges at v2.3. The OD plan does not currently have an explicit "OD-internal cross-cluster dependency" section that would canonicalize these compositions outside §4.5.* cross-axis enumeration. The acceptance criteria within U-OD-27 already describe these compositions implicitly; explicit formalization is not blocking. | 3 | Future OD plan revision pass (non-blocking) OR Session 6 (ε) bootstrap substrate authoring (if implementation surface requires explicit dependency declaration). Surfaced at Session 3 close handoff. |

---

## §1 Spec inventory

[Preserved verbatim from `Implementation_Plan_Operational_Discipline_v2_3.md` §1.]

## §2 Cluster topology

[Preserved verbatim from `Implementation_Plan_Operational_Discipline_v2_3.md` §2.]

## §3 Atomic-unit decomposition

[Preserved verbatim from `Implementation_Plan_Operational_Discipline_v2_3.md` §3 except as follows.]

### §3.4 U-OD-20 (v2.4 amendment to acceptance #11 + Depends on + rollback boundary)

[All other content at §3.4 preserved verbatim from v2.3. Substantive amendment scope per §0.4.1: `Depends on` field, acceptance #11 prose, rollback boundary appended sentence. Acceptances #1–#10 + #12–#15, signatures, internal logic, and v2.3-existing tests preserved verbatim from v2.3.]

`Depends on:` `[U-OD-18, U-OD-19, U-IS-12 (cross-axis: IS — C-IS-10 §10.2)]`

[Acceptance #1 through #10 preserved verbatim from v2.3.]

**Acceptance #11** (v2.4 amendment per §0.4.1):

Cross-axis edge per OD-S4-3.A: `Depends on: [U-IS-12 (cross-axis: IS — C-IS-10 §10.2 idempotency-key join carrier)]`. Resolution at U-OD-34 (preserved from v2.2).

At v2.4, F3-02 **CLOSED** per Phase 6.5 Session 3 (ζ) operator decision (Form A — citation precision, 2026-05-15): the canonical IS-axis carrier for C-IS-10 §10.2 IDEMPOTENCY_KEY_JOIN_EXPORT consumption is **U-IS-12** per IS plan v2.1 §2.4 Cluster 4 (C2-pole selective bounded read contract; carrier surface — per `Implementation_Plan_Information_Substrate_v2_2.md` §0.7 closure record) and IS plan v2.1 §2.6 U-IS-17 substrate seam exports manifest. No IS-axis new-unit revision required; F3-02 was a citation-precision defect at OD plan v2.3, not an IS-plan completeness defect.

The OD-side composition surface declared at this unit's acceptance #15 (hash-chain integrity composition per OD spec v1.3 §14.5.1) gains canonical cross-axis dependency to **U-IS-12** (idempotency-key join carrier per C-IS-10 §10.2) + **U-IS-07** (entry shape carrier per C-IS-10 §10.1 STATE_LEDGER_ENTRY_SHAPE_EXPORT) per the same manifest.

[Acceptance #12 through #15 preserved verbatim from v2.3.]

[Signatures + internal logic + tests preserved verbatim from v2.3.]

**Rollback boundary** (v2.4 amendment per §0.4.1):

[v2.3 rollback boundary preserved verbatim; v2.4 appendix:]

Revert v2.4 F3-02 closure — revert `Depends on` field `U-IS-12` → `U-IS-NN` and revert acceptance #11 prose to v2.3 (F3-02 acknowledged-deferred); the cross-axis edge cardinality at this unit is preserved (1 OD→IS edge); only the canonical-carrier identification changes. v2.3 amendment rollback boundaries (F2-04 hash-chain absorption + v2.2 dedup+orthogonality+invariance+per-attempt-cost-attribution closure substrate) preserved verbatim from v2.3 — F3-02 revert does NOT regress v2.3 hash-chain composition surface or v2.2 F2-12 closure substrate.

[All other §3 sub-sections (§3.1, §3.2, §3.3, §3.5, §3.6, §3.7, §3.8) preserved verbatim from `Implementation_Plan_Operational_Discipline_v2_3.md`.]

## §4 Dependency graph

[Preserved verbatim from `Implementation_Plan_Operational_Discipline_v2_3.md` §4.1 through §4.4. §4.5.1 amended per §0.4.2; §4.5.2 + §4.5.3 preserved verbatim; §4.5.4 (if present at v2.3) preserved verbatim.]

### §4.5 Cross-axis edge enumeration

#### §4.5.1 IS-consuming edges (v2.4: 4 edges per C3-15 Path (i-refined) absorption)

| Source OD unit | Cross-axis target | Contract anchor | Aggregate manifest entry |
|---|---|---|---|
| U-OD-20 | U-IS-12 (idempotency-key join carrier) | C-IS-10 §10.2 | U-OD-34 export #6 |
| U-OD-30 | U-IS-11 (JSONL write contract carrier) | C-IS-10 §10.5 | U-OD-34 export #8 |
| U-OD-30 | U-IS-10 (hash-chain verification carrier) | C-IS-10 §10.3 | U-OD-34 export #8 |
| U-OD-34 | U-IS-17 (terminal aggregate exporter) | IS substrate seam exports | (terminal aggregate reference) |

v2.3 →  v2.4 row delta (deletion + remap records canonical at §0.4.2):

```
DELETED: U-OD-27 → U-IS-NN (sqlite substrate) — C-IS-13 §13.2     [mis-routed OD-internal]
DELETED: U-OD-27 → U-IS-NN (ring-buffer eviction) — C-IS-08 §8.4   [mis-routed OD-internal]
REMAP:   U-OD-30 → U-IS-11 (was C-IS-14 §14.2 → now C-IS-10 §10.5)
REMAP:   U-OD-30 → U-IS-10 (was C-IS-13 §13.5 → now C-IS-10 §10.3)
PRESERVED: U-OD-20 → U-IS-12 (was U-IS-NN → now canonical U-IS-12)
PRESERVED: U-OD-34 → U-IS-17 (terminal aggregate)
```

#### §4.5.2 AS-consuming edges (10 edges)

[Preserved verbatim from `Implementation_Plan_Operational_Discipline_v2_3.md` §4.5.2.]

#### §4.5.3 CP-consuming edges (12 edges)

[Preserved verbatim from `Implementation_Plan_Operational_Discipline_v2_3.md` §4.5.3.]

#### §4.5.4 (Terminal aggregate / supplementary cross-axis enumeration, if separately enumerated at v2.3)

[Preserved verbatim from `Implementation_Plan_Operational_Discipline_v2_3.md` §4.5.4.]

## §5 Spec-traceability

[Preserved verbatim from `Implementation_Plan_Operational_Discipline_v2_3.md` §5.]

---

## §6 Filing footer (v2.4)

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_4.md` |
| Version | v2.4 |
| Status | Proposed (v2.4 revision-pass close pending Phase 6.5 Session 3 ζ exit-criteria verification) |
| Date | 2026-05-15 |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_3.md` (v2.3 canonical at Phase 6 close; F2-12 cascade + F2-04 hash-chain absorption) |
| Authoring discipline | `implementation-planner` SKILL.md §8 revision-pass sub-mode |
| Revision scope | F3-02 absorption (Form A — citation precision) + C3-15 absorption (Path (i-refined) — delete + remap) per Phase 6.5 Session 3 (ζ) operator decisions (Segment 1, 2026-05-15) |
| Companion artifact | `Implementation_Plan_Information_Substrate_v2_2.md` (IS-side closure record for F3-02; change-note-only emission per Form A) |
| Filing destination | `/mnt/user-data/outputs/Implementation_Plan_Operational_Discipline_v2_4.md` → operator pushes to `/mnt/project/` |

---

*End of Implementation Plan — Operational Discipline (OD axis) — v2.4.*
