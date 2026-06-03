# Wave 3 hooks — outcome

*Status record for the U-HK-18..25 "self-improvement + Codex/council + prompt/skill"
wave of the hooks plan
(`~/.claude/plans/let-s-brainstorm-adding-additional-recursive-taco.md` §Wave 3).
Mode-agnostic / process-substrate. 2026-06-03.*

## TL;DR

**All 8 Wave 3 units shipped** (U-HK-18..25). Wave 3 is the low-blast-radius tier:
docs + advisory hooks + skills — **no auto-approve / headless machinery** (that was
Wave 2). Two advisory `UserPromptSubmit` hooks (silent-when-correct) + six doc/skill
units. Nothing auto-drives; the two new hooks only inject advisory context.

## Shipped

| Unit | What | Test / verify | Wiring |
|---|---|---|---|
| **U-HK-18** | Codex/advisor **division of labor** in CLAUDE.md §13.1 + §13.2 matrix + §13.5 + memory. Operator-ratified (AskUserQuestion 2026-06-03) **"keep both"** — Codex = default out-of-family diff reviewer; advisor = transcript-aware decision-fork half. NOT "replaces" (the U-HK-18 title was aspirational; R-600 pilot still ACTIVE). | cites resolve | CLAUDE.md, memory |
| **U-HK-19** | council-orchestrator §5b **Codex decorator** — opt-in out-of-family cross-check (concur / flag-gap) on a convened tension; not a 12th voice. | skill review | council SKILL.md |
| **U-HK-20** | `/optimize-claude-md` — self-improving governance docs. **Two hard invariants: PR-only (never silent in-place) + NEVER `design-substrate/**`** (baked into the body). | skill review | skill |
| **U-HK-21** | `skill-activation-check.sh` (`UserPromptSubmit`) — warns on a mistyped `/slash-command` (near-miss of a real skill); silent on knowns/built-ins/namespaced. | 8/8 hermetic | settings.json |
| **U-HK-22** | `prompt-lint.sh` (`UserPromptSubmit`) — flags a bare deictic/contentless prompt ("fix it"); silent on every idiom ("continue") + command + context-bearing prompt. | 17/17 hermetic | settings.json |
| **U-HK-23** | `/roadmap-continue` + `/ship-pr` — the loop ritual + the §12.2.1 fixed-point refresh checklist, **citing §12 by section** (no drifting hard-coded recipe). | skill review | skills |
| **U-HK-24** | `/self-heal` — cache-clear → run suite → triage env-artifact vs logic → fix → re-run to verified green; surfaces only real defects (never fires a paid call to "pass" a credential-skip). | skill review | skill |
| **U-HK-25** | `/fan-out` — N parallel variant subagents (distinct angles) + a judge against a rubric; chunked output (§14.5). Lower priority; landed clean. | skill review | skill |

## Safety posture

- **Below the Wave-2 line.** No auto-approve, no headless runner, no permission-bypass.
  The two new hooks are **advisory** (`UserPromptSubmit` additionalContext only) and
  **silent-when-correct** — they never block and never auto-decide.
- **Three hooks now share `UserPromptSubmit`** (prompt-context U-HK-08 + skill-check U-HK-21
  + prompt-lint U-HK-22). Verified they **compose** (each emits its own additionalContext,
  no clobber) at **0.26s combined** — well under the 30s budget.
- **U-HK-20 self-edit is PR-only + design-substrate-excluded** by enforced invariant — the
  agent never silently rewrites its own governance, and never crosses the X-AL-3 line.
- **Paid-call / secret boundary preserved verbatim** across every new skill
  (`[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`). Codex is
  $0 ChatGPT-subscription dev tooling (X-AL-1), not a paid harness call.

## U-HK-18 operator decision

The unit title said "Codex-**replaces**-Advisor", but R-600 is still an **ACTIVE pilot**
(the decorrelation A/B hasn't produced its keep/expand/drop data) and its own thesis +
the shipped `/resolve` treat the two as decorrelated complements. Surfaced as one batched
`AskUserQuestion`; operator chose **division of labor (keep both)**. §13 encodes Codex as
the default out-of-family *artifact/diff* reviewer and advisor as the transcript-aware
*decision-fork* reviewer — neither replaces the other; the strongest signal is when they
disagree.

## Verification

`bash -n` on both new hooks + **17/17 hook test suites green** (the 15 prior + the 2 new,
no regressions) + settings.json valid + every CLAUDE.md `§`-cite in the new skills resolves
+ 3-hook `UserPromptSubmit` composition + latency checked. Driven through `just codex-review`
(out-of-family) pre-merge.

## Operating it

- `/optimize-claude-md` — propose a CLAUDE.md tidy as a reviewable PR (periodic / on friction).
- `/roadmap-continue` + `/ship-pr` — the one-command loop + fixed-point-refresh ritual.
- `/self-heal` — drive the suite to a verified green, env-artifact-aware.
- `/fan-out` — N variants + judge for a wide-open design fork.
- council Codex decorator — append `just codex-review` / `resolve_codex` after a convened tension.
