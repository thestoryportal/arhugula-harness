---
artifact: .harness/spec/Spec_HE_Loop_Lanes_v1.md
version: v1.2
cleared_at: 2026-08-19T01:20:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - .harness/clearance/spec-he-loop-lanes-v1.1-cleared-2026-08-18.md (the v1.1 clearance this note amends by ONE retry parameter)
  - .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-02 / U-HE-04 / U-HE-06, the executing units)
  - "tools/review_wrapper_common.py (`PER_ATTEMPT_TIMEOUT_S`, the single implementation site) + tools/test_review_wrapper.py + tools/test_agy_review.py (witnesses)"
merge_commit: pending (pre-merge at filing time; same PR as the S1 code)
reviewer_chain:
  - "first live `just review-with-failover` on the S1 branch: codex REVIEWER_UNAVAILABLE (transient: attempt 2 timed out after 550s) — both attempts killed mid-review, session artifacts without task_complete; gemini failover fired and was itself unavailable (multi-segment marker flake), so the chain could not review its own PR"
  - "author grounding: U-HE-01's ten codex rounds each ran ≈590 s (rollout duration_ms 591514) on a smaller diff; agy_review already bounded one invocation at MAX_AGY_PRINT_TIMEOUT_SECONDS = 1200 s pre-S1"
  - "out-of-family codex round 3+ on the S1 PR runs under X2 (recorded in the PR body)"
  - "council NOT convened (proportionality: one numeric retry parameter; no terminal state, classifier row, or failover rule changed; operator may reverse via v1.3)"
supersedes: spec-he-loop-lanes-v1.1-cleared-2026-08-18.md
superseded_by: null
---

# Clearance — `Spec_HE_Loop_Lanes` v1.2 (execution correction X2; H_E tooling, `C-HE-*` namespace)

v1.2 is v1.1 plus ONE dated change-note (X2) correcting the per-attempt timeout in C-HE-16 §3's retry parameters: v1/v1.1 pinned `per_attempt_timeout: 550 s` (budget arithmetic: two attempts + margin under the 1260 s shared deadline); the codex channel measurably needs longer on a real PR-sized diff, so the figure made the primary channel systematically unavailable and pushed every review onto the failover. The cap is now 1200 s (the bound the gemini channel already applied per invocation), every attempt runs `min(1200, remaining − margin)` on the unchanged 1260 s deadline, and a second attempt therefore exists only after a fast transient failure — the class the retry was specified for. Every other sentence of every contract is byte-identical to v1.1; nothing re-litigates the v1 council pass, D5–D8, or X1.

**What this admits.** Consumers may rely on v1.2 as canonical for `C-HE-*` until a successor marker is filed. The v1 marker remains the record of the full clearance chain; v1.1 records X1; this marker records only X2 and its proportionate review. **Operator may reverse** X2 by a v1.3 change-note; `tools/review_wrapper_common.py::PER_ATTEMPT_TIMEOUT_S` is the single site.
