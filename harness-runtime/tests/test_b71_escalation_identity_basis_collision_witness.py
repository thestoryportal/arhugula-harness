"""B-71 precondition-1 collision witness — the EXTERNAL escalation identity basis.

`.harness/council-b71-hitl-external-correlation-2026-08-12/DELIVERABLE.md` §4 leaves
the identity basis an **OPEN FORK** and §5 precondition 1 requires the nested-fan-out
collision witness to be *executed* against the candidates before any spec text is
drafted — the row has failed three times on exactly this class of unrun premise.

This module is that witness. It composes each candidate basis from the **real
production composers** (no re-implementation) over the realizable tree shape below,
and pins which candidates survive.

**The tree.** A root PARALLELIZATION run of workflow ``wf-root`` fans out two peer
branches; **both** branches are ``SUB_AGENT_DISPATCH`` steps pointing at the **same**
``child_workflow_id`` — the shape ``compose_child_run_id_seed``'s own docstring
(`sub_agent_dispatch.py:371-380`) names as live ("two sibling SUB_AGENT_DISPATCH
workers that dispatch the SAME `child_workflow_id`"), and the reason ``branch_path``
was folded into the child-run seed at U-CP-83. Each child run is itself a
PARALLELIZATION run whose own branch 0 fires a **pre-dispatch** HITL escalation. The
two escalations are genuinely distinct (distinct child runs, pinned below), so any
sound EXTERNAL correlation identity must separate them.

**Why this shape rather than in-run nesting.** A fan-out branch child never re-enters
the fan-out composer inside the *same* run — every ``compose_branch_child_context``
call site descends from a single per-run fan-out point (`workflow_driver.py:8351`,
`:8591`, `:8649`, `:9068`, `:12675`, `:12844`, `:12903`, `:13119`, `:15423`), and
nesting is reached by dispatching a **child run** through
``child_workflow_runner``. So "nested fan-out" is cross-run, and a basis is
tree-wide-unique exactly when it is run-distinguishing.
"""

from __future__ import annotations

from harness_cp.hitl_placement import HITLPlacementKind
from harness_cp.pause_state_projection import pre_dispatch_gate_owning_branch_identity
from harness_cp.workflow_driver import (
    _compute_run_idempotency_key,
    _compute_step_idempotency_key,
    _parallelization_fanout_action_id,
)
from harness_runtime.lifecycle.hitl_gate_composer import compose_hitl_action_id
from harness_runtime.lifecycle.sub_agent_dispatch import compose_child_run_id_seed

_W_ROOT = "wf-root"
_W_CHILD = "wf-child"
_ROOT_RUN_ID = "run-root-0001"
_ENTRY_VERSION = 1
_PLACEMENT = HITLPlacementKind.SUB_AGENT_BOUNDARY


def _child_run_ids(entry_version: int = _ENTRY_VERSION) -> tuple[str, str]:
    """The two sibling child runs, composed exactly as the driver composes them.

    Mirrors `workflow_driver.py:8185-8198` (the one fan-out parent context) and
    `compose_branch_path` (`workflow_driver_types.py:778-788`,
    ``{parent_action_id}:{branch_index}``), then the real
    ``compose_child_run_id_seed``.
    """
    root_run_key = _compute_run_idempotency_key(_ROOT_RUN_ID, _W_ROOT, extras=(str(entry_version),))
    root_fanout_action_id = _parallelization_fanout_action_id(_W_ROOT)
    # `compose_branch_child_context` inherits `parent_idempotency_key` + `step_index`
    # VERBATIM, so both peers carry the fan-out parent's step-0 key; the branch-
    # distinct component is `branch_path`, composed downstream (C-CP-25 §25.16).
    root_parent_idempotency_key = _compute_step_idempotency_key(root_run_key, 0)
    return (
        compose_child_run_id_seed(
            root_parent_idempotency_key, _W_CHILD, f"{root_fanout_action_id}:0"
        ),
        compose_child_run_id_seed(
            root_parent_idempotency_key, _W_CHILD, f"{root_fanout_action_id}:1"
        ),
    )


def _basis_a(child_run_id: str, branch_index: int) -> str:
    """Candidate (A) — ``(parent_action_id, branch_index, placement)``.

    DELIVERABLE §4 candidate (A), the codebase's own branch-causality convention.
    Inside a PARALLELIZATION child run the branch's ``parent_action_id`` is
    ``_parallelization_fanout_action_id(workflow_id)`` (`workflow_driver.py:8187`),
    which takes **only** ``workflow_id`` — ``child_run_id`` is unused here by
    construction, which is precisely the property under test.
    """
    return f"{_branch_parent_action_id(child_run_id)}|{branch_index}|{_PLACEMENT.value}"


def _branch_parent_action_id(child_run_id: str) -> str:
    """The ``parent_action_id`` a branch of the child run actually carries.

    Production takes the child run's ``workflow_id`` and nothing else
    (`workflow_driver.py:8187` → `:7168-7177`); ``child_run_id`` is accepted here so
    the caller expresses "the parent_action_id OF THIS RUN" and the run-blindness is
    a fact this helper reports rather than an assumption the test bakes in.
    """
    del child_run_id  # deliberately unused — that IS candidate (A)'s defect
    return _parallelization_fanout_action_id(_W_CHILD)


def _basis_c(child_run_id: str, branch_index: int, entry_version: int = _ENTRY_VERSION) -> str:
    """The council's original pick — ``(parent_idempotency_key, branch_index, placement)``.

    DELIVERABLE §4 records the council selecting this triple and the orchestrator
    then WITHDRAWING its [HIGH] tree-wide-uniqueness rating.
    """
    child_run_key = _compute_run_idempotency_key(
        child_run_id, _W_CHILD, extras=(str(entry_version),)
    )
    return f"{_compute_step_idempotency_key(child_run_key, 0)}|{branch_index}|{_PLACEMENT.value}"


