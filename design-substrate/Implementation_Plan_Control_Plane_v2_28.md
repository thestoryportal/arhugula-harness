# Implementation Plan — Control Plane (v2.28)

*Delta over v2.27. v2.28 authors **6 NEW atomic units U-CP-74 through U-CP-79** decomposing CP spec v1.24 → v1.25 NEW §16.5 CP→IS state-ledger emission contract per `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md` operator-ratified 2026-05-28 Q-set ((W/S)=S; Q1=Q1(b); Q3=Q3(a); Q4=Q4(b); Q5=Q5(a); Q6=Q6(a)). Unit count 74 → **80**; +6 NEW composer units at L4-within-axis (consume existing per-CP-source-unit modules at L3); ZERO new cluster (singleton-extensions at existing Clusters per source-unit module locality); ZERO DAG topology break; ZERO cross-axis cascade at this CP plan arc. CP spec v1.25 §16.5.10 reclassifies U-CP-12 + U-CP-52 as NOT-APPLICABLE at CP-side (declarative-only + runtime-axis-composed respectively) per impl-time grounding pass; ZERO atomic unit authored for those 2 surfaces.*

## §0 Change note (v2.27 → v2.28)

### §0.1 Revision context — 6 NEW composer atomic units per X-AL-3 spec extension

Per CP spec v1.24 → v1.25 NEW §16.5 CP→IS state-ledger emission contract authoring (Class 1 fork resolution Path A within-A Gap B (S) sibling-variant absorption per `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md` operator-ratified 2026-05-28 Q-set at within-Path-A AskUserQuestion): U-CP-74 through U-CP-79 decompose the harness-cp impl scope into 6 atomic units covering 1 sibling composer addition at U-CP-74 against existing U-CP-14 `per_step_override_evaluator` (load-bearing dual-emission landing + foundational shared `_canonicalize_outcome_bytes` helper co-publication) + 5 NEW greenfield composers at U-CP-75..79 (against U-CP-27 / U-CP-30 / U-CP-37 / U-CP-49 / U-CP-50 source units).

Trigger: U-RT-35 PARTIAL-LAND (1 of 17 spec §12.3 CP→IS edges wired at HEAD) Class 1 fork `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` RE-OPENED 2026-05-28 per harness deployment-readiness audit identifying this as the sole remaining deployment-blocker. Path A full Phase 6 back-flow authorized. Within Path A, Gap B (S)-sibling-variant ratified — preserves C-CP-16 §16.2 + C-CP-20 §20.4 verbatim per CP spec v1.7 §13.5.1 NOTE 3 hash-bytes-immutability discipline.

Mirror precedent: U-CP-34 `sibling_ledger_entry_composition` (Cluster 7 closure 2026-05-21) is the canonical CP→IS state-ledger composer shape — single LANDED §12.3 edge at U-RT-35 AC #1. The 6 NEW v2.28 composers replicate this shape across the 6 IMPL-MATERIALIZABLE source units per §16.5.2 enumeration; CP spec v1.25 §16.5.10 reclassifies the remaining 2 spec-§12.3 source units (U-CP-12 + U-CP-52) as not-applicable at CP-side per impl-time grounding pass.

### §0.2 Sections revised

§0 (this change note); NEW §2 unit bodies authoring at U-CP-74 through U-CP-79 (full template per CP plan v2.15 §2 pattern × 6 units). All other unit bodies preserved verbatim from v2.27 per delta-only-plan-chain convention.

### §0.3 NEW units U-CP-74 through U-CP-79 — CP→IS state-ledger emission composers

See §2 for full unit bodies. Summary:

