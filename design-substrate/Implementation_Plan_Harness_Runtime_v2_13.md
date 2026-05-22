# Implementation Plan — Harness Runtime v2.13

## Change-note (v2.12 → v2.13)

**Scope of revision.** Class 1 fork resolution absorption pass for the `SandboxDecisionPolicy` phantom-cite resolution per `.harness/class_1_fork_sandbox_decision_policy_phantom_cite.md` (operator-ratified 2026-05-22 at this session, Q1=C-i + Q2=Open-now). Absorbs runtime spec v1.15 → v1.16 (this session, commit `e2877f1`): §3 C-RT-02 `sandbox_decision_policy` field-table row carrier-home cite re-pointed from `(AS spec v1.3 §15 carrier)` (phantom — empirically verified at apply: AS spec v1.3 §15/C-AS-15 is `secret.fetch` span schema, not a sandbox policy class; ZERO `SandboxDecisionPolicy` hits across all axis source trees) → `(harness-core carrier)` per Q1=C-i ratification.

**Source of fix.** `.harness/class_1_fork_sandbox_decision_policy_phantom_cite.md` operator-ratified 2026-05-22:
- **Q1=C-i** — re-home the carrier to `harness-core` package (smallest spec edit; preserves the field; no AS-axis-spec reopen; no semantic commitment to AS-internal sandbox policy at the runtime layer)
- **Q2=Open-now** — resolution arc opens this session

**Spec authority chain.** Runtime spec v1.16 §3 C-RT-02 field-table (`sandbox_decision_policy` row carrier-home cite). All other v1.16 content preserved verbatim from v1.15 per spec v1.16 change-note. AS spec v1.3 + CP spec v1.11 + OD spec v1.9 + CXA v2.8 + ADR-D2 v1.2 all unchanged per fork doc §5.

**Plan-side authoring locus decision — option (α) ratified by implementation-planner.** Per `implementation-planner` SKILL.md §3.1 single-coherent-change criterion: bundling a NEW class authoring at `harness-core` package WITH `RuntimeConfig` schema-field extension at `harness-runtime` package within U-RT-71 (option β) would constitute two coherent changes across two packages, NOT a single coherent change. Option (α) is the disciplined pick: **a NEW atomic unit U-CORE-02 at the `harness-core` plan** (v1.1 → v1.2, co-published this arc) authors the `SandboxDecisionPolicy` carrier; U-RT-71 gains a within-axis-cross-package dependency edge to U-CORE-02 (analogous to existing U-RT-NN consumers of U-CORE-01). Precedent: U-RT-71 already imports `TrustPolicy` from CP package per CP-axis authoring; same pattern applies for the harness-core `SandboxDecisionPolicy`.

**Plan-side carrier-shape decision — empty marker.** Per `implementation-planner` SKILL.md §4 sub-discipline 4.4 (no spec extension) + X-AL-3 (no silent H_T design extension at Phase 7): the spec only commits `SandboxDecisionPolicy | None` + `SandboxDecisionPolicy.default()` factory; no §14 contract specifies any internal field set (§14.9.1 step 5 reads only `sandbox.tier ≥ ToolContract.minimum_tier`; the field is a dangling marker per spec v1.16 §"Adjacent defects surfaced" finding (i)). Pre-committing internal fields (e.g. `tier_floor_overrides: Mapping[str, SandboxTier]`) would be a plan-side spec extension. The U-CORE-02 carrier shape is therefore **empty-marker**: frozen Pydantic v2 BaseModel with NO fields + `@classmethod def default() -> SandboxDecisionPolicy` returning the empty instance. Future operator-driven extension surfaces via spec extension + planner revision pass adding fields.

