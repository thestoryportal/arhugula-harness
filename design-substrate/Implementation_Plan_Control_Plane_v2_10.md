# Implementation Plan — Control Plane (CP axis) — v2.10

**Status: Proposed.**

**Revision:** v2.10 — Phase 7 sub-phase 7c prerequisite pass, in-CLI revision. A **status-reconciliation delta** over v2.9: it carries no contract re-decomposition and no signature change. It (a) reconciles CP plan v2.9 §0.5's `RoleRoutingBinding` / `WorkloadRoutingOverride` Class 1 status against the operator resolution of 2026-05-16 (the plan text never caught up to the ruling), and (b) records one Class 3 citation-precision item at U-CP-46. Unit count unchanged (58). Predecessor: v2.9 (Pattern-D tail structured types).

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `CLAUDE.md` §1.3 authority chain; `phase-7-cross-axis-composition` SKILL §7. Companion: `Cross_Axis_Composition_Document_v2_2.md`.

**Entry authorization:** Phase 7 7c prerequisite pass (`.harness/cxa_7c_prerequisites_report.md`, Prereq 2), operator-authorized 2026-05-16.

---

## §0 Change-note

### §0.1 Trigger

Sub-phase 7c entry-gate orientation (Prereq 2) found a **plan-vs-landed-state divergence.** CP plan v2.9 §0.5 is titled "Two sub-records left Class 1 — `RoleRoutingBinding`, `WorkloadRoutingOverride`" and §2A-U-CP-04 declares `RoutingManifest` a **PARTIAL-LAND**. But the operator **resolved** the Class 1 on 2026-05-16 — after the v2.9 text was authored — and U-CP-04 was landed in full (`.harness/class_1_tension_role_routing_binding_underspec.md`, status RESOLVED). The v2.9 plan text never caught up. U-CP-04 is a CP→IS source unit (CXA v2.2 §2.3.2); the stale Class 1 text would otherwise read as a live blocker on those edges at 7c bucket wiring.

### §0.2 Reconciliation — `RoleRoutingBinding` / `WorkloadRoutingOverride` (supersedes v2.9 §0.5)

The operator was presented the design space and **ratified schema R-2 for `RoleRoutingBinding` and W-2 for `WorkloadRoutingOverride`** (2026-05-16) — path 2 of the v2.9 §0.5 routing (operator-ratified factor-out). The operator ruling supplies the design-authority decision the plan/spec lacked; the two records are no longer an X-AL-3 risk because the field set is operator-committed, not implementer-guessed.

**R-2 — `RoleRoutingBinding`** (`harness_cp/routing_manifest_residence.py`):
- `preferred_model_binding : ModelBinding` (U-CP-00c)
- `layer_budget_overrides : Mapping[RoutingLayer, int]` (U-CP-06)
- `fallback_chain_ref : str | None` (U-CP-09 chain name)

**W-2 — `WorkloadRoutingOverride`** (same module):
- `engine_class_override : EngineClass | None` (U-CP-15)
- `sandbox_tier_override : SandboxTier | None` (AS-owned; sanctioned CP→AS edge)
- `model_binding_override : ModelBinding | None` (U-CP-00c)

Both are frozen `extra="forbid"` Pydantic records composing only landed types. **U-CP-04 `RoutingManifest` is upgraded PARTIAL-LAND → FULL-LAND.** pyright strict 0 errors; CP suite 465 tests green at the landing. No design surface introduced beyond the operator-approved field sets.

### §0.3 Status of v2.9 §0.5 and §2A-U-CP-04 acceptance criterion 5

CP plan v2.9 §0.5 (and its filed Class 1 record) and §2A-U-CP-04 acceptance criterion 5 ("`RoutingManifest` partial-land") are **superseded** by §0.2. The v2.9 §0.5 reasoning remains accurate as the *pre-resolution* record (why the two records were Class 1 absent an operator ruling); it is retained as historical context. The operative status is: resolved, full-land. The Class 1 record `.harness/class_1_tension_role_routing_binding_underspec.md` is stamped RESOLVED.

### §0.4 Class 3 citation-precision item — U-CP-46 Implements line (C3-CXA-7c-3)

Surfaced at the 7c Prereq 1 carrier-resolution pass. U-CP-46's title declares "7 `audit.*` attributes + per-persona-tier emission table + **4 `hitl.*` span attribute schemas**"; its `Implements:` line cites `[C-CP-20 §20.4, §20.5]`. CP spec C-CP-20 **§20.6** ("HITL-event span schema, composition with §20.4") is the contract anchor the OD axis cites for the `hitl.*` cross-axis edge (CXA v2.2 §2.3.6, U-OD-23 → U-CP-46), and the CP spec D6-ingestion namespace table attributes `hitl.*` to C-CP-20 §20.6. U-CP-46 **materially carries §20.6** (it declares the 4 `hitl.*` span attribute schemas). The `Implements:` line should read **`[C-CP-20 §20.4, §20.5, §20.6]`** — a citation-precision correction, no body change. The carrier of C-CP-20 §20.6 is unambiguously U-CP-46.

This is Class 3 (informational, non-blocking). It does not block 7c bucket wiring — the OD→CP `hitl.*` edge resolves to U-CP-46 regardless. Logged here for the catch; no v2.10 body change beyond this note.

### §0.5 Scope + sections preserved verbatim from v2.9

Revised: §0 (this change-note added); §0.5 status (superseded per §0.3); §2A-U-CP-04 acceptance criterion 5 status (superseded per §0.3); U-CP-46 `Implements:` line citation per §0.4. **No signature, no acceptance-criterion logic, no contract decomposition, no dependency edge changes.** Every other §0–§11 section is preserved verbatim from v2.9.

### §0.6 Dependency-graph + coverage delta

Within-axis CP DAG: unchanged. Coverage matrix: unchanged at the contract→unit level; §0.4 makes U-CP-46's §20.6 coverage explicit (it was already materially covered). No coverage mark gained or lost.

### §0.7 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_10.md` |
| Status | Proposed — Phase 7 7c prerequisite pass |
| Predecessor | `Implementation_Plan_Control_Plane_v2_9.md` (preserved verbatim except §0, §0.5 status, §2A-U-CP-04 acc 5 status, U-CP-46 `Implements:` line) |
| Companion | `Cross_Axis_Composition_Document_v2_2.md`; `.harness/class_1_tension_role_routing_binding_underspec.md` (RESOLVED) |
| Authored at | Phase 7 sub-phase 7c, 2026-05-16 (in-CLI) |
