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

### §11.5 Cumulative status pointer

| | Live source |
|---|---|
| Latest filed batch | `batch-19` (2026-05-26, H_T-AS-4 PARTIAL → RETIRED) |
| Cumulative RETIRED count | 28/49 (57.1%) per batch-19 §0 footer |
| Cumulative pipeline-advanced (RETIRED + RETIRE-READY + PARTIAL) | 35/49 (71.4%) per batch-19 §0 footer |
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

*End of phase-7d-retirement-ledger v2 (second pass against Phase 2 runtime closure) + 2026-05-27 supersession refresh.*
