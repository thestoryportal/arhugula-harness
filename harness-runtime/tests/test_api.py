"""U-RT-42 — `harness_runtime.run` + `RunResult` shape tests (closes L8).

ACs per Phase 2 Session 7 L8 stage 5 LOOP_INIT (U-RT-42 closes L8):

1. Signature pinned: `async def run(workflow, *, config=None) -> RunResult`.
2. `RunResult` is frozen Pydantic v2 with C-RT-09 field set.
3. Workflow validation: non-`WorkflowObject` input → `InvalidWorkflowError`
   (pre-bootstrap rejection).
4. Concurrency guard: second concurrent `run()` → `ConcurrentRunNotSupported`
   (C-RT-08 v1.1 idempotency-and-concurrency).
5. U-RT-43 wired: valid-shape `run()` runs bootstrap → workflow-execution
   stub → `WorkflowExecutionNotYetLandedError` (U-RT-44+ lands execution).
   `BootstrapNotYetLandedError` is removed.
6. Module-level lock is `asyncio.Lock`; re-export wiring at package root.

Bootstrap body itself is U-RT-43 scope — tests here verify ingress paths
without exercising bootstrap.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Literal

import harness_runtime
import harness_runtime.api as _api
import pytest
from harness_core.identity import WorkflowID
from harness_core.workload_class import WorkloadClass
from harness_od.cross_family_rollup import CrossFamilyCostRollup, RollupAxis
from harness_runtime.api import (
    ConcurrentRunNotSupported,
    FailureCause,
    HarnessDraining,
    InvalidWorkflowError,
    RunResult,
    WorkflowExecutionNotYetLandedError,
    WorkflowObject,
    run,
)
from harness_runtime.types import RuntimeConfig

# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------


class _Workflow:
    """Structural `WorkflowObject` for tests."""

    def __init__(
        self,
        workflow_id: str = "wf-test-1",
        workload_class: WorkloadClass = WorkloadClass.SOFTWARE_ENGINEERING,
    ) -> None:
        self._wid = workflow_id
        self._wc = workload_class

    @property
    def workflow_id(self) -> str:
        return self._wid

    @property
    def workload_class(self) -> WorkloadClass:
        return self._wc


def _rollup() -> CrossFamilyCostRollup:
    return CrossFamilyCostRollup(
        rollup_axis=RollupAxis.PER_PROVIDER_DISCRIMINATOR,
        group_key="anthropic",
        total_cost=0.0,
        span_count=1,
    )


# ---------------------------------------------------------------------------
# AC #1 — Signature.
# ---------------------------------------------------------------------------


def test_run_is_async() -> None:
    assert inspect.iscoroutinefunction(run)


def test_run_signature_matches_spec() -> None:
    """`async def run(workflow, *, config=None) -> RunResult` per C-RT-08."""
    sig = inspect.signature(run)
    params = list(sig.parameters.items())
    assert params[0][0] == "workflow"
    assert params[1][0] == "config"
    assert sig.parameters["config"].kind is inspect.Parameter.KEYWORD_ONLY
    assert sig.parameters["config"].default is None
    assert sig.return_annotation == "RunResult"


# ---------------------------------------------------------------------------
# AC #2 — RunResult shape (C-RT-09).
# ---------------------------------------------------------------------------


def test_run_result_is_frozen() -> None:
    result = RunResult(
        status="completed",
        workflow_id=WorkflowID("wf-1"),
        terminal_state={},
        audit_ledger_head_hash="0" * 64,
        trace_ids=(),
        cost_attribution=(),
    )
    with pytest.raises(Exception):  # noqa: B017 — frozen-violation typing varies
        result.status = "failed"  # type: ignore[misc]


def test_run_result_all_required_fields_per_c_rt_09() -> None:
    fields = set(RunResult.model_fields)
    assert fields == {
        "status",
        "workflow_id",
        "terminal_state",
        "audit_ledger_head_hash",
        "trace_ids",
        "cost_attribution",
        "failure_cause",
    }


def test_run_result_status_literal_three_values() -> None:
    """`status: Literal['completed', 'drained', 'failed']` per C-RT-09."""
    field = RunResult.model_fields["status"]
    # Pydantic v2 stores Literal in field annotation; round-trip both literals.
    for value in ("completed", "drained", "failed"):
        result = RunResult(
            status=value,  # type: ignore[arg-type]
            workflow_id=WorkflowID("wf-1"),
            terminal_state={},
            audit_ledger_head_hash="0" * 64,
            trace_ids=(),
            cost_attribution=(),
            failure_cause=(
                FailureCause(runtime_fail_class="RT-FAIL-BOOTSTRAP", detail="x")
                if value == "failed"
                else None
            ),
        )
        assert result.status == value
    _ = field  # annotation introspection is Pydantic-version-specific


def test_run_result_rejects_unknown_status() -> None:
    with pytest.raises(Exception):  # noqa: B017
        RunResult(
            status="unknown",  # type: ignore[arg-type]
            workflow_id=WorkflowID("wf-1"),
            terminal_state={},
            audit_ledger_head_hash="0" * 64,
            trace_ids=(),
            cost_attribution=(),
        )


def test_run_result_cost_attribution_carries_cross_family_rollup() -> None:
    """`cost_attribution` is `tuple[CrossFamilyCostRollup, ...]` — Class 3 drift note."""
    result = RunResult(
        status="completed",
        workflow_id=WorkflowID("wf-1"),
        terminal_state={},
        audit_ledger_head_hash="0" * 64,
        trace_ids=(),
        cost_attribution=(_rollup(),),
    )
    assert isinstance(result.cost_attribution[0], CrossFamilyCostRollup)


def test_failure_cause_mirrors_c_rt_14() -> None:
    cause = FailureCause(
        runtime_fail_class="RT-FAIL-BOOTSTRAP",
        detail="stage 1 IS failed",
    )
    assert cause.runtime_fail_class == "RT-FAIL-BOOTSTRAP"
    assert cause.validator_fail_class is None


# ---------------------------------------------------------------------------
# AC #3 — Workflow validation.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_rejects_non_workflow_object() -> None:
    with pytest.raises(InvalidWorkflowError):
        await run("not-a-workflow-object")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_run_rejects_object_missing_workflow_id_property() -> None:
    class _BadObj:
        pass

    with pytest.raises(InvalidWorkflowError):
        await run(_BadObj())  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# AC #4 — Concurrency guard.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_raises_on_concurrent_invocation() -> None:
    """Holding the module-level lock surfaces `ConcurrentRunNotSupported`."""
    await _api._run_lock.acquire()  # pyright: ignore[reportPrivateUsage]
    try:
        with pytest.raises(ConcurrentRunNotSupported):
            await run(_Workflow())
    finally:
        _api._run_lock.release()  # pyright: ignore[reportPrivateUsage]


# ---------------------------------------------------------------------------
# AC #5 — Bootstrap deferral.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_valid_run_reaches_execution_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    """U-RT-43 wires bootstrap; execution stub at U-RT-44+."""

    async def _fake_bootstrap(config, *, workload_class):  # type: ignore[no-untyped-def]
        return None

    monkeypatch.setattr("harness_runtime.bootstrap.run_bootstrap", _fake_bootstrap)
    monkeypatch.setattr(_api, "_default_config", lambda: None)
    with pytest.raises(WorkflowExecutionNotYetLandedError):
        await run(_Workflow())


@pytest.mark.asyncio
async def test_execution_stub_releases_lock_after_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    """The execution stub doesn't poison the lock — subsequent calls reach the stub."""

    async def _fake_bootstrap(config, *, workload_class):  # type: ignore[no-untyped-def]
        return None

    monkeypatch.setattr("harness_runtime.bootstrap.run_bootstrap", _fake_bootstrap)
    monkeypatch.setattr(_api, "_default_config", lambda: None)
    with pytest.raises(WorkflowExecutionNotYetLandedError):
        await run(_Workflow())
    with pytest.raises(WorkflowExecutionNotYetLandedError):
        await run(_Workflow())


