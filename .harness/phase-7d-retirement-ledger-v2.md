# Phase 7 sub-phase 7d — substitution retirement ledger (v2 — second pass)

**Filed:** 2026-05-20, Phase 7 sub-phase 7d (second pass against Phase 2 runtime closure). **Skill:** `phase-7-substitution-retirement`.
**Predecessor:** `.harness/phase-7d-retirement-ledger.md` (v1, partial pass, 2026-05-17 — `[[phase-7-bootstrap-status]]`).
**Trigger:** Phase 2 runtime closure 2026-05-20 at `43500bf` (per `[[phase-2-runtime-close]]`); 1152 tests on main (runtime 654 + CP 498).

---

## §0 Reading order + relation to v1

v1 ruled: every runtime-active substitution = bounded-residual because *no H_T runtime existed* — condition B was universally unverifiable.

v2 ruled: H_T runtime exists at `43500bf`. Condition B is now evaluable per substitution. **This pass evaluates B for all 45 v1-bounded-residuals against actual runtime code** under the operator-ratified **runtime-only substitution-site reading** (§2.1) and produces a per-substitution verdict that distinguishes RETIRE-READY / PARTIAL / STILL-BOUNDED.

v1 §1 (4 authoring-only retirements) is **unchanged** at v2 — those retirements were design-phase-close events, not runtime-evaluable.

v1 §2 (45 bounded-residuals) is **superseded** by this document's §3–§7.

v2 does NOT modify any code; it is a verification ledger. Per-axis `CLAUDE.md` substitution-table updates to reflect retirement events are a separate documentation-hygiene pass (filed as outstanding work at §9).

---

## §0.5 Snapshot supersession note (2026-05-27 refresh)

**This document is a frozen verification snapshot dated 2026-05-20 at commit `43500bf`.** It is NOT a live per-substitution status table. Per-row verdicts at §3–§7, cascade dispositions at §8, eligible-retirements list at §9.1, "within reach" list at §9.2.4, and closure counts at §9.3 reflect the 2026-05-20 evaluation only.

For current per-substitution status, read:

