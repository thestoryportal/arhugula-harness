# Class 1 Tension — CP-20 HITL gate composer underspec (runtime composition seam)

**Filed:** 2026-05-20 — Phase 7 sub-phase 7b cluster-open orientation at HEAD `2a15504` (post-U-RT-59 absorption arc close). **In-pass corrected at systems-architect mode 3 orientation same-turn**: original v1 of this record (file basename `class_1_tension_cp_17_*`) miscited the principal substitution as H_T-CP-17 (which is Files primitives per Meta-Architecture §5 line 20). Canonical principal substitution per Meta-Architecture §5 line 23 is **H_T-CP-20** (HITL primitive + 4-response palette + `hitl.*` / `audit.*` namespaces); retirement-gating unit is **U-CP-46** (audit + hitl-span namespace declarations consumed by composer) — NOT U-CP-37..41 (those are declaration units; typed library already landed).
**Surfaced by:** `phase-7-implementation` skill cluster-open orientation against CP-axis cluster 6 (U-CP-37 → U-CP-41 — typed library already landed). Routed here via skill §6 halt condition "Cited spec contract section unreachable or under-specifies the surface."
**Substitutions at stake:** **H_T-CP-20** (HITL primitive + 4-response palette + `hitl.*` / `audit.*` namespaces; retirement-gating per Meta-Architecture §5 line 23). H_T-CP-22 (pause/resume) is a structurally separate substitution per Meta-Architecture §5 line 25 — its retirement gates on a separate `attempt_resume` composer arc (potentially U-RT-61), not this arc; the operator may elect to absorb pause/resume into this arc at the spec-growth-scope question (Q4 below).
**Defect class:** Class 1 — runtime composer absent from runtime spec; X-AL-3 binds (no silent H_T design extension at Phase 7 execution).

---

## Defect

The runtime composer that invokes the **HITL gate** at workflow_driver per-step execution (analogous in shape to `RuntimeLLMDispatcher` for LLM dispatch and `RuntimeSubAgentDispatcher` for sub-agent dispatch) is required for H_T-CP-17 / H_T-CP-20 retirement but has **no spec contract** and **no plan unit**.

State of surrounding artifacts:

| Surface | What it specifies | What it does NOT specify |
|---|---|---|
| `Spec_Control_Plane_v1_9.md` C-CP-16 §16.1–§16.4 | 4-response palette + per-response audit shapes + palette invariants + `hitl.response.class` attribute | WHICH runtime composer invokes the gate; WHERE in the per-step path the gate fires; HOW the H_E surface delivers the response (operator turn vs polling vs async-event) |
| `Spec_Control_Plane_v1_9.md` C-CP-17 §17.1 + §17.1.1 + §17.2 + §17.3 | 3-placement enum + `hitl_gate(...)` interface signature + HITL-as-tool-call rewriting + `HITLPlacement` workflow-definition schema | WHO calls `hitl_gate` at runtime; WHERE the placement-trigger evaluator lives; HOW per-step placement is dispatched against `HITLPlacement[]` from `WorkflowManifestEntry` |
| `Spec_Control_Plane_v1_9.md` C-CP-18 §18.1–§18.5 | Persona-tier × engine-class HITL matrix + both-by-tier overlay + two-agent-observer meta-class + persona-tier-binding selection | WHEN the matrix cell is resolved at runtime; HOW resolved cell composes with placement at gate invocation |
| `Spec_Harness_Runtime_v1.md` v1.8 §14.5 C-RT-15 (LLM dispatch) | Per-step LLM-dispatch composer | (HITL out of scope — LLM-only composer) |
| `Spec_Harness_Runtime_v1.md` v1.8 §14.6 C-RT-16 (retry/breaker/fallback) | Per-step retry/breaker/fallback wrap | (HITL out of scope — retry-only composer) |
| `Spec_Harness_Runtime_v1.md` v1.8 §14.7 C-RT-17 (sub-agent dispatch) | Per-step sub-agent dispatch composer | (HITL out of scope — dispatch-only composer) |
| `Spec_Harness_Runtime_v1.md` v1.8 (terminal) | C-RT-17 is the last authored composer contract | **NO C-RT-18 HITL gate composer authored** |
| `harness-runtime/src/harness_runtime/lifecycle/hitl_placement.py` (U-RT-25) | CP_ROUTING reference-time registry: pure-decision wrappers over `select_variant` / `rewrite_tool_call_to_hitl` / `on_hitl_timeout` / `classify_resume` | Module docstring lines 22–25 explicit: "The NotImplementedError CP stubs (`hitl_gate`, `capture_pause_snapshot`, `attempt_resume`, `deliver_webhook`) are deferred to L8 LOOP_INIT / integration-time composition with the IS substrate; they are NOT wired here. L5 boundary held." |
| Runtime plan v2.6 (`.harness/phase-2-session-3-track-a-atomic-decomposition.md`) | Units U-RT-00 through U-RT-59 | **NO unit owns the "invoke HITL gate at per-step path" composition seam** |

The CP-axis typed library (cluster 6: U-CP-37 / U-CP-38 / U-CP-39 / U-CP-40 / U-CP-41) is fully landed at `harness-cp/src/harness_cp/` (`hitl_response_palette.py`, `hitl_placement.py`, `hitl_as_tool_call_rewriting.py`, `persona_engine_hitl_matrix.py`, `hitl_timeout_degradation.py`, `audit_hitl_span_namespace.py`). The CP_ROUTING runtime registry (U-RT-25) is landed and wraps those surfaces as pure decisions. The **composition seam** between the U-RT-25 registry and the workflow_driver per-step execution path — i.e., the production composer that:

1. Reads `WorkflowManifestEntry.hitl_placements` per step;
2. Evaluates placement-trigger conditions (PRE_ACTION / SUB_AGENT_BOUNDARY / VALIDATOR_ESCALATION);
3. Invokes `hitl_gate(placement, handoff_context, response_palette, timeout, cascade_policy)`;
4. Delivers the gate via H_E surface (sub-phase 7b runtime: bounded substitution; likely operator-turn or polling);
5. Receives `HITLResult`;
6. Emits `hitl.*` + `audit.cp.*` spans per C-CP-20 §20.1 + audit-ledger F2 write per CP→OD CXA edge (per CXA v2.4 §2.3.7);
7. Composes with retry/breaker/fallback (C-RT-16) + sub-agent dispatch (C-RT-17) + LLM dispatch (C-RT-15) per the placement → composer-stack ordering;

has **no owner**.

## Evidence — current code state at HEAD (`2a15504`)

```
# hitl_gate is an explicit NotImplementedError stub at the runtime layer
$ grep -nE "def hitl_gate|raise NotImplementedError" harness-runtime/src/harness_runtime/lifecycle/hitl_placement.py
# (docstring lines 22–25 only — function not defined here; L8 LOOP_INIT deferral confirmed)

# workflow_driver does NOT invoke any HITL gate
$ grep -rn "hitl_gate\|hitl\.invocation\|hitl\.response\.class" harness-runtime/src/harness_runtime/lifecycle/workflow_driver.py
# (no matches — no production HITL emission site)

# Audit-ledger F2 write for HITL is absent — `audit_hitl_span_namespace.py` is declaration-only
$ grep -rn "audit\.cp\.response\|hitl\.gate\.evaluated" harness-runtime/src/
# (no production emission; namespace is declared at harness-cp/src/harness_cp/audit_hitl_span_namespace.py but not invoked at runtime)
```

Per `harness-cp/CLAUDE.md` §4.1 substitution-table line 174:

> STILL-BOUNDED | 9 | H_T-CP-12 / 16 / 17 / 18 / 19 / 20 / 21 / 22 / 23 — bounded on absent HITL / validator / tool-invocation / memory / files / mcp composers

The HITL composer is named in this bounded-residual statement explicitly. Per `[[phase-7-bootstrap-status]]` memory + checkpoint at `20260520-230028-post-u-rt-59-absorption-arc-closed-4-fronts-banked.md` Remaining Work item 2:

> Next atomic unit cluster — phase-7-implementation skill traversal against per-axis plans. Likely Phase 3+ composers (HITL / validator / tool-invocation / memory / files / mcp) that unblock the 10 STILL-BOUNDED substitutions + CP-14 PARTIAL fan-out arc.

The HITL gate composer is one of the four named gating arcs.

## Consequence of silent absorption

Implementing the composer without first authoring the spec contract + plan unit would be **silent H_T design extension** at Phase 7 execution-time — the exact anti-pattern X-AL-3 forbids. Concretely:

1. **No spec contract for the composer.** Where does the composer live (runtime axis as new C-RT-18? CP axis amendment to C-CP-17?). What is its invocation signature against `step_context: StepExecutionContext` (per the U-RT-59 / C-RT-17 Path A resolution)? What is the H_E delivery mechanism for the gate response at sub-phase 7b (operator-turn / polling / async-event / interactive prompt)? At what point in the composer-stack does the gate fire — before or after sub-agent dispatch? before or after retry-wrap? None specified.
2. **No plan unit owning the work.** No acceptance criteria; no test surface; no dependency edges; no coverage-matrix cell at the runtime-plan §3 topology graph.
3. **CXA back-edge undeclared.** The audit-trail composition for HITL response (`audit.cp.response` 4-attribute namespace per C-CP-20 §20.1) requires CP→OD audit-ledger write — a second cross-axis back-edge candidate (precedent: U-RT-59 Fork 2 added CXA v2.4 §2.3.7 CP→OD bucket for sub-agent dispatch audit-write). HITL audit-write may add a second seam to the same bucket; that determination requires spec authoring + adversarial review.
4. **Recording retirement against an unspec'd composer** would violate X-AL-2 (retirement criterion fidelity) — condition B ("substituted H_E surface no longer invoked at substitution site") would be met against an undefined contract for H_T-CP-17 + H_T-CP-20.

## Routing target

**Path A (operator-ratified 2026-05-20 inline with this filing via AskUserQuestion at cluster-open turn):** Runtime axis owns the composition seam.

1. **Spec amendment** — Author new contract in `Spec_Harness_Runtime_v1.md`:
   - Tentative ID: **C-RT-18** — Per-step HITL gate composer.
   - Scope: defines the runtime-side composer that invokes `hitl_gate(...)` at workflow_driver per-step execution per `WorkflowManifestEntry.hitl_placements`; consumes `ctx.hitl_placement` (U-RT-25 registry); resolves persona-tier × engine-class matrix cell at runtime; dispatches placement triggers (PRE_ACTION / SUB_AGENT_BOUNDARY / VALIDATOR_ESCALATION); delivers gate via H_E substitution surface at sub-phase 7b (bounded; AskUserQuestion-equivalent or polling); emits `hitl.*` spans per C-CP-20 §20.1; emits `audit.cp.*` audit-ledger F2 write per CP→OD CXA edge.
   - Composer-stack ordering: HITL gate fires per `HITLPlacementKind` — PRE_ACTION before LLM dispatch (C-RT-15), SUB_AGENT_BOUNDARY before sub-agent dispatch (C-RT-17), VALIDATOR_ESCALATION after validator-fail signal (validator composer arc — future).
   - Failure modes: gate timeout → `TimeoutDegradationKind` per persona-tier table; gate cancellation → `RT-FAIL-HITL-GATE-CANCELLED` (new fail class); gate compose error → `RT-FAIL-HITL-GATE-COMPOSE`.
   - Spec bump: v1.8 → v1.9 (new §14.8 C-RT-18).

