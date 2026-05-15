# Pipeline — Cleared-Unit Queue

*Units the review-ahead lane has cleared for landing. Coding lane pulls from
here in topological-sort order (predecessor units must be landed first). See
`review-pipeline.md` §3 for the clearance definition. Updated 2026-05-15.*

A unit is **cleared** when the reviewer surfaced no blocking §2.7.6 Class 1
fork, OR every such fork was operator-resolved and applied.

## Cleared by pilot review-ahead pass (CP/OD v2.5 re-clearance)

Source: `.harness/adversarial_review_cp_od_v25_reclearance.md` (2026-05-15).
The §4A conformance pass conformed every revised unit byte-exact to its cited
spec; 0 Class 3 / 0 Class 2 / 1 non-blocking Class 1 finding (F1-01, casing
drift — fork-queue item 8). 19 of 21 revised units CLEARED; 2 BLOCKED
(U-CP-43, U-OD-09 — see `pipeline-fork-queue.md`).

**Cleared — landable once predecessors land (topo order per CP/OD plan DAG):**

| Unit | Axis | Notes |
|---|---|---|
| U-CP-01 | CP | conformed v2.4 |
| U-CP-10 | CP | conformed v2.4 |
| U-CP-12 | CP | conformed v2.4 |
| U-CP-19 | CP | conformed v2.4 |
| U-CP-23 | CP | cleared with non-blocking §2.7.6 Class-2 note (fork-queue item 4) |
| U-CP-46 | CP | conforms cleanly; `composition_winner` orphan rides on U-CP-43 |
| U-CP-47 | CP | conformed v2.4 |
| U-CP-48 | CP | conformed v2.4 |
| U-OD-02 | OD | conformed v2.5 |
| U-OD-11 | OD | conformed v2.5 |
| U-OD-12 | OD | conformed v2.5 |
| U-OD-14 | OD | conformed v2.5 |
| U-OD-30 | OD | conformed v2.5 (acc #6 only) |
| U-OD-32 | OD | conformed v2.5 |
| U-OD-33 | OD | conformed v2.5 |

Cleared + already landed pre-pipeline: U-CP-00, U-CP-22, U-OD-04 (see below).

## Landed

12 operational-minimum units (U-IS-01..04, U-AS-01..04, U-CP-15, U-CP-00,
U-CP-22, U-OD-01, U-OD-04) landed pre-pipeline under the §4A inline cadence.

Pipeline-era landings (coding lane, AS-axis bootstrap, existing per-unit
cadence — AS not yet under review-ahead):

| Unit | Date | Commit |
|---|---|---|
| U-AS-05 | 2026-05-15 | `feat(as): land U-AS-05` |
| U-AS-11 | 2026-05-15 | `feat(as): land U-AS-11` |

## Coding-lane bootstrap (AS axis, cold start)

U-AS-07 was the next AS candidate but is BLOCKED — see `pipeline-fork-queue.md`
item 9 (plan-internal `ToolContract.required_secrets` materialization fork).
Next clean AS candidates: U-AS-12 (deps [U-AS-04 ✅]), U-AS-20 (deps TBD),
U-AS-28 (deps [U-AS-04 ✅]).
