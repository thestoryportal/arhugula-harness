---
name: defect-class-preflight
description: Pre-commit self-review sweep against the ten defect classes this workspace's reviewers actually catch, distilled from 1,084 real merge-gate and codex findings. Use BEFORE every commit of code in an arc — after writing or modifying any code under tools/ or harness-*/ and before invoking `just review-with-failover` or the merge-gate. Also use whenever about to claim a fix is complete, whenever a diff touches a shared surface (env variables, hooks, conftest, constants), and whenever a review round's fix is being committed (fixes introduce their own defects at a measured rate). Running this sweep is how a first draft survives review instead of generating BLOCK rounds — skipping it is how arcs run 9–17 review rounds.
---

# Canonical Claude Workflow Bridge

Read `.claude/skills/defect-class-preflight/SKILL.md` completely from the workspace root before acting, including every reference it routes for the task. That canonical skill body is the full workflow; this Codex entrypoint does not summarize, trim, or replace it. Resolve its relative references from the canonical skill directory.

Apply these runner translations only:

- Root `AGENTS.md` is the Codex instruction entrypoint; targeted `CLAUDE.md` sections remain canonical lineage.
- Claude `Agent` or `Task` fan-out means fresh Codex subagents or `codex exec` contexts with self-contained briefs, subject to current delegation policy.
- `AskUserQuestion` means the available Codex user-input surface, and only for a genuine operator-owned fork.
- When Codex is the author, any canonical claim that Codex is out-of-family translates to Antigravity via `just gemini-review`; when Claude is the author, `just codex-review` remains out-of-family.
- Claude `advisor()` transcript judgment translates to the interactive Codex controller's transcript-aware judgment plus the required out-of-family artifact review; never silently drop either function.
- Claude-only scratch paths translate to a safe `/tmp` or ignored workspace scratch path. All Git, CI, worktree, paid-call, secret, and destructive-action guardrails remain binding.
