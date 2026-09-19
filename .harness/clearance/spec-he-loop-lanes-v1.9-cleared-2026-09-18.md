---
artifact: .harness/spec/Spec_HE_Loop_Lanes_v1.md
version: v1.9
cleared_at: 2026-09-18T00:00:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.8-cleared-2026-09-18.md (prior head; v1.9 layers the one-hour-arc program on top of it)"
  - ".harness/spec/Spec_HE_Loop_Lanes_v1.md (v1.9 change-note: X9a bounded review cycle · X9b non-goals follow · X9c cycle_pass field · X9d shadow trial scores pass-3 terminals · X9e door step (viii) becomes lit done · X9f lit is the state of record · X9g tiebreaker on a stale content branch · X9h ROADMAP_STATUS_DRIFT retires with its artifact)"
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md §9 (the unit program U-HE-52 … U-HE-71, its waves and file locks)"
  - ".harness/audit/arc-wallclock-optimization-2026-09-18.md (the measured audit: mean 177 min, median 126, review rounds 64% of arc hours, 34% of accepted P1/P2 first raised at round 6 or later)"
  - "operator ratified 2026-09-18: all audit recommendations accepted, including lit in place of the plain-file roadmap system and a bounded review cycle, with the late-round-yield cost stated before the decision"
  - "red-team pass against the code before any spec byte moved (independent planner, 9 blockers and 11 should-fix corrections folded into the program)"
  - "council NOT convened (proportionality: the decision is the operator's, taken with its measured cost; the amendment records it rather than weighing an open tension)"
supersedes: ".harness/clearance/spec-he-loop-lanes-v1.8-cleared-2026-09-18.md"
superseded_by: null
---

# Clearance — `Spec_HE_Loop_Lanes` v1.9 (one-hour arcs)

The operator set a goal for this loop: an arc lands in a mean of at most 60 minutes, in
one lane or in parallel lanes, while code, doc and repo quality stay reasonably
balanced. The measured baseline is a mean of 177 minutes over the last 30 reserved arcs.
Review rounds run to convergence account for 64% of that time; the merge door's hold
through a second CI run for the terminating roadmap refresh accounts for another 16%.

v1.9 records the contract half of the operator's decision. Each PR now runs one bounded
review cycle instead of reviewing to convergence, and nothing merges past a known P1.
Forward-work state moves from the plain-file roadmap into `lit`, so the door no longer
opens a refresh PR; it closes the ticket instead. The drift detection that guarded the
refresh retires with the file it checked.

The cost was stated before the decision was taken: in the audited cohort, 34% of
accepted P1/P2 findings were first raised at review round 6 or later. A bounded cycle
will ship some of those, or catch them later as follow-up work. The operator accepted
that trade for the wall-clock goal.

Every amended clause keeps its prior text and carries an inline `v1.9 X9<letter>` marker
naming what now governs, so no reader meets a superseded rule without the pointer. The
units that implement the amendment are listed in the plan's §9, each landing through
the merge door. This marker is the back-flow signal the codex context guard's
`DESIGN_IMPL_MIX` check recognises for the spec and plan edits in this PR.
