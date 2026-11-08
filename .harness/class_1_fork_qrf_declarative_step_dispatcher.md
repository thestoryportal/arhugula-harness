# Class 1 fork — `DECLARATIVE_STEP` dispatcher (bundled design back-flow + implementation)

**Status: CONTRACT CLEARED 2026-11-08** (Runtime v1.143; ratified at LIT `arhugula-harness-trial-193.qrf`
`cmt-eaec8ba7-4450-4cd0-afb8-c80f1592921e`; marker
`.harness/clearance/spec-harness-runtime-v1-143-cleared-2026-11-08.md`). PR CI, landing, post-main CI and
installed acceptance remain owed.

## Defect

The installed runtime bound no dispatcher for `DECLARATIVE_STEP`. Any workflow declaring one failed closed
with `RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND` at its first such step, so a declarative orchestrator could
never hand a `worker_plan` to the CP `LEAD_PLAN` selection (CP v1.130 §25.11.1.1) through `harness run`.

## Disposition

Integration-lead option A (LIT `cmt-de679744-ad1b-4a04-8664-67f4d7a536db`, admitted at
`cmt-25152ce4-0505-4d90-8d46-20fd123f8e37`): bind the smallest effect-free dispatcher. Stage 5 binds
`DeclarativeStepDispatcher` beside `TOOL_STEP`; the payload is exactly `{output: <object>}` and dispatch
returns it. Contract delta: `design-substrate/Spec_Harness_Runtime_v1_143.md`.

Independent pass 1 (`cmt-0a4f0226`, on `e0b518b9`) held three findings, all corrected at `72e1f5b5`:

- **F1.** The payload rejects `nan`, `inf` and `-inf` at any depth, so the declared output stays JSON.
- **F2.** The delta replaces the whole C-RT-18 `DECLARATIVE_STEP` row, retiring "body-of-prose evaluation".
- **F3.** The lead-plan test binds each audited effective brief to its fan-out ordinal.

The correction and the delta were approved with zero findings at `cmt-a51a00d7-f76e-443a-b22e-70719db3ba22`.
The native receipt is the `.harness/merge-gate-log.jsonl` row committed at `e4a302f8`.
