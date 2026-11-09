# Fork record — Runtime resume: engine-native pauses (B-314 remainder, T04)

**Status:** RATIFIED 2026-11-08 by the integration lead at LIT `arhugula-harness-trial-193`
`cmt-d6410eca-1542-4e49-9ce0-2dbb469c5339` on this record at `3057fb34b3db7542251ba8ebbad9ee1a859d08d3`
(independent APPROVE `cmt-19fd8de1-b974-4344-89ed-4c27d76369e8`). Applied by T05 (claim `cmt-e5e48bf4`)
as proposed Runtime spec v1.145 and plan v2.72 (U-RT-163): the integration lead renumbered the v1.144 of
section 6 because P2 holds v1.144 and v2.71. Cleared for source consumption by final P3/T05 package ratification cmt-ffe4f953; main landing and installed acceptance remain owed. T04 of the released T01–T20 plan, package P3,
record LIT `arhugula-harness-trial-193` (dispatch `cmt-0c7d0f52`, claim `cmt-7a9b55b1`). Only this
status paragraph changed after ratification. AMENDED by ruling `cmt-4b7f5252-ddff-4f56-9af9-12781e563253` on T05 review `cmt-54c6b7d2`,
the controlling reading of the unchanged-shape and shared-store constraints: section 6 item 1's
`RunResult.run_id` assertion reads as "the resumed execution uses the engine locator's original
`run_id` and creates no new `run_id`; the public `RunResult` and CLI JSON shapes stay unchanged",
and item 3 reads as "`claim-busy` while the exact record is unclaimed and another live attempt holds
its canonical lease; `claim-refused` once its claim exists, during the body and after every outcome".
Section 6 below keeps its reviewed T04 text.

**Class:** 1 (design-substrate amendment), absorbed through one documented back-flow source arc in the
P3 content package (CLAUDE.md §11.4), like `.harness/class_1_fork_runtime_resume_cli_supersession.md`.
No new engine, storage system, H_T primitive, cross-axis edge, per-surface claim store or HTTP surface.

Grounding is at baseline `origin/main` `391823f938daa1cef2ea07219f28e00b64641aa7`. `file:line` refers
to that tree.

## 1. Fork

- **What the contract requires.** B-314: an operator can resume a paused engine-native workflow
  through the supported resume ingress (CLI `harness resume`, daemon MCP `resume_workflow`,
  `api.resume`), with the register's six binding constraints (§7).
- **Why current source cannot meet it.**
  - An engine-native pause writes only its engine store record and a `cp.pause-captured` ledger
    entry, then returns `RunResult(status=PAUSED, pause_snapshot=None)`
    (`harness-cp/src/harness_cp/workflow_driver.py` WAL branch 5507–5545, reconciler branch
    5547–5580). It is checked before the workflow-layer branch, so one pause produces one form.
  - The engine record lives at `run_scoped_substrate_key(workflow_id, run_id)`, a SHA-256 digest
    (`harness-runtime/src/harness_runtime/lifecycle/engine_recovery_loop.py:31`). Locating it requires
    the original `run_id`. Public resume accepts only `resume_handle=<workflow_id>` and reads only the
    workflow-layer pause journal (`harness-runtime/src/harness_runtime/api.py` `admit_root_resume`
    ≈1300–1415, `resume` 1417). The digest cannot be inverted, and nothing durable maps a workflow ID
    to its paused run.
  - The driver resumes an engine pause only when it runs again under the same `run_id`. It probes
    `has_pause_record` (presence, not validity; `engine_recovery_loop.py:154`) and fires
    `attempt_resume` (`engine_recovery_loop.py:188`), failing closed on `ABORT_*`
    (`workflow_driver.py:336-339`; reconciler linear gate 5035–5110, WAL gate ≈5136–5230, reconciler
    fan-out helper 2633–2680). Public `api.run`
    always mints a new `run_id`, so `harness run` starts a fresh run (`docs/how-to-operate-runtime.md:155`).
