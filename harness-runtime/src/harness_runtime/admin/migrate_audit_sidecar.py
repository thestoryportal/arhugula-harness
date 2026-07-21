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
import json
import sys
from collections.abc import Sequence
from typing import cast
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
    # -- U-RT-139 record modes (Runtime plan v2.49 §1.7) --------------------
    parser.add_argument(
        "--retag",
        action="store_true",
        help=(
            "Record-driven retag mode (OD v1.34 §21.2.1 row 6): AUTHENTICATE "
            "the configured cutover record, then rewrite '_single'-tagged "
            "sidecar rows the record dispositions tenant-readable to their "
            "attested tenant_scope (entry content and entry_hash "
            "byte-unchanged; quarantined rows never retagged; all-or-nothing)."
        ),
    )
    parser.add_argument(
        "--author",
        action="store_true",
        help=(
            "Record AUTHORING mode: compose the cutover record from every "
            "observed pre-cutover identity, validate, sign under the pinned "
            "record key, and emit it at the configured "
            "audit_cutover_record_path. Requires --attestation and/or "
            "--tofu-quarantine to cover every '_single' identity."
        ),
    )
    parser.add_argument(
        "--runtime-config",
        type=Path,
        default=None,
        help=(
            "Authoritative RuntimeConfig TOML (REQUIRED for --retag/--author): "
            "supplies the record-trust triple (audit_cutover_record_path / "
            "audit_cutover_record_key_id / audit_ledger_binding_id) and the "
            "audit-signing backend selection."
        ),
    )
    parser.add_argument(
        "--attestation",
        type=Path,
        default=None,
        help=(
            "Authoring input: JSON object mapping entry_hash to the attested "
            "tenant for '_single' identities (the OD v1.34 §21.2.2 row-5 "
            "external authoritative mapping / per-identity attestation)."
        ),
    )
    parser.add_argument(
        "--tofu-quarantine",
        type=str,
        default=None,
        metavar="TENANT",
        help=(
            "Authoring input: declared-TOFU decision — QUARANTINE every "
            "unattested '_single' identity under TENANT (quarantined rows are "
            "never retagged and never pass verification)."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns a process exit code (0 success / 1 refused / 2 usage)."""
    args = build_parser().parse_args(argv)
    ledger_path: Path = args.ledger.resolve()
    if not ledger_path.is_file():
        print(f"error: ledger file not found: {ledger_path}", file=sys.stderr)
        return 2
    if args.retag or args.author:
        return _run_record_mode(args, ledger_path)
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


def _run_record_mode(args: argparse.Namespace, ledger_path: Path) -> int:
    """U-RT-139 record modes — authoring and/or retag (authoring first when
    both are requested, so a single invocation can author-then-retag)."""
    from harness_runtime.admin.record_migration import (
        RecordMigrationError,
        author_cutover_record,
        retag_sidecar,
    )
    from harness_runtime.config.audit_signing import make_audit_signing_backend
    from harness_runtime.config_source import RuntimeConfigLoadError, RuntimeConfigSource
    from harness_runtime.lifecycle.audit_writer import AUDIT_SIDECAR_FILENAME

    if args.runtime_config is None:
        print(
            "error: --retag/--author require --runtime-config (the record-trust "
            "triple and signing-backend selection are config-anchored, never "
            "inferred)",
            file=sys.stderr,
        )
        return 2
    try:
        config = RuntimeConfigSource.load(config_file=args.runtime_config)
    except RuntimeConfigLoadError as exc:
        print(f"error: --runtime-config unusable: {exc}", file=sys.stderr)
        return 2
    backend = make_audit_signing_backend(config.audit_signing)
    if backend is None:
        print(
            'error: the config selects no audit-signing backend (backend="none") '
            "— record modes require the configured backend to authenticate/sign "
            "the trust anchor",
            file=sys.stderr,
        )
        return 2
    sidecar_path = ledger_path.parent / AUDIT_SIDECAR_FILENAME

    attestation: dict[str, str] = {}
    if args.attestation is not None:
        try:
            parsed = json.loads(args.attestation.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"error: --attestation unusable: {exc}", file=sys.stderr)
            return 2
        if not isinstance(parsed, dict) or not all(
            isinstance(k, str) and isinstance(v, str)
            for k, v in cast("dict[object, object]", parsed).items()
        ):
            print(
                "error: --attestation must be a JSON object mapping entry_hash "
                "strings to tenant strings",
                file=sys.stderr,
            )
            return 2
        attestation = cast("dict[str, str]", parsed)

    try:
        if args.author:
            record = author_cutover_record(
                config,
                sidecar_path=sidecar_path,
                signing_backend=backend,
                attestation=attestation,
                tofu_quarantine_tenant=args.tofu_quarantine,
            )
            print(
                f"authored cutover record with {len(record.rows)} row(s) at "
                f"{config.audit_cutover_record_path}"
            )
        if args.retag:
            outcome = retag_sidecar(config, sidecar_path=sidecar_path, signing_backend=backend)
            print(
                f"retagged {outcome.retagged} row(s); "
                f"{outcome.quarantined_left} quarantined left '_single'; "
                f"{outcome.already_tagged_left} already-tagged untouched; "
                f"{outcome.baseline_aliased} baseline pair(s) alias-projected "
                f"(nothing rewritten on disk for baselines)"
            )
    except RecordMigrationError as exc:
        print(f"record migration refused: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