2. **Plan amendment** — Add new atomic unit to runtime plan v2.6 → v2.7:
   - Tentative ID: **U-RT-60** — Per-step HITL gate composer at workflow_driver per-step path.
   - Dependencies: U-RT-25 (CP_ROUTING registry), U-RT-32 (audit-ledger F2 write — IS), U-RT-52 (per-step dispatch site precedent), U-RT-58 (composer-stack precedent), U-RT-59 (step_context plumbing precedent + sub-agent gate-level descent precedent), C-CP-16/17/18/20 (CP contracts), C-RT-18 (new runtime contract).
   - Acceptance criteria: per C-RT-18; runtime test suite verifies (a) `hitl.gate.evaluated` span emission per placement; (b) `hitl.invocation.responded` event with 4-response palette; (c) `audit.cp.response` audit-ledger F2 write per OD CXA edge; (d) timeout-degradation invocation; (e) palette-restriction per cross-trust-boundary state; (f) per-tool tier (auto/ask/deny) overlay evaluation; (g) two-agent-observer dispatch at Tier-3+ blast radius; (h) composer-stack ordering preserved against C-RT-15/16/17.
   - Cascade: full-retires H_T-CP-17 (HITL placement) + H_T-CP-20 (4-response palette runtime invocation); partial-retires H_T-CP-18 (persona-engine matrix — depends on persona-tier-binding wired) + H_T-CP-22 (HITL pause/resume — depends on `attempt_resume` stub materialization).

3. **CXA edge declaration** — At spec arc, evaluate whether HITL audit-write adds a second typed seam to the CXA v2.4 §2.3.7 CP→OD bucket. If yes: CXA v2.4 → v2.5. If the audit-write composes against the same converter (`cp_audit_to_od_audit`) the U-RT-59 Fork 2 arc landed at `harness-cxa/src/harness_cxa/cp_audit_conversion.py`, the seam may reuse existing infrastructure — determine at spec-writer arc.

4. **Implementation** — Open arc per `phase-7-implementation` skill discipline against U-RT-60 acceptance criteria. Land in follow-on arc.

5. **Retirement events** — After U-RT-60 lands, file Phase 7d batch 8 retirement event records for H_T-CP-17 RETIRED + H_T-CP-20 RETIRED (plus PARTIAL transitions for CP-18 / CP-22 as appropriate).

Path B (CP-axis ownership — amend C-CP-17 with composer contract): rejected for symmetry with the C-RT-15 / C-RT-16 / C-RT-17 precedent — composer contracts live at runtime spec; CP spec defines the decision surface, runtime spec defines the invocation site.

Path C (defer to a post-bootstrap milestone): rejected — leaves H_T-CP-17 + H_T-CP-20 + cascade as bounded-residuals indefinitely; blocks the 4 STILL-BOUNDED HITL-gated retirements; contradicts operator's same-session Path A authorization at the cluster-open AskUserQuestion turn.

## Operator decision (2026-05-20)

**Path A ratified.** Operator selected option A ("Open HITL gate composer arc (C-RT-18 / U-RT-60)") at cluster-open AskUserQuestion this session — `phase-7-implementation` skill orientation surfaced the composer-absence finding; operator authorized the multi-skill arc (spec-writer → implementation-planner → phase-7-implementation) in same turn.

Sequence — same shape as U-RT-58 (`[[fork-cp-3-retry-breaker-composer-underspec]]`) and U-RT-59 (`[[fork-c-rt-17-step-dispatcher-parent-context-gap]]`):

1. **This filing** — Class 1 fork record (now).
2. **Spec authoring (next skill: spec-writer or systems-architect mode 3)** — Author C-RT-18 in `Spec_Harness_Runtime_v1.md` v1.8 → v1.9 per §14.6 / §14.7 precedent shape. Spec growth in-CLI per workspace `CLAUDE.md` §4.3 (design-substrate divergence — design-phase back-flow deprecated; workspace `design-substrate/` is canonical).
3. **Plan authoring (implementation-planner skill)** — Add U-RT-60 to runtime plan v2.6 → v2.7 at a new L9-quater section; update §3 topology graph + §6 7d retirement preview + §9 traceability row.
4. **Pre-implementation adversarial review (harness-adversarial-reviewer Phase-7 mode)** — Red-team the C-RT-18 + U-RT-60 spec+plan bundle before implementation lands.
5. **Implementation (phase-7-implementation skill)** — Land U-RT-60 against acceptance criteria. Expected 1–3 commits (composer + tests + integration with workflow_driver).
6. **Retirement events (phase-7-substitution-retirement skill)** — Phase 7d batch 8 record at landing.

Per `[[design-substrate-divergence]]` memory: spec/plan authoring happens in-CLI at `design-substrate/`, not at a separate design-phase workspace.

## Open architectural questions (for spec-writer arc)

These questions surface from precedent comparison and must be ratified before C-RT-18 authoring proceeds:

1. **H_E surface for gate delivery at sub-phase 7b.** Options: (a) operator-turn (Claude Code `AskUserQuestion` equivalent); (b) polling (loop on filesystem marker); (c) async event (webhook). The CP_ROUTING registry already has `deliver_webhook` as a NotImplementedError stub — suggests (c) is the target. But (a) is the simplest 7b bootstrap and lowest-friction. Operator decision required.
2. **Composer-stack ordering vs C-RT-15/16/17.** Where does HITL fire relative to LLM dispatch and sub-agent dispatch? Per §17.1 PRE_ACTION placement, the gate fires before the action — so before the action's primary composer. But for HITL-as-tool-call rewriting (§17.2), the gate **replaces** the tool call. Spec needs to clarify the composer-stack semantics for rewriting vs gating.
3. **Audit-ledger F2 write integration.** Does HITL audit-write share the U-RT-59-landed `cp_audit_to_od_audit` converter, or does it need a parallel converter? `audit_hitl_span_namespace.py` already exists at CP — may suggest parallel. CXA edge decision falls out of this.
4. **Pause/resume integration.** Per `hitl_placement.py` lines 22–25, `capture_pause_snapshot` + `attempt_resume` + `deliver_webhook` are co-stubbed with `hitl_gate`. Are these all the same composer arc (U-RT-60 covers all four)? Or is pause/resume a separate arc (U-RT-61)? The C-CP-22 §22 pause/resume contract is large enough that splitting may be cleaner.
5. **Spec growth scope at C-RT-18.** Should C-RT-18 cover ONLY synchronous PRE_ACTION + SUB_AGENT_BOUNDARY gates (smallest viable), deferring VALIDATOR_ESCALATION to a validator-composer arc? Or all three placements at one contract? Precedent: C-RT-17 (sub-agent dispatch) was scoped to single-sub-agent within linear parent at first landing per U-RT-59 — splitting is acceptable per workspace pattern.

