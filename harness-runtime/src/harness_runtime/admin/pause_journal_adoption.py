"""`python -m harness_runtime.admin.pause_journal_adoption` — the §14.14.8 (3b)
operator-declared adoption of legacy untenanted pause journals.

Runtime spec v1.108 §14.14.8 *"(3b) OPERATOR-DECLARED ADOPTION"* + §13.4 (the
NEW admin-migration inventory row) + §13.7 (the enumeration this action is
unimplementable without). Council conditions `K-2`…`K-6`.

**NOT the default. (3a) — abandon-by-default — is.** The failure-mode asymmetry
is the stated reason: a violated (3a) cutover fails **REFUSING** (the read
reports `absent`, an availability loss); a violated (3b) adoption fails
**SILENTLY AND EXECUTES** (a correctness loss). This action exists because under
(3a) a deployment that upgraded with pauses outstanding has EXACTLY ONE recovery
path and it is this one — the spec says (3b) is AVAILABLE, and a promise the
product does not keep is the state the plan exists to prevent.

**Under Reading A this is a pure RELOCATION**: records are re-published at the
tenant-scoped path with the **RECORD SHAPE UNCHANGED**, so the five-member cause
vocabulary and the no-wrapper-key promise both hold. An unconditional STAMPING
migration is FORBIDDEN — it would silently add the wrapper key this reading
excludes, converting the ratified reading into a different one. The legacy
source file is **left untouched** and becomes an unread orphan; nothing is
rewritten or truncated, so the append-only substrate invariant is not engaged.

**FIVE mechanical terms bind it**, each with its own refusal:

1. **LEGACY-SOURCE EXCLUSION** — the per-journal advisory lock of the SAME
   construction the append path takes, on the **LEGACY SOURCE** journal's lock
   file (the inode a straggler appender actually contends on), held continuously
   from before the source read until after the target publication commits. A
   directory-tree scope lock is explicitly NOT SUFFICIENT: `flock` contends only
   on the same inode, and the pause-journal appender does not take the house
   directory lock — a migration holding it would exclude ZERO writers. Locking
   the tenant-composite TARGET excludes nothing that matters either, because a
   straggler computes the LEGACY key.
2. **READ-BACK VERIFICATION AGAINST THE LEGACY SOURCE** — as the final act under
   the exclusion and BEFORE publishing, re-read the source and compare
   `record_count` + `latest_record_digest`, refusing and leaving the target
   unpublished on any difference. **What this does and does NOT do:** it DETECTS
   interference within the `[source read, read-back]` window and thereby
   NARROWS, but does NOT CLOSE, the residual. **It does NOT cover, and does not
   make safe, the mixed-version window.** The residual, named: a lockless
   straggler that appends to the legacy path AFTER the read-back leaves the
   target holding an older record than the source, with every term here
   satisfied. What that rests on is the MANDATORY no-mixed-version cutover —
   which the harness provides NO MECHANISM to verify — and nothing else.
3. **WRITE-ONCE, CRASH-ATOMIC, NO-REPLACE PUBLICATION** — write aside → make the
   bytes durable → atomic no-replace commit (`os.link`) → make the destination
   directory entry durable. A target created between any pre-check and the
   publish makes the PUBLISH FAIL rather than overwrite, so the commit closes the
   time-of-check/time-of-use race BY CONSTRUCTION; any pre-check is ADVISORY
   ONLY. No second lock on the target is required or permitted.
4. **PER-JOURNAL SEQUENCING; IDEMPOTENT AND RE-RUNNABLE** — strictly per journal,
   NEVER holding journal *i*'s lock while taking journal *i+1*'s, so the
   instantaneous blocking footprint equals one append's. The whole operation is
   directory-non-atomic and therefore re-runnable, completing a directory-level
   partial migration on re-run. **The skip discriminator is CONTENT EQUALITY**
   between the target and the exclusion-held legacy source the run would publish
   — identical → already published, SKIP; different → FOREIGN, REFUSE. A re-run
   MUST NOT delete or replace a committed target on the theory that its own prior
   run *"did not finish"*: crash-atomicity guarantees ABSENT-OR-COMPLETE, and a
   crash AFTER the commit necessarily leaves a complete, valid target.
5. **THE FILENAME↔WRAPPER BINDING, via §13.7's THREE-WAY CLASSIFICATION** — the
   adoption operates ONLY on journals classified LEGACY and REFUSES every other
   enumerated file. The legacy filename is `sha256(workflow_id)` and each record
   carries the store-owned wrapper `workflow_id`, so the two are a self-checking
   pair the shipped read already enforces: a record whose wrapper says `B` sitting
   in the journal named for `A` is refused `workflow-mismatch` on a read of `A`
   and is never opened by a read of `B`. It is **dormant BY CONSTRUCTION**. An
   adoption that trusts the wrapper and republishes it at `encode(tenant, B)`
   **MAKES IT LIVE** — the snapshot-workflow match, step-index range and
   `snapshot_hash` guards ALL PASS, because the record was always internally
   consistent; only its ADDRESS was wrong.

Plus **REFUSE WHERE THE PRIMITIVE DEGRADES**: where the exclusion primitive is a
documented platform no-op (Windows — no `fcntl`), adoption REFUSES BY DEFAULT
rather than proceeding on a declaration. A read-back-only mode is offered SOLELY
under an explicit operator flag whose weaker guarantee is stated in the refusal
text; silent degradation of the guard is PROHIBITED. The cost is stated: such an
operator loses **(3b)**, not correctness — **(3a) remains fully available.**

**NAME THE SILENCE.** A resume against stale-but-internally-consistent adopted
state passes EVERY shipped guard, and this store carries **NO HASH CHAIN** — a
publication that dropped complete records would leave no structural trace and no
post-hoc forensic path. The five terms stand in place of a runtime detection that
does not exist.

**No HITL gate.** The operator is the actor. What replaces a gate is a RECORD —
the durable, operator-retrievable per-journal account below, whose disposition
vocabulary is TOTAL over every refusal this module mandates. See
:class:`AdoptionDisposition` for the `K-17` emission determination.

**Framework discipline** (spec §13 deferred-to-discretion): argparse only,
mirroring `harness_runtime.admin.inspect` / `migrate_audit_sidecar`.

Usage::

    python -m harness_runtime.admin.pause_journal_adoption <journal-dir> \\
        --tenant-id <TENANT>            # omit for the untenanted target scope
    harness adopt-pause-journals <journal-dir> --tenant-id <TENANT>
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
import tempfile
from collections.abc import Sequence
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from harness_runtime.admin.pause_journal_enumeration import (
    EnumeratedJournal,
    JournalIdentityClass,
    classify_journal_bytes,
    enumerate_pause_journals,
)
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    cross_process_journal_lock,
    journal_exclusion_is_degraded,
    pause_journal_filename,
)
from harness_runtime.lifecycle.protected_result_store import normalize_tenant_scope

__all__ = [
    "DEFAULT_ACCOUNT_FILENAME",
    "AdoptionDisposition",
    "AdoptionOutcome",
    "adopt_pause_journals",
    "build_parser",
    "main",
]


#: Where the per-journal account lands by default. Beside the journal directory,
#: NOT inside it — the enumeration's canonical-name filter would exclude it
#: either way, but keeping the journal directory free of non-journal files is
#: what makes that filter a belt rather than the only barrier.
DEFAULT_ACCOUNT_FILENAME = "pause-journal-adoption-account.jsonl"

_EXIT_OK = 0
_EXIT_REFUSED = 1
_EXIT_USAGE = 2

#: Write-aside prefix for the term-3 publication. Deliberately NOT matching the
#: `<64 hex>.jsonl` canonical journal shape, so an interrupted publication's
#: leftover temp file is never counted, classified, or reported by §13.7.
_WRITE_ASIDE_PREFIX = ".adopt-tmp-"


class AdoptionDisposition(StrEnum):
    """The per-journal account's disposition vocabulary — **TOTAL over every
    refusal §14.14.8 mandates**.

    Runtime spec v1.108 §14.14.8: *"the adoption MUST produce a durable,
    operator-retrievable account of what it did, per journal, whose disposition
    vocabulary is TOTAL over every refusal this section mandates ... Totality is
    the contract term: every path that refuses a journal writes a row, and a
    refusal with no disposition is a non-conformance, not a gap to fill later."*

    **Totality is enforced BY CONSTRUCTION, not by enumeration.** Every
    per-journal path in this module returns an :class:`AdoptionOutcome`, whose
    `disposition` field is REQUIRED; the driver loop writes exactly one account
    row per outcome it receives. There is no code path that refuses a journal
    without returning one, so a future refusal cannot be added without also
    carrying a disposition — the type will not permit it.

    **`K-17` EMISSION DETERMINATION — made explicitly, never inherited by
    assumption** (§14.14.8: *"Whether that account additionally lands as an
    OD-owned audit/trace event is NOT determined at this leg and MUST NOT be
    assumed ... owed as an explicit determination at the impl leg"*).

    **DETERMINATION: NO OD-OWNED CARRIER IS OWED. The account is this durable,
    operator-retrievable JSONL file and nothing else.** Grounded against
    `Spec_Operational_Discipline_v1_36.md`:

    1. **No existing OD namespace admits this event.** The C-OD-30 `pause.*` /
       `resume.*` family is defined over `PauseEvent` and
       `(ResumeAttempt, ResumeOutcome)` pairs, and v1.36 §C-OD-30.5 extends it
       with exactly TWO further event kinds — the §14.14.9 accessor read and the
       §30 staleness-refused resume. All four compose from live runtime objects
       this action never constructs. A migration over opaque digest-named files
       is not a member of that family.
    2. **The emission machinery is not reachable from a stopped harness.** OD's
       audit-ledger emission (C-OD-14 / C-OD-21 `sign_audit_entry`) requires a
       `LedgerWriter`, a signing backend and an `Actor`; §13.5 row 5 establishes
       that admin binaries run against a STOPPED harness with no live
       `HarnessContext` and take config as an INPUT rather than bootstrapping one.
    3. **The sibling surface declared the same absence, on the same ground.**
       §13.7's own posture block rules *"Trace/audit emission: NOT DECLARED AT
       THIS LEG"* — the surface runs against a stopped harness, admin-surface
       span design is a follow-on, and no OD-owned schema is engaged.
    4. **Declaring one here would be an X-AL-3 violation.** Minting a namespace
       or extending a C-OD payload is an OD-owned schema surface; the `B-69` leg
       established the precedent that such a change owes an OD spec AND plan
       delta with its own unit (U-OD-57), which a Runtime unit cannot author.

    If a future arc wants admin-surface telemetry, it takes an OD spec leg. This
    determination is recorded so that absence is a DECISION, not an omission.
    """

    ADOPTED = "adopted"
    """Relocated: published at the tenant-composite path, record shape unchanged,
    legacy source left untouched as an orphan."""

    SKIPPED_ALREADY_PUBLISHED = "skipped-as-already-published"
    """Term 4's re-run branch — the target exists and its content is IDENTICAL to
    what this run would publish. Needed for a whole journal already done AND for
    a crash AFTER the commit, which necessarily leaves a complete, valid target.
    **Never republished, never deleted.**"""

    REFUSED_FOREIGN_TARGET = "refused-as-foreign-target"
    """Term 4's other branch — the target exists with DIFFERENT content. Because
    the record shape is unchanged, an adopted record and an upgraded writer's
    fresh capture are structurally identical, so treating every existing target
    as *done* would accept foreign or newer state. Refused."""

    REFUSED_ON_READ_BACK = "refused-on-read-back"
    """Term 2 — the legacy source changed inside the `[read, read-back]` window.
    The target is left UNPUBLISHED."""

    REFUSED_NOT_LEGACY = "refused-as-not-LEGACY"
    """Term 5 — §13.7's classification returned **NOT-ATTRIBUTABLE** (a mis-filed
    record OR a co-tenant's valid journal — this surface cannot tell them apart
    and does not guess) or **no identity at all**. Published under NEITHER name.

    Exactly the two sub-cases §14.14.8's own vocabulary names in its parenthetical
    (*"identity-mismatched or not-attributable"*). The CURRENT-FORMAT case takes
    :attr:`SKIPPED_NOT_ADOPTABLE` instead — see that member for why."""

    SKIPPED_NOT_ADOPTABLE = "skipped-as-current-format-not-adoptable"
    """§13.7.1's second arm — a valid CURRENT-FORMAT journal under this
    deployment's own scope.

    **A DELIBERATE ADDITION beyond §14.14.8's minimum list, and the ground is
    stated rather than assumed.** The spec's vocabulary is explicitly a floor
    (*"at minimum"*), and §13.7.1 rules a current-format journal *"not at risk,
    not adoptable, **reported as ordinary state**"* — NOT as something refused.
    Folding it into `refused-as-not-LEGACY` would have two costs, both surfaced by
    execution rather than argued: the account would describe this deployment's own
    healthy live state as a REFUSAL, and — because the run's exit code is
    nonzero-on-refusal — **every idempotent re-run on a normally-operating
    deployment would exit 1**, since its own current-format journals are enumerated
    alongside the legacy ones. That would convert the promised recoverable retry
    into a permanent failure signal. Totality is unaffected: all six mandated
    dispositions remain, and this member only splits a non-refusal out of one of
    them."""

    REFUSED_EXCLUSION_DEGRADED = "refused-because-the-exclusion-primitive-degraded"
    """The exclusion primitive is a documented platform no-op. REFUSED BY
    DEFAULT; the read-back-only escape is reachable only under an explicit
    operator flag whose weaker guarantee appears in the refusal text."""


#: The dispositions that make the run's exit code nonzero. Keyed on the ENUM
#: MEMBERS, never on a string prefix: a value-prefix test silently swept the
#: CURRENT-FORMAT case in when it was still spelled as a refusal, and would do so
#: again for any future member whose value happens to begin with "refused".
_REFUSAL_DISPOSITIONS = frozenset(
    {
        AdoptionDisposition.REFUSED_FOREIGN_TARGET,
        AdoptionDisposition.REFUSED_ON_READ_BACK,
        AdoptionDisposition.REFUSED_NOT_LEGACY,
        AdoptionDisposition.REFUSED_EXCLUSION_DEGRADED,
    }
)


@dataclasses.dataclass(frozen=True, slots=True)
class AdoptionOutcome:
    """What the adoption did to ONE journal. `disposition` is REQUIRED."""

    source: str
    """The legacy source journal's filename."""

    disposition: AdoptionDisposition
    detail: str
    workflow_id: str | None = None
    target: str | None = None
    """The tenant-composite target filename, where one was derived."""

    def as_account_row(self) -> dict[str, object]:
        """The durable account row. One per journal, always."""
        return {
            "source": self.source,
            "disposition": self.disposition.value,
            "detail": self.detail,
            "workflow_id": self.workflow_id,
            "target": self.target,
        }


