---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_52.md
version: v2.52
cleared_at: 2026-08-12T12:00:00-07:00
clearance_type: Phase-7-absorbed-via-back-flow-record
back_reference:
  - .harness/b-141-validator-fail-class-cascade-2026-08-12.md
  - .harness/clearance/spec-operational-discipline-v1-41-cleared-2026-08-12.md
  - "register row B-141; B-138 operator-ratified disposition (a), CP spec v1.116"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - "advisor() arc-open pass (2026-08-12)"
  - out-of-family `just codex-review` rounds at this PR (to convergence)
supersedes: implementation-plan-control-plane-v2-51-cleared-2026-08-11.md
---

# Clearance — Implementation Plan Control Plane v2.52 (B-141: U-CP-41 / U-CP-47-era as-domain supersession notes)

**What v2.52 changes.** Two supersession NOTES, zero unit-body edits: U-CP-41
acceptance criterion #5's "C-CP-21 §21.5 5-value set" framing and the U-CP-47-era
`VALIDATOR_FAIL_NAMESPACE_SCHEMA` retry-exit enumeration
(`Implementation_Plan_Control_Plane_v2_4.md:631-638`) are superseded AS DOMAIN by the
`ValidatorFailClass` domain per CP spec v1.116 (B-138 disposition (a)). Landed units
stand as HISTORY per the B-97(a)/B-118 new-unit precedent. Test-roster supersession:
`test_verifier_fail_class_in_cp_21_5_set` →
`test_verifier_fail_class_in_validator_fail_class_domain`.
