---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.47
cleared_at: 2026-06-12T18:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork (bundled-absorption — spec + impl + tests)
back_reference:
  - .harness/class_1_fork_api_run_unconditional_provider_ping_for_tool_only_workflows.md (Class-1 fork — Reading B, operator-ratified 2026-06-12)
  - .harness/capability-completion-inventory-v1.md (R-CC-1 arc #4 / item #4 / B-10 / R-100 AC#2)
  - PR (R-CC-1 arc #4 — this arc) — TBD at PR creation
merge_commit: TBD-at-PR-merge
reviewer_chain:
  - advisor (pre-build, full transcript) — required the probe-first discriminator (is inference-need statically determinable?) BEFORE convening a council; on the probe resolving the C9⊥C11 tension, ruled the genuine multi-agent council hollow (§10.9 #1 collapse) and endorsed naming the voice positions in the fork; sharpened Reading B to key on StepKind (not model-binding presence), thread requires_inference, and confirm the EmptyProviderCoverageError/stage-5 sites can be made conditional cleanly without breaking downstream stages
  - empirical grounding passes — 5 StepKinds, dispatch statically keyed via the frozen {StepKind → StepDispatcher} registry (no TOOL→inference escalation); only INFERENCE_STEP + SUB_AGENT_DISPATCH reach a provider; stage 3b CP_ROUTING + every pre-line-197 stage-5 factory are provider-agnostic; ONLY stage_5_loop_init.py:197 reads ctx.providers; llm_dispatcher non-optional + in _REQUIRED_FIELDS → sentinel keeps C-RT-04 + _REQUIRED_FIELDS byte-unchanged
  - impl-time green — predicate units (9 cases) + 2 full-bootstrap integration tests (registry-omission + contrasting baseline) + the AC#2 e2e converted to provider-free/unconditional; full harness-runtime suite green; pyright strict 0/0/0; ruff clean
  - out-of-family Codex (pre-merge, decorrelated) — caught a genuine P1: the first-cut `require_coverage` approach only suppressed the FINAL empty-provider check, so a tool-only `api.run` with the DEFAULT config (`*_optional=False`) + no credentials still hard-failed in stage 3a per-provider construction. Fix: stage 3a now SKIPS provider construction entirely when `not requires_inference` (no construction failure of any kind can abort a tool-only bootstrap); the `require_coverage` param was reverted (composer unchanged)
  - harness-adversarial-reviewer (pre-merge) — TBD at PR
  - advisor (pre-done) — TBD at PR
---

# Clearance — `Spec_Harness_Runtime_v1.md v1.47`

v1.47 makes the **bootstrap provider requirement conditional on the workflow being inference-bearing** (R-CC-1 capability-completion **arc #4**; Class-1 fork `.harness/class_1_fork_api_run_unconditional_provider_ping_for_tool_only_workflows.md`, operator-ratified **Reading B**). Closes the gap that a tool-only `api.run` workflow (no inference) could not bootstrap provider-free: stage 3a constructed + pinged ≥1 provider regardless of step kind (the ping is zero-token — Anthropic `models.list()` / Ollama `GET /api/tags` — but a reachable provider was still *required*), so the R-100 AC#2 tool-only e2e was `skipif`-gated on a live provider it never used. NEW **§2.1** authors the `requires_inference` predicate + the inference-conditional provider/dispatcher materialization contract + the fail-loud backstop, plus two C-RT-02 post-condition qualifications. `C-RT-04` / `C-RT-05` / `C-RT-15` / `C-RT-17` contract bodies, `§14.x`, and all prior lineage PRESERVED VERBATIM (no new contract number).

**What was reviewed.** The C9⊥C11 tension (fail-fast reliability ⊥ tool-only/local-first ergonomics) was flagged dyadic-council-eligible by the inventory, but advisor's §10.9-#5 probe-first ruled the council hollow: inference-need is **exactly statically determinable** from `workflow.steps` (only `INFERENCE_STEP` + `SUB_AGENT_DISPATCH` reach a provider; dispatch is statically keyed via the frozen `{StepKind → StepDispatcher}` registry — `workflow_driver.py:921`; no TOOL→inference escalation, the only "escalate" is validator→HITL), so conditioning the requirement on that predicate preserves C9 fail-fast **fully** (inference workflows still require ≥1 provider at bootstrap) while freeing C11 (tool-only workflows bootstrap provider-free). C9 loses nothing real — the bootstrap ping only ever protected an inference call a tool-only workflow never makes. Voice positions were named in the fork in lieu of a convening.

**Impl (runtime-only; CP/IS byte-unchanged).** `run()`/`resume()` derive `requires_inference = any(step.step_kind ∈ {INFERENCE_STEP, SUB_AGENT_DISPATCH})` (exact — reads the same `workflow.steps` the driver dispatches → no false negatives) and thread it into `run_bootstrap`; **stage 3a skips provider construction entirely when `not requires_inference`** (a tool-only workflow needs no provider — no per-provider construction failure of any kind can abort the bootstrap, regardless of the operator's `*_optional` flags), leaving `ctx.providers` empty; the provider composer (`materialize_provider_clients_stage`) is byte-unchanged (still strict ≥1 for the inference path); stage 5 binds a fail-loud `_NoInferenceDispatcher` sentinel as the LLM-dispatch core (the only stage-5 surface consuming `ctx.providers`) when `not requires_inference` and **omits the INFERENCE_STEP / SUB_AGENT_DISPATCH registry rows** → `StepKindDispatcherNotBoundError` backstop. The sentinel keeps the non-optional `C-RT-04` carrier fields + `_REQUIRED_FIELDS` + `_bound` byte-unchanged (minimal cleared-contract blast radius — no C-RT-04 field-type widening).

**Caveats for Phase 7 consumers.**
- **C9 fail-fast is preserved exactly.** Every workflow that *can* dispatch an inference/sub-agent step requires ≥1 reachable provider at bootstrap; no workflow that *cannot* does. Predicate exactness means there is no workflow taking the provider-free branch that then dispatches inference.
- **No-op-binding skip mechanism.** Stage 5 still materializes the HITL/retry wrappers + the sub-agent chain around the sentinel core (cheap, provider-free) but the registry omits their rows, so they are unreachable. This is the §2 "deferred to implementation discretion" skip-mechanism choice — it keeps the cleared `C-RT-04` field types non-optional.
- **The provider ping mechanism (C-RT-05) is unchanged** — only *whether ≥1 is required* becomes conditional.
- **R-100 AC#2 closed.** The tool-only e2e drops its `skipif` and runs provider-free in CI (no live provider, no paid call). The live-provider paths remain covered by the r300 / r-pm-1 skipif-gated e2e suite.

## Notes

- Phase 7 consumers may rely on v1.47 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
- `merge_commit` + the final PR back-reference + the pre-merge Codex/adversarial/advisor reviewer rows are filled at PR creation/merge.
