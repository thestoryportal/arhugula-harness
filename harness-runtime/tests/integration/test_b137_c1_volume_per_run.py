"""B-137: C1's per-run EXPORTED span count, measured through the real processor chain.

`B-137`'s C11 objection is that C1's `1/base_rate` multiplier is *"unpriced against the C-OD-11
§11.1 per-cell budgets."* `B-182` established that the cap **does** carry a number
(`cell_rate_limit=10_000.0` **spans/sec**) and that what is open is the **volume evidence**. A
spans/sec budget factors as `spans-per-run × runs-per-sec`, and `runs/sec` is Persona §11
open-item 4 — still open, and not closable here.

**This module measures `spans per run`, and it is deliberately narrow about what that buys.**

**A first draft of this module was wrong in the most embarrassing way available.** It reused the
sibling module's `_run_the_real_workflow`, which attaches only a `SimpleSpanProcessor` — so it
counted **head admission** and reported it as **exports**. That is *precisely* the error the
immediately-preceding arc documented, in a module this one cites by name
(`test_b137_c1_discriminator.py`, discipline 1: *"Head admission is not export"*). Out-of-family
Codex caught it in one round. The corrected composition routes through the real
`TailKeepSpanProcessor`, and the numbers change materially:

| composition | exported |
|---|---|
| head only, `base_rate=1.0` (the draft's mistake) | 3 — `workflow.envelope`, `hitl.gate.evaluated`, `pause.captured` |
| **real chain**, `base_rate=1.0` | **1** — `hitl.gate.evaluated` |
| **real chain**, C1 at `base_rate=0.0` | **2** — `hitl.gate.evaluated`, `workflow.envelope` |
| **real chain**, no C1 at `base_rate=0.0` | **0** |

The envelope and `pause.captured` are head-admitted at `1.0` but **buffered and dropped at root
close**, because the trace carries no §10.2 classification trigger. Only C1 rescues the envelope,
and it does so by making the root take the always-sampled bypass arm.

**What is claimed, and it is one sentence.** At the venue this actually ran —
`solo-developer × local-development`, the B-72 fan-out — C1 exports **2 spans per run** where the
shipped configuration exports **1**.

**What is NOT claimed, each because a reviewer was right to stop it.**

- **No break-even run rate.** A first draft divided the `team-binding × self-hosted-server` cap by
  a span count measured at `solo-developer × local-development`. The deployment surface selects the
  tail pipeline and the persona tier affects HITL behaviour, so that division is invalid. Pricing
  the team cell requires measuring **at** the team cell, which this arc did not do — registered as
  the explicit next step rather than approximated.
- **No "lower bound" on span volume.** A first draft called 3 spans/run a floor. Wrong direction:
  B-72 is a *HITL-focused* fixture, so a workflow that never reaches a gate or captures a pause
  emits **fewer** of exactly these spans. One observed sample is a sample, not a bound.
- **Nothing about affordability.** B-137's council call is untouched.

**Determinism.** Only decidable compositions are asserted: `base_rate=1.0` (everything admitted at
the head) and `base_rate=0.0` (the ratio arm admits nothing; only the always-sampled arm can). The
production rate 0.1 is a genuine sample — a probe run at 0.1 exported all three head-admitted spans
because the root happened to win its draw — so nothing is asserted there.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile
from typing import Any

import pytest
from harness_od.tail_keep_span_processor import TailKeepSpanProcessor
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

#: The cell the B-72 harness config really binds. NOT the cell whose cap B-137 quotes — which is
#: exactly why this module derives no break-even rate. See the docstring.
_MEASURED_CELL = ("solo-developer", "local-development")


def _venue() -> Any:
    """Load the sibling step-(2) module, which owns the real-`api.run` harness."""
    path = pathlib.Path(__file__).with_name("test_b137_ninety_two_floor_at_the_real_run_venue.py")
    name = "_b137_volume_venue"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


async def _exported_through_the_real_chain(*, base_rate: float) -> list[str]:
    """Drive the shipped `api.run` path and return what the REAL processor chain EXPORTS.

    The sibling's `_run_the_real_workflow` attaches only a `SimpleSpanProcessor`, which observes
    head ADMISSION. Pricing a spans/sec cap needs EXPORTS, so this composes the production
    `TailKeepSpanProcessor` in front of the exporter — the correction out-of-family Codex forced.
    """
    venue = _venue()
    harness = venue._b72()
    exporter = InMemorySpanExporter()
    with tempfile.TemporaryDirectory() as cfg_tmp:
        provider = venue._production_provider(
            harness._config(pathlib.Path(cfg_tmp)), base_rate=base_rate
        )
    provider.add_span_processor(TailKeepSpanProcessor(downstream=SimpleSpanProcessor(exporter)))

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            harness._FakeTracerProvider,
            "get_tracer",
            lambda self, name, /: provider.get_tracer(name),
        )
        harness._install_fake_providers(mp, harness._SucceedingAnthropicClient())
        harness._install_fake_od_stage4(mp)
        harness._install_fake_webhook_composer_factory(mp, [])
        with tempfile.TemporaryDirectory() as tmp:
            result = await harness.api_run(
                harness._FanOutSubAgentDispatchWorkflow(),
                config=harness._config(pathlib.Path(tmp)),
            )
    assert result.status == "paused", f"the B-72 venue did not reach its gate: {result.status}"
    provider.force_flush()
    return sorted(s.name for s in exporter.get_finished_spans())


def test_the_measured_cell_is_recorded_and_is_not_the_cell_whose_cap_b137_quotes() -> None:
    """**The scope pin that stops the number being misused** (out-of-family Codex [P2]).

    A first draft divided the `team-binding × self-hosted-server` cap by a count measured here.
    The deployment surface selects the tail pipeline and the persona tier affects HITL behaviour,
    so that division is invalid. This asserts the venue's real binding so the mismatch is visible
    at the top of any future read rather than buried.
    """
    venue = _venue()
    with tempfile.TemporaryDirectory() as tmp:
        cfg = venue._b72()._config(pathlib.Path(tmp))
    measured = (cfg.persona_tier.value, cfg.deployment_surface.value)
    assert measured == _MEASURED_CELL, (
        f"the B-72 harness now binds {measured}, not {_MEASURED_CELL}. If it now binds the team "
        "cell, this module's counts CAN price B-137's cap and the derivation it currently "
        "refuses becomes available — re-ground B-137 before assuming either way"
    )


@pytest.mark.asyncio
async def test_the_shipped_configuration_exports_one_span_per_run() -> None:
    """The baseline C1 is a cost against: what the real chain exports with everything admitted.

    Only `hitl.gate.evaluated` survives. `workflow.envelope` and `pause.captured` are admitted at
    the head but buffered and dropped at root close — the trace carries no §10.2 trigger.
    """
    exported = await _exported_through_the_real_chain(base_rate=1.0)
    assert exported == ["hitl.gate.evaluated"], (
        f"the real chain now exports {exported} at full admission, not ['hitl.gate.evaluated']. "
        "B-137's per-run figures are derived from this and are stale"
    )


@pytest.mark.asyncio
async def test_c1_exports_two_spans_per_run_deterministically() -> None:
    """**The measurement.** C1's exported per-run count at a decidable rate.

    At `base_rate=0.0` the ratio arm admits nothing, so everything here is admitted by the
    always-sampled arm via root inheritance — a decision, not a sample.
    """
    venue = _venue()
    with venue._member_set(add=frozenset({venue._ENVELOPE})):
        exported = await _exported_through_the_real_chain(base_rate=0.0)
    assert exported == ["hitl.gate.evaluated", "workflow.envelope"], (
        f"under C1 the real chain now exports {exported}, not the measured pair. B-137's per-run "
        "figure is stale — re-measure before quoting it"
    )


@pytest.mark.asyncio
async def test_without_c1_the_same_run_exports_nothing_at_a_starving_rate() -> None:
    """The contrast that makes C1's count a marginal COST rather than a baseline."""
    exported = await _exported_through_the_real_chain(base_rate=0.0)
    assert exported == [], (
        f"a starving rate now exports {exported} without C1 — the floor reaches the run by some "
        "other route and C1's marginal cost is smaller than measured here"
    )
