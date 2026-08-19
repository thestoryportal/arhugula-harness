"""C-HE-15/16/17 fail-closed review wrapper battery. CLIs are mocked; no skip."""

from __future__ import annotations

import json
import sys
from itertools import count
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import finding_record as fr
import review_wrapper_common as rw

EXPECTED = {
    "head_sha": "a" * 40,
    "base_sha": "b" * 40,
    "diff_digest": "c" * 64,
    "reviewer_identity": "codex-review",
    "prompt_version": "pv1",
    "config_hash": "ch1",
}


def _block(verdict="APPROVE", findings=None, **over):
    body = {"verdict": verdict, "findings": findings or [], **EXPECTED, **over}
    return "chatter\n```json\n" + json.dumps(body) + "\n```\ntrailer\n"


# ── C-HE-15 §1/§2: only a positive schema parse counts ──────────────────────
# mutation-probe: make parse_verdict() return APPROVE when text is empty (exit-code keying)
def test_empty_stdout_exit0_is_unavailable():
    out = rw.parse_verdict("codex", "", EXPECTED)
    assert out.terminal == "REVIEWER_UNAVAILABLE"
    assert rw.parse_verdict("codex", "   \n", EXPECTED).terminal == "REVIEWER_UNAVAILABLE"


def test_truncated_json_is_unavailable():
    text = _block()[:-12]  # cut inside the fence
    assert rw.parse_verdict("codex", text, EXPECTED).terminal == "REVIEWER_UNAVAILABLE"


def test_no_fenced_block_is_unavailable():
    assert (
        rw.parse_verdict("codex", "VERDICT: APPROVE", EXPECTED).terminal == "REVIEWER_UNAVAILABLE"
    )


def test_out_of_enum_severity_is_unavailable():
    text = _block("BLOCK", [{"severity": "P0", "location": "x", "message": "m"}])
    assert rw.parse_verdict("codex", text, EXPECTED).terminal == "REVIEWER_UNAVAILABLE"


def test_extra_property_on_finding_is_unavailable():
    text = _block("BLOCK", [{"severity": "P1", "location": "x", "message": "m", "extra": 1}])
    assert rw.parse_verdict("codex", text, EXPECTED).terminal == "REVIEWER_UNAVAILABLE"


def test_extra_top_level_property_is_unavailable():
    assert rw.parse_verdict("codex", _block(note="x"), EXPECTED).terminal == "REVIEWER_UNAVAILABLE"


def test_blank_location_or_message_is_unavailable():
    """A finding row must be grounded (C-HE-24 §1); an ungrounded reviewer finding fails the
    channel schema at parse time rather than the record at write time."""
    for f in (
        {"severity": "P1", "location": "", "message": "m"},
        {"severity": "P1", "location": "x", "message": ""},
    ):
        assert (
            rw.parse_verdict("codex", _block("BLOCK", [f]), EXPECTED).terminal
            == "REVIEWER_UNAVAILABLE"
        )


def test_verdict_findings_consistency_is_enforced_by_schema():
    """Codex round-1 P2 on this arc: BLOCK with no findings / APPROVE with findings are
    contradictory results and must not parse."""
    assert (
        rw.parse_verdict("codex", _block("BLOCK", []), EXPECTED).terminal == "REVIEWER_UNAVAILABLE"
    )
    text = _block("APPROVE", [{"severity": "P3", "location": "x", "message": "m"}])
    assert rw.parse_verdict("codex", text, EXPECTED).terminal == "REVIEWER_UNAVAILABLE"
    for ch in ("codex", "gemini", "merge-gate"):
        assert len(rw.load_schema(ch)["allOf"]) == 2


def test_well_formed_parses():
    out = rw.parse_verdict(
        "codex", _block("BLOCK", [{"severity": "P1", "location": "x", "message": "m"}]), EXPECTED
    )
    assert out.terminal == "BLOCK" and len(out.findings) == 1 and out.binding == EXPECTED
    assert out.source == "stdout" and out.failure_class is None


def test_last_fenced_block_wins():
    text = _block("BLOCK", [{"severity": "P1", "location": "x", "message": "m"}]) + _block(
        "APPROVE"
    )
    assert rw.parse_verdict("codex", text, EXPECTED).terminal == "APPROVE"


