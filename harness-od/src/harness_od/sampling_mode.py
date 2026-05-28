"""Per-deployment-surface sampling mode + 18-entry always-sampled set — U-OD-11.

Implements C-OD-09 §9.1 (per-deployment-surface sampling mode), §9.2
(always-sampled exception set — head=1.0 across all cells), and §9.3
(sampling-discipline invariants).

`SamplingMode` enumerates the two per-deployment-surface modes;
`PER_DEPLOYMENT_SURFACE_SAMPLING` maps each `DeploymentSurface` to its mode.
`ALWAYS_SAMPLED_EVENT_CLASSES` carries the §9.2 18-entry always-sampled set
(head=1.0 across all cells, inviolable per §9.3). `sampling_decision` returns
`SAMPLE_ALWAYS` for any event in the always-sampled set, `SAMPLE_AT_BASE_RATE`
otherwise.

Authority: Implementation_Plan_Operational_Discipline_v2_5.md §3.4.1 U-OD-11
(v2.5 conformance revision — `ALWAYS_SAMPLED_EVENT_CLASSES` member set + acc #3
conformed to OD spec §9.2; all other surfaces preserved verbatim from v2.1
§3.4.1); Spec_Operational_Discipline_v1_2.md §9 C-OD-09 §9.1 + §9.2 + §9.3
(preserved verbatim into v1.3 per v1.3 §0.1); ADR-D6 v1.1 §1.3 sampling
discipline.

`SamplingDecision` is declared in-unit: the spec §9.3 / acc #6 commit the two
sampling-regime outcomes (`SAMPLE_ALWAYS` / `SAMPLE_AT_BASE_RATE`) without
naming a carrier type; per R5 materializability disposition U-OD-11 declares it
in-unit (single-consumer; no carrier unit).

Depends on: [U-OD-04, U-OD-05, U-OD-06, U-OD-09]. The U-OD-09 edge is the
event-class-string informational dependency only — `"breaker.tripped"` enters
`ALWAYS_SAMPLED_EVENT_CLASSES` as a string literal per §9.2; U-OD-11 imports no
typed surface from U-OD-09's `harness.breaker.*` schema, so the U-OD-09 Class 1
halt does not block U-OD-11.
"""

from __future__ import annotations

from enum import StrEnum

from harness_core import DeploymentSurface
from pydantic import BaseModel, ConfigDict

from harness_od.observability_matrix import CellID

__all__ = [
    "ALWAYS_SAMPLED_EVENT_CLASSES",
    "PER_DEPLOYMENT_SURFACE_SAMPLING",
    "PerDeploymentSurfaceSamplingMode",
    "SamplingDecision",
    "SamplingMode",
    "is_always_sampled",
    "sampling_decision",
]


class SamplingMode(StrEnum):
    """Per-deployment-surface sampling mode (C-OD-09 §9.1) — exactly 2 values.

    `HEAD_BASED_DEV` — sampling decision at span creation; local-development
    cells; head=1.0. `TAIL_BASED_PROD` — sampling decision at trace completion;
    self-hosted-server + managed-cloud cells.
    """

    HEAD_BASED_DEV = "HEAD_BASED_DEV"
    TAIL_BASED_PROD = "TAIL_BASED_PROD"


class SamplingDecision(StrEnum):
    """Sampling-regime outcome for a single event (C-OD-09 §9.3 / acc #6).

    `SAMPLE_ALWAYS` — event is in `ALWAYS_SAMPLED_EVENT_CLASSES`; samples at
    head=1.0 regardless of cell base-rate. `SAMPLE_AT_BASE_RATE` — event falls
    to the C-OD-10 base-rate regime.
    """

    SAMPLE_ALWAYS = "SAMPLE_ALWAYS"
    SAMPLE_AT_BASE_RATE = "SAMPLE_AT_BASE_RATE"


