"""Tests for the T01 operator memory lifecycle entrypoint."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from harness_core import DeploymentSurface
from harness_is.memory_operation_ledger import MemoryOperationKind
from harness_is.memory_path_registry import MemoryRootBinding
from harness_is.memory_policy import (
    MemoryPolicyDocument,
    MemoryPolicyResolver,
    PromotionDecision,
    ReviewMode,
)
from harness_is.memory_record_envelope import (
    CapturedCrossFamily,
    MemoryID,
    MemoryRecordEnvelope,
    MemoryRecordKind,
    MemoryScope,
    MemoryTier,
    MemoryVisibility,
    RedactionState,
    SourceRef,
    SourceRefType,
    compute_memory_content_hash,
)
from harness_is.memory_store import CanonicalMemoryStore, MemoryStoreRecord
from harness_is.state_ledger_entry_schema import ActorClass
from harness_runtime.admin import memory_operator
from harness_runtime.admin.memory_operator import (
    LifecyclePlan,
    LifecycleTransition,
    MemoryOperator,
    MemoryOperatorRefusedError,
)
from harness_runtime.memory_promotion import (
    PromotionCandidateConfidence,
    PromotionCandidateKind,
    SemanticInjectionPolicy,
    SemanticRecordStatus,
)

_NOW = datetime(2026, 11, 8, 12, 0, 0, tzinfo=UTC)
_RUN_ID = "run-t01"
_SOURCE_ID = MemoryID("mem:episodic:episodic_turn:" + "1" * 64)
_OTHER_SOURCE_ID = MemoryID("mem:episodic:episodic_turn:" + "2" * 64)
_SOURCE_REF = SourceRef(ref_type=SourceRefType.TURN, ref="turn-1")


def _seed_source(store: CanonicalMemoryStore, memory_id: MemoryID, turn: str) -> None:
    content: dict[str, object] = {
        "event_type": "turn_completion",
        "run_id": _RUN_ID,
        "turn_id": turn,
    }
    store.write_record(
        MemoryStoreRecord(
            envelope=MemoryRecordEnvelope(
                memory_id=memory_id,
                schema_version="test-episodic/v1",
                tier=MemoryTier.EPISODIC,
                kind=MemoryRecordKind.EPISODIC_TURN,
                created_at=_NOW,
                source_refs=(SourceRef(ref_type=SourceRefType.TURN, ref=turn),),
                scope=MemoryScope(
                    project="arhugula", workflow="t01", visibility=MemoryVisibility.WORKFLOW
                ),
                content_hash=compute_memory_content_hash(content),
                captured_cross_family=CapturedCrossFamily.FALSE,
            ),
            content=content,
        )
    )


def _store(tmp_path: Path) -> CanonicalMemoryStore:
    store = CanonicalMemoryStore(
        root_binding=MemoryRootBinding(default_root=tmp_path / "memory"),
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )
    _seed_source(store, _SOURCE_ID, "turn-1")
    _seed_source(store, _OTHER_SOURCE_ID, "turn-2")
    return store


def _operator(
    store: CanonicalMemoryStore,
    *,
    decision: PromotionDecision = PromotionDecision.PROPOSE_SEMANTIC,
    review_mode: ReviewMode = ReviewMode.AUTOMATIC,
) -> MemoryOperator:
    return MemoryOperator(
        store=store,
        policy_resolver=MemoryPolicyResolver(
            MemoryPolicyDocument(
                policy_id="policy:t01",
                enabled=True,
                promotion_decision=decision,
                review_mode=review_mode,
            )
        ),
        operator_id="robbo",
        policy_ref="policy:t01",
        run_id=_RUN_ID,
    )


def _propose(operator: MemoryOperator, kind: PromotionCandidateKind, statement: str) -> MemoryID:
    return operator.propose(
        _SOURCE_ID,
        kind=kind,
        statement=statement,
        confidence=PromotionCandidateConfidence.HIGH,
        timestamp=_NOW,
    ).memory_id


def test_one_episode_feeds_semantic_and_procedural_proposals_with_source_ids(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    operator = _operator(store)

    semantic = operator.propose(
        _SOURCE_ID,
        kind=PromotionCandidateKind.CONVENTION,
        statement="Run pyright with the worktree venv interpreter.",
        confidence=PromotionCandidateConfidence.HIGH,
        timestamp=_NOW,
    )
    procedural = operator.propose(
        _SOURCE_ID,
        kind=PromotionCandidateKind.PROCEDURAL_UPDATE,
        statement="Sync the worktree venv before running focused tests.",
        confidence=PromotionCandidateConfidence.MEDIUM,
        timestamp=_NOW,
    )

    for result in (semantic, procedural):
        assert result.status is SemanticRecordStatus.PROPOSED
        assert result.record.envelope.source_refs == (_SOURCE_REF,)
        assert result.record.content["injection_policy"] == SemanticInjectionPolicy.NEVER.value
    assert semantic.record.content["source_memory_refs"] == [_SOURCE_ID]
    assert procedural.record.content["procedural_update"] == (
        "Sync the worktree venv before running focused tests."
    )
    proposals = [
        entry
        for entry in store.read_memory_operations()
        if entry.operation_kind is MemoryOperationKind.PROPOSE_PROMOTION
    ]
    assert len(proposals) == 2
    assert {entry.actor.actor_class for entry in proposals} == {ActorClass.OPERATOR}
    assert {entry.actor.actor_id for entry in proposals} == {"robbo"}


@pytest.mark.parametrize(
    "kind", [PromotionCandidateKind.FACT, PromotionCandidateKind.PROCEDURAL_UPDATE]
)
def test_approve_activates_and_deny_records_inactive_decision(
    tmp_path: Path, kind: PromotionCandidateKind
) -> None:
    store = _store(tmp_path)
    operator = _operator(store)
    approved_proposal = _propose(operator, kind, "Approved statement.")
    denied_proposal = _propose(operator, kind, "Denied statement.")

    approved = operator.approve(
        approved_proposal,
        source_id=_SOURCE_ID,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        timestamp=_NOW,
        rationale="checked against the captured turn",
    )
    denied = operator.deny(
        denied_proposal, source_id=_SOURCE_ID, reason="not durable", timestamp=_NOW
    )

    assert approved.status is SemanticRecordStatus.ACTIVE
    assert approved.operation_kind is MemoryOperationKind.PROMOTE
    assert approved.record.content["injection_policy"] == "retrieval_only"
    assert approved.record.envelope.source_refs == (_SOURCE_REF,)
    assert denied.status is SemanticRecordStatus.DENIED
    assert denied.operation_kind is MemoryOperationKind.DENY_PROMOTION
    assert denied.record.content["injection_policy"] == SemanticInjectionPolicy.NEVER.value
    assert denied.record.content["review_reason"] == "not durable"
    decisions = [
        entry for entry in store.read_memory_operations() if entry.actor.actor_id == "robbo"
    ]
    assert [entry.operation_kind for entry in decisions] == [
        MemoryOperationKind.PROPOSE_PROMOTION,
        MemoryOperationKind.PROPOSE_PROMOTION,
        MemoryOperationKind.PROMOTE,
        MemoryOperationKind.DENY_PROMOTION,
    ]


def test_decision_naming_the_wrong_source_is_refused_without_writes(tmp_path: Path) -> None:
    store = _store(tmp_path)
    operator = _operator(store)
    proposal = _propose(operator, PromotionCandidateKind.FACT, "A fact.")
    before = len(store.read_memory_operations())

    with pytest.raises(MemoryOperatorRefusedError, match="was not proposed from source"):
        operator.approve(
            proposal,
            source_id=_OTHER_SOURCE_ID,
            injection_policy=SemanticInjectionPolicy.TOOL_ALLOWED,
            timestamp=_NOW,
        )
    with pytest.raises(MemoryOperatorRefusedError, match="was not proposed from source"):
        operator.deny(proposal, source_id=_OTHER_SOURCE_ID, reason="x", timestamp=_NOW)

    assert len(store.read_memory_operations()) == before


def test_only_proposed_records_can_be_decided(tmp_path: Path) -> None:
    store = _store(tmp_path)
    operator = _operator(store)
    denied = operator.deny(
        _propose(operator, PromotionCandidateKind.FACT, "A fact."),
        source_id=_SOURCE_ID,
        reason="no",
        timestamp=_NOW,
    )
    before = len(store.read_memory_operations())

    with pytest.raises(MemoryOperatorRefusedError, match="is denied, not proposed"):
        operator.approve(
            denied.memory_id,
            source_id=_SOURCE_ID,
            injection_policy=SemanticInjectionPolicy.TOOL_ALLOWED,
            timestamp=_NOW,
        )

    assert len(store.read_memory_operations()) == before


@pytest.mark.parametrize(
    ("decision", "review_mode", "message"),
    [
        (PromotionDecision.DISCARD, ReviewMode.AUTOMATIC, "discards candidates"),
        (PromotionDecision.PROPOSE_SEMANTIC, ReviewMode.FORBIDDEN, "review is forbidden"),
    ],
)
def test_policy_that_forbids_promotion_refuses_propose_and_approve(
    tmp_path: Path, decision: PromotionDecision, review_mode: ReviewMode, message: str
) -> None:
    store = _store(tmp_path)
    proposal = _propose(_operator(store), PromotionCandidateKind.FACT, "A fact.")
    refusing = _operator(store, decision=decision, review_mode=review_mode)
    before = len(store.read_memory_operations())

    with pytest.raises(MemoryOperatorRefusedError, match=message):
        _propose(refusing, PromotionCandidateKind.FACT, "Another fact.")
    with pytest.raises(MemoryOperatorRefusedError, match=message):
        refusing.approve(
            proposal,
            source_id=_SOURCE_ID,
            injection_policy=SemanticInjectionPolicy.TOOL_ALLOWED,
            timestamp=_NOW,
        )

    assert len(store.read_memory_operations()) == before


def test_preference_candidates_are_not_operator_proposable(tmp_path: Path) -> None:
    store = _store(tmp_path)

    with pytest.raises(MemoryOperatorRefusedError, match="not operator-proposable"):
        _propose(_operator(store), PromotionCandidateKind.PREFERENCE, "Prefers terse output.")

    assert store.read_memory_operations() == []


@pytest.mark.parametrize(
    ("transition", "state"),
    [
        (LifecycleTransition.REDACT, RedactionState.REDACTED),
        (LifecycleTransition.TOMBSTONE, RedactionState.TOMBSTONED),
        (LifecycleTransition.EXPIRE, RedactionState.REDACTED),
    ],
)
def test_lifecycle_transition_is_dry_run_until_applied(
    tmp_path: Path, transition: LifecycleTransition, state: RedactionState
) -> None:
    store = _store(tmp_path)
    operator = _operator(store)

    plan = operator.lifecycle(
        transition,
        _SOURCE_ID,
        reason="operator request",
        replacement_summary=None,
        timestamp=_NOW,
        apply=False,
    )

    assert isinstance(plan, LifecyclePlan)
    assert plan.current_redaction_state == RedactionState.ACTIVE.value
    assert store.read_memory_operations() == []
    assert operator.inspect(_SOURCE_ID).envelope.redaction_state is RedactionState.ACTIVE

    operator.lifecycle(
        transition,
        _SOURCE_ID,
        reason="operator request",
        replacement_summary="removed by operator",
        timestamp=_NOW,
        apply=True,
    )

    assert operator.inspect(_SOURCE_ID).envelope.redaction_state is state
    (entry,) = store.read_memory_operations()
    assert entry.actor.actor_class is ActorClass.OPERATOR
    assert entry.redaction_event is not None


def test_cli_round_trip_through_the_configured_entrypoint(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _store(tmp_path)
    config = tmp_path / "harness.toml"
    config.write_text(
        "[runtime]\n"
        'deployment_surface = "local-development"\n'
        f'repository_root = "{tmp_path}"\n'
        'default_topology = "single-threaded-linear"\n'
        "\n[runtime.otel]\n"
        'otlp_endpoint = "http://localhost:4317"\n',
        encoding="utf-8",
    )
    common = [
        "--config",
        str(config),
        "--memory-root",
        str(tmp_path / "memory"),
        "--operator",
        "robbo",
        "--run-id",
        _RUN_ID,
    ]

    assert (
        memory_operator.main(
            [*common, "propose", _SOURCE_ID, "--kind", "fact", "--statement", "A fact."]
        )
        == 0
    )
    proposal = json.loads(capsys.readouterr().out)
    assert proposal["status"] == "proposed"
    assert (
        memory_operator.main(
            [
                *common,
                "approve",
                proposal["memory_id"],
                "--source",
                _SOURCE_ID,
                "--injection-policy",
                "retrieval_only",
            ]
        )
        == 0
    )
    approved = json.loads(capsys.readouterr().out)
    assert approved["status"] == "active"
    assert approved["source_refs"] == [_SOURCE_REF.model_dump(mode="json")]

    assert memory_operator.main([*common, "inspect", _SOURCE_ID]) == 0
    inspected = json.loads(capsys.readouterr().out)
    assert inspected["envelope"]["memory_id"] == _SOURCE_ID
    assert inspected["envelope"]["redaction_state"] == "active"
    assert memory_operator.main([*common, "operations"]) == 0
    assert [entry["operation_kind"] for entry in json.loads(capsys.readouterr().out)] == [
        "propose_promotion",
        "promote",
    ]
    assert memory_operator.main([*common, "tombstone", _SOURCE_ID, "--reason", "r"]) == 0
    assert json.loads(capsys.readouterr().out)["applied"] is False
    assert (
        memory_operator.main(
            [
                *common,
                "approve",
                proposal["memory_id"],
                "--source",
                _OTHER_SOURCE_ID,
                "--injection-policy",
                "tool_allowed",
            ]
        )
        == 1
    )
    assert "was not proposed from source" in capsys.readouterr().err
