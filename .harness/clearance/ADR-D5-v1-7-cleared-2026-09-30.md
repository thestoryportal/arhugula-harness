---
artifact: design-substrate/ADR-D5_v1_7.md
version: v1.7
cleared_at: 2026-09-30T00:14:15-06:00
clearance_status: cleared
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - ".harness/class_1_fork_pr1616_local_signer_and_runtime_plan.md"
  - "PR #1616"
  - "LIT arhugula-harness-trial-193 cmt-d177b0f9-19a1-4bc3-a0db-7df8844d1936 (Buford disposition)"
  - "design-substrate/ADR-D5_v1_7.md SHA256 e4262f3a218c7352ae869f2823343a6d1c57757d5e64d6248f3b5c4b997ab84e"
merge_commit: "pending (recorded at PR #1616)"
reviewer_chain:
  - "Claude Opus 5.5/high draft design closure cmt-a6d57693-e701-4c43-a308-522bac76bf60 (draft only)"
  - "Claude Opus 5.5/high final CP/design review at ca5bb41, native verdict SHA256 fd2e9584bad495423e30618e477ae48a52f5457b5e2694327b162a98febbb5c4 (qualified GO, P2 found)"
  - "Claude Opus 5.5/high narrow re-review at 340578c, native verdict SHA256 9f6d0ab5447bdc053702f4920cba70755bd09ef061fa026c4d375278ab020b3e (P2 closed; no file hashes or tests run)"
  - "Buford GPT-6-sol/high exact-byte hash and clean-head attestation; provider-free affected suites 147 Runtime / 153 CP passed; full composite and CI separate"
supersedes: ADR-D5-v1-6-cleared-2026-08-09.md
---

# Clearance — ADR-D5 v1.7 lower-tier key residence

The solo/team signing-key residence rows now admit the explicit local signer under ADR-F5 v1.2 and ADR-D8 v1.1. The team OS-keychain backend is labeled an unbuilt target; the current Runtime default remains none. The MTC row and audit-chain format do not change.

The local-to-MTC dual-signed transition is not implemented. The first-release operator gate R-AUDIT-TRANSITION-01 prohibits an in-place tier upgrade; no source MTC+KMS history guard or installed continuity witness is claimed.
