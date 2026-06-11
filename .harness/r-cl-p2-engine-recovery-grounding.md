# R-CL-P2 (engine-recovery activation) — entry grounding → DEFER disposition

**Date:** 2026-06-10 · **Posture:** Phase-7 grounding (read-only; no `harness-*/src` edits) → roadmap/process-substrate recording (mode-agnostic).
**Authority chain:** closure-plan `.harness/post-mvp-full-closure-plan-v1.md` §P2; brief `.harness/r-cxa-2-post-mvp-producer-loop-product-brief.md` §3; impl-plan `.harness/r-cxa-2-implementation-plan.md` Slice 2; forward-register `.harness/post-phase-8-forward-register.md` line 181.

This note records the §1 ground-first finding at R-CL-P2 entry (per the per-phase template §6 "Entry"). It is **not** a re-decision of any ratified disposition — it *confirms* them and closes the "is P2 buildable?" question so the next session does not re-litigate it.

## Headline

**P2 is substantially DEFER.** Grounding each work item against HEAD shows the buildable, non-hollow Phase-7 slice is empty. The engine-recovery driver is a *ratified* bounded-residual (not an open build); the other pieces are speculative / hollow / design-gated. The dashboard's optimistic P2 framing ("bind #475 + sandbox wiring + SAVE_POINT") does not survive grounding.

## Per-item disposition

### 1. Engine-recovery driver (closure-plan §120) — **DEFER (confirming batch-55 bounded-residual)**

`RuntimeEngineRecoveryLoop` (`harness-runtime/.../lifecycle/engine_recovery_loop.py`) is instantiated at the stage-5 producer factory (`bootstrap/factories/r_cxa_2_producer_loop_factory.py:208`) and exposed on the harness context, but has **no production caller** — `.capture_pause`/`.attempt_resume` are invoked only by `test_r_cxa_2_producer_loop_factory.py:201,208`. The production pause/resume that *does* fire is the **workflow-layer** `PauseResumeProtocol` (`harness-cp/.../workflow_driver.py:571/796/952`), a distinct layer.

The forward-register line 181 ratifies this: **CXA-2 = RETIRED-AS-BOUNDED-RESIDUAL (batch-55)**, with the explicit instruction — *"Do not wire `workflow_driver.py` as a fake engine recovery loop; re-open only when a real event-sourced replay, reconciler-loop, WAL-segment, or engine-native-pause recovery loop lands."* The engines that would emit engine-layer pauses (Temporal/K8s/Kafka/LangGraph) are I-6-forbidden to vendor. So a "production driver" is **producer-discovery-empty by ratified disposition** — the 4th `[[r-cxa-seam-wiring-is-producer-discovery]]` DEFER. Building one = the fake-producer anti-pattern + X-AL-3.