- **What the existing seams provide.**
  - The per-engine-class store routing (`bootstrap/factories/r_cxa_2_producer_loop_factory.py:329-360`).
  - The run-scoped key.
  - The append-only workflow-layer pause journal, its cross-process append lock and the
    supersession record kind (spec v1.137).
  - The one admission unit `admit_root_resume`, shared by `api.resume` and the daemon.
  - The B-104 `DurableRootResume` claim over an exact `JournalRecordRef`, with reasons in
    `lifecycle/root_resume_admission.py:80-83`.
  - The closed B-313 refusal value and exits 6 and 7 (`docs/how-to-operate-runtime.md:156-157`).

## 2. Identification: the engine-pause locator record (contract item 1)

A third record kind in the **existing** workflow-layer pause journal, beside the snapshot record and
the v1.137 supersession record. It is an address, not a snapshot. It adds no new store, and the engine
stores and keys are unchanged.

```
EnginePauseLocator (journal record kind "engine-pause-locator")
  workflow_id:  str          # plain workflow id (the handle)
  run_id:       str          # ORIGINAL run id; the engine key is run_scoped_substrate_key(workflow_id, run_id)
  engine_class: "WAL-segment" | "reconciler-loop"   # EngineClass.WAL_SEGMENT / .RECONCILER_LOOP values,
                                                    # serialized exactly as harness-cp engine_class.py:46,50
                                                    # define them; no normalization; no other value writable
  step_index:   int >= 0     # the pause step; steps [0, step_index) completed before capture
  depth:        0            # root only; see §4
  locator_hash: sha256 over the canonical fields above (the claim's snapshot_hash analogue)
```

- **Writer (T05).** The two root admission units append one locator after their body returns:
  `FreshRunAdmission.run`, which already appends the supersession record
  (`lifecycle/root_resume_admission.py:227-262`), and `DurableRootResume` (`:149`), whose resumed run
  may pause again. Each uses the existing `JournalWorkflowPauseStore` append under the existing lock,
  in the directory that unit already placed. It is appended only when all of these hold:
  1. the root `RunResult.status` is `PAUSED` and `pause_snapshot is None`;
  2. the manifest `engine_class` is `WAL_SEGMENT` or `RECONCILER_LOOP`;
  3. `engine_recovery_loop.has_pause_record(engine_class, workflow_id, run_id)` is `True`.

  The engine capture is durable before the driver returns. So "locator present" implies "engine
  record was captured". A crash between the two leaves an engine record with no locator. That pause
  is not resumable, which is a fail-closed outcome.
- **Reader.** A `resume_handle=<workflow_id>` request reads the latest journal record for the workflow
  through the existing durable read (`_read_durable_pause_snapshot` path). The record kind is a
  discriminator on that one read result. It is never a second read or a second derivation.
- **Never exposed.** The engine store path and the run-scoped digest are never exposed to an operator.
  Operators name only the `workflow_id` (constraint 3).

## 3. Admission, run identity and effect boundary (contract item 2)

1. **One admission unit.** `admit_root_resume` gains a variant for the locator kind. CLI, MCP and API
   all use it, and none re-implements a check.
   - The existing order and checks are kept: the protocol is bound and durable; the read; the
     superseded check; the depth check; the workflow match; the step range; then staleness, last.
     The locator variant adds the engine-class match (`ResumeEngineClassMismatchError`) right after
     the workflow match.
   - One check is added after the step range: **engine presence**.
     `has_pause_record(engine_class, workflow_id, run_id)` must be `True`, read from the same store
     directories the factory binds through the same `resolve_state_path(StateKind.ENGINE_RECOVERY_*)`
     derivation. This is checked before the claim and before bootstrap.
   - The result is `ResumedEntry` carrying an engine variant `{workflow_id, run_id, engine_class,
     step_index}`. It carries no `PauseSnapshot`, and none is synthesized.
