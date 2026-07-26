# Implementation Plan: Control Plane — v2.45 (delta over v2.44)

*v2.45 is a PROSE-ONLY correction to v2.44 §5's coverage-matrix row (mirrors the spec-side v1.108 → v1.109 sibling correction, same trigger). The row's closing sentence named the `EVALUATOR_OPTIMIZER`/`DECENTRALIZED_HANDOFF` gap "ungrounded by any reproduction" and deferred it to "a future arc" — that arc (the `B-78` impl leg, PR #1117, 2026-07-26) has since landed. Caught by the `merge-gate` skill's spec-conformance lens (out-of-family review, 2026-07-26) as stale-carry-text per workspace `CLAUDE.md` §10.5/§13.1. NO unit amendment, NO new unit, NO DAG/cluster change — the row's substantive scope (the fan-out dispatch-site deferral this row exists to record) is otherwise PRESERVED VERBATIM.*

**Status:** Proposed

---

## §0a Change-note (v2.44 → v2.45)

**Trigger.** The `merge-gate` skill's spec-conformance lens, reviewing PR #1117 (the `B-78` impl leg), found this plan's own §5 coverage-matrix row asserted the `EVALUATOR_OPTIMIZER`/`DECENTRALIZED_HANDOFF` gap was "ungrounded by any reproduction... a future arc's own reproduction-first grounding pass, not silently folded in here" — while the PR under review WAS that future arc, already landed. Sibling correction to `Spec_Control_Plane_v1_109.md`'s change-note for the same underlying spec-side sentence.

**The fix.** §5's row below is corrected to state that the `B-78` impl leg reproduced and closed this gap (PR #1117, 2026-07-26), with no new unit owed — the fix required no CP-spec carrier field (unlike property 6's fan-out fix), so it landed as plain Phase-7 impl work outside this plan's own unit graph, the same way the fan-out delivery-cell wiring this row already covers landed under U-CP-64's scope-discovery pass rather than a new unit. This is a pure prose correction; the row's substantive scope (the fan-out `_execute_parallelization`/`_execute_orchestrator_workers` deferral) is unchanged.

## §0 Change-note (v2.43 → v2.44)

### §0.1 Predecessor

