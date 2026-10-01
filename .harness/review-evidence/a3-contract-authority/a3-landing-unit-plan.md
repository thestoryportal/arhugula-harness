# A3 landing plan: two coherent source units

TO: Buford lead `01a0f594-02cb-72a1-8a9b-46c32e99f1a8`.
FROM: Codex independent source reviewer `01a0f692-3256-72e3-8d95-4bf7e7046e8f`, GPT-6.1-sol/high.
Assignment: `arhugula-harness-trial-193` / `cmt-1cc2b9e9-66f2-4826-b29d-835af01fc525`.

Recommend **Unit 1: shared post-effect fence and Anthropic safety**, then **Unit 2: Ollama C-RT-38 route**. A substantive A3 contract fold must be independently accepted before source implementation is represented as conforming to a cleared v1.134/v2.65 head. Package only after Buford confirms the source author is RELEASED. This is a read-only architecture/sizing proposal, not a created unit, formal clearance or ship gate.

## Pinned size and dependency

Main is `5d93b0bf27e4a6c602ffff7dad49e5dd21be1f22`; A3 is clean at `619cab32785927142deb01876c260cbb696ec4b1`. Actual main→A3 production delta: **509 additions + 56 deletions = 565 changed lines** across four Python files. Counts include production comments/docstrings/blank lines and exclude tests/contracts/docs. This follows the product review-cycle instruction at `.claude/skills/merge-gate/SKILL.md:279` to split near 300 changed non-test lines before formal pass 1.

| Proposed unit | Path relative to worktree | Add / delete | Changed |
| --- | --- | --- | --- |
| 1 | `harness-runtime/src/harness_runtime/lifecycle/post_tool_effect.py` | 102 / 0 | 102 |
| 1 | `harness-runtime/src/harness_runtime/lifecycle/hitl_tool_loop.py` | 16 / 6 | 22 |
| 1 | `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py` | 54 / 0 | 54 |
| 1 | shared/Anthropic hunks in `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` | 73 / 47 | 120 |
| **1 total** | | **245 / 53** | **298** |
| **2 total** | remaining Ollama/result-projection hunks in `llm_dispatch.py` | **264 / 3** | **267** |

The pins JSON records every `git diff --unified=0` hunk allocation and all ten changed-file hashes. These are exact allocations of the existing diff; actual packaged-parent diffs must be recounted because no intermediate tree/ref was created or checked here. Unit 1 has little sizing room; formatting or production additions require a new count before pass 1.

Dependency sequence: current main plus accepted A3 contract fold → Unit 1 → Unit 2. Unit 2's source parent must include the complete verified Unit 1, rebased onto the actual landed parent with a fresh diff/evidence binding. Source review infers that the intermediate runtime is coherent: Anthropic effects gain terminal replay protection; Ollama retains its existing refusal/memory-only behavior until Unit 2. Intermediate importability and tests still require author/new-head verification.

## Unit 1 ownership and indivisible behavior

Released Claude source author should own only these four production paths and their directly associated tests. Codex remains the independent planner/reviewer. Retain the original branch and all original commits; record original commit and session attributions in the packaging commits/evidence rather than rewriting the reviewed branch.

Copy `post_tool_effect.py`, `hitl_tool_loop.py` and `retry_breaker_fallback.py` from 619 in full. In `llm_dispatch.py`, take:

- the `HITLToolLoopCallResult` and `ToolEffectFence` imports;
- one attempt-owned fence in `RuntimeLLMDispatcher.dispatch`, explicit threading through `_provider_dispatch` / `_invoke_provider`, and the guard around the complete `infer()` operation;
- the explicit fence argument at the existing Anthropic call site and `_dispatch_anthropic_with_hitl_tool_loop` signature;
- the final 619 Anthropic provider-call/reply-parsing fence, assistant projection, `_run_fenced_tool_calls` call and continuation bookkeeping;
- `_run_fenced_tool_calls` at 619 lines 4964–4976, including its returned-effects fold and policy override recording.

Keep the base `_anthropic_tool_result_content` name and its base caller in `_anthropic_tool_result_block`. Defer the rename to `_tool_loop_result_content` and its additional docstring to Unit 2, whose Ollama consumer needs that name. Defer the UUID import, Ollama route selection and all new Ollama constants/helpers. Thus Unit 1 has no dangling Ollama function reference or unnecessary forward-only primitive PR. `[LAW:decomposition]` This first unit changes an existing production behavior and carries the complete boundary needed to make that behavior safe.

The carrier/fence, local C-RT-38 effect-entry guard, attempt-wide guard including capture, Anthropic call **and reply parsing**, and retry-wrapper terminal/charge path must land together. Splitting their corrections across intermediate heads would reintroduce either replay, lost capture protection or lost provider charging. `[LAW:single-enforcer]` Preserve origin where the provider reply is consumed, and effect lifetime at the retry-attempt owner. Existing Runtime v1.132 §14.6.3 row 2b / §14.6.4 cell 2 remain charge authority; do not restore the bb275 draft's no-charge behavior. Preserve internal-shape waivers, closed/half-open accounting, non-provider HTTP-shaped errors, signing-family identity and BaseException control identity.

