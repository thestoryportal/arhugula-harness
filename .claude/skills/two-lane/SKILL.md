---
name: two-lane
description: Operator-invoked pilot recipe for running TWO roadmap arcs in parallel worktrees while keeping every merge and every terminating refresh strictly serial through ship-pr. Use when the operator explicitly asks for two lanes ("/two-lane", "run two arcs in parallel", "open a second lane") — it is never auto-selected from roadmap-continue or ship-pr. It is a recipe, not machinery: no spawner, no merge queue, no conflict automation.
---

# two-lane — two arcs building in parallel, one merging at a time

Two arcs can be *built* concurrently. They cannot be *landed* concurrently: CLAUDE.md §12.2.1
gives the merge lane a single fixed point, and every landing has to pass through it in order.
This recipe is the whole feature — a discipline written down, running on machinery that already
exists (`git worktree`, `ship-pr`, `tools/hooks/safe-worktree-remove.sh`). Nothing here is
automated, deliberately (see the CUTs at the end).

## Opt-in only

**Opt-in only — never auto-invoked from `roadmap-continue` or `ship-pr`.** It fires on an
explicit operator request. Pick the two arcs so their `scope.files` do not overlap; that
selection is a judgment call at v1 — the analyzer for it (`tools/arc_disjoint_check.py`,
U-WT-07) is deliberately unbuilt until this pilot proves lane selection is the bottleneck.

## Lane setup

Each lane gets its own worktree under `.codex-worktrees/<slug>` — the existing, already-ignored
worktree root (`.gitignore:103`), and one of the two roots the permission guard admits for both
worktree creation and guarded removal (`tools/hooks/permission-guard.sh:179` and `:203`):

```bash
git fetch origin
base=$(git rev-parse origin/main)   # pin ONCE — a concurrent session's fetch can advance
git worktree add <repo-root>/.codex-worktrees/<slug-a> -b <branch-a> "$base"
git worktree add <repo-root>/.codex-worktrees/<slug-b> -b <branch-b> "$base"
```

Both lanes branch off the **same** pinned base SHA (resolving `origin/main` twice is a TOCTOU:
any other session's SessionStart hook fetches on every start and can advance the ref between
the two adds). Each lane then runs its arc's BUILD
half normally — build, test, `just check`, grounding pass, out-of-family review — entirely
inside its own worktree. Nothing about the build half is serialized. **`merge-gate` and the
final-head CI check are NOT build-half steps**: the gate runs immediately before merge, appends
the shared `.harness/merge-gate-log.md`, and its approvals must cover the branch that will
actually merge — so lane B runs them only inside its own merge sequence, after lane A's
terminating refresh has landed (below).

## The merge lane — strictly serial

**Merges and terminating refreshes are STRICTLY SERIAL through `ship-pr`. §12 is unchanged by
this skill** — this recipe adds no governance, weakens no gate, and introduces no alternative
landing path. The §12.2 post-merge audit and the §12.2.1 terminating-refresh fixed point apply
to each lane's PR exactly as they do to a single-lane arc.

**One lane holds the `ship-pr` fixed point at a time.** Concretely, lane B does not begin its
merge sequence until lane A's *terminating refresh PR has merged* — not merely lane A's content
PR. The refresh is what returns `.harness/roadmap_status.md` to the fixed point; a second merge
landing between lane A's content PR and its refresh leaves an accumulated two-commit drift that
hard-fails `tools/codex_context_guard.py` for everyone (CLAUDE.md §12.2.1, CI-side
generalization). So the order is: A content → A refresh → B content → B refresh. Lane B keeps
building while it waits; only its merge sequence blocks.

