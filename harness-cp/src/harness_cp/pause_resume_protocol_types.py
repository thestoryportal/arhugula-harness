"""C-CP-26 PauseResumeProtocol type carriers — 2 enums + 2 envelope models.

U-CP-62 — first unit of cluster 10-CP-B. Declares the type carriers that the
C-CP-26 PauseResumeProtocol class body (U-CP-63 capture_pause_snapshot + U-CP-64
attempt_resume) and the pause/resume span emitter (U-CP-65) consume at runtime:

- `WorkflowPauseReason` — 6-class workflow-layer pause taxonomy (CP spec §26.2;
  renamed from `PauseReason` at v1.11 per path γ disambiguation; EFFECT_FENCE_AMBIGUOUS
  added for B-EFFECT-FENCE-HITL-ROUTE)
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

from pydantic import BaseModel, ConfigDict, PrivateAttr

from harness_cp.handoff_context import StateSummary

if TYPE_CHECKING:
    from harness_cp.hitl_placement import HITLResult


class WorkflowPauseReason(StrEnum):
    """The 6-class workflow-layer pause reason (CP spec §26.2; the 5 v1.11 members
    + EFFECT_FENCE_AMBIGUOUS added for B-EFFECT-FENCE-HITL-ROUTE).

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

    EFFECT_FENCE_AMBIGUOUS = "effect_fence_ambiguous"
    """Effect fence (runtime spec §14.22 C-RT-31) lost a reserve to a prior
    uncommitted attempt of a non-idempotent effect AND found no captured output
    proving completion (the crash fell in the fire→capture window). Whether the
    effect fired is ambiguous, so the runtime fails to the operator rather than
    auto-re-fire (at-most-once). System-triggered, driver-routed pause
    (B-EFFECT-FENCE-HITL-ROUTE; the runtime ``EffectFenceAmbiguousUncommittedError``
    name-matched at the §26-driver step-dispatch boundary)."""


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


class EffectFenceResolution(StrEnum):
    """The operator's resume-side resolution of a §26.2 `EFFECT_FENCE_AMBIGUOUS` pause.

    B-EFFECT-FENCE-PAUSE-RESOLUTION (R-FS-1) — the §14.22 C-RT-31 effect fence
    pauses (via `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS`) when a re-dispatch
    lost the per-(run, step, tool) reserve AND no captured output proves the
    non-idempotent effect completed: whether the effect fired is genuinely
    ambiguous and the harness CANNOT compute the answer (the crash fell in the
    fire→capture window). The fence pauses *to ask the operator one question — did
    the effect fire?* These three resolutions are the operator ANSWERING with
    ground-truth the harness lacks (e.g. checking whether the email was sent / the
    git push landed). Delivered one-shot via `ResumeContext.effect_fence_resolution`
    on `api.resume`; key-bound to the paused effect via
    `PauseSnapshot.effect_fence_resume.idempotency_key`.

    Answering the fence's question is IN-DOMAIN — it COMPLETES the at-most-once
    decision the harness couldn't compute, it does NOT override the guarantee. A
    mis-assertion is operator-error responsibility (the C-AS-03 `idempotent` /
    `blast_radius_tier` mis-declaration posture).
    """

    SKIP_AS_FIRED = "skip_as_fired"
    """Operator asserts the effect FIRED (the prior attempt fired, then crashed
    before capturing its output). Proceed treating the step as complete — but the
    lost output is genuinely unrecoverable, so the step yields EMPTY output. NEVER
    re-fires the effect. Downstream consumers that needed the lost output fail
    honestly (the data is gone)."""

    RE_FIRE = "re_fire"
    """Operator asserts the effect did NOT fire (the prior attempt claimed the
    reserve, then crashed before firing). Clear the held claim and re-dispatch the
    step fresh — a FIRST-and-only execution, still at-most-once from the true state
    of the world. The operator supplies the ground-truth the fence couldn't compute."""

    ABORT = "abort"
    """Operator cannot determine whether the effect fired (or chooses not to
    proceed). Fail the run terminally (the conservative default — never re-fire,
    never proceed-with-empty)."""

    ABORT_BRANCH = "abort_branch"
    """B-FANOUT-EFFECT-FENCE-PER-BRANCH-SCOPED-ABORT (R-FS-1) — per-branch-SCOPED
    abort: fail just THIS fan-out branch (record it terminal, never re-fire) while
    the SIBLING branches the operator CAN vouch for (SKIP_AS_FIRED / RE_FIRE) resolve
    and FIRE, and the run folds the survivors per `cascade_policy`. Distinct from
    `ABORT`, which is RUN-level terminal (the whole run FAILS, all continue-resolutions
    suppressed — v1.65 §1(b), preserved byte-for-byte). `ABORT_BRANCH` is meaningful
    ONLY for a fan-out fence pause: it is consumed CP-side at the two fan-out resume sites
    (`_execute_parallelization` / `_execute_orchestrator_workers`) and NEVER threaded to the
    runtime fence (the at-most-once guarantee — the scoped-abort branch is never re-dispatched,
    so its ambiguous effect is never re-fired). A LINEAR fence pause has exactly one branch
    (scoping is vacuous); the runtime fence gate recognizes only SKIP_AS_FIRED / RE_FIRE /
    ABORT, so an `ABORT_BRANCH` supplied for a LINEAR pause is unrecognized → it falls through
    to the default no-resolution fence behavior (suppress-if-captured / else INERT re-pause via
    the decline-mirror, NEVER an auto-action) — use `ABORT` for a linear run-terminal abort. On
    a fan-out pause the scoped-abort branch's output is discarded (a degraded non-contributor)
    → the run folds to PARTIAL with the surviving branches (FAILED if NO survivor)."""


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


