"""Workload-binding-time engine-class selection — U-CP-17 (PARTIAL).

Implements C-CP-07 §7.3 — the workload-binding-time engine-class selection
contract. Declares `WorkloadBindingSelectionInput`,
`WorkloadBindingSelectionResult`, and `select_engine_class`.

**PARTIAL LAND — halt-route-split-AC.** The v2.1 U-CP-17 signature carries an
`operator_preferences: Optional<EngineClassPreferences>` field, and acceptance
criterion #1 step 4 ("apply operator preferences if declared"). `Engine-
ClassPreferences` is a record homed at U-CP-27 (`Implementation_Plan_Control_
Plane_v2_6.md` L221/L584) — a blocked deferred-consumer unit. The field and
step 4 are STRUCK at this landing per `.harness/class_1_tension_u_cp_17_engine_
class_preferences_homing.md`; the §7.3 procedure lands as a 4-step procedure
(resolve candidates / workload-class filter / persona-tier filter / return).
Step 4 + the `operator_preferences` field are re-landed at the U-CP-27 landing.

The selection is deterministic given inputs (acceptance #2) and runs at
**workload-binding time** — a binding-time contract, not a runtime path
(acceptance #3); a selection that yields no candidate is a binding failure that
aborts workflow binding.

Authority: Implementation_Plan_Control_Plane_v2_1.md §2 U-CP-17 (preserved
verbatim through v2.6; `[U-CP-00]` + `[U-CORE-01]` edge-adds per v2.5/v2.6 §0.10
— `WorkloadClass`/`DeploymentSurface`/`PersonaTier` resolved from carriers);
Spec_Control_Plane_v1_2.md §7 C-CP-07 §7.3 (preserved verbatim into v1.3);
ADR-D1 v1.1 + ADR-D4 v1.1.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from harness_core import DeploymentSurface, PersonaTier, WorkloadClass
from harness_cp.engine_class import EngineClass
from harness_cp.engine_class_candidate import ENGINE_CLASS_CANDIDATES


class WorkloadBindingSelectionInput(BaseModel):
    """The inputs to the §7.3 five-step engine-class selection procedure.

    The v2.1 signature additionally declared `operator_preferences:
    Optional<EngineClassPreferences>`; that field is STRUCK at this partial
    landing (its type is homed at the blocked unit U-CP-27). It is re-added at
    the U-CP-27 landing per the Class 1 tension record.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    workload_class: WorkloadClass
    """The §7.3 step-2 workload class — operator-declared at binding time."""

    deployment_surface: DeploymentSurface
    """The §7.3 step-1 deployment surface — operator-declared at binding time;
    keys the U-CP-16 candidate-set lookup."""

    persona_tier: PersonaTier
    """The §7.3 step-3 persona tier — keys the durability-primitive filter."""


