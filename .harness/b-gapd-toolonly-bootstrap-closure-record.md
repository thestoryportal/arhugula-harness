# B-GAPD-TOOLONLY-BOOTSTRAP — conditional provider ping for tool-only workflows

**Status:** CLOSED as stale-carry-text disposition. No code change owed; this is a documentation correction, not a build.

## 1. What the register asked for

Per `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §5 (Wave 4) and the arc-ledger's `anticipated_scope`, this arc was registered as a **Class-1 fork candidate** carrying a nameable **C9⊥C11** tension (fail-fast reliability vs. tool-only-workflow ergonomics): the `api.run` bootstrap allegedly pings ≥1 provider regardless of step kind (R-100 AC#2 `must_pass[3]` strict reading), so a tool-only workflow would pay an unnecessary provider dependency. The prescribed drive-to-gate was: file the Class-1 fork doc, run the probe (does a deferred-fail path already exist for a tool-only workflow that later needs a provider?), convene the dyadic council (C9 + C11) if the probe leaves it open, then take an operator-ratification AUQ.

## 2. The probe (run before any convening, per `[[probe-resolves-fork-prescribed-council]]`)

**Probe question:** if a tool-only workflow bootstraps with no provider, and a step later "turns out" to need inference, is a deferred-fail path already typed?

The probe resolved the tension immediately and unexpectedly: **the fork doc for this exact issue already exists and is marked RESOLVED.**

- `.harness/class_1_fork_api_run_unconditional_provider_ping_for_tool_only_workflows.md:3` — `**Status:** RESOLVED → **Reading B** (operator-ratified via AskUserQuestion 2026-06-12). Applied at runtime spec v1.46→v1.47 §2.1 + harness-runtime impl (same PR — bundled-absorption arc per root CLAUDE.md §11.4); clearance marker Spec_Harness_Runtime-v1_47-cleared-2026-06-12.md.`
- `gh pr view 515` — `{"mergedAt":"2026-06-11T23:40:36Z","state":"MERGED","title":"feat(R-CC-1): inference-conditional provider bootstrap — api.run provider-free for tool-only workflows (arc #4)"}`.
- `harness-runtime/tests/integration/test_r100_ac2_tool_step_e2e.py` carries **no `skipif` marker** (only historical narration inside its own docstring, describing the gate as already CLOSED) and passes green with zero provider credentials configured: `uv run pytest harness-runtime/tests/integration/test_r100_ac2_tool_step_e2e.py -q` → `1 passed in 1.29s`.

This is a full arc-cycle (PR #515, merged 2026-06-11) **before** R-FS-2 registered this exact issue as forward work — a textbook stale-carry-text disposition (`[[stale-carry-text-disposition-pattern]]`): the original B-10 residual bullet at `.harness/post-phase-8-forward-register.md` was never refreshed once the dedicated fork doc resolved, and R-FS-2's own registration inherited the stale framing.

## 3. Empirical re-verification of the shipped fix (not trusted from the fork doc's own claim)

- **Bootstrap conditional.** `harness-runtime/src/harness_runtime/bootstrap/stage_3a_cp_clients.py:31-59` — `if ctx.requires_inference: <construct providers> else: ctx.providers = {}`. A tool-only workflow's bootstrap performs zero provider construction and therefore zero provider ping.
- **Classification is static and exact.** `harness-runtime/src/harness_runtime/api.py:524-536` `_workflow_requires_inference()` returns `any(step.step_kind in _INFERENCE_STEP_KINDS for step in workflow.steps)`, reading the identical `workflow.steps` sequence the CP driver's frozen `{StepKind → StepDispatcher}` registry dispatches through. `StepKind` is a closed 7-value enum (`harness-cp/src/harness_cp/workflow_driver_types.py:69+`) with no dynamic step-kind-escalation mechanism — a workflow classified tool-only at bootstrap cannot later "turn out" to need inference, because the same static step list that decided the classification is what the driver dispatches against.
- **Deferred-fail path exists anyway, and is well-typed.** Even in the foreclosed hypothetical, `stage_5_loop_init.py:708-726` omits the `INFERENCE_STEP`/`SUB_AGENT_DISPATCH`/`POST_JOIN_SYNTHESIS` dispatcher rows entirely when `requires_inference` is False. A lookup against an omitted kind raises the typed `StepKindDispatcherNotBoundError` (`harness-cp/src/harness_cp/workflow_driver.py:401`), mapped by the CP driver to a clean `step-failure: RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND` — never a hang or crash. A second defensive layer (`_NoInferenceDispatcher` sentinel → `LLMDispatchBindError`, `llm_dispatch.py:154`) backstops a registry-binding defect that structurally can't be reached. Both layers are exercised by a contrasting-baseline test pair: `test_bootstrap_non_inference_omits_inference_dispatcher_rows` (`test_bootstrap.py:1497`) and `test_bootstrap_inference_with_no_providers_fails` (`test_bootstrap.py:1527`, confirming C9 fail-fast is preserved exactly where load-bearing — an inference-bearing workflow with zero providers still raises `BootstrapFailure`).

## 4. Disposition

No council convening was warranted — the probe collapsed the question before it reached that step, exactly as `[[probe-resolves-fork-prescribed-council]]` anticipates for an on-main invariant. This closes as a documentation correction:

- Arc-ledger `B-GAPD-TOOLONLY-BOOTSTRAP` row: `status: registered` → `status: closed`, `pr: "#515"` (the PR that actually shipped the fix, predating this registration).
- `snapshot`: `standalone_closed` 92→93, `standalone_registered` 2→1.
- `.harness/post-phase-8-forward-register.md` B-10 residual bullet: corrected from open-framing to `✅ RESOLVED 2026-06-12`, pointing at the fork doc's disposition and this record.
- `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §5 Wave 4 + §7 frozen order: B-GAPD entry struck through, marked closed pre-Wave-4, no build owed. Wave 4 reduces to the single remaining registered item, `B-19-BREAKER-AMBIENT-ATTRS`, with a single (not batched) operator AUQ.

No production code changed. No operator gate needed for this row.
