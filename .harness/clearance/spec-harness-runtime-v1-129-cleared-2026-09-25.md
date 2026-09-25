---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.129
cleared_at: 2026-09-25T09:51:16-06:00
clearance_status: cleared
clearance_type: local-isolated-source-contract-after-independent-review
back_reference:
  - "Runtime v1.129 final committed spec SHA256 997ceaec1d314ba5f2a7c3a422e16f38642f251561728ad672c5334f5d2b274b (spec commit 5b88a2b4960343cd73faa2ccda69b2873af5a87d); reviewed draft revision commit 7520310d7917f65df556c4c6e5cf95832c6693ff, spec SHA256 baff6b1751f1c8fde42fdc215de831d6ef419fc7b64aaef4eb7235a03c5c59f9"
  - "paired cleared Control Plane contracts: .harness/clearance/spec-control-plane-v1-122-cleared-2026-09-25.md and .harness/clearance/spec-control-plane-v1-123-cleared-2026-09-25.md"
  - "ratified B-104 operator terms evaluation/production-readiness-arch/b104-operator-amendment-proposal-1.md"
  - "author revision seal evidence-b104-runtime-v129-revision-sonnet-1/SHA256SUMS SHA256 90d1372eb16d30b8ff007c68254b0a1ca34a686c7045a79a2b45b39b9f635ff2"
  - "independent Opus Runtime v1.129 draft HOLD evidence-b104-task4-runtime-v129-review-opus-1/SHA256SUMS SHA256 d84dd24ff65ff4bc0b8d166e70a3b8f63f827f9a1670dd661696aaf593c266a2"
  - "independent Opus Runtime v1.129 delta GO evidence-b104-runtime-v129-opus-delta-review-1/SHA256SUMS SHA256 5ab8388e59f189bf0a1e4796265b42ca392ed4d9d6024b0c3ccf27e19b92199d"
  - ".harness/clearance/spec-harness-runtime-v1-128-cleared-2026-09-25.md (predecessor)"
merge_commit: pending
reviewer_chain:
  - "Claude Sonnet 5/medium drafted and revised the Runtime v1.129 spec from the reviewed Task 4 source"
  - "Claude Opus 5.5/high independently found blocking spec defects in the draft and cleared the corrected delta"
supersedes: spec-harness-runtime-v1-128-cleared-2026-09-25.md
---

# Runtime spec v1.129 local source-contract clearance

This version specifies the Runtime half of B-104 Task 4: numeric-depth durable capture with the exact
record reference, the direct-child and unknown-depth `resume_handle` refusal, exact-record
verification of a durable paused child before the required admission step, the always-refusing
admission binding until the Task 5 gateway, refusal typing and audit-signing precedence under the
Control Plane contract, and the assessment of Runtime-created contexts. It is paired with the cleared
Control Plane v1.122 and v1.123 contracts. C-RT-38 (the Anthropic model tool-call DENY) is unchanged.

This is isolated source-contract clearance only. It is not local-RC composition, installed acceptance
or production acceptance. It does not establish the Task 5 claim, lease, `started` and worker-handoff
gateway, recency proof, audited recovery, a public `pause_record_ref`, a depth refusal for a
caller-supplied `pause_snapshot=`, model tool-call enforcement on Ollama or subscription-CLI paths,
installed crash proof, S5 state-root durability, or any product-main or VM landing. After upgrade every
pre-v1.129 durable record is refused by `resume_handle` (unknown depth is never root). Later Runtime
work, including the Task 5a store contract and model tool-loop slices, takes v1.130 or later.
