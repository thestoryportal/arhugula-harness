---
name: ship-pr
description: Open a PR for the current arc, gate the merge through CI-green + the decorrelated `merge-gate` 3-lens review (code-touching PRs), and run the post-merge fixed-point refresh checklist correctly. Use when the operator says "/ship-pr", "ship it", "open the PR", "land this", or when an arc is built+green and ready to merge. Codifies the §12.2 post-merge audit + the §12.2.1 terminating-refresh fixed-point so the roadmap_status.md refresh is done right (and does not recurse). Do NOT use to author code (that is the arc itself) — use it for the PR + gate + refresh ritual.
---

# ship-pr — PR + fixed-point refresh (U-HK-23)

The close half of the roadmap loop. Like `roadmap-continue`, this skill **executes the
canonical §12 protocol** rather than re-stating it — the recipe lives in CLAUDE.md §12.2 +
§12.2.1, read it live so this never drifts (§10.5).

## Pre-flight (before opening the PR)

- **Green.** `just codex-check` + the relevant test suites pass; `bash -n` on any new shell.
  Name the superset gate, not `just check`: `check` omits `codex-parity-check`, so the
  `tools/hooks/test_*.sh` + `tools/statusline/test_*.sh` shell suites that lane runs are
  never executed by it.
- **Grounding pass (U-WT-01).** Before codex round 1: (a) re-read every `file:line` cite in
  the diff and PR body at HEAD — never from recall; (b) recompute every count/arithmetic
  claim from the actual source rather than restating it; (c) confirm every `#NNN` reference
  actually is that PR (`gh pr view NNN --json title`); (d) confirm `just codex-check` ran at the
  *current* HEAD, not an earlier one; (e) state in the PR body that this pass ran. First
  drafts historically burn 5–10 codex rounds on exactly these defect classes — this pass
  collapses them before round 1.
- **`just leg-selfcheck` — run it BEFORE EVERY PUSH, not once per arc.** The mechanical
  half of the grounding pass above, and the only part of it that is cheap enough to repeat
  every round: it re-resolves every `file:line` cite the arc ADDED, reports count claims
  that DISAGREE across mirrors, flags a newly-minted `§label` already owned elsewhere in
  the delta chain, and asserts a touched register row renders a prose body under
  `--detail` (a YAML-only row prints its heading and nothing else). Use `--uncommitted`
  before committing. **Why per-round:** the `B-71` spec leg took ten codex rounds, and
  rounds 7–10 found defects the *absorption rounds themselves* introduced — counts drifted
  five times, `§25.17`/`§25.18` were already CP v1.32's, a code claim was true only under a
  guard that never fires on the defect's own path. Running the global checks once per arc
  cannot catch defects introduced per round; ~7 of that leg's ~12 findings were mechanically
  detectable. Round count, not token count, is the wall-clock cost.
- **The non-mechanical residue is a habit, not a script:** *when you write a sentence about
  what the code does, open the file in the same action.* Both P1s on the `B-71` leg were
  sentences written from a narrative instead of from a call site.
- **Admission attestation (B-215) — the wrapper REFUSES unattested rounds.** For a
  reserved arc, `review-with-failover` exits 3 (`GATE_REFUSED`, not a review terminal)
  unless the round is admitted: round 1 needs a preflight attestation bound to the
  committed diff — run the defect-class-preflight sweep, write the named answers to an
  in-worktree file, COMMIT the work, then `just review-attest-preflight <answers-file>`
  (attest AFTER the final commit; the attestation binds head+digest and goes stale on
  any later commit). After every BLOCK round: absorb, classify each finding, commit,
  then `just review-attest-sweep <answers-file>` — the answers file must name every
  finding_id (the refusal enumerates any it is missing). The round budget is
  `DEFAULT_ROUND_BUDGET` in `tools/review_loop_gate.py` (the one authority on the
  number); exhaustion is the register-and-hold point (`defer.sh` + register row), and
  only an operator extends it (`just review-attest-budget`, deliberately ask-gated).
