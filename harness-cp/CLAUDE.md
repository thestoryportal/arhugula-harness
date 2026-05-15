# harness-cp/CLAUDE.md — Control Plane (CP) Axis

*Per-axis subdirectory guidance for the CP axis. Loaded by Claude Code at session startup alongside workspace root `CLAUDE.md`. Canonical pointer to design-phase CP-axis artifacts.*

---

## 1. Axis identity + scope boundary

### 1.1 Axis identity

The Control Plane (CP) axis owns **orchestration**: multi-LLM routing core + provider portability (ADR-F1 v1.2 anchor), per-layer time-budget + retry namespaces, fallback chain composition + cross-family fallback, workflow manifest schema + per-step override evaluator + audit-ledger composition, EngineClass + ResumptionKind taxonomies, TopologyPattern 6-class enum + admissibility + CascadePolicy, sub-agent handoff schemas, HITL placement + 4-response palette, sandbox-tier dispatch, Skills enabling discipline (CP-side), memory + files primitive consumption, MCP integration + per-server trust framework function, cross-deployment monotonicity.

CP posture per `Cross_Axis_Composition_Document_v2_1.md` §2.1: **largest cross-axis consumer** (60 outbound edges; 36 → IS + 24 → AS); consumer of 12 OD→CP inbound edges (excluded from outbound; CP terminal manifests U-CP-54 + U-CP-55 surface CP exports for OD consumption). Largest axis by unit count (55) and contract count (24).

### 1.2 Spec + plan authority

| Artifact | Version | Role |
|---|---|---|
| `Spec_Control_Plane_v1_3.md` | v1.3 | Contract authority — 24 contracts C-CP-01 through C-CP-24 |
| `Implementation_Plan_Control_Plane_v2_3.md` | v2.3 (P6-CK Iter 4 close; F2-01 + F2-02 + F2-03 absorbed) | Execution authority — 55 atomic units across 9 clusters and 9 topological levels (L0–L8) |

### 1.3 Scope inclusion — 9 clusters

Per `Implementation_Plan_Control_Plane_v1.md` §3.3 cluster table (preserved verbatim at v2.3 §3):

| Cluster | Scope | Carrier units | Anchor contracts |
|---|---|---|---|
| 1 | F1 routing + fallback + breaker + retry namespaces (multi-LLM provider portability; cross-family fallback) | U-CP-01 → U-CP-09 (9) | C-CP-01 + C-CP-02 + C-CP-03 + C-CP-04 |
| 2 | F3 lifecycle event emission + workflow manifest schema + per-step override evaluator | U-CP-10 → U-CP-14 (5) | C-CP-05 + C-CP-06 |
| 3 | D1 engine + replay (EngineClass enum + workload-binding 5-step selection + F2-substrate-join + ResumptionKind 5-class + `engine.*` namespace) | U-CP-15 → U-CP-21 (7) | C-CP-07 + C-CP-08 + C-CP-09 |
| 4 | D4 topology + sub-agent + workload commitment + sandbox-tier dispatch | U-CP-22 → U-CP-27 (6) | C-CP-10 + C-CP-11 + C-CP-12 |
| 5 | D4 handoff (4-record schema) + spans (`topology.*` + `subagent.*` namespaces) + Skills enabling + memory + files | U-CP-28 → U-CP-36 (9) | C-CP-13 + C-CP-14 + C-CP-15 + C-CP-16 + C-CP-17 |
| 6 | D5 HITL palette (4-response) + placement + invocation matrix | U-CP-37 → U-CP-41 (5) | C-CP-18 + C-CP-19 + C-CP-20 |
| 7 | D5 multiplicative gate + audit crypto | U-CP-42 → U-CP-46 (5) | C-CP-20 + C-CP-21 |
| 8 | D5 escalation + revalidation | U-CP-47 → U-CP-52 (6) | C-CP-22 + C-CP-23 |
| 9 | T-perm-3 + exports (terminal aggregate exporter manifests) | U-CP-53, U-CP-54, U-CP-55 (3) | C-CP-24 |

### 1.4 Scope exclusion

| NOT CP | Owning axis / source |
|---|---|
| Path-class registry, state ledger, hash-chain, JSONL composition, worktree isolation | IS — `harness-is/CLAUDE.md` |
| SandboxTier enum + tier-monotonicity, tool contract schemas, MCP server boundary, Skills filesystem residence, sandbox observability `sandbox.*` namespace | AS — `harness-as/CLAUDE.md` |
| HITL primitive implementation, cost attribution 5-step chain, audit ledger schema (canonical), validator fail catalog, OD observability namespaces (`audit.*` / `validator.fail.*` / `harness.breaker.*` canonical schema) | OD — `harness-od/CLAUDE.md` |
| Within-axis cycles | CP DAG is acyclic per CP plan v1 §3.4 Kahn execution; cycle re-introduction is a Class 1 fork |

