# harness-as/CLAUDE.md — Action Surface (AS) Axis

*Per-axis subdirectory guidance for the AS axis. Loaded by Claude Code at session startup alongside workspace root `CLAUDE.md`. Canonical pointer to design-phase AS-axis artifacts.*

---

## 1. Axis identity + scope boundary

### 1.1 Axis identity

The Action Surface (AS) axis owns **capability**: SandboxTier enum + tier-monotonicity ordering, tool contract schemas (I/O types + namespacing + strict-mode + description-as-prompt), tool gate policy (3-valued GateLevel), sandbox observability namespace (`sandbox.*` 7-attribute), sandbox-event idempotency-key composition, SkillFrontmatter schema + Skills loading discipline, Skills filesystem residence + reachability, Anthropic + MCP primitive observability (15-namespace exports), and AS substrate seam exports manifest.

AS posture per `Cross_Axis_Composition_Document_v2_16.md` §2.4 per-axis attribution: producer of **11 outbound edges (all to IS); 7 genuine** (CXA-canonical at v2.6 → v2.16; AS does not declare outbound edges to CP or OD); consumer of 0 cross-axis edges from CP / OD at axis-attribution layer (CP and OD pull from AS via U-AS-33 substrate seam exports manifest — **19 CP→AS canonical / 6 genuine** + **10 OD→AS** = **29 inbound edges** at v2.16; CP→AS bucket grew 18→19 at v2.15 row 6 U-CP-68 → U-AS-03 ToolContract Pattern-P1 seam landed at U-CP-70 commit `2e417e0`). Active axis-posture claim refreshed at this PR per pre-existing `[[class_3_tension_per_axis_claude_md_v2_1_to_v2_4_count_drift]]` carry **PARTIAL-CLOSED 2026-05-31**; §2.4 plan-internal 13-edge table preserved verbatim per FM-2 (the 13-vs-11 plan-vs-CXA divergence pre-dates the named carry — CXA v2.0 was already at 11; full closure requires plan-vs-CXA reconciliation arc at separate scope).

### 1.2 Spec + plan authority

