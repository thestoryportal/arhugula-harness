---
artifact: design-substrate/Spec_Harness_Runtime_v1_133.md
version: v1.133
cleared_at: 2026-09-30T00:14:15-06:00
clearance_status: cleared
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - ".harness/class_1_fork_pr1616_local_signer_and_runtime_plan.md"
  - "PR #1616"
  - "LIT arhugula-harness-trial-193 cmt-d177b0f9-19a1-4bc3-a0db-7df8844d1936 (Buford disposition)"
  - "design-substrate/Spec_Harness_Runtime_v1_133.md SHA256 98190af5ec9f2f4ea8180778976f572a0e4f022f14ef21781d9a099bc55af17a"
merge_commit: "pending (recorded at PR #1616)"
reviewer_chain:
  - "Claude Opus 5.5/high draft design closure cmt-a6d57693-e701-4c43-a308-522bac76bf60 (draft only)"
  - "Claude Opus 5.5/high final CP/design review at ca5bb41, native verdict SHA256 fd2e9584bad495423e30618e477ae48a52f5457b5e2694327b162a98febbb5c4 (qualified GO, P2 found)"
  - "Claude Opus 5.5/high narrow re-review at 340578c, native verdict SHA256 9f6d0ab5447bdc053702f4920cba70755bd09ef061fa026c4d375278ab020b3e (P2 closed; no file hashes or tests run)"
  - "Buford GPT-6-sol/high exact-byte hash and clean-head attestation; provider-free affected suites 147 Runtime / 153 CP passed; full composite and CI separate"
supersedes: spec-harness-runtime-v1-132-cleared-2026-09-29.md
---

# Clearance — Runtime spec v1.133 MTC-local config refusal

C-RT-03 now rejects MTC with local-ed25519 as RT-FAIL-CONFIG in the pure validation pass before backend construction and signing effects. Earlier bootstrap stages may still create the state root or ledger. Solo/team explicit local selection and MTC KMS semantics remain unchanged.

This spec clearance does not enable local signing, prove installed key placement, or certify any MTC transition. The first-release operator procedure at docs/first-release-omarchy-audit-signing.md owns the scope boundary.
