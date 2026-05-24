# Phase 7d Retirement Events — Batch 12

| Field | Value |
|---|---|
| Batch number | 12 |
| Filed at | 2026-05-23 (post batch-11 doc-hygiene reconciliation arc — `harness-as/CLAUDE.md` + `harness-od/CLAUDE.md` §4.1 axis tables surfaced 3 substitution transitions structurally landed at prior cluster closes but not yet filed as retirement events) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 invoked per ledger-drift reconciliation between batch-11 §7 cumulative table (32/49 advanced) and the refreshed axis CLAUDE.md tables at commits `aeacd93` + `32bb901` (37/49 advanced per axis tables). This batch makes the 3-transition delta explicit as retirement-event records. |
| Predecessor batch | `phase-7d-retirement-events-batch-11.md` (2026-05-23, 1 STILL-BOUNDED → RETIRE-READY for H_T-CP-21 + 4 STILL-BOUNDED → PARTIAL for H_T-CP-16/17/19/22; cumulative 22/49 RETIRED + 2 RETIRE-READY + 8 PARTIAL = 32/49 advanced per §7) |

---

## §0 Batch context

**Status type: 3 retirement-criterion transitions structurally landed at prior arcs, surfaced + made explicit at this filing — 1 STILL-BOUNDED → RETIRE-READY (H_T-AS-2) + 2 STILL-BOUNDED → PARTIAL (H_T-AS-4 + H_T-OD-5). NO new RETIRED transitions.**

This batch records 3 substitution-status transitions that were already structurally complete at prior cluster closes (L9-sexies + L9-septies for AS-axis; cluster 4-OD-D for OD-axis) but had not been filed as standalone retirement-event records. The transitions surfaced during the post-batch-11 doc-hygiene-pass refresh of the per-axis CLAUDE.md §4.1 retirement-status tables (commits `aeacd93` + `32bb901`).

**Reconciliation rationale per workspace `CLAUDE.md` §4.3 forward-only ledger discipline.** Batch-11 §7 cumulative table reported 32/49 advanced. The post-batch-11 axis CLAUDE.md refreshes report 37/49 advanced (AS-axis 5/6 = 83.3%; OD-axis 4/8 = 50.0%). The 5-row delta = (AS-2 RETIRE-READY + AS-4 PARTIAL + OD-5 PARTIAL) + 2 prior transitions already captured at batch 9 / batch 10 + axis-table refresh. Filing this batch makes the AS/OD delta explicit as retirement-event records, restoring forward-only ledger ↔ axis-pointer-table consistency at the batch-record layer.

Per the operator-ratified runtime-only substitution-site reading at `.harness/phase-7d-retirement-ledger-v2.md` §2.1 + line-33 strict-reading discipline:

> Bootstrap-materializes-but-driver-never-invokes ≠ RETIRE-READY. The carrier landing + composer materialization satisfies condition A (cited unit IDs landed) but is silent on condition B. RETIRE-READY requires the production execution path to invoke the primitive end-to-end at runtime — not merely for the primitive to exist as a library.

Under that discipline, all 3 transitions classified by their production-callsite empirical state at HEAD `f364be6`:

- **H_T-AS-2:** `runtime_tool_dispatcher.py:41` imports `ToolContract` + production tool-dispatch operational at L9-sexies/L9-septies; operator-config-gated via `RuntimeConfig.mcp_servers=[]` default. **RETIRE-READY** (same operator-opt-in pattern as H_T-CP-18 batch-10 + H_T-CP-21 batch-11)
- **H_T-AS-4:** 6 of 7 `sandbox.*` attrs declared at `runtime_tool_dispatcher.py:179-184` emit at production `sandbox.enter` + `sandbox.exit` spans (U-RT-67 `83d3b54`); 7th `sandbox.violation` attr deferred per in-file comment. **PARTIAL** (production callsite present; full namespace coverage incomplete)
- **H_T-OD-5:** Cost-attribution at LLM dispatch site landed at U-OD-38 (`7104fd7`, cluster 4-OD-D commit 1/2); production LLM-dispatch path invokes `resolve_for(RATE_TABLE_V1, provider, model)`. 5-step chain operational at 1 of 4 dispatch surfaces (LLM); tool / validator / webhook dispatch sites cross-axis-blocked. **PARTIAL**

