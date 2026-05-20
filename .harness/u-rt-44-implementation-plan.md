# U-RT-44 — Drain semantics (runtime-owned flag-polling)

**Status:** in-progress
**Spec:** `design-substrate/Spec_Harness_Runtime_v1.md` §11 (C-RT-11)
**Decomposition:** `.harness/phase-2-session-3-track-a-atomic-decomposition.md` L10
**Predecessor:** U-RT-43 (LANDED at commit `bf8d838`)
**L-stage:** L10 stage 7 (drain) — opens L10

---

## Scope (partial-land per `[[halt-route-split-AC-pattern]]`)

C-RT-11 commits 3 drain surfaces:

| Surface | Owner | Materializable now? |
|---|---|---|
| (1) `drained_flag` set by signal handler | runtime | ✅ YES |
| (2) CP workflow lifecycle loop polls flag at boundaries | CP | ❌ NO — no CP loop landed; `api.run()` raises `WorkflowExecutionNotYetLandedError` post-bootstrap |
| (3) `harness_runtime.run()` rejects new invocations with `HarnessDraining` | runtime | ✅ YES |

**U-RT-44 lands surfaces (1) + (3). Surface (2) STRUCK → Class 1 fork.**

## ACs

| AC | Status | Materialization |
|---|---|---|
| AC #1: SIGTERM sets the flag | LAND | signal handler installed at stage 7; sets `ctx.drained_flag` + module-level `_process_drained` |
| AC #2: in-flight step completes bounded OR typed timeout | **STRIKE** | requires CP workflow loop primitive (not landed) — Class 1 fork filed |
| AC #3: no new ingress accepted post-drain | LAND | `api.run()` checks `_process_drained` pre-bootstrap; raises `HarnessDraining` |

## Class 1 fork (NEW)

File at `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md`. Resolution paths:

- **A (recommended):** wait for CP workflow loop unit; refactor U-RT-44 to land AC #2 at that point. Matches spec §11 risk surface ("if CP later surfaces a native drain primitive, refactor U-RT-44 to delegate").
- **B (rejected):** land runtime-side workflow loop scaffolding now. Scope creep — not in U-RT-44 atomic decomposition; CP-axis territory.
- **C (rejected):** re-spec C-RT-11 to drop AC #2 from runtime axis entirely. Spec architectural call, not a Phase 7 execution call.

## Implementation

### Files

- `harness_runtime/drain.py` (NEW, ~120 LOC) — `install_signal_handlers(ctx, loop)`, `uninstall_signal_handlers(loop)`, module-level `_process_drained: bool`, `is_process_drained()`, `_on_drain_signal(ctx)`.
- `harness_runtime/api.py` — add `HarnessDraining` typed error; `run()` pre-bootstrap check via `is_process_drained()`.
- `harness_runtime/bootstrap/stage_7_ingress.py` — call `install_signal_handlers(ctx, asyncio.get_running_loop())` AFTER `freeze()` succeeds.
- `harness_runtime/bootstrap/__init__.py` — `_rollback_ingress` calls `uninstall_signal_handlers(loop)` (rollback-symmetry; unreachable in practice since freeze is last, but defensive).

### Signal handler discipline

- Use `loop.add_signal_handler(signal.SIGTERM, _on_drain_signal, ctx)` + same for `SIGINT`. asyncio-aware; correct primitive for setting `asyncio.Event` from signal context.
- `_on_drain_signal(ctx)`: `ctx.drained_flag.set()` + set module-level `_process_drained = True`.
- Second-SIGTERM escalation: **deferred** (spec §11 marks "deferred to implementation discretion").
- Rollback: `loop.remove_signal_handler(signal.SIGTERM)`.
- Process-level drain flag is one-way per spec invariant.

### Test plan (~12 tests)

- `test_drain_signal_handler_sets_flag` — call `_on_drain_signal` directly, verify both flags.
- `test_install_uninstall_signal_handlers_idempotent` — install/uninstall round-trip.
- `test_api_run_rejects_post_drain` — set `_process_drained=True`, expect `HarnessDraining`.
- `test_api_run_drain_check_precedes_bootstrap` — check happens before `_run_lock`.
- `test_signal_handler_installation_at_stage_7` — full bootstrap; verify SIGTERM handler registered.
- `test_drained_flag_one_way_invariant` — once set, stays set.
- 1 integration: `os.kill(os.getpid(), signal.SIGTERM)` + `await asyncio.sleep(0)`; verify flag set. Skip on win32.
- 3 unit tests for `HarnessDraining` typed error shape.

### Test isolation

- Module-level `_process_drained` requires per-test reset. Autouse pytest fixture `_reset_process_drained`.
- Per-test signal-handler cleanup: `loop.remove_signal_handler(SIGTERM/SIGINT)` in teardown.

## Risks

- **R1: Windows.** `loop.add_signal_handler` unsupported. Production target is Linux/macOS per stack commitment. Test marker handles.
- **R2: ctx lifetime.** Track A bootstrap-per-call; ctx outlives one `run()`. After return, loop closes, handlers gone.
- **R3: Test parallelism.** pytest-xdist would parallelize; in-process serial is fine. Module state per worker if xdist invoked.

## Out-of-scope

- AC #2 (in-flight step drain) — Class 1 Path A: wait for CP loop.
- Second-SIGTERM escalation — spec marks deferred to implementation discretion.
- Drain bounded-wait timeout — lands at U-RT-45/46.
- `WorkflowEventClass.DRAINED` emit — STRUCK at U-RT-41 per `[[fork-drained-event-class]]`.
