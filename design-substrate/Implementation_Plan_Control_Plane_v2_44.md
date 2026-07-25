# Implementation Plan: Control Plane — v2.44 (delta over v2.43)

*v2.44 is the CP plan leg of the `B-72` (item 1) spec leg (`Spec_Control_Plane_v1_108.md`, Class 1 tension `.harness/class_1_tension_b72_pre_dispatch_gate_owning_branch_identity.md`, operator-ratified "open the CP spec-leg now, co-designed with `B-71`" via `AskUserQuestion` 2026-07-25). ZERO existing unit is amended — the new CP spec v1.108 §1 property (property 6) constrains a resolver that does not yet exist (deferred to the impl leg, mirroring how v2.42 §5 deferred properties 1-4/5 and v2.43 §5 deferred `B-70`'s effect-fence analogue rather than assigning them to U-CP-64). This delta adds ONE coverage-matrix row recording the deferral. ZERO new units; ZERO new cluster; ZERO DAG topology change; ZERO cross-axis cascade.*

**Status:** Proposed

---

## §0 Change-note (v2.43 → v2.44)

### §0.1 Predecessor

`Implementation_Plan_Control_Plane_v2_43.md` (v2.43 — the `B-70` spec leg's plan absorption; coverage-matrix-only delta, zero units amended).

### §0.2 Revision context

`Spec_Control_Plane_v1_108.md` §1 states a new CONTRACT property (property 6) for the `hitl_responses`/`hitl_response_for` mechanism (C-CP-26 §26.8.1): a pre-dispatch gate-owning branch (one whose own HITL gate fired before any child run was dispatched) MUST be counted in property 4's Safety-clause "unaddressed gate-owning set," using an implementation-discretion internal identity, and MUST NEVER be resolvable via the `child_run_id`-keyed `hitl_responses` map. No field, method signature, or enum changes — properties 1-5 (v1.106 §1.2) are unamended; property 6 is purely additive. The resolver that will enforce property 6 does not exist yet (the impl leg's own scope-discovery + build work, same bucket as properties 1-5's already-deferred resolver mechanism per v2.42 §5); no CURRENT unit owns it.

### §0.3 Sections revised

§0 (this change note); §5 (coverage delta, one new row). All other sections — every unit body, all dependency graphs, cross-cutting units, open items — PRESERVED VERBATIM from v2.43.

### §0.4 Scope discipline

Coverage-matrix-only delta. ZERO new atomic units; ZERO new contract IDs; ZERO amended unit bodies; ZERO new within-axis DAG edges; ZERO cross-axis cascade.

---

## §5 — Coverage matrix delta

| Spec contract | Plan unit(s) |
|---|---|
| CP spec v1.108 §1 (pre-dispatch gate-owning branch counting — property 6, closes `B-72` net-position item (1); a gate-owning branch with no child run yet MUST be counted in property 4's unaddressed-set test via an internal-only identity, and MUST NEVER be `hitl_responses`-keyed) | **DEFERRED — no unit owned at this spec leg.** The impl leg owns a fresh scope-discovery pass (against the real fan-out branch dispatch sites, `_execute_parallelization`/`_execute_orchestrator_workers`, plus `_collect_gate_owning_run_ids`/`compute_hitl_uniform_fallback_eligible_run_id`, `workflow_driver.py:2665-2742`, and the `PeerFanOutResumeState`/`FanOutResumeState` branch-pause capture path, `workflow_driver.py` ~9698-9760) to determine (i) which unit(s) carry a new carrier recording a pre-dispatch gate-owning branch's presence, (ii) the internal identity's shape (impl discretion per CP spec v1.108 §1.1(d) — property 1's `run_id`-shaped `hitl_responses` key is explicitly OUT of scope for this identity, per property 6 §1.1(b)), and (iii) the amendment to `_collect_gate_owning_run_ids`'s tree-walk to include this new carrier alongside its existing `paused_child_branches` walk. Mirrors how v2.42 §5 deferred properties 1-4/5's resolver and v2.43 §5 deferred `B-70`'s effect-fence analogue rather than assigning either to U-CP-64. **Explicitly NOT covered by this row** (per CP spec v1.108 §1.2's own scope note, unchanged forward work): `B-72` items (2)/(3)/(4) — keyed multi-peer addressing (gated on `B-71`), property 4's general resolver set-membership mechanism, and `B-72`'s own round-1 hybrid case. This is an explicit gap, not a silent omission (per workspace `CLAUDE.md` §13.1 "no silent caps" discipline). |

DAG topology preserved verbatim from v2.43 — ZERO new edges, ZERO new units, ZERO amended unit bodies.

---

## §6 — Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_44.md` |
| Version | v2.44 |
| Filing event | `B-72` (item 1) spec leg plan absorption (Class 1 tension, operator-ratified "open the CP spec-leg now, co-designed with `B-71`" via `AskUserQuestion` 2026-07-25) — one coverage-matrix row, no unit amendment |
| Predecessor | `Implementation_Plan_Control_Plane_v2_43.md` |
| Operator authority | `AskUserQuestion` 2026-07-25 |
| Co-published artifacts (this arc) | `Spec_Control_Plane_v1_108.md`; clearance marker; workspace `CLAUDE.md` §2.3/§2.4 pointer bump; `.harness/forward-register.yaml` + `.harness/post-phase-8-forward-register.md` `B-72` row |
| Unit-count change | None (102 → 102 — coverage-row-only delta) |
| Cluster-count change | None |
| DAG topology change | None |
| Cross-axis cascade | None asserted by this delta |
| Impl leg | NOT bundled — code + tests land as a separate follow-on arc per the `B-33`/`B-39`/`B-59`/`B-70` precedent |
| Skill discipline | `implementation-planner` Phase-7 revision-pass absorbing upstream CP spec v1.108 into the coverage matrix only; fidelity-pure; NO contract addition beyond the spec; NO unit re-decomposition; NO DAG topology change |
| Date | 2026-07-25 |
