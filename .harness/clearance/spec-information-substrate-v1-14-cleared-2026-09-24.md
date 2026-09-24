---
artifact: design-substrate/Spec_Information_Substrate_v1.md
version: v1.14
cleared_at: 2026-09-24T16:25:57-06:00
clearance_status: conditional_pending_independent_delta_review
clearance_type: spec-writer-apply-pass
back_reference:
  - "B-104 operator-ratified proposal SHA256 b3ca465ec67a88b4f68a45662e49694659d22551aa0d8a7cf5205be25145de29; LIT cmt-00d96fe1"
  - "B-104 seven-slice plan v2 SHA256 0591218da7269998f62d05af05b0ce738f94ac12fcd6ca4247acecc4288cb5f5"
  - "Task 1 independent NO-GO review: evidence-b104-is-audit-review-opus-1/SHA256SUMS SHA256 11a5aac6908f5e8c473accc2fdcb2ad13bd0160c7dbc9ad59ef5d0ed9d73c134"
  - "Final Task 1 changed-line review: pending independent Opus delta review"
merge_commit: pending
reviewer_chain:
  - "operator ratification of B-104 proposal"
  - "independent Opus Task 1 review at fd60a8c: NO-GO; B1/B2 and supporting fixes assigned"
  - "independent Opus changed-line delta review: pending"
supersedes: spec-information-substrate-v1-13-cleared-2026-08-07.md
---

# Conditional clearance — Information Substrate spec v1.14

The B-104 Task 1 amendment adds a versioned recovery audit sidecar to C-IS-05,
C-IS-06, and C-IS-07. This revision records an explicit null tenant for the
untenanted journal, digest-shaped subject identity, bounded action ID, structured
lease generation and inode identity, UTC attestation, and strict JSONL reading.
Entries without the sidecar retain their prior canonical and JSONL bytes.

This marker records the operator-ratified back-flow and the correction to the
independent Task 1 NO-GO findings. Clearance remains conditional until the
independent changed-line review approves this revision and Buford records its
exact reference here. Task 2 owns durable audit append and ordinary-append
refusal; this marker does not accept those behaviors or installed runtime use.
