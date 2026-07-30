"""Promotion candidate extraction and review decisions.

This module implements the C-MEM-10 extraction boundary and the U-MEM-09
promotion-decision boundary. It validates structured candidate hints from
episodic/operator source records, links each candidate back to source evidence,
annotates risk, resolves whether the current memory policy permits automatic
promotion, and persists review decisions through the canonical memory store and
durable memory-operation ledger.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from enum import StrEnum
from typing import Protocol, Self, cast

from harness_is.memory_observability import (
    MemoryTelemetryOperationName,
    memory_telemetry_span,
)
from harness_is.memory_operation_ledger import (
    MemoryOperationKind,
    MemoryOperationPayload,
    MemoryOperationProjection,
    MemoryOperationWriteResult,
)
from harness_is.memory_policy import (
    MemoryPolicyResolver,
    MemoryPromotionResolution,
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
    SourceRef,
    SourceRefType,
    compute_memory_content_hash,
    derive_memory_id,
)
from harness_is.memory_store import MemoryStoreGuardedWriteConflictError, MemoryStoreRecord
from harness_is.state_ledger_entry_schema import Actor, Identifier
from pydantic import BaseModel, ConfigDict, Field, model_validator

from harness_runtime.memory_scope_family import (
    canonical_scope_family,
    resolve_scope_family,
    scope_family_out_of_domain_message,
)


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
    """Risk flags required by U-MEM-08.

    `CROSS_FAMILY_CAPTURE` is the C-MEM-10 v1.2 (`B-92`) addition and the only
    enum edit U-MEM-27 makes. It is RESERVED to the writer that derives it: it
    names a fact about a stored source record's provenance, so a caller-supplied
    instance carries no authority and is discarded and re-derived (see
    `_risk_flags`). The contract field is an open `list<string>`; this
    implementation-side enumeration is closed, so admitting the value here is
    what makes it expressible at all.
    """

    SENSITIVE = "sensitive"
    LOW_CONFIDENCE = "low_confidence"
    CROSS_SCOPE = "cross_scope"
    BEHAVIOR_CHANGING = "behavior_changing"
    CROSS_FAMILY_CAPTURE = "cross_family_capture"


def cross_family_capture_flagged(provenance: CapturedCrossFamily) -> bool:
    """C-MEM-03 read-side mapping of the tri-state onto the C-MEM-10 gate.

    `unknown` is NOT "presumed same-family": it is treated exactly as `true` is,
    so only an explicit `false` - a comparison the capture writer actually made
    and found equal - leaves a candidate ungated. An absent field deserializes
    to `UNKNOWN`, so a pre-amendment record gates here by construction with no
    back-fill and no migration.
    """

    return provenance is not CapturedCrossFamily.FALSE


class PreferenceCandidateSource(StrEnum):
    """Preference provenance required to avoid model-proposed preference drift."""

    OPERATOR_DIRECT = "operator_direct"
    INFERRED = "inferred"


class SemanticRecordStatus(StrEnum):
    """Semantic/procedural promotion statuses declared by C-MEM-05."""

    PROPOSED = "proposed"
    ACTIVE = "active"
    DENIED = "denied"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"


class SemanticInjectionPolicy(StrEnum):
    """Injection policy values declared by C-MEM-05."""

    NEVER = "never"
    RETRIEVAL_ONLY = "retrieval_only"
    PROMPT_PACKET_ALLOWED = "prompt_packet_allowed"
    TOOL_ALLOWED = "tool_allowed"
    NATIVE_ALLOWED = "native_allowed"


class PreferenceSubject(StrEnum):
    """Preference subjects declared by C-MEM-06."""

    OPERATOR = "operator"
    PROJECT = "project"
    WORKFLOW = "workflow"
    CODE_STYLE = "code_style"
    TOOL_USE = "tool_use"
    PROVIDER = "provider"
    REVIEW = "review"
    OTHER = "other"


class PreferenceStrength(StrEnum):
    """Preference strengths declared by C-MEM-06."""

    WEAK = "weak"
    NORMAL = "normal"
    STRONG = "strong"
    MANDATORY = "mandatory"


class PreferenceSourceAuthority(StrEnum):
    """Preference source-authority values declared by C-MEM-06."""

    OPERATOR_DIRECT = "operator_direct"
    INFERRED_FROM_REPETITION = "inferred_from_repetition"
    IMPORTED = "imported"
    POLICY = "policy"


class PromotionReviewRequiredError(ValueError):
    """Raised when a caller tries to activate a candidate that still needs review."""


class PromotionProvenanceChangedError(RuntimeError):
    """Raised when a cited source's provenance changed after the frozen snapshot.

    C-MEM-10 v1.2 commit binding. The decision the service took is no longer the
    decision the current store state supports, so the write it authorized is
    refused rather than committed against a stale reading. Nothing is written to
    either store; the caller re-reads and re-decides.
    """


class PreferencePromotionValidationError(ValueError):
    """Raised when a preference candidate lacks C-MEM-06 required metadata."""


class PromotionScopeValueDomainError(ValueError):
    """Raised when a candidate scope's `provider_family` is out of the value domain.

    U-MEM-26 / C-MEM-03 v1.1. The suggested scope of a promotion candidate is
    UNTRUSTED - it arrives from a caller- or model-supplied hint, or from a
    statically-supplied tool-execution context - and it is persisted VERBATIM
    into the promoted record's envelope. C-MEM-09 already requires promotion to
    deny on failed policy resolution; an identifier that names no provider
    family this substrate knows is the same class of failure, so it is denied
    rather than stored.

    A ValueError sibling of the two validation refusals above, deliberately:
    the refusal is about the candidate's own contents, not about the store.
    """


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
        if PromotionRiskFlag.CROSS_FAMILY_CAPTURE in self.risk_flags and (
            not self.review_required or self.auto_promote_allowed
        ):
            # C-MEM-10 v1.2 biconditional, CONSISTENCY half. Scope stated
            # exactly: this refuses the illegal PAIR at every VALIDATING
            # constructor (init, `model_validate`). It is not a provenance
            # check - it cannot see a candidate that simply OMITS the mark - and
            # it does not run on `model_copy(update=...)`, which bypasses
            # after-validators by design on this project's Pydantic. Closing the
            # copy route by overriding `model_copy` is deliberately NOT
            # attempted; the activation-boundary re-derivation owns that.
            raise ValueError(
                "cross_family_capture candidates are review-required and never "
                "auto-promotable (C-MEM-10)"
            )
        return self


class PreferencePromotionDetails(BaseModel):
    """C-MEM-06 preference-only fields supplied during promotion."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    preference_subject: PreferenceSubject
    preference_strength: PreferenceStrength
    source_authority: PreferenceSourceAuthority
    confirmation_required: bool