These questions are ratification material for the spec-writer arc, not blockers on this fork-filing.

## Status footer

| Field | Value |
|---|---|
| Filed | 2026-05-20 |
| HEAD at filing | `2a15504` |
| Class | 1 (halt-execution) |
| Routing target | Runtime spec amendment (`Spec_Harness_Runtime_v1.md` v1.8 → v1.9, new §14.8 C-RT-18) + runtime plan v2.6 → v2.7 (new U-RT-60 unit) |
| Halt point | Phase 7 sub-phase 7b CP-axis cluster 6 open (`phase-7-implementation` orientation turn) |
| Operator authorization | Same-turn at cluster-open AskUserQuestion (option A — Open HITL gate composer arc) |
| Next skill | spec-writer (C-RT-18 authoring) OR systems-architect mode 3 (architectural recommendation across 5 open questions) — operator decision at next prompt |
| Precedent records | `[[fork-cp-3-retry-breaker-composer-underspec]]` (U-RT-58 / C-RT-16); `[[fork-c-rt-17-step-dispatcher-parent-context-gap]]` (U-RT-59 / C-RT-17) |
| Substitutions blocked | H_T-CP-20 (HITL primitive + 4-response palette + `hitl.*` / `audit.*` namespaces). NO cascade — H_T-CP-22 (pause/resume) is structurally separate per Meta-Architecture §5; operator may elect to absorb pause/resume into this arc via Q4 spec-growth-scope ratification. |
| Retirement count impact (anticipated) | 21/49 → 22/49 at U-RT-60 landing (CP axis 9/22 → 10/22). If operator elects Q4 expand-scope (absorb pause/resume), then 21/49 → 23/49 and CP axis 9/22 → 11/22. |
| Status | **OPEN** — awaiting spec authoring arc |

---

*End of Class 1 fork record body. Systems-architect mode 3 resolution recommendation appended below.*

---

## Systems-architect mode 3 resolution recommendation (2026-05-20)

**Skill:** `systems-architect` mode 3 (Phase-7 architectural-tension resolution). **Filed:** same session as fork-record creation per §4A.3 ("recommendation appended to the Phase_7_Class_N_Tension record"). **HEAD:** `2a15504`. **Operator decision required at end of each recommendation block** — this skill recommends, does not decide.

Per `systems-architect/SKILL.md` §4A.2 procedure: each of the 5 open architectural questions decomposed against the canonical authority chain (`CLAUDE.md` §1.3: ADR → ADD → PRD → spec → plan + CXA), §2 five-axis discipline, and the substitution-table + precedent-arc evidence base.

### Q1 — H_E surface for HITL gate delivery at sub-phase 7b

**Precise tension.** What H_E surface delivers the operator response at the HITL gate during sub-phase 7b runtime? Three candidates surfaced: (a) operator-turn via Claude Code `AskUserQuestion` mechanism (synchronous); (b) polling on filesystem marker (deferred-async); (c) webhook delivery (`deliver_webhook` is co-stubbed NotImplementedError at `harness-runtime/lifecycle/hitl_placement.py:22-25`).

**Authority-chain placement.** `Phase_7_Meta_Architecture_v1.md` §5 line 23 (H_T-CP-20 substitution row) and line 942 (§10 Phase 7 sub-phase substitution map) **both name `AskUserQuestion`** as the H_E surface for HITL: "`AskUserQuestion` tool + permission-prompt approval" / "H_T HITL primitive (H_T-CP-20) wraps H_E with 4-response palette." The webhook is named as `deliver_webhook` stub at `harness-runtime/lifecycle/hitl_placement.py` lines 22-25 explicitly deferred to "L8 LOOP_INIT / integration-time composition" — post-bootstrap.

**§2 discipline.** Axis 1 (control plane). Probabilistic/deterministic boundary: the **gate evaluation** is deterministic (placement-trigger eval + palette resolution); the **operator response** is the human action surface (out-of-band from the LLM). F/D/I: derivative-of-foundational — H_T-CP-20 substitution mechanism is named at Meta-Architecture §5; this is implementation-realization of an existing decision, not a new foundational commitment.

**Recommended reading.** **AskUserQuestion at sub-phase 7b**; webhook deferred to post-bootstrap composer arc. The CP_ROUTING registry surfaces (`hitl_gate` / `deliver_webhook`) are co-stubbed because they live at the same L8 boundary; the spec-writer arc materializes `hitl_gate` against the synchronous AskUserQuestion path first, leaves `deliver_webhook` co-stubbed for the post-bootstrap durable-async arc.

**Tiebreaker check.** Confirm no ADR-D5 v1.3 §1.x clause OR `Phase_7_Workspace_Design_Substrate_Manifest_v1.md` row asserts a webhook-required posture at 7b. (None found in scan; one Read confirms.)

