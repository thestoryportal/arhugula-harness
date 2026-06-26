# CLAUDE.md — Dashboard Design Workspace

*Bounded context for operator dashboard visual design. This file is the
sole governance surface for agents working inside `dashboard-design/`.
Loaded at session start; self-contained by design.*

> **▶ ACTIVE WORKFLOW:** if you were launched to execute the configurator-elevation
> workflow, read **`HANDOFF.md`** (this directory) FIRST - it has current state, the
> canonical v2 spec/runbook pointers, the next action (Stage 1, gated), and the
> hard-won gotchas. Then `output/configurator-elevation/v2/ORCHESTRATION.md`.

---

## 1. Scope

This directory owns the **visual design** of operator dashboards — the
4-skill autonomous loop, design system references, and design discipline.

**Context boundary.** Agents working here SHOULD NOT load, reference, or
apply the root `CLAUDE.md`. That file governs harness implementation
(Phase 7, substitution accounting, roadmap audit, axis specs, posture
declarations) — none of which is relevant to dashboard visual design.
Everything an agent needs is in this file plus the two pointed-to
references (`DISCIPLINE.md`, `RUNBOOK.md`).

**What this workspace does:**
- Elevate existing dashboard elements via the 4-skill loop
- Design new dashboard surfaces (isolated from existing ones)
- Maintain the Almanac Noir design system fidelity

**What this workspace does NOT do:**
- Harness implementation (Python, Pydantic, pyright, axis specs)
- Roadmap audit, drift detection, substitution ledger accounting
- Data plumbing or functional wiring in `generate.py`

---

## 2. Non-interference rules

> **Any new dashboard designed here MUST NOT conflict with or
> destructively modify existing dashboards.**

### Existing dashboard inventory

| Asset | Path | Owner |
|---|---|---|
| `roadmap.html` | `tools/dashboard/roadmap.html` (187KB, committed) | `tools/dashboard/generate.py` |
| Live service | `http://localhost:8137/` | launchd `org.thestoryportal.harness-dashboard` |
| Pages build | `tools/dashboard/public/index.html` (gitignored) | `generate.py` |

### Hard constraints

1. **MUST NOT modify** `tools/dashboard/generate.py` visual output, CSS
   token values, or HTML structure — unless the explicit task is
   elevating the *existing* dashboard via the 4-skill loop.

2. **MUST NOT overwrite** `tools/dashboard/roadmap.html` — it is
   generator output, never hand-edited.

3. **MUST NOT reuse port 8137** — the launchd service owns it. New
   dashboards use a different port.

4. **MUST NOT introduce CSS class names that collide** with the existing
   `roadmap.html` namespace. The reserved names include (non-exhaustive):
   `panel`, `chip`, `meter`, `waffle`, `led`, `brand`, `shead`,
   `gaugebar`, `arccard`, `arcstrip`, `depgraph-wrap`, `readout`,
   `gridHero`, `grid2`, `rem`, `surf`, `tick`, `wrap`, `top`, `prose`,
   `gate`, `legend`, `cell`, `dep-panel`, `live-ind`, `filter-btn`,
   `status-filters`, `recent`, `rows`, `muted`, `chartnote`, `quote`,
   `unretgrid`, `units`, `arcsep`, `mono`, `lit`.
   New dashboards MUST either use a namespaced prefix (e.g.
   `nd-panel`, `health-chip`) or be fully self-contained files with
   no shared stylesheet.

5. **MUST NOT redefine** the Almanac Noir `:root` token values in
   `generate.py`. New dashboards *consume* these tokens; they do not
   change them.

6. **MUST NOT mix new files** into the existing `tools/dashboard/` root
   alongside `roadmap.html`. New dashboard output goes in its own
   directory (e.g. `dashboard-design/output/<name>/` or
   `tools/dashboard/<name>/`).

---

## 3. Canonical design system — Almanac Noir

The committed canonical design is **Almanac Noir / instrument ledger**.
Its tokens live in `generate.py`'s `:root` block. Inlined here for
zero-hop agent access:

```css
:root {
  /* Surfaces */
  --ground: #15120d;       /* warm near-black — page ground */
  --panel:  #1c1812;       /* card / section background */
  --panel-hi: #221d16;     /* raised / hover surface */

  /* Text */
  --bone:      #e8e0cf;    /* primary text (~11:1 on ground) */
  --bone-soft: #cabfa2;    /* secondary text (>=5.5:1) */
  --bone-faint: #ab9f82;   /* labels, metadata (large/secondary only) */

  /* Accent */
  --amber:      #f0a830;   /* single signal accent */
  --amber-glow: #ffc14d;   /* hover / glow state */
  --ember:      #d8542f;   /* alert / partial ONLY — never decorative */

  /* Structure */
  --hair:      #3a342a;    /* hairline rules, grid lines */
  --hair-soft: #2a251e;    /* subtle grid, background texture */

  /* Geometry */
  --radius: 2px;           /* single corner-radius scale */

  /* Typography */
  --disp: 'Big Shoulders Display', 'Arial Narrow', sans-serif;
  --body: 'IBM Plex Sans', 'Helvetica Neue', sans-serif;
  --mono: 'JetBrains Mono', 'SFMono-Regular', ui-monospace, monospace;
}
```

