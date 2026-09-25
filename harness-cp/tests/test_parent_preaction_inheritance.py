"""CP-side carrier, fold, selection, validation and hash for matching parent
PRE_ACTION inheritance (operator decision 2026-09-24; CP spec v1.120 C-CP-17 §17.3,
C-CP-25 execute_workflow input, C-CP-26 property 7).

CP-only slice: this proves the interface a Runtime `ChildWorkflowRunner` will feed
(`execute_workflow_at_depth(inherited_hitl_placements=..., descent_depth=1,)`) and the selection contract a Runtime
composer will apply. It does NOT prove a child's real gate prompts once; that
one-prompt audit witness belongs to the separate Runtime slice.
"""

from __future__ import annotations

from typing import Any, cast

import pytest
from harness_core import PersonaTier, StepID, WorkloadClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.hitl_placement import (
    HITLPlacement,
    HITLPlacementKind,
    select_governing_pre_action_placement,
)
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import CascadePolicy, TopologyPattern
from harness_cp.workflow_driver import (
    StepDispatcher,
    StepDispatcherRegistry,
    _captured_hitl_gate_config_hash,  # pyright: ignore[reportPrivateUsage]
    _hash_hitl_gate_config,  # pyright: ignore[reportPrivateUsage]
    execute_workflow_at_depth,
)
from harness_cp.workflow_driver_types import (
    RunStatus,
    StepKind,
    WorkflowStep,
    fold_step_hitl_placements,
)
from harness_cp.workflow_manifest_entry import StepOverride, WorkflowManifestEntry
from pydantic import ValidationError

from .test_workflow_driver_hitl_gate_config_hash_b79 import (
    _ctx,  # pyright: ignore[reportPrivateUsage]
    _peer_steps,  # pyright: ignore[reportPrivateUsage]
    _PreDispatchGateAlwaysDispatcher,  # pyright: ignore[reportPrivateUsage]
    _PreDispatchGateOnceDispatcher,  # pyright: ignore[reportPrivateUsage]
)

_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)


def _pre(
    *tools: str, timeout: int | None = None, cascade: CascadePolicy | None = None
) -> HITLPlacement:
    return HITLPlacement(
        position=HITLPlacementKind.PRE_ACTION,
        tool_filter=tools or None,
        timeout=timeout,
        cascade_policy=cascade,
    )


def _manifest(
    topology: TopologyPattern,
    placements: tuple[HITLPlacement, ...] = (),
    overrides: dict[StepID, StepOverride] | None = None,
) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id="wf-child",
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=topology,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=placements,
        per_step_overrides=overrides or {},
    )


# --- 1. First-match selection contract (input contract for the Runtime composer) ------


def test_unfiltered_placement_governs_tool_and_inference_actions() -> None:
    parent = _pre()

    assert select_governing_pre_action_placement((parent,), tool_id="fs.write") is parent
    assert select_governing_pre_action_placement((parent,), tool_id=None) is parent


def test_filtered_placement_governs_only_its_exact_tools_never_inference() -> None:
    parent = _pre("fs.write")

    assert select_governing_pre_action_placement((parent,), tool_id="fs.write") is parent
    assert select_governing_pre_action_placement((parent,), tool_id="http.get") is None
    assert select_governing_pre_action_placement((parent,), tool_id="fs.writer") is None
    # A filtered PRE_ACTION limits which TOOLS trigger the gate (§17.3): inference is not one.
    assert select_governing_pre_action_placement((parent,), tool_id=None) is None


def test_first_placement_in_composed_order_governs_so_a_narrower_child_cannot_suppress_parent() -> (
    None
):
    parent = _pre(timeout=1000)
    narrower_child = _pre("other", timeout=9)

    assert select_governing_pre_action_placement((parent, narrower_child), tool_id="x") is parent
    assert (
        select_governing_pre_action_placement((parent, narrower_child), tool_id="other") is parent
    )


def test_identical_parent_and_child_placements_select_exactly_one() -> None:
    parent = _pre("fs.write", timeout=1000)
    duplicate = _pre("fs.write", timeout=1000)

    assert select_governing_pre_action_placement((parent, duplicate), tool_id="fs.write") is parent


def test_root_duplicate_same_position_placements_select_the_first() -> None:
    first, second = _pre(timeout=1), _pre(timeout=2)

    assert select_governing_pre_action_placement((first, second), tool_id=None) is first


def test_child_placement_governs_actions_the_parent_does_not_cover() -> None:
    parent = _pre("fs.write", timeout=1000)
    child = _pre("http.get", timeout=5)

    assert select_governing_pre_action_placement((parent, child), tool_id="fs.write") is parent
    assert select_governing_pre_action_placement((parent, child), tool_id="http.get") is child
    assert select_governing_pre_action_placement((parent, child), tool_id="other") is None


