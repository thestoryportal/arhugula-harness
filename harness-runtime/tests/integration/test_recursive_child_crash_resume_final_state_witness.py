"""[P1-a] discriminator witness — B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT (R-FS-1).

The #746 design finding feared a re-dispatched recursive SUB_AGENT child returns a
SUFFIX-ONLY ``final_state`` on crash-resume (the parent fold then silently corrupts the
aggregate). Its §8 HEAD-verified re-scope
(``.harness/b-fanout-crash-resume-maybe-ran-subagent-design-finding-v1.md``) hypothesises
that ``B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT`` (#766/#768) already closes that
result-fidelity gap for a ``SINGLE_THREADED_LINEAR`` child — but advisor flagged that the
#766 CP witnesses use a ``_FakeOutputStore`` that IGNORES ``run_key``, so they cannot
witness the load-bearing INTEGRATION fact: *does a REAL recursive child get an
``engine_output_store`` bound under its REUSED run_id with the committed prefix, presented
to the seeding on resume?* "Closed by construction" is the exact presence-not-correctness
move that got the #746 full build reverted.

This is that missing discriminator — the workspace's own open coverage residual
(``test_lifecycle_sub_agent_dispatch.py`` ``test_child_workflow_runner_opts_into_final_state_reconstruct``:
"the real-runner-THROUGH-execute_workflow integration ... needs a fully-bootstrapped
HarnessContext"). It is NON-VACUOUS because it:

  * routes through the REAL ``compose_child_workflow_runner`` -> ``execute_workflow``
    (NOT a mocked runner / spied ``execute_workflow`` — the #746 vacuity trap);
  * binds the REAL on-disk ``EngineOutputStore`` (keyed by ``run_idempotency_key`` — a
    ``run_key``-RESPECTING store, unlike the #766 fake), so the run_id threading is real:
    a broken thread -> the read finds nothing -> suffix-only;
  * PINS the child run_id (monkeypatching ``uuid.uuid4``) to simulate the E1
    deterministic-run_id the arc will build, so the crash-resume re-dispatch reuses the
    same ``run_idempotency_key`` and reaches the committed prefix.

The ``_record_engine_output`` producer auto-commits each step's output to
``ctx.engine_output_store`` regardless of dispatcher (``workflow_driver.py:694``), so an
echo dispatcher suffices for the [P1-a] RESULT-fidelity question (at-most-once / [P1-b] is
a separate concern). The WITH-store / WITHOUT-store pair is the discriminator: a real-store
recursive child reconstructs the FULL final_state; without it, suffix-only — the difference
IS the integration fact under test.
"""

from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import harness_runtime.lifecycle.child_workflow_runner as cwr
import pytest
from harness_core import PersonaTier, StepID, WorkloadClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_types import RunStatus, StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.lifecycle.child_workflow_runner import compose_child_workflow_runner
from harness_runtime.lifecycle.engine_output_store import EngineOutputStore, engine_output_dir_for
from harness_runtime.lifecycle.sub_agent_dispatch import compose_child_run_id_seed

_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-recursive-child")
_DEFAULT_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)

#: The pinned child run_id (simulates the E1 deterministic-run_id the arc will build) +
#: the child workflow_id. Both phases reuse them so the run_idempotency_key is stable.
_CHILD_RUN = "child-run-pinned-e1"
_CHILD_WF = "child-wf"
_ENTRY_VERSION = 1  # WorkflowManifestEntry default; the driver hashes str(entry_version).


def _run_key(run_id: str = _CHILD_RUN, workflow_id: str = _CHILD_WF) -> str:
    """Mirror ``_compute_run_idempotency_key`` (workflow_driver.py:604) — the driver
    passes ``extras=(str(manifest_entry.entry_version),)`` (line 1970)."""
    h = hashlib.sha256()
    h.update(run_id.encode("utf-8"))
    h.update(b"\x00")
    h.update(workflow_id.encode("utf-8"))
    h.update(b"\x00")
    h.update(str(_ENTRY_VERSION).encode("utf-8"))
    return h.hexdigest()


