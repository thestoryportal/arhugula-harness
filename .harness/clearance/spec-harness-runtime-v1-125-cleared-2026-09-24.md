---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.125
cleared_at: 2026-09-24T22:58:03-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - "arhugula-harness-trial-193 cmt-37bdb28e-3ff0-40c1-96c2-1f9b3aeb6fe2 (assignment-state-root-runtime-spec-claude-1.txt SHA256 b1fbe9408b8f9daea264cdcb603aa9f443b98f2443038cfccf3356c40251f554)"
  - "evaluation/production-readiness-arch/external-state-root-first-release-decision-1.md"
  - "evaluation/production-readiness-arch/evidence-external-state-root-design-opus-1/report.md (SHA256SUMS ce6a736fe922ac8677933680b68907b8f33b56c4ea4a84c76efea592d12b8040)"
  - "evaluation/production-readiness-arch/evidence-state-root-s2-operator-guard-review-opus-1/verdict.md; evidence-external-state-root-s2-review-codex-1"
  - "evaluation/production-readiness-arch/evidence-state-root-vm-preflight-1/report.md (candidate location only)"
merge_commit: pending (this spec-only branch; local RC integration is Buford's)
reviewer_chain:
  - "Opus 5.5/high S2 operator-guard source review GO for cd858d1 (merged into local RC e104d9c)"
  - "independent Codex S1/S1-delta/S2 source reviews GO (evidence-external-state-root-*-review-*)"
  - "out-of-family Codex review of THIS spec delta — PENDING; this marker is not independently final until it returns GO"
supersedes: spec-harness-runtime-v1-124-cleared-2026-09-24.md
---

# Clearance — Runtime spec v1.125 (external persistent state root, C-RT-36)

This amendment specifies the behavior of the reviewed, integrated S1+S2 external state-root code: the optional `RuntimeConfig.state_placement` carrier, the stage-1 verifier call before the path registry, the `VerifiedStateRoot` stamp on `HarnessContext`, the 21 typed refusal reasons, the single path derivation, the persistent stores placed under the root, explicit local memory override refusal, and `OPERATOR_DEFINED` memory refusal before import or construction. With `state_placement` unset behavior is unchanged.

It does NOT claim: the durable claim gateway and recovery revalidation (S3), example/profile configuration and documentation (S4), the installed-host witness (S5), acceptance of the VM candidate location, classification of `audit_cutover_record_path` (an open operator/spec item), or the CLI exit behavior for a refused placement (UNVERIFIED). No source or test changed; the contract was read from the integrated source and its 120 focused tests.
