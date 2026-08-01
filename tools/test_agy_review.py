"""Behavioral tests for the fail-closed Antigravity diff reviewer."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWER = ROOT / "tools" / "agy_review.py"


def _fake_commands(tmp_path: Path, *, agy_output: str, agy_exit: int = 0) -> tuple[Path, Path]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    capture = tmp_path / "agy-prompt.txt"
    review_root = tmp_path / "main-root"
    (review_root / ".git").mkdir(parents=True)

    git = bin_dir / "git"
    git.write_text(
        "#!/bin/sh\n"
        "if [ \"$1 $2 $3\" = 'rev-parse --path-format=absolute --git-common-dir' ]; then\n"
        "  printf '%s\\n' \"$AGY_REVIEW_ROOT/.git\"\n"
        "  exit 0\n"
        "fi\n"
        "if [ \"$1\" = 'ls-files' ]; then exit 0; fi\n"
        "printf '%s\\n' 'diff --git a/a.py b/a.py' '+new line'\n",
        encoding="utf-8",
    )
    git.chmod(0o755)

    agy = bin_dir / "agy"
    agy.write_text(
        "#!/bin/sh\n"
        'pwd > "$AGY_CWD_CAPTURE"\n'
        'printf \'%s\\n\' "$@" > "$AGY_ARGS_CAPTURE"\n'
        "prev=''\n"
        'for arg in "$@"; do\n'
        '  if [ "$prev" = \'-p\' ]; then printf \'%s\' "$arg" > "$AGY_CAPTURE"; fi\n'
        '  prev="$arg"\n'
        "done\n"
        'if [ -n "${GEMINI_API_KEY:-}${GOOGLE_API_KEY:-}${GOOGLE_GENAI_USE_VERTEXAI:-}'
        "${GOOGLE_APPLICATION_CREDENTIALS:-}${GOOGLE_CLOUD_PROJECT:-}"
        '${GOOGLE_CLOUD_LOCATION:-}" ]; then\n'
        "  echo 'provider environment leaked'\n"
        "  exit 9\n"
        "fi\n"
        f"printf '%b\\n' {agy_output!r}\n"
        f"exit {agy_exit}\n",
        encoding="utf-8",
    )
    agy.chmod(0o755)
    return bin_dir, capture


def _run(tmp_path: Path, *, agy_output: str, agy_exit: int = 0) -> subprocess.CompletedProcess[str]:
    bin_dir, capture = _fake_commands(tmp_path, agy_output=agy_output, agy_exit=agy_exit)
    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{bin_dir}:{env['PATH']}",
            "AGY_CAPTURE": str(capture),
            "AGY_ARGS_CAPTURE": str(tmp_path / "agy-args.txt"),
            "AGY_CWD_CAPTURE": str(tmp_path / "agy-cwd.txt"),
            "AGY_REVIEW_ROOT": str(tmp_path / "main-root"),
            "GEMINI_API_KEY": "must-not-leak",
            "GOOGLE_API_KEY": "must-not-leak",
            "GOOGLE_GENAI_USE_VERTEXAI": "must-not-leak",
            "GOOGLE_APPLICATION_CREDENTIALS": "must-not-leak",
            "GOOGLE_CLOUD_PROJECT": "must-not-leak",
            "GOOGLE_CLOUD_LOCATION": "must-not-leak",
        }
    )
    return subprocess.run(
        [sys.executable, str(REVIEWER), "--base", "main"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )


def test_review_passes_actual_diff_and_accepts_exact_verdict(tmp_path: Path) -> None:
    proc = _run(tmp_path, agy_output="F1 none\nVERDICT: APPROVE")

    assert proc.returncode == 0, proc.stderr
    prompt = (tmp_path / "agy-prompt.txt").read_text(encoding="utf-8")
    assert "diff --git a/a.py b/a.py" in prompt
    assert "Do not invoke terminal commands" in prompt
    assert "Do not invoke URL, browser, or MCP tools" in prompt
    args = (tmp_path / "agy-args.txt").read_text(encoding="utf-8").splitlines()
    assert "--sandbox" in args
    assert "--dangerously-skip-permissions" in args
    assert f"authoritative workspace root is {tmp_path}" in prompt
    assert (tmp_path / "agy-cwd.txt").read_text(encoding="utf-8").strip() == str(tmp_path)
    assert proc.stdout.rstrip().endswith("VERDICT: APPROVE")


def test_review_rejects_permission_denial_even_when_agy_exits_zero(tmp_path: Path) -> None:
    proc = _run(
        tmp_path,
        agy_output=(
            "jetski: no output produced - a tool required the command permission "
            "that headless mode cannot prompt for"
        ),
    )

    assert proc.returncode != 0
    assert "missing exact final verdict" in proc.stderr


def test_review_preserves_findings_on_nonzero_agy_exit(tmp_path: Path) -> None:
    proc = _run(
        tmp_path,
        agy_output="F1 [P1] concrete defect\nVERDICT: BLOCK",
        agy_exit=7,
    )

    assert proc.returncode == 7
    assert proc.stdout.rstrip().endswith("VERDICT: BLOCK")
    assert "agy-review: reviewer failed: exit 7" in proc.stderr
