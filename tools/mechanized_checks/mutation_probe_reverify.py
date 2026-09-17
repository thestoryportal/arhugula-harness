"""weak / false test witnesses (C-HE-31 §1, hybrid): re-VERIFY the mutation each
`# mutation-probe:` annotation in a changed test file names -- never re-read the annotation as
evidence. Mutation-probe-backed: minutes per annotation, never shipped as "low-risk" (§2).

The line range comes from `.harness/mutation-probe-log.jsonl`, which `tools/mutation_probe.py`
appends on every exit: that log is the one record of which lines an annotation's mutation
removes, so this check keeps no second map of it. An annotation in the red-first
`<path>:<lines>` form matches only log rows for the lines it names, so two annotations stacked on
one test each verify their own mutation; a prose-form annotation names no lines and takes the
latest pinned row for its test and file (two prose annotations on one test and file cannot be
told apart -- a named residual). A logged range is re-run only while the probed file and its
test still digest to the row's `target_sha` and `test_sha` -- the exact bytes whose line numbers
it recorded, and the annotation that names them; a change to either since the probe is reported
stale, never probed at numbers that may now name other lines."""

from __future__ import annotations

import json
import re
import shlex
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import lanes_verify as lv  # [LAW:one-source-of-truth] the annotation grammar lives there
import pin_scope

from .core import MechFinding, Subject, subject_env

PROBE_LOG = ".harness/mutation-probe-log.jsonl"
Probe = Callable[[Path, str, str, str], tuple[int, str]]
Span = tuple[int, int]
_LINES = re.compile(r"(\d+)(?:-(\d+))?\b")


class ProbeRestoreError(RuntimeError):
    """tools/mutation_probe.py ended without a verdict it vouches for: exit 3 (restore unverified),
    a signal (a negative returncode), or any other exit outside 0/1/2. SIGKILL leaves the file
    mutated until a later probe reconciles it. Never a finding -- the tree itself may now be
    wrong, so the whole mech-check run stops here, advisory or blocking alike."""


@dataclass(frozen=True)
class Annotation:
    node: str
    target: str
    lines: Span | None  # None: a prose-form annotation, which names no lines


@dataclass(frozen=True)
class Pinned:
    lines: str


@dataclass(frozen=True)
class Stale:
    lines: str


