---
artifact: design-substrate/Spec_Harness_Runtime_v1_130.md
version: v1.130
cleared_at: 2026-09-25T12:16:35-06:00
clearance_status: cleared
clearance_type: local-isolated-source-contract-after-independent-review
back_reference:
  - "Runtime v1.130 final candidate spec SHA256 ef7592cbb2ad9045ff3f7130978dcedcc912317646126e6d81711e5000b0383b; reviewed author source ca008c658702ce08720cdaaa9ba054d9be00c36c"
  - "paired CP v1.124 final candidate spec SHA256 f85d4dd561b6e7c967b5d7ffa1a44949c62b2c503b37c5fd351df4f1a22d8a89; reviewed author source 79ca281a065b3f5fc487e702cf48baa13d207573"
  - "independent Opus Runtime v1.130 final phrase GO evidence-b104-runtime-v130-opus-final-delta-1/SHA256SUMS SHA256 0e62f1fb31a321a104d751acfecfc79e98ff090dcba5d19790832458ea841ccf"
  - "independent Opus CP v1.124 delta GO evidence-b104-cp-v124-opus-delta-recheck-1/SHA256SUMS SHA256 877c8745cfd38d248d685540de16845649e688084488ba9cd99700b57d39e116"
  - ".harness/clearance/spec-harness-runtime-v1-129-cleared-2026-09-25.md (predecessor)"
  - ".harness/clearance/spec-control-plane-v1-124-cleared-2026-09-25.md (paired marker)"
merge_commit: pending
reviewer_chain:
  - "Codex Sol/medium drafted and corrected Runtime v1.130 in the isolated author worktree"
  - "Claude Opus 5.5/high independently reviewed Runtime v1.130 and gave GO on the final phrase corrections"
  - "Codex Sol/medium assembled this paired marker candidate for an independent final delta recheck"
supersedes: spec-harness-runtime-v1-129-cleared-2026-09-25.md
---

# Runtime v1.130 local source-contract clearance

This version specifies the claim store, phase-typed start and refusal behavior, and an unbound
started-body gateway against the paired CP v1.124 refusal and snapshot-hash contracts. The final
spec SHA256 values above bind this marker to the paired candidate bytes.

This is isolated source-contract clearance only. The combined gateway over the RC store and
parent-worker handoff remain integration work. Stage 5 still binds the refusing admission,
root `api.resume` is not wired to a claim, and installed crash proof, S5 and product-main or VM
landing remain open.