- **Out-of-family review.** `HARNESS_ARC_ID=<arc-id> HARNESS_LANE_ID=<lane-id> just review-with-failover`
  (branch-vs-`main`; the C-HE-18 fail-closed `codex-review` wrapper with the C-HE-17
  `gemini-review` failover) to convergence — the inline `HARNESS_*` prefix is REQUIRED
  even when ship-pr is invoked standalone: shell exports do not survive across Bash tool
  calls, and a bare invocation writes the wrapper's `branch-*`/`-nolane` fallback ids
  into the C-HE-24/25 rows instead of joining the arc's real reservation (`<arc-id>` from
  the arc-open step; `<lane-id>` from `.harness/.lane-id`) — fix real findings, hermetically regression-test each (§13.1). Exit 0
  APPROVE / 1 BLOCK / 2 `REVIEWER_UNAVAILABLE`; the terminal line on stderr is the verdict,
  never the exit code or the absence of output. *Invariant #3 (restated, C-HE-17 §3):
  out-of-family review covers Codex-authored work as before, AND serves as the D-C failover
  for Claude-authored diffs at the identical bar. Exit 2 (`REVIEWER_UNAVAILABLE` on both
  channels) blocks the arc; record both reasons.* Use `--base` here, NOT
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
  **Adopt the `register-pr-prose` skill for the body and for any register close_out this
  PR carries** — its six rules (head-bound counts, round-bound mechanisms, verified
  cites, no implied partitions, named residuals, close_out written once at the end) are
  the distilled prose-findings history; prose that follows them passes the
  spec-conformance lens on the first read instead of costing a gate round.
- Commit/PR trailers per the workspace convention (Co-Authored-By; 🤖 Generated-with).
- **Reservation back-fill at PR creation (C-HE-03 §3, U-HE-21).** The arc's reservation was
  minted at selection by `roadmap-continue`; its `<arc-id>` is the id you reserved there
  (recover it with `show` if the session compacted — shell exports do not survive across
  Bash tool calls, so pass the id as a LITERAL, never `"$HARNESS_ARC_ID"` in a fresh
  shell). Immediately after `gh pr create`, with `<head-sha>`/`<base-sha>` taken from
  prior `git rev-parse HEAD` / `git rev-parse origin/main` output (no `$( )` — the guard
  auto-allows only single clean invocations):
  ```bash
  uv run python tools/reservations.py update --arc-id <arc-id> --set pr=<N> head_sha=<head-sha> base_sha=<base-sha>
  ```
  If `show --arc-id <arc-id>` reports NO reservation (the headless-degradation case in
  roadmap-continue — the arc opened unreserved because the permission layer refused the
  reserve), SKIP both this back-fill and the final-gate one, and say so in the PR body:
  `update` on a nonexistent reservation aborts, and the arc's reservation will instead be
  minted at closure by the U-HE-19 drain bootstrap.

## Pre-merge gate — CI green + decorrelated 3-lens review (before the merge door)

Once the PR's HEAD sha shows CI fully green (`check-runs`, rerunning known flakes first, per
`[[wait-for-main-ci-green-before-forward-work]]`), and for any PR that touches
`harness-*/src|tests` (or equivalent code surface — skip doc-only and terminating
`ops: roadmap status refresh` PRs), invoke the **`merge-gate`** skill before the merge
door: three parallel Agent-tool subagents (concurrency/race-conditions,
spec-conformance-against-ledgers, test-witness-adequacy), each returning a structured
`VERDICT: APPROVE`/`VERDICT: BLOCK: <reason>` line. All-approve → merge without HIL, per
`[[feedback-merge-without-hil-once-ci-green]]` (CI-green remains the base precondition; this
gate is an additional one for code-touching PRs, not a replacement). Any block or split
verdict → do not merge; automatic fix-and-re-gate is capped at ten rounds. An eleventh
substantive disagreement is the decision point surfaced to the operator via one
`AskUserQuestion` — see the skill for the full procedure, parse-failure handling, and the
audit-log append.

**Final-gate reservation back-fill (C-HE-03 §3 + C-HE-06 §4(ii), U-HE-21).** After the
gate all-approves and BEFORE the merge door: refresh the merge tuple and record the
attested merge tree the door will byte-compare. Obtain the three values first, each as
its own command (`git merge-tree --write-tree` needs git ≥ 2.38; prints the tree OID),
then pass them as LITERALS (no `$( )`; same fresh-shell rule as the PR-creation
back-fill — the arc id is a literal, not an inherited variable):

```bash
git rev-parse HEAD
git rev-parse origin/main
git merge-tree --write-tree origin/main HEAD
uv run python tools/reservations.py update --arc-id <arc-id> --set head_sha=<head-sha> base_sha=<base-sha> attested_merge_tree=<tree-oid>
uv run python tools/reservations.py transition --arc-id <arc-id> --to open --lane-id <lane-id>
```

**The `pending→open` flip happens HERE, pre-acquire (spec v1.4 X4a; U-HE-22).** The
merge-door `acquire()` admits only an `open` reservation held by this lane, so the final
gate opens it the moment the merge tuple is attested (the drain-start flip remains the
closure-capture/bootstrap opener; the CLI transition skips the best-effort
`concurrent_lanes_at_open` sensor, which is `derived`-optional per C-HE-03 §7). Skip when
the arc is unreserved (headless degradation) — and skip when the reservation is already
`open` (a resumed gate pass).

