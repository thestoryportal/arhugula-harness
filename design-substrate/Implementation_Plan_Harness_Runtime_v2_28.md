# Implementation Plan — Harness Runtime v2.28

## Change-note (v2.27 → v2.28)

**Scope of revision.** Substantive amendment authoring NEW L9-quindecies 3-unit linear-chain cluster (U-RT-99 / U-RT-100 / U-RT-101) decomposing runtime spec v1.31 → v1.32 NEW §14.17 C-RT-27 `SkillActivationSpanEmitter` + `SkillActivationHook` contract surface per `.harness/class_1_fork_as_8d_skill_activation_surface_absence.md` Reading B Q-set operator ratification 2026-05-28. Closes H_T-AS-8d substitution retirement criterion B at structural-only-met level via factory wiring + 3 hook binding sites at production (per Q2=(d) hybrid + Q4=(q) NEW module ratifications). NO new contract addition beyond C-RT-27; NO new fail class beyond `RT-FAIL-SKILL-ACTIVATION-STAGE-MATERIALIZE`; ZERO cross-axis cascade per Q5=(β) ratification. Co-published with runtime spec v1.32 + AS spec v1.7 footer + harness-runtime + harness-cp impl + AS-8d retirement gate refresh (STILL-BOUNDED → RETIRE-READY) + workspace `CLAUDE.md` row bumps + fork doc Status RATIFIED → ✅ FULLY-APPLIED. 2026-05-28.

**Source of fix.** Runtime spec v1.31 → v1.32 NEW §14.17 + AS spec v1.7 §14.4 footer publication this arc + `.harness/class_1_fork_as_8d_skill_activation_surface_absence.md` Q-set operator ratification 2026-05-28: Q1=(B) IN-SCOPE-MVP / Q2=(d) hybrid all 3 hooks / Q3=(i) preserve Claude Code taxonomy / Q4=(q) NEW module per Memory-tool precedent / Q5=(β) NO new CXA edge.

**v2.27 substantive content preserved verbatim.** All v2.27 in-place U-RT-02 amendment + v2.26 NEW §6 L9-quaterdecies cluster (U-RT-96/97/98) + v2.25/v2.26 §7.1 + §7.3 + all prior cluster bodies PRESERVED VERBATIM. v2.28 adds the L9-quindecies cluster as NEW §1.

**Cluster shape (3-unit linear binding-chain per L9-quaterdecies + L9-decies precedent).**

### §1 (NEW at v2.28) — L9-quindecies cluster (U-RT-99 / U-RT-100 / U-RT-101)

#### U-RT-99 — Carrier substrate (SkillActivationMode + SkillActivationHook + SkillActivationHookConfig + SkillManifest extension)

- **Implements:** Runtime spec v1.32 §14.17.1 — `SkillActivationMode` enum + `SkillActivationHook` Protocol + `SkillActivationHookConfig` empty-marker sub-model; PLUS SkillManifest extension at `lifecycle/skills.py` adding `version_sha: str` + `body_tokens: int` fields per §14.17.5 invariant 7 + §14.17.7 deferred-to-discretion.
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/skill_activation.py` (NEW per Q4=(q)) + `harness-runtime/src/harness_runtime/lifecycle/skills.py` (EXTEND — SkillManifest +2 fields + computation at load).
- **Signatures:**
  - `class SkillActivationMode(StrEnum)` with 3 values per Q3=(i): `FRONTMATTER_ONLY = "frontmatter_only"`, `TOOL_SEARCH = "tool_search"`, `FILESYSTEM_READ = "filesystem_read"`.
  - `@runtime_checkable class SkillActivationHook(Protocol)` with 2 methods: `select_for_workflow_init(loaded_skills, workflow_id) -> Iterable[SkillID]` + `select_for_llm_dispatch(loaded_skills, workflow_id, step_index) -> Iterable[SkillID]`.
  - `@dataclass(frozen=True) class SkillActivationHookConfig` (empty-marker; no fields per CP-22/CP-21 precedent).
  - `class SkillManifest(BaseModel)` gains `version_sha: str` (git content hash; computed via `hashlib.sha1` over `b"blob " + str(len(content)) + b"\0" + content` byte sequence per §14.17.7 deferred-discretion default) + `body_tokens: int` (estimate via `len(body) // 4` per §14.17.7 default heuristic).
  - `def load_skills_from_dir(skills_dir: Path) -> dict[SkillID, Skill]` body extended to compute version_sha + body_tokens at load.
