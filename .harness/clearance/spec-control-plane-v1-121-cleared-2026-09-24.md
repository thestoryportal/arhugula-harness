---
artifact: design-substrate/Spec_Control_Plane_v1_121.md
version: v1.121
cleared_at: 2026-09-24T22:22:42-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - "first-release evaluator accept contract decision: evaluation/production-readiness-arch/evaluator-accept-first-release-decision-1.md"
  - "independent Opus design evidence-evaluator-accept-design-opus-1/verdict.md (SHA256SUMS sha256 921718bf7edf87d6b4f10974ac0ccec7d479ff0e7ed0e4f26cc9755b2f43318f)"
  - ".harness/clearance/spec-control-plane-v1-120-cleared-2026-09-24.md (predecessor)"
merge_commit: pending (recorded at the integration PR)
reviewer_chain:
  - independent Opus design (above) — authored the blueprint this delta implements; did not review this delta or its code
  - out-of-family Codex source review of the CP-only slice — PENDING; this marker is not independently final until it returns GO
supersedes: spec-control-plane-v1-120-cleared-2026-09-24.md
---

# Clearance — Spec_Control_Plane v1.121 (evaluator verdict contract, CP slice)

**What v1.121 changes.** The EVALUATOR_OPTIMIZER accept signal becomes a strict typed
`EvaluatorVerdict` (literal bool `accepted`, optional string `feedback`, no extra keys) read at
the live loop, the resume pending-evaluate and resume-prefix coherence. A missing or malformed verdict
ends the run FAILED with `evaluator-optimizer-verdict-malformed` (prior entries drained; never a
retry, PAUSED or fallback); a malformed resume prefix is a resume mismatch. Explicit rejects still
reach the cap and end SUCCESS with `accepted=False`; acceptance is `final_state["accepted"] is True`.

**Scope, stated.** CP type, parser and driver only. The Runtime provider-response reader and binding
are a separate slice; no installed model acceptance is claimed. Raw evaluation output, pause-cursor and
ledger bytes, RunStatus values and the CLI response surface are unchanged.

**Behavior change disclosed.** Absent/non-bool `accepted` and extra keys now FAIL (previously regenerate
or, for `"false"`, a false accept); pre-change EO cursors lacking a valid verdict fail closed on resume.