class PreDispatchGateOwningBranchResumeState(BaseModel):
    """A branch whose OWN HITL gate fired before any child run was dispatched.

    B-72 impl leg (CP spec v1.108 §1) — carries the CAPTURED `step_id` (out-of-
    family Codex [P1]: an ordinal-only carrier gives the resume-side material-diff
    guard, `_resume_body_mismatch`, no step identity to validate — unlike every
    other persisted branch disposition (`FanOutBranchResumeState`,
    `PausedChildBranchResumeState`, `EffectFencePausedBranchResumeState`), which
    would let a same-count body edit that REPLACES the paused step attach the
    operator's stored response to a DIFFERENT, unrelated step). Resume validates
    the re-supplied branch step's `step_id` against this — a same-count rename/
    reorder/replace fails closed rather than silently deliver a resolved answer
    to the wrong step's dispatch. `step_kind` + `child_workflow_id` (out-of-family
    Codex [P1], round 4; `step_kind` corrected at round 5) close NARROWER gaps
    the `step_id`-only guard left open. `step_kind` is a CAPTURED field, NOT a
    constant check against `StepKind.SUB_AGENT_DISPATCH` — round 5 caught round
    4's own false assumption that a pre-dispatch gate-owning branch is always
    that kind: `HITLPlacementKind.PRE_ACTION` can ALSO gate `INFERENCE_STEP`/
    `TOOL_STEP` steps and raises the SAME name-matched
    `HITLPauseRequestedSignal`, so an unchanged `PRE_ACTION`-gated branch would
    otherwise be rejected as a false material diff on resume — the
    `PausedChildBranchResumeState` (B-31) precedent this class originally
    mirrored does NOT apply here (that carrier IS uniquely `SUB_AGENT_DISPATCH`
    by construction — only that kind can raise `SubAgentChildPausedError` —
    whereas this one is genuinely multi-kind). `child_workflow_id` closes a
    separate gap: a same-`step_id` edit that swaps the target `child_workflow_id`
    previously passed undetected — the same identity dimension
    `PausedChildBranchResumeState` already validates, but here only meaningful
    (and only populated) when the captured `step_kind` is `SUB_AGENT_DISPATCH`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    branch_index: int
    """The fan-out branch ordinal (0-based), same convention as
    `FanOutBranchResumeState.branch_index`."""

    step_id: str
    """The branch's `WorkflowStep.step_id` AT CAPTURE TIME (the material-diff
    identity guard — see class docstring)."""

    step_kind: str
    """The branch's `WorkflowStep.step_kind.value` AT CAPTURE TIME (out-of-family
    Codex [P2], round 5). A pre-dispatch gate-owning branch can be
    `SUB_AGENT_DISPATCH` (`SUB_AGENT_BOUNDARY` placement) OR `INFERENCE_STEP`/
    `TOOL_STEP` (`PRE_ACTION` placement) — both raise the same signal, so this
    MUST be a captured value compared for equality, never a hardcoded constant
    (see class docstring for the round-4-then-corrected-at-round-5 history)."""

    child_workflow_id: str | None = None
    """The target child workflow's identifier AT CAPTURE TIME, read from
    `step.step_payload["child_workflow_id"]` via the same `_opaque_field`
    convention `PausedChildBranchResumeState.child_workflow_id` (B-31) already
    uses. Resume validates it against the re-supplied step's payload ONLY when
    present — default-`None` for byte-compat (`_strip_default_fanout_resume_fields`
    does not need to special-case it since the field lives inside a
    non-empty-tuple-gated carrier row, not a bare top-level field)."""

    hitl_gate_config_hash: str | None = None
    """B-79 impl leg slice 1 (CP spec v1.110 §1.2 property 7) — a sha256 hex
    digest over this branch's APPLICABLE HITL gate configuration AT CAPTURE
    TIME: the ADD-only-folded placement tuple (`fold_step_hitl_placements(
    manifest_entry.hitl_placements, binding.hitl_placement)`) plus the per-step
    `removed_placements` directive (`binding.removed_placements`) — see
    `_hash_hitl_gate_config`. Resume recomputes the same hash against the
    re-supplied step and rejects a mismatch as a material diff, exactly like
    `step_id`/`step_kind`/`child_workflow_id` above: a same-step_id edit that
    ADDS/REMOVES/ALTERS a placement (position, tool_filter, cascade_policy,
    timeout) or the removed-placements set would otherwise silently deliver
    the operator's stored `hitl_response` under a gate configuration different
    from the one that actually paused.

    default-`None` for byte-compat (out-of-family Codex [P1] — corrected from an
    initial `str`-required draft that broke `JournalWorkflowPauseStore._parse_
    snapshot`'s deserialization of an already-durable journal record captured by
    the PRECEDING `B-72` deployment: unlike `child_workflow_id` above, this field
    is being added to an ALREADY-SHIPPED carrier row type, not introduced
    alongside a brand-new one, so a real pre-existing durable snapshot with this
    field absent from its JSON MUST still deserialize + hash + resume
    successfully). Resume SKIPS the gate-config comparison when the CAPTURED
    (snapshot) value is `None` — mirrors `child_workflow_id`'s own "validate
    ONLY when present" convention — rather than treating an unrecoverable legacy
    absence as a rejection. `_strip_default_fanout_resume_fields` DOES
    special-case this one (unlike `child_workflow_id`): a legacy row's `None`
    must drop from the hash-covered dump so its recomputed `snapshot_hash`
    stays byte-identical to how it hashed under the preceding deployment."""


class FanOutResumeState(BaseModel):
    """Fan-out resume reconstruction state carried by a paused-fan-out PauseSnapshot.

    B-FANOUT-PAUSE (R-FS-1) — the self-contained, hash-integrity-checked resume
    source for a `cascade_policy=pause` fan-out halt. Materializes the §25.15.1
    `pause → PAUSED` row's "composes with C-CP-26 PauseResumeProtocol + C-RT-35
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

    synthesis_step_id: str | None = None
    """B-FANOUT-PAUSE-SYNTHESIS (R-FS-1) — the terminal `POST_JOIN_SYNTHESIS` step's
    `step_id` AT PAUSE-CAPTURE TIME, or `None` when the fan-out carried no opt-in
    synthesis. The captured synthesis IDENTITY (presence + step_id). On a pause the
    synthesis NEVER ran (the pause halts at the worker barrier, BEFORE the post-join
    synthesis), so there is nothing to replay — but resume MUST material-diff the
    re-supplied terminal synthesis step against this identity (synthesis added /
    removed / changed `step_id` → fail closed) BEFORE fresh-dispatching it on the
    recovered + re-dispatched branches (effect-free, first-and-only per B-POSTJOIN).
    Additive, default-None: `_compute_snapshot_hash` DROPS this field from the
    canonical serialization when None, so every pre-existing / non-synthesis
    ORCHESTRATOR_WORKERS snapshot hashes byte-identically (an old durable snapshot's
    dict, lacking this key, deserializes via the default + re-hashes unchanged —
    the same `paused_child_branches` drop-when-empty discipline)."""

    effect_fence_paused_branches: tuple[EffectFencePausedBranchResumeState, ...] = ()
    """B-FANOUT-EFFECT-FENCE-BRANCH-PAUSE (R-FS-1) — branches whose own dispatch raised the
    runtime effect fence's `EffectFenceAmbiguousUncommittedError` (C-RT-31 §14.22). DISTINCT from
    `branches` (terminal — MUST NOT re-dispatch), from absent ordinals (re-dispatch FRESH), and
    from `paused_child_branches` (a SUB_AGENT child sub-workflow paused): an effect-fence-paused
    branch is re-entered on resume via the fence-keyed `EffectFenceResolution` (SKIP_AS_FIRED /
    RE_FIRE / ABORT), NOT a fresh dispatch — the fan-out analogue of the LINEAR-path
    B-EFFECT-FENCE-HITL-ROUTE. Additive, default-empty: `_compute_snapshot_hash` DROPS this field
    from the canonical serialization when empty, so every pre-existing snapshot hashes
    byte-identically (the `paused_child_branches` drop-when-empty discipline)."""

    pre_dispatch_gate_owning_branches: tuple[PreDispatchGateOwningBranchResumeState, ...] = ()
    """B-72 impl leg (CP spec v1.108 §1.1/§1.3a) — worker branches whose OWN
    `SUB_AGENT_BOUNDARY` (or equivalent) HITL gate fired BEFORE any child run was
    dispatched (the runtime's `HITLPauseRequestedSignal`, raised ahead of
    `RuntimeSubAgentDispatcher.dispatch`). DISTINCT from `branches` (terminal — MUST
    NOT re-dispatch), from `paused_child_branches` (a child run WAS dispatched and
    itself paused), and from `effect_fence_paused_branches` (a different signal):
    a pre-dispatch gate-owning branch has no child `run_id` to key `hitl_responses`
    by (property 6 §1.1(b) forbids ever keying it there), so it is re-dispatched
    FRESH on resume like an absent ordinal — this field exists ONLY so the resolver
    can COUNT it into property 4's unaddressed gate-owning set (§1.1(a)) and, when it
    is the cycle's sole unaddressed member, DELIVER it the uniform `hitl_response` via
    a delivery-cell construction at the branch's own re-dispatch site (§1.1(b)). Each
    row carries its captured `step_id` (out-of-family Codex [P1]: the resume-side
    material-diff guard needs a step identity to validate, mirroring every other
    persisted branch disposition — see `PreDispatchGateOwningBranchResumeState`'s
    own docstring). The internal identity `_collect_gate_owning_run_ids` derives for
    each ordinal here composes THIS `PauseSnapshot`'s own tree-wide-unique `run_id`
    with the ordinal (§1.1(d)'s tree-wide-uniqueness requirement) — never placed in,
    or compatible with, `hitl_responses`. Additive, default-empty:
    `_compute_snapshot_hash` DROPS this field from the canonical serialization when
    empty, so every pre-existing
    snapshot hashes byte-identically (the `effect_fence_paused_branches` drop-when-
    empty discipline)."""


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

    paused_child_branches: tuple[PausedChildBranchResumeState, ...] = ()
    """B-21 (R-FS-1) — the PARALLELIZATION analogue of
    `FanOutResumeState.paused_child_branches`: peer branches whose own dispatch is a
    `SUB_AGENT_DISPATCH` step whose recursive child sub-workflow itself returned
    `RunStatus.PAUSED` (a grandchild paused under `cascade_policy=pause`; the runtime
    `SUB_AGENT_DISPATCH` dispatcher is topology-agnostic, so a PARALLELIZATION peer
    branch can recurse + pause exactly as an ORCHESTRATOR_WORKERS worker can). DISTINCT
    from `branches` (terminal — MUST NOT re-dispatch) and from an absent ordinal
    (re-dispatch FRESH): a paused-child branch is the THIRD disposition — re-entered on
    resume via the child's OWN `api.resume(child_snapshot)` so the grandchild's
    already-completed steps are NOT re-executed (re-dispatching it fresh would lose
    that work — `[[full-chain-witness-not-half-proofs]]`). Each row's `child_snapshot`
    is COVERED by `_compute_snapshot_hash` transitively (it lives inside
    `peer_fan_out_resume`, whose `model_dump(mode="json")` the hash already serializes
    recursively). Additive, default-empty: `_compute_snapshot_hash` DROPS this field
    from the canonical serialization when empty (the `synthesis_step_id` /
    `effect_fence_paused_branches` drop-when-empty discipline), so every pre-existing
    PARALLELIZATION snapshot hashes byte-identically. A peer ordinal here MUST NOT also
    appear in `branches` (the resume material-diff guard enforces no overlap —
    terminal vs paused-child are disjoint dispositions, mirroring
    `FanOutResumeState.paused_child_branches`)."""

    synthesis_step_id: str | None = None
    """B-FANOUT-PAUSE-SYNTHESIS (R-FS-1) — the PARALLELIZATION analogue of
    `FanOutResumeState.synthesis_step_id`: the terminal `POST_JOIN_SYNTHESIS` step's
    `step_id` at pause-capture time, `None` when no synthesis was opted in. Same
    material-diff-on-resume + fresh-dispatch contract; same additive, default-None,
    drop-from-hash-when-None byte-compat discipline (the `_compute_snapshot_hash` peer
    drop mirrors the FanOut drop — `PeerFanOutResumeState` had no drop before this
    field, so the drop is ADDED at the same site)."""

    effect_fence_paused_branches: tuple[EffectFencePausedBranchResumeState, ...] = ()
    """B-FANOUT-EFFECT-FENCE-BRANCH-PAUSE (R-FS-1) — the PARALLELIZATION analogue of
    `FanOutResumeState.effect_fence_paused_branches`: peer branches whose own dispatch raised the
    runtime effect fence's `EffectFenceAmbiguousUncommittedError` (C-RT-31 §14.22). Re-entered on
    resume via the fence-keyed `EffectFenceResolution`, NOT a fresh dispatch. Additive,
    default-empty, dropped-from-hash-when-empty (same discipline as `synthesis_step_id`)."""

    pre_dispatch_gate_owning_branches: tuple[PreDispatchGateOwningBranchResumeState, ...] = ()
    """B-72 impl leg (CP spec v1.108 §1.1/§1.3a) — the PARALLELIZATION analogue of
    `FanOutResumeState.pre_dispatch_gate_owning_branches`: peer branches whose OWN
    `SUB_AGENT_BOUNDARY` HITL gate fired BEFORE any child run was dispatched (the
    runtime's `HITLPauseRequestedSignal`, raised ahead of
    `RuntimeSubAgentDispatcher.dispatch`). See that field's docstring for the full
    disposition-class + identity discipline (property 6, CP spec v1.108 §1). Additive,
    default-empty, dropped-from-hash-when-empty (same discipline as
    `effect_fence_paused_branches`)."""


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


