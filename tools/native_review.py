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
import sys
from pathlib import Path
from uuid import UUID

import finding_record as fr
import review_loop_gate as gate
import review_wrapper_common as rw


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


def record(repo: Path, text: str, expected: dict[str, str], people: rw.ReviewParticipants) -> int:
    outcome = rw.parse_verdict("codex", text, expected, source="native-session")
    if outcome.terminal == "REVIEWER_UNAVAILABLE":
        raise ValueError(outcome.reason)
    outcome.participants = people
    arc, lane = rw.env_arc_and_lane()
    admit_cycle = gate.delivery_admission(
        repo, outcome, producer="codex_review_wrapper", arc_id=arc, lane_id=lane
    )

    def admit(rows: list[dict]) -> None:
        # [LAW:no-ambient-temporal-coupling] correction authors accumulate across
        # the existing arc; a later report cannot remove a prior material author.
        prior = {a for r in rows if r.get("arc_id") == arc for a in r.get("author_sessions") or ()}
        if not prior <= set(people.author_sessions):
            raise ValueError("material author sessions omitted from correction")
        admit_cycle(rows)

    written = rw.emit_outcome(
        outcome,
        producer="codex_review_wrapper",
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
    args = parser.parse_args(argv)
    try:
        # [LAW:effects-at-boundaries] the CLI reads the actual native store, not an
        # arbitrary verdict file or caller-supplied reviewer UUID.
        transcript = args.transcript.resolve(strict=True)
        native_store = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sessions"
        if not transcript.is_relative_to(native_store.resolve(strict=True)):
            raise ValueError("transcript is outside the native Codex session store")
        reviewer, text = read_transcript(transcript)
        if reviewer not in transcript.name:
            raise ValueError("native transcript filename and metadata disagree")
        people = participants(reviewer, args.authors)
        expected = binding(Path.cwd(), args.base, people)
        if args.action == "binding":
            print(json.dumps(expected, indent=2))
            return 0
        if text is None:
            raise ValueError("latest native turn has no completed final answer")
        if fr.cycle_pass_from_env() not in ("initial", "correction"):
            raise ValueError("native delivery requires initial or correction cycle pass")
        return record(Path.cwd(), text, expected, people)
    except (ValueError, OSError, gate.CycleRefusedError) as exc:
        print(f"native-review: GATE_REFUSED: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
