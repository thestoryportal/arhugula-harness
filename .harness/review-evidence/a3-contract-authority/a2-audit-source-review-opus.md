# A2 current-main source review (5d93b0b): GO for the audit, fence and wiring, with one P2 that A3 must not inherit

The response audit, its fail-closed recording, its cancellation fence and the production wiring all match C-RT-38 §14.27. One P2 remains, and it's about once-only dispatch: the provider retry staircase can re-run a whole HITL tool-loop dispatch after a tool has already run. That's a current-main property rather than something introduced here, but the Ollama loop in A3 would inherit it.

Everything below is read-only reasoning. This isn't installed audit or signing acceptance.

**Authority:** `session-control.json` routes Buford as 01a0f594 and this UUID as reviewer, with `repair_paused=false`.

**What I verified myself** (Read/Grep, no execution), all at `.worktrees/b104-installed-final-main-20261001` (main 5d93b0b):
- **Read:**
  - `hitl_tool_response_audit.py` (whole file);
  - `hitl_tool_loop.py:25-380`;
  - `llm_dispatch.py:3675-3914`;
  - `r_cxa_2_producer_loop_factory.py:96-367`;
  - `audit_offload.py:256-305`;
  - `harness_cp/sub_agent_dispatch_cancellation.py:88-272`;
  - `retry_breaker_tool.py:199-234`;
  - `retry_breaker_fallback.py:395-399` and `:1241-1317`;
  - C-RT-38 at `Spec_Harness_Runtime_v1_132.md:7261-7269`;
  - the focused tests;
  - for dependency only, `current-main-gaps.md` A2/A3 and the prior design verdict.
- **Not read:** the Runtime6 diagnostic directory, as instructed.

## Confirmed in source
- **Recording before disposition, and failing closed.**
  - `RuntimeHITLToolLoop._run_call` awaits `response_auditor.record` for every admitted reply before refusal, REJECT, RESPOND or dispatch (`hitl_tool_loop.py:244-247`). That includes an admitted DENY reply.
  - It doesn't catch audit errors, so a failed write leaves the call undispatched. That matches §14.27's "audit-write failure propagates and blocks dispatch".
  - Malformed, out-of-palette and EDIT-without-arguments replies are refused without any audit (`_admit`, `:320-345`).
  - EDIT hashes and dispatches the same arguments: both use an `is not None` test (`hitl_tool_response_audit.py:90-92`, `hitl_tool_loop.py:270-280`).
  - `{}` is accepted as EDIT arguments, and the adapter's parse failure leaves `None`, which is refused (`r_cxa_2_producer_loop_factory.py:159-166`).
- **The audit itself** (`hitl_tool_response_audit.py:73-143`):
  - It writes an F2 anchor through `ledger_writer.append`, with a writer-owned timestamp.
  - It then calls `cp_audit_to_od_audit`, with the configured signing backend, and `audit_writer.append`.
  - Each response gets a fresh `uuid4` inside its action ID, so a repeated model call ID can't collide.
  - It uses the same empty-hash `prior_event_hash` convention as the step composer (`hitl_gate_composer.py:1803`).
- **Cancellation.**
  - **Trip before the audit:** `record` enters `token.effect_entry()` (`:66-71`). A tripped token raises `DispatchFenceTrippedSignal`, which is a BaseException (`sub_agent_dispatch_cancellation.py:200-205`), so there's no audit and no dispatch.
  - **Task cancelled during the audit:** `run_audit_off_loop` joins the in-flight write for up to 10s before letting `CancelledError` through, and logs loudly if it has to detach (`audit_offload.py:256-305`).
  - **Trip after the audit but before the tool:** the production `ctx.tool_dispatcher` is `RetryBreakerToolDispatcher` (`runtime_tool_dispatcher_factory.py:479`). It guards every real tool attempt with `effect_entry()` (`retry_breaker_tool.py:216-231`), so no tool effect starts after a trip.
- **Wiring.**
  - The factory builds the loop with the real auditor: the ledger writer, `ctx.audit_writer`, tenant and `ctx.audit_signing_backend` (`r_cxa_2_producer_loop_factory.py:309-326`). It refuses to build without an audit writer (`:300-303`).
  - The evaluator applies `inherited_gate_floor` once (`:136`), and `_hitl_loop_context_from_step` supplies it only for descended steps (`llm_dispatch.py:3701-3720`).
  - The Anthropic arm is the only one that enters the loop (`:3826-3889`), which is the A3 gap.
