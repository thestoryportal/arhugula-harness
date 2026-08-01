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
    KeyAbsentLinearEffectFenceAddressableLocation,
    KeyAbsentOrchestratorEffectFenceAddressableLocation,
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
        KeyAbsentOrchestratorEffectFenceAddressableLocation,
        LinearEffectFenceAddressableLocation,
        KeyAbsentLinearEffectFenceAddressableLocation,
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
# AC #A11 — the KEY-ABSENT sibling source shapes, ALL THREE effect-fence carriers
# (`B-100` impl remainder; CP spec v1.113 §1.1, CP plan v2.48 §1.2)
# --------------------------------------------------------------------------


def test_a11a_empty_linear_key_projects_with_the_key_field_absent() -> None:
    """AC #A11(a) — a LINEAR `EffectFenceResumeState` carrying `idempotency_key=""`
    projects as `effect-fence-addressable` with the key field ABSENT.

    Never a `""` key VALUE, and never omitted from the enumeration. This state is
    GENUINELY REACHABLE: the LINEAR capture site's guard is
    `isinstance(_fence_key, str)` alone (`workflow_driver.py:5456`), with no
    truthiness test — so this witness is NOT downgraded to the orchestrator shape's
    constructed-snapshot-only posture (CP plan v2.48 AC #A11 witness constraint 2).
    """
    root = _snapshot(
        run_id="root-run",
        pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
        effect_fence_resume=EffectFenceResumeState(idempotency_key=""),
    )
    locations = project_pause_locations(root)
    fence = next(
        loc for loc in locations if loc.variant is PauseLocationVariant.EFFECT_FENCE_ADDRESSABLE
    )
    assert isinstance(fence, KeyAbsentLinearEffectFenceAddressableLocation)
    assert fence.source_shape is PauseLocationSourceShape.EFFECT_FENCE_LINEAR_KEY_ABSENT
    assert "idempotency_key" not in type(fence).model_fields
    assert "" not in set(fence.model_dump().values())
    # ... and NOT omitted — the enumeration stays total over gate-owning locations.
    assert len(locations) == 1


def test_a11b_empty_orchestrator_key_projects_with_the_key_field_absent() -> None:
    """AC #A11(b) — the same for `OrchestratorEffectFencePausedResumeState`.

    **CONSTRUCTED-SNAPSHOT, never an e2e — deliberately.** The orchestrator carrier's
    sole shipped capture site (`workflow_driver.py:12392`) guards on a TRUTHY key at
    `:12376`-`:12381`, so NO production path can produce this state. The shape is
    declared on TYPE-TOTALITY grounds: the carrier declares `idempotency_key: str`
    with no length constraint, and the projection is a total function over journaled
    records that outlive the capture-site code. An acceptance closeout demanding an
    e2e witness here is demanding an unbuildable one (CP plan v2.48 AC #A11 witness
    constraint 1).

    *Register row `B-100` asserted the OPPOSITE of that guard's presence; the premise
    was checked at the spec leg and found FALSE. The disposition is unchanged; only
    its ground is (CP spec v1.113 §0.4 finding (i)).*
    """
    root = _snapshot(
        run_id="root-run",
        pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
        orchestrator_effect_fence_resume=OrchestratorEffectFencePausedResumeState(
            idempotency_key="",
            step_id="orchestrator",
            step_kind=StepKind.TOOL_STEP.value,
        ),
    )
    fence = next(
        loc
        for loc in project_pause_locations(root)
        if loc.variant is PauseLocationVariant.EFFECT_FENCE_ADDRESSABLE
    )
    assert isinstance(fence, KeyAbsentOrchestratorEffectFenceAddressableLocation)
    assert fence.source_shape is PauseLocationSourceShape.EFFECT_FENCE_ORCHESTRATOR_KEY_ABSENT
    assert "idempotency_key" not in type(fence).model_fields
    assert "" not in set(fence.model_dump().values())
    # No `step_kind` capture is added anywhere — the shape inherits its carrier's
    # field set EXACTLY, minus the key.
    assert fence.step_kind is StepKind.TOOL_STEP
    assert fence.step_id == "orchestrator"