**Do NOT bind the durable `JournalEnginePauseResumeSubstrate` (#475) into the factory in place of `Deterministic`.** Nothing in production calls `ctx.engine_recovery_loop`, so the substrate choice is invisible in every production path — the swap is cosmetic, and it would force resolving the journal-path placement against the **closed 4-class `PathClass` enum** (`harness-is/.../path_class_registry.py:31`; IS-AL-1 forecloses inventing one) for zero production benefit. The impl-plan's own sequencing is correct: journal-path placement is decided *with* the driver that consumes it, and there is no driver. (If the ratified 2026-06-10 `Deterministic`-binding is ever judged wrong, that is a Class-2 fork to surface — not a silent re-build.)

### 2. External-engine `SAVE_POINT_CHECKPOINT` reference adapter (closure-plan §121) — **DEFER (speculative)**

No adapter exists at HEAD. Building a reference adapter for an external engine class (LangGraph-pattern, non-vendored per I-6) is speculative: its only consumer is the engine-recovery loop, which is itself dormant (item 1) → zero consumers. Live-proof is deployment-gated per D-2. Defer with the engine-recovery half.

### 3. HITL model-driven tool-loop depth — OQ-5/6/7 (closure-plan §122) — **DEFER (hollow / thin-latent)**

PR #454 built the **happy path**: `_dispatch_anthropic_with_hitl_tool_loop` (`llm_dispatch.py:1105`) drives a multi-turn Anthropic tool-use continuation through `ctx.hitl_tool_loop.run_tool_calls` (`hitl_tool_loop.py:105`); tests cover emit-when-required, id-preservation, reject-skips-dispatch, and the continuation. OQ-5/6/7 (the *depth*) are unbuilt, and unbuildable as non-hollow Phase-7 slices today:
- **OQ-5 (cross-family fallback id-stability) + OQ-7 (mid-loop breaker + replay-from-journal):** `retry_breaker_fallback.py` / `retry_breaker.py` do **not** compose with `hitl_tool_loop` at all (no reference), and there is no per-tool-call turn journal. There is no production scenario where fallback/breaker fire *during* a journaled HITL tool turn → robustness for a composition that does not occur = hollow.
- **OQ-6 (HITL-gate timeout degradation):** the factory passes `timeout_seconds=None` (`r_cxa_2_producer_loop_factory.py:94`) and there is no config path to set it, so a timeout-degradation branch would never fire. Building it = build-the-capability-and-its-own-exerciser, same category as OQ-5/7. **Captured as a latent gap** (real-but-unconfigured robustness in the sync provider-turn HITL gate); a candidate for a Q-phase robustness item, not a P2 build.

## Roadmap-hygiene correction — unbundle the sandbox item

The **roadmap** entry `R-CL-P2` mis-bundled a fourth piece ("sandbox driver→dispatch wiring", item C-1) that the **authoritative closure-plan §P2 does not contain** (§P2 is engine-recovery + SAVE_POINT + HITL-depth only). It is **unbundled here** as an R-410-family finding:

**Production sandbox tier→driver selection is unwired (real security-posture gap, design-adjacent).** `RuntimeToolDispatcher.__init__` accepts `tool_execution_driver: ... | None = None` and defaults to `MCPHostToolExecutionDriver()` (in-process) at `runtime_tool_dispatcher.py:343`. The production factory `runtime_tool_dispatcher_factory.py:199` constructs the dispatcher with a `sandbox_decision_resolver` (tier *decision* only) and **never passes a driver**; **no tier/tech/provider→driver registry exists anywhere in `bootstrap/`**. So at HEAD every TOOL_STEP runs in-process regardless of a resolved `TIER_2/3/4` decision — sandbox-tier enforcement is real only under **test injection** (`[[test-bypass-as-runtime-truth-pattern]]`).

This is **not a P2 build and not a silent Phase-7 fix.** The fork `class_1_fork_sandbox_tier_no_execution_driver_contract.md` (APPLIED-AS-BOUNDED-READING-B) landed the driver impls + dispatcher-delegation seam (R-410/411/412) but frames the tier→mechanism contract as *"a NEW design contract … design-phase artifact, not a Phase-7 impl decision"*; runtime spec v1.41 §14.9.8 dangles the consumption as "future-arc." R-410/411/412 deliberately closed with **injected-driver** e2e per lane and did **not** wire factory auto-selection — a bounded closure, not an oversight. Wiring it requires inventing the selection contract (canonical tech/provider vocab, per-server driver config, constructor params) = design. The X-AL-1-clean move is the one the original R-410 fork already modeled: **surface/file the selection-contract question, don't build it.** Recorded as an R-410-family residual.

## Disposition + next action

- **R-CL-P2 → DEFERRED** (bounded-residual; the buildable Phase-7 slice is empty). Title corrected to drop the mis-bundled sandbox item.
- **Sandbox tier→driver production-selection gap** → unbundled R-410-family finding (design-adjacent; file-don't-build).
- **OQ-6 timeout degradation** → latent-gap capture (Q-phase robustness candidate).
- **NEXT = R-CL-P3** (persona-tier TEAM_BINDING breadth) — its roadmap note is BUILD-NOT-FORK (design done; owed = e2e proof). Triage at entry: the root `CLAUDE.md` §10.2 reconciliation is a design-substrate touch (clearance marker), and the "live multi-tier e2e" may carry an infra gate — ground both before committing.

*Grounded at HEAD `08004410`. Cites resolved by direct read this session.*