class PromotionDecisionResult(BaseModel):
    """Result of applying or queueing one promotion decision."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: SemanticRecordStatus
    record: MemoryStoreRecord
    memory_id: MemoryID
    operation_kind: MemoryOperationKind
    operation_result: MemoryOperationWriteResult


class PromotionDecisionStore(Protocol):
    """Store surface consumed by ``PromotionDecisionService``.

    `read_record` and `write_record_guarded` are the U-MEM-27 additions. Both
    are INTERNAL SEAM widenings, not public contract changes - verified rather
    than asserted: `PromotionDecisionStore` appears nowhere under
    `design-substrate/`, so no spec declares its shape. Both are satisfied by
    the existing concrete `CanonicalMemoryStore` without new concrete code:
    `read_record` already exists, and `write_record_guarded` is the GENERIC
    compare-and-commit seam this unit added to the store - generic because the
    store must stay free of promotion semantics (carrier-home discipline).
    """

    def write_record(self, record: MemoryStoreRecord) -> object: ...

    def write_record_guarded(
        self,
        record: MemoryStoreRecord,
        *,
        precondition: Callable[[], bool],
    ) -> object: ...

    def read_record(
        self,
        memory_id: MemoryID,
        kind: MemoryRecordKind,
        *,
        run_id: str | None = None,
        audit_mode: bool = False,
    ) -> MemoryStoreRecord: ...

    def append_memory_operation(
        self,
        payload: MemoryOperationPayload,
    ) -> MemoryOperationWriteResult: ...


_EPISODIC_KINDS: frozenset[MemoryRecordKind] = frozenset(
    {
        MemoryRecordKind.EPISODIC_RUN,
        MemoryRecordKind.EPISODIC_TURN,
        MemoryRecordKind.TOOL_EVENT,
        MemoryRecordKind.COMPACTION_EVENT,
    }
)
"""Kinds whose store path is keyed by `run_id`.

`MemoryStore._required_run_id` RAISES for these when no `run_id` is supplied,
and the promotion service holds only an OPTIONAL `self._run_id` which may be
absent or may belong to a different run than the cited source. Named here so
the "no usable run_id" fail-closed branch is an explicit, testable arm rather
than an incidental exception catch.
"""


class _EffectiveProvenance(BaseModel):
    """The ONE frozen provenance snapshot of a single promotion service call.

    The `B-91` frozen-decision-input idiom, and the reason the gate and the
    durable write cannot disagree. The cited source records are resolved exactly
    once, at the start of the call; this value carries both the aggregated
    tri-state AND the normalized risk-flag set derived from it, and the same
    instance is threaded through the activation gate and `_persist_decision`.
    The gate is a PURE PROJECTION of it (`gated`) and performs no lookup of its
    own - deliberately NOT two lookups plus a comparison, which would detect the
    disagreement instead of preventing it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    aggregate: CapturedCrossFamily
    risk_flags: tuple[PromotionRiskFlag, ...]

    @property
    def gated(self) -> bool:
        """Whether automatic activation is withheld on the cross-family ground."""

        return cross_family_capture_flagged(self.aggregate)


def _aggregate_provenance(values: Sequence[CapturedCrossFamily]) -> CapturedCrossFamily:
    """Worst-value aggregation across every cited source (C-MEM-10 v1.2).

    `true` if ANY resolved source is `true`; else `unknown` if ANY is `unknown`
    or unresolvable; `false` only when EVERY cited source resolves `false`. An
    EMPTY citation list is `unknown`, not `false` - a candidate that names no
    source has shown nothing, and the fail-closed reading is the honest one.

    An implementation that gated only when ALL sources were risky would satisfy
    every single-source witness while auto-promoting a mixed candidate.
    """

    if not values:
        return CapturedCrossFamily.UNKNOWN
    if any(value is CapturedCrossFamily.TRUE for value in values):
        return CapturedCrossFamily.TRUE
    if any(value is CapturedCrossFamily.UNKNOWN for value in values):
        return CapturedCrossFamily.UNKNOWN
    return CapturedCrossFamily.FALSE


