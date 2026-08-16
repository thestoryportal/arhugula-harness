"""Ritual smoke — run the DOCUMENTED post-merge sequence end to end.

Why this file exists, separately from `test_roadmap_status_refresh.py`. That
suite tests the tool's FUNCTIONS. This one tests the RITUAL: the exact sequence
`ship-pr` tells a session to run, against a real scratch git repository, ending
in the assertion that actually matters — `codex_context_guard` accepts the
resulting commit as a verified terminating refresh.

It exists because three defects shipped into the PR #1338 arc and NONE of them
was reachable by a unit test or a static check; each surfaced only when the real
command was run at the moment the workflow needed it:

  1. a SOFT byte budget gating the HARD refusal path, so every refresh refused;
  2. a rotation split that let step 2 run without step 1 (and, in the round-12
     draft, made the refresh refuse a round that legitimately is not archived
     yet under `B-168` exit (iii));
  3. a shallow-clone guard that refused OUTRIGHT in a repo that is normally
     shallow, rather than only on the ambiguous not-found path.

Each test below is a regression witness for one of those. The cost is ~1s per
run, in the CI-only tools job, hidden behind the parallel axis-pytest job.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# `tools/` is not a package and pytest runs under `--import-mode=importlib`, which does
# NOT put this directory on `sys.path`. Without this insert the module imports only when
# some OTHER test file in the same invocation happens to have inserted it first — an
# order-dependent pass that vanishes the moment that sibling is renamed (B-184 close-out 3).
sys.path.insert(0, str(Path(__file__).resolve().parent))

import codex_context_guard as guard
import pytest
import roadmap_status_refresh as rsr

# A minimal but STRUCTURALLY REAL status file: the ritual touches the anchor
# table, the in-flight table, recently-completed, the next-action paragraph and
# the drift log, so all of them must be present and parseable.
STATUS_TEMPLATE = """# Roadmap status dashboard

---

## Workspace state anchor

| Field | Value |
|---|---|
| `workspace_state_hash` | `000000000000` |
| `last_refreshed` | 2026-01-01T00:00:00Z |
| `git_head` | `00000000` — seed |
| `latest_retirement_batch` | `.harness/phase-7d-retirement-events-batch-1.md` |
| `open_fork_doc_count` | 0 |

---

## Next action

**Purpose.** Live pointer.

