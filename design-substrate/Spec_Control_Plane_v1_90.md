# Spec: Control Plane — v1.90 (delta over v1.89)

*Delta-only file. The v1.89 body + the entire C-CP-01 … C-CP-29 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). This delta records the B-18-3C-PREWARM-CASCADE bundled-absorption arc: extending the ADR-D4 §1.8 concurrent-prompt-cache warm-up (serialize branch[0], then release branches[1..N-1]) from the PROCEED cascade-policy path (v1.87) to the strict tiers — CASCADE_CANCEL and PAUSE — via the shared `_cancel_fanout()` path.*

## Change-note (v1.89 → v1.90)

**What this materializes.** B-18-3C-PREWARM (v1.87) added the serialized-branch[0] cache warm-up to `_proceed_fanout` (PROCEED) only. The same warm-up benefit applies to the CASCADE_CANCEL and PAUSE paths, which share `_cancel_branch`/`_cancel_fanout`. Design authority: `.harness/b18-3c-prewarm-cascade-ddr.md` (pre-build DDR, Fable-5 review-cleared; §3b Option A operator-ratified 2026-07-11 and then probe-resolved — see below).

**Scope of revision.**

**§25.17 addendum — CASCADE_CANCEL + PAUSE paths:**

1. **Gate lift.** `_same_prefix_cohort()` and `_warmup_gate` (v1.88 dispatcher-attested `CohortKeyCapable` predicate; H3 `len(branch_plan) >= 2` guard) move from PROCEED-local to above the cascade_policy branch: one gate now serializes branch[0] on all three §25.15.1 paths. H3 keys on the LIVE branch_plan (post-recovery-seed): a partial-recovery resume warms the REMAINING cohort with a new "branch[0]" (the first remaining ordinal; Fable-5 C4, witnessed at W4b); a <2-branch remainder — including the crash-reconstruct empty plan — stays all-concurrent.

2. **Two-phase `_cancel_fanout`.** When `_warmup_gate` is True and `cascade_policy is CASCADE_CANCEL or PAUSE`, `_cancel_fanout()` serializes branch[0] (Phase 1, cache-write) before releasing branches[1..N-1] (Phase 2, cache-hits) under an `asyncio.TaskGroup`. Both phases share ONE `asyncio.timeout(deadline)` and ONE `_BRANCH_INFLIGHT_DISPATCHES` deadline-watchdog registration — the warm-up does NOT split into two `cascade_cancel_barrier` calls (each would grant a full `deadline` budget, doubling the §25.11 wall-clock cap). The barrier setup is inlined rather than parameterized (`serialize_first`) so coroutine creation stays lazy: a Phase-1 failure never instantiates a sibling coroutine (no un-awaited-coroutine leak; DDR §4 / Fable-5 C2 disposition).

3. **Phase-1 exception guard (Fable-5 R3).** Phase 1 uses `except asyncio.CancelledError: raise` — NOT `except (asyncio.CancelledError, TimeoutError)` — because `asyncio.timeout` delivers CancelledError INSIDE the block (converted to TimeoutError only at `__aexit__`); a bare `TimeoutError` raised BY branch[0] is a branch failure, not a deadline signal. Any other Phase-1 exception is wrapped `BaseExceptionGroup("cascade-warmup-branch0", [exc])` so the post-barrier classification (`except BaseExceptionGroup` → `branch_failed = True`) treats a Phase-1 failure exactly like a TaskGroup branch failure.

4. **Effect-set invariant (Fable-5 R1-corrected).** The warm-up WITHHOLDS branches[1..N-1] until branch[0] completes. On a Phase-1 failure their effect-set is empty (never dispatched — no reserve-before-dispatch marker is written), a strict SUBSET of the non-warmup barrier's effect-set (where a sibling may land an effect before the cascade arrives). Warm-up is therefore strictly safer on the tiers that exist to bound effects. Witnessed at W2 as dispatch-marker ABSENCE (Fable-5 M1), not merely `cancelled` ledger records.

