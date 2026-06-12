# Capability-Completion Inventory v1 — land all units before the quality sweep

**Authored:** 2026-06-11 · **Posture:** mode-agnostic (process-substrate; grounds `design-substrate/` + `harness-*/src/` + `.harness/` at HEAD `9c38b91`; authors only this `.harness/` file). **Authority:** operator strategic directive 2026-06-11 (below). Grounding verified at HEAD by direct read — not trusted from register prose (per advisor).

---

## 0. The operator's strategic decision (what this inventory serves)

> Operator, 2026-06-11: *"Running devex, code review and simplification now on the harness when all coding and dependencies aren't complete means that once these are finally closed I will need to run this again, a token cost I don't want to spend twice. So I would rather work through all blocked and deferred units even if this requires planning sweeps to make decisions for their producer, disciplines, vendors, corpus/embedding models or run e2e tests… now to land all units fully. Then run the devex, code review and simplification pass on the fully developed harness."*

**Consequence — track re-sequenced.** The closure track's quality phase **R-CL-Q1** (DevEx + code-review + simplification) moves to **last**, run once on the complete harness. All capability units land first. **This supersedes the `R-PM-1` "after R-CL-Q1" sequencing recorded minutes earlier (#499/#500)** — as a capability, R-PM-1 now moves *before* Q1.

**Honest framing up front:** the "many blocked and deferred units" is, on grounding, a **small, well-characterized set**. Nearly every forward surface is already RESOLVED *with live e2e proof* (see §1). The genuine open set is ~11 units, and a few of them hit **committed-constraint walls** (I-6, cleared-contract immutability) where "just land it" forces an ADR-level decision, not a planning-sweep pick. Some may remain bounded-residuals regardless of spend — **but the reorder is still directionally right**: running Q1 once on ~90%-complete code beats running it now and again later.

---

## 1. What is ALREADY fully landed (the reconciliation — don't re-open)

Verified against `.harness/post-phase-8-forward-register.md` Tier B (kept current through batch-56 / R-830 Neon / R-412 E2B 2026-06-08) + the live substitution ledger (54/54 RETIRED):

