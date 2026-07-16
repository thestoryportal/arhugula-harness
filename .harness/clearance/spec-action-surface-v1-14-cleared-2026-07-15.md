---
artifact: design-substrate/Spec_Action_Surface_v1.md
version: v1.14
cleared_at: 2026-07-15T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-roadmap-continue
back_reference:
  - .harness/class_1_fork_sandbox_tier_floor_deterministic_inhouse_false_undefined.md (B-25, Reading A adopted)
  - .harness/clearance/adr-d2-v1-3-cleared-2026-07-15.md (the upstream ADR-level resolution this delta absorbs)
  - .harness/forward-register.yaml (B-25 entry)
merge_commit: pending (pre-merge at filing time)
reviewer_chain:
  - "dyadic council convening (C10 + C4) + operator AskUserQuestion — see ADR-D2 v1.3 clearance marker for the full resolution record; this delta is the spec-side absorption of the same decision"
  - "full test run: harness-as/tests/test_sandbox_tier_floor.py — 18/18 passed"
  - ruff format + ruff check clean; pyright 0 errors/0 warnings/0 informations on all touched files
supersedes: null
superseded_by: null
---

# Clearance — `Spec Harness Action Surface v1.14`

v1.14 absorbs the `ADR-D2 v1.3` resolution of `B-25` into the spec layer. `§2.3`'s row 7 carried the identical self-contradiction traced at the ADR: the row's condition text named `is_deterministic_inhouse` as a qualifier ("Read-only, deterministic in-house tool"), while the "Row→argument keying" paragraph immediately below claimed rows 7–10 key purely on `blast_radius_tier`.

This delta:

- Corrects row 7's condition text to "Read-only, any" (matching rows 8–10's shape).
- Adds a trailing sentence to the "Row→argument keying" paragraph stating explicitly that `is_deterministic_inhouse` is not currently a keying input for any row — reserved, not removed.
- Corrects the `§3.1` `ToolContract.is_deterministic_inhouse` field docstring (previously: "keys the C-AS-02 §2.3 row-7 ... lookup" — wrong) and the `ToolMetadata`-discriminators prose paragraph (previously described row 7 as a "forcing row" alongside rows 1-2 — wrong; only rows 1-2 are forcing).
- Notes the companion runtime-side fix (`harness-runtime/src/harness_runtime/types.py`'s `MCPClientConfig.default_is_deterministic_inhouse` docstring), landed in the same PR though not itself a spec-substrate edit.

**No `sandbox_tier_floor` signature change; no `ToolContract`/`ToolMetadata`/`MCPClientConfig` field added or removed; no `max()` composition change.** This is a documentation correction bundled with the upstream ADR-D2 v1.3 fix per workspace `CLAUDE.md` §4.4/§11.4's bundled-absorption-arc convention — landed in the same PR, both carrying clearance markers, so no merged state ever carries the ADR/spec pair in a still-contradictory state relative to each other.

## Notes

- Phase 7 consumers may rely on this version (v1.14) as canonical for `Spec_Action_Surface_v1.md` §2.3 row 7 and the `is_deterministic_inhouse` field's non-gating status.
- `B-25`'s forward-register row is marked closed in the same PR, citing this clearance marker + the ADR-D2 v1.3 marker.
- Workspace root `CLAUDE.md` §2.3's AS spec pointer table lists `Spec_Action_Surface_v1.md` at `v1.13` — a follow-up token bump to `v1.14` is owed (out of spec-writer remit; flagged, per the established periodic-batch-refresh convention already applied to the CP/Runtime pointers on `main`).
- See `.harness/clearance/README.md` for marker discipline.
