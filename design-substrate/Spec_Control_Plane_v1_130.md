# Spec: Control Plane — v1.130 (delta over v1.129)

*Delta-only file. One contract amended: C-CP-25 §25.11 `ORCHESTRATOR_WORKERS` row (text current at
v1.32) gains NEW §25.11.1, which defines how the orchestrator's output selects and briefs workers.
`HIERARCHICAL_DELEGATION` inherits it at every level through its reuse of the strategy. Every other
v1.129 and earlier C-CP-01 … C-CP-29 term remains in force. Proposed CP deltas, if any, are not
amended here.*

**Status: CLEARED 2026-11-05 — ratified by the integration lead at LIT `cmt-35ae37ac-54fe-4706-9274-0219dfad7e2b`
on the frozen reviewed body `78f6dcb7963411a1508794f2d96d6a45a650a021` (independent contract GREEN
`cmt-1ced7828-9dc5-48ec-b0f0-39c800d46282`); clearance `.harness/clearance/Spec_Control_Plane-v1_130-cleared-2026-11-05.md`.
Contract clearance only; source conformance, CI, landing and installed acceptance remain owed.**

**Filed:** 2026-11-05

**Authority:** C-CP-25 §25.11 already states that "an orchestrator step computes a dynamic worker
set", and U-CP-88's acceptance criterion requires "an orchestrator dispatches a dynamic worker set".
At harness `origin/main` `7c8f3af9`, `_execute_orchestrator_workers` sets
`worker_steps = list(steps[1:])` (`workflow_driver.py` line 12437), and the orchestrator output only
feeds the aggregate fold. This delta specifies the missing selection seam. It is claimed at LIT
`arhugula-harness-trial-193.qrf` `cmt-9e26c9ad`, with grounding at `cmt-d7db4622`.

**Predecessor:** `Spec_Control_Plane_v1_129.md` (head). **Paired Runtime delta:**
`Spec_Harness_Runtime_v1_140.md` (the sub-agent brief reader).

## §0 Change-note (v1.129 → v1.130)

| Site | Before | After |
|---|---|---|
| §25.11 `ORCHESTRATOR_WORKERS` row | Text says the orchestrator computes a dynamic worker set; source dispatches every declared worker with its declared brief | NEW §25.11.1: the manifest selects the worker source. `DECLARED_POOL` keeps the existing behavior. `LEAD_PLAN` parses the orchestrator output into a typed plan that orders a subset of the declared workers and may brief them |
| `WorkflowManifestEntry` (C-CP-25 §25.2) | No worker-source field | Gains `worker_selection: WorkerSelection = WorkerSelection.DECLARED_POOL` (§25.11.1.1) |
| `StepExecutionContext` (§25.3.3.4) | No plan field | Gains hash-inert, non-persistent `lead_brief: SubAgentBrief \| None` (§25.11.1.4) |
| Worker ordinal (v1.42 §26.2, v1.94 §1(3)) | `branch_index` is the ordinal in `steps[1:]` | `branch_index` is the ordinal in the derived plan (§25.11.1.5). Under `DECLARED_POOL` the two are identical |
| Worker `step_index` | `branch_index + 1` at every worker context | The worker's declared ordinal in `steps`, carried on its assignment (§25.11.1.4(2)). Under `DECLARED_POOL` it equals `branch_index + 1` |
| `_determine_fanout_resume` and the driver crash gate | Worker domain sized from the declared pool | Worker domain sized from the plan derived from the recorded orchestrator output; the declared-body cardinality check is kept (§25.11.1.5(3)) |
| Resume carriers | No selection | `FanOutResumeState` and the replay store's orchestrator record carry the run's `worker_selection`; resume refuses a different selection (§25.11.1.5(6)) |
| Orphan worker artifacts | A worker dispatch marker or cardinality marker with no orchestrator record or marker is recovered as a fresh run | Refused as a corrupt store under every `cascade_policy` (§25.11.1.5(4)) |
| Fail classes | — | NEW `orchestrator-workers-plan-invalid: <reason>` (§25.11.1.4(3)), `orchestrator-workers-selection-mismatch` and `orchestrator-workers-plan-store-unsupported` (§25.11.1.5(6)) |

## §1 NEW §25.11.1 — Lead-directed worker plan

### §25.11.1.1 Types

New module `harness_cp/worker_plan.py`:

```python
class WorkerSelection(StrEnum):
    DECLARED_POOL = "declared-pool"   # every declared worker, declared order, declared brief
    LEAD_PLAN = "lead-plan"           # the orchestrator output's plan selects and briefs workers

class WorkerAssignment(BaseModel):    # frozen, extra="forbid"
    step: WorkflowStep                # a member of the declared worker pool
    declared_index: int               # the step's ordinal in `steps` (orchestrator = 0)
    brief: SubAgentBrief | None       # set iff LEAD_PLAN and step is SUB_AGENT_DISPATCH

class WorkerPlan(BaseModel):          # frozen, extra="forbid"
    assignments: tuple[WorkerAssignment, ...]

class WorkerPlanInvalid(Exception):
    reason: str

def derive_worker_plan(
    selection: WorkerSelection,
    orchestrator_output: Mapping[str, Any],
    pool: Sequence[WorkflowStep],
) -> WorkerPlan: ...
```

`WorkflowManifestEntry` gains `worker_selection: WorkerSelection = WorkerSelection.DECLARED_POOL`. A
manifest whose `topology_pattern` is neither `ORCHESTRATOR_WORKERS` nor `HIERARCHICAL_DELEGATION` and
whose `worker_selection` is `LEAD_PLAN` fails manifest validation. `[LAW:no-mode-explosion]`: the
enum is a closed two-variant domain choice between a fixed pipeline and a lead-directed fan-out,
owned by C-CP-25. It has no deletion date because neither variant is transitional. A third
variant needs a new CP delta.

### §25.11.1.2 Pool

The **pool** is the declared worker sequence that the driver already computes: `steps[1:]` after
`_split_synthesis` has removed any terminal `POST_JOIN_SYNTHESIS` step. Pool membership fixes each
worker's identity, `step_kind`, payload, per-step overrides, role/model binding, HITL placement and
`child_workflow_id`. A plan selects, orders and briefs pool members; it cannot create a worker or
change any of those properties.

### §25.11.1.3 Derivation

`derive_worker_plan` is pure. It is the only unit that reads the plan from an orchestrator output.

1. `DECLARED_POOL` returns one assignment per pool step, in pool order, each with `brief=None`. It
   does not read `orchestrator_output`. Every variant sets `declared_index` to the pool position
   plus one, so it is fixed by the declaration and never by the plan. A `worker_plan` key in the
   output has no effect.
2. `LEAD_PLAN` reads `orchestrator_output["worker_plan"]`. The value MUST be a sequence (not a
   string or mapping) of mappings. Each has the key `worker` (a pool `step_id` string). It has the key
   `brief` if and only if that worker's `step_kind` is `SUB_AGENT_DISPATCH`. Assignments keep the
   sequence order. Under `LEAD_PLAN` every sub-agent worker's brief is therefore lead-authored and
   recorded in the orchestrator output. No assignment falls back to the declared payload brief.
3. `brief` holds exactly the four C-CP-13 §13.2 fields (`objective`,
   `output_format`, `guidance`, `task_boundaries`). The parser computes `summary_hash` with
   `compute_brief_summary_hash` and builds the `SubAgentBrief`. A supplied `summary_hash` is an
   extra key and is rejected, so the hash has one source.
4. Any of the following raises `WorkerPlanInvalid` with the named reason. Nothing is skipped or
   defaulted:
   - `missing-worker-plan`: the key is absent;
   - `not-a-sequence`: the value is not a sequence of mappings;
   - `malformed-assignment`: an entry has a missing, extra or non-string key;
   - `unknown-worker:<id>`: the id names no pool member, including the orchestrator and a carved
     synthesis step;
   - `duplicate-worker:<id>`: an id appears twice;
   - `missing-brief:<id>`: a `SUB_AGENT_DISPATCH` worker has no brief;
   - `brief-on-non-subagent:<id>`: a brief is attached to a worker whose `step_kind` is not
     `SUB_AGENT_DISPATCH`;
   - `malformed-brief:<id>`: the brief fails `SubAgentBrief` validation.
5. An empty sequence is a valid plan with zero assignments.

### §25.11.1.4 Dispatch

1. **One plan per fan-out.** The strategy derives the plan once, after `orchestrator_output` is
   available and before any consumer of a worker ordinal. This applies to a fresh dispatch, a pause
   resume (output recovered from `FanOutResumeState.orchestrator_output`) and a crash resume (output
   recovered from the replay store). The pre-strategy crash units of §25.11.1.5(3) call the same
   function on the same recorded output; no unit maps worker ordinals any other way. `worker_steps`
   becomes
   `[a.step for a in plan.assignments]`. Every later strategy operation (warm-up split, dispatch
   markers, cascade, barrier, fold, resume carriers, synthesis) reads that list unchanged.
