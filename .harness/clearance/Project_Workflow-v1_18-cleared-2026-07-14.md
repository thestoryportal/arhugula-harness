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
  - out-of-family `just codex-review` on this PD-8 promotion's own PR, pre-merge, THREE rounds — round 1 caught the audit-window misattribution + overstated independent-arc cardinality; round 2 caught round 1's own new errors (PR #972's axis mischaracterized, its probe count uncorrected); round 3 asked for live execution evidence rather than historical self-report — all 6 corrected before merge, see Notes
  - Independent-arc verification via `gh pr view --json mergedAt,files` + each commit's `Claude-Session` trailer for PR #927 / #933 / #972 (corrected count: 2 genuinely independent instances, not 3 — #927/#933 share one session and collapse per the cadence-2 same-session-same-lesson discriminator; #972 is CP-axis with 2 discriminating-witness probes, not IS-axis with 4)
  - Live mutation-probe re-verification against current HEAD for the PR #972 instance: baseline green (2 passed) → fix reverted, both tests fail with the expected `AssertionError` (not an unrelated crash) → fix restored, `git diff` clean, all 14 tests in the file re-verified green — see `design-substrate/Project_Workflow_v1_18.md` §7.5.1 gate table
supersedes: Project_Workflow-v1_17-cleared-2026-07-12.md
---

# Clearance — `Project_Workflow v1.18`

Narrow additive workflow amendment promoting **PD-8 mutation-probe-as-load-bearing-witness** into the §7.5 process-discipline catalogue. Cadence-7 (2026-07-14, PR #974) flagged the mutation-probe technique as recurring but not yet consolidated into a named, citable memory entry — it lived only as sub-content inside a reviewer-ladder tooling file — and its own write-up said "re-evaluate at the next R-600 cadence." This is that deferred re-evaluation.

**Six factual corrections made pre-merge, across three rounds of out-of-family Codex review of this promotion's own PR** (PD-8 applied to itself, recursively). Round 1 caught: (1) the candidate memory file's mtime (`2026-07-14T00:32:48-06:00`) predates cadence-7's own close commit (`2026-07-14T00:49:43-06:00`) by 17 minutes — it is a deferred re-evaluation of an already-flagged candidate, not a fresh file-delta discovery since cadence-7 close, as the initial draft mischaracterized it; (2) instance-cardinality was initially overstated as "3 distinct arcs" without verifying independence against the primary source — `gh pr view --json mergedAt` + each commit's `Claude-Session` trailer show PR #927 and PR #933 (both 2026-07-11) share one session and one underlying lesson, collapsing to a single instance under the cited same-session-same-lesson discriminator. Round 2 caught two further errors introduced by round 1's own fix: (3) PR #972/`B-26` was mischaracterized as a separate "IS-axis" arc — its commit is `fix(cp)`, wiring real IS hash-chain verification into a CP-owned module, a CP→IS seam rather than a distinct axis; (4) its claimed "4 independent probes," carried forward unverified from the memory file, is actually 2 on direct read of the committed test diff. Round 3 caught the deepest gap and asked for the strongest possible fix: (5) even the corrected "2 probes" claim rested on historical self-report (the PR #972 commit message + test docstrings), not live evidence — closed by literally re-running the mutation-probe against current HEAD (baseline green → fix reverted, both tests fail with the expected `AssertionError` → fix restored, clean, re-verified green); (6) this arc's own corrective edits to the source memory file had bumped its mtime past the cadence-7 cutoff, meaning a fresh file-delta re-run would no longer reproduce the cited 6-file result — clarified as the original audit snapshot. The fully corrected, honest, and now *live-verified* count is **2 genuinely independent instances**: the #927/#933 session + PR #972/`B-26` (2026-07-14, CP-axis, a wholly separate session, 2 discriminating-witness probes in one PR, re-run and confirmed against current HEAD). None of the six corrections changes the promotion outcome — 2 still clears the literal §7.5.1 gate, at the thinnest margin of any PD promoted so far, recorded honestly rather than overstated. The remaining two gates hold as originally assessed: genuinely §7.5-shaped (verification-sequencing, not stale-carry-text or fidelity grammar), and no canonical home elsewhere (adjacent to but distinct from PD-3's verification-shape-matching and PD-6's composed-chain-witness disciplines — PD-8 is the narrower check that a test, once written at the right depth through the right chain, actually discriminates the fix from its absence).

This marker clears v1.18 for Phase 7 consumption as the current workflow head. v1.17 remains the predecessor body and is preserved verbatim; PD-7, PD-6, PD-5, PD-1 through PD-4, §7.5.1, §7.5.3, §7.5.4, and all §7.4 / §7.4.7 content are unchanged. ZERO C-*-NN contract change, ZERO retirement event filing, ZERO production code change, and ZERO cross-axis cascade.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
- PD-8 is adjacent to PD-3 (verification-shape matching) and PD-6 (composed-chain non-vacuity) but does not replace either; it is the narrower "prove the test itself is load-bearing via fault injection" discriminator, applied after PD-3/PD-6 are already satisfied.
- This clearance also corrects a stale governance pointer discovered during the same arc: root `CLAUDE.md` §10.2's "Workflow doc" row still cited v1.16/PD-6 (two versions behind the actual canonical head, which had already advanced to v1.17/PD-7 at the cadence-5 clearance, 2026-07-12) — `.harness/claude-artifact-pointers.md` was correctly current at v1.17 but root `CLAUDE.md` was never bumped alongside it. Both pointers are corrected to v1.18/PD-8 in this same PR.
- The R-600 sweep artifact's own top-of-file "Latest status" summary line was likewise stale (said "cadence-6" even though the file body already contained a complete, closed cadence-7 section) — corrected to reflect cadence-8's outcome in this same PR.
