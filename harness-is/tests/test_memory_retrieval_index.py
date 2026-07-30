"""Tests for U-MEM-10 - derived retrieval indexes."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal, cast

import pytest
from harness_core import DeploymentSurface
from harness_is.memory_path_registry import MemoryRootBinding
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
from harness_is.memory_retrieval_index import (
    CURRENT_DERIVED_RETRIEVAL_INDEX_VERSION,
    DerivedRetrievalIndexEntry,
    DerivedRetrievalIndexMissingError,
    DerivedRetrievalIndexQuery,
    DerivedRetrievalIndexStaleError,
    DerivedRetrievalIndexStore,
)
from harness_is.memory_store import CanonicalMemoryStore, MemoryStoreRecord
from pydantic import BaseModel, ConfigDict

_NOW = datetime(2026, 7, 2, 12, 0, 0, tzinfo=UTC)


def _binding(tmp_path: Path) -> MemoryRootBinding:
    return MemoryRootBinding(default_root=tmp_path / "memory")


def _store(binding: MemoryRootBinding) -> CanonicalMemoryStore:
    return CanonicalMemoryStore(
        root_binding=binding,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )


def _index_store(binding: MemoryRootBinding) -> DerivedRetrievalIndexStore:
    return DerivedRetrievalIndexStore(
        root_binding=binding,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )


def _scope(
    *,
    workflow: str = "memory-substrate",
    cli_profile: str = "codex",
) -> MemoryScope:
    return MemoryScope(
        project="arhugula-v2",
        workflow=workflow,
        cli_profile=cli_profile,
        visibility=MemoryVisibility.WORKFLOW,
    )


def _record(
    *,
    kind: MemoryRecordKind = MemoryRecordKind.SEMANTIC_FACT,
    statement: str,
    tags: tuple[str, ...] = (),
    created_at: datetime = _NOW,
    status: str = "active",
    scope: MemoryScope | None = None,
) -> MemoryStoreRecord:
    tier = (
        MemoryTier.PROCEDURAL
        if kind is MemoryRecordKind.PROCEDURAL_SNAPSHOT
        else MemoryTier.SEMANTIC
    )
    if kind is MemoryRecordKind.PROCEDURAL_SNAPSHOT:
        content = {
            "snapshot_id": statement.lower().replace(" ", "-"),
            "workflow_id": "memory-substrate",
            "cli_profile": "codex",
            "status": status,
            "procedural_update": statement,
            "tags": list(tags),
        }
    else:
        content = {
            "semantic_kind": kind.value,
            "statement": statement,
            "confidence": "high",
            "status": status,
            "injection_policy": "retrieval_only",
            "tags": list(tags),
        }
    content_hash = compute_memory_content_hash(content)
    return MemoryStoreRecord(
        envelope=MemoryRecordEnvelope(
            memory_id=derive_memory_id(tier, kind, content_hash),
            schema_version="memory-store-record/v1",
            tier=tier,
            kind=kind,
            created_at=created_at,
            source_refs=(SourceRef(ref_type=SourceRefType.OPERATOR, ref="operator:u-mem-10"),),
            scope=scope or _scope(),
            content_hash=content_hash,
        ),
        content=content,
    )


def test_rebuild_writes_current_index_with_version_and_hash(tmp_path: Path) -> None:
    binding = _binding(tmp_path)
    store = _store(binding)
    fact = _record(statement="Use the indexed memory path for retrieval.", tags=("retrieval",))
    procedure = _record(
        kind=MemoryRecordKind.PROCEDURAL_SNAPSHOT,
        statement="Run the memory loop from a linked worktree.",
        tags=("workflow",),
        created_at=_NOW + timedelta(seconds=1),
    )
    store.write_record(fact)
    store.write_record(procedure)

    rebuilt = _index_store(binding).rebuild(indexed_at=_NOW)
    reread = _index_store(binding).read_current()

    assert rebuilt.index_version == CURRENT_DERIVED_RETRIEVAL_INDEX_VERSION
    assert reread.index_hash == rebuilt.index_hash
    assert reread.stale is False
    assert [entry.memory_id for entry in reread.entries] == [
        fact.envelope.memory_id,
        procedure.envelope.memory_id,
    ]
    assert {entry.record_kind for entry in reread.entries} == {
        MemoryRecordKind.SEMANTIC_FACT,
        MemoryRecordKind.PROCEDURAL_SNAPSHOT,
    }


def test_stale_index_is_detected_after_canonical_write(tmp_path: Path) -> None:
    binding = _binding(tmp_path)
    store = _store(binding)
    store.write_record(_record(statement="Initial durable memory fact."))
    index_store = _index_store(binding)
    index_store.rebuild(indexed_at=_NOW)

    store.write_record(_record(statement="Later fact makes the derived index stale."))

    stale = index_store.read_current(require_fresh=False)
    assert stale.stale is True
    with pytest.raises(DerivedRetrievalIndexStaleError):
        index_store.read_current()


def test_read_current_raises_when_never_rebuilt(tmp_path: Path) -> None:
    """B-28 finding #4 (test-quality preflight 2026-07-12) — only the
    already-rebuilt-then-stale path was covered; calling ``read_current()``
    (or ``require_fresh=False``) before any ``rebuild()`` has ever run must
    raise ``DerivedRetrievalIndexMissingError``, not a missing-file crash or
    a silent empty index."""
    binding = _binding(tmp_path)
    index_store = _index_store(binding)

    with pytest.raises(DerivedRetrievalIndexMissingError):
        index_store.read_current()
    with pytest.raises(DerivedRetrievalIndexMissingError):
        index_store.read_current(require_fresh=False)


def test_empty_store_rebuild_returns_valid_empty_retrieval_base(tmp_path: Path) -> None:
    binding = _binding(tmp_path)
    index_store = _index_store(binding)

    rebuilt = index_store.rebuild(indexed_at=_NOW)
    result = index_store.retrieve(DerivedRetrievalIndexQuery(query_summary="anything"))

    assert rebuilt.entries == ()
    assert rebuilt.stale is False
    assert result.index_hash == rebuilt.index_hash
    assert result.selected_refs == ()
    assert result.considered_count == 0


def test_large_store_retrieval_uses_bounded_index_metadata(tmp_path: Path) -> None:
    binding = _binding(tmp_path)
    store = _store(binding)
    for index in range(80):
        store.write_record(
            _record(
                statement=f"Unrelated memory record {index}.",
                tags=("filler",),
                created_at=_NOW + timedelta(seconds=index),
            )
        )
    target = _record(
        statement="Derived retrieval indexes must select bounded metadata.",
        tags=("needle", "retrieval"),
        created_at=_NOW + timedelta(seconds=100),
    )
    store.write_record(target)
    index_store = _index_store(binding)
    index_store.rebuild(indexed_at=_NOW)
    for path in (tmp_path / "memory" / "semantic" / "facts").glob("*.json"):
        path.unlink()

    result = index_store.retrieve(
        DerivedRetrievalIndexQuery(
            query_summary="needle retrieval",
            allowed_kinds=(MemoryRecordKind.SEMANTIC_FACT,),
            scope=_scope(),
            limit=3,
        )
    )

    assert result.selected_refs == (target.envelope.memory_id,)
    assert result.considered_count == 81
    assert len(result.entries) == 1
    assert result.entries[0].search_terms
    assert "statement" not in result.entries[0].model_dump()


def test_globally_scoped_record_matches_a_dimension_scoped_query(tmp_path: Path) -> None:
    """Regression guard — a record with `workflow=None` (globally scoped on
    that dimension) must still match a query that requests a concrete
    `workflow` value; only a genuine mismatch between two concrete values
    should exclude a candidate."""
    binding = _binding(tmp_path)
    store = _store(binding)
    global_scope = MemoryScope(
        project="arhugula-v2",
        workflow=None,
        cli_profile="codex",
        visibility=MemoryVisibility.WORKFLOW,
    )
    target = _record(statement="Globally-scoped memory record.", scope=global_scope)
    store.write_record(target)
    index_store = _index_store(binding)
    index_store.rebuild(indexed_at=_NOW)

    result = index_store.retrieve(
        DerivedRetrievalIndexQuery(
            scope=_scope(workflow="some-other-workflow"),
        )
    )

    assert result.selected_refs == (target.envelope.memory_id,)


def test_search_accelerator_is_non_authoritative(tmp_path: Path) -> None:
    binding = _binding(tmp_path)
    store = _store(binding)
    first = _record(statement="First indexed fact.", tags=("one",), created_at=_NOW)
    second = _record(
        statement="Second indexed fact.",
        tags=("two",),
        created_at=_NOW + timedelta(seconds=1),
    )
    store.write_record(first)
    store.write_record(second)
    index_store = _index_store(binding)
    index_store.rebuild(indexed_at=_NOW)

    result = index_store.retrieve(
        DerivedRetrievalIndexQuery(query_summary="indexed", limit=2),
        search_accelerator=lambda _query, _entries: (
            "mem:semantic:semantic_fact:" + "f" * 64,
            first.envelope.memory_id,
        ),
    )

    assert result.selected_refs == (first.envelope.memory_id, second.envelope.memory_id)


def _commit_seqs(binding: MemoryRootBinding) -> list[int]:
    """Every stale marker's `commit_seq`, in ledger order."""

    path = _index_store(binding).index_path()
    return [
        int(json.loads(line)["commit_seq"])
        for line in path.read_text().splitlines()
        if line.strip() and json.loads(line).get("event") == "stale"
    ]