CP and OD share authority over several namespaces (`hitl.*`, `topology.*`, `subagent.*`, `engine.*`, `harness.breaker.*`) via the **D6 ingestion pattern**: CP emits, OD ingests. Authoritative schema lives at OD spec; CP emits per OD's canonical attribute set.

---

## 2. Per-axis canonical artifacts

### 2.1 Anchoring ADRs

Per `Phase_7_Meta_Architecture_v1.md` §2.3 CP-axis primitives:

| ADR | Version | Role |
|---|---|---|
| ADR-F1 | v1.2 | Provider portability (multi-LLM commitment) |
| ADR-F2 | v1.2 | State ledger substrate (CP→IS join) |
| ADR-F3 | v1.1 | Engine event history |
| ADR-F5 | v1.1 | Skills (CP-side enabling discipline) |
| ADR-D1 | v1.2 | Engine + replay |
| ADR-D2 | v1.1 | Sandbox + blast radius (CP-side dispatch) |
| ADR-D3 | v1.2 | Filesystem residence (files primitive consumption) |
| ADR-D4 | v1.1 | Workload classes |
| ADR-D5 | v1.3 | Cross-deployment monotonicity + HITL palette |
| ADR-D6 | v1.2 | Observability + cost-attribution |

ADD attestation: `Architectural_Design_Document_v1_3.md` v1.3.

### 2.2 CP export seams (consumed by OD)

CP terminal aggregate exporters: U-CP-54 + U-CP-55 (per C-CP-24 §24). 12 OD→CP edges consume CP export surfaces. Per-edge enumeration at `Cross_Axis_Composition_Document_v2_1.md` §2.3.3.

### 2.3 Cross-axis edge inventory (CXA v2.1)

| Edge direction | Edges | Source artifact |
|---|---|---|
| CP → IS (outbound) | 36 | `Cross_Axis_Composition_Document_v2_1.md` §2.3.2; `Implementation_Plan_Control_Plane_v1.md` §3.3 |
| CP → AS (outbound) | 24 | `Cross_Axis_Composition_Document_v2_1.md` §2.3.4; CP plan §3.3 |
| OD → CP (inbound) | 12 | `Cross_Axis_Composition_Document_v2_1.md` §2.3.3 |
| CP → OD (outbound) | 0 | OD pulls from CP via U-CP-54 + U-CP-55 manifest |

### 2.4 Per-cluster cross-axis edge profile (preserved at v2.3)

| Cluster | Units | Within-axis edges | → IS edges | → AS edges | Total edges |
|---|---|---|---|---|---|
| 1 (F1 routing + fallback) | 9 | 14 | 3 | 1 | 18 |
| 2 (F3 lifecycle + manifest) | 5 | 9 | 5 | 0 | 14 |
| 3 (D1 engine + replay) | 7 | 9 | 4 | 0 | 13 |
| 4 (D4 topology + sub-agent) | 6 | 8 | 5 | 4 | 17 |
| 5 (D4 handoff + spans + audit) | 9 | 15 | 9 | 5 | 29 |
| 6 (D5 HITL palette + placement) | 5 | 15 | 2 | 0 | 17 |
| 7 (D5 multiplicative gate + audit crypto) | 5 | 19 | 4 | 7 | 30 |
| 8 (D5 escalation + revalidation) | 6 | 24 | 4 | 4 | 32 |
| 9 (T-perm-3 + exports) | 3 | 21 | 1 | 2 | 24 |
| **Total** | **55** | **124** | **36** | **24** | **184** |

---

## 3. Topological entry-points (Level 0)

Per `Implementation_Plan_Control_Plane_v1.md` §3.2 topological levels (preserved verbatim at v2.3):

| L0 unit | Scope | Cluster |
|---|---|---|
| U-CP-01 | `routing.*` namespace + ProviderCapabilities | 1 |
| U-CP-02 | Layered routing strategy (declarative → embedding → LLM-as-router) | 1 |
| U-CP-03 | Per-layer time-budget | 1 |
| U-CP-07 | `fallback.*` + `harness.breaker.*` + `retry.*` namespaces (v2.3 amendment: retry.* extended to 6-attribute child span schema + parent-span event 3-field schema + dual-emission discipline) | 1 |
| U-CP-10 | `LifecycleEventClass` enum | 2 |
| U-CP-11 | `lease.*` namespace | 2 |
| U-CP-15 | `EngineClass` 5-class enum | 3 |
| U-CP-19 | `ResumptionKind` 5-class taxonomy | 3 |
| U-CP-21 | Replay disposition mapping (`REPLAY_DISPOSITION_MAPPING`) | 3 |
| U-CP-22 | `TopologyPattern` 6-class enum + admissibility | 4 |
| U-CP-26 | Sandbox-tier dispatch (depends on U-AS-01 cross-axis only) | 4 |
| U-CP-28 | `HandoffContext` schema | 5 |
| U-CP-37 | HITL palette declaration (4-response) | 6 |

