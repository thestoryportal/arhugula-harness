"""Durable filesystem-journal store for workflow-layer ``PauseSnapshot``s.

R-CC-1 arc #3 cascade step 2 (`.harness/r-cc-1-arc-3-workflow-durable-resume-design-v1.md`
§7b). The **harness-owned** durable persistence that makes a DURABLE_ASYNC
workflow-layer pause survivable across a process restart — so the caller need
NOT persist the ``PauseSnapshot`` itself (cascade step 1 / #513 surfaced the
public ``api.resume`` with a *caller-supplied* snapshot; this owns the
durability).

**Reused-by-pattern from #475, NOT bound.** This applies the *crash-survivable
journal mechanism* proven + tested in ``JournalEnginePauseResumeSubstrate``
(``journal_pause_resume_substrate.py``) — per-workflow JSONL file, ``fsync`` +
directory-fsync, latest-record semantics, fail-closed-on-corruption — to the
**workflow-layer** ``PauseSnapshot`` (CP spec v1.11 §26.2) rather than the
engine-layer ``PauseEvent``. The engine-layer #475 substrate stays the ratified
CXA-2 bounded-residual (line 181), untouched; this is its workflow-layer sibling
where a *real producer* (the DURABLE_ASYNC HITL / EXPLICIT_OPERATOR pause at
``workflow_driver.py:795/:951``) and a *real caller* (``api.resume``) exist.

**One journal file per workflow.** Each workflow's pauses append to a dedicated
``<journal_dir>/<sha256(workflow_id)>.jsonl`` file (mirrors #475). The last line
of a workflow's file is its authoritative latest pause; per-workflow files
isolate workflows (a corrupt record for one workflow cannot block resuming
another). The resume handle is the ``workflow_id`` (the identifier the caller
always knows after a crash — the fresh-uuid ``run_id`` of a lost ``RunResult``
is not knowable post-crash; design §7b keying decision). The ``run_id`` is
carried *inside* the persisted snapshot for audit continuity, and resume
correctness is preserved by the ``api.resume`` detect-then-refuse guards
(``workflow_id`` match + ``step_index`` range) + the ``snapshot_hash``
validation in ``attempt_resume``. Track-A serial bootstrap-per-call (``_run_lock``)
bounds this to ≤1 active pause per workflow per process.

**Fails closed.** A crash *during* an append can leave a torn trailing line.
``read_latest`` reads the **latest** record only; if that record is malformed
(bad JSON / invalid UTF-8 / a ``PauseSnapshot`` that no longer validates / a
mismatched ``workflow_id``), it returns ``None`` rather than silently resuming an
older (stale) snapshot or raising — the ``api.resume`` caller surfaces this as
``RT-FAIL-RESUME-HANDLE-UNKNOWN``.

**Residence (D2-bis, design §7b).** The journal directory co-locates under the
bootstrap-resolved ``STATE_LEDGER`` directory as a ``pause-journal/`` subdir.
This is harness-internal *recovery substrate* (like #475's engine journal), NOT
one of the four canonical *artifact* classes the ``PathClass`` registry
enumerates (C-IS-01 §1 "Four canonical artifact classes"), so it needs no new
``PathClass`` (IS-AL-1 forecloses inventing a canonical artifact class, not
every internal file). Co-location is restart-deterministic via ``PathResolver``,
glob-safe (nothing globs the ``STATE_LEDGER`` dir; the ledger opens the specific
file ``state.jsonl``), and visibility-coherent (inherits operator-during-run +
maintainer-post-run readability), sitting beside the ``cp.pause-captured``
integrity anchor that already writes there.

**Anchor-validation-deferred (U-CP-22).** A fresh-bootstrap resume has a fresh
ledger; the MVP ``pause_context_reader`` returns the constant sentinel
(``"0"*64``) → no material diff → STRICT admits. Position-only resume is correct
*because* the execution model is data-stateless between steps (design §1.1); the
``state_ledger_anchor`` reachability check stays diff-detection-fidelity-only,
NOT a resume-correctness hole. Real anchor-reachability validation is the
deferred U-CP-22 arc.

Authority: runtime spec v1.46 (R-CC-1 arc #3 cascade step 2); CP spec v1.11
§26.2 (``PauseSnapshot``); design ``r-cc-1-arc-3-workflow-durable-resume-design-v1.md``
§7b. Mechanism mirrors ``JournalEnginePauseResumeSubstrate`` (#475).
"""

from __future__ import annotations

import errno
import hashlib
import json
import os
from enum import StrEnum
from pathlib import Path
from typing import NamedTuple, cast

from harness_cp.pause_resume_protocol_types import PauseSnapshot
from pydantic import ValidationError