**Plan shape preserved.** v2.12's L9-septies cluster preserved verbatim. U-RT-71's body is cite-edited at 2 token sites (Implements row + Signatures row); U-RT-75's body is cite-edited at 1 token site (step 3 AC); U-RT-71's `Depends on` line gains the new U-CORE-02 edge. NO U-RT-71 AC change (spec v1.16 did not amend AC-bearing surface — ACs at v2.12 covering RuntimeConfig instantiation + backwards-compat + TrustPolicy storage + ValidationError on type mismatch + importable+pyright-strict are still correct). NO U-RT-72 / U-RT-73 / U-RT-74 / U-RT-68 body change (those units do not cite SandboxDecisionPolicy). NO L9-septies DAG topology change at the L9-septies internal structure; ONLY a new L0-cross-package edge into U-RT-71 from U-CORE-02.

**Sections preserved verbatim from v2.12.** §1 — L9-sexies cluster — all 8 units (U-RT-63 / U-RT-64 / U-RT-65 / U-RT-66 / U-RT-67 / U-RT-68 / U-RT-69 / U-RT-70) preserved verbatim. §1B — L9-septies cluster — U-RT-72 / U-RT-73 / U-RT-74 preserved verbatim. §2 DAG topology preserved within-L9-septies-internal-structure; only the new U-CORE-02 → U-RT-71 edge added at §2 below. §3 coverage matrix preserved (no contract additions; only cite-precision delta). v2.12 + v2.11 + ... + v2.0 + v2 chain preserved.

**Status posture.** Proposed (v2.12) → **Proposed (v2.13)**. v2.13 is a single-token-class cite-edit absorption patch under FM-2 no-extension discipline — 3 cite-edits across 2 units (U-RT-71 ×2, U-RT-75 ×1) + 1 new within-axis-cross-package dependency edge on U-RT-71; no unit re-decomposition; no AC body change; no contract addition.

**Downstream absorption owed (post-v2.13).**
(a) Workspace `CLAUDE.md` §2.3 runtime spec row already at v1.16 per spec-writer commit `e2877f1`; no further bump at this arc.
(b) Workspace `CLAUDE.md` §2.4 runtime plan row version bump (v2.12 → v2.13); unit count unchanged at 76 (U-RT-00..U-RT-70 + U-RT-71..U-RT-75). Co-published this arc.
(c) Workspace `CLAUDE.md` §2.4 NEW row for `Implementation_Plan_Harness_Core_v1_2.md` — v1.1 → v1.2 unit count 1 → 2 (U-CORE-01 preserved + U-CORE-02 new). Co-published this arc.
(d) Phase 7 cluster-open authorization for L9-septies at next session per `phase-7-implementation` skill discipline. Cluster sequencing unchanged from v2.12 except L9-septies opens with U-CORE-02 as the new L0 entry-point (U-CORE-02 → U-RT-71 → U-RT-72 → {U-RT-73, U-RT-75} → U-RT-68 per DAG).
(e) NO CXA v2.8 amendment owed at this arc per fork doc §5 (ZERO cross-axis cascade).
(f) NO CP / OD / AS plan amendments owed at this arc per fork doc §5 (ZERO cross-axis cascade).

---

## §1 — L9-septies cluster — U-RT-71 + U-RT-75 cite-edit absorptions

### U-RT-71 — RuntimeConfig schema extension: trust_policy + sandbox_decision_policy optional fields (cite-edited at v2.13)

