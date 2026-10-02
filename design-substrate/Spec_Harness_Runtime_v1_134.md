# Specification — Harness Runtime v1.134 (delta over v1.133)

**Status:** Proposed. This is the bundled-absorption arc for A3, with fork record `.harness/class_1_fork_a3_ollama_mcp_loop_and_post_effect_retry.md`. Runtime v1.133 remains the cleared head until this delta is independently reviewed and cleared. Every v1.133 and earlier contract term is preserved except the two C-RT-38 §14.27 amendments below and the C-RT-16 §14.6.3/§14.6.4 breaker-accounting clause they link to.

**Numbering:** Proposed v1.134, relative to main (head v1.133). The number is stable only if this fold is accepted and a current-main collision check finds no other v1.134 cleared first. Renumbering is not content-neutral: A3 source comments cite "Runtime v1.134" (at `619cab32`: `llm_dispatch.py` lines 1510, 1881, 3883 and 5057; `post_tool_effect.py:1`; `retry_breaker_fallback.py:1301`), and the A5 (v1.135) and A4 (v1.136) drafts are numbered on top of it. A renumber must update every one of those citations in the same change. They are listed in `.harness/a3_runtime_fence_fold_authority.md`.

## §0 Change-note (v1.133 → v1.134)

[HIGH] **C-RT-38 provider scope, Ollama.** v1.132 §14.27 "Provider scope and typed assessment" wired C-RT-38 only to the non-memory Anthropic path. This delta extends it to the Ollama route. The extension applies when the dispatcher has **both** an effective frozen tool superset (the descended child superset for a descended step) **and** a bound `RuntimeHITLToolLoop`. Without either, the first-release Ollama refusal path is unchanged byte for byte.

When the extension applies:

1. **Wire.**
   - Every superset entry carrying `input_schema` is sent as `{"type":"function","function":{"name","description","parameters"}}`. An entry without `input_schema` is not sent.
   - The projection reads `name` and `description` from every entry it sends. An entry with `input_schema` that lacks either key raises before the first provider call and before any effect. C-RT-16 then classifies it like any other pre-effect exception.
   - This list replaces `payload.tools`.
   - A descended step whose child superset is empty sends `tools: []` and never the step's declared tools.
   - When standard memory tools are selected, the existing memory-tool injection and collision filter apply to this list.
2. **Identity.**
   - Each non-memory call is assessed under `tool_call_id = "ollama:<nonce>:<turn>:<index>"`.
   - `<nonce>` is 32 lowercase hex characters, minted once per dispatch invocation, so two invocations never share an id.
   - `<turn>` and `<index>` are zero-based positions.
   - The id is never sent to Ollama.
   - A tool result correlates only by `tool_name` (an Ollama wire limit). Repeated calls to one tool in one turn correlate by order.
3. **Turn.**
   - Each reply's calls are answered in call order with one `role:"tool"` message per call.
   - Standard memory calls are batch-validated first and then executed by the memory executor.
   - Every other call goes through C-RT-38 exactly as on Anthropic: assessment, rewrite and palette, audit before disposition, then dispatch.
   - The model reads the same text as on Anthropic: the dispatch result (its `response_text`, else sorted JSON); `policy refused this tool call` plus `: <operator text>` for a refusal; and the REJECT text for a skipped call.
   - A call with no name, or whose arguments are not an object (a mapping or a JSON-object string), is answered `policy refused this tool call: the tool call has no name or its arguments are not an object`. It never enters the loop, and it records `policy_override` plus an `ollama.tool_call.refused` event.
   - Usage is summed across turns.
   - The bound stays at 16 model calls and ends in the existing continuation-bound `RuntimeError`.
4. **Tools unsupported.**
   - Applies only when the first call fails with the daemon's tools-unsupported rejection.
   - That rejection is an exception whose class name is `ResponseError` and whose `.error` string contains `does not support tools`. The status code is not consulted: the daemon returns 400 for this rejection, but it also raises `ResponseError` for unrelated failures. If the daemon rewords the message, the rejection no longer matches and propagates as an ordinary failure.
   - The dispatch retries once with no tools. With memory tools selected, the C-MEM-12 packet is governed by the existing B-83 disposition, published before the retry. Without them, the plain arm's packet is used.
   - It records the span event `ollama.tools_unsupported` with `tool.dropped.count` (the number of projected tools dropped).
   - No tool is dispatched.
   - The same rejection on any later call propagates.
5. **Unchanged.** Subscription-CLI routes stay inference-only and still refuse a payload with tools.

[HIGH] **C-RT-38 post-effect fence, Anthropic and Ollama (closes A2 review P2-1), with a linked C-RT-16 §14.6.3/§14.6.4 amendment.**

- **Who owns the effect state.** Each attempt that C-RT-16 retries owns one effect state: one `RuntimeLLMDispatcher.dispatch` call, which the composer returns unchanged. That state is handed explicitly to the tool-loop arm. There is no ambient or shared state.
- **When an effect has started.** A tool effect has started once C-RT-38's tool dispatcher was entered for any call, or a memory tool call began executing on the Ollama C-RT-38 arm. This holds whether the executor returned or raised; a raise is an ambiguous outcome.
- **What surfaces after that.** Any later `Exception` anywhere in that attempt surfaces as `PostToolEffectError`, carrying the original failure (`fault`, also chained as `__cause__`). This includes:
  - a later batch call;
  - a continuation provider call;
  - a response-shape error;
  - the iteration bound;
  - turn capture (`capture_turn_completion`) and other post-turn bookkeeping.
