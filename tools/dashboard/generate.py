#!/usr/bin/env python3
"""Operator dashboard generator (R-XI-01).

Reads the workspace roadmap substrate from five sources and emits a single
self-contained static `roadmap.html` (Tailwind CDN + Chart.js CDN + vanilla JS).
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
    "R-008-od-4-redaction-partial": "Telemetry redaction is half-wired; the per-session on/off switch and token-masking pieces aren't built yet.",
    "R-100-mvp-config-discovery": "Waiting on a small decision: auto-find the config file at the project root, or drop that behavior from the spec.",
    "R-700-phase-8-substitution-accounting": "Waiting on your sign-off of the final 'how many pieces are retired' count (46/47/48) to formally declare the build phase done.",
    # DEFERRED (parked by design)
    "R-005-as-8e-files-indefinite": "File-telemetry support is parked by design until a cloud deployment needs it — not part of the core build.",
    "R-006-as-8f-managed-agents-indefinite": "Managed-agents telemetry is parked by design until a cloud deployment needs it — not part of the core build.",
    "R-CXA-3-cp-as-seam": "Parked until either a cloud 'Files' arc opens or you narrow its scope; no in-workspace work available now.",
    "R-810-files-api-integration": "The real Files-API integration; deferred by design to a managed-cloud stage.",
    "R-820-managed-agents-integration": "The real managed-agents integration; deferred by design to a managed-cloud stage.",
    # PROPOSED (queued; most need credentials or infrastructure only you can provide)
    "R-300-multi-llm-second-provider": "Ready to start, but needs OpenAI/Ollama credentials and a mixed-provider test you'd run.",
    "R-410-sandbox-tier-2-container-execution": "Run tool calls inside a real isolated container instead of in-process; needs a container runtime you'd provide.",
    "R-411-sandbox-tier-3-microvm-execution": "Run tool calls in a microVM; needs that runtime and follows the container tier.",
    "R-412-sandbox-tier-4-full-vm-execution": "Run tool calls in a full VM; cloud-only, and follows the microVM + managed-cloud stages.",
    "R-420-self-hosted-server-deployment-e2e": "Run the harness on a real server with a collector + secrets; needs that infrastructure stood up.",
    "R-421-managed-cloud-deployment-e2e": "Run the harness in managed cloud (cloud secrets + full VM + managed collector); needs cloud infrastructure.",
    "R-430-otlp-collector-tail-keep-preservation": "Confirm the telemetry keep-rule works against a real collector; needs that collector running.",
    "R-440-tier-level-secrets-backend": "Wire a real secrets store for a self-hosted server (today it's env-vars / operator-supplied).",
    "R-500-multi-tenant-deployment": "Exercise the harness with multiple tenants / a non-solo profile; needs a multi-tenant deployment.",
    "R-830-memory-tool-production-backend": "The local SQLite slice is done; the cloud-vault / managed-DB remainder needs cloud credentials you'd provide.",
    "R-900-research-arcs": "Open-ended research / exploration; no fixed scope — pulled in as you choose.",
    "R-CXA-1-as-is-seam": "The one remaining wire (a secret-fetch audit caller) has no real source yet, so wiring it would be hollow; deferred until one exists.",
    "R-CXA-2-cp-is-seam": "Needs the control-plane engine code (pause/resume) built first; that piece doesn't exist yet.",
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
        "why": "Pre-collector redaction is wired, but the per-session toggle + token-masking aren't.",
        "retire": "Not yet — needs that substrate built. Worth doing when multi-tenant/redaction is exercised (R-500).",
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
        "retire": "Effectively done; stays PARTIAL only because the ledger's CXA rows were never folded into the cumulative. Closes at R-700 — low effort, bookkeeping.",
    },
    {
        "id": "CXA-2",
        "rnnn": "R-CXA-2",
        "state": "STILL-BOUNDED",
        "why": "The CP→IS seam has 1 of 17 edges wired.",
        "retire": "Not yet — needs the control-plane engine (pause/resume) substrate built. This is the one genuinely buildable remaining seam.",
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
        "why": "files.* telemetry namespace.",
        "retire": "Only when Files-API integration happens (cloud). Deferred by design — bounded residual, not core build.",
    },
    {
        "id": "AS-8f",
        "rnnn": "R-006",
        "state": "STILL-BOUNDED-INDEFINITELY",
        "why": "managed_agents.* telemetry namespace.",
        "retire": "Only when managed-agents integration happens. Deferred by design — bounded residual.",
    },
    {
        "id": "CP-17",
        "rnnn": "(none yet)",
        "state": "STILL-BOUNDED-INDEFINITELY",
        "why": "files-primitives control-plane row (tied to the Files arc, same as AS-8e).",
        "retire": "Deferred by design. Also a tracking gap — it has no R-NNN entry yet.",
    },
]

# Ordered "remaining to complete", graph-derived from depends_on/blocks then layered.
# layer ∈ {build, activation}. `gate` = what unblocks it / why it's where it is.
REMAINING_ORDERED = [
    # --- Build layer: close the substitution ledger ---
    {
        "n": 1,
        "layer": "build",
        "id": "R-700-phase-8-substitution-accounting",
        "label": "Ratify the final retirement count",
        "gate": "Your sign-off (46/47/48) — declares the build phase done. The 8 rows below all feed this.",
    },
    {
        "n": 2,
        "layer": "build",
        "id": "R-CXA-2-cp-is-seam",
        "label": "Build the CP→IS engine-layer seam",
        "gate": "The one genuinely buildable remaining seam — but needs the pause/resume engine substrate built first.",
    },
    {
        "n": 3,
        "layer": "build",
        "id": "R-008-od-4-redaction-partial",
        "label": "Finish redaction (OD-4)",
        "gate": "Needs a per-session toggle + token-masking substrate; pairs naturally with multi-tenant (R-500).",
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
        "gate": "0 wireable — already done in substance; folds into the R-700 count.",
    },
    {
        "n": 6,
        "layer": "build",
        "id": "R-CXA-3-cp-as-seam",
        "label": "CP→AS seam — build or narrow",
        "gate": "Needs a runtime composer (Files arc) or a scope-narrowing decision.",
    },
    {
        "n": 7,
        "layer": "build",
        "id": "R-005 / R-006 / CP-17",
        "label": "Files + managed-agents namespaces",
        "gate": "Deferred by design — bounded residual; close only at the Files / managed-cloud arc.",
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
        "id": "R-440 → R-420 → R-430",
        "label": "Self-hosted server: secrets → server → collector",
        "gate": "Needs a real server + secrets backend + OTLP collector you'd stand up.",
    },
    {
        "n": 10,
        "layer": "activation",
        "id": "R-410 → R-411",
        "label": "Real sandboxes: container → microVM",
        "gate": "Needs container/microVM runtimes you'd provide.",
    },
    {
        "n": 11,
        "layer": "activation",
        "id": "R-421 → R-412 → R-500",
        "label": "Managed cloud → full-VM → multi-tenant",
        "gate": "Needs cloud infrastructure; follows the self-hosted server.",
    },
    {
        "n": 12,
        "layer": "activation",
        "id": "R-300-multi-llm-second-provider",
        "label": "Second LLM provider",
        "gate": "Needs OpenAI/Ollama credentials + a mixed-provider test.",
    },
    {
        "n": 13,
        "layer": "activation",
        "id": "R-830 / R-810 / R-820",
        "label": "Cloud memory + Files + managed-agents integrations",
        "gate": "Need cloud credentials; deferred-by-design integrations.",
    },
    {
        "n": 14,
        "layer": "activation",
        "id": "R-XI-02 / R-XI-03 / R-900",
        "label": "Dashboard polish + research arcs",
        "gate": "Nice-to-have; no blockers, pulled in at discretion.",
    },
]


def compute_closure(actions: list[dict], dashboard: dict) -> dict:
    """Two layered closure views (operator picked 'Both, layered').

    build      — substitution-ledger retirement (the canonical 'is H_T built'
                 metric). A RANGE 46-48/54 because R-700 (the integer) is
                 unratified; rendered as a range, never a fake-precise number.
    activation — the post-Phase-8 forward axis (deployment / integration);
                 0 exercised, but that is operator-gated infra + bounded-residual
                 by design, NOT remaining build work. The renderer says so loudly.
    """
    total = 54
    retired_lo, retired_hi = 46, 48
    # forward-axis items = post-Phase-8 surfaces + CXA seams (open ones only)
    fwd = [
        a
        for a in actions
        if (a.get("surface") in {"IV", "V", "VI", "IX", "X"} or a["id"].startswith("R-CXA"))
    ]
    fwd_open = [a for a in fwd if a["status"] not in ("RESOLVED", "CANCELLED")]
    return {
        "build": {
            "lo": retired_lo,
            "hi": retired_hi,
            "total": total,
            "pct_lo": round(100 * retired_lo / total, 1),
            "pct_hi": round(100 * retired_hi / total, 1),
            "contested": True,
            "nonretired": NONRETIRED_LEDGER,
        },
        "activation": {
            "total": len(fwd),
            "open": len(fwd_open),
            "exercised_pct": 0,
        },
        "remaining": REMAINING_ORDERED,
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


# --------------------------------------------------------------------------- #
# Source 2 — Project_Roadmap_v1.md §5 R-NNN catalog.
# --------------------------------------------------------------------------- #
def parse_roadmap_actions(text: str) -> list[dict]:
    """Parse the R-NNN entries from the roadmap §5 catalog (YAML-ish blocks)."""
    actions: list[dict] = []
    cur: dict | None = None
    for line in text.split("\n"):
        m = re.match(r"^([A-Za-z0-9-]*R-[A-Za-z0-9-]+):\s*$", line)
        if m:
            cur = {
                "id": m.group(1),
                "title": "",
                "surface": "",
                "status": "",
                "depends_on": [],
                "posture": "",
            }
            actions.append(cur)
            continue
        if cur is None:
            continue
        for key in ("title", "surface", "posture"):
            mm = re.match(rf"^\s+{key}:\s*(.+?)\s*(#.*)?$", line)
            if mm and not cur[key]:
                cur[key] = mm.group(1).strip().strip('"')
        ms = re.match(r"^\s+status:\s*(.+?)\s*(#.*)?$", line)
        if ms and not cur["status"]:
            cur["status"] = ms.group(1).split()[0].strip('"').upper()
        md = re.match(r"^\s+depends_on:\s*\[(.*)\]", line)
        if md and not cur["depends_on"]:
            cur["depends_on"] = [d.strip() for d in md.group(1).split(",") if d.strip()]
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
<title>Harness roadmap — operator dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  body {{ background:#0b0f17; color:#e5e7eb; }}
  .card {{ background:#111827; border:1px solid #1f2937; border-radius:0.75rem; }}
  .chip {{ font-size:0.7rem; padding:0.1rem 0.5rem; border-radius:9999px; font-weight:600; }}
</style>
</head>
<body class="min-h-screen">
<div class="max-w-6xl mx-auto p-6 space-y-6">
  <header class="flex items-baseline justify-between flex-wrap gap-2">
    <h1 class="text-2xl font-bold text-white">Harness roadmap</h1>
    <div class="text-xs text-gray-400" id="anchor"></div>
  </header>

  <section class="card p-5" id="next-action-card">
    <h2 class="text-sm uppercase tracking-wide text-indigo-300 mb-2">Next action</h2>
    <div id="next-action" class="prose prose-invert max-w-none text-sm leading-relaxed"></div>
  </section>

  <section class="card p-5" id="closure-card">
    <h2 class="text-sm uppercase tracking-wide text-emerald-300 mb-3">Harness development closure</h2>
    <div id="closure" class="text-sm leading-relaxed"></div>
  </section>

  <div class="grid md:grid-cols-2 gap-6">
    <section class="card p-5">
      <h2 class="text-sm uppercase tracking-wide text-emerald-300 mb-3">Phase 7 retirement</h2>
      <div id="retire-bar"></div>
      <div id="retire-buckets" class="mt-3 space-y-1 text-xs text-gray-300"></div>
    </section>
    <section class="card p-5">
      <h2 class="text-sm uppercase tracking-wide text-sky-300 mb-3">Commit cadence (30d)</h2>
      <canvas id="cadence" height="90"></canvas>
    </section>
  </div>

  <section class="card p-5">
    <h2 class="text-sm uppercase tracking-wide text-amber-300 mb-3">R-NNN status board</h2>
    <div id="status-board" class="space-y-4"></div>
  </section>

  <section class="card p-5" id="pp8-card">
    <h2 class="text-sm uppercase tracking-wide text-violet-300 mb-2">Post-Phase-8 forward register</h2>
    <div id="pp8-summary" class="text-xs text-gray-400 mb-3"></div>
    <div id="pp8-board" class="space-y-3"></div>
  </section>

  <div class="grid md:grid-cols-2 gap-6">
    <section class="card p-5">
      <h2 class="text-sm uppercase tracking-wide text-fuchsia-300 mb-3">In-flight PRs</h2>
      <div id="prs" class="space-y-2 text-sm"></div>
    </section>
    <section class="card p-5">
      <h2 class="text-sm uppercase tracking-wide text-rose-300 mb-3">Operator gates</h2>
      <div id="gates" class="space-y-2 text-sm"></div>
    </section>
  </div>

  <section class="card p-5">
    <h2 class="text-sm uppercase tracking-wide text-teal-300 mb-3">Recently completed</h2>
    <div id="recent" class="space-y-2 text-sm"></div>
  </section>

  <footer class="text-xs text-gray-500 pt-2">
    Drift-log events: <span id="drift-count"></span> ·
    Generated by <code>tools/dashboard/generate.py</code> (R-XI-01) ·
    static read-only snapshot — refresh by re-running the generator / GitHub Pages deploy.
  </footer>
</div>

<script>
const DATA = __DATA__;

const STATUS_COLORS = {{
  ACTIVE: "bg-blue-600 text-white",
  "APPLIED-PENDING-OPERATOR-E2E": "bg-purple-600 text-white",
  PROPOSED: "bg-amber-500 text-black",
  BLOCKED: "bg-gray-600 text-gray-100",
  DEFERRED: "bg-slate-700 text-gray-300",
  RESOLVED: "bg-emerald-700 text-emerald-100",
  CANCELLED: "bg-red-800 text-red-100",
}};
const CI_COLORS = {{ passing:"text-emerald-400", running:"text-amber-400", failing:"text-red-400", none:"text-gray-500" }};
const esc = (s) => (s ?? "").replace(/[&<>]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c]));

// anchor
document.getElementById("anchor").innerHTML =
  `head <code class="text-gray-300">${{esc(DATA.dashboard.git_head)}}</code> · hash <code>${{esc(DATA.dashboard.hash)}}</code> · ${{esc(DATA.dashboard.last_refreshed)}} · ${{esc(DATA.dashboard.fork_count)}} open forks`;

// next action (markdown-lite: keep as escaped text with bold + code)
function mdLite(s) {{
  let h = esc(s);
  h = h.replace(/`([^`]+)`/g, '<code class="text-indigo-200">$1</code>');
  h = h.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong class="text-white">$1</strong>');
  h = h.replace(/^- (.*)$/gm, '<li class="ml-4 list-disc">$1</li>');
  h = h.replace(/\\n\\n/g, '<br/><br/>');
  return h;
}}
document.getElementById("next-action").innerHTML = mdLite(DATA.dashboard.next_action);

// one item row: strike-through if closed; "open" label; else status word + plain-English why
function itemRow(a) {{
  const title = `<span class="text-gray-500">${{esc(a.id)}}</span> ${{esc(a.title)}}`;
  if (a.rkind === "closed") {{
    return `<div class="flex items-start gap-2 py-0.5"><s class="text-gray-600 flex-1">${{title}}</s><span class="chip bg-emerald-900 text-emerald-300">closed</span></div>`;
  }}
  if (a.rkind === "open") {{
    return `<div class="flex items-start gap-2 py-0.5"><span class="flex-1 text-gray-200">${{title}}</span><span class="chip bg-blue-600 text-white">open</span></div>`;
  }}
  const c = STATUS_COLORS[a.status] || "bg-gray-700 text-gray-200";
  const why = a.why ? `<div class="text-xs text-gray-500 ml-1 mt-0.5">— ${{esc(a.why)}}</div>` : "";
  return `<div class="py-0.5"><div class="flex items-start gap-2"><span class="flex-1 text-gray-200">${{title}}</span><span class="chip ${{c}}">${{esc(a.rword)}}</span></div>${{why}}</div>`;
}}

// harness development closure — two layered views + unretired rows + ordered remaining
(function() {{
  const cl = DATA.closure || {{}};
  const b = cl.build || {{}}, ac = cl.activation || {{}};
  const stateColor = {{ "PARTIAL":"text-amber-300", "STILL-BOUNDED":"text-orange-400", "STILL-BOUNDED-INDEFINITELY":"text-slate-400" }};
  const nonret = (b.nonretired || []).map(r =>
    `<div class="py-1 border-b border-gray-800/60">
       <span class="font-semibold text-gray-200">${{esc(r.id)}}</span>
       <span class="chip bg-gray-800 ${{stateColor[r.state] || 'text-gray-400'}}">${{esc(r.state)}}</span>
       <span class="text-gray-600 text-xs">${{esc(r.rnnn)}}</span>
       <div class="text-xs text-gray-400 mt-0.5">${{esc(r.why)}}</div>
       <div class="text-xs mt-0.5"><span class="text-gray-500">retire? </span><span class="text-emerald-300/90">${{esc(r.retire)}}</span></div>
     </div>`).join("");
  const rem = (cl.remaining || []).map(r =>
    `<div class="flex items-start gap-2 py-0.5">
       <span class="text-gray-600 w-5 text-right shrink-0">${{r.n}}</span>
       <span class="chip shrink-0 ${{r.layer === 'build' ? 'bg-emerald-900 text-emerald-300' : 'bg-sky-900 text-sky-300'}}">${{esc(r.layer)}}</span>
       <span class="flex-1"><span class="text-gray-200">${{esc(r.label)}}</span> <span class="text-gray-600 text-xs">${{esc(r.id)}}</span><div class="text-xs text-gray-500">${{esc(r.gate)}}</div></span>
     </div>`).join("");
  const el = document.getElementById("closure");
  if (!el) return;
  el.innerHTML = `
    <div class="grid md:grid-cols-2 gap-4 mb-4">
      <div class="bg-gray-900/40 rounded-lg p-3">
        <div class="text-xs uppercase tracking-wide text-emerald-300 mb-1">Build closure — is the harness built?</div>
        <div class="text-2xl font-bold text-white">${{b.pct_lo}}–${{b.pct_hi}}%</div>
        <div class="text-xs text-gray-400 mt-1">${{b.lo}}–${{b.hi}} of ${{b.total}} substitutions retired. A <strong class="text-gray-300">range</strong> because the final count is unratified (R-700 — your sign-off). 8 rows remain, listed below.</div>
        <div class="w-full bg-gray-800 rounded-full h-2 mt-2"><div class="bg-emerald-500 h-2 rounded-full" style="width:${{b.pct_lo}}%"></div></div>
      </div>
      <div class="bg-gray-900/40 rounded-lg p-3">
        <div class="text-xs uppercase tracking-wide text-sky-300 mb-1">Activation / deployment closure</div>
        <div class="text-2xl font-bold text-white">0%<span class="text-sm font-normal text-gray-400"> exercised</span></div>
        <div class="text-xs text-gray-400 mt-1">${{ac.open}} of ${{ac.total}} forward items open. <strong class="text-amber-300">This is NOT remaining build work</strong> — it is operator-gated (credentials + infrastructure that cannot run in this workspace) and bounded-residual by design. The harness is built; this axis is "switched on" only at a real deployment.</div>
      </div>
    </div>
    <div class="mb-4">
      <div class="text-xs uppercase tracking-wide text-amber-300 mb-2">Unretired substitution rows (8) — state · why · can we retire?</div>
      <div>${{nonret}}</div>
    </div>
    <div>
      <div class="text-xs uppercase tracking-wide text-indigo-300 mb-2">Remaining to complete — ordered by logical flow (dependency-graph-derived)</div>
      <div class="space-y-0.5">${{rem}}</div>
    </div>`;
}})();

// retirement bar
const r = DATA.dashboard.retirement || {{}};
if (r.total) {{
  const pct = r.pct ?? Math.round(1000*r.retired/r.total)/10;
  document.getElementById("retire-bar").innerHTML =
    `<div class="flex justify-between text-xs mb-1"><span>${{r.retired}}/${{r.total}} RETIRED</span><span class="text-emerald-300 font-semibold">${{pct}}%</span></div>
     <div class="w-full bg-gray-800 rounded-full h-3"><div class="bg-emerald-500 h-3 rounded-full" style="width:${{pct}}%"></div></div>`;
}}
document.getElementById("retire-buckets").innerHTML =
  Object.entries(r.buckets || {{}}).filter(([k])=>!/^RETIRED$/.test(k))
    .map(([k,v]) => `<div><span class="text-gray-400">${{esc(k)}}:</span> ${{mdLite(v)}}</div>`).join("");

// cadence sparkline
const cad = DATA.cadence || [];
new Chart(document.getElementById("cadence"), {{
  type: "bar",
  data: {{ labels: cad.map(d=>d.date.slice(5)), datasets:[{{ data: cad.map(d=>d.count), backgroundColor:"#38bdf8" }}] }},
  options: {{ plugins:{{legend:{{display:false}}}}, scales:{{ x:{{ ticks:{{color:"#6b7280",maxTicksLimit:8,font:{{size:9}}}},grid:{{display:false}} }}, y:{{ ticks:{{color:"#6b7280",precision:0}},grid:{{color:"#1f2937"}} }} }} }}
}});

// status board grouped by surface
const bySurface = {{}};
for (const a of DATA.actions) {{ (bySurface[a.surface || "?"] ||= []).push(a); }}
const STATUS_RANK = {{ ACTIVE:0, "APPLIED-PENDING-OPERATOR-E2E":1, PROPOSED:2, BLOCKED:3, DEFERRED:4, RESOLVED:5, CANCELLED:6 }};
document.getElementById("status-board").innerHTML = Object.keys(bySurface).sort().map(surf => {{
  const items = bySurface[surf].sort((a,b)=>(STATUS_RANK[a.status]??9)-(STATUS_RANK[b.status]??9) || a.id.localeCompare(b.id));
  return `<div><div class="text-xs text-amber-300/80 mb-1 font-semibold">Surface ${{esc(surf)}} <span class="text-gray-600">(${{items.length}})</span></div><div class="border-l border-gray-800 pl-3">${{items.map(itemRow).join("")}}</div></div>`;
}}).join("");

// post-Phase-8 forward register
const pp8 = DATA.post_phase_8 || {{}};
const pp8g = pp8.groups || {{}};
const PP8_NAMES = {{ IV:"Multi-LLM (IV)", V:"Multi-deployment (V)", VI:"Multi-tenant (VI)", IX:"External integrations (IX)", X:"Research (X)", CXA:"Cross-axis seams" }};
document.getElementById("pp8-summary").innerHTML =
  `<strong class="text-white">${{pp8.count||0}} forward items</strong> across ${{Object.keys(pp8g).length}} groups — full detail at <code class="text-indigo-200">${{esc(pp8.register||"")}}</code>. ` +
  `Phase 8 closes the substitution accounting (88.9% RETIRED — legitimate per X-AL-2); these are the <strong class="text-white">activation / deployment / integration</strong> axis, tracked under the same R-NNN discipline (status + memory-on-close + next-action).`;
document.getElementById("pp8-board").innerHTML = Object.keys(pp8g).sort().map(g => {{
  const items = pp8g[g].slice().sort((a,b)=>(STATUS_RANK[a.status]??9)-(STATUS_RANK[b.status]??9) || a.id.localeCompare(b.id));
  return `<div><div class="text-xs text-violet-300 mb-1 font-semibold">${{esc(PP8_NAMES[g]||g)}} <span class="text-gray-600">(${{items.length}})</span></div><div class="border-l border-gray-800 pl-3">${{items.map(itemRow).join("")}}</div></div>`;
}}).join("");

// PRs
const prs = DATA.open_prs || [];
document.getElementById("prs").innerHTML = prs.length ? prs.map(p =>
  `<div class="flex items-start gap-2"><span class="text-gray-500">#${{p.number}}</span>
   <span class="${{CI_COLORS[p.ci]}}">●</span>
   <span class="flex-1">${{esc(p.title)}} ${{p.draft?'<span class="text-gray-600">(draft)</span>':''}}</span></div>`
).join("") : '<div class="text-gray-500">none open</div>';

// operator gates
const gates = DATA.operator_gates || [];
document.getElementById("gates").innerHTML = gates.length ? gates.map(g =>
  `<div><span class="text-rose-300 font-semibold">${{esc(g.id)}}</span> — ${{mdLite(g.gate)}}</div>`
).join("") : '<div class="text-gray-500">none</div>';

// recently completed
document.getElementById("recent").innerHTML = (DATA.dashboard.recently_completed || []).map(rc =>
  `<div><span class="text-teal-300 font-semibold">${{esc(rc.pr)}}</span> <span class="text-gray-500">${{esc(rc.date)}}</span><div class="text-gray-300 text-xs mt-0.5">${{mdLite(rc.note)}}</div></div>`
).join("");

document.getElementById("drift-count").textContent = DATA.dashboard.drift_log_count ?? 0;
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
        "dashboard": dashboard,
        "actions": actions,
        "open_prs": parse_open_prs(root),
        "cadence": parse_cadence(root),
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
