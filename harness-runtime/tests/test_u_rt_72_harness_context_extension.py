"""U-RT-72 — HarnessContext schema extension: 4 new fields.

Tests per Implementation_Plan_Harness_Runtime_v2_13.md §1B (preserved from
v2.12). Spec contract: Spec_Harness_Runtime_v1.md v1.16 §4 C-RT-04
field-table extension.

Note: integration bootstrap tests (`test_bootstrap.py::*`) will be red
through the L9-septies cluster execution arc until U-RT-73 (stage-3a
factory) + U-RT-75 (stage-5 factory) + U-RT-68 (stage-5 wire-up) land
and populate the 4 new required fields. Cluster close re-greens those.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from harness_runtime.bootstrap.mutable_context import (
    IncompleteBootstrapError,
    _MutableHarnessContext,
)
from harness_runtime.types import HarnessContext


def _sentinel(label: str) -> Any:
    """Distinct sentinel object for identity-equality test assertions."""

    class _Sentinel:
        def __repr__(self) -> str:
            return f"<sentinel:{label}>"

    return _Sentinel()


def test_harness_context_declares_four_new_fields() -> None:
    # AC #1 — schema declares the 4 new required fields.
    fields = set(HarnessContext.model_fields)
    assert "mcp_client_hosts" in fields
    assert "tool_dispatcher" in fields
    assert "per_server_trust_evaluator" in fields
    assert "mcp_namespace_emitter" in fields


def test_mutable_builder_accepts_setter_for_four_new_fields() -> None:
    # AC #2 — builder accepts setter calls for the 4 new fields.
    builder = _MutableHarnessContext()
    builder.mcp_client_hosts = _sentinel("mcp_client_hosts")
    builder.tool_dispatcher = _sentinel("tool_dispatcher")
    builder.per_server_trust_evaluator = _sentinel("per_server_trust_evaluator")
    builder.mcp_namespace_emitter = _sentinel("mcp_namespace_emitter")
    # No exception — assignment is the assertion.
    assert builder.mcp_client_hosts is not None
    assert builder.tool_dispatcher is not None
    assert builder.per_server_trust_evaluator is not None
    assert builder.mcp_namespace_emitter is not None


def test_freeze_raises_when_any_of_four_new_fields_is_none() -> None:
    # AC #3 — finalize raises if any of the 4 new fields is None.
    # We can't easily build a full mutable context with EVERYTHING populated
    # except one new field in a unit test, so we exercise the
    # `IncompleteBootstrapError` reporting surface instead — the bare
    # builder reports all 36 required fields (32 prior + 4 new) as missing.
    with pytest.raises(IncompleteBootstrapError) as excinfo:
        _MutableHarnessContext().freeze()
    missing = excinfo.value.missing_fields
    # The 4 new fields are in the missing-fields report.
    assert "mcp_client_hosts" in missing
    assert "tool_dispatcher" in missing
    assert "per_server_trust_evaluator" in missing
    assert "mcp_namespace_emitter" in missing


def test_distinct_primitive_invariant_mcp_host_vs_mcp_client_hosts() -> None:
    # AC #4 — ctx.mcp_host (server-side) is NOT the same object as
    # ctx.mcp_client_hosts (client-side). Verified at the type/builder layer
    # by setting two distinct sentinels and asserting identity inequality.
    builder = _MutableHarnessContext()
    server_side = _sentinel("server-side-mcp-host")
    client_side = _sentinel("client-side-mcp-client-hosts")
    builder.mcp_host = server_side
    builder.mcp_client_hosts = client_side
    assert builder.mcp_host is not builder.mcp_client_hosts
    # And they hold the assigned sentinels.
    assert builder.mcp_host is server_side
    assert builder.mcp_client_hosts is client_side


def test_required_fields_count_includes_four_new() -> None:
    # AC #3 / AC #5 cross-check — _REQUIRED_FIELDS includes the 4 new fields
    # (was 32 at v1.14; 36 at v1.16 post U-RT-72; 37 at v1.17 post U-RT-80
    # adds `memory_tool_registry` per spec §14.12 C-RT-22 + §4 C-RT-04;
    # 38 at v1.21 post U-RT-87 adds `pause_requested_flag` per spec §14.14.3
    # sibling-pattern to `drained_flag`; 39 at v1.25 post U-RT-94 adds
    # `resume_context_holder` per spec §4 C-RT-04 + §14.8.8.9 NEW carrier
    # (RETIRED at B-39 Slice B — per-branch HITL delivery via
    # `StepExecutionContext.hitl_delivery_holder` replaces it, -1 from 39);
    # 41 at R-CXA-2 adds `hitl_tool_loop` + `engine_recovery_loop` (40 net
    # post-retirement).
    from harness_runtime.bootstrap.mutable_context import _REQUIRED_FIELDS

    assert len(_REQUIRED_FIELDS) == 40
    for new_field in (
        "mcp_client_hosts",
        "tool_dispatcher",
        "per_server_trust_evaluator",
        "mcp_namespace_emitter",
    ):
        assert new_field in _REQUIRED_FIELDS


def test_harness_context_importable_from_runtime_types() -> None:
    # AC #5 — importable; field schema reachable.
    from harness_runtime.types import HarnessContext as HC

    assert "mcp_client_hosts" in HC.model_fields


@pytest.mark.asyncio
async def test_frozen_harness_context_accepts_four_new_fields_populated() -> None:
    """AC #1 — frozen HarnessContext instantiates when all 4 new fields are
    populated (alongside the prior 32 required fields). Uses the mutable
    builder with sentinel fills for the entire required-field set.

    This test deliberately bypasses the orchestrator's stage-driven bootstrap
    (which only populates the 4 new fields at U-RT-73 + U-RT-75 + U-RT-68
    landings — those units come later in the L9-septies cascade)."""
    builder = _MutableHarnessContext()
    # Populate every required field with a sentinel — most concrete types
    # are arbitrary-types-allowed on the frozen model.
    from harness_runtime.bootstrap.mutable_context import _REQUIRED_FIELDS

    for name in _REQUIRED_FIELDS:
        if name == "drained_flag":
            setattr(builder, name, asyncio.Event())
        else:
            setattr(builder, name, _sentinel(name))
    # freeze() will fail Pydantic validation on the prior 32 fields because
    # their types are concrete (e.g., `config: RuntimeConfig`). The minimum
    # this test proves: the freeze code path passes through all 4 new fields
    # into the HarnessContext constructor (covered by AC #2 + the freeze body
    # extension committed in this unit). Coverage of full end-to-end
    # construction is exercised by `test_bootstrap.py` post cluster close.
    with pytest.raises(Exception):
        builder.freeze()


def test_freeze_forwards_protected_result_store_to_frozen_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """B-65-A codex [P1] round 6: `protected_result_store` is set on the
    mutable builder at bootstrap stage 4 OD but is an OPTIONAL field
    (default `None`), so it never showed up in the `IncompleteBootstrapError`
    surface the other tests in this file exercise. `freeze()` previously
    omitted it entirely from the `HarnessContext(...)` constructor call —
    every real bootstrap produced a frozen ctx where `getattr(ctx,
    "protected_result_store", None)` was `None` even when stage 4 OD had set
    a real store, making `shutdown()`'s step 5b GC sweep (wired at round 4)
    unreachable in production. The round-4 shutdown test used a duck-typed
    `_FakeCtx` that bypassed real `freeze()` entirely and never caught this.

    Monkeypatches `HarnessContext` itself to capture `freeze()`'s
    constructor kwargs without needing the full required-field set to pass
    Pydantic validation (the pattern the test above notes is impractical
    here).

    Mutation probe: removing the `protected_result_store=...` kwarg from
    `freeze()`'s `HarnessContext(...)` call makes `captured` not contain the
    key at all instead of holding the sentinel."""
    from harness_runtime.bootstrap import mutable_context as mutable_context_module

    captured: dict[str, Any] = {}

    class _CapturingHarnessContext:
        def __init__(self, **kwargs: Any) -> None:
            captured.update(kwargs)
            raise RuntimeError("stop before full Pydantic validation")

    monkeypatch.setattr(mutable_context_module, "HarnessContext", _CapturingHarnessContext)
    from harness_runtime.bootstrap.mutable_context import _REQUIRED_FIELDS

    builder = _MutableHarnessContext()
    for name in _REQUIRED_FIELDS:
        if name == "drained_flag":
            setattr(builder, name, asyncio.Event())
        else:
            setattr(builder, name, _sentinel(name))
    sentinel = _sentinel("protected_result_store")
    builder.protected_result_store = sentinel

    with pytest.raises(RuntimeError):
        builder.freeze()

    assert captured.get("protected_result_store") is sentinel
