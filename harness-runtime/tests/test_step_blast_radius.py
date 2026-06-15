"""U-RT-115 (G1-blast) — `resolve_step_blast_radius` per-step-kind resolver tests.

Per runtime plan v2.44 §2.3 U-RT-115 acceptance criteria + design §3.2 table.
The resolver is a pure function (no IO beyond the registry read); these tests
exercise each step-kind branch + the fail-safe raise directly with a minimal
stub `ctx`.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from harness_as import BlastRadiusTier, SandboxTier
from harness_as.tool_contract import ToolContract
from harness_cp.workflow_driver_types import StepKind, WorkflowStep
from harness_runtime.lifecycle.step_blast_radius import (
    StepBlastRadiusResolutionError,
    make_step_blast_radius_resolver,
    resolve_step_blast_radius,
)


def _tool(blast: BlastRadiusTier) -> ToolContract:
    return ToolContract(
        name="t",
        description="t",
        input_schema={},
        output_schema={},
        minimum_tier=SandboxTier.TIER_1_PROCESS,
        blast_radius_tier=blast,
    )


def _step(kind: StepKind, payload: dict | None = None) -> WorkflowStep:
    return WorkflowStep(step_id="step-1", step_kind=kind, step_payload=payload or {})


class _Registry:
    """Minimal dict-backed `tool_registry` exposing `.get`."""

    def __init__(self, contracts: dict[str, ToolContract]) -> None:
        self._contracts = contracts

    def get(self, tool_id: str) -> ToolContract | None:
        return self._contracts.get(tool_id)


def _ctx_with_registry(contracts: dict[str, ToolContract]) -> SimpleNamespace:
    """Stub `ctx` exposing `mcp_client_host.tool_registry` (runtime authority)."""
    return SimpleNamespace(
        mcp_client_host=SimpleNamespace(tool_registry=_Registry(contracts)),
        tool_contracts=None,
    )


def _ctx_with_contracts(contracts: dict[str, ToolContract]) -> SimpleNamespace:
    """Stub `ctx` exposing only `tool_contracts` (stage-2 registry fallback)."""
    return SimpleNamespace(mcp_client_host=None, tool_contracts=contracts)


_EMPTY_CTX = _ctx_with_registry({})


# --- READ_ONLY step kinds (no external side effect) -------------------------


@pytest.mark.parametrize(
    "kind",
    [StepKind.INFERENCE_STEP, StepKind.DECLARATIVE_STEP, StepKind.HITL_STEP],
)
def test_read_only_kinds_resolve_read_only(kind: StepKind) -> None:
    # A provider chat-completion / declarative / HITL step has no external side
    # effect — side effects come from downstream TOOL/SUB_AGENT steps (each
    # independently gated). Design §3.2.
    assert resolve_step_blast_radius(_step(kind), _EMPTY_CTX) is BlastRadiusTier.READ_ONLY


def test_sub_agent_dispatch_resolves_child_ceiling_read_only() -> None:
    # A sub-agent's blast radius (from the dispatching parent's gate view) is the
    # C-CP-12 §12.1 default-downgrade child ceiling — parent-independent READ_ONLY.
    step = _step(StepKind.SUB_AGENT_DISPATCH)
    assert resolve_step_blast_radius(step, _EMPTY_CTX) is BlastRadiusTier.READ_ONLY


# --- TOOL_STEP: ToolContract.blast_radius_tier lookup ----------------------


def test_tool_step_resolves_contract_blast_radius_via_registry() -> None:
    # The tool IS the side-effecting action; its contract declares the blast
    # radius. A LOCAL_MUTATION-tier tool asserts LOCAL_MUTATION (the AC example).
    ctx = _ctx_with_registry({"writer": _tool(BlastRadiusTier.LOCAL_MUTATION)})
    step = _step(StepKind.TOOL_STEP, {"tool_id": "writer"})
    assert resolve_step_blast_radius(step, ctx) is BlastRadiusTier.LOCAL_MUTATION


def test_tool_step_resolves_external_irreversible_tool() -> None:
    ctx = _ctx_with_registry({"deploy": _tool(BlastRadiusTier.EXTERNAL_IRREVERSIBLE)})
    step = _step(StepKind.TOOL_STEP, {"tool_id": "deploy"})
    assert resolve_step_blast_radius(step, ctx) is BlastRadiusTier.EXTERNAL_IRREVERSIBLE


def test_tool_step_resolves_via_tool_contracts_fallback() -> None:
    # When mcp_client_host is absent, fall back to ctx.tool_contracts (the
    # stage-2 registered contracts).
    ctx = _ctx_with_contracts({"reader": _tool(BlastRadiusTier.READ_ONLY)})
    step = _step(StepKind.TOOL_STEP, {"tool_id": "reader"})
    assert resolve_step_blast_radius(step, ctx) is BlastRadiusTier.READ_ONLY


# --- Fail-safe: unresolvable TOOL_STEP raises (NOT silent READ_ONLY) --------


def test_tool_step_missing_tool_id_raises() -> None:
    step = _step(StepKind.TOOL_STEP, {})  # no tool_id
    with pytest.raises(StepBlastRadiusResolutionError):
        resolve_step_blast_radius(step, _EMPTY_CTX)


def test_tool_step_non_str_tool_id_raises() -> None:
    step = _step(StepKind.TOOL_STEP, {"tool_id": 42})
    with pytest.raises(StepBlastRadiusResolutionError):
        resolve_step_blast_radius(step, _EMPTY_CTX)


def test_tool_step_unregistered_tool_raises_fail_safe() -> None:
    # Contrasting-baseline (AC): an unclassifiable action must gate, never
    # auto-approve via a silent READ_ONLY default.
    ctx = _ctx_with_registry({"known": _tool(BlastRadiusTier.READ_ONLY)})
    step = _step(StepKind.TOOL_STEP, {"tool_id": "unknown"})
    with pytest.raises(StepBlastRadiusResolutionError):
        resolve_step_blast_radius(step, ctx)


# --- The closure factory (stage-5 binding precedent) ------------------------


def test_make_resolver_closure_resolves_via_captured_ctx() -> None:
    ctx = _ctx_with_registry({"writer": _tool(BlastRadiusTier.LOCAL_MUTATION)})
    resolver = make_step_blast_radius_resolver(ctx)  # type: ignore[arg-type]
    assert resolver(_step(StepKind.INFERENCE_STEP)) is BlastRadiusTier.READ_ONLY
    assert (
        resolver(_step(StepKind.TOOL_STEP, {"tool_id": "writer"})) is BlastRadiusTier.LOCAL_MUTATION
    )
