# Implementation Plan: Control Plane — v2.42 (delta over v2.41)

*v2.42 is the CP plan leg of the RATIFIED **B-39 nested paused-child HITL-response-routing arc**'s **spec leg** (`.harness/class_1_fork_b39_nested_hitl_response_threading.md`, RATIFIED 2026-07-23 — Q1=(A) retire `ResumeContextHolder`; Q2 revised at spec-grounding time to a keyed-field-inside-`ResumeContext` carrier via a second operator `AskUserQuestion`, per `Spec_Control_Plane_v1_106.md` change-note), absorbing **CP spec v1.106** (`Spec_Control_Plane_v1_106.md`, TWO same-day out-of-family review rounds). ONE EXISTING unit is amended — **U-CP-64** (the `ResumeContext` carrier-owning unit, per its own v2.21 landing precedent) carries the `hitl_responses` field + `hitl_response_for` method (keyed by the paused child's own `run_id`, round-2-corrected — see §0.2) and the CONTRACT-level `DriverContext.resume_context_holder` Protocol-field retirement. `PausedChildBranchResumeState` is UNAMENDED — a round-1 draft added a `branch_path` field there; removed at round 2 once keying moved to the already-existing `child_snapshot.run_id`. ZERO new units; ZERO new cluster; ZERO DAG topology change; ZERO cross-axis cascade. This is the SPEC LEG's plan absorption only — impl (code + tests) is a separate follow-on arc per the B-33/B-59 precedent.*

**Status:** Proposed

---

## §0 Change-note (v2.41 → v2.42)

### §0.1 Predecessor

`Implementation_Plan_Control_Plane_v2_41.md` (v2.41 — the B-33 spec+plan leg; U-CP-44 + U-CP-45 amended).

### §0.2 Revision context — CP spec v1.106 absorption, CONTRACT-altitude correction pass

