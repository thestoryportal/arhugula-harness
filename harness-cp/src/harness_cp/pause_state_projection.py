"""CP spec v1.112 §2 — the public projection-returning surface over the resume tree.

`B-69` impl leg (U-CP-64 as amended at `Implementation_Plan_Control_Plane_v2_47.md`).

**One authority for the classification.** CP publishes ONE traversal of the resume
tree; the projection and the two uniform-fallback resolvers are *views over that
same walk*, never sibling walkers whose outputs happen to agree (CP spec v1.112
§2.2 constraint / plan AC #A8). `workflow_driver._collect_gate_owning_run_ids`,
`workflow_driver._collect_pre_dispatch_gate_owning_identities` and
`workflow_driver._collect_effect_fence_idempotency_keys` are re-expressed here as
filters over :func:`walk_pause_tree`, so a future divergence is structurally
impossible rather than merely tested-against.

**The public projection carries NO never-keyable identity.** The walk entry
carries the resolver-only identity (a pre-dispatch composed identity, the depth-0
root's own `run_id`) alongside its projection; the *projection* declares no field
for it at all (CP spec v1.112 §2.2 constraint 2 — absent, not opaque, not
redacted). That absence is a type invariant here, not a convention: the variant
classes that must not carry an identity simply do not declare one.

**Four variants, eight source shapes.** The variant set is exactly the council
record's FOUR (CP spec v1.112 §2.1); the SOURCE column is what widened. A variant
spanning more than one source shape carries a source-shape sub-discriminator so a
field absent on one shape is *unrepresentable* there rather than merely optional
— modelling `step_kind` (or the fence key) as a plain optional field would readmit
the illegal states the closed union exists to close.

| Variant | Source shape | `step_kind` | key field |
|---|---|---|---|
| HITL-addressable | paused child branch | absent | child `run_id` |
| effect-fence-addressable | branch | present | `idempotency_key` |
| effect-fence-addressable | branch (crash reconstruction) | present | **absent** |
| effect-fence-addressable | orchestrator | present | `idempotency_key` |
| effect-fence-addressable | LINEAR | absent | `idempotency_key` |
| uniform-fallback-only | pre-dispatch gate-owning branch | present | **absent** |
| uniform-fallback-only | depth-0 root gate-owning pause | absent | **absent** |
| transitively-paused | container node | absent | **absent** |

Authority: `Spec_Control_Plane_v1_112.md` §1 + §2;
`Implementation_Plan_Control_Plane_v2_47.md` §1; consumed cross-axis by
`Spec_Harness_Runtime_v1.md` v1.107 §14.14.9.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal, NamedTuple, Self

from pydantic import BaseModel, ConfigDict, Field

from harness_cp.hitl_placement import HITLResult
from harness_cp.pause_resume_protocol_types import (
    EffectFenceResolution,
    PauseSnapshot,
    ResumeContext,
    WorkflowPauseReason,
)
from harness_cp.workflow_driver_types import StepKind

__all__ = [
    "AccessorDerivedResumeContext",
    "BranchEffectFenceAddressableLocation",
    "CrashReconstructionEffectFenceAddressableLocation",
    "DepthZeroRootUniformFallbackOnlyLocation",
    "HitlAddressableLocation",
    "LinearEffectFenceAddressableLocation",
    "OrchestratorEffectFenceAddressableLocation",
    "PauseLocationProjection",
    "PauseLocationSourceShape",
    "PauseLocationVariant",
    "PauseTreeWalkEntry",
    "PausedWorkflowState",
    "PreDispatchUniformFallbackOnlyLocation",
    "TransitivelyPausedLocation",
    "pre_dispatch_gate_owning_branch_identity",
    "project_pause_locations",
    "walk_pause_tree",
]


class PauseLocationVariant(StrEnum):
    """The FOUR resolution channels a paused location can be addressed through.

    The discriminant is the resolution channel (CP spec v1.112 §2.1); a key field
    exists ONLY on the variants that have one.
    """

    HITL_ADDRESSABLE = "hitl-addressable"
    """Keys `ResumeContext.hitl_responses` by the paused child's own `run_id`."""

    EFFECT_FENCE_ADDRESSABLE = "effect-fence-addressable"
    """Keys `ResumeContext.effect_fence_resolutions` by `idempotency_key`."""

    UNIFORM_FALLBACK_ONLY = "uniform-fallback-only"
    """Gate-owning, ALWAYS unaddressed, resolvable ONLY by the uniform fallback
    when it is the sole member of the unaddressed gate-owning set."""

    TRANSITIVELY_PAUSED = "transitively-paused"
    """Not gate-owning, not counted; position only (CP spec v1.106 §1.2 property 5)."""