def adopt_pause_journals(
    journal_dir: Path,
    *,
    tenant_id: str | None,
    account_path: Path,
    allow_degraded_exclusion: bool = False,
) -> list[AdoptionOutcome]:
    """Run the (3b) adoption over `journal_dir`. Returns one outcome per journal.

    **Term 4 — per-journal sequencing.** Each journal is acquired, read, copied,
    verified, published crash-atomically and released BEFORE the next is touched;
    journal *i*'s lock is never held while journal *i+1*'s is taken, so the
    instantaneous blocking footprint equals one append's and the cross-workflow
    blocking `B-97`(b) deliberately rejected is not reintroduced.

    Each journal is independently all-or-nothing while the operation as a whole
    is **directory-non-atomic** — hence idempotent and re-runnable, completing a
    directory-level partial migration on re-run.

    **The account is a WRITE-AHEAD, append-only, two-phase log**, appended per
    journal as the run proceeds rather than buffered to the end: an interrupted
    run must be reconstructable WITHOUT re-deriving it from the filesystem,
    which a buffer written at exit would defeat.

    **Two phases, because one is not enough** *(out-of-family review round 2
    [P1])*. An outcome row written only AFTER `_adopt_one` returns leaves a
    window in which the target is already committed and durable while no row
    exists — and a re-run then records `skipped-as-already-published`, so the
    ADOPTED fact is lost PERMANENTLY and the operator is left inferring it from
    the filesystem, the exact thing the account exists to avoid. So:

    1. a `publish-intent` row is appended, durably, **immediately before** the
       publication can commit — see :func:`_append_intent_row`;
    2. the outcome row follows.

    An intent row with **no matching outcome row** is therefore an unambiguous
    *"this journal's publication was in flight when the run stopped"* marker,
    naming the exact source and target. Nothing is ever rewritten: the account
    inherits the append-only discipline of the substrate it records.
    """
    tenant_scope = normalize_tenant_scope(tenant_id)
    outcomes: list[AdoptionOutcome] = []
    for journal in enumerate_pause_journals(journal_dir, tenant_scope=tenant_scope):
        outcome = _adopt_one(
            journal,
            journal_dir=journal_dir,
            tenant_scope=tenant_scope,
            allow_degraded_exclusion=allow_degraded_exclusion,
            account_path=account_path,
        )
        _append_account_row(account_path, outcome)
        outcomes.append(outcome)
    return outcomes


