# Council Deliverable — cascade-cancel effectful-cancellation (C10 fork) — RESOLVED

**Arc:** R-FS-1 arc #3 (B1-spec-1) · **Convened:** 2026-06-13 · **Voices:** C1 orchestration ⊥ C10 action-safety/blast-radius (genuine dedicated-agent invocations; contributions verbatim at `01-council/contributions/`).

## Disposition: **Fork (A) — RESOLVED (not carried open)**

`cascade-cancel` is **dispatch-boundary-bounded**: it cancels only not-yet-dispatched sibling steps; an in-flight step at cancel-time runs to its own completion/timeout and is recorded; high-blast-radius effectful steps gate **before** dispatch via the committed chain. **No new primitive.** Fork (B) compensation/saga is **rejected on the merits** (not merely on I-6): you cannot un-send an email — rollback-of-an-already-sent-effect is not a coherent operation, so it is **out of cascade-cancel's domain**, not deferred. A is therefore a **complete honest semantic** under the FULL-SPEC directive.

## Both voices converged on A — and on the reframe

| | C1 (orchestration) | C10 (action-safety) |
|---|---|---|
| Verdict | Fork A | Fork A, COMPLETE |
| Load-bearing grounding | The harness **already owns this primitive — the DRAIN protocol** (`workflow_driver.py` drain sites; spec §25.4 "NO mid-step interruption"). cascade-cancel is its fan-out generalization → composes committed substrate, not a new primitive. | Only `external-irreversible` is genuinely dangerous, and it **cannot reach silent dispatch**: committed chain C-AS-02 `sandbox_tier_floor` (ADR-F4 four-tier; `EXTERNAL_IRREVERSIBLE → tier-4`) → C-CP-19 §19.1 `gate_level` max() → C-CP-16 mandatory HITL. At cancel-time an irreversible step is either not-yet-approved (cleanly cancellable) or operator-approved-and-in-flight (operator already accepted the blast radius). **No silent-uncompensated-effect hole for the dangerous class.** |
| Completeness reframe | completeness = **total persisted terminal-state coverage with no silent gap**, NOT universal rollback. | a "rollback" of an irreversible effect would be a **lie in the audit**; the reversible classes are already served by per-step rollback APIs + C3. |

## Cross-read (B-stage) — the tension reconciles

The voices **agree on every not-yet-dispatched step** (both cancel it). They **differ only on the in-flight effectful step**: C1 frames "cancel" as a clean total abort; C10 insists the word "cancel" must be defined as **cancel-before-dispatch + record-after-dispatch** or the abstraction lies (pretending an in-flight send got cancelled when it actually sent *is* the silent-effect failure mode). Reconciliation: **C1 owns WHERE the gate sits (pre-dispatch, where cancellation is clean); C10 owns WHAT it enforces (tier policy).** The effectful residual is not deferred work — it is C10's standing domain by construction.

Seam guards held (no cross-voice absorption): barrier-deadline (C1) ≠ step-timeout (C9/T-perm-3); compensation = a forward action (C4's domain), which still cannot un-send.

## Discriminator applied (E4 gate) → resolve, do NOT surface

The resolution **composes entirely with committed primitives** — DRAIN protocol (§25.4), C-AS-02 sandbox four-tier floor (ADR-F4), C-CP-19 §19.1 gate-level max(), C-CP-16 4-response palette HITL, the Route-Y branch-metadata sidecar (precedented D-derivative), branch-scoped idempotency keys (CP-side key composition). **Zero net-new primitive. Zero ADR change. Zero six-field/hash-chain change.** → **Not a meaningful-architecture change → resolve + spec + proceed.** No operator gate owed (per CLAUDE.md §13.4 discriminator + `[[feedback-gate-only-on-meaningful-architecture-change]]`).

## The explicit cascade-cancel reach the spec MUST state (the 8 obligations)

1. **Dispatch-boundary-bounded.** `cascade-cancel` cancels only not-yet-dispatched sibling steps (`asyncio.TaskGroup` cancellation of pending branch tasks). An in-flight step at cancel-time is NOT cancelled — it runs to its own completion or barrier-deadline timeout.
2. **No-gate-bypass-by-buffering (C10 #2 — highest value).** The D1.b buffered/deferred-append branch path defers the ledger **write**, never the **gate**: each branch evaluates the pre-dispatch HITL/sandbox-tier gate before each effectful step **exactly as the linear path does**. A naive impl that defers step machinery to the drain would gate *after* the effect — foreclosed.
3. **Audit-completeness (no silent landed effect).** Every dispatched effectful step has its own recorded step ledger entry, regardless of the branch's terminal disposition. No landed effect is ever silent.
4. **Discriminating `terminal_status` (C10 #3).** The Route-Y `branch_metadata` sidecar's `terminal_status` discriminates the branch disposition: `cancelled` ⟹ branch terminated at a **not-yet-dispatched** boundary (no effectful dispatch at the termination point); `completed` / `timed_out` ⟹ the branch's in-flight step ran (effect may have landed) and is recorded. A bare "cancelled" with no discrimination would make audit-as-primary-defense hollow.
5. **High-blast-radius pre-dispatch gating.** Effectful steps gate before dispatch via the committed chain (C-AS-02 four-tier `sandbox_tier_floor` → C-CP-19 §19.1 `gate_level` max() → C-CP-16 HITL); `external-irreversible → tier-4 → mandatory HITL`. cascade-cancel composes this gate, does not re-invent it.
6. **Run-level status.** `cascade-cancel` on a branch failure → run-level `RunStatus = FAILED`. (Distinct from `proceed` → `PARTIAL` + `degraded=true`, and `pause` → `PAUSED`. `PARTIAL` belongs to `proceed`, NOT cascade-cancel — advisor-caught, confirmed by C1.)
7. **Resume-idempotency.** Branch-scoped idempotency keys (`+ branch_path` in the key composition) so `api.resume` reads each branch's persisted `terminal_status` and MUST NOT re-dispatch a branch that is `cancelled` / `completed` / `timed_out`.
8. **`pause` / `proceed` composition.** `pause` halts the fan-out at a HITL/pause boundary (composes with C-RT-30 `api.resume`); `proceed` records the branch failure and lets siblings finish, aggregator sees a partial set with `degraded=true` (Google SRE graceful-degradation).

## Decorrelated review — 3-way convergence

advisor (transcript-aware, in-family — produced the reframe) + C1 (genuine) + C10 (genuine) all independently reached **Fork-A-is-complete**. Out-of-family Codex fires at the arc-level pre-merge review (E2/E3 folded into B1-spec-1's adversarial + codex pass), not separately here. No divergence to dig into.

## Honesty flags (carried into the spec change-note)

- No `dry_run`/`preview` primitive exists today (grep empty); the committed realization of "dry-run-then-approve" is the C-CP-16 EDIT/REJECT palette + the `_hitl_required` ask. The spec states the *obligation* (gate before dispatch); it does not invent a preview primitive.
- The pre-dispatch gate is a committed **contract**; `cascade_policy` is **declared-but-unconsumed** at HEAD (`topology_pattern.py:67`). The B1-impl obligation is to **wire** the fan-out path to the committed gate — not new design.
