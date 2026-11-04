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
Merge-gate correction (PR #1697 pass 1 BLOCK, LIT `cmt-5d0f2389`; pending independent review and
ratification): Rule B1 requires a per-invocation fresh-run admission; Rule B2 makes the existence check
and the append one step under the journal lock; Rules B5, B6 and C2 define earlier and later by journal
position, including for overlapping root runs; Rule B7 item 1 states that a run's bindings can only
make resolution fail; new witness I.16.
Merge-gate pass 2 (PR #1697, witness-adequacy BLOCK at `a1072c21`; pending independent review and
ratification): witness I.16 pins lock scope and per-invocation admission with forced interleavings
that each have one expected result, including a pre-body failure beside a success.
Upstream review finding (PR #1697 `discussion_r4470801910`, P2, LIT `cmt-7a16a6df`; pending independent
review and ratification): §D.1–§D.4 transcribe the adopted B-313 v2 value, boundaries, redaction and
proof word for word, so the eight adopted arms are normative in this repository; §D.5 holds the
ninth arm.

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
(`P/lifecycle/mcp_server.py:296`), from `api.run` (`P/api.py:668` → `:779` → `call_tool("run_workflow")` `:596`)
and from daemon clients (`P/cli/app.py:229-231`). That tool runs the body through
`_admission.run(harness_ctx, _execute)` (`P/lifecycle/mcp_server.py:494-497`); a fresh run uses the default
`UNCLAIMED` admission (`:381`; `P/lifecycle/root_resume_admission.py:185-187`). The Runtime-owned
fresh-run admission replacing `UNCLAIMED` is the one place that writes a supersession record. It
appends the record, then calls `body(None)`. It runs before the run's first step or any model, tool or
body effect. Each `run_workflow` invocation constructs its own fresh-run admission in the handler,
carrying that invocation's `run_id` (`P/lifecycle/mcp_server.py:376`) and its own pre-body failure, as
`api.resume` constructs one `DurableRootResume` per resume (`P/lifecycle/root_resume_admission.py:139`).
No admission object, `run_id` or failure is shared between invocations. The daemon handler takes no
process lock, so concurrent daemon calls would otherwise overwrite each other's `run_id` or failure.

**Rule B2 — what is written, and when.** The fresh-run admission takes the journal lock of the
(tenant, workflow_id) file in the Rule B3 location, then checks and writes in that one locked step. When
the file exists and is non-empty it appends one supersession record; otherwise there is nothing to
supersede, and it writes no journal line (the lock file is created as for any journal operation). The
existence check is never made before the lock is held, so a concurrent snapshot capture that creates
the file is ordered entirely before or entirely after the check. The `run_id` field is the fresh run's
own `run_id`. This locked step is the run's admission point in the journal order (Rule C2).

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

**Rule B5 — outcome independence.** Because the record is written at the later run's admission point, it
covers every outcome of that run with one write: engine-native pause, completion, failure, drain and a crash
after the write. A crash before the append leaves the record unsuperseded; the run has had no step,
so the record is not stale relative to it.

**Rule B6 — guarantee.** With the Rule B7 root bound, a later fresh root run of W under the same tenant
supersedes W's earlier record whatever its path binding, workload class, deployment surface or
process, and whether it then pauses engine-natively, completes or fails. Example: W pauses under
configuration A; a later fresh run of W in another process uses configuration B, whose
`path_bindings` omit A's STATE_LEDGER directory, and appends to the same root file, so a resume with
configuration A reads `superseded`.

Earlier and later are journal positions in the root file (Rule C2), not process start or wall-clock
time. A record is earlier than a fresh run when it precedes that run's admission point (Rule B2).
Overlapping root runs follow the same order. If run R1 has been admitted, run R2 is then admitted, and
R1 captures a snapshot afterwards, that snapshot follows R2's admission point. It is the latest record
and stays resumable until another fresh run is admitted. Resuming it continues R1 over R2's effects,
exactly as R1 would have continued had it not paused. Root runs of one workflow can overlap today: the
`_run_lock` check (`P/api.py:531`, `:714`) is per process and guards only `api.run` and `api.resume`.
This delta neither adds nor removes that concurrency. A snapshot captured before R2's admission point
is superseded.

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
workload class or deployment surface, where a run's bound paths can only make resolution fail (IS spec
v1.17 §1.1 `overlapping`) and never select another root, and a fresh run that fails resolution has no
first step, so it neither supersedes a record nor captures one; (2) holds the one journal file per (tenant, workflow_id), keyed
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
- Overlapping root runs: every admission point (Rule B2) and every snapshot capture is a locked step
  under the same lock, so their order is total. A capture after another fresh run's admission point is
  the latest record and is resumable (Rule B6). A capture before that point is superseded by it.

