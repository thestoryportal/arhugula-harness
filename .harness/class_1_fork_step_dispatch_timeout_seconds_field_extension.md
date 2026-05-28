# Class 1 Fork — `step_dispatch_timeout_seconds` C-RT-03 RuntimeConfig field extension (per-step ↔ whole-workflow timeout-budget conflation at stage 5 facade wiring)

**Filed:** 2026-05-28 at runtime spec v1.30 §7 carve-out follow-on, pre-substantive-work.
**Workspace HEAD at filing:** `3d3b7b1` (main, post runtime spec v1.29 → v1.30 7-of-8 bundled absorption).
**Routing class:** Class 1 (halt-execution; X-AL-3 silent-absorption prevention per workspace `CLAUDE.md` §4.4 + Meta-Architecture §7.7 — no silent H_T design extension at Phase 7 execution).
**Surfaced by:** `class_3_tension_u_rt_59_spec_prose_drift.md` §7 (filed 2026-05-20 at U-RT-59 Path B wiring landing `d64d8cf`); carved out from runtime spec v1.30 bundled-absorption arc per advisor pre-substantive consultation 2026-05-28 (X-AL-3 risk caught — scope sharpened 8 → 7 + 1 carve-out).
**Status:** ✅ FULLY-APPLIED 2026-05-28 — operator-ratified Reading A 2026-05-28 (Q1=A required-with-default 30.0s; Q2=30.0s; Q3=β in-place at U-RT-02; Q4=p `RT-FAIL-STEP-DISPATCH-TIMEOUT`) via AskUserQuestion. Applied at runtime spec v1.30 → v1.31 NEW §3 row + §11 row + runtime plan v2.26 → v2.27 U-RT-02 in-place AC amendment + harness-runtime impl (`types.py` `step_dispatch_timeout_seconds: float = 30.0` field landing + `sync_dispatcher_facade.py` NEW `StepDispatchTimeoutError` typed exception class + 3 `stage_5_loop_init.py:332/336/356` callsite updates reading `config.step_dispatch_timeout_seconds` + drift-item-7 comment-marker removal at lines 325-331 + `workflow_driver.py` `type(exc).__name__ == "StepDispatchTimeoutError"` name-match handler mapping to `RT-FAIL-STEP-DISPATCH-TIMEOUT`) + 4 NEW tests (RuntimeConfig field-default + independence-from-drain + facade `StepDispatchTimeoutError` raise verification + bootstrap stage-5 binding refresh) + 1 in-place test refresh (`test_d4_result_timeout_fires` `TimeoutError` → `StepDispatchTimeoutError`) + 1 in-place bootstrap test refresh (`config.drain_timeout_seconds` → `config.step_dispatch_timeout_seconds`) + class_3_tension_u_rt_59_spec_prose_drift Status refresh OPEN → 8-OF-8 CLOSED + workspace `CLAUDE.md` row bump + this fork doc Status refresh PROPOSING → ✅ FULLY-APPLIED. 1802/1802 harness-runtime + harness-cp tests pass + 4 skipped. ZERO cross-axis cascade. Filed → ratified → applied single-arc single-day per Reading A precondition (Q1=A precondition-bundled spec + production binding co-publication).

---

## §1 — The gap

### §1.1 Production binding (per-step ↔ whole-workflow timeout conflation)

`harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py:325-360` binds three `StepKindDispatcher` rows (INFERENCE_STEP, SUB_AGENT_DISPATCH, TOOL_STEP) through `materialize_sync_dispatcher_facade(...)`. All three callsites pass `config.drain_timeout_seconds` as the facade's `result_timeout_seconds` parameter:

```python
# line 325-360 (post v1.30 absorption; surrounding comment confirms drift item 7)
# Registry binding: both rows wrap through `SyncDispatcherFacade` at the
# top so the CP `StepDispatcher` Protocol (sync) is satisfied uniformly.
# `materialize_sync_dispatcher_facade` captures the running event loop
# (this stage executes on the outer api.py loop per loop-capture-timing
# invariant). Result-timeout reuses `config.drain_timeout_seconds`;
# tracked at Class 3 drift item 7 for the future
# `step_dispatch_timeout_seconds` config split.
inference_step_dispatcher = materialize_sync_dispatcher_facade(
    cast(Any, ctx.llm_dispatcher),
    result_timeout_seconds=config.drain_timeout_seconds,
)
sub_agent_step_dispatcher = materialize_sync_dispatcher_facade(
    cast(Any, ctx.sub_agent_dispatcher),
    result_timeout_seconds=config.drain_timeout_seconds,
)
# ... (TOOL_STEP at line 356-358 identical pattern)
tool_step_dispatcher = materialize_sync_dispatcher_facade(
    cast(Any, ctx.tool_dispatcher),
    result_timeout_seconds=config.drain_timeout_seconds,
)
```

