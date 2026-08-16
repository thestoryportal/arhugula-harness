"""Per-deployment-surface sampling mode + 20-entry always-sampled set — U-OD-11.

Implements C-OD-09 §9.1 (per-deployment-surface sampling mode), §9.2
(always-sampled exception set — head=1.0 across all cells), and §9.3
(sampling-discipline invariants).

`SamplingMode` enumerates the two per-deployment-surface modes;
`PER_DEPLOYMENT_SURFACE_SAMPLING` maps each `DeploymentSurface` to its mode.
`ALWAYS_SAMPLED_EVENT_CLASSES` carries the §9.2 20-entry always-sampled set
(head=1.0 across all cells, inviolable per §9.3). `sampling_decision` returns
`SAMPLE_ALWAYS` for any event in the always-sampled set, `SAMPLE_AT_BASE_RATE`
otherwise.

`is_always_sampled(event_name, attributes=None)` honors the four §9.2
*conditional* rows (B7 over-sampling refinement): `files.operation` /
`memory.operation` always-sample only at mutation `kind`, `validator.fail.*`
only at `permanence=permanent` (the non-mutation / transient complements fall
to the §10.1 base-rate regime); `subagent.span` is root-conditional, delivered
by the `ParentBased` composition (see `composite_sampler`). The decision is
conservative-absent (a missing discriminating attribute always-samples — never
under-sample the §9.3 floor); `attributes` defaults to `None`, so the name-only
callers (`sampling_decision`) are byte-identical to the pre-B7 behavior.

Authority: Implementation_Plan_Operational_Discipline_v2_5.md §3.4.1 U-OD-11
(v2.5 conformance revision — `ALWAYS_SAMPLED_EVENT_CLASSES` member set + acc #3
conformed to OD spec §9.2; all other surfaces preserved verbatim from v2.1
§3.4.1); Spec_Operational_Discipline_v1_2.md §9 C-OD-09 §9.1 + §9.2 + §9.3
(preserved verbatim into v1.3 per v1.3 §0.1); ADR-D6 v1.1 §1.3 sampling
discipline. The §9.2 table's NINETEENTH row (`fallback.exhausted`) is the
`B-116-t3` leg: `Spec_Operational_Discipline_v1_37.md` §1 amends §9.2 18 → 19 on
the CP-declares/OD-ingests chain (`Spec_Control_Plane_v1_2.md:410` declares it
always-sampled; the row was dropped at original OD ingestion while its two
siblings at CP `:409`/`:411` were absorbed at OD `:521`/`:522`), carried at
`Implementation_Plan_Operational_Discipline_v2_32.md` U-OD-58.

The TWENTIETH row (`workflow.envelope`) is the `B-137` step-(3) candidate **C1**
leg, operator-ratified 2026-08-16: `Spec_Operational_Discipline_v1_42.md` §0.2
amends §9.2 19 → 20 on an INTRA-axis declares/ingests chain — C-OD-25 §25.1
(`Spec_Operational_Discipline_v1_8.md:90`) has declared *"the envelope ALWAYS
persists"* at head=1.0 since v1.8 and §9.2 never absorbed it. Root membership is
also the only mechanism that delivers the §9.2 floor to in-envelope member
SPANS: the shipped head is `ParentBased(root=HarnessCompositeSampler)`, which
consults the inner sampler only for roots, so before this row an ordinary
envelope root took every in-envelope member down with its own base-rate draw.

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
from opentelemetry.util.types import Attributes
from pydantic import BaseModel, ConfigDict

from harness_od.observability_matrix import CellID
from harness_od.tail_keep_classification import (
    VALIDATOR_FAIL_PERMANENCE_ATTR,
    VALIDATOR_FAIL_PERMANENCE_PERMANENT_VALUE,
)

__all__ = [
    "ALWAYS_SAMPLED_EVENT_CLASSES",
    "FILES_OPERATION_KIND_ATTR",
    "MEMORY_OPERATION_KIND_ATTR",
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
#: the §9.2 table (20 rows). Inviolable per §9.3: a hard floor at the
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
        "fallback.exhausted",  # §9.2 row 19 (NEW at OD spec v1.37 — U-OD-58)
        # §9.2 row 20 (NEW at OD spec v1.42 — `B-137` step (3) candidate C1,
        # operator-ratified 2026-08-16). Ingests the C-OD-25 §25.1 head=1.0
        # declaration; ALSO the carrier of the floor for in-envelope member
        # spans, which `ParentBased` reaches only by root inheritance.
        "workflow.envelope",
    }
)  # exactly 20 entries per §9.2


# --- §9.2 always-sampled lookup at SDK boundary ----------------------------
#
# `ALWAYS_SAMPLED_EVENT_CLASSES` above declares the §9.2 20-entry set
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


# --- §9.2 conditional-by-attribute rows (B7 over-sampling refinement) -------
#
# Four §9.2 rows are conditional, not name-only:
#   - `files.operation`   always-sampled only at kind ∈ {upload, delete}
#   - `memory.operation`  always-sampled only at kind ∈ {write, update, delete}
#   - `validator.fail.*`  always-sampled only at permanence=permanent
#   - `subagent.span`     always-sampled only at the root
#
# The first three resolve by a span attribute (resolved here); the fourth
# resolves by trace structure (root-ness) and is delivered by the canonical
# `ParentBased(root=HarnessCompositeSampler)` composition — the inner sampler is
# consulted ONLY for root spans, so a `subagent.span` reaching it is root by
# construction. `subagent.span` therefore stays an unconditional literal in
# `ALWAYS_SAMPLED_EVENT_CLASSES`; only the three attribute-conditional rows are
# resolved by `_conditional_always_sampled`.
#
# The non-mutation / transient complements fall to the C-OD-10 §10.1 base-rate
# regime (`files.operation` at {list, metadata, reference}; `memory.operation`
# at {read, list}). The OD mutation kind-sets are declared here against the
# §9.2 / §10.1 spec rows — OD is consumer-most-downstream and does NOT import
# the runtime producer enums `FilesOperationKind` (`files_api.py`) /
# `_HEAD_SAMPLED_KINDS` (`memory_tool_dispatch.py`); those are the emission-side
# mirrors of these spec-fixed sets.
#
# CONSERVATIVE-ABSENT: when the discriminating attribute is absent the decision
# is always-sample — never under-sample the §9.3 inviolable floor. The runtime
# producers set `files.operation.kind` / `memory.operation.kind` AFTER span
# creation, so a HEAD sampler reading `attributes` at span-creation time sees
# None and conservatively samples (see the `composite_sampler` enforcement-
# boundary note: head-sampler §9.2-conditional refinement is bounded to root
# spans carrying the attribute at creation; full non-root / production-tail
# enforcement is the tail-keep concern gated on R-420/R-421).

#: §9.2 / §10.1 span attribute carrying the Files API operation kind.
FILES_OPERATION_KIND_ATTR: str = "files.operation.kind"
#: §9.2 / §10.1 span attribute carrying the Memory tool operation kind.
MEMORY_OPERATION_KIND_ATTR: str = "memory.operation.kind"

#: §9.2 — `files.operation` always-sampled at these kinds (§10.1 base-rate at
#: the {list, metadata, reference} complement).
_FILES_MUTATION_KINDS: frozenset[str] = frozenset({"upload", "delete"})
#: §9.2 — `memory.operation` always-sampled at these kinds (§10.1 base-rate at
#: the {read, list} complement).
_MEMORY_MUTATION_KINDS: frozenset[str] = frozenset({"write", "update", "delete"})

#: §9.2 — `validator.fail.*` dot-anchored span-name prefix (mirrors the
#: `validator.fail.*` entry's derived prefix in `_ALWAYS_SAMPLED_PREFIXES`).
_VALIDATOR_FAIL_PREFIX: str = "validator.fail."


def _conditional_always_sampled(event_name: str, attributes: Attributes) -> bool | None:
    """Resolve the §9.2 conditional-by-attribute decision for the three
    attribute-conditional rows, or `None` if `event_name` is not one of them
    (the caller then falls through to the name-only literal / prefix match).

    Conservative-absent: a missing discriminating attribute returns `True`
    (always-sample) — never under-sample the §9.3 inviolable floor.
    """
    if event_name == "files.operation":
        kind = attributes.get(FILES_OPERATION_KIND_ATTR) if attributes else None
        return kind is None or kind in _FILES_MUTATION_KINDS
    if event_name == "memory.operation":
        kind = attributes.get(MEMORY_OPERATION_KIND_ATTR) if attributes else None
        return kind is None or kind in _MEMORY_MUTATION_KINDS
    if event_name.startswith(_VALIDATOR_FAIL_PREFIX):
        permanence = attributes.get(VALIDATOR_FAIL_PERMANENCE_ATTR) if attributes else None
        return permanence is None or permanence == VALIDATOR_FAIL_PERMANENCE_PERMANENT_VALUE
    return None


def is_always_sampled(event_name: str, attributes: Attributes = None) -> bool:
    """Return True iff `event_name` matches §9.2 always-sampled discipline.

    Resolves three regimes, in order:

      1. The three §9.2 *conditional-by-attribute* rows (`files.operation` /
         `memory.operation` / `validator.fail.*`) via `attributes` — mutation
         kind / `permanence=permanent` always-sample; the non-mutation /
         transient complements fall to the §10.1 base-rate regime;
         conservative-absent (missing attribute → always-sample).
      2. Literal entries (e.g. `sandbox.violation`, `subagent.span`).
      3. Dot-anchored prefix entries (e.g. `audit.*` matches
         `audit.signature.write` AND `audit.cp.dispatch`; `audit` alone does
         NOT match).

    `attributes` defaults to `None` (backward-compatible): callers that do not
    supply attributes get the conservative always-sample decision for the
    conditional rows, byte-identical to the pre-B7 name-only behavior.
    """
    conditional = _conditional_always_sampled(event_name, attributes)
    if conditional is not None:
        return conditional
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

    This function resolves the cell-uniform decision *without* span attributes,
    so the §9.2 conditional-by-attribute rows (B7) resolve conservatively
    (always-sample). The attribute-aware decision is `is_always_sampled(
    event_class, attributes)`; the live SDK-boundary consumer is
    `composite_sampler.HarnessCompositeSampler.should_sample`.

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
