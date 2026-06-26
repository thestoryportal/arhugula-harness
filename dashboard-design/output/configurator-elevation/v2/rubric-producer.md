# v2 Phase 1 - Rubric producer (skills-first, run once, cached)

Produces `rubric.json` (cached per project). The 4 design skills run ONCE, lens-isolated. Per the advisor + Codex redundancy finding, the skills do **NOT** re-derive the reject list (that is a FIXED inherited constant); they contribute only their genuine value-add: **query expansion, per-element hunt-list nuance, lens-specific accept nuance.**

## Fixed constraints (INHERITED - not produced by the skills)
Sourced verbatim from the curator def + REQUIREMENTS, injected into every skill prompt as givens:
- **REJECT (fixed):** standalone logos / brand-identity mockups; light-mode UIs; consumer/mobile app screens; coding-challenge or marketing pages; glassmorphism / glow / lens-flare / gradient-drenched AI-SaaS looks; large rounded cards; multi-color status confetti.
- **ACCEPT frame (fixed):** dark, warm, restrained, instrument-grade dashboard / settings / config-panel / developer-tool / console UIs; judge HIERARCHY / LAYOUT / DENSITY / TYPOGRAPHY / RESTRAINT, not palette.
- **Elements:** brand masthead lockup · 3 numbered step-heads · terminal-preview window frame.
- **Project Context Pack** (read primary sources): `~/.claude/powerline-config/static/{index.html,style.css}` (Almanac Noir tokens) + view `https://powerline.owloops.com/` (the upstream sibling configurator) + `dashboard-design/CLAUDE.md`.

## Per-skill prompt template (one spawn per `{SKILL}`, run ONCE)
> You are a design specialist reasoning through ONE lens. Step 1: invoke `{SKILL}` via the Skill tool and fully adopt its guidance (verified: your run must show the `Skill` tool_use). Step 2: ground in the primary sources - Read the build `index.html`/`style.css` and view `https://powerline.owloops.com/`; note in one line what each told you that a generic search would miss. The REJECT list and ACCEPT frame below are FIXED givens - do NOT re-derive them. Step 3, through `{SKILL}`'s lens ONLY, emit: (a) 4-6 Dribbble search queries your lens would hunt, in the project's vocabulary (configuration dashboard / settings configurator / statusline / control panel / token-matched terms like "amber dark" "warm dark monochrome" "hairline" / browser-desktop, NOT mobile); (b) a per-element hunt-list (brand / step-heads / terminal-preview): the specific structural pattern your lens looks for in each; (c) any lens-specific ACCEPT nuance beyond the fixed frame. [FIXED REJECT + ACCEPT + PCP injected here.]
>
> Output STRICT JSON only: `{"skill":"{SKILL}","groundingNote":"...","queries":["..."],"perElement":{"brand":["..."],"step-heads":["..."],"terminal-preview":["..."]},"acceptNuance":["..."]}`

Skills: `impeccable`, `design-taste-frontend`, `ui-ux-pro-max`, `frontend-design`. [4 spawns]

## Synthesis (caller, deterministic - no spawn)
Merge the 4 lens outputs into `rubric.json`:
```
{
  "fixedRejects": [ <the inherited reject list> ],
  "acceptFrame":  "<the inherited accept frame>",
  "acceptNuance": [ <union of the 4 lenses' acceptNuance, deduped> ],
  "queries":      [ <deduped union of all 4 lenses' queries; cap ~8> ],
  "hexFilters":   ["#f0a830","#15120d"],
  "sort":         "Popular",
  "perElement":   { "brand":[...], "step-heads":[...], "terminal-preview":[...] },   // merged hunt-lists
  "skillsProvenance": ["impeccable","design-taste-frontend","ui-ux-pro-max","frontend-design"],
  "producedAt": "<stamp at write time>"
}
```
Write to `v2/rubric.json`. **Cached (M6):** reuse on later runs; regenerate only if `index.html`/`style.css`/elements change.

## Execution note
Firing the 4 skill spawns is a PAID-call boundary (G3) - gate with the operator before running. Each spawn is read-only (Skill + Read + browser-view for the owloops page); no writes, no Dribbble account actions.