The conflation: `SyncDispatcherFacade.dispatch`'s `future.result(timeout=...)` is a **per-step worker-thread blocking bound**; `drain_timeout_seconds` is the **whole-workflow drain shutdown bound** (`harness_runtime.api.run()` wraps the CP workflow driver call in `asyncio.wait_for(drain_timeout_seconds)` per C-RT-11 + C-RT-14). Wiring the per-step bound to the whole-workflow bound means a single hung step's worker-thread can consume the entire drain-timeout budget before unblocking — the per-step bound is operationally inert.

### §1.2 Spec authority gap

Runtime spec v1.30 §11 declares only `drain_timeout_seconds` as the workflow-execution drain bound. No per-step dispatch timeout is declared at C-RT-03 RuntimeConfig (§3). The spec is silent on the per-step bound; production lacks the field; the facade constructor accepts the parameter but receives the wrong bound.

`harness-runtime/src/harness_runtime/types.py:1013` declares `drain_timeout_seconds: float = 60.0` with full docstring citing C-RT-11 + C-RT-14 RT-FAIL-DRAIN-TIMEOUT. No sibling field at present.

### §1.3 Failure mode

Operationally observable: a single hung dispatch (e.g., LLM API hang, sub-agent infinite loop, tool blocked on external I/O) consumes the full `drain_timeout_seconds` budget at the per-step facade. When `api.run()`'s outer `asyncio.wait_for(drain_timeout_seconds)` then fires, the workflow is forced to shutdown via RT-FAIL-DRAIN-TIMEOUT — but the in-flight step's worker thread has already consumed the entire budget at the per-step layer. The per-step bound provides **no early-termination signal** above the drain-timeout layer; it is structurally redundant with the outer bound.

At a tunable split: per-step bound (e.g., 30s) fires FIRST, surfacing a typed per-step timeout failure, leaving drain-timeout budget for the workflow driver to mark the step failed + advance to next step OR drain cleanly. The drain-timeout bound becomes a backstop, not the only timeout.

### §1.4 Why Class 1 (not Class 3)

Per `Project_Workflow_v1_8.md` §2.7.6 + workspace `CLAUDE.md` §4.4:

- **X-AL-3 invariant:** "no silent H_T design extension at Phase 7 execution. New H_T primitives surfaced at execution-time route to design-phase back-flow (Class 1) before implementation proceeds." Adding `step_dispatch_timeout_seconds: float` to `RuntimeConfig` IS a new H_T design extension — it expands the C-RT-03 RuntimeConfig contract surface.
- **Authority chain compliance:** `RuntimeConfig` is canonical at runtime spec v1 §3 C-RT-03. Field-set extension routes through Phase 5 spec revision-pass before Phase 7 production binding.
- **Cascade scope:** field addition triggers runtime spec v1.30 → v1.31 §3 absorption + runtime plan v2.26 → v2.27 absorption at the `RuntimeConfig`-carrying atomic unit (U-RT-17 per `Implementation_Plan_Harness_Runtime_v2_26.md` field-landing convention; verify at impl arc) + harness-runtime impl (`types.py:1013` sibling field + 3 callsite production updates at `stage_5_loop_init.py:332/336/356`) + test additions covering per-step-timeout-fires-before-drain semantics. Intra-runtime-axis only; ZERO cross-axis cascade expected.

Two convergent Class 1 triggers (X-AL-3 + authority-chain compliance). Not Class 3 because: (a) the extension is not pure documentation-drift; it adds a new contract surface at C-RT-03; (b) downstream consumers (production wiring + tests) will need to absorb the new field; (c) the X-AL-3 silent-absorption discipline is workspace-canonical and explicitly applies to spec extensions surfaced at Phase 7. Advisor pre-substantive consultation 2026-05-28 caught this exact risk during the v1.30 bundled-absorption arc — confirming Class 1 routing.

---

## §2 — Three readings (operator decision required)

### §2.1 Reading A — Minimal additive: required field with documented default

**Spec extension:** Add `step_dispatch_timeout_seconds: float = 30.0` (required field with default; non-Optional) to `RuntimeConfig` at runtime spec v1.30 → v1.31 §3 C-RT-03 canonical-reading amendment. NEW field declaration with documented semantics:

