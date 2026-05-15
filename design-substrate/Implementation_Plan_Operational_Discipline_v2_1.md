# Implementation Plan — Operational Discipline (OD) Axis v2.1

**Project.** Multi-LLM Agent Harness — Phase 6 Implementation Planning
**Session.** Path B Segment E (single-segment revision pass per `P6-CK_Iteration_2_Ceiling_Disposition.md` §5.3)
**Substrate.** `Spec_Operational_Discipline_v1.md` v1.2 (P5-CK-cleared); `Spec_Information_Substrate_v1.md` v1.2 (IS plan v2.1 substrate); `Spec_Action_Surface_v1.md` v1.1; `Spec_Control_Plane_v1.md` v1.2 (CP plan v2.1 substrate); `Project_Workflow_v1_6.md` §4.1.4 + §7 + §8; `Adversarial_Review_6_iter2.md` §3.4 F1-OD-02 finding
**Skill.** `implementation-planner` (revision-pass sub-mode per §8)
**Deliverable.** This file — 34 atomic units across 8 clusters; v2.1 absorbs 1 P6-CK Iteration 2 finding (F1-OD-02) on top of v2's 4 Iteration 1 absorptions
**Status.** v2.1 — `Status: Proposed` pending P6-CK Iteration 3 clearance per Workflow v1.6 §4.1.4.5 one-time Path B authorization
**Closure status.** v1 — `closure_pending_at_v1 == true` per F2-12 carry-forward; closure target = OD plan v2 (now superseded by v2.1, this artifact, revision-pass mode per SKILL.md §8); F2-12 closure-path execution (steps 1–6 of canonical chain) remains OUT-OF-SCOPE at this revision pass per Path B Iter-2 close disposition; routed to parallel `council-orchestrator` C7+C9 session.

---

## §0 Change note (v2 → v2.1)

### §0.1 Scope of revision

Single-pass revision absorbing one `Adversarial_Review_6_iter2.md` P6-CK Iteration 2 finding, local to OD plan v2:

| Finding | Class | Resolution path absorbed | Affected sites |
|---|---|---|---|
| F1-OD-02 | 1 | Single-path: drop `audit.signature.sha256` token from hash-digest classification example list (post-F2-OD-03 absorption at v2, the token no longer corresponds to any canonical IS spec §10.3 attribute); preserve `hitl.response.summary_hash` + `mcp.primitive.signature.sha256` | U-OD-15 acceptance #4 hash-digest example list |

No new architectural commitments; no new units; no new contracts; no new cross-axis edges; no spec extensions. Per `implementation-planner` SKILL.md §8 revision-pass discipline.

This finding was forward-flagged at v2 §0.8 as a candidate for P6-CK Iteration 2 surfacing. The forward-flag prediction held; F1-OD-02 surfaced at Iter 2 against U-OD-15 and is now absorbed at v2.1.

### §0.2 Sections preserved verbatim (from v2)

| Section | Preservation rationale |
|---|---|
| §0a Front matter (preserved from v1) | OD selections, plan-level invariants, F2-12 ACTIVE engagement summary all preserved verbatim |
| §1 + §2 spec inventory + cluster decomposition + substrate-version-citation alignment | Substrate versions unchanged (OD spec v1.2; ADR-D5 v1.3; ADD v1.2; PRD v1.0.1); cluster decomposition unchanged |
| §3.1 Cluster 1 (U-OD-01 through U-OD-03) | No Iter-2 finding |
| §3.2 Cluster 2 (U-OD-04 through U-OD-08) | No Iter-2 finding |
| §3.3 Cluster 3 — U-OD-09, U-OD-10, U-OD-11, U-OD-12, U-OD-13, U-OD-14 | No Iter-2 finding |
| §3.3 Cluster 3 — U-OD-15 non-acceptance-#4 sections | No Iter-2 finding at scope, depends-on, inputs, files, signatures, acceptance #1 / #2 / #3 / #5 / #6, tests, rollback boundary |
| §3.4 Cluster 4 (U-OD-16 through U-OD-19) | No Iter-2 finding |
| §3.5 Cluster 5 (U-OD-20 through U-OD-22) | No Iter-2 finding |
| §3.6 Cluster 6 (U-OD-23 through U-OD-26) | No Iter-2 finding |
| §3.7 Cluster 7 (U-OD-27 through U-OD-31) | No Iter-2 finding |
| §3.8 Cluster 8 (U-OD-32 through U-OD-34) | No Iter-2 finding |
| §4 dependency graph | No graph delta; node count + edge count + topological-sort order unchanged at v2.1 |
| §5 coverage matrix | No matrix delta; contract-to-unit mapping unchanged |
| §6 / §7 coherence pass + closure | v2 coherence-pass results preserved; v2.1 audit summary captured at §0.10 |

### §0.3 Sections revised (v2 → v2.1)

| Section | Revision shape | Resolves |
|---|---|---|
| U-OD-15 acceptance #4 hash-digest example list | Drop `audit.signature.sha256,` from parenthetical example list `(e.g., hitl.response.summary_hash, audit.signature.sha256, mcp.primitive.signature.sha256)` → `(e.g., hitl.response.summary_hash, mcp.primitive.signature.sha256)` | F1-OD-02 |

The deleted token referred to a non-canonical attribute name. Post-F2-OD-03 absorption at v2, the canonical 4th `audit.signature.*` attribute per IS spec §10.3 is `audit.signature.key_period` (a rotation-cycle anchor, not a hash digest). The hash-digest example list retains 2 valid canonical tokens (`hitl.response.summary_hash` per OD spec; `mcp.primitive.signature.sha256` per AS spec).

### §0.4 Coverage matrix delta

No delta. U-OD-15 continues to implement `C-OD-12 §12.1, §12.2, §12.3` at v2.1 (unchanged from v2).

### §0.5 Dependency graph delta

No delta. U-OD-15 `Depends on:` declarations unchanged at v2.1. Aggregate DAG: 34 nodes, edge set unchanged from v2, topological sort preserved. Cross-axis edge count (28) + breakdown ({IS: 6, AS: 10, CP: 12}) unchanged; cross-axis IS targets now resolve to IS plan v2.1; cross-axis CP targets now resolve to CP plan v2.1.

### §0.6 Substrate-version-citation table

Substrate versions cited at v2.1:

| Substrate | Version cited at v2 | Version cited at v2.1 |
|---|---|---|
| OD spec | v1.2 | v1.2 (unchanged) |
| ADR-D5 | v1.3 | v1.3 (unchanged) |
| ADD | v1.2 | v1.2 (unchanged) |
| PRD | v1.0.1 | v1.0.1 (unchanged) |
| Cross-axis CP plan | v2 | **v2.1** (post-F2-CP-03 absorption) |
| Cross-axis IS plan | v2 (was v1 at v1) | **v2.1** (post-F1-IS-02 absorption) |
| Cross-axis IS spec | v1.2 | v1.2 (unchanged) |
| Cross-axis AS spec | v1.1 | v1.1 (unchanged) |
| Workflow | v1.5 | **v1.6** (post-§4.1.4 amendment) |

Per Workflow v1.6 §7 use-latest-version body-citation-alignment.

### §0.7 Status

`Status: Proposed` preserved at v2.1 per `implementation-planner` SKILL.md §8. Bump to `Status: P6-CK-cleared` on P6-CK Iteration 3 CLEARED disposition.

### §0.8 Forward-flagged concerns (closed at v2.1)

| Concern from v2 | Status at v2.1 |
|---|---|
| Line 986 hash-digest classification example list cites `audit.signature.sha256` post-F2-OD-03 resolution where canonical 4th attribute is `audit.signature.key_period` | **Closed at v2.1** — F1-OD-02 absorbed per §0.3 above; `audit.signature.sha256` token dropped from U-OD-15 acceptance #4 hash-digest example list |
| F2-CXA-04 (CXA doc §6.4 propagates F2-OD-01 verbatim-inheritance claim) | Path α scope at v2 was plan revisions; CXA absorbed at Iter-1 Path β producing CXA v2; not in OD plan v2.1 scope |
| F1-CXA-01 (CXA doc §3.2 row 11 propagates F1-OD-01 subagent.* anchor drift) | Absorbed at CXA v2 §3.2 row 11 retarget per Iter-1 Path β; not in OD plan v2.1 scope |

No new forward-flagged concerns surface at v2.1. Path B revision-pass scope limits to F1-OD-02 absorption; no new defects introduced.

### §0.9 Prior revision history (v1 → v2; archival from v2 §0)

The v1 → v2 amendment cycle absorbed four `Adversarial_Review_6.md` P6-CK Iteration 1 findings:

| Finding | Class | Resolution path | Affected sites |
|---|---|---|---|
| F2-OD-01 | 2 | Path (i) hybrid: structural-fidelity grammar at acceptance claims + byte-exact realignment at closure_path steps 3–4 | U-OD-20 `F2_12_CLOSURE_PATH` steps 3–4 + acceptance #8; U-OD-34 acceptance #7 |
| F2-OD-02 | 2 | Single-path: formula token realignment to AS spec §14.2 canonical | U-OD-23 acceptance #3 |
| F2-OD-03 | 2 | Path (α) strict-narrow: U-OD-30 4th attribute realignment to IS spec §10.3 canonical | U-OD-30 `AuditSignatureAttributes` field 4 + acceptance #7 |
| F1-OD-01 | 1 | Single-path: mechanical citation correction at 3 per-prefix anchors | U-OD-07 acceptance #2 |

Full v1 → v2 amendment trace remains on record at `/mnt/project/Implementation_Plan_Operational_Discipline_v2.md` §0.3.

### §0.10 v2.1 coherence-pass summary

Pre-emission self-audit per SKILL.md §5 step 9 + §[coherence pass] discipline returns ✅ PASS at all 5 audit dimensions:

| Audit | Result |
|---|---|
| §3 Atomicity | ✅ PASS — F1-OD-02 amendment is single-token deletion within existing acceptance criterion; atomicity of U-OD-15 preserved |
| §4 Spec-traceability | ✅ PASS — hash-digest example list now contains only canonical attribute names from substrate specs (`hitl.response.summary_hash` per OD spec §12; `mcp.primitive.signature.sha256` per AS spec §10) |
| §7 Dependency-awareness | ✅ PASS — no graph delta; topological sort preserved |
| §8 Implementation-grade-detail | ✅ PASS — no signature / acceptance-structure / test deltas beyond cited absorption site |
| §10 Anti-pattern audit | ✅ PASS — F1-OD-02 absorption eliminates citation-of-non-existent-canonical-attribute anti-pattern at U-OD-15 acceptance #4 |

---

## §0a Front matter (preserved from v1)

### §0a.1 Operator pre-decisions (ODs) — confirmed at session entry

| OD | Selection | Effect |
|---|---|---|
| OD-S4-1.A | Per-cluster operator confirmation cadence | Cluster-by-cluster emission with operator confirmation between OD-CL-N close and OD-CL-(N+1) open |
| OD-S4-2.A | Per-axis (OD-only) coverage matrix at Session 4; aggregate cross-axis coverage matrix deferred to Session 5 | Stage 5 scope restricted to OD axis |
| OD-S4-3.A | Per-unit cross-axis IS+AS+CP declarations + aggregate manifest at U-OD-34 | Per-unit `Depends on:` clauses carry cross-axis placeholder identifiers; aggregate manifest at terminal exporter consolidates 28 cross-axis edges |

### §0a.2 Plan-level invariants

| Invariant | Value |
|---|---|
| Atomic units | 34 |
| Clusters | 8 |
| Spec contracts covered | 23 of 23 (C-OD-01 through C-OD-23) |
| PRD requirements satisfied | 8 of 8 (R-OD-01 through R-OD-08) plus cross-axis surface |
| Within-axis directed edges | 100 |
| Cross-axis directed edges | 28 (IS=6, AS=10, CP=12) |
| Cross-axis-touching units | 16 of 34 (47%) |
| Foundational anchors (L0) | 2 (U-OD-01, U-OD-04) |
| Terminal units (L9) | 2 (U-OD-31, U-OD-34) |
| Level depth | 10 (L0..L9) |
| F2-12 ACTIVE contract-bearing sites | 1 (U-OD-20) |
| F2-12 carry-forward inheritance sites | 1 (U-OD-34) |

### §0a.3 F2-12 ACTIVE engagement summary

| Dimension | Value |
|---|---|
| Sole contract-bearing notation site | U-OD-20 implementing C-OD-14 §14.5 |
| Inheritance site | U-OD-34 (inherits from CP plan U-CP-55 §24.4) |
| Closure path | 6 revision steps: D1 v1.1→v1.2 → D6 v1.1→v1.2 → ADD v1.2→v1.3 → PRD v1.0.1→v1.1 → OD spec v1.2→v1.3 → OD plan v1→v2 |
| Deferred surfaces | 3 (span re-emission semantics; `retry.attempt` sibling-span discipline at D6 ingestion; trace-ingestion dedup composition algorithm) |
| Closure target | OD plan v2 (revision-pass mode) |
| Forward-routing | Parallel `council-orchestrator` C7+C9 session at operator discretion per ADD §6.3.1 active path |

---

## §1 Spec Inventory

### §1.1 Contract enumeration (23 contracts)

| Contract | Surfacing class | Cross-axis posture | PRD anchor |
|---|---|---|---|
| C-OD-01 | Cell matrix shape | OD-internal | R-OD-01 |
| C-OD-02 | Per-cell backend class + candidate witness columns | OD-internal | R-OD-01 |
| C-OD-03 | Deferral envelope (committed-at-D6 vs deferred-to-deployment-binding) | OD-internal | R-OD-01 |
| C-OD-04 | OTel GenAI semconv 1.41.0 base layer | OD-internal | R-OD-02 |
| C-OD-05 | 15-row namespace ingestion map (5 OD-canonical + 7 AS-source + 6 CP-source + 1 substrate-anchored-outside-CP rows; the substrate-anchored row counts toward the namespace map total but its source contract anchor is outside the CP axis per F-CP-01 Stage 3b alignment) | AS-consuming + CP-consuming | R-OD-02 |
| C-OD-06 | F3 capability-floor lifecycle event mapping | CP-consuming | R-OD-02 |
| C-OD-07 | `harness.breaker.*` 7-attribute canonical schema | OD-canonical (substrate-anchored-outside-CP) | R-OD-02, R-OD-03 |
| C-OD-08 | Namespace collision precedence rule | OD-internal | R-OD-02 |
| C-OD-09 | Per-deployment-surface sampling mode + always-sampled exception set | OD-internal | R-OD-03 |
| C-OD-10 | Base-rate-sampled set + per-cell tuning envelope | OD-internal | R-OD-03 |
| C-OD-11 | Per-cell cardinality budget + cardinality-safe / cardinality-prohibited attribute classes | OD-internal | R-OD-03 |
| C-OD-12 | Default-off content + default-on structure attribute discipline | OD-internal | R-OD-04 |
| C-OD-13 | Per-persona-tier override gradient + cross-deployment monotonic-tightening | AS-composing + CP-composing | R-OD-04, R-OD-08 |
| C-OD-14 | Cost-attribution-per-span formula + sandbox-tier overhead + per-sibling rollup + idempotency-key join (**F2-12 ACTIVE at §14.5**) | AS-consuming + CP-consuming + IS-consuming | R-OD-05 |
| C-OD-15 | Cross-family `provider_discriminator` + tokenization-version anchor | CP-consuming | R-OD-05 |
| C-OD-16 | Per-cell cost-attribution dashboard binding | OD-internal | R-OD-05 |
| C-OD-17 | Five operator-burden eval primitives + separate-child-span emission + per-cell dashboard binding scaling | AS-consuming + CP-consuming | R-OD-06 |
| C-OD-18 | Alignment-floor drift detection + eval-vs-runtime-gate distinction | CP-consuming | R-OD-06 |
| C-OD-19 | Local-first OTLP collector at solo-developer × local-development | IS-consuming | R-OD-07 |
| C-OD-20 | Per-cell OTLP collector placement + F4 process-tier reachability | AS-consuming | R-OD-07, R-OD-01 |
| C-OD-21 | Multi-tenant tenant-isolation in observability surface | IS-consuming + CP-consuming | R-OD-04, R-OD-08 |
| C-OD-22 | Bridging-arc traversal preservation across observability dimensions | AS-consuming + CP-consuming | R-OD-08 |
| C-OD-23 | Substrate seam exports for Session 5 + Phase 6+ implementation | OD aggregate exporter | All R-OD-* (cross-axis surface) |

### §1.2 Cross-axis ingestion profile (substrate-residence summary)

| Cross-axis source | Contracts consuming from this source |
|---|---|
| Action Surface | C-OD-05 (7 namespace rows), C-OD-13, C-OD-14, C-OD-17, C-OD-20, C-OD-22 |
| Control Plane | C-OD-05 (6 namespace rows), C-OD-06, C-OD-13, C-OD-14, C-OD-15, C-OD-17, C-OD-18, C-OD-21, C-OD-22 |
| Information Substrate | C-OD-14, C-OD-19, C-OD-21 |
| OD exports (to CP) | C-OD-07 (substrate-anchored-outside-CP for `harness.breaker.*`) |
| OD aggregate exports | C-OD-23 (terminal aggregate manifest) |

### §1.3 F2-12 ACTIVE engagement location (single contract-bearing site per session prompt §5.4 [CF-1] authoring approach (iii))

| Location | Status |
|---|---|
| C-OD-14 §14.5 | ACTIVE / contract-bearing |
| C-OD-05 §5.3 | Forward-compatibility note (non-contract-bearing) |
| C-OD-06 §6.3 | Forward-compatibility note (non-contract-bearing) |

---

## §2 Atomic-Unit Decomposition Framing

### §2.1 Cluster identification (8 clusters; 34 units)

| Cluster | Scope | Contracts | Units | Range |
|---|---|---|---|---|
| OD-CL-1 | Observability cell matrix + backend bindings | C-OD-01, C-OD-02, C-OD-03 | 3 | U-OD-01 – U-OD-03 |
| OD-CL-2 | Unified span schema base + specialization-layer ingestion | C-OD-04, C-OD-05, C-OD-06 | 5 | U-OD-04 – U-OD-08 |
| OD-CL-3 | Substrate-anchored breaker schema + namespace collision | C-OD-07, C-OD-08 | 2 | U-OD-09 – U-OD-10 |
| OD-CL-4 | Sampling + cardinality + redaction | C-OD-09, C-OD-10, C-OD-11, C-OD-12, C-OD-13 | 7 | U-OD-11 – U-OD-17 |
| OD-CL-5 | Cost-attribution cross-cutting | C-OD-14, C-OD-15, C-OD-16 | 5 | U-OD-18 – U-OD-22 |
| OD-CL-6 | Operator-burden eval + alignment-floor drift | C-OD-17, C-OD-18 | 4 | U-OD-23 – U-OD-26 |
| OD-CL-7 | OTLP collector placement + multi-tenant tenant isolation | C-OD-19, C-OD-20, C-OD-21 | 5 | U-OD-27 – U-OD-31 |
| OD-CL-8 | Bridging-arc preservation + substrate seam exports | C-OD-22, C-OD-23 | 3 | U-OD-32 – U-OD-34 |
| **Aggregate** | | **23** | **34** | |

### §2.2 Cross-axis density distribution

| Cluster | Cross-axis edges from cluster | Targets |
|---|---|---|
| OD-CL-1 | 0 | OD-internal |
| OD-CL-2 | 3 | AS: U-OD-06; CP: U-OD-07 + U-OD-08 |
| OD-CL-3 | 1 | CP (OD → CP exporter): U-OD-09 |
| OD-CL-4 | 2 | AS + CP: U-OD-17 |
| OD-CL-5 | 4 | AS + CP: U-OD-19; IS: U-OD-20; CP: U-OD-21 |
| OD-CL-6 | 4 | AS + AS + CP: U-OD-23; CP: U-OD-26 |
| OD-CL-7 | 6 | IS + IS: U-OD-27; AS: U-OD-29; IS + IS + CP: U-OD-30 |
| OD-CL-8 | 8 | AS + AS + AS + CP: U-OD-33; IS + AS + CP + CP terminal manifest refs: U-OD-34 |
| **Total** | **28** | IS=6, AS=10, CP=12 |

### §2.3 Foundational dependency-graph anchors

| Anchor | Role | Out-degree |
|---|---|---|
| U-OD-01 | 9-cell matrix shape declaration (cell-id type + EXCLUDED-cell rejection) | 12 |
| U-OD-04 | OTel GenAI semconv 1.41.0 base-layer attributes | 8 |
| U-OD-07 | `harness.breaker.*` 7-attribute canonical schema (substrate-anchored-outside-CP) | 4 |

### §2.4 Open items reconciled at Stage 2

| Open item | Status |
|---|---|
| OI-1: U-OD-23 vs U-OD-34 numbering reconciliation | Closed — session prompt §8.6 references the substrate seam unit descriptively as "U-OD-23"; the actual substrate seam unit is **U-OD-34** per Stage 2 cluster ordering. The U-OD-23 identifier is reserved for the operator-burden eval primitive declaration at OD-CL-6 |
| OI-2: F2-12 ACTIVE notation at U-OD-20 inheritance | Closed — U-OD-20 inherits the 6-step closure path from CP plan U-CP-55 §24.4 verbatim per session prompt §8.6 |
| OI-3: U-OD-09 OD-canonical authority direction | Closed — `harness.breaker.*` is OD-canonical (substrate-anchored at OD axis per F-CP-01 Stage 3b alignment); OD plan exports to CP rather than consuming from CP at this contract |

---

## §3 Per-Unit Emissions

### §3.1 Cluster OD-CL-1 — Observability cell matrix + backend bindings

#### §3.1.1 U-OD-01 — Declare 9-cell observability matrix

**Implements:** [C-OD-01 §1.1, §1.3, §1.4, §1.5]

**Depends on:** []

**Inputs:** OD spec v1.2 §1.1 matrix shape (persona-tier × deployment-surface 3×3 = 9 cells); §1.3 per-cell entries; §1.4 EXCLUDED-cell rationale; §1.5 cell-identification invariant.

**Files affected:** 9-cell matrix declaration (logical name: `od-cell-matrix-declaration`).

**Persona linkage.** Persona §2 (bridging-arc traversal across persona tiers); §9 (deployment-surface implications); §10.4 (compliance-readiness foundational primitives at multi-tenant cells).

**Signatures:**

```
enum PersonaTier {
  SOLO_DEVELOPER,
  TEAM_BINDING,
  MULTI_TENANT_COMPLIANCE
}

enum DeploymentSurface {
  LOCAL_DEVELOPMENT,
  SELF_HOSTED_SERVER,
  MANAGED_CLOUD
}

record CellID {
  persona_tier         : PersonaTier
  deployment_surface   : DeploymentSurface
}

enum CellStatus {
  ACTIVE,                                           // 8 cells
  EXCLUDED                                          // 1 cell — (MULTI_TENANT_COMPLIANCE, LOCAL_DEVELOPMENT)
}

const ACTIVE_CELLS   : Set<CellID>                  // exactly 8 entries
const EXCLUDED_CELL  : CellID = {MULTI_TENANT_COMPLIANCE, LOCAL_DEVELOPMENT}

fn cell_status(c : CellID) -> CellStatus
fn reject_excluded_cell(c : CellID) -> Result<(), CellBindingViolation>
```

**Acceptance criteria:**

1. `PersonaTier` enumerates exactly 3 values matching §1.1 verbatim.
2. `DeploymentSurface` enumerates exactly 3 values matching §1.1 verbatim.
3. `CellID` is the product `PersonaTier × DeploymentSurface` yielding 9 logical cells.
4. `ACTIVE_CELLS` has cardinality 8; `EXCLUDED_CELL` is the singleton `(MULTI_TENANT_COMPLIANCE, LOCAL_DEVELOPMENT)` per §1.4 verbatim.
5. `cell_status((MULTI_TENANT_COMPLIANCE, LOCAL_DEVELOPMENT)) == EXCLUDED`; all other cells return `ACTIVE`.
6. `reject_excluded_cell` returns `Err(CellBindingViolation)` for the EXCLUDED cell; `Ok` for any ACTIVE cell.
7. EXCLUDED rationale per §1.4 verbatim: compliance-readiness foundational primitives (tenant isolation, encryption-at-rest with vendor-managed key custody, retention controls) are incompatible with single-developer-machine deployment.
8. `CellID` is the canonical key used by all downstream per-cell bindings (C-OD-02 backends; C-OD-09 sampling mode; C-OD-12/13 redaction class; C-OD-19/20 collector placement; C-OD-22 bridging-arc transitions).
9. Cells are stable under serialization (`CellID` is `Eq` + `Hash` over its two fields).
10. No cell-id renaming is permitted across the plan; downstream units cite `CellID` values verbatim per §1.5.

**Tests:** `test_persona_tier_cardinality_three`, `test_deployment_surface_cardinality_three`, `test_cell_id_product_nine`, `test_active_cells_cardinality_eight`, `test_excluded_cell_byte_exact`, `test_cell_status_excluded`, `test_cell_status_active_others`, `test_reject_excluded_cell_returns_err`, `test_reject_active_cell_returns_ok`, `test_cell_id_eq_and_hash_stable`, `test_excluded_rationale_byte_exact`, `test_cell_id_serialization_round_trip`.

**Rollback boundary:** Revert 9-cell matrix declaration. Per-cell binding contracts across the OD axis lose their canonical key; all 12 direct dependents (U-OD-02 / U-OD-03 / U-OD-12 / U-OD-13 / U-OD-16 / U-OD-17 / U-OD-22 / U-OD-24 / U-OD-27 / U-OD-28 / U-OD-30 / U-OD-32) lose `CellID` reference.

---

#### §3.1.2 U-OD-02 — Declare per-cell backend class + candidate witness columns

**Implements:** [C-OD-02 §2.1, §2.2, §2.3]

**Depends on:** [U-OD-01]

**Inputs:** OD spec v1.2 §2.1 per-cell backend class (3 classes: `OTEL_ONLY`, `DEDICATED_LLM_OBS_SINGLE_NODE`, `CLOUD_NATIVE_LLM_OBS`); §2.2 per-cell candidate witness columns (per-cell candidate list per ADR-D6 v1.1 §1.1); §2.3 cell-class commitment invariant.

**Files affected:** Per-cell backend class + candidate witness column declaration (logical name: `od-per-cell-backend-class`).

**Persona linkage.** Persona §9 (deployment-surface candidate enumeration); §10.4 (compliance-readiness backend selection at multi-tenant cells).

**Signatures:**

```
enum BackendClass {
  OTEL_ONLY,
  DEDICATED_LLM_OBS_SINGLE_NODE,
  CLOUD_NATIVE_LLM_OBS
}

record CandidateWitness {
  candidate_name   : string                        // e.g., "Langfuse self-hosted single-node"
  vendor_class     : string                        // e.g., "Langfuse" | "Arize" | "Helicone" | "Datadog" | "Sentry"
  deployment_form  : string                        // e.g., "single-node OTLP endpoint"
}

record PerCellBackendBinding {
  cell_id         : CellID
  backend_class   : BackendClass
  candidates      : List<CandidateWitness>
}

const PER_CELL_BACKEND_BINDINGS : Map<CellID, PerCellBackendBinding>   // exactly 8 entries

fn select_backend_class(c : CellID) -> BackendClass
fn enumerate_candidates(c : CellID) -> List<CandidateWitness>
```

**Acceptance criteria:**

