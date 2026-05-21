# Phase 2 Session 3 — Track A atomic-decomposition plan: `harness-runtime/`

*v2.10 — minor revision (2026-05-21). Absorbs `Spec_Harness_Runtime_v1.md` v1.11 → v1.12 Form A NOTE-form amendment per c_rt_18 MCP-workflow-initiation-topology fork operator-ratified resolution (RATIFIED at HEAD `e9b9c49`; fork-ratified commit `bd9281a`; spec-absorbed commit `7f2fee3`). Adds new sibling unit **U-RT-62** at L9-quinquies (FastMCP server hosting + `run_workflow` MCP tool registration + `HarnessMCPServer` primitive + `api.run()` thin-wrapper reframe + `ServerCtxElicitCallback` replacing `_PlaceholderMCPCallback`) per Q3 + Q4 ratification. U-RT-15 scope preserved verbatim (H_T-as-MCP-client surface; "instantiate FastMCP host; connect configured MCP clients") per Q3 atomicity discipline — the orthogonal H_T-as-MCP-server role lands at U-RT-62. Q2 ratification (`harness-runtime/api.py:run()` Track A operator-facing API symbol preserved as thin wrapper invoking MCP-tool path internally) absorbed at U-RT-62 unit body as implementation detail, NOT as separate atomic unit. Q5 ratification (RETIRE-READY → RETIRED gate on (a)+(b) jointly; H_T-CP-18 does NOT advance jointly under (α)) absorbed at U-RT-62 AC #J + at new §6 v2.10 addendum. §3 topology graph extended with L9-quinquies block. §6 v2.10 addendum at substitution-retirement preview. §9 traceability pointer bumped v1.11 → v1.12. Unit count grows by one (52). No dependency-graph cycles introduced (verified at §3 acyclic invariant pass; U-RT-62 depends on U-RT-15 + U-RT-25 + U-RT-42 + U-RT-49 + U-RT-60 — all foundational-to-it). No coverage-matrix change at C-RT-NN contracts (U-RT-62 traces to C-RT-04 `mcp_host`/`mcp_clients` extension + C-RT-08 `run()` continuity + C-RT-18 §14.8.3 v1.12 topology-pin paragraph — all already covered by §15 spec-to-plan traceability matrix at the U-RT-15 / U-RT-42 / U-RT-60 rows; U-RT-62 row addition owed at spec §15 next revision). Sections preserved verbatim from v2.9: §1 package layout; §2 L0–L11 unit bodies U-RT-00 through U-RT-59 (verbatim); §2 L9-bis U-RT-58 / L9-ter U-RT-59 / L9-quater U-RT-60 ACs #1–#14 (verbatim); §3 L0–L11 + L9-bis + L9-ter + L9-quater topology blocks (verbatim — only L9-quinquies block added); §4 24 CXA edges table; §5 spec recording strategy; §6 §6.5 substitution table + v2.3 / v2.5 / v2.7 addenda (verbatim — only v2.10 addendum added); §7 verification strategy; §8 known risks; revision log v1 through v2.9.*