| Unit | Source-unit module | Composer function | Parent existing unit (L3) | Notes |
|---|---|---|---|---|
| U-CP-74 | `per_step_override_evaluator.py` (sibling to existing `emit_override_audit_entry` at line 200) | `emit_override_state_ledger_entry` | U-CP-14 | Foundational; co-publishes NEW shared `state_ledger_canonicalization.py` helper |
| U-CP-75 | `workload_binding_engine_class_selection.py` (against `select_engine_class` at line 142) | `emit_workload_class_selection_state_ledger_entry` | U-CP-27 | |
| U-CP-76 | `pause_resume_protocol.py` (`PauseResumeProtocol` class methods at line 214+) | `emit_pause_resume_state_ledger_entry` | U-CP-30 | Workflow-layer per CP spec v1.11 §26 NEW NOTE; distinct from engine-layer at U-CP-78/79 |
| U-CP-77 | `hitl_as_tool_call_rewriting.py` (against `rewrite_tool_call_to_hitl` at line 149) | `emit_hitl_tool_call_rewriting_state_ledger_entry` | U-CP-37 | |
| U-CP-78 | `pause_resume_protocol.py` (engine-layer free function `capture_pause_snapshot` at line 106) | `emit_pause_captured_state_ledger_entry` | U-CP-49 | Engine-layer per CP spec v1.11 §26 NEW NOTE |
| U-CP-79 | `pause_resume_protocol.py` (engine-layer free function `attempt_resume` at line 128) | `emit_resume_attempted_state_ledger_entry` | U-CP-50 | Engine-layer per CP spec v1.11 §26 NEW NOTE |

**Cluster placement:** Singleton-extensions at existing Clusters per source-unit module locality. Each NEW unit sits at L4-within-axis depending on its parent source-unit at L3 + the IS-axis HEAD callable surface at IS-axis. NO new cluster created — pattern mirrors U-CP-73 singleton-extension at Cluster 10 (v2.27).

**Two spec-§12.3 source units reclassified as NOT-APPLICABLE at v2.28 per CP spec v1.25 §16.5.10:**

- **U-CP-12** `per_class_attribute_composition.py` — DECLARATIVE-ONLY module (static `PER_CLASS_ATTRIBUTE_SETS` tuple per C-CP-05 §5.2 + helper `required_attributes_for(...)`). NO runtime composer-action moment for state-ledger emission. ZERO atomic unit authored.
- **U-CP-52** `hitl_placement.py` — RUNTIME-AXIS-COMPOSED (canonical §17.4 `hitl_gate(...)` signature at line 205 raises `NotImplementedError`; production gate body composed at runtime-side `RuntimeHITLGateComposer` per C-RT-18 §14.8). Future runtime-plan revision authoring `emit_hitl_gate_state_ledger_entry` at runtime composer site is the canonical path. ZERO CP-axis atomic unit authored at v2.28.

### §0.4 Cross-axis dependency edges — preserved + 6 NEW intra-axis composer-to-source-unit edges

NEW units U-CP-74 through U-CP-79 cross-axis edges: each composer's `ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]` kw-only parameter is bound at runtime composition time to `ctx.ledger_writer.append_ledger_entry` (the IS-axis HEAD callable surface). This is a CP→IS edge at runtime spec §12.3 (canonical 17-edge enumeration; 1 LANDED at U-CP-34 → U-IS-11; 6 wired by these 6 v2.28 units + the runtime-wiring units at separate runtime-plan arc; 2 carried as canonical-but-not-CP-materializable per CP spec v1.25 §16.5.10).

CXA v2.15 → v2.16 §0.4 tracking-marker for §2.3.2 CP→IS bucket OWED — separate arc (NOT amended at this CP plan v2.28 arc per single-focus-arc scope per FM-2). Tracking-marker enumerates 6 pending events.

ZERO new CP→AS edges; ZERO new CP→OD edges; ZERO OD→CP edges. C-CP-16 §16.2 CPAuditLedgerEntry → OD AuditLedgerEntry edge at v1.7 §13.5.1 cp_audit_to_od_audit converter unchanged.

### §0.5 DAG topology — additive at L4-within-axis × 6 NEW units

Each NEW unit sits at L4-within-axis at its source-unit module's owning cluster. DAG verified Kahn-acyclic across all 6 insertions. U-CP-74 introduces shared `_canonicalize_outcome_bytes` helper at NEW `state_ledger_canonicalization.py`; U-CP-75 through U-CP-79 depend on U-CP-74 for the shared helper (intra-axis dependency edge; no cross-axis edge).