class EffectFenceResumeState(BaseModel):
    """Effect-fence ambiguous-pause resume reconstruction state (the held claim key).

    B-EFFECT-FENCE-PAUSE-RESOLUTION (R-FS-1) — the linear/TOOL_STEP analogue of the
    four fan-out resume carriers, present ONLY when this snapshot captures a §14.22
    C-RT-31 effect-fence `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS` pause. Unlike
    the fan-out carriers (which recover completed-branch/step OUTPUTS), the effect
    fence's pause has NO recoverable output by definition (the ambiguity is precisely
    that no output was captured); the only state to carry is the per-(run, step, tool)
    `idempotency_key` of the held reserve, so the resumed dispatch can KEY-BIND the
    operator's resolution to the exact paused effect (apply it only when the recomputed
    dispatch key matches). NEVER co-set with `fan_out_resume` / `peer_fan_out_resume` /
    `handoff_resume` / `evaluator_optimizer_resume` (a fence pause is linear/TOOL_STEP)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    idempotency_key: str
    """The per-(run, step, tool) `idempotency_key` of the reserve the paused dispatch
    lost (the §14.22 fence claim key). Carried so `api.resume` key-binds the operator's
    `EffectFenceResolution` to THIS effect: the resumed dispatch applies the resolution
    ONLY when its recomputed key matches this value, then consumes it. COVERED by
    `_compute_snapshot_hash` (a resumed resolution trusts it → integrity-checked)."""


class OrchestratorEffectFencePausedResumeState(BaseModel):
    """A fan-out ORCHESTRATOR (`steps[0]`) whose OWN sequential dispatch raised the runtime
    effect fence's `EffectFenceAmbiguousUncommittedError` (C-RT-31 §14.22) — the fence lost a
    reserve to a prior uncommitted attempt of a non-idempotent effect AND found no captured
    output proving completion, so whether the orchestrator's effect fired is genuinely ambiguous.

    B-FANOUT-CRASH-RESUME-ORCHESTRATOR-MAYBE-RAN-EFFECT-BEARING (R-FS-1) — the ORCHESTRATOR
    analogue of the WORKER `EffectFencePausedBranchResumeState`. The orchestrator runs FIRST +
    sequentially, BEFORE any worker and BEFORE its own output capture, so when ITS dispatch
    fence-pauses there is no `FanOutResumeState` to carry (no branch ran, no orchestrator output
    exists — that absence IS the ambiguity); this is the FIRST-step analogue of the LINEAR-path
    `EffectFenceResumeState`, not a partial fan-out. Carried on `PauseSnapshot
    .orchestrator_effect_fence_resume` (a 6th top-level resume carrier, NEVER co-set with the
    five others), populated by ORCHESTRATOR_WORKERS / HIERARCHICAL_DELEGATION. On resume the
    orchestrator is RE-DISPATCHED with the operator's `EffectFenceResolution` key-bound to its
    reserve (NOT skipped like a recovered orchestrator, NOT fresh like a pre-arc run) and the
    workers then fan out fresh (none ran). The resolution palette is RE_FIRE / ABORT:
    SKIP_AS_FIRED is REJECTED at the resume site (an orchestrator's empty output would
    silently structure a degenerate fan-out aggregate — fail loud, never silently
    under-execute; the no-silent-failure discipline).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    idempotency_key: str
    """The held effect-fence reserve's `idempotency_key` (read by name off the runtime
    `EffectFenceAmbiguousUncommittedError`, since harness-cp cannot import harness-runtime), so
    `api.resume` key-binds the operator's `EffectFenceResolution` to THIS orchestrator's effect —
    the same keying discipline the LINEAR path's `EffectFenceResumeState` + the worker
    `EffectFencePausedBranchResumeState` use. On resume the orchestrator is re-dispatched with an
    `EffectFenceResolutionDirective(resolution=..., idempotency_key=...)` threaded on its
    `StepExecutionContext.effect_fence_resolution`; the runtime tool / managed-agents dispatcher
    consumes the matching directive (RE_FIRE → clear reserve + re-dispatch, ABORT → fail). Absent
    the key (defensive) → resume re-pauses (INERT, never an auto-re-fire)."""

    step_id: str
    """The orchestrator `WorkflowStep.step_id` AT CAPTURE TIME. Resume validates the re-supplied
    `steps[0].step_id` against this (positional-identity guard, fail-closed on a same-count
    rename/reorder — the same cheap guard `FanOutResumeState.orchestrator_step_id` /
    `EffectFencePausedBranchResumeState.step_id` apply)."""

    step_kind: str
    """The orchestrator `WorkflowStep.step_kind` value AT CAPTURE TIME (`tool-step` or
    `managed-agents` in production — the two fence-recoverable orchestrator kinds). Resume
    validates the re-supplied `steps[0].step_kind` against this (the changed-kind guard): if the
    operator kept the `step_id` but changed the kind away from the captured one, threading the
    `EffectFenceResolution` would reach NO fence (or a DIFFERENT sink) → the original ambiguous
    effect would be silently abandoned. Fail closed — the orchestrator analogue of the worker
    `EffectFencePausedBranchResumeState.step_kind` changed-kind guard (out-of-family Codex [P1])."""