- **Implements:** Runtime spec **v1.16** §3 C-RT-02 field-table extension (rows for `trust_policy: TrustPolicy | None` + `sandbox_decision_policy: SandboxDecisionPolicy | None`). Both fields default `None` → factories use type defaults (`TrustPolicy.default()` + `SandboxDecisionPolicy.default()`). [v2.13 cite-edit: spec version bump v1.15 → v1.16 absorbing the C-i re-home.]
- **Files:** `harness-runtime/src/harness_runtime/config.py` (EXTEND — `RuntimeConfig` Pydantic v2 BaseModel field-table extension).
- **Signatures:** `class RuntimeConfig`: append optional fields `trust_policy: TrustPolicy | None = None` + `sandbox_decision_policy: SandboxDecisionPolicy | None = None`. `TrustPolicy` imported from CP package per CP spec v1.11 §27 carrier home. `SandboxDecisionPolicy` imported from **harness-core package per harness-core plan v1.2 U-CORE-02** (re-pointed at v2.13 from prior v2.12 erroneous "AS spec v1.3 §15 carrier home" cite per Class 1 fork resolution `.harness/class_1_fork_sandbox_decision_policy_phantom_cite.md` Q1=C-i ratification 2026-05-22).
- **Depends on:** [U-CORE-02 (within-axis-cross-package: harness-core — SandboxDecisionPolicy carrier authored at harness-core plan v1.2 §2)]. NEW edge at v2.13 absorbing Q1=C-i re-home. TrustPolicy import from CP package per existing landed carrier (cluster 10-CP-C close); no new edge owed for TrustPolicy.
- **ACs:** (preserved verbatim from v2.12 — spec v1.16 did not amend AC-bearing surface; the 5 ACs covering RuntimeConfig instantiation / backwards-compat / TrustPolicy storage / ValidationError on type mismatch / importable+pyright-strict remain correct)
  1. `RuntimeConfig(deployment_surface=..., ..., trust_policy=None, sandbox_decision_policy=None)` instantiates without ValidationError.
  2. `RuntimeConfig(...)` instantiated WITHOUT the new fields preserves v1.14-shape backwards-compatibility (both fields default to `None` per Pydantic field default; existing callers do not break).
  3. `RuntimeConfig(..., trust_policy=TrustPolicy(...), ...)` accepts an operator-supplied TrustPolicy instance and stores it on the frozen model.
  4. `RuntimeConfig(..., trust_policy="not_a_policy", ...)` raises typed `ValidationError` per Pydantic field validation (type mismatch).
  5. Importable; pyright strict mode passes. Per-field minor-version-bump invariant per C-RT-02 v1.1 version-evolution clause preserved (both new fields are optional → minor bump v1.14 → v1.15; v1.15 → v1.16 is a cite-correction patch under FM-2, no field-shape change).

### U-RT-75 — Stage 5 factory: materialize_runtime_tool_dispatcher_stage(ctx, config) → RetryBreakerToolDispatcher (cite-edited at v2.13)

