---
artifact: design-substrate/Project_Workflow_v1_19.md
version: v1.19
cleared_at: 2026-07-24T00:00:00-06:00
clearance_type: doc-hygiene-refresh
back_reference:
  - .harness/R-600-pattern-bake-in-sweep.md (cadence-9 survey)
  - Project_Roadmap_v1.md §5.6 R-600-pattern-bake-in-sweep
  - design-substrate/Project_Workflow_v1_14.md §7.5.1 + §7.5.3 + §7.5.4
  - design-substrate/Project_Workflow_v1_18.md PD-8 predecessor
  - /Users/robertrhu/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/reviewer-oscillation-register-and-hold.md
  - /Users/robertrhu/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/non-convergent-adversarial-hardening-arms-race.md
  - /Users/robertrhu/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/over-correction-away-from-mostly-right-baseline.md
  - /Users/robertrhu/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/self-referential-review-loop-discriminator.md
merge_commit: <pending — set at v1.19 PR merge>
reviewer_chain:
  - "advisor() pre-substantive review — redirected candidate selection away from the highest-raw-citation token (`merge-gate-catches-what-codex-advisor-miss`, 17+ instances) after identifying its transferable content already has a canonical home (`.claude/skills/merge-gate/SKILL.md`'s own text + root `CLAUDE.md` §13.1's advisor+codex decorrelation framing); pointed at the genuinely uncovered gap instead — four related memories describing distinct adversarial-review-loop non-convergence signatures, none homed in §7.5"
  - "Direct read of the full v1.18 §7.5.2 catalogue (PD-1 through PD-8) to confirm no existing entry covers loop-convergence-recognition (as distinct from single-finding verification, which PD-3/PD-6/PD-8 already cover)"
  - "Direct read of root CLAUDE.md §13.1/§13.2 to confirm the orchestration-mechanism-selection guidance there does not overlap with the loop-stopping-discriminator content promoted here"
  - "Direct read of all 4 source memory files (not citation-count alone) to verify each cited instance's independence and to de-duplicate the prewarm/keepalive-disable arc (`B-55`), which is cited from two different memory files describing the same underlying arc"
  - "Cross-checked `B-55`'s forward-register row exists and is closed at `.harness/forward-register.yaml:1225`"
supersedes: Project_Workflow-v1_18-cleared-2026-07-14.md
---

# Clearance — `Project_Workflow v1.19`

Narrow additive workflow amendment promoting **PD-9 adversarial-review-loop non-convergence discriminators** — a 4-signature family (oscillation / arms-race hardening / over-correction / self-referential drift) — into the §7.5 process-discipline catalogue.

**Candidate-selection correction, recorded honestly.** The cadence-9 survey's first pass treated `merge-gate-catches-what-codex-advisor-miss` (17+ dated named instances of the workspace's 3-lens `merge-gate` skill catching genuine defects codex+advisor missed) as the leading candidate on raw citation volume. `advisor()`, consulted before drafting per the standing pre-substantive-work discipline, corrected this: that evidentiary volume is a tool-usage catch-log for one specific workspace skill, not independent recurrence of a transferable SDLC discipline. Direct read of `merge-gate/SKILL.md` confirmed its two genuinely transferable claims (lens-decorrelation; fail-closed verdict parsing) are already stated verbatim in that file's own text, and the decorrelation framing is independently already codified at root `CLAUDE.md` §13.1 — gate 3 (no canonical home elsewhere) FAILS for that token standalone, mirroring the cadence-6/7 Class-B disposition already given to `codex-out-of-family-reviewer` / `fable5-fallback-reviewer`. It is NOT promoted here.

The genuine gap the cadence surfaced instead: four memories, each naming a distinct signature for *why* an adversarial review loop fails to converge (a flip-flopping design fork; an inexhaustible-finding hardening game against a cooperative/local mechanism; a register correction that reverses rather than narrows across rounds; a loop whose findings drift from substance to self-referential narration about its own prior corrections) — none of which PD-3 (verification-shape depth), PD-6 (composed-chain witness), or PD-8 (mutation-probe test-discrimination) covers, since all three verify a *single finding's* correctness once made rather than whether *continued iteration itself* is still producing signal.

§7.5.1 gate 1 (instance-cardinality) clears with the widest margin of any PD promoted to date: at least 6 independent arcs verified via direct memory-file read (prewarm/keepalive-disable → `B-55`; concurrent-resume-witness → `B-39` scope; PR #1079 permission-guard 6-round hardening; the `B-33-A` spec-leg Q4 instance; `B-40`'s 3-round register over-correction; this workspace's own PD-8/v1.18 promotion rounds 5-6). Gate 2 (genuinely §7.5-shaped) and gate 3 (no canonical home elsewhere) both PASS per direct-read verification recorded in the reviewer chain above.

This marker clears v1.19 for Phase 7 consumption as the current workflow head. v1.18 remains the predecessor body and is preserved verbatim; PD-8, PD-7, PD-6, PD-5, PD-1 through PD-4, §7.5.1, §7.5.3, §7.5.4, and all §7.4 / §7.4.7 content are unchanged. ZERO C-*-NN contract change, ZERO retirement event filing, ZERO production code change, and ZERO cross-axis cascade.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
- PD-9 is adjacent to PD-3 (verification-shape matching), PD-6 (composed-chain non-vacuity), and PD-8 (mutation-probe-as-load-bearing-witness) but does not replace any of them; it operates on the orthogonal axis of loop-convergence recognition rather than single-finding correctness.
- Root `CLAUDE.md` §2.1 + §10.2 "Workflow doc" pointer row and `.harness/claude-artifact-pointers.md` are both bumped to v1.19/PD-9 in this same PR — verified BOTH were current at v1.18 before this bump (the cadence-8 clearance had already caught and fixed a prior 2-version staleness in the root pointer; this cadence confirms it did not regress).
- The R-600 sweep artifact (`.harness/R-600-pattern-bake-in-sweep.md`) gains a cadence-9 section in this same PR, including the file-delta-cutoff resolution: git-history reorganization made the recorded cadence-8 PR merge commit (`323dfeae`) unreachable via `merge-base --is-ancestor` against current HEAD, but `git log --all` still resolves that commit's own object timestamp directly (`2026-07-14T18:52:18-06:00`). The actual cutoff used for both the memory-file-delta enumeration and the merge count is this exact git-object timestamp, not the artifact's prose-recorded close date — a first draft used a same-day-midnight approximation of the latter and was corrected at codex round 1 of this PR's own review after it was shown to silently exclude two already-canonical memory files edited between the true close and midnight; codex round 2 additionally caught that the merge count must be anchored to a fixed pre-arc commit (`e5529e8a`), not a floating branch `HEAD`, to stay reproducible.
