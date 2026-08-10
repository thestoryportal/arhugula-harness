# CLAUDE.md §2 Artifact Pointer Lineage — resolving stub

*This file used to carry the full relocated §2 change-note lineage inline
(414,855 B, one path). Per the U-CTX-06 R-CTX-1 context-optimization arc
(2026-08-10), that content is now split byte-preservingly by family under
`.harness/artifact-pointers/` — query the relevant family file directly
instead of loading this whole lineage. Root `CLAUDE.md` §2 keeps the operative
pointer index; load a family file only when exact per-axis artifact history is
needed.*

## Family files

| File | Carries |
|---|---|
| `.harness/artifact-pointers/is.md` | IS §2.3 spec pointer + §2.4 plan pointer |
| `.harness/artifact-pointers/as.md` | AS §2.3 spec pointer + §2.4 plan pointer |
| `.harness/artifact-pointers/cp.md` | CP §2.3 spec pointer + §2.4 plan pointer + the 2026-07-13..07-25 multi-axis dated change-note block (CP-plurality routing) |
| `.harness/artifact-pointers/od.md` | OD §2.3 spec pointer + §2.4 plan pointer |
| `.harness/artifact-pointers/runtime.md` | Runtime §2.3 spec pointer + §2.4 plan pointer + the `B-69`/`B-97`/`B-104`+`B-98` dated change-note lineage blocks |
| `.harness/artifact-pointers/cxa.md` | CXA §2.4 plan pointer (no dedicated §2.3 spec row — CXA is Phase 6 only) |
| `.harness/artifact-pointers/memory.md` | Memory ADR-D7 + spec + plan relocated dated lineage (this pointer file predates Memory's own §2.3/§2.4 table row — see file for the live-pointer redirect to root `CLAUDE.md`) |
| `.harness/artifact-pointers/plans.md` | §2.1 governance + execution discipline, §2.2 ADR/ADD/PRD, §2.5 axis `CLAUDE.md` pointers, the `core` Implementation Plan pointer, and the 2026-07-30 relocation banner |

Query, do not read wholesale: `rg <term> .harness/artifact-pointers/*.md` for a
specific artifact/version/`B-`-id, rather than loading every family file.

## Other `.harness` working-set surfaces — query, not Read

These carry their own live-derivation tooling; read the derived/rendered
output or query the tool, not the raw ledger file, when only a specific
row/status is needed:

- **`.harness/forward-register.yaml`** — the `B-*` forward register. Query via
  `uv run python tools/forward_register.py <subcommand>` (or `just
  forward-register-check` for the `--check` gate) rather than reading the YAML
  directly for a single row's status.
- **`.harness/loop_status.md`** — the append-only autonomous-loop ledger.
  Written/read via `tools/hooks/loop_lib.sh`'s `loop_status_path` +
  `loop_log`/`loop_skip_set` helpers; grep for a specific item-id or run rather
  than reading the whole ledger.
- **`.harness/arc-ledger.yaml`** — the R-FS-1 arc/unit map. Query via `uv run
  python tools/arc_ledger.py --summary` (or `--check` for the CI validation
  gate; no `just` wrapper exists) rather than reading the YAML directly for a
  single arc/unit's status.