def test_only_pre_action_placements_are_selectable() -> None:
    boundary = HITLPlacement(position=HITLPlacementKind.SUB_AGENT_BOUNDARY)

    assert select_governing_pre_action_placement((boundary,), tool_id=None) is None


# --- 2. tool_filter validation: exact names only, patterns refused loudly -------------


@pytest.mark.parametrize(
    "entry",
    ["fs.*", "fs.?rite", "[fs]", "{a,b}", "(a|b)", "a|b", "^fs", "fs$", "a+", "a\\b", "!a", ""],
)
def test_tool_filter_refuses_glob_regex_and_empty_entries(entry: str) -> None:
    with pytest.raises(ValidationError, match="tool_filter"):
        HITLPlacement(position=HITLPlacementKind.PRE_ACTION, tool_filter=(entry,))


def test_tool_filter_refuses_an_empty_filter_that_would_silently_never_gate() -> None:
    with pytest.raises(ValidationError, match="tool_filter"):
        HITLPlacement(position=HITLPlacementKind.PRE_ACTION, tool_filter=())


@pytest.mark.parametrize("name", ["fs.write", "read_file", "mcp__srv__tool", "srv:tool", "a-b/c@1"])
def test_tool_filter_admits_plain_tool_names(name: str) -> None:
    assert _pre(name).tool_filter == (name,)


# --- 3. Fold order ----------------------------------------------------------------------


def test_fold_composes_outer_ancestor_then_parent_then_child_declarations() -> None:
    root, parent, own = _pre("a"), _pre("b"), _pre("c")

    folded = fold_step_hitl_placements((own,), None, inherited=(root, parent))

    assert folded == (root, parent, own)


def test_fold_with_no_inherited_prefix_is_byte_identical_to_the_workflow_tuple() -> None:
    own = (_pre("c"),)

    assert fold_step_hitl_placements(own, None) is own
    assert fold_step_hitl_placements(own, None, inherited=()) is own


def test_per_step_pre_action_override_cannot_add_a_second_gate_under_an_inherited_one() -> None:
    inherited = _pre(timeout=1000)
    override = _pre("x", timeout=1)

    folded = fold_step_hitl_placements((), override, inherited=(inherited,))

    assert folded == (inherited,)


# --- 4. Driver context sites carry the prefix (real execute_workflow) -------------------


class _ContextRecorder:
    def __init__(self) -> None:
        self.seen: dict[str, tuple[HITLPlacement, ...]] = {}

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        return cast(StepDispatcher, self)

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        self.seen[str(step.step_id)] = step_context.hitl_placements
        return {"ok": True}


def _linear_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID(name),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"n": name},
        )
        for name in ("s0", "s1")
    ]


def _run(
    manifest: WorkflowManifestEntry,
    steps: list[WorkflowStep],
    **kwargs: Any,
) -> _ContextRecorder:
    recorder = _ContextRecorder()
    result = execute_workflow_at_depth(
        manifest,
        steps,
        run_id="run-inherit",
        ctx=_ctx(),
        default_model_binding=_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, recorder),
        **kwargs,
        descent_depth=1,
    )
    assert result.status is RunStatus.SUCCESS
    return recorder


@pytest.mark.parametrize("topology", [TopologyPattern.SINGLE_THREADED_LINEAR])
def test_child_with_no_placement_receives_the_inherited_prefix_on_every_step(
    topology: TopologyPattern,
) -> None:
    inherited = (_pre(timeout=1000),)

    recorder = _run(_manifest(topology), _linear_steps(), inherited_hitl_placements=inherited)

    assert recorder.seen == {"s0": inherited, "s1": inherited}


def test_inherited_prefix_precedes_the_childs_own_workflow_placements() -> None:
    inherited = (_pre("fs.write", timeout=1000),)
    own = _pre("http.get", timeout=5)

    recorder = _run(
        _manifest(TopologyPattern.SINGLE_THREADED_LINEAR, (own,)),
        _linear_steps(),
        inherited_hitl_placements=inherited,
    )

    assert recorder.seen["s0"] == (*inherited, own)


def test_per_step_override_cannot_erase_or_duplicate_an_inherited_placement() -> None:
    inherited = (_pre(timeout=1000),)
    override = StepOverride(step_id=StepID("s1"), hitl_placement=_pre("x", timeout=1))

    recorder = _run(
        _manifest(TopologyPattern.SINGLE_THREADED_LINEAR, (), {StepID("s1"): override}),
        _linear_steps(),
        inherited_hitl_placements=inherited,
    )

    assert recorder.seen["s1"] == inherited


def test_transitive_two_ancestor_prefix_reaches_the_grandchilds_steps_in_order() -> None:
    root_a, parent_b = _pre("a", timeout=1), _pre("b", timeout=2)

    recorder = _run(
        _manifest(TopologyPattern.SINGLE_THREADED_LINEAR),
        _linear_steps(),
        inherited_hitl_placements=(root_a, parent_b),
    )

    assert recorder.seen["s0"] == (root_a, parent_b)


