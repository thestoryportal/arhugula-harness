# Spec: Control Plane — v1.130 (delta over v1.129)

*Delta-only file. One contract amended: C-CP-25 §25.11 `ORCHESTRATOR_WORKERS` row (text current at
v1.32) gains NEW §25.11.1, which defines how the orchestrator's output selects and briefs workers.
`HIERARCHICAL_DELEGATION` inherits it at every level through its reuse of the strategy. Every other
v1.129 and earlier C-CP-01 … C-CP-29 term remains in force. Proposed CP deltas, if any, are not
amended here.*

**Status: PROPOSED — contract text for independent review and integration-lead ratification. Not
cleared; no source, CI, landing or installed claim.**

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
| Fail classes | — | NEW `orchestrator-workers-plan-invalid: <reason>` and `orchestrator-workers-plan-unrecoverable` (§25.11.1.6) |

## §1 NEW §25.11.1 — Lead-directed worker plan

### §25.11.1.1 Types

New module `harness_cp/worker_plan.py`:

```python
class WorkerSelection(StrEnum):
    DECLARED_POOL = "declared-pool"   # every declared worker, declared order, declared brief
    LEAD_PLAN = "lead-plan"           # the orchestrator output's plan selects and briefs workers

class WorkerAssignment(BaseModel):    # frozen, extra="forbid"
    step: WorkflowStep                # a member of the declared worker pool
    brief: SubAgentBrief | None       # None = the step's declared brief applies

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
   does not read `orchestrator_output`. A `worker_plan` key in the output has no effect.
2. `LEAD_PLAN` reads `orchestrator_output["worker_plan"]`. The value MUST be a sequence (not a
   string or mapping) of mappings, each with exactly the keys `worker` (a pool `step_id` string) and
   optionally `brief`. Assignments keep the sequence order.
3. `brief`, when present, holds exactly the four C-CP-13 §13.2 fields (`objective`,
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
   - `brief-on-non-subagent:<id>`: a brief is attached to a worker whose `step_kind` is not
     `SUB_AGENT_DISPATCH`;
   - `malformed-brief:<id>`: the brief fails `SubAgentBrief` validation.
5. An empty sequence is a valid plan with zero assignments.

### §25.11.1.4 Dispatch

1. **One plan per fan-out.** The strategy derives the plan once, after `orchestrator_output` is
   available and before any consumer of a worker ordinal. This applies to a fresh dispatch, a pause
   resume (output recovered from `FanOutResumeState.orchestrator_output`) and a crash resume (output
   recovered from the replay store). `worker_steps` becomes
   `[a.step for a in plan.assignments]`. Every later strategy operation (warm-up split, dispatch
   markers, cascade, barrier, fold, resume carriers, synthesis) reads that list unchanged.
2. **Failure.** `WorkerPlanInvalid` produces `RunStatus.FAILED` with
   `fail_class = "orchestrator-workers-plan-invalid: <reason>"`, before any worker dispatch or worker
   marker. The orchestrator ran, so its sequential ledger entry and replay record are kept, as for any
   post-orchestrator failure. `cascade_policy` does not apply, because no worker failed.
3. **Brief carrier.** `StepExecutionContext` gains
   `lead_brief: SubAgentBrief | None = Field(default=None, exclude=True, repr=False)`, the same
   carrier shape as `validator_run` (v1.129 §28.11.5). The driver sets it from
   `WorkerAssignment.brief` on each worker's context only. Under `DECLARED_POOL` it is always
   `None`. It is absent from every `model_dump`, so it never enters a hash, ledger row or pause
   snapshot. It is re-derived from the recorded orchestrator output on every resume (§25.11.1.5).
   Runtime's sub-agent composer is the only reader (paired Runtime v1.140).
4. **Empty plan.** Zero assignments drains zero workers. Without a synthesis step the strategy returns
   `SUCCESS` with `final_state = {"orchestrator": <output>, "worker_outputs": {}}`. With a synthesis
   step the existing v1.54 dispatch-time guard returns `post-join-synthesis-no-siblings`.

### §25.11.1.5 Resume and ordinals

1. **Ordinal domain.** A worker's `branch_index` is its ordinal in the derived plan. This applies to
   `FanOutBranchResumeState.branch_index` (v1.42 §26.2), `FanOutResumeState.worker_count`, the
   per-branch dispatch markers, the effect-fence branch carriers and the v1.94
   `range(len(worker_steps))` refire-safe domain. Their identity checks
   (`worker_steps[branch_index].step_id` / `step_kind`) now run against the planned list, so a resumed
   manifest that yields a different plan fails closed through the existing mismatch classes.
2. **Pause resume.** The orchestrator is not re-dispatched (unchanged). The plan is re-derived from
   the recovered `orchestrator_output` under the resumed manifest's `worker_selection` and pool.
3. **Crash resume (driver reconstruct gate).** The gate that builds the crash `FanOutResumeState`
   (`workflow_driver.py` lines 3873-4020 at `7c8f3af9`) currently sizes the worker domain from the
   declared pool. It MUST size it from the plan derived from the replay store's recorded
   orchestrator output, through the same `derive_worker_plan`. This includes the
   out-of-range-marker bound `_card_branch_count` and the dispatched-kind comparison.
4. **Crash before the orchestrator record.** Workers are dispatched only after `record_orchestrator`
   (§25.12 reserve-before-commit). So a store with no orchestrator record holds no legitimate worker
   marker. The existing orchestrator maybe-ran classifier (v1.64, v1.86) decides between re-dispatch
   and fail-closed, unchanged. A re-dispatched orchestrator produces a new output, and its plan
   governs the run, because no worker of any earlier plan ran.
5. **Unrecoverable plan.** Under `LEAD_PLAN`, a store holding a worker marker or worker output but no
   orchestrator record returns `RunStatus.FAILED` with
   `fail_class = "orchestrator-workers-plan-unrecoverable"`. The planned list cannot be
   reconstructed, so no ordinal can be attributed. A plan that fails derivation on resume returns
   `orchestrator-workers-plan-invalid: <reason>`.

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
| W1 | `DECLARED_POOL` (default) with pool `[a,b,c]` and an orchestrator output containing `worker_plan: [{"worker":"c"}]` dispatches a, b and c in declared order with declared briefs | Reading `worker_plan` regardless of selection (a key-presence mode) |
| W2 | `LEAD_PLAN` with pool `[a,b,c]` and plan `[c,a]` dispatches only c then a. `worker_outputs` keys are `c` then `a` (branch ordinals 0 and 1). b has no dispatch, marker or ledger entry | `worker_steps = steps[1:]` retained |
| W3 | `LEAD_PLAN` with plan brief on a `SUB_AGENT_DISPATCH` worker: the handoff context, the gate-level-descent `sub_agent_brief` and the dispatch `response_hash` all reflect the planned brief, and `summary_hash` equals `compute_brief_summary_hash` of it | Runtime reading `payload.brief` at any reader site; parser trusting a supplied hash |
| W4 | Each §25.11.1.3(4) reason gives `FAILED` with `orchestrator-workers-plan-invalid: <reason>`, zero worker dispatches and the orchestrator's ledger entry present. This includes a plan naming the carved synthesis step id | Silent skip of an invalid entry; fallback to the declared pool |
| W5 | Empty plan: `SUCCESS` with `worker_outputs == {}`. With a synthesis step: `post-join-synthesis-no-siblings` | Empty plan treated as invalid, or as "all workers" |
| W6 | `cascade_policy=pause`, plan `[c,a]`, a fails → `PAUSED`. Resume does not re-dispatch the orchestrator, keeps c's recorded output and re-dispatches only a. A resumed manifest whose plan differs fails with the existing identity mismatch | Resume deriving `worker_steps` from the declared pool |
| W7 | Crash after the orchestrator record and c's completion (plan `[c,a]`, pool of 3): resume dispatches only a and never c. A stale marker at planned ordinal 2 (inside the declared count, outside the planned count) fails closed | Driver gate sizing `_card_branch_count` from the pool |
| W8 | `LEAD_PLAN` store with a worker output but no orchestrator record → `orchestrator-workers-plan-unrecoverable` | Falling back to the declared pool when the record is missing |
| W9 | `HIERARCHICAL_DELEGATION` with a `LEAD_PLAN` child level: the child's plan selects among the child's pool. A parent level with 4 declared children and a 2-entry plan is still refused by the cap before the orchestrator runs | Cap computed on the plan; child level using the parent's selection |
| W10 | A `LEAD_PLAN` manifest on `PARALLELIZATION` fails manifest validation | Accepting the field on a topology without an orchestrator |

## §3 Status

PROPOSED. Clears only by independent review GREEN of the exact head and integration-lead
ratification, followed by a clearance marker and an artifact-heads refresh. Source landing, CI and
installed acceptance remain owed.
