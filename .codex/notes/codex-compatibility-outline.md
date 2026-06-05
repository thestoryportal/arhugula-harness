# Codex Compatibility Outline

This note codifies the operator-approved Codex setup direction for this repository.

## Durable Setup Sequence

1. Add root `AGENTS.md` as the compact Codex-authoritative projection of `CLAUDE.md`.
2. Add axis-local `AGENTS.md` files for `harness-is`, `harness-as`, `harness-cp`, and `harness-od`.
3. Add project `.codex/config.toml` for instruction discovery and hooks. Keep provider/auth/profile settings user-level.
4. Map load-bearing Claude hooks into Codex hooks:
   - `SessionStart`: roadmap/status and posture reminder.
   - `PreToolUse`: X-AL-3 and destructive-command boundary checks.
   - `PermissionRequest`: paid-provider, credential, destructive, and network review notes.
   - `Stop`: verification and PR-state reminder.
5. Keep reusable workflows as Codex skills under `.agents/skills` or installed user skills. Package as plugins only for distribution.
   - Repo-local shims now live under `.agents/skills/` for overlay queries, roadmap continuation, self-heal, PR shipping, and CLAUDE governance optimization.
6. Run substantive Codex work in isolated worktrees and land changes through reviewable PRs with strict CI.
7. Validate instruction discovery with `codex --ask-for-approval never "Summarize the current instructions."` and nested `--cd` checks.

## Memory Rule

Required team guidance belongs in `AGENTS.md` and checked-in docs. Codex memories are optional generated state under `CODEX_HOME`; do not hand-edit them as the primary rules surface.
