---
artifact: design-substrate/Implementation_Plan_Operational_Discipline_v2_31.md
version: v2.31
cleared_at: 2026-07-31T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/council-b69-pause-state-accessor-2026-07-30.md (RATIFIED 2026-07-30 — OPTION A′, CO-REQUISITE / SEQUENCED)
  - design-substrate/Spec_Operational_Discipline_v1_36.md (§30.5.2 — the OD plan delta OWED AT THE IMPL LEG under EITHER carrier option)
  - .harness/clearance/spec-operational-discipline-v1-36-cleared-2026-07-30.md
merge_commit: pending (pre-merge at filing time; B-69 impl leg PR)
reviewer_chain:
  - operator ratification (2026-07-30) — OPTION A′
  - out-of-family `just codex-review-uncommitted` to convergence on the landing PR (recorded at the PR body)
---

# Clearance — Implementation_Plan_Operational_Discipline_v2_31 (B-69 arc, impl leg)

v2.30→v2.31: **NEW U-OD-57** — the §C-OD-30.5 pre-bootstrap pause-state audit
carrier, filed at the **impl leg** exactly as OD spec v1.36 §30.5.2 requires
("whichever option the impl leg selects, an OD plan delta is OWED AT THAT LEG").

This is a **bundled-absorption arc** per workspace `CLAUDE.md` §11.4: the PR that
carries it also touches `harness-*/src` and `harness-*/tests`, and its back-flow
lineage is the already-cleared `B-69` spec leg (PR #1165, merge `436ebed5`) plus
this marker. The design-substrate edit is confined to the ONE plan delta the spec
leg itself deferred to this leg by name — no spec text is touched, and no other
plan is amended.

## What was decided at this leg, and what was only recorded

- **DECIDED:** §30.5.2's two carrier options resolve to **(b), a sibling payload
  type**. The grounding is byte-compat cost — option (a) would put a
  never-populated field on every already-shipped `PauseResumeAuditPayload` row and
  would make the union of two DISJOINT field sets optional on both, which is the
  illegal-state-representable shape the closed-schema posture exists to prevent.
- **RECORDED, not decided:** the emission call sites and the pre-bootstrap sink
  stay Runtime-owned at U-RT-148; no OD-side projection helper is owed (there is
  no `(ResumeAttempt, ResumeOutcome)` pair to compose from on a pre-bootstrap
  path); the C-OD-05 §5.1 namespace roster is UNCHANGED.
- **NUMBERED:** `Implementation_Plan_Harness_Runtime_v2_55.md` records U-RT-148's
  dependency on "a PENDING, NOT-YET-NUMBERED OD unit". That unit is **U-OD-57**,
  numbered here and co-landed in the same merge — satisfying the arc's ordering
  constraint by simultaneity.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