2. **At most once.** `DurableRootResume` claims the exact locator record. `JournalRecordRef` gets
   `run_id`, `record_count`, `latest_digest` and `snapshot_hash := locator_hash`. The claim reuses the
   existing `ResumeClaimStore`: `started` is fsynced, and the lease is held until the body returns.
   No other claim, lease, journal or idempotency store is added (constraint 1).
3. **Original run identity.** The body runs under the locator's `run_id` (constraint 2). The driver's
   existing engine gates then probe the same run-scoped key, fire `attempt_resume` exactly once, and
   fail closed on `ABORT_*`. No operation ID is created. `resume_context` passes through once, and
   no approval is stored (constraint 5).
4. **Effect boundary (prefix-skew guard).**
   - Steps `[0, step_index)` are the completed-effect prefix and must not re-dispatch.
   - Before the first step dispatch, and before the WAL/reconciler `attempt_resume` fire, the driver
     compares its F2-derived `resume_at` with the locator's `step_index`. They must be equal.
   - On inequality, the body returns
     `RunResult(status=FAILED, fail_class="RT-FAIL-RESUME-ENGINE-PREFIX-SKEW")` with zero step
     dispatches. The claim stays consumed, so manual recovery is the audited route.
   - This guard makes the boundary independent of whether the F2 ledger survives the resume
     process. Its durability is a verification item for T05, not an assumption (§6).
5. **Authority and precedence when forms coexist.**
   - The journal is one ordered sequence per workflow. The **latest** record alone decides:
     - a snapshot means workflow-layer resume (unchanged);
     - a locator means engine resume;
     - a supersession means `pause-record-superseded`.
   - An earlier record of either form is never resumable: the claim already refuses a record that
     is not the latest.
   - One pause yields one form, because the driver checks the engine branch first.
   - Root authority is the depth-0 record only. Child engine pauses are not written as locators (§4).

## 4. Refusal and outcome table (contract item 3)

**4a. Pre-body refusals.** None runs the workflow body: no `attempt_resume` fire, no
`cp.resume-attempted` entry, zero model calls, tool calls or step dispatches, and no fresh run. Their
timing differs by stage:

- **Admission stage (exit 6 rows).** Raised in `admit_root_resume` before bootstrap and before the
  claim. They write no journal or claim record and have no bootstrap effects.
- **Claim stage (exit 7 rows).** Raised after bootstrap, inside `DurableRootResume.run` in the
  bootstrapped worker, during the claim attempt and before the body (`lifecycle/mcp_server.py:545-550`;
  `lifecycle/root_resume_admission.py:167-189`, which creates `ResumeClaimStore` and calls
  `run_started`). Bootstrap has happened, so zero bootstrap effects are not claimed. No new claim is
  taken, and the existing claim or lease stands.

| Case | Representation (exact) | Exit |
| --- | --- | ---: |
| No record for the handle | `ResumeHandleUnknownError`, existing five causes, `kind=handle` | 6 |
| Corrupt locator line | same, the existing corrupt cause (fail-closed read returns `None`) | 6 |
| Stored locator's `workflow_id` differs from the handle it was read for | same, the existing reader cause `PauseJournalReadCause.WORKFLOW_MISMATCH` (`journal_workflow_pause_store.py:986-997`, surfaced by `api.py:1334-1354`); the five-cause reader contract is unchanged | 6 |
| Locator present, engine record absent | **new** `ResumeEnginePauseRecordAbsentError`, `kind=engine-pause-record-absent`, message names the engine class only (no path, digest or run) | 6 |
| Valid locator whose `workflow_id` differs from the supplied `WorkflowObject` | `ResumeWorkflowMismatchError`, `kind=workflow-mismatch` | 6 |
| Valid locator whose `engine_class` differs from the supplied workflow's manifest engine class | **new** `ResumeEngineClassMismatchError`, `kind=engine-class-mismatch`, message names both engine classes only | 6 |
| Step out of range (the workflow changed) | `ResumeStepIndexOutOfRangeError`, `kind=step-index-out-of-range` | 6 |
| Direct child (`depth != 0`, unknown or malformed) | `ResumeDirectChildHandleError`, `kind=depth` | 6 |
| Stale composed `resume_context` | `ResumePauseStateStaleError`, `kind=pause-state-stale` | 6 |
| Superseded (a later fresh run was admitted) | `ResumePauseRecordSupersededError`, `kind=pause-record-superseded` | 6 |
| Busy (claim lease held) | `ResumeClaimRefusedError` reason `claim-busy`, `kind=claim` | 7 |
| Already used (claimed earlier, any outcome) | `ResumeClaimRefusedError` reason `claim-refused`, `kind=claim` | 7 |
| Protocol not bound / not durable | existing `ResumeProtocolNotBoundError` / `ResumeArgsError` | 6 |

