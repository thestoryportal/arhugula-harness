# Phase 7 — Sub-phase 7a Substitution Scaffolding

*7a substitution-scaffolding ledger. Operator-authored Convention-mechanism
declarations standing in for not-yet-built H_T primitives. NOT canonical —
each section is retired per its X-AL-2 retirement criterion. Authority:
Phase_7_Session_1_Entry_Directive_v1.md §6.2; Phase_7_Meta_Architecture_v1.md
§10.1.3 + §5.2.*

---

## §1 Surface 1 — Path conventions  [substitutes H_T-IS-1; C-IS-01 §1]

**Mechanism:** Convention. The 4-class path semantics below are declared here;
Read/Write/Glob operations during 7a obey these roots via prompt-discipline.
**Retirement:** this section retires when U-IS-01 + U-IS-02 + U-IS-03 land
(the typed path-class registry supersedes this convention).

### §1.1 The 4 canonical artifact classes (per C-IS-01 §1)

| Path class       | C-IS-01 residence contract                          | 7a convention root (provisional)        |
|------------------|-----------------------------------------------------|-----------------------------------------|
| SKILLS           | SKILL.md-as-directory; one folder per skill         | `.harness/skills/`                      |
| PROMPTS          | plain-text-file-in-git; one file per prompt         | `.harness/prompts/`                     |
| ROUTING_MANIFEST | single file in git; per-role/-class/-step model map | `.harness/routing.manifest.json`        |
| STATE_LEDGER     | two-mode: JSONL event ledger + git commit stream    | JSONL: `.harness/state.jsonl`; commit stream: workspace git repo |

### §1.2 Prompt-discipline rule

During 7a, all H_T artifact Read/Write/Glob operations resolve against the
roots in §1.1. `Glob` enumerates a path class against its declared root only.

### §1.3 Anti-leakage (IS-AL-1)

The H_T path-class roots live under `.harness/` (H_T-canonical runtime root).
They are NOT `.claude/` — `.claude/skills/` hosts the four H_E Phase 7-specific
skills (execution-harness scaffolding), which are categorically distinct from
the H_T SKILLS path class. `.harness/` ≠ `.claude/`; this convention is a
substitution, not the typed registry (IS-AL-1).

### §1.4 Provisional-binding note

The §1.1 root strings are 7a-provisional. C-IS-01 §1 defers canonical path
strings to implementation; the typed binding lands at U-IS-01/U-IS-02. If
the IS plan v2.2 unit declarations bind different strings, reconcile at
U-IS-01 landing (this section retires at that point regardless).