DAG verified acyclic at all 6 insertions: each NEW unit consumes its parent source-unit at L3 + the IS-axis HEAD callable surface; no back-edge to higher CP layers; no inversion at any existing consumer of the parent source-unit (existing consumers preserved verbatim per the additive-composer-emission discipline).

### §0.6 Status posture

Proposed (v2.27) → **Proposed (v2.28)**. v2.28 is a multi-unit-authoring delta. CP-axis unit count 74 → 80. The CP plan v2.28 is the load-bearing CP-axis delivery for U-RT-35 PARTIAL → RETIRE-READY gating; landing all 6 v2.28 units + runtime-side wiring at separate runtime-plan arc covers the 6 CP-materializable §12.3 edges. The 2 not-applicable surfaces (U-CP-12 + U-CP-52) per §16.5.10 do NOT contribute to U-RT-35 RETIRE-READY gating at CP-axis side; runtime spec §12.3 canonical-vs-materialized differential resolution is deferred.

### §0.7 Adjacent defects surfaced (not patched per FM-2)

(i) **CXA v2.15 → v2.16 §0.4 forward-tracking marker for §2.3.2 CP→IS bucket OWED at separate arc.** Tracking-marker enumerates 6 pending events (1 per v2.28 NEW composer atomic unit). NOT patched at v2.28 per FM-2 single-focus-arc scope.

(ii) **Runtime plan revision-pass OWED at separate arc.** v2.28 publishes the CP-side composer-authoring units; the runtime-side factory-binding extensions are owed at runtime plan revision authoring 6 NEW runtime-wiring units for each composer's materialize-stage helper at `harness-runtime/src/harness_runtime/lifecycle/`. Separate arc; co-publication NOT bundled at v2.28 (different role discipline — implementation-planner authors plan; runtime-plan revision is parallel arc).

(iii) **Gap C runtime spec §12.3 callable-signature drift NOT patched.** Per fork doc Class 3 informational; per CP spec v1.25 Q4(b) ratification, composers produce EntryPayload matching IS HEAD `Callable[[EntryPayload], WriteResult]`; runtime spec §12.3 prose alignment (`StateLedgerEntry` → `EntryPayload`; `EntryHash` → `WriteResult`) deferred. Co-deferred: §12.3 17-vs-7 canonical-vs-materializable differential per CP spec v1.25 §16.5.10.

(iv) **Future runtime-plan U-RT-NEW for `emit_hitl_gate_state_ledger_entry` at runtime-side `RuntimeHITLGateComposer`.** Per CP spec v1.25 §16.5.10 U-CP-52 reclassification, HITL gate state-ledger emission is architecturally a runtime-axis concern. Future runtime-plan revision should author this composer at the runtime composer site. NOT in scope at v2.28.

### §0.8 Downstream absorption owed (post-v2.28)

(a) Workspace `CLAUDE.md` §2.4 CP plan row bump (v2.27 → v2.28). **OWED at Phase 6 close commit.**
(b) CXA v2.15 → v2.16 §0.4 tracking-marker. Separate arc post-v2.28.
(c) Runtime plan revision-pass authoring 6 NEW runtime-wiring units for the per-composer materialize-stage helpers. Separate arc; blocks on v2.28 filing.
(d) Per-CP-unit harness-cp impl + tests landings (Phase 7 7b atomic-unit consumption arcs). Each unit lands independently per ledger-stream cadence; U-RT-35 RETIRE-READY transit at full CP-materializable 6-edge wired + runtime-side composer landings.
(e) `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` annotation owed at each per-CP-unit landing per fork-doc closure-back-reference discipline.

---

## §1 — Cross-arc note (X-AL-3 spec extension via Class 1 fork RE-OPEN)

This arc IS the X-AL-3 spec-extension absorption arc for the Class 1 fork `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` RE-OPENED 2026-05-28 + the architect recommendation at `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md` operator-ratified Q-set. The fork doc enumerates the alternative routings (Path B per-CP-unit re-land; Path C re-classify §12.3 to enumerate only materialized edges) declined at Option A authorization. The architect recommendation enumerates the alternative within-Path-A pattern (W) widen CPAuditLedgerEntry declined at (S) ratification per CP-signed-bytes-immutability discipline. Impl-time grounding pass against `harness-cp/src/harness_cp/` HEAD identified 2 NOT-APPLICABLE source units (U-CP-12 declarative-only; U-CP-52 runtime-axis-composed) absorbed at CP spec v1.25 §16.5.10 + this plan v2.28.