1. **Per-axis `CLAUDE.md` §4.1** at `harness-{is,as,cp,od}/CLAUDE.md` — these are refreshed at each batch close and carry the authoritative live status table for their axis.
2. **Batch records** at `.harness/phase-7d-retirement-events-batch-{1..N}.md` — append-only event records; the latest filed batch is `batch-19` (2026-05-26, H_T-AS-4 PARTIAL → RETIRED, cumulative 28/49 RETIRED).
3. **Cross-axis cascade re-evaluations** are recorded at the batch in which the gating retirement filed (e.g., §6.3.2 OD-2 → CXA-5 cascade closure recorded at batch-3, NOT at this snapshot's §8.2 which remains "DORMANT" against the 2026-05-20 evaluation).

Row text at §3–§7 is **preserved verbatim** per forward-only ledger discipline. Surfaced supersession sites discovered during the 2026-05-27 audit pass are catalogued at §11 below — they document deltas without rewriting the original verdicts.

---

## §1 Methodology

**Operator decision recorded.** Substitution-site reading clarified by operator at v2 pass (this session): the runtime-only reading. Condition B is met when the runtime-invoked workflow no longer routes through the H_E surface for the substituted primitive. Operator-authoring lane is out of scope — operators may still invoke `Bash(git commit)` / `Read .harness/state.jsonl` directly for authoring activities without that counting as "H_E surface still invoked at substitution site." The strict reading (which would regress most IS retirements to PARTIAL) was rejected; the operator-authoring lane is treated as a separate concern not gating 7d closure.

**Per-substitution sweep shape.**
1. Read Meta-Architecture §5.{2,3,4,5,6} verbatim for each substitution's substitution-site + retirement-criterion text.
2. Locate H_T runtime module(s) implementing the H_T contract.
3. Grep `harness-runtime/src/` for production execution-path invocation of the H_T primitive (the production execution path being `harness_runtime.api.run` → `bootstrap.run_bootstrap` → `harness_cp.workflow_driver.execute_workflow` → `_shutdown`).
4. Apply 4-bucket verdict.

**Critical correction relative to a naive reading.** Bootstrap-materializes-but-driver-never-invokes ≠ RETIRE-READY. The carrier landing + composer materialization satisfies condition A (cited unit IDs landed) but is silent on condition B. RETIRE-READY requires the production execution path to invoke the primitive end-to-end at runtime — not merely for the primitive to exist as a library.

**Sub-agent fan-out.** Verification delegated across 4 parallel general-purpose sub-agents (one per axis) plus one final CXA sub-agent. Each sub-agent produced a per-substitution verdict table with file:line evidence; this ledger synthesizes those reports.

---

## §2 Aggregate verdict

| Axis | RETIRE-READY (B) | PARTIAL (~B) | STILL-BOUNDED (¬B) | Count |
|---|---|---|---|---|
| IS | 6 | 0 | 2 | 8 |
| AS | 1 | 1 | 3 | 5 |
| CP | 1 | 3 | 17 | 21 |
| OD | 0 | 2 | 5 | 7 |
| CXA | 0 | 1 | 3 (+CXA-5 STILL-BOUNDED-DOWNSTREAM) | 4 |
| **Aggregate** | **8** | **7** | **30** | **45** |

Plus 4 authoring-retired (v1 §1, unchanged) = 49 substitutions total.

**Net retirement progress relative to v1:** +8 RETIRE-READY recordings ready to file (IS-1, IS-5, IS-6, IS-7, IS-8, IS-9, AS-1, CP-6).

---

## §3 IS axis (8 substitutions)

| ID | Primitive | Verdict | Reason (compressed) |
|---|---|---|---|
| H_T-IS-1 | Path-class registry + workflow-canonical path resolver | **RETIRE-READY** | `bootstrap/stage_1_is.py` step 1 `materialize_path_registry(...)`; `ctx.path_resolver` exposed downstream; no `CLAUDE.md`-convention path-class read at runtime |
| H_T-IS-2 | Artifact-tier registry + cross-tier traceability invariant | STILL-BOUNDED | Typed library exists (`harness-is/.../artifact_tier_registry.py`); zero bootstrap composer invokes `materialize_artifact_tier_registry`; cross-tier traceability invariant unenforced at append-time |
| H_T-IS-4 | Atomic deploy primitive (commit-grain reversibility) | STILL-BOUNDED | `verify_deploy_atomicity` is offline/on-demand verification only; H_T does NOT own the deploy act — `git add`/`git commit` remain operator `Bash(git *)`. C-IS-04 §4 defers commit-message annotation to operator |
| H_T-IS-5 | State-ledger entry shape (6-field idempotency-key carrier) | **RETIRE-READY** | `lifecycle/state_ledger.py` (`LedgerWriter.append`) typed-and-driver-invoked at `workflow_driver.py:401-407`; admin read path at `admin/inspect.py`; no `Bash(python -c)` / `Bash(cat >>)` invocation at runtime |
| H_T-IS-6 | Hash-chain integrity discipline | **RETIRE-READY** | `harness_is.entry_hash` owns in-process `hashlib.sha256` + JCS canonicalization (the H_T implementation, not the H_E `Bash(python -c)` substitution); chain-verify runs at stage_1_is reattach post-condition |
| H_T-IS-7 | T-perm-2 F2-layer read/write contract pair (JSONL composition) | **RETIRE-READY** | `state_ledger_write.append_ledger_entry` + `state_ledger_read.LedgerNavigationPrimitive` both materialized at bootstrap; substitution-site `Bash(cat >>)` / `Bash(jq)` no longer required for runtime callers |
| H_T-IS-8 | Workload-class-opt-in shadow-Git checkpoint | **RETIRE-READY** | `lifecycle/shadow_git.py` (`materialize_isolation_stage`) at stage_1_is step 3; cadence-gate at `shadow_git_checkpoint.py:91`; H_E Checkpointing displaced for harness-state cadence |
| H_T-IS-9 | Workload-class-opt-in worktree isolation | **RETIRE-READY** | Manifest-driven opt-in + concurrency-cap at `worktree_isolation.py:117-121`; `subprocess.run(["git", "worktree", ...])` inside typed manager (H_T-owned, not operator `EnterWorktree`); `ctx.worktree_manager` post-condition non-None |

**IS-axis cross-axis cascade fired:** H_T-IS-5 + H_T-IS-6 + H_T-IS-7 jointly compose the typed state-ledger surface that H_T-CXA-2 leans on (substrate side; consumer side still bounded by CP driver — see §5).

---

## §4 AS axis (5 substitutions)

| ID | Primitive | Verdict | Reason |
|---|---|---|---|
| H_T-AS-1 | SandboxTier 4-tier + sandbox_tier_floor + SandboxDispatchTable | **RETIRE-READY** | `lifecycle/sandbox_dispatch.py` (`materialize_sandbox_dispatch` 6-provider×tier table); `handoff.py:174` enforces C-AS-11 monotonic-ascent (`assert_monotonic_ascent`) in-runtime; no `--permission-mode`/`bypassPermissions`/`acceptEdits` strings reachable from runtime composers |
| H_T-AS-2 | Tool contract schema (FastMCP-server-authored) | PARTIAL | `ToolRegistry` typed surface met (`tool_registry.py:58-91`); `materialize_tool_registry` returns empty (`tool_registry.py:104`); `MCPHost.started=False` placeholder (`mcp_host.py:58-66`). Schema contract retired; production deferred. Partial retirement is non-retirement per X-AL-2 |
| H_T-AS-4 | sandbox.* 7-attribute OTel namespace at MCP server | STILL-BOUNDED | Carriers exist (`sandbox_span_schema.py`, `sandbox_attribute_schema.py`, `sandbox_event_sampling.py`); zero runtime references; no `start_span`/`start_as_current_span` invocations exist anywhere in `harness-runtime/src/`. Compound: blocked on tool-invocation runtime composer (Phase-3+) AND on producer site |
| H_T-AS-5 | Sandbox-event idempotency-key composition (FastMCP-server-side SHA-256) | STILL-BOUNDED | Carrier `harness_as/sandbox_event_idempotency.py` exists; zero runtime references. Tool-invocation path absent (`grep -rn "def.*invoke_tool|tool_invocation"` returns no matches in runtime src outside `dispatch` which is sub-agent/topology). Composes with AS-4 — retire together or not at all |
| H_T-AS-8 | Anthropic + MCP primitive observability (15-namespace exports — `anthropic.*` + 6 others) | STILL-BOUNDED | All 4 `anthropic_*` library carriers exist; zero runtime references. Grep for `"mcp.|"skill.|"files.|"memory.|"managed_agents.|"anthropic.` across runtime src returns nothing. **Double-blocked:** missing producer site (tool-invocation runtime composer) AND blocked terminal namespace (`anthropic.*` slot requires H_T-CP-1 retirement per §6.3.1) |

**AS-axis architectural finding (load-bearing).** AS-4/AS-5/AS-8 all sit on a **tool-invocation runtime path that does not exist in the runtime**. Library carriers landed; production sites (composers that invoke the carriers via TracerProvider + ToolRegistry dispatch) absent. AS-4/5/8 retirement waits on a Phase-3+ tool-invocation runtime composer — **not on Phase 2 runtime as v1 ledger assumed**. This reframes 7d-full-closure scope: it isn't only Phase-2-runtime gated; it's also tool-invocation-runtime gated for the AS observability set.

---

## §5 CP axis (21 substitutions)

| ID | Primitive | Verdict | Reason |
|---|---|---|---|
| **H_T-CP-1** | **Routing core + ProviderCapabilities + multi-LLM** | **STILL-BOUNDED** | 3 providers constructed at `providers.py:679-706` (anthropic + openai + ollama); capability bindings frozen at `providers.py:854`. **Zero LLM call sites exist anywhere in `harness-runtime/src/`** — grep for `messages.create|chat.completions|client.chat|client.messages` returns 0 hits. Multi-provider routing not exercised end-to-end. **§9 Class 2 multi-LLM commitment surface OPEN; ADR-F1 v1.2 commitment not yet met at runtime** |
| H_T-CP-2 | Layered routing strategy (dependency-only) | STILL-BOUNDED | Library exists; no runtime composer invokes layered routing; retires when CP-1 retires |
| H_T-CP-3 | Per-layer time-budget + retry.* 6-attribute namespace + dual-emission | STILL-BOUNDED | `lifecycle/retry_breaker.py` is binding-time + reference-time surface only; LOOP_INIT orchestrator (U-RT-43+) drives the actual retry loop — not invoked by `workflow_driver`; no `retry.*` span emit |
| H_T-CP-4 | Fallback chain + cross-family fallback | STILL-BOUNDED | `lifecycle/fallback_chain.py` exposes `advance_or_raise`; no driver call site; no `fallback.exhausted` emit |
| H_T-CP-5 | Routing attribute namespaces + per-class sampling (dependency-only) | STILL-BOUNDED | Same posture as CP-2; depends on CP-1 retirement |
| **H_T-CP-6** | **Workflow manifest schema + per-step override + audit** | **RETIRE-READY** | Operator-supplied typed `RoutingManifest` validated + persisted to `PathClass.ROUTING_MANIFEST` (`routing_manifest.py:143-145`); `workflow_driver.py:360-364` invokes `resolve_step_binding(manifest_entry, step_id, default_model_binding=...)` per-step at runtime. Manifest is the execution surface, not `CLAUDE.md` prose |
| H_T-CP-8 | F2-substrate-join contract | PARTIAL | `workflow_driver.py:397-417` invokes typed state-ledger append via `_append_step_ledger_entry` with computed `step_idempotency_key`; F2 six-field shape exercised end-to-end. BUT `cp_is_wiring.py` is explicit PARTIAL-LAND (1 of 17 spec edges; 8 source units DEFERRED) per `class_1_tension_u_rt_35_cp_is_wiring_gaps.md` |
| H_T-CP-9 | ResumptionKind 5-class taxonomy + engine.* namespace | PARTIAL | Replay-resumption materialized via `_determine_resume_at` (prefix-match IS lookup) at `workflow_driver.py:323-329`; binary `WorkflowEventClass.RESUMPTION` emit at line 331. **5-class `ResumptionKind` taxonomy NOT emitted** by driver (only binary RESUMPTION event class) |
| H_T-CP-10 | TopologyPattern 6-class enum + admissibility + CascadePolicy | STILL-BOUNDED | `_IN_SCOPE_TOPOLOGY = {SINGLE_THREADED_LINEAR}` only (`workflow_driver.py:65-67`); non-LINEAR patterns raise `TopologyPatternNotYetMaterializedError`; CascadePolicy not invoked. CP-AL-1 boundary held but CP-10 retirement unmet |
| H_T-CP-11 | Per-workload commitment table + D4 multiplicative tunable | PARTIAL | `materialize_engine_selector` exhaustively binds 4×3=12 (WorkloadClass, PersonaTier) combinations at bootstrap; `workflow_driver.py:302` validates engine_class against `_IN_SCOPE_ENGINE_CLASSES` (2 of 5); D4 multiplicative tunable not surfaced at runtime |
| H_T-CP-12 | Sandbox-tier dispatch (cross-deployment monotonicity) | STILL-BOUNDED | `SandboxDispatchTable` materialized at bootstrap; `workflow_driver.py` does not invoke sub-agent dispatch / sandbox-tier branching. No `sandbox.*` runtime emission |
| H_T-CP-13 | Sub-agent handoff (HandoffContext, SubAgentBrief, StateSummary, LedgerEntryRef) | STILL-BOUNDED | `RuntimeHandoffRegistry` materialized as binding-time + reference-time surface only (`handoff.py:65-70`); no driver invocation of `dispatch`/`compose_dispatch_audit`. Sub-agent dispatch deferred to L8 LOOP_INIT |
| H_T-CP-14 | Multi-agent span hierarchy + topology.* + subagent.* namespaces | STILL-BOUNDED | No `topology.*`/`subagent.*` span emission site in runtime (gated by CP-13/CP-10 retirement) |
| H_T-CP-16 | Memory primitives + memory.* consumption | STILL-BOUNDED | No runtime composer for memory primitives; CP plan units U-CP-38…U-CP-41 carrier-only at HEAD |
| H_T-CP-17 | Files primitives + files.* consumption | STILL-BOUNDED | Runtime exercises IS path resolver for residence paths (CP-6, IS substrate); no `files.*` namespace emission |
| H_T-CP-18 | MCP integration + per-server trust + mcp.* consumption | STILL-BOUNDED | `mcp_host.py` instantiates FastMCP host placeholder; `MCPTrustTier` carrier landed at U-CP-00c (library); no per-server-trust runtime evaluator at execution path |
| H_T-CP-19 | D5 cross-deployment monotonicity | STILL-BOUNDED | Single deployment_surface configured; no cross-deployment monotonicity enforcement at runtime |
| H_T-CP-20 | HITL primitive + 4-response palette + hitl.* / audit.* | **RETIRE-READY** (batch 8; criterion A met + criterion B partial) | U-RT-60 wrap-asymmetry impl arc APPLIED 2026-05-21: composer wraps both rows of §14.8.1 wrap-asymmetry table at stage 5 (`bootstrap/stage_5_loop_init.py`); `RuntimeHITLGateComposer` invokes `await ctx.ask_user_question_surface.ask(...)` via `MCPBackedAskUserQuestionSurface` per §14.8.3 v1.11 binding pin; 4-substep audit-write + canonical 4-span hierarchy emitted at workflow execution. Bounded carry-forward: FastMCP transport-level handler registration (`_PlaceholderMCPCallback` raises until real delivery primitive binds at follow-on arc — couples with CP-18 retirement). See `.harness/phase-7d-retirement-events-batch-8.md` §1. |
| H_T-CP-21 | ValidatorFailClass 5-class + operator-burden eval primitive | STILL-BOUNDED | `advance_staircase` library function; no driver invocation; no `validator.fail.*` emission |
| H_T-CP-22 | Pause/resume protocol + state_summary snapshot + material-diff | STILL-BOUNDED | `classify_resume` exposed via `RuntimeHITLPlacementRegistry`; driver uses prefix-replay-based resumption (Path A-modified per `[[fork-u-cp-56-resumption-underspec]]`) NOT the typed pause/resume protocol; `/compact` not retired |
| H_T-CP-23 | Bridging-arc traversal composition (F1 + D1 + D4) | STILL-BOUNDED | No bridging-arc traversal composer at runtime; depends on CP-1/CP-10/CP-11 upstream |

**CP-axis architectural finding (load-bearing).** The dominant runtime gap is the **missing LLM call site**. `step_dispatcher.dispatch(binding, step)` at `workflow_driver.py:379` is an architectural seam (injection point) but is operator-injected — no production multi-provider router landed. This is the single load-bearing gap blocking retirement of CP-1, CP-3, CP-4, and by cascade much of the remaining table. Whether the LLM-dispatch composer routes to a Phase-7-deferred runtime unit or to a back-flow Class 1 spec extension is an operator decision outside this verification's scope.

CP-AL-1 (sub-agent topology ≠ TopologyPattern) and CP-AL-4 (single-LLM ≠ routing core) discipline holds: the runtime has NOT silently absorbed H_E's orchestrator-workers or single-LLM as evidence of H_T retirement.

---

## §6 OD axis (7 substitutions)

| ID | Primitive | Verdict | Reason |
|---|---|---|---|
| H_T-OD-1 | Deferral envelope | STILL-BOUNDED | `harness_od/deferral_envelope.py` axis-internal; no `deferral_envelope` import in `harness-runtime/`; scope deferrals remain `CLAUDE.md`-prose convention at runtime |
| **H_T-OD-2** | **OTel SDK base + GenAI semconv binding** | **PARTIAL** | `materialize_tracer_provider_stage` constructs stock OTel `TracerProvider` globally registered. **GenAI semconv NOT bound**: zero `genai`/`gen_ai` references in `tracer_provider.py`. **Zero CP-driver span emission**: grep `get_tracer|start_as_current_span` in `harness-cp/src` returns 0 hits — production execution path emits no spans. OTel SDK base present; GenAI binding absent; consumer path empty. **Blocks CXA-5 F-CP-01 Stage 3b inversion per §6.3.2** |
| H_T-OD-3 | Composite Sampler (head/tail gradient) | STILL-BOUNDED | `_DEFAULT_SAMPLER: Final[Sampler] = ParentBased(root=ALWAYS_ON)` — stock OTel SDK sampler, not a project-authored composite head/tail subclass. Module docstring explicitly admits `ParentBased(ALWAYS_ON)` for both HEAD_BASED_DEV and TAIL_BASED_PROD. `resolve_sampling_mode(...)` called but result discarded (`_ = resolve_sampling_mode(...)`) — sampler-mode resolution observed for audit trail only |
| H_T-OD-4 | Pre-Collector redaction SpanProcessor | STILL-BOUNDED | `materialize_span_processor_stage` attaches stock `BatchSpanProcessor` + `OTLPSpanExporter`; zero references to `redaction_gradient` / `RedactionSpanProcessor` in runtime. Pre-export redaction NOT wired. Compound-irrelevant: no spans emitted anyway (OD-2), so redaction site doubly inactive |
| H_T-OD-5 | Cost-attribution 5-step chain | STILL-BOUNDED | `CostAttributionChain.compute_cost(...)` exists (`cost_attribution.py:187`) and is wired into `HarnessContext.cost_chain` (`stage_4_od.py:75-76`); **zero production callsites** outside definition + shutdown `cost_chain_noop=True` flag. `api.py:463` hard-codes `cost_attribution=()` in `RunResult` ("U-OD-21 HALTED Class 1... empty tuple is the carry-forward shape"). PRICE_TABLE_REF carry-forward per `[[fork-price-table-ref-substitution-retirement]]`; audit-ledger wiring residual per `[[fork-cost-record-audit-ledger-wiring-residual]]` |
| H_T-OD-6 | Local-first OTLP ingestion (in-process collector + sqlite + TUI) | PARTIAL | `materialize_collector_daemon_stage` + `materialize_ring_buffer_stage` wired into bootstrap; supervisor + ring-buffer in-memory only. **Sqlite write path NOT wired** — U-RT-30 PARTIAL-LAND, AC #2 STRUCK; resolved via `[[fork-trace-storage-pathclass-gap]]` Path B (OD-internal) 2026-05-20 but **sqlite write site itself remains deferred**. TUI absent (`admin/inspect.py:226` is CLI text inspector, not Textual TUI). Compound-irrelevant: no spans → collector ingests nothing |
| H_T-OD-7 | Preservation invariants (5-dimension) | STILL-BOUNDED | Zero `PreservationInvariant`/`preservation_invariant` references in `harness-runtime/`; 5-dimension preservation discipline lives in `harness_od/per_dimension_preservation_invariants.py` library carrier only; no runtime enforcement loop |

**OD-axis compound-irrelevance pattern (load-bearing).** OD-3/4/5/6 share a second-order blocker beyond their own local non-wiring: **even if** the local primitive were wired (composite sampler / redaction processor / cost chain / sqlite store), there are **no spans in the production execution path** to sample/redact/cost/store. The CP driver's only OD-axis invocation is `lifecycle_emitter.emit(...)` for 3 workflow-event-class boundaries; no `tracer.start_*` calls; no `audit_writer.append` calls (only `audit_writer.read_all` at shutdown for head-hash extraction). This is the OD-axis face of the same "no LLM call site" gap surfaced in CP-axis.

---

## §7 CXA seams (4 substitutions + 1 downstream)

| ID | Seam | Verdict | Reason |
|---|---|---|---|
| H_T-CXA-1 | AS → IS substrate consumption (11 canonical / 7 genuine typed) | PARTIAL | Composer materialized at `lifecycle/as_is_wiring.py` + bootstrap stage 6; tests exercise callback end-to-end → IS ledger append. **Zero production callers of `emit_secret_fetch_audit_entry` outside test files** — AS secret-fetch driver path absent at runtime. Type-system wiring (7c-verified) is retire-ready; production composition path blocked by absent AS driver |
| H_T-CXA-2 | CP → IS substrate consumption (37 canonical / 9 genuine typed) | STILL-BOUNDED | `cp_is_wiring.py` is PARTIAL-LAND (1 of 17 spec §12.3 edges materialized; 16 DEFERRED per `class_1_tension_u_rt_35_cp_is_wiring_gaps.md`). Zero production callers of `emit_sibling_ledger_entry` outside tests |
| H_T-CXA-3 | CP → AS substrate consumption (18 canonical / 5 genuine typed) | STILL-BOUNDED | **No `lifecycle/cp_as_wiring.py` module exists** — consistent with spec §12 enumeration (no §12 stage for CP→AS). CXA v2.3 §2.3.3 genuine typed edges anchored at `cxa_terminal_imports` Pattern-P1 import surface (verified at 7c), not at a runtime composition stage |
| H_T-CXA-4 | OD → IS / AS / CP substrate consumption (26 canonical: 4+10+12) | STILL-BOUNDED | Three composers materialize (`od_is_wiring.py`, `od_as_wiring.py`, `od_cp_wiring.py`); manifest-resolution + breaker-inversion checks fire at bootstrap (✓). `ctx.audit_writer.append` has zero non-test callers in production code (only `read_all` in shutdown). OD `sign_audit_entry` / `AuditLedgerEntry` compose path not invoked from any runtime driver |
| H_T-CXA-5 (downstream) | F-CP-01 Stage 3b inversion (`harness.breaker.*` substrate-anchored-outside-CP) | STILL-BOUNDED-DOWNSTREAM | Per Meta-Architecture §6.3.2, gated on H_T-OD-2 retirement. OD-2 is PARTIAL → CXA-5 cannot retire. The §12.6 edge-1 inversion VERIFICATION (`harness.breaker.*` attribute-count agreement) IS materialized + fires at bootstrap (`od_cp_wiring.py:187-223`), satisfying the type-system inversion contract. Runtime *emission* of `harness.breaker.*` spans absent (compound: no breaker driver invocation + no OTel emission path) |

**CXA pattern (load-bearing).** All CXA seams exhibit the same shape — composition modules + Pattern P1 verification + tests are RETIRE-READY at the *bootstrap invariant* layer (correctness checks fire, manifest strings resolve, inversion attribute counts match), but the *producer-driver invocation* layer (AS secret-fetch driver, CP sibling-spawn / multi-LLM call site, OD audit-emission from runtime drivers) is uniformly absent. With CP=17-STILL-BOUNDED, AS=3-STILL-BOUNDED, OD=5-STILL-BOUNDED endpoint substrates, no CXA seam can be RETIRE-READY at this pass.

The 7c verification log at `5a83419` confirmed 22/22 genuine typed seams have Pattern P1 byte-exact alignment in code; that established the type-system layer. The CXA substitution retirement question is distinct: did the H_E composition surface get displaced at runtime invocation? At this pass: not yet — the runtime invocation layer for cross-axis composition is uniformly absent except for CXA-1 (which has a tested composer wired but no production caller, hence PARTIAL).

---

## §8 Cross-axis cascades + §9 Class 2 disposition

### §8.1 §6.3.1 H_T-CP-1 → H_T-AS-8 (anthropic.* namespace emission)

**DORMANT** — CP-1 STILL-BOUNDED; AS-8 STILL-BOUNDED. Both endpoints absent. Cascade does not fire. Until a multi-provider LLM call site lands in `harness-runtime/` exercising the anthropic adapter at `providers.py:679-706` with tracer-attached span emission, the `anthropic.*` namespace remains absent at runtime.

### §8.2 §6.3.2 H_T-OD-2 + H_T-CP-24 → H_T-CXA-5 (F-CP-01 Stage 3b inversion seam)

**DORMANT** — H_T-CP-24 is authoring-only-retired (v1 §1) but per v1 §3 footnote that retirement does NOT half-fire the cascade (authoring-retired ≠ runtime-substrate-active). H_T-OD-2 is PARTIAL. CXA-5 type-system inversion check fires at bootstrap (✓) but the runtime emission flow is absent. Cascade does not fire until OD-2 transitions PARTIAL → RETIRE-READY (which requires GenAI semconv binding + a runtime span emission path).

### §8.3 §9 Class 2 multi-LLM commitment surface

**OPEN — NOT CLOSED.** Per Meta-Architecture §9 + §10.4.3, H_T-CP-1 retirement closes the §9 surface when multi-LLM runtime commitment is met. v2 verification: stage 3a constructs all 3 providers (anthropic + openai + ollama) at `providers.py:679-706` and binds capability surface at `providers.py:788-857`, but **no end-to-end multi-provider LLM call path exists in the runtime** — zero hits for `messages.create`/`chat.completions`/`client.chat`/`client.messages` in `harness-runtime/src/`. The `step_dispatcher.dispatch(binding, step)` injection point at `workflow_driver.py:379` is the architectural seam where LLM dispatch would land, but the implementation is operator-injected; the runtime ships no production dispatcher.

**ADR-F1 v1.2 multi-LLM commitment status:** Met at design + specification + as landed library code (3 provider adapters constructed; capability-aware abstraction present). **Unmet at runtime** — no LLM call ever flows through the constructed providers in the production execution path.

§9 Class 2 surface remains the most consequential unmet project commitment from v1's framing; v2 confirms it.

### §8.4 New cascade surfaced at v2 — tool-invocation runtime composer

Beyond the two §6.3 documented cascades, v2 surfaces a third de-facto cascade: **tool-invocation runtime composer absence blocks AS-4/AS-5/AS-8 + AS-2 production retirement**. This is not a documented Meta-Architecture §6.3 dependency but emerges from the per-substitution analysis. The Phase 2 runtime closure scoped the substrate-bootstrap loop (stage 0-7 bootstrap + CP routing + OD telemetry-bind + F2 ledger); the tool-invocation loop (which would consume AS-2/4/5/8 carriers via TracerProvider + ToolRegistry dispatch) was not in scope and remains a Phase-3+ surface. This reframes 7d-full-closure: it is NOT only Phase-2-runtime gated; it is also tool-invocation-runtime gated for the AS observability set.

---

## §9 Retirement records + outstanding work

### §9.1 Eligible retirement events (8 — ready to file at next session)

The following 8 substitutions transition from "bounded-residual" (v1) to "RETIRED" (this pass), under the operator-ratified runtime-only substitution-site reading. Per-event recording per skill `phase-7-substitution-retirement` §8.1 deferred to a follow-on doc-hygiene pass (this v2 ledger constitutes the verification evidence base):

| ID | Substitution | Verification anchor |
|---|---|---|
| H_T-IS-1 | Path-class registry | §3 |
| H_T-IS-5 | State-ledger entry shape | §3 |
| H_T-IS-6 | Hash-chain integrity discipline | §3 |
| H_T-IS-7 | T-perm-2 F2-layer read/write contract pair | §3 |
| H_T-IS-8 | Workload-class-opt-in shadow-Git checkpoint | §3 |
| H_T-IS-9 | Workload-class-opt-in worktree isolation | §3 |
| H_T-AS-1 | SandboxTier 4-tier + SandboxDispatchTable | §4 |
| H_T-CP-6 | Workflow manifest schema + per-step override | §5 |

### §9.2 Outstanding work

1. **Per-axis `CLAUDE.md` substitution-table doc-hygiene pass.** Update `harness-{is,as,cp,od}/CLAUDE.md` §4 substitution tables to reflect the 8 RETIRE-READY events recorded at §9.1. Non-blocking; documentation-debt only.
2. **Tool-invocation runtime composer scope decision.** Operator decision: does the tool-invocation runtime (AS-2/4/5/8 unblock) route to a Phase-7-deferred runtime unit, a Phase-3 design effort, or a back-flow Class 1 spec extension? Out of scope for this verification ledger.
3. **LLM-dispatch runtime composer scope decision.** Same question for CP-1 retirement + §9 Class 2 multi-LLM commitment surface close. Out of scope for this verification ledger.
4. **PARTIAL upgrades to RETIRE-READY.** AS-2, CP-8, CP-9, CP-11, OD-2, OD-6, CXA-1 are within reach of RETIRE-READY with targeted runtime work (each is bounded by a specific finite gap, not by a missing major composer). Re-evaluate at next runtime delta.
5. **Bounded-residual scope re-statement for 7d-full-closure.** v1 ledger framed full closure as "Phase 2 runtime + per-substitution runtime-trace verification." v2 verification reveals the scope is more layered:
   - Phase 2 runtime substrate-bootstrap (DONE): unblocks IS-1/5/6/7/8/9, AS-1, CP-6 (8 retirements ready).
   - Tool-invocation runtime composer (NOT IN PHASE 2): unblocks AS-2/4/5/8, CXA-1.
   - LLM-dispatch runtime composer (NOT IN PHASE 2): unblocks CP-1/3/4 + cascades to AS-8, OD-2, CXA-5.
   - HITL gate / validator framework / sub-agent dispatch runtime (NOT IN PHASE 2): unblocks CP-10/13/14/20/21/22, OD-7.
   - Each is a separate runtime composer with its own design + implementation scope.

### §9.3 7d closure status

| | |
|---|---|
| Authoring-only retired (v1 §1) | 4 / 4 ✅ |
| Runtime-active RETIRE-READY (v2) | **8 / 45** — eligible to file at synthesis pass |
| Runtime-active PARTIAL (v2) | 7 / 45 — within reach of RETIRE-READY |
| Runtime-active STILL-BOUNDED (v2) | 30 / 45 — bounded by 3+ separate runtime composer absences |
| 7d full closure | **NOT reached** — requires (1) tool-invocation runtime composer, (2) LLM-dispatch runtime composer, (3) HITL/validator/sub-agent runtime composer, plus per-substitution runtime-trace re-verification |
| §9 Class 2 multi-LLM surface | OPEN — closes at LLM-dispatch runtime composer + CP-1 retirement |
| Silent carry-forward | NONE — all 45 explicitly classified under runtime-only substitution-site reading |

### §9.4 Operator ratification required

Per skill §5.3, bounded-residual carry-forward at 7d closure requires operator authorization. v2 ratification request:

1. **Ratify the 8 RETIRE-READY events** at §9.1 for recording (file event records per skill §8.1 at next session).
2. **Ratify the 37 non-retired substitutions** (7 PARTIAL + 30 STILL-BOUNDED) as bounded-residual carried forward, under the updated scope framing at §9.2.5: not just Phase-2-runtime gated, but additionally gated on (a) tool-invocation runtime composer, (b) LLM-dispatch runtime composer, (c) HITL/validator/sub-agent runtime composer.
3. **Acknowledge §8.3 §9 Class 2 surface remains OPEN** — ADR-F1 v1.2 multi-LLM commitment met at design + library code; unmet at runtime.

---

## §10 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-ledger-v2.md` |
| Authored at | Phase 7 sub-phase 7d second pass, 2026-05-20 |
| Authoring authority | Skill `phase-7-substitution-retirement` + operator-ratified runtime-only substitution-site reading |
| Predecessor | `.harness/phase-7d-retirement-ledger.md` (v1, 2026-05-17) |
| Verification base | Phase 2 runtime closure at `43500bf`; 1152 tests on main; 22/22 genuine typed seams verified at 7c log `5a83419` |
| Method | Per-axis sub-agent fan-out (4 axes + CXA); synthesis at this ledger |
| Scope | Verification only — no source-code modification |
| Successor consumption | Per-axis CLAUDE.md doc-hygiene pass; per-substitution retirement event records (skill §8.1); 7d full closure at downstream runtime composer landings |
| Status | Verification complete; 8 retirement events eligible; 7 PARTIAL within reach; 30 STILL-BOUNDED bounded-residual under updated 3-composer scope framing |

---

## §11 Surfaced supersession sites (2026-05-27 refresh)

Audit pass on 2026-05-27 triggered by a candidate batch-20 evaluation for H_T-OD-2 surfaced the following supersession sites. Catalogued here for the reader; original §3–§9 row text preserved verbatim per forward-only discipline.

### §11.1 H_T-OD-2 — RETIRED at batch-2

| Snapshot site | Snapshot text | Superseded by |
|---|---|---|
| §6 row line 124 | "PARTIAL ... GenAI semconv NOT bound ... Zero CP-driver span emission" | **RETIRED 2026-05-20** at `.harness/phase-7d-retirement-events-batch-2.md` §4 (U-RT-52 close arc; criterion B met at `RuntimeLLMDispatcher.dispatch` Step 2 span + Step 4-5 attribute set). Subsequent strengthening at `e874a03` (Path A, 2026-05-27): `llm_dispatch.py:343-360` widened from 5 → 6 of 9 non-Opt-In §C-OD-04 §4.3 attrs (added `gen_ai.conversation.id` + `server.address` + `server.port` per provider). Per-axis live status at `harness-od/CLAUDE.md` §4.1 |
| §8.2 cascade DORMANT | "H_T-OD-2 is PARTIAL ... Cascade does not fire until OD-2 transitions PARTIAL → RETIRE-READY" | **Cascade closed at batch-3** per `harness-od/CLAUDE.md` §4.1 H_T-OD-2 row ("CXA-5 cascade closed at batch 3"). §6.3.2 joint precondition with CP-24 (authoring-retired v1 §1) satisfied at OD-2 RETIRED batch-2 + batch-3 cascade re-evaluation. CXA-5 type-system inversion verification continues to fire at bootstrap per §7 row line 143 |
| §9.2.4 line 197 "within reach" | "OD-2 ... within reach of RETIRE-READY" | OD-2 already RETIRED at batch-2 (4 batches before this snapshot was filed — text was stale at authoring time per the operator-ratified runtime-only substitution-site reading recorded at batch-2 §4) |

### §11.1a H_T-CXA-5 — RETIRED at batch-3 (supersession; filed 2026-05-28 batch-41 successor reconciliation)

| Snapshot site | Snapshot text | Superseded by |
|---|---|---|
| §7 row line 143 | "STILL-BOUNDED-DOWNSTREAM ... Per Meta-Architecture §6.3.2, gated on H_T-OD-2 retirement. OD-2 is PARTIAL → CXA-5 cannot retire" | **RETIRED 2026-05-20** at `.harness/phase-7d-retirement-events-batch-3.md` §4 (U-RT-58 close arc — production `harness.breaker.*` emission site landed at `retry_breaker_fallback.py:_emit_breaker_transition` delegating to `RuntimeRetryBreaker.emit_breaker_transition_event` per OD-canonical C-OD-07 §7.1 7-attribute schema). Both endpoints retired pre-batch (OD-2 RETIRED batch-2 + CP-24 RETIRED authoring close v1 §1); production callsite landed at batch-3 activates the inversion seam end-to-end. Per-axis live status at workspace `CLAUDE.md` §2.5 + `harness-cp/CLAUDE.md` §"§6.3.2 F-CP-01 Stage 3b inversion cascade FULLY DISCHARGED" |
| §7 "CXA pattern" footer line 145 | "no CXA seam can be RETIRE-READY at this pass" | **CXA-5 RETIRED at batch-3** (2026-05-20). Pre-2026-05-27-refresh §7 narrative did not include §11.x supersession for CXA-5; ledger v2 §7 row continued to read STILL-BOUNDED-DOWNSTREAM through 2026-05-27 §11 batch refresh + batches 22–41. Carry-window: 38 batches × 8 days. Cardinality drift propagated through every batch-cardinality check since batch-3: actual workspace cumulative post-batch-41 is **43/54 RETIRED (79.6%) + 2 RETIRE-READY (3.7%) + 3 PARTIAL (5.6%) + 4 STILL-BOUNDED (7.4%) + 2 STILL-BOUNDED-INDEFINITELY (3.7%) = 54 ✓** (was reported as 42 RETIRED + 5 STILL-BOUNDED per stale CXA-5 STILL-BOUNDED-DOWNSTREAM accounting). Pipeline-advanced: **48/54 = 88.9%** (was reported as 47/54 = 87.0%). Corrective accounting applies at batch-41 successor onward; prior batch records stand verbatim per workspace `CLAUDE.md` §4.3 forward-only ledger discipline. Per workflow v1.12 §7.4.7.3.C audit-template applied retroactively at batch-41 successor doc-hygiene arc. |

**Sub-species 10 catalogue impact:** CXA-5 closure (batch-3) predates sub-species 10 catalogue authoring at workflow v1.12 publication 2026-05-28 + does not fit sub-species 10 categorical-mismatch shape (CXA-5 closed via production-emission-site-landing, not via doc-hygiene reclassification of vacuous H_E surface). Sub-species 10 cardinality at workflow v1.12 §7.4.7.2 remains 5 (OD-1 + OD-7 + IS-4 + CP-12 + CP-23 batches 37–41).

**Cardinality adoption scope:** This §11.1a supersession recognizes CXA-5 batch-3 closure at ledger v2 §7 row. Whether the corrective workspace cumulative counts (43/54 RETIRED + 4 STILL-BOUNDED + 48/54 pipeline-advanced) are adopted at workspace `CLAUDE.md` §2.5 + `harness-cp/CLAUDE.md` + batch-41 footer is a separate doc-hygiene scope decision pending operator routing (see batch-41 successor reconciliation note).

### §11.1b H_T-CXA-3 — audit-empty result (filed 2026-05-28 batch-41 successor)

| Audit step | Finding |
|---|---|
| Meta-Arch §5.7 H_E classification | **~ partial** (line 646) — H_E covers untyped sub-agent + Skills + MCP composition via `Agent` + Skills loading + MCP registration + brief-authoring via `CLAUDE.md` |
| Retirement criterion | "CP clusters 5+6+7 land as runtime composers displacing H_E `Agent`/Skills/MCP" (Meta-Arch §5.6 line 748 + §6.3 line 1217) |
| Sub-cluster 5 status | U-CP-32..U-CP-36 includes Files-arc primitives **deferred indefinitely** per runtime spec v1.17 §14.C Memory-only ratified scope (2026-05-23). Sub-cluster 5 criterion B forecloses RETIRED transit at canonical runtime composer layer until Files-arc design-phase opens. |
| Sub-species 10 (categorical-mismatch ✗ absent) fit | **FORECLOSED** — H_E classification is ~ partial, not ✗ absent. Pre-substantive empirical orientation against Meta-Arch §5.7 invalidated initial framing-candidate. |
| Sub-species 7 (operator-discretion MVP carve-out) fit | **FORECLOSED** — no spec-explicit MVP carve-out cite parallel to CP-11/CP-14 (runtime spec v1.6 §14.7.2 step 5 single-sub-agent slice) covering the 24-edge typed contract surface at CXA v2.1 §2.3.3. Sub-cluster 5 Files-arc indefinite-defer is the structural blocker. |
| Disposition | **STILL-BOUNDED preserved**. No in-session closure shape applies; advisor-recommended audit termination at cardinality 1 ratified by operator AskUserQuestion 2026-05-28. CXA-3 retirement pathway gated on either (α) Files-arc design-phase opening + sub-cluster 5 runtime composer landing OR (β) operator AskUserQuestion ratifying Memory-only-scope carve-out for CXA-3 retirement criterion narrowing (parallel to AS-8e + AS-8f indefinite-defer pattern but at CXA-axis row). Neither path is in-session-actionable at this arc. |

**Class 3 informational disposition.** No ledger-row status change; no production code change; no spec amendment; no cross-axis cascade. §3(f) NEW species candidate audit terminates at cardinality 1 (CP-23 batch-41 framing-drift the sole instance; CXA-5 batch-3-vs-§7 framing-drift documented at §11.1a but distinct closure-event-class — production-emission-site-landing supersession, not ledger-authoring-time framing-drift causal pattern at the same level of generality).

### §11.1c H_T-CXA-4 — STILL-BOUNDED → PARTIAL at batch-42 (filed 2026-05-28 deployment-readiness closure arc)

| Snapshot site | Snapshot text | Superseded by |
|---|---|---|
| §7 row line 156 | "STILL-BOUNDED ... `ctx.audit_writer.append` has zero non-test callers in production code (only `read_all` in shutdown). OD `sign_audit_entry` / `AuditLedgerEntry` compose path not invoked from any runtime driver" | **PARTIAL 2026-05-28 (batch-42)** per empirical grep at HEAD `a0ad1be`: (1) 6 production callers of `audit_writer.append` at `harness-runtime/src/harness_runtime/lifecycle/{sub_agent_dispatch:497, hitl_gate_composer:699, cost_attribution_{llm,tool,validator,webhook}_dispatch}.py`; (2) `sign_audit_entry` invoked at `harness-cxa/src/harness_cxa/cp_audit_conversion.py:321` + `AuditLedgerEntry(...)` constructed at `:324` (compose path fully exercised); (3) 3 composer-materialization stages fire at `bootstrap/stage_6_cxa_wiring.py:69+74+78`. Of 26 canonical edges: ~5 materialized + 1 fully exercised (audit-write seam). Refreshed disposition + remaining transit gates at `.harness/phase-7d-retirement-events-batch-42.md` §1.2. |

**Sub-species 3 catalogue expansion:** NEW sub-species candidate **`stale-ledger-row-vs-production-state`** at workflow v1.12 §7.4.7.2 — sibling to CXA-5 §11.1a batch-3-vs-§7 closure-event-class (also 2026-05-28). Cardinality 2 in single calendar day; species 3 sub-species column extension at future workflow revision increasingly warranted.

**Forward-only ledger discipline:** §7 row 156 preserved verbatim. Refreshed row text canonical going forward at batch-42 §1.2. Pre-batch-42 cumulative checks across batches 12 → 41 stand verbatim.

### §11.2 H_T-AS-2 — RETIRED at batch-16

| Snapshot site | Snapshot text | Superseded by |
|---|---|---|
| §9.2.4 line 197 "within reach" | "AS-2 ... within reach of RETIRE-READY" | **RETIRED 2026-05-24** at `.harness/phase-7d-retirement-events-batch-16.md` (joint close with H_T-CP-18 via shared MCP-client substrate; U-RT-86 L9-novies cluster close at `8e6311f`; 2/2 e2e tests pass against in-process stdio MCP echo fixture). Per-axis live status at `harness-as/CLAUDE.md` §4.1 |

### §11.3 §9.1 "8 RETIRE-READY ready to file" — all 8 filed at batch-2

The §9.1 table (IS-1, IS-5, IS-6, IS-7, IS-8, IS-9, AS-1, CP-6) was filed as 8 RETIRED events at `.harness/phase-7d-retirement-events-batch-2.md` §0 cumulative footer (15/49 RETIRED post-batch-2, which includes IS-axis 9/9 at batch-1 + this 8 at batch-2 + OD-2 + CP-1 + CP-2 + AS-8-related at batch-2). The §9.4 operator ratification request (3 items) was satisfied at the batch-2 + batch-3 arcs. For current cumulative status see §11.5 below.

### §11.4 Cross-row drift NOT in this audit's scope

The 2026-05-27 audit pass focused on the surfaced OD-2 candidate transition + sibling rows on the same §9.2.4 line. The following sites at §3–§9 have also drifted between 2026-05-20 and HEAD but are NOT individually catalogued here:

- §3 IS axis row verdicts: 6 RETIRE-READY rows all transitioned to RETIRED at batch-1/batch-2.
- §4 AS axis row verdicts: AS-1 RETIRED batch-1; AS-2 RETIRED batch-16; AS-4 PARTIAL → RETIRED batch-19; AS-8 advances mentioned at multiple batches.
- §5 CP axis row verdicts: CP-1, CP-2, CP-6 RETIRED at batch-1/2; CP-16 batch-14; CP-18 batch-16; CP-21 batch-17; CP-22 batch-18; many more PARTIAL/RETIRE-READY transitions across batches 3–18.
- §6 OD axis row verdicts: OD-5 STILL-BOUNDED → PARTIAL at batch-11 (1 of 4 dispatch surfaces wired).
- §9.3 closure counts (8/45/30 numerators): superseded by cumulative 28/49 RETIRED at batch-19.

Readers requiring exhaustive per-row supersession should consult per-axis `CLAUDE.md` §4.1 + the batch-19 §0 cumulative footer + sibling row references therein. A future doc-hygiene pass MAY produce a complete per-row supersession map; this 2026-05-27 pass deliberately scopes only the OD-2-adjacent surface that triggered the audit.

### §11.4a H_T-AS-8 — DECOMPOSED into 6 sub-rows + 3 sub-RETIRED at batch-24

The 2026-05-20 snapshot's §4 AS-axis row 5 (H_T-AS-8 STILL-BOUNDED) is **superseded** by the ledger-v2-layer decomposition event filed at `batch-24` (2026-05-28):

- The monolithic H_T-AS-8 row was identified per `class_3_drift_as_8_partial_row_per_namespace_breakdown.md` as wrongly scoped to cover 6 independent producer sites (`anthropic.*` / `mcp.*` / `skill.*` / `managed_agents.*` / `files.*` / `memory.*`) with 6 distinct close gates.
- Per drift doc §5(b) operator-discretion routing trigger + operator AskUserQuestion ratification 2026-05-28 (Option A) + advisor Scope B pre-substantive consultation: decomposition lands at ledger-v2-layer ONLY (Meta-Arch §2.2 row 423 PRESERVED VERBATIM per X-AL-3).
- Decomposed sub-rows: AS-8a (anthropic.*) / AS-8b (mcp.*) / AS-8c (memory.*) / AS-8d (skill.*) / AS-8e (files.*) / AS-8f (managed_agents.*).
- Immediate close transits at decomposition event (criteria already MET pre-decomp): AS-8a + AS-8b + AS-8c → RETIRED.
- Carry-forward sub-rows: AS-8d STILL-BOUNDED → RETIRE-READY at batch-25 (operator-opt-in pattern, mirrors CP-18/CP-21/CP-22/RT-94 precedent); AS-8e STILL-BOUNDED-INDEFINITELY (Files arc DEFERRED per runtime spec v1.17 §14.C); AS-8f STILL-BOUNDED → STILL-BOUNDED-INDEFINITELY at batch-26 (DEFER INDEFINITELY mirror AS-8e per `.harness/class_1_fork_as_8f_managed_agents_namespace_production_only_exclusion.md` Q1=(C) + runtime spec v1.33 change-note + AS spec v1.7 → v1.8 §14.5 production-only exclusion footer; honors AS spec C-AS-13 §13.2 adoption-depth matrix design declaration excluding managed_agents at local-development for all workload classes).

**§4 row text PRESERVED VERBATIM** per §0.5 forward-only ledger discipline; the live decomposed view lives at `harness-as/CLAUDE.md` §4.1 + `batch-24` filing.

**Cardinality delta at this batch:** AS-axis ledger denominator 5 → 10 (AS-8 row 1 → 6 sub-rows); workspace ledger denominator 49 → 54. Cumulative RETIRED 30/49 → 33/54 (61.2% → 61.1% — structural cardinality rebalance, not pipeline progress).

**Sub-species 7c "retirement-ID-scoping-too-coarse"** catalogued at batch-24 §2 — distinct from prior 7a (CP-19 operator-explicit-deferred-close-gate at batch-22) + 7b (AS-5 gate-text-stale-vs-production-architecture at batch-23); FIRST instance of retirement-ID decomposition in ledger history.

### §11.4b H_T-CP-14 — PARTIAL → RETIRED at batch-29

The pre-batch-29 CP-axis CP-14 row PARTIAL classification is **superseded** by the operator-discretion ratification event filed at `batch-29` (2026-05-28):

- Runtime spec v1.6 §14.7.2 step 5 line 2546 explicit operator-discretion retirement path: "Operator may ratify the single-sub-agent slice as PARTIAL → RETIRED at retirement audit IF the bounded scope is documented as a follow-on parent-topology-expansion arc."
- Empirical state at batch-29 filing: production at `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:613` emits v1.6 MVP narrow subset per spec — `topology.pattern` + `topology.workload_class` at open-time on `subagent.span`, 7 `subagent.*` attrs across open + close. IN COMPLIANCE.
- Bounded-scope documentation: 8 fan-out-specific `topology.*` attrs (`fan_out_cap`, `cascade_policy`, `results_collected`, `results_failed`, `cascade_applied`, `synthesis_token_budget`, `cascade_decision_audit_ledger_id`, `concurrent_token_budget_at_dispatch`) deferred to v1.7+ parent-topology-expansion arc (Phase 6 substrate) per runtime spec v1.6 §14.7.2 step 5 "Scope: single-sub-agent within linear parent" carve-out.
- Operator AskUserQuestion ratification 2026-05-28 selected "File batch-29 with PARTIAL → RETIRE-READY → RETIRED joint single-batch transit".
- ZERO production code change; ZERO spec amendment; ZERO cross-axis cascade — pure retirement-audit ratification at spec-explicit operator-discretion path.

**Sub-species 7.operator-explicit-deferred-close-gate SECOND CLOSURE** — joins CP-19 batch-22 (Layer 3 e2e reframed in-process scope). Both are *retirement-audit ratification at spec-explicit operator-discretion path*, distinct from sub-species 7.deployment-time-opt-in-gate (AS-8d + OD-5). SECOND same-session joint single-batch transit (CP-19 batch-22 was first; CP-14 batch-29 is second). SIXTH RETIRE-READY → RETIRED close overall in ledger history.

**Cardinality delta at this batch:** CP-axis RETIRED 15/22 → 16/22 (68.2% → 72.7%); workspace RETIRED 33/54 → 34/54 (61.1% → 63.0%); workspace PARTIAL 6/54 → 5/54 (CP-14 transit-out; post-batch-28 empirical PARTIAL = 6 from per-axis CLAUDE.md §4.1 audit at batch-29: CP-8/9/11/14/17 (5 CP) + OD-6 (1 OD) = 6 sites; batch-28 §2 cite "4/54 PARTIAL" was per-axis-audit-undercounted); STILL-BOUNDED 11/54 (batch-28 §2 cite "13/54" was per-axis-audit-overcounted by 2; empirical: IS:2 + CP:2 + OD:4 + CXA:3 = 11); STILL-BOUNDED-INDEFINITELY 2/54 (AS-8e + AS-8f); workspace pipeline-advanced 39/54 → 41/54 (72.2% → 75.9%). **Cardinality check at batch-29 close: 34 + 2 + 5 + 11 + 2 = 54 ✓.** Forward-only ledger discipline preserved at prior batch records; corrected counts apply at batch-29 onward.

### §11.4c H_T-CP-11 — PARTIAL → RETIRED at batch-30

The pre-batch-30 CP-axis CP-11 row PARTIAL classification is **superseded** by the operator-discretion ratification event filed at `batch-30` (2026-05-28; sibling-arc to batch-29 CP-14 close earlier same session):

- Runtime spec v1.6 §14.7.2 step 5 cascade_policy carve-out (SAME spec section that ratified CP-14 at batch-29): "Fan-out-specific `topology.*` attributes (`fan_out_cap`, **`cascade_policy`**, `results_collected`, `results_failed`, `cascade_applied`, `synthesis_token_budget`, `cascade_decision_audit_ledger_id`, `concurrent_token_budget_at_dispatch`) are NOT set at v1.6 (out of scope per change-note 'Scope: single-sub-agent within linear parent')."
- Empirical state at batch-30 filing: U-CP-23 + U-CP-24 carriers landed and consumed at runtime (`topology_dispatcher.py:38, 113` admissibility + `workload_engine_class_matrix.py:77` default-pattern + `t_perm_3_composition.py:275-312` T-perm-3 composition); U-CP-25 2D matrix + `d4_tunable` carriers landed with full C-CP-11 §11.3 + §11.4 cardinality; `d4_tunable` runtime invocation structurally unreachable at v1.6 MVP single-sub-agent scope (ZERO production callers verified empirically; no siblings → no cascade-decision firing point → no `ParentFanoutCloseEntry` construction). IN COMPLIANCE.
- Bounded-scope documentation: `d4_tunable` runtime invocation deferred to v1.7+ parent-topology-expansion arc (Phase 6 substrate — SAME gate as CP-14 batch-29 §3 (a)).
- Operator routing 2026-05-28: AskUserQuestion selected "Deep-audit CP-11 production surface" with disposition "File appropriate retirement event OR fork doc"; audit verdict was clean sub-species 7 third closure via the same v1.6 MVP scope ratification path that closed CP-14 at batch-29.
- ZERO production code change; ZERO spec amendment; ZERO cross-axis cascade — pure retirement-audit ratification at spec-explicit operator-discretion path.

**Sub-species 7 THIRD CLOSURE** — joins CP-19 batch-22 (Layer 3 e2e reframed in-process scope) + CP-14 batch-29 (v1.6 MVP single-sub-agent slice bounded scope). All three are *retirement-audit ratification at spec-explicit operator-discretion path*, distinct from sub-species 7.deployment-time-opt-in-gate (AS-8d + OD-5). THIRD same-session joint single-batch transit (CP-19 batch-22 first; CP-14 batch-29 second; CP-11 batch-30 third). SEVENTH RETIRE-READY → RETIRED close overall in ledger history. **Framing A reinforced empirically**: CP-11 + CP-14 are sibling closures from the SAME §14.7.2 step 5 v1.6 MVP scope carve-out — strengthens the case that the common-ancestor *retirement-audit ratification at spec-explicit operator-discretion path* is the canonical sub-species, with lineage (never-exercised vs deferred-then-closed) as sub-discriminator rather than sister-sub-species split.

**Cardinality delta at this batch:** CP-axis RETIRED 16/22 → 17/22 (72.7% → 77.3%); workspace RETIRED 34/54 → 35/54 (63.0% → 64.8%); workspace PARTIAL 5/54 → 4/54 (CP-11 transit-out); RETIRE-READY unchanged at 2/54 (AS-8d + OD-5); STILL-BOUNDED unchanged at 11/54; STILL-BOUNDED-INDEFINITELY unchanged at 2/54; workspace pipeline-advanced 41/54 = 75.9% (unchanged — within-tier promotion CP-11 PARTIAL → RETIRED). **Cardinality check at batch-30 close: 35 + 2 + 4 + 11 + 2 = 54 ✓.** Forward-only ledger discipline preserved at prior batch records.

### §11.4d H_T-AS-8d — RETIRE-READY → RETIRED at batch-31

The pre-batch-31 AS-axis AS-8d row RETIRE-READY classification is **superseded** by the deployment-time-opt-in-gate closure event filed at `batch-31` (2026-05-28; sibling-arc to batch-32 OD-5 close same merge):

- Runtime spec v1.32 §14.17.6 retirement scope: operator-bound `RuntimeConfig.skill_activation_hook_config` non-None + e2e exercise observing `skill.activation` span at ≥1 hook site per X-AL-2 retirement criterion.
- Empirical state at batch-31 filing: PR #14 merge at `24a9363` (2026-05-28) completed `_FakeSpanContext` OTel `Span` surface (`set_status` / `record_exception` / `add_event` / `end` / `get_span_context`) at `harness-runtime/tests/integration/conftest.py`; `just retire-as-8d` (AC #7) PASS on main against real Anthropic with operator-supplied `SkillActivationHookConfig(hook=_TestHook())`; `skill.activation` span captured with all 6 AS spec v1.7 §14.4 attributes + `workflow.id == "wf-ac7-skill-activation"`. IN COMPLIANCE.
- ZERO production code change at the retirement arc itself; PR #14 was test-side fixture completion only.
- ZERO spec amendment; ZERO cross-axis cascade — pure deployment-time-opt-in-gate close via mech-β AC #7 e2e green proof.

**Sub-species 7.deployment-time-opt-in-gate FIRST CLOSURE** — joins sub-species 7.operator-discretion-ratification-at-spec-explicit-path (CP-19 batch-22 + CP-14 batch-29 + CP-11 batch-30) as the second closure-event-class under sub-species 7. EIGHTH RETIRE-READY → RETIRED close overall in ledger history. **FIRST AS-axis deployment-time-opt-in-gate closure** in ledger.

**Cardinality delta at this batch:** AS-axis RETIRED 8/11 → 9/11 (72.7% → 81.8%); workspace RETIRED 35/54 → 36/54 (64.8% → 66.7%); workspace RETIRE-READY 2/54 → 1/54 (OD-5 carries forward to batch-32); workspace PARTIAL unchanged at 4/54; workspace STILL-BOUNDED unchanged at 11/54; workspace STILL-BOUNDED-INDEFINITELY unchanged at 2/54; workspace pipeline-advanced 41/54 = 75.9% (unchanged — within-tier promotion). **Cardinality check at batch-31 close: 36 + 1 + 4 + 11 + 2 = 54 ✓.** Forward-only ledger discipline preserved at prior batch records.

### §11.4e H_T-OD-5 — RETIRE-READY → RETIRED at batch-32

The pre-batch-32 OD-axis OD-5 row RETIRE-READY classification is **superseded** by the deployment-time-opt-in-gate closure event filed at `batch-32` (2026-05-28; sibling-arc to batch-31 AS-8d close same merge):

- OD spec v1.24 §C-OD-26 + CXA v2.13 §2.3.7 row 8 retirement scope: operator-bound deployment substrate (`RuntimeConfig.validator_framework_config` non-None + operator-explicit `WebhookDeliveryComposer` construction with cost-attribution substrates per Reading H) + real workflow execution exercising ≥1 dispatch surface + production emitted `cost:`-prefixed audit-ledger entries per CXA v2.13 §2.3.7 row 8.
- Empirical state at batch-32 filing: PR #14 merge at `24a9363` (2026-05-28) included AC #8 test typo fix (`retry.attempt.number` → `retry.attempt_number`) at `test_track_b_e2e.py:1922` AND the `_FakeSpanContext` OTel `Span` surface completion at `conftest.py`; `just retire-od-5` (AC #8) PASS on main against real Anthropic with operator-explicit `WebhookDeliveryComposer` + real httpx `MockTransport`; `hitl.webhook.deliver` outer span + `hitl.webhook.attempt` inner span captured with full attribute set (`webhook.url_hash` + `webhook.idempotency_key=='idem-ac8-1'` + `webhook.delivery_attempts==1` + `retry.attempt_number==1` + status code 200). IN COMPLIANCE.
- ZERO production code change at the retirement arc itself; PR #14 was test-side fixture completion + one test-typo fix only.
- ZERO spec amendment; ZERO cross-axis cascade verified — pure deployment-time-opt-in-gate close via mech-β AC #8 e2e green proof.

**Sub-species 7.deployment-time-opt-in-gate SECOND CLOSURE** — joins AS-8d batch-31 (FIRST member); sub-species 7.deployment-time-opt-in-gate now has 2 closures in ledger. **NINTH RETIRE-READY → RETIRED close overall in ledger history. FIRST OD-axis deployment-time-opt-in-gate closure. JOINT same-arc cross-axis RETIRE-READY closure** (AS-8d + OD-5 share PR #14 upstream merge `24a9363`; first ledger event of this shape).

**Cardinality delta at this batch:** OD-axis RETIRED 2/8 → 3/8 (25.0% → 37.5%); workspace RETIRED 36/54 → 37/54 (66.7% → 68.5%); workspace RETIRE-READY 1/54 → 0/54 (**bucket EMPTY at workspace layer — FIRST TIME in ledger history**); workspace PARTIAL unchanged at 4/54; workspace STILL-BOUNDED unchanged at 11/54; workspace STILL-BOUNDED-INDEFINITELY unchanged at 2/54; workspace pipeline-advanced 41/54 = 75.9% (unchanged — within-tier promotion). **Cardinality check at batch-32 close: 37 + 0 + 4 + 11 + 2 = 54 ✓.** Forward-only ledger discipline preserved at prior batch records.

### §11.4f H_T-CP-8 — PARTIAL → RETIRED at batch-47 (sub-species 7e first instance)

The pre-batch-47 CP-axis CP-8 row §5 PARTIAL classification (row line 111 "1 of 17 spec edges; 8 source units DEFERRED") is **superseded** by the direct X-AL-2 first-conjunct satisfaction closure event filed at `batch-47` (2026-05-29; sibling-arc to batch-46 H_T-RT-35 RETIRE-READY → RETIRED close at fork doc `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` paired transit):

- Gap A composer library COMPLETE on main `35744ab` via PRs #39–#44 (U-CP-74..79); 7 of 7 spec §12.3 source units disposed (5 substantive composer landings + 2 reclassified NOT-APPLICABLE at CP spec v1.25 §16.5.10 per impl-time grounding pass — U-CP-12 declarative-only + U-CP-52 runtime-axis-composed).
- Gap B U-CP-14 shape divergence RESOLVED via (S) sibling-variant at CP spec v1.25 → v1.26 (commit `ec4a2f7`) per `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md` operator-ratified 2026-05-28; sibling composer `emit_override_state_ledger_entry` LANDED at U-CP-74 PR #39 (`e63a600`); ZERO `CPAuditLedgerEntry` 8-field shape amendment; ZERO C-CP-20 §20.4 signing contract amendment; ZERO CP-audit-axis cascade.
- Gap C runtime spec §12.3 prose drift DEFERRED per (C-defer) ratification at runtime plan v2.34 — Class 3 informational doc-hygiene, NOT a retirement gate under X-AL-2; impl conforms to IS HEAD directly per CP spec v1.26 §16.5.8 Q4 ratification anchor.
- X-AL-2 first conjunct (cited unit IDs landed) MET at U-CP-18 LANDED + U-CP-34 LANDED + U-CP-74..79 LANDED (5 substantive + 2 reclassified). X-AL-2 second conjunct (H_E surface no longer invoked at substitution site) **MET BY CLASSIFICATION** — Meta-Architecture §5 row for CP-8 = "None — depends on H_T-IS-5, H_T-IS-7"; H_E coverage table = ✗ ("Depends on IS-axis primitives absent in H_E"). No H_E surface exists at the CP-8 substitution site; nothing to "no longer invoke."

**Sub-species 7e FIRST CLOSURE** — `composer-library-complete-with-no-H_E-surface-classification` catalogued at `.harness/phase-7d-retirement-events-batch-47.md` §2; discriminated from sub-species 7d (LANDED-substrate-pending-upstream-loop-substrate) by H_E surface presence at the substitution site. Sub-species 7 lineage cardinality post-batch-47: **12 events across 5 sub-species** (7a=3 + 7b=1 + 7c=1 + 7d=6 + 7e=1). **TENTH PARTIAL → RETIRED close overall in ledger history**; **FIRST direct X-AL-2 first-conjunct close at a "✗ absent (no H_E surface)" Meta-Architecture classification row**.

**Cardinality delta at this batch:** CP-axis RETIRED 19/22 → 20/22 (86.4% → 90.9%); workspace RETIRED 43/54 → 44/54 (79.6% → 81.5%); workspace PARTIAL 5/54 → 4/54 at active-substitution view (§11.1a corrective accounting baseline); workspace pipeline-advanced 48/54 = 88.9% (unchanged — within-pipeline-advanced PARTIAL → RETIRED transit). **Cardinality check at batch-47 close: 44 + 0 + 4 + 4 + 2 = 54 ✓** (preserves §11.1a corrective baseline 43 + 0 + 5 + 4 + 2 = 54). Forward-only ledger discipline preserved at prior batch records; row line 111 text PRESERVED VERBATIM per §0.5 forward-only discipline + this §11.4f supersession is the canonical disposition going forward.

**Fork doc closure:** `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` transitions to CLOSED — paired transit completed at batches 46 (H_T-RT-35) + 47 (H_T-CP-8). Fork doc closure-back-reference appended at fork doc per §"Cross-axis observability" discipline.

### §11.4g H_T-CP-9 — PARTIAL → RETIRED at batch-48 (sub-species 7a 4th closure)

The pre-batch-48 CP-axis CP-9 row §5 PARTIAL classification (row line 112 "Replay-resumption materialized via `_determine_resume_at`... 5-class `ResumptionKind` taxonomy NOT emitted by driver (only binary RESUMPTION event class)") is **superseded** by the sub-species 7a `operator-explicit-deferred-close-gate` closure event filed at `batch-48` (2026-05-29; 4th sub-species 7a closure joining CP-19 batch-22 + CP-14 batch-29 + CP-11 batch-30):

- CP spec v1.6 §25.5 line 375 `workflow.resumption` CONDITIONAL row v1.4 scope carve-out: "Only if driver entry is a re-entry per §8 replay-resumption semantics. At v1.4 scope: emit on re-entry if `manifest_entry.engine_class == 'save-point-checkpoint'` AND `run_id` matches a prior `Spec_Information_Substrate_v1.md` C-IS-05 ledger entry." Preserved verbatim through CP spec v1.27 per delta-only-spec-file convention.
- Production at `harness-cp/src/harness_cp/workflow_driver.py:725-746` emits binary `WorkflowEventClass.RESUMPTION` IN COMPLIANCE with §25.5 v1.4 scope carve-out — two emission paths fire on (i) `resume_at_step_index_override is not None` and (ii) `manifest_entry.engine_class is EngineClass.SAVE_POINT_CHECKPOINT`. Inline comment at lines 738-746 explicitly cites the v1.4 scope carve-out and documents §8.1's 5-class `ResumptionKind` enum + §8.3's universal observable behavior as the full contract space; §25.5 carves out the v1.4 implementation scope.
- X-AL-2 first conjunct (cited unit IDs landed) MET at U-CP-19 / U-CP-20 / U-CP-21 LANDED at runtime impl per CP spec §25.5 + §8.1 + §8.3 contract surfaces; X-AL-2 second conjunct (H_E surface no longer invoked at substitution site) MET — production typed `LifecycleEmitter` carrier displaces H_E `--resume` / `--continue` / `--fork-session` shell-out at the substitution site; 5-class expansion at non-`save-point-checkpoint` engine classes carries as bounded-residual per X-AL-2 + ledger v2 §0.5 bounded-residual discipline at sub-species 7a closure shape.

**Sub-species 7a 4th CLOSURE — FIRST anchored at CP spec authority surface.** CP-19 batch-22 closed via Layer 3 in-process reframe at v1.6 e2e scope; CP-14 batch-29 + CP-11 batch-30 closed via runtime spec v1.6 §14.7.2 step 5 v1.6 MVP scope carve-out. CP-9 batch-48 anchors at CP spec v1.6 §25.5 line 375 — DISTINCT spec authority anchor from CP-11/CP-14. Sub-species 7a now spans **2 distinct spec-explicit operator-discretion authority anchors** demonstrating cross-spec-anchor closure path generalization within a single sub-species. Sub-species 7 lineage cardinality post-batch-48: **15 events across 7 sub-species** (7a=4 + 7b=1 + 7c=1 + 7d=6 + 7e=1 + 7f=2 + 7g=2).

**Cardinality delta at this batch:** CP-axis RETIRED 20/22 → 21/22 (90.9% → 95.5%); CP-axis PARTIAL 2/22 → 0/22 (**CP-axis PARTIAL bucket EMPTY for FIRST TIME in ledger history**); workspace RETIRED 44/54 → 45/54 (81.5% → 83.3%); workspace pipeline-advanced 48/54 = 88.9% (unchanged — within-pipeline-advanced PARTIAL → RETIRED transit). **Cardinality check at batch-48 close: 45 + 0 + 3 + 0 + 3 = 51 active substitutions + 3 SB-INDEF = 54 ✓** (preserves batch-47 corrective baseline 44 + 0 + 4 + 0 + 3 = 51 active + 3 indef = 54). Forward-only ledger discipline preserved at prior batch records; row line 112 text PRESERVED VERBATIM per §0.5 forward-only discipline + this §11.4g supersession is the canonical disposition going forward.

**Catalogue keep-its-keep validation.** PR #76 consolidated retirement-event-pattern catalogue at `.harness/retirement-event-pattern-catalogue.md` merged at `ddeede6` 2026-05-29 ~30 min prior to batch-48 authoring. 4th sub-species 7a closure citing canonical sub-species naming from PR #76 §1.1 validates the catalogue discipline empirically — same-session-sequel keep-its-keep per workflow v1.11 §7.4.7.2 sub-species 5.1 lineage.

### §11.4h H_T-IS-2 — STILL-BOUNDED → PARTIAL (batch-49) → RETIRED (batch-50)

The §3 row line 75 STILL-BOUNDED classification ("Typed library exists (`harness-is/.../artifact_tier_registry.py`); zero bootstrap composer invokes `materialize_artifact_tier_registry`; cross-tier traceability invariant unenforced at append-time") is **superseded** by the substantive substitution-retirement arc closed at `batch-50` (2026-05-31). The intervening STILL-BOUNDED → PARTIAL transit (`batch-49`, 2026-05-30) was recorded at `harness-is/CLAUDE.md` §4.1 (live status) but not catalogued at §11; this entry records the full transit:

- **batch-49 (substrate landing, STILL-BOUNDED → PARTIAL):** IS spec v1.3 §C-IS-05 §5.1 (`EntryPayload.procedural_tier_snapshot_ref` sidecar) + §5.2 (`resolve_procedural_tier_snapshot` resolver contract) + §C-IS-02 line 170 substantive-runtime-gate authored; carrier + `StateLedgerEntry` D-derivative field + `entry_hash.canonicalize` contribution landed at harness-is; resolver primitive + `make_procedural_tier_snapshot_resolver(ctx)` factory landed at runtime axis (residence per Q-γ=(γ-2) per `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` §11.4). X-AL-2 first conjunct MET; second conjunct BOUNDED (producer-site call-sites not yet lifted).
- **batch-50 (producer-site cascade complete, PARTIAL → RETIRED):** all 13 producer sites handled — 6 §16.5 CP→IS composers populate the sidecar (PR #107 Reading C apply `89915af`); 4 active-workflow-context sites lifted (R-003 Cluster A PR #136 `sub_agent_dispatch` + `hitl_gate_composer`; Cluster B PR #137 `workflow_driver._append_step_ledger_entry` + `sibling_ledger_entry_composition`); 3 outside-context sites documented `None`-canonical per IS §5.1 (`audit_writer`, `as_is_wiring`, `shadow_git_rollback`).
- **X-AL-2 second conjunct MET at batch-50:** the H_E convention-substitution (manual cross-tier traceability via `action_id` text per `CLAUDE.md`-declared tier-naming convention) is no longer invoked at any active-workflow-context producer site; cross-tier traceability is now programmatic (typed sidecar field, resolver-populated) + hash-chained at append-time. Empirically verified at HEAD `e736f53`. Both conjuncts MET → **RETIRED** (substantive-substrate-lift close shape; NOT vacuous/authoring-only/categorical-mismatch).

**Cardinality delta at batch-50:** IS-axis RETIRED 8/9 → **9/9 (100%)** — IS-axis PARTIAL bucket EMPTY; **FIRST axis fully RETIRED at the strict RETIRED view** (CP-axis reached PARTIAL-bucket-empty at batch-48 but carries bounded-residual rows). Workspace RETIRED 45/54 → **46/54 (85.2%)** (anchored to batch-49 footer baseline); workspace pipeline-advanced UNCHANGED at 49/54 = 90.7% (within-pipeline-advanced PARTIAL → RETIRED transit); workspace PARTIAL −1 (IS-2 transits out). Row line 75 text PRESERVED VERBATIM per §0.5 forward-only discipline; this §11.4h supersession is the canonical disposition going forward.

### §11.4i H_T-OD-3 — RETIRE-READY → RETIRED at batch-51 (substantive; sub-species 10 THIRD closure)

The `harness-od/CLAUDE.md` §4.1 OD-3 RETIRE-READY classification (batch-36) is **superseded** by the RETIRE-READY → RETIRED substantive transit at `batch-51` (2026-06-01, closing roadmap R-007). Disposition via the `gate-text-stale-vs-production-landings` audit (workflow v1.12 §7.4.7.2 sub-species 10; THIRD closure after OD-1 batch-37 + OD-7 batch-38; FIRST sub-species-10 close where the primitive has live runtime behavior rather than authoring-only typed-declaration). X-AL-2 both conjuncts MET: (A) U-OD-09→U-OD-12 landed; (B) the H_E 7a-scaffold sampler is no longer invoked — `HarnessCompositeSampler` is the live root sampler at `materialize_tracer_provider_stage`, exercised by the R-100-mvp-real-workflow-execution e2e. "Tail-keep at OTLP collector observing §10.2 preservation" reframed as roadmap R-430 production-feature-validation (infra-gated), NOT an X-AL-2 retirement gate. Operator-ratified AskUserQuestion 2026-06-01.

### §11.4j H_T-OD-6 — RETIRE-READY → RETIRED-AS-BOUNDED-RESIDUAL at batch-51 (FIRST bounded-residual close in the ledger)

The `harness-od/CLAUDE.md` §4.1 OD-6 RETIRE-READY classification (batch-33) is **superseded** by the RETIRE-READY → RETIRED-AS-BOUNDED-RESIDUAL transit at `batch-51` (2026-06-01, closing roadmap R-009). **FIRST RETIRED-AS-BOUNDED-RESIDUAL close in the ledger** per X-AL-2 §5.3 bounded-residual carry-forward (Surface VIII / Phase-8 disposition shape). Condition-(B) audit: 4-OD-B SqliteWritePath substrate LANDED (criterion A MET) but `RuntimeRingBuffer.flush_to_sqlite` is dormant at MVP (zero production callers; the collector→sqlite loop is not wired into the run path), so the boundary has not moved — substantive RETIRED is not honestly available at MVP. Documented residual + future-milestone pointer (operator deploys the collector daemon wired; roadmap R-420/R-421, infra-gated). Operator-ratified AskUserQuestion 2026-06-01 (Class 2 in-execution decision per `phase-7-substitution-retirement` §5.3).

**Cardinality delta at batch-51:** OD-axis RETIRED 5/8 → **7/8 (87.5%)** (OD-3 substantive + OD-6 bounded-residual sub-disposition); OD-axis RETIRE-READY 2/8 → **0/8 (bucket EMPTY)**; OD-axis PARTIAL unchanged at 1/8 (OD-4). Workspace RETIRED 46/54 → **48/54 (88.9%)** (OD-3 +1 substantive; OD-6 +1 counted as accounted/closed per Surface VIII "RETIRED or RETIRED-AS-BOUNDED-RESIDUAL", carrying the bounded-residual sub-disposition); workspace RETIRE-READY 2/54 → **0/54**; workspace pipeline-advanced UNCHANGED at 49/54 = 90.7% (both are within-pipeline-advanced RETIRE-READY → RETIRED transits per X-AL-2). Closes 2 R-700 Phase-8 blockers (R-007 + R-009). Per-axis CLAUDE.md §4.1 row text refreshed at this tier-transit per workflow v1.12 §7.4.7.3.C; these §11.4i + §11.4j supersessions are the canonical disposition going forward.

### §11.5 Cumulative status pointer

| | Live source |
|---|---|
| Latest filed batch | `batch-51` (2026-06-01, H_T-OD-3 RETIRE-READY → RETIRED substantive + H_T-OD-6 RETIRE-READY → RETIRED-AS-BOUNDED-RESIDUAL — closes roadmap R-007 + R-009; **OD-axis RETIRE-READY bucket EMPTY; FIRST bounded-residual close in the ledger**; see §11.4i + §11.4j). Prior: `batch-50` (2026-05-31, H_T-IS-2 PARTIAL → RETIRED; IS-axis 9/9 = 100%). |
| Cumulative RETIRED count (raw ledger) | 48/54 (88.9%) per batch-51 §0 (IS-axis 9/9 = 100%; CP-axis 21/22 = 95.5%; OD-axis 7/8 = 87.5% incl. 1 RETIRED-AS-BOUNDED-RESIDUAL = OD-6). **→ SUPERSEDED FORWARD to Phase-8-graduation canonical `46/54 (85.2%)` per `.harness/phase-8-graduation.md` (2026-06-02).** The raw-ledger 48 over-counted by 2 (un-folded CXA accounting §11.1a line 278 + CP-17 SB-INDEF reclassification + CP-21-vs-22 / AS-3↔AS-9 bookkeeping ambiguities); operator-ratified accounting (i) at PR #246. Prior batch records stand verbatim per §0.5; see §11.7. |
| Cumulative pipeline-advanced (RETIRED + RETIRE-READY + PARTIAL) | 49/54 (90.7%) per batch-51 §0 (UNCHANGED at batch-51 — OD-3 + OD-6 within-pipeline-advanced RETIRE-READY → RETIRED transits) |
| Per-axis live status | `harness-{is,as,cp,od}/CLAUDE.md` §4.1 |
| Cross-axis cascade live status | §6.3.1 + §6.3.2 cascade re-evaluations at the batch in which the gating retirement filed (see batch-2 §3 + batch-3 referenced from `harness-od/CLAUDE.md`) |

### §11.6 Refresh footer

| Field | Value |
|---|---|
| Refresh date | 2026-05-27 |
| Trigger | Candidate batch-20 evaluation for H_T-OD-2 PARTIAL → RETIRE-READY driven by Path A production-emission at `e874a03` surfaced that OD-2 was already RETIRED at batch-2; halt-and-redirect produced this doc-hygiene refresh instead of a batch-20 frame |
| Skill | `phase-7-substitution-retirement` §7 halt condition routing — substitution already RETIRED at predecessor batch is not a new retirement event; doc-hygiene supersession is the correct disposition |
| Scope | §0.5 snapshot supersession header + §11 surfaced supersession map; ZERO mutation of §3–§9 row text per forward-only ledger discipline |
| Retirement-count delta | ZERO. This refresh does NOT file a new retirement transition; it documents that prior transitions filed at batches 2–19 supersede the 2026-05-20 snapshot's row verdicts |

---

### §11.7 Phase-8 graduation canonical-count supersession (2026-06-02)

**Trigger.** Operator lifted the HELD R-700 Phase-8 declaration ("kick off the declaration"). The formal close is recorded at `.harness/phase-8-graduation.md`; this section is the ledger-side forward supersession per §0.5 forward-only discipline (prior batch records + §11.5 raw-ledger figures stand verbatim).

**Canonical Phase-8 accounting (supersedes the raw-ledger 48 going forward):**

| Metric | Canonical | Prior raw-ledger |
|---|---|---|
| RETIRED | **46/54 (85.2%)** | 48/54 (88.9%) |
| Pipeline-advanced | **49/54 (90.7%)** | 49/54 (UNCHANGED) |

**Disposition (operator-ratified accounting (i), PR #246 + graduation doc §3):** 36 substantive-RETIRED + 8 RETIRED-AS-AUTHORING-ONLY + 2 RETIRED-AS-BOUNDED-RESIDUAL (CP-16, OD-6) = **46 RETIRED**; + 3 PARTIAL (OD-4, CXA-1, CXA-4) + 2 STILL-BOUNDED (CXA-2, CXA-3) + 3 STILL-BOUNDED-INDEFINITELY (AS-8e, AS-8f, CP-17) = 54 ✓.

**8 terminal sign-off dispositions (graduation doc §4) — labels do NOT re-tally into the 46:** OD-4 → `RETIRED-AS-CROSS-AXIS-DEFERRED` (NEW class; pipeline-advanced PARTIAL, not in the 46); AS-8e/AS-8f/CP-17 → accepted-indefinite-defer (NOT counted; distinct from the *counted* RETIRED-AS-BOUNDED-RESIDUAL of CP-16/OD-6); CXA-1/2/3/4 → Phase-2-runtime-deferred.

**Retirement-count delta vs §11.5 raw ledger:** −2 RETIRED (48 → 46) — a bookkeeping reconciliation, NOT a regression. No substitution re-opened. The 48 over-counted the un-folded CXA accounting (§11.1a line 278) + the CP-17 SB-INDEF reclassification.

**Phase 8: substitution accounting CLOSED.**

**Canonical source from the Phase-8 declaration until the next real transit (R-600-substitution-ledger-schema):** the per-row dispositions + the 46/49/54 integers were DERIVED from `.harness/substitutions.yaml` via `tools/substitution_ledger.py` (`--summary` for live counts; `--check` is the CI tally gate that fails on an impossible tally). These prose figures CITE that derivation — they are no longer hand-maintained. A real retirement-event transit edits the row's `disposition` + the yaml `snapshot:` block (forward-only); §11.8 / batch-52 is that next transit and supersedes these integers for the live ledger.

---

### §11.8 Post-Phase-8 Files / Managed Agents back-flow (2026-06-08)

**Trigger.** The operator opened the previously deferred Files and Managed Agents arcs after Phase 8 closed. R-810 live-proved Anthropic Files upload/reference/delete and managed-cloud `files.operation` export; R-820 live-proved Anthropic Managed Agents SDK/session integration and managed-cloud `managed_agents.*` export. Batch-52 records the forward-only accounting transit.

**Live ledger accounting after batch-52:**

| Metric | Live ledger | Phase-8 declaration |
|---|---|---|
| RETIRED | **49/54 (90.7%)** | 46/54 (85.2%) |
| Pipeline-advanced | **52/54 (96.3%)** | 49/54 (90.7%) |

**Disposition delta:** AS-8e, AS-8f, and CP-17 move from `SB_INDEFINITE` to `SUBSTANTIVE_RETIRED`; SB-INDEFINITE is now **0/54**. The remaining non-RETIRED rows are OD-4, CXA-1, CXA-2, CXA-3, and CXA-4.

**Historical boundary.** §11.7 and `.harness/phase-8-graduation.md` remain the historical Phase-8 declaration. This §11.8 is a post-Phase-8 back-flow supersession for the live ledger only.

---

### §11.9 Post-Phase-8 OD-4 / CXA-4 accounting back-flow (2026-06-08)

**Trigger.** A later accounting/back-flow pass audited the remaining rows after batch-52 in logical dependency order. R-008's runtime residual was closed by the already-landed §13.1 redaction toggle plus the §13.2 opaque-token, durable audit-ledger token-map, provider-free category-classifier, and eval-grade runtime tokenization slices. R-CXA-4's grounding record found 0 remaining wireable edges: the lone genuine OD audit-write data-flow was already wired with production producers, phase-2 runtime composers were already materialized at bootstrap stage 6, and convention edges were already satisfied by manifest/namespace checks. Batch-53 records the forward-only accounting transit.

**Live ledger accounting after batch-53:**

| Metric | Live ledger | Phase-8 declaration |
|---|---|---|
| RETIRED | **51/54 (94.4%)** | 46/54 (85.2%) |
| Pipeline-advanced | **52/54 (96.3%)** | 49/54 (90.7%) |

**Disposition delta:** OD-4 and CXA-4 move from `PARTIAL` to `SUBSTANTIVE_RETIRED`. The remaining non-RETIRED rows are CXA-1 (`PARTIAL`), CXA-2 (`STILL_BOUNDED`), and CXA-3 (`STILL_BOUNDED`).

**Historical boundary.** §11.7 and `.harness/phase-8-graduation.md` remain the historical Phase-8 declaration; §11.8 remains the batch-52 back-flow record. This §11.9 is a post-Phase-8 back-flow supersession for the live ledger only.

---

### §11.10 Post-Phase-8 CXA-3 runtime-composer back-flow (2026-06-08)

**Trigger.** The operator rejected Memory-only/current-MVP scope narrowing for R-CXA-3 and directed the CP→AS runtime-composer path. The implementation lands `RuntimeCpAsWiring`, binds it during stage 6, and exposes it as `HarnessContext.cp_as_wiring`. Batch-54 records the forward-only accounting transit.

**Live ledger accounting after batch-54:**

| Metric | Live ledger | Phase-8 declaration |
|---|---|---|
| RETIRED | **52/54 (96.3%)** | 46/54 (85.2%) |
| Pipeline-advanced | **53/54 (98.1%)** | 49/54 (90.7%) |

**Disposition delta:** CXA-3 moves from `STILL_BOUNDED` to `SUBSTANTIVE_RETIRED`. The remaining non-RETIRED rows are CXA-1 (`PARTIAL`) and CXA-2 (`STILL_BOUNDED`).

**Historical boundary.** §11.7 and `.harness/phase-8-graduation.md` remain the historical Phase-8 declaration; §11.8 and §11.9 remain the batch-52 and batch-53 back-flow records. This §11.10 is a post-Phase-8 runtime-composer supersession for the live ledger only.

---

### §11.11 Post-Phase-8 CXA-2 bounded-residual back-flow (2026-06-09)

**Trigger.** R-CXA-2's MVP-safe CP->IS producer surface advanced after batch-54: U-CP-78 Reading A landed, provider-neutral HITL and engine recovery producer loops were bound at stage 5, direct CP->IS emissions were proved through the bound runtime context, and Anthropic non-memory provider-turn `tool_use` continuation now runs through `ctx.hitl_tool_loop`. The remaining durable recovery concern is post-MVP deployment hardening: the ratified DP-2 decision forbids extending `workflow_driver.py` to impersonate an engine recovery loop and re-opens only when a real event-sourced replay, reconciler, WAL-segment, or engine-native-pause recovery loop lands. Batch-55 records that bounded-residual transit.

**Live ledger accounting after batch-55:**

| Metric | Live ledger | Phase-8 declaration |
|---|---|---|
| RETIRED | **53/54 (98.1%)** | 46/54 (85.2%) |
| Pipeline-advanced | **54/54 (100.0%)** | 49/54 (90.7%) |

**Disposition delta:** CXA-2 moves from `STILL_BOUNDED` to `BOUNDED_RESIDUAL`. The only remaining non-RETIRED row is CXA-1 (`PARTIAL`).

**Historical boundary.** §11.7 and `.harness/phase-8-graduation.md` remain the historical Phase-8 declaration; §11.8, §11.9, and §11.10 remain the batch-52, batch-53, and batch-54 back-flow records. This §11.11 is a post-Phase-8 bounded-residual supersession for the live ledger only.

---

### §11.12 Post-Phase-8 CXA-1 AS->IS edge-scope back-flow (2026-06-09)

**Trigger.** R-CXA-1's AS->IS producer-gated seam advanced after batch-55. PR #458 moved scoped secret-fetch audit production to the active `TOOL_STEP` dispatch site. The follow-on edge-scope audit found that the legacy "remaining ~12 callbacks" wording no longer matched the current direct AS->IS overlay inventory: U-AS-19 and U-AS-28 are read-only IS carrier consumers, while U-AS-26/U-AS-27 are the secret-fetch audit compose/write family. This branch threads the R-003 procedural-tier resolver into the production `RuntimeAsIsWiring` write and batch-56 records the substantive transit.

**Live ledger accounting after batch-56:**

| Metric | Live ledger | Phase-8 declaration |
|---|---|---|
| RETIRED | **54/54 (100.0%)** | 46/54 (85.2%) |
| Pipeline-advanced | **54/54 (100.0%)** | 49/54 (90.7%) |

**Disposition delta:** CXA-1 moves from `PARTIAL` to `SUBSTANTIVE_RETIRED`. No canonical substitution row remains outside a counted RETIRED disposition.

**Historical boundary.** §11.7 and `.harness/phase-8-graduation.md` remain the historical Phase-8 declaration; §11.8, §11.9, §11.10, and §11.11 remain the batch-52, batch-53, batch-54, and batch-55 back-flow records. This §11.12 is a post-Phase-8 AS->IS seam supersession for the live ledger only.

---

*End of phase-7d-retirement-ledger v2 (second pass against Phase 2 runtime closure) + 2026-05-27 supersession refresh + 2026-06-02 Phase-8 graduation supersession (§11.7) + 2026-06-08 post-Phase-8 back-flow (§11.8) + 2026-06-08 OD-4/CXA-4 back-flow (§11.9) + 2026-06-08 CXA-3 runtime-composer back-flow (§11.10) + 2026-06-09 CXA-2 bounded-residual back-flow (§11.11) + 2026-06-09 CXA-1 AS->IS back-flow (§11.12).*
