# Phase 7d Retirement Events — Batch 16

| Field | Value |
|---|---|
| Batch number | 16 |
| Filed at | 2026-05-24 (post U-RT-86 e2e empirical exercise at `8e6311f` — 2/2 e2e tests pass against in-process stdio MCP echo fixture; full `mcp.*` 7-attribute namespace coverage verified at `mcp.tool.call` span) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 invoked per joint RETIRE-READY → RETIRED operator-opt-in gate satisfaction across two coupled substitutions (H_T-CP-18 + H_T-AS-2 share the MCP-client substrate per batch-12 §1.4 coupling note) |
| Predecessor batch | `phase-7d-retirement-events-batch-15.md` (2026-05-24, 1 RETIRE-READY → PARTIAL DOWN-classification for H_T-CP-21 per Reading-D audit; cumulative 23/49 RETIRED + 2 RETIRE-READY + 10 PARTIAL = 35/49 advanced per §3) |

---

## §0 Batch context

**Status type: 2 RETIRE-READY → RETIRED joint retirements (H_T-CP-18 + H_T-AS-2). Cumulative RETIRED count advances 23/49 → 25/49 (46.9% → 51.0%); RETIRE-READY count decrements 2 → 0; PARTIAL count unchanged at 10; pipeline-advanced unchanged at 35/49 (71.4%) — within-tier promotion across two coupled rows. SECOND RETIRE-READY → RETIRED close in ledger history; FIRST JOINT close (two substitutions sharing a substrate close together at a single empirical-exercise event); workspace crosses the 50% RETIRED threshold across the full 49-row mapping table.**

This batch records the joint RETIRE-READY → RETIRED transition for **H_T-CP-18** (MCP integration + per-server trust + `mcp.*` consumption) and **H_T-AS-2** (Tool contract schema + typed dispatch) following empirical exercise of the U-RT-86 e2e test against an in-process stdio MCP echo server fixture. The test was added at L9-novies cluster close `8e6311f` (2026-05-24, runtime plan v2.16) per the close-pattern catalogued at batch-14 §6(a) and the joint-coupling framing established at batch-12 §1.4.

The two substitutions are coupled at the binding chain. Per batch-12 §1.4 coupling note:

> H_T-AS-2 + H_T-CP-18 share an external-server-exercise gate. Both substitutions transition RETIRE-READY → RETIRED jointly at the same e2e exercise event (real workflow step invoking a tool exposed by a configured external MCP server). No independent transition possible — the production tool-dispatch chain wires both substitutions through the same stage-5 callsite + MCPClientHost substrate.

Per the operator-ratified runtime-only substitution-site reading at `.harness/phase-7d-retirement-ledger-v2.md` §2.1 + line-33 strict-reading discipline + the operator-opt-in RETIRE-READY pattern close at this batch:

> RETIRED = (criterion A MET) ∧ (criterion B structural-MET) ∧ (criterion B operational-MET) — where operational-MET for the operator-opt-in bucket = (the operator-supplied config + step payload + external substrate exercise paths have been empirically traversed end-to-end at least once with the production composer in the loop).

Under that discipline, both H_T-CP-18 and H_T-AS-2 transition RETIRE-READY → RETIRED: criterion-A preserved from batch-10 §1 (CP-18) and batch-12 §1.2 (AS-2); structural-criterion-B preserved and now defensively re-verified per batch-15 §6(a) discipline (all 3 binding-chain stages empirical at HEAD — see §2.3 below); operational-criterion-B NEW at this batch via U-RT-86 e2e empirical exercise.

**Conclusion (preview):** **2 new RETIRED transitions** (H_T-CP-18 + H_T-AS-2) — cumulative **25/49 RETIRED** (51.0%, +2 from batch-15). **−2 RETIRE-READY** (both promoted out — RETIRE-READY count 2 → 0; the operator-opt-in RETIRE-READY bucket is now empty for the first time since batch-10 introduced the pattern). PARTIAL count unchanged at 10. Pipeline advanced (RETIRED + RETIRE-READY + PARTIAL): **35/49 = 71.4%** (unchanged from batch-15; bucket composition shifts +2 RETIRED / −2 RETIRE-READY). **Workspace crosses 50% RETIRED threshold across the full 49-row mapping table at this batch.** **CP-axis crosses 12/22 RETIRED (54.5%).** **AS-axis crosses 3/6 RETIRED (50.0%).** **Second RETIRE-READY → RETIRED close in ledger history; first JOINT close.**