The fork doc §"Routing options" enumerates the full downstream cascade absorbed at this arc:

| Layer | Status at v2.28 co-publication |
|---|---|
| CP spec v1.24 → v1.25 NEW §16.5 (6 composer contracts + 2 not-applicable reclassifications) | **Co-published** at this arc |
| CP plan v2.27 → v2.28 NEW U-CP-74..79 | **THIS arc** |
| Runtime spec | ZERO change in this revision (Gap C deferred; canonical-vs-materialized differential deferred) |
| Runtime plan revision authoring 6 per-composer materialize-stage helpers + future `emit_hitl_gate_state_ledger_entry` at runtime composer | **OWED separate arc** post-v2.28 |
| OD spec / OD plan / OD impl | ZERO change |
| AS spec / AS plan / AS impl | ZERO change |
| IS spec / IS plan / IS impl | ZERO change (composers match IS HEAD callable shape) |
| harness-cp impl × 6 composer modules | **OWED Phase 7 7b consumption arcs** post-v2.28 |
| harness-cp tests × 6 composer test modules | **OWED Phase 7 7b consumption arcs** post-v2.28 |
| CXA v2.15 → v2.16 §0.4 tracking-marker (6 pending events) | **OWED separate arc** post-v2.28 |
| Workspace `CLAUDE.md` §2.4 CP plan row bump | **OWED at Phase 6 close commit** |
| `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` closure-back-reference annotations | **OWED per-unit landings** |
| Per-CP-unit retirement event filings | **OWED per-unit landings** at Phase 7 7b cadence |

---

## §2 — NEW unit bodies — U-CP-74 through U-CP-79

### U-CP-74 — emit_override_state_ledger_entry sibling composer at U-CP-14 + shared `_canonicalize_outcome_bytes` helper

- **Implements:** CP spec v1.25 §16.5.2 row U-CP-14 + §16.5.3 EntryPayload composition + §16.5.4 idempotency-key formula + §16.5.5 response-hash recipe + §16.5.6 dual-emission discipline + §16.5.7 firing-site discipline
- **Files:** `harness-cp/src/harness_cp/per_step_override_evaluator.py` (EXTEND — add sibling composer; existing `emit_override_audit_entry` at line 200 preserved verbatim) + `harness-cp/src/harness_cp/state_ledger_canonicalization.py` (NEW — shared `_canonicalize_outcome_bytes` helper) + `harness-cp/tests/test_override_state_ledger_emission.py` (NEW) + `harness-cp/tests/test_state_ledger_canonicalization.py` (NEW)
- **Signatures:** `async def emit_override_state_ledger_entry(*, workflow_id: str, step_id: str, override_id: str, policy_id: str, post_override_step_config: Mapping[str, Any], actor: ActorIdentity, ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]) -> WriteResult`; existing `emit_override_audit_entry(...) -> CPAuditLedgerEntry` signature unchanged; NEW `def _canonicalize_outcome_bytes(payload: BaseModel | Mapping[str, Any]) -> bytes` shared helper
- **Depends on:** [U-CP-14] (Cluster L3 source) + IS-axis HEAD callable surface
- **ACs:**
  1. `action_id = "cp.per-step-override-application"` per §16.5.3
  2. Idempotency-key per §16.5.4 row U-CP-14 Q1(b): `workflow_id || step_id || override_id || policy_id` with 0x1E record-separator + SHA-256 hex-64
  3. Response-hash per §16.5.5 row U-CP-14 over post-override step-config canonical JSON bytes via `_canonicalize_outcome_bytes`
  4. Actor field direct re-use from input `ActorIdentity` per §16.5.3 Q2 ratification
  5. Sibling composer ADDITIVE — existing `emit_override_audit_entry` at line 200 preserved verbatim per §16.5.6; the existing firing site at `resolve_step_binding:179` invokes BOTH composers per dual-emission discipline
  6. Dual-emission order-independent per §16.5.9 invariant 6; neither composer conditions on the other's return value
  7. ZERO change to `CPAuditLedgerEntry` C-CP-16 §16.2 8-field shape; ZERO change to C-CP-20 §20.4 signing contract; ZERO change to v1.7 §13.5.1 cp_audit_to_od_audit converter
  8. `_canonicalize_outcome_bytes` helper: sorted keys, `(",", ":")` separators, UTF-8 encode, NaN/Infinity rejection per §16.5.5 + ECMA-404
  9. Composer awaits `ledger_writer(payload)` return; does NOT condition on `WriteResult` variant per §16.5.9 invariant 4
