# Configurator Elevation - Consolidated Requirements

> **CANONICAL = §M (v2 collapsed architecture).** Sections D / F / G / L describe the
> SUPERSEDED v1 doubled pipeline (4-skill brief + separate 4-skill convergence + Dribbble
> collections) and are kept only for history. Any build or run MUST key off **§M + the v2
> curator agent def** (`.claude/agents/dashboard-reference-curator.md`). Where D/F/G/L
> conflict with M, **M wins.** (Reconciliation per Codex v2 review, this session.)

*Every requirement surfaced this session. Source: operator feedback + advisor + Codex reviews.*

---

## A. Workspace, context, isolation
- **A1.** Operate from `~/Projects/arhugula-v2/dashboard-design/` (MAIN checkout) - NOT a `.claude/worktrees/...` path, NOT global `~/.claude`.
- **A2.** Session cwd lives in `dashboard-design/` so the operator's **statusline reflects it**.
- **A3.** `dashboard-design/CLAUDE.md` is the **sole governing context**. Do NOT load/apply the harness root CLAUDE.md, roadmap (§12), X-AL-3, specs, posture, etc. Ignore the roadmap-drift hooks (not this venue).
- **A4.** `dashboard-design/` is the **sandbox**: work products + experiments land here (isolated subpaths like `output/...`); protected assets stay untouched.
- **A5.** Non-interference: do NOT edit `tools/dashboard/generate.py` visual output or `roadmap.html`, do NOT reuse port 8137, no CSS-class collisions with the reserved roadmap namespace.

## B. The task
- **B1.** Elevate the **powerline statusline configurator UI** (live at `http://localhost:8770/`; source at `~/.claude/powerline-config/static/`).
- **B2.** Elevation runs through the **4-skill autonomous design loop** (impeccable / design-taste-frontend / ui-ux-pro-max / frontend-design) - not hand-authored.
- **B3.** Work on a **sandbox copy**; apply to the live config only on operator approval.

## C. Design system (Almanac Noir) - non-negotiable
- **C1.** Tokens verbatim from `style.css`: ground `#15120d`, panels `#1c1812`/`#221d16`, bone `#e8e0cf`/`#cabfa2`/`#ab9f82`, single amber `#f0a830` (`#ffc14d` hover), ember `#d8542f` alerts-only, hairline `#3a342a`, 2px radius, 8px spacing, fonts Big Shoulders Display / IBM Plex Sans / JetBrains Mono.
- **C2.** Warm palette only; NO cool colors, NO pure black/white, NO drop shadows (inset glow/hairlines), NO rounded corners > 2px, NO glassmorphism/gradient.
- **C3.** Taste-lint: hyphens only, zero em/en dashes anywhere in output.
- **C4.** Mustard Editorial is superseded - do not use.

## D. Reference sourcing - the approved v1 design (skills-first)
- **D1. Skills-first (ESSENTIAL).** The 4 skills FIRST produce the sourcing approach; that becomes the Dribbble agent's embedded context. NOT the Dribbble agent invoking skills ad-hoc.
- **D2. Phase 1 - 4 skill-agents** (each genuinely adopts ONE skill via the Skill tool, verified by stream `Skill` tool_use) + the Project Context Pack -> each emits, through its lens: queries, accept/reject rubric, per-element hunt-list. Lens-isolated (decorrelated).
- **D3. Project Context Pack (per-project, from PRIMARY sources, not paraphrase):** what it is · design system (read from `style.css`) · what it IS / ISN'T · source context = (a) current build `~/.claude/powerline-config/static/{index.html,style.css}`, (b) upstream sibling `https://powerline.owloops.com/` (Powerline Studio - same domain, terminal-preview + numbered sections + export), (c) statusline segments @owloops/claude-powerline · elements (brand masthead, 3 numbered step-heads, terminal-preview frame).
- **D4. Each skill-agent must Read the build files AND view the owloops page itself**, and state in one line what each primary source told it that a generic search would miss (evidence it consumed them).
- **D5. Synthesis:** I merge the 4 lens-briefs into ONE sourcing brief (queries + rubric + per-element hunt-list) carrying all four lenses -> the Dribbble agent's context.
- **D6. Queries varied + specific** (not generic): a couple "dark dashboard" variants + design-system/token-matched (amber, warm-dark, monochrome, hairline) + configuration-specific (configuration dashboard, settings configurator, control/config panel) + browser-based (web/desktop). **Reject mobile dashboards.** (Responsive remains a *build* requirement for what we ship, not a reference filter.)
- **D7. Per-project reuse:** PCP swaps per project; the per-skill template + guarantees stay.