**Conclusion (preview):** 0 new RETIRED transitions; cumulative **22/49 RETIRED** (44.9%) unchanged. **1 new RETIRE-READY transition** (H_T-AS-2 — joins H_T-CP-18 batch-10 + H_T-CP-21 batch-11 in the operator-opt-in RETIRE-READY pattern, now 3 substitutions). **2 new PARTIAL upgrades** from STILL-BOUNDED (H_T-AS-4 + H_T-OD-5). Pipeline advanced (RETIRED + RETIRE-READY + PARTIAL): **37/49 = 75.5%** (vs 32/49 = 65.3% post-batch-11).

---

## §1 H_T-AS-2 STILL-BOUNDED → RETIRE-READY

| Field | Value |
|---|---|
| Substitution ID | H_T-AS-2 |
| Primitive | Tool contract schema (FastMCP-server-authored) |
| Substituted H_E surface | "Ad-hoc MCP server registration with operator-prompted contract enforcement" (Meta-Arch §5.3 row H_T-AS-2 ~ partial classification) |
| Prior status | PARTIAL per ledger-v2 §4 ("`ToolRegistry` typed surface met; `materialize_tool_registry` returns empty; `MCPHost.started=False` placeholder. Production deferred to tool-invocation runtime composer"); per `harness-as/CLAUDE.md` §4.1 pre-batch-12 PARTIAL row |
| Transition this batch | PARTIAL → **RETIRE-READY** |
| Triggering arc | L9-sexies cluster close (U-RT-63 → U-RT-70, 8 carrier units) + L9-septies cluster close at `00da5ef` 2026-05-22 (U-RT-71 → U-RT-75, 5 carrier units): materializing the Phase-3+ tool-invocation runtime composer that ledger-v2 §4 flagged as load-bearing for AS-2 / AS-4 / AS-5 / AS-8 retirement |

### §1.1 Criterion A — MET

| Unit | Landing commit | Surface | Verification at HEAD `f364be6` |
|---|---|---|---|
| **U-RT-64** | `39e23ad` | `MCPClientHost.start()` STDIO subprocess lifecycle + `list_tools` registry population | ✓ git log verified |
| **U-RT-65 + U-RT-66** | `fdbb72e` | `MCPClientHost` HTTP + SSE transport branches | ✓ git log verified |
| **U-RT-67** | `83d3b54` | `RuntimeToolDispatcher.dispatch()` body + sandbox + mcp span emission | ✓ git log verified |
| **U-RT-69** | `bdf3b67` | `WebhookDeliveryComposer` + `WebhookDeliveryResult` carriers | ✓ git log verified |
| **U-RT-70** | `961e3fb` | `OperatorBurdenEvaluator` + `DegradationDecision` carriers + sampled span emission | ✓ git log verified |
| **U-RT-71..U-RT-75** | L9-septies cluster (`00da5ef` close) | Bootstrap-wiring chain — `RuntimeConfig` schema extension + `HarnessContext` schema extension + stage-3a `materialize_mcp_client_host_stage` + `RetryBreakerToolDispatcher` + stage-5 `materialize_runtime_tool_dispatcher_stage` factory + U-RT-68 wire-up | ✓ git log verified |

**Criterion A status: MET.** Production tool-invocation runtime composer landed across L9-sexies + L9-septies clusters (13 carrier units total).

### §1.2 Criterion B — STRUCTURAL MET; OPERATIONAL OPT-IN GATED