5. **Budget tradeoff (Fable-5 R4, acknowledged).** Branch[0]'s serial Phase-1 duration consumes the siblings' deadline budget — the same acknowledged tradeoff as PROCEED warm-up (v1.87 §25.17). Opt-in via `concurrent_cache_warmup` (default True per v1.89, safe via the `CohortKeyCapable` oracle).

**§3b crash-window disposition (DDR §3b / Fable-5 R2 — REFUTED by probe; Option A NOT built).** The DDR flagged a crash window (branch[0] recovered `completed`/no-output + siblings never dispatched + PAUSED snapshot lost) as falling through to a silent PARTIAL, and prescribed a pre-barrier `branch_failed` synthesis (Option A, operator-ratified 2026-07-11). A pre-build empirical probe on HEAD refuted the gap: the ENTRY-time crash-resume gate (B-FANOUT-CRASH-RESUME-CASCADE-POLICY + B-FANOUT-CRASH-RESUME-PAUSE-RECONSTRUCT, v1.68 §1 + v1.70 §1 + v1.71 §1) intercepts before the strategy barrier —

- PAUSE tier: pause-trigger + incomplete recovery + siblings provably-not-run (instrumented, no dispatch marker) → `_crash_pause_reconstruct_no_dispatch` → empty branch_plan → `_crash_pause_reestablish` re-establishes PAUSED without dispatching (probe: `paused`, zero re-dispatches, snapshot = branch[0] only).
- CASCADE_CANCEL tier: degraded recovery → FAILED `fan-out-crash-resume-cascade-cancel` at entry (probe: zero re-dispatches).

The DDR's §3b premise ("branch_plan = [(1,…),(2,…)] non-empty → the fanout barrier runs") was stale against the v1.70 reconstruct mode. Option A's synthesis, correctly guarded, would be dead code on every reachable path (operator snapshot-resume is excluded by `resume_snapshot`; scoped-abort recovers as `scoped_aborted` ≠ `completed`; timed_out is not a pause trigger) — and the decorrelated diff review sharpened this further: **as sketched at DDR §7 (unguarded), Option A would be actively HARMFUL** — its predicate (completed ∧ not-in-collected ∧ not-in-branch_plan) is TRUE on every operator resume of a degraded pause, forcing a re-pause where the ratified Reading A produces PARTIAL (it would regress the W3 resume leg). The operator-ratified INTENT — never a silent PARTIAL in the crash window — holds on the pre-existing machinery and is pinned permanently by witness W6 (which produces the crash state organically through the NEW warm-up path: live Phase-1 failure → PAUSED → snapshot discarded → re-entry → PAUSED again, zero dispatches).

**Invariants preserved.** NO §5.2 IS-hash change. NO new contract / ADR / enum / fail-class / CXA edge. Records equivalence (DDR §3d): the same `_cancel_branch` writes the same dispatch-marker + terminal records regardless of warmup/non-warmup routing, so every crash/pause recovery path consumes byte-equivalent state. Gate=False (non-`CohortKeyCapable` dispatcher, or explicit opt-out) routes to the pre-arc `cascade_cancel_barrier` unchanged (W4).

**New witnesses** (`harness-cp/tests/test_workflow_driver_parallelization_warmup.py`, B-18-3C-PREWARM-CASCADE section):