def _record_kind_from_memory_id(memory_id: MemoryID) -> MemoryRecordKind | None:
    """Recover the record kind from `mem:{tier}:{kind}:{hex}`, or `None`.

    `None` is one of the four unresolvable branches, kept distinct from the
    others so each has its own witness: a caller-supplied `source_memory_refs`
    entry is an opaque string and may name no parseable kind at all.
    """

    parts = str(memory_id).split(":")
    if len(parts) != 4 or parts[0] != "mem":
        return None
    try:
        return MemoryRecordKind(parts[2])
    except ValueError:
        return None


def _resolve_source_provenance(
    store: PromotionDecisionStore,
    memory_id: MemoryID,
    *,
    run_id: str | None,
) -> CapturedCrossFamily:
    """Read ONE cited source record's `captured_cross_family`, fail-closed.

    Every unresolvable branch returns `unknown` - mark carried, automatic
    activation withheld, operator-approved path left open. The branches are
    written out rather than collapsed into one catch-all, because a single
    blanket `except` satisfies one aggregate test while leaving the others
    silently unhandled.
    """

    kind = _record_kind_from_memory_id(memory_id)
    if kind is None:
        # Branch 1: the reference names no parseable record kind.
        return CapturedCrossFamily.UNKNOWN
    if kind in _EPISODIC_KINDS and run_id is None:
        # Branch 2: an episodic source with no usable `run_id`. Pre-checked
        # rather than left to `_required_run_id`'s raise, so the branch is
        # deterministic across every store implementation, not only the
        # concrete one.
        return CapturedCrossFamily.UNKNOWN
    try:
        record = store.read_record(memory_id, kind, run_id=run_id, audit_mode=True)
    except LookupError:
        # Branch 3: absent, or present but unservable.
        return CapturedCrossFamily.UNKNOWN
    except ValueError:
        # Branch 4: the store refused the lookup arguments (the
        # `_required_run_id` raise on a store that does not pre-check) or the
        # stored payload would not deserialize.
        return CapturedCrossFamily.UNKNOWN
    if record.envelope.memory_id != memory_id:
        # `EPISODIC_RUN` is keyed by `run_id`, so `read_record`'s `memory_id`
        # argument is inert for it and a different record can come back. A
        # record that is not the cited one proves nothing about the cited one.
        return CapturedCrossFamily.UNKNOWN
    return record.envelope.captured_cross_family


def _normalized_risk_flags(
    candidate: PromotionCandidate,
    *,
    gated: bool,
) -> tuple[PromotionRiskFlag, ...]:
    """The candidate's flags with the reserved mark restated from the snapshot.

    Every durable write taken from a candidate the service did not itself derive
    persists the RE-DERIVED mark, never the supplied one: injected when
    re-derivation yields `true` or `unknown` (including every unresolvable
    branch - "this needs review and here is why" is the honest durable
    statement), stripped when it yields `false`.
    """

    flags = set(candidate.risk_flags)
    flags.discard(PromotionRiskFlag.CROSS_FAMILY_CAPTURE)
    if gated:
        flags.add(PromotionRiskFlag.CROSS_FAMILY_CAPTURE)
    return tuple(sorted(flags, key=lambda flag: flag.value))


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


