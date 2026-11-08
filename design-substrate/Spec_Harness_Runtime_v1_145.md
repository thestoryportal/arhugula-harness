# Spec: Harness Runtime — v1.145 (delta over cleared v1.143)

*Delta-only file. Amendment sites: the C-RT-35 §30 pause-journal record format and pre-bootstrap
refusal battery as amended by v1.137 Rules A1–A3 and §C; the v1.137 §D closed root refusal value
(tenth and eleventh arms); C-RT-29 §14.18.2 exit 5 row (b) and exit 6 kind list as replaced by v1.137
§F; C-RT-29 §14.18.4 failure-mode taxonomy (one new fail class); and the C-RT-35 §14.14.9 pause-state
accessor projection as amended by v1.137 Rule A4. v1.138 through v1.143 amend none of these sites;
v1.141 adopts the v1.137 §D.2 refusal reply for the daemon MCP `resume_workflow`, and this delta's
arms reach it through that adoption. It is numbered after proposed v1.144 (P2, B-315), which amends only
C-RT-18 §14.8 and none of these sites. Every other v1.144, v1.143 and earlier term remains in force.
Cleared predecessor files are not edited.*

**Status: PROPOSED — contract ratified by the integration lead at LIT `arhugula-harness-trial-193`
`cmt-d6410eca-1542-4e49-9ce0-2dbb469c5339` on the frozen fork record
`.harness/class_1_fork_engine_native_resume.md` at `3057fb34b3db7542251ba8ebbad9ee1a859d08d3`, SHA256
`2ac2ba2b4f20714478a605861b57ab88632e5dd6a311a332bb3d52b996060267` (independent APPROVE
`cmt-19fd8de1-b974-4344-89ed-4c27d76369e8`, three T04 passes spent). This file materializes that
contract; its review rides the T05 frozen candidate. Not cleared.**

**Authority:** forward-register row B-314; the fork record above, section 6 "Disposition on
ratification"; T05 claim `cmt-e5e48bf4-b6bc-45f0-9512-9c7fa2ac855d`. The fork's disposition names this
delta v1.144; the integration lead renumbered it v1.145 because P2 holds v1.144 (`cmt-d6410eca`). The
renumbering changes no ratified behavior.

## §0 Change-note (v1.143 → v1.145)

An engine-native pause (WAL segment or reconciler loop) wrote only its engine store record and returned
`PAUSED` with no pause snapshot. The engine record is keyed by a digest of the workflow ID and the
original `run_id`, and nothing durable mapped a workflow ID to its paused run, so no surface could
resume it: v1.137 §F made such a pause a `handle`/`absent` refusal and left B-314 open. This delta
gives each engine pause a journaled address, admits it through the one existing admission unit and
claim, and resumes it under its original `run_id` without re-dispatching completed steps.

## §1 Engine-pause locator record (C-RT-35 §30 journal format, AMENDED)

The workflow-layer pause journal gains a third record kind, beside the snapshot record and the v1.137
supersession record. A locator is an address, not a snapshot. No store is added, and the engine stores
and their run-scoped keys are unchanged.

| Field | Value |
| --- | --- |
| record kind | `engine-pause-locator` |
| `workflow_id` | the plain workflow ID, which is the resume handle |
| `run_id` | the original run ID; the engine key is `run_scoped_substrate_key(workflow_id, run_id)` |
| `engine_class` | exactly `"WAL-segment"` or `"reconciler-loop"`, the `EngineClass.WAL_SEGMENT` and `EngineClass.RECONCILER_LOOP` values as serialized by `harness_cp.engine_class`, without normalization; no other value can be written |
| `step_index` | integer ≥ 0, the pause step; steps `[0, step_index)` completed before capture |
| `depth` | `0` (root only; child engine pauses are not written as locators) |
| `locator_hash` | SHA-256 over the canonical fields above, the claim's `snapshot_hash` analogue |

**Writer.** The two root admission units append one locator after their body returns:
`FreshRunAdmission.run`, which already appends the v1.137 supersession record, and `DurableRootResume`,
whose resumed run may pause again. Each appends through the store's existing `_append` under the
existing cross-process journal lock (v1.137 Rule A2), in the directory that unit already placed. A
locator is appended only when all three hold:

1. the root `RunResult.status` is `PAUSED` and `pause_snapshot is None`;
2. the manifest `engine_class` is `WAL_SEGMENT` or `RECONCILER_LOOP`;
3. `has_pause_record(engine_class, workflow_id, run_id)` is true.

The engine capture is durable before the driver returns, so a present locator implies a captured
engine record. A crash between the two leaves an engine record with no locator; that pause is not
resumable, which fails closed.

