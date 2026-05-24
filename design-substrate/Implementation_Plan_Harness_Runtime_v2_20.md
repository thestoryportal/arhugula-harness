# Implementation Plan — Harness Runtime v2.20

## Change-note (v2.19 → v2.20)

**Scope of revision.** Spec-revision-driven plan revision absorbing runtime spec **v1.20 → v1.21** §14.14 C-RT-24 NEW contract per CP composer authoring arc (operator-ratified narrow-scope AskUserQuestion 2026-05-24; spec v1.21 committed at `8adb2df` in this worktree). NEW cluster **L9-undecies** appended at §1 below, containing exactly 3 atomic units: **U-RT-87** (`RuntimeConfig.pause_resume_protocol_config` field landing + `PauseResumeProtocolConfig` empty-marker sub-model + `HarnessContext.pause_resume_protocol` field + `HarnessContext.pause_requested_flag` sibling caller-signal field), **U-RT-88** (`materialize_pause_resume_protocol_stage` factory + stage-5 LOOP_INIT wiring + `pause_context_reader` composition + `RT-FAIL-PAUSE-RESUME-STAGE-MATERIALIZE` fail-class landing), **U-RT-89** (workflow_driver per-step pre-entry pause-trigger detection + protocol invocation + `RunStatus.PAUSED` enum extension + resume-on-snapshot-context entry-point branch + real-bootstrap e2e pause/resume cycle). The cluster operationalizes the binding-chain seam authored at spec §14.14 — the missing runtime materialization contract whose absence at HEAD is the empirical finding behind `harness-cp/CLAUDE.md` §4.1 H_T-CP-22 PARTIAL gate ("no workflow_driver invocation of capture_pause_snapshot/attempt_resume per hitl_placement.py:18-23 deferral").

