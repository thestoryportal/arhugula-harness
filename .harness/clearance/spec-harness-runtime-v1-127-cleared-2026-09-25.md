---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.127
cleared_at: 2026-09-25T03:09:20-06:00
clearance_status: cleared
clearance_type: local-RC-source-contract-after-independent-review
back_reference:
  - "operator-ratified B-104 first-release terms: evaluation/production-readiness-arch/b104-operator-amendment-proposal-1.md"
  - "Opus Task 6a source commits 758518e0dad923e9efc52a2c64c43ae03c51a4ea, 076211499e265980d4322f9a030cbf91dcf9ebcb and faceb1e12719b074ef587823705cb11515d7b146"
  - "independent Codex source GO: arhugula-harness-trial-193 cmt-85bfce91-97f0-4c94-96bb-266c6072798d; docs/orchestration/review-evidence/b104-task6a-codex-2/SHA256SUMS SHA256 eb34c41dfcd40e79820d2d19baec56e27bde347b4e6b293fc42c1448bdd44e6a"
  - "Buford local RC correction of the stale C-IS-05 §5.7 MAY sentence after IS v1.16; spec SHA256 0bb5c21a6b7ff60755fc1ec45a2465cbc66ae7a4867d31c3ec2753e04f79f062"
merge_commit: pending
reviewer_chain:
  - "operator ratification of B-104 at-most-once claim terms"
  - "Claude Opus 5.5/high authored Task 6a claim-scoped recovery and corrections"
  - "Codex Sol/medium independently reviewed original HOLD and final source GO"
  - "Buford reconciled the one stale IS §5.7 sentence during local RC integration"
supersedes: spec-harness-runtime-v1-126-cleared-2026-09-25.md
---

# Runtime spec v1.127 local RC clearance

This version pins the Task 6a claim-scoped recovery subject, archive,
tombstone, transition-digest, lease-proof and retry-durability recipes. The
integrated sentence about C-IS-05 §5.7 now matches IS v1.16's required claim
abandon attestation. Record-scoped recovery, CLI/operator visibility, Task 5
gateway and installed crash/recovery proof remain open.

This marker clears the reviewed source contract for local RC consumption. It
does not establish multiprocess, process-kill, power-loss, installed, live, S5
host-storage or production acceptance.
