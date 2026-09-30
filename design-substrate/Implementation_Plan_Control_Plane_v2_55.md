# Implementation Plan: Control Plane — v2.55 (delta over v2.54)

**Status:** Proposed for PR #1616 Class 1 backflow. v2.54 remains the cleared head until this delta is independently reviewed and cleared. This is a retrospective execution map and three source-verification units for CP spec v1.120–v1.124; it cannot make the prior code precede its plan. All v2.54 and earlier unit bodies remain historical and unchanged.

## §0.1 Why a CP plan delta is owed

[HIGH] CP spec v1.120–v1.124 changed production obligations after plan v2.54. The PR #1616 pass-1 spec lens and the independent Class 1 packet review found that the canonical CP plan head has no corresponding execution authority for inherited PRE_ACTION placement, the strict evaluator verdict, or B-104's typed exact-ref carriers/refusals/public hash. The independently reviewed B-104 plans at `/home/robbo/Work/arhugula-trial/evaluation/production-readiness-arch/plans/` are supporting decomposition, not a canonical CP plan head. Source witnesses and clearance must be judged at the final integrated PR head, with installed behavior separate.

## §0.2 U-CP-103 — ancestor PRE_ACTION contract (CP v1.120)

**Owner:** CP C-CP-17 §17.3, C-CP-25, C-CP-26 property 7. **Cluster:** HITL placement fold and workflow driver. **Dependency:** existing placement/fold and gate-config-hash units. **Co-land pin:** Runtime v1.132 consumer of the CP carrier/selector. This is a scheduling pin, not a reverse DAG edge.

Acceptance criteria:

1. Only PRE_ACTION placements inherit; ancestor-first order precedes child declarations and the per-step ADD fold. Tool filters use exact tool names, with no inference match for a nonempty filter. The CP selector returns only the first matching placement for one action. Runtime v2.64 owns the downstream prompt and audit-effect witnesses.
2. Root entry with empty inherited tuple remains byte-identical for placement composition and captured gate-config hash. Descended entry rejects a non-PRE_ACTION inherited element before state change. Every linear/nonlinear driver site and post-join synthesis receives the same inherited tuple.
3. The capture hash binds the ordered inherited prefix; changing/removing/narrowing an ancestor placement refuses resume rather than dropping the parent constraint.
4. The existing nonempty-prefix source witnesses in `harness-cp/cp_tests/test_parent_preaction_inheritance.py` cover linear and PARALLELIZATION paths. No nonempty-prefix source witness exists for the ORCHESTRATOR_WORKERS, EVALUATOR_OPTIMIZER, DECENTRALIZED_HANDOFF, HIERARCHICAL_DELEGATION or post-join synthesis sites. Those five nonempty-prefix witnesses are **open** and must be added and reviewed before U-CP-103 or the paired CP/Runtime plan can be cleared. Runtime v1.132's real descendant and first-match witnesses are checked under Runtime plan v2.64; mock-only pass-through does not close the co-land pin.

## §0.3 U-CP-104 — strict evaluator verdict (CP v1.121)

**Owner:** C-CP-25 §25.11/§25.17. **Cluster:** evaluator-optimizer decision. **Dependency:** existing evaluator driver. **Co-land pin:** Runtime v1.126's Ollama response reader for the first-release provider route; this is not a new DAG edge.

Acceptance criteria:

1. `EvaluatorVerdict.accepted` is a literal boolean; absent, nonboolean or extra-key mappings fail typed. The live loop, pending-evaluate resume, and prefix-coherence check use one parsing authority.
2. A malformed live/pending verdict yields FAILED after prior buffered effects drain; it does not retry an already executed evaluator step, pause resumably, or accept a truthy string. A malformed prefix is a resume mismatch.
3. `harness-cp/cp_tests/test_evaluator_verdict.py` and `test_workflow_driver_evaluator_optimizer.py` exercise all three decision sites and malformed shapes. The Runtime provider-response reader and installed Ollama acceptance stay separate.

## §0.4 U-CP-105 — exact durable-child carriers and refusal vocabulary (CP v1.122–v1.124)

**Owner:** C-CP-25 and C-CP-26 §26.1/§26.6. **Cluster:** pause capture, fan-out carrier, refusal and snapshot-hash authority. **Dependency:** existing durable pause protocol and fan-out driver. **Co-land pin:** Runtime v1.129–v1.130 exact-record and admission consumer, without a reverse CP→Runtime DAG edge.

Acceptance criteria:

1. Root/descended entry and capture carry required nonnegative numeric depth. A durable capture returns an exact `JournalRecordRef` bound to its snapshot; an ephemeral capture carries no ref. Parent PAUSED results and child fan-out carriers retain the exact ref, not a synthetic or latest-only substitute.
2. The public snapshot-hash verifier is the sole CP authority for Runtime parent-carrier verification; the nine `ChildResumeRefusal` spellings and typed terminal handling match v1.123/v1.124. A refusal recorded before the barrier ends is not demoted by `proceed` into PARTIAL; audit-signing failure never replaces the refusal reason.
3. `harness-cp/cp_tests/test_b104_task4a_captured_pause.py`, `test_b104_task4b_child_ref_carry.py`, `test_b104_task4c_child_resume_refusal.py`, `test_b104_child_resume_refusal_values.py`, and `test_pause_snapshot_hash_public.py` are reviewed at final head for the stated behaviors. Runtime's separate record/lease/gateway witnesses are checked under v2.64.
4. This unit does not activate the production stage-5 child-admission binding, root `api.resume` claim wiring, Task 5b worker handoff or installed crash recovery. The first-release B-104 acceptance contract and installed gates remain open.

## §0.5 Boundaries

[HIGH] U-CP-103/104/105 are source-verification units added after the initial source work. Review must identify an absent behavior rather than accept the unit label as proof. Their co-land pins state the consumer relationship and do not mint a CXA edge. No CP spec, contract number, fail class, configuration field, or source API is changed by this plan delta. [SPECULATIVE] Later plan work may be needed for still-unbuilt B-104 production binding; this record grants no waiver for it.