**Rule C3 — tenant and absence.** Journal files are keyed by sha256(tenant, workflow_id); a fresh run
never touches another tenant's file. A wrong-tenant handle therefore reads `absent` exactly as today,
and wrong-tenant and absent stay indistinguishable. A bare engine-native pause with no earlier
workflow-layer record leaves no journal file and reads as `handle`/`absent`.

## D. Root refusal value — the adopted B-313 v2 value plus a ninth arm (AMENDS the B-313 v2 value)

The B-313 v2 closed value is adopted unchanged, with one added arm (§D.5). §D.1–§D.4 make it normative
in this repository. They transcribe, word for word, the adopted decision's sections "Closed refusal
value", "MCP and Python boundaries", the redaction paragraph of "CLI presentation" and items 1–6 of
"Required discriminating proof after contract application" (authority item 3 in
`.harness/runtime-resume-contract-authority.md`, SHA256
`c63b16f754b4298790e6682d1b435f7def232a50d2c7287eb97cccd8b3e9dfc3`). No word is changed.
"Proposed" and "this proposal" in the transcribed text mean the B-313 v2 decision as adopted here. §F
replaces its CLI presentation table, and the seven pre-bootstrap validation refusals it counts are eight
with §D.5.

### D.1 Closed refusal value (B-313 v2, adopted)

A refusal is an object with exactly `protocol` and `refusal`.
`protocol` is the literal string `harness.resume-refusal.v1`. `refusal` is
exactly one of these closed objects; fields from different arms cannot mix.

| `kind` | Exact `fail_class` | Additional required fields |
| --- | --- | --- |
| `arguments` | `RT-FAIL-RESUME-ARGS` | None |
| `handle` | `RT-FAIL-RESUME-HANDLE-UNKNOWN` | `cause`, `retryable`, `indeterminate` |
| `depth` | `RT-FAIL-RESUME-DIRECT-CHILD-HANDLE` | `depth` |
| `protocol-not-bound` | `RT-FAIL-RESUME-PROTOCOL-NOT-BOUND` | None |
| `pause-state-stale` | `RT-FAIL-RESUME-PAUSE-STATE-STALE` | None |
| `workflow-mismatch` | `RT-FAIL-RESUME-WORKFLOW-MISMATCH` | None |
| `step-index-out-of-range` | `RT-FAIL-RESUME-STEP-INDEX-OUT-OF-RANGE` | None |
| `claim` | `RT-FAIL-RESUME-CLAIM-REFUSED` | `reason` |

`cause` is exactly one of `absent`, `empty-journal`, `read-error`,
`corrupt-latest`, `workflow-mismatch`. `retryable` and `indeterminate` are JSON
booleans copied from the original `ResumeHandleUnknownError`. They are not
recomputed from `cause`: `read-error` retryability depends on the underlying
read error, and corrupt-latest decode and parse failures differ in
indeterminacy. Preserve these facts while withholding the raw errno, exception
message, filesystem path and bytes. Preserve the existing indistinguishability
of absent, wrong-tenant and abandoned legacy records; introduce no discriminator
or existence oracle for those underlying states.

`depth` is the recorded integer or JSON null for unknown depth, copied from
`ResumeDirectChildHandleError`; a JSON boolean is not an integer. Do not infer
root depth from null, a malformed record or an omitted field.

`reason` is exactly one of `placement`, `claim-refused`, `claim-busy`,
`start-refused`, copied from the typed root refusal. Claim-busy retains its
existing retryable meaning; other reasons do not acquire it. The presentation
layer does not automatically retry any refusal.

