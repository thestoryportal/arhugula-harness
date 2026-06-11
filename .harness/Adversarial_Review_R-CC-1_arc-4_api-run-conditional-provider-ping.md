# Adversarial Review — R-CC-1 arc #4: `api.run` conditional provider-ping (runtime spec v1.47)

## Summary
- Mode: Phase-7 pre-merge bundled-absorption arc (design-substrate spec amendment + harness-runtime impl + tests, one PR; fork doc + clearance marker present — legitimate per root `CLAUDE.md` §11.4).
- Branch: `feat-r-cc-1-arc-4-api-run-conditional-provider-ping`
- Artifacts reviewed: `Spec_Harness_Runtime_v1.md` v1.47 §2.1; `api.py`; `bootstrap/{__init__,mutable_context,stage_3a_cp_clients,stage_5_loop_init}.py`; `lifecycle/providers.py`; the 6 test files; fork doc + clearance marker.
- **Class-number convention (per SKILL §title disambiguation):** findings use the **§4.1 review-severity** scale — Class 1 (Minor/drift) · Class 2 (Moderate/current-phase revision) · Class 3 (Severe/phase re-opening). This is the OPPOSITE of the §2.7.6 execution-fork scale. No §2.7.6 fork is triggered by this review.
- Finding count by class: Class 3: 0 · Class 2: 0 · Class 1: 2
- Highest-severity finding: F1-01 (spec §2.1 branch-3 cites a non-executing error symbol).
- **Disposition: APPROVE — clearance with two documentation-level inline fixes; no functional defect, no halt/fork warranted.**

---

## Class 3 findings (severe — phase re-opening)
None.

## Class 2 findings (moderate — current-phase revision)
None.

## Class 1 findings (minor — documentation drift)

### F1-01 — Spec §2.1 branch-3 cites `EmptyProviderCoverageError`, which never executes in the live bootstrap path
- **Location:** `design-substrate/Spec_Harness_Runtime_v1.md:2052` (§2.1 spec content, branch 3): *"≥1 provider client is constructed and passes an async ping, else stage 3a raises `EmptyProviderCoverageError` (→ `RT-FAIL-BOOTSTRAP`, fail-closed per ADR-F4)."*
- **Defect:** The live fail-closed guarantee for an inference workflow with zero providers does NOT flow through `EmptyProviderCoverageError`. That symbol is raised only by `materialize_capability_bindings` (`lifecycle/providers.py:891,907`), and `git grep` confirms `materialize_capability_bindings` is **never invoked anywhere in the live bootstrap path** (only defined + exported in `__all__`). The guarantee actually holds via two other guards: `ProviderNoneConfiguredError` (`providers.py:765`, inside `materialize_provider_clients_stage`, the byte-original ≥1 check) and `LLMDispatchBindError` (`stage_5_loop_init.py`→`llm_dispatch.py:1519`, `if len(providers)==0`). The spec body cites a code path that doesn't run; the change-note table + the bootstrap `__init__.py` docstring correctly name `ProviderNoneConfiguredError`, so the drift is internal to the §2.1 prose.
- **Discriminator:** (a) — affects substantive prose of the current-phase artifact (the named fail-closed mechanism is wrong), but resolution is self-contained to the §2.1 wording; (b)/(c) miss → drift only → Class 1.
- **Evidence:** `git grep materialize_capability_bindings -- harness-runtime/src` → only the `def` + the `__all__` line. `providers.py:765 raise ProviderNoneConfiguredError()`; `llm_dispatch.py:1519 if len(providers)==0: raise LLMDispatchBindError(...)`. The contrasting-baseline test `test_bootstrap_inference_with_no_providers_fails` raises `BootstrapFailure` via the `llm_dispatch.py:1519` path (it patches `materialize_provider_clients_stage` away), never via `EmptyProviderCoverageError`.
- **Resolution path:** Correct the §2.1 branch-3 error name to the actually-executing guard(s) (`ProviderNoneConfiguredError` / `LLMDispatchBindError`), or drop the specific symbol in favor of the generic `RT-FAIL-BOOTSTRAP` fail-class. Documentation-only; no code change.
- **Decision label:** *decided.*

