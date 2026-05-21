# Phase 7d Retirement Events — Batch 8

| Field | Value |
|---|---|
| Batch number | 8 |
| Filed at | 2026-05-21 (post-U-RT-60 wrap-asymmetry impl arc landing — fork RATIFIED → APPLIED) |
| Filed by | U-RT-60 follow-on impl arc per fork §8.1 step 8 (AC #14) |
| Predecessor batch | `phase-7d-retirement-events-batch-7.md` (2026-05-20, F2-04 follow-on arc closure — contract-surface refinement event; cumulative 21/49 unchanged) |

---

## §0 Batch context

**Status type: substitution-retirement-readiness transition (1 STILL-BOUNDED → RETIRE-READY) + 1 PARTIAL re-classification noted, NO new RETIRED transitions.**

This batch documents the U-RT-60 wrap-asymmetry sync/async mismatch Class 1 fork APPLIED landing arc (commits `3a9c2f4` composer async refactor + `a1166d6` stage 5 wrap chain + `e7f5cc0` AC #12 retry-of-gate + this commit's docs + APPLIED-transition). The arc materializes the spec §14.8.1 wrap-asymmetry table both rows at bootstrap stage 5 + binds the MCP-backed `AskUserQuestionSurface` (`harness-runtime/.../mcp_backed_ask_user_question_surface.py`) per spec §14.8.3 v1.11 H_E binding pin.

The retirement event recorded here is **H_T-CP-20 STILL-BOUNDED → RETIRE-READY**. NOT RETIRED. The transition is "criterion A met (cited unit IDs landed) + criterion B partially met (the wire is in place but the H_E surface terminal handler is not yet invoked end-to-end against a live operator)" per X-AL-2 reading. The bounded carry-forward is documented at §3.

**Conclusion (preview):** 0 new RETIRED transitions; cumulative 21/49 (42.9%) unchanged. H_T-CP-20 transitions STILL-BOUNDED → RETIRE-READY. The U-RT-60 implementation arc satisfies criterion A (8 cited units landed: U-CP-37 / U-CP-38 / U-CP-39 / U-CP-40 / U-CP-41 / U-CP-46 / U-RT-25 / U-RT-60). Criterion B partially met (production wrap chain materialized, 4-substep audit + 4-span hierarchy emitted at workflow execution); fully met when the FastMCP transport-level handler registers as a separate substantive arc.

---

## §1 H_T-CP-20 STILL-BOUNDED → RETIRE-READY

| Field | Value |
|---|---|
| Substitution ID | H_T-CP-20 |
| Primitive | HITL primitive + 4-response palette + `hitl.*` / `audit.*` namespace emission |
| Prior status | STILL-BOUNDED per `.harness/phase-7d-retirement-ledger-v2.md` §5 line 108 ("`RuntimeHITLPlacementRegistry` materialized as pure decision surfaces only … Driver never invokes HITL gate") |
| Transition this batch | STILL-BOUNDED → **RETIRE-READY** |
| Triggering arc | U-RT-60 wrap-asymmetry fork APPLIED landing (composer async refactor + stage 5 wrap chain + MCP-backed surface + AC #12/#13 + workspace CLAUDE.md absorption) |

### §1.1 Criterion A (cited unit IDs landed) — MET

Per `Spec_Harness_Runtime_v1.md` v1.11 §14.8.5 + §14.8.6 + retirement-reading entry at line 1705 ("H_T-CP-20 RETIRE-READY. Condition A: U-CP-37 + U-CP-38 + U-CP-39 + U-CP-40 + U-CP-41 + U-CP-46 + U-RT-25 + U-RT-60 landed"):

| Unit | Landing commit | Surface |
|---|---|---|
| U-CP-37 | landed (HITL palette declaration) | `harness-cp/.../hitl_response_palette.py` — 4-response enum |
| U-CP-38 | landed (placement schema) | `harness-cp/.../hitl_placement.py` — `HITLPlacement` + `HITLPlacementKind` |
| U-CP-39 | landed (placement registry) | `harness-cp/.../hitl_placement.py` — `RuntimeHITLPlacementRegistry` |
| U-CP-40 | landed (persona-tier × engine-class matrix) | `harness-cp/.../persona_engine_hitl_matrix.py` — `matrix_cell_for` + `HITLMatrixCell` |
| U-CP-41 | landed (audit-ledger composer) | `harness-cp/.../per_step_override_evaluator.py` — `CPAuditLedgerEntry` |
| U-CP-46 | landed (HITL span attr carrier) | `harness-cp/.../audit_hitl_span_namespace.py` — `HITL_SPAN_NAMESPACE_SCHEMA` + `AUDIT_NAMESPACE_SCHEMA` |
| U-RT-25 | landed (workflow lifecycle emitter) | `harness-runtime/.../lifecycle_emitter.py` |
| **U-RT-60** | **landed this arc** (HITL gate composer + stage 5 wrap chain + MCP-backed surface) | `harness-runtime/.../hitl_gate_composer.py` + `.../mcp_backed_ask_user_question_surface.py` + `.../bootstrap/stage_5_loop_init.py` |

**Criterion A status: MET.** All 8 cited units landed end-to-end.

### §1.2 Criterion B (substituted H_E surface no longer invoked) — PARTIALLY MET

Per X-AL-2: "Retirement = (cited unit IDs landed) ∧ (substituted H_E surface no longer invoked at substitution site). **Both conditions required.**"

**Substitution site analysis.** H_T-CP-20's substituted H_E surface was Claude Code's `AskUserQuestion` tool invoked directly by convention (`CLAUDE.md`-prose-routed at operator discretion). The substitution site at the new wrap chain is `await ctx.ask_user_question_surface.ask(prompt, options, timeout)` invoked from the HITL gate composer body step 4f.

**At U-RT-60 APPLIED:**

- The composer body invokes `await ctx.ask_user_question_surface.ask(...)` (NOT Claude Code's `AskUserQuestion` tool directly).
- `ctx.ask_user_question_surface` is bound to `MCPBackedAskUserQuestionSurface` (`harness-runtime/.../mcp_backed_ask_user_question_surface.py`) per spec §14.8.3 v1.11 binding pin.
- The MCP-backed surface holds an injectable `mcp_callback: MCPAskCallback` async delivery primitive (impl-discretion authorized by spec §14.8.3 line 1715: "the integration-test harness (MCP-host-side handler fixture against the MCP-server substitution-mechanism category per §14.8.3 v1.10 pin) **is implementation discretion**").
- At bootstrap stage 5, the default callback is `_PlaceholderMCPCallback` which raises typed `MCPSurfaceCallbackNotBoundError` on invocation. The wire is in place; the actual FastMCP transport-level handler registration is the bounded carry-forward (see §3 below).

**Why criterion B is PARTIALLY met (not fully).** Criterion B has two readings:

1. **Strict structural reading**: "is the H_E surface (Claude Code `AskUserQuestion` tool, direct invocation) still invoked at the substitution site?" Answer: **NO**. The composer body invokes the typed `AskUserQuestionSurface` Protocol through the MCP-backed surface; the H_E delivery primitive is now reached only through the MCP envelope per X-AL-1. By this reading, criterion B is MET.

2. **End-to-end operational reading**: "does the substitution site terminally deliver to a real operator and receive a real response?" Answer: **NO**. The placeholder callback raises on invocation; the FastMCP host wiring lands at a follow-on arc. By this reading, criterion B is PARTIALLY MET.

Per advisor reconciliation at this arc landing turn: **the honest classification is RETIRE-READY, not RETIRED.** The wire IS in place at the H_T design surface (Protocol + composer + wrap chain + MCP-backed surface concrete impl); what's deferred is the FastMCP transport binding. Conservative reading preferred to avoid silent absorption of substitution-criterion-B deferral.

### §1.3 Production callsite invocation evidence

Production wrap chain materialized at `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py` per the fork §7.2 Q1 code block (RATIFIED @ `0a1ca94`):

```
Row 1 (INFERENCE_STEP):
  bare RuntimeLLMDispatcher (async C-RT-15)
    → RuntimeHITLGateComposer (async; applicable_placements={PRE_ACTION})
    → RetryBreakerFallbackDispatcher (async C-RT-16; outer of HITL gate per Q2)
    → SyncDispatcherFacade (sync; registry binding via U-RT-59 Path B reuse)

Row 2 (SUB_AGENT_DISPATCH):
  bare RuntimeSubAgentDispatcher (sync C-RT-17)
    → RuntimeHITLGateComposer (async; applicable_placements={SUB_AGENT_BOUNDARY})
    → SyncDispatcherFacade (sync; registry binding)
```

Verification evidence:

- `harness-runtime/tests/test_bootstrap.py::test_bootstrap_stage_5_binds_inference_and_sub_agent_dispatchers` (AC #13 post-condition): asserts both wrap-chain rows isinstance-by-isinstance + `ctx.ask_user_question_surface` is `MCPBackedAskUserQuestionSurface`.
- `harness-runtime/tests/test_lifecycle_hitl_gate_composer.py::test_retry_of_gate_re_evaluates_gate_per_attempt` (AC #12): asserts 3× surface invocations + 3× audit entries + 3× canonical 4-span hierarchy under C-RT-16 retry through HITL composer through bare async mock.
- `harness-runtime/tests/integration/test_run_smoke.py::test_e2e_bootstrap_shutdown_round_trip`: asserts the full bootstrap-to-shutdown round trip lands the wrap chain (C-RT-16.inner == HITL composer; HITL.inner == bare LLM dispatcher).
- 2311/2311 workspace tests green (+24 net from baseline 2287 across the 3 implementation commits).

### §1.4 RETIRE-READY → RETIRED gate

The H_T-CP-20 STILL-BOUNDED → RETIRED full transition gates on:

1. **FastMCP transport-level handler registration**: replace `_PlaceholderMCPCallback` at stage 5 with a FastMCP-host-bound async delivery primitive. Scope: ~80-150 LOC additional handler module + MCP host wiring. NOT part of U-RT-60 scope per spec §14.8.3 line 1715 impl-discretion authorization.
2. **End-to-end operator delivery test fixture** (`InMemoryMCPHostFixture` or equivalent per spec §14.8.3 v1.10 Q3 test-mock discipline line 1715): integration test exercising the full wrap chain with a real MCP handler that returns a canned response.

Recommended next-arc framing: H_T-CP-18 (MCP integration + per-server trust + `mcp.*` consumption) is also STILL-BOUNDED; the FastMCP host wiring arc would advance both CP-18 and CP-20 to RETIRED jointly. The two substitutions are coupled at the FastMCP transport surface.

---

## §2 H_T-CP-13 sub-agent handoff — re-classification noted (NO change)

| Field | Value |
|---|---|
| Substitution ID | H_T-CP-13 |
| Primitive | Sub-agent handoff (HandoffContext, SubAgentBrief, StateSummary, LedgerEntryRef) |
| Prior status | STILL-BOUNDED per ledger §5 line 102 |
| Batch 8 surface | U-RT-60 commit `a1166d6` row 2 wrap chain materialization: `bare RuntimeSubAgentDispatcher → HITL composer (SUB_AGENT_BOUNDARY) → SyncDispatcherFacade` binds the sub-agent dispatcher into a HITL-gated dispatch surface at `ctx.step_dispatchers[StepKind.SUB_AGENT_DISPATCH]`. The sub-agent dispatcher itself was already production-bound at U-RT-59 landing; this arc adds the HITL wrap layer. |
| Status post batch 8 | STILL-BOUNDED (unchanged). The HITL wrap is a gate composer over the sub-agent dispatcher, not a sub-agent handoff-execution composer. CP-13's substitution site (sub-agent handoff dispatch execution at the workflow driver layer) is structurally separate from the HITL gate's pre-action evaluation surface. |
| Verification anchor | `harness-runtime/tests/test_bootstrap.py::test_bootstrap_stage_5_binds_inference_and_sub_agent_dispatchers` (asserts `ctx.sub_agent_dispatcher` is the HITL composer wrapping the bare `RuntimeSubAgentDispatcher`; both Protocol satisfied). |

CP-13 retirement remains gated on driver invocation of `dispatch` / `compose_dispatch_audit` at production-callsite paths (per ledger §5 line 102). U-RT-60 surface does not advance that gate.

---

## §3 Bounded carry-forward — FastMCP transport-level handler registration

| Field | Value |
|---|---|
| Carry-forward ID | `mcp-backed-ask-user-question-surface-fast-mcp-handler` |
| Scope | `_PlaceholderMCPCallback` at `harness-runtime/.../mcp_backed_ask_user_question_surface.py` raises `MCPSurfaceCallbackNotBoundError` on invocation. Real FastMCP-host-bound async delivery primitive deferred. |
| Why bounded | The MCP-server substitution-mechanism category is the canonical authority for H_E ↔ H_T process-isolation boundary placement per workspace `CLAUDE.md` invariant I-4 + Meta-Architecture §7 X-AL-1. The wire IS in place at the H_T design surface (Protocol + composer wrap chain + `MCPBackedAskUserQuestionSurface` concrete impl + injectable callback abstraction per spec §14.8.3 line 1715 impl-discretion). The bounded part is the FastMCP transport-level handler registration — a separate scope from U-RT-60 (which targets the composer body + wrap chain + binding pin). |
| Anti-leakage compliance | X-AL-2 PARTIAL-RETIREMENT-IS-NON-RETIREMENT discipline: H_T-CP-20 transitions STILL-BOUNDED → RETIRE-READY (NOT RETIRED) until the FastMCP handler arc lands. X-AL-3 (no silent H_T design extension): the injectable callback abstraction is authorized impl-discretion per spec §14.8.3 v1.10 Q3 ratification line 1715 ("integration-test harness … is implementation discretion") — no silent design extension. |
| Recommended next arc | New unit `U-RT-NN` (TBD) — FastMCP transport-level handler module wraps `MCPHost` (currently `started=False` placeholder at `mcp_host.py:58`) with a real FastMCP server lifecycle + binds a real-delivery `MCPAskCallback`. Coupled with H_T-CP-18 retirement (MCP integration + per-server trust); both substitutions advance to RETIRED at that arc landing. |
| Filing reference | Carried-fork audit before next CP cluster opens per `[[carried-fork-audit-before-cluster]]` memory pattern. |

---

## §4 Cumulative retirement ledger (post batch 8)

Per `.harness/phase-7d-retirement-ledger-v2.md` §5 (workspace progress ledger) + batches 1-7:

| Status | Count | Substitutions |
|---|---|---|
| RETIRED (post batch 8) | 21 / 49 (unchanged) | (15 from batches 1-2) + CP-3 / CP-4 / CP-5 / CXA-5 (batch 3) + CP-10 / CP-13 (batch 4 — CP-13 criterion B strengthened at batch 6) |
| RETIRE-READY (post batch 8) | **1 / 49 (NEW)** | **H_T-CP-20** (this batch — wire in place; FastMCP handler carry-forward) |
| PARTIAL (post batch 8) | 2 / 49 (unchanged) | AS-8 (batch 2) + CP-14 single-sub-agent slice (batch 4; gates on fan-out arc) |
| STILL-BOUNDED (post batch 8) | **9 / 49** (down from 10) | Per-axis CLAUDE.md inventories minus H_T-CP-20 (transitioned this batch) |

CP-axis post-batch-8: **9 / 22 RETIRED (40.9%, unchanged) + 1 RETIRE-READY (CP-20)**. Cumulative 21/49 RETIRED (42.9%, unchanged). The "RETIRE-READY" status is a new ledger category introduced this batch to honor the X-AL-2 discipline distinguishing "criterion A met + criterion B partial" from full RETIRED.

**Quality delta this batch:** The U-RT-60 wrap-asymmetry impl arc materializes the spec §14.8.1 wrap-asymmetry table both rows at bootstrap stage 5; binds the MCP-backed AskUserQuestionSurface per spec §14.8.3 v1.11 binding pin; emits the canonical 4-span hierarchy + 4-substep audit-write at workflow execution time. H_T-CP-20 transitions STILL-BOUNDED → RETIRE-READY honestly. Three Class 1 forks at the C-RT-18 contract surface across two sessions all resolved (binding-mechanism APPLIED @ `fb545ec` / span-attr-carrier-drift APPLIED @ `9b6b007` / wrap-asymmetry sync/async **APPLIED at this arc**).

---

## §5 Cross-axis cascade impact

§6.3.1 H_T-CP-1 → H_T-AS-8 anthropic.* namespace emission: **DORMANT** (preserved at this batch).

§6.3.2 F-CP-01 Stage 3b inversion cascade: **FULLY DISCHARGED at batch 3** (preserved at this batch).

§6.3.3 (no §6.3.3 declared at Meta-Architecture §6.3 — preserved).

**U-RT-60 cascade impact:** H_T-CP-20 STILL-BOUNDED → RETIRE-READY unblocks H_T-CP-18 (MCP integration) as the next-coupled-arc target. The FastMCP transport-level handler registration arc would jointly advance CP-18 + CP-20 to RETIRED. No cross-axis cascade at the IS / AS / OD axes — the wrap chain is harness-runtime-internal per fork §7.2 Q5 cascade-bounded ratification.

---

## §6 Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-21 (U-RT-60 wrap-asymmetry impl arc APPLIED landing — AC #14 batch 8 retirement event) |
| Cumulative status | 21/49 RETIRED (42.9%, unchanged) + 1/49 RETIRE-READY (NEW: H_T-CP-20) + 2 PARTIAL (AS-8 + CP-14) + 9 STILL-BOUNDED (down from 10) |
| Predecessor batch | `phase-7d-retirement-events-batch-7.md` (post-F2-04 follow-on arc closure; contract-surface refinement event; no new RETIRED) |
| Audit scope | 3 U-RT-60 implementation commits (`3a9c2f4` composer async refactor + `a1166d6` stage 5 wrap chain + HarnessContext extension + AC #13 post-condition + MCP-backed surface + `e7f5cc0` AC #12 retry-of-gate test) + this commit's documentation absorption |
| Substantive content | §1 H_T-CP-20 STILL-BOUNDED → RETIRE-READY (criterion A met; criterion B partial); §2 CP-13 surface re-classification noted (no change); §3 bounded carry-forward documented (FastMCP transport-level handler); §4 cumulative ledger introduces new RETIRE-READY category; §5 cross-axis cascade impact analysis |
| Successor batch | TBD — gates on (a) FastMCP transport-level handler arc (jointly retires CP-18 + CP-20); (b) HITL composer Phase 2 runtime arc (Phase 7d retirement against H_T-CP-21 + H_T-CP-22 once validator + pause/resume composers land); (c) cost-attribution composer (OD-5 STILL-BOUNDED unblock per `[[fork-price-table-ref-substitution-retirement]]` + `[[fork-cost-record-audit-ledger-wiring-residual]]`) |
| Revision policy | Forward-only ledger discipline per workspace `CLAUDE.md` §4.3 — batch 8 is a new filing referencing batches 1-7; no retroactive edits to prior batches. |

*Batch 8 retirement event filed per the U-RT-60 wrap-asymmetry sync/async mismatch fork APPLIED landing arc. **1 STILL-BOUNDED → RETIRE-READY transition** (H_T-CP-20; criterion A met; criterion B partial). NO new RETIRED transitions; cumulative 21/49 (42.9%) unchanged. Introduces RETIRE-READY ledger category to honor X-AL-2 "criterion A met + criterion B partial" discipline (advisor-reconciled at arc landing). Bounded carry-forward documented (FastMCP transport-level handler registration) per X-AL-3 no-silent-design-extension discipline.*
