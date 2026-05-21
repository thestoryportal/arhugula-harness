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

*End of fork record. Status: PROPOSING. Awaiting systems-architect mode 3 recommendation + operator ratification.*