- **Depends on:** (no within-cluster predecessors; L0).
- **ACs:**
  1. `SkillActivationMode` StrEnum declares 3 members with byte-exact string values preserving AS spec v1.7 §14.4 Claude Code taxonomy.
  2. `SkillActivationHook` Protocol declares 2 query methods with documented hook-to-enum mapping (workflow_init ↔ FRONTMATTER_ONLY; llm_dispatch ↔ TOOL_SEARCH).
  3. `SkillActivationHookConfig` empty-marker frozen dataclass; sibling-shape to `ValidatorFrameworkConfig`/`PauseResumeProtocolConfig`/`WebhookDeliveryComposerConfig`.
  4. `SkillManifest` Pydantic BaseModel gains `version_sha` + `body_tokens` fields (frozen + extra=forbid preserved).
  5. `load_skills_from_dir` computes `version_sha` via git-content-hash recipe (`hashlib.sha1` over canonical git-blob byte sequence; byte-exact-identical to `git hash-object <path>` output).
  6. `load_skills_from_dir` computes `body_tokens` via `len(body) // 4` heuristic; value is non-negative int.
- **Tests:** `test_skill_activation_mode_three_values_byte_exact`, `test_skill_activation_hook_protocol_two_methods`, `test_skill_activation_hook_config_empty_marker_frozen`, `test_skill_manifest_version_sha_field_present`, `test_skill_manifest_body_tokens_field_present`, `test_load_skills_computes_version_sha_byte_exact_to_git_hash_object`, `test_load_skills_computes_body_tokens_nonneg_int`.

#### U-RT-100 — Emitter + factory + stage-5 wiring + fail-class

