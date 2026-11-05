# Spec: Harness Runtime — v1.141 (delta over v1.140)

*Delta-only file. One contract added: the daemon MCP resume operation (B-311), C-RT-35 resume through
the daemon's MCP server. It defines the request, its binding to the C-RT-35 durable admission and the
per-invocation resume binding. The refusal reply is v1.137 §D.2, adopted unchanged. Every other v1.140
and earlier term remains in force.*

**Status: CLEARED 2026-11-05 — ratified by the integration lead at LIT `cmt-1a94786f-b490-4013-afc3-1131aaebdaf9`
on the frozen reviewed body `903cbdd414c26e789dfd85f3cb582bad164c4228` (independent contract GREEN
`cmt-5f7251b4-f79f-4c0e-b221-192d5544bd39`); clearance `.harness/clearance/spec-harness-runtime-v1-141-cleared-2026-11-05.md`.
Contract clearance only; source conformance, CI, landing and installed acceptance remain owed.**

**Filed:** 2026-11-05

**Authority:** forward-register row B-311 and its close-out constraints (1)–(6); the accepted release
campaign's B-312 decision (CLI and MCP operator surfaces; HTTP only as MCP transport); LIT
`arhugula-harness-trial-193` claim `cmt-4d8031bc-4eff-4b26-87cb-488f148f319c`. Fork:
`.harness/class_1_fork_daemon_mcp_resume.md`.

**Predecessor:** `Spec_Harness_Runtime_v1_140.md` (cleared head). v1.140 amends C-RT-17 §14.7.2 only,
so no site overlaps. **Builds on:** v1.137 §B (fresh-run supersession), §C (refusal battery), §D (closed
refusal value and its MCP reply) and Rule B7 (the single pause-journal root).

`P` = `harness-runtime/src/harness_runtime`. Line cites are at harness `f40991fc`.

## §0 Change-note (v1.140 → v1.141)

| Site | Before | After |
|---|---|---|
| Daemon MCP server tools | One tool, `run_workflow(workflow_id)` (`P/lifecycle/mcp_server.py:296`) | Adds `resume_workflow(workflow_id, resume_context)` (§1) |
| C-RT-35 resume admission | Inline in `api.resume`: exactly-one-of, protocol, durable opt-in, durable read, depth, `DurableRootResume`, workflow match, step range and, under `_run_lock`, staleness (`P/api.py:1385-1525`) | `api.resume` parses its two optional inputs into one typed source; one admission unit both surfaces call does the rest (§2) |
| Resume state into the body | Three `_state` keys on the MCP server: `_resume_pause_snapshot`, `_resume_context`, `_resume_admission` (`P/api.py:1549-1570`) | One typed root entry passed to the body per invocation (§3) |
| Daemon resume reply | Not defined (v1.137 §D.2 defines its refusal reply only) | §D.2 refusal reply; existing RunResult representation otherwise (§4) |

## §1 Request

1. **Tool.** The daemon's MCP server registers a second tool, `resume_workflow`, beside `run_workflow`.
   Its input schema has exactly two properties:
   - `workflow_id: str` (required): resolved to a `WorkflowObject` by the same unit `run_workflow` uses,
     the resolution block at `P/lifecycle/mcp_server.py:345-365` with its discriminator
     `_looks_like_manifest_path` (`:85`). A daemon client passes the manifest path, as for `run_workflow`.
   - `resume_context: object | null` (optional, default `null`): parsed once at the tool boundary into the
     closed two-variant `ResumeContext`: the accessor-derived variant
     (`harness_cp.pause_state_projection.AccessorDerivedResumeContext`) when the object carries
     `pause_state`, the legacy base variant (`harness_cp.pause_resume_protocol_types.ResumeContext`)
     otherwise. Both are `extra="forbid"`, so at most one variant accepts a given object; parsing as the
     base variant alone would refuse every accessor-derived context and make the §30 staleness fence
     unreachable from the daemon.
2. **Handle.** `resume_handle = workflow.workflow_id` of the resolved workflow, as for `harness resume`
   (v1.137 §E). There is no separate handle argument.
3. **Not accepted.** No `pause_snapshot`, snapshot path, snapshot body, run ID, operation ID, tenant,
   claim token, journal location or approval record. The tenant is the daemon's bootstrap
   `RuntimeConfig.tenant_id`; the journal is the Rule B7 root that config resolves.
