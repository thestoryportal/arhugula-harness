"""B-OD17-EVAL-LOOP-TOOLING — `harness-inspect` holdout-loop CLI flags.

Acceptance per `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §3
B-OD17-EVAL-LOOP-TOOLING: "Holdout determinism witness; review round-trip
persists; zero model calls in the loop (control assert)." This file drives
the full sample -> review -> scaffold loop through the real CLI entry point
(`main`) and includes the strongest empirical zero-model-calls control: a
patched `socket.socket.connect` that raises on ANY network attempt, proving
no code path in the loop reaches out to a network (an LLM provider call is
necessarily a network call).
"""

from __future__ import annotations

import socket
from pathlib import Path

import pytest
from harness_od.sqlite_span_store import SpanInsertRow, initialize_span_store, insert_spans
from harness_runtime.admin.inspect import main


def _span(trace_id: str, span_id: str) -> SpanInsertRow:
    return SpanInsertRow(
        span_id=span_id,
        trace_id=trace_id,
        parent_span_id=None,
        name="meta-eval",
        kind=0,
        start_time_ns=0,
        end_time_ns=1,
        status_code=0,
        status_message=None,
        attributes_json="{}",
        events_json="[]",
        workflow_id=None,
        workflow_run_id=None,
        workflow_idempotency_key=None,
    )


def _seed_db(db_path: Path, n_traces: int = 5) -> None:
    conn = initialize_span_store(db_path)
    for i in range(n_traces):
        trace_id = f"trace-{i:02d}"
        insert_spans(conn, [_span(trace_id, f"{trace_id}-a")])
    conn.close()


# ---------------------------------------------------------------------------
# --holdout-sample.
# ---------------------------------------------------------------------------


def test_holdout_sample_writes_file(tmp_path: Path) -> None:
    db_path = tmp_path / "spans.db"
    _seed_db(db_path)
    holdout_path = tmp_path / "holdout.json"

    code = main(
        [
            "--holdout-sample",
            "3",
            "--collector-path",
            str(db_path),
            "--primitive",
            "routing_accuracy_holdout",
            "--holdout-path",
            str(holdout_path),
            "--seed",
            "5",
        ]
    )

    assert code == 0
    assert holdout_path.exists()


def test_holdout_sample_is_deterministic_across_cli_invocations(tmp_path: Path) -> None:
    db_path = tmp_path / "spans.db"
    _seed_db(db_path)
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    for target in (a, b):
        code = main(
            [
                "--holdout-sample",
                "3",
                "--collector-path",
                str(db_path),
                "--primitive",
                "routing_accuracy_holdout",
                "--holdout-path",
                str(target),
                "--seed",
                "5",
            ]
        )
        assert code == 0
    # `sampled_at` is stamped with the current time at each CLI invocation
    # (documented as "carried verbatim, not derived" in `holdout_set.py`), so
    # the determinism witness is the trace *selection*, not raw file bytes.
    from harness_od.holdout_set import read_holdout_set

    holdout_a = read_holdout_set(a)
    holdout_b = read_holdout_set(b)
    assert holdout_a.traces == holdout_b.traces
    assert holdout_a.seed == holdout_b.seed == 5


def test_holdout_sample_missing_required_args_exits_nonzero(tmp_path: Path) -> None:
    code = main(["--holdout-sample", "3"])
    assert code == 2


