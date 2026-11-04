# Implementation Plan: Harness Runtime — v2.68 (delta over cleared v2.65)

**Status: Cleared** for source consumption by
`.harness/clearance/implementation-plan-harness-runtime-v2-68-cleared-2026-11-04.md` (ratification
`cmt-7cc5fc50`; exact H `eb607692`, `cmt-9733f3e9`). Grounded on cleared v2.65 (A3, U-RT-157;
`.harness/clearance/implementation-plan-harness-runtime-v2-65-cleared-2026-10-04.md`); implements
cleared Runtime spec v1.137. Plans v2.66 (A5, U-RT-158) and v2.67 (A4, U-RT-159) are separately
PROPOSED and not cleared. Fold order is A3 → A5 → A4 → this delta, so this unit is U-RT-160; a unit-ID
collision recheck is owed at landing. Spec v1.137 amends no site that v1.135 or v1.136 amends.
Authority: `.harness/runtime-resume-contract-authority.md`. Fork:
`.harness/class_1_fork_runtime_resume_cli_supersession.md`. This is a cleared contract, not
an accepted implementation or a product release. Corrected after the first independent review of the
combined candidate (HOLD, LIT `cmt-bcef30fd`, F1 and F2), and after HOLD `cmt-1087cb00` (disposition
`cmt-8b76cb48`): the spec Rule B7 root is the only journal location, with no binding-cell fan-out.
Fourth correction (HOLD `cmt-b64cde80`, F3 and F4): the durable snapshot capture resolves the same root
(spec Rule B3), and journals at the old location get a fail-closed cutover (spec Rule B8).
C-IS-01 companion (after ratification `cmt-7cc5fc50`): criterion 15 pins the unresolved-root resume
refusal to `protocol-not-bound` (spec Rule B7 item 3); after review HOLD `cmt-8720af2b` portion 160a
and criterion 15 retarget the `harness-inspect` enumeration to the root; after HOLD `cmt-e4e959b9`
(disposition `cmt-49143c9e`) 160a keeps the spec Rule B8 pre-upgrade inventory and criterion 17
witnesses it.
Merge-gate correction (PR #1697 pass 1 BLOCK, LIT `cmt-5d0f2389`; pending independent review and
ratification): 160a constructs the fresh-run admission per invocation and checks and appends under the
journal lock (spec Rules B1 and B2); new criterion 18 witnesses overlap and admission (spec §I.16). Upstream finding
`discussion_r4470801910` (LIT `cmt-7a16a6df`): the refusal value and proof cites resolve to spec §D.

## U-RT-160 — superseded-record refusal and `harness resume` (B-314 prerequisite, B-313, B-310)

`P` = `harness-runtime/src/harness_runtime`.

