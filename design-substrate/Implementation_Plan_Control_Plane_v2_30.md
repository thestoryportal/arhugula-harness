# Implementation Plan: Control Plane — v2.30 (delta over v2.29)

---

## §0 — Change-note (v2.29 → v2.30)

**Scope of revision.** Surgical single-unit-body amendment at U-CP-74 absorbing CP spec v1.26 → v1.27 §16.5.4 row U-CP-14 Reading A resolution per `.harness/class_1_tension_u_cp_14_dual_emission_stubs_and_disambiguator_semantics_gap.md` operator-ratified 2026-05-29 Q-set (Q1=A drop override_id + policy_id + collapse formula; Q2=iii audit-stub IN-SCOPE-BUT-MARK-DEFERRED; Q3=i accept v1.25 + v1.26 formula re-ratification; Q5=i bundled apply pass; Q6=α intra-CP only). Spec v1.27 amends §16.5.4 row U-CP-14 idempotency-key formula from 5-tuple `(workflow_id, step_id, override_id, policy_id, outcome_hash)` to 3-tuple `(workflow_id, step_id, outcome_hash)` per the type-shape invariant at `per_step_overrides: dict[StepID, StepOverride]` field at `workflow_manifest_entry.py:109` (per-WorkflowManifestEntry step-id uniqueness on override identity).

**v2.29 substantive content preserved verbatim except for the scoped U-CP-74 unit-body amendments below.** v2.29 §0 change-note + §0.3 NEW units table + §0.4 CXA edge-tracking + §0.5–§0.8 + §1 §"U-CP-75..U-CP-79 unit bodies" (PRESERVED VERBATIM at v2.30 — v1.27 amendment is intra-row-U-CP-14 only; other composer rows unchanged) + §3 DAG topology + Filing footer ALL PRESERVED VERBATIM at v2.30 by reference. v2.28 + earlier substantive content preserved verbatim per delta-only-plan-chain convention.

**ZERO DAG topology change.** U-CP-74 dependency edges preserved verbatim per v2.28 §3 + §0.3 Cluster L4 within-axis dependency table. Shared `_canonicalize_outcome_bytes` helper at NEW `state_ledger_canonicalization.py` PRESERVED VERBATIM at U-CP-74 publication site; helper signature + role unchanged.

**ZERO new units / ZERO removed units / ZERO outer signature shape change at the broad pattern.** The U-CP-74 inner-signature trim drops 2 kwargs (`override_id: str` + `policy_id: str`) per Reading A apply; outer call shape (`async def emit_*_state_ledger_entry(*, ..., ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]) -> WriteResult`) PRESERVED VERBATIM at v2.30. U-CP-75..79 outer + inner signatures PRESERVED VERBATIM (v1.27 amendment intra-row-U-CP-14 only).

**ZERO cross-axis cascade per Q6=(α).** IS-axis HEAD callable surface PRESERVED VERBATIM. AS / OD / Runtime / CXA / ADR PRESERVED VERBATIM. Workflow v1.13 + ADD v1.3 + PRD v1.1 PRESERVED VERBATIM.

**Co-publication this session.** CP spec v1.27 (NEW delta file at `design-substrate/Spec_Control_Plane_v1_27.md`) + this plan v2.30 + harness-cp impl (`per_step_override_evaluator.py` composer + `_override_idempotency_key` helper signature trim) + harness-runtime impl (`lifecycle/cp_is_wiring.py` wiring-layer signature trim) + harness-cp tests refresh + harness-runtime tests refresh + workspace `CLAUDE.md` row bumps + fork doc Status PROPOSING → ✅ APPLIED-AS-READING-A + clearance marker.

---

## §1 — Revised unit body — U-CP-74 (cascade scope only; preserve-verbatim sections referenced)

