# Implementation Plan — Harness Runtime — v2.43

*Delta over v2.42. v2.43 is the runtime-axis leg of **R-FS-1 arc #6 (B1-plan)** — the atomic-unit decomposition of the B1 sub-program's runtime-side amendment, **runtime spec v1.48** (the runtime materialization of the 5 non-`SINGLE_THREADED_LINEAR` topology driver strategies). TWO NEW units: **U-RT-113** — the `RunStatus.PARTIAL` runtime projection (C-RT-09 §9 `status` `Literal` widen + the `_CP_TO_RT_STATUS[PARTIAL]→'partial'` mapping); **U-RT-114** — the branch `AgentRole` dispatch-read (the model-binding half of the C-RT-15 §14.5.3 role seam). The §2.2 materialization **site** is the **existing** stage-5 composition (no new binding — NOT a unit, §6 Open-item); the buffered-drain + write-cadence are CP-driver-internal (decomposed at CP plan v2.32). Co-published with CP plan v2.32 + IS plan v2.6. ZERO spec amendment (runtime spec canonical at v1.48). v2.42 + earlier PRESERVED VERBATIM per delta-only-plan-chain convention.*

**Status:** Proposed

---

## §0 Change-note (v2.42 → v2.43)

### §0.1 Predecessor

`Implementation_Plan_Harness_Runtime_v2_42.md` (v2.42 — the H_T-IS-2 apply-pass impl-half; NEW U-RT-112 `resolve_procedural_tier_snapshot`).

### §0.2 Revision scope (v2.42 → v2.43)

v2.43 decomposes the runtime-OWNED surfaces of **runtime spec v1.48** (cleared at `.harness/clearance/Spec_Harness_Runtime-v1_48-cleared-2026-06-13.md`) into TWO NEW units. The runtime spec authored three sites; their plan homes split by code-residence:

| Runtime spec site | Plan home | Rationale |
|---|---|---|
| **C-RT-09 §9** — `RunResult.status` `Literal` +`'partial'` + the `_CP_TO_RT_STATUS[PARTIAL]→'partial'` projection | **U-RT-113** (runtime; code at `api.py`) | Pure runtime-axis projection surface |
| **§14.5.3** — branch `AgentRole` dispatch-read (model binding only) | **U-RT-114** (runtime; code at `llm_dispatch.py`) | The dispatch-read is the runtime half of the §25.14 role seam |
| **§2.2(a)** materialization SITE — existing stage-5 composition is sufficient, **no new binding** | **NO unit** (§6 Open-item O-RT-1) | "No change needed" is not an atomic coherent change (§3.1); dispositioned as a note, not unit-ified |
| **§2.2(b/c/d)** buffered-drain + write-cadence + branch `StepExecutionContext` composition | **CP plan v2.32** (U-CP-81/82/84) | CP-driver-internal — the strategies + drain + cadence + context run **inside** `workflow_driver.py` (harness-cp) per runtime spec §2.2; runtime spec §2.2 is the contract, the code lands CP-side |

### §0.3 Sections preserved verbatim from v2.42

| Section | Status at v2.43 |
|---|---|
| §0 (v2.42 change-note) | Superseded by this §0 (historical record preserved at v2.42) |
| §1 Spec inventory | Refreshed: runtime spec → **v1.48** canonical at HEAD; +2 contract rows (C-RT-09 §9 `'partial'`; C-RT-15 §14.5.3); all prior rows unchanged |
| §2 — U-RT-01..U-RT-112 (all prior units) | **PRESERVED VERBATIM** from v2.42 + lineage (see prior plan deltas; delta-only-plan-chain convention) |
| §3 Dependency graph | Revised at the U-RT-113 / U-RT-114 nodes only (§3 below); all prior edges + acyclicity preserved verbatim |
| §4 Coverage matrix | Revised: +2 rows (C-RT-09 §9 `'partial'`; C-RT-15 §14.5.3); all prior rows preserved verbatim |
| §5 / §6 | Extended per below |

### §0.4 Authority chain — no operator gate

