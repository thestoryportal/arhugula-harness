---
name: loop-start
description: Turn ON autonomous loop mode for the harness workspace (Wave 2 U-HK-11). Use when the operator says "/loop-start", "start the loop", "go autonomous", "run unattended", "drive the roadmap without me", or otherwise authorizes the guardrailed auto-approve / auto-continue tier. Activating loop mode lights up the Wave-2 autonomy hooks (guardrailed permission auto-approve U-HK-12, in-session Stop-continue U-HK-14) which are INERT by default. Do NOT use to merely answer a question about loop mode — only to actually enable it.
---

# loop-start — enable autonomous loop mode

Lights up the Wave-2 autonomy tier. The auto-approve permission guard (U-HK-12) and
the Stop-continue loop (U-HK-14) are **inert unless loop mode is on** — this skill is
the explicit act that turns them on, so normal interactive sessions are never
auto-driven.

## What it does

1. Creates the `.harness/.loop-active` marker (detected by `loop_mode_active()` in
   `tools/hooks/lib.sh`) and logs an `ACTIVATE` row to `.harness/loop_status.md`.
2. Reaps stale merged worktrees (U-HK-26 `loop_gc_worktrees`) — the in-session
   activation case the SessionStart hook can't cover (it already ran with loop mode
   off). Worktrees only, merged+clean+non-current; logged to the ledger.
3. From now until `/loop-stop`, the autonomy hooks fire: safe non-destructive tools
   auto-approve; the hard-stop deny-list still blocks paid calls / secret relocation /
   destructive git / missing creds and **logs them to the ledger to work around**.

## Run

```bash
source tools/hooks/lib.sh && source tools/hooks/loop_lib.sh && loop_activate "operator /loop-start"
loop_gc_worktrees reap   # U-HK-26: collect stale merged worktrees left by prior sessions
echo "loop mode: $(loop_mode_active && echo ON || echo OFF)"
```

## The guardrails (locked, even in loop mode)

These NEVER auto-fire — they hard-stop and log to `.harness/loop_status.md`, and the
loop works AROUND them (per `[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`):

- **Paid external calls** (live LLM inference, metered APIs) — surface, don't fire.
- **Secret / `.env` relocation** — never move credentials.
- **Destructive / irreversible git** — `push --force` / history rewrite on `main`,
  `rm -rf`, deletion of un-merged branches.
- **Missing creds / vendor gates** — log as `DEFERRED-HIL`, keep working on other items.
- **CLAUDE.md self-edits** — only via PR, never silent in-place.

## After enabling

State that loop mode is ON and begin driving the roadmap next-action per `CLAUDE.md`
§12 (ground → implement with tests → PR → CI-green → merge → fixed-point refresh),
auto-deciding reversible in-repo choices via the `/resolve` resolver (U-HK-13) and
continuing across turns until a genuine gate. Run `/loop-stop` to disable.
