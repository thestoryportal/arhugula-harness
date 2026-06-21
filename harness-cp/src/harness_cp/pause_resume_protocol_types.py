"""C-CP-26 PauseResumeProtocol type carriers — 2 enums + 2 envelope models.

U-CP-62 — first unit of cluster 10-CP-B. Declares the type carriers that the
C-CP-26 PauseResumeProtocol class body (U-CP-63 capture_pause_snapshot + U-CP-64
attempt_resume) and the pause/resume span emitter (U-CP-65) consume at runtime:

- `WorkflowPauseReason` — 5-class workflow-layer pause taxonomy (CP spec v1.11
  §26.2; renamed from `PauseReason` at v1.11 per path γ disambiguation)
- `MaterialDiffPolicy` — 3-class material-diff resumption policy (STRICT default
  per Decision 2.D7)
- `PauseSnapshot` — 8-field pause-snapshot envelope with state-ledger-anchored
  snapshot-hash
- `ResumeResult` — 5-field resume-attempt outcome envelope

Member string values are cited verbatim from CP spec v1.11 §26.2. `PauseSnapshot`
+ `ResumeResult` use frozen Pydantic v2 models (matching the U-CP-58/U-CP-59
precedent at cluster 10-CP-A; the spec's `@dataclass(frozen=True)` declaration
maps to `BaseModel` + `ConfigDict(frozen=True, extra="forbid")` per repo
discipline).

**Naming note (path γ disambiguation, 2026-05-21).** `WorkflowPauseReason`
(workflow-layer) is distinct from the C-CP-22 §22.1 `PauseReason` (engine-layer
replay-pause taxonomy) homed at `harness_cp.pause_resume_protocol`. The two
enums occupy different architectural layers: C-CP-22 = engine-native pause +
replay-resumption mechanics (U-CP-49 surface); C-CP-26 = workflow-driver
explicit-pause + material-diff resumption mechanics. Per workspace
`.harness/class_1_fork_u_cp_63_pause_reason_collision.md` operator-ratified
path γ + CP spec v1.11 §26 NEW NOTE coexistence.

Authority: CP spec v1.11 §26.2 (NEW C-CP-26 PauseResumeProtocol; path γ
identifier rename absorbed); plan unit U-CP-62 (CP plan v2.17 §1).
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict

from harness_cp.handoff_context import StateSummary

if TYPE_CHECKING:
    from harness_cp.hitl_placement import HITLResult


class WorkflowPauseReason(StrEnum):
    """The 5-class workflow-layer pause reason (CP spec v1.11 §26.2).

    Distinct from the engine-layer `PauseReason` at C-CP-22 §22.1 / U-CP-49.
    Per CP spec v1.11 §26 NEW NOTE: C-CP-22 anchors at engine-native pause +
    replay-resumption; C-CP-26 anchors at workflow-driver explicit-pause +
    material-diff resumption. The two protocols coexist as distinct
    architectural primitives at distinct layers.
    """

    EXPLICIT_OPERATOR = "explicit_operator"
    """Operator-initiated pause from outside the workflow loop."""

    HITL_PENDING = "hitl_pending"
    """HITL gate opened; workflow paused awaiting operator response."""

    VALIDATOR_ESCALATION = "validator_escalation"
    """Validator framework escalated to HITL; workflow paused for arbitration."""

    TIMEOUT_BOUNDARY = "timeout_boundary"
    """Step or workflow-layer timeout boundary crossed; system-triggered pause."""

    EXTERNAL_DEPENDENCY = "external_dependency"
    """External dependency unavailable (e.g., MCP server, LLM provider);
    system-triggered pause pending dependency recovery."""


class MaterialDiffPolicy(StrEnum):
    """The 3-class material-diff resumption policy (CP spec v1.11 §26.2).

    `STRICT` is the default per Decision 2.D7 RATIFIED — any diff aborts
    resumption. `LENIENT` permits resumption when only non-behavior-changing
    diffs are detected. `OPERATOR_ARBITRATE` escalates any diff to HITL.
    """

    STRICT = "strict"
    """Any diff aborts resumption (DEFAULT per Decision 2.D7)."""

    LENIENT = "lenient"
    """Only behavior-changing diffs abort resumption."""

    OPERATOR_ARBITRATE = "operator_arbitrate"
    """Any diff escalates to HITL for operator arbitration."""


class FanOutBranchResumeState(BaseModel):
    """Per-branch terminal disposition + recovered output for a paused fan-out.

    B-FANOUT-PAUSE (R-FS-1) — one row per fan-out worker branch that reached a
    terminal disposition before the `cascade_policy=pause` halt. A branch absent
    from `FanOutResumeState.branches` is **left re-dispatchable** (the §25.15.1
    pause semantic: "in-flight finish; not-yet-dispatched left re-dispatchable")
    — `api.resume` re-dispatches it. A branch present here MUST NOT be
    re-dispatched (§25.15.2 obligation 7: a `completed`/`timed_out`/`cancelled`
    branch is terminal); its `output` is recovered into the resumed aggregate.

    The terminal_status mirrors the persisted Route-Y `branch_metadata.terminal_status`
    (§25.13): `completed` = the branch's dispatch ran (effect may have landed —
    incl. a ran-and-errored worker, dispatch-boundary semantic per obligation 4);
    `timed_out` = the barrier deadline cut an in-flight branch.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    branch_index: int
    """The fan-out branch ordinal (0-based). For `ORCHESTRATOR_WORKERS` this is the
    worker `steps[1:]` position; for `PARALLELIZATION` (B-FANOUT-PAUSE-PARALLELIZATION,
    a peer fan-out with NO orchestrator `steps[0]`) it is the `steps` position
    directly."""

    step_id: str
    """The branch's `WorkflowStep.step_id` AT CAPTURE TIME. Resume validates the
    re-supplied branch step's `step_id` against this (identity, not just the
    declared branch count) so a same-count body change (a branch rename / reorder)
    fails closed rather than silently attributing recovered output to the wrong
    step. (Full anchor-reachability material-diff is the deferred U-CP-22 arc;
    this is the cheap positional-identity guard.) Strategy-neutral: the orchestrator
    fan-out re-derives it from `worker_steps[branch_index]`, the peer fan-out from
    `steps[branch_index]`."""

    terminal_status: str
    """The persisted branch disposition: `completed` | `timed_out` (the
    discriminating Route-Y `terminal_status`, §25.15.2 obligation 4)."""

    output: Mapping[str, Any] | None = None
    """The completed branch's dispatch output, recovered into the resumed
    aggregate. `None` for a branch that ran-and-errored or timed out (it
    contributed nothing to the original aggregate — preserved as terminal so
    obligation 7 does not re-dispatch its possibly-landed effect)."""