4. **No surface state.** The tool adds no claim, lease, journal, idempotency store, operation ID or
   approval store, and performs no journal read outside the §2 admission. It does not construct,
   collect, persist or interpret approvals; a supplied `resume_context` is passed through once (§3).
   How an operator obtains an approval stays with B-315.

## §2 One admission unit

1. **Typed source.** A root resume source is either a durable handle or a caller-supplied snapshot,
   never both and never neither. `api.resume` parses its two optional keyword inputs into that source
   with the existing exactly-one-of check and its `ResumeArgsError`. The daemon constructs the durable
   handle source directly (§1.2) and never a snapshot source.
2. **Extraction.** The remaining pre-body half of `api.resume` becomes one asynchronous unit, here
   called `admit_root_resume(workflow, source, resume_context, config)`, returning a resumed root
   entry (§3) or raising the existing typed exception. It performs, in the existing relative order: the
   protocol-bound check (Rule B7 item 3); for a handle source, the durable opt-in check
   (`ResumeArgsError`), the durable read with its `superseded`, unknown-handle and direct-child-depth
   refusals, and `DurableRootResume` construction over the read record; workflow match; step-index
   range; and last the §30 pause-state staleness precondition (`P/api.py:882`), which keeps its own
   off-loop journal read.
3. **Single enforcer.** `api.resume` and `resume_workflow` both call this unit. Neither surface
   re-implements any of its checks. The claim itself stays where it is: `DurableRootResume` claims the
   record in `ResumeClaimStore` when the body is admitted, before any body effect.
4. **What stays outside it.** `api.resume` keeps, in order, its drain check, invalid-workflow check,
   the source parse (§2.1), the `ConcurrentRunNotSupported` guard, then acquires `_run_lock` and calls
   the unit inside it, followed by its per-call bootstrap and shutdown (Track A is bootstrap-per-call).
   The guard still precedes every journal read, so the existing guard-before-read witness
   (`test_api_resume_handle_concurrency_guard_precedes_store_read`) holds. One ordering edge changes:
   with another call holding `_run_lock`, a call whose config lacks the pause protocol now raises
   `ConcurrentRunNotSupported` where it raised `ResumeProtocolNotBoundError`. Neither reaches a journal
   read or a body. The daemon reuses its one bootstrap context, calls the unit with that context's
   `RuntimeConfig`, takes no process lock and keeps the drain behavior `run_workflow` has.
5. **Daemon serialization.** In the daemon, concurrent requests serialize at the journal, not at a
   process lock. The fresh-run root admission appends its supersession record under the journal lock
   (v1.137 Rules B1, B2; at `f40991fc` the store's `supersede` writer exists but no fresh run calls it,
   so this binds when that admission is applied), and the claim refuses a record that is no longer the latest or is already
   claimed. A record that changes between the admission read, the staleness read and the claim is
   refused at the claim; it is never resumed. In `api.resume` `_run_lock` additionally keeps this
   process from writing the journal during the unit; the daemon relies on the claim alone, which is the
   enforcer in both surfaces.
6. **Daemon input.** The snapshot source remains a Python-API-only input; no operator surface can
   construct it.

## §3 Per-invocation root entry

1. **Type.** The body receives one value, the root entry: either a fresh entry (new `run_id`,
   `UNCLAIMED` admission, no snapshot, no resume context) or a resumed entry (the snapshot, its
   `run_id`, the admission from §2 and the parsed `resume_context`). Illegal mixes, such as a snapshot
   with a fresh `run_id` or a `DurableRootResume` admission without a snapshot, are not representable.
2. **Daemon binding.** `resume_workflow` constructs its resumed entry inside its own invocation and
   passes it to the shared body as an argument. It writes no resume state to the server's `_state`, and
   `run_workflow` in the daemon always constructs a fresh entry. A concurrent `run_workflow` therefore
   cannot observe another request's snapshot, admission or resume context.
3. **Track A binding.** `api.resume` bootstraps its own MCP server per call and holds `_run_lock`, so no
   concurrent request shares that server. It hands its resumed entry to the in-process `run_workflow`
   call as one `_state` value that replaces the three keys, removed in its `finally`. The body reads the
   entry once on entry, as today (`P/lifecycle/mcp_server.py` ~376-392).
4. **Once.** The body passes the entry's `resume_context` to the depth-0
   `execute_workflow(resume_context=...)` exactly once and keeps the snapshot's `run_id`. It creates no
   operation ID.