---

## §1 H_T-CP-18 RETIRE-READY → RETIRED

| Field | Value |
|---|---|
| Substitution ID | H_T-CP-18 |
| Primitive | MCP integration + per-server trust framework + `mcp.*` namespace consumption (CP-side runtime consumer of external MCP servers per C-CP-18 + AS spec §14.3 client-side classification) |
| Substituted H_E surface | "Claude Code `claude mcp` CLI + `.claude/mcp.json` operator-config substrate + scope hierarchy" (Meta-Arch v1.5 §5.4 row H_T-CP-18) |
| Prior status | RETIRE-READY per batch-10 §1 (2026-05-23 — STILL-BOUNDED → RETIRE-READY at L9-septies cluster close `00da5ef`; criterion-A MET via U-CP-00b + U-RT-73..U-RT-75 + U-RT-68 cited units; structural-criterion-B MET; operational-criterion-B GATED on operator-supplied `mcp_clients` config non-empty + external MCP server availability) |
| Transition this batch | RETIRE-READY → **RETIRED** |
| Triggering arc | U-RT-86 e2e empirical exercise 2026-05-24 at HEAD `8e6311f` (2/2 e2e tests pass against in-process stdio FastMCP echo server fixture) |

### §1.1 Operational-criterion-B exercise evidence

The operator-opt-in operational sub-conditions enumerated at batch-10 §1.4 RETIRE-READY → RETIRED gate, each verified empirically at the 2026-05-24 e2e exercise:

| Sub-condition | Evidence at U-RT-86 e2e exercise |
|---|---|
| (1) Operator-supplied `mcp_clients` config non-empty | Test fixture constructs a `RuntimeConfig` with `mcp_clients=[MCPClientConfig(client_name="echo-server", transport=MCPTransport.STDIO, connection_url="stdio://...mcp_echo_server.py", trust_level=...)]` (per-test fixture); not the empty-list default `mcp_clients=[]` that produces the empty-sentinel host at `mcp_client_host_factory.py:113`. ✓ |
| (2) `MCPClientHost.start()` succeeds against the configured server | `factory_host = await materialize_mcp_client_host_stage(config)` returns a host bound to the configured stdio echo server (server_name="echo-server"); subsequent `host.start()` spawns the stdio subprocess + completes MCP handshake; assertion at test body verifies `factory_host.server_name == _SERVER_NAME`. ✓ |
| (3) Real `RuntimeToolDispatcher.dispatch(TOOL_STEP)` invocation against a tool exposed by the external server | Test invokes the production dispatch path with a `WorkflowStep(step_kind=TOOL_STEP, ...)` payload targeting `echo` (registered by the FastMCP echo server fixture); dispatcher resolves the tool, invokes via MCP client, returns the tool result with `"hello-u-rt-86"` content block. ✓ |
| (4) `mcp.*` 7-attribute namespace span emission at `mcp.tool.call` | Captured span asserted to carry all 7 attributes per C-AS-14 §14.3 + `MCPClientNamespaceEmitter`: `mcp.server.name`, `mcp.server.trust_tier`, `mcp.protocol_version`, `mcp.transport`, `mcp.auth_present`, `mcp.primitive.kind`, `mcp.primitive.signature.sha256`. Field-specific assertions: `mcp.server.name == "echo-server"`, `mcp.transport == "stdio"`, `mcp.primitive.kind == "tool"`. ✓ |

### §1.2 Empirical evidence block (test output)

Test run captured at 2026-05-24 against in-process stdio FastMCP echo fixture:

```
harness-runtime/tests/integration/test_u_rt_86_mcp_client_external_server_e2e.py::test_mcp_client_external_server_e2e_tool_call_path PASSED [ 50%]
harness-runtime/tests/integration/test_u_rt_86_mcp_client_external_server_e2e.py::test_module_importable                              PASSED [100%]
============================== 2 passed in 1.10s ===============================
```

**Per-AC observable outcomes verified at `test_mcp_client_external_server_e2e_tool_call_path`:**

