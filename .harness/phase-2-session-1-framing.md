# Phase 2 — Session 1 Ratified Framing

**Session:** Phase 2 kickoff. **Date:** 2026-05-19. **Status:** ratified.

**Inputs in scope:** `phase-2-work-outline.md`, `phase-2-council-skill-review.md`,
`phase-2-research-corpus-review.md`, `phase-2-recommended-approach.md`.

**Purpose:** lock the framing for Phase 2 so substantive work can proceed from durable
ground. Per the recommended approach, Session 1 produces the framing, not substantive
design.

---

## Ratified decisions

### D-P2-1 — Track A / Track B split

**Ratified.** Phase 2 splits into two tracks with different design discipline.

| | Track A — Integration runtime | Track B — DevEx agentic plane |
|---|---|---|
| **Scope** | Composition root, entrypoint, agent loop, observability runtime, deployment, 7d full retirement | "Operating brain" + personalized operator features |
| **State** | Bounded by existing contracts (144-unit library) | Genuinely new H_T design (no existing contracts) |
| **Design rigor** | Light scoping → atomic-decomposition plan, Phase-7-style | Full pipeline: research → brainstorm → ADD → PRD → spec → plan, adversarial throughout |
| **Closure gate** | Runtime stands up + 7d condition-B verification fires + §9 Class 2 multi-LLM surface closes | DevEx plane lands as code |

Sequencing: Track A strawman pass first; both tracks parallel after; converge at integration.

### D-P2-2 — Track A scope: instantiate all 24 phase-2-runtime CXA edges

**Ratified.** All 24 CXA edges reclassified as `phase-2-runtime` in CXA v2.3 are
in-scope for Phase 2's Track A. The deferral category is eliminated; Track A's
atomic-decomposition plan must enumerate the 24 edges as wiring deliverables.

**Scope expansion noted:** this is a larger Track A than the recommended approach
suggested (which staged only what the runtime required). The operator-ratified position
forecloses the "runtime needs a deferred edge → Class 1 fork" risk and closes the
deferral category cleanly.

### D-P2-3 — Track B sequencing: definitional pass before persona surfacing

**Ratified.** Before Track B's persona-surfacing interview opens, a definitional pass
locks "what is the DevEx agentic plane, concretely" — naming its components, scope
boundary, and persona target. The Brainstorm Synthesis §9 question scaffold is built for
whole-harness persona surfacing, not for an under-defined plane, so the scaffold is reused
*after* the definitional pass.

### D-P2-4 — Skill adaptation: defer until exercised

**Ratified.** No upfront council-skill adaptation. The workspace's 4 role skills (systems-architect,
spec-writer, implementation-planner, harness-adversarial-reviewer) cover research/scoping.
Tier-1 council voices (C6, C11, C1, C7, Council Orchestrator) are adapted to CLI only when
the design pipeline first convenes them. Real use case shapes the adaptation.

### D-P2-5 — Research strategy: per-voice as convened

**Ratified.** No separate runtime-lens re-mine deliverable upfront. Each Tier-1 voice
mines the Pattern Reference Catalog through its own lens when first convened — C6 for
routing patterns, C11 for operator-surface patterns, C7 for observability patterns, C1
for topology patterns. Lower upfront cost; runtime-lens annex emerges implicitly across
voice contributions.

### D-P2-6 — Session 2: Track A strawman pass

**Ratified.** Session 2 sketches the composition-root shape, agent-loop topology,
entrypoint surface, and bootstrap order against existing contracts. Sketch not plan; one
session. De-risks both tracks: surfaces seam defects early; gives Track B's eventual
persona surfacing a runtime shape to ground against. Expected to surface Class 1 forks
(composition roots routinely do) — the in-CLI spec-fix discipline handles them.

---

## Standing-risk register (carried into Session 2)

| Risk | Mitigation |
|---|---|
| Track A strawman surfaces Class 1 forks (spec under-specifies a runtime contract) | Existing in-CLI spec-fix discipline ([[spec-tension-record-pattern]]); harness-adversarial-reviewer + spec-writer handle the loop |
| DevEx-plane scope creep | The definitional pass (D-P2-3) is the scope-lock; do it first when Track B opens |
| Parallel sub-agent convening unproven | First multi-voice convening is a small validation run before the full pipeline commits to it |
| Terminology collision ("Phase 2" in this workspace ≠ design-project ≠ council-project) | Phase 2 artifacts label at first reference; memories [[phase-1-council-skills]], [[phase-1-research-corpus]] flag it |
| §9 Class 2 multi-LLM surface stays open | Closes at Track A's 7d gate; no separate action |
| 24 CXA edges materially expand Track A wiring | Strawman's atomic-decomposition pass enumerates them; Phase-7-style scope discipline applies |

---

## Explicit deferrals

| Item | Disposition |
|---|---|
| Adapting Tier 2/3 council voices | Defer past Phase 2 unless a voice is convened and Tier-1 use validates the adaptation pattern |
| CI substrate | Deferred to post-bootstrap milestone per `Target_Stack_Commitment_v1.md`; Phase 2 unblocks it, doesn't deliver it |
| Bumping CXA citations in per-axis subdir `CLAUDE.md` files | Separate cosmetic carry from the 7c prerequisite pass; not Phase 2 work |
| Runtime-lens annex to the Pattern Reference Catalog as an explicit deliverable | Folded into per-voice mining (D-P2-5); no upfront deliverable |

---

## What Session 2 needs at entry

- This framing document (`phase-2-session-1-framing.md`) loaded.
- The four prep documents loaded as reference.
- Workspace state: clean. `harness-core`, `harness-is`, `harness-as`, `harness-cp`, `harness-od`, `harness-cxa` all landed at Phase 7 design-time close.
- Skills available: workspace 4 role skills + 4 Phase-7 skills. Council voices not yet adapted (per D-P2-4).

**Session 2 charter:** produce a Track A strawman — sketch the composition-root shape,
agent-loop topology, entrypoint surface, and bootstrap order against the existing
contract corpus. Sketch artifact, not an implementation plan. Surface and route any
Class 1 forks under the standing in-CLI spec-fix discipline. Output: a strawman document
in `.harness/` that Session 3 (atomic-decomposition plan) and Track B (whenever opened)
can ground against.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `phase-2-session-1-framing.md` |
| Authored at | Phase 2 Session 1 kickoff, 2026-05-19 |
| Authority | Operator ratification, 6 decisions D-P2-1 through D-P2-6 |
| Successor | Phase 2 Session 2 — Track A strawman pass |
| Revision policy | Framing decisions are append-only; revisions surface as new D-P2-N entries or operator-ratified overrides |