| Surface | Units | State |
|---|---|---|
| IV Multi-LLM | R-300 routing activation (declarative live) + R-300 second-provider (live Anthropic→OpenAI #281, live Ollama #283) | ✅ live |
| V Deployment | R-410 TIER_2 Docker, R-411 TIER_3 gVisor (Lima VM), R-412 TIER_4 E2B full-VM, R-420 SELF_HOSTED daemon+collector, R-421 MANAGED_CLOUD (E2B+GCP+Cloud Run), R-430 tail-keep, R-440 secrets selector | ✅ live e2e |
| VI Multi-tenant | R-500 multi-tenant live proof, R-008 redaction (toggle + tokenization) | ✅ live |
| IX External | R-800 real external MCP, R-810 Files API (live Anthropic), R-820 managed_agents (live), R-830 memory backends (SQLite + S3 + Neon managed-DB, all live) | ✅ live |
| CXA | CXA-1 (batch-56), CXA-3 (batch-54), CXA-4 (batch-53), CXA-5 (batch-3) | ✅ retired |

**These are NOT in scope for capability-completion** — they are done, most with live paid/infra-gated proofs already run. Re-opening them would be over-excavation.

---

## 2. The genuine open set (what is NOT fully landed) — per-unit inventory

Categories: **[C-now]** Claude-closeable now (small build/doc) · **[design]** design-phase fork/spec first, then Claude-closeable build (X-AL-3) · **[wall]** committed-constraint collision (ADR-level operator decision; not a planning-sweep pick) · **[vendor]** needs an operator vendor/corpus/paid/infra decision · **[hollow]** may remain a bounded-residual regardless of spend.

| # | Unit | What it needs to fully land | Category | Attainability | Recommended disposition |
|---|---|---|---|---|---|
| 1 | **Sandbox tier→driver production selection** (R-410-family, unbundled from P2) | Design the tier/tech/provider→driver **selection contract** (canonical vocab + per-server driver config + factory registry), then wire `runtime_tool_dispatcher_factory` to select the driver from the resolved tier. Drivers already exist (R-410/411/412). HEAD-verified gap: `runtime_tool_dispatcher.py:343` defaults to in-process; factory passes no driver; no registry. **Real security-posture gap.** | **[design]** then [C-now] | **High** — drivers exist; this is the selection seam. | **BUILD (design-fork first).** Highest-value real gap. |
| 2 | **R-PM-1 full prompts management** | Net-new design: no system-prompt route at dispatch today (`cp_shared_types.py:89` `ProviderAgnosticPayload` frozen/ADR-F1, no `system` field). Design-phase spec/ADR covering all 4 layers (injection + selection + versioning/authoring + per-tier governance); injection-mechanism sub-fork (bounded `HarnessContext` channel vs foundational ADR-F1 change). Then 4-layer impl. | **[design]** then [C-now], large | **High** (operator-confirmed full-stack) | **BUILD (design-fork first).** Largest single arc. |
| 3 | **P1 LLM_AS_ROUTER routing layer** | ~~A faithful router-model layer makes an **async** call, but `infer()`/`route()` (U-CP-03/U-CP-05) are cleared sync contracts. Widening them = Class 1 fork. Then bind a router model.~~ **CONFIRM-DEFERRED (operator Option C, 2026-06-11).** Grounding correction: `infer()` is **already async** at HEAD (`routing_core_surface.py:129`); the r-cl-p1 "infer() is sync" premise was stale. Only `route()`/`LayerDecisionFn` are sync. Today only `_declarative_echo` is bound (`llm_dispatch.py:533`) → Layer 3 cleanly falls through, **no behavior missing**. | **[design]** then defer | n/a (deferred) | **DEFER — documented bounded-residual** (Layer-3 twin of #7 EMBEDDING; arc #6 fork `class_2_fork_llm_as_router_layer3_contract_shape_vs_defer.md`). Re-open trigger: real routing traffic + operator router-model + hot-path-cost decision → build via **Reading B** (resolve at the async `infer()` layer; preserves ADD §5.3.3 determinism boundary). |
| 4 | **B-10 / R-100 AC#2 — `api.run` provider-ping** | ~~The bootstrap pings ≥1 provider regardless of step kind, so the tool-only `api.run` e2e is skipif-gated on a live provider. Making the ping conditional on an inference step = **Class 1 fork (C9⊥C11:** fail-fast reliability ⊥ tool-only ergonomics). Then the api.run TOOL_STEP e2e runs unconditional.~~ | **[design]** (C9⊥C11 fork) | Reachable if the fork opens | **✅ RESOLVED (R-CC-1 arc #4).** Reading B (operator-ratified 2026-06-12; C9⊥C11 probe-resolved — inference-need is statically determinable, council ruled hollow). Runtime spec **v1.47 §2.1** authors the `requires_inference` predicate; stage 3a skips provider construction for tool-only workflows; the AC#2 e2e is now provider-free/unconditional in CI. Fork `class_1_fork_api_run_unconditional_provider_ping_for_tool_only_workflows.md`; clearance `Spec_Harness_Runtime-v1_47-cleared-2026-06-12.md`. |
| 5 | **P5 CXA edges U-CP-12 / U-CP-52** | Two phase-2 CXA edges deferred (X-AL-3 per U-RT-35, not-rescued at P5). Need a design decision to wire (or confirm permanent-defer). | **[design]** (X-AL-3) | Reachable if opened; bounded | **GROUND → fork-or-confirm-defer.** |
| 6 | **P2 engine-recovery → durable-resume / crash-recovery** (+ SAVE_POINT) | **BUILD — hand-roll (operator Gate A, 2026-06-11).** Preserve I-6 (no vendored engine). Design-first: define the **engine-layer durable-resume / crash-recovery semantic** (resume a workflow from the #475 `JournalEnginePauseResumeSubstrate` after a process restart) — distinct from the already-working workflow-layer `PauseResumeProtocol` — and wire a **real production caller** (`api.run` resume-from-journal) so it is NOT a fake producer. Then bind #475 into the factory in place of `Deterministic`, resolve the journal PathClass placement *with* the consuming driver. | **[design]** then [C-now], large + **risk: caller must be real** | **Reachable** — the durable substrate (#475) exists; the missing piece is the real durable-resume semantic + caller | **BUILD (design-fork first).** Operator chose hand-roll over residual. |
| 7 | **P1 EMBEDDING routing layer** | Needs a **trained per-workload corpus + an embedding model**. Today the layer correctly falls through (no corpus → confidence never exceeds threshold → spec-correct no-op). | **[vendor]** + **[hollow]** | n/a (deferred) | **DEFER — documented bounded-residual (operator Gate B, 2026-06-11).** Re-open trigger: real routing traffic + an operator-supplied embedding model. No behavior missing today. |
| 8 | **P3 live multi-tier e2e** | Run the full-workflow `api.run` echo-MCP multi-tier e2e. Needs a live provider — **free via local Ollama** (no paid call) or a paid provider with operator auth. (Composes with #4 — the provider-ping fork gates the tool-only path.) | **[vendor]** (paid) or free-Ollama | High (free path) | **BUILD via free Ollama path** (default; no paid call) once #4 lands. |
| 9 | **P3 redaction collector-boundary proof** | Prove MULTI_TENANT redaction at the OTLP-collector boundary. The R-420 self-hosted collector stack **already exists** (`deploy/self-hosted-local/`). Needs a redaction-specific e2e recipe through it. | **[C-now]** (infra already provisioned) | High | **BUILD.** |
| 10 | **P3 cost / U-RT-49 — `RunResult.cost_attribution`** | ~~Wire the aggregate rollup into `RunResult.cost_attribution` (empty at `api.py:949`).~~ **CONFIRM-DEFERRED (grounded R-CC-1 arc #6, HEAD `643f4a8`).** Strike-scope resolved: **NOT [C-now]**. Per-span cost IS produced in production (`cost_attribution_llm_dispatch.py:197` + `_tool_dispatch.py` fire `compute_per_attempt_cost`; records reach the audit ledger via U-OD-41 `cost:` action_id) — but `RunResult.cost_attribution` **sourcing is UNSPECIFIED**: the chain is stateless + step-body-owned (no run-level `SpanCostRecord` accumulator in runtime/cp), and U-RT-49's Q2 shared-carrier was explicitly deferred to "when non-linear topologies land (7c CXA seam)". **R-CL-P5 already ratified `RunResult.cost_attribution=()` as a U-RT-49-bounded residual** — building a ledger read-back wire would re-litigate that with no re-open trigger. The stale api.py comment ("U-OD-21 HALTED Class 1") is doubly-stale (U-OD-21 RESOLVED 2026-05-16; was an inaccurate attribution per `fork_u_rt_49_cost_attribution_invocation_underspec.md`). | **[design]** / bounded | n/a (ratified-bounded) | **CONFIRM-DEFER** — consistent with R-CL-P5. Re-open trigger = a spec decision on RunResult cost-sourcing (read-back vs run-level accumulator) + first non-linear topology. |
| 11 | **P2 HITL OQ-6 timeout degradation** | ~~Thin-latent: add the config path + a scenario.~~ **CONFIRM-DEFERRED (grounded R-CC-1 arc #6, HEAD `643f4a8`): producer-gated, NOT [C-now].** The timeout-degradation **decision** is fully landed + pure (`RuntimeHITLPlacementRegistry.on_timeout` → `on_hitl_timeout` → `TimeoutDegradationKind`, C-CP-21 §21.6 per-persona-tier table). But `on_timeout` has **4 test callers and ZERO non-test callers** — the L8 LOOP_INIT wall-clock-wait loop the docstring says "waits `invocation.timeout` ms then invokes this method" **does not exist as a producer** (`hitl_placement.py:32` "the actual wall-clock wait lives at L8 LOOP_INIT"; `materialize_hitl_placement_stage` consumes no config at HEAD). Adding a `timeout_seconds` config field without that producer loop is hollow (`[[r-cxa-seam-wiring-is-producer-discovery]]`). OQ-5/7 remain **hollow** (no composition scenario). | **[hollow/producer-gated]** | n/a | **CONFIRM-DEFER all OQ.** Re-open trigger = a real HITL wall-clock-wait orchestrator (the L8 timeout loop) lands as a production producer. |
| — | P5 §2.3-vs-§2.1 CXA count | Class 3 doc-fidelity residual (CXA aggregate). Doc-only. | **[C-now]** doc | High | **FIX in the Q-phase doc pass** (or fold into #1's design arc). |

---

## 3. The two committed-constraint walls (genuine operator decisions — NOT planning-sweep picks)

The operator authorized "decisions for vendors/disciplines" — that does **not** auto-authorize overriding a committed ADR/invariant. Two units land here and must be surfaced as explicit forks with a recommendation:

- **Gate A — P2 engine-recovery vs I-6 (no-vendor reliability-framework discipline). → OPERATOR CHOSE: HAND-ROLL (2026-06-11).** Build a real in-house event-sourced/journal recovery substrate (preserving I-6 — no vendored engine), *with a real production caller*. Reframed to avoid the fake-producer trap: the genuine engine-layer semantic is **durable-resume / crash-recovery** (resume a workflow from the #475 journal after a process restart), with `api.run` resume-from-journal as the real caller. Design-first (X-AL-3): define the engine-layer pause/resume semantic + the production trigger before wiring. (Operator overrode the "accept-residual" recommendation — recorded faithfully.)
- **Gate B — P1 EMBEDDING corpus/embedding-model. → OPERATOR CHOSE: DEFER (2026-06-11).** Documented bounded-residual; the layer correctly falls through today (no behavior missing). Re-open trigger: real routing traffic + an operator-supplied embedding model. (Matches recommendation.)

---

## 4. Recommended program sequence (after the gates are answered)

Design-forks first (they unblock their builds), highest-value real gaps first:

1. **Sandbox tier→driver selection contract** (#1) — design the selection contract → wire the factory registry. *Closes the real security gap; drivers already exist.* **← arc #1 (next).**
2. **R-PM-1 full prompts management** (#2) — design-phase spec/ADR (4 layers + injection-mechanism fork) → 4-layer impl. *Largest arc; operator-confirmed.*
3. **Engine-layer durable-resume / crash-recovery** (#6, operator Gate A = hand-roll) — design the engine-layer pause/resume semantic + a real `api.run` resume-from-journal caller → bind #475. *In-house, preserves I-6.*
4. **api.run provider-ping fork** (#4) → then **P3 live multi-tier e2e** (#8, free Ollama) — *unblocks the tool-only path + the multi-tier proof together.*
5. ~~**LLM_AS_ROUTER contract-widening fork** (#3)~~ — **CONFIRM-DEFERRED at arc #6 (operator Option C, 2026-06-11)**; skip unless the re-open trigger fires (real routing-intelligence traffic + operator router-model + hot-path-cost decision → build via Reading B). See item #3 + §6.
6. **P5 CXA edges** (#5) — ground → fork-or-confirm-defer.
7. **Claude-closeable cleanups** (in parallel / as encountered): P3 redaction proof (#9) — **the surviving genuine [C-now]**; ~~cost rollup (#10)~~ + ~~HITL OQ-6 (#11)~~ **both confirm-deferred at arc #6 grounding** (#10 ratified-bounded by R-CL-P5; #11 producer-gated — see §2); CXA doc count.
8. **THEN R-CL-Q1** — DevEx + code-review + simplification, once, on the complete harness. Then Q2→Q3→Q4→D1→C1.

**Attainability honesty:** with the operator's Gate A (hand-roll) + Gate B (defer) calls, the only remaining bounded-residual is **#7 EMBEDDING** (deferred until real routing traffic — no behavior missing) plus the genuinely-hollow **P2 OQ-5/7** (no composition scenario). Everything else is buildable (most design-fork-first). So Q1 will run on a harness that is capability-complete *except* the embedding optimization (which has nothing to optimize yet) — the C1 completeness-critic accounts for it. **#6 is now a real build, not a residual** (operator chose hand-roll); its risk is keeping the production caller real (durable-resume), not the I-6 wall.

---

## 5. Status

- **Gates answered (2026-06-11):** Gate A = **hand-roll** engine-recovery (durable-resume); Gate B = **defer** embedding. Recorded in §2/§3/§4.
- **Arc #3 re-aimed (2026-06-12):** entry-grounding falsified item #6's *engine-layer* framing — the `engine_recovery_loop` has **no production producer** and the only candidate (workflow-layer DURABLE_ASYNC pause) is forbidden by the ratified forward-register line 181 (`[[r-cl-p2-engine-recovery-grounding]]`). Class-2 scoping fork `class_2_fork_engine_durable_resume_no_production_producer.md` → operator chose **Option 1: re-aim to the workflow-layer durable-resume gap** (real producer fires today at `workflow_driver.py:793/948`; resume mechanism already exists at `execute_workflow(pause_snapshot=)`; gaps = harness-owned durable persistence + an `api.resume` public surface). Gate A's *hand-roll durable-resume* intent is preserved; line 181 unviolated (engine-layer #475 stays the ratified CXA-2 bounded-residual, reused by *pattern* not binding). Design doc: `r-cc-1-arc-3-workflow-durable-resume-design-v1.md` (advisor-reviewed; data-stateless execution model → position-only resume is correct). Cascade: runtime-spec `api.resume` amendment (design-fork-first) → durable `PauseSnapshot` store → impl + restart-proof e2e.
- **This turn:** grounded map + gate calls + roadmap re-sequencing (Q1→last; R-PM-1→capability before Q1; P-units re-opened under this program; embedding documented-defer). **No unit built** (per advisor: map → operator's calls → execute next).
- **Owed next:** start **arc #1 — sandbox tier→driver selection contract** (design-fork first per X-AL-3). Workflow is an option for the broad design-fork cluster; not gated on it.
- **Grounded at HEAD `9c38b91`. Cites resolved by direct read this session.**

---

## 6. R-CC-1 arc-execution log (forward-only; appended per arc)

- **arc #1 (#503):** sandbox tier→driver production selection — DONE.
- **arc #2 / R-PM-1 (#505–#511):** full prompts-management 4-layer cascade — DONE / R-PM-1 RESOLVED.
- **arc #3 (#512 re-aim, #513+#514):** workflow-layer durable-resume (`api.resume` + `JournalWorkflowPauseStore`) — DONE.
- **arc #4 (#515):** inference-conditional provider bootstrap (R-100 AC#2) — DONE.
- **arc #5 (#516):** live multi-tier `api.run` e2e (item #8) — DONE.
- **arc #6 (2026-06-11, this session):** **item #3 LLM_AS_ROUTER — CONFIRM-DEFERRED** (operator Option C; fork `class_2_fork_llm_as_router_layer3_contract_shape_vs_defer.md`). Grounding also reclassified the "parallel Claude-closeable lane": **#10 cost + #11 HITL OQ-6 both confirm-deferred** (#10 ratified-bounded by R-CL-P5; #11 producer-gated — `on_timeout` has zero non-test callers), and the stale premises in the r-cl-p1 doc (`infer()` "is sync") + api.py cost comment ("U-OD-21 HALTED") were corrected. **Net survivor of the lane: #9 P3 redaction collector-boundary proof** (genuine [C-now] e2e proof; infra at `deploy/self-hosted-local/` exists). **Corollary:** R-CL-P3's cost sub-part is bounded (not closeable); the dashboard's "#10 closes an R-CL-P3 sub-part" is corrected.
- **Owed next after arc #6:** **#9 P3 redaction collector-boundary proof** (Phase-7 e2e; docker-gated — probe `docker ps` first). Then #5 P5 CXA edges (U-CP-12/U-CP-52: ground → fork-or-confirm-defer) → THEN R-CL-Q1 on the now-capability-complete harness (capabilities #1–#8 landed; #3/#7 deferred-by-design, #10/#11 ratified-bounded).
