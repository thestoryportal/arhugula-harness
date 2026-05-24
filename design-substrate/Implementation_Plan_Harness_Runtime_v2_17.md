# Implementation Plan — Harness Runtime v2.17

## Change-note (v2.16 → v2.17)

**Scope of revision.** Spec-revision-driven plan revision absorbing runtime spec **v1.17 → v1.18** §14.13 C-RT-23 NEW contract per `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` §3.1 Reading A (operator-ratified 2026-05-24, this session, post-batch-16 close at HEAD `1c55138`; spec v1.18 committed at `1707867`). NEW cluster **L9-decies** appended at §1 below, containing exactly 3 atomic units: **U-RT-83** (`RuntimeConfig.validator_framework_config` field landing + `ValidatorFrameworkConfig` empty-marker sub-model), **U-RT-84** (`materialize_validator_framework_stage` factory + stage-4 wiring + `HarnessContext.validator_framework` field type narrowing), **U-RT-85** (real-bootstrap e2e against operator-supplied `ValidatorFramework` instance, analogous to U-RT-82 + U-RT-86 close-pattern e2e shapes per batch-14 + batch-16 §6(a) catalogues). The cluster operationalizes the binding-chain seam authored at spec §14.13 — the missing runtime materialization contract whose absence at HEAD was the empirical finding behind H_T-CP-21 batch-15 §1.2 RETIRE-READY → PARTIAL DOWN-classification.

**Source of fix.** `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` §3.1 Reading A RATIFIED 2026-05-24 (operator). The fork halted H_T-CP-21 RETIRE-READY → RETIRED transition pending design-phase channel opening; Reading A authorizes the **minimal stage-factory landing only** — author the stage-4 OD-bucket factory contract sufficient to bind an operator-supplied `validator_framework` at production `HarnessContext` without touching the §14.8.2 validator-composer arc deferrals (VALIDATOR_ESCALATION foreclosure at step 3; full 4-axis `_hitl_required` composition at step 4c; cross-trust-boundary palette restriction at step 4d). The Reading A arc opens the design-phase channel to restore H_T-CP-21 to RETIRE-READY/RETIRED via the operator-opt-in pattern (mirrors batch-10 H_T-CP-18 + batch-13 H_T-CP-16 RETIRE-READY shape).

**Plan shape preserved.** v2.16's entire body preserved verbatim — L9-novies cluster (U-RT-86) intact, L9-octies cluster (U-RT-76..U-RT-82) intact, L9-septies cluster (U-RT-71..U-RT-75) intact, all prior unit bodies intact. NEW **L9-decies** cluster appended at §1 below containing 3 atomic units (U-RT-83 + U-RT-84 + U-RT-85). NO existing unit body change; NO AC change at any pre-v2.17 unit; NO DAG topology change at L9-novies / L9-octies / L9-septies / earlier internal structure; ONLY a new cluster appended with within-cluster linear-chain DAG (U-RT-83 → U-RT-84 → U-RT-85) plus cluster-boundary edges to already-landed CP-axis carriers + already-landed bootstrap stage-4 OD carriers.