A stale tuple cannot merge: C-HE-06 step (ii) re-confirms head/base against `gh` and
byte-compares the tree at the door (the door primitive landed at U-HE-22; the landing
driver that consumes the attestation lands with U-HE-23). The `update` back-fill is
payload-only and valid on the still-`pending` head; the flip block above then resolves the
formerly-registered flip-timing class (U-HE-19 rev item (vii) → spec v1.4 X4a): the merge
lane opens pre-acquire, drain-start remains the closure-capture opener.

## Land through the merge door (C-HE-06/07, U-HE-28)

After CI green + `merge-gate` all-APPROVE + the final-gate back-fill/flip above, first
**author the next-action pointer** (§12.2 requires the refresh to carry the re-derived
pointer, and the wrapper's fixed refresh string cannot take flags): Write the gitignored
draft `.harness/.next-action-draft` — first line exactly `post-pr: <N>` (this PR's
number), the new pointer prose (ONE paragraph, ending with the "then <next unit>" tail)
below it. The door's refresh consumes the draft iff the number matches this landing and
installs it via the tool's normal `--next-action` path; a mismatched or stale draft is
ignored with a warning and left in place. Then land with the C-HE-07 allowlisted
wrapper — the ONLY merge invocation. The wrapper REQUIRES both ids in its environment
and shell exports do not survive across Bash tool calls, so the prefixed form is the
PRIMARY invocation in every venue (it is also the guard's exact-shape allowlisted form
in loop mode):

```bash
HARNESS_ARC_ID=<arc-id> HARNESS_LANE_ID=<lane-id> bash tools/hooks/safe-merge.sh <pr>
```

(A bare `bash tools/hooks/safe-merge.sh <pr>` works only in a shell where both ids are
already exported — the wrapper aborts pre-lease otherwise.)

This acquires the lease (fail-fast; on `held` it yields — do the next natural gate-pass,
then retry; the wrapper's own `wait_for_door` applies base 30 s ×2 cap 10 min ×12 then
routes `HITL-recoverable`), verifies head/base + `local-base-cas-check` against the
attested tuple, merges with the fixed string, confirms MERGED, flips the reservation,
**holds the lease through the merge SHA's own `main` run and the terminating refresh PR
as a continuation** (`.harness/roadmap_status.md`-only, §12.2.1 shape unchanged — the
door invokes `tools/roadmap_status_refresh.py --emit-refresh-pr-json <pr>`, which
branches from the just-merged `main` tip, runs the mechanical refresh, opens the refresh
PR, and hands `{pr, head_sha}` back for the door to merge under the SAME held lease),
then releases. Exit 0 = landed + refreshed; 3 = door blocked (a `DEFERRED-HIL` row names
`just merge-door-unblock <pr> <sha>`); 4 = re-gate (base moved / door failed); 5 = budget
exhausted (HITL). `just merge-door-status` prints the live lease. Never issue
`gh pr merge` yourself; the guard denies the raw verb in loop mode (C-HE-07).

## Post-merge fixed-point refresh — CLAUDE.md §12.2 + §12.2.1

**The mechanical half now rides the merge door.** The door's §4(viii) continuation above
already ran `just roadmap-status`'s refresh, opened the terminating refresh PR, and merged
it under the held lease — do NOT open a second refresh PR for the same landing (§12.2.1:
one terminating refresh per content merge; the door's is it). The door's refresh carries a
mechanical notes cell and installs the pointer from the `.harness/.next-action-draft` you
wrote above (no draft → the pointer is left untouched, and the standing "then <next
unit>" tail plus the reservation store's terminal-head dedup keep derivation correct;
on the manual recovery path pass `--next-action` to `--emit-refresh-pr-json` directly).

What ship-pr still owes after the door releases: the `--archive-superseded` content-PR
step below (it rides the NEXT substantive PR, never the refresh), the R-NNN registry
prose, and the reflect/exit-report/metrics steps at the end of this skill.

The manual recipe below is retained for the RECOVERY path only — a blocked door
(`refresh_skipped_by_operator`, `record-refresh`/`clear-refresh-intent`) or a checkout
where the door cannot run. (An unreserved/headless arc has no door path at all until the
U-HE-19 drain bootstrap mints its reservation at closure — it reaches this section only
through that bootstrap, never by a raw merge, which the guard denies.) On that path,
after the PR merges:

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
   **The `## Next action` pointer is now SPLICED, not hand-edited.** Its prose
   is still agent-authored (as is `--notes`), but hand-editing the paragraph is
   what reddened `main` on 2026-08-13: commit `49b00f85` re-pointed it by hand
   without re-running the tool, so the anchor still recorded a `git_head` two
   commits back, `codex_context_guard._is_terminating_refresh_commit` (which
   requires a refresh commit's recorded `git_head` to equal its OWN parent)
   rejected it as a verified refresh point, and CI hard-failed
   `ROADMAP_STATUS_DRIFT` in both the guard job and `test_codex_stop_gate`.
   Install it with the TOOL instead, in two guard-clean steps:

   **The next-action pointer is installed BY THE TOOL, inside the terminating
   refresh — never hand-edited:**
   ```
   just roadmap-status --refresh --pr "PR #<NNN>" --date <YYYY-MM-DD> \
     --notes "<what shipped>" --next-action "<new pointer prose, ONE paragraph>"
   ```
   This installs the pointer AND refreshes the anchor in one single-file write,
   so `_lag_expected` covers it. Hand-editing the paragraph is what reddened
   `main` on 2026-08-13 (`49b00f85` left the anchor recording a `git_head` two
   commits back, so it was not a verified refresh point).

   **Never put a `roadmap_status.md` edit in a substantive content PR.** A commit
   on `main` touching it without being a verified terminating refresh satisfies
   neither guard exception, and `main`'s post-merge CI hard-fails.

   **Archive the SUPERSEDED round (N−1) inside the substantive content PR:**
   ```
   just roadmap-status --archive-superseded
   ```
   It reads the most recent round that is no longer live from the head's own git
   history and appends it to `.harness/roadmap-next-action-archive.md` as `Prior`.
   Archive-only write, so the content merge stays the single non-refresh commit
   `_owed_lag` tolerates.

   **Why N−1 and not the live round** (`B-168`, resolved exit (iii)): three
   constraints collide — the archive is PRIOR-rounds-only, the refresh may touch
   only `roadmap_status.md`, and `_owed_lag` tolerates exactly one non-refresh
   commit after a refresh. Archiving the round that is still current satisfies
   the first two and breaks the third's premise; archiving N−1 satisfies all
   three **unchanged**, and is exactly what the archive's own header has always
   specified. The archive therefore lags by one arc BY DESIGN; the live head's
   git history is the lossless record meanwhile.

      `--refresh` REFUSES to write a second file rather than silently producing a
   two-file commit; if it says a drift-log trim is owed, run `--trim-drift-log`
   as its own step — and if the overflow comes from a NEW drift event, pass it
   there (`--trim-drift-log --drift-source ... --drift-resolution ... --date ...`),
   since pre-trimming cannot help with a row that does not exist yet.

   Both `--check` and `--refresh` print the remaining byte headroom. The
   drift-log byte budget is INFORMATIONAL (the hard cap is the whole-file
   `HEAD_BYTE_BUDGET`), so it tells you where to reclaim bytes without redding CI.
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
#    print and fall through). Accepted set is exactly `{success}`; `cancelled` and `failure`
#    are named INCOMPLETE (C-HE-19; the one predicate is `arc_metrics.ci_is_green`). Do not
#    infer green from the absence of a failure.
concl=$(gh run list --commit "$merge_sha" --json conclusion --jq '.[0].conclusion // empty')
case "$concl" in
  cancelled|CANCELLED) echo "ABORT: post-merge CI on main was CANCELLED — INCOMPLETE, never green (C-HE-19)"; exit 1 ;;
esac
[ "$concl" = success ] || { echo "ABORT: post-merge CI on main is not confirmed green (got '${concl:-empty}')"; exit 1; }

# 3. If a `--delete-branch` merge already removed the ref, there's nothing left to
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
  2) echo "Already gone (a --delete-branch merge or a prior run) — nothing to do." ;;
  *) echo "ABORT: could not verify remote ref state (ls-remote exit $rc — network/auth issue?)"; exit 1 ;;
