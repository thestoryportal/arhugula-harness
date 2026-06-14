# R-FS-1 arc #11 (B1-impl-5 = U-CP-85) — decorrelated review record

**Arc:** R-FS-1 arc #11 · **Unit:** U-CP-85 (`cascade_policy` consumption + cascade-cancel, C-CP-25 §25.15) · **Branch:** `r-fs-1-arc-11-cascade-policy` · **Date:** 2026-06-13 · **Posture:** Phase-7 impl (only `harness-cp/src` + tests; no `design-substrate/**`). This doc is back-flow/reconciliation documentation for the arc, not a design-substrate edit.

## What landed

Four composable cascade-policy pieces in `harness-cp/src/harness_cp/workflow_driver.py`, unit-proven against synthetic branch coroutines (real `asyncio` cancellation); the real-strategy + `RunResult` e2e lands at U-CP-88 (the first cascade-policy consumer, deps `[U-CP-82, U-CP-83, U-CP-84]` — all landed; U-CP-85 itself is 3 arcs ahead of its first consumer):

- `cascade_policy_run_status(policy) -> RunStatus` — §25.15.1 on-branch-failure run-level mapping (cascade-cancel→FAILED, proceed→PARTIAL, pause→PAUSED; obl. 6). **No `degraded` field minted** — `RunStatus.PARTIAL` is the sole degradation signal (the "degraded=true" is SRE prose, not a contracted `RunResult` field; verified `RunResult` has no `degraded`).
- `resume_should_redispatch(terminal_status) -> bool` — resume-idempotency-terminality (obl. 7): any persisted terminal_status ⟹ not re-dispatched; only `None` is eligible.
- `cascade_cancel_barrier(branch_coros, *, deadline_seconds)` — `asyncio.TaskGroup` structured cancellation of not-yet-dispatched siblings (obl. 1 + 8) + a HARD wall-clock deadline cap (a deadline watchdog cuts off in-flight dispatches DIRECTLY so the shielded drive honors the deadline; `asyncio.timeout` bounds gate-stuck branches). The in-flight registry CHAINS across nesting (outer deadline stays a hard cap over inner work).
- `dispatch_branch_step_shielded(inflight) -> T` — an in-flight effectful dispatch runs to completion under a sibling cascade-cancel (→ `completed`) or is cut off at the deadline (→ `timed_out`); a dispatch that ERRORS during the cancel-drive → `completed` (ran-and-errored, not a spurious failure).

23 tests; the three discriminating terminal dispositions (`cancelled` / `completed` / `timed_out`, obl. 4) drive through real `asyncio` cancellation and persist via U-CP-84 (drained + asserted).

## Empirical async validation (probe-first discipline)

