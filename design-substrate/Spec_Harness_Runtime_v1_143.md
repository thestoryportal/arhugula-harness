# Spec: Harness Runtime — v1.143 (delta over cleared v1.142)

*Delta-only file. Amendment sites: the C-RT-17 §14.7.1 registry bullet that leaves `DECLARATIVE_STEP`
unbound (`Spec_Harness_Runtime_v1_132.md:4652`), the matching parenthetical in the
`RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND` taxonomy row (`:4802`), and the whole C-RT-18 §14.8.1 wrap-asymmetry row for `DECLARATIVE_STEP` (`:4868`), whose
"body-of-prose evaluation" description and future-binding clause are both replaced. None of these sites is amended by v1.133 through v1.142. Every other
v1.142 and earlier term remains in force. Cleared predecessor files are not edited.*

**Status: CLEARED 2026-11-08 — ratified by the integration lead at LIT `cmt-eaec8ba7-4450-4cd0-afb8-c80f1592921e`
on the reviewed body at `72e1f5b596a3d3241c35d8d2c89c7e1efc72b8c8` (independent APPROVE
`cmt-a51a00d7-f76e-443a-b22e-70719db3ba22`); clearance `.harness/clearance/spec-harness-runtime-v1-143-cleared-2026-11-08.md`.**

**Authority:** integration-lead disposition LIT `arhugula-harness-trial-193.qrf`
`cmt-de679744-ad1b-4a04-8664-67f4d7a536db` (option A of `cmt-f2f25126-a27f-4765-a20f-87568d53ba13`),
admitted at `cmt-25152ce4-0505-4d90-8d46-20fd123f8e37`.

## §0 Change-note (v1.142 → v1.143)

The installed runtime had no dispatcher for `DECLARATIVE_STEP`, so any workflow declaring one failed
closed with `RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND` at its first such step. A declarative
orchestrator could therefore never hand a `worker_plan` to the CP `LEAD_PLAN` selection (CP v1.130
§25.11.1.1) through `harness run`. This delta binds the smallest effect-free dispatcher for the kind:
the step's payload declares its output and dispatch returns it.

### §0.1 C-RT-17 §14.7.1 — `DECLARATIVE_STEP` binding (AMENDED)

Stage 5 (LOOP_INIT) binds `StepKind.DECLARATIVE_STEP → DeclarativeStepDispatcher`
(`harness-runtime/src/harness_runtime/lifecycle/declarative_step_dispatcher.py`) in every
`StepKindDispatcherRegistry`, beside `TOOL_STEP`. The binding does not depend on
`ctx.requires_inference`, because a declarative step never reaches a provider and the §2.1 (v1.47)
inference-need predicate already excludes the kind. The binding is the bare dispatcher, without a
HITL gate composer, retry/breaker wrapper or `SyncDispatcherFacade`: the dispatcher is synchronous and
has no action surface to gate. The C-RT-18 §14.8.1 `DECLARATIVE_STEP` row is replaced in full by:

| `DECLARATIVE_STEP` | NOT in HITL gate composer scope — a declarative step returns the constant output its payload declares (§0.2); it has no action surface to gate. Stage 5 binds the bare `DeclarativeStepDispatcher`. | n/a | n/a |

The earlier "body-of-prose evaluation" description no longer applies to the kind: §0.2 is its only
semantics, and §0.3 lists the evaluation behaviors it excludes.

`HITL_STEP` remains unbound. The `RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND` row's trigger and behavior
are unchanged; its parenthetical list of unbound kinds no longer includes `DECLARATIVE_STEP`.

### §0.2 Payload and output

1. **Payload.** `step.step_payload` is exactly `{"output": <object>}`: a single required `output` key
   whose value is a JSON object with string keys and JSON values. Numbers are finite: a TOML `nan` or
   `inf` at any depth has no JSON representation. Any other key, a missing `output`, a non-object
   `output` or a nonfinite number is mis-shaped.
2. **Output.** Dispatch returns the declared `output` mapping as the step output, unchanged. The
   dispatcher does not read `step_context`, the effective binding, sibling or upstream outputs, and
   does not interpret the output; for example, it never extracts or checks a `worker_plan`. The CP
   driver consumes the returned mapping exactly as it consumes any other step output.
3. **Effects.** None: no provider, tool, MCP, file, clock, randomness, subprocess, daemon or ledger
   effect. Repeated dispatch of the same step returns an equal output, so the kind's existing
   re-fire-safe classification (CP v1.64 §1) is accurate for this dispatcher.
4. **Failure.** A mis-shaped payload raises `DeclarativeStepPayloadShapeError`, whose message begins
   `RT-FAIL-PAYLOAD-SHAPE:` and names the step. That is the existing permanent class from §14.5; this
   delta adds no `RT-FAIL-*` class. The step fails before returning any output, so a mis-shaped
   orchestrator dispatches no worker.

### §0.3 Out of scope

Prose or expression evaluation, templating, references to other steps' outputs, and any runtime
production of a `worker_plan` from model output (the LLM-call producer follow-on) are unchanged and
are not introduced here. The CP plan parser (`harness_cp/worker_plan.py`) and its refusal reasons are
unchanged.

### §0.4 Conformance evidence (to be bound to the reviewed candidate)

`harness-runtime/tests/test_declarative_step_dispatch.py` runs manifest files through `api.run`, whose
bootstrap builds the production registry with no injected dispatcher. It checks that a declarative
orchestrator with nested declarative leaves runs plans `[c, a]` and `[b]` in order, with each worker's
lead brief bound to its own fan-out ordinal through the per-worker dispatch audit, and the join; that
invalid plans and mis-shaped payloads, including nested TOML `nan`/`inf`, dispatch no worker; and that a
declarative-only workflow completes without a provider. Each of these checks fails against the
unbound v1.142 stage 5 with `StepKindDispatcherNotBoundError`.
`harness-runtime/tests/test_bootstrap.py` asserts the bound dispatcher and that `HITL_STEP` stays
unbound.