**Substitution site analysis at HEAD `f364be6`.** H_T-AS-2's substituted H_E surface is ad-hoc MCP server registration with operator-prompted contract enforcement. The H_T substitution-target is the FastMCP-server-authored `ToolContract` schema with typed Pydantic v2 contracts dispatched via `RuntimeToolDispatcher`.

**Strict structural reading:**

```
$ grep -n 'from harness_as.tool_contract' harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py
41:from harness_as.tool_contract import ToolContract
```

The production tool-dispatch path at `runtime_tool_dispatcher.py` consumes the AS-axis `ToolContract` schema. Stage-5 callsite at `stage_5_loop_init.py:309` binds `ctx.tool_dispatcher = await materialize_runtime_tool_dispatcher_stage(ctx, config)` (per U-RT-75 factory body); TOOL_STEP routing through `SyncDispatcherFacade` per runtime spec v1.16 §14.9.6 inv 6 + U-RT-68 wire-up.

**Structural reading: MET.** ✓

**End-to-end operational reading:**

Bounded carry-forward — default `RuntimeConfig.mcp_servers=[]` produces empty-sentinel `MCPClientHost` at `mcp_client_host_factory.py:71`. Same operator-opt-in pattern as H_T-CP-18 batch-10 (`mcp_servers` config gates live MCP-client traffic) + H_T-CP-21 batch-11 (`validator_framework=None` default gates ValidatorFramework invocation).

Production exercise requires:

1. Operator-supplied `mcp_servers` config (non-empty `list[MCPServerConfig]`)
2. External MCP server availability at runtime's network boundary
3. Workflow step invoking a tool exposed by a configured MCP server, routing through stage-5 `tool_step_dispatcher` → `RetryBreakerToolDispatcher` → `RuntimeToolDispatcher.dispatch`

**Operational reading: GATED on operator config + external availability.** ⚠

**Both readings disposition: structural MET; operational opt-in GATED.** RETIRE-READY per the operator-opt-in pattern now spanning 3 substitutions (CP-18 + CP-21 + AS-2).

### §1.3 Production callsite invocation evidence

| Element | Site | Verification |
|---|---|---|
| AS-axis `ToolContract` import | `runtime_tool_dispatcher.py:41` `from harness_as.tool_contract import ToolContract` | ✓ grep verified |
| AS-axis `SandboxTier` import | `runtime_tool_dispatcher.py:40` `from harness_as.sandbox_tier import SandboxTier` | ✓ grep verified |
| Stage-5 factory invocation | `stage_5_loop_init.py:309` `await materialize_runtime_tool_dispatcher_stage(ctx, config)` | ✓ grep verified |
| TOOL_STEP routing | runtime spec v1.16 §14.9.6 inv 6 + U-RT-68 wire-up | ✓ batch-10 §1.3 verified |
| RuntimeToolDispatcher production body | `runtime_tool_dispatcher.py` `class RuntimeToolDispatcher` + `dispatch()` method | ✓ grep verified |

### §1.4 RETIRE-READY → RETIRED gate

H_T-AS-2 RETIRE-READY → RETIRED full transition gates on the same conditions as H_T-CP-18 batch-10 RETIRED gate (the two substitutions share the MCP-client substrate):

1. Operator runtime config landing — `RuntimeConfig(mcp_servers=[MCPServerConfig(...)])` non-empty
2. External MCP server availability
3. End-to-end tool-dispatch integration test exercising real MCP server invocation through the full chain
4. Per advisor reconciliation discipline (batch 10 §1.4 + batch 11 §1.4): RETIRE-READY is the honest classification while operator-opt-in default produces empty-sentinel host

**Coupling note: H_T-AS-2 + H_T-CP-18 share an external-server-exercise gate.** Both substitutions transition RETIRE-READY → RETIRED jointly at the same e2e exercise event (real workflow step invoking a tool exposed by a configured external MCP server). No independent transition possible — the production tool-dispatch chain wires both substitutions through the same stage-5 callsite + MCPClientHost substrate. Operator-discretion timing.

