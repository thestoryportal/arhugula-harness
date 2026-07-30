"""U-MEM-27 slice 3b - the C-MEM-10 v1.2 activation boundary and its snapshot.

Witnesses for the SERVICE-CALL half of U-MEM-27
(`Implementation_Plan_Memory_Substrate_v1.md` U-MEM-27, verification bullets
:1066 and :1083-:1092):

* the single-snapshot witness (:1066) - a counting, mutating store double proves
  exactly ONE decision-bearing resolution per service call, and that the gate
  and the persisted mark agree
* the commit-binding witness (:1066) - a source mutated between the snapshot and
  the durable write, hooked at the PRECONDITION EVALUATION POINT inside the
  write path, must not auto-activate on the stale snapshot
* activation-boundary witness (ii), the copied illegal pair (:1083)
* activation-boundary witness (iii), the OMITTED mark (:1084) - the case no
  value-level check can catch - and its positive control (:1085)
* the eligibility-preserved pair (:1074), the anti-reading-C witness
* the mixed-source worst-value witnesses (:1086)
* the fail-closed branches, one per branch (:1090)
* the durable normalization witnesses at all four `_persist_decision` call
  sites: `PROPOSED` both directions (:1087), both `ACTIVE` writes both
  directions (:1088), and `DENIED` (:1089)

The slice-3a read-side witnesses live at `test_u_mem_27_promotion_gate.py`.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest
from harness_core import DeploymentSurface
from harness_is.memory_operation_ledger import (
    MemoryOperationPayload,
    MemoryOperationWriteResult,
)
from harness_is.memory_path_registry import MemoryRootBinding
from harness_is.memory_policy import PromotionDecision, ReviewMode
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
from harness_is.memory_store import (
    CanonicalMemoryStore,
    MemoryStoreGuardedWriteConflictError,
    MemoryStoreRecord,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.memory_promotion import (
    PromotionCandidate,
    PromotionCandidateConfidence,
    PromotionCandidateKind,
    PromotionDecisionResult,
    PromotionDecisionService,
    PromotionDecisionStore,
    PromotionProvenanceChangedError,
    PromotionReviewRequiredError,
    PromotionRiskFlag,
    SemanticInjectionPolicy,
    SemanticRecordStatus,
)

_NOW = datetime(2026, 7, 29, 15, 0, 0, tzinfo=UTC)
_POLICY_REF = "policy:u-mem-27-activation"
_RUN_ID = "run-u-mem-27-activation"
_FLAG = PromotionRiskFlag.CROSS_FAMILY_CAPTURE
_GATED_ARMS = (CapturedCrossFamily.TRUE, CapturedCrossFamily.UNKNOWN)


def _actor() -> Actor:
    return Actor(actor_class=ActorClass.AGENT, actor_id="u-mem-27")


def _scope() -> MemoryScope:
    return MemoryScope(
        project="arhugula-v2",
        workflow="memory-substrate",
        workload_class="coding-arc",
        provider_family="openai",
        cli_profile="codex",
        visibility=MemoryVisibility.WORKFLOW,
    )


def _store(tmp_path: Path) -> CanonicalMemoryStore:
    return CanonicalMemoryStore(
        root_binding=MemoryRootBinding(default_root=tmp_path / "memory"),
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )


def _semantic_source(
    provenance: CapturedCrossFamily,
    *,
    tag: str,
) -> MemoryStoreRecord:
    """A SEMANTIC_FACT source record - resolvable without any `run_id`."""

    content: dict[str, object] = {
        "semantic_kind": MemoryRecordKind.SEMANTIC_FACT.value,
        "statement": f"Cited source record {tag}.",
        "status": "active",
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
            source_refs=(SourceRef(ref_type=SourceRefType.OPERATOR, ref=f"operator:{tag}"),),
            scope=_scope(),
            content_hash=content_hash,
            captured_cross_family=provenance,
        ),
        content=content,
    )


def _stored_source(
    store: CanonicalMemoryStore,
    provenance: CapturedCrossFamily,
    *,
    tag: str = "primary",
) -> MemoryID:
    record = _semantic_source(provenance, tag=tag)
    store.write_record(record)
    return record.envelope.memory_id


def _unwritten_source(tag: str = "absent") -> MemoryID:
    """A well-formed reference to a record that was never written."""

    return _semantic_source(CapturedCrossFamily.FALSE, tag=tag).envelope.memory_id


def _candidate(
    *,
    source_memory_refs: Sequence[MemoryID],
    risk_flags: Sequence[PromotionRiskFlag] = (),
    review_required: bool = False,
    auto_promote_allowed: bool = True,
    kind: PromotionCandidateKind = PromotionCandidateKind.FACT,
) -> PromotionCandidate:
    """A HAND-BUILT candidate - it touches neither extraction path."""

    return PromotionCandidate(
        candidate_id="promocand:activation-boundary",
        source_refs=(SourceRef(ref_type=SourceRefType.OPERATOR, ref="operator:u-mem-27"),),
        source_memory_refs=tuple(source_memory_refs),
        proposed_kind=kind,
        statement="A hand-built candidate reaching the activation boundary.",
        confidence=PromotionCandidateConfidence.HIGH,
        suggested_scope=_scope(),
        risk_flags=tuple(risk_flags),
        policy_decision=PromotionDecision.PROMOTE_SEMANTIC,
        review_mode=ReviewMode.AUTOMATIC,
        review_required=review_required,
        auto_promote_allowed=auto_promote_allowed,
    )


def _service(
    store: object,
    *,
    run_id: str | None = _RUN_ID,
) -> PromotionDecisionService:
    return PromotionDecisionService(
        store=cast("PromotionDecisionStore", store),
        actor=_actor(),
        policy_ref=_POLICY_REF,
        run_id=run_id,
    )


def _persisted_risk_flags(
    store: CanonicalMemoryStore,
    result: PromotionDecisionResult,
) -> list[str]:
    """Read the record BACK from the store - never the in-memory candidate."""

    stored = store.read_record(result.memory_id, MemoryRecordKind.SEMANTIC_FACT)
    flags = stored.content["risk_flags"]
    assert isinstance(flags, list)
    return [str(flag) for flag in flags]


# ---------------------------------------------------------------------------
# The counting / mutating store double
# ---------------------------------------------------------------------------


class _MutatingSourceStore:
    """A `PromotionDecisionStore` double that counts and mutates.

    It delegates every durable effect to a real `CanonicalMemoryStore`, so the
    "nothing was written" assertions are made against real store state rather
    than against the double's own bookkeeping. What it adds is the two hooks the
    :1066 witnesses need: a count of how many times the cited source was
    resolved, and a controlled point at which that source's provenance changes.

    `mutate_at="at_write"` lands the mutation INSIDE the write path, immediately
    before the precondition is evaluated - the between-snapshot-and-write
    interleaving, hooked where the real store evaluates the guard, rather than
    merely between two service calls.
    """

    def __init__(
        self,
        inner: CanonicalMemoryStore,
        *,
        source: MemoryStoreRecord,
        mutate_to: CapturedCrossFamily | None = None,
        mutate_at: str = "after_first_read",
    ) -> None:
        self.inner = inner
        self._source = source
        self.provenance = source.envelope.captured_cross_family
        self._mutate_to = mutate_to
        self._mutate_at = mutate_at
        self.source_resolutions = 0
        self.decision_resolutions: int | None = None
        self.written: list[MemoryStoreRecord] = []

    @property
    def source_memory_id(self) -> MemoryID:
        return self._source.envelope.memory_id

    def read_record(
        self,
        memory_id: MemoryID,
        kind: MemoryRecordKind,
        *,
        run_id: str | None = None,
        audit_mode: bool = False,
    ) -> MemoryStoreRecord:
        if memory_id != self.source_memory_id:
            return self.inner.read_record(memory_id, kind, run_id=run_id, audit_mode=audit_mode)
        self.source_resolutions += 1
        served = self._source.model_copy(
            update={
                "envelope": self._source.envelope.model_copy(
                    update={"captured_cross_family": self.provenance}
                )
            }
        )
        if (
            self._mutate_at == "after_first_read"
            and self.source_resolutions == 1
            and self._mutate_to is not None
        ):
            self.provenance = self._mutate_to
        return served

    def write_record(self, record: MemoryStoreRecord) -> object:
        self.written.append(record)
        return self.inner.write_record(record)

    def write_record_guarded(
        self,
        record: MemoryStoreRecord,
        *,
        precondition: Callable[[], bool],
    ) -> object:
        # Everything resolved before this point was resolved FOR THE DECISION.
        # A two-read implementation - one lookup at the gate, a second at the
        # durable write - shows 2 here; the bound re-check that follows is not
        # a decision resolution and is deliberately not counted.
        self.decision_resolutions = self.source_resolutions
        if self._mutate_at == "at_write" and self._mutate_to is not None:
            self.provenance = self._mutate_to
        if not precondition():
            raise MemoryStoreGuardedWriteConflictError("fake guarded-write conflict")
        return self.write_record(record)

    def append_memory_operation(
        self,
        payload: MemoryOperationPayload,
    ) -> MemoryOperationWriteResult:
        return self.inner.append_memory_operation(payload)


class _IOFailingSourceStore:
    """Delegates every effect to a real store, except ONE cited source's read.

    That read raises a filesystem I/O error, which is what the concrete store
    does when the record is on disk but unreadable - `read_text` on a file whose
    mode or parent directory denies it, a vanished mount, EMFILE. Modelled at
    the `PromotionDecisionStore` seam rather than by `chmod`, so the branch is
    deterministic regardless of the privileges the suite runs under (`chmod`
    denies nothing to root).

    `fail_after` delays the failure by N successful reads, which turns the same
    double into a source that was readable at the snapshot and is not at commit.
    """

    def __init__(
        self,
        inner: CanonicalMemoryStore,
        *,
        failing: MemoryID,
        error: Exception,
        fail_after: int = 0,
    ) -> None:
        self.inner = inner
        self._failing = failing
        self._error = error
        self._fail_after = fail_after
        self.reads = 0

    def read_record(
        self,
        memory_id: MemoryID,
        kind: MemoryRecordKind,
        *,
        run_id: str | None = None,
        audit_mode: bool = False,
    ) -> MemoryStoreRecord:
        if memory_id == self._failing:
            self.reads += 1
            if self.reads > self._fail_after:
                raise self._error
        return self.inner.read_record(memory_id, kind, run_id=run_id, audit_mode=audit_mode)

    def write_record(self, record: MemoryStoreRecord) -> object:
        return self.inner.write_record(record)

    def write_record_guarded(
        self,
        record: MemoryStoreRecord,
        *,
        precondition: Callable[[], bool],
    ) -> object:
        return self.inner.write_record_guarded(record, precondition=precondition)

    def append_memory_operation(
        self,
        payload: MemoryOperationPayload,
    ) -> MemoryOperationWriteResult:
        return self.inner.append_memory_operation(payload)


class _RunIdBlindSourceStore:
    """A `PromotionDecisionStore` double whose `read_record` IGNORES `run_id`.

    The Protocol permits it - `run_id` is a keyword a store MAY consult, and
    only the concrete `CanonicalMemoryStore` raises for an episodic read without
    one. Against that concrete store the service's episodic-no-`run_id`
    PRE-CHECK is unobservable: the raise lands in `_resolve_source_provenance`'s
    sibling `except ValueError`, which returns `None` identically, so deleting
    the pre-check leaves every concrete-store witness green.

    This double is the shape that tells the two apart. It SERVES the cited
    episodic record, so without the pre-check the service resolves a `false`
    provenance it has no run-scoped right to trust and auto-promotes silently.
    """

    def __init__(self, inner: CanonicalMemoryStore, *, source: MemoryStoreRecord) -> None:
        self.inner = inner
        self._source = source

    def read_record(
        self,
        memory_id: MemoryID,
        kind: MemoryRecordKind,
        *,
        run_id: str | None = None,
        audit_mode: bool = False,
    ) -> MemoryStoreRecord:
        if memory_id == self._source.envelope.memory_id:
            return self._source
        return self.inner.read_record(memory_id, kind, run_id=run_id, audit_mode=audit_mode)

    def write_record(self, record: MemoryStoreRecord) -> object:
        return self.inner.write_record(record)

    def write_record_guarded(
        self,
        record: MemoryStoreRecord,
        *,
        precondition: Callable[[], bool],
    ) -> object:
        return self.inner.write_record_guarded(record, precondition=precondition)

    def append_memory_operation(
        self,
        payload: MemoryOperationPayload,
    ) -> MemoryOperationWriteResult:
        return self.inner.append_memory_operation(payload)


def _episodic_source(provenance: CapturedCrossFamily) -> MemoryStoreRecord:
    """An EPISODIC_TURN source - the kind whose read is run-scoped."""

    content: dict[str, object] = {
        "run_id": _RUN_ID,
        "turn_id": "turn-1",
        "step_id": "step-1",
        "prompt_summary": "the cited episodic source",
        "response_summary": "the cited episodic source",
        "summary_source": "harness_rule",
        "summary_model": None,
        "summary_hash": b"\x21" * 32,
        "tool_event_refs": [],
        "failure_observations": [],
        "promotion_candidates": [],
        "token_usage": None,
    }
    content_hash = compute_memory_content_hash(content)
    return MemoryStoreRecord(
        envelope=MemoryRecordEnvelope(
            memory_id=derive_memory_id(
                MemoryTier.EPISODIC, MemoryRecordKind.EPISODIC_TURN, content_hash
            ),
            schema_version="memory-store-record/v1",
            tier=MemoryTier.EPISODIC,
            kind=MemoryRecordKind.EPISODIC_TURN,
            created_at=_NOW,
            source_refs=(SourceRef(ref_type=SourceRefType.OPERATOR, ref="operator:episodic"),),
            scope=_scope(),
            content_hash=content_hash,
            captured_cross_family=provenance,
        ),
        content=content,
    )


def _mutating_store(
    tmp_path: Path,
    *,
    provenance: CapturedCrossFamily,
    mutate_to: CapturedCrossFamily | None,
    mutate_at: str,
) -> _MutatingSourceStore:
    inner = _store(tmp_path)
    source = _semantic_source(provenance, tag="mutating")
    inner.write_record(source)
    return _MutatingSourceStore(
        inner,
        source=source,
        mutate_to=mutate_to,
        mutate_at=mutate_at,
    )


# ---------------------------------------------------------------------------
# :1066 - the single-snapshot witness
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("call_site", ["approve", "edit_and_approve"])
def test_one_service_call_resolves_the_cited_source_exactly_once(
    tmp_path: Path,
    call_site: str,
) -> None:
    """:1066 - ONE decision-bearing resolution, and gate/mark agreement.

    The cited source is STABLE here, and deliberately so: under the exact
    per-source commit binding (`:1022`, Codex round 2) ANY mutation between the
    snapshot and the write is a conflict, so a mutating arm could no longer
    reach the assertions below. That leaves the COUNTER carrying this witness
    alone, which it does without help - a two-lookup implementation resolves the
    source twice before the write and shows 2 here, whether or not the value
    moved. The mutating arms live in the two commit-binding witnesses below.
    """

    store = _mutating_store(
        tmp_path,
        provenance=CapturedCrossFamily.TRUE,
        mutate_to=None,
        mutate_at="after_first_read",
    )
    service = _service(store)
    candidate = _candidate(source_memory_refs=(store.source_memory_id,))

    if call_site == "approve":
        result = service.approve(
            candidate,
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
            operator_approved=True,
        )
    else:
        result = service.edit_and_approve(
            candidate,
            statement="Operator-edited statement.",
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
            operator_approved=True,
        )

    assert store.decision_resolutions == 1
    assert result.status is SemanticRecordStatus.ACTIVE
    # The gate withheld the AUTOMATIC path (the candidate claimed
    # auto-promotability and only the operator attestation activated it), and
    # the persisted mark says the same thing.
    assert _FLAG.value in _persisted_risk_flags(store.inner, result)


@pytest.mark.parametrize("call_site", ["approve", "edit_and_approve"])
def test_a_source_mutated_before_the_durable_write_does_not_auto_activate(
    tmp_path: Path,
    call_site: str,
) -> None:
    """:1066 - the commit-binding witness.

    The cited source flips `false` -> `true` after the snapshot but before the
    durable write, hooked at the precondition evaluation point INSIDE the write
    path. Failing or retaking-and-gating are both acceptable; a silent
    auto-activation on the stale snapshot is the failure this pins.
    """

    store = _mutating_store(
        tmp_path,
        provenance=CapturedCrossFamily.FALSE,
        mutate_to=CapturedCrossFamily.TRUE,
        mutate_at="at_write",
    )
    service = _service(store)
    candidate = _candidate(source_memory_refs=(store.source_memory_id,))

    with pytest.raises(PromotionProvenanceChangedError):
        if call_site == "approve":
            service.approve(
                candidate,
                timestamp=_NOW,
                injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
            )
        else:
            service.edit_and_approve(
                candidate,
                statement="Operator-edited statement.",
                timestamp=_NOW,
                injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
            )

    assert store.written == []
    assert store.inner.read_memory_operations() == []


def test_a_mutation_that_cannot_change_the_decision_is_still_a_conflict(
    tmp_path: Path,
) -> None:
    """:1022 (Codex round 2 [P2]) - the binding is EXACT, not decision-shaped.

    The plan's obligation is literal and unqualified: "the activation write must
    not commit against a source whose recorded provenance changed after the
    snapshot; on change the invocation fails or retakes the snapshot and
    re-decides." `true` -> `unknown` gates either way and carries the same mark,
    so an earlier reading treated it as a false conflict and committed. That
    narrowed the contract - the plan says "changed", not "changed the decision"
    - and this witness now pins the inverted outcome. Its predecessor,
    `test_a_mutation_that_cannot_change_the_decision_still_commits`, encoded the
    narrowed reading and is superseded by this test, not merely renamed.

    Note the operator attestation: this refuses even an operator-approved
    activation, because the operator attested to the provenance the SNAPSHOT
    showed them, which is no longer what the store records.
    """

    store = _mutating_store(
        tmp_path,
        provenance=CapturedCrossFamily.TRUE,
        mutate_to=CapturedCrossFamily.UNKNOWN,
        mutate_at="at_write",
    )
    service = _service(store)

    with pytest.raises(PromotionProvenanceChangedError):
        service.approve(
            _candidate(source_memory_refs=(store.source_memory_id,)),
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
            operator_approved=True,
        )

    assert store.written == []
    assert store.inner.read_memory_operations() == []


class _RewritingSourceStore:
    """Delegates to a real store, rewriting cited sources at the guarded write.

    The multi-source counterpart of `_MutatingSourceStore`'s `at_write` hook:
    the rewrites land through the REAL store (same content, therefore the same
    hash-inert `memory_id`, therefore the same path), so the precondition's
    re-read observes genuinely re-recorded provenance rather than a double's
    bookkeeping.
    """

    def __init__(
        self,
        inner: CanonicalMemoryStore,
        *,
        rewrites: Sequence[MemoryStoreRecord],
    ) -> None:
        self.inner = inner
        self._rewrites = tuple(rewrites)
        self.written: list[MemoryStoreRecord] = []

    def read_record(
        self,
        memory_id: MemoryID,
        kind: MemoryRecordKind,
        *,
        run_id: str | None = None,
        audit_mode: bool = False,
    ) -> MemoryStoreRecord:
        return self.inner.read_record(memory_id, kind, run_id=run_id, audit_mode=audit_mode)

    def write_record(self, record: MemoryStoreRecord) -> object:
        self.written.append(record)
        return self.inner.write_record(record)

    def write_record_guarded(
        self,
        record: MemoryStoreRecord,
        *,
        precondition: Callable[[], bool],
    ) -> object:
        for rewrite in self._rewrites:
            self.inner.write_record(rewrite)
        self.written.append(record)
        return self.inner.write_record_guarded(record, precondition=precondition)

    def append_memory_operation(
        self,
        payload: MemoryOperationPayload,
    ) -> MemoryOperationWriteResult:
        return self.inner.append_memory_operation(payload)


def test_a_multi_source_change_preserving_the_aggregate_is_a_conflict(
    tmp_path: Path,
) -> None:
    """:1022 (Codex round 2 [P2]) - the case a scalar comparison cannot see.

    Two cited sources SWAP values (`true`/`false` -> `false`/`true`) between the
    snapshot and the write. Every scalar projection is preserved - the worst-
    value aggregate is `true` before and after, the gate is on before and after,
    the persisted mark is identical - yet BOTH sources' recorded provenance
    changed. Only a per-source vector comparison detects it, so this is the
    witness that a re-narrowed implementation cannot pass by widening the
    compared scalar.
    """

    inner = _store(tmp_path)
    first = _stored_source(inner, CapturedCrossFamily.TRUE, tag="first")
    second = _stored_source(inner, CapturedCrossFamily.FALSE, tag="second")
    store = _RewritingSourceStore(
        inner,
        rewrites=(
            _semantic_source(CapturedCrossFamily.FALSE, tag="first"),
            _semantic_source(CapturedCrossFamily.TRUE, tag="second"),
        ),
    )
    service = _service(store)

    with pytest.raises(PromotionProvenanceChangedError):
        service.approve(
            _candidate(source_memory_refs=(first, second)),
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
            operator_approved=True,
        )

    assert inner.read_memory_operations() == []


def test_a_source_that_becomes_unresolvable_is_a_conflict(tmp_path: Path) -> None:
    """:1022 (Codex round 2 [P2]) - unresolvable is DISTINCT from stored unknown.

    The cited source is stored `unknown` and becomes unreadable before the
    write. Its resolved tri-state is `unknown` both times, so a vector that
    collapsed unresolvable into `unknown` would see no change and commit - the
    same compare-a-projection defect, one level down. The snapshot marks
    unresolvable as `None`, so the change is seen.
    """

    inner = _store(tmp_path)
    source = _stored_source(inner, CapturedCrossFamily.UNKNOWN, tag="vanishing")
    store = _IOFailingSourceStore(
        inner,
        failing=source,
        error=PermissionError(13, "Permission denied"),
        fail_after=1,
    )
    service = _service(store)

    with pytest.raises(PromotionProvenanceChangedError):
        service.approve(
            _candidate(source_memory_refs=(source,)),
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
            operator_approved=True,
        )

    assert inner.read_memory_operations() == []


# ---------------------------------------------------------------------------
# :1083 / :1084 / :1085 - the activation boundary itself
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("call_site", ["approve", "edit_and_approve"])
def test_the_copied_illegal_pair_is_refused_at_the_activation_boundary(
    tmp_path: Path,
    call_site: str,
) -> None:
    """:1083 - witness (ii), the copied illegal pair.

    `model_copy(update=...)` bypasses after-validators by design, so this
    constructs a value the slice-3a validator would reject. That is coherent
    only because the unrepresentability claim is scoped to VALIDATING
    constructors; the activation boundary is what closes the copy route.
    """

    store = _store(tmp_path)
    source_record = _semantic_source(CapturedCrossFamily.TRUE, tag="primary")
    store.write_record(source_record)
    source = source_record.envelope.memory_id
    semantic_dir = store.record_path(source_record).parent
    records_before = sorted(path.name for path in semantic_dir.iterdir())
    legal = _candidate(
        source_memory_refs=(source,),
        risk_flags=(_FLAG,),
        review_required=True,
        auto_promote_allowed=False,
    )
    copied = legal.model_copy(update={"auto_promote_allowed": True})
    assert copied.auto_promote_allowed is True
    assert _FLAG in copied.risk_flags
    service = _service(store)

    with pytest.raises(PromotionReviewRequiredError):
        if call_site == "approve":
            service.approve(
                copied,
                timestamp=_NOW,
                injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
            )
        else:
            service.edit_and_approve(
                copied,
                statement="Operator-edited statement.",
                timestamp=_NOW,
                injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
            )

    # Nothing written to EITHER store: no new canonical record file, and no
    # memory-operation ledger row.
    assert sorted(path.name for path in semantic_dir.iterdir()) == records_before
    assert store.read_memory_operations() == []


@pytest.mark.parametrize("provenance", _GATED_ARMS)
def test_a_candidate_that_omits_the_mark_is_still_refused(
    tmp_path: Path,
    provenance: CapturedCrossFamily,
) -> None:
    """:1084 - witness (iii), the OMITTED mark.

    Internally consistent, no flag, `auto_promote_allowed=True`, and its cited
    source carries `true` / `unknown`. Every value-level check passes this
    candidate by construction, so this arm is the only proof the boundary
    RE-DERIVES rather than inspects.
    """

    store = _store(tmp_path)
    source = _stored_source(store, provenance)
    service = _service(store)
    candidate = _candidate(source_memory_refs=(source,))
    assert _FLAG not in candidate.risk_flags
    assert candidate.auto_promote_allowed is True

    with pytest.raises(PromotionReviewRequiredError):
        service.approve(
            candidate,
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        )

    assert store.read_memory_operations() == []


def test_an_all_false_candidate_auto_activates_with_no_operator_approval(
    tmp_path: Path,
) -> None:
    """:1085 - the positive control.

    Without it, the two witnesses above are satisfiable by a boundary that
    refuses everything.
    """

    store = _store(tmp_path)
    source = _stored_source(store, CapturedCrossFamily.FALSE)
    service = _service(store)

    result = service.approve(
        _candidate(source_memory_refs=(source,)),
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
    )

    assert result.status is SemanticRecordStatus.ACTIVE
    assert _FLAG.value not in _persisted_risk_flags(store, result)


# ---------------------------------------------------------------------------
# :1074 - the eligibility-preserved pair (anti-reading-C)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("provenance", _GATED_ARMS)
def test_operator_approved_activation_of_a_cross_family_candidate_reaches_active(
    tmp_path: Path,
    provenance: CapturedCrossFamily,
) -> None:
    """:1074 arm (a) - eligibility is PRESERVED, not removed.

    Arm (a) fails if the unit refuses cross-family activation outright, which
    is the reading the operator explicitly foreclosed.
    """

    store = _store(tmp_path)
    source = _stored_source(store, provenance)
    service = _service(store)

    result = service.approve(
        _candidate(source_memory_refs=(source,)),
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        operator_approved=True,
    )

    assert result.status is SemanticRecordStatus.ACTIVE


@pytest.mark.parametrize("provenance", _GATED_ARMS)
def test_the_identical_call_without_operator_approval_is_refused(
    tmp_path: Path,
    provenance: CapturedCrossFamily,
) -> None:
    """:1074 arm (b) - the IDENTICAL call without the attestation is refused.

    Neither arm alone proves the gate: (a) alone permits a no-op gate, (b) alone
    permits reading C.
    """

    store = _store(tmp_path)
    source = _stored_source(store, provenance)
    service = _service(store)

    with pytest.raises(PromotionReviewRequiredError):
        service.approve(
            _candidate(source_memory_refs=(source,)),
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        )


# ---------------------------------------------------------------------------
# :1086 - worst-value aggregation over multiple cited sources
# ---------------------------------------------------------------------------


def test_mixed_false_and_true_sources_are_gated(tmp_path: Path) -> None:
    """:1086 arm (a) - one `false` plus one `true`."""

    store = _store(tmp_path)
    refs = (
        _stored_source(store, CapturedCrossFamily.FALSE, tag="clean"),
        _stored_source(store, CapturedCrossFamily.TRUE, tag="risky"),
    )
    service = _service(store)

    with pytest.raises(PromotionReviewRequiredError):
        service.approve(
            _candidate(source_memory_refs=refs),
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        )


def test_mixed_false_and_unresolvable_sources_are_gated(tmp_path: Path) -> None:
    """:1086 arm (b) - one `false` plus one unresolvable."""

    store = _store(tmp_path)
    refs = (
        _stored_source(store, CapturedCrossFamily.FALSE, tag="clean"),
        _unwritten_source("never-written"),
    )
    service = _service(store)

    with pytest.raises(PromotionReviewRequiredError):
        service.approve(
            _candidate(source_memory_refs=refs),
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        )


def test_mixed_false_and_unknown_sources_are_gated(tmp_path: Path) -> None:
    """:1086 arm (c) - one `false` plus one `unknown`."""

    store = _store(tmp_path)
    refs = (
        _stored_source(store, CapturedCrossFamily.FALSE, tag="clean"),
        _stored_source(store, CapturedCrossFamily.UNKNOWN, tag="undetermined"),
    )
    service = _service(store)

    with pytest.raises(PromotionReviewRequiredError):
        service.approve(
            _candidate(source_memory_refs=refs),
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        )


def test_two_false_sources_remain_the_positive_control(tmp_path: Path) -> None:
    """:1086 - the fourth cell. Every arm above fails against an implementation
    that gates only when EVERY source is risky; this one fails against an
    implementation that gates unconditionally."""

    store = _store(tmp_path)
    refs = (
        _stored_source(store, CapturedCrossFamily.FALSE, tag="clean-a"),
        _stored_source(store, CapturedCrossFamily.FALSE, tag="clean-b"),
    )
    service = _service(store)

    result = service.approve(
        _candidate(source_memory_refs=refs),
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
    )

    assert result.status is SemanticRecordStatus.ACTIVE


# ---------------------------------------------------------------------------
# :1090 - fail-closed, one witness per branch
# ---------------------------------------------------------------------------


def test_fail_closed_on_empty_source_memory_refs(tmp_path: Path) -> None:
    """:1090 branch 1 - a candidate that cites nothing has shown nothing."""

    store = _store(tmp_path)
    service = _service(store)
    candidate = _candidate(source_memory_refs=())

    with pytest.raises(PromotionReviewRequiredError):
        service.approve(
            candidate,
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        )

    approved = service.approve(
        candidate,
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        operator_approved=True,
    )
    assert approved.status is SemanticRecordStatus.ACTIVE


def test_fail_closed_on_an_unparseable_memory_id(tmp_path: Path) -> None:
    """:1090 branch 2 - a reference whose record KIND cannot be recovered."""

    store = _store(tmp_path)
    service = _service(store)
    candidate = _candidate(source_memory_refs=(MemoryID("not-a-memory-id"),))

    with pytest.raises(PromotionReviewRequiredError):
        service.approve(
            candidate,
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        )

    approved = service.approve(
        candidate,
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        operator_approved=True,
    )
    assert approved.status is SemanticRecordStatus.ACTIVE


def test_fail_closed_on_an_episodic_source_with_no_usable_run_id(tmp_path: Path) -> None:
    """:1090 branch 3 - the `_required_run_id` case.

    The service holds only an OPTIONAL `run_id`, and `MemoryStore` raises for an
    episodic read without one. The service pre-checks the same condition so the
    branch is deterministic rather than store-implementation-dependent.
    """

    store = _store(tmp_path)
    service = _service(store, run_id=None)
    episodic_ref = MemoryID("mem:episodic:episodic_turn:" + "2" * 64)
    candidate = _candidate(source_memory_refs=(episodic_ref,))

    with pytest.raises(PromotionReviewRequiredError):
        service.approve(
            candidate,
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        )

    approved = service.approve(
        candidate,
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        operator_approved=True,
    )
    assert approved.status is SemanticRecordStatus.ACTIVE


def test_the_episodic_no_run_id_pre_check_holds_at_the_protocol_seam(tmp_path: Path) -> None:
    """:1090 branch 3, PINNED where it is actually load-bearing.

    The sibling witness above drives the CONCRETE store, which raises for an
    episodic read without a `run_id` - and `_resolve_source_provenance`'s
    `except ValueError` returns `None` identically, so that witness stays green
    with the pre-check deleted. `PromotionDecisionStore` is a Protocol, though,
    and nothing in it obliges an implementation to raise. Against a store that
    simply SERVES the record, only the pre-check stands between an unscoped read
    and silent auto-promotion.
    """

    source = _episodic_source(CapturedCrossFamily.FALSE)
    store = _RunIdBlindSourceStore(_store(tmp_path), source=source)
    service = _service(store, run_id=None)
    candidate = _candidate(source_memory_refs=(source.envelope.memory_id,))

    with pytest.raises(PromotionReviewRequiredError):
        service.approve(
            candidate,
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        )

    approved = service.approve(
        candidate,
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        operator_approved=True,
    )
    assert approved.status is SemanticRecordStatus.ACTIVE


def test_fail_closed_on_an_unreadable_source_record(tmp_path: Path) -> None:
    """:1090 branch 4 - a well-formed reference to a record that is not there."""

    store = _store(tmp_path)
    service = _service(store)
    candidate = _candidate(source_memory_refs=(_unwritten_source(),))

    with pytest.raises(PromotionReviewRequiredError):
        service.approve(
            candidate,
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        )

    approved = service.approve(
        candidate,
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        operator_approved=True,
    )
    assert approved.status is SemanticRecordStatus.ACTIVE


@pytest.mark.parametrize(
    "error",
    [PermissionError(13, "Permission denied"), OSError(5, "Input/output error")],
    ids=["permission-denied", "eio"],
)
def test_fail_closed_on_a_source_read_that_raises_an_io_error(
    tmp_path: Path,
    error: OSError,
) -> None:
    """:1090 branch 5 (Codex round-1 [P2]) - an UNREADABLE source.

    The four pre-existing branches all concern what the reference SAYS; this one
    concerns the filesystem refusing to answer. It is the branch that breaks the
    fail-closed reading asymmetrically if it escapes: every decision operation
    takes the snapshot first, so an I/O error propagating out of it aborts
    `propose_for_review` and `deny` - neither of which authorizes anything - and
    aborts an operator-approved `approve` too, which the plan requires to stay
    OPEN. All four outcomes are asserted per-branch below; a catch-all
    `assert not raised` would pass on an implementation that only fixed one.
    """

    inner = _store(tmp_path)
    unreadable = _stored_source(inner, CapturedCrossFamily.FALSE, tag="unreadable")
    store = _IOFailingSourceStore(inner, failing=unreadable, error=error)
    service = _service(store)
    candidate = _candidate(source_memory_refs=(unreadable,))

    # Gated: the unreadable source resolves `unknown`, so the AUTOMATIC path is
    # withheld - not crashed.
    with pytest.raises(PromotionReviewRequiredError):
        service.approve(
            candidate,
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        )

    proposed = service.propose_for_review(
        candidate,
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
    )
    assert proposed.status is SemanticRecordStatus.PROPOSED
    assert _FLAG.value in _persisted_risk_flags(inner, proposed)

    denied = service.deny(candidate, timestamp=_NOW, reason="unreadable provenance")
    assert denied.status is SemanticRecordStatus.DENIED

    approved = service.approve(
        candidate,
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        operator_approved=True,
    )
    assert approved.status is SemanticRecordStatus.ACTIVE
    assert _FLAG.value in _persisted_risk_flags(inner, approved)


@pytest.mark.parametrize(
    "error",
    [
        TypeError("expected SHA-256 digest hex string"),
        TypeError("stored envelope field has the wrong JSON type"),
    ],
    ids=["null-content-hash", "wrong-json-type"],
)
def test_fail_closed_on_a_source_read_that_raises_a_type_error(
    tmp_path: Path,
    error: TypeError,
) -> None:
    """:1090 branch 6 (Codex round-2 [P2]) - a MALFORMED stored source.

    Sibling of branch 5, and the same failure class: a stored payload that fails
    deserialization on a TYPE rather than a value - a serialized `content_hash`
    of `null` reaching `_bytes32_from_json`, an envelope field of the wrong JSON
    type - raises `TypeError`, which is neither a `LookupError`, a `ValueError`,
    nor an `OSError`. Escaping the handler, it aborts proposals, denials, and
    operator-approved promotions alike. All four outcomes asserted separately,
    per-branch.
    """

    inner = _store(tmp_path)
    malformed = _stored_source(inner, CapturedCrossFamily.FALSE, tag="malformed")
    store = _IOFailingSourceStore(inner, failing=malformed, error=error)
    service = _service(store)
    candidate = _candidate(source_memory_refs=(malformed,))

    with pytest.raises(PromotionReviewRequiredError):
        service.approve(
            candidate,
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        )

    proposed = service.propose_for_review(
        candidate,
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
    )
    assert proposed.status is SemanticRecordStatus.PROPOSED
    assert _FLAG.value in _persisted_risk_flags(inner, proposed)

    denied = service.deny(candidate, timestamp=_NOW, reason="malformed provenance")
    assert denied.status is SemanticRecordStatus.DENIED

    approved = service.approve(
        candidate,
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
        operator_approved=True,
    )
    assert approved.status is SemanticRecordStatus.ACTIVE
    assert _FLAG.value in _persisted_risk_flags(inner, approved)


# ---------------------------------------------------------------------------
# :1087 / :1088 / :1089 - the choke-point normalization, all four call sites
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("provenance", _GATED_ARMS)
def test_proposed_record_carries_a_mark_the_candidate_omitted(
    tmp_path: Path,
    provenance: CapturedCrossFamily,
) -> None:
    """:1087 - the omitted direction, at the `PROPOSED` call site."""

    store = _store(tmp_path)
    source = _stored_source(store, provenance)
    service = _service(store)

    result = service.propose_for_review(
        _candidate(source_memory_refs=(source,)),
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
    )

    assert result.status is SemanticRecordStatus.PROPOSED
    assert _FLAG.value in _persisted_risk_flags(store, result)


def test_proposed_record_carries_the_mark_on_an_unresolvable_source(tmp_path: Path) -> None:
    """:1087 - an unresolvable branch carries the mark too.

    Matching the read-side `unknown` mapping: "this needs review and here is
    why" is the honest durable statement.
    """

    store = _store(tmp_path)
    service = _service(store)

    result = service.propose_for_review(
        _candidate(source_memory_refs=(_unwritten_source(),)),
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
    )

    assert _FLAG.value in _persisted_risk_flags(store, result)


def test_proposed_record_omits_a_mark_the_candidate_spoofed(tmp_path: Path) -> None:
    """:1087 - the spoofed direction, at the `PROPOSED` call site.

    The candidate carries the LEGAL flagged shape (review-required, not
    auto-promotable), so the validator admits it; the source nonetheless
    resolves `false`, and the durable record states the re-derived fact.
    """

    store = _store(tmp_path)
    source = _stored_source(store, CapturedCrossFamily.FALSE)
    service = _service(store)

    result = service.propose_for_review(
        _candidate(
            source_memory_refs=(source,),
            risk_flags=(_FLAG,),
            review_required=True,
            auto_promote_allowed=False,
        ),
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
    )

    assert _FLAG.value not in _persisted_risk_flags(store, result)


@pytest.mark.parametrize("call_site", ["approve", "edit_and_approve"])
def test_active_record_omits_a_mark_the_candidate_spoofed(
    tmp_path: Path,
    call_site: str,
) -> None:
    """:1088 arm (a) - the spoof arm, at BOTH `ACTIVE` call sites.

    A false provenance must not become durable on the pipeline's longest-lived
    artifact.
    """

    store = _store(tmp_path)
    source = _stored_source(store, CapturedCrossFamily.FALSE)
    service = _service(store)
    candidate = _candidate(
        source_memory_refs=(source,),
        risk_flags=(_FLAG,),
        review_required=True,
        auto_promote_allowed=False,
    )

    if call_site == "approve":
        result = service.approve(
            candidate,
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
            operator_approved=True,
        )
    else:
        result = service.edit_and_approve(
            candidate,
            statement="Operator-edited statement.",
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
            operator_approved=True,
        )

    assert result.status is SemanticRecordStatus.ACTIVE
    assert _FLAG.value not in _persisted_risk_flags(store, result)


@pytest.mark.parametrize("call_site", ["approve", "edit_and_approve"])
def test_active_record_carries_a_mark_the_candidate_omitted(
    tmp_path: Path,
    call_site: str,
) -> None:
    """:1088 arm (b) - the omitted arm, at BOTH `ACTIVE` call sites.

    Doing double duty: it proves the normalization reaches the activation write,
    and it documents that an operator-approved cross-family record stays
    AUDITABLE as cross-family downstream. Approval records a decision to accept
    the provenance, not a decision to forget it.
    """

    store = _store(tmp_path)
    source = _stored_source(store, CapturedCrossFamily.TRUE)
    service = _service(store)
    candidate = _candidate(source_memory_refs=(source,))

    if call_site == "approve":
        result = service.approve(
            candidate,
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
            operator_approved=True,
        )
    else:
        result = service.edit_and_approve(
            candidate,
            statement="Operator-edited statement.",
            timestamp=_NOW,
            injection_policy=SemanticInjectionPolicy.RETRIEVAL_ONLY,
            operator_approved=True,
        )

    assert result.status is SemanticRecordStatus.ACTIVE
    assert _FLAG.value in _persisted_risk_flags(store, result)


def test_denied_record_omits_a_mark_the_candidate_spoofed(tmp_path: Path) -> None:
    """:1089 - the call site an enumeration reached for casually would miss.

    One arm suffices: the point is that the choke-point normalization covers
    `deny` too, which a per-method fix would not have.
    """

    store = _store(tmp_path)
    source = _stored_source(store, CapturedCrossFamily.FALSE)
    service = _service(store)

    result = service.deny(
        _candidate(
            source_memory_refs=(source,),
            risk_flags=(_FLAG,),
            review_required=True,
            auto_promote_allowed=False,
        ),
        timestamp=_NOW,
        reason="not durable enough",
    )

    assert result.status is SemanticRecordStatus.DENIED
    assert _FLAG.value not in _persisted_risk_flags(store, result)
