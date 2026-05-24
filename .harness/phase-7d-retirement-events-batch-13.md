# Phase 7d Retirement Events — Batch 13

| Field | Value |
|---|---|
| Batch number | 13 |
| Filed at | 2026-05-23 (post L9-octies cluster close `42c9a30` — Memory tool primitive decomposition 7-unit arc U-RT-76..U-RT-82) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 invoked per L9-octies cluster-close retirement-event trigger (operator request following arc merge to main 2026-05-23) |
| Predecessor batch | `phase-7d-retirement-events-batch-12.md` (2026-05-23, 1 STILL-BOUNDED → RETIRE-READY for H_T-AS-2 + 2 STILL-BOUNDED → PARTIAL for H_T-AS-4 + H_T-OD-5; cumulative 22/49 RETIRED + 3 RETIRE-READY + 10 PARTIAL = 35/49 advanced per §6) |

---

## §0 Batch context

**Status type: 1 within-tier promotion — PARTIAL → RETIRE-READY (H_T-CP-16). NO new RETIRED transitions. Cumulative pipeline-advanced count unchanged at 35/49 (71.4%); bucket composition shifts +1 RETIRE-READY / −1 PARTIAL.**

This batch records a single within-tier promotion for **H_T-CP-16** (Memory primitives + `memory.*` namespace consumption) following the L9-octies cluster close at `42c9a30` (2026-05-23) — 7-unit Memory tool primitive decomposition arc (U-RT-76 Protocol + sub-model + typed exceptions → U-RT-77 `LocalFilesystemMemoryToolBackend` → U-RT-78 `MemoryToolRegistry` → U-RT-79 RuntimeConfig + HarnessContext field landings → U-RT-80 stage-5 factory + `_REQUIRED_FIELDS` flip → U-RT-81 C-RT-15 §14.5.1 callback-injection composer-step at `llm_dispatch.py` → U-RT-82 e2e local-fs + real Anthropic API exercise).

The L9-octies arc materialized the CP-side runtime composer that batch-11 §2.3 flagged as the PARTIAL → RETIRE-READY gate:

> H_T-CP-16 PARTIAL → RETIRE-READY transition gates on CP-side runtime composer landing that:
> 1. Consumes the AS-axis Memory tool primitive at workflow execution time (e.g., a memory.read or memory.write step in a workflow manifest entry)
> 2. Emits the `memory.*` 6-attribute namespace per C-AS-14 §14.7 on a memory-tool-call span
> 3. Routes through workflow_driver or sub_agent_dispatch composer

All 3 gate conditions satisfied at L9-octies close (see §1.3 below).

Per the operator-ratified runtime-only substitution-site reading at `.harness/phase-7d-retirement-ledger-v2.md` §2.1 + line-33 strict-reading discipline + the operator-opt-in RETIRE-READY pattern established at batch-10 H_T-CP-18 + batch-11 H_T-CP-21 + batch-12 H_T-AS-2:

> RETIRE-READY = (criterion A MET) ∧ (criterion B structural-MET; operational gated on operator-supplied config or operator-supplied step payload).

Under that discipline, H_T-CP-16 transitions PARTIAL → RETIRE-READY: production runtime composer in place at `RuntimeLLMDispatcher.dispatch` body; production invocation gated on operator-supplied step payload containing the Anthropic Memory tool definition (`type == "memory_20250818"`).

H_T-CP-17 (Files API consumer) explicitly stays PARTIAL per runtime spec v1.17 §14.C ratified Files-arc-deferred scope. No transition this batch.

**Conclusion (preview):** 0 new RETIRED transitions; cumulative **22/49 RETIRED** (44.9%) unchanged. **1 new RETIRE-READY transition** (H_T-CP-16 — joins H_T-CP-18 batch-10 + H_T-CP-21 batch-11 + H_T-AS-2 batch-12, now **4 substitutions** in the operator-opt-in RETIRE-READY pattern). **−1 PARTIAL** (H_T-CP-16 promoted out). Pipeline advanced (RETIRED + RETIRE-READY + PARTIAL): **35/49 = 71.4%** (unchanged from batch-12; bucket composition shifts).