### Meaningful Unit 1 tests

Ship a physical Anthropic/shared subset of `test_post_tool_effect_replay.py`, its necessary helpers and the +10 `dispatched` property fixture edits in `test_lifecycle_llm_dispatch.py`. A full 619 replay file at this head would assert the unavailable Ollama route; selecting a subset only in an ad hoc command would leave the committed test suite invalid. Do not add broad skips or claim those unimplemented cases pass.

Current exact nodes that supply the nine-case Anthropic subset, under `harness-runtime/tests/test_post_tool_effect_replay.py::`:

- `test_anthropic_continuation_failure_after_a_tool_effect_is_never_replayed`
- `test_an_ambiguous_tool_dispatch_failure_is_never_replayed`
- `test_a_failure_before_any_tool_effect_still_retries[anthropic]`
- `test_a_capture_failure_after_a_tool_effect_is_never_replayed[anthropic]`
- `test_a_signing_hard_failure_after_an_effect_keeps_its_own_carrier`
- `test_a_malformed_provider_reply_is_charged_whether_or_not_a_tool_ran[anthropic-pre-effect-closed]`
- `test_a_malformed_provider_reply_is_charged_whether_or_not_a_tool_ran[anthropic-pre-effect-half-open]`
- `test_a_malformed_provider_reply_is_charged_whether_or_not_a_tool_ran[anthropic-post-effect-closed]`
- `test_a_malformed_provider_reply_is_charged_whether_or_not_a_tool_ran[anthropic-post-effect-half-open]`

Unit 1 also needs author-packaged Anthropic versions of the current Ollama-specific post-effect non-provider/half-open and exact cancellation/fence-identity controls. Use the existing `test_a_non_provider_post_effect_failure_never_charges_the_breaker[closed|half-open]` and `test_a_control_signal_after_an_effect_keeps_its_identity_and_never_charges[cancelled|dispatch-fence-tripped]` as behavior references; their current bodies require Unit 2 and cannot be counted as Unit 1 passes. These are necessary derivative tests, not executions or invented existing node names. Keep their added names/pins explicit. Existing `test_lifecycle_retry_breaker_fallback.py::test_response_parsing_payload_shape_still_charges`, `test_b118_cell6_audit_signing_hard_failure_during_a_trial_re_arms`, `test_b118_cell8_dispatch_fence_signal_during_a_trial_re_arms` and `test_b118_cell9_cancellation_during_a_trial_re_arms_silently` protect the neighboring rules; they do not alone witness a post-tool effect. Keep the existing dispatch/HITL/retry suites meaningful at this head.

## Unit 2 ownership and invariants

Unit 2 depends on all of Unit 1 and changes only production `llm_dispatch.py`:

- UUID import at 619 line 70;
- Ollama branch hunk at 1877–1902, retaining the existing memory-only branch as `elif`;
- result formatter rename/docstring at 3799–3800 and Anthropic caller at 3826;
- new Ollama block at 4977–5210: constants, `_ollama_tools_from_superset`, `_ollama_call_arguments`, `_ollama_refused_answer`, `_dispatch_ollama_with_hitl_tool_loop`, `_ollama_tools_unsupported_retry`.

Keep the corrected provider-call/reply-parsing fence, first-call-only unsupported-tools fallback, batch memory validation outside the provider boundary, and memory effect entry together with the route selection. Preserve nonce identity, ordered mixed memory/MCP answers, superset replacement, no-superset baseline behavior, usage and iteration bound. This is an extension onto a complete safety boundary, not an alternate carrier implementation. Final production bytes should match all four 619 source-file hashes; tests may include Unit 1's additional Anthropic controls and therefore need their own new hashes.

Unit 2 adds `test_ollama_mcp_tool_loop.py` and completes the retained replay file's Ollama branches. Exact route nodes include `test_the_superset_projection_replaces_payload_tools_on_the_wire`, `test_a_descended_step_sends_the_child_superset`, `test_an_empty_child_superset_sends_no_tools_never_the_step_tools`, `test_an_approved_call_is_audited_dispatched_once_and_answered`, `test_a_mixed_batch_serves_memory_and_mcp_in_call_order`, `test_call_ids_are_distinct_and_never_reused_across_dispatches`, `test_without_superset_and_loop_the_refusal_path_is_unchanged`, `test_a_tools_unsupported_model_gets_one_bare_retry_and_no_dispatch`, `test_a_mid_loop_tools_rejection_still_raises`, `test_the_iteration_bound_still_ends_in_the_typed_error`, `test_usage_is_summed_across_tool_turns`, plus the parametrized refusal/edit/malformed-call nodes already in that file. Include every existing case, not just this illustrative list.

