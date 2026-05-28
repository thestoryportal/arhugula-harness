"""C-OD-09 + C-OD-10 composite sampler — OTel SDK `Sampler` subclass.

H_T-OD-3 retirement substrate. Closes the project-authored-sampler gap at
`harness-runtime/lifecycle/tracer_provider.py:_DEFAULT_SAMPLER` (previously
stock `ParentBased(ALWAYS_ON)` per the module docstring's defense-in-depth
deferral) by honoring the OD spec v1.2 §9.2 always-sampled set at the SDK
boundary.

**Composition** (per OTel canonical pattern):

    ParentBased(root=HarnessCompositeSampler(base_rate=...))

ParentBased wrapping preserves trace consistency — children of a sampled
parent always sample; children of an unsampled parent never sample. The
inner `HarnessCompositeSampler` resolves the root-span decision via:

  1. If `name` matches §9.2 always-sampled set (via `is_always_sampled`):
     return `RECORD_AND_SAMPLE`.
  2. Else: delegate to `TraceIdRatioBased(base_rate)`.

**MVP scoping (conservative over-sampling at §9.2 conditional rows).**
§9.2 has four conditional-by-attribute rows:

  - `files.operation` always-sampled only at `kind ∈ {upload, delete}`
  - `memory.operation` always-sampled only at `kind ∈ {write, update, delete}`
  - `validator.fail.*` always-sampled only at `permanence=permanent`
  - `subagent.span` always-sampled only at the root

The substrate carrier `ALWAYS_SAMPLED_EVENT_CLASSES` lists these by name
(matching the §9.2 row labels). At MVP this sampler over-samples — every
`files.operation` span samples, not only mutation variants. Over-sampling
is conservative (sample MORE than spec mandates, never less); refining via
`attributes` lookup is a future arc.

**Base-rate sourcing.** Per §10.3 the base-rate envelope is keyed by
(persona_tier × deployment_surface). `persona_tier` is not plumbed at the
sampler binding site at HEAD; MVP hardcodes `base_rate=1.0` (matching the
§10.3 solo-developer × local-development default) and accepts that
production-surface envelopes are deferred. Class 3 informational.
"""

from __future__ import annotations

from typing import Sequence

from opentelemetry.context import Context
from opentelemetry.sdk.trace.sampling import (
    Decision,
    ParentBased,
    Sampler,
    SamplingResult,
    TraceIdRatioBased,
)
from opentelemetry.trace import Link, SpanKind
from opentelemetry.trace.span import TraceState
from opentelemetry.util.types import Attributes

from harness_od.sampling_mode import is_always_sampled

__all__ = [
    "HarnessCompositeSampler",
    "build_default_sampler",
]


class HarnessCompositeSampler(Sampler):
    """Composite sampler honoring §9.2 always-sampled set + §10.1 base-rate.

    Designed to sit inside `ParentBased(root=...)` per OTel canonical pattern;
    standalone use samples root spans correctly but does not propagate the
    parent decision to children.
    """

    def __init__(self, base_rate: float = 1.0) -> None:
        if not (0.0 <= base_rate <= 1.0):
            raise ValueError(
                f"base_rate must be in [0.0, 1.0]; got {base_rate}"
            )
        self._base_rate = base_rate
        self._ratio_sampler = TraceIdRatioBased(base_rate)

    @property
    def base_rate(self) -> float:
        """Per §10.1 base-rate set sampling probability (cell-tunable)."""
        return self._base_rate

    def should_sample(
        self,
        parent_context: Context | None,
        trace_id: int,
        name: str,
        kind: SpanKind | None = None,
        attributes: Attributes = None,
        links: Sequence[Link] | None = None,
        trace_state: TraceState | None = None,
    ) -> SamplingResult:
        if is_always_sampled(name):
            return SamplingResult(
                decision=Decision.RECORD_AND_SAMPLE,
                attributes=attributes,
                trace_state=trace_state,
            )
        return self._ratio_sampler.should_sample(
            parent_context=parent_context,
            trace_id=trace_id,
            name=name,
            kind=kind,
            attributes=attributes,
            links=links,
            trace_state=trace_state,
        )

    def get_description(self) -> str:
        return (
            f"HarnessCompositeSampler(always_sampled_per_C-OD-09_§9.2, "
            f"base_rate={self._base_rate})"
        )


def build_default_sampler(base_rate: float = 1.0) -> Sampler:
    """Build the canonical `ParentBased(root=HarnessCompositeSampler(...))`.

    `base_rate` defaults to 1.0 matching §10.3 solo-developer × local-development
    row. Production deployments threading a non-default `base_rate` is owed at
    a follow-on arc once persona_tier is plumbed at the materializer.
    """
    return ParentBased(root=HarnessCompositeSampler(base_rate=base_rate))
