# U-RT-47 — `harness-inspect` admin stub

**Status:** in-progress
**Spec:** `Spec_Harness_Runtime_v1.md` v1.1 §13 (C-RT-13 admin stub semantics)
**Decomposition:** L10 U-RT-47
**Predecessor:** U-RT-46 (commit `10a6bca`), chain_hash fix `645053c`

---

## Scope

Lands the `harness-inspect` CLI: read-only summary of state ledger
contents. Per C-RT-13 invariants:

- MUST NOT write to any file (tested by chmod-readonly fixture).
- Runs against a **stopped harness** — no bootstrap, no HarnessContext.
- argparse stdlib (no click/typer per framework discipline).

## ACs (per session-3 decomposition)

| AC | Status | Materialization |
|---|---|---|
| Runs against stopped harness | LAND | reads filesystem; no process required |
| Returns ledger head | LAND | last entry's `response_hash.hex()` via `_entry_head_hash` from fix commit |
| Returns last N spans | **STRUCK** | extends `[[fork-trace-storage-pathclass-gap]]` — collector sqlite is in-memory-only per U-RT-30 PARTIAL-LAND; no on-disk store to read |

## CLI

```
harness-inspect [--ledger-path PATH] [--collector-path PATH] [--last-n INT] [--json]
```

| Flag | Default | Effect |
|---|---|---|
| `--ledger-path` | `.harness/state.jsonl` | path to state ledger JSONL |
| `--collector-path` | none | accepted but reported as N/A at HEAD |
| `--last-n` | 10 | number of recent entries to dump |
| `--json` | off | switch to JSON output |

Exit codes per C-RT-13:
- `0` — success
- `2` — `RT-FAIL-INSPECT-PATH` (file not found / unreadable)

## Files

- `harness-runtime/src/harness_runtime/admin/__init__.py` (NEW, empty marker)
- `harness-runtime/src/harness_runtime/admin/inspect.py` (NEW, ~150 LOC) —
  `main(argv: list[str] | None = None) -> int`, argparse, ledger read,
  human + JSON output.
- `harness-runtime/pyproject.toml` — activate `[project.scripts]` entry.
- `harness-runtime/tests/test_admin_inspect.py` (NEW, ~12 tests).

## Read path

Reuses the `_entry_head_hash` helper (fix commit) for the head hash.
Reads entries directly via:

```python
from harness_is.state_ledger_write import read_ledger
from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle

entry_count = sum(1 for line in path.read_text().splitlines() if line.strip())
handle = JsonlLedgerHandle(canonical_path=path, exists=True, entry_count=entry_count)
entries = read_ledger(handle)
```

`JsonlLedgerHandle` is plain pydantic with 3 fields; `read_ledger` only
needs `canonical_path`. No bootstrap-time side effects.

## Test plan (~12 tests)

1. `test_inspect_smoke` — point at a tmp_path ledger with 2 entries; main returns 0.
2. `test_inspect_reports_head_hash_lowercase_hex` — verify head hash output.
3. `test_inspect_default_last_n_is_10` — write 15 entries; expect 10 in output.
4. `test_inspect_respects_last_n_flag` — `--last-n 3` writes 5 entries → 3 in output.
5. `test_inspect_json_flag_outputs_json` — `--json` produces valid JSON.
6. `test_inspect_human_output_includes_struck_spans_note` — non-JSON output names the fork.
7. `test_inspect_json_includes_struck_spans_field` — JSON has `"spans": null` + `"spans_unavailable_reason"`.
8. `test_inspect_empty_ledger_reports_genesis` — 0 entries case.
9. `test_inspect_missing_path_exits_nonzero` — bad path → exit 2.
10. `test_inspect_readonly_fixture_no_writes_attempted` — chmod 0o444 on ledger path; inspect succeeds (RO read).
11. `test_inspect_does_not_write_anywhere` — sentinel monkey-patches `open()` for write mode; inspect must not trip it.
12. `test_inspect_pyproject_scripts_entry_present` — read pyproject.toml; assert `harness-inspect = ...:main` line.

## Out-of-scope

- Last N spans (AC #3 STRUCK; deferred to fork resolution).
- Cost-attribution rollup (stateless-by-design per U-RT-31; report "N/A").
- `--collector-path` actual read (accepted; reported N/A).
- pidfile reading (that's U-RT-48 shutdown-cli scope).
