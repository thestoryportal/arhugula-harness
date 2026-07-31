"""`harness_runtime.admin` — admin CLI surfaces (C-RT-13).

*(Index refreshed at the `B-97`(a) impl leg — council record §10 recorded this
docstring as cosmetically stale, describing "Track A admin surface (both
landed)" and naming three modules where the package holds nine.)*

Read-only surfaces (`harness-inspect`, §13's invariant #1 — MUST NOT write):

- `inspect` (U-RT-47) — read-only state-ledger summary; hosts the §13.5
  audit-signature verification inputs and the §13.7 pause-journal enumeration.
- `inspect_audit_verification` (U-RT-138) — the §13.5 verification body.
- `pause_journal_enumeration` (U-RT-149) — the §13.7 enumeration + the §13.7.1
  three-way classification, shared with the two migration actions below.
- `trace_browser` (C-OD-19 §19.3) — the `--browse` TUI over the span store.

Signal / IPC:

- `shutdown_cli` (U-RT-48) — signal a running instance.
- `pidfile` (U-RT-48) — pidfile IPC primitive (written at stage 7; removed at
  the end of `shutdown()`; read by `harness-shutdown`).

Migration + destructive actions (`python -m`, also dispatched under the flat
`harness <subcommand>` namespace per §13.4):

- `migrate_audit_sidecar` (B-53 / U-RT-139) — audit-sidecar migration.
- `record_migration` (U-RT-139) — the cutover-record authoring/retag body.
- `pause_journal_adoption` (U-RT-149) — the §14.14.8 (3b) operator-declared
  adoption of legacy untenanted pause journals. NOT the default.
- `pause_journal_disposal` (U-RT-149) — the OPTIONAL orphan disposal. Dry-run by
  default; foreclosed from `harness-inspect` by the read-only invariant.

Richer admin IPC is Track B per spec §13.
"""