class PerDeploymentSurfaceSamplingMode(BaseModel):
    """A `(deployment_surface, sampling_mode)` pair (C-OD-09 §9.1)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    deployment_surface: DeploymentSurface
    sampling_mode: SamplingMode


# --- §9.1 per-deployment-surface sampling mode -----------------------------

#: §9.1 verbatim — local-development is head-based; self-hosted-server and
#: managed-cloud are tail-based.
PER_DEPLOYMENT_SURFACE_SAMPLING: dict[DeploymentSurface, SamplingMode] = {
    DeploymentSurface.LOCAL_DEVELOPMENT: SamplingMode.HEAD_BASED_DEV,
    DeploymentSurface.SELF_HOSTED_SERVER: SamplingMode.TAIL_BASED_PROD,
    DeploymentSurface.MANAGED_CLOUD: SamplingMode.TAIL_BASED_PROD,
}


# --- §9.2 always-sampled exception set (head=1.0 across all cells) ---------

#: §9.2 verbatim — the always-sampled exception set. Member set conformed to
#: the §9.2 table (18 rows). Inviolable per §9.3: a hard floor at the
#: deployment-binding layer, not operator-tunable at base-rate.
ALWAYS_SAMPLED_EVENT_CLASSES: frozenset[str] = frozenset(
    {
        "sandbox.violation",
        "sandbox.tier_escalation",
        "hitl.gate.evaluated",
        "hitl.invocation.opened",
        "hitl.invocation.responded",
        "hitl.invocation.timed_out",
        "fallback.triggered",
        "breaker.tripped",
        "topology.fanout.opened",
        "topology.fanout.closed",
        "subagent.span",  # §9.2 row "subagent.span (root)"
        "mcp.tool.call",
        "audit.*",  # §9.2 row "audit.* (any event with audit.signature.* attributes)"
        "files.operation",  # §9.2 row "files.operation at kind in {upload, delete}"
        "memory.operation",  # §9.2 row "memory.operation at kind in {write, update, delete}"
        "validator.fail.*",  # §9.2 row "validator.fail.* at validator.fail.permanence=permanent"
        "managed_agents.runtime",
        "skill.activation",
    }
)  # exactly 18 entries per §9.2


# --- §9.2 always-sampled lookup at SDK boundary ----------------------------
#
# `ALWAYS_SAMPLED_EVENT_CLASSES` above declares the §9.2 18-entry set
# verbatim per spec fidelity-grammar, including two wildcard entries
# (`audit.*` and `validator.fail.*`). At the SDK boundary the sampler
# receives concrete span names (`"audit.signature.write"`,
# `"validator.fail.semantic_inconsistency"`) — set-membership lookup
# against the literal `"audit.*"` would under-sample. `is_always_sampled`
# decomposes the set into literals + dot-anchored prefixes derived once at
# module load and resolves the §9.2 contract at concrete span names.

_ALWAYS_SAMPLED_LITERALS: frozenset[str] = frozenset(
    {entry for entry in ALWAYS_SAMPLED_EVENT_CLASSES if not entry.endswith(".*")}
)
#: Dot-anchored prefixes derived from `*.*` entries in the canonical set.
#: An incoming span name `"audit.signature.write"` matches the `"audit."`
#: prefix; `"audit"` alone does NOT (dot anchor forecloses spurious matches).
_ALWAYS_SAMPLED_PREFIXES: tuple[str, ...] = tuple(
    sorted(
        entry[:-1]  # strip trailing `*`; keep the dot anchor
        for entry in ALWAYS_SAMPLED_EVENT_CLASSES
        if entry.endswith(".*")
    )
)


def is_always_sampled(event_name: str) -> bool:
    """Return True iff `event_name` matches §9.2 always-sampled discipline.

    Resolves both literal entries (e.g. `sandbox.violation`) and dot-anchored
    prefix entries (e.g. `audit.*` matches `audit.signature.write` AND
    `audit.cp.dispatch`; `audit` alone does NOT match).
    """
    if event_name in _ALWAYS_SAMPLED_LITERALS:
        return True
    return any(event_name.startswith(prefix) for prefix in _ALWAYS_SAMPLED_PREFIXES)


def sampling_decision(
    cell_id: CellID,
    event_class: str,
    base_rate: float,
) -> SamplingDecision:
    """Return the sampling regime for `event_class` (C-OD-09 §9.2 / §9.3, acc #6).

    Returns `SAMPLE_ALWAYS` for any event in the §9.2 always-sampled set
    (literal entries OR dot-anchored prefix entries — see `is_always_sampled`);
    returns `SAMPLE_AT_BASE_RATE` otherwise. The always-sampled set is
    independent of base-rate sampling (acc #4): events in the set sample at
    head=1.0 at every cell.

    `cell_id` and `base_rate` are accepted per the U-OD-11 signature; the
    always-sampled decision is uniform across all cells (§9.3 per-cell
    sampling-refinement invariant — within the always-sampled set per-cell
    sampling is uniform). They carry no branch in this function and are the
    composition substrate for the C-OD-10 base-rate regime.
    """
    del cell_id, base_rate  # uniform across cells per §9.3; no branch here
    if is_always_sampled(event_class):
        return SamplingDecision.SAMPLE_ALWAYS
    return SamplingDecision.SAMPLE_AT_BASE_RATE
