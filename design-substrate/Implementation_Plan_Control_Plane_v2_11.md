# Implementation Plan — Control Plane (CP axis) — v2.11

**Status: Proposed.**

**Revision:** v2.11 — Phase 7 architectural-tension revision pass, in-CLI. **Adds two new atomic units (U-CP-56 + U-CP-57)** absorbing the new C-CP-25 `WorkflowDriver` contract from `Spec_Control_Plane_v1_4.md` §25 (operator-ratified 2026-05-20 per `.harness/c_cp_25_workflow_driver_recommendation.md`). Unit count 58 → **60**. Predecessor: v2.10 (sub-phase 7c prerequisite status-reconciliation delta).

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `CLAUDE.md` §1.3 authority chain; `implementation-planner` SKILL §2 atomic-decomposition discipline + §8 revision-pass mode. Companion: `Cross_Axis_Composition_Document_v2_2.md`.

**Entry authorization:** Phase 7 architectural-tension resolution path lane 4 (per `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` Resolution Status); operator-ratified at C-CP-25 contract spec-side absorption (Spec_Control_Plane_v1_4.md filed 2026-05-20).

---

## §0 Change-note

### §0.1 Trigger

Operator ratified `.harness/c_cp_25_workflow_driver_recommendation.md` 4/4 sign-off points 2026-05-20 + Path B operator decision 2026-05-20 (no pre-step `step.boundary` emit at drain; preserve §5.2 step.kind 5-value enum). Spec-writer applied C-CP-25 contract into `design-substrate/Spec_Control_Plane_v1_4.md` §25 same session. This v2.11 plan absorbs that new contract into the CP atomic-unit plan, satisfying the post-spec downstream effect declared in CP spec v1.4 Change-note "Cross-cascade-step coordination" row: "CP plan v2.11 revision-pass (`implementation-planner`) → new atomic units U-CP-NN (driver core) + U-CP-NN+1 (drain composition)."

### §0.2 Scope + new units

**Two new atomic units added at v2.11; no existing v2.10 unit revised.** C-CP-25 is a greenfield contract (added at spec v1.4), so the absorption is purely additive — no v2.10 unit cites C-CP-25, so no existing unit body is touched.

| New unit | Implements | One-line scope |
|---|---|---|
| **U-CP-56** | C-CP-25 §25.1 (scope), §25.2 (signatures), §25.3 (iteration discipline), §25.5 (lifecycle event emission boundaries), §25.6 (replay-resumption composition with §8.2 idempotency-key join), §25.7 (failure modes 1–4) | Workflow execution driver core: types (`RunResult`, `RunStatus`, `TopologyPatternNotYetMaterializedError`, `EngineClassNotYetMaterializedError`), `execute_workflow()` happy-path implementation with topology + engine-class validation, step iteration loop, lifecycle event emission filter, replay-resumption read |
| **U-CP-57** | C-CP-25 §25.4 (drain protocol — 4-site check pattern), §25.7 (failure mode 5 — `RT-FAIL-DRAIN-TIMEOUT` composition) | Workflow driver drain composition: 4-site drain check (driver entry / per-step pre-entry / per-step post-exit / no mid-step) consuming `HarnessContext.drained_flag` per U-RT-44; returns `RunResult(status=DRAINED)` with correct `terminal_step_index` + `partial_state` per drain site |

Path B operator-ratified deviation honored: U-CP-56 §25.3.3.1 + U-CP-57 §25.4 row "Per-step pre-entry" implement drain-without-emit (no terminal `step.boundary` event at pre-step-entry drain; `step.kind` 5-value enum at §5.2 preserved verbatim). Terminal observability at pre-step-drain site is `RunResult.status='drained'` + `terminal_step_index` return only.

### §0.3 Sections preserved verbatim from v2.10

All v2.10 sections preserved verbatim. The v2.10 §0.2 reconciliation (`RoleRoutingBinding` / `WorkloadRoutingOverride`), §0.3 status of v2.9 §0.5, §0.4 U-CP-46 citation-precision Class 3, §0.5 scope statement, §0.6 dependency-graph delta, §0.7 filing footer are all preserved verbatim and inherit through this v2.11 revision unchanged. Unit bodies U-CP-00 / U-CP-00b / U-CP-00c / U-CP-01 through U-CP-55 are inherited from the v2.10 stack (with v2.6 onward declaration-site reconciliations preserved) unchanged.

