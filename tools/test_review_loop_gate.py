"""B-215 review-loop admission gate battery.

Covers the pure decision core (no mocks — [LAW:effects-at-boundaries]), the
attest CLI edges in throwaway git repos, and the codex_review.main() wiring
(gate fires BEFORE any reviewer subprocess; refusal is exit 3 and is NOT a
review terminal per C-HE-16 §3 — no C-HE-24 row, no round outcome).
"""

from __future__ import annotations

import json
import os
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


def _sw(ids: tuple[str, ...], head=HEAD, digest=DIGEST, arc=ARC) -> rlg.SweepAttestation:
    return rlg.SweepAttestation(
        arc_id=arc,
        head_sha=head,
        diff_digest=digest,
        finding_ids=ids,
        answers_digest="d",
        ts="t",
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
    d = _decide(_state(sweeps=(_sw(("cw:aa:11:1",)),)), rows)
    assert d == rlg.Allowed(round_n=2)


def test_sweep_missing_one_finding_names_it():
    rows = [_row(1, "finding", "cw:aa:11:1"), _row(1, "finding", "cw:aa:11:2")]
    d = _decide(_state(sweeps=(_sw(("cw:aa:11:1",)),)), rows)
    assert isinstance(d, rlg.Refused)
    assert d.code == "SWEEP_MISSING"
    assert "cw:aa:11:2" in d.detail
    assert "cw:aa:11:1" not in d.detail  # answered ids are not re-demanded


def test_covering_sweep_at_old_head_fails_currency():
    # obligations answered, but the CURRENT bytes carry no attestation
    rows = [_row(1, "finding", "cw:aa:11:1")]
    d = _decide(_state(sweeps=(_sw(("cw:aa:11:1",), head="e" * 40),)), rows)
    assert isinstance(d, rlg.Refused)
    assert d.code == "PREFLIGHT_STALE"


def test_covering_sweep_different_base_fails_currency():
    # codex r1 P2: head alone under-binds — a different --base is a different diff
    rows = [_row(1, "finding", "cw:aa:11:1")]
    d = _decide(_state(sweeps=(_sw(("cw:aa:11:1",), digest="f" * 64),)), rows)
    assert isinstance(d, rlg.Refused)
    assert d.code == "PREFLIGHT_STALE"


def test_standalone_gemini_interleave_still_blocks():
    # codex r2 P1: round numbers are per-producer scales — a gemini finding minted
    # at gemini-round-1 while codex sits at round 5 is still an unanswered
    # obligation; round arithmetic must not hide it
    rows = [
        *[_row(n, "no_finding") for n in range(1, 6)],
        _row(1, "finding", "gw:aa:11:9", producer="gemini_review_wrapper"),
    ]
    d = _decide(_state(preflights=(_pf(),)), rows)
    assert isinstance(d, rlg.Refused)
    assert d.code == "SWEEP_MISSING"
    assert "gw:aa:11:9" in d.detail


def test_approve_round_plus_current_attestation_allows():
    rows = [_row(1, "no_finding")]
    d = _decide(_state(preflights=(_pf(),)), rows)
    assert d == rlg.Allowed(round_n=2)


def test_unavailable_round_does_not_satisfy_currency():
    # codex r2 P1: an UNAVAILABLE round reviewed nothing — with no attestation for
    # the current bytes the next invocation must not bypass the entry preflight
    rows = [_row(1, "reviewer_unavailable")]
    assert isinstance(_decide(_state(), rows), rlg.Refused)
    d = _decide(_state(preflights=(_pf(),)), rows)
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


def test_budget_counts_distinct_producer_round_pairs():
    # codex r2 P1: rounds spent = review invocations across BOTH producer scales —
    # 6 codex + 4 standalone gemini = 10 spent, even though max(round_n) is only 6
    rows = [
        *[_row(n, "no_finding") for n in range(1, 7)],
        *[_row(n, "no_finding", producer="gemini_review_wrapper") for n in range(1, 5)],
    ]
    d = _decide(_state(preflights=(_pf(),)), rows)
    assert isinstance(d, rlg.Refused)
    assert d.code == "BUDGET_EXHAUSTED"
    # the unblock verb attest-budget is ask-gated in loop mode: the recipe must
    # point at the register-and-hold path, never ping-pong against a denied verb
    assert "defer" in d.recipe or "register" in d.recipe
    assert "attest-budget" not in d.recipe.split("operator")[0]


def test_budget_extension_extends():
    rows = [_row(n, "no_finding") for n in range(1, 11)]
    ext = rlg.BudgetExtension(arc_id=ARC, extra_rounds=2, reason="operator ok", ts="t")
    d = _decide(_state(preflights=(_pf(),), extensions=(ext,)), rows)
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


def test_foreign_arc_attestations_never_satisfy(monkeypatch: pytest.MonkeyPatch):
    # merge-gate witness lens P2: the three arc_id-scoping guards each need a
    # discriminating witness — one arc's preflight, sweep, or budget extension
    # must never satisfy/extend a DIFFERENT arc against the shared state file
    foreign = "b-999-other"
    # (1) currency: a foreign-arc preflight bound to the same head/digest does not admit
    d = _decide(_state(preflights=(_pf(arc=foreign),)), [])
    assert isinstance(d, rlg.Refused)
    assert d.code == "PREFLIGHT_MISSING"
    # (2) obligations: a foreign-arc sweep naming the id does not answer it
    rows = [_row(1, "finding", "cw:aa:11:1")]
    d = _decide(_state(sweeps=(_sw(("cw:aa:11:1",), arc=foreign),)), rows)
    assert isinstance(d, rlg.Refused)
    assert d.code == "SWEEP_MISSING"
    # (3) termination: a foreign-arc extension does not raise this arc's budget
    rows = [_row(n, "no_finding") for n in range(1, 11)]
    ext = rlg.BudgetExtension(arc_id=foreign, extra_rounds=5, reason="other arc", ts="t")
    d = _decide(_state(preflights=(_pf(),), extensions=(ext,)), rows)
    assert isinstance(d, rlg.Refused)
    assert d.code == "BUDGET_EXHAUSTED"


def test_state_loss_only_tightens():
    # the tightening-direction invariant: attestations/extensions live in state,
    # round counts live in the gate log — losing state can refuse what was
    # allowed, never allow what was refused
    rows = [_row(1, "finding", "cw:aa:11:1")]
    with_state = _decide(_state(sweeps=(_sw(("cw:aa:11:1",)),)), rows)
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


def test_admit_state_unreadable_refuses(repo: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(rlg, "_reservation_exists", lambda arc_id: True)
    rlg.state_path(repo).write_text("{not json")
    d = rlg.admit(repo, "main", ARC)
    assert isinstance(d, rlg.Refused)
    assert d.code == "STATE_UNREADABLE"


def test_admit_out_of_scope_arc_ignores_unreadable_state(repo: Path):
    # Inactive means NOT IN FORCE: an unreadable state file must not refuse an
    # unreserved interactive invocation (live schema migrations would otherwise
    # brick every wrapper call in the checkout)
    rlg.state_path(repo).write_text("{not json")
    d = rlg.admit(repo, "main", ARC)
    assert isinstance(d, rlg.Inactive)


def test_admit_unreserved_is_inactive_in_every_mode(repo: Path, monkeypatch: pytest.MonkeyPatch):
    # codex r3 P1: the headless-degradation path (reserve REFUSED by the permission
    # layer) is sanctioned and proceeds unreserved — a loop-mode hard refusal would
    # strand it with an unsatisfiable recipe. Fallback-id visibility on every row is
    # the accepted trade (named residual).
    d = rlg.admit(repo, "main", ARC)
    assert isinstance(d, rlg.Inactive)
    assert "unreserved" in d.reason
    monkeypatch.setenv("HARNESS_LOOP", "1")
    assert isinstance(rlg.admit(repo, "main", ARC), rlg.Inactive)
    (repo / ".harness" / ".loop-active").write_text("1")
    assert isinstance(rlg.admit(repo, "main", ARC), rlg.Inactive)


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


def test_preflight_grep_u_sr_01_shapes_each_catch_a_planted_fixture(repo: Path):
    """U-SR-01 (charter WR-03) acceptance: each of the four added shapes catches a
    planted fixture, run through the REAL script — a pattern that matches nothing is
    a class the sweep silently stops covering. The TimeoutExpired case asserts BOTH
    directions: the bare arm is reported and the `(TimeoutExpired, OSError)` sibling
    is NOT, so the exclusion is witnessed as discriminating rather than merely
    present (a label-only assertion passes even if report_unless never filters)."""
    real = Path(__file__).resolve().parents[1] / SCRIPT_REL
    _plant_script(repo, real.read_text(encoding="utf-8"))
    (repo / "planted.py").write_text(
        "if proc.returncode in (0, 1):\n"
        "    verdict = 'approve'\n"
        "try:\n"
        "    run()\n"
        "except subprocess.TimeoutExpired:\n"
        "    give_up()\n"
        "try:\n"
        "    run_sibling()\n"
        "except (subprocess.TimeoutExpired, OSError):\n"
        "    handle()\n"
        'parser.add_argument("--reps", type=int, default=3)\n'
    )
    (repo / "planted_guard.sh").write_text(
        "    elif printf '%s' \"$TRIM\" | grep -Eq '^just[[:space:]]+new-recipe$' \\\n"
    )
    out = subprocess.run(
        ["bash", str(repo / SCRIPT_REL)],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert out.returncode == 0, out.stderr
    for label in (
        "exit code read as verdict",
        "TimeoutExpired without OSError",
        "argparse count without a contract-derived bound",
        "new permission-guard allow branch",
    ):
        assert label in out.stdout, f"shape did not fire: {label}\n{out.stdout}"
    # the discriminating half: only the un-paired arm is carried into the report
    timeout_block = out.stdout.split("[TimeoutExpired without OSError")[1].split("\n\n")[0]
    assert "except subprocess.TimeoutExpired:" in timeout_block
    assert "OSError" not in timeout_block


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
    assert set(sw.finding_ids) == {"cw:aa:11:1", "cw:aa:11:2"}
    binding = rw.code_binding(repo, "main")
    assert sw.head_sha == binding["head_sha"]
    assert sw.diff_digest == binding["diff_digest"]


def test_attest_sweep_id_matching_is_token_exact(repo: Path, monkeypatch: pytest.MonkeyPatch):
    # codex r2 P2: an answer naming ...:10 must not satisfy the sibling ...:1
    _plant_script(repo, "#!/bin/sh\nexit 0\n")
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    fr.GATE_LOG_JSONL.write_text(
        json.dumps(_row(1, "finding", "cw:aa:11:1"))
        + "\n"
        + json.dumps(_row(1, "finding", "cw:aa:11:10"))
        + "\n"
    )
    a = repo / "sweep.md"
    a.write_text("cw:aa:11:10 fixed\n")
    rc = rlg.main(["attest-sweep", "--answers", str(a), "--base", "main", "--repo", str(repo)])
    assert rc != 0
    assert rlg.load_state(repo).sweeps == ()


def test_attest_tmp_symlink_cannot_redirect_write(repo: Path, monkeypatch: pytest.MonkeyPatch):
    # codex r2 P1: a pre-planted symlink at the fixed .tmp name must not receive the
    # write — unlink removes the LINK itself, exclusive-create refuses any survivor
    _plant_script(repo, "#!/bin/sh\nexit 0\n")
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    victim = repo / "victim.json"
    victim.write_text("precious\n")
    sp = rlg.state_path(repo)
    sp.parent.mkdir(parents=True, exist_ok=True)
    # plant at the ACTUAL per-pid temp name production opens (codex r6 P3: the old
    # fixed-name plant went stale when r5 made temp names per-pid, leaving the
    # witness green even with O_EXCL/O_NOFOLLOW removed)
    tmp_name = f"{sp.name}.{os.getpid()}.tmp"
    sp.with_name(tmp_name).symlink_to(victim)
    rc = _attest_preflight(repo)
    assert rc != 0  # O_EXCL refuses the planted entry loudly
    assert victim.read_text() == "precious\n"  # never written through
    assert rlg.load_state(repo).preflights == ()
    sp.with_name(tmp_name).unlink()  # planted link removed by hand -> attest succeeds
    rc = _attest_preflight(repo)
    assert rc == 0
    assert victim.read_text() == "precious\n"
    assert len(rlg.load_state(repo).preflights) == 1


def test_attest_sweep_missing_id_refuses(repo: Path, monkeypatch: pytest.MonkeyPatch):
    _plant_script(repo, "#!/bin/sh\nexit 0\n")
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    fr.GATE_LOG_JSONL.write_text(json.dumps(_row(1, "finding", "cw:aa:11:1")) + "\n")
    a = repo / "sweep.md"
    a.write_text("nothing relevant\n")
    rc = rlg.main(["attest-sweep", "--answers", str(a), "--base", "main", "--repo", str(repo)])
    assert rc != 0
    assert rlg.load_state(repo).sweeps == ()


def test_attest_sweep_on_corrupt_state_treats_it_as_empty(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys
):
    # a corrupt (e.g. old-schema) state must not brick the repair verb: obligations
    # compute against EMPTY state (maximal — tightening) and the write re-inits loudly
    _plant_script(repo, "#!/bin/sh\nexit 0\n")
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    rlg.state_path(repo).parent.mkdir(parents=True, exist_ok=True)
    rlg.state_path(repo).write_text('{"records": [{"kind": "sweep", "bogus_field": 1}]}')
    fr.GATE_LOG_JSONL.write_text(json.dumps(_row(1, "finding", "cw:aa:11:1")) + "\n")
    a = repo / "sweep.md"
    a.write_text("cw:aa:11:1 fixed\n")
    rc = rlg.main(["attest-sweep", "--answers", str(a), "--base", "main", "--repo", str(repo)])
    assert rc == 0
    assert "EMPTY state" in capsys.readouterr().err
    (sw,) = rlg.load_state(repo).sweeps
    assert sw.finding_ids == ("cw:aa:11:1",)


def test_attest_budget_requires_reason_and_records(repo: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    rc = rlg.main(["attest-budget", "--extra", "2", "--reason", "", "--repo", str(repo)])
    assert rc != 0
    # codex r5 P2: a non-positive "extension" would invert the tightening invariant
    rc = rlg.main(["attest-budget", "--extra", "0", "--reason", "ok", "--repo", str(repo)])
    assert rc != 0
    rc = rlg.main(["attest-budget", "--extra", "-3", "--reason", "ok", "--repo", str(repo)])
    assert rc != 0
    assert rlg.load_state(repo).extensions == ()
    for bad in (-2, True):  # bool subclasses int (codex r6 P2): true must refuse too
        rlg.state_path(repo).write_text(
            json.dumps(
                {
                    "records": [
                        {
                            "kind": "budget_extension",
                            "arc_id": ARC,
                            "extra_rounds": bad,
                            "reason": "r",
                            "ts": "t",
                        }
                    ]
                }
            )
        )
        with pytest.raises(rlg.GateError, match="extra_rounds"):
            rlg.load_state(repo)
    rlg.state_path(repo).unlink()
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


def test_symlinked_state_file_is_containment_refusal(repo: Path, monkeypatch: pytest.MonkeyPatch):
    # codex r1 P1: a pre-planted symlink must refuse loudly — never followed on read,
    # never "re-initialized" through on attest (the re-init license covers corrupt
    # CONTENT only)
    target = repo / "victim.json"
    target.write_text("precious\n")
    rlg.state_path(repo).symlink_to(target)
    with pytest.raises(rlg.GateError, match="containment"):
        rlg.load_state(repo)
    monkeypatch.setattr(rlg, "_reservation_exists", lambda arc_id: True)
    d = rlg.admit(repo, "main", ARC)
    assert isinstance(d, rlg.Refused)
    assert d.code == "STATE_UNREADABLE"
    _plant_script(repo, "#!/bin/sh\nexit 0\n")
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    rc = _attest_preflight(repo)
    assert rc != 0
    assert target.read_text() == "precious\n"  # never written through


def test_admit_reservation_store_unreadable_refuses(repo: Path, monkeypatch: pytest.MonkeyPatch):
    # codex r4 P1: "cannot tell" must REFUSE, never disable the gate — a corrupt
    # store would otherwise turn an actually-reserved arc's gate off
    def boom(arc_id):
        raise OSError("corrupt generation")

    monkeypatch.setattr(rlg, "_reservation_exists", boom)
    d = rlg.admit(repo, "main", ARC)
    assert isinstance(d, rlg.Refused)
    assert d.code == "STATE_UNREADABLE"
    assert "reservation store" in d.detail


def test_state_field_types_validated_at_parse(repo: Path):
    # codex r4 P2: dataclasses do not enforce annotations — extra_rounds="2" must
    # resolve to STATE_UNREADABLE at the boundary, not TypeError inside decide()
    rlg.state_path(repo).parent.mkdir(parents=True, exist_ok=True)
    rlg.state_path(repo).write_text(
        json.dumps(
            {
                "records": [
                    {
                        "kind": "budget_extension",
                        "arc_id": ARC,
                        "extra_rounds": "2",
                        "reason": "r",
                        "ts": "t",
                    }
                ]
            }
        )
    )
    with pytest.raises(rlg.GateError, match="extra_rounds"):
        rlg.load_state(repo)


def test_symlinked_answers_file_refused(repo: Path, monkeypatch: pytest.MonkeyPatch):
    # codex r4 P2: the attest verbs' one file input gets the same containment
    # discipline as the state file — an in-worktree symlink must not smuggle an
    # outside file through a guard-approved invocation
    _plant_script(repo, "#!/bin/sh\nexit 0\n")
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    outside = repo.parent / "outside-answers.md"
    outside.write_text("everything answered\n")
    a = repo / "answers.md"
    a.symlink_to(outside)
    rc = rlg.main(["attest-preflight", "--answers", str(a), "--base", "main", "--repo", str(repo)])
    assert rc != 0
    assert rlg.load_state(repo).preflights == ()


def test_finding_row_without_id_refuses_not_skips():
    # codex r8 P2: valid-JSON log corruption (a finding row with no finding_id) must
    # refuse — silently skipping it would erase an obligation
    rows = [_row(1, "finding", None)]
    d = _decide(_state(preflights=(_pf(),)), rows)
    assert isinstance(d, rlg.Refused)
    assert d.code == "STATE_UNREADABLE"


def test_nested_import_error_is_not_absent_substrate(repo: Path, monkeypatch: pytest.MonkeyPatch):
    # codex r8 P1: a broken import INSIDE reservations must refuse, not inactivate
    def broken(arc_id):
        raise ImportError("No module named 'arc_metrics'", name="arc_metrics")

    monkeypatch.setattr(rlg, "_reservation_exists", broken)
    d = rlg.admit(repo, "main", ARC)
    assert isinstance(d, rlg.Refused)
    assert d.code == "STATE_UNREADABLE"


def test_admit_gate_log_unreadable_refuses(repo: Path, monkeypatch: pytest.MonkeyPatch):
    # codex r7 P2: the gate log is the round/obligation authority — unreadable must
    # produce the typed refusal, never a traceback out of the wrapper
    monkeypatch.setattr(rlg, "_reservation_exists", lambda arc_id: True)
    fr.GATE_LOG_JSONL.write_text("{not jsonl\n")
    d = rlg.admit(repo, "main", ARC)
    assert isinstance(d, rlg.Refused)
    assert d.code == "STATE_UNREADABLE"
    assert "gate log" in d.detail


def test_admit_binding_unavailable_defers_to_wrapper(repo: Path, monkeypatch: pytest.MonkeyPatch):
    # codex r1 P2: an unresolvable base is wrapper infrastructure, not an admission
    # fact — defer to run_codex_review's classifier instead of crashing pre-terminal
    monkeypatch.setattr(rlg, "_reservation_exists", lambda arc_id: True)
    d = rlg.admit(repo, "no-such-base", ARC)
    assert isinstance(d, rlg.Inactive)
    assert "binding unavailable" in d.reason


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


# ── wiring: agy_review.main() gates standalone gemini (codex r1 P1) ──────────


@pytest.fixture()
def agy_wired(repo: Path, monkeypatch: pytest.MonkeyPatch):
    import agy_review as agy

    monkeypatch.chdir(repo)
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    monkeypatch.setenv("HARNESS_LANE_ID", "lane-t")
    monkeypatch.delenv("HARNESS_FAILOVER_CHILD", raising=False)
    monkeypatch.setattr(rlg, "_reservation_exists", lambda arc_id: True)
    monkeypatch.setattr(sys, "argv", ["agy_review.py", "--base", "main"])
    return agy


def test_agy_standalone_refuses_unattested(agy_wired, monkeypatch: pytest.MonkeyPatch, capsys):
    # an ungated standalone gemini review would mint loop rounds that poison the
    # guarded wrapper's round count (last > 0 skips the entry preflight)
    monkeypatch.setattr(
        agy_wired, "run_review", lambda repo, base: pytest.fail("reviewer ran despite refusal")
    )
    assert agy_wired.main() == 3
    assert "gemini-review: GATE_REFUSED (PREFLIGHT_MISSING)" in capsys.readouterr().err


def test_agy_failover_child_skips_gate(agy_wired, monkeypatch: pytest.MonkeyPatch):
    # the parent admitted the round; the child must not re-gate (nor double-refuse)
    monkeypatch.setenv("HARNESS_FAILOVER_CHILD", "1")
    monkeypatch.setattr(agy_wired, "run_review", lambda repo, base: 0)
    assert agy_wired.main() == 0


# ── launch verb: per-attempt names (U-HE-49; C-HE-21 §1 X6b) ─────────────────


def test_attempt_destination_first_attempt():
    assert (
        rlg.attempt_destination(".harness/tmp/x-rounds/r9.log", [])
        == ".harness/tmp/x-rounds/r9-a1.log"
    )


def test_attempt_destination_retry_increments():
    assert (
        rlg.attempt_destination(".harness/tmp/x-rounds/r9.log", ["r9-a1.log"])
        == ".harness/tmp/x-rounds/r9-a2.log"
    )


def test_attempt_destination_is_max_plus_one_not_count():
    # a deleted intermediate attempt must never resurrect a taken write-once name
    assert rlg.attempt_destination("d/r9.log", ["r9-a1.log", "r9-a3.log"]) == "d/r9-a4.log"


def test_attempt_destination_sibling_rounds_do_not_interfere():
    # the r1 prefix trap: r10/r11 attempts are not r1 attempts
    names = ["r1-a1.log", "r10-a2.log", "r11-a5.log", "r9-verdict-a1.log"]
    assert rlg.attempt_destination("d/r1.log", names) == "d/r1-a2.log"


def test_attempt_destination_bare_legacy_name_never_reused():
    # a pre-U-HE-49 bare `r9.log` on disk: attempts mint beside it, never claim it
    assert rlg.attempt_destination("d/r9.log", ["r9.log"]) == "d/r9-a1.log"


def test_attempt_destination_idempotent_on_own_output():
    # requesting a prior attempt's name mints the round's NEXT attempt, not a nested one
    assert rlg.attempt_destination("d/r9-a1.log", ["r9-a1.log"]) == "d/r9-a2.log"


def test_attempt_destination_extensionless_basename():
    assert rlg.attempt_destination("r9", []) == "r9-a1"


def test_attempt_names_key_to_their_round_for_arc_metrics():
    # seam contract with U-HE-46 round derivation: the r<N> prefix survives the
    # attempt suffix, so every attempt keys to its round and a refused attempt
    # plus its retry collapse to one round
    import arc_metrics as am

    stem = Path(rlg.attempt_destination("d/r9.log", ["r9-a1.log"])).stem
    m = am.ROUND_ID_RE.match(stem)
    assert m is not None and m.group(1) == "9"


# ── launch verb: admission before launch (U-HE-49; C-HE-21 §1 X6b) ───────────


def _seed_current_preflight(repo: Path) -> None:
    binding = rw.code_binding(repo, "main")
    rec = {
        "kind": "preflight",
        "arc_id": ARC,
        "head_sha": binding["head_sha"],
        "diff_digest": binding["diff_digest"],
        "hit_labels": [],
        "answers_digest": "d",
        "ts": "t",
    }
    rlg.state_path(repo).write_text(json.dumps({"records": [rec]}))


def _launch(repo: Path, log: str = ".harness/tmp/x-rounds/r1.log") -> int:
    return rlg.main(["launch", "--log", log, "--repo", str(repo)])


@pytest.fixture()
def launch_env(repo: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("HARNESS_ARC_ID", ARC)
    monkeypatch.delenv("HARNESS_ROUND_N", raising=False)
    monkeypatch.setattr(rlg, "_reservation_exists", lambda arc_id: True)
    return repo


def test_launch_refused_consumes_no_round_identity(launch_env: Path, capsys):
    # [B] F13 shape 1 (r11 launched into BUDGET_EXHAUSTED / r9 into SWEEP_MISSING):
    # the refusal now lands BEFORE the launch — exit 3, no destination minted,
    # no file, not even the rounds directory
    assert _launch(launch_env) == 3
    out, err = capsys.readouterr()
    assert out == ""  # nothing on the dataflow seam — no round identity consumed
    assert "review-launch: GATE_REFUSED (PREFLIGHT_MISSING)" in err
    assert not (launch_env / ".harness/tmp/x-rounds").exists()


def test_launch_refused_on_spent_budget_before_launch(launch_env: Path, capsys):
    # the literal F13 r11 shape: budget spent → the launch is not made
    _seed_current_preflight(launch_env)
    rows = [_row(n, "no_finding") for n in range(1, rlg.DEFAULT_ROUND_BUDGET + 1)]
    (launch_env / "gate-log.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    assert _launch(launch_env, ".harness/tmp/x-rounds/r11.log") == 3
    out, err = capsys.readouterr()
    assert out == ""
    assert "review-launch: GATE_REFUSED (BUDGET_EXHAUSTED)" in err
    assert not (launch_env / ".harness/tmp/x-rounds").exists()


def test_launch_allowed_prints_first_attempt_destination(launch_env: Path, capsys):
    _seed_current_preflight(launch_env)
    assert _launch(launch_env) == 0
    out, err = capsys.readouterr()
    assert out.strip() == ".harness/tmp/x-rounds/r1-a1.log"
    assert "review-launch: ALLOWED (next round 1)" in err


def test_launch_inactive_arc_proceeds_with_attempt_name(launch_env, monkeypatch, capsys):
    # unreserved degradation path (sanctioned): the gate is not in force, but the
    # per-attempt naming still applies — naming is identity discipline, not admission
    monkeypatch.setattr(rlg, "_reservation_exists", lambda arc_id: False)
    assert _launch(launch_env) == 0
    out, err = capsys.readouterr()
    assert out.strip() == ".harness/tmp/x-rounds/r1-a1.log"
    assert "review-launch: gate INACTIVE" in err


def test_launch_retry_after_refused_attempt_publishes_cleanly(launch_env: Path, capsys):
    # [B] F13 shape 2 (r9's relaunch reused `r9.log` → PUBLISH FAILED exit 4):
    # a wrapper-level refused attempt occupies the round's -a1 name (a refused
    # attempt minted no gate-log row, so the round identity has NOT advanced);
    # the retry re-requests the SAME round, mints -a2, and the REAL publisher
    # accepts it — no write-once collision
    _seed_current_preflight(launch_env)
    rounds = launch_env / ".harness/tmp/x-rounds"
    rounds.mkdir(parents=True)
    (rounds / "r1-a1.log").write_text("codex-review: GATE_REFUSED (SWEEP_MISSING)\n")
    assert _launch(launch_env, ".harness/tmp/x-rounds/r1.log") == 0
    dest = capsys.readouterr().out.strip()
    assert dest == ".harness/tmp/x-rounds/r1-a2.log"
    publisher = Path(__file__).resolve().parent / "round_log_publish.py"
    done = subprocess.run(
        [sys.executable, str(publisher), dest],
        cwd=launch_env,
        input=b"codex-review: BLOCK\n",
        capture_output=True,
    )
    assert done.returncode == 0, done.stderr
    assert (rounds / "r1-a2.log").read_text() == "codex-review: BLOCK\n"
    # the OLD shape stays refused: re-publishing an existing attempt name is still
    # the publisher's write-once refusal — per-attempt naming is what avoids it
    again = subprocess.run(
        [sys.executable, str(publisher), ".harness/tmp/x-rounds/r1-a1.log"],
        cwd=launch_env,
        input=b"x\n",
        capture_output=True,
    )
    assert again.returncode == 4


def test_launch_refuses_round_name_not_matching_recorded_rounds(launch_env: Path, capsys):
    # codex r1 P2: after a RECORDED round 1, re-requesting `r1.log` would mint
    # r1-a2 while the wrapper records round 2 — two review transcripts claiming
    # round 1, which arc_metrics refuses. The launch binds the requested name to
    # round_n_for (the same mint the wrapper records) BEFORE the reviewer call.
    _seed_current_preflight(launch_env)
    (launch_env / "gate-log.jsonl").write_text(json.dumps(_row(1, "no_finding")) + "\n")
    assert _launch(launch_env, ".harness/tmp/x-rounds/r1.log") == 3
    out, err = capsys.readouterr()
    assert out == ""
    assert "GATE_REFUSED (ROUND_NAME_MISMATCH)" in err
    assert "next primary round is 2" in err
    assert not (launch_env / ".harness/tmp/x-rounds").exists()
    # the round the mint names IS accepted
    assert _launch(launch_env, ".harness/tmp/x-rounds/r2.log") == 0
    assert capsys.readouterr().out.strip() == ".harness/tmp/x-rounds/r2-a1.log"


def test_crashed_publisher_temp_neither_blocks_attempt_reuse_nor_its_publish(
    launch_env: Path, capsys
):
    # codex r3/r4 rejection, promoted to a fail-closed witness: a hard-killed
    # publisher leaves only its private `.r<N>-a<K>.log.<pid>.<hex>.tmp` — the
    # FINAL name was never installed, so it is legitimately free. The next
    # launch mints that same attempt name (the anchored matcher ignores the
    # temp) and the REAL publisher installs it cleanly; the orphan temp's bytes
    # survive untouched. No evidence is lost and no collision exists.
    _seed_current_preflight(launch_env)
    rounds = launch_env / ".harness/tmp/x-rounds"
    rounds.mkdir(parents=True)
    temp = rounds / ".r1-a1.log.12345.deadbeef.tmp"
    temp.write_text("partial transcript, publisher killed\n")
    assert _launch(launch_env) == 0
    dest = capsys.readouterr().out.strip()
    assert dest == ".harness/tmp/x-rounds/r1-a1.log"
    publisher = Path(__file__).resolve().parent / "round_log_publish.py"
    done = subprocess.run(
        [sys.executable, str(publisher), dest],
        cwd=launch_env,
        input=b"codex-review: BLOCK\n",
        capture_output=True,
    )
    assert done.returncode == 0, done.stderr
    assert (rounds / "r1-a1.log").read_text() == "codex-review: BLOCK\n"
    assert temp.read_text() == "partial transcript, publisher killed\n"


def test_launch_refuses_destination_outside_harness_tmp(launch_env: Path, capsys):
    # codex r3 P2 (form mirror of the publisher's policy, checked BEFORE the paid
    # call): a destination the publisher would refuse must refuse at launch
    _seed_current_preflight(launch_env)
    assert _launch(launch_env, "tools/r1.log") == 3
    out, err = capsys.readouterr()
    assert out == ""
    assert "GATE_REFUSED (DEST_REFUSED)" in err


def test_launch_refuses_symlinked_rounds_dir(launch_env: Path, tmp_path_factory, capsys):
    # codex r3 P2: a pre-planted symlink under .harness/tmp must not route even
    # the read-only attempt listing outside the worktree — O_NOFOLLOW dir-fd walk
    _seed_current_preflight(launch_env)
    outside = tmp_path_factory.mktemp("outside")
    (outside / "r1-a1.log").write_text("planted\n")
    (launch_env / ".harness/tmp").mkdir(parents=True)
    (launch_env / ".harness/tmp/x-rounds").symlink_to(outside)
    assert _launch(launch_env) == 3
    out, err = capsys.readouterr()
    assert out == ""
    assert "GATE_REFUSED (DEST_REFUSED)" in err
    assert "containment" in err


def test_launch_refuses_stale_forced_round_env(launch_env: Path, monkeypatch, capsys):
    # codex r5: a leaked HARNESS_ROUND_N would force the WRAPPER (which honors
    # it) onto an already-recorded round — refuse pre-launch unless the forced
    # value IS the next unused primary round
    _seed_current_preflight(launch_env)
    (launch_env / "gate-log.jsonl").write_text(json.dumps(_row(1, "no_finding")) + "\n")
    monkeypatch.setenv("HARNESS_ROUND_N", "1")
    assert _launch(launch_env, ".harness/tmp/x-rounds/r2.log") == 3
    out, err = capsys.readouterr()
    assert out == ""
    assert "GATE_REFUSED (FORCED_ROUND_STALE)" in err
    # a forced value equal to the next unused round is the failover-child shape
    # and passes
    monkeypatch.setenv("HARNESS_ROUND_N", "2")
    assert _launch(launch_env, ".harness/tmp/x-rounds/r2.log") == 0
    assert capsys.readouterr().out.strip() == ".harness/tmp/x-rounds/r2-a1.log"


def test_launch_refuses_alias_round_names(launch_env: Path, capsys):
    # codex r5/r6: r01/round-1/r1-notes parse to the right NUMBER but would mint
    # a second attempt family for one round, and r1/r1.txt would publish outside
    # the documented r*.log glob — only the canonical r<N>.log basename launches
    _seed_current_preflight(launch_env)
    for alias in ("r01.log", "round-1.log", "r1-notes.log", "r1", "r1.txt"):
        assert _launch(launch_env, f".harness/tmp/x-rounds/{alias}") == 3
        out, err = capsys.readouterr()
        assert out == "", alias
        assert "GATE_REFUSED (ROUND_NAME_MISMATCH)" in err, alias
    assert not (launch_env / ".harness/tmp/x-rounds").exists()


def test_launch_refuses_unparseable_round_name(launch_env: Path, capsys):
    # a name arc_metrics cannot key to a round would poison the evidence set at
    # queue time — refuse it BEFORE the reviewer call, not after
    _seed_current_preflight(launch_env)
    assert _launch(launch_env, ".harness/tmp/x-rounds/final.log") == 3
    out, err = capsys.readouterr()
    assert out == ""
    assert "GATE_REFUSED (ROUND_NAME_UNPARSEABLE)" in err
    assert not (launch_env / ".harness/tmp/x-rounds").exists()


_RESERVATIONS = Path(__file__).resolve().parent / "reservations.py"


def _rsv(qdir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_RESERVATIONS), *args],
        env=dict(os.environ, ARC_METRICS_QUEUE_DIR=str(qdir)),
        capture_output=True,
        text=True,
    )


def _seed_reservation(qdir: Path, arc: str = "arc-x", lane: str = "lane-1") -> None:
    done = _rsv(
        qdir,
        "reserve",
        "--arc-id",
        arc,
        "--lane-id",
        lane,
        "--branch",
        "b",
        "--arc-type",
        "applying",
    )
    assert done.returncode == 0, done.stderr


def _phases(qdir: Path, arc: str = "arc-x") -> dict:
    done = _rsv(qdir, "show", "--arc-id", arc)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout).get("phases", {})


def _recipe_body(log: str, base: str = "main") -> str:
    justfile = (Path(__file__).resolve().parents[1] / "justfile").read_text()
    body = justfile.split("review-with-failover-logged log base='main':", 1)[1].split("\n\n", 1)[0]
    lines = [ln[4:] if ln.startswith("    ") else ln for ln in body.splitlines()]
    return "\n".join(lines).replace("{{log}}", log).replace("{{base}}", base) + "\n"


@pytest.fixture()
def recipe_env(tmp_path: Path):
    """Execute the REAL recipe body under a PATH-shimmed `uv` (merge-gate witness
    lens, PR #1471): the shim refuses/allows the launch verb per REC_MODE, marks
    any wrapper invocation, and execs the REAL publisher — so the bash
    control-flow binding (`|| exit`, the empty-dest arm, PIPESTATUS folding) is
    witnessed by execution, not by substring presence."""
    repo = tmp_path / "repo"
    (repo / ".harness").mkdir(parents=True)
    shim = tmp_path / "bin"
    shim.mkdir()
    real_publisher = Path(__file__).resolve().parent / "round_log_publish.py"
    (shim / "uv").write_text(
        "#!/usr/bin/env bash\n"
        "# args: run python tools/<script> ...\n"
        'script="$3"; shift 3\n'
        'case "$script" in\n'
        "  tools/review_loop_gate.py)\n"
        '    case "$REC_MODE" in\n'
        "      refuse) echo 'review-launch: GATE_REFUSED (TEST)' >&2; exit 3 ;;\n"
        "      empty) exit 0 ;;\n"
        # allow: echo a MINTED name distinguishable from the raw --log value, as the
        # real verb always does — witness-lens r2: an echo of the input cannot
        # discriminate `publish "$dest"` from `publish "{{log}}"`
        '      allow) shift; echo "${2%.log}-a1.log" ;;\n'
        "    esac ;;\n"
        "  tools/codex_review.py)\n"
        '    touch "$REC_MARKER"\n'
        # REC_WRAP_MODE selects the wrapper's terminal (codex u-he-50 r4): approve
        # exercises the final-round arm, refused the in-process GATE_REFUSED arm
        '    case "${REC_WRAP_MODE:-block}" in\n'
        '      approve) printf "codex-review: APPROVE\\n"; exit 0 ;;\n'
        '      refused) printf "review-launch: GATE_REFUSED (INNER)\\n"; exit 3 ;;\n'
        '      *) printf "codex-review: BLOCK\\n"; exit 1 ;;\n'
        "    esac ;;\n"
        "  tools/round_log_publish.py)\n"
        f'    exec "{sys.executable}" "{real_publisher}" "$@" ;;\n'
        # U-HE-50: span emission execs the REAL store writer against the fixture's
        # ARC_METRICS_QUEUE_DIR, so the verify pair below is witnessed on a real
        # reservation head, not a stub's echo; REC_PHASE_MODE=fail-start injects a
        # start-edge store failure (codex u-he-50 r1: the partial-write arm)
        "  tools/reservations.py)\n"
        '    if [ "${REC_PHASE_MODE:-}" = fail-start ]; then\n'
        '      case "$*" in *"--phase verify --edge start"*)\n'
        '        echo "ABORT: injected start failure" >&2; exit 2 ;; esac\n'
        "    fi\n"
        '    if [ "${REC_PHASE_MODE:-}" = fail-end ]; then\n'
        '      case "$*" in *"--phase verify --edge end"*)\n'
        '        echo "ABORT: injected end failure" >&2; exit 2 ;; esac\n'
        "    fi\n"
        f'    exec "{sys.executable}" "{_RESERVATIONS}" "$@" ;;\n'
        "esac\n"
    )
    (shim / "uv").chmod(0o755)

    def run(
        mode: str,
        log: str = ".harness/tmp/x-rounds/r1.log",
        arc_env: dict[str, str] | None = None,
        phase_mode: str = "",
        wrap_mode: str = "",
    ):
        script = tmp_path / "recipe.sh"
        script.write_text(_recipe_body(log))
        env = dict(
            os.environ,
            PATH=f"{shim}:{os.environ['PATH']}",
            REC_MODE=mode,
            REC_MARKER=str(tmp_path / "wrapper-ran"),
            ARC_METRICS_QUEUE_DIR=str(tmp_path / "queue"),
            REC_PHASE_MODE=phase_mode,
            REC_WRAP_MODE=wrap_mode,
        )
        # hermetic: a live session's exported arc ids must not leak emission into
        # tests that model the unreserved invocation
        for key in ("HARNESS_ARC_ID", "HARNESS_LANE_ID"):
            env.pop(key, None)
        env.update(arc_env or {})
        return subprocess.run(
            ["bash", str(script)], cwd=repo, env=env, capture_output=True, text=True
        )

    return repo, tmp_path, run


def test_recipe_execution_refused_launch_never_reaches_wrapper(recipe_env):
    repo, tmp, run = recipe_env
    done = run("refuse")
    assert done.returncode == 3
    assert not (tmp / "wrapper-ran").exists()  # the reviewer call was NOT made
    assert not (repo / ".harness/tmp").exists()  # and no log was written


def test_recipe_execution_empty_dest_aborts_before_wrapper(recipe_env):
    _repo, tmp, run = recipe_env
    done = run("empty")
    assert done.returncode == 4
    assert "printed no destination" in done.stderr
    assert not (tmp / "wrapper-ran").exists()


def test_recipe_execution_allowed_pipes_wrapper_through_real_publisher(recipe_env):
    repo, tmp, run = recipe_env
    done = run("allow")
    assert done.returncode == 1  # the stub wrapper's BLOCK exit survives PIPESTATUS folding
    assert (tmp / "wrapper-ran").exists()
    # the publish lands at the MINTED destination, never the caller's raw name —
    # execution-discriminates `publish "$dest"` from `publish "{{log}}"` (lens r2)
    assert (repo / ".harness/tmp/x-rounds/r1-a1.log").read_text() == "codex-review: BLOCK\n"
    assert not (repo / ".harness/tmp/x-rounds/r1.log").exists()


def test_logged_recipe_evaluates_admission_before_launch():
    # the launch step composition ([LAW:verifiable-goals] on the bash seam): the
    # launch verb runs BEFORE the wrapper, short-circuits on refusal, and the
    # publisher receives the minted per-attempt destination, never the caller's name.
    # Mutation-probe carrier: removing the pre-launch admission line reds this test.
    justfile = (Path(__file__).resolve().parents[1] / "justfile").read_text()
    recipe = justfile.split("review-with-failover-logged log base='main':", 1)[1].split("\n\n", 1)[
        0
    ]
    assert recipe.index("review_loop_gate.py launch") < recipe.index("codex_review.py")
    launch_line = next(ln for ln in recipe.splitlines() if "review_loop_gate.py launch" in ln)
    assert '|| exit "$?"' in launch_line  # a refused launch is not made
    assert 'round_log_publish.py "$dest"' in recipe
    assert 'round_log_publish.py "{{log}}"' not in recipe


# --- U-HE-50 (C-HE-27 §5 X6a): the wrapper's process boundaries are the verify edges ---

_ARC_ENV = {"HARNESS_ARC_ID": "arc-x", "HARNESS_LANE_ID": "lane-1"}


def test_recipe_reserved_arc_emits_verify_span_pair(recipe_env):
    # the acceptance witness: a fixture round through the REAL recipe body writes
    # the verify {start, end} pair on the reservation head with zero skill-prose
    # involvement — the wrapper is the emitter
    _repo, tmp, run = recipe_env
    _seed_reservation(tmp / "queue")
    done = run("allow", arc_env=dict(_ARC_ENV))
    assert done.returncode == 1  # the verdict exit is untouched by emission
    verify = _phases(tmp / "queue").get("verify", {})
    assert set(verify) == {"start", "end"}
    assert verify["start"] <= verify["end"]  # ISO-8601 UTC orders lexicographically
    assert "WARN" not in done.stderr


def test_recipe_round2_reemission_keeps_round1_window(recipe_env):
    # record_phase is first-write-wins + replay-idempotent, so the round-2 wrapper
    # re-emits as a no-op and the durable pair stays the round-1 window (the ship-pr
    # "verify = the round-1 window" semantics hold by construction, not by prose)
    _repo, tmp, run = recipe_env
    _seed_reservation(tmp / "queue")
    run("allow", arc_env=dict(_ARC_ENV))
    first = _phases(tmp / "queue")["verify"]
    done = run("allow", ".harness/tmp/x-rounds/r2.log", arc_env=dict(_ARC_ENV))
    assert done.returncode == 1
    assert _phases(tmp / "queue")["verify"] == first
    assert "WARN" not in done.stderr  # a no-op replay is not an emission failure


def test_recipe_refused_launch_opens_no_verify_span(recipe_env):
    # C-HE-21 §1 X6b composition: admission precedes emission — a refused launch
    # spends no reviewer call, claims no round name, and opens no span.
    # Mutation-probe carrier: moving `emit_verify start` above the launch line
    # reds this test.
    _repo, tmp, run = recipe_env
    _seed_reservation(tmp / "queue")
    done = run("refuse", arc_env=dict(_ARC_ENV))
    assert done.returncode == 3
    assert "verify" not in _phases(tmp / "queue")


def test_recipe_unreserved_invocation_skips_emission(recipe_env):
    # C-HE-27 §3 disposition: no arc ids in the environment → no store touch at
    # all; the absent span reads null downstream, never a measured zero
    _repo, tmp, run = recipe_env
    done = run("allow")
    assert done.returncode == 1
    assert not (tmp / "queue" / "reservations").exists()
    assert "WARN" not in done.stderr  # the skip is the spec'd disposition, not a failure


def test_recipe_emission_failure_warns_and_preserves_verdict(recipe_env):
    # ids present but no reservation head: record_phase ABORTs (exit 2) — the
    # wrapper warns loud on stderr and the round's verdict + publish are untouched
    # ([LAW:no-silent-failure]: the failure surfaces; it never rewrites the exit).
    # The failed start also mutes the end emission (codex u-he-50 r1: a lone end
    # would durably record a reversed pair).
    repo, _tmp, run = recipe_env
    done = run("allow", arc_env=dict(_ARC_ENV))
    assert done.returncode == 1
    assert "WARN verify.start span emission failed" in done.stderr
    assert "WARN verify.end skipped" in done.stderr
    assert (repo / ".harness/tmp/x-rounds/r1-a1.log").read_text() == "codex-review: BLOCK\n"


def test_recipe_start_failure_records_no_partial_pair(recipe_env):
    # codex u-he-50 r1 (partial-write arm 1): a start-edge store failure with a
    # healthy end path must record NOTHING — a lone end would be a reversed pair
    # once a retry stamps its later start (record_phase refuses no rewrite, so the
    # corrupt state would be durable). The retry then emits a fresh coherent pair.
    _repo, tmp, run = recipe_env
    _seed_reservation(tmp / "queue")
    done = run("allow", arc_env=dict(_ARC_ENV), phase_mode="fail-start")
    assert done.returncode == 1
    assert "WARN verify.start span emission failed" in done.stderr
    assert "WARN verify.end skipped" in done.stderr
    assert "verify" not in _phases(tmp / "queue")  # nothing recorded this attempt
    retry = run("allow", ".harness/tmp/x-rounds/r2.log", arc_env=dict(_ARC_ENV))
    assert retry.returncode == 1
    verify = _phases(tmp / "queue")["verify"]
    assert set(verify) == {"start", "end"}
    assert verify["start"] <= verify["end"]  # coherent, never reversed


def test_recipe_end_failure_leaves_open_window_next_round_closes(recipe_env):
    # codex u-he-50 r2 (partial-write arm 3), pinned as the SAME named bound as the
    # crash window: a failed end WRITE leaves the durable start intact and only the
    # next invocation can close it — the recorded span is an upper bound that can
    # overlap the edit window (no durable same-attempt signal exists that would not
    # mint a second authority; the recipe comment names the bound).
    _repo, tmp, run = recipe_env
    _seed_reservation(tmp / "queue")
    done = run("allow", arc_env=dict(_ARC_ENV), phase_mode="fail-end")
    assert done.returncode == 1
    assert "WARN verify.end span emission failed" in done.stderr
    open_window = _phases(tmp / "queue")["verify"]
    assert set(open_window) == {"start"}  # start intact, window open
    retry = run("allow", ".harness/tmp/x-rounds/r2.log", arc_env=dict(_ARC_ENV))
    assert retry.returncode == 1
    verify = _phases(tmp / "queue")["verify"]
    assert verify["start"] == open_window["start"]  # first-write-wins keeps round-1 start
    assert set(verify) == {"start", "end"}
    assert verify["start"] <= verify["end"]


def test_recipe_half_set_ids_warn_and_skip_emission(recipe_env):
    # codex u-he-50 r2 P3: one id without the other is a MISCONFIGURED invocation,
    # not the spec'd unreserved case — the skip must be loud, and no store write
    # happens (a half-identity can never bind to the holder fence anyway)
    _repo, tmp, run = recipe_env
    done = run("allow", arc_env={"HARNESS_ARC_ID": "arc-x"})
    assert done.returncode == 1
    assert "must both be set" in done.stderr
    assert not (tmp / "queue" / "reservations").exists()


def test_recipe_env_inherited_flag_cannot_skip_end(recipe_env):
    # codex u-he-50 r5 P3: the skip flag is process-local state, initialized by the
    # recipe — an environment-exported _verify_start_failed=1 must not mute the end
    # emission after a successful start.
    _repo, tmp, run = recipe_env
    _seed_reservation(tmp / "queue")
    done = run("allow", arc_env={"_verify_start_failed": "1", **_ARC_ENV})
    assert done.returncode == 1
    verify = _phases(tmp / "queue")["verify"]
    assert set(verify) == {"start", "end"}  # the inherited flag was reset, end emitted
    assert "WARN" not in done.stderr


def test_recipe_inner_gate_refusal_records_no_verify_end(recipe_env):
    # codex u-he-50 r4: the wrapper's own in-process admit is the enforcer of record
    # and can refuse AFTER the launch precheck admitted — GATE_REFUSED is not a round
    # (C-HE-16 §3), so a refused attempt must never land as a COMPLETE verify pair
    # (a lone start closes at the next real round, the named upper bound).
    _repo, tmp, run = recipe_env
    _seed_reservation(tmp / "queue")
    done = run("allow", arc_env=dict(_ARC_ENV), wrap_mode="refused")
    assert done.returncode == 3
    assert "GATE_REFUSED is not a round" in done.stderr
    assert set(_phases(tmp / "queue")["verify"]) == {"start"}  # no end recorded


def test_recipe_terminal_end_failure_repaired_by_documented_command(recipe_env):
    # codex u-he-50 r4: on a final APPROVE there is no next round to close a
    # failed-end window — the carriers document the session repair (re-run the
    # failed edge before ship; the head accretes until terminal). Witness the
    # repair lands: approve + fail-end → open pair; the documented CLI closes it.
    _repo, tmp, run = recipe_env
    _seed_reservation(tmp / "queue")
    done = run("allow", arc_env=dict(_ARC_ENV), phase_mode="fail-end", wrap_mode="approve")
    assert done.returncode == 0  # APPROVE verdict preserved
    assert "WARN verify.end span emission failed" in done.stderr
    assert set(_phases(tmp / "queue")["verify"]) == {"start"}
    repaired = _rsv(
        tmp / "queue",
        "phase",
        "--arc-id",
        "arc-x",
        "--phase",
        "verify",
        "--edge",
        "end",
        "--lane-id",
        "lane-1",
    )
    assert repaired.returncode == 0, repaired.stderr
    verify = _phases(tmp / "queue")["verify"]
    assert set(verify) == {"start", "end"}
    assert verify["start"] <= verify["end"]


def test_recipe_crash_window_closed_by_retry_end(recipe_env):
    # codex u-he-50 r1 (partial-write arm 2), pinned as a NAMED measurement bound:
    # an attempt that recorded start and died before end leaves an open window; the
    # retry keeps the round identity (U-HE-49) and its terminal closes the pair, so
    # the recorded round-1 span is an upper bound that includes the interruption —
    # first-write-wins keeps the original start (no rewrite).
    _repo, tmp, run = recipe_env
    _seed_reservation(tmp / "queue")
    seeded = _rsv(
        tmp / "queue",
        "phase",
        "--arc-id",
        "arc-x",
        "--phase",
        "verify",
        "--edge",
        "start",
        "--lane-id",
        "lane-1",
    )
    assert seeded.returncode == 0, seeded.stderr
    crashed_start = _phases(tmp / "queue")["verify"]["start"]
    done = run("allow", arc_env=dict(_ARC_ENV))
    assert done.returncode == 1
    verify = _phases(tmp / "queue")["verify"]
    assert verify["start"] == crashed_start  # the crashed attempt's start survives
    assert set(verify) == {"start", "end"}
    assert verify["start"] <= verify["end"]


def test_logged_recipe_emits_verify_at_process_boundaries():
    # U-HE-50 composition pin: start is emitted AFTER admission (a refused launch
    # opens no span) and BEFORE the reviewer call; end closes the window at the
    # pipeline terminal BEFORE the publish-failure exit arm can leave it dangling.
    # Mutation-probe carrier: removing either emission line reds this test.
    justfile = (Path(__file__).resolve().parents[1] / "justfile").read_text()
    recipe = justfile.split("review-with-failover-logged log base='main':", 1)[1].split("\n\n", 1)[
        0
    ]
    assert recipe.index("review_loop_gate.py launch") < recipe.index("emit_verify start")
    assert recipe.index("emit_verify start") < recipe.index("codex_review.py --base")
    assert recipe.index("codex_review.py --base") < recipe.index("emit_verify end")
    assert recipe.index("emit_verify end") < recipe.index("PUBLISH FAILED")
    assert '--phase verify --edge "$1" --lane-id "$HARNESS_LANE_ID"' in recipe
