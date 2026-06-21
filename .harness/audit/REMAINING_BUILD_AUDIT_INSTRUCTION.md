# Remaining Build Audit Instruction

Perform a repository-wide audit to surface all remaining arcs/units that need to be built.

## Canonical Sources
Audit against:
- `./CLAUDE.md`
- `./Project_Roadmap_v1.md`
- `./Phase_7_Workspace_Bootstrap_Runbook_v1.md`
- `./Phase_7_Session_1_Entry_Directive_v1.md`
- `./Sub_Agent_Boundary_Specification_v1.md`
- `./Phase_7_Class_3_Tension_001_Git_Tier_Sub_Role_Count.md`
- `./design-substrate/` (all ADRs, ADD, PRD, per-axis specs, per-axis plans, workflow, meta-architecture)
- `./pyproject.toml`
- `./uv.lock`
- `./harness.toml.example`
- all workspace member packages
- `./.harness/` including roadmap, fork, retirement, archive, historical surfaces

## Audit Method
Use all of these passes:

### Pass 1 — Declared Structure
Identify all declared packages, modules, commands, workflows, contracts, schemas, agents, boundaries, MCP/server surfaces, composition surfaces, and governance artifacts.

### Pass 2 — Implemented Structure
Inspect actual files, package contents, exports, tests, docs, examples, configs, and integration points.

### Pass 3 — Spec-to-Implementation Diff
Compare canonical design/design-substrate claims against implementation reality.

### Pass 4 — Boundary/Substitution Diff
Find every place where temporary substitution, CLI delegation, manual operator step, placeholder, or bounded external dependency stands in for a target primitive.

### Pass 5 — Cross-Axis Arc Diff
Find missing connections between packages/axes:
- core ↔ axes
- axis ↔ axis
- axes ↔ CXA
- harness ↔ MCP boundary
- governance/docs ↔ executable surfaces

### Pass 6 — Lifecycle Completeness
For every unit found, check whether it has:
- implementation
- type/interface contract
- config surface
- tests
- docs
- example/fixture
- wiring/invocation path
- observability/reporting
- retirement or archive note if deprecated

## Output Rules
Be exhaustive, not polite.
Do not stop at obvious missing files.
Surface implied missing units as well as explicit missing units.

## Required Deliverables
Produce:

1. `Remaining_Build_Audit_Report.md`
2. `Remaining_Build_Register.csv`

## Report Sections
- Executive summary
- Audit coverage
- Method
- Missing units by domain
- Missing arcs by dependency edge
- Temporary substitutions that must be retired
- Repo governance/documentation gaps
- High-risk hidden gaps
- Recommended build sequence
- Appendix: evidence by file/path

## Register Columns
- ID
- Domain
- Axis
- Unit name
- Unit type
- Canonical source
- Repo evidence
- Gap classification
- Severity
- Build priority
- Depends on
- Proposed artifact path
- Proposed action
- Notes