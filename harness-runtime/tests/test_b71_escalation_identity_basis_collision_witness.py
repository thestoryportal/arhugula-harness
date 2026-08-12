"""B-71 precondition-1 collision witness — the EXTERNAL escalation identity basis.

`.harness/council-b71-hitl-external-correlation-2026-08-12/DELIVERABLE.md` §4 leaves
the identity basis an **OPEN FORK** and §5 precondition 1 requires the nested-fan-out
collision witness to be *executed* against the candidates before any spec text is
drafted — the row has failed three times on exactly this class of unrun premise.

This module is that witness. Every basis under test is read off a
``StepExecutionContext`` that the **real production composer**
(``compose_branch_child_context``) produced, from a fan-out parent composed with the
real ``_compute_run_idempotency_key`` / ``_compute_step_idempotency_key`` /
``_parallelization_fanout_action_id``, threaded through the real
``compose_branch_path`` and ``compose_child_run_id_seed``. Nothing in the identity
chain is re-implemented here.

**The tree.** A root PARALLELIZATION run of workflow ``wf-root`` fans out two peer
branches; **both** branches are ``SUB_AGENT_DISPATCH`` steps pointing at the **same**
``child_workflow_id`` — the shape ``compose_child_run_id_seed``'s own docstring
(`sub_agent_dispatch.py:371-380`) names as live ("two sibling SUB_AGENT_DISPATCH
workers that dispatch the SAME `child_workflow_id`"), and the reason ``branch_path``
was folded into the child-run seed at U-CP-83. Each child run is itself a
PARALLELIZATION run whose own branch 0 fires a **pre-dispatch** HITL escalation. The
two escalations are genuinely distinct (distinct child runs, pinned first below), so
any sound EXTERNAL correlation identity must separate them.

**Why this shape rather than in-run nesting.** A fan-out branch child never re-enters
the fan-out composer inside the *same* run — every ``compose_branch_child_context``
call site descends from a single per-run fan-out point (`workflow_driver.py:8351`,
`:8591`, `:8649`, `:9068`, `:12675`, `:12844`, `:12903`, `:13119`, `:15423`), and
nesting is reached by dispatching a **child run** through
``child_workflow_runner``. So "nested fan-out" is cross-run, and a basis is
tree-wide-unique exactly when it is run-distinguishing.

**What this module does NOT witness** (stated so no claim outruns its evidence):

- It composes the fan-out parent ``StepExecutionContext`` as a struct literal
  mirroring `workflow_driver.py:8185-8200` rather than reaching it through
  ``execute_workflow``; a full two-level PARALLELIZATION run with live HITL webhook
  delivery is a much larger fixture than the identity claim needs. Every *derived*
  field is production-composed, so a change to any composer is caught here; a change
  to how the driver *populates* the fan-out parent is not.
- It does not exercise a live resume. The fact that a resume reuses the paused
  child's original ``run_id`` rather than re-deriving it is **cited**
  (`child_workflow_runner.py:230-234`), not witnessed, and the DELIVERABLE records it
  as cited. What is witnessed here is the half that is this module's to prove: that
  basis (B) has no ``entry_version`` input, so a stable ``run_id`` cannot rotate it.
- It covers the PARALLELIZATION fan-out shape only. HIERARCHICAL_DELEGATION recursion
  and the DECENTRALIZED_HANDOFF stage chain (`workflow_driver.py:15375-15441`) are
  unexamined.
"""

from __future__ import annotations

from harness_as.sandbox_tier import SandboxTier
from harness_cp.cp_shared_types import AgentRole
from harness_cp.gate_level_rule import GateLevel
from harness_cp.hitl_placement import HITLPlacementKind
from harness_cp.pause_state_projection import pre_dispatch_gate_owning_branch_identity
from harness_cp.workflow_driver import (
    _compute_run_idempotency_key,
    _compute_step_idempotency_key,
    _parallelization_fanout_action_id,
)
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    compose_branch_child_context,
    compose_branch_path,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.lifecycle.hitl_gate_composer import compose_hitl_action_id
