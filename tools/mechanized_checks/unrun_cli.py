"""unrun-CLI claims (C-HE-31 §1, deterministic): a command named on a `Verified:` / `Checked:` /
`Ran:` line is re-run, and must exit 0 AND print something before it counts as clean.

The claim text is authored in a commit message or PR body, so only a read-only verification
grammar is ever executed (plain `just <check|*-check|*-verify>`, `uv run pytest`, and
`uv run python tools/<x>.py check|verify|--check`, with shell-inert tokens). Anything else is
reported as not re-run -- never run."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from pathlib import Path

from .core import MechFinding, Subject

CLAIM_LINE = re.compile(r"^(?:Verified|Checked|Ran):[ \t]*(?P<rest>.*)$", re.M | re.I)
COMMAND = re.compile(r"`(?P<cmd>(?:just|uv run) [^`]+)`")
_TOKEN = r"[\w./=:@,+\[\]-]+"
READ_ONLY = re.compile(
    r"(?:just (?:check|[\w-]+-(?:check|verify))|uv run pytest"
    rf"|uv run python tools/[\w/.-]+\.py (?:check|verify|--check))(?: {_TOKEN})*"
)
Execute = Callable[[list[str], Path], tuple[int, str]]


def execute_argv(argv: list[str], cwd: Path) -> tuple[int, str]:
    """An argv, never a shell string: READ_ONLY already admits no shell syntax, and no shell is
    ever given the chance to disagree."""
    # the longest read-only verification the grammar admits is `just codex-check` (~10 min
    # locally); 30 min is 3x that, so a hang fails loud instead of stalling the boundary
    proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=1800)
    return proc.returncode, proc.stdout + proc.stderr


class Check:
    check_id = "unrun_cli"
    kind = "deterministic"

    def __init__(self, execute: Execute = execute_argv):
        self.execute = execute

    def run(self, subject: Subject) -> list[MechFinding]:
        absent = (
            [
                MechFinding(
                    "pr-body",
                    "PR body unavailable; only the commit messages were scanned for claims",
                    "verification claims are read from the PR body and the commit messages",
                    "info",
                )
            ]
            if subject.pr_body is None
            else []
        )
        claims = dict.fromkeys(
            m["cmd"]
            for text in (subject.claims_text, subject.pr_body or "")
            for line in CLAIM_LINE.finditer(text)
            for m in COMMAND.finditer(line["rest"])
        )
        return absent + [finding for cmd in claims for finding in self._verify(subject.repo, cmd)]

    def _verify(self, repo: Path, cmd: str) -> list[MechFinding]:
        if READ_ONLY.fullmatch(cmd) is None:
            return [
                MechFinding(
                    cmd,
                    "claim not re-run: outside the read-only verification grammar",
                    "a claimed check this tool can safely re-run",
                    "info",
                )
            ]
        rc, out = self.execute(cmd.split(), repo)
        clean = rc == 0 and bool(out.strip())
        return (
            []
            if clean
            else [
                MechFinding(
                    cmd,
                    f"claimed clean but exit {rc} with "
                    f"{'non-empty' if out.strip() else 'empty'} output",
                    "exit code 0 AND positive output before claiming clean",
                )
            ]
        )
