"""U-MEM-27 slice 3a - the C-MEM-10 v1.2 read-side cross-family promotion gate.

Witnesses for the READ half of U-MEM-27
(`Implementation_Plan_Memory_Substrate_v1.md` U-MEM-27 verification bullets
:1070-:1082, plus the transition-RESET arm at :1077):

* the read-side gate per entry point, kept SEPARATE (:1070) - the hint path's
  `_candidate_from_hint` and the tool path's `_propose_promotion`, because one
  aggregate test passes over whichever entry point is still ungated
* the per-arm matrix at both entry points (:1071) - `true` and `unknown` flagged
  and gated, `false` unflagged and ungated; plus the legacy ABSENT-field arm
  (:1076), which reads `unknown` without being rewritten
* the vacuity-defeating witness (:1072) under `PROMOTE_SEMANTIC` + `AUTOMATIC`,
  with the `false` arm as the positive control that proves the configuration
  really does permit automatic promotion
* the same matrix under `PROMOTE_PROCEDURAL` + `AUTOMATIC` (:1073), which is
  hint-path-specific: `_auto_promote_allowed` takes a separate branch for
  `PROCEDURAL_UPDATE`, while the tool path's `_promotion_auto_allowed` has no
  kind branch at all
* flag independence from `cross_scope`, both directions (:1075)
* the reserved-flag spoof and suppression arms (:1091 / :1092)
* the direct-construction refusals at the VALIDATING-constructor level (:1082)
* the durable-carrier witness read back from the store (:1078) and its
  ledger-unchanged control (:1079)
* the legacy-record TRANSITION arms (:1077) - materialized explicit `unknown`
  asserted as the EXPECTED outcome, plus the RESET arms for a stored `true` and
  a stored `false`. These sit beside the U-MEM-26 precedent
  `test_legacy_raw_key_record_stays_redactable_with_its_scope_intact`
  (`test_u_mem_26_write_boundary.py`).

Out of scope for this slice, and deliberately not witnessed here: the
activation-boundary re-derivation in `approve` / `edit_and_approve`, worst-value
multi-source aggregation, the frozen provenance snapshot, commit binding,
`_persist_decision` choke-point normalization, and the fail-closed
unresolvable-source branches.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from harness_as.memory_tool_contracts import MemoryToolName
from harness_core import DeploymentSurface
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
    MemoryRecordEnvelope,
    MemoryRecordKind,
    MemoryScope,
    MemoryTier,
    MemoryVisibility,
    SourceRef,
    SourceRefType,
    compute_memory_content_hash,
    derive_memory_id,
)
from harness_is.memory_redaction import MemoryRedactionActor, MemoryRedactionService
from harness_is.memory_retrieval import MemoryRetriever
from harness_is.memory_retrieval_index import DerivedRetrievalIndexStore
from harness_is.memory_store import CanonicalMemoryStore, MemoryStoreRecord
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.memory_promotion import (
    PromotionCandidate,
    PromotionCandidateConfidence,
    PromotionCandidateExtractor,
    PromotionCandidateKind,
    PromotionDecisionResult,
    PromotionDecisionService,
    PromotionRiskFlag,
    SemanticInjectionPolicy,
    SemanticRecordStatus,
)
from harness_runtime.memory_tool_executor import (
    MemoryToolExecutionContext,
    MemoryToolExecutionRequest,
    StandardMemoryToolExecutor,
)

_NOW = datetime(2026, 7, 29, 12, 0, 0, tzinfo=UTC)
_POLICY_REF = "policy:u-mem-27-gate"
_SCOPE_REF = "scope:u-mem-27-gate"
_RUN_ID = "run-u-mem-27-gate"

# The three read-side arms. `None` is the LEGACY arm: no key in the serialized
# payload at all, which is what a pre-amendment record carries.
_GATED_ARMS = (CapturedCrossFamily.TRUE, CapturedCrossFamily.UNKNOWN)


def _actor() -> Actor:
    return Actor(actor_class=ActorClass.AGENT, actor_id="u-mem-27")


def _scope(
    *,
    workflow: str | None = "memory-substrate",
    visibility: MemoryVisibility = MemoryVisibility.WORKFLOW,
) -> MemoryScope:
    return MemoryScope(
        project="arhugula-v2",
        workflow=workflow,
        workload_class="coding-arc",
        provider_family="openai",
        cli_profile="codex",
        visibility=visibility,
    )


# ---------------------------------------------------------------------------
# Entry point 1 - the hint path (`_candidate_from_hint`)
# ---------------------------------------------------------------------------


def _hint_payload(
    *,
    kind: PromotionCandidateKind = PromotionCandidateKind.FACT,
    suggested_scope: MemoryScope | None = None,
    risk_flags: Sequence[PromotionRiskFlag] = (),
) -> dict[str, object]:
    return {
        "proposed_kind": kind.value,
        "statement": "The gate must hold under every policy configuration.",
        "confidence": PromotionCandidateConfidence.HIGH.value,
        "suggested_scope": (suggested_scope or _scope()).model_dump(mode="json"),
        "risk_flags": [flag.value for flag in risk_flags],
    }


def _hint_source_record(
    provenance: CapturedCrossFamily | None,
    *,
    kind: PromotionCandidateKind = PromotionCandidateKind.FACT,
    suggested_scope: MemoryScope | None = None,
    source_scope: MemoryScope | None = None,
    hint_risk_flags: Sequence[PromotionRiskFlag] = (),
) -> MemoryStoreRecord:
    """An episodic-turn source record carrying one structured candidate hint.

    `provenance=None` builds the envelope by DESERIALIZING a payload that has no
    `captured_cross_family` key at all - the pre-amendment shape - rather than
    by passing the enum's default, so the legacy arm exercises the real absent
    key rather than a value that merely equals it.
    """

    content: dict[str, object] = {
        "event_type": "turn_completion",
        "run_id": _RUN_ID,
        "turn_id": "turn-1",
        "summary_source": "model_generated",
        "promotion_candidates": [
            _hint_payload(kind=kind, suggested_scope=suggested_scope, risk_flags=hint_risk_flags)
        ],
    }
    content_hash = compute_memory_content_hash(content)
    envelope_payload: dict[str, object] = {
        "memory_id": str(
            derive_memory_id(MemoryTier.EPISODIC, MemoryRecordKind.EPISODIC_TURN, content_hash)
        ),
        "schema_version": "test-episodic/v1",
        "tier": MemoryTier.EPISODIC.value,
        "kind": MemoryRecordKind.EPISODIC_TURN.value,
        "created_at": _NOW.isoformat(),
        "source_refs": [
            SourceRef(ref_type=SourceRefType.TURN, ref="turn-1").model_dump(mode="json")
        ],
        "scope": (source_scope or _scope()).model_dump(mode="json"),
        "content_hash": content_hash,
    }
    if provenance is not None:
        envelope_payload["captured_cross_family"] = provenance.value
    return MemoryStoreRecord(
        envelope=MemoryRecordEnvelope.model_validate(envelope_payload),
        content=content,
    )


def _resolver(
    *,
    promotion_decision: PromotionDecision = PromotionDecision.PROMOTE_SEMANTIC,
    review_mode: ReviewMode = ReviewMode.AUTOMATIC,
) -> MemoryPolicyResolver:
    return MemoryPolicyResolver(
        MemoryPolicyDocument(
            policy_id=_POLICY_REF,
            enabled=True,
            promotion_decision=promotion_decision,
            review_mode=review_mode,
        )
    )


def _hint_candidate(
    provenance: CapturedCrossFamily | None,
    *,
    kind: PromotionCandidateKind = PromotionCandidateKind.FACT,
    promotion_decision: PromotionDecision = PromotionDecision.PROMOTE_SEMANTIC,
    review_mode: ReviewMode = ReviewMode.AUTOMATIC,
    suggested_scope: MemoryScope | None = None,
    source_scope: MemoryScope | None = None,
    hint_risk_flags: Sequence[PromotionRiskFlag] = (),
) -> PromotionCandidate:
    record = _hint_source_record(
        provenance,
        kind=kind,
        suggested_scope=suggested_scope,
        source_scope=source_scope,
        hint_risk_flags=hint_risk_flags,
    )
    extractor = PromotionCandidateExtractor(
        policy_resolver=_resolver(promotion_decision=promotion_decision, review_mode=review_mode)
    )
    return extractor.extract_from_records((record,))[0]


@pytest.mark.parametrize("provenance", _GATED_ARMS)
def test_hint_path_gates_a_cross_family_captured_source(
    provenance: CapturedCrossFamily,
) -> None:
    """:1071 - `true` and `unknown` are flagged AND gated, identically.

    The `unknown` arm is the load-bearing one: a fail-open implementation that
    only handles `true` passes the other arm and fails here.
    """
    candidate = _hint_candidate(provenance)

    assert PromotionRiskFlag.CROSS_FAMILY_CAPTURE in candidate.risk_flags
    assert candidate.review_required is True
    assert candidate.auto_promote_allowed is False


def test_hint_path_leaves_a_same_family_source_unflagged_and_ungated() -> None:
    """:1071 - `false` is unchanged from today: no flag, no gate."""
    candidate = _hint_candidate(CapturedCrossFamily.FALSE)

    assert PromotionRiskFlag.CROSS_FAMILY_CAPTURE not in candidate.risk_flags
    assert candidate.review_required is False
    assert candidate.auto_promote_allowed is True


def test_hint_path_legacy_source_with_no_key_reads_unknown_and_gates() -> None:
    """:1076 - the legacy read arm, at the hint entry point.

    The source envelope is deserialized from a payload with NO
    `captured_cross_family` key. It reads `unknown`, gates on that basis, and
    the read does not rewrite it.
    """
    record = _hint_source_record(None)
    assert record.envelope.captured_cross_family is CapturedCrossFamily.UNKNOWN

    candidate = PromotionCandidateExtractor(policy_resolver=_resolver()).extract_from_records(
        (record,)
    )[0]

    assert PromotionRiskFlag.CROSS_FAMILY_CAPTURE in candidate.risk_flags
    assert candidate.review_required is True
    assert candidate.auto_promote_allowed is False
    # Not rewritten by the read: no determination was manufactured.
    assert record.envelope.captured_cross_family is CapturedCrossFamily.UNKNOWN


@pytest.mark.parametrize(
    ("provenance", "expected_auto"),
    [
        (CapturedCrossFamily.FALSE, True),
        (CapturedCrossFamily.TRUE, False),
        (CapturedCrossFamily.UNKNOWN, False),
    ],
)
def test_hint_path_gate_holds_under_promote_semantic_and_automatic(
    provenance: CapturedCrossFamily,
    expected_auto: bool,
) -> None:
    """:1072 - the vacuity-defeating witness, with its positive control.

    `PROMOTE_SEMANTIC` + `AUTOMATIC` is the one configuration under which every
    other gate would allow automatic promotion, so the `false` arm proves the
    test configuration really does permit it and the other two arms are the gate
    firing rather than the ambient `PROPOSE_SEMANTIC` pin refusing everything.
    """
    candidate = _hint_candidate(provenance)

    assert candidate.auto_promote_allowed is expected_auto


@pytest.mark.parametrize(
    ("provenance", "expected_auto"),
    [
        (CapturedCrossFamily.FALSE, True),
        (CapturedCrossFamily.TRUE, False),
        (CapturedCrossFamily.UNKNOWN, False),
    ],
)
def test_hint_path_gate_holds_under_promote_procedural_and_automatic(
    provenance: CapturedCrossFamily,
    expected_auto: bool,
) -> None:
    """:1073 - NOT redundant with the semantic row above.

    `_auto_promote_allowed` takes a SEPARATE branch for `PROCEDURAL_UPDATE`, so
    a gate placed only on the semantic return would leave cross-family
    procedural candidates auto-promoting while the semantic matrix stayed green.
    """
    candidate = _hint_candidate(
        provenance,
        kind=PromotionCandidateKind.PROCEDURAL_UPDATE,
        promotion_decision=PromotionDecision.PROMOTE_PROCEDURAL,
    )

    assert candidate.proposed_kind is PromotionCandidateKind.PROCEDURAL_UPDATE
    assert candidate.auto_promote_allowed is expected_auto


def test_cross_family_capture_carries_without_cross_scope() -> None:
    """:1075 - the two flags are independent, direction one."""
    candidate = _hint_candidate(CapturedCrossFamily.TRUE)

    assert PromotionRiskFlag.CROSS_FAMILY_CAPTURE in candidate.risk_flags
    assert PromotionRiskFlag.CROSS_SCOPE not in candidate.risk_flags


def test_cross_scope_carries_without_cross_family_capture() -> None:
    """:1075 - the two flags are independent, direction two.

    A candidate whose suggested scope escapes its source scope is still flagged
    `cross_scope` on a `false`-provenance source; neither flag is derived from
    the other.
    """
    candidate = _hint_candidate(
        CapturedCrossFamily.FALSE,
        suggested_scope=_scope(workflow=None, visibility=MemoryVisibility.PROJECT),
    )

    assert PromotionRiskFlag.CROSS_SCOPE in candidate.risk_flags
    assert PromotionRiskFlag.CROSS_FAMILY_CAPTURE not in candidate.risk_flags


def test_a_candidate_may_carry_both_flags() -> None:
    """:1075 - and a candidate may carry both at once."""
    candidate = _hint_candidate(
        CapturedCrossFamily.TRUE,
        suggested_scope=_scope(workflow=None, visibility=MemoryVisibility.PROJECT),
    )

    assert PromotionRiskFlag.CROSS_SCOPE in candidate.risk_flags
    assert PromotionRiskFlag.CROSS_FAMILY_CAPTURE in candidate.risk_flags


def test_hint_supplied_cross_family_capture_flag_is_discarded_on_a_false_source() -> None:
    """:1091 - the reserved-flag SPOOF arm.

    `PromotionCandidateHint.risk_flags` is typed to the enum, so admitting the
    reserved value makes it a valid hint input. It carries no authority: the
    caller cannot introduce the mark on a source record that carries `false`.
    Without this the flag is caller-writable and the single-authority claim is
    void.
    """
    candidate = _hint_candidate(
        CapturedCrossFamily.FALSE,
        hint_risk_flags=(PromotionRiskFlag.CROSS_FAMILY_CAPTURE,),
    )

    assert PromotionRiskFlag.CROSS_FAMILY_CAPTURE not in candidate.risk_flags
    assert candidate.review_required is False
    assert candidate.auto_promote_allowed is True


@pytest.mark.parametrize("provenance", _GATED_ARMS)
def test_hint_omitting_cross_family_capture_cannot_suppress_it(
    provenance: CapturedCrossFamily,
) -> None:
    """:1092 - the reserved-flag SUPPRESSION arm.

    Both arms are required: an implementation that only strips, or only adds,
    satisfies one and fails the other.
    """
    candidate = _hint_candidate(provenance, hint_risk_flags=())

    assert PromotionRiskFlag.CROSS_FAMILY_CAPTURE in candidate.risk_flags
    assert candidate.review_required is True
    assert candidate.auto_promote_allowed is False


def test_hint_supplied_unrelated_risk_flags_survive_the_reserved_overwrite() -> None:
    """The overwrite is scoped to the ONE reserved flag, not to the whole set."""
    candidate = _hint_candidate(
        CapturedCrossFamily.FALSE,
        hint_risk_flags=(
            PromotionRiskFlag.BEHAVIOR_CHANGING,
            PromotionRiskFlag.CROSS_FAMILY_CAPTURE,
        ),
    )

    assert PromotionRiskFlag.BEHAVIOR_CHANGING in candidate.risk_flags
    assert PromotionRiskFlag.CROSS_FAMILY_CAPTURE not in candidate.risk_flags


# ---------------------------------------------------------------------------
# Entry point 2 - the tool path (`_propose_promotion`)
# ---------------------------------------------------------------------------


def _tool_source_record(provenance: CapturedCrossFamily | None) -> MemoryStoreRecord:
    content: dict[str, object] = {
        "semantic_kind": MemoryRecordKind.SEMANTIC_FACT.value,
        "statement": "A stored source record the tool path promotes from.",
        "confidence": "high",
        "source_authority": "operator_direct",
        "status": "active",
        "injection_policy": "tool_allowed",
        "tags": ["codex", "memory"],
    }
    content_hash = compute_memory_content_hash(content)
    return MemoryStoreRecord(
        envelope=MemoryRecordEnvelope(
            memory_id=derive_memory_id(
                MemoryTier.SEMANTIC, MemoryRecordKind.SEMANTIC_FACT, content_hash
            ),
            schema_version="memory-store-record/v1",
            tier=MemoryTier.SEMANTIC,
            kind=MemoryRecordKind.SEMANTIC_FACT,
            created_at=_NOW,
            source_refs=(SourceRef(ref_type=SourceRefType.OPERATOR, ref="operator:u-mem-27"),),
            scope=_scope(),
            content_hash=content_hash,
            captured_cross_family=provenance or CapturedCrossFamily.UNKNOWN,
        ),
        content=content,
    )


def _strip_provenance_key_on_disk(store: CanonicalMemoryStore, record: MemoryStoreRecord) -> None:
    """Rewrite the persisted payload WITHOUT the key - the pre-amendment shape."""

    path = store.record_path(record)
    payload = json.loads(path.read_text(encoding="utf-8"))
    del payload["envelope"]["captured_cross_family"]
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _tool_context() -> MemoryToolExecutionContext:
    return MemoryToolExecutionContext(
        run_id=_RUN_ID,
        workflow_id="memory-substrate",
        workload_class="coding-arc",
        step_id="step-memory-tools",
        provider="openai",
        model="gpt-5",
        cli_profile="codex",
        scope=_scope(),
        scope_ref=_SCOPE_REF,
        policy_ref=_POLICY_REF,
        token_budget=120,
        timestamp=_NOW,
        actor=_actor(),
    )


def _tool_policy(
    *,
    promotion_decision: PromotionDecision = PromotionDecision.PROMOTE_SEMANTIC,
    review_mode: ReviewMode = ReviewMode.AUTOMATIC,
) -> MemoryPolicyDocument:
    return MemoryPolicyDocument(
        policy_id=_POLICY_REF,
        enabled=True,
        capture_decision=CaptureDecision.CAPTURE_FULL,
        promotion_decision=promotion_decision,
        retrieval_access=AccessDecision.RETRIEVAL_ONLY,
        standard_tool_access=AccessDecision.STANDARD_TOOLS,
        review_mode=review_mode,
    )


def _tool_path_candidate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    provenance: CapturedCrossFamily | None,
    promotion_decision: PromotionDecision = PromotionDecision.PROMOTE_SEMANTIC,
    review_mode: ReviewMode = ReviewMode.AUTOMATIC,
) -> PromotionCandidate:
    """Drive `_propose_promotion` and return the candidate it CONSTRUCTS.

    The tool's public return exposes only `review_required`, and the durable
    record's content is a separate witness whose own mutation probe must leave
    these read-side assertions green - so the candidate is intercepted at the
    service boundary rather than reconstructed from either.
    """

    binding = MemoryRootBinding(default_root=tmp_path / "memory")
    store = CanonicalMemoryStore(
        root_binding=binding,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )
    source = _tool_source_record(provenance)
    store.write_record(source)
    if provenance is None:
        _strip_provenance_key_on_disk(store, source)
    index_store = DerivedRetrievalIndexStore(
        root_binding=binding,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )
    index_store.rebuild(indexed_at=_NOW)
    resolver = MemoryPolicyResolver(
        _tool_policy(promotion_decision=promotion_decision, review_mode=review_mode)
    )
    executor = StandardMemoryToolExecutor(
        store=store,
        index_store=index_store,
        retriever=MemoryRetriever(
            store=store,
            index_store=index_store,
            policy_resolver=resolver,
            policy_ref=_POLICY_REF,
        ),
        policy_resolver=resolver,
    )

    captured: list[PromotionCandidate] = []
    real_propose = PromotionDecisionService.propose_for_review
    real_approve = PromotionDecisionService.approve

    def _spy_propose(
        service: PromotionDecisionService,
        candidate: PromotionCandidate,
        **kwargs: Any,
    ) -> PromotionDecisionResult:
        captured.append(candidate)
        return real_propose(service, candidate, **kwargs)

    def _spy_approve(
        service: PromotionDecisionService,
        candidate: PromotionCandidate,
        **kwargs: Any,
    ) -> PromotionDecisionResult:
        captured.append(candidate)
        return real_approve(service, candidate, **kwargs)

    monkeypatch.setattr(PromotionDecisionService, "propose_for_review", _spy_propose)
    monkeypatch.setattr(PromotionDecisionService, "approve", _spy_approve)

    executor.execute(
        MemoryToolExecutionRequest(
            tool_name=MemoryToolName.PROPOSE_PROMOTION,
            arguments={
                "memory_ref": str(source.envelope.memory_id),
                "target_kind": "convention",
                "policy_ref": _POLICY_REF,
            },
            context=_tool_context(),
        )
    )

    [candidate] = captured
    return candidate


@pytest.mark.parametrize("provenance", _GATED_ARMS)
def test_tool_path_gates_a_cross_family_captured_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    provenance: CapturedCrossFamily,
) -> None:
    """:1070 / :1071 - the SECOND entry point, asserted separately."""
    candidate = _tool_path_candidate(tmp_path, monkeypatch, provenance=provenance)

    assert PromotionRiskFlag.CROSS_FAMILY_CAPTURE in candidate.risk_flags
    assert candidate.review_required is True
    assert candidate.auto_promote_allowed is False


def test_tool_path_leaves_a_same_family_source_unflagged_and_ungated(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """:1071 - `false` at the tool entry point is unchanged from today."""
    candidate = _tool_path_candidate(tmp_path, monkeypatch, provenance=CapturedCrossFamily.FALSE)

    assert PromotionRiskFlag.CROSS_FAMILY_CAPTURE not in candidate.risk_flags
    assert candidate.review_required is False
    assert candidate.auto_promote_allowed is True


def test_tool_path_legacy_source_with_no_key_reads_unknown_and_gates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """:1076 - the legacy read arm at the tool entry point.

    The persisted payload has the key REMOVED on disk, so the executor reads a
    genuine pre-amendment record rather than one that merely carries the
    default.
    """
    candidate = _tool_path_candidate(tmp_path, monkeypatch, provenance=None)

    assert PromotionRiskFlag.CROSS_FAMILY_CAPTURE in candidate.risk_flags
    assert candidate.review_required is True
    assert candidate.auto_promote_allowed is False


@pytest.mark.parametrize(
    ("provenance", "expected_auto"),
    [
        (CapturedCrossFamily.FALSE, True),
        (CapturedCrossFamily.TRUE, False),
        (CapturedCrossFamily.UNKNOWN, False),
    ],
)
def test_tool_path_gate_holds_under_promote_semantic_and_automatic(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    provenance: CapturedCrossFamily,
    expected_auto: bool,
) -> None:
    """:1072 at the tool entry point, positive control included."""
    candidate = _tool_path_candidate(tmp_path, monkeypatch, provenance=provenance)

    assert candidate.auto_promote_allowed is expected_auto


# ---------------------------------------------------------------------------
# The validating-constructor consistency check
# ---------------------------------------------------------------------------


def _direct_candidate(
    *,
    risk_flags: tuple[PromotionRiskFlag, ...],
    review_required: bool,
    auto_promote_allowed: bool,
) -> dict[str, object]:
    """A hand-built candidate payload that touches NEITHER extraction path."""

    return {
        "candidate_id": "promocand:direct",
        "source_refs": (SourceRef(ref_type=SourceRefType.TURN, ref="turn-direct"),),
        "source_memory_refs": (),
        "proposed_kind": PromotionCandidateKind.FACT,
        "statement": "A hand-built candidate reaching the exported model directly.",
        "confidence": PromotionCandidateConfidence.HIGH,
        "suggested_scope": _scope(),
        "risk_flags": risk_flags,
        "preference_source": None,
        "policy_decision": PromotionDecision.PROMOTE_SEMANTIC,
        "review_mode": ReviewMode.AUTOMATIC,
        "review_required": review_required,
        "auto_promote_allowed": auto_promote_allowed,
    }


def test_direct_construction_refuses_the_flag_with_auto_promote_allowed() -> None:
    """:1082 - the illegal pair, direction one, at direct construction."""
    with pytest.raises(ValueError, match="cross_family_capture"):
        PromotionCandidate(
            **_direct_candidate(
                risk_flags=(PromotionRiskFlag.CROSS_FAMILY_CAPTURE,),
                review_required=True,
                auto_promote_allowed=True,
            )
        )


def test_direct_construction_refuses_the_flag_with_review_not_required() -> None:
    """:1082 - the illegal pair, direction two."""
    with pytest.raises(ValueError, match="cross_family_capture"):
        PromotionCandidate(
            **_direct_candidate(
                risk_flags=(PromotionRiskFlag.CROSS_FAMILY_CAPTURE,),
                review_required=False,
                auto_promote_allowed=False,
            )
        )


def test_direct_construction_accepts_the_legal_flagged_shape() -> None:
    """:1082 - the legal flagged candidate constructs normally."""
    candidate = PromotionCandidate(
        **_direct_candidate(
            risk_flags=(PromotionRiskFlag.CROSS_FAMILY_CAPTURE,),
            review_required=True,
            auto_promote_allowed=False,
        )
    )

    assert candidate.risk_flags == (PromotionRiskFlag.CROSS_FAMILY_CAPTURE,)


def test_an_unflagged_candidate_is_entirely_unaffected() -> None:
    """:1082 - the check is scoped to the reserved flag and nothing else."""
    candidate = PromotionCandidate(
        **_direct_candidate(
            risk_flags=(PromotionRiskFlag.BEHAVIOR_CHANGING,),
            review_required=False,
            auto_promote_allowed=True,
        )
    )

    assert candidate.auto_promote_allowed is True


def test_deserialization_refuses_the_illegal_pair() -> None:
    """:1082 - refused by `model_validate` too, not only by `__init__`."""
    legal = PromotionCandidate(
        **_direct_candidate(
            risk_flags=(PromotionRiskFlag.CROSS_FAMILY_CAPTURE,),
            review_required=True,
            auto_promote_allowed=False,
        )
    )
    payload = legal.model_dump(mode="json")
    payload["auto_promote_allowed"] = True

    with pytest.raises(ValueError, match="cross_family_capture"):
        PromotionCandidate.model_validate(payload)


# ---------------------------------------------------------------------------
# The durable carrier, and its C-MEM-08 ledger-unchanged control
# ---------------------------------------------------------------------------


def _decision_store(tmp_path: Path) -> CanonicalMemoryStore:
    return CanonicalMemoryStore(
        root_binding=MemoryRootBinding(default_root=tmp_path / "memory"),
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )


def test_proposed_record_content_carries_the_cross_family_capture_flag(tmp_path: Path) -> None:
    """:1078 - asserted by reading the record BACK from the store.

    The in-memory assertion is what the read-side witnesses above already cover,
    and it is precisely what passes while the durable carrier is missing.
    """
    store = _decision_store(tmp_path)
    candidate = _hint_candidate(CapturedCrossFamily.TRUE)
    service = PromotionDecisionService(
        store=store,
        actor=_actor(),
        policy_ref=_POLICY_REF,
        run_id=_RUN_ID,
    )

    result = service.propose_for_review(
        candidate,
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
    )

    assert result.status is SemanticRecordStatus.PROPOSED
    stored = store.read_record(result.memory_id, MemoryRecordKind.SEMANTIC_FACT)
    assert PromotionRiskFlag.CROSS_FAMILY_CAPTURE.value in stored.content["risk_flags"]


def test_procedural_proposed_record_content_carries_the_flag(tmp_path: Path) -> None:
    """:1078 - the procedural content builder is a separate function."""
    store = _decision_store(tmp_path)
    candidate = _hint_candidate(
        CapturedCrossFamily.UNKNOWN,
        kind=PromotionCandidateKind.PROCEDURAL_UPDATE,
        promotion_decision=PromotionDecision.PROMOTE_PROCEDURAL,
    )
    service = PromotionDecisionService(
        store=store,
        actor=_actor(),
        policy_ref=_POLICY_REF,
        run_id=_RUN_ID,
    )

    result = service.propose_for_review(
        candidate,
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.NEVER,
    )

    stored = store.read_record(result.memory_id, MemoryRecordKind.PROCEDURAL_SNAPSHOT)
    assert PromotionRiskFlag.CROSS_FAMILY_CAPTURE.value in stored.content["risk_flags"]


def test_promotion_ledger_entry_carries_no_risk_flag_field(tmp_path: Path) -> None:
    """:1079 - the obligation was discharged in CONTENT.

    `MemoryOperationPayload` is closed, so a field there would be the C-MEM-08
    amendment this arc forswears. The same decision's ledger row must therefore
    carry no risk-flag field at all.
    """
    store = _decision_store(tmp_path)
    service = PromotionDecisionService(
        store=store,
        actor=_actor(),
        policy_ref=_POLICY_REF,
        run_id=_RUN_ID,
    )

    service.propose_for_review(
        _hint_candidate(CapturedCrossFamily.TRUE),
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
    )

    [operation] = store.read_memory_operations()
    fields = set(type(operation).model_fields)
    assert "risk_flags" not in fields
    assert not [name for name in fields if "risk" in name]
    assert "risk_flags" not in operation.model_dump()


# ---------------------------------------------------------------------------
# The C-MEM-03 content-replacing-transition RESET
#
# These sit beside the U-MEM-26 precedent
# `test_legacy_raw_key_record_stays_redactable_with_its_scope_intact`
# (`test_u_mem_26_write_boundary.py`), which established that a transition is a
# STATE TRANSITION of an already-persisted record.
# ---------------------------------------------------------------------------


def _redaction_service(store: CanonicalMemoryStore) -> MemoryRedactionService:
    return MemoryRedactionService(
        store=store,
        operation_actor=_actor(),
        event_actor=MemoryRedactionActor.OPERATOR,
        policy_ref=_POLICY_REF,
        run_id=_RUN_ID,
    )


def _transition(
    service: MemoryRedactionService,
    record: MemoryStoreRecord,
    transition: str,
) -> MemoryStoreRecord:
    if transition == "redact":
        result = service.redact_content(
            record.envelope.memory_id,
            MemoryRecordKind.SEMANTIC_FACT,
            timestamp=_NOW,
            reason="operator redaction request",
            replacement_summary="[redacted]",
        )
    else:
        result = service.tombstone(
            record.envelope.memory_id,
            MemoryRecordKind.SEMANTIC_FACT,
            timestamp=_NOW,
            reason="operator tombstone request",
        )
    return result.record


@pytest.mark.parametrize("transition", ["redact", "tombstone"])
def test_legacy_record_transition_succeeds_and_materializes_explicit_unknown(
    tmp_path: Path,
    transition: str,
) -> None:
    """:1077 - the legacy TRANSITION arm the read arm cannot cover.

    The materialized explicit `unknown` is asserted as the EXPECTED outcome
    rather than treated as a defect: C-MEM-03's forward-only paragraph permits
    it, since absent and explicit-`unknown` denote the identical undetermined
    status and gate identically.
    """
    store = _decision_store(tmp_path)
    record = _tool_source_record(None)
    store.write_record(record)
    _strip_provenance_key_on_disk(store, record)
    stored_payload = json.loads(store.record_path(record).read_text(encoding="utf-8"))
    assert "captured_cross_family" not in stored_payload["envelope"]

    transitioned = _transition(_redaction_service(store), record, transition)

    assert transitioned.envelope.captured_cross_family is CapturedCrossFamily.UNKNOWN
    rewritten = json.loads(store.record_path(record).read_text(encoding="utf-8"))
    assert rewritten["envelope"]["captured_cross_family"] == CapturedCrossFamily.UNKNOWN.value


@pytest.mark.parametrize("transition", ["redact", "tombstone"])
@pytest.mark.parametrize("provenance", [CapturedCrossFamily.TRUE, CapturedCrossFamily.FALSE])
def test_content_replacing_transition_resets_a_determination_to_unknown(
    tmp_path: Path,
    transition: str,
    provenance: CapturedCrossFamily,
) -> None:
    """:1077 - the RESET arms, which the absent-field arm does not reach.

    `_replacement_content` substitutes a wholly harness-authored mapping for the
    record's content, while `_transition`'s `model_copy` update set carried only
    `updated_at` / `content_hash` / `redaction_state` - so a prior determination
    would have survived onto content that derives from no dispatch, asserting
    the replacement material came from the old dispatch.
    """
    store = _decision_store(tmp_path)
    record = _tool_source_record(provenance)
    store.write_record(record)
    assert record.envelope.captured_cross_family is provenance

    transitioned = _transition(_redaction_service(store), record, transition)

    assert transitioned.envelope.captured_cross_family is CapturedCrossFamily.UNKNOWN
    rewritten = json.loads(store.record_path(record).read_text(encoding="utf-8"))
    assert rewritten["envelope"]["captured_cross_family"] == CapturedCrossFamily.UNKNOWN.value