**Source, portion 160a (Runtime prerequisite, spec v1.137 §A–§D, §G):**
`P/lifecycle/journal_workflow_pause_store.py` (supersession record kind beside the snapshot record;
appended only through `_append`; `read_latest_attributed` returns `superseded`; `read_latest` and
`read_exact` return `None` at a supersession position; `pause_journal_dir_for` is replaced by the one
Runtime root resolver that every journal site below uses, spec Rule B3);
`P/bootstrap/factories/pause_resume_protocol_factory.py` (the durable snapshot store's journal directory
resolves the Rule B7 root instead of `<state_ledger_dir>/pause-journal`, spec Rule B3, so captured
snapshots land in the file the read and claim use);
`P/lifecycle/root_resume_admission.py` (the Runtime-owned fresh-run admission that replaces
`UNCLAIMED` for depth-0 fresh runs and, before `body(None)`, takes the journal lock for (tenant,
workflow_id) in the spec Rule B7 root and, under it, appends the supersession record when that journal
exists and is non-empty, spec Rules B2–B3; the
claim resolves the same root, replacing the capture-directory derivation and its
`JournalDirectoryMismatchError` check);
`P/lifecycle/mcp_server.py` (constructs that admission per `run_workflow` invocation with the
invocation's own `run_id` and pre-body failure, spec Rule B1, so `api.run` and daemon clients use it and
no invocation shares another's);
`P/api.py` (the journal read resolves the Rule B7 root instead of the run's STATE_LEDGER cell;
`ResumePauseRecordSupersededError`, raised from the handle read where a `None` snapshot
raises `ResumeHandleUnknownError`, before depth; the pause-state accessor's `superseded` result and its
failed-read audit event, spec Rule A4);
`P/admin/inspect.py` (the §13.7 inventory directory, spec Rule B8 and IS spec v1.17 §1.1: the explicit
`--pause-journal-dir`; otherwise the resolved Rule B7 root; otherwise, for an unbound declaration, the
existing `<ledger dir>/pause-journal` default, so the §13.7 term 2 pre-upgrade inventory remains; any
other unresolved cause fails as an unreadable pause-journal directory, and term 5 disengages only for
an absent chosen directory; the choice is a read-only diagnostic, never a journal location);
`harness-od/src/harness_od/pause_resume_namespace.py` (`PauseStateCauseAttribution.SUPERSEDED`), only
after the companion OD amendment (OD spec v1.43, OD plan v2.37 unit U-OD-62) is ratified.

**Source, portion 160b (CLI, spec v1.137 §D–§F):**
one Runtime-owned module for the closed `harness.resume-refusal.v1` value (spec §D: B-313 v2 plus the ninth
arm): the typed value, its projection from the nine typed exceptions, and its strict parser;
`P/cli/app.py` (`resume` subcommand, exits 6 and 7, JSON/text refusal presentation);
`docs/how-to-operate-runtime.md` and `harness-runtime/tests/test_operator_guide_exit_codes.py`
(rows 6 and 7; the code-5 row follows the replaced spec row 5(b)).
No daemon resume tool or MCP refusal carrier is added: B-311 defines the daemon resume operation and
reuses this value's strict parser for its `isError` reply.

**Acceptance criteria:**
1. Positive control (spec §I.1): a durable workflow-layer pause with no later run resumes once
   through `harness resume`: exit 0, original `run_id`, one `started` claim. A second invocation exits
   7 `claim` with zero new model, tool or body effects.
2. Superseded record (spec §I.2): W pauses at the workflow layer and is left unclaimed; a later fresh
   run of W (a) pauses engine-natively, (b) completes, (c) fails. Three separate cases, same
   assertions: exit 6 `pause-record-superseded` in both output modes, before any claim; zero new
   model, tool or body effects; the old record stays unclaimed; never presented as success or PAUSED.
   All runs share one bound Rule B7 root. Each case also runs as case (d) (spec §I.2): W pauses under
   configuration A (workload class A); the later fresh run, in another process, uses configuration B
   (workload class B), whose `path_bindings` omit A's STATE_LEDGER directory; the resume uses the
   old manifest and configuration A.
3. Race (spec §I.3), cross-process: a supersession record appended between the handle read and the
   claim yields exit 7 `claim`, reason `claim-refused`; the record stays unclaimed; zero body effects.
4. No prior file (spec §I.4): a bare engine-native pause yields exit 6 `handle`/`absent`, and the
   fresh run writes no supersession record.
5. Wrong tenant (spec §I.5) is indistinguishable from absent in exit, value and output.
6. Opt-in gap (spec §I.6): the later run in criterion 2 has no durable opt-in and still supersedes.
7. Readers (spec §I.7): `read_latest` returns `None` at a supersession record; child admission at a
   supersession position refuses `UNREADABLE_RECORD`; a legacy journal without `kind` reads
   unchanged; a `kind` line with an unknown value or extra/missing fields reads `corrupt-latest`.
8. Refusal mapping (spec §I.8; spec §D.4 proof 1–3, 6 at the CLI-reachable inputs): each reachable
   arm keeps its kind, fail_class, typed facts and exit; a config that loads without the pause
   protocol exits 6 `protocol-not-bound`, a genuine config-file load error keeps exit 3; the strict
   parser refuses malformed JSON, extra or missing fields, quoted booleans, unknown discriminators and
   mixed arms; path, secret and tenant canaries never appear in output. The two arms the CLI cannot
   reach (`workflow-mismatch`, `pause-state-stale`) are tested at the projection, not claimed as live
   CLI witnesses.
9. Mutations that must fail a test: moving any arm to another kind, fail_class or exit; reporting
   `superseded` as a `handle` cause, as `claim` or as `corrupt-latest`; writing the supersession
   record only when the durable opt-in is present; writing it only to the run's own capture
   directory; building the durable snapshot store from the STATE_LEDGER cell; reading or claiming a
   journal at the old location; writing it from a resumed or child run; writing it after the first step; continuing the
   run after a failed append; mapping the accessor's `superseded` to any of the five causes; dropping
   the record-count or digest change from the staleness token.
10. Request shape (spec §I.10): the subcommand accepts no snapshot, context, daemon or model-override
    input, calls `api.resume` exactly once with `resume_handle == workflow.workflow_id` and
    `resume_context is None`, and performs no journal read, claim, lease or store of its own.
11. HITL probe (spec §I.11): a HITL-gated durable pause resumed by the CLI records the exit, whether
    the gate re-fired, webhook delivery count, claim state and the new journal record. The result
    decides whether a Runtime-side refusal is needed before acceptance; no approval is recorded.
12. Child workflow_id (spec §I.9): pin whether a child run can share its root's workflow_id; child
    runs write no supersession record.
13. Operator guide (spec §I.12): the guide and its pinned test list exits 6 and 7 with their
    meanings; the code-5 row states no safe resume for engine-native pauses; the guide states that a
    pause captured before the root was bound cannot be resumed (spec Rule B8).
14. Accessor (spec §I.13): `superseded` raises `PausedWorkflowStateUnavailableError` with cause
    `superseded`, not retryable, not indeterminate, no token; one failed-read `pause.state.read` event
    with `cause_attribution` `superseded` is retrievable from the real sink in a fresh process; the
    Runtime and OD vocabularies are equal at six members.
15. One root (spec §I.14): across configurations with different bindings, workload classes and
    surfaces, and from CLI, MCP server and daemon processes, every journal read, write and claim for
    the key touches only the root file and no STATE_LEDGER cell holds a journal. With the root
    unresolvable, a fresh run fails before its first step and a resume refuses exit 6
    `protocol-not-bound` before any claim or bootstrap for each unresolved cause of IS spec v1.17 §1.1,
    both with zero effects and no journal write; a failed verification or append fails the
    fresh run likewise. Capture-to-read identity: under configurations whose STATE_LEDGER cells
    differ, the durable factory's store appends a captured snapshot to the same file (same real path)
    that the `api.resume` handle read and the claim open. By default `harness-inspect` over a root holding
    journals of several tenants lists every canonical journal there, classified per §13.7.1, and enumerates no
    STATE_LEDGER cell (IS spec v1.17 §1.1 witnesses 4 and 5).
16. Ruff and pyright clean on the touched files; the existing resume, claim, journal, durable child
    admission and CLI suites pass.
17. Cutover (spec §I.15, Rule B8): with the root bound and no root file for (tenant, W), a valid
    legacy snapshot journal at `<state_ledger_dir>/pause-journal` yields exit 6 `handle`/`absent`
    before any claim or bootstrap with zero effects; a fresh run of W writes no supersession record;
    the legacy file stays byte-identical and unclaimed. Operator inventory: with the root unbound,
    `harness-inspect` lists every canonical journal in a populated `<ledger dir>/pause-journal`,
    classified per §13.7.1, and its output is byte-unchanged when that directory is absent; with the
    root bound it lists the root by default and the legacy journals under an explicit
    `--pause-journal-dir`. Every file stays byte-identical, nothing is claimed, and a resume of a listed
    legacy workflow refuses as without the inventory. A mutation that disengages the surface on an
    unbound declaration over a populated legacy directory fails a test.
18. Overlap and admission (spec §I.16), cross-process: R1 admitted, R2 admitted and completed, then R1
    captures: `harness resume` claims R1's snapshot once (exit 0); R1 capturing before R2's admission
    gives exit 6 `pause-record-superseded`. A capture that creates the file during an admission gives
    one of those orders. Concurrent daemon `run_workflow` calls each append a record carrying their
    own `run_id`. Mutations that check existence before taking the lock or share one admission object
    between invocations fail a test.

**Dependencies and gates.** Implementation starts only after spec v1.137 and this plan are ratified
and applied. Spec §D.4 proof 5 (a child-refusal `RunResult` stays a child refusal) binds the actual
U-RT-159 interface before the affected 160b candidate is accepted. The accessor change in 160a and its
criterion 14 need the companion OD C-OD-30.5.1 amendment (spec Rule A4) ratified first; its owner is
profile-coder (OD spec v1.43, OD plan v2.37 unit U-OD-62). The journal location (spec Rules B3 and B7)
needs two prerequisites ratified and applied first, with owners named in LIT `cmt-8b76cb48`: the
retained root storage selection and binding evidence (Buford, integration lead) and the C-IS-01
companion (profile-coder; IS spec v1.17 §1.1, IS plan v2.11 unit U-IS-21, whose resolution result
160a's root resolver consumes). Until then no 160a journal
change is accepted and `harness resume` is not exposed; criteria 2 (including case (d)), 15, 17
and 18 then pass on the bound root. Portion 160b's criteria 1–2 need
160a; its value module, parser and criterion 10 can be prepared first.

**Installed witness enabled.** Criterion 2 cases (a)–(c) against the installed CLI, with criterion 1
as the positive control on the same installation (B-310 v4 witness 5 and 1).

**Not delivered here.** Safe resume of engine-native pauses (original B-314 obligation, OPEN); daemon
resume (B-311); HTTP operator surface (B-312, excluded); approval collection (B-315). The spec Rule B7
shared journal root: its storage selection (Buford) and C-IS-01 companion (profile-coder) are
prerequisites this plan consumes.