esac
```

**The door's refresh branch is a second known branch — close it out the same way.** Each
landing pushes `roadmap-refresh-post-<content-pr>` for the §4(viii) continuation, the
repo does NOT auto-delete merged head branches (`deleteBranchOnMerge: false`), and the
door's fixed merge string carries no `--delete-branch` — so successful arcs accumulate
refresh branches unless this step covers them (U-HE-28 codex r2). The branch name is
deterministic from the content PR you just landed — recover the refresh PR's number from
it (the wrapper prints only `released`, so this lookup, not door output, is the source):

```bash
gh pr view roadmap-refresh-post-<content-pr> --json number,state,mergeCommit
```

Then run the same guarded block a second time with `<PR#>` = that number and
`expected_branch=roadmap-refresh-post-<content-pr>`; its step-2 post-merge-CI check is
the run the door already confirmed green before releasing.

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

## Arc exit report — the last reporting step (U-WT-03/04)

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
re-run overwrites it) and indexes one `EXIT-REPORT` row into the shared `loop_status.md` (`$(loop_status_path)`; default `~/.gstack/projects/arhugula-v2/loop_status.md`).
Paste the emitted `yaml` block into this turn's final message: it is the arc's
machine-readable closure record, and every field is collected or explicitly null — a
missing refresh reads `refresh_commit: null` and a non-green CI reads its conclusion
verbatim, so the block is evidence, not narration. Read what it says before pasting: a
null `refresh_commit`, a `main_ci.conclusion` that is not `success`, or
`checkpoint.confirmed: false` each mean an obligation above is still open.

