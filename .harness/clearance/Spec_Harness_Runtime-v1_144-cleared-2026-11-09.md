---
artifact: design-substrate/Spec_Harness_Runtime_v1_144.md
version: v1.144
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

# Clearance — Harness Runtime v1.144

Runtime v1.144 applies the ratified B-315 operator approval contract to the Python, one-shot CLI, and daemon MCP ingresses. It adds the 900-second default elicitation deadline, operator outcomes, attributable spans, and one-shot resume delivery without a new approval store. The C4 root-delivery wording follows the accepted CP v1.132 correction recorded at cmt-d4450204.

This marker establishes source consumption after the independent contract and T03 reviews and Buford's clearance decision. Exact-final-head CI, safe merge, own-main CI, installed acceptance, and the separate A4 inherited-gate outcome remain open.