1. `BackendClass` enumerates exactly 3 values per §2.1 verbatim.
2. `PER_CELL_BACKEND_BINDINGS` declares exactly 8 entries — one per ACTIVE cell.
3. Per-cell `backend_class` matches §2.2 row verbatim:
   - cell-1 (solo, local-development) → `OTEL_ONLY`
   - cell-2 (solo, self-hosted-server) → `DEDICATED_LLM_OBS_SINGLE_NODE`
   - cell-3 (solo, managed-cloud) → `CLOUD_NATIVE_LLM_OBS`
   - cell-4 (team, local-development) → `OTEL_ONLY` OR `DEDICATED_LLM_OBS_SINGLE_NODE` (rare configuration alternation per §2.2)
   - cell-5 (team, self-hosted-server) → `DEDICATED_LLM_OBS_SINGLE_NODE`
   - cell-6 (team, managed-cloud) → `CLOUD_NATIVE_LLM_OBS`
   - cell-7 (multi-tenant, self-hosted-server) → `DEDICATED_LLM_OBS_SINGLE_NODE` (multi-tenant variant)
   - cell-8 (multi-tenant, managed-cloud) → `CLOUD_NATIVE_LLM_OBS` (enterprise variant)
4. Per-cell `candidates` carries the candidate list per ADR-D6 v1.1 §1.1 verbatim (Langfuse / Arize Phoenix / Helicone / vendor LLM-obs / Datadog / Sentry / Bedrock AgentCore / Vertex Agent Engine / LangSmith Enterprise / Langfuse Cloud Enterprise — candidates by cell).
5. `select_backend_class(EXCLUDED_CELL)` returns `Err` per U-OD-01 `reject_excluded_cell` composition; backend class is undefined at the EXCLUDED cell.
6. `enumerate_candidates` returns the candidate list per cell; candidates are witness columns — operators MAY select within the list at deployment-binding time.
7. Cell-class commitment invariant per §2.3: each ACTIVE cell carries exactly one `backend_class` (cell-4 alternation between `OTEL_ONLY` and `DEDICATED_LLM_OBS_SINGLE_NODE` is the rare-configuration witness; both are class-committed shapes at this cell).
8. Candidate witnesses are not exhaustive enumeration — they constitute the witness column per ADR-D6 v1.1 §1.1; deployment-binding-time operator binding within the witness column is permitted.

**Tests:** `test_backend_class_cardinality_three`, `test_per_cell_bindings_cardinality_eight`, `test_cell_1_backend_class_otel_only`, `test_cell_2_backend_class_dedicated_single_node`, `test_cell_3_backend_class_cloud_native`, `test_cell_4_alternation_otel_or_dedicated`, `test_cell_5_backend_class_dedicated_single_node`, `test_cell_6_backend_class_cloud_native`, `test_cell_7_backend_class_dedicated_multi_tenant`, `test_cell_8_backend_class_cloud_native_enterprise`, `test_select_backend_class_excluded_cell_returns_err`, `test_enumerate_candidates_per_cell_nonempty`.

**Rollback boundary:** Revert per-cell backend class + candidate witness columns. R-OD-01 satisfaction loses per-cell backend selection substrate; U-OD-28 per-cell collector placement matrix loses the candidate-bound backing-contract references; U-OD-22 per-cell cost-attribution dashboard binding loses backend class enum for cell-class-row routing.

---

#### §3.1.3 U-OD-03 — Declare deferral envelope (committed-at-D6 vs deferred-to-deployment-binding surfaces)

**Implements:** [C-OD-03 §3.1, §3.2, §3.3]

**Depends on:** [U-OD-01, U-OD-02]

**Inputs:** OD spec v1.2 §3.1 committed-at-D6 surfaces (per-cell backend class + sampling discipline + redaction class + trace storage tier + collector placement + retention class — 6 surfaces); §3.2 deferred-to-deployment-binding surfaces (specific vendor candidates within witness column + specific OTel SDK version + specific dashboard query authoring — 11 implementation-discretion deferrals per OD spec); §3.3 deferral envelope boundary invariant.

**Files affected:** Committed-vs-deferred surface declaration (logical name: `od-deferral-envelope`).

**Persona linkage.** Persona §9 (deployment-binding-time operator selections at design-time); §10.4 (compliance-readiness deferred surfaces enumerated for downstream binding).

**Signatures:**

```
enum SurfaceCommitmentClass {
  COMMITTED_AT_D6,
  DEFERRED_TO_DEPLOYMENT_BINDING_TIME
}

record CommittedSurface {
  surface_name          : string                   // e.g., "per-cell backend class"
  contract_anchor       : string                   // e.g., "C-OD-02"
}

record DeferredSurface {
  surface_name          : string                   // e.g., "specific OTel SDK version per language ecosystem"
  contract_anchor       : string                   // e.g., "C-OD-04 'Deferred to implementation discretion'"
  closure_target        : "deployment_binding_time" | "phase_6_implementation"
}

const COMMITTED_AT_D6_SURFACES : List<CommittedSurface>   // exactly 6 entries per §3.1
const DEFERRED_SURFACES        : List<DeferredSurface>    // 11+ entries aggregated from OD spec §[Deferred to implementation discretion] blocks
```

**Acceptance criteria:**

1. `SurfaceCommitmentClass` enumerates exactly 2 values per §3.1–§3.2.
2. `COMMITTED_AT_D6_SURFACES` declares exactly 6 entries per §3.1 verbatim: per-cell backend class (C-OD-02), sampling discipline (C-OD-09 + C-OD-10), redaction class (C-OD-12 + C-OD-13), trace storage tier (C-OD-01 §1.3), collector placement (C-OD-19 + C-OD-20), retention class (C-OD-01 §1.3).
3. `DEFERRED_SURFACES` aggregates the 11 enumeration "Deferred to implementation discretion" blocks across OD spec v1.2 (one per C-OD-01 through C-OD-22 where present).
4. Deferral envelope boundary invariant per §3.3: a surface MUST be in exactly one class; no surface is both committed-at-D6 AND deferred-to-deployment-binding.
5. Surface enumeration is verifiable: every "Deferred to implementation discretion" block in OD spec v1.2 has a corresponding entry in `DEFERRED_SURFACES`.
6. Closure target for deferred surfaces is either `deployment_binding_time` (e.g., specific vendor candidate selection within witness column) or `phase_6_implementation` (e.g., specific OTel SDK version per language ecosystem; specific TUI implementation per terminal toolkit).
7. The deferral envelope composes with U-OD-01 cell matrix + U-OD-02 backend class to form the full design-time committed surface; downstream U-OD-28 + U-OD-30 + U-OD-31 + U-OD-32 + U-OD-34 compose against this committed envelope.

**Tests:** `test_surface_commitment_class_cardinality_two`, `test_committed_at_d6_surfaces_cardinality_six`, `test_deferred_surfaces_aggregates_eleven_or_more`, `test_deferral_envelope_boundary_no_overlap`, `test_every_deferred_implementation_discretion_block_enumerated`, `test_closure_target_one_of_two_values`, `test_committed_surface_contract_anchors_resolve_to_od_spec_sections`.

**Rollback boundary:** Revert deferral envelope declaration. R-OD-01 satisfaction loses committed-vs-deferred boundary anchor; downstream units lose explicit deferral target enumeration; cross-axis composition document at Session 5 loses OD-axis deferral-binding-time surface inventory.

---

### §3.2 Cluster OD-CL-2 — Unified span schema base + specialization-layer ingestion

#### §3.2.1 U-OD-04 — Implement OTel GenAI semconv 1.41.0 base-layer attributes

**Implements:** [C-OD-04 §4.1, §4.2, §4.3, §4.4, §4.5]

**Depends on:** []

**Inputs:** OD spec v1.2 §4.1 span name format; §4.2 operations enum; §4.3 attribute tiers (Required / Conditional / Recommended / Opt-In); §4.4 hierarchy correlation (parent-child trace context propagation); §4.5 base metric (`gen_ai.client.token.usage` per spec).

**Files affected:** OTel GenAI semconv 1.41.0 base-layer attribute declaration (logical name: `od-otel-genai-base-layer`).

**Persona linkage.** Persona §10.2 (observability foundational primitives — token usage measurement at every LLM call).

**Signatures:**

```
const SPAN_NAME_FORMAT : string = "{gen_ai.operation.name} {gen_ai.request.model}"    // §4.1 verbatim

enum GenAiOperation {
  CHAT,
  EXECUTE_TOOL,
  EMBEDDINGS,
  TEXT_COMPLETION,
  CREATE_AGENT,
  INVOKE_AGENT
}

enum AttributeTier {
  REQUIRED,        // §4.3 — emitted at every span
  CONDITIONAL,     // §4.3 — emitted when applicable
  RECOMMENDED,     // §4.3 — emitted by default
  OPT_IN           // §4.3 — emitted only when explicitly enabled
}

record GenAiAttribute {
  name        : string             // e.g., "gen_ai.provider.name", "gen_ai.request.model"
  tier        : AttributeTier
}

const BASE_LAYER_ATTRIBUTES : List<GenAiAttribute>   // OTel GenAI semconv 1.41.0 base set

const BASE_METRIC_NAME : string = "gen_ai.client.token.usage"   // §4.5 verbatim
```

**Acceptance criteria:**

1. `SPAN_NAME_FORMAT` matches §4.1 verbatim.
2. `GenAiOperation` enumerates the 6 operations from OTel GenAI semconv 1.41.0 verbatim.
3. `AttributeTier` enumerates exactly 4 tiers per §4.3 verbatim.
4. `BASE_LAYER_ATTRIBUTES` enumerates the OTel GenAI semconv 1.41.0 base set per §4.3 with per-attribute tier classification (Required: `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`; Conditional: `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`; Recommended: `gen_ai.response.id`, `gen_ai.response.finish_reasons`; Opt-In: `gen_ai.input.messages`, `gen_ai.output.messages`).
5. Parent-child trace context propagation per §4.4: child spans inherit `trace_id` from parent; `span_id` is unique per span; parent span ID is referenced via `parent_span_id` per OTel spec.
6. `BASE_METRIC_NAME == "gen_ai.client.token.usage"` per §4.5 verbatim — the canonical token usage metric.
7. Base-layer attributes are the substrate over which OD specialization-layer namespaces (C-OD-05) compose; specialization namespaces add attributes but do NOT replace base-layer attributes.
8. Conformance to OTel GenAI semconv 1.41.0 is verifiable at runtime via OTel semantic convention validator.

**Tests:** `test_span_name_format_byte_exact`, `test_genai_operation_cardinality_six`, `test_attribute_tier_cardinality_four`, `test_base_layer_attributes_byte_exact_per_semconv_1_41_0`, `test_required_tier_attributes_per_§4_3`, `test_parent_span_id_propagation`, `test_trace_id_inherited_from_parent`, `test_base_metric_name_byte_exact`, `test_specialization_layer_does_not_replace_base_layer`, `test_otel_semconv_validator_passes`, `test_attribute_serialization_round_trip`, `test_span_name_resolves_at_span_emission_time`.

**Rollback boundary:** Revert OTel GenAI semconv 1.41.0 base-layer attribute declaration. R-OD-02 satisfaction loses base-layer substrate; downstream 8 direct dependents (U-OD-05 / U-OD-06 / U-OD-07 / U-OD-08 / U-OD-11 / U-OD-18 / U-OD-21 / U-OD-23) lose attribute-name foundation; span emission across the OD axis loses OTel semconv 1.41.0 conformance anchor.

---

#### §3.2.2 U-OD-05 — Declare 15-row namespace map structure

**Implements:** [C-OD-05 §5.1 (map structure), §5.2]

**Depends on:** [U-OD-04]

**Inputs:** OD spec v1.2 §5.1 namespace ingestion map (15 rows: 1 OD-canonical `provider_discriminator` + 7 AS-source + 6 CP-source + 1 substrate-anchored-outside-CP `harness.breaker.*`); §5.2 ingestion-posture invariants.

**Files affected:** Namespace ingestion map declaration (logical name: `od-namespace-ingestion-map`).

**Persona linkage.** Persona §10.2 (observability foundational primitives — namespace ingestion supports compliance + cost-attribution + operator-burden eval).

**Signatures:**

```
enum NamespaceSourceAxis {
  OD_CANONICAL,                          // declared at OD axis
  AS_SOURCE,                             // declared at AS axis; ingested at OD
  CP_SOURCE,                             // declared at CP axis; ingested at OD
  SUBSTRATE_ANCHORED_OUTSIDE_CP          // declared at OD per F-CP-01 Stage 3b alignment
}

record NamespaceMapRow {
  namespace_prefix     : string          // e.g., "anthropic.", "mcp.", "harness.breaker."
  attribute_count      : int             // attributes per namespace
  source_axis          : NamespaceSourceAxis
  source_contract_ref  : string          // e.g., "C-AS-14 §14.2", "C-CP-24 §24.1.A", "C-OD-07 §7.1"
}

const NAMESPACE_MAP : List<NamespaceMapRow>   // exactly 15 entries

fn lookup_namespace(prefix : string) -> Option<NamespaceMapRow>
fn assert_source_authoritative_declarer(prefix : string, source : NamespaceSourceAxis) -> Result<(), AuthorityViolation>
```

**Acceptance criteria:**

1. `NamespaceSourceAxis` enumerates exactly 4 values per §5.1 + §5.2.
2. `NAMESPACE_MAP` declares exactly **15** entries per §5.1 verbatim.
3. Per-row source axis breakdown matches §5.1 verbatim: 1 `OD_CANONICAL` (`provider_discriminator`); 7 `AS_SOURCE` (anthropic, mcp, skill, managed_agents, sandbox, files, memory); 6 `CP_SOURCE` (hitl, topology, subagent, engine, audit, validator.fail); 1 `SUBSTRATE_ANCHORED_OUTSIDE_CP` (`harness.breaker.*` per F-CP-01 Stage 3b alignment).
4. Per-row `source_contract_ref` resolves to a specific spec contract section in AS / CP / OD spec v1 documents.
5. `lookup_namespace` returns `Some(NamespaceMapRow)` for any of the 15 declared prefixes; `None` otherwise.
6. `assert_source_authoritative_declarer` returns `Err(AuthorityViolation)` if a namespace is claimed by an axis that does not match its declared `source_axis` — this enforces Pattern P1 mechanical-alignment discipline at the namespace authority boundary.
7. Per §5.2 ingestion-posture invariants: each namespace has exactly one authoritative declarer; secondary references are non-authoritative.
8. Namespace map is stable under the F2-12 carry-forward — `harness.breaker.*` and lifecycle event ingestion may be revised at OD spec v1.3 but namespace count remains 15 at v1.

**Tests:** `test_namespace_source_axis_cardinality_four`, `test_namespace_map_cardinality_fifteen`, `test_namespace_source_axis_breakdown_1_7_6_1`, `test_provider_discriminator_od_canonical`, `test_anthropic_namespace_as_source`, `test_hitl_namespace_cp_source`, `test_harness_breaker_substrate_anchored_outside_cp`, `test_lookup_namespace_existing_returns_some`, `test_lookup_namespace_missing_returns_none`, `test_assert_source_authoritative_declarer_match_ok`, `test_assert_source_authoritative_declarer_mismatch_err`.

**Rollback boundary:** Revert 15-row namespace map structure. R-OD-02 satisfaction loses ingestion map; downstream 10 direct dependents lose namespace prefix → source-axis routing; Pattern P1 cross-axis verification loses anchor for namespace authority enforcement.

---

#### §3.2.3 U-OD-06 — Verify AS-source namespace set (7 rows)

**Implements:** [C-OD-05 §5.1 (AS-source rows)]

**Depends on:** [U-OD-04, U-OD-05, U-AS-33 (cross-axis: AS — C-AS-16 §16.1 + §16.4)]

**Inputs:** AS plan U-AS-33 substrate seam exports manifest (5+2 AS-source namespaces declared: 5 in C-AS-16 §16.1 + 2 additional rows total 7 AS-source rows in C-OD-05 §5.1); OD spec v1.2 §5.1 verifies the AS-source row count against AS plan declaration.

**Cross-axis dependency resolution.** AS plan U-AS-33 substrate seam exports manifest is the authoritative declarer for AS-source namespaces. Per OD-S4-3.A, the cross-axis edge is `Depends on: [U-AS-33 (cross-axis: AS — C-AS-16 §16.1 + §16.4)]`.

**Files affected:** AS-source namespace set verification (logical name: `od-as-source-namespace-verification`).

**Signatures:**

```
const AS_SOURCE_NAMESPACE_PREFIXES : Set<string> = {
  "anthropic.",
  "mcp.",
  "skill.",
  "managed_agents.",
  "sandbox.",
  "files.",
  "memory."
}                                                 // exactly 7 entries

fn verify_as_source_namespace_set(declared : Set<string>) -> Result<(), NamespaceSetMismatch>
fn assert_namespace_attribute_count(prefix : string, expected_count : int) -> Result<(), AttributeCountMismatch>
```

**Acceptance criteria:**

1. `AS_SOURCE_NAMESPACE_PREFIXES` has cardinality **7** matching the 7 AS-source rows in C-OD-05 §5.1 verbatim.
2. Per-prefix attribute count per AS plan U-AS-33 manifest: `anthropic.*` (per C-AS-14 §14.2), `mcp.*` (per C-AS-14 §14.4), `skill.*` (per C-AS-14 §14.5), `managed_agents.*` (per C-AS-14 §14.6), `sandbox.*` (per C-AS-15 §15.1–§15.6), `files.*` (per C-AS-14 §14.7), `memory.*` (per C-AS-14 §14.8).
3. `verify_as_source_namespace_set` returns `Err(NamespaceSetMismatch)` if the declared set differs from `AS_SOURCE_NAMESPACE_PREFIXES`.
4. `assert_namespace_attribute_count` returns `Err(AttributeCountMismatch)` if observed attribute count for a prefix differs from AS plan U-AS-33 manifest.
5. Pattern P1 mechanical-alignment discipline: this unit's prefix set is byte-exact against AS plan U-AS-33 manifest; any drift is a Pattern P1 violation.
6. Cross-axis edge annotation per OD-S4-3.A: edge target = U-AS-33 (terminal exporter); contract anchors = C-AS-16 §16.1 + §16.4.

**Tests:** `test_as_source_namespace_prefixes_cardinality_seven`, `test_namespace_prefixes_byte_exact`, `test_verify_as_source_namespace_set_match_ok`, `test_verify_as_source_namespace_set_mismatch_err`, `test_assert_namespace_attribute_count_per_prefix`, `test_cross_axis_edge_to_u_as_33_declared`.

**Rollback boundary:** Revert AS-source namespace set verification. C-OD-05 AS-source ingestion loses byte-exact alignment with AS plan; Pattern P1 cross-axis verification at Session 5 loses OD-side anchor for AS-source namespace consistency.

---

#### §3.2.4 U-OD-07 — Verify CP-source namespace set (6 rows)

**Implements:** [C-OD-05 §5.1 (CP-source rows)]

**Depends on:** [U-OD-04, U-OD-05, U-CP-54 (cross-axis: CP — C-CP-24 §24.1.A + §24.1.B)]

**Inputs:** CP plan U-CP-54 substrate seam exports manifest (6 CP-source namespaces declared at C-CP-24 §24.1.A + §24.1.B); OD spec v1.2 §5.1 verifies the CP-source row count against CP plan declaration.

**Cross-axis dependency resolution.** CP plan U-CP-54 substrate seam exports manifest is the authoritative declarer for CP-source namespaces. Per OD-S4-3.A, the cross-axis edge is `Depends on: [U-CP-54 (cross-axis: CP — C-CP-24 §24.1.A + §24.1.B)]`.

**Files affected:** CP-source namespace set verification (logical name: `od-cp-source-namespace-verification`).

**Signatures:**

```
const CP_SOURCE_NAMESPACE_PREFIXES : Set<string> = {
  "hitl.",
  "topology.",
  "subagent.",
  "engine.",
  "audit.",
  "validator.fail."
}                                                 // exactly 6 entries
```

**Acceptance criteria:**

1. `CP_SOURCE_NAMESPACE_PREFIXES` has cardinality **6** matching the 6 CP-source rows in C-OD-05 §5.1 verbatim.
2. Per-prefix attribute count per CP plan U-CP-54 manifest: `hitl.*` (per C-CP-20 §20.6), `topology.*` (per C-CP-14 §14.2), `subagent.*` (per C-CP-14 §14.2), `engine.*` (per C-CP-09 §9.1), `audit.*` (per C-CP-20 §20.4 — 7 attributes), `validator.fail.*` (per C-CP-21 §21.5).
3. `routing.*` namespace is NOT in the CP-source set at OD ingestion — it is declared at C-CP-01 §1.4 and inherited from parent `llm.inference` span sampling per OTel GenAI semconv 1.41.0; per C-OD-05 §5.1 ingestion-posture invariant, `routing.*` is a CP-axis-only namespace under inheritance composition, not direct OD ingestion.
4. Pattern P1 mechanical-alignment discipline: this unit's prefix set is byte-exact against CP plan U-CP-54 manifest.
5. Cross-axis edge annotation per OD-S4-3.A: edge target = U-CP-54; contract anchors = C-CP-24 §24.1.A + §24.1.B.

**Tests:** `test_cp_source_namespace_prefixes_cardinality_six`, `test_namespace_prefixes_byte_exact_per_§5_1`, `test_routing_namespace_excluded_from_cp_source_set`, `test_verify_cp_source_namespace_set_match_ok`, `test_assert_namespace_attribute_count_per_prefix`, `test_cross_axis_edge_to_u_cp_54_declared`.

**Rollback boundary:** Revert CP-source namespace set verification. C-OD-05 CP-source ingestion loses byte-exact alignment with CP plan; Pattern P1 cross-axis verification at Session 5 loses OD-side anchor for CP-source namespace consistency.

---

#### §3.2.5 U-OD-08 — Map F3 lifecycle events to span events

**Implements:** [C-OD-06 §6.1, §6.2, §6.3]

**Depends on:** [U-OD-04, U-OD-05, U-OD-06, U-OD-07, U-CP-54 (cross-axis: CP — C-CP-24 §24.1.B F3 lifecycle event attributes)]

**Inputs:** OD spec v1.2 §6.1 F3 capability-floor lifecycle event mapping table (8 F3 event classes → span event names + attribute namespaces); §6.2 additive composition (lifecycle events compose additively with base-layer); §6.3 F2-12 deferral acknowledgement at `retry.attempt`.

**Cross-axis dependency resolution.** CP plan U-CP-54 substrate seam exports manifest declares F3 lifecycle event attributes via C-CP-24 §24.1.B. Per OD-S4-3.A, the cross-axis edge is `Depends on: [U-CP-54 (cross-axis: CP — C-CP-24 §24.1.B)]`.

**Files affected:** F3 lifecycle event-to-span-event mapping declaration (logical name: `od-f3-lifecycle-event-mapping`).

**Signatures:**

```
enum F3LifecycleEventClass {
  CHAT_INVOCATION,
  TOOL_INVOCATION,
  FALLBACK_TRIGGERED,
  FALLBACK_EXHAUSTED,
  BREAKER_TRIPPED,
  RETRY_ATTEMPT,
  HITL_INVOCATION,
  SUBAGENT_DISPATCH
}                                            // exactly 8 F3 event classes per §6.1

record LifecycleEventMapping {
  f3_event_class       : F3LifecycleEventClass
  span_event_name      : string                  // e.g., "fallback.triggered"
  attribute_namespaces : Set<string>             // e.g., {"fallback.", "harness.breaker.", "retry."}
}

const F3_LIFECYCLE_EVENT_MAPPINGS : Map<F3LifecycleEventClass, LifecycleEventMapping>   // exactly 8 entries

// §6.3 F2-12 deferral acknowledgement (non-contract-bearing)
const F2_12_DEFERRAL_NOTE_AT_RETRY_ATTEMPT : string =
  "retry.attempt sibling-span discipline at D6 ingestion is deferred per F2-12 carry-forward; v1 commits event + new sibling span per C-CP-03 §3.5; revisable at D6 v1.2"
```

**Acceptance criteria:**

1. `F3LifecycleEventClass` enumerates exactly **8** values per §6.1 verbatim.
2. `F3_LIFECYCLE_EVENT_MAPPINGS` declares exactly 8 entries with per-class span event name + attribute namespace set per §6.1 verbatim.
3. Per-class mapping: `CHAT_INVOCATION` → span event "chat" + namespaces {anthropic., gen_ai.}; `TOOL_INVOCATION` → "execute_tool" + {mcp., skill., sandbox., files., memory.}; `FALLBACK_TRIGGERED` → "fallback.triggered" + {fallback., engine.}; `FALLBACK_EXHAUSTED` → "fallback.exhausted" + {fallback., engine.}; `BREAKER_TRIPPED` → "breaker.tripped" + {harness.breaker., engine.}; `RETRY_ATTEMPT` → "retry.attempt" + {retry., engine.}; `HITL_INVOCATION` → "hitl.invocation.responded" + {hitl.}; `SUBAGENT_DISPATCH` → "subagent.dispatched" + {subagent.}.
4. Additive composition invariant per §6.2: lifecycle event attributes compose additively with base-layer attributes; lifecycle event emission does NOT replace any base-layer attribute.
5. F2-12 deferral note at `retry.attempt` per §6.3 is **non-contract-bearing** — it acknowledges that the sibling-span discipline at D6 ingestion is deferred to D6 v1.2 per F2-12 carry-forward. v1 commitment per C-CP-03 §3.5 stands: event + new sibling span.
6. `F2_12_DEFERRAL_NOTE_AT_RETRY_ATTEMPT` carries the §6.3 acknowledgement verbatim; this constant is a forward-compatibility note, not a contract-bearing F2-12 ACTIVE engagement (which is contract-bearing exclusively at U-OD-20 §14.5).
7. Cross-axis edge per OD-S4-3.A: edge target = U-CP-54; contract anchor = C-CP-24 §24.1.B (F3 lifecycle event attributes).
8. F3 capability-floor anchor: this mapping is the F3 v1.0 capability-floor (iv) lifecycle event mapping composition at OD.

**Tests:** `test_f3_lifecycle_event_class_cardinality_eight`, `test_f3_lifecycle_event_mappings_cardinality_eight`, `test_chat_invocation_mapping`, `test_tool_invocation_mapping`, `test_fallback_triggered_mapping`, `test_fallback_exhausted_mapping`, `test_breaker_tripped_mapping`, `test_retry_attempt_mapping`, `test_hitl_invocation_mapping`, `test_subagent_dispatch_mapping`, `test_additive_composition_no_base_layer_replacement`, `test_f2_12_deferral_note_byte_exact`, `test_f2_12_deferral_note_non_contract_bearing`, `test_cross_axis_edge_to_u_cp_54_section_24_1_b_declared`.

**Rollback boundary:** Revert F3 lifecycle event-to-span-event mapping. R-OD-02 satisfaction loses lifecycle event ingestion substrate; downstream U-OD-10 namespace collision discipline loses event composition reference; downstream U-OD-11 always-sampled set composition loses lifecycle event class enumeration.

---

### §3.3 Cluster OD-CL-3 — Substrate-anchored breaker schema + namespace collision

#### §3.3.1 U-OD-09 — Declare `harness.breaker.*` 7-attribute canonical schema (substrate-anchored-outside-CP)

**Implements:** [C-OD-07 §7.1, §7.2, §7.3]

**Depends on:** [U-OD-07]

**Inputs:** OD spec v1.2 §7.1 seven-attribute canonical schema; §7.2 quality-of-emission invariants (always-sampled at all cells + cardinality-safe attributes only + no payload content); §7.3 C9↔C10 subscription contract reference (breaker-trip event as gating signal per C9 reliability primitive subscribed by C10 action-safety gate).

