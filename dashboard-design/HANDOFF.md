# Handoff - Configurator Elevation workflow (v2), ready to EXECUTE

*Read this first. You've been launched into the isolated `dashboard-design/` workspace to EXECUTE the configurator-elevation workflow. This is the current-state + next-action layer on top of `dashboard-design/CLAUDE.md` (your governing context). The implementation is BUILT and verified; nothing has been executed yet.*

## Operating rules (this venue)
- cwd = `~/Projects/arhugula-v2/dashboard-design/` (MAIN checkout). Governing context = **`dashboard-design/CLAUDE.md` ONLY.** IGNORE the harness root `CLAUDE.md`, the roadmap (§12), and the `[ROADMAP]` / drift hooks - not this venue.
- Sandbox: work products land under `output/configurator-elevation/`. Never touch `tools/dashboard/generate.py`, `roadmap.html`, or port 8137.
- Almanac Noir design system: warm near-black ground `#15120d`, bone text `#e8e0cf`, single amber `#f0a830`, ember `#d8542f` alerts-only, hairlines `#3a342a`, 2px radius, Big Shoulders Display / IBM Plex Sans / JetBrains Mono. Warm-only; no glass/gradient/drop-shadow/rounded>2px. **Hyphens only, no em/en dashes.**

## The task
Visually ELEVATE the powerline statusline configurator UI. Live: `http://localhost:8770/`. Source: `~/.claude/powerline-config/static/`. Sandbox working copy: `output/configurator-elevation/target/`. Elements being elevated: brand masthead, 3 numbered step-heads, terminal-preview frame. (Upstream sibling for grounding: `https://powerline.owloops.com/`.)

## The workflow - CANONICAL = v2
- **Spec:** `output/configurator-elevation/REQUIREMENTS.md` **section M** (sections D/F/G/L are the SUPERSEDED v1 doubled pipeline - ignore them).
- **Runbook + data contract (READ THIS):** `output/configurator-elevation/v2/ORCHESTRATION.md` - the stage-by-stage execution guide with the artifact contract and gates.
- **Built + verified pieces:** curator agent `dashboard-reference-curator` (`.claude/agents/dashboard-reference-curator.md` - it auto-registers as an Agent type in a fresh session, so you can invoke it directly; it gathers against a rubric, never invokes skills, never selects - the operator selects); `v2/rubric-producer.md`; `v2/elevation-producer.mjs` (syntax-clean); `v2/ORCHESTRATION.md`.

## NEXT ACTION - start here
Execution begins at **Stage 1 in ORCHESTRATION.md: produce `v2/rubric.json`** - fire 4 lens-isolated skill-agents per `v2/rubric-producer.md`, synthesize, cache. **This is a PAID boundary - gate with the operator (surface the ~4-spawn cost) before firing.** Then: Stage 2 gather (visible browser) → Stage 3 operator selects → Stage 4 distill patterns → Stage 5 elevation (loop markup + code-level CSS) → Stage 6 preview → Stage 7 apply-to-live. Every paid stage gates; apply-to-live gates.

## Hard-won gotchas (do NOT relearn these)
- **Gather in the VISIBLE Chrome** (claude-in-chrome / `browser_batch`, full ~1600x1000 window) - NOT the `dribbble-mcp` server: its window opens tiny/flashing and the headless path hit bot-checks + returned nav-chrome junk. **Human cadence** (deep scroll, dwell between actions) both finds better refs AND dodges the bot-check.
- **Dribbble fallback (M7):** if it flakes (bot-check / zero shots), STOP and have the operator paste 3-5 trusted shot URLs into `candidates.json`. Do not thrash.
- **Verify-before-present:** prior subagent picks were internally inconsistent and a "logo" once slipped past a reject filter. Always re-ground a pick (view the real shot) before showing the operator. Real `/shots/<numeric-id>` URLs only - never invent.
- **Reviewer caution (advisor + Codex, both):** they judged the full reference pipeline over-engineered for what are only input images, and recommended a thin proof slice (one visible CSS change + before/after screenshot) over building everything. The operator chose to build full v2. Keep proportionality front of mind - the real goal is a visible UI change, and zero pixels have changed yet.
- **Env quirks:** `cp` is aliased `-i` (use `command cp -f`); `rm -rf` is guard-blocked (use `mv` to `_archive-*`); Bash cwd can drift (use absolute paths / `git -C`); prefix `_ZO_DOCTOR=0` to silence zoxide noise.

## State
Implementation BUILT + verified. Nothing executed (no `rubric.json`, no gather, zero pixels changed). v1 cruft archived to `output/configurator-elevation/_archive-v1/`. Start at Stage 1, gated.
