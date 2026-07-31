"""§13.7 durable-pause-journal ENUMERATION — the read-only operator surface.

Runtime spec v1.108 §13.7 (NEW at the RATIFIED `B-97` half (a) arc) + §13.7.1
(the normative THREE-WAY classification). The shared core consumed by three
admin-tier callers: the `harness-inspect` extension (§13.7 / `K-11`), the (3b)
adoption tool, and the OPTIONAL disposal action.

**This surface is a PRECONDITION of the (3a) abandon-by-default disposition, not
an optional companion.** §14.14.8's keying amendment CREATES a durable class of
orphaned journals that no code path in the product can reach or list: nothing in
the runtime globs the pause-journal directory (the store's own design property —
reads open exactly one digest-named path), the filenames are irreversible sha256
digests so a manual listing yields opaque hex, and the append-only invariant
forbids removing the records. Without this surface, §14.14.8's own stated
recourse — *"drain pauses before upgrading"* — is NOT EXECUTABLE.

**ADMIN-TIER enumeration is permitted here and PROHIBITED on the runtime read
path** (§13.7 term 7). The two tiers are distinguished by CALLER, not by
convenience: the tenant-facing runtime read stays single-authority, resolves
exactly one key, and MUST NOT gain enumeration.

**READ-ONLY.** Nothing in this module opens a file for write, creates a
directory, or removes anything. The `harness-inspect` chmod-readonly fixture
discipline extends over it verbatim (§13.7 term 6 / C-RT-13 invariant #1).
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import re
from enum import StrEnum
from pathlib import Path
from typing import cast

from harness_runtime.lifecycle.journal_workflow_pause_store import (
    PAUSE_JOURNAL_FILENAME_SUFFIX,
    legacy_pause_journal_filename,
    pause_journal_filename,
)

__all__ = [
    "CANONICAL_JOURNAL_NAME_PATTERN",
    "UPPER_BOUND_DISCLAIMER",
    "EnumeratedJournal",
    "JournalIdentityClass",
    "classify_journal_bytes",
    "enumerate_pause_journals",
    "is_canonical_journal_name",
]


#: §13.7 term 1 — the CANONICAL JOURNAL NAME SHAPE, `<digest>.jsonl` exactly.
#: The filter is a CONTRACT TERM, not a detail: the per-workflow advisory-lock
#: files the `B-97`(b) append path creates with `O_CREAT` beside every journal
#: and NEVER unlinks (`<digest>.jsonl.lock`) MUST be excluded, and so must any
#: adoption write-aside / publication artifact. Listing them would inflate the
#: at-risk bound and emit spurious rows whose wrapper identity is necessarily
#: ABSENT — *a lock file carries no bytes and nothing reads it*.
CANONICAL_JOURNAL_NAME_PATTERN = re.compile(
    r"^[0-9a-f]{64}" + re.escape(PAUSE_JOURNAL_FILENAME_SUFFIX) + r"$"
)


#: §13.7 term 3-bis — the surface MUST say what it CANNOT tell. The store is
#: append-only, never truncated, and writes NO pause-resolved marker, so a
#: workflow that paused and was then successfully resumed leaves its journal
#: behind, byte-indistinguishable from one whose pause is still outstanding.
#: (Registered at `B-104`; the discriminator is capture-side and fork-shaped.)
UPPER_BOUND_DISCLAIMER = (
    "UPPER BOUND ONLY — this is NOT an outstanding-pause inventory. The pause "
    "journal is append-only and writes no pause-resolved marker, so a journal "
    "whose pause was already resumed is byte-indistinguishable from one still "
    "outstanding. This listing bounds the at-risk set FROM ABOVE and MUST NOT "
    "be cited as proof a cutover is safe."
)


class JournalIdentityClass(StrEnum):
    """The §13.7.1 THREE-WAY classification of an enumerated journal.

    Both formats live in ONE directory under digest-shaped filenames, so the
    surface cannot treat what it finds as uniformly legacy. Each file is
    classified by RE-DERIVING its filename from the wrapper `workflow_id` —
    never by probing a path from an operator-supplied identifier, which §13.7
    term 1 forecloses.

    **The classification governs ACTIONABILITY, never DISCLOSURE.** §13.7 term
    3-ter reports the wrapper identity for EVERY enumerated journal; this enum
    decides only whether that identity may be presented as something the
    operator may act on.
    """

    LEGACY = "legacy"
    """`sha256(workflow_id)` re-derives the filename. The identity is
    ACTIONABLE; this journal is what (3a) abandons and (3b) can adopt."""

    CURRENT_FORMAT = "current-format"
    """`sha256(encode(normalize(config.tenant_id), workflow_id))` re-derives the
    filename — CURRENT-FORMAT under THIS deployment's own scope. Not at risk,
    not adoptable, reported as ORDINARY STATE. *This case is what makes the
    classification three-way rather than a bare binding check: without it the
    surface would slander every valid post-upgrade journal as mis-filed.*"""

    NOT_ATTRIBUTABLE = "not-attributable"
    """NEITHER derivation re-derives the filename, and the surface says exactly
    that rather than picking. TWO different things land here and **this surface
    cannot tell them apart**: a MIS-FILED record (wrapper says `B`, file named
    for `A`), and a perfectly valid CO-TENANT journal belonging to a different
    scope sharing the directory — which is the very topology `B-97` exists for.
    Reporting either as the other would be a false diagnosis, so the honest
    report is *"not attributable to this deployment's configured scope; not
    actionable from here"*, with **no guess** as to which case obtains."""


