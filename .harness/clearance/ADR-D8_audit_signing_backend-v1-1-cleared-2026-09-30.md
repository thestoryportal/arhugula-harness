---
artifact: design-substrate/ADR-D8_audit_signing_backend_v1_1.md
version: v1.1
cleared_at: 2026-09-30T00:14:15-06:00
clearance_status: cleared
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - ".harness/class_1_fork_pr1616_local_signer_and_runtime_plan.md"
  - "PR #1616"
  - "LIT arhugula-harness-trial-193 cmt-d177b0f9-19a1-4bc3-a0db-7df8844d1936 (Buford disposition)"
  - "design-substrate/ADR-D8_audit_signing_backend_v1_1.md SHA256 b6629276c33320c48124ac39f95db6a3b4ef813804ce1a745d18a572e527490d"
merge_commit: "pending (recorded at PR #1616)"
reviewer_chain:
  - "Claude Opus 5.5/high draft design closure cmt-a6d57693-e701-4c43-a308-522bac76bf60 (draft only)"
  - "Claude Opus 5.5/high final CP/design review at ca5bb41, native verdict SHA256 fd2e9584bad495423e30618e477ae48a52f5457b5e2694327b162a98febbb5c4 (qualified GO, P2 found)"
  - "Claude Opus 5.5/high narrow re-review at 340578c, native verdict SHA256 9f6d0ab5447bdc053702f4920cba70755bd09ef061fa026c4d375278ab020b3e (P2 closed; no file hashes or tests run)"
  - "Buford GPT-6-sol/high exact-byte hash and clean-head attestation; provider-free affected suites 147 Runtime / 153 CP passed; full composite and CI separate"
supersedes: ADR-D8_audit_signing_backend-cleared-2026-07-16.md
---

# Clearance — ADR-D8 v1.1 first-release local signer boundary

This version permits explicitly selected local-ed25519 signing at solo/team and forbids that backend at MTC, where the existing KMS decision remains in force. The first self-hosted Omarchy profile selects solo/team, retains tenant isolation and redaction, and defers MTC.

The local key is readable by the harness OS user. The shipped lower-tier Runtime strips content attributes by default, but a direct OD caller may narrow them; installed redaction, tenant isolation, key residence, B1/B2 and restart/tamper remain separate gates.
