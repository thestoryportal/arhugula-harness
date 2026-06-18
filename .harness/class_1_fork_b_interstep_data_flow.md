# Class 1 Fork — B-INTERSTEP (inter-step DATA-flow channel: the shared run-context a dispatcher reads)

**Filed:** 2026-06-18 · R-FS-1 standalone `B-*` arc **B-INTERSTEP** (surfaced by U-CP-87 / arc #13; spine ledger `.harness/beyond-mvp-capability-boundary-ledger.md` line 43, registered `Rec: BUILD (runtime arc; design-fork-first per X-AL-3)`). Bundled-absorption posture: runtime spec **v1.58 → v1.59** (NEW §14.21 C-RT-29 — a new optional run-scoped surface + a `RuntimeConfig` opt-in flag + a `RunResult`-adjacent dispatcher read) + `harness-runtime/src` + `harness-cp/src` (driver record site). Class 1 (X-AL-3 spec **surface extension** on a cleared spec — a genuinely NEW H_T capability: inter-step data flow, which `workflow_driver` §25.11 + the spine ledger both flagged as design-fork-first). Design back-flow **FULL-SPEC-pre-authorized** (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`).

**Status:** ✅ RESOLVED + design decided — drives the impl. **NO operator gate.** The change is **additive + operator-opt-in** (default `RuntimeConfig.inter_step_data_flow=False` → `ctx.inter_step_output_channel is None` → the driver records nothing + the LLM dispatcher injects nothing → **byte-identical to pre-v1.59**) and sacrifices **no committed invariant** — the `StepDispatcher.dispatch` signature is UNCHANGED (the channel is a run-scoped surface read off `ctx`, never a per-call parameter), and the C-CP-25 §25.3.3.4 *step-body-opaque-to-driver* invariant is PRESERVED (the driver records the dispatcher's already-produced opaque output Mapping; it never introspects or mutates the frozen `step_payload`). The mechanism is the one `workflow_driver` §25.11 itself named — *"a shared run context the dispatcher reads"* — so this is impl-of-a-design-anticipated surface, not a novel architecture. No nameable cross-domain tension (a runtime/dispatcher data-flow carrier + a CP-driver record call) → advisor, **not council** (§10.9 discriminator applied explicitly). Adopt-and-note per workspace `CLAUDE.md` §12.4.1 + `[[feedback-gate-only-on-meaningful-architecture-change]]`.

---

## §1 The fork — the driver threads NO data between steps, for any topology

At HEAD the workflow driver carries control flow between steps but **no data**:

- `SINGLE_THREADED_LINEAR` builds `accumulated[step_id] = dict(step_output)` for the terminal `final_state`, but **never passes it into a subsequent `dispatch(...)`** (`workflow_driver.py` §25.3.3.7).
- The `StepDispatcher.dispatch(binding, step, *, step_context)` Protocol carries **no prior-output parameter** — and `StepExecutionContext` is metadata-only (its docstring: *"carries metadata about the step's execution environment, NOT step body content"*, preserving §25.3.3.4).
- So in **EVALUATOR_OPTIMIZER** — the load-bearing case — the evaluator never *sees* the generate draft and the regenerate never *sees* the evaluator's feedback. The §25.11 "regenerate-with-feedback" content flow is, at the driver, **control-flow only** (the loop re-dispatching the generate step IS the regenerate; the data does not flow).

The `workflow_driver.py` §25.11 comment names this gap precisely and prescribes the mechanism:

> Inter-step data flow is ... a runtime/dispatcher concern (**a shared run context the dispatcher reads**, or B4 per-step prompt composition), the SAME for every topology — not a B1 EO driver concern.

The spine ledger (line 43) classifies it: *"threading it via `StepExecutionContext`/the dispatcher Protocol would be an **X-AL-3 spec extension**. Owner = a future runtime data-flow arc (**design-fork-first per X-AL-3**)."* This arc is that data channel.

### §1.1 The design fork — WHERE the channel lives + HOW the dispatcher reads it

The spine ledger named two mechanism candidates: *"a shared run context the dispatcher reads, **or** B4-adjacent per-step input composition."* B4 (per-step prompt) is already built and threads a STATIC manifest prompt, NOT dynamic prior outputs — so it does not close the data channel. The genuine fork is the **shared run-context** option, and within it:

- **Where does the channel live?** On the run context, as a by-reference holder. A typed container field on the frozen `HarnessContext` would be **Pydantic-copied at `freeze()`**, silently disconnecting the driver's pre-freeze records from the dispatcher's post-freeze read (the exact CA #625 hazard, `[[new-surface-audit-hash-and-config-not-carrier]]`). → resolved by the `CostRecordAccumulator` / `ResumeContextHolder` **plain-by-reference holder** precedent.
- **How does the dispatcher reach it?** Threaded into the dispatcher at stage-5 construction (the same instance bound on `ctx`), NOT through the per-call `dispatch` signature — so the Protocol signature stays byte-unchanged (the §25.11 comment's "never prior outputs"). Exactly the `cost_record_sink=ctx.cost_record_accumulator.records` threading precedent.
- **Opt-in vs always-on?** The driver-record half is harmless, but the dispatcher-inject half **changes the dispatched payload** → it MUST be opt-in (unlike `CostRecordAccumulator`, which is always-on additive observability). Resolved as a single gate: `RuntimeConfig.inter_step_data_flow` constructs the channel only when `True`; `None` default → no record, no inject, byte-identical (the `cp_is_wiring` / `validator_framework` `object | None` operator-opt-in pattern).

These are resolved by following landed precedent, not a novel architecture — hence advisor-not-council, no operator gate.

---

## §2 Resolution — a run-scoped `InterStepOutputChannel` the driver records + the LLM dispatcher reads

### §2.1 Mechanism (smallest blast radius; precedent-faithful)

1. NEW `harness_runtime/lifecycle/inter_step_output_channel.py` — `InterStepOutputChannel`, a plain (`__slots__`, non-Pydantic) by-reference holder of `(step_id, output)` in **append order**. `record(step_id, output)` (defensive copy), `most_recent_output()` (the immediately-prior step's output), `outputs_by_step_id()` (last-wins view). Append order — NOT a step_id dict — is load-bearing: an EO loop re-dispatches the same generate `step_id`, so a dict would make `most_recent_output()` return the wrong (overwritten-in-place) value on regenerate.
2. `_MutableHarnessContext.inter_step_output_channel: Any = None` + `freeze()` threading + frozen `HarnessContext.inter_step_output_channel: InterStepOutputChannel | None = None` (the `resume_context_holder` by-ref precedent; `arbitrary_types_allowed`).
3. NEW `RuntimeConfig.inter_step_data_flow: bool = False` — opt-in. Stage 5 LOOP_INIT constructs + binds the channel only when `True`, and threads the SAME instance into `materialize_llm_dispatcher_stage(inter_step_channel=...)` (the `cost_record_sink` precedent).
4. CP `DriverContext.inter_step_output_channel: object | None` + `_record_inter_step_output(ctx, step_id, step_output)` — called at the linear `accumulated` site + the EO `_dispatch_and_buffer` (BEFORE the next dispatch). Consumed via `getattr(ctx, ..., None)` dynamic dispatch (the `cp_is_wiring` idiom — harness-cp does NOT import the runtime holder).
5. `RuntimeLLMDispatcher` gains `inter_step_channel` + injects `most_recent_output()` into the dispatched payload as a prepended `user` "Upstream step output:" message (`_inject_upstream_output`, `model_copy`) when bound + non-empty.
6. Runtime spec **v1.58 → v1.59** NEW **§14.21 C-RT-29**.

**No CP spec contract change** — `StepExecutionContext`/`StepDispatcher` are byte-unchanged (the channel is read off `ctx`, not the signature); the §25.11 comment is refreshed in the driver source (it now points at this arc, `[[stale-carry-text-disposition]]`). **No OD/IS spec change, no §5.2-hash change** — the channel is an ephemeral run-scoped carrier (the `cost_record_accumulator` precedent), not persisted state.

### §2.2 Non-vacuity is the deliverable (advisor)

Advisor (full-transcript, pre-build): *"the deliverable is the data flowing, not the channel object — a written-but-no-real-consumer channel is a hollow carrier."* So the GENUINE LLM-dispatcher consumer is built + proven against the **real provider boundary**: `test_lifecycle_llm_dispatch.py::test_inter_step_channel_injects_prior_output_into_provider_call` asserts the prior step's output reaches the actual `client.messages.create(messages=...)` call — not a test stub (`[[test-bypass-as-runtime-truth]]` avoided). The driver-record producer half is proven in a real EO driver run (`test_workflow_driver_evaluator_optimizer.py::test_evaluator_optimizer_dispatch_observes_prior_step_output` — evaluate sees the generate draft; regenerate sees the evaluator feedback). The opt-out default is proven byte-identical.

---

## §3 Scope — genuinely-complete for linear + EVALUATOR_OPTIMIZER; remaining surfaces registered (NOT silent-deferred)

Per advisor (*"lean toward all-topologies-properly or a genuinely-complete linear scope, not a half-MVP"*), v1.59 covers the two **sequential-write** topologies genuinely and completely — `SINGLE_THREADED_LINEAR` (record at the `accumulated` site) + `EVALUATOR_OPTIMIZER` (the load-bearing case the §25.11 comment + spine ledger both name). Two surfaces are **explicitly registered** as follow-on `B-*` arcs (honest, not silent — surfaced in the §14.21 spec body + the §25.11 driver comment + the spine ledger):

| Registered follow-on | Why deferred | Owner |
|---|---|---|
| **Concurrent-fan-out recording** (PARALLELIZATION siblings, ORCHESTRATOR_WORKERS, DECENTRALIZED_HANDOFF, HIERARCHICAL_DELEGATION) | Concurrent sibling writes to a shared holder violate ADR-F2 single-threaded-write; they need the #648 buffered-branch drain path (the `BufferingLedgerWriter` precedent). Note: the genuine inter-step *reads* in these topologies are sequential (orchestrator synthesis post-join), so the channel composes once recording lands on the drain path. | a follow-on R-FS-1 `B-*` arc (`B-INTERSTEP-NONLINEAR`) |
| **Cross-step resume rehydration** | On a skip-prefix resume the replayed prefix is NOT re-dispatched → a downstream cross-step consumer reads an empty channel (fresh-run ≠ resumed-run). Closing it needs the output-carrying event-history substrate (the F2 `EntryPayload` carries only a `response_hash` digest today, not the activity output) = the **`B-ENGINE-OUTPUT-REPLAY`** arc. EO's data flow lives *inside* one driver invocation's loop (atomic — no resume boundary crossed), so the wired consumer is resume-safe; cross-step *linear* data flow is fresh-run correct and resume-correct only once `B-ENGINE-OUTPUT-REPLAY` lands (a composition the spine ledger already names). | composes with **`B-ENGINE-OUTPUT-REPLAY`** |

---

## §4 Why this is X-AL-3-clean (not silent absorption)

| X-AL-3 obligation | Discharge |
|---|---|
| New H_T design surface routed to design back-flow before impl | This fork doc (Class 1) + runtime spec v1.58 → v1.59 §14.21 + clearance marker, all in the bundled-absorption PR |
| Back-flow doc co-lands with the design-substrate edit (CI guard) | This fork doc + `Spec_Harness_Runtime-v1_59-cleared-2026-06-18.md` |
| No committed-invariant sacrifice without an operator gate | None sacrificed — additive + opt-in; §25.3.3.4 + the dispatch signature PRESERVED; default byte-identical |
| Registered (not silent-deferred) residual | §3 follow-ons named in the spec body, the driver comment, + the spine ledger |

---

## §5 Decorrelated review

- **advisor (full-transcript, pre-build):** affirmed the substrate shape (by-ref holder + `object | None` opt-in); the load-bearing finding = *non-vacuity is the deliverable* (build the real consumer, not a hollow channel); flagged resume-correctness (the B-ENGINE-OUTPUT-REPLAY composition) + the all-topologies-vs-genuine-linear scope decision + the dispatcher-purity check (no cleared spec/ADR commits to stateless dispatchers — `cost_record_sink` already makes the LLM dispatcher a reader of run-scoped state).
- **out-of-family Codex (pre-merge, on the diff):** pending at PR-open.

## §6 Gates (impl)

pyright 0/0/0 (changed files) · ruff · the genuine consumer + producer + channel-unit + regression tests green · full harness-runtime + harness-cp non-e2e suites (pre-push). Bundled-absorption: runtime spec v1.59 §14.21 + this fork doc + clearance marker + `harness-runtime`/`harness-cp` impl + by-execution tests + spine-ledger BUILT + arc-and-unit-map §5 + roadmap.html.