**Current next action (post-#{round}).** Round {round} body.

---

## In-flight (open PRs)

| PR | Branch | R-NNN | Posture |
|---|---|---|---|
| *(none)* | — | — | No open PRs at refresh time. |

---

## Recently completed (last 5)

| R-NNN / PR | Closed at | Notes |
|---|---|---|
| PR #1 | 2026-01-01 | seed |

---

## Drift detection log

| Date | Source | Resolution |
|---|---|---|
{drift_rows}
"""

ARCHIVE_SEED = (
    "# Roadmap next-action round archive\n\n"
    "Header prose.\n\n"
    "---\n\n"
    "**Prior next action (post-#0).** The oldest round.\n"
)


def _status_text(round_label: str, drift_rows: int = 1, row_bytes: int = 20) -> str:
    rows = "\n".join(
        f"| 2026-01-{n:02d} | src{n} | {'r' * row_bytes} |" for n in range(1, drift_rows + 1)
    )
    return STATUS_TEMPLATE.format(round=round_label, drift_rows=rows)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _scratch_repo(tmp_path: Path, *, drift_rows: int = 1, row_bytes: int = 20) -> Path:
    """A real git repo whose history contains a SUPERSEDED round (post-#100)
    followed by the live one (post-#200) — the shape `--archive-superseded`
    reads, and the shape a real workspace is always in."""
    repo = tmp_path / "repo"
    (repo / ".harness").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
    _git(repo, "config", "user.email", "ritual@test")
    _git(repo, "config", "user.name", "ritual")
    _git(repo, "config", "commit.gpgsign", "false")

    status = repo / ".harness" / "roadmap_status.md"
    (repo / ".harness" / "roadmap-next-action-archive.md").write_text(ARCHIVE_SEED)

    status.write_text(_status_text("100", drift_rows, row_bytes))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "seed: round 100 live")

    status.write_text(_status_text("200", drift_rows, row_bytes))
    _git(repo, "commit", "-qam", "content: round 200 live, 100 now superseded")
    return repo


def _porcelain(repo: Path) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [ln[3:].strip() for ln in out.stdout.splitlines() if ln.strip()]


# --- 1) the ritual, end to end -----------------------------------------------


def test_ritual_runs_end_to_end_and_the_guard_accepts_the_result(tmp_path, capsys):
    """The whole documented sequence, ending in the ONE assertion that matters:
    `codex_context_guard` accepts the refresh commit as a verified terminating
    refresh. That is the property whose absence reddened `main` at `49b00f85`."""
    repo = _scratch_repo(tmp_path)
    status = repo / ".harness" / "roadmap_status.md"
    archive = repo / ".harness" / "roadmap-next-action-archive.md"

    # STEP 1 — archive the SUPERSEDED round, inside the content PR.
    rc = rsr.main(["--status", str(status), "--archive-superseded"])
    assert rc == 0, capsys.readouterr()
    assert "**Prior next action (post-#100).**" in archive.read_text()
    # ...and it touched ONLY the archive. This is what keeps the content merge
    # the single non-refresh commit `_owed_lag` tolerates (B-168 leg (c)).
    assert _porcelain(repo) == [".harness/roadmap-next-action-archive.md"]
    _git(repo, "commit", "-qam", "content: archive the superseded round")

    # STEP 2 — the terminating refresh: installs the pointer AND the anchor.
    rc = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(repo / "drift_archive.md"),
            "--refresh",
            "--pr",
            "PR #1338",
            "--date",
            "2026-08-14",
            "--notes",
            "what shipped",
            "--next-action",
            "The next arc is the B-71 impl leg.",
        ]
    )
    assert rc == 0, capsys.readouterr()
    text = status.read_text()
    assert "**Current next action (post-#1338).** The next arc is the B-71 impl leg." in text
    assert text.count("**Current next action (") == 1
    # ...and it touched ONLY roadmap_status.md (§12.2.1's exact file set).
    assert _porcelain(repo) == [".harness/roadmap_status.md"]

    _git(repo, "commit", "-qam", "ops: roadmap status refresh post-#1338")

    # THE ASSERTION THAT MATTERS: the guard accepts it. This pins title +
    # file set + the recorded git_head equalling its OWN parent — the exact
    # triple whose failure hard-failed ROADMAP_STATUS_DRIFT on `main`.
    assert guard._is_terminating_refresh_commit(repo, "HEAD") is True

    # And --check is clean on the result the ritual produced.
    assert rsr.main(["--status", str(status), "--check"]) == 0


def test_ritual_refresh_does_not_require_the_outgoing_round_to_be_archived(tmp_path, capsys):
    """REGRESSION (round-12 draft): an archive-before-replace precondition made
    the refresh refuse a round that, under `B-168` exit (iii), legitimately is
    NOT archived yet — the archive lags one arc BY DESIGN. That draft passed its
    unit tests and would have made the refresh unrunnable at the one moment it
    is needed."""
    repo = _scratch_repo(tmp_path)
    status = repo / ".harness" / "roadmap_status.md"
    # Deliberately SKIP the archive step; the live round (200) is unarchived.
    rc = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(repo / "drift_archive.md"),
            "--refresh",
            "--pr",
            "1338",
            "--date",
            "2026-08-14",
            "--notes",
            "n",
            "--next-action",
            "Body.",
        ]
    )
    assert rc == 0, capsys.readouterr()
    assert "**Current next action (post-#1338).** Body." in status.read_text()


# --- 2) the SOFT byte budget must not gate the HARD path ---------------------


def test_ritual_is_not_blocked_by_a_drift_log_over_the_soft_byte_budget(tmp_path, capsys):
    """REGRESSION: keying the two-file refusal on the SOFT byte guidance as well
    as the HARD row cap made EVERY terminating refresh refuse once the live log
    drifted past guidance — and post-merge the remedy it named (a content-commit
    trim) is itself a second non-refresh commit, which reds `main`."""
    # Over the BYTE budget, comfortably under the ROW cap.
    repo = _scratch_repo(tmp_path, drift_rows=4, row_bytes=1200)
    status = repo / ".harness" / "roadmap_status.md"
    rows = rsr._get_table_data_rows(status.read_text(), rsr.DRIFT_LOG_HEADING)
    assert len(rows) <= rsr.DRIFT_LOG_CAP, "precondition: ROW cap not exceeded"
    assert sum(len(r.encode()) + 1 for r in rows) > rsr.DRIFT_LOG_BYTE_BUDGET, (
        "precondition: BYTE budget IS exceeded"
    )

    drift_archive = repo / "drift_archive.md"
    rc = rsr.main(
        [
            "--status",
            str(status),
            "--archive",
            str(drift_archive),
            "--refresh",
            "--pr",
            "1338",
            "--date",
            "2026-08-14",
            "--notes",
            "n",
            "--next-action",
            "Body.",
        ]
    )
    assert rc == 0, capsys.readouterr()
    assert not drift_archive.exists(), "the terminating refresh must stay a ONE-FILE write"
    assert _porcelain(repo) == [".harness/roadmap_status.md"]


# --- 3) shallow clones: work when the round is found, fail closed when not ----


def _shallow_clone(repo: Path, dest: Path, depth: int) -> Path:
    subprocess.run(
        ["git", "clone", "-q", "--depth", str(depth), f"file://{repo}", str(dest)],
        check=True,
        capture_output=True,
    )
    is_shallow = subprocess.run(
        ["git", "-C", str(dest), "rev-parse", "--is-shallow-repository"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert is_shallow == "true", "precondition: the clone must actually be shallow"
    return dest


def test_ritual_archive_step_works_in_a_shallow_clone_that_still_has_the_round(tmp_path, capsys):
    """REGRESSION: a first draft of the history fail-close refused OUTRIGHT on
    any shallow clone — and this workspace is NORMALLY shallow (`.git/shallow`
    is present), so it would have broken the documented workflow the moment
    anyone ran it. Shallowness is only ambiguous on the NOT-FOUND path."""
    repo = _scratch_repo(tmp_path)
    clone = _shallow_clone(repo, tmp_path / "shallow_ok", depth=2)
    status = clone / ".harness" / "roadmap_status.md"

    rc = rsr.main(["--status", str(status), "--archive-superseded"])
    assert rc == 0, capsys.readouterr()
    archive = clone / ".harness" / "roadmap-next-action-archive.md"
    assert "**Prior next action (post-#100).**" in archive.read_text()
    assert _porcelain(clone) == [".harness/roadmap-next-action-archive.md"]


def test_ritual_archive_step_fails_closed_when_a_shallow_clone_hides_the_round(tmp_path):
    """The other side of the same pin: with the superseded round beyond the
    graft point, "none superseded" and "cannot see it" are indistinguishable —
    so it must RAISE rather than report 'nothing to archive' and let the owed
    round go permanently unarchived."""
    repo = _scratch_repo(tmp_path)
    clone = _shallow_clone(repo, tmp_path / "shallow_blind", depth=1)
    status = clone / ".harness" / "roadmap_status.md"

    with pytest.raises(rsr.RoadmapStatusError, match="SHALLOW"):
        rsr.find_superseded_round(status, clone)


def test_ritual_smoke_is_cheap_enough_to_run_every_arc():
    """The whole point of putting this in CI is that it costs ~1s. If the ritual
    ever grows a network call or a real-repo scan, this notices."""
    assert sys.version_info >= (3, 12)
