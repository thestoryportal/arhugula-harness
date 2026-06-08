#!/usr/bin/env python3
"""Operator dashboard generator (R-XI-01).

Reads the workspace roadmap substrate from five sources and emits a single
self-contained static `roadmap.html` (Mustard Editorial CSS + Chart.js CDN + vanilla JS).
No build step, no bundler — pure static output suitable for GitHub Pages.

Sources
-------
1. `.harness/roadmap_status.md`   — anchor, next-action, in-flight, recently-completed,
                                     retirement progress table, drift-detection log.
2. `Project_Roadmap_v1.md` §5     — R-NNN action catalog (id/title/surface/status/deps).
3. `gh pr list` (GitHub API)      — open PRs + per-PR CI rollup. Degrades to [] offline.
4. `git log` (last 30 days)       — commit cadence sparkline.
5. `harness-*/CLAUDE.md` §4.1     — per-axis retirement enumeration (best-effort count).

All parsing is defensive: a missing or malformed source yields an empty section, never
a crash — the dashboard must render in CI and offline.

Usage
-----
    python tools/dashboard/generate.py [--root .] [--out tools/dashboard/roadmap.html]
"""

# ruff: noqa: E501 — this module embeds a long inline HTML/JS template string;
# wrapping those lines to 100 cols would harm readability and is not meaningful here.

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import date, timedelta
from pathlib import Path

# --------------------------------------------------------------------------- #
# Status vocabulary → display color (Tailwind class fragments, resolved in JS).
# --------------------------------------------------------------------------- #
STATUS_ORDER = [
    "ACTIVE",
    "APPLIED-PENDING-OPERATOR-E2E",
    "PROPOSED",
    "BLOCKED",
    "DEFERRED",
    "RESOLVED",
    "CANCELLED",
]

# --------------------------------------------------------------------------- #
# Closure annotation layer (R-XI-04 enhancement).
# Maps each roadmap status to a display "kind" the renderer uses:
#   closed → strike-through (done); open → "open" label; other → status word +
#   a one-line plain-English explanation (authored below in ANNOTATIONS).
# These annotations are NON-CANONICAL editorial for at-a-glance reading; the
# roadmap §5 entries remain the source of truth. Keep them one-line + jargon-free.
# --------------------------------------------------------------------------- #
STATUS_DISPLAY = {
    "RESOLVED": {"kind": "closed", "word": "closed"},
    "CANCELLED": {"kind": "closed", "word": "cancelled"},
    "ACTIVE": {"kind": "open", "word": "open"},
    "PROPOSED": {"kind": "other", "word": "proposed"},
    "BLOCKED": {"kind": "other", "word": "blocked"},
    "DEFERRED": {"kind": "other", "word": "deferred"},
    "APPLIED-PENDING-OPERATOR-E2E": {"kind": "other", "word": "awaiting operator e2e"},
}

# One-line, non-technical "why this status" for every non-closed item.
ANNOTATIONS = {
    # ACTIVE (open) — recurring process loops, always "in flight".
    "R-600-pattern-bake-in-sweep": "Recurring housekeeping: sweep memory for repeating patterns worth writing down.",
    "R-IF-roadmap-refresh": "Recurring housekeeping: refresh this dashboard after every merge.",
    # BLOCKED
    "R-008-od-4-redaction-partial": "Telemetry redaction is advanced: the per-session toggle, OD opaque-token substrate, durable audit-ledger token map, eval-grade classifier, and multi-tenant audit-backed tokenization path exist; accounting label unchanged.",
    "R-100-mvp-config-discovery": "Waiting on a small decision: auto-find the config file at the project root, or drop that behavior from the spec.",
    "R-700-phase-8-substitution-accounting": "RESOLVED — you ratified the count and Phase 8 is declared CLOSED: 46/54 retired (derived from the substitution ledger). The build phase is done.",
    # DEFERRED (parked by design)
    "R-005-as-8e-files-indefinite": "Files telemetry is live-proven by R-810; any Phase-8 tally movement remains a separate accounting/back-flow action.",
    "R-006-as-8f-managed-agents-indefinite": "Managed-agents telemetry is live-proven by R-820; any Phase-8 tally movement remains a separate accounting/back-flow action.",
    "R-CXA-3-cp-as-seam": "Parked until either a real CP→AS runtime composer is authored or you narrow its scope; no in-workspace producer exists now.",
    "R-810-files-api-integration": "Resolved by the real Anthropic Files upload/reference/delete path plus managed-cloud files.operation Cloud Trace proof.",
    "R-820-managed-agents-integration": "Resolved by the real Anthropic Managed Agents SDK/session integration plus managed-cloud managed_agents.* Cloud Trace proof.",
    # PROPOSED (queued; most need credentials or infrastructure only you can provide)
    "R-300-multi-llm-second-provider": "Resolved by deterministic fallback plus live Anthropic→OpenAI and local Ollama fallback exercises.",
    "R-410-sandbox-tier-2-container-execution": "Resolved by the local-only Docker execution driver and live TIER_2 container e2e.",
    "R-411-sandbox-tier-3-microvm-execution": "Resolved by Docker + gVisor/runsc ToolExecutionDriver on the operator-provisioned Lima Linux VM.",
    "R-412-sandbox-tier-4-full-vm-execution": "Deferred until a full-VM provider implementation exists; R-411 now proves the Tier-3 gVisor path and R-421 proves the managed-cloud surface.",
    "R-420-self-hosted-server-deployment-e2e": "Resolved by the local single-node self-hosted daemon + collector + keyring live e2e.",
    "R-421-managed-cloud-deployment-e2e": "Resolved by the approved E2B + GCP Secret Manager + authenticated Cloud Run collector live e2e; Cloud Trace observed the managed-cloud classification trace.",
    "R-430-otlp-collector-tail-keep-preservation": "Resolved by the R-420 local real-collector tail-keep live proof.",
    "R-440-tier-level-secrets-backend": "Resolved by the self-hosted-keyring selector; R-420 proved it live through the local keyring sentinel.",
    "R-500-multi-tenant-deployment": "Resolved by the local self-hosted multi-tenant proof: tenant.id resource separation, non-toggleable redaction, and tenant-scoped audit reads.",
    "R-830-memory-tool-production-backend": "The local SQLite, provider-free S3, and live S3 cloud-vault slices are done; managed-DB remains future optional scope.",
    "R-900-research-arcs": "Open-ended research / exploration; no fixed scope — pulled in as you choose.",
    "R-CXA-1-as-is-seam": "The one remaining wire (a secret-fetch audit caller) has no real source yet, so wiring it would be hollow; deferred until one exists.",
    "R-CXA-2-cp-is-seam": "The materialized pause/resume caller sites are covered; remaining CP→IS work needs engine-layer producers and the unresolved stage-ordering/spec-disambiguator gaps.",
    "R-CXA-4-od-multi-seam": "Already checked — nothing left to wire (the old placeholders were resolved long ago); stays PARTIAL only for bookkeeping.",
    "R-XI-02": "Dashboard polish — dependency-graph view + sparklines; nice-to-have, nothing blocking it.",
    "R-XI-03": "Dashboard live-update mode; nice-to-have, nothing blocking it.",
}

# The 8 non-RETIRED substitution-ledger rows (the "is the harness built" view).
# state ∈ {PARTIAL, STILL-BOUNDED, STILL-BOUNDED-INDEFINITELY}. `retire` = can/should we
# proceed to retire it, in plain terms.
NONRETIRED_LEDGER = [
    {
        "id": "OD-4",
        "rnnn": "R-008",
        "state": "PARTIAL",
        "why": "Pre-collector redaction, the per-session toggle, OD opaque-token substrate, durable token-map persistence, provider-free eval-grade classifier, and runtime multi-tenant audit-backed tokenization are wired; ratified accounting label remains.",
        "retire": "Not in this implementation slice — OD-4 keeps its R-700 ratified bounded label unless a separate accounting/back-flow reclassifies it.",
    },
    {
        "id": "CXA-1",
        "rnnn": "R-CXA-1",
        "state": "PARTIAL",
        "why": "The AS→IS secret-fetch audit edge has no production caller to fire it.",
        "retire": "Not safely — wiring it now would be a hollow seam (no real source). Worth it only once a real secret-fetch path exists.",
    },
    {
        "id": "CXA-4",
        "rnnn": "R-CXA-4",
        "state": "PARTIAL",
        "why": "Grounded this session — 0 wireable edges; everything genuine is already wired.",
        "retire": "Effectively done; stays PARTIAL only because the ledger's CXA rows were never folded into the cumulative. Any movement is accounting/back-flow, not a production wiring task.",
    },
    {
        "id": "CXA-2",
        "rnnn": "R-CXA-2",
        "state": "STILL-BOUNDED",
        "why": "The CP→IS seam is still bounded; the materialized pause/resume caller sites are covered, but the broader §12.3 edge set is not.",
        "retire": "Not yet — needs engine-layer pause/resume producers plus the unresolved stage-ordering and HITL-disambiguator gaps.",
    },
    {
        "id": "CXA-3",
        "rnnn": "R-CXA-3",
        "state": "STILL-BOUNDED",
        "why": "The CP→AS seam has no runtime composer.",
        "retire": "Not without either building one (a Files arc) or narrowing its scope. Low priority — operator discretion.",
    },
    {
        "id": "AS-8e",
        "rnnn": "R-005",
        "state": "STILL-BOUNDED-INDEFINITELY",
        "why": "files.* telemetry namespace. R-810 now live-proves the Files API upload/reference/delete path and managed-cloud files.operation export.",
        "retire": "Implementation gate is closed by R-810; retain the ledger row until a dedicated accounting/back-flow action changes the canonical tally.",
    },
    {
        "id": "AS-8f",
        "rnnn": "R-006",
        "state": "STILL-BOUNDED-INDEFINITELY",
        "why": "managed_agents.* telemetry namespace. R-820 now live-proves the runtime/integration path; Phase-8 tally movement is separate accounting/back-flow.",
        "retire": "Implementation gate is closed by R-820; retain the ledger row until a dedicated accounting action changes the canonical tally.",
    },
    {
        "id": "CP-17",
        "rnnn": "R-010",
        "state": "STILL-BOUNDED-INDEFINITELY",
        "why": "files-primitives control-plane row. R-810 live-proves the runtime Files API path that consumed the Files arc.",
        "retire": "Implementation gate is closed by R-810; retain the ledger row until a dedicated accounting/back-flow action changes the canonical tally.",
    },
]