## E. The Dribbble agent (Phase 2)
- **E1.** A genuine **specialized agent** (durable def at `.claude/agents/dashboard-reference-curator.md`; runs as general-purpose with the full brief until the type registers next session), grounded in project build context + the skills-first brief.
- **E2.** Drives the **visible Chrome in a full ~1600x1000 window** - operator watches live (NOT the tiny/flashing headless dribbble-MCP window).
- **E3.** Moves like a **human**: scroll DEEP (many screens, full results), view options at higher frequency but **human cadence** (dwell between actions). This also avoids Dribbble's bot-check that rapid machine-nav triggers.
- **E4.** Captures only **real `/shots/<numeric-id>` URLs** actually seen (never invented); per-element coverage tracked; reports gaps honestly.
- **E5.** Quality over quota - reject logos, light-mode, consumer/mobile, coding-challenge, glass/gradient.

## F. Selection / convergence
- **F1.** Selection is done by **agents grounded in project + 4 skills' deep knowledge** - not me, not operator-pointing.
- **F2. Unanimous convergence**: a reference is selected only if all 4 skill-lenses agree it is suitable (operator's chosen bar).
- **F3.** Present chosen + evaluated references **with the agreement matrix + per-skill rationale**.

## G. Gates & process discipline
- **G1. Operator reference-review gate (standing, until trust established):** after the Dribbble agent gathers + before convergence/council runs, present the candidate pool to the operator for relevance review. Convergence does not run on an un-reviewed pool.
- **G2.** Present references **visually** (SendUserFile / live browser), not just titles, so the operator can verify validity.
- **G3. Paid-call gate:** at each paid Anthropic boundary, surface the plan + cost and explain the advantage before firing; no unilateral paid calls.
- **G4.** Operator reviews surviving references before the elevation loop runs.
- **G5.** Operator approves applying elevated output to the live `~/.claude/powerline-config/` config.

## H. Verification discipline
- **H1. Verify-before-present / re-ground:** subagent reports are presence-not-correctness; verify picks (URLs real, match rationale) before showing the operator. (Caught the prose-vs-JSON inconsistency.)
- **H2.** Free no-LLM smoke de-risks the loop plumbing before paid spawns.
- **H3.** Clean skills-only WS keeps elevation spawns cheap (~$0.035 vs ~$0.49).

## I. The 4-skill loop mechanics (for elevation, after refs)
- **I1.** Carbonize-safe: variants reuse existing CSS classes, emit NO new CSS, one element per move.
- **I2.** **K2 RESOLVED (loop markup + code-level CSS):** the loop elevates static markup hierarchy (reuse classes); I ADDITIONALLY author CSS/JS-level refinements directly in the configurator's `style.css`/`app.js` against Almanac Noir wherever genuine elevation needs it (beyond re-ordering existing elements). Runtime-rendered viz stays code-level. Most thorough scope.
- **I3.** Reference patterns from the converged set feed the elevation loop's producer prompt as context.

## J. Deliverable flow (end to end)
1. Skills-first brief (4 skill-agents -> synthesis) [paid; gate G3]
2. Dribbble agent gathers pool, live + watchable [paid; gate G3]
3. **Operator reviews pool** [gate G1/G2]
4. Unanimous convergence on reviewed pool [paid; gate G3]
5. **Operator reviews survivors** [gate G4]
6. Elevation loop per element, refs as context [paid; gate G3]
7. Preview (sandbox) [gate]
8. **Operator approves apply to live** [gate G5]

## K. Open items to confirm with operator
- **K1.** Convergence still runs AFTER the operator pool-review gate (G1) - confirm the order (gather -> operator review -> convergence) vs (gather -> convergence -> operator review).
- **K2.** I2: extent of CSS-level elevation allowed for the configurator (standalone app), vs strict carbonize-safe markup-only.
- **K3.** Whether the skills-first brief (Phase 1, 4 paid skill-agents) is wanted every run, or cached/reused across runs for the same project.
- **K4.** Anything from earlier this session not captured above.

---

## L. v1.1 additions (operator round 2)
- **L1. Order reversed (locked):** gather -> **operator approves the gathered pool/collection** (relevance/validity) -> convergence (skill-fit, unanimous) -> final refs -> operator review -> elevate. HIL is intentionally heavy now and steps down gradually as trust builds.
- **L2. Collection-based gather (recommended + adopted):** the Dribbble agent creates ONE project-named **collection** and saves candidates to it via the **ribbon (save-to-collection)** button (hover or in-modal) - NOT the global heart-like, to keep the account tidy. Over-gather broadly; the collection is the durable, operator-viewable candidate pool.
- **L3. Convergence input = the collection:** screenshot the collection grid as thumbnails + open key shots for genuine evaluation; the **4 skill-agents converge (unanimous)** on it. (Chosen over the agent self-narrowing - honors skills-converge.)
- **L4. Dribbble feature usage:**
  - **Filters -> Color:** seed with Almanac Noir hex (amber `#f0a830`, warm-dark `#15120d`) for palette-aligned results.
  - **Sort:** Popular primary; New & Noteworthy optional; skip Following.
  - **Related:** follow the page's `Related:` terms to branch into adjacent searches (human-like discovery) past the primary query.
- **L5. Counts/bounds (proposed, confirm):** searches min 4 / max ~8 (incl. Related branches); collection over-gather ~12-18 candidates; final references presented min 3 (>=1 per element where possible) / target 5-6 / max 8.
- **L6. K3 resolved:** skills-first brief regenerated EVERY run (re-grounds each time).
- **L7. PREREQUISITE - Dribbble login:** collections + saving require the operator's Chrome to be **logged into Dribbble**. Favoriting/collection actions are benign, reversible content-curation on the operator's own account, authorized by the operator. (The earlier human-check was cleared; login state must be confirmed before the collection flow.)
- **L8. Still open:** K2 (CSS-level elevation scope) was not resolved (the K2 slot carried new feedback); re-surfaced for decision.

---

## M. v2 - COLLAPSED lean architecture (operator: "collapse the doubling") - SUPERSEDES the doubled pipeline
The old design ran the 4 skills TWICE (D2 Phase-1 brief + F2/L3 Phase-3 convergence) = 9 spawns/run. Both reviewers (advisor + Codex gpt-5.5) rejected it as over-engineered + brittle. The 4 skills now run ONCE.

- **M1. Skills run ONCE -> ONE sourcing rubric.** 4 lens-isolated skill-agents (genuine, verified by `Skill` tool_use), grounded in the PCP (build files + `powerline.owloops.com` + tokens), run once and are synthesized into ONE **sourcing rubric**: queries + accept/reject criteria + per-element hunt-list. The rubric is BOTH the gather guide AND the selection criteria. [4 spawns]
- **M2. Dribbble gather AGAINST the rubric.** 1 curator agent, visible full-window browser, human cadence, gathers ~10-20 candidates per the rubric (queries, Filters->hex, Sort=Popular, Related branches), captures real `/shots/<id>` URLs + screenshots. It does NOT invoke skills mid-run - it uses the rubric. (Resolves the P1 skill-order contradiction; the curator agent def must be updated to drop mid-run skill invocation.) **NO Dribbble collections / account-writes** - deferred until search+login+save are manually proven stable for 3 consecutive runs (Codex P1). [1 spawn]
- **M3. Selection = operator + rubric. The 4-agent unanimous convergence is REMOVED.** Operator reviews candidate screenshots against the rubric and quick-rejects/selects. (Resolves: convergence-picked-a-logo contradiction = no convergence; unenforceable-gate = selection IS the operator gate.) **Hard per-element coverage:** >=1 selected ref for brand AND step-heads AND terminal-preview, or flag the gap and stop. -> `converge.workflow.mjs` is now OBSOLETE.
- **M4. Total reference spawns = 5** (4 rubric + 1 gather), down from 9. Matches the operator's mental model.
- **M5. CSS-scope clarified (K2 = loop markup + code-level CSS), no contradiction once scoped:** the LOOP stays carbonize-safe (markup, reuse classes, no new CSS - the producer's rule is correct FOR THE LOOP); I SEPARATELY author CSS/JS-level refinements in `style.css`/`app.js` against Almanac Noir, outside the loop. (Supersedes the I1/I2/L8 ambiguity.)
- **M6. Rubric caching (confirm):** produce the rubric ONCE per project + reuse; regenerate only if target files/design change (Codex P1). Supersedes K3's "every run" (which was specced for the now-removed doubled brief).
- **M7. Dribbble fallback:** if Dribbble flakes (bot-check / zero-shots / unreliable), fall back to **operator-provided trusted shot URLs** (the lean path both reviewers + the operator endorsed). Rubric + selection still apply.
- **M8. Flow (v2):** skills->rubric (once, cached) -> gather against rubric (visible, human cadence) -> **operator reviews + selects (rubric, hard per-element coverage)** -> elevation loop + code-level CSS, refs as context -> preview -> operator approves live.
