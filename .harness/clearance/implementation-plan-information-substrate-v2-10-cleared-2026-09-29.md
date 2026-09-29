---
artifact: design-substrate/Implementation_Plan_Information_Substrate_v2_10.md
version: v2.10
cleared_at: 2026-09-29T08:42:02-06:00
clearance_status: cleared
clearance_type: implementation-planner-apply-pass
back_reference:
  - "IS plan v2.10 SHA256 9c517d6297d274042c623e3223feaaf2211db7ab88798d531ec286931a28f2f3; v2.9 remains unchanged"
  - "IS spec v1.16 C-IS-07 §7.6.1 authorizes per-site direct-append election; no IS spec change"
  - "Independent Opus plan/source GO: docs/orchestration/review-evidence/buford-continuation-01a0e147/pr1616-is-plan-v2-10-review/reviewer-verdict-actual.txt SHA256 6076381f7bb090e453a1cd5ab85af70ca456b5600c2ed577728cb0f78316fb08"
  - "Independent Opus watcher/wording delta GO: docs/orchestration/review-evidence/buford-continuation-01a0e147/pr1616-is-v2-10-clearance-delta/reviewer-verdict-actual.txt SHA256 a2817b4667afaa1aee03186d0acaa217c8aae59e7095ef3cfbd26622a5903550"
  - ".harness/clearance/implementation-plan-information-substrate-v2-9-cleared-2026-08-07.md (predecessor)"
merge_commit: pending
reviewer_chain:
  - "Buford GPT-6-sol/high grounded and authored the v2.10 plan row 15 and U-IS-11 AC #21"
  - "Claude Opus 5.5/high independently gave GO for plan classification, source election, stale-clock witness and final watcher/wording delta"
  - "Buford observed red-to-green roster and stale-clock witnesses, 221 focused passes, Ruff, diff and Pyright checks"
supersedes: implementation-plan-information-substrate-v2-9-cleared-2026-08-07.md
---

# Information Substrate plan v2.10 clearance

This successor classifies the model-tool HITL response F2 direct append as one new ELECT site under the existing IS §7.6.1 rule. Its ledger timestamp means append time, sampled inside the existing writer lock; the CP audit's separately sampled composition timestamp is not treated as the ledger's event time. The v2.9 roster and default-preservation obligations remain intact, and no IS spec or writer API changes.

Clearance is limited to the source-contract plan and reviewed implementation. Full composite, PR CI, merge lenses, main and post-main CI, and installed-runtime acceptance remain open.
