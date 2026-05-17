# Implementation Plan — Operational Discipline (OD axis) — v2.9

**Status: Proposed.**

**Revision:** v2.9 — Phase 7 sub-phase 7b in-CLI revision pass. Resolves the **FF-2 carried Class 1 fork** at U-OD-28 (collector-placement enum) by conforming the unit to the v1.4 spec (`Spec_Operational_Discipline_v1_4.md` — C-OD-01 §1.2 + C-OD-20 §20.1, the FF-2 spec fix). v2.9 is a delta over v2.8: **only §3.7.2 U-OD-28 is revised**; every other §0–§11 section is preserved verbatim from v2.8. Predecessor: v2.8 (five Class 1 defects U-OD-02/08/09/12/21).

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `CLAUDE.md` §1.3 authority chain + §4.3 back-flow routing; `harness-od/CLAUDE.md` §5.1 (OD plan atomic-unit signature defect → plan revision); `implementation-planner` SKILL.md §8 revision-pass sub-mode.

**Entry authorization:** Operator ratification 2026-05-16 of the FF-2 resolution (Option A — spec fix at `Spec_Operational_Discipline_v1_4.md`, then plan conform). `.harness/class_1_tension_u_od_28_collector_placement_ff2.md`.

---

## §0 Change-note

### §0.1 Trigger

During OD axis-stream 7b execution (2026-05-16, batch 2), U-OD-28 halted Class 1 — the carried **FF-2** fork (`Implementation_Plan_Operational_Discipline_v2_5.md` §0.6). U-OD-28's `CollectorPlacement` enum was a three-way mismatch: a 7-value plan-introduced deployment-topology taxonomy; spec C-OD-01 §1.2's 6-value architectural-class enum; and C-OD-20 §20.1's 8-row prose matrix with no enum declaration and a cell-2/cell-4 placement gap. The operator ratified Option A: fix the spec, then conform the plan. The spec fix is filed at `Spec_Operational_Discipline_v1_4.md` — §1.2's enum grown 6 → 7 (`self-hosted-backend-collector` added), §20.1 given an explicit 7-value `CollectorPlacement` enum + a `Cell → Set<CollectorPlacement>` per-cell mapping. v2.9 conforms U-OD-28 to that v1.4 spec.

### §0.2 The defect + resolution

| # | Unit | Defect | Resolution (operator-ratified 2026-05-16) |
|---|---|---|---|
| FF-2 | U-OD-28 | `CollectorPlacement` was a 7-value plan-introduced deployment-topology enum (`IN_PROCESS_LOOPBACK` / `EXTERNAL_OTLP_LOCALHOST` / …) transcribing neither spec §1.2's 6-value enum nor §20.1 (an 8-row prose matrix, no enum). acc #1's "7 values per §20.1 verbatim" cited a non-existent surface. `PerCellPlacement.placement_class` was single-valued — but §20.1's cell-2/cell-4/cell-5/cell-7 prose carries alt-route disjunctions. | **Conform to `Spec_Operational_Discipline_v1_4.md` §20.1.** `CollectorPlacement` re-authored to the v1.4 §20.1 7-value architectural-class enum (`IN_PROCESS` / `SELF_HOSTED_BACKEND_COLLECTOR` / `SIDECAR` / `VENDOR_PIPELINE` / `SIDECAR_WITH_PER_TENANT_ROUTING` / `PER_TENANT_COLLECTOR_INSTANCE` / `VENDOR_MANAGED_COLLECTOR`). `PerCellPlacement.placement_class` widened to `placement_classes : Set<CollectorPlacement>`; `PER_CELL_COLLECTOR_PLACEMENT` → `Map<CellID, Set<CollectorPlacement>>`; `collector_placement` return widened to the set. acc #1 → "7 values per §20.1 verbatim" (now true); acc #3 → the v1.4 §20.1 `Cell → Set<CollectorPlacement>` table. See §3.7.2. |

### §0.3 Scope

Only §3.7.2 (U-OD-28) is revised. No contract re-decomposed; no unit added or removed; unit count unchanged (35). No dependency-graph edge added or removed (§4.6) — U-OD-28's `Depends on: [U-OD-01, U-OD-02, U-OD-27]` is unchanged.

