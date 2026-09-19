# Cutting arc wall-clock to a one-hour average

## The answer

A one-hour average is reachable, but only if review stops running until convergence. Review rounds take 64% of every measured arc hour in this repo. No other change moves the mean far enough on its own.

Your friend's workflow gets its speed from three habits this repo lacks:

- a fixed review cycle of at most four passes per PR, run once;
- no per-merge status PR, because project state lives in a tracker database;
- sessions that reset themselves before their context drains.

Adopting those three, plus smaller PRs, projects the mean from about 177 minutes to about 55 to 65 minutes (estimate, derivation below).

The price is real. A third of the P1/P2 findings this repo accepted in the last two weeks were first raised at review round six or later. A bounded cycle will ship some of those defects, or catch them later as follow-up tickets. That trade, and two governance changes it needs, are decisions only you can make. They are listed at the end.

## Where the time goes today

The cohort is the last 40 content merges to main, 2026-09-03 to 2026-09-18. Thirty had a full reservation lifecycle and are fully measured. The method reproduces the independently audited U-HE-42 figure (547 min) within 1%.

| Measure | Value |
|---|---|
| Arc wall-clock, reservation to content merge to refresh merge | median 126 min, mean 177 min |
| Code-touching arcs (22 of 30) | median 203 min |
| Doc-only arcs (8 of 30) | median 33 min |
| Worst arc (#1561, three-lane pilot) | 828 min, 11 codex rounds + 14 lens rounds |

| Phase | Share of the 88 measured hours | Mean per arc |
|---|---|---|
| Review loop: codex rounds and merge-gate lens rounds, non-overlapping span | 64% | ~114 min |
| Merge door dwell: post-merge main CI, then the refresh PR and its CI | 16% | ~28 min (median 11) |
| Build and grounding before the first review | 10% | ~18 min |
| CI wait and merge execution after the last review | 10% | ~17 min |

Four further facts shape the fix.

**The time is spent before and around the PR, not in it.** Once a content PR is open, this repo merges it in a median of 43 minutes and a mean of 90, across 105 PRs since 2026-08-16. That is as fast as your friend's repos: memento has a median of 40 and a mean of 379 over 18 PRs, lit a median of 34 and a mean of 280 over 100. The hours go into local review rounds that run before and alongside the PR.

**Review is not front-loaded here.** Of 209 accepted P1/P2 findings, 37% came in rounds 1–2, 29% in rounds 3–5 and 34% in rounds 6 and later. Codex needs a median of 7 rounds per arc to reach a terminal verdict, at roughly 16 minutes per round (reviewer runtime of 5–9 minutes, plus absorb, re-attest and relaunch). Earlier notes in this repo record that absorption rounds introduce defects of their own. So part of the late-round yield is plausibly the loop catching its own fixes; this is an inference, not measured.

**Half of all merges are bookkeeping.** 95 of the last 200 merged PRs were terminating roadmap-refresh PRs, 1.1 content PRs per refresh. Each holds the global merge lease through a second CI run. In the three-lane pilot, five refreshes failed CI or needed a correcting PR, each blocking the door for every lane. A further 13 of the 40 content merges were repair or residual commits spawned by an earlier arc.

**PRs are large.** Median lines changed per content PR: this repo 619, lit 438, memento 149.

## What his repos do, and what transfers

### The fixed review cycle (dotfiles)

`config/claude/CLAUDE.md`, lines 57–72, fixes the review cycle for every PR:

1. `/code-review high`
2. `/code-review medium`
3. `/code-review high` again only if the medium pass found a major finding. "The escalation runs at most once."
4. `/code-review low` as the merge gate, re-run only until no P0 remains.

The whole cycle "runs ONCE per PR". New work pushed afterwards gets exactly one more review, sized to the change. `/code-review` is Claude Code's built-in review command, which this repo already has.

memento and lit add a CI-side reviewer, `promptctl/copirate-code-review-agent@v1`. It runs on every push, in parallel with CI rather than after it. A newer push cancels the in-flight review (`cancel-in-progress: true`), and it is hard-capped at `MAX_REVIEW_ROUNDS: "5"`.

memento's `address-pr-reviews` skill works the findings as PR threads. Every finding gets a plan comment. Wrong findings are rejected with a cited law rather than absorbed. The loop ends when a fetch returns zero open threads.

**Transfer:** replace the codex-to-convergence loop, the three-lens gate after CI, and the per-round attestation templates with one bounded cycle. It runs alongside CI, and pushes back on wrong findings instead of absorbing them.

### State in a tracker, not in a status file that needs its own PR (lit, with the dolt fork as its storage)

`lit next` computes each checkout's next unit live from states, dependencies and claims (`internal/cli/next_route.go:337-419`). A unit another checkout holds is routed around (line 274). Claims are derived from the event log plus `git worktree list`, so there is no lock file to go stale. Concurrent edits merge field by field in Dolt, with no git conflicts on shared ledgers. Closing work is `lit done <id>`, a database write. No PR rewrites a status file, so no CI drift guard can fail.

**Transfer:** this removes the per-arc refresh PR, the single-pointer selection collisions the pilot hit, and ledger merge conflicts.

It is also the heaviest migration: a Go binary embedding a patched Dolt fork, still pre-1.0. State stops being greppable text, so auditing moves from `cat` to `lit show`. Treat it as a phase-3 option. The refresh PR can be retired sooner without it (below).

### Sessions that end themselves cleanly (memento)

The `context-ceiling` Stop hook blocks the stop once a session passes 250k tokens (configurable per user, project or session). It makes the agent commit, write a handoff with `finalize-session`, and reset with the handoff as the next session's first prompt. A `/goal` carries across the reset.

In the pilot, lanes drained to 0–16% context, and you restarted sessions by hand five times in one lane.

**Transfer:** install the plugin as it is. Low risk, and it removes a class of operator interventions.

### Autonomy without prompts (dotfiles)

`config/claude/settings.json` combines `defaultMode: "auto"`, a broad allowlist and a single deny (`tmux kill-server`). Its guards parse shell syntax with a real reader (`bash_command.py`) instead of grepping text.

In the pilot, a permission storm consumed about 40 minutes across all lanes. This repo's text-grep guard also produced false denials: a Python dict literal was refused, and 199 fake "force-push" ledger rows came from test fixtures.

**Transfer:** settle one permission profile before launching lanes, and move the guard's riskiest patterns to a parser.

### Parallel work with one controller (dotfiles)

`hire-a-minion` runs extra sessions in their own worktrees and tmux windows. One controller assigns work and owns merge order. The controller watches token use and `/clear`s a minion past about 300k tokens. There is no merge lease. Branch protection plus the controller's ordering does that job.

## The plan

Estimates are per arc and against the current 177-minute mean. They overlap, so they are not additive past the projection table.

### Phase 1: no governance change, one to three days

1. **Install memento.** Context ceiling plus handoff. Saves operator restarts rather than measured minutes.
2. **Cap PR size.** Split any arc projected above about 300 changed lines at open time. Keep the existing rule that design filings go first as a separate PR. Smaller diffs draw fewer findings and fewer rounds (estimate: 10–30 min on code arcs).
3. **Run review alongside CI instead of after it.** Launch codex and the lenses on push; do not wait for green. Hides most of the ~17 min CI bucket (estimate: 10–15 min).
4. **Make P3 findings non-blocking and batch them.** The rule exists as of #1581. Route P3s to one follow-up ticket per arc instead of a round.
5. **Settle permissions before launch** and freeze `~/.claude/settings.json` during lane runs.

### Phase 2: needs your decision, one to two weeks

6. **Bounded review cycle**, modelled on his steps 9–12:
   - one parallel codex + lens pass;
   - one fix round;
   - one escalation only on an unfixed P1;
   - a final low pass that blocks only on P0/P1.

   Anything else becomes a follow-up ticket. This drops the per-round preflight/sweep re-attestation and the ten-round checkpoint, and keeps authoring-time preflight. Estimate: review ~114 → ~30–35 min.
7. **Retire the per-arc terminating refresh PR.** Either compute `roadmap_status.md` in CI and have the drift guard compare against the computed value, or refresh in one batch per N merges or per day. The door then releases after the content merge's own main CI. Estimate: door ~28 → ~8 min. It also removes the refresh failure class, which blocked the door five times in the pilot.

### Phase 3: optional, larger

8. **Adopt lit** for next-work selection, claims and ledger rows, or build lane-aware selection in-repo first. This fixes parallel-lane collisions more than per-arc time.
9. **Move the review to a CI-side action** like his, capped per push, so it runs without a live session.

### Projected mean after phases 1 and 2 (estimate)

| Phase | Today | Projected |
|---|---|---|
| Build and grounding | 18 | 18 |
| Review | 114 | 30–35 |
| CI wait and merge, overlapped with review | 17 | 3–5 |
| Door dwell, no refresh PR | 28 | 8 |
| Total | 177 | 59–66 |

A PR-size cap and fewer repair arcs push that under 60. Without phase 2's bounded review, the best case is roughly 130 minutes, because review alone is 64% of the time.

**Parallel lanes.** Per-arc time barely changes with lanes today, since lanes did not contend for the door. What lanes add is door hold time and failure blast radius. Retiring the refresh PR halves the door's hold per arc and removes the failure mode that blocked every lane. Pair it with the pilot audit's fix: deny bare `gh pr merge` so every landing uses the door.

## Decisions only you can make

1. **Accept a bounded review cycle.** This reverses three standing rules:
   - `ship-pr` lists round caps as a refused non-goal;
   - C-HE-21 §1 of the loop-lanes spec forbids a flat round cap;
   - B-230 kept all three lenses always.

   The measured cost: 34% of accepted P1/P2 findings in the cohort surfaced at round 6 or later. Some will now ship or be caught later. Changing C-HE-21 is a spec amendment and routes through the design-phase back-flow.
2. **Retire the per-merge terminating refresh.** This rewrites CLAUDE.md §12.2 and §12.2.1 and the drift guard in `tools/codex_context_guard.py`. CLAUDE.md revisions route through back-flow per its §9.1.
3. **Whether to adopt lit.** Accepting it means state you audit through a CLI rather than through plain files.

## What not to copy

- **Bare `gh pr merge` in memento's finalize step.** It works for a single agent. In this repo's parallel lanes it is exactly what reddened main during the pilot. Keep the door, just lighter.
- **The reviewer credential pool** in `code-review-unblock/probe-accounts.sh`. It rotates subscription tokens to dodge usage limits. That is a policy and terms question, not a speed fix.
- **Alternate-provider model profiles** (z.ai, MiniMax) in his settings. These are cost choices with no bearing on wall-clock here.

## Method and limits

Sources:

- this repo's merge-gate log (3,569 rows), reservation store and loop ledger;
- `git log` on origin/main;
- `gh pr list` for this repo, memento and lit;
- full reads of memento and the dotfiles review, settings and minion files;
- a code-level read of lit.

CI durations were not fetched per run. The CI bucket is the gap from last review to merge, so it is an upper bound. Per-round reviewer runtime is not logged, only round-to-round cycle time. Minute projections are estimates built from the measured phase means, not a trial.

The cheapest proof is to run phase 1 plus a trial of the bounded cycle on the next five code arcs, and compare against the 203-minute code-arc median.
