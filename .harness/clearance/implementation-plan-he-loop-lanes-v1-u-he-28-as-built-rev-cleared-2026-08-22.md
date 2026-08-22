---
artifact: .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md
version: v1.0 + rev 2026-08-22 (U-HE-28 execution corrections, as-built)
cleared_at: 2026-08-22T00:00:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.4-cleared-2026-08-20.md (the spec head this unit executes; C-HE-06 §1/§4(viii)/§6/§8 contract unchanged — recipe, ship-pr door step, and refresh continuation land as specified)"
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-28 as-built rev note items i-v, dated inline: i fresh-path branch base from origin/main; ii refresh composition + untouched next-action pointer residual; iii wrapper $1 + guard retained as permanent probe; iv witness flips discharging U-HE-25 rev (ii); v ship-pr rewrite scope)"
  - "justfile + .claude/skills/ship-pr/SKILL.md + tools/roadmap_status_refresh.py + tools/hooks/safe-merge.sh + tools/hooks/test_skill_reservation_wiring.sh + tools/hooks/test_permission_guard.sh + tools/test_roadmap_status_refresh.py (same PR)"
reviewer_chain:
  - "recorded at PR close per the out-of-family review + merge-gate rows on this arc's PR"
supersedes: null
superseded_by: null
---

# Clearance — `Implementation_Plan_HE_Loop_Lanes` v1.0 rev 2026-08-22 (U-HE-28 as-built)

The U-HE-28 landing revises only the unit's own execution record: rev note items (i)–(v).
Item (i) corrects the plan-time sketch's fresh-path branch base: `emit_refresh_pr()`
branches from the just-merged `origin/main` tip BEFORE running the mechanical refresh, so
the refresh commit's recorded `git_head` equals its own parent
(`_is_terminating_refresh_commit`) and the refresh PR's diff is roadmap-status-only. Item
(ii) documents the refresh composition (`--emit-refresh-pr-json N` runs the mechanical
refresh in-process with derived defaults; `--notes`/`--next-action`/`--date` compose) and
names the door-path residual: the fixed wrapper string carries no authored pointer, so the
`## Next action` pointer is left untouched by door-driven refreshes — self-healing for
derivation via the pointer's "then <next unit>" tail plus C-HE-03 terminal-head dedup.
Item (iii) records the wrapper's `$1` append (this unit's own body) and the retention of
the U-HE-25 pre-lease availability guard as a permanent probe. Item (iv) discharges the
U-HE-25 rev (ii) witness pin: the real-CLI row now asserts probe-pass + door fail-fast
(rc 4, DoorFailed on the nonexistent witness reservation) with rc 69 / rc 0/3/5 as named
failures. Item (v) bounds the ship-pr rewrite (door section inserted; §12.2 mechanical
half door-ridden; manual recipe retained for the recovery path only).

C-HE-06's contract surfaces are UNCHANGED: the §6 unblock recipe lands plan-verbatim (no
raw-unlink recipe exists), the §4(viii) continuation is produced exactly as the wrapper's
plan-verbatim invocation names it, and §8's yield/backoff numbers are restated, not
altered. This marker ratifies the plan-rev + implementation bundle as a documented
as-built absorption (CLAUDE.md §11.4), not silent absorption.
