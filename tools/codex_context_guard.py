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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

DESIGN_RE = re.compile(
    r"^(design-substrate/|\.harness/class_[123]_|\.harness/architect_recommendation_|"
    r".*Spec_[A-Za-z_]+_v\d|.*Implementation_Plan_[A-Za-z_]+_v\d|.*ADR-[FD]\d)"
)
IMPL_RE = re.compile(
    r"^(harness-[a-z]+/(src|tests)/|tests/|tools/|\.codex/hooks/|\.github/workflows/|"
    r"justfile$)"
)
CITE_RE = re.compile(r"^(harness-[a-z]+/src/|harness-[a-z]+/tests/|tools/semantic_overlay/)")
# A clearance marker (CLAUDE.md §4.5) records a design-substrate version operationally
# accepted for Phase-7 consumption — the signal that a design+impl PR is a RATIFIED
# bundled-absorption arc (§11.4), not silent absorption. Its presence is what the
# X-AL-3 guard (§4.4) treats as legitimate back-flow; mirror that here so DESIGN_IMPL_MIX
# stops flagging the bundled-absorption pattern the R-FS-1 build program runs on.
CLEARANCE_MARKER_RE = re.compile(r"^\.harness/clearance/.+-cleared-.*\.md$")
DASHBOARD_SOURCES = {
    ".harness/roadmap_status.md",
    ".harness/substitutions.yaml",
    ".harness/arc-ledger.yaml",
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
DASHBOARD_SNAPSHOT = "tools/dashboard/roadmap.html"
DASHBOARD_MIX_EXEMPT_IMPL = {
    "tools/dashboard/generate.py",
    "tools/dashboard/README.md",
    "tools/dashboard/roadmap.html",
    "tools/test_dashboard_generate.py",
}
CHECKPOINT_DIR = Path(".harness/.checkpoints")
CHECKPOINT_FILE = "codex-context-latest.json"
CREDENTIAL_GATE_LEDGER = Path(".harness/codex_credential_gates.jsonl")
CODEX_LOOP_STATE = Path(".harness/codex_loop_state.json")
CODEX_LOOP_PRE_CLOSEOUT_GATES = (
    "preflight",
    "plan",
    "red",
    "implementation",
    "narrow_verify",
    "local_gate",
    "decorrelated_review",
)
CODEX_LOOP_CURRENT_WORKTREE_GATES = (
    "implementation",
    "narrow_verify",
    "local_gate",
    "decorrelated_review",
)
CREDENTIAL_TRACKING_SURFACES = {
    ".harness/roadmap_status.md",
    "Project_Roadmap_v1.md",
}
SECRET_VALUE_RE = re.compile(
    r"(?i)\b("
    r"ANTHROPIC_API_KEY|OPENAI_API_KEY|"
    r"[A-Z0-9_]*(?:SECRET|TOKEN|CREDENTIAL|PASSWORD|AUTH)[A-Z0-9_]*"
    r")=([^\s]+)"
)
DASHBOARD_JSON_LIVE_HEAD_RE = re.compile(rb'("live_head":\s*")[^"]*(")')
DASHBOARD_JSON_LIVE_ANCHOR_HEAD_RE = re.compile(rb'("live_anchor":\s*\{\s*"git_head":\s*")[^"]*(")')
DASHBOARD_JSON_LIVE_ANCHOR_HASH_RE = re.compile(rb'("live_anchor":\s*\{[^}]*"hash":\s*")[^"]*(")')
DASHBOARD_JSON_LIVE_ANCHOR_RECENT_PRS_RE = re.compile(
    rb'("live_anchor":\s*\{[^}]*"recent_prs":\s*)\[[^\]]*\]'
)
DASHBOARD_META_LIVE_HEAD_RE = re.compile(rb'(<meta name="dashboard-live-head" content=")[^"]*(")')
DASHBOARD_JSON_COMMIT_CADENCE_RE = re.compile(rb'("cadence":\s*)\[[^\]]*\](,\s*"pr_cadence")')


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
    open_prs_available: bool
    fork_doc_count: int
    latest_retirement_batch: str
    lag_expected: bool
    dashboard_snapshot_current: bool | None


@dataclass(frozen=True)
class Finding:
    severity: str  # hard | warn | info
    code: str
    message: str


@dataclass(frozen=True)
class Checkpoint:
    label: str
    fingerprint: str
    head8: str
    branch: str
    changed_files: list[str]
    status_entries: list[str]
    written_at: str


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


def _run_bytes(
    args: list[str], *, cwd: Path, timeout: int = 60
) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return subprocess.CompletedProcess(
            args=args,
            returncode=127,
            stdout=b"",
            stderr=str(exc).encode("utf-8", errors="replace"),
        )


def worktree_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    pathspec = ["--", ".", f":(exclude){CODEX_LOOP_STATE.as_posix()}"]

    def add(label: str, payload: bytes) -> None:
        digest.update(label.encode("utf-8"))
        digest.update(b"\0")
        digest.update(payload)
        digest.update(b"\0")

    for label, args in (
        ("status", ["git", "status", "--short", "--untracked-files=all", *pathspec]),
        ("diff", ["git", "diff", "--binary", "--no-ext-diff", *pathspec]),
        ("cached", ["git", "diff", "--cached", "--binary", "--no-ext-diff", *pathspec]),
    ):
        proc = _run_bytes(args, cwd=root)
        add(f"{label}:returncode", str(proc.returncode).encode("ascii"))
        add(f"{label}:stdout", proc.stdout)
        add(f"{label}:stderr", proc.stderr)

    proc = _run_bytes(
        ["git", "ls-files", "--others", "--exclude-standard", "-z", *pathspec], cwd=root
    )
    add("untracked:returncode", str(proc.returncode).encode("ascii"))
    add("untracked:stderr", proc.stderr)
    for rel_raw in sorted(part for part in proc.stdout.split(b"\0") if part):
        rel = rel_raw.decode("utf-8", errors="surrogateescape")
        add("untracked:path", rel_raw)
        try:
            add("untracked:sha256", hashlib.sha256((root / rel).read_bytes()).hexdigest().encode())
        except OSError as exc:
            add("untracked:error", str(exc).encode("utf-8", errors="replace"))
    return digest.hexdigest()[:16]


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


def _changed_files(root: Path, *, base_ref: str = "", head_ref: str = "") -> list[str]:
    if base_ref and head_ref:
        out = _out(["git", "diff", "--name-only", base_ref, head_ref], cwd=root)
        return sorted(line.strip() for line in out.splitlines() if line.strip())

    files: set[str] = set()
    for args in (
        ["git", "diff", "--name-only"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        out = _out(args, cwd=root)
        files.update(line.strip() for line in out.splitlines() if line.strip())
    return sorted(files)


def _branch_diff_files(root: Path, *, branch: str, default_branch: str) -> list[str]:
    if branch == default_branch or branch == "DETACHED":
        return []
    base_candidates = [default_branch, f"origin/{default_branch}"]
    for candidate in base_candidates:
        merge_base = _out(["git", "merge-base", candidate, "HEAD"], cwd=root)
        if merge_base:
            out = _out(["git", "diff", "--name-only", merge_base, "HEAD"], cwd=root)
            return sorted(line.strip() for line in out.splitlines() if line.strip())
    return []


def _open_prs(root: Path) -> tuple[str, bool]:
    proc = _run(
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
    return (proc.stdout.strip(), True) if proc.returncode == 0 else ("", False)


def _fork_doc_count(root: Path) -> int:
    harness = root / ".harness"
    if not harness.is_dir():
        return 0
    return len(list(harness.glob("class_1_fork_*.md")) + list(harness.glob("class_2_fork_*.md")))


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


def state_fingerprint(state: GuardState) -> str:
    payload = {
        "branch": state.branch,
        "changed_files": state.changed_files,
        "computed_hash": state.computed_hash,
        "dashboard_hash": state.dashboard.hash,
        "head8": state.head8,
        "status_entries": state.status_entries,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def checkpoint_path(root: Path) -> Path:
    return root / CHECKPOINT_DIR / CHECKPOINT_FILE


def load_checkpoint(root: Path) -> Checkpoint | None:
    path = checkpoint_path(root)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    try:
        return Checkpoint(
            label=str(raw["label"]),
            fingerprint=str(raw["fingerprint"]),
            head8=str(raw["head8"]),
            branch=str(raw["branch"]),
            changed_files=[str(f) for f in raw["changed_files"]],
            status_entries=[str(s) for s in raw["status_entries"]],
            written_at=str(raw["written_at"]),
        )
    except (KeyError, TypeError):
        return None


def write_checkpoint(state: GuardState, *, label: str, findings: list[Finding]) -> Path:
    path = checkpoint_path(state.root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "label": label,
        "written_at": datetime.now(timezone.utc).isoformat(),  # noqa: UP017 - /usr/bin/python3 is 3.9.
        "fingerprint": state_fingerprint(state),
        "root": str(state.root),
        "cwd": str(state.cwd),
        "branch": state.branch,
        "default_branch": state.default_branch,
        "head8": state.head8,
        "git_dir": state.git_dir,
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
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def redact_secret_values(value: str) -> str:
    return SECRET_VALUE_RE.sub(lambda m: f"{m.group(1)}=<redacted>", value)


def append_credential_gate(
    state: GuardState,
    *,
    unit: str,
    gate: str,
    forward_closed: str,
    resume: str,
    command: str = "",
) -> Path:
    required = {
        "unit": unit,
        "gate": gate,
        "forward_closed": forward_closed,
        "resume": resume,
    }
    missing = [name for name, value in required.items() if not value.strip()]
    if missing:
        raise ValueError("credential gate log requires: " + ", ".join(missing))

    path = state.root / CREDENTIAL_GATE_LEDGER
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "written_at": datetime.now(timezone.utc).isoformat(),  # noqa: UP017 - /usr/bin/python3 is 3.9.
        "unit": unit.strip(),
        "gate": redact_secret_values(gate.strip()),
        "forward_closed": redact_secret_values(forward_closed.strip()),
        "resume": redact_secret_values(resume.strip()),
        "command": redact_secret_values(command.strip()),
        "branch": state.branch,
        "head8": state.head8,
        "context_fingerprint": state_fingerprint(state),
        "status": "human_review_pending",
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True) + "\n")
    return path


def _lag_expected(root: Path) -> bool:
    title = _out(["git", "log", "-1", "--format=%s"], cwd=root)
    if not title.startswith("ops: roadmap status refresh "):
        return False
    changed = _out(["git", "show", "--name-only", "--pretty=format:", "HEAD"], cwd=root)
    files = sorted(line.strip() for line in changed.splitlines() if line.strip())
    return files in (
        [".harness/roadmap_status.md"],
        [".harness/roadmap_status.md", DASHBOARD_SNAPSHOT],
    )


def _dashboard_snapshot_current(
    root: Path, *, changed_files: list[str] | None = None
) -> bool | None:
    snapshot = root / "tools" / "dashboard" / "roadmap.html"
    generator = root / "tools" / "dashboard" / "generate.py"
    if not snapshot.exists() or not generator.exists():
        return None
    # Cheap short-circuit: if none of the source files changed in this worktree,
    # do not make closeout depend on a heavy HTML regeneration.
    files = changed_files if changed_files is not None else _changed_files(root)
    if not (set(files) & DASHBOARD_SOURCES):
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
        return _normalize_dashboard_snapshot(snapshot.read_bytes()) == (
            _normalize_dashboard_snapshot(out.read_bytes())
        )


def _normalize_dashboard_snapshot(raw: bytes) -> bytes:
    """Ignore volatile commit-derived instrumentation in dashboard snapshots."""
    raw = DASHBOARD_JSON_LIVE_HEAD_RE.sub(rb"\1<LIVE_HEAD>\2", raw, count=1)
    raw = DASHBOARD_JSON_LIVE_ANCHOR_HEAD_RE.sub(rb"\1<LIVE_HEAD>\2", raw, count=1)
    raw = DASHBOARD_JSON_LIVE_ANCHOR_HASH_RE.sub(rb"\1<LIVE_HASH>\2", raw, count=1)
    raw = DASHBOARD_JSON_LIVE_ANCHOR_RECENT_PRS_RE.sub(
        rb'\1[{"pr":"<RECENT>","date":"<RECENT>","note":"<RECENT>"}]', raw, count=1
    )
    raw = DASHBOARD_META_LIVE_HEAD_RE.sub(rb"\1<LIVE_HEAD>\2", raw, count=1)
    return DASHBOARD_JSON_COMMIT_CADENCE_RE.sub(rb'\1[{"date":"<CADENCE>","count":0}]\2', raw)


def derive(
    root: Path | None = None,
    *,
    base_ref: str = "",
    head_ref: str = "",
    include_branch_diff: bool = False,
) -> GuardState:
    root = repo_root(root or Path.cwd())
    head8 = _out(["git", "rev-parse", "--short=8", "HEAD"], cwd=root)
    git_dir = _out(["git", "rev-parse", "--git-dir"], cwd=root)
    branch = _out(["git", "symbolic-ref", "--quiet", "--short", "HEAD"], cwd=root) or "DETACHED"
    default_branch = _default_branch(root)
    prs, prs_available = _open_prs(root)
    forks = _fork_doc_count(root)
    batch = _latest_retirement_batch(root)
    dashboard = _dashboard(root)
    changed_files = _changed_files(root, base_ref=base_ref, head_ref=head_ref)
    if include_branch_diff and not (base_ref and head_ref):
        changed_files = sorted(
            set(changed_files)
            | set(_branch_diff_files(root, branch=branch, default_branch=default_branch))
        )
    return GuardState(
        root=root,
        cwd=Path.cwd().resolve(),
        branch=branch,
        default_branch=default_branch,
        head8=head8,
        git_dir=git_dir,
        is_linked_worktree=".git/worktrees/" in git_dir or git_dir.startswith("../.git/worktrees/"),
        status_entries=_status_entries(root),
        changed_files=changed_files,
        dashboard=dashboard,
        computed_hash=state_hash(head8, prs, forks, batch),
        open_prs=prs,
        open_prs_available=prs_available,
        fork_doc_count=forks,
        latest_retirement_batch=batch,
        lag_expected=_lag_expected(root),
        dashboard_snapshot_current=_dashboard_snapshot_current(root, changed_files=changed_files),
    )


def _has_design_impl_mix(files: list[str]) -> bool:
    # Legitimate bundled-absorption (CLAUDE.md §11.4): a design-substrate amendment
    # co-lands with its impl in one PR when a clearance marker (§4.5) records the
    # operationally-accepted consumption — the same back-flow signal the X-AL-3 guard
    # (§4.4) recognizes. Present → ratified bundle, not a silent mix. A silent mix
    # (design + impl, NO clearance marker) still hard-fails.
    #
    # Presence-based (ANY clearance marker exempts the PR) is INTENTIONAL: it mirrors
    # X-AL-3's own presence-based recognition so the two guards agree on what
    # "legitimate bundled-absorption" is. The residual an artifact-tie would close
    # (an UNRELATED marker riding a design+impl mix) matches X-AL-3's accepted
    # tolerance; tying the marker to the changed design file would make THIS guard
    # stricter than X-AL-3 (the same PR would pass one guard and fail the other) and
    # is brittle (slug / multi-artifact matching false-blocks legitimate arcs).
    # Tightening, if ever wanted, is a deliberate BOTH-guards policy change.
    if any(CLEARANCE_MARKER_RE.search(f) for f in files):
        return False
    impl_files = [f for f in files if f not in DASHBOARD_MIX_EXEMPT_IMPL]
    return any(DESIGN_RE.search(f) for f in files) and any(IMPL_RE.search(f) for f in impl_files)


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
        set(files) & TRACKING_SURFACES or any(f.startswith(".harness/phase-7d-") for f in files)
    )


def _has_credential_gate_ledger_change(files: list[str]) -> bool:
    return CREDENTIAL_GATE_LEDGER.as_posix() in files


def _has_credential_gate_tracking_change(files: list[str]) -> bool:
    return bool(set(files) & CREDENTIAL_TRACKING_SURFACES)


def _codex_loop_issues(state: GuardState) -> list[str]:
    path = state.root / CODEX_LOOP_STATE
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"loop state cannot be read: {exc}"]
    if not isinstance(raw, dict):
        return ["loop state must be a JSON object"]
    loop_state = cast("dict[str, Any]", raw)
    events = loop_state.get("events")
    if not isinstance(events, list):
        return ["loop state events must be a list"]
    latest: dict[str, tuple[int, dict[str, Any]]] = {}
    event_list = cast("list[Any]", events)
    for index, event_obj in enumerate(event_list):
        if not isinstance(event_obj, dict):
            continue
        event = cast("dict[str, Any]", event_obj)
        phase = event.get("phase")
        if isinstance(phase, str):
            latest[phase] = (index, event)
    missing = [phase for phase in CODEX_LOOP_PRE_CLOSEOUT_GATES if phase not in latest]
    issues: list[str] = []
    if missing:
        issues.append("missing pre-closeout gates: " + ", ".join(missing))
    state_branch = loop_state.get("branch")
    state_head8 = loop_state.get("head8")
    if state_branch != state.branch or state_head8 != state.head8:
        issues.append(
            "loop state recorded for "
            f"branch={state_branch or '<missing>'} head={state_head8 or '<missing>'}; "
            f"current branch={state.branch} head={state.head8}"
        )
    current_worktree = worktree_fingerprint(state.root)
    state_worktree = loop_state.get("worktree_fingerprint")
    if state_worktree != current_worktree:
        issues.append(
            "loop state recorded for "
            f"worktree={state_worktree or '<missing>'}; current worktree={current_worktree}"
        )
    positions = [
        (phase, latest[phase][0]) for phase in CODEX_LOOP_PRE_CLOSEOUT_GATES if phase in latest
    ]
    for offset, (phase, index) in enumerate(positions[1:], start=1):
        previous_phase, previous_index = positions[offset - 1]
        if previous_index > index:
            issues.append(
                f"gate order invalid: {previous_phase} recorded after {phase}; "
                + "required pre-closeout order is "
                + " -> ".join(CODEX_LOOP_PRE_CLOSEOUT_GATES)
            )
            break
    red = latest.get("red")
    if red is not None and red[1].get("status") != "failed":
        issues.append("red gate must record status=failed")
    for phase in CODEX_LOOP_PRE_CLOSEOUT_GATES:
        event = latest.get(phase)
        if event is None:
            continue
        event_payload = event[1]
        event_branch = event_payload.get("branch")
        event_head8 = event_payload.get("head8")
        if event_branch != state.branch or event_head8 != state.head8:
            issues.append(
                f"{phase} gate recorded for "
                f"branch={event_branch or '<missing>'} head={event_head8 or '<missing>'}; "
                f"current branch={state.branch} head={state.head8}"
            )
        event_worktree = event_payload.get("worktree_fingerprint")
        if phase in CODEX_LOOP_CURRENT_WORKTREE_GATES and event_worktree != current_worktree:
            issues.append(
                f"{phase} gate recorded for "
                f"worktree={event_worktree or '<missing>'}; current worktree={current_worktree}"
            )
        if phase == "red":
            continue
        if event_payload.get("status") != "passed":
            issues.append(f"{phase} gate must record status=passed")
    return issues


def validate(
    state: GuardState,
    *,
    mode: str,
    allow_dashboard_drift: bool = False,
    require_fresh_checkpoint: bool = False,
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

    if not state.open_prs_available:
        findings.append(
            Finding(
                "warn",
                "OPEN_PRS_UNAVAILABLE",
                "`gh pr list` was unavailable; computed context hash used an empty open-PR set.",
            )
        )

    if state.computed_hash != state.dashboard.hash:
        if state.branch == state.default_branch and not state.lag_expected:
            findings.append(
                Finding(
                    "hard",
                    "ROADMAP_DASHBOARD_DRIFT",
                    f"Dashboard hash {state.dashboard.hash or '<missing>'} "
                    f"does not match computed {state.computed_hash}.",
                )
            )
        elif state.lag_expected:
            findings.append(
                Finding(
                    "warn",
                    "ROADMAP_DASHBOARD_LAG_EXPECTED",
                    "Dashboard hash differs because HEAD is a roadmap-status-only refresh; "
                    "the next terminating refresh should reconcile the lag.",
                )
            )
        elif allow_dashboard_drift:
            findings.append(
                Finding(
                    "warn",
                    "ROADMAP_DASHBOARD_DRIFT_ALLOWED",
                    "Dashboard hash differs, but the caller explicitly allowed drift. "
                    "Use only for CI runtime smoke during the post-merge refresh window.",
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

    if (
        mode in {"closeout", "check"}
        and _has_credential_gate_ledger_change(state.changed_files)
        and not _has_credential_gate_tracking_change(state.changed_files)
    ):
        findings.append(
            Finding(
                "hard",
                "CREDENTIAL_GATE_TRACKING_REQUIRED",
                "Credential-gated work was logged, but no human-facing roadmap/status "
                "surface changed. Surface the pending gate before proceeding.",
            )
        )

    if mode in {"closeout", "check"}:
        loop_issues = _codex_loop_issues(state)
        if loop_issues:
            findings.append(
                Finding(
                    "hard",
                    "CODEX_LOOP_INCOMPLETE",
                    "Active Codex autonomous loop is not ready for closeout: "
                    + "; ".join(loop_issues),
                )
            )

    if (
        mode in {"closeout", "check"}
        and state.changed_files
        and not _has_tracking_changes(state.changed_files)
    ):
        findings.append(
            Finding(
                "warn",
                "TRACKING_SURFACES_REVIEW_REQUIRED",
                "No roadmap/status/ledger tracking surface changed. "
                "Confirm this arc truly needs no tracking update.",
            )
        )

    if require_fresh_checkpoint:
        checkpoint = load_checkpoint(state.root)
        current_fingerprint = state_fingerprint(state)
        if checkpoint is None:
            findings.append(
                Finding(
                    "hard",
                    "CONTEXT_CHECKPOINT_MISSING",
                    "No deterministic context checkpoint exists. Run "
                    "`just codex-checkpoint <label>` or the closeout recipe.",
                )
            )
        elif checkpoint.fingerprint != current_fingerprint:
            findings.append(
                Finding(
                    "hard",
                    "CONTEXT_CHECKPOINT_STALE",
                    "Latest context checkpoint does not match current HEAD/status/dashboard "
                    f"(checkpoint label={checkpoint.label}, written_at={checkpoint.written_at}).",
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
            f"context_fingerprint: {state_fingerprint(state)}",
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
            "context_fingerprint": state_fingerprint(state),
            "open_prs": state.open_prs,
            "open_prs_available": state.open_prs_available,
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
    parser.add_argument(
        "mode",
        choices=["preflight", "closeout", "check", "checkpoint", "credential-gate"],
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument(
        "--label",
        default="manual",
        help="checkpoint label when mode=checkpoint",
    )
    parser.add_argument(
        "--require-fresh-checkpoint",
        action="store_true",
        help="fail if the latest checkpoint does not match current HEAD/status/dashboard",
    )
    parser.add_argument(
        "--allow-dashboard-drift",
        action="store_true",
        help="downgrade non-default-branch dashboard hash drift to a warning",
    )
    parser.add_argument(
        "--base-ref",
        default="",
        help="base git ref for committed-range diff checks, typically the PR base SHA",
    )
    parser.add_argument(
        "--head-ref",
        default="",
        help="head git ref for committed-range diff checks, typically the PR head SHA",
    )
    parser.add_argument(
        "--include-branch-diff",
        action="store_true",
        help="include committed branch changes since the merge-base with the default branch",
    )
    parser.add_argument("--unit", default="", help="unit or roadmap id for mode=credential-gate")
    parser.add_argument(
        "--gate", default="", help="credential gate summary for mode=credential-gate"
    )
    parser.add_argument(
        "--forward-closed",
        default="",
        help="evidence that all non-credential forward actions are closed",
    )
    parser.add_argument(
        "--resume",
        default="",
        help="human-review resume instruction for mode=credential-gate",
    )
    parser.add_argument(
        "--command",
        default="",
        help="optional blocked command, secret values are redacted before logging",
    )
    args = parser.parse_args(argv)

    state = derive(
        base_ref=args.base_ref,
        head_ref=args.head_ref,
        include_branch_diff=args.include_branch_diff,
    )
    if args.mode == "credential-gate":
        try:
            path = append_credential_gate(
                state,
                unit=args.unit,
                gate=args.gate,
                forward_closed=args.forward_closed,
                resume=args.resume,
                command=args.command,
            )
        except ValueError as exc:
            print(f"credential_gate_error: {exc}", file=sys.stderr)
            return 2
        print(f"credential_gate_logged: {path}")
        return 0

    findings = validate(
        state,
        mode=args.mode,
        allow_dashboard_drift=args.allow_dashboard_drift,
        require_fresh_checkpoint=args.require_fresh_checkpoint,
    )
    print(_json_report(state, findings) if args.json else _text_report(state, findings))
    if args.mode in {"preflight", "checkpoint"}:
        path = write_checkpoint(
            state, label=args.label if args.mode == "checkpoint" else "preflight", findings=findings
        )
        print(f"checkpoint_written: {path}")
    return 1 if any(f.severity == "hard" for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
