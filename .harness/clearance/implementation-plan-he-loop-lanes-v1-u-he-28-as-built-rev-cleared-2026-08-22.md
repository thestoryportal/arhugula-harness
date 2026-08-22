---
artifact: .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md
version: v1.0 + rev 2026-08-22 (U-HE-28 execution corrections, as-built)
cleared_at: 2026-08-22T00:00:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.4-cleared-2026-08-20.md (the spec head this unit executes; C-HE-06 §1/§4(viii)/§6/§8 contract unchanged — recipe, ship-pr door step, and refresh continuation land as specified)"
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-28 as-built rev note items i-xi: i fresh-path branch base from origin/main; ii refresh composition; iii wrapper $1 + guard retained as permanent probe; iv witness flips discharging U-HE-25 rev (ii); v ship-pr rewrite scope; vi r1 absorptions — stdout purity, ls-remote exit-code contract, unblock lane-id guard; vii r2 absorptions — wait_pr_head_checks pre-merge gate in merge_door.py, next-action draft channel, refresh-branch hygiene; viii r3 absorptions — recorded-resume head re-adoption, draft durability; ix r5 absorptions — atomic record replace, pending-run wait, durable draft warning, followable branch lookup; x r6 absorptions — landing-bound + main-base adoption gate, sidecar symlink containment, representation-verified draft retirement; xi coverage tally)"
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

The out-of-family absorption rounds (items (vi)–(x)) landed: emit-mode stdout purity +
`ls-remote` exit-code contract + the `${HARNESS_LANE_ID:?}` unblock guard; the door's
`wait_pr_head_checks` pre-merge gate (a strict-fence refusal must not burn the §5
re-issue budget) with pending-run-aware judging; recorded-resume head re-adoption
(identity-gated, landing-bound delimiter-safe title + `main` base, atomic
`publish_exclusive`+`os.replace` record swap with symlink containment); and the §12.2
pointer re-derivation via the gitignored `.harness/.next-action-draft` channel with
representation-verified retirement (an item-(ii) pointer-untouched residual named in an
earlier draft of this marker was SUPERSEDED by the draft channel; unrepresented
authoring — a corrected or overridden draft — is never deleted).

C-HE-06's contract surfaces are UNCHANGED: the §6 unblock recipe lands plan-verbatim (no
raw-unlink recipe exists), the §4(viii) continuation is produced exactly as the wrapper's
plan-verbatim invocation names it, and §8's yield/backoff numbers are restated, not
altered. This marker ratifies the plan-rev + implementation bundle as a documented
as-built absorption (CLAUDE.md §11.4), not silent absorption.
