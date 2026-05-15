# Pipeline — Cleared-Unit Queue

*Units the review-ahead lane has cleared for landing. Coding lane pulls from
here in topological-sort order. See `review-pipeline.md` §3 for the clearance
definition. Authored 2026-05-15.*

A unit is **cleared** when the reviewer surfaced no blocking §2.7.6 Class 1
fork, OR every such fork was operator-resolved and applied.

## Cleared — ready to land

| Unit | Axis | Cleared by | Date | Notes |
|---|---|---|---|---|
| _(none yet — pilot review-ahead pass in progress)_ | | | | |

## Landed (cleared → consumed)

The 12 operational-minimum units (U-IS-01..04, U-AS-01..04, U-CP-15, U-CP-00,
U-CP-22, U-OD-01, U-OD-04) landed pre-pipeline under the §4A inline cadence.
See `phase-7-progress.md` for the landed ledger.

## Coding-lane bootstrap (cold start, per `review-pipeline.md` §5)

While the pilot review-ahead pass runs on CP/OD v2.5, the coding lane
bootstraps on the **AS axis** (not in pilot scope) using the existing per-unit
cadence — read unit body + cited spec directly. Bootstrap candidates with
satisfied dependencies:

| Unit | Depends on | Status |
|---|---|---|
| U-AS-05 | [U-AS-01 ✅] | landable |
| U-AS-07 | [U-AS-01 ✅] | landable |