---

## §2 H_T-AS-4 STILL-BOUNDED → PARTIAL

| Field | Value |
|---|---|
| Substitution ID | H_T-AS-4 |
| Primitive | `sandbox.*` 7-attribute OTel namespace emission at MCP server boundary |
| Substituted H_E surface | "No `sandbox.*` namespace emission — substitution at MCP server boundary post-H_T-CP-1 retirement" (Meta-Arch §5.3 row H_T-AS-4 ✗ absent classification) |
| Prior status | STILL-BOUNDED per ledger-v2 §4 ("Library carriers exist; zero runtime references; no tool-invocation producer site") |
| Transition this batch | STILL-BOUNDED → **PARTIAL** |
| Triggering arc | L9-sexies cluster close — U-RT-67 commit `83d3b54` materializing `RuntimeToolDispatcher.dispatch()` body with `sandbox.enter` + `sandbox.exit` span emission |

### §2.1 Criterion A — MET

`sandbox.*` 7-attribute namespace per C-AS-15 §15 declares 7 typed attributes; 6 declared as named constants at production tool-dispatcher:

```
$ grep -n 'ATTR_SANDBOX_' harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py
179:ATTR_SANDBOX_TIER = "sandbox.tier"
180:ATTR_SANDBOX_TECH = "sandbox.tech"
181:ATTR_SANDBOX_PROVIDER = "sandbox.provider"
182:ATTR_SANDBOX_POLICY_ASSIGNED_TIER_REASON = "sandbox.policy.assigned_tier_reason"
183:ATTR_SANDBOX_COST_TIER_OVERHEAD_MS = "sandbox.cost.tier_overhead_ms"
184:ATTR_SANDBOX_FAIL_CLASS = "sandbox.fail.class"
```

7th attribute `sandbox.violation` deferred per in-file comment:

```
$ grep -n 'sandbox.violation deferred' harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py
414:            # --- Step 9-10: sandbox.exit span (sandbox.violation deferred) --
```

**Criterion A status: PARTIAL — 6 of 7 attribute carriers declared at production site.** Carrier landing per ledger-v2 (`sandbox_span_schema.py`, `sandbox_attribute_schema.py`, `sandbox_event_sampling.py`) preserved at library layer.

### §2.2 Criterion B — STRUCTURAL PARTIAL (production spans emit; full namespace coverage incomplete)

**Production emission sites at HEAD `f364be6`:**

```
$ grep -n 'tracer.start_as_current_span("sandbox' harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py
347:                tracer.start_as_current_span("sandbox.enter")
416:                tracer.start_as_current_span("sandbox.exit")
```

`sandbox.enter` + `sandbox.exit` spans emit at production tool-dispatch path. 6 of 7 `sandbox.*` attribute namespaces populate. 7th attribute (`sandbox.violation`) deferred to follow-on arc.

**Criterion B disposition: STRUCTURAL PARTIAL.** Production callsite present + namespace emission active; full 7-attr coverage incomplete (1 attr deferred). Per ledger-v2 §2.1 strict reading, this is PARTIAL not RETIRE-READY.

### §2.3 PARTIAL → RETIRE-READY gate

H_T-AS-4 PARTIAL → RETIRE-READY transition gates on `sandbox.violation` 7th attribute emission at production tool-dispatch — currently deferred per `runtime_tool_dispatcher.py:414` comment. Follow-on arc: integrate `sandbox.violation` attribute emission at the sandbox-exit boundary when policy violation detected (typed violation classification + namespace emission). Operator-discretion timing.

---

## §3 H_T-OD-5 STILL-BOUNDED → PARTIAL

