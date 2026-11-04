# Spec: Harness Runtime — v1.137 (delta over cleared v1.134)

*Delta-only file. Amendment sites: C-RT-29 §14.18.1 subcommand table (new `resume` row); C-RT-29
§14.18.2 exit code mapping (row 5(b) at `Spec_Harness_Runtime_v1_132.md:1431` replaced; rows 6 and 7
added); C-RT-29 §14.18.4 failure-mode taxonomy (one new fail class); C-RT-35 §30 `resume()` contract
(`Spec_Harness_Runtime_v1_132.md:3669`): the pause-journal record format, the fresh-run supersession
write, and the pre-bootstrap refusal battery; C-RT-35 §14.14.9.4 pause-state accessor failure cause
(Rule A4). Rule A4 also states a companion OD C-OD-30.5.1 amendment that this file does not author.
Neither proposed v1.135 (A5) nor proposed v1.136 (A4) amends any of these sites. Every other v1.134 and
earlier term remains in force. Cleared predecessor files are not edited.*

**Status: Cleared** for source consumption by
`.harness/clearance/spec-harness-runtime-v1-137-cleared-2026-11-04.md` after independent review GREEN
(LIT `cmt-53662ef5`; exact H `eb607692`, `cmt-b58fbcee`) and integration-lead ratification (`cmt-7cc5fc50`,
`cmt-9733f3e9`). It clears no implementation and neither Proposed delta v1.135 nor v1.136.
Corrected after the first independent review of the combined candidate (HOLD, LIT `cmt-bcef30fd`):
F1 in Rules B2, B3, B5, B6 and C2 and witnesses I.2 and I.14; F2 in Rules A3 and A4 and witness I.13.
Second correction (HOLD `cmt-bd5730ba`, disposition `cmt-1ba063e7`): the Rule B6 bound is replaced by
Rule B7 and witness I.2 case (d); the Rule A4 companion OD amendment is authored at
`Spec_Operational_Discipline_v1_43.md` and OD plan v2.37 unit U-OD-62.
Third correction (HOLD `cmt-1087cb00`, disposition `cmt-8b76cb48`): Rules B2, B3, B5, B6, B7 and C2 and
witnesses I.2 and I.14 make the Rule B7 root the only journal location; the binding-cell fan-out is
removed.
Fourth correction (HOLD `cmt-b64cde80`): F3 in Rule B3 and witness I.14 (the durable snapshot capture
resolves the same root); F4 in Rule A1, new Rule B8 and witness I.15 (fail-closed cutover of journals
at the old location).
C-IS-01 companion (after ratification `cmt-7cc5fc50`): Rule B7 item 3 and witness I.14 pin the resume
refusal for an unresolved root to `protocol-not-bound`; IS spec v1.17 §1.1 declares the root. After
review HOLD `cmt-8720af2b`, witness I.14 adds the `harness-inspect` inventory over the root. After
HOLD `cmt-e4e959b9` (disposition `cmt-49143c9e`), Rules B3 and B8 confine their no-read terms to
Runtime journal operations, Rule B8 keeps the operator-only pre-upgrade inventory and witness I.15
covers it.

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

A line without `kind` remains a snapshot record, so a journal's content needs no format migration.
Its location changes (Rule B3); Rule B8 disposes of journals persisted at the old location. Any other
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

**Companion OD amendment (required before implementation ratification; authored at
`Spec_Operational_Discipline_v1_43.md` and OD plan v2.37 unit U-OD-62).** OD
C-OD-30.5.1, cause-attribution row (`Spec_Operational_Discipline_v1_36.md:62`, unchanged through head
v1.42): "one of the five stable identifiers Runtime v1.107 §30 declares" becomes "one of six
identifiers: the five Runtime v1.107 §30 declares, plus `superseded` (Runtime v1.137 Rule A4)", and
`PauseStateCauseAttribution` gains `SUPERSEDED = "superseded"`. Nothing else in §30.5 changes. A failed
read still carries no token, so the §30.5.3 pairing rule is unaffected. Its owner is profile-coder under
disposition `cmt-1ba063e7`.