# ── C-HE-15 §3/§4: binding byte-compare, all six fields ─────────────────────
_SHAPE_VALID_OTHER = {
    "head_sha": "d" * 40,
    "base_sha": "e" * 40,
    "diff_digest": "f" * 64,
    "reviewer_identity": "gemini-review",
    "prompt_version": "pv2",
    "config_hash": "ch2",
}


@pytest.mark.parametrize("field", rw.BINDING_FIELDS)
def test_binding_mismatch_is_unavailable(field):
    """Every binding field is byte-compared against the wrapper's OWN value: a shape-valid but
    foreign value is refused with the field named (reviewer_identity is a schema `const`, so
    the schema refuses it one step earlier -- still REVIEWER_UNAVAILABLE)."""
    text = _block(**{field: _SHAPE_VALID_OTHER[field]})
    out = rw.parse_verdict("codex", text, EXPECTED)
    assert out.terminal == "REVIEWER_UNAVAILABLE"
    if field == "reviewer_identity":
        assert out.reason.startswith("schema:")
    else:
        assert f"binding mismatch on {field}" in out.reason
    # a shape-INVALID value is refused too (by the schema), never accepted
    assert rw.parse_verdict("codex", _block(**{field: "different"}), EXPECTED).terminal == (
        "REVIEWER_UNAVAILABLE"
    )


def test_binding_mismatch_on_shape_valid_value_is_caught_by_byte_compare():
    """A value that satisfies the schema's pattern but is not THIS invocation's value."""
    out = rw.parse_verdict("codex", _block(head_sha="d" * 40), EXPECTED)
    assert out.terminal == "REVIEWER_UNAVAILABLE" and "binding mismatch on head_sha" in out.reason


def test_schema_requires_all_six_binding_fields():
    schema = rw.load_schema("codex")
    assert set(rw.BINDING_FIELDS) <= set(schema["required"])


# ── U-HE-03: per-channel schema shape ────────────────────────────────────────
@pytest.mark.parametrize("channel", ["codex", "gemini", "merge-gate"])
def test_channel_schema_shape(channel):
    s = rw.load_schema(channel)
    assert s["additionalProperties"] is False
    assert s["properties"]["verdict"]["enum"] == ["APPROVE", "BLOCK"]
    item = s["properties"]["findings"]["items"]
    assert item["additionalProperties"] is False
    assert item["properties"]["severity"]["enum"] == ["P1", "P2", "P3"]
    assert set(rw.BINDING_FIELDS) <= set(s["required"])


def test_channel_schema_pins_reviewer_identity():
    assert rw.load_schema("codex")["properties"]["reviewer_identity"] == {"const": "codex-review"}
    assert rw.load_schema("gemini")["properties"]["reviewer_identity"] == {"const": "gemini-review"}
    mg = rw.load_schema("merge-gate")["properties"]["reviewer_identity"]
    assert mg["pattern"] == "^merge-gate-[a-z-]+$"


# ── C-HE-16 §4: classifier table, row by row; unknown → transient ───────────
@pytest.mark.parametrize(
    "channel,text,expected",
    [
        ("codex", "codex-cli requires a newer version of Codex", "permanent"),
        ("codex", "Error: not logged in", "permanent"),
        ("codex", "HTTP 401 Unauthorized", "permanent"),
        ("codex", "HTTP 403 Forbidden", "permanent"),
        ("codex", "bash: codex: command not found", "permanent"),
        ("codex", "rate limit exceeded (429)", "transient"),
        ("codex", "read ETIMEDOUT", "transient"),
        ("codex", "ECONNRESET", "transient"),
        ("codex", "command timed out after 550 seconds", "transient"),
        ("gemini", "antigravity CLI not logged in", "permanent"),
        ("gemini", "Antigravity is not installed", "permanent"),
        ("gemini", "ERROR: agy (Antigravity CLI) not found on PATH.", "permanent"),
        ("gemini", "RESOURCE_EXHAUSTED", "transient"),
        ("gemini", "deadline exceeded", "transient"),
        ("codex", "some brand new vendor error text", "transient"),
        ("codex", "", "transient"),
        ("gemini", "not logged in", "transient"),  # a codex-only row never fires for gemini
    ],
)
def test_classifier_table(channel, text, expected):
    assert rw.classify(channel, text) == expected


def test_classifier_table_shape_is_one_row_per_channel_regex_class():
    for ch, rx, cls in rw.CLASSIFIER:
        assert ch in ("codex", "gemini") and cls in ("permanent", "transient")
        assert hasattr(rx, "search")


