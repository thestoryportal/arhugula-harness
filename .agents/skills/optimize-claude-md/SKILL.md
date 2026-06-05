---
name: optimize-claude-md
description: "Use when the operator asks to optimize, prune, trim, shrink, declutter, or context-budget audit arhugula-v2 CLAUDE.md governance files, including /optimize-claude-md."
---

# Optimize CLAUDE.md

Use this skill for governance-context pruning only. Do not edit design substrate, specs, plans, ADRs, or fork docs under this skill.

## Scope

Allowed targets:

- root `CLAUDE.md`
- per-axis `harness-{is,as,cp,od}/CLAUDE.md`
- pointer/index files under `.harness/` that preserve relocated context
- Codex projections such as `AGENTS.md` when the task explicitly includes Codex compatibility

Out of scope:

- `design-substrate/**`
- implementation code
- formal specs, plans, ADRs, and fork docs

## Workflow

1. Inspect `git status --short --branch`.
2. Read `AGENTS.md`, `.harness/roadmap_status.md`, and the target governance file.
3. Measure the target size with a stable local command such as `wc -w` or a tokenizer script if one exists.
4. Relocate or summarize verbose lineage into a pointer file when needed; keep load-bearing rules in the active guidance.
5. Preserve authoritative pointers and exact filenames for relocated material.
6. Verify pointer integrity with `rg` and a targeted read of the relocated file.
7. Open a reviewable PR; do not make silent governance edits on `main`.

## Quality Bar

- The active guidance should remain sufficient for a fresh Codex session to avoid X-AL-3, destructive git, paid-provider, and verification mistakes.
- Relocation beats deletion when lineage may still be operationally useful.
- Report before/after size and the verification command used.
