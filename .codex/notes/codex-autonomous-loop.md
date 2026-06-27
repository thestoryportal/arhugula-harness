# Codex Autonomous Loop

This note is the tracked, repo-local version of the controller/coder/validator/CI/closeout loop.

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

1. `preflight`
2. `plan`
3. `red` with `status=failed`
4. `implementation`
5. `narrow_verify`
6. `local_gate`
7. `decorrelated_review`
8. `closeout`

`just codex-review` remains the mandatory out-of-family review gate. CodeRabbit is optional advisory review through `just coderabbit-review ...`.
