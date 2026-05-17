# Phase 2 — Council Skill Review

**Question reviewed:** are the Phase-1 council skills useful for Phase 2 (runtime +
composition root + DevEx agentic plane), and what would adapting them to the CLI cost?

**Authored:** 2026-05-17, Phase 7 close-out. **Source:** Google Drive council folder
(`agent-harness-council`) — runbook, decision index, C1 SKILL.md, folder manifest.

**Method note / limitation:** I read the Phase-2 runbook, the council decision index,
and the C1 SKILL.md in full; the other 10 voice SKILL.md files were *not* read — their
scope is derived from C1's negative-keyword enumeration (C1 lists every other voice's
trigger keywords) plus the runbook session table. Per-voice quirks (failure modes,
tension-flag participation, eval contracts) are unconfirmed for C2–C11.

---

## 1. Headline finding — the council partition *is* the harness partition

The council is **11 specialist "voice" skills + 2 utility skills** (Council Orchestrator,
Spec-Writer). It is a *design body*: an orchestrator routes a topic, the relevant voices
contribute bounded design content, the spec-writer synthesizes it into spec sections,
and a decision index logs commitments as global-sequential D-IDs with confidence tags.

The 11 voices map almost 1:1 onto the harness's own axes — not a coincidence, the council
*designed* those axes. Which means the council also maps cleanly onto Phase 2's work areas
(per `phase-2-work-outline.md`):

| Voice | Domain | Phase 2 work area |
|---|---|---|
| C1 Orchestration & Control | topology, control-flow, agent-loop shape, HITL placement | §1 composition root, §3 runtime engine, **§5 DevEx agentic-plane control flow** |
| C2 Context Engineering | context window, compaction, caching, JIT retrieval | §3 runtime context management |
| C3 State, Memory & Persistence | checkpointing, git-as-state, durable state | §1 bootstrap, IS-axis runtime wiring |
| C4 Tools & Integration | MCP servers, tool schemas, idempotency contracts | §3 runtime tool dispatch, AS-axis runtime |
| C5 Validation Contract | gate semantics, evaluator-optimizer convergence | §3 runtime gate execution |
| C6 Model Strategy & Routing | model selection, capability profile, fallback chain | **§3 multi-LLM runtime routing core — closes the §9 Class 2 surface** |
| C7 Observability | OTel spans, trace propagation, attributes | **§4 live tracer provider, collector, TUI** |
| C8 Eval Engineer | eval-set design, judge calibration, drift detection | §5 DevEx eval primitives; the "pre-design tier" |
| C9 Reliability & Recovery | retry/backoff, breakers, idempotency | §3 runtime reliability primitives |
| C10 Action Safety & Blast Radius | trust boundaries, secrets, MCP supply chain | §3 runtime sandbox enforcement |
| C11 Operator Loop & Local Deployment | operator UI, approve/edit/reject, local deploy | **§5 DevEx agentic plane / operator features; §7 deployment** |

**Verdict: yes, highly useful.** Phase 2's first deliverable is a full design pipeline
(research → brainstorm → ADD → PRD → spec → plan). The council *is* a design body with
exactly the domain coverage Phase 2 needs, and it already produces ADR/spec-grade output
with confidence tagging, tension surfacing, and traceability discipline.

The three voices that hit Phase 2's hardest, newest surfaces: **C6** (the multi-LLM
runtime routing core — the unmet ADR-F1 commitment), **C11** (the DevEx/operator plane —
the genuinely new design), **C7** (the live observability runtime).

---

## 2. The council is a *design* body — not a runtime

Every voice is stamped "not a runtime engine — a design voice; output is design-time spec
content." That is the *correct* posture for Phase 2's design pipeline and a hard boundary
on where the council applies:

- **Useful for:** Phase 2's design sub-phase — research, ADD, PRD, spec, implementation
  plan authoring. This is the council's native job.
