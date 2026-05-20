"""U-RT-35 — `materialize_cp_is_wiring_stage` + `RuntimeCpIsWiring` tests.

ACs per Phase 2 Session 7 L7 §12.3 (CP → IS — PARTIAL-LAND, 1 of 17 edges):

AC #1 (LANDED) — U-CP-34 sibling-ledger seam: `emit_sibling_ledger_entry`
composes via CP `construct_sibling_ledger_entry` and appends to IS chain;
chain_verification passes; idempotent on the 5-tuple per C-CP-15.1.

ACs #2 + #3 (STRUCK; routed to Class 1 at
`.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md`) — the remaining
8 CP source units lack materialized composers (or have shape-divergent
composers like U-CP-14's CPAuditLedgerEntry); bridging at runtime would
be X-AL-3 silent design extension.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict

import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_core.workload_class import WorkloadClass
from harness_cp.cp_shared_types import ActorIdentity
from harness_cp.topology_pattern import TopologyPattern
from harness_is.chain_verification import VerificationStatus, verify_chain
from harness_is.path_class_registry import PathClass
from harness_is.path_resolver import PathResolver
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_is.state_ledger_write import WriteResult, read_ledger
from harness_runtime.config.path_bindings import build_path_binding
from harness_runtime.lifecycle.cp_is_wiring import (
    CpIsWiringBindError,
    CpIsWiringStage,
    RuntimeCpIsWiring,
    materialize_cp_is_wiring_stage,
)
from harness_runtime.lifecycle.state_ledger import (
    LedgerWriter,
    materialize_state_ledger,
)
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)

# ---------------------------------------------------------------------------
# Fixtures + helpers.
# ---------------------------------------------------------------------------


def _resolver_for(tmp_path: Path) -> PathResolver:
    config = PathBindingConfig(
        raw_entries=(
            {
                "path_class": PathClass.STATE_LEDGER,
                "workflow_class": WorkloadClass.SOFTWARE_ENGINEERING,
                "deployment_surface": DeploymentSurface.LOCAL_DEVELOPMENT,
                "path": str(tmp_path / "state.jsonl"),
            },
        ),
    )
    return PathResolver(build_path_binding(config))


def _ledger_writer(tmp_path: Path) -> LedgerWriter:
    return materialize_state_ledger(
        _resolver_for(tmp_path),
        workflow_class=WorkloadClass.SOFTWARE_ENGINEERING,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-runtime"),
    )


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )


def _wiring(tmp_path: Path) -> RuntimeCpIsWiring:
    stage = materialize_cp_is_wiring_stage(_config(tmp_path), _ledger_writer(tmp_path))
    return stage.wiring


class _SiblingKwargs(TypedDict):
    parent_action_id: str
    sibling_thread_id: str
    step_index: int
    tool: str
    canonical_args: str
    sibling_agent_identity: ActorIdentity
    timestamp: datetime


def _sibling_kwargs(
    *,
    parent_action_id: str = "parent-action-0",
    sibling_thread_id: str = "sibling-thread-1",
    step_index: int = 0,
    tool: str = "Bash",
    canonical_args: str = '{"cmd":"echo hi"}',
    timestamp: datetime | None = None,
) -> _SiblingKwargs:
    return {
        "parent_action_id": parent_action_id,
        "sibling_thread_id": sibling_thread_id,
        "step_index": step_index,
        "tool": tool,
        "canonical_args": canonical_args,
        "sibling_agent_identity": ActorIdentity("agent-1"),
        "timestamp": timestamp or datetime(2026, 5, 19, 12, 0, 0, tzinfo=UTC),
    }


# ---------------------------------------------------------------------------
# Composer + shape.
# ---------------------------------------------------------------------------


def test_composer_returns_stage(tmp_path: Path) -> None:
    stage = materialize_cp_is_wiring_stage(_config(tmp_path), _ledger_writer(tmp_path))
    assert isinstance(stage, CpIsWiringStage)
    assert isinstance(stage.wiring, RuntimeCpIsWiring)


def test_stage_is_frozen(tmp_path: Path) -> None:
    stage = materialize_cp_is_wiring_stage(_config(tmp_path), _ledger_writer(tmp_path))
    with pytest.raises(AttributeError):
        stage.wiring = stage.wiring  # type: ignore[misc]


def test_wiring_is_frozen(tmp_path: Path) -> None:
    wiring = _wiring(tmp_path)
    with pytest.raises(AttributeError):
        wiring.ledger_writer = wiring.ledger_writer  # type: ignore[misc]


def test_bind_error_typed() -> None:
    err = CpIsWiringBindError("test")
    assert isinstance(err, Exception)


# ---------------------------------------------------------------------------
# AC #1 (LANDED) — U-CP-34 → U-IS-11 sibling-ledger seam.
# ---------------------------------------------------------------------------


def test_emit_returns_appended_on_fresh_sibling(tmp_path: Path) -> None:
    wiring = _wiring(tmp_path)
    result = wiring.emit_sibling_ledger_entry(**_sibling_kwargs())
    assert result is WriteResult.APPENDED


def test_emit_persists_entry_in_ledger(tmp_path: Path) -> None:
    wiring = _wiring(tmp_path)
    wiring.emit_sibling_ledger_entry(**_sibling_kwargs())
    entries = read_ledger(wiring.ledger_writer.handle)
    assert len(entries) == 1


def test_post_emit_chain_verification_passes(tmp_path: Path) -> None:
    wiring = _wiring(tmp_path)
    wiring.emit_sibling_ledger_entry(**_sibling_kwargs())
    entries = read_ledger(wiring.ledger_writer.handle)
    assert verify_chain(entries).status is VerificationStatus.VALID


def test_emit_actor_class_is_sub_agent(tmp_path: Path) -> None:
    """The sibling composer pins actor_class to SUB_AGENT (per C-CP-15.1)."""
    wiring = _wiring(tmp_path)
    wiring.emit_sibling_ledger_entry(**_sibling_kwargs())
    [persisted] = read_ledger(wiring.ledger_writer.handle)
    assert persisted.actor.actor_class is ActorClass.SUB_AGENT
    assert persisted.actor.actor_id == "agent-1"


def test_action_id_is_structural_concat(tmp_path: Path) -> None:
    """`action_id = ParentActionID || sibling_thread_id || step_index` (§15.1)."""
    wiring = _wiring(tmp_path)
    wiring.emit_sibling_ledger_entry(
        **_sibling_kwargs(
            parent_action_id="parent-X",
            sibling_thread_id="thread-Y",
            step_index=42,
        )
    )
    [persisted] = read_ledger(wiring.ledger_writer.handle)
    assert persisted.action_id == "parent-Xthread-Y42"


# ---------------------------------------------------------------------------
# Idempotency on the 5-tuple per C-CP-15.1 + C-IS-07 §7.1.
# ---------------------------------------------------------------------------


def test_replay_same_5tuple_is_idempotent_noop(tmp_path: Path) -> None:
    wiring = _wiring(tmp_path)
    kwargs = _sibling_kwargs()
    first = wiring.emit_sibling_ledger_entry(**kwargs)
    second = wiring.emit_sibling_ledger_entry(**kwargs)
    assert first is WriteResult.APPENDED
    assert second is WriteResult.IDEMPOTENT_NOOP
    assert len(read_ledger(wiring.ledger_writer.handle)) == 1


def test_distinct_5tuples_yield_distinct_entries(tmp_path: Path) -> None:
    wiring = _wiring(tmp_path)
    # Differ on one component of the 5-tuple at a time.
    wiring.emit_sibling_ledger_entry(**_sibling_kwargs(parent_action_id="p-1"))
    wiring.emit_sibling_ledger_entry(**_sibling_kwargs(parent_action_id="p-2"))
    wiring.emit_sibling_ledger_entry(**_sibling_kwargs(sibling_thread_id="t-2"))
    wiring.emit_sibling_ledger_entry(**_sibling_kwargs(step_index=99))
    wiring.emit_sibling_ledger_entry(**_sibling_kwargs(tool="Read"))
    wiring.emit_sibling_ledger_entry(**_sibling_kwargs(canonical_args="{}"))
    entries = read_ledger(wiring.ledger_writer.handle)
    assert len(entries) == 6
    keys = {e.idempotency_key for e in entries}
    assert len(keys) == 6


# ---------------------------------------------------------------------------
# Chain integrity across many sequential emissions.
# ---------------------------------------------------------------------------


def test_chain_integrity_across_50_sibling_emissions(tmp_path: Path) -> None:
    wiring = _wiring(tmp_path)
    base = datetime(2026, 5, 19, 12, 0, 0, tzinfo=UTC)
    for i in range(50):
        result = wiring.emit_sibling_ledger_entry(
            **_sibling_kwargs(
                sibling_thread_id=f"thread-{i}",
                step_index=i,
                timestamp=base.replace(microsecond=i),
            )
        )
        assert result is WriteResult.APPENDED
    entries = read_ledger(wiring.ledger_writer.handle)
    assert len(entries) == 50
    assert verify_chain(entries).status is VerificationStatus.VALID
