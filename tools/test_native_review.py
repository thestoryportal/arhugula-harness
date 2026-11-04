"""Native evidence, immutable bindings and session independence; no live reviewer calls."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import finding_record as fr
import native_review as nr
import pytest
import review_loop_gate as gate
import review_wrapper_common as rw

AUTHOR = "00000000-0000-4000-8000-000000000001"
REVIEWER = "00000000-0000-4000-8000-000000000002"
CORRECTOR = "00000000-0000-4000-8000-000000000003"
BOUND = {
    "head_sha": "a" * 40,
    "base_sha": "b" * 40,
    "diff_digest": "c" * 64,
    "reviewer_identity": "codex-review",
    "prompt_version": "native-session-review-v1",
    "config_hash": "bound-people",
}


def verdict(**changes):
    return (
        "```json\n"
        + json.dumps({"verdict": "APPROVE", "findings": [], **BOUND, **changes})
        + "\n```"
    )


def transcript(path, *, final=True, complete=True, later_turn=False):
    rows = [
        {"type": "session_meta", "payload": {"id": REVIEWER}},
        {"type": "event_msg", "payload": {"type": "task_started"}},
        {
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": verdict()}],
            },
        },
    ]
    if final:
        rows.append(
            {
                "type": "response_item",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "phase": "final_answer",
                    "content": [{"type": "output_text", "text": verdict()}],
                },
            }
        )
    if complete:
        rows.append({"type": "event_msg", "payload": {"type": "task_complete"}})
    if later_turn:
        rows.append({"type": "event_msg", "payload": {"type": "task_started"}})
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


@pytest.mark.parametrize("options", [{"final": False}, {"complete": False}, {"later_turn": True}])
def test_only_latest_completed_assistant_final_is_evidence(tmp_path, options):
    path = tmp_path / "native.jsonl"
    transcript(path, **options)
    assert nr.read_transcript(path) == (REVIEWER, None)


def test_completed_answer_and_actual_identity(tmp_path):
    path = tmp_path / "native.jsonl"
    transcript(path)
    assert nr.read_transcript(path) == (REVIEWER, verdict())
    with path.open("a") as stream:
        stream.write(json.dumps({"type": "session_meta", "payload": {"id": AUTHOR}}) + "\n")
    with pytest.raises(ValueError, match="conflicting"):
        nr.read_transcript(path)


@pytest.mark.parametrize("authors", [[AUTHOR, REVIEWER], [REVIEWER], []])
def test_author_and_material_corrector_cannot_review(authors):
    with pytest.raises(ValueError, match="separate"):
        nr.participants(REVIEWER, authors)


@pytest.fixture
def recording(tmp_path, monkeypatch):
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path / "gate.jsonl")
    monkeypatch.setenv("HARNESS_ARC_ID", "native-arc")
    monkeypatch.setenv("HARNESS_LANE_ID", "native-lane")
    monkeypatch.setenv("HARNESS_CYCLE_PASS", "initial")
    monkeypatch.setattr(gate, "delivery_admission", lambda *a, **k: lambda rows: None)
    monkeypatch.setattr(rw, "record_round_outcome_if_reserved", lambda *a, **k: None)
    return tmp_path


def test_native_review_emits_real_channel_and_independent_session(recording):
    people = nr.participants(REVIEWER, [AUTHOR, CORRECTOR])
    assert nr.record(recording, verdict(), BOUND, people) == 0
    (row,) = fr.read_rows()
    assert row["producer"] == "codex_review_wrapper"
    assert row["reviewer_session"] == REVIEWER
    assert row["author_sessions"] == [AUTHOR, CORRECTOR]
    assert gate.completing_run([row], "native-arc") is not None
    row["author_sessions"].append(REVIEWER)
    with pytest.raises(fr.RecordError, match="materially authored"):
        fr.validate(row)
    assert gate.completing_run([row], "native-arc") is None


@pytest.mark.parametrize(
    "change", [{"head_sha": "d" * 40}, {"config_hash": "changed-authors"}, {"verdict": "BLOCK"}]
)
def test_stale_or_malformed_verdict_records_nothing(recording, change):
    with pytest.raises(ValueError):
        nr.record(recording, verdict(**change), BOUND, nr.participants(REVIEWER, [AUTHOR]))
    assert fr.read_rows() == []


def test_correction_cannot_drop_prior_author(recording):
    nr.record(recording, verdict(), BOUND, nr.participants(REVIEWER, [AUTHOR, CORRECTOR]))
    with pytest.raises(ValueError, match="omitted"):
        nr.record(recording, verdict(), BOUND, nr.participants(REVIEWER, [AUTHOR]))
    assert len(fr.read_rows()) == 1


def test_binding_changes_with_material_authors(monkeypatch):
    monkeypatch.setattr(rw, "compute_binding", lambda *a, **k: k)
    assert nr.binding(Path("."), "main", nr.participants(REVIEWER, [AUTHOR])) != nr.binding(
        Path("."), "main", nr.participants(REVIEWER, [AUTHOR, CORRECTOR])
    )


def test_cli_refuses_arbitrary_verdict_file(tmp_path, monkeypatch):
    path = tmp_path / f"{REVIEWER}.jsonl"
    transcript(path)
    (tmp_path / "codex/sessions").mkdir(parents=True)
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex"))
    assert nr.main(["record", "--transcript", str(path), "--authors", AUTHOR]) == 3
