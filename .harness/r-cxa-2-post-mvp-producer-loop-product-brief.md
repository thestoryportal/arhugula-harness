---
title: R-CXA-2 Post-MVP Producer-Loop Product/Design Brief
status: design-brief (post-MVP loop architecture; specifies (a)-shaped producers conditioned on operator post-MVP scope confirmation — NO runtime code, NO design-substrate edit in this arc)
created: 2026-06-08
posture: design-phase (`.harness/**` only — NO `design-substrate/**` edits in this arc; spec/plan amendments are SPECIFIED here, APPLIED in a later arc)
roadmap: R-CXA-2-cp-is-seam (stays STILL-BOUNDED until operator authorizes the build per §1.3)
parent: r-cxa-1-2-producer-seam-spec.md (the compact decision anchor; this brief is its post-MVP §3/§4 deep-dive)
extends: r-cxa-1-2-producer-seam-spec.md §3 (HITL), §4 (engine pause/resume), §5 (governance)
forks_ratified:
  - class_1_fork_u_cp_78_pause_captured_type_impedance.md (Reading A)
  - class_2_fork_r_cxa_2_producer_loop_ownership.md (DP-1(c), DP-2(c), DP-3(a))
grounded_at_head: 22a7df4 (origin/main, 2026-06-08; ff from 7ae493d the seam-spec/fork HEAD)
---

# R-CXA-2 Post-MVP Producer-Loop Product/Design Brief

*Specifies the post-MVP **producer-loop architecture** for the three CP→IS composers that R-CXA-2 cannot non-hollowly wire at MVP: `cp.hitl-tool-call-rewriting` (HITL model-driven tool loop), `cp.pause-captured` + `cp.resume-attempted` (engine recovery loop). The compact decision anchor is `r-cxa-1-2-producer-seam-spec.md`; this brief is the larger post-MVP deep-dive the operator recommended splitting out. It carries forward the ratified forks (U-CP-78 Reading A; DP-1/2/3) and lays a staged path toward a real implementation plan. **No runtime code is authored; no `design-substrate/**` is edited.** The spec/plan amendments this brief identifies are SPECIFIED for a later apply-arc.*

---

## §0. Relationship to the seam spec, and the (c)→(a) reframe

`r-cxa-1-2-producer-seam-spec.md` (the seam spec) established **why** R-CXA-2 must not be hollow-wired and classified each producer gap into B1/B2/B3 buckets. Its §3–§4 specified the producer *fields, idempotency, and acceptance criteria*; it deliberately left the **loop architecture** ("the inner-loop design surfaced at DP-1", "gated on DP-2") to a follow-on arc. **This brief is that follow-on arc.** It does not restate the seam spec; it deepens §3/§4 into implementable loop designs and sharpens the §5 governance determination.

**The reframe (read this carefully — it is the load-bearing governance posture).** The two forks were ratified 2026-06-08 as **bounded-residual defers with explicit re-open triggers**:

- **DP-1(c)** — defer the HITL model-driven inner loop; *"Re-open only when an actual model-emitted tool-call loop is in scope."*
- **DP-2(c)** — defer the engine recovery loop; *"Re-open when a real event-sourced replay, reconciler, WAL-segment, or engine-native-pause recovery loop lands."*
- **DP-3(a)** — *contingent future rule*: when a real recovery loop exists, it supplies stable opaque `pause_event_id` / `resume_event_id` and a replay-safe `resume_attempt_count`.

The DP-1/DP-2 ratifications were two-branch: **`(a)` IF model-driven tool-use / multi-EngineClass recovery is in scope; `(c)` otherwise.** The operator's "push the harness past MVP" directive is exactly the **re-open signal** the `(a)` branch always pointed to. This brief therefore specifies the **`(a)`-shaped** loops.

> **`[HIGH]` Posture guard (non-negotiable).** This brief is a *conditional design specification*. It does **not** re-ratify the forks, does **not** flip the roadmap selector, and does **not** update the dashboard disposition. **R-CXA-2 stays `STILL-BOUNDED`** until the operator explicitly authorizes the build (§1.3). Authoring the `(a)` design is squarely inside the ratified two-branch structure (we are writing the artifact the `(a)` branch named); declaring R-CXA-2 "buildable/closeable" is not — that needs the operator's build authorization, which this brief surfaces rather than assumes.

---

## §1. Scope, non-goals, and the conditional precondition

### §1.1 In scope (the four Must-Address surfaces)

1. **HITL model-driven tool loop** for `cp.hitl-tool-call-rewriting` (DP-1(a)) — §2.
2. **Engine recovery loop** for `cp.pause-captured` + `cp.resume-attempted` (DP-2(a) + DP-3(a)) — §3.
3. **U-CP-78 Reading A** type-fix implications — §4.
4. **Governance determination** + staged path to an implementation plan — §5 + §6.

### §1.2 Non-goals (handoff, preserved verbatim in intent)

- No runtime code; no placeholder/hollow producer wiring; no collapse of workflow-layer pause/resume into engine-layer; R-CXA-1 not reopened except for contrast; substitution-ledger counts untouched; **no `design-substrate/**` edit** (spec/plan amendments are *specified* here, *applied* later). Compliance table at §10.

### §1.3 The conditional precondition (the one genuine operator gate)

The brief's `(a)` designs are **conditioned on the operator confirming post-MVP scope is genuinely open** for: (i) model-driven multi-tool agentic turns, and/or (ii) multi-`EngineClass` recovery. The handoff signals both. The two loops are **independent** (§6.1) — the operator may authorize one, both, or neither.

