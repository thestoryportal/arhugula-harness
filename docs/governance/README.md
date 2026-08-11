# Governance packs — runner load matrix

Root `CLAUDE.md` is the always-loaded orientation. Its §-bodies that are **reference**
rather than **always-on** were relocated here byte-verbatim by U-CTX-13 (R-CTX-1 Arc 5).
Every root §N[.M] heading survives with its number and position and carries a resolving
pointer into this directory, so `CLAUDE.md §N.M` citations keep resolving (CI-enforced by
`tools/claude_md_citation_resolver.py`).

**Load a pack only when the rule below fires. Never preload the directory.**

## Roster + load matrix

| Pack | Root sections | Load when | Claude Code | codex |
|---|---|---|---|---|
| `docs/governance/project-framing.md` | §1.1, §7, §9, §9.1 | You need the axis scope table, the Phase 7 sub-phase enumeration, or the bootstrap filing footer | Read on demand | Read on demand |
| `docs/governance/stack-and-layout.md` | §3.3 | You are adding a workspace member or need the repo tree | Read on demand | Read on demand |
| `docs/governance/substitution-and-clearance.md` | §4.1, §4.2, §4.5 | A substitution retirement event, or authoring/verifying a `.harness/clearance/` marker | Read on demand; `phase-7-substitution-retirement` skill | Read on demand |
| `docs/governance/skills-and-subphases.md` | §6, §7 | Choosing a Phase 7 skill or routing a sub-phase | Skill router reads it | Read on demand |
| `docs/governance/design-phase-principles.md` | §10, §10.1–§10.9 | **Design-phase posture only** — authoring/revising `design-substrate/**` | Read at posture entry | Read at posture entry |
| `docs/governance/roadmap-protocol.md` | §12, §12.1, §12.2, §12.3, §12.5, §12.5.1–§12.5.4 | Running the session-start audit by hand, the post-merge refresh, or a drift reconciliation | `SessionStart` hook covers the common path; read for the full recipe | `just codex-preflight` covers the common path; read for the full recipe |
| `docs/governance/orchestration.md` | §13.2–§13.5 | Choosing between solo / advisor / codex-review / council / fan-out | Read on demand | Read on demand |

Artifact-head lineage is **not** in this directory — it lives under
`.harness/artifact-pointers/` (`spec-heads.md`, `plan-heads.md`, and the per-family files).
Query it (`rg <term> .harness/artifact-pointers/*.md`); do not read it wholesale.

## What never leaves root

The safety kernel stays VERBATIM-IN-FORCE in `CLAUDE.md` and is never relocated:
§1.3 authority chain · §3.1/§3.2 stack + framework-pull · §4.3/§4.4 back-flow + X-AL-3 ·
§5 sub-agent boundary · §8 execution invariants · §11 posture declaration ·
§12.2.1 refresh fixed point · §12.4.1 no-parking directive · §13.1 always-on disciplines ·
§14 execution + interaction conventions.

The roster above is pinned by `tools/test_governance_router.py`, which asserts SET EQUALITY
across four surfaces — this file, the actual `docs/governance/*.md` files, `CONTEXT.md`, and
`AGENTS.md` — so a pack cannot be added, renamed, or dropped in one venue only.
