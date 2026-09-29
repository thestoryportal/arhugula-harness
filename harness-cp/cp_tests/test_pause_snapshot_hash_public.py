"""B-104 Task 5a F3: the Control Plane owns ONE public verifier for a pause snapshot's hash.

Runtime consumers (the claim store) must not import `_compute_snapshot_hash` or re-list its
eleven inputs: a re-listed copy silently misses the next hashed field. These tests pin the public
`compute_pause_snapshot_hash` / `verify_pause_snapshot_hash` against the byte behaviour the
private function already has (literal golden vectors), the real capture path, the explicit
covered/uncovered field inventory, and the malformed-data boundary. Provider-free.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest
from harness_core import JournalRecordRef
from harness_cp import pause_resume_protocol as prp
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol import PauseResumeProtocol
from harness_cp.pause_resume_protocol_types import (
    EffectFenceResumeState,
    EvaluatorOptimizerResumeState,
    EvaluatorOptimizerStepResumeState,
    FanOutBranchResumeState,
    FanOutResumeState,
    HandoffResumeState,
    HandoffStageResumeState,
    MaterialDiffPolicy,
    OrchestratorEffectFencePausedResumeState,
    PausedChildBranchResumeState,
    PauseSnapshot,
    PeerFanOutResumeState,
    WorkflowPauseReason,
)
from harness_is.state_ledger_entry_schema import Identifier
from pydantic import ValidationError

_SUMMARY = StateSummary(
    relevant_entries=(),
    summary_text="state",
    summary_hash="0" * 64,
    idempotency_key=Identifier("idem-1"),
    external_references=(),
)
_ANCHOR = "a" * 64
_STRICT = MaterialDiffPolicy.STRICT

_HASHED = frozenset(
    {
        "workflow_id",
        "run_id",
        "step_index",
        "state_summary",
        "fan_out_resume",
        "peer_fan_out_resume",
        "handoff_resume",
        "evaluator_optimizer_resume",
        "effect_fence_resume",
        "orchestrator_effect_fence_resume",
        "hitl_gate_config_hash",
    }
)
_NOT_HASHED = frozenset({"snapshot_hash", "created_at", "pause_reason", "state_ledger_anchor"})


def _branch(index: int) -> FanOutBranchResumeState:
    return FanOutBranchResumeState(
        branch_index=index, step_id=f"w{index}", terminal_status="completed", output={"k": index}
    )


def _bare(workflow_id: str, run_id: str) -> dict[str, Any]:
    return {
        "workflow_id": workflow_id,
        "run_id": run_id,
        "step_index": 0,
        "state_summary": _SUMMARY,
    }


def _snapshot(common: dict[str, Any], snapshot_hash: str, **carriers: Any) -> PauseSnapshot:
    return PauseSnapshot(
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        snapshot_hash=snapshot_hash,
        created_at=1_700_000_000_000,
        state_ledger_anchor=_ANCHOR,
        **common,
        **carriers,
    )


def _ref(child: PauseSnapshot, digest: str) -> JournalRecordRef:
    return JournalRecordRef(
        tenant=None,
        workflow_id=child.workflow_id,
        run_id=child.run_id,
        record_count=1,
        latest_digest=digest * 64,
        snapshot_hash=child.snapshot_hash,
    )


def _paused_child_branch(ref_digest: str | None) -> PausedChildBranchResumeState:
    child = _snapshot(_bare("wf-c", "run-c"), "c" * 64)
    return PausedChildBranchResumeState(
        branch_index=0,
        step_id="w0",
        child_workflow_id="wf-c",
        child_snapshot=child,
        child_record_ref=None if ref_digest is None else _ref(child, ref_digest),
    )


def _carriers() -> dict[str, dict[str, Any]]:
    """Every hashed carrier shape, keyed by a stable name (the golden-vector keys)."""
    return {
        "linear": {},
        "hitl_gate": {"hitl_gate_config_hash": "d" * 64},
        "fan_out": {
            "fan_out_resume": FanOutResumeState(
                orchestrator_output={"r": "o"},
                orchestrator_step_id="orch",
                branches=(_branch(0), _branch(1)),
                worker_count=2,
            )
        },
        "fan_out_child_no_ref": {
            "fan_out_resume": FanOutResumeState(
                orchestrator_output={"r": "o"},
                orchestrator_step_id="orch",
                branches=(),
                worker_count=1,
                paused_child_branches=(_paused_child_branch(None),),
            )
        },
        "fan_out_child_with_ref": {
            "fan_out_resume": FanOutResumeState(
                orchestrator_output={"r": "o"},
                orchestrator_step_id="orch",
                branches=(),
                worker_count=1,
                paused_child_branches=(_paused_child_branch("e"),),
            )
        },
        "peer_fan_out": {
            "peer_fan_out_resume": PeerFanOutResumeState(branches=(_branch(0),), branch_count=1)
        },
        "peer_child_with_ref": {
            "peer_fan_out_resume": PeerFanOutResumeState(
                branches=(),
                branch_count=1,
                paused_child_branches=(_paused_child_branch("f"),),
            )
        },
        "handoff": {
            "handoff_resume": HandoffResumeState(
                completed_stages=(
                    HandoffStageResumeState(stage_index=0, step_id="s0", output={"o": 1}),
                ),
                stage_count=2,
            )
        },
        "evaluator_optimizer": {
            "evaluator_optimizer_resume": EvaluatorOptimizerResumeState(
                completed_steps=(
                    EvaluatorOptimizerStepResumeState(
                        entry_index=0,
                        declared_step_index=0,
                        step_id="gen",
                        output={"text": "draft"},
                    ),
                )
            )
        },
        "effect_fence": {"effect_fence_resume": EffectFenceResumeState(idempotency_key="k1")},
        "orchestrator_effect_fence": {
            "orchestrator_effect_fence_resume": OrchestratorEffectFencePausedResumeState(
                idempotency_key="k2", step_id="orch", step_kind="inference"
            )
        },
    }


def _captured(carriers: dict[str, Any]) -> PauseSnapshot:
    """The REAL capture path: the hash the driver stamps on a snapshot."""
    protocol = PauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=lambda: (_SUMMARY, _ANCHOR),
    )
    return asyncio.run(
        protocol.capture_pause_snapshot(
            "wf-p",
            "run-p",
            0,
            WorkflowPauseReason.EXPLICIT_OPERATOR,
            descent_depth=0,
            **carriers,
        )
    ).snapshot


# Literal hashes produced by the UNMODIFIED private function at CP v1.123 (555dbff). Any byte
# change to the canonical serialization changes these and must be a deliberate, reviewed act.
GOLDEN: dict[str, str] = {
    "linear": "9625bd1624759f929d45e1455237704cfa1c7f9eb8186692b896aae3679d0394",
    "hitl_gate": "40bf4fbfb400514582322cd5869448881d4ff4c0b1bf4c138d39ea1e6907a09f",
    "fan_out": "2a0b0cc37ce268deb78ac82dd248a91583aa93ec85366c46e10713b23becf172",
    "fan_out_child_no_ref": "1027499110347566670391b2213a9b6e6cc48179af1de85adeea5c79b36ec135",
    "fan_out_child_with_ref": "048397ec3420cfe4fe675dfecf15d034851798893c0556684f1f9bd95bad769e",
    "peer_fan_out": "3f76933a6928f644c744315fb7a6dc5e80f6bb25c57e40781346ca28e79f0425",
    "peer_child_with_ref": "af89cf30b949d59985bb2ccdd2513fdb6c86a41f7586c6a0b4c64d62f79dcd01",
    "handoff": "e5bf673fd39152e6047cce11ab06fe9e8ecd516511c92de2e7ab5df7f71b7079",
    "evaluator_optimizer": "ca893c6ed0a543eceeee01b80b61c1c5dc40a9deb0fd0cfde303b91c3c347995",
    "effect_fence": "cdd0c0c29c4813839f33f1a2569142450c072c873b30eb639103ec7c8d6cfdc1",
    "orchestrator_effect_fence": "002a98b516d21f1eb78b6f5e0b7846d5104abe779648d33dd600590503a2fa4a",
}
_NAMES = list(GOLDEN)


def _compute(snapshot: PauseSnapshot) -> str:
    return prp.compute_pause_snapshot_hash(snapshot)  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue]


def _verify(snapshot: PauseSnapshot) -> bool:
    return prp.verify_pause_snapshot_hash(snapshot)  # type: ignore[attr-defined]  # pyright: ignore[reportAttributeAccessIssue]


def test_the_public_verifier_is_importable_from_the_protocol_module() -> None:
    from harness_cp.pause_resume_protocol import (  # noqa: F401
        compute_pause_snapshot_hash,
        verify_pause_snapshot_hash,
    )


# --- one byte behaviour: golden vectors, the real capture path and the private function ---------


@pytest.mark.parametrize("name", _NAMES)
def test_compute_matches_the_literal_golden_vector_and_the_capture_path(name: str) -> None:
    snapshot = _captured(_carriers()[name])

    assert snapshot.snapshot_hash == GOLDEN[name]  # the capture path itself did not move
    assert _compute(snapshot) == GOLDEN[name]
    assert _verify(snapshot) is True


@pytest.mark.parametrize("name", _NAMES)
def test_compute_equals_the_private_function_over_the_same_inputs(name: str) -> None:
    carriers = _carriers()[name]
    snapshot = _captured(carriers)

    assert _compute(snapshot) == prp._compute_snapshot_hash(  # pyright: ignore[reportPrivateUsage]
        workflow_id="wf-p", run_id="run-p", step_index=0, state_summary=_SUMMARY, **carriers
    )


def test_attempt_resume_still_accepts_a_captured_snapshot_and_refuses_a_tampered_one() -> None:
    protocol = PauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=lambda: (_SUMMARY, _ANCHOR),
    )
    snapshot = _captured(_carriers()["fan_out_child_with_ref"])
    assert (
        asyncio.run(protocol.attempt_resume(snapshot, material_diff_policy=_STRICT)).resumed is True
    )

    tampered = snapshot.model_copy(update={"step_index": 1})
    result = asyncio.run(protocol.attempt_resume(tampered, material_diff_policy=_STRICT))
    assert result.resumed is False and result.fail_class == prp.CP_FAIL_PAUSE_SNAPSHOT_CORRUPTION


# --- coverage is explicit: adding a PauseSnapshot field forces a classification -----------------


def test_every_snapshot_field_is_classified_hashed_or_not_hashed() -> None:
    hashed = frozenset(prp._HASH_INPUT_FIELDS)  # pyright: ignore[reportPrivateUsage]

    assert hashed == _HASHED and len(prp._HASH_INPUT_FIELDS) == 11  # pyright: ignore[reportPrivateUsage]
    assert not (_HASHED & _NOT_HASHED)
    assert set(PauseSnapshot.model_fields) == _HASHED | _NOT_HASHED


_MUTATIONS: dict[str, Any] = {
    "workflow_id": "wf-other",
    "run_id": "run-other",
    "step_index": 3,
    "state_summary": _SUMMARY.model_copy(update={"summary_text": "other"}),
    "hitl_gate_config_hash": "9" * 64,
    "effect_fence_resume": EffectFenceResumeState(idempotency_key="k9"),
    "orchestrator_effect_fence_resume": OrchestratorEffectFencePausedResumeState(
        idempotency_key="k9", step_id="orch", step_kind="inference"
    ),
    "handoff_resume": HandoffResumeState(completed_stages=(), stage_count=9),
    "evaluator_optimizer_resume": EvaluatorOptimizerResumeState(completed_steps=()),
    "fan_out_resume": FanOutResumeState(
        orchestrator_output={"r": "changed"},
        orchestrator_step_id="orch",
        branches=(),
        worker_count=1,
    ),
    "peer_fan_out_resume": PeerFanOutResumeState(branches=(), branch_count=9),
}


@pytest.mark.parametrize("field", sorted(_HASHED))
def test_changing_any_hashed_field_fails_verification(field: str) -> None:
    snapshot = _captured({"hitl_gate_config_hash": "d" * 64})

    changed = snapshot.model_copy(update={field: _MUTATIONS[field]})

    assert _verify(snapshot) is True
    assert _verify(changed) is False


@pytest.mark.parametrize("name", ["fan_out_child_with_ref", "peer_child_with_ref"])
def test_a_nested_paused_child_ref_and_child_output_are_covered(name: str) -> None:
    snapshot = _captured(_carriers()[name])
    key = "fan_out_resume" if name.startswith("fan_out") else "peer_fan_out_resume"
    carrier = getattr(snapshot, key)
    branch = carrier.paused_child_branches[0]

    other_ref = branch.child_record_ref.model_copy(update={"latest_digest": "0" * 64})
    other_child = branch.child_snapshot.model_copy(update={"step_index": 7})
    for swap in ({"child_record_ref": other_ref}, {"child_snapshot": other_child}):
        moved = carrier.model_copy(
            update={"paused_child_branches": (branch.model_copy(update=swap),)}
        )
        assert _verify(snapshot.model_copy(update={key: moved})) is False


@pytest.mark.parametrize("field", sorted(_NOT_HASHED - {"snapshot_hash"}))
def test_the_four_fields_outside_the_hash_do_not_affect_it(field: str) -> None:
    """Documents present coverage, not a wish: these are deliberately not hashed (CP §26.1)."""
    snapshot = _captured(_carriers()["fan_out"])
    other: dict[str, Any] = {
        "created_at": 1,
        "pause_reason": WorkflowPauseReason.HITL_PENDING,
        "state_ledger_anchor": "b" * 64,
    }

    assert _verify(snapshot.model_copy(update={field: other[field]})) is True


def test_a_wrong_stored_hash_fails_verification() -> None:
    snapshot = _captured(_carriers()["handoff"])

    assert _verify(snapshot.model_copy(update={"snapshot_hash": "0" * 64})) is False


# --- the malformed-data boundary ---------------------------------------------------------------


def test_a_carrier_that_cannot_be_serialised_fails_verification_without_raising() -> None:
    unserialisable = FanOutResumeState.model_construct(
        orchestrator_output={"x": object()},
        orchestrator_step_id="o",
        branches=(),
        worker_count=1,
        paused_child_branches=(),
        synthesis_step_id=None,
        effect_fence_paused_branches=(),
        pre_dispatch_gate_owning_branches=(),
    )
    snapshot = _captured({}).model_copy(update={"fan_out_resume": unserialisable})

    assert _verify(snapshot) is False


def test_an_unrelated_fault_in_the_hash_computation_is_not_reported_as_a_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def broken(**_inputs: Any) -> str:
        raise RuntimeError("programmer fault")

    snapshot = _captured({})  # captured BEFORE the fault is injected
    monkeypatch.setattr(prp, "_compute_snapshot_hash", broken)

    with pytest.raises(RuntimeError, match="programmer fault"):
        _verify(snapshot)


def test_a_snapshot_with_an_unknown_json_field_is_refused_at_parse_not_verified() -> None:
    raw = _captured({}).model_dump_json()
    widened = raw[:-1] + ',"smuggled":{"x":1}}'

    with pytest.raises(ValidationError):
        PauseSnapshot.model_validate_json(widened)