def _adopt_one(
    journal: EnumeratedJournal,
    *,
    journal_dir: Path,
    tenant_scope: str | None,
    allow_degraded_exclusion: bool,
    account_path: Path,
) -> AdoptionOutcome:
    """Adopt (or refuse) ONE journal. ALWAYS returns an outcome — totality.

    `account_path` is taken so the WRITE-AHEAD `publish-intent` row can be
    appended immediately before the publication commits. Every other path here
    changes no durable state, so none of them writes ahead — the intent row
    exists precisely and only where a crash could otherwise leave a committed
    target with no record of who committed it.
    """
    # -- Term 5: the filename<->wrapper binding, via the THREE-WAY class. ----
    # Checked FIRST, before any lock is taken: refusing a non-LEGACY journal
    # needs no exclusion, and taking one would block an appender for a file this
    # run will not touch.
    if not journal.adoptable:
        if journal.classification is JournalIdentityClass.CURRENT_FORMAT:
            return AdoptionOutcome(
                source=journal.path.name,
                disposition=AdoptionDisposition.SKIPPED_NOT_ADOPTABLE,
                detail=(
                    "§13.7.1 classified this journal CURRENT-FORMAT under this "
                    "deployment's own scope — ordinary state, not at risk, not "
                    "adoptable. Reported, never touched."
                ),
                workflow_id=journal.workflow_id,
            )
        classification = (
            journal.classification.value
            if journal.classification is not None
            else "identity-absent"
        )
        return AdoptionOutcome(
            source=journal.path.name,
            disposition=AdoptionDisposition.REFUSED_NOT_LEGACY,
            detail=(
                f"§13.7.1 classified this journal {classification} — the adoption "
                f"operates ONLY on journals whose wrapper workflow_id re-derives "
                f"their own sha256 filename (LEGACY). Published under NEITHER "
                f"name: republishing a record whose address never matched its "
                f"wrapper would promote dormant mis-filed state into LIVE state."
            ),
            workflow_id=journal.workflow_id,
        )
    # `adoptable` is LEGACY-only, and LEGACY requires a non-`None` identity (the
    # classification is `None` exactly when the wrapper key is unreadable), so
    # this branch is unreachable — narrowed here rather than asserted.
    workflow_id = journal.workflow_id
    if workflow_id is None:  # pragma: no cover — excluded by `adoptable`
        return AdoptionOutcome(
            source=journal.path.name,
            disposition=AdoptionDisposition.REFUSED_NOT_LEGACY,
            detail="no wrapper workflow_id to adopt under",
        )

    # -- REFUSE WHERE THE PRIMITIVE DEGRADES. -------------------------------
    if journal_exclusion_is_degraded() and not allow_degraded_exclusion:
        return AdoptionOutcome(
            source=journal.path.name,
            disposition=AdoptionDisposition.REFUSED_EXCLUSION_DEGRADED,
            detail=(
                "the legacy-source exclusion primitive (fcntl.flock) is a "
                "documented no-op on this platform, so a straggler appender "
                "cannot be excluded. REFUSED BY DEFAULT rather than proceeding "
                "on a declaration. --read-back-only proceeds with a STRICTLY "
                "WEAKER guarantee: read-back DETECTS interference inside the "
                "[read, read-back] window but CANNOT EXCLUDE a writer, so an "
                "append landing after the read-back is undetected. The cost of "
                "refusing is (3b), NOT correctness — (3a) abandon-by-default "
                "remains fully available."
            ),
            workflow_id=workflow_id,
        )

    target_name = pause_journal_filename(tenant_scope, workflow_id)
    target = journal_dir / target_name

    # -- Term 1: LEGACY-SOURCE exclusion, held source-read -> publication. ---
    # The lock is on the LEGACY SOURCE journal's own lock file — the inode a
    # straggler appender contends on. Locking the TARGET would exclude nothing
    # that matters, because a straggler computes the LEGACY key.
    with cross_process_journal_lock(journal.path):
        try:
            source_bytes = journal.path.read_bytes()
        except OSError as exc:
            return AdoptionOutcome(
                source=journal.path.name,
                disposition=AdoptionDisposition.REFUSED_ON_READ_BACK,
                detail=f"legacy source unreadable under the exclusion: {exc}",
                workflow_id=workflow_id,
                target=target_name,
            )
        # -- Term 5, RE-CHECKED UNDER THE EXCLUSION. -------------------------
        # The enumeration necessarily classified this journal BEFORE the lock was
        # taken, so a LOCK-RESPECTING legacy writer could have appended in
        # between and changed the wrapper identity. Publishing under the
        # pre-lock identity would then write the CURRENT source bytes to the
        # STALE key: an unusable target under a name whose record says something
        # else, reported as ADOPTED, with a re-run refusing the source. The
        # identity that decides the target must therefore be re-derived from the
        # bytes read UNDER the lock. *(Out-of-family review round 4 [P1].)*
        locked_id, locked_class = classify_journal_bytes(
            journal.path.name, source_bytes, tenant_scope=tenant_scope
        )
        if locked_id != workflow_id or locked_class is not JournalIdentityClass.LEGACY:
            return AdoptionOutcome(
                source=journal.path.name,
                disposition=AdoptionDisposition.REFUSED_NOT_LEGACY,
                detail=(
                    f"the legacy source changed between enumeration and the "
                    f"exclusion: identity {workflow_id!r} -> {locked_id!r}, "
                    f"classification {locked_class}. REFUSED rather than "
                    f"published under the stale key."
                ),
                workflow_id=locked_id,
            )

        copied = _scalars(source_bytes)

        # -- Term 4's re-run discriminator: CONTENT EQUALITY. ---------------
        # Advisory only per term 3 — the no-replace commit is the authority. But
        # it is what distinguishes "already published" from "foreign", which a
        # bare `FileExistsError` cannot. The target read happens HERE; its
        # VERDICT is deferred until after the read-back below.
        target_bytes: bytes | None = None
        if target.exists():
            try:
                target_bytes = target.read_bytes()
            except OSError as exc:
                return AdoptionOutcome(
                    source=journal.path.name,
                    disposition=AdoptionDisposition.REFUSED_FOREIGN_TARGET,
                    detail=(
                        f"target exists but is unreadable, so it cannot be shown identical: {exc}"
                    ),
                    workflow_id=workflow_id,
                    target=target_name,
                )

        # -- Term 2: READ-BACK against the legacy source, before publishing --
        # AND BEFORE THE SKIP VERDICT. *(Out-of-family review round 1 [P2]: the
        # first draft returned SKIPPED_ALREADY_PUBLISHED from inside the
        # target-exists branch, ABOVE this check — so a lockless pre-#1167
        # straggler appending after the source read produced a confident
        # "already published" over a target that is now STALE relative to its
        # own source. The read-back exists to detect exactly that writer, so no
        # branch may bypass it.)* The read-back is still the final act under the
        # exclusion before anything is published or declared done.
        try:
            read_back = _scalars(journal.path.read_bytes())
        except OSError as exc:
            return AdoptionOutcome(
                source=journal.path.name,
                disposition=AdoptionDisposition.REFUSED_ON_READ_BACK,
                detail=f"legacy source unreadable at read-back: {exc}",
                workflow_id=workflow_id,
                target=target_name,
            )
        if read_back != copied:
            return AdoptionOutcome(
                source=journal.path.name,
                disposition=AdoptionDisposition.REFUSED_ON_READ_BACK,
                detail=(
                    f"legacy source CHANGED inside the [read, read-back] window "
                    f"(record_count {copied[0]}->{read_back[0]}, "
                    f"latest_record_digest {copied[1]}->{read_back[1]}). Target "
                    f"left UNPUBLISHED and NOT declared already-published. NOTE: "
                    f"this check DETECTS interference within that window and "
                    f"NARROWS the residual; it does NOT close it and does NOT "
                    f"cover the mixed-version window, which rests on the "
                    f"mandatory no-mixed-version cutover alone."
                ),
                workflow_id=workflow_id,
                target=target_name,
            )

        if target_bytes is not None:
            if target_bytes == source_bytes:
                return AdoptionOutcome(
                    source=journal.path.name,
                    disposition=AdoptionDisposition.SKIPPED_ALREADY_PUBLISHED,
                    detail=(
                        "target content is IDENTICAL to what this run would "
                        "publish, and the legacy source did not move under the "
                        "exclusion — already published (a whole journal already "
                        "done, or a crash AFTER a prior run's commit, which "
                        "leaves a complete valid target). SKIPPED: never "
                        "republished, never deleted."
                    ),
                    workflow_id=workflow_id,
                    target=target_name,
                )
            return AdoptionOutcome(
                source=journal.path.name,
                disposition=AdoptionDisposition.REFUSED_FOREIGN_TARGET,
                detail=(
                    "target exists with DIFFERENT content — foreign or newer "
                    "state (the record shape is unchanged, so an adopted record "
                    "and an upgraded writer's fresh capture are structurally "
                    "identical). REFUSED rather than overwritten."
                ),
                workflow_id=workflow_id,
                target=target_name,
            )

        # -- Term 3: write-once, crash-atomic, NO-REPLACE publication. -------
        # WRITE-AHEAD: the intent row is durable BEFORE the commit can be, so a
        # crash in between leaves an intent row with no outcome — an unambiguous
        # "in flight when the run stopped" marker naming this exact source and
        # target — rather than a committed target with no record at all.
        _append_intent_row(
            account_path, source=journal.path.name, target=target_name, workflow_id=workflow_id
        )
        try:
            _publish_no_replace(journal_dir, target, source_bytes)
        except FileExistsError:
            return AdoptionOutcome(
                source=journal.path.name,
                disposition=AdoptionDisposition.REFUSED_FOREIGN_TARGET,
                detail=(
                    "the no-replace commit REFUSED: a target appeared between "
                    "the advisory pre-check and the publish. The commit closes "
                    "that time-of-check/time-of-use race BY CONSTRUCTION — "
                    "nothing was overwritten."
                ),
                workflow_id=workflow_id,
                target=target_name,
            )
    return AdoptionOutcome(
        source=journal.path.name,
        disposition=AdoptionDisposition.ADOPTED,
        detail=(
            "relocated: republished at the tenant-composite path with the record "
            "shape UNCHANGED. The legacy source is left untouched and becomes an "
            "unread orphan — the harness never removes it."
        ),
        workflow_id=workflow_id,
        target=target_name,
    )


