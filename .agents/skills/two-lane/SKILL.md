---
name: two-lane
description: Use only when the operator explicitly asks for two parallel arcs — two lanes build concurrently in their own worktrees while every merge and every terminating refresh stays strictly serial through the shipping flow.
---

# Canonical Claude Workflow Bridge

Read `.claude/skills/two-lane/SKILL.md` completely from the workspace root before acting, including every reference it routes for the task. That canonical skill body is the full workflow and the source of truth for the lane setup, the strictly-serial merge lane, the one-lane-holds-the-fixed-point rule, the abandon-and-rebase conflict rule, the guard-approved reaping path and the deliberate CUTs; this Codex entrypoint does not summarize, trim, or replace it. Resolve its relative references from the canonical skill directory.

Apply these runner translations only:

- Root `AGENTS.md` is the Codex instruction entrypoint; targeted `CLAUDE.md` sections remain canonical lineage. The canonical body's §12 citations resolve against `CLAUDE.md` — §12 is unchanged by this skill in either runner.
- A "lane" here is one non-interactive `codex exec --profile arhugula-implementer` leg in its own `.codex-worktrees/<leg-id>` worktree, driven from one orchestrator session per `AGENTS.md:29-31`; two lanes is exactly the standing concurrency cap of 2 on the reference machine (`AGENTS.md:31`), so this recipe never justifies a third.
- The canonical `ship-pr` fixed point maps to this flow's autonomous-loop gates: the merge, post-merge-refresh, local-main-sync and worktree-disposition gates recorded with `just codex-loop-record` and verified by `just codex-loop-check` (`AGENTS.md:25`). The serial constraint is therefore: lane B records no merge gate until lane A's post-merge-refresh gate is recorded and its terminating refresh has actually merged. Gate evidence is branch/HEAD/worktree-fingerprint-bound, so a lane that waits must re-record any gate whose diff moved while it waited.
- Where the canonical body would surface a decision through `AskUserQuestion`, use this runner's operator-input surface instead — and where no HIL surface is available, log the gate per the `AGENTS.md` credential/HIL gate convention rather than deciding unilaterally.
- The canonical reaping step is unchanged in mechanism: remove a finished lane's worktree with `tools/hooks/safe-worktree-remove.sh <worktree>` and treat a nonzero exit as a real refusal. The autonomous loop's final disposition gate already demands the arc worktree be unregistered, so this is the same call the loop owes anyway, not an extra step.
- Invocation stays operator-request-only: never chain this skill automatically from roadmap-continue, ship-pr, or the autonomous loop. All Git, CI, worktree, paid-call, secret, and destructive-action guardrails remain binding — in particular the `git rebase` and forced-branch-deletion denials the canonical body relies on.
