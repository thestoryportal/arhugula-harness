# Pipeline — Fork Queue

*Forks awaiting operator decision. The review-ahead lane appends here; it never
edits canonical artifacts (`review-pipeline.md` §3). Operator resolves; an
applicator skill (`spec-writer` / `implementation-planner`) applies; the
reviewer re-checks. Authored 2026-05-15.*

## Open forks — operator decision owed

Seeded from `CLAUDE.md` resume remaining-work + `phase-7-progress.md` §4A.
The pilot review-ahead pass will disposition items 1–2 (verify classification,
recommend resolution shape — not decide).

| # | Item | Class | Source | Status |
|---|---|---|---|---|
| 1 | 4 findings carried from §4A conformance: U-CP-43 input-set divergence + `MCP_TRUST` under-spec; U-CP-46 coverage shrink (`audit.gate.*` dissolved → orphans `composition_winner`); U-CP-23 `default_pattern` single-vs-dual structural mismatch; OD compound-spec-row rendering judgment call | §2.7.6 Class 1/2 (per item) | CP v2.4 §0.8 / OD v2.5 §0.6 | open — pilot reviewer to disposition |
| 2 | 5 original flagged items: U-CP-08 (FallThroughCause design gap), U-CP-11 (LEASE naming call), U-OD-09 acc#2 (tier-split design gap), U-OD-28 (§20.1 surface — conformance target undetermined), U-OD-29 (needs ADR-D2 §1.2 check) | §2.7.6 Class 1/2 (per item) | §4A audit reports | open — pilot reviewer to disposition |
| 3 | ~10 deferred `[U-CP-00]` edge materializations — recorded CP v2.5 §0.5; materialized at each `WorkloadClass`-consuming unit's next full-revision | §2.7.6 Class 3 (informational) | CP v2.5 §0.5 | open — non-blocking; resolves per-unit |
| 4 | F1-02 — root `CLAUDE.md` §2.2 mislabels D-ADRs (ADR-D4 ↔ ADR-D5 swapped: D4 = topology, D5 = HITL) | §2.7.6 Class 3 (doc fix) | `.harness/adversarial_review_phase7_cp_od_preimpl.md` | open — operator confirm + fix |
| 5 | `harness-cp/CLAUDE.md` §3 stale — lists U-CP-22 as L0/in-degree-0; CP v2.5 made it L1 (`Depends on: [U-CP-00]`) | §2.7.6 Class 3 (doc fix) | CP v2.5 §0.5 | open — minor docs follow-up |

## Resolved forks

| Item | Resolution | Date |
|---|---|---|
| Tension 001 — C-IS-03 §3 "four" vs 5 rows | spec fixed in-CLI; block cleared | 2026-05-15 |
| Tension 002 — TopologyPattern enum 3-way divergence | operator signed off Set 2 (spec C-CP-10 §10.1); conformed at 4 loci | 2026-05-15 |
| Tension 003 — `WorkloadClass` undeclared | declared in `harness-core` via new U-CP-00 | 2026-05-15 |
| Tension 004 — U-OD-04 span schema divergence | subsumed into OD §4A audit; conformed in OD plan v2.5 | 2026-05-15 |
