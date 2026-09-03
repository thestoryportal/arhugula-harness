"""`just arc-close` — the one-invocation arc close-out tail (B-230 Task 3).

The recipe is EXECUTED, not dry-run: `just -n` does not expand `$@`, so only a real
run proves the variadic tail reaches `arc-metrics queue` as separate argv elements.
A shim `just` ahead of the real binary on PATH records each inner call's argv as a
JSON array — one element per line would let a `"$*"`-flattened forwarding pass as
`"$@"` forwarding, so the assertions compare argument ARRAYS (plan constraints r2, r6).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARRIERS = (
    ROOT / ".claude" / "skills" / "ship-pr" / "SKILL.md",
    ROOT / ".agents" / "skills" / "ship-pr" / "SKILL.md",
)


def _run(tmp_path: Path, *args: str) -> tuple[int, list[list[str]]]:
    shim_dir = tmp_path / "bin"
    shim_dir.mkdir(parents=True)
    log = tmp_path / "calls.jsonl"
    shim = shim_dir / "just"
    shim.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        f"open({str(log)!r}, 'a').write(json.dumps(sys.argv[1:]) + '\\n')\n"
    )
    shim.chmod(0o755)
    real = shutil.which("just")
    assert real is not None, "just must be installed: the recipe test executes it"
    env = {**os.environ, "PATH": f"{shim_dir}{os.pathsep}{os.environ['PATH']}"}
    proc = subprocess.run(
        [real, "arc-close", *args], capture_output=True, text=True, env=env, cwd=ROOT
    )
    calls = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    return proc.returncode, calls


def test_forwards_full_queue_tail(tmp_path: Path) -> None:
    rc, calls = _run(
        tmp_path,
        "12", "abc123", "cp.md",
        "--arc-id", "u-x", "--arc-type", "applying", "--decisions", "0",
        "--round-logs", "logs/*.log", "--transcript", "t.jsonl", "--levers", "B-1", "B-2",
    )  # fmt: skip
    assert rc == 0
    assert calls == [
        ["arc-exit-report", "--pr", "12", "--merge-sha", "abc123", "--checkpoint", "cp.md"],
        [
            "arc-metrics", "queue", "--pr", "12",
            "--arc-id", "u-x", "--arc-type", "applying", "--decisions", "0",
            "--round-logs", "logs/*.log", "--transcript", "t.jsonl", "--levers", "B-1", "B-2",
        ],
    ]  # fmt: skip


def test_omitting_transcript_and_levers_is_representable(tmp_path: Path) -> None:
    rc, calls = _run(
        tmp_path,
        "12", "abc123", "cp.md",
        "--arc-id", "u-x", "--arc-type", "applying", "--decisions", "0",
        "--round-logs", "logs/*.log",
    )  # fmt: skip
    assert rc == 0
    assert calls[1] == [
        "arc-metrics", "queue", "--pr", "12",
        "--arc-id", "u-x", "--arc-type", "applying", "--decisions", "0",
        "--round-logs", "logs/*.log",
    ]  # fmt: skip


def test_stops_at_the_first_failing_step(tmp_path: Path) -> None:
    """`just` runs the recipe lines in order and stops at the first non-zero exit:
    a failed exit report must never be followed by a queued metrics row."""
    shim_dir = tmp_path / "bin"
    shim_dir.mkdir(parents=True)
    log = tmp_path / "calls.jsonl"
    shim = shim_dir / "just"
    shim.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        f"open({str(log)!r}, 'a').write(json.dumps(sys.argv[1:]) + '\\n')\n"
        "sys.exit(7)\n"
    )
    shim.chmod(0o755)
    real = shutil.which("just")
    assert real is not None
    env = {**os.environ, "PATH": f"{shim_dir}{os.pathsep}{os.environ['PATH']}"}
    proc = subprocess.run(
        [real, "arc-close", "12", "abc123", "cp.md", "--arc-id", "u-x"],
        capture_output=True, text=True, env=env, cwd=ROOT,
    )  # fmt: skip
    assert proc.returncode != 0
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    assert [c[0] for c in calls] == ["arc-exit-report"]


def test_rejects_a_second_pr_in_the_queue_tail_before_running_anything(tmp_path: Path) -> None:
    """codex r1 on b-230-task-3: argparse's last-wins would let `--pr 42` in the tail write
    the exit report for one PR and queue metrics for another. Both spellings are refused,
    and the check runs first, so neither inner call happens."""
    for tail in (("--pr", "42"), ("--pr=42",)):
        rc, calls = _run(
            tmp_path / tail[0].lstrip("-").replace("=", "_"),
            "12",
            "abc123",
            "cp.md",
            "--arc-id",
            "u-x",
            *tail,
        )
        assert rc != 0, tail
        assert calls == [], tail


def test_both_ship_pr_carriers_invoke_arc_close_and_neither_keeps_the_split_calls() -> None:
    """Carrier parity (plan constraint r5): the Claude and Codex ship-pr carriers differ
    by design elsewhere, so this is presence, not byte-equality."""
    for carrier in CARRIERS:
        text = carrier.read_text(encoding="utf-8")
        assert "just arc-close <NNN> <merge-sha> <" in text, carrier
        assert "just arc-exit-report --pr <NNN>" not in text, carrier
        assert "just arc-metrics queue --pr <NNN>" not in text, carrier
