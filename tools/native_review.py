#!/usr/bin/env python3
"""Record an independent existing Codex session's exact frozen review.

No reviewer is launched. Identity and final output come from the native transcript;
the existing schema, cycle admission, log lock and round accounting own delivery.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections.abc import Callable, Mapping
from pathlib import Path
from uuid import UUID

import finding_record as fr
import review_loop_gate as gate
import review_wrapper_common as rw
import workflow_policy as wp

PRODUCER = "codex_review_wrapper"


def session_id(value: str) -> str:
    if str(UUID(value)) != value:
        raise ValueError("session ID must be a canonical UUID")
    return value


def read_transcript(path: Path) -> tuple[str, str | None]:
    """Read the latest turn's completed final answer, never user/tool/earlier output."""
    identity: str | None = None
    final: str | None = None
    complete = False
    for line in path.read_text().splitlines():
        row = json.loads(line)
        payload = row.get("payload", {})
        if row.get("type") == "session_meta":
            found = session_id(payload["id"])
            if identity is not None and identity != found:
                raise ValueError("conflicting native session identities")
            identity = found
        elif row.get("type") == "event_msg":
            if payload.get("type") == "task_started":
                final, complete = None, False
            elif payload.get("type") == "task_complete":
                complete = True
        elif (
            row.get("type") == "response_item"
            and payload.get("type") == "message"
            and payload.get("role") == "assistant"
            and (payload.get("channel") == "final" or payload.get("phase") == "final_answer")
        ):
            final = "\n".join(
                item["text"] for item in payload["content"] if item.get("type") == "output_text"
            )
    if identity is None:
        raise ValueError("native session metadata missing")
    return identity, final if complete else None


def read_selected_turn(
    path: Path, turn_id: str, expected: Mapping[str, str]
) -> tuple[str, str, str]:
    """Select one native completed turn, refusing a later verdict on the same head."""
    session_id(turn_id)
    identity = None
    active = None
    seen: set[str] = set()
    selected_final = selected_model = None
    selected_complete = False
    later_finals: list[str] = []
    for line in path.read_text().splitlines():
        row = json.loads(line)
        payload = row.get("payload", {})
        if row.get("type") == "session_meta":
            found = session_id(payload["id"])
            if identity is not None and identity != found:
                raise ValueError("conflicting native session identities")
            identity = found
        elif row.get("type") == "event_msg" and payload.get("type") == "task_started":
            active = session_id(payload["turn_id"])
            if active in seen:
                raise ValueError("duplicate native turn ID")
            seen.add(active)
        elif row.get("type") == "turn_context" and active == turn_id:
            if (
                payload.get("turn_id") != turn_id
                or not isinstance(payload.get("model"), str)
                or not payload["model"]
            ):
                raise ValueError("selected turn context is invalid")
            if selected_model is not None and selected_model != payload["model"]:
                raise ValueError("conflicting selected turn models")
            selected_model = payload["model"]
        elif row.get("type") == "event_msg" and payload.get("type") == "task_complete":
            if payload.get("turn_id") != active:
                raise ValueError("native turn completion does not match its start")
            if active == turn_id:
                selected_complete = True
            active = None
        elif (
            row.get("type") == "response_item"
            and payload.get("type") == "message"
            and payload.get("role") == "assistant"
            and (payload.get("channel") == "final" or payload.get("phase") == "final_answer")
        ):
            text = "\n".join(
                item["text"] for item in payload["content"] if item.get("type") == "output_text"
            )
            if active == turn_id:
                if selected_final is not None:
                    raise ValueError("multiple selected turn final answers")
                selected_final = text
            elif turn_id in seen and active is not None:
                later_finals.append(text)
    if identity is None:
        raise ValueError("native session metadata missing")
    if not selected_complete or selected_final is None or selected_model is None:
        raise ValueError("selected native turn lacks completed final answer or model context")
    # [LAW:no-ambient-temporal-coupling] Later review evidence of this candidate
    # cannot be bypassed by choosing an older turn, even across a base change.
    for text in later_finals:
        raw = rw.extract_fenced_json(text)
        if raw is not None:
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = None
            if isinstance(body, dict) and body.get("head_sha") == expected["head_sha"]:
                raise ValueError("later verdict supersedes the selected candidate")
        if expected["head_sha"] in text and ("verdict" in text or "findings" in text):
            raise ValueError("later candidate review evidence requires reconciliation")
    return identity, selected_final, selected_model


def binding(repo: Path, base: str, participants: rw.ReviewParticipants) -> dict[str, str]:
    # [LAW:one-source-of-truth] participant provenance is part of the immutable
    # invocation binding; changing the reviewer or material authors invalidates it.
    config = json.dumps(
        {
            "reviewer_session": participants.reviewer_session,
            "author_sessions": sorted(participants.author_sessions),
        },
        sort_keys=True,
    ).encode()
    return rw.compute_binding(
        repo,
        base,
        channel="codex",
        prompt_version="native-session-review-v1",
        config_hash=hashlib.sha256(config).hexdigest(),
    )


def participants(reviewer: str, authors: list[str]) -> rw.ReviewParticipants:
    result = rw.ReviewParticipants(
        session_id(reviewer), tuple(sorted({session_id(a) for a in authors}))
    )
    if not result.author_sessions or reviewer in result.author_sessions:
        raise ValueError("reviewer must be a separate session from every author/correction author")
    return result


