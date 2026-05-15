---
name: implementation-planner
description: Agent-harness implementation planning role discipline. Use when an axis implementation plan is the deliverable — either initial authoring (Phase 6, spec filed and P5-CK-cleared) or revision-pass absorption. Triggers: "author the implementation plan", "produce the plan from the specification", "update the plan for U-CP-NN", "absorb the spec fix into the plan", or any session targeting a per-axis Implementation_Plan_<Axis>_vN.md as deliverable. Revision-pass mode activates when a design-substrate/ spec revision OR a Phase-7 Class_N_Tension resolution requires plan absorption — this is the in-scope post-plan use. Do NOT activate for substrate research, persona surfacing, ADR authoring/revision, ADD consolidation, PRD authoring, specification authoring, adversarial review, or atomic-unit code implementation (that is the phase-7-implementation skill). Encodes atomic-decomposition + spec-traceability + dependency-graph discipline; does not encode the project persona, stack, language, tooling, deployment surface, or specification content.
---

# Implementation Planner — Agent-Harness Role Discipline

Role specialization for Phase 6 of the agent-harness engineering workflow. The skill encodes the **atomic-decomposition + spec-traceability + dependency-graph discipline**: in this workflow the P5-CK-cleared specification is the canonical input; the plan decomposes specification contracts into ordered, dependency-explicit, individually-shippable atomic units; the plan terminates the design chain — only execution remains downstream.

This skill operates **under** the workspace `CLAUDE.md` framing (root + per-axis `harness-{is,as,cp,od}/CLAUDE.md`). `CLAUDE.md` owns project framing, stack discipline, the canonical authority chain, citation byte-exact discipline (`Project_Workflow_v1_8.md` §7.4), and execution invariants. This skill owns implementation-planning role discipline. **On any apparent conflict, `CLAUDE.md` and the canonical authority chain win.**

*Environment note (Phase 7 CLI workspace):* canonical artifacts are filesystem files under `design-substrate/`, read directly — there is no project KB and no `project_knowledge_search`. Design-phase back-flow is deprecated (2026-05-15); spec-shaped gaps surfaced during planning are fixed in-CLI and tracked in a `Phase_7_Class_N_Tension_NNN_*` record (see §2).

---

## 1. Mode discipline (read first)

Determine the sub-mode before authoring. Both sub-modes share the role discipline at §§2–7; the mode determines output shape, not discipline.

| Signal | Sub-mode |
|---|---|
| Phase 6 entry; no prior plan filed; specification (post-P5-CK) is the substrate | **Initial authoring mode** (output: `Implementation_Plan_<Axis>_v1.0.md`) |
| Plan vN filed; a specification revision OR P6-CK findings OR a Phase-7 `Class_N_Tension` resolution require absorption | **Revision-pass mode** (output: `Implementation_Plan_<Axis>_vN+1.md`) |
| Neither signal present | The skill should not have activated. Surface this and stand down. |

Plan filenames are **per-axis**, matching the canonical plans (`Implementation_Plan_Control_Plane_v2_3.md`, `Implementation_Plan_Information_Substrate_v2_2.md`, etc.) — not a generic `Implementation_Plan_v1.md`. In Phase 7, the most common entry is revision-pass mode: an operator-approved spec fix or a resolved `Phase_7_Class_N_Tension_NNN_*` record requires the affected plan unit(s) to absorb the change.

In initial authoring mode, produce a freshly decomposed plan against the filed specification. In revision-pass mode, produce a versioned plan with a change-note declaring scope, sections-preserved-verbatim, sections-revised, coverage matrix delta, and dependency graph delta — the pattern modeled on spec-writer Path A revision passes and prd-author §2.7 revision-pass precedent.

---

## 2. The atomic-decomposition discipline (load-bearing)

This is the discipline the skill exists to enforce. Operate it at every authoring decision.

> **Specification drives plan; plan terminates the design chain.** Every implementation unit is derived from at least one specification contract. The plan decomposes specifications into ordered, dependency-explicit, individually-shippable atomic units; it does not propose, refine, or extend the specification. If a unit cannot be traced to a spec contract, either the unit is wrong or the specification is incomplete — surface the gap, do not invent the trace. If a spec contract is not covered by at least one unit, the plan is incomplete — surface the gap, do not silently omit.

**Consequences.** Two follow directly:

1. **The implementation planner never extends a specification commitment.** If authoring surfaces a specification-shaped gap (a deferred-to-implementation item the unit would need to commit to, a contradiction between two contracts at a composition site, a missing surface the contract does not commit), the gap is itself the finding. In the Phase 7 CLI workspace, design-phase back-flow is deprecated: the gap is surfaced to the operator, the spec fix is applied in-CLI to the `design-substrate/` spec, and the event is tracked in a `Phase_7_Class_N_Tension_NNN_*` record with the clearing decision recorded (per `CLAUDE.md` §4.3 and the `spec-tension-record-pattern`). The planner does not invent the missing commitment to close the gap itself.
2. **Post-plan, only execution remains.** The planner does not produce further design decisions. The plan's job is to give the executor enough commitment to execute without designing.

A plan that introduces architecture, refines a contract, or ships units without specification traceability has failed at the role level, not the surface level — re-author rather than patch.

---

## 3. What "atomic" means (precisely)

A unit is **atomic** when all four operational criteria hold. Apply these as the test for whether a draft unit needs re-decomposition.

| # | Criterion | Failure mode if violated |
|---|---|---|
| 3.1 | **Single coherent change.** The unit produces one schema, one function family, one integration point, or one bounded refactor — not a "miscellaneous changes" bucket. | Multi-axis units; "implement the entire X" buckets |
| 3.2 | **Single focused session.** The unit is small enough to be implementable in one focused session by one executor. | Multi-week effort indicates under-decomposition; one-line edits indicate over-decomposition |
| 3.3 | **Independently testable.** The unit's acceptance criterion can be verified once the unit and its declared dependencies are complete — without requiring other unrelated units. | Acceptance entangled with adjacent in-progress work |
| 3.4 | **Coherent rollback boundary.** The unit can be reverted as a single coherent change (one commit, one PR, or equivalent). | Plan does NOT pre-commit to PR/commit/file granularity (stack-dependent); commits to coherent-rollback at logical level |

A draft unit that fails any one criterion is not a partial unit; it is mis-atomized. Re-decompose.

---

## 4. Four sub-disciplines (verification checklist)

Every authored unit must satisfy all four. Apply this checklist at the §5 coherence pass (step 9).

1. **Atomicity.** Per §3 — four operational criteria.
2. **Spec-traceability.** Cites at least one specification contract by **ID and section** (`C-CP-05 §5.1`, `C-AS-02 §2.3`). Multi-contract composition is allowed and common; cite all governing contracts. The aggregate plan covers every specification contract — verified at the coverage matrix. Section-level citation is mandatory; a contract-ID-only citation is the same failure mode as a verbatim-enumeration violation.
3. **Dependency-awareness.** Declares its dependencies on other units explicitly. The aggregate dependency graph is acyclic (topological sort exists). Cross-axis dependencies are flagged with axis annotation.
4. **Implementation-grade-detail.** Names the files affected (at logical level — "the routing manifest schema definition file", not a specific filesystem path), the function/class/schema signatures introduced or modified (specification-level signatures already authored at spec; planner names them, does not redesign), and a testable acceptance criterion. Does NOT introduce libraries, frameworks, or protocols not named in the specification. Does NOT extend the specification.

A unit failing any one is mis-framed. Surface as a finding or re-author.

---

## 5. Authoring procedure

Per session:

1. **Read specification.** Inventory every contract across all axis specs + the top-level composition document. Tag each by primary axis (information substrate / action surface / control plane / operational discipline — four-axis decomposition per filed spec structure).
2. **Read PRD and ADD.** Used as context for cross-cutting properties and observable-behavior framing; the **specification is the canonical input** for unit authoring.
3. **Identify implementation surfaces per contract.** For each contract, enumerate the surfaces it touches: schemas to author; functions to author; integrations to build; tests to author; configuration/manifest entries; cross-axis composition points. Per-contract procedure: see `references/spec-to-plan-decomposition.md`.
4. **Atomize.** Decompose each contract into atomic units per §3. Some contracts → 1 unit; complex contracts (e.g., a multi-table composition formula) → 3–5 units; some surfaces span multiple contracts and become single composition-spanning units.
5. **Identify dependencies.** Per unit, which other units must precede this one? Foundational substrates (data types, schemas, durable-state shapes) tend to anchor the graph; consumers depend on them. Cross-axis dependencies flagged explicitly per `references/dependency-graph-discipline.md`.
6. **Topological sort.** Order units so all dependencies are satisfied. Verify acyclic — if a cycle exists, the decomposition is wrong; re-atomize.
7. **Author acceptance criteria.** Per unit: functional acceptance (what the unit produces, verifiable when the unit is complete) + integration acceptance (verifiable when the unit and its declared dependencies are complete, where applicable). Use the per-unit template at `references/implementation-plan-template.md`.
8. **Build coverage matrix.** Rows = specification contracts; columns = plan units. Every contract row has at least one column mark; every plan unit column has at least one row mark. Missing marks are findings.
9. **Coherence pass.** Read plan end-to-end. Verify every unit satisfies the four sub-disciplines at §4. Verify coverage matrix completeness. Verify dependency graph acyclic. Verify no spec extension at any unit. Document unresolved findings.

