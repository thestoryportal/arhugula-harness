---
artifact: design-substrate/Spec_Control_Plane_v1_108.md
version: v1.108
cleared_at: 2026-07-25T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-tension-record
back_reference:
  - .harness/class_1_tension_b72_pre_dispatch_gate_owning_branch_identity.md
  - .harness/class_1_fork_b72_gate_ownership_missing_carrier.md
  - .harness/forward-register.yaml B-72 row
merge_commit: pending (direct-to-main commit at authoring time)
reviewer_chain:
  - operator AskUserQuestion ratification (2026-07-25) — "open the CP spec-leg now, co-designed with B-71" vs. "hold both"
  - systems-architect tension-resolution mode (advisor() unavailable at authoring time; recommendation grounded directly against verbatim CP spec v1.106 §1.2 properties 1/4/5 + verbatim sub_agent_dispatch.py code, not paraphrase)
  - out-of-family codex review (round 1, `just codex-review` base=main) — 2 real [P1] findings, both fixed before merge: (1) the plan delta's coverage-matrix row understated its own scope, naming only the counting/carrier side and omitting the delivery-cell construction required to actually consume the resolved response (fixed at `Implementation_Plan_Control_Plane_v2_44.md` §5); (2) the canonicalization bundle (this clearance marker, the sibling plan clearance marker, CLAUDE.md pointer bumps, register updates) was not yet published when the spec/plan text alone was reviewed (fixed by this marker + the co-landing PR's other files)
supersedes: null
---

# Clearance — `Spec_Control_Plane_v1_108` (B-72 item (1) spec leg)

Closes `B-72`'s net-position item (1) (`.harness/forward-register.yaml`; the round-3 reproduction's SOLE pre-dispatch gate-owning branch case, `.harness/class_1_fork_b72_gate_ownership_missing_carrier.md`). Adds ONE additive property (property 6) to `Spec_Control_Plane_v1_106.md` §1.2's HITL delivery mechanism: a pre-dispatch gate-owning branch (per property 5's own gate-owning test — it dispatched into its own HITL gate, but no child run exists yet) MUST be counted in property 4's Safety-clause "unaddressed gate-owning set" via an implementation-discretion internal identity, and MUST NEVER be resolvable via the `child_run_id`-keyed `hitl_responses` map.

Resolves the fork doc's (a)/(b)/(c) framing: neither widening property 1's `run_id`-shaped key (b) nor a separate delivery path (c) is needed — property 4's Safety clause only needs an internal, non-externally-addressable identity for counting purposes, so property 1 stays untouched and `B-71` is confirmed NOT a co-requisite for this specific fix (round 7's own finding: `B-71` only proposes exposing an already-dispatched child's `run_id`, a narrower, sequential follow-on).

Properties 1-5 (v1.106 §1.2) PRESERVED VERBATIM. NO field, method signature, or enum is added or changed. Property 6 constrains a resolver that does not yet exist — deferred to the impl leg (CP plan v2.44 §5's coverage-matrix row, which explicitly names BOTH the counting/carrier side AND the delivery-cell-construction side after the codex [P1] correction above), mirroring exactly how v1.106 §1.2 properties 1-5 and v1.107 §1 (`B-70`) were both deferred rather than assigned to a then-existing unit.

`B-72`'s net-position items (2) (keyed multi-peer addressing, gated on `B-71`), (3) (property 4's general resolver set-membership mechanism), and (4) (`B-72`'s own round-1 hybrid case) remain open, unchanged by this delta.

Impl leg (code + tests) is a separate follow-on arc per the `B-33`/`B-39`/`B-59`/`B-70` spec-leg-first precedent — not built by this clearance.

## Notes

- Phase 7 consumers may rely on `Spec_Control_Plane_v1_108.md` as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
