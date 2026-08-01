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

**One journal file per (TENANT, WORKFLOW) pair.** Each pair's pauses append to a
dedicated ``<journal_dir>/<sha256(encode(tenant_scope, workflow_id))>.jsonl``
file. The last line of a pair's file is its authoritative latest pause;
per-pair files isolate workflows (a corrupt record for one cannot block
resuming another) AND isolate tenants sharing one resolved journal directory
(Runtime spec v1.108 §14.14.8, the RATIFIED ``B-97`` half (a) arc — keying
AMENDED from ``workflow_id`` alone to the tenant-composite tuple, realized as
per-tenant PATH SEGREGATION; see :func:`encode_pause_journal_key`). The resume
handle is STILL the ``workflow_id`` alone and the caller-facing input triple is
BYTE-UNCHANGED — the tenant scope has always lived inside ``RuntimeConfig``,
which both construction sites already hold (the identifier the caller always
knows after a crash — the fresh-uuid ``run_id`` of a lost ``RunResult``
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

from harness_runtime.lifecycle.protected_result_store import normalize_tenant_scope

__all__ = [
    "PAUSE_JOURNAL_FILENAME_SUFFIX",
    "PAUSE_JOURNAL_LOCK_SUFFIX",
    "PAUSE_JOURNAL_SUBDIR",
    "JournalWorkflowPauseStore",
    "PauseJournalReadCause",
    "PauseJournalReadResult",
    "cross_process_journal_lock",
    "encode_pause_journal_key",
    "journal_exclusion_is_degraded",
    "legacy_pause_journal_filename",
    "pause_journal_dir_for",
    "pause_journal_filename",
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
    """No journal record exists for this **TENANT-COMPOSITE KEY** — the
    ``(normalized_tenant_scope, workflow_id)`` pair of §14.14.8, not the
    ``workflow_id`` alone (Runtime spec v1.108 §30; a DEFINITION amendment, no
    new cause member — the vocabulary stays CLOSED at five).

    Permanent for the SINGLE-PROCESS deployment, where it is decisive;
    INDETERMINATE across processes (`B-102`) — a ``capture()`` dispatched but not
    yet having created its journal file reports ``absent``, and that capture may
    complete immediately after this read.

    **THREE DISTINCT UNDERLYING STATES share this cause, and they are
    deliberately NOT DISTINGUISHABLE at this surface**: (1) this workflow never
    journaled a pause under this tenant scope; (2) a WRONG-TENANT lookup — the
    record may exist under a different ``config.tenant_id``, and the lookup
    resolved the caller's OWN path and truthfully found nothing there; (3) an
    ABANDONED LEGACY pre-v1.108 untenanted journal. Adding a discriminator here
    would be exactly the EXISTENCE ORACLE path segregation removes — every tenant
    probes the same legacy path, so a distinct signal would disclose an
    untenanted record for a GUESSED ``workflow_id``. Learning which state obtains
    is the operator-only §13.7 enumeration surface's job."""

    EMPTY_JOURNAL = "empty-journal"
    """The per-workflow file EXISTS but holds no record. Permanent for the
    single-process deployment, where it is decisive; INDETERMINATE across
    processes (a concurrent ``capture()`` may complete immediately after this
    read). That indeterminacy is UNCHANGED by ``B-97`` half (b): serializing
    concurrent APPENDS against each other says nothing about a capture that
    lands after a read has already returned, and the read deliberately takes no
    lock (see :meth:`JournalWorkflowPauseStore.read_latest_attributed`).
    *(`B-102`, v1.108: :attr:`ABSENT` and :attr:`CORRUPT_LATEST`'s parse branch
    now carry this same qualification — the residual asymmetry the `B-97`(b) arc
    registered is closed.)*
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
    with no diagnostic.

    **The `B-102` indeterminacy reaches the PARSE-failure branch ONLY, never the
    DECODE-failure branch** (Runtime spec v1.108 §30). PARSE failure: the latest
    line is present but unparseable — a torn trailing line is exactly what an
    in-flight append looks like from a reader, so this is INDETERMINATE across
    processes. DECODE failure: the stored bytes are not decodable at all —
    UNCONDITIONALLY PERMANENT, since the invalid bytes persist on disk, an append
    leaves them in place, and every re-read fails identically."""

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

    Spec v1.107 §30 was explicit for ``empty-journal``: it is permanent *for the
    single-process deployment, where it is decisive*, but **INDETERMINATE across
    processes** — a concurrent ``capture()`` may complete immediately after this
    read — and
    *"an implementation MUST NOT present it as decisive loss where a second writer
    is reachable."* Reporting a bare ``retryable=False`` did exactly that, so the
    indeterminacy is carried as its own fact rather than collapsed into the retry
    flag. *(Out-of-family review [P2], round 3.)*

    **AMENDED at v1.108 — `B-102`'s impl half. ALL THREE permanent-absence causes
    now carry the qualification, rather than one of three:** ``empty-journal``
    (unchanged), ``absent`` (a capture dispatched but not yet having created its
    file), and ``corrupt-latest``'s **PARSE-failure branch** (a torn tail is what
    an in-flight append looks like from a reader). ``corrupt-latest``'s
    **DECODE-failure branch** stays UNCONDITIONALLY PERMANENT, and so do
    ``read-error`` and ``workflow-mismatch``.
    """

    record_count: int
    """How many **NON-BLANK RAW LINES** the journal holds — counted WITHOUT
    parsing any record, which is what lets the §13.7 enumeration surface report
    the SAME number for a journal that this store does (Runtime spec v1.108
    §13.7 term 3; a *"well-formed lines"* count would require parsing, which
    §13.7 term 4 forbids, and the two surfaces would disagree on a torn journal).
    Monotonically non-decreasing for the journal's lifetime per §14.14.8
    (append-only, NEVER truncated), so two successively observable records always
    differ here."""

    latest_record_digest: str | None
    """sha256 of the latest RAW journal line, or ``None`` when there is none."""


#: Subdirectory under the resolved ``STATE_LEDGER`` directory that holds the
#: per-workflow pause journals (design §7b D2-bis co-location).
PAUSE_JOURNAL_SUBDIR = "pause-journal"

PAUSE_JOURNAL_FILENAME_SUFFIX = ".jsonl"
"""Suffix of a canonical per-`(tenant, workflow)` journal file. The canonical
journal name shape is ``<64 lowercase hex>.jsonl`` and NOTHING else — the
§13.7 enumeration filter is defined against exactly this (Runtime spec v1.108
§13.7 term 1)."""

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


# ---------------------------------------------------------------------------
# The tenant-composite key encoding (Runtime spec v1.108 §14.14.8).
# ---------------------------------------------------------------------------

#: Byte joined BETWEEN length-prefixed segments. Part of the PINNED grammar.
_KEY_SEGMENT_JOINER = b"|"

#: Byte separating a segment's decimal-ASCII BYTE-length prefix from its bytes.
_KEY_LENGTH_SEPARATOR = b":"

#: The error handler is PART OF THE GRAMMAR, not an implementation detail
#: (Runtime spec v1.108 §14.14.8). `RuntimeConfig.tenant_id` and `workflow_id`
#: are plain `str` fields that accept a LONE SURROGATE, which STRICT UTF-8
#: encoding REFUSES — a strict encoder would make this encoding PARTIAL over
#: its own declared domain and turn a config-valid deployment's capture into a
#: crash. `surrogatepass` keeps it TOTAL over the full `(str | None) × str`
#: domain without narrowing a public input contract, which this arc may not do.
_KEY_ENCODING_ERRORS = "surrogatepass"


def encode_pause_journal_key(tenant_scope: str | None, workflow_id: str) -> bytes:
    """The TOTAL, INJECTIVE canonical encoding of `(tenant_scope, workflow_id)`.

    Runtime spec v1.108 §14.14.8, *"THE ENCODING IS A CONTRACT TERM, TOTAL AND
    INJECTIVE"*. The sha256 preimage of a journal filename. **The grammar is
    PINNED by the spec and is NOT implementation discretion:**

    - each segment is encoded UTF-8 **with the ``surrogatepass`` error handler**;
    - each segment is prefixed with its resulting **BYTE** length in decimal
      ASCII followed by ``:`` (the byte-count variant of the in-house
      length-prefixed canonical-segment shape — the codebase ships BOTH a
      character-count form at ``cost_attribution_f2_write`` and a byte-count
      form at ``harness_od.audit_cutover_record``, and they emit different
      bytes for any non-ASCII identifier, so the spec pins the byte-count one);
    - segments are joined with ``|``;
    - the **untenanted branch is the ONE-segment form** and a real tenant scope
      the **TWO-segment form**.

    **THE DERIVATION IS A CONSTANT — there is NO configuration surface, and none
    may be added.** A configurable key derivation would be a second authority
    over one durable address space: flipping it re-addresses every
    `(tenant, workflow_id)` pair, orphaning every journal silently, with no
    migration and no diagnostic. A future encoding change is a KEYING change and
    MUST take the `B-97` half (a) fork path.

    **Injective by construction, closing all THREE recorded hazards.** The
    encoding is prefix-free and self-delimiting — a decoder reads decimal digits
    greedily up to the first ``:``, then takes EXACTLY that many bytes, then
    expects either end-of-input or ``|`` — so:

    1. **branch collision** (`None` vs a real scope) is closed by SEGMENT COUNT
       alone: no reserved literal is needed and none is reserved. *(This store
       does NOT normalize its untenanted scope to ``_single``; see
       :func:`normalize_tenant_scope`, whose `None → None` disposition is the
       Runtime-local authority this encoding delegates to.)*
    2. **delimiter collision** (a scope or `workflow_id` containing ``|`` or
       ``:``) is closed by the length prefix — the delimiter is never SEARCHED
       for, only counted past. Delimiter REJECTION is explicitly NOT available
       as the answer: it would narrow a public input contract.
    3. **field-boundary shift** — the naive ``tenant + "\\x00" + workflow_id``
       concatenation maps `("a", "b\\0c")` and `("a\\0b", "c")` to identical
       bytes; the length prefixes make the boundary explicit.
    """
    segments = (workflow_id,) if tenant_scope is None else (tenant_scope, workflow_id)
    encoded = [segment.encode("utf-8", _KEY_ENCODING_ERRORS) for segment in segments]
    return _KEY_SEGMENT_JOINER.join(
        str(len(part)).encode("ascii") + _KEY_LENGTH_SEPARATOR + part for part in encoded
    )


def pause_journal_filename(tenant_scope: str | None, workflow_id: str) -> str:
    """The canonical journal filename for a `(tenant_scope, workflow_id)` pair.

    `tenant_scope` MUST already be normalized (see :func:`normalize_tenant_scope`).
    The sha256 digest is the ONLY thing that reaches the filesystem — the
    TENANT-SUBDIRECTORY layout is FORECLOSED by Runtime spec v1.108 §14.14.8 on
    path-safety grounds (`RuntimeConfig.tenant_id` accepts `/`, `..`, an absolute
    path and NUL, so a tenant used as a path COMPONENT could escape the journal
    root; injectivity alone does not make a component filesystem-safe).
    """
    digest = hashlib.sha256(encode_pause_journal_key(tenant_scope, workflow_id)).hexdigest()
    return f"{digest}{PAUSE_JOURNAL_FILENAME_SUFFIX}"


def legacy_pause_journal_filename(workflow_id: str) -> str:
    """The PRE-v1.108 journal filename: ``sha256(workflow_id)`` bare.

    Retained SOLELY for the §13.7 three-way classification and the (3b)
    adoption's LEGACY re-derivation. **No read path consults it** — Runtime spec
    v1.108 §14.14.8 forbids a fallback read (*"a fallback would create a second
    read authority over one key and fail open at exactly the boundary being
    built"*), and the (3a) disposition abandons legacy journals by default.

    Raises `UnicodeEncodeError` for a lone-surrogate `workflow_id` — faithful to
    the legacy derivation, which used STRICT UTF-8 and therefore could never
    have produced a file for such an id. Callers classifying an enumerated
    journal treat that as "not LEGACY".
    """
    digest = hashlib.sha256(workflow_id.encode("utf-8")).hexdigest()
    return f"{digest}{PAUSE_JOURNAL_FILENAME_SUFFIX}"


def journal_exclusion_is_degraded() -> bool:
    """Whether :func:`cross_process_journal_lock` is a documented no-op here.

    The predicate the (3b) adoption's *"REFUSE WHERE THE PRIMITIVE DEGRADES"*
    term keys on (Runtime spec v1.108 §14.14.8). Exposed as a NAMED PROPERTY of
    the lock rather than leaving callers to re-test the platform: the adoption's
    question is *"can this primitive exclude a straggler appender?"*, not *"is
    this Windows?"* — and a caller answering the second question would silently
    diverge if a future platform grew the same carve-out.

    Read at CALL time, not import time, so the carve-out branch is exercisable.
    """
    return _IS_WINDOWS


@contextmanager
def cross_process_journal_lock(journal_path: Path) -> Generator[None, None, None]:
    """Hold an exclusive same-host advisory lock over ONE journal's critical section.

    ``B-97`` half (b)'s primitive, promoted to module scope at half (a) so the
    (3b) adoption tool holds **the same lock of the same construction on the same
    inode** a straggler appender contends on (Runtime spec v1.108 §14.14.8 term 1
    / council `K-2`), rather than a second copy that would exclude nothing.
    :meth:`JournalWorkflowPauseStore._cross_process_append_lock` delegates here —
    ONE authority, never two.

    A hand-rolled ``fcntl.flock`` on a dedicated ``<journal>.lock`` file,
    mirroring the primitive already shipped at
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
    ``absent`` cause. A per-workflow lock leaves that pre-existing
    capture-not-yet-landed race exactly the size it already was; a directory-wide
    one would have widened it to the whole contended hold.

    No-op on Windows (``_IS_WINDOWS``) — no ``fcntl`` there; same posture as
    pre-``B-97``, matching ``harness_is.cross_process_ledger_lock``'s own
    carve-out (the ``B-45`` register row). ``fcntl`` is imported lazily inside
    this function, NEVER at module scope: an unguarded top-level import would
    break ``import harness_runtime`` outright on Windows. **The (3b) adoption
    REFUSES BY DEFAULT where this degrades** (spec §14.14.8 *"REFUSE WHERE THE
    PRIMITIVE DEGRADES"*) rather than proceeding on a declaration.

    **This acquisition BLOCKS the calling thread, but starves no event loop
    today (``B-103``, CLOSED — PREMISE FALSIFIED).** ``flock(LOCK_EX)`` holds
    the calling THREAD until the holder releases, and the sole async caller,
    :meth:`DurablePauseResumeProtocol.capture_pause_snapshot`, does call
    ``capture()`` inline. That looked like loop starvation and was registered as
    such — but every production invocation reaches it through
    ``workflow_driver._run_protocol_method_sync``, which runs the coroutine on a
    PRIVATE single-task loop via ``asyncio.run`` inside the driver's own
    ``asyncio.to_thread`` worker (that helper's docstring: *"no current event
    loop is bound on the worker thread"*). The only thing this blocks is the
    already-blocked worker thread; no co-resident coroutine or timer exists to
    starve. An offload was BUILT and DECLINED at the merge gate: it would have
    blocked a second thread and added a cancellation window for zero recovered
    concurrency.

    **Reopening trigger.** If a future arc replaces that helper's ``asyncio.run``
    with a captured-loop bridge — the evolution its own docstring anticipates,
    conditioned on the protocol body gaining real async I/O — this acquisition
    becomes genuinely loop-co-resident and ``B-103``'s premise goes live.
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


class JournalWorkflowPauseStore:
    """Durable per-workflow ``PauseSnapshot`` journal (workflow-layer F2/JOURNAL).

    ``capture`` appends the captured ``PauseSnapshot`` as one JSON line to the
    pair's ``<journal_dir>/<sha256(encode(tenant_scope, workflow_id))>.jsonl``
    file (durably, ``fsync``-ed); ``read_latest`` reads that file's **latest**
    line and re-validates it into a ``PauseSnapshot``. Because the journal is on
    disk, a fresh store over the same directory (a new process after a restart)
    resumes a pause captured by a prior process.

    **``tenant_id`` is a REQUIRED keyword, deliberately without a default.**
    Runtime spec v1.108 §14.14.8 makes the tenant scope part of the store's key
    identity, so a store that does not know its scope cannot compute a key at
    all. ``None`` is a legitimate DOMAIN VALUE here (the untenanted /
    single-tenant deployment), not an absence — defaulting it would conflate
    *"not specified"* with *"untenanted"* and would let a construction site
    silently key the wrong address space. Requiring it makes the §14.14.9.1
    both-surfaces-or-neither rule a type-level property at every construction
    site, not only a runtime one.
    """

    def __init__(self, *, journal_dir: Path, tenant_id: str | None) -> None:
        self._journal_dir = Path(journal_dir)
        # Normalized ONCE, at construction, so an invalid scope fails fast rather
        # than at the first capture. Delegates to the RUNTIME-LOCAL authority
        # (`None -> None`; `""` and `"_single"` REFUSED) — Runtime spec v1.108
        # §14.14.8 BINDS this delegate and explicitly FORBIDS delegating to
        # `harness_od`'s `sidecar_tag` / `_tenant_tag`, whose `None -> "_single"`
        # disposition is incompatible and would bind this store to a reserved
        # literal it has no need to reserve. It must also not be a THIRD
        # re-derivation — hence the import rather than a local copy.
        self._tenant_scope = normalize_tenant_scope(tenant_id)

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
                # `B-102` impl half (Runtime spec v1.108 §30's `absent` row):
                # INDETERMINATE across processes on exactly the argument
                # `empty-journal` already carried — a `capture()` dispatched but
                # not yet having created its journal file reports `absent`, and
                # that capture may complete immediately after this read.
                # `B-97`(b)'s append lock SHRINKS the window; it does not close
                # it, because the reader deliberately takes no lock. Reported
                # unconditionally, exactly as `empty-journal` is: the store
                # cannot know whether a second writer is reachable, and the spec
                # term is *"MUST NOT PRESENT it as decisive loss where a second
                # writer is reachable"* — so the honest value is the one that
                # never over-claims.
                indeterminate=True,
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
            #
            # `B-102`'s indeterminacy reaches the PARSE-failure branch ONLY,
            # NEVER this DECODE-failure branch (Runtime spec v1.108 §30's
            # `corrupt-latest` row): the invalid bytes are persistent on disk, an
            # append leaves them in place, and every re-read fails identically —
            # so routing this indeterminate would send the operator into exactly
            # the futile re-read loop the decode-routing rule exists to prevent.
            # UNCONDITIONALLY PERMANENT.
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
            # `B-102` impl half — the PARSE-failure branch of `corrupt-latest`
            # ONLY (Runtime spec v1.108 §30). A torn trailing line is exactly
            # what an in-flight append looks like from a reader, so a read
            # landing mid-append attributes `corrupt-latest` to a record that is
            # about to become well-formed. `workflow-mismatch` stays decisive:
            # the handle names a different workflow, which no concurrent append
            # changes.
            indeterminate=cause is PauseJournalReadCause.CORRUPT_LATEST,
            record_count=len(lines),
            latest_record_digest=digest,
        )

    # -- durable journal I/O ------------------------------------------------

    def _journal_file(self, workflow_id: str) -> Path:
        """The per-`(tenant, workflow)` journal file (filesystem-safe, collision-free).

        The ONLY key-derivation site in the store. **There is NO fallback read**
        — no code path consults the pre-v1.108 ``sha256(workflow_id)`` name
        (Runtime spec v1.108 §14.14.8: legacy records are ABANDONED BY DEFAULT
        under disposition (3a); a fallback would create a second read authority
        over one key and fail open at exactly the boundary being built).
        """
        return self._journal_dir / pause_journal_filename(self._tenant_scope, workflow_id)

    @contextmanager
    def _cross_process_append_lock(self, journal_path: Path) -> Generator[None, None, None]:
        """Hold an exclusive same-host lock over ONE journal's append section.

        ``B-97`` half (b). Delegates to the module-level
        :func:`cross_process_journal_lock` — promoted out of this method at half
        (a) so the (3b) adoption tool takes the SAME lock, of the same
        construction, on the SAME inode a straggler appender contends on. One
        authority, never two.
        """
        with cross_process_journal_lock(journal_path):
            yield

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
