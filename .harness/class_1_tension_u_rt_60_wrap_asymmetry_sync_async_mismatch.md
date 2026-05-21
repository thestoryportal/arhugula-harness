# Class 1 Tension — U-RT-60 wrap-asymmetry sync/async mismatch

**Status.** PROPOSING (filed 2026-05-21; awaiting systems-architect mode 3 recommendation + operator ratification)

**Detected at.** `phase-7-implementation` Step 2 (cited-spec cross-check vs partial impl + landed C-RT-16 wrapper) during U-RT-60 follow-on impl arc against runtime spec v1.11 + plan v2.9.

**Surfacing turn.** HEAD `9b8a36c` (this session, after composer-body deferred ACs landing). The deferred composer-body ACs (#5 / #6 / #9 / #10 / #11 / #13-source-introspect-half) are independent of this fork and landed at `9b8a36c`. This fork halts the wrap-chain-dependent ACs (#12, #13-stage-5-half, stage 5 wiring, MCP binding, AC #14 retirement event).

**Class.** **1 (halt-execution)** per `Project_Workflow_v1_8.md` §2.7.6: spec contract surface (the §14.8.1 wrap-asymmetry table) cannot be materialized at the target stack without an architectural addition. Single-mechanical-fix is structurally unavailable.

**Pattern.** *4th adversarial-review-missed defect at U-RT-58/59/60 sequence* per the c_rt_18 span-attr-carrier-drift fork's Q6 systemic-pattern observation. **3rd consecutive Class 1 fork at the C-RT-18 contract surface** within the two-session U-RT-60 arc (binding-mechanism @ `fb545ec`; span-attr-carrier-drift @ `95a9436`; wrap-asymmetry sync/async @ this fork).

---

## 1. The contradiction

### 1.1 Spec narrative (canonical)

`Spec_Harness_Runtime_v1.md` v1.11 §14.8.1 wrap-asymmetry table row 1 (`INFERENCE_STEP`):

> `ctx.llm_dispatcher = c_rt_16_compose(hitl_gate_composer(c_rt_15, applicable_placements={PRE_ACTION}))`
>
> Composer reachable via `ctx.step_dispatchers.lookup(INFERENCE_STEP)`.
>
> Retry-of-gate semantics: **C-RT-16 retry is outer of HITL gate — every retry attempt re-evaluates the gate.** `retry.*` namespace covers all per-step attempts including HITL-gated ones.

`Spec_Harness_Runtime_v1.md` v1.11 §14.8.7 NOTE 6-iii (load-bearing future-arc commitment):

> Per Q2 ratification, C-RT-16 retry is outer of HITL gate at `INFERENCE_STEP`. This means: when an LLM dispatch attempt fails and retry triggers a new attempt, the wrapper re-enters the HITL gate composer at step 1 of §14.8.2 — re-evaluating the gate per the configured placement. **Semantically: the operator is re-asked on each retry.**

Plan `phase-2-session-3-track-a-atomic-decomposition.md` v2.9 U-RT-60 AC #12 cites this directly:

> bootstrap stage 5 wrap-chain produces `ctx.llm_dispatcher = c_rt_16_compose(hitl_gate_composer(c_rt_15, applicable_placements={PRE_ACTION}))` per spec §14.8.1 row 1 (Q2 ratification: C-RT-16 retry is outer of HITL gate). When inner LLM dispatch fails and C-RT-16 triggers a new attempt, the wrapper re-enters HITL gate composer at step 1 of §14.8.2 — **operator is re-asked on each retry attempt** per literal Q2 reading.

### 1.2 Landed surface (canonical)

`harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py:226`:

```python
async def dispatch(...)
```

Line 393:

```python
result = await self.inner.dispatch(rebound_binding, step, ...)
```

The wrapper's `dispatch` is **async**; the inner-call site **strictly awaits** the inner dispatcher. Inner MUST be async-callable.

`harness-cp/src/harness_cp/workflow_driver.py:151` (`StepDispatcher` Protocol, frozen at U-RT-59 Stage 1 wiring):

```python
@runtime_checkable
class StepDispatcher(Protocol):
    def dispatch(self, binding, step, *, step_context) -> Mapping[str, Any]: ...
```

The Protocol is **sync** (post-U-RT-59 refactor — driver `execute_workflow` is sync; the registry dispatchers MUST satisfy the sync Protocol).

### 1.3 The mismatch

Per the partial impl landing at `6998e2a`:

```python
@dataclass(slots=True)
class RuntimeHITLGateComposer:
    def dispatch(self, binding, step, *, step_context) -> Mapping[str, Any]:  # sync
        ...
```

HITL composer is **sync** (correct per sync `StepDispatcher` Protocol).

The spec wrap-chain `c_rt_16_compose(hitl(c_rt_15))` requires:

- C-RT-16's `RetryBreakerFallbackDispatcher.inner` = HITL composer
- C-RT-16 dispatch calls `await self.inner.dispatch(...)`
- Sync HITL.dispatch is NOT awaitable; sync inner-of-async cannot compose

**The spec's literal wrap-asymmetry cannot be materialized at the current sync `StepDispatcher` Protocol + async C-RT-16 wrapper.** AC #12 ("operator re-asked each retry attempt") depends on this composition.

### 1.4 Adapter-shape options surface

| Option | Mechanism | Scope | Preserves Q2 literal reading |
|---|---|---|---|
| (a) Reverse facade — `SyncToAsyncDispatcherAdapter(sync_inner)` | New helper at `harness-runtime/lifecycle/`; wraps sync HITL into async-StepDispatcher for C-RT-16 to consume via `await asyncio.to_thread(sync_inner.dispatch, ...)`. Mirror of the existing `SyncDispatcherFacade(async_inner) → sync` direction landed at U-RT-59 Path B. | Bounded (~50 LOC adapter + stage-5 wiring change). Well-precedented. | YES — HITL fires on every retry attempt because each retry attempt awaits the adapter which to_thread-invokes the sync HITL composer. |
| (b) C-RT-16 sync-tolerant inner — modify `RetryBreakerFallbackDispatcher` to detect sync vs async inner and bridge via `await asyncio.to_thread(inner.dispatch, ...)` only when inner is sync | Modifies the C-RT-16 wrapper itself (existing landed code path). Smaller new code (no new adapter module) but couples C-RT-16 to step-dispatcher sync-or-async knowledge — leaks the impedance into the retry primitive. | Smaller LOC; larger blast radius — changes a landed retired primitive's contract. | YES — same per-attempt re-entry. |
| (c) Make HITL composer async, expose sync-facade for registry | HITL becomes `async def dispatch(...)`; bootstrap stage 5 wraps it with `SyncDispatcherFacade` for the registry binding; `RetryBreakerFallback` consumes the bare async HITL. | Inverts the partial impl's design choice (sync HITL). Requires ~80 LOC refactor + test churn. Most spec-conformant: spec §14.8.1 item 1 actually declares "Async `dispatch(binding, step, *, step_context) -> StepOutput`" — the partial impl deviated from spec at the sync choice. | YES — same per-attempt re-entry. |
| (d) Drop AC #12 per-attempt semantics; HITL fires once per step regardless of retry | Wrap-chain becomes `SyncFacade(RetryBreakerFallback(bare_async))` outside HITL; HITL fires once per step at the registry binding layer. Cleanest code shape but violates spec Q2 literal reading. | Bounded code change. | **NO** — violates spec Q2 literal reading + NOTE 6-iii commitment. Operator NOT re-asked on retry; the retry-of-gate-eval semantic surface deferred to a follow-on arc + spec amendment (becomes Class 1 spec revision back-flow). |

---

## 2. 6-Q decision surface

### Q1 — Adapter direction

Which of (a) reverse facade, (b) C-RT-16 sync-tolerant, (c) async-HITL-with-registry-facade, (d) drop-AC-#12 + spec amendment is the operative resolution path?

### Q2 — Single-instance-per-step_kind impact

Does the chosen resolution preserve the v1.9 MVP "single-instance-per-step_kind" composer discipline (spec §14.8.1)?

### Q3 — `SUB_AGENT_DISPATCH` wrap-chain coherence

Spec §14.8.1 row 2 declares `ctx.sub_agent_dispatcher = hitl_gate_composer(c_rt_17, {SUB_AGENT_BOUNDARY})` — no retry layer. C-RT-17 (sub-agent dispatch composer) is sync per the U-RT-59 landing. Sync HITL wrapping sync C-RT-17 composes directly — no mismatch on this row. Does the chosen resolution for INFERENCE_STEP create any consistency obligation against the SUB_AGENT_DISPATCH row?

### Q4 — AC #12 semantic preservation

Per literal Q2 ratification + NOTE 6-iii: "operator re-asked on each retry attempt." Does the resolution preserve this semantic, or does it require a separate spec amendment to alter the semantic? (Options (a), (b), (c) preserve; option (d) requires amendment.)

### Q5 — Cascade scope

Does the resolution change anything outside the runtime axis? In particular: any change to CP `StepDispatcher` Protocol shape (sync vs async)? Any change to C-RT-16 / C-RT-17 spec contracts? Any change to CXA edges?

### Q6 — Retroactive Q6-systemic-pattern catch validation

The c_rt_18 span-attr-carrier-drift fork (resolved at HEAD `95a9436`) surfaced a Q6 systemic-pattern observation: 4 adversarial-review-missed defects at U-RT-58/59/60. The operator scheduled three skill-body extensions (`harness-adversarial-reviewer` pre-impl carrier-diff; `phase-7-implementation` Step 2 attribute-name cross-check; `spec-writer` carrier-diff at attribute revision).

**Validation question:** would any of these extensions have caught the present wrap-asymmetry sync/async mismatch at the pre-impl review stage?

- (a) `harness-adversarial-reviewer` carrier-diff — NO. The wrap-asymmetry is a CONTRACT-shape issue (sync vs async), not an attribute-name issue. Adversarial reviewer carrier-diff catches narrative-vs-carrier drift on attribute names, not wrap-chain composability.
- (b) `phase-7-implementation` Step 2 attribute-name cross-check — PARTIAL. Step 2 reads cited spec contract; if Step 2 were extended to "verify cited wrap chain is materializable at the target stack's sync/async surface" the defect would surface earlier. But the current Q6 articulation is attribute-name-only; extension scope must widen.
- (c) `spec-writer` carrier-diff at attribute revision — NO. spec-writer applies decided fixes; the wrap-asymmetry was authored at v1.9 spec growth (before partial impl), not at a spec revision.

**Recommendation seeded for Q6 follow-on:** Q6 extension scope must widen from attribute-name to **contract-shape composability** (sync/async, sync-Protocol-vs-async-inner). New extension surface: at spec authoring time (`spec-writer` + adversarial reviewer at pre-spec-clearance), mandate composability verification when a contract declares a wrap chain across previously-landed wrappers with known sync/async postures.

---

## 3. Architectural surfaces touched

- `Spec_Harness_Runtime_v1.md` v1.11 §14.8.1 (wrap-asymmetry table) + §14.8.7 NOTE 6-iii
- `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py:226+393` (C-RT-16 wrapper)
- `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:282+510` (sync HITL composer)
- `harness-runtime/src/harness_runtime/lifecycle/sync_dispatcher_facade.py` (precedent — `SyncDispatcherFacade(async) → sync` exists; reverse direction may need new module)
- `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py:113-205` (current stage 5 wrap-chain; pending HITL extension)
- `harness-cp/src/harness_cp/workflow_driver.py:151` (sync `StepDispatcher` Protocol)
- Plan `phase-2-session-3-track-a-atomic-decomposition.md` v2.9 U-RT-60 ACs #12 + #13 (wrap-chain post-condition assertions)

---

## 4. Routing

Per `Project_Workflow_v1_8.md` §2.7.6 Class 1 (halt-execution) routing:

1. **This fork record** filed at PROPOSING.
2. **`systems-architect` mode 3** invoked next to author 6-Q chain-grounded recommendation against the authority chain (ADR-F1 v1.2 + spec §14.8.1 + sync Protocol post-U-RT-59 + landed C-RT-16 wrapper). Expected status: PROPOSING → RATIFIED at operator AskUserQuestion ratification.
3. **`spec-writer`** applies the spec amendment if option (d) chosen; runtime spec v1.11 → v1.12 + plan v2.9 → v2.10 Form A NOTE-form absorption. Otherwise, no spec change required (options a/b/c are implementation-level).
4. **`phase-7-implementation`** resumes U-RT-60 follow-on impl arc against re-clearance state — lands AC #12 retry-of-gate test + stage 5 wiring + AC #13 wrap-chain post-condition half + MCP-server binding + AC #14 retirement event.

**Halt invariants.** Per workspace `CLAUDE.md` §4.3 (Class 1 halt-execution) + §4.4 (NO silent H_T design extension at Phase 7): no stage-5 wiring + no AC #12 test + no MCP-server binding + no AC #14 retirement event before this fork is RATIFIED.

---

## 5. Provenance + co-publication

| Field | Value |
|---|---|
| Filed at | 2026-05-21 (same session as the c_rt_18 span-attr-carrier-drift fork RATIFICATION at HEAD `95a9436` + the deferred-AC landing at HEAD `9b8a36c`) |
| Detected by | `phase-7-implementation` Step 2 cross-check (cited-spec wrap chain vs landed C-RT-16 inner-call shape vs sync StepDispatcher Protocol) |
| Surfacing trigger | Attempt to land stage 5 wiring per AC #13 wrap-chain post-condition + AC #12 retry-of-gate test |
| Halted scope | Stage 5 wiring + AC #12 + AC #13 wrap-chain-half + MCP-server binding + AC #14 retirement event |
| Non-halted scope (LANDED at `9b8a36c`) | AC #5 + AC #6 + AC #9 + AC #10 + AC #11 + AC #13 source-introspect-half + CXA P1 22 → 24 seam extension |
| Predecessor forks at C-RT-18 surface | `.harness/class_1_tension_c_rt_18_ask_user_question_surface_binding_mechanism_underspec.md` (APPLIED @ `fb545ec`); `.harness/class_1_tension_c_rt_18_hitl_span_attribute_carrier_drift.md` (APPLIED @ `95a9436`) |
| Q6 systemic-pattern observation | Re-confirmed at this fork — 5th adversarial-review-missed defect at U-RT-58/59/60 sequence. Q6 extension scope must widen beyond attribute-name to contract-shape composability. |

---

## 6. Next-session entry shape

1. **Operator decision at next session opening:** confirm fork PROPOSING → invoke `systems-architect` mode 3 for 6-Q recommendation.
2. Architect produces recommendation appended to this record.
3. AskUserQuestion ratification turn → PROPOSING → RATIFIED.
4. If option (a/b/c) ratified: `phase-7-implementation` resumes U-RT-60 follow-on without spec amendment. If option (d) ratified: `spec-writer` applies spec v1.11 → v1.12 amendment first; `implementation-planner` updates plan v2.9 → v2.10; then `phase-7-implementation` resumes.
5. Q6 systemic-pattern extension arc revisited at follow-on (contract-shape composability surface added to the 3 skill-body extension scopes already pinned).

---

## 7. Systems-architect mode 3 resolution recommendation (appended 2026-05-21)

**Mode.** `systems-architect` skill §4A tension-resolution. Author does NOT decide; produces a recommendation traced to the canonical authority chain per workspace `CLAUDE.md` §1.3. **Operator decides** at the AskUserQuestion ratification turn.

### 7.1 §2 discipline decomposition

**Five-axis (per `systems-architect` §2.1).**
- **Primary axis: Control Plane.** Wrap-chain composition mechanism for `INFERENCE_STEP` + `SUB_AGENT_DISPATCH` dispatchers. Touches the per-step dispatch composition seam declared at C-RT-18 §14.8.1.
- **Secondary axis: Operational Discipline.** Retry namespace emission per `retry.*` (C-CP-03 §3.5) + audit-entry composition per the 4-substep sequence (C-CP-13 §13.5.1 + §14.8.2 step 4h). Retry-of-gate semantics affect operator-burden + audit-trail cardinality.
- **Out of axis:** ADR-F1 v1.2 (multi-LLM commitment) is unaffected. CP `StepDispatcher` Protocol shape stays sync (the U-RT-59 Path B resolution; not under reconsideration).

**Probabilistic-deterministic boundary (per `systems-architect` §2.2).** The wrap chain is pure deterministic — sync/async composability + dispatcher Protocol satisfaction. No probabilistic surface implicated. The "operator re-asked each retry attempt" semantic (NOTE 6-iii) is a *deterministic* surface: each retry attempt deterministically re-invokes the gate composer (the operator's *response* is probabilistic; the *gate invocation* is not).

**Decision ordering (per `systems-architect` §2.3).** This is a **D-level (derivative)** decision. The F-level commitments are: ADR-F1 v1.2 (multi-LLM) + sync `StepDispatcher` Protocol (post-U-RT-59 Path B) + async `RetryBreakerFallbackDispatcher` (post-U-RT-58 landing) + spec §14.8.1 wrap-asymmetry table (declares `c_rt_16(hitl(c_rt_15))` per Q2 ratification at the c_rt_18 cp_20 fork). The wrap-mechanism choice is downstream of all four and constrained by them.

### 7.2 Per-Q recommendation

#### Q1 — Adapter direction [HIGH] → **(c) make HITL composer async; SyncDispatcherFacade for registry binding**

**Recommended.** Three concurrent chain anchors converge on (c):

1. **Spec-canonical posture.** Spec §14.8.1 item 1 line 1539 declares verbatim:
   > Async `dispatch(binding, step, *, step_context) -> StepOutput`.

   The partial-impl sync choice (HEAD `6998e2a`) is a leaf-narrative deviation from this declaration. Spec is canonical for the composer's posture; the partial-impl deviation is the artifact-out-of-chain.

2. **Wrap-chain literal preservation.** Spec §14.8.1 wrap-asymmetry table row 1 declares verbatim:
   > `ctx.llm_dispatcher = c_rt_16_compose(hitl_gate_composer(c_rt_15, applicable_placements={PRE_ACTION}))`

   Only (c) realizes this literally as a 3-layer chain. Option (a) requires a 4-layer chain with two facades (sync→async for HITL-as-inner-of-async-retry + async→sync at the registry top). Option (b) modifies the C-RT-16 retry primitive itself — leaks dispatcher sync/async knowledge into the retry contract.

3. **U-RT-59 Path B precedent.** `SyncDispatcherFacade` at `harness-runtime/.../sync_dispatcher_facade.py` was authored explicitly to bridge async-dispatcher → sync `StepDispatcher` Protocol via `asyncio.run_coroutine_threadsafe(...).result(timeout=...)` against captured outer loop. (c) reuses this primitive at one site (the registry top); no new facade module needed. (a) requires a *reverse* facade (sync→async) — new module, non-symmetric with the precedent.

**Chain coherence summary:**

| Option | Spec §14.8.1 item 1 (async) | Spec §14.8.1 row 1 literal | U-RT-59 facade reuse | Sync HITL leaf-deviation conformed |
|---|---|---|---|---|
| (a) Reverse facade | ✗ (HITL stays sync; spec declares async) | ✗ (4-layer chain; 2 facades) | ✗ (requires NEW reverse facade) | ✗ (leaf-deviation preserved) |
| (b) C-RT-16 sync-tolerant inner | ✗ | ~ (3-layer + retry primitive contract leak) | ✗ (no facade reuse; modifies primitive) | ✗ |
| **(c) async HITL + SyncDispatcherFacade** | **✓** | **✓** (3-layer chain; 1 facade at top) | **✓** (reuses existing facade) | **✓** (conforms leaf to chain) |
| (d) Drop AC #12 + spec amendment | ~ (spec amends to allow sync) | ✗ (semantic change; HITL fires once per step) | — | n/a |

**Materialized wrap chain under (c):**

```python
# stage 5 LOOP_INIT
bare = materialize_llm_dispatcher_stage(...)               # async (C-RT-15)
hitl_inf = RuntimeHITLGateComposer(
    inner=bare, applicable_placements={PRE_ACTION}, ...
)                                                          # async (C-RT-18 new)
ctx.llm_dispatcher = materialize_retry_breaker_fallback_dispatcher_stage(
    inner=hitl_inf, ...
)                                                          # async (C-RT-16 existing)
sync_inf = materialize_sync_dispatcher_facade(ctx.llm_dispatcher, ...)  # sync (U-RT-59 reuse)

hitl_sub = RuntimeHITLGateComposer(
    inner=sub_agent_dispatcher, applicable_placements={SUB_AGENT_BOUNDARY}, ...
)                                                          # async wrapping sync C-RT-17 (clean)
ctx.sub_agent_dispatcher = hitl_sub                        # field type: async (was sync)
sync_sub = materialize_sync_dispatcher_facade(hitl_sub, ...)

ctx.step_dispatchers = StepKindDispatcherRegistry(
    dispatchers={
        StepKind.INFERENCE_STEP: sync_inf,
        StepKind.SUB_AGENT_DISPATCH: sync_sub,
    },
)
```

This is the **literal spec §14.8.1 wrap-asymmetry table** with the U-RT-59 Path B SyncDispatcherFacade at the registry boundary on both rows.

**Confidence:** [HIGH] — three convergent chain anchors; partial-impl sync choice is the demonstrable leaf-deviation. The cost (composer async refactor ~50-80 LOC + test fixture re-shape to pytest-asyncio with `await composer.dispatch(...)` directly instead of `asyncio.to_thread`-bridging from sync) is bounded and well-precedented.

#### Q2 — Single-instance-per-step_kind impact [HIGH] → **Preserved trivially under (c)**

The single-instance-per-step_kind discipline (spec §14.8.1) is a *binding cardinality* invariant: one composer instance per `applicable_placements` value at v1.11 MVP. (c) does not change this — the wrap chain shown at Q1 instantiates exactly one HITL composer for `{PRE_ACTION}` + exactly one for `{SUB_AGENT_BOUNDARY}`. Same as (a), (b), (d).

**Confidence:** [HIGH]. No cascade.

#### Q3 — `SUB_AGENT_DISPATCH` wrap-chain coherence [HIGH] → **Cleanly handled under (c)**

Spec §14.8.1 row 2 declares `ctx.sub_agent_dispatcher = hitl_gate_composer(c_rt_17, {SUB_AGENT_BOUNDARY})` — no retry layer. C-RT-17 (sub-agent dispatch composer at `RuntimeSubAgentDispatcher.dispatch`) is **sync** (per U-RT-59 landing).

Under (c): async HITL wraps sync C-RT-17. The HITL composer's `async def dispatch` calls `self.inner.dispatch(...)` synchronously inside the async body (no `await` — sync call within `async def` is legal and standard). Works cleanly. Then `SyncDispatcherFacade(hitl_sub)` wraps to the sync Protocol for the registry.

**Field-type change.** `_MutableHarnessContext.sub_agent_dispatcher` field-type changes from the concrete sync `RuntimeSubAgentDispatcher` to the new async `RuntimeHITLGateComposer`. Per the C-RT-04 Protocol-vs-concrete narrowing pattern already used at `ctx.llm_dispatcher` (typed as `LLMDispatcher` Protocol; concretely `RetryBreakerFallbackDispatcher`), the field type is typically narrowed via `Any` or a Protocol — verify the existing type annotation tolerates the swap. If strictly typed, one narrow `cast(Any, ...)` at the binding site suffices (precedented at `stage_5_loop_init.py:117` for `ctx.tracer_provider` + `:176-177` for `ctx.ledger_writer / ctx.audit_writer`).

**Consistency obligation.** Both rows wrap with `SyncDispatcherFacade` at the registry top under (c). This is a *consistency*, not an *inconsistency* — both rows follow the U-RT-59 Path B precedent uniformly. (a) would require the reverse facade on row 1 only — row 2's sync-HITL-wrapping-sync-C-RT-17 needs no adapter — *that* would be the inconsistency.

**Confidence:** [HIGH]. Row 1 + row 2 wrap-chain shape under (c) is uniform; field-type swap is precedented.

#### Q4 — AC #12 semantic preservation [HIGH] → **Fully preserved under (c)**

Per spec §14.8.7 NOTE 6-iii ("operator re-asked on each retry attempt") + plan v2.9 U-RT-60 AC #12 ("3× `hitl.gate.evaluated` spans + 3× `hitl.invocation.responded` spans + 3× audit entries with distinct timestamps"):

Under (c), each `RetryBreakerFallbackDispatcher` retry attempt at line 393 executes:
```python
result = await self.inner.dispatch(rebound_binding, step, ...)
```
where `self.inner = hitl_inf` (async HITL composer). Each attempt re-enters HITL composer body step 1 of §14.8.2 — re-evaluates the gate per the configured placement — re-invokes the AskUserQuestion surface — produces a fresh audit entry. **Operator is re-asked each retry attempt**, verbatim per Q2 ratification.

**Confidence:** [HIGH]. AC #12 test can be authored against the (c) wrap chain: mock 3-attempt retry → assert 3× canonical 4-span hierarchy + 3× audit entries + 3× surface.ask calls.

#### Q5 — Cascade scope [HIGH] → **Bounded; no cross-axis cascade**

**Changes under (c):**

1. `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` (~50-80 LOC delta):
   - `RuntimeHITLGateComposer.dispatch` → `async def dispatch`
   - Drop `loop` + `result_timeout_seconds` constructor fields (no longer needed — async body awaits surface directly)
   - Drop `_ask_via_surface` helper (becomes `await self.ask_user_question_surface.ask(...)` directly)
   - `_compose_and_persist_audit` may stay sync (4-substep writes do not need awaitable inner calls; ledger_writer + audit_writer surfaces are sync per landed types)
2. `harness-runtime/tests/test_lifecycle_hitl_gate_composer.py` (~80-120 LOC test-fixture re-shape):
   - Replace `asyncio.to_thread(composer.dispatch, ...)` with `await composer.dispatch(...)` directly (cleaner; removes loop-capture ceremony)
   - Drop `_make_composer(..., loop=asyncio.get_event_loop())` ceremony; pass nothing for the loop fixture
   - 21 existing tests + the 11 added at HEAD `9b8a36c` re-shape mechanically
3. `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py` (~40 LOC delta):
   - Add HITL wrap layers per the Q1 materialized chain
   - Add 2 new `SyncDispatcherFacade` wraps (1 per registry row)
   - Add `ctx.ask_user_question_surface` binding
4. `harness-runtime/src/harness_runtime/bootstrap/mutable_context.py` + `harness-runtime/src/harness_runtime/types.py`:
   - Add `ask_user_question_surface` field (`AskUserQuestionSurface | None`)
   - `sub_agent_dispatcher` field type widening (or `cast(Any, ...)` at binding site per existing precedent)
5. NEW MCP-server-backed `AskUserQuestionSurface` impl (per spec §14.8.3 v1.11 binding pin) (~80-150 LOC depending on chosen mechanism)
6. `harness-runtime/tests/integration/test_cxa_pattern_p1.py`: AC #13 stage-5 post-condition assertion (the `isinstance(ctx.llm_dispatcher.inner, RuntimeHITLGateComposer)` half not landed at HEAD `9b8a36c`)
7. NEW Phase 7d batch 8 retirement event record per AC #14 (H_T-CP-20 RETIRE-READY)

**Does NOT change:**

- CP `StepDispatcher` Protocol shape (stays **sync** at `harness_cp/workflow_driver.py:155`) — the U-RT-59 Path B resolution is preserved verbatim
- C-RT-16 `RetryBreakerFallbackDispatcher` wrapper — no changes (consumes async inner per its existing contract)
- C-RT-17 `RuntimeSubAgentDispatcher` — no changes (sync; wrapped by async HITL above)
- ADR-F1 v1.2 / D1 / D5 / D6 — no changes
- Spec `Spec_Harness_Runtime_v1.md` v1.11 — no amendment under (c) (the wrap chain shown at Q1 IS the spec-canonical wrap chain plus a SyncDispatcherFacade at the registry boundary per U-RT-59 Path B precedent; the facade is implementation-mechanism, not contract-surface)
- Plan v2.9 U-RT-60 ACs — no body amendments (ACs #5/#6/#9/#10/#11/#13-source-half satisfied at HEAD `9b8a36c`; ACs #12/#13-wrap-chain-half/#14 land at follow-on impl arc against (c))
- CXA v2.5 edges — no changes
- `harness-cp/CLAUDE.md` substitution table — H_T-CP-20 retirement event files at AC #14 landing per existing plan

**Cross-axis cascade: NONE.** The change is entirely within harness-runtime + harness-runtime tests. No CP / AS / OD / CXA / IS edits required.

**Confidence:** [HIGH] on the scope enumeration. The MCP-server-backed binding (#5) is the largest remaining surface; its scope is bounded by spec §14.8.3 v1.11 pin (MCP-server substitution-mechanism category — direct, in-class with the 11 other MCP-server-category bounded-transport substitutions).

#### Q6 — Retroactive Q6-systemic-pattern catch validation [MODERATE-HIGH] → **Scope-widening confirmed; recommend Class 3 informational addendum to c_rt_18 fork's Q6 disposition**

The fork record (§2 Q6) already articulates the validation: none of the three currently-ratified Q6 extensions (carrier-diff at adversarial review + Step 2 attribute-name cross-check at phase-7-implementation + carrier-diff at spec-writer revision) would have caught the present wrap-asymmetry sync/async mismatch at pre-impl review. The mismatch is a **contract-shape composability defect**, not an attribute-name defect.

**Recommended scope-widening for the Q6 follow-on arc:**

| Extension surface | Currently ratified | Add for contract-shape composability |
|---|---|---|
| `harness-adversarial-reviewer` (pre-spec-clearance review) | Carrier-vs-narrative attribute-name diff | **Verify wrap-chain composability:** for every contract declaring a wrap chain across previously-landed wrappers, verify sync/async posture of each layer + inner-call shape of the outer layer + Protocol satisfaction at registry boundary. |
| `phase-7-implementation` Step 2 (cited-spec cross-check) | Attribute-name cross-check vs canonical carrier | **Wrap-chain composability check:** for every cited wrap chain in the spec contract, verify each layer's sync/async posture matches the inner-call shape of its outer layer (e.g., `async def dispatch` strictly `await self.inner.dispatch(...)` requires async inner). |
| `spec-writer` (at spec authoring touching a wrap chain) | Carrier-diff at attribute revision | **Composability declaration:** at any spec authoring declaring a wrap chain, mandate explicit sync/async posture statement for each layer + verify against landed wrapper inner-call shapes. |

**Routing:** This is a Class 3 informational addendum to the c_rt_18 span-attr-carrier-drift fork's Q6 disposition (file under that fork or as a new Class 3 record `class_3_tension_q6_scope_widening_contract_shape_composability.md`). Does NOT block U-RT-60 resolution. Operator schedules the Q6 follow-on arc independently of this fork's ratification.

**Confidence:** [MODERATE-HIGH]. Three convergent cases (c_rt_18 binding-mechanism / span-attr-carrier-drift / now wrap-asymmetry sync/async) establish the pattern; scope-widening is well-founded. MODERATE-HIGH (not HIGH) because the empirical test of "would the extension have caught the defect" is necessarily counterfactual.

### 7.3 Tiebreaker check

Per `systems-architect` §4A.2 step 5: the single verifiable fact that, if confirmed, makes (c) determinate is:

> **The HITL composer body does NOT require sync inner-call invocation for its 4-substep audit-write (step 4h) chain.** All four substep sites — `compose_hitl_response_audit` (sync function), `ledger_writer.append` (sync per landed types at `state_ledger.py`), `cp_audit_to_od_audit` (sync at `harness-cxa/`), `audit_writer.append` (sync per landed types at `audit_writer.py`) — are sync; the composer's async body can call them synchronously without `await`. The ONLY awaitable invocation in the composer body is `await self.ask_user_question_surface.ask(...)` at step 4f.

**Verification.** Inspect `harness-runtime/src/harness_runtime/lifecycle/{state_ledger,audit_writer}.py` for the `append` method signatures (must be sync) + `harness-cxa/src/harness_cxa/cp_audit_conversion.py:cp_audit_to_od_audit` (must be sync). All three already confirmed sync at the AC #9 4-substep E2E test landing (HEAD `9b8a36c`). **Tiebreaker check: PASSES.**

### 7.4 Class confirmation + operator-decides marker

**Fork class: 1 (halt-execution)** per `Project_Workflow_v1_8.md` §2.7.6 confirmed. Phase 7 sub-phase 7b execution of the wrap-chain-dependent ACs (#12 / #13 wrap-chain-half / stage 5 wiring / MCP binding / AC #14 retirement event) remains halted until operator ratification.

**Resolution path under (c):** PROPOSING → RATIFIED → APPLIED. **No spec amendment required** (the wrap chain shown at Q1 IS the spec-canonical wrap chain plus a SyncDispatcherFacade at the registry boundary per U-RT-59 Path B precedent; the facade is implementation-mechanism, not contract-surface). `phase-7-implementation` resumes directly against the v1.11/v2.9 substrate post-ratification.

**Resolution path under (d):** PROPOSING → RATIFIED → spec-writer applies spec v1.11 → v1.12 amendment (drops Q2 ratification "operator re-asked on each retry" semantic from NOTE 6-iii) + implementation-planner updates plan v2.9 → v2.10 (rewrite AC #12 to single-fire-per-step semantic) → APPLIED → `phase-7-implementation` resumes.

**Recommended:** **Option (c).** Three convergent chain anchors. Bounded cascade scope. No cross-axis edits. AC #12 semantic preserved verbatim. Composer body cleanly async. Test fixtures simpler under async (removes the existing `asyncio.to_thread`-bridge ceremony from the 21 existing + 11 added tests at HEAD `9b8a36c`).

**OPERATOR DECIDES.** Per `systems-architect` §4A.4: this is a recommendation, not a decision. Operator selects Q1 = (a) / (b) / (c) / (d) at the AskUserQuestion ratification turn. The Q2–Q5 recommendations follow Q1 (each is internally consistent under any Q1 choice; Q6 scope-widening is independent of Q1).

### 7.5 Status transition

PROPOSING → **ready-for-operator-ratification** at this commit. Next session opens with operator AskUserQuestion on Q1 (4 options) + Q6 disposition (file Class 3 informational addendum vs defer to Q6 follow-on arc). Post-ratification: PROPOSING → RATIFIED → APPLIED at the resumed `phase-7-implementation` arc closing landing.

---

*End of fork record. Status: PROPOSING → ready-for-operator-ratification. systems-architect mode 3 recommendation appended; operator decides at AskUserQuestion turn.*
