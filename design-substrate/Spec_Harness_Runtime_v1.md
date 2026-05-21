# Specification — Harness Runtime v1.7

## Change-note (v1.6 → v1.7)

**Scope of revision.** Phase-7 in-CLI revision absorbing operator-ratified **U-RT-59 Fork 2 implementation arc** per `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` §10 routing chain (Path D + Path B-revised-a both landed 2026-05-20; this v1.7 amendment lands the runtime-side composer-step contract that materializes both). The Fork 2 design-substrate work is complete (CXA v2.4 + CP spec v1.7 §13.5.1 + ADR-D5 v1.4 + OD spec v1.5 C-OD-24); v1.7 amends §14.7.2 step 8 to specify the runtime composer step that exercises the now-complete CP→OD audit-write seam end-to-end.

**Single amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§14.7.2 step 8 (revised)** | The v1.6 step 8 prose (which asserted v1.6 emits via `ctx.audit_ledger_writer.append(...)` directly with the CP-shape entry — a spec-vs-code drift since the code at HEAD does NOT emit per Fork 2 strike) is **replaced with the Path D + B-revised-a composer-step sequence**: (a) compose `CPAuditLedgerEntry` via `ctx.handoff_registry.compose_dispatch_audit(...)` per existing C-CP-13 §13.5 (unchanged); (b) write F2 state-ledger entry for the dispatch action via `ctx.state_ledger_writer.append(...)` → capture `StateLedgerEntryRef`; (c) convert CP→OD via `cp_audit_to_od_audit(cp_entry, key_id=..., algo=..., entry_core=<step-b ref>)` per `Spec_Control_Plane_v1_7.md` §13.5.1; (d) append OD `AuditLedgerEntry` to `ctx.audit_writer.append(tenant_id, od_entry)` per C-RT-04. **Class 3 drift item 1 RESOLVED at this v1.7 amendment**: the v1.6 prose's `ctx.audit_ledger_writer` field name (drifted from C-RT-04's canonical `ctx.audit_writer` per `.harness/class_3_tension_u_rt_59_spec_prose_drift.md` item 1) corrected at v1.7 step 8 rewrite. | Operator-ratified Path D + B-revised-a implementation arc; `Spec_Control_Plane_v1_7.md` §13.5.1 (converter contract); `Spec_Operational_Discipline_v1_5.md` C-OD-24 (OD-side spec-anchored schema); `Cross_Axis_Composition_Document_v2_4.md` §2.3.7 (CXA edge); `ADR-D5.md` v1.4 §1.4 (storage-form reconciliation); `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` (full discovery + sub-questions ratification trail); `.harness/class_1_tension_u_rt_59_cp_to_od_audit_write_gap.md` (fork closure substrate); landed code at `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py` (production callsite — currently STRUCK per fork resolution; un-strike owed at the implementation landing commit, post this v1.7 amendment). |

**U-RT-59 plan AC #9 un-strike (downstream absorption owed).** Per `.harness/phase-2-session-3-track-a-atomic-decomposition.md` v2.5 L9-ter AC #9: the write-half of AC #9 was STRUCK at U-RT-59 landing per `[[halt-route-split-AC-pattern]]` discipline. v1.7 §14.7.2 step 8 now specifies the write-half contract; the AC #9 un-strike + un-strike-aware test reauthoring is owed at the implementation landing commit (next session per phase-7-implementation skill discipline against this v1.7 contract).