class FanOutResumeState(BaseModel):
    """Fan-out resume reconstruction state carried by a paused-fan-out PauseSnapshot.

    B-FANOUT-PAUSE (R-FS-1) — the self-contained, hash-integrity-checked resume
    source for a `cascade_policy=pause` fan-out halt. Materializes the §25.15.1
    `pause → PAUSED` row's "composes with C-CP-26 PauseResumeProtocol + C-RT-30
    `api.resume`" promise for the fan-out case, which position-only resume cannot
    represent (a fan-out paused at the worker barrier has no single `step_index`
    capturing which branches completed vs. need re-dispatch — `adversarial-review-
    r-fs-1-arc-14` F1-01).

    This is the materialization of the R-CC-1 design §1.1 re-open trigger ("a
    future execution model … would need a state-restoration story + a durable
    store carrying more than the [position-only] PauseSnapshot"): the completed
    branches' OUTPUTS do not survive in the ledger (it carries causality +
    `terminal_status`, not the dispatch output mapping), so they are carried here
    and `_compute_snapshot_hash` COVERS this field — a resumed aggregate trusts
    these recovered outputs, so they are integrity-checked, not a silent-tamper gap.

    Satisfies §25.15.2 obligation 7 ("`api.resume` reads each branch's persisted
    `terminal_status` and MUST NOT re-dispatch a `cancelled`/`completed`/`timed_out`
    branch"): `branches` IS that persisted per-branch terminal disposition.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    orchestrator_output: Mapping[str, Any]
    """The orchestrator step's (`steps[0]`) output, recovered on resume so the
    already-run orchestrator is NOT re-dispatched (it is a completed step; effect
    may have landed)."""

    orchestrator_step_id: str
    """The orchestrator step's (`steps[0]`) `step_id` AT CAPTURE TIME. Resume
    validates the re-supplied `steps[0].step_id` against this — the orchestrator
    output is recovered + its dispatch skipped, so a same-count body change that
    renames/reorders `steps[0]` would otherwise apply stale orchestrator output to
    a different body (Codex [P2]). Fail-closed on mismatch."""

    branches: tuple[FanOutBranchResumeState, ...]
    """The terminal branches (completed / timed_out) at pause time. A worker
    branch ordinal absent from this tuple is left re-dispatchable."""

    worker_count: int
    """The total declared worker count (`len(steps[1:])`) at pause time — bounds
    the re-dispatchable set (any ordinal in `range(worker_count)` not present in
    `branches` is re-dispatched). A material-diff guard at resume: a different
    `worker_count` means the workflow body changed."""

    paused_child_branches: tuple[PausedChildBranchResumeState, ...] = ()
    """B-HIERARCHICAL-PAUSE (R-FS-1) — worker branches whose recursive child
    sub-workflow itself returned `RunStatus.PAUSED` (a grandchild paused under
    `cascade_policy=pause`; HIERARCHICAL_DELEGATION reuses ORCHESTRATOR_WORKERS at
    each level, so a `SUB_AGENT_DISPATCH` worker can recurse + pause). DISTINCT
    from `branches` (terminal — MUST NOT re-dispatch) and from absent ordinals
    (re-dispatch FRESH): a paused-child branch is the THIRD disposition — re-entered
    on resume via the child's OWN `api.resume(child_snapshot)` so the grandchild's
    already-completed steps are NOT re-executed (re-dispatching it fresh would lose
    that work — `[[full-chain-witness-not-half-proofs]]`). Each row's
    `child_snapshot` (a full nested `PauseSnapshot`) is COVERED by
    `_compute_snapshot_hash` transitively: it lives inside `fan_out_resume`, whose
    `model_dump(mode="json")` the hash already serializes recursively, so a tampered
    grandchild cursor fails the parent resume recompute. Additive, default-empty:
    `_compute_snapshot_hash` DROPS this field from the canonical serialization when
    empty, so every pre-existing ORCHESTRATOR_WORKERS / pre-B-HIERARCHICAL-PAUSE
    snapshot hashes byte-identically (an old durable snapshot's dict, lacking this
    key, deserializes via the default + re-hashes unchanged). A worker ordinal here
    MUST NOT also appear in `branches` (the resume material-diff guard enforces no
    overlap — terminal vs paused-child are disjoint dispositions)."""


class PeerFanOutResumeState(BaseModel):
    """Peer fan-out (PARALLELIZATION) resume reconstruction state.

    B-FANOUT-PAUSE-PARALLELIZATION (R-FS-1) — the `PARALLELIZATION`-shaped sibling
    of `FanOutResumeState`. PARALLELIZATION is a PEER fan-out: every declared
    `WorkflowStep` is a branch (`branch_index = steps` ordinal), with NO orchestrator
    `steps[0]`. So this carrier has NO `orchestrator_output` / `orchestrator_step_id`
    (the illegal-state-unrepresentable choice: a peer fan-out has no orchestrator,
    so the orchestrator-bearing `FanOutResumeState` is NOT reused — its required
    orchestrator fields would be vacuous here, and loosening them to optional would
    make `orchestrator_output=None` representable for an ORCHESTRATOR_WORKERS snapshot,
    an illegal state for that strategy). `branches` + `branch_count` are the peer
    analogues of `FanOutResumeState.branches` + `worker_count`.

    Carried by `PauseSnapshot.peer_fan_out_resume` (the second additive, defaulted
    field — never co-set with `fan_out_resume`; the strategy that captured the pause
    selects which is populated). Materializes the §25.15.1 `pause → PAUSED` row for
    PARALLELIZATION + the §25.15.2 obligation-7 ledger-based resume reconstruction,
    exactly as `FanOutResumeState` does for ORCHESTRATOR_WORKERS (CP spec v1.44 §1).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    branches: tuple[FanOutBranchResumeState, ...]
    """The terminal branches (completed / timed_out) at pause time. A branch ordinal
    absent from this tuple is left re-dispatchable (the §25.15.1 pause semantic)."""

    branch_count: int
    """The total declared branch count (`len(steps)`) at pause time — bounds the
    re-dispatchable set (any ordinal in `range(branch_count)` not present in
    `branches` is re-dispatched). A material-diff guard at resume: a different
    `branch_count` means the workflow body changed."""


