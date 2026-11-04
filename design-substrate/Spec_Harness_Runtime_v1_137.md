# Spec: Harness Runtime — v1.137 (PROPOSED delta over cleared v1.134)

*Delta-only file. Amendment sites: C-RT-29 §14.18.1 subcommand table (new `resume` row); C-RT-29
§14.18.2 exit code mapping (row 5(b) at `Spec_Harness_Runtime_v1_132.md:1431` replaced; rows 6 and 7
added); C-RT-29 §14.18.4 failure-mode taxonomy (one new fail class); C-RT-35 §30 `resume()` contract
(`Spec_Harness_Runtime_v1_132.md:3669`): the pause-journal record format, the fresh-run supersession
write, and the pre-bootstrap refusal battery; C-RT-35 §14.14.9.4 pause-state accessor failure cause
(Rule A4). Rule A4 also states a companion OD C-OD-30.5.1 amendment that this file does not author.
Neither proposed v1.135 (A5) nor proposed v1.136 (A4) amends any of these sites. Every other v1.134 and
earlier term remains in force. Cleared predecessor files are not edited.*

**Status: PROPOSED — not cleared.** No clearance marker, artifact-head row or pointer is filed.
Corrected after the first independent review of the combined candidate (HOLD, LIT `cmt-bcef30fd`):
F1 in Rules B2, B3, B5, B6 and C2 and witnesses I.2 and I.14; F2 in Rules A3 and A4 and witness I.13.

**Lineage (pending fold):** grounded on cleared v1.134 at H `14b785d84e4d80f15c4e8c0ac1dbf7a69e1afed9`.
Fold order A3 → A5 (v1.135) → A4 (v1.136) → this delta. It combines three decided inputs into one
contract: the B-310 v4 CLI resume request (definition accepted, LIT `cmt-fe2c7b08`), the B-313 v2
closed root-refusal value with one added arm, and the broadened B-314 superseded-record
prerequisite. Authority: `.harness/runtime-resume-contract-authority.md`. Fork:
`.harness/class_1_fork_runtime_resume_cli_supersession.md`.

Citations below use `P` = `harness-runtime/src/harness_runtime` at the grounding revision. They state
current behavior; the normative text is the bold-labelled rules.

---

## A. C-RT-35 §30 — pause-journal record kinds (AMENDED)

Today every journal line is `{"workflow_id", "pause_snapshot", "depth"}` written with `sort_keys`
(`P/lifecycle/journal_workflow_pause_store.py:849-854`). This delta adds a second line kind.

**Rule A1 — two record kinds, one file.** A line of the per-(tenant, workflow_id) journal is exactly
one of:

| Kind | Discriminator | Fields |
| --- | --- | --- |
| Snapshot record | no `kind` key | unchanged: `workflow_id`, `pause_snapshot`, `depth` |
| Supersession record | `"kind": "supersession"` | exactly `kind`, `workflow_id`, `run_id` (the superseding run's `run_id`) |

A line without `kind` remains a snapshot record, so existing journals need no migration. Any other
`kind` value, or a supersession line with missing or extra fields, is an undecodable line and keeps the
existing `corrupt-latest` treatment.

**Rule A2 — one writer path.** Supersession records are appended only through the store's existing
`_append` (`:763`): under `cross_process_journal_lock` (`:470`, `flock LOCK_EX` `:556`), with the same
file and directory fsyncs. No surface (CLI, MCP, HTTP) writes, reads or locks the journal.

**Rule A3 — reader semantics.**

- `read_latest_attributed` (`:615`) returns `superseded` when the latest line is a well-formed
  supersession record whose `workflow_id` equals the handle. Its result is one of three outcomes: a
  snapshot, `superseded`, or one of the five failure causes (`absent`, `empty-journal`, `read-error`,
  `corrupt-latest`, `workflow-mismatch`). `superseded` is never a `ResumeHandleUnknownError` cause: that
  refusal's cause stays closed at five (B-313 v2), and a handle refusal carrying `superseded` must not
  be constructible.
- `read_latest` keeps returning `None` for any latest line that is not a snapshot record (fail-closed).
- `read_exact` returns `None` for a supersession position, so durable child admission refuses with its
  existing `UNREADABLE_RECORD` (`P/lifecycle/durable_child_admission.py:79-83`).
- The staleness token (`P/lifecycle/pause_state_staleness.py:55-59`) is unchanged: it hashes record
  count and latest digest, so any appended line, of either kind, changes it.

**Rule A4 — pause-state accessor (C-RT-35 §14.14.9.4, AMENDED).** `read_paused_workflow_state()` reads
through the same `_read_durable_pause_snapshot` as `resume()` (`P/api.py:1104-1108`) and handles
`superseded` explicitly; it never passes `superseded` to a five-value type. On `superseded` it returns
no projection and no staleness token. It emits exactly one `pause.state.read` event through the
existing failed-read path (`_emit_pause_state_read`, `P/api.py:1120-1128`) with `succeeded=false`, no
token, null per-variant counts and `cause_attribution` `superseded`. It then raises
`PausedWorkflowStateUnavailableError` with cause `superseded`, `retryable=False` and
`indeterminate=False`. The state is permanent: nothing makes a superseded record readable again.

The accessor's failure vocabulary is therefore six identifiers: the five §30 causes plus `superseded`.
The Runtime accessor cause and OD's `PauseStateCauseAttribution`
(`harness_od/pause_resume_namespace.py:482-498`) stay identical, so the existing cross-surface identity
witness covers the sixth value. Today `PauseStateCauseAttribution(cause.value)` (`P/api.py:1234`)
would raise `ValueError` for a sixth value; this rule replaces that failure with the typed result and
the audit event above.

**Companion OD amendment (required before implementation ratification; not authored here).** OD
C-OD-30.5.1, cause-attribution row (`Spec_Operational_Discipline_v1_36.md:62`, unchanged through head
v1.42): "one of the five stable identifiers Runtime v1.107 §30 declares" becomes "one of six
identifiers: the five Runtime v1.107 §30 declares, plus `superseded` (Runtime v1.137 Rule A4)", and
`PauseStateCauseAttribution` gains `SUPERSEDED = "superseded"`. Nothing else in §30.5 changes. A failed
read still carries no token, so the §30.5.3 pairing rule is unaffected. The OD spec delta and its OD
plan unit are outside this candidate's owned paths and need a named owner.

## B. C-RT-35 §30 — fresh-run supersession write (NEW)

**Rule B1 — single enforcer.** Every fresh (non-resume) root run enters the MCP tool `run_workflow`
(`P/mcp_server.py:296`), from `api.run` (`P/api.py:668` → `:779` → `call_tool("run_workflow")` `:596`)
and from daemon clients (`P/cli/app.py:229-231`). That tool runs the body through
`_admission.run(harness_ctx, _execute)` (`P/mcp_server.py:494-497`); a fresh run uses the default
`UNCLAIMED` admission (`:381`; `P/lifecycle/root_resume_admission.py:185-187`). The Runtime-owned
fresh-run admission replacing `UNCLAIMED` is the one place that writes a supersession record. It
appends the record, then calls `body(None)`. It runs before the run's first step or any model, tool or
body effect.

**Rule B2 — what is written, and when.** The fresh-run admission appends one supersession record for
(tenant, workflow_id) to every journal file for that key that already exists and is non-empty, in
every directory Rule B3 names, each under that file's journal lock. Where no such file exists there is
nothing to supersede and nothing is written. The `run_id` field is the fresh run's own `run_id`.

**Rule B3 — journal locations: every STATE_LEDGER cell of the run's binding.** The STATE_LEDGER
directory, and with it the journal directory, depends on `(workload_class, deployment_surface)`
(`P/api.py:849-853`), and a manifest can keep its `workflow_id` while changing its `workload_class`. A
later run of W can therefore bind a different journal directory from the one holding W's earlier
record, so the admission does not write only to its own run's directory. It takes every
`PathBindingEntry` whose `path_class` is `STATE_LEDGER` in the run's path binding (built from
`config.path_bindings`; the binding is the resolver's only path source,
`harness_is/path_binding.py:49-54`, and an unbound triple has no default,
`harness_is/path_resolver.py:62-68`). For each entry it resolves
`PathResolver.resolve_path(STATE_LEDGER, entry.workflow_class, entry.deployment_surface)`, applies
`pause_journal_dir_for` and `os.path.realpath` as the read does (`P/api.py:849-857`), and removes
duplicates. The set always contains the run's own capture directory
(`pause_journal_dir_for(ctx.ledger_writer.handle.canonical_path.parent)`,
`P/lifecycle/root_resume_admission.py:158`; `ctx.ledger_writer` exists after bootstrap stage 1,
`P/bootstrap/stage_1_is.py:103-108`) and the daemon's fixed `SOFTWARE_ENGINEERING` cell
(`P/cli/app.py:619`) when bound. Directories are visited in sorted path order. Each append uses the
placement verification `DurableRootResume` applies before its claim
(`P/lifecycle/root_resume_admission.py:148-155`). Any failed verification or append fails the fresh run
before its first step; no path continues after a partial write. The write does not depend on the
durable pause opt-in: a later run whose config lacks `pause_resume_protocol_config` or the durable
opt-in still supersedes.