def _scalars(raw: bytes) -> tuple[int, str | None]:
    """`(record_count, latest_record_digest)` — the two scalars term 2 compares.

    Both already carried on the store's own read result, so **zero new
    persistence is owed**. Computed here over RAW bytes without parsing a record,
    matching the store's own non-blank-raw-line count exactly.
    """
    import hashlib

    lines = [
        line for line in raw.decode("utf-8", errors="surrogateescape").splitlines() if line.strip()
    ]
    if not lines:
        return 0, None
    return len(lines), hashlib.sha256(
        lines[-1].encode("utf-8", errors="surrogateescape")
    ).hexdigest()


def _publish_no_replace(journal_dir: Path, target: Path, data: bytes) -> None:
    """Term 3, on the §14.8.11 publication model already shipped for the
    protected result store: **write aside → make the bytes durable → atomic
    NO-REPLACE commit → make the destination directory entry durable.**

    `os.link` raises `FileExistsError` if the destination exists — the write-once
    guard itself, with no TOCTOU-racy pre-check. **This term is what makes
    stale-over-newer impossible**: if an upgraded deployment has already captured
    a pause at the new key, the adoption cannot publish over it.

    **Crash-atomicity is ABSENT-OR-COMPLETE, in BOTH directions.** A PRE-commit
    crash leaves NO target (the aside file does not match the canonical journal
    name shape, so §13.7 never reports it, and the next run simply republishes).
    A POST-commit crash necessarily leaves a **COMPLETE, VALID** target — which
    the content-equality re-run RECOGNIZES and SKIPS. There is no partial target
    to handle, because one cannot exist.
    """
    fd, tmp_name = tempfile.mkstemp(dir=journal_dir, prefix=_WRITE_ASIDE_PREFIX)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(tmp_name, target)
        # The DESTINATION directory entry is made durable AFTER the commit.
        _fsync_dir(journal_dir)
    finally:
        os.unlink(tmp_name)


