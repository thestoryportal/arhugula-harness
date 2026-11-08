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

One runtime value, `OperatorDecision`, is the only thing an ingress produces. Every decision from
a harness ingress is sent as an elicitation `accept` whose data also carries `ingress` (C5):

| `action` | Carried fields | `response` in the `accept` data |
|---|---|---|
| `approve` | `response_text` optional | `"approve"` |
| `edit` | `edited_proposal` (JSON object text) required | `"edit"` |
| `reject` | `rejection_reason` optional | `"reject"` |
| `respond` | `response_text` required | `"respond"` |
| `hold` | none | `"hold"` |
| `cancel` | none | `"cancel"` |
| `refuse` | `rejection_reason` (ingress-generated literal) required | `"refuse"` |

`refuse` is never operator-chosen; an ingress produces it for unattended or invalid input. The
schema `AskUserQuestionElicitationSchema` gains `ingress` (optional str); `hold`, `cancel` and
`refuse` are surface values parsed by `ServerCtxElicitCallback` before palette validation and never
become `HITLResponse` members. MCP-native `decline` and `cancel` from other clients (Claude Code)
keep their current mapping.

### C1a. Decision-relevant request

The server's elicitation message stops being only `HITL gate at <position>`
(`P/lifecycle/hitl_gate_composer.py:2329-2332`). It is the deterministic text:

```
HITL gate at <placement.position>
step: <step.step_id> (<step.step_kind>)
payload sha256: <hex of post_mutation_payload_hash(step.step_payload)>
payload: <canonical JSON of step.step_payload, sort_keys, compact>
```

When the canonical payload exceeds 8192 bytes the `payload:` line carries the first 8192 bytes
followed by `… (truncated; <n> bytes total)`; the hash line always covers the whole payload.
`OperatorRequest` (Python) carries the same fields structurally: `position`, `step_id`,
`step_kind`, `payload` (the full mapping), `payload_sha256`, `options`, `message`. Both TTY
ingresses print the whole message to stderr before reading any answer.

### C2. Ingress bindings

- **Python `api.run`.** A keyword-only `operator: OperatorInput | None = None`, an async callable
  `(OperatorRequest) -> OperatorDecision` (C1a). `None` yields `refuse` with reason
  `unattended: no operator input bound` and ingress `unattended`; the outcome for the four existing
  callsites is unchanged (REJECTED, zero effects) and only the recorded reason changes from
  `operator declined elicitation`. A callable that raises or returns a non-`OperatorDecision`
  yields `refuse` with reason `operator input callback failed: <type name>`, ingress `python`.
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
| `accept reject` / MCP-native `decline` | audited, then `RT-FAIL-HITL-GATE-REJECTED` (existing) | zero |
| `accept refuse` with `rejection_reason` | audited as response `reject` with that exact `rejection_reason` (never approval), then `RT-FAIL-HITL-GATE-REJECTED` | zero |
| `accept refuse` without `rejection_reason` | as `accept` outside C1 below | zero |
| `accept respond` | existing 4i RESPOND | per existing RESPOND |
| `accept hold`, durable pause bound | escalate-pause sequence, run ends PAUSED with resume handle, no step-4h audit (§14.8.8.6) | zero until resumed |
| `accept hold`, no durable pause binding | audited REJECT with reason `hold unavailable: no durable pause binding` | zero |
| `accept cancel` / MCP-native `cancel` | existing timeout path: degradation mode, fail-closed `RT-FAIL-HITL-GATE-REJECTED` | zero |
| `accept` with a response or `ingress` outside C1/C5 | `MCPSurfaceCallbackNotBoundError` (existing) | zero |
| no reply by the elicitation deadline (C3a) | `AskUserQuestionTimeoutError`, then as `cancel` | zero |

`hold` is surfaced to the composer as a typed hold request.

### C3a. Bounded wait (every ingress, timeout set or unset)

`ServerCtxElicitCallback` awaits `ctx.elicit` under `asyncio.wait_for` with the elicitation
deadline `placement.timeout` when set, otherwise the fixed contract constant
`OPERATOR_ELICITATION_DEADLINE_SECONDS = 900`. The constant is not configurable in T03. Expiry
raises `TimeoutError`, which `MCPBackedAskUserQuestionSurface.ask` already maps to
`AskUserQuestionTimeoutError`, so a vanished, killed or silent client ends the run fail-closed,
with zero effects, no later than the deadline, whatever the SDK does on disconnect. The in-process
`api.run` path and both TTY readers are under the same server deadline. A transport error raised by
`ctx.elicit` (closed session) is mapped the same way. Earlier termination on session closure is
permitted but not promised.

### C4. Resume of a held gate (single pass-through context)

Resume uses only the existing root admissions: `harness resume <workflow manifest>` (its workflow_id is the handle) / `api.resume(
resume_handle=..., resume_context=ResumeContext(hitl_response=HITLResult(...)))`, or the daemon
tool `resume_workflow(workflow_id, resume_context={...})`. The CLI `resume` command gains
`--hitl-response <approve|reject|edit|respond>` with `--edited-proposal`, `--response-text` and
`--rejection-reason`, building exactly one `ResumeContext`. No pause-snapshot path is accepted from
an operator surface (B-315 constraint 3), and nothing stores the decision outside the existing
resume claim and journal (constraint 5). The resumed step consumes it once through step 0.

### C5. Attribution

- **Audit actor.** The step-4h audit keeps `actor=step_context.parent_actor`, recorded and named as
  the launching principal of the run. No human responder identity is recorded or claimed.