__all__ = [
    "PAUSE_JOURNAL_SUBDIR",
    "JournalWorkflowPauseStore",
    "PauseJournalReadCause",
    "PauseJournalReadResult",
    "pause_journal_dir_for",
]


class PauseJournalReadCause(StrEnum):
    """The FIVE distinguishable causes a durable pause-journal read can fail with.

    Runtime spec v1.107 §30 ("Cause attribution on `RT-FAIL-RESUME-HANDLE-UNKNOWN`")
    + §14.14.9.4 — a closed five-member vocabulary of STABLE IDENTIFIERS, carried
    IDENTICALLY by both surfaces (``resume()`` and the §14.14.9 accessor) so the
    operator never receives two names for one state. Never prose: prose is
    unconsumable by a routing decision.

    The vocabulary names the CAUSE CLASS ONLY — never the underlying exception
    text, never a resolved filesystem path (§30 disclosure limit).
    """

    ABSENT = "absent"
    """No journal record exists for this ``workflow_id`` — permanent."""

    EMPTY_JOURNAL = "empty-journal"
    """The per-workflow file EXISTS but holds no record. Permanent for the
    single-process deployment, where it is decisive; INDETERMINATE across
    processes (a concurrent ``capture()`` may complete immediately after this
    read; cross-process append serialization is unresolved, registered at
    ``B-97``). MUST NOT fold into :attr:`ABSENT` despite sharing that routing —
    collapsing on shared routing is the exact defect this refinement undoes, and
    the two carry different operator repairs."""

    READ_ERROR = "read-error"
    """The read raised an **I/O** error. Transient BY DEFAULT — but retryability
    follows the underlying errno, not the class label: the store's read catches
    the whole ``OSError`` family, which includes permanently-failing shapes
    (permission denied, invalid path component, read-only filesystem). See
    :func:`_read_error_is_retryable`."""

    CORRUPT_LATEST = "corrupt-latest"
    """The stored bytes could not be **decoded**, OR the latest record failed to
    **parse** — permanent. A decode failure routes here rather than to
    :attr:`READ_ERROR` deliberately (Runtime spec v1.107 §30's stated divergence
    from the council record's literal mapping): the journal is serialized as JSON
    via ``model_dump(mode="json")``, so an undecodable byte is persistent
    corruption on disk that no number of re-invocations can repair, and a
    transient classification would send the operator loop into an unbounded retry
    with no diagnostic."""

    WORKFLOW_MISMATCH = "workflow-mismatch"
    """The latest record's ``workflow_id`` does not match — permanent."""


#: errnos whose failure is PERMANENT despite arriving as an ``OSError``. Routing
#: every ``read-error`` as blindly retryable would encode futile retries into the
#: contract (Runtime spec v1.107 §30; the errno partition itself is impl
#: discretion, the "do not blanket-route" term is not).
_PERMANENT_READ_ERRNOS = frozenset(
    {
        errno.EACCES,
        errno.EPERM,
        errno.EROFS,
        errno.EISDIR,
        errno.ENOTDIR,
        errno.ENAMETOOLONG,
        errno.EINVAL,
        errno.ELOOP,
    }
)


def _read_error_is_retryable(error: OSError) -> bool:
    """Whether an ``OSError`` from the journal read is worth re-invoking."""
    return error.errno not in _PERMANENT_READ_ERRNOS


class PauseJournalReadResult(NamedTuple):
    """A cause-attributed durable read (Runtime spec v1.107 §30 + §14.14.9.4).

    Carries the change-detector inputs alongside the outcome so the §30 staleness
    token can be minted WITHOUT a second read and WITHOUT any capture-side carrier
    change — the §14.14.8 append-only / never-truncated substrate invariant is what
    makes ``record_count`` a sound change-detector.
    """

    snapshot: PauseSnapshot | None
    """The latest journaled snapshot, or ``None`` on any of the five causes."""

    cause: PauseJournalReadCause | None
    """``None`` iff :attr:`snapshot` is populated."""

    retryable: bool
    """Whether re-invoking could plausibly succeed. ``True`` only for a
    ``read-error`` whose underlying errno is not permanent."""

    record_count: int
    """How many well-formed lines the workflow's journal holds. Monotonically
    non-decreasing for the journal's lifetime per §14.14.8 (append-only, NEVER
    truncated), so two successively observable records always differ here."""

    latest_record_digest: str | None
    """sha256 of the latest RAW journal line, or ``None`` when there is none."""


#: Subdirectory under the resolved ``STATE_LEDGER`` directory that holds the
#: per-workflow pause journals (design §7b D2-bis co-location).
PAUSE_JOURNAL_SUBDIR = "pause-journal"


