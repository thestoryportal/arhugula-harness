---
artifact: design-substrate/Spec_Control_Plane_v1_27.md
version: v1.27
cleared_at: 2026-05-29T16:30:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_tension_u_cp_14_dual_emission_stubs_and_disambiguator_semantics_gap.md
  - PR #65 (fork doc filing; merged at squash commit d8d091e 2026-05-29)
  - PR for v1.27 apply pass (this PR)
merge_commit: <filled at merge>
reviewer_chain:
  - Operator AskUserQuestion ratification 2026-05-29 Q1=A + Q2=iii + Q3=i + Q5=i + Q6=α
  - Advisor 45th application of [[advisor-before-substantive-work-for-cross-axis-blockers]] pre-substantive consultation at fork-doc authoring (PR #65); reframed checkpoint narrow framing "Override disambiguator extension arc" → composite blocker "named-but-undefined disambiguator + both-halves-stub" per [[advisor-45th-application-reframe-checkpoint-narrow-framing-to-composite-blocker]]
  - Empirical orientation at HEAD `d8d091e` verifying (a) §16.5.4 row U-CP-14 disambiguator-notes absence at lines 67-90; (b) StepOverride / WorkflowManifestEntry field-sets carry no override_id / policy_id; (c) `emit_override_audit_entry` stub functional gap at `per_step_override_evaluator.py:208-231`
  - spec-writer apply pass (this arc)
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Control_Plane v1.27`

v1.27 amends CP spec v1.26 §16.5.4 row U-CP-14 idempotency-key formula per operator-ratified Reading A: drops `override_id` + `policy_id` named-but-undefined placeholder segments and collapses to `workflow_id || step_id || sha256(outcome_canonical_bytes).hex()`. The collapse is grounded in the empirical type-shape invariant at `harness-cp/src/harness_cp/workflow_manifest_entry.py:109` — `per_step_overrides: dict[StepID, StepOverride]` enforces per-WorkflowManifestEntry step-id uniqueness on override identity at v1.6 MVP scope. ZERO new types; ZERO StepOverride / WorkflowManifestEntry field-set extension; ZERO X-AL-3 silent-extension concern.

v1.27 also annotates the audit-half stub functional gap at §16.5.6 per Q2=iii IN-SCOPE-BUT-MARK-DEFERRED — `emit_override_audit_entry` ignores `override` + `actor` inputs and hardcodes placeholder field values; the §16.5.6 dual-emission discipline claim holds at the structural layer but is empirically false at the functional layer. Closure of the audit-half stub is owed at a separate apply-pass arc per Q2=iii deferred-closure operator ratification. State-ledger-half firing site at `resolve_step_binding(...)` also remains absent at HEAD; runtime plan v2.39 U-RT-111 AC #1 STRUCK per `[[u-rt-111-ac-2-strike-fourth-rescope-substrate-lifecycle-mismatch]]` + sibling arcs gates RETIRE-READY transit.

Phase 7 consumers may treat CP spec v1.27 as canonical for the U-CP-14 idempotency-key formula + §16.5.6 dual-emission discipline annotation. Other §16.5 composer rows (U-CP-27 / U-CP-30 / U-CP-37 / U-CP-49 / U-CP-50) PRESERVED VERBATIM at v1.27 per delta-only-spec-file convention. Co-published with CP plan v2.29 → v2.30 single-unit-body amendment at U-CP-74; harness-cp impl (`per_step_override_evaluator.py` composer + helper signature trim); harness-runtime impl (`lifecycle/cp_is_wiring.py` wiring-layer signature trim); harness-cp tests + harness-runtime tests (30 tests touched; 2090 / 10 skipped passing); workspace `CLAUDE.md` row bumps; fork doc Status closure PROPOSING → ✅ APPLIED-AS-READING-A.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Audit-half stub remediation deferred per Q2=iii — `emit_override_audit_entry` remains a functional stub at HEAD post-v1.27; closure requires a separate apply-pass arc producing the audit-half functional body per C-CP-06 §6.2 + C-CP-16 §16.2 + §20.4 signing contract conformance.
- State-ledger-half firing site absent at HEAD — gates H_T-RT-35 RETIRE-READY transit at runtime plan v2.39 U-RT-111 AC #1 (STRUCK per upstream `[[u-rt-111-ac-2-strike-fourth-rescope-substrate-lifecycle-mismatch]]`).
- Reading C (StepOverride + WorkflowManifestEntry field extension for operator-supplied identifiers) remains the architecturally-canonical long-term path if multi-version policy semantics or multi-override-per-step semantics are introduced at a future spec extension arc; v1.27 does NOT foreclose Reading C per v1.27 §2 (d).
- See `.harness/clearance/README.md` for marker discipline.
