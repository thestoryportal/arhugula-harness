# Handoff: resume state at the 2026-08-01 pause (Claude → any runner)

Repo-committed projection of the two gstack checkpoints in this directory, so a Codex (or any) session can resume without access to `~/.gstack/`. Canonical next-action authority remains `.harness/roadmap_status.md` (CLAUDE.md §12 / AGENTS.md §Verification); this file carries only the in-flight-arc state that file does not.

## State at pause

- Main at `aefd055f` (post-#1185 Codex-handoff/Antigravity refresh). PRs #1184–#1185 added the durable Codex handoff, three-lens prompts and the verified `agy` review path; this parity arc completes their operational projection.
- The five-item ratification batch is ANSWERED (2026-08-01, operator): **B-107 → Reading A-hybrid; B-96 → Reading C; B-98 → Reading C (landed #1182); B-104 → Reading D (landed #1182); `run_bootstrap` `__all__` → leave.** Full text in `20260801-093000-*.md`.

## In-flight leg 1 — B-96 council record (fold + finish)

- Remote branch `b96-council-ceiling` is represented locally by `b96-fold-worktree` @ `a44e1971`, **draft PR #1183**, deliverable `.harness/council-b96-grace-ceiling-2026-08-01.md`. Local and remote heads are synchronized and the current PR checks are green; reconcile the post-parity `main`, push that merge, and un-draft only after those new checks pass. **Do not merge #1183 in the finishing session.**
- Verdict **C-2** (elapsed-time grace alone, no ceiling) — stable, unanimous (C3 primary, C10 consultant, C7 Layer-D add), survives everything below. B-74-residue closes structurally under C-2 (its close_out's second option; `:1982` flips to `== []`).
- **Round-3 absorption is complete.** The record carries six review passes and `6 + 12 + 3 + 5 + 7 + 3 = 36` absorbed finding rows; the final dedicated in-family absorption-verification pass found three Class-2 propagation defects, all folded without reopening C-2. The condition table was programmatically recounted as the contiguous set **1–12** after every final edit.
- **No WIP markers remain.** The former condition-#5 candidate-class omission, condition-#6 durability premise and false TENSION-1 classification are folded. The final pass also removed the stale claim that the pull level substitutes for cadence knowledge and replaced diagnostic/detection overclaims with operator-discriminated inspection/evidence.
- C7's Class-3 residue is registered as **B-108** with harness-configured-sink scope and shape-specific closure witnesses. `python3 tools/forward_register.py --check` passes at 108 items (`87 closed`, `19 registered_finding`, `1 design_substrate_gated`, `1 held`).
- Finish only the transport gates: reconcile current `main` into the isolated topic worktree, re-run the condition/count/register checks, push `b96-fold-worktree` to `origin/b96-council-ceiling`, mark #1183 ready and require its CI green. **Stop there; do not merge #1183.** External-canon mode remains explicitly un-run by the council record's low-yield judgment.

## In-flight leg 2 — B-107 A-hybrid spec leg

- Branch `b107-spec-leg-a-hybrid` @ `dc825591` (off `cfa60f4a`). Sole content: `.harness/wip-b107-spec-leg-grounding-notes.md` (delete before PR). **No spec text authored yet — clean (re)launch from the merged artifacts is the intended path.**
- Authority: `.harness/class_2_fork_b107_empty_fence_key_resolution_refusal.md` (§4 Reading A / §6 / §8 / §9) + the ratification (A-hybrid). The notes file preserves: the seven resolver call sites re-derived programmatically at `cfa60f4a` (matches the fork doc); all fork-doc anchors verified UNMOVED; one new `[HIGH]` finding the v1.115 delta must absorb (the membership amendment makes CP v1.112 `:111` / v1.113 `:85`'s "uniform-fallback counts it" sentence stale-as-described AND removes the obstacle behind v1.112's round-11 SOURCE-SHAPE-not-fifth-VARIANT reversal — reconcile at §1, union stays 4 variants / 10 shapes / 7 carriers).
- Deliverables: CP spec v1.114→v1.115 (three A-hybrid amendment sites + the §2-publication reconciliation) + plan v2.48→v2.49 (owed: eight-cell witness grid + PD-8 mutation probe, per the B-100 same-PR precedent) + register row/prose + fork §11 addendum + clearance marker + CLAUDE.md §2.3 pointer + lineage append + check tools + out-of-family review to convergence + PR (never self-merge without the gate discipline).
- After the spec leg: the **B-107 impl leg** (fork §9 leg 4: membership fix, construction refusal, resolver enforcement, three extra witnesses, §6.1 defence-in-depth scoping).

## After both legs

- **B-96 spec leg** on the settled C-2 council verdict and the final **twelve-condition** set in `.harness/council-b96-grace-ceiling-2026-08-01.md` → then its impl leg. **B-74-residue filing** unblocks at B-96's answer.
- Remaining pool: B-99 (trigger-gated), elders (verified dormant), held=1 (R-1). Register after B-108: 108 items / 87 closed / 19 registered_finding / 1 design_substrate_gated / 1 held.

## Hygiene carries

- Operator prune list: local branch `b98-b104-defer-legs`.
- Merge-gate log current through #1182.