def _step_key(step_index: int) -> str:
    """Mirror ``_compute_step_idempotency_key`` (workflow_driver.py:626) for the linear
    (``branch_path=None``) path — the per-step key the ledger_reader is queried with."""
    h = hashlib.sha256()
    h.update(_run_key().encode("utf-8"))
    h.update(b"\x00")
    h.update(str(step_index).encode("utf-8"))
    return h.hexdigest()


def _seeded_step_key(run_id: str, step_index: int) -> str:
    """``_step_key`` for a SEED-derived child run_id (the E1-live path) — same derivation as
    ``_step_key`` but the run_key is computed from the seed (not the pinned ``_CHILD_RUN``)."""
    h = hashlib.sha256()
    h.update(_run_key(run_id=run_id).encode("utf-8"))
    h.update(b"\x00")
    h.update(str(step_index).encode("utf-8"))
    return h.hexdigest()


def _manifest() -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=_CHILD_WF,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.EVENT_SOURCED_REPLAY,
        topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _step(idx: int) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(f"step-{idx}"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={"index": idx},
    )


class _Ledger:
    """In-memory ``LedgerWriterLike``."""

    def __init__(self) -> None:
        self.actor = _ACTOR
        self.appends: list[tuple[Any, Any]] = []

    def append(self, payload: Any, write_key: Any) -> str:
        self.appends.append((payload, write_key))
        return "appended"

    @property
    def is_genesis(self) -> bool:
        return len(self.appends) == 0

    @property
    def entry_count(self) -> int:
        return len(self.appends)


class _Emitter:
    def __init__(self) -> None:
        self.emits: list[Any] = []

    def emit(self, event_class: Any) -> None:
        self.emits.append(event_class)


class _LedgerReader:
    """In-memory ``LedgerReaderLike`` reporting ``resume_at`` via materialized per-step
    keys (the #766 ``_FakeLedgerReader`` shape)."""

    def __init__(self, materialized: dict[str, int]) -> None:
        self._keys = materialized

    def read_by_idempotency_key(self, idempotency_key: Any, bounded_window: Any) -> Any:
        _ = bounded_window
        count = self._keys.get(str(idempotency_key), 0)

        class _Result:
            def __init__(self, n: int) -> None:
                self.entries = tuple(object() for _ in range(n))
                self.truncated = False
                self.next_position = None

        return _Result(count)


