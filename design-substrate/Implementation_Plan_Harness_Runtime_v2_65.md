# Implementation Plan: Harness Runtime — v2.65 (delta over v2.64)

**Status:** Cleared for source consumption by `.harness/clearance/implementation-plan-harness-runtime-v2-65-cleared-2026-10-04.md`, as the execution map for Runtime spec v1.134. Number stability follows the spec header: a renumber is not content-neutral and must update the source citations listed in `.harness/a3_runtime_fence_fold_authority.md`. Independent source/spec GO and criteria 1-5 evidence are pinned in `.harness/a3_runtime_fence_fold_authority.md`; formal shipping review and installed acceptance remain separate. Existing unit bodies are unchanged. Main `c995ec9f9fa5945a40ffe30734b859bb6e88e2a8` carries this plan but none of U-RT-157's source. The committed candidate `a06c0abd8d09a78b1fc63ff2b9c2c98b79dcba5d` (branch `ship/a3-source09-20261004`) implements it and is not on main. Criteria 1-5 hold for the hash-bound provider-free source evidence; landing and installed acceptance are not claimed.

## §0.1 U-RT-157 — Ollama C-RT-38 tool loop and shared post-effect fence

- **Authority:** Runtime spec v1.134 (C-RT-38 §14.27 amendments); fork record `.harness/class_1_fork_a3_ollama_mcp_loop_and_post_effect_retry.md`.
- **Cluster:** Runtime LLM dispatch and retry.
- **Dependencies:** the existing C-RT-38 loop, auditor and factory wiring (v1.131), the frozen tool superset (U-1), C-RT-16.
- No CXA row or cross-axis edge. The only CP-axis change is one row in CP's B-126 `retry.*` wire register (below); no CP spec, plan or contract changes.

**Source:**
- `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py`:
  - the Ollama branch selects the C-RT-38 arm when a superset and the loop are bound;
  - superset projection, non-memory offer membership before C-RT-38 assessment or effects, nonce identity, call-order turn, malformed-call refusal and the tools-unsupported retry; membership derives from the final wire offer after memory injection/collision filtering, never from `step.tools` or registry presence alone [LAW:single-enforcer];
  - a provider-neutral result text;
  - each `dispatch` attempt owns one `ToolEffectFence`, passed explicitly to the tool-loop arms; it guards the whole attempt, including turn capture;
  - provider calls, and the parsing of each provider's own reply, are marked with the `provider` origin; memory validation and every effect stay outside that boundary.
- `harness-runtime/src/harness_runtime/lifecycle/hitl_tool_loop.py`: the dispatcher entry and later batch failures are fenced.
- `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py`: the carrier is never retried or advanced. A `provider`-origin carrier is charged through the existing §14.6.3 waiver and charge path (closed: once unless waived; half-open: §14.6.4 cell 10, charging as cell 2 or 5 or re-arming when waived). A `non-provider` carrier is never charged, and its half-open trial is re-armed with the carrier preserved.
- `harness-runtime/src/harness_runtime/lifecycle/post_tool_effect.py` (new): `PostToolEffectError` (with `fault` and `origin`), `ToolEffectFailureOrigin` and `ToolEffectFence`. HITL terminal errors retain their identity before effects; after effects they become non-provider carriers under cell 10, preserving `fault` and `__cause__`.
- `harness-cp/src/harness_cp/retry_fallback_namespace.py`: one `RETRY_WIRE_REGISTER` row for the wrapper's `retry.post_tool_effect.origin`, declared by spec v1.134 line 57. `harness-cp/cp_tests/test_b126_retry_wire_register.py` moves its pinned counts with that row (emitted keys 10 → 11). Without the row, that drift test fails.

**Acceptance criteria:**
1. `harness-runtime/tests/test_post_tool_effect_replay.py`, through the real retry wrapper, dispatcher and loop: Anthropic and Ollama post-effect 5xx, plus an ambiguous dispatcher raise, give one effect, one attempt and the carrier. A pre-effect 5xx retries on both providers.
   The correction adds:
   - capture failure after an effect (Anthropic and Ollama): one effect, one capture, one attempt;
   - closed and half-open provider-origin charging;
   - a non-provider tool error that looks like HTTP: never charged;
   - a served Ollama memory write then 529, through a real `StandardMemoryToolExecutor` `memory.write_note`: one persisted note, one memory execution, one attempt, the provider fault charged (closed and half-open);
   - the signing-exclusion control;
   - the same malformed provider reply before and after an effect, on both providers, closed and half-open: one effect, one attempt, charged both times (§14.6.3 row 2b, §14.6.4 cell 2);
   - a memory-executor failure that looks like HTTP after an effect: non-provider, never charged;
   - cancellation and a tripped dispatch fence after an effect: identity kept, never charged.
   - the same terminal HITL error before and after an AUTO effect (both providers, closed and half-open), through the real wrapper, dispatcher and loop: original identity and `RT-FAIL-*` before (cell 7), non-provider `PostToolEffectError` with the exact original `fault`/`__cause__` after (cell 10). One attempt, no candidate advance, zero effects before and one after; no charge in either case. Both half-open cases re-arm to `open` with a fresh cooldown, unchanged `fail_count` and `trigger_count = 0`; assert the CP-recorded exception identity as well as breaker state.
   - a waived provider-origin fault after an effect (§14.6.4 cell 10, waived row): in `closed`, nothing recorded; in a half-open trial, re-armed to `open` with a fresh cooldown, `fail_count` unchanged and `trigger_count = 0`;
   - a failing transition emitter on a cell 10 re-arm (waived provider and non-provider): the emitter error is attached to the carrier as a note, and the carrier, not the emitter error, propagates.