@dataclasses.dataclass(frozen=True, slots=True)
class EnumeratedJournal:
    """One enumerated pause journal, as §13.7 requires it be reported."""

    path: Path
    """The journal file itself. Reported so the operator can act on it."""

    record_count: int | None
    """§13.7 term 3 — NON-BLANK RAW LINES, computed WITHOUT parsing a record
    (term 4). The same number the store's own `read_latest_attributed` reports,
    deliberately: a *"well-formed lines"* count would require parsing and the two
    surfaces would disagree on a torn journal — the very case term 3-bis and the
    pre-flight requirement demand stay listable.

    **`None` means UNKNOWN — the journal exists but could not be read at all**
    (`EACCES`, `EIO`, …). It is a DIFFERENT fact from `0`, which means *known to
    hold no record*, and the type keeps them apart so the illegal state — an
    unreadable journal presenting itself as an empty one — is unrepresentable.
    Reporting an unreadable journal as `0` would present UNKNOWN exposure as
    proven-zero on the pre-flight surface that exists to bound it. *(Out-of-family
    review round 3 [P2].)*"""

    latest_record_digest: str | None
    """§13.7 term 3 — sha256 of the latest RAW line (no deserialization);
    `None` when the journal holds no non-blank line."""

    workflow_id: str | None
    """§13.7 term 3-ter — read from the journal record's STORE-OWNED WRAPPER
    key, the outer `workflow_id` the store writes BESIDE the embedded snapshot.
    **This does NOT violate term 4**: term 4 forbids parsing, returning or
    resuming a `PauseSnapshot`, and the wrapper key is a store-owned envelope
    field, not a snapshot field.

    `None` where the wrapper key is unreadable (a torn or undecodable latest
    line) — the journal is STILL LISTED with the identity reported ABSENT. The
    surface MUST NOT fabricate, guess, or omit the row."""

    classification: JournalIdentityClass | None
    """`None` iff :attr:`workflow_id` is `None` — an absent identity cannot be
    classified, and guessing one would be the fabrication term 3-ter forbids."""

    @property
    def unreadable(self) -> bool:
        """Whether the journal's bytes could not be read at all.

        Distinct from *empty*: an unreadable journal has an UNKNOWN record count,
        an unknown identity, and is never a disposal candidate.
        """
        return self.record_count is None

    @property
    def identity_actionable(self) -> bool:
        """Whether the reported identity may be presented as ACTIONABLE.

        TRUE for LEGACY only (§13.7.1). A CURRENT-FORMAT journal is ordinary
        state, not something to drain; a NOT-ATTRIBUTABLE one may be another
        tenant's live journal and this deployment must not act on it.
        """
        return self.classification is JournalIdentityClass.LEGACY

    @property
    def adoptable(self) -> bool:
        """Whether the (3b) adoption may operate on this journal.

        §14.14.8's FIFTH mechanical term: *"the adoption MUST operate ONLY on
        journals §13.7's classification returns as LEGACY, and MUST REFUSE every
        other enumerated file."* An adoption that trusts the wrapper and
        republishes a mis-filed record at `encode(tenant, B)` **makes DORMANT
        state LIVE** — B's read then finds it, and the snapshot-workflow match,
        step-index range and `snapshot_hash` guards ALL PASS, because the record
        was always internally consistent; only its ADDRESS was wrong.
        """
        return self.identity_actionable