class EffectFenceResolutionDirective(BaseModel):
    """The key-bound resolution the driver threads to the resumed dispatch.

    B-EFFECT-FENCE-PAUSE-RESOLUTION (R-FS-1) — pairs the operator's
    `EffectFenceResolution` (from `ResumeContext.effect_fence_resolution`) with the
    `idempotency_key` it is bound to (from `PauseSnapshot.effect_fence_resume`), so the
    resolution and its target travel together (illegal-state-unrepresentable: a
    resolution without its key cannot exist). Set by the CP driver on the resumed
    linear step's `StepExecutionContext.effect_fence_resolution` (hash-inert); read by
    the runtime tool dispatcher at the §14.22 fence gate, which applies it ONLY when the
    recomputed dispatch key equals `idempotency_key` (the key-bind), then it is naturally
    one-shot (set on the resumed step's context only)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    resolution: EffectFenceResolution
    """The operator's resume-side resolution (skip-as-fired / re-fire / abort)."""

    idempotency_key: str
    """The per-(run, step, tool) key this resolution is bound to. The dispatcher applies
    the resolution only when its recomputed key matches this (key-bind)."""


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

    hitl_gate_config_hash: str | None = None
    """B-79 impl leg slice 2 (CP spec v1.111 §1.2 property 7, §1.3a) — the
    sha256 hex digest (via `_hash_hitl_gate_config`, the SAME pure function
    slice 1 built for the fan-out closure) of the applicable HITL gate
    configuration of the step this pause will resume INTO, at capture time.
    Present ONLY for a `pause_reason=HITL_PENDING` capture at one of the three
    single-owner sequential sites (LINEAR `resume_at`, `EVALUATOR_OPTIMIZER`,
    `DECENTRALIZED_HANDOFF`) — the fan-out closure's own material-diff identity
    lives on `PreDispatchGateOwningBranchResumeState.hitl_gate_config_hash`
    (slice 1), not here. A single top-level field serves all three sequential
    sites (unlike the fan-out branches, a sequential resume has at most ONE
    currently-relevant step, so no per-branch carrier is needed) — the LINEAR
    site has no existing per-step resume-identity carrier of any kind to
    extend (§1.3a), so this is a net-new top-level field rather than a field
    added to `EvaluatorOptimizerResumeState`/`HandoffResumeState` (which would
    additionally require new None-strip machinery in `_compute_snapshot_hash`
    for byte-compat, mirroring `_strip_default_fanout_resume_fields` — a
    top-level field needs no such machinery since it is a bare scalar, not a
    nested carrier dump).

    default-`None` for byte-compat: a snapshot captured before this delta
    deserializes with this field absent → `None`. `_compute_snapshot_hash`
    (mirroring `effect_fence_resume`'s own pattern) adds this to the canonical
    dict ONLY when not `None`, so a pre-existing snapshot's recomputed
    `snapshot_hash` is byte-unchanged. Resume SKIPS the material-diff
    comparison when the CAPTURED (snapshot) value is `None` — mirrors
    `PreDispatchGateOwningBranchResumeState.hitl_gate_config_hash`'s own
    "validate ONLY when present" convention — rather than treating an
    unrecoverable legacy absence as a rejection."""

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

    effect_fence_resume: EffectFenceResumeState | None = None
    """B-EFFECT-FENCE-PAUSE-RESOLUTION (R-FS-1) — the §14.22 C-RT-31 effect-fence
    analogue of the four fan-out resume carriers, present ONLY when this snapshot
    captures a `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS` pause (`None` otherwise —
    additive, default-None, so every existing snapshot is byte-unchanged). NEVER co-set
    with the four fan-out carriers: a fence pause is linear/TOOL_STEP, the fan-out
    strategies populate exactly one of the others. Carries the held reserve's
    `idempotency_key` (no recoverable output — that absence IS the ambiguity); COVERED
    by `_compute_snapshot_hash` when present (same integrity contract). `api.resume`
    key-binds the operator's `ResumeContext.effect_fence_resolution` to it (skip-as-fired
    → empty-output proceed / re-fire → clear the claim + fresh dispatch / abort →
    FAILED)."""

    orchestrator_effect_fence_resume: OrchestratorEffectFencePausedResumeState | None = None
    """B-FANOUT-CRASH-RESUME-ORCHESTRATOR-MAYBE-RAN-EFFECT-BEARING (R-FS-1) — the 6th top-level
    resume carrier, present ONLY when an ORCHESTRATOR_WORKERS / HIERARCHICAL_DELEGATION fan-out's
    OWN orchestrator (`steps[0]`) of a fence-recoverable kind (TOOL_STEP / MANAGED_AGENTS)
    raised the §14.22 effect fence at its sequential dispatch — BEFORE any worker, BEFORE its
    output capture (`None` otherwise — additive, default-None, so every existing snapshot is
    byte-unchanged). NEVER co-set with the four fan-out carriers OR `effect_fence_resume`: the
    orchestrator fence pause is the FIRST-step analogue of the linear `effect_fence_resume`, but
    captured + resumed by the orchestrator-workers strategy (so it carries `step_id`/`step_kind`
    for the changed-orchestrator guard, which the key-only linear carrier does not). COVERED by
    `_compute_snapshot_hash` when present (same integrity contract); when nested inside a
    HIERARCHICAL `paused_child_branches[].child_snapshot` it is dropped-when-None by
    `_strip_default_fanout_resume_fields` (byte-compat with pre-arc nested snapshots). `api.resume`
    key-binds the operator's `ResumeContext.effect_fence_resolution` to it and re-dispatches the
    orchestrator (RE_FIRE → clear + fresh dispatch / ABORT → FAILED; SKIP_AS_FIRED rejected)."""


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

    child_workflow_id: str | None = None
    """B-31 — the target child workflow's identifier AT CAPTURE TIME, threaded from
    `SubAgentChildPausedError.child_workflow_id`. Resume validates it against the
    re-supplied branch's `step_payload["child_workflow_id"]` (read via `_opaque_field`,
    the SAME opaque-mapping key CP already reads elsewhere in `workflow_driver.py` for
    grandchild identity) ONLY when both sides are present — closes the previously
    documented gap where a same-`step_id`/same-`step_kind` edit that also swapped the
    payload's target child workflow passed the resume guard undetected. Default-None
    for byte-compat with snapshots captured before this field existed;
    `_strip_default_fanout_resume_fields` drops it when None so an old snapshot
    re-hashes byte-identically (the same discipline as `synthesis_step_id`)."""


