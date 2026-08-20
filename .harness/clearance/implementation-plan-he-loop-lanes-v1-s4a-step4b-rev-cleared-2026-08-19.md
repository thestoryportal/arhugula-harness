---
artifact: .harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md
version: v1.0 + rev 2026-08-19 (S4a execution correction, U-HE-15 Step 4b only)
cleared_at: 2026-08-19T20:20:00-06:00
clearance_type: execution-correction-H_E-tooling
back_reference:
  - .harness/clearance/spec-he-loop-lanes-v1.3-cleared-2026-08-19.md (the spec head this plan executes; C-HE-04 §6 is UNCHANGED by this rev)
  - ".harness/plan/Implementation_Plan_HE_Loop_Lanes_v1.md (U-HE-15 Step 4b body + Status block Version row carry the dated rev note)"
  - "tools/hooks/lib.sh + tools/hooks/test_lib.sh (the executing teardown guard + its witnesses, same PR)"
merge_commit: pending (pre-merge at filing time; same PR as the S4a cluster, #1403)
reviewer_chain:
  - "out-of-family codex rounds 1-2 on the S4a PR raised the plan's no-upstream fail-closed clause against the implemented spec-exact scope; the grounding shows the v1.0 clause unimplementable without flipping five existing safe-removal witnesses (test_lib.sh POST_SCAN rc 0 / HELD_CWD rc 7 / OPEN_UNKNOWN rc 9 / POST_IDENTITY rc 10 / signal-recovery) and without refusing every local-only scratch worktree in production"
  - "author grounding: hook_worktree_local_state gates hook_safe_worktree_remove at the pre-move AND quarantine-recheck sites, both BEFORE the paths those witnesses pin; spec C-HE-04 §6's MUST is scoped to `rev-list @{u}..HEAD` non-empty and is implemented exactly"
  - "r2 hardening: an upstream that RESOLVES but whose ahead-count fails is fail-closed residue; r3 added the detached-HEAD refusal (a worktree whose commits would lose their only ref)"
  - "council NOT convened (proportionality: one Step-4b clause of one unit; the spec contract is unchanged; the never-pushed-branch composition is registered as a residual; operator may reverse by re-instating the clause with the five witnesses reworked)"
supersedes: null
superseded_by: null
---

# Clearance — `Implementation_Plan_HE_Loop_Lanes` v1.0 rev 2026-08-19 (S4a, U-HE-15 Step 4b)

The v1.0 Step 4b body prescribed `no-upstream (cannot verify pushed)` as unconditional
teardown-refusal residue. Grounded at S4a execution, that clause contradicts five
pre-existing green safe-removal witnesses and would refuse disposal of every local-only
scratch worktree; spec C-HE-04 §6 (the canonical authority above the plan) scopes the
committed-but-unpushed check to `rev-list @{u}..HEAD` non-empty, which the landed guard
implements exactly, plus two fail-closed hardenings the review rounds added (unresolvable
ahead-count under a resolvable upstream; detached HEAD). The never-pushed-branch
composition (unpushed local branch + a later manual branch delete) is a REGISTERED
residual of U-HE-15 — worktree disposal itself never deletes a branch, and branch-prune
only prunes gh-merged head-refs, so the loss requires two independent failures.

**What this admits.** The plan's U-HE-15 Step 4b body as revised (dated rev note in place,
Status block Version row updated) is the executed contract for the S4a cluster. Operator
may reverse by a further plan rev re-instating the fail-closed clause together with the
five reworked witnesses.
