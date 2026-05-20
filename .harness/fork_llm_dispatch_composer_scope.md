# Fork — LLM-dispatch composer scope (load-bearing for §9 Class 2 surface close)

**Filed:** 2026-05-20, Phase 7 sub-phase 7d.
**Trigger:** v2 retirement ledger second pass (commit `6796ef0`) surfaced that the H_T runtime ships 3 provider adapters but no production LLM call site. Operator-acknowledged at v2 §9.2.3 + checkpoint `20260520-074654-7c-reverification-7d-second-pass-complete` §Remaining Work item 3.
**Fork class candidate:** Class 2 (operator decision among 3 routing options) — may escalate to Class 1 if option C is chosen.
**Pattern reference:** same shape as `[[fork-u-rt-49-cost-attribution-invocation-underspec]]` (file → ratify → resolve same-day arc, 2026-05-20) and `[[fork-u-cp-56-resumption-underspec]]` (Path A-modified, 2026-05-20).

---

## §1 Observed gap

### §1.1 Runtime state at HEAD (`a0fdd1a`)

`harness-runtime/src/harness_runtime/lifecycle/providers.py`:

| Code site | What lands |
|---|---|
| `providers.py:679-706` | All 3 provider adapters constructed (anthropic + openai + ollama) at stage 3a |
| `providers.py:788-857` | Capability bindings frozen post-construction |
| `providers.py:854` | Final capability binding row |

`harness-runtime/src/harness_runtime/lifecycle/routing_manifest.py:143-145`: typed `RoutingManifest` persisted to `PathClass.ROUTING_MANIFEST`.

`harness-runtime/src/harness_runtime/lifecycle/override_evaluator.py:78-88`: per-step override evaluation surface.

**Production execution path:**

`harness-cp/src/harness_cp/workflow_driver.py:execute_workflow` (lines 233-540):

| Line | What it invokes |
|---|---|
| 360 | `resolve_step_binding(manifest_entry, step_id, default_model_binding=...)` — typed manifest → binding |
| 379 | `StepDispatcher.dispatch(binding, step)` — **operator-injected step dispatcher** |
| 397-417 | `_append_step_ledger_entry(step_idempotency_key=...)` — typed state-ledger append (IS-5/IS-7 retire-ready) |
| 331/336/392 | `lifecycle_emitter.emit(...)` — workflow-event-class emission |

### §1.2 What is verifiably absent

Grep `harness-runtime/src/` for any LLM call site:

| Pattern | Hits |
|---|---|
| `messages.create` | 0 |
| `chat.completions` | 0 |
| `client.chat` | 0 |
| `client.messages` | 0 |
| `provider.invoke` (production call) | 0 (only Protocol declaration at `providers.py`) |
| `await *_client.*` matching an LLM dispatch shape | 0 |

The `StepDispatcher` interface at `workflow_driver.py:379` is an **architectural seam** — an operator-supplied dispatcher is invoked at each step. The runtime ships no production multi-provider router that consumes the 3 constructed provider adapters from `providers.py:679-706` and dispatches an LLM call against the resolved `binding`.

### §1.3 What this gap blocks (per v2 ledger)

Direct blocks:

| Substitution | Status at v2 §5 | Why it can't retire |
|---|---|---|
| H_T-CP-1 | STILL-BOUNDED | Multi-LLM routing core never exercised end-to-end |
| H_T-CP-2 | STILL-BOUNDED | Dependency-only on CP-1 |
| H_T-CP-3 | STILL-BOUNDED | `retry.*` namespace has no event to emit from |
| H_T-CP-4 | STILL-BOUNDED | Fallback chain has no failed call to fall back from |
| H_T-CP-5 | STILL-BOUNDED | Dependency-only on CP-1 |
| H_T-OD-2 | PARTIAL → upgrade-blocked | GenAI semconv binding has no GenAI span to bind to |

Cascade blocks (per Meta-Architecture §6.3):

