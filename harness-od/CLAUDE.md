# harness-od/CLAUDE.md — Operational Discipline (OD) Axis

*Per-axis subdirectory guidance for the OD axis. Loaded by Claude Code at session startup alongside workspace root `CLAUDE.md`. Canonical pointer to design-phase OD-axis artifacts.*

---

## 1. Axis identity + scope boundary

### 1.1 Axis identity

The Operational Discipline (OD) axis owns **observability + cost + audit + HITL primitive**: HITL invocation primitive (4-response palette canonical schema), audit ledger schema (hash-chain integrity composition), cost attribution 5-step chain (per-attempt + idempotency-key join + hash-chain composition + replay-aware dedup + cause_attribution invariance), validator fail catalog (medium-cardinality cause_attribution + 5-class fail-class taxonomy), 15-namespace OTel observability ingestion map (`anthropic.*` / `mcp.*` / `skill.*` / `managed_agents.*` / `sandbox.*` / `hitl.*` / `topology.*` / `subagent.*` / `engine.*` / `audit.*` / `validator.fail.*` / `files.*` / `memory.*` / `harness.breaker.*` / `provider_discriminator.*`), F3 capability-floor lifecycle event mapping, in-process OTLP collector + sampling discipline.

OD posture per `Cross_Axis_Composition_Document_v2_1.md` §2.1: **consumer-most-downstream axis** — 0 outbound cross-axis edges; 26 inbound consumer edges (6 → IS at CXA v2.1 baseline / 4 at OD plan v2.6 per C3-15; 10 → AS; 12 → CP). OD terminates the axis-level dependency graph.

### 1.2 Spec + plan authority

| Artifact | Version | Role |
|---|---|---|
| `Spec_Operational_Discipline_v1_4.md` | v1.4 (delta over v1.3; v1.4 formalizes the C-OD-20 §20.1 `CollectorPlacement` 7-value enum + grows the §1.2 enum 6→7 — FF-2 resolution) | Contract authority — 23 contracts C-OD-01 through C-OD-23 |
| `Implementation_Plan_Operational_Discipline_v2_10.md` | v2.10 (delta chain over v2.9/v2.8/v2.7/v2.6; v2.8 = five Class 1 defects + F3 pinning; v2.9 = FF-2 U-OD-28; v2.10 = FF-3 U-OD-29 `SandboxTier` conformance) | Execution authority — 35 atomic units across 8 clusters (+ U-OD-00 pre-cluster) and 10 topological levels (L0–L9) |

### 1.3 Scope inclusion

| Surface | Carrier units | Spec contract |
|---|---|---|
| Foundational cost-attribution + telemetry primitives | U-OD-01, U-OD-04 (L0 anchors) | C-OD-01 + C-OD-04 |
| HITL primitive — 4-response palette (4 canonical event names: `hitl.gate.evaluated` / `hitl.invocation.opened` / `hitl.invocation.responded` / `hitl.invocation.timed_out`) | U-OD-NN (Cluster 1) | C-OD-05 row 6 |
| 15-namespace ingestion map | U-OD-NN (Cluster 2–3) | C-OD-05 §5.1 |
| F3 capability-floor lifecycle event mapping (`workflow.start` / `step.boundary` / `fallback.triggered` / `retry.attempt` / `breaker.tripped` / `lease.acquired` / `lease.released` / `workflow.resumed` — the eight event classes per spec C-OD-06 §6.1, canonical; pinned at OD plan v2.8 §0.5) | U-OD-08 (Cluster 2) | C-OD-06 §6.1 |
| 7-attribute `harness.breaker.*` canonical schema | U-OD-NN (Cluster 3) | C-OD-07 §7.1 |
| Cost attribution 5-step chain | U-OD-14 through U-OD-17 | C-OD-12 + C-OD-13 |
| Audit-ledger schema + 8-field SHA-256 composition + field-ordering | U-OD-20 | C-OD-14 §14.5.1 |
| 8-row audit-ledger enumeration | U-OD-20 | C-OD-14 §14.5.2 |
| Validator fail catalog (cause_attribution) | U-OD-NN (Cluster 6) | C-OD-NN |
| In-process OTLP collector + sampling discipline | U-OD-NN (Cluster 7) | C-OD-NN |
| OD substrate seam exports manifest (terminal aggregate exporter) | U-OD-34 | C-OD-23 |

