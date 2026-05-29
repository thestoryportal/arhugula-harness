# Implementation Plan — Harness Runtime — v2.38

*Delta over v2.37. v2.38 is a Phase 7 → design-phase Class 1 **fourth** sequel-rescope per `.harness/class_1_tension_u_rt_111_engine_layer_substrate_absence.md` §11 NEW (operator-ratified 2026-05-29 same-calendar-day sequel to v2.37). v2.35 STRUCK ACs #4/#5/#6/#8 at HITL + engine-layer disambiguator gaps; v2.36 STRUCK AC #1 at the `StepOverride` field-set / U-CP-14 disambiguator gap; v2.37 STRUCK AC #11 at the U-CP-34 primitive-scope mismatch; v2.38 STRIKES AC #2 at a **fourth structural shape — substrate-not-built-at-bootstrap-firing-site**. AC #2's firing site at `engine_selector.py:145` lives inside `materialize_engine_selector(config)` which runs at bootstrap **stage 3b CP_ROUTING**; the `cp_is_wiring` substrate is built at **stage 6 CXA_WIRING** per `harness-runtime/src/harness_runtime/bootstrap/__init__.py` `_STAGE_MODULES` tuple. At AC #2's firing site, `ctx.cp_is_wiring` does not yet exist; furthermore `materialize_engine_selector(config)` does not take a `ctx` parameter at all. Actor source is also unanchored at engine_selector scope (the AC #9 actor-source verification cannot resolve to `ctx.ledger_writer.actor` because there is no `ctx`). Synthesizing the binding chain at runtime axis — whether by bootstrap reorder (3b/6 swap), inline-adapter (bypass `cp_is_wiring` and call the CP composer free function directly with an ad-hoc adapter over `ctx.ledger_writer`), or any other shape — is X-AL-3 silent design extension per `Phase_7_Meta_Architecture_v1.md` §7.7 — same closure-event-class as v2.35 AC #4 + v2.36 AC #1 + v2.37 AC #11 STRIKES (`[[plan-revision-against-not-yet-built-substrate]]` sub-species at workflow doc §7.4.7.2). RETAINS ACs #3 + #7 + #9 + #10 (v2.38 reframed) + #12; REFRAMES AC #10 e2e from v2.37's 2 sites to v2.38's 1 site (pause-resume workflow-layer only); H_T-RT-35 transit posture PRESERVED at PARTIAL post-v2.38 impl arc per v2.35/v2.36/v2.37 §1.2 AC #12 framing.*

## §0 Change note (v2.37 → v2.38)

### §0.1 What changed

