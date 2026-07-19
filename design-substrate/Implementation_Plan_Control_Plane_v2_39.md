# Implementation Plan: Control Plane — v2.39 (delta over v2.38)

*v2.39 is the CP plan leg of the RATIFIED **B-48 sync sub-agent dispatch offload arc** (`.harness/class_2_fork_b48_sync_subagent_dispatch_offload.md`, **RATIFIED 2026-07-18 — the operator selected OPTION B AS RECOMMENDED with all filing-settled riders**; the C1 ⊥ C9 apply-leg dyad `.harness/council-dyad-b48-apply-2026-07-18.md` returned **16/16 CONFIRM, ZERO deviations**, its TWO apply-notes incorporated), absorbing **CP spec v1.102** (`Spec_Control_Plane_v1_102.md`, filed 2026-07-19 — the three CP-owned rider sections: §1 fan-out capacity gating; §2 `HIERARCHICAL_DELEGATION` depth-phrase retirement + formal delegation; §3 B-39 interim sequencing constraint). The three spec surfaces + the change-note's CP-owned witness classes (a)–(g) are homed at FIVE EXISTING units — **U-CP-86 + U-CP-88** (the two fan-out strategies whose `_run_fanout_to_completion` `_proceed_fanout` sites are admission-GATED), **U-CP-85** (admission-rejection = branch failure under §25.15 + the nested cascade-deadline cancel), **U-CP-89** (the depth-phrase retirement + formal delegation), and **U-CP-82** (the drain-timestamp call-site change + strict-xfail removal, co-owned with the same-arc IS plan v2.7) — **ZERO new atomic units** (every surface is an amendment of a unit already covering the parent contract section; no unit-less impl scope remains). Unit count unchanged (101). The executor contract, cap field, frame accounting, typed capacity error, and cancellation/fence/pause carriers are Runtime-owned, DEFINED at Runtime spec v1.102 §14.8.10 and decomposed at the same-arc Runtime plan v2.50 (U-RT-140..U-RT-144) — CROSS-REFERENCED, never restated. All sections except the §0 change note and the five unit amendments + coverage delta below are PRESERVED VERBATIM from v2.38 (delta-only-plan-chain convention).* BROADENED (codex round-6): ALL siblings — gated and ungated — sequence around a resumed paused-HITL target (dispatch()'s unconditional consume_and_clear can lose the one-shot response to any sibling).

**Status:** Proposed

---

## §0 Change-note (v2.38 → v2.39)

### §0.1 Predecessor

`Implementation_Plan_Control_Plane_v2_38.md` (v2.38 — the B-51/B-52/B-54 CP leg; U-CP-42/44/45/72/73 amended).

### §0.2 Revision context — CP spec v1.102 absorption

Per the fork's §5 rider (f) (the CP spec/plan rider: "bringing `_run_fanout_to_completion`'s branch-plan execution under the capacity authority changes CP-owned concurrency/cardinality semantics (C-CP-25 §25.11) … that half rides an explicit CP amendment, never Runtime authority alone; the same rider resolves the UNMATERIALIZED §25.11 delegation depth bound … FORMALLY DELEGATE recursion capacity to the executor cap"). **Empirically verified home units (this apply pass):** the four `_run_fanout_to_completion` construction sites live in `_execute_parallelization` (`harness-cp/src/harness_cp/workflow_driver.py:7974` proceed / `:8336` cancel) and `_execute_orchestrator_workers` (`:11238` proceed / `:11589` cancel) — the driver functions owned by U-CP-86 (`PARALLELIZATION`) and U-CP-88 (`ORCHESTRATOR_WORKERS`) respectively (v2.37 re-tabled bodies). §25.15 `cascade_policy` consumption is U-CP-85; the `HIERARCHICAL_DELEGATION` row is U-CP-89; the buffered/branch-drain path (§25.12) is U-CP-82. No CP surface of this arc lacks an owning unit → ZERO new units.

### §0.3 Sections revised