from harness_runtime.lifecycle.sub_agent_dispatch import compose_child_run_id_seed

_W_ROOT = "wf-root"
_W_CHILD = "wf-child"
_ROOT_RUN_ID = "run-root-0001"
_ENTRY_VERSION = 1
_PLACEMENT = HITLPlacementKind.SUB_AGENT_BOUNDARY
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="b71-basis-collision-witness")
_ROLE = AgentRole("w")


def _fanout_parent_context(
    *, workflow_id: str, run_id: str, entry_version: int
) -> StepExecutionContext:
    """The one fan-out parent context of a PARALLELIZATION run.

    Mirrors `workflow_driver.py:8185-8200`. The two identity-bearing fields —
    ``parent_action_id`` and ``parent_idempotency_key`` — are composed by the real
    production helpers, so this literal fixes only the non-identity scaffolding.
    """
    run_key = _compute_run_idempotency_key(run_id, workflow_id, extras=(str(entry_version),))
    return StepExecutionContext(
        workflow_id=workflow_id,
        parent_action_id=_parallelization_fanout_action_id(workflow_id),
        parent_gate_level=GateLevel.ASK,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=_ACTOR,
        parent_entry_hash="",
        parent_idempotency_key=_compute_step_idempotency_key(run_key, 0),
        tenant_id=None,
        step_index=0,
    )


def _branch(parent: StepExecutionContext, branch_index: int) -> StepExecutionContext:
    """A fan-out branch child, composed by the REAL production composer."""
    return compose_branch_child_context(parent, branch_index=branch_index, agent_role=_ROLE)


def _child_run_ids(entry_version: int = _ENTRY_VERSION) -> tuple[str, str]:
    """The two sibling child runs, derived the way production derives them.

    ``compose_branch_child_context`` → ``compose_branch_path`` →
    ``compose_child_run_id_seed``, all real. Both peers dispatch the SAME
    ``child_workflow_id``; only ``branch_path`` separates their child runs
    (C-CP-25 §25.16 / U-CP-83).
    """
    root = _fanout_parent_context(
        workflow_id=_W_ROOT, run_id=_ROOT_RUN_ID, entry_version=entry_version
    )
    seeds = []
    for branch_index in (0, 1):
        branch = _branch(root, branch_index)
        seeds.append(
            compose_child_run_id_seed(
                branch.parent_idempotency_key, _W_CHILD, compose_branch_path(branch)
            )
        )
    return seeds[0], seeds[1]


def _escalating_branch(
    child_run_id: str, branch_index: int = 0, entry_version: int = _ENTRY_VERSION
) -> StepExecutionContext:
    """The child run's OWN branch that fires the pre-dispatch escalation.

    The child run is itself a PARALLELIZATION run over ``_W_CHILD``; this is its
    fan-out parent descended one level, again through the real composer.
    """
    return _branch(
        _fanout_parent_context(
            workflow_id=_W_CHILD, run_id=child_run_id, entry_version=entry_version
        ),
        branch_index,
    )


# --- the three candidate bases, each READ OFF the production-composed context -------


def _basis_a(branch: StepExecutionContext) -> str:
    """Candidate (A) — ``(parent_action_id, branch_index, placement)``.

    DELIVERABLE §4 candidate (A), the codebase's own branch-causality convention.
    ``branch.parent_action_id`` is whatever ``compose_branch_child_context`` actually
    put there; this helper asserts nothing about it, it just reads it.
    """
    return f"{branch.parent_action_id}|{branch.branch_index}|{_PLACEMENT.value}"


def _basis_c(branch: StepExecutionContext) -> str:
    """The council's original pick — ``(parent_idempotency_key, branch_index, placement)``.

    DELIVERABLE §4 records the council selecting this triple and the orchestrator then
    WITHDRAWING its [HIGH] tree-wide-uniqueness rating.
    """
    return f"{branch.parent_idempotency_key}|{branch.branch_index}|{_PLACEMENT.value}"