def is_canonical_journal_name(name: str) -> bool:
    """§13.7 term 1 — whether `name` is a canonical journal file name."""
    return CANONICAL_JOURNAL_NAME_PATTERN.match(name) is not None


def classify_journal_bytes(
    filename: str, raw: bytes, *, tenant_scope: str | None, scope_known: bool = True
) -> tuple[str | None, JournalIdentityClass | None]:
    """The `(wrapper identity, §13.7.1 classification)` of one journal's BYTES.

    Factored out so the (3b) adoption can RE-CLASSIFY a source **under its own
    exclusion lock** against exactly the same rules the enumeration used, rather
    than a second copy that could drift. *(Out-of-family review round 4 [P1]: the
    enumeration necessarily classifies BEFORE the lock is taken, so a
    lock-respecting legacy writer can append between the two and invalidate the
    identity the adoption would otherwise publish under.)*
    """
    lines = [line for line in raw.splitlines() if line.strip()]
    if not lines:
        return None, None
    workflow_id = _wrapper_workflow_id(lines[-1])
    if workflow_id is None:
        return None, None
    return workflow_id, _classify(
        filename, workflow_id, tenant_scope=tenant_scope, scope_known=scope_known
    )


def enumerate_pause_journals(
    journal_dir: Path, *, tenant_scope: str | None, scope_known: bool = True
) -> list[EnumeratedJournal]:
    """ENUMERATE the resolved pause-journal directory — never probe a derived path.

    §13.7 term 1: the surface LISTS the directory and **accepts no `workflow_id`
    (or tenant scope) to stat a DERIVED path**. Every tenant would probe the same
    legacy path, so a single-path probe on an admin binary would reintroduce the
    EXISTENCE ORACLE the read-path diagnostic was withdrawn for — a distinct
    result would disclose that a record exists for a GUESSED `workflow_id`. *This
    is the load-bearing shape term.*

    `tenant_scope` is NOT a lookup key: it is the deployment's own already-normalized
    scope, used ONLY to re-derive candidate filenames for the §13.7.1
    classification of files that were found by LISTING.

    **`scope_known=False` means the deployment's own scope could not be
    determined at all**, and it is NOT the same as an untenanted scope. Passing
    `None` for both would make an untenanted-format journal report
    `CURRENT-FORMAT` — *ordinary state, not at risk* — on a deployment that may
    not own it, which is a false all-clear a JSON consumer would act on. Under an
    unknown scope the CURRENT-FORMAT arm is simply not available: LEGACY still
    proves itself (its derivation needs no scope) and everything else is honestly
    NOT-ATTRIBUTABLE. *(Out-of-family review round 4 [P2].)*

    Returns one row per canonical journal FILE, sorted by filename for a stable
    listing. Rows are returned even when the wrapper identity is unreadable — a
    journal whose latest line cannot be decoded still reports its two scalars and
    an ABSENT identity rather than being omitted.

    **Only REGULAR FILES are described.** §13.7 term 1 counts *"a file matching
    the canonical journal name shape"*, and the name shape alone does not make an
    entry a file: a directory named `<64hex>.jsonl` would become a phantom
    zero-count row, and a FIFO would BLOCK the read indefinitely — on a
    **pre-flight** surface whose whole purpose is to run before an upgrade.
    *(Out-of-family review round 1 [P2].)*

    Raises `OSError` when the directory itself cannot be listed — deliberately
    NOT swallowed into an empty listing, which would render as
    `pause journals: 0` and convert unknown exposure into a FALSE ZERO on the
    surface that exists to prevent exactly that loss. The caller maps it to the
    binary's own path-error exit. *(Out-of-family review round 1 [P2].)*
    """
    rows: list[EnumeratedJournal] = []
    for path in sorted(journal_dir.iterdir(), key=lambda candidate: candidate.name):
        if not is_canonical_journal_name(path.name) or not path.is_file():
            continue
        rows.append(_describe(path, tenant_scope=tenant_scope, scope_known=scope_known))
    return rows


