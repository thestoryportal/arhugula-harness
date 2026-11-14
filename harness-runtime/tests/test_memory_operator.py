"""Tests for the T01 operator memory lifecycle entrypoint."""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from harness_core import DeploymentSurface
from harness_is.memory_operation_ledger import MemoryOperationKind
from harness_is.memory_path_registry import MemoryRootBinding
from harness_is.memory_policy import (
    AccessDecision,
    CaptureDecision,
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
    record_kind_of,
)
from harness_runtime.lifecycle.memory_migration import MemoryMigrationItemStatus
from harness_runtime.memory_compaction_safety import (
    CompactionCandidateDisposition,
    CompactionCandidateDispositionRecord,
    CompactionDispositionRequiredError,
)
from harness_runtime.memory_promotion import (
    PromotionCandidateConfidence,
    PromotionCandidateKind,
    SemanticInjectionPolicy,
    SemanticRecordStatus,
)
from harness_runtime.types import RuntimeMemoryConfig

from .test_state_placement import world  # noqa: F401  (fixture)
from .test_state_placement_bootstrap import (  # noqa: F401
    Site,
    _durable_filesystem,  # autouse fixture: scratch dirs may be tmpfs
)

_NOW = datetime(2026, 11, 8, 12, 0, 0, tzinfo=UTC)
_RUN_ID = "run-t01"
_SOURCE_ID = MemoryID("mem:episodic:episodic_turn:" + "1" * 64)
_OTHER_SOURCE_ID = MemoryID("mem:episodic:episodic_turn:" + "2" * 64)
_SOURCE_REF = SourceRef(ref_type=SourceRefType.TURN, ref="turn-1")


def _seed_source(
    store: CanonicalMemoryStore,
    memory_id: MemoryID,
    turn: str,
    *,
    visibility: MemoryVisibility = MemoryVisibility.WORKFLOW,
    extra: dict[str, object] | None = None,
) -> None:
    content: dict[str, object] = {
        "event_type": "turn_completion",
        "run_id": _RUN_ID,
        "turn_id": turn,
        **(extra or {}),
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
                scope=MemoryScope(project="arhugula", workflow="t01", visibility=visibility),
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
        project="arhugula",
    )


