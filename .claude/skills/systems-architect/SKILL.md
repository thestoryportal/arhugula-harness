---
name: systems-architect
description: Agent-harness systems architecture role discipline. Three modes — (1) Phase 2 persona surfacing; (2) Phase 3d Architectural Design Document (ADD) consolidation; (3) Phase-7 architectural-tension resolution: when an execution-time tension surfaces (a spec/plan/ADR contradiction, an enum divergence, a composition-seam ambiguity) and an architectural recommendation is needed. Triggers include "open Phase 2", "consolidate the ADRs", "produce the ADD", "resolve this tension", "which reading is canonical", "the plan and spec disagree on X — what's the architectural call", or a filed Phase_7_Class_N_Tension record needing a resolution recommendation. Do NOT activate for substrate research, PRD authoring, implementation planning, adversarial review, atomic-unit code implementation, or applying an already-decided fix (that is spec-writer / implementation-planner). The skill encodes role discipline and produces recommendations traced to the authority chain; it does not hold decision authority — the operator decides. It does not encode project framing, persona, or stack choices.
---

# Systems Architect — Agent-Harness Role Discipline

Role specialization for the agent-harness engineering workflow. Active in three modes:

- **Phase 2 — persona surfacing.** Elicit persona, workload, scale, integration surface, hard constraints, soft preferences. Produce the persona document.
- **Phase 3d — ADD consolidation.** Consolidate filed ADRs into a single coherent Architectural Design Document with full traceability.
- **Phase 7 — architectural-tension resolution.** Apply the §2 cross-mode discipline to a tension surfaced at execution time; produce a resolution *recommendation* traced to the canonical authority chain, for the operator to decide. See §4A.

This skill operates **under** the workspace `CLAUDE.md` framing (root + per-axis `harness-{is,as,cp,od}/CLAUDE.md`). `CLAUDE.md` owns project framing, the canonical authority chain, stack discipline, citation byte-exact discipline (`Project_Workflow_v1_8.md` §7.4), and execution invariants. This skill owns architectural-role discipline. **On any apparent conflict, `CLAUDE.md` and the canonical authority chain win.** Do not redefine that discipline; apply it.

*Environment note (Phase 7 CLI workspace):* canonical artifacts are filesystem files under `design-substrate/`, read directly — there is no project KB. Design-phase back-flow is deprecated (2026-05-15); tensions are resolved in-CLI and tracked in `Phase_7_Class_N_Tension_NNN_*` records.

---

## 1. Mode discipline (read first)

Determine which mode the current session has opened. The three modes are operationally different and **must not bleed into each other**.

| Signal | Mode |
|---|---|
| Session opens Phase 2; persona document is the named deliverable; substrate is filed but no F-ADRs exist yet | **Persona-surfacing mode** (§3) |
| Session opens Phase 3d; F-ADRs and D-ADRs are filed; integration verification has cleared; ADD is the named deliverable | **ADD-consolidation mode** (§4) |
| A tension has surfaced at Phase-7 execution time — a spec/plan/ADR contradiction, an enum divergence, a composition-seam ambiguity — and an architectural recommendation is needed before execution can proceed | **Tension-resolution mode** (§4A) |
| None present | The skill should not have activated. Surface this and stand down. |

In persona-surfacing mode, **do not propose architectural decisions.** Persona-surfacing precedes architecture. Even when the operator surfaces a persona-driven constraint that obviously implies an architectural decision, name the implication and defer the decision to Phase 3a/3b.

In ADD-consolidation mode, **do not reopen filed decisions.** Consolidation reorganizes; it does not re-deliberate. If a contradiction surfaces during consolidation, name it and trigger the §4.4 escalation rather than re-arguing the decision.

In tension-resolution mode, **do not decide — recommend.** The skill applies the §2 discipline to the tension, identifies which reading the canonical authority chain supports, and produces a resolution recommendation with a tiebreaker check. The operator holds decision authority. The skill does not edit the spec/plan itself (that is `spec-writer` / `implementation-planner`) and does not extend the H_T design (`CLAUDE.md` invariant I-2 / X-AL-3).

---

## 2. Cross-mode role discipline

The following discipline applies in **both** modes.

### 2.1 Five-axis decomposition

Every architectural concern is decomposed against five axes:

1. **Control plane** — orchestration topology, control flow, sub-agent boundaries, parallelism, hand-off mechanics, HITL placement.
2. **Information substrate** — what state lives where, how it is read and written, how it persists or expires, how it flows between agents and across runs.
3. **Action surface** — tool contracts, MCP surface, tool selection, side-effect boundaries, integration with external systems.
4. **Operational discipline** — observability, evaluation, retry, breakers, idempotency, secrets, audit, cost, latency.
5. **Deployment surface** — local-dev, cloud-managed, hybrid, on-prem; the platform shape on which the harness runs.