## B. C-RT-35 §30 — fresh-run supersession write (NEW)

**Rule B1 — single enforcer.** Every fresh (non-resume) root run enters the MCP tool `run_workflow`
(`P/mcp_server.py:296`), from `api.run` (`P/api.py:668` → `:779` → `call_tool("run_workflow")` `:596`)
and from daemon clients (`P/cli/app.py:229-231`). That tool runs the body through
`_admission.run(harness_ctx, _execute)` (`P/mcp_server.py:494-497`); a fresh run uses the default
`UNCLAIMED` admission (`:381`; `P/lifecycle/root_resume_admission.py:185-187`). The Runtime-owned
fresh-run admission replacing `UNCLAIMED` is the one place that writes a supersession record. It
appends the record, then calls `body(None)`. It runs before the run's first step or any model, tool or
body effect.

**Rule B2 — what is written, and when.** When the journal file for (tenant, workflow_id) in the Rule B3
location exists and is non-empty, the fresh-run admission appends one supersession record to it under
its journal lock. When it does not exist there is nothing to supersede and nothing is written. The
`run_id` field is the fresh run's own `run_id`.

**Rule B3 — journal location: the one Rule B7 root.** Every pause-journal read, snapshot write,
supersession write and claim for (tenant, workflow_id) uses the one journal file for that key in the
Rule B7 pause-journal root of the installation and tenant. This replaces today's derivation of the
journal directory from the run's STATE_LEDGER cell at all three of its sites: the durable snapshot
capture (`JournalWorkflowPauseStore(journal_dir=pause_journal_dir_for(state_ledger_dir))`,
`P/bootstrap/factories/pause_resume_protocol_factory.py:199-210`), the read (`P/api.py:849-857`) and
the claim (`pause_journal_dir_for(ctx.ledger_writer.handle.canonical_path.parent)`,
`P/lifecycle/root_resume_admission.py:158`), and the resume's `JournalDirectoryMismatchError`
comparison between capture and claim directories (`:158-160`). These are the only callers of
`pause_journal_dir_for` (`P/lifecycle/journal_workflow_pause_store.py:338`). All three sites, and the
supersession append, obtain the journal directory from one Runtime root resolver; the STATE_LEDGER
derivation is removed, so a captured snapshot lands in the file the handle read and the claim open. No journal path is derived from the run's `path_bindings`,
workload class or deployment surface, and no journal operation reads, writes or enumerates any
other directory: a STATE_LEDGER cell holds no journal. The operator-only §13.7 inventory is not a
journal operation (Rule B8). The append uses the placement verification `DurableRootResume`
applies before its claim (`P/lifecycle/root_resume_admission.py:148-155`), applied to the root. A
failed root resolution, verification or append fails the fresh run before its first step. The write
does not depend on the durable pause opt-in: a later run whose config lacks
`pause_resume_protocol_config` or the durable opt-in still supersedes.

**Rule B4 — scope.** Only depth-0 fresh runs write. Resumed runs write nothing: their `started` claim
already spends the record. Child runs (`P/child_workflow_runner.py:306`) write nothing.

**Rule B5 — outcome independence.** Because the record is written at the start of the later run, it
covers every later outcome with one write: engine-native pause, completion, failure, drain and a crash
after the write. A crash before the append leaves the record unsuperseded; the run has had no step,
so the record is not stale relative to it.

**Rule B6 — guarantee.** With the Rule B7 root bound, a later fresh root run of W under the same tenant
supersedes W's earlier record whatever its path binding, workload class, deployment surface or
process, and whether it then pauses engine-natively, completes or fails. Example: W pauses under
configuration A; a later fresh run of W in another process uses configuration B, whose
`path_bindings` omit A's STATE_LEDGER directory, and appends to the same root file, so a resume with
configuration A reads `superseded`.

