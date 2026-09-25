---
artifact: design-substrate/Spec_Control_Plane_v1_123.md
version: v1.123
cleared_at: 2026-09-25T09:30:09-06:00
clearance_status: cleared
clearance_type: local-isolated-source-contract-after-independent-review
back_reference:
  - "CP v1.123 final committed spec SHA256 be9a181b8a1ddaad3eefb400ed27227fb61d4922702cbc01516379cb119555b1 (spec commit 49fa023f8cb4414d17f797c63cf9f3e41308ed16)"
  - "ratified B-104 operator terms evaluation/production-readiness-arch/b104-operator-amendment-proposal-1.md"
  - "CP source correction 3b5100052d82eda703e0866ab7aaf40e5ce114b5 (refusal recorded before a barrier deadline stays FAILED under proceed); independent Opus source GO evidence-b104-refusal-deadline-opus-review-1/SHA256SUMS SHA256 c6a5304cf43693211e5e8359288d7e409e68a875a9b266d703eb47782c36bb6e"
  - "independent Opus CP v1.123 HOLD evidence-b104-cp-v123-opus-review-1/SHA256SUMS SHA256 640e695e1e97beb8d635e3c47dc0d8a123d59929018050567f50a6ee5e6a15c2"
  - "independent Opus CP v1.123 delta GO evidence-b104-cp-v123-opus-delta-review-1/SHA256SUMS SHA256 d6667d3daef9611e0200eace262665bef5ad80206414f2db7fc7626e9b1c1c28"
  - ".harness/clearance/spec-control-plane-v1-122-cleared-2026-09-25.md (predecessor)"
merge_commit: pending
reviewer_chain:
  - "Claude Sonnet 5/medium drafted and revised the CP v1.123 delta from the reviewed 3b51000 source"
  - "Claude Opus 5.5/high independently found three blocking spec evidence/scope defects and cleared the corrected draft"
supersedes: spec-control-plane-v1-122-cleared-2026-09-25.md
---

# Control Plane v1.123 local source-contract clearance

This delta gives the Control Plane its own contract for a refused durable paused child: the six
`ChildResumeRefusal` values, `ChildResumeRefusedError` with `audit_signing_failed`, the
family-specific sorted-reasons fail class, and the terminal FAILED outcome. Under `proceed` it orders
a refusal recorded before the barrier ends ahead of the deadline (PARTIAL) and ahead of the
paused-child-not-resumable check, records the ledger terminals, and states that the precedence and the
audit-signing suffix apply only to a refusal recorded before the barrier ends.

This is isolated source-contract clearance only. It is not local-RC composition, installed acceptance
or production acceptance. Runtime v1.129 is a pending paired successor: it still owes its revision to
cite this delta and to carry the recorded-before-deadline limit. Pause and cascade-cancel refusal
behaviour is source-traced only (the pause-tier tests have no passing run; cascade-cancel is untested),
the full refusal test file has no passing run, and the Task 5 claim/started gateway, installed crash
proof, S5 state-root durability and product-main or VM landing remain open.
