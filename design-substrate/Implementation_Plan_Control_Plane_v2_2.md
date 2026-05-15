# Implementation Plan — Control Plane v2.2

## Status block

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_2.md` |
| Status | **Proposed** — F2-12 cascade Step 6a revision pass; promotion to Accepted at cascade close (subject to OD-F212-5 P6-CK gate disposition at Step 6 boundary) |
| Revision | v1 → v2 (P6-CK iter-1 close mechanical revision) → v2.1 (P6-CK iter-2 F2-CP-03 spec-anchor-drift absorption) → **v2.2 (F2-12 cascade Step 6a revision pass authored 2026-05-14 per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 + ADD v1.3 §6.3.1 cascade Step 6a row + CP spec v1.3 absorption)** |
| Revision date | 2026-05-14 (v2.2 revision pass) |
| Phase | 6 — Implementation planning (post-Phase-3 F2-12 cascade Step 6a per `Project_Workflow_v1_7.md` §4.1.2; cascade-driven revision pass under `implementation-planner` SKILL.md §8 revision-pass sub-mode + Workflow v1.7 §7 fidelity-grammar) |
| Skill | `implementation-planner` (revision-pass sub-mode per SKILL.md §8) at v2.2 |
| Promotion path | Accepted at F2-12 cascade close; OD-F212-5 disposition at Step 6 boundary determines whether fresh P6-CK Iteration 4 fires (Option B) or cascade-substrate exemption applies (Option A) or Phase 7 carry-forward (Option C) |
| Source-set | CP spec v1.3 (cascade Step 5a output) + OD spec v1.3 (cascade Step 5b output — cross-axis citation only; no direct ingestion) + ADD v1.3 + ADR-D1 v1.2 + ADR-D6 v1.2 + PRD v1.1 |
| Entry authorization | `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 cascade Step 6a row + ADD v1.3 §6.3.1 cascade execution path Step 6a row |
| Exit gate | F2-12 cascade close (post-Step 6b OD plan v2.2 filing + Closure Declaration); P6-CK Iteration 4 may or may not fire per OD-F212-5 disposition |

## §0 Change note (v2.1 → v2.2)

### §0.1 Scope of revision

F2-12 cascade Step 6a revision pass per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 + ADD v1.3 §6.3.1 cascade execution path Step 6a row. The revision pass absorbs CP spec v1.3 § C-CP-08 + C-CP-09 + §3.5 amendments into the CP plan + closes the F2-12 carry-forward at U-CP-20 acceptance #5 + U-CP-55 §24.4 export manifest + §1.4 F2-12 declaration. The revision pass also incidentally closes the v2.1 §0.8 forward-flagged U-CP-21 acceptance #1 + acceptance #1 citation drifts (3-attribute schema deviation from spec §9.1 canonical), because the cascade Step 5a CP spec v1.3 §9.1 4-attribute canonical declaration is the new ingestion source and the v2.1 §0.8 concerns are subsumed by the v2.2 4-attribute schema revision per substrate-driven absorption (the v2.1 concerns presumed v1.2 spec §9.1 canonical at 3 attributes; v1.3 spec §9.1 canonical at 4 attributes makes the v2.1 concerns moot rather than open).

| Finding ID (cascade-derived) | Class | Resolution shape | Amendment sites |
|---|---|---|---|
| F2-12-cascade-CP-01 | Cascade-driven | U-CP-20 acceptance #5 F2-12 carry-forward declaration revised from "active" to "CLOSED at v2.2 absorbing cascade Step 6a"; tests revised | U-CP-20 acceptance #5 + tests |
| F2-12-cascade-CP-02 | Cascade-driven | U-CP-21 3-attribute schema → 4-attribute schema per CP spec v1.3 §9.1 canonical (4 attributes: `engine.class`, `engine.event_history.tier`, `engine.event.id`, `engine.replay_disposition`); signatures table extended; acceptance #1 revised; tests revised | U-CP-21 `Implements:` + Signatures + Acceptance #1 + #2 + Tests |
| F2-12-cascade-CP-03 | Cascade-driven | U-CP-55 §24.4 export manifest F2-12 carry-forward declaration revised: `active_at_v1 = true` → `active_at_v1 = false; closed_at_v2_2 = true; closure_path = [Step 1 ✅ → ... → Step 6a ✅]` with all six cascade steps recorded as CLOSED; tests revised | U-CP-55 acceptance #3 + Tests |
| F2-12-cascade-CP-04 | Cascade-driven | §1.4 F2-12 carry-forward declaration revised from "forward-routed carry-forward" to "✅ CLOSED at v2.2 absorbing CP spec v1.3 §24.4 closure" | §1.4 |

### §0.2 Sections preserved verbatim (from v2.1)