def test_a11c1_key_absent_shapes_cannot_be_constructed_carrying_a_key() -> None:
    """AC #A11(c1) — unrepresentability, not merely absence, direction ONE.

    Assert the REFUSAL. An absence-only assertion cannot tell a type invariant from
    a happens-to-be-`None`.
    """
    with pytest.raises(ValidationError):  # LINEAR key-absent shape cannot carry a key
        KeyAbsentLinearEffectFenceAddressableLocation(
            pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
            step_index=0,
            idempotency_key="k",  # pyright: ignore[reportCallIssue]
        )
    with pytest.raises(ValidationError):  # orchestrator key-absent shape cannot carry a key
        KeyAbsentOrchestratorEffectFenceAddressableLocation(
            pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
            step_index=0,
            step_id="s",
            step_kind=StepKind.TOOL_STEP,
            idempotency_key="k",  # pyright: ignore[reportCallIssue]
        )


def test_a11c2_key_bearing_shapes_cannot_be_constructed_carrying_an_empty_key() -> None:
    """AC #A11(c2) — direction TWO, the load-bearing half this widening adds.

    A key-bearing shape that accepts `""` reintroduces exactly the value the
    key-absent shapes exist to keep off the boundary, while passing an absence-only
    assertion.
    """
    with pytest.raises(ValidationError):
        LinearEffectFenceAddressableLocation(
            pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
            step_index=0,
            idempotency_key="",
        )
    with pytest.raises(ValidationError):
        OrchestratorEffectFenceAddressableLocation(
            pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
            step_index=0,
            step_id="s",
            step_kind=StepKind.TOOL_STEP,
            idempotency_key="",
        )


def test_a11c3_key_bearing_shapes_cannot_be_constructed_with_the_key_omitted() -> None:
    """AC #A11(c3) — direction THREE, and NOT redundant with (c2).

    An implementation using one key-bearing type with an **optional but
    length-constrained** field passes (c2) — it does reject `""` — while still
    admitting a key-bearing projection with NO key at all, which is exactly the
    illegal state this union exists to close. *(Its omission from an earlier draft
    was caught at the spec leg's out-of-family review round 5 [P1].)*
    """
    with pytest.raises(ValidationError):
        LinearEffectFenceAddressableLocation(  # pyright: ignore[reportCallIssue]
            pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
            step_index=0,
        )
    with pytest.raises(ValidationError):
        OrchestratorEffectFenceAddressableLocation(  # pyright: ignore[reportCallIssue]
            pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
            step_index=0,
            step_id="s",
            step_kind=StepKind.TOOL_STEP,
        )


def test_a11d_branch_carrier_behaviour_is_unchanged() -> None:
    """AC #A11(d) — the branch carrier's existing behaviour is UNCHANGED.

    Its key-absent shape is now a SPECIAL CASE of the general rule, not a separate
    rule. AC #A4's crash-reconstruction witness re-runs green, unmodified (see
    `test_a4_crash_reconstruction_projects_with_the_key_field_absent`); this asserts
    the key-BEARING branch shape is equally untouched.
    """
    root = _snapshot(
        run_id="root-run",
        pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=1,
            effect_fence_paused_branches=(
                EffectFencePausedBranchResumeState(
                    branch_index=0,
                    step_id="p0",
                    step_kind=StepKind.TOOL_STEP.value,
                    idempotency_key="branch-key",
                ),
            ),
        ),
    )
    fence = next(
        loc
        for loc in project_pause_locations(root)
        if loc.variant is PauseLocationVariant.EFFECT_FENCE_ADDRESSABLE
    )
    assert isinstance(fence, BranchEffectFenceAddressableLocation)
    assert fence.idempotency_key == "branch-key"


def test_a11_resolver_enumeration_is_unchanged_by_the_keyless_routing() -> None:
    """AC #A11 / #A9 — §2 publishes the classification; it defines NONE of it.

    The projection now hides the empty LINEAR and orchestrator keys, but the
    RESOLVER-only half of the walk still enumerates `""` for every key-absent shape,
    byte-for-byte as before. Narrowing `effect_fence_key` to `None` here would
    silently change a CP CLASSIFICATION RULE (which locations the sole-member
    uniform-fallback test counts) — which CP spec v1.113 §2 forbids this surface
    from doing, and which is `B-107`'s scope, not this row's.
    """
    root = _snapshot(
        run_id="root-run",
        pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
        effect_fence_resume=EffectFenceResumeState(idempotency_key=""),
        orchestrator_effect_fence_resume=OrchestratorEffectFencePausedResumeState(
            idempotency_key="",
            step_id="orchestrator",
            step_kind=StepKind.TOOL_STEP.value,
        ),
    )
    assert _collect_effect_fence_idempotency_keys(root) == ["", ""]
    assert [entry.effect_fence_key for entry in walk_pause_tree(root)] == ["", ""]


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
