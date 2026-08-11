# R-CTX-1 errata E7 — machine-local orchestrator step (execution record)

*Filed 2026-08-11 by the loop orchestrator session (06fb5dd9). This is the E7
"orchestrator post-merge acceptance step" owed since PR #1299 merged
(`.harness/r-ctx-1-implementation-plan-v1.md` U-CTX-17 errata E7): the machine-local
half of the 21-name removal roster that the tracked-state CI test
(`tools/test_codex_workflow_parity.py::test_r_ctx_1_removed_skill_roster_is_21_and_absent_from_tracked_state`)
deliberately does not cover.*

## E7 ordered procedure — status

| Step | Status |
|---|---|
| (1) PR-6 (#1299) merges the `.gitignore` R3 entries | DONE — 12 `bmad-*` entries at `.gitignore:92-103` |
| (2) Orchestrator deletes local payload dirs in the root checkout | **PARTIAL** — 12 machine-local `bmad-*` dirs + 5 tracked `bmad-*` dirs verified ABSENT on disk 2026-08-11; the **4 design-skill dirs are still PRESENT** (see below) |
| (3) Orchestrator removes the now-redundant `.git/info/exclude` entries | DONE — `.git/info/exclude` verified 2026-08-11 to carry zero `bmad`/design-skill entries (only worktree + claude-code-runtime lines) |

## On-disk 21-name verification (root checkout, 2026-08-11)

17/21 absent; 4 present:

- ABSENT: all 12 machine-local `bmad-*` names (derived from the `.gitignore` R3 block) and all 5 tracked `bmad-*` names (`bmad-agent-pm`, `bmad-prd`, `bmad-prfaq`, `bmad-product-brief`, `bmad-technical-research`).
- PRESENT (untracked, never in git history): `.claude/skills/frontend-design/`, `.claude/skills/impeccable/`, `.claude/skills/taste-skill/`, `.claude/skills/ui-ux-pro-max/`.

No copies exist under repo `.agents/skills/`; `~/.codex/superpowers`, CodeRabbit
surfaces, and `~/.agents/skills` untouched per U-CTX-17.

## Why the 4 remaining dirs matter (measurement coupling)

Their SKILL.md `description:` fields total 2,531 bytes (412 + 908 + 282 + 929)
and are injected into every session's skills listing — ≈600–700 tokens of
preload. The first eligible post-slim cold-start measured **76,656** against the
B-148 ≤76,000 gate (miss = 656 tokens), so this removable mass is decisive for
the gate. See `.harness/r-ctx-1-u-ctx-21-measurement-2026-08-11.md`.

## Blocked removal + operator command (reversible)

The orchestrator's reversible removal (`mv` to a dated backup under `~/.claude/`)
was **denied by the auto-mode permission classifier** (2026-08-11T04:19Z; logged
DEFERRED-HIL at `.harness/loop_status.md`). Per the permission-aware-operation
rule the command was not retried in variant forms. Operator command (reversible —
a move, not a delete):

```bash
mkdir -p ~/.claude/removed-skills-backup-2026-08-11
mv ~/Projects/arhugula-v2/.claude/skills/{frontend-design,impeccable,taste-skill,ui-ux-pro-max} \
   ~/.claude/removed-skills-backup-2026-08-11/
```

Restore recipe (if any skill should return):

```bash
mv ~/.claude/removed-skills-backup-2026-08-11/<name> ~/Projects/arhugula-v2/.claude/skills/
```

After the move, the next fresh `*/cli` session re-measures the B-148 gate via
`just context-budget --sessions 1` (expected ≈76,656 − ~650 ≈ 76.0k, i.e. at or
under the gate).

## Ratification trace

- D2 (design-skills + bmad removal both runners) — the 4 design dirs are the
  "4 operator-installed design skills" of the 21-name roster
  (`tools/test_codex_workflow_parity.py:1029`).
- R3 (12 machine-local bmad payloads: `.git/info/exclude` → `.gitignore` +
  documented reversible local removal) — steps (1)/(3) above.
- E7 (venue split: tracked half in PR-6 CI; machine-local half as this
  orchestrator acceptance step) — `.harness/r-ctx-1-implementation-plan-v1.md:64`.