class EffectFencePausedBranchResumeState(BaseModel):
    """A fan-out branch whose own dispatch raised the runtime effect fence's
    `EffectFenceAmbiguousUncommittedError` (C-RT-31 §14.22) — the fence lost a reserve to a
    prior uncommitted attempt of a non-idempotent effect AND found no captured output proving
    completion, so whether the branch's effect fired is genuinely ambiguous.

    B-FANOUT-EFFECT-FENCE-BRANCH-PAUSE (R-FS-1) — the fan-out analogue of the LINEAR-path
    B-EFFECT-FENCE-HITL-ROUTE / B-EFFECT-FENCE-PAUSE-RESOLUTION (`workflow_driver` §26.2 route).
    A branch raising it was previously caught by the generic branch `except Exception` →
    recorded `completed` (ran-and-errored) → cascade; this carrier COMPOSES that ambiguous-pause
    THROUGH the fan-out barrier instead, so the run PAUSES honestly and `api.resume` re-enters
    the branch with the operator's `EffectFenceResolution` (SKIP_AS_FIRED / RE_FIRE / ABORT).

    Carried by `FanOutResumeState.effect_fence_paused_branches` /
    `PeerFanOutResumeState.effect_fence_paused_branches` (NOT `branches`: a terminal branch MUST
    NOT be re-dispatched, but an effect-fence-paused branch MUST be re-entered — via the
    fence-keyed resolution, NOT a fresh dispatch — the illegal-states-unrepresentable split,
    mirroring `PausedChildBranchResumeState` for the child-pause disposition).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    branch_index: int
    """The fan-out branch/worker ordinal (0-based) whose dispatch raised the fence-ambiguous
    error. On resume this ordinal is re-dispatched THROUGH the fence-keyed resolution directive
    (NOT skipped like a terminal branch, NOT fresh like an absent one)."""

    step_id: str
    """The branch `WorkflowStep.step_id` AT CAPTURE TIME. Resume validates the re-supplied
    branch step's `step_id` against this (positional-identity guard, fail-closed on a same-count
    rename/reorder — the same cheap guard `FanOutBranchResumeState` / `PausedChildBranchResumeState`
    apply)."""

    step_kind: str
    """The branch `WorkflowStep.step_kind` value AT CAPTURE TIME (always `tool-step` in production —
    only a TOOL_STEP's dispatch reaches the runtime tool fence, the source of the ambiguous-pause).
    Resume validates the re-supplied branch's `step_kind` against this (the changed-kind guard): if
    the operator kept the `step_id` but changed the kind away from the captured one, threading the
    `EffectFenceResolution` would reach NO fence → the original ambiguous tool effect would be
    silently abandoned. Fail closed — the live-pause analogue of the §2 crash-resume changed-kind
    guard (out-of-family Codex [P1])."""

    idempotency_key: str
    """The held effect-fence reserve's `idempotency_key` (read by name off the runtime
    `EffectFenceAmbiguousUncommittedError`, since harness-cp cannot import harness-runtime), so
    `api.resume` key-binds the operator's `EffectFenceResolution` to THIS branch's effect — the
    same keying discipline the LINEAR path's `EffectFenceResumeState` uses. On resume the branch
    is re-dispatched with an `EffectFenceResolutionDirective(resolution=..., idempotency_key=...)`
    threaded on its `StepExecutionContext.effect_fence_resolution`; the runtime tool dispatcher
    consumes the matching directive (SKIP_AS_FIRED → empty output, RE_FIRE → clear reserve +
    re-dispatch, ABORT → fail). Absent the key (defensive) → resume re-pauses (INERT, never an
    auto-re-fire)."""


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

    effect_fence_resolution: EffectFenceResolution | None = None
    """Operator resolution of a §26.2 `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS`
    pause (B-EFFECT-FENCE-PAUSE-RESOLUTION). `None` when the pause was not an
    effect-fence pause (e.g. a HITL / EXPLICIT_OPERATOR pause — the `hitl_response`
    field carries those). When set on a resume of an effect-fence pause, the driver
    key-binds it (via `PauseSnapshot.effect_fence_resume.idempotency_key`) and threads
    it to the resumed linear step's dispatch: SKIP_AS_FIRED → proceed with empty output
    (never re-fire); RE_FIRE → clear the held claim + re-dispatch fresh; ABORT → FAILED.
    Mutually exclusive in practice with `hitl_response` (a pause has one reason).

    For a fan-out pause where MULTIPLE branches fence-paused at once (the
    PARALLELIZATION / ORCHESTRATOR_WORKERS / HIERARCHICAL_DELEGATION barrier can hold
    several `effect_fence_paused_branches`), this single field is the UNIFORM default:
    the driver applies it to EVERY fence-paused branch (key-bound per branch to that
    branch's reserve). To resolve two fence-paused branches DIFFERENTLY in one resume,
    supply `effect_fence_resolutions` (below); a per-key entry there OVERRIDES this
    default for its branch (B-FANOUT-EFFECT-FENCE-PER-BRANCH-RESOLUTION)."""

    effect_fence_resolutions: dict[str, EffectFenceResolution] | None = None
    """Per-branch-DISTINCT effect-fence resolutions, keyed by held-reserve
    `idempotency_key` (B-FANOUT-EFFECT-FENCE-PER-BRANCH-RESOLUTION, R-FS-1). `None`
    (the default) → every fence-paused branch resolves to the uniform
    `effect_fence_resolution` above (the v1.65 byte-identical behavior). When supplied,
    a fan-out branch whose held reserve `idempotency_key` (from
    `FanOutResumeState.effect_fence_paused_branches[*].idempotency_key`, surfaced in the
    pause `PauseSnapshot`) appears as a key here is resolved with THIS map's value;
    branches whose key is absent fall back to the uniform `effect_fence_resolution`
    (and re-pause INERT if that too is `None` — the decline-mirror, never an
    auto-re-fire). This is a `default + per-key override` composition (NOT a replacement
    of the single field): the single field is the uniform answer, the map overrides
    specific branches. Read via `effect_fence_resolution_for(key)`.

    Consumed ONLY at the two fan-out consume sites (`_execute_parallelization` /
    `_execute_orchestrator_workers`). The LINEAR effect-fence pause has exactly one held
    reserve key, so per-branch-DISTINCT resolution is structurally inapplicable there —
    the linear resume consumes the single `effect_fence_resolution` field verbatim (a
    map supplied for a linear pause is inert). Map entries whose key matches no
    fence-paused branch this round are harmlessly ignored. Keyed by `idempotency_key`
    (not `branch_index`) so the map is uniform with the dispatcher's per-`(run, step,
    tool)` key-bind. ABORT in a map entry retains its shipped RUN-level-terminal
    semantic (v1.65 §1(b), preserved byte-for-byte) — the whole run FAILS and all
    continue-resolutions are suppressed. ABORT_BRANCH in a map entry is per-branch-SCOPED
    (B-FANOUT-EFFECT-FENCE-PER-BRANCH-SCOPED-ABORT, CP spec v1.73 §1): fail JUST that
    branch (record it terminal, never re-dispatched) while the SIBLINGS the operator
    vouched for (SKIP_AS_FIRED / RE_FIRE) fire and the run folds survivors per
    `cascade_policy`. So all four resolutions compose freely across branches in one map."""

    hitl_responses: dict[str, HITLResult] | None = None
    """Per-branch-DISTINCT HITL responses, keyed by the paused CHILD's own
    `PausedChildBranchResumeState.child_snapshot.run_id` — **NOT** `branch_path`
    (corrected at this pass; see the keying-defect note below). `None` (the
    default) → every GATE-OWNING branch resolves to the uniform `hitl_response`
    above (byte-identical to pre-B-39 single-branch behavior in the single-
    gate-owning-branch case). When supplied, a gate-owning child whose OWN
    `run_id` appears as a key here is resolved with THIS map's value. This
    field's CARRIER shape alone does not by itself guarantee an unaddressed
    gate-owning sibling is never misresolved by the uniform default when 2+
    gate-owning branches are concurrently paused — that safety guarantee is a
    RESOLVER-level invariant (§1.2 property 4, round-4-revised from a
    mechanism to a black-box invariant: safety — no gate-owning branch
    receives a response addressed to a different one; liveness — resume
    still reaches every addressed gate-owning branch, traversing any
    transitively-paused container/ancestor branch en route, property 5),
    deliberately NOT prescribed here as a specific counting/INERT mechanism
    (a round-3 draft of this docstring did prescribe one; out-of-family
    review found it would strand transitively-paused container branches —
    see §1.2 property 4's own round-4 correction note for the full account).
    A pure per-key lookup (`hitl_response_for`, below) has no visibility into
    how many gate-owning siblings are paused this cycle or which branches are
    merely transitive containers — enforcing the invariant is the deferred
    resolver's job (CP plan v2.42 §5), not this field's or that method's.
    This is a `default + per-key override` composition (NOT a replacement of
    the single field) — the SAME CARRIER shape `effect_fence_resolutions`
    ships (the effect-fence sibling's identical uniform-fallback safety gap
    is registered, not fixed, as a pre-existing shipped-and-cleared issue,
    `B-70`). Read via `hitl_response_for(child_run_id)`.

    **Scope limit (round-3 correction): `pause_snapshot`-return resume path
    only.** This addressing scheme requires the caller to already possess a
    `PausedChildBranchResumeState.child_snapshot.run_id` — obtainable only
    from a `RunResult.pause_snapshot` object the caller directly holds (the
    resume path where `api.resume(pause_snapshot=...)` is supplied). The
    OTHER resume mode `api.resume()` supports, `resume_handle` (crash-
    recovery: the caller supplies only a `workflow_id`; the runtime reads the
    latest durably-journaled snapshot itself, per §14.14.8), gives the caller
    NO prior snapshot to read a paused child's `run_id` from BEFORE
    `resume_context` must be constructed — so multi-child concurrent HITL
    addressing via `hitl_responses` is NOT YET SUPPORTED on the
    `resume_handle` path; such a caller is limited to the single-paused-child
    case (uniform `hitl_response` only) until a follow-on accessor exposing
    the durably-journaled pause state to `resume_handle` callers before
    `resume_context` construction is designed. This is a registered scope
    limitation, not a silently-dropped case — see §3's cross-axis
    dispositions.

    **Scope limit (round-6 correction, out-of-family review): operator-
    facing escalation requests do not yet expose the `run_id` a response
    must be keyed by.** This field lets a CALLER who already knows a paused
    child's `run_id` construct a correctly-keyed response. It does NOT by
    itself solve how that caller LEARNS which `run_id` a given HITL
    escalation request corresponds to. The existing operator-facing request
    types this arc does NOT touch — `HITLEscalationBrief` (C-CP-28 §25.2,
    `harness_cp/validator_framework_types.py`) and the webhook delivery
    payload the HITL gate composer sends — carry `parent_action_id` and the
    `hitl:`-prefixed `compose_hitl_action_id(parent_action_id,
    placement_position)` (`harness-runtime/lifecycle/hitl_gate_composer.py`),
    BOTH of which derive from the SAME workflow_id-scoped, non-run-instance
    identifier this arc's own keying-defect note (above) already found
    collides across repeated same-`child_workflow_id` dispatch — NEITHER
    carries a `run_id`. Concretely: when two peer branches dispatch the
    SAME `child_workflow_id` and BOTH hit the identical internal HITL gate,
    their two escalation requests/webhook payloads are byte-identical on
    every field an operator or webhook consumer can see — there is
    structurally no way to tell them apart, so a human (or automated
    consumer) cannot know which `child_run_id` to key a `hitl_responses`
    entry under for either one. Fixing this requires amending
    `HITLEscalationBrief`/the webhook payload shape (an EXISTING C-CP-28
    contract this delta does not touch) to carry a run-instance-distinct
    correlation identifier — a genuinely separate design surface from this
    delta's `ResumeContext` carrier fix, NOT solved here. Registered as
    `B-71` (`.harness/forward-register.yaml`); not this arc's scope.

    **Keying-defect note (why `run_id`, not `branch_path`; recorded so the
    `branch_path` reading is not reinvented).** A first draft of this field
    keyed by C-CP-25 §25.16 `branch_path` (`compose_branch_path`), reasoning
    that it is "globally unique at arbitrary recursion depth." Out-of-family
    review (`just codex-review-uncommitted`) found this FALSE: `branch_path`
    derives from `parent_action_id`, which derives from `action_id =
    f"workflow:{workflow_id}:step:{step_index}"` (`workflow_driver.py`) —
    scoped by the STATIC workflow/manifest identifier, with NO `run_id`
    component. When two PEER branches dispatch the SAME `child_workflow_id`
    (an explicitly supported scenario — see this arc's own register history),
    their respective children's INTERNAL `action_id`/`branch_path` values are
    byte-IDENTICAL (same `workflow_id`, same internal `step_index`), so a
    grandchild paused under child-instance-A and the equivalent grandchild
    paused under child-instance-B would COLLIDE on the same `branch_path` key
    — the map could not carry two distinct responses. `run_id`, by contrast,
    genuinely IS distinct per recursive dispatch instance: `child_run_id` is
    derived via `compose_child_run_id_seed` (`harness-runtime/lifecycle/
    sub_agent_dispatch.py`) as `sha256("child-run:" + parent_idempotency_key +
    ":" + branch_path + ":" + child_workflow_id)`, and `parent_idempotency_key
    = _compute_step_idempotency_key(run_idempotency_key, step_index, ...)`
    where `run_idempotency_key = sha256(run_id, workflow_id, ...)` — the
    SPAWNING invocation's OWN `run_id` is folded in at every level, so two
    peer branches spawning the same `child_workflow_id` (distinct `run_id`s at
    the spawning level, since `run_id` is unique per `execute_workflow`
    invocation) necessarily derive DISTINCT child `run_id`s, and this
    distinctness propagates to every further-nested grandchild by the same
    recursive argument. `run_id` is therefore genuinely unique across
    arbitrary recursion depth AND repeated same-`child_workflow_id` dispatch
    — the property `branch_path` was wrongly assumed to have. No new carrier
    field is needed to expose it: `PausedChildBranchResumeState.child_snapshot.
    run_id` (`PauseSnapshot.run_id: str`, already a REQUIRED existing field)
    already carries it — an operator reads `paused_child.child_snapshot.
    run_id` off a prior `RunResult.pause_snapshot` to build a `hitl_responses`
    key, with NO new public field addition (a prior draft of this spec leg
    added `PausedChildBranchResumeState.branch_path` for this purpose; REMOVED
    at this pass — `child_snapshot.run_id` already solves the identical
    addressability need, more robustly, with a smaller diff).

    HOW the resolved per-branch answer physically reaches the resumed step's
    gate composer (which parameter, which call site, at which recursion
    level) is deliberately UNSPECIFIED here — see §1's contract-level
    statement below; this field only fixes the CARRIER SHAPE an operator
    constructs, not the delivery mechanism.

    A pause that is NOT branch-scoped (the depth-0 root's own linear/fan-out-
    barrier gate) has no child `run_id` to key by (it IS the run); its gate
    always consumes the uniform `hitl_response` field directly, exactly
    mirroring how a LINEAR effect-fence pause consumes `effect_fence_resolution`
    directly (§26.8.1 sibling-field precedent, unamended by this delta)."""

    def hitl_response_for(self, child_run_id: str) -> HITLResult | None:
        """The operator's HITL response for one paused GATE-OWNING child's own `run_id`.

        A PURE per-key lookup-with-fallback: the `hitl_responses` map entry
        for `child_run_id` if present, else the uniform `hitl_response`
        default. `None` when neither is supplied → the branch re-pauses
        INERT (never an auto-re-fire). A `None` map and a map-without-this-
        key both fall through to the single default, so single-gate-owning-
        branch callers (the only shape that existed pre-B-39) are byte-
        unchanged. Keyed by `child_run_id` (`PausedChildBranchResumeState.
        child_snapshot.run_id`), NOT `branch_path` — see the keying-defect
        note above; the composition CARRIER shape (default + per-key
        override) mirrors `effect_fence_resolution_for` (§26.8.1), only the
        key differs. This method is called ONLY for a branch that is itself
        gate-owning (property 5) — a transitively-paused container/ancestor
        branch is never resolved through this method at all; it is simply
        re-entered/recursed into, unconditionally, by whatever mechanism the
        impl leg lands (deferred, §1.3).

        **This method alone does NOT enforce the multi-child fallback-safety
        invariant (§1.2 property 4 — round-4-revised to a black-box
        invariant; NOT a mechanism this method itself implements).** It has
        no visibility into how many gate-owning siblings are paused this
        resume cycle or which OTHER branches in the tree are merely
        transitive containers, so it cannot by itself refuse an unsafe
        uniform-fallback call. The RESOLVER invoking this method (impl
        discretion, §1.3, deferred alongside properties 1-3) MUST itself
        satisfy property 4's safety + liveness invariants — HOW it does so
        (counting, addressed-set tracking, some other technique) is
        deliberately unspecified here; a round-3 draft of this docstring
        prescribed a specific counting/INERT mechanism, which out-of-family
        review found would strand a transitively-paused container branch
        (property 5) — this pure method cannot discharge property 4's
        invariant on its own, and no longer attempts to describe how the
        resolver should."""
        if self.hitl_responses is not None:
            mapped = self.hitl_responses.get(child_run_id)
            if mapped is not None:
                return mapped
        return self.hitl_response

    def effect_fence_resolution_for(self, idempotency_key: str) -> EffectFenceResolution | None:
        """The operator's effect-fence resolution for one held-reserve `idempotency_key`.

        B-FANOUT-EFFECT-FENCE-PER-BRANCH-RESOLUTION (R-FS-1) — the single source of
        truth for "what did the operator answer for THIS branch's fence?": the
        `effect_fence_resolutions` map entry for `idempotency_key` if present, else the
        uniform `effect_fence_resolution` default. `None` when neither is supplied → the
        branch re-pauses INERT (the #701 decline-mirror; never an auto-re-fire). Pure
        lookup-with-fallback (no control-flow branch on "which mode"): a `None` map and a
        map-without-this-key both fall through to the single default, so the v1.65
        single-field behavior is preserved byte-for-byte when no map is supplied."""
        if self.effect_fence_resolutions is not None:
            mapped = self.effect_fence_resolutions.get(idempotency_key)
            if mapped is not None:
                return mapped
        return self.effect_fence_resolution


class HITLDeliveryCell(BaseModel):
    """Per-branch one-shot mutable cell for resolved HITL-response delivery.

    B-39 impl leg Slice B (CP spec v1.106 §1 / Runtime spec §14.8.8.10) — the
    replacement for the retired ctx-level, run-tree-wide-shared
    `ResumeContextHolder` singleton. Reuses the SAME frozen-outer /
    mutable-internal-`PrivateAttr` shape (Runtime's `ResumeContextHolder`)
    rather than inventing a new one-shot pattern — the discriminator that
    separates this from a re-scoped ctx-level holder is REACHABILITY, not
    intent: exactly one `StepExecutionContext` instance holds a reference to
    ANY given cell, created fresh at the single point `resume_context.
    hitl_response_for(run_id)` is resolved (the linear resume_at
    reconstruction site — the same site that already stamps
    `effect_fence_resolution`), never at a ctx/dispatcher/composer-instance
    scope. `harness-cp` cannot import Runtime's `ResumeContextHolder`
    (`harness-runtime` depends on `harness-cp`, so the reverse import would
    cycle — the `[[od-cp-canonical-direction-axis-isolation-fix]]` inverse
    case), so this is a CP-owned sibling type carrying only the narrower
    `HITLResult` payload the composer's Step-0 read actually consumes (the
    retired holder's `consume_and_clear()` returned a full `ResumeContext`
    only to be immediately unwrapped to `.hitl_response` at the one call
    site that read it).
    """

    model_config = ConfigDict(frozen=True)

    _value: HITLResult | None = PrivateAttr(default=None)

    def __init__(self, resolved: HITLResult | None, **data: Any) -> None:
        super().__init__(**data)
        self._value = resolved

    def consume_and_clear(self) -> HITLResult | None:
        """Atomically return the cell's value AND clear it to `None`.

        Enforces the same one-shot semantic the retired ctx-level holder
        enforced (CP spec v1.106 §1 CONTRACT property: "one-shot preserved
        under `RetryBreakerFallbackDispatcher` retry within one resume
        cycle") — `StepExecutionContext` is frozen and constructed once per
        step-dispatch attempt, reused unchanged across retries, so the first
        `dispatch()` call drains this cell and every retry attempt within
        the same resume cycle sees `None`.
        """
        current = self._value
        self._value = None
        return current


# B-HIERARCHICAL-PAUSE (R-FS-1) — `FanOutResumeState.paused_child_branches` forward-refs
# `PausedChildBranchResumeState` (defined after `PauseSnapshot`, which it nests), so the
# annotation cannot resolve at `FanOutResumeState` class-build time (it is the FIRST
# forward reference in this module — `PauseSnapshot.fan_out_resume` resolves backward).
# Rebuild once now that every referenced model exists. `PausedChildBranchResumeState`
# itself needs no rebuild (its `PauseSnapshot` ref is backward).
FanOutResumeState.model_rebuild()
