# Fork record — operator approval collection at the CLI/Python and daemon-client MCP ingresses

**Class:** 1 (design-substrate amendment), the contract stage (T02) of package P2. Registered gap:
forward-register row B-315 (WO-U17 gap G7, "FORK OWED"). Claim: LIT `arhugula-harness-trial-193`
release `cmt-0299a8f2-dc25-4b9a-80dc-9714dbbdcf3d`, dispatch `cmt-884111b9-4221-4ee8-b1b8-6471e8756302`.
Author claude-coder; independent reviewer profile-reviewer. Grounded at main
`391823f938daa1cef2ea07219f28e00b64641aa7`. `P/` = `harness-runtime/src/harness_runtime/`.
No new H_T primitive, CP palette value, approval store, claim store or HTTP operator service.

## Fork

- **What the contract requires.** An operator can approve, edit, reject, hold or cancel a HITL
  gate through (1) the one-shot `harness run` CLI and `api.run` Python ingress and (2) the
  `harness run --daemon` client's MCP elicitation, with attributable audit outcomes and one root
  admission/resume context. Unattended, invalid, disconnected or timed-out input never authorizes
  a tool or hangs the run. B-315 binding constraints 1–6 apply unchanged.
- **Why current source cannot meet it.**
  - `api.run` answers every elicitation with `decline` (`P/api.py:553-581`, bound at `:607`), so
    every gate becomes REJECT.
  - The daemon client opens `ClientSession(read_stream, write_stream, ...)` with no
    `elicitation_callback` (`P/cli/app.py:333-335`). The SDK default answers with an error, so a
    gate under `--daemon` fails rather than reaching an operator.
  - The server's elicitation offers no hold. `ServerCtxElicitCallback` maps `accept` to the
    four-value palette, `decline` to REJECT and `cancel` to `AskUserQuestionTimeoutError`
    (`P/lifecycle/mcp_backed_ask_user_question_surface.py:286-330`). Composer step 4f turns that
    timeout into the persona degradation mode, whose only reachable disposition is fail-closed
    `HITLGateRejectedError` (`P/lifecycle/hitl_gate_composer.py:2333-2457`). A durable pause is
    raised only for durable-async cells (step 4-bis, `:2273-2433`).
  - `ServerCtxElicitCallback` ignores `timeout` (`:268-273`); a vanished client can leave the
    elicitation waiting.
- **What the existing seams provide.** The elicitation schema `AskUserQuestionElicitationSchema`
  (`response`, `edited_proposal`, `response_text`, `rejection_reason`); composer steps 4f–4i with
  the step-4h audit (`CPAuditLedgerEntry` with response class and hashes, F2 entry
  `actor=step_context.parent_actor`, `:1795-1830`); the escalate-pause sequence and
  `HITLPauseRequestedSignal`; the resumed-step one-shot `HITLDeliveryCell.consume_and_clear()`
  that routes `ResumeContext.hitl_response` through step 4i with audit (`:1906-1935`); one root
  admission for both resumes, `api.resume(resume_handle=..., resume_context=...)` and the daemon
  tool `resume_workflow(workflow_id, resume_context)` (`P/lifecycle/mcp_server.py:626-636`,
  `ResumedEntry` at `:150-161`).

## Contract (proposed Runtime spec delta to C-RT-18 §14.8)

### C1. Operator input value

One runtime value, `OperatorDecision`, is the only thing an ingress produces:

| `action` | Carried fields | Elicitation reply the ingress sends |
|---|---|---|
| `approve` | `response_text` optional | `accept`, `response="approve"` |
| `edit` | `edited_proposal` (JSON object text) required | `accept`, `response="edit"` |
| `reject` | `rejection_reason` optional | `accept`, `response="reject"` |
| `respond` | `response_text` required | `accept`, `response="respond"` |
| `hold` | none | `accept`, `response="hold"` |
| `cancel` | none | `cancel` |
| `refuse` | `rejection_reason` (ingress-generated) | `decline` |

