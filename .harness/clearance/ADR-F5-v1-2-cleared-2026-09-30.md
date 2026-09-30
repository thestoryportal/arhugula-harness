---
artifact: design-substrate/ADR-F5_v1_2.md
version: v1.2
cleared_at: 2026-09-30T00:14:15-06:00
clearance_status: cleared
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - ".harness/class_1_fork_pr1616_local_signer_and_runtime_plan.md"
  - "PR #1616"
  - "LIT arhugula-harness-trial-193 cmt-d177b0f9-19a1-4bc3-a0db-7df8844d1936 (Buford disposition)"
  - "design-substrate/ADR-F5_v1_2.md SHA256 f35d1f3e1592a53f8ab4386d5da0e5da7e491889d08c1217830280d26f111de5"
merge_commit: "pending (recorded at PR #1616)"
reviewer_chain:
  - "Claude Opus 5.5/high draft design closure cmt-a6d57693-e701-4c43-a308-522bac76bf60 (draft only)"
  - "Claude Opus 5.5/high final CP/design review at ca5bb41, native verdict SHA256 fd2e9584bad495423e30618e477ae48a52f5457b5e2694327b162a98febbb5c4 (qualified GO, P2 found)"
  - "Claude Opus 5.5/high narrow re-review at 340578c, native verdict SHA256 9f6d0ab5447bdc053702f4920cba70755bd09ef061fa026c4d375278ab020b3e (P2 closed; no file hashes or tests run)"
  - "Buford GPT-6-sol/high exact-byte hash and clean-head attestation; provider-free affected suites 147 Runtime / 153 CP passed; full composite and CI separate"
supersedes: null
---

# Clearance — ADR-F5 v1.2 signing-only exception

The F5 general secret-fetch rule remains in force. This version permits an explicitly selected, file-backed Ed25519 audit key only below MTC; it is not a general F5 provider and has no per-access F5 fingerprint. The private PEM must reside outside Git at installation, which current source does not detect.

MTC delegated signing remains unchanged. This marker clears the bounded design authority, not key provisioning, signer enablement, compromised-user resistance or installed audit-integrity evidence.