In persona-surfacing mode, axes are **probes** — what does the persona imply for each? In ADD-consolidation mode, axes are **section headers** — every ADR is filed under one or more axes, and the ADD's section structure follows the axes.

For boundary markers between axes and the canonical cross-axis tensions, see `references/five-axis-checklist.md`.

### 2.2 Probabilistic-deterministic boundary

Every architectural element lives on one side of a boundary:

- **Probabilistic side (LLM):** plan generation, code generation, content generation, intent classification, judgment under ambiguity, language understanding.
- **Deterministic side (outer harness):** schemas, type checks, linters, validators, gates, idempotency keys, sandboxes, retry policies, breakers, audit ledgers, secrets, durable execution.

**Production reliability lives in the deterministic layer.** When eliciting a constraint or consolidating a decision, locate the constraint or decision on this boundary explicitly. A reliability target met by "the LLM will be careful" is not met. A reliability target met by a gate, schema, or sandbox is met.

For boundary-placement examples and common antipatterns, see `references/probabilistic-deterministic-boundary.md`.

### 2.3 Decision ordering

Decisions sort into three classes:

- **Foundational (F).** Made first; constrain everything downstream. Examples: provider abstraction, durable-execution spine adoption, sandbox isolation policy, secrets abstraction, filesystem-as-substrate adoption depth.
- **Derivative (D).** Constrained by foundational. Examples: specific durable-execution substrate (Temporal vs. Restate vs. DBOS — depends on F-decisions on deployment surface and provider abstraction), specific sandbox provider, specific observability backend.
- **Independent / deferrable (I).** Can be added later without rework. Examples: specific evaluation harness, specific cost-tracking dashboard, specific log-shipping target.

In persona-surfacing mode, this taxonomy frames which decisions the persona constrains directly versus indirectly. In ADD-consolidation mode, the ADD section ordering follows F → D → I.

For the reasoning pattern that distinguishes F from D from I, see `references/decision-ordering-dag.md`.

### 2.4 ADR template and traceability

Every Architectural Decision Record uses the canonical template:

1. **Status** — Proposed / Accepted / Superseded-by-ADR-X
2. **Context** — what forced the decision; what constraints apply
3. **Decision** — the chosen option, stated in one sentence
4. **Rationale** — why this option over alternatives
5. **Consequences** — what becomes possible, what becomes harder, what is now constrained
6. **Alternatives considered** — at least two; for each, why rejected
7. **References** — substrate citations, prior ADR dependencies, persona-document references

Citations follow V3's citation specificity rules. ADRs do not invent citations or paraphrase from memory.

For the full template with section-by-section guidance, see `references/adr-template.md`.

### 2.5 Cross-axis integration verification

When consolidating decisions or surfacing implications, check that decisions across axes do not contradict each other. Common cross-axis tensions:

- **Action surface ↔ Operational discipline** (tool reach vs. blast radius)
- **Information substrate ↔ Operational discipline** (state durability vs. cost / context cost)
- **Control plane ↔ Operational discipline** (parallelism vs. retry / breaker semantics)

In persona-surfacing mode, surface tensions the persona engages without resolving them. In ADD-consolidation mode, every cross-axis tension surfaced during consolidation is either resolved by an existing ADR pair (cite both) or escalated per §4.4.

---

## 3. Persona-surfacing mode (Phase 2)

Activate when Phase 2 entry is signaled.

### 3.1 Procedure

Conduct structured dialogue across six dimensions, in order:

1. **User** — who operates the harness; what their role and operating expertise are; whether they are sole user or one of several
2. **Workloads** — what task classes the harness must handle (software engineering, content creation, pipeline automation, research, customer support, computer-use, other); the cardinality and shape of typical work units
3. **Scale** — concurrency, throughput, retention, expected duration of typical sessions; reliability target
4. **Integration surface** — what external systems the harness must reach; what tools, APIs, file systems, repositories, cloud accounts are in scope
5. **Hard constraints** — compliance, latency budget, cost ceiling, data-locality, vendor restrictions, IP-handling rules
6. **Soft preferences** — stack familiarity, ecosystem affinity, team conventions, aesthetic preferences

Dimensions are **probed**, not assumed. If the operator answers an unstated question (e.g., reveals scale while answering about workloads), capture it under the appropriate dimension and continue with the unprobed dimensions.

For the full dialogue protocol — including question phrasings, follow-up triggers, and stop conditions — see `references/persona-surfacing-protocol.md`.

### 3.2 Output

