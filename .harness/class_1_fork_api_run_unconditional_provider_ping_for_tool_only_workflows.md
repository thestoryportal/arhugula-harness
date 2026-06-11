# Class 1 Fork — `api.run` bootstrap pings ≥1 provider regardless of step kind; tool-only workflows cannot run provider-free

**Status:** RESOLVED → **Reading B** (operator-ratified via AskUserQuestion 2026-06-12). Applied at runtime spec v1.46→v1.47 §2.1 + harness-runtime impl (same PR — bundled-absorption arc per root `CLAUDE.md` §11.4); clearance marker `Spec_Harness_Runtime-v1_47-cleared-2026-06-12.md`.
**Filed:** 2026-06-12 · **Posture:** mode-agnostic (back-flow documentation; no `harness-*/src` or `design-substrate/**` edit — those wait on the reading).
**Arc:** R-CC-1 capability-completion program, **arc #4** (`.harness/capability-completion-inventory-v1.md` item #4 / B-10 / R-100 AC#2).
**Cleared contract in tension:** `Spec_Harness_Runtime_v1.md` C-RT-04 stage-3a post-condition ("each client passes an async ping"; `ctx.providers` populated) + the stage-5 `LLMDispatchBindError` / provider-coverage `EmptyProviderCoverageError` ≥1-provider invariant.
**Nameable cross-domain tension:** **C9** `reliability-recovery` (fail-fast) ⊥ **C11** `operator-loop-local-deployment` (tool-only / local-first ergonomics).
**Grounded at HEAD `9b2392a5` by direct read this session** (cites resolved, not recalled).

---

## 1. The gap (what the inventory flagged)

The R-100 AC#2 tool-only e2e (`harness-runtime/tests/integration/test_r100_ac2_tool_step_e2e.py`) exercises a workflow whose **only** step is a `TOOL_STEP` (echo-MCP) — no inference. Yet the test is `pytestmark = skipif(not (_anthropic() or _ollama_up()))`: it cannot run without a live provider. Its docstring names the cause directly (**Gap D**):

> "the bootstrap constructs + pings ≥1 provider regardless of step kind, so the e2e needs a live provider."

So a capability the harness *advertises* — operator-facing `api.run` of a pure tool/declarative/HITL workflow — is, in practice, gated on a reachable LLM provider it never uses. AC#2 stays un-closeable in CI; tool-only local-first usage carries a phantom provider requirement.

## 2. Grounded state of the world (the probe that resolves the tension)

**Provider requirement is real and load-bearing — but only for inference.** The chain at HEAD:

| Fact | Site |
|---|---|
| Stage 3a constructs Anthropic/OpenAI/Ollama clients; **each passes an async ping**. `*_optional=True` permits per-provider degradation, but if **all** degrade to empty, `EmptyProviderCoverageError` raises — *"the stage-5 LLM dispatcher binding requires at least one provider."* | `stage_3a_cp_clients.py`; `lifecycle/providers.py:168-183` |
| The ping is **zero-token** — Anthropic = `models.list()` (non-inference), Ollama = `GET /api/tags` daemon check. **Not a paid call.** | `lifecycle/providers.py`; test `_ollama_up()`/`_anthropic()` |
| Stage 5 **unconditionally** binds the LLM dispatcher and raises `LLMDispatchBindError` if `ctx.providers` is empty/None — regardless of the workflow's step kinds. | `stage_5_loop_init.py:102-108` |