- **Tests:** `test_emit_override_state_ledger_action_id`, `test_emit_override_state_ledger_idempotency_key_per_q1b`, `test_emit_override_state_ledger_response_hash_over_post_override_config`, `test_emit_override_state_ledger_orthogonal_to_audit_emission`, `test_emit_override_state_ledger_dual_emission_order_independent`, `test_emit_override_audit_entry_preserved_verbatim_byte_identical`, `test_cp_audit_ledger_entry_shape_unchanged_at_v1_25`, `test_cp_signed_audit_ledger_entry_signing_contract_unchanged`, `test_canonicalize_outcome_bytes_sorted_keys_deterministic`, `test_canonicalize_outcome_bytes_rejects_nan_infinity`

### U-CP-75 — emit_workload_class_selection_state_ledger_entry composer

- **Implements:** CP spec v1.25 §16.5.2 row U-CP-27 + §16.5.3 / §16.5.4 / §16.5.5 / §16.5.7
- **Files:** `harness-cp/src/harness_cp/workload_binding_engine_class_selection.py` (EXTEND) + `harness-cp/tests/test_workload_class_selection_state_ledger_emission.py` (NEW)
- **Signatures:** `async def emit_workload_class_selection_state_ledger_entry(*, workflow_id: str, step_id: str, selection_result: WorkloadBindingSelectionResult, actor: ActorIdentity, ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]) -> WriteResult`
- **Depends on:** [U-CP-27, U-CP-74] (Cluster L3 source `select_engine_class` at line 142 + U-CP-74 for shared `_canonicalize_outcome_bytes` helper)
- **ACs:**
  1. `action_id = "cp.workload-binding-class-selection"`
  2. Idempotency-key per §16.5.4 row U-CP-27: `workflow_id || step_id || selection_result.engine_class_id || _canonicalize_outcome_bytes(selection_result)`-derived bytes (canonical-form discipline)
  3. Response-hash over `WorkloadBindingSelectionResult` canonical JSON bytes (resolved class binding + rationale)
  4. Fires AFTER `select_engine_class(...)` at line 142 resolves; BEFORE returning the `WorkloadBindingSelectionResult` to caller
  5. ZERO `CPAuditLedgerEntry` emission per §16.5.9 invariant 5
  6. Reuses `_canonicalize_outcome_bytes` helper from U-CP-74
- **Tests:** `test_emit_workload_class_selection_action_id`, `test_emit_workload_class_selection_idempotency_key_includes_engine_class_id`, `test_emit_workload_class_selection_fires_post_resolve_pre_return`, `test_emit_workload_class_selection_response_hash_over_selection_result`, `test_emit_workload_class_selection_zero_cp_audit_emission`, `test_emit_workload_class_selection_idempotent_replay`

### U-CP-76 — emit_pause_resume_state_ledger_entry composer at workflow-layer `PauseResumeProtocol` class

