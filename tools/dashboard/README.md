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
- **Recently completed** + drift-log event count.

## Data sources

| Source | Used for |
|---|---|
| `.harness/roadmap_status.md` | anchor, next-action, retirement, recently-completed, drift log |
| `Project_Roadmap_v1.md` §5 | R-NNN status board |
| `gh pr list` (GitHub API) | in-flight PRs + CI status (degrades to empty offline) |
| `git log` (30d) | commit-cadence sparkline |
| `harness-*/CLAUDE.md` §4.1 | per-axis retirement (best-effort) |

All parsing is defensive — a missing/malformed source yields an empty section, never a crash.

## Run locally

```bash
python tools/dashboard/generate.py --root .
# then open tools/dashboard/roadmap.html (or serve it):
python -m http.server -d tools/dashboard 8777   # http://localhost:8777/roadmap.html
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