- **Implements:** Runtime spec v1.32 §14.17.1 `SkillActivationSpanEmitter` class + §14.17.3 `materialize_skill_activation_emitter_stage` factory + §14.17.4 `RT-FAIL-SKILL-ACTIVATION-STAGE-MATERIALIZE` fail class + §14.17.5 invariants 1+3+5.
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/skill_activation.py` (EXTEND from U-RT-99) + `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py` (EXTEND — NEW factory invocation + binding) + `harness-runtime/src/harness_runtime/types.py` (EXTEND — RuntimeConfig field + HarnessContext field + _MutableHarnessContext field + freeze() propagation) + fail-class enum extension.
- **Signatures:**
  - `class SkillActivationSpanEmitter`: `__init__(self, tracer_provider)` + `def emit(self, skill_id: SkillID, mode: SkillActivationMode, workflow_id: str, skill: Skill) -> None` (opens `skill.activation` span; sets 6 attrs per AS spec §14.4; closes synchronously).
  - `class SkillActivationEmitterStageMaterializeError(Exception)` for `RT-FAIL-SKILL-ACTIVATION-STAGE-MATERIALIZE`.
  - `def materialize_skill_activation_emitter_stage(config, ctx) -> SkillActivationSpanEmitter | None`.
  - `RuntimeConfig.skill_activation_hook_config: SkillActivationHookConfig | None = None`.
  - `HarnessContext.skill_activation_emitter: SkillActivationSpanEmitter | None`.
- **Depends on:** [U-RT-99].
- **ACs:**
  1. `SkillActivationSpanEmitter.emit` opens a `skill.activation` span, sets all 6 attributes per AS spec v1.7 §14.4, closes the span. Span lifecycle is short (no nested scope).
  2. `materialize_skill_activation_emitter_stage` returns None when `config.skill_activation_hook_config is None`; binds `ctx.skill_activation_emitter = None`.
  3. When `config.skill_activation_hook_config is not None`: factory constructs `SkillActivationSpanEmitter(tracer_provider=ctx.tracer_provider)`, binds `ctx.skill_activation_emitter = emitter`, returns emitter.
  4. `RuntimeConfig.skill_activation_hook_config` field added with default `None`.
  5. `HarnessContext.skill_activation_emitter` field added.
  6. `_MutableHarnessContext` + `freeze()` propagate the new field.
  7. `RT-FAIL-SKILL-ACTIVATION-STAGE-MATERIALIZE` fail class registered + raised by factory on emitter construction failure (e.g., tracer provider unbound).
  8. Stage-5 LOOP_INIT calls the factory; sibling-of `materialize_validator_framework_stage` etc.
- **Tests:** `test_skill_activation_emitter_emit_opens_skill_activation_span`, `test_skill_activation_emitter_emit_sets_all_six_attributes`, `test_materialize_skill_activation_emitter_stage_returns_none_when_config_none`, `test_materialize_skill_activation_emitter_stage_constructs_emitter_when_config_present`, `test_runtime_config_skill_activation_hook_config_default_none`, `test_harness_context_skill_activation_emitter_field_present`, `test_materialize_raises_skill_activation_stage_materialize_on_failure`, `test_stage_5_loop_init_calls_skill_activation_factory`.

#### U-RT-101 — 3 hook binding sites at production + AS-8d retirement gate refresh

- **Implements:** Runtime spec v1.32 §14.17.2 hook-1 (per-workflow-init) + hook-2 (per-LLM-dispatch) + hook-3 (operator-explicit) + §14.17.5 invariants 2+3+4+6+7 + §14.17.6 retirement implications.
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` (EXTEND — NEW per-LLM-dispatch hook binding pre-LLM-call) + `harness-cp/src/harness_cp/workflow_driver.py:execute_workflow` (EXTEND — NEW per-workflow-init hook binding post-bootstrap-stage-6 pre-first-step) + `harness-runtime/src/harness_runtime/types.py` (EXTEND — HarnessContext gains `activate_skill(skill_id)` method) + `harness-as/CLAUDE.md` H_T-AS-8d row refresh.
- **Signatures:**
  - At `lifecycle/llm_dispatch.py`: before LLM call, if `ctx.skill_activation_emitter is not None` AND `operator_hook is not None`: query `operator_hook.select_for_llm_dispatch(ctx.skills.keys(), workflow_id, step_index)` + emit `(skill_id, SkillActivationMode.TOOL_SEARCH, workflow_id)` for each selected.
  - At `workflow_driver.py:execute_workflow`: at entry (post-bootstrap), if `ctx.skill_activation_emitter is not None` AND `operator_hook is not None`: same pattern with `select_for_workflow_init` + `FRONTMATTER_ONLY`.
  - At `HarnessContext.activate_skill(skill_id: SkillID) -> None`: if emitter None silent-skip per §14.17.2 hook-3 recommendation; validate skill_id present in `ctx.skills` (raise `UnknownSkillError` on miss); emit `(skill_id, SkillActivationMode.FILESYSTEM_READ, workflow_id)`.
- **Depends on:** [U-RT-100].
- **ACs:**
  1. Per-LLM-dispatch hook fires AT `lifecycle/llm_dispatch.py` BEFORE the LLM call; emits one `skill.activation` span per skill returned by `operator_hook.select_for_llm_dispatch(...)` with `activation_mode = "tool_search"`.
  2. Per-workflow-init hook fires AT `workflow_driver.py:execute_workflow` AFTER bootstrap completion BEFORE first step dispatch; emits one span per skill returned by `select_for_workflow_init(...)` with `activation_mode = "frontmatter_only"`.
  3. Operator-explicit `HarnessContext.activate_skill(skill_id)` method emits exactly one span with `activation_mode = "filesystem_read"`.
  4. All 3 sites no-op silently when `ctx.skill_activation_emitter is None` (operator opt-out path; no spans, no exception).
  5. `HarnessContext.activate_skill(skill_id)` raises `UnknownSkillError` when `skill_id not in ctx.skills`.
  6. Spans emitted carry the AS spec v1.7 §14.4 6-attribute namespace (`skill.id` + `skill.name` + `skill.version_sha` + `skill.frontmatter.version` + `skill.body_tokens` + `skill.activation_mode`).
  7. Operator-supplied `SkillActivationHook` Protocol implementation supply mechanism: implementation discretion per §14.17.7 — recommended via `run_bootstrap(..., skill_activation_hook=hook)` parameter OR via context attribute set pre-bootstrap. At U-RT-101: bundle the hook reference at `RuntimeConfig.skill_activation_hook_config.hook` future extension OR via threading on `HarnessContext`.
  8. **e2e test:** real bootstrap with operator-bound `SkillActivationHookConfig` + operator hook supplied; load fixture skills; assert all 3 hook sites emit `skill.activation` spans (one per loaded skill + activation mode).
  9. **`harness-as/CLAUDE.md` H_T-AS-8d row:** STILL-BOUNDED → RETIRE-READY with cite to runtime spec v1.32 §14.17 + producer-site at `harness-runtime/src/harness_runtime/lifecycle/skill_activation.py` + 3 hook binding sites. Operator-opt-in note mirror-of CP-18/CP-21/CP-22/RT-94 RETIRE-READY pattern.