| # | Test | Pins |
|---|---|---|
| W1 | `test_cascade_warmup_serializes_branch0_before_siblings` (×2 tiers) | Ordering on CASCADE_CANCEL + PAUSE |
| W2 | `test_cascade_cancel_warmup_branch0_failure_siblings_withheld_cancelled_failed` | Effect-set subset (marker ABSENCE) + `cancelled` scan + FAILED |
| W3 | `test_pause_warmup_branch0_failure_pauses_then_resume_redispatches_siblings` | PAUSE snapshot carries only branch[0]; resume re-dispatches siblings → PARTIAL |
| W4 | `test_cascade_cancel_warmup_gate_false_all_concurrent_baseline` | Gate=False byte-baseline (reverse-completion) |
| W4b | `test_pause_warmup_partial_recovery_resume_new_branch0_serialized` | Partial-recovery resume warms remaining cohort, new branch[0] |
| W5 | pre-existing PROCEED section unchanged-green post-lift | Lift regression |
| W6 | `test_pause_warmup_crash_window_reentry_repauses_never_silent_partial` | §3b crash window → PAUSED (never silent PARTIAL); Option A vacuity pinned |
| W7 | `test_pause_warmup_branch0_bare_timeout_error_is_branch_failure_not_deadline` + `..._fails_as_cascade` | R3 guard: bare branch[0] TimeoutError = branch failure (PAUSED / `parallelization-cascade-cancel`), never `parallelization-barrier-deadline` |

**Witness deviation (recorded).** DDR §4's "W4 covers the deadline-budget witness" line is superseded: the shared-single-budget property (one `asyncio.timeout` + one watchdog wrap BOTH phases) is structural — visible by construction in `_cancel_fanout` — and no unit witness is practical against the non-injectable 300 s `_DEFAULT_FANOUT_BARRIER_DEADLINE_SECONDS`. The built W4 is the gate=False baseline per the DDR §6 table row.

Suite state at close: harness-cp full suite green (incl. 10 new CASCADE witnesses); harness-runtime non-e2e 2360 passed; other axes 1590 passed; workspace pyright 0/0/0; decorrelated Fable-5 diff review 0 blocking / 3 concern (all resolved in-arc: spec+clearance bundled, DDR §10 addendum, W7 added) / 5 cosmetic (gate relocated below the effect-fence guard; W4 both-tiers; W6 cross-ref; 2 accepted-as-noted).

**Registered follow-ons (SPINE `B-*`) — updated status.**

| Follow-on | Scope | Status |
|---|---|---|
| `B-18-3C-PREWARM-COHORTKEY` | Dispatcher-oracle `CohortKeyCapable` Protocol | CLOSED (v1.88) |
| `B-18-3C-PREWARM-DEFAULT-ON` | Flip to required-at-cap>1 per ADR §1.8(f) | CLOSED (v1.89) |
| `B-18-3C-PREWARM-CASCADE` | warm-up on CASCADE_CANCEL + PAUSE paths | **CLOSED (this arc)** |
| `B-18-EPOCH-PARTITION` | version_sha cohort HASH + heterogeneous partition | Registered, open |
| `B-18-3C-PREWARM-TIMEOUT-LEDGER` | Audit-visibility gap when asyncio deadline fires during phase-1 warm-up (M2) — now ALSO applies to the strict-tier Phase 1 | Registered, open |

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_90.md` (delta over v1.89) |
| Arc | B-18-3C-PREWARM-CASCADE — extend cache warm-up to CASCADE_CANCEL + PAUSE cascade-policy paths |
| Committed source | ADR-D4 v1.1 §1.8; `.harness/b18-3c-prewarm-cascade-ddr.md` (Fable-5 review-cleared); §3b Option A operator-ratified 2026-07-11, probe-resolved vacuous (this delta) |
| Disposition | Gate lift + two-phase `_cancel_fanout` (shared deadline/watchdog, R3 guard); Option A NOT built (dead code — entry gate covers); 8 new witnesses |
| Decorrelated review | Fable-5 adversarial diff review (Codex TLS-blocked in bg session, standing fallback per `[[fable5-fallback-reviewer]]`) |
| IS / OD / AS / ADR | UNCHANGED. CXA v2.20 UNCHANGED. |
| Runtime spec | UNCHANGED |
| Follow-on status | B-18-3C-PREWARM-CASCADE CLOSED; B-18-EPOCH-PARTITION + B-18-3C-PREWARM-TIMEOUT-LEDGER remain open |