**No signature change, no acceptance-criterion logic change, no contract decomposition revision, no dependency-edge change among v2.10's 58 units.** This v2.11 revision is strictly additive: two new units added; everything else preserved.

### §0.4 Dependency-graph delta

Within-CP-axis DAG: 2 new nodes added; 6 new directed edges added. New nodes are sink-only at v2.11 (no v2.10 unit depends on U-CP-56 or U-CP-57). Acyclic invariant preserved.

**U-CP-56 dependency edges:**
- U-CP-56 ← U-CP-13 (manifest schema input)
- U-CP-56 ← U-CP-14 (per-step `resolve_step_binding` resolver)
- U-CP-56 ← U-CP-10 (lifecycle event taxonomy `WorkflowEventClass` — declaration-site at CP plan; type carried at `harness-core` U-CORE-01 per CP plan v2.6 D9 / Q-R4-7 reconciliation)
- U-CP-56 ← U-CP-15 (`EngineClass` enum declaration)
- U-CP-56 ← U-CP-01 (cap-aware router thin core — step dispatch surface)
- U-CP-56 ← U-IS-07 (cross-axis: IS) — state-ledger entry shape per `Spec_Information_Substrate_v1.md` C-IS-05
- U-CP-56 ← U-IS-10 (cross-axis: IS) — state-ledger-entry-shape export per C-IS-10 §10.1
- U-CP-56 ← U-IS-11 (cross-axis: IS) — state-ledger append discipline per C-IS-11

**U-CP-57 dependency edges:**
- U-CP-57 ← U-CP-56 (driver core)
- U-CP-57 ← U-RT-44 (cross-axis: runtime) — `HarnessContext.drained_flag` per `Spec_Harness_Runtime_v1.md` §11 C-RT-11

Topological-sort placement (within-axis CP): U-CP-56 is a leaf consumer that anchors on the existing manifest / resolver / router / lifecycle / engine-class substrate (U-CP-01, U-CP-10, U-CP-13, U-CP-14, U-CP-15); cross-axis on IS substrate (U-IS-07/10/11). U-CP-57 depends on U-CP-56 + cross-axis runtime U-RT-44. Both are leaves at v2.11 — no v2.10 unit depends on them.

**Cross-axis edges introduced:** 4 new cross-axis edges (3 CP→IS for U-CP-56, 1 CP→runtime for U-CP-57). These compose against existing cross-axis composition patterns at `Cross_Axis_Composition_Document_v2_2.md` (CP→IS bucket already populated with state-ledger composition edges from U-CP-13/U-CP-14 audit-ledger entries; CP→runtime is a new edge class arising from this v2.11). The 4 new cross-axis edges should be reflected at the next CXA revision pass (v2.3 already exists per workspace inventory; if this v2.11 lands before that next CXA revision, the edges are tracked at the CXA composition pass).

### §0.5 Coverage matrix delta

Coverage matrix gains one new column pair (C-CP-25, with §25.1–§25.7 sub-sections) and two new row entries (U-CP-56 + U-CP-57). Cell marks:

| | C-CP-25 §25.1 (scope) | §25.2 (signatures) | §25.3 (iteration) | §25.4 (drain) | §25.5 (event filter) | §25.6 (resumption) | §25.7 (fail modes) |
|---|---|---|---|---|---|---|---|
| **U-CP-56** | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ (modes 1–4) |
| **U-CP-57** | — | — | — | ✓ | — | — | ✓ (mode 5 composition) |

Aggregate: C-CP-25 is fully covered at v2.11 (every contract sub-section §25.1–§25.7 has at least one materializing unit). Both new units cite their governing C-CP-25 sub-sections per §4.2 spec-traceability.

R-CP-04 (workflow lifecycle event surface) materialization site now exists at the plan layer: U-CP-56 + U-CP-57 jointly. R-CP-07 (replay-resumption semantics) materialization extends to U-CP-56 (was implicit at C-CP-08 + C-CP-09; now driver-side at C-CP-25 §25.6).

### §0.6 Carry-forward findings from CP spec v1.4 Change-note

Three adjacent-defect findings filed at CP spec v1.4 Change-note "Adjacent-defect findings surfaced (not patched at v1.4)" section. These are inherited by this plan as **carry-forwards** — not blockers at v2.11 land:

| Finding | Disposition at v2.11 |
|---|---|
| **§B (per-engine-class lease mechanism mapping under-specified at CP spec)** | U-CP-56 acceptance criterion #4 inherits the under-specification: at implementation time, lease mechanism per engine class is resolved per `c1-orchestration-control` SKILL.md substrate authority. For the v2.11 scope (`pure-pattern-no-engine` + `save-point-checkpoint`), the conservative reading is: `pure-pattern-no-engine` → no lease acquired (state-ledger native dedup per §8.2); `save-point-checkpoint` → checkpointer-owned write-slot mechanism resolved at implementation (likely `engine_native` per §5.3 enum). Acceptance allows either substrate-anchored reading. Routing: surfaced for follow-up CP spec revision pass when first non-in-scope topology / engine class materializes. |
| **§C (`EngineClassNotYetMaterializedError` introduced for symmetry)** | Typed-error name carried verbatim into U-CP-56 §25.7 acceptance. Operator may rename at next revision pass; mechanical token replacement (no unit re-decomposition). |
| **§D (Path B drain-emit deviation)** | Honored at U-CP-56 §25.3.3.1 + U-CP-57 §25.4 acceptance: no pre-step `step.boundary` emit at drain; preserves §5.2 step.kind 5-value enum verbatim. |

### §0.7 Downstream effects flagged

| Effect | Site | Triggered when |
|---|---|---|
| Runtime un-strike of U-RT-44 AC #2 (in-flight step bounded-wait) + U-RT-49 workflow-execution ACs (state-ledger workflow entries; collector sqlite spans per workflow step; cost-attribution chain entry) | `harness-runtime/` test suite + spec amendments | At U-CP-56 + U-CP-57 land; refactor `harness-runtime/` to delegate drain to the driver per `Spec_Harness_Runtime_v1.md` §11 risk-surface guidance ("This contract becomes a thin adapter"). |
| `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` status flip OPEN-RESOLVING → CLOSED | Tension record | At runtime un-strike completion |
| CXA composition document next revision pass | `Cross_Axis_Composition_Document_v2_X.md` | Reflect 4 new cross-axis edges (3 CP→IS via U-CP-56; 1 CP→runtime via U-CP-57). Non-blocking; tracked at next CXA revision. |

### §0.8 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_11.md` |
| Status | Proposed — Phase 7 architectural-tension revision pass |
| Predecessor | `Implementation_Plan_Control_Plane_v2_10.md` (preserved verbatim; U-CP-56 + U-CP-57 added) |
| Companion | `Spec_Control_Plane_v1_4.md` §25 C-CP-25; `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` (OPEN-RESOLVING — spec-side ABSORBED at v1.4; plan-side ABSORBED at v2.11); `.harness/c_cp_25_workflow_driver_recommendation.md` (operator-ratified 2026-05-20) |
| Authored at | Phase 7 architectural-tension resolution, 2026-05-20 (in-CLI) |
| Unit count | 60 (was 58 at v2.10; +2 at v2.11: U-CP-56 + U-CP-57) |
| Next downstream consumer | `phase-7-implementation` skill — atomic-unit consumption against U-CP-56 then U-CP-57 in topological-sort order |

---

## §2X Cluster — C-CP-25 workflow execution driver (v2.11 amendment)

**Anchor.** ADR-F3 v1.1 §Decision (iv) F3 capability-floor (iv) "workflow lifecycle event surface visible at run-event surface as distinct event classes" → CP spec v1.4 §25 C-CP-25 contract.

**Theme.** A deterministic step iteration driver materializing the missing emission site for the F3-committed workflow lifecycle event surface. Scope at v1.4 / v2.11: `SINGLE_THREADED_LINEAR` topology + `pure-pattern-no-engine` + `save-point-checkpoint` engine classes only. Drain composition with U-RT-44 `HarnessContext.drained_flag` resolves `[[fork-u-rt-44-workflow-loop-drain]]` plan-side.

---

#### U-CP-56 — Workflow execution driver core: types + `execute_workflow()` happy-path implementation

**Implements:** [C-CP-25 §25.1 (scope), §25.2 (signatures), §25.3 (iteration discipline), §25.5 (lifecycle event emission boundaries — single-threaded-linear filter over §5.1), §25.6 (replay-resumption composition with §8.2 idempotency-key join), §25.7 (failure modes 1–4: `CP-FAIL-DRIVER-TOPOLOGY-UNSUPPORTED` / `CP-FAIL-DRIVER-ENGINE-CLASS-UNSUPPORTED` / `CP-FAIL-DRIVER-STEP-FAILURE` / `CP-FAIL-DRIVER-LEDGER-APPEND-FAILURE`)]

