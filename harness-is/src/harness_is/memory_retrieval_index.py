"""Derived memory retrieval index - U-MEM-10.

The canonical semantic/procedural records remain the source of truth. This
module rebuilds the derived ``semantic/index.jsonl`` projection from those
records and provides a bounded metadata retrieval base for later U-MEM-11
ranking and packet assembly.

SCOPE OF THE COMMIT-ORDERING PROTECTION (B-93 arc). ``read_current`` orders
rebuilds by commit token rather than by ledger position, but that protection
covers a ledger written ENTIRELY by B-93-or-later writers. Two bounds are
registered rather than fixed:

* A mixed-version window with a live PRE-B-93 WRITER (not merely an old
  reader, which `_DerivedRetrievalIndexLedgerEvent`'s byte-compatibility
  already covers) puts untokenized stale markers on the ledger. Legacy
  markers carry no commit token BY DEFINITION, so no read-side rule can
  order them against a covered rebuild retroactively - the ledger falls back
  to positional ordering and can misorder exactly as pre-B-93 could. See
  register row B-95.
* Rebuilds that pass no ``commit_seq`` - which includes the production
  auto-refresh path, untokenized by design - remain positional last-wins and
  can leave an older overlapping snapshot reading fresh. See register row
  B-94.

Both are pre-existing behaviours that this protocol narrows rather than
introduces; neither is witnessed here, deliberately.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Literal, NamedTuple, Self, cast

from harness_core import DeploymentSurface
from pydantic import BaseModel, ConfigDict, Field, model_validator

from harness_is.memory_path_registry import (
    MemoryPathClass,
    MemoryPathRegistry,
    MemoryRootBinding,
)
from harness_is.memory_record_envelope import (
    MemoryID,
    MemoryRecordKind,
    MemoryScope,
    MemoryTier,
    RedactionState,
)
from harness_is.memory_scope_value_domain import (
    RequestScopeResolution,
    ScopeFamilyCanonicalizer,
    resolve_request_scope,
    scope_intersection_denied,
    scope_partition_denied,
)
from harness_is.memory_store import MemoryStoreRecord

CURRENT_DERIVED_RETRIEVAL_INDEX_VERSION = "derived-retrieval-index/v1"
"""Current rebuildable retrieval-index payload version."""

_REBUILT_EVENT: Literal["rebuilt"] = "rebuilt"
_STALE_EVENT: Literal["stale"] = "stale"
_REBUILT_COVERAGE_EVENT: Literal["rebuilt_coverage"] = "rebuilt_coverage"
_MAX_SEARCH_TERMS_PER_RECORD = 64
_INACTIVE_STATUSES = {"denied", "expired", "proposed", "superseded", "tombstoned"}

type IndexJSON = str | int | bool | None | list[IndexJSON] | dict[str, IndexJSON]
DerivedRetrievalSearchAccelerator = Callable[
    ["DerivedRetrievalIndexQuery", tuple["DerivedRetrievalIndexEntry", ...]],
    Sequence[str],
]


class DerivedRetrievalIndexMissingError(LookupError):
    """Raised when no rebuilt retrieval index snapshot exists."""


class DerivedRetrievalIndexStaleError(ValueError):
    """Raised when canonical writes happened after the current index rebuild."""


class DerivedRetrievalIndexEntry(BaseModel):
    """One bounded metadata row in the derived retrieval index."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    memory_id: MemoryID
    record_kind: MemoryRecordKind
    tier: MemoryTier
    scope: MemoryScope
    created_at: datetime
    updated_at: datetime | None = None
    content_hash: str
    redaction_state: RedactionState
    supersedes: tuple[MemoryID, ...] = ()
    superseded_by: tuple[MemoryID, ...] = ()
    status: str | None = None
    confidence: str | None = None
    tags: tuple[str, ...] = ()
    search_terms: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _validate_hash(self) -> Self:
        if len(self.content_hash) != 64:
            raise ValueError("content_hash must be a SHA-256 hex digest")
        try:
            bytes.fromhex(self.content_hash)
        except ValueError as exc:
            raise ValueError("content_hash must be a SHA-256 hex digest") from exc
        return self


