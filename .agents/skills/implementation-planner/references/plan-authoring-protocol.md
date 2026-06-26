# Plan Authoring Protocol Reference

This reference is loaded when authoring requires the full session shape for initial authoring or revision-pass mode, multi-contract composition handling, or the three-class finding taxonomy.

---

## 1. Initial authoring session (Phase 6 entry)

Procedure for a session where no prior plan is filed and the specification (post-P5-CK) is the substrate:

1.1 **Verify inputs present.** Specification (axis specs + top-level composition; post-P5-CK clearance), PRD, ADD, persona document. Stand down if any missing.

1.2 **Announce the shape decision** per SKILL.md §6. Justify shape choice from the specification or dependency-graph structure. Operator MAY accept or reject; default proceeds with announced shape if no rejection. Record the decision at plan front-matter.

1.3 **Inventory contracts** from specification. Build axis × contract matrix. Tag each contract by primary axis. Cross-axis composition contracts (those at the top-level composition document) are tagged separately for §5 cross-cutting handling.

1.4 **Per contract, enumerate implementation surfaces** per `references/spec-to-plan-decomposition.md` procedure. Surfaces commonly include: schemas to author; functions to author; integrations to build; tests to author; configuration/manifest entries; cross-axis composition points.

1.5 **Atomize surfaces into units** per SKILL.md §3 atomicity criteria. Apply atomicity heuristics from `references/spec-to-plan-decomposition.md` §2 — schema → foundational; composition formula → N+1 units; taxonomy → 1 foundational + per-class consumers; sub-discipline → acceptance criterion of consuming unit; cross-contract composition → dependency edge OR cross-cutting unit.

1.6 **Declare dependencies** per `references/dependency-graph-discipline.md`. Direct dependencies only; cross-axis dependencies flagged with axis annotation; foundational units declare `(none)`.

1.7 **Topological sort.** Apply the leaf-stripping algorithm. Verify acyclic. If cyclic, re-atomize per §6 cycle-resolution patterns of `references/dependency-graph-discipline.md`.

1.8 **Author acceptance criteria** per `references/implementation-plan-template.md` §3. Functional acceptance (testable when unit is complete, given dependencies present) + integration acceptance (where applicable; testable when unit and dependencies are wired together).

1.9 **Build §4 coverage matrix.** Verify every contract has at least one covering unit (no empty rows). Verify every unit cites at least one contract (no empty columns). Surface gaps as findings.

1.10 **Coherence pass** per SKILL.md §5 step 9. Verify the four sub-disciplines on every unit; verify dependency graph acyclic; verify coverage matrix complete; verify no spec extension at any unit. Document unresolved findings at plan §6 open items OR as Class 2/3 findings routed to operator.

1.11 **File `Implementation_Plan_v1.0.md`** with `Status: Proposed`. Surface any findings to operator for routing.

---

## 2. Revision-pass session

Procedure for a session where plan vN is filed and a trigger (spec revision OR P6-CK findings) requires absorption:

2.1 **Verify inputs.** Current plan vN; revision trigger (spec change-note for spec-revision-driven absorption, OR P6-CK adversarial review document for finding-driven absorption).

2.2 **Identify affected units** via coverage matrix (units citing revised contracts) + dependency graph (units depending on affected units; one hop minimum, deeper as the revision shape requires).

2.3 **Author the change-note** at the head of `Implementation_Plan_vN+1.md`. Required fields:

| Field | Content |
|---|---|
| Scope of revision | Which spec contracts revised (with from-version → to-version) OR which P6-CK findings absorbed (with finding IDs) |
| Sections preserved verbatim | Plan unit IDs whose content is unchanged |
| Sections revised | Plan unit IDs whose content is changed, each with one-line rationale |
| Coverage matrix delta | Row additions/removals (contract additions/revisions); column additions/removals (unit additions/revisions); cell changes |
| Dependency graph delta | Node additions/removals (unit additions/removals); edge additions/removals (dependency changes); topological-sort impact |

Pattern modeled on spec v1.0 → v1.1 → v1.2 change-notes per `Project_Workflow_Revision_log.md` v1.6 and prd-author §2.7 revision-pass precedent.

2.4 **Apply substantive revisions only at affected units.** Preserve verbatim all unaffected units — the change-note's preserved-verbatim list and the actual file must agree. Diff-checkable.

2.5 **Update §4 coverage matrix** at delta rows/columns. **Update §3 dependency graph** at delta nodes/edges. **Re-verify acyclic invariant** via the topological-sort leaf-stripping algorithm.

2.6 **Coherence pass on revised units + immediate dependency-graph neighbors.** "Immediate neighbors" = units that depend on a revised unit OR that a revised unit depends on. Coherence-pass scope:
- Four sub-disciplines on revised units (atomicity, spec-traceability, dependency-awareness, implementation-grade-detail)
- Acyclic invariant on revised graph
- Coverage matrix completeness (no new empty rows or columns)
- No spec extension introduced at revised units

2.7 **File `Implementation_Plan_vN+1.md`** with `Status: Proposed` (unchanged status until P6-CK clearance, per spec/PRD post-CK clearance patterns).

---

## 3. Multi-contract composition handling

When a single unit covers multiple closely-coupled contracts (rare; usually for cross-cutting integration consolidated at plan §5):

3.1 Cite **all governing contracts** in the unit's `Spec linkage` field. Order citations by primacy: the contract whose surface most directly anchors the unit comes first; contracts that modify or constrain the unit follow.

3.2 Document at plan §5 (cross-cutting integration units) with a one-line rationale for the consolidation. Acceptable consolidation rationales:

- "Atomizing each composition pair produces N trivial wiring units that fail §3.2 (over-decomposition); consolidating to a single wiring point is one coherent change."
- "Contracts X and Y co-declare a composition surface; the surface is one rollback boundary at execution time."

3.3 Do NOT consolidate to avoid declaring cross-axis dependencies. Consolidation is not a dependency-management shortcut. If two contracts in different axes have a composition surface, the surface either:
- Lives in one axis with a cross-axis dependency declared to the other (most common), OR
- Lives at plan §5 as a cross-cutting unit (rare; reserved for surfaces that span ≥3 axes or that one axis cannot legibly host).

3.4 Coverage matrix discipline. A multi-contract unit marks all its governing contracts as covered. The matrix row count is contracts, not (contract × axis); a contract whose surface composes across axes still has one row, covered by the consolidating unit + possibly per-axis consumer units.

---

## 4. Three-class finding taxonomy

The planner surfaces findings at coherence pass. Three classes, mirroring the prd-author skill's class taxonomy:

### 4.1 Plan Class 1 (Minor)

Defects fixable inline during the coherence pass without escalation:
- Citation format drift (e.g., `C-AS-02` without section number → add `§2.1`)
- Unit-ID typos (e.g., U-AS-3 referenced as U-AS-03)
- Minor wording inconsistencies
- Missing transitive callouts that do not affect topological sort
- Status block field omissions

Resolution: fix inline; do not escalate to operator.

### 4.2 Plan Class 2 (Moderate)

Defects where the unit fails one or more of the four sub-disciplines but the specification is sound:
- Unit fails §3 atomicity criteria (under- or over-decomposition; missing rollback boundary)
- Unit declares incomplete dependencies (acceptance criterion requires undeclared products)
- Unit fails implementation-grade detail (no signatures; no testable acceptance)
- Coverage matrix has an empty unit column (unit cites no contract)
- Dependency graph has a cycle traceable to atomization defect (resolve per `references/dependency-graph-discipline.md` §6)

Resolution: surface the finding; route via operator decision (revise unit / coalesce / split / re-atomize). Author proposes a resolution path with each finding.

### 4.3 Plan Class 3 (Severe)

Defects where the specification itself has a gap or contradiction surfaced during atomization. These are **Phase 5 regressions**, not Phase 6 authoring problems:
- A contract's deferred-to-implementation list omits a surface the unit needs to commit to (but the spec is silent on whether the surface is committed)
- Two contracts contradict at a composition site (the unit cannot satisfy both)
- A coverage gap that is unfixable without spec extension (i.e., no unit can cover the contract without committing to something the spec does not commit to)
- A unit cannot be atomized to satisfy §3 criteria without a spec commitment the spec does not make

Resolution: back-flow to Phase 5. The plan filing is blocked on a Phase 5 revision absorbing the finding. The planner does NOT decide; the planner surfaces.

This is the load-bearing back-flow discipline. A Class 3 finding shipped without back-flow is a load-bearing failure of the role — re-author rather than patch.

---

## 5. Surfacing findings in the artifact

Findings are surfaced in two places:

5.1 **Plan §6 Open items.** Class 1 inline-fixed findings are not surfaced (resolved inline). Class 2 findings surface here if the operator has approved a resolution that defers (e.g., "U-AS-7 carry-forward: atomicity boundary unclear at composition site; revisit at next revision pass"). Class 3 findings surface here only when the operator has approved a deferred back-flow (rare; usually back-flow is immediate).

5.2 **Coherence-pass finding manifest** (separate artifact filed alongside the plan when findings exist). Required fields per finding:

| Field | Content |
|---|---|
| Finding ID | `F-PLAN-vN-NNN` |
| Class | Class 1 / 2 / 3 |
| Affected units | Unit IDs |
| Affected contracts | Contract IDs |
| Description | One paragraph; what the defect is, how it was surfaced |
| Proposed resolution | One paragraph; what action the author recommends |
| Status | Open / In progress / Resolved |

The manifest gives P6-CK reviewers visibility into surfaced defects without requiring them to re-read the entire plan to find them.

---

## 6. Coherence pass checklist (compact form)

For each unit, verify:

| # | Check | Pass condition |
|---|---|---|
| 6.1 | Atomicity §3.1 | Single coherent change; not a multi-axis bucket |
| 6.2 | Atomicity §3.2 | Single focused session; not multi-week, not single-line |
| 6.3 | Atomicity §3.3 | Independently testable given dependencies |
| 6.4 | Atomicity §3.4 | Coherent rollback boundary at logical level |
| 6.5 | Spec-traceability | At least one contract cited by ID + section |
| 6.6 | Spec-traceability | Cited contract is the latest filed version |
| 6.7 | Dependency-awareness | Direct dependencies declared; cross-axis flagged |
| 6.8 | Dependency-awareness | Acceptance-criterion-required products are all declared as dependencies |
| 6.9 | Implementation-grade detail | Surface, signature, acceptance criterion present |
| 6.10 | Implementation-grade detail | No spec extension (no library/framework/protocol not in spec; no schema fields beyond contract; no acceptance behavior beyond contract) |
| 6.11 | Anti-pattern §10 | No effort/risk annotation; no PR/commit/file-granularity; no confidence-schema redefinition |

For the aggregate plan, verify:

| # | Check | Pass condition |
|---|---|---|
| 6.12 | Coverage matrix | Every contract row marked; every unit column marked |
| 6.13 | Dependency graph | Acyclic (topological sort exists) |
| 6.14 | Cross-axis dependencies | All flagged with axis annotation |
| 6.15 | Shape consistency | Plan structure matches declared shape decision; no shape drift mid-plan |
| 6.16 | Citation freshness | All citations point to latest filed contract versions |
