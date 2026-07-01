"""Promotion candidate extraction - U-MEM-08.

This module implements the C-MEM-10 extraction boundary only. It validates
structured candidate hints from episodic/operator source records, links each
candidate back to source evidence, annotates risk, and resolves whether the
current memory policy permits automatic promotion. Canonical promotion writes,
review queues, and durable promotion-decision ledgers land in later units.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Self, cast

from harness_is.memory_policy import (
    MemoryPolicyResolver,
    MemoryPromotionResolution,
    PromotionDecision,
    ReviewMode,
)
from harness_is.memory_record_envelope import (
    MemoryID,
    MemoryScope,
    MemoryVisibility,
    SourceRef,
    SourceRefType,
)
from harness_is.memory_store import MemoryStoreRecord
from pydantic import BaseModel, ConfigDict, Field, model_validator


class PromotionCandidateKind(StrEnum):
    """Candidate kinds declared by C-MEM-10."""

    FACT = "fact"
    DECISION = "decision"
    CONVENTION = "convention"
    FAILURE_LEARNING = "failure_learning"
    RESEARCH = "research"
    PREFERENCE = "preference"
    PROCEDURAL_UPDATE = "procedural_update"


class PromotionCandidateConfidence(StrEnum):
    """Confidence values declared by C-MEM-10."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PromotionRiskFlag(StrEnum):
    """Risk flags required by U-MEM-08."""

    SENSITIVE = "sensitive"
    LOW_CONFIDENCE = "low_confidence"
    CROSS_SCOPE = "cross_scope"
    BEHAVIOR_CHANGING = "behavior_changing"


class PreferenceCandidateSource(StrEnum):
    """Preference provenance required to avoid model-proposed preference drift."""

    OPERATOR_DIRECT = "operator_direct"
    INFERRED = "inferred"


def _empty_source_refs() -> tuple[SourceRef, ...]:
    return ()


def _empty_risk_flags() -> tuple[PromotionRiskFlag, ...]:
    return ()


def _empty_memory_refs() -> tuple[MemoryID, ...]:
    return ()


class PromotionCandidateHint(BaseModel):
    """Structured candidate material carried by an episodic/operator source."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    proposed_kind: PromotionCandidateKind
    statement: str
    confidence: PromotionCandidateConfidence
    suggested_scope: MemoryScope
    source_refs: tuple[SourceRef, ...] = Field(default_factory=_empty_source_refs)
    risk_flags: tuple[PromotionRiskFlag, ...] = Field(default_factory=_empty_risk_flags)
    preference_source: PreferenceCandidateSource | None = None
    sensitive: bool = False
    behavior_changing: bool = False

    @model_validator(mode="after")
    def _validate_preference_source(self) -> Self:
        if (
            self.preference_source is not None
            and self.proposed_kind is not PromotionCandidateKind.PREFERENCE
        ):
            raise ValueError("preference_source is only valid for preference candidates")
        if not self.statement.strip():
            raise ValueError("promotion candidate statement cannot be empty")
        return self


class PromotionCandidate(BaseModel):
    """C-MEM-10 promotion candidate extracted from source evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    candidate_id: str
    source_refs: tuple[SourceRef, ...]
    source_memory_refs: tuple[MemoryID, ...] = Field(default_factory=_empty_memory_refs)
    proposed_kind: PromotionCandidateKind
    statement: str
    confidence: PromotionCandidateConfidence
    suggested_scope: MemoryScope
    risk_flags: tuple[PromotionRiskFlag, ...] = Field(default_factory=_empty_risk_flags)
    preference_source: PreferenceCandidateSource | None = None
    policy_decision: PromotionDecision
    review_mode: ReviewMode
    review_required: bool
    auto_promote_allowed: bool

    @model_validator(mode="after")
    def _validate_preference_source(self) -> Self:
        if not self.source_refs:
            raise ValueError("promotion candidates require at least one source_ref")
        if (
            self.preference_source is not None
            and self.proposed_kind is not PromotionCandidateKind.PREFERENCE
        ):
            raise ValueError("preference_source is only valid for preference candidates")
        if (
            self.proposed_kind is PromotionCandidateKind.PREFERENCE
            and self.preference_source is None
        ):
            raise ValueError("preference candidates require preference_source")
        return self