2. `harness-runtime/tests/test_ollama_mcp_tool_loop.py`:
   - projection, child superset and empty `[]`;
   - a hallucinated registered tool absent from the final offer, including an empty descended child superset and an entry dropped for lacking `input_schema`: refused text, `policy_override` and `ollama.tool_call.refused`, with zero assessment, rewrite, prompt, response-audit and dispatcher calls. A positive control offers a registered tool through the effective descended superset while omitting it from `step.tools`: it reaches assessment and APPROVE dispatches once. A mixed selected-memory/omitted-MCP batch preserves memory execution, collision filtering and call-order replies while refusing the omitted MCP call;
   - APPROVE audited and dispatched once;
   - REJECT, RESPOND, DENY-REJECT, DENY-RESPOND and evaluator failure with no dispatch;
   - EDIT with an object and with `{}`;
   - a mixed memory and MCP batch answered in call order;
   - distinct ids and nonces;
   - unchanged refusal without a loop or superset;
   - tools-unsupported retry, and a mid-loop rejection that raises;
   - the bound;
   - summed usage;
   - malformed calls refused.
3. The existing dispatch, refusal, loop, factory, retry and C-RT-36/38 suites still pass. The only fixture change gives the fake loop results the real `dispatched` field; the B-126 register test's pinned counts move with the new register row.
4. Mutation probes: each of these turns a named test red.
   - removing the wrapper's carrier arm;
   - disabling the fence;
   - a stable nonce;
   - sending `payload.tools`;
   - removing non-memory offer membership, or replacing it with registry membership (the registered-but-unoffered and empty-offer witnesses fail); checking `step.tools` instead of the effective offer fails the positive control;
   - a fallback that keeps tools;
   - removing the attempt-wide guard (capture outside the fence);
   - skipping the provider-origin charge;
   - charging every origin;
   - marking provider calls as non-provider;
   - leaving provider-reply parsing outside the provider boundary;
   - widening the provider boundary over memory execution;
   - deleting the served-memory fence;
   - re-wrapping the signing family;
   - excluding terminal HITL errors from the post-effect fence (the after-effect carrier/fail-class witness fails), or wrapping them before effects (the pre-effect identity witness fails);
   - charging a waived provider-origin fault after an effect (removing the post-effect waiver skip);
   - releasing a cell 10 re-arm without the carrier in flight, so an emitter failure replaces the carrier.
5. Ruff check and format, plus pyright with the venv interpreter, are clean on the touched files.

Installed Ollama tool-calling and installed audit or signing are not claimed.

### §0.1a Execution portions

U-RT-157 is delivered as two source portions, in order. It is complete only when 157b is verified and criteria 1-5 hold together on the combined head. A head carrying only 157a implements U-RT-157 partially: the Ollama route there still refuses model tool calls as before.

- **157a — shared fence, retry wrapper and Anthropic arm.**
  - **Source:** `post_tool_effect.py`, `hitl_tool_loop.py` and `retry_breaker_fallback.py` in full, with the B-126 register row and its test counts. In `llm_dispatch.py`, the attempt-owned fence, its explicit threading, the attempt-wide guard, the Anthropic provider-call and reply-parsing boundary, and the fenced batch helper.
  - **Criteria:** the Anthropic and shared cases of criterion 1, criterion 3, and criterion 5.
  - **New controls:** written against the Anthropic arm. These are new tests for this portion, not existing reviewed test nodes:
    - criterion 1's non-provider cases (closed and half-open);
    - the cancellation and tripped-fence identity cases;
    - the before/after-effect terminal HITL identity and cell 7/cell 10 cases;
    - the waived provider-origin cases (closed and half-open);
    - the re-arm emitter-failure cases;
    - the registered re-prompt residual (spec v1.134 Scope limits): a REJECT or RESPOND answer followed by a transient continuation failure, through the real wrapper, dispatcher and loop, gives zero effects, no `PostToolEffectError`, one retry and, when the re-asked reply repeats the gated call, one further prompt with a new rewrite record under that reply's call id. This pins the residual as accepted behavior; it does not ask the fence to change.
  - **Mutation probes (criterion 4):** carrier arm, fence disabled, attempt-wide guard, skipped provider charge, charging every origin, provider marked non-provider, signing re-wrap, post-effect HITL exclusion or pre-effect HITL wrapping, the Anthropic half of reply parsing outside the provider boundary, the removed post-effect waiver skip, and the dropped in-flight carrier on re-arm.
- **157b — Ollama route.**
  - **Source:** the remaining `llm_dispatch.py` changes: route selection, projection and non-memory offer membership, nonce identity, turn, malformed-call refusal, tools-unsupported retry and the provider-neutral result text.
  - **Criteria:** criterion 2 and the Ollama cases of criterion 1, including the served memory write followed by a 529.
  - **Mutation probes (criterion 4):** stable nonce, sending `payload.tools`, removed offer membership or registry-only membership, membership taken from `step.tools`, a fallback that keeps tools, provider boundary widened over memory execution, deleted served-memory fence, and the Ollama half of reply parsing outside the provider boundary.

## §0.2 Review and completion boundary

- An independent out-of-family source and spec review checks:
  - the fence boundary: the attempt-owned effect state, the effect definition, the exclusions, the before/after-effect HITL carrier routing and the origin-based breaker accounting;
  - the Ollama offer boundary: registered-but-unoffered calls are refused, including an empty descended offer, while membership derives from the effective offer rather than `step.tools`; selected memory injection and collision handling are preserved;
  - that the no-superset path is byte-identical;
  - the ordering of the memory-arm fallback.
- Clearance markers for spec v1.134 and this plan are filed only after that review is accepted.
- Full composite gates and PR CI run on the reviewed head.
