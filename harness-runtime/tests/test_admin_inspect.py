"""U-RT-47 — `harness-inspect` admin CLI tests.

Acceptance criteria per Phase 2 Session 3 atomic decomposition L10 U-RT-47 +
spec §13 C-RT-13:

- AC #1: runs against a stopped harness — LAND
- AC #2: returns ledger head — LAND
- AC #3: returns last N spans — STRUCK per `[[fork-trace-storage-pathclass-gap]]`

C-RT-13 invariant: `harness-inspect` MUST NOT write to any file.
"""

from __future__ import annotations

import json
import os
import stat
from datetime import UTC, datetime
from pathlib import Path

import pytest
from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.state_ledger_entry_schema import (
    Actor,
    ActorClass,
    Identifier,
    StateLedgerEntry,
)
from harness_is.state_ledger_write import (
    EntryPayload,
    WriteKey,
    append_ledger_entry,
)
from harness_runtime.admin.inspect import build_parser, main

# ---------------------------------------------------------------------------
# Fixtures.
# ---------------------------------------------------------------------------


_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="harness-runtime")


def _write_n_entries(ledger_path: Path, n: int) -> list[StateLedgerEntry]:
    """Build a ledger at `ledger_path` with `n` chain-valid entries.

    Uses the real `append_ledger_entry` API so chain construction matches
    production semantics.
    """
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.touch()
    handle = JsonlLedgerHandle(
        canonical_path=ledger_path,
        exists=True,
        entry_count=0,
    )
    entries: list[StateLedgerEntry] = []
    for i in range(n):
        payload = EntryPayload(
            action_id=Identifier(f"action-{i}"),
            idempotency_key=Identifier(f"idem-{i}"),
            actor=_ACTOR,
            timestamp=datetime(2026, 5, 20, 12, 0, i, tzinfo=UTC),
        )
        write_key = WriteKey(
            thread_id=Identifier(f"thread-{i}"),
            step_id=Identifier(f"step-{i}"),
            idempotency_key=Identifier(f"idem-{i}"),
        )
        append_ledger_entry(handle, payload, write_key)
        # Re-read handle counter so chain construction picks up prior entries.
        new_count = sum(1 for line in ledger_path.read_text().splitlines() if line.strip())
        handle = JsonlLedgerHandle(
            canonical_path=ledger_path,
            exists=True,
            entry_count=new_count,
        )
    # Final read for test-side reference.
    from harness_is.state_ledger_write import read_ledger

    entries.extend(read_ledger(handle))
    return entries


# ---------------------------------------------------------------------------
# Parser.
# ---------------------------------------------------------------------------


def test_parser_defaults() -> None:
    ns = build_parser().parse_args([])
    assert ns.ledger_path == Path(".harness/state.jsonl")
    assert ns.last_n == 10
    assert ns.json is False
    assert ns.collector_path is None
    assert ns.browse is False


def test_parser_flags() -> None:
    ns = build_parser().parse_args(["--ledger-path", "/tmp/x.jsonl", "--last-n", "3", "--json"])
    assert ns.ledger_path == Path("/tmp/x.jsonl")
    assert ns.last_n == 3
    assert ns.json is True


# ---------------------------------------------------------------------------
# Happy path.
# ---------------------------------------------------------------------------


