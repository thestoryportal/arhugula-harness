# Spec: Harness Runtime — v1.144 (delta over cleared v1.143)

*Delta-only file. One amendment area: C-RT-18 §14.8 (`Spec_Harness_Runtime_v1_132.md:4829`), as
operator approval collection at the one-shot CLI/Python and daemon-client MCP ingresses. Sites:
§14.8.3 elicitation delivery (`:4910`), §14.8.5 span emission (`:4942`), §14.8.8.5 resume-side
one-shot delivery (`:5174`) and §14.8.9 timeout degradation (`:5234`). v1.133 through v1.143 amend
none of these sites. Every other v1.143 and earlier term remains in force. Cleared predecessor files
are not edited.*

**Status: PROPOSED — contract ratified by the integration lead at LIT `arhugula-harness-trial-193`
`cmt-1802376e-01d6-43d6-96dc-928e87271e38` (independent contract GO
`cmt-9ded37e9-976a-4f79-9b5b-5d491948146a`, five changes-required passes retained). This file
materializes that contract; its review rides the T03 frozen candidate. Not cleared.**

**Authority:** forward-register row B-315; fork record
`.harness/class_1_fork_operator_approval_collection.md` at `ce46421ab851253d87bff5b3d5e477254b522ee0`,
SHA256 `01adf206f582baeb2aedf72bb1f65c9aa9ac5a1b317257a34aec9ad9155f9ca2`.

## §0 Change-note (v1.143 → v1.144)

Before this delta every HITL gate reached through `api.run` was declined, the `harness run --daemon`
client bound no elicitation callback, the server offered no hold, and an elicitation with no
`placement.timeout` could wait without bound. No operator could approve a gate through the harness's
own surfaces. This delta adds that collection without a new H_T primitive, CP palette value,
approval store, claim store or HTTP operator service.

## §1 Normative terms (NEW, C-RT-18 §14.8.12)

The sections **C1, C1a, C2, C3, C3a, C4 and C5** of the fork record named under *Authority*, at the
stated SHA256, are adopted verbatim as C-RT-18 §14.8.12.1–§14.8.12.7 respectively. They are the one
normative text; this file does not restate them. Ratified values:
`OPERATOR_ELICITATION_DEADLINE_SECONDS = 900`, overridden only by an existing `placement.timeout`;
no new configuration surface.

## §2 Amended sites

- **§14.8.3.** The elicitation message is the C1a deterministic text; the schema gains the optional
  `ingress` field; `hold`, `cancel` and `refuse` are surface values parsed before palette validation
  (C1); `ServerCtxElicitCallback` awaits under the C3a deadline.
- **§14.8.5.** `hitl.response.ingress` is set on `hitl.invocation.responded` from the validated reply,
  and on `hitl.invocation.opened` from `AskUserQuestionTimeoutError.ingress` on the cancel/timeout
  path (C5).
- **§14.8.8.5.** The resumed step's one-shot cell may carry a CP `PendingHITLDecision`
  (CP v1.132). Composer step 0 alone turns it into a `HITLResult` with its own step-4h audit
  identity, its clock read, the shared response-summary hash and, for `edit`, the live-derived
  `ProposedAction` with only `payload` replaced (C4).
- **§14.8.9.** `accept hold` with a durable pause binding takes the escalate-pause sequence; without
  one it is an audited REJECT with reason `hold unavailable: no durable pause binding` (C3). Cancel,
  MCP-native `cancel` and deadline expiry keep the existing degradation path.

## §3 Excluded

Child-workflow gates (F5), A4's inherited-gate refusal, human responder identity, any operator
approval store and any HTTP surface. B-315 constraints 1–6 bind unchanged.