**Reader (v1.137 Rule A3, AMENDED).** A `resume_handle=<workflow_id>` request reads the latest journal
record through the existing durable read. The record kind discriminates that one read result: a
snapshot, a locator, `superseded`, or one of the five unchanged failure causes. It is never a second
read. `read_latest` keeps returning `None` for any latest line that is not a snapshot record, and the
staleness token keeps hashing record count and latest digest, so a locator changes it like any other
appended line.

**Precedence.** The journal is one ordered sequence per workflow, and the latest record alone decides:
a snapshot means workflow-layer resume (unchanged), a locator means engine resume, and a supersession
record means `pause-record-superseded`. An earlier record of either form is never resumable, because the
claim refuses a record that is not the latest. One pause yields one form: the driver checks its engine
branch before the workflow-layer branch.

No operator surface exposes the engine store path or the run-scoped digest. Operators name only the
`workflow_id`.

## §2 Admission, run identity and effect boundary (C-RT-35 §30, AMENDED)

1. **One admission unit.** `admit_root_resume` gains a locator variant, used by `api.resume`, the CLI
   and the daemon MCP `resume_workflow`; no surface re-implements a check. The existing order is kept:
   protocol bound and durable, the read, superseded, depth, workflow match, step range, then staleness
   last. The locator variant adds two checks:
   - **engine-class match**, right after the workflow match;
   - **engine presence**, right after the step range: `has_pause_record(engine_class, workflow_id,
     run_id)` must be true, read from the store directories the producer-loop factory binds, through
     the same `resolve_state_path(StateKind.ENGINE_RECOVERY_*)` derivation. It runs before the claim and
     before bootstrap. Presence is not validity: §3 covers a present but corrupt record.

   The admitted entry carries the engine variant `{workflow_id, run_id, engine_class, step_index}` and
   no `PauseSnapshot`; none is synthesized.
2. **At most once.** `DurableRootResume` claims the exact locator record. Its `JournalRecordRef`
   carries `run_id`, `record_count`, `latest_digest` and `snapshot_hash := locator_hash`. The claim
   reuses the existing `ResumeClaimStore`: `started` is fsynced and the lease is held until the body
   returns. No claim, lease, journal or idempotency store is added.
3. **Original run identity.** The body runs under the locator's `run_id`. The driver's existing engine
   gates probe the same run-scoped key, fire `attempt_resume` exactly once, and fail closed on
   `ABORT_*`. No operation ID is created; `resume_context` passes through once and no approval is
   stored.
4. **Prefix-skew guard.** Before the first step dispatch and before the WAL or reconciler
   `attempt_resume` fire, the CP driver compares its F2-derived `resume_at` with the locator's
   `step_index`. On inequality the body returns `RunResult(status=FAILED,
   fail_class="RT-FAIL-RESUME-ENGINE-PREFIX-SKEW")` with zero step dispatches, and the claim stays
   consumed. The completed prefix is therefore never re-dispatched, whether or not the F2 ledger
   survives the resume process.

## §3 Refusals and admitted failures

**Pre-body refusals.** None runs the workflow body: no `attempt_resume` fire, no `cp.resume-attempted`
entry, no model or tool call, no step dispatch and no new run. Admission-stage refusals (exit 6) are
raised in `admit_root_resume` before bootstrap and the claim, and write no journal or claim record.
Claim-stage refusals (exit 7) are raised after bootstrap, inside `DurableRootResume.run` during the claim
attempt and before the body; zero bootstrap effects are not promised, no new claim is taken and the
existing claim or lease stands.

| Case | Representation | Exit |
| --- | --- | ---: |
| No record for the handle | `ResumeHandleUnknownError`, its existing five causes, `kind=handle` | 6 |
| Corrupt locator line | the same, with the existing corrupt cause | 6 |
| Stored locator's `workflow_id` differs from the handle it was read for | the same, with cause `PauseJournalReadCause.WORKFLOW_MISMATCH` | 6 |
| Locator present, engine record absent | **new** `ResumeEnginePauseRecordAbsentError`, `kind=engine-pause-record-absent`; the message names the engine class only | 6 |
| Valid locator whose `workflow_id` differs from the supplied `WorkflowObject` | `ResumeWorkflowMismatchError`, `kind=workflow-mismatch` | 6 |
| Valid locator whose `engine_class` differs from the supplied workflow's manifest | **new** `ResumeEngineClassMismatchError`, `kind=engine-class-mismatch`; the message names both engine classes only | 6 |
| Step out of range | `ResumeStepIndexOutOfRangeError`, `kind=step-index-out-of-range` | 6 |
| Direct child (`depth != 0`, unknown or malformed) | `ResumeDirectChildHandleError`, `kind=depth` | 6 |
| Stale composed `resume_context` | `ResumePauseStateStaleError`, `kind=pause-state-stale` | 6 |
| Superseded by a later fresh run | `ResumePauseRecordSupersededError`, `kind=pause-record-superseded` | 6 |
| Protocol not bound or not durable | the existing `ResumeProtocolNotBoundError` / `ResumeArgsError` | 6 |
| Claim lease held | `ResumeClaimRefusedError`, reason `claim-busy`, `kind=claim` | 7 |
| Record already claimed, any outcome | `ResumeClaimRefusedError`, reason `claim-refused`, `kind=claim` | 7 |

