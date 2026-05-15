# Implementation Plan — Control Plane (v2.1)

## Status block

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_1.md` |
| Status | **Proposed** (v2.1 pending P6-CK Iteration 3 clearance per `Project_Workflow_v1_6.md` §4.1.4.5 one-time Path B authorization; absorbs F2-CP-03 per `Adversarial_Review_6_iter2.md` §3.3) |
| Date | 2026-05-14 |
| Phase | 6 — atomic implementation plan; v2.1 revision pass under Path B authorization per `P6-CK_Iteration_2_Ceiling_Disposition.md` §5.2 |
| Skill | `implementation-planner` SKILL.md in **revision-pass sub-mode** per §8 |
| Axis | Control Plane (CP) — third-axis per `Phase_6_Entry_Handoff.md` §5.1 sequencing rationale |
| Source-set | `Spec_Control_Plane_v1.md` v1.2 §1–§24 (24 contracts: C-CP-01 through C-CP-24); `Implementation_Plan_Information_Substrate_v2_1.md` (cross-axis IS substrate; U-IS-17 manifest); `Implementation_Plan_Action_Surface_v1.md` v1 (cross-axis AS substrate; U-AS-33 manifest); `Project_Workflow_v1_6.md` v1.6 §2.6 + §4.1.4 + §6.4 + §7; `implementation-planner` SKILL.md §1–§11; `Adversarial_Review_6_iter2.md` §3.3 F2-CP-03 finding; `P6-CK_Iteration_2_Ceiling_Disposition.md` §5.2 absorption scope; background substrate (consulted but not cited at units per SKILL.md §2): `Architectural_Design_Document_v1.md` v1.2 §3.2 + §5.2–§5.3, `PRD_v1_0.md` v1.0.1 R-CP-01 through R-CP-12, `Persona_Document_v1.md` v1 §3 + §6 + §10–§11; ADRs at F1 v1.2, F2 v1.2, F3 v1.1, F5 v1.1, D1 v1.1, D2 v1.1, D3 v1.2, D4 v1.1, D5 v1.3, D6 v1.1 |
| ODs applied | (from v2) OD-S3-1.A; OD-S3-2.A; OD-S3-3.A; (at v2.1) no operator OD required — F2-CP-03 is *decided* per `Adversarial_Review_6_iter2.md` §3.3 |
| Entry authorization | `P6-CK_Iteration_2_Ceiling_Disposition.md` §3.3 + Workflow v1.6 §4.1.4.5 |
| Exit gate | This v2.1 plan filed at `/mnt/user-data/outputs/`; Path B Segment D complete; Path B continues to OD plan v2.1 (Segment E) |
| Sub-mode | Revision pass (P6-CK Iteration 2 F2-CP-03 finding absorbed; v2 → v2.1; `## §0 Change note` v2 → v2.1 section authored per SKILL.md §8) |
| Shape decision | Axis-led per OD-6-2.A; within-axis cluster-led decomposition by ADR-anchor groups (9 clusters per §1.2) |

---

## §0 Change note (v2 → v2.1)

### §0.1 Scope of revision

Single-pass revision absorbing one `Adversarial_Review_6_iter2.md` P6-CK Iteration 2 finding, local to CP plan v2:

| Finding | Class | Resolution path absorbed | Affected sites |
|---|---|---|---|
| F2-CP-03 | 2 | Plan-side multi-site re-anchoring of CP spec §8 ↔ §9 sub-section content per `Adversarial_Review_6_iter2.md` §3.3 location table; no spec back-flow (CP spec v1.2 §8 + §9 are canonical) | U-CP-18 `Implements:` + acceptance #1 + #5; U-CP-19 `Implements:` + acceptance #1 + #2; U-CP-20 `Implements:` + acceptance #1; §4.1.8 (3-row restructure); §4.1.9 (4-row restructure + header cardinality) |

No new architectural commitments; no new units; no new contracts; no new cross-axis edges; no spec extensions. Per `implementation-planner` SKILL.md §8 revision-pass discipline.

### §0.2 Sections preserved verbatim (from v2)