# ── C-HE-16 §2/§3: retry parameters ─────────────────────────────────────────
def test_retry_constants():
    assert (
        rw.PER_ATTEMPT_TIMEOUT_S,
        rw.MAX_ATTEMPTS,
        rw.TOTAL_BUDGET_S,
        rw.SECOND_ATTEMPT_MARGIN_S,
    ) == (550.0, 2, 1260.0, 30.0)
    assert rw.TERMINAL_STATES == ("APPROVE", "BLOCK", "REVIEWER_UNAVAILABLE")


def test_permanent_failure_skips_retry():
    calls = count()

    def invoke(timeout):
        next(calls)
        return rw.Attempt(stdout="", stderr="Error: not logged in", returncode=0, timed_out=False)

    out = rw.run_with_retry(
        invoke, channel="codex", expected=EXPECTED, deadline=10_000.0, clock=lambda: 0.0
    )
    assert out.terminal == "REVIEWER_UNAVAILABLE" and out.failure_class == "permanent"
    assert next(calls) == 1  # exactly one attempt made


def test_auth_error_text_with_exit0_is_permanent_unavailable():
    """C-HE-15 verification row: auth-error text + exit 0 → REVIEWER_UNAVAILABLE(permanent)."""

    def invoke(timeout):
        return rw.Attempt(
            stdout="Error: not logged in. Run codex login.",
            stderr="",
            returncode=0,
            timed_out=False,
        )

    out = rw.run_with_retry(
        invoke, channel="codex", expected=EXPECTED, deadline=10_000.0, clock=lambda: 0.0
    )
    assert out.terminal == "REVIEWER_UNAVAILABLE" and out.failure_class == "permanent"


def test_transient_then_success_uses_two_attempts_and_dynamic_second_timeout():
    seen: list[float] = []
    now = {"t": 0.0}

    def invoke(timeout):
        seen.append(timeout)
        now["t"] += 800.0  # first attempt burned 800 s of the 1260 s budget
        if len(seen) == 1:
            return rw.Attempt(
                stdout="", stderr="", returncode=0, timed_out=False
            )  # empty first attempt
        return rw.Attempt(stdout=_block(), stderr="", returncode=0, timed_out=False)

    out = rw.run_with_retry(
        invoke,
        channel="codex",
        expected=EXPECTED,
        deadline=rw.TOTAL_BUDGET_S,
        clock=lambda: now["t"],
    )
    assert out.terminal == "APPROVE"
    assert seen[0] == rw.PER_ATTEMPT_TIMEOUT_S
    # attempt 2 timeout = min(550, remaining - 30) = min(550, 1260-800-30) = 430
    assert seen[1] == pytest.approx(430.0)


def test_empty_on_second_attempt_is_unavailable_transient():
    n = count()

    def invoke(timeout):
        next(n)
        return rw.Attempt(stdout="", stderr="", returncode=0, timed_out=False)

    out = rw.run_with_retry(
        invoke, channel="codex", expected=EXPECTED, deadline=10_000.0, clock=lambda: 0.0
    )
    assert out.terminal == "REVIEWER_UNAVAILABLE" and out.failure_class == "transient"
    assert next(n) == 2  # never a third attempt (max_attempts = 2)


def test_timeout_is_transient_and_retried_once():
    n = count()

    def invoke(timeout):
        next(n)
        return rw.Attempt(stdout="", stderr="", returncode=None, timed_out=True)

    out = rw.run_with_retry(
        invoke, channel="codex", expected=EXPECTED, deadline=10_000.0, clock=lambda: 0.0
    )
    assert out.terminal == "REVIEWER_UNAVAILABLE" and out.failure_class == "transient"
    assert "timed out" in out.reason and next(n) == 2


def test_budget_exhaustion_is_hitl_recoverable():
    def invoke(timeout):
        return rw.Attempt(stdout="", stderr="", returncode=None, timed_out=True)

    out = rw.run_with_retry(
        invoke, channel="codex", expected=EXPECTED, deadline=1.0, clock=lambda: 5.0
    )
    assert out.terminal == "REVIEWER_UNAVAILABLE" and out.reason.startswith("HITL-recoverable")
    assert out.failure_class == "transient"
    assert out.binding == EXPECTED  # an unavailable outcome is still bound to its invocation