The amendments below REPLACE the cited v2.29 §1 U-CP-74 ACs + `Signatures:` + tests-list entries verbatim. All other v2.29 §1 U-CP-74 unit-body fields (Implements citation refresh, Files, Depends on, AC #1, AC #3, AC #4, AC #5, AC #6, AC #7, AC #8, AC #9, untouched test entries, Rollback boundary) PRESERVED VERBATIM at v2.30 by reference. U-CP-75 / U-CP-76 / U-CP-77 / U-CP-78 / U-CP-79 unit bodies PRESERVED VERBATIM at v2.30 by reference (v1.27 amendment intra-row-U-CP-14 only).

### U-CP-74 — emit_override_state_ledger_entry sibling composer at U-CP-14 + shared `_canonicalize_outcome_bytes` helper (CASCADE — Reading A apply)

**Implements (REPLACES v2.29 U-CP-74 Implements):** CP spec v1.27 §16.5.2 row U-CP-14 + v1.26 §16.5.3 EntryPayload composition (4-field shape per IS HEAD `(action_id, idempotency_key, actor, timestamp)`) + v1.27 §16.5.4 idempotency-key formula (per-composer disambiguator collapsed at row U-CP-14 per Reading A; outcome-hash suffix preserved) + v1.26 §16.5.5 outcome-bytes recipe consumed by idempotency_key derivation per §16.5.4 + v1.27 §16.5.6 dual-emission discipline (audit-half stub functional gap annotated per Q2=iii) + v1.26 §16.5.7 firing-site discipline + v1.26 §16.5.8 Q4 attribution (composer supplies EntryPayload's 4 fields; IS computes response_hash + prior_event_hash internally).

**AC #2 (REPLACES v2.29 U-CP-74 AC #2):** Idempotency-key per CP spec v1.27 §16.5.4 row U-CP-14: canonical bytes are `workflow_id || step_id || sha256(outcome_canonical_bytes).hex()` (3-tuple per Reading A; v1.25 + v1.26 `override_id` + `policy_id` placeholder segments dropped per Q1=A operator ratification 2026-05-29) with 0x1E record-separator + SHA-256 hex-64. The outcome-hash suffix is computed at composer-call site over post-override step-config canonical JSON bytes via the shared `_canonicalize_outcome_bytes` helper (this unit's NEW module; AC #8 below). The `(workflow_id, step_id)` discriminator carries per-WorkflowManifestEntry step-id uniqueness invariant per `per_step_overrides: dict[StepID, StepOverride]` at `workflow_manifest_entry.py:109`; the outcome-hash suffix carries the Q5(a) "hash-over-outcome-bytes" semantic per Q-β.i-1(a).

**Signatures (REPLACES v2.29 U-CP-74 Signatures at the 2 affected callable shapes; remaining sibling signatures PRESERVED VERBATIM):**

- `async def emit_override_state_ledger_entry(*, workflow_id: str, step_id: str, post_override_step_config: Mapping[str, Any], actor: ActorIdentity, ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]) -> WriteResult` — drops `override_id: str` + `policy_id: str` kwargs per Reading A apply.
- `def _override_idempotency_key(workflow_id: str, step_id: str, outcome_hash_hex: str) -> str` — drops `override_id: str` + `policy_id: str` parameters per Reading A apply; 3-segment 0x1E-join.
- `def emit_override_audit_entry(workflow_id: str, step_id: str, override: StepOverride, actor: ActorIdentity) -> CPAuditLedgerEntry` PRESERVED VERBATIM at signature surface (Q2=iii IN-SCOPE-BUT-MARK-DEFERRED audit-half stub remediation — functional content remains placeholder at HEAD per spec v1.27 §16.5.6 annotation; signature surface unchanged).
- `def _canonicalize_outcome_bytes(payload: BaseModel | Mapping[str, Any]) -> bytes` PRESERVED VERBATIM from v2.28.

At v2.30 the `EntryPayload` reference resolves to IS HEAD's actual 4-field shape per CP spec v1.26 §16.5.3; outer call shape PRESERVED VERBATIM.

**Tests (REPLACES v2.29 U-CP-74 Tests at the affected 5-tuple-asserting test entries; remaining test entries PRESERVED VERBATIM):**

REPLACED test names at v2.30:

- `test_emit_override_state_ledger_idempotency_key_per_q1b` (v2.29 — asserted 5-tuple per v1.26 row U-CP-14) → at v2.30 RENAMED to **`test_emit_override_state_ledger_idempotency_key_per_reading_a`** and rewritten to assert 3-tuple `workflow_id || step_id || sha256(outcome_canonical_bytes).hex()` 0x1E-joined per CP spec v1.27 §16.5.4 row U-CP-14.

- Fixture helper `_kwargs(...)` at the test module → drops `override_id="ov-3"` + `policy_id="pol-4"` keys per Reading A apply; all dependent tests pick up the trimmed signature transparently.

PRESERVED VERBATIM test names from v2.29: `test_emit_override_state_ledger_action_id`, `test_emit_override_state_ledger_idempotency_key_includes_outcome_hash_suffix` (verifies AC #2 outcome-hash segment is present at idempotency_key derivation with `_canonicalize_outcome_bytes(post_override_step_config)` — semantic unchanged; signature trim applies transparently), `test_emit_override_state_ledger_response_hash_is_is_computed_not_composer_controlled` (verifies AC #3; semantic unchanged), `test_emit_override_state_ledger_actor_direct_reuse`, `test_emit_override_audit_entry_preserved_verbatim_byte_identical`, `test_emit_override_state_ledger_dual_emission_order_independent`, `test_emit_override_state_ledger_orthogonal_to_audit_emission`, `test_cp_audit_ledger_entry_shape_unchanged_at_v1_26` (carrier-conform tests preserved verbatim at signature semantics; cite-text refresh owed at next plan revision pass per `Project_Workflow_v1_13.md` §7.4.2 use-latest-version), `test_cp_signed_audit_ledger_entry_signing_contract_unchanged`, `test_canonicalize_outcome_bytes_sorted_keys_deterministic`, `test_canonicalize_outcome_bytes_rejects_nan_infinity`.

NEW test name at v2.30 (audit-half stub annotation per Q2=iii): **`test_emit_override_audit_entry_is_known_functional_stub_per_v1_27_annotation`** — documents the known functional gap at the test layer per the v1.27 §16.5.6 annotation; assertion shape: `out.gate_level == GateLevel.AUTO and out.response == "approve" and out.timestamp == "" and out.prior_event_hash == "0" * 64` with docstring referencing the v1.27 §16.5.6 audit-half stub annotation + the deferred closure arc. (Sibling to existing `test_emit_override_audit_entry_preserved_verbatim_byte_identical` which asserts the same field values structurally; v2.30 NEW test adds the v1.27-annotation documentation context.)

**AC #1, AC #3, AC #4, AC #5, AC #6, AC #7, AC #8, AC #9 (PRESERVED VERBATIM from v2.29):** v2.29 ACs at these row positions preserved verbatim — `action_id` value, `response_hash` IS-internal semantic per AC #3, actor direct re-use, sibling-composer ADDITIVE discipline, dual-emission order-independence, ZERO change to CPAuditLedgerEntry + C-CP-20 §20.4 + v1.7 §13.5.1 converter, `_canonicalize_outcome_bytes` helper acceptance (sorted keys + `(",", ":")` separators + UTF-8 + NaN/Infinity rejection per spec v1.26 §16.5.5 + ECMA-404), and composer-awaits-`ledger_writer` discipline per spec v1.26 §16.5.9 invariant 4.

**Files (PRESERVED VERBATIM from v2.28 + v2.29):** `harness-cp/src/harness_cp/per_step_override_evaluator.py` (EXTEND) + `harness-cp/src/harness_cp/state_ledger_canonicalization.py` (NEW) + `harness-cp/tests/test_override_state_ledger_emission.py` (NEW) + `harness-cp/tests/test_state_ledger_canonicalization.py` (NEW). Additional file touched at v2.30 (cross-axis impl-only, NOT plan-body authoring scope): `harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py` (signature trim at the `RuntimeCpIsWiring.emit_override_state_ledger_entry` wiring-layer method) + `harness-runtime/tests/test_lifecycle_cp_is_wiring.py` (call-site refresh).

**Depends on (PRESERVED VERBATIM from v2.28 + v2.29):** [U-CP-14] (Cluster L3 source) + IS-axis HEAD callable surface.

**Rollback boundary (PRESERVED VERBATIM from v2.28 + v2.29):** Single coherent change at this unit; revertible as single PR / commit family per workspace per-unit rollback discipline.

---

## §2 — Adjacent observations (NOT patched per FM-2)

- **(a)** Audit-half stub at `emit_override_audit_entry` remains a known functional gap post-v2.30 per Q2=iii deferred closure. Plan body at v2.30 annotates the functional gap at the U-CP-74 unit-body level (NEW test name documentation context + Signatures preservation note) per the spec v1.27 §16.5.6 annotation; functional remediation owed at a separate apply-pass arc on the audit-half composer body. NOT patched at v2.30 per Q2=iii operator-ratified deferral.

- **(b)** Reading C (StepOverride + WorkflowManifestEntry field extension; operator-supplied override_id + policy_id) remains the architecturally-canonical long-term path if multi-version policy semantics or multi-override-per-step semantics are introduced at a future spec extension arc per spec v1.27 §2 (d). Plan v2.30 does NOT foreclose Reading C — the U-CP-74 AC #2 formula can be re-extended at that future arc per X-AL-3 explicit-extension discipline. Mirror plan-level precedent: CP plan v2.25 U-CP-13 `default_gate_level` extension (v1.20 spec) + v2.22 U-CP-14 `persona_tier` extension (v1.17 spec) + runtime plan v2.30 U-RT-94 webhook ctor params (v1.34 spec) — all single-unit-body amendments at plan-side per workspace `[[fork-h-t-cp-19-default-gate-level-spec-extension]]` precedent.

- **(c)** Workspace pattern catalogue at v2.30 closure: this arc instantiates `[[strike-revision-on-refined-second-tier-reason]]` at the **plan layer** — the v2.28 + v2.29 U-CP-74 AC #2 5-tuple formula STRIKE is preserved on a refined second-tier reason (no semantic source for `override_id` + `policy_id`) rather than un-STRUCK at the original v1.25 + v1.26 framing (multi-version policy roadmap). Mirror plan-layer precedent: runtime plan v2.39 AC #4 STRIKE refinement at U-RT-111 per Workflow v1.13 §7.4.7.2 species 2 sub-species catalogue (workspace v1.13 publication 2026-05-29 commit `9ddb9ba`).

---

## §3 — Status

Surgical single-unit-body amendment at U-CP-74 absorbing CP spec v1.26 → v1.27 §16.5.4 row U-CP-14 Reading A resolution + Q2(iii) + Q3(i) + Q5(i) + Q6(α) at AskUserQuestion 2026-05-29. Apply pass: this arc (delta-only plan file co-published with CP spec v1.27 + harness-cp impl + harness-runtime impl + tests + fork doc closure + clearance marker per Q5(i) bundled-absorption per workspace `CLAUDE.md` §11.4).

v2.29 + v2.28 + earlier PRESERVED VERBATIM per delta-only-plan-chain convention. v2.29 §1 U-CP-75 / U-CP-76 / U-CP-77 / U-CP-78 / U-CP-79 unit bodies PRESERVED VERBATIM (v1.27 amendment intra-row-U-CP-14 only). v2.28 §1 broader cluster framing (Cluster L4 within-axis dependency table; CP→IS bucket tracking) PRESERVED VERBATIM. v2.27 NEW U-CP-73 singleton-extension unit PRESERVED VERBATIM.

DAG verified Kahn-acyclic at U-CP-74 amendment. Unit count 80 UNCHANGED (v2.30 amends body only; no new unit; no removed unit). AC count at U-CP-74 grows from v2.29's 9 ACs to v2.30's 9 ACs (no change at AC cardinality; AC #2 text replaced; NEW test name at Tests list documents Q2=iii audit-stub annotation context).

H_T-RT-35 transit posture UNCHANGED at PARTIAL — this arc closes 1 of 5 upstream blockers at the FORK-DOC-FILED → APPLIED transit; 4 remaining upstream arcs gate RETIRE-READY transit per `[[u-rt-111-ac-2-strike-fourth-rescope-substrate-lifecycle-mismatch]]` + sibling arcs.

CXA v2.16 UNCHANGED (intra-CP-axis only per Q6(α); CP→IS bucket cardinality + 6-PENDING + 2-NOT-APPLICABLE composition unchanged).

Clearance marker filed at `.harness/clearance/Spec_Control_Plane-v1_27-cleared-2026-05-29.md`.

2026-05-29.