| Artifact | Version | Role |
|---|---|---|
| `Spec_Action_Surface_v1.md` | v1.8 (footer-only consolidation pass 2026-05-28 — (i) §14.4 `skill.*` producer-site footer reference per AS-8d Q1=B + co-published with runtime spec v1.32 C-RT-27; (ii) §14.5 `managed_agents.*` production-only exclusion footer per AS-8f Q1=C DEFER INDEFINITELY mirror of AS-8e. v1.7 → v1.8 revision row added 2026-05-28; v1.6 → v1.7 GenAI span-name fork resolution row catch-up authored 2026-05-26) | Contract authority — 16 contracts C-AS-01 through C-AS-16 |
| `Implementation_Plan_Action_Surface_v1_4.md` | v1.4 (Class 1 fork resolution Reading B arc 2 absorption 2026-05-26 — U-AS-03 carrier-extension + U-AS-17 AC #3 text-replace + ACs #9/#10; net AC +3; ZERO new units; ZERO DAG change; ZERO cross-axis cascade) | Execution authority — 33 atomic units across 16 contracts and 9 topological levels (L0–L8) |

### 1.3 Scope inclusion

| Surface | Carrier units | Spec contract |
|---|---|---|
| SandboxTier + BlastRadiusTier + MechanismClass enums | U-AS-01, U-AS-02 | C-AS-01 §1 |
| SandboxFailClass + DeploymentSurface + PersonaTier + MCPTransport enums | U-AS-03, U-AS-04 | C-AS-03 §3; C-AS-11 §11 |
| Blast-radius floor mapping + ToolContract.minimum_tier | U-AS-05, U-AS-07 | C-AS-02 §2; C-AS-11 §11 |
| Sandbox-tier composition (5-input + 12-cell matrix + per-MCP-transport floor) | U-AS-06, U-AS-08, U-AS-10, U-AS-13 | C-AS-04 §4; C-AS-11 §11 |
| Sub-agent sandbox tier + SandboxProviderClass | U-AS-09, U-AS-11 | C-AS-04 §4 |
| 5-axis gate-level multiplicative tunable composition (GateLevel: AUTO / ASK / DENY) | U-AS-14 | C-AS-12 §12 |
| Cross-deployment monotonicity | U-AS-15 | C-AS-04 §4 |
| Sandbox observability `sandbox.*` 7-attribute namespace + sandbox-event idempotency-key composition | U-AS-16, U-AS-17, U-AS-18, U-AS-19 | C-AS-09 + C-AS-10 + C-AS-12 + C-AS-15 §15 |
| SecretRef + SecretAllowlist + SecretFailClass + breaker | U-AS-20, U-AS-22, U-AS-24 | C-AS-09 §9; C-AS-15 §15 |
| SkillFrontmatter schema + Skills loading discipline | U-AS-21, U-AS-23 | C-AS-05 + C-AS-06 + C-AS-07 |
| Skills filesystem residence + reachability + outputs_hash formula | U-AS-25, U-AS-26, U-AS-27 | C-AS-08 §8 |
| Anthropic + MCP primitive observability (15-namespace exports) | U-AS-28, U-AS-29, U-AS-30, U-AS-31, U-AS-32 | C-AS-13 + C-AS-14 |
| AS substrate seam exports manifest | U-AS-33 | C-AS-16 §16 |

### 1.4 Scope exclusion

| NOT AS | Owning axis / source |
|---|---|
| Path-class registry, state ledger, hash-chain, JSONL composition, worktree isolation | IS — `harness-is/CLAUDE.md` |
| Routing, retry, breaker, topology, workflow lifecycle, HITL placement | CP — `harness-cp/CLAUDE.md` |
| HITL primitive (4-response palette), cost attribution chain, audit-ledger schema, OD observability namespaces (`engine.*` / `audit.*` / `validator.fail.*` / `harness.breaker.*`) | OD — `harness-od/CLAUDE.md` |
| Workflow-shape-specific H_E surfaces (LSP / plan mode / Chrome / remote control / agent teams) | Out of H_T scope per AS-AL-4 |
| 5-tier MCP trust framework function (per-MCP-server trust composition) | CP plan (function lives in CP; AS surface declares the per-transport floor only — U-AS-13 §3.5 closing-paragraph note) |

---

## 2. Per-axis canonical artifacts

### 2.1 Anchoring ADRs

Per `Phase_7_Meta_Architecture_v1.md` §2.2 AS-axis primitives:

| ADR | Version | Role |
|---|---|---|
| ADR-F4 | v1.1 | Tool contract surface |
| ADR-F5 | v1.1 | Skills |
| ADR-D2 | v1.2 | Sandbox + blast radius |
| ADR-D3 | v1.2 | Filesystem residence |

ADD attestation: `Architectural_Design_Document_v1_3.md` v1.3.

### 2.2 AS export seams (consumed by CP / OD)

Per U-AS-33 substrate seam exports manifest (C-AS-16). Cardinality at CXA v2.16: **19 edges CP→AS canonical (6 genuine) + 10 edges OD→AS = 29 inbound consumer edges** (v2.1 baseline was 24+10=34; refreshed at this PR per `[[class_3_tension_per_axis_claude_md_v2_1_to_v2_4_count_drift]]` PARTIAL-closure 2026-05-31). Detailed per-bucket enumeration at `Cross_Axis_Composition_Document_v2_16.md` §2.3.3 (CP→AS; v2.16 preserves v2.15 row 6 U-CP-68 → U-AS-03 ToolContract Pattern-P1 seam) + §2.3.5 (OD→AS; preserved verbatim from v2.6 → v2.16; original §2.3.6 cite at v2.1 baseline was a typo — §2.3.6 is the OD→CP bucket per CXA §2.3 canonical numbering).

### 2.3 Cross-axis edge inventory (CXA v2.16; PARTIAL-refresh from v2.1 baseline at this PR)

| Edge direction | Edges | Source artifact |
|---|---|---|
| AS → IS (outbound; canonical) | **11** (CXA v2.6+ canonical; AS plan v1.2 §3.4 internally enumerates 13 — see §2.4 divergence note) | `Cross_Axis_Composition_Document_v2_16.md` §2.3.1 + §2.4 per-axis attribution |
| CP → AS (inbound) | **19 canonical / 6 genuine** (was 18/5 at v2.14; v2.15 row 6 U-CP-68 → U-AS-03 ToolContract Pattern-P1 seam landed) | `Cross_Axis_Composition_Document_v2_16.md` §2.3.3 |
| OD → AS (inbound) | 10 (unchanged v2.6 → v2.16) | `Cross_Axis_Composition_Document_v2_16.md` §2.3.5 (original v2.1 cite at `§2.3.6` was a typo — §2.3.6 is OD→CP) |
| AS → CP / AS → OD (outbound) | 0 | AS does not declare outbound edges to CP or OD; CP/OD pull from U-AS-33 |

### 2.4 AS → IS edge profile (13 plan-internal edges across 8 AS units; 11 at CXA canonical — see divergence note)

Per `Implementation_Plan_Action_Surface_v1_2.md` §3.4. **Plan-internal enumeration; CXA v2.16 §2.4 per-axis attribution aggregates to 11 AS outbound.** The 13-vs-11 plan-vs-CXA divergence is a known split that pre-dates the named `[[class_3_tension_per_axis_claude_md_v2_1_to_v2_4_count_drift]]` carry (CXA v2.0 was already at 11); reconciliation arc owed at separate scope (either AS plan v1.2 §3.4 amends 13 → 11 or CXA §2.4 §2.3.1 revisits). **NOT patched at this PR per FM-2.**

| AS unit | IS carrier(s) | IS export seam |
|---|---|---|
| U-AS-19 | U-IS-07, U-IS-12 | STATE_LEDGER_ENTRY_SHAPE_EXPORT + IDEMPOTENCY_KEY_JOIN_EXPORT |
| U-AS-25 | U-IS-08 | HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT (canonicalize carrier) |
| U-AS-26 | U-IS-07, U-IS-09, U-IS-10 | STATE_LEDGER + HASH_CHAIN (chain-link + verification carriers) |
| U-AS-27 | U-IS-11 | JSONL_EVENT_LEDGER_FORMAT_EXPORT (write contract carrier) |
| U-AS-28, U-AS-29, U-AS-30 | U-IS-01, U-IS-02 (each, ×2 carriers) | FILESYSTEM_PATH_CONTRACT_EXPORT (6 edges total) |

Edge cardinality verified at U-IS-17 substrate seam exports manifest per CXA v2.1 §2.3.1 OD-S2-3.A retroactive verification.

---

## 3. Topological entry-points (Level 0)

Per `Implementation_Plan_Action_Surface_v1_2.md` §3.5 ASCII dependency graph:

| L0 unit | Implements | Notes |
|---|---|---|
| U-AS-01 | SandboxTier + BlastRadiusTier + MechanismClass enums | Foundational enum substrate; consumed by 6 of 7 L1 units |
| U-AS-03 | SandboxFailClass enum | Foundational fail-class enum |
| U-AS-04 | DeploymentSurface + PersonaTier + MCPTransport enums | Foundational deployment + persona + transport enums |

**3 L0 units; in-degree 0.** Phase 7 sub-phase 7b AS-axis-stream execution begins from these entry-points.

### 3.1 Full DAG topology (9 levels)

```
LEVEL 0 — Foundational enums:
  U-AS-01 [SandboxTier+BlastRadiusTier+MechanismClass]
  U-AS-03 [SandboxFailClass]
  U-AS-04 [DeploymentSurface+PersonaTier+MCPTransport]

LEVEL 1 — Direct foundational consumers:
  U-AS-02, U-AS-05, U-AS-07, U-AS-11, U-AS-12, U-AS-20, U-AS-28

LEVEL 2 — Composition floors + L1 consumers:
  U-AS-06, U-AS-10, U-AS-22, U-AS-24, U-AS-25, U-AS-29, U-AS-31

LEVEL 3 — Sandbox-tier composition + downstream:
  U-AS-08, U-AS-09, U-AS-13, U-AS-14, U-AS-15, U-AS-26, U-AS-30

LEVEL 4 — Span attribute schema:
  U-AS-16 [seven sandbox.* attributes]

LEVEL 5–7 — Skills + canonicalization + observability composition

LEVEL 8:
  U-AS-33 (terminal aggregate exporter)
```

DAG verified acyclic per AS plan §3.4 Kahn execution: 33 units consumed; remaining edge set ∅.

### 3.2 Coverage matrix verification

Per AS plan §4: 16 of 16 contracts covered by ≥1 unit; no coverage gaps. Coverage matrix per-axis-only per OD-S1-2.A.

---

## 4. Substitution + anti-leakage surface

### 4.1 AS-axis substitutions

Per `Phase_7_Meta_Architecture_v1.md` §5.3: **6 AS-axis substitution entries**. H_E classification per Meta-Architecture §4.4.2:

| H_T primitive | H_E status | Substitution surface |
|---|---|---|
| H_T-AS-1 (SandboxTier 4-tier enum + tier-monotonicity) | ✗ absent | `CLAUDE.md` tier-naming convention + permission-modes-as-coarse-approximation |
| H_T-AS-2 (Tool contract schema) | ~ partial | Ad-hoc MCP server registration with operator-prompted contract enforcement |
| H_T-AS-3 (3-valued GateLevel AUTO/ASK/DENY) | ~ partial | Permission-mode gradient covers 2-of-3 cases (no AUTO-equivalent without prompt) |
| H_T-AS-4 (`sandbox.*` 7-attribute namespace emission) | ✗ absent | No `sandbox.*` namespace emission — substitution at MCP server boundary post-H_T-CP-1 retirement |
| H_T-AS-5 (Sandbox-event idempotency-key composition) | ✗ absent | No idempotency-key primitive in H_E |
| H_T-AS-8 (Anthropic + MCP primitive observability — 15-namespace exports) | ✗ absent | No 15-namespace emission |

H_T-AS-6 (SkillFrontmatter schema) and H_T-AS-7 (Skills filesystem residence at `.claude/skills/<name>/SKILL.md`) are **H_E ✓ native** per Meta-Architecture §4.4.2 direct match — but **AS-AL-3 binds**: H_T Skills additionally carry cross-axis IS-dependencies (filesystem-path classification per C-IS-01), so the U-AS-25 / U-AS-26 / U-AS-27 cross-axis edge declarations remain mandatory.

Full per-substitution bounded-scope + retirement criterion at Meta-Architecture §5.3. Retirement bindings: U-AS-NN landings per the criterion column.

**Retirement status (post 7d batch 16 joint H_T-CP-18 + H_T-AS-2 close, 2026-05-24).** Per cumulative batch records `.harness/phase-7d-retirement-events-batch-{1..16}.md` + v2 ledger `.harness/phase-7d-retirement-ledger-v2.md` §4 under operator-ratified runtime-only substitution-site reading + line-33 strict-reading discipline. **U-RT-86 L9-novies cluster close at `8e6311f` materializes the operational-MET evidence for the joint H_T-CP-18 + H_T-AS-2 RETIRE-READY → RETIRED transition** (2/2 e2e tests pass against in-process stdio MCP echo fixture; full 7-attr `mcp.*` namespace coverage verified at `mcp.tool.call` span). The joint close is the SECOND RETIRE-READY → RETIRED close in ledger history and the FIRST JOINT close (two substitutions sharing a binding chain close together at a single empirical-exercise event). **AS-axis crosses 50% RETIRED threshold at this batch (3/6 = 50.0%).** Forward-only ledger discipline preserved.

| Substitution | Status | Source |
|---|---|---|
| H_T-AS-1 (SandboxTier 4-tier + monotonicity) | **RETIRED** 2026-05-20 | `lifecycle/sandbox_dispatch.py` 6-provider×tier table; `handoff.py:174` monotonic-ascent; `--permission-mode` not reachable from runtime composers |
| H_T-AS-2 (Tool contract schema) | **RETIRED** (batch 16 joint close with H_T-CP-18, 2026-05-24) | `runtime_tool_dispatcher.py:41` imports `from harness_as.tool_contract import ToolContract`; production tool-dispatch operational at L9-sexies close (`83d3b54` U-RT-67 `RuntimeToolDispatcher.dispatch()` body); L9-septies stage-5 callsite wire-up at `stage_5_loop_init.py:309` via `materialize_runtime_tool_dispatcher_stage` factory (U-RT-75); operational-MET evidence at U-RT-86 e2e at `8e6311f` exercising production `RuntimeToolDispatcher.dispatch(TOOL_STEP)` against in-process stdio MCP echo fixture — `ToolContract` schema enforced at every dispatch; binding chain `mcp_clients` → `materialize_mcp_client_host_stage` U-RT-73 → `tool_dispatcher`/`workflow_driver.py:619` all empirically MET per batch-16 §2.3. Joint-coupled with H_T-CP-18 per batch-12 §1.4 + batch-16 §2.1 |
| H_T-AS-4 (sandbox.* 7-attribute namespace) | **RETIRED** (batch 19 Reading B arc 2 close, 2026-05-26) | Class 1 fork Reading B resolution at worktree HEAD `c3545b6`. AS spec v1.5 → v1.6 NEW §15.8/§15.9/§15.10 + AS plan v1.3 → v1.4 + harness-as carrier-extension (`MCPInvocationFailClass` + `project_mcp_to_sandbox_fail_class`) + harness-runtime dispatcher bug fix at `runtime_tool_dispatcher.py:395-412` (invented-string dead-code REPLACED with isinstance dispatch + NEW `_emit_sandbox_violation` helper opens `sandbox.violation` child span on exception path with dual fail-class attrs). Production binding chain empirically MET at 3 stages per batch-16 §6 verification-shape sharpening: (1) carrier landed at `harness-as.sandbox_fail_class`; (2) producer span site at dispatcher exception handlers; (3) 5/5 e2e tests at `test_lifecycle_runtime_tool_dispatcher.py:484-666` PASS against real fastmcp echo fixture verifying the 4 MCPInvocationFailClass paths + happy-path no-violation regression guard. `sandbox.cost.tier_overhead_usd` (a separate §15.2 row not part of the AS-4 retirement gate at PARTIAL framing) tracked at AS plan §0.7 carry-forwards per FM-2 |
| H_T-AS-5 (sandbox-event idempotency-key composition) | **RETIRED** (batch 23 STILL-BOUNDED → RETIRED direct transit, 2026-05-28) | Gate-text reframe per `[[batch-22 sub-species 7]]` precedent — harness-as helpers operate on Pydantic `SandboxSpanEvent` model; production uses OTel spans directly; literal "invoke the helper" reading is structurally impossible. Satisfiable reading per AS spec §15.6 row 1 is OTel span attribute presence. Production at `runtime_tool_dispatcher.py:260-282` `_emit_sandbox_violation` sets `idempotency_key` attribute on `sandbox.violation` span at all 4 exception-path callsites; 1092/1092 harness-runtime tests pass + 4 skipped including new `test_dispatch_sandbox_violation_idempotency_key_matches_parent_dispatch` verifying §15.6 row 1 join. See `phase-7d-retirement-events-batch-23.md` |
| H_T-AS-8a (anthropic.* 10-attribute observability namespace) | **RETIRED** (batch 24 ledger-v2-layer decomposition + immediate close, 2026-05-28) | `anthropic.*` 10/10 LANDED at `llm_dispatch.py:386-432` gen_ai span — 4/10 cache subset pre-existing + 6/10 closed at AS-8 discriminator audit close 2026-05-26 (`thinking_mode` / `thinking_budget_tokens` / `thinking_effort` / `batch_id` / `tokenizer_version` / `inference_geo` per `_AnthropicRequestAttrs` carrier + `_extract_anthropic_request_attrs` extractor). Producer-binding chain MET; consumer-side verified at gen_ai span attribute presence. See `phase-7d-retirement-events-batch-24.md` §1.1 |
| H_T-AS-8b (mcp.* 7-attribute observability namespace) | **RETIRED** (batch 24 ledger-v2-layer decomposition + immediate close, 2026-05-28) | `mcp.*` 7/7 LANDED at `mcp_client_namespace_emitter.py:73-79` + `runtime_tool_dispatcher.py:375` (`mcp.tool.call` span). Producer-binding chain MET; consumer-side verified at e2e test surface (L9-novies + L9-sexies + L9-septies cluster closes 2026-05-22..24). See batch-24 §1.2 |
| H_T-AS-8c (memory.* 6-attribute observability namespace) | **RETIRED** (batch 24 ledger-v2-layer decomposition + immediate close, 2026-05-28) | `memory.*` 6/6 LANDED at `memory_tool_dispatch.py:286-338` (`memory.operation` span; producer site at L9-octies arc `42c9a30`, 2026-05-23). Producer-binding chain MET; consumer-side verified at runtime composer `execute_with_memory_callbacks`. See batch-24 §1.3 |
| H_T-AS-8d (skill.* 6-attribute observability namespace) | **RETIRED** 2026-05-28 (batch-31 deployment-time-opt-in-gate closure via mech-β AC #7 green on main at PR #14 merge `24a9363`; FIRST AS-axis sub-species 7.deployment-time-opt-in-gate close per `.harness/phase-7d-retirement-events-batch-31.md`) | Producer-binding chain LANDED at runtime spec v1.32 §14.17 NEW C-RT-27 + plan v2.28 L9-quindecies cluster (U-RT-99/100/101). `SkillActivationSpanEmitter` at `harness-runtime/src/harness_runtime/lifecycle/skill_activation.py` opens `skill.activation` span carrying all 6 AS spec §14.4 attributes (`skill.id` + `skill.name` + `skill.version_sha` + `skill.frontmatter.version` + `skill.body_tokens` + `skill.activation_mode`). 3 hook binding sites at production: (1) per-LLM-dispatch at `lifecycle/llm_dispatch.py:dispatch` pre-call → `activation_mode = tool_search`; (2) per-workflow-init at `harness-cp/.../workflow_driver.py:execute_workflow` post-drain-check → `activation_mode = frontmatter_only`; (3) operator-explicit `HarnessContext.activate_skill(skill_id, workflow_id)` → `activation_mode = filesystem_read`. Structural-criterion-B MET via factory wiring at `bootstrap/factories/skill_activation_emitter_factory.py`. **Terminal in-CLI state at RETIRE-READY 2026-05-28 (batch-25).** No further in-CLI close pathway. Full RETIRED gates on operator-bound `RuntimeConfig.skill_activation_hook_config` non-None + e2e exercise observing `skill.activation` span emission at ≥1 hook site per X-AL-2 retirement criterion + spec §14.17.6 scope. Bounded-residual carry per X-AL-2; not a defect. Per `.harness/class_1_fork_as_8d_skill_activation_surface_absence.md` Reading B Q-set (Q1=B / Q2=d hybrid / Q3=i preserve / Q4=q NEW module / Q5=β no edge) — operator-ratified 2026-05-28; apply arc landed same-session at commits `471e0e2` + `83251b2` |
| H_T-AS-8e (files.* 8-attribute observability namespace) | **STILL-BOUNDED-INDEFINITELY** | Files arc DEFERRED INDEFINITELY per runtime spec v1.17 §14.C (Memory-only scope ratified 2026-05-23). Not gated on observability decisions; gated on Files API surface authoring decision at operator-discretion timing. Per X-AL-2 bounded-residual carry; not a defect |
| H_T-AS-8f (managed_agents.* 3-attribute observability namespace) | **STILL-BOUNDED-INDEFINITELY** (DEFER INDEFINITELY mirror AS-8e) 2026-05-28 | DEFER INDEFINITELY per `.harness/class_1_fork_as_8f_managed_agents_namespace_production_only_exclusion.md` Q1=(C) operator-ratification + runtime spec v1.33 change-note + AS spec v1.7 §14.5 production-only exclusion footer. Mirror of AS-8e files.* indefinite-defer posture. Honors AS spec C-AS-13 §13.2 adoption-depth matrix design declaration (`surface_qualifier = LOCAL_DEVELOPMENT` + `"X at local-development"` across all 4 workload classes) + ADR-D3 §1.8.1 `managed_agents.runtime (Managed Agents only)` span scope + harness-as enforcement test `test_managed_agents_excluded_at_local_development` at `harness-as/tests/test_anthropic_primitive_adoption.py:183`. Not gated on observability decisions; gated on Anthropic managed_agents beta SDK integration + H_T managed-cloud-surface deployment at operator-discretion timing. Per X-AL-2 bounded-residual carry; not a defect |
| H_T-AS-9 (substrate seam exports manifest) | RETIRED (authoring close, v1 §1) | Authoring-only |

**AS-axis cumulative post-batch-31 (2026-05-28; ledger-v2-layer decomposition view):** **9 / 11 RETIRED (81.8%, AS-1 + AS-2 + AS-4 + AS-5 + AS-8a + AS-8b + AS-8c + AS-8d + AS-9)** + **0 / 11 RETIRE-READY (bucket EMPTY in active denominator)** + **0 / 11 PARTIAL** + **2 / 11 STILL-BOUNDED-INDEFINITELY (18.2%, AS-8e + AS-8f)** — BOTH STILL-BOUNDED-INDEFINITELY per per-namespace production-deployment-surface-gated indefinite-defer ratifications (AS-8e files.* per runtime spec v1.17 §14.C; AS-8f managed_agents.* per runtime spec v1.33 change-note + AS spec v1.7 §14.5 footer + `class_1_fork_as_8f_managed_agents_namespace_production_only_exclusion.md` Q1=(C)). **Active substitutions (excluding both INDEFINITE deferrals): 8 / 9 RETIRED + 1 / 9 RETIRE-READY = 9 / 9 = 100.0% pipeline-advanced (8 RETIRED + 1 RR; ZERO active STILL-BOUNDED).** Pipeline advanced raw (R+RR+P): **9/11 = 81.8%** (was 8/11 = 72.7% post-AS-8d RR; AS-8f's exit from active denominator into INDEFINITE bucket promotes raw pipeline-advanced fraction by 1 unit since SB → SB-INDEFINITE under X-AL-2 is a routing transit, not regression). **AS-axis crosses 81.8% pipeline-advanced at sub-row layer with ZERO active STILL-BOUNDED** at batch-26 close — first AS-axis state where the active-substitution view holds NO open STILL-BOUNDED rows. **Meta-Arch §2.2 view preserved verbatim** (6 AS rows; AS-8 monolithic NOT decomposed at design-declaration layer per X-AL-3 + advisor pre-substantive consultation 2026-05-28). **AS-axis post-batch-25 prior (post-AS-8d RR):** 8/11 RETIRED + 1/11 RETIRE-READY + 0/11 PARTIAL + 2/11 STILL-BOUNDED (AS-8e INDEFINITE + AS-8f active).

**Operator-opt-in RETIRE-READY pattern (post-batch-16: BUCKET EMPTY).** Pattern members across batches 10–16: H_T-CP-18 (batch 10 RETIRE-READY → batch 16 RETIRED), H_T-CP-21 (batch 11 RETIRE-READY → batch 15 DOWN PARTIAL — Reading-D audit per `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md`), H_T-AS-2 (batch 12 RETIRE-READY → batch 16 RETIRED — joint close with CP-18 via shared MCP-client substrate per batch-16 §2.1), H_T-CP-16 (batch 13 RETIRE-READY → batch 14 RETIRED). All 4 historical members closed; the operator-opt-in RETIRE-READY bucket is empty for the first time since batch-10 introduced the pattern. Future PARTIAL → RETIRE-READY promotions under this pattern must apply the batch-16 §6 verification-shape sharpening: **"grep-for-presence ≠ verified-working-end-to-end"** — all 3 binding-chain stages (RuntimeConfig field + bootstrap stage factory + driver invocation succeeds end-to-end against a real substrate) must be empirically verified before promotion.

**L9-sexies/L9-septies architectural finding update (per ledger-v2 §4 reframe).** ledger-v2 §4 identified AS-4/5/8 retirement as Phase-3+ tool-invocation-runtime-gated rather than Phase-2-runtime-gated. The L9-sexies (U-RT-63 → U-RT-70, 8-unit cluster) + L9-septies (U-RT-71 → U-RT-75, 5-unit cluster) close at 2026-05-22 materializes that Phase-3+ tool-invocation runtime composer. AS-2 transitions PARTIAL → RETIRE-READY; AS-4 transitions STILL-BOUNDED → PARTIAL (6/7 attrs emit; 1 deferred); AS-5 STILL-BOUNDED stands (idempotency-key composition not yet invoked at production site); AS-8 PARTIAL stands but coverage expands substantially (mcp.* now full; anthropic.* unchanged cache subset; other namespaces consumer-side gated).

### 4.2 AS-axis anti-leakage rules

Per `Phase_7_Meta_Architecture_v1.md` §7.3:

| Rule | Statement | Anti-pattern foreclosed |
|---|---|---|
| AS-AL-1 | Permission modes ≠ SandboxTier enum. Permission modes gate tool-invocation approval; SandboxTier gates code-execution capability per blast-radius taxonomy (ADR-D2 v1.2) | Adopting H_E's 6-mode taxonomy as H_T's SandboxTier decomposition |
| AS-AL-2 | H_E built-in tools are NOT user-extensible H_T tools. All H_T tool surface lives behind MCP server boundary | Collapsing the MCP-server boundary at the H_T design site |
| AS-AL-3 | H_E Skills loading mechanism is isomorphic; H_T Skills filesystem residence additionally carries cross-axis IS-dependencies (filesystem-path classification per C-IS-01) | Treating "Skills work natively" as license to skip authoring U-AS-25 → U-AS-27 cross-axis edge declarations |
| AS-AL-4 | Workflow-shape-specific H_E surfaces (LSP / plan mode / Chrome / remote control / agent teams) are OUT OF H_T scope. H_T is workflow-shape-agnostic | Adding H_T primitives for LSP / plan mode / Chrome / remote control / agent teams under any pretext |

Cross-cutting rules X-AL-1 / X-AL-2 / X-AL-3 (Meta-Architecture §7.7) also bind AS-axis implementation. **X-AL-1 substrate boundary discipline is most concrete at AS axis**: the H_E ↔ H_T boundary lives at the MCP server process (process isolation, not convention), and that process boundary IS the AS-axis cross-substrate surface. All H_T tool surface lives behind it (AS-AL-2 reinforces this).

---

## 5. Back-flow channels

Axis-specific design defects route per `Project_Workflow_v1_8.md` §2.7.6 + workspace root `CLAUDE.md` §4.3.

### 5.1 Class 1 routing by defect locus

| Defect locus | Class 1 routing |
|---|---|
| AS plan v1.2 atomic unit signature defect (acceptance criteria unimplementable; cross-unit dependency wrong) | Phase 6 plan revision-pass at design-phase workspace |
| AS spec v1.3 contract defect (C-AS-NN under-specifies the surface; spec inconsistent with ADR) | Phase 5 spec revision-pass at design-phase workspace |
| ADR-F4 v1.1 / F5 v1.1 / D2 v1.2 / D3 v1.2 anchor decision defect | Phase 3a/3b ADR revision via council convening |
| ADD v1.3 attestation mismatch with AS spec v1.3 | Phase 3d ADD revision |
| CXA v2.16 §2.3.1 (AS→IS) / §2.3.3 (CP→AS) / §2.3.5 (OD→AS) edge defect | Phase 6 CXA revision-pass at design-phase workspace (original v2.1 cites at §2.3.4 (CP→AS) + §2.3.6 (OD→AS) were typos — canonical bucket numbering is §2.3.3 + §2.3.5; refreshed at this PR per `[[class_3_tension_per_axis_claude_md_v2_1_to_v2_4_count_drift]]` PARTIAL-closure 2026-05-31) |
| AS export seam (U-AS-33 manifest) defect; consumer-side CP / OD plan re-cite required | Phase 6 AS plan revision-pass; cascade to consumer-side plans if seam-export shape changes |

### 5.2 Open carry-forwards at AS axis entry

Per `Plan_Executability_Audit_v1.md` §3.2:

| Carry-forward | Status | Routing |
|---|---|---|
| GUARDRAIL U-AS-17 (custom OTel SpanProcessor for SENSITIVE_DATA_EXCLUSIONS) | Project-authored against `opentelemetry.sdk.trace.SpanProcessor` ABC [HIGH] | Phase 7 execution-time; non-blocking |
| GUARDRAIL U-AS-18 (always-sampled-with-tail-keep Sampler) | Project-authored against `opentelemetry.sdk.trace.sampling.Sampler` ABC [HIGH] | Phase 7 execution-time; non-blocking |
| GUARDRAIL U-AS-20 (TIER_3 / TIER_4 in-sandbox HTTP bootstrap server) | Project-authored; `http.server` stdlib candidate | Phase 7 execution-time; non-blocking |
| GUARDRAIL U-AS-25 (JCS canonicalization carry-forward from U-IS-08) | Inherits U-IS-08 binding decision | Resolves with U-IS-08 landing |

C7 consultation outcome at audit (preserved): `opentelemetry-instrumentation-genai` adoption is limited to LLM-call spans against `anthropic` + `openai` providers only; project-authored emission required for `ollama` provider and all 11 specialization namespaces beyond LLM-call.

### 5.3 Filing footer

| Field | Value |
|---|---|
| Artifact | `harness-as/CLAUDE.md` |
| Authored at | Phase 6.5 Session 6 (ε), 2026-05-15 |
| Authoring authority | `Phase_6_5_Session_6_Kickoff.md` §2.1.2 |
| Predecessor | Design-phase workspace AS spec v1.3 + AS plan v1.2 |
| Revision policy | This file is canonical for the `harness-as/` subdirectory; revisions route to design-phase back-flow per §5.1 |

---

*End of `harness-as/CLAUDE.md`. Parent guidance at workspace root `CLAUDE.md`. AS spec + plan + CXA v2.16 §2.3.1 / §2.3.3 / §2.3.5 at design-phase workspace.*