**Rule B7 — a later run under a different binding: the missing shared authority.** Disposition
`cmt-1ba063e7` keeps the B-310 v4 invariant with no binding exception: after any later fresh root run
of W for the same tenant, W's earlier record is never claimed, including when the later run's
configuration binds different STATE_LEDGER directories and when it runs in another process. Current
bindings cannot carry this. C-IS-01 declares four path classes, each varying by workflow class and
deployment surface (`harness_is/path_class_registry.py:31-37`, `:109-112`), and a run's own
`config.path_bindings` is the resolver's only path source, with no default (`harness_is/path_binding.py:49-54`,
`harness_is/path_resolver.py:62-68`). A run
whose binding omits directory A holds no name for A, and a resume bound to A holds no name for the
later run's directories. So neither a refusal nor an admission restriction can be enforced from state
either process holds: the resume cannot see the later run, the later run cannot see the record, and
per-run configuration is exactly what differs between them.

The missing shared authority, exactly: one Runtime-owned pause-journal root per Runtime installation
and tenant that (1) every process able to start or resume a root run of that installation (CLI, MCP
server, daemon) resolves identically from installation state, not from per-run `path_bindings`,
workload class or deployment surface; (2) holds the one journal file per (tenant, workflow_id), keyed
as today, under that file's existing cross-process lock; (3) fails closed: a fresh root run that cannot
resolve it fails before its first step, and a resume that cannot resolve it refuses before any claim or
bootstrap, with the existing `protocol-not-bound` arm (`ResumeProtocolNotBoundError`, exit 6) at that
check's position: without a resolved root the pause protocol is not bound. No arm, field or handle
cause is added, and an unresolved root never presents as `handle`/`absent`, which would make a lost
root indistinguishable from a missing pause. Rule B3 makes it the only journal location, Rules B2,
B5, C1 and C2 apply to its one file
per key, and the journal stays the only ordering record: no second journal, read path or claim
store. Its storage location is the retained runtime-state boundary release-campaign §4 lists as not yet
selected, and C-IS-01 has no path class for it. Two prerequisites sit outside this delta, each with a
named owner (LIT `cmt-8b76cb48`): selecting and binding that storage with its retention evidence
(Buford, integration lead), and the C-IS-01 companion amendment (profile-coder; IS spec v1.17, IS plan
v2.11 unit U-IS-21). (4) Gate: no implementation of this contract is accepted and `harness resume` is
not exposed until both are ratified and applied. Until the root is bound, every resume refuses under
item 3 before any claim, bootstrap or effect.

**Rule B8 — journals at the old location: fail-closed cutover, no migration.** Journals persisted under
a STATE_LEDGER cell (`<state_ledger_dir>/pause-journal`) before the root is bound are not read,
written, claimed, enumerated, moved or deleted by any Runtime journal operation: fresh run, snapshot
capture, handle read, supersession append or claim. A resume whose key has no file
in the root refuses with handle cause `absent` (Rule A3) before any claim or bootstrap, as a resume
does today when its binding omits the capture directory; a fresh run writes no supersession record for
that key (Rule B2). A migration is not specified because it would have to enumerate every STATE_LEDGER
cell a past binding used, which Rule B7 shows no process can name, and a legacy-location fallback
would be a second read and claim path. The files stay on disk, unclaimed, as operator-owned data. The
operator guide states that a pause captured before the root was bound cannot be resumed.

