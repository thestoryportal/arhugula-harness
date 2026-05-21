# Phase A.0 — LLM-Dispatch Composer Fork Audit + Closure Record

**Filed:** 2026-05-21 (Remaining-Work Closure Arc, Phase A sub-arc A.0)
**Audit target:** `.harness/fork_llm_dispatch_composer_scope.md` (filed 2026-05-20)
**Audit mode:** Operator-ratified "Audit-and-reopen if downstream gaps remain" (defensive)
**Audit verdict:** **CLOSE-AS-RESOLVED.** Option A taken materially at U-RT-52 + U-RT-58. No residual-contract authoring owed.

---

## §1 Audit method

Source-grep audit of the U-RT-52 → U-RT-58 wrapper chain + retirement-table cross-check:

1. **Wrapper chain wiring** verified at `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py:76-116` — stage 5 instantiates bare `RuntimeLLMDispatcher` (U-RT-52, C-RT-15), then *rebinds* `ctx.llm_dispatcher` to `RetryBreakerFallbackDispatcher` (U-RT-58, C-RT-16 §14.6 D6) wrapping the bare dispatcher; rebind raises if the retry/breaker registry or fallback chain are unpopulated.
2. **Step-dispatcher table** verified at `harness-runtime/src/harness_runtime/lifecycle/step_dispatchers.py:15` — `INFERENCE_STEP → ctx.llm_dispatcher` (the U-RT-58 wrapper); driver invocation at `harness-cp/src/harness_cp/workflow_driver.py:379` resolves via this table.
3. **Production LLM call sites** verified at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:415, 445` — `client.messages.create` / equivalent provider SDK invocations land for the multi-provider routing path.
4. **`retry.*` 6-attribute namespace emission** verified at `retry_breaker_fallback.py:386-496` — `retry.attempt_number`, `retry.original_span_id`, `retry.delay_ms`, `retry.cause_attribution`, `retry.fail_class` all set on per-attempt inner span; outer-span emits `retry.skipped` on OPEN-cooldown-unexpired path.
5. **`fallback.*` namespace emission** verified at `retry_breaker_fallback.py:262, 32` — `fallback.chain_length` on outer span; `fallback.exhausted` event on FallbackChainExhaustedError.
6. **`harness.breaker.*` namespace emission** verified at `retry_breaker_fallback.py:518` — delegates to `RuntimeRetryBreaker.emit_breaker_transition_event` per OD-canonical C-OD-07 §7.1 7-attribute schema.
7. **Idempotency-key propagation** verified at `cost_attribution.py:213-228` + `audit_writer.py:17` + per-step callsites at `sub_agent_dispatch.py:302, 334, 476, 483` + `hitl_gate_composer.py:304, 347, 570, 577`.

---

## §2 Retirement-table cross-check (canonical at `harness-cp/CLAUDE.md` §4.1)

CP-axis retirement status post-batch-5 (2026-05-20):

| CP primitive | Status | Production callsite |
|---|---|---|
| H_T-CP-1 (multi-LLM routing core) | **RETIRED** batch 2 | `llm_dispatch.py:RuntimeLLMDispatcher.dispatch` |
| H_T-CP-2 (layered routing strategy) | **RETIRED** batch 2 | Runtime invocation site present at production path |
| H_T-CP-3 (`retry.*` namespace + per-layer time-budget + dual-emission) | **RETIRED** batch 3 | `retry_breaker_fallback.py:_run_per_candidate_attempts` per-attempt span |
| H_T-CP-4 (fallback chain composition + cross-family) | **RETIRED** batch 3 | `retry_breaker_fallback.py:_advance_or_exhaust` candidate loop + `fallback.exhausted` event |
| H_T-CP-5 (routing-attribute namespace inheritance + per-class sampling) | **RETIRED** batch 3 | Three-level OTel span hierarchy preservation |
| H_T-CP-6 (workflow manifest schema) | **RETIRED** batch 1 | `routing_manifest.py:143-145` + `workflow_driver.py:360-364` per-step invocation |

**§9 Class 2 multi-LLM commitment surface CLOSED** per CP CLAUDE.md §4.1 (U-RT-52 close arc). ADR-F1 v1.2 multi-LLM-by-design commitment met at design + library + runtime.

---

## §3 Downstream-blocked verification (defensive scope)

The defensive audit checked whether ANY remaining STILL-BOUNDED or PARTIAL CP-axis substitution is blocked on LLM-dispatch downstream contracts. Per CP CLAUDE.md §4.1:

| CP primitive | Status | Blocker (verified non-LLM-dispatch) |
|---|---|---|
| H_T-CP-8 | PARTIAL | `cp_is_wiring.py` 1/17 spec edges; blocked on CP-IS wiring composer (separate fork) |
| H_T-CP-9 | PARTIAL | Binary RESUMPTION emit; blocked on ResumptionKind 5-class emission arc |
| H_T-CP-11 | PARTIAL | D4 multiplicative tunable not surfaced at runtime; blocked on engine-class-validation arc |
| H_T-CP-12 | STILL-BOUNDED | Sandbox-tier dispatch; blocked on sub-agent dispatch composer (already wired post-U-RT-59 single-slice) |
| H_T-CP-14 | PARTIAL | Single-sub-agent slice landed; blocked on parent-topology-expansion arc (fan-out) |
| H_T-CP-16 | STILL-BOUNDED | Memory primitives; blocked on memory-invocation composer |
| H_T-CP-17 | STILL-BOUNDED | Files primitives; blocked on files-invocation composer |
| H_T-CP-18 | STILL-BOUNDED | MCP per-server trust; blocked on per-server-trust evaluator + `mcp.*` namespace at H_T-as-MCP-client (Phase A.2 in-scope) |
| H_T-CP-19 | STILL-BOUNDED | Cross-deployment monotonicity; blocked on multi-deployment runtime path |
| H_T-CP-20 | RETIRED batch 9 | HITL gate composer landed at U-RT-60 (FastMCP server arc at U-RT-62) |
| H_T-CP-21 | STILL-BOUNDED | Validator framework; blocked on validator-composer arc (Phase A.2 in-scope) |
| H_T-CP-22 | STILL-BOUNDED | Pause/resume protocol; blocked on typed pause/resume composer |
| H_T-CP-23 | STILL-BOUNDED | Bridging-arc traversal; blocked on multi-topology cascade composer |

**Zero CP primitives remain blocked on LLM-dispatch downstream contracts.** The wrapper chain (retry + breaker + fallback + idempotency) is end-to-end at production execution; all retry/fallback/breaker spans emit per OD-canonical schemas.

---

## §4 Closure ratification

**Operator-ratified C.2 verdict (this audit):** CLOSE-AS-RESOLVED. The fork record at `.harness/fork_llm_dispatch_composer_scope.md` is hereby closed with Option A (Phase-7 deferred runtime unit) explicitly ratified-as-taken. Citations:

- `Spec_Harness_Runtime_v1.md` v1.3 §14.5 C-RT-15 (U-RT-52 LLM-dispatch composer contract)
- `Spec_Harness_Runtime_v1.md` v1.5 §14.6 C-RT-16 (U-RT-58 retry/breaker/fallback wrapper contract)
- `.harness/phase-7d-retirement-events-batch-2.md` (CP-1/CP-2 retirement events)
- `.harness/phase-7d-retirement-events-batch-3.md` (CP-3/CP-4/CP-5 retirement events)
- `harness-cp/CLAUDE.md` §4.1 retirement table + §9 Class 2 closure note

**Phase A.2 implication:** NO LLM-dispatch downstream-residual contract authoring needed. Phase A.2 scope reduced to: (1) tool-invocation runtime composer per Path X; (2) HITL delivery + timeout-degradation + validator framework; (3) per-server-trust evaluator + `mcp.*` namespace.

---

## §5 Fork record formal close instruction

The original fork record `.harness/fork_llm_dispatch_composer_scope.md` carries no closure footer at HEAD. Phase A.2 spec-writer pass will append the closure addendum citing this audit + the U-RT-52/58 landing artifacts, completing the fork lifecycle per `Project_Workflow_v1_8.md` §2.7.6 Class 2 routing.

---

## §6 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/Phase_A_0_LLM_Dispatch_Fork_Audit_v1.md` |
| Audit at | Phase A sub-arc A.0, Remaining-Work Closure Arc, 2026-05-21 |
| Audit authority | Plan file `/Users/robertrhu/.claude/plans/begin-comprehensive-and-sharded-bird.md` Phase A.0 + operator ratification of Class 2 C.2 = "Audit-and-reopen if downstream gaps remain" |
| Verdict | CLOSE-AS-RESOLVED — Option A taken at U-RT-52 + U-RT-58 |
| Downstream impact | Phase A.2 scope reduced; no LLM-dispatch residual authoring |
| Next sub-arc | Phase A.1 (Class 1 tension resolution: Pattern-D 13-type cluster + CP unit sequencing) |