| Cascade | Status | Reason |
|---|---|---|
| §6.3.1 CP-1 → AS-8 (`anthropic.*` namespace emission) | DORMANT | CP-1 STILL-BOUNDED |
| §6.3.2 OD-2 + CP-24 → CXA-5 (F-CP-01 Stage 3b inversion) | DORMANT | OD-2 PARTIAL (cannot upgrade until LLM dispatch exists to emit `harness.breaker.*` spans through) |

Effective scope: **≥ 5 RETIRE-READY events directly + 2 cascades + 1 PARTIAL upgrade unblocked** by closing this scope decision.

### §1.4 §9 Class 2 multi-LLM commitment surface — most consequential unmet commitment

Per `Phase_7_Meta_Architecture_v1.md` §9 + §10.4.3, H_T-CP-1 retirement closes the §9 Class 2 surface when multi-LLM runtime commitment is met. ADR-F1 v1.2 multi-LLM-by-design commitment is currently met at:

- Design (ADR-F1 v1.2 ratified)
- Specification (Spec_Control_Plane_v1_3.md C-CP-01 §1)
- Library code (3 provider adapters constructed; capability-aware abstraction present at `providers.py`)

And unmet at:

- **Runtime** — no LLM call flows through the constructed providers in the production execution path

This is the load-bearing project commitment that has not been operationalized. Every other retirement is downstream of resolving where the LLM-dispatch composer lives.

---

## §2 Where the spec is silent

### §2.1 Runtime spec v1.1 coverage

`Spec_Harness_Runtime_v1.md` §5 (C-RT-05 — Provider SDK lifecycle) specifies:

- Provider client construction at stage 3a
- `ProviderClient` Protocol shape
- Capability-aware abstraction surface

§5 does NOT specify:

- A composer that consumes resolved `binding` + step input and invokes `ProviderClient.{messages.create | chat.completions | generate}` against the selected provider
- Where in the bootstrap stage sequence this composer is materialized
- Whether the composer is part of `HarnessContext` or injected per-step
- What runtime contract handles fallback when a provider raises