class PromotionDecisionService:
    """Apply C-MEM-10 promotion decisions through the canonical store and ledger."""

    def __init__(
        self,
        *,
        store: PromotionDecisionStore,
        actor: Actor,
        policy_ref: str | None = None,
        procedural_snapshot_ref: str | None = None,
        run_id: str | None = None,
        step_id: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        cli_profile: str | None = None,
        tracer_provider: object | None = None,
    ) -> None:
        self._store = store
        self._actor = actor
        self._policy_ref = policy_ref
        self._procedural_snapshot_ref = procedural_snapshot_ref
        self._run_id = run_id
        self._step_id = step_id
        self._provider = provider
        self._model = model
        self._cli_profile = cli_profile
        self._tracer_provider = tracer_provider

    def propose_for_review(
        self,
        candidate: PromotionCandidate,
        *,
        timestamp: datetime,
        injection_policy: SemanticInjectionPolicy,
        preference_details: PreferencePromotionDetails | None = None,
        rationale: str | None = None,
        tags: Sequence[str] = (),
    ) -> PromotionDecisionResult:
        """Persist a proposed semantic/procedural record for operator review."""

        return self._persist_decision(
            candidate,
            provenance=self._provenance_snapshot(candidate),
            status=SemanticRecordStatus.PROPOSED,
            operation_kind=MemoryOperationKind.PROPOSE_PROMOTION,
            timestamp=timestamp,
            injection_policy=injection_policy,
            preference_details=preference_details,
            rationale=rationale,
            tags=tags,
            review_reason=None,
            supersedes=(),
            statement_override=None,
        )

    def approve(
        self,
        candidate: PromotionCandidate,
        *,
        timestamp: datetime,
        injection_policy: SemanticInjectionPolicy | None = None,
        preference_details: PreferencePromotionDetails | None = None,
        operator_approved: bool = False,
        rationale: str | None = None,
        tags: Sequence[str] = (),
        supersedes: Sequence[MemoryID] = (),
    ) -> PromotionDecisionResult:
        """Persist an active record when policy or operator review allows it."""

        provenance = self._provenance_snapshot(candidate)
        if not self._auto_promotable(candidate, provenance) and not operator_approved:
            raise PromotionReviewRequiredError(
                "candidate cannot become active until operator review approves it"
            )
        if injection_policy is None:
            if candidate.proposed_kind is PromotionCandidateKind.PREFERENCE:
                raise PreferencePromotionValidationError(
                    "preference promotion requires injection_policy"
                )
            raise ValueError("active promotion requires an injection_policy")
        return self._persist_decision(
            candidate,
            provenance=provenance,
            status=SemanticRecordStatus.ACTIVE,
            operation_kind=MemoryOperationKind.PROMOTE,
            timestamp=timestamp,
            injection_policy=injection_policy,
            preference_details=preference_details,
            rationale=rationale,
            tags=tags,
            review_reason=None,
            supersedes=supersedes,
            statement_override=None,
        )

    def deny(
        self,
        candidate: PromotionCandidate,
        *,
        timestamp: datetime,
        reason: str,
        tags: Sequence[str] = (),
    ) -> PromotionDecisionResult:
        """Persist a denied record and append a denial ledger entry."""

        return self._persist_decision(
            candidate,
            provenance=self._provenance_snapshot(candidate),
            status=SemanticRecordStatus.DENIED,
            operation_kind=MemoryOperationKind.DENY_PROMOTION,
            timestamp=timestamp,
            injection_policy=SemanticInjectionPolicy.NEVER,
            preference_details=None,
            rationale=None,
            tags=tags,
            review_reason=reason,
            supersedes=(),
            statement_override=None,
        )

    def edit_and_approve(
        self,
        candidate: PromotionCandidate,
        *,
        statement: str,
        timestamp: datetime,
        injection_policy: SemanticInjectionPolicy,
        preference_details: PreferencePromotionDetails | None = None,
        operator_approved: bool = False,
        rationale: str | None = None,
        tags: Sequence[str] = (),
        supersedes: Sequence[MemoryID] = (),
    ) -> PromotionDecisionResult:
        """Apply an operator-edited statement and persist it as active."""

        provenance = self._provenance_snapshot(candidate)
        if not self._auto_promotable(candidate, provenance) and not operator_approved:
            raise PromotionReviewRequiredError(
                "candidate cannot become active until operator review approves it"
            )
        if not statement.strip():
            raise ValueError("edited promotion statement cannot be empty")
        return self._persist_decision(
            candidate,
            provenance=provenance,
            status=SemanticRecordStatus.ACTIVE,
            operation_kind=MemoryOperationKind.PROMOTE,
            timestamp=timestamp,
            injection_policy=injection_policy,
            preference_details=preference_details,
            rationale=rationale,
            tags=tags,
            review_reason=None,
            supersedes=supersedes,
            statement_override=statement,
        )

    def _provenance_snapshot(self, candidate: PromotionCandidate) -> _EffectiveProvenance:
        """Resolve the cited source records ONCE and freeze the result.

        Called at the START of every service call that consumes a candidate the
        service did not itself derive, and the only place in this class that
        reads a source record. Everything downstream - the activation gate and
        the durable write's mark alike - is a projection of the value returned
        here, so a call cannot admit an activation on one reading and persist a
        different one.
        """

        aggregate = _aggregate_provenance(
            [
                _resolve_source_provenance(self._store, memory_id, run_id=self._run_id)
                for memory_id in candidate.source_memory_refs
            ]
        )
        return _EffectiveProvenance(
            aggregate=aggregate,
            risk_flags=_normalized_risk_flags(
                candidate,
                gated=cross_family_capture_flagged(aggregate),
            ),
        )

    def _auto_promotable(
        self,
        candidate: PromotionCandidate,
        provenance: _EffectiveProvenance,
    ) -> bool:
        """Override the candidate's `auto_promote_allowed` claim from the snapshot.

        C-MEM-10 v1.2 surface 2, and the shape matters as much as the effect:
        this OVERRIDES the input to the pre-existing disjunction rather than
        adding a second refusal branch ahead of it. A re-derived `true` /
        `unknown` blocks AUTOMATIC activation only - explicit operator approval
        still activates, because approval records a decision to accept the
        provenance and eligibility is preserved, not removed. A refusal that
        outranked operator approval would implement the reading the operator
        explicitly foreclosed.

        It is deliberately blind to `candidate.risk_flags`: the two cases no
        value-level check can catch are a candidate that OMITS the mark while
        claiming auto-promotability, and one carrying the illegal pair reached
        through `model_copy(update=...)`, which bypasses after-validators.
        """

        return candidate.auto_promote_allowed and not provenance.gated

    def _persist_decision(
        self,
        candidate: PromotionCandidate,
        *,
        provenance: _EffectiveProvenance,
        status: SemanticRecordStatus,
        operation_kind: MemoryOperationKind,
        timestamp: datetime,
        injection_policy: SemanticInjectionPolicy,
        preference_details: PreferencePromotionDetails | None,
        rationale: str | None,
        tags: Sequence[str],
        review_reason: str | None,
        supersedes: Sequence[MemoryID],
        statement_override: str | None,
    ) -> PromotionDecisionResult:
        _validate_preference_promotion(
            candidate,
            status=status,
            injection_policy=injection_policy,
            preference_details=preference_details,
        )
        _require_canonical_candidate_scope(candidate)
        # The SINGLE choke point, covering all four callers by construction -
        # `propose_for_review` (PROPOSED), `approve` (ACTIVE), `deny` (DENIED),
        # `edit_and_approve` (ACTIVE) - and every future caller by the same
        # construction. `deny` is exactly the one a per-method fix would miss.
        #
        # The normalized flags are handed to the content builders as VALUES; no
        # normalized `PromotionCandidate` is constructed. That is the deliberate
        # resolution of the interplay with the slice-3a model validator: a
        # candidate that omits the mark against a `true` source legitimately
        # asserts `auto_promote_allowed=True`, so re-building it with the mark
        # injected would hit the validator's illegal-pair refusal and turn a
        # correct normalization into a crash. Normalizing the values keeps the
        # untrusted candidate untouched (it is the caller's object) while making
        # the DURABLE statement the re-derived one.
        record = _promotion_record(
            candidate,
            risk_flags=provenance.risk_flags,
            status=status,
            timestamp=timestamp,
            injection_policy=injection_policy,
            preference_details=preference_details,
            rationale=rationale,
            tags=tags,
            review_reason=review_reason,
            supersedes=supersedes,
            statement_override=statement_override,
            policy_ref=self._policy_ref,
        )
        with memory_telemetry_span(
            self._tracer_provider,
            tracer_name="harness.runtime.memory_promotion",
            operation_name=MemoryTelemetryOperationName.PROMOTION,
            operation_kind=operation_kind.value,
            tier=record.envelope.tier.value,
            provider=self._provider,
            model=self._model,
            cli_profile=self._cli_profile,
            policy_decision=status.value,
            record_count=1,
        ):
            self._commit_record(record, candidate=candidate, provenance=provenance, status=status)
            operation_result = self._store.append_memory_operation(
                self._operation_payload(
                    candidate,
                    record=record,
                    operation_kind=operation_kind,
                    timestamp=timestamp,
                )
            )
        return PromotionDecisionResult(
            status=status,
            record=record,
            memory_id=record.envelope.memory_id,
            operation_kind=operation_kind,
            operation_result=operation_result,
        )

    def _commit_record(
        self,
        record: MemoryStoreRecord,
        *,
        candidate: PromotionCandidate,
        provenance: _EffectiveProvenance,
        status: SemanticRecordStatus,
    ) -> None:
        """Write the decision record, binding an ACTIVATION to its snapshot.

        MECHANISM CHOSEN (C-MEM-10 v1.2 / U-MEM-27 commit binding), and why.
        The obligation is that an activation must not commit against a source
        whose recorded provenance changed after the snapshot, and the round-10
        constraint is that the verification be ATOMIC WITH PERSISTENCE - a
        re-check the runtime performs and then follows with a separate
        `write_record` call is still a TOCTOU window, because the store's own
        locks cover individual writes only. Of the three shapes the plan leaves
        open, a version/generation token is unavailable (the store exposes none,
        and the envelope is hash-inert so `memory_id` cannot serve as one - a
        rewrite carrying different `captured_cross_family` collides on the SAME
        id, which is the whole reason the race is live), and a service-local
        lock would only pretend atomicity (the capture writers that append new
        provenance lines do not hold it). What is left is a GUARDED CONDITIONAL
        WRITE executed inside the store's own write locks: the store's new
        generic `write_record_guarded` evaluates this precondition and performs
        the write it authorizes without releasing those locks in between, so no
        interleaved writer can land between the two. The precondition is kept
        promotion-free on the store side - it is an opaque callable - so
        harness-is gains a general compare-and-commit primitive rather than
        promotion semantics it has no business knowing (carrier-home discipline).

        The compared value is the snapshot's DECISION-BEARING projection, not
        raw equality of every per-source tri-state. `gated` is exactly what both
        the activation decision and the durable mark depend on, so a mutation
        that cannot change either (`true` -> `unknown`, say: both gate, both
        carry the flag) is correctly not a conflict, while any mutation crossing
        the `false` boundary in either direction is. Binding to something
        narrower would miss real changes; binding to something wider would
        refuse commits that no reading of the store could have decided
        differently.

        Scope, stated rather than implied: the guard is applied to the
        ACTIVATION path only. A `PROPOSED` or `DENIED` write authorizes nothing
        - it records that review is owed or was refused - so a concurrent source
        append must not be able to make a denial fail. Those writes still state
        the snapshot's re-derived mark; they simply are not conflict-bound to it.
        """

        if status is not SemanticRecordStatus.ACTIVE:
            self._store.write_record(record)
            return

        def _provenance_unchanged() -> bool:
            return self._provenance_snapshot(candidate).gated == provenance.gated

        try:
            self._store.write_record_guarded(record, precondition=_provenance_unchanged)
        except MemoryStoreGuardedWriteConflictError as exc:
            raise PromotionProvenanceChangedError(
                "cited source provenance changed after the promotion snapshot; "
                "the activation was not committed"
            ) from exc

    def _operation_payload(
        self,
        candidate: PromotionCandidate,
        *,
        record: MemoryStoreRecord,
        operation_kind: MemoryOperationKind,
        timestamp: datetime,
    ) -> MemoryOperationPayload:
        action_id = Identifier(
            f"promotion:{operation_kind.value}:{candidate.candidate_id}:{record.envelope.memory_id}"
        )
        return MemoryOperationPayload(
            action_id=action_id,
            idempotency_key=Identifier(f"idempotent:{action_id}"),
            actor=self._actor,
            timestamp=timestamp,
            operation_kind=operation_kind,
            operation_projection=MemoryOperationProjection.for_operation_kind(operation_kind),
            run_id=self._run_id,
            step_id=self._step_id,
            provider=self._provider,
            model=self._model,
            cli_profile=self._cli_profile,
            engine_class=None,
            memory_refs=(record.envelope.memory_id,),
            policy_ref=self._policy_ref,
            procedural_snapshot_ref=self._procedural_snapshot_ref,
        )


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