2. **Declared step index.** Every site that composes a worker `StepExecutionContext` sets
   `step_index = assignment.declared_index`. This covers fresh dispatch, the pause-resume and
   crash-resume re-dispatch paths, paused-child and effect-fence recovery, and the warm-up split. At
   `7c8f3af9` these sites write `branch_index + 1` (`workflow_driver.py` lines 13312, 13505, 13566
   and 13784). Per-step policy, audit and Runtime skill activation key on `step_index`, so a worker
   keeps its declared identity whatever its plan position. The synthesis step keeps its declared
   ordinal (`branch_count=len(steps)` at the synthesis call sites), independent of plan size.
3. **Failure.** `WorkerPlanInvalid` produces `RunStatus.FAILED` with
   `fail_class = "orchestrator-workers-plan-invalid: <reason>"`, before any worker dispatch or worker
   marker. The orchestrator ran, so its sequential ledger entry and replay record are kept, as for any
   post-orchestrator failure. `cascade_policy` does not apply, because no worker failed.
4. **Brief carrier.** `StepExecutionContext` gains
   `lead_brief: SubAgentBrief | None = Field(default=None, exclude=True, repr=False)`, the same
   carrier shape as `validator_run` (v1.129 §28.11.5). The driver sets it from
   `WorkerAssignment.brief` on each worker's context only. It is set for every `LEAD_PLAN`
   sub-agent worker and is `None` for every other worker, including all `DECLARED_POOL` workers. It is absent from every `model_dump`, so it never enters a hash, ledger row or pause
   snapshot. It is re-derived from the recorded orchestrator output on every resume (§25.11.1.5).
   Runtime's sub-agent composer is the only reader (paired Runtime v1.140).
5. **Empty plan.** Zero assignments drains zero workers. Without a synthesis step the strategy returns
   `SUCCESS` with `final_state = {"orchestrator": <output>, "worker_outputs": {}}`. With a synthesis
   step the existing v1.54 dispatch-time guard returns `post-join-synthesis-no-siblings`.

### §25.11.1.5 Resume and ordinals

1. **Ordinal domain.** A worker's `branch_index` is its ordinal in the derived plan. This applies to
   `FanOutBranchResumeState.branch_index` (v1.42 §26.2), `FanOutResumeState.worker_count`, the
   per-branch dispatch markers, the effect-fence branch carriers and the v1.94
   `range(len(worker_steps))` refire-safe domain. Their identity checks
   (`worker_steps[branch_index].step_id` / `step_kind`) now run against the planned list, so a resumed
   plan with a different worker count, order or membership fails closed through the existing
   mismatch classes. A change of selection with the same worker list is caught by (6).
2. **Pause resume.** The orchestrator is not re-dispatched (unchanged). The plan is re-derived from
   the recovered `orchestrator_output` under the resumed manifest's `worker_selection` and pool.
3. **Crash resume (pre-strategy decisions).** Two pre-strategy units size the worker domain from
   the declared pool at `7c8f3af9`: `_determine_fanout_resume` (`workflow_driver.py` line 7768) and
   the driver crash gate that calls it (lines 3873-4020). For the orchestrator topologies, both MUST
   derive the plan from the store's recorded orchestrator output, through the same
   `derive_worker_plan`, before any worker-ordinal decision. Then:
   - `FanOutResumeState.worker_count` is the plan length (was `len(steps) - 1` at line 8122), so the
     strategy's `worker-count-mismatch` check (line 12455) compares plan to plan;
   - the `RE_DISPATCH` timeout refire bound `_branch_count` (line 7853) and the driver gate's
     out-of-range-marker bound `_card_branch_count` (line 4016) are the plan length;
   - dispatched-kind and maybe-ran comparisons resolve an ordinal through the planned list.
   The recorded fan-out cardinality check (line 7819) is a different fact and is kept: it compares the
   store's capture-time `len(steps)` against the resumed declared body, so a changed pool still fails
   closed even when the plan would fit.