# Substitution-ledger derivation (R-600-substitution-ledger-schema). The canonical RETIRED /
# pipeline-advanced integers + bucket counts are DERIVED from `.harness/substitutions.yaml`
# via `tools/substitution_ledger.py` — NOT hand-maintained here. Defensive: the dashboard must
# still render if the ledger is missing, so this degrades to None and the build card falls back.
_SUB_DERIVATION: dict | None = None
try:
    import sys as _sys

    _sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import substitution_ledger as _subledger

    _SUB_DERIVATION = _subledger.derive(_subledger.load())
except Exception:  # defensive — never crash the dashboard on a ledger read/import issue
    _SUB_DERIVATION = None

# Ordered "remaining to complete", graph-derived from depends_on/blocks then layered.
# layer ∈ {build, activation}. `gate` = what unblocks it / why it's where it is.
REMAINING_ORDERED = [
    # --- Build layer: close the substitution ledger ---
    {
        "n": 1,
        "layer": "build",
        "id": "R-700-phase-8-substitution-accounting",
        "label": "Ratify the final retirement count",
        "gate": "RESOLVED — Phase 8 declared CLOSED at 46/54 (ratified). The 8 rows below carry terminal sign-off dispositions.",
    },
    {
        "n": 2,
        "layer": "build",
        "id": "R-CXA-2-cp-is-seam",
        "label": "Build the CP→IS engine-layer seam",
        "gate": "The pause/resume workflow-driver caller-site coverage is complete; remaining work needs engine-layer producers plus stage-ordering and HITL-disambiguator substrate.",
    },
    {
        "n": 3,
        "layer": "build",
        "id": "R-008-od-4-redaction-partial",
        "label": "Finish redaction (OD-4)",
        "gate": "Runtime classifier/tokenization code gate is closed; any remaining movement is accounting/back-flow for the R-700 ratified OD-4 label.",
    },
    {
        "n": 4,
        "layer": "build",
        "id": "R-CXA-1-as-is-seam",
        "label": "Account/close the AS→IS seam",
        "gate": "Deferred until a real secret-fetch producer exists; otherwise hollow.",
    },
    {
        "n": 5,
        "layer": "build",
        "id": "R-CXA-4-od-multi-seam",
        "label": "Account the OD→multi seam (bookkeeping)",
        "gate": "0 wireable — already done in substance; any movement is accounting/back-flow only.",
    },
    {
        "n": 6,
        "layer": "build",
        "id": "R-CXA-3-cp-as-seam",
        "label": "CP→AS seam — build or narrow",
        "gate": "Needs a real CP→AS runtime composer or a scope-narrowing decision.",
    },
    {
        "n": 7,
        "layer": "build",
        "id": "R-005 / R-006 / CP-17",
        "label": "Files namespace + AS-8f accounting",
        "gate": "Files and AS-8f implementation gates are closed by R-810/R-820; any tally movement is separate accounting/back-flow.",
    },
    # --- Activation layer: operator-gated (creds + infra), deployment-ordered ---
    {
        "n": 8,
        "layer": "activation",
        "id": "R-100-mvp-config-discovery",
        "label": "Config auto-discovery decision",
        "gate": "Small spec decision — independent.",
    },
    {
        "n": 9,
        "layer": "activation",
        "id": "R-411 → R-412",
        "label": "Higher-tier sandboxes: microVM → full VM",
        "gate": "R-411 is resolved by the selected Docker + gVisor/runsc path on the provisioned Lima Linux VM; R-412 remains the full-VM provider lane.",
    },
    {
        "n": 10,
        "layer": "activation",
        "id": "R-300-multi-llm-second-provider",
        "label": "Second LLM provider",
        "gate": "Needs OpenAI/Ollama credentials + a mixed-provider test.",
    },
    {
        "n": 12,
        "layer": "activation",
        "id": "R-XI-02 / R-XI-03 / R-900",
        "label": "Dashboard polish + research arcs",
        "gate": "Nice-to-have; no blockers, pulled in at discretion.",
    },
]


def compute_closure(actions: list[dict], dashboard: dict) -> dict:
    """Two layered closure views (operator picked 'Both, layered').

    build      — substitution-ledger retirement (the canonical 'is H_T built'
                 metric). DERIVED from `.harness/substitutions.yaml` (R-600);
                 R-700 ratified the integer at the Phase-8 graduation (46/54).
    activation — the post-Phase-8 forward axis (deployment / integration);
                 exercised items are tracked separately from remaining build work.
    """
    # Canonical counts derived from the substitution ledger (R-600); fall back to the
    # Phase-8-graduation literals only if the ledger is unreadable (defensive).
    if _SUB_DERIVATION is not None:
        total = _SUB_DERIVATION["total_canonical"]
        retired = _SUB_DERIVATION["retired"]
        _bd = _SUB_DERIVATION["by_disposition"]
        n_partial = _bd.get("PARTIAL", 0)
        n_sb = _bd.get("STILL_BOUNDED", 0)
        n_sbi = _bd.get("SB_INDEFINITE", 0)
    else:
        total = 54
        retired = 46
        n_partial = sum(1 for r in NONRETIRED_LEDGER if r["state"] == "PARTIAL")
        n_sb = sum(1 for r in NONRETIRED_LEDGER if r["state"] == "STILL-BOUNDED")
        n_sbi = sum(1 for r in NONRETIRED_LEDGER if r["state"] == "STILL-BOUNDED-INDEFINITELY")
    # forward-axis items = post-Phase-8 surfaces + CXA seams (open ones only)
    fwd = [
        a
        for a in actions
        if (a.get("surface") in {"IV", "V", "VI", "IX", "X"} or a["id"].startswith("R-CXA"))
    ]
    fwd_open = [a for a in fwd if a["status"] not in ("RESOLVED", "CANCELLED")]
    closed_action_ids = {a["id"] for a in actions if a["status"] in ("RESOLVED", "CANCELLED")}
    remaining = [item for item in REMAINING_ORDERED if item["id"] not in closed_action_ids]
    # waffle-grid breakdown (ui-ux-pro-max chart rec: fraction-of-whole filled).
    # `retired` + the 8 non-retired split by state → total 54 (derived above; R-600).
    return {
        "build": {
            "lo": retired,
            "hi": retired,
            "total": total,
            "pct_lo": round(100 * retired / total, 1),
            "pct_hi": round(100 * retired / total, 1),
            "contested": False,
            "nonretired": NONRETIRED_LEDGER,
            "waffle": {
                "retired": retired,
                "partial": n_partial,
                "still_bounded": n_sb,
                "sb_indef": n_sbi,
                "total": total,
            },
        },
        "activation": {
            "total": len(fwd),
            "open": len(fwd_open),
            "exercised_pct": 0,
        },
        "remaining": remaining,
    }


def _run(cmd: list[str], *, cwd: Path, timeout: int = 30) -> str:
    """Run a command, returning stdout; empty string on any failure."""
    try:
        out = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False
        )
        return out.stdout if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def _substitution_snapshot(root: Path) -> dict[str, int] | None:
    """Parse the ledger snapshot block without PyYAML.

    `tools/substitution_ledger.py` remains the canonical full derivation when PyYAML is
    available. This tiny fallback is only for system-Python dashboard regeneration in
    Codex guards, where the committed snapshot still needs the canonical R-600 pins.
    """
    try:
        text = (root / ".harness" / "substitutions.yaml").read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r"^snapshot:\s*$(.*?)(?=^\S|\Z)", text, re.MULTILINE | re.DOTALL)
    if not match:
        return None
    block = match.group(1)
    out: dict[str, int] = {}
    for key in ("retired", "pipeline_advanced", "total_canonical"):
        field = re.search(rf"^\s+{re.escape(key)}:\s*(\d+)\b", block, re.MULTILINE)
        if not field:
            return None
        out[key] = int(field.group(1))
    return out


# --------------------------------------------------------------------------- #
# Source 2 — Project_Roadmap_v1.md §5 R-NNN catalog.
# --------------------------------------------------------------------------- #
def parse_roadmap_actions(text: str) -> list[dict]:
    """Parse the R-NNN entries from the roadmap §5 catalog (YAML-ish blocks)."""
    actions: list[dict] = []
    cur: dict | None = None
    in_mustpass = False  # collecting the verification.must_pass YAML list
    for line in text.split("\n"):
        m = re.match(r"^([A-Za-z0-9-]*R-[A-Za-z0-9-]+):\s*$", line)
        if m:
            cur = {
                "id": m.group(1),
                "title": "",
                "surface": "",
                "status": "",
                "depends_on": [],
                "blocks": [],
                "posture": "",
                "advisor_required": "",
                "council_required": "",
                "must_pass": [],
            }
            actions.append(cur)
            in_mustpass = False
            continue
        if cur is None:
            continue
        # must_pass is a nested YAML list under `verification:` — collect its
        # `- "..."` items until the next key / blank-terminated dedent.
        if in_mustpass:
            if re.match(r"^\s+-\s+", line):
                cur["must_pass"].append(re.sub(r"^\s+-\s+", "", line).strip().strip('"'))
                continue
            if line.strip() == "":
                continue
            in_mustpass = False  # fall through to parse this line normally
        if re.match(r"^\s+must_pass:\s*$", line):
            in_mustpass = True
            continue
        for key in ("title", "surface", "posture", "advisor_required", "council_required"):
            mm = re.match(rf"^\s+{key}:\s*(.+?)\s*(#.*)?$", line)
            if mm and not cur[key]:
                cur[key] = mm.group(1).strip().strip('"')
        ms = re.match(r"^\s+status:\s*(.+?)\s*(#.*)?$", line)
        if ms and not cur["status"]:
            cur["status"] = ms.group(1).split()[0].strip('"').upper()
        for key in ("depends_on", "blocks"):
            md = re.match(rf"^\s+{key}:\s*\[(.*)\]", line)
            if md and not cur[key]:
                cur[key] = [d.strip() for d in md.group(1).split(",") if d.strip()]
    # drop the schema-enum pseudo-entry if present
    return [a for a in actions if not a["status"].startswith("<")]


