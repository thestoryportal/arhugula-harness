# Repo Surface Map

> Filled during the remaining-build audit (HEAD `46012d5`, 2026-06-20). Corrects the seed stub, which omitted `harness-runtime` (the largest package, 136 src modules) + `tools/`, `deploy/`, `examples/`, `scaffolding/`. See `Remaining_Build_Audit_Report.md` §10 for full evidence.

## Root governance / process
- `CLAUDE.md` (workspace governance), `pyproject.toml` + `uv.lock` (uv workspace), `harness.toml` + `harness.toml.example`, `justfile`
- `Project_Roadmap_v1.md` (master roadmap §5 R-NNN catalog) + phase/session/governance docs (`Phase_7_*`, `Sub_Agent_Boundary_Specification_v1.md`, `AGENTS.md`)
- `.github/workflows/` (`ci.yml`, `x-al-3-guard.yml`, `dashboard-deploy.yml`); `.githooks/` (advisory pre-commit, opt-in)

## Workspace members (`src` / `tests` counts)
- `harness-core/` — 8 / 4 (shared types; cross-axis seam carriers)
- `harness-is/` — 20 / 21 (Information Substrate)
- `harness-as/` — 34 / 35 (Action Surface; curated `__all__`=191)
- `harness-cp/` — 72 / 97 (Control Plane; **empty `__init__` — RB-EXP-01**)
- `harness-od/` — 57 / 53 (Operational Discipline; **empty `__init__` — RB-EXP-01**)
- `harness-cxa/` — 2 / 3 (**near-stub: 1 real module; seam wiring lives in harness-runtime — RB-CXA-02**)
- `harness-runtime/` — **136 / 170** (bootstrap + lifecycle + dispatch + MCP host/server + api; the integration layer — **NOT** one of the 6 design axes, owns most forward arcs)

## MCP boundary
- Native H_T-as-MCP-server: `harness-runtime/src/harness_runtime/lifecycle/mcp_server.py` (U-RT-62, FastMCP `run_workflow`) + `mcp_host.py` / `mcp_client_host.py` (H_T-as-client)
- `.mcp.json` (registers the **retired** `harness-7a-scaffold` dev MCP → `scaffolding/mcp/` — RB-SUB-03 cleanup)

## Tooling / ops
- `tools/semantic_overlay/` (R-IF-112 overlay — spec↔code↔CXA↔substitution; `just overlay*`), `tools/arc_ledger.py`, `tools/substitution_ledger.py`, `tools/dashboard/`
- `deploy/` (`self-hosted-local/`, `managed-cloud/`), `examples/` (`minimal.toml`, `workflows/topology`), `scaffolding/mcp/`, `tests/` (root: persona-tier)

## Governance / historical / audit (`.harness/`)
- Live sources: `arc-ledger.yaml`, `substitutions.yaml`, `roadmap_status.md`, `beyond-mvp-capability-boundary-ledger.md`, `post-phase-8-forward-register.md`, `capability-completion-inventory-v1.md`, `clearance/` (85 markers), `archive/`
- **Audit outputs (this arc):** `audit/Remaining_Build_Audit_Report.md`, `audit/Remaining_Build_Register.csv` (48 rows), `audit/Closure_Gate_v1.md`

## Canonical design
- `design-substrate/` (247 .md; ADRs F1–F5/D1–D6, ADD, PRD, per-axis specs + plans, runtime spec, CXA, workflow — a **delta chain**: every version retained; heads = max-version per family)
