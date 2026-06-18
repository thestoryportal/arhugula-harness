---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.56
cleared_at: 2026-06-17T17:52:06-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b6_slice_2_per_tool_sandbox_tier.md
  - operator AskUserQuestion ratification 2026-06-17 (driver-granularity Option A — "Full per-tool")
merge_commit: pending (R-FS-1 B6 Slice 2 bundled-absorption PR)
reviewer_chain:
  - operator AskUserQuestion ratification 2026-06-17 (Option A — full per-tool driver; the §14.9.9/§14.9.10 inv-3 relaxation is a committed-invariant sacrifice → operator's call)
  - advisor (full-transcript) — confirmed design-fork-first → gate → impl; reframed the gate to fork (b) only, both-options-safe; surfaced the Option-B cost-fidelity discriminator that decided Option A
  - impl-time grounding pass (worktree off bca9a61; corrected an early main-checkout mis-read)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.56`

v1.56 authors **§14.9.11 — per-tool sandbox-tier resolution + per-dispatch driver selection** (NEW), the R-FS-1 arc **B6 Slice 2** (`B-PER-TOOL-SANDBOX-TIER`; the last FROZEN arc of the R-FS-1 umbrella). It lifts the per-server-uniform→per-tool carve-out that §14.9.9 Scope-boundary + §14.9.10 D4/inv-3/Scope-boundary(b) named as "the distinct future arc B6". The §14.9.8 constant per-server resolver becomes a per-`(contract, step)` call to the full 10-row `sandbox_tier_floor` (C-AS-02 §2.3), `max()`-composed with the deployment-surface default — so the per-tool forcing rows (1-2) + per-tool blast rows (7-10) become reachable per tool, while rows 3-6 subsume B6 Slice 1's per-host transport floor per-tool (STDIO→TIER_3 preserved). The driver is selected per-dispatch from a per-host per-tier registry (delivered == resolved — no audit/cost-fidelity gap).

**Operator-gated.** §14.9.11 RELAXES §14.9.9 inv-3 + §14.9.10 inv-3 ("per-server-uniform, construction-time driver") to per-dispatch selection — a committed-invariant sacrifice, ratified via the fork-doc AskUserQuestion (Option A over the spec-complete Option B; the deciding discriminator was Option B's delivered≠resolved audit/cost-fidelity gap against the CA #625 cost-rollup). Scope discipline: ONLY §14.9.11 is new; §14.9.1–§14.9.10, §14.10+, §14.20, §9, §5.2-hash, and all prior change-notes are PRESERVED VERBATIM. No new fail class (reuses §14.9.9 `RT-FAIL-SANDBOX-DRIVER-UNAVAILABLE`, now per-tier). No IS-spec/§5.2-hash change. No ADR change (ADR-F4 "guarantee not advisory" honored — delivered == resolved).

**Phase 7 consumers:** the cross-axis cascade — AS spec C-AS-03 §3.1 (`ToolContract` gains the `ToolMetadata` forcing discriminators, additive, safe defaults) — lands at AS spec v1.11 in the same PR (marker `Spec_Action_Surface-v1_11-cleared-2026-06-17.md`). The impl (resolver body + per-host per-tier driver registry as a `PerTierToolExecutionDriver` composite leaving the bare dispatcher byte-unchanged) is impl-discretion.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
