# Implementation Plan: Control Plane — v2.29 (delta over v2.28)

---

## §0 — Change-note (v2.28 → v2.29)

**Scope of revision.** Surgical cascade at v2.28 §2 NEW unit bodies U-CP-74 through U-CP-79 absorbing CP spec v1.25 → v1.26 β.i amendment (commit `ec4a2f7`; PR #38). Per `Spec_Control_Plane_v1_26.md` §16.5.3 (REWRITES EntryPayload field set to actual IS HEAD `(action_id, idempotency_key, actor, timestamp)`) + §16.5.4 (APPENDS `|| sha256(outcome_canonical_bytes).hex()` to idempotency_key formulas per row per Q-β.i-1(a)) + §16.5.5 (REFRAMES chapeau: outcome-bytes scheme consumed by idempotency_key derivation NOT by response_hash field per Q-β.i-3(b)) + §16.5.8 + §16.5.9 invariant 2 updates: each of U-CP-74..79 unit bodies revises **AC #2 (idempotency_key formula — adds outcome-hash suffix segment)** + **AC #3 (response_hash semantic — composer does NOT control response_hash; IS-internal per C-IS-06 §6.2; outcome-bytes consumed at idempotency_key per §16.5.4)** + **`Implements:` citation refresh to spec v1.26** + **tests list rename at the response_hash-test entry**. All other ACs preserved verbatim. All other unit-body fields (Files, Signatures outer shape, Depends on, helper acceptance at U-CP-74 AC #8, dual-emission discipline at U-CP-74 AC #5/#6, ZERO-CP-audit invariant at U-CP-75..79 AC #5, composer-await discipline at U-CP-74 AC #9) preserved verbatim.

**Trigger.** First 7b consumption attempt against v2.28 design substrate (PR #37 merge `e6c2f2c` 2026-05-29) surfaced nested Class 1 fork `.harness/class_1_tension_u_cp_74_entrypayload_field_set_drift.md` at U-CP-74 pre-substantive — v2.28 §2 unit bodies cite v1.25 §16.5.3 4-field EntryPayload + v1.25 §16.5.5 composer-supplied response_hash, both of which mis-declared IS HEAD shape per `harness-is/src/harness_is/state_ledger_write.py:62-75` + `entry_hash.py:73`. PR #38 routing-doc filed; operator authorized A) Phase 5 + 6 design phase route + β.i resolution + Q-β.i-1(a) append + Q-β.i-3(b) reframe at AskUserQuestion 2026-05-29. Spec v1.26 absorbs β.i at commit `ec4a2f7`. This plan v2.29 cascade absorbs the spec-side amendment into the cited unit bodies.

**v2.28 substantive content preserved verbatim except for the scoped AC #2 + AC #3 + `Implements:` citation refresh + tests list rename at U-CP-74..79 unit bodies below.** v2.28 §0 change-note + §0.3 NEW units table + §0.4 CXA edge-tracking + §0.5–§0.8 + §1 (composer enumeration prose) + §3 DAG topology + Filing footer ALL PRESERVED VERBATIM at v2.29 by reference. v2.27 + earlier substantive content preserved verbatim per delta-only-plan-chain convention.

**ZERO DAG topology change.** U-CP-74..79 dependency edges preserved verbatim per v2.28 §3 + §0.3 Cluster L4 within-axis dependency table. U-CP-74 still publishes shared `_canonicalize_outcome_bytes` helper at NEW `state_ledger_canonicalization.py`; U-CP-75..79 still depend on U-CP-74 for the shared helper. Helper signature + role at v2.29 preserved verbatim — the bytes the helper produces are consumed by idempotency_key derivation per spec v1.26 §16.5.4 rather than by response_hash field; the helper itself is unchanged.

**ZERO cross-axis cascade.** CXA v2.16 UNCHANGED at v2.29. IS plan / IS spec UNCHANGED. OD plan / OD spec UNCHANGED. AS plan / AS spec UNCHANGED. Runtime plan UNCHANGED (runtime spec §12.3 Gap C deferred per spec v1.26 §2(a)).

**ZERO new units / ZERO removed units / ZERO outer signature shape change.** U-CP-74..79 retain `async def emit_X_state_ledger_entry(*, ..., ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]) -> WriteResult` signatures — `EntryPayload` now refers to IS HEAD's actual 4-field shape per spec v1.26 §16.5.3 (was misdeclared at v1.25 + v2.28 §2). Composer-internal logic at AC #2 and AC #3 absorbs the cascade; outer signature surface unchanged.

**Co-publication this arc.** CP spec v1.26 (commit `ec4a2f7`); workspace CLAUDE.md row 79 (commit `ec4a2f7`). Closure-back-references at nested fork doc + parent fork doc + PR #38 merge owed.

---

## §1 — Revised unit bodies — U-CP-74 through U-CP-79 (cascade scope only; preserve-verbatim sections referenced)

The amendments below REPLACE the cited v2.28 §2 ACs + `Implements:` + tests-list entries verbatim. All other v2.28 §2 unit-body fields (Files, Signatures outer shape, Depends on, untouched ACs, untouched test entries) PRESERVED VERBATIM at v2.29 by reference.

### U-CP-74 — emit_override_state_ledger_entry sibling composer at U-CP-14 + shared `_canonicalize_outcome_bytes` helper (CASCADE)

**Implements (REPLACES v2.28 U-CP-74 Implements):** CP spec v1.26 §16.5.2 row U-CP-14 + §16.5.3 EntryPayload composition (4-field shape per IS HEAD `(action_id, idempotency_key, actor, timestamp)`) + §16.5.4 idempotency-key formula at v1.26 (per-composer disambiguator + outcome-hash suffix) + §16.5.5 outcome-bytes recipe consumed by idempotency_key derivation per §16.5.4 + §16.5.6 dual-emission discipline + §16.5.7 firing-site discipline + §16.5.8 Q4 attribution (composer supplies EntryPayload's 4 fields; IS computes response_hash + prior_event_hash internally).

**AC #2 (REPLACES v2.28 U-CP-74 AC #2):** Idempotency-key per CP spec v1.26 §16.5.4 row U-CP-14: canonical bytes are `workflow_id || step_id || override_id || policy_id || sha256(outcome_canonical_bytes).hex()` with 0x1E record-separator + SHA-256 hex-64. The outcome-hash suffix is computed at composer-call site over post-override step-config canonical JSON bytes via the shared `_canonicalize_outcome_bytes` helper (this unit's NEW module; AC #8 below). v2.28 disambiguator segments (`workflow_id`, `step_id`, `override_id`, `policy_id`) preserved verbatim per Q-β.i-1(a); the outcome-hash suffix segment is added per Q-β.i-1(a).

**AC #3 (REPLACES v2.28 U-CP-74 AC #3):** `response_hash` is IS-internal per C-IS-06 §6.2 — composer does NOT control it. IS computes `response_hash = SHA-256(canonicalize(entry))` over the entry's own canonical form at `append_ledger_entry` per `harness-is/src/harness_is/entry_hash.py:73`. The outcome-bytes recipe at CP spec v1.26 §16.5.5 row U-CP-14 (post-override step-config canonical JSON bytes) is consumed by AC #2 idempotency_key derivation per CP spec v1.26 §16.5.4, NOT by `response_hash` field. The shared `_canonicalize_outcome_bytes` helper (AC #8) is the producer of the outcome canonical bytes that AC #2 consumes.

**AC #1, AC #4, AC #5, AC #6, AC #7, AC #8, AC #9 (PRESERVED VERBATIM from v2.28):** v2.28 ACs at these row positions preserved verbatim — `action_id` value, actor direct re-use, sibling-composer ADDITIVE discipline, dual-emission order-independence, ZERO change to CPAuditLedgerEntry + C-CP-20 §20.4 + v1.7 §13.5.1 converter, `_canonicalize_outcome_bytes` helper acceptance (sorted keys + `(",", ":")` separators + UTF-8 + NaN/Infinity rejection per spec v1.26 §16.5.5 + ECMA-404), and composer-awaits-`ledger_writer` discipline per spec v1.26 §16.5.9 invariant 4.

**Files (PRESERVED VERBATIM from v2.28):** `harness-cp/src/harness_cp/per_step_override_evaluator.py` (EXTEND) + `harness-cp/src/harness_cp/state_ledger_canonicalization.py` (NEW) + `harness-cp/tests/test_override_state_ledger_emission.py` (NEW) + `harness-cp/tests/test_state_ledger_canonicalization.py` (NEW).

**Signatures (PRESERVED VERBATIM from v2.28 at outer surface):** `async def emit_override_state_ledger_entry(*, workflow_id: str, step_id: str, override_id: str, policy_id: str, post_override_step_config: Mapping[str, Any], actor: ActorIdentity, ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]) -> WriteResult`; existing `emit_override_audit_entry(...) -> CPAuditLedgerEntry` signature unchanged; NEW `def _canonicalize_outcome_bytes(payload: BaseModel | Mapping[str, Any]) -> bytes`. At v2.29 the `EntryPayload` reference resolves to IS HEAD's actual 4-field shape per CP spec v1.26 §16.5.3; outer signature surface unchanged.

**Depends on (PRESERVED VERBATIM from v2.28):** [U-CP-14] (Cluster L3 source) + IS-axis HEAD callable surface.

**Tests (REPLACES v2.28 U-CP-74 Tests at one test-name entry; remaining test names preserved verbatim):**

REPLACED test name at v2.29: `test_emit_override_state_ledger_response_hash_over_post_override_config` (v2.28) → at v2.29 the corresponding test scope splits into TWO entries: **`test_emit_override_state_ledger_idempotency_key_includes_outcome_hash_suffix`** (verifies AC #2 outcome-hash segment is present at idempotency_key derivation with `_canonicalize_outcome_bytes(post_override_step_config)`) AND **`test_emit_override_state_ledger_response_hash_is_is_computed_not_composer_controlled`** (verifies AC #3: composer does NOT supply response_hash; IS computes it internally via `compute_response_hash` per C-IS-06 §6.2; verify by inspecting the persisted entry's response_hash equals `SHA-256(canonicalize(persisted_entry))` recomputed independently).

PRESERVED VERBATIM test names from v2.28: `test_emit_override_state_ledger_action_id`, `test_emit_override_state_ledger_idempotency_key_per_q1b` (verifies the v2.28 disambiguator segments per AC #2 — note at v2.29 this test should also include the suffix segment OR a sibling test should be added; implementation discretion), `test_emit_override_state_ledger_orthogonal_to_audit_emission`, `test_emit_override_state_ledger_dual_emission_order_independent`, `test_emit_override_audit_entry_preserved_verbatim_byte_identical`, `test_cp_audit_ledger_entry_shape_unchanged_at_v1_25` (rename owed to `_at_v1_26` for citation freshness per `Project_Workflow_v1_8.md` §7.4 use-latest-version; semantic preserved verbatim), `test_cp_signed_audit_ledger_entry_signing_contract_unchanged`, `test_canonicalize_outcome_bytes_sorted_keys_deterministic`, `test_canonicalize_outcome_bytes_rejects_nan_infinity`.

**Rollback boundary (PRESERVED VERBATIM from v2.28):** Single coherent change at this unit; revertible as single PR / commit family per workspace per-unit rollback discipline.

### U-CP-75 — emit_workload_class_selection_state_ledger_entry composer (CASCADE)

**Implements (REPLACES v2.28 U-CP-75 Implements):** CP spec v1.26 §16.5.2 row U-CP-27 + §16.5.3 + §16.5.4 (v1.26 idempotency-key formula with outcome-hash suffix) + §16.5.5 (outcome-bytes recipe consumed by idempotency_key) + §16.5.7.

**AC #2 (REPLACES v2.28 U-CP-75 AC #2):** Idempotency-key per CP spec v1.26 §16.5.4 row U-CP-27: `workflow_id || step_id || engine_class_id || binding_selection_result_canonical_bytes || sha256(outcome_canonical_bytes).hex()` with 0x1E record-separator + SHA-256 hex-64. Outcome canonical bytes per CP spec v1.26 §16.5.5 row U-CP-27: `WorkloadBindingSelectionResult` canonical JSON bytes (resolved class binding + rationale) via `_canonicalize_outcome_bytes` helper from U-CP-74. The v2.28 disambiguator segments (`workflow_id`, `step_id`, `engine_class_id`, `binding_selection_result_canonical_bytes`) preserved verbatim per Q-β.i-1(a).

**AC #3 (REPLACES v2.28 U-CP-75 AC #3):** `response_hash` is IS-internal per C-IS-06 §6.2 — composer does NOT control it. The `WorkloadBindingSelectionResult` canonical JSON bytes per CP spec v1.26 §16.5.5 row U-CP-27 are consumed by AC #2 idempotency_key derivation per §16.5.4, NOT by `response_hash` field. Reuses `_canonicalize_outcome_bytes` helper from U-CP-74.

**AC #1, AC #4, AC #5, AC #6 (PRESERVED VERBATIM from v2.28):** `action_id = "cp.workload-binding-class-selection"`; fires AFTER `select_engine_class(...)` resolves BEFORE returning; ZERO `CPAuditLedgerEntry` emission per spec v1.26 §16.5.9 invariant 5; reuses `_canonicalize_outcome_bytes` helper.

**Files / Signatures / Depends on (PRESERVED VERBATIM from v2.28).** Outer signature `async def emit_workload_class_selection_state_ledger_entry(*, workflow_id: str, step_id: str, selection_result: WorkloadBindingSelectionResult, actor: ActorIdentity, ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]) -> WriteResult` — `EntryPayload` resolves to IS HEAD 4-field shape per CP spec v1.26 §16.5.3.

**Tests (REPLACES one entry; remaining preserved verbatim):** REPLACED: `test_emit_workload_class_selection_response_hash_over_selection_result` (v2.28) → at v2.29 splits into **`test_emit_workload_class_selection_idempotency_key_includes_outcome_hash_suffix`** + **`test_emit_workload_class_selection_response_hash_is_is_computed_not_composer_controlled`**. PRESERVED VERBATIM: `test_emit_workload_class_selection_action_id`, `test_emit_workload_class_selection_idempotency_key_includes_engine_class_id` (v2.28 disambiguator validation; v2.29 implementation discretion to extend or sibling-test for suffix), `test_emit_workload_class_selection_fires_post_resolve_pre_return`, `test_emit_workload_class_selection_zero_cp_audit_emission`, `test_emit_workload_class_selection_idempotent_replay`.

**Rollback boundary (PRESERVED VERBATIM from v2.28).**

### U-CP-76 — emit_pause_resume_state_ledger_entry composer at workflow-layer `PauseResumeProtocol` class (CASCADE)

**Implements (REPLACES v2.28 U-CP-76 Implements):** CP spec v1.26 §16.5.2 row U-CP-30 + §16.5.3 + §16.5.4 (v1.26 formula with outcome-hash suffix) + §16.5.5 (outcome-bytes consumed by idempotency_key) + §16.5.7.

**AC #2 (REPLACES v2.28 U-CP-76 AC #2):** Idempotency-key per CP spec v1.26 §16.5.4 row U-CP-30: `workflow_id || step_id || pause_resume_protocol_event_kind || event_sequence_id || sha256(outcome_canonical_bytes).hex()` with 0x1E record-separator + SHA-256 hex-64. Outcome canonical bytes per CP spec v1.26 §16.5.5 row U-CP-30: protocol-state-transition outcome canonical JSON bytes (the protocol state snapshot after the class-level event) via `_canonicalize_outcome_bytes` helper from U-CP-74. v2.28 disambiguator segments preserved verbatim per Q-β.i-1(a).

**AC #4 (REPLACES v2.28 U-CP-76 AC #4 — was "Response-hash over protocol-state-transition outcome canonical JSON bytes"):** `response_hash` is IS-internal per C-IS-06 §6.2; composer does NOT control it. Protocol-state-transition outcome canonical JSON bytes per CP spec v1.26 §16.5.5 row U-CP-30 are consumed by AC #2 idempotency_key derivation per §16.5.4 NOT by `response_hash`. Reuses `_canonicalize_outcome_bytes` helper from U-CP-74.

**AC #1, AC #3, AC #5, AC #6 (PRESERVED VERBATIM from v2.28):** `action_id = "cp.pause-resume-protocol"`; fires at workflow-layer protocol-class method invocations per spec v1.26 §16.5.7; ZERO `CPAuditLedgerEntry` emission; reuses `_canonicalize_outcome_bytes` helper.

**Files / Signatures / Depends on (PRESERVED VERBATIM from v2.28).** Outer signature includes NEW enum `PauseResumeProtocolEventKind` at module top-level (per v2.28; preserved at v2.29). `EntryPayload` resolves to IS HEAD 4-field shape per CP spec v1.26 §16.5.3.

**Tests (REPLACES one entry; remaining preserved verbatim):** REPLACED: at v2.29 the response_hash-related test entry from v2.28 (if any) split into **`test_emit_pause_resume_idempotency_key_includes_outcome_hash_suffix`** + **`test_emit_pause_resume_response_hash_is_is_computed_not_composer_controlled`**. PRESERVED VERBATIM: `test_emit_pause_resume_workflow_layer_action_id`, `test_emit_pause_resume_idempotency_key_includes_event_kind`, `test_emit_pause_resume_fires_at_workflow_layer_protocol_transitions`, `test_emit_pause_resume_zero_cp_audit_emission`, `test_emit_pause_resume_orthogonal_to_engine_layer_at_u_cp_78_u_cp_79`, `test_pause_resume_protocol_event_kind_enum_exhaustive`.

**Rollback boundary (PRESERVED VERBATIM from v2.28).**

### U-CP-77 — emit_hitl_tool_call_rewriting_state_ledger_entry composer (CASCADE)

**Implements (REPLACES v2.28 U-CP-77 Implements):** CP spec v1.26 §16.5.2 row U-CP-37 + §16.5.3 + §16.5.4 (v1.26 formula with outcome-hash suffix) + §16.5.5 (outcome-bytes consumed by idempotency_key) + §16.5.7.

**AC #2 (REPLACES v2.28 U-CP-77 AC #2):** Idempotency-key per CP spec v1.26 §16.5.4 row U-CP-37: `workflow_id || step_id || tool_call_id || semantic_variant_binding_id || sha256(outcome_canonical_bytes).hex()` with 0x1E record-separator + SHA-256 hex-64. Outcome canonical bytes per CP spec v1.26 §16.5.5 row U-CP-37: `RewrittenToolCall` canonical JSON bytes (impl line 109) via `_canonicalize_outcome_bytes` helper from U-CP-74. v2.28 disambiguator segments preserved verbatim per Q-β.i-1(a).

**AC #4 (REPLACES v2.28 U-CP-77 AC #4 — was "Response-hash over RewrittenToolCall canonical JSON bytes"):** `response_hash` is IS-internal per C-IS-06 §6.2; composer does NOT control it. `RewrittenToolCall` canonical JSON bytes per CP spec v1.26 §16.5.5 row U-CP-37 consumed by AC #2 idempotency_key derivation NOT by `response_hash`. Reuses `_canonicalize_outcome_bytes` helper from U-CP-74.

**AC #1, AC #3, AC #5, AC #6 (PRESERVED VERBATIM from v2.28):** `action_id = "cp.hitl-tool-call-rewriting"`; fires AFTER `rewrite_tool_call_to_hitl(...)` produces RewrittenToolCall BEFORE returning; ZERO `CPAuditLedgerEntry` emission; reuses helper.

**Files / Signatures / Depends on (PRESERVED VERBATIM from v2.28).** `EntryPayload` resolves to IS HEAD 4-field shape per CP spec v1.26 §16.5.3.

**Tests (REPLACES one entry; remaining preserved verbatim):** REPLACED: `test_emit_hitl_rewriting_response_hash_over_rewritten_tool_call` (v2.28) → splits into **`test_emit_hitl_rewriting_idempotency_key_includes_outcome_hash_suffix`** + **`test_emit_hitl_rewriting_response_hash_is_is_computed_not_composer_controlled`**. PRESERVED VERBATIM: `test_emit_hitl_rewriting_action_id`, `test_emit_hitl_rewriting_idempotency_key_includes_semantic_variant_binding_id`, `test_emit_hitl_rewriting_fires_post_rewrite_pre_return`, `test_emit_hitl_rewriting_zero_cp_audit_emission`.

**Rollback boundary (PRESERVED VERBATIM from v2.28).**

### U-CP-78 — emit_pause_captured_state_ledger_entry composer at engine-layer `capture_pause_snapshot` (CASCADE)

**Implements (REPLACES v2.28 U-CP-78 Implements):** CP spec v1.26 §16.5.2 row U-CP-49 + §16.5.3 + §16.5.4 (v1.26 formula with outcome-hash suffix) + §16.5.5 (outcome-bytes consumed by idempotency_key) + §16.5.7.

**AC #2 (REPLACES v2.28 U-CP-78 AC #2):** Idempotency-key per CP spec v1.26 §16.5.4 row U-CP-49: `workflow_id || step_id || pause_event_id || snapshot_hash || sha256(outcome_canonical_bytes).hex()` with 0x1E record-separator + SHA-256 hex-64. The `snapshot_hash` disambiguator (per `PauseResumeProtocol` class spec at line 230) preserved verbatim from v2.28; the outcome-hash suffix segment is independently computed via `_canonicalize_outcome_bytes` over the `PauseSnapshot` canonical JSON bytes per CP spec v1.26 §16.5.5 row U-CP-49 (note: `snapshot_hash` field and outcome-hash suffix are SEPARATE — `snapshot_hash` is a pre-computed field on `PauseSnapshot` per impl line 230; the suffix outcome-hash is computed independently over the full `PauseSnapshot` canonical JSON bytes via the helper).

**AC #4 (REPLACES v2.28 U-CP-78 AC #4 — was "Response-hash over PauseSnapshot canonical JSON bytes"):** `response_hash` is IS-internal per C-IS-06 §6.2; composer does NOT control it. `PauseSnapshot` canonical JSON bytes per CP spec v1.26 §16.5.5 row U-CP-49 (impl line 46) consumed by AC #2 idempotency_key derivation NOT by `response_hash`. Reuses `_canonicalize_outcome_bytes` helper from U-CP-74.

**AC #1, AC #3, AC #5, AC #6 (PRESERVED VERBATIM from v2.28):** `action_id = "cp.pause-captured"`; fires AFTER `capture_pause_snapshot(...)` returns PauseSnapshot BEFORE returning; ZERO `CPAuditLedgerEntry` emission; orthogonal to U-CP-76 workflow-layer per CP spec v1.11 §26 NEW NOTE coexistence; reuses helper.

**Files / Signatures / Depends on (PRESERVED VERBATIM from v2.28).** `EntryPayload` resolves to IS HEAD 4-field shape per CP spec v1.26 §16.5.3.

**Tests (REPLACES one entry; remaining preserved verbatim):** REPLACED: `test_emit_pause_captured_response_hash_over_pause_snapshot` (v2.28) → splits into **`test_emit_pause_captured_idempotency_key_includes_outcome_hash_suffix`** + **`test_emit_pause_captured_response_hash_is_is_computed_not_composer_controlled`**. PRESERVED VERBATIM: `test_emit_pause_captured_action_id`, `test_emit_pause_captured_idempotency_key_includes_snapshot_hash`, `test_emit_pause_captured_fires_post_capture_pre_return`, `test_emit_pause_captured_zero_cp_audit_emission`, `test_emit_pause_captured_engine_layer_orthogonal_to_workflow_layer_at_u_cp_76`.

**Rollback boundary (PRESERVED VERBATIM from v2.28).**

### U-CP-79 — emit_resume_attempted_state_ledger_entry composer at engine-layer `attempt_resume` (CASCADE)

**Implements (REPLACES v2.28 U-CP-79 Implements):** CP spec v1.26 §16.5.2 row U-CP-50 + §16.5.3 + §16.5.4 (v1.26 formula with outcome-hash suffix) + §16.5.5 (outcome-bytes consumed by idempotency_key) + §16.5.7.

**AC #2 (REPLACES v2.28 U-CP-79 AC #2):** Idempotency-key per CP spec v1.26 §16.5.4 row U-CP-50: `workflow_id || step_id || resume_event_id || resume_attempt_count || sha256(outcome_canonical_bytes).hex()` with 0x1E record-separator + SHA-256 hex-64. The `resume_attempt_count` disambiguator (per `ResumeAttempt` / `ResumeOutcome` model contract per impl `pause_resume_protocol.py:63,91`) preserved verbatim from v2.28; the outcome-hash suffix is computed independently via `_canonicalize_outcome_bytes` over `ResumeOutcome` canonical JSON bytes per CP spec v1.26 §16.5.5 row U-CP-50.

**AC #4 (REPLACES v2.28 U-CP-79 AC #4 — was "Response-hash over ResumeOutcome canonical JSON bytes"):** `response_hash` is IS-internal per C-IS-06 §6.2; composer does NOT control it. `ResumeOutcome` canonical JSON bytes per CP spec v1.26 §16.5.5 row U-CP-50 (impl line 91 — `ResumeOutcomeKind` + resumed state) consumed by AC #2 idempotency_key derivation NOT by `response_hash`. Reuses `_canonicalize_outcome_bytes` helper from U-CP-74.

**AC #1, AC #3, AC #5, AC #6, AC #7 (PRESERVED VERBATIM from v2.28):** `action_id = "cp.resume-attempted"`; fires AFTER `attempt_resume(...)` resolves ResumeOutcome BEFORE returning; ZERO `CPAuditLedgerEntry` emission; orthogonal to U-CP-76 workflow-layer; fires at BOTH success and failure outcomes; reuses helper.

**Files / Signatures / Depends on (PRESERVED VERBATIM from v2.28).** `EntryPayload` resolves to IS HEAD 4-field shape per CP spec v1.26 §16.5.3.

**Tests (REPLACES one entry; remaining preserved verbatim):** REPLACED: `test_emit_resume_attempted_response_hash_over_resume_outcome` (v2.28) → splits into **`test_emit_resume_attempted_idempotency_key_includes_outcome_hash_suffix`** + **`test_emit_resume_attempted_response_hash_is_is_computed_not_composer_controlled`**. PRESERVED VERBATIM: `test_emit_resume_attempted_action_id`, `test_emit_resume_attempted_idempotency_key_includes_attempt_count`, `test_emit_resume_attempted_fires_on_success`, `test_emit_resume_attempted_fires_on_failure`, `test_emit_resume_attempted_zero_cp_audit_emission`, `test_emit_resume_attempted_engine_layer_orthogonal_to_workflow_layer_at_u_cp_76`.

**Rollback boundary (PRESERVED VERBATIM from v2.28).**

---

## §2 — Coverage matrix + DAG topology

**Coverage matrix UNCHANGED at v2.29.** U-CP-74..79 still cover CP spec §16.5.2 6-composer enumeration (5 of 7 §16.5.2 contract rows for greenfield composers + 1 sibling addition at U-CP-14) per v2.28 §1. v1.26 spec amendment is INTRA-§16.5 prose-level + intra-§16.5.3/§16.5.4/§16.5.5 sub-section delta — no new spec contract introduced; no contract removed; coverage marks unchanged.

**DAG topology UNCHANGED at v2.29.** U-CP-74..79 dependency edges preserved verbatim per v2.28 §3 + §0.3 Cluster L4 within-axis dependency table. U-CP-74 publishes shared `_canonicalize_outcome_bytes` helper at NEW `state_ledger_canonicalization.py`; U-CP-75..79 depend on U-CP-74 for the shared helper. Helper signature + role at v2.29 preserved verbatim from v2.28 — the bytes produced by the helper are consumed by idempotency_key derivation per spec v1.26 §16.5.4 rather than by response_hash field; the helper itself is unchanged. Cross-axis edges (each composer's `ledger_writer` binds at runtime composition time to IS-axis HEAD callable per spec v1.26 §16.5.8) unchanged from v2.28.

Topological sort acyclic; 6 NEW units consumed at L4 across existing clusters; ∅ remaining unresolved edges within CP-axis. ZERO new CP→AS / CP→OD / OD→CP edges per spec v1.26 §"ZERO cross-axis cascade" change-note clause.

---

## §3 — Status

Surgical cascade at v2.28 §2 U-CP-74..79 unit bodies absorbing operator-ratified β.i resolution per CP spec v1.26 commit `ec4a2f7`. Apply pass: this arc (delta-only plan file co-published with spec v1.26 + PR #38 routing-doc + nested fork doc). v2.28 §0 + §1 + §3 + Filing footer + v2.27 + earlier PRESERVED VERBATIM per delta-only-plan-chain convention. v2.28 §2 unit bodies at U-CP-74..79 receive the surgical AC #2 + AC #3/#4 + Implements + tests-list cascade per §1 above; all other v2.28 §2 unit-body fields PRESERVED VERBATIM.

CP plan v2.29 unblocks Phase 7 sub-phase 7b cluster {U-CP-74..79} consumption against re-issued substrate (spec v1.26 + plan v2.29). Closure-back-references at nested fork doc + parent fork doc owed post-merge of PR #38.

Status: Proposed (cleared at operator merge of PR #38).

2026-05-29.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_29.md` |
| Version | v2.29 |
| Filing event | Surgical cascade absorbing CP spec v1.26 β.i amendment (commit `ec4a2f7`) at v2.28 §2 U-CP-74..79 unit-body AC #2 + AC #3/#4 + Implements citation refresh + tests-list rename per nested fork doc `class_1_tension_u_cp_74_entrypayload_field_set_drift.md` operator-ratified 2026-05-29 Q-set (A + β.i + Q-β.i-1(a) + Q-β.i-3(b)). ZERO DAG topology change. ZERO coverage matrix change. ZERO cross-axis cascade. 2026-05-29. |
| Predecessor | `Implementation_Plan_Control_Plane_v2_28.md` (PRESERVED VERBATIM outside the §2 U-CP-74..79 cascade scope at v2.29) |
| Successor | (none — current canonical) |