def test_exhausted_budget_never_invokes_the_channel():
    def invoke(timeout):
        pytest.fail("must not invoke past the deadline")

    out = rw.run_with_retry(
        invoke, channel="codex", expected=EXPECTED, deadline=1.0, clock=lambda: 5.0
    )
    assert out.terminal == "REVIEWER_UNAVAILABLE"


# ── C-HE-17: failover chain ─────────────────────────────────────────────────
def _unavail(cls):
    return rw.ReviewOutcome("REVIEWER_UNAVAILABLE", "codex", cls, "x", [], None, None)


def test_failover_invoked_once_on_primary_unavailable_and_blocks():
    n = count()

    def failover():
        next(n)
        return rw.ReviewOutcome(
            "BLOCK",
            "gemini",
            None,
            "",
            [{"severity": "P1", "location": "l", "message": "m"}],
            EXPECTED,
            "stdout",
        )

    p, f = rw.run_with_failover(lambda: _unavail("permanent"), failover)
    assert p.terminal == "REVIEWER_UNAVAILABLE"
    assert f is not None and f.terminal == "BLOCK" and next(n) == 1
    assert rw.exit_code(f) == 1


def test_failover_unavailable_blocks_with_both_reasons():
    p, f = rw.run_with_failover(
        lambda: _unavail("permanent"),
        lambda: rw.ReviewOutcome(
            "REVIEWER_UNAVAILABLE", "gemini", "transient", "y", [], None, None
        ),
    )
    assert f is not None and rw.exit_code(p) == 2 and rw.exit_code(f) == 2
    assert p.reason == "x" and f.reason == "y"


def test_failover_not_invoked_when_primary_terminal():
    for terminal in ("APPROVE", "BLOCK"):
        primary = rw.ReviewOutcome(terminal, "codex", None, "", [], EXPECTED, "stdout")
        p, f = rw.run_with_failover(lambda p=primary: p, lambda: pytest.fail("must not run"))
        assert f is None and p.terminal == terminal


def test_exit_codes():
    assert rw.exit_code(rw.ReviewOutcome("APPROVE", "codex", None, "")) == 0
    assert rw.exit_code(rw.ReviewOutcome("BLOCK", "codex", None, "")) == 1
    assert rw.exit_code(_unavail("transient")) == 2


# ── outcome rows: reviewer_unavailable → C-HE-24 rows with fail_class ───────
def test_unavailable_outcome_row_carries_fail_class():
    rows = rw.outcome_rows(
        _unavail("permanent"),
        producer="codex_review_wrapper",
        arc_id="pr-1",
        lane_id="h-w-1",
        round_n=1,
    )
    assert (
        rows[0]["record_kind"] == "reviewer_unavailable"
        and rows[0]["finding_type"] == "permanent-fail-exit"
    )
    assert (
        rows[0]["severity"] == "hard"
        and rows[0]["cause_attribution"] == "reviewer_unavailable_permanent"
    )
    rows = rw.outcome_rows(
        _unavail("transient"),
        producer="codex_review_wrapper",
        arc_id="pr-1",
        lane_id="h-w-1",
        round_n=1,
    )
    assert rows[0]["finding_type"] == "transient-retry" and rows[0]["severity"] == "warn"
    assert "finding_id" not in rows[0]  # minted at append time, never a per-invocation ordinal


def test_outcome_rows_one_finding_row_per_finding_bound_to_head():
    out = rw.ReviewOutcome(
        "BLOCK",
        "codex",
        None,
        "",
        [
            {"severity": "P1", "location": "a.py:1", "message": "m1"},
            {"severity": "P2", "location": "b.py:2", "message": "m2"},
        ],
        EXPECTED,
        "stdout",
    )
    rows = rw.outcome_rows(
        out, producer="codex_review_wrapper", arc_id="pr-1", lane_id="h-w-1", round_n=3
    )
    assert [r["record_kind"] for r in rows] == ["finding", "finding"]
    assert [r["severity"] for r in rows] == ["P1", "P2"] and rows[0]["head_sha"] == "a" * 40
    assert rows[0]["finding_type"] == "terminal-block" and rows[0]["round_n"] == 3
    approve = rw.ReviewOutcome("APPROVE", "codex", None, "", [], EXPECTED, "stdout")
    assert rw.outcome_rows(approve, producer="p", arc_id="a", lane_id="l", round_n=0) == []


