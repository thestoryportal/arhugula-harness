# Implementation Plan — Harness Runtime v2.16

## Change-note (v2.15 → v2.16)

**Scope of revision.** Phase 7d retirement-batch-driven plan revision — NEW singleton cluster **L9-novies** appended at §1 below, containing a single new atomic unit **U-RT-86** (MCP-client external-server e2e). The unit enables the operational-close evidence required for joint retirement-batch close of **H_T-CP-18** (MCP integration + per-server trust + `mcp.*` consumption) and **H_T-AS-2** (Tool contract schema + namespacing + strict-mode) at a future batch-16 per the shared MCP-client substrate framing at `.harness/phase-7d-retirement-events-batch-12.md` §1.2 + the U-RT-82 close-pattern precedent at `.harness/phase-7d-retirement-events-batch-14.md` §6(a).

**Trigger.** Operator-ratified at session 2026-05-24 following:

1. `.harness/phase-7d-retirement-events-batch-15.md` §6(a) verification-shape generalization establishing the empirical-binding-chain discipline for operator-opt-in RETIRE-READY → RETIRED close events
2. Defensive audit at session 2026-05-24 confirming CP-18 + AS-2 binding chains pass all 3 stages (RuntimeConfig field + bootstrap stage factory + driver invocation path); no DOWN-classification needed
3. Absence of an MCP-client-equivalent of U-RT-82 in existing test scaffolding (`harness-runtime/tests/integration/` has `test_u_rt_82_memory_tool_filesystem_e2e.py` for Memory tool but no equivalent for MCP-client substrate)

Per the operator-opt-in close pattern catalogued at batch-14 §6(a), the dedicated test-infrastructure unit landed alongside the RETIRE-READY transition is exercised at close time. CP-18 + AS-2 RETIRE-READY closes (batches 10 + 12 respectively) did NOT land a dedicated U-RT-NN-equivalent at the time, because the L9-septies cluster (U-RT-71..U-RT-75, MCP-client substrate impl) was authored before the close-pattern discipline was catalogued. This plan revision retroactively adds the missing close-evidence unit.