**Sections preserved verbatim from v1.6.** All v1.6 content outside §14.7.2 step 8 preserved unchanged. The §14.7.1 architectural surfaces enumeration is preserved verbatim (the new F2-write + CP→OD convert + audit_writer.append surfaces are operationally introduced at step 8's rewrite, not declared as new architectural surfaces — they compose against existing C-RT-04 `audit_writer` field + IS state-ledger writer + CP spec v1.7 §13.5.1 converter contract). The §14.7.3 + §14.7.4 + §14.7.5+ sub-sections + §14 failure-mode taxonomy + §15 traceability all preserved verbatim from v1.6.

**RuntimeSubAgentDispatcher constructor signature impact.** The v1.7 §14.7.2 step 8 sequence requires `RuntimeSubAgentDispatcher` to access (a) `ctx.state_ledger_writer` for the F2-write at step (b); (b) `ctx.audit_writer` for the OD append at step (d); (c) signing config (`key_id`, `algo`) for the converter call at step (c). The v1.6 dispatcher constructor took `ctx.handoff_registry` + `ctx.topology_dispatcher` + `child_workflow_runner` only; the v1.7 amendment requires extension to bind the new dependencies. Constructor extension is deferred to the implementation landing commit per phase-7-implementation discipline; v1.7 spec commits the composer-step semantics, the constructor wiring follows.

**Status posture.** Proposed (v1.6) → **Proposed (v1.7)**. Adversarial-review pass scheduled at U-RT-59 implementation landing per Phase 7 sub-phase 7b discipline.

**Downstream absorption owed.** (a) `.harness/phase-2-session-3-track-a-atomic-decomposition.md` v2.5 → v2.6 — un-strike U-RT-59 AC #9 write half; cite v1.7 §14.7.2 step 8 contract; (b) `Spec_Control_Plane_v1_8.md` Form A patch — update v1.7 §13.5.1 NOTE 1 + NOTE 2 references from "drift-resolution-arc-pending" to "drift-resolved-at-ADR-D5-v1.4 + OD-spec-v1.5 + runtime-spec-v1.7" (co-published with this v1.7 amendment); (c) workspace `CLAUDE.md` §2.3 contract count update (OD 23 → 24 per OD spec v1.5 C-OD-24); (d) CP plan v2.13 → v2.14 absorption at U-CP-28 + OD plan v2.11 → v2.12 absorption at U-OD-00; (e) converter code move `harness-runtime/lifecycle/cp_audit_conversion.py` → `harness-cxa/src/harness_cxa/cp_audit_conversion.py` per Q5 ratification; (f) composer wiring + tests + AC #9 un-strike at the implementation landing commit.

---

## Change-note (v1.5 → v1.6)

**Scope of revision.** In-CLI spec growth per workspace `CLAUDE.md` §4.3 + memory `design-substrate-divergence` (design-phase back-flow deprecated 2026-05-15; workspace `design-substrate/` is canonical; spec edits in-CLI). New runtime composition contract for sub-agent dispatch — the runtime-side production callsite for `RuntimeHandoffRegistry` (U-RT-26 landed) + `RuntimeTopologyDispatcher` (U-RT-40 landed) + the `subagent.*` / `topology.*` span namespaces declared at CP spec C-CP-13 + C-CP-14. Same architectural shape as the v1.4 C-RT-16 amendment: contract pins the producer site for an upstream-CP-declared observability surface; runtime owns the composition seam.

**Operator ratifications** (recorded 2026-05-20 in-session):

- **Routing-layer architecture: StepKindDispatcherRegistry.** The driver currently binds one `StepDispatcher` (the C-RT-16 wrapper). Supporting a second step_kind (`SUB_AGENT_DISPATCH`) requires a routing layer. Operator ratified the registry shape: bootstrap binds `{StepKind → StepDispatcher}`; driver dispatches by `step.kind`. Each `StepDispatcher` impl handles one kind. The C-RT-16 wrapper becomes the `INFERENCE_STEP` dispatcher binding. Preserves the C-CP-25 §25.3.3.4 "step body opaque to driver" invariant — the driver still does not introspect `step.step_payload`, but does read `step.kind` to route to the correct dispatcher. Extensible to all 5 step_kinds for follow-on tool-invocation / HITL / validator composer arcs.
- **Scope: single-sub-agent within linear parent.** C-CP-14 declares the full fan-out span hierarchy + concurrent-prompt-cache warm-up (§14.4) + cross-family fallback at fan-out (§14.5), but the parent workflow at C-CP-25 v1.4 is `SINGLE_THREADED_LINEAR` only. A SUB_AGENT_DISPATCH step within a linear parent dispatches one sub-agent. v1.6 pins single-sub-agent dispatch + the `subagent.*` namespace (full) + the `topology.*` namespace (narrow subset: `topology.pattern`, `topology.workload_class`, single-sibling result counts). Fan-out warm-up + cross-family fallback at fan-out are NOT in scope at v1.6 (gated on parent topology expansion at C-CP-25; separate arc).
- **Invocation primitive: in-process recursive sub-workflow invocation.** The actual "run the sub-agent" primitive was missing pre-v1.6 (only descent + brief + audit composition existed). Operator ratified: `RuntimeSubAgentDispatcher` re-enters the workflow execution surface (per C-RT-08 `run()` discipline; recursive `execute_workflow()` invocation) with the child's bound HandoffContext + brief. Child runs as a full sub-workflow with its own steps + spans + ledger entries. The dispatcher reads child workflow identity from `step.step_payload` (opaque to driver per C-CP-25 §25.3.3.4; per-step-kind dispatcher knows the payload shape).

**Single-finding addition.** New **§14.7 C-RT-17 — Sub-agent dispatch composer** specifies the runtime composition seam that:
1. Adds `StepKindDispatcherRegistry` as a new runtime-internal type — a frozen mapping `{StepKind → StepDispatcher}` bound at bootstrap stage 5 (LOOP_INIT) alongside `ctx.llm_dispatcher`. Driver dispatches via `ctx.step_dispatchers.lookup(step.kind).dispatch(binding, step)` instead of the v1.5-shape direct `step_dispatcher.dispatch(binding, step)` parameter.
2. Adds `RuntimeSubAgentDispatcher` as the second `StepDispatcher` impl — handles `SUB_AGENT_DISPATCH` steps. Composes `HandoffContext` per C-CP-13 §13.1 7-field payload; calls `ctx.handoff_registry.dispatch(...)` for gate-level descent per C-CP-12; calls `ctx.topology_dispatcher.dispatch(child_manifest_entry)` per C-CP-10 + `is_admissible(...)` per C-CP-10 §10.3; emits `subagent.*` (full namespace per C-CP-14 §14.2) + `topology.*` (narrow subset) span attributes; recursively invokes `execute_workflow()` for the child sub-workflow; composes audit entry via `ctx.handoff_registry.compose_dispatch_audit(...)`; returns child's terminal `RunResult` → step output.

**Sections revised (substantive).**
- New **§14.7 C-RT-17** — Sub-agent dispatch composer contract (after §14.6; §-pin `.7` decimal continuing the §14.5 / §14.6 pattern).
- **§14** failure-mode taxonomy — new row `RT-FAIL-SUB-AGENT-CHILD-FAILED` (permanent; raised when the child sub-workflow's terminal `RunResult.status == FAILED`).
- **§15** Spec-to-plan traceability — new row for U-RT-59 (the new plan unit carrying C-RT-17).

**Sections preserved verbatim from v1.5.** All v1.5 content outside the additions above preserved unchanged. The §14.6 C-RT-16 contract surface stands. The §14.5 C-RT-15 contract surface stands. The v1.5 `retry.*`-canonical-attribute correction stands.

**Status posture.** Proposed (v1.5) → **Proposed (v1.6)**. Class 1 fork (StepDispatcher Protocol parent-context gap) RESOLVED at v1.6 Path A (operator-ratified 2026-05-20; fork record at `.harness/class_1_tension_c_rt_17_step_dispatcher_parent_context_gap.md`). Stage 1 plumbing landed in the same arc: `StepDispatcher` Protocol amended at `Spec_Control_Plane_v1_6.md` §25.2.1 with new keyword-only `step_context: StepExecutionContext` parameter; CP-side type addition at `harness-cp/src/harness_cp/workflow_driver_types.py`; driver loop composes per step + passes; existing dispatcher impls (C-RT-15 + C-RT-16) accept via Protocol conformance (2231 tests green at landing). Adversarial-review pass scheduled at U-RT-59 implementation landing per Phase 7 sub-phase 7b discipline. **U-RT-59 implementation now unblocked**; arc resumes at next session per the L9-ter plan body ACs.

**Downstream absorption owed.** `Implementation_Plan_Harness_Runtime_v*.md` extended with new U-RT-59 (small body authored alongside this spec amendment). CP spec v1.5 unchanged (C-RT-17 emits CP-declared `subagent.*` / `topology.*` namespaces per the C-CP-13 + C-CP-14 schemas; no CP-side amendment). `.harness/phase-7d-retirement-ledger-v2.md` §5 CP rows superseded at U-RT-59 landing event (file ratification target H_T-CP-10 RETIRED + H_T-CP-13 RETIRED + H_T-CP-14 PARTIAL-or-RETIRED at retirement audit). `harness-cp/CLAUDE.md` §4.1 retirement table updated post-landing.

**No fork-record back-reference.** Unlike C-RT-16 (Class 1 fork resolution), C-RT-17 is in-CLI spec growth — no upstream design-substrate defect surfaced; the contract addition is the planned next-arc step authorized at operator ratification this session. Architectural decisions recorded in this change-note rather than in a `.harness/class_N_tension_*.md` file.

---

## Change-note (v1.4 → v1.5)

**Scope of revision.** In-Phase-7 spec-to-spec drift resolution per `.harness/class_1_tension_c_rt_16_retry_attribute_drift.md` (filed + Path A ratified 2026-05-20 during U-RT-58 implementation). Class 1 halt surfaced at AC #4 verification: §14.6 step 4 attribute list named a 6-tuple that did NOT match the canonical CP §3.5 `retry.*` schema (zero overlap; runtime spec author appears to have worked from the pre-v1.3 CP attribute set and improvised). Per workspace `CLAUDE.md` §1.3 authority chain, CP per-axis spec is canonical for CP-owned namespaces; runtime spec cannot rename CP's attributes silently.

**Single-finding correction.** §14.6 step 4 (inner per-attempt span attribute set) re-stated to cite the canonical CP §3.5 6-attribute namespace verbatim. The composer remains the runtime emission site; the attribute schema is CP-canonical:

| Position | Canonical attribute name (CP §3.5) | Source |
|---|---|---|
| 1 | `retry.attempt_number` (integer; 1-indexed) | CP §3.5 v1.3 |
| 2 | `retry.original_span_id` (string; 16-hex W3C trace-context format) | CP §3.5 v1.3 |
| 3 | `retry.delay_ms` (integer; jittered delay per full-jitter backoff) | CP §3.5 v1.3 |
| 4 | `retry.cause_attribution` (string; open-set enum from C5 cause_attribution catalog per C-CP-21) | CP §3.5 v1.3 |
| 5 | `retry.fail_class` (enum: `{transient-retry, Reflexion-recoverable, HITL-recoverable, permanent-fail-exit, terminal-fail-exit}`) | CP §3.5 v1.3 |
| 6 | `engine.replay_disposition` (composition with engine namespace per D1 v1.2 §1.1.1; derived from `binding.engine_class` via `harness_cp.engine_namespace.REPLAY_DISPOSITION_MAPPING`) | CP §3.5 v1.3 + CP §9.1 + D1 v1.2 |

**Producer-side reference.** Wrapper imports the canonical attribute carrier at `harness_cp.retry_fallback_namespace.RETRY_ATTEMPT_CHILD_SPAN_SCHEMA` (landed) rather than hand-coding strings. Ties retirement criterion B verification ("references the canonical attribute carrier") directly to the canonical producer surface.

**Sections revised (substantive).**
- **§14.6** step 4 narrative — attribute list restated canonically (was drifted names; now CP-§3.5 names with byte-exact citation).
- **§14.6** "Invariants" — `retry.*` invariant restated to cite producer carrier.

**Sections preserved verbatim from v1.4.** All v1.4 content outside the §14.6-step-4 corrections preserved unchanged. The §14.6 D1–D6 + Q1=a + Q2=c architectural commitments stand. The C-RT-16 contract surface stands. The composer body discipline (candidate-iteration loop + per-candidate retry loop + breaker pre-check + nested span emission + fail-class taxonomy + reserved registry key extension) stands.

**Downstream absorption owed.** `.harness/phase-2-session-3-track-a-atomic-decomposition.md` v2.3 → v2.4: U-RT-58 AC #4 revised to canonical attribute names. Wrapper implementation at `harness_runtime/lifecycle/retry_breaker_fallback.py` swaps the drifted attribute strings + adds value-derivation for `retry.original_span_id` (outer-wrapper-span `span_id` as the 16-hex original-operation reference) and `engine.replay_disposition` (lookup via `REPLAY_DISPOSITION_MAPPING[binding.engine_class]`). Test assertions at `test_lifecycle_retry_breaker_fallback.py` update to canonical names. `.harness/class_1_tension_c_rt_16_retry_attribute_drift.md` audit-resolved at the same arc.

**Status posture.** Proposed (v1.4) → **Proposed (v1.5)**. Adversarial-review pass at U-RT-58 close (same arc as v1.4).

---

## Change-note (v1.3 → v1.4)

**Scope of revision.** Phase-7 sub-phase 7d Class 1 fork resolution per `.harness/class_1_tension_cp_3_retry_breaker_composer_underspec.md` (filed + Path A ratified 2026-05-20). Operator ratification D1–D6 (composer architectural shape) + Q1=a (nested retry-within-candidate then fallback) + Q2=c (registry key extension with reserved `"llm_dispatch"`): in-Phase-7 closure via new C-RT-16 contract; runtime axis owns the retry/breaker/fallback composition seam between the U-RT-24 registry and the C-RT-15 dispatch composer.

**Single-finding addition.** §14.5 (C-RT-15) preserved verbatim from v1.3. NEW §14.6 contract **C-RT-16 — Retry/breaker/fallback composer (wrapping C-RT-15)** specifies the runtime composition seam that consumes `ctx.retry_breaker` (U-RT-24 registry) + `ctx.fallback_chain` (stage 3b binding) + the inner C-RT-15 `RuntimeLLMDispatcher`, owns the per-step candidate-iteration loop, emits the `retry.*` 6-attribute namespace per C-CP-03 §3.5 + `fallback.exhausted` per C-CP-04 §4.2, surfaces `harness.breaker.*` transitions via the existing `RuntimeRetryBreaker.emit_breaker_transition_event` site, and replaces the bare `RuntimeLLMDispatcher` as `ctx.llm_dispatcher` (preserving the `StepDispatcher` Protocol seam, no driver code change).

**Sections revised (substantive).**
- New **§14.6 C-RT-16** — Retry/breaker/fallback composer contract (between §14.5 and §15 to keep §15–§17 numbering stable; §-pin uses a `.6` decimal continuing the §14.5 pattern).
- **§14** failure-mode taxonomy — new row `RT-FAIL-FALLBACK-EXHAUSTED` (permanent; raised when the fallback chain exhausts after per-candidate retry exhaustion).
- **§15** Spec-to-plan traceability — new row for U-RT-58 (the new plan unit carrying C-RT-16).
- **§17** Coherence pass — re-run for v1.4 deferred per same pattern as v1.2 (covered at U-RT-58 close).

**Sections preserved verbatim from v1.3.** All v1.3 content outside the additions above preserved unchanged. §§1–14 (including the v1.3 §14.5 prose-precision pass), §15 except the new U-RT-58 row, §16, §17, §17.1 unchanged.

**Status posture.** Proposed (v1.3) → **Proposed (v1.4)**. Adversarial-review pass scheduled at U-RT-58 close per Phase 7 sub-phase 7b discipline (in keeping with the U-RT-52 / v1.2-then-v1.3 pattern: implementation begins on the v1.4 surface; adversarial pass folded into the same arc as landing).

**Downstream absorption owed.** `.harness/phase-2-session-3-track-a-atomic-decomposition.md` extended with new U-RT-58 (small body authored alongside this spec amendment; revision log entry added). Per-axis subdirectory `harness-runtime/CLAUDE.md` (if it exists) needs no update — C-RT-16 is runtime-internal. CP spec v1.5 unchanged (the registry-key extension lives in C-RT-16 runtime spec, not as a CP-side amendment — see §14.6 "Registry key extension (Q2=c clause)" sub-section for rationale). `.harness/phase-7d-retirement-ledger-v2.md` §5 CP rows superseded at U-RT-58 landing event (file ratification target H_T-CP-3 RETIRED + H_T-CP-4 RETIRED + H_T-CP-5 PARTIAL → RETIRED; §6.3.2 CXA-5 cascade re-evaluation triggered).

---

## Change-note (v1.2 → v1.3)

**Scope of revision.** Phase-7 sub-phase 7d U-RT-52 close arc absorption per `.harness/fork_u_rt_52_step_payload_shape.md` (filed + ratified 2026-05-20, Class 3 informational). Three §14.5 prose corrections folded in at composer landing:

1. **`step.step_payload` shape pin (`§14.5 Specification content` + new `§14.5 Payload-shape contract`).** v1.2 narrative was silent on how the composer extracts `messages` / `tools` / `params` from `WorkflowStep.step_payload: Mapping[str, Any]`. v1.3 pins the convention: `step.step_payload` IS a `harness_cp.cp_shared_types.ProviderAgnosticPayload` mapping (the `(messages, tools, params)` 3-tuple per ADR-F1 v1.2 + C-CP-01 §1.1). Composer pydantic-validates `step.step_payload` → `ProviderAgnosticPayload`; per-provider helpers translate to SDK kwargs. Mis-shaped payloads surface as a typed `LLMDispatchPayloadShapeError` mapping to `RT-FAIL-PAYLOAD-SHAPE` (new fail class in §14.5 failure-mode taxonomy).
2. **OTel context-manager phrasing (`§14.5 Invariants`).** v1.2 invariants phrased `async with tracer.start_as_current_span(...)`. OpenTelemetry's tracer context manager is synchronous (returns a regular `ContextManager`, not `AsyncContextManager`); inside an async function the composer uses plain `with`. v1.3 rewords the invariant to "exactly one span per call, lifecycle bound by a `with tracer.start_as_current_span(...)` block (synchronous CM, called from within the async `dispatch` body)".
3. **`anthropic.*` cache attribute count (`§14.5 Integration with C-RT-06`).** v1.2 narrative cited "`anthropic.cache_*` attributes per C-AS-14 §14.2" without enumerating. v1.3 makes the full 4-attribute set explicit: `cache_creation_input_tokens` + `cache_read_input_tokens` (response-side, extracted from `response.usage`) + `cache_breakpoint_id` + `cache_ttl_seconds` (request-side, best-effort-extracted from `cache_control` directives on message content blocks; `None` when absent).

**Sections revised (substantive).**
- **§14.5 C-RT-15** — added Payload-shape contract sub-section; reworded async-CM invariant; expanded anthropic.* enumeration; added `RT-FAIL-PAYLOAD-SHAPE` to failure-mode taxonomy.
- **§15** — no row change; U-RT-52 row already present from v1.2.
- **§17** — no re-run at v1.3. The three v1.3 corrections are prose-precision on §14.5 only; no contract count, traceability, or coherence-axis change vs v1.2. The v1.2 §17 coherence pass carries forward unchanged.

**Sections preserved verbatim from v1.2.** All v1.2 content outside §14.5 preserved unchanged. The v1.1 → v1.2 change-note + the v1 → v1.1 change-note + §§1–14 + §15 + §16 + §17 + §17.1 unchanged.

**Status posture.** Proposed (v1.2) → **Proposed (v1.3)**. Adversarial-review pass scheduled at U-RT-52 close (this revision).

**Downstream absorption owed.** None — v1.3 is a prose-precision pass on §14.5, no plan-body or atomic-unit changes. `harness_runtime.lifecycle.llm_dispatch` module docstring cross-references this revision + the Class 3 fork file.

---

## Change-note (v1.1 → v1.2)

**Scope of revision.** Phase-7 sub-phase 7d Class 2 fork resolution per `.harness/fork_llm_dispatch_composer_scope.md` (filed + ratified 2026-05-20). Operator ratification Q1a + Q2a + Q3a + Q4a: in-Phase-7 closure via new C-RT-15 contract; per-step composer (smallest scope — no fallback/retry/breaker wrappers); GenAI semconv 1.41.0 bound at the composer; resolve same-day.

**Single-finding addition.** §14 (C-RT-14) preserved verbatim from v1.1. NEW §14.5 contract C-RT-15 — LLM-dispatch composer — specifies the per-step composer surface that consumes a resolved `StepEffectiveBinding` + `WorkflowStep`, dispatches against the selected `ProviderClient` from C-RT-05, attaches a GenAI-semconv-bound span via C-RT-06's TracerProvider, and returns step output. Satisfies the `StepDispatcher` Protocol declared at `harness_cp.workflow_driver:151`.

**Sections revised (substantive).**
- New **§14.5 C-RT-15** — LLM-dispatch composer contract (between §14 and §15 to keep §15–§17 numbering stable; §-pin uses a `.5` decimal to avoid renumbering downstream cites).
- §15 Spec-to-plan traceability — new row for U-RT-52 (the new plan unit carrying C-RT-15).
- §16 Open questions — no row added; v1.2 closes the LLM-dispatch composer scope question (which §16 did NOT enumerate but operator surfaced at the v2 retirement ledger second pass).
- §17 Coherence pass — re-run for v1.2.

**Sections preserved verbatim from v1.1.** All v1→v1.1 changes (lines below) preserved verbatim; no prior content modified. §§1–14, §15 except the new U-RT-52 row, §16 unchanged.

**Status posture.** Proposed (v1.1) → **Proposed (v1.2)**. Adversarial-review second pass on v1.2 deferred per operator Q4a phasing — implementation begins on the v1.2 surface; adversarial pass scheduled at U-RT-52 landing per Phase 7 sub-phase 7b discipline.

**Downstream absorption owed.** Phase 2 Session 3 Track A plan v2 §atomic-units list extended with new U-RT-52 (small body authored alongside this spec amendment). Per-axis subdirectory `harness-runtime/CLAUDE.md` (if it exists) needs no update — C-RT-15 is runtime-internal. CP plan v2.13 + spec v1.5 unchanged. `.harness/phase-7d-retirement-ledger-v2.md` §9.1 + §9.2 superseded at U-RT-52 landing event (file ratification target H_T-CP-1 + H_T-CP-2 + H_T-CP-5 + H_T-OD-2 + (likely) H_T-AS-8 RETIRED).

---

## Change-note (v1 → v1.1)

**Scope of revision.** Adversarial-review absorption pass per `.harness/Adversarial_Review_phase_2_session_4_runtime_spec.md` (P2-S4-CK gate, 2026-05-19). 7 Class 2 + 3 Class 1 findings absorbed. No Phase-7 §2.7.6 fork engaged; no upstream-phase artifact revision required. Trace-discipline novelty adaptation cleared at the gate.

**Sub-decisions.** F2-01 (fail-class taxonomy) resolved as **Reading 1** per operator decision 2026-05-19: runtime-local fail classes legitimate as distinct from CP validator-fail-taxonomy (different scope: bootstrap-stage failures vs workflow-step failures). New C-RT-14 enumerates the runtime-local set and its relationship to CP's taxonomy.

**Sections revised (substantive).**
- §"ADR scope" — ADR §-citations canonicalized to `§Decision` / `§Consequences` (per actual ADR-F1..F5 + D-ADR section structure verified from the source files).
- §"Cross-axis citation substrate" — axis-spec contract IDs corrected to verified C-NN identifiers (prior v1 cited C-IS-11/14/15 which don't exist; C-CP-04 was misidentified as routing manifest; C-AS-08 was misidentified as tool contract; multiple §-numbers added).
- §"Trace-discipline novelty" — back-flow-shape sketch added (F1-01).
- §3 C-RT-03 — Version-evolution invariant added (F2-04).
- §4 C-RT-04 — Version-evolution invariant added; `providers` field re-typed against new `ProviderClient` Protocol (F2-04, F2-06).
- §5 C-RT-05 — `ProviderClient` Protocol introduced inline; per-provider construction now satisfies the protocol (F2-06).
- §8 C-RT-08 — Idempotency-and-concurrency invariant added: serial calls safe and equivalent to independent runs; concurrent calls from same process surface typed `ConcurrentRunNotSupported` (F2-05).
- §9 C-RT-09 — Version-evolution invariant added (F2-04).
- §12 C-RT-12 — Per-bucket wiring-contract sub-subsections added for the 24 phase-2-runtime edges (F2-07).
- §14 NEW C-RT-14 — Runtime-local fail-class taxonomy + relationship to CP `validator_fail_taxonomy` (F2-01 Reading 1).
- §15 open question #4 — reworded to reflect C-RT-08's pinned decision (F1-02).
- §16 Coherence pass — re-run for v1.1.

**Sections preserved verbatim from v1.** §"Trace-discipline novelty" header + first three paragraphs; §"Axis declaration"; §"Scope and out-of-scope"; §1 C-RT-01; §2 C-RT-02; §6 C-RT-06; §7 C-RT-07; §10 C-RT-10; §11 C-RT-11; §13 C-RT-13; §15 open questions #1, #2, #3, #5, #6, #7.

**Status posture.** Proposed → **Proposed (v1.1)**. P2-S4-CK clearance pending operator confirmation of this revision pass.

**Downstream absorption owed.** Plan v2 §14 traceability table needs one new row for C-RT-14 (fail-class taxonomy) and updated C-RT-12 entry referencing the new per-bucket sub-subsections. Plan revision is a separate small task; not blocking Session 5 entry.

---

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Harness_Runtime_v1.md` |
| Status | **Proposed (v1.1)** — Phase 2 Session 4 runtime-spec authoring + adversarial-review absorption; P2-S4-CK clearance pending |
| Date | 2026-05-19 (v1.1) |
| Phase | Phase 2 (Track A — runtime integration) Session 4 |
| Axis | **Runtime** (new sibling axis under `harness-runtime/`; composition root + bootstrap + ingress for the IS/AS/CP/OD library substrate) |
| Source-set | F-P2-1 / F-P2-2 / F-P2-3 / F-P2-4 / F-P2-5 fork resolutions; `.harness/phase-2-session-1-framing.md` (D-P2-1..D-P2-6); `.harness/phase-2-session-2-track-a-strawman.md`; `.harness/phase-2-session-3-track-a-atomic-decomposition.md` v2 (the 50-unit Track A plan); `.harness/Adversarial_Review_phase_2_session_4_runtime_spec.md` (v1.1 revision driver); ADR-F1 v1.2, F2 v1.2, F3 v1.1, F4 v1.1, F5 v1.1; ADR-D1 v1.2, D2 v1.2, D6 v1.2; ADD v1.3; landed code across `harness-{core,is,as,cp,od,cxa}/` |
| Entry authorization | Operator directive at Session 4 open 2026-05-19; Session 3 close commit `36dbc54` (Track A plan v2 landed + adversarial-reviewed) |
| Exit gate | This spec filed at v1.1; `harness-adversarial-reviewer` second pass on v1.1 returns no Class 3 findings AND no new Class 2 findings (or operator clears them); Session 5 entry directive authored at session close |
| Revision | v1 (2026-05-19 initial) → v1.1 (2026-05-19 adversarial-review absorption) |

---

## Trace-discipline novelty (read first)

This is the workspace's **first net-new axis spec**. The four existing axis specs (IS / AS / CP / OD) inherit a fixed trace structure: each contract names a PRD requirement (R-{AXIS}-NN), an ADR commitment, and a persona linkage. The runtime axis cannot honor that structure unchanged:

- **PRD v1.1 has no R-RT-* requirements.** The PRD predates the runtime axis. The runtime *enables* every R-IS/AS/CP/OD-* requirement (the library is unrunnable without it); it does not introduce net-new observable behavior of its own.
- **Persona is explicitly uncommitted** per workspace `CLAUDE.md` §1 framing. The runtime spec touches no persona-dependent decision (operator-facing surfaces are deferred to Track B per F-P2-2).
- **The source-of-truth for runtime commitments is the F-P2-N fork resolutions.** Five operator-ratified architectural decisions (composition-root package placement, ingress shape, three lifecycle ownerships) anchor this spec.

**Adapted trace convention for this spec:**

| Standard field | Runtime-axis substitution |
|---|---|
| `PRD requirement(s) satisfied` | `PRD enablement` — names the R-{AXIS}-NN requirements the contract enables (composition-level inheritance, not direct satisfaction). |
| `ADR commitment(s) honored` | Unchanged. Every contract cites ≥1 ADR by ID + version + section. |
| `Persona linkage` | Replaced by `Fork-resolution provenance` — names which F-P2-N fork (and which session ratified it) the contract derives from. For contracts not derived from a fork, this field reads `n/a (general runtime discipline)`. |

This adaptation is itself a candidate Class 1 review surface. **Adversarial review at P2-S4-CK 2026-05-19 judged the adaptation sufficient at this gate.** Re-evaluable at any future aggregate review.

**Back-flow shape if re-evaluation flips the verdict.** A PRD v1.2 amendment introducing a new §N Runtime requirements section would carry the R-RT-* requirements that today's runtime contracts implicitly enable. Candidate R-RT-* shape: one requirement per F-P2-N fork's observable consequence (e.g., R-RT-01 "the runtime starts under H_E with bounded bootstrap time"; R-RT-02 "the runtime exposes a single async Python ingress accepting a workflow object"; etc.). Exact shape is operator-decided at back-flow time, not pre-pinned here.

---

## Axis declaration

The **Runtime axis** owns the composition root, bootstrap sequencing, in-process lifecycle ownership for provider clients + tracer provider + collector daemon, the Python API ingress surface (`harness_runtime.run(workflow)`), shutdown sequencing, and the runtime instantiation of the cross-axis composition substrate (terminal exporter manifest import + 24 phase-2-runtime CXA edges).

The Runtime axis is *not* a fifth axis at the design layer — it does not introduce new schemas, contracts, or invariants over IS/AS/CP/OD library content. It is the axis at the *execution* layer that turns the four library axes into a startable process under H_E (Claude Code CLI as Phase-7 execution surface) and, eventually, a self-hosted H_T.

Package: `harness-runtime/` (workspace member; new under Phase 2 Track A).

---

## ADR scope

ADR citations follow the canonical convention verified from each ADR file: F-ADRs use `§Status / §Context / §Decision / §Rationale / §Consequences / §Alternatives considered / §References`; D-ADRs add `§1.N` subsection structure under `§Decision`.

| ADR | Version | Role in this spec |
|---|---|---|
| ADR-F1 | v1.2 | `§Decision` — Multi-LLM commitment. The runtime constructs three async provider clients (`anthropic.AsyncAnthropic`, `openai.AsyncOpenAI`, `ollama.AsyncClient`) under capability-aware abstraction. NOT LiteLLM. |
| ADR-F2 | v1.2 | `§Decision` — State ledger primitive. The runtime reattaches the state-ledger chain at bootstrap stage 1 and wraps the IS writer for audit-ledger composition at stage 4. |
| ADR-F3 | v1.1 | `§Decision` — Index primitive. The runtime reattaches the content-addressed index + semantic cache at bootstrap stage 1. |
| ADR-F4 | v1.1 | `§Decision` + `§Consequences (b)(iv)` — Workflow lifecycle primitive. The runtime accepts a `WorkflowObject` at ingress and hands it to CP's lifecycle loop. Drain at shutdown polls a runtime-owned flag at CP lifecycle boundaries. `§Consequences (b)(iv)` is also the trace target for OD spec C-OD-20 collector placement, transitively. |
| ADR-F5 | v1.1 | `§Decision` — Observability substrate primitive. The runtime constructs the OTel `TracerProvider`, registers it globally via `set_tracer_provider(...)`, and starts the in-process OTLP collector daemon. |
| ADR-D1 | v1.2 | `§Decision §1.1` (engine-class taxonomy) — informs `EngineClass` enum the runtime binds to provider clients at stage 3a/3b. |
| ADR-D2 | v1.2 | `§Decision §1.1` (deployment-surface × blast-radius matrix) + `§1.3` (per-MCP-transport sandbox-tier floor) — sandbox-tier dispatch binding at stage 2 honors these. |
| ADR-D6 | v1.2 | `§Decision §1.2` (unified span schema ingestion contract) + `§1.7` (local-first OTLP collector commitment) — TracerProvider resource attributes carry the 12-namespace tags; collector daemon supervision derives from §1.7. |
| ADD v1.3 | — | ADR consolidation. The runtime spec inherits the coherent architectural overview at the composition layer. |

Other ADRs (D3 validation, D4 cost, D5 topology) are honored *transitively* — the runtime instantiates CP/OD primitives that themselves honor those ADRs; the runtime spec does not restate them.

---

## Cross-axis citation substrate

The runtime spec consumes the following contracts from the four axis specs at composition time. Contract IDs verified against actual axis-spec contract enumerations (IS v1 has C-IS-01..10; CP v1.3 has C-CP-01..24; OD v1.4 has C-OD-01..23; AS v1.3 has C-AS-01..16).

| Source spec | Contracts consumed | Composition shape |
|---|---|---|
| `Spec_Information_Substrate_v1.md` | C-IS-01 §1 (canonical filesystem path contract); C-IS-05 §5 (state-ledger entry shape signature, 6-field); C-IS-06 §6 (hash-chain integrity construction discipline); C-IS-07 §7 (state-ledger read/write contract pair); C-IS-08 §8 (workload-class-opt-in shadow-Git checkpoint contract); C-IS-09 §9 (workload-class-opt-in worktree-isolation contract); C-IS-10 §10 (substrate seam exports surface) | Runtime instantiates `PathResolver(binding)` per C-IS-01, `WorktreeIsolationManager(...)` per C-IS-09, shadow-Git supervisor per C-IS-08, ledger writer wrapper per C-IS-05+06+07 at stage 1; imports C-IS-10 exports at stage 6 |
| `Spec_Action_Surface_v1.md` | C-AS-01 §1 (4-tier sandbox-isolation enumeration); C-AS-02 §2 (per-tool sandbox-tier `max()` composition); C-AS-05 §5 (`fetch_secret(name, scope, tier) -> SecretRef` signature); C-AS-08 §8 (secret-fetch structure-not-content audit composition); C-AS-10 §10 (per-MCP-transport sandbox-tier floor); C-AS-15 §15 (sandbox-bounded span schema `sandbox.*`); C-AS-16 §16 (AS substrate seam exports surface) | Runtime loads skills + registers tool contracts at stage 2 (note: tool-contract *registration site* is not formally a C-AS-NN contract — see risk surface #4); starts MCP host + clients honoring C-AS-10; binds sandbox-tier dispatch per C-AS-01+02; secret resolution via C-AS-05 with C-AS-08 audit; imports C-AS-16 exports at stage 6 |
| `Spec_Control_Plane_v1_3.md` | C-CP-01 §1 (capability-aware multi-LLM provider abstraction); C-CP-02 §2 (layered cheapest-deterministic-first routing strategy); C-CP-04 §4 (cross-family fallback chain composition); C-CP-05 §5 (F3 capability-floor lifecycle event surface); C-CP-06 §6 (manifest-declaration invocation discipline with per-step opt-in override); C-CP-07 §7 (engine class committed per deployment surface); C-CP-09 §9 (`engine.*` span attribute namespace); C-CP-10 (topology pattern — first contract in the multi-agent topology cluster C-CP-10..C-CP-22); C-CP-24 (cross-axis composition exports) | Runtime constructs provider clients (stage 3a) honoring C-CP-01; builds routing manifest + binds reliability primitives at stage 3b honoring C-CP-02+04+05; binds override evaluator + topology dispatcher + lifecycle emission at stage 5 honoring C-CP-06+09+10; imports C-CP-24 exports at stage 6 |
| `Spec_Operational_Discipline_v1_4.md` | C-OD-01 §1 (9-cell deployment-surface × persona-tier matrix; §1.2 7-value `CollectorPlacement` enum after v1.4 FF-2 resolution); C-OD-20 §20.1 (per-cell OTLP collector placement + F4 process-tier reachability); OD spec contracts for cost-attribution chain (within C-OD-01..23 range; specific §-pin verified at U-RT-31 landing); OD audit-ledger schema (within C-OD-01..23 range; specific §-pin verified at U-RT-32 landing) | Runtime constructs TracerProvider per stage 4; collector daemon supervisor honors C-OD-01 §1.2 enum + C-OD-20 §20.1 placement matrix; cost-attribution + audit-ledger writers wire to landed OD primitives (exact contract §-pins resolved at unit landing — see risk surface #4) |
| `Cross_Axis_Composition_Document_v2_3.md` | §3 Pattern P1 22 genuine typed seams; §2.3 24 phase-2-runtime edges; the 5 terminal aggregate exporter manifests | Runtime imports terminal exporter manifests for side-effect at stage 6 (see C-RT-12 §12.1), wires the 24 phase-2-runtime edges per per-bucket sub-subsections (C-RT-12 §12.2–§12.6), verifies Pattern P1 identity-equality at L11 |

**Note on partial §-precision.** Two cross-axis citations resolve to a *contract range* rather than a specific §-pin: cost-attribution and audit-ledger schema in OD. These were originally cited as C-OD-12 and a single C-OD ID in v1; verification against OD v1.4 + its predecessor v1.2/v1.3 (which carry the unrevised §2..§19 + §21..§23 content) is deferred to unit landing at U-RT-31 / U-RT-32, since the OD v1.4 file is amendment-only and full enumeration requires reading the predecessor. This is acceptable per the canonical convention's "verify at consumption time" pattern for amendment-only spec files. If the resolved §-pin reveals a contract gap (cost-attribution or audit-ledger writer not in fact specified), surface as Class 1 fork at U-RT-31/U-RT-32 landing.

---

## Scope and out-of-scope

| In-scope (Runtime axis owns) | Out-of-scope (other axes / Track B / future) |
|---|---|
| 9-stage canonical `BootstrapStage` enum + ordering invariants | Algorithm for selecting which `TopologyPattern` a workflow uses (Track B) |
| `RuntimeConfig` input schema | Operator-facing config file format (Track B); CLI argument parsing (Track B) |
| `HarnessContext` post-bootstrap shape (frozen) | Operator-facing context exposure (Track B) |
| `ProviderClient` Protocol (new at v1.1) | Per-provider SDK internals; provider-agnostic message format (CP spec; not runtime) |
| Async provider SDK lifecycle (F-P2-4) | The capability-aware routing algorithm itself (CP spec) |
| TracerProvider construction + global registration (F-P2-3) | OTel attribute schemas + 12-namespace map (OD spec) |
| In-process OTLP collector daemon supervision (F-P2-5) | TUI trace browser (Track B); collector ring-buffer/sqlite internals (OD spec) |
| `harness_runtime.run(workflow)` Python API (F-P2-2) | CLI `run` subcommand (Track B); markdown workflow authoring (Track B); MCP-server-triggered workflows (Track B); operator-typed prompt → workflow generation (Track B) |
| `RunResult` shape | Operator-facing result formatting (Track B) |
| Shutdown order (drain → flush → close) | Distributed shutdown coordination (out of scope for Track A) |
| Drain semantics (runtime-owned flag-polling) | CP-native drain primitive (does not exist; if CP later adds one, U-RT-44 refactors to delegate) |
| CXA wiring obligations (terminal exporter manifest import + 24 phase-2-runtime edges) | The 22 genuine typed CXA seams themselves (axis spec content; runtime only verifies identity-equality) |
| Admin stub semantics (`harness-inspect`, `harness-shutdown`) | Richer admin IPC (Track B); operator-facing inspection UI (Track B) |
| Runtime-local fail-class taxonomy (new at v1.1 — see C-RT-14) | CP `validator_fail_taxonomy` (orthogonal — CP owns workflow-step-level fail classes) |
| 5 F-P2-N fork resolutions as recorded canonical decisions | Track B definitional pass (separate authoring stream) |

---

## §1 C-RT-01 — Canonical `BootstrapStage` enum (9 values, fixed order)

**Contract surface.** Enum.

**PRD enablement.** Enables every R-IS/AS/CP/OD-* requirement at composition (no runtime, no requirement satisfaction). Specifically gates R-CP-* multi-LLM-routing requirements and R-OD-* observability requirements that depend on bootstrap ordering.

**ADR commitment(s) honored.** ADR-F1 v1.2 §Decision (CP_CLIENTS at stage 3a precedes CP_ROUTING at stage 3b); ADR-F5 v1.1 §Decision (OD stage 4 must come after IS stage 1 since OD audit writer wraps IS ledger writer).

**Fork-resolution provenance.** F-P2-3 + F-P2-4 + F-P2-5 (the three lifecycle-ownership forks fix the stage-4 OD bundle and the stage-3a CP_CLIENTS responsibility).

**Specification content.**

The runtime defines exactly nine bootstrap stages, in this fixed order:

| Index | Enum member | Owner of work |
|---|---|---|
| 0 | `PREAMBLE` | Config resolution (RuntimeConfig materialization, sub-config derivation) |
| 1 | `IS` | Path-class registry, worktree + shadow-Git, state-ledger reattach, content-addressed index + semantic cache reattach |
| 2 | `AS` | Skills load, tool-contract registration, MCP host startup + client connect, sandbox-tier dispatch binding |
| 3a | `CP_CLIENTS` | Async provider SDK client construction (anthropic / openai / ollama), capability-aware abstraction binding |
| 3b | `CP_ROUTING` | Routing manifest construction, engine selection, retry/breaker/idempotency runtime binding, HITL placement registry, sub-agent handoff registry |
| 4 | `OD` | TracerProvider construction + global registration, BatchSpanProcessor + OTLP exporter, in-process collector daemon, ring-buffer + sqlite rotation, cost attribution chain, audit-ledger writer |
| 5 | `LOOP_INIT` | Per-step override evaluator runtime binding, topology dispatcher runtime binding, lifecycle event emission hook |
| 6 | `CXA_WIRING` | Terminal aggregate exporter manifest import (side-effect), 24 phase-2-runtime CXA edges wired |
| 7 | `INGRESS_ACCEPT` | Accept `WorkflowObject` via `run()`; hand to CP lifecycle |

`BootstrapStage` is a Python `enum.Enum` with `len(BootstrapStage) == 9` and `list(BootstrapStage) == [PREAMBLE, IS, AS, CP_CLIENTS, CP_ROUTING, OD, LOOP_INIT, CXA_WIRING, INGRESS_ACCEPT]`. The two stage-3 members (`CP_CLIENTS`, `CP_ROUTING`) are sequenced adjacent and both correspond to file-naming convention `stage_3a_*.py` / `stage_3b_*.py`. There is no `stage_8`; INGRESS_ACCEPT is the terminal bootstrap stage.

**Invariants.**

- No stage runs before its strict predecessor completes successfully. Stage failures roll back already-completed stages in reverse order (see C-RT-10).
- Each stage emits exactly one `workflow_event_class` lifecycle event on entry and exit (per ADR-F5 §Decision).
- The enum is immutable across runtime versions within v1; adding a stage is a major-version event (v2.0).

**Deferred to implementation discretion.** Specific span name and event attribute set per stage (deferred to OD spec + landed `harness_cp.lifecycle_event_span_map`); specific file layout under `bootstrap/` (canonical naming above is binding, internal organization is implementation-discretion).

---

## §2 C-RT-02 — Bootstrap orchestrator + stage-ordering invariants

**Contract surface.** Surface contract.

**PRD enablement.** Enables all axes — bootstrap is the precondition for any runtime behavior.

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (ledger reattach is stage 1; audit writer at stage 4 wraps it); ADR-F5 v1.1 §Decision (tracer provider at stage 4 must precede any axis primitive that calls `get_tracer_provider()`).

**Fork-resolution provenance.** F-P2-3 + F-P2-4 + F-P2-5.

**Specification content.**

The orchestrator (`harness_runtime.bootstrap.__init__`) executes the 9 stages from C-RT-01 in order. Each stage is implemented as a single module (`stage_0_preamble.py`, ..., `stage_7_ingress.py`, with `stage_3a_cp_clients.py` + `stage_3b_cp_routing.py` for the split). Each stage module exposes a single entry point `async def execute(ctx: HarnessContext) -> StageResult` that mutates `ctx` in place during bootstrap (the immutability invariant of `HarnessContext` per C-RT-04 holds only *post-bootstrap*).

**Forward invariants (must hold at successful completion of each stage):**

| After stage | Post-condition |
|---|---|
| 0 PREAMBLE | `ctx.config: RuntimeConfig` populated; sub-configs (path bindings, secrets, OTel, collector) materialized |
| 1 IS | `ctx.path_resolver`, `ctx.worktree_manager`, `ctx.shadow_git`, `ctx.ledger_writer`, `ctx.index`, `ctx.cache` all non-None; ledger chain reattached and verified |
| 2 AS | `ctx.skills`, `ctx.tool_contracts`, `ctx.mcp_host`, `ctx.mcp_clients`, `ctx.sandbox_dispatch` all non-None; MCP clients in READY state |
| 3a CP_CLIENTS | `ctx.providers: dict[str, ProviderClient]` has entries for `anthropic`, `openai`, `ollama`; each client passes an async ping (see C-RT-05 for `ProviderClient` Protocol) |
| 3b CP_ROUTING | `ctx.routing_manifest`, `ctx.engine_selector`, `ctx.fallback_chain`, `ctx.retry_breaker`, `ctx.hitl_registry`, `ctx.handoff_registry` all non-None |
| 4 OD | `opentelemetry.trace.get_tracer_provider()` returns the runtime-registered provider; `ctx.collector_daemon` is running (health-check ok); `ctx.cost_chain`, `ctx.audit_writer` non-None |
| 5 LOOP_INIT | `ctx.override_evaluator`, `ctx.topology_dispatcher`, `ctx.lifecycle_emitter` all non-None |
| 6 CXA_WIRING | All 5 terminal exporter manifests imported; all 24 phase-2-runtime edges wired (test fixture exercises each) |
| 7 INGRESS_ACCEPT | `ctx` frozen; `harness_runtime.run` accepts a `WorkflowObject` and dispatches |

**Failure-mode taxonomy.** Per the runtime-local fail-class set at C-RT-14. The orchestrator surfaces stage failures via `RT-FAIL-BOOTSTRAP` (permanent; cause-attribution identifies the specific stage) or `RT-FAIL-PARTIAL-ROLLBACK-REQUIRED` (stage N+1 fails after stage N completed; rollback executes reverse-order shutdown for stages 0..N). Stage-internal transient failures use `RT-FAIL-TRANSIENT` (bounded retry; persistent escalates to `RT-FAIL-BOOTSTRAP`).

**Deferred to implementation discretion.** Retry intervals at stage-internal bounded retry (suggest 200ms × 2^attempt); structured-error type hierarchy (suggest one exception class per stage with `BootstrapStage` field); concurrent stage execution within an axis (e.g., parallel client construction at stage 3a) is implementation-discretion as long as the post-conditions hold.

---

## §3 C-RT-03 — `RuntimeConfig` schema

**Contract surface.** Schema.

**PRD enablement.** Enables R-CP-* (multi-LLM routing requires per-provider config); R-OD-* (observability requires OTel endpoint + sampler config); R-IS-* (state ledger requires path bindings).

**ADR commitment(s) honored.** ADR-F1 v1.2 §Decision (provider keys allowlist); ADR-D6 v1.2 §Decision §1.2 (unified span schema — 12-namespace resource attrs).

**Fork-resolution provenance.** F-P2-2 (config-vs-CLI ingress split).

**Specification content.**

`RuntimeConfig` is a Pydantic v2 `BaseModel` (frozen). The schema is the contract; field order and type discipline are normative.

| Field | Type | Required | Semantic |
|---|---|---|---|
| `deployment_surface` | `DeploymentSurface` (harness-core enum) | yes | Local / hybrid / cloud — drives OTel resource attrs + collector placement |
| `repository_root` | `pathlib.Path` | yes | Absolute path; must exist; basis for `.harness/` and PATH_CLASS_REGISTRY resolution |
| `path_bindings` | `PathBindingConfig` (sub-model) | yes | Inputs to `PathResolver(binding)`; validated against `WorkloadManifestOptInSchema` |
| `provider_secrets` | `ProviderSecretsConfig` (sub-model) | yes | Keyring allowlist *keys* only; no secret values in config |
| `otel` | `OTelConfig` (sub-model) | yes | OTLP endpoint, sampler mode, additional resource attrs |
| `collector` | `CollectorConfig` (sub-model) | yes | Ring buffer size, sqlite rotation thresholds, placement-matrix selection |
| `mcp_clients` | `list[MCPClientConfig]` | no (default `[]`) | MCP client connection configs |
| `default_topology` | `TopologyPattern` (CP enum) | yes | The TopologyPattern the runtime dispatches when no per-workflow override is set |
| `tenant_id` | `str | None` | no | Multi-tenant separation key per OD audit-ledger; None = single-tenant mode |

**Invariants.**

- `model_config = ConfigDict(frozen=True, extra='forbid')` — frozen post-construction; unknown keys rejected.
- `repository_root.is_absolute()` and `repository_root.exists()`.
- `provider_secrets` contains only allowlist keys; runtime resolves values via `keyring`. No secret value ever appears in `RuntimeConfig` instances or in span attributes.
- Precedence at construction: kwargs to `run()` > environment variables > defaults. (No file-loading; that is Track B.)
- **Version evolution (added at v1.1).** Adding an *optional* field is a minor version bump (v1.N → v1.(N+1)); existing callers continue to work. Adding a *required* field is a major bump (v1 → v2); existing callers without the field surface typed `IncompatibleConfigVersion` at materialization. Removing a field is always a major bump; the field stays through one minor version marked `Deprecated` (Pydantic field metadata) with a runtime warning. Type-narrowing of an existing field (e.g., from `str` to a `Literal[...]`) is a major bump. Type-widening is a minor bump.

**Failure-mode taxonomy.**

| Fail class | Trigger |
|---|---|
| `RT-FAIL-CONFIG` (permanent) | Required field missing; unknown field present; `repository_root` not absolute or not existing; type mismatch |
| `RT-FAIL-CONFIG-VERSION` (permanent) | Incompatible config version per Version evolution clause above |
| `RT-FAIL-SECRET-MISSING` (permanent; deferred to stage 0 secret resolution) | `provider_secrets` references an allowlist key not present in keyring — raises typed `SecretFailClass` per AS C-AS-05 §5 |

**Deferred to implementation discretion.** Exact field names for `OTelConfig` and `CollectorConfig` (inherited from OD spec C-OD-01 §1.2 + C-OD-20 §20.1 conventions); env-var naming (suggest `HARNESS_*` prefix); kwargs-vs-env precedence resolver implementation; specific `Deprecated` warning text.

---

## §4 C-RT-04 — `HarnessContext` schema (frozen post-bootstrap)

**Contract surface.** Schema.

**PRD enablement.** Enables all axes — `HarnessContext` is the post-bootstrap handle through which `run()` reaches every wired component.

**ADR commitment(s) honored.** ADR-F1 v1.2 §Decision; ADR-F2 v1.2 §Decision; ADR-F3 v1.1 §Decision; ADR-F4 v1.1 §Decision; ADR-F5 v1.1 §Decision (the context holds primitives for each ADR-F).

**Fork-resolution provenance.** F-P2-1 (`harness-runtime/` is the package that owns this type).

**Specification content.**

`HarnessContext` is a Pydantic v2 `BaseModel`. Bootstrap mutates it stage-by-stage; at stage 7 INGRESS_ACCEPT it is frozen and handed to `run()`.

| Field | Type | Populated at stage | Semantic |
|---|---|---|---|
| `config` | `RuntimeConfig` (frozen) | 0 | Resolved configuration |
| `path_resolver` | `harness_is.PathResolver` | 1 | Path-class registry handle |
| `worktree_manager` | `harness_is.WorktreeIsolationManager` | 1 | Worktree isolation |
| `shadow_git` | `ShadowGitSupervisor` (runtime-defined) | 1 | Shadow-Git checkpoint/rollback supervisor |
| `ledger_writer` | `LedgerWriter` (runtime-defined, wraps IS) | 1 | State-ledger writer wrapper |
| `index` | `ContentAddressedIndex` (IS landed) | 1 | Index handle |
| `cache` | `SemanticCache` (IS landed) | 1 | Semantic cache handle |
| `skills` | `dict[SkillID, Skill]` | 2 | Loaded skills indexed by ID |
| `tool_contracts` | `dict[ToolName, ToolContract]` | 2 | Registered tool contracts |
| `mcp_host` | `MCPHost` (FastMCP) | 2 | MCP host handle |
| `mcp_clients` | `dict[ClientName, MCPClient]` | 2 | Connected MCP clients |
| `sandbox_dispatch` | `SandboxDispatchTable` | 2 | Sandbox-tier dispatch |
| `providers` | `dict[str, ProviderClient]` | 3a | `ProviderClient` is the runtime-defined Protocol at C-RT-05. Concrete values: `{'anthropic': AsyncAnthropic, 'openai': AsyncOpenAI, 'ollama': AsyncClient}` (each structurally implements `ProviderClient`) |
| `routing_manifest` | `RoutingManifest` (CP R-2 schema) | 3b | Runtime routing manifest |
| `engine_selector` | `EngineSelector` (CP) | 3b | Engine-class binding |
| `fallback_chain` | `FallbackChain` (CP) | 3b | Cross-family fallback chain |
| `retry_breaker` | `RetryBreakerRegistry` (CP) | 3b | Retry/breaker/idempotency primitives bound |
| `hitl_registry` | `HITLPlacementRegistry` (CP) | 3b | HITL placement registry |
| `handoff_registry` | `HandoffRegistry` (CP) | 3b | Sub-agent handoff + brief registry |
| `tracer_provider` | `opentelemetry.sdk.trace.TracerProvider` | 4 | Constructed + globally registered |
| `collector_daemon` | `CollectorDaemonHandle` (runtime-defined) | 4 | In-process OTLP collector supervisor handle |
| `cost_chain` | `CostAttributionChain` (OD) | 4 | 5-step cost-attribution chain |
| `audit_writer` | `AuditLedgerWriter` (runtime-defined, wraps IS+OD) | 4 | Multi-tenant audit-ledger writer |
| `override_evaluator` | `PerStepOverrideEvaluator` (CP) | 5 | Override evaluator runtime |
| `topology_dispatcher` | `TopologyDispatcher` (CP, runtime-bound) | 5 | TopologyPattern dispatcher |
| `lifecycle_emitter` | `LifecycleEventEmitter` (runtime-defined) | 5 | Emits `workflow_event_class` events |
| `drained_flag` | `asyncio.Event` | 0 (initialized) | Set by signal handler; polled by CP loop for drain |

**Invariants.**

- `model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)`. Mutation during bootstrap is via a separate `_MutableHarnessContext` builder; at stage 7 the builder is materialized into the frozen final form.
- Every field is non-`None` at stage 7 EXCEPT `mcp_clients` (empty dict permitted if no clients configured) and `tenant_id`-derived audit-writer scoping.
- `tracer_provider` field is informational only; consumers should call `opentelemetry.trace.get_tracer_provider()` per ADR-F5 §Decision.
- **Version evolution (added at v1.1).** `HarnessContext` is an internal type (consumers reach into specific fields, not the whole context); field-additions are minor; field-removals or type-changes are major (consumers break). The type is not part of any operator-facing surface in Track A.

**Failure-mode taxonomy.** Construction failure of any field surfaces as the relevant stage's failure (per C-RT-02 and C-RT-14).

**Deferred to implementation discretion.** Internal `_MutableHarnessContext` builder shape; whether `providers` keys are string literals or an enum (suggest enum from `harness_core` if landed); whether `tenant_id` defaults wrap audit-writer scoping or live separately on the writer.

---

## §5 C-RT-05 — Provider SDK lifecycle (F-P2-4 absorption) + `ProviderClient` Protocol

**Contract surface.** Surface contract + lifecycle obligations + Protocol definition.

**PRD enablement.** Enables R-CP-* multi-LLM routing requirements — the routing core cannot route without constructed clients.

**ADR commitment(s) honored.** ADR-F1 v1.2 §Decision (three providers under capability-aware abstraction; NOT LiteLLM); ADR-D2 v1.2 §Decision §1.1 (sandbox tier — provider clients respect sandbox-tier reachability).

**Fork-resolution provenance.** F-P2-4 ratified 2026-05-19.

**Specification content.**

The runtime owns construction, lifetime, and close of three async provider clients. Construction occurs at stage 3a CP_CLIENTS; close occurs at the final shutdown step in reverse order (see C-RT-10).

**`ProviderClient` Protocol (new at v1.1):**

The three async clients have no shared base class across the three SDKs. The runtime defines a structural `Protocol` (PEP 544) that each concrete client implements via duck-typing:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class ProviderClient(Protocol):
    """Structural protocol every async provider client satisfies.

    Methods are intentionally minimal — the CP capability-aware abstraction
    layer is what dispatches to provider-specific methods. ProviderClient
    only carries lifecycle obligations the runtime owns.
    """
    async def aclose(self) -> None:
        """Close the underlying SDK client + connections. Idempotent."""
        ...
```

Implementation note: `anthropic.AsyncAnthropic` exposes `.close()` (awaitable in recent versions); `openai.AsyncOpenAI` exposes `.close()` (awaitable); `ollama.AsyncClient` may not expose a public close. Runtime wraps each in a thin adapter (per-provider module under `harness_runtime/lifecycle/providers.py`) so all three satisfy `ProviderClient.aclose()` uniformly. Adapters are runtime-defined; the Protocol is the canonical contract.

**Construction table:**

| Provider | Underlying SDK class | Adapter satisfies | Construction | aclose() implementation |
|---|---|---|---|---|
| Anthropic | `anthropic.AsyncAnthropic` | `ProviderClient` | `AsyncAnthropic(api_key=keyring_resolve('anthropic_key'), ...)` | `await client.close()` |
| OpenAI | `openai.AsyncOpenAI` | `ProviderClient` | `AsyncOpenAI(api_key=keyring_resolve('openai_key'), ...)` | `await client.close()` |
| Ollama | `ollama.AsyncClient` | `ProviderClient` | `AsyncClient(host=config.ollama_host or default)` | `await client.close()` if exposed; else best-effort connection cleanup (adapter handles) |

**Invariants.**

- All clients are **async variants** (matches `async def run(...)` posture per C-RT-08). Sync variants (`anthropic.Anthropic`, `openai.OpenAI`, `ollama.Client`) MUST NOT be constructed by the runtime.
- Each concrete client passes `isinstance(client, ProviderClient)` (per `@runtime_checkable`) when accessed via its adapter.
- Secret resolution at construction time goes through AS `secret_fetch` per C-AS-05 §5; allowlist enforced; secret never logged or emitted as span attribute.
- Construction errors (auth failure, network failure on initial ping) surface as stage 3a failure with provider identity attached to the typed error.
- Capability-aware abstraction binding at C-RT-04's `providers` field hands the 3 adapters to CP `provider_capabilities` per C-CP-01 §1.

**Failure-mode taxonomy.** Per C-RT-14:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-SECRET-MISSING` (permanent) | Secret allowlist key missing from keyring | Stage 3a fails; no rollback (no prior runtime state to undo) |
| `RT-FAIL-TRANSIENT` (transient) | Initial async ping fails with network error | Bounded retry (max 3 per stage policy); persistent → escalation to `RT-FAIL-PROVIDER-AUTH` or `RT-FAIL-PROVIDER-UNREACHABLE` |
| `RT-FAIL-PROVIDER-AUTH` (permanent) | Auth failure (401 / 403 from provider) | No retry; surface typed error naming the provider |
| `RT-FAIL-PROVIDER-DEGRADED` (degraded) | Ollama local-tier unreachable AND `RuntimeConfig.ollama_optional == True` | Surface typed warning; stage continues with 2-provider context; routing core sees Ollama as unavailable per C-CP-01 |

**Deferred to implementation discretion.** Async ping mechanism (suggest a low-cost `count_tokens` or model-list call per provider); whether `ollama_optional` is a top-level `RuntimeConfig` field or under `ProviderSecretsConfig`; specific keyring service-name convention (suggest `harness-runtime`); adapter module organization under `harness_runtime/lifecycle/providers.py`.

---

## §6 C-RT-06 — TracerProvider lifecycle (F-P2-3 absorption)

**Contract surface.** Surface contract + lifecycle obligations.

**PRD enablement.** Enables R-OD-* observability requirements — no observability before TracerProvider registered.

**ADR commitment(s) honored.** ADR-F5 v1.1 §Decision (tracer-provider is foundational); ADR-D6 v1.2 §Decision §1.2 (unified span schema — 12-namespace resource attrs).

**Fork-resolution provenance.** F-P2-3 ratified 2026-05-19.

**Specification content.**

The runtime constructs and globally registers the OTel `TracerProvider` at stage 4 OD, before any axis primitive's first span emission.

**Construction sequence (at stage 4):**

1. Build `Resource` with attributes from `RuntimeConfig.deployment_surface` plus all 12 OTel namespace tags per ADR-D6 §Decision §1.2 + OD spec C-OD-01 §1 conventions.
2. Construct `TracerProvider(resource=resource, sampler=sampler_from_config)`.
3. Attach `BatchSpanProcessor(OTLPSpanExporter(endpoint=config.otel.endpoint, ...))` per OD spec C-OD-20 §20.1 collector-placement matrix.
4. Call `opentelemetry.trace.set_tracer_provider(provider)` — the global registration that landed OD `operator_burden_eval_primitives.py`'s `get_tracer_provider()` call depends on.

**Invariants.**

- `set_tracer_provider(...)` is called exactly once per process; double-registration is a runtime error (also see C-RT-08 idempotency invariant).
- The call precedes execution of every subsequent stage (5, 6, 7) AND any code path that emits a span.
- Resource attributes are immutable after registration; mutations require process restart.
- Provider stored on `HarnessContext.tracer_provider` for diagnostic introspection only; consumers acquire tracers via `opentelemetry.trace.get_tracer(...)` (which uses the global provider).
- On shutdown (per C-RT-10): `provider.force_flush(timeout_millis=...)` then `provider.shutdown()` — both awaitable.

**Failure-mode taxonomy.** Per C-RT-14:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-CONFIG` (permanent) | OTLP endpoint URL malformed (caught at C-RT-03 validation) | Surfaces at stage 0, not stage 4 |
| `RT-FAIL-TRANSIENT` (transient — collector reachability) | OTLP exporter cannot reach endpoint on first attempt | Construction does not require reachability (BSP buffers); reachability surfaces as collector-daemon health (C-RT-07) and downstream span-drop metrics |
| `RT-FAIL-CONCURRENT-REGISTRATION` (permanent) | `set_tracer_provider` called twice in same process | Typed error; possible indicator of orchestrator bug or `run()` concurrent-invocation violation (see C-RT-08) |

**Deferred to implementation discretion.** Sampler choice (suggest `ParentBased(TraceIdRatioBased)` mapped from `RuntimeConfig.otel.sampler_mode`); `BatchSpanProcessor` tuning constants (suggest OD spec defaults); exporter protocol (suggest gRPC; HTTP/protobuf accepted via config).

---

## §7 C-RT-07 — In-process OTLP collector daemon lifecycle (F-P2-5 absorption)

**Contract surface.** Surface contract + supervision contract.

**PRD enablement.** Enables R-OD-* observability requirements that depend on a running collector (TUI trace browser per OD — TUI is Track B; collector is Track A).

**ADR commitment(s) honored.** ADR-F5 v1.1 §Decision; ADR-D6 v1.2 §Decision §1.7 (local-first OTLP collector commitment).

**Fork-resolution provenance.** F-P2-5 ratified 2026-05-19.

**Specification content.**

OD spec C-OD-20 §20.1 defines the collector placement matrix; landed `harness_od.local_first_otlp_collector` exposes the collector as a *library* (ring-buffer + sqlite rotation + no-network-egress policy). The runtime owns the *daemon* that runs the library as an in-process supervised component.

**Supervisor obligations (the runtime piece):**

- Start the daemon at stage 4, after TracerProvider registration so that spans flow through BSP → OTLP exporter → daemon → ring-buffer + sqlite.
- Expose a health check (typed: `healthy | degraded | failed`). Daemon reports health every N seconds (configurable, default 10s).
- On daemon crash, restart bounded: max 3 restarts within 60 seconds. After bounded-restart exhaustion, surface as harness-level `degraded` state; do not crash the harness (spans will be dropped at BSP buffer overflow; cost attribution continues from in-memory state).
- On structured stop (during C-RT-10 shutdown): flush daemon buffers to sqlite, close sqlite cleanly, terminate daemon process/thread, await termination with timeout.
- No-network-egress invariant per OD §Decision §1.7 is preserved by the daemon library; the supervisor does not weaken it.

**Daemon implementation mode.** Implementation-discretion: the supervisor may run the daemon as a separate process (subprocess), as an asyncio task in the same process, or as a thread. Choice affects crash-isolation properties but not the supervisor contract.

**Invariants.**

- Daemon lifecycle is strictly contained within harness process lifecycle. No collector survives harness shutdown; no collector persists across runs (sqlite file persists when on-disk persistence is configured; daemon does not).
- Collector binding at `local_first_otlp_collector.bind_in_process_collector(...)` per OD spec is called once at stage 4.
- sqlite trace-storage location is **OD-internal** per OD plan v2.6 §0.9 (`OD-internal` framing): the collector library owns the sqlite path semantics, not the IS `PATH_CLASS_REGISTRY`. The 4-value IS `PATH_CLASS_REGISTRY` (`SKILLS` / `PROMPTS` / `ROUTING_MANIFEST` / `STATE_LEDGER`) intentionally does NOT carry a trace-storage class; adding one would be an X-AL-3 architectural extension surfaced at Phase 7 execution. **At Track A** the collector store is in-memory (`closure_invariant = FRESH_ON_RESTART_OPTIONAL_PERSISTENCE_BETWEEN_RESTARTS` per OD C-OD-19 §19.2), which satisfies the spec floor without requiring a path resolver. Future on-disk persistence routes through an OD-internal path resolution (not the IS registry).

**Failure-mode taxonomy.** Per C-RT-14:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-COLLECTOR-PATH` (permanent) | sqlite path unwritable (when on-disk persistence configured; in-memory store at Track A bypasses) | Stage 4 fails; rollback stage 3a/3b/2/1/0 |
| `RT-FAIL-TRANSIENT` (transient) | Daemon initial start fails (e.g., port-bind conflict if subprocess mode uses local port) | Bounded retry per supervisor policy |
| `RT-FAIL-COLLECTOR-DEGRADED` (degraded) | Daemon crashes ≤3 times in 60s but recovers | Continue with logged degradation event |
| `RT-FAIL-HARNESS-DEGRADED` (degraded; ongoing) | Daemon crashes >3 times in 60s | Harness continues in degraded mode; surface as ongoing degradation event in audit ledger |

**Deferred to implementation discretion.** Daemon implementation mode (subprocess / asyncio task / thread); health-check cadence (suggest 10s); restart-bound configuration knobs; backpressure mode when buffer fills (drop oldest vs drop newest — suggest drop oldest per OD ring-buffer semantics).

**Risk surface.** OD spec C-OD-20 §20.1 (after v1.4 FF-2 resolution) committed the 7-value `CollectorPlacement` enum and the per-cell placement matrix; it does not explicitly specify daemon supervision semantics (start / health / structured-stop / restart-bound). The contracts above are runtime-axis additions. If P2-S4-CK v1.1 second pass finds that supervision semantics should live in OD spec instead, escalate to back-flow with an OD spec amendment per `Project_Workflow_v1_8.md` §2.7.6.

---

## §8 C-RT-08 — `run()` Python API contract (F-P2-2 absorption)

**Contract surface.** Signature contract.

**PRD enablement.** Enables every R-IS/AS/CP/OD-* requirement that depends on workflow execution (i.e., nearly all of them).

**ADR commitment(s) honored.** ADR-F4 v1.1 §Decision (run() hands to CP lifecycle loop).

**Fork-resolution provenance.** F-P2-2 ratified 2026-05-19 (Track A ingress = Python API placeholder; operator-facing ingress deferred to Track B).

**Specification content.**

The Track A operator-facing API is exactly one async function exposed at the `harness_runtime` package root:

```python
async def run(
    workflow: WorkflowObject,
    *,
    config: RuntimeConfig | None = None,
) -> RunResult:
    ...
```

**Invariants.**

- **Async-only.** No sync wrapper in Track A. If a synchronous-call surface is later needed, it is Track B's responsibility to add it (and to choose whether via `asyncio.run` wrapping or via a separate threading entry).
- **Single-workflow-object input.** The function accepts exactly one `WorkflowObject` per call. Multi-workflow ingest is Track B (and out of scope for Track A entirely).
- **`config=None` default behavior:** materialize `RuntimeConfig` from defaults + env vars per C-RT-03 precedence. Equivalent to `await run(workflow, config=RuntimeConfig())`.
- **Bootstrap on each invocation OR cached `HarnessContext` reuse?** Track A specifies bootstrap-per-call (no cached context). Track B may add a cached-context entry point with operator-facing lifecycle (`harness_runtime.start() → ctx; await ctx.run(workflow); await ctx.shutdown()`); Track A does not preclude this but does not implement it.
- **Unknown `WorkflowObject` type → typed rejection.** If the input does not conform to the `WorkflowObject` contract (see C-RT-09 risk note), surface typed `InvalidWorkflowError` before bootstrap begins.
- **Idempotency and concurrency (added at v1.1).** Serial invocations are safe and equivalent to independent runs: each call performs a fresh bootstrap → execute → shutdown cycle with no shared state across calls (no cached `HarnessContext`, no cached provider clients, no cached tracer provider). **Concurrent invocations from the same process surface typed `ConcurrentRunNotSupported`** — the second concurrent call detects an existing in-flight `HarnessContext` (via process-local lock initialized at module import) and fails fast before stage 0. Rationale: C-RT-06's `set_tracer_provider(...)` is one-per-process; a second concurrent `run()` would fail at stage 4. Fail-fast at ingress is cleaner. Cached-context model (which would support concurrency) is Track B.

**Risk surface — `WorkflowObject` shape.** F-P2-2 deferred operator-facing ingress to Track B, including the workflow-source format. Track A still needs to type the in-process object that CP's lifecycle loop accepts. CP spec does not currently expose a typed `WorkflowObject` contract. Three options at landing time (Class 1 surface):

1. CP spec extends to expose a `WorkflowObject` contract (likely path; routes via `phase-7-back-flow-routing` with a CP amendment).
2. `harness-core` introduces a thin `WorkflowObject` carrier type the runtime + CP both consume.
3. Runtime defines `WorkflowObject` locally as a structural protocol (duck-typed against CP lifecycle loop expectations).

The choice is made at U-RT-42 landing time, not now. The contract here is the *signature shape*; the typed argument's source is open.

**Failure-mode taxonomy.** Per C-RT-14:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-INVALID-WORKFLOW` (permanent) | `InvalidWorkflowError` | Pre-bootstrap rejection; no `HarnessContext` constructed |
| `RT-FAIL-BOOTSTRAP` (permanent) | Bootstrap failure (any stage) | Per C-RT-02 rollback; surface typed `BootstrapError` with `BootstrapStage` field |
| `RT-FAIL-CONCURRENT-RUN` (permanent) | Second concurrent `run()` invocation detected | Fail fast; existing in-flight run continues unaffected |
| (downstream) | Workflow-execution failures | Per CP lifecycle loop contracts; surfaced through `RunResult` |

**Deferred to implementation discretion.** Sync convenience wrapper (Track B); cached-context entry point (Track B); `WorkflowObject` typed source (per risk surface above); process-local lock implementation (suggest `asyncio.Lock` initialized at module import).

---

## §9 C-RT-09 — `RunResult` shape

**Contract surface.** Schema.

**PRD enablement.** Enables R-OD-* observability requirements (RunResult carries trace IDs + audit-ledger head for inspection).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (audit-ledger head exposure); ADR-F5 v1.1 §Decision (trace ID exposure).

**Fork-resolution provenance.** n/a (general runtime discipline).

**Specification content.**

`RunResult` is a Pydantic v2 `BaseModel` (frozen).

| Field | Type | Semantic |
|---|---|---|
| `status` | `Literal['completed', 'drained', 'failed']` | Terminal status of the workflow execution |
| `workflow_id` | `harness_core.identity.WorkflowID` | Identity of the executed workflow |
| `terminal_state` | `dict[str, Any]` | Workflow's terminal state object per CP lifecycle loop contract |
| `audit_ledger_head_hash` | `str` (hex) | Post-execution audit-ledger head hash for verification |
| `trace_ids` | `list[str]` | Root span trace IDs emitted by the workflow execution |
| `cost_attribution` | `CostAttribution` (OD type) | Aggregated 5-step cost-attribution rollup |
| `failure_cause` | `FailureCause | None` | None unless `status == 'failed'` |

**Invariants.**

- `model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)`.
- `status == 'failed'` implies `failure_cause is not None`.
- `status == 'drained'` indicates `drained_flag` was set during execution and CP loop responded at next lifecycle boundary.
- `audit_ledger_head_hash` always present; `terminal_state` may be `{}` for trivial workflows.
- **Version evolution (added at v1.1).** `RunResult` is part of the operator-facing API surface. Adding an *optional* field is a minor bump; adding a *required* field (i.e., one without a default) breaks consumers that construct `RunResult` from kwargs and is a major bump. Removing a field is always a major bump. Renaming is a major bump. Type-widening of an existing field is minor; type-narrowing is major.

**Failure-mode taxonomy.** `RunResult` is a return value, not an operation; it doesn't fail. Failure modes attach to the workflow execution that produces it (see C-RT-08, C-RT-14, CP lifecycle loop contracts).

**Deferred to implementation discretion.** Exact `FailureCause` enumeration (suggest mirror of CP `validator_fail_taxonomy` 5-class set + a 6th `BootstrapFailure` for pre-execution failures; alternatively reuse C-RT-14 runtime-local fail-class set).

---

## §10 C-RT-10 — Shutdown sequence contract

**Contract surface.** Surface contract.

**PRD enablement.** Enables every R-OD-* requirement that depends on flush-completion (audit ledger consistency, span visibility).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (ledger chain head consistency); ADR-F5 v1.1 §Decision (BSP flush before exit).

**Fork-resolution provenance.** n/a (general runtime discipline).

**Specification content.**

Shutdown executes in **reverse-stage order**: stages constructed last close first. The orchestrator's shutdown entry point is `async def shutdown(ctx: HarnessContext, *, timeout: float = 30.0) -> None`.

**Sequence:**

1. **Drain** (per C-RT-11): set `ctx.drained_flag`; refuse new ingress; allow in-flight workflow steps to complete or surface timeout.
2. **Flush observability state**: `await tracer_provider.force_flush(timeout_millis=...)`; sync ledger writers (`fsync` on `.harness/state.jsonl`); flush cost-attribution chain in-memory state to audit ledger.
3. **Close stage-5/4/3b/3a resources in reverse order:**
   - Stop lifecycle emitter (no-op; emitter holds no state).
   - Stop topology dispatcher / override evaluator (no-op).
   - Stop collector daemon (structured-stop per C-RT-07).
   - `await tracer_provider.shutdown()` — closes BSP + exporter.
   - Close audit writer (no-op; wraps IS writer which is below).
   - Close cost chain (no-op).
   - Close CP routing state (no-op; routing manifest is in-memory).
   - `await client.aclose()` for each provider in `ctx.providers` (per `ProviderClient` Protocol at C-RT-05).
4. **Close stage-2 resources:** disconnect MCP clients; close MCP host.
5. **Close stage-1 resources:** close IS ledger writer (final fsync); close index + cache; release worktree leases.
6. **Verify post-shutdown invariants:**
   - All provider clients closed (idempotent re-close is no-op per `ProviderClient.aclose()`).
   - Collector daemon process/thread terminated.
   - Audit-ledger chain head hash is consistent with last `audit_ledger_head_hash` returned by any `RunResult`.
   - No background task remaining on the asyncio event loop owned by the harness.

**Invariants.**

- Shutdown is idempotent: calling `shutdown(ctx)` twice is safe (second call is a no-op or surfaces a typed `AlreadyShutDown` warning).
- Total shutdown time bounded by `timeout` parameter; exceeding the bound surfaces typed `ShutdownTimeout` with a list of resources that failed to close.
- Resources that fail to close cleanly are surfaced individually; shutdown does not abort on first failure.

**Failure-mode taxonomy.** Per C-RT-14:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-PARTIAL-SHUTDOWN` (partial) | One resource fails to close cleanly | Shutdown completes; failed resources reported in `ShutdownReport` |
| `RT-FAIL-SHUTDOWN-TIMEOUT` (permanent) | Shutdown exceeds `timeout` | Surface `ShutdownTimeout`; process should exit regardless (force-kill upstream) |

**Deferred to implementation discretion.** Default `timeout` value (suggest 30.0s); `ShutdownReport` exposure (returned by `shutdown` or logged-only); whether stage-6 CXA wiring requires unwinding (it doesn't; module imports are not unwound).

---

## §11 C-RT-11 — Drain semantics (runtime-owned flag-polling)

**Contract surface.** Surface contract.

**PRD enablement.** Enables graceful R-OD-* audit-ledger consistency on shutdown.

**ADR commitment(s) honored.** ADR-F4 v1.1 §Decision (lifecycle boundaries are the natural drain checkpoints).

**Fork-resolution provenance.** n/a (general runtime discipline); resolves the F2-05 adversarial-review finding from `.harness/Adversarial_Review_phase_2_session_3_track_a_plan.md` (drain ownership ambiguity).

**Specification content.**

CP spec does not currently expose a native drain primitive. Track A specifies drain at the runtime layer using a flag-polling pattern:

- `HarnessContext.drained_flag: asyncio.Event` is initialized at stage 0 and shared across all bootstrap stages.
- A signal handler (installed at stage 7 on the orchestrator's behalf, listening for `SIGTERM` / `SIGINT`) sets the flag.
- The CP workflow lifecycle loop polls `ctx.drained_flag.is_set()` at each lifecycle boundary (per-step entry, per-step exit, per-topology-dispatch entry). On detecting the flag, the loop:
  1. Completes the current in-flight step (no mid-step interruption).
  2. Returns a `RunResult` with `status='drained'` and the partial terminal state.

  *(v1.2 amendment, 2026-05-20):* an earlier draft committed step 2 to emit a `WorkflowEventClass.DRAINED` event. The canonical `harness_core.workflow_event_class` enum is closed at 8 per C-CP-05 §5.1 with no `DRAINED` value; alignment failed at U-RT-41 landing per spec §16 open question #9. The emit step is STRUCK from C-RT-11. Drain observability survives without it via the two remaining surfaces above: `ctx.drained_flag` (asyncio.Event signal-level observability) + `RunResult.status='drained'` (terminal-return observability). This resolves `[[fork-drained-event-class]]` Path B.
- After flag-set, `harness_runtime.run(...)` rejects new invocations with typed `HarnessDraining` error.

**Invariants.**

- The flag is one-way: once set, it stays set for the remaining process lifetime. A new harness invocation requires process restart.
- Drain bounded-wait timeout (per `shutdown(ctx, timeout=...)` parameter) bounds how long shutdown waits at step 1 of C-RT-10. Exceeding the bound forces shutdown to proceed regardless; in-flight step may be in inconsistent state (CP lifecycle is responsible for transactional discipline if it claims it).
- The flag does NOT propagate into sub-agent or sub-workflow boundaries that run outside the harness process (e.g., a long MCP tool call). Those continue to completion; the harness drain waits or times out.

**Failure-mode taxonomy.** Per C-RT-14:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-DRAIN-TIMEOUT` (transient) | Drain times out before in-flight step completes | Shutdown proceeds; `RunResult.status == 'drained'`; downstream observability reflects partial-completion |

**Risk surface.** If CP later surfaces a native drain primitive (e.g., a CP-level `WorkflowDrainController` type), refactor `harness-runtime/` to delegate drain to CP. This contract becomes a thin adapter. Until then, drain ownership is runtime-axis-local.

**Deferred to implementation discretion.** Signal-handler installation site (suggest at stage 7 INGRESS_ACCEPT); whether to expose a Python API for programmatic drain in addition to signal-handler (suggest yes: `ctx.drained_flag.set()` is the API); behavior under repeated `SIGTERM` (suggest second signal escalates to immediate-stop bypassing drain).

---

## §12 C-RT-12 — CXA wiring obligations

**Contract surface.** Surface contract + per-bucket wiring contracts.

**PRD enablement.** Enables every cross-axis observable behavior that depends on runtime wiring (CP-emitted audit entries reaching IS ledger chain; OD-emitted breaker spans reaching CP namespace ingestion; etc.).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (CP→IS ledger composition); ADR-F5 v1.1 §Decision (OD→CP namespace ingestion).

**Fork-resolution provenance.** D-P2-2 ratified 2026-05-19 (24 phase-2-runtime CXA edges in scope for Track A).

**Specification content.**

The runtime is responsible for two distinct CXA categories at stage 6:

### §12.1 Terminal aggregate exporter manifest import (side-effect)

The composition root imports the 5 terminal aggregate exporter manifests so their import-time side-effects realize. Per CXA v2.3 §3, the 22 genuine Pattern P1 typed seams are realized at module-import time; the composition root's import of the consumer modules is what causes them to load and bind their producer references.

| Manifest | Module |
|---|---|
| IS substrate seam exports | `harness_is.substrate_seam_exports` (per IS C-IS-10 §10) |
| AS substrate seam exports | `harness_as.as_substrate_seam_exports` (per AS C-AS-16 §16) |
| CP namespace export manifest | `harness_cp.cp_namespace_export_manifest` (per CP C-CP-24) |
| CP cross-axis composition manifest | `harness_cp.cp_cross_axis_composition_manifest` (per CP C-CP-24) |
| OD substrate seam exports aggregate | `harness_od.substrate_seam_exports_aggregate_manifest` (per OD spec; specific §-pin verified at U-RT-33 landing) |

Verification (separate from wiring): for each of the 22 typed seams, the runtime emits a Pattern P1 identity-equality assertion (`consumer_module.SYMBOL is producer_module.SYMBOL`). Verification lives in tests, not in runtime code. (See plan v2 U-RT-51.)

### §12.2 Phase-2-runtime edges: AS → IS (1 edge)

| Edge | Producer call site | Consumer surface | Payload | Post-wiring invariant |
|---|---|---|---|---|
| U-AS-27 → U-IS-11 | AS skill-load completion site (skill-discovery emission) | IS ledger append via `ctx.ledger_writer.append(entry)` | `StateLedgerEntry` (per C-IS-05 §5) carrying skill-load metadata | Skill-load event appears in `.harness/state.jsonl` with chain integrity intact (verifiable via C-IS-06 §6) |

Wiring contract: at stage 6, the runtime hands `ctx.ledger_writer.append` to the AS skill-load completion site via callback registration. Plan v2 U-RT-34.

### §12.3 Phase-2-runtime edges: CP → IS (17 edges)

Source units: U-CP-12, U-CP-14, U-CP-27, U-CP-30, U-CP-34, U-CP-37, U-CP-49, U-CP-50, U-CP-52. Target units: U-IS-07, U-IS-08, U-IS-09, U-IS-11. (Note: target-unit IDs reference plan-level units; the *contract* target is C-IS-05 §5 entry shape + C-IS-07 §7 read/write contract pair.)

All 17 edges are ledger-emission patterns. The wiring contract is uniform:

| Wiring contract | Per-edge instance |
|---|---|
| Callable signature | `Callable[[StateLedgerEntry], EntryHash]` |
| Payload type | `StateLedgerEntry` (C-IS-05 §5 6-field shape) |
| Post-wiring invariant | At each enumerated CP source unit's emission site, the spec'd IS ledger entry is appended; `chain_verification` (C-IS-06 §6) passes post-emission |

Wiring contract per-edge: at stage 6, the runtime hands `ctx.ledger_writer.append` to each of the 9 CP source units via callback registration (the 17 edges aggregate across the 9 source units; some source units emit multiple entry variants). Plan v2 U-RT-35 (split-allowed per the plan if signature divergence surfaces at any source unit).

### §12.4 Phase-2-runtime edges: OD → IS (2 edges)

| Edge | Producer call site | Consumer surface | Payload | Post-wiring invariant |
|---|---|---|---|---|
| U-OD-30 → U-IS-11 | OD audit-emission site | IS ledger append via `ctx.audit_writer.append(tenant_id, audit_entry)` | `AuditLedgerEntry` (OD-spec'd; specific §-pin verified at U-RT-32 landing) wrapping into `StateLedgerEntry` | OD audit entry reaches IS chain; `chain_verification` passes |
| U-OD-34 → U-IS-17 | OD terminal-exporter manifest declaration | IS terminal-exporter manifest string reference resolution | Manifest string reference (not a value) | Manifest string ID resolves at composition; downstream import-time consumers see consistent string |

Plan v2 U-RT-36.

### §12.5 Phase-2-runtime edges: OD → AS (1 edge)

| Edge | Producer call site | Consumer surface | Payload | Post-wiring invariant |
|---|---|---|---|---|
| U-OD-34 → U-AS-33 | OD terminal-exporter manifest declaration (AS namespace verification target) | AS namespace exports surface (per C-AS-16 §16) | Manifest string reference | AS namespace verification runs at bootstrap; mismatch surfaces typed |

Plan v2 U-RT-37.

### §12.6 Phase-2-runtime edges: OD → CP (3 edges, inversion/manifest)

| Edge | Producer call site | Consumer surface | Payload | Post-wiring invariant |
|---|---|---|---|---|
| U-OD-09 → U-CP-54 | OD `harness.breaker.*` namespace export (F-CP-01 Stage 3b inversion) | CP namespace ingestion at composition | Namespace declaration (typed; per CP C-CP-09 §9 `engine.*` pattern, applied to `harness.breaker.*`) | CP ingestion of `harness.breaker.*` observable |
| U-OD-34 → U-CP-54 | OD terminal-exporter manifest declaration (CP namespace target) | CP namespace export manifest (per C-CP-24) | Manifest string reference | Manifest reference resolves |
| U-OD-34 → U-CP-55 | OD terminal-exporter manifest declaration (CP carry-forward target — F2-12 inheritance) | CP cross-axis composition manifest (per C-CP-24) | Manifest string reference (F2-12 carry-forward) | Manifest reference resolves; dashboard bindings observable |

Plan v2 U-RT-38.

**Invariants (across §12.1–§12.6).**

- The 5 manifest imports (§12.1) occur before any of the 24 edges wire; manifest imports are a precondition.
- Pattern P1 identity-equality holds for all 22 typed seams (verified at L11 tests; runtime code asserts this only in debug builds — see C-RT-12 deferred clause).
- Each of the 24 phase-2-runtime edges is exercised by at least one integration test (per plan v2 U-RT-34..U-RT-38 acceptance criteria).
- Edge wiring failures surface at stage 6 as typed errors naming the (source-unit, target-unit) pair.

**Deferred to implementation discretion.** Whether `cxa_phase2_runtime_edges.py` is a single module or split per-bucket (suggest single module with per-bucket section structure for readability); whether Pattern P1 verification runs in debug builds (suggest yes via env var `HARNESS_VERIFY_P1=1`); edge wiring callable signature beyond the per-bucket tables above (e.g., for §12.3 the registration mechanism — callback vs decorator vs explicit table — is implementation-discretion).

---

## §13 C-RT-13 — Admin stub semantics

**Contract surface.** Surface contract.

**PRD enablement.** Enables operator-facing inspection and shutdown of a running harness (Track A minimum; richer admin UX is Track B).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (state-ledger read-only inspection); ADR-F5 v1.1 §Decision (collector sqlite read-only inspection).

**Fork-resolution provenance.** F-P2-2 (admin stubs are the Track-A-allowed CLI surface; operator-facing `run` is Track B).

**Specification content.**

The runtime exposes two admin CLI stubs via `[project.scripts]` in `pyproject.toml`:

**`harness-inspect` (read-only).**

- Opens state ledger (`.harness/state.jsonl`) and collector sqlite (path resolved via PATH_CLASS_REGISTRY per C-IS-01 §1) in **read-only mode**. No writes.
- Dumps a summary: ledger head hash + last N entries (N from CLI flag, default 10); last N spans from collector (default 10); current cost-attribution rollup if available.
- Runs against a **stopped harness** (does not require a running process); does not modify any state.
- Exits 0 on success; nonzero on file-not-found or read-error.

**`harness-shutdown` (signal-running-instance).**

- Reads pidfile (location resolved via PATH_CLASS_REGISTRY; suggest `.harness/runtime.pid`).
- Sends `SIGTERM` to the pid.
- Optionally waits for process exit with `--wait <seconds>` (default: no wait).
- Exits 0 on signal delivery success; nonzero on pidfile-missing or signal-delivery error.
- The receiving harness instance's signal handler is responsible for the actual drain → shutdown sequence (per C-RT-10 + C-RT-11).

**Pidfile lifecycle.** The harness writes its pidfile at stage 7 INGRESS_ACCEPT and removes it at the end of `shutdown()`. Pidfile contents are the pid only. Stale pidfiles (process not running) surface as `harness-shutdown` typed error.

**Invariants.**

- `harness-inspect` MUST NOT write to any file. Tested by chmod-readonly fixture.
- `harness-shutdown` MUST NOT touch state ledger / collector sqlite / configuration files. It only reads pidfile and emits a signal.
- Richer admin IPC (e.g., a unix socket protocol for query / drain / status) is explicitly Track B.

**Failure-mode taxonomy.** Per C-RT-14:

| Command | Fail class | Trigger |
|---|---|---|
| `harness-inspect` | `RT-FAIL-INSPECT-PATH` (permanent) | Ledger / sqlite path missing or unreadable |
| `harness-shutdown` | `RT-FAIL-ADMIN-PIDFILE` (permanent) | Pidfile missing; pid not running; signal delivery denied |

**Deferred to implementation discretion.** CLI argument parsing library (suggest `argparse` stdlib; no `click` / `typer` per framework-pull discipline at this layer); output format (suggest human-readable default + `--json` flag); pidfile location (default `.harness/runtime.pid`; configurable via `RuntimeConfig`).

---

## §14 C-RT-14 — Runtime-local fail-class taxonomy (new at v1.1; Reading 1 absorption of F2-01)

**Contract surface.** Enum + relationship contract.

**PRD enablement.** Enables every R-IS/AS/CP/OD-* requirement that needs typed failure surfaces at the runtime boundary.

**ADR commitment(s) honored.** ADR-F4 v1.1 §Decision (workflow lifecycle includes failure surfaces); ADR-F5 v1.1 §Decision (failures emit observability events).

**Fork-resolution provenance.** Adversarial-review finding F2-01 at P2-S4-CK 2026-05-19, resolved Reading 1 by operator: runtime axis owns runtime-local fail classes orthogonal to CP's `validator_fail_taxonomy`.

**Specification content.**

The runtime axis introduces a fail-class enumeration distinct from CP's workflow-step-level `validator_fail_taxonomy` (5-class set at landed `harness_cp.validator_fail_taxonomy`). The two are orthogonal: CP's taxonomy covers *workflow-step* failures (validator-fail, transient, permanent at the step boundary); the runtime taxonomy covers *bootstrap-stage* and *runtime-lifecycle* failures (config, secret, provider, collector, bootstrap, shutdown).

**Runtime-local fail-class enumeration:**

| Fail class | Severity | Surface | Recovery |
|---|---|---|---|
| `RT-FAIL-CONFIG` | permanent | Stage 0 PREAMBLE | None; operator fixes config |
| `RT-FAIL-CONFIG-VERSION` | permanent | Stage 0 PREAMBLE | None; operator migrates config |
| `RT-FAIL-SECRET-MISSING` | permanent | Stage 0 (validation) or stage 3a (resolution) | None; operator adds secret to keyring |
| `RT-FAIL-TRANSIENT` | transient | Any stage (stage-internal bounded retry) | Bounded retry; escalates if persistent |
| `RT-FAIL-PROVIDER-AUTH` | permanent | Stage 3a CP_CLIENTS | None; operator fixes provider credentials |
| `RT-FAIL-PROVIDER-UNREACHABLE` | permanent | Stage 3a CP_CLIENTS (after RT-FAIL-TRANSIENT escalation) | None; operator fixes network/provider availability |
| `RT-FAIL-PROVIDER-DEGRADED` | degraded | Stage 3a CP_CLIENTS (Ollama-optional path) | Continue with reduced provider set |
| `RT-FAIL-COLLECTOR-PATH` | permanent | Stage 4 OD | None; operator fixes path permissions |
| `RT-FAIL-COLLECTOR-DEGRADED` | degraded | Stage 4 OD or runtime | Bounded restart; observability survives |
| `RT-FAIL-HARNESS-DEGRADED` | degraded (ongoing) | Runtime | Continue in degraded mode; downstream observability reflects |
| `RT-FAIL-BOOTSTRAP` | permanent | Any stage failing the bootstrap orchestrator | Reverse-order rollback per C-RT-02; surface to caller |
| `RT-FAIL-PARTIAL-ROLLBACK-REQUIRED` | partial | Stage N+1 fails after stage N completes | Reverse-order shutdown for stages 0..N |
| `RT-FAIL-INVALID-WORKFLOW` | permanent | `run()` pre-bootstrap input validation | None; caller passes wrong type |
| `RT-FAIL-CONCURRENT-RUN` | permanent | `run()` ingress concurrency lock | None; caller serializes or uses cached-context (Track B) |
| `RT-FAIL-CONCURRENT-REGISTRATION` | permanent | `set_tracer_provider` double-call | None; indicator of orchestrator bug |
| `RT-FAIL-DRAIN-TIMEOUT` | transient | C-RT-11 drain wait | Shutdown proceeds; partial-completion observable |
| `RT-FAIL-PARTIAL-SHUTDOWN` | partial | C-RT-10 shutdown | Surface in `ShutdownReport` |
| `RT-FAIL-SHUTDOWN-TIMEOUT` | permanent | C-RT-10 shutdown wait | Process force-exit upstream |
| `RT-FAIL-INSPECT-PATH` | permanent | `harness-inspect` admin stub | None; operator fixes path |
| `RT-FAIL-ADMIN-PIDFILE` | permanent | `harness-shutdown` admin stub | None; operator verifies running harness |
| `RT-FAIL-FALLBACK-EXHAUSTED` (new at v1.4) | permanent | C-RT-16 wrapper exhausts the fallback chain after per-candidate retry exhaustion | Driver `try/except` maps to `step-failure: RT-FAIL-FALLBACK-EXHAUSTED: ...` per C-CP-25 §25.3.3.4 |
| `RT-FAIL-SUB-AGENT-CHILD-FAILED` (new at v1.6) | permanent | C-RT-17 child sub-workflow's terminal `RunResult.status == FAILED` after child-runner invocation | Composer raises typed `SubAgentChildFailedError`; driver `try/except` maps to `step-failure: RT-FAIL-SUB-AGENT-CHILD-FAILED: ...` per C-CP-25 §25.3.3.4 |
| `RT-FAIL-SUB-AGENT-TOPOLOGY-INADMISSIBLE` (new at v1.6) | permanent | C-RT-17 `is_admissible(topology, workload_class)` returns False before sub-workflow invocation | Composer raises typed `SubAgentDispatchTopologyInadmissibleError`; driver `try/except` maps to `step-failure: RT-FAIL-SUB-AGENT-TOPOLOGY-INADMISSIBLE: ...` per C-CP-25 §25.3.3.4 |
| `RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND` (new at v1.6) | permanent | Driver invokes `ctx.step_dispatchers.lookup(step.kind)` with an unbound step_kind (3 of 5 unbound at v1.6) | Registry raises `StepKindDispatcherNotBoundError`; driver `try/except` maps to `step-failure: RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND: ...` per C-CP-25 §25.3.3.4 |

**Relationship to CP `validator_fail_taxonomy`:**

| Dimension | Runtime taxonomy (this spec) | CP `validator_fail_taxonomy` |
|---|---|---|
| Scope | Bootstrap-stage + runtime-lifecycle failures | Workflow-step-level validator failures inside CP loop |
| Lifetime | Process-startup, ingress, shutdown | Per-step within an executing workflow |
| Cause attribution | Stage / lifecycle phase / resource | Validator category per C-CP-05 §5 |
| Recovery | Per row above | Per CP `validator_fail_transient_staircase` |
| Audit-ledger emission | RT failures emit via C-RT-04 `audit_writer` at C-RT-14 emission site | CP validator failures emit per CP audit-emission contract |

The two taxonomies are **orthogonal and composable**: a workflow execution that completes bootstrap successfully but then has a validator failure within CP emits a CP `validator_fail_taxonomy` value via CP's emission site; a workflow that fails *before* CP loop starts (e.g., bootstrap failure) emits an `RT-FAIL-*` value via the runtime's emission site. No fail-class is in both taxonomies; cause-attribution disambiguates.

**Invariants.**

- Each `RT-FAIL-*` value is a Python `str` enum member at `harness_runtime.fail_classes.RuntimeFailClass`.
- Every failure surfaced by the runtime carries exactly one `RuntimeFailClass` value (no plural; no untagged failures).
- Every `RT-FAIL-*` permanent / partial value emits an audit-ledger entry via `ctx.audit_writer` (C-RT-04) before propagating; transient failures emit at escalation only.
- Severity column above is normative: permanent / transient / degraded / partial / ongoing-degraded.

**Failure-mode taxonomy.** N/A — this contract *is* the failure-mode taxonomy.

**Deferred to implementation discretion.** Exact enum class name (suggest `RuntimeFailClass`); whether `RT-FAIL-*` string values are stable across versions (recommended: stable, since they appear in audit ledger and operator-facing logs); cause-attribution payload shape attached to each failure surface (suggest a Pydantic `RuntimeFailureCause` model per row).

---

## §14.5 C-RT-15 — LLM-dispatch composer (new at v1.2; Q1a + Q2a + Q3a absorption of `fork_llm_dispatch_composer_scope.md`)

**Contract surface.** Composer module + Protocol-satisfying callable + integration obligations with C-RT-04 (HarnessContext), C-RT-05 (ProviderClient), C-RT-06 (TracerProvider).

**PRD enablement.** Enables R-CP-* multi-LLM routing requirements *at runtime* (C-RT-05 enabled construction; C-RT-15 enables invocation). Enables R-OD-* observability requirements *for GenAI spans* (C-RT-06 enabled TracerProvider; C-RT-15 enables span emission with GenAI semconv attributes).

**ADR commitment(s) honored.** ADR-F1 v1.2 §Decision (multi-LLM routing operationalized at runtime, not just at design + spec + library code); ADR-F5 v1.1 §Decision (observability substrate carries GenAI-semconv attribution per OD spec C-OD-04..08).

**Fork-resolution provenance.** `.harness/fork_llm_dispatch_composer_scope.md` (filed 2026-05-20). Operator ratification (recorded at fork §5):

- **Q1a** — Option A: in-Phase-7 closure via new runtime contract (NOT Class 1 back-flow; NOT Phase-3 deferral).
- **Q2a** — Per-step composer only (smallest scope); fallback / retry / breaker wrappers explicitly out of scope (CP-3 + CP-4 retirements deferred to follow-on units).
- **Q3a** — GenAI semconv 1.41.0 binding included in the same arc (enables H_T-OD-2 PARTIAL → RETIRE-READY upgrade).
- **Q4a** — Resolve same-day (file → ratify → resolve arc per `[[fork-u-rt-49-cost-attribution-invocation-underspec]]` + `[[fork-u-cp-56-resumption-underspec]]` precedent; phased per scope-honesty AskUserQuestion as: spec + plan + composer skeleton this session; implementation + tests + retirement events follow-on session).

**Specification content.**

The runtime contributes one production composer to the `harness_cp.workflow_driver.StepDispatcher` Protocol seam (declared at `harness-cp/src/harness_cp/workflow_driver.py:151`). The composer is a per-step function: given a resolved `StepEffectiveBinding` (which carries the selected provider identity + model name + sandbox-tier floor) and a `WorkflowStep` (which carries the step input payload), the composer:

1. Resolves the `ProviderClient` adapter via `ctx.providers` (C-RT-04 `providers` field bound at C-RT-05) using `binding.model_binding.provider` (the CP `ModelBinding.provider: str` field per C-CP-01 §1.4 routing-binding vocabulary).
2. Coerces `step.step_payload` to `harness_cp.cp_shared_types.ProviderAgnosticPayload` per the **Payload-shape contract** below (`(messages, tools, params)` 3-tuple per ADR-F1 v1.2 + C-CP-01 §1.1).
3. Starts a span on the runtime's TracerProvider (C-RT-06 `ctx.tracer_provider`) under the GenAI semconv 1.41.0 attribute set per OD spec C-OD-04..08 (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, plus the per-provider sub-namespaces for Anthropic primitive observability per AS spec C-AS-13/14 — `anthropic.*` namespace activated for the anthropic provider per §6.3.1 cross-axis dependency cascade closure).
4. Dispatches to the provider's underlying SDK message-construction method (provider-specific: `anthropic.AsyncAnthropic.messages.create` / `openai.AsyncOpenAI.chat.completions.create` / `ollama.AsyncClient.chat`). Per-provider helpers translate `ProviderAgnosticPayload` → SDK kwargs: `messages` + `tools` (when present) pass through unchanged; `params` keys merge into the call kwargs. The capability-aware abstraction layer (CP C-CP-01 §1) determines which method to call; the composer is the runtime-side site that actually calls it.
5. Captures provider response, populates span attributes (request/response/usage), and constructs the step-output mapping per the `StepDispatcher` Protocol return shape (`Mapping[str, Any]`). Provider responses (all pydantic v2 models from the three SDKs) coerce via `response.model_dump()`.
6. Returns the step output.

**Payload-shape contract (new at v1.3, Class 3 fork resolution per `.harness/fork_u_rt_52_step_payload_shape.md`).**

`step.step_payload: Mapping[str, Any]` (the opaque field at `harness_cp.workflow_driver_types.WorkflowStep`) is consumed as a `harness_cp.cp_shared_types.ProviderAgnosticPayload` mapping:

```python
class ProviderAgnosticPayload:
    messages: tuple[Mapping[str, Any], ...]
    tools: tuple[Mapping[str, Any], ...] | None
    params: Mapping[str, Any]
```

Composer pydantic-validates the payload at dispatch entry. Mis-shaped payloads surface as `LLMDispatchPayloadShapeError` mapping to the new `RT-FAIL-PAYLOAD-SHAPE` fail class (see Failure-mode taxonomy below). The convention is anchored at:

- ADR-F1 v1.2 §Decision — provider-neutral thin core commitment.
- C-CP-01 §1.1 — `(messages, tools, params)` 3-tuple substrate.
- `harness_cp.cp_shared_types.ProviderAgnosticPayload` — landed at U-CP-00c L0 carrier.

`ProviderAgnosticPayload` is opaque to the driver and faithful FACTOR-OUT of C-CP-01 §1.1; the composer is the only runtime site that unpacks it.

**Composer module residence.** `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` (new file at v1.2). Module exposes one production class — `RuntimeLLMDispatcher` — that satisfies `StepDispatcher` via duck-typing (the Protocol is `runtime_checkable` at `workflow_driver.py:151`). Construction site: bound at bootstrap stage 5 (LOOP_INIT) alongside the existing override evaluator + topology dispatcher + lifecycle emission hook (per C-RT-02 stage 5 invariants); attached to `ctx` for downstream `run()` consumption.

**Integration with C-RT-04 (HarnessContext).** No new field. The dispatcher consumes `ctx.providers` + `ctx.provider_capabilities` + `ctx.tracer_provider` (all existing); is itself stage-5-materialized into a new context field if and only if the operator chooses a top-of-context attachment shape vs a constructed-at-step-call shape. Defer to implementation discretion. The MVP shape attaches at `ctx.llm_dispatcher` for caller-explicit composition with `run()`.

**Integration with C-RT-05 (ProviderClient).** No protocol change to `ProviderClient` at v1.2. The composer dispatches via per-provider adapter methods that are *not* part of `ProviderClient.aclose()`; the protocol remains lifecycle-only. The composer carries provider-specific dispatch code (one branch per provider) — this is the capability-aware abstraction layer per ADR-F1 v1.2 + CP C-CP-01.

**Integration with C-RT-06 (TracerProvider).** GenAI semconv binding: composer obtains a `Tracer` via `ctx.tracer_provider.get_tracer("harness.runtime.llm_dispatch")` and emits one span per LLM call. Attributes follow OpenTelemetry GenAI semantic conventions 1.41.0 (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.response.id`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, etc.). For the anthropic provider, additionally emit the 4-attribute `anthropic.cache_*` subset of C-AS-14 §14.2 (per v1.3 enumeration):

| Attribute | Source | Behavior |
|---|---|---|
| `anthropic.cache_creation_input_tokens` | `response.usage.cache_creation_input_tokens` | Response-side; emitted when SDK populates the field. |
| `anthropic.cache_read_input_tokens` | `response.usage.cache_read_input_tokens` | Response-side; emitted when SDK populates the field. |
| `anthropic.cache_breakpoint_id` | Request-side: ordinal of first `cache_control`-bearing content block (`msg-{index}`) | Best-effort extraction from request payload; `None` when no `cache_control` directive present. |
| `anthropic.cache_ttl_seconds` | Request-side: `cache_control.ttl` translated to seconds (`"5m"` → 300; `"1h"` → 3600; default 300 when `cache_control` present without explicit ttl) | Best-effort extraction from request payload; `None` when no `cache_control` directive present. |

The remaining 6 attributes in C-AS-14 §14.2 (`thinking_mode` / `thinking_budget_tokens` / `thinking_effort` / `batch_id` / `tokenizer_version` / `inference_geo`) are out of scope for v1.3 — they require either separate SDK-feature surface adoption (thinking modes) or operator-level configuration (geo / batch / tokenizer pinning) that does not exist at the v1.3 composer surface. Future revisions add them at the feature-surface landing event, not here.

**Invariants.**

- Composer is async (matches C-RT-08 async-only `run()` posture). No sync wrapper.
- Exactly one span per LLM call. Span lifecycle (start / end / exception capture) bound by a `with tracer.start_as_current_span(...)` block (per v1.3 correction: OpenTelemetry's tracer context manager is synchronous — returns a regular `ContextManager`, not an `AsyncContextManager` — so the composer uses plain `with` inside the async `dispatch` body. v1.2 phrasing "`async with ...`" was imprecise; semantic unchanged).
- Composer satisfies `isinstance(dispatcher, StepDispatcher)` via `@runtime_checkable` introspection (verified at bootstrap stage 5 binding).
- Provider-specific dispatch branches are exhaustive: composer raises `RT-FAIL-PROVIDER-UNREACHABLE` (per C-RT-14) if `binding.model_binding.provider` resolves to a provider not in `ctx.providers` (e.g., Ollama-degraded path skipped a registration).
- GenAI semconv attribute set is normative per OTel spec 1.41.0 — composer MUST set the required attributes; SHOULD set the recommended attributes; MAY set the opt-in attributes per OTel semconv stability discipline.
- `anthropic.*` namespace attributes per C-AS-14 §14.2 are emitted **only** when `binding.model_binding.provider == "anthropic"` (per AS-AL-3 cross-axis Skills isomorphism doesn't exempt the per-provider attribute scope).
- Composer does NOT implement fallback / retry / breaker per Q2a scope discipline; on provider-side exception, composer propagates the exception unmodified to the `workflow_driver` `try / except` boundary at `workflow_driver.py:380-389` (which fails the step with `step-failure: {type}: {exc}` per existing C-CP-25 §25.3.3.4 contract).

**Failure-mode taxonomy.** Per C-RT-14:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-PROVIDER-UNREACHABLE` (permanent) | `binding.model_binding.provider` not in `ctx.providers` (e.g., Ollama-degraded path was taken) | Raise; propagates to driver `try / except` boundary; driver fails the step with `step-failure: RT-FAIL-PROVIDER-UNREACHABLE: ...` |
| `RT-FAIL-TRANSIENT` (transient) | Provider SDK raises a documented transient error (network, rate limit, server 5xx) | Raise unmodified — composer does NOT retry per Q2a; driver fails step; CP-3 retry logic (separate future unit) wraps composer when it lands |
| `RT-FAIL-PROVIDER-AUTH` (permanent) | Provider SDK raises auth error (401/403) | Raise unmodified |
| `RT-FAIL-PAYLOAD-SHAPE` (permanent, new at v1.3) | `step.step_payload` not coercible to `ProviderAgnosticPayload` (missing `messages` / wrong shape / pydantic validation failure) | Raise; propagates to driver `try / except` boundary; driver fails the step with `step-failure: RT-FAIL-PAYLOAD-SHAPE: ...` |

v1.3 introduces one new fail class (`RT-FAIL-PAYLOAD-SHAPE`); the remaining three carry forward from C-RT-14 unchanged.

**Deferred to implementation discretion.**

- Exact composer class name (suggest `RuntimeLLMDispatcher` per v1.2 spec body recommendation).
- Whether composer attaches at `ctx.llm_dispatcher` or is constructed per-step inside `run()`'s caller composition (MVP recommendation: attach at ctx for parallel construction with override evaluator / topology dispatcher / lifecycle emitter).
- GenAI semconv attribute selection beyond the required set (which optional attributes to emit by default — request/response body, message content, finish reason — driven by OD redaction discipline at C-OD-13..16; composer emits the basic set, SpanProcessor handles redaction).
- Span name convention (suggest `gen_ai.{provider}.{model_or_method}` per OTel GenAI semconv guidance, e.g., `gen_ai.anthropic.messages.create`).
- Whether provider-specific dispatch branches live in `llm_dispatch.py` directly or in per-provider sub-modules (`llm_dispatch_anthropic.py` etc.) — defer to module-size discretion at implementation.
- Test mock strategy: suggest a `MockProviderClient` fixture per provider that records dispatched calls + returns canned responses; pytest-asyncio for async surface.

---

## §14.6 C-RT-16 — Retry/breaker/fallback composer wrapping C-RT-15 (new at v1.4; D1–D6 + Q1=a + Q2=c absorption of `class_1_tension_cp_3_retry_breaker_composer_underspec.md`)

**Contract surface.** Wrapper module + Protocol-satisfying callable + integration obligations with C-RT-15 (inner LLM-dispatch composer), `ctx.retry_breaker` (U-RT-24 registry binding), `ctx.fallback_chain` (stage 3b binding), C-RT-06 (TracerProvider for nested span emission), C-CP-03 §3.5 (`retry.*` namespace + dual-emission), C-CP-04 §4.2 (`fallback.exhausted` event semantics), C-OD-07 §7.1 (`harness.breaker.*` 7-attribute schema, emitted by the existing `RuntimeRetryBreaker.emit_breaker_transition_event` site — no new OD emission code).

**PRD enablement.** Completes the multi-LLM runtime composition surface: C-RT-15 enabled per-step single-attempt dispatch; C-RT-16 enables resilient multi-attempt + multi-candidate dispatch. R-CP-04 + R-CP-07 (CP retry/fallback observability at runtime). R-OD-05 (cost-attribution chain stability against retry-storm — exhaustion produces a single typed terminal fail-class rather than a flood of bare provider exceptions).

**ADR commitment(s) honored.** ADR-F1 v1.2 §Decision (multi-LLM resilience operationalized at runtime, not just at design + spec + library code — closes the §6.3.2 cascade gate via H_T-CP-3 retirement); ADR-D3 v1.2 §Decision (validation-contract retry-staircase semantics composed at the dispatch site via `RuntimeRetryBreaker.advance_staircase`).

**Fork-resolution provenance.** `.harness/class_1_tension_cp_3_retry_breaker_composer_underspec.md` (filed 2026-05-20 at `7fe2c95`). Operator ratification (recorded at fork "Operator decision (2026-05-20)" section):

- **D1** — Composer owns the candidate-iteration loop (iterates `fallback_chain` candidates; per-candidate runs retry loop). Not a single-(provider, model) wrapper.
- **D2** — Retry-eligible iff the provider exception matches CP §21.2 transient staircase (`REFLEXION` / `RETRY_WITH_BACKOFF` stages); fail-fast otherwise (AUTH, payload-shape, shutdown). Composer delegates to `RuntimeRetryBreaker.advance_staircase` per existing C-CP-21 contract.
- **D3** — Nested span emission: one outer span per composer invocation (covers the full retry+fallback envelope); one inner span per attempt carrying the C-CP-03 §3.5 `retry.*` 6-attribute namespace. Matches the OD sampling gradient (head sampler picks outer; tail sampler picks inner).
- **D4** — On fallback chain exhaustion: composer emits `fallback.exhausted` event on the outer span before raising; raises new typed `RT-FAIL-FALLBACK-EXHAUSTED` fail class. The existing `workflow_driver.py:380-389` `try/except` boundary catches and maps to `step-failure: RT-FAIL-FALLBACK-EXHAUSTED: ...` per C-CP-25 §25.3.3.4 contract.
- **D5** — Breaker emission ownership stays with the registry: composer calls `breaker.record_failure()` / `record_success()` / `attempt_half_open()` per the existing `BreakerStateMachine` API; the registry's existing `RuntimeRetryBreaker.emit_breaker_transition_event` handles `harness.breaker.*` span emission per C-OD-07 §7.1. Composer code is thin against breaker concerns.
- **D6** — Bootstrap wiring: stage 5 (LOOP_INIT) constructs `RetryBreakerFallbackDispatcher(inner=RuntimeLLMDispatcher(...), retry_breaker=ctx.retry_breaker, fallback_chain=ctx.fallback_chain, tracer=ctx.tracer_provider.get_tracer("harness.runtime.retry_breaker_fallback"))` and assigns to `ctx.llm_dispatcher`. The bare `RuntimeLLMDispatcher` becomes a private constructor arg of the wrapper (not removed; still constructed at stage 5, just not surfaced as the top-level `ctx.llm_dispatcher`). `workflow_driver` code at line 379 unchanged — invokes `ctx.llm_dispatcher.dispatch(binding, step)` and gets the wrapper.
- **Q1=a** — Nested attempt budget: per-candidate retry up to `RetryPolicy.max_attempts` (full-jitter backoff per `compute_full_jitter_delay_seconds`); on exhaustion call `advance_or_raise(chain, failed_candidate)` to advance to next candidate; next candidate gets its own retry budget. `RetryPolicy.max_attempts` is the per-(provider, model) attempt budget; chain length is a separate per-step budget (operator-supplied via `RoutingManifest.fallback_chain` at C-CP-04).
- **Q2=c** — Registry key extension: the `RuntimeRetryBreaker` registry exposes a reserved `"llm_dispatch"` policy key alongside per-tool keys (see "Registry key extension" sub-section below). The CP retry namespace declarations at C-CP-03 §3.5 are unchanged; the keying scheme is implementation discretion per `Spec_Harness_Runtime_v1.md` §3 — this contract documents the runtime-side extension.

**Specification content.**

The runtime contributes one production wrapper class — `RetryBreakerFallbackDispatcher` — that owns the per-step retry+breaker+fallback orchestration loop around the inner C-RT-15 `RuntimeLLMDispatcher.dispatch` invocation. The wrapper satisfies the same `StepDispatcher` Protocol that C-RT-15 satisfies (declared at `harness-cp/src/harness_cp/workflow_driver.py:151`); from the driver's perspective the wrapper IS the dispatcher.

Per-step invocation discipline (the body of `RetryBreakerFallbackDispatcher.dispatch(binding, step)`):

1. **Lookup `RetryPolicy` from the registry under the reserved `"llm_dispatch"` key** (see Registry key extension below). Resolves to `RetryPolicy(max_attempts, backoff, jitter)` per `harness_cp.routing_manifest_residence.RetryPolicy`.
2. **Construct the candidate iterator from `ctx.fallback_chain`** for the step's `binding.model_binding` family. The chain is operator-supplied at workflow-binding time per C-CP-04 §4. The first candidate is `binding.model_binding` itself; subsequent candidates are cross-family-fallback per the chain.
3. **Start the outer span** via `with tracer.start_as_current_span("harness.runtime.retry_breaker_fallback")` (synchronous CM per the v1.3 §14.5 phrasing correction). The outer span covers the full retry+fallback envelope and is the carrier for the eventual `fallback.exhausted` event on exhaustion.
4. **Per-candidate loop:** for each candidate in the chain iterator:
   - **Breaker pre-check.** `breaker = ctx.retry_breaker.get_breaker(candidate.provider, candidate.model)`. If `breaker.should_attempt() is False` (state is OPEN and cooldown unexpired), advance to next candidate via `advance_or_raise(chain, candidate)` — emit `retry.skipped` event on outer span; do NOT consume retry budget; loop continues.
   - **Per-attempt loop** (bounded by `RetryPolicy.max_attempts` for this candidate):
     - **Start inner span** via `with tracer.start_as_current_span("harness.runtime.retry_attempt")`. Inner span carries the canonical C-CP-03 §3.5 `retry.*` 6-attribute namespace per CP spec v1.3 (NOT renamed at the runtime spec; canonical attribute set imported from the landed producer carrier at `harness_cp.retry_fallback_namespace.RETRY_ATTEMPT_CHILD_SPAN_SCHEMA`): `retry.attempt_number` (integer; 1-indexed), `retry.original_span_id` (string; 16-hex W3C trace-context format; carries the outer wrapper span's `span_id` as the original-operation reference), `retry.delay_ms` (integer; jittered delay per full-jitter backoff), `retry.cause_attribution` (string; open-set enum from C5 cause_attribution catalog per C-CP-21), `retry.fail_class` (5-class enum: `transient-retry` / `Reflexion-recoverable` / `HITL-recoverable` / `permanent-fail-exit` / `terminal-fail-exit`; from `harness_cp.validator_fail_taxonomy.ValidatorFailClass`), and `engine.replay_disposition` (composition with engine namespace per D1 v1.2 §1.1.1; derived from `binding.engine_class` via `harness_cp.engine_namespace.REPLAY_DISPOSITION_MAPPING`).
     - **Dispatch to inner.** `result = await self.inner.dispatch(rebound(binding, candidate), step)` — `rebound(...)` constructs a new `StepEffectiveBinding` whose `model_binding` field is overridden to `candidate` for this attempt. All other binding fields (sandbox_tier_floor, etc.) carry forward unchanged.
     - **On success:** call `breaker.record_success()` (registry handles `harness.breaker.*` transition emission if state changes); annotate inner span with `retry.terminal = "success"`; return `result` (outer span closes via CM; breaker + retry state captured in span attrs).
     - **On `LLMDispatchProviderUnreachableError` / `LLMDispatchPayloadShapeError`:** fail-fast for this candidate (these are not retry-eligible per D2). Annotate inner span with `retry.terminal = "fail-fast"` + `retry.cause_class = "{class_name}"`. Call `breaker.record_failure()` (registry emits transition if breaker trips). Break out of per-attempt loop; advance to next candidate via `advance_or_raise`.
     - **On provider SDK transient (network / rate-limit / 5xx) per C-CP-21 §21.2 transient staircase:** advance the staircase via `ctx.retry_breaker.advance_staircase(policy, attempt_count, validator_fail_class)`. If staircase result is `RETRY_WITH_BACKOFF`: sleep `compute_full_jitter_delay_seconds(policy, attempt_count)`; annotate inner span with `retry.terminal = "retry"` + `retry.backoff_ms`; continue per-attempt loop. If staircase result escalates beyond `RETRY_WITH_BACKOFF` (e.g., `CROSS_FAMILY_FALLBACK` / `LOCAL_TERMINAL` / `HITL_ESCALATION`): annotate inner span with `retry.terminal = "escalate"`; call `breaker.record_failure()`; break out of per-attempt loop; advance to next candidate via `advance_or_raise`.
     - **On `RetryPolicy.max_attempts` exhaustion:** annotate inner span with `retry.terminal = "max-attempts"`; call `breaker.record_failure()`; break out of per-attempt loop; advance to next candidate via `advance_or_raise`.
5. **On `FallbackChainExhaustedError`** (raised by `advance_or_raise` when chain has no remaining candidate): emit `fallback.exhausted` span event on the outer span with attributes per C-CP-04 §4.2 (`fallback.chain_length`, `fallback.last_failure_class`, `fallback.exhaustion_cause`); raise `RetryBreakerFallbackExhaustedError` (typed runtime error) which maps to the new `RT-FAIL-FALLBACK-EXHAUSTED` fail class.

**Registry key extension (Q2=c clause).** The `harness_runtime.lifecycle.retry_breaker.RuntimeRetryBreaker.get_policy(name)` method accepts the reserved string `"llm_dispatch"` in addition to per-tool names. The runtime composer reserves this key for LLM-dispatch retry policy lookup; tools may not declare a tool named `"llm_dispatch"` (enforced at manifest-validation time via a typed `ReservedToolNameError`). The reserved key's `RetryPolicy` is operator-supplied at `RuntimeConfig.routing_manifest.retry_policies["llm_dispatch"]`; if absent at runtime, the registry's `materialize_retry_breaker_stage` materializer binds a default `RetryPolicy(max_attempts=3, backoff="full_jitter", base_delay_seconds=0.2, delay_cap_seconds=10.0)` for the reserved key. Per `Spec_Harness_Runtime_v1.md` §3 ("Deferred to implementation discretion") + C-CP-03 §3.5 (CP namespace declarations are key-agnostic), this extension does NOT require a CP spec amendment — the keying scheme is implementation discretion. The CP-side observability contract is unchanged: `retry.*` spans emit per the §3.5 attribute set regardless of which registry key surfaced the policy.

**Composer module residence.** `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py` (new file at v1.4). Module exposes one production class — `RetryBreakerFallbackDispatcher` — that satisfies `StepDispatcher` via duck-typing. Construction site: bound at bootstrap stage 5 (LOOP_INIT) per the U-RT-52 stage 5 site, wrapping the existing `RuntimeLLMDispatcher` constructor invocation. `ctx.llm_dispatcher` post-condition shape becomes the wrapper, not the bare dispatcher.

**Integration with C-RT-04 (HarnessContext).** No new field. The wrapper consumes `ctx.retry_breaker` (existing, U-RT-24) + `ctx.fallback_chain` (existing, stage 3b) + `ctx.tracer_provider` (existing, C-RT-06) + an internally-constructed `RuntimeLLMDispatcher` instance (private). `ctx.llm_dispatcher` retains the same Protocol shape; runtime users invoke it unchanged.

**Integration with C-RT-15 (inner LLM dispatch composer).** No protocol change to `RuntimeLLMDispatcher.dispatch` at v1.4. The wrapper invokes the inner dispatcher exactly once per attempt with a rebound `binding` (candidate's provider+model overrides). The inner dispatcher's `retry.*`-naive exception propagation per v1.3 §14.5 invariants ("composer propagates the exception unmodified") is the boundary where the wrapper takes over.

**Integration with C-RT-06 (TracerProvider).** Two nested spans per composer invocation: outer (`harness.runtime.retry_breaker_fallback`, covers full envelope) + inner per-attempt (`harness.runtime.retry_attempt`, carries `retry.*` namespace). The inner C-RT-15 `gen_ai.*` span nests inside the inner retry_attempt span — three levels of nesting (outer composer → per-attempt retry → per-call gen_ai). This is the canonical OTel pattern for retry-wrapper instrumentation.

**Invariants.**

- Wrapper is async (matches C-RT-08 async-only `run()` posture + C-RT-15 async dispatch).
- Wrapper satisfies `isinstance(wrapper, StepDispatcher)` via the same `@runtime_checkable` introspection.
- Outer span emitted exactly once per composer invocation; inner per-attempt span emitted exactly once per attempt.
- `retry.*` namespace attributes per the CP-canonical 6-attribute set (per C-CP-03 §3.5 v1.3; carrier at `harness_cp.retry_fallback_namespace.RETRY_ATTEMPT_CHILD_SPAN_SCHEMA`) set on the inner per-attempt span only; outer span carries `fallback.*` attributes on exhaustion.
- `harness.breaker.*` namespace emission is delegated to `RuntimeRetryBreaker.emit_breaker_transition_event` (no wrapper-side span code); per C-OD-07 §7.1 7-attribute schema.
- Wrapper does NOT swallow exceptions: all paths terminate in either successful return OR raised typed fail-class.
- Reserved registry key `"llm_dispatch"` is the ONLY runtime-emitted retry-policy lookup; per-tool keys are reserved for tool-invocation runtime composer (separate future arc per the v2 ledger §9.2.2 tool-invocation gap).

**Failure-mode taxonomy.** Per C-RT-14, with one new fail class added at v1.4:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-FALLBACK-EXHAUSTED` (permanent, new at v1.4) | Fallback chain exhausts after per-candidate retry exhaustion (every candidate either fails-fast or hits `max_attempts`) | Wrapper emits `fallback.exhausted` event on outer span; raises typed `RetryBreakerFallbackExhaustedError`; driver `try/except` maps to `step-failure: RT-FAIL-FALLBACK-EXHAUSTED: ...` per C-CP-25 §25.3.3.4 |

The C-RT-15 fail classes (`RT-FAIL-PROVIDER-UNREACHABLE`, `RT-FAIL-TRANSIENT`, `RT-FAIL-PROVIDER-AUTH`, `RT-FAIL-PAYLOAD-SHAPE`) propagate through the wrapper unchanged for `PROVIDER-UNREACHABLE` + `PAYLOAD-SHAPE` (fail-fast per D2; wrapper advances to next candidate but if chain length is 1, propagates verbatim). `TRANSIENT` is consumed by the staircase loop (composer retries internally); `PROVIDER-AUTH` is fail-fast.

**X-AL-2 retirement implications (v1.4 → retirement event prerequisites).**

The C-RT-16 contract specifies the composition seam whose absence was the substitution-site B-condition blocker for H_T-CP-3 + H_T-CP-4 + H_T-CP-5 per `.harness/phase-7d-retirement-ledger-v2.md` §5 + `.harness/phase-7d-retirement-events-batch-2.md` §3. At U-RT-58 landing event:

- **H_T-CP-3 RETIRE-READY.** `retry.*` 6-attribute namespace emitted at the inner per-attempt span per §14.6 step 4. Condition A: U-CP-03 + U-RT-58 landed. Condition B: `retry.*` namespace no longer requires `CLAUDE.md`-prose substitution; runtime emits at production execution path.
- **H_T-CP-4 RETIRE-READY.** `fallback.exhausted` emitted on chain exhaustion per §14.6 step 5. Condition A: U-CP-04 + U-RT-58 landed. Condition B: fallback chain orchestration no longer requires operator-driven `Bash(retry-then-next)` shell-out; runtime owns the loop.
- **H_T-CP-5 PARTIAL → RETIRE-READY.** `routing.*` attribute namespace (per C-CP-05 §5.1 inheritance composition from `llm.inference` parent span) inherits naturally through the inner C-RT-15 `gen_ai.*` span; the C-RT-16 retry-wrapper does not add new `routing.*` emission but does not break the inheritance. Per batch-2 §3 ("Follow-on CP-3 / CP-4 unit will full-retire CP-5 when retry/breaker wrappers land"), the wrapper landing closes the PARTIAL → RETIRED transition.

**Cross-axis cascade closures at U-RT-58 landing.** Per Meta-Architecture §6.3.2 (F-CP-01 Stage 3b inversion ordering): H_T-OD-2 RETIRED (batch 2) + H_T-CP-3 RETIRED (this contract) jointly enable H_T-CXA-5 RETIRE-READY evaluation. The `harness.breaker.*` namespace producer-emission flow becomes fully runtime-grounded once the wrapper invokes `breaker.record_failure()` at production execution path; the existing `od_cp_wiring.py` Pattern-P1 verification (already firing at bootstrap per `od_cp_wiring.py:187-223`) plus runtime invocation closes both endpoints of the inversion seam.

**Deferred to implementation discretion.**

- Exact wrapper class name (suggest `RetryBreakerFallbackDispatcher` per the §14.6 narrative recommendation).
- Per-candidate breaker key scheme: suggest `(provider, model)` 2-tuple (matches `RuntimeRetryBreaker.get_breaker(provider, model)` library API).
- Whether `RetryPolicy.max_attempts` defaults are operator-overridable per-step (via `binding.retry_policy_override`) or per-runtime (via `RuntimeConfig.routing_manifest.retry_policies["llm_dispatch"]`) — MVP suggests per-runtime only; per-step override is a follow-on if operator needs surface.
- Span name conventions for outer + inner: suggest `harness.runtime.retry_breaker_fallback` (outer) + `harness.runtime.retry_attempt` (inner); align with §14.5's `gen_ai.{provider}.{model_or_method}` for the innermost C-RT-15 span.
- Test mock strategy: suggest a `MockRuntimeLLMDispatcher` fixture that records the sequence of `(binding, step)` calls + returns canned success/failure per call; verify wrapper's iteration + retry + breaker behavior against the recorded sequence. Pytest-asyncio for async surface.
- Whether the wrapper emits a separate `retry.skipped` span event on breaker-open candidate skip, or just an outer-span attribute — defer to OTel telemetry-volume discretion at implementation; spec-MUST is just that the skip is observable.

---

## §14.7 C-RT-17 — Sub-agent dispatch composer (new at v1.6; in-CLI spec growth)

> **✅ Class 1 fork RESOLVED at v1.6 Path A.** v1.6 spec authoring pre-survey at U-RT-59 implementation entry surfaced a structural gap: the `StepDispatcher` Protocol per C-CP-25 §25.3.3.4 (`dispatch(binding: StepEffectiveBinding, step: WorkflowStep) -> Mapping[str, Any]`) lacked the per-step parent context surface that C-CP-12 gate-level descent + C-CP-13 §13.5 audit-trail-link composition require. Fork record `.harness/class_1_tension_c_rt_17_step_dispatcher_parent_context_gap.md` documents the 4-path candidate set; operator ratified Path A 2026-05-20. Resolution arc landed Stage 1 plumbing in the same arc: `StepDispatcher` Protocol extended with new keyword-only `step_context: StepExecutionContext` parameter at `Spec_Control_Plane_v1_6.md` §25.2.1; CP-side type addition at `harness-cp/src/harness_cp/workflow_driver_types.py`; driver loop composes per step + passes; U-RT-58 wrapper + C-RT-15 inner accept via Protocol conformance. The §14.7 narrative below cites `step_context.X` per the resolved Protocol surface.

**Contract surface.** New runtime-internal type `StepKindDispatcherRegistry` (frozen mapping `{StepKind → StepDispatcher}`; bound at bootstrap stage 5 as `ctx.step_dispatchers`) + new Protocol-satisfying composer `RuntimeSubAgentDispatcher` + driver routing-layer refactor at `harness-cp/src/harness_cp/workflow_driver.py` (dispatch via `ctx.step_dispatchers.lookup(step.kind)` instead of the single bound `step_dispatcher` parameter) + integration obligations with `ctx.handoff_registry` (U-RT-26), `ctx.topology_dispatcher` (U-RT-40), `ctx.tracer_provider` (C-RT-06), C-CP-13 §13.1 (HandoffContext schema), C-CP-13 §13.5 (audit-trail-link composition), C-CP-14 §14.1 (multi-agent span hierarchy — narrow-scope subset for single-sub-agent), C-CP-14 §14.2 (`subagent.*` + `topology.*` namespaces), and the existing `compose_dispatch_audit` site at `harness_runtime.lifecycle.handoff.RuntimeHandoffRegistry.compose_dispatch_audit`.

**PRD enablement.** Operationalizes the sub-agent dispatch surface at runtime. R-CP-08 (multi-agent topology — sub-agent dispatch payload + observability surface, single-sub-agent slice). R-CP-09 (sub-agent privilege inheritance — HandoffContext audit composition at production callsite). R-OD-02 (audit-ledger compliance posture — sub-agent dispatch audit entries produced at production execution path, not synthesized post-hoc).

**ADR commitment(s) honored.** ADR-D4 v1.1 §1.7 (HandoffContext serialization contract — runtime production callsite for the CP-declared schema); ADR-D4 v1.1 §1.9 (multi-agent span hierarchy — runtime production emission site for the narrow single-sub-agent slice); ADD §3.1.2 Synthesis (TopologyPattern enum + admissibility predicate operationalized at runtime).

**Fork-resolution provenance.** None (in-CLI spec growth per workspace `CLAUDE.md` §4.3; no Class 1 / Class 2 / Class 3 fork filed). Operator architectural ratifications captured at the v1.5 → v1.6 change-note rather than a fork record.

**Specification content.**

### §14.7.1 Architectural surfaces introduced

The runtime contributes two production surfaces at v1.6:

1. **`StepKindDispatcherRegistry`** (new frozen dataclass at `harness-runtime/src/harness_runtime/lifecycle/step_dispatchers.py`):
   - Frozen mapping `dispatchers: Mapping[StepKind, StepDispatcher]`.
   - Public method `lookup(step_kind: StepKind) -> StepDispatcher` (raises `StepKindDispatcherNotBoundError` if no dispatcher bound for the kind).
   - Bound at bootstrap stage 5 (LOOP_INIT) alongside `ctx.llm_dispatcher`. v1.6 binds two entries: `StepKind.INFERENCE_STEP → ctx.llm_dispatcher` (the C-RT-16 wrapper) + `StepKind.SUB_AGENT_DISPATCH → ctx.sub_agent_dispatcher` (the new composer).
   - Other 3 step_kinds (`DECLARATIVE_STEP`, `TOOL_STEP`, `HITL_STEP`) are NOT bound at v1.6; the lookup raises the typed error if a workflow declares an unbound step_kind. Follow-on composer arcs (tool-invocation / HITL / validator) bind the remaining entries.

2. **`RuntimeSubAgentDispatcher`** (new class at `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py`):
   - Satisfies the `StepDispatcher` Protocol (declared at `harness-cp/src/harness_cp/workflow_driver.py:151`).
   - Async `dispatch(binding, step) -> StepOutput`.
   - Construction site: bootstrap stage 5; consumes `ctx.handoff_registry`, `ctx.topology_dispatcher`, `ctx.tracer_provider`, and an injected "child workflow runner" callable (see §14.7.4).

### §14.7.2 Per-step invocation discipline (composer body)

The body of `RuntimeSubAgentDispatcher.dispatch(binding, step)`:

1. **Validate step payload shape.** `step.step_payload` is opaque to the driver per C-CP-25 §25.3.3.4 but typed at the dispatcher: v1.6 pins the convention that `SUB_AGENT_DISPATCH` step payloads are a `harness_runtime.lifecycle.sub_agent_dispatch.SubAgentDispatchPayload` mapping (4-field Pydantic v2 model — `child_workflow_id: WorkflowID`, `child_manifest_entry: WorkflowManifestEntry`, `child_steps: Sequence[WorkflowStep]`, `brief: SubAgentBrief`). Composer pydantic-validates `step.step_payload → SubAgentDispatchPayload`; mis-shaped payloads surface as a typed `SubAgentDispatchPayloadShapeError` mapping to `RT-FAIL-PAYLOAD-SHAPE` (existing fail class from §14.5).
2. **Compose HandoffContext per C-CP-13 §13.1.** Build the 7-field `HandoffContext` from step inputs + parent context (sourced from `step_context: StepExecutionContext` per `Spec_Control_Plane_v1_6.md` §25.2.1 Path A resolution): `proposed_action` from `payload.brief.objective`; `agent_confidence` `None` at v1.6 MVP (no operator-surfaced confidence at v1.6); `failed_attempts` empty list at v1.6 MVP (no prior sub-agent failure tracking); `alternatives_considered` empty list at v1.6 MVP; `state_summary` composed via C-CP-13 §13.4 (MVP shape: `StateSummary(relevant_entries=[parent_entry_ref], summary_text="", summary_hash=sha256(b""), idempotency_key=step_context.parent_idempotency_key)`); `audit_trail_link` per C-CP-13 §13.5 composed from parent ledger entry (`LedgerEntryRef(action_id=step_context.parent_action_id, entry_hash=step_context.parent_entry_hash, actor=step_context.parent_actor)`); `retry_history` empty at v1.6 MVP.
3. **Compute gate-level descent.** `descent = ctx.handoff_registry.dispatch(parent_action_id=step_context.parent_action_id, parent_gate_level=step_context.parent_gate_level, parent_sandbox_tier=step_context.parent_sandbox_tier, sub_agent_brief=payload.brief, operator_override=None)` — returns a `SubAgentGateLevelDescent` per C-CP-12.
4. **Verify topology admissibility.** `topology = ctx.topology_dispatcher.dispatch(payload.child_manifest_entry)` (returns `TopologyPattern` enum value per C-CP-10 §10.1). `admissible = is_admissible(topology, payload.child_manifest_entry.workload_class)` (per C-CP-10 §10.3). If not admissible, raise typed `SubAgentDispatchTopologyInadmissibleError` mapping to a new fail class (see §14.7 failure-mode taxonomy below).
5. **Start `subagent.span`.** `with tracer.start_as_current_span("subagent.span") as span:` (synchronous CM per the v1.3 §14.5 phrasing pattern). Set `subagent.*` attributes per C-CP-14 §14.2 at span open: `subagent.span.id` (16-hex span_id of this span), `subagent.parent_span_id` (16-hex parent span_id from current context), `subagent.tokens_in` / `subagent.tokens_out` / `subagent.cached_tokens_in` (set at span close from child's terminal cost rollup; v1.6 MVP sets all three to `0` if child does not surface them). Also set narrow-subset `topology.*` attributes at span open: `topology.pattern` (string-value of `topology` per §10.1 enum), `topology.workload_class` (string-value of `payload.child_manifest_entry.workload_class` per Persona §3.1 4-class set). Fan-out-specific `topology.*` attributes (`fan_out_cap`, `cascade_policy`, `results_collected`, `results_failed`, `cascade_applied`, `synthesis_token_budget`, `cascade_decision_audit_ledger_id`, `concurrent_token_budget_at_dispatch`) are NOT set at v1.6 (out of scope per change-note "Scope: single-sub-agent within linear parent").
6. **Invoke the child sub-workflow.** `child_result = await self.child_workflow_runner(workflow_id=payload.child_workflow_id, manifest_entry=payload.child_manifest_entry, steps=payload.child_steps, handoff_context=handoff_context, descent=descent)` — invokes the in-process recursive runner per §14.7.4. The runner returns a `RunResult` per C-RT-09. The runner is responsible for running the child as a full sub-workflow (its own bootstrap-context-share, step-iteration, span hierarchy nested inside the current `subagent.span`).
7. **Map child result to subagent span result_status.** If `child_result.status == SUCCESS`: set `subagent.result_status = "completed"`; set `subagent.request_blocked_by_budget = False`. If `child_result.status == DRAINED`: set `subagent.result_status = "completed"` + `subagent.request_blocked_by_budget = False` (drain is operator-initiated, not failure). If `child_result.status == FAILED`: set `subagent.result_status = "failed"`; do NOT raise (failure surfaces via step output + audit entry; outer composer / driver decides whether to halt). v1.6 MVP does NOT emit `"cascade-cancelled"` (that value is only produced under fan-out cascade semantics out of scope at v1.6).
8. **Compose + write audit entry — v1.7 4-substep sequence (Path D + B-revised-a resolution).** The v1.6 prose's direct `ctx.audit_ledger_writer.append(...)` emission was incompatible with the CP-shape `CPAuditLedgerEntry` (per `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md`); v1.7 specifies the now-spec-anchored 4-substep sequence:

    **8a.** **Compose CP audit entry.** `cp_entry = ctx.handoff_registry.compose_dispatch_audit(parent_action_id=step_context.parent_action_id, descent=descent, brief_hash=ctx.handoff_registry.dispatch_response_hash(payload.brief))` — 3 parameters, verified against `harness_runtime.lifecycle.handoff.RuntimeHandoffRegistry.compose_dispatch_audit` at HEAD. Returns `CPAuditLedgerEntry` per C-CP-13 §13.5 + C-CP-16 §16.2 (8-field shape with response-conditional optional hash fields). The composer is a pure composition of `harness_cp.sub_agent_gate_level_descent.emit_sub_agent_dispatch_audit`. The CP entry carries placeholder `timestamp` + `prior_event_hash` populated downstream by the converter / writer chain. The CP entry shape does NOT carry `child_result_status` (that value lives at the `subagent.result_status` span attribute per §14.7.2 step 7 + C-CP-14 §14.2); audit entries are dispatch-fact records keyed by `(parent_action_id, descent, brief_hash)` per C-CP-12 §12.5.

    **8b.** **Write F2 state-ledger entry for the dispatch action (Q2(a) ratification).** Per `Spec_Control_Plane_v1_7.md` §13.5.1 entry_core source semantic + OD spec v1.5 C-OD-24.6: the dispatch composer MUST write an F2 state-ledger entry recording the dispatch action via `ctx.state_ledger_writer.append(payload, write_key) → WriteResult` (existing IS C-IS-10 §10.5 + C-IS-11 §11.1 contract). Capture the resulting `StateLedgerEntryRef` (the IS-canonical reference to the persisted entry; per OD spec v1.5 C-OD-24.4 opaque marker shape). MVP shape: `payload = EntryPayload(action_id=Identifier(f"dispatch:{step_context.parent_action_id}:{descent.child_index}"), idempotency_key=Identifier(f"dispatch:{step_context.parent_action_id}:{descent.child_index}"), actor=ctx.runtime_actor, timestamp=time_source())`; `write_key = WriteKey(thread_id=Identifier(f"dispatch:{step_context.parent_action_id}"), step_id=action_id, idempotency_key=action_id)`. The F2 entry's `entry_hash` (returned in `WriteResult` or read post-append via `ledger_writer.last_appended_entry_hash` API per `Spec_Control_Plane_v1_6.md` §25.2.1 v1.6 step_context note) is the value bound to `entry_core: StateLedgerEntryRef` at step 8c.

    **8c.** **Convert CP→OD via cp_audit_to_od_audit (CP spec v1.7 §13.5.1).** `od_entry = cp_audit_to_od_audit(cp_entry, key_id=ctx.audit_signing_key_id, algo=ctx.audit_signing_algorithm, entry_core=StateLedgerEntryRef(<step-8b entry_hash>))` — invokes the converter per `Spec_Control_Plane_v1_7.md` §13.5.1 full field-projection table. Returns OD `AuditLedgerEntry` per OD spec v1.5 C-OD-24.2 (3 fields: `payload` + `signature_attrs` + `entry_hash`). Signature attributes produced via OD `sign_audit_entry(payload, key_id, algo)` per ADR-D5 v1.4 §1.4.1 + OD spec v1.5 C-OD-24.2. `audit.cp.*` sub-namespace fields populated per OD spec v1.5 C-OD-24.6. `entry_hash` computed per OD spec v1.5 C-OD-24.5 canonical helper. Per CP spec v1.7 §13.5.1 NOTE 3 cryptographic-payload-mismatch foreclosure: converter signs the OD `AuditPayload` directly; no CP-side signature is re-projected.

    **8d.** **Append OD audit entry to ctx.audit_writer (Class 3 drift item 1 RESOLVED).** `write_result = ctx.audit_writer.append(tenant_id=step_context.tenant_id, audit_entry=od_entry)` — real 2-param signature per `harness_runtime.lifecycle.audit_writer.RuntimeAuditLedgerWriter.append` per C-RT-04 + OD spec v1.5 C-OD-24 + ADR-D5 v1.4 §1.4 (canonical storage form = JSONL via IS state-ledger composition). `step_context.tenant_id` is `None` at v1.7 MVP per `Spec_Control_Plane_v1_6.md` §25.2.1 (multi-tenancy not committed at v1.7 stack). Returns `WriteResult` per IS C-IS-11 §11.1 (APPENDED on fresh entry; IDEMPOTENT_NOOP on replay). The v1.6 prose's field name `ctx.audit_ledger_writer` (drifted from C-RT-04 canonical `ctx.audit_writer` per `.harness/class_3_tension_u_rt_59_spec_prose_drift.md` item 1) is corrected at this step 8d — drift item 1 RESOLVED at v1.7.

    **Failure semantics across 8a–8d.** Any raised typed error at substep 8b (F2-write failure: `LedgerWriteError`), substep 8c (`ValueError` from `sign_audit_entry` on empty `key_id`; converter signature contract violation per CP spec v1.7 §13.5.1), or substep 8d (`LedgerWriteError` or backpressure-class WriteResult): annotate the `subagent.span` with `subagent.result_status = "failed"`; raise mapping to `RT-FAIL-SUB-AGENT-AUDIT-COMPOSE` (new fail class — added at v1.7 §14 failure-mode taxonomy follow-on patch; defer to next §14 amendment). The audit-trail-fact record is preserved even when downstream substeps fail (step 8a's `cp_entry` is the dispatch fact; step 8b's F2 entry is the action record; failure at 8c/8d preserves the dispatch fact + action record without the cryptographically-signed audit anchor).
9. **Return step output.** Construct the step output from `child_result.final_state` (or `child_result.partial_state` if DRAINED). v1.6 MVP shape: step output is the child's `final_state` mapping verbatim (the parent workflow's step body consumes this).
10. **On any raised typed error** (`SubAgentDispatchPayloadShapeError`, `SubAgentDispatchTopologyInadmissibleError`, child-runner unhandled `RuntimeError`): annotate the `subagent.span` with `subagent.result_status = "failed"`; compose + emit a partial audit entry with `child_result_status="failed"`; re-raise. The `subagent.span` closes via CM; outer driver's `try/except` per C-CP-25 §25.3.3.4 maps to the typed fail class.

### §14.7.3 HandoffContext payload composition discipline

Per C-CP-13 §13.1, the `HandoffContext` is the 7-field payload serialized at sub-agent dispatch (across-turn boundary; T-perm-2 adjacency per ADR-D4 v1.1 §1.7). The runtime composer's role per §14.7.2 step 2 is to **compose this payload from parent context** — the schema lives at `harness_cp.handoff_context.HandoffContext` (existing); the composer constructs an instance.

v1.6 MVP composition (per §14.7.2 step 2) makes the following bounded reductions for surfaces not yet operationalized:

| Field | v1.6 MVP composition | Deferred (post-v1.6) |
|---|---|---|
| `proposed_action` | `ProposedAction(text=payload.brief.objective)` | Richer ProposedAction shape per future C-CP-NN |
| `agent_confidence` | `None` | Operator-supplied at workflow-binding time; or computed from prior `RetryHistory` |
| `failed_attempts` | empty list | Cascade re-attempt tracking (gated on cascade semantics; fan-out arc) |
| `alternatives_considered` | empty list | Lead-agent deliberation context capture |
| `state_summary.relevant_entries` | `[parent_entry_ref]` | Multi-entry filtering by sub-agent scope per C-CP-13 §13.4 |
| `state_summary.summary_text` | empty string | Summarization model invocation per C-CP-21 §21.4 |
| `state_summary.summary_hash` | `sha256(b"")` | Hash of non-empty summary |
| `audit_trail_link` | from `step_context` (`parent_action_id`, `parent_entry_hash`, `parent_actor`) per `Spec_Control_Plane_v1_6.md` §25.2.1 Path A | — (v1.6 final shape) |
| `retry_history` | empty `RetryHistory` | RetryHistory cardinality cap per HandoffContext payload boundary discretion |

The bounded reductions are documented at this contract; they are NOT silent X-AL-3 design extensions because they instantiate existing C-CP-13 schema fields with empty / minimal values. Operators authoring a workflow with `SUB_AGENT_DISPATCH` steps may surface richer values via the step payload directly (v1.6 MVP: `SubAgentDispatchPayload` does not yet carry per-field overrides; this is a v1.7+ extension surface).

### §14.7.4 In-process recursive sub-workflow invocation primitive

The "child workflow runner" callable injected at `RuntimeSubAgentDispatcher` construction is a new runtime-internal type. v1.6 specifies its Protocol surface:

```python
class ChildWorkflowRunner(Protocol):
    async def __call__(
        self,
        *,
        workflow_id: WorkflowID,
        manifest_entry: WorkflowManifestEntry,
        steps: Sequence[WorkflowStep],
        handoff_context: HandoffContext,
        descent: SubAgentGateLevelDescent,
    ) -> RunResult: ...
```

The v1.6 MVP implementation invokes `execute_workflow()` recursively (per C-RT-08 `run()` discipline) within the parent's `HarnessContext`. Specifically:

- The child shares the parent's `HarnessContext` for substrate access (state ledger, tracer provider, audit ledger writer, retry/breaker registry, providers, sandbox tier dispatcher). This is the simplest in-process composition; full child-context isolation is a v1.7+ scope question.
- The child's `binding` is constructed by descending from the parent's binding per `descent`: `child_binding.gate_level = descent.child_gate_level`; `child_binding.sandbox_tier = descent.child_sandbox_tier`; `child_binding.action_id = compose_child_action_id(step_context.parent_action_id, child_workflow_id)`; `child_binding.actor = descent.child_actor`; other fields carried forward per the workload class binding rules at C-CP-13 §13.3 (brief-authoring inheritance).
- The child's spans nest inside the current `subagent.span` via the OTel context propagation (current span at runner entry is `subagent.span`; child's `workflow.start` becomes its child).
- The child's audit ledger entries write to the same ledger via the same `ctx.audit_ledger_writer` (no separate ledger primitive at v1.6).
- The child's `RunResult` is returned verbatim to the composer.

**Composer module residence.** Runner implementation at `harness-runtime/src/harness_runtime/lifecycle/child_workflow_runner.py` (new file at v1.6). Module exposes one production function — `compose_child_workflow_runner(ctx) -> ChildWorkflowRunner` — that closes over the `HarnessContext` and returns the callable. Bootstrap stage 5 constructs the runner + injects it into `RuntimeSubAgentDispatcher` construction.

### §14.7.5 Span emission per C-CP-14 §14.1 (narrow-scope subset)

v1.6 emits a single-level `subagent.span` per dispatch (NOT the full fan-out hierarchy with `topology.fanout.opened` / `topology.fanout.closed` envelopes — those are only meaningful when there are siblings, which requires parent topology beyond `SINGLE_THREADED_LINEAR`). The narrow-scope emission:

```
parent step (workflow_driver step.boundary)
└── subagent.span                          (attrs: subagent.span.id, subagent.parent_span_id,
    │                                              topology.pattern, topology.workload_class)
    └── (child sub-workflow spans)         (workflow.start → step.boundary[] → workflow.end
                                            per C-RT-08 + C-CP-25; nested inside subagent.span
                                            via OTel context propagation)
```

The narrow-scope shape preserves the C-CP-14 §14.1 invariant that child sub-agent activity nests inside a `subagent.span`. The full fan-out envelope (`topology.fanout.opened` → siblings → `topology.fanout.closed`) is a strict superset of this shape; the post-v1.6 fan-out arc wraps the existing `subagent.span` emission inside the fan-out envelope without rewriting the per-sibling emission.

**Producer-side attribute carrier reference.** v1.6 composer imports the canonical `subagent.*` attribute name set from `harness_cp.handoff_context` (existing; per C-CP-14 §14.2 v1.3 schema). Hand-coded attribute strings are NOT permitted; the carrier import ties retirement criterion B verification ("references the canonical attribute carrier") directly to the canonical producer surface (analog of how C-RT-16 imports `RETRY_ATTEMPT_CHILD_SPAN_SCHEMA`).

### §14.7.6 Audit-entry composition per C-CP-13 §13.5

v1.6 composer calls `ctx.handoff_registry.compose_dispatch_audit(parent_action_id, descent, brief_hash)` per §14.7.2 step 8 (3-param signature verified at v1.6 against `harness_runtime.lifecycle.handoff.RuntimeHandoffRegistry.compose_dispatch_audit`; landed pre-v1.6 per U-RT-26). The composer returns a `CPAuditLedgerEntry` with placeholder `timestamp` + `prior_event_hash` (populated at write-time by the audit writer per its U-RT-32 contract). The composer writes the entry via `ctx.audit_ledger_writer.append(tenant_id, audit_entry) -> WriteResult` (2-param signature; verified at v1.6 against `harness_runtime.lifecycle.audit_writer.RuntimeAuditLedgerWriter.append`).

The audit-ledger entry **does NOT carry `child_result_status`** — that value lives only as a `subagent.result_status` attribute on the `subagent.span` (per C-CP-14 §14.2). The audit entry is the **dispatch fact** (parent dispatched a sub-agent; the brief hash + descent + parent action identifies the dispatch), not the **result fact** (sub-agent completed / failed / cancelled). Result-fact observability flows via the span hierarchy + the child sub-workflow's own audit-ledger entries (which compose at the child's terminal `workflow.end` per C-RT-08), NOT via the parent's sub-agent-dispatch audit entry.

### §14.7.7 Driver routing-layer refactor

The v1.5 driver at `harness-cp/src/harness_cp/workflow_driver.py:240` takes a `step_dispatcher: StepDispatcher` parameter and calls `step_dispatcher.dispatch(binding, step)` at line 379. v1.6 amends this:

- Parameter changes from `step_dispatcher: StepDispatcher` to `step_dispatchers: StepKindDispatcherRegistry`.
- Call site at line 379 changes from `step_dispatcher.dispatch(binding, step)` to `step_dispatchers.lookup(step.kind).dispatch(binding, step)`.
- Bootstrap stage 5 constructs the registry: `step_dispatchers = StepKindDispatcherRegistry(dispatchers={StepKind.INFERENCE_STEP: ctx.llm_dispatcher, StepKind.SUB_AGENT_DISPATCH: ctx.sub_agent_dispatcher})` and assigns to `ctx.step_dispatchers`. The driver is invoked with `ctx.step_dispatchers` instead of `ctx.llm_dispatcher`.
- The `ctx.llm_dispatcher` binding is preserved (the C-RT-16 wrapper is still bound; it just becomes a value in the registry rather than the only dispatcher). Backwards-compat: any test or composition that invokes `ctx.llm_dispatcher` directly continues to work.
- The driver is **still step-kind-agnostic in the C-CP-25 §25.3.3.4 sense** — it does not introspect `step.step_payload`; it only routes on `step.kind` (which is the documented enum field, not opaque body content). This is consistent with the "step body opaque to driver" invariant.

**Integration with C-RT-04 (HarnessContext).** Two new fields at v1.6: `step_dispatchers: StepKindDispatcherRegistry` + `sub_agent_dispatcher: StepDispatcher`. Both bound at bootstrap stage 5. `ctx.llm_dispatcher` retained (no break). Per C-RT-04 frozen-post-bootstrap discipline.

**Integration with C-RT-15 + C-RT-16 (inner dispatchers).** No protocol change to either. The C-RT-16 wrapper is reused verbatim as the `INFERENCE_STEP` dispatcher binding in the registry.

**Integration with C-RT-06 (TracerProvider).** Two nested spans per composer invocation: outer `subagent.span` (covers the full sub-workflow envelope) + the child workflow's own spans (`workflow.start`, per-step `step.boundary`, etc.) which nest inside `subagent.span` via OTel context propagation. The narrow-scope shape preserves the C-CP-14 §14.1 nesting invariant.

**Integration with C-RT-08 (`run()` Python API).** The child workflow runner per §14.7.4 invokes the same `execute_workflow()` surface that C-RT-08's `run()` invokes for the top-level workflow. v1.6 MVP shares the parent's `HarnessContext`; v1.7+ may introduce child-context isolation per future C-RT-NN.

**Invariants.**

- `RuntimeSubAgentDispatcher` is async (matches C-RT-08 async-only `run()` posture).
- `RuntimeSubAgentDispatcher` satisfies `isinstance(dispatcher, StepDispatcher)` via the same `@runtime_checkable` introspection (per `harness-cp/src/harness_cp/workflow_driver.py:151`).
- `subagent.span` emitted exactly once per composer invocation.
- `subagent.*` and `topology.*` attributes set from the canonical CP-side carrier (no hand-coded attribute strings).
- The child sub-workflow's `RunResult` is returned to the composer without modification; the composer maps to step output without re-interpreting child failure semantics.
- The composer does NOT swallow exceptions from the child runner: typed errors (payload shape, topology inadmissibility, child runtime failure) propagate to the driver's `try/except` per C-CP-25 §25.3.3.4.
- `StepKindDispatcherRegistry` is frozen post-construction; runtime mutation is foreclosed by Pydantic v2 `frozen=True` on the dataclass.
- `StepKindDispatcherRegistry.lookup(unbound_kind)` raises `StepKindDispatcherNotBoundError` (no silent fallback to a default dispatcher).
- v1.6 MVP fan-out emission is foreclosed: composer MUST NOT emit `topology.fanout.opened` / `topology.fanout.closed` events; MUST NOT set the 8 fan-out-specific `topology.*` attributes. Enforcement is by construction (composer body does not call the corresponding emission paths).

**Failure-mode taxonomy.** Per C-RT-14, with one new fail class added at v1.6:

| Fail class | Trigger | Behavior |
|---|---|---|
| `RT-FAIL-SUB-AGENT-CHILD-FAILED` (permanent, new at v1.6) | Child sub-workflow's terminal `RunResult.status == FAILED` after composer's child-runner invocation per §14.7.2 step 6 | Composer sets `subagent.result_status = "failed"` on the `subagent.span`; composes + emits audit entry with `child_result_status="failed"`; raises typed `RetryBreakerFallbackExhaustedError`-shape `SubAgentChildFailedError`; driver `try/except` maps to `step-failure: RT-FAIL-SUB-AGENT-CHILD-FAILED: ...` per C-CP-25 §25.3.3.4 |
| `RT-FAIL-SUB-AGENT-TOPOLOGY-INADMISSIBLE` (permanent, new at v1.6) | `is_admissible(topology, workload_class)` returns False at §14.7.2 step 4 | Composer raises typed `SubAgentDispatchTopologyInadmissibleError`; driver `try/except` maps to `step-failure: RT-FAIL-SUB-AGENT-TOPOLOGY-INADMISSIBLE: ...` per C-CP-25 §25.3.3.4. No partial spans; the failure surfaces before `subagent.span` open. |
| `RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND` (permanent, new at v1.6) | Driver invokes `ctx.step_dispatchers.lookup(step.kind)` with a `step.kind` not bound in the registry (3 of 5 step_kinds are unbound at v1.6: `DECLARATIVE_STEP`, `TOOL_STEP`, `HITL_STEP`) | Registry raises `StepKindDispatcherNotBoundError`; driver `try/except` maps to `step-failure: RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND: ...` per C-CP-25 §25.3.3.4. Documented expected behavior at v1.6; resolved as follow-on composer arcs land. |

The existing `RT-FAIL-PAYLOAD-SHAPE` (from §14.5) is reused for `SubAgentDispatchPayloadShapeError` (the new typed error subclasses the existing payload-shape fail class semantics).

**X-AL-2 retirement implications (v1.6 → retirement event prerequisites).**

The C-RT-17 contract specifies the composition seam whose absence was the substitution-site B-condition blocker for H_T-CP-10 + H_T-CP-13 + H_T-CP-14 per `Phase_7_Meta_Architecture_v1.md` §5.4. At U-RT-59 landing event:

- **H_T-CP-10 RETIRE-READY.** `TopologyPattern` dispatcher operational + `is_admissible` predicate callable at production execution path per §14.7.2 step 4. Condition A: U-CP-22 + U-RT-40 + U-RT-59 landed. Condition B: topology dispatcher no longer requires `CLAUDE.md`-prose substitution; runtime invokes at production execution path. Verified at retirement audit.
- **H_T-CP-13 RETIRE-READY.** `RuntimeHandoffRegistry.dispatch(...)` operational + `HandoffContext` schema composed at production execution path per §14.7.2 step 2 + step 3. Condition A: U-CP-28 + U-CP-29 + U-CP-30 + U-RT-26 + U-RT-59 landed. Condition B: typed sub-agent dispatch schemas enforced at production callsite (Pydantic v2 validation at `SubAgentDispatchPayload` + at `HandoffContext` construction); no longer substituted by `Agent` free-text prompt + tool list.
- **H_T-CP-14 PARTIAL → RETIRE-READY (single-sub-agent slice).** `subagent.*` 7-attribute namespace + narrow-subset `topology.*` (2 attributes: `pattern`, `workload_class`) emitted at production span hierarchy per §14.7.2 step 5. Condition A: U-CP-31 + U-CP-32 + U-RT-59 landed. Condition B: namespace emission at production execution path (vs `CLAUDE.md`-substituted). The fan-out-specific `topology.*` attributes (8 of 10 per §14.2) are NOT emitted at v1.6 (out of scope). Strict X-AL-2 reading: PARTIAL retirement is non-retirement. Operator may ratify the single-sub-agent slice as PARTIAL → RETIRED at retirement audit IF the bounded scope is documented as a follow-on parent-topology-expansion arc; otherwise PARTIAL stands until fan-out arc lands.

**Cross-axis cascade considerations.** None directly enabled by this contract; the §6.3.2 F-CP-01 Stage 3b inversion cascade was FULLY DISCHARGED at U-RT-58 landing. C-RT-17 lands inside an already-discharged inversion-seam region.

**Deferred to implementation discretion.**

- Exact dispatcher class names (suggest `RuntimeSubAgentDispatcher`; `StepKindDispatcherRegistry` per the §14.7 narrative recommendation).
- `SubAgentDispatchPayload` Pydantic model field overrides for the bounded-reduction HandoffContext fields per §14.7.3 (whether operator workflows author overrides for `agent_confidence`, `state_summary.summary_text`, etc. — MVP defers; v1.7+ extension surface).
- `compose_child_action_id(parent_action_id, child_workflow_id)` construction shape (suggest `f"{parent_action_id}::child::{child_workflow_id}"` for traceability; alternatively a SHA-256 hash for stable length).
- Whether child runner shares parent `HarnessContext` (v1.6 MVP) or composes a child context (v1.7+ scope question; relates to sandbox-tier child-descent isolation; CP-AL-1-adjacent boundary — child sub-agent reading from parent's ledger writer at sandbox-tier-descent is a cross-axis question owed to future arc review).
- Test mock strategy: suggest a `MockChildWorkflowRunner` fixture that records the sequence of `(workflow_id, manifest_entry, steps, handoff_context, descent)` calls + returns canned `RunResult` per call; verify composer's HandoffContext composition + descent computation + span emission + audit composition against the recorded sequence. Pytest-asyncio for async surface.
- Span name conventions: suggest `subagent.span` for the dispatch envelope (matches C-CP-14 §14.1 hierarchy element name); the C-RT-08 `workflow.start` is the child's own root span (nested inside).
- Whether the composer emits a `subagent.span.closed` event distinct from `subagent.span` close (per C-CP-14 §14.1 — separately attributed) — v1.6 MVP folds both into the single `subagent.span` close event; if OTel telemetry-volume discretion at deployment surfaces a need, separate event emission is a v1.7+ extension.

---

## §15 Spec-to-plan traceability

Each Track A plan v2 unit cites at least one contract in this spec. Coverage matrix:

| Plan unit | Spec contract(s) | Notes |
|---|---|---|
| U-RT-00 | (this spec entirely — U-RT-00 IS the spec authoring unit) | Hard gate |
| U-RT-01 | C-RT-02 §1 layout | Package scaffold matches stage-file naming |
| U-RT-02 | C-RT-03, C-RT-04 | Types are direct implementations of the schemas |
| U-RT-03 | C-RT-01 | Enum is direct implementation |
| U-RT-04..U-RT-08 | C-RT-03 sub-models | Config sub-models |
| U-RT-09..U-RT-12 | C-RT-02 stage 1 invariants | IS bootstrap stage |
| U-RT-13..U-RT-16 | C-RT-02 stage 2 invariants | AS bootstrap stage |
| U-RT-17..U-RT-20 | C-RT-05 (incl. `ProviderClient` Protocol), C-RT-02 stage 3a invariants | Provider SDK lifecycle |
| U-RT-21..U-RT-26 | C-RT-02 stage 3b invariants | CP routing wiring |
| U-RT-27..U-RT-32 | C-RT-06, C-RT-07, C-RT-02 stage 4 invariants | OD observability runtime |
| U-RT-33 | C-RT-12 §12.1 | Terminal aggregate exporter manifest import |
| U-RT-34 | C-RT-12 §12.2 | AS → IS edge |
| U-RT-35 | C-RT-12 §12.3 | CP → IS 17 edges |
| U-RT-36 | C-RT-12 §12.4 | OD → IS 2 edges |
| U-RT-37 | C-RT-12 §12.5 | OD → AS 1 edge |
| U-RT-38 | C-RT-12 §12.6 | OD → CP 3 edges |
| U-RT-39..U-RT-41 | C-RT-02 stage 5 invariants | Loop activation |
| U-RT-42 | C-RT-08 (incl. v1.1 idempotency invariant), C-RT-09 | Python API + result shape |
| U-RT-43 | C-RT-02 | Bootstrap orchestrator |
| U-RT-44 | C-RT-11 | Drain semantics |
| U-RT-45..U-RT-46 | C-RT-10 | Shutdown sequence |
| U-RT-47..U-RT-48 | C-RT-13 | Admin stubs |
| U-RT-49..U-RT-51 | C-RT-02 + C-RT-12 verification | E2E + Pattern P1 verification |
| U-RT-52 (new at v1.2) | C-RT-15, C-RT-05, C-RT-06 | LLM-dispatch composer; satisfies `harness_cp.workflow_driver.StepDispatcher` Protocol; emits GenAI semconv 1.41.0 spans |
| U-RT-58 (new at v1.4) | C-RT-16, C-RT-15, C-RT-06 + C-CP-03 §3.5, C-CP-04 §4.2, C-CP-21 §21.2 | Retry/breaker/fallback composer wrapping C-RT-15; owns per-step candidate-iteration loop + per-candidate retry loop; emits `retry.*` 6-attribute namespace on inner per-attempt span + `fallback.exhausted` on outer span on chain exhaustion; reserved registry key `"llm_dispatch"`; replaces bare C-RT-15 dispatcher at `ctx.llm_dispatcher` (preserving the `StepDispatcher` Protocol seam) |
| U-RT-59 (new at v1.6) | C-RT-17, C-RT-04, C-RT-06, C-RT-08 + C-CP-10, C-CP-12, C-CP-13, C-CP-14 §14.1/§14.2 (narrow-scope), C-CP-25 §25.2/§25.3.3.4 | Sub-agent dispatch composer + `StepKindDispatcherRegistry` driver routing layer + `ChildWorkflowRunner` in-process recursive invocation primitive; emits `subagent.*` 7-attribute namespace (full) + `topology.*` 2-attribute subset (`pattern` + `workload_class`); composes `HandoffContext` per C-CP-13 §13.1; invokes `ctx.handoff_registry.dispatch` for gate descent per C-CP-12 + `ctx.topology_dispatcher.dispatch` + `is_admissible` per C-CP-10 §10.3; composes audit entry via existing `compose_dispatch_audit`; refactors driver to dispatch via `ctx.step_dispatchers.lookup(step.kind)` (preserves `StepDispatcher` Protocol + C-CP-25 §25.3.3.4 "step body opaque to driver" invariant); fan-out + cache warm-up + cross-family-fallback-at-fan-out out of scope at v1.6 (parent-topology-expansion arc) |
| (cross-cutting) | C-RT-14 | Every U-RT-NN that surfaces a failure emits via the runtime-local fail-class taxonomy |

Every U-RT-NN unit traces to ≥1 spec contract. ✓

---

## §16 Open questions and known risk surfaces (carry into review)

These are explicit open questions surfaced at authoring time. Each must either be resolved at P2-S4-CK adversarial review or carried as a candidate Class 1 fork at unit-landing time.

1. **Trace-discipline adaptation acceptable?** Front-matter §"Trace-discipline novelty" substitutes `PRD enablement` for `PRD requirement(s) satisfied` and `Fork-resolution provenance` for `Persona linkage`. **Cleared at P2-S4-CK 2026-05-19 (v1 review).** Carries forward as a candidate Class 1 fork for any future aggregate review; back-flow shape sketched in front-matter.
2. **`WorkflowObject` shape source.** C-RT-08 risk note enumerates three options. The decision lands at U-RT-42 implementation, not here. P2-S4-CK should pressure-test whether the spec should pin it now. (v1.1: carried — still open.)
3. **Collector daemon supervision contract in OD spec vs Runtime spec.** C-RT-07 specifies supervision here. P2-S4-CK should verify whether this contract belongs in OD spec instead (OD C-OD-20 §20.1 currently covers placement matrix but not supervision semantics). (v1.1: carried — still open.)
4. **Async-only `run()` posture (decided).** C-RT-08 has pinned async-only as a normative invariant at Track A (no sync wrapper). **Open for re-evaluation:** does any anticipated Track A integration scenario require a sync surface? (v1.1: reworded from over-open phrasing per F1-02.)
5. **Pidfile location and CLI naming.** C-RT-13 picks `.harness/runtime.pid` and `harness-inspect` / `harness-shutdown` command names. P2-S4-CK should verify these don't collide with prior workspace conventions. (v1.1: carried — still open.)
6. **Tenant identity scope.** C-RT-03 includes optional `tenant_id`; C-RT-04 routes it through audit writer. P2-S4-CK should verify the routing is complete (does cost attribution also need per-tenant scoping?). (v1.1: carried — still open.)
7. **Bootstrap-per-call vs cached context.** C-RT-08 specifies bootstrap-per-call for Track A. P2-S4-CK should verify this is acceptable for any anticipated Track A integration test scenarios (cached-context optimization is Track B). v1.1 added the concurrency invariant (`RT-FAIL-CONCURRENT-RUN`) which makes the bootstrap-per-call discipline enforceable, partially closing this. (v1.1: partially closed; carry forward the cached-context-Track-B side.)
8. **(v1.1 new) OD cost-attribution + audit-ledger §-pins.** Cross-axis citation substrate cites these as "specific §-pin verified at U-RT-31 / U-RT-32 landing." If verification at landing surfaces that the contracts don't exist (i.e., OD spec doesn't formally specify cost-chain or audit-writer), surface as Class 1 fork.
9. **(v1.1 new) `WorkflowEventClass.DRAINED` event-name landed-axis alignment.** C-RT-11 introduces a `DRAINED` event; per Workflow §2.5.2 Pattern P1-PHASE-5 discipline, event-name verb forms must align across axis specs. If landed `harness_core.workflow_event_class` enum doesn't carry `DRAINED`, U-RT-41 lands an aligned name. Surface as Class 1 fork at U-RT-41 landing if alignment fails.

---

## §17 Coherence pass — self-audit at v1.2 filing

| Dimension | Check | Result |
|---|---|---|
| v1.1 → v1.2 change-note completeness | Single-finding addition documented; scope discipline (Q1a + Q2a + Q3a + Q4a) recorded; preserved-verbatim list explicit | ✅ PASS |
| C-RT-15 trace-discipline conformance | Contract surface + PRD enablement + ADR commitment + Fork-resolution provenance + Specification content + Invariants + Failure-mode taxonomy + Deferred-to-implementation discretion all present | ✅ PASS |
| Q2a scope discipline (no silent extension) | Composer explicitly excludes fallback / retry / breaker per Q2a; CP-3 + CP-4 retirements explicitly deferred; X-AL-3 no-silent-H_T-design-extension holds | ✅ PASS |
| Q3a GenAI semconv binding | `gen_ai.*` attribute set normative; `anthropic.*` namespace explicitly conditional on `binding.model_binding.provider == "anthropic"` per AS-AL-3 | ✅ PASS |
| Cross-axis citation precision | C-AS-13 / C-AS-14 §14.2 (Anthropic primitive observability); C-OD-04..08 (OD GenAI semconv binding); C-CP-01 §1 (capability-aware abstraction); CP `StepDispatcher` Protocol at `harness_cp.workflow_driver:151` | ✅ PASS |
| Fail-class reuse (no new RT-FAIL-*) | C-RT-15 reuses C-RT-14's `RT-FAIL-PROVIDER-UNREACHABLE` + `RT-FAIL-TRANSIENT` + `RT-FAIL-PROVIDER-AUTH`; no new fail-class introduced | ✅ PASS |
| Plan traceability | §15 row added for U-RT-52 citing C-RT-15 + C-RT-05 + C-RT-06 | ✅ PASS |
| Predecessor preservation | §§1–14, §15 (except U-RT-52 row), §16 unchanged verbatim from v1.1 | ✅ PASS |
| Fork-record back-reference | C-RT-15 §Fork-resolution provenance cites `.harness/fork_llm_dispatch_composer_scope.md` + per-Q decision | ✅ PASS |
| Cross-axis cascade documentation | §6.3.1 CP-1 → AS-8 anthropic.* slot closure explicitly noted at C-RT-15 step 2; §6.3.2 OD-2 + CP-24 → CXA-5 cascade not enabled by this contract alone (breaker invocation absent per Q2a) — consistent | ✅ PASS |

---

## §17.1 Coherence pass — self-audit at v1.1 filing (preserved verbatim from v1.1)

| Dimension | Check | Result |
|---|---|---|
| Front-matter completeness | Change-note, Status block, source-set, ADR scope, cross-axis citation substrate, scope table all present | ✅ PASS |
| Trace adaptation explicit | §"Trace-discipline novelty" called out before first contract; back-flow shape sketched at v1.1 | ✅ PASS |
| Per-contract structure | Every C-RT-NN (1..14) has: Contract surface · PRD enablement · ADR commitment · Fork-resolution provenance · Specification content · Invariants · Failure-mode taxonomy (where applicable) · Deferred to implementation discretion | ✅ PASS |
| ADR citations canonicalized (v1.1) | Every ADR cite includes version + canonical §-section (`§Decision` / `§Consequences` / `§N.M` for D-ADRs) verified against source ADR files | ✅ PASS |
| Cross-axis citations corrected (v1.1) | C-IS-01..10, C-AS-01..16, C-CP-01..24, C-OD-01..23 contract IDs verified against source spec enumerations; §-pins included where verified; partial-precision items explicitly flagged | ✅ PASS (with §-pin verification deferred to U-RT-31/32 landing per cross-axis substrate note) |
| Plan trace completeness | §15 covers all 50 U-RT-NN units; C-RT-12 sub-subsections map 1:1 with U-RT-33..U-RT-38 | ✅ PASS |
| Open-questions explicit | §16 enumerates 9 candidate Class 1 fork surfaces; #1 cleared with carry-forward; #4 reworded per F1-02; #7 partially closed by v1.1 concurrency invariant | ✅ PASS |
| Failure modes per operational contract | C-RT-02, 03, 05, 06, 07, 08, 10, 11, 13 each have failure-mode taxonomy; all reference runtime-local fail classes at C-RT-14 | ✅ PASS |
| Schema vs prose discipline | Tables for matrices, Pydantic-style prose for schemas, no mixing within a contract | ✅ PASS |
| Schema version-evolution (v1.1) | C-RT-03, C-RT-04, C-RT-09 each carry Version evolution invariant | ✅ PASS |
| No restated ADR/PRD content | Contracts derive but do not restate | ✅ PASS |
| Deferred-to-implementation explicit | Every operational contract has explicit deferred list | ✅ PASS |
| Scope boundary clean | §"Scope and out-of-scope" table separates Track A from Track B / future; row added at v1.1 for runtime-local fail-class taxonomy (orthogonal to CP) | ✅ PASS |
| Fail-class taxonomy orthogonality (v1.1) | C-RT-14 enumerates runtime-local taxonomy with explicit orthogonality table against CP `validator_fail_taxonomy` | ✅ PASS |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Harness_Runtime_v1.md` |
| Status | **Proposed (v1.2)** — Phase 7 sub-phase 7d Class 2 fork absorption (LLM-dispatch composer scope) |
| Predecessor | v1 (2026-05-19 initial authoring) → v1.1 (2026-05-19 adversarial-review absorption) → v1.2 (2026-05-20 fork-LLM-dispatch-composer-scope absorption via operator Q1a+Q2a+Q3a+Q4a) |
| Substrate consumed | F-P2-1..F-P2-5 fork resolution records; `.harness/phase-2-session-1-framing.md`; `.harness/phase-2-session-2-track-a-strawman.md`; `.harness/phase-2-session-3-track-a-atomic-decomposition.md` v2; `.harness/Adversarial_Review_phase_2_session_4_runtime_spec.md`; ADR-F1..F5; ADR-D1, D2, D6; ADD v1.3; `Cross_Axis_Composition_Document_v2_3.md` §2.3, §3; landed code across `harness-{core,is,as,cp,od,cxa}/`; per-axis spec contract enumerations verified at v1.1 |
| Successor | `harness-runtime/` package landing per Track A plan v2 (Session 5 onward); per-axis spec amendments triggered by U-RT-NN unit landings that surface gaps (per `Project_Workflow_v1_8.md` §2.7.6 back-flow); plan v2 minor revision to add C-RT-14 row in §14 traceability |
| Revision policy | In-CLI per workspace `CLAUDE.md` §4.3 (design-substrate/ canonical; back-flow deprecated 2026-05-15) |
| Adversarial review | v1: P2-S4-CK 2026-05-19 (`.harness/Adversarial_Review_phase_2_session_4_runtime_spec.md`) — 0 Class 3 / 7 Class 2 / 3 Class 1; revision pass produces v1.1. v1.1: P2-S4-CK second pass pending operator request. v1.2: adversarial-review second pass deferred to U-RT-52 landing event per operator Q4a phasing — implementation begins on the v1.2 surface. |
| Date | 2026-05-19 (v1.1) |
