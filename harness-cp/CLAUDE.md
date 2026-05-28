# harness-cp/CLAUDE.md — Control Plane (CP) Axis

*Per-axis subdirectory guidance for the CP axis. Loaded by Claude Code at session startup alongside workspace root `CLAUDE.md`. Canonical pointer to design-phase CP-axis artifacts.*

---

## 1. Axis identity + scope boundary

### 1.1 Axis identity

The Control Plane (CP) axis owns **orchestration**: multi-LLM routing core + provider portability (ADR-F1 v1.2 anchor), per-layer time-budget + retry namespaces, fallback chain composition + cross-family fallback, workflow manifest schema + per-step override evaluator + audit-ledger composition, EngineClass + ResumptionKind taxonomies, TopologyPattern 6-class enum + admissibility + CascadePolicy, sub-agent handoff schemas, HITL placement + 4-response palette, sandbox-tier dispatch, Skills enabling discipline (CP-side), memory + files primitive consumption, MCP integration + per-server trust framework function, cross-deployment monotonicity.

CP posture per `Cross_Axis_Composition_Document_v2_15.md` §2.4: **largest cross-axis consumer** (63 outbound edges per §2.4 axis-attribution; 37 → IS + 19 → AS + 7 → OD CP-axis-attributed at §2.3.7 rows 1-7 per v2.6 composer-arc absorption namespace-ownership convention); consumer of 12 OD→CP inbound edges (excluded from outbound; CP terminal manifests U-CP-54 + U-CP-55 surface CP exports for OD consumption). CP→OD bucket-membership at §2.3.7 is **8 rows** at v2.9 (row 8 = cost-attribution audit-write seam, U-OD-41 producer, OD-axis-attributed per §2.4 namespace-ownership convention — not counted in CP outbound). CP→AS bucket-membership at §2.3.3 is **19 edges / 6 genuine** at v2.15 (row 6 = U-CP-68 → U-AS-03 ToolContract Pattern-P1 seam — CP-side consumer + AS-side producer + AS-axis-owned namespace all converge on CP outbound +1 per vanilla CP→AS attribution; no §2.1-vs-§2.4 divergence). Largest axis by unit count (58) and contract count (24). Counts updated v2.1 baseline → v2.4 per `[[class_3_tension_per_axis_claude_md_v2_1_to_v2_4_count_drift]]` absorption; v2.4 → v2.9 refresh per CXA v2.9 §0.8(e) absorbing v2.6 composer-arc 1→7 CP→OD seam growth + v2.9 row 8 cost-attribution audit-write seam landing; v2.9 → v2.15 refresh per CXA v2.15 §0.8(c)+(d) absorbing the U-CP-68 → U-AS-03 ToolContract CP→AS Pattern-P1 seam landed at U-CP-70 commit `2e417e0`.

### 1.2 Spec + plan authority

| Artifact | Version | Role |
|---|---|---|
| `Spec_Control_Plane_v1_3.md` | v1.3 | Contract authority — 24 contracts C-CP-01 through C-CP-24 |
| `Implementation_Plan_Control_Plane_v2_10.md` | v2.10 (7c-prerequisite status-reconciliation delta over v2.9; `RoleRoutingBinding` / `WorkloadRoutingOverride` Class 1 RESOLVED — operator-ratified R-2/W-2 schemas; U-CP-04 `RoutingManifest` upgraded PARTIAL-LAND → FULL-LAND. No signature, contract, or DAG change since v2.6) | Execution authority — 58 atomic units across 9 clusters and 9 topological levels (L0–L8) |

### 1.3 Scope inclusion — 9 clusters

Per `Implementation_Plan_Control_Plane_v1.md` §3.3 cluster table (preserved verbatim at v2.10 §3):

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

The 9-cluster table enumerates the 55 in-cluster units. CP plan v2.10 additionally carries 3 pre-cluster L0 foundational units — U-CP-00 (`WorkloadClass` carrier; landed), U-CP-00b (CP shared-type carrier: `AttributeValueType` / `Cardinality`; added at v2.6 per R4) and U-CP-00c (the 9 CP-owned structured shared types — `ActorIdentity` / `AgentRole` / `ModelBinding` / `TraceContext` / `ProviderAgnosticPayload` / `RoutingDecisionTrace` / `MCPTrustTier` / `Axis` / `TailKeepPredicate`; added at v2.8 as faithful FACTOR-OUTs per the operator-ratified T2 X-AL-3 resolution — concept spec/ADR-committed, only the declaration site was missing) — for 58 units total.

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

