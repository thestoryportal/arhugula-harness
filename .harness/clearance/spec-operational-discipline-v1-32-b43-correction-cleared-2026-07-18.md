---
artifact: design-substrate/Spec_Operational_Discipline_v1_32.md
version: v1.32 (in-place correction; version label unchanged)
clearance_event: in-place stale-prose correction (B-43)
reviewers: autonomous loop (grounding verified at HEAD) + out-of-family codex convergence on the landing PR
merge_commit: (filled by the landing PR)
date: 2026-07-18
---

# Clearance — OD v1.32 §7.1 `harness.breaker.cause` stale-prose correction (B-43)

**What changed.** Two in-place annotations, no contract change: (1) the §7.1 attribute-table `cause` row's
"Vacuous-today, honestly documented" cell now records that the registered follow-on classifier arc LANDED
at `B-38` (PR #1020) — `retry_breaker_fallback._classify_breaker_cause` populates
`rate_limit`/`auth_failure`/`5xx_streak` at all three real `record_failure()` call sites
(grounded at HEAD this session: `retry_breaker.py:177` cross-reference; classifier at
`retry_breaker_fallback.py:305`; real-site call at `:898`), with `capability_shortfall` remaining a
forward-compatible slot; (2) the v1.32 change-note's vacuous-slot paragraph is annotated historical
(preserved verbatim as the authoring-era record). The `harness-od/CLAUDE.md` pointer-row mirror is
corrected in the same PR.

**Why in-place, not a new delta.** The correction changes NO committed contract surface (schema, types,
attribute count, and emission semantics are exactly what v1.32 committed — B-38 merely populated the slot
v1.32 defined). A new OD delta for prose-only factual staleness would collide with the pending
B-51/B-52/B-54 OD v1.34 amendment numbering awaiting operator ratification. Precedent: the ADR-D7 §15/§86
in-place correction (workspace CLAUDE.md §2.2).

**Register.** `B-43` closes with this PR; its close_out's mixed-posture concern is satisfied by this
marker (the §4.4 X-AL-3 guard recognizes clearance markers as back-flow documentation, and §11.4 records
marker-accompanied bundles as legitimate absorption arcs).