**13 L0 units; in-degree 0 (or cross-axis-only deps).** Phase 7 sub-phase 7b CP-axis-stream execution begins from these entry-points.

### 3.1 DAG topology (9 levels; 55 nodes; 124 within-axis edges)

```
L0  (13 units; foundational + cross-axis-only deps)
L1  (8 units)   ← U-CP-04, U-CP-06, U-CP-08, U-CP-16, U-CP-23, U-CP-29, U-CP-38, U-CP-47
L2  (10 units)  ← U-CP-05, U-CP-09, U-CP-13, U-CP-17, U-CP-18, U-CP-24, U-CP-30, U-CP-31, U-CP-39, U-CP-42
L3  (8 units)   ← U-CP-12, U-CP-14, U-CP-20, U-CP-25, U-CP-33, U-CP-34, U-CP-40, U-CP-44
L4  (5 units)   ← U-CP-27, U-CP-35, U-CP-41, U-CP-43, U-CP-48
L5  (4 units)   ← U-CP-32, U-CP-36, U-CP-45, U-CP-49
L6  (3 units)   ← U-CP-46, U-CP-50, U-CP-52
L7  (3 units)   ← U-CP-51, U-CP-53, U-CP-54
L8  (1 unit)    ← U-CP-55 (terminal aggregate exporter; F2-12 cascade Step 6a closure record carrier)
```

DAG verified acyclic per CP plan §3.4 Kahn execution: 55 units consumed; remaining edge set ∅.

### 3.2 Coverage matrix verification

Per CP plan §4 (preserved at v2.3 with v2.3 coverage deltas at U-CP-07 + U-CP-12): 24 of 24 contracts covered by ≥1 unit; no coverage gaps. Coverage matrix per-axis-only per OD-S3-2.A.

---

## 4. Substitution + anti-leakage surface

### 4.1 CP-axis substitutions (21 entries — largest axis)

Per `Phase_7_Meta_Architecture_v1.md` §5.4 — **CP carries 21 of 49 substitution entries (42.9%)**, reflecting deepest H_T-CP-vs-H_E gap. H_E classification per §4.4.3:

| H_T primitive class | Count | Representative primitives |
|---|---|---|
| ✗ absent (no H_E surface) | 12 | H_T-CP-1 (multi-LLM routing core); H_T-CP-2 (layered routing); H_T-CP-3 (retry.* namespace); H_T-CP-5 (fallback chain); H_T-CP-7 (EngineClass); H_T-CP-8 (F2-substrate-join); H_T-CP-11 (workload-class taxonomy); H_T-CP-14 (topology/subagent namespace emission); H_T-CP-19 (cross-deployment monotonicity); H_T-CP-21 (validator framework); H_T-CP-23 (bridging-arc concept); H_T-CP-24 (authoring artifact) |
| ~ partial (H_E covers subset) | 11 | H_T-CP-4 (`--fallback-model` single-target only); H_T-CP-6 (`CLAUDE.md` flat ≠ typed manifest); H_T-CP-9 (binary session resume ≠ 5-class typed); H_T-CP-10 (one implicit topology ≠ 6-class enum); H_T-CP-12 (permission modes ≠ sandbox-tier dispatch); H_T-CP-13 (`Agent` free-text ≠ typed handoff schemas); H_T-CP-16/17/18 (memory/files/mcp native; no namespace emission); H_T-CP-20 (`AskUserQuestion` ≠ 4-response palette); H_T-CP-22 (`/compact` coarse pause/resume) |
| ✓ native (H_E covers) | 1 | H_T-CP-15 (automatic Skills enabling per frontmatter) |

**H_T-CP-1 is the Class 2 substitution-risk surface** per `Phase_7_Meta_Architecture_v1.md` §9: multi-LLM-by-design commitment per ADR-F1 v1.2 is unmet at 7a runtime (single-LLM during bootstrap). Substitution retirement bound at U-CP-01 landing; CLOSED with operator visibility preserved across workflow-revision boundary per `Project_Workflow_v1_8.md` §2.7.7.

Full per-substitution bounded-scope + retirement criterion at Meta-Architecture §5.4.

### 4.2 CP-axis anti-leakage rules (5 — largest rule set)

Per `Phase_7_Meta_Architecture_v1.md` §7.4 — CP carries 5 of 17 axis-bound rules (29.4%):