class PauseLocationSourceShape(StrEnum):
    """The source carrier a projection was read off — the sub-discriminator that
    makes a per-shape-absent field unrepresentable rather than optional."""

    PAUSED_CHILD_BRANCH = "paused-child-branch"
    EFFECT_FENCE_BRANCH = "effect-fence-branch"
    EFFECT_FENCE_BRANCH_CRASH_RECONSTRUCTION = "effect-fence-branch-crash-reconstruction"
    EFFECT_FENCE_ORCHESTRATOR = "effect-fence-orchestrator"
    EFFECT_FENCE_LINEAR = "effect-fence-linear"
    PRE_DISPATCH_GATE_OWNING_BRANCH = "pre-dispatch-gate-owning-branch"
    DEPTH_ZERO_ROOT_GATE_OWNING = "depth-zero-root-gate-owning"
    CONTAINER_NODE = "container-node"


class _LocationBase(BaseModel):
    """Fields EVERY projection carries (CP spec v1.112 §2.1 "Fields on every variant").

    `pause_reason` is the map-routing discriminator (which map an entry belongs
    in); `step_index` is the workflow position a location gives the operator in
    place of a key. Both declare their CLOSED domain rather than inheriting `str`.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    pause_reason: WorkflowPauseReason
    """The SIX-member `WorkflowPauseReason` domain, including `EFFECT_FENCE_AMBIGUOUS`."""

    step_index: int
    """The paused step's index within its own snapshot's workflow."""


class HitlAddressableLocation(_LocationBase):
    """A paused child branch, addressable through `hitl_responses` by its own `run_id`.

    Source carrier `PausedChildBranchResumeState` declares NO `step_kind`, so this
    variant declares none either (CP spec v1.112 §2.1 field table row 1).
    """

    variant: Literal[PauseLocationVariant.HITL_ADDRESSABLE] = PauseLocationVariant.HITL_ADDRESSABLE
    source_shape: Literal[PauseLocationSourceShape.PAUSED_CHILD_BRANCH] = (
        PauseLocationSourceShape.PAUSED_CHILD_BRANCH
    )
    child_run_id: str
    """The paused child's OWN `run_id` — the `hitl_responses` key (CP v1.106 §1)."""

    step_id: str
    branch_index: int


class BranchEffectFenceAddressableLocation(_LocationBase):
    """A fan-out branch whose dispatch raised the effect fence, carrying a REAL key."""

    variant: Literal[PauseLocationVariant.EFFECT_FENCE_ADDRESSABLE] = (
        PauseLocationVariant.EFFECT_FENCE_ADDRESSABLE
    )
    source_shape: Literal[PauseLocationSourceShape.EFFECT_FENCE_BRANCH] = (
        PauseLocationSourceShape.EFFECT_FENCE_BRANCH
    )
    idempotency_key: str = Field(min_length=1)
    """The held reserve's key — the `effect_fence_resolutions` key. NEVER empty:
    an empty key is the crash-reconstruction source shape, which carries none."""

    step_id: str
    step_kind: StepKind
    branch_index: int


class CrashReconstructionEffectFenceAddressableLocation(_LocationBase):
    """The fan-out CRASH-RECONSTRUCTION fence carrier — key field ABSENT, by type.

    Crash reconstruction constructs `EffectFencePausedBranchResumeState(...,
    idempotency_key="")`; both real resume sites consult a fence resolution only
    when the key is truthy, so surfacing `""` would advertise a key the resolver
    silently IGNORES — the operator's response would be DROPPED, not refused
    (CP spec v1.112 §2.1). This shape therefore declares no key field at all.
    """

    variant: Literal[PauseLocationVariant.EFFECT_FENCE_ADDRESSABLE] = (
        PauseLocationVariant.EFFECT_FENCE_ADDRESSABLE
    )
    source_shape: Literal[PauseLocationSourceShape.EFFECT_FENCE_BRANCH_CRASH_RECONSTRUCTION] = (
        PauseLocationSourceShape.EFFECT_FENCE_BRANCH_CRASH_RECONSTRUCTION
    )
    step_id: str
    step_kind: StepKind
    branch_index: int