- **Ingress carrier.** Each harness ingress sets the elicitation data field `ingress` to one of
  `python`, `cli-tty`, `daemon-client-tty`, `unattended`. It is client-reported over the daemon's
  local Unix socket or the in-process session, not authenticated. `ServerCtxElicitCallback`
  validates it against that closed set and returns it on `AskUserQuestionResult` (new optional
  field `ingress`); MCP-native `decline`/`cancel` and replies without the field give `unreported`.
- **Server-side setter.** The composer sets `hitl.response.ingress` from that field on the
  `hitl.invocation.responded` span (`P/lifecycle/hitl_gate_composer.py:2480-2489`). For the
  `cancel`/timeout path, which has no responded span today, it sets the attribute on the
  `hitl.invocation.opened` span.
- **Refusal reasons.** Ingress refusals carry their literal reasons through `accept refuse` (C3),
  so the audited `rejection_reason_hash` discriminates operator rejection, unattended refusal,
  noninteractive refusal, invalid input and callback failure.

## Literal assertions for T03

Each runs through the public ingress (in-process `api.run` / `harness run`, and a real daemon over
its Unix socket for the `--daemon` rows), with a fixture workflow whose gated step writes one
marker file. "Zero effects" means the marker is absent and the ledger has no dispatch entry for
the gated step. "Audit" is the step-4h `CPAuditLedgerEntry`; "ingress" is the span attribute (C5).

1. `api.run` with `operator` returning `approve`: result SUCCEEDED, marker written once, audit
   response `approve`, ingress `python`. The callback received an `OperatorRequest` whose
   `step_id`, `payload` and `payload_sha256` equal the gated step's.
2. `api.run` with `edit` and `{"k": "edited"}`: marker content comes from the edited payload; the
   audit's `edited_proposal_hash` is the hash of the decoded payload.
3. `api.run` with `reject "no"`: `RT-FAIL-HITL-GATE-REJECTED`, zero effects, audit `reject` with
   `rejection_reason_hash` of `no`, ingress `python`.
4. `api.run` with `operator=None`: REJECTED, zero effects, audit `reject` with the hash of
   `unattended: no operator input bound`, ingress `unattended`.
5. `api.run` with a callback that raises `ValueError`: REJECTED, zero effects, audit hash of
   `operator input callback failed: ValueError`, ingress `python`.
6. `harness run` with stdin not a TTY: no prompt read, the CLI's REJECTED exit code, zero effects,
   audit hash of `noninteractive: no operator terminal`, ingress `cli-tty`, finishes within the
   fixture's bound.
7. `harness run` on a pseudo-TTY: before any answer is read, stderr contains the C1a message with
   the gated `step_id` and payload hash. Input `approve`: exit 0, marker written, ingress
   `cli-tty`. Input `bogus`: REJECTED, zero effects, audit hash of `invalid operator input`.
   Assertions 4–7 give four pairwise distinct `rejection_reason_hash` values.
8. `harness run --daemon` on a pseudo-TTY: the C1a message is shown before reading; input
   `approve`: daemon run SUCCEEDED, marker written, ingress `daemon-client-tty`; input `reject`:
   REJECTED, zero effects. Same daemon, both runs, no restart.
9. `hold` on each ingress with the durable pause binding demonstrated bound in the fixture config:
   exit 5 (PAUSED) with a resume handle, zero effects; then one resume with
   `--hitl-response approve` writes the marker once.
10. `hold` without the durable pause binding: audited REJECT with reason
    `hold unavailable: no durable pause binding`, zero effects.
11. A second resume of the same handle after assertion 9's successful resume is refused by the
    existing root claim refusal class, and the marker is still written once.
12. `cancel` on each ingress: fail-closed REJECTED, zero effects, ingress on the opened span.
13. Bounded wait, `placement.timeout` unset, `OPERATOR_ELICITATION_DEADLINE_SECONDS` patched to
    2 s in the source test: (a) `api.run` whose callback never returns ends REJECTED within 2 s
    plus slack, zero effects; (b) a daemon client killed while the prompt is open: the daemon's
    run ends REJECTED within 2 s plus slack, zero effects, and the same daemon then serves a
    following run. With the constant unpatched, a separate check asserts its value is 900.
14. A non-harness reply `accept` with `ingress="root"` or `response="refuse"` lacking a reason is
    refused as outside C1/C5 with zero effects.
15. Existing workflow-layer pause/resume, root-claim and HITL composer regressions stay green.

## Fork rulings (review pass 1, `cmt-53ad3553-8352-47a3-b855-d19c9239b45e`)

- **F1 hold mapping.** Accepted by the reviewer on condition that the durable binding is
  demonstrated with zero-effect and one-shot resume behavior (assertions 9–11).
- **F2 attribution.** Accepted as the launching principal, subject to the C5 ingress carrier.
- **F3 unset timeout.** Settled in C3a: a fixed 900 s deadline whatever the SDK does.
- **F4 prompt content.** Settled in C1a; no longer deferred.
- **F5 inherited-gate refusal (A4).** Accepted: this contract changes no inherited-gate rule, so
  it needs nothing from A4. Child-workflow gates are excluded from T03 assertions.
- **Open for Buford ratification:** the 900 s constant and the 8192-byte payload display bound.

## Disposition (on ratification)

The C1–C5 contract becomes the next free Runtime spec version's §14.8 amendment to C-RT-18, with
one plan unit for T03 carrying assertions 1–15, materialized in P2 before T03 claims conformance.
No source or test change is made by this stage.