§0 (this change note); §1–§5 (the five unit amendments); §6 (coverage delta). All other sections — U-CP-01..U-CP-100 bodies except the five amended below, all dependency graphs, cross-cutting units, open items — PRESERVED VERBATIM from v2.38.

### §0.4 Scope discipline

ADDITIVE / amended-unit scope only. ZERO new atomic units; ZERO new contract IDs; ZERO new within-axis DAG edges (amendments only). NEW cross-axis CONSUMPTION edges declared CP-side (atomic, unit-to-unit): U-CP-86 → U-RT-141, U-CP-88 → U-RT-141, U-CP-85 → U-RT-141 (the Runtime plan v2.50 executor unit whose capacity authority these amendments consume — Runtime v1.102 §14.8.10.1 cross-referenced). The CP witness classes of the CP v1.102 change-note ((a)–(g), each mutation-probed per Workflow v1.18 PD-8) are transcribed as `Tests:` criteria at their home units: (a) + (c) + (e) → U-CP-86/U-CP-88; (b) + (f) → U-CP-85; (g) → U-CP-82. The typed capacity error's step-attributability (the dyad's C1 condition) is a doc-level criterion at U-CP-89 (its definition site is Runtime-owned, U-RT-140). Co-land pins (recorded, not DAG edges — one B-48 impl arc): U-CP-86/U-CP-88 ⊕ U-RT-141; U-CP-85/U-CP-86 ⊕ U-RT-144; U-CP-82 ⊕ IS plan v2.7 U-IS-11.

---

**Cross-package capacity-authority carrier (codex round-1 on the apply PR — the cycle-safe seam, mirroring the Arc A verifier-seam precedent):** `harness-cp` has NO `harness-runtime` dependency and must not gain one — the amended U-CP-85/86/88 therefore consume the executor cap through a CP-DECLARED capacity-authority Protocol — a RAISE-CAPABLE frame-unit admission surface (codex round-4: a bool-shaped probe cannot carry attribution): atomic `reserve(frames, *, step_id, descent_chain)`-shaped acquisition that RAISES the SHARED typed capacity-exhausted error carrying the overflowing dispatch step + descent chain — HOMED IN `harness-core` (codex round-5 reconciliation of the round-4 CP-owned phrasing: one type, one home, per the workspace carrier-home discipline; both `harness-cp` and `harness-runtime` import `harness-core`, so no package-boundary mapping and no dual ownership; the Runtime §14.8.10.5 taxonomy row maps to the same core type), plus paired release; exact names implementation-discretion, non-binding — injected into the fan-out execution path via the existing DriverContext/runtime-services injection pattern (the §14.9.3-style composition-root threading). U-RT-141 SUPPLIES the adapter over the real executor at the `harness-runtime` composition root and INTEGRATION-TESTS the real authority through the CP fan-out (co-land pin). Package-graph witness: `harness-cp` contains no `harness_runtime` import (mutation probe: adding one fails). Absent-injected-authority behavior (codex round-4 — NEVER ungated, the cap is mandatory on every fan-out path): CP ships a CP-OWNED DEFAULT bounded authority (a process-local frame budget, default 256 — a CP module constant, construction-overridable) that gates identically when nothing is injected (pure-CP tests/embedding); the runtime adapter REPLACES it at the composition root, making the RuntimeConfig cap authoritative when composed — one authority per process, the default is a fallback instance not a second live authority; witness `test_non_composed_fanout_still_capped` (a pure-CP fan-out past the default budget fail-fasts typed — mutation probe: restoring the ungated fallback passes unbounded fan-out and fails). CXA disposition, grounded: `harness-runtime` is the composition layer, not a 4×4-matrix axis — runtime-service injection through a CP-declared protocol is the committed §14.9.3 pattern (trust-evaluator precedent), NOT a new inter-axis edge; no CXA delta owed.

## §1 U-CP-86 amendment — `PARALLELIZATION` fan-out under the single capacity authority (CP v1.102 §1 + §3)