**Depends on:** [U-CP-13 (manifest schema), U-CP-14 (per-step resolver), U-CP-10 (`WorkflowEventClass` lifecycle taxonomy declaration site), U-CP-15 (`EngineClass` enum), U-CP-01 (cap-aware router thin core), U-IS-07 (cross-axis: IS — state-ledger entry shape), U-IS-10 (cross-axis: IS — entry-shape export §10.1), U-IS-11 (cross-axis: IS — append discipline)]

**Inputs:** `WorkflowManifestEntry` (per U-CP-13 / §6.1 manifest schema); `steps: Sequence[WorkflowStep]` (in-session amendment §E — step sequence in declaration order; manifest carries config, body carries steps); `run_id : str` (harness-unique); `HarnessContext` (per U-RT-44 — but `drained_flag` poll surface is consumed at U-CP-57; U-CP-56 consumes the ledger handle + OTel tracer surfaces only).

**Cross-axis substrate consumed.** `STATE_LEDGER_ENTRY_SHAPE_EXPORT` (C-IS-10 §10.1 → U-IS-07/U-IS-10) for per-step ledger append composition; `HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT` + `JSONL_EVENT_LEDGER_FORMAT_EXPORT` (C-IS-10 §10.3, §10.5 → U-IS-08/U-IS-09/U-IS-11) for canonicalize + hash + append at the per-step ledger append site (§25.3.3.7).

**Files affected:** CP-axis workflow-driver module (logical: `workflow-driver-core`); CP-axis workflow-driver types module (logical: `workflow-driver-types`); CP-axis workflow-driver typed errors module (logical: `workflow-driver-errors`).

**Signatures:**

```text
# Types
record RunResult {
  workflow_id        : string
  run_id             : string
  status             : RunStatus
  terminal_step_index: Optional<int>
  partial_state      : Optional<TerminalState>
  final_state        : Optional<TerminalState>
  fail_class         : Optional<FailClass>
}

enum RunStatus {
  SUCCESS,
  DRAINED,
  FAILED,
  PARTIAL
}

# Typed errors
class TopologyPatternNotYetMaterializedError(HarnessControlPlaneError):
    """Raised at execute_workflow() entry when manifest_entry.topology
    is outside the v1.4 in-scope set ({SINGLE_THREADED_LINEAR})."""

class EngineClassNotYetMaterializedError(HarnessControlPlaneError):
    """Raised at execute_workflow() entry when manifest_entry.engine_class
    is outside the v1.4 in-scope set ({pure-pattern-no-engine,
    save-point-checkpoint})."""

# Step-sequence types (in-session amendment §E — per spec v1.4 §25.2 amendment)
class StepKind(StrEnum):
    DECLARATIVE_STEP   = "declarative-step"
    INFERENCE_STEP     = "inference-step"
    TOOL_STEP          = "tool-step"
    HITL_STEP          = "HITL-step"
    SUB_AGENT_DISPATCH = "sub-agent-dispatch"

class WorkflowStep(BaseModel):
    step_id: StepID
    step_kind: StepKind
    step_payload: Mapping[str, Any]  # opaque to driver; consumed by router

# Function (signature amended in-session per spec v1.4 §E)
def execute_workflow(
    manifest_entry: WorkflowManifestEntry,
    steps: Sequence[WorkflowStep],
    run_id: str,
    ctx: HarnessContext,
) -> RunResult:
    # SINGLE_THREADED_LINEAR + (pure-pattern-no-engine | save-point-checkpoint)
    # only at v2.11; out-of-scope topology / engine class raises typed error
    # at entry.
```

**Acceptance criteria:**

