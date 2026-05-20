# Phase 2 Session 3 — Track A atomic-decomposition plan: `harness-runtime/`

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

**Scope:** 50 atomic units across 12 topological levels (L0–L11). Unit numbering is dense (no gaps).

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

Canonical at `design-substrate/Spec_Harness_Runtime_v1.md` v1.4 §15 (Spec-to-plan traceability) — coverage matrix mapping every U-RT-NN unit to ≥1 C-RT-NN contract, including per-bucket C-RT-12 §12.1–§12.6 rows, the C-RT-14 cross-cutting row, the v1.2-introduced U-RT-52 row (C-RT-15), and the v1.4-introduced U-RT-58 row (C-RT-16).

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
