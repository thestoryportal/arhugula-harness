#!/usr/bin/env python3
"""Spec §8.1 verification manifest as data + the umbrella runners (spec-he-loop-lanes).

`just lanes-verify` runs every row. `just lanes-phase0-check` runs rows tagged `phase0`
and treats a skip as a failure (C-HE-13 §1: an implicit precondition is not a gate).
`just mutation-probe-coverage-check` asserts every row marked mutation-probe has a PINNED
probe result in `.harness/mutation-probe-log.jsonl` (the run log `tools/mutation_probe.py`
appends on every exit). Only the three named environment skip reasons are legal; "slow" is
never one. Rows are appended by the unit that lands each artifact; keep them in §8.1 order.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROBE_LOG = REPO / ".harness" / "mutation-probe-log.jsonl"
TAGS = ("phase0", "phase1", "measurement", "layer2", "env", "operator-gated")
ALLOWED_SKIP_REASONS = ("docker-daemon-absent", "provider-login-absent", "gh-auth-absent")
KINDS = ("pytest", "shell", "just", "live")
_SKIP_RE = re.compile(r"^SKIPPED \[\d+\] [^:]+:\d+: (.+)$", re.M)


@dataclass(frozen=True)
class Row:
    contract: str
    artifact: str  # pytest:<nodeid> | shell:<path> | just:<recipe> | live:<desc>
    tag: str
    runs_in: str
    mutation_probe: bool
    skip_reasons: tuple[str, ...] = ()
    depends: str = ""


@dataclass
class Result:
    row: Row
    status: str  # pass | fail | skip | live
    reason: str = ""


#: Rows are appended by the unit that lands each artifact. Keep in §8.1 order.
MANIFEST: list[Row] = [
    # C-HE-05 (U-HE-10)
    Row(
        "C-HE-05",
        "pytest:tools/test_arc_metrics.py::test_env_overrides",
        "phase0",
        "local + CI",
        False,
    ),
    # C-HE-09/10 (U-HE-09)
    Row("C-HE-09/10", "shell:tools/hooks/test_loop_lib.sh", "phase0", "local + CI", True),
    # C-HE-15/16/18 (U-HE-02/03/04); C-HE-17 (U-HE-06/07)
    Row("C-HE-15/16/18", "pytest:tools/test_review_wrapper.py", "phase0", "local + CI", True),
    Row(
        "C-HE-17",
        "pytest:tools/test_review_wrapper.py::test_failover_invoked_once_on_primary_unavailable_and_blocks",
        "phase0",
        "local + CI",
        False,
    ),
    Row("C-HE-17", "pytest:tools/test_agy_review.py", "phase0", "local + CI", False),
    # C-HE-19/20 (U-HE-08)
    Row(
        "C-HE-19/20",
        "pytest:tools/test_arc_metrics.py::test_ci_state_cancelled_incomplete",
        "phase0",
        "local + CI",
        True,
    ),
    # C-HE-23–26 (U-HE-01 / U-HE-11 / U-HE-12 / U-HE-13)
    Row("C-HE-23–26", "pytest:tools/test_finding_record.py", "phase0", "local + CI", True),
    Row(
        "C-HE-23–26",
        "pytest:tools/test_arc_metrics.py::test_arc_row_schema_has_c_he_25_fields",
        "phase0",
        "local + CI",
        False,
    ),
    Row(
        "C-HE-23–26",
        "pytest:tools/test_arc_metrics.py::test_arc_type_at_open",
        "phase0",
        "local + CI",
        True,
    ),
    Row("C-HE-23", "pytest:tools/test_merge_gate_log.py", "phase0", "local + CI", True),
    Row("C-HE-23", "just:merge-gate-log-check", "phase0", "local + CI", False),
    # §8.1 / §0.3 (U-HE-05)
    Row("§8.1", "pytest:tools/test_lanes_verify.py", "phase0", "local + CI", True),
    Row("§0.3", "just:mutation-probe-coverage-check", "phase0", "local + CI", False),
]


def _command(row: Row) -> list[str] | None:
    kind, _, target = row.artifact.partition(":")
    if "<" in target and ">" in target:
        # a placeholder argument (e.g. `just:lanes-pilot-report <run-id>`) is a LIVE row
        return None
    if kind == "pytest":
        return ["uv", "run", "pytest", "-q", "-rs", target]
    if kind == "shell":
        return ["bash", *target.split()]
    if kind == "just":
        return ["just", *target.split()]  # recipe + controlled args, tokenized
    return None  # live


def run_row(row: Row, *, runner=subprocess.run) -> Result:
    cmd = _command(row)
    if cmd is None:
        return Result(row, "live", "operator-gated live step; recorded in the plan evidence log")
    proc = runner(cmd, cwd=REPO, capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    skips = _SKIP_RE.findall(out)
    if proc.returncode != 0:
        return Result(row, "fail", out[-2000:])
    if skips:
        bad = [s.strip() for s in skips if s.strip() not in row.skip_reasons]
        if bad:
            return Result(row, "fail", f"skip with unlisted reason: {bad}")
        return Result(row, "skip", ";".join(s.strip() for s in skips))
    return Result(row, "pass")


def phase0_rows() -> list[Row]:
    return [r for r in MANIFEST if r.tag == "phase0"]


def phase0_verdict(results: list[Result]) -> int:
    """0 iff every phase0 row passed. A skip is NOT a pass here (C-HE-13 §1)."""
    return 0 if all(r.status == "pass" for r in results) else 1


_ANNOT = re.compile(r"^# mutation-probe: .*\n(?:@[^\n]*\n)*def (test_\w+)", re.M)


def _relative(token: str) -> str:
    """A logged path as REPO-relative text; a relative token is returned unchanged."""
    p = Path(token)
    if p.is_absolute():
        try:
            return str(p.relative_to(REPO))
        except ValueError:
            return token
    return token


def _pinned_nodeids(log_path: Path) -> set[str]:
    """Targets of PINNED probes (rc 0): for a pytest command the first non-flag token after
    `pytest` that names a `.py` path (a node id or a file), normalized REPO-relative and
    compared EXACTLY; for `bash <script>` the probed script itself. The command is split on
    whitespace as logged -- the log is written by the probe tool, not typed by hand."""
    if not log_path.exists():
        return set()
    out: set[str] = set()
    for line in log_path.read_text().splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e.get("rc") != 0:
            continue
        toks = str(e["test"]).split()
        if "pytest" in toks:
            rest = toks[toks.index("pytest") + 1 :]
            for tok in rest:
                if not tok.startswith("-") and ".py" in tok:
                    out.add(_relative(tok))
                    break
        elif toks[:1] == ["bash"] and len(toks) > 1:
            out.add(_relative(toks[1]))
    return out


def required_probes(row: Row) -> list[str]:
    """Every `# mutation-probe:` annotation the row's artifact carries -> its exact node id
    (substring matching would let one pinned test cover a whole file). A node-id artifact
    requires exactly itself; a shell artifact requires the script itself."""
    if not row.mutation_probe:
        return []
    kind, _, target = row.artifact.partition(":")
    if kind == "shell":
        return [target.split()[0]]
    if kind != "pytest":
        return [target]
    file_part, _, node = target.partition("::")
    if node:
        return [target]
    path = REPO / file_part
    if not path.exists():
        return [target]  # not yet landed: a gap until the file exists and its probes are pinned
    return [f"{file_part}::{name}" for name in _ANNOT.findall(path.read_text())]


def coverage_gaps(log_path: Path | None = None) -> list[tuple[Row, str]]:
    """`log_path` resolves to PROBE_LOG AT CALL TIME (never bound at def time) so a
    monkeypatched log is honoured and `main` never silently reads the tracked log in a test."""
    pinned = _pinned_nodeids(log_path or PROBE_LOG)
    gaps: list[tuple[Row, str]] = []
    for r in MANIFEST:
        for node in required_probes(r):
            if node not in pinned:
                gaps.append((r, node))
    return gaps


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    mode = args[0] if args else "verify"
    if mode not in ("verify", "phase0", "coverage"):
        print("usage: lanes_verify.py [verify|phase0|coverage]", file=sys.stderr)
        return 2
    if mode == "coverage":
        gaps = coverage_gaps()
        for row, node in gaps:
            print(f"UNPROBED {row.contract} {node}")
        print(f"mutation-probe coverage: {len(gaps)} unprobed annotation(s)")
        return 1 if gaps else 0
    rows = phase0_rows() if mode == "phase0" else MANIFEST
    results = [run_row(r) for r in rows]
    for r in results:
        tail = f" — {r.reason}" if r.reason else ""
        print(f"{r.status.upper():5} {r.row.contract:14} {r.row.artifact}{tail}")
    if mode == "phase0":
        return phase0_verdict(results)
    return 1 if any(r.status == "fail" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
