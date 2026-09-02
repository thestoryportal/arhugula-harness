# Governance pack — skills + Phase 7 sub-phases

*Relocated BYTE-VERBATIM from Root `CLAUDE.md` §6, §7 by U-CTX-13 (R-CTX-1 Arc 5, 2026-08-11).*
*The root file keeps every heading with its number and position, plus a resolving
pointer to this file. Query this pack for the detail; do not preload it.*

---

## 6. Skill activation

This workspace ships with 4 Phase 7-specific skills at `<workspace_root>/.claude/skills/`. Skills activate per `tool_search`-driven trigger evaluation against YAML frontmatter description. On a name collision the user-level skill (`~/.claude/skills/`) takes priority over the project-level one, per the Claude Code skills doc ("enterprise overrides personal, and personal overrides project"; the command comes from the directory name) — a workspace variant of a user-level skill needs its own directory name, e.g. `context-save-lean` (U-SR-08).

| Skill | Path | Activation surface |
|---|---|---|
| `phase-7-implementation` | `.claude/skills/phase-7-implementation/SKILL.md` | Per-axis-stream unit consumption (7b sub-phase); acceptance-criteria-driven implementation; cross-unit dependency-graph traversal |
| `phase-7-cross-axis-composition` | `.claude/skills/phase-7-cross-axis-composition/SKILL.md` | Cross-axis composition seam instantiation (7c sub-phase); CXA v2.1 §2.3 byte-exact alignment verification |
| `phase-7-substitution-retirement` | `.claude/skills/phase-7-substitution-retirement/SKILL.md` | Substitution retirement events (all sub-phases); per-primitive retirement criterion verification per Meta-Architecture §6 |
| `phase-7-back-flow-routing` | `.claude/skills/phase-7-back-flow-routing/SKILL.md` | Fork detection (all sub-phases); design-phase routing per §4.3 |

---

## 7. Phase 7 sub-phase enumeration

Per `Phase_7_Meta_Architecture_v1.md` § Phase 7 internal workflow + `Project_Workflow_v1_8.md` §2.7:

| Sub-phase | Scope | Primary skill | Event-driven skills |
|---|---|---|---|
| 7a | Bootstrap — Claude Code workspace initialization; first H_T primitive landings; substitution scaffolding under single-LLM-during-7a runtime substitution | None specific (consult Meta-Architecture §5 + §6) | `phase-7-back-flow-routing` |
| 7b | Per-axis-stream implementation — IS / AS / CP / OD axis-stream parallel execution per atomic-unit plans | `phase-7-implementation` | `phase-7-substitution-retirement`; `phase-7-back-flow-routing` |
| 7c | Cross-axis composition — CXA v2.1 seam instantiation; cross-axis edge wiring across 6 composition buckets | `phase-7-cross-axis-composition` | `phase-7-substitution-retirement`; `phase-7-back-flow-routing` |
| 7d | Substitution retirement — H_E substitution gradient retirement per self-hosting milestone gradient; closure when all H_E substitutions retired OR bounded-residual carried with documented rationale per X-AL-2 | `phase-7-substitution-retirement` | `phase-7-back-flow-routing` |

---