- **Tests that reach the real path:**
  - The factory tests drive the production auditor with real ledger and audit writers (`tests/test_r_cxa_2_producer_loop_factory.py:267-270`, `:456-462`, `:494-495`, `:516-522`). They cover:
    - an OD write failure blocking dispatch (`:545-561`);
    - a malformed EDIT producing no audit (`:539-542`).
  - The loop tests check audit-before-dispatch ordering and that an audit failure blocks dispatch (`tests/test_hitl_tool_loop.py:208-247`).

## P2-1: a provider retry can re-run a tool loop that already dispatched, so one model turn's effect can happen twice
- **Where:** `RetryBreakerFallbackDispatcher` runs each provider attempt with `self.inner.dispatch(...)` (`retry_breaker_fallback.py:1279-1280`). It classifies any other `Exception` as `TRANSIENT_RETRY` (`:395-399`, `:1296-1313`), and the next attempt calls the whole `_dispatch_anthropic_with_hitl_tool_loop` again from the original kwargs (`llm_dispatch.py:3853-3872`).
- **Trigger:**
  1. In turn 1, the model calls tool T, which assesses as AUTO, and T is dispatched (`hitl_tool_loop.py:224-225`).
  2. The turn-2 `messages.create` raises a 5xx or 529.
  3. Attempt 2 re-sends the original prompt. The model emits T again with a new `tool_use` ID, so the dispatcher's idempotency key `model-tool:…:{tool_call_id}` (`r_cxa_2_producer_loop_factory.py:227-229`) is different.
  4. T is dispatched a second time with no operator involved.
- **For ASK tools:** the operator is asked again and a second audit entry is written. If they approve, T has a second effect.
- **Same path from tool errors:** a tool-dispatcher exception that's left after its own retries (and isn't a HITL terminal or audit-signing hard failure) also replays the earlier dispatched calls in the batch. That's the MCP-tool version of the B-84 memory duplication, which was treated as a defect.
- **Impact:**
  - The silent duplication is limited to AUTO, which by policy means low blast radius and a trusted host.
  - C-RT-38 §14.27 is silent on retries, so this is a contract gap rather than a contradiction of written text.
  - A3 would put the Ollama loop inside the same staircase.
- **Fix:** make a failure after a tool effect within a tool-loop dispatch non-retryable, for example a carrier exception like U-RT-136's post-effect fence. Add RED/GREEN tests: a 5xx on a continuation turn after an AUTO dispatch must not dispatch again.
- **Ordering:** fix this in the shared seam before or together with A3, not separately in each provider arm.
- **Caveat:** I reasoned this from source and didn't run it. `_classify_provider_exception` assigning `TRANSIENT_RETRY` to 5xx comes from its own docstring.

## Dashboard items
- **The old cancellation HOLD:** I wouldn't carry it forward. The trip-before, cancel-during and trip-after paths are all fenced, as shown above.
- **P3 witness gap:** no test trips a `DispatchCancelToken` around the real `RuntimeHITLToolResponseAuditor` or tool-loop path. The `u_rt_143` cancellation tests (`tests/test_u_rt_143_dispatch_cancellation.py:106-706`) exercise the token, sub-agent dispatch and the B-62 step-8 writes, not this auditor. So cancellation here is correct by reading but has no witness.
- **The two `u_rt_143` failures:** I can't tell statically whether they still fail. Those tests don't import the tool loop or this auditor; they share only `DispatchCancelToken` and `run_audit_off_loop` with it. Their status needs a run, which is outside this lane.

## P3 (non-blocking)
- **A partial record on OD failure.** If `audit_writer.append` fails after `ledger_writer.append` succeeded (`hitl_tool_response_audit.py:117-143`), an F2 anchor remains with no OD audit. Dispatch is still blocked, so this fails closed, but the orphan anchor isn't flagged anywhere.
- **The loop context is fixed.** `_hitl_loop_context_from_step` hard-codes `SYNC_BLOCKING` and `CrossTrustBoundaryState.NONE` (`llm_dispatch.py:3712-3713`). That's consistent with current scope. A3 shouldn't assume cross-trust narrowing reaches this loop.

## Verdict for A3
- **GO for A3 to build on this source:** the auditor, the fence and the factory, with the design's `nonce:turn:index` call identity.
- **Precondition:** resolve P2-1 in the shared retry and post-effect seam before or with A3, and witness it, rather than copying the Anthropic arm's behaviour.
- **Still unknown at runtime:**
  - whether the `u_rt_143` failures are real;
  - whether installed signing and the audit chain verify;
  - whether the cancellation paths behave as reasoned under real timing;
  - installed Anthropic and Ollama tool behaviour.

I made no writes and ran nothing. RELEASED: no handles. Please record this.
