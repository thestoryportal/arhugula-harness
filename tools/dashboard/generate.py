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
  const chips = items.map(a => {{
    const c = STATUS_COLORS[a.status] || "bg-gray-700 text-gray-200";
    return `<span class="chip ${{c}}" title="${{esc(a.title)}}">${{esc(a.id)}}</span>`;
  }}).join(" ");
  return `<div><div class="text-xs text-gray-400 mb-1">Surface ${{esc(surf)}} <span class="text-gray-600">(${{items.length}})</span></div><div class="flex flex-wrap gap-1.5">${{chips}}</div></div>`;
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
  const chips = items.map(a => {{
    const c = STATUS_COLORS[a.status] || "bg-gray-700 text-gray-200";
    return `<span class="chip ${{c}}" title="${{esc(a.title)}}">${{esc(a.id)}}</span>`;
  }}).join(" ");
  return `<div><div class="text-xs text-violet-300 mb-1">${{esc(PP8_NAMES[g]||g)}} <span class="text-gray-600">(${{items.length}})</span></div><div class="flex flex-wrap gap-1.5">${{chips}}</div></div>`;
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
        a
        for a in actions
        if a.get("surface") in _FORWARD_SURFACES or a["id"].startswith("R-CXA")
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
    dashboard = parse_dashboard(dash_md)
    return {
        "dashboard": dashboard,
        "actions": actions,
        "open_prs": parse_open_prs(root),
        "cadence": parse_cadence(root),
        "axis_retirement": parse_axis_retirement(root),
        "operator_gates": operator_gates(actions, dashboard),
        "post_phase_8": post_phase_8(actions),
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