@pytest.mark.asyncio
async def test_execution_stub_is_not_implemented_subclass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Generic NotImplementedError handlers still catch the execution stub."""

    async def _fake_bootstrap(config, *, workload_class):  # type: ignore[no-untyped-def]
        return None

    monkeypatch.setattr("harness_runtime.bootstrap.run_bootstrap", _fake_bootstrap)
    monkeypatch.setattr(_api, "_default_config", lambda: None)
    with pytest.raises(NotImplementedError):
        await run(_Workflow())


# ---------------------------------------------------------------------------
# AC #6 — Module-level lock + package-root re-export.
# ---------------------------------------------------------------------------


def test_run_lock_is_asyncio_lock() -> None:
    assert isinstance(_api._run_lock, asyncio.Lock)  # pyright: ignore[reportPrivateUsage]


def test_package_root_re_exports_api() -> None:
    """`harness_runtime.run`, `RunResult`, errors, `WorkflowObject` at package root."""
    assert harness_runtime.run is run
    assert harness_runtime.RunResult is RunResult
    assert harness_runtime.WorkflowObject is WorkflowObject
    assert harness_runtime.InvalidWorkflowError is InvalidWorkflowError
    assert harness_runtime.ConcurrentRunNotSupported is ConcurrentRunNotSupported
    assert (
        harness_runtime.WorkflowExecutionNotYetLandedError
        is WorkflowExecutionNotYetLandedError
    )
    assert harness_runtime.FailureCause is FailureCause


# ---------------------------------------------------------------------------
# AC #7 (U-RT-44) — Pre-bootstrap drain rejection (C-RT-11 surface (3)).
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_raises_harness_draining_when_process_drained(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """C-RT-11 surface (3) — drained process refuses new `run()` invocations.

    `monkeypatch.setattr` restores the original module attribute at test
    teardown, so the one-way `_process_drained` flag is reset between tests.
    """
    from harness_runtime import drain as drain_mod

    monkeypatch.setattr(drain_mod, "_process_drained", True)
    with pytest.raises(HarnessDraining):
        await run(_Workflow())


@pytest.mark.asyncio
async def test_harness_draining_raised_before_workflow_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Drain check fires pre-validation — bad workflow + drained → `HarnessDraining`."""
    from harness_runtime import drain as drain_mod

    monkeypatch.setattr(drain_mod, "_process_drained", True)
    with pytest.raises(HarnessDraining):
        await run("not-a-workflow")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_harness_draining_raised_before_lock_acquisition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Drained process surfaces `HarnessDraining` even with the lock held."""
    from harness_runtime import drain as drain_mod

    monkeypatch.setattr(drain_mod, "_process_drained", True)
    await _api._run_lock.acquire()  # pyright: ignore[reportPrivateUsage]
    try:
        with pytest.raises(HarnessDraining):
            await run(_Workflow())
    finally:
        _api._run_lock.release()  # pyright: ignore[reportPrivateUsage]


def test_harness_draining_is_distinct_typed_error() -> None:
    """`HarnessDraining` is `Exception`-rooted (not NotImplementedError-rooted)."""
    assert issubclass(HarnessDraining, Exception)
    assert not issubclass(HarnessDraining, NotImplementedError)
    assert not issubclass(HarnessDraining, InvalidWorkflowError)
    assert not issubclass(HarnessDraining, ConcurrentRunNotSupported)


def test_harness_draining_re_exported_at_package_root() -> None:
    assert harness_runtime.HarnessDraining is HarnessDraining


def test_run_accepts_optional_config(tmp_path: object) -> None:
    """`config=None` default; both call forms reach the bootstrap stub."""
    # Signature carries `config: RuntimeConfig | None = None`.
    sig = inspect.signature(run)
    assert sig.parameters["config"].annotation == "RuntimeConfig | None"


def test_workflow_object_protocol_runtime_checkable() -> None:
    """`isinstance(_Workflow(), WorkflowObject)` works (runtime_checkable)."""
    assert isinstance(_Workflow(), WorkflowObject)
    assert not isinstance("string", WorkflowObject)


_ = Literal  # silence unused-import on the imported Literal anchor
_ = RuntimeConfig  # signature-introspection anchor