- **Not useful for:** Phase 2's *implementation* sub-phase (landing runtime code). That is
  `phase-7-implementation`-skill territory — atomic-unit consumption against a plan.

So the council slots in *ahead of* the existing Phase-7 execution skills, not alongside them.

---

## 3. Adaptation cost — two kinds, very different sizes

The skills were built for Claude.ai. Two adaptation layers:

### 3.1 Mechanical (cheap — token-level edits)

| Claude.ai primitive | CLI equivalent |
|---|---|
| `/mnt/skills/user/{slug}/SKILL.md` | `~/.claude/skills/` or workspace `.claude/skills/` |
| `present_files` / `/mnt/user-data/outputs/` | just `Write` to the workspace |
| `package_skill.py` → `.skill` zip | not needed — CLI skills are plain directories |
| `memory_user_edits` | the file-based memory at `.claude/.../memory/` |
| "project KB" | workspace `design-substrate/` + `.harness/` |
| skill-creator eval-and-iterate loop | already have a working eval harness (`Skill_Eval_Report_Iteration_1/2.md` at workspace root) |

### 3.2 Posture shift (the real work — genuine re-authoring per voice)

Every voice currently says, in effect: *"operate against the locked Phase-1 spec
(s4–s14); do not relitigate scope; apply the locked design."* The voices are forbidden
to design — they only *apply* settled design.

Phase 2 needs the opposite. The DevEx agentic plane is **new H_T design** (the runtime-gap
tension is explicit about this). The voices' activation/posture sections must be
re-authored to:

1. Re-anchor source-of-truth from the Phase-1 voice specs to the Phase-2 corpus
   (the new research/ADD/PRD/spec as it gets authored).
2. Relax the "do not relitigate / apply only" clause — in Phase 2 the voices *author*
   new design, they don't apply locked design.
3. Re-point the "research artifact" citations — the Phase-1 deep-research artifact may
   need a Phase-2 research pass (which is itself Phase 2's first step, and C8's
   "pre-design tier" pattern already covers how to run it).

This is per-voice rewriting of the most load-bearing section, not find-and-replace.
Estimate: mechanical layer ~15 min/skill; posture layer ~30–60 min/skill depending on
how much new-design latitude the voice needs.

---

## 4. CLI is an *upgrade* for the orchestrator

On Claude.ai the council convened sequentially — the operator pasted a kickoff prompt,
ran a session, pasted the next. The Council Orchestrator skill routed *one topic per
chat session*.

In the CLI, the orchestrator can dispatch convened voices as **parallel sub-agents**
(the `Agent` tool). A genuine multi-voice convening — orchestrator scores voices, spawns
the convened set concurrently, collects contributions, hands to spec-writer — runs in
one session instead of a dozen operator-mediated pastes. This is a real capability gain,
and it means the Council Orchestrator skill should be re-authored around sub-agent
dispatch rather than session-kickoff-prompt emission.

---

## 5. Overlap with existing workspace skills — role × domain

The workspace already has 4 adapted authoring skills: **systems-architect**,
**spec-writer**, **implementation-planner**, **harness-adversarial-reviewer**.

These are *role* skills — they answer "what stage of the pipeline am I in." The council
voices are *domain* skills — they answer "what subject-matter expertise speaks here." The
two are complementary (roles × domains), not redundant. Specifically:

- **Spec-Writer** — direct overlap. The workspace `spec-writer` was almost certainly
  adapted from the council Spec-Writer utility. Reconcile to one skill; don't install two.
- **systems-architect** — likely overlaps the Council Orchestrator's convening role
  and/or C1. Worth a direct compare before installing the orchestrator — not assumed.