- **Implements:** CP spec v1.25 §16.5.2 row U-CP-30 + §16.5.3 / §16.5.4 / §16.5.5 / §16.5.7
- **Files:** `harness-cp/src/harness_cp/pause_resume_protocol.py` (EXTEND at `PauseResumeProtocol` class methods at line 214+) + `harness-cp/tests/test_pause_resume_workflow_layer_state_ledger_emission.py` (NEW)
- **Signatures:** `async def emit_pause_resume_state_ledger_entry(*, workflow_id: str, step_id: str, protocol_event_kind: PauseResumeProtocolEventKind, event_sequence_id: int, protocol_state_snapshot: Mapping[str, Any], actor: ActorIdentity, ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]) -> WriteResult`; NEW enum `PauseResumeProtocolEventKind` at module top-level discriminating workflow-layer protocol transitions
- **Depends on:** [U-CP-30, U-CP-74] (Cluster L3 source `PauseResumeProtocol` class + U-CP-74 helper)
- **ACs:**
  1. `action_id = "cp.pause-resume-protocol"`
  2. Idempotency-key per §16.5.4 row U-CP-30: `workflow_id || step_id || protocol_event_kind || event_sequence_id`
  3. Fires at workflow-layer protocol-class method invocations per §16.5.7 (distinct from engine-layer at U-CP-78/79); `protocol_event_kind` discriminates the transition
  4. Response-hash over protocol-state-transition outcome canonical JSON bytes
  5. ZERO `CPAuditLedgerEntry` emission; orthogonal to U-CP-78/U-CP-79 engine-layer emissions per CP spec v1.11 §26 NEW NOTE 2-layer coexistence
  6. Reuses `_canonicalize_outcome_bytes` helper from U-CP-74
- **Tests:** `test_emit_pause_resume_workflow_layer_action_id`, `test_emit_pause_resume_idempotency_key_includes_event_kind`, `test_emit_pause_resume_fires_at_workflow_layer_protocol_transitions`, `test_emit_pause_resume_zero_cp_audit_emission`, `test_emit_pause_resume_orthogonal_to_engine_layer_at_u_cp_78_u_cp_79`, `test_pause_resume_protocol_event_kind_enum_exhaustive`

### U-CP-77 — emit_hitl_tool_call_rewriting_state_ledger_entry composer

- **Implements:** CP spec v1.25 §16.5.2 row U-CP-37 + §16.5.3 / §16.5.4 / §16.5.5 / §16.5.7
- **Files:** `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py` (EXTEND) + `harness-cp/tests/test_hitl_tool_call_rewriting_state_ledger_emission.py` (NEW)
- **Signatures:** `async def emit_hitl_tool_call_rewriting_state_ledger_entry(*, workflow_id: str, step_id: str, tool_call_id: str, semantic_variant_binding_id: str, rewritten_tool_call: RewrittenToolCall, actor: ActorIdentity, ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]) -> WriteResult`
- **Depends on:** [U-CP-37, U-CP-74] (Cluster L3 source `rewrite_tool_call_to_hitl` at line 149 + U-CP-74 helper)
- **ACs:**
  1. `action_id = "cp.hitl-tool-call-rewriting"`
  2. Idempotency-key per §16.5.4 row U-CP-37: `workflow_id || step_id || tool_call_id || semantic_variant_binding_id`
  3. Fires AFTER `rewrite_tool_call_to_hitl(...)` at line 149 produces `RewrittenToolCall`; BEFORE returning the rewritten call
  4. Response-hash over `RewrittenToolCall` canonical JSON bytes (impl line 109)
  5. ZERO `CPAuditLedgerEntry` emission
  6. Reuses `_canonicalize_outcome_bytes` helper from U-CP-74
- **Tests:** `test_emit_hitl_rewriting_action_id`, `test_emit_hitl_rewriting_idempotency_key_includes_semantic_variant_binding_id`, `test_emit_hitl_rewriting_fires_post_rewrite_pre_return`, `test_emit_hitl_rewriting_response_hash_over_rewritten_tool_call`, `test_emit_hitl_rewriting_zero_cp_audit_emission`

### U-CP-78 — emit_pause_captured_state_ledger_entry composer at engine-layer `capture_pause_snapshot`

