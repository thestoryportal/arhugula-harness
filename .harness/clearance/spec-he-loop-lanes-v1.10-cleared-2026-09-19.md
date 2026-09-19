---
artifact: .harness/spec/Spec_HE_Loop_Lanes_v1.md
version: v1.10
cleared_at: 2026-09-19T00:00:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - ".harness/clearance/spec-he-loop-lanes-v1.9-cleared-2026-09-18.md (prior head; v1.10 adds one change-note on top of it)"
  - ".harness/spec/Spec_HE_Loop_Lanes_v1.md (v1.10 change-note X10: C-HE-04 §6 waives the ahead-of-upstream and unresolvable-upstream refusals when the caller proves the worktree HEAD equals the head of its branch's pull request merged into the default branch)"
  - "#1606 (SessionStart reaps merged worktrees autonomously) and its end-to-end run on 2026-09-19, which showed every standard arc worktree refused as ahead-of-upstream after its squash merge"
  - "operator directive 2026-09-19: merged worktrees are removed autonomously at session start or end when it is safe to do so"
  - "operator decision 2026-09-19: amend the spec (chosen over clearing the branch upstream at closeout, and over leaving merged worktrees in place)"
  - "council NOT convened (proportionality: one clause, the operator took the decision with the alternatives and their costs stated)"
supersedes: ".harness/clearance/spec-he-loop-lanes-v1.9-cleared-2026-09-18.md"
superseded_by: null
---

# Clearance — `Spec_HE_Loop_Lanes` v1.10 (merged worktrees are reapable)

The operator directed that merged worktrees be removed autonomously, at session start or
end, whenever that is safe. #1606 made SessionStart launch the existing reaper, and its
end-to-end run exposed a conflict with C-HE-04 §6. That clause refuses teardown while
`git rev-list @{u}..HEAD` is non-empty. An arc branch is created from `origin/main`, so it
tracks `origin/main`, and after a squash merge its own commits are never ancestors of the
merge commit. The check is therefore non-empty forever, and it fails closed once the
remote branch is deleted and `@{u}` stops resolving. No standard arc worktree could ever
be reaped.

v1.10 keeps §6's intent — disposal must never lose a capture silently — and names the one
case where the ahead check proves nothing: the caller has shown that the worktree's HEAD
is the head of its branch's pull request merged into the default branch — a merge into any
other branch proves nothing. That merge put the content on the default branch, and the reaper leaves the branch ref in place, so every commit keeps a reference.
The proof comes from the caller; a teardown without it refuses exactly as before, and the
other refusals (uncommitted changes, a detached HEAD, precious ignored files) are
unchanged.

The operator chose this amendment over two alternatives: clearing the branch upstream at
closeout, which leaves any worktree closed another way stuck, and leaving merged worktrees
in place. The amended clause keeps its prior text and carries an inline `v1.10 X10` marker.
This marker is the back-flow signal the codex context guard's `DESIGN_IMPL_MIX` check
recognises for the spec edit in this PR.
