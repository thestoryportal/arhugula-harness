---
name: ship-pr
description: Use when the operator says /ship-pr, ship it, open the PR, land this, or asks Codex to package an already-built arhugula-v2 change for review and CI.
---

# Ship PR

Use this skill after implementation is complete and local verification is adequate.

## Preflight

1. Inspect `git status --short --branch`.
2. Review the diff with `git diff --stat` and targeted `git diff`.
3. Confirm no unrelated user changes are staged.
4. Run the narrow relevant checks and `just check` unless the change is documentation-only and a narrower gate is justified.

## PR Flow

1. Stage only intended files.
2. Commit with a concise conventional message.
3. Push the branch.
4. Create the PR with a body that includes:
   - summary of changes
   - verification commands and outcomes
   - any checks intentionally not run
   - design/back-flow notes if applicable
5. Watch CI with `gh pr checks` and address failures before claiming the PR is ready.

## Boundaries

- Do not merge unless the operator explicitly asks.
- Do not delete worktrees or branches containing unrelated active work.
