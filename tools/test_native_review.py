"""Native evidence, immutable bindings and session independence; no live reviewer calls."""

import json
import subprocess
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
TURN = "00000000-0000-4000-8000-000000000004"
LATER = "00000000-0000-4000-8000-000000000005"
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


def native_turn(turn, answer, *, model="review-model", complete=True):
    rows = [
        {"type": "event_msg", "payload": {"type": "task_started", "turn_id": turn}},
        {"type": "turn_context", "payload": {"turn_id": turn, "model": model}},
        {
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "assistant",
                "phase": "final_answer",
                "content": [{"type": "output_text", "text": answer}],
            },
        },
    ]
    if complete:
        rows.append({"type": "event_msg", "payload": {"type": "task_complete", "turn_id": turn}})
    return rows


def test_explicit_completed_turn_survives_unrelated_later_turn(tmp_path):
    path = tmp_path / "native.jsonl"
    rows = [{"type": "session_meta", "payload": {"id": REVIEWER}}]
    rows += native_turn(TURN, verdict(), model="actual-review-model")
    rows += native_turn(LATER, "Unrelated work", model="later-model", complete=False)
    path.write_text("\n".join(map(json.dumps, rows)))
    assert nr.read_transcript(path) == (REVIEWER, None)
    assert nr.read_selected_turn(path, TURN, BOUND) == (REVIEWER, verdict(), "actual-review-model")


@pytest.mark.parametrize(
    "failure", ["incomplete", "missing", "wrong_completion", "superseding", "identity"]
)
def test_explicit_turn_refuses_invalid_or_superseded_evidence(tmp_path, failure):
    path = tmp_path / "native.jsonl"
    rows = [{"type": "session_meta", "payload": {"id": REVIEWER}}]
    rows += native_turn(TURN, verdict(), complete=failure != "incomplete")
    if failure == "wrong_completion":
        rows[-1]["payload"]["turn_id"] = LATER
    if failure == "superseding":
        rows += native_turn(
            LATER,
            verdict(
                verdict="BLOCK",
                findings=[{"severity": "P2", "location": "x:1", "message": "new finding"}],
            ),
        )
    if failure == "identity":
        rows.append({"type": "session_meta", "payload": {"id": AUTHOR}})
    path.write_text("\n".join(map(json.dumps, rows)))
    with pytest.raises(ValueError):
        nr.read_selected_turn(path, LATER if failure == "missing" else TURN, BOUND)


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


@pytest.mark.parametrize(
    "change",
    [
        {"reviewer_session": None},
        {"author_sessions": None},
        {"author_sessions": []},
        {"author_sessions": [AUTHOR, AUTHOR]},
        {"reviewer_session": "not-a-session"},
        {"author_sessions": ["not-a-session"]},
    ],
)
def test_native_provenance_cannot_be_partial_or_malformed(recording, change):
    nr.record(recording, verdict(), BOUND, nr.participants(REVIEWER, [AUTHOR]))
    (row,) = fr.read_rows()
    with pytest.raises(fr.RecordError, match="schema"):
        fr.validate({**row, **change})


@pytest.mark.parametrize(
    "change", [{"reviewer_session": CORRECTOR}, {"author_sessions": [CORRECTOR]}]
)
def test_adjudication_preserves_native_provenance(recording, change):
    nr.record(
        recording,
        verdict(
            verdict="BLOCK",
            findings=[{"severity": "P2", "location": "tools/x.py:12", "message": "contract gap"}],
        ),
        BOUND,
        nr.participants(REVIEWER, [AUTHOR]),
    )
    (row,) = fr.read_rows()
    adj = {
        **row,
        "record_kind": "finding_adjudication",
        "ts": "2099-01-01T00:00:00Z",
        "disposition": "accepted",
        "disposition_actor": "operator",
    }
    with pytest.raises(fr.RecordError, match="core field"):
        fr.append_row({**adj, **change})
    fr.append_row(adj)
    assert fr.read_rows()[-1]["reviewer_session"] == REVIEWER
    assert fr.read_rows()[-1]["author_sessions"] == [AUTHOR]


POLICY = json.loads(
    (Path(__file__).resolve().parent.parent / ".harness/workflow-policy.json").read_text()
)


def committed_policy(repo, **changes):
    """A real commit whose tracked policy the untagged route must read: the head binds it."""
    (repo / ".harness").mkdir(parents=True)
    (repo / ".harness/workflow-policy.json").write_text(json.dumps({**POLICY, **changes}))
    for args in (["init", "-q"], ["add", "."], ["commit", "-qm", "policy"]):
        subprocess.run(
            ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
            check=True,
        )
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    return {**BOUND, "head_sha": head}


@pytest.fixture
def nontrial(recording, monkeypatch):
    monkeypatch.delenv("HARNESS_CYCLE_PASS")
    monkeypatch.setattr(gate, "_reservation_exists", lambda arc: False)
    return recording / "repo"


