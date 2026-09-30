---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.123
cleared_at: 2026-09-24T19:52:20-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - "arhugula-harness-trial-193 cmt-0468a1d2-1bd8-4dd8-9c01-79f054cb5ebc"
  - "evaluation/production-readiness-arch/plans/2026-09-24-b104-durable-hitl-task3-v3.md SHA256 7fd593c3d68486aff8c8653ddc4e7918a6b4dc40ad3b832d8b0da74d799eff07"
  - "evaluation/production-readiness-arch/evidence-b104-task3-design-review-opus-1/SHA256SUMS SHA256 401d29b84e11c62250d0bdafeb964a8a65aa945d9ef140d888478bacfd6ea40a"
  - "evaluation/production-readiness-arch/evidence-b104-task3a-review-opus-1/SHA256SUMS SHA256 c8d90463db0f1f703ba0316e004d1ccec0a5193c4c623d90f451688210142f9c; LIT arhugula-harness-trial-193 cmt-e1836e57-e265-4441-987f-2c422211ff23"
merge_commit: c882d782af61d5ba491c5479a261e05ada04d0c8 (local integrated RC only)
reviewer_chain:
  - "Claude Opus 5.5/high independent Task 3 design review, 2026-09-24"
  - "Codex Sol/medium Task 3a behavioral RED/GREEN, 2026-09-24"
  - "Claude Opus 5.5/high independent Task 3a source review GO, 2026-09-25; evidence-b104-task3a-review-opus-1"
supersedes: spec-harness-runtime-v1-122-cleared-2026-09-24.md
---

# Clearance — Runtime spec v1.123

This amendment binds one exact pause-journal record reference to the same lock hold as append. It shares the frozen reference through harness-core, uses inspect's raw-byte count and digest, and records unknown ancestry explicitly. Exact positional lookup can still find an older record after a later append.

This clearance covers Task 3a source only. Claim, lease, started barrier, direct-handle depth refusal, installed recovery and power-loss acceptance remain separate work. Journal-directory fsync remains best-effort. Independent source review is GO for local source integration only; installed acceptance remains open.