The v2.37 U-CP-86 body is PRESERVED VERBATIM; v2.39 adds:

**Implements (addition):** + C-CP-25 §25.11 (AMENDED at CP v1.102 §1 — fan-out capacity gating) + the CP v1.102 §3 interim constraint. Consumes the Runtime §14.8.10.1 executor capacity authority (Runtime plan v2.50 U-RT-141 — cross-axis).

**Depends on (addition):** + [U-RT-141 (cross-axis: Runtime — the shared frame budget + admission the gated proceed site consumes; co-land)].

**Acceptance criteria (v2.39 additions):**

- **(§1 rows 1–2, 4.)** The strategy's `_proceed_fanout` construction site (`workflow_driver.py:7974`) is admission-GATED under the ONE shared frame budget: a fan-out of N branches with S sync sub-agent branches runs FULLY CONCURRENT when **occupied + N + S ≤ cap** (the budget is SHARED — ancestors and concurrent workflows holding frames count; admission against AVAILABLE capacity, never the local fan-out alone); beyond capacity the NEXT branch FAIL-FASTS with the typed step-attributable capacity error — NEVER queues. The upstream fan-out thread creation itself is gated (an unbounded manifest MUST NOT spawn N upstream CP threads before the excess fail-fasts). Frame charging per the Runtime accounting model — bound, not restated.
- **(§1 row 3.)** Per-branch reservation is ATOMIC (all-frames-or-fail-fast).
- **(§1 row 6 — apply-note 1.)** The strategy's `_cancel_fanout` construction site (`:8336`) is RECOVERY machinery and admission-EXEMPT — admission that can reject recovery converts a capacity breach into a stranded parent.
- **(§1 row 7.)** The v1.97 (`B-21`) `PeerFanOutResumeState.paused_child_branches` resume semantics are PRESERVED VERBATIM: admission gating changes WHETHER a branch starts, never how a paused one resumes.
- **(§3 — the B-39 interim constraint.)** Until `B-39` resolves, concurrent sibling branches carrying durable-HITL gates are SEQUENCED (the driver MUST NOT run two durable-HITL-gated siblings genuinely concurrently); siblings without durable-HITL gates run fully concurrent per the admission rule. This is a DOCUMENTED interim constraint with the CP v1.102 §3 removal condition — B-48 does NOT absorb B-39's CP design (the branch-unique one-shot response routing stays B-39-gated).

**Tests (v2.39 additions — mutation-probed per PD-8):**

> **Witness (a) — fan-out admission (2-branch fan-out per the filing):** `test_fanout_at_boundary_occupied_plus_n_plus_s_equals_cap_fully_concurrent` + `test_fanout_past_boundary_next_branch_fail_fasts_typed_step_attributable` + `test_fanout_admission_under_contention_second_workflow_holding_frames_counted` (mutation probe: computing admission against the local fan-out alone passes the contention case wrongly and fails). **Witness (c) — cancel-path exemption:** `test_cancel_fanout_recovery_at_full_capacity_never_admission_rejected`. **Witness (d) — sibling pause/resume isolation (CP half; Runtime carriers at U-RT-144):** `test_only_raising_branch_recorded_paused_no_false_sibling_pause` + `test_concurrent_resume_response_not_consumed_by_wrong_sibling` + the v1.97 `paused_child_branches` resume-preservation control. **Witness (e) — interim sequencing:** `test_durable_hitl_gated_siblings_sequenced_while_b39_open` (mutation probe: running gated siblings concurrently fails; ungated siblings remain concurrent as control).

---

## §2 U-CP-88 amendment — `ORCHESTRATOR_WORKERS` fan-out under the single capacity authority (CP v1.102 §1 + §3)

The v2.37 U-CP-88 body is PRESERVED VERBATIM; v2.39 adds:

**Implements (addition):** + C-CP-25 §25.11 (AMENDED at CP v1.102 §1) + the CP v1.102 §3 interim constraint. Consumes the Runtime §14.8.10.1 executor capacity authority (Runtime plan v2.50 U-RT-141 — cross-axis).

**Depends on (addition):** + [U-RT-141 (cross-axis: Runtime; co-land)].

**Acceptance criteria (v2.39 additions):** the SAME five criteria as the §1 U-CP-86 amendment, applied at this strategy's construction sites — `_proceed_fanout` at `workflow_driver.py:11238` admission-GATED; `_cancel_fanout` at `:11589` admission-EXEMPT; occupied + N + S ≤ cap with shared-budget/contention semantics; atomic reservation; typed fail-fast never-queue; v1.97 resume semantics preserved; durable-HITL-gated sibling workers SEQUENCED until B-39. (Criteria bound per-site, not duplicated in prose — the contract text is CP v1.102 §1/§3; the sibling U-CP-86 amendment names the rows.)

**Tests (v2.39 additions — mutation-probed per PD-8):** the witness-(a)/(c)/(e) classes above parametrized over this strategy's sites (the shared fan-out machinery makes one parametrized suite over both strategies acceptable — the acceptance requirement is that BOTH strategies' proceed sites are exercised gated and BOTH cancel sites exempt; a suite covering only one strategy's sites is an acceptance FAILURE).

---

## §3 U-CP-85 amendment — admission-rejection as a branch failure under `cascade_policy` + nested cascade-deadline cancel (CP v1.102 §1 rows 4–5)

The v2.37 U-CP-85 body (the 8 §25.15.2 obligations) is PRESERVED VERBATIM; v2.39 adds:

**Implements (addition):** + C-CP-25 §25.11 (AMENDED at CP v1.102 §1 row 5 — apply-note 2: admission-rejection = BRANCH FAILURE composing with the EXISTING §25.15 `cascade_policy` table).

**Depends on (addition):** + [U-RT-141 (cross-axis: Runtime — the typed capacity error consumed as a branch-failure cause; co-land)].

**Acceptance criteria (v2.39 additions):**

