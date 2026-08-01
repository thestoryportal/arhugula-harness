# Codex Compatibility Outline

This note codifies the operator-approved Codex setup direction for this repository.

## Durable Setup Sequence

1. Add root `AGENTS.md` as the compact Codex-authoritative projection of `CLAUDE.md`.
2. Add axis-local `AGENTS.md` files for `harness-is`, `harness-as`, `harness-cp`, and `harness-od`.
3. Add project `.codex/config.toml` for instruction discovery and hooks. Keep provider/auth/profile settings user-level.
4. Map every compatible Claude hook into Codex hooks, retaining the Codex-native
   boundary/context guards as additive checks. The full lifecycle table and the
   one non-event-exact gap (`StopFailure`) are documented in
   `.codex/hooks/README.md` and `.codex/notes/claude-codex-parity.md`.
   `SessionStart` and `Stop` run `tools/codex_context_guard.py` so context
   freshness, worktree isolation, roadmap status drift, and closeout obligations
   are materialized from HEAD instead of remembered. `SessionStart` preflight and
   failure to create the Stop checkpoint remain hard; an incomplete in-progress
   closeout is advisory at Stop and hard at explicit `just codex-closeout`.
5. Keep reusable workflows as Codex skills under `.agents/skills` or installed user skills. Package as plugins only for distribution.
   - Every one of the 35 tracked Claude skills has a Codex discovery entrypoint.
     Native Codex workflow skills carry runner-specific fixed-point gates; bridge
     skills preserve the complete canonical Claude body and translate only agent,
     question, scratch-path, and reviewer mechanics.
   - Operator-installed compatible design skills remain in the root checkout's
     `.claude/skills/` and are exposed through tracked Codex bridge entrypoints;
     their full source bodies are not deleted, copied, shortened, or deprecated.
6. Use `.codex/notes/deterministic-context-workflow.md` as the Codex source of
   truth for context-rot prevention; run `just codex-preflight` before work,
   `just codex-checkpoint <label>` at mid-arc re-grounding points, and
   `just codex-closeout` before final response, commit, or PR.
   - Credential-gated units advance to the credential boundary first. When no
     HIL/operator-approval surface is available, log the gate with
     `just codex-credential-gate ...`, update a human-facing tracking surface,
     and continue to the next implementable unit once non-credential work is
     proven closed.
   - For autonomous implementation arcs, start `just codex-autonomous-arc <arc-id>`;
     record controller/coder/validator/GitHub-shipping gates with
     `just codex-loop-record ...`; require `just codex-loop-check` before
     claiming the loop complete. The active local state lives at
     `.harness/codex_loop_state.json` and is intentionally untracked.
     The full lifecycle includes linked worktree readiness, closeout, commit,
     push, PR, CI, merge, post-merge refresh or explicit non-applicability,
     local main sync, and worktree disposition.
7. Run substantive Codex work in isolated worktrees and land changes through reviewable PRs with strict CI.
8. Validate instruction discovery with `codex --ask-for-approval never "Summarize the current instructions."` and nested `--cd` checks.
9. Query Claude's project memory index and gstack context checkpoints for relevant
   historical lessons, then verify every load-bearing claim against HEAD and the
   deterministic repo instruments.

## Memory Rule

Required team guidance belongs in `AGENTS.md` and checked-in docs. Claude memory
remains queryable historical evidence, and its mandatory runner-agnostic lessons
are distilled in `.codex/notes/discipline-digest.md`. Codex memories are optional
generated state under `CODEX_HOME`; neither memory store overrides current HEAD.
