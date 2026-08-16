---
artifact: design-substrate/Implementation_Plan_Operational_Discipline_v2_36.md
version: v2.36
cleared_at: 2026-08-16T12:00:00-07:00
clearance_type: Phase-7-absorbed-via-operator-ratification
back_reference:
  - .harness/b137-c1-admit-the-envelope-root-2026-08-16.md
  - .harness/clearance/spec-operational-discipline-v1-42-cleared-2026-08-16.md
  - "register row B-137 step (3); the OD-plan sibling is owed by the v2.32 / U-OD-58 precedent for the row-19 amendment of the same table"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - "operator AskUserQuestion ratification 2026-08-16 (B-137 step (3) = C1)"
  - "out-of-family just codex-review rounds at this PR (to convergence)"
supersedes: implementation-plan-operational-discipline-v2-35-cleared-2026-08-12.md
---

# Clearance — Implementation Plan Operational Discipline v2.36 (B-137 C1: U-OD-61, §9.2 row 20)

**What v2.36 changes.** ONE NEW atomic unit, zero existing unit-body edits: **U-OD-61**
carries the C-OD-09 §9.2 **row 20** (`workflow.envelope`) membership plus the count-contract
reconciliation that `Spec_Operational_Discipline_v1_42.md` §0.2 lands. It is the plan-side
carrier for candidate **C1** of `B-137` step (3), operator-ratified 2026-08-16.

**Why a plan unit is owed at all.** The v2.32 precedent: when v1.37 added the *nineteenth*
row to this same table, the plan absorbed it as `U-OD-58` rather than letting a spec row land
with no execution-authority carrier and no acceptance criteria. Row 20 is the identical
amendment shape, so it gets the identical treatment. Without it the arc would leave a spec
amendment whose shipped implementation has no plan-side home — the asymmetry the §1.3
authority chain exists to prevent.

**Six acceptance criteria**, each traceable to a defect this workspace has actually hit:
byte-exact twenty-member set in *both* directions; every live count claim moved in the same
commit across five carriers, with point-in-time carrier landscapes explicitly NOT amended
(the v1.37 precedent); row 20 resolving through the LITERAL arm and not the prefix arm, both
directions asserted; the floor reaching in-envelope member spans end-to-end at the real
`api.run` venue **with** a pre-v1.42 counterfactual arm, since an as-built assertion that
never runs the negative arm cannot distinguish a working repair from a vacuous test; the
ordinary-child measurement the `B-137` ratification explicitly owed before shipping to a
production-bounded cell; and a mutation probe, because a membership change no test detects is
not landed.

**Scope discipline.** ADDITIVE. `U-OD-61` is the next free OD unit ID after `U-OD-60`
(verified at authoring against `design-substrate/` and `.harness/`). ZERO existing unit
amended; ZERO new contract number (C-OD-09 already exists and v1.42 amends its own table);
ZERO signature change to any landed unit; ZERO CXA rows.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- **Does not carry** the C11 exported-volume pricing against C-OD-11 §11.1 (`B-182` /
  `B-183`), candidate **A** (its defining tail half is unbuilt and therefore unmeasurable), or
  a repair for **`B-186`** — C1's floor holds only while `workflow.envelope` is the trace
  root, and an unsampled ambient OTel parent defeats it. That bound is stated at v1.42 §0.3.1,
  witnessed, and registered rather than absorbed, because the fix is an emission-site change
  trading the observability floor against distributed-trace continuity.
- See `.harness/clearance/README.md` for marker discipline.