def _require_canonical_candidate_scope(candidate: PromotionCandidate) -> None:
    """Refuse to persist a candidate whose scope was never canonicalized.

    The write-side backstop for candidates built outside `_candidate_from_hint`
    (the tool-executor path builds its own, and a caller may hand-build one). It
    REFUSES rather than canonicalizing in place: canonicalizing here would fix
    the persisted scope while leaving `candidate_id` and `risk_flags` derived
    from the raw identifier - exactly the split the U-MEM-26 ordering rule
    exists to prevent. Canonicalization belongs ahead of those derivations, so a
    non-canonical scope arriving at the write is a bypass, not something to
    quietly repair.
    """
    resolution = resolve_scope_family(candidate.suggested_scope)
    if resolution.family_out_of_domain:
        raise PromotionScopeValueDomainError(
            scope_family_out_of_domain_message(candidate.suggested_scope)
        )
    if resolution.scope != candidate.suggested_scope:
        raise PromotionScopeValueDomainError(
            "promotion candidate scope provider_family "
            f"{candidate.suggested_scope.provider_family!r} reached the record write "
            "un-canonicalized; canonicalize it before candidate identity and risk "
            "flags are derived (U-MEM-26 write-boundary ordering)"
        )


def canonical_candidate_scope(scope: MemoryScope) -> MemoryScope:
    """Canonicalize a candidate scope's `provider_family`, or deny it.

    U-MEM-26 write-boundary ORDERING rule for the promotion surface: this must
    run BEFORE risk-flag and candidate-identity derivation, not merely before
    the record write. `_candidate_id` hashes the whole suggested scope, so
    canonicalizing at the write would leave key-vs-value-equivalent inputs
    receiving DIFFERENT candidate identities.

    The sibling defect - a registered alias of the record's own family FALSELY
    flagged `CROSS_SCOPE` - was fixed at its own site instead (Codex R3 [P2-b],
    `_family_escapes_source`): the SOURCE side is a stored value this ordering
    rule never reaches, so ordering alone could not close it.
    """
    resolution = resolve_scope_family(scope)
    if resolution.family_out_of_domain:
        raise PromotionScopeValueDomainError(scope_family_out_of_domain_message(scope))
    return resolution.scope


