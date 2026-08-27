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


def test_launch_refuses_unparseable_round_name(launch_env: Path, capsys):
    # a name arc_metrics cannot key to a round would poison the evidence set at
    # queue time — refuse it BEFORE the reviewer call, not after
    _seed_current_preflight(launch_env)
    assert _launch(launch_env, ".harness/tmp/x-rounds/final.log") == 3
    out, err = capsys.readouterr()
    assert out == ""
    assert "GATE_REFUSED (ROUND_NAME_UNPARSEABLE)" in err
    assert not (launch_env / ".harness/tmp/x-rounds").exists()


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