# --------------------------------------------------------------------------- #
# Source 1 — .harness/roadmap_status.md.
# --------------------------------------------------------------------------- #
def _section(md: str, header: str) -> str:
    """Return the body of a `## header` section up to the next `## ` or EOF."""
    m = re.search(rf"^##\s+{re.escape(header)}\s*$(.*?)(?=^##\s|\Z)", md, re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""


def parse_dashboard(md: str) -> dict:
    out: dict = {
        "hash": "",
        "git_head": "",
        "last_refreshed": "",
        "fork_count": "",
        "next_action": "",
        "recently_completed": [],
        "retirement": {},
        "drift_log_count": 0,
    }
    # anchor
    for field, key in (
        (r"`workspace_state_hash`", "hash"),
        (r"`last_refreshed`", "last_refreshed"),
        (r"`git_head`", "git_head"),
        (r"`open_fork_doc_count`", "fork_count"),
    ):
        m = re.search(rf"\|\s*{field}\s*\|\s*(.+?)\s*\|", md)
        if m:
            out[key] = m.group(1).strip()

    # next action — first non-empty paragraph of the section
    na = _section(md, "Next action")
    out["next_action"] = na

    # recently completed — table rows
    rc = _section(md, "Recently completed (last 5)")
    rows = re.findall(r"^\|\s*(PR #\d+[^|]*)\|\s*([^|]*)\|\s*(.+?)\s*\|\s*$", rc, re.MULTILINE)
    out["recently_completed"] = [
        {"pr": r[0].strip(), "date": r[1].strip(), "note": r[2].strip()}
        for r in rows
        if not r[0].strip().startswith("R-NNN")
    ]

    # retirement progress — parse the "RETIRED | **N/M (P%)**" row + bucket counts
    rp = _section(md, "Phase 7 retirement progress")
    buckets: dict[str, str] = {}
    for row in re.findall(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*[^|]*\|\s*$", rp, re.MULTILINE):
        name = row[0].strip().strip("*")
        val = row[1].strip()
        if name and name not in ("Bucket",) and not name.startswith("-"):
            buckets[name] = val
    out["retirement"]["buckets"] = buckets
    mret = re.search(r"RETIRED[^|]*\|\s*\*\*(\d+)\s*/\s*(\d+)\s*\(([\d.]+)%\)", rp)
    if mret:
        out["retirement"]["retired"] = int(mret.group(1))
        out["retirement"]["total"] = int(mret.group(2))
        out["retirement"]["pct"] = float(mret.group(3))

    # drift log — count table rows in the section
    dl = _section(md, "Drift detection log")
    out["drift_log_count"] = len(re.findall(r"^\|\s*\d{4}-\d{2}-\d{2}\s*\|", dl, re.MULTILINE))
    return out


# --------------------------------------------------------------------------- #
# Source 3 — open PRs + CI rollup via gh.
# --------------------------------------------------------------------------- #
def parse_open_prs(root: Path) -> list[dict]:
    raw = _run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--limit",
            "30",
            "--json",
            "number,title,headRefName,statusCheckRollup,isDraft",
        ],
        cwd=root,
    )
    if not raw:
        return []
    try:
        prs = json.loads(raw)
    except json.JSONDecodeError:
        return []
    result = []
    for pr in sorted(prs, key=lambda p: p.get("number", 0)):
        checks = pr.get("statusCheckRollup") or []
        concl = [(c.get("conclusion") or c.get("status") or "") for c in checks]
        if any(c in ("FAILURE", "CANCELLED", "TIMED_OUT", "ERROR") for c in concl):
            ci = "failing"
        elif any(c in ("", "IN_PROGRESS", "PENDING", "QUEUED") for c in concl):
            ci = "running"
        elif concl:
            ci = "passing"
        else:
            ci = "none"
        result.append(
            {
                "number": pr.get("number"),
                "title": pr.get("title", ""),
                "branch": pr.get("headRefName", ""),
                "draft": pr.get("isDraft", False),
                "ci": ci,
            }
        )
    return result