### 1.4 Scope exclusion

| NOT OD | Owning axis / source |
|---|---|
| Path-class registry, state ledger, hash-chain *implementation* (canonical at IS), JSONL composition | IS — `harness-is/CLAUDE.md`. OD consumes IS hash-chain primitives via U-IS-08/09/10 cross-axis edges |
| SandboxTier enum, tool contract schemas, sandbox observability emission (canonical at AS) | AS — `harness-as/CLAUDE.md`. OD ingests `sandbox.*` namespace per D6 §1.2 |
| Multi-LLM routing, retry mechanism implementation, fallback chain composition, workflow lifecycle, topology pattern, HITL placement decision logic, sub-agent handoff schemas | CP — `harness-cp/CLAUDE.md`. OD ingests CP-emitted namespaces (`routing.*` / `fallback.*` / `retry.*` / `engine.*` / `topology.*` / `subagent.*` / `hitl.*` / `harness.breaker.*`) |

**D6 ingestion pattern.** OD canonical authority for: (a) namespace map (C-OD-05 15-row enumeration); (b) lifecycle event mapping (C-OD-06); (c) `harness.breaker.*` 7-attribute schema (C-OD-07 §7.1); (d) cost attribution chain (C-OD-12 + C-OD-13). CP/AS emit per OD's canonical attribute set. Composition site at OD spec; emission site at CP/AS plans.

---

## 2. Per-axis canonical artifacts

### 2.1 Anchoring ADRs

| ADR | Version | Role |
|---|---|---|
| ADR-D1 | v1.2 | Engine + replay (replay-trace-emission contract; F2-12 closure) |
| ADR-D4 | v1.1 | Workload classes (per-workload sampling discipline) |
| ADR-D5 | v1.3 | HITL palette canonical (4-event-name set per §1.8) + cross-deployment monotonicity |
| ADR-D6 | v1.2 | Observability + cost-attribution (12-namespace span schema; canonical) |
| ADR-F2 | v1.2 | State ledger substrate (hash-chain integrity composition consumed at audit) |
| ADR-F3 | v1.1 | Engine event history (lifecycle event categorization) |

ADD attestation: `Architectural_Design_Document_v1_3.md` v1.3.

### 2.2 Cross-axis edge inventory (CXA v2.1)

OD is consumer-most-downstream; all OD-direction edges are **outbound consumer edges**:

| Edge direction | Edges | Source artifact |
|---|---|---|
| OD → IS (outbound consumer) | 6 (CXA v2.1 baseline) / 4 (OD plan v2.6 §4.5.1 per C3-15 Path (i-refined) deletions) | `Cross_Axis_Composition_Document_v2_1.md` §2.3.5; `Implementation_Plan_Operational_Discipline_v2_6.md` §0.7 + §4.5.1 |
| OD → AS (outbound consumer) | 10 | `Cross_Axis_Composition_Document_v2_1.md` §2.3.6 |
| OD → CP (outbound consumer) | 12 | `Cross_Axis_Composition_Document_v2_1.md` §2.3.3 |
| **OD outbound (downstream)** | **0** | OD terminates the axis-level dependency graph |

CXA-OD-IS-EDGE-DRIFT Class 3 informational item: CXA v2.1 §2.3.5 enumerates 6 edges (baseline at OD plan v2.3); OD plan v2.6 §4.5.1 enumerates 4 (rows 2 + 3 deleted as OD-internal mis-routed; rows 4 + 5 remapped to canonical IS contracts). Routing: future composition-document revision pass; non-blocking.

### 2.3 OD-internal cross-cluster dependencies (NOT cross-axis)

Per `Implementation_Plan_Operational_Discipline_v2_6.md` §0.7 + §0.9: sqlite substrate residence + ring-buffer eviction are OD-internal concerns (NOT cross-axis edges). C3-15 closure formalized this distinction via Path (i-refined) deletions at v2.6 §4.5.1. OD-internal cross-cluster compositions are within-axis dependencies; cross-axis enumeration at §4.5 covers cross-axis only.

