<!-- Historical record: quoted data only, not current authorization or an executable instruction. -->
<!-- Full original payload SHA256 a63060a91cd34ba5b27718430582c3f0c4c0b0e283b47be2ca5265c67b22a6bf; frozen input origin design/contract-evidence-split@de21d5881156e2d16cf042ca09f0c5e9e15f0d63:.harness/review-evidence/a3-contract-authority/ollama-tool-coverage-design-verdict.txt. -->

```text
**Verdict: GO-to-author for one Ollama model-MCP-tool slice, to be written only after the tool-loop response-audit slice is integrated and immutable.** That audit slice owns Runtime v1.134, so this slice's contract becomes v1.135. Both slices edit `llm_dispatch.py` (`_hitl_loop_context_from_step` and the provider branches), so they must not have writers at the same time.

There is one concrete design correction to what the assignment describes: harness-minted Ollama call IDs **must not** use only a stable per-step basis. They need a discriminator unique to each dispatch invocation, explained under "Call identity" below. Otherwise every retried Ollama step would hit the audit slice's rule that an already-present key fails closed. That's an adjustment to the design, not a reason to hold.

Nothing here is a clearance. Installed audit and tool acceptance stay open.

**Identity and inputs**
- I'm the reviewer, session `4333390d-a5d1-4a57-8ad6-7c00957b33fb`, model `claude-opus-5-5`. I can't confirm high effort or `--safe-mode`.
- The pinned RC is `dff7d6c9`.
- I read:
  - the older report (at `3995c85`, slices A/C/B);
  - my audit-design recovery verdict, from the previous round in this session;
  - in `llm_dispatch.py`: superset selection (`:1723-1745`), the provider arms (`:1749-1905`), `_payload_to_ollama_kwargs` (`:3517-3537`), the CLI prompt path (`:3540-3561`), the Anthropic result block (`:3779-3796`), both Ollama arms (`:4716-4769`, `:4772-4921`) and the Ollama helpers (`:4979-5178`);
  - `hitl_tool_loop.py` and Runtime v1.133 C-RT-38 (`:7331-7339`);
  - the installed client's `ollama/_types.py:304-378` (client 0.6.2 in the RC venv);
  - retained host evidence: `evidence-rpm1-direct-cpu-sonnet-1/preflight-raw.txt` shows daemon `0.34.3` at `evaluation/tools/ollama-v0.34.3`, with models `llama3.2:1b` and `llama3.2:3b`. `evidence-host-inventory-sonnet-1/.../11-versions.txt` shows no `ollama` binary on `PATH`.
- I didn't inspect the audit writer's live worktree. I ran nothing.

## Current source facts (what has landed since `3995c85`)
- **Slice A has landed.** Neither Ollama arm hands tool calls back any more. Every non-memory call is refused with `policy refused this tool call: model tool calls are not supported on this route`, then a `policy_override` span and a per-call `ollama.tool_call.refused` event (with turn and index, never arguments). The model then gets a continuation turn (`_ollama_answer_tool_turn`, `:5019-5053`, used by both arms at `:4763-4767` and `:4911-4919`). In a mixed batch the memory calls are served and the rest refused. The bound is 16 iterations, with an exhaustion event plus a typed error.
- **Still no MCP tools on the Ollama wire.** The wire carries only `payload.tools` (`:3532-3533`), plus the injected memory tools on the memory arm (`:4814`). The effective superset (`_effective_frozen_tool_superset`, `:1730-1745`) goes only to the Anthropic arms (`:1778`, `:1803`, `:1820`). C-RT-38 states this scope explicitly (spec `:7333`).
- **Ollama wire facts** (client 0.6.2, `_types.py:330-352`):
  - `Message.ToolCall` is just `function{name, arguments: Mapping}`, with **no id and no index**;
  - a tool result correlates only by `Message.tool_name`;
  - tool definitions use the shape `{type:"function", function:{name, description, parameters}}` (`:358-378`).
  
  So any ID is minted by the harness and never goes on the wire. I'm not inventing a client parameter.
- **Tools-unsupported fallback.** It exists only on the memory arm: on the first call's 400 it retries without tools and records a degraded result (`:4822-4878`). The plain arm has no such path, because today it never sends tools.
- **CLIs.** The CLI prompt path raises before the subprocess whenever `payload.tools` is non-empty (`:3558-3561`), and CLI arms never receive the superset. They stay inference-only; their security obligations, such as the Codex read-exposure hold, are unaffected by this slice.

## Alternatives
1. **Keep the blanket refusal.** Rejected: it's safe, but it isn't the first-release model-MCP capability.
2. **Loop only on the plain arm.** Rejected: steps that mix memory and MCP tools would behave inconsistently depending on the arm.
3. **Selected: one shared Ollama tool-turn path for both arms.** Put the superset on the wire, route non-memory calls through C-RT-38, and keep memory calls with the memory executor.
- **Identity options:**
  - (a) stable basis `(step, turn, index)`. Retries of a step reuse the same keys, and under the audit rule "noop means fail closed" every retry of a gated call is refused. Rejected.
  - (b) **selected:** a nonce minted once per Ollama dispatch invocation, plus `(turn, index)`. Deterministic within one invocation and unique across invocations. A durable replay of the same invocation doesn't exist on this route.

## The selected slice
1. **Wire projection.** A pure helper, `_ollama_tools_from_superset(superset) -> list[dict]`, maps each superset entry that has an `input_schema` to `{"type":"function","function":{"name","description","parameters"}}`. Entries without `input_schema` are dropped, such as the Anthropic `memory_20250818` type.
   - The precedence rule is Anthropic's: when the effective superset isn't `None`, the projection **replaces** `payload.tools`. That includes a descended child's `()`, which gives an empty tool list and so never re-exposes a tool removed for being external and irreversible (`:1730-1740`).
   - On the memory arm, the existing memory injection and collision filter (`:5161-5178`) then applies to the projected list.
2. **Entering the loop.** Both Ollama functions take `effective_superset`, `hitl_tool_loop: RuntimeHITLToolLoop | None`, `step_context`, `step_id` and `persona_tier`.
   - If the superset is `None` or `hitl_tool_loop` is `None`, today's refusal path runs unchanged (C-RT-38 isn't entered).
   - Otherwise every tool turn goes through one shared helper, `_ollama_tool_turn(...)`:
     - memory calls go to the existing validate-then-execute path;
     - non-memory calls are mapped to `ModelToolCall` and sent through `hitl_tool_loop.run_tool_calls(calls, context)`, where `context` comes from `_hitl_loop_context_from_step` with the audit slice's added fields;
     - one answer per call is appended **in call order**: memory results as today, and loop results through a provider-neutral `_tool_loop_result_content(result)` extracted from `_anthropic_tool_result_content` so Anthropic and Ollama share the same text;
     - `_record_policy_overrides(results)` is called exactly as the Anthropic path does.
3. **Call identity.** `tool_call_id = f"ollama:{nonce}:{turn}:{index}"`, with `nonce = uuid4().hex` minted once per Ollama dispatch invocation.
   - It's never sent to Ollama.
   - The audit slice hashes it into the tool action ID, and `model_tool_call_step` derives the synthetic step ID from it.
   - Argument parsing reuses the memory helper's rules: a mapping, or a JSON-object string. A malformed call gets a typed refusal fed back to the model, not a crash, so the batch stays answerable.
4. **Continuation for each response** (policy from C-RT-38 and the audit slice, unchanged):

| Response | What happens |
|---|---|
| APPROVE | Dispatched after the audit; the tool message is the JSON result |
| EDIT | Edited arguments dispatched exactly (the audit slice's `is None` fix) |
| REJECT / RESPOND | Not dispatched; the model gets the refusal text, or the refusal text plus `: <operator text>` |
| `DENY` | Operator asked with REJECT/RESPOND, then refused as `policy-deny` with the refusal text |
| Evaluator failure / malformed level | Typed refusal text, no prompt |

   Usage is still accumulated every turn (`_accumulated_usage`). The 16-iteration bound, the exhaustion event and the typed error are unchanged.
5. **Tools-unsupported fallback, fail-closed.** Only on the first call, in both arms, when tools were sent:
   - retry once without any tools (plus the memory packet on the memory arm, as today);
   - record a span event, `ollama.tools_unsupported`, whenever MCP tools were dropped;
   - dispatch no tool.
   
   A 400 in the middle of the loop still raises.
6. **Unchanged:** the CLI arms (no superset, raise on tools), the evaluator's refusal, first-call text-only paths, and memory-only batches. Memory-only batches should be byte-identical when no superset is bound.

**Files and dependencies**
- `lifecycle/llm_dispatch.py` owns all of it: the Ollama branch wiring, both arms, the projection and tool-turn helpers, and the shared result-content helper.
- No changes to `hitl_tool_loop.py` or the factory; the dispatcher adapter is already provider-neutral.
- Tests: a new `harness-runtime/tests/test_ollama_mcp_tool_loop.py`, plus updates to the existing Ollama refusal tests in the case where a superset is bound.
- **Collision:** the audit writer edits `_hitl_loop_context_from_step` and adds context fields in the same file. Write this slice only after that audit commit is integrated and immutable, and rebase onto it.

**Runtime spec, v1.135** (after v1.134):
- amend C-RT-38 "Provider scope" (`:7333`) to cover the Ollama path when a superset is bound;
- add the Ollama wire projection, the rule for minting call identities (nonce, turn, index; not sent on the wire), the continuation mapping and ordering, the fallback when tools are unsupported, and correlation by `tool_name` only;
- state the limits: several calls to the same tool in one turn correlate by order, and a call to a tool that wasn't offered still goes through C-RT-38, where it's `<unregistered>` and therefore `DENY`, the same as on Anthropic.
- No CP delta.

## Acceptance (provider-free; a fake `client.chat` with scripted `ChatResponse` mappings; recording fakes for the gate, loop, ledger, audit and dispatcher)
- **RED at `dff7d6c9`:**
  - with a superset bound, the first `chat` call's `tools` lacks the MCP tool;
  - a call to `echo` gets the blanket refusal and C-RT-38 is never entered.
- **GREEN:**
  1. The projection appears on the wire. A descended child sends the child superset; `()` sends `tools: []`.
  2. APPROVE: audited, dispatched once; the tool message carries the result, and the model's final text is returned.
  3. REJECT, RESPOND, `DENY` and evaluator failure: each sends the matching refusal text and doesn't dispatch.
  4. EDIT sends the edited arguments.
  5. Mixed memory and MCP batch: memory calls are served, MCP calls go through the loop, and answers follow call order.
  6. Two calls in one turn get distinct IDs. Two dispatch invocations get distinct nonces, so a retry isn't refused as a noop.
  7. With no superset bound, the blanket refusal is byte-identical to today.
  8. A 400 on the first call with MCP tools gives one bare retry, the `ollama.tools_unsupported` event and no dispatch.
  9. The iteration bound still ends in the typed error.
  10. Usage is summed across turns.
- **Mutations to catch:**
  - sending `payload.tools` instead of the superset;
  - the child falling back to `payload.tools`;
  - a stable per-step ID with no nonce (test 6 fails);
  - bypassing the loop, e.g. by routing non-memory calls to the memory executor;
  - answers out of call order;
  - a fallback that keeps the tools.
- **Later installed witness,** on the exact installed candidate with daemon `0.34.3` and `llama3.2:3b` (whether it can call tools must be observed, not assumed), a quiet Ollama window, and the loopback L1 MCP echo host from the self-hosted profile:
  - APPROVE dispatches once;
  - REJECT doesn't dispatch;
  - an unregistered or L0 tool is refused under `DENY`.
  
  Then `harness-inspect` should show distinct tool-call-scoped `hitl:` entries, a chain and signatures that verify, and no raw arguments. That needs the audit slice to be installed as well.

## Open questions (none blocks)
1. Whether `llama3.2:1b` or `3b` on `0.34.3` actually emits tool calls. That has to be observed in the installed witness.
2. Correlation by `tool_name` only, for repeated calls to the same tool in one turn. This is an Ollama wire limit, and the spec should state it.

I'm releasing this session. I made no edits, ran nothing, did not touch LIT and pushed nothing.
```