def nontrial_admission(
    repo: Path, bound: Mapping[str, str], reviewer: str, arc: str
) -> Callable[[list[dict]], None]:
    """An untagged import: identity-bound evidence of one independent review for an arc
    outside every review cycle. It completes no cycle pass. Reservation, policy and git are
    read now; the returned check is pure over the log as it stands under the append lock."""
    # [LAW:single-enforcer] reservation scope comes from the gate's own reader; a reserved
    # arc keeps its bounded cycle and cannot be recorded around it with an unset pass.
    state = gate._gate_state_in_force(repo, arc)
    if isinstance(state, gate.Refused):
        raise gate.CycleRefusedError(state)
    if not isinstance(state, gate.Inactive):
        raise ValueError(f"{arc} is reserved: record its initial or correction pass")
    # [LAW:one-source-of-truth] the reviewed commit's tracked policy decides, as for cycle
    # passes; an uncommitted edit or a trial enrollment cannot select this route.
    policy = wp.load_policy(
        rw._git(repo, "show", f"{bound['head_sha']}:.harness/workflow-policy.json").encode()
    )
    if not wp.streamlined_delivery(policy) or wp.arc_unit(policy, arc) is not None:
        raise ValueError(f"{arc} is not nontrial work under the reviewed head's delivery policy")
    review = (bound["head_sha"], bound["diff_digest"], reviewer)

    def check(rows: list[dict]) -> None:
        arc_rows = [r for r in rows if r.get("arc_id") == arc]
        if any(r.get("cycle_pass") is not None for r in arc_rows):
            raise ValueError(f"{arc} has cycle history: record its next tagged pass")
        if any(
            r.get("producer") == PRODUCER
            and (r.get("head_sha"), r.get("diff_digest"), r.get("reviewer_session")) == review
            for r in arc_rows
        ):
            raise ValueError("this native review is already recorded")

    return check


def pass_admission(
    repo: Path, outcome: rw.ReviewOutcome, people: rw.ReviewParticipants, arc: str, lane: str
) -> Callable[[list[dict]], None]:
    # [LAW:dataflow-not-control-flow] the cycle pass is the one discriminator: a tagged pass
    # keeps the existing bounded-cycle admission, an unset pass is the nontrial import.
    cycle_pass = fr.cycle_pass_from_env()
    if cycle_pass is None:
        return nontrial_admission(repo, outcome.binding, people.reviewer_session, arc)
    if cycle_pass not in ("initial", "correction"):
        raise ValueError("native delivery requires initial, correction or an unset nontrial pass")
    return gate.delivery_admission(repo, outcome, producer=PRODUCER, arc_id=arc, lane_id=lane)


def record(repo: Path, text: str, expected: dict[str, str], people: rw.ReviewParticipants) -> int:
    outcome = rw.parse_verdict("codex", text, expected, source="native-session")
    if outcome.terminal == "REVIEWER_UNAVAILABLE":
        raise ValueError(outcome.reason)
    outcome.participants = people
    if not os.environ.get("HARNESS_ARC_ID"):
        # the branch fallback arc would bind the review to an arc nobody claimed
        raise ValueError("native delivery requires an explicit HARNESS_ARC_ID")
    arc, lane = rw.env_arc_and_lane()
    admit_pass = pass_admission(repo, outcome, people, arc, lane)

    def admit(rows: list[dict]) -> None:
        # [LAW:no-ambient-temporal-coupling] correction authors accumulate across
        # the existing arc; a later report cannot remove a prior material author.
        prior = {a for r in rows if r.get("arc_id") == arc for a in r.get("author_sessions") or ()}
        if not prior <= set(people.author_sessions):
            raise ValueError("material author sessions omitted from correction")
        admit_pass(rows)

    written = rw.emit_outcome(
        outcome,
        producer=PRODUCER,
        arc_id=arc,
        lane_id=lane,
        round_n=None,
        admit=admit,
    )
    rw.record_round_outcome_if_reserved(
        arc,
        written[0]["round_n"],
        channel="codex",
        terminal=outcome.terminal,
        finding_count=len(outcome.findings),
    )
    print(
        f"native-review: {outcome.terminal}; session {people.reviewer_session}; "
        f"round {written[0]['round_n']}"
    )
    return rw.exit_code(outcome)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("binding", "record"))
    parser.add_argument("--transcript", required=True, type=Path)
    parser.add_argument("--authors", required=True, nargs="+")
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--turn-id", help="select a completed native turn for record")
    args = parser.parse_args(argv)
    try:
        # [LAW:effects-at-boundaries] the CLI reads the actual native store, not an
        # arbitrary verdict file or caller-supplied reviewer UUID.
        transcript = args.transcript.resolve(strict=True)
        native_store = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sessions"
        if not transcript.is_relative_to(native_store.resolve(strict=True)):
            raise ValueError("transcript is outside the native Codex session store")
        if args.turn_id and args.action != "record":
            raise ValueError("--turn-id applies to record only")
        reviewer, text = read_transcript(transcript)
        if reviewer not in transcript.name:
            raise ValueError("native transcript filename and metadata disagree")
        people = participants(reviewer, args.authors)
        expected = binding(Path.cwd(), args.base, people)
        if args.action == "binding":
            print(json.dumps(expected, indent=2))
            return 0
        if args.turn_id:
            selected_reviewer, text, model = read_selected_turn(transcript, args.turn_id, expected)
            if selected_reviewer != reviewer:
                raise ValueError("selected turn session identity disagrees")
            print(f"native-review: selected turn {args.turn_id}; model {model}", file=sys.stderr)
        if text is None:
            raise ValueError("latest native turn has no completed final answer")
        return record(Path.cwd(), text, expected, people)
    except (
        ValueError,
        TypeError,
        KeyError,
        OSError,
        subprocess.CalledProcessError,
        gate.CycleRefusedError,
    ) as exc:
        print(f"native-review: GATE_REFUSED: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
