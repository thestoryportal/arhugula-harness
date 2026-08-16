"""Standing invariant: every `tools/test_*.py` either RUNS somewhere, or says why not.

`B-184` audited `tools/` and found **15 of 43** test modules executed by no mechanism at
all — 14 of them for no reason anyone had decided, just drift. That sweep is worthless as
a one-off: the same drift resumes the next time a module is added without wiring. This
guard makes it an invariant.

**The rule.** For every `tools/test_*.py`, exactly one of:

* it appears in something that actually executes it — a workflow `run:` block,
  `tools/codex-parity-check.sh`, or the `justfile`; or
* it appears in `EXCLUSIONS` below **with a reason**.

Anything else fails. The reason is the point: `B-184`'s own worst error was classifying
nine modules as "credential-gated" **from their filenames**, when they in fact held 64
provider-free tests that pass in 5.5s with every credential stripped. **A filename is not
a gate.** Without a written reason, "deliberately excluded" and "forgotten" are
indistinguishable — which is precisely the state that let 15 modules rot.

**The guard is two-way.** A stale `EXCLUSIONS` entry — for a module that is now executed,
or that no longer exists — fails too. An exclusion list that only ever grows becomes its
own drift surface.

**Why coverage is derived by PARSING, not by regex.** `B-184` needed four attempts. A
path-prefixed pattern (`tools/test_*.py`) missed CI's **bare-filename** invocations under
`working-directory: tools` and reported 33 dead; a continuation-line pattern mis-reported
an already-wired module and reported 23. Only parsing the workflow YAML's `run:` blocks
reconciled, at 15. This module parses.

Run standalone (`python tools/tools_test_coverage_guard.py`) or import `validate`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

#: Modules deliberately NOT executed by any gate, each with the reason it is out.
#: An entry here is a decision, not a parking space — state the cost or the dependency.
#: Empty is the healthy state, and it is the state B-184 left the tree in. The one
#: module that had a real reason to stay out of the parity gate —
#: `test_codex_loop.py`, 16 tests at ~82s — was not excluded from EXECUTION at all: it
#: was given its own CI job (`tools-test-coverage-and-codex-loop`), which is the
#: distinction this guard exists to force. "Too slow for the pre-push gate" is a reason
#: to move a module to another lane, NOT a reason to stop running it.
EXCLUSIONS: dict[str, str] = {}


def test_modules(root: Path | None = None) -> set[str]:
    """Every `tools/test_*.py`, by basename."""
    base = root or ROOT
    return {p.name for p in (base / "tools").glob("test_*.py")}


def _run_blocks(root: Path) -> list[str]:
    """Every shell body that CI or local tooling actually executes.

    Workflow `run:` steps are read through a YAML parse rather than a text scan, because
    a scan cannot tell an invocation from a comment mentioning the same filename — and
    `B-184` has three wrong answers on record from trying.
    """
    blobs: list[str] = []
    workflows = root / ".github" / "workflows"
    if workflows.is_dir():
        for wf in sorted([*workflows.glob("*.yml"), *workflows.glob("*.yaml")]):
            try:
                doc = yaml.safe_load(wf.read_text(encoding="utf-8"))
            except yaml.YAMLError:  # a malformed workflow is not this guard's business
                continue
            if not isinstance(doc, dict):
                continue
            for job in (doc.get("jobs") or {}).values():
                if not isinstance(job, dict):
                    continue
                for step in job.get("steps") or []:
                    if isinstance(step, dict) and isinstance(step.get("run"), str):
                        blobs.append(step["run"])
    for extra in (root / "tools" / "codex-parity-check.sh", root / "justfile"):
        if extra.is_file():
            blobs.append(extra.read_text(encoding="utf-8"))
    return blobs


#: `pytest` flags whose VALUE is a test path being EXCLUDED, not run.
_NEGATING_FLAGS = ("--ignore", "--deselect")


def _pytest_targets(blob: str) -> set[str]:
    """Test paths a shell body actually hands to pytest.

    Presence of a basename anywhere in the text is NOT execution — out-of-family review
    [P2]: `cat tools/test_x.py`, a comment inside a `run:` block, and
    `--ignore=tools/test_x.py` each satisfy a substring check while running nothing, and
    `--ignore` means the exact opposite. So: join shell continuations, drop comments, keep
    only commands that invoke pytest, and within those skip negating flags.
    """
    joined = blob.replace("\\\n", " ")
    targets: set[str] = set()
    for raw in joined.splitlines():
        line = raw.split("#", 1)[0]
        if "pytest" not in line:
            continue
        for token in line.split():
            if any(token.startswith(flag) for flag in _NEGATING_FLAGS):
                continue
            if token.endswith(".py"):
                targets.add(Path(token).name)
    return targets


def executed_modules(root: Path | None = None) -> set[str]:
    """The subset of `test_modules` genuinely handed to pytest somewhere."""
    base = root or ROOT
    targets: set[str] = set()
    for blob in _run_blocks(base):
        targets |= _pytest_targets(blob)
    return {name for name in test_modules(base) if name in targets}


def validate(root: Path | None = None) -> list[str]:
    """Return the violations, empty when the invariant holds."""
    base = root or ROOT
    present = test_modules(base)
    executed = executed_modules(base)
    problems: list[str] = []

    for name in sorted(present - executed - set(EXCLUSIONS)):
        problems.append(
            f"{name}: executed by NO workflow, parity script or justfile recipe, and carries "
            f"no EXCLUSIONS entry. Wire it, or add an entry stating why it is out. Do not "
            f"infer from the filename that it is credential-gated — run it with credentials "
            f"stripped first (B-184: nine modules were mis-classified exactly that way)."
        )
    for name in sorted(set(EXCLUSIONS) & executed):
        problems.append(
            f"{name}: listed in EXCLUSIONS but IS executed. Remove the stale entry — an "
            f"exclusion list that only grows becomes its own drift surface."
        )
    for name in sorted(set(EXCLUSIONS) - present):
        problems.append(f"{name}: listed in EXCLUSIONS but no such module exists. Remove it.")
    for name, reason in sorted(EXCLUSIONS.items()):
        if not reason.strip():
            problems.append(f"{name}: EXCLUSIONS entry has an empty reason.")
    return problems


def main() -> int:
    problems = validate()
    if problems:
        print("tools/ test-coverage guard FAILED:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    present, executed = test_modules(), executed_modules()
    print(
        f"tools/ test-coverage guard OK — {len(present)} modules: "
        f"{len(executed)} executed, {len(EXCLUSIONS)} explicitly excluded"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