No refusal message or refusal value names an engine store path, a run-scoped digest or a `run_id`.

**Admitted failures.** The claim is taken (`started` fsynced) and stays consumed, so a repeat is
`claim-refused`. Zero step dispatches, zero model or tool calls, no new run.

| Case | Result | `cp.resume-attempted` entries | Exit |
| --- | --- | --- | ---: |
| Prefix skew (`resume_at` ≠ `step_index`) | `FAILED`, `RT-FAIL-RESUME-ENGINE-PREFIX-SKEW` | none: the guard precedes the fire | 1 |
| Engine record present but corrupt | `FAILED`, the CP pause-snapshot-corruption fail class (`CP_FAIL_PAUSE_SNAPSHOT_CORRUPTION`) | exactly one, outcome `abort-snapshot-corrupted` | 1 |
| Revalidation abort | `FAILED`, the CP material-diff fail class (`CP_FAIL_RESUME_MATERIAL_DIFF_DETECTED`) | exactly one, outcome `abort-revalidation-failed` | 1 |

The two CP fail classes are the existing `harness_cp.pause_resume_protocol` constants; their serialized
values are hyphenated (`CP-FAIL-…`), and this delta does not rename them.

## §4 Root refusal value — tenth and eleventh arms (v1.137 §D, AMENDED)

| `kind` | Exact `fail_class` | Additional required fields | Python type | CLI exit |
| --- | --- | --- | --- | --- |
| `engine-pause-record-absent` | `RT-FAIL-RESUME-ENGINE-PAUSE-RECORD-ABSENT` | None | `ResumeEnginePauseRecordAbsentError` | 6 |
| `engine-class-mismatch` | `RT-FAIL-RESUME-ENGINE-CLASS-MISMATCH` | None | `ResumeEngineClassMismatchError` | 6 |

`refusal` is now exactly one of eleven closed objects: the nine of v1.137 §D and these two. Both are
pre-bootstrap validation arms that identify only their kind and fail class. Neither is collapsed into
`handle`, `claim`, `arguments` or `workflow-mismatch`, and none of those is inferred from them. The three
refusal classes (arguments, handle and depth; read refusals; claim) stay distinct. The daemon MCP
`resume_workflow` replies with the same value (v1.141).

## §5 C-RT-29 §14.18.2 exit code mapping (AMENDED)

**Row 5, case (b) — replaced.** The v1.137 §F case (b) text is replaced by: "(b) an engine-native
durable-state pause (`pause_snapshot=None`) captured by a runtime that writes engine-pause locators
(v1.145) is resumable through `harness resume <workflow>`, the daemon MCP `resume_workflow` and
`api.resume`, under its original `run_id`. A pause captured before that has no locator and is refused
as `handle`/`absent`; its engine files stay on disk as operator-owned data. Plain `harness run`
re-invocation is not a resume path and is not documented as one."

**Row 6 — kind list amended.** The trigger list gains `engine-pause-record-absent` and
`engine-class-mismatch`. Rows 0–5 and 7 are otherwise unchanged; `harness resume` arguments and JSON
output are unchanged.

## §6 C-RT-29 §14.18.4 failure-mode taxonomy (NEW row)

| Fail class | Trigger | Exit code |
|---|---|---|
| `RT-FAIL-RESUME-ENGINE-PREFIX-SKEW` | An admitted engine resume whose F2-derived `resume_at` differs from the locator's `step_index` (§2.4); raised before any dispatch or `attempt_resume` | 1 |

## §7 C-RT-35 §14.14.9 pause-state accessor projection (AMENDED)

`read_paused_workflow_state()` projects a latest snapshot record with `pause_layer: "workflow"` (the
existing fields, unchanged) and a latest locator as `{workflow_id, run_id, step_index, depth,
pause_layer: "engine", engine_class}`. The projection never includes a path or digest. Its failure
causes are those of v1.137 Rule A4, unchanged.

## §8 Unchanged and out of scope

Workflow-layer pause and resume, the snapshot path, the root claim and supersession are unchanged.
`harness run` remains a fresh run and never resumes. HTTP stays only the daemon's MCP transport. Child
engine pauses get no locator and stay non-resumable from the root. Pauses captured before this delta
get no retroactive locator. No engine, storage system, claim store or per-surface store is added.

## §9 Conformance evidence (to be bound to the reviewed candidate)

The T05 unit (plan v2.72, U-RT-163) carries the twelve literal acceptance items of the fork record's
section 6 and binds them to tests on the reviewed candidate. Its evidence and recorded divergences are
in that unit and the T05 LIT record.