- **(§1 row 5 — apply-note 2.)** A cap-rejected branch enters the fan-out as a BRANCH OUTCOME — a branch failure driving the EXISTING §25.15 semantics: `cascade-cancel` → cancel not-yet-dispatched siblings, run-level `FAILED`; `proceed` → partial result set, `PARTIAL`/degraded; `pause` → `PAUSED`. NO new control-transfer mode, run-status value, or cascade row is introduced — §25.15 is PRESERVED VERBATIM and simply gains this failure cause among its inputs.
- **(§1 row 4.)** The branch-failure cause is the TYPED step-attributable capacity error (Runtime v1.102 §14.8.10.5, carrier at U-RT-140) — surfaced through the existing `StepDispatcher` fail-propagation path, never a generic executor error.
- **(Change-note witness (f) — the cascade-cancel watchdog's reach into an offloaded child.)** The §25.15 cascade-cancel deadline cancel reaches an offloaded child's fence via the cross-thread-safe `_BRANCH_INFLIGHT_DISPATCHES` cancellation handle (`workflow_driver.py:2092` lineage; carrier Runtime-owned at U-RT-144, §14.8.10.4) — the CP obligation is that cascade-cancel is not silently inert against offloaded branches.

**Tests (v2.39 additions — mutation-probed per PD-8):**

> **Witness (b) — cascade composition:** `test_cap_rejected_branch_drives_existing_cascade_policy_outcomes` (parametrized over `cascade-cancel`/`proceed`/`pause` → `FAILED`/`PARTIAL`/`PAUSED`; mutation probe: introducing a distinct control-transfer path for capacity rejections fails the no-new-mode assertion). **Witness (f):** `test_nested_cascade_deadline_cancel_through_offloaded_child` (pairs with Runtime plan v2.50 U-RT-144's same-named witness; the CP half asserts the watchdog's cancel is observed at the child, not merely issued).

---

## §4 U-CP-89 amendment — `HIERARCHICAL_DELEGATION` depth-phrase retirement + formal delegation of recursion capacity (CP v1.102 §2)

The v2.37 U-CP-89 body is PRESERVED VERBATIM **except** its Scope/Signatures phrase *"with a depth bound"* — which this amendment supersedes (doc-level criterion below); all other body text stands.

**Implements (addition):** + C-CP-25 §25.11 `HIERARCHICAL_DELEGATION` row (AMENDED at CP v1.102 §2 — the "with depth" phrase RETIRED; recursion capacity FORMALLY DELEGATED to the Runtime §14.8.10 executor cap).

**Acceptance criteria (v2.39 additions):**

- **(§2 rows 1–2 — doc-level criterion.)** The strategy implements NO depth bound and carries NO depth carrier: the v1.32 "with depth" phrase named no value and bound no carrier (`sub_agent_descent` is a boolean, `workflow_driver_types.py:319`); recursion capacity — how deep and wide a delegation tree may grow IN TOTAL — is the Runtime §14.8.10 executor cap's authority under the shared frame budget (blocked ancestors count). The unit's plan-body phrase "with a depth bound" (v2.32/v2.37 lineage) is RETIRED with this amendment; any impl-arc reading that materializes a separate CP depth bound is an acceptance FAILURE (the §2 row-5 recorded override NOT taken — re-opening it is an operator decision, not impl discretion).
- **(§2 row 3.)** The per-parent WIDTH cap 3 (C-CP-10 §10.3) is PRESERVED VERBATIM and NOT subsumed: width (per-parent breadth, topology-admissibility) and capacity (global concurrency, resource) are orthogonal; both hold.
- **(§2 row 4 — the dyad's C1 condition.)** A capacity breach during recursive descent surfaces as the TYPED error attributable to the OVERFLOWING DISPATCH STEP with the descent chain in the message — never a generic executor error, never silent starvation of legitimate descent below the ceiling; within a fan-out it composes as a branch failure per the §3 U-CP-85 amendment.

**Tests (v2.39 additions — mutation-probed per PD-8):** `test_delegation_below_cap_unbounded_by_any_cp_depth_bound` (a legal descent deeper than any historically-implied depth value proceeds while frames remain; mutation probe: introducing a CP-side depth check fails it) + `test_capacity_breach_during_descent_surfaces_typed_step_attributable_with_descent_chain` (pairs with the U-RT-140 error-shape witness) + `test_width_cap_3_per_parent_still_enforced` (preservation control).

---

## §5 U-CP-82 amendment — drain-path timestamp call-site change + strict-xfail REMOVAL (CP v1.102 §1 row 8; fork §4 item 7 — co-owned with IS)

The v2.37 U-CP-82 body is PRESERVED VERBATIM; v2.39 adds:

**Implements (addition):** + C-CP-25 §25.11 (AMENDED at CP v1.102 §1 row 8 — the drain-path timestamp-authority binding). The CONTRACT is IS-owned: C-IS-07 §7.6 (IS spec v1.11 — writer-owned timestamp sampling INSIDE the IS `_WRITE_LOCK` on the buffered/branch-drain surface), homed at IS plan v2.7 U-IS-11 — cross-referenced, never restated.

**Acceptance criteria (v2.39 additions):**

- The drain call site (`drain_branch_buffers` at `harness_cp.workflow_driver` — which at HEAD samples `drain_timestamp` BEFORE the IS `_WRITE_LOCK` and re-stamps every buffered payload) is changed to request writer-owned sampling per the C-IS-07 §7.6 contract: any drain-supplied timestamp on this path is a placeholder, not the persisted value. *(The API carrier by which the drain requests writer-owned sampling — mode parameter / sentinel / dedicated entry point — is IS-side implementation discretion per §7.6's deferred list; the CP criterion is that the drain path USES it and no longer carries timestamp authority.)*
- ALL DIRECT append paths (linear step appends and every non-drain CP write) keep caller-supplied timestamp semantics byte-verbatim — the CP side introduces NO change outside the drain call site.
- **(Change-note witness (g) — the xfail removal.)** The strict xfail `test_concurrent_sibling_drains_invert_timestamp` (`harness-cp/tests/test_workflow_driver_buffered_append.py:534-535`, strict=True at HEAD) flips to a PASSING witness when the fix lands, and the strict-xfail marker is REMOVED in the same impl arc. B-48 cannot close over an accepted-failing concurrency witness. Co-land pin: ⊕ IS plan v2.7 U-IS-11.

**Tests (v2.39 additions — mutation-probed per PD-8):**

> **Witness (g):** the un-xfailed `test_concurrent_sibling_drains_invert_timestamp` itself (two concurrent sibling drains persist with no `NonMonotonicTimestampError`, both drains' entries present; the by-construction monotonicity mutation probe rides IS plan v2.7 U-IS-11 — revert to outside-lock capture → the witness must fail again) + re-run of the existing buffered-append concurrency witnesses + the r100 e2e (filing §4 item 7 closing clause).

---

## §6 Coverage matrix delta (v2.38 → v2.39)

| Contract surface | Units covering (delta) |
|---|---|
| C-CP-25 §25.11 fan-out capacity gating (AMENDED at CP v1.102 §1 rows 1–4, 6–7) | **U-CP-86 + U-CP-88 (amended)** (+ Runtime plan v2.50 U-RT-141 cross-axis — the capacity authority) |
| C-CP-25 §25.11 admission-rejection = branch failure under §25.15 (CP v1.102 §1 row 5, apply-note 2) | **U-CP-85 (amended)** |
| C-CP-25 §25.11 `HIERARCHICAL_DELEGATION` row — depth-phrase retirement + formal delegation (CP v1.102 §2) | **U-CP-89 (amended)** |
| C-CP-25 §25.11 B-39 interim sequencing constraint (NEW at CP v1.102 §3) | **U-CP-86 + U-CP-88 (amended)** |
| C-CP-25 §25.11 drain-path timestamp-authority binding (CP v1.102 §1 row 8) + fork §4 item 7 xfail removal | **U-CP-82 (amended)** (contract IS-owned at IS plan v2.7 U-IS-11 — cross-axis) |

DAG: ZERO new within-axis edges; NEW cross-axis consumption edges (atomic, unit-to-unit, declared CP-side): U-CP-86 → U-RT-141, U-CP-88 → U-RT-141, U-CP-85 → U-RT-141. Acyclicity preserved (Kahn-verifiable: the new edges point CP → Runtime only; no Runtime v2.50 unit depends on any U-CP-* unit, so no cycle can close). Co-land pins recorded (not DAG edges): U-CP-86/U-CP-88 ⊕ U-RT-141; U-CP-85/U-CP-86 ⊕ U-RT-144; U-CP-82 ⊕ IS plan v2.7 U-IS-11 — all land in the one B-48 impl arc.

---

## §7 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_39.md` (delta over v2.38) |
| Authored at | Phase 7 — B-48 sync sub-agent dispatch offload apply leg (2026-07-19) |
| Authoring authority | CP spec v1.102 (`Spec_Control_Plane_v1_102.md`, filed 2026-07-19) + `.harness/class_2_fork_b48_sync_subagent_dispatch_offload.md` (RATIFIED 2026-07-18, OPTION B AS RECOMMENDED with all filing-settled riders) + `.harness/council-dyad-b48-apply-2026-07-18.md` (16/16 CONFIRM, zero deviations; apply-notes 1–2 + cite-hygiene incorporated) |
| Predecessor | `Implementation_Plan_Control_Plane_v2_38.md` (v2.38 — B-51/B-52/B-54 CP leg) |
| Siblings (same arc) | `Implementation_Plan_Harness_Runtime_v2_50.md` + `Implementation_Plan_Information_Substrate_v2_7.md` |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
