---
name: c1-orchestration-control
description: Use when the operator names C1 or asks about agent-harness orchestration, topology, control flow, or subagent boundaries.
---

# Canonical Claude Workflow Bridge

Read `.claude/skills/council/c1-orchestration/SKILL.md` completely from the workspace root before acting, including every reference it routes for the task. That canonical skill body is the full workflow; this Codex entrypoint does not summarize, trim, or replace it. Resolve its relative references from the canonical skill directory.

Apply these runner translations only:

- Root `AGENTS.md` is the Codex instruction entrypoint; targeted `CLAUDE.md` sections remain canonical lineage.
- Claude `Agent` or `Task` fan-out means fresh Codex subagents or `codex exec` contexts with self-contained briefs, subject to current delegation policy.
- `AskUserQuestion` means the available Codex user-input surface, and only for a genuine operator-owned fork.
- When Codex is the author, any canonical claim that Codex is out-of-family translates to Antigravity via `just gemini-review`; when Claude is the author, `just codex-review` remains out-of-family.
- Claude `advisor()` transcript judgment translates to the interactive Codex controller's transcript-aware judgment plus the required out-of-family artifact review; never silently drop either function.
- Claude-only scratch paths translate to a safe `/tmp` or ignored workspace scratch path. All Git, CI, worktree, paid-call, secret, and destructive-action guardrails remain binding.
