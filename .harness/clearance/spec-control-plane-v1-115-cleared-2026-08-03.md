---
artifact: design-substrate/Spec_Control_Plane_v1_115.md
version: v1.115
cleared_at: 2026-08-03T00:00:00-04:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/class_2_fork_b107_empty_fence_key_resolution_refusal.md §11
  - .harness/forward-register.yaml row B-107
merge_commit: pending
reviewer_chain:
  - operator ratification of Reading A-hybrid
  - spec-writer apply pass
supersedes: spec-control-plane-v1-114-cleared-2026-08-01.md
---

# Clearance — `Spec Control Plane v1.115`

v1.115 ratifies the B-107 A-hybrid CP contract: empty keys leave scalar eligibility, empty map
keys refuse at ordinary construction through a validated immutable copy, and every resolver consult
makes an empty key inert before map-hit or eligibility logic. The field change reuses B-101(a)'s
compatibility-cost analysis but does not implement its closed variant discriminator: B-101 stays
separately closed under (b)-PLUS, with its promotion trigger unchanged, and the rows are not merged.

The union remains 4 variants / 10 shapes / 7 carriers; no Runtime §30 class, Runtime delta, or CXA
row is owed. U-CP-64 implementation and witnesses remain separately owed, so B-107 is not closed.
