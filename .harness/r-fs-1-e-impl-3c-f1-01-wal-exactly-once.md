# F1-01 — WAL_SEGMENT completed-run-retry duplicate `cp.resume-attempted` (floor-(ii) exactly-once)

**Status:** ✅ CLOSED (R-FS-2 `B-WAL-F1-01-EXACTLY-ONCE`) — Surfaced by the R-FS-1 E-impl-3c decorrelated adversarial re-review (2026-06-15). NOT a defect in E-impl-3c; was NOT gating. Fixed by applying the completed-run guard (`resume_at < len(steps)`) to the WAL_SEGMENT `_resume_engine_pause` predicate at `harness-cp/src/harness_cp/workflow_driver.py`, symmetric to the RECONCILER_LOOP branch's existing guard. Witness: `test_path_i_wal_completed_run_retry_is_idempotent` (`harness-runtime/tests/integration/test_u_rt_95_hitl_pause_trigger_durable_async_full_execution_path.py`) — asserts the `cp.resume-attempted` ledger-entry count stays at 1 across a completed-run retry (confirmed fail-on-main at count=2 before the fix, by execution). Fable-5 decorrelated review: fix confirmed correct + complete (semantics-verified against `_determine_resume_at`'s shared prefix computation; no WAL-specific divergence), test confirmed non-vacuous by mutation-testing (removing the guard reproduces the r3 failure).

**Severity:** floor-(ii) "idempotency-keyed exactly-once via the F2 ledger" (C-CP-07 §7.4) imperfection. Over-counts engine-layer resume attempts by one for an OD audit-trace consumer of the `resume:` action_id prefix. **No fail-closed, no run failure, no corruption** — strictly milder than the reconciler bug E-impl-3c fixed.

## What

A fully-completed `WAL_SEGMENT` workflow re-driven with the **same `run_id`** (at-least-once redelivery / crash-after-completion) emits a **second** `cp.resume-attempted` (C-CP-50) state-ledger entry for the same resume-event identity (`resume:{run_id}:{resume_at}`), rather than being a clean no-op.

Empirical (adversarial re-review probe): a completed WAL run driven 3× under one `run_id` → `cp.resume-attempted` count = 1 after r2, **2 after r3** (duplicate). The run still SUCCEEDs (no failure) — only the audit ledger over-counts.

## Root cause

The WAL_SEGMENT RESUME firing gate (`harness-cp/src/harness_cp/workflow_driver.py`, U-CP-95) is **presence-only** (`has_pause_record(...)`). The journal substrate's `attempt_resume` is **non-destructive** (`journal_pause_resume_substrate.py:187-223` — never deletes the journal record), so `has_pause_record` stays `True` after a successful resume. A same-`run_id` re-drive of a completed run therefore re-fires `attempt_resume`, which returns `RESUME_CLEAN` (WAL is re-resumable → no abort → no failure) but emits the duplicate ledger entry.

This is the WAL sibling of the reconciler completed-run bug E-impl-3c fixed (Codex [P2]). The reconciler version was **severe** (CAS lease → ABORT → fail-closed FAILED); the WAL version is **mild** (re-resumable → SUCCESS, just a duplicate audit entry). Both share the same root cause (presence-only gate + non-destructive substrate + completed-run re-drive); same defect class as the original Codex [P2.a] spurious-emit concern.

## Fix shape (when closed)

Apply the **same** completed-run guard E-impl-3c added to the reconciler branch, symmetrically, to the WAL_SEGMENT RESUME firing gate:

```python
_resume_engine_pause = (
    _engine_recovery_loop is not None
    and resume_at < len(steps)            # <-- add: completed run has nothing to re-resume
    and _engine_recovery_loop.has_pause_record(...)
)
```

`resume_at < len(steps)` skips the fire when every step is already committed (`resume_at == len(steps)`), so a completed-run re-drive returns SUCCESS via the empty step loop with no duplicate emit. The guard is an **upper bound only** — a step-0 engine pause (`resume_at == 0`) still fires (Codex [P2.b]). Verified-correct boundary semantics (E-impl-3c, reconciler branch): `_determine_resume_at` returns the contiguous-committed-prefix count, `step_count` iff every step resolves, so an incomplete run always reads `< step_count`.

Owes a WAL completed-run-retry exactly-once test (symmetric to E-impl-3c's `test_reconciler_completed_run_retry_is_idempotent`) asserting no duplicate `cp.resume-attempted` on the re-drive, plus a decorrelated Codex + adversarial review of the WAL behavior change (the reason it was NOT bundled into E-impl-3c — a behavior change to the cleared U-CP-95 branch owes its own review round; bundling would re-open a converged PR and cross defect domains).

## Why not fixed in E-impl-3c

Pre-existing (U-CP-95 / E-impl-2, shipped + cleared); out of E-impl-3c's unit scope (U-CP-97 + U-RT-124 are reconciler-only). Surgical-changes discipline: mention adjacent pre-existing issues, don't fix them in-arc. Decorrelated adversarial re-review recommended forward-note (not gating); advisor concurred (error asymmetry + avoid re-opening a triple-reviewed PR + the WAL change owes its own review round). FULL-SPEC posture governs deferred *capabilities*, not pre-existing latent bugs in shipped units — so this registration is the correct disposition, not a FULL-SPEC violation.