### §0.4 Sections preserved verbatim from v2.8

All of §0 (v2.8 change-note), §1, §2, §3 except §3.7.2 U-OD-28, §4 except the §4.6 restatement below, §5–§11. The v2.8-revised units (U-OD-02/08/09/12/20/21) and the v2.7-revised units (U-OD-00, U-OD-30) are unchanged.

### §0.5 Coverage matrix delta

| Contract | v2.8 coverage | v2.9 coverage |
|---|---|---|
| C-OD-20 §20.1, §20.2 | U-OD-28 (`CollectorPlacement` divergent — FF-2 halt) | U-OD-28 — `CollectorPlacement` byte-exact with `Spec_Operational_Discipline_v1_4.md` §20.1's 7-value enum; per-cell mapping byte-exact with the v1.4 §20.1 `Cell → Set<CollectorPlacement>` table |

No contract row loses a column mark; no plan-unit column loses a row mark. Coverage complete.

### §0.6 Dependency-graph delta

**No delta.** U-OD-28's `Depends on: [U-OD-01, U-OD-02, U-OD-27]` is unchanged. The within-axis DAG, the Kahn topological sort, and acyclicity are unchanged. See §4.6.

---

## §3.7.2 U-OD-28 — Declare per-cell OTLP collector placement matrix + BatchSpanProcessor universality [REVISED — v2.9]