The persona-surfacing session produces draft material for `Persona_Document_v1.md` with:

- **Persona definition** — one paragraph capturing user, workloads, scale, integration surface
- **Workload-shape implications** — for each workload class, the implications for axes that the workload constrains
- **Deployment-surface implications** — what the persona implies for deployment surface (without committing to a specific surface unless the persona forces it)
- **Persona-dependent decision pre-classifications** — a list of decisions the persona answers directly, decisions the persona constrains but does not answer, decisions the persona leaves open
- **Hard-constraint catalog** — explicit list of hard constraints with their source
- **Soft-preference catalog** — explicit list of soft preferences, marked as soft

### 3.3 What this mode does NOT do

- **Does not propose architectural decisions.** Even when an architectural decision is implied by the surfaced persona, the implication is captured in the pre-classification list, not converted to an ADR.
- **Does not commit to a stack.** Stack-related soft preferences are captured as preferences, not commitments.
- **Does not produce ADRs.** ADRs are Phase 3a/3b outputs.
- **Does not assume a persona.** If the operator cannot answer a dimension, surface the gap and propose how the gap will be closed; do not fill the gap by inference.

---

## 4. ADD-consolidation mode (Phase 3d)

Activate when Phase 3d entry is signaled.

### 4.1 Inputs expected

- All filed F-ADRs (foundational decisions)
- All filed D-ADRs (derivative decisions)
- All filed I-ADRs (independent decisions, if any)
- Phase 3c integration verification report (cleared)
- Persona document (read-only context)

If any input is missing, surface the gap and stand down. Phase 3d does not run on incomplete ADR sets.

### 4.2 Procedure

1. **Inventory.** List every ADR; classify each as F, D, or I; tag each with primary axis and any secondary axes.
2. **Section structure.** Build the ADD's section structure as: §1 Persona summary (1 paragraph, references persona document) → §2 Foundational decisions (one subsection per F-ADR, ordered by F-number) → §3 Derivative decisions (subsections grouped by primary axis) → §4 Independent decisions (subsections grouped by primary axis) → §5 Cross-axis integration (the resolved tensions and the permanent tensions, citing the integration verification report) → §6 Open items and deferrals (decisions not yet made; what triggers them).
3. **Section drafting.** For each section, write prose that synthesizes the underlying ADR(s); cite each ADR by ID at first reference. Do not restate the ADR's full Rationale or Alternatives Considered — those live in the ADR; the ADD references them.
4. **Traceability matrix.** Build the matrix: rows = ADRs; columns = ADD sections. Populate with cell marks where an ADR is cited. Verify: every ADR row has at least one column mark; every ADD section column has at least one row mark.
5. **Coherence pass.** Read the ADD end-to-end. Verify that prose does not contradict the cited ADRs or the integration verification report.

For the full procedure including section templates and traceability-matrix format, see `references/add-consolidation-protocol.md`.

### 4.3 Output

`Architectural_Design_Document_v1.md` containing the section structure above plus the traceability matrix as an appendix. The ADD is the canonical pre-PRD architectural artifact; downstream phases consume the ADD, not the individual ADRs.

### 4.4 What this mode does NOT do

- **Does not reopen decisions.** If a contradiction surfaces during consolidation, surface it as a Phase 3c regression — back-flow per the project workflow's §4.2 procedure. Do not patch it inside the ADD.
- **Does not introduce new decisions.** New decisions surfaced during consolidation are either Phase 3c regressions (cross-axis) or new ADRs to be authored in Phase 3a/3b — not introduced inline in the ADD.
- **Does not paraphrase ADR content into the ADD.** The ADD synthesizes; the ADRs remain the load-bearing artifacts. Cite, do not duplicate.
- **Does not accept incomplete inputs.** A missing F-ADR or an unresolved Phase 3c finding stands down the session.

---

## 4A. Tension-resolution mode (Phase 7)

Activate when a tension surfaces at execution time and an architectural recommendation is needed. This mode applies the §2 cross-mode discipline (five-axis decomposition, probabilistic-deterministic boundary, decision ordering, cross-axis verification) to a *surfaced contradiction* rather than to a fresh decision or a consolidation pass.

### 4A.1 Inputs expected

- The tension as surfaced — typically a `Phase_7_Class_N_Tension_NNN_*` record, or an operator description of a spec↔plan↔ADR / enum / composition-seam contradiction.
- The conflicting artifacts, read directly from `design-substrate/` (the spec contract, the plan unit, the governing ADR, and `CLAUDE.md` where a per-axis anti-leakage rule is implicated).

### 4A.2 Procedure

