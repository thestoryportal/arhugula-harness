# Implementation Plan: Control Plane — v2.54 (delta over v2.53)

*v2.54 is a plan-follows-spec correction. It re-pins the DIRECTION of the U-CP-27
sub-agent gate-level invariant to the ratified CP spec: `child_gate_level >=
parent_gate_level` by escalation rank (a child may be as restrictive or more
restrictive than its parent; a less restrictive child is structurally rejected).
No new unit, cluster, DAG node, dependency edge or CXA row is introduced; NO landed unit
body is rewritten (the v2.52 supersession-note precedent — the landed text stands as
HISTORY and this note is the operative authority). Every unit body, signature block,
rollback boundary and all other plan content are PRESERVED VERBATIM. No CP spec delta is
made or needed.*

**Status:** Proposed

## §0 Change-note (v2.53 → v2.54)

### §0.1 The inversion this delta corrects

The CP spec is already correct and is NOT amended here:

- `Spec_Control_Plane_v1_2.md` C-CP-12 §12.2 defines the child gate as
  `max(parent_gate_level, …)` — monotonic ascending in restrictiveness.
- C-CP-12 §12.3 states "Sub-agent gate-level ≥ parent gate-level" and that downgrades are
  structurally rejected.
- ADR-D4 v1.1 §1.5 carries the same direction.

The plan text that reverses it is U-CP-27 in `Implementation_Plan_Control_Plane_v2_1.md`
(preserved verbatim through v2.9 and every later delta):

- acceptance #1 (`Implementation_Plan_Control_Plane_v2_1.md:1430`): "`child_gate_level ≤
  parent_gate_level` per §12.2 monotonic-descent invariant; ascent prohibited";
- the `SubAgentGateLevelDescent.child_gate_level` record comment
  (`Implementation_Plan_Control_Plane_v2_1.md:1408`): "monotonic descent constraint".

The as-built code and three test files implemented that reversed text: the assertion
accepted `AUTO` under `DENY` and rejected `DENY` under `AUTO`.

### §0.2 The supersession notes (landed unit NOT rewritten)

**NOTE on U-CP-27 acceptance #1 (direction supersession, v2.54).** The operative
criterion is: `child_gate_level >= parent_gate_level` by the canonical gate escalation
rank (`AUTO < ASK < DENY`, `harness_cp.gate_level_rule`) per C-CP-12 §12.2 (`max`) and
§12.3; a child less restrictive than its parent is rejected (`ValueError` naming §12.3,
the less-restrictive child and the parent). Equality — the `dispatch_sub_agent` default —
and a stricter child are admitted. The v2.1 wording "≤ … ascent prohibited" is superseded
AS DIRECTION.

**NOTE on the `SubAgentGateLevelDescent.child_gate_level` comment (v2.54).** The comment
"monotonic descent constraint" reads as: *floor ≥ parent* (the child's gate never
relaxes). "Monotonic descent" remains the spec's own term for privilege descending down
the delegation tree; it does not mean the gate rank descends.

**NOTE on the roster test (v2.54).** `test_child_gate_level_monotonic_descent` is
re-specified: the dispatch default (`child == parent`) satisfies the invariant, and the
nine parent/child `AUTO`/`ASK`/`DENY` cells are covered by
`test_assert_monotonic_descent_matrix` (CP) and `test_assert_descent_matrix` (Runtime
`RuntimeHandoffRegistry.assert_descent`). `assert_monotonic_descent`'s function name and
`dispatch_sub_agent`'s output are unchanged.

### §0.3 What this delta is NOT

- Not a spec change: C-CP-12 / ADR-D4 are unchanged; CP spec version numbering is
  untouched.
- Not a policy-enforcement claim: no production caller currently invokes
  `assert_monotonic_descent` / `assert_descent`, so this corrects the contract and its
  tests only. A real dispatch-time `policy_override` call site is separate follow-up work.
- Not a unit re-open: no new fields, no signature changes. The code/test correction lands
  in the same branch as this delta and its clearance marker
  (`.harness/clearance/implementation-plan-control-plane-v2-54-cleared-2026-09-24.md`).

Authority record: independent Opus source/contract verdict (LIT
`arhugula-harness-trial-193` `cmt-810b3267-b29c-4f0d-b00a-63db3b6698ce`).

---

*End of v2.54 delta. The v2.53 body and all prior deltas stand unchanged beneath this
file per the delta-only convention.*
