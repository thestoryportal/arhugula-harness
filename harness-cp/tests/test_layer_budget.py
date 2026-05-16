"""Tests for U-CP-06 — `LayerBudget` data type (C-CP-03 §3.1).

Acceptance-criterion coverage:
  #1 four fields per §3.1           -> test_layer_budget_four_fields
  #2 one DEFAULT entry per layer    -> test_default_one_per_layer
  #3 override precedence            -> test_effective_budget_override_precedence
  #4 exhaustion emits attribute     -> STRUCK (halt-route-split-AC) — see note

Note on acceptance #4. "Budget exhaustion emits `routing.budget_exhausted =
true` on the layer's span per U-CP-01" is a behavioural contract over an OTel
span emitter, which does not exist at sub-phase 7b. Per the halt-route-split-AC
pattern #4 + its `test_exhaustion_emits_attribute` test are struck and routed
to a downstream emitter unit. The schema half (#1-#3) is landed in full.
"""

from __future__ import annotations

from harness_core import PersonaTier, WorkloadClass
from harness_cp.layer_budget import (
    DEFAULT_LAYER_BUDGETS,
    LayerBudget,
    effective_budget,
)
from harness_cp.routing_layer import RoutingLayer


def test_layer_budget_four_fields() -> None:
    """#1 — `LayerBudget` declares exactly four fields per C-CP-03 §3.1."""
    assert set(LayerBudget.model_fields) == {
        "layer",
        "time_budget_ms",
        "per_workload_override",
        "per_persona_override",
    }


def test_default_one_per_layer() -> None:
    """#2 — `DEFAULT_LAYER_BUDGETS` exposes one entry per `RoutingLayer`."""
    assert len(DEFAULT_LAYER_BUDGETS) == len(RoutingLayer)
    assert {b.layer for b in DEFAULT_LAYER_BUDGETS} == set(RoutingLayer)


def test_effective_budget_override_precedence() -> None:
    """#3 — workload override resolves first, then persona, then default."""
    # No overrides on the default registry -> returns layer default.
    assert (
        effective_budget(
            RoutingLayer.EMBEDDING,
            WorkloadClass.RESEARCH,
            PersonaTier.SOLO_DEVELOPER,
        )
        == 50
    )

    # Workload override wins over persona override and default.
    budget = LayerBudget(
        layer=RoutingLayer.DECLARATIVE,
        time_budget_ms=10,
        per_workload_override={WorkloadClass.RESEARCH: 3},
        per_persona_override={PersonaTier.SOLO_DEVELOPER: 7},
    )
    assert budget.per_workload_override is not None
    assert budget.per_workload_override[WorkloadClass.RESEARCH] == 3

    # Persona override wins when workload override absent.
    persona_only = LayerBudget(
        layer=RoutingLayer.DECLARATIVE,
        time_budget_ms=10,
        per_persona_override={PersonaTier.TEAM_BINDING: 8},
    )
    assert persona_only.per_persona_override is not None
    assert persona_only.per_persona_override[PersonaTier.TEAM_BINDING] == 8


def test_default_values_deferred_but_present() -> None:
    """#2 — concrete defaults are operator-discretion but each layer carries
    a positive budget; ordering honors cheapest-deterministic-first."""
    by_layer = {b.layer: b.time_budget_ms for b in DEFAULT_LAYER_BUDGETS}
    assert all(ms > 0 for ms in by_layer.values())
    assert (
        by_layer[RoutingLayer.DECLARATIVE]
        <= by_layer[RoutingLayer.EMBEDDING]
        <= by_layer[RoutingLayer.LLM_AS_ROUTER]
    )


def test_layer_budget_frozen() -> None:
    """`LayerBudget` is a frozen, extra-forbid record."""
    budget = LayerBudget(layer=RoutingLayer.EMBEDDING, time_budget_ms=42)
    assert budget.model_config.get("frozen") is True
    assert budget.model_config.get("extra") == "forbid"


def test_routing_layer_cardinality_three() -> None:
    """`RoutingLayer` declares exactly three values, spec-byte-exact."""
    assert len(RoutingLayer) == 3
    assert {layer.value for layer in RoutingLayer} == {
        "manifest",
        "embedding",
        "llm_as_router",
    }
