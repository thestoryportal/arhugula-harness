---
name: roadmap-continue
description: Use when the operator says /roadmap-continue, continue, next action, drive the roadmap, or otherwise asks Codex to advance the next arhugula-v2 roadmap item end to end.
---

# Roadmap Continue

Use this skill to run one concrete iteration of the workspace roadmap loop.

## Startup

1. Inspect `git status --short --branch`.
2. Read `.harness/roadmap_status.md`, `AGENTS.md`, `justfile`, and any relevant axis `AGENTS.md`.
3. Identify the next actionable item from the roadmap, not from memory alone.
4. For cite-bearing work, use the `overlay-query` skill before making implementation claims.

## Execution

1. Create or reuse an isolated worktree for substantive edits.
2. Ground nearby code and tests with `rg`, direct reads, and targeted test discovery.
3. If the next item is a design/spec/plan defect, route it as a back-flow arc and do not mix it with implementation.
4. Implement the smallest complete slice that advances the roadmap item.
5. Run narrow verification first, then `just check` when the change is PR-ready.
6. Commit, push, open a PR, and watch CI when the operator has authorized shipping in this session.

## Stop Conditions

- Stop and classify instead of coding when X-AL-3 would be violated.
- Stop before paid provider calls, credential movement, or destructive commands unless explicitly authorized.
- Preserve unrelated user changes.