class PromotionCandidateExtractor:
    """Extract C-MEM-10 candidates from episodic/operator memory records."""

    def __init__(self, policy_resolver: MemoryPolicyResolver | None = None) -> None:
        self._policy_resolver = policy_resolver or MemoryPolicyResolver()

    def extract_from_records(
        self,
        records: Sequence[MemoryStoreRecord],
    ) -> list[PromotionCandidate]:
        """Extract source-linked promotion candidates from stored source records."""

        resolution = self._policy_resolver.resolve_promotion()
        candidates: list[PromotionCandidate] = []
        for record in records:
            for hint in _hints_from_record(record):
                candidates.append(_candidate_from_hint(record, hint, resolution))
        return candidates


def _hints_from_record(record: MemoryStoreRecord) -> list[PromotionCandidateHint]:
    raw_candidates = record.content.get("promotion_candidates")
    if raw_candidates is None:
        return []
    if isinstance(raw_candidates, str) or not isinstance(raw_candidates, Sequence):
        raise TypeError("promotion_candidates must be a sequence of structured candidates")

    hints: list[PromotionCandidateHint] = []
    for raw_item in cast("Sequence[object]", raw_candidates):
        item: object = raw_item
        if isinstance(item, str):
            item = _json_candidate_hint(item)
        if not isinstance(item, Mapping) and not isinstance(item, PromotionCandidateHint):
            raise TypeError("promotion candidate entries must be mappings or JSON mappings")
        hints.append(PromotionCandidateHint.model_validate(item))
    return hints


def _json_candidate_hint(value: str) -> Mapping[str, object]:
    parsed = json.loads(value)
    if not isinstance(parsed, Mapping):
        raise TypeError("promotion candidate JSON entries must decode to mappings")
    return cast("Mapping[str, object]", parsed)


def _candidate_from_hint(
    record: MemoryStoreRecord,
    hint: PromotionCandidateHint,
    resolution: MemoryPromotionResolution,
) -> PromotionCandidate:
    source_refs = _merge_source_refs(record.envelope.source_refs, hint.source_refs)
    risk_flags = _risk_flags(
        hint,
        source_scope=record.envelope.scope,
    )
    preference_source = _preference_source(
        hint,
        source_refs=source_refs,
        source_content=record.content,
    )
    review_required = _review_required(hint, resolution)
    auto_promote_allowed = _auto_promote_allowed(
        hint,
        resolution=resolution,
        review_required=review_required,
    )
    return PromotionCandidate(
        candidate_id=_candidate_id(record.envelope.memory_id, hint, preference_source),
        source_refs=source_refs,
        source_memory_refs=(record.envelope.memory_id,),
        proposed_kind=hint.proposed_kind,
        statement=hint.statement,
        confidence=hint.confidence,
        suggested_scope=hint.suggested_scope,
        risk_flags=risk_flags,
        preference_source=preference_source,
        policy_decision=resolution.promotion_decision,
        review_mode=resolution.review_mode,
        review_required=review_required,
        auto_promote_allowed=auto_promote_allowed,
    )


def _merge_source_refs(
    record_refs: Sequence[SourceRef],
    hint_refs: Sequence[SourceRef],
) -> tuple[SourceRef, ...]:
    refs: list[SourceRef] = []
    seen: set[tuple[str, str, bytes | None]] = set()
    for ref in (*record_refs, *hint_refs):
        key = (ref.ref_type.value, ref.ref, ref.content_hash)
        if key not in seen:
            refs.append(ref)
            seen.add(key)
    return tuple(refs)


