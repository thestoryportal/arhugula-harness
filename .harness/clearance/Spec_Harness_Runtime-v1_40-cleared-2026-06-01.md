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

**Caveats for Phase 7 consumers (IMPORTANT — one necessary piece, NOT a sufficient set):** v1.40 delivers the converter **config surface** only. It does NOT make a TOOL_STEP dispatchable via `api.run`, and the remaining-gap list is **not asserted complete** (a pre-merge completeness critic undercounted twice). Known open gaps: **(B)** the stage-3a bootstrap body never calls `host.start()` (`stage_3a_cp_clients.py:48`), so the registry is empty and the v1.40 converter is currently *unreachable* through the bootstrap — green `_FakeTool` unit tests prove the converter function, not the path; **(C)** the bootstrap `RuntimeToolDispatcher` has no `sandbox_decision_resolver` (defaults-to-raise at `runtime_tool_dispatcher.py:449`, before the tier-floor check). A gap **(D)** candidate (bootstrap provider construction for a tool-only workflow) is unresolved. **R-100-mvp-real-workflow-execution AC #2 closes only when the full bootstrap TOOL_STEP path is wired AND demonstrated end-to-end (echo MCP via `api.run`) — proven by execution, not unit tests.** Gap C (design decision) is filed at `class_1_fork_tool_step_no_bootstrap_sandbox_decision_resolver.md` (PROPOSING) §1-§3; Gap B (impl) is documented at that fork §5 and lands in the same closing arc. A deterministic xfail marker for Gap C lives at `test_u_rt_75_runtime_tool_dispatcher_factory.py::test_ac2_bootstrap_dispatcher_resolves_sandbox_decision`. Class 3 adjacent finding (not patched): the pre-existing unconsumed `MCPClientConfig.blast_radius` overlaps the new `default_blast_radius`; consolidation owed at a future hygiene arc per X-AL-3.

## Notes

- Phase 7 consumers may rely on v1.40 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
- The §14.9.3 **stage-5** factory body (`materialize_runtime_tool_dispatcher_stage`) is PRESERVED VERBATIM at v1.40 — not amended; it is the resolver fork's territory.
