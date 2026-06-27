# Codex Autonomous Loop

This note is the tracked, repo-local version of the controller/coder/validator/CI/GitHub shipping/closeout loop.

Command surface:

```bash
just codex-autonomous-arc ARC_ID
just codex-loop-record --phase red --status failed --command "..." --evidence "..."
just codex-loop-status
just codex-loop-check
just coderabbit-review --base main
```

The local state file is `.harness/codex_loop_state.json` and is gitignored. It is evidence for the current run, not a source file.
Each record captures branch, HEAD, and a worktree fingerprint; if the diff changes after a gate, re-record that gate and all downstream gates.

Required gates:

1. `worktree_ready`
2. `preflight`
3. `plan`
4. `red` with `status=failed`
5. `implementation`
6. `narrow_verify`
7. `local_gate`
8. `decorrelated_review`
9. `closeout`
10. `commit`
11. `push`
12. `pr_opened`
13. `ci_green`
14. `merged`
15. `post_merge_refresh`
16. `main_synced`
17. `worktree_disposition`

`just codex-closeout` verifies the pre-closeout subset through
`decorrelated_review`. `just codex-loop-check` verifies the full lifecycle,
including commit, push, PR, CI, merge, post-merge refresh, main sync, and
worktree disposition evidence. The `worktree_ready` gate must be recorded from
a linked worktree; the final `worktree_disposition` gate must be recorded from
synced `main` after the original arc worktree is no longer registered and the
local topic branch has been pruned.

`just codex-review` remains the mandatory out-of-family review gate. CodeRabbit is optional advisory review through `just coderabbit-review ...`.
