#!/usr/bin/env python3
"""Deterministic Codex context guard for arhugula-v2.

This is the Codex-side anti-rot instrument. It materializes current repository
state from git, roadmap, and dashboard files so Codex does not rely on memory for
load-bearing workflow claims.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

DESIGN_RE = re.compile(
    r"^(design-substrate/|\.harness/class_[12]_fork_|.*Spec_[A-Za-z_]+_v\d|"
    r".*Implementation_Plan_[A-Za-z_]+_v\d|.*ADR-[FD]\d)"
)
IMPL_RE = re.compile(r"^(harness-[a-z]+/(src|tests)/|tests/)")
CITE_RE = re.compile(r"^(harness-[a-z]+/src/|harness-[a-z]+/tests/|tools/semantic_overlay/)")
DASHBOARD_SOURCES = {
    ".harness/roadmap_status.md",
    ".harness/substitutions.yaml",
    "Project_Roadmap_v1.md",
    "tools/dashboard/generate.py",
    "tools/dashboard/README.md",
    ".github/workflows/dashboard-deploy.yml",
}
TRACKING_SURFACES = {
    ".harness/roadmap_status.md",
    "Project_Roadmap_v1.md",
    "tools/dashboard/roadmap.html",
    ".harness/substitutions.yaml",
}


@dataclass(frozen=True)
class DashboardState:
    hash: str
    git_head: str
    last_refreshed: str


@dataclass(frozen=True)
class GuardState:
    root: Path
    cwd: Path
    branch: str
    default_branch: str
    head8: str
    git_dir: str
    is_linked_worktree: bool
    status_entries: list[str]
    changed_files: list[str]
    dashboard: DashboardState
    computed_hash: str
    open_prs: str
    fork_doc_count: int
    latest_retirement_batch: str
    lag_expected: bool
    dashboard_snapshot_current: bool | None


@dataclass(frozen=True)
class Finding:
    severity: str  # hard | warn | info
    code: str
    message: str


def _run(args: list[str], *, cwd: Path, timeout: int = 20) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return subprocess.CompletedProcess(args=args, returncode=127, stdout="", stderr=str(exc))


def _out(args: list[str], *, cwd: Path, timeout: int = 20) -> str:
    proc = _run(args, cwd=cwd, timeout=timeout)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def repo_root(start: Path) -> Path:
    out = _out(["git", "rev-parse", "--show-toplevel"], cwd=start)
    return Path(out).resolve() if out else start.resolve()


def _default_branch(root: Path) -> str:
    out = _out(["git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"], cwd=root)
    return out.removeprefix("origin/") if out else "main"


def _dashboard(root: Path) -> DashboardState:
    path = root / ".harness" / "roadmap_status.md"
    try:
        md = path.read_text(encoding="utf-8")
    except OSError:
        return DashboardState(hash="", git_head="", last_refreshed="")

    def field(name: str, pattern: str) -> str:
        m = re.search(pattern, md)
        return m.group(1).strip() if m else ""

    return DashboardState(
        hash=field(
            "workspace_state_hash",
            r"\|\s*`workspace_state_hash`\s*\|\s*`?([a-f0-9]{12})`?",
        ),
        git_head=field("git_head", r"\|\s*`git_head`\s*\|\s*`?([a-f0-9]{8,40})"),
        last_refreshed=field("last_refreshed", r"\|\s*`last_refreshed`\s*\|\s*([^|]+?)\s*\|"),
    )


def _status_entries(root: Path) -> list[str]:
    out = _out(["git", "status", "--short"], cwd=root)
    return [line for line in out.splitlines() if line.strip()]


def _changed_files(root: Path) -> list[str]:
    files: set[str] = set()
    for args in (
        ["git", "diff", "--name-only"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        out = _out(args, cwd=root)
        files.update(line.strip() for line in out.splitlines() if line.strip())
    return sorted(files)


def _open_prs(root: Path) -> str:
    out = _out(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--json",
            "number,headRefName",
            "--jq",
            '. | sort_by(.number) | map("\\(.number):\\(.headRefName)") | join(",")',
        ],
        cwd=root,
        timeout=15,
    )
    return out


def _fork_doc_count(root: Path) -> int:
    harness = root / ".harness"
    if not harness.is_dir():
        return 0
    return len(
        list(harness.glob("class_1_fork_*.md")) + list(harness.glob("class_2_fork_*.md"))
    )


def _latest_retirement_batch(root: Path) -> str:
    harness = root / ".harness"
    if not harness.is_dir():
        return ""
    files = sorted(
        harness.glob("phase-7d-retirement-events-batch-*.md"),
        key=lambda p: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", p.name)],
    )
    return files[-1].relative_to(root).as_posix() if files else ""


def state_hash(head8: str, prs: str, forks: int, batch: str) -> str:
    raw = f"{head8}|{prs}|{forks}|{batch}".encode()
    return hashlib.sha256(raw).hexdigest()[:12]


def _lag_expected(root: Path) -> bool:
    title = _out(["git", "log", "-1", "--format=%s"], cwd=root)
    if not title.startswith("ops: roadmap status refresh "):
        return False
    changed = _out(["git", "show", "--name-only", "--pretty=format:", "HEAD"], cwd=root)
    files = sorted(line.strip() for line in changed.splitlines() if line.strip())
    return files == [".harness/roadmap_status.md"]


def _dashboard_snapshot_current(root: Path) -> bool | None:
    snapshot = root / "tools" / "dashboard" / "roadmap.html"
    generator = root / "tools" / "dashboard" / "generate.py"
    if not snapshot.exists() or not generator.exists():
        return None
    # Cheap short-circuit: if none of the source files changed in this worktree,
    # do not make closeout depend on a heavy HTML regeneration.
    if not (set(_changed_files(root)) & DASHBOARD_SOURCES):
        return True
    with tempfile.TemporaryDirectory(prefix="codex-dashboard-") as td:
        out = Path(td) / "roadmap.html"
        proc = _run(
            [sys.executable, "tools/dashboard/generate.py", "--root", ".", "--out", str(out)],
            cwd=root,
            timeout=60,
        )
        if proc.returncode != 0 or not out.exists():
            return None
        return snapshot.read_bytes() == out.read_bytes()


def derive(root: Path | None = None) -> GuardState:
    root = repo_root(root or Path.cwd())
    head8 = _out(["git", "rev-parse", "--short=8", "HEAD"], cwd=root)
    git_dir = _out(["git", "rev-parse", "--git-dir"], cwd=root)
    branch = _out(["git", "symbolic-ref", "--quiet", "--short", "HEAD"], cwd=root) or "DETACHED"
    default_branch = _default_branch(root)
    prs = _open_prs(root)
    forks = _fork_doc_count(root)
    batch = _latest_retirement_batch(root)
    dashboard = _dashboard(root)
    return GuardState(
        root=root,
        cwd=Path.cwd().resolve(),
        branch=branch,
        default_branch=default_branch,
        head8=head8,
        git_dir=git_dir,
        is_linked_worktree=".git/worktrees/" in git_dir or git_dir.startswith("../.git/worktrees/"),
        status_entries=_status_entries(root),
        changed_files=_changed_files(root),
        dashboard=dashboard,
        computed_hash=state_hash(head8, prs, forks, batch),
        open_prs=prs,
        fork_doc_count=forks,
        latest_retirement_batch=batch,
        lag_expected=_lag_expected(root),
        dashboard_snapshot_current=_dashboard_snapshot_current(root),
    )


def _has_design_impl_mix(files: list[str]) -> bool:
    return any(DESIGN_RE.search(f) for f in files) and any(IMPL_RE.search(f) for f in files)


def _has_cite_bearing_changes(files: list[str]) -> bool:
    return any(CITE_RE.search(f) for f in files)


def _has_dashboard_source_changes(files: list[str]) -> bool:
    return bool(
        set(files) & DASHBOARD_SOURCES
        or any(f.startswith(".harness/phase-7d-retirement-events-batch-") for f in files)
        or any(re.match(r"harness-[^/]+/CLAUDE\.md$", f) for f in files)
    )


def _has_tracking_changes(files: list[str]) -> bool:
    return bool(
        set(files) & TRACKING_SURFACES
        or any(f.startswith(".harness/phase-7d-") for f in files)
    )


def validate(
    state: GuardState, *, mode: str, allow_dashboard_drift: bool = False
) -> list[Finding]:
    findings: list[Finding] = []

    if state.status_entries and not state.is_linked_worktree:
        findings.append(
            Finding(
                "hard",
                "ROOT_CHECKOUT_EDIT",
                "Tracked/untracked edits exist in the root checkout. "
                "All edits must occur in a linked worktree.",
            )
        )

    if _has_design_impl_mix(state.changed_files):
        findings.append(
            Finding(
                "hard",
                "DESIGN_IMPL_MIX",
                "Changed files mix design/spec/plan/fork-doc surfaces "
                "with implementation/test surfaces.",
            )
        )

    if state.computed_hash != state.dashboard.hash:
        if allow_dashboard_drift:
            findings.append(
                Finding(
                    "warn",
                    "ROADMAP_DASHBOARD_DRIFT_ALLOWED",
                    "Dashboard hash differs, but the caller explicitly allowed drift. "
                    "Use only for CI runtime smoke during the post-merge refresh window.",
                )
            )
        elif state.branch == state.default_branch and not state.lag_expected:
            findings.append(
                Finding(
                    "hard",
                    "ROADMAP_DASHBOARD_DRIFT",
                    f"Dashboard hash {state.dashboard.hash or '<missing>'} "
                    f"does not match computed {state.computed_hash}.",
                )
            )
        else:
            findings.append(
                Finding(
                "warn",
                "ROADMAP_DASHBOARD_BRANCH_DIVERGED",
                "Dashboard hash differs from this branch; this is expected "
                "in feature worktrees but must be reconciled after merge.",
            )
        )

    if mode in {"closeout", "check"} and _has_cite_bearing_changes(state.changed_files):
        findings.append(
            Finding(
                "warn",
                "OVERLAY_CHECK_REQUIRED",
                "Cite-bearing source/test files changed. Run and report "
                "`just overlay-check` unless the PR is docs-only.",
            )
        )

    if mode in {"closeout", "check"} and _has_dashboard_source_changes(state.changed_files):
        if state.dashboard_snapshot_current is False:
            findings.append(
                Finding(
                    "hard",
                    "DASHBOARD_SNAPSHOT_STALE",
                    "`tools/dashboard/roadmap.html` does not match regenerated dashboard output.",
                )
            )
        elif state.dashboard_snapshot_current is None:
            findings.append(
                Finding(
                    "warn",
                    "DASHBOARD_SNAPSHOT_UNCHECKED",
                    "Dashboard sources changed, but snapshot comparison could not run.",
                )
            )

    if mode in {"closeout", "check"} and state.changed_files and not _has_tracking_changes(
        state.changed_files
    ):
        findings.append(
            Finding(
                "warn",
                "TRACKING_SURFACES_REVIEW_REQUIRED",
                "No roadmap/status/ledger tracking surface changed. "
                "Confirm this arc truly needs no tracking update.",
            )
        )

    return findings


def _fmt_findings(findings: list[Finding]) -> str:
    if not findings:
        return "Findings: none"
    lines = ["Findings:"]
    for f in findings:
        lines.append(f"- {f.severity.upper()} {f.code}: {f.message}")
    return "\n".join(lines)


def _text_report(state: GuardState, findings: list[Finding]) -> str:
    changed = "\n".join(f"  - {f}" for f in state.changed_files) or "  <none>"
    status = "\n".join(f"  {s}" for s in state.status_entries) or "  <clean>"
    return "\n".join(
        [
            "Codex context guard",
            f"root: {state.root}",
            f"cwd: {state.cwd}",
            f"branch: {state.branch} (default: {state.default_branch})",
            f"head: {state.head8}",
            f"linked_worktree: {state.is_linked_worktree} (git_dir={state.git_dir})",
            f"dashboard_hash: {state.dashboard.hash or '<missing>'}",
            f"computed_hash: {state.computed_hash}",
            f"dashboard_git_head: {state.dashboard.git_head or '<missing>'}",
            f"latest_retirement_batch: {state.latest_retirement_batch or '<none>'}",
            f"open_fork_doc_count: {state.fork_doc_count}",
            f"dashboard_snapshot_current: {state.dashboard_snapshot_current}",
            "git status:",
            status,
            "changed files:",
            changed,
            _fmt_findings(findings),
            "Required closeout reminders:",
            "- Update roadmap/status/dashboard/ledger surfaces when the arc changes state.",
            "- Run overlay-query/overlay-check for formal cite or CXA seam claims.",
            "- Report exact verification commands and skipped checks before claiming completion.",
        ]
    )


def _json_report(state: GuardState, findings: list[Finding]) -> str:
    return json.dumps(
        {
            "root": str(state.root),
            "cwd": str(state.cwd),
            "branch": state.branch,
            "default_branch": state.default_branch,
            "head8": state.head8,
            "is_linked_worktree": state.is_linked_worktree,
            "status_entries": state.status_entries,
            "changed_files": state.changed_files,
            "dashboard": state.dashboard.__dict__,
            "computed_hash": state.computed_hash,
            "open_prs": state.open_prs,
            "fork_doc_count": state.fork_doc_count,
            "latest_retirement_batch": state.latest_retirement_batch,
            "lag_expected": state.lag_expected,
            "dashboard_snapshot_current": state.dashboard_snapshot_current,
            "findings": [f.__dict__ for f in findings],
        },
        indent=2,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Codex deterministic context guard.")
    parser.add_argument("mode", choices=["preflight", "closeout", "check"])
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument(
        "--allow-dashboard-drift",
        action="store_true",
        help="downgrade dashboard hash drift to a warning; intended only for CI smoke",
    )
    args = parser.parse_args(argv)

    state = derive()
    findings = validate(
        state,
        mode=args.mode,
        allow_dashboard_drift=args.allow_dashboard_drift,
    )
    print(_json_report(state, findings) if args.json else _text_report(state, findings))
    return 1 if any(f.severity == "hard" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
