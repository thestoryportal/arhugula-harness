---
name: ship-pr
description: Open a PR for the current arc and run the post-merge fixed-point refresh checklist correctly. Use when the operator says "/ship-pr", "ship it", "open the PR", "land this", or when an arc is built+green and ready to merge. Codifies the §12.2 post-merge audit + the §12.2.1 terminating-refresh fixed-point so the roadmap_status.md refresh is done right (and does not recurse). Do NOT use to author code (that is the arc itself) — use it for the PR + refresh ritual.
---

# ship-pr — PR + fixed-point refresh (U-HK-23)

The close half of the roadmap loop. Like `roadmap-continue`, this skill **executes the
canonical §12 protocol** rather than re-stating it — the recipe lives in CLAUDE.md §12.2 +
§12.2.1, read it live so this never drifts (§10.5).

## Pre-flight (before opening the PR)

- **Green.** `just check` + the relevant test suites pass; `bash -n` on any new shell.
- **Out-of-family review.** `just codex-review` (branch-vs-`main`) to convergence — fix
  real findings, hermetically regression-test each (§13.1). Use `--base` here, NOT
  `-uncommitted`: `-uncommitted` reviews untracked files too, so any untracked WIP in the
  working tree pollutes + dilutes the review of the actual diff (the 2026-06-26 finding at
  `.harness/uncommitted-review-flaw-verification-arc.md`). `-uncommitted` is for genuine
  pre-commit review in a CLEAN tree only.
- **Posture check (§11).** Confirm the edit scope matches one posture (design-phase /
  Phase 7 / mode-agnostic). A `design-substrate/**` + `harness-*/src/**` mix MUST carry
  back-flow documentation (§11.4) or it is silent absorption — halt + ask.
- **X-AL-3 (§4.4).** If `design-substrate/**` is touched, the PR must include a back-flow
  doc or a clearance marker (§4.5), else the CI guard fails.

## Open the PR

- Branch off the default branch (never the operator's working branch); conventional-commit
  title; body lists what changed + verification (tests/assertions, codex rounds) + the
  R-NNN it advances. End the body with the standard generated-with trailer.
- Commit/PR trailers per the workspace convention (Co-Authored-By; 🤖 Generated-with).

## Post-merge fixed-point refresh — CLAUDE.md §12.2 + §12.2.1

This is the step most often done wrong. After the PR merges:

1. **§12.2:** recompute `workspace_state_hash` (recipe `Project_Roadmap_v1.md` §7.1);
   update `.harness/roadmap_status.md` (`workspace_state_hash`, `last_refreshed`,
   `recently_completed` prepend / cap 5, `in_flight`, re-derive `next_action`); mark any
   closed `R-NNN` RESOLVED + propagate `next_pointer`.
2. **§12.2.1 — the recursion-stopping fixed point.** The refresh commit is itself a merge,
   which would trigger another refresh. Make the refresh PR a **terminating refresh**: title
   begins **exactly** `ops: roadmap status refresh ` AND the **only** changed file is
   `.harness/roadmap_status.md`. Both conditions are required — a refresh-titled commit that
   touches any other file is NOT terminating (the §12.2.1 false-negative the hooks guard
   against). The roadmap_status.md hash then legitimately lags HEAD by one commit; the next
   §12.1 audit recognizes the lag (step-6 carve-out) and does NOT spawn another. **Do not
   spawn a refresh PR for a refresh PR.**
3. **Bundled changes drop the prefix.** If the PR carries substantive non-refresh changes
   alongside a roadmap_status.md touch, its title MUST NOT use the reserved prefix
   (§12.2.1), and a follow-on terminating refresh is owed.

## Branch hygiene close-out — arc closed, delete its REMOTE branch now

Per `~/.claude/CLAUDE.md` §10 CI Discipline: *"Git repo will not have more than the current
CI branch present before any merge actions. If stale previous branches are present, conduct
a careful comprehensive review before deleting or merging them..."* This discipline is about
the **remote (GitHub) branch list**, not local `.git/refs/heads/*` pointers — local refs are
single-clone, cosmetic, and reflog-recoverable regardless; they are not what "branch hygiene"
means here. Don't defer this to a future session — that's how it gets missed.

The moment CI on `main`'s merge commit is confirmed green (not just the PR's own pre-merge
checks — the post-merge, push-triggered run) is exactly the moment this arc's remote branch
is provably safe to delete. This is always a single named branch — the one you just
merged — never a scan or backlog sweep:

```bash
# 1. Confirm the merge commit's OWN post-merge CI run on main is green (not the PR's
#    pre-merge checks — this repo has a documented case where those diverged).
merge_sha=$(gh pr view <PR#> --json mergeCommit --jq .mergeCommit.oid)
gh run list --commit "$merge_sha" --json conclusion --jq '.[0].conclusion'   # expect "success"

# 2. Delete the remote branch. This goes through the normal Bash permission prompt
#    every time — an explicit, reviewed action, never silent/unattended.
gh api -X DELETE repos/<owner>/<repo>/git/refs/heads/<branch>
```

If `gh pr merge --delete-branch` was used and it already removed the remote ref, step 2 is a
no-op (the API call 404s — nothing to do). Local branch refs are left alone entirely; they
carry no unique cleanup obligation. Worktree removal is a separate, structurally later step (a
session can't remove the worktree it's running inside) — that's `loop_gc_worktrees`, which
still runs at the next session's SessionStart per U-HK-26; unrelated to this step.

## R-NNN closure cascade — §12.5.3

On a closed R-NNN: if the close surfaced a `[[pattern]]` at cardinality ≥2, write the memory
entry + `MEMORY.md` line in the same (or a follow-on) PR; if it superseded an existing entry,
refresh it. (Checkpoint hygiene per §12.5.3: a checkpoint is "resolved" when its `branch:` is
merged; PreCompact snapshots are keep-10-pruned by `session-end-cleanup.sh`; resolved-checkpoint
archival is optional and not automated — no standing "archive Remaining-Work-addressed" step.)

## Notes

- The Wave-1 `post-merge-refresh.sh` hook pre-computes the new hash + injects the §12.2
  checklist on a substantive merge — trust it as a cross-check, but the refresh is still the
  agent's to land.
- Canonical text wins on any disagreement — re-read §12.2 / §12.2.1.