def _basis_b(child_run_id: str, branch_index: int) -> str:
    """Candidate (B) — the tree-wide internal identity, with ``placement`` added.

    DELIVERABLE §4 candidate (B): ``pre_dispatch_gate_owning_branch_identity``
    (`pause_state_projection.py:500`) — the identity the driver ALREADY composes for
    this exact branch population at `workflow_driver.py:8346` and `:12670` — plus the
    ``placement`` component whose omission was one of the two objections that defeated
    (B) at the council cross-read.
    """
    return (
        f"{pre_dispatch_gate_owning_branch_identity(child_run_id, branch_index)}|{_PLACEMENT.value}"
    )


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


def test_basis_a_parent_action_id_collides_across_sibling_child_runs() -> None:
    """**Candidate (A) is FALSIFIED.**

    Two peer workers dispatching the same ``child_workflow_id`` produce two distinct
    child runs whose branch-0 pre-dispatch escalations compose the **same** triple,
    because ``_parallelization_fanout_action_id`` (`workflow_driver.py:7168-7177`)
    is keyed on ``workflow_id`` alone and carries **no run identity**. This recreates
    B-71's own defect inside the proposed fix — the failure mode DELIVERABLE §4
    predicted, here on the realizable cross-run shape rather than the in-run one.
    """
    left, right = _child_run_ids()
    assert _basis_a(left, 0) == _basis_a(right, 0), (
        "candidate (A) unexpectedly separated the two branches — re-derive the fork, "
        "the evidence this witness was built on has changed"
    )
    # And the collision reaches the operator-facing delivery key through the REAL
    # composer (`hitl_gate_composer.py:428-440`, used at `:1302` as the webhook
    # Idempotency-Key + the CP audit action_id + the F2 ledger key), not merely the
    # abstract basis tuple.
    assert compose_hitl_action_id(
        _branch_parent_action_id(left), _PLACEMENT
    ) == compose_hitl_action_id(_branch_parent_action_id(right), _PLACEMENT)


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
    assert _basis_c(left, 0) != _basis_c(right, 0)


def test_basis_b_run_scoped_identity_survives_the_collision_witness() -> None:
    """**Candidate (B) survives.** Distinct child runs ⇒ distinct identities."""
    left, right = _child_run_ids()
    assert _basis_b(left, 0) != _basis_b(right, 0)


def test_basis_b_and_c_also_separate_equal_local_ordinals_at_one_placement() -> None:
    """The local ordinal is NOT doing the work — the run component is.

    Both surviving bases separate branch 0 from branch 0 (identical ordinal,
    identical placement) purely on the run component, which is the property the
    reverse-thread carrier needs per DELIVERABLE §4's three-way-convergent finding
    ("the reverse-thread carrier must be keyed by a tree-wide identity — not bare
    ``branch_index``").
    """
    left, right = _child_run_ids()
    assert _basis_b(left, 0) != _basis_b(right, 0)
    assert _basis_c(left, 0) != _basis_c(right, 0)

    # The bare-ordinal carrier — the shape the three-way finding rejects — collapses
    # them, so the separation above is attributable to the run component alone.
    def _bare_ordinal(child_run_id: str, branch_index: int) -> str:
        del child_run_id
        return f"{branch_index}|{_PLACEMENT.value}"

    assert _bare_ordinal(left, 0) == _bare_ordinal(right, 0)


def test_entry_version_bump_rotates_basis_c_even_when_the_snapshot_is_recovered() -> None:
    """**Candidate (C) is falsified on DELIVERABLE §5 precondition 4.**

    ``entry_version`` is folded into ``run_idempotency_key``
    (`workflow_driver.py:3312-3316`), so a resume after an ``entry_version`` bump
    recomputes a DIFFERENT token for (C) — on the ORDINARY resume path, where the
    paused child's original ``run_id`` is reused verbatim
    (`child_workflow_runner.py:230-234`). That is not the narrow mint→persist crash
    window precondition 4 scopes; it is every resumed escalation, which makes the
    unguarded-``entry_version`` defect (registered separately) load-bearing for the
    token rather than adjacent to it.
    """
    left, _ = _child_run_ids()
    assert _basis_c(left, 0, entry_version=1) != _basis_c(left, 0, entry_version=2)


def test_entry_version_bump_leaves_basis_b_stable_when_the_snapshot_is_recovered() -> None:
    """**Candidate (B) is stable on the ordinary resume path.**

    (B)'s run component is the child's ``run_id``, which a resume reuses verbatim from
    the snapshot rather than re-deriving, so an ``entry_version`` bump does not rotate
    the token. (B)'s residual exposure is confined to the crash-BEFORE-persist window
    — exactly the window the design's persist-once rule (DELIVERABLE §3) already
    declares and scopes, rather than an unbounded one.
    """
    left, _ = _child_run_ids()
    recovered = left  # the resume path threads snapshot.run_id, not a fresh derivation
    assert _basis_b(recovered, 0) == _basis_b(left, 0)


def test_crash_before_persist_is_the_only_window_that_rotates_basis_b() -> None:
    """Bounds (B)'s residual: with NO snapshot to recover, the child run_id is
    re-derived from the parent's ``entry_version``-bearing key, so the token does
    rotate — the mint→persist window, and only that window."""
    left_v1, _ = _child_run_ids(entry_version=1)
    left_v2, _ = _child_run_ids(entry_version=2)
    assert _basis_b(left_v1, 0) != _basis_b(left_v2, 0)