1. **Type surface materialized.** `RunResult` record carries the 7 fields declared at §25.2 verbatim; `RunStatus` enum carries the 4 members `{SUCCESS, DRAINED, FAILED, PARTIAL}` verbatim; `TopologyPatternNotYetMaterializedError` + `EngineClassNotYetMaterializedError` typed errors subclass a CP-axis base error class (or `HarnessControlPlaneError`-equivalent). Per `c1-orchestration-control` SKILL.md substrate authority. `TerminalState` shape deferred per §25.8 to U-CP-56 implementation choice (acceptance permits any frozen Pydantic record satisfying §25.2 signature requirements).
2. **Topology + engine-class validation at entry (§25.3.1).** Calling `execute_workflow()` with `manifest_entry.topology != SINGLE_THREADED_LINEAR` raises `TopologyPatternNotYetMaterializedError`; no `workflow.start` emitted; no ledger entry appended. Calling with `manifest_entry.engine_class ∉ {pure-pattern-no-engine, save-point-checkpoint}` raises `EngineClassNotYetMaterializedError`; same side-effect-free guarantee.
3. **`workflow.start` emission (§25.3.2).** Post-validation, driver emits `workflow.start` per `WorkflowEventClass.WORKFLOW_START` (per U-CP-10 declaration site) carrying the §5.2 minimum attribute set verbatim: `workflow.id`, `workflow.class`, `engine.class`, `manifest.entry_id`, `idempotency_key` (root). Always-sampled per §5.4. Verifiable at OTel tracer surface via `ctx.tracer`.
4. **Step iteration loop (§25.3.3, happy path — no drain).** For each step `s` in the `steps` parameter (declaration order per in-session amendment §E; SINGLE_THREADED_LINEAR has no branching): (a) call `resolve_step_binding(manifest_entry, s.id)` per U-CP-14 → `binding`; (b) **if** `binding` requires lease acquisition under §5.3 `lease.mechanism` enum, acquire lease + emit `lease.acquired` per `WorkflowEventClass.LEASE_ACQUIRED`; **else** no lease acquired and no `lease.acquired` span emitted at this step. Per CP spec v1.4 §25.5 lease row: "the driver contract states 'emit per engine-class lookup,' not a fixed assertion per engine class." Per CP spec v1.4 Adjacent finding §B (carry-forward §0.6): "no contract surface explicitly maps `engine.class` → required-lease-mechanism" at CP spec v1.4 — mechanism-to-engine-class binding rule is resolved at implementation time per `c1-orchestration-control` SKILL.md substrate authority. Acceptance permits any substrate-anchored implementation reading of the §5.3 enum → engine-class binding (e.g., `pure-pattern-no-engine` may map to no-lease per §8.2 row 3 "F2 state-ledger native — idempotency_key is the primary dedup substrate" reading; `save-point-checkpoint` likely maps to `engine_native` per §5.3 enum row 1; both substrate-anchored, neither asserted by this acceptance). (c) invoke step body through cap-aware router (`route_invocation(binding, s.payload, ctx)` per U-CP-01); (d) emit `step.boundary` per `WorkflowEventClass.STEP_BOUNDARY` carrying §5.2 minimum attribute set verbatim (`workflow.id`, `step.index`, `step.kind` ∈ §5.2's 5-value enum, `idempotency_key` per `(run_id, step.index)`); (e) release lease if held + emit `lease.released`; (f) compose state-ledger entry per C-IS-05 → C-IS-10 §10.1 export → C-IS-11 append.
5. **Lifecycle event filter (§25.5).** `workflow.start` + per-step `step.boundary` always emitted in happy path. `fallback.triggered` / `retry.attempt` / `breaker.tripped` only emitted if step body itself triggers them (propagated, not synthesized). `lease.acquired` / `lease.released` per acceptance #4. `workflow.resumption` only on re-entry per §25.6.
6. **Replay-resumption read at re-entry (§25.6) — STRUCK at U-CP-56 PARTIAL-LAND 2026-05-20.** Originally specified: under `manifest_entry.engine_class == 'save-point-checkpoint'`: at driver entry, compute `run_idempotency_key = sha256(run_id, manifest_entry.workflow_id, manifest_entry.entry_version)`; read C-IS-07 state-ledger for entries matching prefix; if matches exist, emit `workflow.resumption` carrying §5.2 minimum attribute set; skip already-replayed steps; resume at first unmaterialized step. **STRUCK pending Class 1 fork resolution** at `.harness/class_1_tension_u_cp_56_resumption_underspec.md`: (a) `WorkflowManifestEntry` (U-CP-13 landed) has no `entry_version` field; (b) no IS prefix-match read primitive landed. Weaker behavior shipped at PARTIAL-LAND: save-point-checkpoint binding emits `RESUMPTION` whenever ledger is non-genesis (no prefix match; selective per-run resumption deferred to Class 1 resolution Path A — extend U-CP-13 + add IS read primitive). Under `pure-pattern-no-engine`: no resumption-specific read at entry (state-ledger native dedup per §8.2 handles dedup at per-step `idempotency_key`) — this part LANDS at U-CP-56; per-step `idempotency_key = sha256(run_idempotency_key, step.index)`.
7. **Terminal SUCCESS return (§25.3.4 + §25.3.5).** Happy-path completion: no further `step.boundary` emission after last step; `return RunResult(workflow_id, run_id, status=SUCCESS, terminal_step_index=null, partial_state=null, final_state=<accumulated>, fail_class=null)`. No new lifecycle event class introduced at terminal exit (per §25.5).
8. **Failure-mode taxonomy (§25.7 modes 1–4).** Step body raising uncaught exception → emit `step.boundary` with failure attribute set; `return RunResult(status=FAILED, fail_class=<step-specific per c5-validation-contract SKILL.md catalog>)`; drain-flag NOT auto-set (failure ≠ drain). Ledger append failing (C-IS-11) → fail-loud; `return RunResult(status=FAILED, fail_class='ledger-append-failed')`. State-ledger fidelity is non-negotiable per ADR-F2 v1.2.
9. **Determinism.** Driver iteration order is deterministic given inputs (declarative manifest order; deterministic per-step resolver per U-CP-14 AC #4). Lifecycle event emission boundaries deterministic. State-ledger append order deterministic. Spans not interleaved across concurrent step bodies (single-threaded-linear topology).

**Tests:** `test_run_result_seven_fields`, `test_run_status_four_members`, `test_topology_pattern_not_yet_materialized_raised_at_non_single_threaded_linear`, `test_engine_class_not_yet_materialized_raised_at_out_of_scope_engine_class`, `test_workflow_start_emitted_with_minimum_attribute_set`, `test_step_iteration_declaration_order`, `test_per_step_boundary_emitted_with_idempotency_key`, `test_state_ledger_append_per_step`, `test_lease_acquired_released_emitted_when_binding_requires_lease`, `test_lease_not_emitted_when_binding_does_not_require_lease` (substrate-anchored; specific per-engine-class binding determined at implementation per §0.6 §B carry-forward), `test_workflow_resumption_emitted_on_save_point_checkpoint_reentry`, `test_no_resumption_emission_under_pure_pattern_no_engine` (per §8.2 row 3 "F2 state-ledger native — `idempotency_key` is the primary dedup substrate" — no `workflow.resumption` event class is required for chronological re-read without engine-internal state), `test_terminal_success_return_shape`, `test_step_failure_returns_failed_status`, `test_ledger_append_failure_returns_failed_status`, `test_driver_iteration_deterministic_given_inputs`.

**Rollback boundary:** Revert workflow-driver-core module + workflow-driver-types + workflow-driver-errors modules. C-CP-25 §25.1–§25.3 + §25.5–§25.7 materialization dissolves; any consuming runtime code paths revert to the pre-driver state (workflow execution un-implementable). Cross-axis edges to U-IS-07/10/11 release at the driver site.

---

#### U-CP-57 — Workflow driver drain composition: 4-site check pattern + DRAINED return

**Implements:** [C-CP-25 §25.4 (drain protocol — 4-site check pattern), §25.7 (failure mode 5 — `RT-FAIL-DRAIN-TIMEOUT` composition with `Spec_Harness_Runtime_v1.md` C-RT-14)]

**Depends on:** [U-CP-56 (driver core), U-RT-44 (cross-axis: runtime — `HarnessContext.drained_flag` ownership per `Spec_Harness_Runtime_v1.md` §11 C-RT-11)]

**Inputs:** `HarnessContext.drained_flag : asyncio.Event` (per U-RT-44 ownership); existing U-CP-56 `execute_workflow()` function (extended with drain check hooks at §25.4-declared sites).

**Cross-axis substrate consumed.** `HARNESS_CONTEXT_DRAINED_FLAG_OWNERSHIP_EXPORT` (per `Spec_Harness_Runtime_v1.md` §11 C-RT-11 → U-RT-44) — the `drained_flag` ownership at runtime axis with read-only-poll consumption authorized at the CP workflow-driver site.

**Files affected:** CP-axis workflow-driver-core module (logical: `workflow-driver-core`; extension to U-CP-56's module — drain check hooks added at iteration loop sites per §25.4 table).

**Signatures:**

```text
# No new public types or functions — drain composition extends
# execute_workflow() from U-CP-56 by adding drain check hooks at the
# 4 §25.4-declared sites. Drain check hook signature:

def _drain_check_pre_step(
    ctx: HarnessContext,
    accumulated_state: TerminalState,
    next_step_index: int,
) -> Optional[RunResult]:
    """If ctx.drained_flag.is_set(): return RunResult(status=DRAINED,
    terminal_step_index=next_step_index - 1, partial_state=accumulated_state);
    else return None (caller continues iteration).
    No step.boundary emission at this site (Path B operator decision)."""

def _drain_check_post_step(
    ctx: HarnessContext,
    accumulated_state: TerminalState,
    just_completed_step_index: int,
) -> Optional[RunResult]:
    """If ctx.drained_flag.is_set(): return RunResult(status=DRAINED,
    terminal_step_index=just_completed_step_index,
    partial_state=accumulated_state); else return None.
    State-ledger append for the just-completed step has persisted."""

def _drain_check_entry(
    ctx: HarnessContext,
    workflow_id: str,
    run_id: str,
) -> Optional[RunResult]:
    """If ctx.drained_flag.is_set() at execute_workflow() entry: return
    RunResult(workflow_id, run_id, status=DRAINED, terminal_step_index=None,
    partial_state=None); else return None.
    No workflow.start emission (drain detected before any state mutation)."""
```

**Acceptance criteria:**

1. **Driver-entry drain check (§25.4 row "Driver entry").** If `ctx.drained_flag.is_set()` at `execute_workflow()` entry (BEFORE topology + engine-class validation — operator-ratified ordering 2026-05-20 per spec v1.4 §25.4 row 1 amendment), return `RunResult(workflow_id, run_id, status=DRAINED, terminal_step_index=None, partial_state=None, final_state=None, fail_class=None)`. No `workflow.start` emitted. No state-ledger entry appended. No lifecycle event at this site. Trade-off: invalid manifests (out-of-scope topology or engine class) under drain return DRAINED rather than raising typed errors. Drain is a shutdown contract that supersedes typed-validation-error surfacing; the caller has already abandoned the workflow.
2. **Per-step pre-entry drain check (§25.4 row "Per-step pre-entry"; Path B applied).** Before entering each step `s` (U-CP-56 §25.3.3.1 site): if `ctx.drained_flag.is_set()`: do NOT emit `step.boundary` (Path B operator decision — §5.2 step.kind 5-value enum preserved verbatim); do NOT dispatch step body; return `RunResult(status=DRAINED, terminal_step_index=s.index - 1, partial_state=<accumulated>)`. Terminal observability at this site is `RunResult` return only.
3. **Per-step post-exit drain check (§25.4 row "Per-step post-exit").** After step body completes + lease released + state-ledger append (U-CP-56 §25.3.3.8 site): if `ctx.drained_flag.is_set()`: return `RunResult(status=DRAINED, terminal_step_index=s.index, partial_state=<accumulated including this step>)`. The just-completed step's ledger entry HAS persisted (per U-IS-11 append discipline). `step.boundary` for the completed step HAS been emitted.
4. **No mid-step drain interruption (§25.4 row "Mid-step").** Step bodies (LLM call, tool call, sub-routine) execute to completion (or to step body's own internal failure). Driver does not interrupt step body when `drained_flag` is set; the flag is checked only at the 3 site-boundaries above. Matches `Spec_Harness_Runtime_v1.md` §11 v1.2 settlement: "Completes the current in-flight step (no mid-step interruption)."
5. **Bounded-wait composition (§25.4 row "Bounded wait" + §25.7 mode 5).** Driver does NOT own the bounded-wait timeout — `shutdown(ctx, timeout=...)` at `Spec_Harness_Runtime_v1.md` C-RT-10 + C-RT-14 `RT-FAIL-DRAIN-TIMEOUT` owns it. If step body exceeds the wait, runtime force-shutdown proceeds; driver may not complete its post-step accounting. Driver contract is composition-only at this fail class. Acceptance: U-CP-57 implementation does NOT add a timeout primitive at the driver layer (over-extension would violate spec §25.4 row "Bounded wait" + §25.7 mode 5).
6. **`drained_flag` not auto-set by driver.** Driver never calls `ctx.drained_flag.set()` itself. The flag is owned by U-RT-44 signal handler. Failure modes 1–4 (per U-CP-56 AC #8) return FAILED status without setting `drained_flag`. Confirms `failure ≠ drain` invariant.

**Tests:** `test_drain_at_entry_returns_drained_no_workflow_start_emit`, `test_drain_pre_step_no_step_boundary_emit_path_b`, `test_drain_pre_step_returns_drained_with_prior_step_index`, `test_drain_post_step_after_ledger_append_persists`, `test_no_mid_step_drain_interruption_via_drained_flag`, `test_drain_does_not_emit_terminal_lifecycle_event`, `test_drained_flag_not_set_by_driver`, `test_drained_flag_not_set_on_step_failure`, `test_driver_does_not_own_bounded_wait_timeout`.

**Rollback boundary:** Revert drain check hooks at workflow-driver-core. C-CP-25 §25.4 + §25.7 mode 5 composition dissolves; driver becomes drain-unaware. U-RT-44 AC #2 (in-flight step bounded-wait) re-becomes unmaterializable; U-RT-49 workflow-execution ACs re-strike. Cross-axis edge to U-RT-44 releases.

---

## §[traceability]

[Preserved verbatim from v2.10 (which preserved verbatim from v2.9) except two new column entries added at v2.11: C-CP-25 column added with cell marks at U-CP-56 (§25.1, §25.2, §25.3, §25.5, §25.6, §25.7 modes 1–4) + U-CP-57 (§25.4, §25.7 mode 5); R-CP-04 row gains cell marks at U-CP-56 (driver materialization site) + U-CP-57 (drain composition); R-CP-07 row gains cell mark at U-CP-56 (replay-resumption read at re-entry).]

---

## §[carry-forwards]

[Preserved verbatim from v2.10. v2.11 adds three carry-forward findings inherited from CP spec v1.4 Change-note (Adjacent findings §B / §C / §D), recorded at §0.6 above — no separate [CF-N] entry needed (the spec change-note + this §0.6 are the carry-forward record).]

---

## §[coherence pass]

[Audits preserved verbatim from v2.10. v2.11 coherence pass per `implementation-planner` SKILL §5 step 9:

- **Atomicity (§3).** U-CP-56 and U-CP-57 each satisfy the 4 operational criteria: single coherent change (driver core for U-CP-56; drain hooks for U-CP-57); single focused session (each is ~half-day to one-session effort); independently testable (U-CP-56 testable with `drained_flag` never set; U-CP-57 testable by setting `drained_flag` at various sites); coherent rollback boundary (each unit's modules revert as one commit).
- **Spec-traceability (§4.2).** Every U-CP-56 AC cites a §25.N sub-section (ACs 1–9 trace to §25.1 / §25.2 / §25.3 / §25.5 / §25.6 / §25.7 modes 1–4). Every U-CP-57 AC cites §25.4 or §25.7 mode 5. Coverage matrix at §0.5 confirms C-CP-25 fully covered.
- **Dependency-awareness (§4.3).** U-CP-56 declares 8 dependencies (5 within-CP + 3 cross-axis IS). U-CP-57 declares 2 dependencies (1 within-CP + 1 cross-axis runtime). Aggregate v2.11 DAG: acyclic (both new units are sink leaves; no new edge points back into v2.10's 58 units).
- **Implementation-grade-detail (§4.4).** U-CP-56 + U-CP-57 each name affected module(s) at logical level, declare signatures at type + function level, declare testable acceptance criteria. No spec extension (verified at U-CP-56 AC #1 — typed-error names per spec §25.7 verbatim; AC #4 honors §0.6 §B carry-forward without inventing per-engine-class binding; U-CP-57 ACs honor Path B at acceptance #2 without enum extension).
- **Findings.** None blocking. Three carry-forwards inherited from CP spec v1.4 Change-note recorded at §0.6 + acceptance criteria where applicable.]

---

*Filed at Phase 7 architectural-tension revision pass per `implementation-planner` SKILL.md §8 revision-pass-mode discipline. Two new atomic units (U-CP-56 + U-CP-57) absorb the C-CP-25 `WorkflowDriver` contract from CP spec v1.4 §25. Unit count 58 → 60. Predecessor v2.10 (58 units) preserved verbatim. Dependency graph: 6 new edges added; acyclic invariant preserved. Coverage matrix: C-CP-25 fully covered. Next downstream consumer: `phase-7-implementation` skill — atomic-unit consumption against U-CP-56 then U-CP-57 in topological-sort order. At C-CP-25 land, `harness-runtime/` refactor delegates drain to driver per `Spec_Harness_Runtime_v1.md` §11 risk-surface guidance; un-strike U-RT-44 AC #2 + U-RT-49 workflow-execution ACs; mark `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` CLOSED.*