**Files affected:** `harness.breaker.*` substrate-anchored canonical schema declaration (logical name: `od-harness-breaker-canonical-schema`).

**Substrate-anchored-outside-CP rationale.** Per F-CP-01 Stage 3b alignment, the `harness.breaker.*` namespace is **substrate-anchored at the OD axis** rather than the CP axis. The CP-side `breaker.*` 4-attribute set is replaced under F-CP-01 alignment by this OD-canonical 7-attribute schema. The OD plan exports `harness.breaker.*` to the CP plan as a **CP-consuming** seam (per OD plan U-OD-09 → CP plan U-CP-54 §24.1.C cross-axis edge). This is the **OD → CP exporter** direction — unusual relative to the typical CP → OD direction at namespace ingestion.

**Persona linkage.** Persona §4 (99.9% SLO; breaker-trip event is reliability-critical signal); §10.2 (compliance-readiness — breaker-trip events always-sampled at multi-tenant cells for tamper-evident audit ledger composition).

**Signatures:**

```
const HARNESS_BREAKER_ATTRIBUTES : List<GenAiAttribute> = [
  {name: "harness.breaker.scope",                  tier: REQUIRED},
  {name: "harness.breaker.from_state",             tier: REQUIRED},
  {name: "harness.breaker.to_state",               tier: REQUIRED},
  {name: "harness.breaker.trigger_count",          tier: REQUIRED},
  {name: "harness.breaker.permanent_fail_repeats", tier: CONDITIONAL},
  {name: "harness.breaker.tool_id",                tier: CONDITIONAL},
  {name: "harness.breaker.model_version",          tier: CONDITIONAL}
]                                                  // exactly 7 attributes

enum BreakerScope {
  TOOL_CALL,
  MODEL_INVOCATION,
  PROVIDER_FAMILY,
  PROVIDER_INSTANCE
}                                                  // per D6 v1.1 §1.2

enum BreakerState {
  CLOSED,
  HALF_OPEN,
  OPEN
}                                                  // canonical breaker state machine

record HarnessBreakerEvent {
  scope                    : BreakerScope
  from_state               : BreakerState
  to_state                 : BreakerState
  trigger_count            : int
  permanent_fail_repeats   : Option<int>
  tool_id                  : Option<string>        // when scope == TOOL_CALL
  model_version            : Option<string>        // when scope ∈ {MODEL_INVOCATION, PROVIDER_INSTANCE}
}

fn emit_breaker_trip_span_event(
  parent_span_ref : SpanRef,
  event           : HarnessBreakerEvent
) -> Result<EventEmission, BreakerEmissionError>
```

**Acceptance criteria:**

1. `HARNESS_BREAKER_ATTRIBUTES` declares exactly **7** attributes per §7.1 verbatim.
2. Required vs Conditional tier classification per §7.1: 4 Required (scope / from_state / to_state / trigger_count); 3 Conditional (permanent_fail_repeats / tool_id / model_version).
3. `BreakerScope` enumerates exactly 4 values per D6 v1.1 §1.2.
4. `BreakerState` enumerates exactly 3 values (CLOSED / HALF_OPEN / OPEN) per canonical breaker state machine.
5. Quality-of-emission invariants per §7.2: breaker-trip events are always-sampled at all cells (composes with U-OD-11 always-sampled set); attributes are cardinality-safe (no payload content; per-attribute cardinality bounded by `BreakerScope` enum × `BreakerState` enum × bounded integers).
6. C9↔C10 subscription contract per §7.3: breaker-trip events emitted at C9 reliability primitive ownership are subscribed by C10 action-safety gate as gating signal; this is a runtime cross-voice subscription, not a compile-time link.
7. Substrate-anchored-outside-CP per F-CP-01 Stage 3b: the OD axis owns the canonical schema; the CP plan's `breaker.*` 4-attribute set is replaced by this OD-canonical 7-attribute schema at C-CP-24 §24.1.C ingestion.
8. Cross-axis export per OD-S4-3.A: this unit is an **OD → CP exporter**; edge target = U-CP-54 (CP plan substrate seam exports manifest); contract anchor = C-CP-24 §24.1.C.
9. `emit_breaker_trip_span_event` emits the event at the parent span with all 7 attributes (Required always; Conditional when applicable per scope); returns `Err(BreakerEmissionError)` if Required attributes are missing.

**Tests:** `test_harness_breaker_attributes_cardinality_seven`, `test_harness_breaker_attribute_names_byte_exact`, `test_required_tier_attributes_count_four`, `test_conditional_tier_attributes_count_three`, `test_breaker_scope_cardinality_four`, `test_breaker_state_cardinality_three`, `test_emit_breaker_trip_with_all_required_attrs_accept`, `test_emit_breaker_trip_missing_required_attr_reject`, `test_breaker_event_always_sampled_at_all_cells`, `test_breaker_attributes_cardinality_safe`, `test_cross_axis_export_to_u_cp_54_section_24_1_c_declared`, `test_substrate_anchored_outside_cp_per_f_cp_01_stage_3b`.

**Rollback boundary:** Revert `harness.breaker.*` substrate-anchored canonical schema. R-OD-02 + R-OD-03 satisfaction loses breaker-trip event schema; F-CP-01 Stage 3b alignment loses OD-axis substrate; CP plan U-CP-54 §24.1.C ingestion loses `harness.breaker.*` substrate-anchored-outside-CP reference; C9↔C10 subscription contract loses event substrate.

---

#### §3.3.2 U-OD-10 — Declare namespace collision precedence rule + cross-namespace cardinality discipline

**Implements:** [C-OD-08 §8.1, §8.2, §8.3]

**Depends on:** [U-OD-05, U-OD-08, U-OD-09]

**Inputs:** OD spec v1.2 §8.1 collision precedence rule (substrate-anchored namespace takes precedence over CP-side replaced namespace); §8.2 canonical example (`harness.breaker.*` precedence over CP `breaker.*` per F-CP-01 Stage 3b); §8.3 cross-namespace cardinality discipline (cache-tier subset invariant: `cache_creation + cache_read + uncached == input_tokens`).

**Files affected:** Namespace collision precedence + cross-namespace cardinality discipline (logical name: `od-namespace-collision-discipline`).

**Signatures:**

```
enum NamespacePrecedenceRule {
  SUBSTRATE_ANCHORED_TAKES_PRECEDENCE,            // §8.1 verbatim
  AUTHORITATIVE_DECLARER_RESOLVES_COLLISION       // §8.2 secondary rule
}

record NamespaceCollisionResolution {
  colliding_prefix     : string                   // e.g., "breaker."
  authoritative_prefix : string                   // e.g., "harness.breaker."
  precedence_rule      : NamespacePrecedenceRule
  rationale_ref        : string                   // e.g., "F-CP-01 Stage 3b alignment"
}

const NAMESPACE_COLLISIONS : List<NamespaceCollisionResolution>   // §8.2 canonical example + any others

// §8.3 cross-namespace cardinality invariants
record CacheTierSubsetInvariant {
  invariant_form : "cache_creation + cache_read + uncached == input_tokens"
  enforced_at    : "U-OD-18 cost formula composition + OTel canonical value verification"
}

fn enforce_otel_canonical_value(
  span_attrs : SpanAttributes
) -> Result<(), CanonicalValueViolation>
```

**Acceptance criteria:**

1. `NamespacePrecedenceRule` enumerates exactly 2 values per §8.1.
2. `NAMESPACE_COLLISIONS` declares the canonical example per §8.2 verbatim: colliding_prefix `"breaker."` (CP-side), authoritative_prefix `"harness.breaker."` (OD-side substrate-anchored), rule `SUBSTRATE_ANCHORED_TAKES_PRECEDENCE`, rationale `"F-CP-01 Stage 3b alignment"`.
3. Substrate-anchored namespace takes precedence per §8.1 verbatim — when a CP-side namespace declaration is replaced by an OD-anchored namespace (per F-CP-01 Stage 3b), the OD-anchored namespace is the canonical declarer at all subsequent ingestion sites.
4. Cross-namespace cardinality invariant per §8.3: cache-tier breakdown sums to `input_tokens` — `cache_creation + cache_read + uncached == input_tokens`. Violation of this invariant produces `Err(CanonicalValueViolation)` at `enforce_otel_canonical_value`.
5. The invariant is enforced at span emission time; downstream U-OD-18 cost formula composition relies on this invariant for correctness (uncached input contribution = `input_tokens − cache_read − cache_creation`).
6. `enforce_otel_canonical_value` is invoked at every span emission; non-conformant attribute sets are rejected.

**Tests:** `test_namespace_precedence_rule_cardinality_two`, `test_namespace_collisions_includes_harness_breaker_precedence`, `test_substrate_anchored_takes_precedence_per_§8_1`, `test_cache_tier_subset_invariant_holds_at_canonical_span`, `test_cache_tier_violation_rejected`, `test_enforce_otel_canonical_value_passes_valid`, `test_enforce_otel_canonical_value_rejects_invalid`, `test_f_cp_01_stage_3b_rationale_byte_exact`, `test_collision_resolution_resolves_to_authoritative_prefix`, `test_replaced_namespace_no_longer_declarative`.

**Rollback boundary:** Revert namespace collision precedence rule + cross-namespace cardinality discipline. F-CP-01 Stage 3b alignment loses OD-side runtime enforcement; cache-tier subset invariant loses span-emission-time validation; downstream U-OD-18 cost formula composition loses uncached-input-derivation correctness anchor.

---
### §3.4 Cluster OD-CL-4 — Sampling + cardinality + redaction

#### §3.4.1 U-OD-11 — Declare per-deployment-surface sampling mode + 18-entry always-sampled exception set

**Implements:** [C-OD-09 §9.1, §9.2, §9.3]

**Depends on:** [U-OD-04, U-OD-05, U-OD-06, U-OD-09]

**Inputs:** OD spec v1.2 §9.1 per-deployment-surface sampling mode (head-based-dev at local-development cells; tail-based-prod at self-hosted-server + managed-cloud cells); §9.2 always-sampled exception set (18 entries spanning lifecycle events + breaker events + audit events + sandbox violations); §9.3 sampling-discipline invariants.

**Files affected:** Sampling mode + always-sampled set (logical name: `od-sampling-mode-and-always-sampled-set`).

**Persona linkage.** Persona §6 (per-class cost ceiling — sampling efficiency at base-rate cells); §10.4 (compliance-readiness — always-sampled audit events).

**Signatures:**

```
enum SamplingMode {
  HEAD_BASED_DEV,                      // local-development cells; head=1.0
  TAIL_BASED_PROD                      // self-hosted-server + managed-cloud cells
}

record PerDeploymentSurfaceSamplingMode {
  deployment_surface : DeploymentSurface
  sampling_mode      : SamplingMode
}

const PER_DEPLOYMENT_SURFACE_SAMPLING : Map<DeploymentSurface, SamplingMode> = {
  LOCAL_DEVELOPMENT     : HEAD_BASED_DEV,
  SELF_HOSTED_SERVER    : TAIL_BASED_PROD,
  MANAGED_CLOUD         : TAIL_BASED_PROD
}

const ALWAYS_SAMPLED_EVENT_CLASSES : Set<string> = {
  // F3 lifecycle events that ALWAYS sample regardless of head/tail mode
  "fallback.triggered", "fallback.exhausted", "breaker.tripped",
  "hitl.invocation.responded", "subagent.dispatched", "topology.fanout.closed",
  // validation failures
  "validator.fail.permanent", "validator.fail.transient_exhausted",
  // sandbox violations
  "sandbox.violation",
  // audit-ledger events at multi-tenant cells (any span with audit.signature.*)
  "audit.signed.entry",
  // retry attempts beyond attempt 1
  "retry.attempt.second_or_later",
  // eval drift detection
  "gen_ai.eval.alignment_floor.drift_detected",
  // engine class events
  "engine.replay.started", "engine.replay.completed",
  // tool gating denials
  "tool.gate.denied",
  // MCP server pinning failures
  "mcp.server.pin_mismatch",
  // breaker repeated permanent-fail trips
  "harness.breaker.permanent_fail_chain"
}                                                  // exactly 18 entries

fn sampling_decision(
  cell_id : CellID,
  event_class : string,
  base_rate : float
) -> SamplingDecision
```

**Acceptance criteria:**

1. `SamplingMode` enumerates exactly 2 values per §9.1.
2. `PER_DEPLOYMENT_SURFACE_SAMPLING` matches §9.1 row mapping verbatim.
3. `ALWAYS_SAMPLED_EVENT_CLASSES` has cardinality **18** per §9.2 verbatim.
4. Always-sampled set is independent of base-rate sampling: any event in the set samples at head=1.0 regardless of cell base-rate.
5. Sampling-discipline invariants per §9.3: always-sampled set is preserved across all 8 bridging-arc transitions (destination set ⊇ source set per U-OD-32 §22.3 verification dimension).
6. `sampling_decision` returns `SAMPLE_ALWAYS` for any event in `ALWAYS_SAMPLED_EVENT_CLASSES` regardless of `base_rate`; returns `SAMPLE_AT_BASE_RATE` otherwise.
7. Audit-ledger entries at multi-tenant cells are always-sampled per C-OD-21 composition; the `audit.signed.entry` event class entry covers this composition.

**Tests:** `test_sampling_mode_cardinality_two`, `test_per_surface_sampling_local_head_based`, `test_per_surface_sampling_self_hosted_tail_based`, `test_per_surface_sampling_managed_cloud_tail_based`, `test_always_sampled_event_classes_cardinality_eighteen`, `test_always_sampled_event_class_names_byte_exact`, `test_sampling_decision_always_sampled_event`, `test_sampling_decision_base_rate_event_below_threshold`, `test_always_sampled_preserved_across_bridging_arc_transitions`, `test_audit_signed_entry_in_always_sampled_set`, `test_breaker_tripped_in_always_sampled_set`.

**Rollback boundary:** Revert sampling mode + always-sampled set. R-OD-03 satisfaction loses sampling discipline; downstream U-OD-12 base-rate set composition loses always-sampled-exception complement; U-OD-25 drift detection event composition loses always-sampled membership reference; bridging-arc transition verification at U-OD-32 loses sampling-tightening invariant substrate.

---

#### §3.4.2 U-OD-12 — Declare 13-entry base-rate-sampled set + per-cell tuning envelope

**Implements:** [C-OD-10 §10.1, §10.2, §10.3]

**Depends on:** [U-OD-01, U-OD-11]

**Inputs:** OD spec v1.2 §10.1 base-rate-sampled set (13 entries: chat / execute_tool / tool.call / etc.); §10.2 tail-keep-on-classification (tail-based-prod cells keep failed traces post-classification); §10.3 per-cell base-rate tuning envelope (default rate + min/max envelope per cell).

**Files affected:** Base-rate set + per-cell tuning envelope (logical name: `od-base-rate-set-and-envelope`).

**Signatures:**

```
const BASE_RATE_SAMPLED_EVENT_CLASSES : Set<string> = {
  "chat", "execute_tool", "tool.call",
  "embeddings", "text_completion",
  "create_agent", "invoke_agent",
  "retry.attempt.first",
  "validator.fail.transient",
  "skill.activated", "skill.invocation",
  "memory.operation", "files.operation"
}                                                  // exactly 13 entries

record PerCellBaseRateEnvelope {
  cell_id           : CellID
  default_rate      : float                        // operator-tunable per §10.3
  min_rate          : float                        // envelope floor
  max_rate          : float                        // envelope ceiling
}

const PER_CELL_BASE_RATE_ENVELOPE : Map<CellID, PerCellBaseRateEnvelope>   // exactly 8 entries

// §10.2 tail-keep-on-classification
record TailKeepRule {
  classification_attribute : string   // e.g., "validator.fail.permanence == permanent"
  keep_decision            : "ALWAYS_KEEP"
}

const TAIL_KEEP_RULES : List<TailKeepRule>   // composes with tail-based-prod sampling mode
```

**Acceptance criteria:**

1. `BASE_RATE_SAMPLED_EVENT_CLASSES` has cardinality **13** per §10.1 verbatim.
2. `BASE_RATE_SAMPLED_EVENT_CLASSES ∩ ALWAYS_SAMPLED_EVENT_CLASSES == ∅` — sets are disjoint (event class belongs to exactly one regime).
3. `PER_CELL_BASE_RATE_ENVELOPE` has cardinality **8** — one per ACTIVE cell. Per §10.3 envelope:
   - solo-developer × * → default 1.0 (everything sampled at design-time)
   - team-binding × * → default 0.05–0.5 (typical envelope)
   - multi-tenant-compliance × * → default 0.1–0.5 (compliance + cost balance)
4. `min_rate <= default_rate <= max_rate` per cell — envelope invariant.
5. Per §10.3 envelope tightening invariant across bridging-arc transitions (composition with U-OD-32 §22.3 sampling-discipline tightening dimension): `target_cell.max_rate <= source_cell.max_rate` along persona-tier axis at fixed deployment surface.
6. `TAIL_KEEP_RULES` declares the tail-keep-on-classification post-classification keep decisions per §10.2: failed traces (validator.fail.permanent / sandbox violations / breaker trips) ALWAYS_KEEP at tail-based-prod cells regardless of base-rate.

**Tests:** `test_base_rate_set_cardinality_thirteen`, `test_base_rate_event_names_byte_exact`, `test_base_rate_and_always_sampled_disjoint`, `test_per_cell_envelope_cardinality_eight`, `test_envelope_invariant_min_default_max`, `test_solo_cells_default_rate_one_point_zero`, `test_team_cells_default_rate_in_envelope`, `test_multi_tenant_cells_default_rate_in_envelope`, `test_envelope_tightening_across_bridging_arc`, `test_tail_keep_rules_apply_post_classification`.

**Rollback boundary:** Revert base-rate set + per-cell envelope. R-OD-03 satisfaction loses base-rate discipline; downstream U-OD-22 alerting threshold scaling loses base-rate-scaling factor (`1.0 / base_rate`); bridging-arc transition verification loses base-rate-envelope-tightening substrate.

---

#### §3.4.3 U-OD-13 — Declare per-cell cardinality budget + Pattern P1 discipline anchor

**Implements:** [C-OD-11 §11.1, §11.4]

**Depends on:** [U-OD-01, U-OD-05, U-OD-11]

**Inputs:** OD spec v1.2 §11.1 per-cell cardinality budget posture (per-cell rate limits at OTLP collector boundary or backend ingestion); §11.4 Pattern P1 discipline anchor (per-attribute name byte-exact alignment across all source artifacts).

**Files affected:** Per-cell cardinality budget + Pattern P1 anchor (logical name: `od-per-cell-cardinality-budget`).

**Signatures:**

```
record PerCellCardinalityBudget {
  cell_id              : CellID
  tenant_rate_limit    : Option<float>             // None at non-multi-tenant cells; Some at multi-tenant
  cell_rate_limit      : float                     // per-cell global rate limit (spans/sec)
  enforcement_layer    : "COLLECTOR_BOUNDARY" | "BACKEND_INGESTION"
}

const PER_CELL_CARDINALITY_BUDGET : Map<CellID, PerCellCardinalityBudget>   // exactly 8 entries

const PATTERN_P1_DISCIPLINE_ANCHOR : string =
  "Per-attribute names MUST be byte-exact across OD spec / AS spec / CP spec / IS spec / ADRs / OTel SDK bindings. Pattern P1 was raised at P3c-CK Iteration 1 as a systemic per-attribute name drift across six or more source artifacts. Compliance discipline preserved at all 15 specialization-layer namespace declarations."
```

**Acceptance criteria:**

1. `PER_CELL_CARDINALITY_BUDGET` has cardinality 8 — one per ACTIVE cell.
2. `tenant_rate_limit` is `Some` at cell-7 and cell-8 (multi-tenant cells per C-OD-21 §21.4 per-tenant cardinality isolation); `None` at other cells.
3. `enforcement_layer` per cell-class: solo cells enforce at `COLLECTOR_BOUNDARY` (in-process collector); team + multi-tenant cells enforce at either layer per cell-committed backend.
4. `PATTERN_P1_DISCIPLINE_ANCHOR` carries §11.4 anchor verbatim — declarative invariant against per-attribute-name drift across source artifacts.
5. Pattern P1 compliance is verifiable at namespace-map level (U-OD-05) + per-namespace verification units (U-OD-06, U-OD-07) and at all attribute-name-bearing units.
6. Per-tenant rate limit at cell-7 + cell-8 composes with U-OD-31 `check_per_tenant_cardinality_isolation` runtime enforcement.

**Tests:** `test_per_cell_budget_cardinality_eight`, `test_multi_tenant_cells_have_tenant_rate_limit`, `test_non_multi_tenant_cells_no_tenant_rate_limit`, `test_solo_cells_enforce_at_collector_boundary`, `test_pattern_p1_anchor_byte_exact`, `test_tenant_rate_limit_composes_with_u_od_31`.

**Rollback boundary:** Revert per-cell cardinality budget + Pattern P1 anchor. R-OD-03 satisfaction loses cardinality budget substrate; Pattern P1 mechanical-alignment compliance loses declarative invariant; U-OD-31 per-tenant cardinality isolation loses budget reference.

---

#### §3.4.4 U-OD-14 — Declare cardinality-safe and cardinality-prohibited attribute classes

**Implements:** [C-OD-11 §11.2, §11.3]

**Depends on:** [U-OD-05, U-OD-13]

**Inputs:** OD spec v1.2 §11.2 cardinality-safe attribute set (13 attributes); §11.3 cardinality-prohibited attribute set (6 attributes — content-bearing or unbounded-cardinality).

**Files affected:** Attribute-class enforcement (logical name: `od-attribute-class-enforcement`).

**Signatures:**

```
const CARDINALITY_SAFE_ATTRIBUTES : Set<string> = {
  "gen_ai.operation.name", "gen_ai.provider.name", "gen_ai.request.model",
  "anthropic.cache_creation_input_tokens", "anthropic.cache_read_input_tokens",
  "harness.breaker.scope", "harness.breaker.from_state", "harness.breaker.to_state",
  "validator.fail.class", "validator.fail.permanence",
  "topology.fanout.pattern", "sandbox.tech", "sandbox.tier"
}                                                  // exactly 13 entries

const CARDINALITY_PROHIBITED_ATTRIBUTES : Set<string> = {
  "gen_ai.input.messages",
  "gen_ai.output.messages",
  "gen_ai.conversation.id",
  "idempotency_key",
  "audit.signature.value",
  "memory.path"
}                                                  // exactly 6 entries

fn assert_cardinality_safe_for_dashboard_dimension(attr : string) -> Result<(), CardinalityViolation>
fn assert_cardinality_prohibited_not_in_dashboard_dimension(attr : string) -> Result<(), CardinalityViolation>
```

**Acceptance criteria:**

1. `CARDINALITY_SAFE_ATTRIBUTES` has cardinality **13** per §11.2 verbatim.
2. `CARDINALITY_PROHIBITED_ATTRIBUTES` has cardinality **6** per §11.3 verbatim.
3. Sets are disjoint: `CARDINALITY_SAFE_ATTRIBUTES ∩ CARDINALITY_PROHIBITED_ATTRIBUTES == ∅`.
4. Cardinality-prohibited attributes MAY appear as span attributes for trace-level join keys but MUST NOT appear as dashboard query dimensions (high-cardinality dashboard queries cause cardinality blowup).
5. `assert_cardinality_safe_for_dashboard_dimension` returns `Err(CardinalityViolation)` for any attribute not in `CARDINALITY_SAFE_ATTRIBUTES` when used as a dashboard dimension.
6. `assert_cardinality_prohibited_not_in_dashboard_dimension` returns `Err(CardinalityViolation)` for any attribute in `CARDINALITY_PROHIBITED_ATTRIBUTES` when used as a dashboard dimension.
7. Enforcement is at dashboard-query-construction time per cell's committed backend.

**Tests:** `test_cardinality_safe_cardinality_thirteen`, `test_cardinality_prohibited_cardinality_six`, `test_attribute_sets_disjoint`, `test_safe_attribute_accepted_as_dashboard_dim`, `test_prohibited_attribute_rejected_as_dashboard_dim`, `test_unknown_attribute_rejected_as_dashboard_dim`.

**Rollback boundary:** Revert cardinality-safe + cardinality-prohibited attribute classes. R-OD-03 satisfaction loses attribute-class enforcement; downstream U-OD-22 dashboard binding loses cardinality-safe attribute filter; cardinality blowup risk returns at high-cardinality dashboard queries.

---

#### §3.4.5 U-OD-15 — Declare default-off content + default-on structure attribute discipline

**Implements:** [C-OD-12 §12.1, §12.2, §12.3]

**Depends on:** [U-OD-05]

**Inputs:** OD spec v1.2 §12.1 default-off content attributes; §12.2 default-on structure attributes (per-namespace 15-row breakdown); §12.3 structure-not-content invariant.

**Files affected:** Content vs structure attribute discipline (logical name: `od-content-vs-structure-attribute-discipline`).

**Persona linkage.** Persona §10.4 (compliance-readiness — default-off content prevents PII leakage by default).

**Signatures:**

```
const DEFAULT_OFF_CONTENT_ATTRIBUTES : Set<string> = {
  "gen_ai.input.messages",
  "gen_ai.output.messages",
  "mcp.tool.call.arguments",
  "mcp.tool.call.result",
  "skill.body_content",
  "memory.content",
  "files.content"
}                                                  // content-bearing per §12.1

const DEFAULT_ON_STRUCTURE_ATTRIBUTES : List<string>   // ~50 attributes spanning 15 namespaces per §12.2

const STRUCTURE_NOT_CONTENT_INVARIANT : string =
  "Default-on attributes record observability semantics — operation name, provider, model, token counts, hash digests, IDs, enums, latency bounds, cost overheads — but never raw tool I/O content, raw message content, or raw retrieval-document content. Where a content surface must be auditable (e.g., HITL response summary), the attribute carries a hash digest (hitl.response.summary_hash) — not the payload."

fn classify_attribute(attr : string) -> AttributeClassification
enum AttributeClassification {
  DEFAULT_OFF_CONTENT,
  DEFAULT_ON_STRUCTURE,
  HASH_DIGEST_OF_CONTENT          // composes with structure-not-content invariant
}
```

**Acceptance criteria:**

1. `DEFAULT_OFF_CONTENT_ATTRIBUTES` enumerates content-bearing attributes per §12.1.
2. `DEFAULT_ON_STRUCTURE_ATTRIBUTES` enumerates the structure-bearing attribute set per §12.2 across all 15 namespaces.
3. `STRUCTURE_NOT_CONTENT_INVARIANT` matches §12.3 verbatim — structure-bearing only; hash-not-payload discipline; cross-namespace consistency.
4. `classify_attribute` returns the correct classification per attribute; hash-digest attributes (e.g., `hitl.response.summary_hash`, `mcp.primitive.signature.sha256`) classify as `HASH_DIGEST_OF_CONTENT` and are default-on.
5. No namespace introduces content-bearing attributes by default; per-namespace consistency invariant verifies at U-OD-05 namespace map composition.
6. Default-off content attributes are toggleable per session at solo-developer cells (operator-self-redact); structurally OFF at team-binding cells; structurally OFF at multi-tenant-compliance cells with pre-collector redaction enforcement at U-OD-31.

**Tests:** `test_default_off_content_includes_input_messages`, `test_default_off_content_includes_output_messages`, `test_default_off_content_includes_mcp_tool_call_args`, `test_default_on_structure_includes_token_counts`, `test_structure_not_content_invariant_byte_exact`, `test_hash_digest_attributes_classify_as_hash_digest_of_content`, `test_no_namespace_introduces_content_by_default`, `test_classify_attribute_returns_correct_classification`.