def test_emit_outcome_mints_distinct_ids_on_rerun_at_same_head(tmp_path: Path):
    """A rerun on the same head re-reporting the same location gets a NEW observation id
    (next_finding_id under the log lock), never a rejected core mutation."""
    log = tmp_path / "gate.jsonl"
    out = rw.ReviewOutcome(
        "BLOCK",
        "codex",
        None,
        "",
        [{"severity": "P1", "location": "a.py:1", "message": "m1"}],
        EXPECTED,
        "stdout",
    )
    first = rw.emit_outcome(
        out, producer="codex_review_wrapper", arc_id="pr-1", lane_id="h-w-1", round_n=1, path=log
    )
    out2 = rw.ReviewOutcome(
        "BLOCK",
        "codex",
        None,
        "",
        [{"severity": "P1", "location": "a.py:1", "message": "m1 again"}],
        EXPECTED,
        "stdout",
    )
    second = rw.emit_outcome(
        out2, producer="codex_review_wrapper", arc_id="pr-1", lane_id="h-w-1", round_n=2, path=log
    )
    assert first[0]["finding_id"].endswith(":1") and second[0]["finding_id"].endswith(":2")
    rows = fr.read_rows(log)
    assert len(rows) == 2 and all(r["producer"] == "codex_review_wrapper" for r in rows)
    for r in rows:
        fr.validate(r)


def test_emit_outcome_unavailable_row_uses_nohead_token(tmp_path: Path):
    log = tmp_path / "gate.jsonl"
    rows = rw.emit_outcome(
        _unavail("transient"),
        producer="codex_review_wrapper",
        arc_id="pr-1",
        lane_id="h-w-1",
        round_n=1,
        path=log,
    )
    assert (
        rows[0]["finding_id"].startswith("codex_review_wrapper:nohead:")
        and rows[0]["head_sha"] is None
    )
    assert fr.read_rows(log)[0]["record_kind"] == "reviewer_unavailable"


def test_env_arc_and_lane_never_empty_never_colon(monkeypatch):
    monkeypatch.setenv("HARNESS_ARC_ID", "pr:1")
    monkeypatch.setenv("HARNESS_LANE_ID", "host:w:1")
    assert rw.env_arc_and_lane() == ("pr_1", "host_w_1")
    monkeypatch.delenv("HARNESS_ARC_ID")
    monkeypatch.delenv("HARNESS_LANE_ID")
    arc, lane = rw.env_arc_and_lane()
    assert arc.startswith("branch-") and lane.endswith("-nolane") and ":" not in arc + lane


# ── U-HE-04: codex_review.py wrapper (C-HE-18) ───────────────────────────────
import os  # noqa: E402
import time  # noqa: E402
import types  # noqa: E402

import codex_review as cr  # noqa: E402


def _artifact_tree(tmp_path: Path, head: str, mtime: float) -> Path:
    d = tmp_path / "2026" / "08" / "18"
    d.mkdir(parents=True)
    p = d / "rollout-2026-08-18T00-00-00-abc.jsonl"
    # real shape: the assistant text (fenced block, newlines ESCAPED inside the string) nested
    # in a JSONL envelope
    p.write_text(
        json.dumps(
            {
                "type": "response_item",
                "payload": {
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": _block(head_sha=head)}],
                },
            }
        )
        + "\n"
    )
    os.utime(p, (mtime, mtime))
    return p


def test_artifact_text_decodes_jsonl_envelopes(tmp_path):
    p = _artifact_tree(tmp_path, "a" * 40, mtime=1.0)
    raw = p.read_text()
    decoded = cr.artifact_text(p)
    assert rw.extract_fenced_json(raw) is None  # the raw envelope hides the fence behind escaping
    assert rw.extract_fenced_json(decoded) is not None  # decoding exposes it


def test_session_artifact_discovery_newest_after_start_containing_head(tmp_path):
    old = _artifact_tree(tmp_path / "a", "a" * 40, mtime=100.0)
    hit = _artifact_tree(tmp_path / "b", "a" * 40, mtime=200.0)
    assert (
        cr.find_session_artifact("a" * 40, started_at=150.0, now=210.0, root=tmp_path / "b") == hit
    )
    assert (
        cr.find_session_artifact("a" * 40, started_at=150.0, now=210.0, root=tmp_path / "a") is None
    )
    assert old.exists()
    # a fresh artifact for a DIFFERENT head is never picked up (binding to this invocation)
    assert (
        cr.find_session_artifact("d" * 40, started_at=150.0, now=210.0, root=tmp_path / "b") is None
    )
    assert (
        cr.find_session_artifact("a" * 40, started_at=0.0, now=1.0, root=tmp_path / "missing")
        is None
    )