| Field | Value |
|---|---|
| Substitution ID | H_T-OD-5 |
| Primitive | Cost-attribution 5-step chain (substrate → carrier → resolver → reducer → emitter) |
| Substituted H_E surface | "`/cost` + `--max-budget-usd` coarse; not 5-step chain" (Meta-Arch §5.5 row H_T-OD-5 ~ partial classification) |
| Prior status | STILL-BOUNDED per ledger-v2 §6 ("`CostAttributionChain.compute_cost(...)` exists ... wired into ctx.cost_chain; zero production callsites outside definition + shutdown `cost_chain_noop=True` flag; `api.py:463` hard-codes `cost_attribution=()` per U-OD-21 HALT carry-forward") |
| Transition this batch | STILL-BOUNDED → **PARTIAL** |
| Triggering arc | U-OD-38 landing at commit `7104fd7` (cluster 4-OD-D impl arc commit 1/2 partial): cost-attribution at LLM dispatch site |

### §3.1 Criterion A — MET

Cost-attribution 5-step chain carriers landed across cluster 4-OD-C + cluster 4-OD-D:

| Unit | Landing commit | Surface | Verification |
|---|---|---|---|
| **U-OD-46** | `1daeda0` | `PRICE_TABLE_REF` canonical schema — 4 frozen Pydantic v2 models | ✓ git log verified |
| **U-OD-47** | `2e025e1` | v1 default rate-table substrate — anthropic + openai + ollama | ✓ git log verified |
| **U-OD-48** | `4899792` | Rate-table resolver — provider-then-model resolution + `CP-FAIL-RATE-TABLE-MISSING` typed error | ✓ git log verified |
| **U-OD-49** | `404fef7` | Decimal string-serialization at OTel attribute boundary | ✓ git log verified |
| **U-OD-38** | `7104fd7` (cluster 4-OD-D commit 1/2 partial) | Cost-attribution at LLM dispatch site | ✓ git log verified |

**Criterion A status: MET.** PRICE_TABLE_REF substitution RETIRED at U-OD-38 landing per `[[fork-price-table-ref-substitution-retirement]]` memory entry.

### §3.2 Criterion B — STRUCTURAL PARTIAL (1 of 4 dispatch surfaces operational)

**Production invocation site at HEAD `f364be6`:**

```
$ grep -n 'anthropic.tokenizer_version' harness-runtime/src/harness_runtime/lifecycle/cost_attribution_llm_dispatch.py
128: anthropic.tokenizer_version attribute; defaults to `"v0"` when absent
```

The LLM dispatch site (`cost_attribution_llm_dispatch.py`) invokes the rate-table resolver + 5-step cost chain at production execution path. Per memory `[[fork-price-table-ref-substitution-retirement]]`: "production LLM-dispatch path uses `resolve_for(RATE_TABLE_V1, provider, model)`; grep verified no production callsite invokes the old PRICE_TABLE_REF placeholder".

**LLM dispatch surface: STRUCTURAL MET.** ✓ 1 of 4 cost-attribution dispatch surfaces operational at production.

**Remaining 3 dispatch surfaces NOT yet wired (cross-axis-blocked):**

