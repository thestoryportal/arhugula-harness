"""B-162 closure witness — `U-CP-65` AC #5: pause + resume spans really are emitted.

**What B-162 was.** `C-OD-30.3` declares `pause.captured` and `resume.attempted` at
`head=1.0`, and `U-CP-65` requires both to *emit* with 4 canonical attributes each (AC #1,
AC #2) plus *"Integration test: pause + resume + verify span emission via OTel test
collector"* (AC #5). Both emitters were landed and unit-tested in
`harness-cp/src/harness_cp/pause_resume_protocol.py` — and **nothing in `src/` called
either of them**, so neither span existed at runtime. The unit was green on its helper and
unmet on its contract.

It was found while re-measuring `B-137` at the real `api.run` venue: an earlier draft of
that arc used `emit_pause_captured_span` as its *"real production emitter"* and drove it
directly. The function was real; the **path** was not.
`[[verification-shape-sharpened-grep-vs-e2e]]`

**What closes it.** `workflow_driver.py` now calls `_emit_pause_captured` after every
`protocol.capture_pause_snapshot(...)` — 11 sites across the 6 topology executors — and
`_emit_resume_attempted` after the entry-point `protocol.attempt_resume(...)`. This module
is AC #5: it drives the shipped `api.run` path with a real `TracerProvider` and reads the
spans back off the exporter, asserting the canonical attribute set rather than mere
presence.

**Scope, stated.** These spans are emitted *inside* `workflow.envelope` on the pause path,
so their §9.2 floor remains subject to `B-137`'s root-only starvation — wiring them is
**AC conformance, not a sampling fix**, and B-160's disposition still depends on B-137.
This module therefore uses an always-on provider: it asserts *emission*, which is what
U-CP-65 requires, and deliberately says nothing about survival under the production
sampler (that is B-137's subject, measured at
`test_b137_ninety_two_floor_at_the_real_run_venue.py`).
"""

from __future__ import annotations

import ast
import importlib.util
import pathlib
import sys
import tempfile
from typing import Any

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_REPO = pathlib.Path(__file__).resolve().parents[3]
_DRIVER = _REPO / "harness-cp/src/harness_cp/workflow_driver.py"

#: The 4 canonical attributes each span carries per OD spec §C-OD-30.1.
_PAUSE_ATTRS = frozenset(
    {"pause.reason", "pause.snapshot_hash", "pause.step_index", "pause.state_ledger_anchor"}
)
_RESUME_ATTRS = frozenset(
    {"resume.snapshot_hash", "resume.diff_detected", "resume.diff_policy", "resume.outcome"}
)


def _b72() -> Any:
    """Load the B-72 fan-out harness by path — it is the venue that really pauses."""
    path = pathlib.Path(__file__).with_name(
        "test_b72_fanout_sub_agent_dispatch_hitl_gate_resume.py"
    )
    name = "_b162_b72_harness"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


async def _run_and_collect(*, then_resume: bool = False) -> list[Any]:
    """Drive the shipped `api.run` (and optionally `api.resume`) path; return exported spans.

    `then_resume=True` completes AC #5's *"pause + resume"* half by feeding the paused
    snapshot back through the real `resume()` entry point, which is the call site
    `_emit_resume_attempted` is wired to.
    """
    harness = _b72()
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

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
            assert result.status == "paused", f"the venue did not reach its pause: {result.status}"
            if then_resume:
                await harness.resume(
                    harness._FanOutSubAgentDispatchWorkflow(),
                    pause_snapshot=result.pause_snapshot,
                    resume_context=harness.ResumeContext(
                        hitl_response=harness._resolved_hitl_result(entry_suffix="b162")
                    ),
                    config=harness._config(pathlib.Path(tmp)),
                )
    return list(exporter.get_finished_spans())


@pytest.mark.asyncio
async def test_pause_captured_is_emitted_by_the_shipped_run() -> None:
    """**AC #1 + AC #5** — the span exists at runtime, not just as a helper.

    Reverting the `_emit_pause_captured(...)` call in `workflow_driver.py` turns this RED,
    which is the whole point: before B-162 this assertion could not have passed at all.
    """
    spans = await _run_and_collect()
    captured = [s for s in spans if s.name == "pause.captured"]
    assert captured, (
        f"`pause.captured` was not emitted by the shipped run; got {sorted({s.name for s in spans})}"
        " — U-CP-65 AC #1 is unmet and B-162 has regressed"
    )


@pytest.mark.asyncio
async def test_pause_captured_carries_the_four_canonical_attributes() -> None:
    """**AC #4** — attribute names byte-exact per OD §C-OD-30.1, not merely present.

    Asserting the exact set (rather than a subset) means a dropped attribute reddens, and
    an extra one forces a deliberate contract re-read rather than silent drift.
    """
    spans = await _run_and_collect()
    captured = [s for s in spans if s.name == "pause.captured"]
    assert captured, "`pause.captured` was not emitted — see the emission test above"

    emitted = set((captured[0].attributes or {}).keys())
    assert emitted == _PAUSE_ATTRS, (
        f"`pause.captured` attribute set drifted from OD §C-OD-30.1: "
        f"missing={sorted(_PAUSE_ATTRS - emitted)} unexpected={sorted(emitted - _PAUSE_ATTRS)}"
    )
    # The values come from the real snapshot, not a fixture.
    values = captured[0].attributes or {}
    assert values["pause.reason"] == "hitl_pending", (
        f"expected the B-72 venue to pause for HITL, got {values['pause.reason']!r}"
    )
    assert (
        isinstance(values["pause.snapshot_hash"], str)
        and len(str(values["pause.snapshot_hash"])) == 64
    ), "pause.snapshot_hash is not a 64-char digest — the real snapshot is not reaching the span"