def _fsync_dir(directory: Path) -> None:
    """Best-effort directory fsync (no-op where unsupported), matching the store."""
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


def _append_intent_row(account_path: Path, *, source: str, target: str, workflow_id: str) -> None:
    """Append the WRITE-AHEAD `publish-intent` row, durably, before a commit.

    Carries NO disposition — it is not an outcome, and the disposition
    vocabulary's totality is over OUTCOMES. An intent row with no matching
    outcome row for the same `source` is the reconstruction signal: *this
    journal's publication was in flight when the run stopped.*
    """
    _append_row(
        account_path,
        {
            "phase": "publish-intent",
            "source": source,
            "target": target,
            "workflow_id": workflow_id,
        },
    )


def _append_account_row(account_path: Path, outcome: AdoptionOutcome) -> None:
    """Append ONE outcome row, durably. Called for EVERY outcome — totality."""
    row = outcome.as_account_row()
    row["phase"] = "outcome"
    _append_row(account_path, row)


def _append_row(account_path: Path, row: dict[str, object]) -> None:
    """Append one JSONL account row and make it durable — bytes AND dirent.

    **The DIRECTORY entry is fsynced too, and only doing the file is unsound.**
    On the FIRST run the account file is created, and on POSIX an `fsync` of a
    newly-created file does NOT persist its entry in the parent directory — so a
    power loss could leave the adopted target journals durable while the ENTIRE
    account file disappears, which is the state the account exists to make
    impossible. *(Out-of-family review round 2 [P2]; the same reasoning the
    store's own `_append` already applies to its journal dirent.)*
    """
    row = {**row, "recorded_at": datetime.now(UTC).isoformat()}
    # Any directory this call CREATES needs its OWN dirent made durable in ITS
    # parent — fsyncing only `account_path.parent` persists the account file's
    # entry INSIDE a directory whose own entry may still be unflushed, so a power
    # loss could preserve the adopted targets and lose the whole account
    # directory. *(Out-of-family review round 4 [P2].)*
    created = [
        ancestor
        for ancestor in (account_path.parent, *account_path.parent.parents)
        if not ancestor.exists()
    ]
    account_path.parent.mkdir(parents=True, exist_ok=True)
    for directory in reversed(created):
        _fsync_dir(directory.parent)
    with account_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    _fsync_dir(account_path.parent)


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser. Factored for unit-testability."""
    parser = argparse.ArgumentParser(
        prog="python -m harness_runtime.admin.pause_journal_adoption",
        description=(
            "Runtime spec v1.108 §14.14.8 (3b): operator-declared adoption of "
            "LEGACY untenanted pause journals into the tenant-composite key. A "
            "pure RELOCATION — the record shape is unchanged and the legacy "
            "source is left untouched as an orphan. NOT the default: (3a) "
            "abandon-by-default is, because a violated (3a) fails REFUSING "
            "while a violated (3b) fails SILENTLY AND EXECUTES."
        ),
    )
    parser.add_argument(
        "journal_dir",
        type=Path,
        help="The resolved pause-journal directory (<STATE_LEDGER dir>/pause-journal).",
    )
    parser.add_argument(
        "--tenant-id",
        type=str,
        default=None,
        help=(
            "The tenant scope to adopt these records INTO. Omit for the "
            "untenanted target scope. This is a one-time, explicit operator "
            "declaration that the legacy untenanted records in this directory "
            "belong to this tenant — absence of a tenant attribution proves "
            "NOTHING about ownership, so no tenant adopts them implicitly."
        ),
    )
    parser.add_argument(
        "--account-path",
        type=Path,
        default=None,
        help=(
            "Where the durable per-journal account is appended (default: "
            f"<journal-dir>/../{DEFAULT_ACCOUNT_FILENAME})."
        ),
    )
    parser.add_argument(
        "--read-back-only",
        action="store_true",
        help=(
            "Proceed where the exclusion primitive is a documented platform "
            "no-op, relying on read-back verification ALONE. STRICTLY WEAKER: "
            "read-back DETECTS interference inside the [read, read-back] window "
            "but CANNOT EXCLUDE a writer. Without this flag the adoption "
            "REFUSES on such a platform; silent degradation is prohibited."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns a process exit code (0 success / 1 refused / 2 usage)."""
    args = build_parser().parse_args(argv)
    journal_dir: Path = args.journal_dir
    if not journal_dir.is_dir():
        print(f"error: pause-journal directory not found: {journal_dir}", file=sys.stderr)
        return _EXIT_USAGE
    account_path: Path = (
        args.account_path
        if args.account_path is not None
        else journal_dir.parent / DEFAULT_ACCOUNT_FILENAME
    )
    try:
        outcomes = adopt_pause_journals(
            journal_dir,
            tenant_id=args.tenant_id,
            account_path=account_path,
            allow_degraded_exclusion=args.read_back_only,
        )
    except ValueError as exc:  # normalize_tenant_scope refusal
        print(f"adoption refused: {exc}", file=sys.stderr)
        return _EXIT_REFUSED

    counts: dict[str, int] = {}
    for outcome in outcomes:
        counts[outcome.disposition.value] = counts.get(outcome.disposition.value, 0) + 1
    print(f"pause-journal adoption over {journal_dir} — {len(outcomes)} journal(s)")
    for disposition, count in sorted(counts.items()):
        print(f"  {disposition}: {count}")
    print(f"account: {account_path}")
    for outcome in outcomes:
        if outcome.disposition in _REFUSAL_DISPOSITIONS:
            print(f"  refused {outcome.source}: {outcome.detail}", file=sys.stderr)
    refused = any(o.disposition in _REFUSAL_DISPOSITIONS for o in outcomes)
    return _EXIT_REFUSED if refused else _EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
