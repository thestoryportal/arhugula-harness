"""unrun-CLI claims (C-HE-31 §1, deterministic): a command named on a `Verified:` / `Checked:` /
`Ran:` line is re-run, and must exit 0 AND print something before it counts as clean.

The claim text is authored in a commit message or PR body, so a command is re-run only when it
parses into one of three argv shapes with every token pinned:
- `just <recipe>` -- exactly one recipe token (`just` runs extra tokens as further recipes),
  named `check` or `*-check` / `*-verify`, and never a recipe that runs this runner;
- `uv run pytest <arg>...` -- repo-relative test paths / node ids and the output flags `-q`,
  `-v`, `-x` only (a `--basetemp` would delete its directory);
- `uv run python tools/<name>.py check|verify|--check` -- a top-level tools script, one verb.
Anything else is reported as not re-run -- never run."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from pathlib import Path

from .core import MechFinding, Subject

CLAIM_LINE = re.compile(r"^(?:Verified|Checked|Ran):[ \t]*(?P<rest>.*)$", re.M | re.I)
COMMAND = re.compile(r"`(?P<cmd>(?:just|uv run) [^`]+)`")
#: The justfile recipes whose bodies invoke tools/mechanized_checks/runner.py: a claim that
#: re-runs one recurses into this check (`test_runner_recipes_match_the_justfile` pins the set).
RUNNER_RECIPES = frozenset({"lanes-verify", "mech-check", "mech-replay"})
_RECIPE = re.compile(r"check|[\w-]+-(?:check|verify)")
_PYTEST_ARG = re.compile(r"-[qvx]|(?:\w[\w-]*/)*\w[\w.-]*(?:::[\w.\[\]-]+)*")
_TOOLS_SCRIPT = re.compile(r"tools/\w[\w-]*\.py")
Execute = Callable[[list[str], Path], tuple[int, str]]


def rerunnable(cmd: str) -> list[str] | None:
    """The argv a claim may re-run, or None when any token falls outside the pinned shapes."""
    argv = cmd.split(" ")
    match argv:
        case ["just", recipe] if _RECIPE.fullmatch(recipe) and recipe not in RUNNER_RECIPES:
            return argv
        case ["uv", "run", "pytest", *args] if all(_PYTEST_ARG.fullmatch(a) for a in args):
            return argv
        case ["uv", "run", "python", script, "check" | "verify" | "--check"] if (
            _TOOLS_SCRIPT.fullmatch(script)
        ):
            return argv
        case _:
            return None


def execute_argv(argv: list[str], cwd: Path) -> tuple[int, str]:
    """An argv, never a shell string: no shell is ever given the chance to reinterpret it."""
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
        argv = rerunnable(cmd)
        if argv is None:
            return [
                MechFinding(
                    cmd,
                    "claim not re-run: outside the read-only verification grammar",
                    "a claimed check this tool can safely re-run",
                    "info",
                )
            ]
        rc, out = self.execute(argv, repo)
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
