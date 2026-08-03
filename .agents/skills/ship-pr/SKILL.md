---
name: ship-pr
description: Use when the operator says /ship-pr, ship it, open the PR, land this, or a completed arhugula-v2 arc must pass review, CI, merge, refresh, and cleanup.
---

# Ship PR

Close an arc through the same fixed-point workflow used by the Claude runner. Read
`AGENTS.md`, `.codex/notes/discipline-digest.md`, and the live `CLAUDE.md` §12.2/§12.2.1
before executing; those authorities win if this summary drifts.

## Preflight and local gates

1. Confirm the absolute worktree path, branch, status, and merge-base diff. Never mutate
   the shared root checkout and never use `git add -A`.
2. Recompute affected roadmap, register, ledger, and cite surfaces before committing.
3. Run the narrow witness first, then `just codex-check` for a substantive PR. Run
   `just overlay-check` for cite/CXA-bearing changes and `bash -n` for shell changes.
4. Run `just codex-closeout`. If the diff changes afterward, re-run every affected gate.
5. Review the actual diff, stage only explicit paths, and inspect the staged diff.

Use the real worktree as `cwd` rather than `git -C` so durable command-prefix approvals
match. The normal command shapes are:

```bash
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
git diff --merge-base main
git add -- <explicit-path> [<explicit-path> ...]
git diff --cached --stat
git diff --cached
```

## Grounding pass (U-WT-01)

Before the first out-of-family review round: re-read every `file:line` cite in the diff
and PR body at HEAD — never from recall; recompute every count/arithmetic claim from the
actual source rather than restating it; confirm every `#NNN` reference actually is that
PR; confirm local gates ran at the *current* HEAD; state in the PR body that this pass
ran. First drafts historically burn 5–10 review rounds on exactly these defect classes.

## Authorship-dependent out-of-family review

- When Codex authored the change, run `just gemini-review`. Despite its legacy recipe
  name, it invokes the Antigravity `agy` subscription CLI with provider API environment
  variables stripped. Require exit 0, non-empty output, and final `VERDICT: APPROVE`.
- When Claude authored the change, `just codex-review` is the out-of-family gate.

A BLOCK means fix, add a regression witness where applicable, re-run local gates, and
review the new diff again. Never count self-review by the authoring model as decorrelated.

## Commit, PR, and CI

1. Commit the explicit staged scope and push the topic branch.
2. Open or update the PR. Its body names the tracking surfaces updated (or why none apply),
   exact verification results, skipped checks, and design/back-flow posture.
3. Watch every required PR check on the final PR HEAD and every required check on the current
   base `main` HEAD to a terminal green conclusion. Pending, missing, empty, cancelled, or
   skipped-required checks are not green. Inventory open PR and remote topic branches before
   merge; if a stale prior branch exists, inspect its PR/worktree/unique commits and reconcile
   it without deleting or overwriting work.
4. Run the `merge-gate` skill for every substantive code or hook PR after PR CI is green
   and out-of-family review has converged. This is the fresh three-lens gate, not a second
   generic review. A documentation-only or terminating-refresh PR may take a proportional
   skip, but the skip and evidence must be logged.
5. Append the result to `.harness/merge-gate-log.md`, commit and push that row, then wait
   for CI on the final PR HEAD to be green again. If a code fix follows any approval,
   re-run out-of-family review and the affected lens against the delta.

Merge only when the operator's request or standing autonomous-loop authorization includes
merge. All three lenses must approve and final-HEAD CI must be green. Never use `--admin` to
bypass protection.

```bash
git commit -m "<conventional title>"
git push -u origin <topic-branch>
gh pr create --base main --head <topic-branch> --title "<title>" --body-file <body-file>
gh pr checks <PR#> --watch
gh pr merge <PR#> --squash --match-head-commit <final-head-sha>
```

Validate each external call before using its output: exit 0, non-empty JSON where expected,
and the requested PR/head SHA. Do not interpolate an empty PR number, SHA, branch, or run id.

## Post-merge fixed point

1. Record the merge SHA and wait for the merge commit's own main CI run to conclude green.
   PR CI is not a substitute. Do not begin forward work while main CI is pending or red.
   Discover runs with `gh run list --branch main --commit <merge-sha> --event push
   --json databaseId,status,conclusion,headSha`; require at least one matching run, watch every
   returned run with `gh run watch <run-id> --exit-status`, then re-query and require every
   conclusion to equal `success`.
2. Perform branch hygiene only against the exact merged PR/head OID. Recheck remote state;
   do not infer squash-merge ancestry. Preserve any branch with new or unmerged work.
3. Run `python3 tools/roadmap_status_refresh.py --refresh --pr "PR #<N>" --date
   <YYYY-MM-DD> --notes "<summary>"`, update the hand-authored next action, then run
   `python3 tools/roadmap_status_refresh.py --check`.
4. Land the terminating refresh as the immediate next commit/PR. Its title starts exactly
   `ops: roadmap status refresh ` and its closed changed-file set is only
   `.harness/roadmap_status.md`. Do not recurse on a terminating refresh.
5. Wait for the refresh merge's own main CI to be green, fast-forward local `main`, remove
   the clean arc worktree, and prune only the verified merged local topic branch.
6. Record loop gates through `worktree_disposition` and require `just codex-loop-check`.

## Reflect and checkpoint

Before the next arc, reflect on new recurrent lessons and run the gstack `context-save` skill.
Update durable agent memory only when the operator explicitly requests it and the active host
memory policy permits it; context-save itself remains mandatory. A checkpoint's remaining-work
prose is advisory, so verify it against HEAD when resuming. After the fixed point, create the
next isolated worktree and run `just codex-autonomous-arc <next-arc-id>`. Skip reflection only
for a pure terminating-refresh PR.