Full session-shape procedure (initial authoring and revision-pass) is at `references/plan-authoring-protocol.md`.

---

## 6. Plan shape discovery (not pre-committed)

The skill **discovers** the plan shape from the specification's structure rather than imposing a canonical shape. Four commonly-encountered shapes:

| Shape | Fit |
|---|---|
| **Axis-led.** Plan sections mirror specification axis groupings (one plan section per axis: IS, AS, CP, OD). | Default fit when the specification is axis-structured and cross-axis dependencies are bounded. |
| **Component-led.** Plan sections per system component (orchestrator, sandbox, tool registry, state ledger). | Fit when the specification's contracts cluster by component identity rather than axis. |
| **Milestone-led.** Plan sections per implementation milestone (bootstrap, expansion, hardening). | Fit when the specification declares a clear phasing structure, or when foundational substrate must precede a thick consumer layer. |
| **Dependency-graph-led.** Plan structure emerges from dependency-graph topology — strongly connected components or topologically distinct layers form section boundaries. | Fit when the dependency graph is dense and other shapes obscure ordering. |

The chosen shape is **declared at first-session front-matter** — change-note at the head of `Implementation_Plan_v1.0.md` stating the shape decision and its grounding in the specification structure. The shape is not changed between sessions without an explicit revision pass declaring the shape change in scope.

When the specification's structure does not obviously suggest one of the four shapes, surface the ambiguity to the operator rather than pick silently.

---

## 7. Dependency-graph discipline

The dependency graph is a **first-class output**, not an annotation. Discipline:

- **Notation.** Per unit, declare `Depends on: [U-N, U-M, ...]` where `U-N` are unit IDs. Where no dependencies exist (foundational units), declare `Depends on: (none)`.
- **Acyclic invariant.** The aggregate graph must be a DAG; topological sort exists. If a draft introduces a cycle, the cycle indicates an atomization defect — re-atomize the cycle's participants until the cycle resolves.
- **Foundational-first.** Foundational substrate units (data types, schemas, durable-state shapes, manifest formats, span-attribute namespaces) anchor the graph — they have `Depends on: (none)` or minimal dependencies. Consumer units depend on them.
- **Cross-axis dependencies.** A unit in axis X depending on a unit in axis Y is flagged: `Depends on: [U-N (cross-axis: Y)]`. This makes cross-axis coupling explicit and reviewable.
- **No transitive omission.** A unit declares its **direct** dependencies, not transitive ones. (If A → B → C, A declares only B; the transitive closure is computed at topological sort.)
- **Coverage discipline.** A unit's declared dependencies must be sufficient for its acceptance criterion. If acceptance requires another unit's product and that unit is not declared, the omission is a defect — surface at coherence pass.

Full discipline including cycle resolution worked examples: `references/dependency-graph-discipline.md`.

---

## 8. Revision-pass mode

When the skill re-activates after a specification revision (v1.x → v1.y) requires plan absorption, OR after P6-CK findings require partial re-author:

1. **Identify the revision trigger.** Specification revision (read spec change-note; identify revised contracts) OR P6-CK findings (read review document; identify findings to absorb).
2. **Identify affected units.** Use the coverage matrix to enumerate units citing revised spec contracts; use the dependency graph to identify units depending on affected units (one hop minimum, deeper as the trigger requires).
3. **Author the change-note.** Declare scope (which revisions or findings are being absorbed); sections preserved verbatim; sections revised; coverage matrix delta; dependency graph delta. Pattern modeled on spec v1.0 → v1.1 → v1.2 change-notes per `Project_Workflow_Revision_log.md` v1.6 and prd-author §2.7 precedent.
4. **Apply substantive revisions only at affected units.** Preserve verbatim all unaffected units — the change-note's preserved-verbatim list and the actual file must agree.
5. **Update the coverage matrix** at delta rows/columns. **Update the dependency graph** at delta nodes/edges. **Re-verify acyclic invariant** on the revised graph.
6. **Coherence pass on revised units + immediate dependency-graph neighbors.** Verify the four sub-disciplines on revised units; verify dependency graph remains acyclic; verify coverage matrix remains complete.

Status posture: `Status: Proposed` preserved until P6-CK clearance (analog to spec and PRD post-CK clearance patterns).

Full revision-pass session shape including multi-contract composition handling and three-class finding routing: `references/plan-authoring-protocol.md`.