def _permitting(kind: PromotionCandidateKind) -> PromotionDecision:
    if kind is PromotionCandidateKind.PROCEDURAL_UPDATE:
        return PromotionDecision.PROPOSE_PROCEDURAL
    return PromotionDecision.PROPOSE_SEMANTIC


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
    procedural = _operator(store, decision=PromotionDecision.PROPOSE_PROCEDURAL).propose(
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
    operator = _operator(store, decision=_permitting(kind))
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


def test_a_denied_candidate_cannot_be_approved_through_its_proposal_id(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)
    operator = _operator(store)
    proposal = _propose(operator, PromotionCandidateKind.FACT, "A fact.")
    operator.deny(proposal, source_id=_SOURCE_ID, reason="no", timestamp=_NOW)
    before = len(store.read_memory_operations())

    with pytest.raises(MemoryOperatorRefusedError, match="already decided \\(deny_promotion\\)"):
        operator.approve(
            proposal,
            source_id=_SOURCE_ID,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
            timestamp=_NOW,
        )

    assert len(store.read_memory_operations()) == before
    assert store.read_record(proposal, record_kind_of(proposal)).content["status"] == "proposed"


def test_an_approved_candidate_cannot_be_decided_again(tmp_path: Path) -> None:
    store = _store(tmp_path)
    operator = _operator(store)
    proposal = _propose(operator, PromotionCandidateKind.FACT, "A fact.")
    operator.approve(
        proposal,
        source_id=_SOURCE_ID,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        timestamp=_NOW,
    )
    before = len(store.read_memory_operations())

    with pytest.raises(MemoryOperatorRefusedError, match="already decided \\(promote\\)"):
        operator.deny(proposal, source_id=_SOURCE_ID, reason="late", timestamp=_NOW)
    with pytest.raises(MemoryOperatorRefusedError, match="already decided \\(promote\\)"):
        operator.approve(
            proposal,
            source_id=_SOURCE_ID,
            injection_policy=SemanticInjectionPolicy.TOOL_ALLOWED,
            timestamp=_NOW,
        )

    assert len(store.read_memory_operations()) == before


_FACT = PromotionCandidateKind.FACT
_PROCEDURAL = PromotionCandidateKind.PROCEDURAL_UPDATE


@pytest.mark.parametrize(
    ("decision", "review_mode", "kind", "message"),
    [
        (PromotionDecision.DISCARD, ReviewMode.AUTOMATIC, _FACT, "does not permit fact"),
        (PromotionDecision.KEEP_EPISODIC, ReviewMode.AUTOMATIC, _FACT, "does not permit fact"),
        (PromotionDecision.PROPOSE_PROCEDURAL, ReviewMode.AUTOMATIC, _FACT, "does not permit"),
        (PromotionDecision.PROMOTE_PROCEDURAL, ReviewMode.AUTOMATIC, _FACT, "does not permit"),
        (PromotionDecision.PROPOSE_SEMANTIC, ReviewMode.AUTOMATIC, _PROCEDURAL, "does not permit"),
        (PromotionDecision.PROMOTE_SEMANTIC, ReviewMode.AUTOMATIC, _PROCEDURAL, "does not permit"),
        (PromotionDecision.PROPOSE_SEMANTIC, ReviewMode.FORBIDDEN, _FACT, "review is forbidden"),
    ],
)
def test_policy_that_does_not_name_the_target_refuses_propose_and_approve(
    tmp_path: Path,
    decision: PromotionDecision,
    review_mode: ReviewMode,
    kind: PromotionCandidateKind,
    message: str,
) -> None:
    store = _store(tmp_path)
    proposal = _propose(_operator(store, decision=_permitting(kind)), kind, "Proposed earlier.")
    # The policy changed between proposal and decision; the decision obeys the new one.
    refusing = _operator(store, decision=decision, review_mode=review_mode)
    before = len(store.read_memory_operations())

    with pytest.raises(MemoryOperatorRefusedError, match=message):
        _propose(refusing, kind, "Another statement.")
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


@pytest.mark.parametrize(
    ("decision", "kind"),
    [
        (PromotionDecision.PROMOTE_SEMANTIC, _FACT),
        (PromotionDecision.PROMOTE_PROCEDURAL, _PROCEDURAL),
    ],
)
def test_promote_decision_permits_operator_review_of_its_own_target(
    tmp_path: Path, decision: PromotionDecision, kind: PromotionCandidateKind
) -> None:
    store = _store(tmp_path)
    operator = _operator(store, decision=decision)

    approved = operator.approve(
        _propose(operator, kind, "Reviewed statement."),
        source_id=_SOURCE_ID,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        timestamp=_NOW,
    )

    assert approved.status is SemanticRecordStatus.ACTIVE


def test_decision_refused_when_the_source_scope_changed_since_proposal(tmp_path: Path) -> None:
    store = _store(tmp_path)
    operator = _operator(store)
    proposal = _propose(operator, _FACT, "A workflow-visible fact.")
    _seed_source(store, _SOURCE_ID, "turn-1", visibility=MemoryVisibility.PRIVATE)
    assert operator.inspect(_SOURCE_ID).envelope.scope.visibility is MemoryVisibility.PRIVATE
    before = len(store.read_memory_operations())

    with pytest.raises(MemoryOperatorRefusedError, match="scope changed since"):
        operator.approve(
            proposal,
            source_id=_SOURCE_ID,
            injection_policy=SemanticInjectionPolicy.TOOL_ALLOWED,
            timestamp=_NOW,
        )
    with pytest.raises(MemoryOperatorRefusedError, match="scope changed since"):
        operator.deny(proposal, source_id=_SOURCE_ID, reason="x", timestamp=_NOW)

    assert len(store.read_memory_operations()) == before


def _native_operator(store: CanonicalMemoryStore) -> MemoryOperator:
    return MemoryOperator(
        store=store,
        policy_resolver=MemoryPolicyResolver(
            MemoryPolicyDocument(
                policy_id="policy:t01-native",
                enabled=True,
                capture_decision=CaptureDecision.CAPTURE_FULL,
                native_memory_access=AccessDecision.NATIVE_PROVIDER,
            )
        ),
        operator_id="robbo",
        policy_ref="policy:t01-native",
        run_id=_RUN_ID,
        project="arhugula",
    )


def test_migration_is_dry_run_until_applied(tmp_path: Path) -> None:
    store = _store(tmp_path)
    legacy = tmp_path / "legacy"
    (legacy / "project").mkdir(parents=True)
    (legacy / "project" / "notes.txt").write_bytes(b"legacy memory\n")
    operator = _native_operator(store)
    paths = ["/memories/project/notes.txt"]

    planned = asyncio.run(
        operator.migrate(
            legacy, paths, migration_id="m1", visibility=MemoryVisibility.PRIVATE, apply=False
        )
    )

    assert planned.dry_run is True
    assert [item.status for item in planned.items] == [MemoryMigrationItemStatus.READY]
    assert store.read_memory_operations() == []

    applied = asyncio.run(
        operator.migrate(
            legacy, paths, migration_id="m1", visibility=MemoryVisibility.PRIVATE, apply=True
        )
    )

    assert [item.status for item in applied.items] == [MemoryMigrationItemStatus.MIGRATED]
    entries = store.read_memory_operations()
    assert entries
    assert {entry.actor.actor_id for entry in entries} == {"robbo"}


def test_migration_under_a_policy_without_native_access_writes_nothing(tmp_path: Path) -> None:
    store = _store(tmp_path)
    legacy = tmp_path / "legacy"
    (legacy / "project").mkdir(parents=True)
    (legacy / "project" / "notes.txt").write_bytes(b"legacy memory\n")

    with pytest.raises(MemoryOperatorRefusedError, match="migration refused"):
        asyncio.run(
            _operator(store).migrate(
                legacy,
                ["/memories/project/notes.txt"],
                migration_id="m1",
                visibility=MemoryVisibility.PRIVATE,
                apply=True,
            )
        )

    assert store.read_memory_operations() == []


_HINTED_ID = MemoryID("mem:episodic:episodic_turn:" + "3" * 64)


def _seed_hinted_source(store: CanonicalMemoryStore) -> None:
    _seed_source(
        store,
        _HINTED_ID,
        "turn-3",
        extra={
            "promotion_candidates": [
                {
                    "proposed_kind": "fact",
                    "statement": "A hint-carried fact.",
                    "confidence": "medium",
                    "suggested_scope": {
                        "project": "arhugula",
                        "workflow": "t01",
                        "visibility": "workflow",
                    },
                }
            ]
        },
    )


def test_compaction_lists_candidates_then_persists_one_disposition_each(tmp_path: Path) -> None:
    store = _store(tmp_path)
    _seed_hinted_source(store)
    operator = _operator(store)

    planned = operator.compact(
        "compaction-1",
        source_ids=[_HINTED_ID],
        dispositions=[],
        summary="operator compaction",
        timestamp=_NOW,
        apply=False,
    )

    assert isinstance(planned, tuple)
    (candidate,) = planned
    assert candidate.source_memory_refs == (_HINTED_ID,)
    assert store.read_memory_operations() == []
    with pytest.raises(CompactionDispositionRequiredError):
        operator.compact(
            "compaction-1",
            source_ids=[_HINTED_ID],
            dispositions=[],
            summary="operator compaction",
            timestamp=_NOW,
            apply=True,
        )
    assert store.read_memory_operations() == []

    result = operator.compact(
        "compaction-1",
        source_ids=[_HINTED_ID],
        dispositions=[
            CompactionCandidateDispositionRecord(
                candidate_id=candidate.candidate_id,
                disposition=CompactionCandidateDisposition.KEEP_EPISODIC,
                rationale="stays episodic",
            )
        ],
        summary="operator compaction",
        timestamp=_NOW,
        apply=True,
    )

    assert not isinstance(result, tuple)
    assert result.candidate_count == 1
    (entry,) = store.read_memory_operations()
    assert entry.actor.actor_id == "robbo"


def test_source_rescoped_between_check_and_commit_is_not_activated(tmp_path: Path) -> None:
    store = _store(tmp_path)
    operator = _operator(store)
    proposal = _propose(operator, _FACT, "A workflow-visible fact.")
    before = len(store.read_memory_operations())
    real_read = store.read_record
    reads = 0

    def _read_then_rescope(*args: object, **kwargs: object) -> MemoryStoreRecord:
        # After the operator's pre-check read of the source, re-scope it so only the
        # check inside the guarded activation write can see the change.
        nonlocal reads
        record = real_read(*args, **kwargs)  # type: ignore[arg-type]
        if args[0] == _SOURCE_ID:
            reads += 1
            if reads == 1:
                _seed_source(store, _SOURCE_ID, "turn-1", visibility=MemoryVisibility.PRIVATE)
        return record

    store.read_record = _read_then_rescope  # type: ignore[method-assign]

    with pytest.raises(MemoryOperatorRefusedError, match="nothing was activated"):
        operator.approve(
            proposal,
            source_id=_SOURCE_ID,
            injection_policy=SemanticInjectionPolicy.TOOL_ALLOWED,
            timestamp=_NOW,
        )

    store.read_record = real_read  # type: ignore[method-assign]
    assert reads >= 2
    assert len(store.read_memory_operations()) == before
    assert not any(
        entry.operation_kind is MemoryOperationKind.PROMOTE
        for entry in store.read_memory_operations()
    )


def test_configured_target_selects_the_proposal_kind_for_one_source(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = _store(tmp_path)

    def cli(decision: str, *argv: str) -> int:
        config = tmp_path / f"{decision}.toml"
        config.write_text(
            "[runtime]\n"
            'deployment_surface = "local-development"\n'
            f'repository_root = "{tmp_path}"\n'
            'default_topology = "single-threaded-linear"\n'
            "\n[runtime.otel]\n"
            'otlp_endpoint = "http://localhost:4317"\n'
            "\n[runtime.memory]\n"
            f'promotion_decision = "{decision}"\n',
            encoding="utf-8",
        )
        common = ["--memory-root", str(tmp_path / "memory"), "--operator", "robbo"]
        return memory_operator.main(["--config", str(config), *common, "--run-id", _RUN_ID, *argv])

    def propose(decision: str, kind: str) -> int:
        return cli(decision, "propose", _SOURCE_ID, "--kind", kind, "--statement", kind)

    def refused(exit_code: int, reason: str) -> None:
        assert exit_code == 1
        assert reason in capsys.readouterr().err
        assert len(store.read_memory_operations()) == writes

    writes = 0
    for decision in ("promote_semantic", "promote_procedural", "keep_episodic", "discard"):
        refused(propose(decision, "convention"), "promotion_decision")

    assert propose("propose_semantic", "convention") == 0
    semantic = json.loads(capsys.readouterr().out)
    writes = len(store.read_memory_operations())
    refused(propose("propose_semantic", "procedural_update"), "does not permit")
    assert propose("propose_procedural", "procedural_update") == 0
    procedural = json.loads(capsys.readouterr().out)
    writes = len(store.read_memory_operations())
    refused(propose("propose_procedural", "convention"), "does not permit")

    for proposal in (semantic, procedural):
        assert proposal["status"] == "proposed"
        assert proposal["source_refs"] == [_SOURCE_REF.model_dump(mode="json")]
    assert semantic["content"]["source_memory_refs"] == [_SOURCE_ID]
    assert procedural["content"]["evidence"] == [_SOURCE_REF.model_dump(mode="json")]

    approve = ("approve", procedural["memory_id"], "--source", _SOURCE_ID)
    refused(
        cli("propose_semantic", *approve, "--injection-policy", "retrieval_only"),
        "does not permit",
    )
    assert cli("propose_procedural", *approve, "--injection-policy", "retrieval_only") == 0
    assert json.loads(capsys.readouterr().out)["status"] == "active"


# --- declared state placement: the operator derives through the verified root ------------


@pytest.fixture
def placement_site(world: Path) -> Site:  # noqa: F811
    return Site(world / "site")


def _install_placement_config(
    monkeypatch: pytest.MonkeyPatch, site: Site, *, memory_root: Path
) -> None:
    config = site.config(placement=True).model_copy(
        update={"memory": RuntimeMemoryConfig(enabled=True, root_path=memory_root)}
    )
    monkeypatch.setattr(
        "harness_runtime.config_source.RuntimeConfigSource.load",
        classmethod(lambda cls, **_kw: config),
    )


_PLACEMENT_ARGS = ["--config", "unused.toml", "--operator", "robbo", "--run-id", _RUN_ID]


def test_declared_placement_derives_the_memory_root_through_the_verified_stamp(
    placement_site: Site, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    site = placement_site
    _install_placement_config(monkeypatch, site, memory_root=site.root / "memory")
    site.stamp(site.config(placement=True))
    store = _store(site.root)
    _seed_source(store, _SOURCE_ID, "turn-1")

    assert memory_operator.main([*_PLACEMENT_ARGS, "inspect", _SOURCE_ID]) == 0

    assert json.loads(capsys.readouterr().out)["envelope"]["memory_id"] == _SOURCE_ID


def test_declared_placement_that_cannot_be_verified_refuses_without_a_checkout_path(
    placement_site: Site, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    site = placement_site
    # The root was never bootstrapped: the probe never creates it.
    _install_placement_config(monkeypatch, site, memory_root=site.root / "memory")
    before = site.snapshot()

    assert memory_operator.main([*_PLACEMENT_ARGS, "operations"]) == 1

    assert "RT-FAIL-STATE-ROOT-PLACEMENT:" in capsys.readouterr().err
    assert site.snapshot() == before


def test_declared_placement_refuses_a_memory_root_outside_the_verified_root(
    placement_site: Site, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    site = placement_site
    _install_placement_config(monkeypatch, site, memory_root=site.repo / ".harness" / "memory")
    site.stamp(site.config(placement=True))

    assert memory_operator.main([*_PLACEMENT_ARGS, "operations"]) == 1

    assert "RT-FAIL-STATE-ROOT-PLACEMENT:" in capsys.readouterr().err
