# v2 Orchestration - the explicit contract (canonical: REQUIREMENTS §M)

End-to-end runbook + the data contract between stages (per Codex: "make the slice contract explicit - cached rubric artifact, curator JSON output, operator-selected refs, hard per-element coverage before elevation"). Each stage names its INPUT artifact, OUTPUT artifact, and GATE.

All artifacts live under `dashboard-design/output/configurator-elevation/v2/`. The elevation working copy is `../target/` (a copy of `~/.claude/powerline-config/static/`).

## Stage 0 - inputs (exist now)
- `../target/{index.html,style.css,app.js}` - configurator copy (sandbox; apply-to-live is the last gate).
- `.claude/agents/dashboard-reference-curator.md` - v2 curator (gather-against-rubric, no skills/selection).
- `v2/rubric-producer.md` - Phase-1 spec. `v2/elevation-producer.mjs` - loop producer.

## Stage 1 - Rubric (skills run ONCE, cached)  [PAID gate G3]
- IN: PCP (build files + `powerline.owloops.com` + tokens) + fixed rejects/accept (inherited).
- DO: fire 4 lens-isolated skill-agents per `rubric-producer.md`; synthesize.
- OUT: **`v2/rubric.json`** (cached; regenerate only if target files/elements change - M6).
- Skip-if-cached: if `rubric.json` exists and target unchanged, reuse (0 spawns).

## Stage 2 - Gather (curator, visible browser, human cadence)  [PAID gate G3]
- IN: `v2/rubric.json`.
- DO: invoke the curator (general-purpose carrying the def's brief until the type registers; pass `rubric.json` inline/path). Drives the visible full-window Chrome; Filters->hex, Sort=Popular, Related branches; scroll deep, human cadence; pre-filter per fixed rejects; NO collections/account-writes.
- OUT: **`v2/candidates.json`** = `{rubricUsed, candidates:[{title,url,element,matchesRubric}], perElementCoverage, gaps, note}` + candidate screenshots.
- FALLBACK (M7): if Dribbble flakes (bot-check / zero shots), STOP; operator supplies 3-5 trusted shot URLs -> write them into `candidates.json` by hand. No thrash.

## Stage 3 - Operator review + select  [GATE - human-in-loop, the trust gate]
- IN: `v2/candidates.json` + screenshots (shown via SendUserFile / live browser).
- DO: operator quick-rejects/selects against the rubric.
- OUT: **`v2/selected.json`** = `{selected:[{url,element}]}`.
- HARD COVERAGE: must have >=1 selected for brand AND step-heads AND terminal-preview, or STOP and report the gap (do not proceed to elevation with a hole).

## Stage 4 - Summarize selected refs -> patterns
- IN: `v2/selected.json` (+ the shot images).
- DO: distill each selected ref into the concrete pattern it teaches, per element (caller, or one cheap pass).
- OUT: **`v2/refs-patterns.json`** = `{ "brand":["pattern", ...], "step-heads":[...], "terminal-preview":[...] }`.

## Stage 5 - Elevation  [PAID gate G3 for the loop]
- 5a. MARKUP (loop, carbonize-safe): no-LLM smoke first (free), then:
  `SKILLCHAIN_RUBRIC=v2/rubric.json SKILLCHAIN_REFS_PATTERNS=v2/refs-patterns.json \`
  `node tools/dashboard/live-auto/orchestrator.mjs --root=<repo> --file=dashboard-design/output/configurator-elevation/target/index.html --plan=v2/elevate-plan.mjs --producer=dashboard-design/output/configurator-elevation/v2/elevation-producer.mjs --no-inject`
  - `v2/elevate-plan.mjs`: one move per static element (brand `.brand`; step-heads `.step-head` x3 disambiguated by unique text "Theme & display"/"Hover a name"/"Custom data"; terminal-preview `.approx`/termbar), action+count+acceptVariant. (Authored at execution from the elements; selectors validated by the free smoke per the v1 lesson - unique text only.)
- 5b. CSS/JS (K2, code-level - me, NOT the loop): author refinements in `target/style.css` + `target/app.js` against Almanac Noir + the patterns, where markup-only can't reach.

## Stage 6 - Preview  [GATE]
- Serve `../target/` on a free port (NOT 8137/8770) or open the file; screenshot before/after; show the operator.

## Stage 7 - Apply to live  [GATE G5]
- On operator approval: copy `../target/*` -> `~/.claude/powerline-config/static/`. Only on explicit OK.

## Spawn budget (per full run, before caching)
Stage 1 = 4 (cached after first run -> 0) · Stage 2 = 1 · Stage 5a = N moves (~4-6). Cached steady-state run ~= 1 (gather) + N (loop). All paid stages gate at G3.

## Invariants (carried from REQUIREMENTS + reviews)
- Skills run ONCE (rubric); curator never invokes skills; convergence removed (operator selects).
- Real `/shots/<id>` URLs only; verify-before-present.
- Hard per-element coverage before elevation.
- Hyphens only (taste-lint). Almanac Noir tokens; warm-only; loop = no new CSS (CSS is Stage 5b).
- Every paid boundary gates; apply-to-live gates.