- **Implements:** CP spec v1.25 §16.5.2 row U-CP-49 + §16.5.3 / §16.5.4 / §16.5.5 / §16.5.7
- **Files:** `harness-cp/src/harness_cp/pause_resume_protocol.py` (EXTEND at engine-layer free function `capture_pause_snapshot` at line 106) + `harness-cp/tests/test_pause_captured_engine_layer_state_ledger_emission.py` (NEW)
- **Signatures:** `async def emit_pause_captured_state_ledger_entry(*, workflow_id: str, step_id: str, pause_event_id: str, pause_snapshot: PauseSnapshot, actor: ActorIdentity, ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]) -> WriteResult`
- **Depends on:** [U-CP-49, U-CP-74] (Cluster L3 source `capture_pause_snapshot` at line 106 + U-CP-74 helper)
- **ACs:**
  1. `action_id = "cp.pause-captured"`
  2. Idempotency-key per §16.5.4 row U-CP-49: `workflow_id || step_id || pause_event_id || pause_snapshot.snapshot_hash` (snapshot_hash per impl line 230 sha256 hex over canonical JSON of `(workflow_id + run_id + step_index + state_summary)`)
  3. Fires AFTER `capture_pause_snapshot(...)` returns the `PauseSnapshot`; BEFORE returning the snapshot to caller
  4. Response-hash over `PauseSnapshot` canonical JSON bytes (impl line 46)
  5. ZERO `CPAuditLedgerEntry` emission; orthogonal to U-CP-76 workflow-layer emission per CP spec v1.11 §26 NEW NOTE 2-layer coexistence
  6. Reuses `_canonicalize_outcome_bytes` helper from U-CP-74
- **Tests:** `test_emit_pause_captured_action_id`, `test_emit_pause_captured_idempotency_key_includes_snapshot_hash`, `test_emit_pause_captured_fires_post_capture_pre_return`, `test_emit_pause_captured_response_hash_over_pause_snapshot`, `test_emit_pause_captured_zero_cp_audit_emission`, `test_emit_pause_captured_engine_layer_orthogonal_to_workflow_layer_at_u_cp_76`

### U-CP-79 — emit_resume_attempted_state_ledger_entry composer at engine-layer `attempt_resume`

- **Implements:** CP spec v1.25 §16.5.2 row U-CP-50 + §16.5.3 / §16.5.4 / §16.5.5 / §16.5.7
- **Files:** `harness-cp/src/harness_cp/pause_resume_protocol.py` (EXTEND at engine-layer free function `attempt_resume` at line 128) + `harness-cp/tests/test_resume_attempted_engine_layer_state_ledger_emission.py` (NEW)
- **Signatures:** `async def emit_resume_attempted_state_ledger_entry(*, workflow_id: str, step_id: str, resume_event_id: str, resume_attempt_count: int, resume_outcome: ResumeOutcome, actor: ActorIdentity, ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]) -> WriteResult`
- **Depends on:** [U-CP-50, U-CP-74] (Cluster L3 source `attempt_resume` at line 128 + U-CP-74 helper)
- **ACs:**
  1. `action_id = "cp.resume-attempted"`
  2. Idempotency-key per §16.5.4 row U-CP-50: `workflow_id || step_id || resume_event_id || resume_attempt_count` (attempt_count discriminates retry attempts at same resume_event_id per `ResumeAttempt` impl line 63)
  3. Fires AFTER `attempt_resume(...)` resolves the `ResumeOutcome` (per impl line 91; success OR failure outcome); BEFORE returning the outcome to caller
  4. Response-hash over `ResumeOutcome` canonical JSON bytes (impl line 91 — includes `ResumeOutcomeKind` + resumed state)
  5. ZERO `CPAuditLedgerEntry` emission; orthogonal to U-CP-76 workflow-layer emission
  6. Fires at BOTH success and failure outcomes (failure is a recorded outcome via `ResumeOutcome.kind = FAILURE`, not a swallowed exception)
  7. Reuses `_canonicalize_outcome_bytes` helper from U-CP-74
- **Tests:** `test_emit_resume_attempted_action_id`, `test_emit_resume_attempted_idempotency_key_includes_attempt_count`, `test_emit_resume_attempted_fires_on_success`, `test_emit_resume_attempted_fires_on_failure`, `test_emit_resume_attempted_response_hash_over_resume_outcome`, `test_emit_resume_attempted_zero_cp_audit_emission`, `test_emit_resume_attempted_engine_layer_orthogonal_to_workflow_layer_at_u_cp_76`