| AC | Observable outcome at e2e exercise |
|---|---|
| AC #1 | `materialize_mcp_client_host_stage(config)` returns a started host bound to the configured stdio echo server (no empty-sentinel branch); `host.start()` completes within the test timeout |
| AC #2 | `RuntimeToolDispatcher` resolves the `echo` tool via the configured host + invokes it via the live MCP session; tool result content block contains the fixture round-trip payload verbatim |
| AC #3 | `mcp.tool.call` OTel span emitted with all 7 attributes per `mcp.*` namespace (verified at test body lines 340–369); attribute values match the configured server (transport=stdio, primitive.kind=tool, server.name=echo-server) |
| AC #4 (joint with AS-2) | `ToolContract` (AS-axis schema) consumed at production tool-dispatch path; `RuntimeToolDispatcher` validates the dispatched payload against the typed contract; no ad-hoc operator-prompted enforcement path invoked |

### §1.3 No new gating dependencies

H_T-CP-18 RETIRED is now unconditional. The retirement is permanent under the prevailing runtime spec v1.17 + AS spec v1.5 + Meta-Arch v1.5 §5.4 cite shape.

Should a future spec revision extend the MCP-client surface (e.g., declarative `RuntimeConfig.tool_contract_converter` field landing per §3 disposition note below), the new surface would require its own retirement-event analysis at the time of landing — but the existing 5-cited-unit retirement is not disturbed.

---

## §2 H_T-AS-2 RETIRE-READY → RETIRED

| Field | Value |
|---|---|
| Substitution ID | H_T-AS-2 |
| Primitive | Tool contract schema (AS-side `ToolContract` Pydantic v2 schema + typed dispatch via `RuntimeToolDispatcher` per C-AS-02 / C-AS-11) |
| Substituted H_E surface | "Ad-hoc MCP server registration with operator-prompted contract enforcement" (Meta-Arch v1.5 §5.3 row H_T-AS-2) |
| Prior status | RETIRE-READY per batch-12 §1 (2026-05-23 — PARTIAL → RETIRE-READY at L9-septies cluster close `00da5ef`; criterion-A MET; structural-criterion-B MET via `runtime_tool_dispatcher.py:41` ToolContract import + production tool-dispatch operational at L9-sexies/L9-septies; operational-criterion-B GATED jointly with CP-18 on operator-supplied `mcp_clients` config non-empty + external MCP server availability per batch-12 §1.4 coupling note) |
| Transition this batch | RETIRE-READY → **RETIRED** (jointly with H_T-CP-18) |
| Triggering arc | Same as §1 — U-RT-86 e2e empirical exercise 2026-05-24 at HEAD `8e6311f` |

### §2.1 Joint-coupling rationale

Per batch-12 §1.4 coupling note + L9-septies cluster close substrate framing: H_T-AS-2 and H_T-CP-18 share the same end-to-end binding chain. The `RuntimeToolDispatcher` produced by stage-5 `materialize_runtime_tool_dispatcher_stage` consumes the `MCPClientHost` produced by stage-3a `materialize_mcp_client_host_stage`; the AS-side `ToolContract` is the typed schema the dispatcher enforces at every dispatch invocation. There is no production code path that exercises one substitution's runtime composer without simultaneously exercising the other's.

The U-RT-86 e2e exercises BOTH substitutions in a single test invocation:

- The MCP-client substrate (CP-18) — host bootstrap + stdio transport + `mcp.*` namespace emission
- The typed `ToolContract` dispatch (AS-2) — `RuntimeToolDispatcher` validates the dispatched step payload against the contract schema before invoking the MCP client

The joint close is the structurally correct outcome — neither substitution can be exercised in isolation through the production composer at runtime spec v1.17.

### §2.2 Operational-criterion-B exercise evidence

