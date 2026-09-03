# Code implementation loop — Archify diagrams

Five self-contained HTML diagrams of the `continue` → build → review → merge → refresh loop this
workspace runs. Open any `.html` file directly in a browser; each is interactive (search, focus,
trace, dark/light, PNG/SVG export). The `.workflow.json` next to each is the typed source.

| File | Scope |
|---|---|
| `00-overview.html` | End to end: SessionStart audit → derive → build → codex-review round → gh pr create → PR CI → merge-gate → merge door (squash, main CI, refresh PR) → arc close. Blocked exits drawn: DRIFT halt, Codex BLOCK, merge-gate BLOCK, door blocked; the CI-red exit is drawn only in Phase C. Four guided views (Audit, Build, Review, Land). |
| `01-audit-derive.html` | Phase A: SessionStart hooks, hash compare, DRIFT halt, UserPromptSubmit hooks, `roadmap-continue` derivation, arc open, `arc_disjoint_check`, reservation. |
| `02-build.html` | Phase B: grounding, transcript-brief review, red-first tests, PreToolUse/PostToolUse hooks, `defect-class-preflight`, `graft callers`, `just codex-check`, commit, Stop hooks. |
| `03-review-gates.html` | Phase C: admission attestation, `review-with-failover-logged` round (exit 0/1/2/3), `gh pr create`, PR CI, scope + blast radius, the 3 merge-gate lenses, Agent hooks, gate rows, all-APPROVE vs BLOCK. |
| `04-merge-refresh.html` | Phase D: final-gate back-fill, `.next-action-draft`, `safe-merge.sh` → `merge_door.py` lease, squash merge, main CI, refresh continuation, terminating refresh PR, door blocked (exit 3), release, arc close-out. |

Sources grounded on 2026-09-03 against `.claude/skills/{roadmap-continue,ship-pr,merge-gate,
defect-class-preflight,resolve}/SKILL.md`, `.claude/settings.json`, `justfile`,
`tools/roadmap-audit/session-start.sh`, `tools/hooks/safe-merge.sh`, `tools/merge_door.py`,
and `tools/roadmap_status_refresh.py`.

Regenerate after editing a source:

```bash
cd ~/.claude/skills/archify
node bin/archify.mjs deliver workflow <name>.workflow.json <name>.html --quality showcase --json
```

`visual-check/` holds the browser-evidence sidecars from `archify visual-check` (receipts, contact
sheets, screenshots); the folder can be deleted without affecting the diagrams.
