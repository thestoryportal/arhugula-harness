# Fork record — daemon MCP resume through the shared root admission

**Class:** 1 (design-substrate amendment), absorbed through a documented back-flow source arc
(CLAUDE.md §11.4). Registered gap: forward-register row B-311 (WO-U17 gap G2). Under the accepted
release campaign the recovery contracts B-310/311/313/314/315 are drafted concurrently and ratified
before implementation claims conformance. Claim: LIT `arhugula-harness-trial-193`
`cmt-4d8031bc-4eff-4b26-87cb-488f148f319c`. No new H_T primitive or cross-axis edge.

## Fork

- **What the contract requires.** The accepted operator surfaces are CLI and MCP (B-312 excludes a
  separate HTTP surface; HTTP stays the MCP transport). An MCP client of the daemon must be able to
  resume a durable workflow-layer pause through the same admission `api.resume` uses, ending in the
  `DurableRootResume` claim, with no per-surface claim, journal, operation ID or approval store
  (B-311 constraints 1–6). Its refusal reply is already fixed by Runtime spec v1.137 §D.2.
- **Why current source cannot meet it.** The daemon registers one tool, `run_workflow(workflow_id)`
  (`P/lifecycle/mcp_server.py:296`). `api.resume` hands resume state to that tool through three keys
  on the server's process-wide `_state` dict (`P/api.py:1549-1570`). That handoff is safe only because
  Track A bootstraps one server per call under `_run_lock`; in the daemon a concurrent `run_workflow`
  would read another request's snapshot, admission or resume context. No MCP request can carry a resume.
- **What the existing seams provide.** The C-RT-35 admission sequence in `api.resume`, the
  `DurableRootResume` claim in `ResumeClaimStore`, the closed refusal value with its strict parser
  (`P/resume_refusal.py`), the daemon's workflow resolution block and the per-invocation ContextVar
  isolation already used for the tool ctx.

## Disposition

- Runtime spec **v1.141** (CLEARED 2026-11-05; amends no site v1.138–v1.140 amends):
  - a second daemon tool `resume_workflow(workflow_id, resume_context)`; the handle is the resolved
    workflow's ID, and `resume_context` parses into the closed two-variant `ResumeContext`;
  - the pre-body admission extracted into one unit both `api.resume` and the daemon call, over a typed
    root resume source; one stated ordering edge changes in `api.resume`;
  - one typed per-invocation root entry replacing the three `_state` resume keys;
  - the v1.137 §D.2 refusal reply adopted unchanged; non-refusal replies keep the control-plane
    `RunResult` JSON `run_workflow` returns.
- Plan **v2.69** adds U-RT-161 with witnesses W1–W8.
- No source, test or operator-guide change is made by this arc.

## Open

- Spec v1.137 Rule B7 item 4 holds U-RT-161 acceptance and daemon exposure until the Rule B7 root
  storage selection and binding evidence (owner Buford, LIT `cmt-8b76cb48`) are ratified and applied.
- Witness W3 needs the v1.137 Rules B1/B2 fresh-run supersession append applied; at `f40991fc` the
  store's `supersede` writer has no caller.
- A CLI daemon-client resume route, B-315 approval collection, the original B-314 engine-native resume
  obligation and A4's child refusal carrier are not defined.

## Clearance

Cleared 2026-11-05: independent GREEN pass 1 `cmt-5f7251b4-f79f-4c0e-b221-192d5544bd39` and integration-lead ratification
`cmt-1a94786f-b490-4013-afc3-1131aaebdaf9` on frozen `903cbdd414c26e789dfd85f3cb582bad164c4228`. Markers
`.harness/clearance/spec-harness-runtime-v1-141-cleared-2026-11-05.md` and
`.harness/clearance/implementation-plan-harness-runtime-v2-69-cleared-2026-11-05.md`. An integration
collision check of the v1.141/v2.69 numbers and the U-RT-161 unit ID remains owed at landing.
