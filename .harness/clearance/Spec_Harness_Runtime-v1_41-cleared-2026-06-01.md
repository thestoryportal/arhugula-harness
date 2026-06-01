---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.41
cleared_at: 2026-06-01T18:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_tool_step_no_bootstrap_sandbox_decision_resolver.md (APPLIED-AS-READING-B 2026-06-01)
  - PR (AC#2-closing arc — TBD at PR creation)
  - .harness/clearance/Spec_Harness_Runtime-v1_40-cleared-2026-06-01.md (Gap A / converter, prerequisite)
merge_commit: TBD-at-PR-merge
reviewer_chain:
  - execution-backed gap investigation (4-agent workflow, 2026-06-01) — found the 5-gap set {D,B,C,E,F} + verified §14.9.7 phantom (a scratch run wired all five + completed a real TOOL_STEP)
  - operator AskUserQuestion ratification 2026-06-01 (Gap C → Reading B per-server sandbox-mechanism fields; e2e → config-around / skipif-gated)
  - advisor (pre-authoring — live tier-floor under Reading B; ground §14.9.x against the code carrier; faithful-minimal +3 fields; per-server-uniform honesty note; ollama-or-key e2e gate)
  - spec-writer apply pass (this arc — NEW §14.9.8 + change-note)
  - impl-time grounding pass (1355/1355 harness-runtime non-e2e tests pass + 1 e2e skip; pyright strict + ruff clean on touched files)
---

# Clearance — `Spec_Harness_Runtime_v1.md v1.41`

v1.41 authors the **NEW §14.9.8 sandbox-decision-resolver contract** per the AC#2-closing-arc fork (`class_1_fork_tool_step_no_bootstrap_sandbox_decision_resolver.md`, operator-ratified **Reading B**, 2026-06-01). It is the missing spec anchor for the `SandboxDispatchDecision` carrier + `SandboxDecisionResolver` callable the runtime has carried since v1.13 with **phantom §14.9.7 cites** (an execution-backed completeness investigation verified §14.9.7 defers only emitter-mutation / idempotency / health-check — never the resolver; the phantom code cites at `runtime_tool_dispatcher.py:85,:98` are corrected at impl). §14.9.8 declares the 5-field carrier (grounded field-for-field against the code), the resolver type, and the stage-5 factory's obligation to build a per-server default-policy resolver from `MCPClientConfig.{default_sandbox_tier, default_sandbox_tech, default_sandbox_provider}` (impl-declared +3 fields, faithful-minimal). Under Reading B the §14.9.4 tier-floor is **LIVE** (resolved `tier` is independent of `minimum_tier`); §14.9.8 documents the per-server-tier-consistency requirement and the per-server-uniform scope (per-tool granularity is future). v1.40 + earlier lineage PRESERVED VERBATIM.

What was reviewed: the gap set was established by execution (a 4-agent investigation + scratch run found {D,B,C,E,F} — five gaps, vindicating the non-falsifiable framing); the operator ratified Reading B over the recommended identity resolver (Reading A) for a meaningful floor; the apply faithfully added exactly the 3 ratified fields. Impl co-published: §14.9.8 resolver wiring (Gap C), stage-3a `host.start()` (Gap B), emitter `info_lookup` from host (Gap E), `host.shutdown()` in shutdown.py (Gap F), + 18 new CI-green unit/integration tests + a skipif-gated echo-MCP-via-`api.run` TOOL_STEP e2e. 1355/1355 harness-runtime non-e2e tests pass.

**Caveats for Phase 7 consumers — AC #2 is wired but NOT yet proven closed.** v1.41 + the co-published impl wire the full bootstrap TOOL_STEP path, but **R-100 AC #2 closes only on an operator's live run** of the e2e (`test_r100_ac2_tool_step_e2e.py`): Gap D (provider-construction precondition) means the e2e needs a live provider (ollama daemon OR `ANTHROPIC_API_KEY`), so it is skipif-gated and skips in CI. The harness does not fire a paid call autonomously. The wiring is proven by 18 CI-green unit/integration tests (resolver, info_lookup, config fields, stage-3a start, shutdown drain) + a one-time execution-confirmed scratch run during investigation — but the canonical end-to-end proof is the operator's live-green run. Per-server-uniform: one floor per server (a read-only and a destructive tool on one server share it); per-tool granularity is a future arc.

## Notes

- Phase 7 consumers may rely on v1.41 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
- Prerequisite: `Spec_Harness_Runtime-v1_40-cleared-2026-06-01.md` (Gap A converter config surface).
- §14.9.7 is PRESERVED VERBATIM — it correctly defers emitter/idempotency/health-check; only the code's mis-cite *to* it was phantom (fixed at impl).
