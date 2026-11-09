# Spec: Control Plane — v1.132 (delta over cleared v1.131)

*Delta-only file. One amendment site: C-CP-26 §26.8.1 `ResumeContext` and its HITL delivery
(`harness-cp/src/harness_cp/pause_resume_protocol_types.py:1364`, `:1456`, `:1581-1620`,
`:1640-1685`), with one new value in `harness_cp.hitl_placement`. Every other v1.131 and earlier
C-CP-01 … C-CP-29 term remains in force. No `RunStatus` value, `HITLResponse` member, pause-snapshot
hash byte or fail-class prefix is added or changed.*

**Status: PROPOSED — contract ratified with Runtime v1.144 at LIT `arhugula-harness-trial-193`
`cmt-1802376e-01d6-43d6-96dc-928e87271e38`; review rides the T03 frozen candidate. Not cleared.**

**Authority:** C4 of `.harness/class_1_fork_operator_approval_collection.md` at
`ce46421ab851253d87bff5b3d5e477254b522ee0` (SHA256
`01adf206f582baeb2aedf72bb1f65c9aa9ac5a1b317257a34aec9ad9155f9ca2`), adopted verbatim for the
CP-owned terms below.

## §1 `PendingHITLDecision` (NEW, `harness_cp.hitl_placement`)

Frozen, extra forbidden: `kind: Literal["pending"]`; `response: HITLResponse`
(approve/edit/reject/respond); `edited_proposal_payload: dict[str, Any] | None`, required for and
only for edit; `response_text: str | None`, required for and only for respond;
`rejection_reason: str | None`. It carries no timestamp, hash or audit identity: the resumed gate
assigns those (Runtime v1.144 §2, §14.8.8.5).

## §2 `ResumeContext` (AMENDED)

- New field `pending_hitl_decision: PendingHITLDecision | None = None`.
- A model validator refuses it together with `hitl_response` or `hitl_responses`, so exactly one
  of the three carries a response.
- `hitl_response_for` is unchanged and never returns the pending value.
- The depth-0 root's resumed step (`step_index == resume_at`) consumes the uniform
  `hitl_response` or `pending_hitl_decision`. It does not read `hitl_responses`, which addresses
  children by their run IDs. Child runners keep `hitl_response_for` and never receive a pending
  decision.
- The v1.112/v1.114 response-provenance carrier is unchanged. It fences keyed child response maps;
  the pending value addresses only the root's own gate and is built inside the root admission from
  the same durable snapshot read.

**T03 review disposition:** Ratified C4 named `hitl_delivery_for(run_id)`, but its required
`hitl_response_for(run_id)` lookup lets a map entry keyed by the root run ID override the root's
uniform response. That conflicts with the existing root precedence in
`test_workflow_driver_hitl_uniform_fallback_property4.py`. The method had no caller and is removed
in this candidate. Independent review and Buford must accept this explicit contract correction
before this proposed CP delta is cleared.

## §3 `HITLDeliveryCell` (AMENDED)

`_value` and `consume_and_clear()` widen to `HITLResult | PendingHITLDecision | None`. One cell per
resumed step, read-and-clear unchanged, so a pending value is consumed at most once. A stored
`HITLResult` behaves exactly as before.
