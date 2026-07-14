# AGENTS.md — Codex Compatibility Layer

This repository is developed primarily with Claude Code CLI. For Codex, this file is the authoritative compact projection of the project rules. The canonical governance remains in `CLAUDE.md`; load it only for targeted sections or exact lineage, not as default context.

## Startup Context

- Read `.harness/roadmap_status.md`, `justfile`, `.codex/notes/codex-compatibility-outline.md`, and the relevant local `AGENTS.md` before substantive work.
- Read `.codex/notes/deterministic-context-workflow.md` and run `just codex-preflight` before substantive work. This writes the required local context checkpoint.
- For axis-specific work, read the closest `harness-{is,as,cp,od}/AGENTS.md` first; consult the matching `CLAUDE.md` only when exact Claude lineage or axis posture is needed.
- For `C-*`, `U-*`, `H_T-*`, ADR, or CXA seam claims, ground with the semantic overlay instead of free-form recall.

## Working Pattern

- Use isolated worktrees for substantive edits. Prefer external or ignored worktree directories; `.codex-worktrees/` is ignored for operator-created local worktrees.
- Do not edit `design-substrate/**`, specs, plans, ADRs, or fork docs in the same arc as implementation files unless the task is explicitly a design-phase/back-flow arc.
- Do not run paid provider calls, credential-moving commands, destructive git commands, or network-dependent actions without explicit operator authorization.
- For credential-gated units, build to the exact credential boundary, prove all non-credential forward actions are closed, then log the gate with `just codex-credential-gate --unit ... --gate ... --forward-closed ... --resume ...` if no HIL/operator-approval surface is available. Update a human-facing tracking surface so the pending gate is visible on the next human engagement, then proceed to the next implementable unit.
- Preserve user work. Do not revert unrelated changes.
- Re-run `just codex-preflight` after long work, merges, rebases, resumes, or compaction; memory/checkpoints are advisory until re-grounded against HEAD. Use `just codex-checkpoint <label>` for explicit mid-arc context checkpoints.
- For autonomous coding arcs, initialize the controller/coder/validator/GitHub-shipping evidence loop with `just codex-autonomous-arc <arc-id>`, record gates with `just codex-loop-record ...`, and require `just codex-loop-check` before claiming the loop complete. Gate evidence is branch/HEAD/linked-worktree/worktree-fingerprint-bound; after a pre-commit diff change, re-record the affected gate and downstream pre-commit gates. The full loop is not complete until commit, push, PR, CI, merge, post-merge refresh or explicit non-applicability, local main sync, and worktree disposition are recorded; final disposition must prove the original arc worktree is no longer registered and the local topic branch is pruned.

## Claude-Native Context Mapping

- Claude `CLAUDE.md` files map to Codex `AGENTS.md` projections.
- Claude hooks map to `.codex/hooks.json` plus scripts under `.codex/hooks/`.
- Claude skills map to Codex repo/user skills under `.agents/skills` or installed Codex skills; package as plugins only when distribution is needed.
- Claude memory remains Claude-owned. Codex durable team rules belong here; Codex local memories are optional generated state under `CODEX_HOME`.

## Verification

- Start with the narrowest meaningful test or static check.
- For PR-ready code or governance changes, run `just check` unless the change is documentation-only and a narrower documented gate is sufficient.
- For governance/context changes, also verify instruction discovery or pointer integrity when applicable.
- For roadmap/status changes, update `.harness/roadmap_status.md` directly (recompute `workspace_state_hash`, `recently_completed`, `next_action` per CLAUDE.md §12.2); do not hand-maintain volatile facts inconsistently with the recipe there.
- Run `just codex-closeout` before final response, commit, or PR; it writes a fresh pre-closeout checkpoint and hard-fails if the guard cannot verify it. Resolve hard findings and report warnings explicitly.
- If `.harness/codex_loop_state.json` exists, closeout also verifies the active autonomous loop has reached every pre-closeout gate from linked worktree readiness through decorrelated review.
- Before claiming green, report exactly which checks ran and which did not.

## PR Discipline

- Every substantive Codex setup change should land on a branch and open a PR.
- Strict CI gates are required: lint, typecheck, tests, semantic overlay, substitution ledger, and axis isolation when CI provides them.
- `just codex-review` is for out-of-family review of concrete diffs; it complements Claude advisor review and does not replace transcript-aware advisor judgment.
- PR bodies must name tracking surfaces updated or explicitly state why roadmap/status/ledger updates were not applicable.
