# Fork extension — U-RT-49 workflow-execution ACs extend [[fork-u-rt-44-workflow-loop-drain]]

**Class:** 1 (extension of existing OPEN fork)
**Status:** **MOSTLY CLOSED at Lane 6 (2026-05-20).** Ledger-entry + lifecycle-span ACs un-struck via Lane 6 runtime un-strike. Cost-attribution AC carries forward on `[[fork-u-od-21-span-cost-record-missing-rollup-keys]]` (U-OD-21 HALTED Class 1).
**Filed:** 2026-05-20 at U-RT-49 partial-landing
**Carrier:** `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md`

## Extension

The U-RT-44 fork records: "in-flight step drain unmaterializable until CP
workflow loop primitive lands." That same primitive blocks U-RT-49's
workflow-execution ACs:

- State ledger has workflow entries — STRUCK
- Collector sqlite has spans per stage + workflow step — STRUCK
- Cost attribution chain produced an entry — STRUCK

The fork now blocks **two units** until the loop primitive lands:
- U-RT-44 AC #2 (in-flight step bounded-wait)
- U-RT-49 workflow-execution ACs (3 of 5 above)

Operator-ratified routing path (2026-05-20): **Path A — defer to follow-up
phase.** No new unit added at this phase. The fork carries forward to
whatever follow-up phase introduces a CP workflow loop primitive (Track B
runtime or a new Track A revision-pass unit).

## What U-RT-49 lands

| AC | LAND/STRIKE | Land event |
|---|---|---|
| Touches all 9 `BootstrapStage` members | LAND | U-RT-49 initial land |
| Clean shutdown leaves no resources open | LAND | U-RT-49 initial land |
| Workflow ledger entries | **LAND** | Lane 6 (2026-05-20) — driver writes to `ctx.ledger_writer` per C-CP-25 §25.3.3 |
| Workflow spans | **LAND** | Lane 6 (2026-05-20) — lifecycle emitter records driver §25.5 events |
| Cost-attribution entries | STRIKE | Carries on `[[fork-u-od-21-span-cost-record-missing-rollup-keys]]` (U-OD-21 HALTED) |

## Re-land plan

When the CP workflow loop primitive lands:

1. Extend the existing U-RT-49 test (`tests/integration/test_run_smoke.py`)
   to actually invoke a `WorkflowObject` step.
2. Assert workflow ledger entries appear in `audit_writer.read_all()`.
3. Assert collector ring buffer / sqlite has ≥1 span for the workflow step.
4. Assert cost-attribution chain produces a `SpanCostRecord` (requires
   landed rate table, currently `U-OD-21` deferred — sub-fork).

## Provenance

- Operator decision: 2026-05-20 in-session AskUserQuestion ("(A) Partial-land
  + carry forward to follow-up phase").
- Spec source: `Spec_Harness_Runtime_v1.md` §10 + §11.
- Decomposition source: `.harness/phase-2-session-3-track-a-atomic-decomposition.md` L11 U-RT-49.
- Predecessor units: U-RT-43 (bootstrap, commit bf8d838); U-RT-46 (shutdown, commit 10a6bca).