4. **Crash before the orchestrator record.** Workers are dispatched only after `record_orchestrator`
   (§25.12 reserve-before-commit). So a store with no orchestrator record holds no legitimate worker
   marker. The existing orchestrator maybe-ran classifier (v1.64, v1.86) decides between re-dispatch
   and fail-closed, unchanged. A re-dispatched orchestrator produces a new output, and its plan
   governs the run, because no worker of any earlier plan ran. Worker dispatch markers, worker
   branch records and the cardinality marker are all written after `record_orchestrator`, so any of
   them without an orchestrator record is a corrupt store. At `7c8f3af9` a worker branch record
   fails closed (`_FanOutStoreCorruptError`, line 8104), and the lost-capture allowlist (line 7967)
   runs only when the orchestrator dispatch marker is present. With no orchestrator marker, the
   no-branch arm returns `None` at line 8100 and the run is re-dispatched fresh even when worker or
   cardinality markers are present. Before that return, the arm MUST refuse any present worker
   dispatch marker (`dispatched_branch_kinds` non-empty) or cardinality marker
   (`fanout_cardinality_present`) with `_FanOutStoreCorruptError`. The orchestrator-marker-present
   path keeps its existing allowlist unchanged, so each case has one enforcer. The check is by
   presence. It applies under every
   `cascade_policy`, including `PROCEED`, whose workers write no dispatch markers, so any marker
   there is orphaned. It applies under both selections, because the inconsistency does not depend
   on the plan. No plan is derived in this arm.
5. **Plan failure on resume.** A recorded orchestrator output whose plan fails derivation under the
   resumed manifest returns `orchestrator-workers-plan-invalid: <reason>`.
6. **Selection binding.** The plan is a pure function of `worker_selection`, the recorded
   orchestrator output and the declared pool. The output is recorded, and pool identity is checked
   by (1) and the cardinality check. The selection is the remaining input, so it is recorded with the
   output:
   - `FanOutResumeState` gains `worker_selection: WorkerSelection`. Pause capture sets it from the
     running manifest. A snapshot without the field predates this delta, so it parses as
     `DECLARED_POOL`, the only selection that existed then.
   - The replay store's orchestrator record gains the selection:
     `record_orchestrator(run_key, step_id, output, worker_selection)`, and
     `read_orchestrator_output` returns it. A record without it predates this delta and reads as
     `DECLARED_POOL`. Under `LEAD_PLAN`, a bound store whose `record_orchestrator` does not accept
     `worker_selection` returns `RunStatus.FAILED` with
     `fail_class = "orchestrator-workers-plan-store-unsupported"` before the orchestrator dispatches.
     A `LEAD_PLAN` record is never written without its selection.
   - Pause and crash resume compare the recorded selection with the resumed manifest's before
     deriving the plan. A difference returns `RunStatus.FAILED` with
     `fail_class = "orchestrator-workers-selection-mismatch"`, with no orchestrator or worker dispatch.
   - Under `LEAD_PLAN` every sub-agent brief comes from the recorded output (§25.11.1.3(2)). An
     unchanged selection therefore reproduces the same briefs, and a changed declared payload brief
     has no effect on a resumed `LEAD_PLAN` run.
   - Under `DECLARED_POOL` a worker's brief comes from its declared payload. Resume does not compare
     step payloads under either selection; that is unchanged from v1.129 and is not widened here.

### §25.11.1.6 `HIERARCHICAL_DELEGATION`

Each level calls `_execute_orchestrator_workers` with its own manifest entry and steps, so each level
applies its own `worker_selection`. The fan-out cap of 3 per parent (C-CP-10 §10.3) is still checked
against the declared pool before the orchestrator runs (`detect-then-refuse`, unchanged). A plan is a
subset of the pool, so the cap also bounds every plan. Gate-level descent and bottom-up composition
are unchanged.

### §25.11.1.7 Non-goals

- How an orchestrator dispatcher produces `worker_plan`. A `TOOL_STEP`, a deterministic planner or a
  `SUB_AGENT_DISPATCH` whose output carries the key satisfies this delta now. Structured plan
  emission by an `LLM_CALL` orchestrator is a separate Runtime follow-on.
- Repeating a pool member with different briefs (a duplicate id is rejected). That would need
  per-assignment identity for `child_workflow_id`, dispatch markers and resume carriers.
- `PARALLELIZATION`, `DECENTRALIZED_HANDOFF` and `EVALUATOR_OPTIMIZER`.

## §2 Witnesses

Each witness is a behavior test on the public `execute_workflow` entry with recording dispatchers. A
discriminating mutant is listed for each, and the witness fails under it.