**Rule B4 — scope.** Only depth-0 fresh runs write. Resumed runs write nothing: their `started` claim
already spends the record. Child runs (`P/child_workflow_runner.py:306`) write nothing.

**Rule B5 — outcome independence.** Because the record is written at the start of the later run, it
covers every later outcome with one write per journal file: engine-native pause, completion, failure,
drain and a crash after the writes. A crash between two appends leaves the later files unsuperseded;
the run has had no step, so those records are not stale relative to it.

**Rule B6 — guarantee, and the one bound needing a scope disposition.** A later fresh root run of W
under the same tenant supersedes W's earlier record whenever its path binding binds that record's
directory as a STATE_LEDGER cell. This holds whatever workload class or deployment surface the later
run uses, and whether it then pauses engine-natively, completes or fails. Example: W pauses under
workload class A; a later fresh run of W under class B, with the same binding, appends a supersession
record to A's journal, so a resume with the class-A manifest reads `superseded`. The resume's own
`JournalDirectoryMismatchError` check (`P/lifecycle/root_resume_admission.py:158-160`) compares its read
directory only with its own capture derivation, so it cannot detect a run in another cell. Rule B3's
enumeration does.

*Bound (scope disposition requested, not decided here).* A later run whose path binding does not bind
the earlier record's directory, because its configuration's `path_bindings` differ, cannot see that
journal and does not supersede it. No source the run holds names that directory; covering this case
would need a new cross-binding store, which is outside this contract. The B-310 v4 definition says "any
later run of the same workflow" and does not name this case. The integration lead decides either that
this case needs its own refusal mechanism, or that a run under a binding that does not bind the
record's directory is not a later run of the same workflow for this rule.

## C. C-RT-35 §30 — refusal battery (AMENDED)

The existing `api.resume` order is unchanged: draining (`P/api.py:1362`), invalid workflow (`:1368`),
arguments (`:1375`), protocol-not-bound (`:1389`), concurrent run (`:1409`), durable opt-in (`:1418`),
handle read (`:1424-1440`), depth (`:1444`), workflow mismatch (`:1473`), step index (`:1483`), stale
under the lock (`:1503`), bootstrap (`:1512`), claim (`:1544`).

**Rule C1 — new refusal.** When the handle read returns `superseded`, `api.resume` raises
`ResumePauseRecordSupersededError` at the handle-read step, from the same read and in the same place
where a `None` snapshot raises `ResumeHandleUnknownError`. It precedes depth. It carries no fields
and exposes no workflow identifier, run identifier, path or digest. It is raised before any claim,
bootstrap or resumed body: zero new model, tool or body effects; the superseded record stays
unclaimed; the original `run_id` is never reused by a new run.

**Rule C2 — race ordering.** For each journal file, position under that file's cross-process lock is
the order.