## Arc-metrics capture — after the exit report (B-170)

Capture is two steps that deliberately sit in **different arcs**: this arc *queues* its
inputs, the next arc *folds* them into the ledger. Skip both on a terminating
roadmap-status refresh (§12.2.1) — a refresh is not an arc.

**Step 1 — queue, at closure (writes NOTHING to the repo).** After the exit report above,
because `merged_at` and the merge SHA do not exist before merge:

```
just arc-metrics queue --pr <NNN> --arc-type <inventing|applying> --decisions <N> \
  --round-logs '<glob for THIS arc's round logs>' --levers <lever-ids-or-omit>
```

This writes one file per arc into a queue directory **outside** the repo. That placement is
load-bearing, not tidiness: in an autonomous arc this step runs inside the topic worktree,
and writing the tracked ledger there would leave a dirty file that both strands the row when
the worktree is disposed and *blocks the disposal itself* — worktree GC skips a merged
worktree carrying local state, while loop completion requires that worktree to be
unregistered. Committing straight to `main` instead is no escape: before the terminating
refresh the drift guard hard-fails the push, and after it the next local preflight
hard-fails and demands another refresh.

One file per arc rather than a shared log is also deliberate: parallel lanes queue
concurrently, and a shared append-log makes loss structural (two writers on one inode, a
drain rewriting from a stale snapshot). Re-queueing the same arc is refused rather than
silently overwriting the first session's declarations.

`--arc-type`, `--decisions` and `--levers` are **declared** judgements — the tool records
them as such and never infers them, and this session is the only one that knows them, which
is precisely why they are queued rather than reconstructed later. Omitting `--levers`
records the empty baseline cohort `[]`, which is a claim in itself: it says no wall-clock
lever was live. Do not pass it loosely — every efficacy comparison B-171..B-174 makes is a
cohort split on that field.

**Step 2 — drain, inside the NEXT arc's PR.** Early in the next arc, before opening its PR:

```
just arc-metrics drain
```

This folds every queued arc into `.harness/arc-metrics.jsonl` as an ordinary tracked change,
committed inside that arc's own PR (`git add .harness/arc-metrics.jsonl` — never
`git add -A`). A doc-only sweep can still carry the row — `.harness/*.jsonl` is not
`harness-*/src|tests`, so it does not drag the diff through the 3-lens merge-gate.

**`drain` exits non-zero while anything is still outstanding, and that is not a failure.**
A queued capture is released only once its row appears in **merged history** (`origin/main`),
because until then the declarations it carries exist nowhere else — a working-tree change is
obviously not durable, but neither is a topic-branch commit: that branch can still be reset,
abandoned, or have its worktree disposed. So the normal sequence is: `drain` (exit 1, "entry
held until the row is committed") → commit and **merge** the row → the *next* arc's `drain`
releases the entry (exit 0). A non-zero exit means "work is still outstanding", which also
covers a capture that failed and a claim held by a live peer. Only treat exit 0 as "nothing
left to fold".

Read the folded rows before moving on. `--round-logs` fails closed (zero matched files
aborts rather than recording `0 rounds`), and a `provenance` value beginning `unmapped:`
means that field had no input — an honest null, not a measured zero. A lever must never be
evaluated against one.

## Notes

- The Wave-1 `post-merge-refresh.sh` hook pre-computes the new hash + injects the §12.2
  checklist on a substantive merge — trust it as a cross-check, but the refresh is still the
  agent's to land.
- Canonical text wins on any disagreement — re-read §12.2 / §12.2.1.
