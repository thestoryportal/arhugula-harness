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
    # waffle-grid breakdown (ui-ux-pro-max chart rec: fraction-of-whole filled).
    # retired = conservative low (46); the 8 non-retired split by state → total 54.
    n_partial = sum(1 for r in NONRETIRED_LEDGER if r["state"] == "PARTIAL")
    n_sb = sum(1 for r in NONRETIRED_LEDGER if r["state"] == "STILL-BOUNDED")
    n_sbi = sum(1 for r in NONRETIRED_LEDGER if r["state"] == "STILL-BOUNDED-INDEFINITELY")
    return {
        "build": {
            "lo": retired_lo,
            "hi": retired_hi,
            "total": total,
            "pct_lo": round(100 * retired_lo / total, 1),
            "pct_hi": round(100 * retired_hi / total, 1),
            "contested": True,
            "nonretired": NONRETIRED_LEDGER,
            "waffle": {
                "retired": retired_lo,
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
<meta name="description" content="Multi-LLM agent harness — development closure, retirement ledger, and R-NNN roadmap at a glance."/>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%232B2620'/%3E%3Crect x='8' y='8' width='14' height='14' rx='2' fill='%23E0A82E'/%3E%3C/svg%3E"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root{{
    --mustard:#E0A82E; --paper:#F4EFE3; --paper-hi:#FBF8F1; --sand:#D8CFBC;
    --terracotta:#C25B3A; --ink:#2B2620; --ink-soft:#6B6354; --ink-faint:#9A8E76;
    --serif:Canela,Georgia,'Times New Roman',serif;
    --sans:Inter,'Helvetica Neue',Arial,sans-serif;
    --radius:10px; --shadow:6px 6px 0 var(--mustard); --shadow-sm:4px 4px 0 var(--mustard);
  }}
  *{{box-sizing:border-box;margin:0;padding:0;}}
  html{{scroll-behavior:smooth;}}
  body{{background:#E7E0D0;font-family:var(--sans);color:var(--ink);line-height:1.5;
    font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased;}}
  .wrap{{max-width:1160px;margin:0 auto;padding:0 24px 64px;}}
  .serif{{font-family:var(--serif);}}
  a{{color:inherit;}}

  /* topbar — ink ground, mustard type (premium/closing ground) */
  .topbar{{background:var(--ink);color:var(--mustard);}}
  .topbar .inner{{max-width:1160px;margin:0 auto;padding:18px 24px;display:flex;
    justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:10px;}}
  .topbar .brand{{font-family:var(--serif);font-size:22px;font-weight:500;letter-spacing:.3px;}}
  .topbar .brand em{{font-style:italic;color:#F0C766;}}
  .topbar .anchor{{font-size:11px;letter-spacing:1px;color:#C8941E;}}
  .topbar .anchor code{{color:#F0C766;}}

  /* numbered serif section header + hairline rule (signature motif D) */
  section{{margin-top:40px;}}
  .shead{{display:flex;align-items:baseline;gap:14px;margin-bottom:18px;}}
  .shead .num{{font-family:var(--serif);font-size:30px;font-weight:500;color:var(--mustard);line-height:1;}}
  .shead .htxt{{font-family:var(--serif);font-size:24px;font-weight:500;color:var(--ink);line-height:1;}}
  .shead .rule{{flex:1;border-top:1.5px solid var(--sand);transform:translateY(-6px);}}
  .label{{font-size:11px;letter-spacing:2.5px;text-transform:uppercase;color:var(--ink-faint);font-weight:700;}}

  /* cards — paper-on-paper + mustard offset shadow; dark variant inverts */
  .card{{background:var(--paper-hi);border:1px solid var(--sand);border-radius:var(--radius);
    box-shadow:var(--shadow);padding:22px;}}
  .card.dark{{background:var(--ink);color:var(--paper);box-shadow:var(--shadow);}}
  .grid2{{display:grid;grid-template-columns:1fr 1fr;gap:22px;}}
  .grid-hero{{display:grid;grid-template-columns:1fr 1fr;gap:22px;align-items:stretch;}}

  /* stat cards (closure hero) */
  .stat .k{{font-size:11px;letter-spacing:2px;text-transform:uppercase;font-weight:700;margin-bottom:8px;}}
  .stat.build .k{{color:#7a5a12;}}
  .stat .big{{font-family:var(--serif);font-size:46px;font-weight:500;line-height:.95;}}
  .stat .big .unit{{font-size:18px;color:var(--ink-soft);font-family:var(--sans);font-weight:600;}}
  .stat .sub{{font-size:12.5px;color:var(--ink-soft);margin-top:8px;line-height:1.6;}}
  .stat .sub strong{{color:var(--ink);}}
  .bar{{height:8px;border-radius:6px;background:var(--sand);margin-top:12px;overflow:hidden;}}
  .bar > span{{display:block;height:100%;background:var(--mustard);}}
  .pull{{font-family:var(--serif);font-style:italic;font-size:16px;color:var(--terracotta);
    margin-top:10px;line-height:1.3;}}

  /* waffle — 54 substitution cells, fraction-of-whole-filled (ui-ux-pro-max rec) */
  .waffle{{display:grid;grid-template-columns:repeat(18,1fr);gap:4px;margin-top:6px;max-width:520px;}}
  .cell{{aspect-ratio:1;border-radius:3px;background:var(--sand);}}
  .cell.retired{{background:var(--mustard);}}
  .cell.partial{{background:var(--terracotta);}}
  .cell.bounded{{background:var(--ink-soft);}}
  .cell.indef{{background:var(--sand);border:1px dashed var(--ink-faint);}}
  .legend{{display:flex;flex-wrap:wrap;gap:14px;margin-top:14px;font-size:11.5px;color:var(--ink-soft);}}
  .legend i{{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:6px;
    vertical-align:middle;}}

  /* item rows — strike(closed)/open/status word + plain-english why (never color-alone) */
  .surf{{margin-bottom:18px;}}
  .surf .stitle{{font-size:11px;letter-spacing:2px;text-transform:uppercase;font-weight:700;
    color:var(--ink-faint);margin-bottom:6px;}}
  .rows{{border-left:2px solid var(--sand);}}
  .row{{display:flex;align-items:flex-start;gap:10px;padding:7px 0 7px 14px;
    transition:background .18s ease,border-color .18s ease;border-left:2px solid transparent;
    margin-left:-2px;}}
  .row:hover{{background:var(--paper-hi);border-left-color:var(--mustard);}}
  .row .rid{{font-size:11px;color:var(--ink-soft);font-weight:600;flex-shrink:0;min-width:0;}}
  .row .rmain{{flex:1;min-width:0;}}
  .row .rt{{font-size:13.5px;color:var(--ink);}}
  .row.closed .rt{{text-decoration:line-through;text-decoration-color:var(--ink-faint);color:var(--ink-faint);}}
  .row .rwhy{{font-size:11.5px;color:var(--ink-soft);margin-top:2px;line-height:1.5;}}

  /* status chips — warm palette, status word always present (color is reinforcement) */
  .chip{{font-size:10px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;
    padding:3px 8px;border-radius:4px;flex-shrink:0;white-space:nowrap;}}
  .chip.closed{{background:var(--sand);color:#6b6354;}}
  .chip.open{{background:var(--mustard);color:var(--ink);}}
  .chip.blocked{{background:var(--terracotta);color:var(--paper);}}
  .chip.other{{background:transparent;color:var(--ink-soft);border:1.5px solid var(--sand);}}
  .chip.build{{background:var(--mustard);color:var(--ink);}}
  .chip.activation{{background:transparent;color:var(--ink-soft);border:1.5px solid var(--ink-soft);}}
  .chip.state{{background:transparent;border:1.5px solid var(--terracotta);color:var(--terracotta);}}

  /* unretired ledger + remaining list */
  .led{{padding:12px 0;border-bottom:1px solid var(--sand);}}
  .led:last-child{{border-bottom:none;}}
  .led .lh{{display:flex;align-items:center;gap:9px;flex-wrap:wrap;}}
  .led .lid{{font-family:var(--serif);font-size:17px;color:var(--ink);}}
  .led .lwhy{{font-size:12px;color:var(--ink-soft);margin-top:5px;line-height:1.55;}}
  .led .lretire{{font-size:12px;margin-top:5px;line-height:1.55;}}
  .led .lretire b{{font-weight:700;font-size:10px;letter-spacing:1px;text-transform:uppercase;
    color:var(--terracotta);margin-right:6px;}}

  .rem{{display:flex;align-items:flex-start;gap:12px;padding:9px 0;border-bottom:1px solid var(--sand);}}
  .rem:last-child{{border-bottom:none;}}
  .rem .rn{{font-family:var(--serif);font-size:22px;color:var(--mustard);width:30px;text-align:right;
    flex-shrink:0;line-height:1.1;}}
  .rem .rbody{{flex:1;}}
  .rem .rlabel{{font-size:14px;font-weight:600;color:var(--ink);}}
  .rem .rgate{{font-size:12px;color:var(--ink-soft);margin-top:2px;line-height:1.5;}}
  .rem .rmeta{{font-size:10.5px;color:var(--ink-soft);margin-top:2px;}}

  /* misc lists */
  .pr{{display:flex;align-items:baseline;gap:8px;padding:5px 0;font-size:13px;}}
  .pr .dot{{font-size:9px;}}
  .pr .dot.passing{{color:#5a7a2e;}} .pr .dot.running{{color:var(--mustard);}}
  .pr .dot.failing{{color:var(--terracotta);}} .pr .dot.none{{color:var(--ink-faint);}}
  .recent{{padding:9px 0;border-bottom:1px solid var(--sand);}}
  .recent:last-child{{border-bottom:none;}}
  .recent .rh{{font-family:var(--serif);font-size:14px;color:var(--ink);}}
  .recent .rd{{font-size:11px;color:var(--ink-soft);}}
  .recent .rn2{{font-size:12px;color:var(--ink-soft);margin-top:3px;line-height:1.55;}}
  .gate{{padding:7px 0;font-size:13px;border-bottom:1px solid var(--sand);}}
  .gate:last-child{{border-bottom:none;}}
  .gate b{{font-weight:700;font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--terracotta);}}
  .muted{{color:var(--ink-soft);font-size:12.5px;}}
  .prose{{font-size:13.5px;color:var(--ink-soft);line-height:1.7;}}
  .prose strong{{color:var(--ink);font-weight:600;}}
  .prose code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.86em;
    background:var(--paper);border:1px solid var(--sand);border-radius:3px;padding:.5px 4px;color:#7a5a12;}}
  .prose li{{margin-left:18px;list-style:disc;}}

  footer{{margin-top:48px;padding-top:18px;border-top:1.5px solid var(--sand);
    font-size:11px;color:var(--ink-soft);letter-spacing:.3px;}}
  footer code{{color:var(--ink-soft);}}

  :focus-visible{{outline:2.5px solid var(--mustard);outline-offset:2px;border-radius:3px;}}

  @media(max-width:760px){{
    .grid2,.grid-hero{{grid-template-columns:1fr;}}
    .waffle{{grid-template-columns:repeat(12,1fr);}}
    .shead .htxt{{font-size:20px;}} .stat .big{{font-size:38px;}}
  }}
  @media(prefers-reduced-motion:reduce){{
    html{{scroll-behavior:auto;}} .row{{transition:none;}}
  }}
</style>
</head>
<body>
<header class="topbar">
  <div class="inner">
    <span class="brand">Harness roadmap <em>— operator dashboard</em></span>
    <span class="anchor" id="anchor"></span>
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
      <div class="card"><div id="next-action" class="prose"></div></div>
    </section>

    <section>
      <div class="shead"><span class="num">03</span><span class="htxt">R-NNN status board</span><span class="rule"></span></div>
      <div class="card"><div id="status-board"></div></div>
    </section>

    <section id="pp8-card">
      <div class="shead"><span class="num">04</span><span class="htxt">Post-Phase-8 forward register</span><span class="rule"></span></div>
      <div class="card"><div id="pp8-summary" class="prose" style="margin-bottom:14px"></div><div id="pp8-board"></div></div>
    </section>

    <div class="grid2">
      <section style="margin-top:0">
        <div class="shead"><span class="num">05</span><span class="htxt">In-flight PRs</span><span class="rule"></span></div>
        <div class="card"><div id="prs"></div></div>
      </section>
      <section style="margin-top:0">
        <div class="shead"><span class="num">06</span><span class="htxt">Operator gates</span><span class="rule"></span></div>
        <div class="card"><div id="gates"></div></div>
      </section>
    </div>

    <div class="grid2">
      <section style="margin-top:0">
        <div class="shead"><span class="num">07</span><span class="htxt">Commit cadence</span><span class="rule"></span></div>
        <div class="card"><canvas id="cadence" height="120"></canvas></div>
      </section>
      <section style="margin-top:0">
        <div class="shead"><span class="num">08</span><span class="htxt">Recently completed</span><span class="rule"></span></div>
        <div class="card"><div id="recent"></div></div>
      </section>
    </div>

    <footer>
      Drift-log events: <span id="drift-count"></span> ·
      generated by <code>tools/dashboard/generate.py</code> (R-XI-01) ·
      design: Mustard Editorial (dashboard-design/DESIGN.md) ·
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

// anchor
const d = DATA.dashboard || {{}};
document.getElementById("anchor").innerHTML =
  `head <code>${{esc(d.git_head)}}</code> · hash <code>${{esc(d.hash)}}</code> · ${{esc(d.last_refreshed)}} · ${{esc(d.fork_count)}} open forks`;

// next action
document.getElementById("next-action").innerHTML = mdLite(d.next_action);

// ---- closure hero ----
(function() {{
  const cl = DATA.closure || {{}}, b = cl.build || {{}}, ac = cl.activation || {{}}, w = b.waffle || {{}};
  const stateClass = {{ "PARTIAL":"partial", "STILL-BOUNDED":"bounded", "STILL-BOUNDED-INDEFINITELY":"indef" }};
  // waffle cells
  let cells = "";
  for (let i=0;i<(w.retired||0);i++) cells += '<div class="cell retired"></div>';
  for (let i=0;i<(w.partial||0);i++) cells += '<div class="cell partial"></div>';
  for (let i=0;i<(w.still_bounded||0);i++) cells += '<div class="cell bounded"></div>';
  for (let i=0;i<(w.sb_indef||0);i++) cells += '<div class="cell indef"></div>';
  const legend =
    `<span><i style="background:var(--mustard)"></i>retired ${{w.retired||0}}</span>` +
    `<span><i style="background:var(--terracotta)"></i>partial ${{w.partial||0}}</span>` +
    `<span><i style="background:var(--ink-soft)"></i>still-bounded ${{w.still_bounded||0}}</span>` +
    `<span><i style="background:var(--sand);border:1px dashed var(--ink-faint)"></i>indefinite ${{w.sb_indef||0}}</span>`;

  const nonret = (b.nonretired||[]).map(r => `
    <div class="led">
      <div class="lh"><span class="lid">${{esc(r.id)}}</span>
        <span class="chip state">${{esc(r.state)}}</span>
        <span class="muted">${{esc(r.rnnn)}}</span></div>
      <div class="lwhy">${{esc(r.why)}}</div>
      <div class="lretire"><b>retire?</b>${{esc(r.retire)}}</div>
    </div>`).join("");

  const rem = (cl.remaining||[]).map(r => `
    <div class="rem">
      <span class="rn">${{r.n}}</span>
      <div class="rbody">
        <div><span class="rlabel">${{esc(r.label)}}</span> <span class="chip ${{r.layer==='build'?'build':'activation'}}">${{esc(r.layer)}}</span></div>
        <div class="rgate">${{esc(r.gate)}}</div>
        <div class="rmeta">${{esc(r.id)}}</div>
      </div>
    </div>`).join("");

  document.getElementById("closure").innerHTML = `
    <div class="grid-hero">
      <div class="card stat build">
        <div class="k">Build closure — is the harness built?</div>
        <div class="big">${{b.pct_lo}}<span class="unit">–${{b.pct_hi}}%</span></div>
        <div class="sub"><strong>${{b.lo}}–${{b.hi}} of ${{b.total}}</strong> substitutions retired. A range, not a single number, because the final count is unratified — <strong>R-700, your sign-off</strong> (46/47/48). The 8 rows below are what remain.</div>
        <div class="bar"><span style="width:${{b.pct_lo}}%"></span></div>
        <div class="waffle" role="img" aria-label="${{w.retired}} of ${{w.total}} substitutions retired — ${{w.partial}} partial, ${{w.still_bounded}} still-bounded, ${{w.sb_indef}} indefinite">${{cells}}</div>
        <div class="legend">${{legend}}</div>
      </div>
      <div class="card stat">
        <div class="k">Activation / deployment closure</div>
        <div class="big">0<span class="unit">% exercised</span></div>
        <div class="sub"><strong>${{ac.open}} of ${{ac.total}}</strong> forward items open. This is <strong>not remaining build work</strong> — it is operator-gated (credentials + infrastructure that cannot run in this workspace) and bounded-residual by design.</div>
        <div class="pull">"The harness is built; this axis switches on at a real deployment."</div>
      </div>
    </div>
    <div class="grid2" style="margin-top:22px">
      <div class="card">
        <div class="label" style="margin-bottom:12px">Unretired substitutions (8) — state · why · can we retire?</div>
        ${{nonret}}
      </div>
      <div class="card">
        <div class="label" style="margin-bottom:12px">Remaining to complete — ordered by logical flow</div>
        ${{rem}}
      </div>
    </div>`;
}})();

// ---- item row (R-NNN board + register) ----
function itemRow(a) {{
  const title = `<span class="rid">${{esc(a.id)}}</span>`;
  if (a.rkind === "closed") {{
    return `<div class="row closed"><div class="rmain"><span class="rt">${{esc(a.title)}}</span></div><span class="chip closed">closed</span></div>`;
  }}
  if (a.rkind === "open") {{
    return `<div class="row"><div class="rmain"><span class="rt">${{esc(a.title)}}</span></div><span class="chip open">open</span></div>`;
  }}
  const chipClass = a.status === "BLOCKED" ? "blocked" : "other";
  const why = a.why ? `<div class="rwhy">${{esc(a.why)}}</div>` : "";
  return `<div class="row"><div class="rmain"><span class="rt">${{esc(a.title)}}</span>${{why}}</div><span class="chip ${{chipClass}}">${{esc(a.rword)}}</span></div>`;
}}
const STATUS_RANK = {{ ACTIVE:0, "APPLIED-PENDING-OPERATOR-E2E":1, PROPOSED:2, BLOCKED:3, DEFERRED:4, RESOLVED:5, CANCELLED:6 }};
function rowsFor(items) {{
  return items.slice().sort((a,b)=>(STATUS_RANK[a.status]??9)-(STATUS_RANK[b.status]??9) || a.id.localeCompare(b.id)).map(a=>`<div class="row-id-wrap">${{itemRow(a)}}</div>`).join("");
}}

// status board grouped by surface
const bySurface = {{}};
for (const a of (DATA.actions||[])) {{ (bySurface[a.surface || "?"] ||= []).push(a); }}
document.getElementById("status-board").innerHTML = Object.keys(bySurface).sort().map(surf => {{
  const items = bySurface[surf];
  return `<div class="surf"><div class="stitle">Surface ${{esc(surf)}} <span class="muted">(${{items.length}})</span></div><div class="rows">${{rowsFor(items)}}</div></div>`;
}}).join("");

// post-Phase-8 register
const pp8 = DATA.post_phase_8 || {{}}, pp8g = pp8.groups || {{}};
const PP8_NAMES = {{ IV:"Multi-LLM (IV)", V:"Multi-deployment (V)", VI:"Multi-tenant (VI)", IX:"External integrations (IX)", X:"Research (X)", CXA:"Cross-axis seams" }};
document.getElementById("pp8-summary").innerHTML =
  `<strong>${{pp8.count||0}} forward items</strong> across ${{Object.keys(pp8g).length}} groups — full detail at <code>${{esc(pp8.register||"")}}</code>. Phase 8 closed the substitution accounting; these are the activation / deployment / integration axis, tracked under the same R-NNN discipline.`;
document.getElementById("pp8-board").innerHTML = Object.keys(pp8g).sort().map(g => {{
  const items = pp8g[g];
  return `<div class="surf"><div class="stitle">${{esc(PP8_NAMES[g]||g)}} <span class="muted">(${{items.length}})</span></div><div class="rows">${{rowsFor(items)}}</div></div>`;
}}).join("");

// PRs
const prs = DATA.open_prs || [];
document.getElementById("prs").innerHTML = prs.length ? prs.map(p =>
  `<div class="pr"><span class="muted">#${{p.number}}</span><span class="dot ${{p.ci}}">●</span><span>${{esc(p.title)}} ${{p.draft?'<span class="muted">(draft)</span>':''}}</span></div>`
).join("") : '<div class="muted">none open</div>';

// gates
const gates = DATA.operator_gates || [];
document.getElementById("gates").innerHTML = gates.length ? gates.map(g =>
  `<div class="gate"><b>${{esc(g.id)}}</b> — ${{mdLite(g.gate)}}</div>`
).join("") : '<div class="muted">none</div>';

// recently completed
document.getElementById("recent").innerHTML = (d.recently_completed || []).map(rc =>
  `<div class="recent"><span class="rh">${{esc(rc.pr)}}</span> <span class="rd">${{esc(rc.date)}}</span><div class="rn2">${{mdLite(rc.note)}}</div></div>`
).join("");

document.getElementById("drift-count").textContent = d.drift_log_count ?? 0;

// cadence — warm restyle
const cad = DATA.cadence || [];
new Chart(document.getElementById("cadence"), {{
  type: "bar",
  data: {{ labels: cad.map(x=>x.date.slice(5)), datasets:[{{ data: cad.map(x=>x.count), backgroundColor:"#E0A82E", borderRadius:2 }}] }},
  options: {{ plugins:{{legend:{{display:false}}}}, animation:false,
    scales:{{ x:{{ ticks:{{color:"#9A8E76",maxTicksLimit:8,font:{{size:9}}}},grid:{{display:false}} }},
              y:{{ ticks:{{color:"#9A8E76",precision:0}},grid:{{color:"#D8CFBC"}} }} }} }}
}});
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