**Fork class per §2.7.6.** This is a Class 2 (in-execution operator decision) component of the Class 1 spec-authoring arc — the answer is chain-determined but operator-sign-off worthwhile because it shapes the spec-text at C-RT-18.

**Operator decides.**

### Q2 — Composer-stack ordering vs C-RT-15 / C-RT-16 / C-RT-17

**Precise tension.** Where in the composer stack does the HITL gate fire relative to the existing per-step composers (C-RT-15 LLM dispatch, C-RT-16 retry/breaker/fallback, C-RT-17 sub-agent dispatch), and how does HITL-as-tool-call rewriting (C-CP-17 §17.2) interact — does it replace or precede the action's primary composer?

**Authority-chain placement.** `Spec_Control_Plane_v1_9.md` C-CP-17 §17.1 declares 3-placement enum (`HITLPlacementKind`: PRE_ACTION / SUB_AGENT_BOUNDARY / VALIDATOR_ESCALATION) with placement-trigger semantics. C-CP-17 §17.2 declares HITL-as-tool-call rewriting as a **transformation primitive** invoked at PRE_ACTION when the action is a tool call (not a separate placement). C-RT-16 (retry) wraps C-RT-15 (LLM dispatch) per `Spec_Harness_Runtime_v1.md` §14.6 step structure; C-RT-17 (sub-agent dispatch) is a sibling per-step composer dispatched via `StepKindDispatcherRegistry` per §14.7.

**§2 discipline.** Axis 1 (control plane) + axis 4 (operational discipline — span emission ordering at composer boundaries). The composer-stack ordering is a determinism question (outer composer determines failure-mode propagation; inner composer is wrapped). PRE_ACTION fires **before** the action's primary composer; SUB_AGENT_BOUNDARY **wraps** C-RT-17; VALIDATOR_ESCALATION **wraps** the validator output (validator composer arc not yet built per Q5).

**Recommended reading.** Composer-stack ordering at C-RT-18 (outer-to-inner per per-step path):

```
C-RT-16 retry/breaker/fallback (outermost — retry semantics span gate evaluation too)
  → HITL gate evaluator (per WorkflowManifestEntry.hitl_placements)
    → if PRE_ACTION matches: hitl_gate fires; on APPROVE proceed; on EDIT mutate; on REJECT raise; on RESPOND record + proceed
    → inner: C-RT-15 (LLM dispatch) OR C-RT-17 (sub-agent dispatch) OR tool-dispatch (AS-axis composer — future)
```

HITL-as-tool-call rewriting (§17.2) is invoked **at the PRE_ACTION evaluator when the action is a tool call** — it rewrites the tool call to a synchronous AskUserQuestion variant rather than dispatching the tool. SUB_AGENT_BOUNDARY is invoked at C-RT-17's entry (wraps sub-agent dispatch). VALIDATOR_ESCALATION is invoked at validator-fail signal (validator composer — deferred per Q5).

**Tiebreaker check.** Confirm C-CP-17 §17.1.1 `hitl_gate(...)` signature semantics — does `placement: HITLPlacementKind` parameterize the same gate function across all 3 placements? Read shows yes (one function, placement-dispatched).

**Fork class per §2.7.6.** Class 2 component — chain-determined but operator-sign-off worthwhile for the wrap-order between C-RT-16 (retry) and the HITL gate (does the gate get retried? answer: yes per `retry.*` namespace which covers all per-step attempts including HITL-gated ones).

**Operator decides.**

### Q3 — Audit-ledger F2 write: shared converter or parallel?