**Lane B's merge sequence starts with a replay, then the FULL ship-pr flow — not a jump to the
gate.** Once lane A's terminating refresh has merged AND its `main`-push CI has concluded green
(a pending or red refresh CI means the base is unverified — wait), lane B fetches and replays
onto the refreshed `origin/main` (fresh branch off refreshed main + re-apply, per the conflict
section below — this is unconditional, not just for visible conflicts: lane A's merge-gate run
appended the shared `.harness/merge-gate-log.md`, so stale lane B's own log append would
conflict at the table tail every time). Then lane B restarts the whole `ship-pr` sequence on
the replayed branch: a **replacement PR** (the original PR is attached to the abandoned branch
and never merges — **close the original PR first** with a comment pointing at the replacement,
and reconcile its stale remote branch per ship-pr's stale-branch flow, operator-handed where
deletion is privileged, so the replacement doesn't merge around an open ghost in the in-flight
inventory), out-of-family review of the **current** diff (conflict-driven redone edits
were never covered by the pre-replay review), `merge-gate`, and final-head CI. Gate approvals,
reviews, and CI are branch-and-HEAD-bound evidence; recording any of them before the replay
would attest to a branch that never merges.

## On merge conflict — abandon and rebase

If lane B's PR conflicts with the now-refreshed `main`, **abandon the second lane's branch and
rebase it on the refreshed main — no merge-order heuristics, no cherry-pick rescue of a
conflicted merge.** Do not reorder the lanes to make the conflict go away, do not try to land
B first because it looks smaller, do not hand-resolve a merge commit.

Two guard facts shape how that is actually executed:

- `git rebase` is hard-denied by the permission guard (`tools/hooks/permission-guard.sh:325-326`,
  "git history rewrite"). The rebase is therefore realized as: branch fresh from the refreshed
  `origin/main` and re-apply lane B's work there (`git cherry-pick <sha>...` on the *clean* new
  branch, or simply redo the edits — the arc is small by construction).
- Deleting the abandoned branch is a privileged operation: `git branch -d` refuses an unmerged
  branch and forced `-D` is hard-denied (`tools/hooks/permission-guard.sh:327-328`). Abandoning
  means *not merging it*; leave the branch in place and hand the operator the deletion command
  if it needs to go.
- **The durable prune reminder is a TRACKED row, shipped in the replacement PR:** append the
  abandoned branch's name + the operator's exact prune command to
  `.harness/two-lane-pending-prunes.md` (create the file on first use; the operator deletes
  the row when pruning). No gitignored, worktree-local surface can carry this reminder — the
  loop ledger in particular is deleted with the reaped worktree or wiped at the next loop
  activation, and the merged-refs-only hygiene sweeps cannot see an unmerged branch — so a
  tracked file in the repo is the only home that survives until the operator acts. Until the
  row is cleared, it also answers the pre-merge branch-hygiene precondition: the branch is
  accounted for, not stray.

## Reaping a lane

A finished lane's worktree is **reaped ONLY via `tools/hooks/safe-worktree-remove.sh`**:

```bash
bash tools/hooks/safe-worktree-remove.sh <repo-root>/.codex-worktrees/<slug>
```

Direct `git worktree remove` is denied for live-session-registered worktrees
(`tools/hooks/permission-guard.sh:56-70`; the deny is session-scoped, with a deliberate
`HARNESS_ALLOW_LIVE_WORKTREE_REMOVE=1` escape hatch — not unconditional) — removal
and SessionStart lease registration must share one mutex, or the removal orphans a live session.
A nonzero exit is a real refusal, not a retry prompt: 3 = live session, 4 = local state,
7 = retained process references (`tools/hooks/safe-worktree-remove.sh:45-57`). Surface it; never
force it.

## Deliberate CUTs

**No spawner script, no merge-queue lock, no conflict automation.** Each is cut for a reason,
not for lack of time:

- **No merge-queue lock.** The §12.2.1 fixed point already admits exactly one in-flight landing,
  so the queue is *structurally depth-1 — a lock is ceremony* on top of an invariant the roadmap
  protocol enforces anyway.
- **No spawner.** Two `git worktree add` lines are not a program.
- **No conflict automation.** The abandon-and-rebase rule above is total; automating it would
  encode merge-order heuristics, which is precisely what the rule forbids.

**Follow-on orchestration is registered only after ≥3 manual pilot runs surface a named
recurring pain** — a specific, repeated, described friction, not a hypothetical one. Until then
this file is the whole feature.