class DerivedRetrievalIndex(BaseModel):
    """Current rebuilt index snapshot plus freshness state."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    index_version: str
    indexed_at: datetime
    index_hash: str
    entries: tuple[DerivedRetrievalIndexEntry, ...] = ()
    stale: bool = False


class DerivedRetrievalIndexQuery(BaseModel):
    """Metadata-only query over the rebuilt derived retrieval index."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    query_summary: str = ""
    allowed_kinds: tuple[MemoryRecordKind, ...] = ()
    scope: MemoryScope | None = None
    limit: int = Field(default=20, ge=0)


class DerivedRetrievalIndexResult(BaseModel):
    """Bounded retrieval base returned from the derived index."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    index_version: str
    index_hash: str
    selected_refs: tuple[MemoryID, ...]
    entries: tuple[DerivedRetrievalIndexEntry, ...]
    considered_count: int
    stale: bool = False


class _DerivedRetrievalIndexLedgerEvent(BaseModel):
    """Append-only event stored in ``semantic/index.jsonl``."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event: Literal["rebuilt"]
    index_version: str
    indexed_at: datetime
    index_hash: str
    entries: tuple[DerivedRetrievalIndexEntry, ...]

    # BYTE-COMPATIBLE WITH PRE-B-93 WRITERS, DELIBERATELY (Codex R3 [P1]).
    # This model is `extra="forbid"` and an older reader validates EVERY
    # `rebuilt` line against its own copy of it. A new writer sharing a memory
    # root with a still-running older process - the daemon + one-shot upgrade
    # window - would break that reader's retrieval outright by adding ANY key
    # here, including one serialized as `null`. Rebuild coverage therefore
    # rides a separate event kind (`_REBUILT_COVERAGE_EVENT`), which the older
    # reader's `event ==` discrimination skips instead of validating.


class _LedgerEventMeta(NamedTuple):
    """One ledger line reduced to what `read_current`'s rules need - no payload.

    A `rebuilt` line carries the ENTIRE index entry array. Holding the decoded
    form of every line would tie peak memory to the ledger's rebuild history
    rather than to a single index, so the resolution passes run over these
    scalars and only the winning line is decoded (Codex R5 [P2]).

    `seq` is whichever commit token the line's own kind carries: a stale
    marker's `commit_seq`, or a coverage event's `covers_commit_seq`.
    """

    kind: str
    index_hash: str | None
    seq: int | None
    line_number: int


