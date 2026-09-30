---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.126
cleared_at: 2026-09-25T00:10:55-06:00
clearance_type: local-RC-implementation-contract-pending-independent-review
back_reference:
  - "arhugula-harness-trial-193 cmt-4be814c8-563a-46ef-b5a3-a04d92f51e29"
  - "evaluation/production-readiness-arch/evaluator-accept-first-release-decision-1.md"
  - "evaluation/production-readiness-arch/evidence-evaluator-verdict-runtime-preflight-opus-1/review-verbatim.md"
reviewer_chain:
  - "Opus 5.5/high current-source design GO at a699b699; implementation review pending"
supersedes: spec-harness-runtime-v1-125-cleared-2026-09-24.md
---

# Runtime spec v1.126 local clearance

This amendment records the Ollama-only evaluator verdict reader and its bootstrap binding on both mutable and frozen contexts. It uses CP's existing strict verdict type and malformed FAILED/drain path. It does not change CP or IS, the stored raw provider output, the ledger format, or the success status at the rejection cap. The pending independent source review and installed Ollama witness remain separate gates.
