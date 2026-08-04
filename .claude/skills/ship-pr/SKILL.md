---
name: ship-pr
description: Open a PR for the current arc, gate the merge through CI-green + the decorrelated `merge-gate` 3-lens review (code-touching PRs), and run the post-merge fixed-point refresh checklist correctly. Use when the operator says "/ship-pr", "ship it", "open the PR", "land this", or when an arc is built+green and ready to merge. Codifies the §12.2 post-merge audit + the §12.2.1 terminating-refresh fixed-point so the roadmap_status.md refresh is done right (and does not recurse). Do NOT use to author code (that is the arc itself) — use it for the PR + gate + refresh ritual.
---

# ship-pr — PR + fixed-point refresh (U-HK-23)

The close half of the roadmap loop. Like `roadmap-continue`, this skill **executes the
canonical §12 protocol** rather than re-stating it — the recipe lives in CLAUDE.md §12.2 +
§12.2.1, read it live so this never drifts (§10.5).

## Pre-flight (before opening the PR)

- **Green.** `just check` + the relevant test suites pass; `bash -n` on any new shell.
- **Grounding pass (U-WT-01).** Before codex round 1: (a) re-read every `file:line` cite in
  the diff and PR body at HEAD — never from recall; (b) recompute every count/arithmetic
  claim from the actual source rather than restating it; (c) confirm every `#NNN` reference
  actually is that PR (`gh pr view NNN --json title`); (d) confirm `just check` ran at the
  *current* HEAD, not an earlier one; (e) state in the PR body that this pass ran. First
  drafts historically burn 5–10 codex rounds on exactly these defect classes — this pass
  collapses them before round 1.
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

## Pre-merge gate — CI green + decorrelated 3-lens review (before `gh pr merge`)

Once the PR's HEAD sha shows CI fully green (`check-runs`, rerunning known flakes first, per
`[[wait-for-main-ci-green-before-forward-work]]`), and for any PR that touches
`harness-*/src|tests` (or equivalent code surface — skip doc-only and terminating
`ops: roadmap status refresh` PRs), invoke the **`merge-gate`** skill before running
`gh pr merge`: three parallel Agent-tool subagents (concurrency/race-conditions,
spec-conformance-against-ledgers, test-witness-adequacy), each returning a structured
`VERDICT: APPROVE`/`VERDICT: BLOCK: <reason>` line. All-approve → merge without HIL, per
`[[feedback-merge-without-hil-once-ci-green]]` (CI-green remains the base precondition; this
gate is an additional one for code-touching PRs, not a replacement). Any block or split
verdict → do not merge; automatic fix-and-re-gate is capped at ten rounds. An eleventh
substantive disagreement is the decision point surfaced to the operator via one
`AskUserQuestion` — see the skill for the full procedure, parse-failure handling, and the
audit-log append.

## Post-merge fixed-point refresh — CLAUDE.md §12.2 + §12.2.1

This is the step most often done wrong. After the PR merges:

1. **§12.2, mechanical half — run the script, don't hand-Edit.** Per
   `[[roadmap-ledger-edits-via-idempotent-script]]`, `.harness/roadmap_status.md`'s
   anchor table / in-flight PR table / capped `recently_completed` + `Drift detection
   log` tables are owned by `tools/roadmap_status_refresh.py` (`just roadmap-status`),
   not the `Edit` tool — long single-line table rows are exactly where `Edit`'s
   old_string matching goes stale (`String to replace not found`) or races a
   not-yet-`Read` file. Run:
   ```
   just roadmap-status --refresh --pr "PR #<NNN>" --date <YYYY-MM-DD> \
     --notes "<one-line agent-authored summary of what shipped>" \
     [--drift-source "..." --drift-resolution "..."]
   ```
   This recomputes `workspace_state_hash` (byte-parity-tested against
   `tools/hooks/lib.sh`'s `hook_state_hash`), sets `last_refreshed`/`git_head`/
   `latest_retirement_batch`/`open_fork_doc_count`, regenerates `in_flight` from
   live `gh pr list`, prepends+caps `recently_completed` (dedup by PR ref), and
   caps the `Drift detection log` at 10 — overflow moves (never deletes) into
   `.harness/roadmap_drift_log_archive.md`. Use `--dry-run` to preview the diff
   first on a high-stakes refresh. `just roadmap-status-check` is the CI/pre-commit
   gate (cap violations or a real hash mismatch = exit 1).
   **Still hand-authored, by design (not machine-derivable):** the `## Next
   action` prose block and the `--notes` text itself — write those as before,
   the script only splices them into a structurally-guaranteed-correct skeleton.
   Mark any closed `R-NNN` RESOLVED + propagate `next_pointer` (still by hand — the
   R-NNN registry prose is out of the script's mechanical scope).
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

On a closed R-NNN: if the close surfaced a `[[pattern]]` at cardinality ≥2, write the topic
memory file (`~/.claude/projects/<slug>/memory/<pattern-slug>.md`) as before, then land its
`MEMORY.md` index line via the byte-cap-gated script rather than a hand `Edit` — the file has
a hard 24,400-byte cap and the "measure once, trim in one pass" discipline (root `CLAUDE.md`
§14) is exactly what `tools/memory_compact.py` enforces mechanically:
```
just memory-compact --upsert <path-to-MEMORY.md> --slug <pattern-slug> \
  --line "- [Title](pattern-slug.md) — one-line hook"
```
This is idempotent (re-running with the same `--slug` replaces the line in place, never
duplicates) and **refuses to write** if the result would exceed the cap — instead of landing
an over-cap file, it reports the overage/headroom so an existing entry gets trimmed first. If
a close superseded an existing entry, refresh it the same way (or `--remove` if it's now
dead); `just memory-compact --check <path>` reports the current byte/cap/headroom without
writing. (Checkpoint hygiene per §12.5.3: a checkpoint is "resolved" when its `branch:` is
merged; PreCompact snapshots are keep-10-pruned by `session-end-cleanup.sh`; resolved-checkpoint
archival is optional and not automated — no standing "archive Remaining-Work-addressed" step.)

## Reflect + `/context-save` — mandatory, every arc close (not just R-NNN closes)

**This step is not optional and does not wait to be asked.** CLAUDE.md §15 (reflect for
self-improvement) + §12.5.2 (checkpoint disciplines) both fire at every arc's completion —
that means every time this skill reaches this point, not only when an R-NNN closed. Skipping
it was a recurring failure before this step existed in the skill file
(`[[feedback-autonomous-loop-dont-stop-to-ask]]` — 5 recorded instances across #640, #642,
#723, and 2026-07-15's PRs #1009 + #1011, corrected only when the operator asked directly
whether the discipline had run). A memory paragraph alone was not a reliable trigger; this
skill step is.

Before handing off to the next arc (whether via `ScheduleWakeup`, `/loop-stop`, or simply
ending the turn):

1. **Reflect.** Ask: did this arc surface anything genuinely new or recurrence-likely — a
   pattern, a corrected assumption, a tooling gotcha, a process gap? Not "what did I do"
   (that's the PR body) — "what would a future session want to know before repeating this."
   If nothing qualifies, say so explicitly rather than skipping the step silently.
2. **Save it.** Per the auto-memory discipline (global `~/.claude/CLAUDE.md`): cardinality ≥2
   patterns and any explicit user feedback (correction OR confirmation) get saved/updated —
   fold into an existing entry when one matches, don't duplicate. Land the `MEMORY.md` index
   line via `just memory-compact --upsert` (above), never a hand `Edit`.
3. **Run `/context-save`.** Even if the next action is "stop the loop" — a saved checkpoint is
   what makes the next session's resume cheap and honest, per
   `[[feedback-checkpoint-remaining-work-is-advisory-not-authoritative]]`.

Skip only when this PR was itself the terminating roadmap-status refresh (§12.2.1) — a
refresh-only commit has no new learnings to reflect on.

## Arc exit report — the LAST step (U-WT-03/04)

**After** the reflect + `/context-save` block above, not before it. That ordering is the
whole point: the merge SHA, the post-merge main-CI conclusion, the §12.2.1 refresh commit
**and** the checkpoint you just wrote all exist only at this point, so the report records
the arc's *real* final checkpoint rather than a stale or fabricated one. **Skip this step
entirely when the PR was itself the terminating roadmap-status refresh (§12.2.1)** — the
same rule as the reflect block above: a refresh-only PR is not an arc, owes no report, and
running it would mislabel its structurally-absent refresh as an open obligation. Run:

```
just arc-exit-report --pr <NNN> --merge-sha <merge-sha> --checkpoint <the-path-/context-save-just-reported>
```

Pass `--checkpoint` explicitly — the roadmap authorizes a **parallel frontier**, so another
live session can `/context-save` between your save and this collection; mtime cannot tell
whose checkpoint is whose, so an unbound run reports the workspace-newest file as an
unconfirmed heuristic and `checkpoint.confirmed` stays `false`. Only the path *your*
`/context-save` step just reported binds the report to this arc.

It writes `.harness/.checkpoints/arc-exit-report-pr<NNN>.md` (gitignored, PR-keyed — a
re-run overwrites it) and indexes one `EXIT-REPORT` row into `.harness/loop_status.md`.
Paste the emitted `yaml` block into this turn's final message: it is the arc's
machine-readable closure record, and every field is collected or explicitly null — a
missing refresh reads `refresh_commit: null` and a non-green CI reads its conclusion
verbatim, so the block is evidence, not narration. Read what it says before pasting: a
null `refresh_commit`, a `main_ci.conclusion` that is not `success`, or
`checkpoint.confirmed: false` each mean an obligation above is still open.

## Notes

- The Wave-1 `post-merge-refresh.sh` hook pre-computes the new hash + injects the §12.2
  checklist on a substantive merge — trust it as a cross-check, but the refresh is still the
  agent's to land.
- Canonical text wins on any disagreement — re-read §12.2 / §12.2.1.
