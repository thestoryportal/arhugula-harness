"""`python -m harness_runtime.admin.pause_journal_disposal` — the OPTIONAL
disposal of orphaned legacy pause journals.

Runtime spec v1.108 §14.14.8 *"ORPHANED JOURNALS"* + §13.4 (the NEW CONDITIONAL
admin destructive-action row) + §13.7 term 6. Council condition `K-13`.

**The orphan statement, both halves.** Journals orphaned at the retired key are
**RETAINED INDEFINITELY and are NEVER RECLAIMED BY THE HARNESS** — no pruner is
specified and none is owed. And: the append-only / never-truncated invariant
governs the records of a **LIVE** journal and does **not** extend to a
retired-key orphan; **an operator MAY remove one, and the harness will never do
so on its own.** This module is that operator's hands, never the harness's.

**A retention POLICY — a default, a tunable, a sweep trigger — is a FOLLOW-ON
ARC and is explicitly NOT owed here.** A lifecycle subsystem must not be grafted
onto a keying change. Nothing in this module runs on a schedule, at bootstrap, at
shutdown, or on any harness path; it runs when an operator types it.

**Why this is a SEPARATE action and not a `harness-inspect` mode.** §13.7 term 6:
`harness-inspect` MUST NOT write to any file (the §13 read-only invariant,
untouched), so *"a DISPOSAL action is a destructive write and is therefore
FORECLOSED FROM THAT SURFACE BY THAT INVARIANT"*. It lives here, on the
`migrate-audit-sidecar` precedent.

**Two terms bind it** (§14.14.8):

1. **DRY-RUN BY DEFAULT.** Nothing is removed absent an explicit non-dry-run
   flag. The default invocation reports what WOULD be removed and exits.
2. **REFUSES WHILE (3b) ADOPTION REMAINS POSSIBLE** — i.e. while any enumerated
   journal still classifies LEGACY — absent an explicit operator acknowledgement
   that recoverable state is being discarded. *An operator who upgrades, learns
   from §13.7 that pauses were abandoned, and reaches for disposal must not
   thereby destroy their only (3b) recovery path using the very tool that told
   them the records existed.*

Any confirmation here is an **in-command confirmation, not a HITL gate** —
gating an operator-invoked migration on an operator approval is empty ritual.

Usage::

    python -m harness_runtime.admin.pause_journal_disposal <journal-dir>
    python -m harness_runtime.admin.pause_journal_disposal <journal-dir> --delete \\
        --acknowledge-discarding-recoverable-state
    harness dispose-pause-journals <journal-dir>
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from harness_runtime.admin.pause_journal_enumeration import (
    EnumeratedJournal,
    enumerate_pause_journals,
)
from harness_runtime.lifecycle.journal_workflow_pause_store import PAUSE_JOURNAL_LOCK_SUFFIX
from harness_runtime.lifecycle.protected_result_store import normalize_tenant_scope

__all__ = ["build_parser", "main", "plan_disposal"]

_EXIT_OK = 0
_EXIT_REFUSED = 1
_EXIT_USAGE = 2


def plan_disposal(
    journal_dir: Path, *, tenant_id: str | None
) -> tuple[list[EnumeratedJournal], list[EnumeratedJournal]]:
    """Return `(orphans, retained)` for `journal_dir`.

    **`orphans` is the LEGACY-classified set and NOTHING ELSE**, because that is
    precisely what §14.14.8's orphan statement scopes this action to: *"journals
    ORPHANED AT THE RETIRED KEY"*. `retained` is every other enumerated journal —
    never a candidate for removal on any flag.

    **The orphan class and the (3b)-recoverable class are THE SAME SET**, which
    is exactly why the refuse-while-recoverable term exists: a LEGACY journal is
    simultaneously the thing an adoption can still relocate and the only thing
    this action may ever delete. There is no third category that is safe to
    delete without acknowledgement, and treating one as if there were is how a
    disposal tool destroys live state.

    *(Corrected at out-of-family review round 1 [P1]. The first draft computed
    the delete set as `not adoptable`, which is the exact INVERSE — it swept in
    this deployment's own CURRENT-FORMAT live journals, a CO-TENANT's valid
    journals, and every unreadable-identity row, and would have removed all of
    them under `--delete` with no acknowledgement at all, since none of them
    counts as "recoverable" under that reading. The bug's shape is worth naming:
    a predicate that reads as "everything not worth saving" is never a safe
    deletion set — only a predicate that PROVES orphanhood is.)*
    """
    tenant_scope = normalize_tenant_scope(tenant_id)
    journals = enumerate_pause_journals(journal_dir, tenant_scope=tenant_scope)
    orphans = [journal for journal in journals if journal.adoptable]
    retained = [journal for journal in journals if not journal.adoptable]
    return orphans, retained


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser. Factored for unit-testability."""
    parser = argparse.ArgumentParser(
        prog="python -m harness_runtime.admin.pause_journal_disposal",
        description=(
            "Runtime spec v1.108 §14.14.8 (OPTIONAL): operator-invoked disposal "
            "of orphaned pause journals. DRY-RUN BY DEFAULT. Refuses while a "
            "(3b) adoption could still recover LEGACY records, absent an "
            "explicit acknowledgement that recoverable state is discarded. The "
            "harness NEVER reclaims a journal on its own."
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
            "This deployment's tenant scope, used ONLY to classify what it finds "
            "(§13.7.1). Omit for the untenanted deployment."
        ),
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help=(
            "Actually remove. WITHOUT this flag the action is a DRY RUN and "
            "removes nothing — the default, deliberately."
        ),
    )
    parser.add_argument(
        "--acknowledge-discarding-recoverable-state",
        action="store_true",
        help=(
            "Explicit acknowledgement that LEGACY journals a (3b) adoption "
            "could still relocate are being DESTROYED. Required to proceed "
            "while any such journal remains."
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
    try:
        orphans, retained = plan_disposal(journal_dir, tenant_id=args.tenant_id)
    except OSError as exc:
        print(f"error: pause-journal directory unreadable: {exc}", file=sys.stderr)
        return _EXIT_USAGE
    except ValueError as exc:  # normalize_tenant_scope refusal
        print(f"disposal refused: {exc}", file=sys.stderr)
        return _EXIT_REFUSED

    # **THE DELETE SET IS THE ORPHAN SET, AND ONLY THAT.** Everything else the
    # enumeration found — this deployment's own CURRENT-FORMAT journals, a
    # co-tenant's journals, and any journal whose identity is unreadable and
    # therefore UNPROVEN — is retained unconditionally. No flag widens this.
    targets = orphans

    # -- Term 1: DRY RUN BY DEFAULT — and it runs FIRST. --------------------
    # The refuse-while-recoverable gate below guards the DESTRUCTIVE act, never
    # the PREVIEW. Ordering it first made the default invocation refuse on
    # exactly the directory the tool exists for — every LEGACY journal is both
    # the only disposal candidate AND the thing that triggers the refusal — so
    # an operator had to acknowledge destroying recoverable state merely to SEE
    # what would be destroyed. That is a dry run in name only. *(Out-of-family
    # review round 2 [P2].)*
    if not args.delete:
        print(f"pause-journal disposal — DRY RUN over {journal_dir}. Nothing removed.")
        for journal in targets:
            records = "UNREADABLE" if journal.record_count is None else journal.record_count
            print(f"  would remove: {journal.path.name} (records={records})")
        for journal in retained:
            classification = (
                journal.classification.value
                if journal.classification is not None
                else "identity-absent"
            )
            print(
                f"  RETAINED (never a disposal candidate): {journal.path.name} [{classification}]"
            )
        print(f"  {len(targets)} journal(s) would be removed; pass --delete to proceed.")
        if targets and not args.acknowledge_discarding_recoverable_state:
            print(
                f"  NOTE: all {len(targets)} are LEGACY and a (3b) adoption could still "
                f"relocate them, so --delete alone will REFUSE; "
                f"--acknowledge-discarding-recoverable-state is required to proceed."
            )
        return _EXIT_OK

    # -- Term 2: REFUSE WHILE (3b) ADOPTION REMAINS POSSIBLE. ---------------
    if orphans and not args.acknowledge_discarding_recoverable_state:
        print(
            f"disposal refused: {len(orphans)} journal(s) classify LEGACY and a "
            f"(3b) adoption could still relocate them. Adopt them first "
            f"(python -m harness_runtime.admin.pause_journal_adoption), or pass "
            f"--acknowledge-discarding-recoverable-state to destroy recoverable "
            f"state deliberately. Nothing was removed.",
            file=sys.stderr,
        )
        return _EXIT_REFUSED

    removed = _remove(targets, journal_dir)
    print(f"pause-journal disposal over {journal_dir} — removed {removed} journal(s)")
    return _EXIT_OK


def _remove(targets: list[EnumeratedJournal], journal_dir: Path) -> int:
    """Unlink the orphan set and make the REMOVALS durable.

    An unlink is a directory-entry change like any other: without an fsync of
    the directory afterwards the command can report success and the orphan can
    REAPPEAR after a power loss — a disposal tool whose deletions do not survive
    a reboot is worse than one that refuses. *(Out-of-family review round 4
    [P3]; the same reasoning the store's own append path applies to its dirent
    CREATION, in the other direction.)*
    """
    removed = 0
    for journal in targets:
        journal.path.unlink()
        # The dedicated advisory-lock sibling the append path created with
        # O_CREAT and never unlinks is removed WITH its journal — leaving it
        # would strand a lock file guarding a file that no longer exists. It is
        # a LOCK file, never a canonical one: it carries no bytes and nothing
        # reads it, so removing it discards no state.
        lock = journal.path.with_name(journal.path.name + PAUSE_JOURNAL_LOCK_SUFFIX)
        lock.unlink(missing_ok=True)
        removed += 1
    _fsync_dir(journal_dir)
    return removed


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
    return _EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
