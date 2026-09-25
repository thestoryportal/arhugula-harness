---
artifact: design-substrate/Spec_Control_Plane_v1_124.md
version: v1.124
cleared_at: 2026-09-25T12:16:35-06:00
clearance_status: cleared
clearance_type: local-isolated-source-contract-after-independent-review
back_reference:
  - "CP v1.124 final candidate spec SHA256 f85d4dd561b6e7c967b5d7ffa1a44949c62b2c503b37c5fd351df4f1a22d8a89; reviewed author source 79ca281a065b3f5fc487e702cf48baa13d207573"
  - "paired Runtime v1.130 final candidate spec SHA256 ef7592cbb2ad9045ff3f7130978dcedcc912317646126e6d81711e5000b0383b; reviewed author source ca008c658702ce08720cdaaa9ba054d9be00c36c"
  - "independent Opus CP v1.124 delta GO evidence-b104-cp-v124-opus-delta-recheck-1/SHA256SUMS SHA256 877c8745cfd38d248d685540de16845649e688084488ba9cd99700b57d39e116"
  - "independent Opus Runtime v1.130 final phrase GO evidence-b104-runtime-v130-opus-final-delta-1/SHA256SUMS SHA256 0e62f1fb31a321a104d751acfecfc79e98ff090dcba5d19790832458ea841ccf"
  - ".harness/clearance/spec-control-plane-v1-123-cleared-2026-09-25.md (predecessor)"
  - ".harness/clearance/spec-harness-runtime-v1-130-cleared-2026-09-25.md (paired marker)"
merge_commit: pending
reviewer_chain:
  - "Claude Sonnet 5/medium drafted and corrected CP v1.124 in the isolated author worktree"
  - "Claude Opus 5.5/high independently reviewed the corrected CP delta and gave GO to marker"
  - "Codex Sol/medium assembled this paired marker candidate for an independent final delta recheck"
supersedes: spec-control-plane-v1-123-cleared-2026-09-25.md
---

# Control Plane v1.124 local source-contract clearance

This delta adds the three claim/start refusal values to the closed child-resume vocabulary and
publishes one snapshot-hash verification authority. The paired Runtime v1.130 contract specifies
the claim store, unbound gateway and typed refusal mapping. The final spec SHA256 values above
bind this marker to the paired candidate bytes.

This is isolated source-contract clearance only. S1 source remains outside the local RC and no
production binding admits a durable paused child. This marker does not assert RC integration,
installed crash proof, live-device acceptance or product-main and VM landing.
