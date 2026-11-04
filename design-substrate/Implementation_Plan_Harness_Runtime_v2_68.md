# Implementation Plan: Harness Runtime — v2.68 (PROPOSED delta over cleared v2.65)

**Status: PROPOSED — not cleared.** Grounded on cleared v2.65 (A3, U-RT-157;
`.harness/clearance/implementation-plan-harness-runtime-v2-65-cleared-2026-10-04.md`); implements
proposed Runtime spec v1.137. Plans v2.66 (A5, U-RT-158) and v2.67 (A4, U-RT-159) are separately
PROPOSED and not cleared. Fold order is A3 → A5 → A4 → this delta, so this unit is U-RT-160; a unit-ID
collision recheck is owed at landing. Spec v1.137 amends no site that v1.135 or v1.136 amends.
Authority: `.harness/runtime-resume-contract-authority.md`. Fork:
`.harness/class_1_fork_runtime_resume_cli_supersession.md`. This is a proposed contract, not
clearance, ratification or a product release.

## U-RT-160 — superseded-record refusal and `harness resume` (B-314 prerequisite, B-313, B-310)

`P` = `harness-runtime/src/harness_runtime`.

**Source, portion 160a (Runtime prerequisite, spec v1.137 §A–§D, §G):**
`P/lifecycle/journal_workflow_pause_store.py` (supersession record kind beside the snapshot record;
appended only through `_append`; `read_latest_attributed` returns `superseded`; `read_latest` and
`read_exact` return `None` at a supersession position);
`P/lifecycle/root_resume_admission.py` (the Runtime-owned fresh-run admission that replaces
`UNCLAIMED` for depth-0 fresh runs and appends the supersession record before `body(None)`);
`P/mcp_server.py` (binds that admission as the `run_workflow` default, so `api.run` and daemon clients
share it);
`P/api.py` (`ResumePauseRecordSupersededError`, raised from the handle read where a `None` snapshot
raises `ResumeHandleUnknownError`, before depth).

**Source, portion 160b (CLI, spec v1.137 §D–§F):**
one Runtime-owned module for the closed `harness.resume-refusal.v1` value (B-313 v2 plus the ninth
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
3. Race (spec §I.3), cross-process: a supersession record appended between the handle read and the
   claim yields exit 7 `claim`, reason `claim-refused`; the record stays unclaimed; zero body effects.
4. No prior file (spec §I.4): a bare engine-native pause yields exit 6 `handle`/`absent`, and the
   fresh run writes no supersession record.
5. Wrong tenant (spec §I.5) is indistinguishable from absent in exit, value and output.
6. Opt-in gap (spec §I.6): the later run in criterion 2 has no durable opt-in and still supersedes.
7. Readers (spec §I.7): `read_latest` returns `None` at a supersession record; child admission at a
   supersession position refuses `UNREADABLE_RECORD`; a legacy journal without `kind` reads
   unchanged; a `kind` line with an unknown value or extra/missing fields reads `corrupt-latest`.
8. Refusal mapping (spec §I.8; B-313 v2 proof 1–3, 6 at the CLI-reachable inputs): each reachable
   arm keeps its kind, fail_class, typed facts and exit; a config that loads without the pause
   protocol exits 6 `protocol-not-bound`, a genuine config-file load error keeps exit 3; the strict
   parser refuses malformed JSON, extra or missing fields, quoted booleans, unknown discriminators and
   mixed arms; path, secret and tenant canaries never appear in output. The two arms the CLI cannot
   reach (`workflow-mismatch`, `pause-state-stale`) are tested at the projection, not claimed as live
   CLI witnesses.
9. Mutations that must fail a test: moving any arm to another kind, fail_class or exit; reporting
   `superseded` as a `handle` cause, as `claim` or as `corrupt-latest`; writing the supersession
   record only when the durable opt-in is present; writing it from a resumed or child run; writing it
   after the first step; dropping the record-count or digest change from the staleness token.
10. Request shape (spec §I.10): the subcommand accepts no snapshot, context, daemon or model-override
    input, calls `api.resume` exactly once with `resume_handle == workflow.workflow_id` and
    `resume_context is None`, and performs no journal read, claim, lease or store of its own.
11. HITL probe (spec §I.11): a HITL-gated durable pause resumed by the CLI records the exit, whether
    the gate re-fired, webhook delivery count, claim state and the new journal record. The result
    decides whether a Runtime-side refusal is needed before acceptance; no approval is recorded.
12. Child workflow_id (spec §I.9): pin whether a child run can share its root's workflow_id; child
    runs write no supersession record.
13. Operator guide (spec §I.12): the guide and its pinned test list exits 6 and 7 with their
    meanings; the code-5 row states no safe resume for engine-native pauses.
14. Ruff and pyright clean on the touched files; the existing resume, claim, journal, durable child
    admission and CLI suites pass.

**Dependencies and gates.** Implementation starts only after spec v1.137 and this plan are ratified
and applied. B-313 v2 proof 5 (a child-refusal `RunResult` stays a child refusal) binds the actual
U-RT-159 interface before the affected 160b candidate is accepted. Portion 160b's criteria 1–2 need
160a; its value module, parser and criterion 10 can be prepared first.

**Installed witness enabled.** Criterion 2 cases (a)–(c) against the installed CLI, with criterion 1
as the positive control on the same installation (B-310 v4 witness 5 and 1).

**Not delivered here.** Safe resume of engine-native pauses (original B-314 obligation, OPEN); daemon
resume (B-311); HTTP operator surface (B-312, excluded); approval collection (B-315). The visibility
bound in spec Rule B6 is a named residual, not a gap this unit closes.
