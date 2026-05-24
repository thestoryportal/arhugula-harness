# Implementation Plan — Control Plane v2.18

## Change-note (v2.17 → v2.18)

**Scope of revision.** Class 1 fork resolution Path A absorption companion to CP spec v1.11 → v1.12 — per `.harness/class_1_fork_step_execution_context_workflow_id_field_absence.md` ratification 2026-05-24. The U-CP-56 plan-body absorbs the v1.12 §25.2.1 NEW 9th field `workflow_id: str` at the `StepExecutionContext` Pydantic BaseModel. AC + Files + Signatures lines amended at U-CP-56 to reflect the 9-field shape (was 8 at v1.6 baseline).

**v2.17 substantive content preserved verbatim.** All v2.17 content (U-CP-00 through U-CP-72; the v2.17 Path γ rename absorptions at U-CP-62/63/64; all clusters; DAG topology; coverage matrix) preserved unchanged outside the single U-CP-56 amendment site enumerated below. The v2.16 + v2.15 + ... + v2 chain all preserved.

**Source of fix.** Cost-axis production callsite migration arc opening per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` + advisor pre-implementation gate per `[[advisor-before-substantive-work-for-cross-axis-blockers]]`:
- OD spec v1.10 §C-OD-26.6.1 step 2 cites `step_context.workflow_id` as the source for the canonical `cost:<workflow_id>:<step_action_id>` audit action_id pattern at the `CostRecordAuditPayload` typed carrier.
- Empirical inventory at HEAD `c413d40`: `StepExecutionContext` per `harness-cp/src/harness_cp/workflow_driver_types.py:119-183` has 8 fields; `workflow_id` is NOT among them — silent absorption of a CP-spec extension at OD-spec v1.10 §C-OD-26.6.1 Sub-arc B publication arc per X-AL-3.
- Path A (CP-spec amendment) operator-ratified at AskUserQuestion 2026-05-24.
- Companion CP spec v1.12 §25.2.1 9th-field addition published this session (commit `8614c9f`).

**One amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **U-CP-56 — StepExecutionContext 9th field addition** | Plan body Pydantic BaseModel field-list amended to add 9th field `workflow_id: str` per CP spec v1.12 §25.2.1 NEW. AC #1 (carrier authoring) text update to cite 9-field shape (was 8); AC #6 (full-line driver integration per v2.12) text update to cite driver composition site fill from `manifest_entry.workflow_id` (already in driver scope at `workflow_driver.py:597-608`). Files line preserved verbatim (`harness-cp/src/harness_cp/workflow_driver_types.py` already enumerated). Signatures line amended to reflect the 9-field record. Within-axis dependency edges preserved verbatim (U-CP-56 dependencies at U-CP-13 + U-CP-14 + U-CP-10 + U-CP-15 + U-CP-01 + U-IS-07 + U-IS-10 + U-IS-11 + U-RT-44 all unchanged — the 9th field is an additive value-pass-through, no new cross-axis edge). | CP spec v1.12 §25.2.1 NEW 9th field |

**Plan shape preserved.** v2.17's 73-unit axis-led structure preserved verbatim. No new units; no DAG topology change (U-CP-56 stays at its existing topological level; the 9th-field absorption is intra-unit, no new edge); no coverage matrix change.

**Status posture.** Proposed (v2.17) → **Proposed (v2.18)**. v2.18 is a fidelity-bookkeeping patch — single-field addition absorption at U-CP-56 plan body. No v2.17 unit re-decomposition; no contract removal; no signature change beyond the additive field; no DAG change.

**Downstream absorption owed (post-v2.18).**
(a) Workspace `CLAUDE.md` §2.4 CP plan row version bump (v2.17 → v2.18).
(b) `harness-cp/src/harness_cp/workflow_driver_types.py` — Pydantic BaseModel field addition (`workflow_id: str` after `step_index: int` OR ordering per Pydantic v2 model_config conventions); existing 8 fields preserved byte-exact.
(c) `harness-cp/src/harness_cp/workflow_driver.py:597-608` — driver composition site fill of `workflow_id=manifest_entry.workflow_id` at the `StepExecutionContext(...)` construction call.
(d) `harness-runtime/src/harness_runtime/lifecycle/cost_attribution_llm_dispatch.py` — companion impl: `attribute_llm_dispatch_cost` signature widening (kwargs `workflow_id: str` + `parent_action_id: str`); caller at `llm_dispatch.py:701` passes from `step_context.workflow_id` + `step_context.parent_action_id`; replace local `_project_and_convert_audit_entry` helper with import of canonical `harness_od.cost_record_audit_writer._project_cost_record_to_audit_payload`.
(e) Tests: driver-side `StepExecutionContext` field-population test + harness-runtime typed-path production callsite emission test.
(f) `.harness/class_1_fork_step_execution_context_workflow_id_field_absence.md` §8 ratification footer documenting Path A applied at this v1.12 + v2.18 + impl arc.

**Adjacent defects surfaced (not patched per FM-2 no-extension discipline).**

(i) **§25-renumbering drift across CP spec v1.10.** CP spec v1.10 introduced NEW §25 C-CP-25 ValidatorFramework, which collides with the v1.6 NEW §25 C-CP-25 WorkflowDriver section number. The v1.6 §25.2.1 StepExecutionContext authoring site lives at the v1.6 spec file canonically; v1.7/v1.8/v1.9 preserved verbatim by reference; v1.10 introduced the renumbering ambiguity. The v1.12 amendment (this session) cites `§25.2.1` per the v1.6 canonical authoring site — the cite is operatively correct (StepExecutionContext is defined at v1.6 §25.2.1 and that authoring site is preserved through the spec chain) but the §25 renumbering drift at v1.10 surfaces a section-numbering hygiene issue at the cross-version interpretation surface. Surfaced; routing to a future CP spec hygiene revision arc; non-blocking at v1.12 + v2.18 publication.

(ii) **U-CP-56 acceptance criterion enumeration shape.** U-CP-56 acceptance criteria (per CP plan v2.11 + v2.12 absorption chain) enumerate the 8-field StepExecutionContext at AC #1 — the v2.18 amendment extends AC #1 to cite 9 fields. The remaining ACs (#2 through #6) preserved verbatim — the 9th field absorption is an additive value-pass-through, no AC re-decomposition required.

---

## §1 — U-CP-56 plan-body amendment (v2.18)

The U-CP-56 declaration last canonically authored at CP plan v2.12 (per `harness-cp/src/harness_cp/workflow_driver.py:114` "Introduced at CP plan v2.12 to materialize U-CP-56 AC #6 (full driver integration)") is amended at v2.18 as follows. Original content preserved verbatim except for the field-list extension + AC #1 + AC #6 text updates.

### U-CP-56 — Workflow execution driver core + StepExecutionContext schema (v2.18 amendment — 9th field `workflow_id` addition per CP spec v1.12 §25.2.1)

**Plan-body amendment delta.**

- **Carrier shape (StepExecutionContext Pydantic BaseModel).** v2.17 enumerated 8 fields: `parent_action_id` / `parent_gate_level` / `parent_sandbox_tier` / `parent_actor` / `parent_entry_hash` / `parent_idempotency_key` / `tenant_id` / `step_index`. v2.18 extends to 9 fields by adding `workflow_id: str` at the carrier per CP spec v1.12 §25.2.1 amendment. Field semantics: parent workflow identifier sourced from `manifest_entry.workflow_id` at the driver §25.3.3.4 composition site. Required (NOT Optional). Discrete typed surface for consumer dispatchers + OD-axis cost-attribution audit-write wiring per OD spec v1.10 §C-OD-26.6.1 step 2 cite.

- **AC #1 text update (carrier authoring).** v2.17 AC #1 text "Authors `StepExecutionContext` Pydantic v2 BaseModel with 8 fields per CP spec v1.6 §25.2.1" updates to "Authors `StepExecutionContext` Pydantic v2 BaseModel with 9 fields per CP spec v1.12 §25.2.1 (the v1.6 8-field shape extended at v1.12 with NEW 9th field `workflow_id: str`)". Field-set verification at acceptance: all 9 fields present; type / cardinality / semantics per spec §25.2.1; `extra="forbid"` Pydantic model_config preserved; `frozen=True` preserved.

- **AC #6 text update (full driver integration).** v2.17 AC #6 text "Driver composes `StepExecutionContext` at the §25.3.3.4 dispatch site from driver-tracked run-level state (4 fields composed deterministically: `parent_action_id`, `parent_actor`, `parent_idempotency_key`, `step_index`) + 4 MVP-default-bounded fields" updates to "Driver composes `StepExecutionContext` at the §25.3.3.4 dispatch site from driver-tracked run-level state (**5 fields** composed deterministically: `workflow_id`, `parent_action_id`, `parent_actor`, `parent_idempotency_key`, `step_index`) + 4 MVP-default-bounded fields (`parent_gate_level`, `parent_sandbox_tier`, `parent_entry_hash`, `tenant_id`) per CP spec v1.12 §25.2.1 composition discipline amendment. `workflow_id` value sourced from `manifest_entry.workflow_id` (already in driver scope at the existing composition site `workflow_driver.py:597-608` where `parent_action_id` is composed via string interpolation from the same value)." Verification at acceptance: `workflow_id` field populated at every driver composition; field value byte-exact equal to `manifest_entry.workflow_id`.

- **Signatures line update.** v2.17 Signatures line "Signatures: `class StepExecutionContext(BaseModel)` 8-field" updates to "Signatures: `class StepExecutionContext(BaseModel)` 9-field per CP spec v1.12 §25.2.1".

- **Files line preserved verbatim.** `harness-cp/src/harness_cp/workflow_driver_types.py` already enumerated at U-CP-56 Files line (canonical home of StepExecutionContext type) — preserved verbatim. `harness-cp/src/harness_cp/workflow_driver.py` (driver composition site) already enumerated at U-CP-56 Files line — preserved verbatim.

- **Depends-on edges preserved verbatim.** U-CP-56 cross-axis dependencies (per CP plan v2.11 §1 absorption: U-CP-13 + U-CP-14 + U-CP-10 + U-CP-15 + U-CP-01 + U-IS-07 + U-IS-10 + U-IS-11 + U-RT-44) all preserved. The 9th-field absorption is an additive value-pass-through; no new cross-axis edge introduced.

- **Acceptance-criteria coverage matrix preserved verbatim.** v2.17 AC #2 (step iteration loop) + #3 (drain protocol) + #4 (lifecycle event emission filter) + #5 (RunResult terminal type) all preserved unchanged.

**Within-axis DAG impact.** ZERO. U-CP-56 stays at its existing topological level; within-axis dependents (U-CP-57 drain composition + U-CP-58/59/60/61 validator framework cluster + downstream consumers) absorb the 9th-field-bearing carrier at Protocol-conformance-additive shape; no edge added; no edge removed.

**Cross-axis DAG impact.** ZERO. The OD spec v1.10 §C-OD-26.6.1 step 2 cite to `step_context.workflow_id` was already implicit-forward-cite at OD spec v1.10 publication (commit `0919a9b`); the v1.12 + v2.18 amendment RESOLVES the cite without introducing a new cross-axis edge — the CP→OD audit-write seam at CXA v2.9 §2.3.7 row 8 already encompasses the cost-attribution wiring; this amendment makes the source-field provenance byte-exact resolvable.

---

## §2 — Preservation guarantees

| Element | Disposition |
|---|---|
| All v2.17 units (U-CP-00 through U-CP-72) | Preserved verbatim outside U-CP-56 plan-body amendment site |
| v2.17 Path γ absorptions at U-CP-62/63/64 (`WorkflowPauseReason` rename + AC #4 strikes + Files-column note amendments) | Preserved verbatim |
| v2.16 path-β `ValidatorFailClass` → `ValidatorRetryExitClass` rename at U-CP-47 + U-CP-48 | Preserved verbatim |
| v2.15 + v2.14 + v2.13 + ... + v2 chain | Preserved verbatim |
| DAG topology | Preserved verbatim (zero new edges; zero edge removals) |
| Coverage matrix | Preserved verbatim |
| Cluster table (9 clusters; 55 in-cluster units + 3 pre-cluster L0) | Preserved verbatim |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_18.md` |
| Version | v2.18 |
| Filing event | Class 1 fork resolution Path A absorption — U-CP-56 StepExecutionContext 9th-field addition per `.harness/class_1_fork_step_execution_context_workflow_id_field_absence.md` ratification 2026-05-24; companion to CP spec v1.11 → v1.12 |
| Predecessor | `Implementation_Plan_Control_Plane_v2_17.md` (v2.17 substantive content preserved verbatim outside U-CP-56 plan-body amendment site) |
| Co-published artifacts | CP spec v1.12 (commit `8614c9f`); harness-cp impl (StepExecutionContext field add + driver fill); harness-runtime impl (cost-attribution callsite migration); workspace `CLAUDE.md` row bumps; fork doc §8 ratification footer |
| Operator authority | `.harness/class_1_fork_step_execution_context_workflow_id_field_absence.md` Path A ratification (AskUserQuestion 2026-05-24) |
| Unit-count change | None (73 → 73) |
| DAG topology change | None |
| Skill discipline | `implementation-planner` revision-pass mode (Phase-7 fork-resolution apply at companion to spec-writer v1.12 amendment); `phase-7-back-flow-routing` Class 1 fork detection at cost-axis production migration arc opening |
| Date | 2026-05-24 |