class _RebuiltCoverageEvent(BaseModel):
    """Which commit a `rebuilt` event's index reflects (`semantic/index.jsonl`).

    A SEPARATE event kind rather than a field on the rebuild, so the rebuild
    stays byte-compatible for readers that predate this metadata: their loop
    matches neither `rebuilt` nor `stale` on this line and ignores it.

    It is written AFTER the rebuild it describes and claims exactly ONE of
    them: the nearest preceding rebuild of the same content not already
    claimed. `index_hash` alone is NOT the association (Codex R4) - the same
    entries can be rebuilt many times, and a later UNTOKENIZED rebuild must
    stay untokenized rather than inherit an older rebuild's coverage.

    The claim walk needs no atomic paired append, which matters because
    `_append_jsonl` takes no lock and another process can land lines between a
    rebuild and its coverage.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    event: Literal["rebuilt_coverage"]
    index_hash: str
    covers_commit_seq: int


class DerivedRetrievalIndexStore:
    """Filesystem-backed derived index API for C-MEM-02/C-MEM-11."""

    def __init__(
        self,
        *,
        root_binding: MemoryRootBinding | None = None,
        deployment_surface: DeploymentSurface = DeploymentSurface.LOCAL_DEVELOPMENT,
        family_canonicalizer: ScopeFamilyCanonicalizer | None = None,
    ) -> None:
        """Bind the index location and the optional request-side value domain.

        `family_canonicalizer` is the C-MEM-03 request-side value-domain
        authority (U-MEM-26). It is optional so the IS axis keeps zero outbound
        cross-axis edges; production composition MUST inject it - absent, a
        queried `provider_family` is compared as the raw string it arrived as.
        See `memory_scope_value_domain`.
        """
        self._registry = MemoryPathRegistry(root_binding)
        self._deployment_surface = deployment_surface
        self._family_canonicalizer = family_canonicalizer

    def index_path(self) -> Path:
        """Return the canonical derived semantic index ledger path."""

        return self._registry.resolve_path(
            MemoryPathClass.SEMANTIC_INDEX_LEDGER,
            self._deployment_surface,
        )

    def rebuild(
        self,
        *,
        indexed_at: datetime,
        commit_seq: int | None = None,
    ) -> DerivedRetrievalIndex:
        """Rebuild the current index from canonical semantic/procedural records.

        `commit_seq` is the `DerivedIndexInvalidation.commit_seq` of the write
        this rebuild answers, and a hook rebuilding in response to one MUST
        pass it. The store notifies hooks outside its write hold, so two
        overlapping writes can rebuild in either order; without the token, a
        late rebuild of an older commit lands LAST in the append-only ledger
        and `read_current` would report it as the newest index, silently
        dropping the newer write's records.

        Attributing the rebuild to its TRIGGERING commit under-claims by
        design: the rebuild reads the filesystem after that commit, so it
        reflects at least that commit and possibly later ones. Under-claiming
        costs a spurious `stale` (safe); over-claiming would report a missing
        record as fresh (not safe).
        """

        entries = tuple(_iter_index_entries(self._registry, self._deployment_surface))
        index_hash = _compute_index_hash(
            entries,
            index_version=CURRENT_DERIVED_RETRIEVAL_INDEX_VERSION,
        )
        index = DerivedRetrievalIndex(
            index_version=CURRENT_DERIVED_RETRIEVAL_INDEX_VERSION,
            indexed_at=indexed_at,
            index_hash=index_hash,
            entries=entries,
            stale=False,
        )
        path = self.index_path()
        event = _DerivedRetrievalIndexLedgerEvent(
            event=_REBUILT_EVENT,
            index_version=index.index_version,
            indexed_at=index.indexed_at,
            index_hash=index.index_hash,
            entries=index.entries,
        )
        _append_jsonl(path, _canonical_json_bytes(event.model_dump(mode="json")))
        if commit_seq is not None:
            # AFTER its rebuild, deliberately. The two appends are NOT atomic
            # as a pair (`_append_jsonl` takes no lock), so either line can be
            # the one a crash loses. Losing the trailing coverage leaves an
            # untokenized rebuild, which falls to the legacy positional rule -
            # safe. The reverse order would leave an ORPHAN coverage that an
            # EARLIER unclaimed rebuild of the same content could adopt (the
            # claim walk only ever pairs a coverage to a rebuild that precedes
            # it), which is the misassociation this ordering exists to prevent.
            coverage = _RebuiltCoverageEvent(
                event=_REBUILT_COVERAGE_EVENT,
                index_hash=index.index_hash,
                covers_commit_seq=commit_seq,
            )
            _append_jsonl(path, _canonical_json_bytes(coverage.model_dump(mode="json")))
        return index

    def read_current(self, *, require_fresh: bool = True) -> DerivedRetrievalIndex:
        """Read the newest rebuilt index and detect uncovered canonical writes.

        Ledger POSITION alone is not the freshness authority. Because the store
        notifies its derived-index hooks outside the write hold, two overlapping
        writes can rebuild in either order, so the last `rebuilt` line is not
        necessarily the newest index. Two rules run together:

        * a `rebuilt_coverage` event ORDERS rebuilds. A rebuild answering an
          older commit than one already accepted is ignored outright, however
          late it landed in the file. Coverage is a separate event kind so the
          `rebuilt` line stays byte-compatible for pre-B-93 readers.
        * a stale marker's `commit_seq` greater than the accepted rebuild's
          means that commit is NOT reflected in this index - stale, whatever the
          two lines' relative positions.

        The original positional rule is preserved verbatim underneath for
        events that carry no token (legacy ledger lines and direct `rebuild()`
        calls), so an untokenized ledger behaves exactly as before.
        """

        winner: _LedgerEventMeta | None = None
        current_seq: int | None = None
        stale_after_current = False
        max_stale_seq: int | None = None
        path = self.index_path()
        if not path.exists():
            raise DerivedRetrievalIndexMissingError(f"retrieval index not found at {path!s}")

        lines = path.read_text().splitlines()

        # PASS 1 - METADATA ONLY (Codex R5 [P2]). Every `rebuilt` event carries
        # the COMPLETE entry array, so retaining each decoded event would make
        # peak memory grow with the ledger's whole rebuild HISTORY rather than
        # with one index. Each decoded line is reduced to the few scalars the
        # rules below need and then dropped; only the winning rebuild is
        # decoded into a snapshot, after the winner is known.
        records: list[_LedgerEventMeta] = []
        for line_number, line in enumerate(lines):
            if not line.strip():
                continue
            raw_object: object = json.loads(line)
            if not isinstance(raw_object, dict):
                continue
            raw = cast("Mapping[str, object]", raw_object)
            event = raw.get("event")
            if not isinstance(event, str):
                continue
            index_hash = raw.get("index_hash")
            seq_value = (
                raw.get("covers_commit_seq")
                if event == _REBUILT_COVERAGE_EVENT
                else raw.get("commit_seq")
            )
            records.append(
                _LedgerEventMeta(
                    kind=event,
                    index_hash=index_hash if isinstance(index_hash, str) else None,
                    seq=seq_value if isinstance(seq_value, int) else None,
                    line_number=line_number,
                )
            )
            # `raw` dies here - no decoded entry array outlives this iteration.

        # Pair each coverage event to ONE rebuild INSTANCE (Codex R4 [P2]): the
        # nearest PRECEDING rebuild of the same content that no other coverage
        # event has already claimed. Binding by content hash alone let a single
        # coverage event attach to every rebuild that happened to produce the
        # same entries - including a later UNTOKENIZED one, whose whole point is
        # that it has no coverage and must fall to the legacy positional rule.
        #
        # The claim walk is what makes this safe without atomic paired appends
        # (`_append_jsonl` takes no lock, so another process can interleave
        # between a rebuild and its coverage): each coverage consumes exactly
        # one rebuild. Interleaved same-hash pairs MAY cross-claim (the walk is
        # LIFO), and that is benign by construction: the hash covers entries
        # only, so two same-hash rebuilds are byte-identical as content, any
        # claimed seq is a true statement about that content, and the winner
        # rule takes the max seq under either pairing. The one arrangement
        # that diverges - a tokenized and an untokenized rebuild of the same
        # content, where the untokenized one adopts the token - errs toward a
        # spurious stale, the documented-safe direction. An extra rebuild
        # simply goes unclaimed.
        coverage_for_record: dict[int, int] = {}
        unclaimed_rebuilds: dict[str, list[int]] = {}
        for position, meta in enumerate(records):
            if meta.index_hash is None:
                continue
            if meta.kind == _REBUILT_EVENT:
                unclaimed_rebuilds.setdefault(meta.index_hash, []).append(position)
            elif meta.kind == _REBUILT_COVERAGE_EVENT:
                pending = unclaimed_rebuilds.get(meta.index_hash)
                if meta.seq is not None and pending:
                    coverage_for_record[pending.pop()] = meta.seq

        for position, meta in enumerate(records):
            if meta.kind == _REBUILT_EVENT:
                seq = coverage_for_record.get(position)
                if seq is not None and current_seq is not None and seq < current_seq:
                    # A LATE rebuild answering an OLDER commit. Accepting it
                    # would drop every record committed since the rebuild it
                    # displaces, and report the result as fresh.
                    continue
                winner = meta
                current_seq = seq
                stale_after_current = False
            elif meta.kind == _STALE_EVENT:
                if meta.seq is not None:
                    max_stale_seq = (
                        meta.seq if max_stale_seq is None else max(max_stale_seq, meta.seq)
                    )
                if winner is not None:
                    stale_after_current = True
        if winner is None:
            raise DerivedRetrievalIndexMissingError(f"retrieval index not found at {path!s}")
        if current_seq is not None and max_stale_seq is not None and max_stale_seq > current_seq:
            stale_after_current = True
        if stale_after_current and require_fresh:
            raise DerivedRetrievalIndexStaleError("retrieval index is stale after canonical write")
        # The ONLY full decode: one snapshot per call, whatever the history.
        winning_object: object = json.loads(lines[winner.line_number])
        current = _index_from_event(cast("Mapping[str, object]", winning_object))
        return current.model_copy(update={"stale": stale_after_current})

    def retrieve(
        self,
        query: DerivedRetrievalIndexQuery,
        *,
        search_accelerator: DerivedRetrievalSearchAccelerator | None = None,
    ) -> DerivedRetrievalIndexResult:
        """Return bounded metadata matches from the current derived index."""

        index = self.read_current()
        resolution = (
            None
            if query.scope is None
            else resolve_request_scope(query.scope, self._family_canonicalizer)
        )
        candidates = tuple(_filter_candidates(index.entries, query, resolution))
        ordered = _order_candidates(query, candidates, search_accelerator)
        selected_entries = tuple(ordered[: query.limit])
        return DerivedRetrievalIndexResult(
            index_version=index.index_version,
            index_hash=index.index_hash,
            selected_refs=tuple(entry.memory_id for entry in selected_entries),
            entries=selected_entries,
            considered_count=len(index.entries),
            stale=index.stale,
        )


def _iter_index_entries(
    registry: MemoryPathRegistry,
    deployment_surface: DeploymentSurface,
) -> tuple[DerivedRetrievalIndexEntry, ...]:
    records: list[MemoryStoreRecord] = []
    for path_class in _INDEXED_RECORD_DIRECTORIES:
        directory = registry.resolve_path(path_class, deployment_surface)
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.json"), key=lambda item: item.as_posix()):
            records.append(_read_store_record(path))
    entries = [_entry_from_record(record) for record in records]
    return tuple(
        sorted(
            entries,
            key=lambda entry: (
                _tier_sort_key(entry.tier),
                entry.record_kind.value,
                str(entry.memory_id),
            ),
        )
    )


_INDEXED_RECORD_DIRECTORIES = (
    MemoryPathClass.SEMANTIC_FACTS_DIR,
    MemoryPathClass.SEMANTIC_PREFERENCES_DIR,
    MemoryPathClass.SEMANTIC_DECISIONS_DIR,
    MemoryPathClass.SEMANTIC_CONVENTIONS_DIR,
    MemoryPathClass.SEMANTIC_FAILURES_DIR,
    MemoryPathClass.SEMANTIC_RESEARCH_DIR,
    MemoryPathClass.PROCEDURAL_SNAPSHOTS_DIR,
)


def _read_store_record(path: Path) -> MemoryStoreRecord:
    raw = json.loads(path.read_text())
    if not isinstance(raw, dict):
        raise ValueError(f"memory record at {path!s} must be a JSON object")
    return MemoryStoreRecord.model_validate(
        {
            "envelope": _deserialize_envelope(cast("Mapping[str, object]", raw["envelope"])),
            "content": raw["content"],
        }
    )


def _deserialize_envelope(raw: Mapping[str, object]) -> dict[str, object]:
    envelope = dict(raw)
    envelope["content_hash"] = _bytes32_from_json(envelope["content_hash"])
    source_refs: list[dict[str, object]] = []
    source_refs_object = envelope.get("source_refs", ())
    if not isinstance(source_refs_object, Sequence) or isinstance(source_refs_object, str | bytes):
        raise ValueError("stored memory envelope source_refs must be a sequence")
    for source_ref in cast("Sequence[object]", source_refs_object):
        if not isinstance(source_ref, dict):
            raise ValueError("stored memory envelope source_ref must be an object")
        source_ref_payload = dict(cast("Mapping[str, object]", source_ref))
        if source_ref_payload.get("content_hash") is not None:
            source_ref_payload["content_hash"] = _bytes32_from_json(
                source_ref_payload["content_hash"]
            )
        source_refs.append(source_ref_payload)
    envelope["source_refs"] = source_refs
    return envelope


def _entry_from_record(record: MemoryStoreRecord) -> DerivedRetrievalIndexEntry:
    content = record.content
    return DerivedRetrievalIndexEntry(
        memory_id=record.envelope.memory_id,
        record_kind=record.envelope.kind,
        tier=record.envelope.tier,
        scope=record.envelope.scope,
        created_at=record.envelope.created_at,
        updated_at=record.envelope.updated_at,
        content_hash=record.envelope.content_hash.hex(),
        redaction_state=record.envelope.redaction_state,
        supersedes=record.envelope.supersedes,
        superseded_by=record.envelope.superseded_by,
        status=_string_or_none(content.get("status")),
        confidence=_string_or_none(content.get("confidence")),
        tags=_string_tuple(content.get("tags")),
        search_terms=_search_terms_for(record),
    )


def _filter_candidates(
    entries: Sequence[DerivedRetrievalIndexEntry],
    query: DerivedRetrievalIndexQuery,
    resolution: RequestScopeResolution | None,
) -> tuple[DerivedRetrievalIndexEntry, ...]:
    """Apply the C-MEM-03 scope boundary before ranking (U-MEM-26).

    `resolution` is `None` exactly when the query carries no scope object at
    all. That is not a total wildcard: an absent request scope names no
    partition, so it is denied against partition-scoped entries on the same
    terms as an explicit `null` (`scope_partition_denied` with no requested
    scope). The remaining dimensions and the visibility rank stay unconstrained,
    since an absent scope asserts nothing about them.

    An out-of-domain `provider_family` is a different disposition again: it
    rejects the QUERY outright, so the result is empty rather than narrowed to
    the unpartitioned remainder (see `memory_scope_value_domain`).
    """
    if resolution is not None and resolution.family_out_of_domain:
        return ()
    query_terms = set(_tokenize(query.query_summary))
    candidates: list[DerivedRetrievalIndexEntry] = []
    for entry in entries:
        if not _is_active_retrieval_entry(entry):
            continue
        if query.allowed_kinds and entry.record_kind not in query.allowed_kinds:
            continue
        if resolution is None:
            if scope_partition_denied(entry.scope, None):
                continue
        elif not _scope_matches(entry.scope, resolution.scope):
            continue
        if query_terms and not (set(entry.search_terms) & query_terms):
            continue
        candidates.append(entry)
    return tuple(candidates)


def _order_candidates(
    query: DerivedRetrievalIndexQuery,
    candidates: tuple[DerivedRetrievalIndexEntry, ...],
    search_accelerator: DerivedRetrievalSearchAccelerator | None,
) -> tuple[DerivedRetrievalIndexEntry, ...]:
    default_order = tuple(sorted(candidates, key=lambda entry: _rank_key(query, entry)))
    if search_accelerator is None:
        return default_order

    by_id = {str(entry.memory_id): entry for entry in default_order}
    accelerator_order: list[DerivedRetrievalIndexEntry] = []
    seen: set[str] = set()
    for memory_id in search_accelerator(query, candidates):
        key = str(memory_id)
        if key in seen or key not in by_id:
            continue
        seen.add(key)
        accelerator_order.append(by_id[key])
    accelerator_order.extend(entry for entry in default_order if str(entry.memory_id) not in seen)
    return tuple(accelerator_order)


def _rank_key(
    query: DerivedRetrievalIndexQuery,
    entry: DerivedRetrievalIndexEntry,
) -> tuple[int, str, str]:
    query_terms = set(_tokenize(query.query_summary))
    match_count = len(query_terms & set(entry.search_terms)) if query_terms else 0
    return (-match_count, _reverse_iso(entry.created_at), str(entry.memory_id))


def _is_active_retrieval_entry(entry: DerivedRetrievalIndexEntry) -> bool:
    if entry.redaction_state is not RedactionState.ACTIVE:
        return False
    if entry.status is not None and entry.status in _INACTIVE_STATUSES:
        return False
    return not entry.superseded_by


def _scope_matches(record_scope: MemoryScope, requested_scope: MemoryScope) -> bool:
    """True when the requested scope may reach this record (C-MEM-03, U-MEM-26).

    The scope-partition fields (`provider_family`, `tenant`) carry the
    asymmetric-`null` semantics: a `null` RECORD value is the unpartitioned
    wildcard, but a `null` REQUEST value does NOT widen access past a
    partitioned record. The remaining fields keep the either-side-`null`-skips
    semantics. Both rules live at `memory_scope_value_domain`, shared with the
    retriever predicate, per the per-layer independence U-MEM-26 requires.
    """
    if scope_partition_denied(record_scope, requested_scope):
        return False
    if scope_intersection_denied(record_scope, requested_scope):
        return False
    return _visibility_rank(record_scope.visibility) <= _visibility_rank(requested_scope.visibility)


def _visibility_rank(visibility: object) -> int:
    ranks = {
        "private": 0,
        "workflow": 1,
        "project": 2,
        "tenant": 3,
        "public": 4,
    }
    return ranks[str(visibility)]


def _search_terms_for(record: MemoryStoreRecord) -> tuple[str, ...]:
    content = record.content
    values: list[object] = [
        record.envelope.memory_id,
        record.envelope.kind,
        record.envelope.tier,
        record.envelope.scope.project,
        record.envelope.scope.workflow,
        record.envelope.scope.workload_class,
        record.envelope.scope.provider_family,
        record.envelope.scope.cli_profile,
        record.envelope.scope.tenant,
        content.get("semantic_kind"),
        content.get("statement"),
        content.get("confidence"),
        content.get("status"),
        content.get("injection_policy"),
        content.get("snapshot_id"),
        content.get("workflow_id"),
        content.get("cli_profile"),
        content.get("procedural_update"),
        content.get("tags"),
    ]
    terms: set[str] = set()
    for value in values:
        terms.update(_tokenize_value(value))
    return tuple(sorted(terms)[:_MAX_SEARCH_TERMS_PER_RECORD])


def _tokenize_value(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, StrEnum):
        return _tokenize(value.value)
    if isinstance(value, str):
        return _tokenize(value)
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        terms: list[str] = []
        sequence = cast("Sequence[object]", value)
        for item in sequence:
            terms.extend(_tokenize_value(item))
        return tuple(terms)
    return ()


def _tokenize(value: str) -> tuple[str, ...]:
    normalized = unicodedata.normalize("NFC", value).lower()
    return tuple(re.findall(r"[a-z0-9_:-]+", normalized))


def _string_or_none(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, str):
        return value
    return None


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        return ()
    sequence = cast("Sequence[object]", value)
    return tuple(item for item in sequence if isinstance(item, str))


def _compute_index_hash(
    entries: tuple[DerivedRetrievalIndexEntry, ...],
    *,
    index_version: str,
) -> str:
    payload = {
        "index_version": index_version,
        "entries": [entry.model_dump(mode="json") for entry in entries],
    }
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


def _index_from_event(raw: Mapping[str, object]) -> DerivedRetrievalIndex:
    event = _DerivedRetrievalIndexLedgerEvent.model_validate(raw)
    index = DerivedRetrievalIndex(
        index_version=event.index_version,
        indexed_at=event.indexed_at,
        index_hash=event.index_hash,
        entries=event.entries,
        stale=False,
    )
    expected_hash = _compute_index_hash(index.entries, index_version=index.index_version)
    if index.index_hash != expected_hash:
        raise ValueError("stored retrieval index hash does not match entries")
    return index


def _tier_sort_key(tier: MemoryTier) -> int:
    return {MemoryTier.SEMANTIC: 0, MemoryTier.PROCEDURAL: 1}.get(tier, 99)


def _reverse_iso(value: datetime) -> str:
    return "".join(chr(255 - ord(character)) for character in value.isoformat())


def _bytes32_from_json(value: object) -> bytes:
    if isinstance(value, bytes):
        digest = value
    elif isinstance(value, str):
        digest = bytes.fromhex(value)
    else:
        raise TypeError("expected SHA-256 digest hex string")
    if len(digest) != 32:
        raise ValueError("expected SHA-256 digest to be exactly 32 bytes")
    return digest


def _canonical_json_bytes(payload: object) -> bytes:
    return json.dumps(
        cast("IndexJSON", payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _append_jsonl(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as fh:
        fh.write(payload + b"\n")


__all__ = [
    "CURRENT_DERIVED_RETRIEVAL_INDEX_VERSION",
    "DerivedRetrievalIndex",
    "DerivedRetrievalIndexEntry",
    "DerivedRetrievalIndexMissingError",
    "DerivedRetrievalIndexQuery",
    "DerivedRetrievalIndexResult",
    "DerivedRetrievalIndexStaleError",
    "DerivedRetrievalIndexStore",
    "DerivedRetrievalSearchAccelerator",
]