`Implementation_Plan_Control_Plane_v2_43.md` (v2.43 — the `B-70` spec leg's plan absorption; coverage-matrix-only delta, zero units amended).

### §0.2 Revision context

`Spec_Control_Plane_v1_108.md` §1 states a new CONTRACT property (property 6) for the `hitl_responses`/`hitl_response_for` mechanism (C-CP-26 §26.8.1): a pre-dispatch gate-owning branch (one whose own HITL gate fired before any child run was dispatched) MUST be counted in property 4's Safety-clause "unaddressed gate-owning set" AND MUST BE DELIVERED the uniform `hitl_response` when it is sole, using an implementation-discretion internal identity, and MUST NEVER be resolvable via the `child_run_id`-keyed `hitl_responses` map. No method signature or enum changes — properties 1-5 (v1.106 §1.2) are unamended; property 6 is purely additive to the mechanism's REQUIREMENTS, though spec §1.3a DOES authorize one new additive, drop-when-empty/`None` hash-strip-scoped field on the fan-out resume carriers to satisfy it (codex out-of-family review [P2], 2026-07-25, caught before merge — this sentence previously said "No field ... changes," contradicting §1.3a and this plan's own §5). The resolver that will enforce property 6 does not exist yet (the impl leg's own scope-discovery + build work, same bucket as properties 1-5's already-deferred resolver mechanism per v2.42 §5); no CURRENT unit owns it.

### §0.3 Sections revised

§0 (this change note); §5 (coverage delta, one new row). All other sections — every unit body, all dependency graphs, cross-cutting units, open items — PRESERVED VERBATIM from v2.43.

### §0.4 Scope discipline

Coverage-matrix-only delta. ZERO new atomic units; ZERO new contract IDs; ZERO amended unit bodies; ZERO new within-axis DAG edges; ZERO cross-axis cascade.

---

## §5 — Coverage matrix delta

| Spec contract | Plan unit(s) |
|---|---|
| CP spec v1.108 §1 (pre-dispatch gate-owning branch counting — property 6, closes `B-72` net-position item (1); a gate-owning branch with no child run yet MUST be counted in property 4's unaddressed-set test via an internal-only identity, and MUST NEVER be `hitl_responses`-keyed) | **DEFERRED — no unit owned at this spec leg.** Scoped to the `PARALLELIZATION`/`ORCHESTRATOR_WORKERS`/`HIERARCHICAL_DELEGATION` topologies ONLY, per CP spec v1.108 §1.2b (codex out-of-family review, 2 rounds — round 5 [P1]: property 6's text is not topology-agnostic; round 6 [P1]: the round-5 fix itself under-scoped, omitting `HIERARCHICAL_DELEGATION`, which recursively reuses `_execute_orchestrator_workers` per U-CP-88/89 and shares the identical `FanOutResumeState`/`PeerFanOutResumeState` carrier — NOT a separate implementation, so amending `_execute_orchestrator_workers`'s own carrier-construction and delivery-cell sites per this row already covers every `HIERARCHICAL_DELEGATION` recursion level, no separate call site owed). `EVALUATOR_OPTIMIZER`/`DECENTRALIZED_HANDOFF`'s sequential `EvaluatorOptimizerResumeState`/`HandoffResumeState` carriers were, at this row's original v2.44 authoring, explicitly OUT of scope and NOT owed by this row — as of v2.45 (2026-07-26 stale-carry-text correction, see this file's own §0a change-note), that gap has since been reproduced and closed by the `B-78` impl leg (PR #1117), with NO new unit owed here — it required no CP-spec carrier field (unlike this row's own fan-out delivery-cell scope) and landed as plain Phase-7 impl work. The impl leg owns a fresh scope-discovery pass (against the real fan-out branch dispatch sites, `_execute_parallelization`/`_execute_orchestrator_workers` — the latter entered either at the top level or recursively via `_execute_hierarchical_delegation`, `workflow_driver.py:13745-13849` — plus `_collect_gate_owning_run_ids`/`compute_hitl_uniform_fallback_eligible_run_id`, `workflow_driver.py:2665-2742`, and the `PeerFanOutResumeState`/`FanOutResumeState` branch-pause capture path, `workflow_driver.py` ~9698-9760) to determine (i) which unit(s) carry a new carrier recording a pre-dispatch gate-owning branch's presence, (ii) the internal identity's shape (impl discretion per CP spec v1.108 §1.1(d) — property 1's `run_id`-shaped `hitl_responses` key is explicitly OUT of scope for this identity, per property 6 §1.1(b) — but MUST be unique across the WHOLE resume tree per §1.1(d)'s codex-caught amendment, e.g. ancestry-qualified, not merely locally-unique among sibling branches under one fan-out barrier; the impl leg MUST include a collision-witness test asserting two pre-dispatch gate-owning branches at different tree positions produce DISTINCT identities), (iii) the amendment to `_collect_gate_owning_run_ids`'s tree-walk to include this new carrier alongside its existing `paused_child_branches` walk, and **(iv) the actual DELIVERY-CELL CONSTRUCTION at the fan-out dispatch sites** — counting the branch per (i)-(iii) alone does not consume the resolved response; `_execute_parallelization`'s (`workflow_driver.py` ~7851-7866) and `_execute_orchestrator_workers`'s (~11696-11710) `StepExecutionContext` construction currently leave `hitl_delivery_cell`/`hitl_delivery_holder` unset for every fan-out branch — mirroring `workflow_driver.py:4766-4777`'s LINEAR-only `HITLDeliveryCell` construction (per (ii)'s internal identity, when it is the sole unaddressed member per property 6 §1.1(a)/(b)) is a REQUIRED part of this row's scope, not a separate follow-on — without it the composer's Step 0 still finds no delivered value and B-72's round-3 reproduction remains unfixed even after (i)-(iii) land. Out-of-family `just codex-review` [P1] caught this row understating its own scope before merge (2026-07-25) — a first draft of this row named only the counting/carrier side. Mirrors how v2.42 §5 deferred properties 1-4/5's resolver and v2.43 §5 deferred `B-70`'s effect-fence analogue rather than assigning either to U-CP-64. **Explicitly NOT covered by this row** (per CP spec v1.108 §1.2/§1.2b's own scope notes, unchanged forward work): `B-72` items (2)/(3)/(4) — keyed multi-peer addressing (gated on `B-71`), property 4's general resolver set-membership mechanism, and `B-72`'s own round-1 hybrid case. The non-fan-out sequential topologies (`EVALUATOR_OPTIMIZER`/`DECENTRALIZED_HANDOFF`) were a distinct gap per §1.2b at this row's original authoring; per v2.45's correction above, that gap is now closed by the separate `B-78` impl leg (PR #1117), outside this row's own unit scope. This is an explicit gap, not a silent omission (per workspace `CLAUDE.md` §13.1 "no silent caps" discipline). |

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
