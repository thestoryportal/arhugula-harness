# Implementation Plan: Harness Runtime — v2.72 (delta over cleared v2.70)

**Status: PROPOSED — implements proposed Runtime spec v1.145, whose contract the integration lead
ratified at LIT `arhugula-harness-trial-193` `cmt-d6410eca-1542-4e49-9ce0-2dbb469c5339`. Its review rides
the T05 frozen candidate. Not cleared.**
Numbered after proposed v2.71 (P2, U-RT-162, B-315), which it does not amend; U-RT-163 is the next unit
ID unused in this tree. A version and unit-ID collision recheck against v2.71, v1.144 and U-RT-162 is
owed at landing. Fork: `.harness/class_1_fork_engine_native_resume.md`. Authority: forward-register row
B-314 and the T05 claim `cmt-e5e48bf4-b6bc-45f0-9512-9c7fa2ac855d`.

## U-RT-163 — resume engine-native pauses through the existing root admission (B-314, P3 T05)

**Source:**
`harness-runtime/src/harness_runtime/lifecycle/journal_workflow_pause_store.py` (the
`EnginePauseLocator` record kind, its capture and exact read, and the latest-record discriminator);
`harness-runtime/src/harness_runtime/lifecycle/root_resume_admission.py` (the locator writer in
`FreshRunAdmission` and `DurableRootResume`); `harness-runtime/src/harness_runtime/lifecycle/engine_recovery_loop.py`
(the engine store binder shared by the factory and admission, and the presence probe);
`harness-runtime/src/harness_runtime/api.py` (the locator admission variant, its engine-class and
engine-presence checks, and the two new refusal types); `harness-runtime/src/harness_runtime/resume_refusal.py`
(the tenth and eleventh arms); `harness-runtime/src/harness_runtime/lifecycle/mcp_server.py` (the daemon
`resume_workflow` through the same admission); `harness-cp/src/harness_cp/workflow_driver.py` (the
prefix-skew guard); `harness-cp/src/harness_cp/pause_state_projection.py` (the engine-layer projection).

**Acceptance criteria.** These are the twelve literal items of the fork record's section 6. Every
pre-body refusal also checks no `attempt_resume` fire, no new `cp.resume-attempted` entry, zero step
dispatches, zero model or tool calls and no new `run_id`; admission-stage refusals also check no new
journal or claim record. Every admitted failure checks the claim is consumed, zero dispatches, zero
model or tool calls, no new `run_id` and its stated `cp.resume-attempted` count.

1. **WAL resume.** A real WAL pause at step 1 through `api.run`, then `harness resume <wf>` in a new
   process: exit 0 with the original `run_id`; step 0 not re-dispatched; exactly one
   `cp.resume-attempted` entry, `resume-clean`; the locator's serialized `engine_class` is the literal
   `"WAL-segment"` and parses back to `EngineClass.WAL_SEGMENT`.
2. **Reconciler resume.** The same for `RECONCILER_LOOP` (`"reconciler-loop"`), through the daemon MCP
   `resume_workflow`.
3. **Repeat.** Resuming the same handle again exits 7: `claim-busy` during the run, `claim-refused`
   after it.
4. **Superseded.** Pause, `harness run` of the same workflow, then resume: exit 6,
   `pause-record-superseded`.
5. **Engine record removed.** Exit 6, `engine-pause-record-absent`.
6. **Engine record corrupted.** Exit 1, the pause-snapshot-corruption fail class, zero dispatches,
   exactly one `cp.resume-attempted` with `abort-snapshot-corrupted`, claim consumed.
7. **Corrupt locator line.** Exit 6, `handle`, the existing corrupt cause. A stored locator naming
   another workflow: exit 6, `handle`, cause `PauseJournalReadCause.WORKFLOW_MISMATCH`.
8. **Engine class changed.** Exit 6, `engine-class-mismatch`. A supplied workflow whose `workflow_id`
   differs from a valid locator's: exit 6, `workflow-mismatch`.
9. **Child depth.** An injected depth-1 locator: exit 6, `depth`.
10. **F2 prefix lost.** Resume with an empty state ledger: `FAILED`, `RT-FAIL-RESUME-ENGINE-PREFIX-SKEW`,
    zero dispatches, no `attempt_resume` fire, claim consumed. Record whether the production F2 ledger
    survives a process restart.
11. **Coexistence.** A snapshot then a later locator: the engine record wins. The reverse: the snapshot
    wins. The earlier record is not resumable.
12. **Regression.** Existing workflow-layer resume, root claim, supersession and B-313 refusal tests
    pass unchanged.

**Witnesses on the T05 candidate** (`harness-runtime/tests/` unless noted):

| Item | Witness | Limit recorded for review |
| --- | --- | --- |
| 1 | `test_engine_resume_end_to_end.py::test_an_engine_pause_resumes_once_under_its_run_id_without_redispatching_its_prefix` (both engine classes); `test_engine_pause_locator_journal.py::test_locator_round_trips_its_literal_engine_class` | Resume runs through `api.resume` on a fresh bootstrap after shutdown, in the same OS process; the `harness resume` CLI in a separate process is not witnessed. `api.RunResult` carries no `run_id`, so the test reads the CP driver's result. |
| 2, 3 | `test_engine_resume_end_to_end.py::test_the_daemon_resumes_a_reconciler_pause_once_and_refuses_a_repeat_during_and_after` | Item 3 literal: a repeat during the run is `claim-refused`, not `claim-busy`. The unchanged B-104 claim store makes the `started` frame durable before the body runs, so `claim-busy` arises only in the pre-claim lease window (`test_b104_root_resume_facade.py::test_a_live_lease_holder_makes_the_resume_busy_and_runs_nothing`). The test asserts the actual behavior; no claim store change is allowed. |
| 4, 5, 8, 9 | `test_engine_resume_admission.py::test_an_engine_locator_refusal_runs_nothing_and_writes_nothing` (cases superseded, engine record removed, engine class changed, another workflow supplied, child depth, step out of range) | Item 4 arranges the supersession record directly rather than through `harness run`. |
| 6 | `test_engine_resume_end_to_end.py::test_a_corrupt_engine_record_fails_its_one_attempt_and_consumes_the_claim` | |
| 7 | `test_engine_resume_admission.py::test_a_corrupt_locator_line_is_the_existing_corrupt_handle_cause`, `::test_a_locator_naming_another_workflow_is_the_mismatch_handle_cause` | |
| 10 | `test_engine_resume_end_to_end.py::test_a_lost_f2_prefix_fails_closed_before_any_attempt`; `harness-cp/cp_tests/test_workflow_driver.py::test_engine_resume_prefix_skew_fails_closed_before_any_effect` | The production F2 ledger is a JSONL file at the `STATE_LEDGER` binding and survives shutdown and a fresh bootstrap; a separate OS process is not witnessed. |
| 11 | `test_engine_resume_end_to_end.py::test_a_later_engine_locator_outranks_an_earlier_snapshot`, `::test_a_later_snapshot_outranks_an_earlier_engine_locator` | |
| 12 | the existing runtime resume and CP driver suites, unchanged | |

Ruff and pyright are clean on the touched files. PR CI, main landing, post-main CI and installed
acceptance remain owed. This unit closes B-314 only after main landing and successful post-main CI.