**4b. Admitted failed outcomes.** The claim is made (`started` fsynced) and stays consumed, so a
repeat is `claim-refused`. Zero step dispatches and zero model or tool calls. No fresh run.

| Case | Representation (exact) | `attempt_resume` / `cp.resume-attempted` | Exit |
| --- | --- | --- | ---: |
| Prefix skew (F2 `resume_at` != locator `step_index`) | `FAILED`, `fail_class=RT-FAIL-RESUME-ENGINE-PREFIX-SKEW` | none (checked before the fire) | 1 |
| Engine record present but corrupt (presence is not validity) | `FAILED`, `fail_class=CP_FAIL_PAUSE_SNAPSHOT_CORRUPTION` | exactly one, outcome `abort-snapshot-corrupted` | 1 |
| Revalidation abort | `FAILED`, `fail_class=CP_FAIL_RESUME_MATERIAL_DIFF_DETECTED` | exactly one, outcome `abort-revalidation-failed` | 1 |

- The B-313 closed refusal value gains exactly two arms, `engine-pause-record-absent` (tenth) and
  `engine-class-mismatch` (eleventh). The
  three refusal classes (arguments/handle/depth vs read refusals vs claim) stay distinct
  (constraint 4).
- `harness run` remains a fresh run and never resumes.

## 5. Surfaces (contract item 4)

- **Result.** The `RunResult` shape is unchanged. An engine-resumed run returns `SUCCESS`, `FAILED`
  or `PAUSED` under the **original** `run_id`. A new engine pause appends a new locator, which is a
  new, separately claimable record.
- **CLI.**
  - `harness resume` is unchanged in arguments and JSON output, with exits 0–7.
  - The exit 5 row (b) is replaced: an engine-native pause captured after T05 is resumable through
    `harness resume <workflow>`.
  - Pauses captured before T05 have no locator. They stay non-resumable, and their engine files stay
    on disk as operator-owned data.
  - The exit 6 kind list gains `engine-pause-record-absent` and `engine-class-mismatch`.
- **MCP.** `resume_workflow` gets the same admission and the same closed refusal value. HTTP stays only
  the daemon's MCP transport (constraint 6).
- **Inspection.** The §14.14.9 pause-state accessor projects a locator as
  `{workflow_id, run_id, step_index, depth, pause_layer: "engine", engine_class}`, and a snapshot record
  as `pause_layer: "workflow"`. It never includes a path or digest. Its failure causes are unchanged
  apart from those from §4.
- **Unchanged behavior.** Workflow-layer pause/resume, the snapshot path, the root claim and
  supersession are unchanged.

## 6. Disposition and T05 acceptance (contract item 5)

**Disposition on ratification.** In the one P3 content PR:

- Runtime spec **v1.144**, numbered after main's v1.143:
  - the locator record kind and its writer condition;
  - the engine admission variant and the presence check;
  - the prefix-skew fail class;
  - the tenth and eleventh closed-value arms;
  - the exit 5 row (b), exit 6 list and §14.14.9 projection text.
- The next plan version adds one U-RT unit, T05.
- One clearance file for each of the two.
- The register row B-314 moves to applied.

None of this is applied by T04.

