# Phase 2 — Recommended Approach

**Question:** given the work outline, the council-skill review, and the research-corpus
review, what is the recommended approach for initiating and working through Phase 2?

**Authored:** 2026-05-19. **Inputs:** `phase-2-work-outline.md`,
`phase-2-council-skill-review.md`, `phase-2-research-corpus-review.md`.

**Posture:** this is the recommendation for Session 1; it is not a plan-of-plans for
Sessions 2–N. The operator decides per session per the workspace's standing decide-per-step
discipline. The right shape is: ratify the framing, do one substantive step, decide the
next.

---

## 1. The load-bearing recommendation — split Phase 2 into two tracks

The seven work areas in the outline are not the same kind of work. Splitting them by
*design discipline needed* changes the timeline meaningfully:

**Track A — Integration runtime.** Composition root, entrypoint, agent loop, observability
runtime, deployment, and 7d full substitution retirement. **Bounded by existing contracts** —
the 144-unit library specifies what to wire together. The missing artifact is a runtime
*integration plan* (Phase-7-style atomic decomposition against the existing spec corpus),
not a fresh research → ADD → PRD → spec pipeline. Light design rigor; closure gate is the
runtime standing up + 7d's runtime-trace condition-B verification firing + §9 Class 2
multi-LLM surface closing.

**Track B — DevEx agentic plane.** The "operating brain of the workflow" + personalized
operator features. **Genuinely new H_T design** — no existing contracts; the operator
named this as the real point of Phase 2. Full design rigor: research → brainstorm →
ADD → PRD → spec → implementation plan, adversarial throughout. This is where the
council voices earn their adaptation cost.

Applying full-rigor design to Track A would over-engineer settled contracts. Applying
light scoping to Track B would silently extend H_T design under X-AL-3. The split is the
load-bearing call.

---

## 2. Sequencing — Track A strawman first, then both in parallel

Track B's persona surfacing depends on having a runtime shape to surface personas against
("what runtime are we surfacing personas *for*?"). So Track A needs a **thin strawman pass**
first — a one-session sketch of the composition-root shape, agent-loop topology, and
entrypoint surface, against the existing contracts. Output is not a plan, just a sketch
the persona interview can ground itself against.

Once the strawman exists, the two tracks run in parallel:
- Track A → from strawman to atomic-decomposition plan to implementation (Phase-7-style).
- Track B → from definitional pass through the full design pipeline to implementation.

They converge at integration: Track B's DevEx-plane artifacts land *into* the runtime
Track A stood up.

---

## 3. What Session 1 should produce

Session 1 is the **Phase 2 kickoff** — an operator-led scoping session. Don't try to do
substantive design in Session 1; produce the ratified framing the rest works from.

**Pre-load:** the three Phase-2 prep documents (`phase-2-work-outline.md`,
`phase-2-council-skill-review.md`, `phase-2-research-corpus-review.md`).

**Decisions to surface for ratification:**

1. **The Track A / Track B split** — does the operator ratify the framing, or scope Phase 2
   differently?
2. **Definitional pass on the DevEx agentic plane — *before* persona surfacing.** The
   Brainstorm Synthesis §9 scaffold is designed for whole-harness persona surfacing, not
   for an under-defined plane. Before any persona work, the operator needs to answer
   "what is the DevEx agentic plane, concretely" — a definitional pass, not a persona
   pass. Candidate output: a short scope document naming the plane's components.
3. **Track A scope boundary — what is deferred.** Notably the **24 phase-2-runtime CXA
   edges** struck in CXA v2.3 — does Phase 2 instantiate them all, stage them, or defer
   further? Same question for the §6.3 dormant cross-axis cascades.
4. **Skill adaptation strategy: defer until exercised.** The workspace already has 4 role
   skills (architect, planner, reviewer, spec-writer) sufficient for research/scoping.
   Adapting 13 council SKILL.md files up front risks adapting them wrong — the actual use
   case shapes the adaptation. Adapt Tier-1 voices on-demand as they are first convened.
5. **First convening = validation run.** The "Council Orchestrator dispatches voices as
   parallel sub-agents" upgrade (from the council review) is unproven. Treat the first
   multi-voice convening as a small validation run before the whole pipeline commits to it.
6. **Research strategy:** the runtime-lens re-mine of the Pattern Reference Catalog
   (recommended in the research review) — commission as an explicit deliverable, or fold
   into per-voice research as voices are convened?

**Immediate next move after ratification:** the substantive Session 2 work, picked from
the ratified framing (likely either the Track A strawman or the DevEx definitional pass).

---

## 4. Named risks — surface before they bite

**Track A will surface Class 1 forks.** Composition roots routinely surface seam defects
(a contract under-specifies a runtime field, a hook cardinality is wrong, an enum is
incomplete). This is the documented pattern from Phase 7. Pre-establish the back-flow
channel: runtime-discovered contract gaps route to spec revision under the existing
in-CLI spec-fix discipline ([[spec-tension-record-pattern]]), with the
`harness-adversarial-reviewer` + `spec-writer` skills handling the loop. Without this
channel, Track A's "light scoping" claim breaks at the first defect.

**Skill adaptation rabbit hole.** Adapting all 13 council SKILL.md files is a real
sub-project (~½–1 day at the council-review's posture-shift estimates). Defer until
exercised; adapt Tier-1 voices (C6, C11, C1, C7, Council Orchestrator) only when the
design pipeline first convenes them.

**Parallel sub-agent convening is unproven.** Validate on a small run before the full
pipeline commits to it. If it doesn't work cleanly, fall back to sequential convening
(operator-mediated) — the design pipeline still works, just slower.

**DevEx-plane scope creep.** "Operating brain + personalized operator features" can absorb
arbitrary scope. The definitional pass (§3.2) is the scope-locking step; do it first.
Treat anything not in that definition as a future-phase decision.

**Terminology-collision propagation.** "Phase 2" in this workspace ≠ "Phase 2" in the
design project (= persona surfacing) ≠ "Phase 2" of the council project (= SKILL drafting).
Phase 2 artifacts should call this out at first reference. Memories
[[phase-1-council-skills]] and [[phase-1-research-corpus]] flag it.

**The §9 Class 2 multi-LLM surface stays open** until Track A's runtime closes 7d. ADR-F1's
multi-LLM commitment is met in design + landed code but unmet at runtime — Phase 2 closes
the gap, but only at Track A's closure gate.

---

## 5. What gets explicitly deferred

The work-ahead outline's seven areas all live in Phase 2 — but a few sub-questions can be
deferred without blocking the kickoff:

- **The 24 phase-2-runtime CXA edges** — deferred from 7c. Phase 2 instantiation strategy
  is a Session 1 decision.
- **The 2 dormant cross-axis cascades** (§6.3 — anthropic.* namespace; F-CP-01 inversion
  seam) — fire automatically once their endpoints retire at Track A's 7d gate.
- **Adapting Tier 2/3 council voices** — defer until Tier-1 use validates the adaptation
  pattern.
- **CI substrate** — already deferred to post-bootstrap milestone per the stack commitment;
  Phase 2 unblocks it, doesn't deliver it.
- **Bumping CXA citations in the per-axis subdir CLAUDE.md files** — separate cosmetic
  carry from the 7c prerequisite pass; not Phase 2 work.

---

## 6. Immediate next move

Open the Phase 2 kickoff session with the three prep documents in context. Ask the
operator to ratify the Track A / Track B split and the deferral list, and pick the next
substantive session (likely Track A strawman or DevEx definitional pass).

Do not pre-commit Sessions 2–N. The right shape is one decision at a time, with the next
one emerging from what the session produced.
