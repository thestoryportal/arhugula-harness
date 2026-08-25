"""B-215 review-loop admission gate battery.

Covers the pure decision core (no mocks — [LAW:effects-at-boundaries]), the
attest CLI edges in throwaway git repos, and the codex_review.main() wiring
(gate fires BEFORE any reviewer subprocess; refusal is exit 3 and is NOT a
review terminal per C-HE-16 §3 — no C-HE-24 row, no round outcome).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import finding_record as fr
import review_loop_gate as rlg
import review_wrapper_common as rw

ARC = "b-000-test"
HEAD = "a" * 40
BASE = "b" * 40
DIGEST = "c" * 64
LOOP_PRODUCER = "codex_review_wrapper"


def _row(round_n: int, kind: str, finding_id: str | None = None, **over) -> dict:
    base = dict(
        arc_id=ARC,
        producer=LOOP_PRODUCER,
        round_n=round_n,
        record_kind=kind,
        finding_id=finding_id,
    )
    base.update(over)
    return base


def _pf(head=HEAD, digest=DIGEST, arc=ARC) -> rlg.PreflightAttestation:
    return rlg.PreflightAttestation(
        arc_id=arc, head_sha=head, diff_digest=digest, hit_labels=(), answers_digest="d", ts="t"
    )


def _sw(round_n: int, ids: tuple[str, ...], head=HEAD, arc=ARC) -> rlg.SweepAttestation:
    return rlg.SweepAttestation(
        arc_id=arc, round_n=round_n, head_sha=head, finding_ids=ids, answers_digest="d", ts="t"
    )


def _state(preflights=(), sweeps=(), extensions=()) -> rlg.GateState:
    return rlg.GateState(preflights=preflights, sweeps=sweeps, extensions=extensions)


def _decide(state, rows, **over):
    kw = dict(arc_id=ARC, head_sha=HEAD, diff_digest=DIGEST)
    kw.update(over)
    return rlg.decide(state, rows, **kw)


# ── pure core: entry gate ────────────────────────────────────────────────────


def test_round0_without_preflight_refuses():
    d = _decide(_state(), [])
    assert isinstance(d, rlg.Refused)
    assert d.code == "PREFLIGHT_MISSING"
    # loop-reachable recipe: names the attest recipe and the attest-after-commit discipline
    assert "review-attest-preflight" in d.recipe
    assert "commit" in d.recipe.lower()


def test_round0_with_bound_preflight_allows():
    d = _decide(_state(preflights=(_pf(),)), [])
    assert d == rlg.Allowed(round_n=1)


def test_round0_preflight_wrong_head_refuses_stale():
    d = _decide(_state(preflights=(_pf(head="e" * 40),)), [])
    assert isinstance(d, rlg.Refused)
    assert d.code == "PREFLIGHT_STALE"


def test_round0_preflight_wrong_digest_refuses_stale():
    d = _decide(_state(preflights=(_pf(digest="f" * 64),)), [])
    assert isinstance(d, rlg.Refused)
    assert d.code == "PREFLIGHT_STALE"


# ── pure core: post-round sweep gate ─────────────────────────────────────────


def test_block_round_without_sweep_refuses_and_enumerates_ids():
    rows = [_row(1, "finding", "cw:aa:11:1"), _row(1, "finding", "cw:aa:11:2")]
    d = _decide(_state(preflights=(_pf(),)), rows)
    assert isinstance(d, rlg.Refused)
    assert d.code == "SWEEP_MISSING"
    # the refusal must hand the agent the exact unanswered ids — no log scraping
    assert "cw:aa:11:1" in d.detail and "cw:aa:11:2" in d.detail
    assert "review-attest-sweep" in d.recipe


def test_block_round_with_covering_sweep_allows():
    rows = [_row(1, "finding", "cw:aa:11:1")]
    d = _decide(_state(sweeps=(_sw(1, ("cw:aa:11:1",)),)), rows)
    assert d == rlg.Allowed(round_n=2)


def test_sweep_missing_one_finding_names_it():
    rows = [_row(1, "finding", "cw:aa:11:1"), _row(1, "finding", "cw:aa:11:2")]
    d = _decide(_state(sweeps=(_sw(1, ("cw:aa:11:1",)),)), rows)
    assert isinstance(d, rlg.Refused)
    assert d.code == "SWEEP_MISSING"
    assert "cw:aa:11:2" in d.detail
    assert "cw:aa:11:1" not in d.detail  # answered ids are not re-demanded


def test_sweep_at_old_head_refuses_stale():
    rows = [_row(1, "finding", "cw:aa:11:1")]
    d = _decide(_state(sweeps=(_sw(1, ("cw:aa:11:1",), head="e" * 40),)), rows)
    assert isinstance(d, rlg.Refused)
    assert d.code == "SWEEP_STALE"


def test_sweep_for_wrong_round_does_not_cover():
    rows = [_row(2, "finding", "cw:bb:22:9")]
    d = _decide(_state(sweeps=(_sw(1, ("cw:bb:22:9",)),)), rows)
    assert isinstance(d, rlg.Refused)
    assert d.code == "SWEEP_MISSING"


def test_approve_last_round_allows_without_sweep():
    rows = [_row(1, "no_finding")]
    d = _decide(_state(), rows)
    assert d == rlg.Allowed(round_n=2)


def test_unavailable_last_round_allows_retry():
    rows = [_row(1, "reviewer_unavailable")]
    d = _decide(_state(), rows)
    assert d == rlg.Allowed(round_n=2)


def test_failover_gemini_findings_same_round_must_be_swept():
    # a failover round's findings land under the GEMINI producer at the forced
    # shared round number — they are loop findings and must be answered
    rows = [
        _row(1, "reviewer_unavailable"),
        _row(1, "finding", "gw:aa:11:1", producer="gemini_review_wrapper"),
    ]
    d = _decide(_state(), rows)
    assert isinstance(d, rlg.Refused)
    assert d.code == "SWEEP_MISSING"
    assert "gw:aa:11:1" in d.detail


# ── pure core: termination predicate ─────────────────────────────────────────


def test_budget_exhausted_refuses_with_loop_reachable_recipe():
    rows = [_row(n, "finding", f"cw:aa:11:{n}") for n in range(1, 11)]
    sweeps = tuple(_sw(n, (f"cw:aa:11:{n}",)) for n in range(1, 11))
    d = _decide(_state(sweeps=sweeps), rows)
    assert isinstance(d, rlg.Refused)
    assert d.code == "BUDGET_EXHAUSTED"
    # the unblock verb attest-budget is ask-gated in loop mode: the recipe must
    # point at the register-and-hold path, never ping-pong against a denied verb
    assert "defer" in d.recipe or "register" in d.recipe
    assert "attest-budget" not in d.recipe.split("operator")[0]


def test_budget_extension_extends():
    rows = [_row(n, "no_finding") for n in range(1, 11)]
    ext = rlg.BudgetExtension(arc_id=ARC, extra_rounds=2, reason="operator ok", ts="t")
    d = _decide(_state(extensions=(ext,)), rows)
    assert d == rlg.Allowed(round_n=11)


def test_foreign_rows_do_not_count():
    # other arcs, lens producers (their per-producer round numbers collide), and
    # round_n=None detection rows (codex_context_guard) are all out of scope
    rows = [
        _row(9, "finding", "x:1", arc_id="other-arc"),
        _row(9, "finding", "x:2", producer="merge-gate-concurrency"),
        _row(None, "finding", "x:3", producer="codex_context_guard"),
    ]
    d = _decide(_state(preflights=(_pf(),)), rows)
    assert d == rlg.Allowed(round_n=1)


def test_state_loss_only_tightens():
    # the tightening-direction invariant: attestations/extensions live in state,
    # round counts live in the gate log — losing state can refuse what was
    # allowed, never allow what was refused
    rows = [_row(1, "finding", "cw:aa:11:1")]
    with_state = _decide(_state(sweeps=(_sw(1, ("cw:aa:11:1",)),)), rows)
    without_state = _decide(_state(), rows)
    assert isinstance(with_state, rlg.Allowed)
    assert isinstance(without_state, rlg.Refused)


# ── edges: state parse + admit ───────────────────────────────────────────────


@pytest.fixture()
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    (tmp_path / "f.txt").write_text("one\n")
    subprocess.run(
        ["git", "-C", str(tmp_path), "-c", "user.email=t@t", "-c", "user.name=t", "add", "."],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "commit",
            "-qm",
            "c1",
        ],
        check=True,
    )
    (tmp_path / ".harness").mkdir()
    monkeypatch.setenv("HARNESS_GATE_LOG", str(tmp_path / "gate-log.jsonl"))
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path / "gate-log.jsonl")
    monkeypatch.delenv("HARNESS_LOOP", raising=False)
    return tmp_path


def test_load_state_missing_file_is_empty(repo: Path):
    assert rlg.load_state(repo) == _state()


def test_admit_state_unreadable_refuses(repo: Path):
    rlg.state_path(repo).write_text("{not json")
    d = rlg.admit(repo, "main", ARC)
    assert isinstance(d, rlg.Refused)
    assert d.code == "STATE_UNREADABLE"


def test_admit_unreserved_loop_mode_refuses(repo: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("HARNESS_LOOP", "1")
    d = rlg.admit(repo, "main", ARC)
    assert isinstance(d, rlg.Refused)
    assert d.code == "ARC_UNRESERVED"


def test_admit_unreserved_interactive_is_inactive(repo: Path):
    d = rlg.admit(repo, "main", ARC)
    assert isinstance(d, rlg.Inactive)
    assert "unreserved" in d.reason


def test_admit_loop_marker_file_refuses_unreserved(repo: Path):
    (repo / ".harness" / ".loop-active").write_text("1")
    d = rlg.admit(repo, "main", ARC)
    assert isinstance(d, rlg.Refused)
    assert d.code == "ARC_UNRESERVED"


# ── edges: attest CLI ────────────────────────────────────────────────────────

SCRIPT_REL = Path(".claude/skills/defect-class-preflight/scripts/preflight-grep.sh")


def _plant_script(repo: Path, body: str) -> None:
    p = repo / SCRIPT_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)


def _attest_preflight(repo: Path, answers: str | None = "answers: all clean\n") -> int:
    a = repo / "answers.md"
    if answers is not None:
        a.write_text(answers)
    return rlg.main(
        ["attest-preflight", "--answers", str(a), "--base", "main", "--repo", str(repo)]
    )


def test_attest_preflight_script_cannot_run_refuses(repo: Path):
    _plant_script(repo, "#!/bin/sh\necho 'SWEEP DID NOT RUN' >&2\nexit 2\n")
    rc = _attest_preflight(repo)
    assert rc != 0
    assert rlg.load_state(repo).preflights == ()


def test_attest_preflight_unanswered_label_refuses(repo: Path):
    _plant_script(repo, "#!/bin/sh\nprintf '\\n[check-then-act on paths]\\n3:+x\\n'\nexit 0\n")
    rc = _attest_preflight(repo, answers="something unrelated\n")
    assert rc != 0
    assert rlg.load_state(repo).preflights == ()


def test_attest_preflight_records_bound_attestation(repo: Path, monkeypatch: pytest.MonkeyPatch):
    _plant_script(repo, "#!/bin/sh\nprintf '\\n[check-then-act on paths]\\n3:+x\\n'\nexit 0\n")
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    rc = _attest_preflight(repo, answers="check-then-act on paths: guarded by exclusive create\n")
    assert rc == 0
    (pf,) = rlg.load_state(repo).preflights
    binding = rw.code_binding(repo, "main")
    assert pf.head_sha == binding["head_sha"]
    assert pf.diff_digest == binding["diff_digest"]
    assert pf.arc_id == ARC
    assert pf.hit_labels == ("check-then-act on paths",)


def _commit_all(repo: Path, msg: str) -> None:
    for verb in (["add", "."], ["commit", "-qm", msg]):
        subprocess.run(
            ["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", *verb],
            check=True,
        )


def test_attest_preflight_real_script_integration(repo: Path, monkeypatch: pytest.MonkeyPatch):
    # the REAL preflight-grep.sh in RANGE mode against a committed silent-failure
    # shape on an arc branch: proves label parsing matches the script's actual
    # output AND that the attested range (base..head) is what gets swept — the
    # working tree is clean here, exactly the post-commit state attest requires
    real = Path(__file__).resolve().parents[1] / SCRIPT_REL
    _plant_script(repo, real.read_text())
    _commit_all(repo, "c2")  # script itself on main, outside the arc range
    subprocess.run(["git", "-C", str(repo), "checkout", "-qb", "arc"], check=True)
    (repo / "new.sh").write_text("run 2>/dev/null\n")
    _commit_all(repo, "arc work")
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    rc = _attest_preflight(repo, answers="silent-failure shapes: named answer here\n")
    assert rc == 0
    (pf,) = rlg.load_state(repo).preflights
    assert "silent-failure shapes" in pf.hit_labels


def test_attest_sweep_records_and_covers(repo: Path, monkeypatch: pytest.MonkeyPatch):
    _plant_script(repo, "#!/bin/sh\nexit 0\n")
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    fr.GATE_LOG_JSONL.write_text(
        json.dumps(_row(1, "finding", "cw:aa:11:1"))
        + "\n"
        + json.dumps(_row(1, "finding", "cw:aa:11:2"))
        + "\n"
    )
    a = repo / "sweep.md"
    a.write_text("cw:aa:11:1 fixed by X; cw:aa:11:2 registered\n")
    rc = rlg.main(["attest-sweep", "--answers", str(a), "--base", "main", "--repo", str(repo)])
    assert rc == 0
    (sw,) = rlg.load_state(repo).sweeps
    assert sw.round_n == 1
    assert set(sw.finding_ids) == {"cw:aa:11:1", "cw:aa:11:2"}


def test_attest_sweep_missing_id_refuses(repo: Path, monkeypatch: pytest.MonkeyPatch):
    _plant_script(repo, "#!/bin/sh\nexit 0\n")
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    fr.GATE_LOG_JSONL.write_text(json.dumps(_row(1, "finding", "cw:aa:11:1")) + "\n")
    a = repo / "sweep.md"
    a.write_text("nothing relevant\n")
    rc = rlg.main(["attest-sweep", "--answers", str(a), "--base", "main", "--repo", str(repo)])
    assert rc != 0
    assert rlg.load_state(repo).sweeps == ()


def test_attest_budget_requires_reason_and_records(repo: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    rc = rlg.main(["attest-budget", "--extra", "2", "--reason", "", "--repo", str(repo)])
    assert rc != 0
    rc = rlg.main(
        ["attest-budget", "--extra", "2", "--reason", "operator approved", "--repo", str(repo)]
    )
    assert rc == 0
    (ext,) = rlg.load_state(repo).extensions
    assert ext.extra_rounds == 2


def test_attest_on_corrupt_state_reinits_loudly(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys
):
    # safe direction only: state loss tightens, so a corrupt file may be re-inited
    _plant_script(repo, "#!/bin/sh\nexit 0\n")
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    rlg.state_path(repo).write_text("{corrupt")
    rc = _attest_preflight(repo)
    assert rc == 0
    assert "re-init" in capsys.readouterr().err
    assert len(rlg.load_state(repo).preflights) == 1


# ── wiring: codex_review.main() gates before any reviewer ────────────────────


@pytest.fixture()
def wired(repo: Path, monkeypatch: pytest.MonkeyPatch):
    import codex_review as cr

    monkeypatch.chdir(repo)
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    monkeypatch.setenv("HARNESS_LANE_ID", "lane-t")
    monkeypatch.setattr(
        cr, "run_bounded", lambda *a, **k: pytest.fail("reviewer ran despite gate refusal")
    )
    # a reservation exists for the arc → the gate is ACTIVE
    monkeypatch.setattr(rlg, "_reservation_exists", lambda arc_id: True)
    return cr


def test_wrapper_refuses_before_any_reviewer(wired, capsys):
    rc = wired.main(["--base", "main"])
    assert rc == 3
    err = capsys.readouterr().err
    assert "codex-review: GATE_REFUSED (PREFLIGHT_MISSING)" in err
    # NOT a review terminal: no C-HE-24 row, no round consumed
    assert fr.read_rows() == []


def test_wrapper_gate_fires_even_with_round_env(wired, monkeypatch: pytest.MonkeyPatch):
    # the advisor-killed bypass: HARNESS_ROUND_N forces row numbering for the
    # failover CHILD (gemini), which never re-enters codex_review.main —
    # nothing legitimate needs a gate skip here
    monkeypatch.setenv("HARNESS_ROUND_N", "7")
    assert wired.main(["--base", "main"]) == 3


def test_wrapper_inactive_arc_warns_and_proceeds(wired, monkeypatch: pytest.MonkeyPatch, capsys):
    monkeypatch.setattr(rlg, "_reservation_exists", lambda arc_id: False)
    monkeypatch.setattr(
        wired, "run_codex_review", lambda repo, base, invoke=None: pytest.fail("stop at review")
    )
    with pytest.raises(pytest.fail.Exception):
        wired.main(["--base", "main"])
    assert "review gate INACTIVE" in capsys.readouterr().err
