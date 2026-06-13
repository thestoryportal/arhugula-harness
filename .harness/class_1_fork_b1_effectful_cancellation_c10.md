# Class 1 Fork — B1 cascade-cancel effectful-cancellation (C10)

**Filed + RESOLVED:** 2026-06-13 · R-FS-1 arc #3 (B1-spec-1), design-phase posture. Class 1 (the one genuinely-contested B1 design surface; C1 orchestration ⊥ C10 action-safety/blast-radius). Resolved by a **genuine dyadic C1⊥C10 council** + decorrelated review; **no operator gate owed** (the §13.4 discriminator places the resolution as composing committed primitives → not a meaningful-architecture change).

**Status:** ✅ RESOLVED → Reading A (dispatch-boundary-bounded; no new primitive). Applied at `Spec_Control_Plane_v1_32.md` §25.15. Council record: `.harness/council/r-fs-1-b1-cascade-cancel/` (charter + C1/C10 contributions + DELIVERABLE).

## §1 The fork

`asyncio.TaskGroup` cancellation aborts the Python task but CANNOT roll back an already-dispatched **effectful** step (a `TOOL_STEP` whose sandbox call already hit the world — file written / email sent / API mutated; or a billed `INFERENCE_STEP`). So what is `cascade-cancel`'s complete, honest semantic under fan-out?

| Reading | Semantic | Assessment |
|---|---|---|
| **A — dispatch-boundary-bounded** | Cancel only not-yet-dispatched siblings; in-flight steps run to completion/timeout + recorded with a discriminating persisted `terminal_status`; gate high-blast-radius effectful steps **before** dispatch via the committed C-AS-02 → C-CP-19 → C-CP-16 chain. NO new primitive. | **CHOSEN.** |
| B — compensation/saga rollback-after | A net-new rollback-after primitive. | **Rejected on the merits** (independent of I-6): you cannot un-send an email; a "rollback" of an irreversible effect would be a *lie in the audit*. The reversible classes are already served by per-step rollback APIs + C3. Rollback-of-an-already-sent-effect is not a coherent operation → **out of cascade-cancel's domain**, not a deferral. |

## §2 Council resolution (genuine dyadic C1⊥C10)

Both voices independently reached **A** and the same reframe (rollback-of-sent-effects is incoherent → A is COMPLETE, not a defer). Distinct load-bearing contributions:
- **C1 (orchestration):** the harness already owns this primitive — the **DRAIN protocol** (`workflow_driver.py` drain sites; spec §25.4 "NO mid-step interruption"); cascade-cancel is its fan-out generalization → composes committed substrate. Completeness = total persisted terminal-state coverage, NOT universal rollback.
- **C10 (action-safety):** only `external-irreversible` is genuinely dangerous, and it **cannot reach silent dispatch** (`EXTERNAL_IRREVERSIBLE → tier-4 → gate_level max() → mandatory HITL`, C-AS-02/ADR-F4 → C-CP-19 §19.1 → C-CP-16). Plus the sharpest obligation: **the D1.b buffered path must defer the ledger *write*, never the *gate*** (else fan-out bypasses pre-dispatch HITL), and **`terminal_status` must discriminate** clean-cancel vs effect-landed.

Reconciliation: the voices agree on every not-yet-dispatched step; they differ only on the in-flight effectful step → "cancel" is defined as **cancel-before-dispatch + record-after-dispatch**. C1 owns WHERE the gate sits (pre-dispatch, where cancellation is clean); C10 owns WHAT it enforces (tier policy).

3-way decorrelated convergence: advisor (transcript-aware; produced the reframe) + C1 + C10. Out-of-family Codex fires at the arc-level pre-merge review.

## §3 Discriminator applied (§13.4) → resolve, do NOT surface

The resolution composes **only** committed primitives — DRAIN protocol (§25.4), C-AS-02 four-tier sandbox floor (ADR-F4), C-CP-19 §19.1 gate-level max(), C-CP-16 4-response palette, the Route-Y `branch_metadata` sidecar, branch-scoped idempotency keys. **Zero net-new primitive, zero ADR change, zero six-field/hash-chain change** → not a meaningful-architecture gate → resolved + spec'd (the 8 obligations at §25.15.2). No `dry_run`/`preview` primitive invented — the committed realization is the C-CP-16 EDIT/REJECT palette + the `_hitl_required` pre-dispatch ask.
