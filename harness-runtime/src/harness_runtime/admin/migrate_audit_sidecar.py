"""`python -m harness_runtime.admin.migrate_audit_sidecar` — one-time
pre-sidecar audit-ledger migration.

Codex round-48 P1 on the B-47 PR-B1 landing: `adopt_legacy_is_refs()`
(the round-46 explicit migration for ledgers written before the full-entry
sidecar existed) had no supported invocation path — an operator upgrading in
place could not run it without writing internal Python, so every pre-sidecar
deployment's first audit read or append failed permanently. This module is
that supported path.

**Deliberately NOT registered in `[project.scripts]`** — the operator-facing
CLI inventory is spec-committed (runtime spec §13.4 / §14.18.1); a new
console script is a design-substrate decision. `python -m` invocation keeps
the committed script inventory unchanged while giving upgrades a real
command (registered as a B-47 close-out consideration for the §21.2
persistence-substrate arc).

**Framework discipline** (spec §13 deferred-to-discretion): argparse only,
mirroring `harness_runtime.admin.inspect` / `shutdown_cli`.

Usage::

    python -m harness_runtime.admin.migrate_audit_sidecar <state-ledger.jsonl>

Run ONCE per upgraded deployment, while no harness process is active. The
adoption itself refuses to run when a sidecar already exists (a
missing-entry condition on an existing sidecar is loss, not legacy — the
round-36 fail-loud posture is unchanged).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.state_ledger_entry_schema import Actor, ActorClass

from harness_runtime.lifecycle.audit_writer import RuntimeAuditLedgerWriter
from harness_runtime.lifecycle.state_ledger import LedgerWriter

__all__ = ["build_parser", "main"]


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser. Factored for unit-testability."""
    parser = argparse.ArgumentParser(
        prog="python -m harness_runtime.admin.migrate_audit_sidecar",
        description=(
            "One-time migration for IS state ledgers written BEFORE the "
            "B-47 full-entry audit sidecar existed: baselines every "
            "existing audit: reference as legacy (full entries "
            "unrecoverable by construction) so reads and appends stop "
            "failing loud. Refuses to run when a sidecar already exists."
        ),
    )
    parser.add_argument(
        "ledger",
        type=Path,
        help="Path to the deployment's state-ledger JSONL file.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns a process exit code (0 success / 1 refused / 2 usage)."""
    args = build_parser().parse_args(argv)
    ledger_path: Path = args.ledger.resolve()
    if not ledger_path.is_file():
        print(f"error: ledger file not found: {ledger_path}", file=sys.stderr)
        return 2
    # Construct the handle directly, mirroring `admin.inspect._read_entries`
    # — no `initialize_jsonl_event_ledger` (which would mkdir/create on a
    # mistyped path).
    text = ledger_path.read_text()
    entry_count = sum(1 for line in text.splitlines() if line.strip())
    writer = RuntimeAuditLedgerWriter(
        ledger_writer=LedgerWriter(
            handle=JsonlLedgerHandle(
                canonical_path=ledger_path,
                exists=True,
                entry_count=entry_count,
            ),
            actor=Actor(
                actor_class=ActorClass.OPERATOR,
                actor_id="migrate-audit-sidecar",
            ),
        ),
        time_source=lambda: datetime.now(UTC),
    )
    try:
        baselined = writer.adopt_legacy_is_refs()
    except ValueError as exc:
        print(f"migration refused: {exc}", file=sys.stderr)
        return 1
    print(f"baselined {baselined} legacy audit reference(s) at {writer.sidecar_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