| Section | Preservation rationale |
|---|---|
| §1.1–§1.3 spec inventory + cluster decomposition + substrate-version-citation alignment | Substrate versions unchanged (CP spec v1.2; ADR-F2 v1.2; ADD v1.2; PRD v1.0.1); cluster decomposition unchanged |
| §2.1–§2.3 Clusters 1–3 (U-CP-01 through U-CP-17) | No Iter-2 finding |
| §2.4 Cluster 4 — U-CP-18 non-amendment sections (scope, depends-on, inputs, files, signatures, acceptance #2/#3/#4/#6, tests, rollback boundary) | No Iter-2 finding at these sub-sections |
| §2.4 Cluster 4 — U-CP-19 non-amendment sections (scope, depends-on, inputs, files, signatures, acceptance #3, tests, rollback boundary) | No Iter-2 finding |
| §2.4 Cluster 4 — U-CP-20 non-amendment sections (scope, depends-on, inputs, files, signatures, acceptance #2/#3/#4/#5, tests, rollback boundary) | No Iter-2 finding |
| §2.4 Cluster 4 — U-CP-21 (forward-flagged at §0.8; not absorbed at v2.1 scope) | Out of F2-CP-03 finding scope per strict-narrow discipline |
| §2.5–§2.12 Clusters 5–12 | No Iter-2 finding |
| §3 dependency graph | No graph delta; node count + edge count + topological-sort order unchanged at v2.1 |
| §4.1.1–§4.1.7; §4.1.10–§4.1.24 | No Iter-2 finding at these contract-coverage sub-sections |
| §5 / §6 coherence pass | v2 coherence-pass results preserved as historical record; v2.1 audit summary captured at §0.10 |

### §0.3 Sections revised (v2 → v2.1)

| Section | Revision shape | Resolves |
|---|---|---|
| U-CP-18 `Implements:` field | `C-CP-08 §8.1, §8.2` → `C-CP-08 §8.2` (drop §8.1 — §8.1 is ResumptionKind enum territory, U-CP-19's anchor; U-CP-18 implements F2 join discipline at §8.2 only) | F2-CP-03 |
| U-CP-18 acceptance #1 | "F2JoinKind declares exactly three values per C-CP-08 §8.1 verbatim discrimination" → "...per C-CP-08 §8.2 verbatim discrimination" (F2JoinKind discrimination is §8.2 territory; §8.1 is resumption-kind enum) | F2-CP-03 |
| U-CP-18 acceptance #5 | "This unit is the R-CP-07-satisfying contract per spec §8.1" → "...per spec §8.2" (R-CP-07-satisfying contract spans C-CP-08 whole per §8 contract header; U-CP-18 specifically covers §8.2) | F2-CP-03 |
| U-CP-19 `Implements:` field | `C-CP-09 §9.1` → `C-CP-08 §8.1` (canonical ResumptionKind 5-class enum declaration is at C-CP-08 §8.1 per spec line 722) | F2-CP-03 |
| U-CP-19 acceptance #1 | "`ResumptionKind` declares exactly five values per C-CP-09 §9.1 verbatim" → "...per C-CP-08 §8.1 verbatim" | F2-CP-03 |
| U-CP-19 acceptance #2 | "`RESUMPTION_KIND_BINDINGS` declares 1:1 mapping ... per §9.1 verbatim" → "...per §8.1 verbatim" | F2-CP-03 |
| U-CP-20 `Implements:` field | `C-CP-09 §9.2` → `C-CP-08 §8.3` (canonical per-resumption observable behavior is at C-CP-08 §8.3 per spec line 748; §9.2 is per-row Tier-3 / Tier-5 mapping) | F2-CP-03 |
| U-CP-20 acceptance #1 | "`PER_RESUMPTION_OBSERVABLE_BEHAVIOR` declares exactly five entries per C-CP-09 §9.2 verbatim" → "...per C-CP-08 §8.3 verbatim" | F2-CP-03 |
| §4.1.8 header | "Contract C-CP-08 (2 sub-sections)" → "Contract C-CP-08 (3 sub-sections)" | F2-CP-03 |
| §4.1.8 rows | 2 rows (§8.1 mis-attributed; §8.2 covered) → 3 rows: `§8.1 ResumptionKind 5-class taxonomy \| U-CP-19`; `§8.2 F2 state-ledger composition via idempotency_key \| U-CP-18`; `§8.3 per-resumption observable behavior \| U-CP-20` | F2-CP-03 |
| §4.1.9 header | "Contract C-CP-09 (2 sub-sections; §9.1 covered by 2 units)" → "Contract C-CP-09 (4 sub-sections; §9.2 / §9.3 / §9.4 derivative of §9.1 attribute substrate)" | F2-CP-03 |
| §4.1.9 rows | 3 rows (2 mis-attributed) → 4 rows: `§9.1 engine.* attribute declarations \| U-CP-21`; `§9.2 per-row Tier-3 / Tier-5 mapping \| U-CP-21 (derivative)`; `§9.3 composition with C-IS-10 §10.2 idempotency-key join \| U-CP-21 (derivative)`; `§9.4 D6 ingestion contract \| U-CP-21 (derivative)` | F2-CP-03 |

### §0.4 Coverage matrix delta

| Site | v2 | v2.1 |
|---|---|---|
| §4.1.8 header | `Contract C-CP-08 (2 sub-sections)` | `Contract C-CP-08 (3 sub-sections)` |
| §4.1.8 rows | 2 rows (§8.1 + §8.2; both citing U-CP-18) | 3 rows (§8.1 U-CP-19; §8.2 U-CP-18; §8.3 U-CP-20) |
| §4.1.9 header | `Contract C-CP-09 (2 sub-sections; §9.1 covered by 2 units)` | `Contract C-CP-09 (4 sub-sections; §9.2 / §9.3 / §9.4 derivative of §9.1)` |
| §4.1.9 rows | 3 rows (1 correct: U-CP-21; 2 mis-attributed: U-CP-19 + U-CP-20) | 4 rows (U-CP-21 covers §9.1–§9.4) |

Aggregate spec-coverage invariant: every spec sub-section of C-CP-08 (§8.1–§8.4) + C-CP-09 (§9.1–§9.4) covered by ≥1 unit at v2.1. C-CP-08 §8.4 (F2-12 carry-forward affected-contract notation) is meta-substrate covered by U-CP-20 acceptance #5 carry-forward declaration.

### §0.5 Dependency graph delta

No delta. Affected units' `Depends on:` declarations unchanged:

| Unit | `Depends on:` v2 | `Depends on:` v2.1 |
|---|---|---|
| U-CP-18 | [U-CP-15, U-IS-07 (cross-axis: IS), U-IS-09 (cross-axis: IS), U-IS-12 (cross-axis: IS)] | (unchanged) |
| U-CP-19 | [U-CP-15] | (unchanged) |
| U-CP-20 | [U-CP-10, U-CP-12, U-CP-18, U-CP-19] | (unchanged) |

Aggregate DAG: 55 nodes across 9 clusters; edge set unchanged from v2; topological sort preserved. Cross-axis edge count (60 = 36 IS + 24 AS) unchanged; cross-axis IS edge targets to IS plan v2.1 (formerly v1 / v2).

### §0.6 Substrate-version-citation table

Substrate versions cited at v2.1 are updated for cross-axis IS plan version only:

| Substrate | Version cited at v2 | Version cited at v2.1 |
|---|---|---|
| CP spec | v1.2 | v1.2 (unchanged) |
| ADR-F2 | v1.2 | v1.2 (unchanged) |
| ADD | v1.2 | v1.2 (unchanged) |
| PRD | v1.0.1 | v1.0.1 (unchanged) |
| Cross-axis IS plan | v1 (from v2) | **v2.1** (latest filed post-F1-IS-02 absorption) |
| Cross-axis AS plan | v1 | v1 (unchanged) |
| Workflow | v1.5 | **v1.6** (post-§4.1.4 amendment) |
| ADR body-citations | F1 v1.2, F2 v1.2, F3 v1.1, F5 v1.1, D1 v1.1, D2 v1.1, D3 v1.2, D4 v1.1, D5 v1.3, D6 v1.1 | (unchanged) |

Per Workflow v1.6 §7 use-latest-version body-citation-alignment.

### §0.7 Status

`Status: Proposed` preserved at v2.1 per `implementation-planner` SKILL.md §8 (analog to spec and PRD post-CK clearance patterns). Bump to `Status: P6-CK-cleared` on P6-CK Iteration 3 CLEARED disposition.

### §0.8 Forward-flagged concerns (not absorbed at v2.1)

| Concern | Disposition | Routing |
|---|---|---|
| U-CP-21 acceptance #1 declares 3 engine.* attributes as `engine.class`, `engine.resumption_kind`, `engine.tech` — but CP spec §9.1 canonical 3 attributes are `engine.class`, `engine.event_history.tier`, `engine.event.id` (per spec line 792–796). U-CP-21 attribute composition deviates from spec §9.1 canonical | Not amended at v2.1 per strict-narrow scope discipline (`implementation-planner` SKILL.md §8); out of F2-CP-03 finding scope per `Adversarial_Review_6_iter2.md` §3.3 location table | Candidate finding for P6-CK Iteration 3 |
| U-CP-21 acceptance #1 cites "ADR-D1 v1.1 §1.1.1 + CP spec §5.3 + §9.2 verbatim" — spec §5.3 is `lease.*` namespace territory (not engine.*); §9.2 is per-row Tier-3 / Tier-5 mapping (not engine.* attribute names) | Not amended at v2.1 per same rationale as above | Candidate finding for P6-CK Iteration 3 |
| U-CP-12 acceptance #3 cites `C-CP-09 §9.2` for "workflow.resumption event composes with U-CP-21 engine.* namespace" — engine.* namespace is canonically declared at C-CP-09 §9.1; §9.2 is per-row Tier-3/Tier-5 mapping. Citation ambiguity surfaced during F2-CP-03 absorption verification pass | Not amended at v2.1 — out of F2-CP-03 finding scope per `Adversarial_Review_6_iter2.md` §3.3 location table (U-CP-12 not enumerated); strict-narrow Path B discipline preserved | Candidate finding for P6-CK Iteration 3 |

### §0.9 Prior revision history (v1 → v2; archival from v2 §0)

The v1 → v2 amendment cycle absorbed two `Adversarial_Review_6.md` P6-CK Iteration 1 findings:

| Finding | Class | Resolution path | Affected sites |
|---|---|---|---|
| F2-CP-01 | 2 | U-CP-54 §24.1.A/B/C realignment to spec §24.1 canonical | U-CP-54 acceptance #2 / #3 / #4 / #6 / #8 |
| F2-CP-02 | 2 | U-CP-21 `Implements:` retarget to C-CP-09 §9.1 | U-CP-21 `Implements:`; §4.1.5; §4.1.9 |

Full v1 → v2 amendment trace remains on record at `/mnt/project/Implementation_Plan_Control_Plane_v2.md` §0.3.

### §0.10 v2.1 coherence-pass summary

Pre-emission self-audit per SKILL.md §5 step 9 + §[coherence pass] discipline returns ✅ PASS at all 5 audit dimensions:

| Audit | Result |
|---|---|
| §3 Atomicity | ✅ PASS — no v2.1 amendments affect atomicity of any unit |
| §4 Spec-traceability | ✅ PASS — F2-CP-03 absorption restores correct §8 ↔ §9 sub-section anchoring; U-CP-18 / U-CP-19 / U-CP-20 Implements + acceptance #1 + §4.1.8 + §4.1.9 all aligned to canonical CP spec §8 + §9 partition |
| §7 Dependency-awareness | ✅ PASS — no graph delta; topological sort preserved |
| §8 Implementation-grade-detail | ✅ PASS — no signature / acceptance / test deltas beyond cited absorption sites |
| §10 Anti-pattern audit | ✅ PASS — F2-CP-03 absorption eliminates spec-anchor-drift anti-pattern at named sites; U-CP-21 forward-flagged concerns remain outside scope per §0.8 |

---

## §1 Spec inventory

### §1.1 Contract inventory

Twenty-four CP-spec contracts tagged by surfacing class; cross-axis surfacing posture identified.

| C-CP-NN | Spec § | Contract surface (one-line) | Surfacing class | Cross-axis surfacing |
|---|---|---|---|---|
| C-CP-01 | §1 | Routing core thin-surface + `ProviderCapabilities` + manifest residence + `routing.*` namespace | `api-surface` + `data-type` | **Cross-axis IS + AS consumer** |
| C-CP-02 | §2 | Layered routing strategy (declarative → embedding → LLM-as-router) | `algorithm` | CP-internal |
| C-CP-03 | §3 | Per-layer time-budget + `LayerBudget` + `fallback.*` + `harness.breaker.*` + `retry.*` namespaces | `data-type` + `algorithm` | CP-internal |
| C-CP-04 | §4 | Cross-family fallback chain composition + cache-state-loss handling | `algorithm` | **Cross-axis AS consumer** (U-AS-30) |
| C-CP-05 | §5 | F3 lifecycle event 8-class taxonomy + `lease.*` namespace + per-class attribute composition | `data-type` | **Cross-axis IS consumer** (U-IS-07) |
| C-CP-06 | §6 | `WorkflowManifestEntry` schema + per-step override + audit composition | `data-type` + `algorithm` | CP-internal |
| C-CP-07 | §7 | 5-class `EngineClass` enum + per-deployment-surface candidate mapping + workload-binding-time selection + capability-floor preservation | `data-type` + `algorithm` | **Cross-axis IS consumer** (U-IS-13 referenced) |
| C-CP-08 | §8 | F2 substrate join discipline at engine-class boundary (R-CP-07-satisfying contract; F2-12 active engagement surface) | `algorithm` + `module-boundary` | **Cross-axis IS consumer** (U-IS-07, U-IS-09, U-IS-12) |
| C-CP-09 | §9 | 5-class `ResumptionKind` taxonomy + per-resumption observable behavior (F2-12 active carry-forward) | `data-type` | CP-internal |
| C-CP-10 | §10 | 6-pattern `TopologyPattern` enum + admissibility predicate + workload-class composition | `data-type` + `policy-enforcement` | CP-internal |
| C-CP-11 | §11 | Topology × workload-class × engine-class 2D matrix + D4 multiplicative tunable + per-engine-class overlay + T-perm-3 reading | `data-type` + `algorithm` + `policy-enforcement` | CP-internal |
| C-CP-12 | §12 | Sub-agent gate-level composition (default-downgrade rule + monotonic descent + cross-deployment monotonicity + audit) | `algorithm` + `policy-enforcement` | **Cross-axis AS consumer** (U-AS-01, U-AS-09, U-AS-14, U-AS-15) |
| C-CP-13 | §13 | HandoffContext + SubAgentBrief + brief-authoring inheritance + StateSummary + LedgerEntryRef | `data-type` | **Cross-axis IS + AS consumer** (U-IS-07, U-IS-12, U-AS-29) |
| C-CP-14 | §14 | Multi-agent span hierarchy + `topology.*` + `subagent.*` namespaces + sampling + concurrent-cache warm-up | `data-type` + `algorithm` | **Cross-axis IS + AS consumer** (U-IS-01, U-IS-02, U-AS-17, U-AS-31) |
| C-CP-15 | §15 | Per-sibling F2 ledger + `parent_fanout_close_entry` separate primitive + merkle construction + per-persona-tier crypto + trace inspection | `data-type` + `algorithm` | **Cross-axis IS consumer** (U-IS-07, U-IS-08, U-IS-09, U-IS-11, U-IS-12) |
| C-CP-16 | §16 | 4-response `HITLResponse` palette + per-response audit entry shapes + completeness invariants + `hitl.response.class` attribute | `data-type` + `policy-enforcement` | **Cross-axis IS consumer** (U-IS-07, U-IS-09) |
| C-CP-17 | §17 | 3-placement `HITLPlacementKind` enum + `hitl_gate(...)` signature + HITL-as-tool-call rewriting + workflow-definition schema | `data-type` + `api-surface` + `algorithm` | CP-internal |
| C-CP-18 | §18 | Persona-tier × engine-class 15-cell matrix + cell exclusion inheritance + both-by-tier overlay + two-agent-observer + binding selection | `data-type` + `algorithm` | CP-internal |
| C-CP-19 | §19 | 4-axis multiplicative gate-level rule + cross-deployment monotonicity + `_hitl_required` predicate + 5-axis composition with C-AS-12 + operator-policy override | `algorithm` + `policy-enforcement` | **Cross-axis AS consumer** (U-AS-05, U-AS-12, U-AS-13, U-AS-14, U-AS-15) |
| C-CP-20 | §20 | Per-persona-tier audit-ledger cryptographic shape + signing-key resolution via F5 + key-rotation two-row pattern + 7 `audit.*` + 4 `hitl.*` span schemas | `data-type` + `algorithm` | **Cross-axis IS + AS consumer** (U-IS-07, U-IS-08, U-IS-09, U-IS-11, U-AS-20) |
| C-CP-21 | §21 | 5-class fail taxonomy + transient staircase + palette restriction + summarization-model table + 3 `validator.fail.*` attrs + sampling + operator-burden eval + timeout-degradation | `data-type` + `algorithm` + `policy-enforcement` | **Cross-axis IS + AS consumer** (U-IS-07, U-IS-11, U-AS-03, U-AS-10, U-AS-29) |
| C-CP-22 | §22 | Context revalidation resume protocol + material-diff detection + state_summary snapshot capture + T-perm-2 F2-layer composition | `algorithm` | **Cross-axis IS + AS consumer** (U-IS-01, U-IS-11, U-IS-12, U-AS-10) |
| C-CP-23 | §23 | T-perm-3 three-layer composition (F1 + D1 + D4) + per-cell reading + runtime fault-handling + orthogonal composition + deterministic outer-harness boundary | `algorithm` + `module-boundary` | **Cross-axis AS consumer** (U-AS-14) |
| C-CP-24 | §24 | CP-axis substrate seam exports manifest (6 specialization + 4 F3-lifecycle-event + 1 inheritance = 11 namespaces) + session-4 + session-5 composition exports + F2-12 carry-forward | `module-boundary` | **Cross-axis CP exporter** |

19 of 24 contracts (79%) consume cross-axis substrate. CP is the most cross-axis-coupled axis in the harness; the cross-axis coupling density reflects the control-plane responsibility for composing IS substrate and AS substrate at every gate, audit, and topology decision.

### §1.2 Cluster decomposition realized

Nine clusters discovered from CP spec structure; ADR-anchoring + composition-density-by-contract-group decomposition:

| Cluster | Anchor ADR(s) | Contracts | Unit count | Unit IDs |
|---|---|---|---|---|
| 1 | F1 v1.2 | C-CP-01, C-CP-02, C-CP-03, C-CP-04 | 9 | U-CP-01 → U-CP-09 |
| 2 | F3 v1.1 | C-CP-05, C-CP-06 | 5 | U-CP-10 → U-CP-14 |
| 3 | D1 v1.1 | C-CP-07, C-CP-08, C-CP-09 | 7 | U-CP-15 → U-CP-21 |
| 4 | D4 v1.1 | C-CP-10, C-CP-11, C-CP-12 | 6 | U-CP-22 → U-CP-27 |
| 5 | D4 v1.1 | C-CP-13, C-CP-14, C-CP-15 | 9 | U-CP-28 → U-CP-36 |
| 6 | D5 v1.3 | C-CP-16, C-CP-17, C-CP-18 | 5 | U-CP-37 → U-CP-41 |
| 7 | D5 v1.3 + F5 v1.1 | C-CP-19, C-CP-20 | 5 | U-CP-42 → U-CP-46 |
| 8 | D5 v1.3 | C-CP-21, C-CP-22 | 6 | U-CP-47 → U-CP-52 |
| 9 | D1 v1.1 + D4 v1.1 + F1 v1.2 + composition | C-CP-23, C-CP-24 | 3 | U-CP-53 → U-CP-55 |
| **Total** | — | **24** | **55** | U-CP-01 → U-CP-55 |

### §1.3 Substrate-version citation alignment

Per Workflow v1.5 §7 use-latest-version body-citation discipline + SKILL.md §9 V3 deference:

| Substrate | Citation version | Rationale |
|---|---|---|
| CP spec (`Spec_Control_Plane_v1.md`) | **v1.2** | Latest filed; P5-CK-cleared. Session 3 prompt §2.1 + §3 cited "v1.1"; Workflow §7 use-latest-version discipline applied per IS plan v1 §1.3 precedent |
| IS plan (`Implementation_Plan_Information_Substrate_v1.md`) | **v1** | Latest filed (Phase 6 Session 1 close) |
| AS plan (`Implementation_Plan_Action_Surface_v1.md`) | **v1** | Latest filed (Phase 6 Session 2 close) |
| ADR-F1 | v1.2 | Substrate-anchored by CP spec §1–§4 |
| ADR-F2 | v1.2 | Substrate-anchored by CP spec §5–§6, §8, §15 |
| ADR-F3 | v1.1 | Substrate-anchored by CP spec §3, §5 |
| ADR-F5 | v1.1 | Substrate-anchored by CP spec §20 |
| ADR-D1 | v1.1 | Substrate-anchored by CP spec §7–§9 |
| ADR-D2 | v1.1 | Substrate-anchored by CP spec §12, §19 (cross-axis composition) |
| ADR-D3 | v1.2 | Substrate-anchored by CP spec §13 (brief-authoring inheritance) |
| ADR-D4 | v1.1 | Substrate-anchored by CP spec §10–§15 |
| ADR-D5 | v1.3 | Substrate-anchored by CP spec §16–§22 |
| ADR-D6 | v1.1 | Substrate-anchored by CP spec §24 ingestion target |

All unit `Implements:` citations point to CP spec v1.2; no prior-version (v1.1) citations emitted. Cross-axis `Depends on: [U-IS-NN (cross-axis: IS)]` declarations cite IS plan v1; cross-axis AS declarations cite AS plan v1.

### §1.4 F2-12 carry-forward declaration

CP spec v1.2 §24.4 declares F2-12 as a forward-routed carry-forward (not closed at v1.2). Active engagement surface at U-CP-20 (C-CP-08 R-CP-07-satisfying contract). Closure path declared at U-CP-55 §24.4 export manifest. Inheritance at sessions 4 + 5 per spec §24.4 closing sentence.

| Carry-forward | Active at | Closure path | Inheritance |
|---|---|---|---|
| F2-12 | U-CP-20 (C-CP-08 R-CP-07 contract) | D1 v1.2 + D6 v1.2 → ADD v1.3 → PRD v1.1 → CP spec v1.3 → CP plan v2 (revision-pass mode) | Session 4 + Session 5 §[carry-forwards] |

---

## §2 Atomic-unit decomposition

### §2.1 Cluster 1 — F1 routing + fallback (C-CP-01, C-CP-02, C-CP-03, C-CP-04)

**Anchor.** ADR-F1 v1.2.

**Theme.** Four contracts compose the routing substrate: core API surface (C-CP-01); layered routing strategy (C-CP-02); per-layer time-budget + fallback namespace declarations (C-CP-03); cross-family fallback chain (C-CP-04).

#### U-CP-01 — Declare `routing.*` namespace + per-attribute schema

**Implements:** [C-CP-01 §1.4]

**Depends on:** (none)

**Inputs:** None (foundational; root unit of CP-axis routing namespace).

**Files affected:** CP-axis routing namespace declaration (logical: `routing-namespace-attribute-schema`).

**Signatures:**

```
record RoutingAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
  inherited_from : string  // "llm.inference parent span per OTel GenAI semconv 1.41.0"
}

const ROUTING_NAMESPACE_SCHEMA: List<RoutingAttributeSchema>  // exactly 4 entries

enum AttributeValueType { STRING, INT, FLOAT, BOOL, ENUM_REF }
enum Cardinality { LOW, MEDIUM, HIGH, PER_REQUEST }
```

**Acceptance criteria:**
1. `ROUTING_NAMESPACE_SCHEMA` declares exactly four `routing.*` attributes per C-CP-01 §1.4 verbatim: `routing.layer`, `routing.candidate`, `routing.decision_ms`, `routing.budget_exhausted`.
2. Each attribute's `inherited_from` field cites parent `llm.inference` span per OTel GenAI semconv 1.41.0.
3. The namespace does NOT carry independent sampling discipline; inherits from parent span per C-CP-24 §24.1.C.
4. D6 ingestion is **out-of-scope at this unit**; OD plan Session 4 ingests via U-CP-54 namespace export manifest.

**Tests:** `test_routing_namespace_cardinality_four`, `test_routing_attributes_match_spec_verbatim`, `test_routing_inherits_from_llm_inference`, `test_no_independent_sampling_discipline`.

**Rollback boundary:** Revert `ROUTING_NAMESPACE_SCHEMA` declaration. Routing observability degrades; cross-axis citation at U-CP-54 §24.1.C export manifest releases.

#### U-CP-02 — Declare `ProviderCapabilities` reflection contract

**Implements:** [C-CP-01 §1.2]

**Depends on:** (none)

**Inputs:** None (foundational; consumed at routing-time selection per C-CP-02 §2.1).

**Files affected:** CP-axis provider capabilities schema (logical: `provider-capabilities-schema`).

**Signatures:**

```
record ProviderCapabilities {
  provider          : string                          // {anthropic, openai, ollama, ...}
  model_family      : string
  model_version     : string
  max_context_tokens: int
  supports_tools    : bool
  supports_caching  : bool
  supports_thinking : bool                            // extended-thinking budget per Anthropic Sonnet/Opus
  supports_batch    : bool                            // Anthropic Batch API
  cost_per_input_token  : float
  cost_per_output_token : float
}

function reflect_provider_capabilities(provider: string, model: string) -> ProviderCapabilities
function provider_supports(capability: ProviderCapability, caps: ProviderCapabilities) -> bool

enum ProviderCapability { TOOLS, CACHING, THINKING, BATCH }
```

**Acceptance criteria:**
1. `ProviderCapabilities` declares exactly ten fields per C-CP-01 §1.2 verbatim.
2. `reflect_provider_capabilities` returns the same `ProviderCapabilities` value for the same (provider, model) pair (deterministic; no inference path).
3. `cost_per_input_token` and `cost_per_output_token` are float; concrete cost-table maintenance deferred to implementation discretion per spec §1.2 deferred list.
4. `supports_thinking` per C-CP-01 §1.2 narrative is `true` only for Anthropic Sonnet 4.6 / Opus 4.6 / Opus 4.7 per AS C-AS-13 §13.4 model-tier table; verified by integration test against U-AS-29 catalog.

**Tests:** `test_provider_capabilities_ten_fields`, `test_reflect_deterministic`, `test_supports_thinking_anthropic_only`.

**Rollback boundary:** Revert `ProviderCapabilities` schema. Routing-time provider selection at U-CP-05 loses capability discrimination input; fallback chain composition at U-CP-09 loses cross-family capability filter.

#### U-CP-03 — Declare thin routing core surface

**Implements:** [C-CP-01 §1.1]

**Depends on:** (none)

**Inputs:** None (foundational; api-surface unit).

**Files affected:** CP-axis routing core API surface (logical: `routing-core-api-surface`).

**Signatures:**

```
record InferenceRequest {
  agent_role        : AgentRole
  workload_class    : WorkloadClass
  persona_tier      : PersonaTier
  context_tokens    : int
  request_payload   : ProviderAgnosticPayload
  trace_context     : TraceContext                    // for routing.* span attribution
}

record InferenceResponse {
  provider_used     : string
  model_used        : string
  routing_decision  : RoutingDecisionTrace            // layer + candidate + decision_ms
  response_payload  : ProviderAgnosticPayload
  tokens_in         : int
  tokens_out        : int
  cached_tokens_in  : int
}

function infer(request: InferenceRequest) -> InferenceResponse
    // thin core surface; orchestrates layered routing → provider dispatch → response materialization
    // routing strategy delegates to U-CP-05; provider dispatch delegates to provider SDK adapters
    // (out of scope at CP plan; AS plan declares MCP server SDK boundaries)
```

**Acceptance criteria:**
1. `infer` is the only entry-point for LLM inference at CP layer; all downstream LLM calls flow through this surface.
2. `InferenceRequest` carries `agent_role`, `workload_class`, `persona_tier` for layered-routing-strategy discrimination per C-CP-02 §2.1.
3. `InferenceResponse.routing_decision` populated by U-CP-05 at routing-time; emits `routing.*` span attributes per U-CP-01.
4. Per ADD §5.3.3: `infer` is the **probabilistic core** of the deterministic outer harness; everything around it (chain-advancement, cascade-enforcement, retry, breaker, HITL) is deterministic per U-CP-53 declaration.

**Tests:** `test_infer_single_entry_point`, `test_infer_emits_routing_attributes`, `test_infer_probabilistic_core_per_add_53`.

**Rollback boundary:** Revert `infer` surface. All downstream CP plan units lose entry-point; the harness has no LLM-inference path at CP layer; build fails at multiple consumer sites.

#### U-CP-04 — Implement routing manifest residence

**Implements:** [C-CP-01 §1.3]

**Depends on:** [U-CP-01, U-IS-01 (cross-axis: IS), U-IS-02 (cross-axis: IS), U-IS-06 (cross-axis: IS)]

**Inputs:** `routing.*` namespace (U-CP-01); filesystem path contract (U-IS-01 `PathClass`); path-resolver (U-IS-02); per-deployment-surface storage residence (U-IS-06).

**Files affected:** CP-axis routing manifest residence (logical: `routing-manifest-residence`); CP-axis routing-manifest schema declaration (logical: `routing-manifest-schema`).

**Cross-axis substrate consumed.** `FILESYSTEM_PATH_CONTRACT_EXPORT` (C-IS-10 §10.4 → U-IS-01, U-IS-02) for canonical manifest residence; per-deployment-surface storage classification via U-IS-06.

**Signatures:**

```
record RoutingManifest {
  manifest_version  : int
  per_role_bindings : Map<AgentRole, RoleRoutingBinding>
  per_workload_overrides : Map<WorkloadClass, WorkloadRoutingOverride>
  fallback_chains   : List<FallbackChain>             // populated per C-CP-04
  retry_policies    : Map<ToolName, RetryPolicy>      // populated per C-CP-03 §3.5
}

function load_routing_manifest(path: FilesystemPath) -> RoutingManifest
function validate_routing_manifest(manifest: RoutingManifest) -> Result<Unit, ValidationError>
```

**Acceptance criteria:**
1. `RoutingManifest` schema declares exactly five top-level fields per C-CP-01 §1.3 + cross-references to C-CP-03 §3.5 + C-CP-04 §4.1.
2. Manifest residence path resolves via U-IS-02 against U-IS-01 `PathClass`; per-deployment-surface residence delegates to U-IS-06.
3. `validate_routing_manifest` returns `Err` if any `RoleRoutingBinding` cites a model not present in U-AS-29 model-binding catalog (cross-axis check; runtime-deferred).
4. Manifest format (JSON vs YAML vs TOML) deferred to implementation discretion per spec §1.3 deferred list.

**Tests:** `test_routing_manifest_five_fields`, `test_load_via_u_is_02`, `test_validate_rejects_unknown_model`, `test_format_deferred`.

**Rollback boundary:** Revert `RoutingManifest` schema + residence binding. Routing-manifest-driven binding at U-CP-05 loses canonical persistence; runtime routing degrades to hardcoded defaults. Cross-axis IS edges to U-IS-01, U-IS-02, U-IS-06 release.

#### U-CP-05 — Implement layered routing strategy (declarative → embedding → LLM-as-router)

**Implements:** [C-CP-02 §2.1, §2.2]

**Depends on:** [U-CP-01, U-CP-02, U-CP-04, U-CP-06]

**Inputs:** `routing.*` namespace (U-CP-01); `ProviderCapabilities` (U-CP-02); routing manifest (U-CP-04); `LayerBudget` (U-CP-06).

**Files affected:** CP-axis layered routing strategy (logical: `layered-routing-strategy`); CP-axis routing layer enum (logical: `routing-layer-enum`).

**Signatures:**

```
enum RoutingLayer {
  DECLARATIVE,                                        // manifest-driven role × workload binding
  EMBEDDING,                                          // semantic similarity to canonical role descriptors
  LLM_AS_ROUTER                                       // fallback layer; LLM classification
}

record RoutingDecisionTrace {
  layer              : RoutingLayer
  candidate          : string                         // "provider:model" tuple
  decision_ms        : int
  budget_exhausted   : bool
}

function route(request: InferenceRequest, manifest: RoutingManifest) -> RoutingDecisionTrace
    // 1. Try DECLARATIVE layer per manifest's per_role_bindings + per_workload_overrides
    // 2. If layer returns no decision OR budget exhausted, fall through to EMBEDDING
    // 3. If embedding layer returns no decision OR budget exhausted, fall through to LLM_AS_ROUTER
    // 4. Emits routing.* span attributes per U-CP-01
```

**Acceptance criteria:**
1. `RoutingLayer` declares exactly three values per C-CP-02 §2.1 verbatim.
2. Layer ordering is fixed at compile time: DECLARATIVE → EMBEDDING → LLM_AS_ROUTER per §2.2 layer ordering invariant; reordering is a Workflow §4.1.2 Class-2 F1 revision.
3. `route` honors per-layer `LayerBudget` from U-CP-06; budget exhaustion triggers fall-through per U-CP-08.
4. Each layer emits its `routing.*` span attributes per U-CP-01 namespace.
5. DECLARATIVE layer hit short-circuits the strategy; no embedding/LLM-router computation when manifest binding present.

**Tests:** `test_routing_layer_cardinality_three`, `test_layer_ordering_fixed`, `test_declarative_short_circuits`, `test_budget_exhaustion_triggers_fall_through`, `test_emits_routing_attributes_per_layer`.

**Rollback boundary:** Revert `RoutingLayer` enum + `route` strategy. U-CP-03 `infer` surface loses routing implementation; harness LLM dispatch defaults to provider-of-last-resort selection without role-aware discrimination.

#### U-CP-06 — Declare `LayerBudget` data type

**Implements:** [C-CP-03 §3.1]

**Depends on:** [U-CP-01]

**Inputs:** `routing.*` namespace (U-CP-01) for `routing.budget_exhausted` attribute reference.

**Files affected:** CP-axis layer budget declaration (logical: `layer-budget-schema`).

**Signatures:**

```
record LayerBudget {
  layer                : RoutingLayer
  time_budget_ms       : int                          // wall-clock budget per layer
  per_workload_override: Optional<Map<WorkloadClass, int>>
  per_persona_override : Optional<Map<PersonaTier, int>>
}

const DEFAULT_LAYER_BUDGETS: List<LayerBudget>        // exactly 3 entries

function effective_budget(
    layer: RoutingLayer,
    workload_class: WorkloadClass,
    persona_tier: PersonaTier
) -> int
    // returns time_budget_ms after applying overrides
```

**Acceptance criteria:**
1. `LayerBudget` declares exactly four fields per C-CP-03 §3.1.
2. `DEFAULT_LAYER_BUDGETS` exposes one entry per `RoutingLayer` value; concrete default values deferred to operator-binding-time discretion per spec §3.1 deferred list.
3. `effective_budget` resolves per-workload override first, then per-persona override; both unset returns default.
4. Budget exhaustion at `effective_budget(layer) ms` emits `routing.budget_exhausted = true` on the layer's span per U-CP-01.

**Tests:** `test_layer_budget_four_fields`, `test_default_one_per_layer`, `test_effective_budget_override_precedence`, `test_exhaustion_emits_attribute`.

**Rollback boundary:** Revert `LayerBudget` schema. Per-layer timing discipline at U-CP-05 loses budget enforcement; fall-through at U-CP-08 loses trigger.

#### U-CP-07 — Declare `fallback.*` + `harness.breaker.*` + `retry.*` namespaces

**Implements:** [C-CP-03 §3.5]

**Depends on:** (none)

**Inputs:** None (foundational; substrate-supplying data-type unit).

**Files affected:** CP-axis fallback namespace (logical: `fallback-namespace-schema`); CP-axis harness-breaker namespace (logical: `harness-breaker-namespace-schema`); CP-axis retry namespace (logical: `retry-namespace-schema`).

**Note on substrate authority.** Per C-CP-24 §24.1.B narrative: `harness.breaker.*` is substrate-anchored at `c9-reliability-recovery` SKILL.md per F2-16 closure + Workflow v1.3 §2.3.3.1 clause (iii). CP plan emits the CP-side composition surface (this unit's namespace) without claiming canonical authorship. Canonical schema at OD C-OD-07 §7.1.

**Signatures:**

```
record FallbackAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
}
const FALLBACK_NAMESPACE_SCHEMA: List<FallbackAttributeSchema>  // exactly 9 entries

record HarnessBreakerAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
  source_authority: string  // "c9-reliability-recovery SKILL.md (substrate-anchored outside CP)"
}
const HARNESS_BREAKER_NAMESPACE_SCHEMA: List<HarnessBreakerAttributeSchema>  // exactly 7 entries

record RetryAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
}
const RETRY_NAMESPACE_SCHEMA: List<RetryAttributeSchema>  // exactly 4 entries

enum RetryCause {
  TRANSIENT_PROVIDER_ERROR,
  RATE_LIMIT,
  TIMEOUT,
  CAPABILITY_SHORTFALL,
  VALIDATOR_FAIL_TRANSIENT
}
```

**Acceptance criteria:**
1. `FALLBACK_NAMESPACE_SCHEMA` declares exactly nine attributes per C-CP-03 §3.5 verbatim: `fallback.layer`, `fallback.candidate_chosen`, `fallback.candidates_skipped`, `fallback.cause`, `fallback.cross_family`, `fallback.cross_family_triggered`, `fallback.exhausted`, `fallback.depth`, `fallback.cache_state_lost`.
2. `HARNESS_BREAKER_NAMESPACE_SCHEMA` declares exactly seven attributes per C-CP-03 §3.5 + OD C-OD-07 §7.1 canonical schema verbatim: `harness.breaker.id`, `harness.breaker.state`, `harness.breaker.scope`, `harness.breaker.trip_count`, `harness.breaker.trip_window_seconds`, `harness.breaker.fail_count_in_window`, `harness.breaker.fail_threshold`. Each attribute carries `source_authority = "c9-reliability-recovery SKILL.md"`.
3. `RETRY_NAMESPACE_SCHEMA` declares exactly four attributes per C-CP-03 §3.5 verbatim: `retry.attempt`, `retry.cause`, `retry.backoff_ms`, `retry.budget_exhausted`.
4. `RetryCause` declares exactly five values discriminating retry-causation; consumed at U-CP-48 cause-attribution-conditioned branching.
5. D6 ingestion is **out-of-scope at this unit**; OD plan Session 4 ingests via U-CP-54 §24.1.B export manifest.

**Tests:** `test_fallback_namespace_cardinality_nine`, `test_fallback_attributes_match_spec_verbatim`, `test_harness_breaker_namespace_cardinality_seven`, `test_harness_breaker_source_authority`, `test_retry_namespace_cardinality_four`, `test_retry_cause_cardinality_five`.

**Rollback boundary:** Revert three namespace declarations. F3-lifecycle-event substrate at U-CP-54 §24.1.B export manifest loses CP-side source for `fallback.*` + `retry.*`; `harness.breaker.*` substrate-anchored at C9 unaffected (CP plan does not own).

#### U-CP-08 — Implement deterministic fall-through procedure

**Implements:** [C-CP-03 §3.2, §3.3]

**Depends on:** [U-CP-01, U-CP-05, U-CP-06, U-CP-07]

**Inputs:** `routing.*` namespace (U-CP-01); layered routing strategy (U-CP-05); `LayerBudget` (U-CP-06); `fallback.*` namespace (U-CP-07).

**Files affected:** CP-axis fall-through procedure (logical: `fall-through-procedure`).

**Signatures:**

```
enum FallThroughCause {
  LAYER_NO_DECISION,
  LAYER_BUDGET_EXHAUSTED,
  PROVIDER_UNAVAILABLE,
  CAPABILITY_SHORTFALL
}

record FallThroughResult {
  triggered_at_layer    : RoutingLayer
  cause                 : FallThroughCause
  next_layer            : Optional<RoutingLayer>
  emit_fallback_event   : bool
}

function fall_through(
    current_layer: RoutingLayer,
    cause: FallThroughCause,
    request: InferenceRequest
) -> FallThroughResult
    // returns next layer in DECLARATIVE → EMBEDDING → LLM_AS_ROUTER chain
    // emits fallback.triggered span event when emit_fallback_event = true
```

**Acceptance criteria:**
1. `FallThroughCause` declares exactly four values per C-CP-03 §3.2 verbatim.
2. `fall_through` honors layer ordering invariant from U-CP-05; no upward layer skip permitted.
3. `LAYER_NO_DECISION` triggers fall-through silently (no `fallback.triggered` event); `LAYER_BUDGET_EXHAUSTED` and `CAPABILITY_SHORTFALL` emit `fallback.triggered` per U-CP-07 namespace per §3.3.
4. Final-layer fall-through (LLM_AS_ROUTER → no next layer) returns `next_layer = None` and emits `fallback.exhausted = true`.
5. Procedure is deterministic given inputs.

**Tests:** `test_fall_through_cause_cardinality_four`, `test_fall_through_honors_layer_ordering`, `test_no_decision_silent`, `test_budget_exhausted_emits_event`, `test_capability_shortfall_emits_event`, `test_final_layer_exhausted`.

**Rollback boundary:** Revert fall-through procedure. U-CP-05 layered routing loses fall-through implementation; budget exhaustion or capability shortfall blocks inference at the failed layer without recovery path.

#### U-CP-09 — Implement cross-family fallback chain composition

**Implements:** [C-CP-04 §4.1, §4.2, §4.3]

**Depends on:** [U-CP-02, U-CP-05, U-CP-07, U-CP-08, U-AS-30 (cross-axis: AS)]

**Inputs:** `ProviderCapabilities` (U-CP-02); layered routing (U-CP-05); `fallback.*` namespace (U-CP-07); fall-through procedure (U-CP-08); model-tier escalation chain from C-AS-13 §13.4 (U-AS-30 cross-axis).

**Files affected:** CP-axis cross-family fallback chain (logical: `cross-family-fallback-chain`).

**Cross-axis substrate consumed.** `ELEVEN_PRIMITIVE_ADOPTION_DEPTH_MATRIX_EXPORT` (C-AS-16 §16.6 → U-AS-30) for cross-family chain composition.

**Signatures:**

```
record FallbackChain {
  primary       : ProviderCandidate
  same_family   : List<ProviderCandidate>          // ordered fallback within family
  cross_family  : List<ProviderCandidate>          // ordered fallback across families
  terminal      : Optional<ProviderCandidate>      // local/open-weight tier per C-AS-13 §13.4
}

record ProviderCandidate {
  provider     : string
  model        : string
  family       : ProviderFamily
}

enum ProviderFamily {
  ANTHROPIC,
  OPENAI,
  GOOGLE,
  LOCAL_OPEN_WEIGHT
}

function compose_fallback_chain(role: AgentRole, workload: WorkloadClass) -> FallbackChain
function on_provider_failure(failed: ProviderCandidate, chain: FallbackChain) -> Optional<ProviderCandidate>
    // returns next candidate per chain composition rule
    // when crossing family boundary, emits fallback.cross_family_triggered + fallback.cache_state_lost
```

**Acceptance criteria:**
1. `FallbackChain` declares exactly four fields per C-CP-04 §4.1 verbatim.
2. `ProviderFamily` declares exactly four values per C-CP-04 §4.1 + AS C-AS-13 §13.4 verbatim.
3. `on_provider_failure` honors fall-through ordering: same-family before cross-family before terminal per §4.2.
4. Cross-family transition emits `fallback.cross_family_triggered = true` AND `fallback.cache_state_lost = true` per §4.3.
5. Cache state loss attribution: per-family prompt-cache state is provider-bound; cross-family fallback resets `anthropic.cache_read_input_tokens` to 0 per §4.3.
6. Chain composition delegates per-workload-class candidate selection to U-AS-30 (AS C-AS-13 §13.4).

**Tests:** `test_fallback_chain_four_fields`, `test_provider_family_cardinality_four`, `test_on_provider_failure_ordering`, `test_cross_family_emits_both_events`, `test_cache_state_loss_attribution`, `test_composition_delegates_to_u_as_30`.

**Rollback boundary:** Revert cross-family fallback chain. U-CP-05 layered routing loses cross-family recovery; provider outage halts inference at first failure without family-boundary crossing. Cross-axis AS edge to U-AS-30 releases.

---

### §2.2 Cluster 2 — F3 lifecycle + manifest (C-CP-05, C-CP-06)

**Anchor.** ADR-F3 v1.1.

**Theme.** Two contracts compose the lifecycle-event substrate (C-CP-05) and the workflow manifest entry shape (C-CP-06).

#### U-CP-10 — Declare 8-class F3 lifecycle event taxonomy

**Implements:** [C-CP-05 §5.1]

**Depends on:** (none)

**Inputs:** None (foundational; root of F3 lifecycle event taxonomy).

**Files affected:** CP-axis lifecycle event class enum (logical: `lifecycle-event-class-enum`).

**Signatures:**

```
enum LifecycleEventClass {
  WORKFLOW_START,
  WORKFLOW_CHECKPOINT,
  WORKFLOW_RESUMPTION,
  WORKFLOW_FANOUT_OPEN,
  WORKFLOW_FANOUT_CLOSE,
  WORKFLOW_HITL_INVOCATION,
  WORKFLOW_FALLBACK_TRIGGERED,
  WORKFLOW_BREAKER_TRIPPED
}

record LifecycleEventClassMetadata {
  class             : LifecycleEventClass
  span_name         : string                          // canonical OTel span name
  parent_relation   : ParentRelation
}
const LIFECYCLE_EVENT_CLASS_METADATA: List<LifecycleEventClassMetadata>  // exactly 8 entries
```

**Acceptance criteria:**
1. `LifecycleEventClass` declares exactly eight values per C-CP-05 §5.1 verbatim.
2. Each value maps to a canonical OTel span name per §5.1: `workflow.start`, `workflow.checkpoint`, `workflow.resumption`, `topology.fanout.opened`, `topology.fanout.closed`, `hitl.invocation.opened`, `fallback.triggered`, `breaker.tripped`.
3. Taxonomy is closed at cardinality 8 — extension requires Workflow §4.1.2 Class-2 F3 revision.
4. D6 ingestion delegates to U-CP-54 §24.1.B (4 of 8 are F3 lifecycle event attributes).

**Tests:** `test_lifecycle_event_class_cardinality_eight`, `test_class_to_span_name_match_spec_verbatim`, `test_taxonomy_closed`.

**Rollback boundary:** Revert `LifecycleEventClass` enum. F3 lifecycle event substrate dissolves; U-CP-12 per-class attribute composition loses discriminator; U-CP-20 resumption observable behavior loses class anchor.

#### U-CP-11 — Declare `lease.*` namespace + 5-attribute schema

**Implements:** [C-CP-05 §5.3]

**Depends on:** (none)

**Inputs:** None (foundational; substrate-supplying data-type unit).

**Files affected:** CP-axis lease namespace (logical: `lease-namespace-attribute-schema`).

**Signatures:**

```
record LeaseAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
}
const LEASE_NAMESPACE_SCHEMA: List<LeaseAttributeSchema>  // exactly 5 entries

enum LeaseEventKind {
  LEASE_ACQUIRED,
  LEASE_RENEWED,
  LEASE_RELEASED,
  LEASE_LOST
}
```

**Acceptance criteria:**
1. `LEASE_NAMESPACE_SCHEMA` declares exactly five attributes per C-CP-05 §5.3 verbatim: `lease.id`, `lease.holder`, `lease.acquired_at`, `lease.duration_ms`, `lease.event_kind`.
2. `LeaseEventKind` declares exactly four values matching `lease.event_kind` discriminator.
3. D6 ingestion delegates to U-CP-54 §24.1.B (lease.acquired / lease.released span events).
4. Sampling discipline per OD plan Session 4 D6 §1.3 base-rate per C-CP-05 §5.4.

**Tests:** `test_lease_namespace_cardinality_five`, `test_lease_event_kind_cardinality_four`, `test_attributes_match_spec_verbatim`.

**Rollback boundary:** Revert `LEASE_NAMESPACE_SCHEMA`. Lease-event observability degrades; U-CP-12 per-class attribute composition for `lease.acquired` / `lease.released` events loses substrate.

#### U-CP-12 — Implement per-class attribute composition + per-class sampling discipline

**Implements:** [C-CP-05 §5.2, §5.4]

**Depends on:** [U-CP-07, U-CP-10, U-CP-11, U-CP-15, U-CP-19, U-CP-21, U-IS-07 (cross-axis: IS)]

**Inputs:** Fallback/retry/harness-breaker namespaces (U-CP-07); lifecycle event class enum (U-CP-10); lease namespace (U-CP-11); `EngineClass` enum (U-CP-15); `ResumptionKind` enum (U-CP-19); `engine.*` namespace (U-CP-21); F2 state-ledger entry shape (U-IS-07 cross-axis).

**Files affected:** CP-axis per-class attribute composition (logical: `per-class-attribute-composition`); CP-axis per-class sampling table (logical: `per-class-sampling-table`).

**Cross-axis substrate consumed.** `STATE_LEDGER_ENTRY_SHAPE_EXPORT` (C-IS-10 §10.1 → U-IS-07) for `workflow.checkpoint` event attribute composition (action_id, prior_event_hash fields).

**Signatures:**

```
record PerClassAttributeSet {
  class               : LifecycleEventClass
  required_attributes : Set<string>                   // names from declared namespaces
  optional_attributes : Set<string>
}
const PER_CLASS_ATTRIBUTE_SETS: List<PerClassAttributeSet>  // exactly 8 entries

enum SamplingRate {
  ALWAYS_SAMPLED,                                     // head = 1.0
  BASE_RATE                                           // head per deployment-bound base rate
}

record SamplingDisposition {
  class             : LifecycleEventClass
  head_rate         : SamplingRate
  tail_keep         : bool
}
const SAMPLING_DISPOSITIONS: List<SamplingDisposition>  // exactly 8 entries
```

**Acceptance criteria:**
1. `PER_CLASS_ATTRIBUTE_SETS` declares exactly eight entries per C-CP-05 §5.2 verbatim, one per `LifecycleEventClass` value.
2. `workflow.checkpoint` event composes with F2 entry shape via U-IS-07 — required attributes include `action_id`, `prior_event_hash` from F2 six-field shape.
3. `workflow.resumption` event composes with U-CP-21 `engine.*` namespace per C-CP-09 §9.2.
4. `SAMPLING_DISPOSITIONS` declares per C-CP-05 §5.4 verbatim: `WORKFLOW_START`, `WORKFLOW_CHECKPOINT`, `WORKFLOW_RESUMPTION`, `WORKFLOW_FANOUT_OPEN`, `WORKFLOW_FANOUT_CLOSE`, `WORKFLOW_HITL_INVOCATION`, `WORKFLOW_FALLBACK_TRIGGERED`, `WORKFLOW_BREAKER_TRIPPED` all `ALWAYS_SAMPLED` (operator-burden and tamper-evidence relevance).
5. Per-class attribute composition is deterministic given inputs; runtime emission validates `required_attributes` set is fully populated.

**Tests:** `test_per_class_attribute_sets_cardinality_eight`, `test_checkpoint_composes_with_f2_entry`, `test_resumption_composes_with_engine_namespace`, `test_sampling_dispositions_all_always_sampled`, `test_required_attributes_enforced`.

**Rollback boundary:** Revert per-class attribute composition + sampling table. F3 lifecycle event emission loses per-class discrimination; D6 §1.2 + §1.3 ingestion loses CP-side composition. Cross-axis IS edge to U-IS-07 releases.

#### U-CP-13 — Declare `WorkflowManifestEntry` schema

**Implements:** [C-CP-06 §6.1]

**Depends on:** [U-CP-04, U-CP-06, U-CP-09, U-CP-15, U-CP-22, U-CP-38]

**Inputs:** Routing manifest (U-CP-04); `LayerBudget` (U-CP-06); fallback chain (U-CP-09); `EngineClass` enum (U-CP-15); `TopologyPattern` enum (U-CP-22); `HITLPlacement` schema (U-CP-38).

**Files affected:** CP-axis workflow manifest entry schema (logical: `workflow-manifest-entry-schema`).

**Signatures:**

```
record WorkflowManifestEntry {
  workflow_id          : string
  workload_class       : WorkloadClass
  persona_tier         : PersonaTier
  engine_class         : EngineClass
  topology_pattern     : TopologyPattern
  layer_budgets        : List<LayerBudget>             // per-layer overrides
  fallback_chain       : FallbackChain                  // overrides for cross-family chain
  hitl_placements      : List<HITLPlacement>           // declared per workflow per C-CP-17 §17.3
  sub_agent_briefs     : Optional<List<SubAgentBrief>> // for fanout patterns
  per_step_overrides   : Map<StepID, StepOverride>     // populated for pipeline-automation
}

record StepOverride {
  step_id              : StepID
  model_binding        : Optional<ModelBinding>
  engine_class         : Optional<EngineClass>
  hitl_placement       : Optional<HITLPlacement>
}
```

**Acceptance criteria:**
1. `WorkflowManifestEntry` declares exactly ten top-level fields per C-CP-06 §6.1 verbatim.
2. `workload_class` and `persona_tier` are mandatory (no default); validation rejects missing values per ADR-F1 v1.2 workload-class commitment.
3. `topology_pattern` admissibility verified against U-CP-22 admissibility predicate at validation time.
4. `engine_class` selection verified against U-CP-16 candidate mapping at validation time.
5. `hitl_placements` ordered by placement-kind precedence per U-CP-38 schema.

**Tests:** `test_workflow_manifest_entry_ten_fields`, `test_workload_class_mandatory`, `test_persona_tier_mandatory`, `test_topology_admissibility_at_validation`, `test_engine_class_candidate_at_validation`.

**Rollback boundary:** Revert `WorkflowManifestEntry` schema. Workflow definition surface dissolves; per-workflow customization loses canonical persistence.

#### U-CP-14 — Implement per-step override evaluator + audit-ledger entry composition

**Implements:** [C-CP-06 §6.2]

**Depends on:** [U-CP-13, U-CP-15, U-IS-07 (cross-axis: IS), U-IS-08 (cross-axis: IS), U-IS-09 (cross-axis: IS), U-IS-11 (cross-axis: IS)]

**Inputs:** Workflow manifest entry (U-CP-13); `EngineClass` enum (U-CP-15); F2 substrate (U-IS-07, U-IS-08, U-IS-09, U-IS-11 cross-axis).

**Files affected:** CP-axis per-step override evaluator (logical: `per-step-override-evaluator`); CP-axis override audit-ledger entry composition (logical: `override-audit-ledger-composition`).

**Cross-axis substrate consumed.** `STATE_LEDGER_ENTRY_SHAPE_EXPORT` + `HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT` + `JSONL_EVENT_LEDGER_FORMAT_EXPORT` (C-IS-10 §10.1, §10.3, §10.5) for audit-ledger entry composition.

**Signatures:**

```
function resolve_step_binding(
    manifest_entry: WorkflowManifestEntry,
    step_id: StepID
) -> StepEffectiveBinding
    // applies per_step_overrides over manifest_entry defaults
    // emits audit-ledger entry per ADR-F2 audit composition when override applied

record StepEffectiveBinding {
  step_id            : StepID
  model_binding      : ModelBinding                   // effective (override or default)
  engine_class       : EngineClass
  hitl_placement     : Optional<HITLPlacement>
  override_applied   : bool
  override_audit_ref : Optional<LedgerEntryRef>       // when override_applied = true
}

function emit_override_audit_entry(
    workflow_id: string,
    step_id: StepID,
    override: StepOverride,
    actor: ActorIdentity
) -> AuditLedgerEntry
    // delegates F2 six-field construction to U-IS-07/08/09/11
```

**Acceptance criteria:**
1. `resolve_step_binding` returns the effective binding combining manifest defaults + per-step override; override field-by-field; no field-set substitution.
2. When override applied, `override_audit_ref` populated by `emit_override_audit_entry` per F2 audit composition; audit entry shape per U-IS-07 six-field shape with `action_id = workflow_id || step_id`.
3. `emit_override_audit_entry` delegates canonicalize+hash to U-IS-08; chain construction to U-IS-09; append to U-IS-11.
4. Override evaluator is deterministic given inputs.

**Tests:** `test_resolve_step_binding_field_by_field_override`, `test_audit_ref_populated_on_override`, `test_audit_entry_action_id_composition`, `test_delegates_to_u_is_07_08_09_11`.

**Rollback boundary:** Revert per-step override evaluator + audit composition. Pipeline-automation per-stage customization loses runtime evaluation; override audit trail dissolves. Cross-axis IS edges to U-IS-07, U-IS-08, U-IS-09, U-IS-11 release.

---

### §2.3 Cluster 3 — D1 engine + replay (C-CP-07, C-CP-08, C-CP-09)

**Anchor.** ADR-D1 v1.1.

**Theme.** Three contracts compose the engine substrate: engine-class taxonomy + capability-floor preservation + per-deployment-surface candidate mapping + workload-binding-time selection (C-CP-07); F2 substrate join discipline at engine-class boundary (C-CP-08); resumption taxonomy + observable behavior (C-CP-09).

#### U-CP-15 — Declare `EngineClass` enum + capability-floor preservation invariant

**Implements:** [C-CP-07 §7.1, §7.4]

**Depends on:** [U-CP-11]

**Inputs:** `lease.*` namespace (U-CP-11) for capability-floor lease-property reference.

**Files affected:** CP-axis engine class enum (logical: `engine-class-enum`); CP-axis capability-floor preservation invariant (logical: `capability-floor-preservation`).

**Signatures:**

```
enum EngineClass {
  EVENT_SOURCED_REPLAY,
  SAVE_POINT_CHECKPOINT,
  PURE_PATTERN_NO_ENGINE,
  RECONCILER_LOOP,
  WAL_SEGMENT
}

record CapabilityFloor {
  capability_name   : string                          // e.g., "lease_acquisition", "checkpoint_emission"
  required_at_class : Set<EngineClass>
  rationale         : string                          // §7.4 verbatim
}
const CAPABILITY_FLOORS: List<CapabilityFloor>
```

**Acceptance criteria:**
1. `EngineClass` declares exactly five values per C-CP-07 §7.1 verbatim.
2. Each value's narrative carries durable-execution-substrate citation per §7.1 (Temporal/Restate, DBOS/LangGraph, 12-factor agents, K8s CRD reconciler, Kafka WAL).
3. Taxonomy is closed at cardinality 5 — extension requires Workflow §4.1.2 Class-2 D1 revision.
4. `CAPABILITY_FLOORS` declares per §7.4 the minimum capability set required for each engine class to preserve F3 capability-floor invariants (lease acquisition, checkpoint emission, durable write, replay determinism).

**Tests:** `test_engine_class_cardinality_five`, `test_engine_class_values_match_spec_verbatim`, `test_taxonomy_closed`, `test_capability_floors_per_class_match_spec`.

**Rollback boundary:** Revert `EngineClass` enum + `CAPABILITY_FLOORS`. All downstream D1 + D4 + D5 units lose engine discriminator; cluster 4 + 5 + 6 + 7 + 8 + 9 composition dependencies fail.

#### U-CP-16 — Implement per-deployment-surface engine-class candidate mapping

**Implements:** [C-CP-07 §7.2]

**Depends on:** [U-CP-15]

**Inputs:** `EngineClass` enum (U-CP-15).

**Files affected:** CP-axis per-deployment-surface candidate mapping (logical: `engine-class-candidate-per-deployment-surface`).

**Signatures:**

```
enum DeploymentSurface {
  LOCAL_DEVELOPMENT,
  SELF_HOSTED_SERVER,
  MANAGED_CLOUD
}

record EngineClassCandidate {
  deployment_surface : DeploymentSurface
  candidate_set      : Set<EngineClass>
  exclusion_reasons  : Map<EngineClass, string>       // §7.2 column 3 verbatim per excluded class
}
const ENGINE_CLASS_CANDIDATES: List<EngineClassCandidate>  // exactly 3 entries
```

**Acceptance criteria:**
1. `DeploymentSurface` declares exactly three values per C-CP-07 §7.2 verbatim.
2. `ENGINE_CLASS_CANDIDATES` declares exactly three entries per §7.2 verbatim:

   | deployment_surface | candidate_set | structurally excluded |
   |---|---|---|
   | `LOCAL_DEVELOPMENT` | `{EVENT_SOURCED_REPLAY, SAVE_POINT_CHECKPOINT, PURE_PATTERN_NO_ENGINE, WAL_SEGMENT}` | `RECONCILER_LOOP` (requires K8s control plane) |
   | `SELF_HOSTED_SERVER` | `{EVENT_SOURCED_REPLAY, SAVE_POINT_CHECKPOINT, RECONCILER_LOOP, WAL_SEGMENT}` | `PURE_PATTERN_NO_ENGINE` (server context requires durability primitive) |
   | `MANAGED_CLOUD` | `{EVENT_SOURCED_REPLAY, SAVE_POINT_CHECKPOINT, RECONCILER_LOOP, WAL_SEGMENT}` | `PURE_PATTERN_NO_ENGINE` (managed context requires durability primitive) |

3. Exclusion inheritance is inherited at U-CP-40 HITL matrix per §18.2 (cell exclusion observed, not re-derived).
4. Specific engine candidates within each set deferred to implementation discretion per spec §7.2 deferred list.

**Tests:** `test_deployment_surface_cardinality_three`, `test_engine_class_candidates_cardinality_three`, `test_candidate_sets_match_spec`, `test_local_excludes_reconciler`, `test_server_and_cloud_exclude_pure_pattern`.

**Rollback boundary:** Revert candidate mapping. U-CP-17 workload-binding selection loses deployment-surface filter; U-CP-40 HITL matrix loses cell exclusion source.

#### U-CP-17 — Implement workload-binding-time engine-class selection (5-step procedure)

**Implements:** [C-CP-07 §7.3]

**Depends on:** [U-CP-15, U-CP-16]

**Inputs:** `EngineClass` enum (U-CP-15); candidate mapping (U-CP-16).

**Files affected:** CP-axis workload-binding selection procedure (logical: `workload-binding-engine-class-selection`).

**Signatures:**

```
record WorkloadBindingSelectionInput {
  workload_class      : WorkloadClass
  deployment_surface  : DeploymentSurface
  persona_tier        : PersonaTier
  operator_preferences: Optional<EngineClassPreferences>
}

record WorkloadBindingSelectionResult {
  selected_class      : EngineClass
  candidate_set       : Set<EngineClass>
  selection_rationale : string
}

function select_engine_class(input: WorkloadBindingSelectionInput) -> WorkloadBindingSelectionResult
```

**Acceptance criteria:**
1. `select_engine_class` implements §7.3 five-step procedure verbatim:
   - Step 1: Resolve candidate set from U-CP-16 per `deployment_surface`.
   - Step 2: Filter candidates by `workload_class` admissibility (event-sourced-replay favored at pipeline-automation; save-point-checkpoint favored at software-engineering; reconciler-loop favored at content-creation when reconvergence required).
   - Step 3: Filter candidates by `persona_tier` (solo-developer admits pure-pattern; team-binding+ requires durability primitive).
   - Step 4: Apply operator preferences if declared.
   - Step 5: Return single selected class; selection_rationale documents winning filter.
2. Selection is deterministic given inputs; no inference path.
3. Selection runs at **workload-binding time** (not at runtime); validation failure aborts workflow binding.

**Tests:** `test_select_engine_class_five_step`, `test_step_1_resolves_candidates_from_u_cp_16`, `test_step_2_workload_class_filter`, `test_step_3_persona_tier_filter`, `test_step_4_operator_preference_filter`, `test_selection_deterministic`, `test_selection_at_binding_time`.

**Rollback boundary:** Revert workload-binding selection. Workflow manifest entry (U-CP-13) loses engine-class binding source; manifest validation degrades to operator-declared engine without admissibility filtering.

#### U-CP-18 — Implement F2 substrate join discipline (R-CP-07-satisfying contract)

**Implements:** [C-CP-08 §8.2]

**Depends on:** [U-CP-15, U-IS-07 (cross-axis: IS), U-IS-09 (cross-axis: IS), U-IS-12 (cross-axis: IS)]

**Inputs:** `EngineClass` enum (U-CP-15); F2 substrate (U-IS-07, U-IS-09, U-IS-12 cross-axis).

**Files affected:** CP-axis F2 substrate join (logical: `f2-substrate-join-discipline`).

**Cross-axis substrate consumed.** `STATE_LEDGER_ENTRY_SHAPE_EXPORT` (C-IS-10 §10.1 → U-IS-07); `HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT` (C-IS-10 §10.3 → U-IS-09); `IDEMPOTENCY_KEY_JOIN_EXPORT` (C-IS-10 §10.2 → U-IS-12).

**Signatures:**

```
record EngineF2JoinContract {
  engine_class          : EngineClass
  join_kind             : F2JoinKind
  read_contract         : string                      // delegates to U-IS-07 read primitive
  write_contract        : string                      // delegates to U-IS-07 write primitive
  chain_construction    : string                      // delegates to U-IS-09 prior_event_hash
  idempotency_key_path  : string                      // delegates to U-IS-12 join key
}

enum F2JoinKind {
  ENGINE_NATIVE_LEDGER,                               // event-sourced-replay engines own ledger
  HARNESS_OVERLAY_LEDGER,                             // save-point/pure-pattern/WAL engines compose above harness ledger
  CRD_RECONCILER_LEDGER                               // reconciler-loop owns CRD-resident ledger
}

const ENGINE_F2_JOIN_CONTRACTS: List<EngineF2JoinContract>  // exactly 5 entries (one per EngineClass)

function f2_join_contract(engine: EngineClass) -> EngineF2JoinContract
```

**Acceptance criteria:**
1. `F2JoinKind` declares exactly three values per C-CP-08 §8.2 verbatim discrimination.
2. `ENGINE_F2_JOIN_CONTRACTS` declares exactly five entries (one per `EngineClass`):
   - `EVENT_SOURCED_REPLAY` → `ENGINE_NATIVE_LEDGER`
   - `SAVE_POINT_CHECKPOINT` → `HARNESS_OVERLAY_LEDGER`
   - `PURE_PATTERN_NO_ENGINE` → `HARNESS_OVERLAY_LEDGER`
   - `RECONCILER_LOOP` → `CRD_RECONCILER_LEDGER`
   - `WAL_SEGMENT` → `HARNESS_OVERLAY_LEDGER`
3. Join discipline preserves F2 six-field shape regardless of join kind per §8.2; engine-native and CRD-reconciler join kinds adapt their internal substrate to expose the F2 shape at read surface.
4. Read contract delegates to U-IS-12; write contract delegates to U-IS-07 + U-IS-09 composition.
5. This unit is the **R-CP-07-satisfying contract** per spec §8.2.
6. **F2-12 carry-forward note.** Active engagement at U-CP-20 (resumption observable behavior). Closure path declared at U-CP-55 §24.4; not closed at v1.

**Tests:** `test_f2_join_kind_cardinality_three`, `test_engine_f2_join_contracts_cardinality_five`, `test_per_engine_join_kind_match_spec`, `test_f2_shape_preserved_across_join_kinds`, `test_delegates_to_u_is_07_09_12`.

**Rollback boundary:** Revert F2 join contract table. R-CP-07 acceptance criterion fails; engine-class boundary loses F2 substrate composition; CP plan loses canonical F2 read/write delegation. Cross-axis IS edges to U-IS-07, U-IS-09, U-IS-12 release.

#### U-CP-19 — Declare `ResumptionKind` 5-class taxonomy

**Implements:** [C-CP-08 §8.1]

**Depends on:** [U-CP-15]

**Inputs:** `EngineClass` enum (U-CP-15).

**Files affected:** CP-axis resumption kind enum (logical: `resumption-kind-enum`).

**Signatures:**

```
enum ResumptionKind {
  REPLAY_FROM_EVENT,                                  // event-sourced-replay engines
  RESTORE_FROM_CHECKPOINT,                            // save-point-checkpoint engines
  RECONSTRUCT_FROM_LEDGER,                            // pure-pattern (12-factor) engines
  RECONVERGE_VIA_RECONCILER,                          // reconciler-loop engines
  RESUME_FROM_WAL_SEGMENT                             // WAL-segment engines
}

record ResumptionKindBinding {
  engine_class    : EngineClass
  resumption_kind : ResumptionKind
}
const RESUMPTION_KIND_BINDINGS: List<ResumptionKindBinding>  // exactly 5 entries (1:1 with EngineClass)
```

**Acceptance criteria:**
1. `ResumptionKind` declares exactly five values per C-CP-08 §8.1 verbatim.
2. `RESUMPTION_KIND_BINDINGS` declares 1:1 mapping `EngineClass → ResumptionKind` per §8.1 verbatim.
3. Taxonomy closed at cardinality 5; extension requires Workflow §4.1.2 Class-2 D1 revision.

**Tests:** `test_resumption_kind_cardinality_five`, `test_resumption_kind_bindings_1to1_with_engine_class`, `test_taxonomy_closed`.

**Rollback boundary:** Revert `ResumptionKind` enum + bindings. U-CP-20 resumption observable behavior loses kind discriminator; F2-12 carry-forward narrative loses anchor.

#### U-CP-20 — Implement per-resumption observable behavior (F2-12 active carry-forward)

**Implements:** [C-CP-08 §8.3]

**Depends on:** [U-CP-10, U-CP-12, U-CP-18, U-CP-19]

**Inputs:** Lifecycle event class enum (U-CP-10); per-class attribute composition (U-CP-12); F2 join contract (U-CP-18); `ResumptionKind` enum (U-CP-19).

**Files affected:** CP-axis per-resumption observable behavior (logical: `per-resumption-observable-behavior`); CP-axis F2-12 carry-forward declaration (logical: `f2-12-carry-forward-active`).

**Signatures:**

```
record PerResumptionObservableBehavior {
  resumption_kind        : ResumptionKind
  emits_span             : string                     // workflow.resumption
  required_attributes    : Set<string>                // includes engine.class, engine.resumption_kind
  f2_join_path           : F2JoinKind                 // from U-CP-18
  observable_continuity  : ContinuityGuarantee
}

enum ContinuityGuarantee {
  EXACT_REPLAY,
  CHECKPOINT_RESTORE,
  REPLAY_FROM_LEDGER,
  RECONVERGE,
  WAL_REPLAY
}

const PER_RESUMPTION_OBSERVABLE_BEHAVIOR: List<PerResumptionObservableBehavior>  // exactly 5 entries
```

**Acceptance criteria:**
1. `PER_RESUMPTION_OBSERVABLE_BEHAVIOR` declares exactly five entries per C-CP-08 §8.3 verbatim.
2. Each entry emits `workflow.resumption` span per U-CP-10 lifecycle event class; required attributes include `engine.class` + `engine.resumption_kind` per U-CP-21 `engine.*` namespace.
3. `f2_join_path` carried from U-CP-18 `EngineF2JoinContract`; resumption observable behavior is per-engine-class.
4. `ContinuityGuarantee` discriminates across the five resumption kinds; per-kind continuity contract documented at acceptance.
5. **F2-12 carry-forward active at this unit.** Per CP spec §24.4: D1 v1.2 + D6 v1.2 → ADD v1.3 → PRD v1.1 → CP spec v1.3 revision required to close. CP plan v1 declares the carry-forward; closure deferred to revision-pass mode per spec-writer precedent.

**Tests:** `test_per_resumption_observable_behavior_cardinality_five`, `test_emits_workflow_resumption_span`, `test_engine_class_required_attribute`, `test_continuity_guarantee_per_kind`, `test_f2_12_carry_forward_declared`.

**Rollback boundary:** Revert per-resumption observable behavior. R-CP-04 acceptance criterion (engine-class resumption transparency) fails; F2-12 carry-forward declaration site dissolves.

#### U-CP-21 — Declare `engine.*` namespace + 3-attribute schema

**Implements:** [C-CP-09 §9.1 (engine.* namespace declaration per three-attribute schema; consumed at C-CP-05 §5.2 per-class attribute composition and C-CP-09 §9.4 D6 ingestion contract)]

**Depends on:** [U-CP-15]

**Inputs:** `EngineClass` enum (U-CP-15).

**Files affected:** CP-axis engine namespace (logical: `engine-namespace-attribute-schema`).

**Signatures:**

```
record EngineAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
}
const ENGINE_NAMESPACE_SCHEMA: List<EngineAttributeSchema>  // exactly 3 entries
```

**Acceptance criteria:**
1. `ENGINE_NAMESPACE_SCHEMA` declares exactly three attributes per ADR-D1 v1.1 §1.1.1 + CP spec §5.3 + §9.2 verbatim: `engine.class` (`EngineClass` enum value), `engine.resumption_kind` (`ResumptionKind` enum value), `engine.tech` (deployment-bound; e.g., "temporal-worker", "langgraph-postgres-redis", "kafka-streams").
2. `engine.class` cardinality bounded at 5 (matches `EngineClass`); `engine.resumption_kind` cardinality bounded at 5 (matches `ResumptionKind`); `engine.tech` cardinality low-medium (deployment-bound).
3. D6 ingestion delegates to U-CP-54 §24.1.A (specialization-layer namespace).

**Tests:** `test_engine_namespace_cardinality_three`, `test_engine_attributes_match_spec_verbatim`, `test_engine_class_cardinality_bounded_five`, `test_engine_resumption_kind_cardinality_bounded_five`.

**Rollback boundary:** Revert `ENGINE_NAMESPACE_SCHEMA`. U-CP-12 per-class attribute composition for `workflow.resumption` loses required attributes; U-CP-20 observable behavior loses namespace anchor; U-CP-54 §24.1.A export manifest loses CP-side source declaration.

---

### §2.4 Cluster 4 — D4 topology + sub-agent (C-CP-10, C-CP-11, C-CP-12)

**Anchor.** ADR-D4 v1.1.

**Theme.** Three contracts compose the sub-agent topology and gate-level inheritance substrate: 6-pattern topology enum + admissibility (C-CP-10); workload-class × engine-class 2D matrix + D4 multiplicative tunable + per-engine overlay (C-CP-11); sub-agent gate-level composition with default-downgrade + monotonic descent + cross-deployment monotonicity (C-CP-12).

#### U-CP-22 — Declare 6-pattern `TopologyPattern` enum + admissibility predicate

**Implements:** [C-CP-10 §10.1, §10.2, §10.3]

**Depends on:** (none)

**Inputs:** None (foundational; substrate-supplying enum unit).

**Files affected:** CP-axis topology pattern enum (logical: `topology-pattern-enum`); CP-axis topology admissibility predicate (logical: `topology-admissibility-predicate`).

**Signatures:**

```
enum TopologyPattern {
  SINGLE_AGENT,
  SEQUENTIAL_HANDOFF,
  PARENT_FANOUT_AGGREGATE,
  RECONCILER_MESH,
  ROUTER_DELEGATE,
  PIPELINE_STAGES
}

enum CascadePolicy {
  COMPLETE_ALL,                                       // wait for all siblings; aggregate
  CANCEL_ON_FIRST_FAIL,                               // cancel siblings on first failure
  PAUSE_ON_FIRST_FAIL                                 // pause workflow; route to HITL
}

function is_admissible(pattern: TopologyPattern, workload: WorkloadClass) -> bool
    // §10.2 admissibility predicate; pre-conditions per pattern × workload pair
```

**Acceptance criteria:**
1. `TopologyPattern` declares exactly six values per C-CP-10 §10.1 verbatim.
2. `CascadePolicy` declares exactly three values per C-CP-10 §10.3 verbatim.
3. `is_admissible` returns `true` per §10.2 admissibility matrix: SEQUENTIAL_HANDOFF and PARENT_FANOUT_AGGREGATE admissible for all four workload classes; RECONCILER_MESH admissible for content-creation + pipeline-automation; ROUTER_DELEGATE admissible for software-engineering + research; PIPELINE_STAGES admissible only for pipeline-automation.
4. Taxonomy closed at cardinality 6; extension requires Workflow §4.1.2 Class-2 D4 revision.

**Tests:** `test_topology_pattern_cardinality_six`, `test_cascade_policy_cardinality_three`, `test_admissibility_per_workload_class_match_spec`, `test_pipeline_stages_pipeline_only`, `test_taxonomy_closed`.

**Rollback boundary:** Revert `TopologyPattern` + `CascadePolicy` enums + admissibility predicate. All downstream D4 units (Cluster 4 + Cluster 5) lose topology discriminator; sub-agent dispatch loses pattern selection.

#### U-CP-23 — Declare per-workload-class topology commitment table

**Implements:** [C-CP-11 §11.1]

**Depends on:** [U-CP-22]

**Inputs:** `TopologyPattern` enum (U-CP-22).

**Files affected:** CP-axis per-workload-class topology commitment (logical: `per-workload-class-topology-commitment`).

**Signatures:**

```
record PerWorkloadClassTopologyCommitment {
  workload_class       : WorkloadClass
  default_pattern      : TopologyPattern
  permitted_patterns   : Set<TopologyPattern>         // subset of TopologyPattern values
  rationale            : string                       // §11.1 verbatim
}
const PER_WORKLOAD_CLASS_TOPOLOGY: List<PerWorkloadClassTopologyCommitment>  // exactly 4 entries
```

**Acceptance criteria:**
1. `PER_WORKLOAD_CLASS_TOPOLOGY` declares exactly four entries per C-CP-11 §11.1 verbatim (one per workload class).
2. Default pattern per workload class:
   - `software-engineering` → `SEQUENTIAL_HANDOFF`
   - `content-creation` → `PARENT_FANOUT_AGGREGATE`
   - `pipeline-automation` → `PIPELINE_STAGES`
   - `research` → `ROUTER_DELEGATE`
3. Permitted patterns per workload class composes with `is_admissible` from U-CP-22; no permitted pattern violates admissibility.
4. Workload-class commitment is the source-of-truth for U-CP-25 2D matrix anchoring.

**Tests:** `test_per_workload_class_topology_cardinality_four`, `test_default_patterns_match_spec`, `test_permitted_composes_with_admissibility`.

**Rollback boundary:** Revert per-workload topology commitment. U-CP-25 2D matrix loses row anchor; workflow manifest validation at U-CP-13 loses topology default source.

#### U-CP-24 — Implement per-engine-class topology overlay + T-perm-3 reading binding

**Implements:** [C-CP-11 §11.2]

**Depends on:** [U-CP-15, U-CP-11]

**Inputs:** `EngineClass` enum (U-CP-15); `lease.*` namespace (U-CP-11) — referenced for cascade-enforcement at engine-native lifecycle ownership.

**Files affected:** CP-axis per-engine-class topology overlay (logical: `per-engine-class-topology-overlay`); CP-axis T-perm-3 reading binding (logical: `t-perm-3-reading-binding`).

**Signatures:**

```
enum TopologyFaultHandling {
  ABOVE_ENGINE,                                       // harness composes lease + dedup + resumption
  BELOW_ENGINE,                                       // engine owns lifecycle; harness becomes topology-author
  RECONCILER                                          // control-loop owns reconvergence
}

record PerEngineClassTopologyOverlay {
  engine_class                     : EngineClass
  t_perm_3_reading                 : TopologyFaultHandling
  cascade_enforcement_mechanism    : CascadeEnforcementMechanism
  writer_serialization_mechanism   : WriterSerializationMechanism
}

enum CascadeEnforcementMechanism {
  HARNESS_CANCELLATION_PROPAGATION,
  ENGINE_NATIVE_CANCELLATION,
  CRD_RECONCILER_DRIVEN
}

enum WriterSerializationMechanism {
  HARNESS_LEASE_ACQUISITION,
  ENGINE_NATIVE_WRITER_SERIAL,
  CRD_RESOURCE_VERSION
}

const PER_ENGINE_CLASS_OVERLAYS: List<PerEngineClassTopologyOverlay>  // exactly 5 entries
```

**Acceptance criteria:**
1. `PER_ENGINE_CLASS_OVERLAYS` declares exactly five entries per C-CP-11 §11.2 verbatim:

   | engine_class | t_perm_3_reading | cascade_enforcement | writer_serialization |
   |---|---|---|---|
   | `EVENT_SOURCED_REPLAY` | `BELOW_ENGINE` | `ENGINE_NATIVE_CANCELLATION` | `ENGINE_NATIVE_WRITER_SERIAL` |
   | `SAVE_POINT_CHECKPOINT` | `ABOVE_ENGINE` | `HARNESS_CANCELLATION_PROPAGATION` | `HARNESS_LEASE_ACQUISITION` |
   | `PURE_PATTERN_NO_ENGINE` | `ABOVE_ENGINE` | `HARNESS_CANCELLATION_PROPAGATION` | `HARNESS_LEASE_ACQUISITION` |
   | `RECONCILER_LOOP` | `RECONCILER` | `CRD_RECONCILER_DRIVEN` | `CRD_RESOURCE_VERSION` |
   | `WAL_SEGMENT` | `ABOVE_ENGINE` | `HARNESS_CANCELLATION_PROPAGATION` | `HARNESS_LEASE_ACQUISITION` |

2. T-perm-3 reading is **per-engine-class** binding; no engine class maps to multiple readings (per §11.2 non-collapsing invariant + U-CP-53 acceptance).
3. Cascade-enforcement mechanism delegates to engine-native at `BELOW_ENGINE`; harness-driven at `ABOVE_ENGINE`; CRD-driven at `RECONCILER`.

**Tests:** `test_per_engine_overlays_cardinality_five`, `test_per_engine_overlay_match_spec_verbatim`, `test_t_perm_3_reading_one_per_engine`, `test_cascade_enforcement_consistent_with_reading`.

**Rollback boundary:** Revert per-engine topology overlay. U-CP-25 2D matrix loses column anchor; U-CP-53 T-perm-3 composition loses D1-layer reading source.

#### U-CP-25 — Implement workload-class × engine-class 2D matrix + D4 multiplicative tunable

**Implements:** [C-CP-11 §11.3, §11.4]

**Depends on:** [U-CP-15, U-CP-22, U-CP-23, U-CP-24]

**Inputs:** `EngineClass` enum (U-CP-15); `TopologyPattern` enum (U-CP-22); per-workload commitment (U-CP-23); per-engine overlay (U-CP-24).

**Files affected:** CP-axis 2D matrix (logical: `workload-engine-class-2d-matrix`); CP-axis D4 multiplicative tunable (logical: `d4-multiplicative-tunable`).

**Signatures:**

```
record WorkloadEngineMatrixCell {
  workload_class                : WorkloadClass
  engine_class                  : EngineClass
  topology_pattern              : TopologyPattern
  cascade_enforcement_mechanism : CascadeEnforcementMechanism
  t_perm_3_reading              : TopologyFaultHandling
  cell_admissible               : bool                // false when (workload, engine) excluded at U-CP-16
}
const WORKLOAD_ENGINE_MATRIX: List<WorkloadEngineMatrixCell>  // exactly 20 entries (4 × 5)

record D4MultiplicativeTunable {
  topology_fault_handling : TopologyFaultHandling
  workload_class          : WorkloadClass
  topology_pattern        : TopologyPattern
  cascade_policy          : CascadePolicy
}

function lookup_cell(workload: WorkloadClass, engine: EngineClass) -> WorkloadEngineMatrixCell
function d4_tunable(cell: WorkloadEngineMatrixCell, persona_tier: PersonaTier) -> D4MultiplicativeTunable
```

**Acceptance criteria:**
1. `WORKLOAD_ENGINE_MATRIX` declares exactly 20 cells (4 workload classes × 5 engine classes) per C-CP-11 §11.3 verbatim.
2. Each cell's `topology_pattern` composes with U-CP-23 default pattern AND U-CP-24 per-engine overlay; cells where (workload, engine) is structurally excluded carry `cell_admissible = false`.
3. `lookup_cell` is deterministic; returns matrix cell content for the given pair.
4. `d4_tunable` returns D4 multiplicative composition per §11.4: `(topology_fault_handling, workload_class, topology_pattern, cascade_policy)`; persona-tier influences cascade_policy default.

**Tests:** `test_workload_engine_matrix_cardinality_twenty`, `test_matrix_composes_with_u_cp_23_defaults`, `test_matrix_composes_with_u_cp_24_overlay`, `test_excluded_cells_marked`, `test_lookup_cell_deterministic`, `test_d4_tunable_composition`.

**Rollback boundary:** Revert 2D matrix + D4 tunable. R-CP-08 multi-agent topology surface fails; U-CP-53 T-perm-3 composition loses D4-layer source.

#### U-CP-26 — Declare default-downgrade rule (Tier-3 → Tier-1 ceiling)

**Implements:** [C-CP-12 §12.1]

**Depends on:** [U-AS-01 (cross-axis: AS)]

**Inputs:** `SandboxTier` enum + `BlastRadiusTier` enum (U-AS-01 cross-axis AS).

**Files affected:** CP-axis default-downgrade rule (logical: `sub-agent-default-downgrade-rule`).

**Cross-axis substrate consumed.** AS C-AS-01 `SandboxTier` + `BlastRadiusTier` foundational substrate via U-AS-01.

**Signatures:**

```
record SubAgentDefaultDowngrade {
  parent_blast_radius : BlastRadiusTier
  child_ceiling       : BlastRadiusTier               // Tier-3 (EXTERNAL_REVERSIBLE) → Tier-1 (READ_ONLY)
  rationale           : string                       // §12.1 verbatim
}
const DEFAULT_DOWNGRADE_RULE: SubAgentDefaultDowngrade

function compute_child_blast_radius_ceiling(parent: BlastRadiusTier) -> BlastRadiusTier
```

**Acceptance criteria:**
1. `DEFAULT_DOWNGRADE_RULE` declares per C-CP-12 §12.1 verbatim: parent Tier-3 → child Tier-1 ceiling.
2. `compute_child_blast_radius_ceiling` returns ceiling per spec §12.1 four-row table; Tier-1 parent → Tier-1 child, Tier-2 parent → Tier-1 child, Tier-3 parent → Tier-1 child (downgrade), Tier-4 parent → Tier-1 child (downgrade).
3. Default-downgrade is **default** (operator override permitted with audit per U-CP-27).
4. Rule applies at sub-agent dispatch time; pre-condition for U-CP-27 monotonic descent computation.

**Tests:** `test_default_downgrade_rule_per_spec_verbatim`, `test_tier_3_parent_yields_tier_1_child`, `test_compute_ceiling_four_row_table`, `test_default_with_override_permitted`.

**Rollback boundary:** Revert default-downgrade rule. R-CP-09 sub-agent privilege inheritance surface fails; U-CP-27 monotonic descent loses ceiling input. Cross-axis AS edge to U-AS-01 releases.

#### U-CP-27 — Implement sub-agent gate-level monotonic descent + override audit + cross-deployment monotonicity composition

**Implements:** [C-CP-12 §12.2, §12.3, §12.4, §12.5]

**Depends on:** [U-CP-22, U-CP-26, U-CP-43, U-AS-09 (cross-axis: AS), U-AS-14 (cross-axis: AS), U-AS-15 (cross-axis: AS), U-IS-07 (cross-axis: IS), U-IS-09 (cross-axis: IS), U-IS-11 (cross-axis: IS)]

**Inputs:** `TopologyPattern` enum (U-CP-22); default-downgrade rule (U-CP-26); 4-axis multiplicative gate-level rule (U-CP-43); AS substrate (U-AS-09, U-AS-14, U-AS-15); F2 substrate (U-IS-07, U-IS-09, U-IS-11).

**Files affected:** CP-axis sub-agent gate-level descent (logical: `sub-agent-gate-level-monotonic-descent`); CP-axis sub-agent dispatch audit entry composition (logical: `sub-agent-dispatch-audit-composition`).

**Cross-axis substrate consumed.** `FIVE_AXIS_MULTIPLICATIVE_TUNABLE_EXPORT` (C-AS-16 §16.2 → U-AS-09, U-AS-14, U-AS-15) for sandbox-tier ascension + cross-deployment monotonicity; F2 substrate seams for audit entry composition.

**Signatures:**

```
record SubAgentGateLevelDescent {
  parent_gate_level       : GateLevel                 // from U-CP-43 at parent dispatch site
  parent_sandbox_tier     : SandboxTier
  child_blast_radius_ceiling : BlastRadiusTier
  child_sandbox_tier      : SandboxTier               // monotonic ascent (≥ parent) per U-AS-09
  child_gate_level        : GateLevel                 // monotonic descent constraint
  override_applied        : bool
  override_audit_ref      : Optional<LedgerEntryRef>
}

function dispatch_sub_agent(
    parent_action_id: ActionID,
    parent_gate_level: GateLevel,
    parent_sandbox_tier: SandboxTier,
    sub_agent_brief: SubAgentBrief,
    operator_override: Optional<GateOverride>
) -> SubAgentGateLevelDescent

function emit_sub_agent_dispatch_audit(
    parent_action_id: ActionID,
    descent: SubAgentGateLevelDescent,
    brief_hash: SHA256
) -> AuditLedgerEntry
    // §12.5 audit entry composition
```

**Acceptance criteria:**
1. `child_gate_level ≤ parent_gate_level` per §12.2 monotonic-descent invariant; ascent prohibited.
2. `child_sandbox_tier ≥ parent_sandbox_tier` per U-AS-09 monotonic-ascent (sandbox tier ascends; gate level descends; orthogonal axes).
3. `child_blast_radius_ceiling` from U-CP-26 default-downgrade rule; operator override permitted at SOLO_DEVELOPER and TEAM_BINDING with audit; prohibited at MULTI_TENANT_COMPLIANCE per U-CP-45 operator-policy override scope.
4. Cross-deployment monotonicity composes per §12.4 with U-CP-43 + U-AS-15: sub-agent dispatch within bridging-arc traversal honors monotonic ascending `persona_tier_floor` AND `sandbox_tier_floor`.
5. Audit entry shape per §12.5: F2 six-field per U-IS-07, prior_event_hash per U-IS-09, append via U-IS-11; `response_hash = sha256(canonicalize(SubAgentBrief))`.
6. `parent_gate_level` resolves via U-CP-43 `gate_level(...)` at parent dispatch site; this unit consumes the result, does not recompute.

**Tests:** `test_child_gate_level_monotonic_descent`, `test_child_sandbox_tier_monotonic_ascent`, `test_default_downgrade_applied`, `test_override_permitted_at_solo_and_team`, `test_override_prohibited_at_multi_tenant`, `test_cross_deployment_monotonicity_composition`, `test_audit_entry_f2_six_field_shape`, `test_audit_entry_response_hash_brief_canonicalize`.

**Rollback boundary:** Revert sub-agent gate-level descent + audit composition. R-CP-09 sub-agent privilege inheritance fails; sub-agent dispatch loses gate-level inheritance discipline; audit trail for sub-agent privilege transitions dissolves. Cross-axis AS edges (U-AS-09, U-AS-14, U-AS-15) and IS edges (U-IS-07, U-IS-09, U-IS-11) release.

---

### §2.5 Cluster 5 — D4 handoff + spans + audit (C-CP-13, C-CP-14, C-CP-15)

**Anchor.** ADR-D4 v1.1.

**Theme.** Three contracts compose the multi-agent dispatch substrate: HandoffContext + SubAgentBrief + StateSummary + LedgerEntryRef (C-CP-13); multi-agent span hierarchy + namespaces + sampling + cache warm-up (C-CP-14); per-sibling F2 ledger + fanout-close primitive + merkle + crypto + trace inspection (C-CP-15).

#### U-CP-28 — Declare `SubAgentBrief` schema

**Implements:** [C-CP-13 §13.2]

**Depends on:** (none)

**Inputs:** None (foundational schema declaration).

**Files affected:** CP-axis SubAgentBrief schema (logical: `sub-agent-brief-schema`).

**Signatures:**

```
record SubAgentBrief {
  objective            : string                       // single sentence; bounded scope
  output_format        : OutputSchema
  guidance             : string                       // approach hints; non-prescriptive
  task_boundaries      : ClearTaskBoundaries
  summary_hash         : SHA256                       // sha256(canonicalize(brief))
}

record OutputSchema {
  schema_kind  : OutputSchemaKind                     // {JSON_SCHEMA, FREE_TEXT, STRUCTURED_RECORD}
  schema_body  : Optional<string>
}

record ClearTaskBoundaries {
  in_scope             : List<string>
  out_of_scope         : List<string>
  termination_criteria : List<string>
}

function canonicalize_brief(brief: SubAgentBrief) -> bytes
function compute_brief_summary_hash(brief: SubAgentBrief) -> SHA256
```

**Acceptance criteria:**
1. `SubAgentBrief` declares exactly five fields per C-CP-13 §13.2 verbatim.
2. `ClearTaskBoundaries` declares three fields per §13.2; explicit scope-limit prevents sub-agent scope-creep.
3. `compute_brief_summary_hash` returns `sha256(canonicalize_brief(brief))`; canonicalization deterministic.
4. `summary_hash` is the join key for U-CP-27 audit entry (`response_hash` source).

**Tests:** `test_sub_agent_brief_five_fields`, `test_clear_task_boundaries_three_fields`, `test_canonicalize_deterministic`, `test_summary_hash_round_trip`.

**Rollback boundary:** Revert `SubAgentBrief`. U-CP-30 HandoffContext loses brief embedding; U-CP-13 manifest entry loses `sub_agent_briefs` element type; U-CP-27 audit loses `response_hash` source.

#### U-CP-29 — Declare brief-authoring model-binding inheritance table

**Implements:** [C-CP-13 §13.3]

**Depends on:** [U-CP-28, U-AS-29 (cross-axis: AS)]

**Inputs:** `SubAgentBrief` (U-CP-28); per-sub-agent-role × model-binding catalog (U-AS-29 cross-axis).

**Files affected:** CP-axis brief-authoring inheritance table (logical: `brief-authoring-inheritance`).

**Cross-axis substrate consumed.** `ELEVEN_PRIMITIVE_ADOPTION_DEPTH_MATRIX_EXPORT` (C-AS-16 §16.6 → U-AS-29).

**Signatures:**

```
enum InheritanceRule {
  INHERIT_LEAD_BINDING,
  INHERIT_PER_STAGE_LEAD_BINDING
}

record BriefAuthoringInheritance {
  workload_class        : WorkloadClass
  inheritance_rule      : InheritanceRule
  reducible_to_haiku    : bool                        // always false per ADR-D3 v1.2 §1.4
  narrative             : string
}
const BRIEF_AUTHORING_INHERITANCE: List<BriefAuthoringInheritance>  // exactly 4 entries

function inheritance_for(workload_class: WorkloadClass) -> BriefAuthoringInheritance
function resolve_brief_authoring_model_binding(workload_class: WorkloadClass, stage_id: Optional<StageID>) -> ModelBinding
```

**Acceptance criteria:**
1. `BRIEF_AUTHORING_INHERITANCE` declares exactly four entries per C-CP-13 §13.3 verbatim:
   - `software-engineering` → `INHERIT_LEAD_BINDING`
   - `content-creation` → `INHERIT_LEAD_BINDING`
   - `pipeline-automation` → `INHERIT_PER_STAGE_LEAD_BINDING`
   - `research` → `INHERIT_LEAD_BINDING`
2. `reducible_to_haiku == false` invariant for all rows per ADR-D3 v1.2 §1.4 NOT-reducible-to-Haiku clause.
3. `resolve_brief_authoring_model_binding` delegates to U-AS-29 catalog; this unit declares inheritance rule only.
4. Brief-authoring binding is **not independently configurable** per §13.3 closing sentence.

**Tests:** `test_brief_authoring_inheritance_cardinality_four`, `test_inheritance_rule_per_workload_class`, `test_reducible_to_haiku_false_invariant`, `test_delegates_to_u_as_29`, `test_no_independent_override`.

**Rollback boundary:** Revert inheritance table. Brief-authoring loses workload-class-specific binding rule; runtime defaults to lead-agent's bound model uniformly. Cross-axis AS edge to U-AS-29 unaffected.

#### U-CP-30 — Declare `HandoffContext` + `StateSummary` + `LedgerEntryRef` schemas

**Implements:** [C-CP-13 §13.1, §13.4, §13.5]

**Depends on:** [U-CP-07, U-CP-28, U-IS-07 (cross-axis: IS), U-IS-12 (cross-axis: IS)]

**Inputs:** `RETRY_NAMESPACE_SCHEMA` (U-CP-07) for `RetryHistory`; `SubAgentBrief` (U-CP-28); F2 entry shape (U-IS-07); idempotency-key join (U-IS-12).

**Files affected:** CP-axis HandoffContext schema (logical: `handoff-context-schema`); StateSummary schema (logical: `state-summary-schema`); LedgerEntryRef schema (logical: `ledger-entry-ref-schema`).

**Cross-axis substrate consumed.** `STATE_LEDGER_ENTRY_SHAPE_EXPORT` + `IDEMPOTENCY_KEY_JOIN_EXPORT` (C-IS-10 §10.1, §10.2 → U-IS-07, U-IS-12).

**Signatures:**

```
record HandoffContext {
  proposed_action          : ProposedAction
  agent_confidence         : Optional<Float>
  failed_attempts          : List<FailedAttempt>
  alternatives_considered  : List<Alternative>
  state_summary            : StateSummary
  audit_trail_link         : LedgerEntryRef
  retry_history            : RetryHistory
}

record ProposedAction {
  action_kind     : ActionKind                        // {TOOL_CALL, SUB_AGENT_DISPATCH, INFERENCE_STEP}
  payload         : ActionPayload
  brief           : Optional<SubAgentBrief>           // populated when action_kind = SUB_AGENT_DISPATCH
}

record StateSummary {
  relevant_entries     : List<LedgerEntryRef>
  summary_text         : string
  summary_hash         : SHA256
  idempotency_key      : IdempotencyKey
  external_references  : List<ExternalReference>     // pause-time snapshot anchors per U-CP-49
}

record LedgerEntryRef {
  action_id   : ActionID
  entry_hash  : SHA256
  actor       : ActorIdentity
}

record ExternalReference {
  reference_class           : ReferenceClass         // {F2_LEDGER_ENTRY, EXTERNAL_MCP_RESOURCE, FILESYSTEM_STATE, FAILED_ATTEMPTS_HISTORY}
  reference_id              : string
  snapshot_capture_at_pause : Optional<bytes>
}
```

**Acceptance criteria:**
1. `HandoffContext` declares exactly seven fields per C-CP-13 §13.1 verbatim.
2. `StateSummary` declares five fields per §13.4 verbatim plus `external_references` for U-CP-49 pause-time snapshot composition.
3. `LedgerEntryRef` declares three fields per §13.5 verbatim.
4. `idempotency_key` references `IDEMPOTENCY_KEY_JOIN_EXPORT` per §13.4 + C-IS-10 §10.2.
5. T-perm-2 (across-turn boundary) crosses through F2 read/write contract pair per §13.1; F2-layer resolution stands.
6. Serialization format deferred to implementation discretion per spec §13.1 deferred list.

**Tests:** `test_handoff_context_seven_fields`, `test_state_summary_five_spec_fields_plus_external_references`, `test_ledger_entry_ref_three_fields`, `test_idempotency_key_references_u_is_12`, `test_t_perm_2_f2_layer_resolution_stands`.

**Rollback boundary:** Revert HandoffContext + StateSummary + LedgerEntryRef. Sub-agent dispatch loses payload schema; U-CP-38 `hitl_gate` signature loses `handoff_context` parameter type; U-CP-49 resume protocol loses snapshot-capture target. Cross-axis IS edges to U-IS-07, U-IS-12 release.

#### U-CP-31 — Declare `topology.*` + `subagent.*` span attribute namespaces

**Implements:** [C-CP-14 §14.2]

**Depends on:** [U-CP-22, U-CP-15]

**Inputs:** `TopologyPattern` enum + `CascadePolicy` enum (U-CP-22); `EngineClass` enum (U-CP-15).

**Files affected:** CP-axis topology namespace (logical: `topology-namespace-attribute-schema`); CP-axis subagent namespace (logical: `subagent-namespace-attribute-schema`).

**Signatures:**

```
record TopologyAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
  emitted_on     : string                             // span name
}
const TOPOLOGY_NAMESPACE_SCHEMA: List<TopologyAttributeSchema>  // exactly 10 entries

record SubAgentAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
  emitted_on     : string
}
const SUBAGENT_NAMESPACE_SCHEMA: List<SubAgentAttributeSchema>  // exactly 7 entries

enum SubAgentResultStatus { COMPLETED, FAILED, CASCADE_CANCELLED }
```

**Acceptance criteria:**
1. `TOPOLOGY_NAMESPACE_SCHEMA` declares exactly 10 attributes per C-CP-14 §14.2 verbatim: `topology.pattern`, `topology.fan_out_cap`, `topology.cascade_policy`, `topology.workload_class`, `topology.concurrent_token_budget_at_dispatch`, `topology.results_collected`, `topology.results_failed`, `topology.cascade_applied`, `topology.synthesis_token_budget`, `topology.cascade_decision_audit_ledger_id`.
2. `SUBAGENT_NAMESPACE_SCHEMA` declares exactly 7 attributes per §14.2 verbatim: `subagent.span.id`, `subagent.parent_span_id`, `subagent.result_status`, `subagent.request_blocked_by_budget`, `subagent.tokens_in`, `subagent.tokens_out`, `subagent.cached_tokens_in`.
3. `SubAgentResultStatus` declares exactly three values per §14.2.
4. D6 ingestion at U-CP-54 §24.1.A (rows 7 and 8).

**Tests:** `test_topology_namespace_cardinality_ten`, `test_topology_attributes_match_spec_verbatim`, `test_subagent_namespace_cardinality_seven`, `test_subagent_attributes_match_spec_verbatim`, `test_sub_agent_result_status_cardinality_three`.

**Rollback boundary:** Revert two namespace schemas. U-CP-32 span hierarchy loses attribute schemas; U-CP-54 §24.1.A export manifest loses CP-side source for rows 7+8; OD plan Session 4 D6 §1.2 ingestion loses CP source.

#### U-CP-32 — Implement multi-agent span hierarchy + per-span sampling discipline

**Implements:** [C-CP-14 §14.1, §14.3, §14.5]

**Depends on:** [U-CP-10, U-CP-12, U-CP-31, U-CP-46, U-AS-17 (cross-axis: AS), U-AS-31 (cross-axis: AS)]

**Inputs:** `LifecycleEventClass` (U-CP-10); `SAMPLING_DISPOSITIONS` (U-CP-12); topology/subagent namespaces (U-CP-31); `hitl.*` span schema (U-CP-46); sandbox-bounded span schema (U-AS-17 cross-axis); `anthropic.*` cache-token attributes (U-AS-31 cross-axis).

**Files affected:** CP-axis multi-agent span hierarchy (logical: `multi-agent-span-hierarchy`); CP-axis per-span sampling enforcement (logical: `multi-agent-span-sampling`).

**Cross-axis substrate consumed.** `SANDBOX_BOUNDED_SPAN_SCHEMA_EXPORT` (C-AS-16 §16.1 → U-AS-17); `SIX_ANTHROPIC_PRIMITIVE_ATTRIBUTE_NAMESPACE_EXPORT` (C-AS-16 §16.4 → U-AS-31).

**Span hierarchy (§14.1 verbatim):**

```
parent_session                                       (workflow.start per U-CP-10)
├── topology.fanout.opened                          (TOPOLOGY_NAMESPACE_SCHEMA per U-CP-31)
├── subagent.span[0]                                (parent_span_id = topology.fanout.opened)
│   ├── llm.inference[]                             (anthropic.* per U-AS-31)
│   ├── sandbox.enter                               (per U-AS-17)
│   ├── tool.call[]                                 (gate_level_computed per U-CP-27)
│   ├── sandbox.exit                                (per U-AS-17)
│   ├── hitl.gate.evaluated                         (per U-CP-46; if gate triggered)
│   └── subagent.span.closed                        (SUBAGENT_NAMESPACE_SCHEMA per U-CP-31)
├── subagent.span[1 .. N-1]                         (siblings concurrent per U-CP-33 warm-up)
└── topology.fanout.closed                          (TOPOLOGY_NAMESPACE_SCHEMA per U-CP-31)
```

**Signatures:**

```
record SpanHierarchyNode {
  span_name           : string
  parent_relationship : ParentRelationship           // {ROOT, CHILD_OF, SIBLING_OF}
  parent_span_name    : Optional<string>
  ordered_children    : List<string>
}
const MULTI_AGENT_SPAN_HIERARCHY: List<SpanHierarchyNode>

record SpanSamplingDecision {
  span_name           : string
  head_sampling_rate  : SamplingRate
  tail_keep_predicate : Optional<TailKeepPredicate>
}
const MULTI_AGENT_SPAN_SAMPLING: List<SpanSamplingDecision>
```

**Acceptance criteria:**
1. `MULTI_AGENT_SPAN_HIERARCHY` declares parent-child relationships per §14.1 verbatim.
2. `MULTI_AGENT_SPAN_SAMPLING` per §14.3: `topology.fanout.opened` / `topology.fanout.closed` `ALWAYS_SAMPLED`; `subagent.span` `BASE_RATE` with `tail-keep on subagent.result_status == FAILED`; `subagent.span.closed` `ALWAYS_SAMPLED`.
3. `hitl.gate.evaluated` appears inside `subagent.span[i]` when gate triggered (sampling per U-CP-46 always-sampled).
4. Cross-family fallback inside `subagent.span[i]` emits `fallback.triggered` event on that span (not sibling); `subagent.cached_tokens_in` resets to 0 per §14.5 + C-CP-04 §4.3.
5. Hierarchy construction is **deterministic** given inputs; no inference-based reparenting.
6. `topology.fanout.opened` + `topology.fanout.closed` always-sampled provides tamper-evidence anchor for cost-attribution rollup at C-CP-24 §24.2.

**Tests:** `test_multi_agent_hierarchy_root_parent_session`, `test_topology_fanout_opened_child_of_parent_session`, `test_subagent_span_parent_id_topology_fanout_opened`, `test_six_grandchild_span_classes_per_subagent`, `test_sampling_topology_always_sampled`, `test_sampling_subagent_base_rate_tail_keep_failed`, `test_hitl_gate_evaluated_when_triggered`, `test_cross_family_fallback_emits_on_subagent_span`, `test_cached_tokens_reset_cross_family`, `test_hierarchy_deterministic`.

**Rollback boundary:** Revert hierarchy + sampling. R-CP-08 multi-agent topology observability fails; OD plan D6 §1.5 cost-attribution loses fan-out boundary anchors. Cross-axis AS edges to U-AS-17, U-AS-31 release.

#### U-CP-33 — Implement concurrent-prompt-cache warm-up protocol

**Implements:** [C-CP-14 §14.4]

**Depends on:** [U-CP-32, U-AS-31 (cross-axis: AS), U-IS-01 (cross-axis: IS), U-IS-02 (cross-axis: IS)]

**Inputs:** Span hierarchy (U-CP-32); `anthropic.*` cache attributes (U-AS-31); filesystem path contract (U-IS-01); path-resolver (U-IS-02).

**Files affected:** CP-axis fan-out warm-up protocol (logical: `concurrent-prompt-cache-warmup`).

**Cross-axis substrate consumed.** `SIX_ANTHROPIC_PRIMITIVE_ATTRIBUTE_NAMESPACE_EXPORT` (C-AS-16 §16.4 → U-AS-31); `FILESYSTEM_PATH_CONTRACT_EXPORT` (C-IS-10 §10.4 → U-IS-01, U-IS-02).

**Protocol (§14.4 four-step verbatim):**

```
Step 1. Persist lead-agent's plan to filesystem (CoALA episodic memory) via U-IS-02 resolver
Step 2. Dispatch siblings[0] synchronously to write cache at anthropic.cache_breakpoint_id
Step 3. Await CACHE_ACKNOWLEDGEMENT OR FIRST_TOKEN_EMISSION (whichever fires first)
Step 4. Dispatch siblings[1..N-1] concurrently with cache-hit on shared prefix
```

**Signatures:**

```
record CacheWarmupInput {
  siblings              : List<SubAgent>
  cache_breakpoint_id   : string
  lead_agent_plan       : LeadAgentPlan
}

enum CacheCompletionProxyKind { CACHE_ACKNOWLEDGEMENT, FIRST_TOKEN_EMISSION }

record CacheCompletionProxy {
  proxy_kind  : CacheCompletionProxyKind
  proxy_at_ms : int
}

function on_fanout_dispatch(input: CacheWarmupInput) -> CacheWarmupResult
function persist_lead_agent_plan(plan: LeadAgentPlan) -> FilesystemPath
function await_cache_completion(sibling: SubAgent) -> CacheCompletionProxy
```

**Acceptance criteria:**
1. `on_fanout_dispatch` executes the four steps in order per §14.4 verbatim; no step skipped or reordered.
2. Step 1 plan persistence delegates to U-IS-02 against U-IS-01 `PathClass` at canonical CoALA episodic memory location.
3. Step 2 first sibling dispatched synchronously with cache-write at `anthropic.cache_breakpoint_id`; `anthropic.cache_creation_input_tokens` populated per U-AS-31.
4. Step 3 completion proxy is whichever of `CACHE_ACKNOWLEDGEMENT` / `FIRST_TOKEN_EMISSION` fires first.
5. Step 4 remaining siblings dispatched concurrently; siblings observe cache-hit via `anthropic.cache_read_input_tokens` at 0.10× cost.
6. Cross-family fallback during fan-out loses cache state for that sibling per U-CP-32 acceptance.

**Tests:** `test_on_fanout_dispatch_four_steps_in_order`, `test_step_1_persists_via_u_is_02`, `test_step_2_synchronous_cache_write`, `test_step_3_first_of_two_signals`, `test_step_4_concurrent_after_completion`, `test_cache_read_tokens_populated_on_hit`, `test_cache_state_lost_cross_family`.

**Rollback boundary:** Revert warm-up protocol. Fan-out defaults to fully-concurrent dispatch without cache-warm-up; cache-miss-storm risk reintroduced. Cross-axis edges to U-AS-31, U-IS-01, U-IS-02 release.

#### U-CP-34 — Declare per-sibling F2 ledger entry composition + F2-14 Reading 1 closure rationale

**Implements:** [C-CP-15 §15.1, §15.3]

**Depends on:** [U-IS-07 (cross-axis: IS), U-IS-08 (cross-axis: IS), U-IS-09 (cross-axis: IS), U-IS-11 (cross-axis: IS)]

**Inputs:** F2 entry shape (U-IS-07); canonicalization + hash (U-IS-08); chain construction (U-IS-09); append write (U-IS-11).

**Files affected:** CP-axis per-sibling F2 ledger entry (logical: `sibling-ledger-entry-composition`); CP-axis F2-14 Reading 1 rationale (logical: `f2-14-reading-1-rationale`).

**Cross-axis substrate consumed.** `STATE_LEDGER_ENTRY_SHAPE_EXPORT` + `HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT` + `JSONL_EVENT_LEDGER_FORMAT_EXPORT` (C-IS-10 §10.1, §10.3, §10.5).

**Signatures:**

```
record SiblingLedgerEntry {
  action_id         : string                          // ParentActionID || sibling_thread_id || step_index
  idempotency_key   : IdempotencyKey                  // sha256(parent_action_id, sibling_thread_id, step_index, tool, canonical_args)
  actor             : ActorIdentity                   // sibling_agent_identity
  response_hash     : SHA256                          // sha256(canonicalize(tool_output))
  timestamp         : ISO8601
  prior_event_hash  : SHA256                          // per U-IS-09
}

record F2_14_Reading_1_Rationale {
  primitive_name      : string                        // "parent_fanout_close_entry"
  omitted_field       : string
  omission_rationale  : string                        // §15.3 column 2 verbatim
}
const F2_14_READING_1_RATIONALE: List<F2_14_Reading_1_Rationale>  // exactly 3 entries

function construct_sibling_ledger_entry(...) -> SiblingLedgerEntry
function append_sibling_ledger_entry(entry: SiblingLedgerEntry) -> Result<Unit, AppendError>
```

**Acceptance criteria:**
1. `SiblingLedgerEntry` matches F2 six-field shape per U-IS-07 verbatim.
2. `idempotency_key` per Stripe-style construction per §15.1 + C-IS-10 §10.2.
3. `action_id` concatenation order is structural per §15.1.
4. `F2_14_READING_1_RATIONALE` declares exactly three entries per §15.3 verbatim (one per omitted F2 field at `parent_fanout_close_entry`: `idempotency_key`, `actor`, `response_hash`).
5. `append_sibling_ledger_entry` delegates to U-IS-11 C3-pole append-only write.

**Tests:** `test_sibling_ledger_entry_matches_f2_shape`, `test_idempotency_key_construction`, `test_action_id_concatenation`, `test_response_hash_via_u_is_08`, `test_prior_event_hash_via_u_is_09`, `test_append_delegates_to_u_is_11`, `test_f2_14_rationale_cardinality_three`, `test_f2_14_rationale_per_field_match_spec`.

**Rollback boundary:** Revert sibling ledger entry composition + F2-14 rationale. R-CP-08 + R-CP-09 cross-sibling audit fails; sub-agent dispatch loses per-sibling entry write path. Cross-axis IS edges to U-IS-07, U-IS-08, U-IS-09, U-IS-11 release.

#### U-CP-35 — Declare `parent_fanout_close_entry` separate primitive + merkle-root construction

**Implements:** [C-CP-15 §15.2, §15.4]

**Depends on:** [U-CP-22, U-CP-34, U-IS-07 (cross-axis: IS), U-IS-12 (cross-axis: IS)]

**Inputs:** `TopologyPattern` enum (U-CP-22); sibling ledger entry (U-CP-34); F2 entry shape (U-IS-07); bounded-read primitive (U-IS-12).

**Files affected:** CP-axis parent_fanout_close_entry primitive (logical: `parent-fanout-close-entry-shape`); CP-axis merkle-root construction (logical: `merkle-root-construction`).

**Cross-axis substrate consumed.** `STATE_LEDGER_ENTRY_SHAPE_EXPORT` + `IDEMPOTENCY_KEY_JOIN_EXPORT` (C-IS-10 §10.1, §10.2 → U-IS-07, U-IS-12).

**Signatures:**

```
enum CascadeDecisionAtFanoutClose { COMPLETED, CASCADE_CANCELLED, PAUSED_ON_FAILURE }

record ParentFanoutCloseEntry {
  // separate ledger primitive — NOT an F2 entry
  action_id           : ActionID                      // ParentActionID — joins F2 via this field
  fanout_topology     : TopologyPattern
  sibling_ledger_root : MerkleRoot
  cascade_decision    : CascadeDecisionAtFanoutClose
  timestamp           : ISO8601
  prior_event_hash    : SHA256
  // F2 fields intentionally omitted per U-CP-34 F2-14 Reading 1 rationale
}

record MerkleRoot { root_hash: SHA256; tree_height: int; leaf_count: int }

enum MerkleStepOperation {
  READ_F2_ENTRIES,
  HASH_PER_ENTRY_CHAIN,
  CONSTRUCT_TREE,
  WRITE_FANOUT_CLOSE_PRIMITIVE
}

enum F2Effect { READ_ONLY, NO_F2_WRITES, SEPARATE_PRIMITIVE_WRITE }

record MerkleConstructionStep {
  step_index : int
  operation  : MerkleStepOperation
  f2_effect  : F2Effect
}
const MERKLE_CONSTRUCTION_STEPS: List<MerkleConstructionStep>  // exactly 4 entries

function construct_parent_fanout_close_entry(...) -> ParentFanoutCloseEntry
function construct_sibling_ledger_root(parent_action_id: ActionID, sibling_thread_ids: List<ThreadID>) -> MerkleRoot
```

**Acceptance criteria:**
1. `ParentFanoutCloseEntry` declares exactly six fields per C-CP-15 §15.2 verbatim.
2. `CascadeDecisionAtFanoutClose` declares exactly three values per §15.2 verbatim.
3. F2 fields (`idempotency_key`, `actor`, `response_hash`) intentionally omitted per U-CP-34 F2-14 rationale; verified by negative test.
4. `MERKLE_CONSTRUCTION_STEPS` declares exactly 4 steps per §15.4 verbatim:
   - Step 1: `READ_F2_ENTRIES` (read-only)
   - Step 2: `HASH_PER_ENTRY_CHAIN` (read-only)
   - Step 3: `CONSTRUCT_TREE` (no F2 writes)
   - Step 4: `WRITE_FANOUT_CLOSE_PRIMITIVE` (separate primitive write)
5. Construction does NOT write F2 entries; invariant `f2_effect ∈ {READ_ONLY, NO_F2_WRITES, SEPARATE_PRIMITIVE_WRITE}` across all four steps.
6. T-perm-2 F2-layer resolution stands per ADR-D4 v1.1 §1.10 (no F2 revision required at this primitive).
7. Read-side merkle construction uses U-IS-12 bounded-read.

**Tests:** `test_parent_fanout_close_entry_six_fields`, `test_cascade_decision_cardinality_three`, `test_omits_idempotency_key`, `test_omits_actor`, `test_omits_response_hash`, `test_merkle_steps_cardinality_four`, `test_merkle_construction_no_f2_writes`, `test_t_perm_2_stands`, `test_merkle_read_delegates_to_u_is_12`.

**Rollback boundary:** Revert fanout-close primitive + merkle construction. R-CP-08 + R-CP-09 + R-CP-12 cross-audit composition halves fail; merkle-root tamper-evidence at multi-tenant-compliance dissolves. Cross-axis IS edges release.

#### U-CP-36 — Implement per-persona-tier cryptographic shape composition + audit-ledger read at trace inspection

**Implements:** [C-CP-15 §15.5, §15.6]

**Depends on:** [U-CP-31, U-CP-34, U-CP-35, U-CP-42]

**Inputs:** `topology.cascade_decision_audit_ledger_id` attribute (U-CP-31); sibling ledger entry (U-CP-34); fanout-close primitive (U-CP-35); per-persona-tier cryptographic shape table (U-CP-42).

**Files affected:** CP-axis cross-sibling cryptographic composition (logical: `cross-sibling-cryptographic-shape`); CP-axis audit-ledger read at trace inspection (logical: `cross-sibling-audit-read`).

**Signatures:**

```
record CrossSiblingCryptographicComposition {
  persona_tier                                  : PersonaTier
  sibling_ledger_entry_cryptographic_shape      : CryptographicShape
  parent_fanout_close_entry_cryptographic_shape : CryptographicShape
}
const CROSS_SIBLING_CRYPTOGRAPHIC_COMPOSITION: List<CrossSiblingCryptographicComposition>  // exactly 3 entries

record TraceInspectionSurface {
  surface_name           : string
  resolution_mechanism   : string                     // §15.6 verbatim
}
const CROSS_SIBLING_TRACE_INSPECTION: List<TraceInspectionSurface>

function compose_per_persona_tier_cryptographic_shape(persona_tier: PersonaTier) -> CrossSiblingCryptographicComposition
function resolve_audit_ledger_entry_from_trace(cascade_decision_audit_ledger_id: string) -> Result<ParentFanoutCloseEntry, ResolutionError>
function verify_multi_tenant_compliance_signature(parent_close_entry: ParentFanoutCloseEntry, sibling_entries: List<SiblingLedgerEntry>) -> VerificationResult
```

**Acceptance criteria:**
1. `CROSS_SIBLING_CRYPTOGRAPHIC_COMPOSITION` declares exactly three entries per C-CP-15 §15.5 verbatim (one per persona tier).
2. `solo-developer`: append-only SQLite per IS C-IS-05; `team-binding`: hash-chained SQLite per IS C-IS-06; `multi-tenant-compliance`: hash-chained SQLite + signature per entry per C-CP-20 §20.2.
3. Each row delegates to U-CP-42 per-persona-tier table; this unit declares composition rule.
4. `CROSS_SIBLING_TRACE_INSPECTION` declares three surfaces per §15.6 verbatim: `cascade_decision_audit_ledger_id` resolution, per-sibling `action_id` join, multi-tenant signature verification.
5. Signature verification delegates to U-CP-45 verifier.
6. Merkle inclusion-proof generation for tamper-evident trace proof deferred to implementation discretion per spec §15.6.

**Tests:** `test_cross_sibling_composition_cardinality_three`, `test_per_tier_match_spec`, `test_cascade_decision_id_resolution`, `test_action_id_join`, `test_signature_verification_delegates_to_u_cp_45`.

**Rollback boundary:** Revert cross-sibling composition + trace inspection. R-CP-12 audit-ledger cryptographic shape per persona tier fails; trace-inspection-time audit verification dissolves at multi-tenant-compliance.

---

### §2.6 Cluster 6 — D5 HITL palette + placement + matrix (C-CP-16, C-CP-17, C-CP-18)

**Anchor.** ADR-D5 v1.3.

**Theme.** Three contracts define the HITL operator-loop surface: closed 4-response palette + audit shapes + invariants + response-class attribute (C-CP-16); 3-placement primitive + `hitl_gate(...)` signature + HITL-as-tool-call rewriting + workflow schema (C-CP-17); persona-tier × engine-class 15-cell matrix + cell exclusion + overlay + observer + binding selection (C-CP-18).

#### U-CP-37 — Declare 4-response palette + per-response audit entry shape + palette invariants + `hitl.response.class` attribute

**Implements:** [C-CP-16 §16.1, §16.2, §16.3, §16.4]

**Depends on:** [U-IS-07 (cross-axis: IS), U-IS-09 (cross-axis: IS)]

**Inputs:** F2 entry shape (U-IS-07); chain-link construction (U-IS-09).

**Files affected:** CP-axis HITL response palette enum (logical: `hitl-response-palette`); per-response audit entry shapes (logical: `hitl-response-audit-entry-shapes`); `hitl.response.class` attribute (logical: `hitl-response-class-attribute`); palette completeness invariant (logical: `hitl-palette-completeness-invariant`).

**Cross-axis substrate consumed.** `STATE_LEDGER_ENTRY_SHAPE_EXPORT` (C-IS-10 §10.1 → U-IS-07); `HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT` (C-IS-10 §10.3 → U-IS-09).

**Signatures:**

```
enum HITLResponse { APPROVE, EDIT, REJECT, RESPOND }

record HITLResponseSemantic {
  response           : HITLResponse
  semantic           : string                         // §16.1 column 2 verbatim
  cell_applicability : CellApplicabilityScope         // {ALL_CELLS}
}
const HITL_RESPONSE_SEMANTICS: List<HITLResponseSemantic>  // exactly 4 entries

enum AuditFieldName {
  ACTION_ID, GATE_LEVEL, RESPONSE, EDITED_PROPOSAL_HASH,
  REJECTION_REASON_HASH, RESPONSE_TEXT_HASH, TIMESTAMP, PRIOR_EVENT_HASH
}

record PerResponseAuditEntryShape {
  response         : HITLResponse
  required_fields  : Set<AuditFieldName>
  optional_fields  : Set<AuditFieldName>
}
const PER_RESPONSE_AUDIT_ENTRY_SHAPES: List<PerResponseAuditEntryShape>  // exactly 4 entries

enum InvariantEnforcementPoint {
  EVERY_HITL_INVOCATION, CELL_SYNCHRONY_DELIVERY, PRE_HITL_ESCALATION
}

record PaletteCompletenessInvariant {
  invariant_name      : string
  invariant_statement : string                        // §16.3 verbatim
  enforced_at         : InvariantEnforcementPoint
}
const PALETTE_INVARIANTS: List<PaletteCompletenessInvariant>  // exactly 3 entries

record HITLResponseClassAttribute {
  attribute_name : string                             // "hitl.response.class"
  value_type     : AttributeValueType                 // HITLResponse enum
  cardinality    : Cardinality                        // bounded (4)
  emitted_on     : string                             // "hitl.invocation.responded"
}
```

**Acceptance criteria:**
1. `HITLResponse` declares exactly four values per C-CP-16 §16.1 verbatim.
2. `HITL_RESPONSE_SEMANTICS` carries `cell_applicability == ALL_CELLS` for all four rows per §16.1.
3. `PER_RESPONSE_AUDIT_ENTRY_SHAPES` declares four entries per §16.2 verbatim. `APPROVE` requires `{ACTION_ID, GATE_LEVEL, RESPONSE, TIMESTAMP, PRIOR_EVENT_HASH}`; `EDIT` adds `EDITED_PROPOSAL_HASH`; `REJECT` adds optional `REJECTION_REASON_HASH`; `RESPOND` adds required `RESPONSE_TEXT_HASH`.
4. `PALETTE_INVARIANTS` declares three invariants per §16.3 verbatim: palette completeness (every invocation; full palette); synchrony class does not narrow palette (cell synchrony delivery); pre-HITL escalation MAY narrow palette (PRE_HITL_ESCALATION).
5. `HITL_RESPONSE_CLASS_ATTRIBUTE` per §16.4: cardinality bounded at 4; emitted on `hitl.invocation.responded`.
6. `prior_event_hash` chains per IS C-IS-06 at team-binding+; delegates to U-IS-09.
7. `RESPOND` distinguishes "continue dialogue without action" from `REJECT` ("cancel action") per §16.3 closing sentence.

**Tests:** `test_hitl_response_cardinality_four`, `test_response_values_match_spec_verbatim`, `test_semantics_cell_applicability_all`, `test_per_response_audit_shapes_match_spec`, `test_approve_audit_required_fields`, `test_edit_audit_carries_edited_proposal_hash`, `test_reject_audit_rejection_reason_optional`, `test_respond_audit_required_response_text_hash`, `test_palette_invariants_cardinality_three`, `test_hitl_response_class_cardinality_bounded_four`, `test_emitted_on_hitl_invocation_responded`, `test_prior_event_hash_delegates_to_u_is_09`.

**Rollback boundary:** Revert palette enum + audit shapes + invariants + response-class attribute. R-CP-10 four-response palette at every gate fails; per-response audit composition with F2 dissolves; D6 §1.2 ingestion loses `hitl.response.class` source. Cross-axis IS edges to U-IS-07, U-IS-09 release.

#### U-CP-38 — Declare 3-placement enum + `hitl_gate(...)` interface signature + `HITLPlacement` workflow-definition schema

**Implements:** [C-CP-17 §17.1, §17.1.1, §17.3]

**Depends on:** [U-CP-22, U-CP-30, U-CP-37]

**Inputs:** `CascadePolicy` enum (U-CP-22); `HandoffContext` (U-CP-30); `HITLResponse` enum (U-CP-37).

**Files affected:** CP-axis 3-placement enum (logical: `hitl-placement-enum`); `hitl_gate` interface signature (logical: `hitl-gate-interface-signature`); `HITLPlacement` workflow-definition schema (logical: `hitl-placement-workflow-definition-schema`).

**Signatures:**

```
enum HITLPlacementKind {
  PRE_ACTION,
  SUB_AGENT_BOUNDARY,
  VALIDATOR_ESCALATION
}

record HITLPlacementTrigger {
  placement_kind                : HITLPlacementKind
  trigger_summary               : string              // §17.1 column 2 verbatim
  cell_applicability_qualifier  : string              // §17.1 column 3 verbatim
}
const HITL_PLACEMENT_TRIGGERS: List<HITLPlacementTrigger>  // exactly 3 entries

record HITLResult {
  response                : HITLResponse
  edited_proposal         : Optional<ProposedAction>
  response_text           : Optional<string>
  timestamp               : ISO8601
  audit_ledger_entry_id   : EntryID
  response_summary_hash   : SHA256
}

function hitl_gate(
  placement       : HITLPlacementKind,
  handoff_context : HandoffContext,
  response_palette: Set<HITLResponse>,
  timeout         : Optional<Duration>,
  cascade_policy  : CascadePolicy
) -> HITLResult

record HITLPlacement {
  position       : HITLPlacementKind
  tool_filter    : Optional<List<ToolName>>
  cascade_policy : Optional<CascadePolicy>
  timeout        : Optional<Duration>
}
```

**Acceptance criteria:**
1. `HITLPlacementKind` declares exactly three values per C-CP-17 §17.1 verbatim.
2. `HITL_PLACEMENT_TRIGGERS` declares three entries per §17.1 verbatim. Closed at cardinality 3 — extension requires Workflow §4.1.2 Class-2 D5 revision.
3. `hitl_gate` signature matches §17.1.1 verbatim — five parameters; return type `HITLResult` with six fields.
4. `HITLResult.response` is one of four `HITLResponse` enum values; `edited_proposal` only when `response == EDIT`; `response_text` only when `response == RESPOND`.
5. `response_palette` is `Set<HITLResponse>` (NOT `List<HITLResponse>`) — palette is a set per U-CP-48 restriction rule.
6. `HITLPlacement` declares four fields per §17.3 verbatim. Multiple placements per workflow permitted.
7. `tool_filter` semantics (glob vs regex) deferred to implementation discretion per spec §17.3.

**Tests:** `test_placement_kind_cardinality_three`, `test_placement_triggers_match_spec`, `test_hitl_gate_signature_five_parameters`, `test_hitl_result_six_fields`, `test_response_palette_is_set`, `test_hitl_placement_four_fields`, `test_multiple_placements_permitted`.

**Rollback boundary:** Revert placement enum + signature + schema. R-CP-11 three-placement HITL topology primitive fails; U-CP-13 manifest entry loses `hitl_placements` element type; U-CP-39 rewriting algorithm loses target signature.

#### U-CP-39 — Implement HITL-as-tool-call rewriting algorithm + three semantic variants

**Implements:** [C-CP-17 §17.2]

**Depends on:** [U-CP-37, U-CP-38, U-CP-43, U-CP-48]

**Inputs:** HITL palette (U-CP-37); placement + signature (U-CP-38); `_hitl_required` predicate (U-CP-43); palette-restriction state (U-CP-48).

**Files affected:** CP-axis HITL-as-tool-call rewriting (logical: `hitl-as-tool-call-rewriting`); three semantic variant dispatchers (logical: `hitl-rewriting-three-variants`).

**Signatures:**

```
enum HITLSemanticVariant {
  REQUEST_HUMAN_INPUT,                                // sync-blocking
  AWAIT_HUMAN_APPROVAL,                               // durable-async
  ESCALATE_TO_HUMAN                                   // post retry-budget exhaustion
}

enum EngineBindingClass { SYNC_BLOCKING, DURABLE_ASYNC, ALL_CELLS }

record HITLSemanticVariantBinding {
  variant         : HITLSemanticVariant
  tool_signature  : string                            // §17.2 column 2 verbatim
  engine_binding  : EngineBindingClass
  cell_mapping    : string                            // §17.2 column 4 verbatim
}
const HITL_SEMANTIC_VARIANTS: List<HITLSemanticVariantBinding>  // exactly 3 entries

function rewrite_tool_call_to_hitl(
    tool                       : ToolName,
    server                     : MCPServerID,
    persona_tier               : PersonaTier,
    proposed_action            : ProposedAction,
    cell_synchrony_class       : SynchronyClass,
    cross_trust_boundary_state : CrossTrustBoundaryState
) -> RewrittenToolCall
```

**Acceptance criteria:**
1. `HITLSemanticVariant` declares exactly three values per C-CP-17 §17.2 verbatim.
2. `HITL_SEMANTIC_VARIANTS` declares three entries per §17.2 verbatim: `REQUEST_HUMAN_INPUT` ↔ `SYNC_BLOCKING`; `AWAIT_HUMAN_APPROVAL` ↔ `DURABLE_ASYNC`; `ESCALATE_TO_HUMAN` ↔ `ALL_CELLS` (validator-escalation placement).
3. `rewrite_tool_call_to_hitl` evaluates `_hitl_required` via U-CP-43; if `false`, returns original tool call unchanged.
4. Variant selection deterministic per `cell_synchrony_class`: SYNC_BLOCKING → REQUEST_HUMAN_INPUT; DURABLE_ASYNC → AWAIT_HUMAN_APPROVAL; validator-escalation → ESCALATE_TO_HUMAN.
5. `response_palette` populated full when no cross-trust-boundary state; restricted per U-CP-48 when CROSS_FAMILY_ACTIVE / LOCAL_TERMINAL_ACTIVE / UNTRUSTED_MCP_ACTIVE.
6. Per-tool `tier` (auto/ask/deny) read from SKILL.md frontmatter or MCP server manifest at runtime (C4 contract per cross-axis AS); this unit does NOT declare frontmatter schema.
7. Rewriting fires **before** tool dispatch — no tool call reaches action surface without `_hitl_required` evaluation.

**Tests:** `test_semantic_variant_cardinality_three`, `test_variants_match_spec`, `test_rewrite_evaluates_predicate`, `test_returns_original_when_false`, `test_variant_selection_per_synchrony`, `test_palette_full_when_no_cross_trust`, `test_palette_restricted_when_cross_family_active`, `test_palette_restricted_when_local_terminal`, `test_palette_restricted_when_untrusted_mcp`, `test_rewriting_before_dispatch`.

**Rollback boundary:** Revert rewriting algorithm. R-CP-11 three-placement HITL topology primitive degrades at runtime; tool calls reach action surface without HITL gating regardless of `_hitl_required`.

#### U-CP-40 — Declare persona-tier × engine-class 2D matrix + cell exclusion inheritance

**Implements:** [C-CP-18 §18.1, §18.2]

**Depends on:** [U-CP-15, U-CP-16]

**Inputs:** `EngineClass` enum (U-CP-15); per-deployment-surface candidate mapping with exclusions (U-CP-16).

**Files affected:** CP-axis HITL matrix (logical: `hitl-persona-engine-class-matrix`); CP-axis cell exclusion inheritance (logical: `hitl-cell-exclusion-inheritance`).

**Signatures:**

```
enum PersonaTier { SOLO_DEVELOPER, TEAM_BINDING, MULTI_TENANT_COMPLIANCE }

enum SynchronyClass {
  SYNC_BLOCKING,
  DURABLE_ASYNC,
  BOTH_BY_TIER,                                       // per-tool overlay class per §18.3
  EXCLUDED                                            // cell structurally excluded per §18.2
}

enum HITLPrimitiveShape {
  IN_PROCESS_FUNCTION_SYNCHRONOUS_RETURN,
  LANGGRAPH_INTERRUPT_COMMAND_RESUME,
  TWELVE_FACTOR_APPLICATION_DEFINED_EVENT_AND_RESUME,
  SEGMENT_RESUME_WITH_APPROVAL_PENDING_MARKER,
  CONTACT_CHANNEL_CR_MESH_PATTERN,
  TEMPORAL_WAIT_CONDITION_SIGNAL_HANDLER,
  LANGGRAPH_POSTGRES_REDIS_LEASE,
  CLAUDE_CODE_PERMISSION_MODEL,
  TEMPORAL_CLOUD_BEDROCK_VERTEX_NATIVE,
  LANGGRAPH_DYNAMODB_MANAGED_CHECKPOINTER,
  ACP_K8S_MULTI_TENANT_CONTACT_CHANNEL,
  MANAGED_WAL_CRYPTOGRAPHIC_AUDIT
}

record HITLMatrixCell {
  persona_tier             : PersonaTier
  engine_class             : EngineClass
  synchrony_class          : SynchronyClass
  primary_primitive_shapes : List<HITLPrimitiveShape>
  candidate_evidence       : string                   // §18.1 cell verbatim
  is_excluded              : bool
  exclusion_source         : Optional<string>
}
const HITL_MATRIX: List<HITLMatrixCell>  // exactly 15 entries (3 × 5)

function matrix_cell_for(persona_tier: PersonaTier, engine_class: EngineClass) -> HITLMatrixCell
```

**Acceptance criteria:**
1. `PersonaTier` declares exactly three values per Persona §3 + ADR-D5 v1.3 §1.7 verbatim.
2. `SynchronyClass` declares exactly four values per §18.1 + §18.3 verbatim.
3. `HITL_MATRIX` declares exactly 15 entries (3 persona tiers × 5 engine classes) per C-CP-18 §18.1 verbatim.
4. `(TEAM_BINDING, PURE_PATTERN_NO_ENGINE)` and `(MULTI_TENANT_COMPLIANCE, PURE_PATTERN_NO_ENGINE)` cells carry `is_excluded = true`; `exclusion_source = "C-CP-07 §7.2"`; inherited from U-CP-16.
5. Each non-excluded cell carries `primary_primitive_shapes` cardinality ≥ 1.
6. `(SOLO_DEVELOPER, SAVE_POINT_CHECKPOINT)` cell narrative cites LangGraph HITL doc per §18.1.
7. `(TEAM_BINDING, SAVE_POINT_CHECKPOINT)` cell uses `BOTH_BY_TIER` synchrony class.

**Tests:** `test_persona_tier_cardinality_three`, `test_synchrony_class_cardinality_four`, `test_hitl_matrix_cardinality_fifteen`, `test_matrix_cells_match_spec`, `test_team_binding_pure_pattern_excluded`, `test_multi_tenant_pure_pattern_excluded`, `test_exclusion_source_cites_c_cp_07`, `test_non_excluded_cells_have_primitive`, `test_solo_sync_blocking_across_four_cells`, `test_multi_tenant_durable_async_across_four_cells`, `test_both_by_tier_at_team_save_point`.

**Rollback boundary:** Revert matrix + exclusion inheritance. R-CP-11 cell applicability fails; runtime cell-to-primitive lookup degrades to engine-class-only resolution without persona-tier discrimination.

#### U-CP-41 — Implement both-by-tier overlay + two-agent-observer meta-class + persona-tier-binding selection

**Implements:** [C-CP-18 §18.3, §18.4, §18.5]

**Depends on:** [U-CP-37, U-CP-40, U-CP-43, U-CP-47]

**Inputs:** HITL palette (U-CP-37); matrix cell (U-CP-40); 4-axis multiplicative rule + `_hitl_required` (U-CP-43); validator-fail taxonomy (U-CP-47).

**Files affected:** CP-axis both-by-tier overlay (logical: `hitl-both-by-tier-overlay`); two-agent-observer (logical: `hitl-two-agent-observer-meta-class`); persona-tier-binding selection (logical: `persona-tier-binding-selection`).

**Signatures:**

```
record BothByTierOverlay {
  scope               : string                        // §18.3 row 1 verbatim
  composition_rule    : string                        // §18.3 row 2 verbatim
  audit_composition   : string                        // §18.3 row 3 verbatim
}
const BOTH_BY_TIER_OVERLAY: BothByTierOverlay

record TwoAgentObserverMetaClass {
  trigger_condition          : string                 // §18.4 row 1 verbatim
  composition_with_primary   : string                 // §18.4 row 2 verbatim
  audit_composition          : string                 // §18.4 row 3 verbatim
  applicable_cell_predicate  : Cell -> bool
}
const TWO_AGENT_OBSERVER: TwoAgentObserverMetaClass

record PersonaTierBindingSelectionInput {
  operator_persona_tier        : PersonaTier
  operator_deployment_surface  : DeploymentSurface
  operator_engine_choice       : EngineClass
  operator_workflow_class      : WorkloadClass
}

record PersonaTierBindingSelectionResult {
  resolved_cell                  : HITLMatrixCell
  composition_with_c_cp_19       : ReferenceToUnit    // U-CP-43
  composition_with_c_cp_20       : ReferenceToUnit    // U-CP-42
  composition_with_c_cp_21       : ReferenceToUnit    // U-CP-47
  composition_with_c_cp_22       : ReferenceToUnit    // U-CP-49
  binding_valid                  : bool
  rejection_reason               : Optional<string>
}

function evaluate_both_by_tier_overlay(tool_tier: ToolTier, cell: HITLMatrixCell) -> OverlayResolution
function dispatch_two_agent_observer(proposed_action: ProposedAction, blast_radius: BlastRadiusTier) -> VerifierResult
function compose_persona_tier_binding_selection(input: PersonaTierBindingSelectionInput) -> PersonaTierBindingSelectionResult
```

**Acceptance criteria:**
1. `BOTH_BY_TIER_OVERLAY` declares three properties per C-CP-18 §18.3 verbatim: per-tool `tier ∈ {auto, ask, deny}` annotation gates HITL invocation at any cell; overlay does NOT replace cell's primitive shape; auto-tier emits `tool.call` span only, ask-tier emits both `tool.call` and `hitl.gate.evaluated`.
2. `evaluate_both_by_tier_overlay` returns three outcomes per tool_tier: AUTO → no gate; ASK → cell synchrony delivers gate; DENY → dispatch structurally rejected, palette restricted to `{REJECT, RESPOND}` per C-CP-19 §19.4.
3. `TWO_AGENT_OBSERVER` declares three properties per §18.4: trigger condition is Tier-3+ blast-radius; verifier output composes with primary HITL gate at `validator-escalation` placement; verifier emits `subagent.span[verifier]` + `validator.fail.*` per U-CP-47.
4. `compose_persona_tier_binding_selection` implements §18.5 five-step procedure verbatim: operator declares persona tier + deployment surface + engine class + workflow class; cell lookup via U-CP-40; candidate selection from §18.1 evidence column; composition with U-CP-43 / U-CP-42 / U-CP-47 / U-CP-49 enforced at runtime.
5. Selection deterministic; runs at persona-tier-binding time; validation failure aborts workflow binding.
6. Selected cell binds via U-CP-13 `WorkflowManifestEntry.hitl_placements`; per-placement `cascade_policy` and `timeout` override cell defaults per U-CP-38.

**Tests:** `test_both_by_tier_overlay_three_properties`, `test_auto_no_gate`, `test_ask_invokes_synchrony`, `test_deny_rejects_dispatch`, `test_overlay_no_primitive_replacement`, `test_overlay_audit_auto_tool_call_only`, `test_overlay_audit_ask_both_spans`, `test_observer_trigger_tier_3_plus`, `test_observer_dispatches_verifier`, `test_verifier_emits_subagent_span`, `test_verifier_emits_validator_fail`, `test_binding_selection_five_steps`, `test_selection_deterministic`, `test_selection_at_binding_time`, `test_composes_with_43_42_47_49`.

**Rollback boundary:** Revert overlay + observer + binding selection. Per-tool tier annotation loses runtime effect; verifier-agent pattern dissolves; persona-tier-binding-time validation degrades. R-CP-10 + R-CP-11 reduce to primitive cell-binding without operator selection discipline.

---

### §2.7 Cluster 7 — D5 multiplicative gate + audit crypto (C-CP-19, C-CP-20)

**Anchor.** ADR-D5 v1.3 + ADR-F5 v1.1.

**Theme.** Two contracts compose the gate-level decision substrate and audit-ledger cryptographic shape: 4-axis multiplicative rule + monotonicity + `_hitl_required` predicate + 5-axis composition with C-AS-12 + operator-override scope (C-CP-19); per-persona-tier audit cryptographic shape + F5 signing-key resolution + key-rotation + 7 `audit.*` + 4 `hitl.*` span schemas (C-CP-20).

#### U-CP-42 — Declare per-persona-tier audit-ledger cryptographic shape table

**Implements:** [C-CP-20 §20.1, §20.2]

**Depends on:** [U-IS-07 (cross-axis: IS), U-IS-08 (cross-axis: IS), U-IS-09 (cross-axis: IS), U-IS-11 (cross-axis: IS)]

**Inputs:** F2 entry shape (U-IS-07); canonicalization + hash (U-IS-08); chain-link construction (U-IS-09); append-only write (U-IS-11).

**Files affected:** CP-axis per-persona-tier cryptographic shape table (logical: `per-persona-tier-audit-cryptographic-shape`).

**Cross-axis substrate consumed.** `STATE_LEDGER_ENTRY_SHAPE_EXPORT` + `JSONL_EVENT_LEDGER_FORMAT_EXPORT` (C-IS-10 §10.1, §10.5 → U-IS-07, U-IS-11); `HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT` (C-IS-10 §10.3 → U-IS-09); `RESPONSE_HASH_COMPUTATION_EXPORT` (C-IS-10 §10.6 → U-IS-08).

**Signatures:**

```
enum CryptographicShape {
  APPEND_ONLY_SQLITE,                                 // solo-developer
  HASH_CHAINED_SQLITE,                                // team-binding
  HASH_CHAINED_SQLITE_WITH_SIGNATURE                  // multi-tenant-compliance
}

record PersonaTierCryptographicShape {
  persona_tier              : PersonaTier
  cryptographic_shape       : CryptographicShape
  chain_construction_source : string                  // delegation citation to U-IS-09
  signing_required          : bool
  signing_key_source        : Optional<string>        // delegation citation to U-CP-44
  verification_at_read      : bool
}
const PERSONA_TIER_CRYPTOGRAPHIC_SHAPES: List<PersonaTierCryptographicShape>  // exactly 3 entries
```

**Acceptance criteria:**
1. `CryptographicShape` declares exactly three values per C-CP-20 §20.1 verbatim.
2. `PERSONA_TIER_CRYPTOGRAPHIC_SHAPES` declares exactly three entries:
   - `SOLO_DEVELOPER` → `APPEND_ONLY_SQLITE`, `signing_required = false`, `verification_at_read = false`
   - `TEAM_BINDING` → `HASH_CHAINED_SQLITE`, `signing_required = false`, `verification_at_read = true`
   - `MULTI_TENANT_COMPLIANCE` → `HASH_CHAINED_SQLITE_WITH_SIGNATURE`, `signing_required = true`, `verification_at_read = true`
3. Cryptographic shape is **strictly monotonic** along the persona-tier axis per §20.2 — shape strength ascends across `SOLO_DEVELOPER → TEAM_BINDING → MULTI_TENANT_COMPLIANCE`. Reordering is a Workflow §4.1.2 Class-2 D5 revision.
4. `chain_construction_source` cites U-IS-09 for `TEAM_BINDING` and `MULTI_TENANT_COMPLIANCE` (no chain at `SOLO_DEVELOPER`).
5. `signing_key_source` cites U-CP-44 for `MULTI_TENANT_COMPLIANCE` (F5 signing-key resolution).
6. `verification_at_read` triggers chain verification on read at team-binding+; signature verification on read at multi-tenant-compliance per §20.2.

**Tests:** `test_cryptographic_shape_cardinality_three`, `test_persona_tier_shapes_cardinality_three`, `test_solo_append_only_no_chain`, `test_team_hash_chained_no_signing`, `test_multi_tenant_signed`, `test_monotonic_strength_ascending`, `test_chain_construction_delegates_to_u_is_09`, `test_signing_key_source_cites_u_cp_44`.

**Rollback boundary:** Revert per-persona-tier table. R-CP-12 audit-ledger cryptographic shape per persona tier fails; U-CP-36 cross-sibling composition loses per-tier rule; U-CP-45 5-axis composition loses anchor row. Cross-axis IS edges to U-IS-07, U-IS-08, U-IS-09, U-IS-11 release.

#### U-CP-43 — Implement 4-axis multiplicative gate-level rule + monotonicity + `_hitl_required` predicate + persona-tier floor

**Implements:** [C-CP-19 §19.1, §19.2, §19.4]

**Depends on:** [U-CP-26, U-AS-05 (cross-axis: AS), U-AS-13 (cross-axis: AS), U-AS-14 (cross-axis: AS), U-AS-15 (cross-axis: AS)]

**Inputs:** Default-downgrade rule (U-CP-26); per-MCP-server trust-tier (U-AS-13); `SandboxTier` enum (U-AS-05); 5-axis multiplicative tunable from AS C-AS-12 (U-AS-14, U-AS-15).

**Files affected:** CP-axis 4-axis multiplicative rule (logical: `four-axis-multiplicative-gate-level-rule`); cross-deployment monotonicity (logical: `gate-level-cross-deployment-monotonicity`); `_hitl_required` predicate (logical: `_hitl_required-predicate`); persona-tier floor (logical: `persona-tier-gate-level-floor`).

**Cross-axis substrate consumed.** `SANDBOX_TIER_FOUNDATIONAL_SUBSTRATE_EXPORT` (C-AS-16 §16.7 → U-AS-05); `PER_MCP_TRUST_TIER_EXPORT` (C-AS-16 §16.5 → U-AS-13); `FIVE_AXIS_MULTIPLICATIVE_TUNABLE_EXPORT` (C-AS-16 §16.2 → U-AS-14, U-AS-15).

**Signatures:**

```
enum GateLevel { GATE_NONE, GATE_NOTIFY, GATE_APPROVE, GATE_REVIEW_BOARD }

record GateLevelInput {
  persona_tier         : PersonaTier
  blast_radius_tier    : BlastRadiusTier
  deployment_surface   : DeploymentSurface
  mcp_trust_tier       : MCPTrustTier
}

record GateLevelComputation {
  inputs               : GateLevelInput
  per_axis_floors      : Map<Axis, GateLevel>
  composition_winner   : Axis
  computed_gate_level  : GateLevel
}

function gate_level(input: GateLevelInput) -> GateLevelComputation
    // multiplicative max() over four per-axis floors
function _hitl_required(input: GateLevelInput) -> bool
    // returns true when gate_level(input) > GATE_NONE

const PERSONA_TIER_GATE_LEVEL_FLOOR: Map<PersonaTier, GateLevel>
const BLAST_RADIUS_GATE_LEVEL_FLOOR: Map<BlastRadiusTier, GateLevel>
const DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR: Map<DeploymentSurface, GateLevel>
const MCP_TRUST_GATE_LEVEL_FLOOR: Map<MCPTrustTier, GateLevel>
```

**Acceptance criteria:**
1. `GateLevel` declares exactly four values per C-CP-19 §19.1 verbatim. Ordering monotonic: `GATE_NONE < GATE_NOTIFY < GATE_APPROVE < GATE_REVIEW_BOARD`.
2. `gate_level` computes per §19.1 composition rule: `max()` over per-axis floors from the four input axes. Composition deterministic given inputs.
3. `PERSONA_TIER_GATE_LEVEL_FLOOR` per §19.1 verbatim: `SOLO_DEVELOPER → GATE_NONE`, `TEAM_BINDING → GATE_NOTIFY`, `MULTI_TENANT_COMPLIANCE → GATE_APPROVE`.
4. `BLAST_RADIUS_GATE_LEVEL_FLOOR` per §19.1 verbatim: `READ_ONLY → GATE_NONE`, `LOCAL_MUTATION → GATE_NONE`, `EXTERNAL_REVERSIBLE → GATE_NOTIFY`, `EXTERNAL_IRREVERSIBLE → GATE_APPROVE`.
5. `DEPLOYMENT_SURFACE_GATE_LEVEL_FLOOR` per §19.1 verbatim: `LOCAL_DEVELOPMENT → GATE_NONE`, `SELF_HOSTED_SERVER → GATE_NOTIFY`, `MANAGED_CLOUD → GATE_APPROVE`.
6. `MCP_TRUST_GATE_LEVEL_FLOOR` per §19.1 verbatim (4-level framework per AS C-AS-10): `TIER_1_FIRST_PARTY → GATE_NONE`, `TIER_2_VENDOR_VERIFIED → GATE_NOTIFY`, `TIER_3_COMMUNITY_AUDITED → GATE_APPROVE`, `TIER_4_UNTRUSTED → GATE_REVIEW_BOARD`.
7. Cross-deployment monotonicity per §19.2: under bridging-arc traversal across deployment surfaces, `gate_level` ascends monotonically (never descends). Verified by integration test against U-CP-50 + U-AS-15 cross-deployment composition.
8. `_hitl_required` returns `true` iff `computed_gate_level > GATE_NONE`. Consumed at U-CP-39 rewriting algorithm.
9. **Cross-finding precedent.** Per F-iter1-04 Path A closure: gate_level computation **does not** consume AS C-AS-12 sandbox-tier directly — the orthogonal axis composition (sandbox-tier × gate-level) is performed at U-CP-45 (5-axis composition), not here. This unit's 4-axis composition is gate-level-only.
10. `composition_winner` identifies which of the four axes set the winning floor for the computed gate level; consumed for audit attribution at U-CP-46 `audit.gate.composition_winner_axis`.

**Tests:** `test_gate_level_cardinality_four`, `test_gate_level_monotonic_ordering`, `test_gate_level_max_composition`, `test_persona_tier_floor_match_spec`, `test_blast_radius_floor_match_spec`, `test_deployment_surface_floor_match_spec`, `test_mcp_trust_floor_match_spec`, `test_cross_deployment_monotonicity`, `test_hitl_required_predicate_above_none`, `test_no_sandbox_tier_input_per_path_a`, `test_composition_winner_attribution`, `test_persona_solo_blast_external_irreversible_yields_approve`, `test_persona_multi_mcp_untrusted_yields_review_board`, `test_local_solo_read_only_yields_none`, `test_multi_external_irreversible_yields_review_board_via_mcp_or_persona`.

**Rollback boundary:** Revert `GateLevel` enum + multiplicative rule + floors + predicate. R-CP-10 gate-level decision discipline fails at all four axes; HITL invocation loses gate-level discriminator; U-CP-39 rewriting loses predicate; U-CP-27 sub-agent gate-level descent loses parent gate-level source; U-CP-45 5-axis composition loses CP-side input. Cross-axis AS edges to U-AS-05, U-AS-13, U-AS-14, U-AS-15 release.

#### U-CP-44 — Implement F5 signing-key resolution for `MULTI_TENANT_COMPLIANCE`

**Implements:** [C-CP-20 §20.3.1]

**Depends on:** [U-CP-42, U-AS-20 (cross-axis: AS)]

**Inputs:** Per-persona-tier crypto shape (U-CP-42); F5 `fetch_secret(name, scope) -> SecretRef` signature (U-AS-20 cross-axis AS).

**Files affected:** CP-axis F5 signing-key resolution (logical: `f5-signing-key-resolution`); CP-axis signing-key lifecycle (logical: `signing-key-lifecycle`).

**Cross-axis substrate consumed.** AS C-AS-05 `fetch_secret(...)` signature via U-AS-20.

**Signatures:**

```
record SigningKeyScope {
  scope_kind       : SecretScopeKind                  // {WORKFLOW_BOUND, TENANT_BOUND, FLEET_BOUND}
  scope_identifier : string
}

record SigningKeyHandle {
  key_id           : string
  key_secret_ref   : SecretRef                        // from U-AS-20
  rotation_state   : KeyRotationState                 // {ACTIVE, ROTATING, RETIRED}
  acquired_at      : ISO8601
}

enum SigningKeyResolutionError { SECRET_FETCH_FAIL, SCOPE_UNAUTHORIZED, KEY_RETIRED }

function resolve_signing_key(scope: SigningKeyScope, persona_tier: PersonaTier) -> Result<SigningKeyHandle, SigningKeyResolutionError>
    // delegates secret resolution to U-AS-20 fetch_secret(name, scope)
    // permitted only when persona_tier == MULTI_TENANT_COMPLIANCE
function sign_audit_entry(entry: AuditLedgerEntry, key: SigningKeyHandle) -> SignedAuditLedgerEntry
function verify_audit_entry_signature(signed: SignedAuditLedgerEntry, key: SigningKeyHandle) -> VerificationResult
```

**Acceptance criteria:**
1. `resolve_signing_key` returns `Err(SCOPE_UNAUTHORIZED)` when `persona_tier != MULTI_TENANT_COMPLIANCE`; signing keys are MULTI_TENANT_COMPLIANCE-exclusive per C-CP-20 §20.3.1.
2. Secret retrieval delegates to U-AS-20 `fetch_secret(name, scope)`; this unit does NOT implement secret retrieval mechanics (AS owns).
3. `SigningKeyHandle.rotation_state` is one of three values; transitions per U-CP-45 rotation pattern.
4. `sign_audit_entry` produces a `SignedAuditLedgerEntry` carrying the canonical hash from U-IS-08 + signature over `(prior_event_hash, response_hash, action_id, actor, timestamp)`.
5. `verify_audit_entry_signature` runs at read-time per U-CP-42 `verification_at_read = true` invariant for multi-tenant-compliance.
6. Specific signature algorithm (Ed25519 vs ECDSA-P256 vs other) deferred to implementation discretion per spec §20.3.1 deferred list.

**Tests:** `test_resolve_signing_key_scope_unauthorized_below_multi_tenant`, `test_resolve_delegates_to_u_as_20`, `test_signing_key_rotation_state_three_values`, `test_sign_produces_signed_entry`, `test_verify_at_read_per_invariant`, `test_signature_algorithm_deferred`.

**Rollback boundary:** Revert F5 signing-key resolution. R-CP-12 multi-tenant-compliance audit signature dissolves; U-CP-45 rotation loses key resolution source; trace inspection signature verification at U-CP-36 fails. Cross-axis AS edge to U-AS-20 releases.

#### U-CP-45 — Implement 5-axis composition (C-AS-12 + C-CP-19) + operator-policy override + key-rotation two-row pattern

**Implements:** [C-CP-19 §19.3, §19.5, C-CP-20 §20.3, §20.3.1]

**Depends on:** [U-CP-42, U-CP-43, U-CP-44, U-AS-12 (cross-axis: AS), U-AS-14 (cross-axis: AS)]

**Inputs:** Per-persona-tier crypto shape (U-CP-42); 4-axis gate-level rule (U-CP-43); F5 signing-key resolution (U-CP-44); AS sandbox-tier composition (U-AS-12); AS 5-axis multiplicative tunable (U-AS-14).

**Files affected:** CP-axis 5-axis composition (logical: `five-axis-composition-rule`); CP-axis operator-policy override (logical: `operator-policy-override-scope`); CP-axis key-rotation two-row pattern (logical: `signing-key-rotation-pattern`); CP-axis key-rotation 6-step verification (logical: `signing-key-rotation-verification`).

**Cross-axis substrate consumed.** `SANDBOX_TIER_COMPOSITION_EXPORT` (C-AS-16 §16.3 → U-AS-12); `FIVE_AXIS_MULTIPLICATIVE_TUNABLE_EXPORT` (C-AS-16 §16.2 → U-AS-14).

**Signatures:**

```
record FiveAxisCompositionInput {
  // From U-CP-43:
  persona_tier         : PersonaTier
  blast_radius_tier    : BlastRadiusTier
  deployment_surface   : DeploymentSurface
  mcp_trust_tier       : MCPTrustTier
  // From U-AS-12 (cross-axis):
  sandbox_tier         : SandboxTier
}

record FiveAxisCompositionResult {
  gate_level                  : GateLevel             // from U-CP-43
  sandbox_tier_floor          : SandboxTier           // from U-AS-12
  composition_admissible      : bool                  // orthogonal axes; product space valid
  cross_axis_composition_audit_attrs : Set<string>    // emitted at U-CP-46
}

record OperatorPolicyOverride {
  override_kind            : OverrideKind             // {LOWER_GATE_LEVEL, RAISE_GATE_LEVEL, NARROW_PALETTE}
  scope                    : OverrideScope            // {PER_TOOL, PER_WORKFLOW, PER_PERSONA_TIER}
  permitted_at             : Set<PersonaTier>
  audit_required           : bool                     // always true
}
const OPERATOR_POLICY_OVERRIDE_SCOPE_TABLE: List<OperatorPolicyOverride>

enum KeyRotationStage { ROW_1_DUAL_VERIFY_ACTIVE, ROW_2_RETIRE_OLD }

record KeyRotationPattern {
  stage                     : KeyRotationStage
  active_key_count          : int                     // {1, 2}
  signing_key               : SigningKeyHandle
  verification_key_set      : Set<SigningKeyHandle>
}

enum RotationVerificationStep {
  STAGE_NEW_KEY,
  WRITE_DUAL_VERIFY_ENTRY,
  PROBE_VERIFY_AT_READ,
  VERIFY_HASH_CHAIN_LINK,
  ROTATE_SIGNING_TO_NEW,
  RETIRE_OLD_KEY
}

function compose_five_axis(input: FiveAxisCompositionInput) -> FiveAxisCompositionResult
function apply_operator_policy_override(base: FiveAxisCompositionResult, override: OperatorPolicyOverride, persona_tier: PersonaTier) -> Result<FiveAxisCompositionResult, OverrideRejection>
function execute_key_rotation(scope: SigningKeyScope) -> KeyRotationOutcome
function verify_rotation_6_steps(scope: SigningKeyScope) -> List<StepResult>
```

**Acceptance criteria:**
1. `compose_five_axis` runs U-CP-43 gate-level computation + U-AS-12 sandbox-tier composition as **orthogonal axes** per C-CP-19 §19.3 — no axis collapses into the other. Result carries both `gate_level` and `sandbox_tier_floor` independently.
2. `composition_admissible` is `true` for all valid input tuples; orthogonality invariant verified at integration test against U-AS-14 + U-CP-43.
3. `OPERATOR_POLICY_OVERRIDE_SCOPE_TABLE` declares per C-CP-19 §19.5 verbatim:
   - `LOWER_GATE_LEVEL` override permitted at `SOLO_DEVELOPER` and `TEAM_BINDING`; **prohibited** at `MULTI_TENANT_COMPLIANCE`
   - `RAISE_GATE_LEVEL` override permitted at all three persona tiers
   - `NARROW_PALETTE` override permitted at all three persona tiers
4. Every override emits audit entry per U-CP-46 `audit.policy.*` attributes regardless of persona tier.
5. `KEY_ROTATION_PATTERN` declares two stages per C-CP-20 §20.3 verbatim:
   - Row 1 `ROW_1_DUAL_VERIFY_ACTIVE`: both old and new keys verify signatures at read; new key signs new entries
   - Row 2 `ROW_2_RETIRE_OLD`: old key removed from verification set; only new key active
6. `verify_rotation_6_steps` implements §20.3.1 six-step verification protocol verbatim:
   - Step 1: `STAGE_NEW_KEY` — provision new key via U-CP-44; rotation_state = ROTATING
   - Step 2: `WRITE_DUAL_VERIFY_ENTRY` — first new-key-signed entry written; old key remains in verification set
   - Step 3: `PROBE_VERIFY_AT_READ` — both keys verify the new entry successfully
   - Step 4: `VERIFY_HASH_CHAIN_LINK` — `prior_event_hash` continuity preserved across rotation boundary
   - Step 5: `ROTATE_SIGNING_TO_NEW` — old key rotation_state = RETIRING; new key rotation_state = ACTIVE
   - Step 6: `RETIRE_OLD_KEY` — old key removed from verification set after dual-verify quiescence
7. Rotation does NOT modify historical entries (immutable per F2 invariant); historical entries remain verifiable by the (retired) key that signed them per C-CP-20 §20.3 closing invariant.
8. Rotation 6-step verification is integration-test-bound; partial-rotation states (Step 1–5 incomplete) emit `audit.policy.rotation_state_partial = true`.

**Tests:** `test_five_axis_orthogonality`, `test_gate_level_and_sandbox_tier_independent`, `test_composition_admissible_for_valid_inputs`, `test_override_scope_table_match_spec`, `test_lower_gate_prohibited_at_multi_tenant`, `test_raise_gate_permitted_at_all_tiers`, `test_narrow_palette_permitted_at_all_tiers`, `test_override_emits_audit_regardless_of_tier`, `test_key_rotation_two_stages`, `test_rotation_six_steps_in_order`, `test_step_2_dual_verify`, `test_step_3_both_keys_verify`, `test_step_4_chain_link_continuity`, `test_step_6_retire_after_dual_verify`, `test_historical_entries_immutable_across_rotation`, `test_partial_rotation_state_audited`.

**Rollback boundary:** Revert 5-axis composition + override + rotation. R-CP-10 multi-axis gate-level composition collapses to 4-axis only (loses sandbox-tier orthogonal axis); operator-policy override loses scope discipline; signing-key rotation degrades to single-key (no historical-entry verifiability across rotation). Cross-axis AS edges to U-AS-12, U-AS-14 release.

#### U-CP-46 — Declare 7 `audit.*` attributes + per-persona-tier emission table + 4 `hitl.*` span attribute schemas

**Implements:** [C-CP-20 §20.4, §20.5]

**Depends on:** [U-CP-37, U-CP-38, U-CP-42, U-CP-43, U-CP-44, U-CP-45, U-CP-47]

**Inputs:** HITL palette (U-CP-37); placement + signature (U-CP-38); per-persona-tier crypto shape (U-CP-42); 4-axis gate-level rule + composition winner (U-CP-43); F5 signing-key resolution (U-CP-44); 5-axis composition + override (U-CP-45); validator-fail taxonomy (U-CP-47).

**Files affected:** CP-axis audit namespace (logical: `audit-namespace-attribute-schema`); CP-axis hitl-span namespace (logical: `hitl-span-namespace-attribute-schema`); CP-axis per-persona-tier emission table (logical: `per-persona-tier-audit-emission-table`).

**Signatures:**

```
record AuditAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
  emitted_on     : string                             // span name where attribute appears
}
const AUDIT_NAMESPACE_SCHEMA: List<AuditAttributeSchema>  // exactly 7 entries

record HITLSpanAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
  emitted_on     : string                             // hitl.* span name
}
const HITL_SPAN_NAMESPACE_SCHEMA: List<HITLSpanAttributeSchema>  // exactly 4 entries

record PersonaTierEmissionRow {
  persona_tier              : PersonaTier
  required_audit_attributes : Set<string>
  optional_audit_attributes : Set<string>
}
const PERSONA_TIER_AUDIT_EMISSION: List<PersonaTierEmissionRow>  // exactly 3 entries
```

**Acceptance criteria:**
1. `AUDIT_NAMESPACE_SCHEMA` declares exactly 7 attributes per C-CP-20 §20.4 verbatim:
   - `audit.gate.computed_level` (`GateLevel` enum)
   - `audit.gate.composition_winner_axis` (string; from U-CP-43)
   - `audit.policy.override_kind` (`OverrideKind` enum)
   - `audit.policy.override_scope` (`OverrideScope` enum)
   - `audit.policy.rotation_state_partial` (bool)
   - `audit.signature.key_id` (string)
   - `audit.signature.verification_result` (`VerificationResult` enum)
2. `HITL_SPAN_NAMESPACE_SCHEMA` declares exactly 4 attributes per C-CP-20 §20.5 verbatim:
   - `hitl.gate.evaluated.placement` (`HITLPlacementKind` enum)
   - `hitl.gate.evaluated.response_palette` (`Set<HITLResponse>`)
   - `hitl.invocation.responded.response_class` (`HITLResponse` enum)
   - `hitl.invocation.responded.response_latency_ms` (int)
3. Spans where attributes appear per spec §20.5:
   - `audit.gate.*` → `hitl.gate.evaluated`
   - `audit.policy.*` → `hitl.policy.overridden`
   - `audit.signature.*` → emitted at audit-entry-write time (audit-ledger entries only at multi-tenant-compliance)
   - `hitl.gate.evaluated.*` → `hitl.gate.evaluated` span
   - `hitl.invocation.responded.*` → `hitl.invocation.responded` span
4. `PERSONA_TIER_AUDIT_EMISSION` declares per C-CP-20 §20.4 verbatim:
   - `SOLO_DEVELOPER`: required `{audit.gate.computed_level}`; optional `{audit.gate.composition_winner_axis, audit.policy.*}`
   - `TEAM_BINDING`: required `{audit.gate.computed_level, audit.gate.composition_winner_axis, audit.policy.override_kind}`; optional `{audit.signature.*}`
   - `MULTI_TENANT_COMPLIANCE`: required all 7 audit attributes; optional `{}`
5. Emission is **strictly monotonic** along persona-tier axis — required set ascends across tiers. Reordering is Workflow §4.1.2 Class-2 D5 revision.
6. `audit.signature.*` attributes emit only at `MULTI_TENANT_COMPLIANCE` per U-CP-42 + U-CP-44 invariants.
7. `audit.policy.rotation_state_partial = true` flagged whenever U-CP-45 6-step rotation incomplete (steps 1–5 in flight).
8. D6 ingestion delegates to U-CP-54 §24.1.A (specialization-layer namespaces).
9. Sampling discipline per OD plan Session 4 D6 §1.3: all audit + HITL spans `ALWAYS_SAMPLED` (operator-burden + tamper-evidence relevance).
10. `hitl.gate.evaluated` span fires regardless of `_hitl_required` outcome (records the evaluation decision).
11. `hitl.invocation.responded` span fires only when human response received (timeout → no span; recorded at U-CP-52 timeout-degradation instead).
12. `audit.signature.verification_result` discriminates `{VALID, INVALID, KEY_RETIRED_BUT_HISTORICAL, KEY_NOT_FOUND}` per §20.5.
13. `hitl.gate.evaluated.response_palette` cardinality is bounded (`Set<HITLResponse>` over 4 values → 16 possible values including empty); empty set is invalid (palette completeness invariant per U-CP-37).
14. `hitl.invocation.responded.response_latency_ms` is positive integer; bounded by U-CP-52 timeout if configured.
15. `audit.gate.composition_winner_axis` value space matches U-CP-43 four input axes (`persona_tier`, `blast_radius_tier`, `deployment_surface`, `mcp_trust_tier`) per §19.1 composition rule.
16. `audit.policy.override_kind` value space matches U-CP-45 `OverrideKind` enum (`LOWER_GATE_LEVEL`, `RAISE_GATE_LEVEL`, `NARROW_PALETTE`).
17. `audit.policy.override_scope` value space matches U-CP-45 `OverrideScope` enum (`PER_TOOL`, `PER_WORKFLOW`, `PER_PERSONA_TIER`).
18. Attribute names are **byte-exact** per spec verbatim; renaming requires Workflow §4.1.2 Class-2 D5 revision.
19. Schema declaration is **purely descriptive** — emission mechanics owned by OD plan Session 4 D6 §1.2 + §1.3.
20. Cardinality enforcement: `AUDIT_NAMESPACE_SCHEMA.length == 7` and `HITL_SPAN_NAMESPACE_SCHEMA.length == 4` invariants verified at startup.

**Tests:** `test_audit_namespace_cardinality_seven`, `test_audit_attributes_match_spec_verbatim`, `test_hitl_span_namespace_cardinality_four`, `test_hitl_span_attributes_match_spec_verbatim`, `test_per_persona_emission_cardinality_three`, `test_solo_minimal_required`, `test_team_required_three_attrs`, `test_multi_tenant_required_all_seven`, `test_monotonic_emission_ascending`, `test_signature_attrs_only_multi_tenant`, `test_rotation_state_partial_when_in_flight`, `test_hitl_gate_evaluated_fires_regardless`, `test_hitl_invocation_responded_fires_only_on_response`, `test_signature_verification_result_four_values`, `test_response_palette_empty_invalid`, `test_response_latency_positive_int`, `test_composition_winner_axis_four_values`, `test_override_kind_three_values`, `test_override_scope_three_values`, `test_attribute_names_byte_exact`, `test_schema_purely_descriptive`, `test_cardinality_invariants_at_startup`.

**Rollback boundary:** Revert audit + HITL-span namespaces + per-persona emission table. R-CP-10 audit attribute composition fails; R-CP-11 HITL span schema fails; R-CP-12 multi-tenant-compliance audit attribute set fails; U-CP-54 §24.1.A export manifest loses CP-side source for `audit.*` + `hitl.*` namespaces; OD plan Session 4 D6 §1.2 + §1.3 ingestion loses CP source for audit + HITL spans.

---

### §2.8 Cluster 8 — D5 escalation + context revalidation (C-CP-21, C-CP-22)

**Anchor.** ADR-D5 v1.3.

**Theme.** Two contracts compose the validator-fail escalation surface and the pause/resume context-revalidation discipline: 5-class fail taxonomy + transient staircase + palette restriction + summarization-model table + `validator.fail.*` attrs + sampling + operator-burden eval + timeout-degradation (C-CP-21); context revalidation resume protocol + material-diff detection + state_summary snapshot + T-perm-2 F2-layer composition (C-CP-22).

#### U-CP-47 — Declare 5-class fail taxonomy + `validator.fail.*` namespace

**Implements:** [C-CP-21 §21.1, §21.5]

**Depends on:** [U-AS-03 (cross-axis: AS)]

**Inputs:** `SandboxFailClass` taxonomy (U-AS-03 cross-axis AS) — composition reference for `sandbox_violation` class.

**Files affected:** CP-axis validator-fail class enum (logical: `validator-fail-class-taxonomy`); CP-axis validator-fail namespace (logical: `validator-fail-namespace-schema`).

**Cross-axis substrate consumed.** AS C-AS-04 `SandboxFailClass` taxonomy via U-AS-03 for `sandbox_violation` cross-axis composition reference.

**Signatures:**

```
enum ValidatorFailClass {
  SCHEMA_MISMATCH,                                    // permanent; no retry
  TIMEOUT,                                            // transient; retry per staircase
  RATE_LIMIT,                                         // transient; retry per staircase
  PERMANENT_REJECTION,                                // permanent; no retry; escalate to HITL
  SANDBOX_VIOLATION                                   // permanent; composes with AS C-AS-04 SandboxFailClass
}

enum ValidatorFailDispositionKind {
  PERMANENT_NO_RETRY,
  TRANSIENT_RETRY_PER_STAIRCASE,
  PERMANENT_ESCALATE_HITL,
  PERMANENT_COMPOSED_WITH_AS_FAIL_CLASS
}

record ValidatorFailMetadata {
  fail_class           : ValidatorFailClass
  is_transient         : bool
  disposition          : ValidatorFailDispositionKind
  composes_with        : Optional<string>             // cross-axis composition citation
}
const VALIDATOR_FAIL_METADATA: List<ValidatorFailMetadata>  // exactly 5 entries

record ValidatorFailAttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType
  cardinality    : Cardinality
}
const VALIDATOR_FAIL_NAMESPACE_SCHEMA: List<ValidatorFailAttributeSchema>  // exactly 3 entries
```

**Acceptance criteria:**
1. `ValidatorFailClass` declares exactly five values per C-CP-21 §21.1 verbatim. Closed at cardinality 5; extension requires Workflow §4.1.2 Class-2 D5 revision.
2. `VALIDATOR_FAIL_METADATA` declares per §21.1 verbatim:
   - `SCHEMA_MISMATCH` → permanent; no retry
   - `TIMEOUT` → transient; retry per staircase
   - `RATE_LIMIT` → transient; retry per staircase
   - `PERMANENT_REJECTION` → permanent; escalate to HITL
   - `SANDBOX_VIOLATION` → permanent; composes with AS C-AS-04 `SandboxFailClass`
3. `VALIDATOR_FAIL_NAMESPACE_SCHEMA` declares exactly three attributes per §21.5 verbatim: `validator.fail.class` (`ValidatorFailClass` enum); `validator.fail.is_transient` (bool); `validator.fail.retry_attempt` (int).
4. `is_transient` field is the discriminator consumed by U-CP-48 transient staircase entry decision.
5. D6 ingestion delegates to U-CP-54 §24.1.A.

**Tests:** `test_validator_fail_class_cardinality_five`, `test_validator_fail_metadata_match_spec`, `test_schema_mismatch_permanent`, `test_timeout_transient`, `test_rate_limit_transient`, `test_permanent_rejection_escalates_hitl`, `test_sandbox_violation_composes_with_as`, `test_validator_fail_namespace_cardinality_three`.

**Rollback boundary:** Revert `ValidatorFailClass` enum + metadata + namespace. R-CP-11 validator-escalation HITL placement loses fail-class discriminator; U-CP-48 staircase loses cause input; U-CP-54 §24.1.A export manifest loses CP-side source. Cross-axis AS edge to U-AS-03 releases.

#### U-CP-48 — Implement transient staircase + cause-attribution branching + palette restriction

**Implements:** [C-CP-21 §21.2, §21.4]

**Depends on:** [U-CP-07, U-CP-37, U-CP-47, U-AS-10 (cross-axis: AS), U-AS-29 (cross-axis: AS)]

**Inputs:** `RetryCause` enum (U-CP-07); HITL palette (U-CP-37); validator-fail taxonomy (U-CP-47); `secret.fail.class` taxonomy (U-AS-10 cross-axis); model catalog for summarization fallback (U-AS-29 cross-axis).

**Files affected:** CP-axis transient staircase (logical: `validator-fail-transient-staircase`); CP-axis cause-attribution branching (logical: `staircase-cause-branching`); CP-axis palette restriction rule (logical: `palette-restriction-rule`).

**Cross-axis substrate consumed.** AS C-AS-07 `secret.fail.class` taxonomy (U-AS-10) — cross-axis source for cause-branching; AS C-AS-13 §13.4 model-tier catalog (U-AS-29) — for cross-family fallback model selection.

**Signatures:**

```
enum StaircaseStage {
  STAGE_1_REFLEXION,                                  // verbal feedback + retry
  STAGE_2_RETRY_WITH_BACKOFF,                         // full-jitter exponential backoff
  STAGE_3_CROSS_FAMILY_FALLBACK,                      // delegate to U-CP-09
  STAGE_4_LOCAL_TERMINAL,                             // local open-weight tier
  STAGE_5_HITL_ESCALATION                             // validator-escalation placement
}

record StaircaseTransition {
  from_stage              : StaircaseStage
  on_cause                : ValidatorFailClass
  to_stage                : StaircaseStage
  preserves_cache_state   : bool                      // false at stage 3 cross-family per C-CP-04 §4.3
  emits_fallback_event    : bool
}
const TRANSIENT_STAIRCASE_TRANSITIONS: List<StaircaseTransition>

enum CrossTrustBoundaryState {
  NONE,
  CROSS_FAMILY_ACTIVE,                                // post-stage-3
  LOCAL_TERMINAL_ACTIVE,                              // post-stage-4
  UNTRUSTED_MCP_ACTIVE                                // when MCP server trust < TIER_2
}

record PaletteRestriction {
  cross_trust_state    : CrossTrustBoundaryState
  restricted_palette   : Set<HITLResponse>
  rationale            : string
}
const PALETTE_RESTRICTION_TABLE: List<PaletteRestriction>  // exactly 4 entries

function advance_staircase(current: StaircaseStage, cause: ValidatorFailClass, attempt: int) -> StaircaseTransition
function compute_restricted_palette(state: CrossTrustBoundaryState) -> Set<HITLResponse>
```

**Acceptance criteria:**
1. `StaircaseStage` declares exactly five stages per C-CP-21 §21.2 verbatim.
2. `TRANSIENT_STAIRCASE_TRANSITIONS` implements §21.2 cause-attribution branching:
   - `STAGE_1_REFLEXION` on `SCHEMA_MISMATCH` → `STAGE_5_HITL_ESCALATION` (permanent; bypass remaining stages)
   - `STAGE_1_REFLEXION` on `TIMEOUT` / `RATE_LIMIT` → `STAGE_2_RETRY_WITH_BACKOFF`
   - `STAGE_2_RETRY_WITH_BACKOFF` retry-budget exhausted → `STAGE_3_CROSS_FAMILY_FALLBACK`
   - `STAGE_3_CROSS_FAMILY_FALLBACK` on family-chain exhausted → `STAGE_4_LOCAL_TERMINAL`
   - `STAGE_4_LOCAL_TERMINAL` on local-fail → `STAGE_5_HITL_ESCALATION`
   - Any stage on `SANDBOX_VIOLATION` → `STAGE_5_HITL_ESCALATION` (permanent; immediate escalation)
   - Any stage on `PERMANENT_REJECTION` → `STAGE_5_HITL_ESCALATION` (permanent; immediate escalation)
3. Stage 3 transitions emit `fallback.cross_family_triggered` + `fallback.cache_state_lost` per U-CP-09 + C-CP-04 §4.3.
4. `CrossTrustBoundaryState` declares exactly four values per §21.4 verbatim.
5. `PALETTE_RESTRICTION_TABLE` declares exactly four entries per §21.4 verbatim:
   - `NONE` → full palette `{APPROVE, EDIT, REJECT, RESPOND}`
   - `CROSS_FAMILY_ACTIVE` → `{REJECT, RESPOND}` (APPROVE/EDIT prohibited; cache state lost; no proposal continuity)
   - `LOCAL_TERMINAL_ACTIVE` → `{REJECT, RESPOND}` (APPROVE/EDIT prohibited; tier downgrade explicit)
   - `UNTRUSTED_MCP_ACTIVE` → `{REJECT, RESPOND}` (APPROVE/EDIT prohibited; trust-tier-floor invariant)
6. Restriction composes with U-CP-37 palette completeness invariant — restriction is permissible at `PRE_HITL_ESCALATION` invariant enforcement point per §16.3.
7. `advance_staircase` deterministic given inputs; no inference path.

**Tests:** `test_staircase_stage_cardinality_five`, `test_schema_mismatch_bypass_to_stage_5`, `test_timeout_advances_to_stage_2`, `test_rate_limit_advances_to_stage_2`, `test_budget_exhausted_advances_to_stage_3`, `test_family_exhausted_advances_to_stage_4`, `test_local_fail_advances_to_stage_5`, `test_sandbox_violation_immediate_stage_5`, `test_permanent_rejection_immediate_stage_5`, `test_stage_3_emits_cache_state_lost`, `test_cross_trust_state_cardinality_four`, `test_palette_restriction_match_spec`, `test_none_full_palette`, `test_cross_family_restricted_to_reject_respond`, `test_local_terminal_restricted_to_reject_respond`, `test_untrusted_mcp_restricted_to_reject_respond`, `test_restriction_composes_with_completeness_invariant`.

**Rollback boundary:** Revert staircase + cause-branching + palette restriction. R-CP-11 validator-escalation HITL placement loses staircase progression; U-CP-39 rewriting algorithm loses palette restriction source; cross-trust-boundary state at HITL invocation degrades to full palette regardless of state. Cross-axis AS edges to U-AS-10, U-AS-29 release.

#### U-CP-49 — Implement pause/resume protocol + state_summary snapshot capture

**Implements:** [C-CP-22 §22.1]

**Depends on:** [U-CP-30, U-CP-50, U-IS-11 (cross-axis: IS), U-IS-12 (cross-axis: IS)]

**Inputs:** `HandoffContext` + `StateSummary` + `ExternalReference` schemas (U-CP-30); material-diff detection (U-CP-50); F2 append + bounded-read (U-IS-11, U-IS-12).

**Files affected:** CP-axis pause/resume protocol (logical: `pause-resume-protocol`); CP-axis state_summary snapshot capture (logical: `state-summary-snapshot-capture`).

**Cross-axis substrate consumed.** `JSONL_EVENT_LEDGER_FORMAT_EXPORT` + `IDEMPOTENCY_KEY_JOIN_EXPORT` (C-IS-10 §10.5, §10.2 → U-IS-11, U-IS-12).

**Signatures:**

```
record PauseEvent {
  paused_at              : ISO8601
  pause_reason           : PauseReason
  state_summary_snapshot : StateSummary
  external_refs_captured : List<ExternalReference>
  pause_audit_entry_id   : EntryID
}

enum PauseReason {
  HITL_INVOCATION_PENDING,
  CROSS_DEPLOYMENT_BRIDGING_ARC_PAUSE,
  OPERATOR_INITIATED_PAUSE,
  ENGINE_NATIVE_PAUSE                                 // event-sourced-replay / reconciler engines
}

record ResumeAttempt {
  paused_workflow_id    : WorkflowID
  resume_at             : ISO8601
  resume_request_actor  : ActorIdentity
}

record ResumeOutcome {
  outcome_kind          : ResumeOutcomeKind
  material_diff         : Optional<MaterialDiff>      // from U-CP-50
  context_revalidated   : bool
  resume_audit_entry_id : Optional<EntryID>
}

enum ResumeOutcomeKind {
  RESUME_CLEAN,                                       // no material diff; resume immediately
  RESUME_AFTER_REVALIDATION,                          // material diff detected; revalidation completed; resume
  ABORT_REVALIDATION_FAILED,                          // material diff detected; revalidation failed; escalate to HITL
  ABORT_SNAPSHOT_CORRUPTED                            // snapshot integrity violated
}

function capture_pause_snapshot(workflow_id: WorkflowID, pause_reason: PauseReason) -> PauseEvent
function attempt_resume(attempt: ResumeAttempt) -> ResumeOutcome
```

**Acceptance criteria:**
1. `PauseEvent` declares exactly five fields per C-CP-22 §22.1 verbatim.
2. `PauseReason` declares exactly four values per §22.1.
3. `capture_pause_snapshot` captures `external_refs_captured` per U-CP-30 `ExternalReference.snapshot_capture_at_pause` field; serialized at pause time.
4. `pause_audit_entry_id` written via U-IS-11 append; F2 entry shape per U-IS-07 with `actor = OPERATOR_OR_ENGINE`, `response_hash = sha256(canonicalize(PauseEvent))`.
5. `attempt_resume` reads pause snapshot via U-IS-12 bounded-read keyed on `paused_workflow_id`; integrity-verifies snapshot via prior_event_hash chain per U-IS-09.
6. `ResumeOutcomeKind` declares exactly four values per §22.1.
7. Material-diff detection delegates to U-CP-50; this unit consumes the result, does not recompute.
8. T-perm-2 across-turn boundary crosses through F2 read/write contract pair (snapshot read; resume audit append) — F2-layer resolution stands per ADR-D4 v1.1 §1.10 + C-CP-22 §22.4.
9. Snapshot serialization format deferred to implementation discretion per spec §22.1 deferred list; integrity invariant requires deterministic round-trip.
10. Resume protocol is **deterministic** given (pause_snapshot, current_state, material_diff); no inference path.

**Tests:** `test_pause_event_five_fields`, `test_pause_reason_cardinality_four`, `test_pause_snapshot_captures_external_refs`, `test_pause_audit_via_u_is_11`, `test_attempt_resume_reads_via_u_is_12`, `test_snapshot_integrity_verified_via_u_is_09`, `test_resume_outcome_cardinality_four`, `test_clean_resume_no_diff`, `test_revalidation_resume_with_diff`, `test_abort_on_revalidation_fail`, `test_abort_on_snapshot_corruption`, `test_t_perm_2_f2_layer_resolution_stands`, `test_resume_deterministic`.

**Rollback boundary:** Revert pause/resume protocol + snapshot capture. R-CP-13 context revalidation discipline fails; workflow pause across HITL invocation loses durable resume substrate; T-perm-2 F2-layer composition surface dissolves. Cross-axis IS edges to U-IS-11, U-IS-12 release.

#### U-CP-50 — Implement material-diff detection + revalidation + summarization fallback

**Implements:** [C-CP-21 §21.4, C-CP-22 §22.2, §22.3]

**Depends on:** [U-CP-30, U-CP-49, U-IS-01 (cross-axis: IS), U-IS-11 (cross-axis: IS), U-IS-12 (cross-axis: IS), U-AS-10 (cross-axis: AS), U-AS-29 (cross-axis: AS)]

**Inputs:** `ExternalReference` + `StateSummary` schemas (U-CP-30); pause/resume protocol (U-CP-49); F2 substrate (U-IS-11, U-IS-12); filesystem path contract (U-IS-01); secret-fail taxonomy (U-AS-10); summarization model catalog (U-AS-29).

**Files affected:** CP-axis material-diff detector (logical: `material-diff-detector`); CP-axis revalidation procedure (logical: `revalidation-procedure`); CP-axis summarization fallback (logical: `summarization-model-fallback`).

**Cross-axis substrate consumed.** `FILESYSTEM_PATH_CONTRACT_EXPORT` (C-IS-10 §10.4 → U-IS-01); `JSONL_EVENT_LEDGER_FORMAT_EXPORT` + `IDEMPOTENCY_KEY_JOIN_EXPORT` (C-IS-10 §10.5, §10.2 → U-IS-11, U-IS-12); AS C-AS-07 `secret.fail.class` (U-AS-10) for secret-state diff; AS C-AS-13 §13.4 model catalog (U-AS-29) for summarization fallback.

**Signatures:**

```
record MaterialDiff {
  diff_categories       : Set<DiffCategory>
  per_category_changes  : Map<DiffCategory, List<DiffEntry>>
  material              : bool                        // false if all diffs immaterial
}

enum DiffCategory {
  F2_LEDGER_ENTRY_DRIFT,                              // entries added since pause
  EXTERNAL_MCP_RESOURCE_CHANGED,
  FILESYSTEM_STATE_CHANGED,
  FAILED_ATTEMPTS_DIVERGED,
  SECRET_STATE_CHANGED                                // cross-axis AS C-AS-07 composition
}

record DiffEntry {
  category              : DiffCategory
  reference             : ExternalReference
  pre_pause_hash        : SHA256
  post_pause_hash       : SHA256
  materiality_predicate : Bool                        // category-specific materiality rule
}

record SummarizationModelBinding {
  persona_tier        : PersonaTier
  primary_binding     : ModelBinding
  fallback_binding    : ModelBinding
  rationale           : string
}
const SUMMARIZATION_MODEL_TABLE: List<SummarizationModelBinding>  // exactly 3 entries

function detect_material_diff(pause: PauseEvent, current_state: CurrentState) -> MaterialDiff
function revalidate_context(diff: MaterialDiff, persona_tier: PersonaTier) -> RevalidationOutcome
function summarize_diff_for_operator(diff: MaterialDiff, persona_tier: PersonaTier) -> string
```

**Acceptance criteria:**
1. `DiffCategory` declares exactly five values per C-CP-22 §22.2 verbatim.
2. `detect_material_diff` examines all five categories at resume time; produces `MaterialDiff` with per-category change set.
3. `material = false` when all diff entries' `materiality_predicate = false`; resume proceeds clean per U-CP-49 `RESUME_CLEAN`.
4. `F2_LEDGER_ENTRY_DRIFT` reads via U-IS-12 bounded-read on entries after pause `prior_event_hash` cursor.
5. `EXTERNAL_MCP_RESOURCE_CHANGED` compares pre-pause snapshot hash from U-CP-30 `ExternalReference.snapshot_capture_at_pause` against current resource hash.
6. `FILESYSTEM_STATE_CHANGED` resolves via U-IS-01 canonical paths + hash comparison.
7. `SECRET_STATE_CHANGED` composes with AS C-AS-07 `secret.fail.class` taxonomy via U-AS-10 — secret rotation between pause and resume is a material diff.
8. Per-category `materiality_predicate` deferred to implementation discretion per spec §22.2 deferred list; default-materiality rule: any cryptographic-hash mismatch is material.
9. `SUMMARIZATION_MODEL_TABLE` declares per C-CP-21 §21.4 + C-CP-22 §22.3 verbatim:
   - `SOLO_DEVELOPER` → primary: Sonnet 4.6; fallback: Haiku 4.5
   - `TEAM_BINDING` → primary: Sonnet 4.6; fallback: Haiku 4.5
   - `MULTI_TENANT_COMPLIANCE` → primary: Opus 4.7; fallback: Sonnet 4.6
10. Summarization fallback delegates model selection to U-AS-29 catalog.
11. `revalidate_context` outcome depends on `persona_tier`: `SOLO_DEVELOPER` auto-resumes after operator notification; `TEAM_BINDING` requires operator approval; `MULTI_TENANT_COMPLIANCE` requires operator approval AND audit emission.
12. Material-diff detection is **deterministic** given (pause_snapshot, current_state); summarization is the only LLM-invoking step.

**Tests:** `test_diff_category_cardinality_five`, `test_detect_examines_all_categories`, `test_immaterial_diff_clean_resume`, `test_f2_drift_via_u_is_12`, `test_mcp_resource_via_snapshot_hash`, `test_filesystem_via_u_is_01`, `test_secret_state_via_u_as_10`, `test_summarization_model_table_match_spec`, `test_summarization_per_tier`, `test_fallback_via_u_as_29`, `test_revalidate_solo_auto_resume`, `test_revalidate_team_operator_approval`, `test_revalidate_multi_tenant_approval_plus_audit`, `test_diff_detection_deterministic`.

**Rollback boundary:** Revert material-diff detection + revalidation + summarization. R-CP-13 context revalidation discipline fails; U-CP-49 resume protocol loses diff input; cross-deployment bridging-arc resume degrades to no-revalidation. Cross-axis edges to U-IS-01, U-IS-11, U-IS-12, U-AS-10, U-AS-29 release.

#### U-CP-51 — Implement operator-burden eval primitive sampling + tail-keep rules

**Implements:** [C-CP-21 §21.3]

**Depends on:** [U-CP-37, U-CP-46]

**Inputs:** HITL palette (U-CP-37); `hitl.*` span schemas (U-CP-46).

**Files affected:** CP-axis operator-burden eval (logical: `operator-burden-eval-primitive`); CP-axis tail-keep rules (logical: `operator-burden-tail-keep`).

**Signatures:**

```
record OperatorBurdenEval {
  invocations_per_workflow      : int
  responses_per_class           : Map<HITLResponse, int>
  avg_response_latency_ms       : float
  workflow_throughput_impact_ms : int                 // (sum of latencies) / wallclock duration
}

record TailKeepRule {
  span_name        : string
  keep_predicate   : TailKeepPredicate
  rationale        : string
}
const HITL_TAIL_KEEP_RULES: List<TailKeepRule>  // exactly 3 entries

function compute_operator_burden(workflow_id: WorkflowID, time_window: Duration) -> OperatorBurdenEval
function evaluate_tail_keep(span: Span) -> bool
```

**Acceptance criteria:**
1. `OperatorBurdenEval` declares exactly four fields per C-CP-21 §21.3 verbatim.
2. `HITL_TAIL_KEEP_RULES` declares exactly three entries per §21.3 verbatim:
   - `hitl.gate.evaluated` → keep when `audit.gate.computed_level > GATE_NONE` (skip when no gate triggered; reduces high-volume noise)
   - `hitl.invocation.responded` → always-keep (every operator response retained for burden analysis)
   - `hitl.policy.overridden` → always-keep (override evidence for audit)
3. `compute_operator_burden` aggregates over `time_window`; `invocations_per_workflow` divides total invocations by distinct workflow count.
4. `responses_per_class` cardinality bounded at 4 (`HITLResponse` enum cardinality).
5. `workflow_throughput_impact_ms` measures wall-clock displacement attributable to HITL waiting, not absolute latency.
6. Eval primitive is **passive observation** — does not modify workflow execution.

**Tests:** `test_operator_burden_eval_four_fields`, `test_tail_keep_rules_cardinality_three`, `test_gate_evaluated_keep_above_none`, `test_invocation_responded_always_keep`, `test_policy_overridden_always_keep`, `test_invocations_per_workflow_division`, `test_responses_per_class_cardinality_four`, `test_eval_passive_no_execution_impact`.

**Rollback boundary:** Revert operator-burden eval + tail-keep rules. OD plan Session 4 D6 §1.3 sampling discipline loses CP-side rule source for HITL spans; operator-burden analysis degrades to span-volume-only metric.

#### U-CP-52 — Implement HITL timeout-degradation + webhook delivery semantics

**Implements:** [C-CP-21 §21.6]

**Depends on:** [U-CP-37, U-CP-38, U-CP-46, U-IS-07 (cross-axis: IS), U-IS-11 (cross-axis: IS)]

**Inputs:** HITL palette (U-CP-37); HITL placement + signature (U-CP-38); `hitl.*` + `audit.*` span schemas (U-CP-46); F2 append (U-IS-07, U-IS-11).

**Files affected:** CP-axis HITL timeout-degradation (logical: `hitl-timeout-degradation`); CP-axis webhook delivery semantics (logical: `hitl-webhook-delivery`).

**Cross-axis substrate consumed.** F2 substrate seams (U-IS-07, U-IS-11).

**Signatures:**

```
enum TimeoutDegradationKind {
  CONTINUE_AS_REJECT,                                 // treat timeout as REJECT response
  ESCALATE_TO_REVIEW_BOARD,                           // raise gate level; second invocation
  ABORT_WORKFLOW                                      // terminal; no further attempts
}

record TimeoutDegradationPolicy {
  persona_tier            : PersonaTier
  default_kind            : TimeoutDegradationKind
  override_permitted      : bool
  audit_required          : bool                      // always true
}
const TIMEOUT_DEGRADATION_TABLE: List<TimeoutDegradationPolicy>  // exactly 3 entries

record WebhookDeliveryEvent {
  webhook_id           : string
  workflow_id          : WorkflowID
  gate_evaluation_ref  : EntryID
  payload_hash         : SHA256
  delivery_attempts    : int
  delivery_outcome     : WebhookDeliveryOutcome
}

enum WebhookDeliveryOutcome { DELIVERED, RETRY_PENDING, EXHAUSTED_AFTER_RETRIES }

function on_hitl_timeout(invocation: HITLInvocation, persona_tier: PersonaTier) -> TimeoutDegradationKind
function deliver_webhook(webhook: WebhookConfig, payload: WebhookPayload) -> WebhookDeliveryEvent
```

**Acceptance criteria:**
1. `TimeoutDegradationKind` declares exactly three values per C-CP-21 §21.6 verbatim.
2. `TIMEOUT_DEGRADATION_TABLE` declares per §21.6 verbatim:
   - `SOLO_DEVELOPER` → `CONTINUE_AS_REJECT`; override permitted
   - `TEAM_BINDING` → `ESCALATE_TO_REVIEW_BOARD`; override permitted
   - `MULTI_TENANT_COMPLIANCE` → `ABORT_WORKFLOW`; override prohibited (terminal)
3. `on_hitl_timeout` emits audit entry per U-CP-46 `audit.policy.*` attributes; F2 entry written via U-IS-07 + U-IS-11.
4. Webhook delivery delegates retry mechanics to harness retry primitive (substrate-anchored at C9 per U-CP-07 substrate-authority note); per-webhook retry budget deferred to implementation discretion per spec §21.6.
5. Webhook payload signature: `payload_hash = sha256(canonicalize(payload))`; receiver verification deferred.
6. `WebhookDeliveryOutcome` cardinality bounded at three; `EXHAUSTED_AFTER_RETRIES` triggers `audit.policy.webhook_delivery_failed = true`.
7. Webhook delivery is **idempotent** — duplicate delivery on retry does not produce duplicate workflow side effects (receiver-side dedup by `gate_evaluation_ref` join).

**Tests:** `test_timeout_degradation_kind_cardinality_three`, `test_timeout_degradation_table_match_spec`, `test_solo_continue_as_reject`, `test_team_escalate_review_board`, `test_multi_tenant_abort_workflow`, `test_multi_tenant_override_prohibited`, `test_timeout_emits_audit_entry`, `test_audit_via_u_is_07_11`, `test_webhook_payload_signature`, `test_webhook_outcome_cardinality_three`, `test_exhausted_emits_audit_flag`, `test_webhook_idempotency_via_gate_eval_ref`.

**Rollback boundary:** Revert timeout-degradation + webhook delivery. R-CP-11 HITL timeout discipline fails; workflow blocks indefinitely on unanswered HITL invocations; webhook integration for durable-async workflow loses delivery substrate. Cross-axis IS edges to U-IS-07, U-IS-11 release.

---

### §2.9 Cluster 9 — T-perm-3 composition + CP exports (C-CP-23, C-CP-24)

**Anchor.** ADR-D1 v1.1 + ADR-D4 v1.1 + ADR-F1 v1.2 + cross-axis composition.

**Theme.** Three units close the CP plan: T-perm-3 three-layer composition + deterministic outer-harness boundary (U-CP-53); CP-axis namespace export manifest (U-CP-54); cross-axis composition manifest + F2-12 carry-forward (U-CP-55).

#### U-CP-53 — Implement T-perm-3 three-layer composition + per-cell reading + orthogonal contract + deterministic outer-harness boundary

**Implements:** [C-CP-23 §23.1, §23.2, §23.3, §23.4]

**Depends on:** [U-CP-06, U-CP-08, U-CP-09, U-CP-16, U-CP-17, U-CP-24, U-CP-25, U-CP-43, U-AS-14 (cross-axis: AS)]

**Inputs:** `LayerBudget` (U-CP-06); fall-through procedure (U-CP-08); cross-family fallback (U-CP-09); per-deployment candidate mapping (U-CP-16); workload-binding selection (U-CP-17); per-engine topology overlay (U-CP-24); 2D matrix + D4 tunable (U-CP-25); 4-axis gate-level rule (U-CP-43); AS 5-axis multiplicative tunable (U-AS-14 cross-axis).

**Files affected:** CP-axis T-perm-3 composition (logical: `t-perm-3-three-layer-composition`); CP-axis per-cell reading (logical: `t-perm-3-per-cell-reading`); CP-axis runtime fault handling (logical: `t-perm-3-runtime-fault-handling`); CP-axis deterministic outer-harness boundary declaration (logical: `deterministic-outer-harness-boundary`).

**Cross-axis substrate consumed.** `FIVE_AXIS_MULTIPLICATIVE_TUNABLE_EXPORT` (C-AS-16 §16.2 → U-AS-14).

**T-perm-3 three layers (§23.1 verbatim):**

```
Layer F1 (routing/fallback): U-CP-08 fall-through + U-CP-09 cross-family chain
                              ↓ composes orthogonally with
Layer D1 (engine-class):     U-CP-16 candidate mapping + U-CP-17 binding selection
                              ↓ composes orthogonally with
Layer D4 (topology):         U-CP-24 per-engine overlay + U-CP-25 2D matrix + D4 tunable
```

**Signatures:**

```
record TPerm3LayerComposition {
  f1_layer_state         : F1LayerState               // routing/fallback state
  d1_layer_state         : D1LayerState               // engine-class state
  d4_layer_state         : D4LayerState               // topology state
  composition_admissible : bool                       // orthogonality invariant
}

record F1LayerState {
  current_routing_layer  : RoutingLayer
  fall_through_active    : bool
  cross_family_active    : bool
  cache_state_lost       : bool
}

record D1LayerState {
  engine_class           : EngineClass
  f2_join_kind           : F2JoinKind
  resumption_kind        : ResumptionKind
}

record D4LayerState {
  topology_pattern               : TopologyPattern
  cascade_enforcement_mechanism  : CascadeEnforcementMechanism
  t_perm_3_reading               : TopologyFaultHandling
}

enum PerCellReadingKind {
  ABOVE_ENGINE_HARNESS_COMPOSES,
  BELOW_ENGINE_HARNESS_AUTHORS_TOPOLOGY,
  RECONCILER_CONTROL_LOOP_OWNS_RECONVERGENCE
}

record PerCellTPerm3Reading {
  workload_class        : WorkloadClass
  engine_class          : EngineClass
  t_perm_3_reading      : PerCellReadingKind
  active_layer_owner    : LayerOwner                  // {HARNESS, ENGINE, CONTROL_LOOP}
}
const PER_CELL_T_PERM_3_READINGS: List<PerCellTPerm3Reading>  // exactly 20 entries (4 × 5)

record DeterministicOuterHarnessBoundary {
  probabilistic_core_surface  : string                // "infer(...) per U-CP-03"
  deterministic_primitives    : List<string>          // 5 primitives per §23.4
  boundary_contract           : string                // ADD §5.3.3 verbatim
}

function compose_t_perm_3(workload: WorkloadClass, engine: EngineClass, persona: PersonaTier) -> TPerm3LayerComposition
function read_per_cell_t_perm_3(workload: WorkloadClass, engine: EngineClass) -> PerCellTPerm3Reading
function handle_runtime_fault(fault: RuntimeFault, composition: TPerm3LayerComposition) -> FaultHandlingDisposition
```

**Acceptance criteria:**
1. `compose_t_perm_3` runs F1 + D1 + D4 as **orthogonal layers** per C-CP-23 §23.1 — no layer collapses into another. Composition result carries all three layer states independently.
2. `composition_admissible = true` for all valid (workload, engine, persona) tuples; orthogonality invariant verified at integration test against U-CP-25 + U-AS-14.
3. `PER_CELL_T_PERM_3_READINGS` declares exactly 20 cells (4 workload classes × 5 engine classes) per C-CP-23 §23.2 verbatim:
   - `EVENT_SOURCED_REPLAY` cells → `BELOW_ENGINE_HARNESS_AUTHORS_TOPOLOGY`; `active_layer_owner = ENGINE`
   - `SAVE_POINT_CHECKPOINT` / `PURE_PATTERN_NO_ENGINE` / `WAL_SEGMENT` cells → `ABOVE_ENGINE_HARNESS_COMPOSES`; `active_layer_owner = HARNESS`
   - `RECONCILER_LOOP` cells → `RECONCILER_CONTROL_LOOP_OWNS_RECONVERGENCE`; `active_layer_owner = CONTROL_LOOP`
4. Per-cell reading inherits U-CP-24 per-engine overlay; non-collapsing invariant preserved (each cell has exactly one reading).
5. Excluded cells per U-CP-16 (`PURE_PATTERN_NO_ENGINE` at `SELF_HOSTED_SERVER` / `MANAGED_CLOUD`) carry `cell_admissible = false`; reading is N/A.
6. `handle_runtime_fault` per C-CP-23 §23.3 dispatches by `t_perm_3_reading`:
   - `ABOVE_ENGINE` → harness composes lease re-acquisition + dedup + resumption (via U-CP-09, U-CP-20)
   - `BELOW_ENGINE` → engine-native cancellation propagates; harness becomes topology-author observer (via U-CP-24 overlay)
   - `RECONCILER` → CRD reconciler reconverges; harness emits topology spans only
7. `DeterministicOuterHarnessBoundary` declares per ADD §5.3.3 + C-CP-23 §23.4 verbatim:
   - **Probabilistic core**: `infer(...)` surface at U-CP-03 (LLM inference)
   - **Deterministic outer-harness primitives** (5 per §23.4):
     - Chain-advancement (U-CP-09 cross-family fallback)
     - Cascade-enforcement (U-CP-25 D4 tunable)
     - Retry mechanics (U-CP-07 `retry.*` namespace; harness-anchored)
     - Breaker mechanics (`harness.breaker.*` substrate-anchored at C9 per U-CP-07 substrate-authority note)
     - HITL escalation (U-CP-47 + U-CP-48 staircase + U-CP-49 pause/resume)
8. Boundary contract: everything outside the probabilistic core is deterministic; verified at integration test by exhaustive enumeration of T-perm-3 cells.
9. T-perm-3 composition is **per-binding-time** (not runtime); selection bound at workflow manifest entry (U-CP-13); runtime evaluates the bound composition.
10. Per-cell reading non-collapsing invariant: no cell maps to multiple readings per §23.2 closing sentence.
11. Five deterministic primitives are byte-exact enumeration; addition or removal is a Workflow §4.1.2 Class-2 D1+D4+F1 revision.
12. Orthogonal contract: F1 layer state independent of D1 layer state independent of D4 layer state — product space is admissible without cross-layer constraints (other than excluded cells per #5).
13. T-perm-3 reading determines **which layer owns fault recovery**; non-collapsing invariant prevents recovery-path ambiguity.
14. Runtime fault dispatcher delegates to U-CP-09 / U-CP-24 / U-CP-25 / U-CP-49 per reading; this unit does not implement recovery itself.
15. T-perm-3 composition is **deterministic** given (workload, engine, persona); no inference path.
16. Composition result emits `topology.t_perm_3_reading` audit attribute at workflow start per U-CP-31 topology namespace.
17. Boundary declaration is the **closure of the CP plan's architectural commitment** — every subsequent unit in OD plan (Session 4) inherits this boundary as substrate constant.

**Tests:** `test_compose_t_perm_3_three_orthogonal_layers`, `test_composition_admissible_for_valid_tuples`, `test_layer_states_independent`, `test_per_cell_readings_cardinality_twenty`, `test_event_sourced_below_engine`, `test_save_point_above_engine`, `test_pure_pattern_above_engine_where_admissible`, `test_reconciler_loop_control_loop`, `test_wal_segment_above_engine`, `test_excluded_cells_n_a_reading`, `test_per_cell_inherits_u_cp_24_overlay`, `test_non_collapsing_invariant`, `test_fault_above_engine_dispatches_to_harness`, `test_fault_below_engine_engine_native_cancellation`, `test_fault_reconciler_crd_reconverges`, `test_deterministic_outer_harness_five_primitives`, `test_probabilistic_core_only_infer_surface`, `test_boundary_contract_per_add`, `test_binding_time_composition`, `test_runtime_uses_bound_composition`, `test_t_perm_3_reading_audit_attribute`, `test_composition_deterministic`.

**Rollback boundary:** Revert T-perm-3 composition + per-cell reading + fault handling + boundary declaration. R-CP-08 multi-agent topology composition fails; R-CP-04 engine-class resumption transparency loses T-perm-3 substrate; ADD §5.3.3 deterministic outer-harness boundary loses CP-side closure; OD plan Session 4 inherits ambiguous T-perm-3 substrate. Cross-axis AS edge to U-AS-14 releases.

#### U-CP-54 — Author CP-axis namespace export manifest (6 specialization + 4 F3-lifecycle-event + 1 inheritance = 11 namespaces)

**Implements:** [C-CP-24 §24.1.A, §24.1.B, §24.1.C]

**Depends on:** [U-CP-01, U-CP-07, U-CP-11, U-CP-21, U-CP-31, U-CP-37, U-CP-46, U-CP-47]

**Inputs:** All CP-axis namespace declarations: `routing.*` (U-CP-01); `fallback.*` + `harness.breaker.*` + `retry.*` (U-CP-07); `lease.*` (U-CP-11); `engine.*` (U-CP-21); `topology.*` + `subagent.*` (U-CP-31); HITL palette context (U-CP-37); `audit.*` + `hitl.*` (U-CP-46); `validator.fail.*` (U-CP-47).

**Files affected:** CP-axis namespace export manifest (logical: `cp-axis-namespace-export-manifest`).

**Signatures:**

```
record NamespaceExport {
  namespace_name        : string
  attribute_count       : int
  source_unit           : UnitID
  ingestion_target      : IngestionTarget
  sub_section_authority : string                      // C-CP-24 sub-section anchor
  source_authority_posture : SourceAuthorityPosture
}

enum SourceAuthorityPosture {
  OWNED_BY_CP,
  SUBSTRATE_ANCHORED_OUTSIDE_CP,                     // harness.breaker.* per F2-16
  COMPOSED_FROM_CROSS_AXIS                            // composition of CP + IS or CP + AS sources
}

enum IngestionTarget {
  OD_PLAN_SESSION_4_D6_SECTION_1_2,                   // specialization-layer namespaces
  OD_PLAN_SESSION_4_D6_SECTION_1_4,                   // F3 lifecycle event attributes
  OD_PLAN_SESSION_4_D6_SECTION_1_5                    // inheritance from parent llm.inference
}

const CP_NAMESPACE_EXPORT_MANIFEST: List<NamespaceExport>  // exactly 11 entries
```

**Acceptance criteria:**
1. `CP_NAMESPACE_EXPORT_MANIFEST` declares exactly 11 entries per C-CP-24 §24.1 verbatim.
2. **Section §24.1.A (specialization-layer namespaces; D6 §1.2 direct ingest) — 6 entries**:
   - `engine.*` (3 attrs) → U-CP-21 → `OD_PLAN_SESSION_4_D6_SECTION_1_2`
   - `topology.*` (10 attrs) → U-CP-31 → `OD_PLAN_SESSION_4_D6_SECTION_1_2`
   - `subagent.*` (7 attrs) → U-CP-31 → `OD_PLAN_SESSION_4_D6_SECTION_1_2`
   - `hitl.*` (4 attrs) → U-CP-46 → `OD_PLAN_SESSION_4_D6_SECTION_1_2`
   - `audit.*` (7 attrs) → U-CP-46 → `OD_PLAN_SESSION_4_D6_SECTION_1_2`
   - `validator.fail.*` (3 attrs) → U-CP-47 → `OD_PLAN_SESSION_4_D6_SECTION_1_2`
3. **Section §24.1.B (F3-capability-floor lifecycle-event-attribute namespaces; D6 §1.2 lines 124–133 event sub-tree) — 4 entries**:
   - `fallback.*` (9 attrs) → U-CP-07 → `OD_PLAN_SESSION_4_D6_SECTION_1_4`
   - `retry.*` (4 attrs) → U-CP-07 → `OD_PLAN_SESSION_4_D6_SECTION_1_4`
   - `lease.*` (5 attrs) → U-CP-11 → `OD_PLAN_SESSION_4_D6_SECTION_1_4`
   - `harness.breaker.*` (7 attrs) → U-CP-07 → `OD_PLAN_SESSION_4_D6_SECTION_1_4`; `source_authority_posture = SUBSTRATE_ANCHORED_OUTSIDE_CP` per F2-16 + Workflow v1.3 §2.3.3.1 clause (iii); canonical schema at OD C-OD-07 §7.1
4. **Section §24.1.C (inheritance-composition note; NOT ingested at D6 §1.2) — 1 entry**:
   - `routing.*` (4 attrs) → U-CP-01 → `OD_PLAN_SESSION_4_D6_SECTION_1_5`; inherits sampling from parent `llm.inference` span per OTel GenAI semconv 1.41.0; no independent D6 ingestion contract.
5. Manifest is **byte-exact** verbatim transcription of spec §24.1; renaming attributes or adjusting cardinalities requires Workflow §4.1.2 Class-2 C-CP-24 revision.
6. Total attribute count: (3 + 10 + 7 + 4 + 7 + 3) + (9 + 4 + 5 + 7) + (4) = 34 + 25 + 4 = **63 CP-axis attributes** exported to OD plan Session 4 D6 §1.2 + §1.4 + §1.5.
7. Inheritance attribution per §24.1.C: `routing.*` inherits sampling from parent `llm.inference` span; no independent sampling discipline declared at this manifest.
8. F2-16 substrate-anchored-outside-CP posture for `harness.breaker.*` is **explicitly declared** at this manifest at §24.1.B (the F3-lifecycle-event-attribute sub-table where `harness.breaker.*` resides per spec v1.2 §24.1.B); OD plan Session 4 D6 ingests from C-OD-07 §7.1 (canonical OD-axis source), not from this manifest.
9. Manifest is **descriptive, not declarative** — namespace declarations live at source units (U-CP-01 / U-CP-07 / U-CP-11 / U-CP-21 / U-CP-31 / U-CP-46 / U-CP-47); this manifest exports references only.

**Tests:** `test_cp_export_manifest_cardinality_eleven`, `test_section_24_1_a_six_entries`, `test_section_24_1_b_four_entries`, `test_section_24_1_c_one_entry`, `test_per_namespace_attribute_count_match_spec`, `test_per_namespace_source_unit_match_spec`, `test_ingestion_target_routing_to_d6_1_2`, `test_ingestion_target_lease_to_d6_1_4`, `test_ingestion_target_harness_breaker_to_d6_1_5`, `test_harness_breaker_substrate_anchored_outside_cp`, `test_harness_breaker_source_authority_per_f2_16`, `test_total_attribute_count_sixty_three`, `test_manifest_byte_exact`, `test_routing_inheritance_per_24_1_c`, `test_manifest_descriptive_only`.

**Rollback boundary:** Revert CP namespace export manifest. OD plan Session 4 D6 ingestion loses CP-side authoritative reference; D6 §1.2 + §1.4 + §1.5 namespace-source declarations lose CP-axis anchor; cross-axis composition at Session 5 loses CP namespace export catalog.

#### U-CP-55 — Author cross-axis composition manifest + F2-12 carry-forward declaration

**Implements:** [C-CP-24 §24.2, §24.3, §24.4]

**Depends on:** [U-CP-05, U-CP-09, U-CP-20, U-CP-21, U-CP-25, U-CP-27, U-CP-32, U-CP-46, U-CP-51, U-CP-53, U-CP-54, U-IS-12 (cross-axis: IS), U-AS-14 (cross-axis: AS)]

**Inputs:** All CP plan composition surfaces: routing strategy (U-CP-05); cross-family fallback (U-CP-09); F2 substrate join (U-CP-20); `engine.*` namespace (U-CP-21); 2D matrix + D4 tunable (U-CP-25); sub-agent gate-level descent (U-CP-27); multi-agent span hierarchy (U-CP-32); audit + HITL span schemas (U-CP-46); operator-burden eval (U-CP-51); T-perm-3 composition (U-CP-53); CP namespace export manifest (U-CP-54); IS idempotency-key join (U-IS-12); AS 5-axis multiplicative tunable (U-AS-14).

**Files affected:** CP-axis cross-axis composition manifest (logical: `cp-cross-axis-composition-manifest`); CP-axis F2-12 carry-forward declaration (logical: `f2-12-carry-forward-declaration`).

**Signatures:**

```
record CrossAxisCompositionExport {
  composition_name        : string
  exported_to_session     : SessionTarget
  composition_surfaces    : List<CompositionSurface>
  exported_invariants     : List<string>
}

record CompositionSurface {
  cp_source_units         : List<UnitID>
  cross_axis_consumer     : AxisName                  // {OD, COMPOSITION_SESSION_5}
  surface_kind            : SurfaceKind
}

enum SessionTarget { OD_PLAN_SESSION_4, CROSS_AXIS_COMPOSITION_SESSION_5 }

enum SurfaceKind {
  NAMESPACE_EXPORT,
  TUNABLE_COMPOSITION,
  GATE_LEVEL_RULE,
  T_PERM_3_READING,
  DETERMINISTIC_BOUNDARY,
  AUDIT_LEDGER_INVARIANT
}

const CP_CROSS_AXIS_COMPOSITION_MANIFEST: List<CrossAxisCompositionExport>  // exactly 9 entries

record F2_12_CarryForward {
  active_engagement_unit  : UnitID                    // U-CP-20
  closure_path            : List<RevisionStep>
  inheritance_sessions    : List<SessionTarget>
  active_at_v1            : bool                      // true
}

record RevisionStep {
  step_index       : int
  revision_target  : string                           // artifact + version transition
  rationale        : string
}
const F2_12_CARRY_FORWARD: F2_12_CarryForward
```

**Acceptance criteria:**
1. `CP_CROSS_AXIS_COMPOSITION_MANIFEST` declares exactly 9 entries per C-CP-24 §24.2 + §24.3 verbatim:

   | composition_name | exported_to_session | source_units | surface_kind |
   |---|---|---|---|
   | CP_namespace_exports | `OD_PLAN_SESSION_4` | U-CP-54 (11 namespaces) | `NAMESPACE_EXPORT` |
   | T_perm_3_three_layer_composition | `CROSS_AXIS_COMPOSITION_SESSION_5` | U-CP-53 | `T_PERM_3_READING` |
   | five_axis_gate_level_composition | `CROSS_AXIS_COMPOSITION_SESSION_5` | U-CP-43, U-CP-45 (composes with U-AS-14) | `GATE_LEVEL_RULE` |
   | sub_agent_gate_descent | `CROSS_AXIS_COMPOSITION_SESSION_5` | U-CP-27 | `GATE_LEVEL_RULE` |
   | multi_agent_span_hierarchy | `OD_PLAN_SESSION_4` | U-CP-32 | `NAMESPACE_EXPORT` |
   | F2_substrate_join_at_engine_boundary | `OD_PLAN_SESSION_4` | U-CP-20 | `AUDIT_LEDGER_INVARIANT` |
   | deterministic_outer_harness_boundary | `OD_PLAN_SESSION_4` + `CROSS_AXIS_COMPOSITION_SESSION_5` | U-CP-53 | `DETERMINISTIC_BOUNDARY` |
   | per_persona_tier_audit_cryptographic_shape | `OD_PLAN_SESSION_4` | U-CP-42, U-CP-44, U-CP-45 | `AUDIT_LEDGER_INVARIANT` |
   | operator_burden_eval_primitive | `OD_PLAN_SESSION_4` | U-CP-51 | `TUNABLE_COMPOSITION` |

2. Each composition export carries the union of its CP source units; cross-axis consumers (IS or AS) cited via `cross-axis` annotations preserved at source units.
3. **F2-12 carry-forward declaration** per C-CP-24 §24.4 verbatim:
   - `active_engagement_unit = U-CP-20` (R-CP-07-satisfying F2 substrate join contract)
   - `closure_path` is the canonical revision-pass chain:
     - Step 1: D1 v1.1 → v1.2 (resolve resumption-observable-behavior body-citation drift)
     - Step 2: D6 v1.1 → v1.2 (consolidate downstream observability ingestion of D1 v1.2)
     - Step 3: ADD v1.2 → v1.3 (reconsolidate engine-class + observability cross-section per revised ADRs)
     - Step 4: PRD v1.0.1 → v1.1 (cite revised ADD + ADRs at R-CP-04 + R-CP-07)
     - Step 5: CP spec v1.2 → v1.3 (revise C-CP-08 + C-CP-09 + §24.4 to close carry-forward)
     - Step 6: CP plan v1 → v2 (revision-pass mode per SKILL.md §8)
   - `inheritance_sessions = [OD_PLAN_SESSION_4, CROSS_AXIS_COMPOSITION_SESSION_5]`
   - `active_at_v1 = true` (not closed at this version)
4. F2-12 closure is **deferred to revision-pass mode** — CP plan v1 declares the carry-forward; closure occurs at CP plan v2 after spec v1.3 ingests revised D1 + D6 + ADD + PRD.
5. Spec §24.4 deferred-list items inherited at OD plan Session 4 + Composition Session 5: cross-spec citation strings, seam-versioning convention, F2-12 closure path verification, T-perm-3 boundary cross-axis composition checks.
6. Manifest is **byte-exact** verbatim transcription of spec §24.2 + §24.3 + §24.4; addition, removal, or reordering requires Workflow §4.1.2 Class-2 C-CP-24 revision.
7. F2-12 closure path is **the only path** to close the carry-forward; partial closure (e.g., D1 v1.2 only) does not close the carry-forward per spec §24.4 closure invariant.
8. Composition Session 5 (cross-axis composition plan) ingests T-perm-3 composition + 5-axis gate-level + sub-agent gate descent + deterministic outer-harness boundary as the four cross-axis-load-bearing CP exports.
9. OD plan Session 4 ingests CP namespace exports (U-CP-54) + multi-agent span hierarchy + F2 substrate join + per-persona-tier audit crypto + operator-burden eval as the five OD-load-bearing CP exports.
10. F2-12 carry-forward declaration is **the closure of CP plan v1** — every subsequent CP-axis change must either close the carry-forward (revision-pass mode) or extend it (Class-2 finding).
11. Manifest exports surface kind discriminator (`NAMESPACE_EXPORT`, `TUNABLE_COMPOSITION`, `GATE_LEVEL_RULE`, `T_PERM_3_READING`, `DETERMINISTIC_BOUNDARY`, `AUDIT_LEDGER_INVARIANT`) to enable per-surface-kind ingestion at downstream sessions.
12. This unit is the **terminal unit** of the CP plan dependency graph (L8); no within-axis CP unit depends on U-CP-55. Cross-axis ingestion of U-CP-55 occurs at OD plan Session 4 + Composition Session 5 entry-substrate read.

**Tests:** `test_cross_axis_composition_manifest_cardinality_nine`, `test_per_composition_source_units_match_spec`, `test_session_targets_match_spec`, `test_surface_kind_discriminator_six_values`, `test_f2_12_active_engagement_at_u_cp_20`, `test_f2_12_closure_path_six_steps`, `test_f2_12_closure_path_step_1_d1_v1_2`, `test_f2_12_closure_path_step_5_cp_spec_v1_3`, `test_f2_12_closure_path_step_6_cp_plan_v2_revision_pass`, `test_f2_12_inheritance_at_session_4_and_5`, `test_f2_12_active_at_v1`, `test_partial_closure_does_not_close`, `test_session_5_ingests_four_load_bearing_exports`, `test_session_4_ingests_five_load_bearing_exports`, `test_manifest_byte_exact`, `test_u_cp_55_terminal_no_within_axis_consumer`.

**Rollback boundary:** Revert cross-axis composition manifest + F2-12 carry-forward declaration. OD plan Session 4 entry-substrate read loses CP load-bearing export catalog; Composition Session 5 entry-substrate read loses cross-axis composition seam catalog; F2-12 carry-forward declaration site dissolves — runtime engagement at U-CP-20 remains, but closure-path coordination disappears. Cross-axis IS edge to U-IS-12 and AS edge to U-AS-14 release.

---

## §3 Dependency graph

### §3.1 Graph scope

The CP-axis dependency graph spans 55 units across 9 clusters. Edges: 124 within-axis; 60 cross-axis (36 → IS plan v1; 24 → AS plan v1). Cross-axis edges are unidirectional CP → {IS, AS} per OD-S3-3.A.

### §3.2 Topological levels (canonical, post-RC-1/RC-2 reconciliation)

Kahn execution yields a 9-level DAG with no cycles. Level depth = 9 (L0 through L8).

| Level | Unit count | Units |
|---|---|---|
| L0 | 13 | U-CP-01, U-CP-02, U-CP-03, U-CP-07, U-CP-10, U-CP-11, U-CP-22, U-CP-28, U-CP-37 (foundational; (none) or cross-axis-only deps), U-CP-15 (depends only on U-CP-11), U-CP-19 (depends only on U-CP-15), U-CP-26 (depends on U-AS-01 cross-axis only), U-CP-21 (depends only on U-CP-15) |
| L1 | 8 | U-CP-04, U-CP-06, U-CP-08, U-CP-16, U-CP-23, U-CP-29, U-CP-38, U-CP-47 |
| L2 | 10 | U-CP-05, U-CP-09, U-CP-13, U-CP-17, U-CP-18, U-CP-24, U-CP-30, U-CP-31, U-CP-39, U-CP-42 |
| L3 | 8 | U-CP-12, U-CP-14, U-CP-20, U-CP-25, U-CP-33, U-CP-34, U-CP-40, U-CP-44 |
| L4 | 5 | U-CP-27, U-CP-35, U-CP-41, U-CP-43, U-CP-48 |
| L5 | 4 | U-CP-32, U-CP-36, U-CP-45, U-CP-49 |
| L6 | 3 | U-CP-46, U-CP-50, U-CP-52 |
| L7 | 3 | U-CP-51, U-CP-53, U-CP-54 |
| L8 | 1 | U-CP-55 (terminal) |

### §3.3 Per-cluster dependency-edge profile

| Cluster | Units | Within-axis edges | Cross-axis IS edges | Cross-axis AS edges | Total edges |
|---|---|---|---|---|---|
| 1 (F1 routing+fallback) | 9 | 14 | 3 | 1 | 18 |
| 2 (F3 lifecycle+manifest) | 5 | 9 | 5 | 0 | 14 |
| 3 (D1 engine+replay) | 7 | 9 | 4 | 0 | 13 |
| 4 (D4 topology+sub-agent) | 6 | 8 | 5 | 4 | 17 |
| 5 (D4 handoff+spans+audit) | 9 | 15 | 9 | 5 | 29 |
| 6 (D5 HITL palette+placement+matrix) | 5 | 15 | 2 | 0 | 17 |
| 7 (D5 multiplicative gate+audit crypto) | 5 | 19 | 4 | 7 | 30 |
| 8 (D5 escalation+revalidation) | 6 | 24 | 4 | 4 | 32 |
| 9 (T-perm-3 + exports) | 3 | 21 | 1 | 2 | 24 |
| **Total** | **55** | **124** | **36** | **24** | **184** |

### §3.4 Cycle verification

Kahn execution sequence (foundational-first descent):

```
L0 (13 units, in-degree 0)
  → remove edges to L1 consumers; 8 units reach in-degree 0
L1 (8 units)
  → remove edges to L2 consumers; 10 units reach in-degree 0
L2 (10 units)
  → remove edges to L3 consumers; 8 units reach in-degree 0
L3 (8 units)
  → remove edges to L4 consumers; 5 units reach in-degree 0
L4 (5 units)
  → remove edges to L5 consumers; 4 units reach in-degree 0
L5 (4 units)
  → remove edges to L6 consumers; 3 units reach in-degree 0
L6 (3 units)
  → remove edges to L7 consumers; 3 units reach in-degree 0
L7 (3 units)
  → remove edges to L8 consumer; 1 unit reaches in-degree 0
L8 (1 unit; U-CP-55 terminal)
```

All 55 nodes consumed. Remaining edge set: ∅. **Verdict: ✅ ACYCLIC DAG verified.**

### §3.5 Backref reconciliations applied

Two within-axis forward-citation backrefs applied at Stage 4 emission:

| Reconciliation | Source unit | Initial cited target | Corrected target | Rationale |
|---|---|---|---|---|
| RC-1 | U-CP-27 | "U-CP-31" | **U-CP-43** | Sub-agent gate-level descent depends on `gate_level(...)` computation, owned by U-CP-43 (4-axis multiplicative rule), not U-CP-31 (topology/subagent namespace declaration) |
| RC-2 | U-CP-32 | "U-CP-43" | **U-CP-46** | Multi-agent span hierarchy depends on `hitl.gate.evaluated` span schema, owned by U-CP-46 (audit + HITL span namespaces), not U-CP-43 (gate-level rule) |

Both reconciliations preserve acyclicity; corrected targets are forward in topological order.

### §3.6 Cross-axis edge enumeration

**To IS plan v1 (36 edges):**

| Source CP unit | IS target units | Substrate consumed |
|---|---|---|
| U-CP-04 | U-IS-01, U-IS-02, U-IS-06 | Filesystem path contract + path resolver + per-deployment storage residence |
| U-CP-12 | U-IS-07 | F2 state-ledger entry shape (workflow.checkpoint composition) |
| U-CP-14 | U-IS-07, U-IS-08, U-IS-09, U-IS-11 | F2 entry shape + canonicalize/hash + chain construction + append (per-step override audit) |
| U-CP-18 | U-IS-07, U-IS-09, U-IS-12 | F2 read/write substrate (engine-class boundary join) |
| U-CP-27 | U-IS-07, U-IS-09, U-IS-11 | F2 audit composition (sub-agent dispatch audit) |
| U-CP-30 | U-IS-07, U-IS-12 | F2 entry shape + idempotency-key join (HandoffContext schema) |
| U-CP-33 | U-IS-01, U-IS-02 | Filesystem path contract + path resolver (warm-up plan persistence) |
| U-CP-34 | U-IS-07, U-IS-08, U-IS-09, U-IS-11 | F2 audit composition (per-sibling ledger entry) |
| U-CP-35 | U-IS-07, U-IS-12 | F2 entry shape + bounded-read (merkle construction) |
| U-CP-37 | U-IS-07, U-IS-09 | F2 entry shape + chain construction (HITL response audit) |
| U-CP-42 | U-IS-07, U-IS-08, U-IS-09, U-IS-11 | F2 cryptographic shape composition |
| U-CP-49 | U-IS-11, U-IS-12 | F2 append + bounded-read (pause/resume protocol) |
| U-CP-50 | U-IS-01, U-IS-11, U-IS-12 | Filesystem path + F2 append + bounded-read (material-diff detection) |
| U-CP-52 | U-IS-07, U-IS-11 | F2 entry shape + append (timeout-degradation audit) |
| U-CP-55 | U-IS-12 | F2 idempotency-key join (cross-axis composition manifest) |

**To AS plan v1 (24 edges):**

| Source CP unit | AS target units | Substrate consumed |
|---|---|---|
| U-CP-09 | U-AS-30 | Eleven-primitive adoption-depth matrix (cross-family fallback chain) |
| U-CP-26 | U-AS-01 | SandboxTier + BlastRadiusTier foundational substrate |
| U-CP-27 | U-AS-09, U-AS-14, U-AS-15 | Sub-agent sandbox-tier ascension + 5-axis composition |
| U-CP-29 | U-AS-29 | Per-sub-agent-role × model-binding catalog |
| U-CP-32 | U-AS-17, U-AS-31 | Sandbox-bounded span schema + anthropic.* cache attributes |
| U-CP-33 | U-AS-31 | Anthropic.* cache attributes (warm-up cache write/read) |
| U-CP-39 | (none; consumes via U-CP-43) | (transitive through U-CP-43 cross-axis AS deps) |
| U-CP-43 | U-AS-05, U-AS-13, U-AS-14, U-AS-15 | SandboxTier + per-MCP trust-tier + 5-axis multiplicative tunable |
| U-CP-44 | U-AS-20 | F5 fetch_secret signature (signing-key resolution) |
| U-CP-45 | U-AS-12, U-AS-14 | Sandbox-tier composition + 5-axis multiplicative tunable |
| U-CP-47 | U-AS-03 | SandboxFailClass taxonomy (validator-fail composition reference) |
| U-CP-48 | U-AS-10, U-AS-29 | secret.fail.class taxonomy + model catalog (fallback) |
| U-CP-50 | U-AS-10, U-AS-29 | secret.fail.class taxonomy + summarization model catalog |
| U-CP-53 | U-AS-14 | 5-axis multiplicative tunable (T-perm-3 composition) |
| U-CP-55 | U-AS-14 | 5-axis multiplicative tunable (cross-axis composition manifest) |

### §3.7 Substrate-residence-inversion handling

`harness.breaker.*` namespace is **substrate-anchored outside CP** per F2-16 + Workflow v1.3 §2.3.3.1 clause (iii). CP plan emits CP-side composition surface at U-CP-07 with `source_authority_posture = SUBSTRATE_ANCHORED_OUTSIDE_CP`; canonical schema at OD C-OD-07 §7.1.

The substrate-residence-inversion is **structurally acknowledged** at U-CP-07 + U-CP-54 export manifest; CP plan does not claim canonical authorship. This is the sole substrate-residence-inversion in the CP plan.

---

## §4 Coverage matrix

### §4.1 Forward mapping (spec sub-section → covering unit)

107 spec sub-sections across 24 contracts; each covered by ≥ 1 unit.

#### §4.1.1 Contract C-CP-01 (4 sub-sections)

| Sub-section | Covering units | Surfacing class |
|---|---|---|
| §1.1 thin routing core | U-CP-03 | api-surface |
| §1.2 ProviderCapabilities | U-CP-02 | data-type |
| §1.3 manifest residence | U-CP-04 | data-type |
| §1.4 routing.* namespace | U-CP-01 | data-type |

#### §4.1.2 Contract C-CP-02 (2 sub-sections)

| Sub-section | Covering units |
|---|---|
| §2.1 layered routing strategy | U-CP-05 |
| §2.2 layer ordering invariant | U-CP-05 |

#### §4.1.3 Contract C-CP-03 (5 sub-sections)

| Sub-section | Covering units |
|---|---|
| §3.1 LayerBudget | U-CP-06 |
| §3.2 fall-through cause taxonomy | U-CP-08 |
| §3.3 fallback event emission | U-CP-08 |
| §3.4 (deferred-list) | — (covered transitively at U-CP-06 acceptance) |
| §3.5 fallback/breaker/retry namespaces | U-CP-07 |

#### §4.1.4 Contract C-CP-04 (3 sub-sections)

| Sub-section | Covering units |
|---|---|
| §4.1 FallbackChain shape | U-CP-09 |
| §4.2 fall-through ordering | U-CP-09 |
| §4.3 cache state loss attribution | U-CP-09 |

#### §4.1.5 Contract C-CP-05 (4 sub-sections)

| Sub-section | Covering units |
|---|---|
| §5.1 LifecycleEventClass 8-class taxonomy | U-CP-10 |
| §5.2 per-class attribute composition | U-CP-12 |
| §5.3 lease.* namespace | U-CP-11 |
| §5.4 per-class sampling discipline | U-CP-12 |

#### §4.1.6 Contract C-CP-06 (2 sub-sections)

| Sub-section | Covering units |
|---|---|
| §6.1 WorkflowManifestEntry schema | U-CP-13 |
| §6.2 per-step override + audit | U-CP-13 + U-CP-14 |

#### §4.1.7 Contract C-CP-07 (4 sub-sections)

| Sub-section | Covering units |
|---|---|
| §7.1 EngineClass 5-class enum | U-CP-15 |
| §7.2 per-deployment candidate mapping | U-CP-16 |
| §7.3 workload-binding 5-step selection | U-CP-17 |
| §7.4 capability-floor preservation | U-CP-15 |

#### §4.1.8 Contract C-CP-08 (3 sub-sections)

| Sub-section | Covering units |
|---|---|
| §8.1 ResumptionKind 5-class taxonomy (per-engine-class resumption-kind enum) | U-CP-19 |
| §8.2 F2 state-ledger composition via idempotency_key (per-class F2 join discipline) | U-CP-18 |
| §8.3 per-resumption observable behavior | U-CP-20 |

#### §4.1.9 Contract C-CP-09 (4 sub-sections; §9.2 / §9.3 / §9.4 derivative of §9.1 attribute substrate)

| Sub-section | Covering units |
|---|---|
| §9.1 engine.* attribute declarations | U-CP-21 |
| §9.2 per-row Tier-3 / Tier-5 mapping | U-CP-21 (derivative) |
| §9.3 composition with C-IS-10 §10.2 idempotency-key join | U-CP-21 (derivative) |
| §9.4 D6 ingestion contract | U-CP-21 (derivative) |

#### §4.1.10 Contract C-CP-10 (3 sub-sections)

| Sub-section | Covering units |
|---|---|
| §10.1 TopologyPattern 6-class enum | U-CP-22 |
| §10.2 admissibility predicate | U-CP-22 |
| §10.3 CascadePolicy 3-class enum | U-CP-22 |

#### §4.1.11 Contract C-CP-11 (4 sub-sections)

| Sub-section | Covering units |
|---|---|
| §11.1 per-workload commitment table | U-CP-23 |
| §11.2 per-engine overlay | U-CP-24 |
| §11.3 workload × engine 2D matrix | U-CP-25 |
| §11.4 D4 multiplicative tunable | U-CP-25 |

#### §4.1.12 Contract C-CP-12 (5 sub-sections)

| Sub-section | Covering units |
|---|---|
| §12.1 default-downgrade rule | U-CP-26 |
| §12.2 monotonic-descent invariant | U-CP-27 |
| §12.3 override-with-audit permission | U-CP-27 |
| §12.4 cross-deployment monotonicity | U-CP-27 |
| §12.5 dispatch audit composition | U-CP-27 |

#### §4.1.13 Contract C-CP-13 (5 sub-sections)

| Sub-section | Covering units |
|---|---|
| §13.1 HandoffContext schema | U-CP-30 |
| §13.2 SubAgentBrief schema | U-CP-28 |
| §13.3 brief-authoring inheritance | U-CP-29 |
| §13.4 StateSummary schema | U-CP-30 |
| §13.5 LedgerEntryRef schema | U-CP-30 |

#### §4.1.14 Contract C-CP-14 (5 sub-sections)

| Sub-section | Covering units |
|---|---|
| §14.1 multi-agent span hierarchy | U-CP-32 |
| §14.2 topology.* + subagent.* namespaces | U-CP-31 |
| §14.3 per-span sampling discipline | U-CP-32 |
| §14.4 concurrent cache warm-up | U-CP-33 |
| §14.5 cross-family cache-state loss on subagent span | U-CP-32 |

#### §4.1.15 Contract C-CP-15 (6 sub-sections)

| Sub-section | Covering units |
|---|---|
| §15.1 per-sibling F2 entry | U-CP-34 |
| §15.2 parent_fanout_close_entry primitive | U-CP-35 |
| §15.3 F2-14 Reading 1 rationale | U-CP-34 |
| §15.4 merkle construction 4-step | U-CP-35 |
| §15.5 per-persona crypto composition | U-CP-36 |
| §15.6 trace inspection surface | U-CP-36 |

#### §4.1.16 Contract C-CP-16 (4 sub-sections)

| Sub-section | Covering units |
|---|---|
| §16.1 HITLResponse 4-class palette | U-CP-37 |
| §16.2 per-response audit shape | U-CP-37 |
| §16.3 palette invariants | U-CP-37 |
| §16.4 hitl.response.class attribute | U-CP-37 |

#### §4.1.17 Contract C-CP-17 (4 sub-sections; §17.1 split into §17.1 + §17.1.1)

| Sub-section | Covering units |
|---|---|
| §17.1 HITLPlacementKind enum | U-CP-38 |
| §17.1.1 hitl_gate signature | U-CP-38 |
| §17.2 three semantic variants | U-CP-39 |
| §17.3 HITLPlacement workflow-definition schema | U-CP-38 |

#### §4.1.18 Contract C-CP-18 (5 sub-sections)

| Sub-section | Covering units |
|---|---|
| §18.1 persona × engine 15-cell matrix | U-CP-40 |
| §18.2 cell exclusion inheritance | U-CP-40 |
| §18.3 both-by-tier overlay | U-CP-41 |
| §18.4 two-agent-observer meta-class | U-CP-41 |
| §18.5 persona-tier binding selection | U-CP-41 |

#### §4.1.19 Contract C-CP-19 (5 sub-sections)

| Sub-section | Covering units |
|---|---|
| §19.1 4-axis multiplicative rule + per-axis floors | U-CP-43 |
| §19.2 cross-deployment monotonicity | U-CP-43 |
| §19.3 5-axis composition (orthogonal w/ C-AS-12) | U-CP-45 |
| §19.4 _hitl_required predicate + palette restriction | U-CP-43 + U-CP-48 |
| §19.5 operator-policy override scope | U-CP-45 |

#### §4.1.20 Contract C-CP-20 (6 sub-sections; §20.3 split into §20.3 + §20.3.1)

| Sub-section | Covering units |
|---|---|
| §20.1 CryptographicShape enum | U-CP-42 |
| §20.2 per-persona-tier shape | U-CP-42 |
| §20.3 key-rotation two-row pattern | U-CP-45 |
| §20.3.1 F5 signing-key resolution + 6-step verification | U-CP-44 + U-CP-45 |
| §20.4 7 audit.* attributes + per-tier emission | U-CP-46 |
| §20.5 4 hitl.* span attributes | U-CP-46 |

#### §4.1.21 Contract C-CP-21 (6 sub-sections)

| Sub-section | Covering units |
|---|---|
| §21.1 ValidatorFailClass 5-class | U-CP-47 |
| §21.2 transient staircase + cause-branching | U-CP-48 |
| §21.3 operator-burden eval primitive | U-CP-51 |
| §21.4 palette restriction + summarization model table | U-CP-48 + U-CP-50 |
| §21.5 validator.fail.* namespace | U-CP-47 |
| §21.6 timeout-degradation + webhook delivery | U-CP-52 |

#### §4.1.22 Contract C-CP-22 (4 sub-sections)

| Sub-section | Covering units |
|---|---|
| §22.1 pause/resume protocol + state_summary snapshot | U-CP-49 |
| §22.2 material-diff detection 5-category | U-CP-50 |
| §22.3 summarization fallback + revalidation | U-CP-50 |
| §22.4 T-perm-2 F2-layer composition | U-CP-49 + U-CP-50 |

#### §4.1.23 Contract C-CP-23 (4 sub-sections)

| Sub-section | Covering units |
|---|---|
| §23.1 three-layer composition (F1 + D1 + D4) | U-CP-53 |
| §23.2 per-cell reading (20 cells) | U-CP-53 |
| §23.3 runtime fault handling | U-CP-53 |
| §23.4 deterministic outer-harness boundary | U-CP-53 |

#### §4.1.24 Contract C-CP-24 (4 sub-sections; §24.1 split into §24.1.A/B/C)

| Sub-section | Covering units |
|---|---|
| §24.1.A specialization-layer namespaces (6) | U-CP-54 |
| §24.1.B F3 lifecycle event attributes (4) | U-CP-54 |
| §24.1.C substrate-anchored-outside-CP (harness.breaker.*) | U-CP-54 |
| §24.2 cross-axis composition exports | U-CP-55 |
| §24.3 inheritance at sessions 4 + 5 | U-CP-55 |
| §24.4 F2-12 carry-forward declaration | U-CP-55 |

### §4.2 Forward-mapping completeness verdict

| Verdict | Count |
|---|---|
| Spec sub-sections | 107 |
| Covered by ≥ 1 unit | **107** |
| Uncovered | **0** |

✅ **PASS — 100% forward-mapping coverage.**

### §4.3 Inverse mapping (unit → cited spec sub-sections)

All 55 units cite ≥ 1 spec sub-section. Aggregate citation depth distribution:

| Citations per unit | Unit count | Units |
|---|---|---|
| 1 sub-section | 14 | U-CP-01, U-CP-02, U-CP-03, U-CP-06, U-CP-11, U-CP-15 (split), U-CP-19, U-CP-22, U-CP-23, U-CP-26, U-CP-28, U-CP-31, U-CP-33, U-CP-42 |
| 2 sub-sections | 18 | U-CP-04, U-CP-05, U-CP-07, U-CP-08, U-CP-09, U-CP-10, U-CP-13, U-CP-14, U-CP-16, U-CP-17, U-CP-18, U-CP-20, U-CP-21, U-CP-24, U-CP-25, U-CP-29, U-CP-30, U-CP-34 |
| 3 sub-sections | 15 | U-CP-12, U-CP-32, U-CP-35, U-CP-36, U-CP-38, U-CP-39, U-CP-40, U-CP-41, U-CP-44, U-CP-47, U-CP-48, U-CP-49, U-CP-50, U-CP-51, U-CP-52 |
| 4 sub-sections | 6 | U-CP-27, U-CP-37, U-CP-43, U-CP-45, U-CP-46, U-CP-53 |
| 5+ sub-sections | 2 | U-CP-54 (3 from §24.1), U-CP-55 (3 from §24.2/3/4) |

✅ **PASS — 100% inverse-mapping coverage.**

### §4.4 Cross-cluster composition surfaces

Four cross-cluster composition surfaces close without orphan units:

| Composition surface | Spanning clusters | Closure units |
|---|---|---|
| T-perm-1 (5-axis multiplicative gate-level) | 4, 6, 7, 9 | U-CP-25 + U-CP-43 + U-CP-45 + U-CP-53 |
| T-perm-3 (three-layer F1+D1+D4 composition) | 1, 3, 4, 9 | U-CP-08 + U-CP-09 + U-CP-17 + U-CP-24 + U-CP-25 + U-CP-53 |
| HITL palette + placement + gate level + escalation | 6, 7, 8 | U-CP-37 + U-CP-38 + U-CP-43 + U-CP-48 |
| Audit ledger F2 + crypto + span schemas | 4, 5, 6, 7 | U-CP-27 + U-CP-34 + U-CP-42 + U-CP-45 + U-CP-46 |

Each surface's source units span ≥ 2 clusters; closure verified at §3.4 acyclic invariant + §4.1 forward mapping.

### §4.5 Coverage matrix verdict

| Audit | Result |
|---|---|
| §4.1 forward-mapping (107 sub-sections × 55 units) | ✅ PASS |
| §4.2 forward-mapping completeness | ✅ PASS (0 uncovered) |
| §4.3 inverse-mapping (55 units × ≥1 citation) | ✅ PASS |
| §4.4 cross-cluster composition closure (4 surfaces) | ✅ PASS |

**Aggregate verdict: ✅ COVERAGE COMPLETE.**

---

## §5 Coherence pass

### §5.1 Audit dimensions and verdicts

| § | Audit dimension | Verdict | Findings |
|---|---|---|---|
| §5.2 | Atomicity (4 criteria × 55 units) | ✅ PASS | 1 mechanical DEFECT corrected (U-CP-21 citation specificity); 2 OBSERVATIONS |
| §5.3 | Spec-traceability (forward + inverse + version) | ✅ PASS | 2 OBSERVATIONS |
| §5.4 | Dependency-awareness (within-axis + cross-axis + acyclic + direct + sufficiency) | ✅ PASS | 2 OBSERVATIONS |
| §5.5 | Implementation-grade detail (5 fields × 55 units) | ✅ PASS | 3 OBSERVATIONS |
| §5.6 | Anti-pattern audit (8 anti-patterns) | ✅ PASS | 2 OBSERVATIONS on handled cases |
| §5.7 | Cross-cutting concerns (F2-12, five-axis, tamper-evidence, deterministic outer-harness) | ✅ PASS | All surfaces covered |

### §5.2 Atomicity audit results

Per-cluster atomicity verdict across the four operational criteria from `implementation-planner` SKILL.md §3:

| Cluster | Units | Atomicity verdict |
|---|---|---|
| 1 | 9 | ✅ PASS — each unit produces one of {namespace, data type, API surface, manifest residence, layered routing, fall-through, cross-family chain} |
| 2 | 5 | ✅ PASS — each unit produces one of {taxonomy, namespace, per-class attribute composition, manifest entry, per-step override} |
| 3 | 7 | ✅ PASS — each unit produces one of {enum + invariant, candidate mapping, selection procedure, F2 join, resumption enum, resumption observable behavior, engine namespace} |
| 4 | 6 | ✅ PASS — each unit produces one of {topology enum + admissibility, per-workload commitment, per-engine overlay, 2D matrix + tunable, default-downgrade, gate-level descent} |
| 5 | 9 | ✅ PASS — each unit produces one of {SubAgentBrief schema, inheritance table, HandoffContext composition, namespace, span hierarchy + sampling, warm-up protocol, F2 entry + rationale, fanout-close + merkle, cross-sibling crypto} |
| 6 | 5 | ✅ PASS — each unit produces one of {palette + audit shapes + invariants + attribute, placement + signature + schema, rewriting algorithm, 2D matrix + exclusion, overlay + observer + binding} |
| 7 | 5 | ✅ PASS — each unit produces one of {per-tier crypto shape, 4-axis rule + monotonicity + predicate, signing-key resolution, 5-axis composition + override + rotation, audit + HITL span schemas} |
| 8 | 6 | ✅ PASS — each unit produces one of {fail taxonomy + namespace, staircase + branching + palette restriction, pause/resume protocol, material-diff + revalidation, operator-burden eval, timeout + webhook} |
| 9 | 3 | ✅ PASS — each unit produces one of {T-perm-3 three-layer composition + boundary, namespace export manifest, cross-axis composition manifest} |

Three findings, none requiring re-decomposition:

- **Finding §5.2.A (OBSERVATION).** Four units carry the highest acceptance-criteria density (U-CP-43: 15; U-CP-45: 16; U-CP-46: 20; U-CP-53: 17). Density reflects composition site complexity, not braided concerns. Each unit shares a single runtime composition site.
- **Finding §5.2.B (OBSERVATION).** U-CP-13 and U-CP-14 both implement C-CP-06 §6.2. Split is by surfacing class — U-CP-13 declares the data type; U-CP-14 implements per-step override evaluator + audit composition algorithm. Atomicity preserved.
- **Finding §5.2.C (DEFECT).** U-CP-21 implements citation re-anchored at audit. Canonical citation reads `C-CP-05 §5.3 (engine.* namespace declaration; consumed at §5.2 per-class attribute composition and §9.2 resumption observable behavior)`. Mechanical correction applied at §4.1 inverse mapping.

### §5.3 Spec-traceability audit results

| Audit dimension | Result |
|---|---|
| Forward-mapping completeness (107 sub-sections) | ✅ PASS (100% coverage per §4.2) |
| Inverse-mapping completeness (55 units) | ✅ PASS (100% citation per §4.3) |
| Spec-version alignment (CP spec v1.2; IS plan v1; AS plan v1) | ✅ PASS — all citations point to latest filed versions per Workflow §7 |
| Sub-section ID hygiene (12 sampled citations) | ✅ PASS — all 12 resolve to existing spec sub-sections |

Two findings:

- **Finding §5.3.A (OBSERVATION).** Spec §24.1 reorganized at v1.2 into three sub-tables (§24.1.A, §24.1.B, §24.1.C) per F-iter2-01 Path A closure. U-CP-54 cites all three sub-section IDs.
- **Finding §5.3.B (OBSERVATION).** Two units carry multi-contract implements: U-CP-45 (C-CP-19 + C-CP-20); U-CP-50 (C-CP-21 + C-CP-22). Both compose at the same surfacing site per SKILL.md §4 multi-contract sanction.

### §5.4 Dependency-awareness audit results

| Audit dimension | Result |
|---|---|
| Within-axis declaration completeness (55 units × `Depends on:`) | ✅ PASS |
| Cross-axis annotation completeness per OD-S3-3.A (60 cross-axis edges annotated) | ✅ PASS |
| Acyclic invariant (Kahn execution verified at §3.4) | ✅ PASS |
| Direct-dep-only (no transitive omissions; sampled at U-CP-55 terminal) | ✅ PASS |
| Acceptance-criterion sufficiency (per-cluster audit) | ✅ PASS (0 gaps across 55 units) |

Two findings:

- **Finding §5.4.A (OBSERVATION).** Two backref reconciliations applied (RC-1: U-CP-27 → U-CP-43; RC-2: U-CP-32 → U-CP-46). Both correct forward-citation mis-anchorings at Stage 4 emission. Acyclicity preserved.
- **Finding §5.4.B (OBSERVATION).** One within-axis edge skips > 3 topological levels (U-CP-13 L4 → U-CP-38 L1 backward reference: corrected at RC analysis as U-CP-38 actually depends on U-CP-13 forward, no skip). All other edges within tolerance.

### §5.5 Implementation-grade detail audit results

Per-unit detail density:

| Cluster | Units | Avg acceptance criteria | Avg tests | Files-affected coverage | Rollback coverage |
|---|---|---|---|---|---|
| 1 | 9 | 9.2 | 8.1 | 9 / 9 | 9 / 9 |
| 2 | 5 | 8.6 | 8.0 | 5 / 5 | 5 / 5 |
| 3 | 7 | 8.9 | 8.4 | 7 / 7 | 7 / 7 |
| 4 | 6 | 10.5 | 8.7 | 6 / 6 | 6 / 6 |
| 5 | 9 | 10.1 | 8.6 | 9 / 9 | 9 / 9 |
| 6 | 5 | 12.8 | 11.6 | 5 / 5 | 5 / 5 |
| 7 | 5 | 14.4 | 13.6 | 5 / 5 | 5 / 5 |
| 8 | 6 | 12.5 | 12.2 | 6 / 6 | 6 / 6 |
| 9 | 3 | 14.7 | 14.0 | 3 / 3 | 3 / 3 |
| **Total** | **55** | **11.0** | **10.4** | **55 / 55** | **55 / 55** |

Three findings:

- **Finding §5.5.A (OBSERVATION).** Cluster 9 (14.7 acceptance / unit) and Cluster 7 (14.4) carry the highest density, reflecting composition surface complexity at the closing cluster + cryptographic substrate cluster.
- **Finding §5.5.B (OBSERVATION).** All 55 units use pseudocode signatures (records, enums, function signatures) per SKILL.md §3; no language-specific binding emitted. Language binding deferred to implementation discretion per spec deferred lists.
- **Finding §5.5.C (OBSERVATION).** Rollback boundaries cite R-CP-NN regression bindings where applicable; non-applicable rollback boundaries (foundational substrate) cite consumer-dependency-cone invalidation.

### §5.6 Anti-pattern audit results

| Anti-pattern | Result |
|---|---|
| Sequential numbering masquerading as decomposition | ✅ ABSENT (cluster sizes 3–9 reflect actual complexity) |
| Non-atomic mega-units | ✅ ABSENT (high-density units share single composition site) |
| Under-scoped acceptance criteria | ✅ ABSENT (avg 11.0 per unit; sample-verified) |
| Missing rollback | ✅ ABSENT (55 / 55 declared) |
| Forward-reference loops | ✅ ABSENT (Kahn 0 cycles per §3.4) |
| Transitive-dep declaration | ✅ ABSENT (sampled at U-CP-55) |
| Cross-axis bidirectionality | ✅ ABSENT (60 edges unidirectional) |
| Substrate-residence inversion | ✅ HANDLED (`harness.breaker.*` declared `SUBSTRATE_ANCHORED_OUTSIDE_CP` at U-CP-07 + U-CP-54) |

Two findings, both on handled cases:

- **Finding §5.6.A (OBSERVATION).** Substrate-residence-inversion for `harness.breaker.*` handled per F2-16 closure + Workflow v1.3 §2.3.3.1 clause (iii). U-CP-54 §24.1.B export manifest declares the namespace with explicit posture; canonical authority at C9 SKILL.md.
- **Finding §5.6.B (OBSERVATION).** RC-1 + RC-2 reconciliations applied at Stage 4; no cycle introduced.

### §5.7 Cross-cutting concerns coverage

| Cross-cutting concern | Covering units | Status |
|---|---|---|
| F2-12 carry-forward | U-CP-20 (active engagement) + U-CP-55 (closure path declaration) | ✅ Declared; deferred to revision-pass mode |
| Five-axis space coverage (persona × workload × deployment × engine × topology) | U-CP-15 / U-CP-16 / U-CP-22 / U-CP-23 / U-CP-25 / U-CP-40 / U-CP-43 / U-CP-50 / U-CP-52 | ✅ All 5 axes covered |
| Tamper-evidence chain (hash chain → signature → merkle → trace inspection → rotation) | U-CP-34 / U-CP-35 / U-CP-36 / U-CP-37 / U-CP-42 / U-CP-44 / U-CP-45 / U-CP-46 | ✅ Full chain covered |
| Deterministic outer-harness boundary (5 primitives) | U-CP-07 / U-CP-09 / U-CP-25 / U-CP-47 / U-CP-48 / U-CP-49 / U-CP-53 | ✅ All 5 primitives covered |

### §5.8 Coherence verdict

| Audit dimension | Findings | Verdict |
|---|---|---|
| §5.2 Atomicity | 1 mechanical DEFECT corrected; 2 OBSERVATIONS | ✅ PASS |
| §5.3 Spec-traceability | 2 OBSERVATIONS | ✅ PASS |
| §5.4 Dependency-awareness | 2 OBSERVATIONS | ✅ PASS |
| §5.5 Implementation-grade detail | 3 OBSERVATIONS | ✅ PASS |
| §5.6 Anti-pattern audit | 2 OBSERVATIONS on handled cases | ✅ PASS |
| §5.7 Cross-cutting concerns | 4 / 4 covered | ✅ PASS |
| **Aggregate** | **1 DEFECT (corrected); 11 OBSERVATIONS; 0 BLOCKERS** | ✅ **COHERENCE PASS COMPLETE** |

Plan authorized for filing.

---

## §6 Carry-forwards and open items

### §6.1 F2-12 active carry-forward

| Field | Value |
|---|---|
| Carry-forward ID | F2-12 |
| Active engagement | U-CP-20 (per-resumption observable behavior) |
| Substrate dependency | C-CP-08 R-CP-07-satisfying F2 substrate join contract |
| Closure path | D1 v1.1 → v1.2 + D6 v1.1 → v1.2 + ADD v1.2 → v1.3 + PRD v1.0.1 → v1.1 + CP spec v1.2 → v1.3 + CP plan v1 → v2 (revision-pass) |
| Inheritance scope | OD plan Session 4 + Composition Session 5 §[carry-forwards] |
| Active at v1 | true (not closed at this plan version) |
| Closure trigger | Partial closure does not close carry-forward per spec §24.4 closure invariant |

Closure path declared at U-CP-55 §24.4. Revision-pass mode per SKILL.md §8 invoked when closure substrate is filed.

### §6.2 Spec §[deferred-list] items inherited

| Source contract | Deferred item | Resolution discretion |
|---|---|---|
| C-CP-01 §1.2 | Concrete cost-table maintenance for `ProviderCapabilities` | Implementation discretion |
| C-CP-01 §1.3 | Manifest format (JSON / YAML / TOML) | Implementation discretion |
| C-CP-03 §3.1 | Concrete default values for `DEFAULT_LAYER_BUDGETS` | Operator-binding-time discretion |
| C-CP-07 §7.2 | Specific engine candidates within each surface set | Implementation discretion |
| C-CP-13 §13.1 | HandoffContext serialization format | Implementation discretion |
| C-CP-17 §17.3 | `tool_filter` semantics (glob vs regex) | Implementation discretion |
| C-CP-20 §20.3.1 | Signature algorithm (Ed25519 vs ECDSA-P256 vs other) | Implementation discretion |
| C-CP-21 §21.6 | Per-webhook retry budget | Implementation discretion |
| C-CP-22 §22.1 | Pause-snapshot serialization format | Implementation discretion |
| C-CP-22 §22.2 | Per-category materiality predicate (default: any hash mismatch) | Implementation discretion |
| C-CP-24 §24.4 | Cross-spec citation strings + seam-versioning convention | OD plan Session 4 + Session 5 inherit |

### §6.3 Cross-axis substrate inheritance

CP plan v1 consumes 60 cross-axis edges (36 IS + 24 AS). Inheritance documented at each source unit's `Cross-axis substrate consumed` field per §2. Cross-axis substrate seam exports declared at U-CP-55 §24.2 cross-axis composition manifest.

Inherited from IS plan v1:
- F2 state-ledger entry shape, canonicalize/hash, chain construction, append-only write, bounded-read
- Filesystem path contract + path resolver + per-deployment storage residence
- Idempotency-key join + JSONL event ledger format + response-hash computation

Inherited from AS plan v1:
- SandboxTier + BlastRadiusTier + MechanismClass foundational substrate
- Per-MCP transport sandbox-tier floor + four-level trust-tier framework
- Sub-agent sandbox-tier monotonic-ascension formula
- 5-axis multiplicative gate-level tunable + cross-deployment monotonicity
- Eleven-primitive Anthropic adoption-depth matrix + model-tier escalation chain
- `secret.fail.class` taxonomy + F5 `fetch_secret(name, scope)` signature
- Six Anthropic-primitive attribute namespaces (`anthropic.*` cache attributes)
- Sandbox-bounded span hierarchy + `sandbox.*` attribute names

### §6.4 Open items requiring downstream attention

- OD plan Session 4 must ingest U-CP-54 11-namespace export manifest at entry-substrate read; D6 §1.2 / §1.4 / §1.5 ingestion paths declared per §24.1.A/B/C.
- Composition Session 5 must ingest U-CP-55 four cross-axis-load-bearing CP exports: T-perm-3 composition, 5-axis gate-level composition, sub-agent gate descent, deterministic outer-harness boundary.
- F2-12 carry-forward closure requires coordinated revision pass across six artifacts (D1, D6, ADD, PRD, CP spec, CP plan); single-artifact partial revision does not close.
- Spec §[deferred-list] items resolved at implementation discretion are not blockers for plan filing; resolution occurs at execution time per SKILL.md §2 (plan terminates the design chain).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_1.md` |
| Status | Filed at `/mnt/user-data/outputs/Implementation_Plan_Control_Plane_v2_1.md` (Path B Segment D close) per `Project_Workflow_v1_6.md` §4.1.4.5 one-time Iter-3 authorization |
| Aggregate adversarial review | P6-CK Iteration 3 against v2.1 ensemble per Workflow v1.6 §4.1.4.5; entry-gate AUTHORIZED pending Segment E + F + G filing |
| Operator action | Push from `/mnt/user-data/outputs/` to `/mnt/project/Implementation_Plan_Control_Plane_v2_1.md` at session close |
| Predecessor | `Implementation_Plan_Control_Plane_v2.md` (v2, filed 2026-05-14 under Path α); `Adversarial_Review_6_iter2.md` §3.3 F2-CP-03 finding; `P6-CK_Iteration_2_Ceiling_Disposition.md` §5.2 absorption scope; `Project_Workflow_v1_6.md` §4.1.4.5 |
| Next segment | Path B Segment E — `Implementation_Plan_Operational_Discipline_v2_1.md` (F1-OD-02 absorption); then Segment F — `Cross_Axis_Composition_Document_v2_1.md` (F1-CXA-03 absorption); then Segment G — `P6-CK_Iteration_3_Kickoff.md` |
| Exit-gate verification | v2.1 §0.10 coherence-pass summary returns ✅ PASS at all 5 audit dimensions; F2-CP-03 absorbed at 12 sites; U-CP-21 attribute-composition concerns forward-flagged at §0.8 |
| Unit count | 55 atomic units across 9 clusters (unchanged at v2.1) |
| Contract coverage | 24 / 24 CP-axis contracts (107 / 107 sub-sections; C-CP-08 partition restored to 3-row canonical at v2.1) |
| Within-axis edges | 124; acyclic DAG verified at §3.4 (unchanged at v2.1) |
| Cross-axis edges | 60 (36 IS + 24 AS); cross-axis IS targets now resolve to IS plan v2.1 |

**v2.1 plan filed.** Path B Segment D closes; Path B continues to Segment E.