def untagged(repo, bound, authors=(AUTHOR, CORRECTOR)):
    return nr.record(repo, verdict(**bound), bound, nr.participants(REVIEWER, list(authors)))


def test_nontrial_import_records_one_untagged_bound_row(nontrial):
    bound = committed_policy(nontrial)
    assert untagged(nontrial, bound) == 0
    (row,) = fr.read_rows()
    assert (row["cycle_pass"], row["record_kind"], row["producer"]) == (
        None,
        "no_finding",
        "codex_review_wrapper",
    )
    assert (row["head_sha"], row["reviewer_session"], row["author_sessions"]) == (
        bound["head_sha"],
        REVIEWER,
        [AUTHOR, CORRECTOR],
    )
    # evidence of a review, never a completed cycle pass
    assert gate.completing_run([row], "native-arc") is None
    with pytest.raises(ValueError, match="already recorded"):
        untagged(nontrial, bound)
    assert len(fr.read_rows()) == 1


def test_cli_selected_turn_records_once_and_rejects_wrong_candidate(nontrial, monkeypatch):
    bound = committed_policy(nontrial)
    monkeypatch.chdir(nontrial)
    store = nontrial / "codex" / "sessions"
    store.mkdir(parents=True)
    monkeypatch.setenv("CODEX_HOME", str(store.parent))
    path = store / f"rollout-{REVIEWER}.jsonl"
    rows = [{"type": "session_meta", "payload": {"id": REVIEWER}}]
    rows += native_turn(TURN, verdict(**bound))
    rows += native_turn(LATER, "Unrelated work", complete=False)
    path.write_text("\n".join(map(json.dumps, rows)))
    monkeypatch.setattr(nr, "binding", lambda *args: bound)
    args = ["record", "--transcript", str(path), "--authors", AUTHOR, "--turn-id", TURN]
    monkeypatch.setattr(nr, "binding", lambda *args: {**bound, "head_sha": "d" * 40})
    assert nr.main(args) == 3
    assert fr.read_rows() == []
    monkeypatch.setattr(nr, "binding", lambda *args: bound)
    assert (
        nr.main(["record", "--transcript", str(path), "--authors", REVIEWER, "--turn-id", TURN])
        == 3
    )
    assert fr.read_rows() == []
    assert nr.main(args) == 0
    assert nr.main(args) == 3
    assert len(fr.read_rows()) == 1


@pytest.mark.parametrize(
    "policy",
    [
        {"eligible_units": [{"unit": "arhugula-harness-trial-193.qrf", "arc": "native-arc"}]},
        {"review_rules": {}},
    ],
)
def test_nontrial_import_refuses_trial_or_undelegated_head(nontrial, policy):
    bound = committed_policy(nontrial, **policy)
    with pytest.raises(ValueError, match="not nontrial"):
        untagged(nontrial, bound)
    assert fr.read_rows() == []


def test_unset_pass_cannot_bypass_a_reserved_cycle(nontrial, monkeypatch):
    bound = committed_policy(nontrial)
    monkeypatch.setattr(gate, "_gate_state_in_force", lambda repo, arc: gate.GateState())
    with pytest.raises(ValueError, match="reserved"):
        untagged(nontrial, bound)
    assert fr.read_rows() == []


@pytest.mark.parametrize("cycle_pass", ["initial", "1"])
def test_unset_pass_cannot_follow_cycle_history(nontrial, monkeypatch, cycle_pass):
    bound = committed_policy(nontrial)
    monkeypatch.setenv("HARNESS_CYCLE_PASS", cycle_pass)
    tagged = rw.parse_verdict("codex", verdict(**bound), bound, source="native-session")
    tagged.participants = nr.participants(REVIEWER, [AUTHOR])
    rw.emit_outcome(
        tagged,
        producer="codex_review_wrapper",
        arc_id="native-arc",
        lane_id="native-lane",
        round_n=None,
        admit=lambda rows: None,
    )
    monkeypatch.delenv("HARNESS_CYCLE_PASS")
    with pytest.raises(ValueError, match="cycle history"):
        untagged(nontrial, {**bound, "diff_digest": "e" * 64})
    assert len(fr.read_rows()) == 1


def test_native_delivery_refuses_legacy_pass_and_fallback_arc(recording, monkeypatch):
    people = nr.participants(REVIEWER, [AUTHOR])
    monkeypatch.setenv("HARNESS_CYCLE_PASS", "1")
    with pytest.raises(ValueError, match="unset nontrial pass"):
        nr.record(recording, verdict(), BOUND, people)
    monkeypatch.setenv("HARNESS_CYCLE_PASS", "initial")
    monkeypatch.delenv("HARNESS_ARC_ID")
    with pytest.raises(ValueError, match="HARNESS_ARC_ID"):
        nr.record(recording, verdict(), BOUND, people)
    assert fr.read_rows() == []
