# Class 3 Drift — `Spec_Harness_Runtime_v1.md` §11 prose post-Lane-6

**Class:** 3 (informational drift)
**Filed:** 2026-05-20 at Lane 6 close
**Trigger:** Runtime un-strike of `[[fork-u-rt-44-workflow-loop-drain]]` realized
the §11 risk-surface "thin adapter" outcome, but §11's body prose still reads
as if runtime owns the flag-polling loop.

## Drift

`Spec_Harness_Runtime_v1.md` v1.1 §11 C-RT-11 lines 618-622 say:

> Track A specifies drain at the runtime layer using a flag-polling pattern:
> - `HarnessContext.drained_flag: asyncio.Event` is initialized at stage 0 …
> - A signal handler (installed at stage 7 …) sets the flag.
> - **The CP workflow lifecycle loop polls `ctx.drained_flag.is_set()` at each
>   lifecycle boundary** (per-step entry, per-step exit, per-topology-dispatch
>   entry).

Post-Lane-6, the CP workflow lifecycle loop primitive exists at
`harness_cp.workflow_driver.execute_workflow()` per `Spec_Control_Plane_v1_4.md`
§25 C-CP-25 + plan v2.11 U-CP-56/U-CP-57. The runtime delegates via
`api.run()` → `asyncio.wait_for(asyncio.to_thread(execute_workflow, ...))`.
The §11 risk-surface explicitly anticipated this:

> If CP later surfaces a native drain primitive … refactor `harness-runtime/`
> to delegate drain to CP. This contract becomes a thin adapter.

So the §11 outcome is realized, but the §11 body prose is now stale (it
describes the pre-resolution state).

## Asymmetry with the CP-side arc

The CP-side fork resolution bumped `Spec_Control_Plane_v1_3.md` → v1.4 to
record C-CP-25. The runtime-side made no analogous spec bump. The Lane 6
landing follows the spec §11 risk-surface guidance verbatim ("thin adapter")
without altering the contract surface or adding new ADR commitments — there
is no new C-RT-NN contract to record. The drift is documentation-only.

## Disposition

Non-blocking; informational only. No revision-pass triggered.

- ✅ No new contract surface introduced at Lane 6 (the spec already
  authorized the outcome at §11 risk surface).
- ✅ No callee-facing API drift (`run()` signature pinned at C-RT-08).
- ✅ No ADR commitments altered.
- ⚠️ §11 body prose describes pre-resolution state; future readers should
  pair §11 body with the §11 risk-surface guidance + this drift record.

## Routing

Class 3 informational; logged here for visibility. Routes to a future
`Spec_Harness_Runtime_v1.md` revision pass when the runtime spec next bumps
(any reason). Suggested §11 body amendment at that pass:

- Add an "Updated at Lane 6 (2026-05-20)" header line.
- Rewrite §11 body to describe the post-resolution shape: runtime
  delegates drain to CP driver via `asyncio.wait_for(asyncio.to_thread(...))`
  composition; signal handler installs at stage 7 INGRESS_ACCEPT as before;
  `RuntimeConfig.drain_timeout_seconds` bounds the wait.
- Preserve the §11 risk-surface text as historical anchor.

## Provenance

- Lane 6 commit: (current uncommitted; will be the Lane 6 landing commit).
- Advisor flag: 2026-05-20 advisor call at Lane 6 pre-commit review.
- Parent fork: `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md`
  (now CLOSED-PARTIAL).