class OrchestratorEffectFenceAddressableLocation(_LocationBase):
    """A fan-out ORCHESTRATOR whose own sequential dispatch fence-paused.

    Source carrier `OrchestratorEffectFencePausedResumeState` declares
    `idempotency_key` + `step_id` + `step_kind` and NO `branch_index`.
    """

    variant: Literal[PauseLocationVariant.EFFECT_FENCE_ADDRESSABLE] = (
        PauseLocationVariant.EFFECT_FENCE_ADDRESSABLE
    )
    source_shape: Literal[PauseLocationSourceShape.EFFECT_FENCE_ORCHESTRATOR] = (
        PauseLocationSourceShape.EFFECT_FENCE_ORCHESTRATOR
    )
    idempotency_key: str
    """The held reserve's key.

    **NOT length-constrained, and the residual is REGISTERED rather than absorbed
    (`B-100`).** CP spec v1.112 §2.1 scopes the empty-key key-ABSENT carve-out to
    the fan-out crash-reconstruction carrier — the site the spec leg verified
    constructs `""` deliberately — and tables this orchestrator shape as carrying
    its key. The shipped capture site permits an empty key here too, and both real
    resume sites consult a fence resolution only when the key is TRUTHY, so an
    empty key surfaced here is the same drop-not-refuse hazard one door over.
    Widening the carve-out would add source shapes the cleared enumeration does not
    contain — an X-AL-3 design extension this impl leg must not make silently — so
    the projection conforms to the spec exactly and the gap is filed."""

    step_id: str
    step_kind: StepKind


class LinearEffectFenceAddressableLocation(_LocationBase):
    """The LINEAR effect-fence pause — `EffectFenceResumeState` declares exactly ONE
    field (`idempotency_key`), so this projection carries the key plus the common
    fields and NOTHING else. Not an exception to the per-source-shape rule; that
    rule working (CP spec v1.112 §2.1)."""

    variant: Literal[PauseLocationVariant.EFFECT_FENCE_ADDRESSABLE] = (
        PauseLocationVariant.EFFECT_FENCE_ADDRESSABLE
    )
    source_shape: Literal[PauseLocationSourceShape.EFFECT_FENCE_LINEAR] = (
        PauseLocationSourceShape.EFFECT_FENCE_LINEAR
    )
    idempotency_key: str
    """The held reserve's key. **NOT length-constrained — see
    `OrchestratorEffectFenceAddressableLocation.idempotency_key` for the same
    registered residual (`B-100`).** The shipped LINEAR capture site constructs
    this carrier whenever the runtime error's `idempotency_key` attribute
    `isinstance(_, str)`, which admits `""`."""


class PreDispatchUniformFallbackOnlyLocation(_LocationBase):
    """A branch whose OWN HITL gate fired before any child run was dispatched.

    Gate-owning and counted, but NEVER keyable: its resolver identity is a
    `run_id`-shaped string, so an operator who keyed it would hit the resolver's
    collision defence and have the response silently DROPPED. No identity field is
    declared here at all (CP spec v1.112 §2.2 constraint 2).
    """

    variant: Literal[PauseLocationVariant.UNIFORM_FALLBACK_ONLY] = (
        PauseLocationVariant.UNIFORM_FALLBACK_ONLY
    )
    source_shape: Literal[PauseLocationSourceShape.PRE_DISPATCH_GATE_OWNING_BRANCH] = (
        PauseLocationSourceShape.PRE_DISPATCH_GATE_OWNING_BRANCH
    )
    step_id: str
    step_kind: StepKind
    branch_index: int