Per `Spec_Control_Plane_v1_106.md` §0/§1: the `ResumeContext` carrier (§26.8.1) gains `hitl_responses`/`hitl_response_for` (U-CP-64's own carrier, per its v2.21 authoring); `DriverContext.resume_context_holder` is retired as a ctx-level binding, with the exact replacement propagation mechanism left to impl discretion (spec §1.3).

**Round-1 correction note (same-day, this arc).** A first draft of this plan delta additionally amended U-CP-86 (`PARALLELIZATION`), U-CP-88 (`ORCHESTRATOR_WORKERS`), and U-CP-89 (`HIERARCHICAL_DELEGATION`) with ACs asserting that these functions' own worker re-dispatch sites directly thread new parameters into a recursive `execute_workflow(...)` call. Out-of-family review (`just codex-review-uncommitted`) plus an `Explore` grounding pass found this call graph EMPIRICALLY FALSE: `_execute_parallelization`/`_execute_orchestrator_workers` do not recursively call `execute_workflow` for a paused-child re-dispatch — they stamp `StepExecutionContext.child_resume_snapshot` and hand off to `harness-runtime`'s `RuntimeSubAgentDispatcher.dispatch()`, which reads that field and invokes an injected `ChildWorkflowRunner` closure (`harness-runtime/lifecycle/child_workflow_runner.py`) that itself calls back into `harness_cp.workflow_driver.execute_workflow`. The propagation-mechanism wiring this arc's spec-leg contract (spec §1.2) obligates therefore crosses the CP↔Runtime package boundary at a DIFFERENT seam than this plan delta assumed, and may touch U-CP-86/88/89, may touch Runtime-owned units (`sub_agent_dispatch.py`, `child_workflow_runner.py`), or both — this is genuine scope-discovery work belonging to the impl leg, not something this spec-leg plan delta can responsibly assert today. §2-§4 (the U-CP-86/88/89 amendments) are THEREFORE REMOVED from this delta rather than re-authored against a fourth unverified call graph; see §5 below for the deferred-scope note.

**Round-2 correction note (same-day, second out-of-family pass).** After round 1 landed, a second `just codex-review-uncommitted` pass found the round-1-corrected `hitl_responses` key shape — `branch_path` (CP spec v1.106 §0, `compose_branch_path`) — is ALSO wrong: it derives from a workflow_id-scoped `action_id` with NO run-instance component, so it collides when two peer branches dispatch the SAME `child_workflow_id` (an explicitly supported scenario). The fix keys `hitl_responses` by the paused child's own `run_id` instead (`PausedChildBranchResumeState.child_snapshot.run_id` — an EXISTING `PauseSnapshot` field, genuinely unique across recursion depth AND repeated same-`child_workflow_id` dispatch, per the `compose_child_run_id_seed` derivation chain CP spec v1.106 §0 traces). This requires NO new field on `PausedChildBranchResumeState` — the round-1 draft's `branch_path` field addition is REMOVED as unnecessary. §1 below (U-CP-64's amendment) is updated accordingly.

### §0.3 Sections revised

§0 (this change note); §1 (the one unit amendment); §5 (coverage delta, including the deferred-scope note). All other sections — every other unit body, all dependency graphs, cross-cutting units, open items — PRESERVED VERBATIM from v2.41.

### §0.4 Scope discipline

ADDITIVE / amended-unit scope only. ZERO new atomic units; ZERO new contract IDs; ZERO new within-axis DAG edges. ZERO cross-axis cascade asserted by THIS delta (the eventual propagation-mechanism wiring's cross-axis shape, if any, is impl-leg scope-discovery work — see §0.2 correction note).

---

## §1 U-CP-64 amendment — `ResumeContext.hitl_responses` (keyed by `child_run_id`) + `DriverContext.resume_context_holder` retirement (contract only)

The v2.21 U-CP-64 body (last full re-table; PRESERVED VERBATIM through v2.41) is amended as follows.

- **Implements (addition):** + CP spec v1.106 §0 (`ResumeContext.hitl_responses` + `hitl_response_for`, keyed by `child_run_id` — round-2-corrected) + §1.2/§1.4 (`DriverContext.resume_context_holder` retirement — CONTRACT only; the replacement delivery mechanism's exact wiring is impl discretion, NOT asserted by this unit). **§2 (the round-1 `PausedChildBranchResumeState.branch_path` field) is NOT implemented by this unit — that field was REMOVED at the round-2 correction; do not reintroduce it.**
- **Files (EXTEND):** `harness-cp/src/harness_cp/pause_resume_protocol_types.py` — EXTEND `ResumeContext` (ADD `hitl_responses: dict[str, HITLResult] | None = None` field + `hitl_response_for(child_run_id: str) -> HITLResult | None` method, keyed by the paused child's own `run_id` — round-2-corrected, see below; NOT a verbatim mirror of `effect_fence_resolutions`/`effect_fence_resolution_for`'s `idempotency_key` keying, since that key does not have this field's recursion-collision exposure). `harness-cp/src/harness_cp/workflow_driver.py` — AMEND `DriverContext` Protocol (the class itself is defined here, around line 510; REMOVE its `resume_context_holder: object | None` field, around line 641 — the field's replacement, if any, and its consumption sites are OUT OF SCOPE for this unit; that is impl-leg scope-discovery work per §0.2). **NO change to `PausedChildBranchResumeState`** (`pause_resume_protocol_types.py`) — a round-1 draft added a `branch_path` field here; REMOVED at round 2 once keying moved to `child_snapshot.run_id` (an EXISTING field, no addition needed). Do NOT re-add it.
- **Signatures:** `def hitl_response_for(self, child_run_id: str) -> HITLResult | None` (NEW method on `ResumeContext`). No `execute_workflow` signature change is asserted by this unit (a prior draft asserted one; corrected — see §0.2).
- **Depends on:** [U-CP-62, U-CP-63] (preserved verbatim)
- **ACs (preserved verbatim #1-#6 from v2.15 through v2.21 chain; NEW ACs #7-#8 at v2.42, round-2-corrected):**
  1-6. (preserved verbatim — snapshot hash validation, material diff detection, STRICT/OPERATOR_ARBITRATE policy handling, U-CP-56 coexistence, `ResumeContext` carrier landing per v1.16 §26.8.1)
  7. **NEW at v2.42, round-2-corrected (was keyed by `branch_path`; a round-2 out-of-family review round found this collides when two peer branches dispatch the SAME `child_workflow_id`, since `branch_path` derives from a workflow_id-scoped identifier with no run-instance component).** `ResumeContext.hitl_responses: dict[str, HITLResult] | None = None` field + `hitl_response_for(child_run_id)` method land per CP spec v1.106 §0 — default+per-key-override composition, keyed by the paused child's own `run_id` (`PausedChildBranchResumeState.child_snapshot.run_id`, an EXISTING `PauseSnapshot` field — genuinely unique across recursion depth AND repeated same-`child_workflow_id` dispatch, per the `compose_child_run_id_seed` derivation chain CP spec v1.106 §0 traces). A `child_run_id` key matching no currently-paused branch this round is harmlessly ignored; an unaddressed branch falls back to the uniform `hitl_response`; `None`+`None` → re-pause INERT (never an auto-re-fire). Unit test verifies: map-hit override, map-miss fallback-to-uniform, both-`None` → `None`, byte-identical single-branch behavior when `hitl_responses` is never supplied (pre-B-39 callers unaffected), AND — the round-2 fix's own witness — TWO peer branches dispatching the IDENTICAL `child_workflow_id` resolve to DISTINCT `hitl_responses` entries via their own distinct `child_snapshot.run_id` values (mutation probe: keying by `branch_path` instead causes this test to fail with both peers reading the same map entry). CRITICAL: the fallback-to-uniform test MUST assert against the ORIGINAL, caller-supplied `ResumeContext` instance (never a copy) — `hitl_response_for` must never be called against a field-mutated derivative (CP spec v1.106 §1.2's rejected-design note — this remains true regardless of what the impl leg's eventual propagation mechanism turns out to be).
  8. **NEW at v2.42.** `DriverContext.resume_context_holder: object | None` Protocol field is REMOVED. Unit test verifies the `DriverContext` Protocol no longer declares the field (structural-typing check against a minimal conforming test double). This AC does NOT assert what replaces the field's 3 existing consumption sites (the linear + 2 fan-out effect-fence peek readers) — that re-pointing is impl-leg scope-discovery work, since the correct replacement shape depends on the propagation mechanism the impl leg grounds and lands (§0.2).

**Rollback boundary (preserved verbatim from v2.21; extended at v2.42).** Revert the `hitl_responses`/`hitl_response_for` addition + revert the `DriverContext.resume_context_holder` removal (restore the field).

---

## §2-§4 — REMOVED at this correction pass

A prior draft of this delta carried U-CP-86 (`PARALLELIZATION`), U-CP-88 (`ORCHESTRATOR_WORKERS`), and U-CP-89 (`HIERARCHICAL_DELEGATION`) amendments here, asserting specific `workflow_driver.py` worker-re-dispatch-site code changes. Removed per §0.2's correction note — the asserted call graph (a direct intra-CP recursive `execute_workflow` call at these sites) is empirically false; the real propagation-mechanism wiring crosses into `harness-runtime` and is impl-leg scope-discovery work, not assertable at this spec leg. These three units remain UNAMENDED by this plan delta; their v2.39/v2.41 bodies are PRESERVED VERBATIM.

---

## §5 — Coverage matrix delta

| Spec contract | Plan unit(s) |
|---|---|
| CP spec v1.106 §0 (`ResumeContext.hitl_responses` + `hitl_response_for`, keyed by `child_run_id` — round-2-corrected) | U-CP-64 |
| CP spec v1.106 §2 (round-1 `branch_path` field — REMOVED at round 2, no longer a live contract) | N/A — superseded, no unit owed |
| CP spec v1.106 §1.2/§1.4 (`DriverContext.resume_context_holder` retirement — CONTRACT: field removal only) | U-CP-64 |
| CP spec v1.106 §1.2 (replacement delivery-mechanism CONTRACT — per-branch-distinct resolution, one-shot-under-retry, no new global sharing) | **DEFERRED — no unit owned at this spec leg.** The impl leg owns a fresh scope-discovery + grounding pass (against the REAL call graph: `harness_runtime/api.py`'s `resume()` + `lifecycle/mcp_server.py` for depth-0; `StepExecutionContext.child_resume_snapshot` → `RuntimeSubAgentDispatcher` → `ChildWorkflowRunner` → `child_workflow_runner.py` for nested children) to determine which unit(s) — U-CP-86/88/89, Runtime-owned units, or a mix — carry this contract's acceptance criteria. This is an explicit gap, not a silent omission (per workspace `CLAUDE.md` §13.1 "no silent caps" discipline). |
| CP spec v1.106 §1.3 (impl discretion note itself) | N/A — a statement about scope, not a testable contract |

DAG topology preserved verbatim from v2.41 — ZERO new edges, ZERO new units.

---

## §6 — Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_42.md` |
| Version | v2.42 |
| Filing event | B-39 spec leg (Q1=(A) + Q2 revised-at-grounding) plan absorption; TWO same-day correction passes — round 1 (out-of-family review + empirical re-grounding falsified the U-CP-86/88/89 amendments' call-graph premise) and round 2 (out-of-family review found the `hitl_responses` key shape collides on repeated same-`child_workflow_id` dispatch; re-keyed to `child_run_id`, `branch_path` field addition removed) |
| Predecessor | `Implementation_Plan_Control_Plane_v2_41.md` |
| Operator authority | Fork ratification 2026-07-23 (Q1/Q2 original); `AskUserQuestion` 2026-07-23 (Q2 carrier-shape reconcile) |
| Co-published artifacts (this arc) | `Spec_Control_Plane_v1_106.md`; `Spec_Harness_Runtime_v1.md` v1.106; `Implementation_Plan_Harness_Runtime_v2_54.md`; clearance markers for both specs; workspace `CLAUDE.md` + `harness-cp/CLAUDE.md` pointer bumps |
| Unit-count change | None (102 → 102 — one amended-unit-body amendment; U-CP-86/88/89 unamended) |
| Cluster-count change | None |
| DAG topology change | None |
| Cross-axis cascade | None asserted by this delta — the eventual propagation-mechanism wiring's cross-axis shape is impl-leg scope-discovery work (§5 deferred row) |
| Impl leg | NOT bundled — code + tests land as a separate follow-on arc per the B-33/B-59 precedent; the impl leg additionally owes the scope-discovery pass §5 defers |
| Skill discipline | `implementation-planner` Phase-7 revision-pass absorbing upstream CP spec v1.106 into ONE existing unit body; fidelity-pure amendment-only pass; NO contract addition beyond the spec; NO unit re-decomposition; NO DAG topology change; NO assertion of unverified wiring (corrected from a first draft that did) |
| Date | 2026-07-23 |
