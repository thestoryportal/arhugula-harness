---
artifact: .harness/spec/Spec_HE_Loop_Lanes_v1.md
version: v1.7
cleared_at: 2026-09-02T18:30:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.6-cleared-2026-08-26.md (prior head; v1.7 is a single-clause correction on top of it)"
  - ".harness/spec/Spec_HE_Loop_Lanes_v1.md (v1.7 change-note: X7 — C-HE-13 §5 lane set = every non-terminal reservation, conforming to C-HE-03 §4)"
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-36 execution-correction rev note, item (i) — the plan snippet keyed on state == open)"
  - "tools/arc_disjoint_check.py other_lane_heads + NON_TERMINAL/TERMINAL (same PR: the gate that reads the corrected clause) and tools/test_arc_disjoint_check.py::test_other_lane_heads_are_the_non_terminal_siblings (the witness)"
reviewer_chain:
  - "surfaced by the out-of-family codex reviewer on the U-HE-36 landing PR (r1 P2: a plan-side execution note does not amend the canonical contract) — not silently absorbed; the same PR's remaining codex rounds and its 3-lens merge gate re-review the landed wording"
  - "operator NOT asked at authoring (no-parking, CLAUDE.md §12.4.1: one clause conformed to the state machine C-HE-03 §4 already defines; the literal reading yields a gate that fences nothing); operator may reverse by a v1.8 note"
  - "council NOT convened (proportionality: single-clause execution correction; no committed surface revisited)"
supersedes: ".harness/clearance/spec-he-loop-lanes-v1.6-cleared-2026-08-26.md"
superseded_by: null
---

# Clearance — `Spec_HE_Loop_Lanes` v1.7 (U-HE-36 landing)

C-HE-13 §5 named "the `open` reservations' `branch`" as every other lane's current
head. Under C-HE-03 §4 a lane is `pending` from selection to drain start and `open`
only while landing, so the selection-time gate read literally would compare against no
sibling during any sibling's build. v1.7 conforms the clause: the lane set is every
non-terminal (`pending` or `open`) reservation held by another lane, and a state
outside the C-HE-03 §2 domain makes the check refuse rather than pass.

This is a bundled-absorption at the landing PR per CLAUDE.md §11.4 — this marker is
the ratifying back-flow signal the X-AL-3 guard and the codex context guard
(`DESIGN_IMPL_MIX`) recognize.
