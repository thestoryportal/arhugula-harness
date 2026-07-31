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
import sys
from collections.abc import Generator
from contextlib import contextmanager
from enum import StrEnum
from pathlib import Path
from typing import NamedTuple, cast

from harness_cp.pause_resume_protocol_types import PauseSnapshot
from pydantic import ValidationError

__all__ = [
    "PAUSE_JOURNAL_LOCK_SUFFIX",
    "PAUSE_JOURNAL_SUBDIR",
    "JournalWorkflowPauseStore",
    "PauseJournalReadCause",
    "PauseJournalReadResult",
    "pause_journal_dir_for",
]

_IS_WINDOWS = sys.platform == "win32"


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
    read). That indeterminacy is UNCHANGED by ``B-97`` half (b): serializing
    concurrent APPENDS against each other says nothing about a capture that
    lands after a read has already returned, and the read deliberately takes no
    lock (see :meth:`JournalWorkflowPauseStore.read_latest_attributed`).
    MUST NOT fold into :attr:`ABSENT` despite sharing that routing —
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

    indeterminate: bool
    """Whether this outcome is NOT decisive loss.

    Spec v1.107 §30 is explicit for ``empty-journal``: it is permanent *for the
    single-process deployment, where it is decisive*, but **INDETERMINATE across
    processes** — a concurrent ``capture()`` may complete immediately after this
    read — and
    *"an implementation MUST NOT present it as decisive loss where a second writer
    is reachable."* Reporting a bare ``retryable=False`` did exactly that, so the
    indeterminacy is carried as its own fact rather than collapsed into the retry
    flag. *(Out-of-family review [P2], round 3.)*
    """

    record_count: int
    """How many well-formed lines the workflow's journal holds. Monotonically
    non-decreasing for the journal's lifetime per §14.14.8 (append-only, NEVER
    truncated), so two successively observable records always differ here."""

    latest_record_digest: str | None
    """sha256 of the latest RAW journal line, or ``None`` when there is none."""


#: Subdirectory under the resolved ``STATE_LEDGER`` directory that holds the
#: per-workflow pause journals (design §7b D2-bis co-location).
PAUSE_JOURNAL_SUBDIR = "pause-journal"

