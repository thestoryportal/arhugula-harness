---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.40
cleared_at: 2026-06-01T12:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_tool_step_no_operator_supplied_converter.md (RATIFIED-AS-READING-B 2026-06-01; this apply arc)
  - .harness/class_1_fork_tool_step_no_bootstrap_sandbox_decision_resolver.md (sibling gap surfaced + filed at this arc; PROPOSING)
  - PR #169 (converter fork ratification)
  - PR (this apply arc — TBD at PR creation)
merge_commit: TBD-at-PR-merge
reviewer_chain:
  - use-the-product probe (R-100-mvp-real-workflow-execution, 2026-05-31) — surfaced the converter gap
  - operator AskUserQuestion ratification 2026-06-01 (Reading B — per-server default tool-contract policy; PR #169)
  - advisor (apply-arc pre-substantive — field-shape +2-as-ratified discipline + tier-floor warning) + advisor reconcile call (resolver-gap discovery — converter-necessary-but-not-sufficient)
  - spec-writer apply pass (this arc — Reading B absorption into §14.9.3 stage-3a body + change-note)
  - impl-time grounding pass (1344/1344 harness-runtime non-e2e tests pass + 1 xfail AC#2 marker; pyright strict + ruff clean on touched files)
---

# Clearance — `Spec_Harness_Runtime_v1.md v1.40`

v1.40 absorbs the Class 1 fork resolution **Reading B** of `class_1_fork_tool_step_no_operator_supplied_converter.md` (operator-ratified 2026-06-01, PR #169). The stage-3a `materialize_mcp_client_host_stage` factory contract (§14.9.3) is extended: for a configured MCP server, the factory MUST build a default-policy `MCPToolContractConverter` from two new operator-declared `MCPClientConfig` fields (`default_minimum_tier: SandboxTier` + `default_blast_radius: BlastRadiusTier`, conservative defaults `TIER_2_CONTAINER` / `READ_ONLY`) and pass it to the `MCPClientHost` constructor. This closes the converter half of the operator `api.run` TOOL_STEP path — previously the bootstrap-built host carried only the raise-on-every-call default converter and operators had no config surface to supply one. Spec body PRESERVED VERBATIM except the §14.9.3 stage-3a paragraph (v1.40 Reading B clause appended). Field count ratified at +2 per fork §3.

What was reviewed: the converter gap was surfaced empirically by the R-100 use-the-product probe (a TOOL_STEP cannot dispatch via `api.run`); operator ratified Reading B over A/C/D; the apply arc applied the +2 field shape faithfully (advisor confirmed not re-deciding the contract to +1 despite the pre-existing unconsumed `blast_radius` overlap). Impl co-published: `MCPClientConfig` +2 fields; `mcp_client_host_factory._build_default_policy_converter`; 5 converter unit tests; full harness-runtime non-e2e suite green (1344 passed).

**Caveats for Phase 7 consumers (IMPORTANT — converter half only):** v1.40 is **necessary but NOT sufficient** to dispatch a TOOL_STEP via `api.run`. A sibling gap surfaced at the apply arc: the bootstrap-built `RuntimeToolDispatcher` has no `sandbox_decision_resolver` (defaults-to-raise; the factory wires none), so dispatch raises at `runtime_tool_dispatcher.py:449` BEFORE the tier-floor check. That gap is an un-ratified design surface (implementer-discretion §14.9.7 vs operator-policy parity-with-converter) filed as `class_1_fork_tool_step_no_bootstrap_sandbox_decision_resolver.md` (PROPOSING). **R-100-mvp-real-workflow-execution AC #2 remains BLOCKED after v1.40.** A deterministic xfail marker lives at `test_u_rt_75_runtime_tool_dispatcher_factory.py::test_ac2_bootstrap_dispatcher_resolves_sandbox_decision`. Class 3 adjacent finding (not patched): the pre-existing unconsumed `MCPClientConfig.blast_radius` overlaps the new `default_blast_radius`; consolidation owed at a future hygiene arc per X-AL-3.

## Notes

- Phase 7 consumers may rely on v1.40 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
- The §14.9.3 **stage-5** factory body (`materialize_runtime_tool_dispatcher_stage`) is PRESERVED VERBATIM at v1.40 — not amended; it is the resolver fork's territory.
