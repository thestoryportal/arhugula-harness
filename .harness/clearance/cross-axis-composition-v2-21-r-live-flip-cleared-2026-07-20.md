---
artifact: design-substrate/Cross_Axis_Composition_Document_v2_21.md
version: v2.21 (in-place status flip; no new delta version)
clearance_event: prescribed in-place amendment — §2.3.9 row 1 `R-planned` → `R-live`
reviewer_chain: 9 out-of-family codex rounds + merge-gate 3-lens (concurrency / spec-conformance / test-witness, all APPROVE) at PR #1067; the flip itself was flagged as the owed post-merge follow-up by the spec-conformance lens
merge_commit: d0c07ac8 (PR #1067, 2026-07-20)
date: 2026-07-20
---

# CXA v2.21 §2.3.9 `R-planned` → `R-live` flip (B-54 audit-verification seam)

v2.21 §0.4 pre-authorized this exact amendment at registration: *"the impl
arc's landing PR SHOULD flip the tag to `R-live` (a one-cell edit +
clearance)"*. The impl arc landed at **PR #1067** (squash `d0c07ac8`,
2026-07-20): U-CP-44/45/42 (the C-CP-20 §20.3.1 blocking walk over the
CP-owned injected-verifier Protocol + result boundary at
`harness_cp/audit_walk_verification.py`) ⊕ U-RT-138 (the composition-root
`OdVerifierWalkAdapter` at `harness_runtime/lifecycle/audit_walk_adapter.py`
+ the `harness-inspect` §13.5 verification inputs — the first production
injection site).

The seam is now materialized-live end-to-end: `harness-runtime` imports both
packages and injects the real U-OD-55 verifier behind the CP Protocol;
`harness-cp` never imports `harness-od` (package-graph witness
`test_walk_verifier_injected_no_od_import`). Edits in this flip: §0.3
heading, §2.3.9 row-1 Status cell, §0.4 flip note, §0.5 aggregate-clause
tag, + the root `CLAUDE.md` §1.1 pointer. No contract, carrier, or count
change — 110 total relationships unchanged.

This PR also restores a 6-line accepted-residual comment on
`WalkVerificationOutcome.signature_dispositions` (harness-cp) that was
authored in PR #1067's round-8 batch but missed the merge (doc-only).