CP terminal aggregate exporters: U-CP-54 + U-CP-55 (per C-CP-24 §24). 12 OD→CP edges consume CP export surfaces. Per-edge enumeration at `Cross_Axis_Composition_Document_v2_9.md` §2.3.6.

### 2.3 Cross-axis edge inventory (CXA v2.9)

| Edge direction | Edges | Source artifact |
|---|---|---|
| CP → IS (outbound) | 37 | `Cross_Axis_Composition_Document_v2_9.md` §2.3.2; `Implementation_Plan_Control_Plane_v1.md` §3.3 |
| CP → AS (outbound) | 19 | `Cross_Axis_Composition_Document_v2_15.md` §2.3.3 (was 18 at v2.9; v2.15 adds row 6 U-CP-68 → U-AS-03 ToolContract Pattern-P1 seam; bucket renumbered at v2.3 reclassification from v2.1 §2.3.4); CP plan §3.3 |
| OD → CP (inbound) | 12 | `Cross_Axis_Composition_Document_v2_9.md` §2.3.6 (was v2.1 §2.3.3 — bucket renumbered at v2.3 reclassification) |
| CP → OD (bucket-membership) | 8 | `Cross_Axis_Composition_Document_v2_9.md` §2.3.7 — 8 genuine-typed-seams at the shared `cp_audit_to_od_audit` converter (homed at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` per Q5 ratification). Rows 1-7 CP-axis-attributed per §2.4 namespace-ownership convention (count toward CP outbound 62); row 8 (cost-attribution audit-write seam, U-OD-41 → U-OD-00 via `cost:` action_id prefix, NEW at v2.9 per `.harness/Remaining_Work_Closure_Arc_Handoff_v1.md` §6) is OD-axis-attributed (counts toward OD outbound 27). Per-bucket discriminator at OD audit-trace consumers is the 8-prefix action_id table per CXA v2.9 §0.3 (`dispatch:` / `hitl:` / `hitl_webhook:` / `operator_burden:` / `validator:` / `pause:` / `resume:` / `mcp_trust:` / `cost:` — the v2.6 7-row enumeration extended to 8 at v2.9). Bucket growth chronology: row 1 NEW v2.4 (U-CP-28 → U-OD-00 audit-ledger entry composition, first cross-axis back-edge per U-RT-59 Fork 2 Path D); rows 2-7 NEW v2.6 (composer-arc absorption: ValidatorFramework + PauseResumeProtocol + PerServerTrustEvaluator + HITL webhook delivery + HITL operator-burden + one prior); row 8 NEW v2.9 (cost-attribution audit-write seam). `[[class_3_tension_cxa_v2_4_axis_back_edge]]`. NOTE: U-CP-54 + U-CP-55 manifest is the OD→CP **inbound** terminal-aggregate-exporter surface (12 edges row above), not a CP→OD outbound. |

### 2.4 Per-cluster cross-axis edge profile (preserved at v2.10)

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

Per `Implementation_Plan_Control_Plane_v1.md` §3.2 topological levels (preserved verbatim at v2.10):

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

**13 cluster-bearing L0 units; in-degree 0 (or cross-axis-only deps).** Phase 7 sub-phase 7b CP-axis-stream execution begins from these entry-points. The 3 pre-cluster foundational carriers U-CP-00 + U-CP-00b + U-CP-00c are additional L0 source nodes (`Depends on: (none)`) outside this cluster-bearing enumeration — 16 L0 source nodes total. U-CP-00c is L0; its 15 direct Pattern-D consumer edges point consumer → U-CP-00c (no level inversion; DAG remains acyclic).

### 3.1 DAG topology (9 levels; 58 nodes incl. U-CP-00 + U-CP-00b + U-CP-00c L0 carriers; 124 within-axis edges)

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

DAG verified acyclic per CP plan §3.4 Kahn execution: 58 units consumed; remaining edge set ∅.

### 3.2 Coverage matrix verification

Per CP plan §4 (preserved at v2.10 with coverage deltas at U-CP-07 + U-CP-12; v2.10 §0.4 makes U-CP-46's C-CP-20 §20.6 coverage explicit — no mark gained or lost): 24 of 24 contracts covered by ≥1 unit; no coverage gaps. Coverage matrix per-axis-only per OD-S3-2.A.

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

**Retirement status (post 7d batch 18 H_T-CP-22 workflow-layer composer close, 2026-05-24).** Batch-18 advances H_T-CP-22 PARTIAL → RETIRED via the narrow-scope CP composer authoring arc (runtime spec v1.20 → v1.21 NEW §14.14 C-RT-24 `materialize_pause_resume_protocol_stage` factory + plan v2.19 → v2.20 NEW L9-undecies cluster + impl arc U-RT-87/88/89 + U-RT-89 e2e 6/6 pass through real `run_bootstrap`; FOURTH RETIRE-READY → RETIRED close in ledger history; CP-axis crosses 14/22 = 63.6% RETIRED; workspace 27/49 = 55.1%). Operator-opt-in RETIRE-READY pattern bucket transits 0 → 1 → 0 in this batch filing (joint two-step PARTIAL → RETIRE-READY → RETIRED single-batch transit; mirrors batch-17 CP-21 close-pattern shape).

**Retirement status (post 7d batch 21 H_T-CP-19 PARTIAL → RETIRE-READY transit, 2026-05-27).** Per `.harness/phase-7d-retirement-events-batch-{1..21}.md` cumulative (batch 20 number consumed by empty-survey filing per `[[batch-20-survey-empty-2026-05-27]]`) + `.harness/phase-7d-retirement-ledger-v2.md` (operator-ratified runtime-only substitution-site reading + line-33 strict-reading discipline). This block advances through batch-14 (H_T-CP-16 RETIRE-READY → RETIRED via U-RT-82 e2e against real Anthropic API at `03025cb` — FIRST RETIRE-READY → RETIRED close in ledger history; CP-axis crosses 50% RETIRED at 11/22), batch-15 (H_T-CP-21 RETIRE-READY → PARTIAL DOWN-classification at `f373c93` per Reading-D audit of fork doc `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` — FIRST DOWN-classification in ledger history), batch-16 (H_T-CP-18 + H_T-AS-2 joint RETIRE-READY → RETIRED via U-RT-86 e2e at `8e6311f` — SECOND RETIRE-READY → RETIRED close; FIRST JOINT close; workspace crosses 50% RETIRED at 25/49 = 51.0%; CP-axis crosses 12/22 = 54.5%), and batch-17 (H_T-CP-21 PARTIAL → RETIRED via validator-composer Reading A arc landing spec v1.18 §14.13 + plan v2.17 L9-decies cluster + U-RT-83/84/85 impl + U-RT-85 e2e at `37e9d67` against operator-supplied ValidatorFramework fixture — THIRD RETIRE-READY → RETIRED close + FIRST corrective close restoring the batch-15 DOWN-classification per Reading A resolution path; CP-axis crosses 13/22 = 59.1%; workspace 26/49 = 53.1%). Forward-only ledger discipline preserved — prior batch records stand verbatim per workspace `CLAUDE.md` §4.3.

| Status | Count | Substitutions |
|---|---|---|
| **RETIRED** | 14/22 (63.6%) | (12 prior RETIRED rows preserved verbatim per row-history at batch-17 close); H_T-CP-22 (PauseResumeProtocol + state_summary — batch 18 PARTIAL → RETIRED workflow-layer composer close via narrow-scope CP composer authoring arc landing runtime spec v1.21 §14.14 C-RT-24 + plan v2.20 L9-undecies + U-RT-87/88/89 impl + U-RT-89 e2e at `671f195` against bootstrapped `PauseResumeProtocol` instance through real `run_bootstrap`; criterion-A preserved (6 cited carriers U-CP-49/50/62/63/64/65 MET per Meta-Arch v1.5 §5.4 row) + structural-B newly MET via 3-stage binding chain (RuntimeConfig.pause_resume_protocol_config + HarnessContext.pause_resume_protocol + workflow_driver per-step pre-entry pause-trigger detection + entry-point resume detection) + operational-B newly MET via U-RT-89 e2e 6/6 PASS exercising capture + clean-resume + corruption paths through bootstrapped protocol async methods; FOURTH RETIRE-READY → RETIRED close in ledger history; workflow-layer audit-write residual CLOSED-as-WON'T-FIX per `.harness/class_1_fork_u_cp_72_cost_and_pause_resume_prefix_gap.md` §11 (2026-05-24; lossy projection PauseSnapshot→PauseEvent foreclosed by §26 NOTE disjoint-primitives declaration + no concrete consumer named; recovery path preserved at fork §11 if a consumer surfaces)) |
| **RETIRE-READY** | 1/22 (4.5%) | H_T-CP-19 (D5 cross-deployment monotonicity — batch 21 PARTIAL → RETIRE-READY via Class 1 fork Reading A apply pass landing CP spec v1.19 → v1.20 NEW §6.1.Y `WorkflowManifestEntry.default_gate_level: GateLevel \| None = None` field + CP plan v2.24 → v2.25 U-CP-13 absorption + harness-cp impl at `workflow_manifest_entry.py` + `workflow_driver.py:738` composition site read `manifest_entry.default_gate_level if not None else GateLevel.AUTO` + `workflow_driver_types.py:163-168` docstring lift at commit `f59945b`; criterion-A preserved (3 cited carriers U-CP-26/27/43 MET per Meta-Arch v1.5 §5.4 row) + structural-B newly MET via field declaration + plan-side absorption + operational-B layers 1+2 MET via 692/692 harness-cp + 1091/1091 harness-runtime tests pass through real bootstrap path; **operational-B Layer 3 (multi-deployment e2e fixture exercising cross-deployment monotonicity per D5 contract) explicitly deferred per Q3=defer-layer-3-e2e ratification** — gates RETIRE-READY → RETIRED close; SEVENTH historical member of operator-opt-in RETIRE-READY pattern + FIRST entry where the RETIRED close gate is operator-deferred at ratification time per sub-species 7.operator-explicit-deferred-close-gate catalogued at batch-21 §2) |
| **PARTIAL** | 5/22 (22.7%) | H_T-CP-8 (F2-substrate-join — `cp_is_wiring.py` 1 of 17 edges); H_T-CP-9 (ResumptionKind 5-class — driver emits binary only); H_T-CP-11 (D4 multiplicative tunable not surfaced at runtime); H_T-CP-14 (multi-agent span hierarchy + `subagent.*` + `topology.*` — batch 4 single-sub-agent slice; 8 fan-out-specific `topology.*` attrs deferred to parent-topology-expansion arc); H_T-CP-17 (files.* CP-side consumer — batch 11, U-AS-28+U-AS-31 landed at AS axis; Files arc deferred indefinitely per runtime spec v1.17 §14.C fork-doc ratified scope) |
| **STILL-BOUNDED** | 2/22 (9.1%) | H_T-CP-12 (sandbox-tier dispatch monotonic-descent invariant beyond permission-mode coarse default-downgrade); H_T-CP-23 (bridging-arc concept — manual operator orchestration during 7a) |

Totals: 14 RETIRED + 1 RETIRE-READY + 5 PARTIAL + 2 STILL-BOUNDED = 22 ✓.

**Pipeline advanced (RETIRED + RETIRE-READY + PARTIAL):** 20/22 = **90.9%** CP-axis advanced post-batch-21 (unchanged from post-batch-18; within-tier promotion CP-19 PARTIAL → RETIRE-READY this batch). Workspace-wide pipeline advanced: 35/49 = 71.4% (per batch-21 §0 cumulative table — unchanged from batch-13..19, within-tier promotion + DOWN compositions). **Workspace 28/49 = 57.1% RETIRED post-batch-21** (unchanged from batch-19; CP-19 transit is RETIRE-READY not RETIRED).

**Operator-opt-in RETIRE-READY pattern (post-batch-21: 1 active member CP-19; 6 of 7 historical members RETIRED).** Pattern members across batches 10–21: CP-18 (batch 10 RETIRE-READY → batch 16 RETIRED), CP-21 (batch 11 RETIRE-READY → batch 15 DOWN PARTIAL → batch 17 PARTIAL → RETIRED via Reading A corrective close), AS-2 (batch 12 RETIRE-READY → batch 16 RETIRED), CP-16 (batch 13 RETIRE-READY → batch 14 RETIRED), CP-22 (batch 18 PARTIAL → RETIRED workflow-layer composer close), AS-4 (batch 19 PARTIAL → RETIRED Reading B arc 2 close), **CP-19 (batch 21 PARTIAL → RETIRE-READY — NEW; close gate operator-deferred per Q3)**. Future PARTIAL → RETIRE-READY promotions under this pattern (for any of the 5 remaining CP-axis PARTIALs) must apply the batch-16 §6 verification-shape sharpening (first prospectively applied at batch-17 §4): **"grep-for-presence ≠ verified-working-end-to-end"** — all 3 binding-chain stages (carrier + bootstrap stage factory / consumer site + e2e exercise against real substrate, not merely "driver code references the bound field") must be empirically verified before promotion. Per CP-19 precedent set at batch-21, operator-discretion deferral of Stage 3 at ratification time is admissible when (i) the contract semantic requires a substrate that doesn't yet exist and (ii) Layer 1+2 close the immediate silent-absorption gap. See batch-16 §6 + batch-17 §4 + batch-21 §2 + `[[verification-shape-sharpened-grep-vs-e2e]]`.

**§9 Class 2 multi-LLM commitment surface CLOSED (U-RT-52 close arc, 2026-05-20).** All 3 providers (anthropic + openai + ollama) constructed at `harness-runtime/.../lifecycle/providers.py:679-706`; production LLM call site landed at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:RuntimeLLMDispatcher.dispatch` (per `Spec_Harness_Runtime_v1.md` v1.3 §14.5 C-RT-15). `step_dispatcher.dispatch(binding, step)` at `harness-cp/src/harness_cp/workflow_driver.py:379` now has a typed runtime composer satisfying the Protocol (the `RetryBreakerFallbackDispatcher` wrapper around `RuntimeLLMDispatcher` post-U-RT-58); ADR-F1 v1.2 multi-LLM commitment met at design + library code + runtime. Per v2 §9.2.3 closure criterion satisfied.

**§6.3.2 F-CP-01 Stage 3b inversion cascade FULLY DISCHARGED (U-RT-58 landing arc, 2026-05-20).** Both endpoints retired (H_T-OD-2 batch 2 + H_T-CP-24 authoring close v1 §1) + production `harness.breaker.*` emission site landed at `retry_breaker_fallback.py:_emit_breaker_transition` which delegates to `RuntimeRetryBreaker.emit_breaker_transition_event` per OD-canonical C-OD-07 §7.1 7-attribute schema. **H_T-CXA-5 RETIRED** at batch 3 (the inversion seam is operational end-to-end).

**PARTIAL → RETIRE-READY gates (the 7 PARTIALs):** all gate on workflow_driver / sub_agent_dispatch composer invocation of carrier primitives that already landed at library layer. Specifically: CP-8 on CP-IS-wiring 17-edge completion (`[[fork-cp-is-wiring-gaps]]`); CP-9 on driver emission of 5-class ResumptionKind beyond binary; CP-11 on workload commitment table runtime exposure; CP-14 on parent-topology-expansion arc; CP-17 on Files-arc design-phase opening (currently deferred indefinitely per runtime spec v1.17 §14.C); CP-19 on multi-deployment runtime scenario; CP-22 on workflow_driver pause-event handler invoking PauseResumeProtocol.capture_pause_snapshot/attempt_resume. Each is bounded by a specific finite gap, not by a missing major composer. Operator-discretion timing per existing 7d retirement-event cadence.

**Cross-axis cite chain U-OD-51 ↔ U-CP-62 ↔ U-CP-72 (batch-11 §9(e) observation):** U-CP-62 landed at cluster 10-CP-B (`49617e7`) unblocks U-OD-51 PauseResumeAuditPayload re-eligibility at follow-on OD plan revision-pass arc; downstream U-CP-72 cp_audit_to_od_audit converter `pause:` + `resume:` branches can subsequently un-STRIKE (3-arc cascade — OD plan → U-OD-51 landing → U-CP-72 amendment). H_T-CP-22 PARTIAL → RETIRE-READY does NOT require this cascade (CP-axis criterion is workflow_driver invocation; OD-side audit-write is downstream observability).

**U-RT-59 sibling-fork status (post batch 5, 2026-05-20):**
- `[[class_1_tension_u_rt_59_async_sync_step_dispatcher]]` — **RESOLVED** at Path B wiring landing `d64d8cf` (INFERENCE_STEP bound via `SyncDispatcherFacade(ctx.llm_dispatcher)` at stage 5; spec text unchanged at v1.6 §14.7.7; facade documentation owed to Class 3 drift item 6). End-to-end LLM-dispatch execution path re-affirmed at strict X-AL-2 reading for CP-1/CP-3/CP-4/CP-5 per `.harness/phase-7d-retirement-events-batch-5.md`.
- `[[class_1_tension_u_rt_59_topology_admissibility_predicate]]` — **RESOLVED** at Path A landing `e52c2da` (strict gate restored via `is_topology_permitted(topology, workload)` union predicate — C-CP-11 §11.1 primary topologies ∪ C-CP-10 §10.3 cross-pattern admissibility, membership in workload's `permitted_patterns`; composer step 4 raises `SubAgentDispatchTopologyInadmissibleError` before `subagent.span` opens; spec §14.7.2 step 4 predicate-name correction owed to Class 3 drift item 8). Batch 5 §2 advisory-gate carry-forward pointer-closed.
- `[[class_1_tension_u_rt_59_cp_to_od_audit_write_gap]]` — OPEN (AC #9 write half STRUCK; CP→OD audit-write composition owed to Phase 6 CP-composer-authoring arc; joins `[[fork-cp-is-wiring-gaps]]` family). **Last of three U-RT-59 sibling Class 1 forks remaining OPEN.**

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
| CP plan v2.10 atomic unit signature defect | Phase 6 plan revision-pass at design-phase workspace |
| CP spec v1.3 contract defect (C-CP-NN under-specifies the surface; spec inconsistent with ADR) | Phase 5 spec revision-pass at design-phase workspace |
| ADR-F1 v1.2 / F2 v1.2 / F3 v1.1 / F5 v1.1 / D1 v1.2 / D2 v1.2 / D3 v1.2 / D4 v1.1 / D5 v1.3 / D6 v1.2 anchor decision defect | Phase 3a/3b ADR revision via council convening |
| ADD v1.3 attestation mismatch with CP spec v1.3 | Phase 3d ADD revision |
| CXA v2.1 §2.3.2 (CP→IS) / §2.3.3 (OD→CP) / §2.3.4 (CP→AS) edge defect | Phase 6 CXA revision-pass at design-phase workspace |
| CP export seam (U-CP-54 / U-CP-55 manifest) defect; consumer-side OD plan re-cite required | Phase 6 CP plan revision-pass; cascade to OD plan if seam-export shape changes |

### 5.2 Open carry-forwards at CP axis entry

| Carry-forward | Status | Routing |
|---|---|---|
| F2-12 cascade Step 6a (CP plan layer) | CLOSED at v2.2; preserved through v2.10 per `F2-12_Closure_Declaration.md` | No action |
| H_T-CP-1 Class 2 substitution-risk surface (multi-LLM commitment unmet at 7a runtime) | RETIRED at U-RT-52 close arc, 2026-05-20 — runtime LLM call site landed at `lifecycle/llm_dispatch.py` per Spec v1.3 §14.5 C-RT-15. Was: CLOSED-with-visibility | Closed |
| GUARDRAIL units (4 of 55; per `Plan_Executability_Audit_v1.md` §3.3) | Project-authored per framework-pull discipline | Phase 7 execution-time; non-blocking |

### 5.3 Filing footer

| Field | Value |
|---|---|
| Artifact | `harness-cp/CLAUDE.md` |
| Authored at | Phase 6.5 Session 6 (ε), 2026-05-15 |
| Authoring authority | `Phase_6_5_Session_6_Kickoff.md` §2.1.2 |
| Predecessor | Design-phase workspace CP spec v1.3 + CP plan v2.6 |
| Reconciled at | Phase 7 sub-phase 7c carry-forward pass, 2026-05-17 — CP plan pointer v2.6 → v2.10 (58 units; U-CP-00c L0 carrier added; `RoleRoutingBinding` Class 1 RESOLVED). Per `.harness/cxa_7c_prerequisites_report.md` known-carry |
| Revision policy | This file is canonical for the `harness-cp/` subdirectory; revisions route to design-phase back-flow per §5.1 |

---

*End of `harness-cp/CLAUDE.md`. Parent guidance at workspace root `CLAUDE.md`. CP spec + plan + CXA v2.1 §2.3.2 / §2.3.3 / §2.3.4 at design-phase workspace. Sub-agent boundary application per CP-AL-1 at `Sub_Agent_Boundary_Specification_v1.md` (workspace root).*