PAUSE_JOURNAL_LOCK_SUFFIX = ".lock"
"""Suffix of a workflow journal's dedicated cross-process advisory-lock file
(``<sha256(workflow_id)>.jsonl.lock``), one per workflow, beside the journal
it guards (``B-97`` half (b)).

A DEDICATED file rather than the journal itself: `flock` rides the inode, and
locking the journal would couple the lock's lifetime to any future operation
that replaces that inode. It is a LOCK file, never a canonical one — it carries
no bytes and nothing reads it. Reads open one sha256-named path directly and
nothing globs this directory, so the extra sibling is inert.
"""


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

        **This read deliberately does NOT acquire `_append`'s cross-process write
        lock (`B-97` half (b)).** Taking it would make an empty-journal read
        mutually exclusive with a concurrent ``capture()``, and that is precisely
        the property Runtime spec v1.107 §30 declines to promise: the spec calls
        ``empty-journal`` *"INDETERMINATE across processes"* because *"a concurrent
        `capture()` may complete immediately after this read"* — an
        after-the-read completion no write lock can exclude, since the read has
        already returned. Locking here would therefore buy no additional
        determinism while making :attr:`PauseJournalReadResult.indeterminate`'s
        ``True`` on that cause read as over-conservative rather than exact. Keeping
        the read unlocked is what holds the shipped §30 attribution correct AS
        WRITTEN and is why serializing the write path owed zero spec text.
        """
        path = self._journal_file(workflow_id)
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return PauseJournalReadResult(
                snapshot=None,
                cause=PauseJournalReadCause.ABSENT,
                retryable=False,
                indeterminate=False,
                record_count=0,
                latest_record_digest=None,
            )
        except IsADirectoryError:
            # Not "no record" — the path is occupied by something unusable.
            return PauseJournalReadResult(
                snapshot=None,
                cause=PauseJournalReadCause.READ_ERROR,
                retryable=False,
                indeterminate=False,
                record_count=0,
                latest_record_digest=None,
            )
        except UnicodeDecodeError:
            # An undecodable byte is persistent on-disk corruption, NOT an I/O
            # blip: routing it transient would send the operator loop into an
            # unbounded retry with no diagnostic (spec v1.107 §30's stated
            # divergence from the council record's literal mapping).
            return PauseJournalReadResult(
                snapshot=None,
                cause=PauseJournalReadCause.CORRUPT_LATEST,
                retryable=False,
                indeterminate=False,
                record_count=0,
                latest_record_digest=None,
            )
        except OSError as exc:
            return PauseJournalReadResult(
                snapshot=None,
                cause=PauseJournalReadCause.READ_ERROR,
                retryable=_read_error_is_retryable(exc),
                indeterminate=False,
                record_count=0,
                latest_record_digest=None,
            )
        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            return PauseJournalReadResult(
                snapshot=None,
                cause=PauseJournalReadCause.EMPTY_JOURNAL,
                retryable=False,
                indeterminate=True,
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
            indeterminate=False,
            record_count=len(lines),
            latest_record_digest=digest,
        )

    # -- durable journal I/O ------------------------------------------------

    def _journal_file(self, workflow_id: str) -> Path:
        """The per-workflow journal file (filesystem-safe, collision-free name)."""
        digest = hashlib.sha256(workflow_id.encode("utf-8")).hexdigest()
        return self._journal_dir / f"{digest}.jsonl"

    @contextmanager
    def _cross_process_append_lock(self, journal_path: Path) -> Generator[None, None, None]:
        """Hold an exclusive same-host lock over ONE workflow's append section.

        ``B-97`` half (b). A hand-rolled ``fcntl.flock`` on a dedicated
        ``<journal>.lock`` file, mirroring the primitive already shipped at
        ``protected_result_store._cross_process_lock`` — a fresh fd opened and
        closed per call, no process-wide registry: ``flock`` coordinates through
        the kernel via the on-disk inode, and the lock is released on process
        death.

        **PER-WORKFLOW, not per-directory — the grounded choice.** The house
        ``harness_is.cross_process_ledger_lock.cross_process_scope_lock`` was the
        obvious candidate (one exclusive lock per directory TREE, already imported
        across this axis) and was tried first. Out-of-family review found it does
        NOT fit cleanly here: a directory-wide lock makes one workflow's append
        wait behind ANOTHER workflow's, which (i) contradicts this store's own
        stated isolation property — per-workflow files exist precisely so one
        workflow cannot block another — and (ii) has an externally visible cost,
        because the read path is deliberately unlocked: while workflow B's first
        capture queues behind workflow A's append, a read of B reports the
        ``absent`` cause, which Runtime spec v1.107 §30 attributes as PERMANENT.
        A per-workflow lock leaves that pre-existing capture-not-yet-landed race
        exactly the size it already was; a directory-wide one would have widened
        it to the whole contended hold. *(The residual spec-side asymmetry — §30
        qualifies only ``empty-journal`` as cross-process INDETERMINATE, though
        ``absent`` and ``corrupt-latest`` are reachable the same way — is a
        contract question an impl leg must not settle, and is registered at
        ``B-102``.)*

        No-op on Windows (``_IS_WINDOWS``) — no ``fcntl`` there; same posture as
        pre-``B-97``, matching ``harness_is.cross_process_ledger_lock``'s own
        carve-out (the ``B-45`` register row). ``fcntl`` is imported lazily inside
        this method, NEVER at module scope: an unguarded top-level import would
        break ``import harness_runtime`` outright on Windows.

        **KNOWN + REGISTERED, deliberately not built here: this ``flock`` blocks
        the event loop.** ``capture()`` is called synchronously from the async
        ``DurablePauseResumeProtocol.capture_pause_snapshot``, so a contended
        acquisition stalls the loop for the holder's critical section (one write
        plus two directory fsyncs — bounded by that section, not unbounded, but
        still on-loop). The sibling durable store hit exactly this and grew an
        off-loop path (``resolve_result_ref_off_loop``), so the shape is
        precedented; adopting it here is a scoping decision for the ``B-97``
        half-(a) leg or a follow-on, recorded on the ``B-97`` register row rather
        than absorbed silently into a serialization arc. Re-raised by every
        transcript-less reviewer — it is a DEFERRAL, not an oversight.
        """
        if _IS_WINDOWS:
            yield
            return
        import fcntl  # POSIX-only; never reached on Windows.

        lock_path = journal_path.with_name(journal_path.name + PAUSE_JOURNAL_LOCK_SUFFIX)
        # O_NOFOLLOW: a symlink planted at the lock path — including a dangling
        # one, which O_CREAT would otherwise materialize at its target — fails
        # loud with ELOOP rather than silently locking (or creating) elsewhere.
        flags = os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        fd = os.open(lock_path, flags, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)

    def _append(self, snapshot: PauseSnapshot) -> None:
        """Append one JSONL record to the workflow's file, durably.

        The record is ``fsync``-ed to stable storage before returning so a host
        crash / power loss immediately after ``capture`` cannot lose an
        already-accepted pause. Two directory-fsyncs persist the dirents
        (best-effort — POSIX): the ``pause-journal`` directory's own entry in its
        parent (the ``STATE_LEDGER`` dir), and this workflow's journal-file entry
        inside ``pause-journal``. Both are needed — fsyncing only the child dir
        persists the file entry inside it but NOT the child dir's own entry in
        its parent, so a crash could lose the entire ``pause-journal`` directory
        (→ a spurious ``RT-FAIL-RESUME-HANDLE-UNKNOWN`` despite the durability
        guarantee).

        **Both directory fsyncs are UNCONDITIONAL, and that is load-bearing.**
        Every flag-gated form of them is unsound, because the flags are
        process-local and the crash they guard against is another process's:

        - Gating the parent fsync on ``dir_is_new`` (this call created the
          directory) loses it whenever a writer created the directory and died
          before fsyncing — the dirent is then present but NOT durable, every
          later writer samples ``dir_is_new=False``, and the fsync is skipped
          FOREVER.
        - Gating it on ``is_new_file or dir_is_new`` narrows that window but does
          NOT close it (out-of-family review, this arc): a writer whose
          ``path.open("a")`` creates the journal file and which then dies before
          reaching the fsync leaves BOTH flags False for every successor. "A
          journal file exists ⇒ some earlier writer already fsynced" is simply
          false for that interleaving.
        - Gating the child fsync on ``is_new_file`` has the identical shape one
          level down: create the file, write, die before the fsync, and no
          successor ever links the dirent durably. This one is PRE-EXISTING —
          byte-identical to the pre-``B-97`` code — and is closed here rather
          than left as a known twin of the defect being fixed beside it.

        Unconditional fsyncs make the invariant true BY CONSTRUCTION with no
        interleaving exception: the parent is fsynced before any statement that
        could create a journal file, and the child is fsynced after every append.
        The cost is two best-effort directory fsyncs on a path that already
        ``fsync``s the record itself, for an event (a durable pause capture) that
        occurs at human latency — and it deletes both flags rather than adding a
        third.

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

        **Cross-process write serialization (B-97 half (b)).** Everything from
        the existence probes through the final directory fsyncs runs under
        :meth:`_cross_process_append_lock`, an exclusive same-host advisory lock
        on THIS workflow's journal. Without it two OS processes sharing one
        resolved ``STATE_LEDGER`` dir were serialized by NOTHING: the plain
        append-mode ``open`` carries no ``O_EXCL``, no lockfile and no advisory
        lock. The three-way TOCTOU — ``is_new_file``, ``needs_leading_newline``
        and the append itself were each computed or performed against a file
        another process could mutate in between — is closed by that hold, which
        is also what makes the torn-append self-heal above sound: it was
        single-writer-only reasoning before.

        The lock is a LEAF (nothing inside the hold acquires another
        cross-process lock), so it cannot participate in a lock-ordering cycle
        with the IS ledger locks that guard the enclosing ``STATE_LEDGER``
        directory, whatever order a caller composes them in.

        ``is_new_file`` survives ONLY as the guard on ``needs_leading_newline``
        (a brand-new file must not receive a spurious leading newline, since
        :meth:`_last_byte_is_not_newline` reports ``True`` for an absent file).
        It carries no durability meaning any more — see above.

        Windows: the lock degrades to a documented no-op there (no ``fcntl``;
        C-STK-10 / the ``B-45`` register row), so Windows sits at exact pre-B-97
        parity rather than gaining a partial guarantee.

        **The read path deliberately does NOT take this lock** — see
        :meth:`read_latest_attributed`.
        """
        record = {
            "workflow_id": snapshot.workflow_id,
            "pause_snapshot": snapshot.model_dump(mode="json"),
        }
        line = json.dumps(record, sort_keys=True)
        path = self._journal_file(snapshot.workflow_id)
        journal_dir = path.parent
        journal_dir.mkdir(parents=True, exist_ok=True)
        # UNCONDITIONAL, and BEFORE the lock — so it precedes any statement that
        # could create a journal file. See the docstring's durability section:
        # both directory fsyncs are unconditional precisely because every
        # flag-gated form leaves a crash window that a later writer then skips
        # FOREVER.
        self._fsync_dir(journal_dir.parent)
        with self._cross_process_append_lock(path):
            is_new_file = not path.exists()
            needs_leading_newline = (not is_new_file) and self._last_byte_is_not_newline(path)
            with path.open("a", encoding="utf-8") as handle:
                if needs_leading_newline:
                    handle.write("\n")
                handle.write(line + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            # UNCONDITIONAL, and AFTER the file exists — durably links this
            # workflow's journal dirent into `pause-journal`.
            self._fsync_dir(journal_dir)

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
            snapshot = PauseSnapshot.model_validate(record["pause_snapshot"])
            if snapshot.workflow_id != expected_workflow_id:
                # The JSONL WRAPPER matched but the EMBEDDED snapshot names a
                # different workflow. Attributing this here — rather than letting a
                # successful read flow on to `resume()`'s own
                # `ResumeWorkflowMismatchError` — is what keeps §30's promise that
                # BOTH surfaces report the SAME five stable identifiers: otherwise
                # the accessor would say `workflow-mismatch` while `resume()` raised
                # a differently-named class for the identical state.
                return None, PauseJournalReadCause.WORKFLOW_MISMATCH
            return snapshot, None
        except (ValueError, ValidationError, KeyError, TypeError):
            # ValueError covers json.JSONDecodeError; any value-level failure
            # means a corrupt record → fail closed.
            return None, PauseJournalReadCause.CORRUPT_LATEST
