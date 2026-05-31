# Cross-Axis Composition Document (v2.17)

*Delta over v2.16. v2.17 ABSORBS the 6 PENDING §0.4 forward-tracking marker entries (U-CP-74..U-CP-79 §16.5 CP→IS composer atomic-unit LANDED events at PRs #39-#44 2026-05-28..29) into canonical §2.3.2 row enumeration + §2.1 aggregate matrix + §2.4 per-axis attribution. CP→IS bucket grows 37 → 43 canonical (+6 NEW rows); 9 → 15 genuine (+6 NEW Pattern-P1 typed seams); aggregate matrix 101 → 107; genuine total 31 → 37. Per-axis attribution: CP outbound 63 → 69; CP genuine 22 → 28. Mirror precedent: v2.6 absorbed 5 composer-arc rows at §2.3.7 in single bundled arc; v2.9 absorbed 1 row at §2.3.7 cost-attribution; v2.15 absorbed 1 row at §2.3.3 ToolContract. v2.17 absorbs 6 rows at §2.3.2 in single bundled arc. ZERO change to §2.2 / §2.3.1 / §2.3.3 / §2.3.4 / §2.3.5 / §2.3.6 / §2.3.7. All v2.16 + earlier substantive content preserved verbatim except for the §2.1 / §2.3.2 / §2.4 amendment sites enumerated at §0.2. Co-published with `harness-runtime/tests/integration/test_cxa_pattern_p1.py` PATTERN_P1_SEAMS extension 25 → 31 seams (6 new rows; `test_seam_count_is_25` → `test_seam_count_is_31` rename per workspace v2.15 precedent).*

## §0 Change note (v2.16 → v2.17)

### §0.1 Revision context — 6 §16.5 CP→IS Pattern-P1 absorption events

Per CXA v2.16 §0.4 forward-tracking marker pre-commitment: *"Per-CP-unit impl landing cadence is operator-discretion at Phase 7 7b consumption rhythm. Each landing event MUST trigger a CXA narrow-scope revision absorbing the Pattern-P1 enforcement row addition (per the v2.9 / v2.15 precedent). Bundling multiple per-CP-unit landings into a single CXA revision is acceptable per discretion."*

The 6 NEW CP→IS state-ledger emission composer atomic units LANDED at HEAD in the 2026-05-28..29 window per memory anchor `[[cluster-a-cp-is-wiring-library-complete-phase-6-handoff]]`:

| CP-source-unit | NEW atomic unit | Composer function | Production module + line | Landing PR |
|---|---|---|---|---|
| U-CP-14 | U-CP-74 | `emit_override_state_ledger_entry` (sibling-variant to existing `emit_override_audit_entry`) | `harness-cp/src/harness_cp/per_step_override_evaluator.py:288` | PR #39 |
| U-CP-27 | U-CP-75 | `emit_workload_class_selection_state_ledger_entry` | `harness-cp/src/harness_cp/workload_binding_engine_class_selection.py:302` | PR #40 |
| U-CP-30 | U-CP-76 | `emit_pause_resume_state_ledger_entry` (workflow-layer class method) | `harness-cp/src/harness_cp/pause_resume_protocol.py:637` | PR #41 |
| U-CP-37 | U-CP-77 | `emit_hitl_tool_call_rewriting_state_ledger_entry` | `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py:249` | PR #42 |
| U-CP-49 | U-CP-78 | `emit_pause_captured_state_ledger_entry` (engine-layer free function) | `harness-cp/src/harness_cp/pause_resume_protocol.py:750` | PR #43 |
| U-CP-50 | U-CP-79 | `emit_resume_attempted_state_ledger_entry` (engine-layer free function) | `harness-cp/src/harness_cp/pause_resume_protocol.py:868` | PR #44 |

Each composer constructs `EntryPayload` from `harness_is.state_ledger_write` per CP spec v1.25 § 16.5.3 contract; the import is a vanilla Pattern-P1 symbol-equality CP→IS edge per workspace canonical convention.

Bundled-absorption pattern per CXA v2.16 §0.4 discretion clause. Single-arc absorption mirrors v2.6 5-row arc (Phase A.2 composer absorption at §2.3.7). Force-multiplier rationale: 6 LANDED units sharing a single producer-module (`harness_is.state_ledger_write`) + single producer-symbol (`EntryPayload`) at all 6 sites — natural bundling.

### §0.2 Sections revised

§0 (this change note); §2.1 (aggregate 4×4 matrix — CP→IS bucket cell 37 → 43; aggregate total 101 → 107); §2.3.2 (CP→IS per-bucket enumeration — 6 NEW rows appended; row classification = genuine Pattern-P1 typed seam at each); §2.4 (per-axis outbound posture summary — CP outbound 63 → 69, CP genuine 22 → 28; aggregate genuine 31 → 37; standard CP→IS Pattern-P1 symbol-equality attribution); §0.4 (v2.16 forward-tracking marker tracking-status transit 6 PENDING → 6 ABSORBED). All other sections preserved verbatim from v2.16 (which preserved verbatim from v2.15 + v2.14 + v2.13 + v2.12 + v2.11 + v2.10 + v2.9 + v2.8 + v2.7 + v2.6).

### §0.3 §2.3.2 row absorption (6 NEW rows; CP→IS bucket 37 → 43)

The v2.3-and-later §2.3.2 enumeration (preserved verbatim through v2.16) is amended at v2.17 with 6 new rows appended. Row entries:

| # | Row entry | Consumer (CP) | Producer (IS) | Pattern-P1 symbol | Classification |
|---|---|---|---|---|---|
| Row 38 | U-CP-74 → U-IS-11 | `harness_cp.per_step_override_evaluator` | `harness_is.state_ledger_write` | `EntryPayload` | Genuine typed seam |
| Row 39 | U-CP-75 → U-IS-11 | `harness_cp.workload_binding_engine_class_selection` | `harness_is.state_ledger_write` | `EntryPayload` | Genuine typed seam |
| Row 40 | U-CP-76 → U-IS-11 | `harness_cp.pause_resume_protocol` (workflow-layer class) | `harness_is.state_ledger_write` | `EntryPayload` | Genuine typed seam |
| Row 41 | U-CP-77 → U-IS-11 | `harness_cp.hitl_as_tool_call_rewriting` | `harness_is.state_ledger_write` | `EntryPayload` | Genuine typed seam |
| Row 42 | U-CP-78 → U-IS-11 | `harness_cp.pause_resume_protocol` (engine-layer free fn) | `harness_is.state_ledger_write` | `EntryPayload` | Genuine typed seam |
| Row 43 | U-CP-79 → U-IS-11 | `harness_cp.pause_resume_protocol` (engine-layer free fn) | `harness_is.state_ledger_write` | `EntryPayload` | Genuine typed seam |

All 6 rows target U-IS-11 (canonical state-ledger write seam per C-IS-07 §7.2 JsonlLedgerHandle write contract; producer module `harness_is.state_ledger_write` exports `EntryPayload` per IS spec v1.2 §C-IS-10 §10.5). Rows 40 + 42 + 43 share consumer module `pause_resume_protocol` (3 distinct composer surfaces at the same file — 1 class method + 2 module-level free functions per CP spec v1.11 §26 NOTE engine-layer-vs-workflow-layer coexistence); the symbol-equality enforcement at the runtime Pattern-P1 test ENFORCES the `(consumer_mod, producer_mod)` pair regardless of edge-name multiplicity.

Carrier-allowlist transition (`harness-runtime/tests/integration/test_cxa_pattern_p1.py` lines 360-365): `EntryPayload` REMAINS at the carrier-allowlist for U-AS-26 + U-CP-34 secondary-import contexts (existing canonical-seam coverage at v2.16 preserved). The 6 NEW rows at v2.17 §2.3.2 are PRIMARY canonical-seam declarations (consumer module imports `EntryPayload` as the foundational shape it constructs), distinct from the carrier-allowlist secondary-import role.

### §0.4 v2.16 forward-tracking marker tracking-status transit (6 PENDING → 6 ABSORBED)

The v2.16 §0.4 marker enumerated 6 PENDING per-CP-unit absorption events. v2.17 transits all 6 to ABSORBED:

| CP-source-unit | v2.16 tracking-status | v2.17 tracking-status |
|---|---|---|
| U-CP-14 | PENDING per-CP-unit impl landing | **ABSORBED at v2.17 §2.3.2 row 38** |
| U-CP-27 | PENDING per-CP-unit impl landing | **ABSORBED at v2.17 §2.3.2 row 39** |
| U-CP-30 | PENDING per-CP-unit impl landing | **ABSORBED at v2.17 §2.3.2 row 40** |
| U-CP-37 | PENDING per-CP-unit impl landing | **ABSORBED at v2.17 §2.3.2 row 41** |
| U-CP-49 | PENDING per-CP-unit impl landing | **ABSORBED at v2.17 §2.3.2 row 42** |
| U-CP-50 | PENDING per-CP-unit impl landing | **ABSORBED at v2.17 §2.3.2 row 43** |
| U-CP-34 | ABSORBED at v2.x prior | PRESERVED VERBATIM (no change) |
| U-CP-12 (NOT-APPLICABLE) | NOT-APPLICABLE per CP spec v1.25 §16.5.10 | PRESERVED VERBATIM (no change) |
| U-CP-52 (NOT-APPLICABLE) | NOT-APPLICABLE per CP spec v1.25 §16.5.10 | PRESERVED VERBATIM (no change) |

§0.4 marker closure: **6 of 6 PENDING transit to ABSORBED.** Future-PENDING marker now EMPTY (the 2 NOT-APPLICABLE reclassifications are not pending events; they are structural NOT-IN-SCOPE-AT-CP-LAYER declarations). Workspace pre-commitment closed.

### §0.5 §2.1 aggregate matrix amendment

Pre-v2.17 §2.1 matrix at CP→IS cell: **37 canonical / 9 genuine**.
v2.17 §2.1 matrix at CP→IS cell: **43 canonical (+6) / 15 genuine (+6)**.

Aggregate total: **101 → 107** (+6).
Genuine total: **31 → 37** (+6).
Convention-level + Phase-2-runtime: **48 + 22 = 70** PRESERVED VERBATIM.

37 + 70 = 107. Matrix arithmetic balances.

### §0.6 §2.4 per-axis attribution amendment

| Axis | v2.16 outbound | v2.17 outbound | v2.16 genuine | v2.17 genuine |
|---|---|---|---|---|
| **CP** | 63 | **69 (v2.17: +6 rows 38-43)** | 22 | **28 (v2.17: +6 rows 38-43)** |
| AS | 11 | 11 (unchanged) | 7 | 7 (unchanged) |
| OD | 27 | 27 (unchanged) | 2 | 2 (unchanged) |
| IS | 0 | 0 (unchanged) | 0 | 0 (unchanged) |

CP-axis attribution: vanilla CP→IS Pattern-P1 symbol-equality. The 6 NEW rows have CP-side consumer + IS-side producer + IS-axis-owned namespace (`harness_is.state_ledger_write`) — all three attributions converge on CP outbound. No §2.1-vs-§2.4 divergence (unlike v2.9 row 8 cost-attribution case which was OD-axis-attributed at §2.4 despite living at the CP→OD bucket at §2.1).

### §0.7 Status posture

Proposed (v2.16) → **Proposed (v2.17)**. v2.17 is an additive amendment — 6 new rows at §2.3.2 + aggregate matrix update + per-axis outbound posture update + §0.4 tracking-marker closure. No prior edge classification change; no prior edge spec-version cite change; no acceptance criterion change at any prior row.

### §0.8 Forward-cite acknowledgement

§0.3 cites CP spec v1.25 §16.5.3 (`EntryPayload` shape contract) + IS spec v1.2 §C-IS-10 §10.5 (`EntryPayload` exporter at `harness_is.state_ledger_write`). Both cites resolve byte-exact at HEAD.

### §0.9 Adjacent defects surfaced (not patched per FM-2 no-extension discipline)

(i) **§2.3.2 row 8 (U-CP-34) status reconciliation STILL OWED at next CXA revision.** v2.16 §0.7 (i) flagged this carry; v2.17 preserves it per FM-2. The U-CP-34 → U-IS-11 row at §2.3.2 prose carries pre-LANDING text; the row's LANDED status at U-RT-35 PARTIAL (commit `2e417e0` 2026-05-21) is reflected at the carrier-allowlist + at `[[h-t-cp-34-class-1-fork-aggregate-routing-update]]` family but NOT in §2.3.2 row prose. NOT patched at v2.17 per FM-2.

(ii) **U-CP-12 + U-CP-52 §2.3.2 row prose reflecting NOT-APPLICABLE status STILL OWED at future CXA revision.** v2.16 §0.7 (iv) flagged this carry; v2.17 preserves it per FM-2. The existing §2.3.2 rows enumerating U-CP-12 + U-CP-52 → IS-target-unit pairs carry forward-looking edges that CP spec v1.25 §16.5.10 reclassifies as not-applicable. NOT patched at v2.17 per FM-2.

(iii) **Plan-vs-CXA AS→IS 13-vs-11 reconciliation flagged at PR #91.** AS plan v1.2 §3.4 enumerates 13 AS→IS edges (preserved at `harness-as/CLAUDE.md` §2.4 plan-internal table); CXA v2.6 → v2.17 §2.4 attribution aggregates to 11. The 13-vs-11 collapse pre-dates the `[[class_3_tension_per_axis_claude_md_v2_1_to_v2_4_count_drift]]` carry (CXA v2.0 was already at 11). Reconciliation arc owed at separate scope. NOT patched at v2.17 per FM-2.

### §0.10 Downstream absorption owed (post-v2.17)

(a) Workspace `CLAUDE.md` §2.4 CXA row version bump (v2.16 → v2.17). **Co-published at this PR.**
(b) Workspace `CLAUDE.md` §1.1 CXA row aggregate count refresh (101 → 107 canonical; 31 → 37 genuine; §2.3.2 row 8 → row 43; close §0.4 6-PENDING marker). **Co-published at this PR.**
(c) `harness-runtime/tests/integration/test_cxa_pattern_p1.py` PATTERN_P1_SEAMS extension 25 → 31 seams; `test_seam_count_is_25` rename → `test_seam_count_is_31`. **Co-published at this PR.**
(d) `.harness/clearance/Cross_Axis_Composition_Document-v2_17-cleared-2026-05-31.md` clearance marker filing per workspace `CLAUDE.md` §4.5. **Co-published at this PR.**
(e) `harness-cp/CLAUDE.md` §2.3 CP→IS row cardinality refresh — **NO change owed at v2.17.** §2.3 row cardinality at harness-cp/CLAUDE.md is sourced from CXA §2.1 aggregate matrix; the workspace-level refresh at (b) covers the cite.
(f) `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` annotation owed at retirement-event filing absorbing the §0.4 6-PENDING → 6-ABSORBED transit. Deferred to retirement-event filing arc (separate scope per FM-2).
(g) `Implementation_Plan_Control_Plane_v2_28.md` § per-unit body cite refresh from CXA v2.16 → v2.17. Deferred per FM-2 no-extension discipline; plan-side cite refresh follows the v2.9 / v2.15 precedent (cite-refresh at next CP plan revision pass).

---

## §1 — Cross-arc note (Phase 6 design arc workspace-pre-commitment closure)

This v2.17 amendment closes the workspace pre-commitment authored at CXA v2.16 §0.4 forward-tracking marker: *"Each landing event MUST trigger a CXA narrow-scope revision absorbing the Pattern-P1 enforcement row addition."* All 6 PENDING transit to ABSORBED in single bundled arc; future-PENDING marker now EMPTY.

Per workspace pattern catalogue: this is the THIRD application of the narrow-scope-CXA-revision pattern (v2.9 = 5 absorptions at §2.3.7; v2.15 = 1 absorption at §2.3.3; v2.17 = 6 absorptions at §2.3.2). Cardinality 3 at the pattern catalogue: candidate for workflow §7.4.7.2 sub-species addition at next workflow-doc revision (cumulative absorption count 5 + 1 + 6 = 12 rows across 3 narrow-scope arcs).

The full Phase 6 design arc absorbed across CP spec v1.25 + CP plan v2.28 + CXA v2.16 → v2.17 covers the design-substrate + impl-layer cascade:

| Layer | Status |
|---|---|
| Architect recommendation `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md` | **Filed** 2026-05-28 (operator-ratified Q-set) |
| Parent fork `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` | **RE-OPENED** 2026-05-28; Path A authorized |
| CP spec v1.24 → v1.25 NEW §16.5 (6 composers + 2 not-applicable reclassifications at §16.5.10) | **Co-published** at Phase 6 design arc |
| CP plan v2.27 → v2.28 NEW U-CP-74..79 (6 atomic units) | **Co-published** at Phase 6 design arc |
| CXA v2.15 → v2.16 tracking-marker | **Filed** at Phase 6 design arc |
| Per-CP-unit impl + tests at PRs #39-#44 (6 atomic-unit consumption arcs) | **LANDED** 2026-05-28..29 |
| CXA v2.16 → v2.17 narrow-scope absorption + Pattern-P1 enforcement extension + workspace CLAUDE.md bump + clearance marker | **THIS arc** 2026-05-31 |
| H_T-RT-35 PARTIAL → RETIRE-READY transit | **PRESERVED** (gated on full CP-materializable 6-edge §12.3 wired + Gap C canonical-vs-materialized differential resolution at runtime spec revision — separate from this CXA absorption arc) |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Cross_Axis_Composition_Document_v2_17.md` |
| Version | v2.17 |
| Filing event | Narrow-scope absorption of 6 PENDING §0.4 forward-tracking marker entries (U-CP-74..U-CP-79 §16.5 CP→IS composer atomic-unit LANDED events at PRs #39-#44 2026-05-28..29) into canonical §2.3.2 row enumeration + §2.1 aggregate matrix + §2.4 per-axis attribution. Closes workspace pre-commitment authored at CXA v2.16 §0.4 marker. 2026-05-31 |
| Predecessor | `Cross_Axis_Composition_Document_v2_16.md` (preserved verbatim outside the §0 + §2.1 + §2.3.2 6-row-append + §2.4 amendment sites enumerated at §0.2) |
| Successor | (none — current canonical) |
| Aggregate count | **107 canonical cross-axis relationships** (v2.16: 101 + 6 NEW v2.17 §2.3.2 absorption). **37 genuine typed seams** (v2.16: 31 + 6 NEW v2.17 §2.3.2 absorption). Convention-level **48** preserved. Phase-2-runtime **22** preserved. 37 + 48 + 22 = 107. |
| CP→IS bucket | **43 canonical edges** (v2.16: 37 + 6 NEW v2.17 §2.3.2 absorption). **15 genuine** (v2.16: 9 + 6 NEW). |
| CP→AS bucket | **19 canonical edges** (v2.16 unchanged at v2.17). **6 genuine** (v2.16 unchanged). |
| Per-axis attribution | CP outbound 63 → **69** (+6 rows 38-43); CP genuine 22 → **28** (+6 rows 38-43); AS outbound + AS genuine + OD outbound + OD genuine + IS outbound UNCHANGED from v2.16. |
| §0.4 v2.16 marker status | **6 of 6 PENDING → ABSORBED at v2.17 §2.3.2 rows 38-43.** §0.4 marker closure complete. |
| Operator authority | Workspace pre-commitment closure per CXA v2.16 §0.4 marker authority chain (architect recommendation `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md` Q-set ratification 2026-05-28 + impl-time grounding pass ratification + parent fork doc Option A authorization). Operator AskUserQuestion ratification at session resumption 2026-05-31 for THIS arc scope. |
| Related forks | `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` (RE-OPENED 2026-05-28; Path A authorized; PARTIAL → RETIRE-READY transit STILL gated on full CP-materializable 6-edge §12.3 wired + Gap C resolution per runtime spec revision) |
| Related memory | `[[cluster-a-cp-is-wiring-library-complete-phase-6-handoff]]` + `[[close-phase-complete-pre-design-batches-42-44]]` + `[[backlog-steady-state-post-batch-41]]` + `[[phase-6-design-arc-cluster-a-cp-is-wiring]]` |
| Date | 2026-05-31 |