def test_log_frozen_but_artifact_has_verdict_parses_from_artifact(tmp_path, monkeypatch):
    """PR #1386 mode: stdout inconclusive, session artifact carries the verdict."""
    head = "a" * 40
    _artifact_tree(tmp_path, head, mtime=time.time() + 1)
    monkeypatch.setattr(cr, "SESSIONS_DIR", tmp_path)
    monkeypatch.setattr(cr, "_binding", lambda repo, base: {**EXPECTED, "head_sha": head})

    def invoke(timeout):
        return rw.Attempt(stdout="working...\n", stderr="", returncode=0, timed_out=False)

    out = cr.run_codex_review(Path("."), "main", invoke=invoke)
    assert out.terminal == "APPROVE" and out.source == "session-artifact"


def test_artifact_with_foreign_binding_is_still_unavailable(tmp_path, monkeypatch):
    """The artifact path requires the SAME positive parse + byte-compare (C-HE-18 §2)."""
    _artifact_tree(tmp_path, "a" * 40, mtime=time.time() + 1)
    monkeypatch.setattr(cr, "SESSIONS_DIR", tmp_path)
    monkeypatch.setattr(cr, "ARTIFACT_LAG_S", 0.0)
    monkeypatch.setattr(cr, "_binding", lambda repo, base: {**EXPECTED, "head_sha": "d" * 40})
    out = cr.run_codex_review(Path("."), "main", invoke=lambda t: rw.Attempt("", "", 0, False))
    assert out.terminal == "REVIEWER_UNAVAILABLE" and out.source != "session-artifact"


def test_artifact_polling_capped_by_shared_deadline(tmp_path, monkeypatch):
    """Two 550 s attempts + artifact polling must not exceed the 1260 s budget."""
    monkeypatch.setattr(cr, "SESSIONS_DIR", tmp_path / "empty")
    monkeypatch.setattr(cr, "_binding", lambda repo, base: EXPECTED)
    fake_now = {"t": 1000.0}
    monkeypatch.setattr(cr.time, "time", lambda: fake_now["t"])
    monkeypatch.setattr(cr.time, "sleep", lambda s: fake_now.__setitem__("t", fake_now["t"] + s))
    clock = {"m": 0.0}

    def invoke(timeout):
        clock["m"] += timeout
        fake_now["t"] += timeout
        return rw.Attempt("", "", 0, False)

    out = cr.run_codex_review(Path("."), "main", invoke=invoke, clock=lambda: clock["m"])
    assert out.terminal == "REVIEWER_UNAVAILABLE"
    assert fake_now["t"] - 1000.0 <= rw.TOTAL_BUDGET_S + 1e-6


def test_zero_byte_output_emits_finding_row(tmp_path, monkeypatch):
    monkeypatch.setattr(cr, "SESSIONS_DIR", tmp_path / "empty")
    monkeypatch.setattr(cr, "_binding", lambda repo, base: EXPECTED)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path / "gate.jsonl")
    monkeypatch.setattr(cr, "ARTIFACT_LAG_S", 0.0)
    rc = cr.main(["--base", "main", "--invoke-test-empty"])
    assert rc == 2
    rows = fr.read_rows(tmp_path / "gate.jsonl")
    assert rows and rows[0]["producer"] == "codex_review_wrapper"
    assert rows[0]["record_kind"] == "reviewer_unavailable"
    assert rows[0]["finding_type"] == "transient-retry" and rows[0]["head_sha"] == "a" * 40
    fr.validate(rows[0])


