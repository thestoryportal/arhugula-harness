---
title: R-CXA-2 Implementation Plan
status: implementation-plan
created: 2026-06-08
roadmap: R-CXA-2-cp-is-seam
posture: back-flow + runtime implementation arc
extends:
  - r-cxa-1-2-producer-seam-spec.md
  - r-cxa-2-post-mvp-producer-loop-product-brief.md
authorization: operator authorized implementation moving forward to bring this phase to closure
---

# R-CXA-2 Implementation Plan

This plan resolves the brief's implementation-blocking open questions before
runtime code lands. It keeps the model-driven HITL loop and the engine recovery
loop separate, then implements the prerequisite U-CP-78 Reading A type fix first.

## 1. Decisions Required Before Coding

### OQ-1 — Provider tool call to `ProposedAction`

Map provider tool calls to `ProposedAction` without extending CP types:

- Default model-emitted tool calls become
  `ProposedAction(action_kind=ActionKind.TOOL_CALL, payload=..., brief=None)`.
- `payload` carries the provider-neutral structure needed by the rewrite and
  dispatch layers: `tool_name`, `tool_args`, `server`, `tool_call_id`,
  `provider`, and `model`.
- Sub-agent dispatch is selected only when the resolved tool binding is the
  sub-agent dispatch surface; that case uses
  `ActionKind.SUB_AGENT_DISPATCH` and populates `brief`.
- `ActionKind.INFERENCE_STEP` is not used for individual tool calls; the
  containing model turn remains the `INFERENCE_STEP`.

### OQ-2 — `pause_event_id` derivation

Collapse `pause_event_id` into `PauseEvent.pause_audit_entry_id` for
`cp.pause-captured`.

U-CP-78 Reading A requires `emit_pause_captured_state_ledger_entry` to consume
engine-layer `PauseEvent`. `PauseEvent` already carries the stable substrate
identifier `pause_audit_entry_id`, so the composer and runtime wrapper should
derive the idempotency disambiguator internally as
`str(pause_event.pause_audit_entry_id)`. Runtime code must not synthesize a
workflow-layer `PauseSnapshot`.

`resume_event_id` and `resume_attempt_count` stay loop-owned because
`ResumeOutcome` has no equivalent stable event identifier.

### OQ-3 / E1-E2 — Escalation check

No new `StepKind` and no new ADR are required for this implementation arc.

The HITL tool loop is an `INFERENCE_STEP` inner loop, matching the existing
runtime §14.12 pattern for model tool-use. The loop preserves declarative
workflow semantics because the model-driven iteration happens inside one
inference step; it does not introduce an agent-authored workflow topology.

Hard stop condition: if implementation requires a new workflow `StepKind`,
manifest semantic change, or CP design-substrate field extension, stop and file
a design fork instead of continuing in runtime code.

### OQ-4 — Inner-loop mechanism

Use mechanism β: a harness-authored inner loop wrapping model response handling.

The concrete runtime primitive should be a provider-neutral module, for example
`harness_runtime.lifecycle.hitl_tool_loop`, that:

- reads provider-emitted tool calls through a narrow adapter,
- evaluates the existing HITL requirement rule,
- invokes `RuntimeHITLPlacementRegistry.rewrite_tool_call`,
- opens `RuntimeHITLGateComposer` before dispatch when needed,
- dispatches approved tool calls through `RuntimeToolDispatcher`, and
- feeds tool results or HITL responses back to the model turn.

Do not use SDK-internal loops as the control authority, and do not hide the loop
inside a single manifest-declared `TOOL_STEP`.

### OQ-5 — `tool_call_id` idempotency under fallback

Treat a cross-family fallback candidate switch as a new live model turn unless
the original turn was already journaled.

Replay idempotency is based on stable provider tool-call ids from a journaled
turn. During live fallback before any committed tool dispatch, new provider ids
are expected and must not be deduplicated against the failed candidate. Once a
turn has committed any tool dispatch or HITL rewrite emission, recovery must use
the journaled transcript and continue from the first unprocessed tool call
instead of resampling under a fallback candidate.

### OQ-6 — HITL timeout / degradation

Use the existing `RuntimeHITLPlacementRegistry.on_timeout` and
`RuntimeHITLGateComposer` semantics.

The model-driven loop translates timeout outcomes as follows:

- continue-as-reject: skip dispatch and record the rejection/timeout outcome,
- escalate: re-enter the HITL path or surface a typed escalation,
- abort: fail the inference step.

The loop must not dispatch the underlying tool after a timeout unless the
existing gate semantics explicitly resolve to an approved or edited action.

### OQ-7 — Mid-loop breaker and replay state

Persist per-tool-call loop progress before dispatch.