**Precise tension.** Does the HITL audit-write at the gate-response site reuse the `cp_audit_to_od_audit` converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` (landed U-RT-59 Fork 2 implementation arc), or does it require a parallel converter for the HITL-specific carrier?

**Authority-chain placement.** `Spec_Control_Plane_v1_9.md` §13.5.1 NOTE 5 explicitly states: "The `CPAuditLedgerEntry` shape is declared at C-CP-16 §16.2 as the HITL per-response audit shape — `response: str ∈ {approve, edit, reject, respond}` per the C-CP-16 §16.1 4-response palette (operator response to a HITL gate). For sub-agent dispatch, this carrier is **reused via the convention `response="approve"`**..." The carrier was HITL-canonical at origin; sub-agent dispatch was the reuse.

**Evidence at HEAD.** `harness-cp/src/harness_cp/per_step_override_evaluator.py:48-79` materializes `CPAuditLedgerEntry` with 4 HITL-shaped hash fields (`edited_proposal_hash` / `rejection_reason_hash` / `response_text_hash` + presumed timestamp + prior_event_hash) — these field semantics are designed for HITL (lines 53-54: "iff `response == 'edit'`", "iff `'reject'`"). `harness-cp/src/harness_cp/audit_hitl_span_namespace.py` declares **OTel span-attribute schemas** (`AuditAttributeSchema`, `HITLSpanSchema`) — orthogonal axis to the F2 ledger-entry carrier; span-attribute declarations describe span emission, not entry-write payload.

**§2 discipline.** Axis 2 (information substrate — F2 entry write) + axis 4 (operational discipline — audit-trail composition). F/D/I: derivative — the CXA v2.4 §2.3.7 CP→OD bucket exists; the question is whether HITL adds a second typed seam to the existing bucket.

**Recommended reading.** **SHARED converter.** `cp_audit_to_od_audit` at `harness-cxa/cp_audit_conversion.py` is HITL-canonical infrastructure (U-RT-59 Fork 2 reused it via `response="approve"` convention). HITL audit-write at gate-response site populates `CPAuditLedgerEntry.response` per the operator's actual response (one of {approve, edit, reject, respond}) and invokes the existing converter. **CXA edge cardinality: CXA v2.4 §2.3.7 CP→OD bucket grows from 1 → 2 typed seams** (U-CP-28 → U-OD-00 sub-agent dispatch + new U-CP-46 → U-OD-00 HITL gate response). CXA v2.4 → v2.5 absorbs the second-seam declaration.

**Tiebreaker check.** Verify `CPAuditLedgerEntry` schema has not gained HITL-incompatible fields since U-RT-59 landing. Read at HEAD `2a15504` confirms structure unchanged from §13.5.1 NOTE 5 description. Verify converter's namespace-projection table at `_project_namespace_attrs` handles all four `response` enum values without `response="approve"` hard-coding. (Likely yes per converter design; verify at spec-writer arc.)

**Fork class per §2.7.6.** Class 2 component for CXA edge addition decision (technically Class 1 if CXA absorption is required for the arc to land; can be Class 3 if deferred — but at strict reading, CXA v2.4 cardinality declaration must absorb the new seam before implementation per `phase-7-cross-axis-composition` skill discipline).

**Operator decides.**

### Q4 — Pause/resume scope: same arc or separate?

**Precise tension.** Should the HITL gate composer arc (C-RT-18 / U-RT-60) also absorb the `capture_pause_snapshot` + `attempt_resume` + `deliver_webhook` stubs that are co-stubbed at `harness-runtime/lifecycle/hitl_placement.py:22-25`, or should pause/resume open as a separate composer arc (potentially C-RT-19 / U-RT-61)?

**Authority-chain placement.** `Phase_7_Meta_Architecture_v1.md` §5 line 25 makes H_T-CP-22 (pause/resume — "H_E `/compact` + resume + `--fork-session`") **structurally separate** from H_T-CP-20 (HITL — line 23). Each substitution gates on independent runtime composer materialization. `Spec_Control_Plane_v1_9.md` C-CP-22 §22 (context revalidation resume protocol + material-diff detection + state_summary snapshot + T-perm-2 F2-layer composition) is a large contract surface — comparable in size to C-CP-21 §21 (validator framework + transient staircase). U-RT-59 precedent: narrow-scope-first split (single-sub-agent within linear parent; fan-out deferred to parent-topology-expansion arc per `Spec_Harness_Runtime_v1.md` §14.7 change-note).

**§2 discipline.** Axis 1 (control plane — pause/resume lifecycle is structurally distinct from gate dispatch). F/D/I: pause/resume composer is derivative-of-foundational F4 (workflow lifecycle primitive) — a separate composer per ADR-F4 v1.1 commitment. Mode bleed risk if absorbed into HITL gate arc: pause/resume couples to context-revalidation + material-diff detection (C-CP-22 §22) which has nothing to do with gate-response synchronization.

**Recommended reading.** **SEPARATE arcs.** C-RT-18 / U-RT-60 = HITL gate composer (synchronous PRE_ACTION + SUB_AGENT_BOUNDARY only — see Q5). Pause/resume = future C-RT-19 / U-RT-61 absorbing `capture_pause_snapshot` + `attempt_resume` + `deliver_webhook` at one arc (since deliver_webhook is the async-resume delivery primitive, structurally adjacent to pause/resume). This split honors the structural separation at Meta-Architecture §5; matches U-RT-59 narrow-scope-first precedent; preserves rollback boundary at composer-grain.

**Tiebreaker check.** Confirm C-CP-22 §22 pause/resume contract size is comparable to C-CP-21 (~equivalent narrative + multi-step procedure + state-summary schema). One read of §22 confirms. (Skip if operator already familiar with C-CP-22.)

**Fork class per §2.7.6.** Class 2 component — chain supports separate arcs; operator decision because expand-scope is technically viable (both stubs co-resident at L8 boundary).

**Operator decides.**

### Q5 — Spec-growth scope at C-RT-18: all 3 placements or PRE_ACTION + SUB_AGENT_BOUNDARY first?

**Precise tension.** Should C-RT-18 author all 3 `HITLPlacementKind` values (PRE_ACTION + SUB_AGENT_BOUNDARY + VALIDATOR_ESCALATION) at one contract, or defer VALIDATOR_ESCALATION to a future validator-composer arc since its dependency (validator-fail signal from H_T-CP-21 framework) is not yet built?

**Authority-chain placement.** `Spec_Control_Plane_v1_9.md` C-CP-17 §17.1 declares all 3 placements at the typed library level. `Phase_7_Meta_Architecture_v1.md` §5 line 24 declares H_T-CP-21 (validator framework — "Operator reviews every sub-agent output before commit; no automated validator framework") as a separate substitution gating on U-CP-47+48+51+52 — the validator composer arc is structurally distinct and not in this arc's scope. U-RT-59 precedent: spec-grew `narrow-scope` deliberately ("Scope: single-sub-agent within linear parent" per §14.7 change-note) deferring fan-out emission to parent-topology-expansion arc.

**§2 discipline.** Axis 1 (control plane — placement-dispatch ordering). Dependency analysis: VALIDATOR_ESCALATION fires after a validator-fail signal; the validator framework (H_T-CP-21) is not built; no signal source exists at HEAD. Implementing VALIDATOR_ESCALATION at C-RT-18 would require either (a) constructing a stub signal source (silent extension — X-AL-3 violation) or (b) authoring code paths that no caller reaches (dead code — silent absorption hazard at retirement audit).

**Recommended reading.** **C-RT-18 = PRE_ACTION + SUB_AGENT_BOUNDARY only.** VALIDATOR_ESCALATION cited at C-RT-18 as **deferred to validator-composer arc** (future C-RT-NN; gates on H_T-CP-21 retirement preconditions). Spec text: explicit foreclosure clause matching U-RT-59 §14.7 narrow-scope precedent ("v1.9 MVP fan-out emission is foreclosed: composer MUST NOT...") adapted to: "v1.9 MVP VALIDATOR_ESCALATION emission is foreclosed: composer MUST NOT raise validator-escalation gate; the placement-trigger evaluator returns `no-placement-match` for VALIDATOR_ESCALATION at v1.9. Validator-composer arc lands the trigger source." This preserves the C-CP-17 §17.1 3-placement contract at the typed library while binding only 2 placements to runtime invocation at v1.9.

**Tiebreaker check.** Confirm `HITL_PLACEMENT_TRIGGERS` at `harness-cp/src/harness_cp/hitl_placement.py` carries `cardinality 3` invariant (per U-CP-38 acceptance criterion 2 "Closed at cardinality 3 — extension requires Workflow §4.1.2 Class-2 D5 revision"). Read confirms. → Foreclosure at C-RT-18 is at **runtime-invocation-binding** layer, not at typed-library cardinality layer; library cardinality preserved.

**Fork class per §2.7.6.** Class 2 component — chain supports narrow-scope-first; operator decision because the foreclosure-clause text shape matters at C-RT-18.

**Operator decides.**

### Summary table

| Q | Question | Recommendation | Chain authority |
|---|---|---|---|
| Q1 | H_E surface at 7b | AskUserQuestion (synchronous); webhook deferred to post-bootstrap | Meta-Architecture §5 line 23 + line 942 |
| Q2 | Composer-stack ordering | C-RT-16 outer → HITL gate (placement-dispatched) → C-RT-15/C-RT-17/tool-dispatch inner | C-CP-17 §17.1+§17.2 + §14.6/§14.7 wrap precedent |
| Q3 | Shared or parallel converter | SHARED — `cp_audit_to_od_audit` is HITL-canonical at origin; CXA bucket grows 1→2 seams | CP spec v1.9 §13.5.1 NOTE 5; converter implementation evidence |
| Q4 | Pause/resume scope | SEPARATE arc (future C-RT-19 / U-RT-61) | Meta-Architecture §5 line 25 structural separation + U-RT-59 narrow-scope precedent |
| Q5 | Spec-growth scope | PRE_ACTION + SUB_AGENT_BOUNDARY only; VALIDATOR_ESCALATION deferred to validator-composer arc | Meta-Architecture §5 line 24 H_T-CP-21 separation + dependency analysis + U-RT-59 narrow-scope precedent |

### Downstream artifacts requiring absorption

Per §4A.2 step 4 ("identify the downstream artifacts that must absorb the resolution — but do not edit them"):

1. **`Spec_Harness_Runtime_v1.md`** v1.8 → v1.9 — new §14.8 C-RT-18 authoring per recommendations Q1+Q2+Q3+Q5; spec-writer skill.
2. **`.harness/phase-2-session-3-track-a-atomic-decomposition.md`** v2.6 → v2.7 — new U-RT-60 unit declaration per recommendation Q3+Q5 acceptance criteria; implementation-planner skill.
3. **`Cross_Axis_Composition_Document_v2_4.md`** v2.4 → v2.5 — §2.3.7 CP→OD bucket grows 1→2 typed seams per recommendation Q3; CXA revision (likely co-published with C-RT-18 + U-RT-60).
4. **`Phase_7_Meta_Architecture_v1.md`** — substitution-table H_T-CP-20 row palette-value drift per `[[class_3_tension_meta_architecture_hitl_palette_drift]]`; Class 3, non-blocking; defer to next Meta-Architecture revision pass.

### Cross-axis verification per §2.5

| Cross-axis tension | Resolution per recommendations |
|---|---|
| Action surface ↔ Operational discipline (HITL-as-tool-call rewriting vs tool-dispatch composer) | Q2 places rewriting at PRE_ACTION evaluator, **before** tool-dispatch composer (when authored); preserves AS-axis tool-dispatch as inner composer |
| Information substrate ↔ Operational discipline (CPAuditLedgerEntry F2 write durability vs audit-ledger composition) | Q3 reuses existing `cp_audit_to_od_audit` infrastructure; preserves U-RT-59-landed CXA edge invariants; F2-write composition stays at IS substrate per existing seam |
| Control plane ↔ Operational discipline (retry-wrap around gate evaluation) | Q2 places C-RT-16 retry outer to HITL gate — retry semantics include gate-evaluation attempts (e.g., AskUserQuestion delivery failure → retry); preserves C-RT-16 `retry.*` namespace coverage |

No new cross-axis tensions surfaced.

### Explicit "operator decides" marker

Per `systems-architect/SKILL.md` §4A.4: "Does not decide. It recommends; the operator decides." All 5 recommendation blocks above represent the chain-supported reading; operator retains authority to ratify, modify, or counter-route any of them at the spec-writer arc opening. Recommended sequence at operator authorization:

1. Ratify (or modify) the 5-question recommendation block above.
2. If ratified-as-recommended: invoke `spec-writer` skill to author C-RT-18 in `Spec_Harness_Runtime_v1.md` v1.8 → v1.9 per Q1+Q2+Q3+Q5 commitments + narrow-scope foreclosure clauses per Q5.
3. Co-publish runtime plan v2.6 → v2.7 (new U-RT-60) via `implementation-planner` skill.
4. Co-publish CXA v2.4 → v2.5 (CP→OD bucket grows 1→2 seams) inline at spec-writer arc.
5. (Optional) `harness-adversarial-reviewer` Phase-7 pre-implementation review of the C-RT-18 + U-RT-60 + CXA v2.5 spec+plan bundle before implementation lands.
6. `phase-7-implementation` skill lands U-RT-60.
7. `phase-7-substitution-retirement` skill files Phase 7d batch 8 retirement event (H_T-CP-20 RETIRED).

---

*End of systems-architect mode 3 resolution recommendation. The chain speaks; operator decides.*

---

## Operator ratification (2026-05-20, same session)

**All 5 recommendations ratified as-recommended at AskUserQuestion option A** (post-recommendation block). Decision:

- Q1 = AskUserQuestion at 7b; webhook deferred to post-bootstrap arc
- Q2 = C-RT-16 (retry) outer → HITL gate (placement-dispatched) → C-RT-15/C-RT-17/tool-dispatch inner
- Q3 = SHARED `cp_audit_to_od_audit` converter; CXA v2.4 §2.3.7 bucket grows 1→2 typed seams (CXA v2.4 → v2.5 co-publish)
- Q4 = SEPARATE arc — pause/resume + `deliver_webhook` defer to future C-RT-19 / U-RT-61
- Q5 = C-RT-18 scope = PRE_ACTION + SUB_AGENT_BOUNDARY only; VALIDATOR_ESCALATION foreclosed at v1.9 MVP per U-RT-59 narrow-scope precedent

**Next skill: `spec-writer`** — author C-RT-18 in `Spec_Harness_Runtime_v1.md` v1.8 → v1.9 per Q1+Q2+Q3+Q5 commitments + Q5 narrow-scope foreclosure clause; co-publish CXA v2.4 → v2.5 (§2.3.7 cardinality update) inline. Then `implementation-planner` for U-RT-60 unit addition at runtime plan v2.6 → v2.7. Status of this fork record: **OPEN → moves to AUTHORING** at spec-writer arc start.

---

## Spec-writer arc disposition (2026-05-20, same session)

**APPLIED.** spec-writer arc landed two coupled deliverables this session:

1. **`Spec_Harness_Runtime_v1.md` v1.8 → v1.9** — title bumped; change-note prepended (records the 5-Q ratification table + fork-record back-reference); new §14.8 C-RT-18 contract authored (~270 lines, 7 subsections matching §14.7 precedent shape: §14.8.1 architectural surfaces + wrap-asymmetry table; §14.8.2 per-step invocation discipline with 6 steps + 4-substep audit-write at step 4h; §14.8.3 AskUserQuestion delivery per Q1; §14.8.4 placement-trigger + VALIDATOR_ESCALATION foreclosure per Q5; §14.8.5 span emission; §14.8.6 audit composition + CXA seam-cardinality update; §14.8.7 4 path-(ii) NOTEs deferred per advisor pre-emption to prevent F2-01-style discovery-at-implementation hazard); 4 new fail classes (`RT-FAIL-HITL-GATE-REJECTED` / `RT-FAIL-HITL-GATE-TIMEOUT` / `RT-FAIL-HITL-GATE-AUDIT-COMPOSE` / `RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19`); §15 traceability row added for U-RT-60 (citing C-RT-18 + 6 CP contracts + CXA v2.5 §2.3.7).

2. **`Cross_Axis_Composition_Document_v2_5.md`** (NEW file) — pointer-style document matching v2.4's "Only the sections enumerated in §0.2 are revised" pattern; §0.4 reclassification matrix extended with v2.5 column (CP→OD 1→2; aggregate 93→94; genuine 23→24); §2.1 adjacency matrix updated; §2.3.7 row appended for new U-CP-46 → U-OD-00 typed seam (Class G; shares `cp_audit_to_od_audit` converter at `harness-cxa/`); §2.4 per-axis outbound posture summary updated (CP outbound 56→57; genuine 15→16); v2.5 change-note + filing footer.

**Audit-before-emit per spec-writer §"Audit checklist":**

| Check | Status |
|---|---|
| Decided-fix | ✅ 5 ratifications + advisor-authorized path-(ii) NOTE pre-emption. Nothing decided by spec-writer. |
| No-extension | ✅ The 5 ratifications bound the contract; path-(ii) NOTEs are deferrals not commitments; one new fail class beyond the 3 anticipated (`RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19`) is the structural consequence of Q5 foreclosure — declarative-only, no extension surface. |
| Verbatim round-trip | ✅ Q5 foreclosure clause mirrors U-RT-59 §14.7 narrow-scope precedent text shape ("v1.9 MVP VALIDATOR_ESCALATION emission is foreclosed: composer MUST NOT raise validator-escalation gate; the placement-trigger evaluator returns no-placement-match for VALIDATOR_ESCALATION at v1.9. Validator-composer arc lands the trigger source."). |
| Preservation | ✅ Runtime spec v1.8 content outside §14.8 + §15 row addition + change-note prepend preserved verbatim. CXA v2.5 preserves v2.4 §2.3.1–§2.3.6 + §0.11 + §2.2 (label-only update). |
| Version + change-note | ✅ Both files bumped per forward-only ledger discipline (workspace `CLAUDE.md` §4.3); change-notes record trigger / scope / revised / preserved / findings / tension-record reference. |
| Back-reference reconciliation | ✅ Intra-file: §14.8 cites §14.7.2 step 8 pattern; §15 row links U-RT-60 → C-RT-18; CXA v2.5 §2.3.7 augments existing v2.4 row preservation. Cross-file absorption (workspace `CLAUDE.md` §2.3/§2.4 + per-axis CLAUDE.md + runtime plan + harness-cp/harness-od CLAUDE.md edge-count updates) flagged in change-notes — owed to `implementation-planner` revision-pass + workspace-tracking absorption. |
| Citation byte-exact | ✅ Citations to CP spec v1.9 §13.5.1 NOTE 5, Meta-Architecture §5, runtime spec §14.7 patterns, CXA v2.5 §2.3.7 — all consistent. |

**Next skill: `implementation-planner`** — add U-RT-60 to runtime plan at `.harness/phase-2-session-3-track-a-atomic-decomposition.md` v2.6 → v2.7. Acceptance criteria derived from C-RT-18 §14.8.2 step 4 + §14.8.6 audit-write + §14.8.7 NOTE foreclosures. Plan-unit shape matches U-RT-59 v2.6 L9-ter precedent.

**Status of this fork record: AUTHORING → APPLIED** at spec-writer arc landing. Fork closure pending U-RT-60 implementation arc landing per `phase-7-implementation` skill discipline (next session at operator pacing).