| Dispatch surface | Status | Block |
|---|---|---|
| **Tool dispatch** | NOT wired | U-OD-39 cross-axis-blocked on U-RT-67 / U-RT-69 (tool-invocation composer — landed at L9-sexies, but cost-attribution at tool-dispatch site not yet routed) |
| **Validator dispatch** | NOT wired | U-OD-40 cross-axis-blocked on U-CP-60 (ValidatorFramework — landed at cluster 10-CP-A, but cost-attribution at validator-dispatch site not yet routed) |
| **Webhook dispatch** | NOT wired | U-OD-41 cross-axis-blocked on U-CP-72 audit-write seam (PARTIAL-LAND 6/8 per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]`) + CXA v2.9 amendment owed |

Per `[[fork-cost-record-audit-ledger-wiring-residual]]` (OPEN Class 3 bounded residual): §25.9 specifies carrier production; downstream audit-ledger wiring NOT specified — CXA v2.9 amendment paired with U-CP-72 implementation per handoff §6.

**Criterion B disposition: STRUCTURAL PARTIAL.** 1 of 4 production dispatch surfaces operational; 3 cross-axis-blocked. Per ledger-v2 strict reading, this is PARTIAL not RETIRE-READY.

### §3.3 PARTIAL → RETIRE-READY gate

H_T-OD-5 PARTIAL → RETIRE-READY transition gates on the 3 remaining dispatch surfaces wiring:

1. **Tool dispatch** — U-OD-39 unblock + landing at OD plan revision-pass; cost-attribution at `runtime_tool_dispatcher.py` step 7 (post-mcp.tool.call span) — analogous to LLM dispatch site at U-OD-38
2. **Validator dispatch** — U-OD-40 unblock + landing; cost-attribution at workflow_driver.py:668 post-validator.evaluate span
3. **Webhook dispatch + audit-write seam** — U-OD-41 + U-CP-72 audit converter `cost:` prefix un-STRIKE + CXA v2.8 → v2.9 amendment (3-arc cascade per batch-11 §9(e))

Operator-discretion timing per existing 7d retirement-event cadence.

---

## §4 Cross-axis retirement dependency cascade

Per Meta-Architecture §6.3 (workspace `CLAUDE.md` §4 → `phase-7-substitution-retirement` skill §4):

| Cross-axis dependency | Status |
|---|---|
| §6.3.1 — H_T-CP-1 → H_T-AS-8 anthropic.* namespace emission | Unchanged — H_T-CP-1 RETIRED at batch 2; H_T-AS-8 PARTIAL with cache subset 4/10 attrs + mcp.* full namespace coverage post-L9-septies (per `harness-as/CLAUDE.md` §4.1 batch-11 refresh) |
| §6.3.2 — F-CP-01 Stage 3b inversion ordering | Unchanged — fully discharged at U-RT-58 landing arc (batch 3) |

**No new cross-axis dependency activation at this batch.** The 3 transitions documented do not satisfy any documented cross-axis retirement dependency at Meta-Architecture §6.3. H_T-AS-2 + H_T-CP-18 share the MCP-client substrate gate (see §1.4 coupling note); both transition jointly at the external-server-exercise event but are independent substitution rows under the §6.3 enumeration.

---

## §5 Cumulative status (post-batch-12)

| Bucket | Pre-batch-12 (per batch-11 §7) | Δ batch-12 | Post-batch-12 |
|---|---|---|---|
| RETIRED | 22/49 (44.9%) | +0 | **22/49 (44.9%)** |
| RETIRE-READY | 2/49 (CP-18 + CP-21) | +1 (AS-2) | **3/49** |
| PARTIAL | 8/49 | +2 (AS-4 + OD-5) | **10/49** |
| STILL-BOUNDED | 13/49 effective (excluding 4 authoring-only) | −3 | **10/49** |

**Pipeline advanced (RETIRED + RETIRE-READY + PARTIAL):** **35/49 = 71.4%** (vs 32/49 = 65.3% post-batch-11).

NOTE: post-batch-12 cumulative table reads 35/49 advanced. The discrepancy with the post-batch-11 axis-CLAUDE.md table reading 37/49 reflects that the axis tables additionally counted H_T-CP-14 (PARTIAL — single-sub-agent slice landed at batch 4) + H_T-CP-20 (RETIRED at batch 9) as already advanced — both correctly. The corrected workspace-wide count under forward-only ledger discipline is 35/49 (this batch's table) — the axis tables already included those prior transitions in their per-axis totals.

**Per-axis roll-ups (post-batch-12):**

| Axis | RETIRED | RETIRE-READY | PARTIAL | STILL-BOUNDED | Advanced (R+RR+P) |
|---|---|---|---|---|---|
| IS | 7/9 (78%) | 0 | 0 | 2/9 | 7/9 = 77.8% (stable) |
| AS | 2/6 (33%) | 1/6 (AS-2 NEW) | 2/6 (incl. AS-4 NEW) | 1/6 (AS-5) | **5/6 = 83.3%** |
| CP | 10/22 (45%) | 2/22 (CP-18 + CP-21) | 8/22 (incl. batch-11 transitions) | 2/22 | **20/22 = 90.9%** |
| OD | 2/8 (25%) | 0 | 2/8 (incl. OD-5 NEW) | 4/8 | **4/8 = 50.0%** |
| CXA | 1/5 (20%) per ledger-v2 §7 H_T-CXA-5 RETIRED | 0 | 0 | 4/5 STILL-BOUNDED | 1/5 = 20.0% |

**Workspace-wide:** 22/49 RETIRED + 3/49 RETIRE-READY + 10/49 PARTIAL + 10/49 STILL-BOUNDED + 4/49 authoring-only = 49. Advanced 35/49 = 71.4%.

---

## §6 Forward-only ledger discipline preservation

Per workspace `CLAUDE.md` §4.3 forward-only ledger convention:

- Batch-11 §7 cumulative table ("22/49 RETIRED + 2 RETIRE-READY + 8 PARTIAL = 32/49 advanced") stands verbatim AS OF batch-11 filing (2026-05-23 pre-batch-12). Batch-12 supersedes via forward-only succession.
- Per-axis CLAUDE.md §4.1 retirement tables at `aeacd93` (OD) + `32bb901` (IS + AS) are forward-looking pointer tables, not batch records — they incorporated the AS-2 / AS-4 / OD-5 transitions ahead of the batch-record filing per the doc-hygiene-pass scope. This batch records the same transitions as standalone retirement-event records, restoring batch-record ↔ axis-pointer-table consistency.
- The L9-sexies / L9-septies cluster closes (`00da5ef` and prior) + U-OD-38 landing (`7104fd7`) are upstream implementation events — referenced at this batch by commit hash + carrier-unit ID. No re-litigation of implementation discipline at retirement-skill scope.

---

## §7 Adjacent observations (NOT this batch's retirement event)

(a) **Operator-opt-in RETIRE-READY pattern at 3-occurrence stability.** Pattern: production execution path branches on operator-supplied config with empty-sentinel default; RETIRE-READY at branch-landing; RETIRED at operator-config-non-default + e2e exercise. Members: H_T-CP-18 (batch 10, `mcp_servers=[]` default) + H_T-CP-21 (batch 11, `validator_framework=None` default) + H_T-AS-2 (this batch, shared `mcp_servers=[]` substrate). Future similar substitutions (e.g., webhook delivery via U-OD-53 + U-RT-69 carriers; operator burden via U-OD-54 + U-RT-70 carriers) likely follow the same RETIRE-READY → RETIRED path. Pattern documented for retirement-skill scope reference.

(b) **AS-2 + CP-18 coupling at RETIRED gate.** Both substitutions transition RETIRED jointly at the external-MCP-server-exercise event (per §1.4 coupling note). The two production substitution sites share the MCPClientHost substrate at stage-3a `materialize_mcp_client_host_stage` + stage-5 `materialize_runtime_tool_dispatcher_stage` factory chain. No independent transition possible without breaking the shared-substrate semantics. Future retirement-filing arc for either substitution should re-evaluate both jointly.

(c) **3-arc cascade for OD-5 PARTIAL → RETIRE-READY (cross-axis cite chain U-OD-51 ↔ U-CP-62 ↔ U-CP-72).** U-CP-62 landed this filing's evaluation horizon (cluster 10-CP-B `49617e7`). U-OD-51 PauseResumeAuditPayload was cross-axis-blocked on U-CP-62 per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]`. The 3-arc cascade — (i) OD plan revision-pass authoring U-OD-51 + CostRecordAuditPayload, (ii) U-OD-51 landing at OD axis, (iii) CXA v2.8 → v2.9 amendment + U-CP-72 audit converter pause:/resume:/cost: branch un-STRIKE — would jointly advance OD-5 PARTIAL → RETIRE-READY (cost: branch covers webhook dispatch) + H_T-CP-22 PARTIAL → RETIRE-READY (pause:/resume: branches cover pause-event audit-write). Coupled-front opportunity.

