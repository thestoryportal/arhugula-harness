---
artifact: design-substrate/Spec_Control_Plane_v1_116.md
version: v1.116
cleared_at: 2026-08-09T00:00:00-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/forward-register.yaml row B-138
merge_commit: pending
reviewer_chain:
  - operator ratification of disposition (a), 2026-08-09 (AskUserQuestion)
  - Sonnet grounding pass (all cites re-read by content at HEAD)
  - out-of-family codex review
supersedes: spec-control-plane-v1-115-cleared-2026-08-03.md
---

# Clearance — `Spec Control Plane v1.116`

v1.116 applies the operator-ratified B-138 disposition (a): the live span attribute
`validator.fail.class` carries the C-CP-25→C-CP-28 §25.2 `ValidatorFailClass` domain
(`schema_violation … external_rejection`), and C-CP-21 §21.1/§21.5's contrary gloss — which
bound the wire name to the five retry-exit routing values — is corrected. The retry-exit
taxonomy (`ValidatorRetryExitClass`) is demoted from the wire name, never deleted: it remains
canonical for §21's routing/staircase semantics, which are preserved byte-for-byte in substance.

The grounding that decided it: both live producers (`validator_framework.py:347`,
`validator_escalation_composer.py:152`) write `ValidatorFailClass` values; OD's C-OD-29.1
ingestion schema declares exactly the C-CP-28 §25.5 four-attribute shape; no reader asserts a
retry-exit value on the attribute; no projection function exists. The register row's own
falsifier (a cleared surface declaring the C-CP-25 domain) fired at C-CP-28 §25.2/§25.5.

The CP-3/OD-4 attribute-set divergence is dispositioned in the same pass as two contracts
declaring disjoint-except-`class` subsets of one namespace: §21.5's declared count stays THREE,
so the export-manifest / namespace-map count gates pinned to it are untouched.
`validator.fail.permanence`'s derivation base is re-declared from the validator OUTCOME
(`permanent` iff `PERMANENT_FAIL`), unblocking B-124's build; its emission stays build-owed
there. ZERO contract numbers, ZERO code/plan/Runtime/OD/CXA edits, ZERO hash impact.

`B-138` closes at this leg. Code-side Class 3 residual (the stale `"NEW at C-CP-25"` docstring
at `validator_framework_types.py:71`) rides the next arc touching that file.
