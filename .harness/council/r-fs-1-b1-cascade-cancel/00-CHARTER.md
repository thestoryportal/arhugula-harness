# Council Charter — R-FS-1 B1-spec-1 · cascade-cancel effectful-cancellation (C10 fork)

**Convened:** 2026-06-13 · **Arc:** R-FS-1 arc #3 (B1-spec-1) · **Posture:** design-phase (CP spec amendment).
**Spec followed:** `.harness/council/council-workflow.harness-aware.yaml` (dyadic-focused; HIL gates run autonomously per standing operator directive — `[[feedback-autonomous-loop-dont-stop-to-ask]]` + `[[feedback-gate-only-on-meaningful-architecture-change]]`).

## Nameable-tension gate — PASS

- **C1 (orchestration)** wants `cascade-cancel` to be a *clean, complete cancel* of the fan-out — siblings stop, the run fails fast, the orchestration semantics are simple.
- **C10 (action-safety / blast-radius)** wants *zero silent uncompensated side effects* — a cancelled branch must not leave the world half-mutated with no audit trace.

The tension is genuine and pre-nameable → council-eligible (CLAUDE.md §10.9 amendment 1).

## Layer + voices (CP axis; dyadic)

Per `layer_voice_map` CP primaries `[c1,c5,c6,c9]` + consultant `c10`. The fork is squarely **orchestration-lifecycle ⊥ security-blast-radius** → promote **C10 to first-class** (the evidence is squarely its domain) and convene the **C1⊥C10 dyad** (the design's own prescription: "dyadic C1⊥C10 council warranted"). C5/C6/C9 not convened — no nameable distinct tension from them on *this* fork (validation-contract/cost/reliability are downstream of the cancel-reach decision, not in tension with it).

## Spine tension

**completeness-of-cancel (C1) vs no-uncompensated-effect (C10)** — and whether the honest resolution composes with committed primitives (sandbox 4-tier blast-radius + HITL 4-response palette) or requires a net-new primitive (saga/compensation).

## The fork

- **(A)** Restrict `cascade-cancel` to **pre-dispatch boundaries** — cancel only not-yet-dispatched sibling steps; in-flight effectful steps run to their own completion/timeout and are recorded with a persisted `terminal_status`; gate high-blast-radius effectful steps **before** dispatch (compose with the committed sandbox 4-tier blast-radius + HITL gate). NO new primitive. Corpus: cancel-before-dispatch / dry-run-then-approve; Google SRE graceful degradation.
- **(B)** Add **compensation/saga rollback-after** semantics — a net-new primitive.

## Hard constraints (the council MUST honor)

- **I-6** hand-roll — NO `temporal`/`langgraph`/saga frameworks. A hand-rolled saga is still a net-new primitive.
- **ADR-F2** single-threaded ledger writer (the audit substrate).
- Committed **sandbox 4-tier blast radius** + **HITL 4-response palette** are the composition substrate.
- **FULL-SPEC directive** — nothing deferred. "Carry open" is NOT a valid close. The resolution must be a complete honest semantic.

## Discriminator for gating (applied at E4)

If the resolution **composes with committed primitives** → resolve + spec + proceed (not a meaningful-architecture change). If it genuinely **requires a net-new primitive** (saga/compensation) → that IS the meaningful-architecture gate → surface to operator.

## Ledger

- `01-council/contributions/` — per-voice genuine contributions (C1, C10), independent + blind.
- `02-adversarial/REVIEW-cp-v1.32.md` — pre-merge adversarial review (genuine invocation).
- `DELIVERABLE.md` — resolved disposition + the explicit cascade-cancel reach the spec must state. **The B-stage cross-read is folded into DELIVERABLE.md §"Cross-read (B-stage)"** (dyadic convening — C1 + C10 each named the other's position there; no separate `cross-read.md` file for a 2-voice convening).
