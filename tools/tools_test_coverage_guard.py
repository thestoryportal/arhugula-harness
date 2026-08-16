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

import ast
import shlex
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


#: `pytest` flags whose VALUE names a test path being EXCLUDED, not run. Both the
#: `--flag=value` and the space-separated `--flag value` spellings are handled.
_NEGATING_FLAGS = ("--ignore", "--ignore-glob", "--deselect")

#: Tokens that may precede the real command without being it: environment prefixes and
#: runner wrappers. `env A=B uv run python -m pytest ...` is a pytest invocation;
#: `echo pytest ...` is not, and the difference is which token is the COMMAND.
_WRAPPERS = frozenset(
    {"env", "uv", "run", "poetry", "python", "python3", "-m", "--no-sync", "exec", "time"}
)


def _is_pytest_command(tokens: list[str]) -> int | None:
    """Index of the `pytest` token when these tokens are a pytest COMMAND, else `None`.

    Out-of-family review [P2], twice: a line merely *containing* `pytest` is not a pytest
    run. `echo pytest tools/test_x.py` prints a string. So walk from the command position,
    stepping over wrappers and `VAR=value` prefixes only, and require `pytest` to be the
    command actually reached.
    """
    for i, tok in enumerate(tokens):
        if tok == "pytest" or tok.endswith("/pytest"):
            return i
        if tok in _WRAPPERS or ("=" in tok.split("/")[0][:64] and not tok.startswith("-")):
            continue  # environment assignment or runner wrapper
        return None
    return None


def _pytest_targets(blob: str) -> set[str]:
    """Test paths a shell body actually hands to pytest as positional targets.

    Presence of a basename anywhere in the text is NOT execution. Three shapes that a
    substring check wrongly certifies, each pinned by a test: `cat tools/test_x.py` (wrong
    command), a `#` comment inside a `run:` block (not a command at all), and
    `--ignore=tools/test_x.py` / `--ignore tools/test_x.py` (which mean the OPPOSITE).
    """
    joined = blob.replace("\\\n", " ")
    targets: set[str] = set()
    for raw in joined.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        try:
            tokens = shlex.split(line)
        except ValueError:  # unbalanced quotes in a shell fragment
            tokens = line.split()
        idx = _is_pytest_command(tokens)
        if idx is None:
            continue
        skip_next = False
        for token in tokens[idx + 1 :]:
            if skip_next:
                skip_next = False
                continue
            if token in _NEGATING_FLAGS:
                skip_next = True  # `--ignore tools/test_x.py`
                continue
            if any(token.startswith(f + "=") for f in _NEGATING_FLAGS):
                continue  # `--ignore=tools/test_x.py`
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


def _establishes_import_path(node: ast.stmt) -> bool:
    """True when this statement makes `tools/` importable for what follows.

    Either `sys.path.insert(...)` / `sys.path.append(...)`, or an `importlib` file-path
    load (`spec_from_file_location`) which sidesteps `sys.path` entirely.
    """
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        func = sub.func
        if isinstance(func, ast.Attribute):
            if func.attr in {"insert", "append"} and isinstance(func.value, ast.Attribute):
                if func.value.attr == "path":
                    return True
            if func.attr == "spec_from_file_location":
                return True
        if isinstance(func, ast.Name) and func.id == "spec_from_file_location":
            return True
    return False


def _bare_sibling(node: ast.stmt, siblings: set[str], own: str) -> str | None:
    """The sibling module this statement imports BARE, if any.

    `from tools.X import ...` is excluded: it resolves through the repo root and was
    measured working from both cwds, so it is a second legitimate convention.
    """
    names: list[str] = []
    if isinstance(node, ast.Import):
        names = [a.name.split(".")[0] for a in node.names]
    elif isinstance(node, ast.ImportFrom):
        if node.level or not node.module:
            return None
        if node.module.split(".")[0] == "tools":
            return None
        names = [node.module.split(".")[0]]
    for name in names:
        if name in siblings and name != own:
            return name
    return None


def import_self_sufficiency_problems(root: Path | None = None) -> list[str]:
    """Modules that import a sibling before making `tools/` importable.

    `B-184` close-out (3). `tools/` is not a package and pytest runs under
    `--import-mode=importlib`, so nothing puts this directory on `sys.path`. Ten modules
    nevertheless passed in the parity gate — because an unrelated sibling happened to
    insert the path first, earlier in the same invocation. Run alone from the repo root
    they failed at collection. That is an order-dependent green: silent, and it evaporates
    the moment the inserting sibling is renamed or the file order changes.

    Read through the **AST**, not the raw text (out-of-family review [P2], twice). A text
    scan has two holes in opposite directions: a marker appearing in a comment — or *after*
    the import it is supposed to precede — silently excuses a genuinely broken module,
    while a docstring containing `import arc_ledger` as an example fabricates a failure.
    Parsing removes both, and lets the check enforce what actually matters: **order**.
    """
    base = root or ROOT
    tools_dir = base / "tools"
    siblings = {p.stem for p in tools_dir.glob("*.py")}
    problems: list[str] = []

    for path in sorted(tools_dir.glob("test_*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:  # a broken module is pytest's problem, not this guard's
            continue
        established = False
        for node in tree.body:
            if _establishes_import_path(node):
                established = True
                continue
            sibling = _bare_sibling(node, siblings, path.stem)
            if sibling and not established:
                problems.append(
                    f"{path.name}: imports the sibling `{sibling}` before putting `tools/` "
                    f"on `sys.path`. It will import only when another file in the same "
                    f"pytest run inserted the path first — an order-dependent pass. Add "
                    f"`sys.path.insert(0, str(Path(__file__).resolve().parent))` ABOVE the "
                    f"import, or load the sibling via "
                    f"`importlib.util.spec_from_file_location`."
                )
                break
    return problems


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
    problems.extend(import_self_sufficiency_problems(base))
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