**T05 acceptance (literal).** Every §4a refusal assertion also checks: no `attempt_resume` fire, no new
`cp.resume-attempted` entry, zero step dispatches, zero model or tool calls and no new `run_id`.
Admission-stage (exit 6) assertions also check no new journal or claim records. Claim-stage (exit 7)
assertions also check that no new claim is taken and the body never starts. Every §4b admitted failure checks the claim is consumed,
zero step dispatches, zero model or tool calls, no new `run_id`, and exactly the
`cp.resume-attempted` count its §4b row states.

1. **WAL resume.** A real WAL pause at step 1 through `api.run`, then
   `harness resume <wf>` in a new process:
   - the run exits 0, and its `RunResult.run_id` is the original;
   - step 0 is not re-dispatched;
   - exactly one `cp.resume-attempted` entry is written, with `resume-clean`;
   - the journaled locator round-trips: its serialized `engine_class` is the literal `"WAL-segment"`
     and parses back to `EngineClass.WAL_SEGMENT` (likewise `"reconciler-loop"` in 2).
2. **Reconciler resume.** The same as 1 for `RECONCILER_LOOP`, through the daemon MCP `resume_workflow`.
3. **Repeat.** Resuming the same handle again returns exit 7 with `reason=claim-busy` during the run
   and `reason=claim-refused` after it.
4. **Superseded.** A pause, then `harness run` of the same workflow (a fresh run), then resume:
   exit 6, `kind=pause-record-superseded`.
5. **Engine record removed.** Locator kept, engine record deleted: exit 6,
   `kind=engine-pause-record-absent`.
6. **Engine record corrupted.** Exit 1, `fail_class=CP_FAIL_PAUSE_SNAPSHOT_CORRUPTION`, zero
   dispatches, exactly one `cp.resume-attempted` with `abort-snapshot-corrupted`, claim consumed.
7. **Corrupt locator line.** Exit 6, `kind=handle`, the existing corrupt cause. A stored locator
   whose `workflow_id` differs from its handle: exit 6, `kind=handle`,
   `cause=PauseJournalReadCause.WORKFLOW_MISMATCH`.
8. **Engine class changed.** The workflow file's engine class was changed: exit 6,
   `kind=engine-class-mismatch`. A supplied `WorkflowObject` with a different `workflow_id` than a
   valid locator: exit 6, `kind=workflow-mismatch`.
9. **Child depth.** A locator with depth 1 is injected: exit 6, `kind=depth`.
10. **F2 prefix lost.** Simulated by resuming with an empty state ledger: `FAILED`
    `RT-FAIL-RESUME-ENGINE-PREFIX-SKEW`, zero dispatches, no `attempt_resume` fire, claim consumed. T05 also records whether the production F2
    ledger survives a process restart.
11. **Coexistence.** A workflow-layer snapshot followed by a later engine locator: the engine record
    wins. The reverse order: the snapshot wins. The earlier record is not resumable.
12. **Regression.** Existing workflow-layer resume, root claim, supersession and B-313 refusal tests
    pass unchanged.

## 7. Register constraints honored (B-314)

1. **Admission.** Admission goes only through `admit_root_resume` and `DurableRootResume`. No new
   store is added.
2. **Run identity.** The request accepts a `workflow_id`, keeps the original `run_id` and creates no
   operation IDs.
3. **No paths exposed.** No operator surface exposes a path or a caller-supplied snapshot.
4. **Distinct refusals.** The three refusal classes stay distinct, each under its own fail class.
5. **Resume context.** `resume_context` passes through once, and no approvals are stored.
6. **HTTP.** HTTP stays only the daemon's MCP transport.

## Open

- **P2 crossover.** T05 edits `api.py` admission and the daemon `resume_workflow`. Any P2 change to
  those files is reconciled at the Git gate. Both owners stay active.
- **F2 durability.** Whether the production F2 ledger survives a process restart is unverified at
  this baseline. §3.4 makes safety independent of the answer.
