---
artifact: design-substrate/Project_Workflow_v1_18.md
version: v1.18
cleared_at: 2026-07-14T00:00:00-06:00
clearance_type: doc-hygiene-refresh
back_reference:
  - .harness/R-600-pattern-bake-in-sweep.md (cadence-8 survey; cadence-7 card-frontier flag consolidated this arc)
  - Project_Roadmap_v1.md §5.6 R-600-pattern-bake-in-sweep
  - design-substrate/Project_Workflow_v1_14.md §7.5.1 + §7.5.3 + §7.5.4
  - design-substrate/Project_Workflow_v1_17.md PD-7 predecessor
  - /Users/robertrhu/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/mutation-probe-load-bearing-witness.md (the consolidated candidate)
merge_commit: <pending — set at v1.18 PR merge>
reviewer_chain:
  - advisor() pre-substantive review (confirmed the no-parking-compliant terminal at the prior loop iteration; recommended surfacing R-600 as an explicit operator choice rather than auto-running)
  - Pre-substantive empirical cadence-8 file-delta audit against the exact cadence-7 close timestamp (2026-07-14T00:49:43-06:00), not a rounded date
  - Independent-arc verification via `gh pr view` merge timestamps for PR #927 / #933 / #972 (confirmed 2 distinct calendar days, 3 distinct build arcs, 2 distinct axes — not a same-session/same-lesson collapse per the cadence-2 producer-discovery discriminator)
supersedes: Project_Workflow-v1_17-cleared-2026-07-12.md
---

# Clearance — `Project_Workflow v1.18`

Narrow additive workflow amendment promoting **PD-8 mutation-probe-as-load-bearing-witness** into the §7.5 process-discipline catalogue. Cadence-7 (2026-07-14, PR #974) flagged the mutation-probe technique as recurring but not yet consolidated into a named, citable memory entry — it lived only as sub-content inside a reviewer-ladder tooling file. That consolidation happened between cadence-7 and cadence-8 (`mutation-probe-load-bearing-witness.md`, mtime 2026-07-14T00:32:48-06:00), and this cadence's file-delta audit (against the precise cadence-7 close timestamp, not a rounded date — mirroring the cadence-7 audit's own tightened-cutoff precedent) confirms it clears all three §7.5.1 gates: instance-cardinality >=2 across genuinely independent arcs (PR #927 and PR #933, both 2026-07-11 but distinct sibling CP-axis builds; PR #972 / `B-26`, 2026-07-14, a wholly separate IS-axis arc with 4 independent probes in one PR), genuinely §7.5-shaped (verification-sequencing, not stale-carry-text or fidelity grammar), and no canonical home elsewhere (adjacent to but distinct from PD-3's verification-shape-matching and PD-6's composed-chain-witness disciplines — PD-8 is the narrower check that a test, once written at the right depth through the right chain, actually discriminates the fix from its absence).

This marker clears v1.18 for Phase 7 consumption as the current workflow head. v1.17 remains the predecessor body and is preserved verbatim; PD-7, PD-6, PD-5, PD-1 through PD-4, §7.5.1, §7.5.3, §7.5.4, and all §7.4 / §7.4.7 content are unchanged. ZERO C-*-NN contract change, ZERO retirement event filing, ZERO production code change, and ZERO cross-axis cascade.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
- PD-8 is adjacent to PD-3 (verification-shape matching) and PD-6 (composed-chain non-vacuity) but does not replace either; it is the narrower "prove the test itself is load-bearing via fault injection" discriminator, applied after PD-3/PD-6 are already satisfied.
- This clearance also corrects a stale governance pointer discovered during the same arc: root `CLAUDE.md` §10.2's "Workflow doc" row still cited v1.16/PD-6 (two versions behind the actual canonical head, which had already advanced to v1.17/PD-7 at the cadence-5 clearance, 2026-07-12) — `.harness/claude-artifact-pointers.md` was correctly current at v1.17 but root `CLAUDE.md` was never bumped alongside it. Both pointers are corrected to v1.18/PD-8 in this same PR.
- The R-600 sweep artifact's own top-of-file "Latest status" summary line was likewise stale (said "cadence-6" even though the file body already contained a complete, closed cadence-7 section) — corrected to reflect cadence-8's outcome in this same PR.