Replay nodes include `test_ollama_continuation_failure_after_a_tool_effect_is_never_replayed`, `test_a_post_effect_provider_fault_charges_the_closed_breaker_once`, `test_a_half_open_trial_provider_fault_is_charged_and_re_opens[pre-effect|post-effect]`, `test_a_served_ollama_memory_write_then_provider_fault_is_never_replayed[closed|half-open]`, all paired Ollama malformed-reply nodes, and the non-provider/memory/control-identity cases deferred above. The memory-only B-84 replay gap with no superset remains outside both units; do not extend Unit 1's claim to that arm.

## Contract fold and evidence boundaries

Cleared Runtime v1.133 / plan v2.64 remain authoritative until accepted clearance. Preserve A3's full Proposed Runtime v1.134 / plan v2.65 / fork record from 619. Recommend one **substantive contract-fold step** before Unit 1, after independent specification/back-flow review and Buford disposition. It carries the actual normative provider/fence/charge amendments and U-RT-157 execution map; it is not a tracking-only PR. Required clearance/pointer/derived-head updates occur only through the accepted fold. No new versions or ratification are minted here, and A5 Runtime135/266 or A4 Runtime136/267 are not borrowed.

Track the two source deliveries as U-RT-157 implementation portions; the current plan's combined acceptance criteria and completion boundary remain open until both portions and their verification are complete. A cleared plan may describe future implementation. Unit 1 is an explicit partial implementation with the old Ollama route still present; do not mark the full U-RT-157, Ollama capability or complete contract conformance done at its intermediate head. If the formal fold requires changing the proposed execution map to make those portions explicit, obtain independent review of that changed contract before accepting it; preserve the original proposed artifact and provenance. Alternatively Buford can carry that same accepted full contract fold in Unit 1's substantive bundle, with partial implementation recorded. This choice changes packaging, not the 298/267 production allocation.

Original commits remain preserved: bb275efff1bd74ca2e0631d643d22b27e8bf4bb5 (initial A3 author report attributes facade-coder f235114c), c6d017cfc05a508145ed75dd28ef99cf016c2305 (attempt/origin correction), and 619cab32785927142deb01876c260cbb696ec4b1 (parsing correction attributed to Claude coder8617fb60 in `a3-parsing-fix/evidence.md`). Git's common Robert Rhu identity is not evidence that these agent roles are interchangeable. Preserve the correction's ticket/session attribution from its retained record when packaging; do not infer its agent solely from Git.

Retained author mutation evidence is relevant mechanism evidence where bytes remain unchanged: initial M1/M2 terminal-carrier/fence and correction C1/C2/C3/C4/C6/C7 belong to Unit 1 mechanisms; M3 nonce/M4 superset/M5 tools fallback/M6 loop routing and C5 served-memory fence belong to Unit 2. Some original witnesses for shared mutations use Ollama and thus transfer only after Unit 2. Final parsing mutation `mutation-parse-outside-provider` must split its paired Anthropic/Ollama witnesses across units; `mutation-provider-over-memory` belongs to Unit 2. Retain original failures/restoration hashes and author attribution. None of these logs is a newly executed mutation or new-head attestation. Unit 1's derivative tests and any relocated hunks must be rebound; author mutation equivalence must be checked against actual packaged bytes.

The independent 619 replay **26-pass** result and 15 supplemental cases remain evidence for that head. New unit heads require their own import/HEAD/hash-bound narrow behavioral tests, pertinent mutation discriminators, configured ruff/format/pyright, full `codex-check`, cite/CXA `overlay-check` where applicable, grounding/preflight/closeout and source/contract reviews. Every substantive source unit owes its actual bounded formal cycle with the required producer rows: authorship-dependent out-of-family review and all three lenses in pass 1, one fix round, pass 2 plus witness lens, qualifying single escalation, then pass 3 under the defined stop rule. Prep source GO and historical informal reviews do not supply those rows. Freeze the review inputs while a pass runs. No review or gate ran in this planning assignment.

Buford retains PR/push/integration ownership. Required final-PR/current-base CI, matching-head main landing, successful post-main CI, applicable terminating refresh/metadata/fixed-point closure and the separate installed Ollama/audit/signing/C-RT-38 witnesses remain owed. Historical combined48 is unverified; do not relabel it or turn retained author counts into independent gates. Source splitting does not expand live-device consent.

## Release

Only read-only Git/source/evidence inspection and owned plan/pins output occurred. No intermediate source file/ref/worktree/unit, test execution, installation, source/spec/marker edit, integration action, helper/provider/service/live operation or agent was created/run. Retained full Laws:Code/Chat/Prose governed architecture and reporting; the product shipping/pre-pass sizing and formal-cycle guidance were checked. Source remains clean at the pinned head. RELEASED/no processes or writer handles. Buford should first disposition this plan, then assign the released Claude author the Unit 1 hunk/test packaging and contract-fold venue explicitly.
