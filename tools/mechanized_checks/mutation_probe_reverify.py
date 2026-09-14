"""weak / false test witnesses (C-HE-31 §1, hybrid): re-VERIFY the mutation each
`# mutation-probe:` annotation in a changed test file names -- never re-read the annotation as
evidence. Mutation-probe-backed: minutes per annotation, never shipped as "low-risk" (§2).

The line range comes from `.harness/mutation-probe-log.jsonl`, which `tools/mutation_probe.py`
appends on every exit: that log is the one record of which lines an annotation's mutation
removes, so this check keeps no second map of it. A logged range is re-run only while its pin
still matches the bytes it measured (`lanes_verify._pin_is_live`): code that moved since the
probe is reported stale, never probed at numbers that now name other lines."""

from __future__ import annotations

import json
import shlex
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import lanes_verify as lv  # [LAW:one-source-of-truth] annotation grammar + pin liveness live there
import pin_scope

from .core import MechFinding, Subject

PROBE_LOG = ".harness/mutation-probe-log.jsonl"
Probe = Callable[[Path, str, str, str], tuple[int, str]]


class ProbeRestoreError(RuntimeError):
    """tools/mutation_probe.py exit 3: the probed file may not have been restored. Never a
    finding -- the tree itself may now be wrong, so the whole mech-check run stops here,
    advisory or blocking alike."""


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
    proc = subprocess.run(argv, cwd=repo, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def _probed(row: dict, node: str, target: str) -> bool:
    """The row is a probe of THIS annotation: one pytest target equal to the node, run against
    the annotated file."""
    toks = str(row.get("test", "")).split()
    targets = pin_scope.pytest_targets(toks) if "pytest" in toks else []
    same_file = lv._relative(str(row.get("file", ""))) == target
    return [lv._relative(t) for t in targets] == [node] and same_file


def logged_range(rows: Sequence[dict], node: str, target: str, root: Path) -> Pinned | Stale | None:
    """The annotation's latest PINNED (rc 0) probe, live or stale against the bytes at `root`;
    None when it was never pinned."""
    pinned = [r for r in rows if r.get("rc") == 0 and r.get("lines") and _probed(r, node, target)]
    if not pinned:
        return None
    last = pinned[-1]
    live = lv._pin_is_live(last, node, target, root=root)
    return Pinned(last["lines"]) if live else Stale(last["lines"])


class Check:
    check_id = "mutation_probe_reverify"
    kind = "hybrid"

    def __init__(self, probe: Probe = run_probe):
        self.probe = probe

    def run(self, subject: Subject) -> list[MechFinding]:
        log = subject.read(PROBE_LOG) or ""
        rows = [json.loads(line) for line in log.splitlines() if line.strip()]
        annotated = [
            (f"{rel}::{name}", target or lv.default_probe_target(rel))
            for rel, _text in subject.changed_texts(".py")
            if Path(rel).name.startswith("test_")
            for name, target in lv._annotations(subject.repo / rel)
        ]
        return [
            finding
            for node, target in annotated
            for finding in self._verify(
                subject.repo, node, target, logged_range(rows, node, target, subject.repo)
            )
        ]

    def _verify(
        self, repo: Path, node: str, target: str, logged: Pinned | Stale | None
    ) -> list[MechFinding]:
        if logged is None:
            return [
                MechFinding(
                    node,
                    f"annotation never probed: no pinned probe-log row names a range of {target}",
                    "each # mutation-probe: annotation names a mutation the probe tool has run",
                )
            ]
        if isinstance(logged, Stale):
            return [
                MechFinding(
                    node,
                    f"logged range {target}:{logged.lines} no longer pins the current bytes "
                    "(the code or the test changed since it was probed)",
                    "re-probe the annotation before its mutation is re-verified",
                )
            ]
        rc, output = self.probe(repo, target, logged.lines, node)
        if rc == 3:
            raise ProbeRestoreError(
                f"{node}: the probe of {target}:{logged.lines} could not verify its restore -- "
                f"the file may still be mutated; stop and inspect it:\n{output[-2000:]}"
            )
        last = (output.strip().splitlines() or [""])[-1][:200]
        outcomes = {
            0: [],
            1: [
                MechFinding(
                    node,
                    f"annotation is FALSE: test stayed green with {target}:{logged.lines} removed",
                    "the named mutation turns the test red",
                    "hard",
                )
            ],
        }
        indeterminate = [
            MechFinding(
                node,
                f"probe indeterminate (exit {rc}) on {target}:{logged.lines}: {last}",
                "the probe returns pinned (0) or failed (1)",
            )
        ]
        return outcomes.get(rc, indeterminate)