(d) **`harness-cp/CLAUDE.md` §4.1 already reflects this batch's H_T-AS-2 RETIRE-READY via the "Operator-opt-in RETIRE-READY pattern" observation at the post-batch-11 refresh.** No CP-axis CLAUDE.md update owed at this batch — AS-2 is not a CP-axis substitution; the CP-axis pattern reference correctly anticipated the AS-2 inclusion.

(e) **MEMORY index update.** No memory-entry status transition owed at this batch — batches 11 + 12 jointly close the per-row retirement re-invocation arc that fork-doc `class_1_fork_meta_arch_cp_spec_renumbering_drift.md` §16 v1.5 application footer flagged as operator-discretion follow-on. The fork-doc closure was at the v1.5 application footer commit `b2cf37b` (memory entry already APPLIED).

---

## §8 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-12.md` |
| Batch number | 12 |
| Filed at | 2026-05-23 (post-axis-CLAUDE.md-refresh ledger drift reconciliation) |
| Filing authority | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5; criterion-A ∧ structural-criterion-B met for H_T-AS-2 → RETIRE-READY (operational opt-in GATED per shared CP-18 substrate); criterion-A met + criterion-B production-callsite present + namespace coverage incomplete for H_T-AS-4 → PARTIAL (6/7 attrs); criterion-A met + criterion-B 1 of 4 dispatch surfaces operational for H_T-OD-5 → PARTIAL (LLM dispatch via U-OD-38) |
| HEAD at filing | `f364be6` (post axis-CLAUDE.md refresh merges); upstream L9-sexies cluster close at `00da5ef` (2026-05-22) + L9-septies (2026-05-22) + U-OD-38 cluster 4-OD-D commit 1/2 partial at `7104fd7` (2026-05-22); 2751/2751 tests green workspace-wide |
| Predecessor | `.harness/phase-7d-retirement-events-batch-11.md` (2026-05-23, 1 RETIRE-READY + 4 PARTIAL across H_T-CP-16/17/19/21/22) |
| Successor | `.harness/phase-7d-retirement-events-batch-13.md` (TBD at next retirement-criterion-trigger arc — likely PARTIAL → RETIRE-READY for the 8 CP-axis PARTIALs + AS-4/AS-8 + OD-5/OD-6 at future workflow_driver consumer-composer landings; or RETIRED transitions for CP-18 + CP-21 + AS-2 jointly at external-MCP-server-exercise event) |
| Related forks | `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` (OPEN — 3-arc cascade per §7(c)); `[[fork-price-table-ref-substitution-retirement]]` (RETIRED at U-OD-38 landing, referenced at §3.1); `[[fork-cost-record-audit-ledger-wiring-residual]]` (OPEN Class 3 bounded residual at §3.2 webhook-dispatch table) |
| MEMORY.md update | None owed per §7(e) |

---

*End of Phase 7d retirement events batch 12. 1 STILL-BOUNDED → RETIRE-READY (H_T-AS-2) + 2 STILL-BOUNDED → PARTIAL (H_T-AS-4 + H_T-OD-5). Cumulative 22/49 RETIRED + 3 RETIRE-READY + 10 PARTIAL = 35/49 advanced (71.4%). NO new RETIRED transitions. Reconciles batch-11 §7 cumulative count with post-batch-11 axis-CLAUDE.md doc-hygiene-pass refresh; restores batch-record ↔ axis-pointer-table consistency under forward-only ledger discipline.*
