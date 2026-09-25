---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.124
cleared_at: 2026-09-24T21:00:00-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - "arhugula-harness-trial-193 cmt-141176ca-076e-42f9-9b33-ca555307ce70"
  - "arhugula-harness-trial-193 cmt-e01c329f-e0e2-4f27-aed2-47272e9ed46c"
  - "evaluation/production-readiness-arch/plans/2026-09-24-b104-durable-hitl-task3-v3.md SHA256 7fd593c3d68486aff8c8653ddc4e7918a6b4dc40ad3b832d8b0da74d799eff07"
  - "evaluation/production-readiness-arch/assignment-b104-task3b-claim-store-sol-1.txt SHA256 c506617687df53f66791300e9d917c8b1b4c2c5d774bf2a22e64baa24a0ced15"
  - "evaluation/production-readiness-arch/assignment-b104-task3b-stale-delta-sol-1.txt SHA256 b2922502ef905f40abf4ef2536f1f20ebe128a2cd9148133529ea6f369dd30ae"
merge_commit: pending local RC integration
reviewer_chain:
  - "Claude Opus 5.5/high independent Task 3a source review GO, 2026-09-25"
  - "Codex Sol/medium Task 3b behavioral RED/GREEN, 2026-09-24"
  - "Independent Task 3b source review of 12c462b identified stale-record and lease-byte corrections; delta review pending"
supersedes: spec-harness-runtime-v1-123-cleared-2026-09-24.md
---

# Clearance — Runtime spec v1.124

This amendment specifies the exact-record lease publication and sticky claim admission in Task 3b. It does not add an execution gateway or a `started` write. Only the latest valid journal record is claimable. Lease bytes must match their canonical encoding. Partial claims and invalid leases hold admission; no recovery transition is authorized in this slice. The source awaits independent review and installed crash acceptance.
