---
artifact: .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md
version: v1.0 + rev 2026-09-02 (U-HE-36 execution correction — status-block note items (i)–(v); no other unit changed)
cleared_at: 2026-09-02T18:30:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.7-cleared-2026-09-02.md (the spec head this plan executes; X7 is the contract-side half of item (i))"
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (status block: the U-HE-36 rev note — (i) non-terminal lane set, (ii) merge-tree parse + exit-1-without-OID, (iii) no --merge-base on git 2.39.5 → patch-apply replay under a scratch object dir, (iv) o3-colliding-pairs.txt re-derived, (v) guard allow for the check verb)"
  - "tools/arc_disjoint_check.py + tools/test_arc_disjoint_check.py (same PR: the as-built unit the note describes)"
  - "tools/hooks/permission-guard.sh _disjoint_check_shape + tools/hooks/test_permission_guard.sh (item (v), U-HE-25 precedent)"
---

What changed and why it is a correction, not an extension:

The U-HE-36 plan snippet (§2, Step 2–3) was executed against git 2.39.5 and the
C-HE-03 state machine, and five of its assumptions did not survive contact: the
lane set keyed on `state == "open"` (a lane is `pending` for its whole build); the
`--name-only` parse took every non-blank line after the OID (merge-tree prints
informational messages after the path list) and treated exit 1 as the conflict
verdict (an unresolvable ref also exits 1, with no tree OID); `--merge-base` does
not exist on this git (the replay applies B's patch onto A's tree and parents the
result at A^ under a scratch `GIT_OBJECT_DIRECTORY`, reporting unappliable files as
masked); `.harness/plan/o3-colliding-pairs.txt` did not exist (`derive-pairs`
re-derives it from the P-R3 window and reproduces 150 PRs / 444 window pairs / 172
colliding); and the guard needed an exact-shape allow for the `check` verb so the
gate runs headless. The unit's scope, spec linkage (C-HE-13 §4-5), files, and
dependency edges are unchanged; the rev is recorded as one dated status-block
sentence. Operator may reverse by a dated plan note.