class HandoffStageResumeState(BaseModel):
    """One completed stage of a `DECENTRALIZED_HANDOFF` paused at a later stage.

    B-HANDOFF-PAUSE (R-FS-1) — `DECENTRALIZED_HANDOFF` is single-owner SEQUENTIAL
    (one stage-expert owns the workflow at a time, then hands off to the next via a
    `HandoffContext` record). When a stage fails under `cascade_policy=pause`, the
    completed-stage PREFIX is captured so resume recovers their outputs (the ledger
    carries causality, not the dispatch output mapping) WITHOUT re-executing them.

    Distinct from the fan-out carriers' `FanOutBranchResumeState`: handoff stages are
    a CONTIGUOUS sequential prefix (`stage_index` 0..k-1 for a pause at stage k), not a
    set of terminal branches with re-dispatchable gaps. There is no `terminal_status`
    (a handoff stage either completed — recovered here — or is the failed/not-yet-run
    stage at/after the cursor, re-dispatched on resume)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    stage_index: int
    """The declared stage ordinal (0-based `steps` position) that completed. The
    captured prefix is contiguous `0..k-1` for a pause at stage `k`."""

    step_id: str
    """The stage `WorkflowStep.step_id` AT CAPTURE TIME. Resume validates the
    re-supplied `steps[stage_index].step_id` against this (positional-identity guard,
    fail-closed on a same-count rename/reorder — the recovered output is replayed into
    this stage's slot + its dispatch skipped, so a renamed body would mis-attribute)."""

    output: Mapping[str, Any]
    """The completed stage's dispatch output, recovered on resume so the stage is NOT
    re-dispatched (it is a completed step; effect may have landed) — replayed into the
    aggregate `stages` map + re-seeded into the inter-step output channel so the next
    stage reads its upstream context (B-INTERSTEP-HANDOFF, runtime §14.21). COVERED by
    `_compute_snapshot_hash` (a resumed aggregate trusts it → integrity-checked)."""


class HandoffResumeState(BaseModel):
    """Single-owner sequential handoff resume reconstruction state (the stage cursor).

    B-HANDOFF-PAUSE (R-FS-1) — the `DECENTRALIZED_HANDOFF` analogue of
    `FanOutResumeState` / `PeerFanOutResumeState`, but a STAGE CURSOR rather than a
    branch set: handoff is single-owner sequential, so a pause at stage `k` has a
    contiguous completed prefix `0..k-1` and re-dispatches from stage `k` onward.

    Materializes the §25.15.1 `pause → PAUSED` row EXTENDED to the single-owner
    sequential case (the §25.15.1 row text is fan-out-barrier-scoped; this extension
    is the §25.18-named `DECENTRALIZED_HANDOFF` impl-discretion materialization — the
    last/hardest strategy in the §25.18 simplest→hardest order). No new orchestrator
    fields (no `steps[0]` orchestrator; no peer-branch set): just the completed-stage
    prefix + the declared stage count.

    Carried by `PauseSnapshot.handoff_resume` (the THIRD additive, defaulted resume
    field — never co-set with `fan_out_resume` / `peer_fan_out_resume`; the capturing
    strategy populates exactly one). On resume, `_execute_decentralized_handoff`
    re-walks the body: the recovered prefix's outputs are replayed (NOT re-dispatched),
    the handoff-chain `parent_action_id` is recomputed deterministically through the
    prefix (so the resumed stage chains off the last completed stage's `action_id`, NOT
    re-anchored to the workflow origin — the load-bearing handoff causality), and stage
    `k` onward is dispatched fresh."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    completed_stages: tuple[HandoffStageResumeState, ...]
    """The contiguous completed-stage prefix (`stage_index` 0..k-1) at pause time. A
    stage ordinal at/after `len(completed_stages)` is re-dispatched on resume. A RE-pause
    (pause→resume→pause) unions the recovered prefix + the newly-completed-on-resume
    stages, so this stays a contiguous prefix across repeated resumes."""

    stage_count: int
    """The total declared stage count (`len(steps)`) at pause time. A material-diff
    guard at resume: a different `stage_count` means the workflow body changed →
    fail-closed rather than recover stale outputs into a changed body."""


class EvaluatorOptimizerStepResumeState(BaseModel):
    """One completed generate-or-evaluate step of an `EVALUATOR_OPTIMIZER` loop paused later.

    B-FANOUT-PAUSE-EVALUATOR-OPTIMIZER (R-FS-1) — `EVALUATOR_OPTIMIZER` is a SEQUENTIAL
    generate→evaluate→regenerate loop (NO fan-out, NO branches, NO `branch_metadata`),
    bounded by a max-iteration cap. When a generate/evaluate dispatch fails under
    `cascade_policy=pause`, the contiguous completed-STEP prefix is captured so resume
    recovers each step's output WITHOUT re-dispatching it (a completed step's effect may
    have landed).

    The #681 `HandoffStageResumeState` analogue, but the cursor unit is a LOOP STEP
    (generate or evaluate) keyed by the MONOTONIC `entry_index` (the ledger row index),
    not a declared stage ordinal: the EO loop re-dispatches the SAME two declared steps
    across iterations, so the resume cursor is entry-granular. The iteration semantics
    (which iteration, the cap) DERIVE from `entry_index` parity (even ⟹ generate, odd ⟹
    evaluate; iteration = entry_index // 2) — no separate iteration field is stored."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    entry_index: int
    """The MONOTONIC ledger-row index (0,1,2,3,…) of this completed loop step. The
    captured prefix is contiguous `0..m-1` for a pause at the failed step `m`. Even ⟹ a
    generate dispatch, odd ⟹ an evaluate dispatch (the loop alternates strictly)."""

    declared_step_index: int
    """The DECLARED step ordinal (0=generate, 1=evaluate) this entry dispatched. Resume
    validates `declared_step_index == entry_index % 2` (loop-alternation coherence) and
    `steps[declared_step_index].step_id == step_id` (positional-identity guard)."""

    step_id: str
    """The `WorkflowStep.step_id` AT CAPTURE TIME (`steps[0]`=generate / `steps[1]`=evaluate).
    Resume validates the re-supplied `steps[declared_step_index].step_id` against this —
    fail-closed on a body rename so a recovered output is never replayed into a renamed
    step's slot (the recovered step's dispatch is skipped on resume)."""

    output: Mapping[str, Any]
    """This completed step's dispatch output, recovered on resume so the step is NOT
    re-dispatched. Replayed into the inter-step output channel (so the next live step
    reads its upstream draft/feedback — B-INTERSTEP, runtime §14.21) and into
    `last_generate_output` / `last_evaluation` for the SUCCESS final_state. COVERED by
    `_compute_snapshot_hash` (a resumed loop trusts it → integrity-checked)."""


class EvaluatorOptimizerResumeState(BaseModel):
    """Sequential generate→evaluate loop resume reconstruction state (the iteration cursor).

    B-FANOUT-PAUSE-EVALUATOR-OPTIMIZER (R-FS-1) — the `EVALUATOR_OPTIMIZER` analogue of
    `HandoffResumeState`: a single-owner SEQUENTIAL cursor (no peer-branch set), but over
    the loop's completed STEPS rather than a stage list. A pause at the failed step `m`
    has a contiguous completed-step prefix `0..m-1`; resume recovers their outputs and
    re-dispatches from step `m` onward, honoring the original max-iteration cap across the
    resume boundary (the cap is reconstructed from the recovered generate count — every
    iteration has exactly one generate).

    Materializes the §25.15.1 `pause → PAUSED` row EXTENDED to the sequential
    `EVALUATOR_OPTIMIZER` case (the §25.15.1 row text is fan-out-barrier-scoped; this
    extension is the §25.18-named `EVALUATOR_OPTIMIZER` impl-discretion materialization,
    mirroring the #681 `DECENTRALIZED_HANDOFF` extension). Only `cascade_policy=pause`
    (TEAM tier, with a bound `pause_resume_protocol`) is materialized; `proceed` /
    `cascade-cancel` retain EO's existing terminal-FAILED disposition.

    Carried by `PauseSnapshot.evaluator_optimizer_resume` (the FOURTH additive, defaulted
    resume field — never co-set with `fan_out_resume` / `peer_fan_out_resume` /
    `handoff_resume`; the capturing strategy populates exactly one)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    completed_steps: tuple[EvaluatorOptimizerStepResumeState, ...]
    """The contiguous completed-step prefix (`entry_index` 0..m-1) at pause time. A step
    at/after `len(completed_steps)` is re-dispatched on resume. A RE-pause unions the
    recovered prefix + the newly-completed-on-resume steps, so this stays a contiguous
    prefix across repeated resumes. The recovered-generate count reconstructs the
    iteration cap across the resume boundary; recovered evaluations are all non-accepts by
    construction (an accept would have terminated the loop SUCCESS, not paused)."""


class PauseSnapshot(BaseModel):
    """8-field pause-snapshot envelope (CP spec v1.11 §26.2).

    Captures the pause-point state digest plus the state-ledger anchor and
    a canonical-serialization sha256 snapshot hash. Frozen after capture per
    §26.6 invariant 1; resume must validate `snapshot_hash` per invariant 2.

    The `state_ledger_anchor` carries the C-IS-05 §5 `entry_hash` at the
    pause point; material-diff detection at U-CP-64 checks whether this
    anchor remains reachable from the current entry chain (§26.6 invariant 3).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    workflow_id: str
    """Workflow identifier owning this pause."""

    run_id: str
    """Run identifier owning this pause."""

    step_index: int
    """Step index at which pause was captured."""

    pause_reason: WorkflowPauseReason
    """Why the workflow paused (5-class enum per §26.2)."""

    state_summary: StateSummary
    """Across-turn state digest at pause point (Pattern-D inherited from CP
    plan v2.9 + C-CP-13 §13.4)."""

    snapshot_hash: str
    """sha256 hex string (64 chars) over canonical serialization of
    (workflow_id + run_id + step_index + state_summary)."""

    created_at: int
    """Epoch ms at snapshot capture."""

    state_ledger_anchor: str
    """C-IS-05 §5 `entry_hash` at pause point. Material-diff detection at
    U-CP-64 checks reachability from current entry chain."""

    fan_out_resume: FanOutResumeState | None = None
    """B-FANOUT-PAUSE (R-FS-1) — fan-out resume reconstruction state, present
    ONLY when this snapshot captures a `cascade_policy=pause` fan-out halt
    (`None` for every linear / single-step pause — additive, default-None, so
    existing 8-field snapshots are byte-unchanged and still validate).

    When present, `_compute_snapshot_hash` COVERS it (the resumed aggregate
    trusts the recovered completed-branch outputs → integrity-checked, no
    silent-tamper gap), and `api.resume` re-enters the fan-out strategy with it:
    terminal branches are skipped (outputs recovered), absent branch ordinals
    re-dispatched (§25.15.2 obligation 7)."""

    peer_fan_out_resume: PeerFanOutResumeState | None = None
    """B-FANOUT-PAUSE-PARALLELIZATION (R-FS-1) — the `PARALLELIZATION` (peer fan-out)
    analogue of `fan_out_resume`, present ONLY when this snapshot captures a
    `PARALLELIZATION` `cascade_policy=pause` halt (`None` otherwise — additive,
    default-None, so every existing snapshot is byte-unchanged). NEVER co-set with
    `fan_out_resume`: the strategy that captured the pause populates exactly one (an
    ORCHESTRATOR_WORKERS pause sets `fan_out_resume`; a PARALLELIZATION pause sets
    this). COVERED by `_compute_snapshot_hash` when present (same integrity contract
    as `fan_out_resume`); `api.resume` re-enters `_execute_parallelization` with it
    (terminal branches skipped, outputs recovered; absent ordinals re-dispatched)."""

    handoff_resume: HandoffResumeState | None = None
    """B-HANDOFF-PAUSE (R-FS-1) — the `DECENTRALIZED_HANDOFF` (single-owner sequential)
    analogue of `fan_out_resume` / `peer_fan_out_resume`, present ONLY when this snapshot
    captures a `DECENTRALIZED_HANDOFF` `cascade_policy=pause` halt (`None` otherwise —
    additive, default-None, so every existing snapshot is byte-unchanged). NEVER co-set
    with `fan_out_resume` / `peer_fan_out_resume`: the strategy that captured the pause
    populates exactly one (a handoff pause sets this). COVERED by `_compute_snapshot_hash`
    when present (same integrity contract); `api.resume` re-enters
    `_execute_decentralized_handoff` with it (the completed-stage prefix's outputs
    recovered + their dispatch skipped; stage `k` onward re-dispatched, the handoff chain
    recomputed through the prefix)."""

    evaluator_optimizer_resume: EvaluatorOptimizerResumeState | None = None
    """B-FANOUT-PAUSE-EVALUATOR-OPTIMIZER (R-FS-1) — the `EVALUATOR_OPTIMIZER`
    (single-owner sequential generate→evaluate loop) analogue of `fan_out_resume` /
    `peer_fan_out_resume` / `handoff_resume`, present ONLY when this snapshot captures an
    `EVALUATOR_OPTIMIZER` `cascade_policy=pause` halt (`None` otherwise — additive,
    default-None, so every existing snapshot is byte-unchanged). NEVER co-set with the
    other three resume carriers: the strategy that captured the pause populates exactly
    one (an EO pause sets this). COVERED by `_compute_snapshot_hash` when present (same
    integrity contract); `api.resume` re-enters `_execute_evaluator_optimizer` with it
    (the completed-step prefix's outputs recovered + their dispatch skipped; the loop
    re-dispatches from the failed step onward, honoring the original iteration cap)."""


class PausedChildBranchResumeState(BaseModel):
    """A worker branch whose recursive child sub-workflow returned `RunStatus.PAUSED`.

    B-HIERARCHICAL-PAUSE (R-FS-1) — HIERARCHICAL_DELEGATION reuses ORCHESTRATOR_WORKERS
    at each recursion level (`workflow_driver._execute_hierarchical_delegation`), so a
    `SUB_AGENT_DISPATCH` worker can re-enter the driver for a child sub-workflow that
    itself pauses (a grandchild branch failing under `cascade_policy=pause`). That
    child PAUSE — previously swallowed as success-equivalent at the sub-agent dispatch
    boundary — is now surfaced + captured here so the parent fan-out pauses honestly
    and `api.resume` re-enters the child at its own cursor.

    Carried by `FanOutResumeState.paused_child_branches` (NOT `branches`: a terminal
    branch MUST NOT be re-dispatched, but a paused-child branch MUST be — via the
    child's own resume, not a fresh dispatch — the illegal-states-unrepresentable
    split that keeps the two dispositions type-distinct, mirroring the
    `FanOutResumeState` vs `PeerFanOutResumeState` choice at #679).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    branch_index: int
    """The fan-out worker ordinal (0-based, the `steps[1:]` position) whose child
    sub-workflow paused. On resume this ordinal is re-dispatched THROUGH the child's
    own resume (NOT skipped like a terminal branch, NOT fresh like an absent one)."""

    step_id: str
    """The worker `WorkflowStep.step_id` AT CAPTURE TIME. Resume validates the
    re-supplied worker step's `step_id` against this (positional-identity guard,
    fail-closed on a same-count rename/reorder — the same cheap guard
    `FanOutBranchResumeState` applies to terminal branches)."""

    child_snapshot: PauseSnapshot
    """The child sub-workflow's OWN terminal `PauseSnapshot` (`RunResult.pause_snapshot`
    at the child's PAUSED return). On resume, the worker re-dispatch threads this as
    the child's `execute_workflow(pause_snapshot_input=...)` so the child re-enters at
    its cursor — the grandchild's already-completed steps are recovered, NOT
    re-executed. Nested recursively: this child snapshot may itself carry a
    `fan_out_resume` with its own `paused_child_branches` (a grandchild that paused on
    a great-grandchild). COVERED by `_compute_snapshot_hash` transitively via the
    enclosing `fan_out_resume.model_dump(mode="json")`."""


class ResumeResult(BaseModel):
    """5-field resume-attempt outcome envelope (CP spec v1.11 §26.2).

    Reports whether the resumption succeeded, whether a material diff was
    detected, and the optional new `run_id` if resumption required a fresh
    run identifier. `diff_summary_hash` is sha256 of the diff serialization
    (format owed to U-CP-22 implementation arc per §26.7).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    resumed: bool
    """True iff workflow resumed successfully; False on diff-abort, snapshot
    corruption, or arbitration-owed escalation."""

    diff_detected: bool
    """True iff U-CP-64 material-diff detection found a diff."""

    diff_summary_hash: str | None = None
    """sha256 hex of diff-set canonical serialization; None when no diff
    detected. Format owed to U-CP-22 implementation per §26.7."""

    new_run_id: str | None = None
    """Fresh run_id if resumption required one; None when same run_id reused."""

    fail_class: str | None = None
    """CP-FAIL-* class identifier on resume failure; None on clean resume.
    One of CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION, CP-FAIL-RESUME-MATERIAL-DIFF-DETECTED,
    CP-FAIL-RESUME-OPERATOR-ARBITRATION-OWED per §26.5."""