- **Origin.** The carrier records a structural origin, set by the boundary that observed the failure, never by its message or status code:
  - `provider`: the model provider call failed, or parsing that provider's own reply failed (a malformed reply is provider health under §14.6.3 row 2b, so a response-parsing `LLMDispatchPayloadShapeError` is `provider` whether or not a tool ran first);
  - `non-provider`: tool host, memory validation or executor, turn capture or harness bookkeeping. An error from these that looks like HTTP, such as one with `status_code=529`, is still `non-provider`.
- **Retry wrapper (C-RT-16).** It never retries this carrier and never advances to another candidate. It sets `retry.terminal="post-tool-effect"` and `retry.post_tool_effect.origin`.
- **Breaker accounting (amends C-RT-16 §14.6.3/§14.6.4 for this carrier only).** Replay safety and provider health are separate facts. The carrier's `fault` is judged by the existing §14.6.3 rules; only the control flow (no retry, no advance) differs.
  - **`closed` breaker.** A `provider`-origin carrier whose `fault` is not waived under §14.6.3 is charged once, with `breaker.cause` from the existing classification. It can trip the breaker like any other charge. A waived `provider` fault and every `non-provider` carrier record nothing.
  - **Half-open trial: new §14.6.4 cell 10, "post-tool-effect carrier".** The nine-cell matrix becomes ten. Cells 1-9 are unchanged. Cell 10's outcome depends on the carrier's origin and its `fault`:

    | Carrier | §14.6.3 charge | Breaker disposition | Emission |
    |---|---|---|---|
    | `provider`; `fault` is a charging fail-fast (row 2b response-parsing shape, row 3's 401/403) | CHARGES | as cell 2 | as cell 2 |
    | `provider`; `fault` is transient | CHARGES | as cell 5 | as cell 5 |
    | `provider`; `fault` is waived | WAIVED | INCONCLUSIVE → re-arm: `open`, fresh cooldown, `fail_count` unchanged | `half_open → open`, `trigger_count = 0`, carrier preserved (below) |
    | `non-provider` | never charges | as the waived row | as the waived row |

  - **Emission while the carrier propagates.** In the two re-arm rows the trial is released while the carrier is still in flight. If emitting the transition fails, the emitter error is attached to the carrier as a note, and the carrier propagates unchanged. This differs from ordinary cell 3, where nothing is in flight and an emitter failure propagates as its own fault. In the two charging rows the transition is emitted as in cells 2 and 5. An emitter failure there propagates as it would in those cells, with the carrier as its context.
  - In every row the carrier is neither retried nor advanced to another candidate. Cells 6-9 (signing, HITL terminal, tripped fence, cancellation) do not route through cell 10, because those exceptions keep their own carriers (see Exclusions).
  - No §14.6.3 waiver and no §14.6.4 cell 1-9 is weakened. The earlier "no breaker charge" draft wording is withdrawn.
- **Exclusions.** These keep their existing carriers and are never re-wrapped:
  - the audit-signing hard failures;
  - an already-fenced carrier;
  - `BaseException` signals (cancellation, a tripped dispatch fence, a pause request).

  A failure before any effect keeps its existing classification.
- **No new fail class.** The CP driver records the carrier like any other step exception.
- **Scope limits.**
  - The fence covers dispatches that enter the C-RT-38 Anthropic or Ollama loops. Memory-only arms with no superset keep the registered B-84 residual.
  - The loop also keeps a batch-local record of dispatcher entry. This is what makes an ambiguous or in-batch failure terminal; it hands completed effects to the attempt's state.
  - A HITL terminal error raised after an effect inside the attempt is recorded as the carrier, not its own `RT-FAIL-*`. It is still neither retried nor advanced.

**Acceptance discriminator (source, provider-free).**

- Through the real C-RT-16 wrapper, C-RT-15 dispatcher and C-RT-38 loop:
  - when a retryable 5xx follows an AUTO dispatch, the tool runs exactly once, the wrapper makes one attempt, and the carrier is raised;
  - when the dispatcher is entered and then raises, the effect is entered exactly once;
  - when the first model call fails before any effect, the wrapper retries;
  - when turn capture fails after an AUTO effect, there is one effect, one capture and one attempt (Anthropic and Ollama);
  - when a served Ollama memory write is followed by a 529, there is one memory execution and one attempt;
  - a post-effect provider 529 charges a `closed` breaker once (0 → 1), and in a half-open trial goes 5 → 6, back to `open` with a fresh cooldown, the same as before any effect;
  - a post-effect tool-host error that looks like HTTP never charges the breaker, and its half-open trial is released as inconclusive;
  - a post-effect signing hard failure keeps its own type.
- On Ollama, the wire carries the projection, and each operator outcome (APPROVE, EDIT including `{}`, REJECT, RESPOND, DENY and evaluator failure) reaches the model as specified.
- These are source witnesses. Installed Ollama tool-calling (daemon and model capability) and installed audit or signing remain separate gates.

**Scope.** No new contract number, refusal reason, fail class, configuration field, CXA row or cross-axis edge. §14.6.4 gains cell 10 inside C-RT-16. The design authority for the Ollama route and for the fence is recorded, with full SHA256 values and provenance, in `.harness/a3_runtime_fence_fold_authority.md`.