def test_empty_prefix_leaves_the_root_step_context_exactly_as_declared() -> None:
    own = (_pre("c"),)

    with_default = _run(_manifest(TopologyPattern.SINGLE_THREADED_LINEAR, own), _linear_steps())
    with_explicit_empty = _run(
        _manifest(TopologyPattern.SINGLE_THREADED_LINEAR, own),
        _linear_steps(),
        inherited_hitl_placements=(),
    )

    assert with_default.seen == with_explicit_empty.seen == {"s0": own, "s1": own}


def test_parallelization_branches_receive_the_inherited_prefix() -> None:
    inherited = (_pre(timeout=1000),)

    recorder = _run(
        _manifest(TopologyPattern.PARALLELIZATION),
        _peer_steps(),
        inherited_hitl_placements=inherited,
    )

    assert set(recorder.seen.values()) == {inherited}


# --- 5. The prefix is bound into the captured gate-config hash --------------------------


def test_captured_hash_of_an_empty_prefix_is_byte_identical_to_the_root_hash() -> None:
    own = (_pre("c", timeout=7),)
    manifest = _manifest(TopologyPattern.SINGLE_THREADED_LINEAR, own)
    step = _linear_steps()[0]

    captured = _captured_hitl_gate_config_hash(
        step, manifest, default_model_binding=_BINDING, inherited_hitl_placements=()
    )

    assert captured == _hash_hitl_gate_config(own, frozenset())


def test_captured_hash_changes_with_a_nonempty_or_changed_or_reordered_prefix() -> None:
    manifest = _manifest(TopologyPattern.SINGLE_THREADED_LINEAR)
    step = _linear_steps()[0]
    a, b = _pre("a"), _pre("b")

    def hash_with(prefix: tuple[HITLPlacement, ...]) -> str:
        return _captured_hitl_gate_config_hash(
            step, manifest, default_model_binding=_BINDING, inherited_hitl_placements=prefix
        )

    assert (
        len({hash_with(()), hash_with((a,)), hash_with((b,)), hash_with((a, b)), hash_with((b, a))})
        == 5
    )


def test_a_changed_parent_prefix_fails_a_child_resume_closed_and_an_unchanged_one_resumes() -> None:
    prefix = (_pre("read_file", timeout=5000, cascade=CascadePolicy.PAUSE),)
    manifest = _manifest(TopologyPattern.PARALLELIZATION)
    dispatcher = _PreDispatchGateOnceDispatcher()
    paused = execute_workflow_at_depth(
        manifest,
        _peer_steps(),
        run_id="run-1",
        ctx=_ctx(),
        default_model_binding=_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
        inherited_hitl_placements=prefix,
        descent_depth=1,
    )
    assert paused.status is RunStatus.PAUSED
    snapshot = paused.pause_snapshot
    assert snapshot is not None

    def resume(inherited: tuple[HITLPlacement, ...], disp: Any) -> Any:
        return execute_workflow_at_depth(
            manifest,
            _peer_steps(),
            run_id="run-1",
            ctx=_ctx(),
            default_model_binding=_BINDING,
            step_dispatchers=cast(StepDispatcherRegistry, disp),
            pause_snapshot_input=snapshot,
            inherited_hitl_placements=inherited,
            descent_depth=1,
        )

    dropped = resume((), _PreDispatchGateAlwaysDispatcher())
    narrowed = resume((_pre("write_file", timeout=5000, cascade=CascadePolicy.PAUSE),), dispatcher)
    unchanged = resume(prefix, dispatcher)

    assert dropped.status is RunStatus.FAILED
    assert "hitl-gate-config-changed" in (dropped.fail_class or "")
    assert narrowed.status is RunStatus.FAILED
    assert "hitl-gate-config-changed" in (narrowed.fail_class or "")
    assert unchanged.status is RunStatus.SUCCESS


@pytest.mark.parametrize(
    "kind", [HITLPlacementKind.SUB_AGENT_BOUNDARY, HITLPlacementKind.VALIDATOR_ESCALATION]
)
def test_only_pre_action_placements_may_be_inherited(kind: HITLPlacementKind) -> None:
    # The operator decision covers PRE_ACTION only; boundary and validator placements
    # belong to the declaring workflow and must never ride down to a child.
    with pytest.raises(ValueError, match="PRE_ACTION"):
        execute_workflow_at_depth(
            _manifest(TopologyPattern.SINGLE_THREADED_LINEAR),
            _linear_steps(),
            run_id="run-inherit",
            ctx=_ctx(),
            default_model_binding=_BINDING,
            step_dispatchers=cast(StepDispatcherRegistry, _ContextRecorder()),
            inherited_hitl_placements=(HITLPlacement(position=kind),),
            descent_depth=1,
        )
