---
artifact: design-substrate/Implementation_Plan_Action_Surface_v1_6.md
version: v1.6
cleared_at: 2026-07-15T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-roadmap-continue
back_reference:
  - .harness/class_1_fork_sandbox_tier_floor_deterministic_inhouse_false_undefined.md (B-25, Reading A adopted)
  - .harness/clearance/adr-d2-v1-3-cleared-2026-07-15.md
  - .harness/clearance/spec-action-surface-v1-14-cleared-2026-07-15.md
  - .harness/forward-register.yaml (B-25 entry)
merge_commit: pending (pre-merge at filing time)
reviewer_chain:
  - "out-of-family `just codex-review` round 1 on PR #1030 — caught that the B-25 spec/ADR fix landed without a matching plan delta: `Implementation_Plan_Action_Surface_v1_2.md` §5.2 U-AS-06's Inputs line, Signatures comment, and AC #7 (preserved verbatim through v1.5) still describe `is_deterministic_inhouse` as a §2.3 row-1/2/7 discriminator — the same category of gap caught one session earlier at the B-24 arc (`Implementation_Plan_Action_Surface_v1_5.md`'s own change-note). This v1.6 delta is the correction, landed in the same PR before merge."
  - "full test run: harness-as/tests/test_sandbox_tier_floor.py — 18/18 passed (unchanged by this delta — prose-only correction, no code/test change)"
supersedes: null
superseded_by: null
---

# Clearance — `Implementation Plan Action Surface v1.6`

v1.6 closes the plan-layer half of the `B-25` resolution: `Implementation_Plan_Action_Surface_v1_2.md`'s U-AS-06 unit body (Inputs line, Signatures block comment, AC #7) named `is_deterministic_inhouse` alongside `forces_computer_use`/`forces_code_execution` as a "§2.3 row-1/2/7 discriminator," and AC #1's row enumeration named row 7 "read-only deterministic" — both preserved byte-exact through v1.3/v1.4/v1.5, both describing the reading `ADR-D2 v1.3` and `Spec_Action_Surface_v1.md v1.14` (this same B-25 resolution) corrected away from.

This delta corrects all four sites to state `is_deterministic_inhouse` is carried on `ToolMetadata` but does not gate row 7 or any row — reserved, non-gating, per the operator-ratified Reading A. **Zero code change, zero test change, zero AC-count change** — this is a documentation-only correction bringing the canonical plan's description of an existing field in line with what the field has always actually done (production implemented Reading A before this delta; the plan's *prose* was the only thing stale).

**Process correction, same PR.** The PR that closes B-25 initially amended only `ADR-D2.md` and `Spec_Action_Surface_v1.md`. Out-of-family `just codex-review` (round 1) caught that the canonical execution authority for U-AS-06 — the *plan*, not the spec — still carried the superseded reading, recreating (at the plan layer) the exact contradiction this PR set out to close at the ADR/spec layer. This v1.6 delta + marker is filed in the same PR before merge, so no merged state ever carries the plan in a still-contradictory posture relative to the resolved spec/ADR.

## Notes

- Phase 7 consumers may rely on this version (v1.6) as canonical for U-AS-06's Inputs/Signatures/AC text.
- `B-25`'s forward-register row close-out text is corrected in the same PR to cite this plan delta alongside the ADR-D2/spec clearance markers.
- See `.harness/clearance/README.md` for marker discipline.