*v2.9 — minor revision (2026-05-21). Q5 single-arc co-publication per `.harness/class_1_tension_c_rt_18_hitl_span_attribute_carrier_drift.md` operator-ratified resolution (RATIFIED at HEAD `95a9436`; spec absorption at HEAD `904a4ec`). Absorbs spec `Spec_Harness_Runtime_v1.md` v1.10 → v1.11 Form A NOTE-form amendment (canonical 4-span shape restoration per ADR-D5 v1.3 §1.8 + CP carrier `HITL_SPAN_NAMESPACE_SCHEMA`; v1.9/v1.10 hand-coded attribute names retired). Two U-RT-60 ACs amended (#7 canonical `hitl.gate.{level,persona_tier,required}` attribute set + drop hand-coded `.outcome` reference; #8 canonical 4-span shape — open `hitl.invocation.opened` per spec §14.8.2 step 4f-bis + canonical `hitl.response.{class,latency_ms,summary_hash}` on `hitl.invocation.responded` + canonical `hitl.invocation.timed_out` on timeout path) + AC #11 assertion-shape note appended (4-span coverage per matching placement). ACs #1/#2/#3/#4/#5/#6/#9/#10/#12/#13/#14 preserved verbatim from v2.8. No unit-count change (51); no dependency-graph change; no topology graph change; no coverage-matrix change (every spec contract covered by ≥1 unit per v2.8 baseline; v1.11 amendment is narrative-refinement within C-RT-18 §14.8.2 + §14.8.5, not a new contract). Sections preserved verbatim from v2.8: §1 package layout; §2 L0–L11 unit bodies U-RT-00 through U-RT-59 (untouched) + U-RT-60 ACs #1/#2/#3/#4/#5/#6/#9/#10/#12/#13/#14 (untouched); §3 topology graph (L9-quater wrap-chain block preserved); §4 24 CXA edges table; §5 spec recording strategy; §6 7d retirement preview (v2.7 addendum preserved verbatim); §7 verification strategy; §8 known risks; §9 traceability pointer (already v1.10 → v1.11 absorption owed; pointer text references "v1.10" → updates to "v1.11"); revision-log entries v1 through v2.8.*

*v2.8 — minor revision (2026-05-21). Q5 single-arc co-publication per `.harness/class_1_tension_c_rt_18_ask_user_question_surface_binding_mechanism_underspec.md` operator-ratified resolution (RATIFIED at HEAD `fb545ec`; spec absorption at HEAD `510c502`). Two coupled triggers: (1) absorbs spec `Spec_Harness_Runtime_v1.md` v1.9 → v1.10 amendment (§14.8.3 H_E binding mechanism pinned to MCP-server-backed per Q1 + retirement-reading simplification "analogous to" → "via" per Q2 + MockAskUserQuestionSurface MUST-language upgrade per Q3); (2) absorbs 6 secondary findings from `.harness/adversarial_review_u_rt_60_pre_impl.md` (F2-01 retirement-criterion enumeration gap; F2-02 multi-placement test design; F2-03 entry_core opaque-str drift acknowledgment; F1-01 deferred-list silence; F1-02 U-RT-51 seam-count split; F1-03 version-baked fail-class observation). Four U-RT-60 ACs amended (#2 MCP-server binding pin per Q1 + deferred-list enumeration sentence per F1-01 folded in; #9 entry_core opaque-str carry-forward acknowledgment per F2-03; #11 multi-placement test design per F2-02; #14 U-CP-13 enumeration + "via" not "analogous" per F2-01 + Q2). No unit-count change (51); no dependency-graph change; no topology graph change. Sections preserved verbatim from v2.7: §1 package layout; §2 L0–L11 unit bodies U-RT-00 through U-RT-59 (only U-RT-60 ACs #2/#9/#11/#14 touched; ACs #1/#3/#4/#5/#6/#7/#8/#10/#12/#13 preserved verbatim); §3 topology graph (L9-quater wrap-chain block preserved); §4 24 CXA edges table; §5 spec recording strategy; §6 7d retirement preview (v2.7 addendum preserved verbatim — F1-02 U-RT-51 seam-count split kept at change-note level per scope-minimality option (b)); §7 verification strategy; §8 known risks; §9 traceability pointer (already v1.9 → v1.10 absorption owed but pointer text references "v1.9" → updates to "v1.10"); revision-log entries v1 through v2.7. F1-02 + F1-03 absorbed at change-note observation rows below (no AC body changes).*

*v2.7 — minor revision (2026-05-20). Adds U-RT-60 (HITL gate composer + `RuntimeHITLGateComposer` wrapper class + `AskUserQuestionSurface` H_E delivery Protocol) at a new L9-quater section, plus §3 topology graph edge, §6 7d retirement preview update for H_T-CP-20, §9 traceability pointer version bump (v1.6 → v1.9). Absorbs the operator-ratified in-CLI spec growth at `Spec_Harness_Runtime_v1.md` v1.8 → v1.9 (adds the §14.8 C-RT-18 contract + CXA v2.4 → v2.5 §2.3.7 CP→OD bucket cardinality 1 → 2 typed seams). Operator architectural ratifications captured at the v1.9 change-note + the systems-architect mode 3 5-question chain at `.harness/class_1_tension_cp_20_hitl_gate_composer_underspec.md`: Q1 = AskUserQuestion @ sub-phase 7b synchronous (webhook deferred); Q2 = composer-stack outer→inner C-RT-16 retry → HITL gate → C-RT-15/C-RT-17 dispatch (per-attempt re-eval); Q3 = SHARED `cp_audit_to_od_audit` converter at `harness-cxa/` (HITL-canonical at origin per CP spec v1.9 §13.5.1 NOTE 5); Q4 = SEPARATE pause/resume arc (C-RT-19 / U-RT-61 future); Q5 = PRE_ACTION + SUB_AGENT_BOUNDARY only at v1.9 MVP (VALIDATOR_ESCALATION foreclosed; validator-composer arc lands trigger source). Unit count grows by one (U-RT-60 fills the next slot after the v2.5-introduced U-RT-59). Total = 51. Pre-empts 4 path-(ii) NOTE-deferrals at §14.8.7 mirrored as ACs (multi-placement same step + edited_proposal mutation semantics + retry-of-gate-eval semantics + cross-trust-boundary palette restriction) per advisor recommendation to prevent F2-01-style discovery-at-implementation hazard.*

*v2.6 — minor revision (2026-05-20). UN-STRUCKS U-RT-59 AC #9 write half at the U-RT-59 Fork 2 implementation arc landing. v2.5 AC #9 strike (per `[[halt-route-split-AC-pattern]]` at first U-RT-59 landing) cited Fork 2's CP→OD audit-write gap as the blocker; v2.6 lands the full 4-substep sequence per runtime spec v1.7 §14.7.2 step 8 (Path D + Path B-revised-a resolution) + adds 6 new step-8-specific tests at `harness-runtime/tests/test_lifecycle_sub_agent_dispatch.py` (per-substep verification + failure-semantics + 3-dispatch IS-chain integrity integration test). Co-published with the implementation commit + runtime spec v1.7 follow-on fail-class addition (`RT-FAIL-SUB-AGENT-AUDIT-COMPOSE`). 2283 workspace tests green.*

*v2.5 — minor revision (2026-05-20). Adds U-RT-59 (sub-agent dispatch composer + StepKindDispatcherRegistry driver routing-layer refactor + in-process recursive ChildWorkflowRunner primitive) at a new L9-ter section, plus §3 topology graph edge, §6 7d retirement preview update for H_T-CP-10 + H_T-CP-13 + H_T-CP-14 (PARTIAL slice), §9 traceability row. Absorbs the operator-ratified in-CLI spec growth at `Spec_Harness_Runtime_v1.md` v1.5 → v1.6 (which adds the §14.7 C-RT-17 contract). Three operator architectural ratifications captured at v1.5 → v1.6 change-note: routing-layer = StepKindDispatcherRegistry; scope = single-sub-agent within linear parent (fan-out + cache warm-up + cross-family-fallback-at-fan-out deferred to parent-topology-expansion arc); invocation primitive = in-process recursive sub-workflow invocation. Unit count grows by one (U-RT-59 fills the next slot after the existing v2.3-introduced U-RT-58). Initial draft HALT-marked at first revision pass due to C-RT-17 StepDispatcher Protocol parent-context gap; **Path A resolution landed same arc** (operator-ratified 2026-05-20; fork record at `.harness/class_1_tension_c_rt_17_step_dispatcher_parent_context_gap.md`; CP spec v1.5 → v1.6 amendment + Protocol extension + driver loop change + dispatcher pass-throughs; 2231 tests green). HALT markers dropped; ACs #4 + #5 reference `step_context.X` per Path A resolution. U-RT-59 implementation now unblocked at next session.*

*v2.4 — minor revision (2026-05-20). Revises U-RT-58 AC #4 attribute names to the CP-canonical 6-attribute set per `.harness/class_1_tension_c_rt_16_retry_attribute_drift.md` Path A (filed + ratified during U-RT-58 implementation). Co-published with `Spec_Harness_Runtime_v1.md` v1.5 which restates §14.6 step 4 canonically. No structural unit-count or DAG change.*

*v2.3 — minor revision (2026-05-20). Adds U-RT-58 (retry/breaker/fallback composer wrapping C-RT-15) at a new L9-bis section, plus §3 topology graph edge, §6 7d retirement preview update, §9 traceability row. Absorbs the operator-ratified Path A resolution of `.harness/class_1_tension_cp_3_retry_breaker_composer_underspec.md` (filed 2026-05-20 at `7fe2c95`). Co-published with `Spec_Harness_Runtime_v1.md` v1.4 (which adds the C-RT-16 contract). Unit count grows by one (U-RT-58 fills the next slot after the existing v1.2-introduced U-RT-52).*

*v2.1 — minor revision (2026-05-19). Adds §9 pointing at `design-substrate/Spec_Harness_Runtime_v1.md` v1.1 §15 as the single source of truth for spec-to-plan traceability. Closes the v1.1 spec change-note "Downstream absorption owed" line by canonicalizing the trace in one place rather than duplicating it. No unit-set or topology changes.*

*v2 — post-adversarial-review revision (2026-05-19). Absorbs `.harness/Adversarial_Review_phase_2_session_3_track_a_plan.md` findings F2-01..F2-08, F1-01..F1-03. Phase-7-style unit enumeration; topological levels L0–L11.*

---

## Context

Phase 2 Session 3 turns 144 landed library units across `harness-{core,is,as,cp,od,cxa}/` into a startable Python process. The library specifies *what* the harness is (schemas, contracts, policies, terminal exporters as reference manifests); Track A specifies *who instantiates and wires it* and *in what order*. The empirical gap from the Session 2 strawman is total: zero `__main__`, zero provider SDK construction, zero `set_tracer_provider`, empty `harness-cxa/src/harness_cxa/`, terminal exporters are reference-only.

Five Class 1 forks have been resolved, anchoring Track A:

- **F-P2-1** → new `harness-runtime/` workspace member owns the composition root.
- **F-P2-2** → Track A ingress is `harness_runtime.run(workflow_object)`; CLI/discovery/markdown deferred to Track B.
- **F-P2-3** → `harness-runtime/` owns OTel TracerProvider lifecycle (bootstrap stage 4 OD).
- **F-P2-4** → `harness-runtime/` owns provider SDK (anthropic/openai/ollama) client lifecycle (bootstrap stage 3a CP_CLIENTS).
- **F-P2-5** → `harness-runtime/` owns the in-process OTLP collector daemon lifecycle (bootstrap stage 4 OD).

Track A is bounded: it instantiates and wires; it does not redefine schemas, topology-selection algorithms, operator-facing UX, or workflow authoring formats. Substitution retirement under H_T condition B fires event-driven as runtime stand-up activates real surfaces. Track B (concurrent) designs the DevEx agentic plane on top.

**Canonical bootstrap stage enumeration (9 stages, indices 0–8):**

| # | Stage | Owner unit(s) | Notes |
|---|---|---|---|
| 0 | PREAMBLE | U-RT-04..U-RT-08 | Load `RuntimeConfig`, validate, derive sub-configs |
| 1 | IS | U-RT-09..U-RT-12 | Path resolver, worktree + shadow-Git, ledger, index + cache |
| 2 | AS | U-RT-13..U-RT-16 | Skills load, tool contracts, MCP host, sandbox dispatch |
| 3a | CP_CLIENTS | U-RT-17..U-RT-20 | Provider SDK clients + capability abstraction |
| 3b | CP_ROUTING | U-RT-21..U-RT-26 | Routing manifest, engine selection, retry/breaker, HITL, handoff |
| 4 | OD | U-RT-27..U-RT-32 | TracerProvider, BSP, OTLP exporter, collector daemon, cost chain, audit writer |
| 5 | LOOP_INIT | U-RT-39..U-RT-41 | Override evaluator, topology dispatcher, lifecycle emission |
| 6 | CXA_WIRING | U-RT-33..U-RT-38 | Terminal exporter manifest import + 24 phase-2-runtime edges |
| 7 | INGRESS_ACCEPT | U-RT-42, U-RT-43 | Accept `WorkflowObject` via `run()`; orchestrator runs stages 0–6 in fixed order |

(Stage 3 splits into 3a + 3b — two adjacent stages with the same numeric "3" suffix-distinguished `a`/`b`; canonical file naming follows `stage_3a_cp_clients.py` / `stage_3b_cp_routing.py`. Total enum cardinality = 9, file count = 9.)

**Scope:** 51 atomic units across 12 topological levels (L0–L11). Unit numbering is dense (no gaps).

---

## 1. Package layout

```
harness-runtime/
  pyproject.toml
  src/harness_runtime/
    __init__.py                       # public surface: run, RuntimeConfig, HarnessContext
    py.typed
    types.py                          # HarnessContext, RuntimeConfig, BootstrapStage enum
    config/
      loader.py                       # config precedence (defaults < env < kwargs)
      path_bindings.py
      provider_secrets.py             # keyring lookup driver
      otel_config.py
      collector_config.py
    bootstrap/
      __init__.py                     # orchestrator: stages 0..7 in order (9 stage files; 3a + 3b)
      stage_0_preamble.py
      stage_1_is.py
      stage_2_as.py
      stage_3a_cp_clients.py
      stage_3b_cp_routing.py
      stage_4_od.py
      stage_5_loop_init.py
      stage_6_cxa_wiring.py
      stage_7_ingress.py
    lifecycle/
      providers.py                    # AsyncAnthropic/AsyncOpenAI/AsyncOllama construction + close
      tracer.py                       # TracerProvider build, BSP, OTLP exporter
      collector_daemon.py             # in-process collector supervisor
      mcp_host.py                     # MCP host startup + client connect
      audit_ledger_writer.py
      shadow_git.py                   # shadow-Git checkpoint/rollback supervisor binding
    wiring/
      cxa_terminal_exporters.py       # import the 5 terminal aggregate exporter manifests for side-effects
      cxa_phase2_runtime_edges.py     # the 24 phase-2-runtime edges
      cost_attribution.py
      hitl_placement_registry.py
    api.py                            # async def run(workflow, *, config=None) -> RunResult
    shutdown.py                       # drain, flush, close, reverse-stage order
    admin/
      inspect.py                      # read-only admin stub
      shutdown_cli.py                 # signal-running-instance stub
  tests/
    unit/
    integration/
      test_bootstrap_stages.py
      test_run_smoke.py
      test_shutdown_drain.py
      test_cxa_pattern_p1.py
    conftest.py                       # tmp .harness/, fake async providers, in-mem collector
```

**`pyproject.toml`:**

```toml
[project]
name = "harness-runtime"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "harness-core", "harness-is", "harness-as", "harness-cp", "harness-od", "harness-cxa",
  "anthropic>=0.45", "openai>=1.60", "ollama>=0.4",
  "mcp>=1.2", "keyring>=25.5",
  "opentelemetry-api>=1.30", "opentelemetry-sdk>=1.30", "opentelemetry-exporter-otlp>=1.30",
  "pydantic>=2.10",
]

[project.scripts]
# Track A: admin-only stubs. Operator-facing `run` is Track B.
harness-inspect  = "harness_runtime.admin.inspect:main"
harness-shutdown = "harness_runtime.admin.shutdown_cli:main"

[tool.uv.sources]
harness-core = { workspace = true }
harness-is   = { workspace = true }
harness-as   = { workspace = true }
harness-cp   = { workspace = true }
harness-od   = { workspace = true }
harness-cxa  = { workspace = true }
```

Root `pyproject.toml` adds `"harness-runtime"` to `[tool.uv.workspace].members` and to `[tool.pyright].include` / `[tool.pytest.ini_options].testpaths`.

---

## 2. Atomic units

Each unit is sized to land in a single PR with a fixed acceptance test set. Every unit cites a **landed contract** that drives the wiring and a **runtime spec section** (`Spec_Harness_Runtime_v1.md §N` — placeholder until §5 spec authoring lands; pre-condition gate at U-RT-00).

### L0 — Spec gate + scaffold + shared runtime types

**U-RT-00 — Author `Spec_Harness_Runtime_v1.md`**
- Scope: hard gate on all U-RT-NN landing. Authors a new thin spec covering: bootstrap stage order + invariants, `HarnessContext` + `RuntimeConfig` schemas, `run()` Python-API contract, shutdown order, admin-stub semantics, 24 phase-2-runtime CXA edge wiring obligations, the five F-P2-N fork resolutions. Filed at `design-substrate/Spec_Harness_Runtime_v1.md`.
- Deps: F-P2-1..F-P2-5 resolved (already true at session open).
- AC: file exists; passes adversarial review (`harness-adversarial-reviewer`); every U-RT-NN unit can cite at least one `Spec_Harness_Runtime_v1.md §N` section.
- Spec source: F-P2-N fork records + strawman §2/§3.
- Notes: executed via `spec-writer` skill at Session 4.

**U-RT-01 — Workspace member registration**
- Scope: add `harness-runtime/` to root workspace; create `pyproject.toml`, `__init__.py`, `py.typed`, empty `tests/`.
- Deps: U-RT-00.
- AC: `uv sync --all-packages` resolves; `pyright`/`ruff` see the package; `pytest harness-runtime/tests` exits 0; root pyproject lists it.

**U-RT-02 — `HarnessContext` and `RuntimeConfig` types**
- Scope: Pydantic v2 models in `types.py`. `RuntimeConfig` (input). `HarnessContext` (output of bootstrap, frozen after stage 7; holds resolved registries, async clients, tracer, collector handle, ledger writer, MCP host handle).
- Deps: U-RT-01.
- AC: pyright-strict clean; `RuntimeConfig` round-trips; `HarnessContext` is frozen.
- Spec: `harness_core.identity`, `harness_core.deployment_surface`, F1–F5 ADRs.

**U-RT-03 — `BootstrapStage` enum + stage-result protocol**
- Scope: 9-value enum `BootstrapStage` (`PREAMBLE`, `IS`, `AS`, `CP_CLIENTS`, `CP_ROUTING`, `OD`, `LOOP_INIT`, `CXA_WIRING`, `INGRESS_ACCEPT`); `StageResult` protocol; lifecycle-event hook stub.
- Deps: U-RT-02.
- AC: enum has exactly 9 members in the order above; `len(BootstrapStage)==9`; result protocol consumed by stage modules.

### L1 — Config loading (stage 0 PREAMBLE)

**U-RT-04 — Config precedence resolver**
- Scope: `RuntimeConfig` materializer combining defaults, env vars, kwargs to `run()`. No file/CLI parsing (Track B).
- Deps: U-RT-02.
- AC: precedence tested via three-source fixture (default vs env vs kwargs); missing-required raises typed error; unknown keys rejected.

**U-RT-05 — Path-binding config**
- Scope: build `PathBinding` (IS landed) from `RuntimeConfig`; validate against `WorkloadManifestOptInSchema` (IS).
- Deps: U-RT-04; landed `harness_is.path_binding`, `harness_is.workload_manifest_opt_in_schema`.
- AC: PathBinding accepted by `PathResolver`; opt-ins validated.

**U-RT-06 — Provider-secret config + keyring resolver driver**
- Scope: `provider_secrets.py` looks up secrets via `keyring` per AS `secret_fetch`/`secret_allowlist`. No secret values in `RuntimeConfig` (allowlist keys only).
- Deps: U-RT-04; landed `harness_as.secret_*`.
- AC: keyring miss raises typed `SecretFailClass`; allowlist enforced; fetch audit event emitted via AS primitives.
- **Risk:** Class 1 candidate if AS spec is silent on fetch *site*.

**U-RT-07 — OTel config (endpoint, sampler, resource attrs)**
- Scope: validate OTLP endpoint URL, sampler mode from `harness_od.sampling_mode`, resource attrs from deployment surface.
- Deps: U-RT-04; landed `harness_od.sampling_mode`, `namespace_map`.
- AC: endpoint URL validates; resource attrs include required 12-namespace tags.

**U-RT-08 — Collector daemon config**
- Scope: in-process collector config (ring buffer size, sqlite rotation thresholds, placement matrix per `per_cell_collector_placement_matrix`).
- Deps: U-RT-04; landed `harness_od.local_first_otlp_collector`, `per_cell_collector_placement_matrix`.
- AC: placement matrix selected; thresholds bounded; defaults match OD spec.

### L2 — IS bootstrap (stage 1)

**U-RT-09 — Content-addressed-index reattach + semantic cache init**
- Scope: instantiate the content-addressed-index handle from landed IS index module; initialize semantic cache; reattach to existing on-disk index or fresh-create.
- Deps: U-RT-10 (needs path resolver); landed IS index + cache modules.
- AC: index handle returned non-null; existing index reattaches with byte-identical content hash; missing index path fresh-creates idempotently; cache hits observable in tests.

**U-RT-10 — Path-class registry materialization**
- Scope: instantiate `PathResolver(binding)`; populate `PATH_CLASS_REGISTRY` per landed IS taxonomy.
- Deps: U-RT-05; landed `harness_is.path_resolver`, `path_class_registry`.
- AC: all PathClass members resolve; missing paths created idempotently; resolver stored on `HarnessContext`.

**U-RT-11 — Worktree isolation manager init + shadow-Git supervisor binding**
- Scope: instantiate `WorktreeIsolationManager(repo_root, worktree_base, opt_ins)`; bind shadow-Git checkpoint/rollback supervisor (subprocess invocation of `git`, worktree-tier sub-role binding).
- Deps: U-RT-10; landed `harness_is.worktree_isolation`, `shadow_git_checkpoint`, `shadow_git_rollback`.
- AC: manager initialized; isolation invariants asserted at boot; round-trip checkpoint → rollback against tmp `.harness/` returns to byte-identical pre-checkpoint state.

**U-RT-12 — State-ledger writer init + chain reattach**
- Scope: open `.harness/state.jsonl` (or fresh-create); reattach chain head via `chain_verification`; bind writer wrapper around `state_ledger_write`.
- Deps: U-RT-10; landed `harness_is.jsonl_event_ledger_lifecycle`, `state_ledger_write`, `chain_verification`, `entry_hash`.
- AC: fresh-create produces genesis entry; reattach verifies prior chain; tampered chain refuses to open.
- **Risk:** reattach semantics across crashed prior run may surface IS spec gap.

### L3 — AS bootstrap (stage 2)

**U-RT-13 — Skills filesystem load**
- Scope: enumerate Skills via `PATH_CLASS_REGISTRY[PathClass.SKILLS]`; parse skill manifests.
- Deps: U-RT-10; landed AS skills surface.
- AC: all skills under PathClass.SKILLS loaded; duplicate IDs rejected; manifest schema enforced.

**U-RT-14 — Tool contract registration**
- Scope: register tool contracts from landed `harness_as.tool_contract` into runtime registry consumable by CP.
- Deps: U-RT-13; landed `harness_as.tool_contract`.
- AC: contracts discoverable by name; discriminator dispatch wired.
- **Risk:** registration *site* may not be specified — Class 1 candidate.

**U-RT-15 — MCP host startup + client connect**
- Scope: instantiate FastMCP host; connect configured MCP clients; bind tool surfaces.
- Deps: U-RT-14, U-RT-06; landed `harness_as.mcp_transport_floor`.
- AC: host accepts connections; configured clients reach READY; transport-floor invariants asserted.
- **Risk:** AS spec may not pin host startup lifecycle — Class 1 candidate.

**U-RT-16 — Sandbox-tier dispatch binding**
- Scope: bind dispatch table per `sandbox_tier`, `sub_agent_sandbox_tier`, `sandbox_tier_floor`, `sandbox_provider_class`.
- Deps: U-RT-15; landed AS sandbox modules.
- AC: each declared tier resolves a provider; floor enforced; fail-class typed.

### L4 — Provider SDK lifecycle (stage 3a CP_CLIENTS) — **async clients**

**U-RT-17 — AsyncAnthropic client construction + close**
- Scope: instantiate `anthropic.AsyncAnthropic(...)` with resolved secret; close on shutdown. Async client per `async def run(...)` posture (F2-06 resolution).
- Deps: U-RT-06; landed `harness_cp.provider_capabilities`.
- AC: client constructs; async ping succeeds in integration; close idempotent and awaitable.

**U-RT-18 — AsyncOpenAI client construction + close**
- Scope: as U-RT-17 for `openai.AsyncOpenAI(...)`.
- Deps: U-RT-06.
- AC: same as U-RT-17.

**U-RT-19 — Ollama AsyncClient construction + close**
- Scope: as U-RT-17 for `ollama.AsyncClient(...)`; local-tier reachability checks.
- Deps: U-RT-06.
- AC: same as U-RT-17; local-tier unreachable → typed degraded.

**U-RT-20 — Capability-aware abstraction binding**
- Scope: bind 3 async provider clients behind CP `provider_capabilities`; populate per-engine-class candidates per `engine_class_candidate`.
- Deps: U-RT-17, U-RT-18, U-RT-19; landed `harness_cp.provider_capabilities`, `engine_class`, `engine_class_candidate`.
- AC: each `EngineClass` resolves to at least one capable provider; capability assertions exhaustively typed.

### L5 — CP routing-core wiring (stage 3b CP_ROUTING)

**U-RT-21 — Routing manifest construction (R-2/W-2)**
- Scope: build runtime routing manifest per CP v2.10 R-2 (read) and W-2 (write) schemas; persist via `routing_manifest_residence`.
- Deps: U-RT-20, U-RT-10; landed `harness_cp.routing_manifest_residence`, `routing_core_surface`.
- AC: manifest validates against R-2 + W-2 (schema round-trip); residence policy honored (manifest persists at `PathClass.ROUTING_MANIFEST` resolved path); **replay determinism test:** two invocations of `build_routing_manifest(config)` against identical config produce byte-identical canonical-JSON output.
- **Risk:** R-2/W-2 only landed at CP v2.10 — **highest Class 1 probability** in the plan.

**U-RT-22 — Engine-selection binding**
- Scope: wire engine-class selection per `workload_binding_engine_class_selection`, `workload_engine_class_matrix`.
- Deps: U-RT-21; landed CP modules above.
- AC: every `WorkloadClass` resolves to an `EngineClass`; missing binding raises typed error at bootstrap, not at runtime.

**U-RT-23 — Cross-family fallback chain construction**
- Scope: build fallback chain per `cross_family_fallback_chain` + `fall_through_procedure`; bind `default_downgrade_rule`.
- Deps: U-RT-22; landed CP modules.
- AC: degenerate (all-down) case surfaces typed; downgrade rule auditable.

**U-RT-24 — Retry / breaker / idempotency runtime binding**
- Scope: bind retry + breaker primitives (hand-rolled, no `tenacity`/`pybreaker`) per `validator_fail_transient_staircase`, `harness_breaker_schema`, `idempotency_join_dedup`.
- Deps: U-RT-21; landed CP + OD modules.
- AC: **transient-staircase observability:** injected transient fault N times surfaces N escalated retry intervals matching the `validator_fail_transient_staircase` table; breaker state transitions emit `harness.breaker.*` spans on each open/half-open/close; idempotency join dedupes a replayed request to a single ledger entry.

**U-RT-25 — HITL placement registry**
- Scope: instantiate `hitl_placement` registry; bind `hitl_response_palette`, `hitl_timeout_degradation`, `hitl_as_tool_call_rewriting`, `pause_resume_protocol`.
- Deps: U-RT-21.
- AC: HITL surfaces registered; timeout degradation emits typed event after configured wait; tool-call rewriting wires.

**U-RT-26 — Sub-agent handoff + brief registry**
- Scope: bind `handoff_context`, `sub_agent_brief`, `sub_agent_gate_level_descent`, `brief_authoring_inheritance`.
- Deps: U-RT-25.
- AC: handoff registry queryable; brief schemas enforced.

### L6 — OD observability runtime (stage 4 OD)

**U-RT-27 — TracerProvider construction + global registration**
- Scope: build SDK `TracerProvider(resource=...)`; call `set_tracer_provider(...)` — the site U-OD-23 depends on.
- Deps: U-RT-07; landed `harness_od.namespace_map`.
- AC: `get_tracer_provider()` returns the registered provider in-process; resource carries deployment-surface attrs.

**U-RT-28 — BatchSpanProcessor + OTLP exporter**
- Scope: attach `BatchSpanProcessor(OTLPSpanExporter(endpoint=...))` per OD `per_sandbox_tier_otlp_reachability`.
- Deps: U-RT-27.
- AC: spans flush on demand; reachability matrix enforced.

**U-RT-29 — In-process OTLP collector daemon supervisor**
- Scope: start the collector daemon described by `local_first_otlp_collector` (U-OD-27 is library-only; this unit *runs* it). Health check, bounded restart-on-fail, structured stop.
- Deps: U-RT-08, U-RT-28; landed `harness_od.local_first_otlp_collector`, `per_cell_collector_placement_matrix`.
- AC: daemon starts and answers health; controlled stop flushes; crash-restart bounded.
- **Risk:** process supervision likely surfaces OD spec gap — Class 1 candidate.

**U-RT-30 — Ring-buffer + sqlite rotation wiring**
- Scope: wire ring buffer + sqlite rotation per OD modules; bind sqlite path via `PATH_CLASS_REGISTRY`.
- Deps: U-RT-29.
- AC: rotation under load tested; sqlite path resolves via IS registry; backpressure observable.

**U-RT-31 — Cost-attribution 5-step chain wiring**
- Scope: instantiate cost-attribution chain per `cost_formula`, `cost_attribution_sandbox_fanout`, `cost_attribution_dashboard_binding`, `operator_burden_eval_primitives`.
- Deps: U-RT-28; landed OD modules.
- AC: end-to-end attribution observable on a single fake span; sandbox fanout splits attribution correctly.

**U-RT-32 — Audit-ledger writer instantiation**
- Scope: build runtime `AuditLedgerWriter` protocol over `audit_ledger_types`, `multi_tenant_trace_separation_and_audit_ledger`; share IS ledger chain via U-RT-12's writer wrapper. Writer entry point: `append_audit_entry(tenant_id, entry: AuditLedgerEntry) -> EntryHash`.
- Deps: U-RT-12, U-RT-27.
- AC: `append_audit_entry` round-trip — entry → IS ledger chain → `chain_verification` passes; cross-tenant separation enforced (entries written under tenant A's hash chain are unreachable from tenant B's reader); chain integrity preserved across 100 sequential appends.

### L7 — CXA wiring (stage 6 CXA_WIRING)

**U-RT-33 — Terminal aggregate exporter manifest import (side-effect)**
- Scope: import the 5 terminal aggregate exporter manifests (`harness_is.substrate_seam_exports`, `harness_as.as_substrate_seam_exports`, `harness_cp.cp_namespace_export_manifest`, `harness_cp.cp_cross_axis_composition_manifest`, `harness_od.substrate_seam_exports_aggregate_manifest`) at composition-root load time so their import-time side-effects (Pattern P1 reference exposure) realize. Distinct from U-RT-51 verification.
- Deps: L2–L6 init.
- AC: import succeeds without exception; module-level manifest constants resolve non-empty; no circular-import error.
- Spec source: strawman §2 ("Only composition root imports seam exports").

**U-RT-34 — Phase-2-runtime edges: AS→IS (1 edge)**
- Scope: wire AS skills load → IS ledger append (skill-discovery ledger emission). Edge: U-AS-27 → U-IS-11.
- Deps: U-RT-13, U-RT-32.
- AC: skill-load event surfaces in ledger; `chain_verification` passes post-emission.

**U-RT-35 — Phase-2-runtime edges: CP→IS (17 edges)**
- Scope: wire ledger-append delegations per CXA v2.3 §2.3 enumeration — source units U-CP-12, U-CP-14, U-CP-27, U-CP-30, U-CP-34, U-CP-37, U-CP-49, U-CP-50, U-CP-52 → target units U-IS-07, U-IS-08, U-IS-09, U-IS-11. All 17 are ledger-emission patterns.
- Deps: U-RT-21, U-RT-32.
- AC: each enumerated CP site, when exercised in integration, emits the spec'd IS ledger entry with correct schema variant; per-edge assertion table in test exhausts the 17.
- **Split rule:** if signature divergence surfaces at any of the 9 CP source units, split per-source-unit (`U-RT-35a..i`). This is the only unit allowed to split mid-flight without back-flow.

**U-RT-36 — Phase-2-runtime edges: OD→IS (2 edges)**
- Scope: wire OD audit-ledger writer through IS ledger chain. Edges: U-OD-30 → U-IS-11; U-OD-34 → U-IS-17.
- Deps: U-RT-32.
- AC: OD audit entries reach IS chain; `chain_verification` passes; terminal-exporter manifest string reference to U-IS-17 resolves.

**U-RT-37 — Phase-2-runtime edges: OD→AS (1 edge)**
- Scope: wire terminal-exporter manifest string reference U-OD-34 → U-AS-33 at runtime.
- Deps: U-RT-13, U-RT-27.
- AC: manifest reference resolves; AS namespace verification runs at bootstrap; mismatch surfaces typed.

**U-RT-38 — Phase-2-runtime edges: OD→CP (3 edges, inversion/manifest)**
- Scope: 3 OD→CP edges — U-OD-09 → U-CP-54 (F-CP-01 Stage 3b inversion: OD exports `harness.breaker.*` ingested at CP composition); U-OD-34 → U-CP-54 (terminal-exporter manifest string ref); U-OD-34 → U-CP-55 (F2-12 inheritance carry-forward declaration).
- Deps: U-RT-21, U-RT-27, U-RT-31.
- AC: CP namespace ingestion of `harness.breaker.*` observable; manifest references resolve; dashboard bindings observable.

*Edge total: 1 + 17 + 2 + 1 + 3 = 24. Matches D-P2-2.*

### L8 — Workflow loop activation (stage 5 LOOP_INIT)

**U-RT-39 — Per-step override evaluator runtime binding**
- Scope: instantiate runtime around landed `per_step_override_evaluator`.
- Deps: U-RT-21; landed `harness_cp.per_step_override_evaluator`.
- AC: override evaluations type-check; audit hook fires on each override.

**U-RT-40 — Topology dispatcher runtime binding**
- Scope: bind dispatcher over `topology_pattern` enum + `per_workload_class_topology`. Track A *dispatches* what config selects; selection algorithm is Track B.
- Deps: U-RT-22, U-RT-39; landed `harness_cp.topology_pattern`, `per_workload_class_topology`.
- AC: each TopologyPattern dispatches to a callable; default selected from config.
- **Risk:** Tension 002 (TopologyPattern enum) — re-verify resolution before landing.

**U-RT-41 — Lifecycle event emission hook**
- Scope: emit `workflow_event_class` events at each bootstrap stage and per CP workflow lifecycle event.
- Deps: U-RT-28, U-RT-32, U-RT-40; landed `harness_core.workflow_event_class`, `harness_cp.lifecycle_event_span_map`.
- AC: every stage emits typed event; spans map per `lifecycle_event_span_map`.

### L9 — Python API entrypoint (stage 7 INGRESS_ACCEPT)

**U-RT-42 — `harness_runtime.run(workflow, *, config=None)` signature**
- Scope: pin signature, return type (`RunResult` Pydantic model carrying terminal workflow state + audit-ledger head + trace IDs), async posture.
- Deps: U-RT-02, U-RT-40, U-RT-41.
- AC: signature is `async def run(workflow: WorkflowObject, *, config: RuntimeConfig | None = None) -> RunResult`; accepts a single workflow object; unknown workflow types rejected typed. No sync wrapper in Track A (deferred to Track B if needed).
- **Risk:** Class 1 candidate around `WorkflowObject` shape — F-P2-2 deferred operator-facing ingress, but Track A still types the in-process object.

**U-RT-43 — Bootstrap orchestrator (stages 0–7, 9 substage files)**
- Scope: `bootstrap/__init__.py` runs the 9 stage files (stage_0..stage_7 with 3a + 3b) in fixed order; hands resulting `HarnessContext` to `api.run`. Stage failures roll back initialized resources in reverse order.
- Deps: all L2–L8 units.
- AC: full bootstrap returns a `HarnessContext`; injected stage failure at each of the 9 substages triggers reverse-order rollback; each stage emits exactly one lifecycle event.

### L10 — Shutdown sequence + admin stubs

**U-RT-44 — Drain in-flight workflow steps (runtime-owned drain)**
- Scope: `harness-runtime/`-owned drain — signal handler sets `drained_flag` on `HarnessContext`; CP workflow loop polls flag at lifecycle boundaries and surfaces typed completion or typed timeout. No dependency on a landed CP drain primitive (none exists; per F-P2-2 ingress deferred).
- Deps: U-RT-43.
- AC: SIGTERM sets the flag; an in-flight step completes within bounded wait OR surfaces typed timeout; no new ingress accepted post-drain.
- **Risk:** if CP later surfaces a native drain primitive, refactor U-RT-44 to delegate. Track as Class-1 surface at landing.

**U-RT-45 — Flush tracer + audit ledger**
- Scope: force-flush BSP, sync ledger fsync, flush cost attribution.
- Deps: U-RT-28, U-RT-32, U-RT-44.
- AC: post-shutdown, all spans visible in collector sqlite; ledger chain head consistent.

**U-RT-46 — Close clients + collector daemon**
- Scope: close async provider clients (awaitable); disconnect MCP clients; stop collector daemon; close MCP host. Reverse order of construction.
- Deps: U-RT-45.
- AC: all resources closed idempotently; awaitable closures complete within bounded timeout.

**U-RT-47 — Admin stub: `harness-inspect`**
- Scope: read-only stub opens state ledger + collector sqlite read-only and dumps a summary. No write paths.
- Deps: U-RT-12, U-RT-30.
- AC: runs against a stopped harness; returns ledger head and last N spans.

**U-RT-48 — Admin stub: `harness-shutdown`**
- Scope: signal running instance to drain. IPC = pidfile + signal handler (minimum); richer IPC is Track B.
- Deps: U-RT-44.
- AC: signal triggers ordered shutdown; pidfile lifecycle correct.

### L11 — End-to-end verification

**U-RT-49 — No-op workflow smoke test**
- Scope: smallest possible workflow exercising all 9 bootstrap stages; assert ledger entries, spans, and cost attribution all appear.
- Deps: U-RT-43, U-RT-46.
- AC: green run touches each of the 9 `BootstrapStage` enum members (asserted by lifecycle-event capture); collector receives ≥1 span per stage; ledger chain extends; clean shutdown.

**U-RT-50 — Bootstrap-stage isolation test suite**
- Scope: per-stage tests bring up only through stage N and assert invariants; rollback test injects failure at each stage.
- Deps: U-RT-43.
- AC: each of the 9 stages has a focused integration test; rollback verified at each.

**U-RT-51 — Pattern P1 import-graph completeness assertion**
- Scope: test asserts the 22 genuine typed CXA seams (per CXA v2.3 §3) realize Pattern P1 byte-exact — for each (producer-export, consumer-import) pair, `consumer_module.SYMBOL is producer_module.SYMBOL` returns `True`. Distinct from U-RT-33's *import* of terminal aggregate exporter manifests; this asserts the identity-equality invariant the manifests publish.
- Deps: U-RT-33.
- AC: 22 identity-equality assertions pass; missing seam fails with typed error naming the (producer, consumer) pair.

### L9 — LLM-dispatch composer (new at v1.2; Phase-7 sub-phase 7d Class 2 fork absorption)

**U-RT-52 — LLM-dispatch composer (Spec_Harness_Runtime_v1.md §14.5 C-RT-15)**
- Scope: implement `RuntimeLLMDispatcher` at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` satisfying the `harness_cp.workflow_driver.StepDispatcher` Protocol (`runtime_checkable`, declared at `workflow_driver.py:151`). Per-step async composer that (1) resolves `ProviderClient` from `ctx.provider_capabilities` via `binding.model_binding.provider`, (2) starts a GenAI-semconv 1.41.0 span via `ctx.tracer_provider.get_tracer("harness.runtime.llm_dispatch")`, (3) dispatches to the provider's underlying SDK method (anthropic.messages.create / openai.chat.completions.create / ollama.chat) via capability-aware abstraction per CP C-CP-01 §1, (4) populates GenAI semconv attributes (`gen_ai.system`, `gen_ai.request.model`, `gen_ai.response.id`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`) + `anthropic.cache_*` attributes per C-AS-14 §14.2 when `binding.model_binding.provider == "anthropic"`, (5) returns `Mapping[str, Any]` per Protocol contract. Bound at bootstrap stage 5 (LOOP_INIT) alongside override evaluator / topology dispatcher / lifecycle emitter; attached to `ctx.llm_dispatcher`. Excludes fallback / retry / breaker per Q2a scope discipline — provider-side exceptions propagate unmodified to `workflow_driver.py:380-389` `try/except`.
- Deps: U-RT-20 (provider capability bindings); U-RT-27 (TracerProvider); U-RT-39 (override evaluator bound at stage 5 — composer attaches alongside).
- Cross-axis deps (Pattern P1 imports): `harness_cp.workflow_driver.StepDispatcher` Protocol; `harness_cp.engine_class_candidate` for provider selection; CP C-CP-01 §1 capability-aware dispatch semantics; AS C-AS-14 §14.2 (`anthropic.cache_*` attribute set); OD C-OD-04..08 (GenAI semconv binding semantics).
- AC #1: `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` exists; defines async `RuntimeLLMDispatcher` class; `isinstance(RuntimeLLMDispatcher(...), StepDispatcher)` returns `True` via `runtime_checkable`.
- AC #2: per-provider dispatch branch exists for each of 3 providers (anthropic / openai / ollama) with at-least-one mock-provider test exercising each path end-to-end (mock returns canned response; assert span emitted; assert step output mapping shape).
- AC #3: GenAI semconv 1.41.0 attribute set verified — test asserts at minimum `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` are present on the emitted span.
- AC #4: `anthropic.cache_read_input_tokens` + `anthropic.cache_creation_input_tokens` attributes set when `binding.model_binding.provider == "anthropic"`; absent otherwise (per C-AS-14 §14.2 + AS-AL-3 cross-axis discipline).
- AC #5: `RT-FAIL-PROVIDER-UNREACHABLE` raised when `binding.model_binding.provider` not in `ctx.providers` (e.g., Ollama-degraded path skipped registration); typed error with provider name attached.
- AC #6: composer is async; sync wrapper test verifies `RuntimeError: cannot use sync run() with async dispatcher` if a sync `run()` ever lands (no such surface today; future-proof assertion).
- AC #7: bootstrap stage 5 binding test — `ctx.llm_dispatcher` post-condition non-None after stage 5; verified by `test_bootstrap_stage.py`.
- AC #8: Phase 7d retirement-event prerequisite — after U-RT-52 lands, file batch 2 retirement event records for **H_T-CP-1** + **H_T-CP-2** + **H_T-CP-5** + **H_T-OD-2** + **H_T-AS-8** per `.harness/phase-7d-retirement-events-batch-1.md` shape under v2 ledger §9.1 evidence framework (condition B verified end-to-end at the new composer site). Updates `harness-{cp,od,as}/CLAUDE.md` §4.1 substitution-table status entries.

---

### L9-bis — Retry/breaker/fallback composer (new at v1.4 / v2.3; Phase-7 sub-phase 7d Class 1 fork absorption)

**U-RT-58 — Retry/breaker/fallback composer wrapping C-RT-15 (Spec_Harness_Runtime_v1.md §14.6 C-RT-16)**
- Scope: implement `RetryBreakerFallbackDispatcher` at `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py` satisfying the `harness_cp.workflow_driver.StepDispatcher` Protocol (same duck-typing pattern as U-RT-52). Per-step async wrapper that owns the candidate-iteration loop + per-candidate retry loop around the inner C-RT-15 `RuntimeLLMDispatcher.dispatch` invocation. (1) Looks up `RetryPolicy` from `ctx.retry_breaker.get_policy("llm_dispatch")` (reserved registry key per C-RT-16 §"Registry key extension"). (2) Iterates `ctx.fallback_chain` candidates (first candidate = `binding.model_binding`; subsequent = cross-family-fallback per C-CP-04 §4). (3) Per candidate: breaker pre-check via `breaker.should_attempt()`; if open-and-cooldown-unexpired, emit `retry.skipped` event and `advance_or_raise` to next candidate. (4) Per-attempt loop (bounded by `RetryPolicy.max_attempts`): start inner `harness.runtime.retry_attempt` span carrying `retry.*` 6-attribute namespace per C-CP-03 §3.5; dispatch via `self.inner.dispatch(rebound_binding, step)`; on success → `breaker.record_success()` + return; on `LLMDispatchProviderUnreachableError`/`LLMDispatchPayloadShapeError` → fail-fast for this candidate; on provider transient → `advance_staircase`; on `RetryPolicy.max_attempts` exhausted → advance candidate. (5) On `FallbackChainExhaustedError` → emit `fallback.exhausted` on outer span per C-CP-04 §4.2; raise `RetryBreakerFallbackExhaustedError` mapping to new `RT-FAIL-FALLBACK-EXHAUSTED` fail class. (6) Bootstrap stage 5 wraps the bare `RuntimeLLMDispatcher` and binds the wrapper to `ctx.llm_dispatcher` — `workflow_driver` invocation at `workflow_driver.py:379` unchanged.
- Deps: U-RT-24 (retry/breaker registry); U-RT-25 (fallback chain); U-RT-27 (TracerProvider); U-RT-52 (inner C-RT-15 LLM-dispatch composer). Stage 5 wiring extension at the existing U-RT-52 binding site.
- Cross-axis deps (Pattern P1 imports): `harness_cp.workflow_driver.StepDispatcher` Protocol (same as U-RT-52); CP C-CP-03 §3.5 (`retry.*` 6-attribute namespace + dual-emission); CP C-CP-04 §4.2 (`fallback.exhausted` event semantics + chain composition); CP C-CP-21 §21.2 (transient staircase advancement function `advance_staircase`); OD C-OD-07 §7.1 (`harness.breaker.*` 7-attribute schema, emitted by existing `RuntimeRetryBreaker.emit_breaker_transition_event` — wrapper does NOT add OD-side emission code).
- AC #1: `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py` exists; defines async `RetryBreakerFallbackDispatcher` class; `isinstance(RetryBreakerFallbackDispatcher(...), StepDispatcher)` returns `True` via `runtime_checkable`.
- AC #2: per-candidate iteration verified — mock fallback chain with 3 candidates; mock inner dispatcher that fails (transient) on candidate 0 + (transient) on candidate 1 + succeeds on candidate 2; assert wrapper iterates all three, calls `advance_or_raise` twice, returns candidate-2 result; verify outer span spans full envelope; verify three nested per-attempt span sequences.
- AC #3: per-candidate retry-then-success verified — mock inner that fails (transient) twice then succeeds on attempt 3 under `RetryPolicy(max_attempts=3)`; assert wrapper sleeps via `compute_full_jitter_delay_seconds` between attempts (with a sleep-mock to keep tests fast); assert success on attempt 3; verify three per-attempt spans emitted, each carrying `retry.*` 6-attribute namespace; verify final `retry.terminal = "success"`.
- AC #4: `retry.*` 6-attribute namespace emission verified against the CP-canonical schema (v2.4 amendment 2026-05-20 per `.harness/class_1_tension_c_rt_16_retry_attribute_drift.md` Path A) — test asserts each per-attempt span carries the canonical CP §3.5 6-attribute set: `retry.attempt_number` (1-indexed), `retry.original_span_id` (16-hex outer-span-id), `retry.delay_ms` (full-jitter backoff in ms), `retry.cause_attribution` (open-set string from C5 catalog), `retry.fail_class` (`ValidatorFailClass` enum value), `engine.replay_disposition` (looked up via `REPLAY_DISPOSITION_MAPPING[binding.engine_class]`). Attribute carrier imported from `harness_cp.retry_fallback_namespace.RETRY_ATTEMPT_CHILD_SPAN_SCHEMA` (landed canonical producer surface).
- AC #5: `fallback.exhausted` emission verified — mock chain with all candidates failing-fast (provider-unreachable); assert wrapper iterates all candidates; assert `fallback.exhausted` event emitted on outer span with attributes per C-CP-04 §4.2 (`fallback.chain_length`, `fallback.last_failure_class`, `fallback.exhaustion_cause`); assert `RetryBreakerFallbackExhaustedError` raised; assert `RT-FAIL-FALLBACK-EXHAUSTED` fail class set on the error.
- AC #6: breaker integration verified — mock breaker that is OPEN with unexpired cooldown for candidate 0; assert wrapper skips candidate 0 (emits `retry.skipped` event; does NOT call inner dispatcher); assert wrapper proceeds to candidate 1. Separately: mock breaker transitions CLOSED → OPEN after 3 failures; assert `RuntimeRetryBreaker.emit_breaker_transition_event` invoked once at the transition; verify `harness.breaker.*` 7-attribute span event emitted with attributes per C-OD-07 §7.1.
- AC #7: nested-span hierarchy verified — assert OTel span parent-child relationships: outer `harness.runtime.retry_breaker_fallback` is root; per-attempt `harness.runtime.retry_attempt` spans nest inside outer; inner `gen_ai.*` spans (from C-RT-15) nest inside per-attempt; three nesting levels verified via `InMemorySpanExporter` parent-span-id linkage.
- AC #8: reserved registry key extension verified — assert `ctx.retry_breaker.get_policy("llm_dispatch")` returns a populated `RetryPolicy` after bootstrap (default applied when operator-config absent); assert `ReservedToolNameError` raised at manifest-validation time if a tool is named `"llm_dispatch"` in `RoutingManifest.retry_policies`.
- AC #9: bootstrap stage 5 wrap verified — `ctx.llm_dispatcher` post-condition is `isinstance(..., RetryBreakerFallbackDispatcher)` (not bare `RuntimeLLMDispatcher`) after stage 5; verify by `test_bootstrap_stage.py` extension; verify the wrapper's `.inner` attribute is the `RuntimeLLMDispatcher` instance.
- AC #10: Phase 7d retirement-event prerequisite — after U-RT-58 lands, file batch 3 retirement event records for **H_T-CP-3** RETIRED + **H_T-CP-4** RETIRED + **H_T-CP-5** PARTIAL → RETIRED per `.harness/phase-7d-retirement-events-batch-1.md` shape under v2 ledger §5 CP-row evidence framework (condition B verified end-to-end at the new composer site). Re-evaluate §6.3.2 cascade: H_T-CXA-5 (F-CP-01 Stage 3b inversion) candidate for RETIRE-READY once H_T-CP-3 RETIRED + production `harness.breaker.*` emission verified end-to-end (likely RETIRE-READY in same batch event; verify per the wrapper integration tests). Updates `harness-cp/CLAUDE.md` §4.1 substitution-table status entries.

---

### L9-ter — Sub-agent dispatch composer + StepKindDispatcherRegistry + ChildWorkflowRunner (new at v1.6 / v2.5; in-CLI spec growth — **Path A Stage 1 LANDED**)

> **✅ Class 1 fork RESOLVED — Path A Stage 1 plumbing LANDED.** Operator ratified Path A 2026-05-20 (fork record `.harness/class_1_tension_c_rt_17_step_dispatcher_parent_context_gap.md`). Stage 1 plumbing landed in the same arc: `StepDispatcher` Protocol amended at `Spec_Control_Plane_v1_6.md` §25.2.1 with new keyword-only `step_context: StepExecutionContext` parameter; CP-side `StepExecutionContext` type added at `harness-cp/src/harness_cp/workflow_driver_types.py`; driver loop composes per step + passes; existing dispatcher impls (C-RT-15 + C-RT-16) accept via Protocol conformance + pass-through. 2231 tests green at landing. ACs #4 (HandoffContext composition) + #5 (gate-descent + admissibility invocation) below reference `step_context.X` per the v1.6 Path A resolution; U-RT-59 implementation is now **unblocked** and proceeds against the L9-ter ACs at the next session.

**U-RT-59 — Sub-agent dispatch composer (Spec_Harness_Runtime_v1.md §14.7 C-RT-17)**
- Scope: implement three production surfaces. (a) `StepKindDispatcherRegistry` (frozen mapping `{StepKind → StepDispatcher}` + `lookup(step_kind) → StepDispatcher` + typed `StepKindDispatcherNotBoundError`) at `harness-runtime/src/harness_runtime/lifecycle/step_dispatchers.py`. (b) `RuntimeSubAgentDispatcher` async class at `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py` satisfying the `harness_cp.workflow_driver.StepDispatcher` Protocol; consumes `ctx.handoff_registry` + `ctx.topology_dispatcher` + `ctx.tracer_provider` + injected `ChildWorkflowRunner` callable; composer body per spec §14.7.2 ten-step discipline (payload validation → `HandoffContext` composition → gate-descent → topology admissibility → `subagent.span` open + attribute emission → child runner invocation → result mapping → audit entry composition + write → step output return → typed error propagation). (c) `ChildWorkflowRunner` Protocol + `compose_child_workflow_runner(ctx) → ChildWorkflowRunner` factory at `harness-runtime/src/harness_runtime/lifecycle/child_workflow_runner.py`; in-process recursive invocation of `execute_workflow()` per C-RT-08 surface; child shares parent `HarnessContext` at v1.6 MVP; child's binding descended per `SubAgentGateLevelDescent`; child spans nest inside `subagent.span` via OTel context propagation; child ledger entries write to same `ctx.audit_ledger_writer`. (d) Driver refactor at `harness-cp/src/harness_cp/workflow_driver.py`: parameter changes from `step_dispatcher: StepDispatcher` to `step_dispatchers: StepKindDispatcherRegistry`; call site at line 379 changes from `step_dispatcher.dispatch(binding, step)` to `step_dispatchers.lookup(step.kind).dispatch(binding, step)`. Bootstrap stage 5 (LOOP_INIT) constructs the registry with two bindings (`INFERENCE_STEP → ctx.llm_dispatcher` per U-RT-58 wrapper + `SUB_AGENT_DISPATCH → ctx.sub_agent_dispatcher` per U-RT-59 new composer) + assigns to `ctx.step_dispatchers`; assigns the dispatcher to `ctx.sub_agent_dispatcher`; runs the driver invocation against `ctx.step_dispatchers` instead of `ctx.llm_dispatcher`.
- Deps: U-RT-26 (handoff registry materialization, stage 3b); U-RT-40 (topology dispatcher materialization, stage 5); U-RT-27 (TracerProvider); U-RT-32 (audit ledger writer binding); U-RT-42 (the `execute_workflow()` surface that the ChildWorkflowRunner re-enters); U-RT-58 (the C-RT-16 wrapper that becomes the INFERENCE_STEP binding in the registry, preserved unchanged). Stage 5 wiring extension at the existing U-RT-58 binding site.
- Cross-axis deps (Pattern P1 imports): `harness_cp.workflow_driver.StepDispatcher` Protocol (same as U-RT-52/58); `harness_cp.workflow_driver_types.StepKind` enum (5-value, closed; SUB_AGENT_DISPATCH = "sub-agent-dispatch"); `harness_cp.workflow_driver_types.WorkflowStep` (step_payload opaque to driver); CP C-CP-10 §10.1 (TopologyPattern 6-class enum) + §10.3 (`is_admissible` predicate); CP C-CP-12 (`SubAgentGateLevelDescent` shape + `dispatch_sub_agent` invocation); CP C-CP-13 §13.1 (`HandoffContext` 7-field payload schema) + §13.2 (`SubAgentBrief` 4-field) + §13.5 (`LedgerEntryRef` + audit-trail-link composition); CP C-CP-14 §14.1 (multi-agent span hierarchy — narrow single-sub-agent slice; fan-out envelope NOT emitted at v1.6) + §14.2 (`subagent.*` 7-attribute namespace + `topology.*` 2-attribute subset); CP C-CP-25 §25.2 (driver signature) + §25.3.3.4 (step body opaque to driver — preserved by routing on `step.kind` only).
- AC #1: `harness-runtime/src/harness_runtime/lifecycle/step_dispatchers.py` exists; defines frozen `StepKindDispatcherRegistry` Pydantic v2 dataclass; `lookup(step_kind)` returns the bound `StepDispatcher` or raises `StepKindDispatcherNotBoundError`; registry is constructed with at least 2 bindings at bootstrap stage 5 (INFERENCE_STEP + SUB_AGENT_DISPATCH).
- AC #2: `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py` exists; defines async `RuntimeSubAgentDispatcher` class; `isinstance(RuntimeSubAgentDispatcher(...), StepDispatcher)` returns `True` via `runtime_checkable` introspection at `harness_cp.workflow_driver:151`.
- AC #3: SubAgentDispatchPayload Pydantic v2 validation verified — mock step with mis-shaped `step_payload` raises `SubAgentDispatchPayloadShapeError`; mapped to `RT-FAIL-PAYLOAD-SHAPE` fail class semantics; verify shape (`child_workflow_id`, `child_manifest_entry`, `child_steps`, `brief`) extraction from valid payload.
- AC #4: HandoffContext composition verified — composer constructs C-CP-13 §13.1 7-field `HandoffContext` from step inputs + `step_context: StepExecutionContext` per `Spec_Control_Plane_v1_6.md` §25.2.1 Path A resolution; verify the 7 fields populated per spec §14.7.3 v1.6 MVP shape (proposed_action from brief.objective; agent_confidence None; failed_attempts empty; alternatives_considered empty; state_summary with parent_entry_ref + empty summary keyed on `step_context.parent_idempotency_key`; audit_trail_link composed as `LedgerEntryRef(action_id=step_context.parent_action_id, entry_hash=step_context.parent_entry_hash, actor=step_context.parent_actor)`; retry_history empty).
- AC #5: gate-level descent + topology admissibility verified — composer calls `ctx.handoff_registry.dispatch(parent_action_id=step_context.parent_action_id, parent_gate_level=step_context.parent_gate_level, parent_sandbox_tier=step_context.parent_sandbox_tier, sub_agent_brief=payload.brief, operator_override=None)` per v1.6 Path A resolution and receives `SubAgentGateLevelDescent`; composer calls `ctx.topology_dispatcher.dispatch(child_manifest_entry)` and receives `TopologyPattern`; composer calls `is_admissible(topology, workload_class)` and respects the verdict (proceeds on True; raises `SubAgentDispatchTopologyInadmissibleError` mapping to `RT-FAIL-SUB-AGENT-TOPOLOGY-INADMISSIBLE` on False).
- AC #6: `subagent.span` + narrow-subset `topology.*` emission verified — exactly one `subagent.span` per composer invocation; span carries `subagent.span.id` (16-hex) + `subagent.parent_span_id` (16-hex) + `subagent.result_status` (set at close) + `subagent.request_blocked_by_budget` (bool) + `subagent.tokens_in` / `subagent.tokens_out` / `subagent.cached_tokens_in` (int; 0 if child does not surface). Span carries `topology.pattern` (string-value of TopologyPattern enum) + `topology.workload_class` (string-value of WorkloadClass enum). Span does NOT carry the 8 fan-out-specific `topology.*` attributes (`fan_out_cap`, `cascade_policy`, `results_collected`, `results_failed`, `cascade_applied`, `synthesis_token_budget`, `cascade_decision_audit_ledger_id`, `concurrent_token_budget_at_dispatch`) — explicit assertion of absence. Attribute carrier imported from `harness_cp.handoff_context` (no hand-coded strings).
- AC #7: `ChildWorkflowRunner` recursive invocation verified — mock parent workflow with a SUB_AGENT_DISPATCH step that invokes a child workflow (3 declarative steps in the child); assert child's `workflow.start` span nests inside `subagent.span` via OTel parent-span-id linkage (verify via `InMemorySpanExporter`); assert child's terminal `RunResult.status == SUCCESS`; assert child's `final_state` is returned to the parent composer; assert child's audit-ledger entries land in the same ledger writer (verify entry count delta).
- AC #8: child result mapping verified — three sub-cases. (a) Child SUCCESS → `subagent.result_status = "completed"`; composer returns child `final_state`; no error raised. (b) Child DRAINED → `subagent.result_status = "completed"`; composer returns child `partial_state`. (c) Child FAILED → `subagent.result_status = "failed"`; composer raises `SubAgentChildFailedError` mapping to `RT-FAIL-SUB-AGENT-CHILD-FAILED`; audit entry composed + emitted with `child_result_status="failed"` before raise.
- AC #9 (v2.6 — UN-STRUCK; full 4-substep sequence per runtime spec v1.7 §14.7.2 step 8): composer body materializes the 4-substep audit composition + persistence sequence. **8a** compose `CPAuditLedgerEntry` via `ctx.handoff_registry.compose_dispatch_audit(parent_action_id, descent, brief_hash)`. **8b** F2-write the dispatch action via `ctx.ledger_writer.append(payload, write_key)` where `action_id = Identifier(f"dispatch:{parent_action_id}:{descent.child_index}")` (Q2(a) ratification — composer writes F2 BEFORE composing OD audit). **8c** convert CP→OD via `cp_audit_to_od_audit(cp_entry, key_id=audit_signing_key_id, algo=audit_signing_algorithm, entry_core=StateLedgerEntryRef(str(dispatch_action_id)))` per CP spec v1.7 §13.5.1 converter contract + OD spec v1.5 C-OD-24.4 opaque-str discipline (action_id-as-marker; spec narrative cites "entry_hash" — Class 3 prose-drift carry-forward since `LedgerWriter.append` does not expose the forward chain hash). **8d** persist via `ctx.audit_writer.append(tenant_id=step_context.tenant_id, audit_entry=od_entry)` per C-RT-04 + OD spec v1.5 C-OD-24 + ADR-D5 v1.4 §1.4 (JSONL via IS state-ledger composition). Failure semantics: on SUCCESS / DRAINED child paths, any error at 8b/8c/8d raises typed `SubAgentDispatchAuditComposeError` → driver maps to `RT-FAIL-SUB-AGENT-AUDIT-COMPOSE` (new fail class at runtime spec v1.7 §14). On FAILED / exception-bubble paths the 4-substep is best-effort + failures swallowed so the primary fault (`SubAgentChildFailedError` / original exception) is what surfaces per spec §14.7.2 step 8 failure-semantics paragraph. Test coverage: per-substep verification (`test_dispatcher_takes_audit_writer_kwarg_at_v1_7`, `test_step8a_composes_cp_audit_entry`, `test_step8b_writes_f2_dispatch_action_entry`, `test_step8c_8d_persists_od_audit_entry_through_writer`) + failure semantics (`test_step8b_failure_raises_audit_compose_error_on_success_path`, `test_step8_failure_swallowed_on_failed_child_path`) + integration (`test_three_sequential_dispatches_chain_through_audit_writer` — three dispatches; IS chain verification VALID).
- AC #10: driver routing-layer refactor verified — driver invoked with `ctx.step_dispatchers: StepKindDispatcherRegistry` (NOT a single `step_dispatcher: StepDispatcher`); driver dispatches via `step_dispatchers.lookup(step.kind).dispatch(binding, step)` at line 379; verify driver still does not introspect `step.step_payload` (preserves C-CP-25 §25.3.3.4 "step body opaque to driver" invariant — verified by mocking a step with arbitrary opaque payload and asserting driver does not touch it before delegation). Verify unbound step_kind (e.g., `DECLARATIVE_STEP` at v1.6) raises `StepKindDispatcherNotBoundError` → driver maps to `RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND`.
- AC #11: bootstrap stage 5 wiring verified — `ctx.step_dispatchers` post-condition is a populated `StepKindDispatcherRegistry` with INFERENCE_STEP + SUB_AGENT_DISPATCH bindings after stage 5; `ctx.sub_agent_dispatcher` post-condition is `isinstance(..., RuntimeSubAgentDispatcher)`; `ctx.llm_dispatcher` post-condition preserved (still `isinstance(..., RetryBreakerFallbackDispatcher)` per U-RT-58); verify by `test_bootstrap_stage.py` extension.
- AC #12: Phase 7d retirement-event prerequisite — after U-RT-59 lands, file batch 4 retirement event records for **H_T-CP-10** RETIRED + **H_T-CP-13** RETIRED + **H_T-CP-14** PARTIAL or RETIRED (single-sub-agent slice per spec §14.7 X-AL-2 retirement implications) per `.harness/phase-7d-retirement-events-batch-1.md` shape under v2 ledger §5 CP-row evidence framework (condition B verified end-to-end at the new composer site). Operator ratifies CP-14 RETIRED vs PARTIAL at retirement audit per X-AL-2 strict reading. Updates `harness-cp/CLAUDE.md` §4.1 substitution-table status entries.

---

### L9-quater — HITL gate composer + `AskUserQuestionSurface` H_E delivery Protocol (new at v1.9 / v2.7; in-CLI spec growth — **Class 1 fork RESOLVED at spec authoring**)

> **✅ Class 1 fork RESOLVED at spec authoring.** Operator ratified all 5 systems-architect mode 3 recommendations 2026-05-20 (fork record `.harness/class_1_tension_cp_20_hitl_gate_composer_underspec.md`; spec landed at HEAD `2685774`). Architecture is fully frozen for U-RT-60 implementation. Four path-(ii) NOTEs pre-empted at spec §14.8.7 (vs U-RT-59's discovery-at-implementation pattern that surfaced 4 NOTEs post-landing at adversarial review) — each NOTE is mirrored as an AC below (NOTE 6-i / 6-ii / 6-iii / 6-iv) so the deferral surface is auditable at implementation time.

**U-RT-60 — HITL gate composer (Spec_Harness_Runtime_v1.md §14.8 C-RT-18)**
- Scope: implement three production surfaces. (a) `RuntimeHITLGateComposer` async class at `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` satisfying the `harness_cp.workflow_driver.StepDispatcher` Protocol (same duck-typing pattern as U-RT-52/58/59); wraps an inner `StepDispatcher` and produces a HITL-gated `StepDispatcher`; per-step async composer body per spec §14.8.2 6-step discipline (read placement triggers → filter by applicable_placements → foreclose VALIDATOR_ESCALATION → per-placement loop [HandoffContext compose / matrix cell resolve / `_hitl_required` bounded read / palette determine / `hitl.gate.evaluated` span open / AskUserQuestion invoke / `hitl.invocation.responded` span / 4-substep audit-write / 4-response process] → delegate to inner → return). Constructor signature per spec §14.8.1: `RuntimeHITLGateComposer(inner: StepDispatcher, applicable_placements: frozenset[HITLPlacementKind], hitl_placement: HITLPlacementRegistry, handoff_registry: HandoffRegistry, ask_user_question_surface: AskUserQuestionSurface, state_ledger_writer: StateLedgerWriter, audit_writer: AuditLedgerWriter, tracer_provider: TracerProvider, audit_signing_key_id: str, audit_signing_algorithm: SignatureAlgorithm)`. (b) `AskUserQuestionSurface` Protocol at `harness-runtime/src/harness_runtime/lifecycle/ask_user_question_surface.py` with one async method `ask(prompt, options, timeout) -> AskUserQuestionResult`; H_E binding at v1.9 MVP wraps Claude Code's `AskUserQuestion` mechanism (synchronous operator-turn invocation per Q1 ratification); Protocol surface H_T-canonical (replaceable post-bootstrap by `deliver_webhook` per future C-RT-19 / U-RT-61 arc — Q4 ratification). (c) Bootstrap stage 5 (LOOP_INIT) wrap-chain construction per spec §14.8.1 wrap-asymmetry table (Q2 ratification): single-instance-per-step_kind at v1.9 MVP — one `INFERENCE_STEP`-targeted instance with `applicable_placements={PRE_ACTION}` wrapped *inside* C-RT-16 retry (`ctx.llm_dispatcher = c_rt_16_compose(hitl_gate_composer(c_rt_15, applicable_placements={PRE_ACTION}))`) + one `SUB_AGENT_DISPATCH`-targeted instance with `applicable_placements={SUB_AGENT_BOUNDARY}` wrapping C-RT-17 directly (`ctx.sub_agent_dispatcher = hitl_gate_composer(c_rt_17, applicable_placements={SUB_AGENT_BOUNDARY})` — no retry layer); TOOL_STEP / DECLARATIVE_STEP / HITL_STEP not bound at v1.9 (future arcs).
- Deps: U-RT-12 (state-ledger writer); U-RT-25 (HITL placement registry — production callsite changes from co-stubbed `NotImplementedError` at `harness-runtime/lifecycle/hitl_placement.py:22` to composer consumer); U-RT-26 (handoff registry, stage 3b); U-RT-27 (TracerProvider); U-RT-32 (audit ledger writer binding); U-RT-58 (C-RT-16 retry/breaker/fallback composer — becomes outer wrap at INFERENCE_STEP per Q2 wrap-asymmetry); U-RT-59 (C-RT-17 sub-agent dispatch composer — becomes inner of HITL gate at SUB_AGENT_DISPATCH per Q2 wrap-asymmetry); U-RT-42 (`execute_workflow()` surface — the workflow-driver invocation that consumes `ctx.step_dispatchers`). Stage 5 wiring extension at the existing U-RT-58 + U-RT-59 binding site.
- Cross-axis deps (Pattern P1 imports): `harness_cp.workflow_driver.StepDispatcher` Protocol (same as U-RT-52/58/59); `harness_cp.workflow_driver_types.StepKind` enum + `StepExecutionContext` per `Spec_Control_Plane_v1_6.md` §25.2.1 Path A; CP C-CP-16 §16.1 (4-response palette: APPROVE / EDIT / REJECT / RESPOND) + §16.2 (per-response audit shapes — `CPAuditLedgerEntry` HITL-canonical at origin) + §16.3 (palette invariants) + §16.4 (response-handling invariants); CP C-CP-17 §17.1 (3-placement enum: PRE_ACTION / SUB_AGENT_BOUNDARY / VALIDATOR_ESCALATION) + §17.2 (HITL-as-tool-call rewriting interface — cited for traceability; not operationalized at v1.9 per TOOL_STEP foreclosure) + §17.3 (HITLPlacement schema); CP C-CP-18 §18.1–§18.5 (persona-tier × engine-class matrix + overlay + observer + binding-selection — composer reads matrix cell at step 4b); CP C-CP-19 §19.1 (`_hitl_required` 4-axis composition — v1.9 MVP uses bounded reading from `placement.requires_hitl` only; full 4-axis composition deferred to validator-composer arc per Q5 dependency); CP C-CP-20 §20.4 (`audit.*` 7-attribute namespace + per-persona-tier monotonic ascending emission rule) + §20.5 (`hitl.*` 4-attribute span schema: `hitl.gate.evaluated.placement` + `hitl.gate.evaluated.response_palette` + `hitl.invocation.responded.response_class` + `hitl.invocation.responded.response_latency_ms`) + §20.6 (HITL-event span schema); CP C-CP-25 §25.2 (driver signature with `step_dispatchers: StepKindDispatcherRegistry` per U-RT-59 refactor) + §25.3.3.4 (step body opaque to driver — preserved); CXA v2.5 §2.3.7 (CP→OD bucket grows 1→2 typed seams; new U-CP-46 → U-OD-00 HITL audit-write seam alongside existing U-CP-28 → U-OD-00 sub-agent dispatch seam — shares `cp_audit_to_od_audit` converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py`).
- AC #1: `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` exists; defines async `RuntimeHITLGateComposer` class with constructor matching spec §14.8.1 signature (10-parameter); `isinstance(RuntimeHITLGateComposer(...), StepDispatcher)` returns `True` via `runtime_checkable` introspection at `harness_cp.workflow_driver:151`; `applicable_placements` field is `frozenset[HITLPlacementKind]` (immutable post-construction per spec §14.8.6 Invariants).
- AC #2 (v2.8 absorption per spec v1.10 §14.8.3 Q1 pin + F1-01 deferred-list enumeration): `harness-runtime/src/harness_runtime/lifecycle/ask_user_question_surface.py` exists; defines `AskUserQuestionSurface` Protocol with one async method `ask(prompt: str, options: Sequence[HITLResponseOption], timeout: Duration | None) -> AskUserQuestionResult`; `AskUserQuestionResult` Pydantic v2 model carries `HITLResponse` + optional `edited_proposal` / `response_text` / `rejection_reason` + `latency_ms`; bootstrap stage 5 binds `ctx.ask_user_question_surface` to an H_E-backed implementation **via the MCP-server substitution-mechanism category** per `Phase_7_Meta_Architecture_v1.md` §5.7 (12-entry MCP-server category) — implementation MUST emit the tool call through an MCP host (`harness-as.mcp_transport_floor` per U-RT-15 lifecycle); an MCP-server-side handler intercepts the call, dispatches to Claude Code's `AskUserQuestion` mechanism with the composed prompt + 4-response palette options + timeout, awaits the operator's response, and re-injects the result through the MCP response channel back to the runtime coroutine. Chain-grounded against workspace `CLAUDE.md` invariant I-4 + `Phase_7_Meta_Architecture_v1.md` §7 X-AL-1 ("H_E ↔ H_T substrate boundary at MCP server process; process isolation, not convention") + AS-AL-2 line 522 ("all H_T tool surface lives behind MCP server boundary"). Protocol surface itself H_T-canonical for future durable-async swap per C-RT-19 / U-RT-61 arc (Q4 ratification — durable-async impl stays inside the MCP envelope, transparent to H_T runtime). **Deferred-list items inherited by U-RT-60 implementation (per F1-01 absorption; cite spec v1.10 §14.8 deferred-list):** `compose_gate_prompt(placement, handoff_context)` shape; `compose_hitl_action_id(parent_action_id, placement_position)` construction shape (suggest `f"hitl:{parent_action_id}:{placement_position.value}"`); MockAskUserQuestionSurface fixture shape per spec v1.10 MUST-language upgrade (Protocol-level mock MUST satisfy Protocol; queue-of-canned-results shape reference for unit-test layer; integration-test MCP-host-side handler fixture at impl discretion); `AskUserQuestionSurface` construction timing (suggest stage 5); `_hitl_required` predicate evaluation at composer body step 4c reads from `placement.requires_hitl` only at v1.9/v1.10 MVP (full 4-axis composition deferred to validator-composer arc).
- AC #3: placement-trigger filter + empty-placements skip path verified (spec §14.8.2 steps 1–2) — mock step with `step.hitl_placements = []` → composer delegates directly to inner dispatcher without opening any HITL spans; mock step with non-empty `hitl_placements` but none matching `self.applicable_placements` → same; mock step with at least one matching placement → composer proceeds to step 3 evaluation.
- AC #4 (Q5 mirror + spec §14.8.2 step 3 + §14.8.4 foreclosure): VALIDATOR_ESCALATION foreclosure verified — mock step with any placement carrying `position == VALIDATOR_ESCALATION` → composer raises typed `HITLPlacementForeclosedAtV19Error` mapping to `RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19` fail class (new at runtime spec v1.9 §14.8 failure-mode taxonomy); test asserts the placement-trigger evaluator returns `no-placement-match` for VALIDATOR_ESCALATION at v1.9 MVP per Q5 ratification; cardinality-3 invariant at `HITL_PLACEMENT_TRIGGERS` typed library preserved (foreclosure is at runtime-invocation-binding layer only, NOT at library cardinality).
- AC #5 (spec §14.8.2 steps 4a + 4b + 4c): HandoffContext composition + persona-tier × engine-class matrix cell resolution + `_hitl_required` bounded reading verified — composer composes C-CP-13 §13.1 7-field `HandoffContext` per the §14.7.2 step 2 discipline (re-used verbatim from C-RT-17; `audit_trail_link` sourced from `step_context.parent_action_id` + `parent_entry_hash` + `parent_actor` per `Spec_Control_Plane_v1_6.md` §25.2.1 Path A); composer calls `matrix_cell_for(persona_tier=binding.persona_tier, engine_class=binding.engine_class)` per C-CP-18 §18.1 and raises `HITLCellExcludedError` mapping to new fail class on `cell.is_excluded`; composer reads `_hitl_required` from `placement.requires_hitl` bool only at v1.9 MVP per spec §14.8.2 step 4c (full 4-axis composition per C-CP-19 §19.1 deferred to validator-composer arc per Q5 dependency analysis); when `placement.requires_hitl == False` → composer skips to step 4j (no gate fires).
- AC #6 (NOTE 6-iv mirror + spec §14.8.2 step 4d + §14.8.7 NOTE 6-iv): response palette = `DEFAULT_FULL_PALETTE = frozenset({APPROVE, EDIT, REJECT, RESPOND})` unconditionally at v1.9 MVP per spec §14.8.2 step 4d. Cross-trust-boundary palette restriction per C-CP-19 §19.4 + U-CP-48 `PALETTE_RESTRICTION_TABLE` is **deferred to validator-composer + MCP-trust-framework arcs** per `Spec_Harness_Runtime_v1.md` §14.8.7 NOTE 6-iv — composer does NOT consult `cross_trust_boundary_state`. Test asserts that for any `cross_trust_boundary_state` value the palette presented to operator is the full 4-response set; deferral comment cites NOTE 6-iv verbatim so the future-arc absorption surface is auditable.
- AC #7 (v2.9 absorption per spec v1.11 §14.8.2 step 4e + §14.8.5 + ADR-D5 v1.3 §1.8 row 1 + CP carrier `HITL_SPAN_NAMESPACE_SCHEMA[0]`): `hitl.gate.evaluated` span emission verified — exactly one `hitl.gate.evaluated` span per matching placement (spec §14.8.6 Invariants); span carries the canonical 3-attribute set per ADR-D5 v1.3 §1.8 row 1: `hitl.gate.level` (from `cell.gate_level` — cardinality-safe metric dimension) + `hitl.gate.persona_tier` (from `binding.persona_tier`) + `hitl.gate.required` (`bool` — from the step-4c `_hitl_required` outcome: `True` when the gate fires, `False` when skipped to step 4j); gate span fires regardless of `_hitl_required` outcome per `Spec_Control_Plane_v1_9.md` U-CP-46 AC #10 (the `.required` attribute carries the outcome). **v2.9 amendment per Q1+Q2 resolution at `.harness/class_1_tension_c_rt_18_hitl_span_attribute_carrier_drift.md`:** v2.8 references to hand-coded `hitl.gate.evaluated.placement` + `.response_palette` + `.outcome` attribute names are retired (v1.9/v1.10 narrative drift; the placement attribute lives canonically on `hitl.invocation.opened` per AC #8 step 4f-bis; the response-palette semantic content is implicit at the step 4h audit-entry composition; the outcome semantic is carried at canonical 4-span shape per AC #8). On timeout path: composer opens canonical `hitl.invocation.timed_out` dedicated span per AC #8 (NOT a `.outcome="timeout"` attribute extension). On audit-compose failure path: composer annotates `hitl.gate.evaluated` span via OTel `Span.set_status(StatusCode.ERROR)` + `Span.record_exception(typed_error)` per semconv-canonical error discipline (NOT a `.outcome="audit-compose-failed"` attribute extension); the `RT-FAIL-HITL-GATE-AUDIT-COMPOSE` fail class is preserved unchanged (only the span-annotation mechanism conforms to canonical OTel status discipline).
- AC #8 (v2.9 absorption per spec v1.11 §14.8.2 step 4f + step 4f-bis + step 4g + fail class `RT-FAIL-HITL-GATE-TIMEOUT` + ADR-D5 v1.3 §1.8 rows 2/3/4 + CP carrier `HITL_SPAN_NAMESPACE_SCHEMA[1/2/3]`): AskUserQuestion invocation + canonical 4-span shape emission verified. Composer body materializes the §14.8.2 step 4f / 4f-bis / 4g sequence: composer calls `await ctx.ask_user_question_surface.ask(prompt=compose_gate_prompt(placement, handoff_context), options=[...], timeout=placement.timeout)`; before awaiting, opens canonical `hitl.invocation.opened` span per spec §14.8.2 step 4f-bis (NEW at v1.11) with 4-attribute set per ADR-D5 v1.3 §1.8 row 2: `hitl.gate.level` (cross-event reference; same canonical attribute as on gate-evaluated span — value from `cell.gate_level`) + `hitl.invocation.placement` (string-value of `placement.position` — **canonical home for the placement attribute**) + `hitl.invocation.handoff_context_size_bytes` (computed from `handoff_context` serialization size; impl-discretion shape per spec v1.11 deferred-list — suggested `len(handoff_context.model_dump_json().encode("utf-8"))`) + `hitl.invocation.audit_ledger_entry_id` (set at step 4h completion when the F2 dispatch entry's `action_id = f"hitl:{step_context.parent_action_id}:{placement.position.value}"` is known; OTel set-attribute-deferred discipline). **On response received** → composer opens `hitl.invocation.responded` span per spec §14.8.2 step 4g with canonical 3-attribute set per ADR-D5 v1.3 §1.8 row 3: `hitl.response.class` (string-value of `gate_result.response` — cardinality-safe metric dimension ∈ `approve` / `edit` / `reject` / `respond` per C-CP-16 §16.1) + `hitl.response.latency_ms` (= `gate_result.latency_ms`) + `hitl.response.summary_hash` (cardinality-safe per-response content digest; impl-discretion content shape per spec v1.11 deferred-list — suggested sha256 of one of the per-response hash fields from step 4h substep 8a-HITL: `edited_proposal_hash` when response==EDIT / `response_text_hash` when response==RESPOND / `rejection_reason_hash` when response==REJECT / `sha256(b"")` empty-hash when response==APPROVE). **On `placement.timeout` elapse** → surface raises `AskUserQuestionTimeoutError` → composer opens canonical `hitl.invocation.timed_out` dedicated span per spec §14.8.2 step 4f + ADR-D5 v1.3 §1.8 row 4 with 2-attribute set: `hitl.timeout.duration_ms` (= `placement.timeout` converted to milliseconds — pre-elapsed budget) + `hitl.timeout.degradation_mode_applied` (string-value from per-persona-tier `harness_cp.hitl_timeout_degradation` consult at audit-entry composition; semantic equivalent of audit `audit.policy.*` namespace value derivation); composer raises `HITLGateTimeoutError` mapping to `RT-FAIL-HITL-GATE-TIMEOUT` fail class. On timeout path: composer emits partial audit entry with `response=None`; does NOT emit `hitl.invocation.responded` span (per U-CP-46 AC #11 + canonical 4-span shape per spec v1.11 §14.8.5 hierarchy diagram). **v2.9 amendment per Q1+Q2 resolution at `.harness/class_1_tension_c_rt_18_hitl_span_attribute_carrier_drift.md`:** v2.8 references to hand-coded `hitl.invocation.responded.response_class` / `.response_latency_ms` retired (renamed to canonical `hitl.response.class` / `hitl.response.latency_ms` per ADR-D5 §1.8 row 3 + CP carrier); previously-dropped `hitl.response.summary_hash` is pulled in at the canonical name. v2.8 reference to `hitl.gate.evaluated.outcome="timeout"` attribute extension retired (canonical `hitl.invocation.timed_out` dedicated span is the authoritative timeout-outcome surface).
- AC #9 (spec §14.8.2 step 4h + §14.8.6 + CXA v2.5 §2.3.7 + fail class `RT-FAIL-HITL-GATE-AUDIT-COMPOSE`): 4-substep audit-write HITL-flavor verified — composer body materializes the §14.7.2 step 8 4-substep sequence with HITL-specific differences. **8a-HITL** `cp_entry = compose_hitl_response_audit(action_id=compose_hitl_action_id(step_context.parent_action_id, placement.position), gate_level=cell.gate_level, response=gate_result.response, edited_proposal_hash=sha256(gate_result.edited_proposal) if response==EDIT else None, rejection_reason_hash=sha256(gate_result.rejection_reason) if response==REJECT else None, response_text_hash=sha256(gate_result.response_text) if response==RESPOND else None)` — `response` populates per operator's actual response (one of `{approve, edit, reject, respond}`) per CP spec v1.9 §13.5.1 NOTE 5 (HITL-canonical at origin; unlike sub-agent dispatch which uses `response="approve"` via convention). **8b-HITL** F2 state-ledger entry write with `action_id = Identifier(f"hitl:{step_context.parent_action_id}:{placement.position.value}")` — `hitl:` prefix is the HITL-source discriminator at OD audit-trace consumers (matches `dispatch:` prefix discriminator at §14.7.2 step 8b). **8c-HITL** `od_entry = cp_audit_to_od_audit(cp_entry, key_id=ctx.audit_signing_key_id, algo=ctx.audit_signing_algorithm, entry_core=StateLedgerEntryRef(<step-8b-HITL entry_hash>))` — **same `cp_audit_to_od_audit` converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` shared with U-RT-59 sub-agent dispatch per Q3 ratification** (HITL-canonical at origin); no parallel converter. **v2.8 carry-forward acknowledgment (F2-03 absorption):** the spec literal `entry_core=StateLedgerEntryRef(<step-8b-HITL entry_hash>)` reproduces the same prose-form-vs-implementation drift surfaced at the U-RT-59 implementation arc (Class 3 prose-drift item 5 per `.harness/class_3_tension_u_rt_59_spec_prose_drift.md`). The U-RT-59 production callsite uses `StateLedgerEntryRef(str(dispatch_action_id))` — the action_id-as-opaque-str discipline per `Spec_Operational_Discipline_v1_5.md` C-OD-24.4 — because `LedgerWriter.append` does not expose the forward chain hash. U-RT-60 implementation inherits this pattern transparently via the shared `cp_audit_to_od_audit` converter (the converter already handles the opaque-str passthrough per the landed U-RT-59 impl at `harness-cxa/src/harness_cxa/cp_audit_conversion.py:_project_namespace_attrs`); the HITL-flavor substep 8b-HITL constructs `action_id = Identifier(f"hitl:{step_context.parent_action_id}:{placement.position.value}")` and substep 8c-HITL passes `StateLedgerEntryRef(str(<that action_id>))` per the carry-forward convention. Implementation arc does NOT re-derive; no new fork required. **8d-HITL** `write_result = ctx.audit_writer.append(tenant_id=step_context.tenant_id, audit_entry=od_entry)`. Failure semantics: on APPROVE / EDIT / RESPOND paths, any error at 8b-HITL / 8c-HITL / 8d-HITL raises typed `HITLGateAuditComposeError` → driver maps to `RT-FAIL-HITL-GATE-AUDIT-COMPOSE`; **suppressed on REJECT path** — `HITLGateRejectedError` is primary fault (audit-fact-preservation discipline matches §14.7 v1.7 audit-suppression-on-failed pattern). CXA v2.5 §2.3.7 absorbs the new typed seam (U-CP-46 → U-OD-00); test verifies the second seam realizes Pattern P1 byte-exact alignment (extends U-RT-51 seam-count from 22 → 23).
- AC #10 (NOTE 6-ii mirror + spec §14.8.2 step 4i + §14.8.7 NOTE 6-ii + fail class `RT-FAIL-HITL-GATE-REJECTED`): 4-response processing verified per C-CP-16 §16.1 palette. **APPROVE** → composer proceeds to step 5 (delegate to inner dispatcher) with `step` unchanged. **EDIT** → composer mutates `step.step_payload` by **replacement** (`gate_result.edited_proposal` becomes new `step_payload` verbatim) per v1.9 MVP shape; `edited_proposal_hash` audit field captures post-mutation payload hash (not diff); **richer mutation semantics (field-level patches, type-aware merging, multi-version-history-tracking) deferred to future workflow-mutation-discipline arc** per `Spec_Harness_Runtime_v1.md` §14.8.7 NOTE 6-ii — implementation MUST replace-not-merge; consumers MUST treat `gate_result.edited_proposal` as authoritative replacement. **REJECT** → composer raises `HITLGateRejectedError` mapping to `RT-FAIL-HITL-GATE-REJECTED` fail class (new at v1.9); rejection audit entry from step 4h carries `rejection_reason_hash` and is preserved even if step 4h substeps fail (per AC #9 audit-suppression-on-REJECT discipline). **RESPOND** → composer records `response_text_hash` in audit entry (8a-HITL) but does NOT inject response text into `step.step_payload` (RESPOND is "continue dialogue without action" per C-CP-16 §16.1 row 4 + U-CP-37 AC #7); proceeds to step 5 with `step` unchanged. NOTE 6-ii deferral comment in composer source cites `§14.8.7 NOTE 6-ii` verbatim.
- AC #11 (NOTE 6-i mirror + spec §14.8.2 step 4 per-placement loop + §14.8.7 NOTE 6-i): multi-placement same-step independence verified — when `step.hitl_placements` declares multiple matching placements (e.g., one step declares both PRE_ACTION + SUB_AGENT_BOUNDARY with overlapping `applicable_placements`), each placement evaluates independently per the §14.8.2 step 4 loop; each placement's audit entry uses a distinct `action_id` (includes `placement.position.value` per substep 8b-HITL); sibling-distinguishability via IS-anchored `entry_core` preserved (each placement's F2 entry has its own action_id pattern matching `hitl:{parent_action_id}:{position.value}`). At v1.9 MVP this case is not exercised by existing C-CP-25 §25.3.3 step body shapes (single step typically declares 0 or 1 placement matching a given composer's `applicable_placements`); the contract supports it per `Spec_Harness_Runtime_v1.md` §14.8.7 NOTE 6-i but operator workflows that exercise it are deferred to a future workflow-grammar arc. **Test design (v2.8 amendment per F2-02 absorption):** the original v2.7 test specification (2-placement case "PRE_ACTION + SUB_AGENT_BOUNDARY on a single step") tested an impossible-at-v1.9/v1.10-MVP case — the step-kind routing discipline (single-instance-per-step_kind composer per spec §14.8.1 with `applicable_placements={PRE_ACTION}` or `={SUB_AGENT_BOUNDARY}`) filters out cross-position placements at composer body step 2 before they ever reach the per-placement loop. The exercise-able NOTE 6-i case at v1.9/v1.10 MVP is **multiple placements of the same `position` value** on a single step (e.g., two PRE_ACTION placements on a single INFERENCE_STEP step — one for "review the prompt", one for "approve model selection"; both match the composer's single-element `applicable_placements={PRE_ACTION}` and both fire in the §14.8.2 step 4 per-placement loop). Test asserts each placement evaluates independently per the §14.8.2 step 4 loop; each gets a distinct `action_id` per the §14.8.2 step 4h substep 8b-HITL action_id prefix shape `hitl:{parent_action_id}:{placement.position.value}` (where both same-position placements share the prefix but distinguish via in-loop iteration index or distinct placement-instance UUIDs per implementation-discretion sub-shape); no action_id collision; both HITL gate evaluations fire; both audit entries reach the writer (verify via 2-entry delta against fresh ledger); NOTE 6-i deferral comment in composer source cites `§14.8.7 NOTE 6-i` verbatim. **v2.9 assertion-shape note (canonical 4-span shape per spec v1.11):** the 2-placement test asserts each matching placement produces exactly one `hitl.gate.evaluated` span + exactly one `hitl.invocation.opened` span + exactly one of (`hitl.invocation.responded` OR `hitl.invocation.timed_out`) per matching placement — i.e., 2× gate.evaluated + 2× invocation.opened + 2× invocation.responded (assuming both placements receive responses) at the 2-placement same-position case (canonical 4-span emission discipline per spec v1.11 §14.8.5 hierarchy diagram + §14.8.6 Invariants).
- AC #12 (NOTE 6-iii mirror + spec §14.8.1 wrap-asymmetry table row 1 + §14.8.7 NOTE 6-iii): retry-of-gate semantics at INFERENCE_STEP wrap-chain verified — bootstrap stage 5 wrap-chain produces `ctx.llm_dispatcher = c_rt_16_compose(hitl_gate_composer(c_rt_15, applicable_placements={PRE_ACTION}))` per spec §14.8.1 row 1 (Q2 ratification: C-RT-16 retry is outer of HITL gate). When inner LLM dispatch fails and C-RT-16 triggers a new attempt, the wrapper re-enters HITL gate composer at step 1 of §14.8.2 — **operator is re-asked on each retry attempt** per literal Q2 reading. v1.9 MVP accepts this; operator-burden mitigation via `retry.*` attempt cap per C-CP-03 §3.5 jittered backoff; **approve-once-cache-for-retry-attempts optimization deferred to future ops-burden-reduction arc** per `Spec_Harness_Runtime_v1.md` §14.8.7 NOTE 6-iii — v1.9 MVP emits one audit entry per attempt (no cached-approve). Test: mock 3-attempt retry sequence where inner LLM dispatch fails (transient) → succeeds on attempt 3; assert HITL gate evaluated 3 times (3× `hitl.gate.evaluated` spans + 3× `hitl.invocation.responded` spans + 3× audit entries with distinct timestamps); NOTE 6-iii deferral comment in composer source cites `§14.8.7 NOTE 6-iii` verbatim. SUB_AGENT_DISPATCH wrap-chain (`ctx.sub_agent_dispatcher = hitl_gate_composer(c_rt_17, applicable_placements={SUB_AGENT_BOUNDARY})` per spec §14.8.1 row 2) verified to have NO retry layer at v1.9 (HITL gate fires once per dispatch).
- AC #13 (spec §14.8.1 wrap-asymmetry table + bootstrap stage 5 wiring): bootstrap stage 5 wrap-chain construction verified — `ctx.llm_dispatcher` post-condition produces exactly the wrap chain in spec §14.8.1 row 1 (`isinstance(ctx.llm_dispatcher, RetryBreakerFallbackDispatcher)` per U-RT-58 preserved; `ctx.llm_dispatcher.inner` is the HITL-gated layer; `ctx.llm_dispatcher.inner.inner` is the bare `RuntimeLLMDispatcher` per U-RT-52); `ctx.sub_agent_dispatcher` post-condition produces exactly the wrap chain in spec §14.8.1 row 2 (`isinstance(ctx.sub_agent_dispatcher, RuntimeHITLGateComposer)` with `applicable_placements={SUB_AGENT_BOUNDARY}`; `ctx.sub_agent_dispatcher.inner` is the bare `RuntimeSubAgentDispatcher` per U-RT-59); `ctx.step_dispatchers: StepKindDispatcherRegistry` per U-RT-59 routing layer continues to dispatch via `step_dispatchers.lookup(step.kind)` (driver invocation unchanged); TOOL_STEP / DECLARATIVE_STEP / HITL_STEP not bound at v1.9 (lookup raises `StepKindDispatcherNotBoundError` per U-RT-59 AC #10). Verified by `test_bootstrap_stage.py` extension; producer-side carrier import discipline per spec §14.8.5 also verified (composer imports `hitl.*` + `audit.*` attribute name set from `harness_cp.audit_hitl_span_namespace.AUDIT_NAMESPACE_SCHEMA` + `HITL_SPAN_NAMESPACE_SCHEMA` per U-CP-46; hand-coded attribute strings NOT permitted — pyright/ruff lint-clean assertion).
- AC #14 (v2.8 absorption per spec v1.10 §14.8.3 Q2 simplification + F2-01 enumeration completion): Phase 7d retirement-event prerequisite — after U-RT-60 lands, file batch 8 retirement event record for **H_T-CP-20** STILL-BOUNDED → RETIRE-READY (or RETIRED per operator audit) per `.harness/phase-7d-retirement-events-batch-1.md` shape under v2 ledger §5 CP-row evidence framework. Per spec v1.10 §14.8.3 X-AL-2 retirement-implications subsection: condition A satisfied — **U-CP-13 + U-CP-37 + U-CP-38 + U-CP-39 + U-CP-40 + U-CP-41 + U-CP-46 + U-RT-25 + U-RT-60** all landed (v2.8 amendment per F2-01 absorption: extends the v2.7 enumeration to include U-CP-13, the workflow-binding production site that populates `step.hitl_placements` per spec v1.10 §14.8.2 step 1 — "populated at workflow-binding time per U-CP-13 + U-CP-38"; without U-CP-13 landed, no real workflow's steps carry `hitl_placements` and the composer's step-1 read always returns `[]`, making condition B unverifiable at production execution path; spec v1.10 §14.8.3 X-AL-2 enumeration still omits U-CP-13 — Class 3 spec-level drift filed at change-note "Downstream findings owed" row for separate spec-writer arc absorption; not blocking U-RT-60 implementation since the dependency is already enforced via the §14.8.2 step 1 narrative); condition B satisfied at production execution path (`4-response palette + hitl.* / audit.* namespaces emitted at production execution path per §14.8.5 + §14.8.6`). The H_E `AskUserQuestion` surface remains as bounded delivery transport per the substitution-retirement reading at spec v1.10 §14.8.3 (**via** the `Phase_7_Meta_Architecture_v1.md` MCP-server substitution-mechanism category per Q2 ratification simplification — direct, in-class with the 11 other MCP-server-category bounded-transport substitutions; v2.7 phrasing "analogous to" superseded by v2.8 phrasing "via" mirroring spec v1.10). Anticipated cumulative retirement count 21/49 → 22/49 (44.9%); CP axis 9/22 → 10/22 (45.5%). Updates `harness-cp/CLAUDE.md` §4.1 substitution-table status entries. No cross-axis cascade re-evaluation expected at U-RT-60 landing (§6.3.2 F-CP-01 Stage 3b inversion FULLY DISCHARGED at U-RT-58; C-RT-18 lands inside an already-discharged inversion-seam region).

### L9-quinquies — FastMCP server hosting + workflow tool registration + `HarnessMCPServer` primitive (new at v1.12 / v2.10; Class 1 fork RESOLVED at spec-writer absorption — Q1+Q2+Q3+Q4+Q5 ratified)

> **✅ Class 1 fork RATIFIED at systems-architect mode 3 + spec-writer + this plan absorption.** Operator ratified all 5 systems-architect mode 3 recommendations 2026-05-21 (fork record `.harness/class_1_tension_c_rt_18_mcp_workflow_initiation_topology_underspec.md`; spec landed at HEAD `7f2fee3`; this plan amendment co-publishes). Architecture is fully frozen for U-RT-62 implementation. The architectural commitment per Q1 ratification: Reading (α) CC-initiates topology — H_T is the MCP server; Claude Code is the registered MCP client; workflow execution is invoked by Claude Code calling the `run_workflow` MCP tool on H_T's server; HITL elicitation rides outbound on the active server session via `ctx.elicit(...)` back to Claude Code (which honors `elicitation/create` requests since CC 2.1.76, March 2026).

**U-RT-62 — FastMCP server hosting + workflow tool + `HarnessMCPServer` primitive (Spec_Harness_Runtime_v1.md §14.8.3 v1.12 topology pin + v1.12 RETIRE-READY → RETIRED gate)**

- Scope: implement four coupled production surfaces under the H_T-as-MCP-server topology pin. (a) `HarnessMCPServer` primitive at `harness-runtime/src/harness_runtime/lifecycle/mcp_server.py` (or implementation-discretion equivalent module path) — frozen dataclass wrapping a `mcp.server.fastmcp.FastMCP` instance + lifecycle state (started: bool; tool-registry references). Distinct from existing `MCPHost` primitive at `harness-runtime/lifecycle/mcp_host.py` (which retains H_T-as-MCP-client semantics per U-RT-15; preserved verbatim per Q3 atomicity discipline). `HarnessContext` schema extended with `mcp_server: HarnessMCPServer | None` field analog to existing `mcp_host: MCPHost | None`. (b) FastMCP server lifecycle: `materialize_mcp_server_stage()` at bootstrap stage 2 (AS sub-bootstrap, sibling to existing `materialize_mcp_stage()` per U-RT-15) constructs the FastMCP server instance; registers the `run_workflow` tool with workflow-execution adapter body; binds the server lifecycle (`server.started=True` after registration); operator-supplied `.mcp.json` configures CC as a registered MCP client per the H_T-server endpoint (operator-side configuration; no in-spec contract). (c) `run_workflow` MCP tool handler at the FastMCP server: async `@mcp.tool()` decorated function with signature `async def run_workflow(workflow_id: str, ctx: Context[ServerSession, None]) -> RunResultDict` (or implementation-discretion equivalent — `WorkflowObject` discovery shape is impl-detail per Q2). Tool body invokes the existing `execute_workflow` driver synchronously inside the tool handler's `ctx` (the workflow body runs inside the in-flight tool ctx — this is the topology pin); during workflow execution, when a HITL gate fires at the composer body, the composer calls `await ctx.ask_user_question_surface.ask(...)` which delegates to the v1.12-shape MCP-backed surface; the surface's bound `MCPAskCallback` (replaced at v1.12 from placeholder to `ServerCtxElicitCallback` per (d)) invokes `await ctx.elicit(message=composed_prompt, schema=HITLResponseSchema)` outbound on the active server session; CC renders the dialog; CC returns the response through the MCP response channel; the surface returns `AskUserQuestionResult` to the composer; workflow continues. (d) `ServerCtxElicitCallback` async callable at `harness-runtime/src/harness_runtime/lifecycle/mcp_backed_ask_user_question_surface.py` replaces `_PlaceholderMCPCallback`; binds to the in-flight `ctx` of the workflow-execution tool handler (via contextvar OR direct ctx-passing through the workflow body — implementation discretion); satisfies `MCPAskCallback` Protocol contract; on invocation calls `result = await ctx.elicit(message=prompt, schema=AskUserQuestionResultSchema)`; maps the `ElicitResult.action` field to the `HITLResponse` enum (`accept` + content → operator response; `decline` → `HITLResponse.REJECT`; `cancel` → `AskUserQuestionTimeoutError` or `HITLGateCancelledError` per implementation discretion). (e) `harness-runtime/api.py:run()` Track A operator-facing API symbol preserved as thin wrapper per Q2 ratification — the symbol stays; the internal body invokes the MCP-tool path (constructs an in-process MCP client via `mcp.client.session.ClientSession`, connects to the same in-process FastMCP server materialized at bootstrap stage 2, calls the `run_workflow` tool). For tests (4 callsites at `harness-runtime/tests/test_bootstrap.py` + 3 others importing `from harness_runtime.api import run`), the thin-wrapper reframe is transparent — `api.run()` continues to work but operationally rides the MCP path. Concurrency invariants from existing `_run_lock` preserved.

- Deps: U-RT-15 (existing FastMCP host = H_T-as-MCP-client surface; preserved verbatim per Q3; U-RT-62's H_T-as-server hosting is the orthogonal sibling); U-RT-25 (HITL placement registry — composer consumer; landed); U-RT-42 (`execute_workflow()` surface — invoked from inside the `run_workflow` tool handler body); U-RT-49 (smoke test fixture infrastructure — extended to assert e2e CC → tool → HITL → elicit → response → continuation); U-RT-60 (HITL gate composer + `AskUserQuestionSurface` Protocol + `MCPBackedAskUserQuestionSurface` placeholder — landed; `_PlaceholderMCPCallback` is the symbol replaced by `ServerCtxElicitCallback` per (d)). No new cross-axis deps beyond the existing CXA v2.5 §2.3.7 CP→OD bucket already satisfied at U-RT-60 landing.

- Cross-axis deps (Pattern P1 imports): unchanged from U-RT-60 baseline. `harness_cp.workflow_driver.StepDispatcher` Protocol (composer body unchanged); `harness_cp.hitl_response_palette.HITLResponse` enum (4-response palette per C-CP-16 §16.1; consumed at `ServerCtxElicitCallback` `ElicitResult.action` → `HITLResponse` mapping); no AS spec extension (the H_T-as-server hosting is runtime-spec-internal per `Spec_Harness_Runtime_v1.md` v1.12 §14.8.3 topology pin; AS-AL-2 line 522 discipline statement is upheld — "all H_T tool surface lives behind MCP server boundary" — the `run_workflow` tool IS H_T tool surface, hosted behind the H_T MCP server boundary).

- AC #1 (`HarnessMCPServer` primitive declaration): `harness-runtime/src/harness_runtime/lifecycle/mcp_server.py` (or implementation-discretion equivalent module path) exists; defines `HarnessMCPServer` frozen dataclass with at minimum a `started: bool` lifecycle field + a typed reference to the `mcp.server.fastmcp.FastMCP` instance (specific field shape impl-discretion). Distinct primitive from existing `MCPHost` at `harness-runtime/lifecycle/mcp_host.py` (verified by pyright/ruff lint pass — no symbol collision; `MCPHost` preserved verbatim). `HarnessContext` schema at `harness-runtime/types.py` extended with `mcp_server: HarnessMCPServer | None` field analog to existing `mcp_host: MCPHost | None`. Test asserts `HarnessContext` instances post-bootstrap have non-None `mcp_server` AND non-None `mcp_host` (the two MCP-role primitives coexist).

- AC #2 (FastMCP server lifecycle materialization at bootstrap stage 2): `materialize_mcp_server_stage()` at `harness-runtime/src/harness_runtime/bootstrap/stage_2_as.py` (or equivalent — sibling to existing `materialize_mcp_stage()` per U-RT-15) constructs the FastMCP server instance per `mcp.server.fastmcp.FastMCP(name="harness-runtime", ...)`; registers the `run_workflow` tool per AC #3; transitions `HarnessMCPServer.started: False → True` after registration. Pre-condition: stage 1 IS materialized + stage 2 AS materialization order preserved per existing bootstrap discipline. Post-condition: `ctx.mcp_server.started == True` AND `ctx.mcp_server` has at least one registered tool. Failure semantics: on `mcp.server.fastmcp.FastMCP` constructor failure OR tool registration failure, stage 2 raises typed `MCPServerStartupError` → bootstrap rollback per existing 9-stage discipline.

- AC #3 (`run_workflow` MCP tool handler registration + body): the FastMCP server at `ctx.mcp_server` has the `run_workflow` tool registered with signature `async def run_workflow(workflow_id: str, ctx: Context[ServerSession, None]) -> dict` (or implementation-discretion `RunResult`-isomorphic return shape). Tool body resolves `workflow_id` to a `WorkflowObject` (resolution mechanism — file-based registry / in-memory registry / etc. — impl-discretion at v1.12 MVP; future arc may formalize a `WorkflowRegistry` primitive); invokes the existing `execute_workflow` driver synchronously inside the tool handler's `ctx`; the workflow body's HITL gate composer at the stage 5 wrap chain reaches `await ctx.ask_user_question_surface.ask(...)` which routes through the v1.12 `ServerCtxElicitCallback` (AC #4) and rides the active `ctx` for the elicitation. Test verifies the tool is discoverable via `await session.list_tools()` from an in-process MCP client + callable + returns a structurally-valid `RunResult`-isomorphic dict.

- AC #4 (`ServerCtxElicitCallback` replaces `_PlaceholderMCPCallback`): `harness-runtime/src/harness_runtime/lifecycle/mcp_backed_ask_user_question_surface.py` carries a new `ServerCtxElicitCallback` async callable class satisfying the `MCPAskCallback` Protocol contract (`(prompt: str, options: Sequence[HITLResponse], timeout: float | None) -> AskUserQuestionResult`). Implementation: receives the in-flight workflow-tool-handler `ctx: Context[ServerSession, None]` (binding mechanism — contextvar OR direct ctx-passing through the workflow execution layer — impl-discretion); on `__call__`, invokes `result = await self._ctx.elicit(message=prompt, schema=AskUserQuestionResultElicitationSchema)` (where `AskUserQuestionResultElicitationSchema` is a Pydantic v2 model mirroring the 4-response palette + optional content fields); maps `result.action == "accept"` + content → `AskUserQuestionResult` via the 4-response palette discriminator; maps `result.action == "decline"` → `AskUserQuestionResult(response=HITLResponse.REJECT, ...)`; maps `result.action == "cancel"` → raise `AskUserQuestionTimeoutError` (or `HITLGateCancelledError` per impl-discretion). Bootstrap stage 5 wiring updated at `materialize_mcp_backed_ask_user_question_surface_stage(...)` to bind `ServerCtxElicitCallback` instead of the v1.11 `_PlaceholderMCPCallback` default; the placeholder may remain as a documented fallback for test substrates that explicitly inject it. Test asserts that under normal workflow execution with a HITL placement, the surface's `ask()` calls the elicitation primitive on the in-flight `ctx`.

- AC #5 (`api.run()` thin-wrapper reframe per Q2 ratification): `harness-runtime/src/harness_runtime/api.py:run(workflow, *, config=None) -> RunResult` symbol preserved. Body refactored: instead of directly invoking `run_bootstrap(...)` + `execute_workflow(...)` inline, the body materializes an in-process MCP client via `mcp.client.session.ClientSession` (or equivalent in-process transport — `stdio_client` variant against the same Python process is one impl-discretion option), connects to the in-process FastMCP server materialized at bootstrap stage 2, calls the `run_workflow` tool with the workflow's `workflow_id` (or registers the `WorkflowObject` in the in-memory registry first if the workflow is supplied directly per the current `api.run(workflow)` signature), and returns the tool's response unmarshalled to `RunResult`. The `_run_lock: asyncio.Lock` concurrency invariant preserved. The 4 existing test files importing `from harness_runtime.api import run` continue to work — the thin-wrapper reframe is transparent at the Python symbol level. Test asserts: (i) `await run(workflow)` still returns `RunResult` shape unchanged from v1.11 baseline; (ii) the test substrate's tracing/audit assertions still pass (the wrap chain at stage 5 is unaffected; only the entry layer changed); (iii) `ConcurrentRunNotSupported` is still raised on concurrent invocation per C-RT-08 §16 #4.

- AC #6 (e2e CC → `run_workflow` → HITL fire → `ctx.elicit` → response → continuation test — load-bearing for criterion B verification per spec v1.12 §14.8.3 v1.12 RETIRE-READY → RETIRED gate): integration test at `harness-runtime/tests/integration/test_run_workflow_elicitation_e2e.py` exercises the full topology. Fixture: in-process `ClientSession` paired with the in-process FastMCP server at `ctx.mcp_server`; an `elicitation_callback` set on the client session to deliver a canned response. Workflow: a mock `WorkflowObject` with one step carrying a single PRE_ACTION HITL placement; the workflow's inner LLM dispatcher is a fake async client returning a fixed string. Test asserts: (i) client calls `run_workflow` tool successfully; (ii) the HITL gate composer at stage 5 fires once; (iii) `ctx.elicit` is invoked exactly once with the composed prompt; (iv) the `elicitation_callback` receives the request and returns the canned response; (v) the composer's audit-write 4-substep sequence completes per spec §14.8.6 + the canonical 4-span hierarchy per §14.8.5 (4 spans emitted per matching placement: `hitl.gate.evaluated` + `hitl.invocation.opened` + `hitl.invocation.responded` — the timeout branch unexercised in this test variant); (vi) the workflow continues to step 5 of the composer body (delegate to inner dispatcher); (vii) the workflow completes; (viii) the tool returns the `RunResult`. Asserts the H_E `AskUserQuestion` surface is NOT invoked directly (the production substitution site at the composer body is now reached only via the MCP envelope per the v1.12 topology pin; the v1.11 `_PlaceholderMCPCallback` is replaced; criterion B verification per X-AL-2).

- AC #7 (`MCPHost` schema reconciliation verified — `MCPHost` preserved verbatim per Q4): test asserts `MCPHost` dataclass at `harness-runtime/lifecycle/mcp_host.py` retains v2.9 shape unchanged (no `server: FastMCP | None` field added per Q4 (a) rejected); `MCPStage` composition at `materialize_mcp_stage(...)` continues to produce `MCPStage(host=MCPHost(started=False), clients=dict[ClientName, MCPClient])` per existing L3 U-RT-15 contract; the new `HarnessMCPServer` primitive is a separate sibling module. pyright/ruff lint-clean assertion: no symbol collision between `MCPHost` (H_T-as-client) and `HarnessMCPServer` (H_T-as-server). `HarnessContext` schema verifies both `ctx.mcp_host: MCPHost | None` (existing) AND `ctx.mcp_server: HarnessMCPServer | None` (new) are present and bound post-bootstrap.

- AC #8 (Q2 carrier-preservation verified): existing test substrate calling `from harness_runtime.api import run` at `harness-runtime/tests/test_bootstrap.py:750` + 3 other test files continues to pass unchanged. The thin-wrapper reframe is transparent at the Python symbol level; no test refactor required at the existing call sites. Tests calling `execute_workflow` directly (5 test files per the pre-amendment baseline) continue to work unchanged (the lower-level surface is preserved). New tests added for the e2e topology per AC #6.

- AC #9 (Class 3 carry-forward closure — placeholder `_PlaceholderMCPCallback` retirement reading): at U-RT-62 landing, the `_PlaceholderMCPCallback` symbol at `harness-runtime/lifecycle/mcp_backed_ask_user_question_surface.py` is either (a) retained as a documented fallback for test substrates explicitly injecting it (with a docstring note that production binding uses `ServerCtxElicitCallback` per v1.12), or (b) removed entirely if no production fallback is needed (impl-discretion at U-RT-62 implementation arc). Either way, the v1.11 `MCPSurfaceCallbackNotBoundError` typed error continues to fire only when neither callback is bound (defensive default behavior preserved). Resolves the v1.11 Class 3 carry-forward filed at `.harness/class_1_tension_u_rt_60_wrap_asymmetry_sync_async_mismatch.md` §9.4 (the §14.8.3 line 1715 impl-discretion broad-reading carry-forward).

- AC #J (Phase 7d batch 9 retirement event prerequisite per Q5 ratification): after U-RT-62 lands + AC #6 e2e test passes, file batch 9 retirement event record for **H_T-CP-20** RETIRE-READY → **RETIRED** per `.harness/phase-7d-retirement-events-batch-8.md` shape + spec v1.12 §14.8.3 v1.12 RETIRE-READY → RETIRED gate paragraph. Criterion verification: (a) `HarnessMCPServer` primitive materialized + `run_workflow` MCP tool registered + Claude Code MCP-client connection verified at runtime (per AC #1 + AC #2 + AC #3) AND (b) end-to-end integration test per AC #6 demonstrates the full path Claude Code → `run_workflow` → workflow body → HITL gate fire → `ctx.elicit` → response → continuation → 4-substep audit-write per §14.8.6 + canonical 4-span hierarchy per §14.8.5 → workflow result returned. **Q5 disjointness pin (load-bearing at AC body language per workspace `CLAUDE.md` §4.3 no-silent-absorption discipline):** H_T-CP-18 (MCP integration + per-server trust + `mcp.*` consumption per Meta-Arch §5 line 124) does NOT advance jointly with H_T-CP-20 at this retirement event. CP-18's substitution site is the H_T-as-MCP-client surface (the runtime consumes other MCP servers — e.g., filesystem, GitHub, sandbox MCP servers — gated by per-server-trust framework + `mcp.*` namespace emission at the client-side per U-RT-15 lifecycle). The U-RT-62 H_T-as-MCP-server workflow-execution hosting is orthogonal; CP-18 retirement remains a separate arc gated on the per-server-trust framework landing + `mcp.*` namespace emission at the H_T-as-client surface. Anticipated cumulative retirement count 21/49 RETIRED + 1/49 RETIRE-READY → 22/49 RETIRED + 0/49 RETIRE-READY (44.9%); CP axis 9/22 RETIRED + 1/22 RETIRE-READY → 10/22 RETIRED + 0/22 RETIRE-READY (45.5%). Updates `harness-cp/CLAUDE.md` §4.1 substitution-table status entries (H_T-CP-20 row: RETIRE-READY → RETIRED; H_T-CP-18 row: STILL-BOUNDED preserved). Batch 9 record explicitly amends batch 8 §3 carry-forward language ("Coupled with H_T-CP-18 retirement … both substitutions advance to RETIRED at that arc landing") per the Q5 disjointness ratification — forward-only ledger discipline at workspace `CLAUDE.md` §4.3 (new batch record, NOT retroactive edit to batch 8).

---

## 3. Topological dependency graph

```
L0  U-RT-00 (spec gate) → U-RT-01 → U-RT-02 → U-RT-03

L1  U-RT-04 ─┬─ U-RT-05 (path bindings)
             ├─ U-RT-06 (secrets)
             ├─ U-RT-07 (otel cfg)
             └─ U-RT-08 (collector cfg)

L2  U-RT-05 → U-RT-10 → U-RT-09 (index + cache)
                      → U-RT-11 (worktree + shadow-Git)
                      → U-RT-12 (ledger)

L3  U-RT-10 → U-RT-13 → U-RT-14 → U-RT-15 (+U-RT-06) → U-RT-16

L4  U-RT-06 → U-RT-17, U-RT-18, U-RT-19 → U-RT-20

L5  U-RT-20 + U-RT-10 → U-RT-21 → U-RT-22 → U-RT-23
                                  → U-RT-24
                                  → U-RT-25 → U-RT-26

L6  U-RT-07 → U-RT-27 → U-RT-28
                      → U-RT-31
    U-RT-08 + U-RT-28 → U-RT-29 → U-RT-30
    U-RT-12 + U-RT-27 → U-RT-32

L7  L2..L6 init → U-RT-33 (terminal exporter manifest import)
                → U-RT-34, 35, 36, 37, 38 (24 phase-2-runtime edges)

L8  U-RT-21 → U-RT-39
    U-RT-22 + U-RT-39 → U-RT-40
    U-RT-28 + U-RT-32 + U-RT-40 → U-RT-41

L9  L0..L8 → U-RT-42 → U-RT-43

L10 U-RT-43 → U-RT-44 → U-RT-45 → U-RT-46
    U-RT-12 + U-RT-30 → U-RT-47
    U-RT-44 → U-RT-48

L11 U-RT-43 + U-RT-46 → U-RT-49
    U-RT-43 → U-RT-50
    U-RT-33 → U-RT-51 (Pattern P1 completeness)

L9-bis (v2.3 addition; wraps U-RT-52 at stage 5):
    U-RT-24 + U-RT-25 + U-RT-27 + U-RT-52 → U-RT-58
    (stage 5 wiring rebinds ctx.llm_dispatcher from bare RuntimeLLMDispatcher to RetryBreakerFallbackDispatcher; driver call site unchanged)

L9-ter (v2.5 addition; sub-agent dispatch composer + driver routing-layer refactor at stage 5):
    U-RT-26 + U-RT-40 + U-RT-27 + U-RT-32 + U-RT-42 + U-RT-58 → U-RT-59
    (stage 5 wiring constructs ctx.step_dispatchers: StepKindDispatcherRegistry with 2 bindings — INFERENCE_STEP → ctx.llm_dispatcher (U-RT-58 wrapper preserved) + SUB_AGENT_DISPATCH → ctx.sub_agent_dispatcher (new); driver refactored to dispatch via step_dispatchers.lookup(step.kind))

L9-quater (v2.7 addition; HITL gate composer + AskUserQuestionSurface H_E delivery Protocol; bootstrap stage 5 wrap-asymmetric per step_kind):
    U-RT-12 + U-RT-25 + U-RT-26 + U-RT-27 + U-RT-32 + U-RT-42 + U-RT-58 + U-RT-59 → U-RT-60
    (stage 5 wiring per spec §14.8.1 wrap-asymmetry table:
       ctx.llm_dispatcher       = c_rt_16_compose(hitl_gate_composer(c_rt_15, applicable_placements={PRE_ACTION}))         # INFERENCE_STEP: retry-outer-of-HITL per Q2
       ctx.sub_agent_dispatcher = hitl_gate_composer(c_rt_17, applicable_placements={SUB_AGENT_BOUNDARY})                  # SUB_AGENT_DISPATCH: HITL-direct, no retry layer
     ctx.ask_user_question_surface bound to H_E AskUserQuestion-wrapping impl per Q1; ctx.step_dispatchers registry unchanged from L9-ter; TOOL_STEP / DECLARATIVE_STEP / HITL_STEP still unbound per spec §14.8.1)

L9-quinquies (v2.10 addition; H_T-as-MCP-server topology pin per spec v1.12 §14.8.3 v1.12 workflow-initiation topology pin; FastMCP server hosting + run_workflow tool + HarnessMCPServer primitive + api.run() thin-wrapper reframe + ServerCtxElicitCallback):
    U-RT-15 + U-RT-25 + U-RT-42 + U-RT-49 + U-RT-60 → U-RT-62
    (bootstrap stage 2 AS sub-bootstrap wiring extension:
       ctx.mcp_server = HarnessMCPServer(started=True, server=mcp.server.fastmcp.FastMCP("harness-runtime"))   # H_T-as-server hosting, sibling to ctx.mcp_host (H_T-as-client)
       ctx.mcp_server registers the run_workflow MCP tool with workflow-execution adapter body
     stage 5 LOOP_INIT wiring extension:
       ctx.ask_user_question_surface MCPAskCallback rebinds from _PlaceholderMCPCallback to ServerCtxElicitCallback
         (binds to in-flight workflow-tool-handler ctx via contextvar or direct ctx-passing per impl-discretion)
     api.py:run() refactored to thin wrapper invoking the run_workflow MCP tool through an in-process MCP ClientSession;
     wrap chain at stage 5 unchanged from L9-quater; Claude Code (the operator's MCP client) is registered via operator-supplied .mcp.json;
     workflow execution path: CC -> run_workflow tool -> execute_workflow inside tool ctx -> HITL composer -> ctx.elicit -> CC dialog -> response -> continuation)
```

---

## 4. 24 phase-2-runtime CXA edges — unit correspondence

| Bucket | Count | Unit | Edge enumeration (per CXA v2.3 §2.3) |
|---|---|---|---|
| AS → IS | 1 | U-RT-34 | U-AS-27 → U-IS-11 |
| CP → IS | 17 | U-RT-35 | U-CP-12, 14, 27, 30, 34, 37, 49, 50, 52 → U-IS-07/08/09/11 (split-allowed if signatures diverge) |
| CP → AS | 0 | — | None in scope. |
| OD → IS | 2 | U-RT-36 | U-OD-30 → U-IS-11; U-OD-34 → U-IS-17 |
| OD → AS | 1 | U-RT-37 | U-OD-34 → U-AS-33 |
| OD → CP | 3 | U-RT-38 | U-OD-09 → U-CP-54; U-OD-34 → U-CP-54; U-OD-34 → U-CP-55 |
| **Total** | **24** | | Plus U-RT-33 (terminal exporter manifest import) + U-RT-51 (Pattern P1 completeness verification). |

---

## 5. Spec recording strategy

**Authoring order (hard gate):**

1. **U-RT-00 first** — author `Spec_Harness_Runtime_v1.md` at Session 4 via `spec-writer` skill.
2. Then `harness-adversarial-reviewer` second pass on the spec.
3. Then U-RT-01 onward.

**`Spec_Harness_Runtime_v1.md`** specifies what no axis owns alone: bootstrap stage order and 9-stage enum invariants, `HarnessContext` and `RuntimeConfig` schemas, `run()` Python-API contract, shutdown order, admin-stub semantics, the 24 phase-2-runtime CXA edge wiring obligations, the five F-P2-N fork resolutions.

**Per-axis amendments** are surgical, driven by unit-landing back-flow:
- **AS** — tool-contract registration *site* (U-RT-14); MCP host startup lifecycle (U-RT-15); skills-load ledger event shape (U-RT-34) if gaps surface.
- **CP** — routing-manifest construction-time invariants R-2/W-2 consumer side (U-RT-21); `WorkloadObject` ingress shape (U-RT-42); optional drain primitive (U-RT-44 follow-up).
- **OD** — collector-daemon process-supervision contract (U-RT-29) — start/health/stop semantics — likely required.

Spec is canonical at `design-substrate/` (back-flow deprecated 2026-05-15; in-CLI fix discipline applies per `[[spec-tension-record-pattern]]`).

---

## 6. 7d substitution-retirement preview

Retirement criterion B = "real surface stands up, substitute carry-forward becomes unreachable." Track A is mostly criterion-B retirement.

| Substitution category | Retired when | Driving units |
|---|---|---|
| `H_T-CP-1` (anthropic.* namespace emission convention substitute) | TracerProvider registered + first real provider call instrumented | U-RT-27, U-RT-28, U-RT-31 |
| Provider-SDK shell-out substitutes | Real async SDK clients constructed | U-RT-17, U-RT-18, U-RT-19, U-RT-20 |
| Collector-daemon manual-supervision substitute | Daemon supervisor runs | U-RT-29, U-RT-30 |
| MCP-server convention substitute (host startup) | MCP host real-started | U-RT-15 |
| Ledger-append authoring-only substitutes for CP call sites | CP→IS edges wired | U-RT-35 (and U-RT-34, U-RT-36) |
| Audit-ledger writer authoring-only substitute | Real writer instantiated | U-RT-32 |
| Skill-load filesystem-read convention substitute | Real load runs | U-RT-13 |
| Routing-manifest authoring-only substitute | R-2/W-2 manifest constructed | U-RT-21 |
| Index reattach authoring-only substitute | Real reattach runs | U-RT-09 |
| Shadow-Git supervisor authoring-only substitute | Real supervisor binds | U-RT-11 |

Bounded residuals expected to carry forward past Track A: substitutes whose real surface is operator-facing (CLI ingress, markdown workflow authoring, MCP-triggered workflow, TUI). Those retire under Track B.

Per X-AL-2, file a retirement event against `Phase_7_Meta_Architecture_v1.md §5` as each unit above lands. Use the `phase-7-substitution-retirement` skill.

**v2.3 addendum (2026-05-20).** U-RT-58 lands the retry/breaker/fallback composer (per C-RT-16). At its landing, retirement-event prerequisites are satisfied for three CP-axis substitutions previously bounded by the "no production retry/fallback orchestration call site" gap surfaced at `.harness/phase-7d-retirement-ledger-v2.md` §5:

| Substitution | Retired when | Driving unit |
|---|---|---|
| `H_T-CP-3` (per-layer time-budget + `retry.*` 6-attribute namespace + dual-emission) | Wrapper emits `retry.*` 6-attribute span per attempt at production execution path | U-RT-58 |
| `H_T-CP-4` (fallback chain + cross-family fallback) | Wrapper owns the candidate-iteration loop + emits `fallback.exhausted` on chain exhaustion | U-RT-58 |
| `H_T-CP-5` PARTIAL → RETIRED (routing attribute namespaces composition) | `routing.*` inheritance through the inner `gen_ai.*` span surfaces at the wrapper's per-attempt span hierarchy | U-RT-58 |

Cross-axis cascade re-evaluation at U-RT-58 landing: §6.3.2 (F-CP-01 Stage 3b inversion) candidate for closure once H_T-CP-3 RETIRED + production `harness.breaker.*` emission verified end-to-end. Re-evaluate at the retirement-event filing step per the `phase-7-substitution-retirement` skill §4 cross-axis dependency tracking.

**v2.5 addendum (2026-05-20).** U-RT-59 lands the sub-agent dispatch composer + `StepKindDispatcherRegistry` driver routing-layer refactor + `ChildWorkflowRunner` in-process recursive invocation primitive (per C-RT-17). At its landing, retirement-event prerequisites are satisfied for three CP-axis substitutions previously bounded on "no production sub-agent composer call site" per `Phase_7_Meta_Architecture_v1.md` §5.4 + `harness-cp/CLAUDE.md` §4.1 STILL-BOUNDED enumeration:

| Substitution | Retired when | Driving unit |
|---|---|---|
| `H_T-CP-10` (TopologyPattern 6-class enum + admissibility predicate) | `ctx.topology_dispatcher.dispatch(...)` + `is_admissible(...)` invoked at production execution path per spec §14.7.2 step 4 | U-RT-59 |
| `H_T-CP-13` (HandoffContext + SubAgentBrief + StateSummary + LedgerEntryRef typed schemas at production dispatch) | `HandoffContext` composed per C-CP-13 §13.1 + `ctx.handoff_registry.dispatch(...)` invoked at production execution path per spec §14.7.2 steps 2-3 | U-RT-59 |
| `H_T-CP-14` PARTIAL or RETIRED (multi-agent span hierarchy + `topology.*` + `subagent.*` namespaces) | `subagent.span` emitted with full `subagent.*` 7-attribute namespace + narrow-subset `topology.*` 2-attribute slice (`pattern` + `workload_class`) at production span hierarchy per spec §14.7.2 step 5. Operator ratifies RETIRED vs PARTIAL at retirement audit per X-AL-2 strict reading: full `topology.*` 10-attribute namespace + fan-out envelope deferred to parent-topology-expansion arc (post-v1.6). | U-RT-59 (single-sub-agent slice) |

No cross-axis cascade re-evaluation expected at U-RT-59 landing. §6.3.2 (F-CP-01 Stage 3b inversion) was FULLY DISCHARGED at U-RT-58 landing. C-RT-17 lands inside an already-discharged inversion-seam region.

**v2.7 addendum (2026-05-20).** U-RT-60 lands the HITL gate composer + `AskUserQuestionSurface` H_E delivery Protocol + bootstrap stage 5 wrap-asymmetric wrap-chain construction (per C-RT-18). At its landing, retirement-event prerequisites are satisfied for one CP-axis substitution previously bounded on "no production HITL gate composer call site" per `Phase_7_Meta_Architecture_v1.md` §5 line 23 + `harness-cp/CLAUDE.md` §4.1 STILL-BOUNDED enumeration:

| Substitution | Retired when | Driving unit |
|---|---|---|
| `H_T-CP-20` (HITL primitive + 4-response palette + `hitl.*` / `audit.*` namespaces) | 4-response palette + `hitl.*` / `audit.*` namespaces emitted at production execution path per spec §14.8.5 + §14.8.6 (condition A: U-CP-37 + U-CP-38 + U-CP-39 + U-CP-40 + U-CP-41 + U-CP-46 + U-RT-25 + U-RT-60 landed; condition B: namespace emission at production execution path vs `CLAUDE.md`-substituted). The H_E `AskUserQuestion` surface remains as the bounded delivery transport per spec §14.8.3 substitution-retirement reading (analog of MCP-server bounded-transport mechanism category). | U-RT-60 |

No cross-axis cascade re-evaluation expected at U-RT-60 landing. §6.3.2 (F-CP-01 Stage 3b inversion) FULLY DISCHARGED at U-RT-58 landing; C-RT-18 lands inside an already-discharged inversion-seam region. CXA v2.5 §2.3.7 CP→OD bucket cardinality grows from 1 → 2 typed seams (adds U-CP-46 → U-OD-00 HITL audit-write seam alongside existing U-CP-28 → U-OD-00 sub-agent dispatch seam — shared `cp_audit_to_od_audit` converter per Q3 ratification); U-RT-51 Pattern P1 completeness assertion seam-count extends from 22 → 23 at U-RT-60 landing.

**v2.10 addendum (2026-05-21).** U-RT-62 lands the FastMCP server hosting + `run_workflow` MCP tool registration + `HarnessMCPServer` primitive + `api.run()` thin-wrapper reframe + `ServerCtxElicitCallback` (replaces `_PlaceholderMCPCallback`) per spec v1.12 §14.8.3 v1.12 workflow-initiation topology pin (Reading α CC-initiates). At its landing, retirement-event prerequisites are satisfied for **one** CP-axis substitution previously RETIRE-READY at batch 8 — H_T-CP-20 transitions RETIRE-READY → RETIRED per spec v1.12 §14.8.3 v1.12 RETIRE-READY → RETIRED gate. Adds a NEW substitution-table row for the H_T-as-MCP-server hosting site (distinct from the existing U-RT-15 H_T-as-MCP-client host-startup row at §6.5 line 635 — the two MCP roles are orthogonal per Q3 atomicity discipline + Q5 disjointness):

| Substitution | Retired when | Driving unit |
|---|---|---|
| `H_T-CP-20` RETIRE-READY → RETIRED (HITL primitive + 4-response palette + `hitl.*` / `audit.*` namespaces) | (a) `HarnessMCPServer` primitive materialized + `run_workflow` MCP tool registered + Claude Code MCP-client connection verified at runtime AND (b) end-to-end integration test exercises the full path Claude Code → `run_workflow` → workflow body → HITL gate fire → `ctx.elicit` → response → continuation → 4-substep audit-write per §14.8.6 + canonical 4-span hierarchy per §14.8.5 (criterion B verification per X-AL-2 — the H_E `AskUserQuestion` surface is reached only via the MCP envelope; the spec-substituted direct-invocation H_E surface is no longer invoked at the substitution site) | U-RT-62 |
| MCP-server hosting (workflow tool + elicitation) — H_T-as-MCP-server surface | `HarnessMCPServer` real-started at bootstrap stage 2 + `run_workflow` tool callable from registered MCP client (Claude Code) + `ServerCtxElicitCallback` bound at stage 5 LOOP_INIT (replaces `_PlaceholderMCPCallback`) | U-RT-62 |

**v2.10 H_T-CP-18 retirement disjointness pin (Q5 ratification).** Per spec v1.12 §14.8.3 v1.12 H_T-CP-18 retirement disjointness pin paragraph: H_T-CP-18 (MCP integration + per-server trust + `mcp.*` consumption per `Phase_7_Meta_Architecture_v1.md` §5 line 124) does NOT advance jointly with H_T-CP-20 at the U-RT-62 retirement event. CP-18's substitution site is the H_T-as-MCP-client surface (the runtime consumes other MCP servers — e.g., filesystem, GitHub, sandbox MCP servers — gated by per-server-trust framework + `mcp.*` namespace emission at the client-side per U-RT-15 lifecycle). U-RT-62's H_T-as-MCP-server workflow-execution hosting is orthogonal; CP-18 retirement remains a separate arc gated on the per-server-trust framework landing + `mcp.*` namespace emission at the H_T-as-client surface. The batch 8 §3 carry-forward language ("Coupled with H_T-CP-18 retirement … both substitutions advance to RETIRED at that arc landing") is INACCURATE under (α) and is amended at the batch 9 retirement-event record per forward-only ledger discipline at workspace `CLAUDE.md` §4.3 (new batch record, NOT retroactive edit to batch 8).

Anticipated cumulative retirement count at U-RT-62 landing: 21/49 RETIRED + 1/49 RETIRE-READY → 22/49 RETIRED + 0/49 RETIRE-READY (44.9% RETIRED). CP axis: 9/22 RETIRED + 1/22 RETIRE-READY → 10/22 RETIRED + 0/22 RETIRE-READY (45.5% RETIRED). No cross-axis cascade re-evaluation expected at U-RT-62 landing — §6.3.2 (F-CP-01 Stage 3b inversion) FULLY DISCHARGED at U-RT-58 landing; the v1.12 topology pin is runtime-spec-internal per Q5 disjointness (no CXA edges added; no per-axis spec amendments required).

---

## 7. Verification strategy

**Three tiers:**

1. **Per-unit unit tests** (`tests/unit/`) — verify the *wiring* shape (async provider client constructed with right kwargs, registry populated, BSP attached). Library has its own unit tests.

2. **Per-stage integration tests** (`tests/integration/test_bootstrap_stages.py` — U-RT-50) — bring up bootstrap through stage N, assert post-conditions, tear down. One test per stage 0–7 (9 substage files incl. 3a + 3b). Failure injection asserts ordered rollback.

3. **End-to-end smoke** (`tests/integration/test_run_smoke.py` — U-RT-49) — minimal no-op workflow:
   - `WorkflowObject` with one step calling a fake async provider returning a fixed string.
   - Full bootstrap → `await run(workflow)` → assert: state ledger has bootstrap + workflow entries; collector sqlite has spans for every stage and the workflow step; cost attribution chain produced an entry; clean shutdown leaves no resources open.

**Pattern P1 verification** (`tests/integration/test_cxa_pattern_p1.py` — U-RT-51) — assert identity-equality across all 22 Pattern P1 typed CXA seams.

Fixtures (`conftest.py`):
- Tmp `.harness/` per test.
- **Fake async provider clients** — subclass `anthropic.AsyncAnthropic` / `openai.AsyncOpenAI` / `ollama.AsyncClient`, override the chat-completion / generate methods to return deterministic `AsyncIterator[Response]`. Bounded fixture complexity: each fake is ~30 LOC, returns a single fixed string, no network. Avoids hitting real APIs.
- In-memory OTLP collector sink for tests that don't need the real daemon; real daemon for U-RT-29/30 + smoke.
- Keyring backend stubbed to in-memory.

CI: `uv run pytest harness-runtime/tests` runs both tiers; integration tier gated by `--runtime-integration` marker so library-only CI stays cheap.

---

## 8. Known risks / open Class 1 surfaces

Priority order (highest probability of fork first):

1. **U-RT-21 (routing manifest construction)** — CP v2.10 R-2/W-2 schemas just landed; runtime is first real consumer. Expect ambiguities in residence + write-time invariants.
2. **U-RT-29 (collector daemon supervision)** — `local_first_otlp_collector` is explicitly library-only. OD spec does not specify supervision semantics. Likely needs an OD amendment.
3. **U-RT-42 (`run()` signature → `WorkflowObject` shape)** — F-P2-2 deferred ingress to Track B but Track A still types the in-process object. Almost certainly surfaces CP gap on workflow-input contract.
4. **U-RT-44 (runtime-owned drain vs eventual CP drain primitive)** — Track A owns drain via flag-polling. If CP later surfaces a native drain primitive, refactor required. Track as Class-1 surface at landing.
5. **U-RT-14/15 (tool-contract registration + MCP host startup)** — AS contracts specify *what* a tool contract is but may not specify the registration *site* or host startup lifecycle.
6. **U-RT-12 (state-ledger reattach)** — reattach semantics across crashed prior run (idempotency, partial-write recovery) may surface IS gap.
7. **U-RT-40 (topology dispatcher)** — Tension 002 filed; re-verify resolution before landing. Unresolved → blocks.
8. **U-RT-35 (17 CP→IS edges)** — risk that the 9 CP source units disagree on ledger-writer signature; split per-source-unit if it surfaces.

Standing discipline: any of the above surfacing a *spec* gap triggers back-flow per `Project_Workflow_v1_8.md` §2.7.6 (`phase-7-back-flow-routing`). No silent absorption (X-AL-3). File as `Phase_7_Class_1_Tension_NNN.md`, route to `systems-architect` for resolution recommendation, then `spec-writer` applies the fix before the unit re-opens.

---

## 9. Spec-to-plan traceability

Canonical at `design-substrate/Spec_Harness_Runtime_v1.md` v1.12 §15 (Spec-to-plan traceability) — coverage matrix mapping every U-RT-NN unit to ≥1 C-RT-NN contract, including per-bucket C-RT-12 §12.1–§12.6 rows, the C-RT-14 cross-cutting row, the v1.2-introduced U-RT-52 row (C-RT-15), the v1.4-introduced U-RT-58 row (C-RT-16), the v1.6-introduced U-RT-59 row (C-RT-17), and the v1.9-introduced U-RT-60 row (C-RT-18; v1.10/v1.11/v1.12 refinements are narrative-only within C-RT-18 §14.8 — §15 row preserved verbatim at the spec layer). U-RT-62 (v2.10) traces to C-RT-04 `mcp_host` / `mcp_clients` extension (HarnessContext schema with new `mcp_server` field) + C-RT-08 `run()` continuity (thin-wrapper reframe) + C-RT-18 §14.8.3 v1.12 workflow-initiation topology pin + v1.12 RETIRE-READY → RETIRED gate paragraph (no new C-RT-NN contract; the topology pin is a v1.12 narrative refinement within existing C-RT-18 §14.8.3); §15 U-RT-62 row addition is owed at the spec next-revision pass (cross-file back-reference; spec-writer SKILL.md §5 procedure flags this for downstream absorption).

This plan does not duplicate the matrix. Spec §15 is the single source of truth; revisions to either the unit set (here) or the contract set (spec) require lockstep updates to spec §15.

---

## Critical files

**To create (Track A execution):**
- `/Users/robertrhu/Projects/arhugula-v2/design-substrate/Spec_Harness_Runtime_v1.md` (U-RT-00, hard gate; Session 4)
- `/Users/robertrhu/Projects/arhugula-v2/harness-runtime/pyproject.toml`
- `/Users/robertrhu/Projects/arhugula-v2/harness-runtime/src/harness_runtime/**`
- `/Users/robertrhu/Projects/arhugula-v2/harness-runtime/tests/**`

**To modify:**
- `/Users/robertrhu/Projects/arhugula-v2/pyproject.toml` — add `harness-runtime` to workspace members, pyright, pytest paths.
- Per-axis spec files in `design-substrate/` — surgical amendments as units surface gaps.

**Reference inputs (read-only):**
- `/Users/robertrhu/Projects/arhugula-v2/.harness/phase-2-session-1-framing.md`
- `/Users/robertrhu/Projects/arhugula-v2/.harness/phase-2-session-2-track-a-strawman.md`
- `/Users/robertrhu/Projects/arhugula-v2/.harness/phase_2_fork_F-P2-1_runtime_package_placement.md`
- `/Users/robertrhu/Projects/arhugula-v2/.harness/phase_2_fork_F-P2-2_workflow_ingress.md`
- `/Users/robertrhu/Projects/arhugula-v2/.harness/phase_2_forks_F-P2-3_4_5_runtime_lifecycle_ownership.md`
- `/Users/robertrhu/Projects/arhugula-v2/.harness/Adversarial_Review_phase_2_session_3_track_a_plan.md`
- `/Users/robertrhu/Projects/arhugula-v2/design-substrate/Cross_Axis_Composition_Document_v2_3.md`
- `/Users/robertrhu/Projects/arhugula-v2/design-substrate/Implementation_Plan_Control_Plane_v2_10.md`
- `/Users/robertrhu/Projects/arhugula-v2/design-substrate/Implementation_Plan_Operational_Discipline_v2_11.md`
- `/Users/robertrhu/Projects/arhugula-v2/design-substrate/Phase_7_Meta_Architecture_v1.md` (substitution table §5)

---

## Execution recommendations (post-approval)

1. **Session 4** — Author `Spec_Harness_Runtime_v1.md` first (U-RT-00, hard gate). Use `spec-writer` skill.
2. Red-team the spec (`harness-adversarial-reviewer`).
3. Land L0 cluster (U-RT-01..U-RT-03); verify tooling green.
4. Land L1 config cluster (U-RT-04..U-RT-08).
5. Land L2 IS bootstrap; smoke ledger round-trip + index reattach + shadow-Git round-trip.
6. Land L3 + L4 in parallel (AS bootstrap and async provider SDK lifecycle have no inter-cluster dep).
7. Land L5 CP routing in single cluster (U-RT-21 is the risk gate).
8. Land L6 OD in single cluster (U-RT-29 is the risk gate).
9. Land L7 CXA wiring after L2–L6 stable.
10. Land L8–L9 (loop + ingress) — U-RT-42 closes F-P2-2's deferred-to-Session-3 detail.
11. Land L10–L11 (shutdown + verification) — U-RT-49 smoke is the Track A close gate.

Every unit landing emits a substitution-retirement check via `phase-7-substitution-retirement`. Every Class 1 fork halts and routes via `phase-7-back-flow-routing`.

---

## Revision log

- **v1 (2026-05-19)** — initial Session 3 atomic-decomposition; approved via plan mode.
- **v2 (2026-05-19)** — adversarial-review absorption pass. Resolved F2-01..F2-08 (Class 2) and F1-01..F1-03 (Class 1) per `.harness/Adversarial_Review_phase_2_session_3_track_a_plan.md`. Changes:
  - **F2-01 + F1-03** — Canonical 9-stage `BootstrapStage` enum committed; bootstrap files renamed `stage_0..stage_7` with `stage_3a` + `stage_3b` (9 files total); §"Canonical bootstrap stage enumeration" table added; U-RT-49/U-RT-50 ACs rewritten to assert coverage of all 9 enum members.
  - **F2-02** — U-RT-33 reframed to "Terminal aggregate exporter manifest import (side-effect)" at L7; Pattern P1 identity-equality verification extracted as new U-RT-51 at L11.
  - **F2-03 + F1-01** — U-RT-09 backfilled: content-addressed-index reattach + semantic cache init.
  - **F2-04** — U-RT-11 scope extended to bind shadow-Git checkpoint/rollback supervisor; AC adds round-trip test.
  - **F2-05** — U-RT-44 scoped to `harness-runtime/`-owned drain (flag-polling). Risk surface #4 added.
  - **F2-06** — U-RT-17/18/19 switched to async clients (`AsyncAnthropic`, `AsyncOpenAI`, `ollama.AsyncClient`); U-RT-46 close awaitable.
  - **F2-07** — U-RT-00 added as hard-gate root: `Spec_Harness_Runtime_v1.md` authoring is a unit, not a soft recommendation. U-RT-01 depends on U-RT-00.
  - **F2-08** — ACs rewritten at U-RT-21 (byte-identical replay test), U-RT-24 (transient-staircase observability), U-RT-32 (named writer entry + round-trip test).
  - **F1-02** — Dropped unused `(strawman §N)` citation convention from §2 preamble.
- **v2.1 (2026-05-19)** — minor revision; closes the v1.1 spec change-note "Downstream absorption owed" line.
  - Added §9 as a one-paragraph pointer at `Spec_Harness_Runtime_v1.md` v1.1 §15. Spec §15 is the single source of truth for spec-to-plan traceability; the plan does not duplicate the matrix. (Earlier in-session iteration mirrored the full table; rejected as duplicate source of truth.)
  - No unit-set, dependency-graph, AC, or topology changes. Pure trace-documentation pass.
- **v2.10 (2026-05-21)** — minor revision; absorbs `Spec_Harness_Runtime_v1.md` v1.11 → v1.12 Form A NOTE-form amendment per c_rt_18 MCP-workflow-initiation-topology fork operator-ratified resolution (RATIFIED at HEAD `e9b9c49`; fork-ratified commit `bd9281a`; spec-absorbed commit `7f2fee3`). New sibling unit U-RT-62 added at L9-quinquies per Q3 ratification (FastMCP server hosting + `run_workflow` MCP tool registration + `HarnessMCPServer` primitive + `api.run()` thin-wrapper reframe + `ServerCtxElicitCallback` replacing `_PlaceholderMCPCallback`; 10 ACs covering primitive declaration / FastMCP lifecycle / tool handler body / callback replacement / `api.run()` reframe / e2e topology test / `MCPHost` schema preservation / carrier-preservation / placeholder retirement closure / batch 9 retirement event filing). U-RT-15 scope preserved verbatim per Q3 atomicity discipline (H_T-as-MCP-client surface; orthogonal MCP role at U-RT-62). Q2 ratification (`api.run()` thin-wrapper reframe) absorbed at U-RT-62 AC #5 as implementation detail. Q4 ratification (`HarnessMCPServer` sibling primitive distinct from `MCPHost`) absorbed at U-RT-62 AC #1 + AC #7. Q5 ratification (RETIRE-READY → RETIRED gate on (a)+(b) jointly; CP-18 disjointness) absorbed at U-RT-62 AC #J + §6 v2.10 addendum. §3 topology graph extended with L9-quinquies block (deps: U-RT-15 + U-RT-25 + U-RT-42 + U-RT-49 + U-RT-60 → U-RT-62; acyclic invariant preserved). §6 v2.10 addendum adds 2-row retirement-table entry (H_T-CP-20 RETIRE-READY → RETIRED gate + new H_T-as-MCP-server hosting site → U-RT-62) + H_T-CP-18 retirement disjointness pin (per Q5). §9 pointer bumped v1.11 → v1.12 + U-RT-62 §15 row addition flagged for spec-writer SKILL.md §5 downstream absorption. Unit count grows by one (52). No coverage-matrix change at C-RT-NN contracts (U-RT-62 traces to existing C-RT-04 + C-RT-08 + C-RT-18 narrative-only refinements). Sections preserved verbatim from v2.9: §1 package layout; §2 L0–L11 unit bodies U-RT-00 through U-RT-59 (verbatim) + L9-quater U-RT-60 ACs #1–#14 (verbatim); §3 L0–L11 + L9-bis + L9-ter + L9-quater topology blocks (verbatim); §4 24 CXA edges table; §5 spec recording strategy; §6 §6.5 substitution table + v2.3 / v2.5 / v2.7 addenda (verbatim); §7 verification strategy; §8 known risks; revision log v1 through v2.9. **Downstream findings owed (Class 3 informational; not blocking U-RT-62 implementation):** spec v1.12 §15 spec-to-plan traceability row for U-RT-62 owed at next spec revision pass (cross-file back-reference; not the implementation-planner's edit per spec-writer SKILL.md §5 procedure).
- **v2.9 (2026-05-21)** — minor revision; Q5 single-arc co-publication absorbing `Spec_Harness_Runtime_v1.md` v1.10 → v1.11 Form A NOTE-form amendment (HEAD `904a4ec`) per c_rt_18 span-attribute-carrier-drift fork operator-ratified resolution (RATIFIED at HEAD `95a9436`). 2 U-RT-60 AC body amendments + AC #11 assertion-shape note + §9 pointer bump v1.10 → v1.11:
  - **AC #7** — Q1+Q2 ratification absorption: drop hand-coded `hitl.gate.evaluated.placement` + `.response_palette` + `.outcome` attribute names; conform to canonical 3-attribute set per ADR-D5 v1.3 §1.8 row 1 + CP carrier `HITL_SPAN_NAMESPACE_SCHEMA[0]` (`hitl.gate.level` + `hitl.gate.persona_tier` + `hitl.gate.required`). Audit-compose-failure annotation uses OTel `Span.set_status(StatusCode.ERROR)` + `Span.record_exception` per semconv-canonical error discipline (NOT custom `.outcome` attribute).
  - **AC #8** — Q1+Q2 ratification absorption: canonical 4-span shape per ADR-D5 v1.3 §1.8 + CP carrier `HITL_SPAN_NAMESPACE_SCHEMA` 4-entry shape. Composer body opens `hitl.invocation.opened` per spec §14.8.2 step 4f-bis (NEW at v1.11; placement attribute lives here at `hitl.invocation.placement` per row 2; handoff_context_size_bytes + audit_ledger_entry_id complete the 4-attribute set). On response received → `hitl.invocation.responded` span with canonical `hitl.response.{class,latency_ms,summary_hash}` per row 3 (rename + pull in previously-dropped summary_hash). On timeout → canonical `hitl.invocation.timed_out` dedicated span per row 4 with `hitl.timeout.{duration_ms,degradation_mode_applied}` (NOT `.outcome="timeout"` attribute extension).
  - **AC #11** — assertion-shape note appended for canonical 4-span coverage per matching placement: each matching placement produces exactly one `hitl.gate.evaluated` + exactly one `hitl.invocation.opened` + exactly one of (`hitl.invocation.responded` OR `hitl.invocation.timed_out`) per spec v1.11 §14.8.5 hierarchy diagram + §14.8.6 Invariants.
  - **§9** — traceability pointer bumped v1.10 → v1.11.
  - Sections preserved verbatim from v2.8: §1 package layout; §2 L0–L11 unit bodies U-RT-00 through U-RT-59 (verbatim) + U-RT-60 ACs #1 + #2 + #3 + #4 + #5 + #6 + #9 + #10 + #12 + #13 + #14 (verbatim); §3 topology graph (L9-quater wrap-chain block preserved); §4 24 CXA edges table; §5 spec recording strategy; §6 7d retirement preview (v2.7 addendum preserved verbatim); §7 verification strategy; §8 known risks; revision log v1 through v2.8.
  - No unit-count change (51); no dependency-graph change; no topology-graph change; no coverage-matrix change (every spec contract covered by ≥1 unit per v2.8 baseline; v1.11 amendment is narrative-refinement within C-RT-18 §14.8.2 + §14.8.5, not a new contract).
  - **Downstream findings owed (Class 3 informational; not blocking U-RT-60 implementation):** Q6 systemic-pattern follow-on arc for `harness-adversarial-reviewer` / `phase-7-implementation` / `spec-writer` skill body extension — operator schedules independently of U-RT-60 resumption; file Class 3 informational record at fork-resolution landing time per ratified Q6 disposition.
- **v2.8 (2026-05-21)** — minor revision; Q5 single-arc co-publication absorbing `Spec_Harness_Runtime_v1.md` v1.9 → v1.10 amendment (HEAD `510c502`) + 6 secondary findings from `.harness/adversarial_review_u_rt_60_pre_impl.md` per c_rt_18 fork operator-ratified resolution (RATIFIED at HEAD `fb545ec`). 5 U-RT-60 AC body amendments + §9 pointer bump v1.9 → v1.10:
  - **AC #2** — Q1 ratification absorption: MCP-server substitution-mechanism category pin per spec v1.10 §14.8.3 + F1-01 absorption: deferred-list enumeration sentence appended.
  - **AC #9** — F2-03 absorption: `entry_core` opaque-str carry-forward acknowledgment (inherits U-RT-59 implementation arc Class 3 prose-drift item 5 transparently via shared `cp_audit_to_od_audit` converter; no fork required).
  - **AC #11** — F2-02 absorption: multi-placement test design revised from impossible-at-v1.9/v1.10-MVP case (PRE_ACTION + SUB_AGENT_BOUNDARY cross-position) to exercise-able same-position case (two PRE_ACTION placements on a single INFERENCE_STEP).
  - **AC #14** — Q2 ratification absorption: retirement-reading "analogous to" → "via" mirroring spec v1.10 §14.8.3 simplification + F2-01 absorption: U-CP-13 added to condition A unit-ID enumeration (workflow-binding production site per spec §14.8.2 step 1).
  - **§9** — traceability pointer bumped v1.9 → v1.10.
  - **F1-02 (U-RT-51 seam-count split) — change-note observation row, scope-minimality option (b):** §6 v2.7 addendum's "U-RT-51 Pattern P1 completeness assertion seam-count extends from 22 → 23" remains as downstream-absorption-owed note at change-note level; U-RT-51 plan body NOT amended in v2.8 (still cites 22 seams per CXA v2.3 §3). U-RT-60 implementation arc operator extends `test_cxa_pattern_p1.py` to assert the 23rd seam (CXA v2.5 §2.3.7 U-CP-46 → U-OD-00 HITL audit-write seam) at the same arc as U-RT-60 landing; alternatively a U-RT-51 follow-on plan revision lands the formal AC update post-U-RT-60.
  - **F1-03 (version-baked fail-class name) — change-note observation row:** `RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19` bakes spec version into fail-class name; observed naming-convention outlier vs other RT-FAIL-* identifiers; documented expected behavior per spec v1.10 §14.8 fail-class table ("Documented expected behavior at MVP; resolved at the validator-composer arc landing (future C-RT-NN)"). Future churn at validator-composer arc landing — fail-class either renamed (breaking error-class identity downstream) or kept with confusing name. Pure observation; no AC body change required.
  - **Downstream findings owed at separate spec-writer arc (Class 3 drift; not blocking U-RT-60 implementation):** spec v1.10 §14.8.3 X-AL-2 condition-A enumeration omits U-CP-13 (the plan AC #14 corrects this at the plan layer but the spec carries the same gap; non-blocking because the §14.8.2 step 1 narrative cites U-CP-13 explicitly + the plan AC enforces). File as Class 3 spec-prose-drift item at next runtime spec revision pass.
  - Sections preserved verbatim from v2.7: §1 package layout; §2 L0–L11 unit bodies U-RT-00 through U-RT-59 (verbatim); §2 L9-quater U-RT-60 ACs #3 + #4 + #5 + #6 + #7 + #8 + #10 + #12 + #13 (verbatim); §3 topology graph (L9-quater wrap-chain block preserved); §4 24 CXA edges table; §5 spec recording strategy; §6 7d retirement preview (v2.7 addendum preserved verbatim per F1-02 option (b) scope-minimality); §7 verification strategy; §8 known risks; revision log v1 through v2.7.
  - No unit-count change (51); no dependency-graph change; no topology-graph change; no coverage-matrix change (every spec contract covered by ≥1 unit per v2.7 baseline; v1.10 amendment is narrative-refinement within C-RT-18, not a new contract).
- **v2.7 (2026-05-20)** — minor revision; absorbs `Spec_Harness_Runtime_v1.md` v1.8 → v1.9 (adds §14.8 C-RT-18 HITL gate composer contract) + `Cross_Axis_Composition_Document_v2_5.md` §2.3.7 (CP→OD bucket cardinality 1 → 2 typed seams adding U-CP-46 → U-OD-00 HITL audit-write seam). Adds U-RT-60 at new L9-quater section with 14 ACs covering: composer class + Protocol conformance (#1); `AskUserQuestionSurface` Protocol + H_E binding (#2); placement-trigger filter + empty-skip (#3); VALIDATOR_ESCALATION foreclosure Q5 mirror (#4); HandoffContext + matrix-cell + `_hitl_required` bounded reading (#5); palette unconditional NOTE 6-iv mirror (#6); `hitl.gate.evaluated` span (#7); AskUserQuestion invocation + timeout + `hitl.invocation.responded` span (#8); 4-substep audit-write HITL-flavor + CXA v2.5 second seam + shared converter (#9); 4-response processing + EDIT replace-semantics NOTE 6-ii mirror (#10); multi-placement same-step independence NOTE 6-i mirror (#11); retry-of-gate per-attempt re-eval NOTE 6-iii mirror (#12); bootstrap stage 5 wrap-asymmetry per spec §14.8.1 + producer-side carrier import discipline (#13); Phase 7d batch 8 H_T-CP-20 RETIRE-READY (#14). Updates §3 topology graph with L9-quater wrap-chain block (U-RT-12 + U-RT-25 + U-RT-26 + U-RT-27 + U-RT-32 + U-RT-42 + U-RT-58 + U-RT-59 → U-RT-60). Updates §6 retirement preview with v2.7 addendum (H_T-CP-20 row + CXA v2.5 §2.3.7 seam-count growth note + U-RT-51 seam-count extension 22 → 23). Bumps §9 traceability pointer v1.6 → v1.9. Unit count grows by one (51). Operator-ratified architectural decisions captured at the v1.9 spec change-note + the `.harness/class_1_tension_cp_20_hitl_gate_composer_underspec.md` fork record (Q1 = AskUserQuestion @ 7b; Q2 = retry-outer-of-HITL per wrap-asymmetry; Q3 = shared converter at harness-cxa/; Q4 = separate pause/resume arc; Q5 = PRE_ACTION + SUB_AGENT_BOUNDARY only). Four path-(ii) NOTE-deferrals at spec §14.8.7 mirrored as ACs #6 / #10 / #11 / #12 per advisor recommendation (pre-emptive disclosure pattern; matches U-RT-59 v1.8 NOTE-absorption pattern in reverse — pre-empts at spec authoring instead of absorbing post-implementation).