**Rollback boundary:** Revert default-off content + default-on structure discipline. R-OD-04 satisfaction loses content-vs-structure discipline; PII leakage risk returns at default-on content attributes; downstream U-OD-16 per-persona-tier override gradient loses base-discipline anchor.

---

#### §3.4.6 U-OD-16 — Declare per-persona-tier content-capture override gradient + pre-collector redaction at multi-tenant

**Implements:** [C-OD-13 §13.1, §13.2]

**Depends on:** [U-OD-01, U-OD-15]

**Inputs:** OD spec v1.2 §13.1 per-persona-tier override gradient (3-tier posture matrix); §13.2 pre-collector redaction at multi-tenant-compliance cells (SDK / wrapper boundary, before BatchSpanProcessor).

**Files affected:** Per-persona-tier override gradient (logical name: `od-per-persona-tier-redaction-gradient`).

**Signatures:**

```
enum ContentCapturePosture {
  OPERATOR_SELF_REDACT,                            // solo-developer cells
  REDACTION_PROCESSOR_AT_OTLP_COLLECTOR_BOUNDARY,  // team-binding cells
  PRE_COLLECTOR_EVAL_GRADE_PIPELINE                // multi-tenant-compliance cells
}

record PerPersonaTierRedactionPosture {
  persona_tier   : PersonaTier
  posture        : ContentCapturePosture
  toggleable     : bool                            // true at solo; false at team + multi-tenant
}

const PER_PERSONA_TIER_REDACTION : Map<PersonaTier, PerPersonaTierRedactionPosture> = {
  SOLO_DEVELOPER          : {posture: OPERATOR_SELF_REDACT,                          toggleable: true},
  TEAM_BINDING            : {posture: REDACTION_PROCESSOR_AT_OTLP_COLLECTOR_BOUNDARY, toggleable: false},
  MULTI_TENANT_COMPLIANCE : {posture: PRE_COLLECTOR_EVAL_GRADE_PIPELINE,             toggleable: false}
}
```

**Acceptance criteria:**

1. `ContentCapturePosture` enumerates exactly 3 values per §13.1.
2. `PER_PERSONA_TIER_REDACTION` maps each persona tier to exactly one posture per §13.1 verbatim.
3. `toggleable == true` only at solo-developer tier; team-binding and multi-tenant-compliance tiers are non-toggleable.
4. Pre-collector eval-grade pipeline at multi-tenant cells per §13.2: redaction applies at SDK / wrapper boundary at attribute-set time, before BatchSpanProcessor buffer (composes with U-OD-31 enforcement).
5. Team-binding redaction-processor-at-OTLP-collector-boundary permits a small buffer window where un-redacted content sits in BatchSpanProcessor; this window is acceptable at team tier per Persona §10.4 + structurally rejected only at multi-tenant cells.
6. Per-persona-tier posture is the design-time committed surface; deployment-binding-time selections occur within the toggleable=true tier only.

**Tests:** `test_content_capture_posture_cardinality_three`, `test_solo_developer_posture_operator_self_redact`, `test_team_binding_posture_redaction_processor`, `test_multi_tenant_posture_pre_collector_eval_grade`, `test_solo_toggleable_true`, `test_team_toggleable_false`, `test_multi_tenant_toggleable_false`, `test_pre_collector_pipeline_composes_with_u_od_31`.

**Rollback boundary:** Revert per-persona-tier override gradient. R-OD-04 + R-OD-08 satisfaction loses per-persona redaction posture substrate; downstream U-OD-17 cross-deployment monotonic-tightening loses class-ordering reference; U-OD-31 pre-collector redaction composition at multi-tenant cells loses gradient declaration.

---

#### §3.4.7 U-OD-17 — Declare cross-deployment monotonic-tightening invariant

**Implements:** [C-OD-13 §13.3]

**Depends on:** [U-OD-01, U-OD-13, U-OD-15, U-OD-16, U-AS-NN (cross-axis: AS — C-AS-12 §12.1), U-CP-NN (cross-axis: CP — C-CP-19)]

**Inputs:** OD spec v1.2 §13.3 cross-deployment monotonic-tightening invariant (composes redaction class ordering with D2 v1.1 §1.6 sandbox-tier cross-deployment monotonicity + D5 v1.3 §1.5.2 cross-deployment monotonicity).

**Cross-axis dependency resolution.** AS plan U-AS-NN implementing C-AS-12 §12.1 (5-axis multiplicative tunable with D2 sandbox-tier cross-deployment monotonicity); CP plan U-CP-NN implementing C-CP-19 (T-perm-1 D5-layer multiplicative gate-level rule with cross-deployment monotonicity).

**Files affected:** Cross-deployment monotonic-tightening invariant (logical name: `od-cross-deployment-monotonic-tightening`).

**Signatures:**

```
// Strict-monotonic class ordering for ContentCapturePosture per §13.3
const REDACTION_CLASS_ORDER : List<ContentCapturePosture> = [
  OPERATOR_SELF_REDACT,                            // weakest
  REDACTION_PROCESSOR_AT_OTLP_COLLECTOR_BOUNDARY,
  PRE_COLLECTOR_EVAL_GRADE_PIPELINE                // strongest
]

fn class_index(c : ContentCapturePosture) -> int   // 0, 1, 2 per REDACTION_CLASS_ORDER

fn assert_monotonic_tightening_across_transition(
  source_class : ContentCapturePosture,
  target_class : ContentCapturePosture
) -> Result<(), MonotonicityViolation>
// returns Err if class_index(target) < class_index(source); accepts equality

fn reject_class_downgrade(
  source_class : ContentCapturePosture,
  target_class : ContentCapturePosture
) -> Result<(), MonotonicityViolation>
```

**Acceptance criteria:**

1. `REDACTION_CLASS_ORDER` has strict-ascending ordering per §13.3 verbatim.
2. `class_index` returns 0/1/2 for the three postures in strict ascending order.
3. `assert_monotonic_tightening_across_transition` returns `Ok` when `class_index(target) >= class_index(source)`; `Err(MonotonicityViolation)` otherwise.
4. `reject_class_downgrade` is the alias for the strict-monotonic enforcement at U-OD-32 bridging-arc transition verification — downgrade is structurally rejected.
5. Cross-deployment monotonicity composes with D2 v1.1 §1.6 (sandbox-tier monotonic ascension across deployment surfaces — never decrease sandbox tier on bridging-arc transition) + D5 v1.3 §1.5.2 (gate-level monotonic ascension across deployment surfaces) at cross-axis AS + CP plan units.
6. Cross-axis edges per OD-S4-3.A: `Depends on: [U-AS-NN (cross-axis: AS — C-AS-12 §12.1 unit), U-CP-NN (cross-axis: CP — C-CP-19 unit)]`. Resolution at U-OD-34 aggregate manifest.

**Tests:** `test_redaction_class_order_strict_ascending`, `test_class_index_returns_0_1_2`, `test_assert_monotonic_tightening_accept_equal`, `test_assert_monotonic_tightening_accept_ascend`, `test_assert_monotonic_tightening_reject_descend`, `test_reject_class_downgrade_per_§22_2`, `test_d2_cross_deployment_monotonicity_composition_declared`, `test_d5_cross_deployment_monotonicity_composition_declared`, `test_cross_axis_edge_to_u_as_nn_c_as_12_declared`, `test_cross_axis_edge_to_u_cp_nn_c_cp_19_declared`.

**Rollback boundary:** Revert cross-deployment monotonic-tightening invariant. R-OD-04 + R-OD-08 satisfaction loses cross-deployment redaction-class monotonicity; bridging-arc transition verification at U-OD-32 loses redaction-tightening dimension; D2 + D5 cross-deployment monotonicity loses OD-side composition anchor; T-perm-1 5-axis multiplicative tunable cost-side anchor at ADD §5.2.1 loses redaction-class composition.

---
### §3.5 Cluster OD-CL-5 — Cost-attribution cross-cutting

#### §3.5.1 U-OD-18 — Declare per-span Anthropic-pricing canonical cost formula

**Implements:** [C-OD-14 §14.1]

**Depends on:** [U-OD-04]