---

## §1 H_T-CP-16 PARTIAL → RETIRE-READY

| Field | Value |
|---|---|
| Substitution ID | H_T-CP-16 |
| Primitive | Memory primitives + `memory.*` namespace consumption (CP-side runtime consumer of Anthropic Memory tool client-side primitive per ADR-D3 v1.2 §1.1 #11) |
| Substituted H_E surface | "`CLAUDE.md` hierarchy as memory; no `memory.*` namespace emission" (Meta-Arch v1.5 §5.4 row H_T-CP-16) |
| Prior status | PARTIAL per batch-11 §2 (2026-05-23 — STILL-BOUNDED → PARTIAL on Meta-Arch v1.4 re-anchoring to AS-axis carrier cite U-AS-28 + U-AS-31; criterion-A met at AS library layer; criterion-B structural-only-met-as-library) |
| Transition this batch | PARTIAL → **RETIRE-READY** |
| Triggering arc | L9-octies cluster close `42c9a30` (2026-05-23 — `b6d3c4e`..`42c9a30`; 7-unit Memory tool primitive decomposition arc per fork doc `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` §16 RATIFIED-AMENDED Memory-only scope per §14.C; runtime spec v1.16 → v1.17 + AS spec v1.4 → v1.5 + runtime plan v2.13 → v2.15 P6-CK absorption pass + cluster execution at this arc) |

### §1.1 Criterion A (cited unit IDs landed) — MET

Per Meta-Architecture v1.5 §5.4 row H_T-CP-16: `U-AS-28 + U-AS-31` (verified MET at batch-11 §2.1).

**Augmented cite shape (operator-discretion follow-on per §6(a) observation below).** The L9-octies arc materialized the runtime composer that the prior Meta-Arch cite did not name. The runtime composer carriers U-RT-76..U-RT-82 are the production CP-side surface that satisfies criterion-B. Strictly under existing v1.5 cite, criterion-A remains MET via U-AS-28 + U-AS-31 alone (the runtime composer was the criterion-B gate, not criterion-A); a future Meta-Arch v1.6 amendment MAY add the runtime composer carriers to the §5.4 row H_T-CP-16 cite for cite-shape completeness.

| Unit | Landing commit | Surface | Verification at HEAD `42c9a30` |
|---|---|---|---|
| **U-AS-28** | AS plan v1 cluster L2 close (Memory tool primitive #11 per AC #6 — combined primitive declaration body) | Memory tool primitive declaration + filesystem-loading binding per C-AS-13 §13.1 row 11; `MemoryToolStorageBackend` enum at `harness-as/src/harness_as/anthropic_graceful_degradation.py:88` | ✓ grep verified |
| **U-AS-31** | `8002dbc` (`feat(as): land U-AS-31 — six Anthropic-primitive attribute namespaces`) + Class 1 fork resolution at `59c5d42` | `memory.*` 6-attribute namespace per C-AS-14 §14.7 (`memory.operation.kind`, `memory.path`, `memory.backend`, `memory.bytes_read`, `memory.bytes_written`, `memory.context_editing_active`) + §14.7 v1.5 producer-site footer note repointing to runtime spec v1.17 §14.5.1 + §14.12 callback-invocation sites | ✓ grep verified |

**Criterion A status: MET.** Both AS-axis carriers materialized at the AS-axis library layer; this state was already MET at batch-11 §2.1 filing.

### §1.2 Criterion B (substituted H_E surface no longer invoked) — STRUCTURAL MET; OPERATIONAL GATED

Per X-AL-2: "Retirement = (cited unit IDs landed) ∧ (substituted H_E surface no longer invoked at substitution site). **Both conditions required.**"

**Substitution site analysis at HEAD `42c9a30`.** H_T-CP-16's substituted H_E surface is the "`CLAUDE.md` hierarchy as memory; no `memory.*` namespace emission" convention. The H_T-side substitution-target surface is the runtime LLM-dispatch composer that consumes the Anthropic Memory tool client-side primitive via the `MemoryToolStorageBackendProtocol` callback-injection inner loop with `memory.*` namespace emission at each storage-backend callback span boundary.

**Strict structural reading** ("is the substituted H_E surface — `CLAUDE.md` hierarchy as memory + no `memory.*` namespace emission — still the production-path mechanism for memory primitives?"):

Empirical grep at HEAD `42c9a30`:

```
$ grep -rnE 'memory_20250818|MemoryToolStorageBackend|memory\.operation' \
    harness-runtime/src harness-cp/src harness-cxa/src harness-as/src \
    2>/dev/null | grep -v __pycache__ | grep -v test | wc -l
~30 production-callsite hits across the runtime composer, registry, factory, and AS-axis carrier
```

The harness runtime now invokes the Memory tool storage-backend Protocol at production LLM-dispatch path when `step.step_payload.tools` contains `{"type": "memory_20250818", ...}`. The full inner loop emits one `memory.operation` span per CRUD callback invocation per AS spec v1.5 §14.7 + runtime spec v1.17 §14.12.2 invariant 2.

**Structural reading: MET.** ✓

**End-to-end operational reading** ("does the substitution site terminally invoke the Memory tool backend and emit a `memory.*` namespace span at production execution path?"):

Bounded carry-forward — at default config (`step.step_payload.tools=None` OR memory tool absent from `payload.tools`), the production composer is in place but no memory call exercises the inner loop:

```python
# llm_dispatch.py:319 (anthropic branch)
if (
    self.memory_tool_registry is not None
    and self.deployment_surface is not None
    and step_has_memory_tool(payload.tools)  # ← default: False (tools=None or no memory tool)
):
    response, usage_attrs, cache_attrs = await _dispatch_anthropic_with_memory(...)
else:
    response, usage_attrs, cache_attrs = await _dispatch_anthropic(adapter, model, payload)
```

With default workflow steps (no memory tool in payload), the inner loop is not exercised end-to-end at production runtime. Production exercise requires:

1. Operator-supplied workflow step with `payload.tools` containing the Anthropic Memory tool definition (`{"type": "memory_20250818", "name": "memory"}`)
2. Operator-supplied `extra_headers={"anthropic-beta": "context-management-2025-06-27"}` per ADR-D3 v1.2 §1.1 #11
3. Real Anthropic API access at the runtime's network boundary (gated on `ANTHROPIC_API_KEY` or equivalent credential substrate)
4. A workflow execution that triggers the LLM to invoke a Memory tool command (`view` / `create` / `delete` / `str_replace` / `insert`)

**Operational reading: GATED on operator config + step payload + external Anthropic API availability.** ⚠

**Both readings disposition: structural MET; operational GATED.** This is the RETIRE-READY criterion-B pattern introduced at batch 8 (H_T-CP-20) + batch 10 (H_T-CP-18) + batch 11 (H_T-CP-21) + batch 12 (H_T-AS-2). The wire is in place at the H_T design surface (5-CRUD-callback Protocol + LocalFilesystemMemoryToolBackend implementation + registry + stage-5 factory + composer-step amendment + e2e test); what's deferred is live exercise against the real Anthropic API.

### §1.3 Production callsite invocation evidence

Production wrap chain at HEAD `42c9a30`:

```
Bootstrap stage 5 LOOP_INIT (U-RT-80 factory + U-RT-81 dispatcher binding):

  # U-RT-80 stage-5 factory body at memory_tool_registry_factory.py
  await materialize_memory_tool_registry_stage(config, ctx)
    # 4-step composition per spec v1.17 §14.12.3:
    #   step 1: resolve configured MemoryToolStorageBackend enum
    #           (config.memory_tool_backend_config override OR
    #            harness_as.anthropic_graceful_degradation.memory_tool_storage_backend
    #            resolver default — picks FILESYSTEM at LOCAL_DEVELOPMENT)
    #   step 2: construct backend impl (LocalFilesystemMemoryToolBackend
    #           rooted at config.repository_root / ".harness/memories"
    #           for FILESYSTEM enum; raises RT-FAIL-MEMORY-BACKEND-RESOLUTION
    #           with §14.D pointer for other enum values)
    #   step 3: Protocol-conformance enforcement (@runtime_checkable +
    #           per-method callable sweep per §14.12.5 invariant 2)
    #   step 4: construct MemoryToolRegistry(backend=..., configured_backend=...)
    #           + bind to ctx.memory_tool_registry

  # U-RT-81 composer-step binding at llm_dispatch.py
  bare_dispatcher = materialize_llm_dispatcher_stage(
    providers,
    tracer_provider,
    ...,
    memory_tool_registry=ctx.memory_tool_registry,  # ← bound this arc
    deployment_surface=config.deployment_surface,    # ← bound this arc
  )

Production LLM dispatch (llm_dispatch.py:319 anthropic branch):

  if step_has_memory_tool(payload.tools):
    # Mechanism β harness-authored inner loop per spec v1.17 §14.5.1
    response = await execute_with_memory_callbacks(
      adapter=adapter,
      model=model,
      messages_create_kwargs=kwargs,
      backend=registry.resolve_backend(deployment_surface),
      backend_enum=registry.configured_backend,
      tracer=tracer,
      context_editing_active=derive_context_editing_active(payload.params),
    )
    # Loops: messages.create → if stop_reason == "tool_use" + memory tool_use blocks:
    #   for each tool_use block:
    #     with tracer.start_as_current_span("memory.operation") as span:
    #       span.set_attribute("memory.operation.kind",
    #         <view→read | create→write | str_replace→update |
    #          insert→update | delete→delete>)
    #       span.set_attribute("memory.path", path)
    #       span.set_attribute("memory.backend", backend_enum.value)
    #       span.set_attribute("memory.bytes_read", n)        # optional
    #       span.set_attribute("memory.bytes_written", n)     # optional
    #       span.set_attribute("memory.context_editing_active", bool)
    #       if kind in {"write", "update", "delete"}:
    #         span.set_attribute("sampling.head_rate", 1.0)  # audit-floor per AS §14.8
    #       result = await backend.<method>(...)  # 5-CRUD Protocol invocation
    #       # On MemoryPathViolationError / MemoryCallbackIOError: propagate verbatim
    #       # → driver try/except at workflow_driver.py:618-635 → step-failure
  else:
    response = await _dispatch_anthropic(adapter, model, payload)  # unchanged path
```

Verification evidence:

- `grep -n 'step_has_memory_tool' harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` → line 320 (branch detection) ✓
- `grep -n 'execute_with_memory_callbacks' harness-runtime/src/harness_runtime/lifecycle/memory_tool_dispatch.py` → composer body ✓
- `grep -n 'memory.operation' harness-runtime/src/harness_runtime/lifecycle/memory_tool_dispatch.py` → span emission ✓
- `grep -n 'class LocalFilesystemMemoryToolBackend' harness-runtime/src/harness_runtime/lifecycle/memory_tool_filesystem.py` → backend impl ✓
- `grep -n 'class MemoryToolRegistry' harness-runtime/src/harness_runtime/lifecycle/memory_tool_registry.py` → registry ✓
- `grep -n 'materialize_memory_tool_registry_stage' harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py` → stage-5 invocation ✓
- `grep -n 'memory_tool_registry: Any = None' harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` → dispatcher field ✓
- 2864/2864 tests green workspace-wide (+ 3 e2e skipped pending ANTHROPIC_API_KEY) ✓

**3-gate verification per batch-11 §2.3 RETIRE-READY criterion:**

1. ✓ **Consumes the AS-axis Memory tool primitive at workflow execution time.** When `step.step_payload.tools` contains memory_20250818 + step is INFERENCE_STEP, the inner loop invokes `backend.<view|create|str_replace|insert|delete>` per LLM tool_use block per spec §14.5.1 step 3.

2. ✓ **Emits the `memory.*` 6-attribute namespace per C-AS-14 §14.7 on a memory-tool-call span.** `_emit_memory_operation_span` opens `memory.operation` span carrying all 6 attributes + audit-floor `sampling.head_rate` for mutation kinds per AS spec §14.8 audit-floor commitment.

3. ✓ **Routes through workflow_driver or sub_agent_dispatch composer.** The Memory tool inner loop is integrated at C-RT-15 `RuntimeLLMDispatcher.dispatch` body (existing INFERENCE_STEP composer); workflow_driver invokes via the existing `step_dispatchers.lookup(StepKind.INFERENCE_STEP).dispatch(binding, step, step_context=...)` Protocol path at `workflow_driver.py:619`.

All 3 gates satisfied at L9-octies close.

### §1.4 RETIRE-READY → RETIRED gate

The H_T-CP-16 RETIRE-READY → RETIRED full transition gates on end-to-end exercise of the Memory tool callback inner loop against a real Anthropic API. Specifically:

1. **Operator-bound `memory_tool_backend_config` non-default** — production deployment supplies `RuntimeConfig(memory_tool_backend_config=MemoryToolBackendConfig(backend=MemoryToolStorageBackend.FILESYSTEM))` (or one of the other enum values, but only FILESYSTEM is implemented at v2.15 per §14.D scope). Substrate: existing — `RuntimeConfig.memory_tool_backend_config` field landed at U-RT-79 per runtime plan v2.15.

2. **End-to-end Memory tool callback exercise** — integration test exercising the full path: runtime config with `memory_tool_backend_config=FILESYSTEM` → bootstrap stage-5 materializes `MemoryToolRegistry` wrapping `LocalFilesystemMemoryToolBackend` → workflow step with `step.step_payload.tools=[{"type": "memory_20250818", "name": "memory"}]` + `extra_headers={"anthropic-beta": "context-management-2025-06-27"}` → INFERENCE_STEP routes through C-RT-15 dispatcher → detect-memory-tool branch → harness inner loop calls `messages.create` → LLM emits `tool_use` block invoking `memory` `create` → harness invokes `backend.create(path, content)` → file written + `memory.operation` span emitted with `kind=write` + correct attributes → `tool_result` re-dispatched → LLM final response returned. Substrate: **U-RT-82 test module landed at L9-octies close (`42c9a30`)** but gated behind `ANTHROPIC_API_KEY` (no API key in CI; tests skip cleanly per AC #2). Live exercise pending operator-supplied credential.

3. **Spec §16 §6.C v2 C.vii local-fs scope verification** — operator exercise scope is local-filesystem backend only at this arc. S3 / ENCRYPTED_FILESYSTEM / DATABASE backend e2e tests deferred to operator-discretion follow-on retirement-batch arcs per spec §14.D ratification.

Comparable to batch 10 §1.4 (H_T-CP-18 RETIRED gates on external-MCP-server exercise) + batch 12 §1.4 (H_T-AS-2 RETIRED gates on same MCP shared substrate); H_T-CP-16 RETIRED gates on the Anthropic API key e2e exercise landing. No timeline commitment at this batch — operator-discretion timing per existing 7d retirement-event cadence.

**Per advisor reconciliation discipline (per batch 8 + 10 + 12 §1.4 patterns):** the honest classification is RETIRE-READY, not RETIRED. The wire IS in place at the H_T design surface (5-CRUD-callback Protocol + concrete filesystem backend + registry + stage-5 factory + composer-step amendment + e2e test infrastructure); what's deferred is live operational exercise against the real Anthropic API. Conservative reading preferred to avoid silent absorption of criterion-B-operational deferral.

---

## §2 H_T-CP-17 PRESERVED PARTIAL (Files arc deferred per §14.C)

| Field | Value |
|---|---|
| Substitution ID | H_T-CP-17 |
| Primitive | Files primitives + `files.*` namespace consumption (CP-side cross-axis consumer of AS-axis Files API primitive) |
| Prior status | PARTIAL per batch-11 §3 (2026-05-23) |
| Transition this batch | **NONE — preserved PARTIAL** |
| Rationale | Runtime spec v1.17 §14.C operator-ratified Files-arc-deferred scope: "NO Files API contract authoring at v1.17 — Files arc deferred indefinitely per §14.C". The fork doc `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` §16 RATIFIED-AMENDED with Memory-only scope per §6.A v2 A.iv + §14.C; H_T-CP-17 Files-consumer composer NOT authored at L9-octies arc (intentional non-coverage). Operator-discretion timing for any future Files-arc design-phase opening. |

H_T-CP-17 status unchanged at this batch. Future PARTIAL → RETIRE-READY transition gates on the Files-arc design-phase opening (currently deferred indefinitely per spec §14.C).

---

## §3 Cross-axis retirement dependency cascade

Per Meta-Architecture §6.3 (workspace `CLAUDE.md` §4 → `phase-7-substitution-retirement` skill §4):

| Cross-axis dependency | Status |
|---|---|
| §6.3.1 — H_T-CP-1 → H_T-AS-8 anthropic.* namespace emission | Unchanged — H_T-CP-1 RETIRED (batch 2); cascade discharged 2026-05-20. The L9-octies arc consumes already-emitted `anthropic.*` attributes (no new cascade activation) |
| §6.3.2 — F-CP-01 Stage 3b inversion ordering (H_T-OD-2 + H_T-CP-24 joint-landing) | Unchanged — both endpoints RETIRED (batch 2 + authoring close v1 §1); cascade FULLY DISCHARGED at U-RT-58 landing arc per batch-3 |

**No new cross-axis dependency activation at this batch.** Per fork doc `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` §5 + architect recommendation §13.6.D: **ZERO cross-axis cascade beyond the AS spec v1.5 §14.7 producer-site footer note** (co-published with the runtime spec v1.17 arc; documentary, not a new CXA edge). The L9-octies arc adds 0 new CXA edges per fork doc §5 — consumption of already-landed `MemoryToolStorageBackend` enum carrier at `harness-as` is cross-package consumption against existing carriers, NOT a new cross-axis composition seam (CXA v2.8 unchanged).

---

## §4 Cumulative status (post-batch-13)

| Bucket | Pre-batch-13 (post-batch-12) | Δ batch-13 | Post-batch-13 |
|---|---|---|---|
| RETIRED | 22/49 (44.9%) | +0 | **22/49 (44.9%)** |
| RETIRE-READY | 3 (CP-18, CP-21, AS-2) | +1 (CP-16) | **4 (CP-18, CP-21, AS-2, CP-16)** |
| PARTIAL | 10 | −1 (CP-16 promoted out) | **9** |
| STILL-BOUNDED | 14 | +0 | **14** |
| Authoring-only (out-of-scope per skill §6.3) | excluded | — | excluded |

**Per-axis CP roll-up (post-batch-13):**

| CP-axis bucket | Count | Note |
|---|---|---|
| RETIRED | 10/22 (45.5%) | Unchanged from batch-12 |
| RETIRE-READY | 3/22 (13.6%) | NEW — H_T-CP-16 joins H_T-CP-18 (batch-10) + H_T-CP-21 (batch-11) |
| PARTIAL | 7/22 (31.8%) | Was 8/22 pre-batch-13; H_T-CP-16 transitioned out |
| STILL-BOUNDED | 2/22 (9.1%) | Unchanged (H_T-CP-12 + H_T-CP-23) |

**Pipeline advanced (RETIRED + RETIRE-READY + PARTIAL):**

| Scope | Post-batch-12 | Post-batch-13 | Delta |
|---|---|---|---|
| Workspace-wide | 35/49 (71.4%) | 35/49 (71.4%) | unchanged (within-tier promotion) |
| CP-axis | 20/22 (90.9%) | 20/22 (90.9%) | unchanged (within-tier promotion) |

The within-tier promotion preserves the pipeline-advanced count; the composition shifts the H_T-CP-16 row from PARTIAL into RETIRE-READY, reflecting the structural readiness gain from L9-octies arc materializing the production runtime composer.

---

## §5 Forward-only ledger discipline preservation

Per workspace `CLAUDE.md` §4.3 forward-only ledger discipline. This batch adheres:

- Prior batch records (1..12) NOT modified
- Only new batch-13 added + per-axis CLAUDE.md §4.1 forward-state refresh
- H_T-CP-16 row at `harness-cp/CLAUDE.md` §4.1 retirement-status table updated PARTIAL → RETIRE-READY (status-column edit only; rationale + gating notes appended in-place per pattern at H_T-CP-18 + H_T-CP-21 rows; PARTIAL-bucket row count decrements 8 → 7)

---

## §6 Adjacent observations (NOT this batch's retirement event)

(a) **Meta-Arch v1.5 §5.4 row H_T-CP-16 cite-shape augmentation candidate.** The current Meta-Arch cite is `U-AS-28 + U-AS-31` (AS-axis library carriers). The L9-octies arc materialized the runtime composer carriers U-RT-76..U-RT-82 that satisfy criterion-B. A future Meta-Arch v1.6 amendment MAY add the runtime composer carriers (or the spec contracts they implement — C-RT-15 §14.5.1 + C-RT-22 §14.12) to the §5.4 row H_T-CP-16 cite for cite-shape completeness. NOT this batch's scope — criterion-B is met under the existing cite per §1.2 above. Operator-discretion follow-on at next Meta-Arch amendment arc.

(b) **H_T-CP-16 + H_T-CP-17 fork doc §16 RATIFIED-AMENDED Memory-only scope.** Fork doc `class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` §16 §6.A v2 A.iv + §14.C scope ratification: H_T-CP-16 receives full Memory-arc treatment (L9-octies); H_T-CP-17 Files arc deferred indefinitely. The asymmetry is intentional — Files arc opens only when operator authorizes a Phase-6-back-flow design extension. Memory tool was prioritized because Anthropic Memory tool is a client-side primitive per ADR-D3 §1.1 #11 (harness owns storage backend; SDK runs message loop) — directly answerable at the runtime layer; Files API is server-side (Anthropic-managed reference model with workspace-scoped resource lifecycle) — requires deeper design work for the H_T harness boundary at the workspace-scoping seam.

(c) **U-RT-82 e2e gating substrate.** The U-RT-82 test module at `harness-runtime/tests/integration/test_u_rt_82_memory_tool_filesystem_e2e.py` ships with `@pytest.mark.e2e` + `@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), ...)` module-level gating. CI runs default to skip; operator can enable with `ANTHROPIC_API_KEY` set in env. Once exercised, the test produces empirical evidence for the H_T-CP-16 RETIRED transition gate per §1.4. Coupling note: the same test exercises U-RT-77 + U-RT-78 + U-RT-80 + U-RT-81 jointly — a single passing e2e run satisfies criterion-B operational reading for all of L9-octies.

(d) **Cost-attribution under-reports memory-tool inner-loop iterations (Class 3 adjacent-defect).** The U-RT-81 inner loop invokes `messages.create` N times per dispatch (initial + per-tool-use turn until non-tool-use response). The existing `_attribute_cost_best_effort(...)` at the C-RT-15 dispatcher attributes ONLY the FINAL `messages.create` response's `usage`; intermediate-turn token consumption is unattributed. This was surfaced at the U-RT-81 commit body but NOT patched per FM-2. Future arc owes either (i) aggregate `usage` across loop iterations, or (ii) emit one cost record per inner `messages.create`. Operator-discretion timing — does NOT block the H_T-CP-16 RETIRE-READY transition (the cost-attribution concern is OD-axis observability scope, not CP-axis substitution-retirement scope).

(e) **SDK `rename` command absent from harness Protocol (FM-2 structural-decline).** Anthropic SDK's `BetaAsyncAbstractMemoryTool` exposes 6 abstract methods: `view` / `create` / `delete` / `str_replace` / `insert` / `rename`. The harness `MemoryToolStorageBackendProtocol` per runtime spec v1.17 §14.12.1 enumerates 5 callbacks (excluding `rename`). The U-RT-81 inner loop treats an LLM-emitted `rename` command as a structural-decline (returns an error `tool_result` content block to the LLM without invoking any Protocol method) per FM-2 no-extension discipline. Does NOT constitute a silent X-AL-3 H_T design extension (the omission is explicit). Future spec revision MAY add a `rename` callback if operator decides Memory tool surface should be exhaustive against SDK; OR the spec MAY document the 5-callback subset as intentional. Operator-discretion follow-on at any future runtime spec amendment arc.

---

## §7 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-13.md` |
| Batch number | 13 |
| Filed at | 2026-05-23 (post L9-octies cluster close `42c9a30` + arc merge to main) |
| Filing authority | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5; criterion-A MET (preserved from batch-11) ∧ structural-criterion-B MET (NEW at L9-octies close) for H_T-CP-16 → PARTIAL → RETIRE-READY (operational opt-in GATED per §1.4 ANTHROPIC_API_KEY e2e exercise) |
| HEAD at filing | `42c9a30` (L9-octies cluster close); 2864/2864 tests green workspace-wide + 3 e2e skipped (pending ANTHROPIC_API_KEY) |
| Predecessor | `.harness/phase-7d-retirement-events-batch-12.md` (2026-05-23, 1 RETIRE-READY + 2 PARTIAL across H_T-AS-2 + H_T-AS-4 + H_T-OD-5) |
| Successor | `.harness/phase-7d-retirement-events-batch-14.md` (TBD — likely RETIRED transitions for the 4 RETIRE-READY substitutions (CP-18, CP-21, AS-2, CP-16) at joint or staggered operator-supplied-config + external-substrate-exercise events; OR additional PARTIAL → RETIRE-READY transitions for the 9 remaining PARTIALs at future runtime composer landings) |
| Related forks | `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` (RATIFIED-AMENDED 2026-05-23 — full arc closed at L9-octies merge); `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` memory entry (status transition: gate-analysis → arc-LANDED post-this-batch) |
| MEMORY.md update owed | Update `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` reflecting the as-built shape (runtime composer arc landed, H_T-CP-16 RETIRE-READY this batch, H_T-CP-17 preserved PARTIAL per §14.C); ADD new memory entry for the L9-octies cluster traversal arc itself |

---

*End of Phase 7d retirement events batch 13. 1 PARTIAL → RETIRE-READY (H_T-CP-16). Cumulative 22/49 RETIRED + 4 RETIRE-READY + 9 PARTIAL = 35/49 advanced (71.4%, unchanged from batch-12 — within-tier promotion). NO new RETIRED transitions. H_T-CP-17 preserved PARTIAL per spec §14.C Files-arc-deferred scope. ZERO new cross-axis cascade per fork doc §5 + architect §13.6.D.*