| If the operator… | Then R-CXA-2 selector… |
|---|---|
| authorizes building the HITL loop and/or recovery loop | transits `STILL-BOUNDED` → the relevant impl arc opens; the ratified `(c)` becomes a recorded *historical* disposition superseded by the `(a)` build authorization |
| wants the design on the shelf (spec, don't build yet) | stays `STILL-BOUNDED`; this brief is the durable design record; re-open trigger remains armed |

No silent flip either way. This is the AskUserQuestion-worthy decision — surfaced, not pre-decided.

---

## §2. HITL model-driven tool loop (DP-1(a))

**Target composer (LANDED + tested, zero production caller):** `RuntimeCpIsWiring.emit_hitl_tool_call_rewriting_state_ledger_entry(*, workflow_id, step_id, tool_call_id, semantic_variant_binding_id, rewritten_tool_call: RewrittenToolCall, actor)` → `cp.hitl-tool-call-rewriting` (CP composer `hitl_as_tool_call_rewriting.py:249`; runtime wrapper `cp_is_wiring.py:274`).

### §2.1 Where the loop lives in the runtime architecture `[HIGH]`

**A NEW runtime-axis primitive — sibling to `RuntimeToolDispatcher`** (`harness-runtime/.../lifecycle/runtime_tool_dispatcher.py:423`), sitting *between* `RuntimeLLMDispatcher.dispatch` (`llm_dispatch.py`, C-RT-15 §14.5) and the per-tool-call `RuntimeToolDispatcher.dispatch` (C-RT-19 §14.9).

**This is NOT an unprecedented new execution mode.** The committed design already admits a model-driven tool-use inner loop: runtime spec **§14.5.1 / §14.12** (Memory-tool CRUD) specifies a *"SDK tool-use → tool-result inner loop"* inside an INFERENCE_STEP, with mechanism deferred to implementation discretion — option **β** is verbatim *"Harness-authored inner loop wrapping the `messages.create` call. Composer dispatches initial request, polls response for `tool_use` content block …, executes the callback, formats `tool_result` content block, re-dispatches until non-…-tool-use response"* (`Spec_Harness_Runtime_v1.md:2693`). The HITL-rewrite loop is **that same inner-loop pattern generalized** from memory-CRUD callbacks to arbitrary model-emitted tool calls, with the C-CP-17 §17.2 rewrite gate inserted before each tool dispatch.

> **`[HIGH]` Loop home = the INFERENCE_STEP inner loop, NOT a new step-kind.** Framed as the inference dispatcher's inner loop (mirroring §14.12), the HITL loop fits the existing `StepKind` enum (`workflow_driver_types.py:74-78`: `DECLARATIVE_STEP / INFERENCE_STEP / TOOL_STEP / HITL_STEP / SUB_AGENT_DISPATCH`, **closed at cardinality 5**). It does **not** require a new step-kind. (If a future design wants a *dedicated* "agentic-turn" step-kind, that is a Workflow §4.1.2 Class-2 revision of §5.2 — a CP-spec amendment, escalation-gated at §5.)

**Discriminator vs. the discouraged DP-1(b).** DP-1(b) ("fold the rewrite gate into the single-dispatch TOOL_STEP path") gates *one manifest-declared* tool call — meaningful HITL, but **not** model-driven *iteration*; the seam spec / fork flagged it as risking a hollow seam. DP-1(a) is the real loop: the **model** decides which tools to call within the turn, and each model-emitted call passes the rewrite gate. This brief specs (a). It also notes a legitimate hybrid: (a) for INFERENCE_STEP model-driven turns AND the same rewrite gate reused at the TOOL_STEP path for manifest-declared tool calls — both are valid firing sites for `rewrite_tool_call`; only (a) is "model-driven."

### §2.2 Control-flow — answering the 10 HITL sub-bullets explicitly

Pseudo-control-flow of the inner loop (one INFERENCE_STEP turn):

```
response = RuntimeLLMDispatcher.dispatch(binding, step, step_context)   # C-RT-15; LLM emits tool_use blocks
while response has tool_use content blocks:
    for tc in response.tool_use_blocks:                                 # model-emitted tool calls
        tool_call_id = tc.id                                            # (b) STABLE provider tool_use id — NOT minted
        proposed = ProposedAction(action_kind=…, payload=…, brief=…)    # (c) handoff_context.py:79 (3 fields)
        required = hitl_required(GateLevelInput(…))                     # (d) U-CP-43 predicate, gate_level_rule.py:195
        rewritten = registry.rewrite_tool_call(                         # (e) hitl_placement.py:187
            tool, server, persona_tier, proposed,
            cell_synchrony_class, cross_trust_boundary_state, required)
        if rewritten.hitl_required:                                     # a REAL rewrite occurred
            emit_hitl_tool_call_rewriting_state_ledger_entry(           # (f) cp_is_wiring.py:274
                workflow_id, step_id, tool_call_id,
                semantic_variant_binding_id=rewritten.variant.value,    # (settled: v2.39 Reading B)
                rewritten_tool_call=rewritten, actor=…)
            gate = RuntimeHITLGateComposer(...).dispatch(              # (i) runtime composer body — OPENS before dispatch
                binding, step, step_context=step_context)
            apply gate.response  # APPROVE→dispatch; EDIT→dispatch edited_proposal; REJECT→skip; RESPOND→feed text back
        else:
            pass                                                        # (g) NO §16.5 emission — the no-op
        tool_result = RuntimeToolDispatcher.dispatch(…)                 # unless REJECT
        feed tool_result back to the model
    response = RuntimeLLMDispatcher.dispatch(… updated transcript …)    # re-dispatch until no tool_use blocks
```

| # | Must-Address sub-bullet | Answer (grounded) |
|---|---|---|
| (a) | Where the loop lives | New runtime primitive sibling to `RuntimeToolDispatcher`, as the INFERENCE_STEP inner loop generalizing §14.12 option β (§2.1). |
| (b) | Stable tool-call IDs | Source `tool_call_id` from the provider's `tool_use` block `id` (Anthropic `tool_use.id` / OpenAI `tool_call.id`). **Never mint a fresh per-attempt uuid** — that defeats idempotency dedup (§2.3). Replay-stability requires the turn (with its ids) be journaled, not re-sampled. |
| (c) | tool call → `ProposedAction` | Construct `ProposedAction(action_kind: ActionKind, payload: ActionPayload, brief: SubAgentBrief|None)` (`handoff_context.py:79`, exactly 3 fields). The `tool_use` name+args map to `action_kind` + `payload`; `brief` populated only for `SUB_AGENT_DISPATCH`. The exact `tool_use → ActionKind/ActionPayload` mapping is the one genuinely-new contract the impl arc authors (§8 OQ-1). |
| (d) | Where `hitl_required` is evaluated | Upstream of the rewrite gate, via U-CP-43 `hitl_required(GateLevelInput) -> bool` (`gate_level_rule.py:195`; runtime consumption surface `hitl_required_consumption.py`). The loop builds the `GateLevelInput` (4-axis multiplicative gate) per tool call. |
| (e) | Where `rewrite_tool_call(...)` is invoked | After `hitl_required` is computed, **immediately before dispatch** — "rewrite is the last gate before the action surface" (C-CP-17 §17.2; `hitl_as_tool_call_rewriting.py:176`). `RuntimeHITLPlacementRegistry.rewrite_tool_call` (`hitl_placement.py:187`) pure-composes `rewrite_tool_call_to_hitl`. |
| (f) | When the composer fires | Only when `rewritten.hitl_required is True` (a real rewrite). `semantic_variant_binding_id = rewritten.variant.value` (StrEnum value; **B2-settled, runtime plan v2.39 Reading B** — do not re-derive). |
| (g) | No-op semantics | `hitl_required is False` → `rewrite_tool_call_to_hitl` returns the call unchanged (`variant=None`, `response_palette=None`, `hitl_as_tool_call_rewriting.py:185-192`) → **NO §16.5 emission**. The loop dispatches the tool directly. |
| (h) | Replay / idempotency | §2.3. |
| (i) | Approval/HITL gate × tool dispatch | The gate opens **before** `RuntimeToolDispatcher.dispatch`. **Production gate body = the runtime `RuntimeHITLGateComposer`** (`Spec_Harness_Runtime_v1.md` §14.8) — *not* the CP-side `hitl_gate(...)` signature (`harness-cp/.../hitl_placement.py:204`, `HITLGateResult`), which is a **pure-signature surface closing the historical `NotImplementedError`** and delegates its body to the runtime composer (review finding S-2: wire `RuntimeHITLGateComposer`, not the CP signature). The 4-response palette decides dispatch: APPROVE→dispatch; EDIT→dispatch `edited_proposal`; REJECT→skip (record rejection); RESPOND→feed `response_text` back to the model. `DURABLE_ASYNC` variants pause the workflow (HITL_INVOCATION_PENDING) and resume via `ResumeContext.hitl_response` (one-shot per §14.8.8). |
| (j) | Test/e2e proof shape | §2.4. |

### §2.3 Stable tool-call IDs, replay, idempotency `[HIGH]`

Idempotency key (verified, `hitl_as_tool_call_rewriting.py:224`): `sha256(0x1E.join(workflow_id, step_id, tool_call_id, semantic_variant_binding_id, sha256(RewrittenToolCall canonical bytes).hex()))`. Replay of the same rewrite at the same `(workflow_id, step_id, tool_call_id)` → identical key → IS `IDEMPOTENT_NOOP`.

> **`[HIGH]` Cross-cutting finding — replay-safety couples the HITL loop to *journaling*, not to the recovery loop.** Because LLM turns are non-deterministic, "replay" of a HITL-gated turn is only idempotent if the *original* model turn (with its `tool_use` ids) is **journaled** (IS state ledger / engine event-history, ADR-F3) and *replayed*, not re-sampled. The idempotency-key machinery already assumes this. **This is a journaling dependency, NOT a dependency on the DP-2 engine recovery loop** — keep the two loops' dependency graphs separate (§6.1). The HITL loop depends on `{journaled turn + U-CP-43 + rewrite gate}`; it must not be gated behind recovery.

### §2.4 Acceptance criteria + test/e2e proof shape (R-CXA-2 HITL)

AC (gated on operator build authorization per §1.3): a production inner loop iterates model-emitted tool calls; fires the composer with `semantic_variant_binding_id = variant.value` when `hitl_required`; emits **nothing** when not; replays to `IDEMPOTENT_NOOP` on stable `tool_call_id`; the gate is consulted before dispatch.

Tests (prove a *producer*, beyond the existing composer-unit suite `test_hitl_tool_call_rewriting_state_ledger_emission.py`):
- `test_hitl_rewrite_producer_fires_when_hitl_required` — drive a fixture LLM emitting ≥2 tool calls (one HITL-required, one not) through the loop; assert exactly one `cp.hitl-tool-call-rewriting` entry in `state.jsonl`, chain integrity intact (C-IS-06).
- `test_hitl_rewrite_producer_noop_when_not_required` — the non-required call emits zero entries.
- `test_hitl_rewrite_producer_replay_idempotent` — replay the journaled turn → `IDEMPOTENT_NOOP`; ledger length unchanged.
- `test_hitl_rewrite_tool_call_id_is_stable_from_model` — `tool_call_id` equals the provider `tool_use.id`, not a minted uuid.
- `test_hitl_gate_consulted_before_dispatch` — REJECT response → tool is not dispatched.

---

## §3. Engine recovery loop (DP-2(a) + DP-3(a))

**Target composers (LANDED + tested, zero production caller):**
- `emit_pause_captured_state_ledger_entry(...)` → `cp.pause-captured` (`pause_resume_protocol.py:864`; wrapper `cp_is_wiring.py:308`) — **re-typed by U-CP-78 Reading A**, see §4.
- `emit_resume_attempted_state_ledger_entry(...)` → `cp.resume-attempted` (`pause_resume_protocol.py:967`; wrapper `cp_is_wiring.py:340`).

### §3.1 What owns the engine recovery loop `[HIGH]`

**A NEW runtime-axis engine-recovery primitive — DP-2(a).** It binds an `EnginePauseResumeSubstrate` and drives the engine-layer **free functions** `capture_pause_snapshot` / `attempt_resume` (`pause_resume_protocol.py:252`/`:272`). It is **NOT** an extension of `workflow_driver.py` (DP-2(b), discouraged) — the workflow driver correctly owns the *workflow-layer* `cp.pause-resume-protocol` (C-CP-26; `workflow_driver.py:582/808/965`); folding the engine layer into it blurs the deliberate **C-CP-22 (engine) vs C-CP-26 (workflow)** two-layer distinction (`pause_resume_protocol_types.py:21-28`).

The loop init/composition site is the bootstrap **stage-5 LOOP_INIT** (`bootstrap/stage_5_loop_init.py`) or a dedicated recovery-loop factory it materializes; this is where the substrate is bound and the recovery cycle is driven.

### §3.2 Which EngineClass / ResumptionKind cases are in scope — provider-free first `[HIGH]`

The 5 `EngineClass` ↔ `ResumptionKind` bindings (1:1, `engine_class.py` / `resumption_kind.py`, C-CP-07/08):

| EngineClass | ResumptionKind | Substrate (C-CP-07 §7.1) | Recovery-loop tractability |
|---|---|---|---|
| `PURE_PATTERN_NO_ENGINE` | `JOURNAL_RESUME` | **F2** (filesystem-journal + state-ledger + idempotency-key) — *harness-owned* | **FIRST target** — provider-free; the harness already owns F2 (the very IS substrate R-CXA-2 writes to). Framework-pull-clean. |
| `SAVE_POINT_CHECKPOINT` | `SAVE_POINT_RESUME` | DBOS / LangGraph checkpointer | SECOND — harness "composes lease+dedup+resumption" atop save points; the only class with *any* production today (binary RESUMPTION, `workflow_driver.py:725-746`). Save-point substrate is external (LangGraph I-6-named). |
| `EVENT_SOURCED_REPLAY` | `ENGINE_REPLAY` | Temporal / Restate / DBOS | Deployment-time **adapter** class; candidates deferred per **C-CP-07 §7.4**. |
| `RECONCILER_LOOP` | `RECONCILER_CONVERGE` | K8s CRD reconciler / etcd | Deployment-time adapter; deferred per §7.4. |
| `WAL_SEGMENT` | `SEGMENT_REPLAY` | Kafka-style WAL | Deployment-time adapter; deferred per §7.4. |

> **`[HIGH]` Staging constraint (corrected I-6 framing).** Start with `PURE_PATTERN_NO_ENGINE` over F2 — it is the one class the harness owns end-to-end with **zero external framework**. `EVENT_SOURCED_REPLAY` / `RECONCILER_LOOP` / `WAL_SEGMENT` bind external engines (Temporal / K8s / Kafka). The harness **must not vendor those frameworks as its own layer** (I-6: no `temporal` / `langgraph` / `prefect` / …); per **C-CP-07 §7.4** their substrate candidates are *deferred to implementation discretion*, and they compose via **deployment-time adapters** (a thin `EnginePauseResumeSubstrate` impl wrapping the operator-deployed engine's native pause/resume), not vendored dependencies. So the recovery-loop's *contract* is engine-agnostic (the free-function Protocol); only the bound substrate varies by deployment. `PauseReason.ENGINE_NATIVE_PAUSE` (`pause_resume_protocol.py:55`) is specifically the event-sourced-replay/reconciler path.

`PauseReason` 4-class (verified `:49`): `HITL_INVOCATION_PENDING`, `CROSS_DEPLOYMENT_BRIDGING_ARC_PAUSE`, `OPERATOR_INITIATED_PAUSE`, `ENGINE_NATIVE_PAUSE`. `ResumeOutcomeKind` 4-class (verified `:88`): `RESUME_CLEAN`, `RESUME_AFTER_REVALIDATION`, `ABORT_REVALIDATION_FAILED`, `ABORT_SNAPSHOT_CORRUPTED`.

### §3.3 When `bind_engine_pause_resume_substrate` / `capture_pause_snapshot` / `attempt_resume` fire

- **`bind_engine_pause_resume_substrate(substrate)`** (`pause_resume_protocol.py:154`) is a **process-local `@contextmanager`**; the free functions fail closed (`EnginePauseResumeSubstrateNotBoundError`) when unbound. The recovery loop binds a concrete substrate for the duration of the recovery cycle — `DeterministicEnginePauseResumeSubstrate` for harness-owned classes (tests + F2), a deployment adapter for external-engine classes.
- **`capture_pause_snapshot(workflow_id, pause_reason) -> PauseEvent`** fires when the engine captures a recovery pause (crash-recovery / replay-boundary / engine-native pause). The loop then calls `emit_pause_captured_state_ledger_entry(...)`.
- **`attempt_resume(attempt: ResumeAttempt) -> ResumeOutcome`** fires when the loop attempts resumption. The loop then calls `emit_resume_attempted_state_ledger_entry(...)` on **both** success and `ABORT_*` outcomes (§3.6).

### §3.4 Identity generation — DP-3(a), and the Reading-A refinement `[MODERATE]`

DP-3(a) ratified: the recovery loop supplies stable opaque `pause_event_id` / `resume_event_id` and a replay-safe `resume_attempt_count` — **no type-field extension, no spec amendment** (mirroring the HITL `tool_call_id` "caller-provided opaque" precedent). These are the loop's own state, not invented engine-type fields.

> **`[MODERATE]` Refinement DP-3(a) admits (impl-arc open question OQ-2, NOT a re-litigation).** U-CP-78 Reading A re-types `emit_pause_captured_state_ledger_entry` to consume a `PauseEvent`, which **already carries `pause_audit_entry_id: EntryID`** (`pause_resume_protocol.py:73`; minted by the substrate at `capture_pause_snapshot`, e.g. `DeterministicEnginePauseResumeSubstrate` `:202-216`). Sourcing the `pause_event_id` disambiguator *from* `pause_event.pause_audit_entry_id` is still "recovery-loop/substrate-context-supplied" (it just names *where* the opaque id comes from — consistent with DP-3(a)) and may let the separate `pause_event_id` kwarg **collapse** entirely, leaving only `resume_event_id` + `resume_attempt_count` as genuinely loop-minted. The impl arc should evaluate this collapse; it simplifies the composer signature without contradicting the ratified decision. The sibling `cp.resume-attempted` has no equivalent field on `ResumeOutcome`, so `resume_event_id`/`resume_attempt_count` remain loop-supplied.

### §3.5 Where recovery state persists `[HIGH]`

**The IS state ledger (F2), via the very CP→IS seam R-CXA-2 closes — not in-process memory.** The engine free-function docstrings already specify this: `capture_pause_snapshot` writes `pause_audit_entry_id` via the **U-IS-11 F2 append** (`response_hash = sha256(canonicalize(PauseEvent))`, `:257-262`); `attempt_resume` **reads the pause snapshot via the U-IS-12 bounded-read** keyed on `paused_workflow_id` and integrity-verifies it via the U-IS-09 `prior_event_hash` chain (`:275-281`).

> **`[HIGH]` Test-fixture vs production persistence.** `DeterministicEnginePauseResumeSubstrate` stores pause events in an **in-memory dict** (`self._pause_events: dict[str, PauseEvent]`, `:196`). That is a *test/deterministic fixture* — it does **not** survive a process crash, which would defeat crash-recovery. A production recovery loop must persist pause/resume state durably in the IS ledger (the `pause_audit_entry_id` *is* the durable handle; resume reads it back). The loop-minted `pause_event_id`/`resume_event_id`/`resume_attempt_count` (§3.4) must likewise be journaled so replay re-derives the same idempotency keys. **This couples the recovery loop's correctness to the CP→IS durable-write seam** — i.e., R-CXA-2's own emission path is the persistence substrate.

### §3.6 How abort outcomes are recorded `[HIGH]`

`emit_resume_attempted_state_ledger_entry` fires on **all four** `ResumeOutcomeKind` values, including `ABORT_REVALIDATION_FAILED` / `ABORT_SNAPSHOT_CORRUPTED` — **failure is a recorded outcome, not a swallowed exception** (composer AC). `ResumeOutcome.outcome_kind` is consumed directly (no derivation gap). Note the cross-loop link: `ABORT_REVALIDATION_FAILED` "escalates to HITL" (`:97`) — i.e., a failed resume can hand off to the §2 HITL gate, which is the only place the two loops legitimately meet at the *escalation* boundary (still not a build dependency).

### §3.7 Replay safety + idempotency

Idempotency keys (verified): `_pause_captured_idempotency_key` = `sha256(0x1E.join(workflow_id, step_id, pause_event_id, snapshot_hash, outcome_hash))` (`:833`) — **Reading A re-derives the suffix from `PauseEvent` canonical bytes + `pause_audit_entry_id`** instead of `PauseSnapshot.snapshot_hash` (§4). `_resume_attempted_idempotency_key` = `sha256(0x1E.join(workflow_id, step_id, resume_event_id, resume_attempt_count, outcome_hash))` (`:938`). Dedup holds **iff** the loop supplies stable ids + a consistent `resume_attempt_count` (§3.4) — a fresh-uuid-per-call defeats `IDEMPOTENT_NOOP`.

### §3.8 Acceptance criteria + test/e2e proof shape (R-CXA-2 engine)

AC (gated on §1.3 + U-CP-78 Reading A applied): a production recovery loop binds the engine substrate and drives `capture_pause_snapshot`/`attempt_resume` at real recovery sites (start `PURE_PATTERN_NO_ENGINE`/F2); supplies stable replay-safe ids (§3.4); the type seam is resolved (§4) so engine output flows to the composer; both composers fire with chain integrity; `cp.resume-attempted` fires on `ABORT_*` too; replay → `IDEMPOTENT_NOOP`.

Tests (beyond the composer-unit `test_pause_resume_workflow_layer_state_ledger_emission.py`):
- `test_engine_recovery_loop_emits_pause_captured` — bind `DeterministicEnginePauseResumeSubstrate`; drive capture→emit; assert `cp.pause-captured` entry + chain integrity.
- `test_engine_recovery_loop_emits_resume_attempted_on_abort` — force `ABORT_SNAPSHOT_CORRUPTED`; assert `cp.resume-attempted` fires with that outcome.
- `test_pause_captured_consumes_real_engine_output` — **the U-CP-78 Reading A type-seam guard**: `capture_pause_snapshot` output (`PauseEvent`) flows into the composer with **no** runtime-axis field synthesis.
- `test_engine_pause_resume_replay_idempotent` — replay with the same loop-minted ids → `IDEMPOTENT_NOOP`.
- `test_recovery_state_persists_across_process` (PURE_PATTERN/F2) — pause state read back from the IS ledger, not in-process memory.

---

## §4. U-CP-78 Reading A — type-fix implications `[HIGH]`

**Ratified (`class_1_fork_u_cp_78_pause_captured_type_impedance.md`, Reading A):** the engine-layer `cp.pause-captured` composer must consume the engine-layer producer's output type **`PauseEvent`**, not the workflow-layer **`PauseSnapshot`**.

**Why it is owed.** The engine free function `capture_pause_snapshot(...) -> PauseEvent` (5-field: `paused_at`, `pause_reason: PauseReason`, `state_summary_snapshot`, `external_refs_captured`, `pause_audit_entry_id`; `:59`) cannot feed `emit_pause_captured_state_ledger_entry(..., pause_snapshot: PauseSnapshot, ...)` — `PauseSnapshot` is the 8-field *workflow-layer* type (`pause_resume_protocol_types.py:92`, has `snapshot_hash` / `state_ledger_anchor` / `run_id` / `step_index` / `WorkflowPauseReason`). Synthesizing a `PauseSnapshot` from a `PauseEvent` at the runtime axis would invent fields not present on the engine surface — the X-AL-3 silent extension the v2.34 AC #8 flag forbids. (The sibling `emit_resume_attempted_state_ledger_entry` consumes `ResumeOutcome`, which `attempt_resume` *actually* returns — **no impedance**; the defect is `pause-captured`-specific.)

**The implementation contract Reading A authorizes (from the ratified fork):**
1. Re-type `emit_pause_captured_state_ledger_entry(..., pause_event: PauseEvent, ...)`.
2. Re-derive the idempotency suffix from canonical `PauseEvent` bytes + `pause_audit_entry_id` (replaces `PauseSnapshot.snapshot_hash`; equivalent dedup strength).
3. Add `test_pause_captured_consumes_real_engine_output`.
4. **Preserve C-CP-22 / C-CP-26 separation** — do **not** collapse `PauseReason` into `WorkflowPauseReason`; do **not** add a lossy adapter; do **not** invent `PauseSnapshot` fields at runtime.

**Spec / plan / code surface (the "amendment locus" the handoff asks for) `[HIGH]`:**

| Surface | Change | Authority |
|---|---|---|
| **CP spec** (`design-substrate/Spec_Control_Plane_v1_*.md`) | §16.5.4/§16.5.5 row **U-CP-49** outcome-bytes recipe re-stated for `PauseEvent`; the C-CP-22 §22.1 composer-input type. **CP spec amendment** (delta bump). | fork §0 + Reading A |
| **CP code** (`harness-cp/.../pause_resume_protocol.py`) | composer signature `:864` + idempotency-key segment `:833` + tests. | apply-arc |
| **Runtime plan** (`Implementation_Plan_Harness_Runtime_v2_*.md`) | the engine recovery-loop producer arc that calls the re-typed composer (new U-RT unit). | apply-arc |

**Determination: BOTH a CP spec amendment AND a runtime plan amendment** (with the CP code change between them). It is *not* runtime-plan-only — the composer's input *type* is a CP-spec §16.5 contract. This is the one surface in the R-CXA-2 producer arc that touches `design-substrate/**` → it is a **bundled-absorption arc** (root CLAUDE.md §11.4) owing a **clearance marker** at the spec-amendment PR.

---

## §5. Governance determination `[HIGH]`

**Question (handoff #4):** does post-MVP R-CXA-2 require a product brief only / runtime-CP spec amendment / impl plan / ADR escalation / combination? **Be explicit.**

**Answer: a COMBINATION — (this) design brief + CP spec amendment + runtime plan amendment + implementation plan; NO new foundational ADR — *conditionally*, with one named escalation gate.**

> **Conditional, not settled (review finding S-4).** The "no new ADR" conclusion rests **entirely** on the premise that §14.12's *memory-CRUD* inner loop legitimately generalizes to *arbitrary* model-driven tool use. **That premise IS the §5.1 E2 risk** — so the verdict is **"conditionally sound": no ADR *iff* the §5.1 (E1)/(E2) gate clears at impl-planning (OQ-3).** If the generalization is judged a foundational execution-model shift (E2), the answer flips to "fork → ADR." Read §5.1 as load-bearing, not a footnote.

| Vehicle | Needed? | Why |
|---|---|---|
| **Design/product brief** | ✅ (this doc) | Specifies the `(a)` loop architecture; the workspace-native back-flow surface for "new H_T producer-loop ownership surfaced at execution time." |
| **CP spec amendment** | ✅ | U-CP-78 Reading A re-types the `cp.pause-captured` composer (CP spec §16.5.4/.5 row U-CP-49). The only `design-substrate/**` touch; bundled-absorption + clearance marker (§4). |
| **Runtime plan amendment** | ✅ | Both loops are new runtime-axis primitives → new `U-RT-NN` units in `Implementation_Plan_Harness_Runtime_v2_*.md` (HITL inner loop generalizing §14.12; engine recovery loop). DP-3(a) identities are runtime-plan-only (no type/spec extension). |
| **Implementation plan** | ✅ | The staged build (§6), authored post-brief, post-operator-authorization. |
| **PRD** | ❌ | Internal cross-axis runtime architecture; no operator-facing approval/recovery *product* surface is introduced (the HITL/pause/resume surfaces already exist; this specs their producers). |
| **New foundational ADR** | ❌ — **see escalation gate** | The primitives are ADR-committed: HITL rewrite-before-dispatch (**ADR-D5 §1.3.2** / C-CP-17 §17.2); pause/resume (**ADR-D5 §1.11** / C-CP-22/26); EngineClass/ResumptionKind (**ADR-D1** / C-CP-07/08). The model-driven tool-use inner loop is **already admitted** by the committed design (§14.5.1/§14.12 memory inner loop, option β, mechanism deferred to impl discretion). Generalizing it + inserting the rewrite gate is a runtime-lifecycle *realization* of committed design, not a foundational change. |

### §5.1 The escalation boundary (named, reviewer-verifiable) `[HIGH]`

A fork→ADR escalation becomes owed **only if**, at impl-planning, *either* of these proves true:

- **(E1) A new `StepKind` is required.** If the HITL loop cannot be expressed as an INFERENCE_STEP inner loop (per §2.1 / the §14.12 precedent) and instead needs a *dedicated* agentic-turn step-kind, that extends the cardinality-5 `StepKind` enum — a **Workflow §4.1.2 Class-2 revision of CP spec §5.2** (a CP-spec amendment). This is *still not an ADR* by itself — but it touches the manifest execution-model contract and should be reviewed against (E2).
- **(E2) The foundational execution-model stance shifts.** If generalizing the §14.12 memory-specific inner loop to *arbitrary* model-driven tool use is judged to move the harness from **declarative-workflow-manifest-driven** (C-CP-05/06 typed `WorkflowManifestEntry` + 5 typed step-kinds; CP-AL-5 "`CLAUDE.md` declarations ≠ typed `WorkflowManifestEntry`") to **agent-driven** as a foundational commitment, *that* contradicts the committed execution model and is a **Class 1 fork → ADR escalation** (locus: **ADR-F3** engine event-history + the ADD execution-model attestation; **not** ADR-D4 TopologyPattern, which governs multi-agent orchestration shape and is orthogonal to intra-agent tool iteration).

> **`[HIGH]` Why the boundary lands at the execution-model commitment, not the topology enum.** Per the probe (§0 grounding): `StepKind` is closed at 5 and the design already contemplates an inference-step inner loop (§14.12). So the *default* path is "no ADR." The genuine risk is whether arbitrary model-driven tool use is the same thing as the §14.12 memory inner loop or a broader stance change. The impl arc must make that call explicitly; if it is broader, escalate per (E2). TopologyPattern (ADR-D4) is **not** the locus — topologies describe multi-agent orchestration, the inner loop describes intra-agent tool iteration.

---

## §6. Staged implementation-plan outline (recommended) `[MODERATE]`

### §6.1 Dependency graph — the two loops are independent

```
                 ┌─ HITL loop (DP-1(a)) ── depends on: journaled turn (ADR-F3) + U-CP-43 + rewrite gate (C-CP-17)
operator         │       └─ NO dependency on the recovery loop (§2.3)
build-authz ─────┤
(§1.3)           └─ Engine recovery loop (DP-2(a)+DP-3(a)) ── depends on: U-CP-78 Reading A (§4) + substrate binding
                         └─ shares the IS-ledger journaling substrate, but is NOT a HITL-loop prerequisite
```

The loops may be built in parallel or in either order. **Do not gate HITL behind recovery** (a tempting but wrong coupling — they only share the journaling substrate and meet at the §3.6 *escalation* boundary).

### §6.2 Stages

| Stage | Scope | Touches | Gate |
|---|---|---|---|
| **S0** (this brief) | post-MVP loop architecture specified | `.harness/**` | — |
| **S1 — U-CP-78 Reading A apply** | CP spec §16.5 amendment + CP code re-type + `test_pause_captured_consumes_real_engine_output` | `design-substrate/` CP spec + `harness-cp/src` + tests | bundled-absorption + **clearance marker** (§4); precondition for any engine-layer producer (S3) |
| **S2 — HITL inner-loop runtime plan + impl** | new `U-RT-NN` (INFERENCE_STEP inner loop generalizing §14.12 + rewrite gate); `tool_use → ProposedAction` mapping (OQ-1) | runtime plan + `harness-runtime/src` + tests | §1.3 authorization; check (E1)/(E2) |
| **S3 — Engine recovery-loop runtime plan + impl** | new `U-RT-NN` recovery loop; `PURE_PATTERN_NO_ENGINE`/F2 first; loop-minted ids per DP-3(a)/OQ-2; IS-ledger persistence | runtime plan + `harness-runtime/src` + tests | §1.3 authorization; **requires S1** |
| **S4 — CXA seam absorption + R-CXA-2 close** | the 3 CP→IS Pattern-P1 seams now have real producers; CXA enumeration + roadmap selector flip | `harness-cxa` / CXA doc / roadmap | producers proven e2e (use-the-product probe, not unit-only) |

### §6.3 Per-stage proof discipline

Each producer stage closes only on an **e2e producer test** (drive the real path), not a passing composer-unit test — per `[[verification-shape-sharpened-grep-vs-e2e]]` and the seam spec's "composer ≠ producer" lesson. S4 should run a use-the-product probe (`[[use-the-product-probe-pattern]]`).

---

## §7. Research grounding + the NotebookLM gap `[HIGH]`

**Local corpus consumed (primary):** the seam spec, both ratified forks, the 2026-06-08 producer audit, and direct reads of `pause_resume_protocol.py`, `hitl_as_tool_call_rewriting.py`, `hitl_placement.py` (CP + runtime), `runtime_tool_dispatcher.py`, `handoff_context.py`, `engine_class.py`, `resumption_kind.py`, `workflow_driver_types.py`, plus `design-substrate/Spec_Harness_Runtime_v1.md` §14.5.1/§14.12 + `Spec_Control_Plane_v1_2.md` §5.2/§7.4. All symbols/line-cites in this brief were grounded at HEAD `22a7df4`. The producer-seam *design* is fully determined by the workspace's own ratified contracts.

**NotebookLM corpus query — RESEARCH GAP, marked-and-carried.** The handoff (and `class_2_fork` §DP-2 deferral note) flag a NotebookLM / harness-research-corpus query for HITL pause/resume + durable tool-loop + recovery-loop-ownership + event-sourced-replay precedent. **This query was NOT run in this arc** — the NotebookLM MCP is interactively-authenticated and unreliable in non-interactive sessions (`[[notebooklm-harness-corpus-url]]`), and chasing it risks an external-service rabbit hole. The design does not block on it (it is determined by intra-workspace contracts). **Continuation contract:** a NotebookLM query + vendor-doc retrieval is owed at the **S2/S3 impl-plan arc** to ground the loop implementations, if the operator authorizes the build (§1.3).

**Operator-named external precedents (woven, not independently re-retrieved — `[MODERATE]`, citations owed at S2/S3 per `CLAUDE.md` §10.4):**
- **OpenAI Agents SDK HITL — durable `RunState` resume** ≈ **§3.5** (where recovery state persists: serialize at the interrupt, rehydrate on resume — the harness's analogue is the IS-ledger `pause_audit_entry_id`).
- **AWS Step Functions callback task token** ≈ **§3.4 / DP-3(a)** (the durable correlation token = the loop-minted `pause_event_id` / `resume_event_id`).
- **Temporal signals / updates / wait-conditions** ≈ **§3.2** (`ENGINE_NATIVE_PAUSE` + reconciler recovery + `resume_attempt_count` retry coordination) — and exactly the framework the harness composes-with-but-does-not-vendor (I-6 / §3.2).

---

## §8. Open questions / resolved decisions

**Resolved (cite, do not re-derive):**
- HITL `semantic_variant_binding_id = rewritten_call.variant.value` — runtime plan v2.39 **Reading B** (ratified 2026-05-29).
- `cp.pause-captured` composer input type → `PauseEvent` — **U-CP-78 Reading A** (ratified 2026-06-08).
- DP-1(c)/DP-2(c)/DP-3(a) — ratified 2026-06-08; this brief specs the `(a)` branch the re-open trigger arms.
- Bootstrap provider-key secret-fetch stays excluded (Reading-D) — R-CXA-1 only, not in this brief's scope.

**Open (for the S2/S3 impl-plan arc):**
- **OQ-1** — the exact `tool_use` (provider tool-call) → `ProposedAction(action_kind, payload, brief)` mapping. The one genuinely-new contract; author at S2 (likely an AS↔CP seam touch for `ActionKind`/`ActionPayload`).
- **OQ-2** — whether `pause_event_id` collapses into `pause_event.pause_audit_entry_id` under Reading A (§3.4) — a DP-3(a)-consistent simplification to evaluate, not re-litigate.
- **OQ-3** — (E1)/(E2) escalation check (§5.1): does the general model-driven loop fit the INFERENCE_STEP inner-loop framing, or need a new `StepKind` / a foundational execution-model ADR? Make the call explicitly at S2 before building.
- **OQ-4** — the §14.12 inner-loop *mechanism* (α SDK-internal / β harness-authored / γ sibling-composer) for the HITL loop — impl discretion, but should align with whatever the memory-tool C-RT-22 arc chooses, to avoid two divergent inner-loop mechanisms.
- **OQ-5 (loop concern — review S-3a)** — **`tool_call_id` ⊥ idempotency under cross-family fallback on a *live* (non-replay) turn.** §2.3 establishes replay-safety needs the turn journaled; but a *fallback* re-dispatch to a different provider (C-CP-04) re-samples the model → **new** provider `tool_call_id`s, so the HITL-rewrite idempotency key won't dedup across the fallback boundary. Specify whether a fallback turn is a fresh turn (new ids, expected) or must preserve ids — at S2.
- **OQ-6 (loop concern — review S-3b)** — **HITL gate timeout / degradation in-loop.** A `DURABLE_ASYNC` gate that times out hits the C-CP-21 §21.6 per-persona-tier `on_hitl_timeout` degradation (`TimeoutDegradationKind`: SOLO→CONTINUE_AS_REJECT / TEAM→ESCALATE / MULTI_TENANT→ABORT). The inner loop must consume that outcome (REJECT-path / abort) — not covered in §2.2. Specify at S2.
- **OQ-7 (loop concern — review S-3c)** — **mid-loop breaker trip vs journaled-replay state.** If the retry/breaker wrapper (C-RT-16/21) trips mid-turn (after some tool calls dispatched + emitted), how does replay reconcile the partially-journaled turn? Specify the interaction of breaker-open with the journaled-turn replay invariant (§2.3) — at S2/S3.

---

## §9. Verification / tracking + roadmap/status

- **Roadmap selector UNCHANGED.** R-CXA-2 stays `STILL-BOUNDED` (§1.3). This brief is a `.harness/**` design record; it does **not** flip the selector, re-ratify the forks, or update the dashboard disposition. The selector flips only on operator build authorization (then S2/S3) or at S4 producer-proven close.
- **No clearance marker owed by THIS arc** (no `design-substrate/**` edit). A clearance marker **is** owed at **S1** (the U-CP-78 Reading A CP-spec amendment, §4) and at any later design-substrate touch.
- **X-AL-3 clean** — `.harness/**`-only; zero `design-substrate/**`, zero `harness-*/src/**` edits in this arc.
- **Substitution ledger untouched** — no count change.
- **Pointer added** to `r-cxa-1-2-producer-seam-spec.md` (§3/§4 → this brief).
- **Post-merge:** a terminating `ops: roadmap status refresh` is owed per `CLAUDE.md` §12.2.1; `recently_completed` prepends this brief PR; `next_action` re-derives (R-CXA-2 stays the next item, now with a post-MVP design record attached pending build authorization).

---

## §10. Non-goals compliance (handoff)

| Non-goal | Compliance |
|---|---|
| Do not implement code | ✅ design brief only; zero `harness-*/src/**` edits |
| Do not wire placeholder/hollow R-CXA-2 producers | ✅ producers SPECIFIED-not-built; gated on §1.3 |
| Do not collapse workflow-layer into engine-layer pause/resume | ✅ §3.1 keeps C-CP-22 (engine) vs C-CP-26 (workflow) distinct; DP-2(b) explicitly rejected |
| Do not reopen R-CXA-1 unless for contrast | ✅ R-CXA-1 referenced only for the B1-vs-B3 contrast |
| Do not change substitution ledger counts | ✅ untouched (§9) |
| Do not modify `design-substrate/**` unless arc escalates | ✅ spec/plan amendments SPECIFIED (§4, §6) for a later apply-arc; zero edits here |

## §11. See also

- `r-cxa-1-2-producer-seam-spec.md` (compact decision anchor; this brief is its post-MVP deep-dive)
- `class_1_fork_u_cp_78_pause_captured_type_impedance.md` (Reading A) · `class_2_fork_r_cxa_2_producer_loop_ownership.md` (DP-1/2/3)
- `class_1_tension_u_rt_35_cp_is_wiring_gaps.md` (CLOSED parent lineage; firing-site-layer continuation)
- `r-cxa-2-producer-audit-2026-06-08.md` · runtime plan v2.39 §0.3/§0.4 · v2.34 AC #8
- `[[r-cxa-seam-wiring-is-producer-discovery]]` · `[[grounding-reveals-claude-closeable-slice-close-honestly]]` · `[[halt-route-split-ac-pattern]]` · `[[verification-shape-sharpened-grep-vs-e2e]]` · `[[use-the-product-probe-pattern]]`
- `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-3 (no silent design extension)
