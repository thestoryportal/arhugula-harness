# Implementation Plan: Harness Runtime — v2.67 (PROPOSED delta over cleared v2.64)

**Status: PROPOSED — not cleared.** Grounded on cleared v2.64; implements proposed Runtime spec
v1.136. Plans v2.65 (A3, U-RT-157; on main through PR #1633) and v2.66 (A5, U-RT-158; on main through PR #1635) are separately PROPOSED and not cleared; v2.64 remains the cleared head. Fold order is
A3 → A5 → A4, so this unit is U-RT-159; it was drafted as U-RT-158, which A5 keeps (root decision,
LIT `cmt-fcde66ad-1705-4ba8-bc49-7a4e03d4b0e0`). This is a proposed label reconciliation, not clearance.

## U-RT-159 — typed child refusal at the sub-agent dispatch FAILED row (A4)

**Source:** `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py` (FAILED + carrier →
`ChildResumeRefusedError` after best-effort audit; fail-closed signing → `RefusedChildAuditSigningError`
with the complete refusal; raised-refusal arm forwards the complete refusal);
`harness-runtime/src/harness_runtime/lifecycle/audit_signing_errors.py` (`RefusedChildAuditSigningError`
accepts a `ResumeRefusal`).

**Acceptance criteria:**
1. A FAILED child with a multi-reason refusal raises `ChildResumeRefusedError` carrying every reason.
2. Under a fail-closed signing failure it raises `RefusedChildAuditSigningError` with every reason,
   `audit_signing_failed` true, in the signing family, never `PostEffectAuditSigningError`.
3. A FAILED child without the carrier, including one whose text names the reason, raises
   `SubAgentChildFailedError`.
4. Root ORCHESTRATOR_WORKERS → middle ORCHESTRATOR_WORKERS → leaf, real dispatcher at both hops: a leaf
   gate refusal produced by the real CP resume guard and a depth-2 `claim-busy` both end the root
   FAILED with the exact typed class and carrier, no pause snapshot; a genuinely failed leaf keeps
   existing semantics.
   *Historical evidence limit:* Unit 1's depth-2 Runtime propagation observation uses a synthesized
   leaf result. Unit 2 supplies the CP gate-refusal producers required for the real-leaf portion;
   that final witness remains required. The historical synthesized-leaf observation is not evidence
   for the corrected head or a waiver of this criterion (fork record, Named limits and follow-ups).
5. Mutations that must fail a test: remapping the carrier to the generic error; setting a carrier on
   every FAILED child; classifying by fail-class substring; using the completed-effect signing carrier.
6. Ruff and pyright clean on the touched files; existing B-104 refusal/admission/signing suites pass.
7. A provider-free public `api.resume` integration with the durable
   claim store asserting the second root resume is claim-refused and zero tool/HITL/webhook effects.
   *Status (corrected):* a source test committed at a preparation head, `harness-runtime/tests/test_public_nested_resume_refusal.py`, targets this criterion; it is unlanded source preparation, not on main, and its evidence limits are recorded in the fork record.
8. A raised multi-reason `ChildResumeRefusedError` under fail-closed audit signing raises `RefusedChildAuditSigningError` carrying the complete reason set, `audit_signing_failed` true, in the signing family, never the completed-effect carrier (`PostEffectAuditSigningError`).
   *Witness (Unit 1):* the test `test_a_raised_multi_reason_refusal_with_fail_closed_signing_keeps_every_reason` in `harness-runtime/tests/test_child_resume_refusal_propagation.py`, which exists at the Unit 1 preparation head and is not on main. *Owed:* a discriminating mutation that collapses the raised arm to a single reason (or drops a reason) must turn it red. The fork record keeps a historical observation of such mutants at the preparation head; it is not new-head evidence.

<!-- [APPSPEC:observed-beats-inferred] Historical synthesized-leaf evidence cannot establish the required real-leaf behavior. -->
Delivery portions (by content; commits are recorded in the fork record): Unit 1 carries the typed
refusal value with all consumers and terminal propagation, including all U-RT-159 Runtime source,
criteria 1-3, 5-6 and 8, and the synthesized-leaf propagation portion of criterion 4. Unit 2 adds
the CP gate-refusal producers needed for criterion 4's final real-leaf witness and the public test
(criterion 7). Criterion 4 therefore crosses both portions; the final real-dispatcher, real-leaf
witness remains owed at the applicable source head.
