"""weak / false test witnesses (C-HE-31 §1, hybrid): re-VERIFY the mutation each
`# mutation-probe:` annotation in a changed test file names -- never re-read the annotation as
evidence. Mutation-probe-backed: minutes per annotation, never shipped as "low-risk" (§2).

The line range comes from `.harness/mutation-probe-log.jsonl`, which `tools/mutation_probe.py`
appends on every exit: that log is the one record of which lines an annotation's mutation
removes, so this check keeps no second map of it."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from pathlib import Path

import lanes_verify as lv  # [LAW:one-source-of-truth] the annotation grammar lives there
import pin_scope

from .core import MechFinding, Subject

PROBE_LOG = ".harness/mutation-probe-log.jsonl"
Probe = Callable[[Path, str, str, str], tuple[int, str]]


class ProbeRestoreError(RuntimeError):
    """tools/mutation_probe.py exit 3: the probed file may not have been restored. Never a
    finding -- the tree itself may now be wrong, so the whole mech-check run stops here,
    advisory or blocking alike."""


def run_probe(repo: Path, file: str, lines: str, node: str) -> tuple[int, str]:
    """tools/mutation_probe.py exit: 0 pinned, 1 PROBE FAILED, 2 refused, 3 restore failure."""
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
        f"uv run pytest {node} -q",
    ]
    proc = subprocess.run(argv, cwd=repo, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def _logged_ranges(log_text: str) -> dict[tuple[str, str], str]:
    """`(node id, probed file) -> lines` of the latest logged probe per pair (later rows win).
    A row naming no line range, or several pytest targets, binds nothing."""
    rows = [json.loads(line) for line in log_text.splitlines() if line.strip()]
    pytest_rows = [(r, str(r["test"]).split()) for r in rows if r.get("lines")]
    return {
        (lv._relative(targets[0]), lv._relative(str(r.get("file", "")))): r["lines"]
        for r, toks in pytest_rows
        if "pytest" in toks
        for targets in [pin_scope.pytest_targets(toks)]
        if len(targets) == 1
    }


class Check:
    check_id = "mutation_probe_reverify"
    kind = "hybrid"

    def __init__(self, probe: Probe = run_probe):
        self.probe = probe

    def run(self, subject: Subject) -> list[MechFinding]:
        ranges = _logged_ranges(subject.read(PROBE_LOG) or "")
        annotated = [
            (f"{rel}::{name}", target or lv.default_probe_target(rel))
            for rel, _text in subject.changed_texts(".py")
            if Path(rel).name.startswith("test_")
            for name, target in lv._annotations(subject.repo / rel)
        ]
        return [
            finding
            for node, target in annotated
            for finding in self._verify(subject.repo, node, target, ranges.get((node, target)))
        ]

    def _verify(self, repo: Path, node: str, target: str, lines: str | None) -> list[MechFinding]:
        if lines is None:
            return [
                MechFinding(
                    node,
                    f"annotation never probed: no probe-log row names a line range of {target}",
                    "each # mutation-probe: annotation names a mutation the probe tool has run",
                )
            ]
        rc, output = self.probe(repo, target, lines, node)
        if rc == 3:
            raise ProbeRestoreError(
                f"{node}: the probe of {target}:{lines} could not verify its restore -- the file "
                f"may still be mutated; stop and inspect it:\n{output[-2000:]}"
            )
        last = (output.strip().splitlines() or [""])[-1][:200]
        outcomes = {
            0: [],
            1: [
                MechFinding(
                    node,
                    f"annotation is FALSE: test stayed green with {target}:{lines} removed",
                    "the named mutation turns the test red",
                    "hard",
                )
            ],
        }
        indeterminate = [
            MechFinding(
                node,
                f"probe indeterminate (exit {rc}) on {target}:{lines}: {last}",
                "the probe returns pinned (0) or failed (1)",
            )
        ]
        return outcomes.get(rc, indeterminate)
