---
artifact: .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md
version: v1.0 + rev 2026-08-20 (S4b execution correction, U-HE-19 fold line only) + store-audit authority-cell companion
cleared_at: 2026-08-20T03:40:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.3-cleared-2026-08-19.md (the spec head this plan executes; C-HE-25's arc-row shape is UNCHANGED by this rev)"
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-19 drain-fold line now routes through rs.fold_round_outcomes; dated rev note inline)"
  - ".harness/spec/store-audit-he-loop-lanes.md (store-2 Authority cell gains the accreted per-round-outcomes fact -- one authority, folded to the arc row at drain)"
  - "tools/reservations.py fold_round_outcomes (the committed projection, mutation-probe PINNED; same PR #1405)"
merge_commit: "pending (pre-merge at filing time; same PR as the U-HE-17 cluster, #1405)"
reviewer_chain:
  - "out-of-family codex rounds 10/13/19 on the U-HE-17 PR raised that the reservation-side composite (round/channel) keys need a committed projection before the U-HE-19 fold can satisfy C-HE-25's numeric {round_n: ...} arc-row shape"
  - "author grounding: round_outcomes is NOT in the C-HE-03 §3 payload enumeration -- the reservation-side carrier shape is plan-level; only the arc-row fold owes the C-HE-25 shape, so the projection is a plan-body wiring fix, not a spec change"
  - "merge-gate spec-conformance lens (gate round 2) reviewed the wired projection + audit cell at PR head and APPROVEd"
  - "council NOT convened (proportionality: one fold expression of one not-yet-landed unit; the spec contract is unchanged; residual composite-key/fold questions are registered to U-HE-19/U-HE-21 in the PR body)"
supersedes: null
superseded_by: null
---

# Clearance — `Implementation_Plan_HE_Loop_Lanes` v1.0 rev 2026-08-20 (S4b, U-HE-19 fold line)

The U-HE-17 landing (PR #1405) revises exactly one plan expression: the U-HE-19 drain-fold
line `row.round_outcomes = res.get("round_outcomes", {})` becomes
`row.round_outcomes = rs.fold_round_outcomes(res.get("round_outcomes", {}))`, projecting the
reservation's composite `"<round>/<channel>"` carrier into the C-HE-25 numeric arc-row shape.
The companion `.harness/spec/store-audit-he-loop-lanes.md` edit records the reservation
store's new accreted fact (per-round outcomes) in its Authority cell — same single-authority
rule, no second authority created (the gate log remains the verdict authority; the
reservation map is the arc's folded summary).

This is a bundled-absorption of review findings (codex rounds 10/13/19) at the landing PR,
per CLAUDE.md §11.4 — this marker is the ratifying back-flow signal the X-AL-3 guard and the
codex context guard (`DESIGN_IMPL_MIX`) recognize.
