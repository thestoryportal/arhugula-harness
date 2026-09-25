---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.128
cleared_at: 2026-09-25T05:30:53-06:00
clearance_status: cleared
clearance_type: local-isolated-source-contract-after-independent-review
back_reference:
  - "Runtime v1.128 draft spec SHA256 22d76f563319d7549a064c3855b44a079d78ecb2ad0d8dbcf4e966763789c53b"
  - "Claude corrected DENY source commit 8fad2178bf34a257897a6b44e457b9c0bdb7e334; independent Codex source GO docs/orchestration/review-evidence/tool-loop-deny-codex-delta-1/SHA256SUMS SHA256 16d80c4b0da95f44c99ce60ef3d8d2b15cd049d2782bd14126bf1bf7b1a943e8"
  - "Opus premerge spec HOLD evidence-deny-runtime-v128-integration-review-opus-1/SHA256SUMS SHA256 be93eef69fe55ca27fb925a9fd8edf7f435847d7ddc79e24eed3ad0c1686a409; corrected spec delta GO evidence-deny-runtime-v128-spec-delta-review-opus-1/SHA256SUMS SHA256 519a3b5aab8f48e869149314b7a8d69246098be6eaf5915c57b20f01b423526f"
  - "Buford isolated integration source commits 993807143a8e27e8921d84961dad5684891ff2ee and 3995c85adf981deff4465006960542f643c29c29"
merge_commit: pending
reviewer_chain:
  - "Claude Sonnet authored and corrected the Anthropic DENY source slice"
  - "Codex Sol/medium independently reviewed the corrected source GO"
  - "Buford reconciled Runtime v1.128 with the existing B-104 v1.127 terms"
  - "Claude Opus 5.5/high independently reviewed the draft HOLD and corrected spec delta GO"
supersedes: spec-harness-runtime-v1-127-cleared-2026-09-25.md
---

# Runtime spec v1.128 local source-contract clearance

This version describes C-RT-38 as implemented on the non-memory Anthropic
model tool-call path. It preserves the v1.127 B-104 claim recovery contract.
Buford's provider-free isolated checks passed 75 DENY focused cases and 190
B-104/state-placement compatibility cases; three async continuation cases
stalled in this local runner on both source and integration branches and are
not counted as passes.

This marker clears the reviewed source contract for local RC consumption. It
does not establish model-emitted tool-call enforcement on first-release local
Ollama or subscription-CLI paths, C-CP-20 operator-response audit, CP
hash-seed-stable rewrite keys, independent dynamic continuation proof,
installed/live behavior, S5 state-root durability or production acceptance.