class DepthZeroRootUniformFallbackOnlyLocation(_LocationBase):
    """The depth-0 ROOT snapshot's own gate-owning pause — the single most common
    HITL pause shape (a top-level LINEAR / EVALUATOR_OPTIMIZER / DECENTRALIZED_HANDOFF
    workflow that dispatched directly into its own gate).

    Counted, never keyable (*it IS the run*), and required to be served by the
    uniform fallback when sole — this variant's definition precisely. Carries no
    identity field and no `step_kind` (the root snapshot declares neither a
    per-branch step identity nor a step kind).
    """

    variant: Literal[PauseLocationVariant.UNIFORM_FALLBACK_ONLY] = (
        PauseLocationVariant.UNIFORM_FALLBACK_ONLY
    )
    source_shape: Literal[PauseLocationSourceShape.DEPTH_ZERO_ROOT_GATE_OWNING] = (
        PauseLocationSourceShape.DEPTH_ZERO_ROOT_GATE_OWNING
    )


class TransitivelyPausedLocation(_LocationBase):
    """A container node — paused only because something beneath it is. Not
    gate-owning, not counted; position only (CP spec v1.106 §1.2 property 5)."""

    variant: Literal[PauseLocationVariant.TRANSITIVELY_PAUSED] = (
        PauseLocationVariant.TRANSITIVELY_PAUSED
    )
    source_shape: Literal[PauseLocationSourceShape.CONTAINER_NODE] = (
        PauseLocationSourceShape.CONTAINER_NODE
    )


PauseLocationProjection = Annotated[
    HitlAddressableLocation
    | BranchEffectFenceAddressableLocation
    | CrashReconstructionEffectFenceAddressableLocation
    | OrchestratorEffectFenceAddressableLocation
    | LinearEffectFenceAddressableLocation
    | PreDispatchUniformFallbackOnlyLocation
    | DepthZeroRootUniformFallbackOnlyLocation
    | TransitivelyPausedLocation,
    Field(discriminator="source_shape"),
]
"""The CLOSED discriminated union of location projections (four variants across
eight source shapes)."""


class PausedWorkflowState(BaseModel):
    """The root claim a §14.14.9 accessor read returns.

    Residence is CP because the CARRIER at §1 must accept it as a typed field
    (`harness-cp` cannot import `harness-runtime`), and Runtime spec v1.107
    §14.14.9's own "Deferred to implementation discretion" clause leaves "the
    projection types' module residence" open. Runtime composes an instance by
    supplying ONLY the root-level + accessor-minted fields (`workflow_id`,
    `created_at`, `staleness_token`) around CP's ordered `locations` sequence,
    exactly as §14.14.9.3 requires.

    The five-member cause attribution is deliberately NOT a field here: it belongs
    exclusively to the FAILED read, which returns no projection at all.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    workflow_id: str
    """The read's only key."""

    created_at: int
    """The journaled record's capture timestamp, epoch ms — a genuine cross-pause
    discriminator, since `run_id` is REUSED across resume."""

    staleness_token: str = Field(min_length=1)
    """The opaque, accessor-minted staleness token — ONE per read. Its required
    PROPERTY (it MUST differ between any two durably-journaled pause records of
    the same workflow a caller could successively observe) is Runtime-owned at
    `Spec_Harness_Runtime_v1.md` v1.107 §30 term 1; CP only transports it."""

    locations: tuple[PauseLocationProjection, ...]
    """The ORDERED sequence of typed location projections."""