The four validation arms with no additional fields identify only their exact
kind/fail_class. They expose no workflow identifiers, indices, pause tokens,
configuration values or exception prose. Map each named Python type to its own
row; do not collapse a validation error into `arguments`, `handle` or `claim`.
In particular, `handle` with `cause: "workflow-mismatch"` is the durable-read
failure carried by `ResumeHandleUnknownError`; the separate `workflow-mismatch`
arm represents `ResumeWorkflowMismatchError`. Neither is inferred from the other.

The pause-state-stale text presentation may say "paused state changed; re-read
and recompose" without copying the token, comparing digests on the surface, or
retrying the resume. Protocol-not-bound may say "pause protocol is not bound";
the other validation kinds may use their stable names. These are descriptions
of typed values, never recovery instructions to bypass a refusing precondition.

Construct the value from typed exceptions, not their message strings. At the
receiving boundary, a strict parser returns the corresponding discriminated
value or an explicit protocol error. Reject extra or missing fields, unknown
protocols/kinds/codes/reasons/causes, mismatched kind/fail_class pairs, quoted
booleans and malformed JSON. No success-shaped default and no parsing a human
exception message to recover a refusal.

Example valid value:

```json
{"protocol":"harness.resume-refusal.v1","refusal":{"kind":"handle","fail_class":"RT-FAIL-RESUME-HANDLE-UNKNOWN","cause":"read-error","retryable":false,"indeterminate":false}}
```

The same cause with `retryable: true` is also representable when the originating
typed error says so. A receiver cannot replace either value with its own cause
lookup table. A claim refusal carrying a `cause` field, or a handle refusal
carrying `reason: "claim-busy"`, is invalid.

### D.2 MCP and Python boundaries (B-313 v2, adopted)

For a recognized refusal, the proposed daemon resume operation returns an MCP
tool result with `isError: true` and exactly one text content item containing
the serialized closed refusal object above. The text item is explicitly a JSON
data carrier, not an exception-message convention. The decoder requires both
the error indicator and the exact protocol/object schema. It accepts no prefix,
suffix, second content item or recovered substring. It never infers a refusal
from prose produced by the server or transport.

A non-refusal resume reply retains the existing RunResult representation.
This change does not wrap ordinary `run_workflow` results, create a replacement
RunResult type, or reinterpret a child refusal embedded in an applicable
RunResult as a root pre-body refusal. B-311 separately defines the daemon resume
request and binding to `api.resume`; this proposal specifies its refusal reply.

The local Python API still returns RunResult or raises its actual existing
typed exception. Its local `__cause__` relationship is preserved. A decoded
remote refusal is a presentation value, not a fabricated original Python
exception or proof of remote exception-object identity.

An unrecognized tool/transport failure is a protocol/runtime failure, not a
root claim refusal. A malformed or lost reply gives no proof that the body did
not run and never authorizes replay. Only a valid typed root admission refusal
carries the existing pre-body refusal meaning. Bootstrap, invalid-workflow,
concurrent-run and unrelated failures keep their existing classifications;
they do not become arms of this root-refusal value.

### D.3 CLI output redaction (B-313 v2, adopted)

JSON refusal output adds no raw exception text, resolved path, record digest,
claim token, tenant identifier or new operation/run identifier. Text mode uses
the same discriminated value, with no message scraping. The implementation
must update the operator guide and the owning CLI exit table together with the
new behavior. A shell exit code alone is not the full refusal classification.

### D.4 Required discriminating proof (B-313 v2, adopted)

1. Exercise the real API errors at their owning pre-bootstrap/pre-body seams
   and preserve all eight named typed classes and fail_class values across the
   MCP adapter and receiving parser. At the real API, cover a loaded config
   without the pause protocol, a stale accessor token, an out-of-range stored
   step index, and workflow mismatch wherever the selected API input path
   admits that error. Distinguish a durable-read workflow-mismatch cause from
   the separate workflow-mismatch exception. A path made unreachable by a
   surface's admitted inputs is recorded as such, not claimed as a live
   witness from a mocked exception; its typed adapter mapping is still tested.
   Test all four root reasons and all five handle
   causes; use both read-error retryability values and both corrupt-latest
   indeterminacy values. Confirm the adapter preserves the originating booleans.
