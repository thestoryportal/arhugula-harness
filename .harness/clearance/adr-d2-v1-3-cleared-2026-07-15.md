---
artifact: design-substrate/ADR-D2.md
version: v1.3
cleared_at: 2026-07-15T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-roadmap-continue
back_reference:
  - .harness/class_1_fork_sandbox_tier_floor_deterministic_inhouse_false_undefined.md (B-25, Reading A adopted)
  - .harness/forward-register.yaml (B-25 entry)
merge_commit: pending (pre-merge at filing time)
reviewer_chain:
  - "dyadic council convening (C10 action-safety/blast-radius + C4 tool-contract-semantics) run at the fork's own Q3 recommendation, per workspace CLAUDE.md §10.9 nameable-tension discriminator + §13.4 worked-example precedent — decisive finding: `is_deterministic_inhouse` carries zero verification today, so branching the floor on it is trivially spoofable by the actor it targets while only penalizing honest tool authors who never opted into the field; both voices converged on Reading A"
  - "operator `AskUserQuestion` on 2026-07-15 selecting 'Reading A + reserved annotation (Recommended)' from 4 synthesized options"
  - "full test run: harness-as/tests/test_sandbox_tier_floor.py — 18/18 passed, including new `test_sandbox_tier_floor_read_only_ignores_is_deterministic_inhouse`, mutation-probed (reverted the resolver to branch on `is_deterministic_inhouse` for read-only tools, confirmed 1 failure/17 pass, restored, confirmed 18/18 pass)"
  - ruff format + ruff check clean; pyright 0 errors/0 warnings/0 informations on all touched files
supersedes: null
superseded_by: null
---

# Clearance — `ADR-D2 v1.3`

v1.3 resolves the `B-25` fork: `§1.5.1`'s own `where:`-block row 7 read `(read-only, *, deterministic in-house) → Tier 1` — a 3-element condition tuple naming `is_deterministic_inhouse` as a real match condition — while the very next paragraph, "Row→argument keying," claimed rows 7–10 key purely on `blast_radius_tier` with no carve-out for row 7's extra qualifier. This is a genuine ADR-level self-contradiction (traced by the B-25 fork's own §1.5 addendum), not merely a downstream spec-vs-code drift.

This delta corrects the `where:`-block's row 7 to a 2-element tuple `(read-only, *)`, matching rows 8–10's shape and the keying paragraph's own claim — the reading production code (`harness-as/src/harness_as/sandbox_tier_floor.py`) already implemented. A new sentence is added directly beneath the `where:` block stating explicitly that `is_deterministic_inhouse` is carried on `ToolMetadata`/`ToolContract` but is **not** currently a keying input for any row — reserved, not removed, should a future verification mechanism (see `.harness/architect_recommendation_tool_determinism_attestation.md`) make the self-declared claim meaningful enough to gate on.

**Resolution process.** The fork's own §2 Q3 recommended a dyadic council convening (C10 ⊥ C4) before Q1's three candidate readings (A: non-forcing status quo / B: one-tier bump / C: forcing-tier bump) were put to the operator. That convening ran three empirical probes before either voice committed a position; the decisive one (`is_deterministic_inhouse` is a plain self-declared boolean with zero verification mechanism today) converted what looked like an irreducible C10-vs-C4 calibration tradeoff into a case where both voices' actual missions were served by the same answer — Reading B/C's "extra safety" is spoofable by exactly the actor it targets, while its cost falls on honest authors who simply never opted into a newer field. Both voices converged on Reading A. The council's synthesis (Option 1 of 4, alongside Option 2 = also deprecate the field, Option 3 = Reading B anyway, Option 4 = defer and build verification first) was presented to the operator via `AskUserQuestion`; the operator selected Option 1.

**No code change.** `sandbox_tier_floor()`'s 5-argument signature, all other `where:`-block rows, and the `max()` composition formula are unchanged — this delta documents the reading the resolver already implements. Companion fixes in the same PR: `Spec_Action_Surface_v1.md` v1.13 → v1.14 (the same row-7 self-contradiction existed there, downstream of this ADR), stale `ToolContract.is_deterministic_inhouse` / `MCPClientConfig.default_is_deterministic_inhouse` / `ToolMetadata` docstrings corrected (all previously claimed the field "keys" or is a "row-7 discriminator" — wrong as of this delta), and a new mutation-probed witness test (`test_sandbox_tier_floor_read_only_ignores_is_deterministic_inhouse`) pinning `True`/`False` producing identical tiers for a read-only tool, so Reading A is documented as an intentional decision rather than an untested gap.

## Notes

- Phase 7 consumers may rely on this version (v1.3) as canonical for `sandbox_tier_floor`'s §1.5.1 `where:`-block row 7.
- `B-25`'s forward-register row (`.harness/forward-register.yaml` + `.harness/post-phase-8-forward-register.md`) is marked closed in the same PR, citing this clearance marker.
- Workspace root `CLAUDE.md` §2.2's ADR-version table lists `ADR-D2 v1.2` — a follow-up token bump to `v1.3` is owed (out of spec-writer remit; flagged, per the established convention that this pointer batch-refreshes rather than bumping per-delta — the CP/Runtime spec pointers already lag similarly on `main`).
- See `.harness/clearance/README.md` for marker discipline.