def _candidate_from_hint(
    record: MemoryStoreRecord,
    hint: PromotionCandidateHint,
    resolution: MemoryPromotionResolution,
) -> PromotionCandidate:
    # Ahead of EVERY derivation below, per the U-MEM-26 ordering rule.
    hint = hint.model_copy(
        update={"suggested_scope": canonical_candidate_scope(hint.suggested_scope)}
    )
    source_refs = _merge_source_refs(record.envelope.source_refs, hint.source_refs)
    # The C-MEM-10 provenance read happens HERE and exactly once per candidate.
    # The predicates below consume the DERIVED FLAG SET, never a second read of
    # `record.envelope.captured_cross_family` - two parallel derivations of the
    # same fact are free to diverge under later edits, which is the advisory-flag
    # condition the `B-92` fork found and C-MEM-10 now forbids.
    risk_flags = _risk_flags(
        hint,
        source_scope=record.envelope.scope,
        captured_cross_family=record.envelope.captured_cross_family,
    )
    preference_source = _preference_source(
        hint,
        source_refs=source_refs,
        source_content=record.content,
    )
    review_required = _review_required(hint, resolution, risk_flags=risk_flags)
    auto_promote_allowed = _auto_promote_allowed(
        hint,
        resolution=resolution,
        review_required=review_required,
        risk_flags=risk_flags,
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
    captured_cross_family: CapturedCrossFamily,
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
    # C-MEM-10 v1.2: `cross_family_capture` is RESERVED to this derivation, so
    # whatever the hint said about it is discarded and re-derived from the
    # source record - unconditionally and in BOTH directions. A hint can neither
    # introduce the mark on a `false` source nor suppress it on a `true` /
    # `unknown` one. This is an overwrite, not a refusal: a hint carrying the
    # value is not malformed, merely not authoritative. `cross_scope` above is
    # untouched and stays independent - neither flag is derived from the other,
    # and a candidate may carry both.
    flags.discard(PromotionRiskFlag.CROSS_FAMILY_CAPTURE)
    if cross_family_capture_flagged(captured_cross_family):
        flags.add(PromotionRiskFlag.CROSS_FAMILY_CAPTURE)
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
        "cli_profile",
        "tenant",
    ):
        source_value = getattr(source_scope, field_name)
        candidate_value = getattr(candidate_scope, field_name)
        if source_value is not None and candidate_value != source_value:
            return True
    return _family_escapes_source(candidate_scope.provider_family, source_scope.provider_family)


def _family_escapes_source(candidate_family: str | None, source_family: str | None) -> bool:
    """True when the candidate's family leaves the SOURCE record's partition.

    `provider_family` is the one scope field with a value domain, so it is the
    one field a raw string comparison gets wrong. The candidate side is already
    canonical by the U-MEM-26 ordering rule, but the SOURCE side is a STORED
    value that may predate C-MEM-03 v1.1: a legacy record persisted under the
    registered key `ollama` names the SAME partition as a `local_open_weight`
    candidate, and comparing the raw strings flagged that same-family promotion
    `CROSS_SCOPE` - forcing review and blocking auto-promotion. Both sides are
    therefore canonicalized before they are compared.

    An out-of-domain value on EITHER side stays fail-closed. It names a
    partition this substrate cannot resolve, so the candidate cannot be shown
    to stay inside the source's - and `CROSS_SCOPE` is the conservative answer
    (a review, not a disclosure).
    """
    if source_family is None:
        # Preserved verbatim from the shared loop above: an unpartitioned
        # source constrains nothing, whatever the candidate names.
        return False
    source_canonical = canonical_scope_family(source_family)
    if source_canonical is None or candidate_family is None:
        return True
    candidate_canonical = canonical_scope_family(candidate_family)
    if candidate_canonical is None:
        return True
    return candidate_canonical != source_canonical


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
    *,
    risk_flags: Sequence[PromotionRiskFlag],
) -> bool:
    if PromotionRiskFlag.CROSS_FAMILY_CAPTURE in risk_flags:
        # Unconditional on policy: not a decision value, not a review mode, not
        # a confidence threshold.
        return True
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
    risk_flags: Sequence[PromotionRiskFlag],
) -> bool:
    if PromotionRiskFlag.CROSS_FAMILY_CAPTURE in risk_flags:
        # AHEAD of the `proposed_kind` branch below, deliberately: a gate placed
        # only on the semantic return would leave cross-family PROCEDURAL
        # candidates auto-promoting under `PROMOTE_PROCEDURAL` + `AUTOMATIC`.
        return False
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