**Cluster naming.** "L9-decies" follows the existing -ies enumeration (septies/octies/novies/**decies** = 7th/8th/9th/10th). Next available -ies-suffix per the v2.12+ runtime-plan-cluster convention.

**Cluster ordering.** L9-decies opens with U-RT-83 as L0-within-cluster (foundational field + sub-model authoring; no within-cluster predecessors); U-RT-84 at L1-within-cluster (depends on U-RT-83 within-cluster + CP-axis cluster-boundary deps); U-RT-85 at L2-within-cluster (depends on U-RT-84 within-cluster — e2e exercises the wired factory output). Cluster-boundary edges declared explicitly per §7 dependency discipline (CP spec v1.11 §25 carriers at U-CP-58/59/60 closure commits; bootstrap stage-4 OD-bucket carriers from pre-cluster-7 L0 foundational units). NO edges from any pre-v2.17 unit into L9-decies (L9-decies is structurally terminal at v2.17 — produces the validator-framework binding chain; no downstream unit at this plan revision consumes its output beyond U-RT-85's own e2e exercise).

**Operator-discretion test-infrastructure shape (FM-2).** U-RT-85 implementer selects e2e test fixture mechanism per FM-2 no-extension discipline (mirrors U-RT-86 §"Test-substrate mechanism" + U-RT-82 §"Mechanism choice" enumeration patterns). Options:
- **α** — Operator supplies a real `ConcreteValidatorFramework` instance with a single no-op `PASS`-returning `Validator`. Test fixture constructs the framework + wires it via `ValidatorFrameworkConfig` opt-in non-default; bootstrap; workflow step exercises the `workflow_driver.py:668` True-arm. Recommended default.
- **β** — Operator supplies a richer test-fixture validator that exercises the 5-class `ValidatorFailClass` outcome routing across at least `PASS` + `PERMANENT_FAIL`. Two test functions; broader coverage.
- **γ** — Gate on operator-supplied env var (`VALIDATOR_FRAMEWORK_E2E_FIXTURE_PATH`) pointing at a fixture module; test loads + exercises. Mirrors U-RT-86 mechanism-γ pattern for CI-skipping when fixture unavailable.

Recommended default per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` verification: **mechanism α** (in-process fixture, single deterministic `PASS` outcome) — sufficient for U-RT-85's AC #5 verification-shape (binding chain succeeds end-to-end against a real `ValidatorFramework` instance, not a stubbed Protocol); broader outcome-routing coverage deferred to follow-on retirement-batch arc per §14.13.6.

**Adjacent observations (NOT this plan's authoring scope).**

(a) **Spec v1.18 §14.13.7 deferrals.** Reading A explicitly disclaims the validator-composer arc broader scope (VALIDATOR_ESCALATION trigger source landing, 4-axis `_hitl_required` composition, cross-trust-boundary palette restriction). These remain deferred to a future Reading B full-arc opening per fork doc §3.2. L9-decies cluster does NOT touch any §14.8.2 deferral.

(b) **`ValidatorFrameworkConfig` empty-marker shape preserved at U-RT-83.** Per spec §14.13.1 + change-note adjacent finding (iv): the empty-marker dataclass is intentional at Reading A scope (operator-supply mechanism deferred to follow-on arc). U-RT-83 lands the empty-marker shape; future plan revisions may extend the sub-model when operator-supply semantics materialize. **U-RT-83 ACs explicitly enforce empty-marker shape**: no fields beyond `.default()` factory.

(c) **Factory body construction discretion at U-RT-84.** Per spec §14.13.1 (factory signature + opt-out branch is full-spec; opt-in branch construction body is deferred to impl arc per §14.13.7): U-RT-84 implementer selects whether to (i) land `NotImplementedError` on the opt-in branch (deferring construction body to a follow-on arc), OR (ii) land minimal construction body sufficient to produce a `ConcreteValidatorFramework` instance from an operator-supplied `ValidatorFrameworkConfig`. **U-RT-84 ACs accommodate both shapes**; AC #5 selects between them at impl-time per `[[halt-route-split-AC-pattern]]` precedent if neither full-implementation nor full-deferral is achievable. **U-RT-85 e2e gates on the opt-in branch returning a real `ValidatorFramework`** — so option (i) at U-RT-84 leaves U-RT-85 needing its own minimal construction shim, OR U-RT-85 selects to gate the e2e fully on the opt-in branch being a no-op `PASS` shape. Implementer-selected per FM-2.

(d) **Carrier-home decision: `ValidatorFrameworkConfig` lives in `harness-runtime`** at U-RT-83. Parallel to `MemoryToolBackendConfig` at `harness-runtime` per spec v1.17 §14.12 + v1.18 §14.13 (both RuntimeConfig sub-models live in the runtime package). Alternative carrier-home (`harness-core` empty-marker per `SandboxDecisionPolicy` precedent) was considered but rejected on grounds of consistency with the §14.12 precedent — RuntimeConfig sub-models that pair with stage factories at runtime spec contracts live in `harness-runtime`. `harness-core` carries cross-axis-shared types (like `SandboxDecisionPolicy` which is consumed by harness-cp); `ValidatorFrameworkConfig` is consumed ONLY by the runtime-spec factory at v1.18 (the actual `ValidatorFramework` Protocol surface remains at CP spec v1.11 §25).

**Downstream absorption owed (post-v2.17).**

(a) Workspace `CLAUDE.md` §2.4 runtime row version bump (v2.16 → v2.17); co-published at L9-decies cluster open arc OR batch-17 retirement-event arc (whichever fires first). Unit count 84 → 87 (+3 units).

(b) Adversarial review per `harness-adversarial-reviewer` skill — P5-CK adversarial review of runtime spec v1.18 + P6-CK adversarial review of runtime plan v2.17 owed at follow-on session per `Project_Workflow_v1_8.md` §4.1 (P5-CK / P6-CK checkpoint shape).

(c) Phase 7 cluster-open authorization for L9-decies at follow-on session per `phase-7-implementation` skill discipline. Cluster sequencing: L9-decies opens with U-RT-83 as the L0 entry-point; topological sort U-RT-83 → U-RT-84 → U-RT-85.

(d) Batch-17 retirement-event filing per `phase-7-substitution-retirement` skill at L9-decies cluster close: H_T-CP-21 PARTIAL → RETIRE-READY (post-U-RT-84 stage-factory landing per spec §14.13.6) → RETIRED (post-U-RT-85 e2e exercise per batch-14 §6(a) close pattern + batch-16 §6 verification-shape sharpening).

(e) `Cross_Axis_Composition_Document_v2_8.md` unchanged at v2.17 — fork doc §5 confirms ZERO cross-axis cascade. The `validator_framework` ctx-binding consumes already-landed CP spec v1.11 §25 `ConcreteValidatorFramework` carrier without new CXA edge introduction.

(f) CP spec v1.11 + OD spec v1.9 unchanged at v2.17. The CP-axis `Validator` + `ValidatorFramework` Protocol surfaces are canonical at CP spec v1.11 §25; the runtime spec v1.18 §14.13 consumes them without amendment. The OD-axis `validator.*` span schema is canonical at OD spec v1.9 §C-OD-29.1; the runtime composer at `workflow_driver.py:668` emits per OD-canonical attribute set without OD-side amendment.

---

## §1 — L9-decies cluster (NEW at v2.17)

### U-RT-83 — `RuntimeConfig.validator_framework_config` field + `ValidatorFrameworkConfig` empty-marker sub-model

- **Implements:** Runtime spec **v1.18** §3 C-RT-02 RuntimeConfig table NEW row (`validator_framework_config: ValidatorFrameworkConfig | None = None`) + **v1.18** §14.13.1 `ValidatorFrameworkConfig` empty-marker `@dataclass(frozen=True)` sub-model + `.default()` factory classmethod per the SandboxDecisionPolicy-precedent shape applied at the runtime-package carrier-home per change-note adjacent observation (d). NO field beyond the `.default()` factory at v1.18 Reading A scope.

- **Files:**
  - `harness-runtime/src/harness_runtime/types.py` — append NEW field `validator_framework_config: ValidatorFrameworkConfig | None = None` to the existing `RuntimeConfig` Pydantic v2 BaseModel at the established field-ordering pattern (after `memory_tool_backend_config`).
  - `harness-runtime/src/harness_runtime/validator_framework_config.py` (NEW) — author `ValidatorFrameworkConfig` empty-marker `@dataclass(frozen=True)` with `.default()` factory classmethod; module exports `ValidatorFrameworkConfig`. Parallel to `harness-runtime/src/harness_runtime/lifecycle/memory_tool_*.py` module-organization pattern for runtime-internal sub-models per spec §14.12.

- **Signatures:**
  - `RuntimeConfig.validator_framework_config: ValidatorFrameworkConfig | None = None` — appended to existing frozen Pydantic v2 BaseModel; default `None`.
  - `@dataclass(frozen=True)` `ValidatorFrameworkConfig` with NO fields; `@classmethod def default(cls) -> ValidatorFrameworkConfig: return cls()` factory.

- **Depends on:** (within-cluster) (none); (cluster-boundary) (none) — U-RT-83 is foundational at L9-decies; lands the operator-supply opt-in surface without consuming any prior carrier beyond the existing `RuntimeConfig` Pydantic v2 BaseModel + `harness-runtime` package scaffolding (already at HEAD pre-v2.17).

- **ACs:**
  1. **`RuntimeConfig.validator_framework_config` field appended** at the established field-ordering position (after `memory_tool_backend_config`); type annotation `ValidatorFrameworkConfig | None`; default `None`; frozen-model invariant preserved per existing C-RT-02 §3 invariants.
  2. **`ValidatorFrameworkConfig` empty-marker authored** as `@dataclass(frozen=True)` with NO fields; `.default()` classmethod returns `cls()` empty instance.
  3. **Module organization parallel to §14.12 precedent**: `ValidatorFrameworkConfig` lives in `harness-runtime/src/harness_runtime/validator_framework_config.py` (or equivalent runtime-package-internal module organization at implementer discretion); not in `harness-core` (per change-note adjacent observation (d) carrier-home decision).
  4. **`RuntimeConfig(validator_framework_config=None)` constructs successfully** + `RuntimeConfig(validator_framework_config=ValidatorFrameworkConfig.default())` constructs successfully. Both shapes pass Pydantic v2 frozen-model validation.
  5. **Spec v1.18 §3 C-RT-02 RuntimeConfig table NEW row verbatim**: field name, type, default, semantic prose all match the spec table row at the field-table layer (citation byte-exact per `Project_Workflow_v1_8.md` §7.4.2).
  6. **Importable; pyright strict mode passes.** `from harness_runtime.types import RuntimeConfig` + `from harness_runtime.validator_framework_config import ValidatorFrameworkConfig` (or implementer-selected module path) both resolve without error.

### U-RT-84 — `materialize_validator_framework_stage` factory + stage-4 wiring + `HarnessContext.validator_framework` field type narrowing

- **Implements:** Runtime spec **v1.18** §14.13.1 factory signature (`async def materialize_validator_framework_stage(config: RuntimeConfig) → ValidatorFramework | None`) + **v1.18** §14.13.2 per-factory invocation discipline (4 invariants) + **v1.18** §14.13.3 stage-4 OD-bucket wiring (factory runs at stage 4 after `tracer_provider` + `audit_writer` + `cost_chain` + `collector_daemon` per the §14.13.3 ordering pin) + **v1.18** §4 C-RT-04 HarnessContext field type narrowing (`object | None` → `ValidatorFramework | None` typed Protocol surface from CP spec v1.11 §25) + **v1.18** §14.13.4 NEW fail class `RT-FAIL-VALIDATOR-STAGE-MATERIALIZE` landing + **v1.18** §14.13.5 invariants (4).

- **Files:**
  - `harness-runtime/src/harness_runtime/bootstrap/factories/validator_framework_factory.py` (NEW) — author `materialize_validator_framework_stage(config) → ValidatorFramework | None` factory per spec §14.13.1 signature. Module parallels existing `harness-runtime/src/harness_runtime/bootstrap/factories/memory_tool_registry_factory.py` + `mcp_client_host_factory.py` + `runtime_tool_dispatcher_factory.py` module-organization patterns.
  - `harness-runtime/src/harness_runtime/bootstrap/stage_4_od.py` (or equivalent existing stage-4-bundle module) — append factory invocation at the established stage-4 ordering pin (after `tracer_provider` + `audit_writer` + `cost_chain` + `collector_daemon` per spec §14.13.3); bind factory output to `ctx.validator_framework`.
  - `harness-runtime/src/harness_runtime/types.py` — amend existing `HarnessContext.validator_framework` field annotation at the row currently typed `object | None = None` (pre-v2.17 untyped carrier at line ~1157 per spec v1.18 §4 amendment row) → narrow to `ValidatorFramework | None`. Import `ValidatorFramework` from `harness_cp.validator_framework_types` (CP spec v1.11 §25 Protocol carrier) at the runtime-types module-import boundary.
  - `harness-runtime/src/harness_runtime/fail_classes.py` (or equivalent existing fail-class enum module) — append `RT-FAIL-VALIDATOR-STAGE-MATERIALIZE` enum member per spec §14.13.4 + runtime-local fail-class taxonomy convention.

- **Signatures:**
  - `async def materialize_validator_framework_stage(config: RuntimeConfig) -> ValidatorFramework | None`
  - Factory body per spec §14.13.1: `if config.validator_framework_config is None: return None` (empty-sentinel branch — returns the no-validator state); else construct + return a `ValidatorFramework` Protocol-satisfying instance per spec §14.13.5 invariant 3 (`@runtime_checkable` Protocol-conformance enforced).
  - `HarnessContext.validator_framework: ValidatorFramework | None` — Pydantic v2 field annotation amended from `object | None`; default `None`.
  - `RT-FAIL-VALIDATOR-STAGE-MATERIALIZE` — new fail-class enum member at the runtime-local fail-class taxonomy.

- **Depends on:** (within-cluster) [U-RT-83 — RuntimeConfig field + ValidatorFrameworkConfig empty-marker]; (cluster-boundary, CP-axis) [U-CP-58 — ValidatorFailClass 5-class enum at C-CP-25 §25.2 landed at closure-arc commit `16cf6d7`; U-CP-59 — Validator + ValidatorFramework Protocol envelope schemas at C-CP-25 §25.1 landed at `cdf83b1`; U-CP-60 — ConcreteValidatorFramework body + evaluate() async method at C-CP-25 §25.3 landed at `5ca86aa`]; (cluster-boundary, runtime-axis) bootstrap stage-4 OD-bucket carriers (tracer_provider + audit_writer + cost_chain + collector_daemon — pre-cluster-7 L0 foundational units, all already at HEAD).

- **ACs:**
  1. **`materialize_validator_framework_stage(config) → ValidatorFramework | None` factory authored** at `harness-runtime/src/harness_runtime/bootstrap/factories/validator_framework_factory.py` (or implementer-selected module path); signature matches spec §14.13.1 verbatim; async; returns `ValidatorFramework | None` (CP spec v1.11 §25 Protocol surface).
  2. **Opt-out branch: `config.validator_framework_config is None` → factory returns `None`** unconditionally; no exception raised. The production-default state (operator has not opted in) yields `ctx.validator_framework is None`; the `workflow_driver.py:668` branch evaluates False; backward-compatible behavior preserved per spec §14.13.5 invariant 2.
  3. **Opt-in branch behavior** (per implementer FM-2 selection between options (i) and (ii) at change-note adjacent observation (c)):
     - **Option (i)**: factory raises `NotImplementedError` on the non-`None` opt-in branch with a clear diagnostic message ("ValidatorFrameworkConfig construction body deferred to follow-on arc per spec v1.18 §14.13.7"). U-RT-85 gates on the opt-out branch only.
     - **Option (ii)**: factory constructs a minimal `ConcreteValidatorFramework` instance from `config.validator_framework_config` (the empty-marker shape carries no operator-supplied validators at v1.18 Reading A scope; implementer constructs the simplest no-op framework). `@runtime_checkable` Protocol-conformance enforced; raises `RT-FAIL-VALIDATOR-STAGE-MATERIALIZE` on conformance failure per spec §14.13.4.
  4. **Stage-4 OD-bucket wiring** at `harness-runtime/src/harness_runtime/bootstrap/stage_4_od.py` (or equivalent): factory invocation runs AFTER `tracer_provider` + `audit_writer` + `cost_chain` + `collector_daemon` stage-4 bindings per spec §14.13.3 ordering pin; factory output bound to `ctx.validator_framework`. Stage-4 ordering verified per spec §14.13.3 — implementer may verify via integration test exercising the stage-4 ordering invariant.
  5. **`HarnessContext.validator_framework` field type narrowed** from `object | None` (v1.17-era untyped carrier at `harness-runtime/src/harness_runtime/types.py:1157`) → `ValidatorFramework | None` (typed Protocol surface from `harness_cp.validator_framework_types`). Import path resolves; pyright strict mode validates the type narrowing without error.
  6. **`RT-FAIL-VALIDATOR-STAGE-MATERIALIZE` fail-class enum member appended** at the runtime-local fail-class taxonomy module per spec §14.13.4; permanent severity; bootstrap-rollback semantics per C-RT-02 (mirrors `RT-FAIL-MEMORY-BACKEND-RESOLUTION` v1.17 §14.12.4 precedent).
  7. **Spec §14.13.5 invariants verified**:
     - Invariant 1 (single instance per bootstrap): factory invoked exactly once at stage 4; `ctx.validator_framework` bound exactly once.
     - Invariant 2 (empty-sentinel preserves backward compat): existing test suite (pre-v2.17 broader test coverage) passes without amendment because the default `RuntimeConfig.validator_framework_config = None` yields the no-validator state observed at HEAD pre-v2.17.
     - Invariant 3 (CP-canonical Protocol satisfaction): when factory returns non-`None`, the instance satisfies `@runtime_checkable ValidatorFramework` Protocol from CP spec v1.11 §25.1.
     - Invariant 4 (no validator-composer arc resolutions at v1.18): U-RT-84 implementation does NOT touch `harness-cp/src/harness_cp/workflow_driver.py:668` hook or any §14.8.2 site; the existing C-CP-25 §25.3.3.4 driver hook contract is preserved verbatim.
  8. **Importable; pyright strict mode passes.** `from harness_runtime.bootstrap.factories.validator_framework_factory import materialize_validator_framework_stage` resolves; integration test exercising opt-out branch passes.

### U-RT-85 — Real-bootstrap e2e test against operator-supplied `ValidatorFramework`

- **Implements:** Runtime spec **v1.18** §14.13.6 X-AL-2 retirement implication path (operational-criterion-B exercise for H_T-CP-21 RETIRE-READY → RETIRED transition) + **v1.18** §14.13.5 invariants (operationally verified at e2e exercise) + Meta-Arch **v1.5** §7.7 X-AL-2 retirement criterion (full RETIRED transition prerequisites for H_T-CP-21 operator-opt-in pattern per fork doc §3.1 Reading A scope) + **batch-14 §6(a)** close pattern catalogue + **batch-16 §6** verification-shape sharpening discipline ("grep-for-presence ≠ verified-working-end-to-end" — driver invocation must succeed end-to-end against a real substrate).

- **Files:** `harness-runtime/tests/integration/test_u_rt_85_validator_framework_e2e.py` (NEW — e2e integration test module). Parallel module-organization pattern to `harness-runtime/tests/integration/test_u_rt_82_memory_tool_filesystem_e2e.py` + `test_u_rt_86_mcp_client_external_server_e2e.py`.

- **Test scope.** Single passing test run satisfies operational-criterion-B for H_T-CP-21 per `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` close pattern catalogue. The test constructs `HarnessContext` via the real bootstrap with operator-supplied `validator_framework_config` non-default (an opt-in `ValidatorFrameworkConfig` instance — empty-marker at v1.18 Reading A scope) + drives a workflow with a single workflow step that triggers the `workflow_driver.py:668` True-arm (validator framework non-`None` branch) + verifies the 5-class outcome routing per C-CP-25 §25.3.3.4 fires (at minimum the `PASS` outcome).

- **Test-substrate mechanism: implementer discretion (FM-2 per change-note "Operator-discretion test-infrastructure shape").** Implementer selects mechanism α (in-process fixture with single no-op `PASS`-returning `Validator`, recommended default) / β (richer fixture exercising `PASS` + `PERMANENT_FAIL` outcomes) / γ (env-var-gated fixture path). Mechanism α is the minimum AC-satisfying shape; β + γ extend coverage at implementer-discretion. The recommended default mechanism (α) is sufficient for U-RT-85 ACs verification.

- **Signatures:**
  - `async def test_validator_framework_e2e_pass_outcome()` — full bootstrap with `RuntimeConfig(deployment_surface=LOCAL_DEV, ..., validator_framework_config=<test ValidatorFrameworkConfig>)`; constructs a workflow with a single workflow step that triggers the validator hook at `workflow_driver.py:668` True-arm; executes the workflow via `harness_runtime.api.run(config, workflow_manifest)` (or the equivalent production entry point); asserts (i) `ctx.validator_framework is not None`, (ii) the `workflow_driver.py:668` True-arm fired (verified via in-test framework's evaluate-call recorder), (iii) the `PASS` outcome was returned by the framework's `evaluate(...)` method, (iv) the workflow step's terminal output reflects the validator framework's `PASS` outcome routing per C-CP-25 §25.3.3.4.
  - **Deterministic-validator fixture (eliminates flakiness).** The test uses a fixed `ValidatorFramework` fixture that always returns `ValidatorFailClass.PASS`. No LLM in the loop at U-RT-85 (contrast with U-RT-82 which gated on Anthropic API); the test exercises ONLY the validator-framework binding chain + `workflow_driver.py:668` hook firing, not any LLM-driven validation decision-making.
  - `async def test_validator_framework_e2e_opt_out_branch()` — separate test verifying the opt-out shape: `RuntimeConfig(..., validator_framework_config=None)` yields `ctx.validator_framework is None`; the `workflow_driver.py:668` False-arm executes; no validator hook fires; backward-compatible behavior preserved per spec §14.13.5 invariant 2.
  - Test gating: both tests marked `@pytest.mark.e2e`; mechanism-specific `@pytest.mark.skipif(...)` only at mechanism-γ selection; otherwise unconditional. Explicit pytest fixture for `ValidatorFramework` lifecycle (setup + teardown if needed).

- **Depends on:** (within-cluster) [U-RT-83 — RuntimeConfig field landing + ValidatorFrameworkConfig empty-marker; U-RT-84 — factory + stage-4 wiring + HarnessContext field type narrowing]; (cluster-boundary, CP-axis) [U-CP-58 + U-CP-59 + U-CP-60 + U-CP-61 — Validator + ValidatorFramework Protocol envelope schemas + ConcreteValidatorFramework body + workflow_driver.py:668 post-dispatch hook landings at closure-arc commits `16cf6d7`/`cdf83b1`/`5ca86aa`/`9b009d3` per `[[fork-validator-composer-arc-stage-4-absence]]` empirical verification at batch-15 §1.1]; (cluster-boundary, runtime-axis) bootstrap stage-7 INGRESS_ACCEPT carriers + workflow-execution entry point at `harness_runtime.api.run(...)` (pre-cluster-7 L0 foundational units, all already at HEAD).

- **ACs:**
  1. **Test runs with operator-supplied validator framework**: completes within reasonable timeout (~10s); the validator framework's `evaluate(...)` method was invoked at the production hook site (verified via in-test framework's method-call recorder asserting the expected `(step, ...)` tuple); the `PASS` outcome was returned to the workflow driver (verified via workflow step's terminal output asserting the `PASS`-routed path).
  2. **Test runs with opt-out config**: `RuntimeConfig(validator_framework_config=None)` yields `ctx.validator_framework is None`; the `workflow_driver.py:668` False-arm fires (no validator-evaluate call recorded); backward-compatible behavior preserved.
  3. **`ctx.validator_framework` type-narrowed correctly**: opt-in branch returns a `ValidatorFramework` Protocol-satisfying instance per spec §14.13.5 invariant 3; pyright strict-mode validates `@runtime_checkable` Protocol conformance at the test fixture's construction site.
  4. **5-class outcome routing exercise**: at minimum the `PASS` outcome is exercised; the workflow step terminates with the `PASS`-routed path per C-CP-25 §25.3.3.4 (other outcomes — `PERMANENT_FAIL` / `ESCALATE_HITL` / `REVALIDATE` / `TRANSIENT_FAIL` — implementer-discretion at mechanism-β selection; not required at mechanism-α minimum AC-satisfying shape).
  5. **Composer-depth parity with U-RT-82 + U-RT-86 close-pattern shape**: the test constructs `HarnessContext` via the **real** `harness_runtime.api.run(...)` (or equivalent production bootstrap entry point), NOT via `_FakeCtx` or `_MutableHarnessContext` test-locals. This is the critical AC enforcing the verification-shape discipline catalogued at batch-15 §6(a) + batch-16 §6 sharpening; test FAILS at design-review if the test scaffolding bypasses production bootstrap.
  6. **Stage-4 ordering empirically verified**: the validator framework binds at stage 4 OD-bucket AFTER `tracer_provider` + `audit_writer` + `cost_chain` + `collector_daemon` per spec §14.13.3; either via stage-ordering instrumentation OR via integration-test side-effect ordering (the framework's `evaluate(...)` method, if it emits a `validator.*` span per OD spec v1.9 §C-OD-29.1, requires `tracer_provider` to be bound prior — empirical verification of the ordering invariant).
  7. **Test cleans up fixture state at teardown** (no test artifacts persisted between runs; no zombie subprocesses at mechanism-γ selection if used).
  8. **Importable; pyright strict mode passes.** Both test functions resolve; integration test suite (broader workspace) remains green at U-RT-85 landing arc.

---

## §2 — DAG topology delta (v2.16 → v2.17)

NEW L9-decies cluster appended with cluster-boundary edges to already-landed CP-axis substrate (CP spec v1.11 §25 carriers) + already-landed runtime-axis stage-4 OD-bucket carriers + the existing `harness_runtime.api.run(...)` workflow-execution entry point. No edges into v2.16 units beyond cluster-boundary deps to L9-septies/octies/novies (those clusters are fully landed at HEAD). No edges from L9-septies / L9-octies / L9-novies into L9-decies (L9-decies is structurally terminal at v2.17 — produces the validator-framework binding chain; no downstream unit at this plan revision consumes its output beyond U-RT-85's own e2e exercise).

Topological sort within L9-decies (acyclic verified — linear chain):

```
L9-decies (NEW at v2.17):
  L0-within-cluster: U-RT-83 (within-cluster deps: none;
                              cluster-boundary deps: none)
  L1-within-cluster: U-RT-84 (within-cluster deps: U-RT-83;
                              cluster-boundary deps: U-CP-58, U-CP-59, U-CP-60
                              at cluster 10-CP-A closure commits)
  L2-within-cluster: U-RT-85 (within-cluster deps: U-RT-83, U-RT-84;
                              cluster-boundary deps: U-CP-58, U-CP-59, U-CP-60, U-CP-61
                              at cluster 10-CP-A closure commits)
```

**Cluster-boundary edges (NEW at v2.17):** 7 edges total —
- `U-RT-84 ← U-CP-58` (ValidatorFailClass enum landing at `16cf6d7`)
- `U-RT-84 ← U-CP-59` (Validator + ValidatorFramework Protocol envelopes at `cdf83b1`)
- `U-RT-84 ← U-CP-60` (ConcreteValidatorFramework body at `5ca86aa`)
- `U-RT-85 ← U-CP-58` (ValidatorFailClass — outcome routing exercise)
- `U-RT-85 ← U-CP-59` (Validator + ValidatorFramework — type-narrowing assertion)
- `U-RT-85 ← U-CP-60` (ConcreteValidatorFramework — test fixture construction baseline)
- `U-RT-85 ← U-CP-61` (workflow_driver.py:668 post-dispatch hook at `9b009d3` — True-arm firing assertion)

All target already-landed cluster 10-CP-A closure commits (no in-flight predecessor). No cycle risk.

**Within-cluster edges (NEW at v2.17):** 3 edges total —
- `U-RT-84 ← U-RT-83` (factory consumes `RuntimeConfig.validator_framework_config` field + `ValidatorFrameworkConfig` empty-marker)
- `U-RT-85 ← U-RT-83` (e2e test constructs `RuntimeConfig` with `ValidatorFrameworkConfig` instance)
- `U-RT-85 ← U-RT-84` (e2e test exercises the wired `materialize_validator_framework_stage` factory + `ctx.validator_framework` field)

Linear chain U-RT-83 → U-RT-84 → U-RT-85 acyclic by construction.

**Cross-axis edges:** unchanged from v2.16. L9-decies adds ZERO new cross-axis edges — U-RT-84 + U-RT-85 consume already-landed CP-axis carriers (CP spec v1.11 §25 `Validator` + `ValidatorFramework` Protocol + `ConcreteValidatorFramework` body + `ValidatorFailClass` enum) per existing CXA-declared composition seams; no new CXA edge declaration. CXA v2.8 unchanged per fork doc §5.

DAG verified acyclic via Kahn execution (delta layer): 7 new cluster-boundary edges consumed (all targeting already-landed cluster 10-CP-A units); 3 new within-cluster edges (linear chain U-RT-83 → U-RT-84 → U-RT-85); 0 new cross-axis edges. No cycle path within L9-decies (linear chain trivially acyclic); no cycle path into L9-decies (cluster 10-CP-A is fully landed at HEAD, no back-edge possible).

---

## §3 — Coverage matrix delta (v2.16 → v2.17)

| Contract | Units covering | Change at v2.17 |
|---|---|---|
| Runtime spec v1.18 §3 C-RT-02 RuntimeConfig table NEW row (`validator_framework_config`) | U-RT-83 | NEW v2.17 ADD column |
| Runtime spec v1.18 §14.13.1 architectural surfaces (`ValidatorFrameworkConfig` + factory signature) | U-RT-83 (sub-model), U-RT-84 (factory signature) | NEW v2.17 ADD column |
| Runtime spec v1.18 §14.13.2 per-factory invocation discipline (4 invariants) | U-RT-84 | NEW v2.17 ADD column |
| Runtime spec v1.18 §14.13.3 lifecycle stage placement (stage-4 OD-bucket wiring) | U-RT-84 | NEW v2.17 ADD column |
| Runtime spec v1.18 §14.13.4 failure-mode taxonomy (`RT-FAIL-VALIDATOR-STAGE-MATERIALIZE`) | U-RT-84 | NEW v2.17 ADD column |
| Runtime spec v1.18 §14.13.5 invariants (4) | U-RT-84 (1-4 structural), U-RT-85 (operational verification) | NEW v2.17 ADD column |
| Runtime spec v1.18 §14.13.6 X-AL-2 retirement implications (operational-criterion-B exercise for H_T-CP-21) | U-RT-85 | NEW v2.17 ADD column |
| Runtime spec v1.18 §4 C-RT-04 HarnessContext field type narrowing (`validator_framework: object \| None → ValidatorFramework \| None`) | U-RT-84 | NEW v2.17 ADD column |
| Meta-Arch v1.5 §7.7 X-AL-2 retirement criterion (operational-MET semantics for H_T-CP-21 operator-opt-in pattern) | U-RT-85 | NEW v2.17 ADD column |
| CP spec v1.11 §25 Validator + ValidatorFramework Protocol + ConcreteValidatorFramework body | (pre-v2.17 CP-axis coverage at U-CP-58/59/60), U-RT-84 (consumes Protocol surface), U-RT-85 (e2e exercises Protocol-conformance) | (no change to CP coverage; runtime-axis ADD column) |
| All other v1.18 + v1.5 + v1.11 + v1.9 contracts | preserved verbatim from v2.16 coverage | (no change) |

**Coverage gap audit:** none surfaced at coherence pass.
- The L9-decies units' `Implements` lines cite **only existing filed contracts** (runtime spec v1.18 + Meta-Arch v1.5 + CP spec v1.11) — no spec-shaped gap requiring `Phase_7_Class_N_Tension` filing per `implementation-planner` SKILL.md §2.
- The operator-opt-in close pattern's "test infrastructure landed alongside RETIRE-READY transition" obligation (per batch-14 §6(a)) is **pre-included** at L9-decies via U-RT-85 (the close-evidence unit). This is the correct cluster-design discipline per `[[h-t-cp-21-batch-15-down-classification]]` §6(a) verification-shape generalization — future operator-opt-in RETIRE-READY substitutions should pre-include their close-evidence unit at cluster authoring time. L9-decies follows the U-RT-82 + U-RT-86 precedents (Memory tool + MCP client) of pre-including a close-evidence unit at cluster authoring.

**Cite-precision audit:** all v2.17 cites against runtime spec point at **v1.18** (latest filed version per `Project_Workflow_v1_8.md` §7.4 use-latest-version body-citation-alignment clause; v1.18 committed at `1707867` in this worktree, predecessor v1.17 preserved verbatim by reference). Cross-axis cites: CP spec v1.11 §25 at latest filed version; Meta-Arch v1.5 §7.7 at latest filed version; OD spec v1.9 §C-OD-29.1 at latest filed version (referenced as adjacent context at U-RT-85 AC #6 stage-ordering verification — not a direct dependency). No invented `§` pins; no inferred cites.

**Already-landed cluster-boundary consumption cites:**
- CP spec v1.11 §25 `ConcreteValidatorFramework` body at `harness-cp/src/harness_cp/validator_framework.py:130/303/323/361` (per `[[fork-validator-composer-arc-stage-4-absence]]` §1.1 grep-verified inventory) — consumed at U-RT-84 + U-RT-85 type-narrowing + opt-in branch construction baseline.
- CP spec v1.11 §25.1 `Validator` + `ValidatorFramework` Protocol envelope schemas at `harness-cp/src/harness_cp/validator_framework_types.py:192/211` — consumed at U-RT-84 import + Protocol-conformance enforcement.
- CP spec v1.11 §25.2 `ValidatorFailClass` 5-class enum at `harness-cp/src/harness_cp/validator_framework_types.py:69` — consumed at U-RT-85 outcome-routing exercise.
- CP spec v1.11 §25.3.3.4 `workflow_driver.py:668` post-dispatch hook (existing at HEAD per U-CP-61 closure `9b009d3`) — consumed at U-RT-85 True-arm firing assertion; **not modified by L9-decies** (the hook contract is preserved verbatim per spec v1.18 §14.13.5 invariant 4).

---

## §4 — Coherence pass

Per `implementation-planner` SKILL.md §5 step 9. Verifying U-RT-83, U-RT-84, U-RT-85 against the four sub-disciplines at §4:

### U-RT-83

1. **Atomicity (§3 four criteria).**
   - 3.1 Single coherent change ✓ — one RuntimeConfig field + one empty-marker dataclass + one module
   - 3.2 Single focused session ✓ — ~1-hour implementation including module-organization + Pydantic v2 frozen-model validation testing
   - 3.3 Independently testable ✓ — RuntimeConfig instantiation + ValidatorFrameworkConfig.default() construction verifiable standalone
   - 3.4 Coherent rollback boundary ✓ — one commit revertible

2. **Spec-traceability (§4.2).** Cites 2 contract sections by ID + section: runtime spec v1.18 §3 C-RT-02 + §14.13.1. All verified against `design-substrate/Spec_Harness_Runtime_v1.md` at HEAD `1707867`. ✓

3. **Dependency-awareness (§4.3).** Declares (none) — foundational at L9-decies. ✓

4. **Implementation-grade-detail (§4.4).** Names files (`harness-runtime/src/harness_runtime/types.py` + new `harness-runtime/src/harness_runtime/validator_framework_config.py`); 2 signatures (RuntimeConfig field + ValidatorFrameworkConfig dataclass); 6 ACs each independently verifiable. Does NOT introduce a library not in spec. Does NOT extend the specification (empty-marker shape preserved verbatim from spec §14.13.1). ✓

### U-RT-84

1. **Atomicity (§3 four criteria).**
   - 3.1 Single coherent change ✓ — one factory + one stage-4 wiring + one HarnessContext field-type narrowing + one fail-class enum addition (all bound together by the C-RT-23 binding-chain contract)
   - 3.2 Single focused session ✓ — ~2-3-hour implementation including stage-4-ordering integration test + pyright validation
   - 3.3 Independently testable ✓ — once U-RT-83 lands, U-RT-84's AC can be verified standalone (factory invocation, stage-4 ordering, fail-class enum addition all testable without U-RT-85)
   - 3.4 Coherent rollback boundary ✓ — one commit revertible (factory module + stage-4 invocation site + types.py amendments + fail-class enum amendment all bound together by the binding-chain contract)

2. **Spec-traceability (§4.2).** Cites 5 contract sections by ID + section: runtime spec v1.18 §14.13.1 + §14.13.2 + §14.13.3 + §14.13.4 + §14.13.5 + §4 C-RT-04. All verified against `design-substrate/Spec_Harness_Runtime_v1.md` at HEAD `1707867`. ✓

3. **Dependency-awareness (§4.3).** Declares within-cluster dep [U-RT-83] + cluster-boundary deps [U-CP-58, U-CP-59, U-CP-60] + cluster-boundary deps [bootstrap stage-4 OD carriers — pre-cluster-7 L0 foundational units]. DAG acyclic per §2 Kahn verification. ✓

4. **Implementation-grade-detail (§4.4).** Names files (4 — factory module + stage-4 module + types.py amendments + fail-class enum module); 4 signatures (factory + HarnessContext field + fail-class enum + sub-routine surfaces); 8 ACs each independently verifiable. AC #3 explicitly enumerates the two implementer-discretion options (i) NotImplementedError + (ii) minimal construction body per `[[halt-route-split-AC-pattern]]` precedent (mirrors U-RT-80 + U-RT-81 deferred-callback-via-spec-prose ACs). Does NOT introduce a library not in spec (CP-axis import at `harness_cp.validator_framework_types` is the established Protocol-surface import path per CP spec v1.11). Does NOT extend the specification (§14.8.2 deferrals preserved verbatim per AC #7 invariant 4). ✓

### U-RT-85

1. **Atomicity (§3 four criteria).**
   - 3.1 Single coherent change ✓ — one e2e test module exercising the binding chain produced by U-RT-83 + U-RT-84
   - 3.2 Single focused session ✓ — ~1-2-hour implementation including fixture authoring + pytest-fixture lifecycle
   - 3.3 Independently testable ✓ — once U-RT-83 + U-RT-84 land, U-RT-85's AC can be verified standalone (full bootstrap via `harness_runtime.api.run(...)` + workflow exercise + assertion fan-out)
   - 3.4 Coherent rollback boundary ✓ — one commit revertible

2. **Spec-traceability (§4.2).** Cites 5 contract sections by ID + section: runtime spec v1.18 §14.13.6 + §14.13.5 + Meta-Arch v1.5 §7.7 X-AL-2 + batch-14 §6(a) close pattern + batch-16 §6 verification-shape sharpening. All verified against `design-substrate/Spec_Harness_Runtime_v1.md` + `Phase_7_Meta_Architecture_v1.md` + `.harness/phase-7d-retirement-events-batch-{14,16}.md` at HEAD. ✓

3. **Dependency-awareness (§4.3).** Declares within-cluster deps [U-RT-83, U-RT-84] + cluster-boundary deps [U-CP-58, U-CP-59, U-CP-60, U-CP-61]. DAG acyclic per §2 Kahn verification. ✓

4. **Implementation-grade-detail (§4.4).** Names file (`harness-runtime/tests/integration/test_u_rt_85_validator_framework_e2e.py`); 2 test function signatures; 8 ACs each independently verifiable. Three test-substrate mechanism options enumerated for implementer FM-2 selection (mechanism α recommended default). AC #5 explicitly enforces composer-depth parity with U-RT-82 + U-RT-86 close-pattern shape (real bootstrap via `harness_runtime.api.run(...)`, NOT `_FakeCtx`); this is the verification-shape discipline per batch-16 §6 sharpening. Does NOT introduce a library not in spec. Does NOT extend the specification. ✓

All four sub-disciplines pass at U-RT-83, U-RT-84, U-RT-85. Cluster-level coherence verified.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_17.md` |
| Version | v2.17 |
| Filing event | Spec-revision-driven plan revision — NEW L9-decies linear-chain cluster (3 units: U-RT-83 + U-RT-84 + U-RT-85) absorbs runtime spec v1.17 → v1.18 §14.13 C-RT-23 NEW contract per `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` §3.1 Reading A operator-ratified 2026-05-24 (post-batch-16 close at HEAD `1c55138`; spec v1.18 committed at `1707867` in this worktree). 2026-05-24 |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_16.md` (v2.16 substantive content preserved verbatim outside the additive L9-decies cluster authoring) |
| New units | 3 — U-RT-83 (RuntimeConfig field + ValidatorFrameworkConfig empty-marker sub-model), U-RT-84 (materialize_validator_framework_stage factory + stage-4 wiring + HarnessContext field type narrowing + RT-FAIL-VALIDATOR-STAGE-MATERIALIZE fail class), U-RT-85 (real-bootstrap e2e against operator-supplied ValidatorFramework instance) |
| Revised units | 0 at this plan (all v2.16 units preserved verbatim) |
| Cluster | NEW L9-decies cluster appended (linear-chain DAG U-RT-83 → U-RT-84 → U-RT-85); L9-novies + L9-octies + L9-septies + L9-sexies + all earlier clusters preserved verbatim |
| Cross-axis dependencies | unchanged from v2.16. L9-decies adds 0 new CXA edges — U-RT-84 + U-RT-85 consume already-landed CP-axis carriers (CP spec v1.11 §25 ConcreteValidatorFramework + Validator + ValidatorFramework Protocol + ValidatorFailClass enum) per existing CXA-declared composition seams. CXA v2.8 unchanged per fork doc §5. |
| DAG verification | Kahn-acyclic; 7 new cluster-boundary edges consumed (all targeting already-landed cluster 10-CP-A units U-CP-58/59/60/61); 3 new within-cluster edges (linear chain U-RT-83 → U-RT-84 → U-RT-85); ∅ remaining edges within L9-decies (linear-chain trivially complete). |
| Coverage verification | L9-decies units cite contract sections across runtime spec v1.18 (§3 + §4 + §14.13.1 + §14.13.2 + §14.13.3 + §14.13.4 + §14.13.5 + §14.13.6) + Meta-Arch v1.5 §7.7 X-AL-2 + CP spec v1.11 §25 + batch-14 §6(a) close pattern + batch-16 §6 verification-shape sharpening; all verified against `design-substrate/` + `.harness/` at HEAD; no spec-shaped gap surfaced; no `Phase_7_Class_N_Tension` filing required. |
| Mechanism discretion | U-RT-84 ACs accommodate (i) NotImplementedError opt-in branch OR (ii) minimal construction body per `[[halt-route-split-AC-pattern]]` precedent. U-RT-85 ACs accommodate α (recommended default: in-process fixture with single no-op PASS-returning Validator) / β (richer fixture exercising PASS + PERMANENT_FAIL) / γ (env-var-gated fixture path) per FM-2 no-extension discipline. |
| Retirement-batch absorption owed | batch-17: H_T-CP-21 PARTIAL → RETIRE-READY (post-U-RT-84 stage-factory landing per spec §14.13.6) → RETIRED (post-U-RT-85 e2e exercise per batch-14 §6(a) close pattern + batch-16 §6 verification-shape sharpening). Restores CP-21 from batch-15 DOWN-classification per `[[h-t-cp-21-batch-15-down-classification]]` Reading A resolution path. |
| Date | 2026-05-24 |