The hard async design was validated through throwaway `asyncio` probes BEFORE committing (the same discipline that caught arc-9's concurrency bugs). The first probe caught a real bug: a naive `asyncio.shield`-drive-to-completion makes the deadline ineffective (a 0.1s deadline waited the full 1.0s in-flight dispatch and recorded `completed`, never `timed_out`). Fixed via the deadline-watchdog that cuts off in-flight dispatches directly. All five canonical cases (in-flight-deadline → timed_out 0.10s; gate-stuck → cancelled 0.10s; sibling-fail → completed; cancel-at-gate; clean) verified with `warnings.simplefilter("error")` (leaks-as-errors). Nested + dispatch-error cases probed similarly.

## Decorrelated review — 3-way, all converged

| Reviewer | Kind | Findings → resolution |
|---|---|---|
| **advisor()** | transcript-aware (in-family) | (1) The `cascade_cancel_barrier` docstring falsely claimed `bounded_barrier` is the "proceed/pause counterpart [that] lets siblings run to completion" — FALSE: `bounded_barrier`'s `finally` cancels pending siblings on a branch failure, so it does NOT implement `proceed`. **Fixed** the docstring (proceed/pause flows owed at U-CP-88). (2) The watchdog "created-first → scheduled-first" comment isn't the real guarantee. **Fixed** (the direct `inflight.cancel()` is order-independent). (3) `timed_out` only tested single-branch. **Fixed** (added a 3-branch all-in-flight deadline test). (4) Honesty: commit said obl. 5 "discharged" — only gate-ORDERING is shown; the real C-AS-02→C-CP-19→C-CP-16 gate + proceed/pause flows are owed at U-CP-88. **Fixed** the commit/PR/this-doc framing. |
| **`just codex-review`** | out-of-family (gpt, $0 subscription) | (1) [P2] obl-3 audit gap: the `timed_out` path recorded only the terminal marker, not the dispatched step's entry — a timed-out step WAS dispatched, so obl. 3 ("every dispatched effectful step has its own step ledger entry, regardless of terminal disposition") owes it. **Fixed** (record step on both completed + timed_out; `cancelled` records none). (2) [P1] nested fan-out: `_BRANCH_INFLIGHT_DISPATCHES.set()` SHADOWED the parent registry, so a nested barrier's in-flight dispatches were invisible to the OUTER deadline watchdog → the outer deadline stopped being a hard cap (HIERARCHICAL_DELEGATION, U-CP-89). **Fixed** via the registry CHAIN (a dispatch registers in every enclosing barrier's set; probe confirmed outer-deadline 0.05s hard-caps a nested 30s dispatch at 0.053s). |
| **harness-adversarial-reviewer** (genuine dedicated agent, 43 tool-uses) | spec-faithful red-team | **VERDICT: APPROVE-WITH-CLASS-2.** F2-01 (Class 2): `dispatch_branch_step_shielded` let a non-`CancelledError` dispatch exception ESCAPE during the drive-to-completion → a sibling-cancelled branch whose in-flight model/tool call ALSO errors was spuriously marked FAILED with NO `terminal_status` recorded (audit gap — the silent-effect failure mode Fork-A exists to foreclose). **Reachable** at U-CP-88 (a `StepDispatcher.dispatch` raising is the dominant real failure mode). **Fixed** per the landed `append_branch_terminal_ledger_entry` closed-set contract ("a ran-and-errored branch is `completed`"): swallow the dispatch error in the drive + re-raise `CancelledError`; the caller records `completed` (probe confirmed: branch → completed, ExceptionGroup carries ONLY the sibling's `ValueError`, no spurious failure, no "exception never retrieved"). The agent also CLEARED (with stated evidence): obl. 6 / no-degraded; §25.15.1 enum mapping; obl. 8 TaskGroup leak-freedom; deadline hard cap (50/50 runs); ContextVar add/discard vs watchdog snapshot; `procedural_tier_snapshot_ref` faithfulness (synthetic harness `None` matches the landed helpers' resolver-less canonicalization — no papered-over gap); obl. 7; X-AL-3 / no silent design extension; cross-spec drift. Its F1-01 (deadline-ordering comment) + F1-02 (`RunStatus` "cardinality 4" stale docstring — pre-existing, spec's own Q1 nit) were already-fixed / out-of-scope respectively. |

**Decorrelation value realized:** each reviewer caught what the others missed — Codex caught the obl-3 gap + the nested [P1] (concurrency), the adversarial agent caught F2-01 (the dispatch-error audit gap), advisor caught the false docstring claim + the scope-honesty overclaim. No two found the same primary issue.

## Honest scope boundary (owed at U-CP-88, NOT closed here)

Under the FULL-SPEC "nothing deferred" directive these are tracked-as-owed, not silently dropped:

- The `proceed` FLOW (siblings run to completion → partial set → `PARTIAL`; needs a `return_exceptions`-collecting barrier — NOT `bounded_barrier` as-is, which cancels pending siblings on a failure).
- The `pause` FLOW (halt the fan-out at the HITL/pause boundary → `PAUSED`).
- Obligation 5's REAL high-blast-radius pre-dispatch gate (the committed C-AS-02 `sandbox_tier_floor` → C-CP-19 §19.1 `gate_level` max() → C-CP-16 4-response HITL chain). U-CP-85 demonstrates obl. 2 gate-ORDERING structurally (a synthetic `asyncio.sleep` gate fires before dispatch); the real gate is the consuming strategy's to wire.

U-CP-85 supplies the cascade-cancel barrier + the `cascade_policy_run_status` mapping; the consuming strategy (U-CP-88) composes these with the real gate + the proceed/pause flows.

## Posture + X-AL-3

Phase-7 impl posture — only `harness-cp/src/harness_cp/workflow_driver.py` + `harness-cp/tests/test_workflow_driver_cascade_policy.py`. Zero `design-substrate/**` edits; no new primitive/contract minted (the §25.15 design was committed at the cleared arc-#6 spec v1.32 + council-resolved Fork A; this arc CONSUMES it). X-AL-3 trivially clean; plans cleared at arc #6 → no clearance marker owed. `CascadePolicy` import is CP-local → no CXA Pattern-P1 ripple (verified: harness-runtime CXA gate green).

## Verification

harness-cp 903 + harness-runtime 1646 (+19 skipped, creds-gated) + pyright strict 0/0/0 (harness-cp + harness-runtime packages) + ruff + overlay 312 nodes / 31-31 seams — all green. 23 arc tests.