---

## 9. Cross-mode citation + fidelity discipline

The workspace `CLAUDE.md` and `Project_Workflow_v1_8.md` §7.4 (fidelity-grammar) own citation and fidelity discipline. **Do not redefine these.** This skill inherits that discipline at every authoring step:

- Use `[HIGH]` / `[MODERATE]` / `[SPECULATIVE]` for confidence; do not introduce plan-specific tags.
- Cite spec contracts by **verified IDs and section numbers**; do not infer citation targets.
- A contract citation that cannot be verified by reading the spec is a fabrication and a Class-1 finding (per the §4.1 review-severity scale; see anti-patterns §10).

`Project_Workflow_v1_8.md` §7.4 use-latest-version body-citation-alignment clause: when a unit cites a spec contract, the citation must point to the **latest filed version** of the cited `design-substrate/` spec — not a prior version. At revision pass, citations to revised contracts are bumped to the new version. Byte-exact citation discipline per §7.4.2 (`CLAUDE.md` invariant I-1).

Trace-back is a citation discipline, not an attribution gesture: a section number is required.

---

## 10. Anti-patterns to avoid

| Anti-pattern | Why it fails |
|---|---|
| **Under-decomposition.** Units too big — multi-day effort, multi-axis scope, "implement the entire control plane" as one unit. | Fails §3.1 (single coherent change), §3.2 (single focused session). Re-atomize. |
| **Over-decomposition.** Units trivial — single-import additions, one-line edits, "create the directory" as a unit. | Fails §3.2 (over-fine). Coalesce into the consuming unit. |
| **Spec extension.** Unit introduces a commitment not in the specification — names a library not in the spec, declares a schema field not specified, adds a behavior absent from the contract. | Fails §4.4 (no spec extension). Plan implements; it does not extend. Surface the gap as a finding → operator-approved in-CLI spec fix tracked in a `Phase_7_Class_N_Tension` record (§2); do not invent the commitment. |
| **Implementation-detail leakage in the wrong direction.** Omitting implementation-grade detail where the contract requires it — vague "implement the sandbox tier composition" with no signature, file, or acceptance criterion. | Fails §4.4 (implementation-grade-detail). Plan exists to give the executor enough to execute; vagueness defeats the purpose. |
| **Cyclic dependencies.** Two or more units depend on each other directly or transitively. | Fails §4.3 (acyclic invariant). Cycle indicates an atomization defect — re-atomize. |
| **Missing dependencies.** A unit's acceptance criterion silently requires another unit's product, but the dependency is undeclared. | Fails §7 coverage discipline. Surface at coherence pass. |
| **Under-specified acceptance.** Acceptance criterion not testable ("the sandbox works correctly"). | Fails §4.4. Re-author at testable granularity. |
| **Coverage gaps.** Specification contracts not covered by any unit. | Fails §4.2 aggregate coverage. Surface as a finding; do not ship an incomplete plan. |
| **Risk/estimate annotations.** Plan annotates per-unit risk or per-unit effort estimates. | Operator pre-decision: plan is for the executor; resourcing artifacts are separate and out of scope. |
| **Trace-omission.** Authoring a unit without a spec contract citation. | Fails §4.2. The load-bearing trace-back failure — surface as a finding; do not ship. |
| **PR/commit/file-granularity pre-commitment.** Plan describes units at specific PR / commit / filesystem-path granularity rather than logical "single coherent change" granularity. | Stack-dependent; deferred to execution per §3.4. |
| **Confidence-schema redefinition.** `CLAUDE.md` framing owns the schema. | Use `[HIGH]` / `[MODERATE]` / `[SPECULATIVE]`; do not introduce plan-specific tags. |
| **Citation invention.** Citing spec contract IDs by inference; citing section numbers by inference. | Anti-fabrication discipline at plan granularity. Verify against the `design-substrate/` file before citing. |

---

## 11. Reference files

Load these when the body summary above is insufficient for the task at hand:

- `references/implementation-plan-template.md` — canonical plan section structure, per-unit template, well-formed example, malformed-example anti-patterns
- `references/spec-to-plan-decomposition.md` — per-contract procedure for surfacing atomic units, atomicity heuristics with worked examples, spec extension test, contract → unit ratio guidance
- `references/dependency-graph-discipline.md` — acyclic invariant verification, topological sort procedure, foundational-first ordering, cross-axis dependency callouts, transitive-dependency discipline, cycle examples with resolutions
- `references/plan-authoring-protocol.md` — full session shape for initial authoring and revision-pass mode, multi-contract composition handling, three-class finding taxonomy
