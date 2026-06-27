# Arc-open grounding — `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT-SAVE-POINT`

*R-FS-1 forward-arc grounding. 2026-06-26. Bundled-absorption (CP spec v1.78 → v1.79 + harness-cp/harness-runtime impl in this arc's PR). Records the grounding + advisor design fork for the SAVE_POINT slice of the registered `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT-SAVE-POINT-RECONCILER`, and the RECONCILER follow-on framing.*

---

## 0. TL;DR

The registered arc anticipated *"SAVE_POINT/RECONCILER have NO durable per-step output store → an entirely new output substrate, a larger lift."* Empirical grounding overturned the substrate half **for SAVE_POINT**: the `EngineOutputStore` is mechanically engine-class-AGNOSTIC, and a real `SAVE_POINT_CHECKPOINT` run flows through the same `SINGLE_THREADED_LINEAR` dispatch loop as ESR/WAL. So the SAVE_POINT close is a **CP-side gate extension reusing the existing class-agnostic store** — NOT a new substrate (`[[grounding-reveals-claude-closeable-slice-close-honestly]]`).

**DECOMPOSE — close the SAVE_POINT slice (CP v1.79), register the RECONCILER follow-on. Net-zero (close 1 + register 1). No operator gate.**

---

## 1. The grounding (what the code actually shows)

- `EngineOutputStore` (runtime C-RT-32, `harness-runtime/.../engine_output_store.py`) is a per-run JSONL keyed by `run_idempotency_key`. Its stage-5 binding (`stage_5_loop_init.py:263`) is gated **only** on `RuntimeConfig.engine_output_replay` — **never** on engine class. The store is class-agnostic.
- The ONLY restriction of final_state reconstruction to `{ESR, WAL}` was two CP-side gates in `workflow_driver.py`: the `_record_durable_step_output` producer call site (was `:4225`) and the `final_state` seed (was `:3555`).
- The resume-`resume_at` dispatch block shows ALL four durable classes (SAVE_POINT, ESR, RECONCILER, WAL) compute `resume_at` via the same F2-prefix join, then fall through to the **same** linear dispatch loop where both gates sit. A real SAVE_POINT forward run therefore records through the producer (if the gate admits it) and reconstructs through the seed (if the gate admits it).

## 2. The advisor design fork + resolution

- **Reading A (chosen):** extend both gates to admit `SAVE_POINT_CHECKPOINT`, reusing the class-agnostic store. Unify the gates onto ONE `_FINAL_STATE_RECONSTRUCT_ENGINE_CLASSES` constant so "never record-only / never seed-only" is structural.
- **Reading B (rejected for SAVE_POINT):** a new class-native substrate. Unnecessary — the store already holds SAVE_POINT outputs mechanically.
- **Blocking criterion on the close (advisor):** a producer-half full-chain witness driving a REAL SAVE_POINT forward run (not a hand-seeded store) — the gate between honest-light-close and vacuous-close. **Confirmed RED on HEAD** (`assert set() == {0,1,2}` — the producer recorded nothing) → GREEN with the gate extensions. The producer is non-vacuous for SAVE_POINT.
- **Flag:** reuse `engine_output_replay` (the store-binding already keys on it) + generalize its docstring; no second flag (a second binding gate = a second source of truth). The conflation is cosmetic — the inter-step rehydrate is separately gated.
- **Spec-vs-fork:** bundled-absorption amendment, NOT X-AL-3 — the spec NOT-YET-PROVIDED reconstruction for SAVE_POINT (a registered boundary), it did not FORBID per-step outputs (`[[disposition-label-is-a-claim-verify-against-spec]]`). No §5.2 IS-hash arc.
- **Scope:** LINEAR-only (both gates live in the `SINGLE_THREADED_LINEAR` loop section; non-linear strategies return before the seed), mirroring the v1.75 child-scoped narrowing.

## 3. The RECONCILER follow-on (`B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT-RECONCILER`) — grounding lead

RECONCILER_LOOP is split out, NOT closed here, because the advisor's **two-authorities** concern is real and needs its own grounding:

- RECONCILER_LOOP is an **ENGINE-OWNS-SUBSTRATE** class (`workflow_driver.py` reconciler branch comment: *"the AUTHORITATIVE durable reconciler state lives in U-RT-123"*). The `ReconcilerEnginePauseResumeSubstrate` (`reconciler_pause_resume_substrate.py`) already persists `partial_state` in its `PauseEvent` checkpoint records.
- So reconstructing RECONCILER's CP-`accumulated` from the `EngineOutputStore` would create a **second output authority** alongside the U-RT-123 substrate (violates one-source-of-truth).
- **The follow-on's grounding question:** does a RECONCILER resume's `accumulated` reconstruct from the U-RT-123 `partial_state` (derive-from-the-reconciler-substrate), or from the EngineOutputStore (store-reuse, accepting the two-authorities cost)? Probe the reconciler resume path before wiring either. Do NOT blindly reuse the store.

## 4. As-built (this arc)

- `harness-cp/src/harness_cp/workflow_driver.py` — new `_FINAL_STATE_RECONSTRUCT_ENGINE_CLASSES = {ESR, WAL, SAVE_POINT_CHECKPOINT}` constant; producer + seed gates unified onto it.
- `harness-runtime/src/harness_runtime/types.py` — `engine_output_replay` docstring clarified (class-agnostic store also backs final_state reconstruction); no behavior change.
- `design-substrate/Spec_Control_Plane_v1_79.md` + clearance marker.
- tests: `harness-cp/tests/test_workflow_driver.py` — `test_reconstruct_final_state_round_trips_through_store_save_point` (the blocking producer-half witness, RED-without-fix) + `test_reconstruct_final_state_reconciler_out_of_scope_degrades` (reframed from the old SAVE_POINT-degrade test).
- `.harness/arc-ledger.yaml` — flip the registered arc → closed (SAVE_POINT slice) + register the RECONCILER follow-on; snapshot bump.
