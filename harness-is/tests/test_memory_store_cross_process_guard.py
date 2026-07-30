"""U-MEM-27 Codex round-1 [P1] - the guarded write's CROSS-PROCESS face.

`write_record_guarded` originally held only `threading.RLock`s, so its
compare-and-commit excluded concurrent writers in ONE process and made no
cross-process claim. That scope is not sufficient here: the canonical memory
root is repo-derived and stable (`<repository_root>/.harness/memory`,
`harness_runtime.automatic_memory`), so two ordinary same-host invocations - a
one-shot `harness run` alongside a `harness daemon` - already share it. A second
OS process could therefore append a superseded provenance line between the
precondition read and the write it authorizes, which is exactly the interleaving
the plan's commit-binding obligation forbids.

The witness below is deliberately NOT thread-based: every thread in this process
contends on the same `_DirLock` in-process face, so a thread pair would pass on
the `RLock`s alone. A genuine second OS process has fresh locks and fresh fds -
only the `flock` can exclude it. Forked BEFORE any lock is acquired (fork AFTER
acquiring duplicates locked state into the child - the documented workspace
hazard, and the same rule `test_cross_process_ledger_lock` follows).
"""

from __future__ import annotations

import json
import multiprocessing
import sys
import threading
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path

import pytest
from harness_core import DeploymentSurface
from harness_is.memory_path_registry import MemoryRootBinding
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
from harness_is.memory_store import CanonicalMemoryStore, MemoryStoreRecord

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="POSIX flock semantics (B-45 posture)"
)

_NOW = datetime(2026, 7, 29, 16, 0, 0, tzinfo=UTC)
_RUN_ID = "run-u-mem-27-cross-process"
_WAIT = 10.0


def _store(root: Path) -> CanonicalMemoryStore:
    return CanonicalMemoryStore(
        root_binding=MemoryRootBinding(default_root=root),
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )


def _scope() -> MemoryScope:
    return MemoryScope(project="arhugula-v2", visibility=MemoryVisibility.PROJECT)


def _source_record(provenance: CapturedCrossFamily) -> MemoryStoreRecord:
    """A JSONL-backed EPISODIC_TURN source - the determination-bearing shape.

    The envelope is hash-inert, so the two provenance values below yield the
    SAME `content_hash` and therefore the SAME `memory_id`: the second write
    appends a colliding line that a reader resolves last-wins. That collision is
    the whole reason the commit must be bound to the version the snapshot read.
    """

    content: Mapping[str, object] = {
        "run_id": _RUN_ID,
        "turn_id": "turn-1",
        "step_id": "step-1",
        "prompt_summary": "the cited source turn",
        "response_summary": "the cited source turn",
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
            source_refs=(SourceRef(ref_type=SourceRefType.OPERATOR, ref="operator:source"),),
            scope=_scope(),
            content_hash=content_hash,
            captured_cross_family=provenance,
        ),
        content=content,
    )


def _target_record() -> MemoryStoreRecord:
    """The JSON-backed activation the guarded section commits."""

    content: Mapping[str, object] = {
        "semantic_kind": "fact",
        "statement": "the activation under the guarded write",
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
            source_refs=(SourceRef(ref_type=SourceRefType.OPERATOR, ref="operator:target"),),
            scope=_scope(),
            content_hash=content_hash,
            captured_cross_family=CapturedCrossFamily.FALSE,
        ),
        content=content,
    )


def _committed_memory_ids(root: Path) -> list[str]:
    """The store's own total commit order.

    Every `write_record` appends a stale marker to the rebuildable semantic
    index INSIDE the same section it writes the record in, so this ledger orders
    committed writes across processes without any test-side instrumentation.
    """

    index = root / "semantic" / "index.jsonl"
    return [
        str(json.loads(line)["memory_id"])
        for line in index.read_text().splitlines()
        if line.strip()
    ]


def _mp_guarded_writer_worker(
    root: Path,
    in_precondition: object,
    release: object,
) -> None:
    """Module-level (picklable) worker: a GENUINE second OS process holding a
    guarded section open across its precondition evaluation."""

    store = _store(root)

    def _precondition() -> bool:
        in_precondition.set()  # type: ignore[attr-defined]
        release.wait(timeout=_WAIT)  # type: ignore[attr-defined]
        return True

    store.write_record_guarded(_target_record(), precondition=_precondition)


def test_a_second_process_cannot_append_between_precondition_and_commit(
    tmp_path: Path,
) -> None:
    """THE [P1] witness: an ordinary `write_record` in a second OS process must
    not land inside another process's guarded section.

    Codex reproduced the open race as `precondition_saw=false`,
    `source_at_commit=true`, `activation_committed=True` - the activation
    committed against provenance that had already been superseded. Under the
    per-root scope lock the interleaving is excluded outright: the appending
    process BLOCKS for the guarded section's duration, and the store's own
    commit order shows the activation strictly before the superseding append.
    """

    root = tmp_path / "memory"
    parent_store = _store(root)
    source_v1 = _source_record(CapturedCrossFamily.FALSE)
    parent_store.write_record(source_v1)  # completes BEFORE the fork

    ctx = multiprocessing.get_context("fork")
    in_precondition = ctx.Event()
    release = ctx.Event()
    child = ctx.Process(
        target=_mp_guarded_writer_worker,
        args=(root, in_precondition, release),
    )
    child.start()
    try:
        assert in_precondition.wait(timeout=_WAIT), "child never entered its precondition"
        append_done = threading.Event()

        def _superseding_append() -> None:
            # Same `memory_id`, different `captured_cross_family` - the
            # colliding, last-wins line that supersedes what the child read.
            parent_store.write_record(_source_record(CapturedCrossFamily.TRUE))
            append_done.set()

        appender = threading.Thread(target=_superseding_append)
        appender.start()
        assert not append_done.wait(0.5), (
            "a second process appended superseding provenance INSIDE the guarded "
            "section - the guard is in-process only"
        )
        release.set()
        appender.join(_WAIT)
        child.join(_WAIT)
        assert append_done.is_set()
        assert child.exitcode == 0
    finally:
        release.set()
        child.join(5)
        if child.is_alive():  # pragma: no cover - cleanup path
            child.terminate()

    source_id = str(source_v1.envelope.memory_id)
    target_id = str(_target_record().envelope.memory_id)
    assert _committed_memory_ids(root) == [source_id, target_id, source_id], (
        "the activation did not commit strictly before the superseding append"
    )