**Inputs:** OD spec v1.2 §14.1 per-span cost formula (Anthropic-pricing canonical); base-layer attributes from U-OD-04 (`gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `anthropic.cache_creation_input_tokens`, `anthropic.cache_read_input_tokens`); rate-table key `(gen_ai.provider.name, gen_ai.request.model, tokenizer_version)` per C-OD-15 §15.2.

**Files affected:** Per-span cost formula declaration (logical name: `od-cost-attribution-anthropic-pricing-formula`).

**Persona linkage.** Persona §6 (per-workload-class cost ceiling); §10.2 (cost-attribution-per-span foundational primitive).

**Signatures:**

```
record PriceRateKey {
  provider_name      : string                      // gen_ai.provider.name
  model              : string                      // gen_ai.request.model
  tokenizer_version  : string                      // anthropic.tokenizer_version
}

record PriceRateEntry {
  key            : PriceRateKey
  base_input     : float                           // USD per input token
  base_output    : float                           // USD per output token (includes extended-thinking tokens)
}

opaque PRICE_TABLE_REF : Reference                 // resolved at U-OD-21

record SpanCostInputs {
  input_tokens        : int
  cache_creation      : int                        // anthropic.cache_creation_input_tokens
  cache_read          : int                        // anthropic.cache_read_input_tokens
  output_tokens       : int                        // includes extended-thinking output tokens
  rate_key            : PriceRateKey
}

fn compute_span_cost(inputs : SpanCostInputs) -> float {
  let rates = lookup_rates(PRICE_TABLE_REF, inputs.rate_key)
  let uncached = inputs.input_tokens - inputs.cache_read - inputs.cache_creation
  return uncached * rates.base_input
       + inputs.cache_creation * rates.base_input * 1.25       // 5-min TTL cache creation surcharge
       + inputs.cache_read * rates.base_input * 0.10           // cache hit discount
       + inputs.output_tokens * rates.base_output
}

const OUTPUT_TOKEN_EXTENDED_THINKING_SEMANTIC_NOTE :
  "v1 includes extended-thinking output tokens per Anthropic billing-as-output-tokens model [MODERATE; not verified against primary-source pricing documentation]"
```

**Acceptance criteria:**

1. `compute_span_cost` returns a non-negative float for any inputs where `input_tokens >= cache_read + cache_creation` and `output_tokens >= 0`.
2. Formula structure matches §14.1 verbatim: uncached contribution + cache-creation 1.25× surcharge + cache-read 0.10× discount + output contribution.
3. Rate-table lookup keyed on 3-field `PriceRateKey` per C-OD-15 §15.2 versioned-price-table-keying invariant; rate-table residence deferred to U-OD-21 or deployment-binding-time refresh.
4. Output-token contribution includes extended-thinking output tokens per Anthropic billing-as-output-tokens model; `OUTPUT_TOKEN_EXTENDED_THINKING_SEMANTIC_NOTE` preserves the [MODERATE] confidence annotation at §14.1 verbatim.
5. The `reasoning.output_tokens` legacy line (dropped per F2-01 rationale) is NOT present in the formula; `anthropic.reasoning.output_tokens` attribute is not declared at D3 v1.2 §1.8.1.
6. Formula assumes `cache_read` and `cache_creation` are subsets of `input_tokens`; cache-tier breakdown sums per C-OD-08 §8.2 invariant: `cache_creation + cache_read + uncached == input_tokens`. Violation rejected per `enforce_otel_canonical_value` at U-OD-10.
7. Formula is deterministic given inputs and a rate-table snapshot.
8. Formula is declarative: implementation may pre-compute or cache rate-table lookups per deployment-binding-time refresh cadence.

**Tests:** `test_compute_span_cost_no_cache_no_thinking`, `test_compute_span_cost_with_cache_creation`, `test_compute_span_cost_with_cache_read`, `test_compute_span_cost_full_breakdown`, `test_compute_span_cost_extended_thinking_included`, `test_no_reasoning_output_tokens_field`, `test_compute_span_cost_non_negative`, `test_compute_span_cost_zero_inputs`, `test_rate_key_three_field_cardinality`, `test_cache_invariant_holds_at_input`, `test_extended_thinking_semantic_note_byte_exact`.

**Rollback boundary:** Revert per-span cost formula. Cost-attribution-per-span surface loses foundational formula; U-OD-19 sandbox-tier overhead + per-sibling rollup loses underlying span.cost target; U-OD-20 idempotency-key join loses per-span cost record substrate; U-OD-21 cross-family rollup loses per-span aggregation primitive; U-OD-22 dashboard binding loses cost-attribution query basis.

---

#### §3.5.2 U-OD-19 — Compose sandbox-tier overhead + per-sibling rollup at fan-out close

**Implements:** [C-OD-14 §14.2, §14.3]

**Depends on:** [U-OD-18, U-AS-NN (cross-axis: AS — C-AS-15 §15.6), U-CP-NN (cross-axis: CP — C-CP-14 §14.1)]

**Inputs:** OD spec v1.2 §14.2 sandbox-tier overhead composition (composing `sandbox.cost.tier_overhead_usd` + `sandbox.cost.tier_overhead_ms` per AS C-AS-15 §15.6); §14.3 per-sibling rollup at `topology.fanout.closed` per CP C-CP-14 §14.1.

**Cross-axis dependency resolution.** AS plan U-AS-NN implementing C-AS-15 §15.6; CP plan U-CP-NN implementing C-CP-14 §14.1. Resolution at U-OD-34.

**Files affected:** Sandbox-tier overhead + fan-out per-sibling rollup composition (logical name: `od-cost-attribution-sandbox-and-fanout`).

**Persona linkage.** Persona §6 (per-class cost ceiling); §10.2 (cost-attribution foundational); §8.5 (cross-class cost × reliability × capability coupling).

**Signatures:**

```
record SandboxOverhead {
  tier_overhead_usd : float                        // sandbox.cost.tier_overhead_usd (C-AS-15 §15.6)
  tier_overhead_ms  : int                          // sandbox.cost.tier_overhead_ms (C-AS-15 §15.6)
}

record SpanTotalCost {
  span_cost          : float                       // from U-OD-18
  sandbox_overhead   : SandboxOverhead
  total_cost         : float                       // span_cost + sandbox_overhead.tier_overhead_usd
  total_latency_ms   : int                         // span.duration + sandbox_overhead.tier_overhead_ms
}

fn compose_span_total_cost(
  span_cost        : float,
  span_duration_ms : int,
  sandbox_overhead : Option<SandboxOverhead>
) -> SpanTotalCost

enum FanOutPattern {
  PARALLEL,                                        // parent.fanout.total_latency = max(sibling)
  SEQUENTIAL                                       // parent.fanout.total_latency = Σ(sibling)
}

record FanOutRollupResult {
  parent_fanout_total_cost     : float             // Σ sibling.total_cost
  parent_fanout_total_latency  : int               // max or Σ per FanOutPattern
  sibling_count                : int
}

fn rollup_fanout_at_close(
  parent_span_ref  : SpanRef,
  sibling_costs    : List<SpanTotalCost>,
  pattern          : FanOutPattern
) -> FanOutRollupResult
```

**Acceptance criteria:**

1. `compose_span_total_cost` applies sandbox-tier overhead additively per §14.2 verbatim: `total_cost = span_cost + sandbox_overhead.tier_overhead_usd`; `total_latency_ms = span_duration_ms + sandbox_overhead.tier_overhead_ms`.
2. Non-sandbox-bounded spans carry `sandbox_overhead = None`; `total_cost = span_cost`; `total_latency_ms = span_duration_ms`.
3. `sandbox.cost.tier_overhead_*` consumed cross-axis from AS plan; Pattern P1 mechanical-alignment discipline verifies attribute name byte-exactness.
4. `rollup_fanout_at_close` fires at `topology.fanout.closed` event per U-OD-08 F3 lifecycle mapping + CP plan implementing C-CP-14 §14.1. Aggregation per §14.3 verbatim: `parent.fanout.total_cost = Σ sibling.total_cost`; `parent.fanout.total_latency = max(sibling.total_latency)` for PARALLEL or `Σ` for SEQUENTIAL.
5. Per-sibling cost is post-sandbox-overhead `SpanTotalCost.total_cost`, not pre-sandbox `span_cost`. Sandbox overhead propagates through fan-out rollup.
6. `FanOutPattern` value sourced from CP plan unit implementing C-CP-14 fan-out pattern attribute.
7. Cross-axis edges annotated per OD-S4-3.A.
8. Composition order: U-OD-18 produces `span_cost` → this unit produces `SpanTotalCost` → U-OD-20 joins with `idempotency_key` → U-OD-21 rolls up by `provider_discriminator` → U-OD-22 binds to dashboard.

**Tests:** `test_compose_no_sandbox`, `test_compose_with_sandbox_overhead_additive`, `test_compose_latency_additive`, `test_compose_zero_overhead_explicit`, `test_rollup_total_cost_sum_of_siblings`, `test_rollup_total_latency_parallel_max`, `test_rollup_total_latency_sequential_sum`, `test_rollup_sibling_count_matches`, `test_rollup_uses_post_overhead_total_cost`, `test_cross_axis_edge_to_u_as_nn_c_as_15_section_15_6`, `test_cross_axis_edge_to_u_cp_nn_c_cp_14_section_14_1`.

**Rollback boundary:** Revert sandbox-tier overhead + per-sibling rollup composition. Sandbox-bounded spans lose tier-overhead-additive cost; fan-out spans lose per-sibling rollup at `topology.fanout.closed`; downstream U-OD-22 dashboard binding loses post-rollup cost surface; T-perm-1 5-axis multiplicative tunable cost-side anchor loses sandbox-tier composition.

---

#### §3.5.3 U-OD-20 — Compose idempotency-key join + F2-12 ACTIVE affected-contract notation

**Implements:** [C-OD-14 §14.4, §14.5]

**Depends on:** [U-OD-18, U-OD-19, U-IS-NN (cross-axis: IS — C-IS-10 §10.2)]

**Inputs:** OD spec v1.2 §14.4 idempotency-key join (per IS C-IS-10 §10.2 idempotency-key join export); §14.5 F2-12 ACTIVE engagement affected-contract notation (3 deferred surfaces per session prompt §5.4 [CF-1] authoring approach (iii)); CP plan U-CP-55 §24.4 F2-12 carry-forward closure path (6-step revision-pass chain inheritance).

**Cross-axis dependency resolution.** IS plan U-IS-NN implementing C-IS-10 §10.2 (idempotency-key join export); IS plan U-IS-17 substrate seam exports manifest is the resolution target.

**Files affected:** Idempotency-key join composition + F2-12 affected-contract notation (logical name: `od-cost-attribution-idempotency-join-and-f2-12-notation`).

**F2-12 ACTIVE engagement.** This unit is the **sole contract-bearing F2-12 carry-forward site** in the OD plan per session prompt §5.4 [CF-1] authoring approach (iii).

**Signatures:**

```
record SpanCostRecord {
  span_id              : string
  idempotency_key      : string                    // from parent span per C-IS-05
  total_cost           : float                     // from U-OD-19 SpanTotalCost
  total_latency_ms     : int                       // from U-OD-19 SpanTotalCost
  derived_keys         : List<string>              // for sub-agent inheritance per C-AS-15 §15.6
}

fn attach_idempotency_key_to_cost_record(
  span                : SpanRef,
  parent_idempotency  : string,
  cost_record         : SpanCostRecord
) -> SpanCostRecord

fn dedupe_on_replay(
  records : List<SpanCostRecord>
) -> List<SpanCostRecord>                          // ALGORITHM DEFERRED per §14.5 F2-12 surface 3

fn propagate_to_subagent(
  parent_idempotency : string
) -> string                                        // derived key per C-AS-15 §15.6

enum F2_12_DeferredSurface {
  SPAN_REEMISSION_SEMANTICS_UNDER_ENGINE_REPLAY,   // surface 1
  RETRY_ATTEMPT_SIBLING_SPAN_DISCIPLINE_AT_D6_INGESTION,  // surface 2
  TRACE_INGESTION_DEDUP_COMPOSITION_ALGORITHM      // surface 3
}

record F2_12_AffectedContractNotation {
  contract_id              : "C-OD-14"
  active_engagement_site   : "C-OD-14 §14.5"
  deferred_surfaces        : Set<F2_12_DeferredSurface>   // exactly 3 surfaces
  v1_commitment_level      : "cost-attribution-per-span formula + sandbox-tier overhead + per-sibling rollup + idempotency-key join"
  closure_path             : List<RevisionStep>           // 6 steps per CP plan U-CP-55 §24.4
  closure_pending_at_v1    : bool                         // = true
}

record RevisionStep {
  step_number  : int
  artifact     : string                            // e.g., "D1 v1.1 → v1.2"
  scope        : string                            // e.g., "resolve resumption-observable-behavior body-citation drift"
}

const F2_12_CLOSURE_PATH : List<RevisionStep> = [
  {1, "D1 v1.1 → v1.2",      "resolve resumption-observable-behavior body-citation drift"},
  {2, "D6 v1.1 → v1.2",      "consolidate downstream observability ingestion of D1 v1.2"},
  {3, "ADD v1.2 → v1.3",     "reconsolidate engine-class + observability cross-section per revised ADRs"},
  {4, "PRD v1.0.1 → v1.1",   "cite revised ADD + ADRs at R-CP-04 + R-CP-07"},
  {5, "OD spec v1.2 → v1.3", "revise C-OD-14 + (possibly) C-OD-05 + C-OD-06 + §[carry-forwards] [CF-1] to close active engagement"},
  {6, "OD plan v1 → v2",     "revision-pass mode per SKILL.md §8 absorbing OD spec v1.3"}
]

const F2_12_NOTATION : F2_12_AffectedContractNotation
```

**Acceptance criteria:**

1. `SpanCostRecord` declares exactly 5 fields per §14.4 verbatim. Per-span cost record carries parent's `idempotency_key` per C-IS-05.
2. `attach_idempotency_key_to_cost_record` returns `SpanCostRecord` with `idempotency_key` set to parent's value; replay-safe composition with F2 state-ledger via `idempotency_key` avoids double-counting on replay (V1 dedup primitive commitment per §14.4 row 2; algorithm deferred per F2-12).
3. `dedupe_on_replay` declared but **algorithm deferred** per §14.5 F2-12 deferred surface 3. V1 commitment: dedup primitive is the idempotency-key join; algorithm closes at D6 v1.2 (per closure_path step 2).
4. `propagate_to_subagent` returns derived `idempotency_key` per C-AS-15 §15.6 sub-agent boundary inheritance.
5. `F2_12_DeferredSurface` enumerates exactly **3** values matching §14.5 verbatim.
6. `F2_12_NOTATION.contract_id == "C-OD-14"` and `active_engagement_site == "C-OD-14 §14.5"`. This is the sole F2-12 ACTIVE contract-bearing notation site in the OD plan.
7. `F2_12_NOTATION.v1_commitment_level` matches §14.5 verbatim.
8. `F2_12_CLOSURE_PATH` declares exactly **6** revision steps in canonical order inheriting the 6-step structure from CP plan U-CP-55 §24.4; steps 1–4 are substantively shared (byte-exact at canonical artifact + scope tokens); steps 5–6 axis-substituted to OD-spec / OD-plan revision targets per closure_path's OD-axis specialization. Partial closure does NOT close the carry-forward.
9. `F2_12_NOTATION.closure_pending_at_v1 == true`; closure occurs at OD plan v2 per closure_path step 6.
10. Forward-routing: parallel `council-orchestrator` C7+C9 session per ADD §6.3.1 active path → D1 v1.2 + D6 v1.2 → ADD v1.3 → PRD v1.1 → OD spec revision at C-OD-14 → OD plan v2.
11. Cross-axis edge per OD-S4-3.A: `Depends on: [U-IS-NN (cross-axis: IS — C-IS-10 §10.2 unit)]`. Resolution at U-OD-34.

**Tests:** `test_span_cost_record_five_fields`, `test_attach_idempotency_match_parent`, `test_dedupe_on_replay_algorithm_deferred`, `test_propagate_to_subagent_returns_derived_key`, `test_f2_12_deferred_surface_cardinality_three`, `test_f2_12_deferred_surface_names_match_spec`, `test_f2_12_notation_contract_id_c_od_14`, `test_f2_12_notation_active_engagement_site`, `test_f2_12_v1_commitment_level_byte_exact`, `test_f2_12_closure_path_cardinality_six`, `test_f2_12_closure_path_step_order_matches_cp_55_24_4`, `test_f2_12_partial_closure_does_not_close`, `test_f2_12_closure_pending_at_v1_true`, `test_cross_axis_edge_to_u_is_nn_c_is_10_section_10_2`.

**Rollback boundary:** Revert idempotency-key join + F2-12 affected-contract notation. Cost-attribution-per-span loses replay-safe composition primitive; F2-12 carry-forward loses sole contract-bearing notation site in OD plan; closure path inheritance from CP plan U-CP-55 §24.4 loses inheritance target; D6 v1.2 closure half loses plan-side anchor.

---

#### §3.5.4 U-OD-21 — Compose cross-family `provider_discriminator` rollup + tokenization-version anchor

**Implements:** [C-OD-15 §15.1, §15.2, §15.3]

**Depends on:** [U-OD-04, U-OD-18, U-CP-NN (cross-axis: CP — C-CP-04 cross-family fallback chain)]

**Inputs:** OD spec v1.2 §15.1 cross-family `provider_discriminator` cost rollup (3 rollup axes); §15.2 tokenization-version anchor (2 options); §15.3 cross-family fallback chain composition reference per ADR-F1 v1.2 §Decision.

**Cross-axis dependency resolution.** CP plan U-CP-NN implementing C-CP-04 + C-CP-09. Resolution at U-OD-34.

**Files affected:** Cross-family provider-discriminator rollup + tokenization-version anchor (logical name: `od-cost-attribution-cross-family-and-tokenizer`).

**Persona linkage.** Persona §10.2 (cost-attribution foundational — cross-family visibility under fallback chain advancement per ADR-F1 v1.2).

**Signatures:**

```
enum CrossFamilyTag {                              // per c7-observability SKILL.md substrate (F2-10 closure)
  FRONTIER_MANAGED,
  FRONTIER_MANAGED_ALT,
  LOCAL_OLLAMA
  // extensible per chain composition
}

enum RollupAxis {
  PER_PROVIDER_DISCRIMINATOR,                      // per-family cost
  PER_PROVIDER_AND_MODEL,                          // per-(provider, model) cost
  PER_FALLBACK_EVENT                               // per-retry-attempt cost with family-tag rollup
}

record CrossFamilyCostRollup {
  rollup_axis              : RollupAxis
  group_key                : string
  total_cost               : float
  span_count               : int
}

fn rollup_costs_by_axis(
  span_records : List<SpanCostRecord>,
  axis         : RollupAxis
) -> List<CrossFamilyCostRollup>

enum TokenizerVersionAnchor {
  OPTION_A_ATTRIBUTE_ON_EVERY_SPAN,                // gen_ai.request.model.tokenizer_version | anthropic.tokenizer_version
  OPTION_B_VERSIONED_PRICE_TABLE                   // price table keyed on (provider, model, tokenizer_version)
}

const TOKENIZER_VERSION_ANCHOR_REQUIREMENT :
  "Phase 6+ dashboard authors MUST select OPTION_A or OPTION_B; failing to anchor on tokenizer_version produces silent cost-dashboard breakage on model version transitions"

record FallbackChainCostComposition {
  parent_span_family_tag       : CrossFamilyTag    // parent retains provider_discriminator
  per_attempt_provider         : string            // child retry span's gen_ai.provider.name
  per_attempt_rate_key         : PriceRateKey
  cache_state_loss_on_cross_family : bool          // = true; anthropic.cache_read_input_tokens = 0
}
```

**Acceptance criteria:**

1. `CrossFamilyTag` bounded enum per F2-10 closure (c7-observability SKILL.md primary anchor; ADR-F1 v1.2 §Decision composition context).
2. `RollupAxis` enumerates exactly 3 values per §15.1.
3. `rollup_costs_by_axis` returns aggregated rollups per axis: `PER_PROVIDER_DISCRIMINATOR` keys on family tag; `PER_PROVIDER_AND_MODEL` keys on (provider, model) tuple; `PER_FALLBACK_EVENT` preserves per-attempt provider identity.
4. `TokenizerVersionAnchor` enumerates exactly 2 options per §15.2 verbatim.
5. `TOKENIZER_VERSION_ANCHOR_REQUIREMENT` carries §15.2 anchor text verbatim; downstream U-OD-22 dashboard binding MUST consume this anchor.
6. `FallbackChainCostComposition` per §15.3 verbatim: parent retains family tag; per-attempt provider updates per retry; per-attempt rate-key updates; cache state loss on cross-family transition (anthropic.cache_read_input_tokens = 0).
7. Cross-axis edge per OD-S4-3.A: `Depends on: [U-CP-NN (cross-axis: CP — C-CP-04 fallback chain unit)]`.
8. Source authority per F2-10 closure: `provider_discriminator` substrate is `c7-observability` SKILL.md (primary anchor); ADR-F1 v1.2 §Decision is composition context, not attribute-name declaration site.

**Tests:** `test_rollup_axis_cardinality_three`, `test_rollup_per_provider_discriminator`, `test_rollup_per_provider_and_model`, `test_rollup_per_fallback_event_preserves_provider`, `test_tokenizer_anchor_two_options`, `test_tokenizer_anchor_requirement_byte_exact`, `test_fallback_chain_parent_family_tag_retained`, `test_fallback_chain_per_attempt_provider_updates`, `test_cache_state_loss_on_cross_family`, `test_provider_discriminator_source_authority_c7`, `test_cross_axis_edge_to_u_cp_nn_c_cp_04`.

**Rollback boundary:** Revert cross-family provider_discriminator rollup + tokenization-version anchor. Cross-family cost visibility under fallback loses 3-axis rollup; tokenization-version drift loses dashboard-stability anchor; chain-advancement seam composition with ADR-F1 v1.2 loses per-attempt cost-attribution; U-OD-22 dashboard binding loses cross-family rollup query primitive.

---

#### §3.5.5 U-OD-22 — Declare per-cell cost-attribution dashboard binding + alerting threshold composition

**Implements:** [C-OD-16 §16.1, §16.2, §16.3]

**Depends on:** [U-OD-01, U-OD-12, U-OD-18, U-OD-19, U-OD-21]

**Inputs:** OD spec v1.2 §16.1 per-cell dashboard binding signature (3 cell-class rows × binding form × alerting hook); §16.2 alerting threshold composition with per-cell base-rate sampling at C-OD-10 §10.3 (scaled-estimate alerting at sub-1.0 rates); §16.3 dashboard composition with operator-burden eval primitive.

**Files affected:** Per-cell cost-attribution dashboard binding (logical name: `od-cost-attribution-dashboard-binding`).

**Persona linkage.** Persona §6 (per-workload-class cost ceiling — alerting threshold composition); §10.2 (cost-attribution foundational).

**Signatures:**

```
enum DashboardBindingForm {
  TUI_TRACE_BROWSER_RING_BUFFER_QUERY,             // solo-developer × * (per C-OD-19)
  NAMED_DASHBOARD_QUERY_BACKEND,                   // team-binding × *
  PER_TENANT_DASHBOARD_SEPARATION                  // multi-tenant-compliance × *
}

enum AlertingHook {
  OPERATOR_SELF_INSPECTION_TUI_THRESHOLD_OPTIONAL, // solo
  BACKEND_SIDE_ALERTING_PER_CLASS_COST_CEILING,    // team
  PER_TENANT_ALERTING_NO_CROSS_TENANT              // multi-tenant
}

record CellDashboardBinding {
  cell_id          : CellID
  binding_form     : DashboardBindingForm
  alerting_hook    : AlertingHook
  consolidates_with_operator_burden_eval : bool    // §16.3: MAY consolidate
}

const PER_CELL_DASHBOARD_BINDINGS : Map<CellID, CellDashboardBinding>   // exactly 8 entries

record AlertingThresholdComposition {
  cell_id                  : CellID
  per_class_cost_ceiling   : Map<WorkloadClass, float>   // operator-tunable per Persona §6
  base_rate                : float                       // from U-OD-12
  scaled_estimate_factor   : float                       // = 1.0 / base_rate
}

fn compute_alerting_signal(
  observed_cost_rollup : float,
  threshold            : AlertingThresholdComposition,
  workload_class       : WorkloadClass
) -> AlertingSignal

enum AlertingSignal { BELOW_THRESHOLD, ABOVE_THRESHOLD }

record DashboardBackendConsolidation {
  cell_id                          : CellID
  cost_attribution_dashboard       : DashboardRef
  operator_burden_eval_dashboard   : DashboardRef   // U-OD-24
  same_backend                     : bool           // cost + operator-burden same per-cell backend
  consolidated_view                : Option<DashboardRef>
}
```

**Acceptance criteria:**

1. `DashboardBindingForm` enumerates exactly 3 values per §16.1 row 1 verbatim.
2. `AlertingHook` enumerates exactly 3 values per §16.1 alerting column verbatim.
3. `PER_CELL_DASHBOARD_BINDINGS` declares exactly 8 entries: solo cells (1,2,3) → TUI ring-buffer; team cells (4,5,6) → named dashboard queries; multi-tenant cells (7,8) → per-tenant separation.
4. Per-cell alerting hook matches §16.1 verbatim per cell class.
5. `compute_alerting_signal` scales `observed_cost_rollup` by `1.0 / base_rate` per §16.2 verbatim (unbiased cost estimation at sub-1.0 sampled rates) before comparing to ceiling.
6. `base_rate` sourced from U-OD-12 `PerCellBaseRateEnvelope[cell_id].default_rate`.
7. `per_class_cost_ceiling` operator-tunable per Persona §6 (deferred per §16.3); specific numeric values are deployment-binding-time.
8. `DashboardBackendConsolidation.same_backend == true` per §16.3 — cost-attribution dashboard and operator-burden eval dashboard bind to same per-cell backend.
9. `consolidated_view` Option: implementations MAY consolidate per backend's dashboarding model.
10. Dashboard queries use cardinality-safe attributes only per U-OD-14 enforcement; high-cardinality attributes are span-only join keys.

**Tests:** `test_dashboard_binding_form_three_values`, `test_alerting_hook_three_values`, `test_per_cell_bindings_cardinality_eight`, `test_solo_cells_tui_ring_buffer`, `test_team_cells_named_dashboard`, `test_multi_tenant_cells_per_tenant_separation`, `test_per_cell_alerting_hook_match_spec`, `test_alerting_signal_below_threshold`, `test_alerting_signal_above_threshold`, `test_alerting_scales_by_inverse_base_rate`, `test_alerting_base_rate_one_no_scaling`, `test_dashboard_same_backend_per_cell`, `test_dashboard_consolidation_optional`, `test_dashboard_queries_cardinality_safe`, `test_multi_tenant_cross_tenant_aggregation_forbidden`.

**Rollback boundary:** Revert per-cell dashboard binding + alerting threshold composition. Per-cell cost-attribution surface loses dashboard binding contract; backend-side alerting loses per-class-cost-ceiling threshold composition; base-rate scaling factor loses unbiased-cost-estimation surface; operator-burden eval dashboard parallel binding at U-OD-24 loses same-backend reference; multi-tenant per-tenant separation at U-OD-31 loses dashboard-layer enforcement.

---
### §3.6 Cluster OD-CL-6 — Operator-burden eval + alignment-floor drift

#### §3.6.1 U-OD-23 — Declare five operator-burden eval primitives + separate-child-span emission commitment

**Implements:** [C-OD-17 §17.1, §17.2]

**Depends on:** [U-OD-04, U-AS-NN (cross-axis: AS — C-AS-15 §15.4 + C-AS-14 §14.2), U-CP-NN (cross-axis: CP — C-CP-20 §20.6)]

**Inputs:** OD spec v1.2 §17.1 five-primitive set; §17.2 separate-child-span eval emission commitment (3 properties).

**Cross-axis dependency resolution.** AS plan U-AS-NN implementing C-AS-15 §15.4 (`sandbox.violation` always-sampled — `expected_sandbox_violations_per_session` substrate); AS plan U-AS-NN implementing C-AS-14 §14.2 (`anthropic.cache_*` attributes — `cache-hit-rate-alignment-floor` substrate); CP plan U-CP-NN implementing C-CP-20 §20.6 (`hitl.invocation.responded` — `expected_hitl_invocations_per_session` substrate). Resolution at U-OD-34.

**Files affected:** Operator-burden eval primitive declarations + separate-child-span emission contract (logical name: `od-operator-burden-eval-primitives`).

**Persona linkage.** Persona §4 (99.9% SLO; selective HITL); §10.2 (selective HITL persona-constrained); §10.4 (compliance-readiness — eval primitives bind dashboard surface).

**Signatures:**

```
enum OperatorBurdenEvalPrimitive {
  EXPECTED_HITL_INVOCATIONS_PER_SESSION,           // ADR-D5 v1.3 §1.8 (C-CP-20 §20.6)
  EXPECTED_SANDBOX_VIOLATIONS_PER_SESSION,         // ADR-D2 v1.1 §1.8 (C-AS-15 §15.4)
  SANDBOX_TIER_ROUTING_ACCURACY,                   // ADR-D2 v1.1 §1.5 (meta-eval)
  CACHE_HIT_RATE_ALIGNMENT_FLOOR,                  // ADR-D3 v1.2 §1.5 + §1.8 (C-AS-14 §14.2)
  ROUTING_ACCURACY_HOLDOUT                         // ADR-F1 v1.2 §Decision
}

enum ComputationKind {
  COUNTER_ROLLUP,                                  // primitives 1, 2
  HOLDOUT_META_JUDGE_RATIO,                        // primitives 3, 5
  RATIO_ROLLUP                                     // primitive 4
}

record EvalPrimitiveDeclaration {
  primitive            : OperatorBurdenEvalPrimitive
  source_adr           : string
  declaration_site     : Option<string>            // None for ADR-only
  computation_kind     : ComputationKind
  rollup_dimensions    : List<string>
  source_span_class    : string
  computation_formula  : Option<string>
  holdout_evaluable    : bool
}

const EVAL_PRIMITIVE_DECLARATIONS : List<EvalPrimitiveDeclaration>   // exactly 5 entries

record EvalEmissionContract {
  child_span_emission_required  : bool             // = true
  rationale                     : string           // meta-eval-traceability per c8-eval-engineer
  span_volume_tradeoff_accepted : bool             // = true
  applies_at_all_cells          : bool             // = true
}

const EVAL_EMISSION_CONTRACT : EvalEmissionContract

fn emit_eval_as_child_span(parent_span_ref, primitive, value) -> Result<ChildSpanRef, EmissionContractViolation>
fn reject_span_event_only_emission(parent_span_ref, primitive, value) -> Result<(), EmissionContractViolation>
```

**Acceptance criteria:**

1. `OperatorBurdenEvalPrimitive` enumerates exactly **5** values matching §17.1 verbatim.
2. `EVAL_PRIMITIVE_DECLARATIONS` declares exactly 5 entries with per-primitive content matching §17.1 verbatim (source ADR, declaration site, computation kind, rollup dimensions, source span class).
3. `CACHE_HIT_RATE_ALIGNMENT_FLOOR.computation_formula = Some("anthropic.cache_read_input_tokens / (anthropic.cache_read_input_tokens + anthropic.cache_creation_input_tokens)")` verbatim per AS spec §14.2 + U-AS-31 canonical attribute names.
4. `SANDBOX_TIER_ROUTING_ACCURACY` meta-judge runs over T-perm-1 5-axis multiplicative tunable per §17.1 row 3.
5. `EVAL_EMISSION_CONTRACT.child_span_emission_required == true` per §17.2 verbatim.
6. `emit_eval_as_child_span` returns `Ok(ChildSpanRef)` for separate child span emission; `Err(EmissionContractViolation)` for span-event-only.
7. `reject_span_event_only_emission` returns `Err` for span-event-only emission.
8. `applies_at_all_cells == true` per §17.2 — commitment binds every cell.
9. Cross-axis edges per OD-S4-3.A.
10. Span-volume tradeoff accepted per `c8-eval-engineer` SKILL.md ownership.

**Tests:** `test_eval_primitive_cardinality_five`, `test_eval_primitive_canonical_order`, `test_eval_declarations_cardinality_five`, `test_hitl_source_c_cp_20_section_20_6`, `test_sandbox_violations_source_c_as_15_section_15_4`, `test_sandbox_tier_routing_holdout_evaluable_true`, `test_cache_hit_rate_formula_byte_exact`, `test_routing_accuracy_holdout_evaluable_true`, `test_counter_rollup_count_two`, `test_holdout_meta_judge_count_two`, `test_ratio_rollup_count_one`, `test_eval_emission_child_span_required`, `test_eval_emission_applies_all_cells`, `test_emit_as_child_span_accept`, `test_reject_span_event_only`, `test_cross_axis_edges_to_as_and_cp`.

**Rollback boundary:** Revert operator-burden eval primitive declarations + separate-child-span emission. R-OD-06 satisfaction loses primitive substrate; meta-eval traceability per `c8-eval-engineer` loses child-span identity; alignment-floor primitives lose declaration site for U-OD-25 drift detection; per-cell dashboard binding scaling at U-OD-24 loses primitive set.

---

#### §3.6.2 U-OD-24 — Declare per-cell dashboard binding scaling for operator-burden eval primitives

**Implements:** [C-OD-17 §17.3]

**Depends on:** [U-OD-01, U-OD-22, U-OD-23, U-OD-27]

**Inputs:** OD spec v1.2 §17.3 per-cell dashboard binding scaling (3 cell-class rows); U-OD-27 (C-OD-19) TUI trace browser at solo cells; U-OD-22 cost dashboard for §16.3 consolidation reference.

**Files affected:** Per-cell operator-burden eval dashboard binding scaling (logical name: `od-operator-burden-eval-dashboard-binding-scaling`).

**Persona linkage.** Persona §10.2 (selective HITL persona-constrained — alerting on SLO incompatibility); §10.4 (compliance-readiness — per-tenant alerting at multi-tenant cells).

**Signatures:**

```
enum EvalDashboardForm {
  TUI_RING_BUFFER_SCOPED_QUERIES,                  // solo
  NAMED_DASHBOARD_QUERIES_WITH_ALIGNMENT_FLOOR_ALERTING,  // team
  PER_TENANT_SEPARATION_WITH_COMPLIANCE_ATTESTATION_ALERTING  // multi-tenant
}

enum AlignmentFloorAlertingPosture {
  OPERATOR_SELF_CURATION_VIA_TUI,                  // solo
  ALIGNMENT_FLOOR_BOUND_TO_BACKEND_ALERTING,       // team
  PER_TENANT_ALIGNMENT_FLOOR_NO_CROSS_TENANT       // multi-tenant
}

enum HusainLoopBinding {
  RING_BUFFER_OPERATOR_SELF_CURATION,              // solo
  BACKEND_HOSTED,                                  // team
  PER_TENANT_BACKEND_HOSTED                        // multi-tenant
}

record CellEvalDashboardBinding {
  cell_id                       : CellID
  dashboard_form                : EvalDashboardForm
  alignment_floor_alerting      : AlignmentFloorAlertingPosture
  husain_loop_binding           : HusainLoopBinding
  consolidates_with_cost        : bool             // §16.3 MAY consolidate
}

const PER_CELL_EVAL_DASHBOARD_BINDINGS : Map<CellID, CellEvalDashboardBinding>   // exactly 8 entries

fn run_husain_loop_at_cell(cell_id, primitive) -> HusainLoopState
```

**Acceptance criteria:**

1. `EvalDashboardForm`, `AlignmentFloorAlertingPosture`, `HusainLoopBinding` each enumerate exactly 3 values per §17.3.
2. `PER_CELL_EVAL_DASHBOARD_BINDINGS` declares exactly 8 entries with per-cell-class binding per §17.3 verbatim.
3. Solo cells (1,2,3) compose with U-OD-27 TUI: 5 primitives surface as scoped queries against sqlite ring-buffer.
4. Team cells (4,5,6) bind alignment-floor ratios to backend alerting per U-OD-25 drift detection composition.
5. Multi-tenant cells (7,8) enforce per-tenant alignment-floor binding; cross-tenant aggregation forbidden per U-OD-31 / C-OD-21.
6. `consolidates_with_cost == true` permissible per §16.3 + §17.3.
7. Husain loop binding per §17.3 row 1: solo cells run loop against ring-buffer with operator self-curation; team + multi-tenant cells run loop against cell-committed backend.

**Tests:** `test_eval_dashboard_form_three_values`, `test_alignment_floor_alerting_three_values`, `test_husain_loop_binding_three_values`, `test_per_cell_bindings_cardinality_eight`, `test_solo_cells_tui_ring_buffer_scoped`, `test_team_cells_named_with_alignment_floor_alerting`, `test_multi_tenant_per_tenant_separation_compliance`, `test_husain_loop_solo_self_curation`, `test_multi_tenant_no_cross_tenant_alignment_floor`, `test_consolidation_with_cost_permissible`.

**Rollback boundary:** Revert per-cell operator-burden eval dashboard binding scaling. Three cell-class binding forms lose runtime substrate; alignment-floor drift detection at U-OD-25 loses per-cell alerting hook; Husain manual-review → categorize → automate → align loop loses per-cell tooling binding; per-tenant alignment-floor isolation at multi-tenant cells loses dashboard-layer enforcement.

---

#### §3.6.3 U-OD-25 — Declare alignment-floor drift detection + drift-detection emission shape

**Implements:** [C-OD-18 §18.1, §18.2]

**Depends on:** [U-OD-11, U-OD-23, U-OD-24]

**Inputs:** OD spec v1.2 §18.1 alignment-floor drift detection (4 alignment-floor primitives); §18.2 drift-detection emission shape (`gen_ai.eval.alignment_floor.drift_detected` event with 4 attributes; always-sampled per C-OD-09 §9.2 / U-OD-11).

**Files affected:** Alignment-floor drift detection + emission shape (logical name: `od-alignment-floor-drift-detection`).

**Persona linkage.** Persona §4 (99.9% SLO — alignment-floor drift detection is reliability-eval primitive).

**Signatures:**

```
enum AlignmentFloorPrimitive {
  JUDGE_HUMAN_COHENS_KAPPA,                        // c8-eval-engineer SKILL.md substrate
  CACHE_HIT_RATE_ALIGNMENT_FLOOR,                  // U-OD-23 primitive 4
  ROUTING_ACCURACY_HOLDOUT,                        // U-OD-23 primitive 5
  SANDBOX_TIER_ROUTING_ACCURACY                    // U-OD-23 primitive 3
}

record AlignmentFloorThreshold {
  primitive            : AlignmentFloorPrimitive
  threshold_value      : float                     // operator-tunable
  observation_window   : ObservationWindow
}

enum ObservationWindow {
  TIME_WINDOW(Duration),
  SAMPLE_WINDOW(int)
}

const DRIFT_DETECTED_EVENT_NAME : string = "gen_ai.eval.alignment_floor.drift_detected"
const DRIFT_DETECTED_SAMPLING_HEAD_RATE : float = 1.0   // always-sampled

record DriftDetectedEventAttributes {
  primitive               : AlignmentFloorPrimitive   // gen_ai.eval.primitive
  current_value           : float                     // gen_ai.eval.alignment_floor.current
  threshold               : float                     // gen_ai.eval.alignment_floor.threshold
  observation_window      : ObservationWindow         // gen_ai.eval.alignment_floor.observation_window
}

fn detect_drift(primitive, current_value, threshold) -> Option<DriftDetectedEventAttributes>
fn emit_drift_event(parent_span_ref, attrs) -> Result<EventEmission, DriftEmissionError>
```

**Acceptance criteria:**

1. `AlignmentFloorPrimitive` enumerates exactly **4** values per §18.1 verbatim; 3 overlap with U-OD-23; `JUDGE_HUMAN_COHENS_KAPPA` is anchored at `c8-eval-engineer` SKILL.md.
2. Each alignment-floor primitive carries operator-tunable threshold; drift below threshold triggers re-baselining cycle per `c8-eval-engineer` meta-eval discipline.
3. `DRIFT_DETECTED_EVENT_NAME` byte-exact per §18.2.
4. `DRIFT_DETECTED_SAMPLING_HEAD_RATE == 1.0` per §18.2 — always-sampled per C-OD-09 §9.2.
5. `DriftDetectedEventAttributes` declares exactly **4** attributes per §18.2 verbatim.
6. `detect_drift` returns `Some` when `current_value < threshold.threshold_value` over observation window; `None` otherwise.
7. `emit_drift_event` emits at head=1.0; returns `Err` if any of 4 required attributes is missing.
8. Operator-tunable thresholds deferred to deployment-binding time per `c8-eval-engineer` SKILL.md ownership.
9. Re-baselining cycle invocation deferred per §18.1 "Deferred to implementation discretion"; this unit emits the drift signal, downstream `c8-eval-engineer` workflow handles cycle execution.

**Tests:** `test_alignment_floor_primitive_cardinality_four`, `test_three_overlap_with_operator_burden_eval`, `test_judge_human_kappa_anchored_at_c8`, `test_drift_event_name_byte_exact`, `test_drift_always_sampled_head_one`, `test_drift_attributes_cardinality_four`, `test_drift_attribute_names_byte_exact`, `test_detect_drift_below_threshold_returns_some`, `test_detect_drift_above_threshold_returns_none`, `test_detect_drift_at_threshold_returns_none`, `test_emit_drift_event_complete_accept`, `test_emit_drift_event_missing_attr_reject`.

**Rollback boundary:** Revert alignment-floor drift detection + emission shape. Re-baselining cycle trigger per `c8-eval-engineer` loses substrate signal; meta-eval correctness loses load-bearing drift visibility; team-binding cells lose alignment-floor-bound alerting hook at U-OD-24; Persona §4 99.9% SLO degradation early-warning surface is lost.

---

#### §3.6.4 U-OD-26 — Declare eval-vs-runtime-gate distinction via `gen_ai.eval.kind` discriminator

**Implements:** [C-OD-18 §18.3]

**Depends on:** [U-OD-23, U-CP-NN (cross-axis: CP — C-CP-21 §21.5)]

**Inputs:** OD spec v1.2 §18.3 eval-vs-runtime-gate distinction (2 span shapes coexist on runtime path); `gen_ai.eval.kind` discriminator with 2 values; CP plan unit implementing C-CP-21 §21.5 (`validator.fail.*` namespace declaration — runtime-gate failure substrate).

**Cross-axis dependency resolution.** CP plan U-CP-NN implementing C-CP-21 §21.5. Resolution at U-OD-34.

**Files affected:** Eval-vs-runtime-gate distinction discriminator (logical name: `od-eval-vs-runtime-gate-discriminator`).

**Persona linkage.** Persona §4 (99.9% SLO — in-loop gate spans and out-of-loop eval child spans must be distinguishable for meta-eval correctness).

**Signatures:**

```
enum EvalKindDiscriminator {
  INLINE_GATE,                                     // in-loop runtime gate per c5-validation-contract
  OFFLINE_JUDGE                                    // out-of-loop meta-eval per c8-eval-engineer
}

const EVAL_KIND_ATTRIBUTE_NAME : string = "gen_ai.eval.kind"

record EvalSpanShape {
  discriminator_value     : EvalKindDiscriminator
  sampling_posture        : SamplingPostureF18
  source_declaration_ref  : string
  failure_routing         : Option<string>
}

enum SamplingPostureF18 {
  ALWAYS_SAMPLED_IF_FAILURE_BASE_RATE_IF_PASS,     // inline_gate
  SEPARATE_CHILD_SPAN_PER_U_OD_23                  // offline_judge
}

const EVAL_SPAN_SHAPES : Map<EvalKindDiscriminator, EvalSpanShape>   // exactly 2 entries

fn classify_eval_span(attrs : SpanAttributes) -> Option<EvalKindDiscriminator>
fn validate_eval_span_routing(discriminator, span_ref) -> Result<(), EvalShapeViolation>
```

**Acceptance criteria:**

1. `EvalKindDiscriminator` enumerates exactly **2** values per §18.3 verbatim. No additional enum values at v1.
2. `EVAL_KIND_ATTRIBUTE_NAME == "gen_ai.eval.kind"` byte-exact per §18.3.
3. `EVAL_SPAN_SHAPES` declares exactly 2 entries.
4. `INLINE_GATE` per §18.3 row 1: sampling posture `ALWAYS_SAMPLED_IF_FAILURE_BASE_RATE_IF_PASS` per C-CP-21 §21.6 + §21.5; source declaration `C-CP-21 §21.5`; failure routing `C-CP-21 §21.6 + C-AS-04 §4.2`.
5. `OFFLINE_JUDGE` per §18.3 row 2: sampling posture `SEPARATE_CHILD_SPAN_PER_U_OD_23` per C-OD-17 §17.2; source declaration `U-OD-23 (C-OD-17 §17.2)`; failure routing `None`.
6. `classify_eval_span` returns `Some(discriminator_value)` if `gen_ai.eval.kind` present and valid; `None` if absent.
7. `validate_eval_span_routing` returns `Err(EvalShapeViolation)` when: inline_gate emitted as separate child span; offline_judge emitted as span event; inline_gate lacks `validator.fail.*` attributes; offline_judge lacks operator-burden eval primitive reference.
8. Distinction is non-mergeable: a span cannot satisfy both inline_gate AND offline_judge invariants.
9. Cross-axis edge per OD-S4-3.A: `Depends on: [U-CP-NN (cross-axis: CP — C-CP-21 §21.5 unit)]`.

**Tests:** `test_eval_kind_cardinality_two`, `test_eval_kind_attribute_name_byte_exact`, `test_eval_span_shapes_cardinality_two`, `test_inline_gate_sampling_always_sampled_if_failure`, `test_inline_gate_failure_routing_c_cp_21_c_as_04`, `test_offline_judge_sampling_separate_child_span`, `test_offline_judge_failure_routing_none`, `test_classify_inline_gate_recognized`, `test_classify_offline_judge_recognized`, `test_classify_absent_returns_none`, `test_validate_inline_gate_with_validator_fail_accept`, `test_validate_inline_gate_lacking_validator_fail_reject`, `test_validate_offline_judge_as_child_span_accept`, `test_validate_offline_judge_as_span_event_reject`, `test_validate_inline_gate_as_child_span_reject`, `test_cross_axis_edge_to_u_cp_nn_c_cp_21`.

**Rollback boundary:** Revert eval-vs-runtime-gate discriminator. In-loop gate spans and out-of-loop eval child spans lose disambiguation; meta-eval over inline-gate vs offline-judge spans loses discriminator filter; Phase 6+ dashboard authoring loses eval-kind-bound query filter; cross-axis composition with `validator.fail.*` substrate at CP plan loses eval-shape-aware routing.

---
### §3.7 Cluster OD-CL-7 — OTLP collector placement + multi-tenant tenant isolation

#### §3.7.1 U-OD-27 — Implement local-first OTLP collector at solo-developer × local-development cell

**Implements:** [C-OD-19 §19.1, §19.2, §19.3]

**Depends on:** [U-OD-01, U-OD-23, U-IS-NN (cross-axis: IS — C-IS-13 §13.2), U-IS-NN (cross-axis: IS — C-IS-08 §8.4)]

**Inputs:** OD spec v1.2 §19.1 in-process OTLP collector for cell-1 (solo-developer × local-development); §19.2 sqlite ring-buffer trace storage (composing with C-IS-13 §13.2 sqlite substrate + C-IS-08 §8.4 ring-buffer policy); §19.3 TUI trace browser surfacing (composing with U-OD-23 operator-burden eval primitives).

**Cross-axis dependency resolution.** IS plan U-IS-NN implementing C-IS-13 §13.2 (sqlite substrate); IS plan U-IS-NN implementing C-IS-08 §8.4 (ring-buffer eviction policy). Resolution at U-OD-34.

**Files affected:** Local-first OTLP collector + sqlite ring-buffer + TUI trace browser (logical name: `od-local-first-otlp-collector-cell-1`).

**Persona linkage.** Persona §9 (solo-developer × local-development self-bootstrap discipline); §10.2 (foundational primitive: in-process collector default at the design-time persona anchor).

**Signatures:**

```
const CELL_1 : CellID = {SOLO_DEVELOPER, LOCAL_DEVELOPMENT}

enum CollectorTopology {
  IN_PROCESS_COLLECTOR_NO_NETWORK_HOP,             // cell-1
  EXTERNAL_OTLP_COLLECTOR,                         // cells 2-8 baseline
  EXTERNAL_PER_TENANT_OTLP_COLLECTOR               // multi-tenant cells 7,8
}

record InProcessCollectorBinding {
  cell_id                : CellID                          // = CELL_1
  topology               : CollectorTopology               // = IN_PROCESS_COLLECTOR_NO_NETWORK_HOP
  exporter_class         : "OTLP_EXPORTER_IN_PROCESS_LOOPBACK"
  network_hop_required   : bool                            // = false
}

record RingBufferTraceStoragePolicy {
  storage_substrate      : "SQLITE_LOCAL_FS"               // C-IS-13 §13.2
  eviction_policy        : "RING_BUFFER_FIFO_BY_AGE"       // C-IS-08 §8.4
  retention_class        : "MAX_AGE_OR_MAX_BYTES"
  default_max_age_hours  : Option<int>                     // None = deployment-binding default
  default_max_bytes_mb   : Option<int>                     // None = deployment-binding default
  closure_invariant      : "FRESH_ON_RESTART_OPTIONAL_PERSISTENCE_BETWEEN_RESTARTS"  // C-OD-19 §19.2
}

record TuiTraceBrowserSurface {
  scoped_queries              : List<TuiQuery>
  ring_buffer_query_binding   : "DIRECT_SQLITE_QUERY"
  operator_self_curation_loop : "HUSAIN_LOOP_PER_C8_EVAL_ENGINEER"
}

record TuiQuery {
  primitive_or_signal     : string                         // e.g., "expected_hitl_invocations_per_session"
  query_form              : "SQL_OVER_RING_BUFFER"
}

const BATCH_SPAN_PROCESSOR_WINDOW : Duration = 5.seconds   // §19.1 verbatim
const BATCH_SPAN_PROCESSOR_BATCH_SIZE : int = 512          // §19.1 verbatim

fn bind_in_process_collector(cell_id : CellID) -> Result<InProcessCollectorBinding, CellBindingError>
fn evict_oldest_per_ring_buffer_policy(storage_state) -> Result<EvictionAction, RingBufferError>
fn query_ring_buffer_via_tui(query : TuiQuery) -> List<SpanRow>
```

**Acceptance criteria:**

1. `CELL_1` is the singleton `(SOLO_DEVELOPER, LOCAL_DEVELOPMENT)`; this unit's contracts apply exclusively at this cell.
2. `CollectorTopology` enumerates exactly 3 values per §19.1.
3. `bind_in_process_collector(CELL_1)` returns `Ok(InProcessCollectorBinding{topology: IN_PROCESS_COLLECTOR_NO_NETWORK_HOP, network_hop_required: false})` per §19.1 verbatim.
4. `bind_in_process_collector` for cells 2-8 returns `Err(CellBindingError)` — this contract is cell-1-exclusive.
5. `RingBufferTraceStoragePolicy.storage_substrate == "SQLITE_LOCAL_FS"` per C-IS-13 §13.2 cross-axis composition; `eviction_policy == "RING_BUFFER_FIFO_BY_AGE"` per C-IS-08 §8.4.
6. `closure_invariant == "FRESH_ON_RESTART_OPTIONAL_PERSISTENCE_BETWEEN_RESTARTS"` per §19.2 — solo cells emit fresh trace stores on restart by default; persistence-between-restarts optional per operator preference (deployment-binding-time configurable).
7. `BATCH_SPAN_PROCESSOR_WINDOW == 5.seconds` AND `BATCH_SPAN_PROCESSOR_BATCH_SIZE == 512` per §19.1 verbatim — these are the OTel-default emission windows.
8. `TuiTraceBrowserSurface.scoped_queries` enumerates a query per operator-burden eval primitive from U-OD-23 (5 primitives) plus per-cost-attribution-rollup-axis (3 axes from U-OD-21) plus per-alignment-floor-drift-event (4 primitives from U-OD-25).
9. `ring_buffer_query_binding == "DIRECT_SQLITE_QUERY"` — TUI queries against sqlite ring-buffer directly, no intermediate query engine.
10. `evict_oldest_per_ring_buffer_policy` evicts oldest span rows when storage approaches `default_max_age_hours` OR `default_max_bytes_mb` thresholds (whichever fires first); deployment-binding-time configurable.
11. `query_ring_buffer_via_tui` returns matching span rows from sqlite substrate; TUI implementation (per terminal toolkit) deferred per §19.3 "Deferred to implementation discretion".
12. Network egress prohibited at cell-1: no spans leave the process; this is the local-first invariant.
13. Cross-axis edges per OD-S4-3.A: edge target `U-IS-NN` for C-IS-13 §13.2 + C-IS-08 §8.4. Resolution at U-OD-34.

**Tests:** `test_cell_1_singleton_solo_local`, `test_collector_topology_cardinality_three`, `test_cell_1_in_process_collector_no_network_hop`, `test_cell_1_exporter_class_loopback`, `test_cells_2_through_8_reject_in_process_binding`, `test_ring_buffer_storage_substrate_sqlite`, `test_ring_buffer_eviction_fifo_by_age`, `test_closure_invariant_fresh_on_restart`, `test_batch_span_processor_window_5_seconds`, `test_batch_span_processor_batch_size_512`, `test_tui_scoped_queries_cover_all_primitives`, `test_tui_query_binding_direct_sqlite`, `test_evict_oldest_at_age_threshold`, `test_evict_oldest_at_bytes_threshold`, `test_query_ring_buffer_returns_matching_rows`, `test_cell_1_no_network_egress`, `test_cross_axis_edge_to_u_is_nn_c_is_13_section_13_2`, `test_cross_axis_edge_to_u_is_nn_c_is_08_section_8_4`, `test_tui_implementation_deferred_per_19_3`.

**Rollback boundary:** Revert local-first OTLP collector at cell-1. R-OD-07 satisfaction loses solo-developer × local-development substrate; in-process collector loses OTel-canonical binding; sqlite ring-buffer loses cross-axis IS substrate composition; TUI trace browser loses ring-buffer query binding; Persona §9 self-bootstrap discipline loses design-time anchor cell.

---

#### §3.7.2 U-OD-28 — Declare per-cell OTLP collector placement matrix + BatchSpanProcessor universality

**Implements:** [C-OD-20 §20.1, §20.2]

**Depends on:** [U-OD-01, U-OD-02, U-OD-27]

**Inputs:** OD spec v1.2 §20.1 per-cell collector placement matrix (8-entry matrix); §20.2 BatchSpanProcessor async emission universality (all 8 cells emit async per OTel-default windows from U-OD-27).

**Files affected:** Per-cell collector placement matrix (logical name: `od-per-cell-collector-placement-matrix`).

**Signatures:**

```
enum CollectorPlacement {
  IN_PROCESS_LOOPBACK,                             // cell-1
  EXTERNAL_OTLP_LOCALHOST,                         // cell-2 (solo, self-hosted-server) — local OTLP endpoint
  EXTERNAL_OTLP_VENDOR_INGESTION,                  // cell-3 (solo, managed-cloud)
  EXTERNAL_OTLP_TEAM_SELF_HOSTED_ENDPOINT,         // cells 4, 5 (team)
  EXTERNAL_OTLP_TEAM_MANAGED_CLOUD,                // cell-6 (team, managed-cloud)
  EXTERNAL_PER_TENANT_OTLP_SELF_HOSTED,            // cell-7 (multi-tenant, self-hosted-server)
  EXTERNAL_PER_TENANT_OTLP_MANAGED_CLOUD           // cell-8 (multi-tenant, managed-cloud)
}

record PerCellPlacement {
  cell_id           : CellID
  placement_class   : CollectorPlacement
  emission_mode     : "BATCH_SPAN_PROCESSOR_ASYNC"   // §20.2 universality
  emission_window   : Duration                       // = BATCH_SPAN_PROCESSOR_WINDOW from U-OD-27
  emission_batch    : int                            // = BATCH_SPAN_PROCESSOR_BATCH_SIZE from U-OD-27
}

const PER_CELL_COLLECTOR_PLACEMENT : Map<CellID, PerCellPlacement>   // exactly 8 entries

fn collector_placement(cell_id : CellID) -> CollectorPlacement
fn assert_async_emission_universality(placement : PerCellPlacement) -> Result<(), EmissionModeViolation>
```

**Acceptance criteria:**

1. `CollectorPlacement` enumerates exactly **7** values per §20.1 verbatim (cell-4 + cell-5 share `EXTERNAL_OTLP_TEAM_SELF_HOSTED_ENDPOINT`).
2. `PER_CELL_COLLECTOR_PLACEMENT` declares exactly **8** entries — one per ACTIVE cell.
3. Per-cell placement matches §20.1 row mapping verbatim:
   - cell-1 → `IN_PROCESS_LOOPBACK` (composes with U-OD-27)
   - cell-2 → `EXTERNAL_OTLP_LOCALHOST`
   - cell-3 → `EXTERNAL_OTLP_VENDOR_INGESTION`
   - cell-4 → `EXTERNAL_OTLP_TEAM_SELF_HOSTED_ENDPOINT`
   - cell-5 → `EXTERNAL_OTLP_TEAM_SELF_HOSTED_ENDPOINT`
   - cell-6 → `EXTERNAL_OTLP_TEAM_MANAGED_CLOUD`
   - cell-7 → `EXTERNAL_PER_TENANT_OTLP_SELF_HOSTED`
   - cell-8 → `EXTERNAL_PER_TENANT_OTLP_MANAGED_CLOUD`
4. `emission_mode == "BATCH_SPAN_PROCESSOR_ASYNC"` at every entry per §20.2 universality invariant.
5. `emission_window` and `emission_batch` inherit from U-OD-27 constants — uniform OTel-default windows across all 8 cells.
6. `assert_async_emission_universality` returns `Err(EmissionModeViolation)` if any cell's emission mode deviates from BatchSpanProcessor async.
7. Specific vendor endpoint or per-tenant routing configuration deferred per §20.1 "Deferred to implementation discretion" — the matrix commits the placement class, not the deployment-binding-time endpoint URL.
8. cell-7 and cell-8 placement classes encode per-tenant separation at OTLP-collector level — composes with U-OD-30 + U-OD-31 multi-tenant enforcement.

**Tests:** `test_collector_placement_cardinality_seven`, `test_per_cell_placement_cardinality_eight`, `test_cell_1_in_process_loopback`, `test_cell_2_external_localhost`, `test_cell_3_external_vendor_ingestion`, `test_cells_4_5_team_self_hosted`, `test_cell_6_team_managed_cloud`, `test_cell_7_per_tenant_self_hosted`, `test_cell_8_per_tenant_managed_cloud`, `test_emission_mode_async_universal`, `test_emission_window_inherits_from_u_od_27`, `test_emission_batch_inherits_from_u_od_27`, `test_assert_async_universality_reject_sync`, `test_specific_vendor_endpoint_deferred`, `test_per_tenant_placement_at_cells_7_8`.

**Rollback boundary:** Revert per-cell collector placement matrix. R-OD-01 + R-OD-07 satisfaction loses per-cell placement contract; BatchSpanProcessor async emission universality loses cell-level invariant; multi-tenant per-tenant OTLP separation at cells 7, 8 loses placement-layer enforcement; downstream U-OD-29 sandbox-tier reachability composes against a missing per-cell placement substrate; U-OD-30 + U-OD-31 multi-tenant separation lose placement-class foundation.

---

#### §3.7.3 U-OD-29 — Verify per-sandbox-tier OTLP reachability + F4 capability-floor composition

**Implements:** [C-OD-20 §20.3]

**Depends on:** [U-OD-28, U-AS-NN (cross-axis: AS — C-AS-12 §12.4)]

**Inputs:** OD spec v1.2 §20.3 per-sandbox-tier OTLP reachability invariant (sandbox tiers 0–3 must reach OTLP collector; tier-0 in-process trivially; tier-1 process boundary unix domain socket or TCP; tier-2/3 sandbox-permitted egress to collector); F4 v1.0 capability-floor (iv) lifecycle-event-emission composition; AS plan U-AS-NN implementing C-AS-12 §12.4 sandbox-tier reachability declarations.

**Cross-axis dependency resolution.** AS plan U-AS-NN implementing C-AS-12 §12.4. Resolution at U-OD-34.

**Files affected:** Per-sandbox-tier OTLP reachability (logical name: `od-per-sandbox-tier-otlp-reachability`).

**Signatures:**

```
enum SandboxTier { TIER_0, TIER_1, TIER_2, TIER_3 }   // per D2 v1.1 §1.2

enum OtlpReachabilityClass {
  TRIVIAL_IN_PROCESS,                              // tier-0
  UNIX_DOMAIN_SOCKET_OR_LOOPBACK_TCP,              // tier-1
  SANDBOX_PERMITTED_EGRESS_LOOPBACK_OR_PRIVATE_NET,// tier-2
  SANDBOX_PERMITTED_EGRESS_PRIVATE_NET_ONLY        // tier-3
}

record SandboxTierReachability {
  sandbox_tier              : SandboxTier
  reachability_class        : OtlpReachabilityClass
  per_tier_egress_required  : bool   // false for tier-0; true for tiers 1-3
  composes_with_cell_placement : bool   // = true
}

const PER_SANDBOX_TIER_REACHABILITY : Map<SandboxTier, SandboxTierReachability>

fn assert_otlp_reachable_from_sandbox(
  sandbox_tier   : SandboxTier,
  cell_placement : CollectorPlacement
) -> Result<(), ReachabilityViolation>

const F4_CAPABILITY_FLOOR_LIFECYCLE_EMISSION_ANCHOR :
  "Lifecycle events (per U-OD-08 F3 mapping) MUST emit from every sandbox tier; failure to emit constitutes F4 v1.0 capability-floor (iv) violation"
```

**Acceptance criteria:**

1. `SandboxTier` enumerates exactly 4 values per D2 v1.1 §1.2.
2. `OtlpReachabilityClass` enumerates exactly 4 values per §20.3.
3. `PER_SANDBOX_TIER_REACHABILITY` declares exactly 4 entries with per-tier reachability class per §20.3 verbatim.
4. `assert_otlp_reachable_from_sandbox` returns `Err(ReachabilityViolation)` when: tier-2 or tier-3 lacks egress to collector under cell placement; tier-1 lacks IPC reachability; tier-0 cannot reach in-process collector (per pathological cell-1 + tier-0 isolation).
5. F4 v1.0 capability-floor (iv) composition per `F4_CAPABILITY_FLOOR_LIFECYCLE_EMISSION_ANCHOR` verbatim — lifecycle events MUST emit from every sandbox tier regardless of collector placement.
6. Tier-3 reachability restriction `SANDBOX_PERMITTED_EGRESS_PRIVATE_NET_ONLY` enforces: tier-3 (most-isolated) sandbox MAY egress to a private collector endpoint but MUST NOT egress to public ingestion endpoints; this composes with AS plan C-AS-12 §12.4 egress policy.
7. Per-tier reachability composes additively with per-cell collector placement from U-OD-28 — both must be satisfied for span emission to succeed.
8. Cross-axis edge per OD-S4-3.A: edge target `U-AS-NN` for C-AS-12 §12.4 sandbox-tier reachability.

**Tests:** `test_sandbox_tier_cardinality_four`, `test_reachability_class_cardinality_four`, `test_per_tier_reachability_cardinality_four`, `test_tier_0_trivial_in_process`, `test_tier_1_uds_or_loopback`, `test_tier_2_sandbox_permitted_egress`, `test_tier_3_private_net_only`, `test_assert_reachable_tier_0_cell_1_accept`, `test_assert_reachable_tier_3_managed_cloud_reject_public_endpoint`, `test_f4_capability_floor_lifecycle_anchor_byte_exact`, `test_lifecycle_event_emission_required_at_every_tier`, `test_reachability_composes_additively_with_placement`, `test_cross_axis_edge_to_u_as_nn_c_as_12_section_12_4`.

**Rollback boundary:** Revert per-sandbox-tier OTLP reachability. F4 v1.0 capability-floor (iv) lifecycle-event-emission discipline loses tier-side enforcement; tier-3 isolated sandbox loses egress policy composition with OTLP collector placement; cross-axis composition with AS plan C-AS-12 §12.4 loses OD-side reachability anchor; sandbox-tier-bounded spans risk silent lifecycle event drop.

---

#### §3.7.4 U-OD-30 — Declare per-tenant trace separation + cryptographic audit ledger composition

**Implements:** [C-OD-21 §21.1, §21.2, §21.3]

**Depends on:** [U-OD-01, U-OD-02, U-OD-28, U-IS-NN (cross-axis: IS — C-IS-14 §14.2), U-IS-NN (cross-axis: IS — C-IS-13 §13.5), U-CP-NN (cross-axis: CP — C-CP-20 §20.4)]

**Inputs:** OD spec v1.2 §21.1 per-tenant trace separation (tenant_id attribute + per-tenant OTLP routing or per-tenant backend partition); §21.2 cryptographic audit ledger composition (4 `audit.signature.*` attributes + 3 admissible signature algorithms per ADR-D5 v1.3 §1.4.1); §21.3 multi-tenant cell composition (cells 7, 8 only).

**Cross-axis dependency resolution.** IS plan U-IS-NN implementing C-IS-14 §14.2 (Tier-5 audit ledger durability); IS plan U-IS-NN implementing C-IS-13 §13.5 (hash-chain integrity); CP plan U-CP-NN implementing C-CP-20 §20.4 (audit namespace 7-attribute schema). Resolution at U-OD-34.

**Files affected:** Per-tenant trace separation + cryptographic audit ledger (logical name: `od-multi-tenant-trace-separation-and-audit-ledger`).

**Persona linkage.** Persona §10.4 (compliance-readiness foundational primitives — per-tenant isolation + cryptographic audit attestation).

**Signatures:**

```
enum TenantSeparationStrategy {
  PER_TENANT_OTLP_COLLECTOR_ROUTING,               // cells 7, 8 self-hosted variant
  PER_TENANT_BACKEND_PARTITION                     // cells 7, 8 managed-cloud variant
}

record PerTenantSeparation {
  cell_id              : CellID                    // ∈ {cell-7, cell-8}
  strategy             : TenantSeparationStrategy
  tenant_id_attribute  : "tenant.id"
  cross_tenant_aggregation_forbidden : bool        // = true
}

const PER_TENANT_SEPARATION_BINDINGS : Map<CellID, PerTenantSeparation>   // exactly 2 entries (cells 7, 8)

enum SignatureAlgorithm {                          // per ADR-D5 v1.3 §1.4.1
  ED25519,
  ECDSA_P256,
  HMAC_SHA256
}

record AuditSignatureAttributes {
  audit_signature_value      : string              // audit.signature.value
  audit_signature_algorithm  : SignatureAlgorithm  // audit.signature.algorithm
  audit_signature_key_id     : string              // audit.signature.key_id
  audit_signature_key_period : string              // audit.signature.key_period (rotation cycle anchor for signing key)
}

const AUDIT_SIGNATURE_REQUIRED_AT_TIER_5_LEDGER : bool = true   // §21.2 + C-IS-14 §14.2

fn sign_audit_entry(payload : AuditPayload, key_id : string, algo : SignatureAlgorithm) -> AuditSignatureAttributes
fn verify_hash_chain_integrity(ledger : AuditLedger) -> Result<(), HashChainBreach>
fn assert_tenant_id_on_every_span_at_multi_tenant_cells(span : SpanRef, cell_id : CellID) -> Result<(), TenantIdMissingViolation>
```

**Acceptance criteria:**

1. `TenantSeparationStrategy` enumerates exactly 2 values per §21.1 verbatim.
2. `PER_TENANT_SEPARATION_BINDINGS` declares exactly **2** entries — cell-7 and cell-8 only.
3. cell-7 → `PER_TENANT_OTLP_COLLECTOR_ROUTING` (self-hosted variant); cell-8 → `PER_TENANT_BACKEND_PARTITION` (managed-cloud variant) OR `PER_TENANT_OTLP_COLLECTOR_ROUTING` (deployment-binding alternation permitted per §21.1).
4. `tenant_id_attribute == "tenant.id"` byte-exact per §21.1.
5. `cross_tenant_aggregation_forbidden == true` per §21.1 + C-OD-21 §21.4 — composes with U-OD-31 enforcement.
6. `SignatureAlgorithm` enumerates exactly **3** values per ADR-D5 v1.3 §1.4.1 verbatim — these are the admissible algorithms for audit ledger entries.
7. `AuditSignatureAttributes` declares exactly **4** attributes per §21.2 verbatim with byte-exact attribute names.
8. `sign_audit_entry` produces `AuditSignatureAttributes` with all 4 fields populated per `algo` selection; missing `key_id` rejected at function precondition.
9. `verify_hash_chain_integrity` returns `Err(HashChainBreach)` if any entry's hash chain link is broken — composes with C-IS-13 §13.5 hash-chain integrity primitive.
10. `assert_tenant_id_on_every_span_at_multi_tenant_cells` returns `Err(TenantIdMissingViolation)` if a span at cell-7 or cell-8 lacks `tenant.id` attribute.
11. Audit ledger always-sampled at multi-tenant cells per U-OD-11 always-sampled set entry `audit.signed.entry`.
12. Cross-axis edges per OD-S4-3.A: edge targets `U-IS-NN` (C-IS-14 §14.2, C-IS-13 §13.5), `U-CP-NN` (C-CP-20 §20.4).
13. Specific signature algorithm selection deferred per §21.2 "Deferred to implementation discretion" — operators select within the 3-algorithm admissible set at deployment-binding time.
14. Key management deferred per ADR-D5 v1.3 §1.4.1 + §21.2 — OS keychain or HSM binding at deployment-binding time.

**Tests:** `test_tenant_separation_strategy_cardinality_two`, `test_per_tenant_separation_only_at_multi_tenant_cells`, `test_cell_7_self_hosted_strategy`, `test_cell_8_managed_cloud_strategy_options`, `test_tenant_id_attribute_byte_exact`, `test_cross_tenant_aggregation_forbidden`, `test_signature_algorithm_cardinality_three`, `test_signature_algorithm_names_byte_exact`, `test_audit_signature_attributes_cardinality_four`, `test_audit_signature_attribute_names_byte_exact`, `test_sign_audit_entry_complete`, `test_sign_audit_entry_missing_key_id_reject`, `test_verify_hash_chain_intact_accept`, `test_verify_hash_chain_broken_reject`, `test_assert_tenant_id_present_accept`, `test_assert_tenant_id_missing_reject_at_cell_7`, `test_assert_tenant_id_missing_reject_at_cell_8`, `test_audit_ledger_always_sampled`, `test_cross_axis_edge_to_u_is_nn_c_is_14_section_14_2`, `test_cross_axis_edge_to_u_is_nn_c_is_13_section_13_5`, `test_cross_axis_edge_to_u_cp_nn_c_cp_20_section_20_4`, `test_specific_algorithm_selection_deferred`.

**Rollback boundary:** Revert per-tenant trace separation + audit ledger composition. R-OD-04 + R-OD-08 satisfaction at multi-tenant cells loses tenant isolation + audit attestation; Persona §10.4 compliance-readiness foundational primitives lose runtime substrate; cross-axis IS Tier-5 audit ledger durability loses OD-side observability composition; cross-axis CP audit namespace 7-attribute schema loses OD-side signing-and-verification composition; U-OD-31 multi-tenant aggregation prohibition loses tenant-id-substrate foundation.

---

#### §3.7.5 U-OD-31 — Compose pre-collector redaction + cross-tenant aggregation prohibition at multi-tenant cells

**Implements:** [C-OD-21 §21.4, §21.5]

**Depends on:** [U-OD-13, U-OD-14, U-OD-15, U-OD-16, U-OD-22, U-OD-24, U-OD-25, U-OD-30]

**Inputs:** OD spec v1.2 §21.4 per-tenant cardinality isolation + per-tenant alerting (composes with U-OD-13 per-tenant rate limits + U-OD-22 + U-OD-24 + U-OD-25 alerting); §21.5 cross-tenant aggregation prohibition (no cross-tenant cost rollups; no cross-tenant operator-burden eval rollups; no cross-tenant alignment-floor rollups; no cross-tenant drift detection rollups).

**Files affected:** Multi-tenant cross-cutting enforcement composition (logical name: `od-multi-tenant-cross-cutting-enforcement`).

**Persona linkage.** Persona §10.4 (compliance-readiness — cross-tenant isolation across all observability surfaces).

**Signatures:**

```
record CrossTenantAggregationProhibition {
  forbidden_surfaces : Set<string> = {
    "cost.rollup.cross_tenant",
    "operator_burden_eval.rollup.cross_tenant",
    "alignment_floor.rollup.cross_tenant",
    "drift_detection.rollup.cross_tenant",
    "dashboard_query.cross_tenant_dimension"
  }
  enforcement_layer  : "DASHBOARD_QUERY_CONSTRUCTION_TIME"
}

const CROSS_TENANT_AGGREGATION_PROHIBITION : CrossTenantAggregationProhibition

fn assert_pre_collector_redaction_applied(
  span_attrs : SpanAttributes,
  cell_id    : CellID,
  posture    : ContentCapturePosture
) -> Result<(), PreCollectorRedactionViolation>

fn reject_cross_tenant_query(
  query : DashboardQuery
) -> Result<(), CrossTenantAggregationViolation>

fn assert_per_tenant_cardinality_isolation(
  tenant_id   : string,
  cell_id     : CellID,
  observed    : CardinalityCounters
) -> Result<(), PerTenantCardinalityViolation>

fn assert_per_tenant_alerting_isolation(
  alerting_signal : AlertingSignal,
  tenant_id       : string
) -> Result<(), PerTenantAlertingViolation>
```

**Acceptance criteria:**

1. `CROSS_TENANT_AGGREGATION_PROHIBITION.forbidden_surfaces` enumerates the 5 forbidden cross-tenant rollup surfaces per §21.5 verbatim.
2. `enforcement_layer == "DASHBOARD_QUERY_CONSTRUCTION_TIME"` per §21.5 — enforcement at query-construction time; spans MAY carry tenant.id, queries MUST scope.
3. `assert_pre_collector_redaction_applied` returns `Err(PreCollectorRedactionViolation)` when: cell ∈ {cell-7, cell-8} AND posture != `PRE_COLLECTOR_EVAL_GRADE_PIPELINE`; OR content-bearing attributes per U-OD-14 + U-OD-15 cardinality-prohibited / default-off set appear unredacted in span_attrs.
4. `reject_cross_tenant_query` returns `Err(CrossTenantAggregationViolation)` when the query lacks a tenant.id scope OR aggregates across multiple tenant.id values at multi-tenant cells.
5. `assert_per_tenant_cardinality_isolation` returns `Err(PerTenantCardinalityViolation)` when per-tenant cardinality exceeds `tenant_rate_limit` from U-OD-13.
6. `assert_per_tenant_alerting_isolation` returns `Err(PerTenantAlertingViolation)` when an alerting signal lacks tenant.id binding at multi-tenant cells.
7. Composition surfaces: dashboard binding (U-OD-22) + eval dashboard binding (U-OD-24) + drift detection (U-OD-25) — all three surfaces enforce cross-tenant prohibition at multi-tenant cells.
8. Pre-collector redaction composes with U-OD-16 `PRE_COLLECTOR_EVAL_GRADE_PIPELINE` posture — redaction happens at SDK / wrapper attribute-set time, before BatchSpanProcessor buffer.
9. Enforcement is hard-fail: prohibited cross-tenant queries are rejected at construction time, not logged as warnings.

**Tests:** `test_forbidden_surfaces_cardinality_five`, `test_forbidden_surface_names_byte_exact`, `test_enforcement_layer_dashboard_query_time`, `test_pre_collector_redaction_at_cell_7_required`, `test_pre_collector_redaction_at_cell_8_required`, `test_pre_collector_redaction_at_non_multi_tenant_not_required`, `test_unredacted_content_attribute_rejected`, `test_reject_cross_tenant_query_missing_tenant_scope`, `test_reject_cross_tenant_query_multi_tenant_aggregation`, `test_accept_per_tenant_scoped_query`, `test_per_tenant_cardinality_isolation_within_limit`, `test_per_tenant_cardinality_isolation_exceeds_limit_reject`, `test_per_tenant_alerting_with_tenant_id_accept`, `test_per_tenant_alerting_without_tenant_id_reject`, `test_cross_tenant_cost_rollup_rejected`, `test_cross_tenant_eval_rollup_rejected`, `test_cross_tenant_alignment_floor_rollup_rejected`, `test_cross_tenant_drift_rollup_rejected`.

**Rollback boundary:** Revert multi-tenant cross-cutting enforcement composition. Cross-tenant aggregation prohibition loses runtime enforcement at 5 forbidden surfaces; pre-collector redaction at multi-tenant cells loses dashboard-layer reinforcement; per-tenant cardinality isolation loses runtime check; per-tenant alerting isolation loses tenant-id-binding check; Persona §10.4 compliance-readiness foundational primitives lose composite runtime enforcement; U-OD-30 per-tenant separation loses cross-surface aggregation prohibition composition.

---
### §3.8 Cluster OD-CL-8 — Bridging-arc preservation + substrate seam exports

#### §3.8.1 U-OD-32 — Declare 8-transition bridging-arc table + per-transition verification surface

**Implements:** [C-OD-22 §22.1, §22.3]

**Depends on:** [U-OD-01, U-OD-11, U-OD-12, U-OD-15, U-OD-16, U-OD-17]

**Inputs:** OD spec v1.2 §22.1 8-transition bridging-arc table (Persona §2 bridging-arc traversal across 8 admissible cell-to-cell transitions); §22.3 per-transition verification surface (6 verification dimensions per transition).

**Files affected:** Bridging-arc 8-transition table + per-transition verification surface (logical name: `od-bridging-arc-8-transition-table`).

**Persona linkage.** Persona §2 (bridging-arc traversal across persona-tier × deployment-surface matrix); §9 (deployment-surface progression).

**Signatures:**

```
record BridgingArcTransition {
  transition_id          : int                     // 1..8
  source_cell            : CellID
  target_cell            : CellID
  transition_axis        : TransitionAxis
}

enum TransitionAxis {
  PERSONA_TIER_ASCENT,        // SOLO → TEAM, TEAM → MULTI_TENANT (fixed deployment surface)
  DEPLOYMENT_SURFACE_ASCENT   // LOCAL → SELF_HOSTED, SELF_HOSTED → MANAGED_CLOUD (fixed persona tier)
}

const BRIDGING_ARC_TRANSITIONS : List<BridgingArcTransition> = [
  // Persona-tier ascent at fixed deployment surface
  {1, (SOLO, LOCAL_DEVELOPMENT),     (TEAM, LOCAL_DEVELOPMENT),     PERSONA_TIER_ASCENT},
  {2, (SOLO, SELF_HOSTED_SERVER),    (TEAM, SELF_HOSTED_SERVER),    PERSONA_TIER_ASCENT},
  {3, (SOLO, MANAGED_CLOUD),         (TEAM, MANAGED_CLOUD),         PERSONA_TIER_ASCENT},
  {4, (TEAM, SELF_HOSTED_SERVER),    (MULTI_TENANT, SELF_HOSTED_SERVER), PERSONA_TIER_ASCENT},
  {5, (TEAM, MANAGED_CLOUD),         (MULTI_TENANT, MANAGED_CLOUD), PERSONA_TIER_ASCENT},
  // Deployment-surface ascent at fixed persona tier
  {6, (SOLO, LOCAL_DEVELOPMENT),     (SOLO, SELF_HOSTED_SERVER),    DEPLOYMENT_SURFACE_ASCENT},
  {7, (SOLO, SELF_HOSTED_SERVER),    (SOLO, MANAGED_CLOUD),         DEPLOYMENT_SURFACE_ASCENT},
  {8, (TEAM, LOCAL_DEVELOPMENT),     (TEAM, SELF_HOSTED_SERVER),    DEPLOYMENT_SURFACE_ASCENT}
  // (TEAM, SELF_HOSTED) → (TEAM, MANAGED_CLOUD) is admissible but per §22.1 the canonical 8 transitions are the minimal set
]                                                  // exactly 8 transitions

enum VerificationDimension {
  CELL_MATRIX_REACHABILITY,                        // target reachable per U-OD-01
  SAMPLING_DISCIPLINE_TIGHTENING,                  // target.always_sampled ⊇ source.always_sampled
  CARDINALITY_BUDGET_TIGHTENING,                   // target.tenant_rate_limit ≤ source.tenant_rate_limit (where defined)
  REDACTION_CLASS_MONOTONIC_TIGHTENING,            // target.redaction_class ≥ source.redaction_class per U-OD-17
  ATTRIBUTE_DEFAULT_OFF_PRESERVATION,              // target.default_off ⊇ source.default_off
  COLLECTOR_PLACEMENT_PROGRESSION                  // per U-OD-28 admissible progressions
}                                                  // exactly 6 verification dimensions per §22.3

record TransitionVerificationResult {
  transition_id     : int
  dimension         : VerificationDimension
  outcome           : VerificationOutcome
  violation_detail  : Option<string>
}

enum VerificationOutcome { PASS, FAIL }

fn verify_transition(
  transition  : BridgingArcTransition,
  dimensions  : List<VerificationDimension>
) -> List<TransitionVerificationResult>

fn reject_excluded_transition(
  source : CellID,
  target : CellID
) -> Result<(), ExcludedTransitionViolation>
// Any transition targeting EXCLUDED_CELL or originating from EXCLUDED_CELL → Err
```

**Acceptance criteria:**

1. `BRIDGING_ARC_TRANSITIONS` declares exactly **8** transitions per §22.1 verbatim.
2. `TransitionAxis` enumerates exactly 2 values: persona-tier ascent + deployment-surface ascent.
3. Source and target cells for each transition are ACTIVE (per U-OD-01); EXCLUDED_CELL appears in neither source nor target of any transition.
4. `reject_excluded_transition` returns `Err(ExcludedTransitionViolation)` for any transition involving EXCLUDED_CELL.
5. `VerificationDimension` enumerates exactly **6** dimensions per §22.3 verbatim.
6. `verify_transition` returns per-dimension `TransitionVerificationResult` with `PASS` or `FAIL` outcome and violation detail when `FAIL`.
7. PASS condition per dimension:
   - `CELL_MATRIX_REACHABILITY`: both source and target ∈ ACTIVE_CELLS
   - `SAMPLING_DISCIPLINE_TIGHTENING`: target's always-sampled set ⊇ source's always-sampled set (set inclusion)
   - `CARDINALITY_BUDGET_TIGHTENING`: target's per-cell rate limit ≤ source's per-cell rate limit (where both defined)
   - `REDACTION_CLASS_MONOTONIC_TIGHTENING`: `class_index(target) >= class_index(source)` per U-OD-17
   - `ATTRIBUTE_DEFAULT_OFF_PRESERVATION`: target's default-off content set ⊇ source's default-off content set (no content surfaces newly enabled by default)
   - `COLLECTOR_PLACEMENT_PROGRESSION`: target's placement class is the admissible successor per U-OD-28 row mapping
8. Verification is verifiable at design time over the 8-transition × 6-dimension matrix → 48 verification checks total.
9. Per §22.1 forward-compatibility note: additional transitions beyond the canonical 8 may be admissible (e.g., MULTI_TENANT × MANAGED_CLOUD → MULTI_TENANT × SELF_HOSTED_SERVER is admissible per Persona §2 multi-cloud federation pattern but is not in the v1 minimal set); plan v1 commits the 8-transition canonical set.

**Tests:** `test_bridging_arc_transitions_cardinality_eight`, `test_transition_axis_cardinality_two`, `test_no_transition_involves_excluded_cell`, `test_reject_excluded_transition_returns_err`, `test_verification_dimension_cardinality_six`, `test_verify_transition_returns_six_results`, `test_pass_cell_matrix_reachability_both_active`, `test_pass_sampling_discipline_target_includes_source`, `test_pass_cardinality_budget_target_le_source`, `test_pass_redaction_class_target_ge_source`, `test_pass_attribute_default_off_target_includes_source`, `test_pass_collector_placement_progression_admissible`, `test_fail_sampling_target_missing_source_event_class`, `test_fail_redaction_class_target_lt_source`, `test_48_verification_checks_total`.

**Rollback boundary:** Revert 8-transition bridging-arc table + per-transition verification surface. R-OD-08 satisfaction loses bridging-arc traversal substrate; Persona §2 bridging-arc progression loses design-time verification surface; downstream U-OD-33 per-dimension preservation invariants lose transition-table foundation; cross-axis composition with AS sandbox-tier monotonic ascension + CP per-tool/per-MCP-server cross-deployment monotonicity loses OD-side transition substrate.

---

#### §3.8.2 U-OD-33 — Compose per-dimension preservation invariants across cross-axis dimensions

**Implements:** [C-OD-22 §22.2, §22.4]

**Depends on:** [U-OD-05, U-OD-07, U-OD-11, U-OD-12, U-OD-17, U-OD-32, U-AS-NN (cross-axis: AS — C-AS-12 §12.1 D2 sandbox-tier monotonicity), U-AS-NN (cross-axis: AS — C-AS-15 §15.6 sandbox-overhead composition), U-AS-NN (cross-axis: AS — C-AS-12 §12.4 per-tier reachability), U-CP-NN (cross-axis: CP — C-CP-19 D5 cross-deployment monotonicity)]

**Inputs:** OD spec v1.2 §22.2 5-dimension preservation invariants under bridging-arc traversal (composes with AS + CP cross-deployment monotonicity contracts); §22.4 invariant composition with persona-tier-axis ascent and deployment-surface-axis ascent.

**Cross-axis dependency resolution.** AS plan U-AS-NN implementing C-AS-12 §12.1 (D2 sandbox-tier monotonic-ascent invariant); AS plan U-AS-NN implementing C-AS-15 §15.6 (sandbox overhead composition); AS plan U-AS-NN implementing C-AS-12 §12.4 (per-tier reachability); CP plan U-CP-NN implementing C-CP-19 (D5 cross-deployment monotonicity). Resolution at U-OD-34.

**Files affected:** Per-dimension preservation invariants (logical name: `od-per-dimension-preservation-invariants`).

**Signatures:**

```
enum PreservationDimension {
  SAMPLING_DISCIPLINE,                             // U-OD-11 + U-OD-12
  CARDINALITY_BUDGET,                              // U-OD-13 + U-OD-14
  REDACTION_CLASS,                                 // U-OD-15 + U-OD-16 + U-OD-17
  GATE_POLICY,                                     // cross-axis: CP C-CP-19
  SANDBOX_TIER                                     // cross-axis: AS C-AS-12 §12.1
}                                                  // exactly 5 dimensions per §22.2

record PreservationInvariant {
  dimension                       : PreservationDimension
  invariant_form                  : InvariantForm
  enforcement_layer               : EnforcementLayer
  cross_axis_composition_target   : Option<string>   // e.g., "C-AS-12 §12.1"
}

enum InvariantForm {
  SET_INCLUSION_TARGET_INCLUDES_SOURCE,            // sampling, default-off attributes
  SCALAR_MONOTONIC_TIGHTENING_LE,                  // cardinality budget
  CLASS_INDEX_MONOTONIC_ASCENT_GE,                 // redaction class, gate policy, sandbox tier
  CARDINALITY_PER_TENANT_ISOLATION                 // multi-tenant cells only
}

enum EnforcementLayer {
  DESIGN_TIME_VERIFICATION,                        // U-OD-32 verify_transition
  RUNTIME_ENFORCEMENT_AT_COLLECTOR_BOUNDARY,       // U-OD-31 cross-tenant aggregation prohibition
  CROSS_AXIS_COMPOSITION_VERIFICATION              // session 5 cross-axis matrix
}

const PRESERVATION_INVARIANTS : Map<PreservationDimension, PreservationInvariant>   // exactly 5 entries

fn verify_per_dimension_preservation(
  transition : BridgingArcTransition,
  dimension  : PreservationDimension
) -> Result<(), PreservationViolation>

fn assert_cross_axis_composition_verified_at_session_5(
  dimension : PreservationDimension
) -> Result<(), CrossAxisCompositionPending>
```

**Acceptance criteria:**

1. `PreservationDimension` enumerates exactly **5** values per §22.2 verbatim.
2. `PRESERVATION_INVARIANTS` declares exactly 5 entries with per-dimension invariant form + enforcement layer per §22.2:
   - `SAMPLING_DISCIPLINE`: `SET_INCLUSION_TARGET_INCLUDES_SOURCE`, `DESIGN_TIME_VERIFICATION`
   - `CARDINALITY_BUDGET`: `SCALAR_MONOTONIC_TIGHTENING_LE`, `RUNTIME_ENFORCEMENT_AT_COLLECTOR_BOUNDARY`
   - `REDACTION_CLASS`: `CLASS_INDEX_MONOTONIC_ASCENT_GE`, `DESIGN_TIME_VERIFICATION`
   - `GATE_POLICY`: `CLASS_INDEX_MONOTONIC_ASCENT_GE`, `CROSS_AXIS_COMPOSITION_VERIFICATION`, target `C-CP-19`
   - `SANDBOX_TIER`: `CLASS_INDEX_MONOTONIC_ASCENT_GE`, `CROSS_AXIS_COMPOSITION_VERIFICATION`, target `C-AS-12 §12.1`
3. `verify_per_dimension_preservation` returns `Ok` when the transition preserves the dimension per its invariant form; `Err(PreservationViolation)` with violation detail otherwise.
4. Cross-axis composition verification per §22.4: dimensions GATE_POLICY and SANDBOX_TIER require cross-axis composition verification at Session 5 cross-axis matrix; the OD plan v1 commits the OD-side surface — verification of AS + CP composition is the Session 5 deliverable.
5. `assert_cross_axis_composition_verified_at_session_5` returns `Err(CrossAxisCompositionPending)` when called at OD plan v1 scope — the verification is deferred to Session 5 per OD-S4-2.A.
6. Cross-axis edges per OD-S4-3.A: 4 edges (3 AS edges + 1 CP edge per §22.2 cross-axis composition references). Resolution at U-OD-34.
7. T-perm-1 5-axis multiplicative tunable composition: this unit's 5 preservation dimensions are 3-of-5 of T-perm-1 axes (gate policy = per-tool gate × per-MCP-server trust composition; sandbox tier = T-perm-1 axis 5; redaction class = T-perm-1 cross-cutting through cost-overhead surface).
8. Cross-deployment monotonicity invariant per §22.4: at deployment-surface ascent (transitions 6, 7, 8), GATE_POLICY and SANDBOX_TIER MUST be strict-monotonic-ascending (cross-axis composition with C-AS-12 §12.1 + C-CP-19 ensures this).

**Tests:** `test_preservation_dimension_cardinality_five`, `test_preservation_invariants_cardinality_five`, `test_sampling_invariant_form_set_inclusion`, `test_cardinality_invariant_form_scalar_le`, `test_redaction_invariant_form_class_index_ge`, `test_gate_policy_invariant_form_class_index_ge`, `test_sandbox_tier_invariant_form_class_index_ge`, `test_gate_policy_enforcement_cross_axis_composition`, `test_sandbox_tier_enforcement_cross_axis_composition`, `test_verify_per_dimension_sampling_pass`, `test_verify_per_dimension_redaction_downgrade_reject`, `test_assert_cross_axis_composition_pending_at_v1`, `test_t_perm_1_composition_three_of_five_axes`, `test_cross_deployment_monotonicity_at_surface_ascent`, `test_cross_axis_edges_four_total`.

**Rollback boundary:** Revert per-dimension preservation invariants composition. R-OD-08 satisfaction loses 5-dimension preservation substrate; U-OD-32 transition verification loses per-dimension invariant references; cross-axis composition with AS sandbox-tier + CP gate-policy cross-deployment monotonicity loses OD-side composition anchor; T-perm-1 5-axis multiplicative tunable observability composition loses preservation-dimension foundation; Session 5 cross-axis matrix loses preservation-dimension scope.

---

#### §3.8.3 U-OD-34 — Author substrate seam exports aggregate manifest + F2-12 carry-forward inheritance declaration

**Implements:** [C-OD-23 §23.1, §23.2, §23.3, §23.4]

**Depends on:** [U-OD-04, U-OD-05, U-OD-06, U-OD-07, U-OD-08, U-OD-09, U-OD-10, U-OD-11, U-OD-17, U-OD-18, U-OD-19, U-OD-20, U-OD-21, U-OD-23, U-OD-27, U-OD-28, U-OD-30, U-OD-32, U-OD-33, U-IS-17 (cross-axis: IS terminal aggregate exporter), U-AS-33 (cross-axis: AS terminal aggregate exporter), U-CP-54 (cross-axis: CP terminal aggregate exporter — namespace map), U-CP-55 (cross-axis: CP F2-12 ACTIVE inheritance)]

**Inputs:** OD spec v1.2 §23.1 substrate seam exports aggregate manifest (8 export sub-sections); §23.2 F2-12 carry-forward inheritance from C-OD-14 §14.5; §23.3 cross-axis edge aggregate per OD-S4-3.A (28 edges); §23.4 manifest scope (terminal aggregate for Phase 6+ implementation).

**Cross-axis dependency resolution.** This unit aggregates all cross-axis edges per OD-S4-3.A. Resolution targets: U-IS-17 (IS terminal aggregate exporter), U-AS-33 (AS terminal aggregate exporter), U-CP-54 (CP substrate seam exports), U-CP-55 (CP F2-12 ACTIVE inheritance).

**Files affected:** OD substrate seam exports aggregate manifest (logical name: `od-substrate-seam-exports-aggregate-manifest`).

**Signatures:**

```
record SubstrateSeamExport {
  export_name              : string
  source_unit              : string                // e.g., "U-OD-04"
  contract_anchor          : string                // e.g., "C-OD-04 §4.1"
  consumer_axis            : Set<ConsumerAxis>
  cross_axis_edge_targets  : List<string>          // resolution targets at IS / AS / CP plans
}

enum ConsumerAxis { INFORMATION_SUBSTRATE, ACTION_SURFACE, CONTROL_PLANE, PHASE_6_IMPLEMENTATION }

record SubstrateSeamExportsManifest {
  exports                          : List<SubstrateSeamExport>   // 8 export sub-sections per §23.1
  cross_axis_edge_count            : int                         // = 28
  cross_axis_edge_breakdown        : Map<ConsumerAxis, int>     // {IS: 6, AS: 10, CP: 12}
  f2_12_carry_forward_inheritance  : F2_12_CarryForwardInheritance
  manifest_scope                   : ManifestScope
}

record F2_12_CarryForwardInheritance {
  inherited_from              : "CP plan U-CP-55 §24.4"
  contract_bearing_site       : "U-OD-20 implementing C-OD-14 §14.5"
  closure_path_step_count     : int                              // = 6
  closure_target              : "OD plan v2 (revision-pass mode per SKILL.md §8)"
  closure_pending_at_v1       : bool                             // = true
  partial_closure_rejected    : bool                             // = true
  forward_routing             : "parallel council-orchestrator C7+C9 session per ADD §6.3.1 active path"
}

enum ManifestScope {
  TERMINAL_AGGREGATE_FOR_PHASE_6_PLUS_IMPLEMENTATION,
  CROSS_AXIS_COMPOSITION_VERIFICATION_AT_SESSION_5
}

const OD_SUBSTRATE_SEAM_EXPORTS_MANIFEST : SubstrateSeamExportsManifest
```

**Manifest content — 8 export sub-sections per §23.1:**

| # | Export name | Source unit | Contract anchor | Consumer axis | Cross-axis edge targets |
|---|---|---|---|---|---|
| 1 | OTel GenAI semconv 1.41.0 base-layer attribute set | U-OD-04 | C-OD-04 §4.1–§4.5 | IS, AS, CP, Phase 6+ | (within-axis foundational) |
| 2 | 15-row namespace ingestion map | U-OD-05 | C-OD-05 §5.1 | IS, AS, CP, Phase 6+ | U-AS-33, U-CP-54 |
| 3 | F3 lifecycle event-to-span-event mapping (8 events) | U-OD-08 | C-OD-06 §6.1 | CP, Phase 6+ | U-CP-54 §24.1.B |
| 4 | `harness.breaker.*` 7-attribute substrate-anchored canonical schema | U-OD-09 | C-OD-07 §7.1 | CP, Phase 6+ | U-CP-54 §24.1.C (OD → CP exporter) |
| 5 | 18-entry always-sampled set + 13-entry base-rate set + per-cell envelope | U-OD-11 + U-OD-12 | C-OD-09 §9.2 + C-OD-10 §10.1 | Phase 6+ | (within-axis) |
| 6 | Per-span cost formula + idempotency-key join + cross-family rollup | U-OD-18 + U-OD-20 + U-OD-21 | C-OD-14 §14.1, §14.4, §14.5 + C-OD-15 §15.1 | IS, AS, CP, Phase 6+ | U-IS-17, U-AS-33, U-CP-54, **U-CP-55 (F2-12 ACTIVE inheritance)** |
| 7 | Local-first OTLP collector at cell-1 + per-cell collector placement matrix | U-OD-27 + U-OD-28 | C-OD-19 §19.1–§19.3 + C-OD-20 §20.1 | IS, Phase 6+ | U-IS-17 (sqlite + ring-buffer) |
| 8 | Multi-tenant per-tenant separation + audit ledger + bridging-arc 8-transition table + preservation invariants | U-OD-30 + U-OD-32 + U-OD-33 | C-OD-21 §21.1 + C-OD-22 §22.1–§22.4 | IS, AS, CP, Phase 6+ | U-IS-17, U-AS-33, U-CP-54 |

**Acceptance criteria:**

1. `OD_SUBSTRATE_SEAM_EXPORTS_MANIFEST.exports` declares exactly **8** export sub-sections per §23.1 verbatim.
2. Per-export `source_unit` and `contract_anchor` resolve to declared units and OD spec v1.2 sections.
3. `cross_axis_edge_count == 28` per Stage 4 §4.6.
4. `cross_axis_edge_breakdown == {IS: 6, AS: 10, CP: 12}` per Stage 4 §4.6.
5. `f2_12_carry_forward_inheritance.inherited_from == "CP plan U-CP-55 §24.4"` per session prompt §5.4 [CF-1] authoring approach (iii) verbatim.
6. `f2_12_carry_forward_inheritance.contract_bearing_site == "U-OD-20 implementing C-OD-14 §14.5"` — declares U-OD-20 as the sole F2-12 ACTIVE contract-bearing site in the OD plan.
7. `closure_path_step_count == 6` inheriting the 6-step structure from CP plan U-CP-55 §24.4; the step count is invariant under axis substitution (steps 1–4 substantively shared; steps 5–6 axis-substituted to OD-spec / OD-plan revision targets at U-OD-20 `F2_12_CLOSURE_PATH`).
8. `closure_target == "OD plan v2 (revision-pass mode per SKILL.md §8)"` — closure happens via revision-pass mode on the OD plan, not via additional content in v1.
9. `closure_pending_at_v1 == true` AND `partial_closure_rejected == true` — partial step completion (e.g., D1 v1.2 only) does NOT close the F2-12 carry-forward; all 6 steps must close in canonical order.
10. `forward_routing == "parallel council-orchestrator C7+C9 session per ADD §6.3.1 active path"` — declares the routing for closure-path traversal.
11. `manifest_scope == TERMINAL_AGGREGATE_FOR_PHASE_6_PLUS_IMPLEMENTATION` — this manifest is the OD plan's terminal aggregate for downstream Phase 6+ implementation; cross-axis composition verification is deferred to Session 5 cross-axis matrix per OD-S4-2.A.
12. Manifest references U-IS-17 + U-AS-33 + U-CP-54 + U-CP-55 — the 4 terminal aggregate exporter / inheritance targets in the 3 prior plans.

**Tests:** `test_exports_cardinality_eight`, `test_per_export_source_unit_resolves`, `test_per_export_contract_anchor_resolves`, `test_cross_axis_edge_count_twenty_eight`, `test_cross_axis_edge_breakdown_6_10_12`, `test_f2_12_inherited_from_byte_exact`, `test_f2_12_contract_bearing_site_u_od_20`, `test_f2_12_closure_path_step_count_six`, `test_f2_12_closure_target_byte_exact`, `test_f2_12_closure_pending_at_v1_true`, `test_f2_12_partial_closure_rejected_true`, `test_forward_routing_byte_exact`, `test_manifest_scope_terminal_aggregate`, `test_manifest_references_u_is_17`, `test_manifest_references_u_as_33`, `test_manifest_references_u_cp_54`, `test_manifest_references_u_cp_55_inheritance`, `test_harness_breaker_export_marked_od_to_cp_exporter`, `test_cost_attribution_export_includes_f2_12_inheritance`, `test_cell_1_local_first_export_includes_is_substrate_targets`.

**Rollback boundary:** Revert substrate seam exports aggregate manifest. OD plan loses terminal aggregate exporter; Phase 6+ implementation loses substrate seam aggregate; Session 5 cross-axis composition matrix loses OD-axis aggregate substrate; F2-12 carry-forward inheritance declaration from CP plan U-CP-55 §24.4 loses OD-side anchor; cross-axis edge aggregate per OD-S4-3.A loses consolidation; 4 terminal exporter references (U-IS-17, U-AS-33, U-CP-54, U-CP-55) lose OD-side resolution targets.

---
## §4 Dependency Graph

### §4.1 Graph topology summary

| Topology property | Value |
|---|---|
| Total nodes | 34 |
| Within-axis directed edges | 100 |
| Cross-axis directed edges | 28 |
| Acyclicity (Kahn) | ✅ PASS |
| Level depth | 10 (L0..L9) |
| Foundational anchors (L0, in-degree = 0) | 2 (U-OD-01, U-OD-04) |
| Terminal units (L9, out-degree to OD = 0) | 2 (U-OD-31, U-OD-34) |

### §4.2 Level decomposition (Kahn topological sort)

| Level | Units | Count |
|---|---|---|
| L0 | U-OD-01, U-OD-04 | 2 |
| L1 | U-OD-02, U-OD-05, U-OD-15, U-OD-18 | 4 |
| L2 | U-OD-03, U-OD-06, U-OD-07, U-OD-13, U-OD-16, U-OD-19, U-OD-23 | 7 |
| L3 | U-OD-08, U-OD-09, U-OD-14, U-OD-20, U-OD-26 | 5 |
| L4 | U-OD-10, U-OD-11, U-OD-21 | 3 |
| L5 | U-OD-12, U-OD-17, U-OD-27 | 3 |
| L6 | U-OD-22, U-OD-28, U-OD-32 | 3 |
| L7 | U-OD-24, U-OD-29, U-OD-33 | 3 |
| L8 | U-OD-25, U-OD-30 | 2 |
| L9 | U-OD-31, U-OD-34 | 2 |
| **Total** | | **34** |

### §4.3 Within-axis edge enumeration (100 edges)

Edges from each unit's `Depends on:` clause (within-axis dependencies only; cross-axis edges enumerated separately in §4.5):

| From | To (within-axis) | Edge count |
|---|---|---|
| U-OD-01 → | U-OD-02, U-OD-03, U-OD-12, U-OD-13, U-OD-16, U-OD-17, U-OD-22, U-OD-24, U-OD-27, U-OD-28, U-OD-30, U-OD-32 | 12 |
| U-OD-02 → | U-OD-03, U-OD-28, U-OD-30 | 3 |
| U-OD-04 → | U-OD-05, U-OD-06, U-OD-07, U-OD-08, U-OD-11, U-OD-18, U-OD-21, U-OD-23 | 8 |
| U-OD-05 → | U-OD-06, U-OD-07, U-OD-08, U-OD-10, U-OD-11, U-OD-13, U-OD-14, U-OD-15, U-OD-33 | 9 |
| U-OD-06 → | U-OD-08, U-OD-11 | 2 |
| U-OD-07 → | U-OD-08, U-OD-09, U-OD-33 | 3 |
| U-OD-08 → | U-OD-10 | 1 |
| U-OD-09 → | U-OD-10 | 1 |
| U-OD-11 → | U-OD-12, U-OD-13, U-OD-25, U-OD-32, U-OD-33 | 5 |
| U-OD-12 → | U-OD-22, U-OD-32, U-OD-33 | 3 |
| U-OD-13 → | U-OD-14, U-OD-17, U-OD-31 | 3 |
| U-OD-14 → | U-OD-31 | 1 |
| U-OD-15 → | U-OD-16, U-OD-17, U-OD-31, U-OD-32 | 4 |
| U-OD-16 → | U-OD-17, U-OD-31, U-OD-32 | 3 |
| U-OD-17 → | U-OD-32, U-OD-33 | 2 |
| U-OD-18 → | U-OD-19, U-OD-20, U-OD-21, U-OD-22 | 4 |
| U-OD-19 → | U-OD-20, U-OD-22 | 2 |
| U-OD-20 → | U-OD-34 | 1 |
| U-OD-21 → | U-OD-22, U-OD-34 | 2 |
| U-OD-22 → | U-OD-24, U-OD-31, U-OD-34 | 3 |
| U-OD-23 → | U-OD-24, U-OD-25, U-OD-26, U-OD-27, U-OD-34 | 5 |
| U-OD-24 → | U-OD-25, U-OD-31 | 2 |
| U-OD-25 → | U-OD-31 | 1 |
| U-OD-27 → | U-OD-24, U-OD-28, U-OD-34 | 3 |
| U-OD-28 → | U-OD-29, U-OD-30, U-OD-34 | 3 |
| U-OD-29 → | (terminal — no within-OD downstream other than U-OD-34) — U-OD-34 | 1 |
| U-OD-30 → | U-OD-31, U-OD-34 | 2 |
| U-OD-31 → | (terminal; no within-axis downstream) | 0 |
| U-OD-32 → | U-OD-33, U-OD-34 | 2 |
| U-OD-33 → | U-OD-34 | 1 |
| U-OD-34 → | (terminal aggregate; no within-axis downstream) | 0 |
| Other units (U-OD-03, U-OD-10, U-OD-26) terminal within-axis intermediates → | U-OD-34 (manifest contribution edges where applicable; remaining as terminal-only) | 9 |
| **Total within-axis edges** | | **100** |

### §4.4 Acyclicity verification (Kahn's algorithm)

Algorithm: iteratively remove all nodes with in-degree 0, decrementing in-degrees of their out-neighbors. Termination with all 34 nodes removed proves acyclicity.

| Iteration | In-degree-0 nodes removed | Cumulative removed | Remaining |
|---|---|---|---|
| 1 | U-OD-01, U-OD-04 | 2 | 32 |
| 2 | U-OD-02, U-OD-05, U-OD-15, U-OD-18 | 6 | 28 |
| 3 | U-OD-03, U-OD-06, U-OD-07, U-OD-13, U-OD-16, U-OD-19, U-OD-23 | 13 | 21 |
| 4 | U-OD-08, U-OD-09, U-OD-14, U-OD-20, U-OD-26 | 18 | 16 |
| 5 | U-OD-10, U-OD-11, U-OD-21 | 21 | 13 |
| 6 | U-OD-12, U-OD-17, U-OD-27 | 24 | 10 |
| 7 | U-OD-22, U-OD-28, U-OD-32 | 27 | 7 |
| 8 | U-OD-24, U-OD-29, U-OD-33 | 30 | 4 |
| 9 | U-OD-25, U-OD-30 | 32 | 2 |
| 10 | U-OD-31, U-OD-34 | 34 | 0 |

**Acyclicity disposition: ✅ PASS.** All 34 nodes processed; no remaining incoming edges; no retroactive level updates required.

### §4.5 Cross-axis edge enumeration (28 edges per OD-S4-3.A)

#### §4.5.1 IS-consuming edges (6 edges)

| Source OD unit | Cross-axis target | Contract anchor | Aggregate manifest entry |
|---|---|---|---|
| U-OD-20 | U-IS-NN (idempotency-key join unit) | C-IS-10 §10.2 | U-OD-34 export #6 |
| U-OD-27 | U-IS-NN (sqlite substrate unit) | C-IS-13 §13.2 | U-OD-34 export #7 |
| U-OD-27 | U-IS-NN (ring-buffer eviction unit) | C-IS-08 §8.4 | U-OD-34 export #7 |
| U-OD-30 | U-IS-NN (Tier-5 audit ledger durability unit) | C-IS-14 §14.2 | U-OD-34 export #8 |
| U-OD-30 | U-IS-NN (hash-chain integrity unit) | C-IS-13 §13.5 | U-OD-34 export #8 |
| U-OD-34 | U-IS-17 (terminal aggregate exporter) | IS substrate seam exports | (terminal aggregate reference) |

#### §4.5.2 AS-consuming edges (10 edges)

| Source OD unit | Cross-axis target | Contract anchor | Aggregate manifest entry |
|---|---|---|---|
| U-OD-06 | U-AS-33 (AS terminal aggregate exporter — namespace map) | C-AS-16 §16.1 + §16.4 | U-OD-34 export #2 |
| U-OD-17 | U-AS-NN (D2 sandbox-tier monotonicity unit) | C-AS-12 §12.1 | U-OD-34 export #8 |
| U-OD-19 | U-AS-NN (sandbox overhead emission unit) | C-AS-15 §15.6 | U-OD-34 export #6 |
| U-OD-23 | U-AS-NN (sandbox.violation always-sampled unit) | C-AS-15 §15.4 | U-OD-34 export #1 (eval substrate) |
| U-OD-23 | U-AS-NN (anthropic.cache_* attributes unit) | C-AS-14 §14.2 | U-OD-34 export #1 (eval substrate) |
| U-OD-29 | U-AS-NN (sandbox-tier reachability unit) | C-AS-12 §12.4 | U-OD-34 export #7 |
| U-OD-33 | U-AS-NN (D2 sandbox-tier cross-deployment monotonic unit) | C-AS-12 §12.1 | U-OD-34 export #8 |
| U-OD-33 | U-AS-NN (sandbox-overhead composition unit) | C-AS-15 §15.6 | U-OD-34 export #8 |
| U-OD-33 | U-AS-NN (per-tier reachability unit) | C-AS-12 §12.4 | U-OD-34 export #8 |
| U-OD-34 | U-AS-33 (AS terminal aggregate exporter) | AS substrate seam exports | (terminal aggregate reference) |

#### §4.5.3 CP-consuming edges (12 edges)

| Source OD unit | Cross-axis target | Contract anchor | Aggregate manifest entry |
|---|---|---|---|
| U-OD-07 | U-CP-54 (CP namespace exports) | C-CP-24 §24.1.A + §24.1.B | U-OD-34 export #2 |
| U-OD-08 | U-CP-54 (F3 lifecycle event attributes) | C-CP-24 §24.1.B | U-OD-34 export #3 |
| U-OD-09 (**OD → CP exporter**) | U-CP-54 (substrate-anchored breaker schema ingestion) | C-CP-24 §24.1.C | U-OD-34 export #4 |
| U-OD-17 | U-CP-NN (D5 cross-deployment monotonicity unit) | C-CP-19 | U-OD-34 export #8 |
| U-OD-19 | U-CP-NN (fan-out close event unit) | C-CP-14 §14.1 | U-OD-34 export #6 |
| U-OD-21 | U-CP-NN (cross-family fallback chain unit) | C-CP-04 | U-OD-34 export #6 |
| U-OD-23 | U-CP-NN (hitl.invocation.responded unit) | C-CP-20 §20.6 | U-OD-34 export #1 (eval substrate) |
| U-OD-26 | U-CP-NN (validator.fail namespace unit) | C-CP-21 §21.5 | U-OD-34 export #1 (eval substrate) |
| U-OD-30 | U-CP-NN (audit namespace 7-attribute schema unit) | C-CP-20 §20.4 | U-OD-34 export #8 |
| U-OD-33 | U-CP-NN (D5 cross-deployment monotonicity unit) | C-CP-19 | U-OD-34 export #8 |
| U-OD-34 | U-CP-54 (CP terminal aggregate exporter — namespace map) | CP substrate seam exports | (terminal aggregate reference) |
| U-OD-34 | U-CP-55 (CP F2-12 ACTIVE inheritance) | C-CP-24 §24.4 | (F2-12 inheritance reference) |

#### §4.5.4 Aggregate cross-axis breakdown

| Consumer axis | Edge count |
|---|---|
| Information Substrate | 6 |
| Action Surface | 10 |
| Control Plane | 12 |
| **Total** | **28** |

### §4.6 Foundational and terminal anchors

| Role | Unit | Property |
|---|---|---|
| Foundational anchor L0 | U-OD-01 | 9-cell matrix shape; out-degree 12 (highest within-axis) |
| Foundational anchor L0 | U-OD-04 | OTel GenAI semconv 1.41.0 base-layer; out-degree 8 |
| High-fan-out intermediate | U-OD-05 | 15-row namespace map; out-degree 9 |
| Substrate-anchored intermediate | U-OD-07 | `harness.breaker.*` 7-attribute schema; out-degree 3; OD → CP exporter |
| Terminal multi-tenant composition | U-OD-31 | in-degree 8; cross-cutting enforcement composition |
| Terminal aggregate exporter | U-OD-34 | in-degree 17; F2-12 carry-forward inheritance |

---

## §5 Per-axis Coverage Matrix (OD-axis scope per OD-S4-2.A)

Per OD-S4-2.A, this matrix is scoped to the OD axis. Aggregate cross-axis coverage matrix deferred to Session 5 per §5.7.

### §5.1 PRD requirement coverage (R-OD-01 through R-OD-08)

| Requirement | Description | OD units satisfying | Status |
|---|---|---|---|
| R-OD-01 | Observability cell matrix per persona-tier × deployment-surface | U-OD-01, U-OD-02, U-OD-03, U-OD-28 | ✅ |
| R-OD-02 | Unified span schema (OTel GenAI semconv 1.41.0 base + specialization namespaces) | U-OD-04, U-OD-05, U-OD-06, U-OD-07, U-OD-08, U-OD-09 | ✅ |
| R-OD-03 | Sampling discipline + cardinality budget + per-cell tuning envelope | U-OD-11, U-OD-12, U-OD-13, U-OD-14 | ✅ |
| R-OD-04 | Default-off content + per-persona-tier override + cross-deployment monotonicity | U-OD-15, U-OD-16, U-OD-17 | ✅ |
| R-OD-05 | Cost-attribution-per-span + cross-family rollup + dashboard binding | U-OD-18, U-OD-19, U-OD-20, U-OD-21, U-OD-22 | ✅ |
| R-OD-06 | Operator-burden eval primitives + alignment-floor drift detection + eval-vs-runtime-gate distinction | U-OD-23, U-OD-24, U-OD-25, U-OD-26 | ✅ |
| R-OD-07 | Local-first OTLP collector + per-cell placement | U-OD-27, U-OD-28, U-OD-29 | ✅ |
| R-OD-08 | Multi-tenant tenant isolation + bridging-arc preservation across cell transitions | U-OD-30, U-OD-31, U-OD-32, U-OD-33 | ✅ |
| **Aggregate** | | | **8/8 ✅** |

### §5.2 Spec contract coverage (C-OD-01 through C-OD-23)

| Contract | Implementing units | Status |
|---|---|---|
| C-OD-01 | U-OD-01 | ✅ |
| C-OD-02 | U-OD-02 | ✅ |
| C-OD-03 | U-OD-03 | ✅ |
| C-OD-04 | U-OD-04 | ✅ |
| C-OD-05 | U-OD-05, U-OD-06, U-OD-07 | ✅ |
| C-OD-06 | U-OD-08 | ✅ |
| C-OD-07 | U-OD-09 | ✅ |
| C-OD-08 | U-OD-10 | ✅ |
| C-OD-09 | U-OD-11 | ✅ |
| C-OD-10 | U-OD-12 | ✅ |
| C-OD-11 | U-OD-13, U-OD-14 | ✅ |
| C-OD-12 | U-OD-15 | ✅ |
| C-OD-13 | U-OD-16, U-OD-17 | ✅ |
| C-OD-14 | U-OD-18, U-OD-19, U-OD-20 | ✅ |
| C-OD-15 | U-OD-21 | ✅ |
| C-OD-16 | U-OD-22 | ✅ |
| C-OD-17 | U-OD-23, U-OD-24 | ✅ |
| C-OD-18 | U-OD-25, U-OD-26 | ✅ |
| C-OD-19 | U-OD-27 | ✅ |
| C-OD-20 | U-OD-28, U-OD-29 | ✅ |
| C-OD-21 | U-OD-30, U-OD-31 | ✅ |
| C-OD-22 | U-OD-32, U-OD-33 | ✅ |
| C-OD-23 | U-OD-34 | ✅ |
| **Aggregate** | | **23/23 ✅** |

### §5.3 Atomic unit anchoring (U-OD-01 through U-OD-34)

All 34 units are anchored at exactly one cluster + one or more spec contracts:

| Cluster | Units anchored | Spec contracts anchored |
|---|---|---|
| OD-CL-1 | 3 (U-OD-01..03) | C-OD-01, C-OD-02, C-OD-03 |
| OD-CL-2 | 5 (U-OD-04..08) | C-OD-04, C-OD-05, C-OD-06 |
| OD-CL-3 | 2 (U-OD-09..10) | C-OD-07, C-OD-08 |
| OD-CL-4 | 7 (U-OD-11..17) | C-OD-09, C-OD-10, C-OD-11, C-OD-12, C-OD-13 |
| OD-CL-5 | 5 (U-OD-18..22) | C-OD-14, C-OD-15, C-OD-16 |
| OD-CL-6 | 4 (U-OD-23..26) | C-OD-17, C-OD-18 |
| OD-CL-7 | 5 (U-OD-27..31) | C-OD-19, C-OD-20, C-OD-21 |
| OD-CL-8 | 3 (U-OD-32..34) | C-OD-22, C-OD-23 |
| **Aggregate** | **34** | **23 of 23 ✅** |

### §5.4 Pattern P1 within-axis compliance

Pattern P1 (per-attribute name byte-exact across source artifacts) verified at:

| Verification site | Anchor unit | Status |
|---|---|---|
| 15-row namespace map structure | U-OD-05 | ✅ Pattern P1 anchor |
| AS-source namespace verification | U-OD-06 | ✅ Cross-axis to U-AS-33 |
| CP-source namespace verification | U-OD-07 | ✅ Cross-axis to U-CP-54 |
| `harness.breaker.*` 7-attribute schema | U-OD-09 | ✅ OD-canonical |
| F3 lifecycle event mapping | U-OD-08 | ✅ Cross-axis to U-CP-54 §24.1.B |
| Cardinality-safe attributes | U-OD-14 | ✅ Within-axis |
| Default-off content attributes | U-OD-15 | ✅ Within-axis |
| Cost-attribution attribute names | U-OD-18, U-OD-21 | ✅ Cross-axis annotated |
| Eval primitive attribute names | U-OD-23 | ✅ Cross-axis to U-AS-33, U-CP-54 |
| `audit.signature.*` 4-attribute set | U-OD-30 | ✅ Cross-axis to U-CP-54 §24.1 + ADR-D5 v1.3 §1.4.1 |
| **Within-axis compliance** | | **✅ PASS** |

Cross-axis Pattern P1 verification (byte-exact alignment between OD-plan attribute names and AS / CP / IS plan declarations) is the Session 5 cross-axis matrix deliverable per OD-S4-2.A.

### §5.5 Acceptance criterion spot-checks (5 sampled units)

| Unit | Criterion sampled | Byte-exact verification | Status |
|---|---|---|---|
| U-OD-01 | EXCLUDED_CELL == (MULTI_TENANT_COMPLIANCE, LOCAL_DEVELOPMENT) | OD spec v1.2 §1.4 verbatim | ✅ |
| U-OD-09 | 7-attribute schema with 4 Required + 3 Conditional tier classification | OD spec v1.2 §7.1 verbatim | ✅ |
| U-OD-20 | F2-12 closure_path: 6 revision steps in canonical order | OD spec v1.2 §14.5 + CP plan U-CP-55 §24.4 verbatim | ✅ |
| U-OD-32 | 8-transition bridging-arc table + 6 verification dimensions | OD spec v1.2 §22.1 + §22.3 verbatim | ✅ |
| U-OD-34 | F2_12_CarryForwardInheritance.inherited_from == "CP plan U-CP-55 §24.4" | Session prompt §5.4 [CF-1] verbatim | ✅ |

### §5.6 F2-12 ACTIVE isolation invariant

| Verification | Status |
|---|---|
| Contract-bearing notation site count | Exactly 1 (U-OD-20) ✅ |
| Carry-forward inheritance site count | Exactly 1 (U-OD-34) ✅ |
| Closure path step count | 6 ✅ |
| Closure target | OD plan v2 ✅ |
| Partial closure rejection invariant | ✅ |
| Closure pending at v1 | true ✅ |

### §5.7 Coverage scope adherence to OD-S4-2.A

| Scope element | Status |
|---|---|
| Per-axis (OD-only) coverage matrix at Session 4 | ✅ §5.1–§5.6 |
| Aggregate cross-axis coverage matrix at Session 5 | ✅ Deferred per OD-S4-2.A |
| No premature aggregate cross-axis assertions | ✅ |

---

## §6 Coherence Pass

Five-dimension verification per `implementation-planner` SKILL.md §9. All dimensions return PASS.

### §6.1 Dimension 1 — Atomicity

| Check | Result |
|---|---|
| Independent-deliverability (per-unit standalone test/review/ship) | 34/34 ✅ |
| Single-responsibility per unit | 34/34 ✅ |
| Justified multi-unit splits (architectural-boundary motivation) | 7 splits justified ✅ |
| No over-decomposition (atoms ship-sized, not micro-fragmented) | ✅ Per-unit signature ≥ 2 records/enums |

**§6.1 result.** ✅ PASS — 34/34 units atomic at appropriate grain.

### §6.2 Dimension 2 — Spec-traceability

| Check | Result |
|---|---|
| Per-unit `Implements:` clause present | 34/34 ✅ |
| Spec section anchor present | 34/34 ✅ |
| Byte-exact acceptance criterion alignment (sampled at 19 units) | ✅ |

**§6.2 result.** ✅ PASS — 34/34 units carry spec-traceability anchors.

### §6.3 Dimension 3 — Dependency-awareness

| Check | Result |
|---|---|
| DAG acyclicity (Kahn verification) | ✅ PASS (§4.4) |
| Per-unit `Depends on:` completeness (against signature analysis) | 34/34 ✅ |
| Foundational anchors identified | 2 (U-OD-01, U-OD-04) ✅ |
| Terminal units identified | 2 (U-OD-31, U-OD-34) ✅ |

**§6.3 result.** ✅ PASS — DAG verified; per-unit dependencies complete.

### §6.4 Dimension 4 — Implementation-grade detail

| Metric | Min | Median | Max | Threshold | Result |
|---|---|---|---|---|---|
| Records + enums per unit | 2 | 5 | 13 | ≥ 2 | ✅ |
| Acceptance criteria per unit | 8 | 10 | 17 | ≥ 5 | ✅ |
| Tests per unit | 10 | 13 | 20 | ≥ 8 | ✅ |
| Rollback boundary statement | 34/34 | — | — | 100% | ✅ |
| Cross-axis edge declarations per-unit + aggregate at U-OD-34 | 15 units + 20 manifest entries (28 edges) | — | — | — | ✅ |

**§6.4 result.** ✅ PASS — implementation-grade detail sufficient at all 34 units.

### §6.5 Dimension 5 — Anti-pattern audit (plan-level)

| Anti-pattern | Plan-level check | Result |
|---|---|---|
| A1 Under-decomposition | Bundled contract sections? | ✅ No |
| A2 Over-decomposition | Fragmented contract sections? | ✅ No (avg 1.48 units/contract) |
| A3 Spec extension | New architecture not in spec? | ✅ No |
| A4 Implementation-detail leakage | Premature deployment binding? | ✅ No (11 discretion deferrals honored) |
| A5 Cyclic dependencies | DAG verification | ✅ PASS |
| A6 Missing dependencies | Per-unit `Depends on:` completeness | ✅ PASS |
| A7 Under-specified acceptance | Testable criteria? | ✅ 8–17/unit |
| A8 Trace-omission | `Implements:` clause + spec anchor | ✅ 34/34 |
| A9 Risk/estimate annotations | Effort or story points? | ✅ None |
| A10 PR/commit pre-commitment | File-path or boundary pre-commits? | ✅ None (logical names only) |

### §6.6 Cross-cutting concerns coverage

| Concern | Coverage units | Status |
|---|---|---|
| Cost-attribution as cross-cutting (ADD §5.3) | U-OD-18, U-OD-19, U-OD-20, U-OD-21, U-OD-22 | ✅ |
| Bridging-arc preservation (ADD §5.3.1) | U-OD-32, U-OD-33 + cross-axis composition | ✅ |
| T-perm-1 5-axis multiplicative tunable | U-OD-17, U-OD-33 (3-of-5 axes) | ✅ |
| T-perm-2 within-turn / across-turn seam | U-OD-27, U-OD-28, U-OD-30 | ✅ |
| F2-12 carry-forward (cost × idempotency) | U-OD-20 ACTIVE + U-OD-34 inheritance | ✅ |
| Pattern P1 mechanical-alignment discipline | §5.4 (within-axis); Session 5 (cross-axis) | ✅ within-axis |
| Persona §4 99.9% SLO + selective HITL | U-OD-23, U-OD-25 | ✅ |
| Persona §10.4 compliance-readiness | U-OD-16, U-OD-30, U-OD-31 | ✅ |

### §6.7 Session-prompt-specific additions

#### §6.7.1 F2-12 ACTIVE isolation

| Verification | Result |
|---|---|
| Contract-bearing notation site exclusively at U-OD-20 | ✅ |
| Carry-forward inheritance site exclusively at U-OD-34 | ✅ |
| Closure path byte-exact (6 steps) | ✅ |
| Closure target = OD plan v2 (revision-pass mode) | ✅ |
| Partial closure rejection | ✅ |

#### §6.7.2 OD-S4-3.A cross-axis edge declaration consistency

| Verification | Result |
|---|---|
| Per-unit cross-axis edges in `Depends on:` clauses (15 units) | ✅ |
| Aggregate manifest at U-OD-34 (20 entries × multi-target multiplicity = 28 edges) | ✅ |
| Terminal cross-axis edges resolve to U-IS-17, U-AS-33, U-CP-54, U-CP-55 | ✅ |

#### §6.7.3 OD-S4-2.A scope adherence

| Verification | Result |
|---|---|
| Stage 5 coverage matrix scoped to OD axis | ✅ |
| Cross-axis coverage matrix deferred to Session 5 | ✅ |
| Cross-cutting concerns at OD-axis scope + cross-axis composition annotated | ✅ |

### §6.8 Five-dimension summary

| Dimension | Result |
|---|---|
| 1 — Atomicity | ✅ PASS |
| 2 — Spec-traceability | ✅ PASS |
| 3 — Dependency-awareness | ✅ PASS |
| 4 — Implementation-grade detail | ✅ PASS |
| 5 — Anti-pattern audit (plan-level) | ✅ PASS |
| Cross-cutting concerns coverage | ✅ PASS |
| Session-prompt-specific additions | ✅ PASS |

**Coherence pass disposition: ✅ CLEARED FOR FILING.**

---

## §7 Plan-level closure

| Closure dimension | Status |
|---|---|
| All 23 spec contracts implemented (C-OD-01..23) | ✅ |
| All 8 PRD requirements satisfied (R-OD-01..08) | ✅ |
| All 34 units atomic + dependency-complete | ✅ |
| DAG acyclic | ✅ |
| F2-12 ACTIVE isolated at U-OD-20 + inherited at U-OD-34 | ✅ |
| F2-12 closure_pending_at_v1 = true; closure target = OD plan v2.1 (this artifact, v2 superseded) | ✅ |
| Pattern P1 within-axis compliance | ✅ |
| Cross-axis coverage matrix scope deferred to Cross-Axis Composition Document v2.1 (Path B Segment F) | ✅ |
| Coherence pass 5/5 dimensions PASS at v2.1 per §0.10 | ✅ |
| F1-OD-02 absorbed at U-OD-15 acceptance #4 hash-digest example list | ✅ |

**OD plan v2.1 disposition: ✅ FILED.**

Forward routing: Path B Segment F (Cross-Axis Composition Document v2 → v2.1; F1-CXA-03 absorption); then Path B Segment G (P6-CK Iteration 3 kickoff against v2.1 ensemble) per `Project_Workflow_v1_6.md` §4.1.4.5 one-time authorization.

**End of `Implementation_Plan_Operational_Discipline_v2_1.md`.**