Operator inventory stays (disposition `cmt-49143c9e`). The operator-only `harness-inspect` surface
(spec v1 §13.7) is not a journal operation and keeps its term 2 pre-upgrade inventory. Each invocation
reads and enumerates one directory, chosen in this order: the explicit `--pause-journal-dir`; otherwise
the resolved root; otherwise, when the root is `unresolved(unbound)` (IS spec v1.17 §1.1), the existing
`<ledger dir>/pause-journal` default. Any other unresolved cause fails as an unreadable pause-journal
directory. An unbound declaration is not an absent directory: term 5 disengages the surface only when
the chosen directory does not exist. Terms 1–7 and §13.7.1 apply unchanged, including the read-only
invariant. The chosen directory is a diagnostic read, never a journal location, and no inventory
result resumes, claims, moves or deletes a journal. The tenant-facing read path gains no enumeration,
and no other past binding's directory is scanned.

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

**Rule C2 — race ordering.** Position in the root journal file, under its cross-process lock, is the
order.

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
   model, tool or body effects; the old record stays unclaimed. All runs share one bound Rule B7 root.
   Each case runs twice: with the later run under the same configuration, and as case (d), distinct
   bindings: W pauses under configuration A (workload class A); the later fresh run of W, in another
   process, uses configuration B (workload class B), whose `path_bindings` omit A's STATE_LEDGER
   directory; `harness resume` with the old manifest and configuration A gives the same result.
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
    states that engine-native pauses have no safe resume, and that a pause captured before the Rule B7
    root was bound cannot be resumed (Rule B8).
13. Accessor (Rule A4): on a superseded record `read_paused_workflow_state()` raises
    `PausedWorkflowStateUnavailableError` with cause `superseded`, `retryable` and `indeterminate`
    false, and returns no token. In a fresh process, exactly one `pause.state.read` event with
    `succeeded=false`, `cause_attribution` `superseded` and no token is retrievable from the real sink.
    The Runtime and OD cause vocabularies are equal at six members.
14. One root (Rules B3 and B7): across configurations with different `path_bindings`, workload
    classes and deployment surfaces, and from CLI, MCP server and daemon processes, every journal read,
    snapshot write, supersession append and claim for (tenant, W) touches only the root file; no journal
    file is created or read under a STATE_LEDGER cell. Unresolvable root: a fresh run fails before its
    first step and a resume refuses exit 6 `protocol-not-bound` in both output modes before any claim or
    bootstrap, for each unresolved cause of IS spec v1.17 §1.1, each with zero model, tool or body
    effects and no journal write. A failed verification or append fails the fresh run likewise.
    Capture-to-read identity: under configurations whose STATE_LEDGER cells differ, the file the
    durable factory's store appends a captured snapshot to is the same file (same real path) that the
    `api.resume` handle read and the claim open; a test fails if the store is built from the
    STATE_LEDGER cell. Inventory: by default `harness-inspect` (§13.7) lists the root as its
    pause-journal directory; over a root holding journals of several tenants it lists every canonical journal,
    classified per §13.7.1, and enumerates no STATE_LEDGER cell.
15. Cutover (Rule B8): with the root bound and holding no file for (tenant, W), and a valid snapshot
    journal for W at `<state_ledger_dir>/pause-journal` from the old derivation, `harness resume`
    exits 6 `handle`/`absent` before any claim or bootstrap with zero model, tool or body effects; a
    fresh run of W writes no supersession record; the legacy file is byte-identical and unclaimed
    afterwards; a mutation that makes a journal operation read or claim the legacy location fails a
    test. Operator inventory (Rule B8): with the root unbound and `<ledger dir>/pause-journal`
    populated, `harness-inspect` lists every canonical journal there, classified per §13.7.1 with the
    term 3-bis limit; with the root unbound and that directory absent, its output is byte-unchanged
    (term 5); with the root bound, the default lists the root and an explicit `--pause-journal-dir`
    naming the legacy directory lists the legacy journals. In each case every file is byte-identical
    afterwards (the chmod-readonly fixture), nothing is claimed, and a resume of a listed legacy
    workflow refuses as it would without the inventory (exit 6 `protocol-not-bound` while unbound,
    `handle`/`absent` once bound). A mutation that disengages the surface on an unbound declaration
    over a populated legacy directory fails a test.
