# Phase 7 — Class 1 Tension Record 003 — `WorkloadClass` type undeclared by any plan unit

*Plan-gap tension record. Authored at tension detection during Phase 7 sub-phase
7b atomic-unit execution. Class 1 — halt-execution; the CP plan references a
foundational type that no atomic unit is assigned to declare. Per the in-CLI fix
regime (back-flow deprecated 2026-05-15), the fix is applied in Claude Code CLI
once the operator authorizes a resolution.*

---

## §1 Detection state

| Field | Value |
|---|---|
| Tension class | **Class 1** (halt-execution; plan gap — missing declaring unit) |
| Detected at | Phase 7 sub-phase 7b, atomic unit **U-CP-22** (TopologyPattern enum + admissibility predicate) |
| Detected | 2026-05-15 |
| Halt point | U-CP-22 implementation — surfaced before code execution |
| Status | **OPEN** — U-CP-22 halted; operator authorized landing unaffected siblings (U-OD-01, U-OD-04) first |

## §2 Defect

U-CP-22's `is_admissible` signature is `is_admissible(pattern: TopologyPattern, workload: WorkloadClass) -> bool` (`Implementation_Plan_Control_Plane_v2_1.md` §2 U-CP-22, line 1200). It references the type **`WorkloadClass`**.

`WorkloadClass` is used as a type across **~10 CP-plan unit signatures** — U-CP-13 (`WorkflowManifestEntry.workload_class`, line 328), U-CP-05 (`per_workload_overrides`, line 379), U-CP-06 (line 458), U-CP-09 (`compose_fallback_chain`, line 621), U-CP-17 (line 788), U-CP-21 (line 973), U-CP-22 (line 1200), U-CP-23 (`PerWorkloadClassTopologyCommitment`, line 1228), and others.

**No atomic unit in the CP plan declares `WorkloadClass`.** A grep across `Implementation_Plan_Control_Plane_v2_1.md` for `enum WorkloadClass` / `Declare ... WorkloadClass` returns zero hits. The type is used pervasively but never declared by a carrier unit.

U-CP-22 is `Depends on: (none)` / `Inputs: None` — so even if a declaring unit existed, U-CP-22 does not depend on it; the signature would be unsatisfiable from U-CP-22's declared dependency set alone.

## §3 Why Class 1 (halt-execution)

The CP plan is internally incomplete: it consumes a foundational type at ~10 unit signatures with no unit assigned to produce it. This is a Phase 6 plan defect (a missing atomic unit), not a determinate fix. Resolution requires an operator decision on **which unit declares `WorkloadClass` and where it resides**, then a plan revision-pass. Silently inventing the type at U-CP-22 would be a silent H_T design extension (`CLAUDE.md` I-2 / X-AL-3) and would mis-home a cross-axis foundational type inside a single axis package.

## §4 Substrate — the value set is persona-canonical

The *values* are not in doubt; only the declaring unit is missing. The 4 workload classes are canonical per **Persona §3.1** and are enumerated verbatim at **C-CP-07 §7.3**: `software-engineering | content-creation | pipeline-automation | research`, with an `extension-class` flag per Persona §3.2 (C-CP-07 §7.3 "extension-class per Persona §3.2"). `WorkloadClass` is a closed foundational enum; the gap is purely structural (no carrier unit).

## §5 Proposed resolution (operator decision required)

Recommended direction (pending operator confirmation of the resolution mechanics):
1. Assign a new foundational atomic unit (suggest **U-CP-00** or a `harness-core` shared-types unit) to declare `WorkloadClass` as a closed enum of the 4 persona-canonical values, residing in **`harness-core`** (cross-axis foundational — IS / AS / CP / OD all reference workload classes).
2. Plan revision-pass: add the declaring unit; add `Depends on: [<new unit>]` to U-CP-22 and the ~10 other consuming units; bump the CP plan version.
3. Resume U-CP-22 implementation once `WorkloadClass` is landed.

This record does not apply a fix — the operator selects the resolution.

## §6 Block-clearing decision

| Field | Value |
|---|---|
| Decision | **OPEN.** U-CP-22 implementation halted. Operator authorized (2026-05-15) landing the unaffected operational-minimum siblings first. |
| Unblocked siblings | U-OD-01 (C-OD-01) and U-OD-04 (C-OD-04) do not reference `WorkloadClass` — independently implementable. |

## §7 Sibling assessment

| Unit | Status |
|---|---|
| U-OD-01 (9-cell observability matrix) | ✅ Clean. `Depends on: []`; no `WorkloadClass` reference. |
| U-OD-04 (OTel GenAI semconv base) | ✅ Clean. `Depends on: []`; no `WorkloadClass` reference. |
| U-CP-15 (EngineClass enum) | ✅ Already landed 2026-05-15 (commits `a267f09` / `a42b4f8`). |
