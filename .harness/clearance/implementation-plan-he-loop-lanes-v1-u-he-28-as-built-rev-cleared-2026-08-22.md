---
artifact: .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md
version: v1.0 + rev 2026-08-22 (U-HE-28 execution corrections, as-built)
cleared_at: 2026-08-22T00:00:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.4-cleared-2026-08-20.md (the spec head this unit executes; C-HE-06 §1/§4(viii)/§6/§8 contract unchanged — recipe, ship-pr door step, and refresh continuation land as specified)"
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-28 as-built rev note items i-xxvi, in full: i-v plan-draft corrections; vi-x codex r1-r6 absorptions; xi-xxi codex r7-r17 absorptions incl. the r8 refutation-by-design-cite and the r10 fork-PR/origin-binding + r13 FETCH_HEAD-clobber + O_NOFOLLOW P1 fixes; xxii codex r18 incl. the C-HE-06 §6 one-arg unblock restoration; xxiii codex r19 — the r18 baseRefOid pin REVERTED as a wedge, B-193 registered; xxiv codex r20 convergence round, witness-only findings; xxv superseded tally; xxvi 3-lens merge-gate round 1 — 3x BLOCK all absorbed: ephemeral-worktree isolation for the producer (concurrency P1), this marker re-synced + tallies consolidated (spec lens), composed e2e producer witness + containment/revalidation-arm rows (witness lens))"
  - ".harness/forward-register.yaml + .harness/post-phase-8-forward-register.md (B-192 pointer-freshness posture, register-and-held with the merge-gate spec lens as arbiter — that lens GROUNDED and ENDORSED the hold; B-193 BEHIND-refresh recovery design + mid-landing-correction intent chain, register-and-held after the r18/r19 absorb-revert cycle)"
  - "justfile + .claude/skills/ship-pr/SKILL.md + tools/roadmap_status_refresh.py + tools/merge_door.py + tools/hooks/safe-merge.sh + tools/hooks/test_skill_reservation_wiring.sh + tools/hooks/test_permission_guard.sh + tools/test_roadmap_status_refresh.py + tools/test_merge_door.py + .gitignore (same PR)"
reviewer_chain:
  - "recorded at PR close per the out-of-family review + merge-gate rows on this arc's PR"
supersedes: null
superseded_by: null
---

# Clearance — `Implementation_Plan_HE_Loop_Lanes` v1.0 rev 2026-08-22 (U-HE-28 as-built)

The U-HE-28 landing revises the unit's own execution record (rev note items (i)–(xi))
and, as a cross-unit integration absorption justified by this unit's flag making the
path reachable, hardens U-HE-23's `tools/merge_door.py` §4(viii) continuation. The
plan-time-draft corrections: the fresh path branches from the just-merged `origin/main`
tip BEFORE the mechanical refresh (item (i) — both §12.2.1 halves depend on it); the
emit mode composes the refresh in-process with derived defaults (item (ii)); the wrapper
appends `$1` and keeps the U-HE-25 pre-lease guard as a permanent probe (item (iii));
the U-HE-25 rev (ii) witness pin flips to probe-pass + door fail-fast rc 4 (item (iv));
the ship-pr rewrite scope is bounded at item (v).

The out-of-family absorption arc (items (vi)–(xxiv), codex rounds r1–r20, 59 findings:
55 absorbed, 1 refuted by design-cite, 3 register-and-held as B-192/B-193) landed, among
others: emit-mode stdout purity; the door's `wait_pr_head_checks` pre-merge gate with
pending-run-aware judging and full post-wait identity revalidation; recorded-resume head
re-adoption (landing-bound delimiter-safe title + `main` base, atomic record swap,
`_check_door` containment); the §12.2 pointer re-derivation via the gitignored
`.harness/.next-action-draft` channel with representation-verified, label-bound,
rename-claim-atomic retirement and O_NOFOLLOW reads; origin-bound (`isCrossRepository`)
resume identity gates; explicit tracking-ref refspecs; the C-HE-06 §6 one-arg unblock
restoration; and the r18 baseRefOid pin REVERTED at r19 as an unrecoverable wedge
(B-193 carries the converging-recovery design). The 3-lens merge gate (item (xxvi))
then found the one class every codex round missed — the producer mutating the INVOKING
worktree's HEAD — absorbed as ephemeral-detached-worktree isolation with no local branch
ever created; the gate's spec lens re-synced THIS marker and independently endorsed the
B-192 hold; its witness lens closed the producer/door composition gap with a real
subprocess e2e row.

C-HE-06's contract surfaces are UNCHANGED: the §6 unblock recipe lands plan-verbatim (no
raw-unlink recipe exists), the §4(viii) continuation is produced exactly as the wrapper's
plan-verbatim invocation names it, and §8's yield/backoff numbers are restated, not
altered. This marker ratifies the plan-rev + implementation bundle as a documented
as-built absorption (CLAUDE.md §11.4), not silent absorption.