All v2.1 content beyond the v2.2 revision scope is preserved verbatim. Specifically: §0 Change-notes (v2 → v2.1; preserved as historical record); §1 Spec inventory §1.1 + §1.2 + §1.3 (contract inventory + cluster decomposition + substrate-version citation alignment); §2 Atomic-unit decomposition §2.1 Cluster 1 (F1 routing + fallback; U-CP-01 → U-CP-09); §2.2 Cluster 2 (F3 lifecycle + manifest; U-CP-10 → U-CP-13); §2.3 Cluster 3 (D1 engine + replay; U-CP-14 → U-CP-19 — only U-CP-20 acceptance #5 and U-CP-21 acceptance #1 + signatures + tests revised at v2.2); §2.4 Cluster 4 (D4 topology + sub-agent; U-CP-22 → U-CP-27); §2.5 Cluster 5 through §2.9 Cluster 9 (D5 HITL + audit + validator + composition; U-CP-28 → U-CP-54 — only U-CP-55 acceptance #3 revised at v2.2); §3 Dependency graph + §4 Spec-traceability + §5 Persona linkage + §6 Cross-axis citation + §7 PRD-trace + §8 Through §10 (forward-flagged concerns superseded entries; ADR-trace; anti-pattern audit) — only §1.4 F2-12 carry-forward declaration revised at v2.2; §[carry-forwards] (only the F2-12 line revised at v2.2 to closure); §[coherence pass] (preserved verbatim as v1 + v2 + v2.1 historical record).

### §0.3 Sections revised (v2.1 → v2.2)

| Site | Revision | Source |
|---|---|---|
| §1.4 F2-12 carry-forward declaration | "CP spec v1.2 §24.4 declares F2-12 as a forward-routed carry-forward (not closed at v1.2)" → "CP spec v1.3 §24.4 closes F2-12 at cascade Step 5a per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2; CP plan v2.2 absorbs the closure at cascade Step 6a per ADD v1.3 §6.3.1"; closure_path table inline updated | F2-12-cascade-CP-04 |
| §1.4 closure path table row | Closure path table row updated: "Inheritance at sessions 4 + 5 per spec §24.4 closing sentence" → "Inheritance closed at cascade Step 5a (CP spec v1.3 §24.4) + Step 5b (OD spec v1.3 §14.5)" | F2-12-cascade-CP-04 |
| U-CP-20 acceptance #5 | "F2-12 carry-forward active at this unit. Per CP spec §24.4: ... CP plan v1 declares the carry-forward; closure deferred to revision-pass mode per spec-writer precedent." → "F2-12 carry-forward ✅ CLOSED at this unit per cascade Step 6a absorbing CP spec v1.3 §8.4 closure + ADD v1.3 §6.3.1 closure declaration. Per CP spec v1.3 §8.4 + §3.5: D1 v1.2 + D6 v1.2 closed sub-scopes (i) + (ii) + (iii); ADD v1.3 + PRD v1.1 + CP spec v1.3 + OD spec v1.3 closed cross-axis substrate; CP plan v2.2 closes plan-level absorption. Formal `closure_pending false` declaration at `F2-12_Closure_Declaration.md` at cascade close." | F2-12-cascade-CP-01 |
| U-CP-20 tests | Test `test_f2_12_carry_forward_declared` retained at v2.2 (declaration still present); new test `test_f2_12_carry_forward_closed_at_v2_2` added; new test `test_f2_12_closure_substrate_cascade_step_6a` added | F2-12-cascade-CP-01 |
| U-CP-21 `Implements:` | "C-CP-09 §9.1 (engine.* namespace declaration per three-attribute schema; consumed at C-CP-05 §5.2 per-class attribute composition and C-CP-09 §9.4 D6 ingestion contract)" → "C-CP-09 §9.1 (engine.* namespace declaration per **four-attribute schema** per CP spec v1.3 §9.1 amendment + ADR-D1 v1.2 §1.1.1; consumed at C-CP-05 §5.2 per-class attribute composition and C-CP-09 §9.4 D6 ingestion contract per ADR-D6 v1.2 §1.2 row engine.*)" | F2-12-cascade-CP-02 |
| U-CP-21 Signatures `ENGINE_NAMESPACE_SCHEMA` | "List<EngineAttributeSchema> // exactly 3 entries" → "List<EngineAttributeSchema> // exactly 4 entries"; signature record extended with `enum_values_when_enum` optional field for `engine.replay_disposition` 5-value enum declaration | F2-12-cascade-CP-02 |
| U-CP-21 acceptance #1 | "ENGINE_NAMESPACE_SCHEMA declares exactly three attributes per ADR-D1 v1.1 §1.1.1 + CP spec §5.3 + §9.2 verbatim: `engine.class` (`EngineClass` enum value), `engine.resumption_kind` (`ResumptionKind` enum value), `engine.tech` (deployment-bound; e.g., 'temporal-worker', 'langgraph-postgres-redis', 'kafka-streams')." → "`ENGINE_NAMESPACE_SCHEMA` declares exactly **four** attributes per CP spec v1.3 §9.1 verbatim + ADR-D1 v1.2 §1.1.1 canonical declaration: (1) `engine.class` ∈ `{event-sourced-replay, save-point-checkpoint, pure-pattern-no-engine, reconciler-loop, WAL-segment}` (bounded-5 enum; matches `EngineClass`); (2) `engine.event_history.tier` ∈ `{Tier-3, Tier-5}` (bounded-2 enum); (3) `engine.event.id` (opaque string under engine-class-native ID convention; per-event cardinality); (4) `engine.replay_disposition` ∈ `{deterministic_replay, checkpoint_resume, no_replay, reconciler_iteration, wal_consume}` (bounded-5 enum; closed-mapped to `engine.class` per ADR-D1 v1.2 §1.1.1 — new at v2.2 absorbing F2-12 sub-scope (i) closure)." | F2-12-cascade-CP-02 |
| U-CP-21 acceptance #2 | "`engine.class` cardinality bounded at 5 (matches `EngineClass`); `engine.resumption_kind` cardinality bounded at 5 (matches `ResumptionKind`); `engine.tech` cardinality low-medium (deployment-bound)." → "`engine.class` cardinality bounded at 5 (matches `EngineClass`); `engine.event_history.tier` cardinality bounded at 2; `engine.event.id` cardinality per-event (opaque); `engine.replay_disposition` cardinality bounded at 5 (closed-mapped to `engine.class` per ADR-D1 v1.2 §1.1.1; mapping table in `ReplayDispositionMapping` constant per acceptance #3)." | F2-12-cascade-CP-02 |
| U-CP-21 acceptance (new #3) | NEW acceptance criterion #3: "`ReplayDispositionMapping` constant declares the closed mapping `engine.class → engine.replay_disposition`: `event-sourced-replay → deterministic_replay`; `save-point-checkpoint → checkpoint_resume`; `pure-pattern-no-engine → no_replay`; `reconciler-loop → reconciler_iteration`; `WAL-segment → wal_consume`. The mapping is **closed and total** — every `engine.class` value has exactly one `engine.replay_disposition` value; no cross-class sharing per ADR-D1 v1.2 §1.1.1 + §1.1.2." | F2-12-cascade-CP-02 |
| U-CP-21 acceptance (former #3 → #4) | Renumbered from #3 to #4; content preserved verbatim ("D6 ingestion delegates to U-CP-54 §24.1.A (specialization-layer namespace).") with v2.2 amendment note: "D6 ingestion at v2.2 inherits the 4-attribute namespace per CP spec v1.3 §9.4 + ADR-D6 v1.2 §1.2 row engine.* (4-attribute ingestion)" | F2-12-cascade-CP-02 |
| U-CP-21 tests | `test_engine_namespace_cardinality_three` → `test_engine_namespace_cardinality_four`; new tests added: `test_engine_replay_disposition_enum_five_values`, `test_engine_replay_disposition_closed_mapped_to_engine_class`, `test_engine_event_history_tier_enum_two_values`, `test_engine_event_id_opaque_string`; existing tests `test_engine_attributes_match_spec_verbatim` updated to v1.3 spec citation; existing tests `test_engine_class_cardinality_bounded_five` + `test_engine_resumption_kind_cardinality_bounded_five` — latter renamed/repurposed to `test_engine_replay_disposition_cardinality_bounded_five` | F2-12-cascade-CP-02 |
| U-CP-55 acceptance #3 closure_path | "active_at_v1 = true (not closed at this version)" → "active_at_v1 = false; closed_at_v2_2 = true; closure_status = ✅ CLOSED at cascade Step 6a"; closure_path entries Steps 1–6 all annotated with ✅ filed-status + filing-date + artifact-path | F2-12-cascade-CP-03 |
| U-CP-55 acceptance #3 closure_path | Closure_path table extended with: Step 1 (council deliberation; filed 2026-05-14; `F2-12_Council_Deliberation_Output.md`); Step 2a + 2b (ADR-D1 + ADR-D6 v1.2; filed 2026-05-14); Step 3 (ADD v1.3; filed 2026-05-14); Step 4 (PRD v1.1; filed 2026-05-14); Step 5a + 5b (CP spec + OD spec v1.3; filed 2026-05-14); Step 6a (this artifact); Step 6b pending; Close pending | F2-12-cascade-CP-03 |
| U-CP-55 acceptance #4 | "F2-12 closure is **deferred to revision-pass mode** — CP plan v1 declares the carry-forward; closure occurs at CP plan v2 after spec v1.3 ingests revised D1 + D6 + ADD + PRD." → "F2-12 closure ✅ occurs at this CP plan v2.2 cascade Step 6a; cascade close is at Step 6b (OD plan v2.2) + F2-12 Closure Declaration." | F2-12-cascade-CP-03 |
| U-CP-55 tests | `test_f2_12_active_at_v1` → `test_f2_12_active_at_v2_2_false`; new tests: `test_f2_12_closed_at_v2_2_true`, `test_f2_12_closure_path_all_six_steps_filed`, `test_f2_12_closure_path_steps_2_through_5_present`; existing `test_f2_12_closure_path_step_6_cp_plan_v2_revision_pass` retained at v2.2 | F2-12-cascade-CP-03 |
| §[carry-forwards] [CF-1] F2-12 | Transitioned from active to ✅ CLOSED with closure-summary content | F2-12-cascade-CP-04 |

### §0.4 Coverage matrix delta

| Coverage cell | At v2.1 | At v2.2 |
|---|---|---|
| C-CP-08 §8.4 F2-12 carry-forward affected-contract notation | Meta-substrate covered by U-CP-20 acceptance #5 carry-forward declaration (active) | Meta-substrate covered by U-CP-20 acceptance #5 ✅ CLOSED declaration |
| C-CP-09 §9.1 engine.* attribute declarations | 3-attribute schema (v2.1 §0.8 forward-flagged: spec §9.1 canonical at v1.2 = 3 attrs `engine.class` + `engine.event_history.tier` + `engine.event.id`; v2.1 U-CP-21 = 3 attrs `engine.class` + `engine.resumption_kind` + `engine.tech` — drift unresolved at v2.1) | 4-attribute schema per CP spec v1.3 §9.1 canonical: `engine.class` + `engine.event_history.tier` + `engine.event.id` + `engine.replay_disposition` (drift resolved at v2.2 via cascade Step 5a + 6a substrate alignment) |
| §1.4 F2-12 carry-forward declaration | Active engagement, closure deferred | ✅ CLOSED at v2.2 |

**v2.1 §0.8 forward-flagged-concerns disposition.** The three v2.1 §0.8 forward-flagged concerns at U-CP-21 are CLOSED at v2.2 by substrate-driven absorption:
- v2.1 §0.8 row 1 (U-CP-21 acceptance #1 declares 3 engine.* attributes as `engine.class`, `engine.resumption_kind`, `engine.tech` deviating from spec §9.1 canonical at v1.2): CLOSED at v2.2 — v2.2 U-CP-21 acceptance #1 declares 4 attributes per CP spec v1.3 §9.1 canonical (the spec canonical is now 4 attributes; the v2.1 deviation is replaced rather than corrected to old canonical).
- v2.1 §0.8 row 2 (U-CP-21 acceptance #1 cites ADR-D1 v1.1 §1.1.1 + CP spec §5.3 + §9.2 verbatim with §5.3/§9.2 as wrong substrate): CLOSED at v2.2 — v2.2 acceptance #1 cites ADR-D1 v1.2 §1.1.1 + CP spec v1.3 §9.1 canonically.
- v2.1 §0.8 row 3 (U-CP-12 acceptance #3 cites C-CP-09 §9.2 for engine.* namespace where canonical is §9.1): NOT closed at v2.2 within cascade scope; v2.2 strict-narrow discipline preserves U-CP-12 verbatim. Forward-flagged for P6-CK Iteration 4 (if Option B) or future revision pass.

### §0.5 Dependency graph delta

No dependency graph changes at v2.2. U-CP-20 dependencies preserved (`[U-CP-10, U-CP-12, U-CP-18, U-CP-19]`); U-CP-21 dependencies preserved (`[U-CP-15]`); U-CP-55 dependencies preserved (terminal at L8).

### §0.6 Substrate-version-citation table (v2.2 amendment)

| Substrate | v2.1 version cited | v2.2 version cited |
|---|---|---|
| ADR-D1 | v1.1 | **v1.2** |
| ADR-D6 | v1.1 | **v1.2** |
| ADD | v1.2 | **v1.3** |
| PRD | v1.0.1 | **v1.1** |
| CP spec | v1.2 | **v1.3** |
| OD spec | v1.2 | **v1.3** (cross-axis citation only) |

### §0.7 Status

`Status: Proposed` preserved per `Project_Workflow_v1_7.md` §3.1 — promotion to `Accepted` blocked until F2-12 cascade close (post-Step 6b + Closure Declaration) and OD-F212-5 P6-CK disposition resolution. CP plan v2.2 enters cascade Step 6b context-providing entry as cross-axis substrate (OD plan v2.2 ingests CP plan v2.2 U-CP-55 §24.4 export manifest closure record).

### §0.8 Forward-flagged concerns (v2.2 update)

| Concern | v2.2 disposition | Forward-routed at v2.2 |
|---|---|---|
| v2.1 §0.8 row 1 (U-CP-21 3-attribute drift) | ✅ CLOSED at v2.2 by substrate-driven absorption | — |
| v2.1 §0.8 row 2 (U-CP-21 citation drift §5.3 + §9.2) | ✅ CLOSED at v2.2 by re-citation to v1.3 spec §9.1 | — |
| v2.1 §0.8 row 3 (U-CP-12 acceptance #3 §9.2 citation) | NOT closed at v2.2 — out of F2-12 cascade scope per strict-narrow discipline | Candidate finding for P6-CK Iteration 4 (if Option B at OD-F212-5) or future revision pass |
| C-CP-03 §3.5 retry.* 6-attribute namespace + parent-event 3-field schema (CP spec v1.3 amendment) | NOT absorbed at v2.2 within strict-narrow F2-12 cascade scope (cascade explicitly scoped to U-CP-20 + U-CP-21 + U-CP-55 per kickoff §3.2); plan unit currently at U-CP-07 (4-attribute retry namespace per v2.1) | Forward-flagged for P6-CK Iteration 4 OR future revision pass; cross-references CP spec v1.3 §3.5 amendment |
| §5.4 sampling table retry.attempt dual-emission row (CP spec v1.3 amendment) | NOT absorbed at v2.2 within strict-narrow F2-12 cascade scope; plan unit currently at U-CP-12 per-class attribute composition per v2.1 | Forward-flagged for P6-CK Iteration 4 OR future revision pass |

### §0.9 Prior revision history (v1 → v2.1; archival from v2.1 §0.9)

[Preserved verbatim from v2.1 §0.9.]

### §0.10 v2.2 coherence-pass summary

| Pass | Status |
|---|---|
| §1 Spec inventory | ✅ PASS — substrate-version citations updated to v1.3 CP spec; F2-12 carry-forward declaration at §1.4 transitioned to CLOSED |
| §2 Atomic-unit decomposition | ✅ PASS — U-CP-20 acceptance #5 + U-CP-21 acceptance #1/2/(new #3)/(former #3 → #4) + U-CP-55 acceptance #3/4 revised; all other units preserved verbatim per strict-narrow scope discipline |
| §3 Dependency graph | ✅ PASS — no dependency graph changes at v2.2 |
| §4 Spec-traceability | ✅ PASS — U-CP-20 → C-CP-08 §8.4 (closure) + U-CP-21 → C-CP-09 §9.1 (4-attribute canonical) + U-CP-55 → C-CP-24 §24.4 (closure manifest) all aligned to v1.3 spec canonical |
| §10 Anti-pattern audit | ✅ PASS — v2.1 §0.8 rows 1+2 closed at v2.2 by substrate-driven absorption; row 3 preserved at strict-narrow scope; cascade scope per kickoff §3.2 enforced |

---

## §1 Spec inventory

[§1.1 Contract inventory + §1.2 Cluster decomposition + §1.3 Substrate-version citation alignment preserved verbatim from v2.1.]

### §1.4 F2-12 carry-forward declaration (v2.2 amendment — ✅ CLOSED)

**Status (v2.2 amendment).** ✅ **CLOSED** at CP plan v2.2 filing per ADD v1.3 §6.3.1 cascade Step 6a row. CP spec v1.3 §24.4 closed F2-12 at cascade Step 5a per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2; CP plan v2.2 absorbs the closure at cascade Step 6a per ADD v1.3 §6.3.1. The v2.1 status was "CP spec v1.2 §24.4 declares F2-12 as a forward-routed carry-forward (not closed at v1.2). Active engagement surface at U-CP-20 (C-CP-08 R-CP-07-satisfying contract). Closure path declared at U-CP-55 §24.4 export manifest"; v2.2 transitions to ✅ CLOSED with full closure path filed.

| Carry-forward | Closure surface at v2.2 | Closure path filed | Inheritance status at v2.2 |
|---|---|---|---|
| F2-12 | U-CP-20 acceptance #5 ✅ CLOSED + U-CP-55 acceptance #3 closure_path ✅ filed + §1.4 ✅ CLOSED declaration (this row) | D1 v1.2 ✅ + D6 v1.2 ✅ → ADD v1.3 ✅ → PRD v1.1 ✅ → CP spec v1.3 ✅ → CP plan v2.2 ✅ (this artifact); Step 6b OD plan v2.2 + Closure Declaration pending | Inheritance closed at cascade Step 5a (CP spec v1.3 §24.4) + Step 5b (OD spec v1.3 §14.5); cross-axis composition session 5 inheritance: ingest CP plan v2.2 U-CP-55 §24.4 closure record |

---

## §2 Atomic-unit decomposition

[§2.1 Cluster 1 through §2.2 Cluster 2 preserved verbatim from v2.1.]

### §2.3 Cluster 3 — D1 engine + replay (C-CP-07, C-CP-08, C-CP-09)

[U-CP-14 through U-CP-19 preserved verbatim from v2.1.]

#### U-CP-20 — Per-resumption observable behavior catalog (v2.2 amendment to acceptance #5)

**Implements:** [C-CP-08 §8.3 (per-resumption observable behavior)]

**Depends on:** [U-CP-10, U-CP-12, U-CP-18, U-CP-19]

**Inputs / Files affected / Signatures.** [Preserved verbatim from v2.1.]

**Acceptance criteria (v2.2 amendment to #5).**

1. `PER_RESUMPTION_OBSERVABLE_BEHAVIOR` declares exactly five entries per C-CP-08 §8.3 verbatim. [Preserved verbatim from v2.1.]
2. Each entry emits `workflow.resumption` span per U-CP-10 lifecycle event class; required attributes include `engine.class` + `engine.replay_disposition` per U-CP-21 4-attribute `engine.*` namespace (v2.2 amendment — was `engine.class` + `engine.resumption_kind` at v2.1; updated to align with CP spec v1.3 §9.1 4-attribute canonical and ADR-D1 v1.2 §1.1.1 + §1.1.2).
3. `f2_join_path` carried from U-CP-18 `EngineF2JoinContract`; resumption observable behavior is per-engine-class. [Preserved verbatim from v2.1.]
4. `ContinuityGuarantee` discriminates across the five resumption kinds; per-kind continuity contract documented at acceptance. [Preserved verbatim from v2.1.]
5. **F2-12 carry-forward ✅ CLOSED at this unit (v2.2 amendment).** Per CP spec v1.3 §8.4 + §3.5 + §9.1: D1 v1.2 + D6 v1.2 closed sub-scopes (i) span re-emission semantics + (ii) retry.attempt child-per-attempt + (iii) trace-ingestion dedup composition. Cascade closure: D1 v1.2 ✅ + D6 v1.2 ✅ → ADD v1.3 ✅ → PRD v1.1 ✅ → CP spec v1.3 ✅ → CP plan v2.2 ✅ (this revision); Step 6b OD plan v2.2 + Closure Declaration pending. The v2.1 acceptance #5 declared the carry-forward as "active, closure deferred to revision-pass mode per spec-writer precedent"; v2.2 acceptance #5 declares ✅ CLOSED via the cascade execution path.

**Tests (v2.2 amendment).** `test_per_resumption_observable_behavior_cardinality_five`, `test_emits_workflow_resumption_span`, `test_engine_class_required_attribute`, **`test_engine_replay_disposition_required_attribute` (v2.2 new)**, `test_continuity_guarantee_per_kind`, **`test_f2_12_carry_forward_closed_at_v2_2` (v2.2 new; replaces `test_f2_12_carry_forward_declared` which is retained as historical)**, **`test_f2_12_closure_substrate_cascade_step_6a` (v2.2 new)**.

**Rollback boundary.** [Preserved verbatim from v2.1.]

#### U-CP-21 — Declare `engine.*` namespace + 4-attribute schema (v2.2 amendment from 3-attribute schema; closes v2.1 §0.8 rows 1+2)

**Implements (v2.2 amendment):** [C-CP-09 §9.1 (engine.* namespace declaration per **four-attribute schema** per CP spec v1.3 §9.1 amendment + ADR-D1 v1.2 §1.1.1; consumed at C-CP-05 §5.2 per-class attribute composition and C-CP-09 §9.4 D6 ingestion contract per ADR-D6 v1.2 §1.2 row engine.*)]

**Depends on:** [U-CP-15]

**Inputs:** `EngineClass` enum (U-CP-15).

**Files affected:** CP-axis engine namespace (logical: `engine-namespace-attribute-schema`).

**Signatures (v2.2 amendment).**

```
record EngineAttributeSchema {
  attribute_name        : string
  value_type            : AttributeValueType
  cardinality           : Cardinality
  enum_values_when_enum : Optional<List<string>>  // v2.2: declared for engine.class +
                                                  // engine.event_history.tier +
                                                  // engine.replay_disposition;
                                                  // null for engine.event.id (opaque)
}

const ENGINE_NAMESPACE_SCHEMA: List<EngineAttributeSchema>  // exactly 4 entries (v2.2; was 3)

# v2.2 new — closed mapping per ADR-D1 v1.2 §1.1.1
const REPLAY_DISPOSITION_MAPPING: Map<EngineClass, ReplayDisposition>  // total over EngineClass

enum ReplayDisposition {  // v2.2 new — bounded-5 enum
  DETERMINISTIC_REPLAY,
  CHECKPOINT_RESUME,
  NO_REPLAY,
  RECONCILER_ITERATION,
  WAL_CONSUME
}
```

**Acceptance criteria (v2.2 amendment).**

1. `ENGINE_NAMESPACE_SCHEMA` declares exactly **four** attributes per CP spec v1.3 §9.1 verbatim + ADR-D1 v1.2 §1.1.1 canonical declaration:
   - `engine.class` ∈ `{event-sourced-replay, save-point-checkpoint, pure-pattern-no-engine, reconciler-loop, WAL-segment}` (bounded-5 enum; matches `EngineClass`).
   - `engine.event_history.tier` ∈ `{Tier-3, Tier-5}` (bounded-2 enum).
   - `engine.event.id` (opaque string under engine-class-native ID convention — Temporal eventId, LangGraph checkpoint_id, ACP CRD event UID, Kode-Agent segment offset, pure-pattern harness-assigned UUID; per-event cardinality).
   - `engine.replay_disposition` ∈ `{deterministic_replay, checkpoint_resume, no_replay, reconciler_iteration, wal_consume}` (bounded-5 enum; closed-mapped to `engine.class` per ADR-D1 v1.2 §1.1.1 — **new at v2.2 absorbing F2-12 sub-scope (i) closure**).
2. `engine.class` cardinality bounded at 5 (matches `EngineClass`); `engine.event_history.tier` cardinality bounded at 2; `engine.event.id` cardinality per-event (opaque); `engine.replay_disposition` cardinality bounded at 5 (closed-mapped to `engine.class` per acceptance #3).
3. **`REPLAY_DISPOSITION_MAPPING` constant declares the closed mapping `engine.class → engine.replay_disposition` (v2.2 new):** `event-sourced-replay → deterministic_replay`; `save-point-checkpoint → checkpoint_resume`; `pure-pattern-no-engine → no_replay`; `reconciler-loop → reconciler_iteration`; `WAL-segment → wal_consume`. The mapping is **closed and total** — every `engine.class` value has exactly one `engine.replay_disposition` value; no cross-class sharing per ADR-D1 v1.2 §1.1.1 + §1.1.2.
4. D6 ingestion delegates to U-CP-54 §24.1.A (specialization-layer namespace). **At v2.2, D6 ingestion inherits the 4-attribute namespace per CP spec v1.3 §9.4 + ADR-D6 v1.2 §1.2 row engine.* (4-attribute ingestion; was 3 at v1.1).**

**Tests (v2.2 amendment).** `test_engine_namespace_cardinality_four` (was `_three` at v2.1), `test_engine_attributes_match_spec_v1_3_verbatim` (citation updated to v1.3), `test_engine_class_cardinality_bounded_five`, `test_engine_event_history_tier_enum_two_values` (v2.2 new), `test_engine_event_id_opaque_string` (v2.2 new), `test_engine_replay_disposition_enum_five_values` (v2.2 new), `test_engine_replay_disposition_cardinality_bounded_five` (v2.2 new; replaces deprecated `test_engine_resumption_kind_cardinality_bounded_five`), `test_engine_replay_disposition_closed_mapped_to_engine_class` (v2.2 new), `test_replay_disposition_mapping_total_over_engine_class` (v2.2 new).

**Rollback boundary (v2.2 amendment).** Revert `ENGINE_NAMESPACE_SCHEMA` to 3-attribute v2.1 form + revert `REPLAY_DISPOSITION_MAPPING` constant + revert `ReplayDisposition` enum. U-CP-12 per-class attribute composition for `workflow.resumption` loses `engine.replay_disposition` required attribute; U-CP-20 observable behavior loses replay-disposition discriminator; U-CP-54 §24.1.A export manifest reverts to CP spec v1.2 ingestion. **At v2.2, additional impact: F2-12 sub-scope (i) closure substrate at CP plan level dissolves; cascade Step 6a closure status regresses; OD plan v2.2 cross-axis substrate at U-OD-14 may lose alignment with CP-side declaration.**

[U-CP-22 through U-CP-54 preserved verbatim from v2.1.]

---

### §2.9 Cluster 9 — Composition + T-perm-3 + cross-axis manifest

[U-CP-53 + U-CP-54 preserved verbatim from v2.1.]

#### U-CP-55 — Author cross-axis composition manifest + F2-12 carry-forward declaration (v2.2 amendment to acceptance #3 + #4 + tests; closes F2-12 closure_path)

**Implements / Depends on / Inputs / Files affected / Signatures.** [Preserved verbatim from v2.1.]

**Acceptance criteria (v2.2 amendment to #3 + #4).**

1. [Preserved verbatim from v2.1.]
2. [Preserved verbatim from v2.1.]
3. **F2-12 carry-forward declaration (v2.2 amendment)** per C-CP-24 §24.4 verbatim:
   - `active_engagement_unit = U-CP-20` (R-CP-07-satisfying F2 substrate join contract).
   - `closure_path` is the canonical revision-pass chain with all six steps now ✅ filed at v2.2:
     - Step 1: Council deliberation ✅ filed 2026-05-14 — `F2-12_Council_Deliberation_Output.md` (cascade Step 1 substrate; v2.2-new in closure_path)
     - Step 2a: D1 v1.1 → v1.2 ✅ filed 2026-05-14 — `ADR-D1_v1_2.md`
     - Step 2b: D6 v1.1 → v1.2 ✅ filed 2026-05-14 — `ADR-D6_v1_2.md`
     - Step 3: ADD v1.2 → v1.3 ✅ filed 2026-05-14 — `Architectural_Design_Document_v1_3.md`
     - Step 4: PRD v1.0.1 → v1.1 ✅ filed 2026-05-14 — `PRD_v1_1.md`
     - Step 5a: CP spec v1.2 → v1.3 ✅ filed 2026-05-14 — `Spec_Control_Plane_v1_3.md`
     - Step 5b: OD spec v1.2 → v1.3 ✅ filed 2026-05-14 — `Spec_Operational_Discipline_v1_3.md` (v2.2-new in closure_path)
     - Step 6a: CP plan v2.1 → v2.2 ✅ filed 2026-05-14 — this artifact
     - Step 6b: OD plan v2.1 → v2.2 ⏳ PENDING — `Implementation_Plan_Operational_Discipline_v2_2.md`
     - Close: F2-12 Closure Declaration ⏳ PENDING — `F2-12_Closure_Declaration.md`
   - `inheritance_sessions = [OD_PLAN_SESSION_4, CROSS_AXIS_COMPOSITION_SESSION_5]` (preserved at v2.2; inheritance closed at cascade Step 5a + 5b per CP spec v1.3 §24.4 + OD spec v1.3 §14.5).
   - **`active_at_v1 = false` (v2.2 amendment; was `true` at v2.1)** — closed at v2.2 by cascade execution.
   - **`closed_at_v2_2 = true` (v2.2 new)** — closure status declared.
   - **`closure_status = ✅ CLOSED` (v2.2 new)** — formal closure status at cascade Step 6a; cascade-close formal `closure_pending false` declaration deferred to `F2-12_Closure_Declaration.md`.
4. **F2-12 closure ✅ occurs at this CP plan v2.2 cascade Step 6a (v2.2 amendment)** — cascade close is at Step 6b (OD plan v2.2) + F2-12 Closure Declaration. The v2.1 acceptance #4 declared closure as "deferred to revision-pass mode — CP plan v1 declares the carry-forward; closure occurs at CP plan v2 after spec v1.3 ingests revised D1 + D6 + ADD + PRD"; v2.2 acceptance #4 declares closure ✅ realized at cascade Step 6a.
5. Spec §24.4 deferred-list items inherited at OD plan Session 4 + Composition Session 5: cross-spec citation strings, seam-versioning convention, F2-12 closure path verification, T-perm-3 boundary cross-axis composition checks. **At v2.2, F2-12 closure path verification ✅ complete (all six steps filed except cascade-close declaration).**
6. Manifest is **byte-exact** verbatim transcription of spec §24.2 + §24.3 + §24.4; addition, removal, or reordering requires Workflow §4.1.2 Class-2 C-CP-24 revision.
7. F2-12 closure path is **the only path** to close the carry-forward; partial closure (e.g., D1 v1.2 only) does not close the carry-forward per spec §24.4 closure invariant. **At v2.2, full closure achieved at cascade Step 6a per the closure-path-six-steps invariant.**
[8–12 preserved verbatim from v2.1.]

**Tests (v2.2 amendment).** Existing v2.1 tests preserved except as noted: `test_cross_axis_composition_manifest_cardinality_nine`, `test_per_composition_source_units_match_spec`, `test_session_targets_match_spec`, `test_surface_kind_discriminator_six_values`, `test_f2_12_active_engagement_at_u_cp_20`, `test_f2_12_closure_path_six_steps`, `test_f2_12_closure_path_step_1_d1_v1_2`, `test_f2_12_closure_path_step_5_cp_spec_v1_3`, `test_f2_12_closure_path_step_6_cp_plan_v2_revision_pass`, `test_f2_12_inheritance_at_session_4_and_5`, **`test_f2_12_active_at_v2_2_false` (v2.2 new; replaces `test_f2_12_active_at_v1`)**, `test_partial_closure_does_not_close`, `test_session_5_ingests_four_load_bearing_exports`, `test_session_4_ingests_five_load_bearing_exports`, `test_manifest_byte_exact`, `test_u_cp_55_terminal_no_within_axis_consumer`, **`test_f2_12_closed_at_v2_2_true` (v2.2 new)**, **`test_f2_12_closure_path_all_six_steps_filed` (v2.2 new)**, **`test_f2_12_closure_path_steps_2_through_5_present` (v2.2 new)**, **`test_f2_12_closure_status_closed` (v2.2 new)**.

**Rollback boundary.** [Preserved verbatim from v2.1; v2.2 additional impact: F2-12 closure declaration site dissolves; cascade Step 6a closure status regresses; OD plan v2.2 cross-axis substrate at U-OD-20 + U-OD-14 may lose alignment.]

---

## §3 Dependency graph + §4 Spec-traceability + §5 Persona linkage + §6 Cross-axis citation + §7 PRD-trace + §8 Forward-flagged concerns + §9 ADR-trace + §10 Anti-pattern audit

[All sections preserved verbatim from v2.1 except §8 forward-flagged concerns superseded entries — see §0.8 above for v2.2 disposition.]

---

## §[carry-forwards]

### [CF-1] F2-12 — D1 v1.1 → v1.2 + D6 v1.1 → v1.2 replay-trace-emission contract (✅ CLOSED at v2.2)

**Status (v2.2 amendment).** ✅ **CLOSED** at CP plan v2.2 filing per ADD v1.3 §6.3.1 cascade Step 6a row. Plan-level absorption at §1.4 F2-12 carry-forward declaration + U-CP-20 acceptance #5 closure + U-CP-21 4-attribute schema absorption + U-CP-55 acceptance #3 + #4 closure_path filed. Closure execution path table recorded at U-CP-55 acceptance #3. Cascade close at Step 6b (OD plan v2.2) + F2-12 Closure Declaration pending. Formal `closure_pending false` declaration deferred to `F2-12_Closure_Declaration.md` at cascade close.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_2.md` |
| Filing destination | `/mnt/user-data/outputs/Implementation_Plan_Control_Plane_v2_2.md` |
| Status | Proposed (pending F2-12 cascade close + OD-F212-5 P6-CK disposition) |
| Predecessor | `Implementation_Plan_Control_Plane_v2_1.md` (v1 → v2 → v2.1 baseline) |
| Substrate consumed | CP spec v1.3 + ADD v1.3 + ADR-D1 v1.2 + ADR-D6 v1.2 + PRD v1.1 + OD spec v1.3 (cross-axis reference only) |
| Successor | `Implementation_Plan_Operational_Discipline_v2_2.md` (F2-12 cascade Step 6b — cross-axis substrate consumer) |
| F2-12 closure status | ✅ CLOSED at cascade Step 6a (this artifact); cascade-close declaration pending |
| Workflow discipline | `Project_Workflow_v1_7.md` §7 fidelity-grammar |
| Date | 2026-05-14 |

*Filed at F2-12 cascade Step 6a close. U-CP-20 acceptance #5 F2-12 carry-forward → ✅ CLOSED; U-CP-21 3-attribute schema → 4-attribute schema canonically per CP spec v1.3 §9.1 + ADR-D1 v1.2 §1.1.1 (closes v2.1 §0.8 rows 1+2 forward-flagged concerns by substrate-driven absorption); U-CP-55 acceptance #3 closure_path filed all six cascade steps (Steps 1, 2a, 2b, 3, 4, 5a, 5b, 6a ✅; Step 6b + Close pending); U-CP-55 acceptance #4 closure declared at cascade Step 6a; §1.4 F2-12 carry-forward declaration → ✅ CLOSED. Cascade segment boundary per OD-F212-4.A; OD-F212-5 P6-CK disposition pending at Step 6 boundary. Recommended next cascade step: Step 6b (OD plan v2.2 revision pass) per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 — U-OD-14 cost-attribution-per-span unit + U-OD-20 closure_path tracker absorption against OD spec v1.3 §14.5.1–§14.5.4.*
