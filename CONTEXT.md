# CONTEXT.md — workspace task router

Router only. Every rule traces to root `CLAUDE.md` (§ cited inline); read it for the rest.

## Route by posture (§11.1–§11.2)

| Editing | Posture | Read next |
|---|---|---|
| `design-substrate/**`, `.harness/**` back-flow docs, `.harness/clearance/**` **markers** | **Design-phase** | §10; canonical = ADRs / ADD / PRD / Workflow doc (§1.3) |
| `harness-{is,as,cp,od}/**` | **Phase-7 impl** | that axis's `CLAUDE.md` (§2.5); canonical = its spec + plan (§2.3/§2.4) |
| `harness-core/**` | **Phase-7 impl** | §2.5 (shared types); canonical = `Implementation_Plan_Harness_Core_v1_3.md` (§2.4) |
| `harness-runtime/**` | **Phase-7 impl** | canonical = the Runtime spec + plan heads (§2.3/§2.4) |
| `harness-cxa/**` | **Phase-7 impl** | §2.5 (seam instantiation); canonical = the CXA head (§2.4) + §4.3 |
| root `CLAUDE.md` / `CONTEXT.md` / `AGENTS.md`, `.github/`, `.claude/`, `.harness/` tooling **incl. `clearance/README.md`**, `pyproject.toml` | **Mode-agnostic ops** | §11.2 — unconstrained by X-AL-3 |

`harness-{core,runtime,cxa}` have no local `CLAUDE.md`. An explicit operator declaration overrides
the table (§11.3); ambiguous intent → ask, never infer (§11.6).

## Mixed edits

`design-substrate/**` **and** `harness-*/src/**` in one session → **halt + ask** (§11.2), unless it
is a bundled-absorption arc carrying back-flow — fork doc, architect recommendation, retirement
filing, or clearance marker (§11.4, §4.5). Phase-7 never edits `design-substrate/**` (§4.4, X-AL-3).

## Pointers

- Next action + drift audit — `.harness/roadmap_status.md` (§12)
- Artifact heads §2.1–§2.4; their lineage — `.harness/claude-artifact-pointers.md` (§2)
- Sub-agent boundary (H_E ≠ H_T topology) — `Sub_Agent_Boundary_Specification_v1.md` (§5)
- Fork detection + back-flow routing (§4.3) · review + orchestration disciplines (§13, §14)
