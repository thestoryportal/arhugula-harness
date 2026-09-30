---
artifact: design-substrate/Spec_Information_Substrate_v1.md
version: v1.16
cleared_at: 2026-09-25T03:09:20-06:00
clearance_status: cleared
clearance_type: local-RC-source-contract-after-independent-review
back_reference:
  - "operator-ratified B-104 first-release terms: evaluation/production-readiness-arch/b104-operator-amendment-proposal-1.md"
  - "Opus Task 6a amendment: arhugula-harness-trial-193 cmt-6d3c8a9b-c5a7-4255-b12b-2ec6718b2a2a; source commit faceb1e12719b074ef587823705cb11515d7b146"
  - "independent Codex source GO: arhugula-harness-trial-193 cmt-85bfce91-97f0-4c94-96bb-266c6072798d; docs/orchestration/review-evidence/b104-task6a-codex-2/SHA256SUMS SHA256 eb34c41dfcd40e79820d2d19baec56e27bde347b4e6b293fc42c1448bdd44e6a"
  - "local RC spec SHA256 e65750acd60ddec4ed581f0df9d29b32d526605aecab8c42117c1ac90a512d08"
merge_commit: pending
reviewer_chain:
  - "operator ratification of B-104 at-most-once claim terms"
  - "Claude Opus 5.5/high authored the bounded §5.7 amendment"
  - "Codex Sol/medium independently reviewed final claim-scoped source and IS v1.16"
supersedes: spec-information-substrate-v1-15-cleared-2026-09-24.md
---

# Information Substrate spec v1.16 local RC clearance

C-IS-05 §5.7 requires typed quiescence attestation for a claim-scoped abandon at
both INTENT and COMPLETE. The IS schema refuses an unattested abandon. The
record-scoped rule and existing field, hash, JSONL, key and writer contracts
remain unchanged.

This marker clears the reviewed source contract for local RC consumption. It
does not establish process-kill, power-loss, installed, live, S5 host-storage or
production acceptance.
