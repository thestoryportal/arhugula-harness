---
artifact: .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md
version: v1.0 + rev 2026-08-21 (U-HE-25 execution corrections, as-built)
cleared_at: 2026-08-21T12:30:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.4-cleared-2026-08-20.md (the spec head this unit executes; C-HE-07 contract unchanged — matcher + deny predicate landed byte-verbatim)"
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-25 as-built rev note items i-v, dated inline: i transition-to-open allowance; ii pre-lease availability guard; iii carrier-doc re-grounding; iv B-188 registration; v witness residual routed to U-HE-26)"
  - "tools/hooks/safe-merge.sh + tools/hooks/permission-guard.sh + tools/hooks/test_permission_guard.sh + tools/lanes_verify.py (same PR #1416)"
reviewer_chain:
  - "out-of-family codex rounds r1-r5 on the U-HE-25 PR: r1-r3 absorbed (transition --to open allowance with token-parse, prefixed-wrapper allowance, direct-exec pin, pseudo-assertion removal, hermetic execution witness); r4/r5 register-and-held (transition-window class -> U-HE-28 owner; free-text deny class -> B-188)"
  - "3-lens merge gate round 1: 3x BLOCK (all lenses converged on the pre-U-HE-28 refresh-flag door-wedge; spec lens added the documentation-trail and carrier-doc findings) -> fix round: pre-lease availability guard (exit 69 before any lease), as-built rev note, carrier docs re-grounded"
  - "3-lens merge gate round 2 at 74da5277: concurrency APPROVE (fail-closed probe trace + empirical rerun), witness-adequacy APPROVE (all mutation probes empirically caught by both hermetic and real-CLI witnesses)"
  - "council NOT convened (proportionality: execution-time corrections of one unit's own sketch; C-HE-07 contract surfaces unchanged; the one contract-adjacent decision — the transition --to open allowance — preserves the U-HE-21 r6 exclusion rationale and is witnessed 8 ways)"
supersedes: null
superseded_by: null
---

# Clearance — `Implementation_Plan_HE_Loop_Lanes` v1.0 rev 2026-08-21 (U-HE-25 as-built)

The U-HE-25 landing revises only the unit's own execution record: rev note items (i)–(v).
Item (i) documents the `transition --to open` allowance (producer: ship-pr's final-gate
pending→open flip, the U-HE-22-landed spec v1.4 X4a carrier) as a TOKEN PARSER preserving
the U-HE-21 r6 exclusion rationale — terminal transitions and `gc` still surface to the
operator. Item (ii) documents the pre-lease availability guard on `safe-merge.sh`: the
plan-verbatim `--refresh-cmd` names `--emit-refresh-pr-json`, which the plan itself defers
to U-HE-28; until the CLI supports it the wrapper aborts exit 69 BEFORE any lease/merge
(the 3-lens gate traced the unguarded form to a deterministic post-merge wedge of the
shared door). Item (iii) re-grounds the two carrier docs (roadmap-continue known-gap →
CLOSED; two-lane guard line cites re-pinned). Item (iv) records the B-188 registration
(spec-verbatim free-text raw-merge deny — spec change-note decision, not an in-unit edit).
Item (v) records the non-exploitable witness residual routed to U-HE-26.

C-HE-07's contract surfaces are UNCHANGED: the `_safe_merge_wrapper` matcher and the raw
`gh pr merge` deny predicate landed byte-verbatim from the cleared spec; the §3 test
inversion and §8.1 manifest row landed as specified. This marker ratifies the
plan-rev + implementation bundle as a documented as-built absorption (CLAUDE.md §11.4),
not silent absorption.