2. Mutate kind/fail_class association, erase a flag, force every read-error to
   retryable, force every corrupt-latest to permanent, or convert null depth to
   root depth: each mutation must make the corresponding behavioral test fail.
   Misclassifying any of the four added validation types as a claim, a handle
   read, a config-load failure or an unrecognized transport failure must also
   fail the corresponding adapter/CLI witness.
3. Run real CLI invocation tests for exits 6 and 7 and both output modes, plus
   unchanged representative exits 0–5. Prove specifically that a successfully
   loaded config missing the pause protocol emits its closed refusal with exit
   6; a genuine config-file load error keeps exit 3. Malformed JSON, extra/missing fields,
   quoted booleans, unknown discriminators and mixed arms must refuse loudly.
4. At the real resume entrypoint, prove one handle read/admission path, one-shot
   resume_context delivery, original run_id retention and no surface-owned
   claim/approval store. A real root claim-busy/already-claimed refusal must
   produce zero new model/tool/body effects. An argument/depth error must not
   be relabeled claim-busy to obtain that result.
5. Verify a separately accepted child-refusal RunResult stays a child refusal;
   retain genuine failure/cancellation behavior. This test must bind the actual
   applicable A4 interface instead of assuming the Proposed result shape is
   installed. It is an explicit acceptance dependency, not current proof.
6. Use path/secret/tenant canaries in exception messages and causes; none may
   appear in refusal output. Wrong-tenant and absent projections must retain
   their existing indistinguishability. For damaged or missing replies, prove
   no automatic second resume and no claim that effects were absent.

### D.5 Ninth arm (this delta)

| `kind` | Exact `fail_class` | Additional required fields | Python type | CLI exit |
| --- | --- | --- | --- | --- |
| `pause-record-superseded` | `RT-FAIL-RESUME-PAUSE-RECORD-SUPERSEDED` | None | `ResumePauseRecordSupersededError` | 6 |

With it, `refusal` is exactly one of nine closed objects: the eight of §D.1 and this one. It is a
pre-bootstrap validation arm. Like the §D.1 validation arms with no additional fields, it identifies only
its exact kind and fail_class (Rule C1). It is never collapsed into `handle`, `claim` or `arguments`, and
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
16. Overlap and admission (Rules B1, B2, B6 and C2), cross-process: with a non-empty root file for
    (tenant, W), R1 is admitted and appends its supersession record; R2 is then admitted, appends its
    own and completes; R1 then pauses at the workflow layer. The journal order is R1's admission,
    R2's admission, then R1's snapshot, and `harness resume` claims that snapshot once (exit 0). In
    the reversed case, where R1 captures before R2 is admitted, the resume exits 6
    `pause-record-superseded`. Lock scope, from no root file: the test holds the journal lock, starts a
    fresh run and waits until its admission blocks on that lock, writes one snapshot for (tenant, W)
    under the held lock, then releases it. The admission appends its supersession record and the resume
    exits 6 `pause-record-superseded`; a mutation that checks the file's existence before taking the
    lock writes nothing, so the resume exits 0 and the test fails. Per-invocation admission: three
    concurrent daemon `run_workflow` calls are held at a barrier until all three admissions are
    constructed, then released in a forced order. W's non-empty root file is read-only. F1 runs W with
    bound paths that make root resolution fail (IS spec v1.17 §1.1 `overlapping`), so it touches no
    journal. F2 runs W with ordinary bindings, so its supersession append fails. F1 and F2 each record
    their pre-body failure before either F caller's outcome is projected. S then runs a second workflow
    W2 with a non-empty root file, appends a record carrying S's own `run_id` and completes, and S's
    outcome is projected; F1's and F2's outcomes are projected after it. The test asserts all three
    outcomes: S's caller receives success with S's `run_id`, F1's caller the root-resolution failure
    and F2's caller the append failure. A mutation that shares the admission object, the `run_id` or
    the pre-body failure between invocations fails this test: a shared failure slot gives one F caller
    the other's cause, or S a failure, and a shared object crosses `run_id`.