class WorkloadBindingSelectionResult(BaseModel):
    """The result of the §7.3 engine-class selection procedure."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    selected_class: EngineClass
    """The single engine class bound at the workflow manifest."""

    candidate_set: frozenset[EngineClass]
    """The §7.2 candidate set the selection ran against (post step-1)."""

    selection_rationale: str
    """Documents the winning filter — which §7.3 step bound the result."""


class WorkloadBindingError(ValueError):
    """A §7.3 selection that yields no admissible engine class.

    Per acceptance #3, a binding-time validation failure aborts workflow
    binding — it is not a recoverable runtime path.
    """


# --- §7.3 step-2: workload-class admissibility favoring -------------------
#
# Per §7.3 step 2: event-sourced-replay favored at pipeline-automation;
# save-point-checkpoint favored at software-engineering; reconciler-loop
# favored at content-creation when reconvergence required. The favored class
# is selected when present in the candidate set; otherwise the filter is a
# no-op and the procedure falls through to the persona-tier filter.
_WORKLOAD_CLASS_FAVORED: dict[WorkloadClass, EngineClass] = {
    WorkloadClass.PIPELINE_AUTOMATION: EngineClass.EVENT_SOURCED_REPLAY,
    WorkloadClass.SOFTWARE_ENGINEERING: EngineClass.SAVE_POINT_CHECKPOINT,
    WorkloadClass.CONTENT_CREATION: EngineClass.RECONCILER_LOOP,
}
"""The §7.3 step-2 per-workload-class favored engine class. `RESEARCH` has no
§7.3-named favoring — it falls through to the persona-tier filter."""

# --- §7.3 step-3: persona-tier durability filter --------------------------
#
# Per §7.3 step 3: solo-developer admits pure-pattern-no-engine; team-binding
# and multi-tenant-compliance require a durability primitive (every class
# except pure-pattern-no-engine).
_PURE_PATTERN: EngineClass = EngineClass.PURE_PATTERN_NO_ENGINE


def _candidate_set_for(surface: DeploymentSurface) -> frozenset[EngineClass]:
    """§7.3 step 1 — resolve the U-CP-16 candidate set for `surface`."""
    for candidate in ENGINE_CLASS_CANDIDATES:
        if candidate.deployment_surface == surface:
            return candidate.candidate_set
    # ENGINE_CLASS_CANDIDATES has one entry per DeploymentSurface (U-CP-16
    # acceptance #1) — this is unreachable for a valid enum member.
    raise WorkloadBindingError(
        f"no §7.2 candidate set for deployment surface {surface!r}"
    )


def _persona_tier_admits(
    persona_tier: PersonaTier, engine_class: EngineClass
) -> bool:
    """§7.3 step 3 — whether `persona_tier` admits `engine_class`.

    `pure-pattern-no-engine` is admitted only at `solo-developer`; every other
    engine class carries a durability primitive and is admitted at all tiers.
    """
    if engine_class is _PURE_PATTERN:
        return persona_tier is PersonaTier.SOLO_DEVELOPER
    return True


def select_engine_class(
    input: WorkloadBindingSelectionInput,
) -> WorkloadBindingSelectionResult:
    """Run the C-CP-07 §7.3 workload-binding-time selection procedure.

    PARTIAL — the §7.3 five-step procedure lands here as four steps; the
    operator-preference step (v2.1 step 4) is struck per the U-CP-17 Class 1
    tension record (`EngineClassPreferences` homed at blocked U-CP-27).

    - Step 1: resolve the candidate set from U-CP-16 per `deployment_surface`.
    - Step 2: filter candidates by `workload_class` admissibility.
    - Step 3: filter candidates by `persona_tier` durability requirement.
    - Step 4 (was step 5): return the single selected class; the rationale
      documents the winning filter.

    Deterministic given inputs — no inference path (acceptance #2). A selection
    that yields no admissible class raises `WorkloadBindingError` — a
    binding-time abort (acceptance #3).
    """
    # Step 1 — resolve candidate set per deployment surface.
    candidate_set = _candidate_set_for(input.deployment_surface)

    # Step 3 (applied first as a filter) — restrict to persona-tier-admissible
    # candidates. Determinism: a pure set intersection, no ordering dependence.
    tier_admissible = frozenset(
        ec
        for ec in candidate_set
        if _persona_tier_admits(input.persona_tier, ec)
    )
    if not tier_admissible:
        raise WorkloadBindingError(
            f"persona tier {input.persona_tier!r} admits no engine class in "
            f"the {input.deployment_surface!r} candidate set"
        )

    # Step 2 — workload-class favoring. If the §7.3-favored class for this
    # workload class is persona-tier-admissible, it wins; the rationale names
    # the favoring. Otherwise fall through to step 4 deterministic selection.
    favored = _WORKLOAD_CLASS_FAVORED.get(input.workload_class)
    if favored is not None and favored in tier_admissible:
        return WorkloadBindingSelectionResult(
            selected_class=favored,
            candidate_set=candidate_set,
            selection_rationale=(
                f"§7.3 step 2 — {input.workload_class.value} favors "
                f"{favored.value}; admissible at persona tier "
                f"{input.persona_tier.value}."
            ),
        )

    # Step 4 — return a single class deterministically. With no §7.3-favored
    # class admissible, the binding selects the persona-tier-admissible
    # candidate with the lowest enum-member name (a total, input-independent
    # order — determinism per acceptance #2).
    selected = min(tier_admissible, key=lambda ec: ec.name)
    return WorkloadBindingSelectionResult(
        selected_class=selected,
        candidate_set=candidate_set,
        selection_rationale=(
            f"§7.3 step 3 — no workload-class-favored class admissible for "
            f"{input.workload_class.value} at persona tier "
            f"{input.persona_tier.value}; deterministic selection of "
            f"{selected.value} from the tier-admissible candidate set."
        ),
    )
