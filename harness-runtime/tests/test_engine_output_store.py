"""B-ENGINE-OUTPUT-REPLAY — durable per-run output store unit tests.

Verifies the crash-survivable journal mechanics (round-trip across a fresh store
instance = a process restart; per-step keying; last-wins; torn-append skip + the
self-healing leading newline) in isolation — the substrate the producer +
resume-rehydration compose with. Mirrors `test_r_cc_1_api_resume.py`'s durable-
store unit tests.
"""

from __future__ import annotations

from pathlib import Path

from harness_runtime.lifecycle.engine_output_store import (
    EngineOutputStore,
    engine_output_dir_for,
)

_RUN_KEY = "run-idem-key-abc"


def test_record_then_read_round_trip(tmp_path: Path) -> None:
    """record() persists per-step outputs; a FRESH store over the same dir (a
    process restart) reads them back keyed by step_index."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    store.record(_RUN_KEY, 0, "step-0", {"role": "gen", "v": 1})
    store.record(_RUN_KEY, 1, "step-1", {"role": "eval", "v": 2})

    fresh = EngineOutputStore(journal_dir=tmp_path / "eo")  # restart
    outputs = fresh.read_outputs(_RUN_KEY)
    assert outputs == {
        0: ("step-0", {"role": "gen", "v": 1}),
        1: ("step-1", {"role": "eval", "v": 2}),
    }


def test_missing_run_returns_empty(tmp_path: Path) -> None:
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    assert store.read_outputs("never-recorded") == {}


def test_last_record_per_step_index_wins(tmp_path: Path) -> None:
    """An idempotent re-record of the same step_index (e.g. a resume re-write)
    yields the latest output (last-wins)."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    store.record(_RUN_KEY, 0, "step-0", {"v": "first"})
    store.record(_RUN_KEY, 0, "step-0", {"v": "second"})
    assert store.read_outputs(_RUN_KEY) == {0: ("step-0", {"v": "second"})}


def test_per_run_isolation(tmp_path: Path) -> None:
    """Each run_key has a dedicated file; a read for one run never returns another's."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    store.record("run-a", 0, "s0", {"r": "a"})
    store.record("run-b", 0, "s0", {"r": "b"})
    assert store.read_outputs("run-a") == {0: ("s0", {"r": "a"})}
    assert store.read_outputs("run-b") == {0: ("s0", {"r": "b"})}


def test_torn_trailing_line_is_skipped_not_corrupting(tmp_path: Path) -> None:
    """A crash mid-append leaves a partial trailing line with no newline; the next
    record's leading-newline self-heal makes the fragment its own (skipped) line,
    so the prior committed records + the new clean record are all readable."""
    journal_dir = tmp_path / "eo"
    store = EngineOutputStore(journal_dir=journal_dir)
    store.record(_RUN_KEY, 0, "step-0", {"v": 0})
    # Simulate a crash mid-append: a partial record with NO trailing newline.
    import hashlib

    digest = hashlib.sha256(_RUN_KEY.encode("utf-8")).hexdigest()
    journal_file = journal_dir / f"{digest}.jsonl"
    with journal_file.open("a", encoding="utf-8") as handle:
        handle.write('{"step_index": 1, "step_id": "TORN-NO-NEWLINE')
    # A clean record after the torn append must be readable + not corrupt step-0.
    store.record(_RUN_KEY, 1, "step-1", {"v": 1})
    outputs = store.read_outputs(_RUN_KEY)
    assert outputs[0] == ("step-0", {"v": 0})
    assert outputs[1] == ("step-1", {"v": 1})


def test_corrupt_line_skipped_committed_records_survive(tmp_path: Path) -> None:
    """A garbage middle line is skipped; the surrounding committed records survive
    (per-line fail-soft; the resume-site prefix-completeness check is the
    fail-closed gate for a MISSING committed step)."""
    journal_dir = tmp_path / "eo"
    store = EngineOutputStore(journal_dir=journal_dir)
    store.record(_RUN_KEY, 0, "step-0", {"v": 0})
    import hashlib

    digest = hashlib.sha256(_RUN_KEY.encode("utf-8")).hexdigest()
    journal_file = journal_dir / f"{digest}.jsonl"
    with journal_file.open("a", encoding="utf-8") as handle:
        handle.write("{not json at all}\n")
    store.record(_RUN_KEY, 2, "step-2", {"v": 2})
    outputs = store.read_outputs(_RUN_KEY)
    assert outputs == {0: ("step-0", {"v": 0}), 2: ("step-2", {"v": 2})}
    # The gap at index 1 is the corruption the rehydrate site fails closed on.
    assert 1 not in outputs


def test_journal_exists_discriminates_absent_from_recorded(tmp_path: Path) -> None:
    """`journal_exists` is the rehydrate discriminator: False before any record (a
    config flip → degrade), True after (a recorded run; if read then yields nothing
    → unreadable → fail-closed)."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    assert store.journal_exists(_RUN_KEY) is False
    store.record(_RUN_KEY, 0, "step-0", {"v": 0})
    assert store.journal_exists(_RUN_KEY) is True
    # A FRESH store over the same dir (a restart) also sees the existing journal.
    assert EngineOutputStore(journal_dir=tmp_path / "eo").journal_exists(_RUN_KEY) is True