v2.43 absorbs a **cleared** spec amendment (runtime v1.48, APPROVE-WITH-CLASS-3 + Codex 3-[P2]-fixed + advisor 4/4-deliverables at PR #533). No operator decision owed; ZERO X-AL-3 risk (plan-layer decomposition of a cleared contract, no spec amendment).

### §0.5 Status posture

`Status: Proposed`. Clearance marker filed at `.harness/clearance/Implementation_Plan_Harness_Runtime-v2_43-cleared-2026-06-13.md`. Sibling co-publications: CP plan v2.32 + IS plan v2.6.

---

## §1 Spec inventory

PRESERVED VERBATIM from v2.42 §1, **plus**:

| Contract | Version | Status at v2.43 |
|---|---|---|
| **C-RT-09 §9** (`RunResult.status` `Literal` +`'partial'`; `_CP_TO_RT_STATUS[PARTIAL]→'partial'` projection; the `'partial'` graceful-degradation invariant; exit-code already-`1`) | **runtime spec v1.48 (extended)** | **Covered at U-RT-113 (NEW)** |
| **C-RT-15 §14.5.3** (branch `AgentRole` dispatch-read — model binding only; per-role prompt deferred to B4) | **runtime spec v1.48 (NEW subsection)** | **Covered at U-RT-114 (NEW)** |
| C-RT-02 §2.2(a) (non-linear materialization site — existing stage-5 composition sufficient) | runtime spec v1.48 | NO unit (no-change disposition); §6 Open-item O-RT-1 |

---

## §2 Atomic-unit decomposition

### §2.1 Preserved-verbatim units

U-RT-01..U-RT-112 — PRESERVED VERBATIM from v2.42 + lineage (delta-only-plan-chain convention).

### §2.2 NEW units (2)

#### U-RT-113 — `RunStatus.PARTIAL` runtime projection (C-RT-09 §9)

**Scope.** Widen the runtime-facing `RunResult.status` `Literal` to admit `'partial'` and flip the `_CP_TO_RT_STATUS` projection entry from the v1.4 defensive `PARTIAL → 'failed'` placeholder to `PARTIAL → 'partial'`, so a `proceed`-cascade graceful-degradation run (CP `RunStatus.PARTIAL`) surfaces at the public API as `RunResult.status == 'partial'`. One coherent change at the CP→runtime status-projection surface.

**Spec linkage.** C-RT-09 §9 (the `status` `Literal` widen + the `'partial'` graceful-degradation invariant + `failure_cause` stays `None` + no `degraded` field). CP spec v1.32 §25.15.1 (the `proceed` cascade → `RunStatus.PARTIAL` run-level outcome this projects). Runtime §14.18.2 (exit-code mapping — already lists `PARTIAL → 1`; no edit, the unit asserts the existing mapping holds for the now-distinct literal).

**Surfaces affected.** The CP-`RunResult` → runtime-`RunResult` projection map (`_CP_TO_RT_STATUS`) and the `RunResult.status` `Literal` type annotation in the runtime API surface; the CLI exit-code mirror (`_CP_STATUS_TO_EXIT_CODE`, asserted already-correct — already maps `"partial"`).

**Signatures introduced or modified** (transcribed from runtime spec v1.48 §9, NOT redesigned):
- `RunResult.status: Literal['completed', 'drained', 'failed', 'paused', 'partial']` (add `'partial'` — minor type-widen).
- `_CP_TO_RT_STATUS[RunStatus.PARTIAL] = 'partial'` (flip from `'failed'`).

**Depends on.** (none) — the CP `RunStatus.PARTIAL` enum member is code-real (pre-existing, reserved at CP §25.2); this unit is the runtime-side projection only.

**Acceptance criterion (functional).** Given a CP `RunResult(status=RunStatus.PARTIAL, …)`, `_build_run_result` projects `RunResult.status == 'partial'`; `failure_cause is None` (a degraded run did not fail — the existing `status=='failed' ⟹ failure_cause is not None` invariant is unchanged); `terminal_state` carries the partial aggregate; no `degraded` field is added. A `'partial'`-projection unit test asserts the mapping + the invariant. The `pyright`-strict `Literal` narrows cleanly (no `KeyError`, no exhaustiveness gap).

**Acceptance criterion (integration).** Under a `PARALLELIZATION` / fan-out workflow with `cascade_policy = proceed` and ≥1 failed branch (CP plan v2.32 U-CP-85 + a strategy), `api.run(...)` returns `RunResult.status == 'partial'` and the CLI exit code is `1` per §14.18.2 (the cross-axis integration, exercised at B1-impl-N).

**Notes.** Mirrors the v1.45 `'paused'` type-widen exactly (the minor-bump precedent). No new `RunStatus` value (PARTIAL is the CP §25.2 reserved value, now activated by `proceed`).

#### U-RT-114 — branch `AgentRole` dispatch-read — model binding (C-RT-15 §14.5.3)

**Scope.** Make the runtime LLM-dispatch composer read `step_context.agent_role` (the branch `AgentRole` carried on the CP-composed child `StepExecutionContext`, CP plan v2.32 U-CP-81) to index the per-role **model binding** (`RoutingManifest.per_role_bindings`), replacing the hardcoded `_MVP_DEFAULT_AGENT_ROLE` discard — so worker/delegation/handoff branches route per-role models. One coherent change at the dispatch seam. **Model binding only** — the per-role prompt is NOT in scope (resolved once at stage 0 with the default role before branch contexts exist; deferred to B4).

**Spec linkage.** C-RT-15 §14.5.3 (primary — the dispatch-read mechanism, the model-binding-only scope, the per-role-prompt→B4 deferral). CP spec v1.32 §25.14 (the role seam — the CP `StepExecutionContext` carries `AgentRole`, the runtime indexes it). C-CP-01 §1.3 (`RoutingManifest.per_role_bindings` — the per-role model binding indexed).

**Surfaces affected.** The runtime LLM-dispatch composer's role-resolution point (where `_MVP_DEFAULT_AGENT_ROLE` is bound today) — read `step_context.agent_role` for the per-role `RoutingManifest.per_role_bindings` lookup.

**Signatures introduced or modified** (transcribed from runtime spec v1.48 §14.5.3 — NO new signature; a read-substitution): the dispatch composer indexes `RoutingManifest.per_role_bindings[step_context.agent_role]` (fall-through to the default model binding on miss / `"default"` role / empty catalog — byte-identical to v1.47 in that case). No `StepExecutionContext` shape change here (the `agent_role` field is added CP-side at U-CP-81).

**Depends on.** [U-CP-81 (cross-axis: CP) — the branch `StepExecutionContext` carrying the `agent_role` field this unit reads]. (Direction: runtime → CP, matching the `harness-runtime` → `harness-cp` package dependency — downstream, no cycle.)

**Acceptance criterion (functional).** Given a `StepExecutionContext` with `agent_role` set to a role present in `RoutingManifest.per_role_bindings`, the composer dispatches against that role's model binding (not `_MVP_DEFAULT_AGENT_ROLE`'s). Given `agent_role` = `"default"` / absent / an empty catalog, dispatch is byte-identical to v1.47 (fall-through to the manifest default — a non-breaking-default test asserts this). The `SINGLE_THREADED_LINEAR` path (no branch child context) reads the existing default-role path verbatim (regression-safe).

