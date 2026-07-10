"""Cacheable-epoch primitive — the ttl-selection half (U-1 slice 3b, B-18).

Materializes the ttl-selection half of the ADR-D3 §1.5 cacheable-epoch contract::

    ttl: 5min default; 1hr at Persona §6 cost-ceiling cells where epoch > 5min

The cacheable epoch (ADR-D3 §1.5) is the unit of Anthropic prompt-cache reuse.
Its *identity* (which dispatches share a warm cache) is the byte-exact content
hash of the ``[frozen_tool_superset + system_prompt]`` prefix — Anthropic's cache
is byte-exact, so ``active_prompt_version.version_sha`` (IS ``PromptVersion``) is
already the cache-correct system-prompt key (see
``.harness/u1-slice3b-epoch-partition-design.md`` §2). The version_sha-keyed
cohort identity is consumed only by the ADR-D4 §1.8 fan-out pre-warm (slice 3c,
deferred), so it is NOT built here.

This module builds the one cache-epoch dimension with a LIVE consumer today: the
per-dispatch cache **ttl**. The ttl is a run-scoped constant (the run's
``workload_class`` is fixed at bootstrap stage 5), so it is selected once and
bound onto ``RuntimeLLMDispatcher.cache_ttl`` alongside ``frozen_tool_superset``
(the slice-1/2/3a precedent), then consumed at the Anthropic translate seam.

Persona §6 records the cost ceiling as a per-workload-class, **operator-asserted**
constraint (no fixed cell matrix). So "Persona §6 cost-ceiling cells" resolves to
an operator opt-in: the workload-classes for which the >5min (1hr) epoch is worth
the 2× cache-write cost. The default is empty → every workload-class uses the 5m
tier → byte-identical to pre-slice-3b. The selection gates a cost optimization,
not a correctness property (the 5m default is always correct), so — unlike
``effect_fencing`` / ``routing_activation`` — the opt-in is a file/CLI-only
collection field, NOT env-keyed (mirrors the other RuntimeConfig collections).

Authority: ``design-substrate/ADR-D3.md`` §1.5 (lines 187-188 cacheable_epoch +
ttl); ``Spec_Harness_Runtime_v1.md`` §14.5 (translate-seam breakpoint) + v1.97
(this ttl-selection binding). ``ProviderAgnosticPayload`` stays frozen (ADR-F1);
OpenAI/Ollama translators are untouched (Anthropic-only cache primitive).
"""

from __future__ import annotations

from typing import Literal

from harness_core.workload_class import WorkloadClass

__all__ = [
    "DEFAULT_CACHE_TTL",
    "LONG_CACHE_TTL",
    "CacheTTL",
    "select_cache_ttl",
]

# The two committed Anthropic ephemeral-cache tiers (ADR-D3 §1.5 line 188; the
# observability enum `anthropic.cache_ttl_seconds` ∈ {300, 3600}). A closed set —
# any third value is an ADR-D3 revision, not an impl choice.
CacheTTL = Literal["5m", "1h"]

DEFAULT_CACHE_TTL: CacheTTL = "5m"
LONG_CACHE_TTL: CacheTTL = "1h"


def select_cache_ttl(
    workload_class: WorkloadClass | None,
    long_ttl_workloads: frozenset[WorkloadClass],
) -> CacheTTL:
    """Select the Anthropic prompt-cache ttl for a run's workload class.

    Returns the 1hr tier when the run's ``workload_class`` is one the operator
    has opted into the long-ttl set (a Persona §6 cost-ceiling cell where the
    >5min epoch amortizes the 2× cache-write against a tight per-class ceiling);
    the 5min default otherwise. A ``None`` workload class (no run workload) always
    resolves to the 5min default. Empty ``long_ttl_workloads`` (the default) →
    every class resolves 5min → byte-identical to pre-slice-3b.
    """
    if workload_class is not None and workload_class in long_ttl_workloads:
        return LONG_CACHE_TTL
    return DEFAULT_CACHE_TTL