`refuse` is never operator-chosen; an ingress produces it for unattended or invalid input.

### C2. Ingress bindings

- **Python `api.run`.** A keyword-only `operator: OperatorInput | None = None`, an async callable
  `(OperatorRequest) -> OperatorDecision`. `OperatorRequest` carries the server's elicitation
  message and the offered options. `None` keeps today's `decline` exactly (the four existing
  callsites stay byte-identical in behavior). A callable that raises or returns a non-
  `OperatorDecision` yields `refuse` with reason `operator input callback failed: <type name>`.
- **One-shot `harness run` CLI.** Prompts on the controlling TTY only when stdin and stderr are
  both TTYs, writing the prompt to stderr and reading one line. Input grammar:
  `approve`, `reject [reason]`, `edit <JSON object>`, `respond <text>`, `hold`, `cancel`.
  Non-TTY gives `refuse` with reason `noninteractive: no operator terminal`. Any other line gives
  `refuse` with reason `invalid operator input` (no re-prompt). No new CLI flag is needed to enable
  the prompt; the existing non-TTY behavior stays fail-closed.
- **Daemon client `harness run --daemon`.** Binds `ClientSession(..., elicitation_callback=...)`
  to the same TTY reader and grammar, so both CLI ingresses share one parser.

### C3. Server dispositions (runtime-only; the CP four-value palette is unchanged)

| Input reaching the server | Disposition | Effects of the gated step |
|---|---|---|
| `accept approve` | step dispatched (existing 4i APPROVE) | exactly once |
| `accept edit`, valid JSON object | edited payload dispatched (existing 4i EDIT) | once, with the edited payload |
| `accept edit`, undecodable | audited, then `RT-FAIL-HITL-GATE-EDIT-DECODE` (existing) | zero |
| `accept reject` / `decline` | audited, then `RT-FAIL-HITL-GATE-REJECTED` (existing) | zero |
| `accept respond` | existing 4i RESPOND | per existing RESPOND |
| `accept hold`, durable pause bound | escalate-pause sequence, run ends PAUSED with resume handle, no step-4h audit (§14.8.8.6) | zero until resumed |
| `accept hold`, no durable pause binding | audited REJECT with reason `hold unavailable: no durable pause binding` | zero |
| `cancel` | existing timeout path: degradation mode, fail-closed `RT-FAIL-HITL-GATE-REJECTED` | zero |
| `accept` with a response outside C1 | `MCPSurfaceCallbackNotBoundError` (existing) | zero |
| no reply by `placement.timeout` (or client disconnect) | `AskUserQuestionTimeoutError`, then as `cancel` | zero |

`hold` is parsed by `ServerCtxElicitCallback` before palette validation and surfaced to the
composer as a typed hold request; it never becomes an `HITLResponse` member.
The server bounds `ctx.elicit` by `placement.timeout` when set. A client disconnect must end the
wait; see open fork F3 for the unset-timeout case.

### C4. Resume of a held gate (single pass-through context)

Resume uses only the existing root admissions: `harness resume <workflow manifest>` (its workflow_id is the handle) / `api.resume(
resume_handle=..., resume_context=ResumeContext(hitl_response=HITLResult(...)))`, or the daemon
tool `resume_workflow(workflow_id, resume_context={...})`. The CLI `resume` command gains
`--hitl-response <approve|reject|edit|respond>` with `--edited-proposal`, `--response-text` and
`--rejection-reason`, building exactly one `ResumeContext`. No pause-snapshot path is accepted from
an operator surface (B-315 constraint 3), and nothing stores the decision outside the existing
resume claim and journal (constraint 5). The resumed step consumes it once through step 0.

### C5. Attribution