### F1-02 — capability-completion inventory item #4 still reads as open-gap, not closed
- **Location:** `.harness/capability-completion-inventory-v1.md:42` — item #4 row still states the pre-fix gap ("The bootstrap pings ≥1 provider regardless of step kind, so the tool-only `api.run` e2e is skipif-gated…") with no RESOLVED/closed marker, though this arc closes it.
- **Defect:** The inventory is the R-CC-1 problem register; leaving item #4 reading as the live gap after the fix lands is a checkpoint-listed-as-open-but-already-applied shape (pattern-checklist item #4). Low-severity roadmap hygiene, not a spec/impl defect.
- **Discriminator:** (a/b/c) all miss for the design artifacts; this is `.harness/` process-substrate drift → Class 1.
- **Evidence:** inventory line 42 unchanged in the diff; the fork doc + clearance marker + spec §2.1 all record the closure, so the inventory row is the lone stale-carry.
- **Resolution path:** Mark inventory item #4 RESOLVED (or annotate "closed at arc #4 / v1.47") in this PR or the follow-on roadmap refresh. Documentation-only.
- **Decision label:** *decided.*

---

## Findings considered and rejected (transparency — what was attacked and held)

1. **Predicate exactness / no false negatives (claim 1) — HOLDS.** CP driver dispatch is statically keyed: `step_dispatchers.lookup(step.step_kind).dispatch(...)` (`workflow_driver.py:921`); registry `lookup` is a pure dict keyed on `step_kind` (`step_dispatchers.py:86`). Only INFERENCE_STEP/SUB_AGENT_DISPATCH are provider-backed. No TOOL→inference escalation exists (the only `ESCALATE_*` is validator→HITL). Additionally confirmed the TOOL_STEP dispatcher does NOT reach a provider internally: `runtime_tool_dispatcher.py`'s two `llm_dispatch` mentions are cost-attribution docstring mirrors, not provider calls; the tool/ memory-tool factories have zero provider/llm reach. Predicate is exact in both directions. Predicate unit test is exhaustive over all 5 StepKinds + mixed + empty-workflow.
2. **C9 fail-fast preserved (claim 2) — HOLDS.** Inference path is byte-unchanged: stage 3a `materialize_provider_clients_stage` (strict ≥1 via `ProviderNoneConfiguredError`, `providers.py` byte-original except 3 comment lines) + stage-5 `materialize_llm_dispatcher_stage` (`len(providers)==0` → `LLMDispatchBindError`). Two independent guards. `test_bootstrap_inference_with_no_providers_fails` exercises it (green).
3. **Sentinel unreachable (claim 3) — HOLDS.** `git`-wide search: ZERO `.dispatch(` call sites on `ctx.llm_dispatcher`/`ctx.sub_agent_dispatcher` outside the stage-5 binding itself; no consumer reads `ctx.llm_dispatcher` directly post-freeze. The only path to the sentinel (the `inference_step_dispatcher` facade, built at `stage_5:443`) is OMITTED from the registry when `not requires_inference`. `test_bootstrap_non_inference_omits_inference_dispatcher_rows` asserts the omission + `StepKindDispatcherNotBoundError` on lookup (green).
4. **Frozen-context invariant (claim 4) — HOLDS.** `types.py` byte-unchanged (`HarnessContext`, `_REQUIRED_FIELDS`, `LLMDispatcher` Protocol all untouched — no diff). The sentinel `async def dispatch(self, binding, step, *, step_context) -> Mapping[str, Any]` structurally satisfies the `LLMDispatcher.dispatch` Protocol; it is the *inner* core, wrapped by HITL+retry, so `ctx.llm_dispatcher` itself is the real `RetryBreakerFallbackDispatcher`. No C-RT-04 field-type widening. pyright strict 0/0/0 on all 5 changed src files.
5. **Non-inference branch provider-read safety — HOLDS.** `stage_5:134` reads `providers = ctx.providers` and raises only on `is None`; the non-inference branch sets `ctx.providers = {}` (empty dict, not None) → passes. `providers` is otherwise only passed into the now-guarded `materialize_llm_dispatcher_stage`. No other stage-5 surface consumes `ctx.providers`.
6. **resume() path (claim, advisor #5) — HOLDS, safe direction.** `resume(workflow: WorkflowObject, ...)` threads the predicate over the FULL `workflow.steps` (`api.py:822`), not the remaining suffix. No C9 false-negative possible; worst case is a harmless C11 over-count (provider required on resume whose remaining steps are tool-only). Correct/safe.
7. **Cross-spec + cross-plan drift (claim 5) — CLEAN.** Grepped IS/CP/OD/AS sibling specs + the runtime PLAN v2.42 + within-runtime-spec for "each client passes an async ping" / "≥1 provider" / the provider-coverage symbols. No sibling axis spec or the runtime plan cross-cites the stage-3a ≥1-provider invariant. All 4 in-spec occurrences are now v1.47-QUALIFIED (no unqualified stale carry inside the spec). (The lone unqualified occurrence is the inventory gap-statement → F1-02, expected.)
8. **Delta-only-spec convention — HOLDS.** v1.47 adds only §2.1 + two qualified C-RT-02 post-condition rows + the change-note; prior lineage preserved verbatim. No new contract number (C-RT-04/05/15/17 bodies untouched). Verified by diff.
9. **X-AL-3 anti-extension (SKILL's most load-bearing check) — HOLDS, this is the OPPOSITE of silent extension.** §2.1 is an operator-ratified Class-1-fork amendment: fork filed → AskUserQuestion (Reading B chosen 2026-06-12) → spec+impl+tests+clearance marker in one bundled-absorption PR. It refines *whether a provider is required*, not the multi-LLM commitment (ADR-F1 v1.2 untouched) and not a new H_T primitive. Clearance marker frontmatter is well-formed (artifact path + v1.47 + clearance_type + back_reference + reviewer_chain + merge_commit; `merge_commit: TBD` is the expected pre-merge placeholder filled at merge).
10. **Verification-shape grep-vs-e2e — SATISFIED.** Closure is proven by a discriminating contrasting-baseline pair (tool-only+0-providers → SUCCEEDS + TOOL_STEP dispatches; inference+0-providers → RAISES) run through the real `run_bootstrap`, plus the AC#2 e2e genuinely converted to provider-free (skipif + all live-provider/credential machinery removed) and green in CI. 75 tests pass on the touched suite; pyright 0/0/0.
11. **Spec/impl fidelity (claim 6) — HOLDS except F1-01.** §2.1 prose matches impl: skip-construction at stage 3a; sentinel core; registry-row omission; `StepKindDispatcherNotBoundError` backstop; HITL/retry wrappers + sub-agent chain still materialized. Only deviation is the F1-01 error-name.

---

## Disposition
**APPROVE.** No Class 2 or Class 3 findings. The arc is mechanically clean and faithfully implements operator-ratified Reading B: the C9 fail-fast guarantee is preserved exactly (two independent guards on the inference path; predicate exactness proven from both the dispatch-keying and internal-reach angles), the C-RT-04 frozen-context contract is byte-unchanged (sentinel satisfies it without type widening), and closure is proven by a discriminating contrasting-baseline test pair + a genuinely-converted provider-free AC#2 e2e. The two Class-1 findings are documentation-only inline fixes (§2.1 error-name drift; inventory item-#4 closure marker) carrying no functional risk and no halt/fork. Recommend landing with F1-01 + F1-02 fixed inline (or F1-02 in the follow-on roadmap refresh).

**Confidence:** HIGH — every load-bearing claim verified by direct code read AND execution (75 tests green, pyright 0/0/0), with the two findings grounded in `git grep` + line-resolved evidence; the single substantive finding (F1-01) is a non-executing-symbol citation, not a behavior defect.