- **Implements:** Runtime spec **v1.16** §14.9.3 stage-5 factory contract — 5-step composition body: (1) construct `PerServerTrustEvaluator` consuming `config.trust_policy`; (2) construct `MCPClientNamespaceEmitter` consuming `ctx.mcp_client_host.tool_registry`; (3) construct bare `RuntimeToolDispatcher` with ctx refs + `config.sandbox_decision_policy`; (4) construct `RetryBreakerToolDispatcher` per §14.11 wrapping the bare dispatcher; (5) bind wrapper to `ctx.tool_dispatcher`. [v2.13 cite-edit: spec version bump v1.15 → v1.16; no factory-body change.]
- **Files:** `harness-runtime/src/harness_runtime/bootstrap/factories/runtime_tool_dispatcher_factory.py` (NEW — factory body module; mirrors existing factory-module pattern at `harness-runtime/src/harness_runtime/bootstrap/factories/`).
- **Signatures:** `async def materialize_runtime_tool_dispatcher_stage(ctx: _MutableHarnessContext, config: RuntimeConfig) -> RetryBreakerToolDispatcher`. Factory body executes 5 steps verbatim per spec **v1.16** §14.9.3 stage-5 prose; binds intermediate carriers to `ctx.per_server_trust_evaluator` + `ctx.mcp_namespace_emitter` during composition; returns the wrapper for the stage-5 callsite (U-RT-68) to bind to `ctx.tool_dispatcher`.
- **Depends on:** [U-RT-71 (config fields), U-RT-72 (ctx fields), U-RT-67 (bare RuntimeToolDispatcher class), U-RT-74 (RetryBreakerToolDispatcher wrapper class), U-CP-68 (cross-axis: CP — PerServerTrustEvaluator), U-CP-69 (cross-axis: CP — MCPClientNamespaceEmitter)]. U-RT-71's new dep on U-CORE-02 is transitively closed; U-RT-75 declares only direct deps per `implementation-planner` SKILL.md §7 no-transitive-omission discipline.
- **ACs:** (preserved verbatim from v2.12 — spec v1.16 did not amend stage-5 factory contract beyond the §3 cite re-point; AC step-by-step body unchanged)
  1. `materialize_runtime_tool_dispatcher_stage(ctx, config)` with valid ctx (post-stage-3a) + config returns a `RetryBreakerToolDispatcher` instance.
  2. Factory step 1: `ctx.per_server_trust_evaluator` bound to a `PerServerTrustEvaluator` instance consuming `config.trust_policy` (or `TrustPolicy.default()` if `None`).
  3. Factory step 2: `ctx.mcp_namespace_emitter` bound to an `MCPClientNamespaceEmitter` instance consuming `ctx.mcp_client_host.tool_registry`.
  4. Factory step 3: a bare `RuntimeToolDispatcher` constructed with refs to `ctx.mcp_client_host` + `ctx.per_server_trust_evaluator` + `ctx.mcp_namespace_emitter` + `config.sandbox_decision_policy` (or `SandboxDecisionPolicy.default()` — class home at `harness-core` per U-CORE-02 / v2.13 cite-edit absorbing Q1=C-i re-home); NOT bound to `ctx.tool_dispatcher` (private to wrapper).
  5. Factory step 4: a `RetryBreakerToolDispatcher` constructed wrapping the bare dispatcher with `inner=<bare_dispatcher>` + `retry_breaker=ctx.retry_breaker` + `tracer_provider=ctx.tracer_provider`.
  6. Factory step 5: returns the wrapper (caller U-RT-68 binds to `ctx.tool_dispatcher`).
  7. Integration test: full stage-3a + stage-5 invocation with mock MCP server config produces a wired `ctx.tool_dispatcher` that dispatches a known tool through wrapper → bare dispatcher → MCP host successfully; all 4 ctx fields populated post-factory.

**Other L9-septies units (U-RT-72, U-RT-73, U-RT-74) preserved verbatim from v2.12.** Those units do not cite `SandboxDecisionPolicy` and require no v2.13 absorption.

**U-RT-68 (REWRITTEN at v2.12) preserved verbatim from v2.12.** U-RT-68's stage-5 callsite invocation consumes the U-RT-75 factory output (bound to `ctx.tool_dispatcher`); does not directly cite `SandboxDecisionPolicy`. No v2.13 absorption.

---

## §2 — DAG topology delta (v2.12 → v2.13)

1 new within-axis-cross-package edge added at L9-septies cluster: **U-CORE-02 → U-RT-71**. NO other DAG changes. Topological sort preserved acyclic:

```
L9-septies (post-v2.13 with U-CORE-02 entry-point):
  L0-within-delta: U-CORE-02 (new at v2.13; SandboxDecisionPolicy carrier at harness-core),
                   U-RT-74 (preserved from v2.12 — no deps within delta)
  L1-within-delta: U-RT-71 (←U-CORE-02 NEW EDGE; ←U-CP-72-transitive for TrustPolicy at CP package — no
                   new edge per existing landed carrier),
                   U-RT-72 (preserved from v2.12: ←74, ←63 L9-sexies, ←U-CP-68/69 cross-axis)
  L2-within-delta: U-RT-73 (preserved from v2.12: ←71, ←72, ←63/64/65/66 L9-sexies),
                   U-RT-75 (preserved from v2.12: ←71, ←72, ←67 L9-sexies, ←74, ←U-CP-68/69 cross-axis)

L9-sexies (rewrite delta preserved from v2.12):
  L3-within-delta: U-RT-68 REWRITTEN (preserved from v2.12: ←75 L9-septies, ←67 L9-sexies)
```