- Default: 30.0s (operator-tunable; suggested smaller than `drain_timeout_seconds = 60.0` default by ~2× factor).
- Semantics: per-step worker-thread blocking bound at `SyncDispatcherFacade.dispatch`'s `future.result(timeout=...)`. A single step's hang surfaces a typed per-step timeout failure BEFORE the whole-workflow drain bound fires.
- Independence: independent of `drain_timeout_seconds`; the drain bound becomes a backstop ensuring shutdown progress when per-step bound is also exceeded or when other progress conditions fail.
- Fail class: typed per-step timeout failure (`RT-FAIL-STEP-DISPATCH-TIMEOUT` proposed; concrete name + binding site at impl arc).

**Production binding:** `stage_5_loop_init.py:332/336/356` three callsites read `config.step_dispatch_timeout_seconds` instead of `config.drain_timeout_seconds` for `result_timeout_seconds`. Remove the drift-item-7 carve-out comment at `:325-331`.

**Scope:** ~4-6 commits — runtime spec v1.31 §3 NEW field + runtime plan v2.27 absorption at U-RT-17 (or successor RuntimeConfig-carrying unit) + harness-runtime impl (`types.py` sibling field + 3 callsite updates + comment-marker removal) + test additions covering per-step-fires-before-drain semantics + workspace CLAUDE.md row bump + fork doc Status refresh PROPOSING → ✅ APPLIED.

**Pros:**
- Cleanest spec shape; required field with documented default matches `drain_timeout_seconds` precedent at runtime spec v1 §3 declaration style.
- Operator-tunable from day one.
- Forecloses §1.3 failure mode at the per-step bound layer.

**Cons:**
- All existing `RuntimeConfig` instantiation sites get the new default automatically (Pydantic v2 default); ZERO known breakage (`RuntimeConfig` is constructed once at `api.run()` entry); residual risk if external test fixtures construct `RuntimeConfig` with `model_fields_set` exhaustive assertions.

### §2.2 Reading B — Optional field (defer-tunability)

**Spec extension:** Add `step_dispatch_timeout_seconds: float | None = None` (Optional, default None) to `RuntimeConfig`. Production binding reads `config.step_dispatch_timeout_seconds if config.step_dispatch_timeout_seconds is not None else config.drain_timeout_seconds` — preserves v1.7+ MVP wiring for None case; operator-surfaced configs use the operator's value.

**Production binding:** Same 3 callsites with the if-None-else-drain coalescing expression.

**Scope:** ~4-6 commits, same as Reading A.

**Pros:**
- Backward-compatibility shape matches `[[fork-h-t-cp-19-default-gate-level-spec-extension]]` precedent (Optional widening; preserves MVP read path).
- Zero downstream-consumer disruption risk (None preserves drift-item-7 behavior verbatim).

**Cons:**
- Preserves the §1.3 failure mode unless operator-supplied — production defaults to the conflated behavior.
- Tunability semantics at the spec layer are softer ("operator may supply" vs "operator-tunable").
- Asymmetry with `drain_timeout_seconds` sibling field (required-with-default) at C-RT-03 §3.

### §2.3 Reading C — Defer indefinitely (close fork doc without spec extension)

**Spec extension:** None. Document at the v1.30 v1.30 §7 carve-out body as "deferred to step_dispatch_timeout_seconds substantive arc (no current production binding owed)" — explicit non-extension disposition.

**Production binding:** Preserve current conflated wiring. Comment marker at `stage_5_loop_init.py:325-331` retained as audit trail.

**Scope:** ~1 commit — fork doc Status refresh PROPOSING → ✅ CLOSED-AS-DEFERRED + workspace CLAUDE.md row bump (no spec or production change).

**Pros:**
- Zero risk; preserves existing behavior verbatim.
- Defers timeout-budget split until empirical failure mode is observed.

**Cons:**
- Preserves §1.3 failure mode indefinitely.
- §7 remains carried at `class_3_tension_u_rt_59_spec_prose_drift.md` as the only unresolved item from the 8-item drift catalogue (status-quo at v1.30 publication).
- Operationally, the conflation is a latent timing-defect that surfaces only on hung-step incidents — defer cost is unbounded.

---

## §3 — Operator decisions

### §3.1 Q1 — Which reading?