def pause_journal_dir_for(state_ledger_dir: Path) -> Path:
    """Return the pause-journal directory co-located under the STATE_LEDGER dir.

    The single source of truth for the journal directory location, consumed by
    BOTH the stage-5 factory (which derives ``state_ledger_dir`` from
    ``ctx.ledger_writer.handle.canonical_path.parent``) and ``api.resume`` (which
    resolves it from ``config`` via ``PathResolver``) — both compute the same
    ``<state_ledger_dir>/pause-journal`` path for the same
    ``(workflow_class, deployment_surface)``, so a capture-side write and a
    resume-side read over a fresh bootstrap find the same file (restart-survival).
    """
    return state_ledger_dir / PAUSE_JOURNAL_SUBDIR


class JournalWorkflowPauseStore:
    """Durable per-workflow ``PauseSnapshot`` journal (workflow-layer F2/JOURNAL).

    ``capture`` appends the captured ``PauseSnapshot`` as one JSON line to the
    workflow's ``<journal_dir>/<sha256(workflow_id)>.jsonl`` file (durably,
    ``fsync``-ed); ``read_latest`` reads that file's **latest** line and
    re-validates it into a ``PauseSnapshot``. Because the journal is on disk, a
    fresh store over the same directory (a new process after a restart) resumes a
    pause captured by a prior process.
    """

    def __init__(self, *, journal_dir: Path) -> None:
        self._journal_dir = Path(journal_dir)

    def capture(self, snapshot: PauseSnapshot) -> None:
        """Append one ``PauseSnapshot`` record to the workflow's file, durably."""
        self._append(snapshot)

    def read_latest(self, workflow_id: str) -> PauseSnapshot | None:
        """Return the workflow's latest journaled ``PauseSnapshot``, or ``None``.

        ``None`` when the workflow has no journal file OR its latest record is
        unparseable (fail closed). Only the last record is consulted: a torn
        latest append must NOT silently resume an older snapshot.

        Behaviour is PRESERVED VERBATIM at the ``B-69`` impl leg — this is now a
        projection of :meth:`read_latest_attributed`, which distinguishes the five
        causes the flat ``None`` collapses.
        """
        return self.read_latest_attributed(workflow_id).snapshot

    def read_latest_attributed(self, workflow_id: str) -> PauseJournalReadResult:
        """Read the latest record, attributing any failure to one of FIVE causes.

        Runtime spec v1.107 §30 + §14.14.9.4. The fail-closed disposition is
        UNCHANGED — the read stays **latest-record-only** and NEVER walks backwards
        to an older well-formed record (§14.14.8: everything is kept so a
        change-detector can be derived over the journal's growth; nothing older is
        ever resumed from).
        """
        path = self._journal_file(workflow_id)
        if not path.exists():
            return PauseJournalReadResult(
                snapshot=None,
                cause=PauseJournalReadCause.ABSENT,
                retryable=False,
                record_count=0,
                latest_record_digest=None,
            )
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # An undecodable byte is persistent on-disk corruption, NOT an I/O
            # blip: routing it transient would send the operator loop into an
            # unbounded retry with no diagnostic (spec v1.107 §30's stated
            # divergence from the council record's literal mapping).
            return PauseJournalReadResult(
                snapshot=None,
                cause=PauseJournalReadCause.CORRUPT_LATEST,
                retryable=False,
                record_count=0,
                latest_record_digest=None,
            )
        except OSError as exc:
            return PauseJournalReadResult(
                snapshot=None,
                cause=PauseJournalReadCause.READ_ERROR,
                retryable=_read_error_is_retryable(exc),
                record_count=0,
                latest_record_digest=None,
            )
        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            return PauseJournalReadResult(
                snapshot=None,
                cause=PauseJournalReadCause.EMPTY_JOURNAL,
                retryable=False,
                record_count=0,
                latest_record_digest=None,
            )
        latest = lines[-1]
        digest = hashlib.sha256(latest.encode("utf-8")).hexdigest()
        snapshot, cause = self._parse_snapshot_attributed(latest, workflow_id)
        return PauseJournalReadResult(
            snapshot=snapshot,
            cause=cause,
            retryable=False,
            record_count=len(lines),
            latest_record_digest=digest,
        )

    # -- durable journal I/O ------------------------------------------------

    def _journal_file(self, workflow_id: str) -> Path:
        """The per-workflow journal file (filesystem-safe, collision-free name)."""
        digest = hashlib.sha256(workflow_id.encode("utf-8")).hexdigest()
        return self._journal_dir / f"{digest}.jsonl"

    def _append(self, snapshot: PauseSnapshot) -> None:
        """Append one JSONL record to the workflow's file, durably.

        The record is ``fsync``-ed to stable storage before returning so a host
        crash / power loss immediately after ``capture`` cannot lose an
        already-accepted pause. Two directory-fsyncs persist the new dirents
        (best-effort — POSIX) so the journal survives a first-capture crash:
        when the journal *file* is created, its directory entry is fsync-ed; and
        when the ``pause-journal`` *directory* itself is created (the very first
        durable pause), its parent (the ``STATE_LEDGER`` dir) is also fsync-ed —
        otherwise fsyncing only the new child dir persists the file entry inside
        it but NOT the child dir's own entry in its parent, so a crash could lose
        the entire ``pause-journal`` directory (→ a spurious
        ``RT-FAIL-RESUME-HANDLE-UNKNOWN`` despite the durability guarantee).

        **Torn-append self-healing.** A crash *during* a prior append can leave a
        partial trailing line with no terminating newline. To prevent the next
        append from concatenating onto that fragment (which would make the latest
        line `fragment+record` → unparseable → ``read_latest`` returns ``None``
        *permanently* until manual repair), a leading newline is written first
        when the existing file is non-empty and does not already end with ``\\n``.
        The torn fragment then becomes its own (ignored, non-latest) line and the
        new record is the clean latest line.

        Both durability hardenings caught by out-of-family Codex review
        (R-CC-1 arc #3 cascade step 2).
        """
        record = {
            "workflow_id": snapshot.workflow_id,
            "pause_snapshot": snapshot.model_dump(mode="json"),
        }
        line = json.dumps(record, sort_keys=True)
        path = self._journal_file(snapshot.workflow_id)
        journal_dir = path.parent
        dir_is_new = not journal_dir.exists()
        journal_dir.mkdir(parents=True, exist_ok=True)
        is_new_file = not path.exists()
        needs_leading_newline = (not is_new_file) and self._last_byte_is_not_newline(path)
        with path.open("a", encoding="utf-8") as handle:
            if needs_leading_newline:
                handle.write("\n")
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        if is_new_file:
            self._fsync_dir(journal_dir)
        if dir_is_new:
            # Durably link the freshly-created `pause-journal` dirent into its
            # parent (the STATE_LEDGER dir), else a crash could lose the dir.
            self._fsync_dir(journal_dir.parent)

    @staticmethod
    def _last_byte_is_not_newline(path: Path) -> bool:
        """Return ``True`` iff the file's last byte is not ``\\n`` (a torn trailing
        append). Reads only the final byte; on any read error, conservatively
        returns ``True`` so the next append is newline-separated rather than
        risking a concatenation onto a fragment."""
        try:
            with path.open("rb") as handle:
                handle.seek(-1, os.SEEK_END)
                return handle.read(1) != b"\n"
        except OSError:
            return True

    @staticmethod
    def _fsync_dir(directory: Path) -> None:
        """fsync a directory so a freshly-created file's dirent is durable.

        Best-effort: directory fsync is unsupported on some platforms/filesystems
        (e.g. Windows), where it is a no-op rather than a failure.
        """
        try:
            dir_fd = os.open(directory, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(dir_fd)
        except OSError:
            pass
        finally:
            os.close(dir_fd)

    @staticmethod
    def _parse_snapshot(line: str, expected_workflow_id: str) -> PauseSnapshot | None:
        """Parse one journal line into a ``PauseSnapshot``, or ``None`` if corrupt.

        Guards against the record belonging to an unexpected workflow as a
        defensive integrity check (per-workflow files make this near-impossible,
        but a mismatched record is treated as corruption — fail closed).
        """
        return JournalWorkflowPauseStore._parse_snapshot_attributed(line, expected_workflow_id)[0]

    @staticmethod
    def _parse_snapshot_attributed(
        line: str, expected_workflow_id: str
    ) -> tuple[PauseSnapshot | None, PauseJournalReadCause | None]:
        """Parse one journal line, splitting the flat ``None`` into its two causes.

        A record belonging to a DIFFERENT workflow is ``workflow-mismatch``, not
        ``corrupt-latest``: the two share the permanent routing but carry different
        operator repairs (the handle names a different workflow vs. the record we
        would resume from is unusable).
        """
        try:
            loaded = json.loads(line)
            if not isinstance(loaded, dict):
                return None, PauseJournalReadCause.CORRUPT_LATEST
            record = cast("dict[str, object]", loaded)
            if record.get("workflow_id") != expected_workflow_id:
                return None, PauseJournalReadCause.WORKFLOW_MISMATCH
            return PauseSnapshot.model_validate(record["pause_snapshot"]), None
        except (ValueError, ValidationError, KeyError, TypeError):
            # ValueError covers json.JSONDecodeError; any value-level failure
            # means a corrupt record → fail closed.
            return None, PauseJournalReadCause.CORRUPT_LATEST