**Within-axis-cross-package edge classification.** U-CORE-02 → U-RT-71 is a within-axis-cross-package edge (analogous to existing U-CORE-01 consumers across all axes). Per CXA v2.1 §2.3 + workspace CLAUDE.md §3.3 (`harness-core` hosts shared types), edges between axis-plan units and `harness-core` units are NOT cross-axis edges in the CXA sense; they are within-axis-cross-package consumption edges. NO CXA v2.8 amendment owed.

**Cross-axis edges:** unchanged from v2.12. U-RT-72 + U-RT-75 → U-CP-68 + U-CP-69 preserved (already documented at v2.12 §2). NO new cross-axis edge introduction at v2.13 per fork doc §5.

DAG verified acyclic via Kahn execution (delta layer): 1 new edge consumed (U-CORE-02 → U-RT-71); remaining edge set ∅. The new edge sits at L0 boundary and creates no new cycle path (U-CORE-02 has no deps; U-RT-71 has no path back to U-CORE-02).

---

## §3 — Coverage matrix delta (v2.12 → v2.13)

| Contract (spec v1.16) | Units covering | Change at v2.13 |
|---|---|---|
| C-RT-02 §3 RuntimeConfig (2 new optional fields; carrier-home cite re-pointed at v1.16) | U-RT-71 | preserved row; cite-precision delta only (spec v1.15 → v1.16) |
| C-RT-19 §14.9.3 stage-5 lifecycle placement (factory body) | U-RT-75 | preserved row; cite-precision delta only (spec v1.15 → v1.16) |
| All other contract rows | all other units | preserved verbatim from v2.12 |

**Coverage gap audit:** none surfaced at coherence pass.

**Cite-precision audit:** all v2.13 surviving cites against runtime spec point at **v1.16** (latest filed version per `Project_Workflow_v1_8.md` §7.4 use-latest-version body-citation-alignment clause). Cross-axis cites to CP spec v1.11 / AS spec v1.3 / OD spec v1.9 unchanged.

**Harness-core plan citation:** U-RT-71's `Depends on` row cites `U-CORE-02` at `Implementation_Plan_Harness_Core_v1_2.md` §2 (co-published this arc).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_13.md` |
| Version | v2.13 |
| Filing event | `SandboxDecisionPolicy` phantom-cite Class 1 fork resolution absorption pass; runtime spec v1.15 → v1.16 co-published `e2877f1`; harness-core plan v1.1 → v1.2 co-published this arc; 2026-05-22 |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_12.md` (v2.12 substantive content preserved verbatim outside the 3 cite-edit sites at U-RT-71 / U-RT-75 + the new U-CORE-02 → U-RT-71 dependency edge) |
| New units | 0 at this plan (the new U-CORE-02 unit is filed at `Implementation_Plan_Harness_Core_v1_2.md` co-published this arc) |
| Revised units | 2 (U-RT-71 cite-edits + new dep; U-RT-75 cite-edit) |
| Cluster | L9-septies preserved; L9-sexies preserved (with U-RT-68 v2.12 rewrite preserved verbatim) |
| Cross-axis dependencies | unchanged from v2.12 (2 cross-axis edges to U-CP-68 + U-CP-69 preserved at U-RT-72 + U-RT-75); 1 NEW within-axis-cross-package edge (U-CORE-02 → U-RT-71); NO new CXA v2.8 edge enumeration count delta per fork doc §5 |
| DAG verification | Kahn-acyclic; 1 new within-axis-cross-package edge consumed; ∅ remaining edges |
| Coverage verification | All v1.16 spec contracts covered ≥ 1 unit (v1.16 = v1.15 contracts + cite-correction; no contract addition); all v2.12-preserved units retain ≥ 1 contract citation |
| Fork ratification | `.harness/class_1_fork_sandbox_decision_policy_phantom_cite.md` RATIFIED 2026-05-22 |
| Date | 2026-05-22 |
