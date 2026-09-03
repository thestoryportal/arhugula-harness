"""Consumer witness suite for the U-CTX-03 `roadmap_status.md` truncation (U-CTX-04).

Table-driven: every REAL dependent of `.harness/roadmap_status.md` located by
`rg -l 'roadmap_status' tools/ .claude/ .codex/ .githooks/` is exercised
against the file AS IT NOW STANDS post-truncation (not a synthetic stand-in
for the ones that touch the real repo state) — asserting the consumer still
functions: extracts the field it depends on, emits well-formed hook JSON, or
still reports the required source path as present. This closes the "never
exercised against a truncated file" gap named in the U-CTX-04 acceptance
criteria for `closure_certification.py` / `docs_completeness.py`.

Grounding note (recorded, not glossed over): `tools/closure_gate.py`'s
`_roadmap_status()` function is a false-positive hit on the name alone — it
reads `Project_Roadmap_v1.md` (`ROADMAP = REPO_ROOT / "Project_Roadmap_v1.md"`
at closure_gate.py:33), not `.harness/roadmap_status.md`. It is therefore NOT
a content consumer of this arc's truncation and is intentionally excluded
below (there is nothing to witness).

Consumer inventory + what each witness below actually exercises:

  - `hook_roadmap_next` (tools/hooks/lib.sh) — the ONE function that parses
    "## Next action" CONTENT (not just the anchor table). Callers:
    tools/hooks/postcompact-reinject.sh, tools/hooks/prompt-context.sh,
    tools/hooks/stop-loop.sh, tools/roadmap-audit/session-start.sh,
    hook_write_checkpoint (lib.sh itself).
  - tools/roadmap-audit/post-merge-refresh.sh — reads the ANCHOR table's
    `git_head` field via grep; unaffected by the Next-action truncation in
    content-shape, exercised here for completeness against the real file.
  - tools/codex_context_guard.py `_roadmap_status()` — reads the anchor table
    (hash/git_head/last_refreshed) only.
  - tools/closure_certification.py `_source_paths_check()` +
    tools/docs_completeness.py `_evidence_matrix_check()` — check that
    `.harness/roadmap_status.md` is still a real file at the same path (a
    path-presence check, exercised for real against the truncated file).
  - tools/arc_exit_report.py `_refresh_shape_ok()` — the §12.2.1
    terminating-refresh-shape detector (git-history function; exercised with
    a real one-file commit carrying the ACTUAL truncated bytes).

Mutation probe (U-CTX-04's required RED-then-restored demonstration): see the
session report — `_ARCHIVED_PARAGRAPH_RE`/byte-budget guard in
tools/roadmap_status_refresh.py was removed, `tools/test_roadmap_status_refresh.py`'s
new byte-budget/inline-history tests went RED (3 failures), and the guard was
restored via a `cp` backup (not `git checkout`). That is the load-bearing
mutation probe for the truncation guard itself; this file's own witnesses are
integration-shaped (real subprocess / real function calls against the real
truncated artifact), so their "mutation" is the artifact already existing in
truncated form — reverting `.harness/roadmap_status.md` to the pre-truncation
9-heading-but-huge shape would not fail any witness here (every one of these
consumers is deliberately content-agnostic beyond the anchor table + the
Next-action R-/U- token scan), which is itself the finding worth recording:
none of the ~10 real functional dependents besides `hook_roadmap_next` cares
about Next-action body SIZE, only about section/path/table PRESENCE.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIB_SH = ROOT / "tools" / "hooks" / "lib.sh"
POSTCOMPACT_HOOK = ROOT / "tools" / "hooks" / "postcompact-reinject.sh"
PROMPT_CONTEXT_HOOK = ROOT / "tools" / "hooks" / "prompt-context.sh"
STOP_LOOP_HOOK = ROOT / "tools" / "hooks" / "stop-loop.sh"
SESSION_START_HOOK = ROOT / "tools" / "roadmap-audit" / "session-start.sh"
POST_MERGE_REFRESH_HOOK = ROOT / "tools" / "roadmap-audit" / "post-merge-refresh.sh"
STATUS_PATH = ROOT / ".harness" / "roadmap_status.md"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import arc_exit_report as aer  # noqa: E402
import closure_certification as cc  # noqa: E402
import codex_context_guard as ccg  # noqa: E402
import docs_completeness as dc  # noqa: E402


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=15)


@pytest.fixture
def scratch_repo(tmp_path: Path) -> Path:
    """A throwaway git repo whose `.harness/roadmap_status.md` is a BYTE-FOR-BYTE
    copy of the real, post-truncation file — mirrors the existing
    tools/roadmap-audit/test_session_start.sh + tools/hooks/test_stop_loop.sh
    fixture convention (mktemp -d repo + CLAUDE_PROJECT_DIR), driven from
    Python so the ~10-consumer table lives in one place."""
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@t.t")
    _git(tmp_path, "config", "user.name", "t")
    harness = tmp_path / ".harness"
    harness.mkdir()
    (harness / "roadmap_status.md").write_bytes(STATUS_PATH.read_bytes())
    (tmp_path / "Project_Roadmap_v1.md").write_text("stub\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "seed: real truncated roadmap_status.md")
    return tmp_path


def _run_hook(
    hook: Path, project_dir: Path, stdin: str = "{}", extra_env: dict[str, str] | None = None
):
    import os

    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(hook)],
        input=stdin,
        cwd=project_dir,
        capture_output=True,
        text=True,
        env=env,
        timeout=20,
    )


# --- hook_roadmap_next: the direct content-parsing function -------------------


def test_hook_roadmap_next_runs_clean_against_the_real_truncated_file():
    """No crash, deterministic output, against the ACTUAL current file (not a
    fixture copy) — the ground-truth witness the table-driven ones below cross-check."""
    out = subprocess.run(
        ["bash", "-c", f"source {LIB_SH} && hook_roadmap_next .harness/roadmap_status.md"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert out.returncode == 0, out.stderr
    # Deterministic: re-running yields the same result (no ordering/parsing flake).
    out2 = subprocess.run(
        ["bash", "-c", f"source {LIB_SH} && hook_roadmap_next .harness/roadmap_status.md"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert out.stdout == out2.stdout


def test_hook_roadmap_next_still_extracts_a_backtick_token_when_present(tmp_path):
    """Positive control: hook_roadmap_next's grep-based extraction still works on
    the NEW (short) "## Next action" shape when a `U-`/`R-` token IS present —
    proves the truncation did not break the extraction mechanism itself, only
    changed whether the CURRENT round happens to carry such a token (it
    doesn't post-#1290 — see the next test)."""
    dash = tmp_path / "roadmap_status.md"
    dash.write_text(
        "## Next action\n\n"
        "**Purpose.** stub.\n\n"
        "**Current next action (post-#9999).** Ship `U-CTX-07` next.\n\n"
        "**Archive.** `.harness/roadmap-next-action-archive.md`.\n\n"
        "## Remaining forward work\n",
        encoding="utf-8",
    )
    out = subprocess.run(
        ["bash", "-c", f"source {LIB_SH} && hook_roadmap_next '{dash}'"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "U-CTX-07"


def test_hook_roadmap_next_on_real_truncated_file_returns_the_live_token():
    """GROUNDED FINDING (recorded, not silently absorbed): pre-truncation, this
    same function returned a STALE `U-IS-11` token — the first `` `U-`/`R-` ``
    backtick match anywhere in the 292KB "## Next action" body, buried deep in
    OLD "Prior next action" history, NOT the actual current pointer (the
    pre-existing `[[roadmap-hook-next-parser-b-token-blind]]` defect class).
    Post-truncation, the LIVE pointer requirement (AGENTS.md) demands the hook
    surface the CURRENT round's own token — the truncated head carries the
    canonical `next implementable unit is \\`<token>\\`` phrase precisely so
    the hook's primary sed path resolves it. Empty output would silently strip
    the autonomous loop of its dashboard item (codex round-2 catch against the
    earlier `== \"\"` pin, which had normalized the regression). The token is
    asserted non-empty AND non-stale rather than pinned to one literal, so a
    future round rotating the pointer doesn't break this witness.
    B-230 Task 2 widened the parser's carriers (a backticked plan-doc pointer
    -> `plan:<name>`, a bold unit, the unit after the first `then `), so the
    accepted set below is every carrier on the CURRENT line, not a second copy
    of the parser's precedence — membership is the stale-leak witness."""
    out = subprocess.run(
        ["bash", "-c", f"source {LIB_SH} && hook_roadmap_next .harness/roadmap_status.md"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert out.returncode == 0
    token = out.stdout.strip()
    assert token != "U-IS-11", "the pre-truncation stale-history token must never resurface"
    status_text = (ROOT / ".harness" / "roadmap_status.md").read_text()
    current_line = next(
        line for line in status_text.splitlines() if line.startswith("**Current next action (")
    )
    # Conditional demand (codex round-7): a B-only round LEGITIMATELY yields
    # empty — hook_roadmap_next is documented + pinned (tools/hooks/lib.sh,
    # test_lib.sh) to surface a `U-`/`R-` unit or a `plan:<name>` pointer. So:
    # when the CURRENT line carries any such carrier, the hook MUST resolve one
    # of the current line's own (never empty, never archived history); when it
    # carries none, empty is the documented correct answer.
    import re as _re

    current_tokens = {
        f"plan:{n}" for n in _re.findall(r"`\.harness/plan/([A-Za-z0-9._-]+)\.md`", current_line)
    } | {
        t
        for t in _re.findall(r"\b([UR]-[A-Za-z0-9._-]*[A-Za-z0-9_-])", current_line)
        if ".." not in t
    }
    if current_tokens:
        assert token in current_tokens, (
            f"hook returned {token!r} but the live Current line's own tokens are "
            f"{sorted(current_tokens)} — a stale/archived pointer leaked "
            "(empty would silently strip the loop's dashboard item)"
        )
    else:
        assert token == "", "B-only round: the documented contract is an empty token"


# --- Table-driven: the real bash-hook callers of hook_roadmap_next ------------


def test_postcompact_reinject_runs_against_truncated_file(scratch_repo):
    result = _run_hook(POSTCOMPACT_HOOK, scratch_repo, stdin=json.dumps({"session_id": "s1"}))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "roadmap next-action=" in ctx
    assert "Post-compaction on" in ctx


def test_prompt_context_runs_against_truncated_file(scratch_repo):
    result = _run_hook(PROMPT_CONTEXT_HOOK, scratch_repo, stdin="{}")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert ctx.startswith("[roadmap] next=")


def test_stop_loop_runs_against_truncated_file(scratch_repo):
    result = _run_hook(
        STOP_LOOP_HOOK,
        scratch_repo,
        stdin="{}",
        extra_env={"HARNESS_LOOP": "1", "HARNESS_LOOP_MAX": "5"},
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["decision"] == "block"
    assert "Dashboard next-action:" in payload["reason"]


def test_session_start_runs_against_truncated_file(scratch_repo):
    result = _run_hook(SESSION_START_HOOK, scratch_repo, stdin="{}")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert ctx.startswith("[ROADMAP")
    assert "next=" in ctx


def _rewrite_stored_git_head(repo: Path, head8: str) -> None:
    import re as _re

    status = repo / ".harness" / "roadmap_status.md"
    text = status.read_text(encoding="utf-8")
    new_text, n = _re.subn(
        r"(\| *`git_head` *\| *`)[a-f0-9]{8}(`)", rf"\g<1>{head8}\g<2>", text, count=1
    )
    assert n == 1, "anchor git_head row not found — truncation must preserve it"
    status.write_text(new_text, encoding="utf-8")


def test_post_merge_refresh_silent_when_stored_head_matches(scratch_repo):
    """post-merge-refresh.sh's only roadmap_status.md read is the anchor table's
    `git_head` grep. Discriminating direction 1 (codex round-4 — the earlier
    form accepted silence OR any output, a vacuous probe): with the stored
    head REWRITTEN to equal ORIGIN_HEAD, the no-advance early exit MUST be
    silent — which only happens if the grep against the truncated file's
    anchor table actually parsed the stored head."""
    head = _git(scratch_repo, "rev-parse", "HEAD").stdout.strip()[:8]
    _rewrite_stored_git_head(scratch_repo, head)
    result = _run_hook(
        POST_MERGE_REFRESH_HOOK,
        scratch_repo,
        stdin=json.dumps({"tool_input": {"command": "gh pr merge 123"}}),
        extra_env={"POST_MERGE_REFRESH_REF": head},
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "", (
        "stored==origin head must be the SILENT path; output means the git_head "
        "grep failed against the truncated anchor table"
    )


def test_post_merge_refresh_emits_when_origin_advanced(scratch_repo):
    """Discriminating direction 2: stored head pinned to the PARENT commit and
    ORIGIN_HEAD at a newer non-refresh-titled commit MUST emit the §12.2
    refresh-owed reminder. A truncation that broke the git_head row would make
    STORED_HEAD empty and this exact emit-branch assertion fail."""
    base = _git(scratch_repo, "rev-parse", "HEAD").stdout.strip()[:8]
    (scratch_repo / "feature.txt").write_text("x", encoding="utf-8")
    _git(scratch_repo, "add", "feature.txt")
    _git(scratch_repo, "commit", "-qm", "feat: substantive change")
    new_head = _git(scratch_repo, "rev-parse", "HEAD").stdout.strip()[:8]
    _rewrite_stored_git_head(scratch_repo, base)
    result = _run_hook(
        POST_MERGE_REFRESH_HOOK,
        scratch_repo,
        stdin=json.dumps({"tool_input": {"command": "gh pr merge 123"}}),
        extra_env={"POST_MERGE_REFRESH_REF": new_head},
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    ctx = payload["hookSpecificOutput"]["additionalContext"]
    assert "terminating refresh is owed" in ctx
    assert new_head in ctx


# --- Python tool consumers (path-presence / anchor-table only) ----------------


def test_codex_context_guard_parses_the_real_anchor_table():
    state = ccg._roadmap_status(ROOT)
    assert state.hash  # anchor table parsed
    assert state.git_head
    assert state.last_refreshed


def test_closure_certification_still_finds_roadmap_status_path():
    missing_files = [source for source in cc.REQUIRED_SOURCE_PATHS if not (ROOT / source).exists()]
    assert ".harness/roadmap_status.md" not in missing_files


def test_docs_completeness_still_finds_roadmap_status_path():
    assert ".harness/roadmap_status.md" in dc.REQUIRED_MATRIX_SOURCES
    assert (ROOT / ".harness" / "roadmap_status.md").is_file()


def test_arc_exit_report_refresh_shape_detector_against_a_real_truncated_commit(tmp_path):
    """Builds a real one-file commit carrying the ACTUAL truncated bytes and
    confirms `_refresh_shape_ok` (the §12.2.1 terminating-refresh detector)
    still classifies a roadmap-status-only commit correctly."""
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@t.t")
    _git(tmp_path, "config", "user.name", "t")
    harness = tmp_path / ".harness"
    harness.mkdir()
    (tmp_path / "README.md").write_text("seed\n", encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "base")

    (harness / "roadmap_status.md").write_bytes(STATUS_PATH.read_bytes())
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "ops: roadmap status refresh post-test")
    sha = _git(tmp_path, "rev-parse", "HEAD").stdout.strip()

    assert aer._refresh_shape_ok(sha, tmp_path) is True

    # Negative control: a commit touching an EXTRA file must not classify as
    # refresh-only, even carrying the same truncated bytes.
    (tmp_path / "README.md").write_text("seed2\n", encoding="utf-8")
    (harness / "roadmap_status.md").write_bytes(STATUS_PATH.read_bytes())
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "not a refresh")
    sha2 = _git(tmp_path, "rev-parse", "HEAD").stdout.strip()
    assert aer._refresh_shape_ok(sha2, tmp_path) is False
