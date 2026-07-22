# Class 2 Fork — B-59: capacity authority not preserved across sequential bootstrap invocations

**Status: FILED (draft) — awaiting out-of-family review + operator selection at §6.** Registered
at the B-48 apply arc (codex round-4 [P1] "preserve one capacity authority across bootstrap
runs"); the register row's close_out mandates Class 2 back-flow BEFORE building ("this is an
architectural decision on multi-bootstrap-per-process semantics, not a bounded bug fix").
Filed per the no-parking discipline (root `CLAUDE.md` §12.4.1): the complete filing is built
without the ratification; the operator answers §6.

## §1 The defect

`api.run()`'s shutdown drains the `SubAgentDispatchExecutor` with a deadline
(`sub_agent_dispatch_executor.py:404` `drain(deadline_seconds=...)` — join-free, poll-based,
never blocks on loop-bridged workers). Per the documented abandoned-worker contract
(§14.8.10.3: a drained-under-fence worker keeps its frame lease until its job's own finally
acks the fence), a worker still draining at the deadline retains its occupied frame. The
process then releases its run lock and permits another `api.run()` — but the NEXT bootstrap
constructs a FRESH executor at `bootstrap/stage_5_loop_init.py:617`
(`SubAgentDispatchExecutor(frame_budget=config.sub_agent_dispatch_max_workers)`) with the FULL
configured budget. The old worker's occupied frame is invisible to the new executor's
accounting, so the process can transiently exceed the single-shared-cap promise
(C-RT-03 cap field; Runtime spec v1.102 §14.8.10 executor contract) across the boundary.

Scope note (from the register row): the B-48 fork's own §4 verification obligations scope
entirely to a SINGLE dispatch/workflow-run's offload mechanics — cross-invocation continuity
was never ratified there. This filing owns it.

## §2 The design constraint

Whatever preserves the cap must survive `api.run()` teardown without violating:
- **Daemon-worker lifecycle** (§14.8.10.1): workers are daemon threads on the executor's own
  terms, never joined at interpreter exit — a "wait for full drain" cannot become an unbounded
  interpreter-exit join.
- **Fence-ack semantics** (§14.8.10.3 part 3): the drained worker's lease release is tied to
  its job's REAL termination (`add_done_callback` → `release_unless_job_bound`), not to any
  bootstrap-side bookkeeping — double-release and phantom-release are the failure modes.
- **Per-run isolation** (the B-48 ContextVar discipline): no cross-run bleed of run-scoped
  state through whatever survives the boundary.

## §3 Options (the Class 2 selection)

**Option A — process-scoped capacity-authority singleton.** A module-level (process-lifetime)
authority holding the frame ledger; each bootstrap ADOPTS it instead of constructing fresh.
Draining workers' leases stay counted until their own done-callbacks release them — the next
run's admissions see the true residual budget.
- For: exact cap preservation; zero waiting at bootstrap; the lease-release path is untouched
  (the done-callback releases into the SAME authority the new run reads).
- Against: process-global mutable state (the workspace has avoided module-level singletons —
  per-run isolation discipline); config drift across runs (run 2 configures a DIFFERENT
  `sub_agent_dispatch_max_workers` — the singleton must reconcile budgets: adopt-new-budget
  with occupied carried over is the coherent rule, but needs its own witnesses); test isolation
  (every test constructing executors must reset the singleton — a conftest fixture).

**Option B — cross-invocation drain barrier.** Block a NEW bootstrap's stage 5 until the PRIOR
executor reports zero occupied frames (poll with its own deadline; on expiry, fail bootstrap
loudly with a typed RT-FAIL naming the still-draining workers).
- For: no global mutable state; each run keeps its own executor; the cap invariant holds by
  exclusion rather than shared accounting.
- Against: bootstrap latency coupled to a wedged worker (the exact stranding §14.8.10's
  join-free drain exists to avoid — mitigated by the typed-failure deadline, but then a wedged
  worker makes the process UNABLE to bootstrap until it exits: availability loss where Option A
  degrades gracefully); needs a process-scoped registry of prior executors anyway (to find the
  thing to wait on), i.e. a singleton of a different shape.

**Recommendation: Option A** — the singleton's residual hazards (config drift, test isolation)
are witness-coverable and bounded, while Option B converts a drained-worker residual into a
bootstrap availability loss and still needs process-scoped state to name its barrier target.
Riders if A is selected: (1) adopt-new-budget-carry-occupied reconciliation rule with a
budget-shrink-below-occupied typed refusal; (2) a conftest reset fixture + an isolation
witness (two sequential in-process bootstraps see one authority); (3) the B-48 fence-ack
lease-release path byte-unchanged (witnessed by a drained-worker crossing the boundary and
releasing into the adopted authority); (4) **every executor admission surface** backs onto
the singleton — the DIRECT non-fan-out `reserve(1)` path as well as the CP fan-out adapter's
`reserve_fanout` (codex round-1 [P1] on this filing: globalizing only fan-out accounting
while each executor keeps a per-run direct budget still exceeds the cap on a run-2 single
offload).

## §4 Verification obligations (the apply arc's acceptance criteria)

1. Two sequential `api.run()` invocations in ONE process with a still-draining worker from
   run 1: run 2's fan-out admission sees `budget - occupied`, not the full budget (the defect's
   direct witness; PD-8: revert to fresh-construction → over-admission reproduces).
1b. The DIRECT-dispatch twin (codex round-1 [P1]): run 2's single NON-fan-out offload
   (`reserve(1)`) also sees `budget - occupied` — pins that the singleton backs every
   admission surface, not only the fan-out adapter.
2. The straggler's eventual done-callback releases into the authority run 2 reads (no phantom
   frame after the release; no double release).
3. Budget reconfiguration across runs: grow honored immediately; shrink below current occupied
   → typed refusal at bootstrap (never silent over-cap).
4. Per-run isolation preserved: run-scoped ContextVars/leases do not bleed (the existing B-48
   isolation witnesses re-run green).
5. Interpreter-exit posture unchanged (daemon workers; no new join).

## §5 Spec surface

Runtime spec v1.102 §14.8.10 (executor contract; C-RT-03 cap field) — an amendment rider
naming the process-lifetime authority scope (Option A) or the bootstrap barrier (Option B).
CP spec v1.102 §25.11 (capacity gating) references the single shared budget; the rider must
state that "single" spans sequential bootstraps within one process. Both are design-substrate
edits → the apply arc is a bundled-absorption PR with clearance markers (X-AL-3).

## §6 The operator selection (ONE decision)

Select the cross-bootstrap capacity-authority mechanism:
- **(A) process-scoped singleton authority, adopt-new-budget-carry-occupied (RECOMMENDED)**
- (B) cross-invocation drain barrier with typed bootstrap refusal on deadline
- (C) reject both — accept the transient over-cap as a documented residual (flips B-59 to a
  conditional queryable record like B-57)