**Acceptance criterion (integration).** Under an `ORCHESTRATOR_WORKERS` workflow (CP plan v2.32 U-CP-88) with per-role model bindings, distinct workers dispatch against distinct per-role models — the worker patterns are non-hollow by per-role model specialization. Verified at B1-impl-N (live e2e where a provider step is involved).

**Notes.** Per-role **prompt** specialization is explicitly OUT of scope (the stage-0 single-prompt resolution per C-CP-29 §29.4 predates the branch context) — deferred to R-FS-1 child-arc B4, per runtime spec §14.5.3.

---

## §3 Dependency graph

### §3.1 Dependency-graph delta (v2.43)

| Operation | Detail |
|---|---|
| NEW node | U-RT-113 (`Depends on: (none)` — runtime projection of a code-real CP enum member) |
| NEW node | U-RT-114 (`Depends on: [U-CP-81 (cross-axis: CP)]`) |
| NEW cross-axis edge | U-RT-114 → U-CP-81 (runtime → CP; downstream package direction) |

### §3.2 Acyclicity preservation

U-RT-113 is a leaf (`(none)`). U-RT-114 → U-CP-81 runs **runtime → CP**, matching the `harness-runtime` → `harness-cp` package dependency; no CP unit depends back on U-RT-114 (the CP strategies SET `agent_role` on the context via U-CP-81; the runtime READS it via U-RT-114 — no CP→RT edge, so no cycle). Aggregate B1 acyclicity + topological order recorded at CP plan v2.32 §3 (the arc's aggregate-graph home). Runtime-axis internal DAG PRESERVED VERBATIM plus the two new nodes.

---

## §4 Coverage matrix

### §4.1 Coverage-matrix delta (v2.43)

| Spec contract | Atomic unit |
|---|---|
| runtime spec v1.48 C-RT-09 §9 (`'partial'` `Literal` widen + `_CP_TO_RT_STATUS[PARTIAL]→'partial'` projection + invariant) | **U-RT-113** (NEW) |
| runtime spec v1.48 C-RT-15 §14.5.3 (branch `AgentRole` dispatch-read — model binding) | **U-RT-114** (NEW) |
| runtime spec v1.48 C-RT-02 §2.2(a) (materialization site — existing stage-5 sufficient, no new binding) | NO unit — §6 Open-item O-RT-1 (no-change disposition) |

All other C-RT-* rows PRESERVED VERBATIM from v2.42 §4. (Runtime spec §2.2(b/c/d) — buffered-drain / write-cadence / branch `StepExecutionContext` composition — are covered at CP plan v2.32 U-CP-81/82/84, the CP-driver-internal code home.)

---

## §5 Cross-cutting integration units

None new at v2.43. (The runtime spec §2.2 write-cadence — the one tri-spec cross-cutting surface — is covered as a cross-cutting integration unit at **CP plan v2.32 U-CP-84**, its CP-producer code home, citing CP §25.13 + IS §5.4 + runtime §2.2c.)

---

## §6 Open items

**O-RT-1 — runtime §2.2(a) materialization-site confirmation (no-change; NOT a unit).** Runtime spec v1.48 §2.2(a) states the non-linear topology materialization site is the **existing** stage-5 LOOP_INIT composition (`ctx.topology_dispatcher` / `ctx.step_dispatchers` / `ctx.state_ledger_writer` already bound) — **no new stage-5 binding**, and the CP driver is invoked via the existing C-RT-08 `execute_workflow` (no new runtime invocation surface). Per the implementation-planner atomicity discipline (§3.1 — a unit produces a coherent *change*; "no change needed" is not one), this is **not unit-ified**; it is recorded here as a satisfied-by-existing-substrate confirmation. The B1-impl-N executor verifies no new stage-5 binding is introduced when the strategies land (a regression check that the §2 stage-5 post-condition is not widened). Cited at the coverage matrix (§4.1) as a no-unit disposition, NOT an uncovered row.

---

## §7 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.43 (delta over v2.42) |
| Authored at | 2026-06-13 |
| Authoring authority | R-FS-1 arc #6 (B1-plan); runtime spec v1.48 (cleared PR #533); design `.harness/r-fs-1-b1-topology-orchestration-design-v1.md` §8 |
| Net delta | +2 NEW units (U-RT-113 `Depends on: (none)`; U-RT-114 `Depends on: [U-CP-81 cross-axis: CP]`); +1 cross-axis edge (U-RT-114 → U-CP-81); +2 coverage rows; +1 §6 Open-item (O-RT-1, no-change disposition for §2.2a); ZERO spec amendment |
| Sibling co-publications | CP plan v2.32 (11 units) + IS plan v2.6 (U-IS-19); clearance markers; workspace `CLAUDE.md` §2.4 plan-head bumps |
| Cross-axis cascade | U-RT-114 → U-CP-81 (runtime → CP, downstream) |
