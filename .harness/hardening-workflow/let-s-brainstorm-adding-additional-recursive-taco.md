# Plan — Hooks-driven Autonomy + Self-Improvement Infrastructure

## Context

The workspace already runs a highly autonomous "continue" roadmap loop, but continuation is **operator-initiated** (you reopen a session; the SessionStart hook injects state; Claude derives next-action). Two hooks exist today: `SessionStart` (roadmap audit) and the `PostToolUse(Bash)` refresh-reminder built in the prior session (PR #264). The Claude insights report (2026-06-02) independently flagged the exact next steps — Hooks, Custom Skills, Headless Mode, fixed-point-refresh codification, empirical-grounding rituals, token-cap mitigation, and self-healing loops.

This plan turns the 14 goals + every insights-report recommendation + the Codex/Advisor/council changes into a single comprehensive set of **atomic units** (one independently-implementable, independently-testable unit per PR — mirroring the workspace's own `U-<axis>-NN` discipline, so there is no drift and each lands clean). It uses the Claude Code hooks substrate (31 events; grounded against both the official `code.claude.com/docs/en/hooks` reference and the practical `claudefa.st/blog/tools/hooks/hooks-guide`).

**Ratified decisions (this session):**
1. **Guardrailed autonomy** — auto-decide all reversible/in-repo choices via Codex+Advisor; auto-approve non-destructive tools in loop mode; **HARD-STOP** only for paid calls, secret relocation, destructive/irreversible git, and missing creds/vendor (log to loop-status, keep working around). Self-improving CLAUDE.md lands via PR, never silent.
2. **Codex default, Advisor narrow niche** — Codex = default reviewer for code/diffs/pre-merge; Advisor retained only for (i) the #6 dual-decision and (ii) transcript-aware decision-fork sanity (its unique value: it sees the full transcript; Codex doesn't).
3. **Both loop models** — in-session `Stop`-hook auto-continue **and** a headless `claude -p` overnight runner.
4. **One comprehensive plan, implemented in 3 waves, decomposed into atomic units.**

## Status — ✅ COMPLETE (Waves 1–3 shipped, U-HK-01..25)

All three waves are merged to `main` as of 2026-06-03:

| Wave | Units | PR | Merge | Notes |
|---|---|---|---|---|
| **Wave 1 — always-on hooks** | U-HK-01..10 | #266 | `4d0baee` | Codex gate 5 rounds → 0; Hook A went live + self-validated on its own merge. |
| **Wave 2 — loop-mode autonomy** | U-HK-11..17 | #268 | `574f333` | OFF by default (`loop_mode_active()`); operator-authorized (tripped the auto-mode classifier — needed explicit human direction); Codex gate 12 rounds / ~30 bypasses fixed. Residuals documented at `.harness/wave2-hooks-status.md`. |
| **Wave 3 — self-improvement + Codex/council + prompt/skill** | U-HK-18..25 | #270 | `3a71e39` | Low-blast-radius (docs + advisory hooks + skills). Codex gate 3 → 0. Status at `.harness/wave3-hooks-status.md`. |

**As-built deviation from "Ratified decision 2" (Codex default / Advisor narrow):** at U-HK-18 the literal "Codex *replaces* Advisor" framing was **not** adopted — R-600 (the Codex pilot) was still ACTIVE (its keep/expand/drop A/B unfinished) and "replaces" contradicts the decorrelation thesis the shipped `/resolve` already encodes. Surfaced as one operator `AskUserQuestion` → ratified **"keep both" (division of labor)**: Codex = default out-of-family code/diff reviewer; advisor = transcript-aware decision-fork half; neither replaces the other; the strongest signal is when they disagree. Encoded at CLAUDE.md §13.1/§13.2.

Each wave was driven through the out-of-family `just codex-review` gate to convergence and a §12.2.1 terminating dashboard refresh after merge. The per-unit detail below is preserved as the authored record.

## Architecture (the load-bearing primitives)

- **`tools/hooks/lib.sh`** — one shared library (extracted from the two existing hook scripts' conventions) every new hook sources: JSON `emit()` (`hookSpecificOutput`), stdin JSON parse, the bounded-run watchdog (portable, stock-macOS-safe), and `loop_mode_active()` detection. **This is the anti-drift keystone** — all hooks share one tested helper instead of re-implementing.
- **Loop-mode gate** — a single flag (`.harness/.loop-active` file + `HARNESS_LOOP=1` env). The autonomy hooks (auto-approve, Stop-continue) are **inert unless loop mode is on**, so normal interactive sessions are never auto-driven. Lighting it up is an explicit act (a `/loop-start` skill or the headless runner sets it).
- **The hard-stop boundary** — a `PreToolUse` deny-list enforced **even in loop mode**: paid external calls, secret/`.env` relocation, `git push --force`/history-rewrite on main, `rm -rf`, branch deletion of un-merged work. These never auto-fire; they log to `.harness/loop_status.md` and the loop works around them. This preserves `[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`.
- **Codex+Advisor decision resolver** — uses the hook `prompt`/`agent` types (and the `just codex-review` recipe): both run; agree → auto-decide; disagree → take the safer/reversible default + log the split to loop-status for your later review.
- **Per-unit shape** — every hook unit = a script in `tools/hooks/` + `.claude/settings.json` wiring + a **hermetic test** (own fixture, never rots — the proven `test_post_merge_refresh.sh` pattern) + a roadmap `R-NNN`/memory entry. PR-per-unit; CI green before merge; follow-on terminating refresh.

## Atomic units

Each unit: **what** · **hook event** · **files** · **acceptance criteria (AC)** · **deps** · **test**. Goal-coverage map at the end confirms nothing is dropped.

### Wave 1 — Always-on hooks (zero autonomy risk; cheap friction wins) — ✅ SHIPPED (PR #266 `4d0baee`)

**U-HK-01 — Shared hook library.** `tools/hooks/lib.sh`: `emit()`, `read_tool_input()`, `bounded()` watchdog, `loop_mode_active()`. Refactor `session-start.sh` + `post-merge-refresh.sh` to source it (behavior-preserving). · Foundation · AC: both existing hooks' tests still 6/6 + a new `test_lib.sh` unit-tests each helper · deps: none.

**U-HK-02 — CLAUDE.md report-rec additions.** Add the insights-report CLAUDE.md items: a concise `## Roadmap Protocol` pointer (defer to §12), "always use AskUserQuestion not [y/n]", "clear stale caches before concluding from no-output", "large doc writes go incrementally to file, not heredoc/base64", and the token-cap "chunk large outputs" discipline. · No hook · files: root `CLAUDE.md` · AC: sections present + cross-ref §12/§13; mode-agnostic · deps: none.

**U-HK-03 — Stale-cache guard.** `PreToolUse(Bash)`: when the command is pytest/build, clear `__pycache__`/`*.pyc` first (the `.pyc` trap the report's fun-fact + friction #3 names). Advisory, fast, idempotent. · files: `tools/hooks/precmd-clear-cache.sh` + settings · AC: fires only on test/build commands; no-op otherwise; hermetic test · deps: 01.

**U-HK-04 — Lint-on-edit.** `PostToolUse(Edit|Write)`: run `ruff check` (+ format check) on the edited file; inject findings as `additionalContext` (non-blocking — PostToolUse can't undo). · files: `tools/hooks/postedit-lint.sh` + settings · AC: emits findings for a dirty file, silent for clean; scoped to the touched path · deps: 01.

**U-HK-05 — Pre-compaction checkpoint.** `PreCompact` with `async: true`: snapshot roadmap state + a `/context-save`-equivalent to `~/.gstack/.../checkpoints/`; dual-trigger (also a token-threshold proactive save per the claudefa.st StatusLine pattern). · files: `tools/hooks/precompact-checkpoint.sh` + settings · AC: checkpoint file written before compaction; async (non-blocking); manual-vs-auto matcher · deps: 01.

**U-HK-06 — Post-compaction re-inject.** `PostCompact` + `SessionStart(source=compact)`: re-inject roadmap next-action + the latest checkpoint pointer so context survives compaction. · files: `tools/hooks/postcompact-reinject.sh` + settings · AC: additionalContext carries next-action + checkpoint path · deps: 01, 05.

**U-HK-07 — Failure + token-cap capture.** `PostToolUseFailure` + `StopFailure`: log tool failures + API errors (esp. `max_output_tokens`, `rate_limit`) to `.harness/session-issues.jsonl`; flag cardinality-≥2 patterns as memory candidates (goal #3 — session learning). · files: `tools/hooks/capture-failure.sh` + settings · AC: appends structured rows; surfaces a memory-candidate note when a pattern repeats · deps: 01.

**U-HK-08 — Prompt context injector.** `UserPromptSubmit`: inject current roadmap next-action + drift status into every prompt (persistent context within a running session; goal #1/#2). Fast (<30s budget). · files: `tools/hooks/prompt-context.sh` + settings · AC: additionalContext present; never blocks; reuses the §12.1 hash recipe via lib · deps: 01.

**U-HK-09 — Session-end cleanup.** `SessionEnd`: archive resolved checkpoints, audit MEMORY.md against the 24.4 KB cap, prune merged worktrees/branches, emit a git-hygiene summary (goal #4). · files: `tools/hooks/session-end-cleanup.sh` + settings · AC: stale checkpoints moved to `checkpoints/archive/`; MEMORY.md cap reported; merged branches listed · deps: 01.

**U-HK-10 — Stop completion gate.** `Stop`: if code changed this turn, run scoped `just check` (lint/typecheck/test) + verify open tasks are complete; on failure `decision: block` so Claude fixes before stopping. **`stop_hook_active` guard** prevents loops. (goal #9.) · files: `tools/hooks/stop-gate.sh` + settings · AC: blocks on failing check, passes on green, never loops; hermetic test with synthetic stop payloads · deps: 01.

### Wave 2 — Autonomous loop + guardrailed permissions + Codex/Advisor resolver — ✅ SHIPPED (PR #268 `574f333`)

**U-HK-11 — Loop-mode flag + status ledger.** `.harness/.loop-active` gate + `HARNESS_LOOP` env + `.harness/loop_status.md` (records deferred genuinely-blocking HILs: creds/vendor/paid, what was completed-around, resume state). A `/loop-start` + `/loop-stop` skill toggles it. · files: `tools/hooks/loop_lib.sh`, `.harness/loop_status.md` template, `.claude/skills/loop-start|loop-stop/` · AC: flag detectable by lib; status ledger append API; off by default · deps: 01.

**U-HK-12 — Guardrailed auto-approve.** `PreToolUse` + `PermissionRequest`: in loop mode, safe-prefix allowlist auto-`allow`s non-destructive tools; the **hard-stop deny-list** (paid/secret/destructive/irreversible) `deny`s + logs to loop-status. Case-sensitive matchers, no `|` spaces (claudefa.st gotcha). **Inert when loop mode off.** (goals #12 + autonomy posture A.) · files: `tools/hooks/permission-guard.sh` + settings · AC: allowlist auto-approves; deny-list hard-stops + logs; zero effect outside loop mode; hermetic test covering allow/deny/off · deps: 01, 11.

**U-HK-13 — Codex+Advisor decision resolver.** Skill `/resolve` (+ optional `prompt`/`agent` hook): runs `just codex-review`/`codex exec` (out-of-family) **and** advisor (transcript-aware); agree → auto-decide + record rationale; disagree → pick the safer/reversible default, log the split to loop-status. (goal #6 core.) · files: `.claude/skills/resolve/SKILL.md`, `tools/hooks/resolve_lib.sh` · AC: both reviewers invoked; agreement auto-closes; disagreement logged + safe-default taken; paid/secret forks still hard-stop · deps: 11.

**U-HK-14 — In-session Stop-continue loop.** `Stop`: in loop mode + not `stop_hook_active` + not at a genuine gate → derive next-action (§4) + `decision: block` to continue; genuine gate (paid/secret/destructive/missing-cred) → stop + log to loop-status. Composes with U-HK-10 (gate must pass first). (goal #6.) · files: `tools/hooks/stop-loop.sh` + settings · AC: continues in loop mode, stops at gates, never infinite-loops (stop_hook_active), inert off-mode; hermetic test · deps: 01, 10, 11, 12, 13.

**U-HK-15 — Headless overnight runner.** `tools/loop/run.sh`: `claude -p "continue roadmap…"` with `--allowedTools`, loop-mode on, the guardrails, looping until a genuine gate; writes loop-status; reuses the existing `tools/dashboard/live-auto/orchestrator.mjs` headless pattern. A `just loop` recipe. (goal #6, Q3 headless.) · files: `tools/loop/run.sh`, justfile recipe · AC: runs a bounded N-item batch unattended, ships verified PRs, halts + logs at genuine ambiguity; dry-run mode for testing · deps: 11, 12, 13.

**U-HK-16 — Autonomous git-workflow guard.** `PostToolUse(git)` + `Stop`: enforce arc completeness (branch → commit → PR → CI-green → merge → refresh; no orphaned state, no work on stale main). Reuses the post-merge-refresh hook. (goal #5.) · files: `tools/hooks/git-arc-guard.sh` + settings · AC: flags uncommitted/unpushed/un-refreshed state at Stop; detects behind-origin main · deps: 01, 10.

**U-HK-17 — Subagent self-validation.** `SubagentStart` (inject the task's validation contract) + `SubagentStop` (validate output shape; `decision: block` → retry on malformed). (goal #13.) · files: `tools/hooks/subagent-validate.sh` + settings · AC: malformed subagent output blocked+retried once; valid passes; agent-type matchers · deps: 01.

### Wave 3 — Self-improvement + Codex/council + prompt/skill — ✅ SHIPPED (PR #270 `3a71e39`)

**U-HK-18 — Codex-replaces-Advisor wiring.** Update `CLAUDE.md` §13 (and the role-skill cross-refs) so Codex is the default reviewer; advisor narrowed to the #6 dual-decision + transcript-aware decision-fork sanity. Encode the decision-flow. (Advisor→Codex swap.) · files: `CLAUDE.md` §13, memory · AC: §13 reflects Codex-default; advisor niche documented; `[[advisor-before-substantive-work…]]` updated · deps: 13.

**U-HK-19 — Council + Codex multi-opinion.** Extend `council-orchestrator/SKILL.md` to optionally append an out-of-family **Codex decorator** after convening (concur / flag-gap on the convened tension) — not a 12th deliberating voice, a decorrelated cross-check. (council-Codex ask.) · files: `.claude/skills/council/council-orchestrator/SKILL.md` + references · AC: post-convening Codex section appears on tension; concur/flag format; opt-in · deps: 13.

**U-HK-20 — Self-improving CLAUDE.md optimizer.** Periodic skill (`/optimize-claude-md`, cadence ~N PRs or SessionEnd trigger): Codex+Advisor review CLAUDE.md files for optimization, **propose via PR** (CI + review catch regressions; never silent in-place per posture A). (goal #10.) · files: `.claude/skills/optimize-claude-md/SKILL.md` · AC: produces a reviewable diff PR, not an in-place edit; guarded against design-substrate (X-AL-3) · deps: 13, 18.

**U-HK-21 — Skill-activation validation.** `UserPromptExpansion` + a check that required skills fire when they should (and not when they shouldn't). (goal #7.) · files: `tools/hooks/skill-activation-check.sh` + settings · AC: warns on a slash-command/skill mismatch; silent when correct · deps: 01.

**U-HK-22 — Prompt optimization + validation.** `UserPromptSubmit` prompt-lint: flag under-specified/ambiguous prompts, optionally suggest a tightened form (goal #14). Advisory; composes with U-HK-08. · files: `tools/hooks/prompt-lint.sh` + settings · AC: flags a vague prompt with a suggestion; silent on well-formed · deps: 01, 08.

**U-HK-23 — Custom skills `/roadmap-continue` + `/ship-pr`.** Codify the loop ritual (ground → implement → PR → merge → fixed-point refresh) and the fixed-point-refresh checklist as one-command skills (report rec). · files: `.claude/skills/roadmap-continue/`, `.claude/skills/ship-pr/` · AC: each runs the documented checklist end-to-end · deps: 14, 16.

**U-HK-24 — Test-anchored self-healing.** `/self-heal` skill: clear caches → run full e2e/parametrized suite → root-cause failures (env-artifact vs logic) → fix → re-run to a verified fixed point; surface only genuine logic defects (report "On the Horizon" #3). · files: `.claude/skills/self-heal/SKILL.md` · AC: loops to green or surfaces a real defect with repro · deps: 03, 10.

**U-HK-25 — Parallel variant subagents + judge.** `/fan-out` workflow: N parallel design/impl subagents (distinct angles) + a judge agent scoring against a rubric; chunked outputs to dodge the token cap (report "On the Horizon" #2). Lower priority. · files: `.claude/skills/fan-out/SKILL.md` · AC: spawns N variants + returns a scored winner + rationale · deps: 17.

## Goal-coverage map (nothing dropped)

| Goal | Units |
|---|---|
| 1 Persistent context (running + fresh) | 06, 08, 05 (+ existing SessionStart) |
| 2 Drift prevention | 08, 10, 16 (+ existing audit) |
| 3 Session learning from issues | 07 |
| 4 Workspace cleanup (space/memory/git) | 09, 03 |
| 5 Autonomous git workflow | 16 (+ existing post-merge-refresh) |
| 6 No-HIL loop + Codex+Advisor on decisions | 11, 12, 13, 14, 15 |
| 7 Skill-activation hooks | 21 |
| 8 Pre-compaction | 05, 06 |
| 9 Test/build/lint/task gate before stop | 10 |
| 10 Self-improving CLAUDE.md | 20 |
| 11 Checkpointing throughout | 05, 09 (+ context-save) |
| 11b Hardened context recovery | 06, 08 (+ context-restore) |
| 12 Permissions for the loop | 12 |
| 13 Agent self-validation | 17 |
| 14 Prompt optimization + validation | 22 |
| Codex replaces Advisor | 18 |
| Council + Codex multi-opinion | 19 |
| Report: CC features / patterns / horizon | 02, 03, 04, 15, 23, 24, 25 + token-cap in 02/07 |

## Critical files (reused, not reinvented)

- `tools/hooks/lib.sh` (NEW keystone) — extracted from `tools/roadmap-audit/session-start.sh` + `post-merge-refresh.sh` conventions.
- `.claude/settings.json` — the hooks block (currently SessionStart + PostToolUse); each unit adds one event.
- `justfile` — existing `check`, `codex-review`/`_require-codex-subscription`; add `loop`.
- `.claude/skills/council/council-orchestrator/SKILL.md` — extend for Codex decorator (U-HK-19).
- `tools/dashboard/live-auto/orchestrator.mjs` — headless `claude -p` pattern to reuse (U-HK-15).
- `Project_Roadmap_v1.md` §5 + `.harness/roadmap_status.md` — each unit gets an `R-NNN` (a NEW **Surface VII / "autonomy infrastructure"** cluster) so it flows through the roadmap machinery.
- Memory: the two new Codex memories + `[[advisor-before-substantive-work…]]` updated at U-HK-18.

## Verification (end-to-end)

- **Per unit:** hermetic test (own fixture repo / synthetic stdin payloads, the `test_post_merge_refresh.sh` pattern) → `bash -n` + the test green → `just check` → `just codex-review` (out-of-family) → CI green → merge → terminating refresh.
- **Wave 1 gate:** open a normal session; confirm cache-clear, lint-on-edit, prompt context-injection, pre/post-compact, failure-capture, and the Stop gate all fire correctly and stay quiet when they should — **with loop mode OFF (no auto-drive).**
- **Wave 2 gate:** `/loop-start` → run a bounded batch; confirm auto-approve only fires for safe tools, the hard-stop deny-list blocks + logs a paid/secret/destructive op, the Codex+Advisor resolver auto-decides on agreement and logs on disagreement, and `Stop`-continue halts at a genuine gate without infinite-looping (`stop_hook_active`). Then `just loop` headless dry-run.
- **Wave 3 gate:** confirm Codex is the default reviewer, the council Codex-decorator appears on a tension, and `/optimize-claude-md` produces a *reviewable PR* (never a silent edit).

## Risks / guardrails

- **Infinite loops:** every blocking Stop/Subagent hook checks `stop_hook_active` / a turn counter (claudefa.st warning). U-HK-14 is bounded.
- **Latency:** advisory hooks are fast + `async: true` where possible (compaction backup); the 30s/60s timeouts are respected.
- **Autonomy blast radius:** all auto-approve/auto-continue is **gated behind loop mode** (off by default); the hard-stop deny-list is enforced even in loop mode; CLAUDE.md self-edit only via PR. The paid-call/secret boundary is preserved verbatim.
- **Drift:** one shared `lib.sh`, PR-per-unit, hermetic tests, roadmap `R-NNN` per unit — the workspace's own anti-drift discipline.

## Open items (decide at implementation, not blocking the plan)

- Exact safe-allowlist vs hard-stop deny-list contents for U-HK-12 (draft at impl, Codex+Advisor-reviewed).
- Cadence for U-HK-20 optimizer and U-HK-15 batch size (operator-tunable).
- Whether U-HK-25 (parallel judge) lands this round or defers (lowest priority).
