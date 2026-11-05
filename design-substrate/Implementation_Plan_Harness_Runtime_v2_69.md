# Implementation Plan: Harness Runtime — v2.69 (delta over v2.68)

**Status: PROPOSED.** Not cleared. Implements Runtime spec v1.141 (PROPOSED). Independent review,
integration-lead ratification and a clearance marker are owed before any source claims conformance.
Grounded on v2.68 (U-RT-160, cleared); plans v2.66 (A5, U-RT-158) and v2.67 (A4, U-RT-159) stay
separately PROPOSED. This unit is U-RT-161; a unit-ID collision recheck is owed at landing. Spec v1.141
amends no site v1.138, v1.139 or v1.140 amends. Fork: `.harness/class_1_fork_daemon_mcp_resume.md`.
Authority: forward-register row B-311 and LIT `arhugula-harness-trial-193` claim `cmt-4d8031bc`.

## U-RT-161 — daemon MCP resume through the shared root admission (B-311)

`P` = `harness-runtime/src/harness_runtime`. Line cites are at harness `f40991fc`.

**Source:**
`P/api.py` (the exactly-one-of parse into the typed root resume source; the remaining pre-body checks
of `resume` (`:1395-1525`) move into one asynchronous `admit_root_resume` that returns the resumed root
entry, spec §2.1–§2.2; `resume` calls it inside `_run_lock` after the `ConcurrentRunNotSupported`
guard, spec §2.4; its three `_state` resume keys (`:1549-1551`, popped `:1568-1570`) become one root
entry value, spec §3.3; the post-call `admission.refusal` recovery is unchanged);
`P/lifecycle/mcp_server.py` (the root entry type, spec §3.1; the tool body becomes one shared function
taking `(workflow, entry, ctx)`; `run_workflow` builds a fresh entry, or reads the Track A entry from
`_state` once on entry where it now reads three keys (`:376-388`); a second tool `resume_workflow`
with exactly `workflow_id` and `resume_context`, spec §1, which resolves the workflow through the same
block as `run_workflow` (`:345-365`), parses `resume_context` into the closed two-variant type, calls
`admit_root_resume` with the daemon context's `RuntimeConfig`, and runs the shared body with its
resumed entry; spec §4 reply mapping);
`P/resume_refusal.py` (no new arm or field: the handler uses the existing `project` and `to_json`, and
the witnesses decode with the existing strict `parse`).
No CLI, admin CLI, HTTP or approval-store change.

**Acceptance criteria:**
1. W1 (spec §6): a daemon `resume_workflow` and a concurrent `run_workflow` of a different workflow,
   forced to overlap after the resume's admission. The fresh run has a new `run_id`, the `UNCLAIMED`
   admission and no resume context; the resume keeps the snapshot's `run_id`. Fails if resume state
   travels through server `_state`.
2. W2: two concurrent `resume_workflow` calls for one handle. Exactly one body runs; the other returns
   the `claim` arm reply with zero model, tool or body effects.
3. W3: a fresh run of the same workflow appends its supersession record between a resume's admission
   read and its claim. The resume is refused at the claim and no body runs.
4. W4: each reachable arm (spec §4.3) round-trips through the real tool reply and the strict `parse`;
   the unreachable `workflow-mismatch` arm keeps its adapter mapping test; a reply missing `isError`,
   with a prefix or suffix, or with a second content item is refused by the decoder.
5. W5: the published input schema of `resume_workflow` has exactly `workflow_id` and
   `resume_context`; path, secret and tenant canaries placed in raised exceptions never appear in a
   reply.
6. W6: a legacy and an accessor-derived `resume_context` each reach the depth-0
   `execute_workflow` exactly once as their own variant; a stale accessor-derived one returns the
   `pause-state-stale` arm; an object neither variant accepts returns the `arguments` arm with zero
   journal reads.
7. W7: a resumed run's completed and paused replies equal the `run_workflow` control-plane `RunResult`
   JSON for the same outcome.
8. W8: the existing `api.resume` tests pass unchanged, including
   `test_api_resume_handle_concurrency_guard_precedes_store_read`; one new test pins spec §2.4's
   changed edge (lock held, pause protocol unbound → `ConcurrentRunNotSupported`); no `_state` key
   named `_resume_pause_snapshot`, `_resume_context` or `_resume_admission` remains.

**Tests:** `harness-runtime/tests/test_daemon_mcp_resume.py` (new; criteria 1–7 against a real
in-process daemon `HarnessMCPServer` with fake providers, temporary-root journals and forced
interleavings, no sleeps); `harness-runtime/tests/integration/test_r_cc_1_api_resume.py` (criterion 8's
new edge test beside the existing guard-before-read witness).

**Dependencies and gates.** Implementation starts only after spec v1.141 and this plan are ratified.
Spec v1.137 Rule B7 item 4 applies unchanged: isolated source and provider-free temporary-root tests may
be prepared, but no U-RT-161 implementation is accepted and `resume_workflow` is not exposed on a served
daemon until the Rule B7 root storage selection and binding evidence (Buford, integration lead, LIT
`cmt-8b76cb48`) are ratified and applied. Criterion 3 needs the v1.137 Rules B1/B2 fresh-run admission
(supersession append under the journal lock) applied: at `f40991fc` the store's `supersede` writer
exists but no fresh run calls it. Until then criterion 3 is prepared against that admission and is not
counted as passing. Criteria 1, 2 and 4–8 need nothing beyond `f40991fc`.

**Installed witness enabled.** Against the installed daemon on the bound Rule B7 root: a durable
workflow-layer pause resumed once through `resume_workflow` (original `run_id`, one `started` claim),
and a second call returning the `claim` arm reply with zero new effects.

**Not delivered here.** A CLI daemon-client route for resume (v1.137 §E keeps `--daemon` excluded);
HTTP operator surface (B-312, excluded); approval collection (B-315); the original B-314 engine-native
resume obligation; A4's child refusal carrier.