| ID | Behavior | Mutant it kills |
|---|---|---|
| W1 | `DECLARED_POOL` (default) with pool `[a,b,c]` and an orchestrator output containing `worker_plan: [{"worker":"c"}]` dispatches a, b and c in declared order with declared briefs and `step_index` 1, 2, 3 | Reading `worker_plan` regardless of selection (a key-presence mode) |
| W2 | `LEAD_PLAN` with pool `[a,b,c]` and plan `[c,a]` dispatches only c then a. `worker_outputs` keys are `c` then `a` (branch ordinals 0 and 1). b has no dispatch, marker or ledger entry. c's context has `step_index` 3 and a's has 1, and a per-step policy and skill-activation binding keyed on index 3 applies to c only | `worker_steps = steps[1:]` retained; `step_index = branch_index + 1` retained |
| W3 | `LEAD_PLAN` with plan brief on a `SUB_AGENT_DISPATCH` worker: the handoff context, the gate-level-descent `sub_agent_brief` and the dispatch `response_hash` all reflect the planned brief, and `summary_hash` equals `compute_brief_summary_hash` of it | Runtime reading `payload.brief` at any reader site; parser trusting a supplied hash |
| W4 | Each §25.11.1.3(4) reason gives `FAILED` with `orchestrator-workers-plan-invalid: <reason>`, zero worker dispatches and the orchestrator's ledger entry present. This includes a plan naming the carved synthesis step id | Silent skip of an invalid entry; fallback to the declared pool |
| W5 | Empty plan: `SUCCESS` with `worker_outputs == {}`. With a synthesis step: `post-join-synthesis-no-siblings` | Empty plan treated as invalid, or as "all workers" |
| W6 | `cascade_policy=pause`, plan `[c,a]`, a fails → `PAUSED`. Resume does not re-dispatch the orchestrator, keeps c's recorded output and re-dispatches only a. A resumed manifest whose plan differs fails with the existing identity mismatch | Resume deriving `worker_steps` from the declared pool |
| W6b | Same worker list, changed selection: a `LEAD_PLAN` run over pool `[a,b]` with plan `[a,b]` and a lead brief on b pauses after a completes. Resuming under `DECLARED_POOL` returns `orchestrator-workers-selection-mismatch` with no dispatch. A `DECLARED_POOL` pause resumed under `LEAD_PLAN` gets the same result. The same check holds on crash resume through the store record | Selection not recorded; b re-dispatched with its declared brief beside a's lead-plan output |
| W6d | Same selection, same worker list, changed declared brief: a `LEAD_PLAN` run over pool `[a,b]`, both `SUB_AGENT_DISPATCH`, plan `[a,b]` with lead briefs, pauses after a completes. On pause resume and crash resume, b's declared payload brief is changed. b re-dispatches with its recorded lead brief, and the changed declared brief reaches no reader | Optional lead brief falling back to the declared payload brief |
| W6c | A pause snapshot and a store record written without `worker_selection` resume as `DECLARED_POOL`. A `LEAD_PLAN` run on a store whose `record_orchestrator` lacks the parameter fails `orchestrator-workers-plan-store-unsupported` before the orchestrator dispatches | Absent selection read as `LEAD_PLAN`; a `LEAD_PLAN` record written without its selection |
| W7a | Completed-branch path: crash after the orchestrator record and c's completion (plan `[c,a]`, pool of 3). Resume succeeds with no `worker-count-mismatch`, dispatches only a with `step_index` 1, and never re-dispatches c | `_determine_fanout_resume` returning `worker_count = len(steps) - 1`; recovery contexts using `branch_index + 1` |
| W7b | Cardinality-only and timeout path: same plan, no completed branch. A stale dispatch marker at planned ordinal 2 (inside the declared count, outside the planned count) fails closed at the driver gate. Under `RE_DISPATCH`, a timed-out marker at planned ordinal 2 is refire-unsafe. A resumed body with a changed pool size still fails the recorded-cardinality check | `_card_branch_count` or the timeout `_branch_count` sized from the pool; the cardinality check dropped or switched to plan length |
| W8 | `LEAD_PLAN` store with a worker branch record but no orchestrator record fails closed with the existing corrupt-store error, and no worker dispatches | Falling back to the declared pool when the record is missing |
| W8b | Marker-only stores with no orchestrator record and no orchestrator dispatch marker: (i) a worker dispatch marker, (ii) a cardinality marker. Each fails closed with `_FanOutStoreCorruptError` and no orchestrator dispatch, under `PAUSE` and under `PROCEED`, for both selections | The no-branch arm returning `None` (fresh re-dispatch) when only markers are present |
| W9 | `HIERARCHICAL_DELEGATION` with a `LEAD_PLAN` child level: the child's plan selects among the child's pool. A parent level with 4 declared children and a 2-entry plan is still refused by the cap before the orchestrator runs | Cap computed on the plan; child level using the parent's selection |
| W10 | A `LEAD_PLAN` manifest on `PARALLELIZATION` fails manifest validation | Accepting the field on a topology without an orchestrator |

## §3 Status

CLEARED 2026-11-05 by independent review GREEN of the exact head and integration-lead ratification
(see the status banner). Source landing, CI and installed acceptance remain owed.