If a breaker trips before any tool dispatch is committed for the model turn, the
candidate can be abandoned and fallback may resample a new turn. If a breaker
trips after any tool dispatch or HITL rewrite emission is committed, the turn is
partial and must be recovered from journaled state. Recovery resumes at the
first unprocessed `tool_call_id`; it must not re-sample and re-dispatch already
committed tool calls.

## 2. Implementation Order

### Slice 1 — U-CP-78 Reading A type fix

Goal: make `cp.pause-captured` consume real engine-layer `PauseEvent`.

Tests first:

- CP composer test constructs a `PauseEvent` from the engine-layer type and
  asserts `pause_event.pause_audit_entry_id` is used in the idempotency key.
- CP composer test asserts canonical outcome bytes are computed from
  `PauseEvent`, not `PauseSnapshot`.
- Runtime wiring test calls `RuntimeCpIsWiring.emit_pause_captured_state_ledger_entry`
  with `PauseEvent` and verifies a durable `cp.pause-captured` ledger entry.

Code:

- Re-type `emit_pause_captured_state_ledger_entry` from `pause_snapshot` to
  `pause_event`.
- Remove the public `pause_event_id` kwarg from the CP composer and runtime
  wrapper.
- Re-derive the idempotency suffix from `PauseEvent` canonical bytes and
  `pause_event.pause_audit_entry_id`.
- Update docstrings so they name the engine-layer free-function output
  accurately.

### Slice 2 — Engine recovery loop producer

Goal: add a runtime recovery primitive that binds an
`EnginePauseResumeSubstrate`, drives `capture_pause_snapshot` /
`attempt_resume`, and emits `cp.pause-captured` / `cp.resume-attempted`.

Tests first:

- capture path emits `cp.pause-captured` from real `PauseEvent`;
- abort resume path emits `cp.resume-attempted`;
- replay with stable ids returns `IDEMPOTENT_NOOP`;
- recovery state is not represented by a workflow-layer `PauseSnapshot`.

**Durable-substrate decision (landed 2026-06-10, operator-ratified).** The
in-memory `DeterministicEnginePauseResumeSubstrate` is a test fixture, not
crash-survivable, which is why the bound recovery loop was recorded as a
counted bounded-residual. The harness-owned **`PURE_PATTERN_NO_ENGINE` /
`JOURNAL_RESUME` / F2** durable substrate landed as
`harness_runtime.lifecycle.journal_pause_resume_substrate.JournalEnginePauseResumeSubstrate`.

Resolved decisions (so a later spec↔code drift check does not re-flag them):

- **Content store = per-workflow filesystem journal, NOT the IS state ledger.**
  C-CP-22 §22.1 acceptance #5 prose says resume reads "via the U-IS-12
  bounded-read keyed on `paused_workflow_id`", but U-IS-12's `NavigationQuery`
  has no `workflow_id` selector and `StateLedgerEntry` stores a `response_hash`,
  not the `PauseEvent` body — the ledger is an integrity *anchor*, not a content
  store. The durable `PauseEvent` content therefore lives in a filesystem
  journal (`<dir>/<sha256(workflow_id)>.jsonl`); the `cp.pause-captured` /
  `cp.resume-attempted` ledger entries the loop emits remain the integrity
  anchors. Snapshot serialization is impl-discretion per acceptance #9. This is
  a build (operator-ratified 2026-06-10), not a U-IS-12 spec amendment.
- **Does NOT close R-CXA-2.** The engine recovery loop still has no production
  *driver*; the factory still binds `Deterministic`. The durable substrate is a
  committed-but-unwired capability. CXA-2 stays `BOUNDED_RESIDUAL`; wiring (and
  the journal-path / IS-path-class placement decision) is deferred until a real
  recovery driver exists. No substitution-ledger count change.

### Slice 3 — HITL model-driven tool loop producer

Goal: add the provider-neutral model tool loop that fires
`cp.hitl-tool-call-rewriting` before dispatch for HITL-required tool calls.

Tests first:

- one model turn with two tool calls emits exactly one rewrite entry when only
  one call requires HITL;
- non-required calls emit no §16.5 rewrite entry;
- replay of the same journaled `tool_call_id` is idempotent;
- a rejected gate response prevents tool dispatch.

### Slice 4 — Bootstrap / composition wiring

Goal: materialize the new primitives where runtime stage-5 loop initialization
can bind them without changing workflow step cardinality.

This slice may update bootstrap factories, but must not add a new `StepKind` or
alter declarative workflow manifests.

### Slice 5 — Closeout and roadmap accounting

Goal: prove the producers are non-hollow and update tracking surfaces.

Run focused runtime/CP tests, then the repo-required closeout checks. Update
roadmap/status/dashboard only after the implementation evidence exists; do not
pre-close R-CXA-2 from the plan alone.

