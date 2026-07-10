---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.96
cleared_at: 2026-07-10T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - .harness/u1-slice3-findings-and-f1-c10-gap.md (F1 finding — the gap this slice closes)
  - .harness/u1-slice3a-c10-reconfirmation.md (C10 blast-radius re-confirmation for the downgrade)
  - .harness/u1-slice1-c10-blast-radius-verdict.md (slice-1 C10 verdict — condition 2 now materialized)
  - .harness/post-phase-8-forward-register.md (B-18 / U-1)
  - PR (U-1 slice 3a, branch u1-slice3a-child-frozen-tool-superset-f1)
merge_commit: (squash-merge of the U-1 slice-3a PR)
reviewer_chain:
  - decorrelated advisor (transcript-aware) — broke the Option-A-vs-B tie toward the per-call StepExecutionContext carrier; flagged the wrapper-stack propagation witness (grep-confirmed)
  - out-of-family just codex-review (gpt-5.5, subscription) — caught + fixed the empty-child payload.tools fallback [P2]
  - main-agent artifact review (dispatch seam + stage-5 dual compute + CP threading across 5 fresh construction sites)
---

# Clearance — `Spec Harness Runtime v1.96`

v1.96 materializes **U-1 slice 3a** (forward register B-18) — the **child-scoped (descended sub-agent) frozen tool superset**, closing the **F1 latent C10 condition-2 gap** the slice-3 design pass surfaced in the merged slice 1. A child workflow reused the parent `ctx.step_dispatchers` → the parent `RuntimeLLMDispatcher` with the parent's `frozen_tool_superset`, so a sub-agent inference emitted the PARENT's full superset (a visibility-only leak — execution stays registry/trust/sandbox/effect-fence-gated — latent because both supersets are `None` at MVP with no MCP tools).

**Mechanism (ADR-D4 §1.5 REMOVE half, per-call route).** `compute_frozen_tool_superset(..., remove_tiers)` filters `ToolContract.blast_radius_tier ∈ remove_tiers` at compute-time; the child policy `CHILD_DOWNGRADE_REMOVE_TIERS = {EXTERNAL_IRREVERSIBLE}` (only REMOVE — `local-mutation`/`external-reversible` stay VISIBLE, the latter's DOWNGRADE_TO_ASK being a gate-level not visibility concern). Stage 5 binds BOTH the full `frozen_tool_superset` and the downgraded `child_frozen_tool_superset` on the bare `RuntimeLLMDispatcher`; `dispatch()` selects the child superset when `step_context.sub_agent_descent` is True. Empty-child disambiguation (out-of-family Codex [P2]): a descended child in a run that HAS MCP tools whose downgraded union is empty emits `tools: []`, NEVER the `payload.tools` fallback (which would re-expose the removed tool). The descent marker is the paired CP `StepExecutionContext.sub_agent_descent` carrier (CP spec v1.86), threaded by `execute_workflow(sub_agent_descent=...)` onto every step context (linear + 5 non-linear strategies; branch children inherit via `compose_branch_child_context` model_copy); `child_workflow_runner` re-enters with `True`. `ProviderAgnosticPayload` FROZEN (ADR-F1); OpenAI/Ollama untouched; both supersets `None` at MVP → byte-identical.

**Verification.** pyright 0/0/0 on all touched files; ruff+format clean; 9 slice-3a tests (compute-level REMOVE filter + idempotent-uniform-descent + empty-when-all-removed + memory-retained; dispatch-level: top-level emits T / descended child omits T while keeping the other three tiers / **the Codex-[P2] regression: descended-all-removed sends `tools: []` not the declared removed tool** / top-level contrast); **full `harness-runtime/tests/` non-e2e = 2327 passed** + **full `harness-cp/tests/` non-e2e = 1474 passed** (0 failures — the CP `sub_agent_descent` threading across 5 fresh construction sites + 789 topology tests regression-clean). Wrapper-stack propagation grep-confirmed (facade / retry-breaker / HITL composer all forward the identical `step_context` unchanged); the heavy full-bootstrap-with-MCP-echo e2e is the noted residual (proportionate given latent/None-at-MVP).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Slice 3b (cacheable-epoch primitive) + slice 3c (ADR-D4 §1.8 PARALLELIZATION concurrent-cache pre-warm) remain registered follow-ons at B-18.
- See `.harness/clearance/README.md` for marker discipline.
