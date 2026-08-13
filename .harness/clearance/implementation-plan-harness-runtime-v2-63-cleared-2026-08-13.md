---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_63.md
version: v2.63
cleared_at: 2026-08-13T16:00:00-07:00
clearance_type: Phase-7-absorbed-via-back-flow-record
back_reference:
  - .harness/clearance/spec-harness-runtime-v1-121-cleared-2026-08-13.md
  - .harness/clearance/spec-control-plane-v1-119-cleared-2026-08-13.md
  - "register row B-71; council CONVENED + CLOSED 2026-08-12; leg shape recorded on main at PR #1326"
co_requisite:
  - .harness/clearance/implementation-plan-control-plane-v2-53-cleared-2026-08-13.md
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - out-of-family `just codex-review` at this leg's PR (to convergence)
supersedes: implementation-plan-harness-runtime-v2-62-cleared-2026-08-12.md
---

# Clearance — Implementation_Plan_Harness_Runtime v2.63 (B-71 Runtime-side execution authority)

**What v2.63 adds.** ONE new unit, **U-RT-155**, owning the two Runtime sites Runtime spec
v1.121 names: the §14.8.8.1 step-1 escalation-brief minter and the step-2
`compose_hitl_action_id` fold. Seven acceptance criteria and three mutation-probe
obligations.

**The defect witness is a criterion, not a side effect.** Criterion 5 requires that two
peer branches sharing a `child_workflow_id` produce DISTINCT keys and that both HITL audit
entries survive the C-IS-07 §7.5 key-only dedup. That is the criterion by which `B-71`
closes — anything weaker witnesses the carriers rather than the fix, which is the failure
mode this row's three earlier attempts each hit in a different form.

**Signature shape is deliberately unasserted.** No criterion constrains how the token
reaches `compose_hitl_action_id`. That restraint is the Runtime spec's own §14.8.8.10
CONTRACT-not-mechanism precedent (set at v1.106 after a draft prescribed a call shape that
grounding falsified against the real call graph), and it is the discipline `B-71`'s earlier
attempts violated by prescribing wiring they had not executed.

**Scope is auditable by construction.** §0.3 names the two live `compose_hitl_action_id`
mentions that are NOT call sites (the §14.8.2 step 4h substep 8b-HITL cite and the §14.8.8
helper construction-shape note), so the call-site count can be checked rather than assumed:
THREE sites are touched (step 1, step 2, the step-3 payload adapter) and these two are not
among them.

**The CP relationship is ONE DAG edge plus a CO-LAND PIN.** U-CP-102 declares the carriers;
U-RT-155 writes, folds and projects. A first draft declared the dependency in both
directions — a two-node cycle with no valid topological level; out-of-family review caught
it. The edge is U-RT-155 → U-CP-102, one way; the mutual need is a co-land pin outside the
topological sort. Neither is independently observable, so they land in one arc — recorded in
both plan deltas so the fact survives whichever a future session reads first.

**Not a design extension (X-AL-3).** ZERO contract number, fail class, configuration field,
`HarnessContext` field, CXA row or cross-axis edge minted; no landed unit body amended; no
prescription of the composer signature; none of the CP spec §0.9 follow-ons in scope.

**Posture.** Design-phase (`design-substrate/**` + this `.harness/` clearance companion),
per workspace `CLAUDE.md` §11.2. This delta assigns the work; the code lands at the impl
leg, which is not in this arc.