def test_a_late_rebuild_of_an_older_commit_does_not_supersede_a_newer_index(
    tmp_path: Path,
) -> None:
    """Codex R2 [P2-1] — ledger POSITION is not the freshness authority.

    The store notifies derived-index hooks OUTSIDE its write hold (the callback
    deadlock fix), so two overlapping writes can rebuild in either order. The
    hazardous interleaving: A commits, B commits, B's hook rebuilds A+B, and
    A's slower hook appends its A-ONLY rebuild LAST. Reading the last `rebuilt`
    line then reports the older index as current — with B missing and `stale`
    false, because B's marker precedes that final line.

    Reproduced deterministically at the ledger, with real rebuild output: the
    A-only rebuild is produced while only A exists, withheld, and replayed
    after B's. No threads, so the witness cannot flake.
    """

    binding = _binding(tmp_path)
    store = _store(binding)
    index_store = _index_store(binding)
    path = index_store.index_path()

    record_a = _record(statement="Record A, committed first.")
    record_b = _record(statement="Record B, committed second.")

    # Commit A, and produce the rebuild A's hook would have produced.
    store.write_record(record_a)
    [seq_a] = _commit_seqs(binding)
    index_store.rebuild(indexed_at=_NOW, commit_seq=seq_a)
    lines = path.read_text().splitlines()
    late_rebuild_line = lines[-1]
    # Withhold it — A's hook has not returned yet.
    path.write_text("\n".join(lines[:-1]) + "\n")

    # Commit B; B's hook rebuilds and sees BOTH records.
    store.write_record(record_b)
    seq_a_again, seq_b = _commit_seqs(binding)
    assert seq_a_again == seq_a
    assert seq_b > seq_a, "commit_seq must order the two commits"
    index_store.rebuild(indexed_at=_NOW + timedelta(seconds=1), commit_seq=seq_b)

    # A's hook finally lands — LAST in the append-only ledger.
    with path.open("a", encoding="utf-8") as fh:
        fh.write(late_rebuild_line + "\n")

    current = index_store.read_current()

    indexed = {entry.memory_id for entry in current.entries}
    assert indexed == {record_a.envelope.memory_id, record_b.envelope.memory_id}, (
        "the late A-only rebuild superseded the newer A+B index — a committed "
        "record is missing from an index reported as current"
    )
    assert not current.stale