def test_holdout_sample_wrong_schema_db_exits_nonzero_instead_of_crashing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A sqlite file with a `spans` table but the wrong columns (e.g. a stale
    collector db from an older schema) must exit cleanly, not raise a raw
    `sqlite3.DatabaseError` traceback — mirrors the `--browse` fix for the
    same failure mode (sqlite defers "no such column" to first query, not
    `sqlite3.connect`)."""
    import sqlite3

    db_path = tmp_path / "wrong-schema.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE spans (span_id TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()

    code = main(
        [
            "--holdout-sample",
            "3",
            "--collector-path",
            str(db_path),
            "--primitive",
            "routing_accuracy_holdout",
            "--holdout-path",
            str(tmp_path / "holdout.json"),
            "--seed",
            "5",
        ]
    )
    err = capsys.readouterr().err

    assert code == 2
    assert "RT-FAIL-INSPECT-PATH" in err
    assert not (tmp_path / "holdout.json").exists()


# ---------------------------------------------------------------------------
# --holdout-review + --holdout-scaffold, end to end.
# ---------------------------------------------------------------------------


def test_full_loop_sample_review_scaffold(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "spans.db"
    _seed_db(db_path, n_traces=2)
    holdout_path = tmp_path / "holdout.json"
    ledger_path = tmp_path / "ledger.jsonl"
    stub_dir = tmp_path / "stubs"

    assert (
        main(
            [
                "--holdout-sample",
                "2",
                "--collector-path",
                str(db_path),
                "--primitive",
                "sandbox_tier_routing_accuracy",
                "--holdout-path",
                str(holdout_path),
                "--seed",
                "1",
            ]
        )
        == 0
    )

    typed_lines = iter(["correct", "looked fine", "mis-routed", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(typed_lines))

    assert (
        main(
            [
                "--holdout-review",
                "--holdout-path",
                str(holdout_path),
                "--review-ledger-path",
                str(ledger_path),
            ]
        )
        == 0
    )
    assert ledger_path.exists()
    ledger_lines = [line for line in ledger_path.read_text().splitlines() if line.strip()]
    assert len(ledger_lines) == 2

    assert (
        main(
            [
                "--holdout-scaffold",
                "--review-ledger-path",
                str(ledger_path),
                "--stub-dir",
                str(stub_dir),
            ]
        )
        == 0
    )
    stub_files = list(stub_dir.glob("*.py"))
    assert len(stub_files) == 2
    for stub in stub_files:
        assert "raise NotImplementedError" in stub.read_text()


def test_holdout_review_skips_already_reviewed_traces(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "spans.db"
    _seed_db(db_path, n_traces=2)
    holdout_path = tmp_path / "holdout.json"
    ledger_path = tmp_path / "ledger.jsonl"

    main(
        [
            "--holdout-sample",
            "2",
            "--collector-path",
            str(db_path),
            "--primitive",
            "routing_accuracy_holdout",
            "--holdout-path",
            str(holdout_path),
            "--seed",
            "1",
        ]
    )

    typed_lines = iter(["cat-a", "", "cat-b", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(typed_lines))
    main(
        [
            "--holdout-review",
            "--holdout-path",
            str(holdout_path),
            "--review-ledger-path",
            str(ledger_path),
        ]
    )
    assert len(ledger_path.read_text().splitlines()) == 2

    def _fail_if_called(_prompt: str = "") -> str:
        raise AssertionError("input() called again — a reviewed trace was not skipped")

    monkeypatch.setattr("builtins.input", _fail_if_called)
    code = main(
        [
            "--holdout-review",
            "--holdout-path",
            str(holdout_path),
            "--review-ledger-path",
            str(ledger_path),
        ]
    )
    assert code == 0


# ---------------------------------------------------------------------------
# Zero-model-calls control — strongest form: no network reachable at all.
# ---------------------------------------------------------------------------


def test_full_loop_makes_zero_network_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An LLM provider call is necessarily a network call. Patch
    `socket.socket.connect` to raise on any attempt and drive the entire
    sample -> review -> scaffold loop through the real CLI — if any code
    path reached out to a model, this raises and the test fails."""

    def _connect_forbidden(self: socket.socket, address: object) -> None:
        raise AssertionError(f"unexpected network connect attempt: {address!r}")

    monkeypatch.setattr(socket.socket, "connect", _connect_forbidden)

    db_path = tmp_path / "spans.db"
    _seed_db(db_path, n_traces=3)
    holdout_path = tmp_path / "holdout.json"
    ledger_path = tmp_path / "ledger.jsonl"
    stub_dir = tmp_path / "stubs"

    assert (
        main(
            [
                "--holdout-sample",
                "3",
                "--collector-path",
                str(db_path),
                "--primitive",
                "routing_accuracy_holdout",
                "--holdout-path",
                str(holdout_path),
                "--seed",
                "3",
            ]
        )
        == 0
    )

    typed_lines = iter(["a", "", "b", "", "c", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(typed_lines))
    assert (
        main(
            [
                "--holdout-review",
                "--holdout-path",
                str(holdout_path),
                "--review-ledger-path",
                str(ledger_path),
            ]
        )
        == 0
    )

    assert (
        main(
            [
                "--holdout-scaffold",
                "--review-ledger-path",
                str(ledger_path),
                "--stub-dir",
                str(stub_dir),
            ]
        )
        == 0
    )