- Supersession record appended after the pre-bootstrap handle read and before the claim: the claim's
  exact-current check (`P/lifecycle/resume_claim_store.py:699-713`) refuses, which maps to
  `RootResumeRefusal.CLAIM_REFUSED` (`P/lifecycle/root_resume_admission.py:116-117`) and is raised as
  `ResumeClaimRefusedError` (`P/api.py:1537-1544`). This window presents as kind `claim`, reason
  `claim-refused`, never as `pause-record-superseded`. The record stays unclaimed and no body effect
  occurs.
- Supersession record appended after the `started` claim is fsynced: the resume owns the record and
  the later run proceeds independently. Any later resume of the workflow sees `superseded`.

**Rule C3 — tenant and absence.** Journal files are keyed by sha256(tenant, workflow_id); a fresh run
never touches another tenant's file. A wrong-tenant handle therefore reads `absent` exactly as today,
and wrong-tenant and absent stay indistinguishable. A bare engine-native pause with no earlier
workflow-layer record leaves no journal file and reads as `handle`/`absent`.

## D. Root refusal value — ninth arm (AMENDS the B-313 v2 value)

The B-313 v2 closed value (`protocol: "harness.resume-refusal.v1"`, eight arms, its field, redaction,
strict-parser, MCP `isError` carrier and tenant-indistinguishability rules) is adopted unchanged, with
one added arm:

| `kind` | Exact `fail_class` | Additional required fields | Python type | CLI exit |
| --- | --- | --- | --- | --- |
| `pause-record-superseded` | `RT-FAIL-RESUME-PAUSE-RECORD-SUPERSEDED` | None | `ResumePauseRecordSupersededError` | 6 |

It is a pre-bootstrap validation arm. It is never collapsed into `handle`, `claim` or `arguments`, and
none of those is inferred from it. Text mode may say "pause record superseded by a later run".

## E. C-RT-29 §14.18.1 — `harness resume` (NEW row)

```text
harness resume WORKFLOW_FILE [--config PATH] [--tenant-id ID] [--output text|json]
```

- The manifest loads through `WorkflowManifestLoader.load_workflow` with the same admissibility check
  as `run` (`P/cli/app.py:456`).
- `resume_handle = workflow.workflow_id`; there is no separate handle flag.
- `--config`, `--tenant-id` and `--output` mean what they mean for `run`.
- Not offered: `--provider`, `--model`, `--daemon`, `--socket-path`, a result timeout, any
  `pause_snapshot` input, and any `resume_context` input (always `None`).
- The subcommand calls `api.resume` exactly once and adds no claim, lease, journal, operation ID or
  approval store, and performs no journal read of its own. The snapshot's `run_id` is kept.

## F. C-RT-29 §14.18.2 — exit code mapping (AMENDED)

**Row 5, case (b) — replaced.** The v1.100 case (b) sentences from "**(b) has NO safe resume path at
v1.100**" to the end of the row are replaced by: "(b) engine-native durable-state pauses
(`pause_snapshot=None`) are not resumable by any surface. `harness resume` resolves only the latest
workflow-layer journal record for the workflow_id; a bare engine-native pause with no earlier
workflow-layer record is refused as `handle`/`absent`, and an earlier workflow-layer record followed by
any later run is refused as `pause-record-superseded`. Plain `harness run` re-invocation is not a resume
path and is not documented as one. Safe engine-native recovery remains an open obligation (B-314)."

**Rows added.** The CLI defines exits 0–5 today (`P/cli/app.py:53-58`); this delta introduces 6 and 7.

| Exit code | Meaning | Trigger |
|---|---|---|
| `6` | RESUME_REFUSED | Any pre-bootstrap resume-validation refusal: `arguments`, `handle`, `depth`, `protocol-not-bound`, `pause-state-stale`, `workflow-mismatch`, `step-index-out-of-range`, `pause-record-superseded` |
| `7` | RESUME_CLAIM_REFUSED | Root claim refusal, kind `claim`, with its `reason`; never success or PAUSED |

Existing 0, 1, 2, 3, 4 and 5 keep their triggers for `resume` as for `run`. A config that loads without
the pause protocol exits 6 `protocol-not-bound`; a genuine config-file load failure keeps exit 3.
JSON mode emits the exact closed refusal value once on stdout; text mode reports kind, fail_class and
the permitted typed facts on stderr. The exit code alone is not the full classification.

