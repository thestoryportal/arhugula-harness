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
# 0. Set this to the branch you already know you're closing out (the one THIS arc's PR
#    used — e.g. `git branch --show-current` if the worktree hasn't moved on yet). A hard
#    check below, not just an eyeballed echo, against a mistyped PR number that happens to
#    resolve to some OTHER legitimately-merged PR.
expected_branch="<branch-name>"

# 1. Pull the PR's own state + the branch name + its exact merged tip SHA — never typed
#    by hand. Confirm it's actually MERGED into the default branch AND that its branch
#    matches what you expected (both guard against a mistyped PR number silently
#    targeting some OTHER valid merged PR's branch).
pr_json=$(gh pr view <PR#> --json state,baseRefName,headRefName,headRefOid,mergeCommit)
[ "$(jq -r .state <<<"$pr_json")" = MERGED ] || { echo "ABORT: PR is not MERGED"; exit 1; }
[ "$(jq -r .baseRefName <<<"$pr_json")" = "$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name)" ] \
  || { echo "ABORT: PR did not merge into the default branch"; exit 1; }
branch=$(jq -r .headRefName <<<"$pr_json")
[ "$branch" = "$expected_branch" ] || { echo "ABORT: PR <PR#>'s branch ($branch) != expected ($expected_branch)"; exit 1; }
head_oid=$(jq -r .headRefOid <<<"$pr_json")
merge_sha=$(jq -r .mergeCommit.oid <<<"$pr_json")

# 2. Fail closed unless the merge commit's OWN post-merge CI run on main is an exact
#    "success" (not the PR's pre-merge checks, which this repo has a documented case of
#    diverging from — and not "pending"/"failure"/empty, which must ALSO abort, not just
#    print and fall through).
concl=$(gh run list --commit "$merge_sha" --json conclusion --jq '.[0].conclusion // empty')
[ "$concl" = success ] || { echo "ABORT: post-merge CI on main is not confirmed green (got '${concl:-empty}')"; exit 1; }

# 3. If gh pr merge --delete-branch already removed the ref, there's nothing left to
#    delete — treat that as done, not a failure. Exit 2 from `ls-remote --exit-code` is the
#    ONLY "genuinely absent" signal; any other nonzero (network unreachable, auth failure,
#    ...) must abort, not be silently read as "already gone". Otherwise, lease-guarded
#    delete: refuses atomically if the remote tip no longer equals the verified merged SHA
#    (new work pushed to the same branch name post-merge, or a stale/reused ref). A bare
#    `gh api -X DELETE`/`git push --delete` has no such guard and would silently destroy
#    whatever is currently there, with no recovery. Goes through the normal Bash
#    permission prompt every time — an explicit, reviewed action, never silent/unattended.
git ls-remote --exit-code --heads origin "refs/heads/${branch}" >/dev/null 2>&1; rc=$?
case "$rc" in
  0) git push --force-with-lease="refs/heads/${branch}:${head_oid}" origin ":refs/heads/${branch}" ;;
  2) echo "Already gone (gh pr merge --delete-branch or a prior run) — nothing to do." ;;
  *) echo "ABORT: could not verify remote ref state (ls-remote exit $rc — network/auth issue?)"; exit 1 ;;
esac
```

Local branch refs are left alone entirely; they carry no unique cleanup obligation. Worktree
removal is a separate, structurally later step (a session can't remove the worktree it's
running inside) — that's `loop_gc_worktrees`, which still runs at the next session's
SessionStart per U-HK-26; unrelated to this step.

**Loop mode:** `permission-guard.sh`'s deny-list hard-blocks `git push --force-with-lease`
unconditionally, even in loop mode (branch deletion is a destructive git operation — the
workspace's standing discipline is that these always require an explicit, per-instance human
review, never silent auto-approval, loop mode included). Don't route around this by adding an
allowlist carve-out — that reintroduces exactly the auto-approved-destructive-op pattern the
operator has twice rejected. Instead, when running inside loop mode, defer this step through
the permission guard's allowlisted wrapper — a bare `loop_defer` call is undefined in a fresh
child shell and would silently no-op:
`bash tools/04-loop/defer.sh <arc-id> "branch hygiene close-out pending: <branch>"` — and let the next
interactive session run it.

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
