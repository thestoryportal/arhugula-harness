# Audit Scope — Remaining Build Surface

## Objective
Identify all remaining arcs, units, modules, contracts, workflows, interfaces, artifacts, and repo surfaces that are specified or implied by the canonical design substrate and governance artifacts but are not yet fully implemented, wired, tested, documented, or retired.

## Audit Questions
1. What is specified in `./design-substrate/` that has no implementation?
2. What exists in code but is incomplete, stubbed, placeholder-only, substitution-backed, or disconnected?
3. What repo-level governance, workflow, audit, roadmap, retirement, and archive surfaces are missing or partial?
4. What cross-axis composition (CXA) surfaces are implied but not yet built?
5. What MCP/server/boundary artifacts are required but absent or underdefined?
6. What tests, fixtures, schemas, examples, and operator runbooks are still missing?
7. What current substitutions are temporary and should resolve into concrete H_T primitives?

## Definition of “Remaining”
A unit counts as remaining if any of the following are true:
- absent
- stubbed
- TODO-only
- placeholder implementation
- substitution-backed
- undocumented contract
- untested
- unwired to calling surface
- specified in design but missing in workspace
- implied by naming, dependency, or workflow but not concretized

## Required Output
Claude must produce:
- a complete inventory of remaining units
- grouped by axis: core / IS / AS / CP / OD / CXA / repo governance / MCP boundary / docs / tests / ops
- for each item:
  - canonical source artifact
  - current repo evidence
  - gap type
  - build priority
  - dependency blockers
  - exact proposed artifact(s) to create or modify