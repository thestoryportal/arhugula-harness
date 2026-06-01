# Class 1 fork — per-dispatch cost-attribution does not fire on a real `api.run` inference workflow

**Status:** PROPOSING — awaiting operator ratification (root-cause debug + OD-5 retirement-validity review).
**Filed:** 2026-05-31, during R-100-mvp-real-workflow-execution use-the-product probe (live 3-step Anthropic run).
**Class:** 1 (a landed substitution surface — H_T-OD-5 cost-attribution, RETIRED batch-32 — does not produce its contracted output on the production path; the retirement may rest on a grep-vs-e2e verification gap).
**Blocks:** R-100-mvp-real-workflow-execution AC #4 ("cost-attribution entries present"). Does NOT block AC #1 / AC #3.

---

## 1. The defect (empirically confirmed)

A real 3-step INFERENCE workflow run through `api.run` against the live Anthropic provider (`claude-haiku-4-5`, `harness-runtime/tests/integration/test_r100_real_workflow_e2e.py`, 2026-05-31) wrote **zero `cost:`-prefixed entries** to the audit ledger. The observed `action_id`s were exactly:

```
audit:_single:<hash>      (×3 — workflow audit)
workflow:wf-r100-real:step:0
workflow:wf-r100-real:step:1
workflow:wf-r100-real:step:2
```

No `cost:` entry for any of the 3 inference dispatches. (The R-100-mvp-operator-usable-cli-shipped live smoke — a single inference step — showed the same absence.)

## 2. Why this is surprising (the wiring exists)

- `RuntimeLLMDispatcher.dispatch` calls `_attribute_cost_best_effort(...)` at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:517` on every dispatch, after extracting Anthropic usage at `_dispatch_anthropic` (usage → `input_tokens`/`output_tokens`, llm_dispatch.py:786-788).
- The cost substrate is bound to the dispatcher at bootstrap stage 5: `cost_chain` + `audit_writer` + `rate_table=RATE_TABLE_V1` are passed at `stage_5_loop_init.py:147-149`; stage 5 hard-asserts `ctx.cost_chain` / `ctx.audit_writer` non-None (`:123-125`).
- `RATE_TABLE_V1` covers `claude-haiku-4-5` (`harness-od/src/harness_od/rate_table_v1.py:55`) — so it is not a rate-table-miss.
- The audit-writer writes through `ctx.ledger_writer` (same state-ledger substrate where the `audit:_single` + `workflow:...:step:N` entries DID land) — so a written `cost:` entry would be observable in the same place. It was not.

So cost-attribution is wired end-to-end but produces nothing on the real dispatch path.

## 3. Candidate root causes (one focused debug arc)

`_attribute_cost_best_effort` silently returns / swallows in three cases (llm_dispatch.py:930-959):
1. **`input_tokens` or `output_tokens` is None** (line 934) — the Anthropic response's `usage` not extracted into `usage_attrs` at the workflow dispatch path. (Most likely candidate; needs a live assertion of `usage_attrs` values.)
2. **The workflow dispatch path does not reach `RuntimeLLMDispatcher.dispatch`** — the workflow calls `SyncDispatcherFacade(ctx.llm_dispatcher)` where `ctx.llm_dispatcher` is the `RetryBreakerFallbackDispatcher` wrapper (`stage_5_loop_init.py:274`); if the wrapper routes to a dispatch method that bypasses the line-517 cost block, cost never fires.
3. **`attribute_llm_dispatch_cost(...)` raises and is swallowed** (line 958 `except Exception`) — cost-attribution is "observability, not contract," so any failure is silent.

A focused debug (add a non-swallowing probe at the three branch points, or a single live run asserting `usage_attrs`) discriminates in minutes.

## 4. Retirement-validity implication (the load-bearing finding)

H_T-OD-5 (cost-attribution) was RETIRED at batch-32 via mechanism-β tests (`u-od-39-tool-dispatch-cost-attribution` / `u-od-40-validator-webhook-cost-attribution`, both LANDED). Those tests exercise the cost helpers / dispatch sites in isolation. The **production `api.run` inference path emits no cost** — exactly the `[[verification-shape-sharpened-grep-vs-e2e]]` gap ("grep-for-presence / unit-pass ≠ verified-working-end-to-end"). The OD-5 RETIRED claim should be re-examined against this real-run evidence: either (a) the defect is LLM-path-specific and the tool/webhook paths (which retired OD-5) do fire, or (b) OD-5's retirement rests on tests that don't cover the production emission path.

## 5. Resolution path

- Debug per §3; fix the LLM-path cost emission (likely usage-extraction or dispatch-method routing).
- Re-validate OD-5: run a real tool-dispatch + webhook-dispatch through their production paths and confirm `cost:` entries; if absent there too, OD-5 → re-open.
- The R-100 e2e test (`test_r100_real_workflow_e2e.py`) carries AC #4 as a runtime `pytest.xfail` citing this doc; it auto-converts to a passing regression guard once the fix lands.

## 6. Tracking

Roadmap: R-100-mvp-real-workflow-execution AC #4 + a follow-on R-NNN if ratified. Sibling to `class_1_fork_tool_step_no_operator_supplied_converter.md` (AC #2) — both surfaced by the same R-100 real-workflow probe.