def test_engine_output_dir_for_co_locates_under_state_ledger(tmp_path: Path) -> None:
    assert engine_output_dir_for(tmp_path) == tmp_path / "engine-output"


# -- B-FANOUT-OUTPUT-REPLAY: concurrent-fan-out branch sidecar -----------------
#
# The STORE is the sole authority for which-branches-completed on a fan-out
# crash-resume (the durable ledger is binary for a concurrent fan-out). These
# verify per-branch capture/read, the per-branch-FILE isolation that lets N
# concurrent writers avoid contention, the present-vs-readable fail-closed
# discriminator, and the orchestrator-output capture.


def test_record_branch_then_read_round_trip(tmp_path: Path) -> None:
    """record_branch() persists per-branch outputs keyed by branch_index; a FRESH
    store over the same dir (a crash + fresh-bootstrap resume) reads them back."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    store.record_branch(_RUN_KEY, 0, "worker-0", "completed", {"out": "b0"})
    store.record_branch(_RUN_KEY, 2, "worker-2", "completed", {"out": "b2"})

    fresh = EngineOutputStore(journal_dir=tmp_path / "eo")  # crash + restart
    assert fresh.read_branch_records(_RUN_KEY) == {
        0: ("worker-0", "completed", {"out": "b0"}),
        2: ("worker-2", "completed", {"out": "b2"}),
    }
    assert fresh.present_branch_indexes(_RUN_KEY) == {0, 2}


def test_branch_disposition_round_trip(tmp_path: Path) -> None:
    """The store records the terminal DISPOSITION for every branch — completed-with-output,
    completed-no-output (ran-and-errored), and timed_out — read back across a fresh store
    (crash + restart). The disposition is what closes the at-most-once recovery class."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    store.record_branch(_RUN_KEY, 0, "w0", "completed", {"out": 0})
    store.record_branch(_RUN_KEY, 1, "w1", "completed", None)  # ran-and-errored (no output)
    store.record_branch(_RUN_KEY, 2, "w2", "timed_out", None)  # deadline-cut (ambiguous)

    fresh = EngineOutputStore(journal_dir=tmp_path / "eo")  # crash + restart
    assert fresh.read_branch_records(_RUN_KEY) == {
        0: ("w0", "completed", {"out": 0}),
        1: ("w1", "completed", None),
        2: ("w2", "timed_out", None),
    }