class AccessorDerivedResumeContext(ResumeContext):
    """The accessor-derived `ResumeContext` variant (CP spec v1.112 §1).

    The closed two-variant discrimination is expressed as *the base class is the
    legacy variant, this subclass is the accessor-derived one*:

    1. **REQUIRED, not optional.** `pause_state` has no default, so
       *read-then-omitted is unrepresentable* — a caller cannot hold an accessor
       read and construct THIS variant without carrying the token.
    2. **Legacy preserved byte-identically.** Every existing caller constructs the
       base `ResumeContext` and observes today's behavior exactly.
    3. **Non-downgradable, and mintable only from a projection.** There is no
       downgrade helper and no `.without_token()`; the carriers are frozen; and
       because `ResumeContext` is `extra="forbid"`, re-validating this variant's
       dump into the legacy type is REFUSED rather than silently dropping the
       token. The token is not constructible from a bare string a caller can
       retype — the field's type is the projection object itself.

    **The residual, stated rather than hidden** (CP spec v1.112 §1.2): a caller who
    takes an accessor read and then INDEPENDENTLY constructs a legacy
    `ResumeContext` from scratch is unfenced. No conversion occurs, so no type
    discipline can observe the prior read. Closing that would require deprecating
    the legacy path, a cost this arc explicitly declines to pay.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    pause_state: PausedWorkflowState
    """The §14.14.9 projection these responses were composed against. The projection
    is the sole capability: the token rides it, and cannot be supplied as a bare
    string."""

    @property
    def staleness_token(self) -> str:
        """The read's staleness token, transported opaquely for Runtime's §30 fence."""
        return self.pause_state.staleness_token

    @classmethod
    def from_pause_state(
        cls,
        pause_state: PausedWorkflowState,
        *,
        hitl_response: HITLResult | None = None,
        hitl_responses: dict[str, HITLResult] | None = None,
        effect_fence_resolution: EffectFenceResolution | None = None,
        effect_fence_resolutions: dict[str, EffectFenceResolution] | None = None,
    ) -> Self:
        """Compose responses against a specific accessor read.

        The ONLY intended construction path. Every response field — the MAP fields
        AND the SCALAR fields alike — is bound to `pause_state`'s token by the act
        of composing here (CP spec v1.112 §1.1: a `uniform-fallback-only` location
        is answered by the SCALAR field, and that path is the arc's PRIMARY witness).
        """
        return cls(
            pause_state=pause_state,
            hitl_response=hitl_response,
            hitl_responses=hitl_responses,
            effect_fence_resolution=effect_fence_resolution,
            effect_fence_resolutions=effect_fence_resolutions,
        )


def pre_dispatch_gate_owning_branch_identity(snapshot_run_id: str, branch_index: int) -> str:
    """Tree-wide-unique internal identity for a pre-dispatch gate-owning branch.

    B-72 impl leg (CP spec v1.108 §1.1(d)) — a pre-dispatch gate-owning branch has
    no child `run_id` to identify it (property 6 §1.1(b) forbids ever keying it into
    `hitl_responses`), so the resolver needs an impl-discretion internal identity for
    property 4's counting + SOLE-member comparison. Composing the CONTAINING
    `PauseSnapshot`'s own `run_id` (already tree-wide-unique by construction — every
    recursion level's snapshot carries the run_id of the distinct sub-workflow run
    that captured it) with the local branch ordinal is sufficient: two pre-dispatch
    gate-owning branches at different tree positions are, by definition, captured
    under snapshots with distinct `run_id`s, so their composed identities can never
    collide even when the LOCAL ordinal happens to match (the nested-fan-out
    collision codex's [P1] review named). Never placed in, or compatible with,
    `hitl_responses` (which stays exclusively `child_run_id`-keyed per property 1).

    **Relocated (not redefined) at the `B-69` impl leg** from `workflow_driver` into
    this module so the single shared traversal can compose it without importing the
    driver. `workflow_driver` re-imports it under its original private name; the
    composition is byte-identical.
    """
    return f"{snapshot_run_id}:pre-dispatch-gate:{branch_index}"


class PauseTreeWalkEntry(NamedTuple):
    """One visited location: its PUBLIC projection plus the RESOLVER-ONLY identity.

    The split is the whole point. The projection is what crosses the caller-facing
    boundary and therefore declares no never-keyable identity; the resolver
    identity is what `compute_hitl_uniform_fallback_eligible_run_id` /
    `compute_effect_fence_uniform_fallback_eligible_key` count and compare, and it
    never leaves CP.
    """

    projection: PauseLocationProjection
    gate_owning_identity: str | None
    """The gate-owning identity the HITL resolver counts (a child `run_id`, the
    depth-0 root's own `run_id`, or a composed pre-dispatch identity) — `None` for
    a location that is not gate-owning."""

    effect_fence_key: str | None
    """The effect-fence key the fence resolver enumerates — `""` for the
    crash-reconstruction shape (whose projection carries NO key), `None` for a
    location that is not an effect-fence pause."""


def walk_pause_tree(root_snapshot: PauseSnapshot) -> tuple[PauseTreeWalkEntry, ...]:
    """THE single traversal of the resume tree (CP spec v1.112 §2.3 / plan AC #A8).

    Every CP consumer of resume-tree structure — the HITL uniform-fallback
    resolver, the effect-fence uniform-fallback resolver, the never-keyable
    pre-dispatch identity set, and the public projection — is a FILTER over this
    one walk. No second recursion over `PauseSnapshot` exists for any of them, so a
    third classification authority cannot ship and pass on every finite tested tree.

    Emission order per node is chosen so each filtered view reproduces the order
    its pre-`B-69` walk produced, byte-for-byte:

    1. the node's own LINEAR fence carrier;
    2. the node's own ORCHESTRATOR fence carrier;
    3. if the node has no fan-out carrier: its own gate-owning leaf projection
       (depth-0 root shape at the root, HITL-addressable beneath it) when its
       `pause_reason` is `HITL_PENDING`;
    4. otherwise: the container projection, then its pre-dispatch gate-owning
       branches, then its effect-fence-paused branches, then the recursion into
       its paused child branches.
    """
    return tuple(_walk(root_snapshot, child_position=None))


class _ChildPosition(NamedTuple):
    """The `PausedChildBranchResumeState` position a nested snapshot hangs off.

    `None` at the depth-0 root — which is exactly the depth discriminator
    `_gate_owning_leaf_entry` keys on, so the two facts cannot drift apart.
    """

    step_id: str
    branch_index: int


def _walk(
    snapshot: PauseSnapshot, *, child_position: _ChildPosition | None
) -> list[PauseTreeWalkEntry]:
    entries: list[PauseTreeWalkEntry] = []
    # `snapshot.pause_reason` is the NODE's aggregate label, and a mixed pause can
    # carry several locations of different kinds beneath one node — a container
    # whose reason is `EFFECT_FENCE_AMBIGUOUS` may hold a pre-dispatch HITL branch,
    # and B-32's own capture sites INFORMATIONALLY relabel a container to
    # `HITL_PENDING`. Since CP v1.112 §2.1 makes `pause_reason` the MAP-ROUTING
    # discriminator — what tells the operator which map an entry belongs in —
    # stamping the aggregate onto every location would misroute exactly the way
    # property 4 exists to prevent. Each location's reason is therefore derived
    # from ITS OWN SOURCE CARRIER, which determines it by construction: an
    # effect-fence carrier IS `EFFECT_FENCE_AMBIGUOUS`; a gate-owning HITL carrier
    # IS `HITL_PENDING`. Only the container node keeps the node's own aggregate,
    # which is the one place that label is truthful.
    # *(Out-of-family review [P2] at the impl leg; no classification RULE is added
    # here — the variant is unchanged, only the label is read off the right thing.)*
    reason = snapshot.pause_reason
    step_index = snapshot.step_index

    if snapshot.effect_fence_resume is not None:
        entries.append(
            PauseTreeWalkEntry(
                projection=LinearEffectFenceAddressableLocation(
                    pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
                    step_index=step_index,
                    idempotency_key=snapshot.effect_fence_resume.idempotency_key,
                ),
                gate_owning_identity=None,
                effect_fence_key=snapshot.effect_fence_resume.idempotency_key,
            )
        )
    if snapshot.orchestrator_effect_fence_resume is not None:
        _orch = snapshot.orchestrator_effect_fence_resume
        entries.append(
            PauseTreeWalkEntry(
                projection=OrchestratorEffectFenceAddressableLocation(
                    pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
                    step_index=step_index,
                    idempotency_key=_orch.idempotency_key,
                    step_id=_orch.step_id,
                    step_kind=StepKind(_orch.step_kind),
                ),
                gate_owning_identity=None,
                effect_fence_key=_orch.idempotency_key,
            )
        )

    resume_state = snapshot.fan_out_resume or snapshot.peer_fan_out_resume
    if resume_state is None:
        if reason is WorkflowPauseReason.HITL_PENDING:
            entries.append(_gate_owning_leaf_entry(snapshot, child_position=child_position))
        return entries

    entries.append(
        PauseTreeWalkEntry(
            projection=TransitivelyPausedLocation(pause_reason=reason, step_index=step_index),
            gate_owning_identity=None,
            effect_fence_key=None,
        )
    )
    for _row in resume_state.pre_dispatch_gate_owning_branches:
        entries.append(
            PauseTreeWalkEntry(
                projection=PreDispatchUniformFallbackOnlyLocation(
                    pause_reason=WorkflowPauseReason.HITL_PENDING,
                    step_index=step_index,
                    step_id=_row.step_id,
                    step_kind=StepKind(_row.step_kind),
                    branch_index=_row.branch_index,
                ),
                gate_owning_identity=pre_dispatch_gate_owning_branch_identity(
                    snapshot.run_id, _row.branch_index
                ),
                effect_fence_key=None,
            )
        )
    for _fence in resume_state.effect_fence_paused_branches:
        entries.append(
            PauseTreeWalkEntry(
                projection=_effect_fence_branch_projection(
                    reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
                    step_index=step_index,
                    step_id=_fence.step_id,
                    step_kind=StepKind(_fence.step_kind),
                    branch_index=_fence.branch_index,
                    idempotency_key=_fence.idempotency_key,
                ),
                gate_owning_identity=None,
                effect_fence_key=_fence.idempotency_key,
            )
        )
    for paused_child in resume_state.paused_child_branches:
        entries.extend(
            _walk(
                paused_child.child_snapshot,
                child_position=_ChildPosition(
                    step_id=paused_child.step_id, branch_index=paused_child.branch_index
                ),
            )
        )
    return entries


def _gate_owning_leaf_entry(
    snapshot: PauseSnapshot, *, child_position: _ChildPosition | None
) -> PauseTreeWalkEntry:
    """A gate-owning LEAF: the depth-0 root's own pause, or a paused child branch.

    The discriminator is depth, exactly as the shipped resolver reads it: a depth-0
    pause has no child `run_id` to key by — *it IS the run* — so it is
    uniform-fallback-only, while the same shape one level down IS the paused child
    the `hitl_responses` map addresses, keyed by that child's own `run_id`.
    """
    if child_position is None:
        return PauseTreeWalkEntry(
            projection=DepthZeroRootUniformFallbackOnlyLocation(
                pause_reason=snapshot.pause_reason, step_index=snapshot.step_index
            ),
            gate_owning_identity=snapshot.run_id,
            effect_fence_key=None,
        )
    return PauseTreeWalkEntry(
        projection=HitlAddressableLocation(
            pause_reason=snapshot.pause_reason,
            step_index=snapshot.step_index,
            child_run_id=snapshot.run_id,
            step_id=child_position.step_id,
            branch_index=child_position.branch_index,
        ),
        gate_owning_identity=snapshot.run_id,
        effect_fence_key=None,
    )


def _effect_fence_branch_projection(
    *,
    reason: WorkflowPauseReason,
    step_index: int,
    step_id: str,
    step_kind: StepKind,
    branch_index: int,
    idempotency_key: str,
) -> PauseLocationProjection:
    """Route an `EffectFencePausedBranchResumeState` to its own SOURCE SHAPE.

    An EMPTY key is the crash-reconstruction shape, whose projection carries no key
    field at all — never a `""` key value both resume sites would silently ignore.
    """
    if idempotency_key:
        return BranchEffectFenceAddressableLocation(
            pause_reason=reason,
            step_index=step_index,
            idempotency_key=idempotency_key,
            step_id=step_id,
            step_kind=step_kind,
            branch_index=branch_index,
        )
    return CrashReconstructionEffectFenceAddressableLocation(
        pause_reason=reason,
        step_index=step_index,
        step_id=step_id,
        step_kind=step_kind,
        branch_index=branch_index,
    )


def project_pause_locations(root_snapshot: PauseSnapshot) -> tuple[PauseLocationProjection, ...]:
    """The PUBLIC projection surface (CP spec v1.112 §2.1).

    An ORDERED SEQUENCE of TYPED LOCATION PROJECTIONS over the resume tree of the
    supplied pause snapshot — the same computation the uniform-fallback resolvers
    consume, exposed as structure rather than re-derived by the caller. Bare
    identifier sets are FORBIDDEN as the return shape: they cannot populate
    position, step, reason and addressability per location without the caller
    re-walking, and they would carry the one value that must not cross this
    boundary.
    """
    return tuple(entry.projection for entry in walk_pause_tree(root_snapshot))