**The decisive probe (§10.9 #5 probe-first): is "needs inference" statically determinable from `workflow.steps`?** Yes — definitively:

- There are **5 fixed `StepKind`s**: `DECLARATIVE_STEP`, `INFERENCE_STEP`, `TOOL_STEP`, `HITL_STEP`, `SUB_AGENT_DISPATCH` (`harness_cp/workflow_driver_types.py:74-78`).
- Dispatch is **statically keyed on `step_kind`** via a frozen `{StepKind → StepDispatcher}` registry — `step_dispatchers.lookup(step.step_kind).dispatch(...)` (`workflow_driver.py:921`). **No dynamic TOOL→inference escalation exists** — the only "escalate" path is validator→HITL (`ESCALATE_HITL`, `workflow_driver.py:1036+`), not tool→LLM. Fallback chains are provider→provider *within* an inference call, never tool→inference.
- **Only `INFERENCE_STEP` and `SUB_AGENT_DISPATCH` reach a provider** (`INFERENCE_STEP → ctx.llm_dispatcher`, `SUB_AGENT_DISPATCH → ctx.sub_agent_dispatcher`, both built from `ctx.providers`; `step_dispatchers.py:15-17`). `DECLARATIVE_STEP` / `TOOL_STEP` / `HITL_STEP` never do.

**∴ a workflow needs ≥1 provider iff `any(s.step_kind in {INFERENCE_STEP, SUB_AGENT_DISPATCH} for s in workflow.steps)` — a pure, exact, static predicate over the same `workflow.steps` the driver dispatches (no false negatives possible).**

## 3. The tension — and why the probe resolves it

- **C9 (reliability-recovery / fail-fast)** *wants*: validate provider reachability at bootstrap so a workflow that will call inference fails fast (at PREAMBLE) rather than mid-run. The unconditional ping is the fail-fast guarantee.
- **C11 (operator-loop-local-deployment / local-first ergonomics)** *wants*: a tool-only workflow runs with **zero** provider config/reachability — no phantom LLM dependency for a pipeline that never infers.

**Probe-resolved (not a live council convening).** Because inference-need is *exactly* statically determinable and no TOOL_STEP can escalate, **conditioning the provider requirement on the static predicate gives C9 everything real it protects** (inference/sub-agent workflows still require ≥1 provider at bootstrap — fail-fast fully preserved) **and** C11 its ergonomics (tool-only workflows run provider-free). The bootstrap ping never protected anything for a tool-only workflow — it guarded an inference call that workflow never makes. The two voices **agree** once the static-determinability fact is on the table; spinning up a multi-agent council to watch them agree is the hollow-council failure mode (`CLAUDE.md` §10.9 #1). Voice positions are named here in lieu of a convening.

**Residual C9 note (honest):** under Reading B, an inference step dispatched in a workflow derived as `requires_inference=False` would fail at *dispatch* (`StepKindDispatcherNotBoundError`), not at bootstrap. This is **unreachable** — the predicate reads the same `workflow.steps` the driver dispatches — so it is a fail-loud backstop, not a fail-fast regression.

## 4. Readings

| # | Reading | Behavior | C9 / C11 | Cost |
|---|---|---|---|---|
| **A** | **Status quo — unconditional ≥1-provider ping** | No change. Tool-only `api.run` stays gated on a live provider; AC#2 e2e stays `skipif`. | C9 ✓ (over-broad) / C11 ✗ | none (do-nothing) |
| **B (RECOMMENDED)** | **Conditional on the static inference predicate** | `run()` derives `requires_inference = any(step_kind ∈ {INFERENCE_STEP, SUB_AGENT_DISPATCH})`; threads it into `run_bootstrap`. When `False`: stage-3a tolerates empty `ctx.providers` (no `EmptyProviderCoverageError`), stage-5 skips binding the LLM + sub-agent dispatchers (those registry rows stay unbound → fail-loud if ever dispatched). When `True`: today's behavior verbatim (≥1 provider required at bootstrap). | **C9 ✓ (fully preserved)** / **C11 ✓** | Multi-stage arc: `run()` predicate + `run_bootstrap` kwarg + stage-3a/stage-5 conditionals + C-RT-04 spec amendment + clearance. Mechanically clean. |
| C | **All-optional / degraded-allow** | Allow zero-provider bootstrap unconditionally (all providers optional → empty `ctx.providers` never raises); an `INFERENCE_STEP` fails at *dispatch* if no provider. | C9 ✗ (fail-fast lost for inference workflows) / C11 ✓ | Smaller code change, but sacrifices C9 fail-fast even for genuine inference workflows. |

## 5. Recommendation

**Reading B.** It is the only reading that satisfies *both* voices with no real loss: C9's fail-fast is preserved exactly where it matters (inference/sub-agent workflows), and C11's tool-only ergonomics are freed. It is buildable cleanly (the predicate is exact; the fail-loud guard is free via the unbound registry rows). It closes R-100 AC#2 (the e2e drops its `skipif` for tool-only and runs unconditionally in CI) and unblocks arc #4→#8 (P3 live multi-tier e2e composes on top).

**Not A** (leaves an advertised capability phantom-gated + AC#2 permanently un-closeable in CI). **Not C** (discards C9 fail-fast for real inference workflows to save a predicate — the static determinability makes that trade unnecessary).

Reading B amends a cleared contract (C-RT-04 stage-3a "each client passes an async ping" → "...for inference-bearing workflows"), so it is **design-fork-first (X-AL-3)**: runtime-spec amendment + clearance marker before/with impl.

## 6. Disposition

- **RESOLVED → Reading B.** Operator chose "Reading B (Recommended)" via AskUserQuestion 2026-06-12.
- **Applied (this PR, bundled-absorption):** runtime spec v1.46→v1.47 NEW §2.1 (inference-conditional provider materialization: the `requires_inference` predicate + `run()`/`resume()` derivation + `run_bootstrap` threading + the conditional stage-3a coverage / stage-5 binding + the `StepKindDispatcherNotBoundError` fail-loud backstop) + the two C-RT-02 post-condition qualifications. Impl: `run()`/`resume()` predicate + `run_bootstrap(requires_inference=…)` threading + stage-3a empty-providers tolerance + stage-5 conditional LLM/sub-agent dispatcher binding. The R-100 AC#2 tool-only e2e drops its `skipif` on the provider-free path. Clearance marker `Spec_Harness_Runtime-v1_47-cleared-2026-06-12.md`.
- **Closure proof:** contrasting-baseline test (tool-only + zero providers → bootstrap SUCCEEDS + TOOL_STEP dispatches; inference + zero providers → bootstrap RAISES `RT-FAIL-BOOTSTRAP`) + the now-unconditional tool-only AC#2 e2e.