def _describe(path: Path, *, tenant_scope: str | None, scope_known: bool) -> EnumeratedJournal:
    """Describe ONE journal: the two raw scalars, the wrapper identity, the class.

    **The two scalars are computed over RAW BYTES**, and the wrapper identity is
    decoded separately and conditionally. §13.7 term 3 defines the count as
    NON-BLANK RAW LINES and the digest as a hash of the latest RAW line —
    neither requires decoding, and a journal holding one invalid UTF-8 byte
    anywhere (an old corrupt line beneath a perfectly valid latest record, say)
    must still report both, or the cutover upper bound is UNDERSTATED on exactly
    the torn-journal case term 3-bis says must stay listable. *(Out-of-family
    review round 1 [P2]: a whole-file `read_text` collapsed such a journal to
    `record_count=0`.)*
    """
    try:
        raw = path.read_bytes()
    except OSError:
        # Listed, never omitted — and reported as UNKNOWN, never as empty.
        # §13.7 term 3-bis and the pre-flight requirement demand an unreadable
        # journal stay VISIBLE; fabricating `record_count=0` would make it look
        # like a journal known to hold nothing, understating the very bound this
        # surface exists to compute. *(Out-of-family review round 3 [P2].)*
        return EnumeratedJournal(
            path=path,
            record_count=None,
            latest_record_digest=None,
            workflow_id=None,
            classification=None,
        )
    lines = [line for line in raw.splitlines() if line.strip()]
    if not lines:
        return EnumeratedJournal(
            path=path,
            record_count=0,
            latest_record_digest=None,
            workflow_id=None,
            classification=None,
        )
    latest = lines[-1]
    digest = hashlib.sha256(latest).hexdigest()
    workflow_id, classification = classify_journal_bytes(
        path.name, raw, tenant_scope=tenant_scope, scope_known=scope_known
    )
    return EnumeratedJournal(
        path=path,
        record_count=len(lines),
        latest_record_digest=digest,
        workflow_id=workflow_id,
        classification=classification,
    )


def _wrapper_workflow_id(line: bytes) -> str | None:
    """Read the STORE-OWNED WRAPPER `workflow_id` — and nothing else.

    §13.7 term 4's boundary is **the EMBEDDED SNAPSHOT, not the record**: reading
    the wrapper's own keys is permitted and is what term 3-ter requires;
    deserializing, projecting, or returning anything from
    `record["pause_snapshot"]` is not. This function never touches that key.

    Takes RAW BYTES and returns `None` on any decode or parse failure — the
    *"identity reported ABSENT"* disposition term 3-ter mandates, kept separate
    from the two scalars so an undecodable byte costs the identity and nothing
    else.
    """
    try:
        loaded = json.loads(line.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(loaded, dict):
        return None
    value = cast("dict[str, object]", loaded).get("workflow_id")
    return value if isinstance(value, str) else None


def _classify(filename: str, workflow_id: str, *, tenant_scope: str | None) -> JournalIdentityClass:
    """The §13.7.1 THREE-WAY classification, by RE-DERIVATION of the filename."""
    try:
        if legacy_pause_journal_filename(workflow_id) == filename:
            return JournalIdentityClass.LEGACY
    except UnicodeEncodeError:
        # A lone-surrogate `workflow_id` could never have produced a LEGACY file:
        # the pre-v1.108 derivation used STRICT UTF-8 and would have raised at
        # capture. Not legacy — fall through to the remaining derivations.
        pass
    if pause_journal_filename(tenant_scope, workflow_id) == filename:
        return JournalIdentityClass.CURRENT_FORMAT
    return JournalIdentityClass.NOT_ATTRIBUTABLE
