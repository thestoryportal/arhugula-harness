"""B-69 impl leg — U-CP-64 as amended (`Implementation_Plan_Control_Plane_v2_47.md`).

Witnesses AC #A1 … #A10 for the two CP-owned surfaces CP spec v1.112 declares:
§1 the REQUIRED, non-downgradable `ResumeContext` response-provenance carrier, and
§2 the public projection-returning surface over the resume-tree walk.

Every criterion here is BY EXECUTION. The load-bearing ones are the
detect-then-refuse pairs — asserting the refusal, not merely the absence of a
helper — and AC #A8's STRUCTURAL check that no second recursion over
`PauseSnapshot` exists for the projection, which output-agreement alone cannot
establish (it would pass on every finite tested tree while a third classification
authority ships).
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest
from harness_core.identity import EntryID
from harness_cp.handoff_context import StateSummary
from harness_cp.hitl_placement import HITLResult
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.pause_resume_protocol_types import (
    EffectFencePausedBranchResumeState,
    EffectFenceResolution,
    EffectFenceResumeState,
    OrchestratorEffectFencePausedResumeState,
    PausedChildBranchResumeState,
    PauseSnapshot,
    PeerFanOutResumeState,
    PreDispatchGateOwningBranchResumeState,
    ResumeContext,
    WorkflowPauseReason,
)
from harness_cp.pause_state_projection import (
    AccessorDerivedResumeContext,
    BranchEffectFenceAddressableLocation,
    CrashReconstructionEffectFenceAddressableLocation,
    DepthZeroRootUniformFallbackOnlyLocation,
    HitlAddressableLocation,
    LinearEffectFenceAddressableLocation,
    OrchestratorEffectFenceAddressableLocation,
    PausedWorkflowState,
    PauseLocationSourceShape,
    PauseLocationVariant,
    PreDispatchUniformFallbackOnlyLocation,
    TransitivelyPausedLocation,
    pre_dispatch_gate_owning_branch_identity,
    project_pause_locations,
    walk_pause_tree,
)
from harness_cp.workflow_driver import (
    _collect_effect_fence_idempotency_keys,
    _collect_gate_owning_run_ids,
    _collect_pre_dispatch_gate_owning_identities,
    compute_hitl_uniform_fallback_eligible_run_id,
)
from harness_cp.workflow_driver_types import StepKind
from harness_is.state_ledger_entry_schema import Identifier
from pydantic import ValidationError

_WORKFLOW_ID = "wf-b69"


def _hitl(response: HITLResponse) -> HITLResult:
    return HITLResult(
        response=response,
        timestamp="2026-07-31T00:00:00Z",
        audit_ledger_entry_id=EntryID("entry-b69"),
        response_summary_hash="0" * 64,
    )


def _summary() -> StateSummary:
    return StateSummary(
        relevant_entries=(),
        summary_text="",
        summary_hash="0" * 64,
        idempotency_key=Identifier(""),
        external_references=(),
    )


def _snapshot(
    *,
    run_id: str,
    pause_reason: WorkflowPauseReason = WorkflowPauseReason.HITL_PENDING,
    step_index: int = 0,
    **carriers: object,
) -> PauseSnapshot:
    return PauseSnapshot(
        workflow_id=_WORKFLOW_ID,
        run_id=run_id,
        step_index=step_index,
        pause_reason=pause_reason,
        state_summary=_summary(),
        snapshot_hash="f" * 64,
        created_at=0,
        state_ledger_anchor="0" * 64,
        **carriers,  # pyright: ignore[reportArgumentType]
    )


def _pause_state(locations: tuple[object, ...] = ()) -> PausedWorkflowState:
    return PausedWorkflowState(
        workflow_id=_WORKFLOW_ID,
        created_at=1,
        staleness_token="tok-1",
        locations=locations,  # pyright: ignore[reportArgumentType]
    )


# --------------------------------------------------------------------------
# AC #A1 / #A2 / #A3 — the §1 provenance carrier
# --------------------------------------------------------------------------


def test_a1_accessor_derived_context_cannot_omit_the_read() -> None:
    """AC #A1 — REQUIRED, and read-then-omitted is UNREPRESENTABLE.

    There is no way to hold an accessor read and construct a token-free
    accessor-derived context: the projection field has no default. An OPTIONAL
    token would make omission itself the prohibited escape — `resume()` could not
    distinguish "read, then omitted" from "never read", leaving every accessor
    user's default path unfenced (safe-by-diligence, a species of luck).
    """
    with pytest.raises(ValidationError):
        AccessorDerivedResumeContext(hitl_response=_hitl(HITLResponse.APPROVE))  # pyright: ignore[reportCallIssue]

    ctx = AccessorDerivedResumeContext.from_pause_state(
        _pause_state(), hitl_response=_hitl(HITLResponse.APPROVE)
    )
    assert ctx.staleness_token == "tok-1"


def test_a1_bare_string_token_is_not_a_capability() -> None:
    """AC #A1 — the projection is the SOLE capability; a bare string a caller can
    retype is not. The carrier's field TYPE is the projection object, so a
    hand-written token string is refused at validation."""
    with pytest.raises(ValidationError):
        AccessorDerivedResumeContext(pause_state="tok-forged")  # pyright: ignore[reportArgumentType]


def test_a2_no_downgrade_path_from_accessor_derived_to_legacy() -> None:
    """AC #A2 — non-downgradability, by DETECT-THEN-REFUSE.

    Assert the REFUSAL, not merely the absence of a helper. Three distinct
    downgrade attempts are each refused: a named helper does not exist; field
    mutation is refused by the frozen carrier; and re-validating the
    accessor-derived dump into the legacy type is REFUSED by `extra="forbid"`
    rather than silently dropping the token.
    """
    ctx = AccessorDerivedResumeContext.from_pause_state(
        _pause_state(), hitl_response=_hitl(HITLResponse.APPROVE)
    )
    assert not hasattr(ctx, "without_token")
    assert not any(
        "downgrade" in name or "without_token" in name or "to_legacy" in name for name in dir(ctx)
    )
    with pytest.raises(ValidationError):
        ctx.pause_state = _pause_state()  # pyright: ignore[reportAttributeAccessIssue]
    with pytest.raises(ValidationError):
        ResumeContext.model_validate(ctx.model_dump())


def test_a3_legacy_variant_is_byte_compatible() -> None:
    """AC #A3 — every existing `hitl_response` / `hitl_responses` /
    `effect_fence_resolution` / `effect_fence_resolutions` semantic is unchanged
    for a caller who never took a read."""
    legacy = ResumeContext(
        hitl_response=_hitl(HITLResponse.APPROVE),
        hitl_responses={"child-a": _hitl(HITLResponse.REJECT)},
        effect_fence_resolution=EffectFenceResolution.RE_FIRE,
        effect_fence_resolutions={"key-a": EffectFenceResolution.ABORT},
    )
    assert legacy.hitl_response_for("child-a").response is HITLResponse.REJECT  # pyright: ignore[reportOptionalMemberAccess]
    assert legacy.hitl_response_for("child-z").response is HITLResponse.APPROVE  # pyright: ignore[reportOptionalMemberAccess]
    assert legacy.effect_fence_resolution_for("key-a") is EffectFenceResolution.ABORT
    assert legacy.effect_fence_resolution_for("key-z") is EffectFenceResolution.RE_FIRE
    assert not isinstance(legacy, AccessorDerivedResumeContext)
    assert set(ResumeContext.model_fields) == {
        "hitl_response",
        "hitl_responses",
        "effect_fence_resolution",
        "effect_fence_resolutions",
    }


def test_a3_accessor_derived_preserves_every_legacy_resolver_semantic() -> None:
    """AC #A3 — the accessor-derived variant resolves IDENTICALLY; the carrier
    records provenance, it does not change what anything resolves to."""
    ctx = AccessorDerivedResumeContext.from_pause_state(
        _pause_state(),
        hitl_response=_hitl(HITLResponse.APPROVE),
        hitl_responses={"child-a": _hitl(HITLResponse.REJECT)},
        effect_fence_resolution=EffectFenceResolution.RE_FIRE,
        effect_fence_resolutions={"key-a": EffectFenceResolution.ABORT},
    )
    assert ctx.hitl_response_for("child-a").response is HITLResponse.REJECT  # pyright: ignore[reportOptionalMemberAccess]
    assert ctx.hitl_response_for("child-z").response is HITLResponse.APPROVE  # pyright: ignore[reportOptionalMemberAccess]
    assert ctx.effect_fence_resolution_for("key-a") is EffectFenceResolution.ABORT
    assert ctx.effect_fence_resolution_for("key-z") is EffectFenceResolution.RE_FIRE


# --------------------------------------------------------------------------
# AC #A4 — the FOUR variants, the SOURCE SHAPES, the ABSENT key fields
# --------------------------------------------------------------------------


def _tree_with_one_of_each() -> PauseSnapshot:
    """A root container holding one location of every variant.

    - `TransitivelyPaused` — the root container node itself.
    - `UniformFallbackOnly` — a pre-dispatch gate-owning peer.
    - `EffectFenceAddressable` — a keyed fan-out fence branch.
    - `HitlAddressable` — a paused child whose own leaf gate fired.
    """
    child = _snapshot(run_id="child-run-1", step_index=3)
    return _snapshot(
        run_id="root-run",
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=3,
            pre_dispatch_gate_owning_branches=(
                PreDispatchGateOwningBranchResumeState(
                    branch_index=0, step_id="peer-0", step_kind=StepKind.SUB_AGENT_DISPATCH.value
                ),
            ),
            effect_fence_paused_branches=(
                EffectFencePausedBranchResumeState(
                    branch_index=1,
                    step_id="peer-1",
                    step_kind=StepKind.TOOL_STEP.value,
                    idempotency_key="key-real",
                ),
            ),
            paused_child_branches=(
                PausedChildBranchResumeState(
                    branch_index=2, step_id="peer-2", child_snapshot=child
                ),
            ),
        ),
    )


def test_a4_all_four_variants_present_against_one_tree() -> None:
    """AC #A4 — the projection returns all four variants against a tree with one
    of each."""
    locations = project_pause_locations(_tree_with_one_of_each())
    assert {loc.variant for loc in locations} == set(PauseLocationVariant)


def test_a4_uniform_fallback_and_transitively_paused_carry_no_identity_at_all() -> None:
    """AC #A4, the LOAD-BEARING assertion — not opaque, not redacted, **ABSENT**.

    The pre-dispatch internal identity is a `run_id`-shaped string; an operator who
    keys it hits the resolver's collision defence, which counts that response as
    unaddressed — the response is silently DROPPED, not refused. Livelock with no
    diagnostic. Absence makes CP v1.108 §1.1(b)'s prohibition a TYPE invariant.
    """
    identity_bearing = {"run_id", "child_run_id", "identity", "idempotency_key"}
    for cls in (
        PreDispatchUniformFallbackOnlyLocation,
        DepthZeroRootUniformFallbackOnlyLocation,
        TransitivelyPausedLocation,
    ):
        assert identity_bearing.isdisjoint(cls.model_fields), cls.__name__

    root = _tree_with_one_of_each()
    identity_values = {
        root.run_id,
        pre_dispatch_gate_owning_branch_identity(root.run_id, 0),
    }
    for location in project_pause_locations(root):
        if isinstance(
            location, PreDispatchUniformFallbackOnlyLocation | TransitivelyPausedLocation
        ):
            assert identity_values.isdisjoint(set(location.model_dump().values()))


def test_a4_crash_reconstruction_projects_with_the_key_field_absent() -> None:
    """AC #A4 / AC #16(a) — a fan-out crash-reconstruction fence carrier holding an
    EMPTY `idempotency_key` projects as effect-fence-addressable with the key field
    ABSENT, never carrying a `""` value both resume sites ignore on their
    truthiness check (the response would be silently DROPPED, not refused)."""
    root = _snapshot(
        run_id="root-run",
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=2,
            effect_fence_paused_branches=(
                EffectFencePausedBranchResumeState(
                    branch_index=0,
                    step_id="peer-0",
                    step_kind=StepKind.TOOL_STEP.value,
                    idempotency_key="",
                ),
            ),
        ),
    )
    fence = next(
        loc
        for loc in project_pause_locations(root)
        if loc.variant is PauseLocationVariant.EFFECT_FENCE_ADDRESSABLE
    )
    assert isinstance(fence, CrashReconstructionEffectFenceAddressableLocation)
    assert "idempotency_key" not in type(fence).model_fields
    assert "" not in set(fence.model_dump().values())


# --------------------------------------------------------------------------
# AC #A5 — TOTAL enumeration across BOTH uniform-fallback-only source shapes
# --------------------------------------------------------------------------


def test_a5a_pre_dispatch_and_addressable_locations_both_appear() -> None:
    """AC #A5(a) — omit either and the downstream operator's safety judgment
    INVERTS ("one location, uniform is safe" when the true set has two)."""
    locations = project_pause_locations(_tree_with_one_of_each())
    shapes = {loc.source_shape for loc in locations}
    assert PauseLocationSourceShape.PRE_DISPATCH_GATE_OWNING_BRANCH in shapes
    assert PauseLocationSourceShape.PAUSED_CHILD_BRANCH in shapes


def test_a5b_depth_zero_root_gate_owning_pause_is_uniform_fallback_only() -> None:
    """AC #A5(b) — the depth-0 root gate-owning pause (a top-level LINEAR /
    EVALUATOR_OPTIMIZER / DECENTRALIZED_HANDOFF HITL pause with no fan-out carrier)
    appears as `uniform-fallback-only`, NOT `HitlAddressable` and NOT omitted.

    This is the single most common HITL pause shape in the system. Rendering it as
    addressable would hand the operator a key the resolver silently IGNORES."""
    locations = project_pause_locations(_snapshot(run_id="root-run", step_index=7))
    assert len(locations) == 1
    only = locations[0]
    assert isinstance(only, DepthZeroRootUniformFallbackOnlyLocation)
    assert only.variant is PauseLocationVariant.UNIFORM_FALLBACK_ONLY
    assert only.step_index == 7


# --------------------------------------------------------------------------
# AC #A6 / #A10 — return shape + posture
# --------------------------------------------------------------------------


def test_a6_bare_identifier_sets_are_refused_as_the_return_shape() -> None:
    """AC #A6 — structured projections, never `list[str]` / `set[str]`. A bare set
    cannot populate position, step, reason and addressability without the caller
    re-walking, AND it would carry the one value that must not cross the
    boundary."""
    locations = project_pause_locations(_tree_with_one_of_each())
    assert isinstance(locations, tuple)
    assert locations
    assert not any(isinstance(loc, str) for loc in locations)
    for loc in locations:
        assert hasattr(loc, "variant")
        assert hasattr(loc, "source_shape")
        assert hasattr(loc, "pause_reason")
        assert hasattr(loc, "step_index")


def test_a10_projection_is_not_shaped_like_the_hitl_approval_queue() -> None:
    """AC #A10 — no TTL field, no per-item status field, no queue-lifecycle
    vocabulary. The pause journal and the HITL approval queue have deliberately
    different postures, and conflating them in a type is how that difference gets
    lost."""
    forbidden = {"ttl", "ttl_ms", "expires_at", "status", "state", "queue", "queued_at", "claimed"}
    for cls in (
        HitlAddressableLocation,
        BranchEffectFenceAddressableLocation,
        CrashReconstructionEffectFenceAddressableLocation,
        OrchestratorEffectFenceAddressableLocation,
        LinearEffectFenceAddressableLocation,
        PreDispatchUniformFallbackOnlyLocation,
        DepthZeroRootUniformFallbackOnlyLocation,
        TransitivelyPausedLocation,
        PausedWorkflowState,
    ):
        assert forbidden.isdisjoint(cls.model_fields), cls.__name__


# --------------------------------------------------------------------------
# AC #A7 / #A8 — one authority, ONE SHARED TRAVERSAL
# --------------------------------------------------------------------------


def _recursive_pause_snapshot_walkers(module_path: Path) -> set[str]:
    """Every function in `module_path` that recurses over a `PauseSnapshot` tree.

    Detected structurally: a function that calls itself AND performs a real
    ATTRIBUTE ACCESS on one of the resume-tree carrier fields. The attribute-access
    test (rather than a substring scan of the dumped node) is what keeps the check
    honest — a prose docstring that merely NAMES a carrier field is not a walk, and
    an earlier draft of this helper mis-flagged `_payload_engine_signature` on
    exactly that basis.

    This is what makes AC #A8's criterion checkable rather than prose: an
    output-agreement-only assertion would let a THIRD classification authority ship
    and pass on every finite tested tree.
    """
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    carrier_fields = {
        "paused_child_branches",
        "pre_dispatch_gate_owning_branches",
        "effect_fence_paused_branches",
        "effect_fence_resume",
        "orchestrator_effect_fence_resume",
        "fan_out_resume",
        "peer_fan_out_resume",
    }
    walkers: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        calls_self = any(
            isinstance(inner, ast.Call)
            and isinstance(inner.func, ast.Name)
            and inner.func.id == node.name
            for inner in ast.walk(node)
        )
        touches_carrier = any(
            isinstance(inner, ast.Attribute) and inner.attr in carrier_fields
            for inner in ast.walk(node)
        )
        if calls_self and touches_carrier:
            walkers.add(node.name)
    return walkers


def test_a8_exactly_one_recursion_over_pause_snapshot_exists_in_cp() -> None:
    """AC #A8, the STRUCTURAL half — ONE SHARED TRAVERSAL, not merely agreeing
    outputs.

    `_collect_gate_owning_run_ids` and `_collect_effect_fence_idempotency_keys`
    were already SEPARATE recursive walks before this arc, so an
    output-agreement-only criterion would let a third authority ship. After the
    B-69 impl leg exactly ONE recursion over `PauseSnapshot` exists in CP, in the
    projection module, and both resolvers plus the public projection are filters
    over it.
    """
    import harness_cp.pause_state_projection as projection_module
    import harness_cp.workflow_driver as driver_module

    projection_walkers = _recursive_pause_snapshot_walkers(Path(inspect.getfile(projection_module)))
    driver_walkers = _recursive_pause_snapshot_walkers(Path(inspect.getfile(driver_module)))
    assert projection_walkers == {"_walk"}, projection_walkers
    assert driver_walkers == set(), driver_walkers


def test_a8_resolvers_and_projection_agree_on_gate_ownership() -> None:
    """AC #A8, the output half — every location the resolvers count as gate-owning
    appears in the projection with a gate-owning variant, and no location the
    resolvers treat as a traversable container appears as addressable."""
    root = _tree_with_one_of_each()
    entries = walk_pause_tree(root)
    gate_owning = _collect_gate_owning_run_ids(root)
    assert gate_owning == [e.gate_owning_identity for e in entries if e.gate_owning_identity]
    for entry in entries:
        if entry.gate_owning_identity is not None:
            assert entry.projection.variant in {
                PauseLocationVariant.HITL_ADDRESSABLE,
                PauseLocationVariant.UNIFORM_FALLBACK_ONLY,
            }
        if entry.projection.variant is PauseLocationVariant.TRANSITIVELY_PAUSED:
            assert entry.gate_owning_identity is None
            assert entry.effect_fence_key is None


def test_a8_effect_fence_view_reproduces_the_pre_b69_enumeration() -> None:
    """AC #A8 — the fence resolver's own view over the shared walk, including the
    empty-key crash-reconstruction entry the projection deliberately hides."""
    root = _snapshot(
        run_id="root-run",
        pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
        effect_fence_resume=EffectFenceResumeState(idempotency_key="linear-key"),
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=2,
            effect_fence_paused_branches=(
                EffectFencePausedBranchResumeState(
                    branch_index=0,
                    step_id="p0",
                    step_kind=StepKind.TOOL_STEP.value,
                    idempotency_key="",
                ),
                EffectFencePausedBranchResumeState(
                    branch_index=1,
                    step_id="p1",
                    step_kind=StepKind.TOOL_STEP.value,
                    idempotency_key="branch-key",
                ),
            ),
        ),
    )
    assert _collect_effect_fence_idempotency_keys(root) == ["linear-key", "", "branch-key"]


def test_a8_never_keyable_subset_is_a_view_over_the_same_walk() -> None:
    """AC #A8 — the never-keyable subset cannot drift from the set it is a subset
    of."""
    root = _tree_with_one_of_each()
    never_keyable = _collect_pre_dispatch_gate_owning_identities(root)
    assert never_keyable == frozenset({pre_dispatch_gate_owning_branch_identity(root.run_id, 0)})
    assert never_keyable <= set(_collect_gate_owning_run_ids(root))


def test_a7_orchestrator_and_linear_fence_shapes_project_from_their_own_carriers() -> None:
    """AC #A7 / #A4 — the orchestrator and LINEAR fence source shapes, each
    declaring exactly the fields its own carrier has."""
    root = _snapshot(
        run_id="root-run",
        pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
        effect_fence_resume=EffectFenceResumeState(idempotency_key="linear-key"),
        orchestrator_effect_fence_resume=OrchestratorEffectFencePausedResumeState(
            idempotency_key="orch-key",
            step_id="orchestrator",
            step_kind=StepKind.TOOL_STEP.value,
        ),
    )
    locations = project_pause_locations(root)
    linear = next(loc for loc in locations if isinstance(loc, LinearEffectFenceAddressableLocation))
    orch = next(
        loc for loc in locations if isinstance(loc, OrchestratorEffectFenceAddressableLocation)
    )
    assert linear.idempotency_key == "linear-key"
    assert "step_kind" not in type(linear).model_fields
    assert "step_id" not in type(linear).model_fields
    assert "branch_index" not in type(linear).model_fields
    assert orch.step_kind is StepKind.TOOL_STEP
    assert "branch_index" not in type(orch).model_fields


# --------------------------------------------------------------------------
# AC #A9 — properties 1–8 unchanged
# --------------------------------------------------------------------------


def test_a9_uniform_fallback_resolver_semantics_unchanged() -> None:
    """AC #A9 — §2 publishes the classification; it defines none of it. The
    sole-member rule still fires at exactly 1 and returns `None` at 2+."""
    sole = _snapshot(run_id="root-run")
    assert compute_hitl_uniform_fallback_eligible_run_id(sole, ResumeContext()) == "root-run"

    two = _snapshot(
        run_id="root-run",
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=3,
            pre_dispatch_gate_owning_branches=(
                PreDispatchGateOwningBranchResumeState(
                    branch_index=0, step_id="p0", step_kind=StepKind.SUB_AGENT_DISPATCH.value
                ),
                PreDispatchGateOwningBranchResumeState(
                    branch_index=1, step_id="p1", step_kind=StepKind.SUB_AGENT_DISPATCH.value
                ),
            ),
        ),
    )
    assert compute_hitl_uniform_fallback_eligible_run_id(two, ResumeContext()) is None