## G. C-RT-29 §14.18.4 — failure-mode taxonomy (NEW row)

| Fail class | Trigger | Exit code |
|---|---|---|
| `RT-FAIL-RESUME-PAUSE-RECORD-SUPERSEDED` | Latest journal line for the handle is a supersession record (Rule C1) | 6 |

## H. Not changed, not closed

- The original B-314 obligation, a safe resume path for engine-native pauses, stays OPEN. This delta
  refuses superseded records; it does not resume engine-native pauses.
- `ResumeWorkflowMismatchError` and `ResumePauseStateStaleError` are unreachable from `harness resume`
  (handle equals manifest workflow_id; `resume_context` is always `None`, `P/api.py:898`). Their arms
  still apply to any surface that reaches them.
- Daemon resume (B-311), HTTP operator surface (B-312, excluded) and approval collection (B-315) are
  not defined here.

## I. Required discriminating witnesses (after application)

Future tests, not run by this delta.

1. Positive control: a durable workflow-layer pause with no later run resumes once through
   `harness resume`: exit 0, original `run_id`, one `started` claim; a second invocation is refused
   exit 7 `claim` with zero new effects.
2. Superseded records, three cases with the same assertions: W pauses at the workflow layer and is
   left unclaimed, then a later fresh run of W (a) pauses engine-natively, (b) completes, (c) fails.
   `harness resume` exits 6 `pause-record-superseded` in both output modes, before any claim; zero new
   model, tool or body effects; the old record stays unclaimed. Each case runs twice: with the later
   run in the same STATE_LEDGER cell, and as an A/B directory witness, where W pauses under workload
   class A, the later fresh run uses class B in a different directory of the same binding, and the
   resume uses the class-A manifest and config.
3. Race: a supersession record appended between the handle read and the claim yields exit 7 `claim`,
   reason `claim-refused`; the record stays unclaimed; zero body effects. Cross-process.
4. No prior file: a bare engine-native pause yields exit 6 `handle`/`absent`; no supersession record is
   written by the fresh run.
5. Wrong tenant: indistinguishable from absent in exit, value and output.
6. Opt-in gap: the later run in case 2 has no durable opt-in and still supersedes.
7. Readers: `read_latest` returns `None`; child admission at a supersession position refuses
   `UNREADABLE_RECORD`; a legacy file without `kind` lines reads unchanged.
8. Each reachable B-310 v4 / B-313 v2 refusal keeps its decided exit and value; mutating any mapping
   to another class fails a test; path, secret and tenant canaries never appear in output.
9. Child workflow_id: pin whether a child run can share its root's workflow_id; child runs write no
   supersession record.
10. Request shape: the subcommand accepts no snapshot, context, daemon or model-override input, calls
    `api.resume` exactly once with `resume_handle == workflow.workflow_id` and `resume_context` `None`,
    and performs no journal read, claim, lease or store of its own.
11. HITL probe: a HITL-gated durable pause resumed through `harness resume` records the exit, whether
    the gate re-fired, webhook delivery count, claim state and the new journal record. The result decides
    whether a Runtime-side refusal is needed before acceptance (B-310 v4). No approval is recorded.
12. Operator guide: the guide's exit table and its pinned test list exits 6 and 7, and its code-5 row
    states that engine-native pauses have no safe resume.
13. Accessor (Rule A4): on a superseded record `read_paused_workflow_state()` raises
    `PausedWorkflowStateUnavailableError` with cause `superseded`, `retryable` and `indeterminate`
    false, and returns no token. In a fresh process, exactly one `pause.state.read` event with
    `succeeded=false`, `cause_attribution` `superseded` and no token is retrievable from the real sink.
    The Runtime and OD cause vocabularies are equal at six members.
14. Fan-out (Rule B3): two cells that resolve to one directory receive one record; a cell with no journal
    file for (tenant, W) gets no file; a failed verification or append in any directory fails the fresh
    run before its first step with zero model, tool or body effects.
