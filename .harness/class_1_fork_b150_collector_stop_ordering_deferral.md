# Class 1 fork — B-150 collector half: step-3a collector stop races a timed-out flush's late export

**Status:** ✅ APPLIED-AS-(a) (Runtime v1.116 → v1.117, this PR) — adjudicated
via loop-mode /resolve per
`[[feedback-noncoding-operator-decorrelated-adjudication]]`: transcript advisor
**VOTE: A** (three corrections absorbed below); out-of-family codex vote
**UNPARSEABLE across 3 attempts** (agentic despite answer-only constraints; its
own worktree implementation was A-shaped — recorded, not counted; the
out-of-family layer still fires on this PR's diff via `just codex-review`).
RESOLVE row at `.harness/loop_status.md`. Clearance
`spec-harness-runtime-v1-117-cleared-2026-08-11.md`.

*Filed 2026-08-11 by the loop orchestrator (B-150 collector half — the only
remaining B-150 leg; falsifier grounding at PR #1305 and the register row's
`grounded_2026_08_11` block confirmed the leg spec-touching; the atexit half
closed impl-only at PR #1307). All cites re-read at HEAD this session.*

## The discrepancy

C-RT-10 (`Spec_Harness_Runtime_v1.md` §10, :3724-3763 at v1.116) orders an
UNCONDITIONAL step-3 close sequence: *"Stop collector daemon (structured-stop
per C-RT-07)"* (:3745) strictly before *"`await tracer_provider.shutdown()`"*
(:3746), and step 6 verifies *"Collector daemon process/thread terminated"*
(:3755) at shutdown return.

The B-147 bounded-flush machinery (PR #1303, impl-only) made step 3b
CONDITIONAL: when a timed-out `force_flush` worker is still exporting
(`_tracer_flush_in_flight`, `shutdown.py:1167`), the inline tracer close is
skipped, `tracer_provider` is reported failed, and a deferred daemon watcher
closes the provider after the last worker completes
(`_spawn_deferred_tracer_close`, `shutdown.py:481-589`, with the #1307 ordered
atexit backstop). Step 3a (`_close_collector_daemon`, `shutdown.py:1153-1158`)
remained unconditional — so on exactly the deferred path, the still-running
export completes AFTER the collector is stopped: flush-start → collector-stop
→ flush-end, and the late spans land on a stopped collector (codex P1 at the
#1303 delta round; registered as B-150 rather than absorbed).

## The two candidate resolutions

**(a) In-flight-conditional step-3a deferral mirroring 3b (recommended).**
When `_tracer_flush_in_flight(ctx)` at step 3a, skip the inline collector
stop, report `collector_daemon` in the `ShutdownReport` failures (the same
honest-reporting shape 3b uses), and thread the collector stop into the SAME
deferred chain: last worker completes → collector stop (3a) → tracer close
(3b) — C-RT-10's 3a→3b relative order preserved verbatim inside the deferred
chain. Grounds:

1. **Forward-correctness (advisor-corrected framing).** At HEAD the collector
   daemon is a supervisor SCAFFOLD with no live OTLP receiver
   (`collector_daemon.py:34-42`; placeholder `ingest_span_row` :279-287), so
   today the window is VACUOUS — no span is salvaged or lost at the daemon
   either way. That cuts BOTH ways, and it cuts harder against (b): a
   ratified-cost carve-out would permanently encode span loss against
   C-RT-10's own enablement (*"Enables every R-OD-* requirement that depends
   on flush-completion (audit ledger consistency, span visibility)"*, :3728)
   for a cost that becomes REAL exactly when the live receiver lands — which
   is exactly when the deferral becomes the correct behavior (a live export
   RPC completing against a stopped receiver FAILS; a receiver kept up until
   worker-finish lets the deferred export succeed). Scope honesty: worker
   completion means `force_flush` RETURNED; on `True` the export completed;
   on `False` (internal BSP timeout, `shutdown.py:663-664`) the BSP thread
   may still be exporting — the deferral NARROWS the window, it does not
   eliminate it (the same residual the 3b deferral already carries).
2. **One mechanism, not two behaviors.** The deferred chain + ordered atexit
   backstop already exist and already own the close lifecycle on this path
   (#1303/#1307, ten review rounds + 3-lens gates); deferring 3a is the
   consistent completion of that machinery, not new machinery.
3. **The spec order is preserved, not weakened** — 3a still strictly precedes
   3b, both inline (normal path) and inside the deferred chain (timeout
   path). Only the *when* moves, in the same way 3b's already did.
4. TWO step-6 invariants are qualified (advisor catch — the fork's first
   filing named only one): *"Collector daemon process/thread terminated"*
   (:3755) becomes terminated-OR-owned-by-the-deferred-chain, AND *"No
   background task remaining on the asyncio event loop"* (:3757) gains the
   deferred-path qualification (the daemon's `_run_loop` task is alive at
   return on this path, terminated by the deferred chain or dying with the
   loop/process). This ALSO ratifies in contract text the 3b deferral +
   ordered-atexit-backstop machinery that currently rides impl-only —
   closing an unratified-deviation gap in the same pass.
5. **Impl constraint (advisor catch):** `CollectorDaemonSupervisor.stop()` is
   async and loop-bound (`collector_daemon.py:226-255` awaits a task on the
   harness loop); the deferred watcher is a plain daemon thread and the loop
   may be closed by worker-finish. The deferred stop must schedule
   thread-safely with a loop-dead guard — loop closed ⇒ the daemon task was
   destroyed with it ⇒ treat as terminated. Live surface is cell-1
   (in-process placement) only; non-cell-1 supervisors are no-op stops.

**(b) Ratified-cost carve-out** — declare the flush-start → collector-stop →
flush-end window an accepted cost of bounded shutdown (flush already reported
failed; late spans lost). Rejected: it ratifies span loss against the
contract's own stated enablement, on the only path where the data is still
recoverable, and leaves the machinery asymmetric (3b defers to save the
provider close; 3a discards the very spans that close was deferred to
protect). The carve-out saves one small impl diff — the deferral's cost is
one mirrored conditional + threading one stop call into an existing chain.

## Blast radius

Spec §10: one clause at the step-3 collector bullet; one qualification at the
step-6 invariant; one paragraph declaring the deferred-close discipline
(covers 3a+3b + the atexit backstop). Impl: mirror the `_tracer_flush_in_flight`
condition at step 3a + thread `_close_collector_daemon` into the watcher chain
ahead of the tracer close; witnesses per the #1303 subprocess-probe shape +
ordering spy. Normal-path (no in-flight worker) behavior byte-identical. No
CXA rows; no new contract numbers; no cross-axis delta; no hash impact.

## Routing

Class 1 (spec revision) per `Project_Workflow_v1_8.md` §2.7.6 →
`Spec_Harness_Runtime_v1.md` v1.116 → v1.117 amendment + clearance marker,
bundled-absorption arc per root `CLAUDE.md` §11.4 (this fork doc + the
clearance marker are the X-AL-3 back-flow documentation). Closes the last
open B-150 half; re-run the #1303 witness set green per the register
close_out step (3).
