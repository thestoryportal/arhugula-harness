"""U-MEM-26 read-boundary witnesses - C-MEM-03 null asymmetry, `B-90` tenant.

Covers the read half of U-MEM-26: the asymmetric-`null` pair, the per-layer
null-request denial, the `B-90` layer-independent tenant denial (three separate
predicate assertions - a single composite retrieval witness passes OVER
whichever layer still leaks, which is exactly how `B-90` survived), and the
request-boundary `provider_family` value domain.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from harness_core import DeploymentSurface
from harness_is.memory_path_registry import MemoryRootBinding
from harness_is.memory_policy import (
    AccessDecision,
    MemoryPolicyDocument,
    MemoryPolicyResolver,
    ReviewMode,
)
from harness_is.memory_policy import _scope_not_broader as policy_scope_not_broader
from harness_is.memory_record_envelope import (
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
from harness_is.memory_retrieval import (
    MemoryPacketAccessMode,
    MemoryRetrievalRequest,
    MemoryRetrievalResult,
    MemoryRetriever,
    RetrievalExclusionReason,
)
from harness_is.memory_retrieval import _scope_mismatch as retriever_scope_mismatch
from harness_is.memory_retrieval_index import (
    DerivedRetrievalIndexQuery,
    DerivedRetrievalIndexStore,
)
from harness_is.memory_retrieval_index import _scope_matches as index_scope_matches
from harness_is.memory_scope_value_domain import ScopeFamilyCanonicalizer
from harness_is.memory_store import CanonicalMemoryStore, MemoryStoreRecord
from harness_is.state_ledger_entry_schema import Actor, ActorClass

_NOW = datetime(2026, 7, 28, 9, 0, 0, tzinfo=UTC)

_REGISTERED_FAMILIES = frozenset({"anthropic", "openai", "google", "local_open_weight"})
_FAMILY_BY_PROVIDER_KEY = {
    "claude_code": "anthropic",
    "codex": "openai",
    "gemini": "google",
    "ollama": "local_open_weight",
}


def _fake_canonicalizer(provider_family: str) -> str | None:
    """Stand-in for `lifecycle/cross_family_cost_tag.provider_family_for_scope_check`.

    `harness-is` has zero outbound cross-axis edges, so the real authority is
    injected rather than imported; this fake reproduces its registered /
    unregistered split (a family value resolves to itself, a registered provider
    key resolves to its family, anything else is out of domain).
    """
    if provider_family in _REGISTERED_FAMILIES:
        return provider_family
    return _FAMILY_BY_PROVIDER_KEY.get(provider_family)


def _scope(
    *,
    provider_family: str | None = None,
    tenant: str | None = None,
) -> MemoryScope:
    return MemoryScope(
        project="arhugula-v2",
        workflow="memory-substrate",
        provider_family=provider_family,
        cli_profile="codex",
        tenant=tenant,
        visibility=MemoryVisibility.WORKFLOW,
    )


def _binding(tmp_path: Path) -> MemoryRootBinding:
    return MemoryRootBinding(default_root=tmp_path / "memory")


def _store(binding: MemoryRootBinding) -> CanonicalMemoryStore:
    return CanonicalMemoryStore(
        root_binding=binding,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )


def _index_store(
    binding: MemoryRootBinding,
    *,
    canonicalizer: ScopeFamilyCanonicalizer | None = None,
) -> DerivedRetrievalIndexStore:
    return DerivedRetrievalIndexStore(
        root_binding=binding,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        family_canonicalizer=canonicalizer,
    )


def _record(*, statement: str, scope: MemoryScope) -> MemoryStoreRecord:
    content: dict[str, object] = {
        "semantic_kind": MemoryRecordKind.SEMANTIC_FACT.value,
        "statement": statement,
        "confidence": "high",
        "source_authority": "operator_direct",
        "status": "active",
        "injection_policy": "retrieval_only",
        "tags": [],
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
            source_refs=(SourceRef(ref_type=SourceRefType.OPERATOR, ref="operator:u-mem-26"),),
            scope=scope,
            content_hash=content_hash,
        ),
        content=content,
    )


def _enabled_policy() -> MemoryPolicyDocument:
    return MemoryPolicyDocument(
        policy_id="policy:u-mem-26-test",
        enabled=True,
        retrieval_access=AccessDecision.RETRIEVAL_ONLY,
        injection_access=AccessDecision.PROMPT_PACKET,
        review_mode=ReviewMode.AUTOMATIC,
    )


def _request(*, scope: MemoryScope) -> MemoryRetrievalRequest:
    return MemoryRetrievalRequest(
        run_id="run-u-mem-26",
        workflow_id="memory-substrate",
        cli_profile="codex",
        provider="openai",
        model="gpt-5",
        query_summary="",
        scope=scope,
        token_budget=500,
    )


def _retrieved_refs(
    tmp_path: Path,
    *,
    records: tuple[MemoryStoreRecord, ...],
    request_scope: MemoryScope,
    canonicalizer_injected: bool = False,
) -> tuple[str, ...]:
    """Run a full `MemoryRetriever.retrieve` and return the selected refs."""
    result = _retrieval_result(
        tmp_path,
        records=records,
        request_scope=request_scope,
        canonicalizer_injected=canonicalizer_injected,
    )
    return tuple(str(ref) for ref in result.selected_refs)


def _retrieval_result(
    tmp_path: Path,
    *,
    records: tuple[MemoryStoreRecord, ...],
    request_scope: MemoryScope,
    canonicalizer_injected: bool = False,
) -> MemoryRetrievalResult:
    """Run a full `MemoryRetriever.retrieve` and return the whole result."""
    binding = _binding(tmp_path)
    store = _store(binding)
    for record in records:
        store.write_record(record)
    index_store = _index_store(binding)
    index_store.rebuild(indexed_at=_NOW)
    retriever = MemoryRetriever(
        store=store,
        index_store=index_store,
        policy_resolver=MemoryPolicyResolver(_enabled_policy()),
        policy_ref="policy:u-mem-26-test",
        family_canonicalizer=_fake_canonicalizer if canonicalizer_injected else None,
    )
    return retriever.retrieve(
        _request(scope=request_scope),
        timestamp=_NOW,
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="codex"),
        access_mode=MemoryPacketAccessMode.PROMPT_EXTENSION_PACKET,
    )


# --- Witness 1: the asymmetric-`null` pair (plan acceptance :910) ------------


def test_null_family_record_is_reachable_by_a_family_scoped_request(tmp_path: Path) -> None:
    """A stored `null` is the unpartitioned wildcard - C-MEM-03."""
    record = _record(statement="Unpartitioned memory fact.", scope=_scope())

    selected = _retrieved_refs(
        tmp_path,
        records=(record,),
        request_scope=_scope(provider_family="anthropic"),
    )

    assert selected == (str(record.envelope.memory_id),)


def test_family_scoped_record_is_not_reachable_by_a_null_family_request(tmp_path: Path) -> None:
    """The wildcard is stored-side only: a `null` REQUEST does not widen."""
    record = _record(
        statement="Anthropic-partitioned memory fact.",
        scope=_scope(provider_family="anthropic"),
    )

    selected = _retrieved_refs(
        tmp_path,
        records=(record,),
        request_scope=_scope(),
    )

    assert selected == ()


# --- Witness 2: per-layer null-request denial (plan acceptance :919/:920) ----


def test_retriever_predicate_denies_a_null_family_request() -> None:
    """Witness (i), retriever: asserted against `_scope_mismatch` directly."""
    assert retriever_scope_mismatch(_scope(provider_family="anthropic"), _scope()) is True
    assert retriever_scope_mismatch(_scope(), _scope(provider_family="anthropic")) is False


def test_index_predicate_denies_a_null_family_request() -> None:
    """Witness (ii), derived index: asserted against `_scope_matches` directly."""
    assert index_scope_matches(_scope(provider_family="anthropic"), _scope()) is False
    assert index_scope_matches(_scope(), _scope(provider_family="anthropic")) is True


def test_index_retrieve_denies_a_null_family_request_end_to_end(tmp_path: Path) -> None:
    """Witness (ii) end-to-end: the public `retrieve` carries neither ref nor entry.

    `DerivedRetrievalIndexStore.retrieve` has no policy leg, so before U-MEM-26
    this public path returned family-scoped metadata and refs to a `null`
    request - and did so after `_order_candidates`, breaking the before-ranking
    scope-boundary requirement.
    """
    binding = _binding(tmp_path)
    store = _store(binding)
    record = _record(
        statement="Anthropic-partitioned memory fact.",
        scope=_scope(provider_family="anthropic"),
    )
    store.write_record(record)
    index_store = _index_store(binding)
    index_store.rebuild(indexed_at=_NOW)

    result = index_store.retrieve(DerivedRetrievalIndexQuery(scope=_scope()))

    assert result.selected_refs == ()
    assert result.entries == ()
    assert result.considered_count == 1


def test_index_retrieve_denies_an_absent_scope_query_against_a_partitioned_record(
    tmp_path: Path,
) -> None:
    """An absent query scope is not a total wildcard for the partition fields."""
    binding = _binding(tmp_path)
    store = _store(binding)
    partitioned = _record(
        statement="Anthropic-partitioned memory fact.",
        scope=_scope(provider_family="anthropic"),
    )
    unpartitioned = _record(statement="Unpartitioned memory fact.", scope=_scope())
    store.write_record(partitioned)
    store.write_record(unpartitioned)
    index_store = _index_store(binding)
    index_store.rebuild(indexed_at=_NOW)

    result = index_store.retrieve(DerivedRetrievalIndexQuery())

    assert result.selected_refs == (unpartitioned.envelope.memory_id,)


# --- Witness 3: `B-90` layer-independent tenant denial (:921/:922/:923) ------


def test_b90_tenant_denial_at_the_retriever_predicate() -> None:
    """`B-90` witness (i) - `MemoryRetriever._scope_mismatch`, in isolation."""
    assert retriever_scope_mismatch(_scope(tenant="tenant-b"), _scope(tenant="tenant-a")) is True


def test_b90_tenant_denial_at_the_index_predicate() -> None:
    """`B-90` witness (ii) - `_scope_matches`, in isolation."""
    assert index_scope_matches(_scope(tenant="tenant-b"), _scope(tenant="tenant-a")) is False


def test_b90_tenant_denial_at_the_policy_predicate() -> None:
    """`B-90` witness (iii) - `_scope_not_broader`, in isolation."""
    assert (
        policy_scope_not_broader(
            record_scope=_scope(tenant="tenant-b"),
            requested_scope=_scope(tenant="tenant-a"),
        )
        is False
    )


def test_b90_null_tenant_request_is_denied_at_every_predicate() -> None:
    """The `B-90` half that made every tool-captured record tenant-unpartitioned.

    A request naming no tenant must not reach a tenant-partitioned record at any
    of the three layers.
    """
    record_scope = _scope(tenant="tenant-b")
    request_scope = _scope()

    assert retriever_scope_mismatch(record_scope, request_scope) is True
    assert index_scope_matches(record_scope, request_scope) is False
    assert (
        policy_scope_not_broader(record_scope=record_scope, requested_scope=request_scope) is False
    )


def test_retriever_retrieve_denies_a_tenant_partitioned_record_end_to_end(
    tmp_path: Path,
) -> None:
    """`B-90` through `MemoryRetriever.retrieve`, not the predicate in isolation.

    The retriever's own tenant coverage was predicate-level only: a mutation
    stopping `_static_exclusion_reason` from consulting `_scope_mismatch` left
    every isolation witness green, because the policy leg one step later denies
    the same record on its own hand-listed fields - the record disappears from
    `selected_refs` either way. The EXCLUSION REASON is what discriminates the
    two layers, so it is asserted rather than the selection alone.

    The `null`-tenant request is the arm that pins NEW behaviour: before
    U-MEM-26 the retriever compared `tenant` with either-side-`null`-skips
    semantics, so the mismatched-tenant arm alone would pass against the old
    predicate too. The unpartitioned sibling is the liveness control - it proves
    the query genuinely reaches records, so an empty result cannot pass this
    test for the wrong reason.
    """
    partitioned = _record(
        statement="Tenant-A-partitioned memory fact.",
        scope=_scope(tenant="tenant-a"),
    )
    unpartitioned = _record(statement="Unpartitioned memory fact.", scope=_scope())
    records = (partitioned, unpartitioned)

    mismatched = _retrieval_result(
        tmp_path / "mismatched-tenant",
        records=records,
        request_scope=_scope(tenant="tenant-b"),
    )
    null_tenant = _retrieval_result(
        tmp_path / "null-tenant",
        records=records,
        request_scope=_scope(),
    )

    for result in (mismatched, null_tenant):
        assert tuple(str(ref) for ref in result.selected_refs) == (
            str(unpartitioned.envelope.memory_id),
        )
        assert {ref.memory_ref: ref.reason for ref in result.excluded_refs} == {
            partitioned.envelope.memory_id: RetrievalExclusionReason.SCOPE_MISMATCH
        }


def test_index_retrieve_denies_a_tenant_partitioned_record_end_to_end(tmp_path: Path) -> None:
    """`B-90` through the PUBLIC path, not the predicate in isolation.

    The three witnesses above assert `tenant` at each predicate; none of them
    runs a real store-write / index-rebuild / retrieve. That is the shape that
    let `B-90` survive at `provider_family` — a predicate can be correct while
    the production path never consults it for this field (an unindexed `tenant`,
    a partition list the rebuild does not carry). The unpartitioned sibling is
    the liveness control: it proves the query is genuinely reaching records, so
    an empty result cannot pass this test for the wrong reason.
    """
    binding = _binding(tmp_path)
    store = _store(binding)
    partitioned = _record(
        statement="Tenant-A-partitioned memory fact.",
        scope=_scope(tenant="tenant-a"),
    )
    unpartitioned = _record(statement="Unpartitioned memory fact.", scope=_scope())
    store.write_record(partitioned)
    store.write_record(unpartitioned)
    index_store = _index_store(binding)
    index_store.rebuild(indexed_at=_NOW)

    mismatched = index_store.retrieve(DerivedRetrievalIndexQuery(scope=_scope(tenant="tenant-b")))
    null_tenant = index_store.retrieve(DerivedRetrievalIndexQuery(scope=_scope()))
    absent_scope = index_store.retrieve(DerivedRetrievalIndexQuery())

    # A different tenant, an explicit `null` tenant, and no scope object at all
    # are three distinct request shapes; none of them may reach tenant-A's
    # record, and each still reaches the stored-`null` wildcard.
    for result in (mismatched, null_tenant, absent_scope):
        assert result.considered_count == 2
        assert result.selected_refs == (unpartitioned.envelope.memory_id,)


def test_policy_resolve_retrieval_denies_a_tenant_mismatched_record() -> None:
    """`B-90` witness (iii) one layer UP — the resolver's own public method.

    `memory_policy._scope_not_broader` hand-lists its comparison fields instead
    of consuming `SCOPE_PARTITION_FIELDS`, so this third path is un-bounded by
    the shared value domain: striking `tenant` from that list leaves the other
    two layers green. `resolve_retrieval` is the method every policy-gated
    consumer actually calls, and the matched-tenant control below keeps the
    denial from being an artifact of some unrelated gate in `_resolve_access`.
    """
    resolver = MemoryPolicyResolver(_enabled_policy())

    denied = resolver.resolve_retrieval(
        record_kind=MemoryRecordKind.SEMANTIC_FACT,
        record_scope=_scope(tenant="tenant-a"),
        requested_scope=_scope(tenant="tenant-b"),
    )
    allowed = resolver.resolve_retrieval(
        record_kind=MemoryRecordKind.SEMANTIC_FACT,
        record_scope=_scope(tenant="tenant-a"),
        requested_scope=_scope(tenant="tenant-a"),
    )

    assert denied.access_decision is AccessDecision.DENY
    assert allowed.access_decision is AccessDecision.RETRIEVAL_ONLY


# --- Witness 4: request-boundary value domain (plan acceptance :916) ---------


def test_registered_provider_key_request_is_canonicalized_at_the_retriever(
    tmp_path: Path,
) -> None:
    """A registered raw key reaches records stored under its family value."""
    record = _record(
        statement="Anthropic-partitioned memory fact.",
        scope=_scope(provider_family="anthropic"),
    )

    selected = _retrieved_refs(
        tmp_path,
        records=(record,),
        request_scope=_scope(provider_family="claude_code"),
        canonicalizer_injected=True,
    )

    assert selected == (str(record.envelope.memory_id),)


def test_out_of_domain_request_family_rejects_the_request_at_the_retriever(
    tmp_path: Path,
) -> None:
    """Codex R3 [P2-a] - out-of-domain REJECTS the request, it does not narrow it.

    C-MEM-03 v1.1 gives exactly two dispositions, and the executor
    (`StandardMemoryToolExecutor._resolved_scope`) denies such a call outright.
    Excluding only the partition-scoped records - serving the unpartitioned
    remainder - was a third posture: a rejected request answered anyway, just
    with less. The unpartitioned record here is the discriminator; without it
    this test would pass under the old behaviour.
    """
    partitioned = _record(
        statement="Anthropic-partitioned memory fact.",
        scope=_scope(provider_family="anthropic"),
    )
    unpartitioned = _record(statement="Unpartitioned memory fact.", scope=_scope())

    result = _retrieval_result(
        tmp_path,
        records=(partitioned, unpartitioned),
        request_scope=_scope(provider_family="not-a-provider"),
        canonicalizer_injected=True,
    )

    assert result.selected_refs == ()
    excluded = {ref.memory_ref: ref.reason for ref in result.excluded_refs}
    assert excluded == {
        partitioned.envelope.memory_id: RetrievalExclusionReason.SCOPE_MISMATCH,
        unpartitioned.envelope.memory_id: RetrievalExclusionReason.SCOPE_MISMATCH,
    }


def test_null_request_family_still_reaches_unpartitioned_records(tmp_path: Path) -> None:
    """The paired positive: a `null` REQUEST is not an out-of-domain request.

    Naming no partition is the legitimate unscoped ask; failing to resolve a
    named identifier is not. The rejection above must not collapse the two.
    """
    unpartitioned = _record(statement="Unpartitioned memory fact.", scope=_scope())

    selected = _retrieved_refs(
        tmp_path,
        records=(unpartitioned,),
        request_scope=_scope(),
        canonicalizer_injected=True,
    )

    assert selected == (str(unpartitioned.envelope.memory_id),)


def test_legacy_raw_key_record_stays_unreachable_by_a_crafted_raw_key_request(
    tmp_path: Path,
) -> None:
    """The crafted-bypass negative at the retriever.

    A pre-v1.1 record persisted with the raw provider key `claude_code` must
    stay unreachable, including from a request crafted with that same raw key -
    the request is canonicalized to `anthropic` before the predicate sees it, so
    the raw-key record no longer matches. This is the forward-only residual the
    C-MEM-03 permanent-residual claim rests on.
    """
    legacy = _record(
        statement="Legacy raw-key memory fact.",
        scope=_scope(provider_family="claude_code"),
    )

    selected = _retrieved_refs(
        tmp_path,
        records=(legacy,),
        request_scope=_scope(provider_family="claude_code"),
        canonicalizer_injected=True,
    )

    assert selected == ()


def test_legacy_raw_key_record_stays_unreachable_at_the_derived_index(
    tmp_path: Path,
) -> None:
    """The same crafted-bypass negative at the second read layer."""
    binding = _binding(tmp_path)
    store = _store(binding)
    legacy = _record(
        statement="Legacy raw-key memory fact.",
        scope=_scope(provider_family="claude_code"),
    )
    store.write_record(legacy)
    index_store = _index_store(binding, canonicalizer=_fake_canonicalizer)
    index_store.rebuild(indexed_at=_NOW)

    result = index_store.retrieve(
        DerivedRetrievalIndexQuery(scope=_scope(provider_family="claude_code"))
    )

    assert result.selected_refs == ()
    assert result.entries == ()


def test_registered_provider_key_query_is_canonicalized_at_the_derived_index(
    tmp_path: Path,
) -> None:
    """The canonicalize half at the index layer, mirroring the retriever."""
    binding = _binding(tmp_path)
    store = _store(binding)
    record = _record(
        statement="Anthropic-partitioned memory fact.",
        scope=_scope(provider_family="anthropic"),
    )
    store.write_record(record)
    index_store = _index_store(binding, canonicalizer=_fake_canonicalizer)
    index_store.rebuild(indexed_at=_NOW)

    result = index_store.retrieve(
        DerivedRetrievalIndexQuery(scope=_scope(provider_family="claude_code"))
    )

    assert result.selected_refs == (record.envelope.memory_id,)


def test_out_of_domain_query_family_rejects_the_query_at_the_derived_index(
    tmp_path: Path,
) -> None:
    """Codex R3 [P2-a] - the same rejection at the index layer, end to end.

    Empty means empty at this layer: no entries AND no refs. The unpartitioned
    record is again the discriminator - it was served under the old
    partition-only filter.
    """
    binding = _binding(tmp_path)
    store = _store(binding)
    partitioned = _record(
        statement="Anthropic-partitioned memory fact.",
        scope=_scope(provider_family="anthropic"),
    )
    unpartitioned = _record(statement="Unpartitioned memory fact.", scope=_scope())
    store.write_record(partitioned)
    store.write_record(unpartitioned)
    index_store = _index_store(binding, canonicalizer=_fake_canonicalizer)
    index_store.rebuild(indexed_at=_NOW)

    result = index_store.retrieve(
        DerivedRetrievalIndexQuery(scope=_scope(provider_family="not-a-provider"))
    )

    assert result.selected_refs == ()
    assert result.entries == ()
    assert result.considered_count == 2  # the records exist; the QUERY was rejected


def test_unregistered_raw_key_record_stays_unreachable_by_its_own_raw_key_request(
    tmp_path: Path,
) -> None:
    """The crafted-bypass negative for an UNREGISTERED legacy identifier.

    Canonicalization alone cannot close this one: the identifier resolves to no
    family, so a raw-string comparison would find record and request EQUAL and
    admit the legacy record. Only the out-of-domain denial keeps it unreachable.
    """
    legacy = _record(
        statement="Legacy unregistered-key memory fact.",
        scope=_scope(provider_family="mystery-provider"),
    )

    selected = _retrieved_refs(
        tmp_path,
        records=(legacy,),
        request_scope=_scope(provider_family="mystery-provider"),
        canonicalizer_injected=True,
    )

    assert selected == ()


def test_unregistered_raw_key_record_stays_unreachable_at_the_derived_index(
    tmp_path: Path,
) -> None:
    """The same unregistered crafted-bypass negative at the second read layer."""
    binding = _binding(tmp_path)
    store = _store(binding)
    legacy = _record(
        statement="Legacy unregistered-key memory fact.",
        scope=_scope(provider_family="mystery-provider"),
    )
    store.write_record(legacy)
    index_store = _index_store(binding, canonicalizer=_fake_canonicalizer)
    index_store.rebuild(indexed_at=_NOW)

    result = index_store.retrieve(
        DerivedRetrievalIndexQuery(scope=_scope(provider_family="mystery-provider"))
    )

    assert result.selected_refs == ()
    assert result.entries == ()


def test_absent_canonicalizer_preserves_raw_string_comparison(tmp_path: Path) -> None:
    """The documented un-wired default.

    Without an injected authority the value domain is NOT enforced - a raw-key
    request still reaches a raw-key record. This asymmetry against the two tests
    above is the reason production composition MUST inject the canonicalizer;
    the witness pins it so the gap is visible rather than silent.
    """
    legacy = _record(
        statement="Legacy raw-key memory fact.",
        scope=_scope(provider_family="claude_code"),
    )

    selected = _retrieved_refs(
        tmp_path,
        records=(legacy,),
        request_scope=_scope(provider_family="claude_code"),
    )

    assert selected == (str(legacy.envelope.memory_id),)
