# Specification — Harness Runtime v1.134 (delta over v1.133)

**Status:** Proposed. This is the bundled-absorption arc for A3, with fork record `.harness/class_1_fork_a3_ollama_mcp_loop_and_post_effect_retry.md`. Runtime v1.133 remains the cleared head until this delta is independently reviewed and cleared. Every v1.133 and earlier contract term is preserved except the two C-RT-38 §14.27 amendments below and the C-RT-16 §14.6.3/§14.6.4 breaker-accounting clause they link to. Two baselines apply. Main `c995ec9f9fa5945a40ffe30734b859bb6e88e2a8` carries this Proposed text but not its implementation: Ollama there still refuses model tool calls, and no post-effect fence exists. The implementation is the committed candidate `47ca58b507133e7c9839e822d5925026c53cc8e9` (branch `prep/a3-current-controls-20261003`), which is not on main. Citations to main facts name `c995ec9f`; citations to A3 behavior name `47ca58b5`. Landing, CI and installed acceptance are not claimed.

**Numbering:** Proposed v1.134, relative to main (head v1.133). The number is stable only if this fold is accepted and a current-main collision check finds no other v1.134 cleared first; at `c995ec9f` none is (this is the only v1.134 file, and no v1.134 or v2.65 clearance marker or artifact-head row exists). Renumbering is not content-neutral. On main, the A5 (v1.135) and A4 (v1.136) drafts are numbered on top of this one and CP spec v1.128 names it. Main source cites no "Runtime v1.134", but candidate `47ca58b5` cites it in runtime source, CP source and tests, and its B-126 register row cites this file's line 57 (`Spec_Harness_Runtime_v1_134.md:57`). A renumber, or an edit that moves line 57, must update every one of those citations in the same change. They are listed in `.harness/a3_runtime_fence_fold_authority.md`.

## §0 Change-note (v1.133 → v1.134)

[HIGH] **C-RT-38 provider scope, Ollama.** v1.132 §14.27 "Provider scope and typed assessment" wired C-RT-38 only to the non-memory Anthropic path. This delta extends it to the Ollama route. The extension applies when the dispatcher has **both** an effective frozen tool superset (the descended child superset for a descended step) **and** a bound `RuntimeHITLToolLoop`. Without either, the first-release Ollama refusal path is unchanged byte for byte. Entry therefore differs by provider. Ollama enters whenever both are bound, without consulting `payload.tools`: a step that declares no tools still enters and is offered the projected superset, and a descended step whose child superset is empty enters with an empty offer (candidate `47ca58b5` `llm_dispatch.py:1877-1879`). Anthropic entry is unchanged from main: the C-RT-38 arm runs when the loop is bound and the step declares tools that do not include the Anthropic Memory tool (`llm_dispatch.py:1783-1787` at `c995ec9f`; the same condition at `47ca58b5` `:1794-1798`). An Anthropic memory step goes to the memory arm when the memory registry and deployment surface are bound, and to the plain arm otherwise. Cleared v1.132 §14.27 states the Anthropic scope as "the non-memory Anthropic dispatch path with `payload.tools`" (`Spec_Harness_Runtime_v1_132.md:7263`); the bound-loop condition is the implementation's precondition, not a cleared term.

When the extension applies:

1. **Wire.**
   - Every superset entry carrying `input_schema` is sent as `{"type":"function","function":{"name","description","parameters"}}`. An entry without `input_schema` is not sent.
   - The projection reads `name` and `description` from every entry it sends. An entry with `input_schema` that lacks either key raises before the first provider call and before any effect. C-RT-16 then classifies it like any other pre-effect exception. The production superset supplies both keys. Each MCP entry is projected from a registry contract: stage 3a binds `MCPClientHost` instances, whose `ToolRegistry` is typed to `ToolContract` (`stage_3a_cp_clients.py:66`, `mcp_client_host_factory.py:263-266`, `mcp_client_host.py:43,280,340-343`, `tool_registry.py:95,108`); the registry does not check types at runtime. The production converter is what constructs each contract: it builds a validated `ToolContract` with `description=tool.description or ""` (`mcp_client_host_factory.py:194-196`) and is wired into every stage-3a host (`:258`). Its `description` is therefore that contract's required `str` (C-AS-03 §3.1, `tool_contract.py:74`), which is empty when the MCP server supplies none, in which case `""` is sent (`frozen_tool_superset.py:130-150`). The `search_tools` stub carries a literal description (`tool_search.py:48-50`), and the Memory entry has no `input_schema` and is not sent (`frozen_tool_superset.py:41`). All at `c995ec9f`.
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
   - A well-formed non-memory call is admitted only if its name is among the non-memory tools in the final list sent to Ollama, after superset projection and the existing memory injection/collision filter. A call outside that offer is refused before assessment, rewrite, prompt, response audit or dispatch, even if its tool is registered; the model receives `policy refused this tool call`, with `policy_override` and an `ollama.tool_call.refused` event. This includes an empty offer and entries omitted for lacking `input_schema`. [APPSPEC:condition-effect]
   - Offer membership is distinct from `step.tools`: a registered tool omitted from that declaration may still be admitted if the effective descended superset offers it. This amends the Ollama arm only; v1.132's §14.14.8 paragraph "Runtime-created contexts outside the CP driver" records the existing C-RT-38 not-offered residual, which remains on Anthropic. Selected standard memory calls retain their existing validation and execution rules.
   - Each admitted non-memory call then goes through C-RT-38 as on Anthropic: assessment, rewrite and palette, audit before disposition, then dispatch. Membership never substitutes for gate enforcement.
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
  - **Half-open trial: new §14.6.4 cell 10, "post-tool-effect carrier".** The nine-cell matrix becomes ten. Cells 1-9 retain their dispositions for outcomes that keep their own carriers; a HITL terminal error uses cell 7 before any effect and the non-provider row of cell 10 after an effect. Cell 10's outcome depends on the carrier's origin and its `fault`:

    | Carrier | §14.6.3 charge | Breaker disposition | Emission |
    |---|---|---|---|
    | `provider`; `fault` is a charging fail-fast (row 2b response-parsing shape, row 3's 401/403) | CHARGES | as cell 2 | as cell 2 |
    | `provider`; `fault` is transient | CHARGES | as cell 5 | as cell 5 |
    | `provider`; `fault` is waived | WAIVED | INCONCLUSIVE → re-arm: `open`, fresh cooldown, `fail_count` unchanged | `half_open → open`, `trigger_count = 0`, carrier preserved (below) |
    | `non-provider` | never charges | as the waived row | as the waived row |

  - **Emission while the carrier propagates.** In the two re-arm rows the trial is released while the carrier is still in flight. If emitting the transition fails, the emitter error is attached to the carrier as a note, and the carrier propagates unchanged. This differs from ordinary cell 3, where nothing is in flight and an emitter failure propagates as its own fault. In the two charging rows the transition is emitted as in cells 2 and 5. An emitter failure there propagates as it would in those cells, with the carrier as its context.
  - In every row the carrier is neither retried nor advanced to another candidate. Cells 6, 8 and 9 (signing, tripped fence, cancellation) do not route through cell 10: their exceptions keep their own carriers (see Exclusions). Cell 7's HITL terminal identity is preserved only before any effect; after an effect it becomes a non-provider carrier, still never charged, retried or advanced.
  - No §14.6.3 waiver or existing cell disposition is weakened. The post-effect HITL routing above is the sole change to cell 7's applicability. The earlier "no breaker charge" draft wording is withdrawn.
- **Exclusions.** These keep their existing carriers and are never re-wrapped:
  - the audit-signing hard failures;
  - an already-fenced carrier;
  - `BaseException` signals (cancellation, a tripped dispatch fence, a pause request).

  A failure before any effect keeps its existing classification.
- **No new fail class.** The CP driver records the carrier like any other step exception.
- **Scope limits.**
  - The fence covers dispatches that enter the C-RT-38 Anthropic or Ollama loops. Memory-only arms with no superset keep the registered B-84 residual.
  - The loop also keeps a batch-local record of dispatcher entry. This is what makes an ambiguous or in-batch failure terminal; it hands completed effects to the attempt's state.
  - A HITL terminal error before any effect retains its original identity and `RT-FAIL-*`. After an effect inside the attempt it surfaces as a non-provider `PostToolEffectError`, with the original error as `fault` and `__cause__`; CP records the carrier rather than the original `RT-FAIL-*`. In `closed` it is uncharged; in a half-open trial cell 10 re-arms to `open` with a fresh cooldown, unchanged `fail_count` and `trigger_count = 0`. Both cases remain terminal without retry or candidate advance. [APPSPEC:errors-are-api]
  - **Registered residual: a no-dispatch answer can be asked again.** A C-RT-38 outcome that does not dispatch is not an effect: REJECT, RESPOND, a DENY reply, an evaluator or malformed-assessment refusal, and on Ollama an offer or malformed-call refusal. None of them enters the tool dispatcher, the only place an effect starts (`hitl_tool_loop.py:210-218,247-276,302` and `llm_dispatch.py:5144,5152-5166` at `47ca58b5`). If the attempt then fails before any effect, for example with a transient continuation 5xx, C-RT-16 classifies the failure as before and may retry the whole attempt with a fresh effect state (`llm_dispatch.py:1456`). The retry asks the model again. If the new reply repeats a gated call, the operator may be prompted again, and the rewrite record and any response-audit entry are written again under the new reply's call id: a fresh nonce on Ollama (`llm_dispatch.py:5085`), the new reply's tool-use id on Anthropic. This is a registered residual, not replay of a tool effect, and it changes neither the effect fence nor runtime behavior. Making an answered gate start the fence would be a separate design change with its own source and tests.

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
  - the same HITL terminal error before and after an AUTO effect, on both providers and with closed and half-open breakers: before, original identity and `RT-FAIL-*` (cell 7); after, a non-provider carrier with that exact error as `fault` and `__cause__` (cell 10). Each makes one attempt and no candidate advance; the before case has zero effects and the after case one. Neither charges; both half-open cases re-arm with a fresh cooldown, unchanged `fail_count` and `trigger_count = 0`.
- On Ollama, the wire carries the projection, and each operator outcome (APPROVE, EDIT including `{}`, REJECT, RESPOND, DENY and evaluator failure) reaches the model as specified. A model-emitted registered non-memory tool absent from the final offer is refused with no assessment, prompt, response audit or dispatch, including `tools: []` and projection omissions. A tool omitted from `step.tools` but present in the effective descended offer passes this boundary and is still gated. A mixed selected-memory/omitted-MCP batch serves memory and refuses the omitted MCP call in call order.
- These are source witnesses. Installed Ollama tool-calling (daemon and model capability) and installed audit or signing remain separate gates.

**Scope.** No new contract number, refusal reason, fail class, configuration field, CXA row or cross-axis edge. §14.6.4 gains cell 10 inside C-RT-16. The retry wrapper's `retry.post_tool_effect.origin` (line 57) is a new `retry.*` wire key that C-CP-03 §3.5 does not declare, so it takes a row in CP's B-126 wire register. At `c995ec9f` that register has five rows and no such key (`harness-cp/src/harness_cp/retry_fallback_namespace.py:256-288`), and its drift test pins ten emitted keys (`harness-cp/cp_tests/test_b126_retry_wire_register.py:473,487`). Candidate `47ca58b5` adds the row, with this file's line 57 as its declaring authority (`retry_fallback_namespace.py:257-264`, authority at `:260-261`), and moves the pin to eleven (`test_b126_retry_wire_register.py:473,487`). The row changes no CP spec, plan or contract. The design authority for the Ollama route and for the fence is recorded, with full SHA256 values and provenance, in `.harness/a3_runtime_fence_fold_authority.md`.
