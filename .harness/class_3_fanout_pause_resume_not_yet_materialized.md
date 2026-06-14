# Class 3 (informational) — fan-out `pause` cascade returns FAILED, not the cleared-spec PAUSED (interim, pending the resumable-fan-out-pause build arc)

**Filed at:** R-FS-1 arc #14 / B1-impl-8 (U-CP-88 `ORCHESTRATOR_WORKERS`) landing (2026-06-14)
**Locus:** impl `harness-cp/src/harness_cp/workflow_driver.py` `_execute_orchestrator_workers` (the `pause` cascade branch) vs cleared spec `design-substrate/Spec_Control_Plane_v1_32.md` §25.15.1 row (`pause → PAUSED`) + §25.15.2 obligation 6
**Classification:** Class 3 (informational) per `Project_Workflow_v1_8.md` §2.7.6
**Routing:** Non-blocking; log-and-proceed. The resumable-fan-out-pause **build** is tracked at `beyond-mvp-capability-boundary-ledger.md` Bucket B (`B-FANOUT-PAUSE`). The §25.15.1 spec's final shape for fan-out `pause` is decided **by** that build arc (it may become resumable-PAUSED, or a distinct disposition) — so this is a fork doc recording the interim deviation, NOT a premature §25.15.1 amendment.

## The deviation

Cleared CP spec §25.15.1 maps, byte-exact and unconditional:

> `| pause | Halt the fan-out at a HITL/pause boundary (composes with C-CP-26 PauseResumeProtocol + C-RT-30 api.resume). … | **PAUSED** |`

and §25.15.2 obligation 6: "`pause` → `RunStatus.PAUSED`".

The U-CP-88 impl, on a worker failure under `cascade_policy == pause` (reachable: TEAM_BINDING persona via the §11.4 D4 tunable), returns **`RunStatus.FAILED`** with `fail_class == "orchestrator-workers-pause-resume-not-yet-materialized"` (+ `salvage=True` so completed-worker outputs persist in `partial_state`; the orchestrator + dispatched-worker ledger entries persist — no silent loss).

## Why FAILED-now instead of the spec's PAUSED

§25.15.1 promises `pause → PAUSED` "composing with C-CP-26 PauseResumeProtocol + C-RT-30 `api.resume`". For the LINEAR path that composition works: the driver captures a position-only C-CP-26 `PauseSnapshot` (single `step_index`) and `api.resume` re-enters from it. For a **fan-out**, that composition is not yet materializable:

1. **Resume reconstruction is ledger-based (§25.15.2 obl. 7), not snapshot-based.** Fan-out resume must read each branch's persisted `terminal_status` (via the branch-scoped idempotency key) and skip the terminal branches / re-dispatch the rest. That **resume-re-entry path does not exist** — the non-linear strategies deliberately bypass the §25.3 prefix-replay / resume-detection (it is linear-only at HEAD; the strategy is resume-blind by design).
2. **Completed-branch OUTPUTS are not persisted for a resume merge.** The ledger entries carry `action_id` / `idempotency_key` / `branch_metadata` (causality + terminal_status) — NOT the dispatch OUTPUT mapping. So even with the resume-re-entry, the aggregate of a resumed fan-out could not recover the already-completed branches' outputs without a new persistence mechanism (candidate: the `PauseSnapshot.state_summary`, shape TBD).

Returning the spec's `PAUSED` **without** (1)+(2) would advertise a resumability the harness cannot honor: the runtime surfaces `RunResult.pause_snapshot` only from `cp_result.pause_snapshot` (None here), and `api.resume` requires a snapshot-or-handle — so a `paused` fan-out would be unrecoverable. That false-resumable `PAUSED` is the silent-degradation failure mode, **independently caught by two decorrelated reviewers** (a genuine harness-adversarial-reviewer agent + out-of-family Codex; record `.harness/adversarial-review-r-fs-1-arc-14-orchestrator-workers.md`). The honest interim is fail-loud (FAILED + an explicit `not-yet-materialized` fail_class), never a false-PAUSED.

## Why Class 3, not Class 1

Nothing ships broken and no downstream consumer gets a wrong answer:
- SUCCESS / `proceed` → PARTIAL / `cascade-cancel` → FAILED are independent of the pause gap and are correct + tested (incl. a live e2e through a real IS writer, §6.3 chain VALID).
- The `pause` path is HONEST (loud FAILED + explicit cause; audit record + salvaged outputs persist) — it does not silently mis-report. The runtime projects FAILED + a non-empty `terminal_state` + `failure_cause.validator_fail_class = <fail_class>`; no consumer keys "`partial_state` non-None ⟹ PARTIAL".

So this is `log-and-proceed` (the deviation is recorded here; the build is registered), not `halt-execution`. Back-flow is pre-authorized under the R-FS-1 full-spec directive (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`), so a follow-on build arc — not a silent bounded-residual — is the disposition.

## Resolution path (the follow-on build arc)

`B-FANOUT-PAUSE` at `beyond-mvp-capability-boundary-ledger.md` Bucket B. The build: (a) the fan-out resume-re-entry path (read persisted branch `terminal_status`, skip terminal branches per obl. 7, re-dispatch the rest); (b) completed-branch-output persistence for the resume merge (candidate: `PauseSnapshot.state_summary`); (c) capture a `PauseSnapshot` in the `pause` branch + return `PAUSED`; (d) the final §25.15.1 shape decision (resumable-PAUSED vs a distinct fan-out disposition) — design-fork-first per X-AL-3. On that arc landing, this Class 3 record closes and the U-CP-88 `pause` branch flips FAILED → PAUSED.
