---
artifact: design-substrate/Spec_Action_Surface_v1.md
version: v1.13
cleared_at: 2026-07-12T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/arc-ledger.yaml (B-TOOL-SEARCH-RUNTIME entry)
  - .harness/r-fs-2-final-closure-implementation-plan-v1.md (B-TOOL-SEARCH-RUNTIME grounding-first branch)
  - ADR-D3 v1.2 §1.1 (primitive #2 MCP-as-code — tool_search lazy-loading facet)
  - ADR-D3 v1.2 §1.5 (cache-prefix integrity discipline — "per-MCP capability discovery via tool_search rather than tools[] mutation")
merge_commit: pending (pre-merge at filing time)
reviewer_chain:
  - Grounding pass — AS spec §13.2 adoption-depth matrix read live (r/o/R/r, no cell X — the literal "close if deferred/not-adopted" branch does not fire)
  - advisor() — two rounds; first round mis-read the frozen superset as already satisfying the tool_search facet, second round corrected: the plan names a concrete build shape and §13.6's discretion clauses do not cover tool_search
  - Phase 7 impl grounding — confirmed no existing search/query surface on ToolRegistry or MCPClientHost; confirmed SkillActivationMode.TOOL_SEARCH is a distinct, already-built, unrelated mechanism (Skill activation, not MCP capability discovery)
  - just codex-review pre-merge (§13.1 out-of-family review)
---

# Clearance — `Spec_Action_Surface v1.13`

v1.13 is the B-TOOL-SEARCH-RUNTIME build arc (R-FS-2 Wave 2). New §13.7 commits a minimal `search_tools` capability-discovery contract realizing the ADR-D3 §1.1 primitive-#2 `tool_search` facet that was previously unbuilt: a `defer_names` parameter on the frozen-superset computation that omits selected MCP tools from the eager `tools[]` union, a single static `search_tools` stub entry appended when any tools are deferred, and a deterministic (substring, sorted-by-name) search dispatch that returns deferred tools' full schemas as an ordinary tool result — never as a `tools[]` mutation. The cache-prefix invariance property (§13.7 point 4) is the acceptance witness: `compute_frozen_tool_superset(...)` bytes are identical before and after any number of `search_tools` dispatches within an epoch.

The grounding for this arc took two passes. §13.2's adoption-depth matrix (r/o/R/r for MCP-as-code, no workload-class cell excluded) does not literally satisfy the plan's "close if depth is deferred/not-adopted for every live cell" condition, so a first-pass close-with-evidence disposition (reasoning that the pre-existing frozen superset already satisfied ADR-D3 §1.5's no-mutation clause) was reconsidered and reversed: that clause is about *not mutating* `tools[]`, not about *providing lazy discovery*, and §13.6's discretion clauses ("specific per-MCP-server-registration mechanism"; "specific `tools[]` array warm-up cycle at restart") do not cover the tool_search *mechanism* itself — only two narrower operational details. The plan also names a concrete acceptance shape (search tool + span emission + invariance witness), which forecloses an "undesigned architecture" reading. §13.7 is scoped to the minimal shape the plan actually specifies; match-ranking sophistication and defer-set selection policy are explicitly left to implementation discretion (mirroring the existing §13.6 discretion pattern) since neither is named in ADR-D3 or the plan's acceptance criteria.

`SkillActivationMode.TOOL_SEARCH` (AS spec §14.4 / runtime spec §14.17, C-RT-27) is a distinct, already-built, already-tested mechanism — it records the activation mode of a *Skill* selected at the per-LLM-dispatch hook, not MCP tool discovery — and is unmodified by this delta. §13.7 explicitly disclaims any relationship beyond possible co-occurrence in the same dispatch.

## Notes

- Phase 7 consumers may rely on this version (v1.13) as canonical for the `search_tools` capability-discovery contract.
- §13.1–§13.6 are unchanged; v1.13 is additive-only (new §13.7).
- See `.harness/clearance/README.md` for marker discipline.
