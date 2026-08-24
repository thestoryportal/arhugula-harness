---
name: arc-lever-report
description: Read-only observability over the arc-metrics lever cohorts — whether the two self-improvement skills shipped at PR #1445 (defect-class-preflight, lever B-211; register-pr-prose, lever B-212) are actually improving arcs. Use WHENEVER the operator asks how the new skills are performing, whether arcs are improving, "/arc-lever-report", or the status of a lever/cohort/B-211/B-212. Runs `uv run python tools/arc_lever_report.py` and reports its output; never edits the ledger or the forward register.
---

# arc-lever-report — cohort status, never a verdict

## Why this exists

B-211 and B-212 shipped at PR #1445 on a bet: preflight sweeps and prose discipline
reduce review rounds. The bet is unproven until the cohorts say so. This skill is the
instrument that reads the bet's scoreboard — it does not decide the bet, and it must
never be read as deciding it. A cohort median moving the right direction after one
treated arc is not evidence; it is noise that happens to point the way you hoped.

## Running it

`uv run python tools/arc_lever_report.py` (`just arc-lever-report` once wired).

- `--arc-type inventing|applying` — filter to one arc type. **Use this by default**:
  mixing arc types compares arcs that were never comparable.
- `--levers B-211,B-212` — override the treated-set definition.
- `--json` — machine-readable summary.
- `--ledger PATH` — override the ledger (default `.harness/arc-metrics.jsonl`).

## Data source and lag

Source is the committed `.harness/arc-metrics.jsonl`. A just-closed arc's row lands
only after the NEXT arc's `just arc-metrics drain` folds it in and merges. The report
is therefore always one drain behind the newest arc — **by design, not a defect**: if
the numbers look one arc short, that is the lag, not a bug to chase.

## Reading rules — apply every one, every time you report a number

Do not paste the tool's output and stop. Each rule below governs how you talk about
what it printed; skipping one is how a scoreboard reading turns into a false claim.

1. **A row with null `review_rounds` is an honest could-not-look, not a zero.**
   Exclude it from every median and list it as "excluded (unmapped rounds, B-170)".
   Never let a null collapse into "0 rounds" — that reads as the best possible score
   for an arc you never actually measured, which is the opposite of what happened.

2. **"Per-skill separation: NOT separable" means exactly that — say it, don't paper
   over it.** Every treated arc so far declared both B-211 and B-212 together, so no
   row isolates one skill's effect from the other's. The temptation is to write "B-212
   (prose discipline) drove the improvement" because the prose fixes are the more
   visible ones in the diff — resist it. Until a treated arc exists with only one
   lever declared, attribute improvement to "the treated set", never to a named skill.

3. **Cohort medians are directional, not causal.** Arcs differ in scope, and a single
   treated arc proves nothing about either lever — a good arc could have been good
   anyway. The evaluation bar lives at the B-211/B-212 rows in
   `.harness/forward-register.yaml`: judge only once >=5 treated arcs exist of the
   same `arc_type`, and retire the lever ids if the cohorts turn out indistinguishable
   at that count. Reporting three treated arcs as "trending well" without naming the
   n=5 bar and the current count is an unearned verdict — name both.

4. **`delta_rounds_vs_baseline_median` is per treated arc, not per cohort.** Negative
   means that arc took fewer review rounds than the untreated baseline's median.
   Report deltas as a spread across the treated arcs shown, not averaged into one
   number that hides how many arcs are actually behind it.

## What this skill must never do

- Never edit `.harness/arc-metrics.jsonl`, `.harness/forward-register.yaml`, or any
  register — this is reporting, not remediation.
- Never present the tool's medians/deltas without restating rules 1–4 inline; a bare
  number dump is a claim the reading rules exist specifically to prevent.
- Never say a lever "worked" or "should retire" before the n>=5 bar in rule 3 is met —
  that call belongs to the register's evaluation gate, not to this report.