**Spec authority chain.** Runtime spec v1.17 unchanged. AS spec v1.5 unchanged. CP spec v1.11 unchanged. CXA v2.8 unchanged. NO spec amendment triggered — C-RT-19 §14.9 (MCPClientHost) + C-RT-21 §14.11 (RuntimeToolDispatcher) + AS spec v1.5 §14.7 (mcp.* attribute namespace per ADR-D3 §1.1 #11) + Meta-Arch §7.7 X-AL-2 retirement criterion are all already filed at HEAD and sufficient for U-RT-86's `Implements` citation. The unit produces empirical evidence against existing contracts; it does NOT introduce a new contract surface (contrast with U-RT-82 which was paired with a newly-authored §14.12.6 sub-section because §14.12 was being authored fresh — U-RT-86 has no analogous spec authoring; X-AL-2 operational-MET semantics come from Meta-Arch + ledger-v2, not from a per-contract spec amendment).

**Plan shape preserved.** v2.15's entire body preserved verbatim — L9-octies cluster (U-RT-76..U-RT-82) intact, L9-septies cluster (U-RT-71..U-RT-75) intact, L9-sexies cluster intact, all prior unit bodies intact. NEW **L9-novies** cluster appended at §1 below containing exactly 1 atomic unit (U-RT-86). NO existing unit body change; NO AC change at any pre-v2.16 unit; NO DAG topology change at L9-octies / L9-septies / L9-sexies internal structure; ONLY a new cluster appended with internal-edge-only DAG (within-cluster deps on already-landed L9-septies carriers).

**Sections preserved verbatim from v2.15.** Entire v2.15 file body preserved AS-IS. §2 DAG topology delta preserved verbatim (no edge change at existing clusters). §3 coverage matrix preserved verbatim (one new row appended at v2.16 for C-RT-19 §14.9.1 / C-RT-21 §14.11 operational-close-evidence coverage — additive only). The v2.14 + v2.13 + v2.12 + ... + v2.0 + v2 chain preserved transitively.

**Status posture.** Proposed (v2.15) → **Proposed (v2.16)**. v2.16 is a retirement-batch-driven additive plan revision under FM-2 no-extension discipline — 1 new atomic unit appended; no unit removed; no AC body change at unaffected units; no contract addition (operational-close-evidence against existing contracts only).

**Cluster ordering.** L9-novies opens with U-RT-86 as L0-within-cluster (singleton cluster — no within-cluster predecessors). Cluster-boundary edges to L9-septies cluster carriers (U-RT-71, U-RT-72, U-RT-73, U-RT-74, U-RT-75) declared explicitly per §7 dependency discipline. NO edges from any pre-v2.16 unit into L9-novies (L9-novies is structurally terminal — produces evidence; no downstream unit consumes its output).

**Operator-discretion test-infrastructure shape (deferred to implementation-arc per FM-2).** U-RT-86 acceptance criteria specify operational properties (real bootstrap → real `ctx.mcp_client_host` → real driver invocation → real MCP tool call → `mcp.*` span emission verified). The test-substrate mechanism for spawning a spec-compliant MCP server in-test is **deferred to implementation discretion** per FM-2:

- **Mechanism α (in-process FastMCP test server):** spawn a FastMCP server in-process within the test module exposing a simple deterministic tool (e.g., an `echo` tool); transport stdio. Recommended default per workspace `CLAUDE.md` §3.1 stack commitment (`modelcontextprotocol/python-sdk` FastMCP host already a dep).
- **Mechanism β (subprocess-spawn external server):** spawn a separately-authored MCP server script as a subprocess. Higher fidelity to "external MCP server" semantics; higher test-infrastructure surface area.
- **Mechanism γ (gate on operator-supplied real MCP server):** mark test `@pytest.mark.skipif(not os.getenv("MCP_E2E_SERVER_URL"))` and exercise against an operator-supplied reachable server. Lowest test-infrastructure surface; gates close on operator providing the substrate.

Implementer SHOULD verify mechanism effectiveness empirically (per `[[advisor-before-substantive-work-for-cross-axis-blockers]]`) before landing — likely default to mechanism α (in-process FastMCP) for self-containment, with mechanism γ as a marker gate for operators who want to exercise against their actual deployment substrate. Mechanism selection per FM-2 no-extension discipline at implementation arc.

**Adjacent observations (NOT this revision's scope).**

(a) **The L9-septies cluster did not pre-author its close-evidence unit.** When the L9-septies cluster (U-RT-71..U-RT-75) landed at retirement-batch-10/12 (CP-18 + AS-2 RETIRE-READY closes), the operator-opt-in close pattern was still implicit (it was catalogued at batch-14 §6(a) explicitly only after the U-RT-82 close for CP-16). The L9-septies cluster therefore lacks a dedicated close-evidence unit analogous to U-RT-82. v2.16 corrects this asymmetry. Future cluster designs SHOULD pre-include a close-evidence unit (analogous to U-RT-82) when targeting an operator-opt-in RETIRE-READY substitution; per `[[h-t-cp-21-batch-15-down-classification]]` §6(a) verification-shape generalization, that's now part of the cluster-design discipline.

(b) **U-RT-86's binding chain depth matches U-RT-82's.** The defensive audit at session 2026-05-24 verified CP-18 + AS-2 have all 3 stages (RuntimeConfig.mcp_clients + materialize_mcp_client_host_stage U-RT-73 + RuntimeToolDispatcher TOOL_STEP dispatch). U-RT-86 exercises these production-bootstrapped surfaces end-to-end. Per `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` pattern, the close-evidence test should construct `HarnessContext` via the real bootstrap (NOT via `_FakeCtx` or `_MutableHarnessContext` test-locals) to ensure composer-depth parity with U-RT-82's empirical evidence shape.

(c) **Joint-close framing at batch-16.** A single passing U-RT-86 run satisfies criterion-B operational-MET for BOTH H_T-CP-18 (MCP-client substrate exercise) AND H_T-AS-2 (ToolContract enforcement at dispatch boundary), because the two substitutions share the MCP-client substrate per batch-12 §1.2. Batch-16 §1.1 evidence block can document the joint close in a single §1 row OR two parallel §1.X rows; filer-discretion at batch-16 authoring time.

(d) **No spec amendment owed.** Runtime spec v1.17 §14.9 + §14.10 + §14.11 contracts are sufficient. NO `RT-FAIL-MCP-*` fail-class addition required (existing fail classes cover MCP-client invocation paths). NO `mcp.*` attribute namespace amendment required (already filed at AS spec v1.5 §14.7). NO X-AL-2 retirement-implications sub-section authoring required — workflow-level X-AL-2 discipline from Meta-Arch §7.7 + ledger-v2 §2.1 is the authoritative source for operational-MET semantics, not a per-contract spec sub-section.

**Downstream absorption owed (post-v2.16).**

(a) Workspace `CLAUDE.md` §2.4 runtime plan row version bump (v2.15 → v2.16); unit count 83 → 84 (U-RT-00..U-RT-70 + U-RT-71..U-RT-82 + U-RT-86). Co-published this arc.
(b) Phase 7 cluster-open authorization for L9-novies at follow-on session per `phase-7-implementation` skill discipline. Cluster sequencing: L9-novies opens with U-RT-86 as the L0 entry-point + only-node.
(c) Implementation arc lands U-RT-86 (separate commit; not bundled with this plan-revision commit).
(d) Post-implementation: batch-16 retirement-events arc records joint H_T-CP-18 + H_T-AS-2 RETIRE-READY → RETIRED close per U-RT-86 e2e empirical exercise evidence.
(e) NO CXA v2.8 amendment owed (no cross-axis cascade at v2.16).
(f) NO CP / OD / AS plan amendments owed (no cross-axis cascade).
(g) NO runtime spec / AS spec / CP spec / OD spec revisions triggered.
(h) Retirement-batch absorption shape: batch-16 records joint H_T-CP-18 + H_T-AS-2 RETIRE-READY → RETIRED at U-RT-86 landing arc (post-impl). H_T-CP-21 PARTIAL preserved at batch-15 down-classification (separate scope per `[[fork-validator-composer-arc-stage-4-absence]]`).

---

## §1 — L9-novies cluster (NEW at v2.16)

### U-RT-86 — End-to-end test: MCP-client external server + real TOOL_STEP dispatch with `mcp.*` namespace verification

- **Implements:** Runtime spec **v1.17** §14.9.1 (MCPClientHost contract — operational execution path via stage-3a `materialize_mcp_client_host_stage` factory landed at U-RT-73) + §14.11 C-RT-21 (RuntimeToolDispatcher TOOL_STEP dispatch contract landed at U-RT-74/U-RT-75) + **AS spec v1.5** §14.7 (`mcp.*` attribute namespace 6-attribute schema per ADR-D3 v1.2 §1.1 + §1.8.1) + **AS spec v1.5** C-AS-02 + C-AS-11 (ToolContract schema + monotonic-ascent enforcement) + **Meta-Arch v1.5** §7.7 X-AL-2 retirement criterion (full RETIRED transition prerequisites for H_T-CP-18 + H_T-AS-2 operator-opt-in pattern per shared MCP-client substrate framing at `.harness/phase-7d-retirement-events-batch-12.md` §1.2 + the U-RT-82 close-pattern precedent at `.harness/phase-7d-retirement-events-batch-14.md` §6(a)).

- **Files:** `harness-runtime/tests/integration/test_u_rt_86_mcp_client_external_server_e2e.py` (NEW — e2e integration test module).

- **Test scope.** Single passing test run satisfies criterion-B operational-MET for BOTH H_T-CP-18 AND H_T-AS-2 simultaneously per shared-substrate framing. The test constructs `HarnessContext` via the real bootstrap with operator-supplied `mcp_clients` config non-empty + spec-compliant in-test MCP server + drives a workflow with a `TOOL_STEP` whose body invokes a real MCP tool call → `RuntimeToolDispatcher` consumes `ctx.mcp_client_host` → MCP-client substrate dispatches the tool against the in-test server → tool result returned → `mcp.*` span attrs emitted at the tool-call span → `ToolContract.output_schema` validation enforced at the dispatch boundary (AS-2 surface).

- **Test-substrate mechanism: implementer discretion (FM-2 per change-note above).** Implementer selects mechanism α (in-process FastMCP test server, recommended default) / β (subprocess-spawn external server) / γ (gate on operator-supplied `MCP_E2E_SERVER_URL` env var). The test infrastructure for spawning + teardown of the in-test server is authored as part of U-RT-86 implementation; pytest fixture pattern preferred for setup/teardown symmetry. The selected mechanism produces a single tool surface that the test workflow's `TOOL_STEP` invokes — a deterministic `echo`-style tool sufficient for span-attr verification.

- **Signatures:**
  - `async def test_mcp_client_external_server_e2e_tool_call_path()` — full bootstrap with `RuntimeConfig(deployment_surface=LOCAL_DEV, mcp_clients=[<test MCPClientConfig>])`; constructs a workflow with a single `TOOL_STEP` whose `step_payload` references the test server's tool ID + arg dict; executes the workflow via `harness_runtime.api.run(config, workflow_manifest)` (or the equivalent production entry point); asserts (i) the MCP tool was invoked at the in-test server (verified via server-side method-call recorder), (ii) the tool result was returned to the workflow step, (iii) `mcp.tool.call` span emitted with the AS spec v1.5 §14.7 6-attribute namespace, (iv) `ToolContract.output_schema` enforcement verified at the dispatch boundary (no `ToolContractMismatchError` raised on valid output; the test exercises the success path explicitly).
  - **Deterministic-tool fixture (eliminates LLM-behavior-class flakiness — though the test is not LLM-gated, the workflow step still needs a deterministic input/output shape).** The test uses a fixed `TOOL_STEP` payload that invokes the test server's `echo` tool with known args + verifies known output. No LLM in the loop at U-RT-86 (contrast with U-RT-82 which gated on Anthropic API); the test exercises ONLY the MCP-client substrate's tool dispatch path, not any LLM-driven tool-use decision-making.
  - `async def test_mcp_client_external_server_e2e_skip_without_substrate()` — separate test verifying the gating mechanism: marked `@pytest.mark.e2e` + `@pytest.mark.skipif(<mechanism-specific gate>, ...)` skip-decorator semantics. Mechanism α: skip if FastMCP test-server-spawn unavailable. Mechanism γ: skip if `MCP_E2E_SERVER_URL` env var unset.
  - Test gating: both tests marked `@pytest.mark.e2e` + mechanism-specific `@pytest.mark.skipif(...)` to allow CI to skip when the test substrate is unavailable. Explicit pytest fixture for server lifecycle (setup + teardown).

- **Depends on:** [U-RT-71, U-RT-72, U-RT-73, U-RT-74, U-RT-75 — L9-septies cluster carriers (RuntimeConfig schema extension + HarnessContext fields + stage-3a `materialize_mcp_client_host_stage` factory + stage-5 `materialize_runtime_tool_dispatcher_stage` factory + `RetryBreakerToolDispatcher` wire-up); all already landed at L9-septies cluster close `00da5ef` per `.harness/phase-7d-retirement-events-batch-10.md` §1.3].

- **ACs:**
  1. **Test runs with substrate available**: completes within reasonable timeout (~10s); the MCP tool was invoked at the in-test server (verified via server-side method-call recorder asserting the expected `(tool_id, args)` tuple); the tool result was returned to the workflow step (verified via workflow step's terminal output asserting the expected echo value).
  2. **Test runs without substrate available**: skips cleanly per mechanism-specific `@pytest.mark.skipif` gate (no false failure in CI).
  3. **`mcp.tool.call` span emitted with `mcp.*` 6-attribute namespace per AS spec v1.5 §14.7**: the test asserts the in-memory OTel span exporter captured a `mcp.tool.call` span with the 6 attributes (`mcp.tool.name`, `mcp.tool.invocation_id`, `mcp.client.name`, `mcp.transport`, `mcp.trust_level`, `mcp.blast_radius`) — exact attribute names verified against the spec's §14.7 declaration at HEAD; if spec attr names drift, the test should fail with a clear diagnostic naming the attribute mismatch.
  4. **AS-2 ToolContract enforcement verified at dispatch boundary**: the test asserts the `RuntimeToolDispatcher` invoked `ToolContract.output_schema` validation on the tool's return value (verified either via direct mock-recording of the validation call OR via observation of a typed `ToolContractMismatchError` on a separate negative-case sub-test that injects a schema-mismatched output — implementer discretion which sub-shape under FM-2).
  5. **Composer-depth parity with U-RT-82**: the test constructs `HarnessContext` via the **real** `harness_runtime.api.run(...)` (or equivalent production bootstrap entry point), NOT via `_FakeCtx` or `_MutableHarnessContext` test-locals. This is the critical AC enforcing the verification-shape discipline catalogued at batch-15 §6(a); test FAILS at design-review if the test scaffolding bypasses production bootstrap.
  6. **Test cleans up server process / in-process resources at teardown** (no test artifacts persisted between runs; no zombie subprocesses on β-mechanism selection).
  7. **Importable; pyright strict mode passes.**

---

## §2 — DAG topology delta (v2.15 → v2.16)

NEW L9-novies cluster appended with cluster-boundary edges to L9-septies cluster carriers. No edges into v2.15 units beyond the L9-septies dependency (L9-novies is structurally terminal — produces close-evidence; no downstream unit consumes its output). No edges from L9-octies / L9-sexies / earlier clusters into L9-novies.

Topological sort within L9-novies (acyclic verified — singleton cluster):

```
L9-novies (NEW at v2.16):
  L0-within-cluster: U-RT-86 (singleton — within-cluster deps: none;
                              cluster-boundary deps: U-RT-71, U-RT-72, U-RT-73, U-RT-74, U-RT-75
                              at L9-septies cluster)
```

**Cluster-boundary edges (NEW at v2.16):** 5 edges — `U-RT-86 ← U-RT-71`, `U-RT-86 ← U-RT-72`, `U-RT-86 ← U-RT-73`, `U-RT-86 ← U-RT-74`, `U-RT-86 ← U-RT-75`. All target the already-landed L9-septies cluster (no in-flight predecessor). No cycle risk.

**Cross-axis edges:** unchanged from v2.15. L9-novies adds ZERO new cross-axis edges — U-RT-86 exercises existing CXA-declared seams (mcp.* namespace per AS spec v1.5 §14.7 → already a declared cross-axis composition per CXA v2.8) but does NOT introduce a new CXA edge declaration. CXA v2.8 unchanged.

DAG verified acyclic via Kahn execution (delta layer): 5 new cluster-boundary edges consumed (all targeting already-landed L9-septies units); 0 new within-cluster edges (singleton); 0 new intra-L9-novies edges. No cycle path within L9-novies (singleton trivially acyclic); no cycle path into L9-novies (L9-septies is fully landed at HEAD, no back-edge possible).

---

## §3 — Coverage matrix delta (v2.15 → v2.16)

| Contract | Units covering | Change at v2.16 |
|---|---|---|
| C-RT-19 §14.9.1 MCPClientHost operational execution path (X-AL-2 retirement evidence for H_T-CP-18) | U-RT-73 (stage-3a factory landing — pre-v2.16), U-RT-86 (operational-close evidence via real bootstrap + production-path tool call) | NEW v2.16 ADD column (U-RT-86 appended) |
| C-RT-21 §14.11 RuntimeToolDispatcher TOOL_STEP dispatch surface (X-AL-2 retirement evidence for H_T-CP-18 + H_T-AS-2 joint exercise) | U-RT-74 + U-RT-75 (stage-5 factory + wrap-shape — pre-v2.16), U-RT-86 (operational-close evidence) | NEW v2.16 ADD column |
| AS spec v1.5 §14.7 `mcp.*` 6-attribute namespace span schema (X-AL-2 retirement evidence for H_T-AS-2 cross-axis emission) | (pre-v2.16 AS-axis coverage), U-RT-86 (runtime emission verification at production tool-call span) | NEW v2.16 ADD column |
| AS spec v1.5 C-AS-02 + C-AS-11 ToolContract schema + monotonic-ascent (X-AL-2 retirement evidence for H_T-AS-2 dispatch-boundary enforcement) | (pre-v2.16 AS-axis coverage), U-RT-86 (dispatch-boundary enforcement verification) | NEW v2.16 ADD column |
| Meta-Arch v1.5 §7.7 X-AL-2 retirement criterion (operational-MET semantics for operator-opt-in pattern) | U-RT-82 (Memory-tool close evidence — pre-v2.16), U-RT-86 (MCP-client close evidence) | NEW v2.16 ADD column for the joint CP-18 + AS-2 close evidence |
| All other v1.17 + v1.5 contracts | preserved verbatim from v2.15 coverage | (no change) |

**Coverage gap audit:** none surfaced at coherence pass.
- The unit's `Implements` line cites **only existing filed contracts** (runtime spec v1.17 + AS spec v1.5 + Meta-Arch v1.5) — no spec-shaped gap requiring `Phase_7_Class_N_Tension` filing per `implementation-planner` SKILL.md §2.
- The operator-opt-in close pattern's "test infrastructure landed alongside RETIRE-READY transition" obligation (per batch-14 §6(a)) is retroactively satisfied by U-RT-86 — the asymmetry between L9-octies (which pre-included U-RT-82) and L9-septies (which did not pre-include an equivalent) is documented at change-note adjacent observation (a) above.

**Cite-precision audit:** all v2.16 cites against runtime spec point at **v1.17** (latest filed version per `Project_Workflow_v1_8.md` §7.4 use-latest-version body-citation-alignment clause). Cross-axis cites: AS spec v1.5 §14.7 (`mcp.*` namespace) at latest filed version; Meta-Arch v1.5 §7.7 X-AL-2 at latest filed version. No invented `§` pins; no inferred cites.

**Already-landed cluster-boundary consumption cites:**
- `materialize_mcp_client_host_stage` factory at `harness-runtime/src/harness_runtime/bootstrap/factories/mcp_client_host_factory.py` (or equivalent — implementer verifies at impl arc) — consumed at U-RT-86 stage-3a binding-chain assertion
- `materialize_runtime_tool_dispatcher_stage` factory at `harness-runtime/src/harness_runtime/bootstrap/factories/runtime_tool_dispatcher_factory.py` — consumed at U-RT-86 stage-5 binding-chain assertion
- `RuntimeConfig.mcp_clients` field at `harness-runtime/src/harness_runtime/types.py:960` — consumed at U-RT-86 RuntimeConfig instantiation
- `ctx.mcp_client_host` field at production `HarnessContext` (stage 3a populated per U-RT-73) — consumed at U-RT-86 driver-invocation assertion

---

## §4 — Coherence pass

Per `implementation-planner` SKILL.md §5 step 9. Verifying U-RT-86 against the four sub-disciplines at §4:

1. **Atomicity (§3 four criteria).**
   - 3.1 Single coherent change ✓ — one e2e test module; one workflow exercise path; one set of binding-chain assertions
   - 3.2 Single focused session ✓ — implementation estimated at 1-3 hours including test-substrate authoring and pytest-fixture lifecycle
   - 3.3 Independently testable ✓ — once L9-septies cluster lands (already at HEAD), U-RT-86's AC can be verified standalone
   - 3.4 Coherent rollback boundary ✓ — one commit revertible without affecting any other unit

2. **Spec-traceability (§4.2).** Implements cites 5 contract sections by ID + section: C-RT-19 §14.9.1, C-RT-21 §14.11, AS spec v1.5 §14.7, AS spec v1.5 C-AS-02 + C-AS-11, Meta-Arch v1.5 §7.7. All verified against `design-substrate/` at HEAD. ✓

3. **Dependency-awareness (§4.3).** Declares 5 direct dependencies (U-RT-71, U-RT-72, U-RT-73, U-RT-74, U-RT-75) — all L9-septies cluster carriers already landed at HEAD. DAG acyclic per §2 Kahn verification. ✓

4. **Implementation-grade-detail (§4.4).** Names: file path (`harness-runtime/tests/integration/test_u_rt_86_mcp_client_external_server_e2e.py`); 2 test function signatures; 7 ACs each independently verifiable. Three test-substrate mechanism options enumerated for implementer FM-2 selection. Does NOT introduce a library/framework not named in the spec (FastMCP / modelcontextprotocol Python SDK already a workspace stack commitment per `CLAUDE.md` §3.1). Does NOT extend the specification. ✓

All four sub-disciplines pass at U-RT-86.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_16.md` |
| Version | v2.16 |
| Filing event | Retirement-batch-driven plan revision — NEW L9-novies singleton cluster (1 unit: U-RT-86) enables joint H_T-CP-18 + H_T-AS-2 RETIRE-READY → RETIRED close at follow-on batch-16 per shared MCP-client substrate framing at batch-12 §1.2 + U-RT-82 close-pattern precedent at batch-14 §6(a). Operator-ratified at session 2026-05-24 following batch-15 §6(a) verification-shape generalization. 2026-05-24 |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_15.md` (v2.15 substantive content preserved verbatim outside the additive L9-novies cluster authoring) |
| New units | 1 — U-RT-86 (e2e integration test: MCP-client external server + real TOOL_STEP dispatch + `mcp.*` namespace verification + AS-2 ToolContract enforcement) |
| Revised units | 0 at this plan (all v2.15 units preserved verbatim) |
| Cluster | NEW L9-novies cluster appended; L9-octies + L9-septies + L9-sexies + all earlier clusters preserved verbatim |
| Cross-axis dependencies | unchanged from v2.15. L9-novies adds 0 new CXA edges (U-RT-86 exercises existing CXA-declared `mcp.*` cross-axis emission per AS spec v1.5 §14.7 but does NOT introduce a new CXA edge declaration). CXA v2.8 unchanged. |
| DAG verification | Kahn-acyclic; 5 new cluster-boundary edges consumed (all targeting already-landed L9-septies cluster); 0 new within-cluster edges (singleton); ∅ remaining edges within L9-novies. |
| Coverage verification | U-RT-86 cites 5 contract sections (C-RT-19 §14.9.1 + C-RT-21 §14.11 + AS spec v1.5 §14.7 + AS spec v1.5 C-AS-02 + C-AS-11 + Meta-Arch v1.5 §7.7 X-AL-2); all verified against `design-substrate/` at HEAD; no spec-shaped gap surfaced; no `Phase_7_Class_N_Tension` filing required. |
| Mechanism discretion | α / β / γ enumerated at change-note "Operator-discretion test-infrastructure shape" section + unit body "Test-substrate mechanism" sub-section. Implementer selects per FM-2 no-extension discipline at implementation arc (recommended default mechanism α in-process FastMCP per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` verification). |
| Retirement-batch absorption owed | batch-16: joint H_T-CP-18 + H_T-AS-2 RETIRE-READY → RETIRED at U-RT-86 landing arc per shared MCP-client substrate framing at batch-12 §1.2 + close-pattern at batch-14 §6(a). H_T-CP-21 PARTIAL preserved at batch-15 (separate scope per `[[fork-validator-composer-arc-stage-4-absence]]`). |
| Date | 2026-05-24 |