The step-4h audit keeps `actor=step_context.parent_actor`, the principal that launched the run
(for the solo-developer persona, the operator who answers). Each ingress additionally records
`hitl.response.ingress` on the `hitl.invocation.responded` span, one of `python`, `cli-tty`,
`daemon-client-tty`, `unattended`. Refusal reasons in C2/C3 are literal, so the audited
`rejection_reason_hash` discriminates operator rejection from ingress refusal.

## Literal assertions for T03

Each runs through the public ingress (in-process `api.run` / `harness run`, and a real daemon over
its Unix socket for the `--daemon` rows), with a fixture workflow whose gated step writes one
marker file. "Zero effects" means the marker is absent and the ledger has no dispatch entry for
the gated step.

1. `api.run` with `operator` returning `approve`: result SUCCEEDED, marker written once, audit
   response `approve`.
2. `api.run` with `edit` and `{"k": "edited"}`: marker content comes from the edited payload; the
   audit's `edited_proposal_hash` is the hash of the decoded payload.
3. `api.run` with `reject "no"`: `RT-FAIL-HITL-GATE-REJECTED`, zero effects, audit `reject`.
4. `api.run` with `operator=None`: same as 3 but reason `operator declined elicitation` (current
   behavior preserved).
5. `api.run` with a callback that raises: refuse, zero effects, reason names the exception type.
6. `harness run` with stdin not a TTY: no prompt, exit code for REJECTED, zero effects, finishes
   within the fixture's bound (no hang).
7. `harness run` on a pseudo-TTY, input `approve`: exit 0 and marker written; input `bogus`: refuse
   with `invalid operator input`, zero effects.
8. `harness run --daemon` on a pseudo-TTY, input `approve`: daemon run SUCCEEDED, marker written;
   input `reject`: REJECTED, zero effects. Same daemon, both runs, no restart.
9. `hold` with the durable pause bound, on each ingress: exit 5 (PAUSED) with a resume handle,
   zero effects; then one resume with `--hitl-response approve` writes the marker once.
10. `hold` without the durable pause binding: audited REJECT with reason
    `hold unavailable: no durable pause binding`, zero effects.
11. A second resume of the same handle after 10's successful resume is refused by the existing
    root claim refusal class, and the marker is still written once.
12. `cancel` on each ingress: fail-closed REJECTED, zero effects.
13. Daemon client killed while the prompt is open: the daemon's run ends REJECTED (timeout path)
    within the placement timeout, zero effects, and the daemon still serves a following run.
14. Existing workflow-layer pause/resume, root-claim and HITL composer regressions stay green.

## Open forks for reviewer judgment and Buford ratification

- **F1 hold mapping.** Recommended above: `hold` as a surface value mapped onto the existing
  escalate-pause sequence. Alternative: no sync hold (hold only where step 4-bis already pauses),
  which leaves solo sync gates without a hold. Recommendation: the mapping.
- **F2 attribution.** Recommended: launching principal plus the ingress span attribute. A per-human
  responder field would change the CP audit schema; recommended out of scope for the solo persona.
- **F3 unset timeout.** When `placement.timeout` is None and the SDK does not end `ctx.elicit` on
  client disconnect, the server can wait forever. Recommended: T03 first witnesses the SDK
  behavior (assertion 13 with no placement timeout); if it hangs, bind the wait to the daemon
  session's lifetime, adding no new configurable default.
- **F4 prompt content.** The server's message is `HITL gate at <position>` and does not show the
  proposed action. Recommended: out of T03 scope, registered as a follow-up; the operator decides
  from the run's own context.
- **F5 inherited-gate refusal (A4).** B-315 names A4 for the inherited-gate refusal. This contract
  changes no inherited-gate rule, so it needs nothing from A4. Child-workflow gates are excluded
  from T03 assertions.

## Disposition (on ratification)

The C1–C5 contract becomes the next free Runtime spec version's §14.8 amendment to C-RT-18, with
one plan unit for T03 carrying assertions 1–14, materialized in P2 before T03 claims conformance.
No source or test change is made by this stage.
