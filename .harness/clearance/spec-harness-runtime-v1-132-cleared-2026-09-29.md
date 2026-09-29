---
artifact: design-substrate/Spec_Harness_Runtime_v1_132.md
version: v1.132
cleared_at: 2026-09-29T15:43:18-06:00
clearance_status: cleared
clearance_type: spec-writer-apply-pass
back_reference:
  - "Runtime v1.132 spec SHA256 624ce77027e0646f4439fb99463c7b51b73356edd822ab5df29cb0424a814db7; v1.131 remains unchanged"
  - "PR #1616 integrated Runtime first-match and descendant-placement correction, reviewed at base fb896e36e0569a1f47059b854e98a9dbdebdc39e plus the exact ten-file manifest"
  - "Independent Opus GO: docs/orchestration/review-evidence/buford-continuation-01a0e147/pr1616-runtime-firstmatch-review2/reviewer-verdict-actual.txt SHA256 b11ef5d65c13ccdd4ffc27a3f819e0d537badba81d0a16b6ce8b9dbb9f89cc71"
  - "Exact reviewed file manifest: docs/orchestration/review-evidence/buford-continuation-01a0e147/pr1616-runtime-firstmatch-review2/files-current.json SHA256 2f5b16f52ace1891f447de5b0d84224891722fe31660c100de4a0bed3c0a8344"
  - ".harness/clearance/spec-harness-runtime-v1-131-cleared-2026-09-29.md (predecessor)"
merge_commit: pending
reviewer_chain:
  - "Buford GPT-6-sol/high authored the integrated Runtime source/spec correction and exact-byte evidence"
  - "Claude Opus 5.5/high independently reviewed the production path, test correction, B-165 residual, and v1.132 wording and gave GO"
  - "Buford verified all ten frozen file hashes; provider-free full Runtime suite passed 4986, 2 skipped, 40 deselected, 1 xfailed"
supersedes: spec-harness-runtime-v1-131-cleared-2026-09-29.md
---

# Runtime v1.132 source-contract clearance

This version aligns the Runtime child runner and gate composer with cleared CP v1.120: the folded ancestor-first PRE_ACTION prefix reaches real child and grandchild CP entry, and the first exact-filter match governs normal dispatch and durable-resume Step 0. The independent reviewer found the real descendant witness sufficient for CP §0.5 and confirmed the remaining same-position SUB_AGENT_BOUNDARY collision stays open under B-165. A pre-change child under a parent PRE_ACTION prefix fails closed on the ordered gate-config hash when resumed; production stage 5 still refuses durable child admission.

Clearance is limited to the integrated source contract. The reviewer did not independently run tests or verify file hashes; Buford verified those exact bytes and ran the provider-free Runtime suite. Composite verification, fresh PR CI, merge-gate dispositions and lenses, main and post-main CI, and installed acceptance remain separate gates.