def test_the_driver_emits_at_every_capture_site() -> None:
    """Every `capture_pause_snapshot` call is followed by an emission — not just one.

    The pause span must exist for **all six** topology executors, not only the path the
    integration venue happens to exercise. A partial wiring would leave `pause.captured`
    missing for the other topologies while the tests above stayed green, so the site count
    is asserted structurally by AST.
    """
    tree = ast.parse(_DRIVER.read_text())

    capture_sites = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "capture_pause_snapshot"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "protocol"
    ]
    emit_sites = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_emit_pause_captured"
    ]
    assert capture_sites, "no `protocol.capture_pause_snapshot` sites found — re-ground B-162"
    assert len(emit_sites) >= len(capture_sites), (
        f"{len(capture_sites)} capture site(s) but only {len(emit_sites)} emission(s) — a "
        "topology executor would pause without emitting `pause.captured`"
    )


def test_the_resume_emission_honours_the_corruption_carve_out() -> None:
    """`resume.attempted` must NOT be emitted on the corruption path.

    `emit_resume_attempted_span`'s docstring states the caller convention: §C-OD-30.1's
    `resume.outcome` enum (`resumed` / `diff_aborted` / `arbitration_owed`) has **no value**
    for corruption, which is a pre-resume validation failure rather than a resume outcome.
    The driver-side wrapper implements that guard; this asserts the guard exists, since
    losing it would emit a span with no valid outcome value.
    """
    source = _DRIVER.read_text()
    tree = ast.parse(source)

    wrapper = next(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "_emit_resume_attempted"
        ),
        None,
    )
    assert wrapper is not None, "`_emit_resume_attempted` is gone — B-162's wiring regressed"

    body = ast.unparse(wrapper)
    assert "CP_FAIL_PAUSE_SNAPSHOT_CORRUPTION" in body, (
        "the corruption carve-out left `_emit_resume_attempted` — a `resume.attempted` span "
        "would be emitted with no valid §C-OD-30.1 `resume.outcome` value"
    )


def test_the_resume_emitter_is_wired_to_the_entry_point_call() -> None:
    """The resume emission sits on the entry-point `protocol.attempt_resume`, not a sibling.

    `workflow_driver.py` also calls `_engine_recovery_loop.attempt_resume(...)` at three
    other sites — a different, engine-layer function. Anchoring on the wrong one is a real
    hazard here (out-of-family Codex caught exactly that mistake in the B-137 arc), so the
    receiver is resolved explicitly.
    """
    tree = ast.parse(_DRIVER.read_text())

    entry_calls = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "attempt_resume"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "protocol"
    ]
    emit_calls = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_emit_resume_attempted"
    ]
    assert len(entry_calls) == 1, (
        f"expected exactly one entry-point `protocol.attempt_resume`, got {entry_calls}"
    )
    assert len(emit_calls) == 1, (
        f"expected exactly one `_emit_resume_attempted` call, got {emit_calls}"
    )
    assert emit_calls[0] > entry_calls[0], (
        f"the resume emission ({emit_calls[0]}) does not follow the entry-point resume call "
        f"({entry_calls[0]})"
    )


@pytest.mark.asyncio
async def test_resume_attempted_is_emitted_and_carries_its_four_attributes() -> None:
    """**AC #2 + AC #5's resume half** — driven through the real `resume()` entry point.

    The pause tests above cover only half of what U-CP-65 AC #5 asks for (*"pause + resume
    + verify span emission"*). This feeds the paused snapshot back through the shipped
    `resume()` API, which is exactly where `_emit_resume_attempted` is wired, and asserts
    the canonical `resume.*` attribute set rather than mere presence.
    """
    spans = await _run_and_collect(then_resume=True)
    attempted = [s for s in spans if s.name == "resume.attempted"]
    assert attempted, (
        f"`resume.attempted` was not emitted by the shipped resume; got "
        f"{sorted({s.name for s in spans})} — U-CP-65 AC #2 is unmet"
    )

    emitted = set((attempted[0].attributes or {}).keys())
    assert emitted == _RESUME_ATTRS, (
        f"`resume.attempted` attribute set drifted from OD §C-OD-30.1: "
        f"missing={sorted(_RESUME_ATTRS - emitted)} unexpected={sorted(emitted - _RESUME_ATTRS)}"
    )
    values = attempted[0].attributes or {}
    assert values["resume.outcome"] in {"resumed", "diff_aborted", "arbitration_owed"}, (
        f"`resume.outcome` is {values['resume.outcome']!r}, outside §C-OD-30.1's 3-class enum"
    )
    assert values["resume.diff_policy"] == "strict", (
        f"expected the driver's STRICT default policy, got {values['resume.diff_policy']!r}"
    )