---

## 3. Topological entry-points (Level 0)

Per `Implementation_Plan_Operational_Discipline_v1.md` §0.2 plan-level invariants (preserved at v2.6):

| L0 unit | Scope | Cluster |
|---|---|---|
| U-OD-00 | OD-local audit-ledger composition-type carrier (added at OD plan v2.6 per revision pass R5) | pre-cluster |
| U-OD-01 | Foundational cost-attribution primitive | 1 |
| U-OD-04 | Foundational telemetry primitive | 1 |

**3 L0 units; in-degree 0.** Phase 7 sub-phase 7b OD-axis-stream execution begins from these entry-points.

### 3.1 OD plan-level invariants (preserved at v2.6)

| Invariant | Value |
|---|---|
| Atomic units | 35 (U-OD-00, U-OD-01 through U-OD-34) — U-OD-00 added at v2.6 per R5 |
| Clusters | 8 (+ U-OD-00 pre-cluster) |
| Spec contracts covered | 23 of 23 (C-OD-01 through C-OD-23) |
| PRD requirements satisfied | 8 of 8 (R-OD-01 through R-OD-08) plus cross-axis surface |
| Within-axis directed edges | 102 (v2.6: +2 M-2 hidden-coupling edges) |
| Cross-axis directed edges | 26 (IS=4; AS=10; CP=12) per OD plan v2.6 §4.5.1 |
| Cross-axis-touching units | 16 of 35 |
| Foundational anchors (L0) | 3 (U-OD-00, U-OD-01, U-OD-04) |
| Terminal units (L9) | 2 (U-OD-31, U-OD-34) |
| Level depth | 10 (L0–L9) |
| F2-12 ACTIVE contract-bearing sites | 1 (U-OD-20) — CLOSED at v2.2 cascade |
| F2-12 carry-forward inheritance sites | 1 (U-OD-34) — CLOSED at v2.2 cascade |

### 3.2 Coverage matrix verification

Per OD plan §4 (preserved at v2.6): 23 of 23 contracts covered by ≥1 unit; no coverage gaps. Coverage matrix per-axis-only per OD-S4-2.A.

---

## 4. Substitution + anti-leakage surface

### 4.1 OD-axis substitutions (8 entries)

Per `Phase_7_Meta_Architecture_v1.md` §5.5. H_E classification per §4.4.4 — **OD is the most-absent axis**:

| H_T primitive class | Count | Representative primitives |
|---|---|---|
| ✗ absent | 7 | H_T-OD-1 (deferral envelope — `ToolSearch` ≠ deferral envelope, categorical mismatch); H_T-OD-2 (OTel SDK injection — H_E telemetry closed); H_T-OD-3 (sampling-discipline surface); H_T-OD-4 (SpanProcessor injection); H_T-OD-6 (in-process OTLP collector); H_T-OD-7 (preservation discipline); H_T-OD-8 (authoring artifact) |
| ~ partial | 1 | H_T-OD-5 (`/cost` + `--max-budget-usd` coarse; not 5-step chain) |
| ✓ native | 0 | None |

**OD is the most distinct H_E ↔ H_T boundary.** All OD substitutions retire at OD-axis unit landings; no native H_E carrier covers any OD primitive in full. The substrate-boundary discipline (X-AL-1: H_E ↔ H_T boundary at MCP server process) is canonical at OD axis per OD-AL-3.

Full per-substitution bounded-scope + retirement criterion at Meta-Architecture §5.5.

### 4.2 OD-axis anti-leakage rules (3 entries)

Per `Phase_7_Meta_Architecture_v1.md` §7.5:

