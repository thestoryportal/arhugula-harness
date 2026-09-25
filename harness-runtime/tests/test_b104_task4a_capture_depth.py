"""B-104 Task 4a: durable capture returns its own exact ref and records true depth.

Behavior under test (the real durable capture path, no stubbed store): the ref returned
by a durable capture is the ref of the record that call appended, even when a same-ID
sibling appends afterwards; the journaled depth is the depth the driver passed; and the
ref never enters the snapshot bytes the journal stores.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, cast

import pytest
from harness_core import PersonaTier, StepID, WorkloadClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import (
    DurableCapturedPause,
    WorkflowPauseReason,
)
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    execute_workflow,
)
from harness_cp.workflow_driver_types import RunStatus, StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_runtime.lifecycle.durable_pause_resume_protocol import DurablePauseResumeProtocol
from harness_runtime.lifecycle.journal_workflow_pause_store import JournalWorkflowPauseStore

_WF = "wf-b104-4a-shared-id"
_ANCHOR = "0" * 64


def _summary() -> StateSummary:
    return StateSummary(
        relevant_entries=(),
        summary_text="",
        summary_hash="0" * 64,
        idempotency_key=Identifier(""),
        external_references=(),
    )


def _store(tmp_path: Path) -> JournalWorkflowPauseStore:
    return JournalWorkflowPauseStore(journal_dir=tmp_path / "pj", tenant_id=None)


def _protocol(store: JournalWorkflowPauseStore) -> DurablePauseResumeProtocol:
    return DurablePauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=lambda: (_summary(), _ANCHOR),
        store=store,
    )


async def _capture(
    protocol: DurablePauseResumeProtocol, run_id: str, *, depth: int
) -> DurableCapturedPause:
    captured = await protocol.capture_pause_snapshot(
        _WF, run_id, 0, WorkflowPauseReason.EXPLICIT_OPERATOR, descent_depth=depth
    )
    assert isinstance(captured, DurableCapturedPause)
    return captured


@pytest.mark.asyncio
async def test_durable_capture_returns_the_exact_ref_of_the_record_it_wrote(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    captured = await _capture(_protocol(store), "run-1", depth=0)

    ref = captured.record_ref
    assert ref.workflow_id == _WF
    assert ref.run_id == "run-1"
    assert ref.record_count == 1
    assert ref.snapshot_hash == captured.snapshot.snapshot_hash
    at_ref = store.read_exact(ref)
    assert at_ref is not None
    assert at_ref.snapshot == captured.snapshot


@pytest.mark.asyncio
async def test_two_same_id_siblings_keep_their_own_distinct_refs(tmp_path: Path) -> None:
    """Both siblings share one (tenant, workflow_id) journal; the first ref must still
    name record 1 after the second sibling appended record 2 (never the latest)."""
    store = _store(tmp_path)
    protocol = _protocol(store)  # one shared instance, exactly as parent and children share it

    first = await _capture(protocol, "run-a", depth=1)
    second = await _capture(protocol, "run-b", depth=1)

    assert (first.record_ref.record_count, second.record_ref.record_count) == (1, 2)
    assert first.record_ref != second.record_ref
    first_at = store.read_exact(first.record_ref)
    second_at = store.read_exact(second.record_ref)
    assert first_at is not None and first_at.snapshot.run_id == "run-a"
    assert second_at is not None and second_at.snapshot.run_id == "run-b"


@pytest.mark.asyncio
@pytest.mark.parametrize("depth", [0, 1, 2])
async def test_journal_records_the_depth_the_caller_passed(tmp_path: Path, depth: int) -> None:
    """Root 0, child 1, grandchild 2 — a true numeric depth, not `None` or a boolean."""
    store = _store(tmp_path)
    captured = await _capture(_protocol(store), "run-1", depth=depth)

    at_ref = store.read_exact(captured.record_ref)
    assert at_ref is not None
    assert at_ref.depth == depth
    assert type(at_ref.depth) is int


@pytest.mark.asyncio
async def test_the_ref_is_not_part_of_the_journaled_snapshot_bytes(tmp_path: Path) -> None:
    store = _store(tmp_path)
    captured = await _capture(_protocol(store), "run-1", depth=1)

    journal_files = list((tmp_path / "pj").rglob("*.jsonl"))
    assert len(journal_files) == 1
    record: dict[str, Any] = json.loads(journal_files[0].read_text().splitlines()[0])
    # The journaled snapshot is exactly the snapshot the driver received: nothing about the
    # ref (whose digest covers this very line) can be inside the bytes it identifies.
    assert record["pause_snapshot"] == captured.snapshot.model_dump(mode="json")
    assert captured.record_ref.latest_digest not in json.dumps(record["pause_snapshot"])


@pytest.mark.asyncio
async def test_durable_capture_requires_an_explicit_depth(tmp_path: Path) -> None:
    protocol = _protocol(_store(tmp_path))
    with pytest.raises(TypeError):
        await protocol.capture_pause_snapshot(  # type: ignore[call-arg]
            _WF, "run-1", 0, WorkflowPauseReason.EXPLICIT_OPERATOR
        )


# ---------------------------------------------------------------------------
# Driver -> durable journal, end to end: the depth the driver was given is the depth
# journaled, and the paused RunResult carries the ref of that very record.
# ---------------------------------------------------------------------------


class _Ledger:
    def __init__(self) -> None:
        self.actor = Actor(actor_class=ActorClass.AGENT, actor_id="test-b104-4a")
        self.appends: list[Any] = []

    def append(self, payload: Any, write_key: Any) -> Any:
        self.appends.append((payload, write_key))
        return "appended"

    @property
    def is_genesis(self) -> bool:
        return not self.appends

    @property
    def entry_count(self) -> int:
        return len(self.appends)


class _Emitter:
    def emit(self, event_class: Any) -> None:
        return None


class _DriverCtx:
    def __init__(self, protocol: DurablePauseResumeProtocol) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = _Ledger()
        self.lifecycle_emitter = _Emitter()
        self.drained_flag = asyncio.Event()
        self.pause_requested_flag = asyncio.Event()
        self.pause_resume_protocol = protocol
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None
        self.inter_step_output_channel = None


class _Registry:
    def lookup(self, step_kind: StepKind) -> Any:
        if step_kind is StepKind.DECLARATIVE_STEP:
            return _FailingSecondStage()
        raise StepKindDispatcherNotBoundError(step_kind)


class _FailingSecondStage:
    def dispatch(self, binding: Any, step: WorkflowStep, *, step_context: Any = None) -> Any:
        if str(step.step_id) == "s1":
            raise RuntimeError("simulated stage failure")
        return {"stage": str(step.step_id)}


@pytest.mark.parametrize("depth", [0, 1, 2])
def test_driver_pause_journals_its_depth_and_returns_the_matching_ref(
    tmp_path: Path, depth: int
) -> None:
    store = _store(tmp_path)
    workflow_id = "wf-b104-4a-driver"
    manifest = WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.TEAM_BINDING,  # cascade_policy=pause
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.DECENTRALIZED_HANDOFF,
        layer_budgets=(),
        fallback_chain=FallbackChain(
            primary=ProviderCandidate(
                provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
            ),
            same_family=(),
            cross_family=(),
            terminal=None,
        ),
        hitl_placements=(),
        per_step_overrides={},
    )
    steps = [
        WorkflowStep(
            step_id=StepID(name),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"stage": name},
        )
        for name in ("s0", "s1")
    ]

    result = execute_workflow(
        manifest,
        steps,
        run_id="run-1",
        ctx=cast(DriverContext, _DriverCtx(_protocol(store))),
        default_model_binding=ModelBinding(provider="anthropic", model="claude-haiku-4-5"),
        step_dispatchers=cast(StepDispatcherRegistry, _Registry()),
        descent_depth=depth,
    )

    assert result.status is RunStatus.PAUSED
    ref = result.pause_record_ref
    assert ref is not None
    at_ref = store.read_exact(ref)
    assert at_ref is not None
    assert at_ref.depth == depth
    assert at_ref.snapshot == result.pause_snapshot