class ResumeContext(BaseModel):
    """Operator-supplied resume-time context envelope (CP spec v1.16 §26.8.1).

    Authored at CP spec v1.16 to enable HITL-gate-as-pause-trigger composition
    per runtime spec v1.21 §14.14.7 deferred-discretion residual (i) resolution.
    The envelope carries operator-supplied data the resumed step must consume
    during the resume cycle. v1.16 authors a single field for the durable-async
    HITL response delivery surface; future arcs may extend per v1.16 §26.8.1
    change-note adjacent defect (i).

    Consumed by runtime spec v1.24 §14.8.2 step 4-bis (the HITL gate composer
    body durable-async branch on resumed-step re-entry). The CP-side
    `attempt_resume(...)` method ingests but does NOT consume `ResumeContext`
    per CP spec v1.16 §26.8.5 method-body-posture-at-v1.16 framing.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    hitl_response: HITLResult | None = None
    """Operator HITL response delivered during durable-async pause.

    None when the pause was not correlated with a HITL gate (e.g.,
    EXPLICIT_OPERATOR, TIMEOUT_BOUNDARY, EXTERNAL_DEPENDENCY pause reasons).
    Populated HITLResult when the pause was triggered by a HITL gate composer
    body firing on durable-async cell synchrony per C-CP-18 §18.1 and the
    operator has delivered a response via the inbound webhook endpoint.
    HITLResult shape canonical at C-CP-17 §17.1.1 (`harness_cp.hitl_placement`).
    """


# B-HIERARCHICAL-PAUSE (R-FS-1) — `FanOutResumeState.paused_child_branches` forward-refs
# `PausedChildBranchResumeState` (defined after `PauseSnapshot`, which it nests), so the
# annotation cannot resolve at `FanOutResumeState` class-build time (it is the FIRST
# forward reference in this module — `PauseSnapshot.fan_out_resume` resolves backward).
# Rebuild once now that every referenced model exists. `PausedChildBranchResumeState`
# itself needs no rebuild (its `PauseSnapshot` ref is backward).
FanOutResumeState.model_rebuild()