- **implementation-planner / harness-adversarial-reviewer** — no council equivalent;
  keep as-is. (The council's adversarial discipline is *inside* each voice as failure-mode
  self-audits, plus the runbook's adversarial-throughout posture — different mechanism.)

Net: the **11 domain voices are genuinely new capability** the workspace lacks. The
2 utilities need a de-dup pass against the 4 existing role skills.

---

## 6. The council already produced Phase-2-relevant *content*

This is not just skills — the council folder also holds design output already pointed at
Phase 2 surfaces:

- **`p1-planner-model-strategy-spec.md`** + the decision index's **18 D-IDs** — a complete
  planner-agent model strategy: Sonnet 4.7 default tier, extended-thinking budget,
  prompt-cache strategy, a 5-step fallback chain (Sonnet 4.7 → 4.6 → Opus 4.7 →
  cross-family → local Ollama), full-jitter exponential backoff params, two breaker
  scopes, routing-accuracy eval primitive, holdout-corpus design, drift signals. This is
  direct DevEx-agentic-plane / multi-LLM-routing design.
- **`pre-design-tier-pattern.md`** — a voluntary research/brainstorm/question-sharpening
  tier; this is exactly the front of Phase 2's design pipeline.
- **`workflow-class-taxonomy-disposition.md`** — 5 workflow classes (planner / executor /
  validator-loop / data-pipeline / interactive-coding).
- `p7-kickoff-and-handoff.md`, `p7-operator-burden-disposition.md`,
  `s15-phase2-prep-reconciliation.md` — handoff and operator-burden material.

Phase 2 scoping should **absorb or explicitly supersede** this content rather than
re-deriving it. Caveat: this is the *council project's* "P-1 / phase 2 / phase 3"
numbering, which is a terminology collision with this workspace's Phase 1 / Phase 2 —
keep the two phasings distinct when consuming.

---

## 7. Priority tiers (for the operator's Phase 2 scoping call)

Not a recommended order — the operator picks scope. Tiers reflect Phase-2 surface match.

**Tier 1 — adapt first; hit Phase 2's hardest/newest surfaces:**
- C6 Model Strategy & Routing — the multi-LLM runtime core; closes the §9 Class 2 surface
- C11 Operator Loop & Local Deployment — the DevEx agentic plane (the new design)
- C1 Orchestration & Control — agentic-plane control flow + composition-root topology
- C7 Observability — the live tracer/collector/TUI runtime
- Council Orchestrator — re-author around CLI sub-agent dispatch (§4)

**Tier 2 — adapt for the full design pipeline:**
- C8 Eval Engineer — eval primitives + the pre-design tier
- C9 Reliability & Recovery — runtime retry/breaker design
- C5 Validation Contract — runtime gate execution
- Spec-Writer — reconcile with the existing workspace `spec-writer` (don't double-install)

**Tier 3 — relevant but lower Phase-2 intensity (axes already built as libraries):**
- C2 Context Engineering, C3 State/Memory/Persistence, C4 Tools & Integration,
  C10 Action Safety & Blast Radius — useful when their axis's runtime wiring is designed,
  but the contracts are already settled in the Phase-1 corpus.

Every voice is *relevant* (Phase 2 wires all axes into a runtime); the tiers reflect how
much *new* design each voice carries, not whether it applies.

---

## 8. Open questions for the scoping session

1. Install all 13, or Tier-1 first? Adapting all 13 is a real sub-project (~½–1 day at
   the posture-shift estimates in §3.2).
2. How much new-design latitude does each voice get? The Phase-1 "do not relitigate"
   clause must be relaxed — but by how much, per voice, needs an operator call.
3. Reconcile Spec-Writer (council) vs `spec-writer` (workspace) and Council Orchestrator
   vs `systems-architect` — one skill each, or keep both with distinct scope?
4. Does Phase 2 absorb `p1-planner-model-strategy-spec.md` + the 18 D-IDs as canonical
   input, or treat them as superseded and re-derive?
5. Confirm the C2–C11 per-voice details (failure modes, eval contracts) by reading their
   SKILL.md files before adapting — this review derived their scope indirectly.