def _promotion_record(
    candidate: PromotionCandidate,
    *,
    risk_flags: Sequence[PromotionRiskFlag],
    status: SemanticRecordStatus,
    timestamp: datetime,
    injection_policy: SemanticInjectionPolicy,
    preference_details: PreferencePromotionDetails | None,
    rationale: str | None,
    tags: Sequence[str],
    review_reason: str | None,
    supersedes: Sequence[MemoryID],
    statement_override: str | None,
    policy_ref: str | None,
) -> MemoryStoreRecord:
    kind = _record_kind_for_candidate(candidate)
    tier = _tier_for_record_kind(kind)
    content = _record_content(
        candidate,
        risk_flags=risk_flags,
        status=status,
        injection_policy=injection_policy,
        preference_details=preference_details,
        rationale=rationale,
        tags=tags,
        review_reason=review_reason,
        statement_override=statement_override,
        policy_ref=policy_ref,
    )
    content_hash = compute_memory_content_hash(content)
    return MemoryStoreRecord(
        envelope=MemoryRecordEnvelope(
            memory_id=derive_memory_id(tier, kind, content_hash),
            schema_version="promotion-record/v1",
            tier=tier,
            kind=kind,
            created_at=timestamp,
            updated_at=None,
            source_refs=candidate.source_refs,
            scope=candidate.suggested_scope,
            content_hash=content_hash,
            supersedes=tuple(supersedes),
        ),
        content=content,
    )


def _record_kind_for_candidate(candidate: PromotionCandidate) -> MemoryRecordKind:
    if candidate.proposed_kind is PromotionCandidateKind.FACT:
        return MemoryRecordKind.SEMANTIC_FACT
    if candidate.proposed_kind is PromotionCandidateKind.DECISION:
        return MemoryRecordKind.DECISION
    if candidate.proposed_kind is PromotionCandidateKind.CONVENTION:
        return MemoryRecordKind.CONVENTION
    if candidate.proposed_kind is PromotionCandidateKind.FAILURE_LEARNING:
        return MemoryRecordKind.FAILURE_LEARNING
    if candidate.proposed_kind is PromotionCandidateKind.RESEARCH:
        return MemoryRecordKind.RESEARCH
    if candidate.proposed_kind is PromotionCandidateKind.PREFERENCE:
        return MemoryRecordKind.PREFERENCE
    if candidate.proposed_kind is PromotionCandidateKind.PROCEDURAL_UPDATE:
        return MemoryRecordKind.PROCEDURAL_SNAPSHOT
    raise AssertionError(f"unhandled promotion kind {candidate.proposed_kind.value}")


def _tier_for_record_kind(kind: MemoryRecordKind) -> MemoryTier:
    if kind is MemoryRecordKind.PROCEDURAL_SNAPSHOT:
        return MemoryTier.PROCEDURAL
    return MemoryTier.SEMANTIC


def _record_content(
    candidate: PromotionCandidate,
    *,
    risk_flags: Sequence[PromotionRiskFlag],
    status: SemanticRecordStatus,
    injection_policy: SemanticInjectionPolicy,
    preference_details: PreferencePromotionDetails | None,
    rationale: str | None,
    tags: Sequence[str],
    review_reason: str | None,
    statement_override: str | None,
    policy_ref: str | None,
) -> dict[str, object]:
    if candidate.proposed_kind is PromotionCandidateKind.PROCEDURAL_UPDATE:
        return _procedural_record_content(
            candidate,
            risk_flags=risk_flags,
            status=status,
            injection_policy=injection_policy,
            rationale=rationale,
            tags=tags,
            review_reason=review_reason,
            statement_override=statement_override,
            policy_ref=policy_ref,
        )
    return _semantic_record_content(
        candidate,
        risk_flags=risk_flags,
        status=status,
        injection_policy=injection_policy,
        preference_details=preference_details,
        rationale=rationale,
        tags=tags,
        review_reason=review_reason,
        statement_override=statement_override,
    )


def _risk_flag_values(risk_flags: Sequence[PromotionRiskFlag]) -> list[str]:
    """C-MEM-10 durable-review-artifact carrier for the decision's risk flags.

    The promotion-written record's own CONTENT states them, so an operator
    inspecting the durable record can see why it was held. `MemoryStoreRecord.
    content` is an open mapping, so no model edit is needed; `_promotion_record`
    hashes the extended content, which means promotion records written from here
    on carry one more key and therefore a different `content_hash` / `memory_id`
    than they would have. That is forward-shape only - no already-written record
    is rewritten, re-hashed, or re-identified.

    Takes the flag VALUES rather than the candidate: what is persisted is the
    `_persist_decision` choke point's NORMALIZED set, re-derived from the frozen
    provenance snapshot, never the untrusted candidate's own claim.

    Deliberately NOT the C-MEM-08 ledger row: `MemoryOperationPayload` is closed
    (`extra="forbid"`), and a field there would be the C-MEM-08 amendment this
    arc forswears, so `_operation_payload` is unchanged.
    """

    return [flag.value for flag in risk_flags]


