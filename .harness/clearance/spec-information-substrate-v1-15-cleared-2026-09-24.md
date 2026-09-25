---
artifact: design-substrate/Spec_Information_Substrate_v1.md
version: v1.15
cleared_at: 2026-09-24T18:51:50-06:00
clearance_status: cleared
clearance_type: spec-writer-apply-pass
back_reference:
  - "B-104 operator-ratified proposal SHA256 b3ca465ec67a88b4f68a45662e49694659d22551aa0d8a7cf5205be25145de29; LIT cmt-00d96fe1-8671-4eeb-bc32-d0a522ac5449"
  - "Task 1 independent GO: evidence-b104-is-audit-delta-review-opus-1/SHA256SUMS SHA256 07d344497e1077e5395c9d91c08a68ac802daa1847eb78f1ff47a3f868d4a95a; LIT cmt-bdbdcca2-d4b7-4e32-8a5d-2c6d6f5c8b39"
  - "Task 2 Opus preimplementation review: evidence-b104-is-audit-task2-design-review-opus-1/SHA256SUMS SHA256 37a0d383a21cc5a52639c71ad207953ddc55a9e7de35e7a1f9ed0fe4e4510e90; LIT cmt-f829583a"
  - "Task 2 reviewed brief SHA256 69121665b72d5b8d3cd8d7d0748618173035ffc8df734d4fcc8fbca0d0d81df9; LIT cmt-a4fa6284-5c44-42dc-9f96-bed27e622d60"
  - "Task 2 independent source GO/P2: evaluation/production-readiness-arch/evidence-b104-is-audit-task2-delta-review-opus-1/SHA256SUMS SHA256 7b1bfe4227a6a75191c3f805ee7da01b8ff0f338c3874f595010dc1eb3dfac93; LIT cmt-473a089a-095b-4b1d-acdd-37da60ae2613"
  - "Task 2 independent P2 closeout GO: evaluation/production-readiness-arch/evidence-b104-is-audit-task2-closeout-review-opus-1/SHA256SUMS SHA256 e28d17c196f258c5a00ca3c59026b6a5f748686c56af567a893b96f7ce8693fa; LIT cmt-b7f57030-591b-4556-84b5-4991e9cbaed0"
  - "Final v1.15 spec SHA256 229916df47247b5d68cfbec0e98c95adfc4b5c4093a530a66e90a68133f33901"
merge_commit: pending
reviewer_chain:
  - "operator ratification of B-104 proposal"
  - "independent Task 1 changed-line GO"
  - "independent Task 2 preimplementation corrections incorporated into dispatch"
  - "independent Task 2 source GO with P2 spec-limit correction incorporated"
  - "independent Task 2 P2 closeout changed-line GO"
supersedes: spec-information-substrate-v1-14-cleared-2026-09-24.md
---

# Clearance — Information Substrate spec v1.15

C-IS-07 §7.8 specifies one IS-owned durable recovery-audit append operation.
It fixes the derived key and action encoding, whole-ledger integrity admission,
stable duplicate comparison, writer-owned timestamp, whole-line write, and
file/parent/grandparent sync order. Ordinary append refuses the audit sidecar
and retains its earlier behavior. C-IS-06 §6.4 remains unchanged.

This marker records the specification apply pass, the independent Task 2 source GO,
and the independently reviewed P2 limit correction. Integration remains pending.
It does not attest to installed recovery, power-loss durability, or production
acceptance.