def _basis_b(child_run_id: str, branch: StepExecutionContext) -> str:
    """Candidate (B) — the tree-wide internal identity, with ``placement`` added.

    ``pre_dispatch_gate_owning_branch_identity`` (`pause_state_projection.py:500`) is
    the identity the driver ALREADY composes for this exact branch population at
    `workflow_driver.py:8346` and `:12670`; ``placement`` closes one of the two
    objections that defeated (B) at the council cross-read.
    """
    identity = pre_dispatch_gate_owning_branch_identity(child_run_id, branch.branch_index or 0)
    return f"{identity}|{_PLACEMENT.value}"


# --- the witness -------------------------------------------------------------------


def test_the_two_sibling_child_runs_are_genuinely_distinct() -> None:
    """Grounds the witness: the tree really does hold TWO escalations, not one.

    Without this the collision assertions below would be vacuous — two identical
    identities for what is actually one branch is not a defect.
    """
    left, right = _child_run_ids()
    assert left != right, (
        "the witness tree is degenerate — both peers derived the same child run_id, "
        "so there is only one escalation and nothing to distinguish"
    )


def test_the_two_escalating_branches_are_distinct_contexts() -> None:
    """...and the two branches that escalate are genuinely different objects.

    Pins that the collision found below is a collapse of the *identity basis*, not an
    artifact of handing the same context to both sides.
    """
    left, right = _child_run_ids()
    assert _escalating_branch(left) != _escalating_branch(right)


def test_basis_a_parent_action_id_collides_across_sibling_child_runs() -> None:
    """**Candidate (A) is FALSIFIED.**

    A PARALLELIZATION branch's ``parent_action_id`` comes from
    ``_parallelization_fanout_action_id(workflow_id)`` (`workflow_driver.py:8187` →
    `:7168-7177`), which takes ``workflow_id`` and **nothing else** — no run identity
    at all. Two distinct sibling child runs of the same ``child_workflow_id``
    therefore compose the same triple, recreating B-71's own defect inside the fix.
    """
    left, right = _child_run_ids()
    left_branch, right_branch = _escalating_branch(left), _escalating_branch(right)
    assert _basis_a(left_branch) == _basis_a(right_branch), (
        "candidate (A) unexpectedly separated the two branches — re-derive the fork, "
        "the evidence the DELIVERABLE §4-bis resolution rests on has changed"
    )
    # And the collision reaches the operator-facing delivery key through the REAL
    # composer (`hitl_gate_composer.py:428-440`, used at `:1302` as the webhook
    # Idempotency-Key + the CP audit action_id + the F2 ledger key), not merely the
    # abstract basis tuple.
    assert compose_hitl_action_id(
        left_branch.parent_action_id, _PLACEMENT
    ) == compose_hitl_action_id(right_branch.parent_action_id, _PLACEMENT)


def test_basis_c_parent_idempotency_key_survives_the_collision_witness() -> None:
    """The council's original triple is **not** falsified by the collision shape.

    ``parent_idempotency_key`` descends from
    ``_compute_run_idempotency_key(run_id, workflow_id, entry_version)``
    (`workflow_driver.py:646-665`), so it is run-distinguishing. The orchestrator's
    withdrawal argument — verbatim inheritance of ``parent_idempotency_key`` through
    ``compose_branch_child_context`` — is correct *within* a run but does not reach
    across runs, and cross-run is where nesting actually lives.
    """
    left, right = _child_run_ids()
    assert _basis_c(_escalating_branch(left)) != _basis_c(_escalating_branch(right))


def test_basis_b_run_scoped_identity_survives_the_collision_witness() -> None:
    """**Candidate (B) survives.** Distinct child runs ⇒ distinct identities."""
    left, right = _child_run_ids()
    assert _basis_b(left, _escalating_branch(left)) != _basis_b(right, _escalating_branch(right))