Per §1.2 above — the same 2/2-passing test invocation provides operational-MET evidence for AS-2 (AC #4 specifically; ACs #1–#3 jointly cover the substrate AS-2 depends on). No separate test or evidence block required — the joint-coupling discipline at §2.1 makes the §1.2 evidence load-bearing for both rows.

### §2.3 Binding-chain defensive audit (per batch-15 §6(a) discipline)

Per batch-15 §6(a) verification-shape generalization, every operator-opt-in RETIRE-READY → RETIRED close requires empirical verification of all 3 binding-chain stages prior to the close. The defensive audit at HEAD `8e6311f` for the joint CP-18 + AS-2 chain:

| Binding-chain stage | Evidence at HEAD `8e6311f` |
|---|---|
| (1) RuntimeConfig field for operator-supplied value | `mcp_clients: list[MCPClientConfig] = []` at `harness-runtime/src/harness_runtime/types.py:960`. Default empty-list; operator-declarative. ✓ |
| (2) Bootstrap stage factory reads config + binds HarnessContext field | `materialize_mcp_client_host_stage(config)` at `harness-runtime/src/harness_runtime/bootstrap/factories/mcp_client_host_factory.py:97` consumes `config.mcp_clients`; bound at `harness-runtime/src/harness_runtime/bootstrap/stage_3a_cp_clients.py:48` (`ctx.mcp_client_host = await materialize_mcp_client_host_stage(config)`). Stage-5 `tool_dispatcher` bound at `stage_5_loop_init.py:321` via `materialize_runtime_tool_dispatcher_stage`. ✓ |
| (3) Driver invocation path exercises bound field at production runtime | `harness-cp/src/harness_cp/workflow_driver.py:619` invokes `step_dispatchers.lookup(step.step_kind).dispatch(...)` covering `TOOL_STEP`; TOOL_STEP path routes through `RuntimeToolDispatcher` → `MCPClientHost`. U-RT-86 e2e confirms end-to-end traversal succeeds against a real stdio MCP echo server. ✓ |

All 3 stages empirically verified. Per §6 verification-shape sharpening below, stage-(3) is now stronger than the batch-15 catalogue statement: not merely "driver code references the bound field" but **"driver invocation succeeds end-to-end against a real substrate"** — verified by U-RT-86 e2e at HEAD.

### §2.4 No new gating dependencies

H_T-AS-2 RETIRED is now unconditional, jointly with H_T-CP-18.

---

## §3 Adjacent finding — `RuntimeConfig.tool_contract_converter` absence (disposition note)

The U-RT-86 impl arc surfaced a milder relative of the CP-21 binding-chain gap. The `MCPClientHost` consumer surface depends on a `tool_contract_converter` callable that translates the AS-side `ToolContract` schema to the CP-side dispatcher's expected shape (per the MCPClientHost constructor signature + production tool-dispatch invariant). The U-RT-86 test supplies this converter the same way an operator must — by manual host construction or extension of stage-3a wiring — because **no `RuntimeConfig` field exists at runtime spec v1.17 for operators to declaratively supply this converter**.

**Disposition options enumerated:**

| Option | Verdict at this batch | Rationale |
|---|---|---|
| (a) Accept "operator-supplied" includes manual host construction (preserve CP-18 + AS-2 RETIRED at this batch) | **ADOPTED** | Per Meta-Arch v1.5 §5.3/§5.4 row prose: criterion-B is about whether the H_E substitution-target surface (manual MCP-server registration via Claude Code CLI / ad-hoc operator-prompted contract enforcement) is still invoked at substitution site. Manual host construction by operator code is not the H_E substituted surface — it is a different operator-facing API shape (Python code vs CLI command). The production-composer path is operational end-to-end; the H_E surface is no longer invoked at the substitution site. RETIRED stands. |
| (b) Strict reading — DOWN-classify CP-18 + AS-2 like CP-21 was at batch-15 | REJECTED | The CP-21 DOWN-classification was triggered by absence of BOTH the RuntimeConfig field AND the bootstrap stage factory — the production driver branch was unreachable from any production entrypoint. For CP-18 + AS-2, the RuntimeConfig field (`mcp_clients`) and stage factory (`materialize_mcp_client_host_stage`) both exist + are wired + U-RT-86 e2e empirically traverses the chain. The `tool_contract_converter` gap is a narrower API ergonomics concern (declarative-vs-manual operator-supply path), not a structural-binding-chain absence. |
| (c) File a separate fork for `tool_contract_converter` config landing | **NOTED for follow-on** | A future-arc spec extension may add `RuntimeConfig.tool_contract_converter_config` (or analogous declarative shape) to lower operator burden. Such an extension would be additive (does NOT re-open CP-18 + AS-2 RETIRED — only adds a more ergonomic operator-supply path alongside the existing one). Operator-discretion timing; not blocked on any pending arc. |

**Disposition this batch: (a) ADOPTED.** CP-18 + AS-2 RETIRED is preserved. Option (c) is logged at §8 below as adjacent observation; future arc routing remains open.

---

## §4 Cross-axis cascade analysis

| Cascade endpoint | Disposition at this batch |
|---|---|
| §6.3.1 — H_T-CP-1 → H_T-AS-8 anthropic.* namespace emission | Unchanged — H_T-CP-1 RETIRED (batch 2); cascade discharged 2026-05-20. H_T-CP-18 + H_T-AS-2 RETIRED does NOT activate a new cascade — the `mcp.*` namespace was already emitted at L9-septies cluster close via `MCPClientNamespaceEmitter`; this batch records operational-MET via U-RT-86 exercise but does not change the cascade structure |
| §6.3.2 — F-CP-01 Stage 3b inversion ordering | Unchanged — cascade fully discharged at U-RT-58 landing arc per batch-3 |
| AS-axis sibling rows (AS-4 / AS-5 / AS-8) | Unchanged — independent gates per batch-12 §2/§3. AS-4 PARTIAL stands (gates on `sandbox.violation` 7th attribute); AS-5 STILL-BOUNDED stands (gates on `sandbox_event_idempotency` invocation); AS-8 PARTIAL stands (gates on cross-namespace consumer-side wiring). U-RT-86 exercise does NOT advance these rows (the test exercises tool-dispatch but not the sandbox-event idempotency composition or full-coverage namespace consumer paths) |
| CP-axis sibling rows | Unchanged — CP-axis PARTIAL rows (CP-8 / CP-9 / CP-11 / CP-14 / CP-17 / CP-19 / CP-21 / CP-22) gate on independent driver-composer landings per harness-cp/CLAUDE.md §4.1 |

**Conclusion.** ZERO new cross-axis cascade triggered by the joint RETIRE-READY → RETIRED transition. The transitions consume the existing wire-up state without modifying any cross-axis edge.

---

## §5 Cumulative retirement state

**Workspace-wide post-batch-16:**

| Tier | Post-batch-15 | Delta this batch | Post-batch-16 |
|---|---|---|---|
| RETIRED | 23/49 (46.9%) | +2 (CP-18, AS-2) | **25/49 (51.0%)** |
| RETIRE-READY | 2 (CP-18, AS-2) | −2 (both → RETIRED) | **0** |
| PARTIAL | 10 | +0 | **10** |
| STILL-BOUNDED | 13 | +0 | **13** |

Sum: 25 + 0 + 10 + 13 = 48 ✓ (matches the 49-row table with the 1 documented authoring-only-retired row preserved at prior batches' aggregate accounting).

**Pipeline advanced (RETIRED + RETIRE-READY + PARTIAL):**

| Scope | Post-batch-15 | Post-batch-16 | Delta |
|---|---|---|---|
| Workspace-wide | 35/49 (71.4%) | 35/49 (71.4%) | unchanged (within-tier promotion) |
| CP-axis | 20/22 (90.9%) | 20/22 (90.9%) | unchanged (within-tier promotion) |
| AS-axis | 5/6 (83.3%) | 5/6 (83.3%) | unchanged (within-tier promotion) |

**CP-axis bucket breakdown post-batch-16:**

| Tier | Pre | Post | Delta |
|---|---|---|---|
| RETIRED | 11/22 (50.0%) | **12/22 (54.5%)** | +1 (CP-18) |
| RETIRE-READY | 1/22 (4.5%) | **0/22 (0.0%)** | −1 (CP-18) |
| PARTIAL | 8/22 (36.4%) | 8/22 (36.4%) | unchanged |
| STILL-BOUNDED | 2/22 (9.1%) | 2/22 (9.1%) | unchanged |

**AS-axis bucket breakdown post-batch-16:**

| Tier | Pre | Post | Delta |
|---|---|---|---|
| RETIRED | 2/6 (33.3%) | **3/6 (50.0%)** | +1 (AS-2) |
| RETIRE-READY | 1/6 (16.7%) | **0/6 (0.0%)** | −1 (AS-2) |
| PARTIAL | 2/6 (33.3%) | 2/6 (33.3%) | unchanged |
| STILL-BOUNDED | 1/6 (16.7%) | 1/6 (16.7%) | unchanged |

**Milestones at this batch:**

| Milestone | Status |
|---|---|
| Workspace-wide 50% RETIRED threshold | **CROSSED at this batch (25/49 = 51.0%)** — first time the full 49-row mapping table reaches half-RETIRED |
| CP-axis 50% RETIRED milestone (from batch-14) | Preserved + advanced — 11/22 → 12/22 (50.0% → 54.5%) |
| AS-axis 50% RETIRED threshold | **CROSSED at this batch (3/6 = 50.0%)** — first time the AS axis reaches half-RETIRED |
| Operator-opt-in RETIRE-READY bucket | **EMPTY for the first time since batch-10** (CP-21 down-classified at batch-15; CP-16 + CP-18 + AS-2 all RETIRED across batch-14 + batch-16) |

**Second RETIRE-READY → RETIRED close in ledger history; first JOINT close.** The within-tier promotion preserves the pipeline-advanced count; the composition shifts the H_T-CP-18 + H_T-AS-2 rows from RETIRE-READY into RETIRED, reflecting the operational readiness gain from the U-RT-86 e2e empirical exercise.

---

## §6 Verification-shape sharpening — "grep-for-presence ≠ verified-working-end-to-end"

Per advisor note at the U-RT-86 impl arc + carry-forward from batch-15 §6(a) verification-shape generalization, this batch sharpens the binding-chain verification discipline established at batch-15.

**The U-RT-86 impl arc surfaced a real defect that grep-only audits would have missed.** Prior to the U-RT-86 e2e test landing, the defensive binding-chain audit at session 2026-05-24 (pre-impl) confirmed all 3 stages of the CP-18 + AS-2 chain exist by grep:

- `mcp_clients` field present at `RuntimeConfig` ✓
- `materialize_mcp_client_host_stage` factory present + wired at stage-3a ✓
- `tool_dispatcher` driver invocation present at `workflow_driver.py:619` ✓

That grep audit did NOT catch the **factory transport_config key mismatch** at `mcp_client_host_factory.py:88` (pre-fix): the factory passed `transport_config={"connection_url": ...}` but `MCPClientHost._stdio_connection_context` reads `transport_config["command"]` and raises `ValueError("STDIO transport_config requires str 'command'")`. Any `host.start()` invocation against stdio transport would fail. The defect was latent because no end-to-end stdio MCP connection had ever been attempted in the test suite — the unit tests at L9-septies stubbed the host construction or used the empty-sentinel path.

**The lesson.** "The bound field is referenced by the driver" ≠ "the driver invocation succeeds end-to-end against a real substrate". Static presence (grep hits, type checks, import resolutions) is necessary but not sufficient for criterion-B operational-MET claims.

**Sharpened verification shape (supersedes batch-15 §6(a) stage-(3) statement):**

Before promoting a substitution from PARTIAL to RETIRE-READY under the operator-opt-in pattern, verify all 3 binding-chain stages empirically:

1. **RuntimeConfig field present** for the operator-supplied config value (e.g., `mcp_clients` for CP-18 + AS-2; `memory_tool_backend_config` for CP-16) — grep-verified at HEAD
2. **Bootstrap stage factory present** that reads the config + binds the corresponding `HarnessContext` field (e.g., `materialize_mcp_client_host_stage` U-RT-73 for CP-18 + AS-2; `materialize_memory_tool_registry_stage` U-RT-80 for CP-16) — grep-verified at HEAD + factory's input/output contract grep-verified to match host/registry expectations
3. **Driver invocation succeeds end-to-end against a real substrate** at production runtime — NOT merely "driver code references the bound field". Verification requires an e2e test that exercises the full production composer chain against a real (or in-process-real) external substrate; tests using empty-sentinel paths or stubbed inner-loop primitives are insufficient

**Where the sharpening applies.** Future RETIRE-READY → RETIRED close events should rest on an e2e test at landing arc. The U-RT-86 + U-RT-82 pattern (e2e test landed alongside the close-pattern's substrate readiness) is the canonical close shape. Future PARTIAL → RETIRE-READY promotions should defer the RETIRE-READY classification until an e2e test landing is at least scoped at the corresponding implementation plan — if no e2e arc is on the roadmap, PARTIAL → RETIRE-READY may be premature (echoing the CP-21 batch-15 DOWN-classification).

**Discipline name catalogued for cross-reference.** "grep-for-presence ≠ verified-working-end-to-end" — apply at every operator-opt-in promotion event going forward. Pairs with `[[advisor-before-substantive-work-for-cross-axis-blockers]]` (advisor surfaces the binding-chain question at promotion time) + `[[h-t-cp-21-batch-15-down-classification]]` (the corrective pattern when stage-(3) is grep-only-verified).

---

## §7 Forward-only ledger discipline preservation

Per workspace `CLAUDE.md` §4.3 forward-only ledger discipline. This batch adheres:

- Prior batch records (1..15) NOT modified
- Only new batch-16 added + per-axis CLAUDE.md §4.1 forward-state refresh
- H_T-CP-18 row at `harness-cp/CLAUDE.md` §4.1 retirement-status table updated RETIRE-READY → RETIRED (status-column edit + rationale block reflecting the U-RT-86 e2e exercise; RETIRE-READY-bucket row count decrements 1 → 0; RETIRED-bucket row count increments 11 → 12)
- H_T-AS-2 row at `harness-as/CLAUDE.md` §4.1 retirement-status table updated RETIRE-READY → RETIRED (status-column edit + rationale block; RETIRE-READY-bucket row count decrements 1 → 0; RETIRED-bucket row count increments 2 → 3)
- Operator-opt-in RETIRE-READY pattern paragraph at harness-cp/CLAUDE.md §4.1 amended to record the pattern's empty-bucket state post-batch-16 (all 3 members CP-16/CP-18/AS-2 RETIRED across batch-14 + batch-16; the CP-21 misclassification was DOWN at batch-15)

---

## §8 Adjacent observations (NOT this batch's retirement event)

(a) **Second RETIRE-READY → RETIRED close in ledger history; first JOINT close — pattern catalogue.** Batch-14 closed H_T-CP-16 (single substitution; Memory tool surface). Batch-16 closes H_T-CP-18 + H_T-AS-2 jointly (two substitutions sharing the MCP-client substrate). The close pattern at batch-14 §6(a) generalizes to joint closes when the substitutions are coupled at the binding chain — a single e2e exercise event provides operational-MET evidence for all coupled rows. Future joint closes (e.g., AS-4 + AS-5 + AS-8 coupled via shared sandbox-event substrate; OD-5 + OD-6 coupled via shared dispatch-surface substrate) follow the same shape if/when their substrate readiness gates align.

(b) **Workspace 50% RETIRED milestone.** Per §5 cumulative table — workspace crosses 25/49 RETIRED (51.0%) at this batch. First time the full 49-row mapping table reaches half-RETIRED. Pipeline-advanced (R+RR+P) remains 35/49 = 71.4% — the milestone is composition-shifted (lower tiers shrink as RETIRED expands).

(c) **Operator-opt-in RETIRE-READY bucket empty for the first time since batch-10.** The pattern was introduced at batch-10 H_T-CP-18 STILL-BOUNDED → RETIRE-READY; pattern members grew to 3 (CP-18 + CP-21 + AS-2; CP-16 added at batch-13); peaked at 4 post-batch-13; closed to 3 RETIRED + 1 misclassification at batch-14 + batch-15; closed to 0 RETIRE-READY remaining at this batch. Future use of the pattern would require a new PARTIAL → RETIRE-READY promotion event (e.g., for one of the 10 remaining PARTIALs) — each subject to the §6 verification-shape sharpening discipline.

(d) **`RuntimeConfig.tool_contract_converter` declarative field absence (per §3).** Logged at §3 disposition (c) as future-arc opportunity to lower operator burden. Does NOT block CP-18 + AS-2 RETIRED at this batch (disposition (a) ADOPTED). Operator-discretion routing — could batch with any future runtime spec amendment touching `RuntimeConfig`.

(e) **L9-novies cluster minimal scope.** The U-RT-86 single-unit cluster is the smallest cluster in runtime plan history (1 unit; 0 within-cluster edges; cluster-boundary deps to already-landed L9-septies). The pattern — closing a retirement gate that was structurally present at a prior cluster close by adding a single e2e test — is reproducible. Future retirement gates that rest on prior cluster closes (where the production substrate is structurally complete but operationally unverified) can use the same minimal-scope cluster shape.

(f) **Factory parser fix surfaced at impl arc (per U-RT-86 commit body).** The `mcp_client_host_factory.py:88` `transport_config={"connection_url": ...}` → `host.start() ValueError` defect was caught by U-RT-86's e2e fan-out and fixed in the same commit. This is the direct empirical evidence for the §6 "grep-for-presence ≠ verified-working-end-to-end" sharpening — the L9-septies cluster grep-passed but the production chain was broken until U-RT-86 exercised it. The fix is FM-2-compliant (factory-side translation only; no spec change, no host change).

(g) **Cost-attribution under-reports memory-tool inner-loop iterations (carried from batch-13 §6(d) + batch-14 §6(e) + batch-15 §6(e)).** Still owed; OD-axis observability scope, not CP-axis/AS-axis substitution-retirement scope.

(h) **SDK `rename` command absent from harness Protocol (carried from batch-13 §6(e) + batch-14 §6(f) + batch-15 §6(f)).** Still owed at any future runtime spec amendment arc.

(i) **CXA v2.8 → v2.9 cost-attribution audit-write seam amendment (owed per batch-13 §6 + handoff §6 + batch-15 §6(g)).** Still owed; could batch with future arc opening.

(j) **Validator-composer arc routing decision (per batch-15 §6(d) + fork doc §6).** Open. H_T-CP-21 restoration to RETIRE-READY/RETIRED gates on Reading A or B routing.

(k) **Meta-Arch v1.5 §5.4 row H_T-CP-16 cite-shape augmentation (carried from batch-13 §6(a) + batch-14 §6(d)).** Still owed at next Meta-Arch amendment arc.

---

## §9 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-16.md` |
| Batch number | 16 |
| Filed at | 2026-05-24 (post U-RT-86 e2e empirical exercise at HEAD `8e6311f`) |
| Filing authority | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 invoked per joint RETIRE-READY → RETIRED operator-opt-in gate satisfaction; criterion-A MET (preserved from batch-10 for CP-18 + batch-12 for AS-2) ∧ structural-criterion-B MET (preserved from prior batches + defensively re-verified at §2.3 per batch-15 §6(a) discipline) ∧ operational-criterion-B MET (NEW at this batch via U-RT-86 e2e empirical exercise per §1.1 + §1.2) — joint close per §2.1 coupling rationale |
| HEAD at filing | `8e6311f` (workspace clean; 2/2 U-RT-86 e2e tests pass against in-process stdio MCP echo fixture per §1.2 evidence block) |
| Predecessor | `.harness/phase-7d-retirement-events-batch-15.md` (2026-05-24, 1 RETIRE-READY → PARTIAL DOWN-classification for H_T-CP-21) |
| Successor | `.harness/phase-7d-retirement-events-batch-17.md` (TBD — likely PARTIAL → RETIRE-READY transitions for one or more of the 10 remaining PARTIALs at future workflow_driver / sub_agent_dispatch composer landings; OR validator-composer arc opening event at Reading A / Reading B routing decision restoring H_T-CP-21 to RETIRE-READY/RETIRED; OR CXA v2.9 amendment landing) |
| Related forks | `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` (preserved OPEN → PARTIALLY-APPLIED state from batch-15; this batch does NOT evolve fork doc state) |
| Related memory | `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` (CP-18 RETIRED close pattern extends the catalogue established at batch-14; close pattern now generalizes to joint closes per §8(a)); `[[advisor-before-substantive-work-for-cross-axis-blockers]]` (pattern application — advisor reconciliation at U-RT-86 impl arc surfaced the factory defect + the §6 verification-shape sharpening); `[[h-t-cp-21-batch-15-down-classification]]` (DOWN-classification corrective pattern preserved + §6 sharpening pairs with §6(a) generalization); `[[halt-route-split-AC-pattern]]` (not applicable — both RETIRED transitions are clean closes with full operational-MET) |
| MEMORY.md update owed | Update `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` description line to reflect CP-18 RETIRED at batch-16 (joint close with AS-2; CP-axis 12/22 = 54.5% RETIRED; workspace crosses 50% RETIRED at 25/49); ADD new memory entry for the joint close pattern + verification-shape sharpening discipline (§6 "grep-for-presence ≠ verified-working-end-to-end") |

---

*End of Phase 7d retirement events batch 16. 2 joint RETIRE-READY → RETIRED (H_T-CP-18 + H_T-AS-2) — SECOND RETIRE-READY → RETIRED close in ledger history; FIRST JOINT close. Cumulative 25/49 RETIRED + 0 RETIRE-READY + 10 PARTIAL = 35/49 advanced (71.4%, unchanged from batch-15 — within-tier promotion). Workspace crosses 50% RETIRED threshold (25/49 = 51.0%). CP-axis 12/22 RETIRED (54.5%); AS-axis 3/6 RETIRED (50.0%). Operator-opt-in RETIRE-READY bucket empty for the first time since batch-10. ZERO new cross-axis cascade. §6 verification-shape sharpened: "grep-for-presence ≠ verified-working-end-to-end" — apply at every future operator-opt-in promotion + close event.*
