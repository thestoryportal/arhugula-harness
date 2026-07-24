# Implementation Plan: Control Plane — v2.43 (delta over v2.42)

*v2.43 is the CP plan leg of the `B-70` spec leg (`Spec_Control_Plane_v1_107.md`, Class 2 fork `.harness/class_2_fork_b70_effect_fence_resolution_uniform_fallback.md`, operator-ratified "open the spec-leg now" via `AskUserQuestion` 2026-07-24). ZERO existing unit is amended — the new CP spec v1.107 §1 property constrains a resolver that does not yet exist (deferred to the impl leg, mirroring how v1.106 §1.2 property 4 was deferred rather than assigned to U-CP-64). This delta adds ONE coverage-matrix row recording the deferral, following the IDENTICAL disposition v2.42 §5 already used for property 4 itself. ZERO new units; ZERO new cluster; ZERO DAG topology change; ZERO cross-axis cascade.*

**Status:** Proposed

---

## §0 Change-note (v2.42 → v2.43)

### §0.1 Predecessor

`Implementation_Plan_Control_Plane_v2_42.md` (v2.42 — the B-39 spec leg's plan absorption; U-CP-64 amended).

### §0.2 Revision context

`Spec_Control_Plane_v1_107.md` §1 states a new safety+liveness invariant for the `effect_fence_resolution_for`/`effect_fence_resolutions` mechanism's uniform-fallback behavior (closing `B-70`). No field, method signature, or enum changes — the mechanism's carrier (`ResumeContext.effect_fence_resolution(s)`, built at v2.15-era `Spec_Control_Plane_v1_66.md` §1) is unamended. The resolver that will enforce §1's invariant does not exist yet (the impl leg's scope-discovery + build work); no CURRENT unit owns it, mirroring v2.42 §5's own disposition for the parallel `hitl_responses` property 4 invariant (which was similarly deferred rather than assigned to U-CP-64).

### §0.3 Sections revised

§0 (this change note); §5 (coverage delta, one new row). All other sections — every unit body, all dependency graphs, cross-cutting units, open items — PRESERVED VERBATIM from v2.42.

### §0.4 Scope discipline

Coverage-matrix-only delta. ZERO new atomic units; ZERO new contract IDs; ZERO amended unit bodies; ZERO new within-axis DAG edges; ZERO cross-axis cascade.

---

## §5 — Coverage matrix delta

| Spec contract | Plan unit(s) |
|---|---|
| CP spec v1.107 §1 (multi-branch effect-fence-resolution fallback-safety invariant — closes `B-70`; safety + liveness properties for the uniform `effect_fence_resolution` fallback, no property-5 equivalent per §2's grounding) | **DEFERRED — no unit owned at this spec leg.** The impl leg owns a fresh scope-discovery pass (against the real LINEAR `_execute_workflow_body` §14.22.9 consume site + the ORCHESTRATOR resume site, `workflow_driver.py` ~line 11044 + the two fan-out consume sites, `_execute_parallelization`/`_execute_orchestrator_workers`) to determine which unit(s) carry the resolver's tree-walk enumeration of the unaddressed effect-fence-pause set across arbitrary recursion depth, mirroring how v2.42 §5 deferred the parallel `hitl_responses` property 4/5 invariants rather than assigning them to U-CP-64. The scope-discovery pass MUST ALSO land the LINEAR site's amendment to become map-addressable — calling `effect_fence_resolution_for(effect_fence_resume.idempotency_key)` (reusing the ALREADY-EXISTING `idempotency_key` field on `EffectFenceResumeState`) instead of reading `effect_fence_resolution` directly — per CP spec v1.107 §1.1's round-3 correction (a first draft of both this row and the spec text made a LINEAR pause UNCONDITIONALLY unaddressed regardless of any map entry, which out-of-family review found would permanently livelock any 2+-simultaneous-LINEAR-pause resume; corrected to genuine map-addressability instead, since the carrier already exposes the needed key). This is an explicit gap, not a silent omission (per workspace `CLAUDE.md` §13.1 "no silent caps" discipline). |

DAG topology preserved verbatim from v2.42 — ZERO new edges, ZERO new units, ZERO amended unit bodies.

---

## §6 — Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_43.md` |
| Version | v2.43 |
| Filing event | `B-70` spec leg plan absorption (Class 2 fork, operator-ratified "open the spec-leg now" via `AskUserQuestion` 2026-07-24) — one coverage-matrix row, no unit amendment |
| Predecessor | `Implementation_Plan_Control_Plane_v2_42.md` |
| Operator authority | `AskUserQuestion` 2026-07-24 |
| Co-published artifacts (this arc) | `Spec_Control_Plane_v1_107.md`; clearance marker; workspace `CLAUDE.md` §2.3/§2.4 pointer bump; `.harness/forward-register.yaml` + `.harness/post-phase-8-forward-register.md` B-70 row |
| Unit-count change | None (102 → 102 — coverage-row-only delta) |
| Cluster-count change | None |
| DAG topology change | None |
| Cross-axis cascade | None asserted by this delta |
| Impl leg | NOT bundled — code + tests land as a separate follow-on arc per the B-33/B-39/B-59 precedent |
| Skill discipline | `implementation-planner` Phase-7 revision-pass absorbing upstream CP spec v1.107 into the coverage matrix only; fidelity-pure; NO contract addition beyond the spec; NO unit re-decomposition; NO DAG topology change |
| Date | 2026-07-24 |