def test_unknown_disposition_is_unreadable_fail_closed(tmp_path: Path) -> None:
    """A parseable record with an UNKNOWN terminal_status (tamper / a future schema) is
    treated as UNREADABLE — omitted from read_branch_records but surfaced by
    present_branch_indexes, so the resume site fails closed (out-of-family Codex [P2])."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    store.record_branch(_RUN_KEY, 0, "w0", "completed", {"o": 0})
    store._branch_file(_RUN_KEY, 1).write_text(
        '{"output": null, "step_id": "w1", "terminal_status": "bogus"}', encoding="utf-8"
    )
    readable = set(store.read_branch_records(_RUN_KEY).keys())
    present = store.present_branch_indexes(_RUN_KEY)
    assert readable == {0}  # the bogus-disposition record is omitted (unreadable)
    assert present == {0, 1}
    assert present - readable == {1}  # the fail-closed corrupt set


def test_branch_files_are_per_branch_isolated(tmp_path: Path) -> None:
    """Each branch writes its OWN file (no shared-handle contention for N
    concurrent writers); the filename is the branch-index authority."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    store.record_branch(_RUN_KEY, 0, "w0", "completed", {"r": 0})
    store.record_branch(_RUN_KEY, 1, "w1", "completed", {"r": 1})
    branches_dir = store._branches_dir(_RUN_KEY)
    files = sorted(p.name for p in branches_dir.glob("branch-*.jsonl"))
    assert files == ["branch-0.jsonl", "branch-1.jsonl"]


def test_branch_present_but_unreadable_is_fail_closed_signal(tmp_path: Path) -> None:
    """A present-but-corrupt branch file is OMITTED from read_branch_records but
    SURFACED by present_branch_indexes — the set difference is the corrupt set the
    resume site fails closed on (never silently re-dispatching a corrupt branch)."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    store.record_branch(_RUN_KEY, 0, "w0", "completed", {"r": 0})
    # Branch 1's file exists but holds no parseable record (corruption / tamper).
    store._branch_file(_RUN_KEY, 1).write_text("{ not json", encoding="utf-8")
    present = store.present_branch_indexes(_RUN_KEY)
    readable = set(store.read_branch_records(_RUN_KEY).keys())
    assert present == {0, 1}
    assert readable == {0}
    assert present - readable == {1}  # the fail-closed corrupt set


def test_branch_last_record_wins(tmp_path: Path) -> None:
    """An idempotent re-record of the same branch yields the latest (last-wins)."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    store.record_branch(_RUN_KEY, 0, "w0", "completed", {"v": "first"})
    store.record_branch(_RUN_KEY, 0, "w0", "completed", {"v": "second"})
    assert store.read_branch_records(_RUN_KEY) == {0: ("w0", "completed", {"v": "second"})}


def test_orchestrator_capture_and_read(tmp_path: Path) -> None:
    """The ORCHESTRATOR_WORKERS steps[0] output rides a dedicated orchestrator
    record (not a branch file); absent → None, present → (step_id, output)."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    assert store.read_orchestrator_output(_RUN_KEY) is None
    assert store.orchestrator_present(_RUN_KEY) is False
    store.record_orchestrator(_RUN_KEY, "orch-step", {"plan": "delegate"})
    assert store.read_orchestrator_output(_RUN_KEY) == ("orch-step", {"plan": "delegate"})
    assert store.orchestrator_present(_RUN_KEY) is True
    # The orchestrator record does NOT pollute the worker branch set.
    assert store.read_branch_records(_RUN_KEY) == {}
    assert store.present_branch_indexes(_RUN_KEY) == set()


def test_branch_absent_run_returns_empty(tmp_path: Path) -> None:
    """No fan-out journals (config flip / first run) → empty/None, no error."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    assert store.read_branch_records("never") == {}
    assert store.present_branch_indexes("never") == set()
    assert store.read_orchestrator_output("never") is None
    assert store.orchestrator_present("never") is False


def test_branch_sidecar_does_not_collide_with_linear_file(tmp_path: Path) -> None:
    """The linear {digest}.jsonl FILE and the {digest}.branches DIR coexist for the
    same run_key (a SUB_AGENT_DISPATCH parent-linear + fan-out child run)."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    store.record(_RUN_KEY, 0, "lin-0", {"x": 1})
    store.record_branch(_RUN_KEY, 0, "w0", "completed", {"y": 2})
    assert store.read_outputs(_RUN_KEY) == {0: ("lin-0", {"x": 1})}
    assert store.read_branch_records(_RUN_KEY) == {0: ("w0", "completed", {"y": 2})}
    assert store.journal_exists(_RUN_KEY) is True
