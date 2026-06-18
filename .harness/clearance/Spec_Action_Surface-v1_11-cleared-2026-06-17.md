---
artifact: design-substrate/Spec_Action_Surface_v1.md
version: v1.11
cleared_at: 2026-06-17T17:52:06-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b6_slice_2_per_tool_sandbox_tier.md
  - design-substrate/Spec_Harness_Runtime_v1.md v1.56 §14.9.11 (the runtime cascade this AS leg serves)
merge_commit: pending (R-FS-1 B6 Slice 2 bundled-absorption PR)
reviewer_chain:
  - operator AskUserQuestion ratification 2026-06-17 (the B6 Slice 2 arc; the AS leg itself is additive/adopt-and-note)
  - advisor (full-transcript) — confirmed fork (a) ToolContract extension is additive, safe-default, non-gated
  - impl-time grounding pass (worktree off bca9a61)
supersedes:
superseded_by:
---

# Clearance — `Spec_Action_Surface v1.11`

v1.11 extends the **C-AS-03 §3.1 `ToolContract` field signature** with the three §2.2 `ToolMetadata` forcing discriminators (`forces_computer_use` / `forces_code_execution` / `is_deterministic_inhouse`) so the runtime per-tool sandbox resolver (runtime spec v1.56 §14.9.11, R-FS-1 B6 Slice 2) can carry them to `sandbox_tier_floor` and key the C-AS-02 §2.3 forcing rows 1-2 + row 7 **per tool**. This is the AS-side leg of the runtime §14.9.11 cross-axis cascade.

**Additive + non-breaking (adopt-and-note — no operator gate at the AS leg).** The three fields are optional with safe non-forcing defaults (`false`): every existing `ToolContract` resolves byte-identically (rows 1-2 skipped at `false`; row 7's `tier-1-process` is bounded below by the deployment-surface default + the per-tool `blast_radius_tier` floor); only a NEW declaration opts into the forcing rows. No `minimum_tier` / `blast_radius_tier` / `required_secrets` change; no `sandbox_tier_floor` signature change (§2.2/§2.3 + `ToolMetadata` PRESERVED VERBATIM — v1.11 only lets `ToolContract` *carry* the existing `ToolMetadata` discriminators); no C-AS-02 composition change; no AS-AL rule added. §3.2 + §3.3 PRESERVED VERBATIM.

**Phase 7 consumers:** the AS↔runtime registration seam (`RawContractInput` + the v1.40 stage-3a `MCPToolContractConverter`) threads the three new fields; impl lands in the same B6 Slice 2 PR as the runtime §14.9.11 carrier (`harness-as/tool_contract.py`).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