def test_verbatim_inheritance_is_within_run_and_does_not_itself_collide() -> None:
    """Pins the v1 withdrawal argument's actual reach, through the real composer.

    ``compose_branch_child_context`` really does inherit ``parent_idempotency_key``
    and ``step_index`` verbatim (`workflow_driver_types.py:632-645`) — asserted here
    against production output, not assumed. But within one run the two peers still
    differ on ``branch_index``, so verbatim inheritance alone produces no collision;
    that is why the v1 escalation does not land on (C).
    """
    root = _fanout_parent_context(
        workflow_id=_W_ROOT, run_id=_ROOT_RUN_ID, entry_version=_ENTRY_VERSION
    )
    peer_0, peer_1 = _branch(root, 0), _branch(root, 1)
    assert peer_0.parent_idempotency_key == root.parent_idempotency_key
    assert peer_1.parent_idempotency_key == root.parent_idempotency_key
    assert peer_0.step_index == peer_1.step_index == root.step_index
    assert _basis_c(peer_0) != _basis_c(peer_1)


def test_the_bare_ordinal_carrier_collapses_what_the_run_component_separates() -> None:
    """The local ordinal is NOT doing the work — the run component is.

    Re-pins DELIVERABLE §4's three-way-convergent finding: "the reverse-thread carrier
    must be keyed by a tree-wide identity — not bare ``branch_index``".
    """
    left, right = _child_run_ids()
    left_branch, right_branch = _escalating_branch(left), _escalating_branch(right)
    assert left_branch.branch_index == right_branch.branch_index  # identical ordinal
    assert _basis_b(left, left_branch) != _basis_b(right, right_branch)
    assert _basis_c(left_branch) != _basis_c(right_branch)


def test_entry_version_bump_rotates_basis_c_for_a_fixed_run() -> None:
    """**Candidate (C) is falsified on DELIVERABLE §5 precondition 4.**

    ``entry_version`` is folded into ``run_idempotency_key``
    (`workflow_driver.py:3312-3316`), so for one and the same child run a bump
    recomputes a different (C) token. Combined with the cited fact that the ordinary
    resume path reuses the paused child's ``run_id`` verbatim
    (`child_workflow_runner.py:230-234`), that means (C) rotates on *every* resumed
    escalation after a bump — not merely inside the narrow mint→persist crash window
    precondition 4 scopes.
    """
    left, _ = _child_run_ids()
    assert _basis_c(_escalating_branch(left, entry_version=1)) != _basis_c(
        _escalating_branch(left, entry_version=2)
    )


def test_entry_version_bump_leaves_basis_b_untouched_for_a_fixed_run() -> None:
    """**Candidate (B) has no ``entry_version`` input, so a stable run cannot rotate it.**

    The contrast with the test above is the content: both call sites compose branch
    contexts that genuinely differ (their ``parent_idempotency_key`` differs, asserted
    here), yet (B) is identical across them because its inputs are ``run_id`` and
    ``branch_index`` alone. Given the cited resume behaviour
    (`child_workflow_runner.py:230-234`, reuse of ``snapshot.run_id``), (B)'s token
    survives an ``entry_version`` bump on the ordinary resume path.
    """
    left, _ = _child_run_ids()
    at_v1 = _escalating_branch(left, entry_version=1)
    at_v2 = _escalating_branch(left, entry_version=2)
    assert at_v1.parent_idempotency_key != at_v2.parent_idempotency_key, (
        "the two contexts are supposed to differ — otherwise the (B)-stability "
        "assertion below is trivially true and witnesses nothing"
    )
    assert _basis_b(left, at_v1) == _basis_b(left, at_v2)


def test_crash_before_persist_is_the_only_window_that_rotates_basis_b() -> None:
    """Bounds (B)'s residual.

    With no snapshot to recover, the child ``run_id`` is re-derived from the parent's
    ``entry_version``-bearing key, so the token does rotate — the mint→persist window,
    and only that window.
    """
    left_v1, _ = _child_run_ids(entry_version=1)
    left_v2, _ = _child_run_ids(entry_version=2)
    assert left_v1 != left_v2
    assert _basis_b(left_v1, _escalating_branch(left_v1, entry_version=1)) != _basis_b(
        left_v2, _escalating_branch(left_v2, entry_version=2)
    )
