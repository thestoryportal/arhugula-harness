# harness-cp/CLAUDE.md — Control Plane (CP) Axis

*Per-axis subdirectory guidance for the CP axis. Loaded by Claude Code at session startup alongside workspace root `CLAUDE.md`. Canonical pointer to design-phase CP-axis artifacts.*

---

## 1. Axis identity + scope boundary

### 1.1 Axis identity

The Control Plane (CP) axis owns **orchestration**: multi-LLM routing core + provider portability (ADR-F1 v1.2 anchor), per-layer time-budget + retry namespaces, fallback chain composition + cross-family fallback, workflow manifest schema + per-step override evaluator + audit-ledger composition, EngineClass + ResumptionKind taxonomies, TopologyPattern 6-class enum + admissibility + CascadePolicy, sub-agent handoff schemas, HITL placement + 4-response palette, sandbox-tier dispatch, Skills enabling discipline (CP-side), memory + files primitive consumption, MCP integration + per-server trust framework function, cross-deployment monotonicity.

CP posture per `Cross_Axis_Composition_Document_v2_19.md` §2.4: **largest cross-axis consumer** (69 outbound edges per §2.4 axis-attribution; 43 → IS + 19 → AS + 7 → OD CP-axis-attributed at §2.3.7 rows 1-7 per v2.6 composer-arc absorption namespace-ownership convention); consumer of 12 OD→CP inbound edges (excluded from outbound; CP terminal manifests U-CP-54 + U-CP-55 surface CP exports for OD consumption). CP→OD bucket-membership at §2.3.7 is **8 rows** at v2.9 (row 8 = cost-attribution audit-write seam, U-OD-41 producer, OD-axis-attributed per §2.4 namespace-ownership convention — not counted in CP outbound). CP→AS bucket-membership at §2.3.3 is **19 edges / 6 genuine** at v2.15 (row 6 = U-CP-68 → U-AS-03 ToolContract Pattern-P1 seam — CP-side consumer + AS-side producer + AS-axis-owned namespace all converge on CP outbound +1 per vanilla CP→AS attribution; no §2.1-vs-§2.4 divergence). CP→IS bucket-membership at §2.3.2 grew **37→43 canonical / 9→15 genuine at v2.17 2026-05-31** (6 NEW Pattern-P1 typed seams absorbing U-CP-74..U-CP-79 §16.5 CP→IS composer atomic-unit LANDED events at PRs #39-#44; rows 38-43 each consumer `harness_cp.<composer_module>` imports `EntryPayload` from `harness_is.state_ledger_write` per CP spec v1.25 §16.5.3 contract). Largest axis by unit count (58) and contract count (24). Counts updated v2.1 baseline → v2.4 per `[[class_3_tension_per_axis_claude_md_v2_1_to_v2_4_count_drift]]` absorption; v2.4 → v2.9 refresh per CXA v2.9 §0.8(e) absorbing v2.6 composer-arc 1→7 CP→OD seam growth + v2.9 row 8 cost-attribution audit-write seam landing; v2.9 → v2.15 refresh per CXA v2.15 §0.8(c)+(d) absorbing the U-CP-68 → U-AS-03 ToolContract CP→AS Pattern-P1 seam landed at U-CP-70 commit `2e417e0`; v2.15 → v2.17 refresh absorbing the 6-row CP→IS Pattern-P1 absorption from v2.16 §0.4 forward-tracking marker closure at PR #92 commit `28259ed` 2026-05-31.

### 1.2 Spec + plan authority

| Artifact | Version | Role |
|---|---|---|
| `Spec_Control_Plane_v1_33.md` | **v1.33 — canonical HEAD** (delta-only chain; this row's prior `v1.3` was the Phase-6.5 authoring-era pin, pre-dating the Phase-7 v1.4→v1.33 deltas — latest delta = the **C-CP-07 §7.4 reconciler-loop substrate-deferral reconciliation** (R-FS-1 E-spec-3): adds `reconciler-loop` to the §7.4 impl-discretion clause (hand-rolled etcd-style per I-6, reconciling §7.1's named "K8s controller / etcd" *reference* substrate with the no-vendored-K8s invariant; operator-ratified 2026-06-15); §7.1/§7.2/§7.4-floor-table + all other sections PRESERVED VERBATIM. Prior delta v1.32 = NEW §25.10–§25.18, an **in-place additive extension of C-CP-25 WorkflowDriver** materializing the 5 non-`SINGLE_THREADED_LINEAR` topology patterns (R-FS-1 arc #3 / B1-spec-1): driver-strategy dispatch + per-pattern contracts + buffered/deterministic-append path (D1.b; ADR-F2 single-threaded-write boundary, ZERO six-field/hash-chain change) + Route-Y branch-metadata sidecar seam (forward-ref to coordinated B1-spec-1b IS amendment) + B1↔B4 role seam (D2) + cascade_policy/cascade-cancel reach (D3 Fork A, council-resolved) + branch-scoped idempotency keys. §25.10+ additive; §1/§16.5.x/§25.1–§25.9/§26–§29 PRESERVED VERBATIM. Prior delta v1.31 = NEW §29 / C-CP-29 `PromptSelectionManifest`. Per delta-only convention each version is canonical-at-authoring for its scope; the chain head is the current contract authority. **Identity-label corrected at v1.32:** the v1.29–31 change-note tables mislabeled §25/C-CP-25 (it is WorkflowDriver, not ValidatorFramework) and §28/C-CP-28 (it is ValidatorFramework) per the v1.13 Reading A collision-resolution) | Contract authority — 29 contracts C-CP-01 through C-CP-29 *(authoring-era count was 24; deltas grew the enumeration — per v1.13 Reading A: C-CP-25 WorkflowDriver / C-CP-26 PauseResumeProtocol / C-CP-27 PerServerTrust / C-CP-28 ValidatorFramework (incl. §28.x v1.24 validator post-evaluate hook) / C-CP-29 PromptSelectionManifest — see the canonical spec)* |
| `Implementation_Plan_Control_Plane_v2_31.md` | **v2.31 — canonical HEAD** (delta over v2.30; this row's prior `v2.10` was the authoring-era pin) | Execution authority — 58 atomic units across 9 clusters and 9 topological levels (L0–L8) *(authoring-era figures; see the canonical plan)* |

### 1.3 Scope inclusion — 9 clusters

Per the canonical CP plan 9-cluster table (head `Implementation_Plan_Control_Plane_v2_31.md`; the `_v1.md` §3.3 origin was superseded by the delta-only v2.x chain — cluster structure summarized inline below):

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

CP terminal aggregate exporters: U-CP-54 + U-CP-55 (per C-CP-24 §24). 12 OD→CP edges consume CP export surfaces. Per-edge enumeration at `Cross_Axis_Composition_Document_v2_19.md` §2.3.6.

### 2.3 Cross-axis edge inventory (CXA v2.19 canonical reading)

*The `§2.3.x` cites below name the **v2.19 canonical reading**; the per-bucket row tables are preserved verbatim from the last full re-table at **v2.3** (§2.3.2 CP→IS last amended at v2.17), not byte-tabled in the v2.19 delta — per the delta-only chain (root `CLAUDE.md` §2 delta-baseline §-cite convention). v2.19 itself only restated §2.1 (aggregate matrix) + §2.4 (per-axis attribution).*

| Edge direction | Edges | Source artifact |
|---|---|---|
| CP → IS (outbound) | 43 | `Cross_Axis_Composition_Document_v2_19.md` §2.3.2 (was 37 at v2.9-v2.16; v2.17 absorbs 6 NEW Pattern-P1 typed seams at rows 38-43 for U-CP-74..U-CP-79 §16.5 composer atomic-unit LANDED events at PRs #39-#44 2026-05-28..29 per CP spec v1.25 §16.5.3 contract); CP plan head `Implementation_Plan_Control_Plane_v2_31.md` (the `_v1.md` §3.3 origin was superseded by the delta-only v2.x chain) |
| CP → AS (outbound) | 19 | `Cross_Axis_Composition_Document_v2_15.md` §2.3.3 (was 18 at v2.9; v2.15 adds row 6 U-CP-68 → U-AS-03 ToolContract Pattern-P1 seam; bucket renumbered at v2.3 reclassification from v2.1 §2.3.4); CP plan §3.3 |
| OD → CP (inbound) | 12 | `Cross_Axis_Composition_Document_v2_19.md` §2.3.6 (was v2.1 §2.3.3 — bucket renumbered at v2.3 reclassification) |
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

Per the canonical CP plan topological levels (head `Implementation_Plan_Control_Plane_v2_31.md`; the `_v1.md` §3.2 origin was superseded by the delta-only v2.x chain — levels summarized inline below):

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

> **🎓 PHASE-8 GRADUATION SUPERSESSION (2026-06-02).** Phase 8 substitution accounting is **CLOSED** per `.harness/phase-8-graduation.md`. **Canonical workspace cumulative: 46/54 RETIRED (85.2%); 49/54 pipeline-advanced (90.7%)** (operator-ratified accounting (i), PR #246). This supersedes forward all prior batch-cumulative workspace figures in this file (e.g. the batch-48 `45/54` + batch-30 `34/54` lines below); per-batch records + CP-axis-local figures (21/22 = 95.5%) stand verbatim per workspace `CLAUDE.md` §4.3 forward-only discipline. CP-axis dispositions in the graduation: CP-1..14/18/19/20/21/22 + CP-3/4/5/6/8/9/10/11/13 RETIRED-substantive; CP-12/CP-23 RETIRED-AS-AUTHORING-ONLY; CP-16 RETIRED-AS-BOUNDED-RESIDUAL; **CP-17 accepted-indefinite-defer** (Files-arc, batch-44; NOT counted in the 46; R-010). **Canonical source (R-600): these dispositions + counts are DERIVED from `.harness/substitutions.yaml` via `tools/substitution_ledger.py`; cite the derivation, don't hand-maintain.**

**Retirement status (post 7d batch 18 H_T-CP-22 workflow-layer composer close, 2026-05-24).** Batch-18 advances H_T-CP-22 PARTIAL → RETIRED via the narrow-scope CP composer authoring arc (runtime spec v1.20 → v1.21 NEW §14.14 C-RT-24 `materialize_pause_resume_protocol_stage` factory + plan v2.19 → v2.20 NEW L9-undecies cluster + impl arc U-RT-87/88/89 + U-RT-89 e2e 6/6 pass through real `run_bootstrap`; FOURTH RETIRE-READY → RETIRED close in ledger history; CP-axis crosses 14/22 = 63.6% RETIRED; workspace 27/49 = 55.1%). Operator-opt-in RETIRE-READY pattern bucket transits 0 → 1 → 0 in this batch filing (joint two-step PARTIAL → RETIRE-READY → RETIRED single-batch transit; mirrors batch-17 CP-21 close-pattern shape).

**Retirement status (post 7d batch 30 H_T-CP-11 PARTIAL → RETIRED via operator-discretion ratification of v1.6 MVP cascade_policy carve-out per runtime spec v1.6 §14.7.2 step 5, 2026-05-28; sibling-arc to CP-14 batch-29 same-session close).** This block advances through batch-30 (`phase-7d-retirement-events-batch-30.md`) + batch-29 (`phase-7d-retirement-events-batch-29.md`): H_T-CP-14 PARTIAL → RETIRE-READY → RETIRED joint single-batch transit via operator-discretion retirement-audit ratification at runtime spec v1.6 §14.7.2 step 5 explicit path. v1.6 MVP narrow subset (`topology.pattern` + `topology.workload_class` at open + 7 `subagent.*` attrs full) emitted at production `sub_agent_dispatch.py:613` per runtime spec v1.6 §14.7.2 step 5 — IN COMPLIANCE; 8 fan-out-specific `topology.*` attrs deferred to v1.7+ parent-topology-expansion arc (Phase 6 substrate). SIXTH RETIRE-READY → RETIRED close in ledger history; SECOND same-session joint single-batch transit (first was CP-19 at batch-22); SECOND closure of sub-species 7.operator-explicit-deferred-close-gate; ZERO production code change; ZERO cross-axis cascade. **CP-axis crosses 16/22 = 72.7% RETIRED; workspace 34/54 = 63.0% RETIRED**. v1.6 MVP single-sub-agent slice ratified as bounded-scope close per the spec-explicit ratification path. — **Retirement status (post 7d batch 22 H_T-CP-19 RETIRE-READY → RETIRED close via Layer 3 e2e reframed scope, 2026-05-27).** Per `.harness/phase-7d-retirement-events-batch-{1..22}.md` cumulative (batch 20 number consumed by empty-survey filing per `[[batch-20-survey-empty-2026-05-27]]`) + `.harness/phase-7d-retirement-ledger-v2.md` (operator-ratified runtime-only substitution-site reading + line-33 strict-reading discipline). This block advances through batch-14 (H_T-CP-16 RETIRE-READY → RETIRED via U-RT-82 e2e against real Anthropic API at `03025cb` — FIRST RETIRE-READY → RETIRED close in ledger history; CP-axis crosses 50% RETIRED at 11/22), batch-15 (H_T-CP-21 RETIRE-READY → PARTIAL DOWN-classification at `f373c93` per Reading-D audit of fork doc `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` — FIRST DOWN-classification in ledger history), batch-16 (H_T-CP-18 + H_T-AS-2 joint RETIRE-READY → RETIRED via U-RT-86 e2e at `8e6311f` — SECOND RETIRE-READY → RETIRED close; FIRST JOINT close; workspace crosses 50% RETIRED at 25/49 = 51.0%; CP-axis crosses 12/22 = 54.5%), and batch-17 (H_T-CP-21 PARTIAL → RETIRED via validator-composer Reading A arc landing spec v1.18 §14.13 + plan v2.17 L9-decies cluster + U-RT-83/84/85 impl + U-RT-85 e2e at `37e9d67` against operator-supplied ValidatorFramework fixture — THIRD RETIRE-READY → RETIRED close + FIRST corrective close restoring the batch-15 DOWN-classification per Reading A resolution path; CP-axis crosses 13/22 = 59.1%; workspace 26/49 = 53.1%). Forward-only ledger discipline preserved — prior batch records stand verbatim per workspace `CLAUDE.md` §4.3.

| Status | Count | Substitutions |
|---|---|---|
| **RETIRED** | 21/22 (95.5%) | (20 prior RETIRED rows preserved verbatim per row-history at batch-47 close); **H_T-CP-9 (ResumptionKind 5-class taxonomy + engine.* namespace — batch 48 PARTIAL → RETIRED via sub-species 7a `operator-explicit-deferred-close-gate` at CP spec v1.6 §25.5 line 375 `workflow.resumption` CONDITIONAL row v1.4 scope carve-out preserved verbatim through CP spec v1.27 per delta-only-spec-file convention; 4th sub-species 7a closure joining CP-19 batch-22 + CP-14 batch-29 + CP-11 batch-30; FIRST sub-species 7a closure anchored at CP spec authority surface; production at `workflow_driver.py:725-746` emits binary RESUMPTION on `save-point-checkpoint` engine class IN COMPLIANCE with §25.5 v1.4 carve-out + inline comment explicitly cites §8.1/§8.3 5-class contract preservation; ZERO production code change; ZERO design-substrate edit; ZERO cross-axis cascade)**; (prior batch-47 close) **H_T-CP-8 (F2-substrate-join contract — batch 47 PARTIAL → RETIRED via direct X-AL-2 first-conjunct satisfaction under "✗ absent (no H_E surface)" Meta-Architecture §5 classification; Gap A composer library COMPLETE at PRs #39–#44 + Gap B (S) sibling-variant APPLIED at CP spec v1.26 + Gap C deferred Class 3 informational; FIRST sub-species 7e instance — `composer-library-complete-with-no-H_E-surface-classification` catalogued at `phase-7d-retirement-events-batch-47.md` §2; ZERO production code change; ZERO design-substrate edit; ZERO cross-axis cascade beyond paired fork doc closure-back-reference)**; (prior batch-41 close) **H_T-CP-23 (bridging-arc traversal composition; F1 + D1 + D4 three-layer composition per C-CP-23 §23 — batch 41 STILL-BOUNDED → RETIRED-AS-AUTHORING-ONLY via sub-species 10 categorical-mismatch retirement criterion shape; ZERO production code change; ZERO spec amendment; ZERO cross-axis cascade)**. CP-23 close anchors: substrate IS C-CP-23 §23 contract realization at U-CP-53 `t_perm_3_composition.py` (F1+D1+D4 layer states; TPerm3LayerComposition; PerCellTPerm3Reading; PER_CELL_T_PERM_3_READINGS 20-cell table; compose_t_perm_3 / read_per_cell_t_perm_3 / handle_runtime_fault composer surfaces); sibling-field consumers at `per_engine_class_topology_overlay.py:63` (5 engine-class overlay rows declare `t_perm_3_reading`) + `workload_engine_class_matrix.py:52+89` (U-CP-24 2D matrix instantiates `t_perm_3_reading=overlay_for(ec).t_perm_3_reading`); composer surfaces ZERO production callers per Meta-Arch §5.4 H_E classification "✗ absent (no H_E surface)" + substitution mechanism "manual operator orchestration during 7a" (categorical-mismatch vacuous X-AL-2 second conjunct). Pre-batch-41 CLAUDE.md gate-text framing "substantive runtime composer landing invoking U-CP-53" structurally STALE-vs-spec — C-CP-23 §23 is a compose-time + reference-table + dispatch surface, NOT a runtime composer mandate at v1.6 MVP single-deployment scope. NINTH RETIRE-READY/STILL-BOUNDED → RETIRED close in ledger history; FIFTH sub-species 10 categorical-mismatch closure (after OD-1 batch-37 + OD-7 batch-38 + IS-4 batch-39 + CP-12 batch-40); same calendar day as batches 37-40. NEW species candidate at workflow v1.12 §7.4.7.2 catalogued at batch-41 §3 (f) — `categorical-mismatch-at-retirement-ledger-v2-authoring` (ledger-authoring-time framing-drift causal pattern; sub-species 10 is the doc-hygiene closure event-class) — DEFERRED pending cardinality build-up |
| **RETIRE-READY** | 0/22 (0.0%) | (empty — preserved verbatim from batch-30 close) |
| **PARTIAL** | 0/22 (0.0%) | (**PARTIAL bucket EMPTY at CP-axis for FIRST TIME in ledger history at batch-48 close**; CP-9 transited PARTIAL → RETIRED at batch-48 via sub-species 7a 4th closure — see RETIRED row above; CP-8 transited PARTIAL → RETIRED at batch-47 via sub-species 7e 1st closure; CP-17 reclassified STILL-BOUNDED-INDEFINITELY at batch-44 via sub-species 7g `indefinite-defer-tier-reclassification` per runtime spec v1.17 §14.C Files arc ratified scope) |
| **STILL-BOUNDED** | 0/22 (0.0%) | (empty post-batch-41 — CP-23 was sole STILL-BOUNDED member, transit RETIRED via sub-species 10 categorical-mismatch) |

Totals: 21 RETIRED + 0 RETIRE-READY + 0 PARTIAL + 0 STILL-BOUNDED = 21 ✓ at active substitution view (CP-17 SB-INDEF excluded; +1 SB-INDEF row brings total to 22 ✓; post-batch-48; prior batch-47 close 20 + 0 + 2 + 0 = 22 ✓ + prior batch-41 close 19 + 0 + 3 + 0 = 22 ✓ both preserved verbatim per forward-only ledger discipline).

**Pipeline advanced (RETIRED + RETIRE-READY + PARTIAL):** 22/22 = **100.0%** CP-axis advanced post-batch-48 (preserved at axis-closure ceiling since batch-41; CP-9 transit at batch-48 is within-pipeline-advanced PARTIAL → RETIRED). CP-axis crosses **95.5% RETIRED at batch-48** (+4.5 pp from 90.9% post-batch-47; CP-axis enters **single-axis-clean state at active substitution view** — PARTIAL bucket EMPTY for FIRST TIME in ledger history; joins AS-axis + CXA-axis at single-axis-clean state). CP-axis STILL-BOUNDED + RETIRE-READY + PARTIAL buckets ALL EMPTY at active substitution view (CP-17 SB-INDEF preserved from batch-44 sub-species 7g reclassification). Workspace-wide pipeline advanced **48/54 = 88.9%** (preserved — CP-9 transits within pipeline-advanced bucket from PARTIAL to RETIRED; both rows count toward pipeline-advanced denominator). **Workspace 45/54 = 83.3% RETIRED post-batch-48** (+1.9 pp from 44/54 = 81.5% at batch-47). **Cardinality check at batch-48 close: 45 + 0 + 3 + 0 + 3 (SB-INDEF: AS-8f + CP-17 + CXA-5/sup) = 51 active + 3 indef = 54 ✓** (batch-47 close 44 + 0 + 4 + 0 + 3 = 51 active + 3 indef = 54 ✓ preserved verbatim per forward-only ledger discipline). Cumulative-counts line refresh per workflow v1.12 §7.4.7.3.C retirement-tier-transit audit-template — published at batch-41 + batch-41-successor + batch-47 + batch-48 this session per ledger-tier-transit audit cadence.

**Operator-opt-in RETIRE-READY pattern (post-batch-30: bucket EMPTY at CP-axis; 9 historical members across workspace, 8 RETIRED at CP-axis + AS-8d/OD-5 RETIRE-READY at AS/OD axes pending deployment-time opt-in).** Pattern members across batches 10–30 add CP-11 (batch-30 PARTIAL → RETIRE-READY → RETIRED joint single-batch transit; THIRD closure of sub-species 7 catalogue via spec-explicit operator-discretion ratification path at runtime spec v1.6 §14.7.2 step 5 — SAME v1.6 MVP scope carve-out that closed CP-14 at batch-29; CP-11's `cascade_policy` and CP-14's fan-out attrs are sibling-deferred at the same §14.7.2 step 5 8-attr statement). Sub-species 7 catalogue now has 3 closure events sharing common-ancestor *retirement-audit ratification at spec-explicit operator-discretion path* (CP-19 batch-22 via Layer 3 in-process reframe; CP-14 batch-29 via v1.6 MVP single-sub-agent slice bounded scope; CP-11 batch-30 via v1.6 MVP cascade_policy carve-out sibling close) — distinct from sub-species 7.deployment-time-opt-in-gate (AS-8d + OD-5). Framing A reinforced empirically at CP-11 (THIRD instance, SECOND never-exercised lineage in 24 hours). Prior pattern members across batches 10–22: CP-18 (batch 10 RETIRE-READY → batch 16 RETIRED), CP-21 (batch 11 RETIRE-READY → batch 15 DOWN PARTIAL → batch 17 PARTIAL → RETIRED via Reading A corrective close), AS-2 (batch 12 RETIRE-READY → batch 16 RETIRED), CP-16 (batch 13 RETIRE-READY → batch 14 RETIRED), CP-22 (batch 18 PARTIAL → RETIRED workflow-layer composer close), AS-4 (batch 19 PARTIAL → RETIRED Reading B arc 2 close), **CP-19 (batch 21 PARTIAL → RETIRE-READY → batch 22 RETIRED via Layer 3 e2e reframed in-process scope; fastest bucket transit 1 → 0 within day; first sub-species 7.operator-explicit-deferred-close-gate same-session close)**. Future PARTIAL → RETIRE-READY promotions under this pattern (for any of the 5 remaining CP-axis PARTIALs) must apply the batch-16 §6 verification-shape sharpening (first prospectively applied at batch-17 §4): **"grep-for-presence ≠ verified-working-end-to-end"** — all 3 binding-chain stages (carrier + bootstrap stage factory / consumer site + e2e exercise against real substrate, not merely "driver code references the bound field") must be empirically verified before promotion. Per CP-19 precedent set at batch-21, operator-discretion deferral of Stage 3 at ratification time is admissible when (i) the contract semantic requires a substrate that doesn't yet exist and (ii) Layer 1+2 close the immediate silent-absorption gap. See batch-16 §6 + batch-17 §4 + batch-21 §2 + `[[verification-shape-sharpened-grep-vs-e2e]]`.

**§9 Class 2 multi-LLM commitment surface CLOSED (U-RT-52 close arc, 2026-05-20).** All 3 providers (anthropic + openai + ollama) constructed at `harness-runtime/.../lifecycle/providers.py:679-706`; production LLM call site landed at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:RuntimeLLMDispatcher.dispatch` (per `Spec_Harness_Runtime_v1.md` v1.3 §14.5 C-RT-15). `step_dispatcher.dispatch(binding, step)` at `harness-cp/src/harness_cp/workflow_driver.py:379` now has a typed runtime composer satisfying the Protocol (the `RetryBreakerFallbackDispatcher` wrapper around `RuntimeLLMDispatcher` post-U-RT-58); ADR-F1 v1.2 multi-LLM commitment met at design + library code + runtime. Per v2 §9.2.3 closure criterion satisfied.

**§6.3.2 F-CP-01 Stage 3b inversion cascade FULLY DISCHARGED (U-RT-58 landing arc, 2026-05-20).** Both endpoints retired (H_T-OD-2 batch 2 + H_T-CP-24 authoring close v1 §1) + production `harness.breaker.*` emission site landed at `retry_breaker_fallback.py:_emit_breaker_transition` which delegates to `RuntimeRetryBreaker.emit_breaker_transition_event` per OD-canonical C-OD-07 §7.1 7-attribute schema. **H_T-CXA-5 RETIRED** at batch 3 (the inversion seam is operational end-to-end).

**PARTIAL → RETIRE-READY gates (post-batch-48: 0 active PARTIALs remain at CP-axis; PARTIAL bucket EMPTY for FIRST TIME in ledger history).** CP-9 transited PARTIAL → RETIRED at batch-48 via sub-species 7a 4th closure (v1.4 scope carve-out at CP spec §25.5 line 375 — FIRST sub-species 7a closure anchored at CP spec authority surface; CP-11/CP-14 anchored at runtime spec §14.7.2 step 5; CP-19 at Layer 3 in-process reframe). CP-8 transited PARTIAL → RETIRED at batch-47 via direct X-AL-2 first-conjunct satisfaction (sub-species 7e); fork `[[fork-cp-is-wiring-gaps]]` closes at paired transit (RT-35 batch-46 + CP-8 batch-47). CP-17 reclassified STILL-BOUNDED-INDEFINITELY at batch-44 via sub-species 7g `indefinite-defer-tier-reclassification` per runtime spec v1.17 §14.C Files arc ratified scope. CP-11 (D4 multiplicative tunable / cascade_policy carve-out) + CP-14 (parent-topology-expansion) both transited to RETIRED via sub-species 7 operator-discretion ratification at batches 30 + 29 respectively — sharing the SAME runtime spec v1.6 §14.7.2 step 5 v1.6 MVP scope carve-out. Each remaining PARTIAL is bounded by a specific finite gap, not by a missing major composer. Operator-discretion timing per existing 7d retirement-event cadence.

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