[v2.1-base unit (preserved verbatim through v2.8). v2.9 delta (FF-2): `CollectorPlacement` re-authored to the `Spec_Operational_Discipline_v1_4.md` §20.1 7-value architectural-class enum; `PerCellPlacement.placement_class` widened to a set; `PER_CELL_COLLECTOR_PLACEMENT` and `collector_placement` widened to set-valued; acc #1 + acc #3 conformed to the v1.4 §20.1 enum + per-cell `Set<CollectorPlacement>` table. acc #2/#4/#5/#6/#7/#8, `Depends on`, the §20.2 `BatchSpanProcessor` universality surface, Files affected, rollback boundary preserved verbatim from v2.1 except as conformed.]

**Implements:** [C-OD-20 §20.1, §20.2] — cited at `Spec_Operational_Discipline_v1_4.md` (the FF-2 spec fix; §20.1 enum declaration + per-cell `Set<CollectorPlacement>` mapping).

**Depends on:** [U-OD-01, U-OD-02, U-OD-27]

**Inputs:** OD spec v1.4 §20.1 per-cell collector placement matrix (the 7-value `CollectorPlacement` enum + the 8-cell `Cell → Set<CollectorPlacement>` table — singleton for cells 1/3/5/6/8, 2-element for the alt-route cells 2/4/7); §20.2 BatchSpanProcessor async emission universality (all 8 cells emit async per OTel-default windows from U-OD-27); §1.2 per-cell entry schema (Collector-placement field draws from the §20.1 7-value enum).

**Files affected:** Per-cell collector placement matrix (logical name: `od-per-cell-collector-placement-matrix`).

**Signatures (v2.9 — `CollectorPlacement` conformed to v1.4 §20.1; per-cell mapping widened to `Set<CollectorPlacement>`):**

```
// v1.4 §20.1 verbatim — the 7-value CollectorPlacement architectural-class
// enum. v2.9 (FF-2): replaces the v2.1 plan-introduced deployment-topology
// taxonomy. Byte-exact with Spec_Operational_Discipline_v1_4.md §20.1.
enum CollectorPlacement {
  IN_PROCESS,                                      // §20.1 — in-process otelcol-contrib via localhost socket
  SELF_HOSTED_BACKEND_COLLECTOR,                   // §20.1 — cell-committed self-hosted single-node backend's OTLP endpoint
  SIDECAR,                                         // §20.1 — collector-as-sidecar / collector-as-DaemonSet (K8s deployment-form)
  VENDOR_PIPELINE,                                 // §20.1 — vendor-managed ingestion pipeline (SDK / agent / Lambda)
  SIDECAR_WITH_PER_TENANT_ROUTING,                 // §20.1 — sidecar with per-tenant routing
  PER_TENANT_COLLECTOR_INSTANCE,                   // §20.1 — distinct collector instance per tenant
  VENDOR_MANAGED_COLLECTOR                         // §20.1 — vendor-managed collector at vendor-managed runtime
}                                                  // exactly 7 values per v1.4 §20.1

record PerCellPlacement {
  cell_id            : CellID
  placement_classes  : Set<CollectorPlacement>      // v2.9 — non-empty; |·| ∈ {1, 2} (2 at the alt-route cells 2/4/7)
  emission_mode      : "BATCH_SPAN_PROCESSOR_ASYNC" // §20.2 universality
  emission_window    : Duration                     // = BATCH_SPAN_PROCESSOR_WINDOW from U-OD-27
  emission_batch     : int                          // = BATCH_SPAN_PROCESSOR_BATCH_SIZE from U-OD-27
}

const PER_CELL_COLLECTOR_PLACEMENT : Map<CellID, PerCellPlacement>   // exactly 8 entries

fn collector_placement(cell_id : CellID) -> Set<CollectorPlacement>  // non-empty; Err at EXCLUDED cell
fn assert_async_emission_universality(placement : PerCellPlacement) -> Result<(), EmissionModeViolation>
```

**Acceptance criteria (v2.9 — acc #1 + #3 conformed to v1.4 §20.1; #2/#4/#5/#6/#7/#8 preserved verbatim from v2.1):**

1. **(v2.9 FF-2.)** `CollectorPlacement` enumerates exactly **7** values per `Spec_Operational_Discipline_v1_4.md` §20.1 verbatim: `IN_PROCESS`, `SELF_HOSTED_BACKEND_COLLECTOR`, `SIDECAR`, `VENDOR_PIPELINE`, `SIDECAR_WITH_PER_TENANT_ROUTING`, `PER_TENANT_COLLECTOR_INSTANCE`, `VENDOR_MANAGED_COLLECTOR`.
2. `PER_CELL_COLLECTOR_PLACEMENT` declares exactly **8** entries — one `PerCellPlacement` per ACTIVE cell.
3. **(v2.9 FF-2.)** Each cell's `placement_classes` is a non-empty `Set<CollectorPlacement>` matching the v1.4 §20.1 `Cell → Set<CollectorPlacement>` table verbatim:
   - cell-1 (solo-developer × local-development) → `{IN_PROCESS}`
   - cell-2 (solo-developer × self-hosted-server) → `{IN_PROCESS, SELF_HOSTED_BACKEND_COLLECTOR}` (the §20.1 alt-route disjunction — in-process permitted as alt-route, backend's collector preferred)
   - cell-3 (solo-developer × managed-cloud) → `{VENDOR_PIPELINE}`
   - cell-4 (team-binding × local-development) → `{IN_PROCESS, SELF_HOSTED_BACKEND_COLLECTOR}` (the §20.1 alt-route disjunction — in-process + sqlite OR Langfuse self-hosted single-node OTLP)
   - cell-5 (team-binding × self-hosted-server) → `{SIDECAR}` (collector-as-sidecar / collector-as-DaemonSet — DaemonSet is a K8s deployment-form of the sidecar class)
   - cell-6 (team-binding × managed-cloud) → `{VENDOR_PIPELINE}`
   - cell-7 (multi-tenant-compliance × self-hosted-server) → `{SIDECAR_WITH_PER_TENANT_ROUTING, PER_TENANT_COLLECTOR_INSTANCE}` (the §20.1 alt-route disjunction)
   - cell-8 (multi-tenant-compliance × managed-cloud) → `{VENDOR_MANAGED_COLLECTOR}`
4. `emission_mode == "BATCH_SPAN_PROCESSOR_ASYNC"` at every entry per §20.2 universality invariant.
5. `emission_window` and `emission_batch` inherit from U-OD-27 constants — uniform OTel-default windows across all 8 cells.
6. `assert_async_emission_universality` returns `Err(EmissionModeViolation)` if any cell's emission mode deviates from BatchSpanProcessor async.
7. Specific vendor endpoint or per-tenant routing configuration deferred per §20.1 "Deferred to implementation discretion" — the matrix commits the placement class(es), not the deployment-binding-time endpoint URL; at the three alt-route cells (2/4/7) the operator selects one alternant from the 2-element set at deployment-binding time.
8. cell-7 and cell-8 placement classes encode per-tenant separation at OTLP-collector level — `SIDECAR_WITH_PER_TENANT_ROUTING` / `PER_TENANT_COLLECTOR_INSTANCE` / `VENDOR_MANAGED_COLLECTOR` — composes with U-OD-30 + U-OD-31 multi-tenant enforcement.

**Tests (v2.9 — cardinality + per-cell tests conformed to v1.4 §20.1):** `test_collector_placement_cardinality_seven`, `test_collector_placement_members_byte_exact_per_v1_4_section_20_1`, `test_per_cell_placement_cardinality_eight`, `test_cell_1_placement_singleton_in_process`, `test_cell_2_placement_alt_route_in_process_or_self_hosted_backend`, `test_cell_3_placement_singleton_vendor_pipeline`, `test_cell_4_placement_alt_route_in_process_or_self_hosted_backend`, `test_cell_5_placement_singleton_sidecar`, `test_cell_6_placement_singleton_vendor_pipeline`, `test_cell_7_placement_alt_route_sidecar_routing_or_per_tenant_instance`, `test_cell_8_placement_singleton_vendor_managed`, `test_placement_classes_set_nonempty_all_cells`, `test_placement_classes_cardinality_one_or_two_all_cells`, `test_emission_mode_async_universal`, `test_emission_window_inherits_from_u_od_27`, `test_emission_batch_inherits_from_u_od_27`, `test_assert_async_universality_reject_sync`, `test_specific_vendor_endpoint_deferred`, `test_per_tenant_placement_at_cells_7_8`.

**Rollback boundary:** Revert per-cell collector placement matrix. R-OD-01 + R-OD-07 satisfaction loses per-cell placement contract; BatchSpanProcessor async emission universality loses cell-level invariant; multi-tenant per-tenant OTLP separation at cells 7, 8 loses placement-layer enforcement; downstream U-OD-29 sandbox-tier reachability composes against a missing per-cell placement substrate; U-OD-30 + U-OD-31 multi-tenant separation lose placement-class foundation. [v2.9 revert appendix:] Reverting v2.9 restores the v2.1 plan-introduced 7-value deployment-topology enum — i.e. the FF-2 three-way-mismatch defect; the revert MUST NOT be performed absent a re-disposition.

---

## §4.6 Dependency-graph delta (v2.9)

**No delta.** U-OD-28's `Depends on: [U-OD-01, U-OD-02, U-OD-27]` is unchanged — the FF-2 conformance is a signature/enum revision, not an edge change. All v2.8 within-axis + cross-axis edges are preserved verbatim. The within-axis DAG is unchanged; the Kahn topological sort is unchanged; acyclicity holds. All 35 units still consume.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_9.md` |
| Authored at | Phase 7 sub-phase 7b, 2026-05-16 — v2.9 revision pass (FF-2 collector-placement conformance) |
| Authoring authority | Operator ratification 2026-05-16 (FF-2 Option A); `implementation-planner` SKILL.md §8 revision-pass sub-mode |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_8.md` (five Class 1 defects U-OD-02/08/09/12/21) |
| Substrate consumed | `Spec_Operational_Discipline_v1_4.md` §1.2 + §20.1 (the FF-2 spec fix); `.harness/class_1_tension_u_od_28_collector_placement_ff2.md` |
| Successor consumption | U-OD-28 lands against this file; its dependents U-OD-29, U-OD-30, U-OD-31, U-OD-34 (terminal exporter) unblock. |
| Revision policy | Canonical for the OD axis plan; revisions in-CLI per workspace discipline |

*End of Implementation Plan — Operational Discipline v2.9. Delta over v2.8 — only §3.7.2 U-OD-28 revised (FF-2 conformance to `Spec_Operational_Discipline_v1_4.md` §20.1). All other sections preserved verbatim from v2.8. No dependency-graph edge changed; unit count unchanged (35).*