def _risk_flags(
    hint: PromotionCandidateHint,
    *,
    source_scope: MemoryScope,
) -> tuple[PromotionRiskFlag, ...]:
    flags = set(hint.risk_flags)
    if hint.sensitive:
        flags.add(PromotionRiskFlag.SENSITIVE)
    if hint.confidence is PromotionCandidateConfidence.LOW:
        flags.add(PromotionRiskFlag.LOW_CONFIDENCE)
    if _scope_escapes_source(hint.suggested_scope, source_scope):
        flags.add(PromotionRiskFlag.CROSS_SCOPE)
    if hint.behavior_changing:
        flags.add(PromotionRiskFlag.BEHAVIOR_CHANGING)
    return tuple(sorted(flags, key=lambda flag: flag.value))


_VISIBILITY_RANK = {
    MemoryVisibility.PRIVATE: 0,
    MemoryVisibility.WORKFLOW: 1,
    MemoryVisibility.PROJECT: 2,
    MemoryVisibility.TENANT: 3,
    MemoryVisibility.PUBLIC: 4,
}


def _scope_escapes_source(candidate_scope: MemoryScope, source_scope: MemoryScope) -> bool:
    if _VISIBILITY_RANK[candidate_scope.visibility] > _VISIBILITY_RANK[source_scope.visibility]:
        return True
    for field_name in (
        "project",
        "workflow",
        "workload_class",
        "provider_family",
        "cli_profile",
        "tenant",
    ):
        source_value = getattr(source_scope, field_name)
        candidate_value = getattr(candidate_scope, field_name)
        if source_value is not None and candidate_value != source_value:
            return True
    return False


def _preference_source(
    hint: PromotionCandidateHint,
    *,
    source_refs: Sequence[SourceRef],
    source_content: Mapping[str, object],
) -> PreferenceCandidateSource | None:
    if hint.proposed_kind is not PromotionCandidateKind.PREFERENCE:
        return None
    if hint.preference_source is not None:
        return hint.preference_source
    if any(ref.ref_type is SourceRefType.OPERATOR for ref in source_refs):
        return PreferenceCandidateSource.OPERATOR_DIRECT
    if source_content.get("summary_source") == "operator":
        return PreferenceCandidateSource.OPERATOR_DIRECT
    return PreferenceCandidateSource.INFERRED


def _review_required(
    hint: PromotionCandidateHint,
    resolution: MemoryPromotionResolution,
) -> bool:
    if hint.confidence is PromotionCandidateConfidence.LOW:
        return True
    if resolution.review_mode is ReviewMode.OPERATOR_REQUIRED:
        return True
    return resolution.promotion_decision in {
        PromotionDecision.PROPOSE_SEMANTIC,
        PromotionDecision.PROPOSE_PROCEDURAL,
    }


def _auto_promote_allowed(
    hint: PromotionCandidateHint,
    *,
    resolution: MemoryPromotionResolution,
    review_required: bool,
) -> bool:
    if review_required:
        return False
    if resolution.review_mode is not ReviewMode.AUTOMATIC:
        return False
    if hint.confidence is PromotionCandidateConfidence.LOW:
        return False
    if hint.proposed_kind is PromotionCandidateKind.PROCEDURAL_UPDATE:
        return resolution.promotion_decision is PromotionDecision.PROMOTE_PROCEDURAL
    return resolution.promotion_decision is PromotionDecision.PROMOTE_SEMANTIC


def _candidate_id(
    source_memory_id: MemoryID,
    hint: PromotionCandidateHint,
    preference_source: PreferenceCandidateSource | None,
) -> str:
    payload = {
        "source_memory_id": str(source_memory_id),
        "proposed_kind": hint.proposed_kind.value,
        "statement": unicodedata.normalize("NFC", hint.statement),
        "confidence": hint.confidence.value,
        "suggested_scope": hint.suggested_scope.model_dump(mode="json"),
        "preference_source": preference_source.value if preference_source is not None else None,
    }
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return f"promocand:{hashlib.sha256(serialized.encode('utf-8')).hexdigest()}"


__all__ = [
    "PreferenceCandidateSource",
    "PromotionCandidate",
    "PromotionCandidateConfidence",
    "PromotionCandidateExtractor",
    "PromotionCandidateHint",
    "PromotionCandidateKind",
    "PromotionRiskFlag",
]
