---
artifact: design-substrate/Spec_Control_Plane_v1_132.md
version: v1.132
cleared_at: "2026-11-09T04:47:09+00:00"
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - ".harness/class_1_fork_operator_approval_collection.md"
  - "LIT arhugula-harness-trial-193 cmt-1802376e-01d6-43d6-96dc-928e87271e38"
  - "LIT arhugula-harness-trial-193 cmt-d4450204-4f4f-4b8a-866d-a224f0634abf"
  - "PR #1735"
merge_commit: pending
reviewer_chain:
  - "profile-reviewer T02 independent contract GO cmt-9ded37e9; five prior contract passes retained"
  - "Buford T02 fork ratification cmt-1802376e"
  - "implementer T03 independent source review cmt-d8f06a38, cmt-9ae1d515 and cmt-54fa4480; original findings and passes retained"
  - "Buford source-consumption clearance and C4 disposition cmt-d4450204"
---

# Clearance — Control Plane v1.132

CP v1.132 carries one pending HITL decision to the resumed root step and keeps keyed response maps for child runs. Buford accepted removal of the unused hitl_delivery_for helper prescription because its root-keyed lookup conflicted with existing uniform-response precedence. The one-shot cell and root-owned response authority remain.

This marker establishes source consumption after the independent contract and T03 reviews and Buford's clearance decision. Exact-final-head CI, safe merge, own-main CI, installed acceptance, and the separate A4 inherited-gate outcome remain open.