| Element | v2.37 | v2.38 |
|---|---|---|
| U-RT-111 unit body | 6 ACs (12 declared with 6 STRUCK at v2.37 — v2.35's 4 + v2.36's #1 + v2.37's #11) covering 2 caller-site invocation surfaces | **5 ACs** (12 declared with **7 STRUCK total** — v2.35's 4 + v2.36's #1 + v2.37's #11 + v2.38's #2) covering **1 caller-site invocation surface** |
| AC #2 (workload-class-selection emission @ engine_selector.py:145 inside `materialize_engine_selector(config)`) | RETAINED at v2.37 (PRESERVED VERBATIM from v2.34/v2.35/v2.36); "`emit_workload_class_selection_state_ledger_entry(workflow_id, step_id, selection_result, actor)`; `actor` from runtime context (impl-discretion at engine_selector scope)" | **STRUCK at v2.38** per fork doc §11 NEW gap finding — bootstrap stage 3b CP_ROUTING (where `materialize_engine_selector(config)` runs) precedes stage 6 CXA_WIRING (where `cp_is_wiring` binding is built) per `harness-runtime/src/harness_runtime/bootstrap/__init__.py:101-110` `_STAGE_MODULES` tuple. At the firing site, `ctx.cp_is_wiring` is unset; `materialize_engine_selector(config)` does not take a `ctx` parameter at all (signature is `materialize_engine_selector(config: RuntimeConfig) -> RuntimeEngineSelector` per `engine_selector.py:122`). Actor source also unanchored at engine_selector scope (the AC #9 actor-source-from-`ctx.ledger_writer.actor` clause cannot resolve; there is no `ctx`). Routes to CP-axis / runtime-axis design-phase per `.harness/class_1_tension_u_rt_111_engine_layer_substrate_absence.md` §11 (NEW sequel item) |
| AC #10 (reframed e2e) | 2 caller-sites (workload-class-selection + pause-resume workflow-layer) | **1 caller-site** (pause-resume workflow-layer only) |
| AC #9 (actor-source verification) | Applied across all retained caller sites including engine_selector | PRESERVED VERBATIM in body text; effective scope NARROWS to the 3 workflow_driver pause-resume sites where `ctx.ledger_writer.actor` is empirically reachable (engine_selector site removed at AC #2 STRIKE) |
| §1 unit count | 109 (UNCHANGED) | 109 (UNCHANGED — canonical-reading sequel-rescope, NOT a new unit) |
| §2 DAG | UNCHANGED | UNCHANGED |
| H_T-RT-35 transit framing | STAYS PARTIAL post-v2.37 impl arc per AC #12 (4 upstream-arc blockers) | UNCHANGED — STAYS PARTIAL post-v2.38 impl arc. **5 upstream-arc blockers** now: engine-layer impl + HITL disambiguator + override disambiguator + sibling-ledger firing-site + **NEW: bootstrap-time emission substrate (stage-ordering reorder OR alternate-firing-site OR carrier-extension for engine-selector emission)** |
| CXA v2.16 → v2.17 transit | 2 PENDING → 2 LANDED at v2.37 impl arc (U-CP-75 workload-class-selection + U-CP-76 pause-resume workflow-layer) | **1 PENDING → 1 LANDED at v2.38 impl arc** (U-CP-76 pause-resume workflow-layer ONLY). U-CP-75 workload-class-selection carries to upstream bootstrap-emission-substrate arc per §0.4 NEW row. Aggregate 6 PENDING → 1 LANDED + 5 carry at v2.38 |

### §0.2 Scope discipline

§0 (this change note); §1 U-RT-111 unit-body canonical-reading amendment STRIKING AC #2; §2 DAG preservation (ZERO edge changes); §3 adjacent observations + carry-forward; §4 filing footer. All v2.37 + v2.36 + v2.35 + v2.34 + ... + v1 lineage PRESERVED VERBATIM per delta-only-plan-chain convention except the U-RT-111 AC #2 entry which is STRUCK at v2.38 + the AC #10 e2e site enumeration which is narrowed from 2 to 1 + the §3 (c) CXA transit count which is refreshed (U-CP-75 carry line) + the §3 (e) U-CP-75 transit framing which is REVERSED.

### §0.3 Authoring rationale + the v2.38 empirical finding

v2.37 §0.3 documented the empirical orientation finding at AC #11 (U-CP-34 primitive-scope mismatch). At the v2.38 impl arc empirical orientation pass (worktree `u-rt-111-impl-v2-35`, PR #61 head `6415ce2` post-v2.37 plan landing), the AC #2 caller-site investigation surfaced a **fourth structural disambiguator gap** that v2.34/v2.35/v2.36/v2.37 all missed at authoring time:

The firing site at `engine_selector.py:145` lives inside `materialize_engine_selector(config: RuntimeConfig) -> RuntimeEngineSelector`. Empirical orientation at `harness-runtime/src/harness_runtime/bootstrap/__init__.py:101-110` `_STAGE_MODULES`:

```
_STAGE_MODULES: tuple[tuple[BootstrapStage, object], ...] = (
    (BootstrapStage.PREAMBLE, stage_0_preamble),
    (BootstrapStage.IS, stage_1_is),
    (BootstrapStage.AS, stage_2_as),
    (BootstrapStage.CP_CLIENTS, stage_3a_cp_clients),
    (BootstrapStage.CP_ROUTING, stage_3b_cp_routing),     # ← engine_selector materialized here
    (BootstrapStage.OD, stage_4_od),
    (BootstrapStage.LOOP_INIT, stage_5_loop_init),
    (BootstrapStage.CXA_WIRING, stage_6_cxa_wiring),       # ← cp_is_wiring built here
    (BootstrapStage.INGRESS_ACCEPT, stage_7_ingress),
)
```

Stage 3b (CP_ROUTING) precedes stage 6 (CXA_WIRING). At AC #2's firing site:

1. **`ctx.cp_is_wiring` is unset.** The `materialize_cp_is_wiring_stage` factory at `cp_is_wiring.py:369` does not execute until stage 6. The Phase 1 v2.36 plumbing landing added `HarnessContext.cp_is_wiring: object | None = None` field; at stage 3b the field IS the default `None`.
2. **`ctx` not in scope.** `materialize_engine_selector(config)` takes only `config: RuntimeConfig`; the calling stage at `stage_3b_cp_routing.py:45` reads `ctx.engine_selector = materialize_engine_selector(config)` — the caller has `ctx` but the callee does not. Threading `ctx.cp_is_wiring` to the loop body at `engine_selector.py:143-155` requires widening the `materialize_engine_selector` signature.
3. **Actor source unanchored.** AC #9's "actor sourced from `ctx.ledger_writer.actor`" mechanism requires `ctx`; absent `ctx` there is no spec-anchored derivation rule for `actor` at engine_selector scope.

Three architectural branches surface at this gap:

- **(a) Bootstrap reorder.** Move stage 6 CXA_WIRING before stage 3b CP_ROUTING. Requires substrate audit: stage 6 currently consumes routing manifest + ledger_writer + other stage-1-through-5 artifacts. Mechanical risk surface is wide; this is a runtime-spec-level decision per `Spec_Harness_Runtime_v1.md` v1.1 §1 9-value BootstrapStage enum which declares the ordering canonically.
- **(b) Inline adapter at stage 3b.** Bypass `cp_is_wiring` entirely; call the CP composer free function `emit_workload_class_selection_state_ledger_entry` directly with an inline async adapter wrapping `ctx.ledger_writer.append`. Requires widening `materialize_engine_selector` signature to accept `ledger_writer: LedgerWriter` + `actor: ActorIdentity` (or `ctx: _MutableHarnessContext`). This is a runtime-axis design extension under CP spec §16.5.8 "runtime wiring discipline binds the ledger_writer Callable here" silence on whether the binding must route through `cp_is_wiring`.
- **(c) Carrier-extension at U-RT-110.** Extend `RuntimeCpIsWiring` to optionally accept `bootstrap_emission_buffer` collecting pre-stage-6 emissions for replay at stage 6 binding-time. Requires both spec extension (the buffer is a new primitive) AND runtime-side coordination across the stage 3b → stage 6 transition.

Synthesizing any of (a)/(b)/(c) at runtime axis under CP spec §16.5 silence is X-AL-3 silent design extension. Operator ratified Reading (A) sequel-strike via AskUserQuestion 2026-05-29 (option 1 — STRIKE AC #2 + amend to v2.38; file gap finding at fork doc §11 NEW + bundle as same-PR back-flow).

Per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` 41st application at v2.38 authoring: advisor flagged bootstrap stage ordering as the load-bearing constraint pre-substantive ("stage 3b precedes stage 6 per module docstring; verify before authoring"). Empirical verification at `_STAGE_MODULES` confirmed the ordering; advisor recommended STRIKE-via-AskUserQuestion if confirmed. Grep + read of `materialize_engine_selector` signature confirmed both the `ctx`-absence gap AND the actor-source gap. Operator ratified Reading (A).

### §0.4 Out-of-scope at v2.38 (owed separately, extending v2.37 §0.4)

| Owed arc | Routing target | Rationale |
|---|---|---|
| **NEW at v2.38:** Runtime spec v1.7 → v1.N amendment AND/OR CP spec v1.26 → v1.27 amendment authorizing the bootstrap-time emission substrate for U-CP-75 workload-class-selection at engine_selector scope. Three options at upstream arc: (a) BootstrapStage enum reorder placing CXA_WIRING before CP_ROUTING (runtime spec §1 amendment); (b) `materialize_engine_selector` signature widening to accept `ledger_writer` + `actor` + emit inline at stage 3b (runtime spec §14.x amendment + CP spec §16.5.8 clarification permitting non-`cp_is_wiring` binding); (c) NEW `RuntimeCpIsWiring.bootstrap_emission_buffer` primitive with stage-6 flush (CP spec §16.5 extension + runtime spec extension). Operator-discretion at upstream arc. | Runtime-axis design-phase routing OR CP-axis design-phase routing per `Project_Workflow_v1_12.md` §2.7.6 | Pre-v2.38 plan v2.34/v2.35/v2.36/v2.37 row 2 assumed `ctx.cp_is_wiring` reachable at `materialize_engine_selector` scope; empirical bootstrap ordering at HEAD `6415ce2` `_STAGE_MODULES` contradicts the assumption. CP spec §16.5.8 binds runtime wiring discipline to "ledger_writer Callable" without specifying whether `cp_is_wiring` is mandatory consumer; spec is silent on bootstrap-time-vs-runtime-time emission scope for U-CP-27 / U-CP-75. |
| CP spec v1.26 → v1.27 canonical-reading amendment for U-CP-34 firing-site scope | CP-axis design-phase routing | UNCHANGED carry from v2.37 §0.4 |
| CP plan v2.29 → v2.30 NEW units for engine-layer impl | CP-axis design-phase routing | UNCHANGED carry from v2.36/v2.37 §0.4 |
| CP spec v1.26 → v1.27 amendments for HITL + override disambiguator fields | CP-axis design-phase routing OR engine-layer impl arc absorption | UNCHANGED carry from v2.36/v2.37 §0.4 |
| CXA v2.16 → v2.17 §2.3.2 enumeration refresh — full 6 PENDING → 6 LANDED | Retirement-batch filing arc post-engine-layer-landing | v2.38 lands 1-of-6 PENDING (U-CP-76 only); 5-of-6 carry to upstream arcs (UNCHANGED from v2.37 except U-CP-75 moves from "v2.37 LANDED" to "carries to bootstrap-emission-substrate arc") |
| Runtime spec §12.3 prose alignment per v2.33 (C-defer) | Next runtime-spec revision pass | UNCHANGED carry |

---

## §1 U-RT-111 unit-body canonical-reading amendment (v2.38)

### §1.1 Site

PRESERVED VERBATIM from v2.37 §1.1 — U-RT-111 slots at the L7-and-later wiring-consumer layer, singleton extension of U-RT-110's stage-6 surface.

### §1.2 U-RT-111 — Body (v2.38 canonical reading)

**Implements:** UNCHANGED structurally from v2.37 §1.2 except CP-materializable edge count refreshed (CP spec v1.26 §16.5.7 firing-site discipline for the **1 retained caller-site** at v2.38; CP spec v1.26 §16.5.9 invariants 1-7; runtime spec v1.7 §12.3 17-edge enumeration — **1 of 7 CP-materializable edges at this arc**, down from v2.37's 2; cross-axis composition per CXA v2.16 §0.4 — **1 PENDING → 1 LANDED** upon v2.38 impl arc completion + e2e verification PASS).

**Files (v2.38 narrowed from v2.37):**
- ~~`harness-runtime/src/harness_runtime/lifecycle/engine_selector.py`~~ — **REMOVED at v2.38** per AC #2 STRIKE
- `harness-cp/src/harness_cp/workflow_driver.py` (EXTEND at 3 `PauseResumeProtocol` class method invocation sites — line 559 RESUME_ATTEMPTED + line 769 PAUSE_CAPTURED drain-flag path + line 894 PAUSE_CAPTURED HITL-signal path; existing body PRESERVED VERBATIM at non-firing-site lines; **line numbers refreshed at v2.38 against HEAD `6415ce2`** — v2.37 carried `:546`/`:756`/`:881` from HEAD `9cca6d6` per checkpoint anchor)
- `harness-runtime/tests/test_cp_is_caller_site_integration.py` (NEW — 1 scoped e2e covering the 1 implementable site in a single workflow lifecycle + 1 negative-path test (no-binding short-circuit) + 3 per-caller-site unit tests for AC #3 = **5 tests; reframed from v2.37's 4 to v2.38's 5** to compensate for losing the workload-class-selection unit test by adding 3 distinct AC-#3 site unit tests)

**Signatures introduced:** NONE at U-RT-111 (UNCHANGED from v2.37 §1.2) — v2.38 modifies existing function bodies at 3 caller-site locations (all within `workflow_driver.execute_workflow`) to invoke U-RT-110's `emit_pause_resume_state_ledger_entry` method via the sync-bridging idiom.

**Per-caller-site invocation contract (1 invocation surface at v2.38; 3 sites within `workflow_driver.execute_workflow` body sharing the same composer method):**

| # | Caller site (file:line at HEAD `6415ce2`) | U-RT-110 method invoked | Composer args sourced at caller site | Spec authority |
|---|---|---|---|---|
| 1 | ~~`harness-cp/src/harness_cp/workflow_driver.py:777` + `override_evaluator.py:61`~~ — **STRUCK at v2.36** | ~~`emit_override_state_ledger_entry`~~ | ~~per v2.35 §1.2 row 1~~ | Routes to CP-axis disambiguator-extension arc per fork §9 |
| 2 | ~~`harness-runtime/src/harness_runtime/lifecycle/engine_selector.py:145`~~ — **STRUCK at v2.38** | ~~`emit_workload_class_selection_state_ledger_entry`~~ | ~~per v2.36 §1.2 row 2~~ | Routes to runtime-axis / CP-axis design-phase per fork §11 NEW |
| 3 | `harness-cp/src/harness_cp/workflow_driver.py:559` post-`protocol.attempt_resume(...)` + `:769` post-`protocol.capture_pause_snapshot(...)` drain-flag path + `:894` post-`protocol.capture_pause_snapshot(...)` HITL-signal path (line numbers REFRESHED at v2.38 against HEAD `6415ce2`) | `emit_pause_resume_state_ledger_entry(workflow_id, step_id, protocol_event_kind, event_sequence_id, protocol_state_snapshot, actor)` | per v2.36 §1.2 row 3 detail PRESERVED VERBATIM; `protocol_event_kind` is `PauseResumeProtocolEventKind.RESUME_ATTEMPTED` at site `:559` and `PauseResumeProtocolEventKind.PAUSE_CAPTURED` at sites `:769` + `:894`; `actor` from `ctx.ledger_writer.actor` per AC #9 (workflow_driver scope clean) | CP spec v1.26 §16.5.7 row U-CP-30 (workflow-layer per CP spec v1.11 §26 NEW NOTE coexistence) |
| 11 | ~~`harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py` post-step-8 audit-composition success path~~ — **STRUCK at v2.37** | ~~`emit_sibling_ledger_entry(...)`~~ | ~~per v2.37 detail~~ | Routes to CP-axis canonical-reading or alternate-site spec amendment arc per fork §10 |

**Depends on:** PRESERVED VERBATIM structurally from v2.37 §1.2 — U-RT-110 (within-axis), U-RT-12 (transitive), U-CP-76 (cross-axis transitive via U-RT-110 for the retained pause-resume site). **U-CP-75 cross-axis edge for AC #2 NO LONGER consumed at v2.38 impl arc** (AC #2 STRUCK); edge declaration carries to upstream bootstrap-emission-substrate arc.

**Acceptance criteria (v2.38 reframed from v2.37):**

1. ~~**Caller-site (1) override-application.**~~ **STRUCK at v2.36** (preserved at v2.37, preserved at v2.38).

2. ~~**Caller-site (2) workload-class-selection @ engine_selector.py:145.**~~ **STRUCK at v2.38** per fork doc §11 NEW gap finding: bootstrap stage 3b CP_ROUTING (where `materialize_engine_selector(config)` runs) precedes stage 6 CXA_WIRING (where `cp_is_wiring` binding is built); at the firing site `ctx.cp_is_wiring` is unset and `materialize_engine_selector(config)` does not take a `ctx` parameter; actor source also unanchored. Synthesizing the binding chain at runtime axis under CP spec §16.5 + runtime spec §1 silence on bootstrap-time emission scope would be X-AL-3 silent design extension. Routes to design-phase per §0.4 NEW row.

3. **Caller-site (3) pause-resume workflow-layer.** PRESERVED VERBATIM from v2.37 §1.2 AC #3 — only the line numbers refresh per HEAD `6415ce2`: at `workflow_driver.py:559` post-`protocol.attempt_resume(...)` await `ctx.cp_is_wiring.emit_pause_resume_state_ledger_entry(...)` with `protocol_event_kind=PauseResumeProtocolEventKind.RESUME_ATTEMPTED`; at `:769` post-`protocol.capture_pause_snapshot(...)` (drain-flag path) await with `PAUSE_CAPTURED`; at `:894` post-`protocol.capture_pause_snapshot(...)` (HITL-signal path) await with `PAUSE_CAPTURED`. All 3 sites use the sync-bridging idiom `_run_protocol_method_sync(...)` mirroring the existing `protocol.attempt_resume(...)` invocation pattern at the same sites. Defensive `getattr(ctx, "cp_is_wiring", None)` access pattern (sibling to `skill_activation_emitter` pattern at `workflow_driver.py:506` per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` recommendation); when `cp_is_wiring` is None, skip emission silently (no-binding short-circuit per operator-opt-in pattern).

4-6. ~~**Caller-site (4)/(5)/(6).**~~ **STRUCK at v2.35** (preserved verbatim).

7. **CP-axis production functions PRESERVED VERBATIM.** PRESERVED VERBATIM from v2.37 §1.2 AC #7 — ZERO modification to any CP-axis function signature; ZERO return-type widening at CP-axis. v2.38: the 1 site at `workflow_driver.py:559+769+894` extends the SURROUNDING function bodies (`execute_workflow` + `_execute_steps`) with the NEW emission invocations; the `PauseResumeProtocol` class method signatures PRESERVED VERBATIM.

8. ~~**Disambiguator-availability halt.**~~ **STRUCK at v2.35** (preserved).

9. **Actor-source verification.** PRESERVED VERBATIM from v2.37 §1.2 AC #9 in body text; **effective scope NARROWS at v2.38** to the 3 workflow_driver pause-resume sites where `ctx.ledger_writer.actor` is empirically reachable (engine_selector site removed at AC #2 STRIKE). The actor binding at the 3 retained sites resolves to `ctx.ledger_writer.actor` per CP spec v1.6 §25.2.1 9th-field (StepExecutionContext) lineage at workflow_driver scope.

10. **1-site full chain e2e (REFRAMED from v2.37's 2 to v2.38's 1).** `harness-runtime/tests/test_cp_is_caller_site_integration.py` exercises the 1 caller-site invocation surface (pause-resume workflow-layer; 3 firing sites within a single end-to-end workflow lifecycle exercising both `RESUME_ATTEMPTED` and `PAUSE_CAPTURED` event kinds). Assert: persisted ledger contains entries with `action_id = cp.pause-resume-protocol` (the v2.38 implementable subset); `chain_verification` per C-IS-06 §6 passes for the multi-entry chain.

11. ~~**U-CP-34 LANDED-but-never-fired residual closure.**~~ **STRUCK at v2.37** (preserved at v2.38).

12. **H_T-RT-35 transit posture PRESERVED at v2.38.** v2.37 AC #12 PRESERVED VERBATIM — H_T-RT-35 STAYS PARTIAL post-v2.38 impl arc. NO retirement-event filing at v2.38 impl arc per X-AL-2 second-conjunct unreachability finding at fork doc §3 + §9 + §10 + §11. The bootstrap-emission-substrate gap at AC #2 STRIKE adds a **fifth upstream-arc blocker** (alongside engine-layer impl + HITL disambiguator + override disambiguator + sibling-ledger firing-site); H_T-RT-35 RETIRE-READY transit gated on ALL five upstream arcs landing + e2e exercising the full chain.

**Tests (v2.38 reframed):** `test_caller_site_pause_resume_protocol_emission_resume_attempted` (PRESERVED from v2.37); `test_caller_site_pause_resume_protocol_emission_pause_captured_drain_flag` (PRESERVED from v2.37); `test_caller_site_pause_resume_protocol_emission_pause_captured_hitl_signal` (PRESERVED from v2.37); `test_one_caller_site_full_chain_verification_passes_e2e` (AC #10 reframed from v2.37's 2-site test name); `test_no_pause_resume_protocol_binding_does_not_emit_state_ledger_entry` (PRESERVED from v2.37 — operator-opt-out negative path covering all 3 PAUSE_RESUME sites). **REMOVED at v2.38:** `test_caller_site_workload_class_selection_emission_engine_selector` (covered AC #2 STRUCK at v2.38).

**Rollback boundary:** UNCHANGED from v2.37 §1.2.

---

## §2 DAG delta

ZERO DAG edge changes at v2.38 (UNCHANGED from v2.37). The sequel-rescope drops one more AC (AC #2) at U-RT-111; it does NOT drop the unit itself, the unit's dependency edges, or its position in the topological sort. v2.34 + v2.35 + v2.36 + v2.37 §2 DAG declarations PRESERVED VERBATIM.

Unit count: 109 (UNCHANGED from v2.37).

---

## §3 Adjacent observations + carry-forward

(a) **CP plan v2.29 → v2.30 NEW units for engine-layer impl OWED at separate design-phase routing.** PRESERVED VERBATIM from v2.37 §3 (a).

(b) **CP spec v1.26 → v1.27 disambiguator-field amendments OWED at separate arc.** EXTENDED at v2.38: now covers 6 disambiguator surfaces — `RewrittenToolCall.semantic_variant_binding_id` + `PauseEvent.pause_event_id` + `resume_attempt_count` (v2.35 carry) + `override_id` + `policy_id` derivation rule OR `StepOverride` model field-set extension (v2.36 carry) + U-CP-34 `emit_sibling_ledger_entry` firing-site canonical-reading clarification (v2.37 carry) + **NEW at v2.38: bootstrap-time emission substrate for U-CP-75 workload-class-selection (BootstrapStage enum reorder OR `materialize_engine_selector` signature widening OR `RuntimeCpIsWiring.bootstrap_emission_buffer` primitive per §0.4 NEW row)**. Implementer-discretion at the upstream arcs.

(c) **CXA v2.16 §0.4 forward-tracking partial transit at v2.38 impl arc — REFRESHED.** **1 PENDING → 1 LANDED at v2.38 impl arc PR merge** for U-CP-76 (pause-resume workflow-layer) ONLY. Remaining 5 PENDING carry to upstream arcs (U-CP-74 override + U-CP-75 workload-class-selection NEW carry + U-CP-77 HITL + U-CP-78 engine-layer + U-CP-79 engine-layer).

(d) **H_T-RT-35 batch-filing precedent NOT applicable at v2.38.** PRESERVED VERBATIM from v2.37 §3 (d). Now requires **6-arc convergence** (v2.38 impl arc + override-disambiguator arc + HITL disambiguator arc + engine-layer impl arc + sibling-ledger firing-site arc + **NEW: bootstrap-emission-substrate arc**) for full RETIRE-READY transit per X-AL-2 second-conjunct.

(e) ~~**U-CP-75 workload-class-selection LANDED at v2.37 impl arc per AC #2 (PRESERVED).**~~ **REVERSED at v2.38** — U-CP-75 does NOT land at v2.38 impl arc per AC #2 STRIKE. U-CP-75 carries to upstream bootstrap-emission-substrate arc per §0.4 NEW row + §3 (b) extended.

(f) **Workspace `CLAUDE.md` §2.4 runtime plan row bump owed.** Runtime plan row v2.37 → v2.38 at workspace root `CLAUDE.md` §2.4. Co-publication this arc. Unit count: 109 (UNCHANGED).

(g) **`harness-runtime/CLAUDE.md` plan-unit anchor refresh owed at impl arc.** PRESERVED VERBATIM from v2.37 §3 (g).

(h) **PR-shape recommendation.** v2.38 sequel-rescope arc + impl arc BUNDLED at PR #61 (same branch `worktree-u-rt-111-impl-v2-35`; Phase 1 plumbing already shipped at `9cca6d6`; v2.37 AC #11 STRIKE landed at `6415ce2`; v2.38 plan + fork §11 + workspace CLAUDE.md bump + AC #3 impl + AC #10 e2e + negative path test bundled as additional commits). Mixed-posture bundled-absorption arc per CLAUDE.md §11.4; the fork doc §11 amendment IS the back-flow record; X-AL-3 CI guard satisfied via fork doc co-location at same PR.

(i) **41st application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`.** Pre-substantive advisor consultation at v2.38 authoring caught the bootstrap stage ordering as load-bearing pre-substantive ("stage 3b precedes stage 6 per module docstring; verify before authoring"). Empirical verification at `_STAGE_MODULES` confirmed; advisor recommended STRIKE-via-AskUserQuestion if confirmed. Memory posture continues to validate — 4 of 4 sequel-rescope arcs at U-RT-111 in single calendar day caught pre-substantive by the discipline; ZERO X-AL-3 silent extension occurred.

(j) **Sub-species `plan-revision-against-not-yet-built-substrate` cardinality 3 → 4 at workflow doc §7.4.7.2.** v2.37 §3 (j) catalogued cardinality 3 (v2.35 + v2.36 + v2.37 transit). v2.38 IS the **FOURTH instance** of the same sub-species at the SAME atomic-unit (U-RT-111) in a single calendar day (2026-05-29). **Distinct closure-event-class at v2.38 from v2.35/v2.36/v2.37 instances:** v2.35/v2.36 = "missing carrier-field on existing type" (downstream-substrate-absence shape); v2.37 = "primitive-scope mismatch between firing site and spec-anchored canonical use" (semantic-scope-conflation shape); **v2.38 = "binding-substrate not yet constructed at firing site execution-time per bootstrap stage ordering"** (substrate-lifecycle-mismatch shape — distinct from prior 3 because the substrate DOES exist at this codebase, just not at this firing site's execution moment). Same meta-pattern (plan claims wiring against not-spec-anchored substrate); distinct surface (bootstrap-stage-ordering mismatch vs missing-field vs primitive-scope). Workflow-doc revision candidate strengthens further — empirical cardinality 4 across 4 sibling arcs in 1 calendar day is very strong empirical signal warranting formal inclusion at workflow doc §7.4.7.2 next revision pass.

(k) **Plan-revision discipline preserved at v2.38.** UNCHANGED from v2.37 §3 (k). v2.38 cites runtime spec v1.7 §1 (UNCHANGED) + CP spec v1.26 §16.5.8 (UNCHANGED); does NOT invent any commitment; does NOT amend any cited spec; preserves dependency edges; coverage matrix UNCHANGED.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.38 |
| Predecessor | v2.37 (runtime plan v2.36 → v2.37 third sequel-rescope at U-RT-111 STRIKE AC #11; PR #61 commit `6415ce2`) |
| Successor consumption | U-RT-111 v2.38-scope implementation arc (1 caller-site invocation surface across 3 sites + scoped 1-site e2e + negative path) — bundled at PR #61 per CLAUDE.md §11.4 |
| Cross-axis cascade | ZERO at v2.38 plan (per §0.3 + §0.4). 1 within-axis dependency edge UNCHANGED. CXA v2.17 §2.3.2 enumeration refresh partial REFRESHED from v2.37 (1 of 6 LANDED at v2.38 impl arc; remainder gated on 5 upstream arcs — now including NEW bootstrap-emission-substrate arc). |
| Authority anchors | `.harness/class_1_tension_u_rt_111_engine_layer_substrate_absence.md` §11 NEW (operator-ratified sequel-strike Reading A 2026-05-29); `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-2 + X-AL-3; `Project_Workflow_v1_12.md` §2.7.6 Class 1 back-flow; `Spec_Harness_Runtime_v1.md` v1.1 §1 BootstrapStage enum 9-value ordering (load-bearing for the substrate-lifecycle-mismatch finding); CP spec v1.26 §16.5.8 (runtime wiring discipline silence on bootstrap-time-vs-runtime-time emission scope); runtime plan v2.37 §1.2 (this v2.38 amends in-place at delta-only-plan-chain layer) |
| Co-publications | Fork doc §11 NEW filed at same PR (fourth sequel amendment to existing v2.35/v2.36/v2.37 fork doc); workspace `CLAUDE.md` §2.4 row bump (v2.37 → v2.38; unit count 109 UNCHANGED) |
| Date | 2026-05-29 |