def test_wrapper_persists_round_outcome_on_reservation(monkeypatch):
    calls = []
    stub = types.SimpleNamespace(
        current=lambda arc_id: (1, {"state": "open"}),
        record_round_outcome=lambda arc_id, n, **kw: calls.append((arc_id, n, kw)),
    )
    monkeypatch.setitem(sys.modules, "reservations", stub)
    rw.record_round_outcome_if_reserved(
        "pr-1", 2, channel="codex", terminal="REVIEWER_UNAVAILABLE", finding_count=0
    )
    assert calls == [
        ("pr-1", 2, {"channel": "codex", "terminal": "REVIEWER_UNAVAILABLE", "finding_count": 0})
    ]
    # no reservation for this arc → no-op
    stub.current = lambda arc_id: None
    rw.record_round_outcome_if_reserved(
        "pr-2", 1, channel="codex", terminal="APPROVE", finding_count=0
    )
    assert len(calls) == 1


def test_wrapper_round_outcome_noop_without_reservation_substrate(monkeypatch, capsys):
    """Pre-S4b: tools/reservations.py is absent → silent no-op, no stderr noise."""
    monkeypatch.setitem(sys.modules, "reservations", None)  # forces ImportError
    rw.record_round_outcome_if_reserved(
        "pr-1", 1, channel="codex", terminal="APPROVE", finding_count=0
    )
    assert capsys.readouterr().err == ""


def test_build_command_is_codex_review_with_positional_instructions():
    """codex-cli 0.146.0: the PROMPT is a review target, mutually exclusive with `--base`
    (`error: the argument '--base <BRANCH>' cannot be used with '[PROMPT]'`, probed live)."""
    cmd = cr.build_command("INSTR")
    assert cmd[:2] == ["codex", "review"] and cmd[-1] == "INSTR"
    assert "--base" not in cmd and 'preferred_auth_method="chatgpt"' in cmd


def test_review_instructions_name_the_bound_diff_and_carry_all_six_binding_values():
    text = cr.review_instructions(EXPECTED)
    assert f"git diff {EXPECTED['base_sha']} {EXPECTED['head_sha']}" in text
    for k, v in EXPECTED.items():
        assert f"{k}={v}" in text
    assert "```json" in text and "APPROVE|BLOCK" in text


def test_stderr_echo_is_a_second_source_under_the_same_bar(monkeypatch, tmp_path):
    """`codex review` echoes the transcript on stderr; the same parse + byte-compare applies."""
    monkeypatch.setattr(cr, "SESSIONS_DIR", tmp_path / "empty")
    monkeypatch.setattr(cr, "_binding", lambda repo, base: EXPECTED)
    monkeypatch.setattr(cr, "ARTIFACT_LAG_S", 0.0)
    out = cr.run_codex_review(
        Path("."), "main", invoke=lambda t: rw.Attempt("", "transcript\n" + _block(), 0, False)
    )
    assert out.terminal == "APPROVE" and out.source == "stderr"
    foreign = _block(head_sha="d" * 40)
    out = cr.run_codex_review(Path("."), "main", invoke=lambda t: rw.Attempt("", foreign, 0, False))
    assert out.terminal == "REVIEWER_UNAVAILABLE"


def test_default_invoke_maps_run_bounded_timeout_to_timed_out(monkeypatch):
    import subprocess

    monkeypatch.setattr(
        cr,
        "run_bounded",
        lambda *a, **k: subprocess.CompletedProcess(
            a[0], 124, "", "command timed out after 1 seconds"
        ),
    )
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-leak")
    seen = {}

    def fake_rb(cmd, *, cwd, timeout, env):
        seen["env"] = env
        return subprocess.CompletedProcess(cmd, 124, "", "command timed out after 1 seconds")

    monkeypatch.setattr(cr, "run_bounded", fake_rb)
    att = cr._default_invoke(Path("."), "I")(1.0)
    assert att.timed_out and att.returncode == 124
    assert "OPENAI_API_KEY" not in seen["env"]  # subscription auth only, never the metered key


def test_gate_log_env_override_redirects_the_process_tree(tmp_path: Path):
    """`HARNESS_GATE_LOG` (finding_record) is the seam subprocess fixtures use so a reviewer run
    never appends to the tracked log."""
    import subprocess

    env = {**os.environ, "HARNESS_GATE_LOG": str(tmp_path / "g.jsonl")}
    out = subprocess.run(
        [sys.executable, "-c", "import finding_record as fr; print(fr.GATE_LOG_JSONL)"],
        cwd=Path(__file__).resolve().parent,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert out == str(tmp_path / "g.jsonl")
    assert fr.GATE_LOG_JSONL.name == "merge-gate-log.jsonl"  # this process: the default
