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
  - out-of-family codex review, 5 rounds to convergence (`just codex-review` base=main): round 1 — 2 real [P1]s, the plan delta's coverage row understated scope (named only counting/carrier, omitted delivery-cell construction) and the canonicalization bundle was incomplete when reviewed, both fixed; round 2 — [P1] property 6's internal identity permitted local-only uniqueness, colliding under nested fan-out and violating property 4's SOLE-member safety guarantee (fixed — now requires resume-tree-wide uniqueness + a collision-witness test), plus 2 [P2]s (a stale `child_run_id`-based close-out recipe in the register, stale canonical-pointer rows in `claude-artifact-pointers.md`), all fixed; round 3 — [P1] property 6 permitted "counted + never-keyed" without requiring actual delivery to the sole branch, leaving the round-3 repro's livelock unclosed (fixed — §1.1(b) now requires delivery as an explicit contract outcome), plus 2 [P2]s (this tension record's stale Status field, an overbroad `B-71` dependency label on items (3)/(4) in the register), all fixed; round 4 — [P1] the new carrier's EXISTENCE and byte-compat treatment were left to impl discretion despite `PeerFanOutResumeState`/`FanOutResumeState` participating in the persisted `snapshot_hash` (fixed — NEW §1.3a pre-authorizes one additive, drop-when-empty/`None` hash-strip-scoped field, mirroring the `v1.97`/`v1.99` precedent; only the exact field name/type stays impl discretion), plus 1 [P2] (stale `harness-cp/CLAUDE.md` + this marker's own summary, not yet mentioning the delivery requirement or the durable-carrier authorization — fixed by this marker's rewrite); round 5 — 2 real [P1]s, `.harness/roadmap_status.md`'s own Next-action prose still said the spec leg was "not yet started" despite the completed spec/plan delta (fixed — dashboard round-8 update) and property 6's contract text read as topology-agnostic while only `PARALLELIZATION`/`ORCHESTRATOR_WORKERS` are grounded by the round-3 reproduction, leaving `EVALUATOR_OPTIMIZER`/`DECENTRALIZED_HANDOFF`'s sequential `EvaluatorOptimizerResumeState`/`HandoffResumeState` carriers silently uncovered by the plan (fixed — NEW §1.2b explicitly scopes property 6 to the two fan-out topologies and names the sequential-topology gap as a distinct, ungrounded, out-of-scope forward item)
supersedes: null
---

# Clearance — `Spec_Control_Plane_v1_108` (B-72 item (1) spec leg)

Closes `B-72`'s net-position item (1) (`.harness/forward-register.yaml`; the round-3 reproduction's SOLE pre-dispatch gate-owning branch case, `.harness/class_1_fork_b72_gate_ownership_missing_carrier.md`). Adds ONE additive property (property 6) to `Spec_Control_Plane_v1_106.md` §1.2's HITL delivery mechanism: a pre-dispatch gate-owning branch (per property 5's own gate-owning test — it dispatched into its own HITL gate, but no child run exists yet), under the `PARALLELIZATION`/`ORCHESTRATOR_WORKERS` fan-out topologies ONLY (§1.2b, round 5's correction — the only topologies the round-3 reproduction grounds), MUST be counted in property 4's Safety-clause "unaddressed gate-owning set" via a tree-wide-unique implementation-discretion internal identity, MUST NEVER be resolvable via the `child_run_id`-keyed `hitl_responses` map, and MUST be DELIVERED the operator's uniform `hitl_response` when it is the sole unaddressed member (an explicit contract outcome — counting + never-keying alone does not close the livelock, per round 3's correction below). §1.3a additionally pre-authorizes ONE new additive, drop-when-empty/`None` hash-strip-scoped field on `PeerFanOutResumeState`/`FanOutResumeState` to carry this identity, since these types participate in the persisted `snapshot_hash` and a bare "impl discretion" grant would have left the field's existence unauthorized (round 4's correction).

Resolves the fork doc's (a)/(b)/(c) framing: neither widening property 1's `run_id`-shaped key (b) nor a separate delivery path (c) is needed — property 4's Safety clause only needs an internal, non-externally-addressable identity for counting purposes, so property 1 stays untouched and `B-71` is confirmed NOT a co-requisite for this specific fix (round 7's own finding: `B-71` only proposes exposing an already-dispatched child's `run_id`, a narrower, sequential follow-on).

Properties 1-5 (v1.106 §1.2) PRESERVED VERBATIM. NO method signature or enum is added or changed. Property 6 constrains a resolver that does not yet exist — deferred to the impl leg (CP plan v2.44 §5's coverage-matrix row, which explicitly names the counting/carrier side, the tree-wide-uniqueness + collision-witness requirement, AND the delivery-cell-construction side after the codex corrections above), mirroring exactly how v1.106 §1.2 properties 1-5 and v1.107 §1 (`B-70`) were both deferred rather than assigned to a then-existing unit.

`B-72`'s net-position items (2) (keyed multi-peer addressing, gated on `B-71`), (3) (property 4's general resolver set-membership mechanism), and (4) (`B-72`'s own round-1 hybrid case) remain open, unchanged by this delta.

Impl leg (code + tests) is a separate follow-on arc per the `B-33`/`B-39`/`B-59`/`B-70` spec-leg-first precedent — not built by this clearance.

## Notes

- Phase 7 consumers may rely on `Spec_Control_Plane_v1_108.md` as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
