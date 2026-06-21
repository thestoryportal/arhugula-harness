# R-FS-1 Arc-and-Unit Map — RETIRED (pointer stub)

> **This file is retired.** The R-FS-1 arc + unit map is now a **structured single source of
> truth** at **`.harness/arc-ledger.yaml`**, derived by **`tools/arc_ledger.py`** and rendered
> in the operator dashboard's **Arc & unit map** section (`tools/dashboard/roadmap.html`). The
> dashboard no longer parses this markdown.

**Authored:** 2026-06-17 (full map) · **Retired:** 2026-06-20 (R-FS-1 dashboard overhaul, Phase B) ·
**Posture:** mode-agnostic (process-substrate; this `.harness/` file only — no `design-substrate/**`
or `harness-*/src` edit, X-AL-3 trivially clean).

---

## Why it was retired

The original markdown carried the whole map (every arc, its plain-language capability, build
position, dependencies, and atomic units) as **hand-maintained prose the dashboard PARSED** — and
it drifted (the §5 status table lagged #671; hardcoded test counts went stale = R-IF-114; the
~14 registered-forward arcs were invisible). The overhaul replaced it with the proven
`substitutions.yaml → ledger tool → dashboard + blocking CI gate` pattern (R-600):

| Concern | Where it lives now |
|---|---|
| Every arc + unit + status (the single source) | **`.harness/arc-ledger.yaml`** |
| Derivation + the blocking tally gate | **`tools/arc_ledger.py`** (`--check` / `--summary` / `--json`; CI job `arc-ledger`) |
| The human-readable render (frozen arcs + units, standalone + forward arcs) | dashboard **Arc & unit map** (`tools/dashboard/generate.py` → `roadmap.html`) |
| Per-arc rationale + the forward `B-*` register | **`.harness/beyond-mvp-capability-boundary-ledger.md`** (the spine ledger) |
| Per-arc grounding leads | **`.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md`** (re-ground at arc-open) |

**Forward-only discipline.** A real transit (an arc closes/resolves, or a new arc/unit surfaces)
edits the `arc-ledger.yaml` row **and** bumps its `snapshot:` block in the **same commit**;
`tools/arc_ledger.py --check` fails CI on an impossible/stale tally. No second parseable copy
exists to drift.

## Old section-anchor redirects

Historical cites to this file's sections resolve to the ledger:

- `§R-FS-1·<TAG>` (e.g. `§R-FS-1·B6`, `§R-FS-1·M`) → the `kind: frozen` row with `id: <TAG>` in `arc-ledger.yaml` (`gives` = the plain-language capability; `units` = the as-built units).
- `§5` (standalone arc status table) → the `kind: standalone` rows in `arc-ledger.yaml` (`status`: closed / remaining / gated / resolved / registered).
- `§7` (at-a-glance counts) → `python tools/arc_ledger.py --summary`, or the dashboard masthead.

---

*Filing footer — Artifact: `.harness/r-fs-1-arc-and-unit-map.md` (RETIRED pointer stub). Canonical
arc→unit source: `.harness/arc-ledger.yaml` (derived by `tools/arc_ledger.py`, rendered by
`tools/dashboard/generate.py`). Spine: `.harness/beyond-mvp-capability-boundary-ledger.md`. Posture:
mode-agnostic; X-AL-3 trivially clean. Prior 376-line full map preserved in git history.*