# --------------------------------------------------------------------------- #
# Source 4 — commit cadence (last 30 days).
# --------------------------------------------------------------------------- #
def parse_cadence(root: Path, days: int = 30) -> list[dict]:
    raw = _run(
        ["git", "log", f"--since={days}.days", "--date=short", "--pretty=format:%ad"],
        cwd=root,
    )
    counts: dict[str, int] = {}
    for line in raw.split("\n"):
        d = line.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            counts[d] = counts.get(d, 0) + 1
    try:
        today = date.fromisoformat(max(counts)) if counts else date.today()
    except ValueError:
        today = date.today()
    series = []
    for i in range(days - 1, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        series.append({"date": d, "count": counts.get(d, 0)})
    return series


# --------------------------------------------------------------------------- #
# Source 4b — PR-merge cadence (R-XI-02): daily count of merged PRs, last 30d.
# --------------------------------------------------------------------------- #
def parse_pr_cadence(root: Path, days: int = 30) -> list[dict]:
    """Daily count of merged PRs — commits whose subject ends `(#NN)`."""
    raw = _run(
        ["git", "log", f"--since={days}.days", "--date=short", "--pretty=format:%ad %s"],
        cwd=root,
    )
    counts: dict[str, int] = {}
    for line in raw.split("\n"):
        mm = re.match(r"^(\d{4}-\d{2}-\d{2})\s+.*\(#\d+\)\s*$", line)
        if mm:
            counts[mm.group(1)] = counts.get(mm.group(1), 0) + 1
    try:
        today = date.fromisoformat(max(counts)) if counts else date.today()
    except ValueError:
        today = date.today()
    series = []
    for i in range(days - 1, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        series.append({"date": d, "count": counts.get(d, 0)})
    return series


# --------------------------------------------------------------------------- #
# Source 4c — RETIRED-count trend (R-XI-02): cumulative retirement over time.
# Each `phase-7d-retirement-events-batch-N.md` carries an `N/54`-style cumulative
# fraction; date each file by its first commit, take the max plausible numerator
# (denominator 49-54), carried forward monotonically. Degrades to batch-ordinal
# x with empty dates when git history is shallow/unavailable.
# --------------------------------------------------------------------------- #
def parse_retired_trend(root: Path) -> list[dict]:
    bdir = root / ".harness"
    if not bdir.is_dir():
        return []

    def _batch_no(p: Path) -> int:
        mb = re.search(r"batch-(\d+)", p.name)
        return int(mb.group(1)) if mb else 0

    files = sorted(bdir.glob("phase-7d-retirement-events-batch-*.md"), key=_batch_no)
    series: list[dict] = []
    running = 0
    for p in files:
        added = (
            _run(
                [
                    "git",
                    "log",
                    "--diff-filter=A",
                    "--reverse",
                    "--format=%ad",
                    "--date=short",
                    "--",
                    str(p.relative_to(root)),
                ],
                cwd=root,
            )
            .split("\n")[0]
            .strip()
        )
        try:
            body = p.read_text(encoding="utf-8")
        except OSError:
            body = ""
        # Parse the cumulative RETIRED count, tied specifically to the word
        # "RETIRED" — NOT any `/5x` fraction (batch prose also carries
        # "pipeline-advanced 49/54", "RETIRE-READY 2/54", etc.). Two canonical
        # phrasings: a transition arrow ("RETIRED 46/54 -> 48/54", post-arrow is
        # the new cumulative) and a headline ("48/54 RETIRED").
        cands = [
            int(x)
            for x in re.findall(
                r"RETIRED[^.\n]{0,40}?\d+\s*/\s*5[0-4]\s*(?:→|->)\s*\*{0,2}(\d+)\s*/\s*5[0-4]",
                body,
            )
        ]
        cands += [int(x) for x in re.findall(r"(\d+)\s*/\s*5[0-4]\s+RETIRED\b", body)]
        if cands:
            running = max(running, max(cands))
        series.append({"batch": _batch_no(p), "date": added, "retired": running})
    # Reconcile the endpoint to the canonical derivation (R-600). The historical points
    # are parsed from batch prose (no structured per-batch source exists), but batch-51's
    # published `48` was superseded to the graduation canonical `46` at R-700 — pin the
    # final point so the trend ends on the same number the headline derives, not stale prose.
    if series:
        snapshot = _SUB_DERIVATION or _substitution_snapshot(root)
        if snapshot is not None:
            series[-1] = {**series[-1], "retired": snapshot["retired"]}
    return series


# --------------------------------------------------------------------------- #
# Dependency graph (R-XI-02): Mermaid flowchart + per-node schema for the
# click-to-inspect panel. Edges run prerequisite -> dependent (depends_on),
# restricted to known nodes so no phantom nodes are auto-created.
# --------------------------------------------------------------------------- #
_DEPGRAPH_STATUS_CLASS = {
    "RESOLVED": "resolved",
    "CANCELLED": "resolved",
    "ACTIVE": "active",
    "APPLIED-PENDING-OPERATOR-E2E": "active",
    "BLOCKED": "blocked",
    "PROPOSED": "proposed",
    "DEFERRED": "deferred",
}


def _short_id(rid: str) -> str:
    """R-300-multi-llm-... -> R-300 ; R-CXA-1-as-is -> R-CXA-1 ; R-XI-02 -> R-XI-02."""
    parts = rid.split("-")
    if len(parts) >= 2 and parts[0] == "R":
        if parts[1].isdigit():
            return f"R-{parts[1]}"
        if len(parts) >= 3 and parts[2].isdigit():
            return f"R-{parts[1]}-{parts[2]}"
        return f"R-{parts[1]}"
    return rid


def build_depgraph(actions: list[dict]) -> dict:
    idmap = {a["id"]: f"n{k}" for k, a in enumerate(actions)}
    lines = ["graph LR"]
    lines += [
        "  classDef resolved fill:#221d16,stroke:#3a342a,color:#7d745f;",
        "  classDef active fill:#f0a830,stroke:#ffc14d,color:#15120d;",
        "  classDef blocked fill:#3a1f17,stroke:#d8542f,color:#e8e0cf;",
        "  classDef proposed fill:#1c1812,stroke:#7d745f,color:#b3a98f;",
        "  classDef deferred fill:#1c1812,stroke:#3a342a,color:#7d745f,stroke-dasharray:3 3;",
    ]
    schema: dict[str, dict] = {}
    for a in actions:
        nid = idmap[a["id"]]
        lines.append(f'  {nid}["{_short_id(a["id"])}"]')
        schema[nid] = {
            "id": a["id"],
            "title": a["title"],
            "status": a["status"],
            "surface": a["surface"],
            "posture": a["posture"],
            "depends_on": a["depends_on"],
            "blocks": a["blocks"],
            "must_pass": a["must_pass"],
            "advisor": a["advisor_required"],
            "council": a["council_required"],
        }
    for a in actions:
        for dep in a["depends_on"]:
            if dep in idmap:
                lines.append(f"  {idmap[dep]} --> {idmap[a['id']]}")
    for a in actions:
        nid = idmap[a["id"]]
        lines.append(f"  class {nid} {_DEPGRAPH_STATUS_CLASS.get(a['status'], 'proposed')};")
        lines.append(f"  click {nid} nodeClick")
    return {"mermaid": "\n".join(lines), "schema": schema}


# --------------------------------------------------------------------------- #
# Source 5 — per-axis retirement enumeration from harness-*/CLAUDE.md §4.1.
# --------------------------------------------------------------------------- #
def parse_axis_retirement(root: Path) -> list[dict]:
    axes = []
    for axis in ("is", "as", "cp", "od"):
        p = root / f"harness-{axis}" / "CLAUDE.md"
        if not p.exists():
            continue
        try:
            body = p.read_text(encoding="utf-8")
        except OSError:
            continue
        retired = len(re.findall(r"\bRETIRED\b", body))
        axes.append({"axis": axis.upper(), "retired_mentions": retired})
    return axes


# --------------------------------------------------------------------------- #
# Operator-gate inventory — derived from action statuses + dashboard signals.
# --------------------------------------------------------------------------- #
def operator_gates(actions: list[dict], dashboard: dict) -> list[dict]:
    gates = []
    for a in actions:
        st = a["status"]
        if st == "APPLIED-PENDING-OPERATOR-E2E":
            gates.append({"id": a["id"], "gate": "live e2e run (operator)"})
    # RETIRE-READY buckets from the retirement table
    buckets = dashboard.get("retirement", {}).get("buckets", {})
    for name, val in buckets.items():
        if "RETIRE-READY" in name.upper() or "RETIRE-READY" in val.upper():
            gates.append({"id": name, "gate": val})
    return gates


# --------------------------------------------------------------------------- #
# HTML rendering.
# --------------------------------------------------------------------------- #
HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Harness roadmap — operator console</title>
<meta name="description" content="Multi-LLM agent harness — development closure, retirement ledger, and R-NNN roadmap. Instrument-ledger console."/>
<meta name="dashboard-live-head" content="__LIVE_HEAD__"/>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='3' fill='%2315120d'/%3E%3Crect x='7' y='7' width='8' height='8' fill='%23f0a830'/%3E%3Crect x='17' y='7' width='8' height='8' fill='none' stroke='%233a342a'/%3E%3Crect x='7' y='17' width='8' height='8' fill='none' stroke='%233a342a'/%3E%3Crect x='17' y='17' width='8' height='8' fill='%23d8542f'/%3E%3C/svg%3E"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<style>
  :root{{
    --ground:#15120d;        /* warm near-black ~oklch(0.19 0.02 70) */
    --panel:#1c1812;
    --panel-hi:#221d16;
    --bone:#e8e0cf;          /* primary text ~11:1 on ground */
    --bone-soft:#cabfa2;     /* >=5.5:1 */
    --bone-faint:#ab9f82;    /* labels/meta, large/secondary only */
    --amber:#f0a830;         /* single signal accent */
    --amber-glow:#ffc14d;
    --ember:#d8542f;         /* alert / partial ONLY */
    --hair:#3a342a;          /* hairline rules + grid */
    --hair-soft:#2a251e;
    --radius:2px;            /* single corner-radius scale */
    --disp:'Big Shoulders Display','Arial Narrow',sans-serif;
    --body:'IBM Plex Sans','Helvetica Neue',sans-serif;
    --mono:'JetBrains Mono','SFMono-Regular',ui-monospace,monospace;
  }}
  *{{box-sizing:border-box;margin:0;padding:0;}}
  html{{scroll-behavior:smooth;}}
  body{{
    background:var(--ground);color:var(--bone);font-family:var(--body);
    line-height:1.55;-webkit-font-smoothing:antialiased;font-variant-numeric:tabular-nums;
    background-image:
      linear-gradient(var(--hair-soft) 1px,transparent 1px),
      linear-gradient(90deg,var(--hair-soft) 1px,transparent 1px);
    background-size:46px 46px;background-position:-1px -1px;
  }}
  @media(prefers-reduced-motion:no-preference){{
    body>.wrap>main>*{{animation:rise .5s cubic-bezier(.22,.61,.36,1) both;}}
    main>*:nth-child(2){{animation-delay:.05s;}} main>*:nth-child(3){{animation-delay:.1s;}}
    main>*:nth-child(4){{animation-delay:.15s;}} main>*:nth-child(5){{animation-delay:.2s;}}
  }}
  @keyframes rise{{from{{opacity:0;transform:translateY(10px);}}to{{opacity:1;transform:none;}}}}

  .wrap{{max-width:none;margin:0;padding:0 clamp(28px,4vw,88px) 72px;}}
  .mono{{font-family:var(--mono);}}
  a{{color:var(--amber);text-decoration:none;}}
  a:hover{{text-decoration:underline;text-underline-offset:2px;}}
  code{{font-family:var(--mono);font-size:.84em;color:var(--amber-glow);
    background:var(--hair-soft);border:1px solid var(--hair);border-radius:var(--radius);padding:.5px 4px;}}
  strong{{color:var(--bone);font-weight:600;}}

  /* masthead — the instrument header band */
  .top{{border-bottom:1px solid var(--hair);background:
    linear-gradient(180deg,rgba(240,168,48,.05),transparent 60%);}}
  .top .inner{{max-width:none;margin:0;padding:22px clamp(28px,4vw,88px) 18px;}}
  .top .row1{{display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:12px;}}
  .brand{{font-family:var(--disp);font-weight:700;font-size:34px;letter-spacing:.5px;
    line-height:.9;text-transform:uppercase;color:var(--bone);}}
  .brand .sig{{color:var(--amber);}}
  .brand .sub{{display:block;font-family:var(--mono);font-weight:400;font-size:14.5px;
    letter-spacing:3px;color:var(--bone-faint);margin-top:7px;text-transform:none;}}
  .readout{{font-family:var(--mono);font-size:14px;line-height:1.7;color:var(--bone-soft);
    text-align:right;max-width:560px;}}
  .readout .lab{{color:var(--bone-faint);}}
  .readout .v{{color:var(--amber);}}
  .top .ticks{{display:flex;gap:0;margin-top:16px;border-top:1px solid var(--hair-soft);
    border-bottom:1px solid var(--hair-soft);}}
  .tick{{flex:1;padding:9px 0;font-family:var(--mono);font-size:13.5px;letter-spacing:1.5px;
    text-transform:uppercase;color:var(--bone-faint);border-right:1px solid var(--hair-soft);}}
  .tick:last-child{{border-right:none;}}
  .tick b{{display:block;font-family:var(--disp);font-weight:700;font-size:21px;letter-spacing:.5px;
    color:var(--bone);margin-top:2px;}}
  .tick.sig b{{color:var(--amber);}} .tick.ember b{{color:var(--ember);}}

  /* numbered section header — quiet, integrated */
  section{{margin-top:46px;}}
  .shead{{display:flex;align-items:baseline;gap:13px;margin-bottom:18px;}}
  .shead .num{{font-family:var(--mono);font-size:14.5px;font-weight:700;color:var(--amber);
    letter-spacing:1px;flex-shrink:0;}}
  .shead .htxt{{font-family:var(--disp);font-weight:600;font-size:24px;letter-spacing:.6px;
    text-transform:uppercase;color:var(--bone);line-height:1;}}
  .shead .rule{{flex:1;border-top:1px solid var(--hair);transform:translateY(-5px);}}

  /* panels — hairline border + inset glow, NO drop shadow */
  .panel{{background:var(--panel);border:1px solid var(--hair);border-radius:var(--radius);padding:24px;}}
  .panel.lit{{box-shadow:inset 0 0 0 1px rgba(240,168,48,.08),inset 0 1px 22px rgba(240,168,48,.05);
    border-color:#4a4030;}}
  .grid2{{display:grid;grid-template-columns:1fr 1fr;gap:20px;}}
  .gridHero{{display:grid;grid-template-columns:1.25fr 1fr;gap:20px;align-items:stretch;}}

  .label{{font-family:var(--mono);font-size:13.5px;letter-spacing:2px;text-transform:uppercase;
    color:var(--bone-faint);font-weight:500;}}

  /* closure readouts */
  .meter .k{{font-family:var(--mono);font-size:13.5px;letter-spacing:2px;text-transform:uppercase;
    color:var(--bone-soft);margin-bottom:10px;}}
  .meter .big{{font-family:var(--disp);font-weight:700;font-size:62px;line-height:.85;
    color:var(--amber);letter-spacing:1px;}}
  .meter .big .u{{font-size:23px;color:var(--bone-soft);font-family:var(--mono);font-weight:500;letter-spacing:0;}}
  .meter.cold .big{{color:var(--bone);}}
  .meter .sub{{font-size:15px;color:var(--bone-soft);margin-top:12px;line-height:1.65;}}
  .gaugebar{{height:7px;background:var(--hair-soft);border:1px solid var(--hair);border-radius:var(--radius);
    margin-top:14px;overflow:hidden;position:relative;}}
  .gaugebar > span{{display:block;height:100%;background:linear-gradient(90deg,var(--amber),var(--amber-glow));
    box-shadow:0 0 8px rgba(255,193,77,.4);}}
  .quote{{font-family:var(--disp);font-weight:500;font-size:20px;letter-spacing:.3px;line-height:1.15;
    color:var(--bone);margin-top:18px;padding-left:14px;border-left:2px solid var(--amber);}}

  /* THE HERO: 54-cell waffle of glowing amber cells on dark ground */
  .waffle{{display:grid;grid-template-columns:repeat(18,1fr);gap:5px;margin-top:14px;max-width:520px;}}
  .cell{{aspect-ratio:1;border-radius:1px;background:transparent;border:1px solid var(--hair);}}
  .cell.retired{{background:var(--amber);border-color:var(--amber-glow);
    box-shadow:0 0 5px rgba(255,193,77,.55),inset 0 0 3px rgba(255,225,160,.6);}}
  .cell.partial{{background:var(--ember);border-color:#f06a45;
    box-shadow:0 0 5px rgba(216,84,47,.6);}}
  .cell.bounded{{background:var(--bone-faint);border-color:var(--bone-soft);}}
  .cell.indef{{background:transparent;border:1px dashed var(--bone-faint);}}
  .legend{{display:flex;flex-wrap:wrap;gap:10px 18px;margin-top:16px;font-family:var(--mono);
    font-size:14.5px;color:var(--bone-soft);}}
  .legend span{{display:inline-flex;align-items:center;gap:7px;}}
  .legend i{{width:11px;height:11px;border-radius:1px;flex-shrink:0;display:inline-block;}}
  .legend .n{{color:var(--bone);font-weight:700;}}

  /* ledger rows — status word always present; strike for closed */
  .led{{padding:13px 0;border-bottom:1px solid var(--hair-soft);}}
  .led:last-child{{border-bottom:none;}}
  .led .lh{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}}
  .led .lid{{font-family:var(--disp);font-weight:700;font-size:19.5px;letter-spacing:.5px;color:var(--bone);}}
  .led .lwhy{{font-size:14.5px;color:var(--bone-soft);margin-top:6px;line-height:1.6;}}
  .led .lret{{font-size:14.5px;margin-top:5px;line-height:1.6;color:var(--bone-soft);}}
  .led .lret b{{font-family:var(--mono);font-weight:700;font-size:13px;letter-spacing:1.5px;
    text-transform:uppercase;color:var(--amber);margin-right:7px;}}

  /* status chips — shape + label + hue (never hue alone) */
  .chip{{font-family:var(--mono);font-size:13px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
    padding:3px 8px;border-radius:var(--radius);flex-shrink:0;white-space:nowrap;border:1px solid transparent;}}
  .chip.partial{{background:rgba(216,84,47,.14);color:#f5805a;border-color:var(--ember);}}      /* alert hue */
  .chip.bounded{{background:transparent;color:var(--bone-soft);border-color:var(--bone-faint);}}  /* outline */
  .chip.indef{{background:transparent;color:var(--bone-faint);border-style:dashed;border-color:var(--bone-faint);}} /* dashed = deferred */
  .chip.build{{background:var(--amber);color:var(--ground);border-color:var(--amber-glow);}}        /* filled amber */
  .chip.activation{{background:transparent;color:var(--amber);border-color:var(--amber);}}           /* amber outline */
  .chip.closed{{background:var(--hair-soft);color:var(--bone-faint);border-color:var(--hair);}}
  .chip.open{{background:var(--amber);color:var(--ground);border-color:var(--amber-glow);}}
  .chip.proposed{{background:transparent;color:var(--bone-soft);border-color:var(--hair);}}
  .chip.deferred{{background:transparent;color:var(--bone-faint);border-style:dashed;border-color:var(--bone-faint);}}
  .chip.blocked{{background:rgba(216,84,47,.14);color:#f5805a;border-color:var(--ember);}}
  .chip.other{{background:transparent;color:var(--bone-soft);border-color:var(--hair);}}
  .chip.state{{background:transparent;color:var(--bone-soft);border-color:var(--bone-faint);}}

  /* remaining-to-complete ordered list */
  .rem{{display:flex;align-items:flex-start;gap:14px;padding:11px 0;border-bottom:1px solid var(--hair-soft);}}
  .rem:last-child{{border-bottom:none;}}
  .rem .rn{{font-family:var(--mono);font-weight:700;font-size:15px;color:var(--amber);width:26px;
    text-align:right;flex-shrink:0;padding-top:2px;}}
  .rem .rbody{{flex:1;min-width:0;}}
  .rem .rt{{display:flex;align-items:center;gap:9px;flex-wrap:wrap;}}
  .rem .rlabel{{font-size:15.5px;font-weight:600;color:var(--bone);}}
  .rem .rgate{{font-size:14px;color:var(--bone-soft);margin-top:4px;line-height:1.55;}}
  .rem .rmeta{{font-family:var(--mono);font-size:14px;color:var(--bone-faint);margin-top:4px;}}

  /* status-board surfaces */
  .surf{{margin-bottom:20px;}}
  .surf .stitle{{font-family:var(--disp);font-weight:600;font-size:16.5px;letter-spacing:.7px;
    text-transform:uppercase;color:var(--bone);margin-bottom:8px;display:flex;align-items:baseline;gap:8px;}}
  .surf .stitle .ct{{font-family:var(--mono);font-size:13.5px;color:var(--bone-faint);font-weight:400;letter-spacing:1px;}}
  .rows{{border-left:1px solid var(--hair);}}
  .r{{display:flex;align-items:flex-start;gap:11px;padding:8px 0 8px 14px;border-left:2px solid transparent;
    margin-left:-1px;transition:border-color .16s ease,background .16s ease;}}
  .r:hover{{background:var(--panel-hi);border-left-color:var(--amber);}}
  .r .rmain{{flex:1;min-width:0;}}
  .r .rt2{{font-size:15px;color:var(--bone);}}
  .r.closed .rt2{{text-decoration:line-through;text-decoration-color:var(--bone-faint);color:var(--bone-faint);}}
  .r .rwhy{{font-size:15px;color:var(--bone-soft);margin-top:3px;line-height:1.5;}}

  /* prose blocks */
  .prose{{font-size:15px;color:var(--bone-soft);line-height:1.75;}}
  .prose strong{{color:var(--bone);}}
  .prose li{{margin-left:20px;list-style:square;margin-top:4px;}}
  .prose li::marker{{color:var(--amber);}}

  /* small lists */
  .pr{{display:flex;align-items:baseline;gap:9px;padding:7px 0;font-size:15px;color:var(--bone-soft);
    border-bottom:1px solid var(--hair-soft);}}
  .pr:last-child{{border-bottom:none;}}
  .pr .num{{font-family:var(--mono);font-size:14.5px;color:var(--bone-faint);}}
  .pr .dot{{font-size:12.5px;line-height:1;}}
  .pr .dot.passing{{color:var(--amber);}} .pr .dot.running{{color:var(--amber-glow);}}
  .pr .dot.failing{{color:var(--ember);}} .pr .dot.none{{color:var(--bone-faint);}}
  .gate{{padding:9px 0;font-size:15px;border-bottom:1px solid var(--hair-soft);color:var(--bone-soft);}}
  .gate:last-child{{border-bottom:none;}}
  .gate b{{font-family:var(--mono);font-weight:700;font-size:13px;letter-spacing:1.5px;
    text-transform:uppercase;color:var(--amber);}}
  .recent{{padding:13px 0;border-bottom:1px solid var(--hair-soft);}}
  .recent:last-child{{border-bottom:none;}}
  .recent .rh{{font-family:var(--disp);font-weight:700;font-size:17.5px;letter-spacing:.4px;color:var(--bone);}}
  .recent .rd{{font-family:var(--mono);font-size:14px;color:var(--bone-faint);margin-left:8px;}}
  .recent .rn2{{font-size:14px;color:var(--bone-soft);margin-top:5px;line-height:1.6;}}
  .muted{{color:var(--bone-faint);font-family:var(--mono);font-size:14.5px;}}
  .chartnote{{padding:28px;text-align:center;color:var(--bone-faint);font-family:var(--mono);
    font-size:15px;letter-spacing:.5px;border:1px dashed var(--hair);border-radius:var(--radius);}}

  footer{{margin-top:54px;padding-top:18px;border-top:1px solid var(--hair);
    font-family:var(--mono);font-size:14px;color:var(--bone-faint);letter-spacing:.5px;line-height:1.8;}}
  footer code{{color:var(--bone-soft);background:transparent;border:none;padding:0;}}

  :focus-visible{{outline:2px solid var(--amber);outline-offset:2px;border-radius:var(--radius);}}

  /* R-XI-02 — dependency graph + click-to-inspect panel (scaffold; loop elevates) */
  .depgraph-wrap{{overflow:auto;border:1px solid var(--hair);border-radius:var(--radius);background:var(--ground);padding:12px;max-height:600px;}}
  .mermaid-host{{min-width:640px;}}
  .mermaid-host svg{{max-width:none;height:auto;}}
  .dep-panel{{margin-top:14px;border:1px solid var(--hair);border-left:2px solid var(--amber);border-radius:var(--radius);background:var(--panel-hi);padding:14px 16px;}}
  .dep-panel .dp-head{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}}
  .dep-panel .dp-id{{font-family:var(--mono);font-size:15px;color:var(--amber);}}
  .dep-panel .dp-title{{font-family:var(--disp);font-size:19.5px;color:var(--bone);margin-top:6px;}}
  .dep-panel .dp-grid{{display:grid;grid-template-columns:1fr 1fr;gap:6px 18px;margin-top:10px;font-size:14.5px;color:var(--bone-soft);}}
  .dep-panel .lab{{font-size:13.5px;letter-spacing:1.5px;text-transform:uppercase;color:var(--bone-faint);font-weight:700;margin-right:6px;}}
  .dep-panel ul.mp{{margin:4px 0 0 0;}}
  .dep-panel ul.mp li{{margin-left:18px;list-style:square;font-size:14.5px;color:var(--bone-soft);line-height:1.55;}}
  .dep-panel code{{font-family:var(--mono);font-size:14.5px;color:var(--amber-glow);background:var(--ground);border:1px solid var(--hair);border-radius:2px;padding:1px 4px;}}

  /* operator readability pass (preview feedback): primary text in these
     blocks -> 16px / #ddd5bd. <strong> keeps var(--bone) via the global
     strong rule; amber numbers, chips, status dots, mono-meta and display
     headers keep their accent colors. */
  .rem, .led, .prose, .r, .pr, .recent .rn2,
  .r .rt2, .r .rwhy, .led .lwhy, .led .lret, .rem .rlabel, .rem .rgate{{
    font-size:16px;color:#ddd5bd;}}

  /* R-XI-03 live-update indicator */
  .live-ind{{font-family:var(--mono);}}
  .live-ind.on{{color:var(--amber);}}
  .live-ind.upd{{color:var(--amber-glow);}}
  .live-ind.off{{color:var(--bone-faint);}}

  @media(max-width:768px){{
    .grid2,.gridHero{{grid-template-columns:1fr;}}
    .waffle{{grid-template-columns:repeat(12,1fr);}}
    .brand{{font-size:27px;}} .meter .big{{font-size:50px;}}
    .readout{{text-align:left;}} .top .row1{{align-items:flex-start;}}
    .tick b{{font-size:18.5px;}}
  }}
  @media(prefers-reduced-motion:reduce){{
    html{{scroll-behavior:auto;}} .r{{transition:none;}}
    body>.wrap>main>*{{animation:none;}}
  }}
</style>
</head>
<body>
<header class="top">
  <div class="inner">
    <div class="row1">
      <div class="brand">Harness <span class="sig">Roadmap</span>
        <span class="sub">OPERATOR CONSOLE / INSTRUMENT LEDGER</span>
      </div>
      <div class="readout mono">
        <div><span class="lab">HEAD</span> <span class="v" id="ro-head"></span> (main)</div>
        <div><span class="lab">LAST</span> <span id="ro-last"></span></div>
        <div><span class="lab">HASH</span> <span class="v" id="ro-hash"></span> <span class="lab">/</span> <span id="ro-when"></span></div>
        <div><span class="lab">OPEN FORKS</span> <span class="v" id="ro-forks"></span></div>
        <div><span class="lab">LIVE</span> <span id="ro-live" class="live-ind">● —</span></div>
      </div>
    </div>
    <div class="ticks">
      <div class="tick sig">build closure <b id="tk-build"></b></div>
      <div class="tick">retired <b id="tk-retired"></b></div>
      <div class="tick ember">unretired <b id="tk-unret"></b></div>
      <div class="tick">activation <b id="tk-activation"></b></div>
      <div class="tick">drift events <b id="tk-drift"></b></div>
    </div>
  </div>
</header>

<div class="wrap">
  <main>
    <section id="closure-card">
      <div class="shead"><span class="num">01</span><span class="htxt">Development closure</span><span class="rule"></span></div>
      <div id="closure"></div>
    </section>

    <section>
      <div class="shead"><span class="num">02</span><span class="htxt">Next action</span><span class="rule"></span></div>
      <div class="panel lit"><div id="next-action" class="prose"></div></div>
    </section>

    <section>
      <div class="shead"><span class="num">03</span><span class="htxt">R-NNN status board</span><span class="rule"></span></div>
      <div class="panel"><div id="status-board"></div></div>
    </section>

    <section id="pp8-card">
      <div class="shead"><span class="num">04</span><span class="htxt">Post-Phase-8 forward register</span><span class="rule"></span></div>
      <div class="panel"><div id="pp8-summary" class="prose" style="margin-bottom:16px"></div><div id="pp8-board"></div></div>
    </section>

    <div class="grid2">
      <section style="margin-top:0">
        <div class="shead"><span class="num">05</span><span class="htxt">In-flight PRs</span><span class="rule"></span></div>
        <div class="panel"><div id="prs"></div></div>
      </section>
      <section style="margin-top:0">
        <div class="shead"><span class="num">06</span><span class="htxt">Operator gates</span><span class="rule"></span></div>
        <div class="panel"><div id="gates"></div></div>
      </section>
    </div>

    <div class="grid2">
      <section style="margin-top:0">
        <div class="shead"><span class="num">07</span><span class="htxt">Commit cadence</span><span class="rule"></span></div>
        <div class="panel"><canvas id="cadence" height="120"></canvas></div>
      </section>
      <section style="margin-top:0">
        <div class="shead"><span class="num">08</span><span class="htxt">Recently completed</span><span class="rule"></span></div>
        <div class="panel"><div id="recent"></div></div>
      </section>
    </div>

    <section id="depgraph-card">
      <div class="shead"><span class="num">09</span><span class="htxt">Dependency graph</span><span class="rule"></span></div>
      <div class="panel">
        <div class="label" style="margin-bottom:12px">R-NNN dependency flow / prerequisite &rarr; dependent &nbsp;·&nbsp; click a node to inspect its discipline schema</div>
        <div class="depgraph-wrap"><div id="depgraph" class="mermaid-host"></div></div>
        <div id="dep-panel" class="dep-panel" hidden></div>
      </div>
    </section>

    <div class="grid2">
      <section style="margin-top:0">
        <div class="shead"><span class="num">10</span><span class="htxt">PR cadence</span><span class="rule"></span></div>
        <div class="panel"><canvas id="pr-cadence" height="120"></canvas></div>
      </section>
      <section style="margin-top:0">
        <div class="shead"><span class="num">11</span><span class="htxt">Retired trend</span><span class="rule"></span></div>
        <div class="panel"><canvas id="retired-trend" height="120"></canvas></div>
      </section>
    </div>

    <footer>
      Drift-log events: <span class="mono" style="color:var(--amber)" id="drift-count"></span> &nbsp;/&nbsp;
      generated by <code>tools/dashboard/generate.py</code> (R-XI-01) &nbsp;/&nbsp;
      design: Almanac Noir / instrument ledger (candidate B) &nbsp;/&nbsp;
      static read-only snapshot — refresh via the generator / Pages deploy.
    </footer>
  </main>
</div>

<script>
const DATA = __DATA__;
const esc = (s) => (s ?? "").replace(/[&<>]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c]));
function mdLite(s) {{
  let h = esc(s);
  h = h.replace(/`([^`]+)`/g, '<code>$1</code>');
  h = h.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
  h = h.replace(/^- (.*)$/gm, '<li>$1</li>');
  h = h.replace(/\\n\\n/g, '<br/><br/>');
  return h;
}}

// masthead readout + ticks (instrument-ledger header)
const d = DATA.dashboard || {{}};
(function() {{
  const cl = DATA.closure || {{}}, b = cl.build || {{}}, ac = cl.activation || {{}}, w = b.waffle || {{}};
  const set = (id, html) => {{ const el = document.getElementById(id); if (el) el.innerHTML = html; }};
  const rc0 = (d.recently_completed || [])[0] || null;
  set("ro-head", esc(d.git_head));
  set("ro-last", rc0 ? `${{esc(rc0.pr)}} — ${{esc(rc0.note).slice(0,90)}}${{rc0.note && rc0.note.length>90?'…':''}}` : "—");
  set("ro-hash", esc(d.hash));
  set("ro-when", esc(d.last_refreshed));
  set("ro-forks", esc(d.fork_count));
  set("tk-build", `${{b.pct_lo}}%`);
  set("tk-retired", `${{w.retired||0}} / ${{w.total||b.total||0}}`);
  set("tk-unret", `${{(b.nonretired||[]).length}} rows`);
  set("tk-activation", `${{ac.exercised_pct||0}}% exercised`);
  set("tk-drift", `${{d.drift_log_count ?? 0}}`);
}})();

// next action
document.getElementById("next-action").innerHTML = mdLite(d.next_action);

// ---- closure hero ----
(function() {{
  const cl = DATA.closure || {{}}, b = cl.build || {{}}, ac = cl.activation || {{}}, w = b.waffle || {{}};
  const stateClass = {{ "PARTIAL":"partial", "STILL-BOUNDED":"bounded", "STILL-BOUNDED-INDEFINITELY":"indef" }};
  const pad2 = (n) => String(n).padStart(2, "0");
  // waffle cells
  let cells = "";
  for (let i=0;i<(w.retired||0);i++) cells += '<div class="cell retired"></div>';
  for (let i=0;i<(w.partial||0);i++) cells += '<div class="cell partial"></div>';
  for (let i=0;i<(w.still_bounded||0);i++) cells += '<div class="cell bounded"></div>';
  for (let i=0;i<(w.sb_indef||0);i++) cells += '<div class="cell indef"></div>';
  const legend =
    `<span><i style="background:var(--amber)"></i>retired <span class="n">${{w.retired||0}}</span></span>` +
    `<span><i style="background:var(--ember)"></i>partial <span class="n">${{w.partial||0}}</span></span>` +
    `<span><i style="background:var(--bone-faint)"></i>still-bounded <span class="n">${{w.still_bounded||0}}</span></span>` +
    `<span><i style="background:transparent;border:1px dashed var(--bone-faint)"></i>indefinite <span class="n">${{w.sb_indef||0}}</span></span>`;

  const nonret = (b.nonretired||[]).map(r => `
    <div class="led">
      <div class="lh"><span class="lid">${{esc(r.id)}}</span>
        <span class="chip ${{stateClass[r.state]||'bounded'}}">${{esc(r.state)}}</span>
        <span class="muted">${{esc(r.rnnn)}}</span></div>
      <div class="lwhy">${{esc(r.why)}}</div>
      <div class="lret"><b>retire?</b>${{esc(r.retire)}}</div>
    </div>`).join("");

  const rem = (cl.remaining||[]).map(r => `
    <div class="rem"><span class="rn">${{pad2(r.n)}}</span><div class="rbody">
      <div class="rt"><span class="rlabel">${{esc(r.label)}}</span> <span class="chip ${{r.layer==='build'?'build':'activation'}}">${{esc(r.layer)}}</span></div>
      <div class="rgate">${{esc(r.gate)}}</div>
      <div class="rmeta">${{esc(r.id)}}</div>
    </div></div>`).join("");

  document.getElementById("closure").innerHTML = `
    <div class="gridHero">
      <div class="panel lit meter">
        <div class="k">Build closure / is the harness built?</div>
        <div class="big">${{b.pct_lo}}<span class="u">%</span></div>
        <div class="sub"><strong>${{b.lo}} of ${{b.total}}</strong> substitutions retired — the canonical count, derived from the substitution ledger and ratified at the <strong>Phase-8 graduation (R-700)</strong>. The 8 rows below carry terminal sign-off dispositions.</div>
        <div class="gaugebar"><span style="width:${{b.pct_lo}}%"></span></div>
        <div class="waffle" role="img" aria-label="${{w.total}} substitution cells: ${{w.retired}} retired, ${{w.partial}} partial, ${{w.still_bounded}} still-bounded, ${{w.sb_indef}} indefinite">${{cells}}</div>
        <div class="legend">${{legend}}</div>
      </div>
      <div class="panel meter cold">
        <div class="k">Activation / deployment closure</div>
        <div class="sub">Operator-gated: credentials + infrastructure that cannot run in this workspace. The <strong>${{ac.open}} of ${{ac.total}}</strong> open forward items are bounded-residual by design, <strong>not remaining build work</strong>.</div>
        <div class="big">${{ac.exercised_pct||0}}<span class="u">% exercised</span></div>
        <div class="quote">"The harness is built; this axis switches on at a real deployment."</div>
      </div>
    </div>
    <div class="grid2" style="margin-top:20px">
      <div class="panel">
        <div class="label" style="margin-bottom:14px">Unretired substitutions (${{(b.nonretired||[]).length}}) / state, why, can we retire?</div>
        ${{nonret}}
      </div>
      <div class="panel">
        <div class="label" style="margin-bottom:14px">Remaining to complete / ordered by logical flow</div>
        ${{rem}}
      </div>
    </div>`;
}})();

// ---- item row (R-NNN board + register) ----
function itemRow(a) {{
  if (a.rkind === "closed") {{
    return `<div class="r closed"><div class="rmain"><span class="rt2">${{esc(a.title)}}</span></div><span class="chip closed">closed</span></div>`;
  }}
  if (a.rkind === "open") {{
    return `<div class="r"><div class="rmain"><span class="rt2">${{esc(a.title)}}</span></div><span class="chip open">open</span></div>`;
  }}
  const CHIP = {{ BLOCKED:"blocked", DEFERRED:"deferred", PROPOSED:"proposed" }};
  const chipClass = CHIP[a.status] || "other";
  const why = a.why ? `<div class="rwhy">${{esc(a.why)}}</div>` : "";
  return `<div class="r"><div class="rmain"><span class="rt2">${{esc(a.title)}}</span>${{why}}</div><span class="chip ${{chipClass}}">${{esc(a.rword)}}</span></div>`;
}}
const STATUS_RANK = {{ ACTIVE:0, "APPLIED-PENDING-OPERATOR-E2E":1, PROPOSED:2, BLOCKED:3, DEFERRED:4, RESOLVED:5, CANCELLED:6 }};
function rowsFor(items) {{
  return items.slice().sort((a,b)=>(STATUS_RANK[a.status]??9)-(STATUS_RANK[b.status]??9) || a.id.localeCompare(b.id)).map(a=>itemRow(a)).join("");
}}

// status board grouped by surface
const bySurface = {{}};
for (const a of (DATA.actions||[])) {{ (bySurface[a.surface || "?"] ||= []).push(a); }}
document.getElementById("status-board").innerHTML = Object.keys(bySurface).sort().map(surf => {{
  const items = bySurface[surf];
  return `<div class="surf"><div class="stitle">Surface ${{esc(surf)}} <span class="ct">(${{items.length}})</span></div><div class="rows">${{rowsFor(items)}}</div></div>`;
}}).join("");

// post-Phase-8 register
const pp8 = DATA.post_phase_8 || {{}}, pp8g = pp8.groups || {{}};
const PP8_NAMES = {{ IV:"Multi-LLM (IV)", V:"Multi-deployment (V)", VI:"Multi-tenant (VI)", IX:"External integrations (IX)", X:"Research (X)", CXA:"Cross-axis seams" }};
document.getElementById("pp8-summary").innerHTML =
  `<strong>${{pp8.count||0}} forward items</strong> across ${{Object.keys(pp8g).length}} groups, full detail at <code>${{esc(pp8.register||"")}}</code>. Phase 8 closed the substitution accounting; these are the activation / deployment / integration axis, tracked under the same R-NNN discipline.`;
document.getElementById("pp8-board").innerHTML = Object.keys(pp8g).sort().map(g => {{
  const items = pp8g[g];
  return `<div class="surf"><div class="stitle">${{esc(PP8_NAMES[g]||g)}} <span class="ct">(${{items.length}})</span></div><div class="rows">${{rowsFor(items)}}</div></div>`;
}}).join("");

// PRs
const prs = DATA.open_prs || [];
document.getElementById("prs").innerHTML = prs.length ? prs.map(p =>
  `<div class="pr"><span class="num">#${{p.number}}</span><span class="dot ${{p.ci}}">●</span><span>${{esc(p.title)}} ${{p.draft?'<span class="muted">(draft)</span>':''}}</span></div>`
).join("") : '<div class="muted">none open</div>';

// gates
const gates = DATA.operator_gates || [];
document.getElementById("gates").innerHTML = gates.length ? gates.map(g =>
  `<div class="gate"><b>${{esc(g.id)}}</b> &nbsp; ${{mdLite(g.gate)}}</div>`
).join("") : '<div class="muted">none</div>';

// recently completed
document.getElementById("recent").innerHTML = (d.recently_completed || []).map(rc =>
  `<div class="recent"><span class="rh">${{esc(rc.pr)}}</span><span class="rd mono">${{esc(rc.date)}}</span><div class="rn2">${{mdLite(rc.note)}}</div></div>`
).join("");

document.getElementById("drift-count").textContent = d.drift_log_count ?? 0;

// cadence — instrument-ledger restyle (amber bars on dark ground)
const cad = DATA.cadence || [];
new Chart(document.getElementById("cadence"), {{
  type: "bar",
  data: {{ labels: cad.map(x=>x.date.slice(5)), datasets:[{{ data: cad.map(x=>x.count), backgroundColor:"#f0a830", borderRadius:1 }}] }},
  options: {{ plugins:{{legend:{{display:false}}}}, animation:false,
    scales:{{ x:{{ ticks:{{color:"#7d745f",maxTicksLimit:8,font:{{size:9,family:"'JetBrains Mono',monospace"}}}},grid:{{display:false}} }},
              y:{{ ticks:{{color:"#7d745f",precision:0,font:{{family:"'JetBrains Mono',monospace"}}}},grid:{{color:"#2a251e"}} }} }} }}
}});

// ---- R-XI-02: dependency graph (Mermaid) + click-to-inspect schema panel ----
(function() {{
  const dg = DATA.depgraph || {{}};
  const host = document.getElementById("depgraph");
  const panel = document.getElementById("dep-panel");
  if (!host || !dg.mermaid || typeof mermaid === "undefined") {{
    if (host) host.innerHTML = '<div class="muted">dependency graph unavailable</div>';
    return;
  }}
  const CHIPMAP = {{ RESOLVED:"closed", CANCELLED:"closed", ACTIVE:"open", BLOCKED:"blocked", DEFERRED:"deferred", PROPOSED:"proposed", "APPLIED-PENDING-OPERATOR-E2E":"open" }};
  // Mermaid securityLevel:'loose' callback — arg is the node id ("nK").
  window.nodeClick = function(nid) {{
    const s = (dg.schema || {{}})[nid];
    if (!s || !panel) return;
    const list = (arr) => (arr && arr.length) ? arr.map(x=>`<code>${{esc(x)}}</code>`).join(" ") : '<span class="muted">none</span>';
    const mp = (s.must_pass && s.must_pass.length)
      ? `<ul class="mp">${{s.must_pass.map(x=>`<li>${{esc(x)}}</li>`).join("")}}</ul>`
      : '<span class="muted">none listed</span>';
    panel.hidden = false;
    // Markup hierarchy authored by the 4-skill elevation loop (R-XI-02):
    // lead with the human-readable title; demote the R-NNN id + status to
    // metadata below it. Carbonize-safe — reuses existing classes, no new CSS.
    panel.innerHTML = `
      <div class="dp-title">${{esc(s.title)}}</div>
      <div class="dp-head"><span class="dp-id">${{esc(s.id)}}</span>
        <span class="chip ${{CHIPMAP[s.status]||'other'}}">${{esc(s.status||'')}}</span>
        <span class="muted">Surface ${{esc(s.surface||'?')}} · ${{esc(s.posture||'')}}</span></div>
      <div class="dp-grid">
        <div><span class="lab">depends on</span> ${{list(s.depends_on)}}</div>
        <div><span class="lab">blocks</span> ${{list(s.blocks)}}</div>
        <div><span class="lab">advisor</span> ${{s.advisor ? esc(s.advisor) : '<span class="muted">no</span>'}}</div>
        <div><span class="lab">council</span> ${{s.council ? esc(s.council) : '<span class="muted">no</span>'}}</div>
      </div>
      <div class="lab">must pass</div>${{mp}}`;
    panel.scrollIntoView({{ behavior:"smooth", block:"nearest" }});
  }};
  try {{
    mermaid.initialize({{ startOnLoad:false, securityLevel:"loose", theme:"dark",
      themeVariables:{{ fontFamily:"'JetBrains Mono', monospace", fontSize:"12px",
        lineColor:"#3a342a", primaryColor:"#1c1812", primaryTextColor:"#b3a98f" }} }});
    host.textContent = dg.mermaid;
    host.classList.add("mermaid");
    Promise.resolve(mermaid.run({{ nodes:[host] }})).catch(() => {{
      host.innerHTML = '<div class="muted">dependency graph unavailable</div>';
    }});
  }} catch (e) {{
    host.innerHTML = '<div class="muted">dependency graph unavailable</div>';
  }}
}})();

// ---- R-XI-02: PR-merge cadence (last 30 days) ----
(function() {{
  const el = document.getElementById("pr-cadence"); if (!el) return;
  const pc = DATA.pr_cadence || [];
  new Chart(el, {{
    type: "bar",
    data: {{ labels: pc.map(x=>x.date.slice(5)), datasets:[{{ data: pc.map(x=>x.count), backgroundColor:"#f0a830", borderRadius:1 }}] }},
    options: {{ plugins:{{legend:{{display:false}}}}, animation:false,
      scales:{{ x:{{ ticks:{{color:"#7d745f",maxTicksLimit:8,font:{{size:9,family:"'JetBrains Mono',monospace"}}}},grid:{{display:false}} }},
                y:{{ ticks:{{color:"#7d745f",precision:0,font:{{family:"'JetBrains Mono',monospace"}}}},grid:{{color:"#2a251e"}} }} }} }}
  }});
}})();

// ---- R-XI-02: RETIRED-count trend (cumulative, from retirement-batch files) ----
(function() {{
  const el = document.getElementById("retired-trend"); if (!el) return;
  const rt = DATA.retired_trend || [];
  new Chart(el, {{
    type: "line",
    data: {{ labels: rt.map(x=>"b"+x.batch), datasets:[{{ data: rt.map(x=>x.retired),
      borderColor:"#f0a830", backgroundColor:"rgba(240,168,48,0.12)", fill:true, tension:0.25, pointRadius:0, borderWidth:2 }}] }},
    options: {{ plugins:{{ legend:{{display:false}},
      tooltip:{{ callbacks:{{ title:(it)=>{{ const p=rt[it[0].dataIndex]||{{}}; return `batch ${{p.batch}} · ${{p.date||'—'}}`; }}, label:(it)=>`retired ${{it.raw}}/54` }} }} }},
      animation:false,
      scales:{{ x:{{ ticks:{{color:"#7d745f",maxTicksLimit:10,font:{{size:9,family:"'JetBrains Mono',monospace"}}}},grid:{{display:false}} }},
                y:{{ ticks:{{color:"#7d745f",precision:0,font:{{family:"'JetBrains Mono',monospace"}}}},grid:{{color:"#2a251e"}},suggestedMin:0,suggestedMax:54 }} }} }}
  }});
}})();

// ---- R-XI-03: live-update mode (short-poll; static-deploy-friendly) ----
(function() {{
  const ind = document.getElementById("ro-live");
  const meta = document.querySelector('meta[name="dashboard-live-head"]');
  const cur = meta ? (meta.getAttribute("content") || "") : "";
  const POLL_MS = 45000;
  const pad = (n) => String(n).padStart(2, "0");
  const stamp = () => {{ const t = new Date(); return pad(t.getHours()) + ":" + pad(t.getMinutes()) + ":" + pad(t.getSeconds()); }};
  const setInd = (txt, cls) => {{ if (ind) {{ ind.textContent = txt; ind.className = "live-ind " + (cls || ""); }} }};
  try {{
    if ("scrollRestoration" in history) history.scrollRestoration = "manual";
    const y = sessionStorage.getItem("dash-scroll");
    if (y !== null) {{ window.scrollTo(0, parseInt(y, 10) || 0); sessionStorage.removeItem("dash-scroll"); }}
  }} catch (e) {{}}
  if (!cur || !ind) {{ setInd("● off", "off"); return; }}
  setInd("● live · " + stamp(), "on");
  async function check() {{
    if (document.hidden) return;
    try {{
      const r = await fetch(location.pathname + "?_lc=" + Date.now(), {{ cache: "no-store" }});
      const txt = await r.text();
      const fm = new DOMParser().parseFromString(txt, "text/html").querySelector('meta[name="dashboard-live-head"]');
      const fresh = fm ? (fm.getAttribute("content") || "") : "";
      if (fresh && fresh !== cur) {{
        setInd("↻ new data · refreshing", "upd");
        try {{ sessionStorage.setItem("dash-scroll", String(window.scrollY | 0)); }} catch (e) {{}}
        setTimeout(() => location.reload(), 600);
      }} else {{
        setInd("● live · " + stamp(), "on");
      }}
    }} catch (e) {{
      setInd("● live · retry", "on");
    }}
  }}
  setInterval(check, POLL_MS);
}})();
</script>
</body>
</html>
"""


def render_html(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False, indent=None)
    # Escape any `</script>` that could appear inside string values.
    payload = payload.replace("</", "<\\/")
    # The template is authored with doubled braces ({{ }}) for readability/lint
    # parity; collapse them to single braces BEFORE injecting the payload so the
    # payload's own JSON braces are never disturbed. (We render via .replace, not
    # str.format, so no real escaping is needed — this is a pure de-double.)
    tmpl = HTML_TEMPLATE.replace("{{", "{").replace("}}", "}")
    tmpl = tmpl.replace("__LIVE_HEAD__", str(data.get("live_head", "")))
    return tmpl.replace("__DATA__", payload)


# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# Source 6 — post-Phase-8 forward register (forward surfaces + CXA seams).
# --------------------------------------------------------------------------- #

_FORWARD_SURFACES = {"IV", "V", "VI", "IX", "X"}


def post_phase_8(actions: list[dict]) -> dict:
    """Forward-activation items: forward surfaces {IV,V,VI,IX,X} + CXA seams.

    Tracks `.harness/post-phase-8-forward-register.md` under the same R-NNN
    discipline as all prior work — these items flow through next-action
    derivation + memory-on-close like any other roadmap entry.
    """
    items = [
        a for a in actions if a.get("surface") in _FORWARD_SURFACES or a["id"].startswith("R-CXA")
    ]
    groups: dict[str, list[dict]] = {}
    for a in items:
        label = "CXA" if a["id"].startswith("R-CXA") else (a.get("surface") or "?")
        groups.setdefault(label, []).append(a)
    return {
        "register": ".harness/post-phase-8-forward-register.md",
        "count": len(items),
        "groups": groups,
    }


def build(root: Path) -> dict:
    dash_md = (root / ".harness" / "roadmap_status.md").read_text(encoding="utf-8")
    roadmap_md = (root / "Project_Roadmap_v1.md").read_text(encoding="utf-8")
    actions = parse_roadmap_actions(roadmap_md)
    # attach display annotations (closed/open/other + one-line why) per item
    for a in actions:
        disp = STATUS_DISPLAY.get(a["status"], {"kind": "other", "word": a["status"].lower()})
        a["rkind"] = disp["kind"]
        a["rword"] = disp["word"]
        a["why"] = ANNOTATIONS.get(a["id"], "")
    dashboard = parse_dashboard(dash_md)
    return {
        "live_head": _run(["git", "rev-parse", "--short=12", "HEAD"], cwd=root).strip(),
        "dashboard": dashboard,
        "actions": actions,
        "open_prs": parse_open_prs(root),
        "cadence": parse_cadence(root),
        "pr_cadence": parse_pr_cadence(root),
        "retired_trend": parse_retired_trend(root),
        "depgraph": build_depgraph(actions),
        "axis_retirement": parse_axis_retirement(root),
        "operator_gates": operator_gates(actions, dashboard),
        "post_phase_8": post_phase_8(actions),
        "closure": compute_closure(actions, dashboard),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate the operator roadmap dashboard.")
    ap.add_argument("--root", default=".", help="workspace root (default: cwd)")
    ap.add_argument(
        "--out",
        default="tools/dashboard/roadmap.html",
        help="output HTML path (relative to --root)",
    )
    args = ap.parse_args()
    root = Path(args.root).resolve()
    data = build(root)
    out = root / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_html(data), encoding="utf-8")
    n = len(data["actions"])
    rp = data["dashboard"].get("retirement", {})
    print(
        f"wrote {out} — {n} R-NNN actions, "
        f"{len(data['open_prs'])} open PRs, "
        f"retirement {rp.get('retired', '?')}/{rp.get('total', '?')}"
    )


if __name__ == "__main__":
    main()