| Rule | Statement | Anti-pattern foreclosed |
|---|---|---|
| **CP-AL-1** | H_E sub-agent topology (orchestrator-workers via `Agent` tool) ≠ H_T TopologyPattern 6-class enum (single-threaded-linear / orchestrator-workers / decentralized-handoff / hierarchical-delegation / evaluator-optimizer / parallelization) | Concluding "we already have orchestrator-workers" implies H_T-CP-10 is met |
| CP-AL-2 | H_E session resume binary operations ≠ ResumptionKind 5-class typed taxonomy (CRASH_RECOVERY / EXPLICIT_PAUSE / TIMEOUT / HITL_PENDING / VALIDATOR_FAIL) | Treating any H_E session resume as evidence that U-CP-19 / U-CP-20 / U-CP-21 are functionally complete |
| CP-AL-3 | H_E `--fallback-model` (single-target, overload-only, print-mode-only) ≠ H_T multi-step chain composition with cross-family fallback | Authoring U-CP-04 / U-CP-05 to wrap `--fallback-model` as the fallback chain implementation |
| CP-AL-4 | H_E `--model` single-LLM ≠ routing core. Single-LLM-during-7a is *runtime* substitution; multi-LLM design commitment unchanged at ADR-F1 v1.2 + U-CP-01 specification | Concluding "we use Claude exclusively" implies the project's multi-LLM commitment is abandoned |
| CP-AL-5 | H_E `CLAUDE.md` (prose convention loaded into system prompt) ≠ typed `WorkflowManifestEntry` schema with per-step override evaluator + audit | Treating `CLAUDE.md` declarations as functional substitute for typed workflow manifest entries |

Cross-cutting rules X-AL-1 / X-AL-2 / X-AL-3 (Meta-Architecture §7.7) also bind CP-axis implementation.

**CP-AL-1 is the most load-bearing rule at the H_E ↔ H_T boundary.** See `Sub_Agent_Boundary_Specification_v1.md` at workspace root for the explicit anti-leakage application + per-sub-agent scope discipline + verbatim citation per kickoff §5.2.4.

---

## 5. Back-flow channels

Axis-specific design defects route per `Project_Workflow_v1_8.md` §2.7.6 + workspace root `CLAUDE.md` §4.3.

### 5.1 Class 1 routing by defect locus

| Defect locus | Class 1 routing |
|---|---|
| CP plan v2.3 atomic unit signature defect | Phase 6 plan revision-pass at design-phase workspace |
| CP spec v1.3 contract defect (C-CP-NN under-specifies the surface; spec inconsistent with ADR) | Phase 5 spec revision-pass at design-phase workspace |
| ADR-F1 v1.2 / F2 v1.2 / F3 v1.1 / F5 v1.1 / D1 v1.2 / D2 v1.1 / D3 v1.2 / D4 v1.1 / D5 v1.3 / D6 v1.2 anchor decision defect | Phase 3a/3b ADR revision via council convening |
| ADD v1.3 attestation mismatch with CP spec v1.3 | Phase 3d ADD revision |
| CXA v2.1 §2.3.2 (CP→IS) / §2.3.3 (OD→CP) / §2.3.4 (CP→AS) edge defect | Phase 6 CXA revision-pass at design-phase workspace |
| CP export seam (U-CP-54 / U-CP-55 manifest) defect; consumer-side OD plan re-cite required | Phase 6 CP plan revision-pass; cascade to OD plan if seam-export shape changes |

### 5.2 Open carry-forwards at CP axis entry

| Carry-forward | Status | Routing |
|---|---|---|
| F2-12 cascade Step 6a (CP plan layer) | CLOSED at v2.2; preserved at v2.3 per `F2-12_Closure_Declaration.md` | No action |
| H_T-CP-1 Class 2 substitution-risk surface (multi-LLM commitment unmet at 7a runtime) | CLOSED with operator visibility per `Project_Workflow_v1_8.md` §2.7.7 + `Phase_6_5_Session_4_Close_Handoff.md` §5.2 | Non-blocking; substitution retirement at U-CP-01 landing |
| GUARDRAIL units (4 of 55; per `Plan_Executability_Audit_v1.md` §3.3) | Project-authored per framework-pull discipline | Phase 7 execution-time; non-blocking |

### 5.3 Filing footer

| Field | Value |
|---|---|
| Artifact | `harness-cp/CLAUDE.md` |
| Authored at | Phase 6.5 Session 6 (ε), 2026-05-15 |
| Authoring authority | `Phase_6_5_Session_6_Kickoff.md` §2.1.2 |
| Predecessor | Design-phase workspace CP spec v1.3 + CP plan v2.3 |
| Revision policy | This file is canonical for the `harness-cp/` subdirectory; revisions route to design-phase back-flow per §5.1 |

---

*End of `harness-cp/CLAUDE.md`. Parent guidance at workspace root `CLAUDE.md`. CP spec + plan + CXA v2.1 §2.3.2 / §2.3.3 / §2.3.4 at design-phase workspace. Sub-agent boundary application per CP-AL-1 at `Sub_Agent_Boundary_Specification_v1.md` (workspace root).*