class _Echo:
    """Echo dispatcher; the driver's ``_record_engine_output`` does the durable store
    commit, so the dispatcher need not."""

    def __init__(self) -> None:
        self.dispatched: list[tuple[Any, WorkflowStep]] = []

    def dispatch(
        self, binding: Any, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        _ = step_context
        self.dispatched.append((binding, step))
        return {"step_id": str(step.step_id), "echoed": dict(step.step_payload)}


class _Registry:
    def __init__(self, dispatcher: _Echo) -> None:
        self._d = dispatcher

    def lookup(self, step_kind: StepKind) -> _Echo:
        _ = step_kind
        return self._d


class _Ctx:
    """Complete duck-typed mutable ``DriverContext`` (mirrors the #766 ``_FakeCtx`` field
    set) with a REAL ``engine_output_store`` + ``step_dispatchers`` bound — the runner reads
    ``ctx.step_dispatchers`` (child_workflow_runner.py:185) + ``execute_workflow`` reads
    ``ctx.engine_output_store`` for the reconstruct seed."""

    def __init__(
        self,
        *,
        ledger: _Ledger,
        reader: _LedgerReader,
        store: EngineOutputStore | None,
        dispatchers: _Registry,
    ) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = ledger
        self.lifecycle_emitter = _Emitter()
        self.ledger_reader = reader
        self.engine_output_store = store
        self.step_dispatchers = dispatchers
        self.tracer_provider = NoOpTracerProvider()
        self.drained_flag = asyncio.Event()
        self.pause_requested_flag = asyncio.Event()
        self.pause_resume_protocol = None
        self.validator_framework = None
        self.tenant_id = None
        self.inter_step_output_channel = None


def _pin_child_run_id(monkeypatch: Any) -> None:
    """Pin the child run_id so the crash-resume re-dispatch reuses the
    ``run_idempotency_key`` (simulating the E1 deterministic-run_id the arc will build).
    The runner derives ``child_run_id = uuid.uuid4().hex`` on a crash-resume
    (``pause_snapshot_input is None``; child_workflow_runner.py:153-154)."""
    monkeypatch.setattr(cwr.uuid, "uuid4", lambda: SimpleNamespace(hex=_CHILD_RUN))


def _resume_ctx(store: EngineOutputStore | None) -> _Ctx:
    """A child crash-resume ctx: 2 steps materialized (``resume_at == 2``) so the resume
    seeds the committed prefix ``[0, 2)`` and re-dispatches only step-2."""
    reader = _LedgerReader({_step_key(0): 1, _step_key(1): 1})
    return _Ctx(ledger=_Ledger(), reader=reader, store=store, dispatchers=_Registry(_Echo()))


def test_recursive_child_crash_resume_reconstructs_full_final_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """[P1-a] DISCRIMINATOR (the re-scope hypothesis CONFIRMED if GREEN) — a REAL recursive
    child routed through ``compose_child_workflow_runner`` -> ``execute_workflow`` over a REAL
    ``run_key``-respecting ``EngineOutputStore`` holding the committed prefix, crash-resumed
    with the child run_id PINNED, reconstructs its COMPLETE ``final_state``
    {step-0, step-1, step-2} — NOT the suffix-only {step-2} the #746 finding feared. The
    prefix is reconstructed from the store (seeded before the loop), only step-2 is
    re-dispatched."""
    store = EngineOutputStore(journal_dir=engine_output_dir_for(tmp_path))
    run_key = _run_key()
    # The committed prefix the pre-crash child durably recorded (the producer keys by
    # run_idempotency_key; a REUSED run_id -> the SAME key -> this prefix is found).
    store.record(run_key, 0, "step-0", {"out": "v0"})
    store.record(run_key, 1, "step-1", {"out": "v1"})

    _pin_child_run_id(monkeypatch)
    ctx = _resume_ctx(store)
    runner = compose_child_workflow_runner(cast(Any, ctx))
    result = runner(
        workflow_id=_CHILD_WF,
        manifest_entry=_manifest(),
        steps=[_step(0), _step(1), _step(2)],
        handoff_context=cast(Any, None),  # not forwarded to execute_workflow
        descent=cast(Any, None),  # not forwarded to execute_workflow
        default_model_binding=_DEFAULT_BINDING,
        pause_snapshot_input=None,  # CRASH-resume (not a pause-resume)
    )

    assert result.status is RunStatus.SUCCESS
    assert result.final_state is not None
    # [P1-a] is CLOSED for the linear child: FULL terminal state, not suffix-only {step-2}.
    assert set(result.final_state.keys()) == {"step-0", "step-1", "step-2"}
    assert result.final_state["step-0"] == {"out": "v0"}
    assert result.final_state["step-1"] == {"out": "v1"}
    # The committed prefix was reconstructed from the store, NOT re-dispatched.
    dispatcher = ctx.step_dispatchers.lookup(StepKind.INFERENCE_STEP)
    assert len(dispatcher.dispatched) == 1
    assert str(dispatcher.dispatched[0][1].step_id) == "step-2"


_PARENT_KEY = "parent-idem-key-worker-branch-0"


def test_recursive_child_crash_resume_e1_live_seed_reconstructs_full_final_state(
    tmp_path: Path,
) -> None:
    """E1-LIVE full-chain witness (B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT) — the discriminator
    advisor #3 flagged: the #770 sibling PINS the child run_id (monkeypatching ``uuid.uuid4``) to
    SIMULATE E1. This one uses the REAL ``compose_child_run_id_seed`` (the deterministic E1 seed the
    arc builds) as ``child_run_id_seed`` — NO uuid pin — and proves the seed-derived run_id drives
    the ``run_idempotency_key`` -> committed-prefix -> reconstruction chain through the REAL runner.

    The seed is a PURE function of (parent_idempotency_key, child_workflow_id), so a parent-crash
    re-dispatch RE-DERIVES the SAME id (asserted directly) -> the child auto-resumes from the durable
    store under the stable key -> the resumed ``final_state`` reconstructs the COMPLETE terminal
    state {step-0, step-1, step-2}, only step-2 re-dispatched. This closes the half-mechanism gap:
    #770 proved reconstruction GIVEN a stable id; this proves the E1 seed PRODUCES that stable id
    through the real runner."""
    seed = compose_child_run_id_seed(_PARENT_KEY, _CHILD_WF)
    # The seed is deterministic — a re-dispatch re-derives it (the recovery prerequisite).
    assert compose_child_run_id_seed(_PARENT_KEY, _CHILD_WF) == seed
    # A different worker / child workflow_id -> a distinct seed (per-branch / per-child isolation).
    assert compose_child_run_id_seed("parent-idem-key-worker-branch-1", _CHILD_WF) != seed
    assert compose_child_run_id_seed(_PARENT_KEY, "other-child-wf") != seed

    store = EngineOutputStore(journal_dir=engine_output_dir_for(tmp_path))
    run_key = _run_key(run_id=seed)
    store.record(run_key, 0, "step-0", {"out": "v0"})
    store.record(run_key, 1, "step-1", {"out": "v1"})

    # resume ctx keyed on the SEED-derived run_key (no uuid pin — the seed IS the id).
    reader = _LedgerReader({_seeded_step_key(seed, 0): 1, _seeded_step_key(seed, 1): 1})
    ctx = _Ctx(ledger=_Ledger(), reader=reader, store=store, dispatchers=_Registry(_Echo()))
    runner = compose_child_workflow_runner(cast(Any, ctx))
    result = runner(
        workflow_id=_CHILD_WF,
        manifest_entry=_manifest(),
        steps=[_step(0), _step(1), _step(2)],
        handoff_context=cast(Any, None),
        descent=cast(Any, None),
        default_model_binding=_DEFAULT_BINDING,
        pause_snapshot_input=None,  # CRASH-resume (not a pause-resume)
        child_run_id_seed=seed,  # E1-LIVE: the deterministic seed, NOT a pinned uuid
    )

    assert result.status is RunStatus.SUCCESS
    assert result.final_state is not None
    assert set(result.final_state.keys()) == {"step-0", "step-1", "step-2"}
    assert result.final_state["step-0"] == {"out": "v0"}
    assert result.final_state["step-1"] == {"out": "v1"}
    dispatcher = ctx.step_dispatchers.lookup(StepKind.INFERENCE_STEP)
    assert len(dispatcher.dispatched) == 1
    assert str(dispatcher.dispatched[0][1].step_id) == "step-2"


def test_recursive_child_crash_resume_without_store_degrades_to_suffix_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """NEGATIVE CONTROL (RED-without-the-store) — the SAME recursive child crash-resume with
    NO ``engine_output_store`` bound degrades to the suffix-only ``final_state`` {step-2} (the
    pre-#766 behavior the #746 finding feared). Proves the real-store reconstruction through
    the real child runner is the ONLY source of the full final_state — the integration fact
    the #766 ``run_key``-ignoring fake could not witness."""
    _ = tmp_path
    _pin_child_run_id(monkeypatch)
    ctx = _resume_ctx(store=None)  # NO store bound
    runner = compose_child_workflow_runner(cast(Any, ctx))
    result = runner(
        workflow_id=_CHILD_WF,
        manifest_entry=_manifest(),
        steps=[_step(0), _step(1), _step(2)],
        handoff_context=cast(Any, None),
        descent=cast(Any, None),
        default_model_binding=_DEFAULT_BINDING,
        pause_snapshot_input=None,
    )

    assert result.status is RunStatus.SUCCESS
    assert result.final_state is not None
    assert set(result.final_state.keys()) == {"step-2"}