def _semantic_record_content(
    candidate: PromotionCandidate,
    *,
    risk_flags: Sequence[PromotionRiskFlag],
    status: SemanticRecordStatus,
    injection_policy: SemanticInjectionPolicy,
    preference_details: PreferencePromotionDetails | None,
    rationale: str | None,
    tags: Sequence[str],
    review_reason: str | None,
    statement_override: str | None,
) -> dict[str, object]:
    content: dict[str, object] = {
        "candidate_id": candidate.candidate_id,
        "source_memory_refs": [str(memory_id) for memory_id in candidate.source_memory_refs],
        "semantic_kind": candidate.proposed_kind.value,
        "statement": statement_override or candidate.statement,
        "risk_flags": _risk_flag_values(risk_flags),
        "rationale": rationale,
        "evidence": [ref.model_dump(mode="json") for ref in candidate.source_refs],
        "confidence": candidate.confidence.value,
        "status": status.value,
        "ttl": None,
        "expires_at": None,
        "injection_policy": injection_policy.value,
        "tags": [str(tag) for tag in tags],
    }
    if review_reason is not None:
        content["review_reason"] = review_reason
    if candidate.proposed_kind is PromotionCandidateKind.PREFERENCE:
        assert preference_details is not None
        content.update(
            {
                "preference_subject": preference_details.preference_subject.value,
                "preference_strength": preference_details.preference_strength.value,
                "source_authority": preference_details.source_authority.value,
                "confirmation_required": preference_details.confirmation_required,
            }
        )
    return content


def _procedural_record_content(
    candidate: PromotionCandidate,
    *,
    risk_flags: Sequence[PromotionRiskFlag],
    status: SemanticRecordStatus,
    injection_policy: SemanticInjectionPolicy,
    rationale: str | None,
    tags: Sequence[str],
    review_reason: str | None,
    statement_override: str | None,
    policy_ref: str | None,
) -> dict[str, object]:
    content: dict[str, object] = {
        "snapshot_id": candidate.candidate_id,
        "workflow_id": candidate.suggested_scope.workflow,
        "cli_profile": candidate.suggested_scope.cli_profile,
        "prompt_refs": [],
        "skill_refs": [],
        "routing_manifest_ref": None,
        "instruction_file_refs": [],
        "memory_policy_ref": policy_ref,
        "procedural_update": statement_override or candidate.statement,
        "risk_flags": _risk_flag_values(risk_flags),
        "rationale": rationale,
        "evidence": [ref.model_dump(mode="json") for ref in candidate.source_refs],
        "confidence": candidate.confidence.value,
        "status": status.value,
        "injection_policy": injection_policy.value,
        "tags": [str(tag) for tag in tags],
    }
    if review_reason is not None:
        content["review_reason"] = review_reason
    return content


def _validate_preference_promotion(
    candidate: PromotionCandidate,
    *,
    status: SemanticRecordStatus,
    injection_policy: SemanticInjectionPolicy,
    preference_details: PreferencePromotionDetails | None,
) -> None:
    if candidate.proposed_kind is not PromotionCandidateKind.PREFERENCE:
        if preference_details is not None:
            raise PreferencePromotionValidationError(
                "preference_details are only valid for preference candidates"
            )
        return
    if preference_details is None:
        raise PreferencePromotionValidationError("preference promotion requires preference_details")
    if not candidate.source_refs:
        raise PreferencePromotionValidationError("preference promotion requires source evidence")
    if (
        status is SemanticRecordStatus.ACTIVE
        and preference_details.source_authority
        is PreferenceSourceAuthority.INFERRED_FROM_REPETITION
        and len(candidate.source_refs) < 2
    ):
        raise PreferencePromotionValidationError(
            "inferred preference promotion requires at least two source refs "
            "or must remain proposed"
        )
    if (
        preference_details.preference_strength is PreferenceStrength.MANDATORY
        and not _scope_has_binding(candidate.suggested_scope)
    ):
        raise PreferencePromotionValidationError(
            "mandatory preference promotion requires a scoped binding"
        )


def _scope_has_binding(scope: MemoryScope) -> bool:
    return any(
        getattr(scope, field_name) is not None
        for field_name in (
            "project",
            "workflow",
            "workload_class",
            "provider_family",
            "cli_profile",
            "tenant",
        )
    )


__all__ = [
    "PreferenceCandidateSource",
    "PreferencePromotionDetails",
    "PreferencePromotionValidationError",
    "PreferenceSourceAuthority",
    "PreferenceStrength",
    "PreferenceSubject",
    "PromotionCandidate",
    "PromotionCandidateConfidence",
    "PromotionCandidateExtractor",
    "PromotionCandidateHint",
    "PromotionCandidateKind",
    "PromotionDecisionResult",
    "PromotionDecisionService",
    "PromotionDecisionStore",
    "PromotionProvenanceChangedError",
    "PromotionReviewRequiredError",
    "PromotionRiskFlag",
    "PromotionScopeValueDomainError",
    "SemanticInjectionPolicy",
    "SemanticRecordStatus",
    "canonical_candidate_scope",
]
