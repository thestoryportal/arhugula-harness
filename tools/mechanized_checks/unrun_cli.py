"""unrun-CLI claims (C-HE-31 §1, deterministic): a command named on a `Verified:` / `Checked:` /
`Ran:` line is re-run, and must exit 0 AND print something before it counts as clean.

The claim text is authored in a commit message or PR body, so it never chooses what runs: a claim
naming one of two provider-free static checks is re-run as this harness environment's own ruff
EXECUTABLE, by absolute path, against the subject tree -- never through the subject's justfile,
whose recipe bodies the subject controls, and never as `python -m ruff`, which would resolve a
`ruff.py` in the subject's working directory first. Ruff reads the subject's configuration and
never executes its code. Every other claim, test runs
included (a named test can be a billed live e2e), is reported as not re-run -- never run."""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from .core import MechFinding, Subject, subject_env

CLAIM_LINE = re.compile(r"^(?:Verified|Checked|Ran):[ \t]*(?P<rest>.*)$", re.M | re.I)
COMMAND = re.compile(r"`(?P<cmd>(?:just|uv run) [^`]+)`")
#: The ruff executable installed beside this interpreter: an absolute path the subject tree cannot
#: shadow, unlike a module lookup that searches the subprocess's working directory.
RUFF = str(Path(sys.executable).parent / "ruff")
#: Claim text -> the trusted argv re-run for it (what the workspace recipe of that name runs).
RERUN: dict[str, tuple[str, ...]] = {
    "just lint": (RUFF, "check", "."),
    "just fmt-check": (RUFF, "format", "--check", "."),
}
Execute = Callable[[list[str], Path], tuple[int, str]]


def execute_argv(argv: list[str], cwd: Path) -> tuple[int, str]:
    """A trusted argv, never a shell string."""
    # bounds a hung linter only: a ruff pass over this repo is one of the static steps
    # `codex-check` runs ahead of its test suites, so a normal run finishes far inside 30 min
    proc = subprocess.run(
        argv, cwd=cwd, env=subject_env(), capture_output=True, text=True, timeout=1800
    )
    return proc.returncode, proc.stdout + proc.stderr


class Check:
    check_id = "unrun_cli"
    kind = "deterministic"
    replayable = True

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
        argv = RERUN.get(cmd)
        if argv is None:
            return [
                MechFinding(
                    cmd,
                    "claim not re-run: outside the provider-free static-check allowlist",
                    "a claimed check this tool can safely re-run",
                    "info",
                )
            ]
        rc, out = self.execute(list(argv), repo)
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