## §4 Reply

1. **Refusal.** A recognized refusal raised by §2, or by the `DurableRootResume` claim at body
   admission, produces the v1.137 §D.2 reply: `isError: true` and exactly one text item holding the
   closed refusal object, projected by the existing value module (`P/resume_refusal.py`, `project` and
   `to_json`). The tool handler catches the typed exception in the same invocation. It never parses
   text and never relabels an argument, handle, depth or validation error as a claim refusal.
2. **Malformed `resume_context`.** An object that neither `ResumeContext` variant accepts is a caller
   argument error, raised as `ResumeArgsError` and replied with the `arguments` arm
   (`RT-FAIL-RESUME-ARGS`) before any journal read. A value that is not a JSON object or null fails the
   tool's published input schema in the MCP layer; that is an unrecognized tool failure under §D.2, not
   a refusal arm.
3. **Reachable arms.** On the daemon, the `ResumeWorkflowMismatchError` arm stays unreachable (handle
   equals the resolved workflow's ID), as for `harness resume`. `ResumePauseStateStaleError` is
   reachable when a `resume_context` is supplied. All other §D.1/§D.5 arms are reachable.
4. **Non-refusal.** A completed, paused, failed or drained resumed run returns the existing RunResult
   representation: the control-plane `RunResult` JSON object `run_workflow` returns
   (`model_dump(mode="json")`), including its drained form. A child refusal inside a RunResult stays
   a child refusal (§D.2).
5. **Other failures.** Manifest load failures, invalid workflow, drain, bootstrap and unrelated errors
   keep their existing tool-error behavior and are never encoded as refusal objects. A lost or malformed
   reply never authorizes an automatic second resume (§D.2).

## §5 Unchanged and not closed

- Rule B7 item 4 applies to this operation unchanged: no implementation of `resume_workflow` is accepted
  and the tool is not exposed on a served daemon until the Rule B7 root storage selection and binding
  evidence are ratified and applied. Isolated source and test preparation may proceed.
- No CLI daemon-client route for resume is added; `harness resume` keeps `--daemon` excluded (v1.137
  §E). Any MCP client reaches `resume_workflow` over the daemon's existing transport. HTTP remains only
  the MCP transport (B-312 excluded).
- B-315 (approval collection), the original B-314 engine-native resume obligation and A4's child
  refusal carrier are not defined here.
- `run_workflow`'s request, reply and fresh-run admission are unchanged.

## §6 Required discriminating witnesses (after application)

| ID | Behavior | Mutant it kills |
|---|---|---|
| W1 | A daemon `resume_workflow` and a concurrent `run_workflow` of a different workflow, forced to overlap after the resume's admission: the fresh run has a new `run_id`, `UNCLAIMED` admission and no resume context; the resume keeps the snapshot's `run_id` | Resume state bound through shared server state |
| W2 | Two concurrent `resume_workflow` calls for one handle: exactly one body runs; the other returns the `claim` arm reply with zero model, tool or body effects | A per-surface claim, or no claim at the daemon |
| W3 | A fresh run of the same workflow appends its supersession record between a resume's admission read and its claim: the resume is refused at the claim and no body runs | Admission that trusts the read without the claim |
| W4 | Each reachable arm round-trips through the real tool reply and the strict `parse`; the unreachable mismatch arm keeps its adapter mapping test; missing `isError`, a prefix or suffix, or a second content item is refused by the decoder | Prose inference, lost arm, or kind/fail_class drift at the daemon |
| W5 | The tool's published input schema has exactly `workflow_id` and `resume_context`; path, secret and tenant canaries in exceptions never appear in a reply | Snapshot path or internal detail exposed |
| W6 | A supplied legacy and a supplied accessor-derived `resume_context` each reach the depth-0 `execute_workflow` exactly once as their own variant; a stale accessor-derived one returns the `pause-state-stale` arm; an object neither variant accepts returns the `arguments` arm with zero journal reads | Double delivery, a downgraded variant that skips the fence, or a malformed context reaching the read |
| W7 | A resumed run's completed and paused replies equal the `run_workflow` RunResult serialization | A wrapper or replacement result type |
| W8 | `api.resume`'s existing tests pass unchanged after the extraction, including the guard-before-read witness; the only changed ordering edge is §2.4's; the three `_state` resume keys no longer exist | A second admission path left behind |