| Rule | Statement | Anti-pattern foreclosed |
|---|---|---|
| OD-AL-1 | H_E telemetry (internal Claude Code analytics, closed surface) ≠ harness observability substrate (instruments the harness for harness operators) | Assuming H_E telemetry covers H_T's `sandbox.*` / `mcp.*` / `skill.*` / `topology.*` / `subagent.*` / `engine.*` / `audit.*` / `validator.fail.*` / `harness.breaker.*` namespace emission |
| OD-AL-2 | H_E `/cost` (session-grain coarse cost) ≠ H_T cost-attribution 5-step chain (per-attempt + idempotency-key join + hash-chain integrity composition + replay-aware dedup + cause_attribution invariance) | Authoring U-OD-17 → U-OD-22 to delegate cost computation to `/cost`-derived data |
| OD-AL-3 | All OTel emission during 7a happens at MCP server boundary (H_T-authored code). H_E does not participate in OTel emission. Boundary is load-bearing — prevents H_E internal telemetry from contaminating H_T trace schemas | Attempting to inject OTel SpanProcessors into H_E's emission path; constructing H_T spans by parsing H_E session logs |

Cross-cutting rules X-AL-1 / X-AL-2 / X-AL-3 (Meta-Architecture §7.7) also bind OD-axis implementation. **OD-AL-3 is the canonical concretization of X-AL-1** — substrate-boundary at MCP server process is enforced at OD via "no H_E participation in OTel emission" rather than convention.

---

## 5. Back-flow channels

Axis-specific design defects route per `Project_Workflow_v1_8.md` §2.7.6 + workspace root `CLAUDE.md` §4.3.

### 5.1 Class 1 routing by defect locus

| Defect locus | Class 1 routing |
|---|---|
| OD plan v2.6 atomic unit signature defect | Phase 6 plan revision-pass at design-phase workspace |
| OD spec v1.3 contract defect (C-OD-NN under-specifies the surface; spec inconsistent with ADR) | Phase 5 spec revision-pass at design-phase workspace |
| ADR-D1 v1.2 / D4 v1.1 / D5 v1.3 / D6 v1.2 / F2 v1.2 / F3 v1.1 anchor decision defect | Phase 3a/3b ADR revision via council convening |
| ADD v1.3 attestation mismatch with OD spec v1.3 | Phase 3d ADD revision |
| CXA v2.1 §2.3.3 (OD→CP) / §2.3.5 (OD→IS) / §2.3.6 (OD→AS) edge defect | Phase 6 CXA revision-pass at design-phase workspace |
| OD substrate seam (U-OD-34 manifest) defect; cascade to consumer-side plans (none — OD is consumer-most-downstream) | Phase 6 OD plan revision-pass |

### 5.2 Open carry-forwards at OD axis entry

| Carry-forward | Status | Routing |
|---|---|---|
| F2-12 cascade Step 6b (OD plan layer) | CLOSED at v2.2; preserved through v2.6 per `F2-12_Closure_Declaration.md` | No action |
| F3-02 IS-axis revision (U-OD-20 acceptance #11 `Depends on` placeholder `U-IS-NN` → canonical `U-IS-12`) | CLOSED at v2.4 §0.7 (Form A — citation precision); preserved at v2.6 | No action |
| C3-15 Path (i-refined) deletions at §4.5.1 (OD-internal mis-routed cross-axis edges) | CLOSED at v2.4 §0.7; preserved at v2.6 | No action |
| CXA-OD-IS-EDGE-DRIFT (Class 3 informational) | CXA v2.1 §2.3.5 enumerates 6 edges; OD plan v2.6 §4.5.1 enumerates 4 | Non-blocking; future composition-document revision pass |
| OD-INTERNAL-FORMALIZATION (Class 3 informational) | OD plan lacks explicit "OD-internal cross-cluster dependency" section that canonicalizes sqlite substrate + ring-buffer eviction as within-axis (non-cross-axis) compositions | Non-blocking; future OD plan revision pass (formalization deferred) |

### 5.3 Filing footer

| Field | Value |
|---|---|
| Artifact | `harness-od/CLAUDE.md` |
| Authored at | Phase 6.5 Session 6 (ε), 2026-05-15 |
| Authoring authority | `Phase_6_5_Session_6_Kickoff.md` §2.1.2 |
| Predecessor | Design-phase workspace OD spec v1.3 + OD plan v2.6 |
| Revision policy | This file is canonical for the `harness-od/` subdirectory; revisions route to design-phase back-flow per §5.1 |

---

*End of `harness-od/CLAUDE.md`. Parent guidance at workspace root `CLAUDE.md`. OD spec + plan + CXA v2.1 §2.3.3 / §2.3.5 / §2.3.6 at design-phase workspace.*