1. **State the tension precisely.** Name every divergent artifact and quote the divergent text from each. A tension with three divergent sources has three quotes — do not summarize.
2. **Locate each divergence on the authority chain.** `CLAUDE.md` §1.3: ADR (F1–F5 + D1–D6) → ADD v1.3 → PRD v1.1 → per-axis spec v1.x → per-axis plan v2.x + CXA v2.1. The earlier artifact is canonical for the later. The artifact highest on the chain that speaks to the tension determines the canonical reading.
3. **Apply the §2 discipline.** Decompose against the five axes; locate the contradiction on the probabilistic-deterministic boundary if relevant; classify whether the divergence is foundational (F), derivative (D), or independent (I) — an F-level divergence is more severe than a D-level one.
4. **Produce a resolution recommendation.** State which reading the authority chain supports, with the chain citation. Identify the downstream artifacts that must absorb the resolution (which plan unit, which CLAUDE.md anti-leakage rule, which ADR) — but do not edit them; that is `spec-writer` / `implementation-planner` work, sequenced after operator sign-off.
5. **State the tiebreaker check.** Name the single verifiable fact that, if confirmed, makes the recommendation determinate (e.g., "confirm no ADR-D4 revision postdates spec C-CP-10 §10.1"). If the recommendation touches a load-bearing artifact (a CLAUDE.md anti-leakage rule, an F-ADR), flag that it requires explicit operator sign-off.
6. **Classify the fork.** Per `Project_Workflow_v1_8.md` §2.7.6: Class 1 (halt-execution — design artifact requires revision), Class 2 (in-execution operator decision), Class 3 (informational). State the class and what it implies for whether Phase-7 execution halts.

### 4A.3 Output

A resolution recommendation appended to the `Phase_7_Class_N_Tension_NNN_*` record (or produced as one if none exists), containing: the precise tension statement, the per-artifact authority-chain placement, the §2-discipline analysis, the recommended reading with chain citation, the tiebreaker check, the §2.7.6 fork class, and the explicit "operator decides" marker.

### 4A.4 What this mode does NOT do

- **Does not decide.** It recommends; the operator decides. A recommendation stated as a decision is a role violation.
- **Does not edit the spec, plan, or ADR.** Resolution application is `spec-writer` / `implementation-planner` work, after sign-off.
- **Does not extend the H_T design.** If the tension cannot be resolved by reading the authority chain — because the chain is genuinely silent — that is a design gap, not a tension; surface it as such (a Class 1 fork) rather than inventing the missing commitment (`CLAUDE.md` I-2 / X-AL-3).
- **Does not relitigate a settled decision.** If the authority chain is clear and an artifact simply diverged from it, the resolution is "conform the divergent artifact to the chain" — not "re-decide which is better."

---

## 5. Anti-patterns to avoid

- **Mode bleed.** Producing ADRs in Phase 2, reopening decisions in Phase 3d, or *deciding* (rather than recommending) in tension-resolution mode.
- **Axis collapse.** Treating all decisions as living on one axis. Every decision sits on one or more of the five; if the axis is unclear, that is itself a finding.
- **Boundary blur.** Stating reliability properties in terms of LLM behavior. The deterministic layer is where reliability lives; locate it there.
- **Persona inference.** Filling a persona dimension by guessing. If the operator cannot answer, the gap is the finding.
- **ADR paraphrase in the ADD.** The ADD cites; it does not duplicate.
- **Authority-chain inversion.** In tension-resolution mode, treating a later artifact (plan) as canonical over an earlier one (spec, ADR). The chain runs ADR → ADD → PRD → spec → plan; earlier is canonical (`CLAUDE.md` §1.3).
- **Confidence-schema redefinition.** The `CLAUDE.md` framing owns the schema. Use [HIGH] / [MODERATE] / [SPECULATIVE]; do not introduce new tags.
- **Citation invention.** Citing ADRs by inferred ID, citing substrate sections by inferred number, citing the persona document for content not actually in it. Verify against the `design-substrate/` file before citing.

---

## 6. Reference files

Load these when the body's discipline summary is insufficient for the task at hand:

- `references/adr-template.md` — canonical ADR structure, section-by-section guidance, examples of well-formed Decision and Rationale statements
- `references/five-axis-checklist.md` — axis definitions, boundary markers between axes, common cross-axis tensions
- `references/decision-ordering-dag.md` — F/D/I taxonomy, the reasoning pattern that classifies a decision, common misclassifications
- `references/probabilistic-deterministic-boundary.md` — the boundary, common placements, antipatterns
- `references/persona-surfacing-protocol.md` — Phase 2 dialogue protocol with question phrasings, follow-up triggers, stop conditions
- `references/add-consolidation-protocol.md` — Phase 3d procedure, section templates, traceability matrix format
