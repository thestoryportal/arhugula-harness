# Operator dashboard (R-XI-01)

A single-page, at-a-glance view of harness development status, generated from the
roadmap substrate. No build step, no bundler — `generate.py` emits one
self-contained `roadmap.html` (hand-authored CSS + Chart.js via CDN).

**Canonical design: Almanac Noir / instrument ledger** (candidate B). Visual
design changes go through the **4-skill autonomous loop**, not hand-edits —
see `../../dashboard-design/DISCIPLINE.md` (the rule) + `live-auto/RUNBOOK.md`
(the how-to). A persistent live copy runs at **http://localhost:8137/** (launchd
service, regenerated from live data on every page load).

## What it surfaces

- **Next action** — the deterministic next-action panel from `.harness/roadmap_status.md`.
- **Phase 7 retirement** — RETIRED progress bar + bucket breakdown.
- **Commit cadence** — last-30-day commit sparkline (`git log`).
- **R-NNN status board** — every action from `Project_Roadmap_v1.md` §5, grouped by
  surface, colored by status (hover a chip for the title).
- **In-flight PRs** — open PRs + per-PR CI rollup (`gh pr list`).
- **Operator gates** — actions awaiting an operator-only step (live e2e, deployment).
- **Arc & unit map** — every R-FS-1 arc + its as-built units (frozen build order) plus the
  standalone + registered-forward `B-*` arcs, derived from `.harness/arc-ledger.yaml`.
- **Recently completed** + drift-log event count.

## Data sources

| Source | Used for |
|---|---|
| `.harness/roadmap_status.md` | anchor, next-action, retirement, recently-completed, drift log |
| `.harness/arc-ledger.yaml` | the Arc & unit map (frozen arcs + units; standalone + registered-forward arcs) — derived via `tools/arc_ledger.py`; **single structured source**, no parseable markdown copy |
| `.harness/substitutions.yaml` | substitution-retirement closure counts — derived via `tools/substitution_ledger.py` |
| `Project_Roadmap_v1.md` §5 | R-NNN status board |
| `gh pr list` (GitHub API) | in-flight PRs + CI status (degrades to empty offline) |
| `git log` (30d) | commit-cadence sparkline |
| `harness-*/CLAUDE.md` §4.1 | per-axis retirement (best-effort) |

All parsing is defensive — a missing/malformed source yields an empty section, never a crash.
The `.harness/arc-ledger.yaml` path additionally has a **no-PyYAML fallback** (the system-Python
3.9 Codex guard hand-parses the YAML and feeds it through the same `arc_ledger.derive()`), so the
regenerated dashboard is byte-identical with or without PyYAML.

## Currentness discipline

`generate.py` owns the dashboard's volatile facts. The visible masthead values
(`HEAD`, `LAST`, `HASH`, and `OPEN FORKS`) are derived from current git,
filesystem, and open-PR inputs at generation time; closure and activation copy
uses computed counts, not copied prose. Do not hand-edit
`tools/dashboard/roadmap.html` or hard-code current counts in the template.

Refresh order:

1. Update `.harness/roadmap_status.md` from the current roadmap protocol.
2. If an R-FS-1 arc transited (closed/resolved, or a new arc/unit surfaced), edit the
   `.harness/arc-ledger.yaml` row **and** bump its `snapshot:` block in the **same commit**
   (forward-only; `python tools/arc_ledger.py --check` gates it).
3. Run `python3 tools/dashboard/generate.py --root .`.
4. Verify with `uv run pytest tools/test_arc_ledger.py tools/test_dashboard_generate.py` and the
   Codex closeout/context guard for the arc.

## Run locally

```bash
python3 tools/dashboard/generate.py --root .
# then open tools/dashboard/roadmap.html (or serve it):
python3 -m http.server -d tools/dashboard 8777   # http://localhost:8777/roadmap.html
```

`tools/dashboard/roadmap.html` is a committed snapshot for local viewing; CI regenerates
a fresh copy on deploy. `tools/dashboard/public/` is the ephemeral Pages build dir (gitignored).

## Deploy (GitHub Pages)

`.github/workflows/dashboard-deploy.yml` regenerates + publishes on every relevant push to
`main`. **One-time operator setup:** repo **Settings → Pages → Source: "GitHub Actions"**.
Until then the workflow's `deploy` job fails (expected); the `build` job still validates the
generator. Once enabled, the dashboard lives at `https://thestoryportal.github.io/arhugula-harness/`.

## Design discipline

Visual design is **not** hand-edited. Any change to the dashboard's look goes
through the **4-skill autonomous loop** (`impeccable` + `design-taste-frontend` +
`ui-ux-pro-max` + `frontend-design`) at `live-auto/`. Data/functional wiring in
`generate.py` (new sections, series, parsing) is authored directly; the visual
elevation of those elements is produced by the loop. See
`../../dashboard-design/DISCIPLINE.md` + `live-auto/RUNBOOK.md`.

## Roadmap

R-XI-01 = the MVP. R-XI-04/05/06 = closure section + Mustard redesign + polish
(superseded by the Almanac Noir canonical). R-XI-02 (dependency-graph viz via
Mermaid + richer sparklines) and R-XI-03 (live-update mode) are follow-on
iterations.