---

## §3 — DAG topology delta (v2.27 → v2.28)

6 NEW units at U-CP-74 through U-CP-79 added at L4-within-axis across existing clusters. Topological sort acyclic. Each NEW unit consumes its parent source-unit at L3 + the IS-axis HEAD callable surface at runtime composition time; no back-edge to higher CP layers; no inversion at any existing consumer.

U-CP-74 introduces shared `_canonicalize_outcome_bytes` helper at NEW `state_ledger_canonicalization.py` module; U-CP-75 through U-CP-79 depend on U-CP-74 in addition to their parent source-unit. Helper dependency edge is intra-axis CP; introduces no cross-axis edge.

Cross-axis edges at U-CP-74 through U-CP-79: each composer's `ledger_writer` kw-only parameter binds at runtime composition time to IS-axis HEAD callable — this is a CP→IS edge at runtime spec §12.3 canonical 17-edge enumeration. Per §0.4: ZERO new CP→AS / CP→OD / OD→CP edges; CP→IS bucket cardinality grows by 6 wired-at-CP-plan-v2.28 edges (plus 6 wired-at-runtime-plan = 12; combined with 1 LANDED at U-CP-34 = 7 of 17 §12.3 spec-declared edges, with the remaining 10 = 2 not-applicable per CP spec v1.25 §16.5.10 + 8 declared but documented Gap C canonical-vs-materialized differential awaiting runtime spec revision).

DAG verified Kahn-acyclic; 6 NEW units consumed at L4 across existing clusters; ∅ remaining unresolved edges within CP-axis.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_28.md` |
| Version | v2.28 |
| Filing event | 6 NEW atomic units U-CP-74 through U-CP-79 authoring per CP spec v1.25 NEW §16.5 CP→IS state-ledger emission contract (6 composers + 2 not-applicable reclassifications at U-CP-12 + U-CP-52); Class 1 fork resolution Path A within-A Gap B (S) sibling-variant absorption per `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` RE-OPEN + `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md` operator-ratified 2026-05-28 Q-set. Impl-time grounding pass against `harness-cp/src/harness_cp/` HEAD identified 2 NOT-APPLICABLE source units + 3 naming mismatches (U-CP-27/37/49) corrected. 2026-05-28 |
| Predecessor | `Implementation_Plan_Control_Plane_v2_27.md` (preserved verbatim outside the §0 + §2 amendments at v2.28) |
| Successor | (none — current canonical) |
| Unit count | 74 → **80** (+6 NEW units U-CP-74 through U-CP-79) |
| DAG topology | Extended per §3 (L4-within-axis × existing-clusters; singleton-extensions; NO new cluster; DAG Kahn-acyclic; U-CP-75..79 depend on U-CP-74 for shared helper) |
| AC count delta | +37 NEW ACs across U-CP-74..79 (10 ACs at U-CP-74 + 5-7 ACs × 5 mid-units) |
| Cross-axis cascade | ZERO at CP plan v2.28 arc (CXA tracking-marker at separate CXA v2.16 arc; runtime-side wiring at separate runtime-plan arc) |
| Not-applicable reclassifications | U-CP-12 (declarative-only) + U-CP-52 (runtime-axis-composed) per CP spec v1.25 §16.5.10 impl-time grounding pass |
| H_T-RT-35 status | PARTIAL → RETIRE-READY transit GATED on full 6-CP-materializable-edge wired at runtime composition time (6 v2.28 composers + runtime-side materialize-stage helpers at separate runtime-plan arc) per `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` Option A close discipline + Gap C canonical-vs-materialized differential resolution at runtime spec revision |
| Operator authority | `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md` Q-set ratification 2026-05-28 ((W/S)=S sibling-variant; Q1=Q1(b); Q2=direct-reuse; Q3=Q3(a); Q4=Q4(b); Q5=Q5(a); Q6=Q6(a)) + impl-time grounding pass ratification at AskUserQuestion 2026-05-28 (drop U-CP-12 + U-CP-52; force-push revised PR #37) + parent fork doc Option A authorization |