def test_a_commit_no_rebuild_covers_is_stale_even_when_its_marker_comes_first(
    tmp_path: Path,
) -> None:
    """The other half of [P2-1] — under-covered, not merely out-of-order.

    A commits, B commits, and only A's hook ever rebuilds. Both stale markers
    precede that rebuild, so the purely positional rule sees no marker AFTER
    the current index and reports it fresh — while B is genuinely absent.
    `commit_seq` makes the gap visible: the highest committed marker outruns
    what the rebuild claims to cover.
    """

    binding = _binding(tmp_path)
    store = _store(binding)
    index_store = _index_store(binding)

    store.write_record(_record(statement="Record A, covered."))
    [seq_a] = _commit_seqs(binding)
    store.write_record(_record(statement="Record B, never rebuilt for."))

    # A's hook rebuilds, but attributes only A's commit (the honest,
    # under-claiming attribution the rebuild contract requires).
    index_store.rebuild(indexed_at=_NOW, commit_seq=seq_a)

    with pytest.raises(DerivedRetrievalIndexStaleError):
        index_store.read_current()
    assert index_store.read_current(require_fresh=False).stale


class _PreB93LedgerEvent(BaseModel):
    """Verbatim copy of the PRE-B-93 closed rebuild model.

    `git show fc40fb2b:harness-is/src/harness_is/memory_retrieval_index.py`,
    lines 135-144. Reproduced here rather than imported so the witness keeps
    testing the OLD shape after the live one moves on.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    event: Literal["rebuilt"]
    index_version: str
    indexed_at: datetime
    index_hash: str
    entries: tuple[DerivedRetrievalIndexEntry, ...]


def _pre_b93_read_current(path: Path) -> tuple[int, bool]:
    """Replay the PRE-B-93 read loop verbatim (same source, lines 210-227).

    Returns `(entry_count, stale)`. Raises exactly where the old reader would:
    `ValidationError` out of the closed model on any unexpected key.
    """

    current: _PreB93LedgerEvent | None = None
    stale_after_current = False
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        raw_object: object = json.loads(line)
        if not isinstance(raw_object, dict):
            continue
        raw = cast("Mapping[str, object]", raw_object)
        event = raw.get("event")
        if event == "rebuilt":
            current = _PreB93LedgerEvent.model_validate(raw)
            stale_after_current = False
        elif event == "stale" and current is not None:
            stale_after_current = True
    if current is None:
        raise AssertionError("the pre-B-93 reader found no rebuilt event")
    return len(current.entries), stale_after_current


def test_a_new_writer_ledger_still_parses_under_the_pre_b93_reader(tmp_path: Path) -> None:
    """Codex R3 [P1] — the mixed-version window must not break the old side.

    The memory root is repo-derived and shared, so a `harness daemon` started
    before an upgrade keeps reading a ledger a new one-shot process is writing
    (the same topology the U-MEM-27 cross-process witness rests on). The old
    reader validates EVERY `rebuilt` line against a closed `extra="forbid"`
    model, so one added key there — even serialized `null` — raises
    `ValidationError` on its auto-refresh path and leaves its retrieval broken
    until restart.

    So this drives the real new writer and replays the real old reader over
    every event kind the new writer emits to the shared file.
    """

    binding = _binding(tmp_path)
    store = _store(binding)
    index_store = _index_store(binding)
    path = index_store.index_path()

    store.write_record(_record(statement="Record visible to both versions."))
    [seq] = _commit_seqs(binding)
    index_store.rebuild(indexed_at=_NOW, commit_seq=seq)
    store.write_record(_record(statement="A later commit the old reader must see as stale."))

    kinds = {
        str(json.loads(line)["event"]) for line in path.read_text().splitlines() if line.strip()
    }
    assert kinds == {"stale", "rebuilt_coverage", "rebuilt"}, (
        f"unexpected event kinds on the shared ledger: {sorted(kinds)} — every kind here "
        f"must be one the pre-B-93 reader either validates cleanly or skips"
    )

    # The load-bearing call: raises ValidationError if any shared-file event
    # the new writer emits carries a key the old closed model forbids.
    entry_count, stale = _pre_b93_read_current(path)

    assert entry_count == 1
    assert stale, "the old reader must still see the later commit's stale marker"

    # And the new reader agrees about the same ledger.
    assert index_store.read_current(require_fresh=False).stale