**Source of fix.** Operator-ratified narrow-scope CP composer authoring arc per AskUserQuestion 2026-05-24 ("driver-invocation-only" scope; audit-write side authored at last session's narrow-scope landing at `7988335` consumes engine-layer §22.1 helpers — workflow-layer audit-write is a separate follow-on arc out of v1.21 scope). H_T-CP-22 PARTIAL → RETIRE-READY (structural materialization) → RETIRED (e2e exercise) joint advance gates on this plan landing + impl arc + e2e per `[[verification-shape-sharpened-grep-vs-e2e]]` discipline.

**Plan shape preserved.** v2.19's delta + v2.18 delta + v2.17 substantive body all preserved verbatim — L9-decies cluster (U-RT-83/84/85) intact, L9-novies cluster (U-RT-86) intact, L9-octies cluster (U-RT-76..U-RT-82) intact, L9-septies cluster (U-RT-71..U-RT-75) intact, all prior unit bodies intact. NEW **L9-undecies** cluster appended at §1 below containing 3 atomic units (U-RT-87 + U-RT-88 + U-RT-89). NO existing unit body change; NO AC change at any pre-v2.20 unit; NO DAG topology change at L9-decies / L9-novies / L9-octies / L9-septies / earlier internal structure; ONLY a new cluster appended with within-cluster linear-chain DAG (U-RT-87 → U-RT-88 → U-RT-89) plus cluster-boundary edges to already-landed CP-axis carriers (CP spec v1.13 §26 carriers at U-CP-62/63/64/65 closure commits) + already-landed bootstrap stage-1 IS substrate.

**Cluster naming.** "L9-undecies" follows the existing -ies enumeration (septies/octies/novies/decies/**undecies** = 7th/8th/9th/10th/11th). Next available -ies-suffix per the v2.12+ runtime-plan-cluster convention.

**Cluster ordering.** L9-undecies opens with U-RT-87 as L0-within-cluster (foundational field + sub-model authoring; no within-cluster predecessors); U-RT-88 at L1-within-cluster (depends on U-RT-87 within-cluster + CP-axis cluster-boundary deps + stage-1 IS cluster-boundary deps); U-RT-89 at L2-within-cluster (depends on U-RT-88 within-cluster — workflow_driver invocation + e2e exercises the wired factory output). Cluster-boundary edges declared explicitly per §7 dependency discipline (CP spec v1.13 §26 carriers at U-CP-62/63/64/65 closure commits; bootstrap stage-1 IS-bucket carriers from pre-cluster-7 L0 foundational units). NO edges from any pre-v2.20 unit into L9-undecies (L9-undecies is structurally terminal at v2.20 — produces the pause/resume-protocol binding chain; no downstream unit at this plan revision consumes its output beyond U-RT-89's own e2e exercise).

**Operator-discretion test-infrastructure shape (FM-2).** U-RT-89 implementer selects e2e test fixture mechanism per FM-2 no-extension discipline (mirrors U-RT-85 §"Test-substrate mechanism" + U-RT-86 + U-RT-82 enumeration patterns). Options:
- **α** — Operator supplies a `PauseResumeProtocolConfig.default()` opt-in instance. Test fixture constructs a workflow with N steps; in a parallel asyncio task sets `ctx.pause_requested_flag` before step K; asserts driver returns `RunStatus.PAUSED` with `pause_snapshot` populated at step K-1; then re-invokes `execute_workflow` with the captured snapshot; asserts driver resumes cleanly (RunStatus.SUCCESS with all N-K steps executed post-resume). Recommended default.
- **β** — Mechanism α + an additional resume-with-material-diff test exercising the `ResumeResult.fail_class = CP-FAIL-RESUME-MATERIAL-DIFF-DETECTED` path (mutate `ctx.ledger_writer` between pause and resume to invalidate `state_ledger_anchor`). Two test functions; broader coverage of the §26.6 invariant 4 STRICT-policy resume-abort branch.
- **γ** — Gate on operator-supplied env var (`PAUSE_RESUME_E2E_FIXTURE_PATH`) pointing at a fixture module; test loads + exercises. Mirrors U-RT-86 mechanism-γ pattern for CI-skipping when fixture unavailable.

Recommended default per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` verification: **mechanism α** (in-process fixture, single clean-resume cycle) — sufficient for U-RT-89's AC #5 verification-shape (binding chain succeeds end-to-end against a real `PauseResumeProtocol` instance through real workflow_driver execution, not via test-locals); broader diff-detection coverage deferred to follow-on retirement-batch arc.

**Adjacent observations (NOT this plan's authoring scope).**

(a) **Spec v1.21 §14.14.7 deferrals.** Reading A explicitly disclaims the broader scope (HITL-gate-composer integration as pause-trigger source, `pause_context_reader` composition body discretion, pause-trigger reason source discretion, resume-policy source discretion, `pause_requested_flag` caller-surface contract discretion, snapshot persistence mechanism discretion). These remain deferred to follow-on arcs. L9-undecies cluster does NOT touch any §14.14.7 deferral beyond the implementer-discretion choices enumerated at the per-unit ACs.

(b) **`PauseResumeProtocolConfig` empty-marker shape preserved at U-RT-87.** Per spec §14.14.1 + change-note adjacent observation (a): the empty-marker dataclass is intentional at Reading A scope (operator-supply mechanism deferred to follow-on arc). U-RT-87 lands the empty-marker shape; future plan revisions may extend the sub-model when operator-supply semantics materialize. **U-RT-87 ACs explicitly enforce empty-marker shape**: no fields beyond `.default()` factory.

(c) **Factory body construction discretion at U-RT-88.** Per spec §14.14.1 (factory signature + opt-out branch is full-spec; opt-in branch construction body is fully specified — construct `PauseResumeProtocol(state_ledger_writer, state_ledger_reader, pause_context_reader)` from already-bound `ctx.ledger_writer` + `ctx.ledger_reader` + composed `pause_context_reader`). U-RT-88 lands the full factory body (no `NotImplementedError` opt-in branch); the construction body is straightforward Pydantic-v2-style instantiation of the existing `PauseResumeProtocol` class.

(d) **Carrier-home decision: `PauseResumeProtocolConfig` lives in `harness-runtime`** at U-RT-87. Parallel to `ValidatorFrameworkConfig` at `harness-runtime` per spec v1.21 §14.14 + `MemoryToolBackendConfig` at `harness-runtime` per spec v1.17 §14.12 (RuntimeConfig sub-models that pair with stage factories at runtime spec contracts live in `harness-runtime`). `harness-core` carries cross-axis-shared types; `PauseResumeProtocolConfig` is consumed ONLY by the runtime-spec factory at v1.21 (the actual `PauseResumeProtocol` class surface remains at CP spec v1.13 §26).

(e) **`RunStatus.PAUSED` enum extension at U-RT-89.** The existing `RunStatus` enum at `harness-cp/src/harness_cp/workflow_driver_types.py` enumerates `SUCCESS` + `DRAINED` + `FAILED` per current canonical reading. U-RT-89 lands a NEW `PAUSED` value via additive enum extension. Per spec v1.21 §14.14.5 invariant 4 the RunResult shape adds an optional `pause_snapshot: PauseSnapshot | None` field; both changes are additive minor-version evolution per the existing C-RT-09 §9 Version evolution clause. No existing caller breaks (the new value is only returned when both `ctx.pause_resume_protocol is not None` AND `ctx.pause_requested_flag.is_set()`, neither of which are default at HEAD pre-v2.20).

**Downstream absorption owed (post-v2.20).**

(a) Workspace `CLAUDE.md` §2.4 runtime row version bump (v2.19 → v2.20); co-published at L9-undecies cluster open arc OR batch-18 retirement-event arc (whichever fires first). Unit count 87 → 90 (+3 units).

(b) Phase 7 cluster-open authorization for L9-undecies at follow-on session per `phase-7-implementation` skill discipline. Cluster sequencing: L9-undecies opens with U-RT-87 as the L0 entry-point; topological sort U-RT-87 → U-RT-88 → U-RT-89.

(c) Batch-18 retirement-event filing per `phase-7-substitution-retirement` skill at L9-undecies cluster close: H_T-CP-22 PARTIAL → RETIRE-READY (post-U-RT-88 stage-factory landing + U-RT-89 workflow_driver invocation per spec §14.14.6) → RETIRED (post-U-RT-89 e2e exercise per batch-14 §6(a) close pattern + batch-16 §6 verification-shape sharpening).

(d) `Cross_Axis_Composition_Document_v2_9.md` unchanged at v2.20 — spec §14.14.6 cross-axis cascade enumeration confirms ZERO cross-axis cascade. The `pause_resume_protocol` ctx-binding consumes already-landed CP spec v1.13 §26 `PauseResumeProtocol` carrier without new CXA edge introduction.

(e) CP spec v1.13 + OD spec v1.11 unchanged at v2.20. The CP-axis `PauseResumeProtocol` class surface is canonical at CP spec v1.13 §26; the runtime spec v1.21 §14.14 consumes it without amendment. The OD-axis `pause.*` + `resume.*` span schema is canonical at OD spec v1.11 §C-OD-30.1; the OD-side audit-write helpers landed at `7988335` consume engine-layer §22.1 carriers (`PauseEvent` / `ResumeAttempt` / `ResumeOutcome`) — workflow-layer audit-write is a separate follow-on arc out of v1.21 scope (workflow_driver invocation of helpers is implementer-discretion per OD spec v1.11 §C-OD-30.4.5 — v2.20 explicitly does NOT wire the workflow-layer audit-write path).

---

## §1 — L9-undecies cluster (NEW at v2.20)

### U-RT-87 — `RuntimeConfig.pause_resume_protocol_config` field + `PauseResumeProtocolConfig` empty-marker sub-model + `HarnessContext.pause_resume_protocol` field + `HarnessContext.pause_requested_flag` sibling field

- **Implements:** Runtime spec **v1.21** §3 C-RT-02 RuntimeConfig table NEW row (`pause_resume_protocol_config: PauseResumeProtocolConfig | None = None`) + **v1.21** §14.14.1 `PauseResumeProtocolConfig` empty-marker `@dataclass(frozen=True)` sub-model + `.default()` factory classmethod per the ValidatorFrameworkConfig-precedent shape applied at the runtime-package carrier-home per change-note adjacent observation (d) + **v1.21** §4 C-RT-04 HarnessContext table NEW row (`pause_resume_protocol: PauseResumeProtocol | None`) + **v1.21** §4 C-RT-04 HarnessContext table NEW row (`pause_requested_flag: asyncio.Event` sibling-pattern to existing `drained_flag`). NO field beyond the `.default()` factory at v1.21 Reading A scope.

- **Files:**
  - `harness-runtime/src/harness_runtime/types.py` — (i) append NEW field `pause_resume_protocol_config: PauseResumeProtocolConfig | None = None` to the existing `RuntimeConfig` Pydantic v2 BaseModel at the established field-ordering pattern (after `validator_framework_config`); (ii) append NEW field `pause_resume_protocol: PauseResumeProtocol | None = None` to the existing `HarnessContext` Pydantic v2 BaseModel at the established field-ordering pattern (after `validator_framework`); (iii) append NEW field `pause_requested_flag: asyncio.Event` to the existing `HarnessContext` Pydantic v2 BaseModel at the established field-ordering pattern (sibling to existing `drained_flag` at line ~1122); import `PauseResumeProtocol` from `harness_cp.pause_resume_protocol` at the runtime-types module-import boundary.
  - `harness-runtime/src/harness_runtime/lifecycle/pause_resume_protocol_types.py` (NEW) — author `PauseResumeProtocolConfig` empty-marker `@dataclass(frozen=True)` with `.default()` factory classmethod; module exports `PauseResumeProtocolConfig`. Parallel to `harness-runtime/src/harness_runtime/lifecycle/memory_tool_types.py` + `lifecycle/validator_framework_types.py` module-organization pattern for runtime-internal sub-models per spec §14.12 + §14.13 precedent.

- **Signatures:**
  - `RuntimeConfig.pause_resume_protocol_config: PauseResumeProtocolConfig | None = None` — appended to existing frozen Pydantic v2 BaseModel; default `None`.
  - `HarnessContext.pause_resume_protocol: PauseResumeProtocol | None = None` — appended to existing frozen Pydantic v2 BaseModel; default `None`.
  - `HarnessContext.pause_requested_flag: asyncio.Event` — appended to existing frozen Pydantic v2 BaseModel; no default (initialized at stage 0 PREAMBLE via `_MutableHarnessContext` builder per existing `drained_flag` precedent).
  - `@dataclass(frozen=True)` `PauseResumeProtocolConfig` with NO fields; `@classmethod def default(cls) -> PauseResumeProtocolConfig: return cls()` factory.

- **Depends on:** (within-cluster) (none); (cluster-boundary, CP-axis) [U-CP-62 — `PauseResumeProtocolConfig` carriers + `PauseResumeProtocol` class landing at cluster 10-CP-B `49617e7` per `harness-cp/src/harness_cp/pause_resume_protocol.py:213+`]; (cluster-boundary, runtime-axis) (none — `HarnessContext` builder + `drained_flag` field already at HEAD pre-v2.20).

- **ACs:**
  1. **`RuntimeConfig.pause_resume_protocol_config` field appended** at the established field-ordering position (after `validator_framework_config`); type annotation `PauseResumeProtocolConfig | None`; default `None`; frozen-model invariant preserved per existing C-RT-02 §3 invariants.
  2. **`HarnessContext.pause_resume_protocol` field appended** at the established field-ordering position (after `validator_framework`); type annotation `PauseResumeProtocol | None`; default `None`; frozen-model invariant preserved per existing C-RT-04 §4 invariants.
  3. **`HarnessContext.pause_requested_flag` field appended** at the established field-ordering position (sibling to existing `drained_flag`); type annotation `asyncio.Event`; no default at field declaration (initialized at `_MutableHarnessContext` builder during stage 0 PREAMBLE per existing `drained_flag` precedent); frozen-model invariant preserved.
  4. **`PauseResumeProtocolConfig` empty-marker authored** as `@dataclass(frozen=True)` with NO fields; `.default()` classmethod returns `cls()` empty instance.
  5. **Module organization parallel to §14.13 precedent**: `PauseResumeProtocolConfig` lives in `harness-runtime/src/harness_runtime/lifecycle/pause_resume_protocol_types.py` (or equivalent runtime-package-internal module organization at implementer discretion); not in `harness-core` (per change-note adjacent observation (d) carrier-home decision).
  6. **`RuntimeConfig(pause_resume_protocol_config=None)` constructs successfully** + `RuntimeConfig(pause_resume_protocol_config=PauseResumeProtocolConfig.default())` constructs successfully. Both shapes pass Pydantic v2 frozen-model validation.
  7. **Spec v1.21 §3 C-RT-02 RuntimeConfig table NEW row verbatim** + **§4 C-RT-04 HarnessContext table NEW rows verbatim**: field name, type, default, semantic prose all match the spec table rows at the field-table layer (citation byte-exact per `Project_Workflow_v1_8.md` §7.4.2).
  8. **Importable; pyright strict mode passes.** `from harness_runtime.types import RuntimeConfig, HarnessContext` + `from harness_runtime.lifecycle.pause_resume_protocol_types import PauseResumeProtocolConfig` (or implementer-selected module path) all resolve without error.

### U-RT-88 — `materialize_pause_resume_protocol_stage` factory + stage-5 LOOP_INIT wiring + `pause_context_reader` composition + `RT-FAIL-PAUSE-RESUME-STAGE-MATERIALIZE` fail class

- **Implements:** Runtime spec **v1.21** §14.14.1 factory signature (`async def materialize_pause_resume_protocol_stage(config: RuntimeConfig, ctx, *, pause_context_reader: PauseContextReader) → PauseResumeProtocol | None`) + **v1.21** §14.14.2 per-factory invocation discipline (5 invariants) + **v1.21** §14.14.3 stage-5 LOOP_INIT wiring (factory runs at stage 5 after stage-1 IS prerequisites populated per the §14.14.3 ordering) + **v1.21** §14.14.4 NEW fail class `RT-FAIL-PAUSE-RESUME-STAGE-MATERIALIZE` landing + **v1.21** §14.14.5 invariants (5).

- **Files:**
  - `harness-runtime/src/harness_runtime/bootstrap/factories/pause_resume_protocol_factory.py` (NEW) — author `materialize_pause_resume_protocol_stage(config, ctx, *, pause_context_reader) → PauseResumeProtocol | None` factory per spec §14.14.1 signature. Module parallels existing `harness-runtime/src/harness_runtime/bootstrap/factories/memory_tool_registry_factory.py` + `runtime_tool_dispatcher_factory.py` module-organization patterns.
  - `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py` — append factory invocation at the established stage-5 ordering pin (after stage-1 IS prerequisites are populated per spec §14.14.3); compose `pause_context_reader` callable closing over `ctx.ledger_reader` + a current-state-summary provider (impl-discretion at the factory invocation site per spec §14.14.2 invariant 4); bind factory output to `ctx.pause_resume_protocol`.
  - `harness-runtime/src/harness_runtime/fail_classes.py` (or equivalent existing fail-class enum module) — append `RT-FAIL-PAUSE-RESUME-STAGE-MATERIALIZE` enum member per spec §14.14.4 + runtime-local fail-class taxonomy convention.

- **Signatures:**
  - `async def materialize_pause_resume_protocol_stage(config: RuntimeConfig, ctx: _MutableHarnessContext, *, pause_context_reader: PauseContextReader) -> PauseResumeProtocol | None`
  - Factory body per spec §14.14.1: `if config.pause_resume_protocol_config is None: return None` (empty-sentinel branch — returns the no-pause-protocol state); else verify `ctx.ledger_writer` + `ctx.ledger_reader` non-None (raise `PauseResumeStageMaterializeError` otherwise per spec §14.14.4) + construct `PauseResumeProtocol(state_ledger_writer=ctx.ledger_writer, state_ledger_reader=ctx.ledger_reader, pause_context_reader=pause_context_reader)` + return.
  - `PauseContextReader = Callable[[], tuple[StateSummary, str]]` — type alias per spec §14.14.1 callable docstring; provider returning (current state_summary, current state_ledger_anchor entry_hash).
  - `RT-FAIL-PAUSE-RESUME-STAGE-MATERIALIZE` — new fail-class enum member at the runtime-local fail-class taxonomy.

- **Depends on:** (within-cluster) [U-RT-87 — RuntimeConfig field + HarnessContext fields + PauseResumeProtocolConfig empty-marker]; (cluster-boundary, CP-axis) [U-CP-62 — `PauseResumeProtocol` class + `PauseContextReader` type alias at cluster 10-CP-B `49617e7` per `harness-cp/src/harness_cp/pause_resume_protocol.py:213+`; U-CP-63 — `capture_pause_snapshot` async method at `49617e7`; U-CP-64 — `attempt_resume` async method at `49617e7`]; (cluster-boundary, runtime-axis) bootstrap stage-1 IS-bucket carriers (`ctx.ledger_writer` + `ctx.ledger_reader` — pre-cluster-7 L0 foundational units, all already at HEAD).

- **ACs:**
  1. **`materialize_pause_resume_protocol_stage(config, ctx, *, pause_context_reader) → PauseResumeProtocol | None` factory authored** at `harness-runtime/src/harness_runtime/bootstrap/factories/pause_resume_protocol_factory.py` (or implementer-selected module path); signature matches spec §14.14.1 verbatim; async; returns `PauseResumeProtocol | None` (CP spec v1.13 §26 class surface from `harness_cp.pause_resume_protocol`).
  2. **Opt-out branch: `config.pause_resume_protocol_config is None` → factory returns `None`** unconditionally; no exception raised. The production-default state (operator has not opted in) yields `ctx.pause_resume_protocol is None`; the workflow_driver per-step pre-entry pause-trigger detection at U-RT-89 evaluates False (no-pause-protocol-bound branch); backward-compatible behavior preserved per spec §14.14.5 invariant 2.
  3. **Opt-in branch: `config.pause_resume_protocol_config is not None` → factory verifies prerequisites + constructs `PauseResumeProtocol` instance.** Verifies `ctx.ledger_writer` + `ctx.ledger_reader` non-None; raises `RT-FAIL-PAUSE-RESUME-STAGE-MATERIALIZE` on absence per spec §14.14.4. Constructs `PauseResumeProtocol(state_ledger_writer=ctx.ledger_writer, state_ledger_reader=ctx.ledger_reader, pause_context_reader=pause_context_reader)` per CP spec v1.13 §26.3 constructor-ref discipline; returns the constructed instance.
  4. **Stage-5 LOOP_INIT wiring** at `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py`: factory invocation runs after stage-1 IS prerequisites populated (no specific ordering pin within stage 5 per spec §14.14.3 — implementation discretion); `pause_context_reader` composed at the factory invocation site as a closure over `ctx.ledger_reader` + a workflow-driver-supplied current-state-summary provider (per spec §14.14.2 invariant 4 implementer-discretion); factory output bound to `ctx.pause_resume_protocol`.
  5. **`pause_context_reader` composition body**: implementer selects between (i) closure-over-ctx, (ii) partial-application of a module-level helper, or (iii) class-bound-method on a stage-5 helper class per spec §14.14.7 deferred-discretion. The composition body must return `tuple[StateSummary, str]` where the str is the current state_ledger_anchor entry_hash read from `ctx.ledger_reader`. MVP shape may return a placeholder StateSummary (empty Pattern-D inheritance) if no current-state-summary provider is available at v2.20 scope; this is the simplest opt-out-when-no-workflow-active path.
  6. **`RT-FAIL-PAUSE-RESUME-STAGE-MATERIALIZE` fail-class enum member appended** at the runtime-local fail-class taxonomy module per spec §14.14.4; permanent severity; bootstrap-rollback semantics per C-RT-02 (mirrors `RT-FAIL-VALIDATOR-STAGE-MATERIALIZE` v1.18 §14.13.4 precedent).
  7. **Spec §14.14.5 invariants verified**:
     - Invariant 1 (single instance per bootstrap): factory invoked exactly once at stage 5; `ctx.pause_resume_protocol` bound exactly once.
     - Invariant 2 (empty-sentinel preserves backward compat): existing test suite (pre-v2.20 broader test coverage) passes without amendment because the default `RuntimeConfig.pause_resume_protocol_config = None` yields the no-pause-protocol state observed at HEAD pre-v2.20.
     - Invariant 3 (CP-canonical class satisfaction): when factory returns non-`None`, the instance is the CP-canonical `harness_cp.pause_resume_protocol.PauseResumeProtocol` class body (not a substitute).
     - Invariant 5 (resume-on-snapshot determinism): coexistence with U-CP-56 prefix-replay-based resumption preserved (the two paths are mutually exclusive at `execute_workflow` invocation; verified at U-RT-89 driver-level integration).
  8. **Importable; pyright strict mode passes.** `from harness_runtime.bootstrap.factories.pause_resume_protocol_factory import materialize_pause_resume_protocol_stage` resolves; integration test exercising opt-out branch passes.

### U-RT-89 — workflow_driver per-step pre-entry pause-trigger detection + protocol invocation + `RunStatus.PAUSED` + resume-on-snapshot-context entry-point branch + e2e

- **Implements:** Runtime spec **v1.21** §14.14.3 workflow_driver per-step pre-entry detection point + entry-point resume detection + **v1.21** §14.14.5 invariant 4 (additive `RunResult.pause_snapshot: PauseSnapshot | None` field) + **v1.21** §14.14.6 X-AL-2 retirement implication path (operational-criterion-B exercise for H_T-CP-22 RETIRE-READY → RETIRED transition) + Meta-Arch **v1.5** §7.7 X-AL-2 retirement criterion (full RETIRED transition prerequisites for H_T-CP-22 operator-opt-in pattern per the v1.21 §14.14 narrow-scope arc) + **batch-14 §6(a)** close pattern catalogue + **batch-16 §6** verification-shape sharpening discipline ("grep-for-presence ≠ verified-working-end-to-end" — driver invocation must succeed end-to-end against a real substrate).

- **Files:**
  - `harness-cp/src/harness_cp/workflow_driver_types.py` — extend existing `RunStatus` enum with NEW `PAUSED` value (additive minor-version evolution per existing C-CP-25 §25 conventions); extend existing `RunResult` Pydantic v2 BaseModel with NEW optional field `pause_snapshot: PauseSnapshot | None = None` (additive minor-version evolution per spec §14.14.5 invariant 4); import `PauseSnapshot` from `harness_cp.pause_resume_protocol_types` at the workflow_driver_types module-import boundary.
  - `harness-cp/src/harness_cp/workflow_driver.py` — (i) at per-step pre-entry (existing `drained_flag.is_set()` check site at line 549 region): add NEW sibling check `if ctx.pause_resume_protocol is not None and ctx.pause_requested_flag.is_set():` that invokes `await ctx.pause_resume_protocol.capture_pause_snapshot(workflow_id, run_id, step_index, pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR)` + returns `RunResult` with `status=RunStatus.PAUSED` + `pause_snapshot=<captured>`; (ii) at `execute_workflow` entry point (after envelope open, before drain check): add NEW pre-loop branch detecting `pause_snapshot_input is not None and ctx.pause_resume_protocol is not None` → invoke `await ctx.pause_resume_protocol.attempt_resume(pause_snapshot_input, material_diff_policy=MaterialDiffPolicy.STRICT)` + branch on `ResumeResult.resumed`: if False, return `RunResult(status=FAILED, fail_class=resume_result.fail_class)`; if True, set `resume_at_step_index = pause_snapshot_input.step_index` + continue loop from there.
  - `harness-cp/src/harness_cp/workflow_driver.py` — extend `execute_workflow` signature with NEW optional `pause_snapshot_input: PauseSnapshot | None = None` kwarg (additive minor-version evolution; existing callers not breaking).
  - `harness-runtime/tests/integration/test_u_rt_89_pause_resume_e2e.py` (NEW — e2e integration test module). Parallel module-organization pattern to `harness-runtime/tests/integration/test_u_rt_85_validator_framework_e2e.py` + `test_u_rt_86_mcp_client_external_server_e2e.py`.

- **Signatures:**
  - `RunStatus.PAUSED = "paused"` — NEW enum value appended.
  - `RunResult.pause_snapshot: PauseSnapshot | None = None` — NEW optional field appended.
  - `execute_workflow(..., pause_snapshot_input: PauseSnapshot | None = None)` — NEW optional kwarg appended.
  - `async def test_pause_resume_e2e_clean_cycle()` — full bootstrap with `RuntimeConfig(deployment_surface=LOCAL_DEV, ..., pause_resume_protocol_config=PauseResumeProtocolConfig.default())`; constructs a workflow with N steps; in a parallel asyncio task `await asyncio.sleep(short_delay); ctx.pause_requested_flag.set()` before step K completes; asserts `result.status == RunStatus.PAUSED + result.pause_snapshot is not None + result.terminal_step_index == K-1`; re-invokes `execute_workflow(..., pause_snapshot_input=result.pause_snapshot)`; asserts `result_resumed.status == RunStatus.SUCCESS` + `len(result_resumed.final_state) == N` (all steps observed at terminal).
  - `async def test_pause_resume_e2e_opt_out_branch()` — separate test verifying the opt-out shape: `RuntimeConfig(..., pause_resume_protocol_config=None)` yields `ctx.pause_resume_protocol is None`; setting `ctx.pause_requested_flag` is silently no-op (workflow proceeds normally); backward-compatible behavior preserved per spec §14.14.5 invariant 2.
  - Test gating: both tests marked `@pytest.mark.e2e`; no `@pytest.mark.skipif(...)` at mechanism-α selection (no external dependencies); explicit pytest fixture for `_MutableHarnessContext` lifecycle.

- **Depends on:** (within-cluster) [U-RT-87 — RuntimeConfig + HarnessContext field landings; U-RT-88 — factory + stage-5 wiring]; (cluster-boundary, CP-axis) [U-CP-62 — `PauseResumeProtocol` class + `PauseSnapshot` + `ResumeResult` + `WorkflowPauseReason` + `MaterialDiffPolicy` at cluster 10-CP-B `49617e7`; U-CP-63 — `capture_pause_snapshot` async method at `49617e7`; U-CP-64 — `attempt_resume` async method at `49617e7`; U-CP-65 — `pause.captured` + `resume.attempted` span emission helpers at `49617e7`]; (cluster-boundary, runtime-axis) bootstrap stage-7 INGRESS_ACCEPT carriers + workflow-execution entry point at `harness_runtime.api.run(...)` (pre-cluster-7 L0 foundational units, all already at HEAD).

- **ACs:**
  1. **`RunStatus.PAUSED` enum value appended** at `harness-cp/src/harness_cp/workflow_driver_types.py`; existing values preserved verbatim; additive minor-version evolution.
  2. **`RunResult.pause_snapshot: PauseSnapshot | None = None` optional field appended** at `harness-cp/src/harness_cp/workflow_driver_types.py`; existing fields preserved verbatim; field is `None` for all non-PAUSED returns per spec §14.14.5 invariant 4; additive minor-version evolution.
  3. **`execute_workflow(..., pause_snapshot_input: PauseSnapshot | None = None)` signature extension**: existing callers unbroken; new kwarg defaults `None`.
  4. **Per-step pre-entry pause-trigger detection** at `harness-cp/src/harness_cp/workflow_driver.py` (existing `drained_flag.is_set()` check site at line ~549): NEW sibling check `if ctx.pause_resume_protocol is not None and ctx.pause_requested_flag.is_set():` fires; invokes `await ctx.pause_resume_protocol.capture_pause_snapshot(workflow_id, run_id, step_index, pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR)`; returns `RunResult(status=RunStatus.PAUSED, terminal_step_index=step_index-1 if step_index > 0 else None, partial_state=dict(accumulated), pause_snapshot=<captured>)`.
  5. **Entry-point resume detection** at `harness-cp/src/harness_cp/workflow_driver.py` (post-envelope-open, pre-loop): NEW branch `if pause_snapshot_input is not None and ctx.pause_resume_protocol is not None:` fires; invokes `await ctx.pause_resume_protocol.attempt_resume(pause_snapshot_input, material_diff_policy=MaterialDiffPolicy.STRICT)`; if `resume_result.resumed is False`: returns `RunResult(status=RunStatus.FAILED, terminal_step_index=pause_snapshot_input.step_index, fail_class=resume_result.fail_class)`; if `resume_result.resumed is True`: sets `resume_at_step_index = pause_snapshot_input.step_index` + continues loop from there (replacing the existing `_determine_resume_at` prefix-replay path when `pause_snapshot_input is not None` per spec §14.14.5 invariant 5 mutual-exclusivity).
  6. **E2E test: clean pause-resume cycle**: bootstrap via `harness_runtime.api.run(...)` (or equivalent production bootstrap entry point — NOT `_FakeCtx`); construct workflow with N steps; in parallel task set `ctx.pause_requested_flag` before step K; assert `RunStatus.PAUSED` + `pause_snapshot` populated + `terminal_step_index == K-1`; re-invoke with `pause_snapshot_input=<captured>`; assert `RunStatus.SUCCESS` + all N steps observed at terminal state.
  7. **E2E test: opt-out branch**: `RuntimeConfig(pause_resume_protocol_config=None)` yields `ctx.pause_resume_protocol is None`; setting `ctx.pause_requested_flag` is silently no-op; workflow proceeds to `RunStatus.SUCCESS` normally; backward-compatible behavior preserved per spec §14.14.5 invariant 2.
  8. **Composer-depth parity with U-RT-82 + U-RT-85 + U-RT-86 close-pattern shape**: the test constructs `HarnessContext` via the **real** `harness_runtime.api.run(...)` (or equivalent production bootstrap entry point), NOT via `_FakeCtx` or `_MutableHarnessContext` test-locals. This is the critical AC enforcing the verification-shape discipline catalogued at batch-15 §6(a) + batch-16 §6 sharpening; test FAILS at design-review if the test scaffolding bypasses production bootstrap.
  9. **Test cleans up fixture state at teardown** (no test artifacts persisted between runs; no zombie subprocesses).
  10. **Importable; pyright strict mode passes.** Both test functions resolve; integration test suite (broader workspace) remains green at U-RT-89 landing arc.

---

## §2 — DAG topology delta (v2.19 → v2.20)

NEW L9-undecies cluster appended with cluster-boundary edges to already-landed CP-axis substrate (CP spec v1.13 §26 carriers at U-CP-62/63/64/65 closure commits in cluster 10-CP-B) + already-landed runtime-axis stage-1 IS-bucket carriers + the existing `harness_runtime.api.run(...)` workflow-execution entry point. No edges into v2.19 units beyond cluster-boundary deps to L9-decies / L9-novies / L9-octies / L9-septies (those clusters are fully landed at HEAD). No edges from L9-decies / L9-novies / L9-octies / L9-septies into L9-undecies (L9-undecies is structurally terminal at v2.20 — produces the pause/resume-protocol binding chain; no downstream unit at this plan revision consumes its output beyond U-RT-89's own e2e exercise).

Topological sort within L9-undecies (acyclic verified — linear chain):

```
L9-undecies (NEW at v2.20):
  L0-within-cluster: U-RT-87 (within-cluster deps: none;
                              cluster-boundary deps: U-CP-62 at cluster 10-CP-B closure)
  L1-within-cluster: U-RT-88 (within-cluster deps: U-RT-87;
                              cluster-boundary deps: U-CP-62, U-CP-63, U-CP-64
                              at cluster 10-CP-B closure commits)
  L2-within-cluster: U-RT-89 (within-cluster deps: U-RT-87, U-RT-88;
                              cluster-boundary deps: U-CP-62, U-CP-63, U-CP-64, U-CP-65
                              at cluster 10-CP-B closure commits)
```

**Cluster-boundary edges (NEW at v2.20):** 8 edges total —
- `U-RT-87 ← U-CP-62` (PauseResumeProtocol class + PauseResumeProtocolConfig carrier types landing at `49617e7` — type import boundary)
- `U-RT-88 ← U-CP-62` (PauseResumeProtocol class — factory body constructor invocation)
- `U-RT-88 ← U-CP-63` (capture_pause_snapshot async method — protocol-conformance baseline)
- `U-RT-88 ← U-CP-64` (attempt_resume async method — protocol-conformance baseline)
- `U-RT-89 ← U-CP-62` (PauseSnapshot + ResumeResult + WorkflowPauseReason + MaterialDiffPolicy carriers — driver type imports + test-fixture construction)
- `U-RT-89 ← U-CP-63` (capture_pause_snapshot — driver per-step invocation)
- `U-RT-89 ← U-CP-64` (attempt_resume — driver entry-point invocation)
- `U-RT-89 ← U-CP-65` (pause.captured + resume.attempted span emission — driver context for observability)

All target already-landed cluster 10-CP-B closure commits (no in-flight predecessor). No cycle risk.

**Within-cluster edges (NEW at v2.20):** 3 edges total —
- `U-RT-88 ← U-RT-87` (factory consumes `RuntimeConfig.pause_resume_protocol_config` field + `HarnessContext.pause_resume_protocol` + `HarnessContext.pause_requested_flag` field landings)
- `U-RT-89 ← U-RT-87` (driver consumes `ctx.pause_resume_protocol` + `ctx.pause_requested_flag` fields; e2e test constructs `RuntimeConfig` with `PauseResumeProtocolConfig` instance)
- `U-RT-89 ← U-RT-88` (driver invocation + e2e test exercise the wired `materialize_pause_resume_protocol_stage` factory output bound to `ctx.pause_resume_protocol`)

Linear chain U-RT-87 → U-RT-88 → U-RT-89 acyclic by construction.

**Cross-axis edges:** unchanged from v2.19. L9-undecies adds ZERO new cross-axis edges — U-RT-87 + U-RT-88 + U-RT-89 consume already-landed CP-axis carriers (CP spec v1.13 §26 `PauseResumeProtocol` class + `PauseResumeProtocolConfig` + `PauseSnapshot` + `ResumeResult` + `WorkflowPauseReason` + `MaterialDiffPolicy` carriers) per existing CXA-declared composition seams; no new CXA edge declaration. CXA v2.9 unchanged per spec §14.14.6 cross-axis cascade enumeration.

DAG verified acyclic via Kahn execution (delta layer): 8 new cluster-boundary edges consumed (all targeting already-landed cluster 10-CP-B units); 3 new within-cluster edges (linear chain U-RT-87 → U-RT-88 → U-RT-89); 0 new cross-axis edges. No cycle path within L9-undecies (linear chain trivially acyclic); no cycle path into L9-undecies (cluster 10-CP-B is fully landed at HEAD, no back-edge possible).

---

## §3 — Coverage matrix delta (v2.19 → v2.20)

| Contract | Units covering | Change at v2.20 |
|---|---|---|
| Runtime spec v1.21 §3 C-RT-02 RuntimeConfig table NEW row (`pause_resume_protocol_config`) | U-RT-87 | NEW v2.20 ADD column |
| Runtime spec v1.21 §4 C-RT-04 HarnessContext table NEW rows (`pause_resume_protocol` + `pause_requested_flag`) | U-RT-87 | NEW v2.20 ADD column |
| Runtime spec v1.21 §14.14.1 architectural surfaces (`PauseResumeProtocolConfig` + `PauseContextReader` + factory signature) | U-RT-87 (sub-model), U-RT-88 (PauseContextReader type alias + factory signature) | NEW v2.20 ADD column |
| Runtime spec v1.21 §14.14.2 per-factory invocation discipline (5 invariants) | U-RT-88 | NEW v2.20 ADD column |
| Runtime spec v1.21 §14.14.3 lifecycle stage placement (stage-5 LOOP_INIT wiring + workflow_driver detection point) | U-RT-88 (stage-5 wiring), U-RT-89 (workflow_driver detection point + entry-point resume detection) | NEW v2.20 ADD column |
| Runtime spec v1.21 §14.14.4 failure-mode taxonomy (`RT-FAIL-PAUSE-RESUME-STAGE-MATERIALIZE`) | U-RT-88 | NEW v2.20 ADD column |
| Runtime spec v1.21 §14.14.5 invariants (5) | U-RT-87 (1 + 2 + 4 structural), U-RT-88 (1 + 2 + 3 structural), U-RT-89 (4 + 5 operational verification) | NEW v2.20 ADD column |
| Runtime spec v1.21 §14.14.6 X-AL-2 retirement implications (operational-criterion-B exercise for H_T-CP-22) | U-RT-89 | NEW v2.20 ADD column |
| Meta-Arch v1.5 §7.7 X-AL-2 retirement criterion (operational-MET semantics for H_T-CP-22 operator-opt-in pattern) | U-RT-89 | NEW v2.20 ADD column |
| CP spec v1.13 §26 PauseResumeProtocol class + PauseResumeProtocolConfig + PauseSnapshot + ResumeResult + WorkflowPauseReason + MaterialDiffPolicy carriers | (pre-v2.20 CP-axis coverage at U-CP-62/63/64/65), U-RT-87 (type import), U-RT-88 (consumes class + carriers), U-RT-89 (e2e exercises class) | (no change to CP coverage; runtime-axis ADD column) |
| All other v1.21 + v1.5 + v1.13 + v1.11 contracts | preserved verbatim from v2.19 coverage | (no change) |

**Coverage gap audit:** none surfaced at coherence pass.
- The L9-undecies units' `Implements` lines cite **only existing filed contracts** (runtime spec v1.21 + Meta-Arch v1.5 + CP spec v1.13) — no spec-shaped gap requiring `Phase_7_Class_N_Tension` filing per `implementation-planner` SKILL.md §2.
- The operator-opt-in close pattern's "test infrastructure landed alongside RETIRE-READY transition" obligation (per batch-14 §6(a)) is **pre-included** at L9-undecies via U-RT-89 (the close-evidence unit). This is the correct cluster-design discipline per `[[h-t-cp-21-batch-15-down-classification]]` §6(a) verification-shape generalization — operator-opt-in RETIRE-READY substitutions pre-include their close-evidence unit at cluster authoring time. L9-undecies follows the U-RT-82 + U-RT-85 + U-RT-86 precedents (Memory tool + ValidatorFramework + MCP client) of pre-including a close-evidence unit at cluster authoring.

**Cite-precision audit:** all v2.20 cites against runtime spec point at **v1.21** (latest filed version per `Project_Workflow_v1_8.md` §7.4 use-latest-version body-citation-alignment clause; v1.21 committed at `8adb2df` in this worktree, predecessor v1.20 preserved verbatim by reference). Cross-axis cites: CP spec v1.13 §26 at latest filed version; Meta-Arch v1.5 §7.7 at latest filed version; OD spec v1.11 referenced as adjacent context only (workflow-layer audit-write is out of scope at v2.20 — explicit at change-note observation (e)). No invented `§` pins; no inferred cites.

**Already-landed cluster-boundary consumption cites:**
- CP spec v1.13 §26.1 `PauseResumeProtocol` class body at `harness-cp/src/harness_cp/pause_resume_protocol.py:213+` per U-CP-62 cluster 10-CP-B closure `49617e7` — consumed at U-RT-88 + U-RT-89 type-import + factory body constructor invocation + driver per-step invocation.
- CP spec v1.13 §26.2 `WorkflowPauseReason` 5-class + `MaterialDiffPolicy` 3-class + `PauseSnapshot` 8-field + `ResumeResult` 5-field carriers at `harness-cp/src/harness_cp/pause_resume_protocol_types.py` — consumed at U-RT-89 driver type imports + test-fixture construction.
- CP spec v1.13 §26.3 `capture_pause_snapshot` async method + `attempt_resume` async method at `harness-cp/src/harness_cp/pause_resume_protocol.py:262+` — consumed at U-RT-89 driver per-step invocation + entry-point resume invocation.
- CP spec v1.13 §26.4 `pause.captured` + `resume.attempted` span emission helpers at `harness-cp/src/harness_cp/pause_resume_protocol.py:472+` — consumed at U-RT-89 driver context for observability (call-site-level — not modified by L9-undecies; helpers are caller-side invocation per spec §C-OD-30.1 byte-exact alignment).

---

## §4 — Coherence pass

Per `implementation-planner` SKILL.md §5 step 9. Verifying U-RT-87, U-RT-88, U-RT-89 against the four sub-disciplines at §4:

### U-RT-87

1. **Atomicity (§3 four criteria).**
   - 3.1 Single coherent change ✓ — one RuntimeConfig field + two HarnessContext fields + one empty-marker dataclass + one module
   - 3.2 Single focused session ✓ — ~1-hour implementation including module-organization + Pydantic v2 frozen-model validation testing
   - 3.3 Independently testable ✓ — RuntimeConfig instantiation + HarnessContext field landing + PauseResumeProtocolConfig.default() construction verifiable standalone
   - 3.4 Coherent rollback boundary ✓ — one commit revertible

2. **Spec-traceability (§4.2).** Cites 4 contract sections by ID + section: runtime spec v1.21 §3 C-RT-02 + §4 C-RT-04 + §14.14.1 + CP spec v1.13 §26. All verified against `design-substrate/Spec_Harness_Runtime_v1.md` + `design-substrate/Spec_Control_Plane_v1_13.md` at HEAD `8adb2df`. ✓

3. **Dependency-awareness (§4.3).** Declares (within-cluster) none + (cluster-boundary) [U-CP-62 at cluster 10-CP-B `49617e7`]. ✓

4. **Implementation-grade-detail (§4.4).** Names files (`harness-runtime/src/harness_runtime/types.py` + new `harness-runtime/src/harness_runtime/lifecycle/pause_resume_protocol_types.py`); 4 signatures (RuntimeConfig field + 2 HarnessContext fields + PauseResumeProtocolConfig dataclass); 8 ACs each independently verifiable. Does NOT introduce a library not in spec. Does NOT extend the specification (empty-marker shape preserved verbatim from spec §14.14.1). ✓

### U-RT-88

1. **Atomicity (§3 four criteria).**
   - 3.1 Single coherent change ✓ — one factory + one stage-5 wiring + one fail-class enum addition + one pause_context_reader composition (all bound together by the C-RT-24 binding-chain contract)
   - 3.2 Single focused session ✓ — ~2-3-hour implementation including stage-5 integration test + pyright validation
   - 3.3 Independently testable ✓ — once U-RT-87 lands, U-RT-88's AC can be verified standalone (factory invocation, stage-5 wiring, fail-class enum addition all testable without U-RT-89)
   - 3.4 Coherent rollback boundary ✓ — one commit revertible (factory module + stage-5 invocation site + fail-class enum amendment all bound together by the binding-chain contract)

2. **Spec-traceability (§4.2).** Cites 4 contract sections by ID + section: runtime spec v1.21 §14.14.1 + §14.14.2 + §14.14.3 + §14.14.4 + §14.14.5 + CP spec v1.13 §26.3. All verified against `design-substrate/Spec_Harness_Runtime_v1.md` + `design-substrate/Spec_Control_Plane_v1_13.md` at HEAD `8adb2df`. ✓

3. **Dependency-awareness (§4.3).** Declares within-cluster dep [U-RT-87] + cluster-boundary deps [U-CP-62, U-CP-63, U-CP-64] + cluster-boundary deps [bootstrap stage-1 IS carriers — pre-cluster-7 L0 foundational units]. DAG acyclic per §2 Kahn verification. ✓

4. **Implementation-grade-detail (§4.4).** Names files (3 — factory module + stage-5 module + fail-class enum module); 4 signatures (factory + PauseContextReader type alias + fail-class enum + sub-routine surfaces); 8 ACs each independently verifiable. AC #5 enumerates pause_context_reader composition body implementer-discretion per spec §14.14.7 (3 options: closure-over-ctx / partial-application / class-bound-method). Does NOT introduce a library not in spec (CP-axis import at `harness_cp.pause_resume_protocol` is the established class-surface import path per CP spec v1.13). Does NOT extend the specification. ✓

### U-RT-89

1. **Atomicity (§3 four criteria).**
   - 3.1 Single coherent change ✓ — one workflow_driver per-step pre-entry detection + one entry-point resume detection + one RunStatus enum extension + one RunResult field extension + one execute_workflow signature extension + one e2e test module (all bound together by the pause/resume invocation contract)
   - 3.2 Single focused session ✓ — ~3-4-hour implementation including workflow_driver instrumentation + e2e test authoring + pyright validation
   - 3.3 Independently testable ✓ — once U-RT-87 + U-RT-88 land, U-RT-89's AC can be verified standalone (full bootstrap via `harness_runtime.api.run(...)` + workflow exercise + pause + resume + assertion fan-out)
   - 3.4 Coherent rollback boundary ✓ — one commit revertible

2. **Spec-traceability (§4.2).** Cites 5 contract sections by ID + section: runtime spec v1.21 §14.14.3 + §14.14.5 + §14.14.6 + Meta-Arch v1.5 §7.7 X-AL-2 + CP spec v1.13 §26.6. All verified against `design-substrate/Spec_Harness_Runtime_v1.md` + `Phase_7_Meta_Architecture_v1.md` + `design-substrate/Spec_Control_Plane_v1_13.md` + `.harness/phase-7d-retirement-events-batch-{14,16}.md` at HEAD. ✓

3. **Dependency-awareness (§4.3).** Declares within-cluster deps [U-RT-87, U-RT-88] + cluster-boundary deps [U-CP-62, U-CP-63, U-CP-64, U-CP-65]. DAG acyclic per §2 Kahn verification. ✓

4. **Implementation-grade-detail (§4.4).** Names files (3 — workflow_driver_types.py + workflow_driver.py + new test module); 5 signatures (RunStatus value + RunResult field + execute_workflow kwarg + 2 test functions); 10 ACs each independently verifiable. AC #8 explicitly enforces composer-depth parity with U-RT-82 + U-RT-85 + U-RT-86 close-pattern shape (real bootstrap via `harness_runtime.api.run(...)`, NOT `_FakeCtx`); this is the verification-shape discipline per batch-16 §6 sharpening. Does NOT introduce a library not in spec. Does NOT extend the specification. ✓

All four sub-disciplines pass at U-RT-87, U-RT-88, U-RT-89. Cluster-level coherence verified.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_20.md` |
| Version | v2.20 |
| Filing event | Spec-revision-driven plan revision — NEW L9-undecies linear-chain cluster (3 units: U-RT-87 + U-RT-88 + U-RT-89) absorbs runtime spec v1.20 → v1.21 §14.14 C-RT-24 NEW contract per CP composer authoring arc (operator-ratified narrow-scope AskUserQuestion 2026-05-24; spec v1.21 committed at `8adb2df` in this worktree). 2026-05-24 |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_19.md` (v2.19 + v2.18 + v2.17 substantive content preserved verbatim outside the additive L9-undecies cluster authoring) |
| New units | 3 — U-RT-87 (RuntimeConfig field + HarnessContext fields + PauseResumeProtocolConfig empty-marker sub-model), U-RT-88 (materialize_pause_resume_protocol_stage factory + stage-5 wiring + pause_context_reader composition + RT-FAIL-PAUSE-RESUME-STAGE-MATERIALIZE fail class), U-RT-89 (workflow_driver per-step pre-entry pause-trigger detection + protocol invocation + RunStatus.PAUSED + resume-on-snapshot-context entry-point branch + real-bootstrap e2e pause/resume cycle) |
| Revised units | 0 at this plan (all v2.19 + v2.18 + v2.17 units preserved verbatim) |
| Cluster | NEW L9-undecies cluster appended (linear-chain DAG U-RT-87 → U-RT-88 → U-RT-89); L9-decies + L9-novies + L9-octies + L9-septies + L9-sexies + all earlier clusters preserved verbatim |
| Cross-axis dependencies | unchanged from v2.19. L9-undecies adds 0 new CXA edges — U-RT-87 + U-RT-88 + U-RT-89 consume already-landed CP-axis carriers (CP spec v1.13 §26 PauseResumeProtocol class + PauseResumeProtocolConfig + PauseSnapshot + ResumeResult + WorkflowPauseReason + MaterialDiffPolicy) per existing CXA-declared composition seams. CXA v2.9 unchanged per spec §14.14.6. |
| DAG verification | Kahn-acyclic; 8 new cluster-boundary edges consumed (all targeting already-landed cluster 10-CP-B units U-CP-62/63/64/65); 3 new within-cluster edges (linear chain U-RT-87 → U-RT-88 → U-RT-89); ∅ remaining edges within L9-undecies (linear-chain trivially complete). |
| Coverage verification | L9-undecies units cite contract sections across runtime spec v1.21 (§3 + §4 + §14.14.1 + §14.14.2 + §14.14.3 + §14.14.4 + §14.14.5 + §14.14.6) + Meta-Arch v1.5 §7.7 X-AL-2 + CP spec v1.13 §26 + batch-14 §6(a) close pattern + batch-16 §6 verification-shape sharpening; all verified against `design-substrate/` + `.harness/` at HEAD; no spec-shaped gap surfaced; no `Phase_7_Class_N_Tension` filing required. |
| Mechanism discretion | U-RT-88 AC #5 enumerates pause_context_reader composition body implementer-discretion per spec §14.14.7 (3 options: closure-over-ctx / partial-application / class-bound-method); recommended default closure-over-ctx. U-RT-89 ACs accommodate α (recommended default: in-process fixture with clean pause-resume cycle) / β (richer fixture exercising clean-resume + diff-detected paths) / γ (env-var-gated fixture path) per FM-2 no-extension discipline. |
| Retirement-batch absorption owed | batch-18: H_T-CP-22 PARTIAL → RETIRE-READY (post-U-RT-88 stage-factory landing + U-RT-89 workflow_driver invocation per spec §14.14.6) → RETIRED (post-U-RT-89 e2e exercise per batch-14 §6(a) close pattern + batch-16 §6 verification-shape sharpening). Joint PARTIAL → RETIRE-READY → RETIRED transit in single batch (mirrors batch-17 H_T-CP-21 pattern). |
| Date | 2026-05-24 |