def test_inspect_smoke(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ledger = tmp_path / "state.jsonl"
    entries = _write_n_entries(ledger, 2)

    code = main(["--ledger-path", str(ledger)])
    out = capsys.readouterr().out

    assert code == 0
    assert "harness-inspect" in out
    assert entries[-1].response_hash.hex() in out


def test_inspect_reports_head_hash_lowercase_hex(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    ledger = tmp_path / "state.jsonl"
    entries = _write_n_entries(ledger, 3)

    main(["--ledger-path", str(ledger)])
    out = capsys.readouterr().out

    head = entries[-1].response_hash.hex()
    assert head in out
    assert head == head.lower()  # lowercase invariant
    assert len(head) == 64  # SHA-256


def test_inspect_default_last_n_is_10(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 15)

    main(["--ledger-path", str(ledger)])
    out = capsys.readouterr().out

    # First 5 entries (action-0..action-4) should NOT appear; entries 5..14 should.
    assert "action-0 " not in out and "action-0'" not in out
    assert "action-14" in out


def test_inspect_respects_last_n_flag(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 5)

    main(["--ledger-path", str(ledger), "--last-n", "3"])
    out = capsys.readouterr().out

    # action-2, action-3, action-4 only (last 3 of 5).
    assert "action-4" in out
    assert "action-3" in out
    assert "action-2" in out
    assert "action-1" not in out
    assert "action-0" not in out


def test_inspect_last_n_zero_prints_no_entries(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Regression guard — `--last-n 0` must print ZERO entries, not every
    entry. Python's `list[-0:]` is the same as `list[0:]` (the whole list),
    since `-0 == 0`; the header already correctly computed `min(0, ...) = 0`
    but the loop below it used to dump the entire ledger anyway."""
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 5)

    main(["--ledger-path", str(ledger), "--last-n", "0"])
    out = capsys.readouterr().out

    assert "Last 0 entries:" in out
    for i in range(5):
        assert f"action-{i}" not in out


def test_inspect_json_last_n_zero_returns_empty_entries(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 5)

    main(["--ledger-path", str(ledger), "--json", "--last-n", "0"])
    out = capsys.readouterr().out

    payload = json.loads(out)
    assert payload["total_entries"] == 5
    assert payload["entries"] == []


# ---------------------------------------------------------------------------
# JSON output.
# ---------------------------------------------------------------------------


def test_inspect_json_flag_outputs_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 2)

    main(["--ledger-path", str(ledger), "--json"])
    out = capsys.readouterr().out

    payload = json.loads(out)
    assert payload["total_entries"] == 2
    assert isinstance(payload["head_hash"], str)
    assert len(payload["head_hash"]) == 64
    assert payload["spans"] is None
    assert "fork-trace-storage-pathclass-gap" in payload["spans_unavailable_reason"]
    assert payload["cost_rollup"] is None
    assert len(payload["entries"]) == 2


def test_inspect_json_empty_ledger(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ledger = tmp_path / "state.jsonl"
    ledger.write_text("")

    main(["--ledger-path", str(ledger), "--json"])
    out = capsys.readouterr().out

    payload = json.loads(out)
    assert payload["total_entries"] == 0
    assert payload["head_hash"] is None
    assert payload["entries"] == []


# ---------------------------------------------------------------------------
# Human output references the struck spans surface.
# ---------------------------------------------------------------------------


def test_inspect_human_output_names_struck_spans(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)

    main(["--ledger-path", str(ledger)])
    out = capsys.readouterr().out

    assert "Spans:" in out
    assert "fork-trace-storage-pathclass-gap" in out
    assert "U-RT-30 PARTIAL-LAND" in out


def test_inspect_human_output_names_struck_cost(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)

    main(["--ledger-path", str(ledger)])
    out = capsys.readouterr().out

    assert "Cost rollup:" in out
    assert "U-RT-31" in out


# ---------------------------------------------------------------------------
# Error paths.
# ---------------------------------------------------------------------------


def test_inspect_missing_path_exits_nonzero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ledger = tmp_path / "does-not-exist.jsonl"

    code = main(["--ledger-path", str(ledger)])

    assert code == 2
    err = capsys.readouterr().err
    assert "RT-FAIL-INSPECT-PATH" in err


def test_inspect_empty_ledger_reports_genesis(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ledger = tmp_path / "state.jsonl"
    ledger.write_text("")

    code = main(["--ledger-path", str(ledger)])
    out = capsys.readouterr().out

    assert code == 0
    assert "genesis" in out.lower()


# ---------------------------------------------------------------------------
# Read-only invariant (C-RT-13 invariant #1).
# ---------------------------------------------------------------------------


def test_inspect_succeeds_against_readonly_ledger(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """chmod 0o444 the ledger; inspect must still read it cleanly."""
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 2)
    # Strip write bits.
    ledger.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    try:
        code = main(["--ledger-path", str(ledger)])
        assert code == 0
    finally:
        # Restore to clean up tmp_path.
        ledger.chmod(stat.S_IRUSR | stat.S_IWUSR)


def test_inspect_does_not_open_anything_for_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Sentinel-monkey-patch `Path.open` and `os.open` to detect write attempts."""
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)

    from typing import Any

    real_path_open: Any = Path.open
    real_os_open: Any = os.open
    write_attempts: list[str] = []

    def _spy_path_open(self: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if any(c in mode for c in ("w", "a", "x", "+")):
            write_attempts.append(f"Path.open({self}, mode={mode!r})")
        return real_path_open(self, mode, *args, **kwargs)

    def _spy_os_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
        write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
        if flags & write_flags:
            write_attempts.append(f"os.open({path}, flags={flags})")
        return real_os_open(path, flags, *args, **kwargs)  # type: ignore[no-any-return]

    monkeypatch.setattr(Path, "open", _spy_path_open)
    monkeypatch.setattr(os, "open", _spy_os_open)

    code = main(["--ledger-path", str(ledger)])

    assert code == 0
    assert write_attempts == [], f"unexpected write attempts: {write_attempts}"


# ---------------------------------------------------------------------------
# --browse (B-OD19-LOCAL-INSPECTION slice a — C-OD-19 §19.3 TUI trace browser).
# ---------------------------------------------------------------------------


def test_browse_without_collector_path_exits_nonzero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = main(["--browse"])
    err = capsys.readouterr().err
    assert code == 2
    assert "RT-FAIL-INSPECT-PATH" in err
    assert "--collector-path" in err


def test_browse_missing_collector_db_exits_nonzero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "does-not-exist.db"
    code = main(["--browse", "--collector-path", str(missing)])
    err = capsys.readouterr().err
    assert code == 2
    assert "RT-FAIL-INSPECT-PATH" in err


def test_browse_non_span_store_db_exits_nonzero_instead_of_crashing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A sqlite file that exists but has no `spans` table (e.g. an empty
    file, or the wrong db) must exit cleanly with RT-FAIL-INSPECT-PATH —
    not raise `sqlite3.OperationalError` from inside `curses.wrapper`."""
    import curses

    db_path = tmp_path / "not-a-span-store.db"
    db_path.write_bytes(b"")  # a valid-enough sqlite file with no schema

    called = False

    def _fake_wrapper(func: object, *args: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(curses, "wrapper", _fake_wrapper)

    code = main(["--browse", "--collector-path", str(db_path)])
    err = capsys.readouterr().err

    assert code == 2
    assert "RT-FAIL-INSPECT-PATH" in err
    assert called is False  # never reached curses


def test_browse_non_sqlite_file_exits_nonzero_instead_of_crashing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A file that exists but isn't a SQLite database at all (operator typo
    pointing --collector-path at the wrong file) raises `sqlite3.DatabaseError`
    ("file is not a database") on the first read, not `OperationalError` —
    must still exit cleanly with RT-FAIL-INSPECT-PATH."""
    import curses

    db_path = tmp_path / "not-sqlite-at-all.db"
    db_path.write_text("not a sqlite database")

    called = False

    def _fake_wrapper(func: object, *args: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(curses, "wrapper", _fake_wrapper)

    code = main(["--browse", "--collector-path", str(db_path)])
    err = capsys.readouterr().err

    assert code == 2
    assert "RT-FAIL-INSPECT-PATH" in err
    assert called is False  # never reached curses


def test_browse_wrong_schema_db_exits_nonzero_instead_of_crashing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A sqlite file with a `spans` table but the WRONG columns (e.g. a stale
    collector db from an older schema) must also exit cleanly — the fix runs
    the real rollup query (not just `SELECT 1 FROM spans`) before curses."""
    import curses
    import sqlite3

    db_path = tmp_path / "wrong-schema.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE spans (span_id TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

    called = False

    def _fake_wrapper(func: object, *args: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(curses, "wrapper", _fake_wrapper)

    code = main(["--browse", "--collector-path", str(db_path)])
    err = capsys.readouterr().err

    assert code == 2
    assert "RT-FAIL-INSPECT-PATH" in err
    assert called is False  # never reached curses


def test_browse_opens_readonly_and_dispatches_to_curses_wrapper(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`--browse` opens the sqlite store read-only, computes the rollups, and
    hands off to `curses.wrapper(run_trace_browser_tui, rollups)` — verified
    by monkeypatching `curses.wrapper` (no real terminal available under
    pytest)."""
    import curses

    from harness_od.sqlite_span_store import initialize_span_store

    db_path = tmp_path / "spans.db"
    initialize_span_store(db_path).close()

    calls: list[tuple[object, tuple[object, ...]]] = []

    def _fake_wrapper(func: object, *args: object) -> None:
        calls.append((func, args))

    monkeypatch.setattr(curses, "wrapper", _fake_wrapper)

    code = main(["--browse", "--collector-path", str(db_path)])

    assert code == 0
    assert len(calls) == 1
    func, args = calls[0]
    assert getattr(func, "__name__", None) == "run_trace_browser_tui"
    assert len(args) == 1
    (rollups,) = args
    assert len(rollups) == 5  # the 5 operator-burden eval primitives


# ---------------------------------------------------------------------------
# pyproject scripts entry.
# ---------------------------------------------------------------------------


def test_pyproject_scripts_entry_present() -> None:
    """`harness-inspect = harness_runtime.admin.inspect:main` activated."""
    # Locate harness-runtime/pyproject.toml relative to this test file.
    here = Path(__file__).resolve()
    pyproject = here.parent.parent / "pyproject.toml"
    assert pyproject.exists()
    text = pyproject.read_text()
    assert 'harness-inspect    = "harness_runtime.admin.inspect:main"' in text, (
        f"harness-inspect script entry missing in {pyproject}"
    )


# ---------------------------------------------------------------------------
# Entry point via `python -m`-style direct call (sanity that main is importable).
# ---------------------------------------------------------------------------


def test_main_module_callable() -> None:
    import inspect as stdlib_inspect

    from harness_runtime.admin import inspect as admin_inspect

    assert callable(admin_inspect.main)
    sig = stdlib_inspect.signature(admin_inspect.main)
    params = list(sig.parameters.keys())
    assert params == ["argv"]


# ---------------------------------------------------------------------------
# §14.8.11.1 term 8(b) — the read-only protected-result-store row (U-RT-150).
# ---------------------------------------------------------------------------


def _runtime_config_file(config_dir: Path, repository_root: Path) -> Path:
    config_file = config_dir / "harness.toml"
    config_file.write_text(
        "[runtime]\n"
        'deployment_surface = "local-development"\n'
        f'repository_root = "{repository_root}"\n'
        'default_topology = "single-threaded-linear"\n'
        "\n[runtime.otel]\n"
        'otlp_endpoint = "http://localhost:4317"\n'
    )
    return config_file


def _seed_protected_result_store(repository_root: Path) -> Path:
    """Create the store root the composition root derives, holding one
    past-TTL crash orphan and no observation record."""
    from harness_runtime.bootstrap.factories.protected_result_store_factory import (
        PROTECTED_RESULT_STORE_ROOT_SUBPATH,
    )

    store_root = repository_root / PROTECTED_RESULT_STORE_ROOT_SUBPATH
    store_root.mkdir(parents=True, exist_ok=True)
    orphan = store_root / ".tmp-inspect-row-orphan"
    orphan.write_bytes(b"partial ciphertext from a killed write")
    stale = datetime.now(UTC).timestamp() - 120.0
    os.utime(orphan, (stale, stale))
    return store_root


def test_protected_result_store_row_absent_leaves_the_summary_byte_unchanged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """U-RT-150 AC #8(b) engagement predicate — the row ENGAGES ONLY when the
    config-derived store root exists. Absent, the output is BYTE-UNCHANGED from
    a pre-v1.111 run, and nothing is created.

    Mutation probe: engaging unconditionally (or creating the store root to
    check it) changes the output for a deployment that has never written a
    protected result, and the byte-equality assertion fails."""
    from harness_runtime.bootstrap.factories.protected_result_store_factory import (
        PROTECTED_RESULT_STORE_ROOT_SUBPATH,
    )

    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)
    config_file = _runtime_config_file(tmp_path, tmp_path)

    assert main(["--ledger-path", str(ledger)]) == 0
    baseline = capsys.readouterr().out

    assert main(["--ledger-path", str(ledger), "--runtime-config", str(config_file)]) == 0
    with_config = capsys.readouterr().out

    assert with_config == baseline
    assert "protected result store" not in with_config
    assert not (tmp_path / PROTECTED_RESULT_STORE_ROOT_SUBPATH).exists(), (
        "the read-only row CREATED the store root"
    )


def test_protected_result_store_row_reports_the_gauge_and_the_three_way_record_state(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """U-RT-150 AC #8(b) — the row reports the oldest resident candidate's age
    (covering BOTH classes) and the observation record's own state THREE-WAY,
    states in its own output what it CANNOT tell, and emits NO bound, NO
    threshold and NO pass/fail verdict. The record-absent reading is presented
    as EITHER a first-cutover store OR a repeating record-loss loop,
    indistinguishable at this surface — attributing it would reproduce AC #6's
    fact-not-verdict defect one surface over.

    Mutation probe: attributing the absent reading to record loss (or emitting
    any verdict/threshold token) fails the assertions below."""
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)
    _seed_protected_result_store(tmp_path)
    config_file = _runtime_config_file(tmp_path, tmp_path)

    assert main(["--ledger-path", str(ledger), "--runtime-config", str(config_file)]) == 0
    out = capsys.readouterr().out

    assert "protected result store" in out
    assert "resident crash-orphans: 1" in out
    assert "oldest_orphan_age=" in out
    assert "GC observation record: absent" in out
    assert "CANNOT TELL WHICH" in out
    assert "READ-TIME SNAPSHOT" in out
    assert "does NOT imply a sweep will run" in out
    assert "No bound, threshold or pass/fail verdict" in out
    lowered = out.lower()
    for verdict_token in ("exceeds", "threshold of", "pass/fail:", "unhealthy", "violation"):
        assert verdict_token not in lowered, f"the row emitted a verdict token: {verdict_token!r}"


def test_protected_result_store_row_json_shape(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """U-RT-150 AC #8(b) — the JSON rendering composes into the summary payload
    (never replacing a section) and carries the same readings.

    Mutation probe: replacing rather than composing drops `total_entries` and
    the ledger keys, failing the composition assertions."""
    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)
    _seed_protected_result_store(tmp_path)
    config_file = _runtime_config_file(tmp_path, tmp_path)

    assert main(["--ledger-path", str(ledger), "--runtime-config", str(config_file), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["total_entries"] == 1  # composed, not replaced
    assert payload["protected_result_store_entry_count"] == 0
    assert payload["protected_result_store_orphan_count"] == 1
    assert payload["protected_result_store_oldest_entry_age_seconds"] is None
    assert payload["protected_result_store_oldest_orphan_age_seconds"] > 100.0
    assert payload["protected_result_store_observation_record_state"] == "absent"
    assert "CANNOT TELL WHICH" in payload["protected_result_store_observation_record_absent_note"]


def test_protected_result_store_unusable_root_exits_rt_fail_inspect_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """U-RT-150 AC #8(b) — an UNUSABLE store root takes the binary's own
    `RT-FAIL-INSPECT-PATH` exit rather than silently suppressing the row.
    Suppressing it would report nothing at all, successfully, for a store the
    operator cannot inspect — on the one surface whose purpose is to make the
    retention level falsifiable. Same disposition the §13.7 pause-journal
    enumeration already takes for an unreadable journal directory.

    *(Out-of-family review round 1 [P2].)*

    Mutation probe: dropping the `except OSError` around the row lets the
    `NotADirectoryError` escape as an uncaught traceback instead of exit 2."""
    from harness_runtime.bootstrap.factories.protected_result_store_factory import (
        PROTECTED_RESULT_STORE_ROOT_SUBPATH,
    )

    ledger = tmp_path / "state.jsonl"
    _write_n_entries(ledger, 1)
    # A regular FILE where the store root should be.
    store_root = tmp_path / PROTECTED_RESULT_STORE_ROOT_SUBPATH
    store_root.parent.mkdir(parents=True, exist_ok=True)
    store_root.write_text("not a store root")
    config_file = _runtime_config_file(tmp_path, tmp_path)

    code = main(["--ledger-path", str(ledger), "--runtime-config", str(config_file)])
    captured = capsys.readouterr()

    assert code == 2
    assert "RT-FAIL-INSPECT-PATH" in captured.err
    assert "protected result store root unusable" in captured.err


def test_protected_result_store_row_root_is_config_derived_not_ledger_path_derived(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """U-RT-150 AC #8(b)'s PINNED ROOT RESOLUTION. The row MUST read the SAME
    store root the composition root derives —
    `materialize_protected_result_store_stage`'s
    `config.repository_root / PROTECTED_RESULT_STORE_ROOT_SUBPATH` — and MUST
    NOT introduce a second, independent resolution. `--ledger-path` selects the
    STATE LEDGER, not this store, so a `--ledger-path` pointed at a different
    directory can never redirect the row: a report rendered against a different
    directory than the one the sweep collects is an acceptance FAILURE, not a
    configuration nuance.

    The two directories are deliberately set DIFFERENT here, and only the
    config-derived one holds a store.

    Mutation probe: resolving the root from `--ledger-path` (e.g.
    `ledger_path.parent / subpath`) renders the row against the ledger
    directory, where there is no store — the row would not engage at all and the
    assertions below fail."""
    ledger_dir = tmp_path / "ledger-elsewhere"
    ledger_dir.mkdir()
    ledger = ledger_dir / "state.jsonl"
    _write_n_entries(ledger, 1)

    repository_root = tmp_path / "deployment-root"
    repository_root.mkdir()
    store_root = _seed_protected_result_store(repository_root)
    config_file = _runtime_config_file(tmp_path, repository_root)

    # A store also exists under the LEDGER directory, holding a DIFFERENT
    # candidate count — so reading the wrong root would be visible, not merely
    # empty.
    from harness_runtime.bootstrap.factories.protected_result_store_factory import (
        PROTECTED_RESULT_STORE_ROOT_SUBPATH,
    )

    decoy_root = ledger_dir / PROTECTED_RESULT_STORE_ROOT_SUBPATH
    decoy_root.mkdir(parents=True)
    stale = datetime.now(UTC).timestamp() - 120.0
    for index in range(3):
        decoy = decoy_root / f".tmp-decoy-{index}"
        decoy.write_bytes(b"decoy")
        os.utime(decoy, (stale, stale))

    assert main(["--ledger-path", str(ledger), "--runtime-config", str(config_file), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["protected_result_store_root"] == str(store_root), (
        "the row resolved its root from --ledger-path instead of the config-derived store root"
    )
    assert payload["protected_result_store_orphan_count"] == 1, (
        "the row reported the DECOY store under the ledger directory — it would "
        "render against a different directory than the one the sweep collects"
    )