### Typography scale

| Level | Family | Weight | Usage |
|---|---|---|---|
| Display (h1) | `--disp` | 700 | Masthead brand, large readouts |
| Section head | `--disp` | 600 | Numbered `01`..`11` section titles |
| Body | `--body` | 400/500 | Prose, descriptions, annotations |
| Mono labels | `--mono` | 400-700 | Status chips, readout values, code |

### Geometry rules

- **8px spacing base** — tokens at 8 / 14 / 16 / 18 / 24 / 46 / 72.
- **2px radius** everywhere (no large rounded corners).
- **Hairline rules** (1px `--hair`) before box-shadow; box-shadow is
  rare and always inset glow, never drop.
- **Background grid** — 46px repeating hairline-soft grid on `body`.

### Superseded systems

`DESIGN.md` in this directory describes the **Mustard Editorial** system
(warm paper ground, mustard offset shadows, serif display). That system
is **superseded** by Almanac Noir and is NOT the canonical design.
Agents MUST NOT apply Mustard Editorial tokens to new dashboard work.

---

## 4. The 4-skill autonomous loop

Visual design edits to dashboards go through the autonomous skill chain —
never hand-authored. The full discipline is at `DISCIPLINE.md` in this
directory; the operational how-to is at
`tools/dashboard/live-auto/RUNBOOK.md`.

### The four skills

| Skill | Install name | Contribution |
|---|---|---|
| **Impeccable** | `impeccable` | Named visual actions (`polish`, `bolder`, `typeset`, `colorize`, etc.) |
| **Taste** | `design-taste-frontend` | Anti-slop "tells" — detects and corrects generic AI aesthetics |
| **UI/UX Pro Max** | `ui-ux-pro-max` | Accessibility, hierarchy, status-not-by-color-alone |
| **Frontend Design** | `frontend-design` | Intentional aesthetic direction, bold design choices |

### Dribbble MCP — mandatory design references

> **MUST USE.** Before designing or elevating any dashboard element,
> search Dribbble for quality reference designs. This is not optional.

The `dribbble` MCP server loads from `.mcp.json` (symlinked from root)
and provides four tools:

| Tool | Purpose |
|---|---|
| `dribbble_auth()` | One-time: open a visible Chrome window, log in / clear human-check. Session persists. |
| `dribbble_status()` | Check if the persisted session is live (logged in, no check). |
| `dribbble_search(query, limit=12)` | Search Dribbble for any design query -> `[{title, url}]`. |
| `dribbble_shot(url)` | Get details for one shot -> `{title, image, url}`. |

**Workflow integration:**
1. At session start, run `dribbble_status()` to verify the session is live.
   If not, run `dribbble_auth()` and have the operator clear the check.
2. Before any design work, run `dribbble_search()` with relevant queries
   (e.g. `"dark dashboard data viz"`, `"operator console status board"`,
   `"instrument panel warm dark"`, `"analytics dashboard amber"`).
3. Review 3-5 top shots with `dribbble_shot()` to extract reference
   patterns (layout, hierarchy, density, typography treatment).
4. Cite the reference URLs in your design rationale.

The MCP runs a real visible Chrome with a persistent profile at
`~/.dribbble-mcp/chrome_profile/` — no stealth, no anti-detection.
If a human-check appears, it surfaces the window for the operator.

### Invocation

The loop is orchestrated by `tools/dashboard/live-auto/orchestrator.mjs`
with the skill-chain producer at `producer-skillchain.mjs`. Each move
spawns a headless `claude` agent with `--allowedTools Skill,Read,Grep,Glob`
(read-only — the agent cannot mutate files).

```bash
node tools/dashboard/live-auto/orchestrator.mjs \
  --file=<target.html> --plan=<plan.mjs> \
  --producer=tools/dashboard/live-auto/producer-skillchain.mjs
```

### Rules for the loop

- **Carbonize-safe**: variants reuse existing CSS classes verbatim.
  Invent NO new class names. Emit NO new CSS (`scopedCss: ''`).
- **Cost**: each spawn ~$0.035 (claude-sonnet-4-6). Paid calls require
  explicit operator approval.
- **Taste-lint gate**: zero em-dashes, zero en-dashes anywhere in output.
  Use hyphens only.
- **No-LLM smoke**: `orchestrator.mjs` with the default canned producer
  exercises orchestration without any LLM/network calls.

---

## 5. Edit split — who touches what

| Edit kind | Who does it |
|---|---|
| Data plumbing, new sections, parsing, chart data | Authored directly in `tools/dashboard/generate.py` (Python) |
| Visual elevation of existing elements | The 4-skill loop (`tools/dashboard/live-auto/`) |
| New dashboard surfaces (design + build) | Designed through the skill chain; output to isolated paths per §2 |
| Runtime-rendered viz (Mermaid SVG, Chart.js) | Authored in `generate.py` JS/style — outside the loop's scope |