def run_probe(repo: Path, file: str, lines: str, node: str) -> tuple[int, str]:
    """tools/mutation_probe.py exit: 0 pinned, 1 PROBE FAILED, 2 refused, 3 restore failure. The
    probe tool runs `--test` through a shell, so the filename-derived node is quoted here."""
    argv = [
        "uv",
        "run",
        "python",
        "tools/mutation_probe.py",
        "--file",
        file,
        "--lines",
        lines,
        "--test",
        f"uv run pytest {shlex.quote(node)} -q",
    ]
    proc = subprocess.run(argv, cwd=repo, env=subject_env(), capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def _span(text: str) -> Span | None:
    """`A-B` or `A` -> (A, B); the probe tool accepts both spellings of one range."""
    m = _LINES.match(text)
    return (int(m[1]), int(m[2] or m[1])) if m else None


def annotations(rel: str, text: str) -> list[Annotation]:
    """Every `# mutation-probe:` annotation in one test file, with the lines it names."""
    out: list[Annotation] = []
    for m in lv._ANNOT.finditer(text):
        desc = m.group("desc").strip()
        named = lv._DESC_TARGET.match(desc)
        path = named.group("path") if named else None
        target = m.group("target") or path or lv.default_probe_target(rel)
        lines = _span(desc[named.end() - 1 :]) if named else None
        out.append(Annotation(f"{rel}::{m.group('name')}", target, lines))
    return out


def _probed(row: dict, node: str, target: str) -> bool:
    """The row is a probe of THIS annotation: one pytest target equal to the node, run against
    the annotated file."""
    toks = str(row.get("test", "")).split()
    targets = pin_scope.pytest_targets(toks) if "pytest" in toks else []
    same_file = lv._relative(str(row.get("file", ""))) == target
    return [lv._relative(t) for t in targets] == [node] and same_file


def _digest(path: Path) -> str | None:
    return pin_scope.digest16(path.read_bytes()) if path.is_file() else None


def logged_range(rows: Sequence[dict], a: Annotation, root: Path) -> Pinned | Stale | None:
    """The annotation's latest PINNED (rc 0) probe, live or stale against the bytes at `root`;
    None when it was never pinned."""
    pinned = [
        r
        for r in rows
        if r.get("rc") == 0 and r.get("lines") and _probed(r, a.node, a.target)
        if a.lines is None or _span(str(r["lines"])) == a.lines
    ]
    if not pinned:
        return None
    last = pinned[-1]
    target_sha, test_sha = last.get("target_sha"), last.get("test_sha")
    # the range names these lines only in the exact bytes the probe measured -- the probed file
    # AND the test, whose annotation says which lines its mutation removes
    test_rel = a.node.split("::", 1)[0]
    live = (
        bool(target_sha and test_sha)
        and _digest(root / a.target) == target_sha
        and _digest(root / test_rel) == test_sha
    )
    return Pinned(last["lines"]) if live else Stale(last["lines"])


class Check:
    check_id = "mutation_probe_reverify"
    kind = "hybrid"
    replayable = False  # runs subject tests through the subject's own probe script

    def __init__(self, probe: Probe = run_probe):
        self.probe = probe

    def run(self, subject: Subject) -> list[MechFinding]:
        log = subject.read(PROBE_LOG) or ""
        rows = [json.loads(line) for line in log.splitlines() if line.strip()]
        return [
            finding
            for rel, text in self._subjects(subject)
            for a in annotations(rel, text)
            for finding in self._verify(subject.repo, a, logged_range(rows, a, subject.repo))
        ]

    def _subjects(self, subject: Subject) -> list[tuple[str, str]]:
        """The annotated test files this run must re-verify: every test file whose own text
        changed, PLUS every test file an annotation of which names a changed target.

        Scanning only changed tests left the asymmetric case uninspected -- a probed SOURCE
        file changes while its annotated test does not, so the pin's target digest goes
        stale and nothing looks at it, letting a blocking gate pass (codex r11 P2). The
        universe scan is bounded to `test_*.py`."""
        changed = set(subject.changed)
        found: list[tuple[str, str]] = []
        for rel in subject.universe:
            if not (rel.endswith(".py") and Path(rel).name.startswith("test_")):
                continue
            text = subject.read(rel)
            if text is None:
                continue
            due = rel in changed
            due = due or any(a.target in changed for a in annotations(rel, text))
            if due:
                found.append((rel, text))
        return found

    def _verify(
        self, repo: Path, a: Annotation, logged: Pinned | Stale | None
    ) -> list[MechFinding]:
        # mutation_probe.py and lanes_verify.py both split the logged command on whitespace, so a
        # node that needs shell quoting has no logged evidence they (or this check) can match
        if shlex.quote(a.node) != a.node:
            return [
                MechFinding(
                    a.node,
                    "test node needs shell quoting, which the probe log's whitespace-split "
                    "command cannot carry -- it can be neither matched nor re-verified",
                    "a shell-safe test path and name (letters, digits, @%+=:,./-_)",
                )
            ]
        if logged is None:
            named = f":{a.lines[0]}-{a.lines[1]}" if a.lines else ""
            return [
                MechFinding(
                    a.node,
                    f"annotation never probed: no pinned probe-log row for {a.target}{named}",
                    "each # mutation-probe: annotation names a mutation the probe tool has run",
                )
            ]
        if isinstance(logged, Stale):
            return [
                MechFinding(
                    a.node,
                    f"logged range {a.target}:{logged.lines} no longer pins the current bytes "
                    "(the probed file or its test changed since the probe ran)",
                    "re-probe the annotation before its mutation is re-verified",
                )
            ]
        rc, output = self.probe(repo, a.target, logged.lines, a.node)
        last = (output.strip().splitlines() or [""])[-1][:200]
        verdicts = {
            0: [],
            1: [
                MechFinding(
                    a.node,
                    "annotation is FALSE: test stayed green with "
                    f"{a.target}:{logged.lines} removed",
                    "the named mutation turns the test red",
                    "hard",
                )
            ],
            # the probe tool refused or found the run indeterminate, and restored the file itself
            2: [
                MechFinding(
                    a.node,
                    f"probe indeterminate (exit 2) on {a.target}:{logged.lines}: {last}",
                    "the probe returns pinned (0) or failed (1)",
                )
            ],
        }
        if rc not in verdicts:
            raise ProbeRestoreError(
                f"{a.node}: the probe of {a.target}:{logged.lines} exited {rc} without a verdict "
                f"-- the file may still be mutated; stop and inspect it:\n{output[-2000:]}"
            )
        return verdicts[rc]