| Option | Reading | Recommendation |
|---|---|---|
| (A) | Reading A — required field with `default = 30.0` | Cleanest spec shape; matches `drain_timeout_seconds` sibling-pattern; forecloses failure mode immediately |
| (B) | Reading B — Optional field, coalesce to drain bound when None | Conservative; matches H_T-CP-19 precedent; preserves MVP-default read path; failure mode persists when None |
| (C) | Reading C — defer indefinitely; close fork as wont-fix | Zero-touch; preserves status quo; defer cost unbounded |

### §3.2 Q2 — If Reading A or B chosen: default value?

Suggested defaults per §2.1: `step_dispatch_timeout_seconds = 30.0` (Reading A) — matches the ~2× factor against `drain_timeout_seconds = 60.0` to give the drain bound headroom for graceful shutdown after a per-step timeout fires.

| Option | Default | Rationale |
|---|---|---|
| (i) | 30.0s | ~2× headroom against drain default; suggested at §2.1 |
| (ii) | 20.0s | ~3× headroom; more aggressive per-step bound |
| (iii) | 45.0s | ~1.3× headroom; conservative per-step bound (closer to drain) |
| (iv) | Custom (operator-specified) | Operator picks a different concrete value |

### §3.3 Q3 — Cascade scope: where does the new field land at the plan layer?

Runtime plan v2.26 declares 96 atomic units across L1..L9-quaterdecies clusters. Two convention layers govern `RuntimeConfig` field landings, depending on the shape of the extension:

- **Binding-chain shape** (config-field + empty-marker sub-model + HarnessContext field + factory + stage-wiring + fail-class + e2e) — modern precedent at L9-decies (U-RT-83 ValidatorFrameworkConfig) / L9-undecies (U-RT-87 PauseResumeProtocolConfig) / L9-quaterdecies (U-RT-96 WebhookDeliveryComposerConfig). Each lands as a NEW single-unit-or-3-unit cluster at the L9-N apex.
- **Primitive scalar field-set extension shape** (single field + production binding read + fail-class — no sub-model, no ctx field, no factory) — modern precedent at single-unit-body in-place AC amendments per CP plan v2.25 U-CP-13 `default_gate_level` (+1 field, +3 ACs) and runtime plan v2.26 U-RT-94 `fail_detail_hash` (in-place AC text amendment).

`step_dispatch_timeout_seconds` matches the **primitive scalar** shape — it is a single `float` field, no sub-model, no `HarnessContext` field, no factory, no stage materialization. The binding-chain shape is overkill.

Empirical verification 2026-05-28: `RuntimeConfig` was originally authored at **U-RT-02** (commit `a04c6f8` "feat(runtime): U-RT-02 — RuntimeConfig + HarnessContext schemas"). The U-RT-02 body lives at the original v2.5-or-earlier authoring plan version and only delta-changes appear in v2.11+ delta plan files per delta-only-plan-chain convention.

Three candidate landing patterns:

| Option | Landing site | Rationale |
|---|---|---|
| (α) | NEW single-unit cluster (L9-quindecies) decomposing field addition + 3 callsite updates + test | Cleanest cluster boundary if treated as binding-chain shape; overkill for a primitive float field per precedent above |
| (β) | U-RT-02 in-place AC text amendment + Files-line extension to add stage_5_loop_init.py callsites + NEW AC for production binding | Minimal cluster surface; matches CP v2.25 U-CP-13 + runtime v2.26 U-RT-94 in-place single-unit-body amendment precedent for primitive scalar field-set extensions; lands at the authoring unit per spec-revision-driven plan-revision convention |
| (γ) | Hybrid — field landing at U-RT-02 in-place AC + NEW single-unit at L9-quindecies for production binding + test | Splits spec-extension from production-binding for cleaner traceability; matches L9-decies / L9-undecies cluster-boundary split shape but with primitive field at L0 |

Recommendation: **(β) in-place at U-RT-02** — the scope is tight (1 field + 3 stage_5_loop_init.py callsite updates + 1 fail-class addition + 1-2 unit tests + 1 e2e test), and the in-place AC amendment shape matches the closest-precedent (primitive scalar field-set extensions). The L9-N cluster shape is reserved for binding chains with sub-models + factories.

### §3.4 Q4 — Fail-class naming?

Reading A or B introduces a typed per-step timeout failure. Sibling-pattern to existing runtime fail classes at runtime spec §11 (RT-FAIL-DRAIN-TIMEOUT, RT-FAIL-PROTOCOL-VIOLATION) and stage materialization fail classes (RT-FAIL-VALIDATOR-STAGE-MATERIALIZE, RT-FAIL-PAUSE-RESUME-STAGE-MATERIALIZE, RT-FAIL-WEBHOOK-COMPOSER-STAGE-MATERIALIZE). Candidate names:

| Option | Name | Notes |
|---|---|---|
| (p) | `RT-FAIL-STEP-DISPATCH-TIMEOUT` | Sibling to RT-FAIL-DRAIN-TIMEOUT; explicit per-step scope |
| (q) | `RT-FAIL-FACADE-RESULT-TIMEOUT` | Names the binding site (SyncDispatcherFacade.dispatch result_timeout); implementation-layer-leaky |
| (r) | `RT-FAIL-PER-STEP-TIMEOUT` | Symmetric with whole-workflow drain framing; emphasises the per-step ↔ whole-workflow distinction |

Recommendation: **(p) `RT-FAIL-STEP-DISPATCH-TIMEOUT`** — matches existing taxonomy at runtime spec §11 + stage_5_loop_init.py docstring convention.

---

## §4 — Downstream cascade

Per §1.4 cascade scope analysis. Intra-runtime-axis only; ZERO cross-axis cascade expected:

| Artifact | Touch | Notes |
|---|---|---|
| Runtime spec v1.30 → v1.31 §3 C-RT-03 | NEW field declaration + docstring + §11 fail-class addition | Spec-side authoring |
| Runtime plan v2.26 → v2.27 U-RT-02 (or operator-ratified landing site per Q3) | In-place AC amendment per Q3 (β) | Plan-side absorption |
| `harness-runtime/src/harness_runtime/types.py:1013` | NEW sibling field declaration | Pydantic field landing |
| `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py:332/336/356` | 3 callsite updates + comment-marker removal at :325-331 | Production binding |
| `harness-runtime/tests/` | NEW e2e test covering per-step-timeout-fires-before-drain semantics | Test coverage |
| `class_3_tension_u_rt_59_spec_prose_drift.md` | Status refresh OPEN → ✅ 8-OF-8 CLOSED at §7 row | Carry closure |
| Workspace `CLAUDE.md` §2.3 + `harness-runtime/CLAUDE.md` | Row bump v1.30 → v1.31 | Citation cascade |
| This fork doc | Status refresh PROPOSING → ✅ APPLIED with operator-ratified reading | Closure |

**ZERO cross-axis edges expected** — `step_dispatch_timeout_seconds` is intra-C-RT-03; no IS / AS / CP / OD / CXA artifact cite. Verified via grep at design-substrate/ — no consumer references the field name (field does not exist).

---

## §5 — Pattern catalogued at filing

**Pre-substantive advisor consultation prevents X-AL-3 silent-absorption.** The 2026-05-28 v1.30 bundled-absorption arc originally framed all 8 spec-prose drift items as "ship as bundled spec patches." Advisor caught §7's structural difference at pre-substantive consultation: items §§1-6 + 8 are fidelity-pure citation-correction patches (production already matches the absorbed reading); §7 adds a NEW contract surface (`step_dispatch_timeout_seconds` field at C-RT-03) with NO current production binding. Absorbing §7 into v1.30 as a spec-only contract addition would be silent H_T design extension at Phase 7 per workspace `CLAUDE.md` §4.4 X-AL-3.

Scope sharpened 8 → 7 items + 1 carve-out at v1.30. §7 routes through proper back-flow channel (this fork doc) before any production binding lands.

This is the **24th application** of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` memory posture in workspace history. Pattern continues to discriminate silent-absorption risk from fidelity-pure refresh risk.

---

## §6 — Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_fork_step_dispatch_timeout_seconds_field_extension.md` |
| Filed at | 2026-05-28 |
| Filing arc HEAD | `3d3b7b1` (main, post v1.30 absorption) |
| Filing authority | Workspace `CLAUDE.md` §4.4 X-AL-3 + Meta-Architecture §7.7 |
| Source carry | `class_3_tension_u_rt_59_spec_prose_drift.md` §7 (filed 2026-05-20 at `d64d8cf`) |
| Carve-out anchor | Runtime spec v1.30 change-note (`design-substrate/Spec_Harness_Runtime_v1.md`) + workspace `CLAUDE.md` §2.3 runtime spec row + fork doc Status at this filing |
| Successor consumption | Operator ratification via AskUserQuestion (Q1 + Q2 + Q3 + Q4); then absorption arc landing the ratified reading |
| Routing target | Phase 5 spec revision (runtime spec v1.30 → v1.31) + Phase 6 plan absorption (runtime plan v2.26 → v2.27) before Phase 7 production binding |

---

*End of fork doc.*