### Scope boundary (learned at R-XI-02)

The loop re-authors **one element's static markup**, reusing existing CSS
classes. It can polish markup hierarchy of a concrete element. It
**cannot** design runtime-rendered viz (Mermaid SVG, Chart.js canvases)
or author new CSS classes a new section needs. That styling is code-level,
authored in `generate.py` against the Almanac Noir token system.

---

## 6. File map

### This directory (`dashboard-design/`)

| Path | Purpose |
|---|---|
| `CLAUDE.md` | This file — bounded context for design agents |
| `.mcp.json` | Symlink to root `.mcp.json` — loads the Dribbble MCP (+ others) |
| `DESIGN.md` | **Superseded** Mustard Editorial system (historical) |
| `DISCIPLINE.md` | The 4-skill autonomous loop discipline + edit split |
| `impeccable/` | Impeccable skill clone (local reference, ~gitignored) |
| `taste-skill/` | Taste skill clone (local reference, ~gitignored) |
| `ui-ux-pro-max-skill/` | UI/UX Pro Max clone (local reference, ~gitignored) |
| `frontend-design/` | Frontend Design skill (`SKILL.md` + `LICENSE.txt`) |
| `archive/` | Previous design outputs (Mustard Editorial kit) |

### Dashboard infrastructure (`tools/dashboard/`)

| Path | Purpose |
|---|---|
| `generate.py` | Python generator — data plumbing + HTML/CSS/JS template |
| `roadmap.html` | Committed snapshot — **DO NOT hand-edit** |
| `public/` | Gitignored Pages build directory |
| `live-auto/` | Orchestrator, producers, plans, RUNBOOK |
| `README.md` | Dashboard operational docs |

### Live service

The persistent live dashboard runs at `http://localhost:8137/` via
launchd (`org.thestoryportal.harness-dashboard`). It regenerates from
live workspace data on every page load. Do NOT start a second server
on port 8137.

---

## 7. Do / Don't

### Do

- **Search Dribbble first** (`dribbble_search`) for quality references before any design work
- Use the Almanac Noir token system (§3) for all dashboard design
- Run the 4-skill loop for visual elevation (§4)
- Cite Dribbble reference URLs in design rationale
- Namespace new dashboard CSS classes to avoid collisions (§2)
- Output new dashboards to isolated directories (§2)
- Read `DISCIPLINE.md` for the full edit-split discipline
- Read `tools/dashboard/live-auto/RUNBOOK.md` for operational how-to
- Keep body text at 16px with line-height 1.55-1.75 on dark ground
- Use hairline rules (`1px --hair`) before considering shadows

### Don't

- ❌ Apply root `CLAUDE.md` governance (harness impl, Phase 7, axis specs)
- ❌ Hand-edit `roadmap.html` or `generate.py` visual output
- ❌ Introduce new CSS classes in existing dashboard markup (carbonize-safe)
- ❌ Overwrite, collide with, or destructively modify existing dashboards
- ❌ Reuse port 8137
- ❌ Use pure black (`#000`) or pure white (`#fff`) — always use warm tokens
- ❌ Use cool colors (blue, green, cyan) — the palette is entirely warm
- ❌ Use the superseded Mustard Editorial system
- ❌ Run paid LLM calls without explicit operator approval
- ❌ Use em-dashes or en-dashes — hyphens only (taste-lint gate)
- ❌ Use drop shadows — use inset glow or hairline rules instead
- ❌ Use rounded corners larger than `--radius` (2px)

---

## 8. Skill + tool reference pointers

For deeper reference when authoring design guidance or reviewing
skill output:

- **Dribbble MCP** (mandatory): `dribbble_search` / `dribbble_shot`
  via the `dribbble` MCP server. Server code at `~/.dribbble-mcp/server.py`;
  launcher at `~/.local/bin/dribbble-mcp`; persistent Chrome profile
  at `~/.dribbble-mcp/chrome_profile/`. See `~/.dribbble-mcp/README.md`
  for env config (`DRIBBBLE_MCP_HEADLESS`, `DRIBBBLE_MCP_AUTH_WAIT`).
- **Impeccable design system**: `impeccable/.impeccable/design.json`
  (Neo Kinpaku — the impeccable.dev brand system, distinct from
  Almanac Noir but shares the warm-dark sensibility)
- **Frontend Design skill**: `frontend-design/SKILL.md` — design
  thinking framework + aesthetics guidelines
- **Taste skill**: installed at `~/.claude/skills/`; local clone at
  `taste-skill/` for reference (v2 default, anti-slop tells, GSAP
  skeletons, variance/motion/density dials)
- **UI/UX Pro Max**: installed at `~/.claude/skills/`; local clone at
  `ui-ux-pro-max-skill/` for reference (search databases for styles,
  typography, color, charts, UX patterns)

---

*Dashboard Design Workspace · Almanac Noir · v1.0*