- **Tests:** `test_per_workflow_init_hook_emits_frontmatter_only_span`, `test_per_llm_dispatch_hook_emits_tool_search_span`, `test_activate_skill_emits_filesystem_read_span`, `test_all_hook_sites_no_op_when_emitter_none`, `test_activate_skill_raises_unknown_skill_error`, `test_span_carries_all_six_skill_attributes`, `test_e2e_real_bootstrap_with_operator_hook_emits_all_three_modes`.

### §2 (NEW at v2.28) — DAG topology + coverage matrix delta

**Within-L9-quindecies edges (3 nodes, 2 edges, acyclic linear chain):**
- U-RT-99 (carrier substrate) → U-RT-100 (emitter + factory)
- U-RT-100 → U-RT-101 (hook binding sites + retirement gate refresh)

**Cluster-boundary edges:** L9-quindecies cluster opens at L0-equivalent (U-RT-99 has no within-axis predecessors beyond v2.27-and-earlier landed types/protocols). Cross-axis edges: U-RT-101 at L2 depends on harness-cp `workflow_driver.execute_workflow` modifications (within-cross-package; not within-axis dependency).

**Coverage matrix delta:** NEW row `C-RT-27 §14.17 (SkillActivationSpanEmitter + SkillActivationHook)` covered by U-RT-99 + U-RT-100 + U-RT-101.

### §3 (NEW at v2.28) — Cross-axis cascade verification

Per Q5=(β) ratification + runtime spec v1.32 §14.17.6: ZERO cross-axis cascade verified at this arc.

- CXA v2.15 — NO edge addition; convention-level cite at AS spec footer suffices.
- AS spec v1.7 — footer note co-published at §14.4 (separate file edit; not a CXA edge).
- CP spec — NO amendment owed.
- OD spec — NO amendment owed (§C-OD-08 cross-namespace ingestion already declares `skill.*` row).
- ADR / ADD / PRD — NO amendment owed.

### §4 (NEW at v2.28) — Adjacent observations

(a) **Skill activation event design is operator-discretion at MVP.** The fork doc Q1=(B) shape preserves the harder design question ("what activates a Skill at H_T?") as operator-discretion. v2.28 ships the carrier substrate + 3 hook sites + RETIRE-READY gate; the actual policy is operator-supplied. Sub-species candidate: **MVP-with-operator-discretion-policy-supply** — distinct from full-implementation arc shapes; characteristic of Reading B operator-opt-in landings.

(b) **Hook implementation supply mechanism unresolved at MVP.** Per §14.17.7: how the operator supplies the `SkillActivationHook` Protocol implementation is implementation discretion at the landing arc. Three options enumerated (run_bootstrap parameter / singleton accessor / config sub-model field extension). v2.28 selects (a) `run_bootstrap` parameter recommended; deferred to v1.32 follow-on if needed.

(c) **`HarnessContext.activate_skill(...)` workflow_id source.** §14.17.7 enumerates 3 options; v2.28 selects (b) `ctx.current_workflow_id: str | None` field set at workflow entry. Implementation lift: U-RT-101 adds this field at HarnessContext, set at execute_workflow entry, cleared at execute_workflow exit.

**Status posture.** Proposed (v2.27) → **Proposed (v2.28)**. Unit count 96 → 99 (+3: U-RT-99 + U-RT-100 + U-RT-101).
