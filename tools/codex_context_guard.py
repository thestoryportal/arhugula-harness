#!/usr/bin/env python3
"""Deterministic Codex context guard for arhugula-v2.

This is the Codex-side anti-rot instrument. It materializes current repository
state from git and roadmap files so Codex does not rely on memory for
load-bearing workflow claims.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import codex_loop

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
TRACKING_SURFACES = {
    ".harness/roadmap_status.md",
    "Project_Roadmap_v1.md",
    ".harness/substitutions.yaml",
}
TERMINATING_REFRESH_FILE_SETS = (frozenset({".harness/roadmap_status.md"}),)
CHECKPOINT_DIR = Path(".harness/.checkpoints")
CHECKPOINT_FILE = "codex-context-latest.json"
CREDENTIAL_GATE_LEDGER = Path(".harness/codex_credential_gates.jsonl")
CODEX_LOOP_STATE = Path(".harness/codex_loop_state.json")
CODEX_LOOP_PRE_CLOSEOUT_GATES = (
    "worktree_ready",
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
# NAME=VALUE-shaped secrets are only one carrier shape. A Bearer/Authorization
# header or a bare vendor-prefixed API key passed via `--command` has no
# `NAME=` prefix at all and previously slipped past SECRET_VALUE_RE straight
# into the non-gitignored, actively-committed credential-gate ledger.
BEARER_TOKEN_RE = re.compile(r"(?i)\b(bearer|authorization:\s*bearer)\s+(\S+)")
KNOWN_SECRET_PREFIX_RE = re.compile(
    r"\b(sk-ant-|sk-|ghp_|gho_|ghu_|ghs_|ghr_|glpat-|xox[baprs]-|AKIA)([A-Za-z0-9_-]{8,})"
)


@dataclass(frozen=True)
class RoadmapStatusState:
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
    roadmap_status: RoadmapStatusState
    computed_hash: str
    open_prs: str
    open_prs_available: bool
    fork_doc_count: int
    latest_retirement_batch: str
    lag_expected: bool
    owed_lag: bool


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


def _roadmap_status(root: Path) -> RoadmapStatusState:
    path = root / ".harness" / "roadmap_status.md"
    try:
        md = path.read_text(encoding="utf-8")
    except OSError:
        return RoadmapStatusState(hash="", git_head="", last_refreshed="")

    def field(name: str, pattern: str) -> str:
        m = re.search(pattern, md)
        return m.group(1).strip() if m else ""

    return RoadmapStatusState(
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
        "roadmap_status_hash": state.roadmap_status.hash,
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
        "roadmap_status": state.roadmap_status.__dict__,
        "computed_hash": state.computed_hash,
        "open_prs": state.open_prs,
        "fork_doc_count": state.fork_doc_count,
        "latest_retirement_batch": state.latest_retirement_batch,
        "lag_expected": state.lag_expected,
        "owed_lag": state.owed_lag,
        "findings": [f.__dict__ for f in findings],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def redact_secret_values(value: str) -> str:
    """Redact secret-shaped substrings before they're written to the ledger.

    Three carrier shapes, applied in sequence: `NAME=VALUE` (the original
    shape), `Bearer <token>` / `Authorization: Bearer <token>` headers, and
    bare vendor-prefixed API keys (`sk-...`, `ghp_...`, `AKIA...`, etc.) with
    no `NAME=` prefix at all. Redacting only the first shape let a
    Bearer-token or bare API key passed via `--command` land verbatim in the
    non-gitignored, actively-committed `.harness/codex_credential_gates.jsonl`.
    """
    value = SECRET_VALUE_RE.sub(lambda m: f"{m.group(1)}=<redacted>", value)
    value = BEARER_TOKEN_RE.sub(lambda m: f"{m.group(1)} <redacted>", value)
    value = KNOWN_SECRET_PREFIX_RE.sub(lambda m: f"{m.group(1)}<redacted>", value)
    return value


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
    """True when HEAD itself is a verified terminating-refresh point (direct
    commit or merge-wrapped). This is the fixed point's OWN lag — a refresh
    commit can never record its own not-yet-computed SHA — and is tolerated
    unconditionally, for every caller (CI, session-start, preflight alike):
    a session-start hook checking out exactly the refresh commit must still
    see it as clean, not as unreconciled drift.
    """
    return _is_verified_refresh_point(root, "HEAD")


def _owed_lag(root: Path) -> bool:
    """True when HEAD does NOT touch roadmap_status.md and HEAD's parent is a
    verified terminating-refresh point. This is the "refresh owed" case: the
    very next content commit after a refresh still (correctly, unavoidably)
    carries the refresh's recorded value, since that commit's own SHA did not
    exist yet when the refresh was authored.

    Unlike `_lag_expected`, this tolerance is CALLER-GATED (on
    `--allow-roadmap-drift` in `validate()`), not universal: a post-merge CI
    push on `main` sits at exactly this commit and must pass clean, but a
    local session-start/preflight check on the SAME commit must still force
    the owed refresh before substantive work proceeds — the underlying git
    state is identical in both cases, so only the caller's context can tell
    them apart.

    The file-touch guard below is the same anti-loophole as before: if HEAD
    itself modifies roadmap_status.md — under the wrong title, or bundled with
    unrelated content — it must qualify as a refresh entirely on its own merits
    via `_lag_expected`/`_is_verified_refresh_point`, never by riding its
    parent's owed-lag allowance.
    """
    parents = _out(["git", "rev-list", "--parents", "-n", "1", "HEAD"], cwd=root).split()
    if len(parents) < 2:
        return False
    if ".harness/roadmap_status.md" in _changed_files(root, base_ref=parents[1], head_ref="HEAD"):
        return False
    return _is_verified_refresh_point(root, parents[1])


def _is_verified_refresh_point(root: Path, ref: str) -> bool:
    """True when `ref` is a verified terminating-refresh point: either a direct
    refresh commit (title + exact file set), or a merge commit that wraps one
    (2 parents, diff-vs-first-parent matches the refresh file set, and the
    second parent is itself a verified refresh point — recursing through
    however many merge layers actually exist).

    Checking `ref` directly (rather than resolving "the last commit that
    touched the path") sidesteps git's default history simplification, which
    hides a merge commit from path-limited `git log` whenever the merge is
    tree-same to one parent for that path — exactly the shape of a real
    terminating refresh merged with `git merge --no-ff`. It also means a stray,
    malformed, or bundled edit to `roadmap_status.md` can never be mistaken for
    a legitimate refresh: only a ref that independently proves refresh shape
    (title + exact file set) counts, never mere path-touching position.

    `_lag_expected` calls this on HEAD (covers HEAD itself being a refresh, or
    a merge-wrapped refresh — tolerated unconditionally for every caller).
    `_owed_lag` calls this on HEAD's own parent (covers the far more common
    case: a plain content commit that doesn't touch the file at all, so it
    still carries whatever value the last verified refresh point recorded —
    a commit can never record its own not-yet-computed SHA, so this one-step
    lag is exactly as unavoidable as a refresh commit's own lag, but is
    tolerated only when the caller passes `--allow-roadmap-drift`, i.e. the
    post-merge CI push context). Two or more content commits stacked past the
    last verified refresh point correctly returns False — genuinely
    unreconciled drift, not tolerated by either caller.

    For the merge-wrapped case, the merged content must describe THIS merge's
    own first parent — not merely be internally self-consistent with the
    refresh branch's own (possibly stale) lineage. A refresh branch created at
    commit A, left open while `main` advances to B, then merged in with
    `--no-ff`, must NOT pass: its content still records A, and the merge's
    real predecessor state is B, not A. `second_parent` being itself a
    verified refresh point only proves it correctly described its own parent
    (A) — a fact that is stale, not wrong, once main has moved past it.
    """
    if _is_terminating_refresh_commit(root, ref):
        return True
    parents = _out(["git", "rev-list", "--parents", "-n", "1", ref], cwd=root).split()
    if len(parents) < 3:
        return False
    first_parent, second_parent = parents[1], parents[2]
    if not _is_terminating_refresh_file_set(
        _changed_files(root, base_ref=first_parent, head_ref=ref)
    ):
        return False
    if _roadmap_git_head_at_ref(root, ref) != _out(
        ["git", "rev-parse", "--short=8", first_parent], cwd=root
    ):
        return False
    return _is_verified_refresh_point(root, second_parent)


def _is_terminating_refresh_commit(root: Path, ref: str) -> bool:
    title = _out(["git", "log", "-1", "--format=%s", ref], cwd=root)
    if not title.startswith("ops: roadmap status refresh "):
        return False
    if not _is_terminating_refresh_file_set(_commit_files(root, ref)):
        return False
    return _roadmap_git_head_at_ref(root, ref) == _out(
        ["git", "rev-parse", "--short=8", f"{ref}^"], cwd=root
    )


def _commit_files(root: Path, ref: str) -> list[str]:
    changed = _out(["git", "show", "--name-only", "--pretty=format:", ref], cwd=root)
    return sorted(line.strip() for line in changed.splitlines() if line.strip())


def _is_terminating_refresh_file_set(files: list[str]) -> bool:
    return frozenset(files) in TERMINATING_REFRESH_FILE_SETS


def _roadmap_git_head_at_ref(root: Path, ref: str) -> str:
    """Read `.harness/roadmap_status.md`'s recorded `git_head` field AS OF `ref`
    (not the current worktree) — a refresh commit is only genuinely a refresh
    if it correctly records its own parent's SHA as the state it describes;
    a structurally-shaped commit (right title, right lone file) that writes
    malformed/stale/missing content must not pass as verified.
    """
    md = _out(["git", "show", f"{ref}:.harness/roadmap_status.md"], cwd=root)
    match = re.search(r"\|\s*`git_head`\s*\|\s*`?([a-f0-9]{8,40})", md)
    return match.group(1).strip() if match else ""


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
    roadmap_status = _roadmap_status(root)
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
        roadmap_status=roadmap_status,
        computed_hash=state_hash(head8, prs, forks, batch),
        open_prs=prs,
        open_prs_available=prs_available,
        fork_doc_count=forks,
        latest_retirement_batch=batch,
        lag_expected=_lag_expected(root),
        owed_lag=_owed_lag(root),
    )


def _has_design_impl_mix(files: list[str]) -> bool:
    # Legitimate bundled-absorption (CLAUDE.md §11.4): a design-substrate amendment
    # co-lands with its impl in one PR when a clearance marker (§4.5) records the
    # operationally-accepted consumption — the same back-flow signal the X-AL-3 guard
    # (§4.4) recognizes. Present → ratified bundle, not a silent mix. A silent mix
    # (design + impl, NO clearance marker) still hard-fails.
    if any(CLEARANCE_MARKER_RE.search(f) for f in files):
        return False
    return any(DESIGN_RE.search(f) for f in files) and any(IMPL_RE.search(f) for f in files)


def _has_cite_bearing_changes(files: list[str]) -> bool:
    return any(CITE_RE.search(f) for f in files)


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
    if all(phase in latest for phase in codex_loop.SHIP_GATES):
        current = codex_loop.git_identity(state.root)
        active_issues = codex_loop.check_state(loop_state, current=current)
        if not active_issues:
            return []
        archived_issues = codex_loop.check_state(loop_state, current=None)
        latest_events = {phase: event for phase, (_, event) in latest.items()}
        archived_issues.extend(
            codex_loop.worktree_disposition_issues(loop_state, latest_events, current)
        )
        if not archived_issues:
            return []
        return active_issues
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
        if phase == "worktree_ready" and event_payload.get("linked_worktree") is not True:
            issues.append("worktree_ready gate must be recorded in a linked worktree")
        if phase == "red":
            continue
        if event_payload.get("status") != "passed":
            issues.append(f"{phase} gate must record status=passed")
    return issues


def validate(
    state: GuardState,
    *,
    mode: str,
    allow_roadmap_drift: bool = False,
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

    if state.computed_hash != state.roadmap_status.hash:
        # `owed_lag` (HEAD's parent, not HEAD itself, is the verified refresh) is
        # only tolerated when the caller explicitly allows roadmap drift — i.e.
        # the post-merge CI push context. `lag_expected` (HEAD itself is the
        # verified refresh) is tolerated unconditionally for every caller. Both
        # describe the identical git state on the same commit; only the caller's
        # context can distinguish "CI post-merge smoke, pass clean" from
        # "session-start/preflight, force the owed refresh first."
        ci_owed_lag = allow_roadmap_drift and state.owed_lag
        if state.branch == state.default_branch and not state.lag_expected and not ci_owed_lag:
            findings.append(
                Finding(
                    "hard",
                    "ROADMAP_STATUS_DRIFT",
                    f"roadmap_status.md hash {state.roadmap_status.hash or '<missing>'} "
                    f"does not match computed {state.computed_hash}.",
                )
            )
        elif state.lag_expected or ci_owed_lag:
            findings.append(
                Finding(
                    "warn",
                    "ROADMAP_STATUS_LAG_EXPECTED",
                    "roadmap_status.md hash differs because HEAD is a verified terminating "
                    "roadmap refresh (tolerated for every caller), or HEAD is one commit past "
                    "one and the caller explicitly allowed roadmap drift (CI post-merge push "
                    "only) — a commit can never record its own not-yet-computed SHA; the next "
                    "terminating refresh should reconcile the lag.",
                )
            )
        elif allow_roadmap_drift:
            findings.append(
                Finding(
                    "warn",
                    "ROADMAP_STATUS_DRIFT_ALLOWED",
                    "roadmap_status.md hash differs, but the caller explicitly allowed drift. "
                    "Use only for CI runtime smoke during the post-merge refresh window.",
                )
            )
        else:
            findings.append(
                Finding(
                    "warn",
                    "ROADMAP_STATUS_BRANCH_DIVERGED",
                    "roadmap_status.md hash differs from this branch; this is expected "
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
                    "Latest context checkpoint does not match current HEAD/status/roadmap "
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
            f"roadmap_status_hash: {state.roadmap_status.hash or '<missing>'}",
            f"computed_hash: {state.computed_hash}",
            f"roadmap_status_git_head: {state.roadmap_status.git_head or '<missing>'}",
            f"context_fingerprint: {state_fingerprint(state)}",
            f"latest_retirement_batch: {state.latest_retirement_batch or '<none>'}",
            f"open_fork_doc_count: {state.fork_doc_count}",
            "git status:",
            status,
            "changed files:",
            changed,
            _fmt_findings(findings),
            "Required closeout reminders:",
            "- Update roadmap/status/ledger surfaces when the arc changes state.",
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
            "roadmap_status": state.roadmap_status.__dict__,
            "computed_hash": state.computed_hash,
            "context_fingerprint": state_fingerprint(state),
            "open_prs": state.open_prs,
            "open_prs_available": state.open_prs_available,
            "fork_doc_count": state.fork_doc_count,
            "latest_retirement_batch": state.latest_retirement_batch,
            "lag_expected": state.lag_expected,
            "owed_lag": state.owed_lag,
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
        help="fail if the latest checkpoint does not match current HEAD/status/roadmap",
    )
    parser.add_argument(
        "--allow-roadmap-drift",
        action="store_true",
        help=(
            "downgrade non-default-branch roadmap_status.md hash drift to a warning "
            "unconditionally; on the default branch, downgrade only the one-commit "
            "'owed lag' case (HEAD's parent is a verified terminating refresh — the "
            "post-merge CI push scenario). Never masks arbitrary default-branch drift."
        ),
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
        allow_roadmap_drift=args.allow_roadmap_drift,
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