§16 (open questions) enumerates 9 candidate Class 1 fork surfaces (#1–#9). **The LLM-dispatch composer is NOT among them.** This is a v1.1-authoring-time absence, not a v1.1-deferred-decision.

### §2.2 CP spec coverage

`Spec_Control_Plane_v1_3.md` C-CP-01 §1 specifies the capability-aware multi-LLM abstraction surface; C-CP-02 §2 specifies layered routing strategy. Both are surface specifications — they declare what the abstraction looks like, not how the runtime invokes it.

`Implementation_Plan_Control_Plane_v2_13.md` units U-CP-01 through U-CP-55 cover all 22 CP primitives. **U-CP-01 (`Routing core + ProviderCapabilities`) landed at 7b** with the typed surface. No CP plan unit specifies a runtime LLM-dispatch composer; CP is a substrate axis providing the typed surface that runtime consumes.

### §2.3 Runtime plan coverage

The runtime plan (per `[[phase-2-runtime-close]]` memory: closed 2026-05-20 at `43500bf`; 654 runtime tests) authored U-RT-NN units through ~U-RT-55. The `StepDispatcher` injection pattern at `workflow_driver.py:379` matches the v1.4 minimum-viable scope (`SINGLE_THREADED_LINEAR + (PURE_PATTERN_NO_ENGINE | SAVE_POINT_CHECKPOINT)`) and is consistent with what the runtime spec authorized.

### §2.4 Net: no spec owns the LLM-dispatch composer

| Spec | Owns? | Why not |
|---|---|---|
| `Spec_Harness_Runtime_v1.md` | No | §5 + §16 silent on the composer; v1.1 scoped to substrate-bootstrap |
| `Spec_Control_Plane_v1_3.md` | No | CP is the substrate axis; specifies the abstraction surface, not runtime invocation |
| `Spec_Information_Substrate_v1.md` | No | Out of axis |
| `Spec_Action_Surface_v1.md` | No | Out of axis (tool-invocation runtime composer is a separate gap per v2 §9.2.2) |
| `Spec_Operational_Discipline_v1_4.md` | No | OD consumes telemetry; doesn't dispatch |

No design-substrate spec currently owns the contract. **This is the architectural ambiguity the operator is being asked to resolve.**

---

## §3 Three routing options

### §3.1 Option A — Phase-7-deferred runtime unit (in-Phase-7 closure)

**Shape.** Author a new U-RT-NN unit specifying the LLM-dispatch composer surface — a runtime-internal Pydantic v2 contract that consumes resolved `binding` + step input, dispatches to the selected `ProviderClient`, attaches a GenAI-semconv span via the materialized TracerProvider, and returns the result. No design-substrate spec extension; no ADR-revision.

**Locus.** `Spec_Harness_Runtime_v1.md` gains a new C-RT-15 contract at v1.2; the runtime plan grows a corresponding U-RT-NN unit; runtime implementation lands the composer.

**Effort.** Spec amendment ~1 hour (one new contract surface). Plan unit authoring ~1 hour. Implementation ~3-6 hours (3 provider-specific dispatch paths + telemetry binding + tests).

**Implications.**

| Effect | Detail |
|---|---|
| Retirement unblocked | H_T-CP-1 / 3 / 4 directly; cascades AS-8, OD-2 → CXA-5 (after OD-2 PARTIAL → RETIRE-READY follow-on) |
| §9 Class 2 surface | CLOSES at U-RT-NN landing + CP-1 retirement event |
| Phase 7 status | Sub-phase 7d completes (with bounded-residual for HITL / validator / sub-agent composers still carried per v2 §9.2.5) |
| Design-substrate revision | Runtime spec v1.1 → v1.2 (new contract); CP spec unchanged; no ADR revision |
| Architectural commitment | The runtime owns LLM dispatch as a Phase-7 deliverable, consistent with v1.1 substrate-bootstrap framing extended by one contract |
| Risk | Low — composer is well-bounded; pattern matches existing C-RT-05 lifecycle stage |

### §3.2 Option B — Phase-3 design effort (Phase-7-without-multi-LLM-at-runtime closure)

**Shape.** Acknowledge that the runtime is "done" at v1.4 per the substrate-bootstrap scope; LLM dispatch is a separate Phase-3 deliverable with its own design + plan + implementation cycle. Phase 7 closes with CP-1 / 3 / 4 carried as bounded-residual to Phase 3.

**Locus.** No design-substrate revision at Phase 7. Phase 3 opens later with its own scope, possibly with its own runtime-plan-revision pass.

**Effort.** Zero immediate code/spec work. Phase 3 scoping effort (substantial — likely multi-session) deferred.

**Implications.**

| Effect | Detail |
|---|---|
| Retirement unblocked | None at Phase 7. CP-1 / 3 / 4 + AS-8 + OD-2 + CXA-5 all stay bounded-residual carried to Phase 3 |
| §9 Class 2 surface | OPEN at Phase 7 close — ADR-F1 v1.2 multi-LLM commitment unmet at runtime through Phase 7 |
| Phase 7 status | Sub-phase 7d closes with explicit Phase-3-gated bounded-residual section (more than v2 §9.2.5 currently scopes; would be an admission rather than an unblock) |
| Design-substrate revision | None |
| Architectural commitment | The runtime is bounded to substrate-bootstrap; LLM dispatch is architecturally separate from Phase 7 |
| Risk | Medium-high — §9 surface remains the most-consequential unmet commitment indefinitely; project framing ("multi-LLM by design") becomes "multi-LLM-by-design but-not-by-Phase-7-runtime" |

### §3.3 Option C — Back-flow Class 1 spec extension

**Shape.** The runtime spec under-specifies its own LLM-dispatch surface (the spec has the providers but never specifies a composer that calls them). Route as Class 1 fork; revise `Spec_Harness_Runtime_v1.md` to add the LLM-dispatch contract before Phase 7 implementation proceeds (per X-AL-3: no silent H_T design extension).

**Locus.** Runtime spec v1.1 → v1.2 via back-flow Class 1; runtime plan revision pass; then runtime implementation.

**Effort.** Higher than A — formal back-flow includes adversarial review (P2-S4-CK second pass). Spec revision ~2-3 hours + review cycle. Plan revision pass. Then implementation similar to A.

**Implications.**

| Effect | Detail |
|---|---|
| Retirement unblocked | Same as A, but on a longer timeline due to back-flow discipline |
| §9 Class 2 surface | CLOSES at U-RT-NN landing + CP-1 retirement event, same as A |
| Phase 7 status | Sub-phase 7d HALTS until back-flow completes; spec revision absorbed; resumes |
| Design-substrate revision | Runtime spec v1.1 → v1.2 with formal change-note discipline; possibly ADR-F1 v1.2 amplification clause |
| Architectural commitment | The gap is treated as a design-time defect that required surfacing before implementation, not as an in-Phase-7 spec extension |
| Risk | Lowest spec-fidelity risk; highest schedule cost |

### §3.4 Comparison snapshot

| Dimension | Option A | Option B | Option C |
|---|---|---|---|
| Closes §9 Class 2 surface at Phase 7? | Yes | No | Yes |
| Direct retirement events unblocked | 5+ (CP-1/3/4 + cascade) | 0 | 5+ (after back-flow) |
| Design-substrate revision required | Runtime spec v1.2 (new contract) | None | Runtime spec v1.2 (back-flow) |
| Phase 7 close timeline | Days–week | Indefinite (Phase 3) | Week-plus (back-flow + impl) |
| Spec-fidelity risk | Low | Low (admits scope) | Lowest |
| Architectural-honesty risk | Low (extends existing substrate framing by one contract) | Medium-high (admits multi-LLM unmet at runtime through Phase 7) | Low (acknowledges design-time defect explicitly) |
| Project-commitment posture | Multi-LLM met at Phase 7 close | Multi-LLM unmet at Phase 7 close | Multi-LLM met at Phase 7 close, after explicit design correction |

---

## §4 Recommendation

**Option A** is the recommended path, on the following reading:

1. **The gap is a missing composer, not a missing primitive.** The provider abstraction, capability binding, routing manifest, and per-step binding resolution are all landed. The only thing missing is a composer that consumes resolved `binding` + step input and dispatches an LLM call. This fits the runtime spec's existing scope (substrate composers at each bootstrap stage) extended by one stage-or-step-level composer. It is not a new H_T primitive surfaced at execution time (which would invoke X-AL-3 and force Option C).

2. **Option B sacrifices the project's load-bearing commitment for schedule.** ADR-F1 v1.2 is the framing commitment. Closing Phase 7 with multi-LLM unmet at runtime would be a project-level admission, not a scope-discipline win.

3. **Option C is the right answer if the spec genuinely under-specifies.** §2.4 shows no design-substrate spec currently owns the contract — which is suggestive of design-time omission. But the runtime spec is at v1.1 and was authored in scope to the substrate-bootstrap loop by design (per the runtime-entrypoint design-gap closure 2026-05-16, which scoped runtime to bootstrap + lifecycle, deferring orchestration). The LLM-dispatch composer was not omitted; it was scoped out. Extending scope in v1.2 with a new contract is faithful to the substrate framing.

4. **Option A precedent in this workspace.** v1.4→v1.5 §25.9 propagated-emission row addition (per `[[fork-u-rt-49-cost-attribution-invocation-underspec]]`) extended CP spec with a new contract surface without invoking back-flow. Same shape: an in-Phase-7 spec extension under operator ratification when the addition is a faithful extension of existing scope, not a new H_T design surface.

5. **Acknowledged uncertainty.** If the operator reads the runtime spec's substrate-bootstrap scope as load-bearing (i.e., the spec deliberately excludes LLM dispatch because LLM dispatch belongs to a separate runtime authored at a different Phase), Option B is the architecturally honest answer. The operator owns that reading; this fork surfaces the question.

---

## §5 Resolution surface — questions for operator

### Q1 — Composer locus

Which option is selected?

| Choice | Effect |
|---|---|
| Q1a — Option A (in-Phase-7 runtime spec v1.2 + new U-RT-NN unit) | Recommended per §4 |
| Q1b — Option B (Phase-3 deferred; close 7d with explicit Phase-3-gated CP-1/3/4 residual) | If runtime spec scope is load-bearing |
| Q1c — Option C (Class 1 back-flow; runtime spec v1.2 via back-flow discipline) | If the gap reads as design-time defect |

### Q2 (only if Q1 = Q1a) — Composer surface shape

The new C-RT-15 contract specifies what?

| Choice | Effect |
|---|---|
| Q2a — Per-step composer invoked by `StepDispatcher.dispatch(binding, step)` | Smallest scope; matches `workflow_driver.py:379` seam; composer consumes resolved binding + step input, returns step output |
| Q2b — Per-step composer + fallback-chain wrapper (unblocks CP-4 in same arc) | Larger scope; H_T-CP-4 retirement criterion B met in the same landing |
| Q2c — Per-step composer + fallback + retry/breaker wrapper (unblocks CP-3 + CP-4 in same arc) | Largest scope; H_T-CP-3 + CP-4 retirement criterion B met; matches the `retry_breaker.py` LOOP_INIT orchestrator (U-RT-43+) framing referenced at v2 §5 CP-3 row |

### Q3 (only if Q1 = Q1a) — Telemetry binding

GenAI semconv 1.41.0 binding for OD-2 PARTIAL → RETIRE-READY upgrade in the same arc?

| Choice | Effect |
|---|---|
| Q3a — Bind GenAI semconv at the new composer (in-arc OD-2 upgrade) | OD-2 retires with the composer; cascades CXA-5 (after CP-1 retires) |
| Q3b — Defer GenAI semconv binding to a separate OD-2-targeted arc | Smaller composer scope; OD-2 stays PARTIAL after this arc |

### Q4 — Authorization scope of this fork

| Choice | Effect |
|---|---|
| Q4a — Resolve in this session (file → ratify → resolve same-day, per fork-u-rt-49 / fork-u-cp-56 precedent) | High momentum; risk of operator rushing on a load-bearing scope decision |
| Q4b — File now; resolve in a future session after operator-considered review | Lower velocity; better deliberation for a load-bearing decision |

---

## §6 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/fork_llm_dispatch_composer_scope.md` |
| Authored at | Phase 7 sub-phase 7d, 2026-05-20 |
| Authoring authority | v2 retirement ledger §9.2.3 + checkpoint `20260520-074654` §Remaining Work item 3 (operator-acknowledged open scope question) |
| Predecessor | `.harness/phase-7d-retirement-ledger-v2.md` §5 CP-1 row + §8.3 §9 Class 2 disposition |
| Successor consumption | Operator ratification of Q1 (+ Q2/Q3 if Q1a); if Q1a → runtime spec v1.1 → v1.2 amendment + new U-RT-NN unit + implementation; if Q1b → 7d closure ledger amendment to mark CP-1/3/4 + cascades as Phase-3-gated; if Q1c → Class 1 back-flow routing |
| Pattern | fork-record-as-design-doc + Q&A ratification + multi-step arc, same as `[[fork-u-rt-49-cost-attribution-invocation-underspec]]` (closed same-day) |
| Status | OPEN — awaiting operator ratification of Q1 (+ Q2/Q3 conditional + Q4 timing) |

---

*End of LLM-dispatch composer scope fork.*
