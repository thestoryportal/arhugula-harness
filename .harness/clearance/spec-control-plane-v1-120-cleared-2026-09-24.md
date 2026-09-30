---
artifact: design-substrate/Spec_Control_Plane_v1_120.md
version: v1.120
cleared_at: 2026-09-24T20:06:06-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - "operator decision 'Yes, inherit matching placements' 2026-09-24: evaluation/production-readiness-arch/profile-contract-decision-1.md (Parent PRE_ACTION placement inheritance decision); LIT arhugula-harness-trial-193 cmt-8d4fa328-59f1-406e-bbe6-a56ecd8f5381"
  - "independent Opus design evidence-parent-preaction-inheritance-design-opus-1/review.txt (sha256 of its SHA256SUMS 8dd2872ac1e05a08210bd1bd6942404957ef425a09eeae2bd57c4660329900d8); blueprint accepted at LIT cmt-64772dd8-97ad-4049-afda-db7692cfe6e9"
  - ".harness/clearance/spec-control-plane-v1-119-cleared-2026-08-13.md (predecessor)"
merge_commit: pending (recorded at the integration PR)
reviewer_chain:
  - independent Opus design (above) — authored the blueprint this delta implements; did not review this delta or its code
  - out-of-family Codex source review of the CP-only slice — PENDING; this marker is not independently final until it returns GO
supersedes: spec-control-plane-v1-119-cleared-2026-08-13.md
---

# Clearance — Spec_Control_Plane v1.120 (parent PRE_ACTION inheritance, CP carrier)

**What v1.120 changes.** C-CP-17 §17.3 gains ancestor-first inheritance of `pre-action`
placements, first-match governing selection and exact-name `tool_filter` semantics (patterns
and empty filters refused at construction). C-CP-25's `execute_workflow` gains one additive
input, `inherited_hitl_placements`. C-CP-26 property 7's captured gate-config hash covers the
inherited prefix, so a changed parent fails a child resume closed. An empty prefix is
byte-identical to pre-v1.120 for every root run.

**Scope, stated.** CP carrier, fold, selection function, validation and hash binding only. No
production caller supplies the prefix and the gate composer does not call the selection
function yet, so no runtime enforcement is claimed; the Runtime slice (runner, dispatch
capture, composer selection, audit witness) is owed and named in v1.120 §0.7. Direct
depth-greater-than-zero child resume stays register row `B-104`'s separate refusal.

**Behavior change disclosed.** A manifest declaring a glob/regex `tool_filter` now fails to
load. **Version-number note:** `B-104` had reserved CP v1.120; this number was assigned on
the v1.119 head at the lead's direction and may need renumbering when both land.
