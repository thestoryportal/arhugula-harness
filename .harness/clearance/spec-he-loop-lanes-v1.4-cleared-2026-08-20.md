---
artifact: .harness/spec/Spec_HE_Loop_Lanes_v1.md
version: v1.4
cleared_at: 2026-08-20T21:30:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.3-cleared-2026-08-19.md (prior head; v1.4 is additive wording-only on top of it)"
  - ".harness/spec/Spec_HE_Loop_Lanes_v1.md (v1.4 change-note: X4a flip-timing, X4b merged-gate carve-out, X4c keep-loudly, X4d interleaving count)"
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-19 rev items vii/ix, U-HE-20 rev item v/viii, U-HE-21 rev items vi-xi, U-HE-22 Scope carrier line -- the registered classes this note discharges)"
  - "tools/merge_door.py + tools/test_merge_door.py (U-HE-22 primitive, same PR: acquire() enforces the section-7 P2 open-holder invariant at acquisition, the timeline the X4a wording now states)"
reviewer_chain:
  - "the four classes were held under register-and-hold across the U-HE-19 (22 rounds), U-HE-20 (7 rounds) and U-HE-21 (7 rounds) out-of-family loops and adjudicated by the 3-lens merge gate on #1409/#1411/#1412 -- every edit conforms spec text to that landed, reviewed behavior"
  - "out-of-family review chain on the U-HE-22 PR covers the bundled v1.4 note + edits"
  - "council NOT convened (proportionality: wording-only reconciliation of internally-contradictory sentences to terminal-reviewed behavior; no committed surface revisited; operator may reverse by v1.5 note)"
supersedes: ".harness/clearance/spec-he-loop-lanes-v1.3-cleared-2026-08-19.md"
superseded_by: null
---

# Clearance — `Spec_HE_Loop_Lanes` v1.4 (S4c, U-HE-22 landing)

The U-HE-22 landing applies the four registered wording classes routed to the merge-door
landing: (X4a) the C-HE-03 §4 `pending→open` flip gains its merge-lane pre-acquire opener
and the C-HE-06 open-ness invariant binds at acquisition across the §4(vi)–(ix)
continuation; (X4b) C-HE-03 §6 + C-HE-04 §2(ii) carry the merged-holder first-capture
carve-out; (X4c) C-HE-04 §5 + Verification (vi) state keep-loudly + converge-at-committed-
point, name the `MERGED_REF` freshness bound and the merged-headless-capture stall; (X4d)
§8.1 "(5 interleavings)" → six. Wording-only; contract numbers, store counts and §6 order
unchanged.

This is a bundled-absorption of register-and-hold classes at the landing PR, per
CLAUDE.md §11.4 — this marker is the ratifying back-flow signal the X-AL-3 guard and the
codex context guard (`DESIGN_IMPL_MIX`) recognize.
