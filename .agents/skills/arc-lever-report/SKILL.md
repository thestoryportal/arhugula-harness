---
name: arc-lever-report
description: Read-only observability over the arc-metrics lever cohorts — whether the two self-improvement skills shipped at PR #1445 (defect-class-preflight, lever B-211; register-pr-prose, lever B-212) are actually improving arcs. Use WHENEVER the operator asks how the new skills are performing, whether arcs are improving, "/arc-lever-report", or the status of a lever/cohort/B-211/B-212. Runs `uv run python tools/arc_lever_report.py` and reports its output; never edits the ledger or the forward register.
---

# Canonical Claude Workflow Bridge

Read `.claude/skills/arc-lever-report/SKILL.md` completely from the workspace root before acting, including every reference it routes for the task. That canonical skill body is the full workflow; this Codex entrypoint does not summarize, trim, or replace it. Resolve its relative references from the canonical skill directory.

Apply these runner translations only:

- Root `AGENTS.md` is the Codex instruction entrypoint; targeted `CLAUDE.md` sections remain canonical lineage.
- Claude `Agent` or `Task` fan-out means fresh Codex subagents or `codex exec` contexts with self-contained briefs, subject to current delegation policy.
- `AskUserQuestion` means the available Codex user-input surface, and only for a genuine operator-owned fork.
- When Codex is the author, any canonical claim that Codex is out-of-family translates to Antigravity via `just gemini-review`; when Claude is the author, `just codex-review` remains out-of-family.
- Claude's transcript-brief-review judgment (a fresh-context Agent reviewer briefed on the session; CLAUDE.md §13.1) translates to the interactive Codex controller's transcript-aware judgment plus the required out-of-family artifact review; never silently drop either function.
- Claude-only scratch paths translate to a safe `/tmp` or ignored workspace scratch path. All Git, CI, worktree, paid-call, secret, and destructive-action guardrails remain binding.
