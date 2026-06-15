# Council Charter — U-RT-123 CAS-lease realization (R-FS-1 E-impl-3b)

*Genuine multi-agent council per `.harness/council/council-workflow.harness-aware.yaml`. Additive-only process-substrate (NOT design-substrate; the spec v1.33 §7.4 already cleared the reconciler substrate to impl-discretion — this council decides the HOW, no spec amendment). Posture: Phase-7 impl-design (informs `harness-runtime/src` U-RT-123).*

## Spine-tension

**Correctness-vs-honest-substrate-assumption.** A hand-rolled (I-6, no vendored etcd/K8s) CAS lease for the RECONCILER_LOOP `EnginePauseResumeSubstrate` must be genuinely SAFE against concurrent double-execution at the §7.2 multi-host surfaces (self-hosted-server + managed-cloud) — C10/C9 — while only assuming shared-storage/liveness atomicity an operator HONESTLY has (no silent infra assumption) — C11. The static owner-token is defeated (the [P1]); the real discriminator between crash-retry and concurrent-distinct is liveness/time.

## The question (verbatim)

How to realize the spec-named "etcd compare-and-swap lease" (C-CP-07 §7.1 row 4; §7.4 floor (iii); v1.33 §7.4 reconciliation note) for U-RT-123 on a filesystem substrate, distinguishing:
- (a) **crash-then-retry** by the same logical reconciler (sequential, prior process DEAD) → MUST re-enter (floor (i) durable replay across restart);
- (b) **two concurrent distinct** reconcilers (both LIVE) → exactly ONE proceeds; the other ABORTs `ABORT_REVALIDATION_FAILED`.

## Verified premises (this session, body-read)

1. **[P1] real.** `resume_request_actor` defaults to the shared `harness-runtime` actor (`engine_recovery_loop.py:167`); `resume_event_id`/`resume_attempt_count` are deterministic/hardcoded (`workflow_driver.py:1632-1633`). Two concurrent distinct reconcilers share the owner token → both pass same-owner re-entry → both re-execute.
2. **Floor (ii) F2 idempotency does NOT cover the concurrent case.** The resume EFFECT is the workflow re-executing steps (`workflow_driver.py:1681`, after a non-abort outcome); `idempotency_key` is only on the `cp.resume-attempted` AUDIT entry. So the CAS lease is the SOLE guard against concurrent double-EXECUTION. (Option "drop lease, rely on idempotency" REFUTED by advisor + body-read.)
3. The durable-log + torn-write recovery + gap-safety + per-workflow flock parts of the WIP substrate (commit `0c0bf66`) are SOLID (14 tests green, pyright 0/0/0) and reusable; ONLY the CAS-lease cross-process correctness is open.

## Convening (5 voices)

| Role | Voice | Why |
|---|---|---|
| Primary | C9 reliability-recovery | crash-recovery lease correctness — the domain center |
| Primary | C10 action-safety/blast-radius | double-execution = the blast-radius concern; minimum SAFE mechanism |
| Primary | C11 operator-loop/local-deployment | honest substrate/liveness assumption; O-E3-2 admissibility |
| Consultant | C1 orchestration/lifecycle | engine resumption lifecycle semantics |
| Consultant | C5 validation-contract | ResumeOutcomeKind / PathClass / X-AL-3 cleanliness |

## Constraints

FULL-SPEC (no scope-to-single-host defer; cross-host is a BUILD); I-6 hand-rolled; X-AL-3 (map onto closed ResumeOutcomeKind); IS-AL-1 (PathClass.STATE_LEDGER, no IS extension). Pre-bind first cites to `Spec_Control_Plane_v1_33.md` + ADR-D1 v1.2 + `.harness/r-fs-1-e3-plan-decomposition.md`.

## Stage ledger

| Stage | Status |
|---|---|
| E1 A1 primaries (blind) | DONE (C9/C10/C11) |
| E1 A2 consultants (react) | DONE (C1/C5/C3) |
| E1 B cross-read debate | DONE (reconciled-to-internal-zero) |
| E2 adversarial #1 | DONE (F-01/F-02 Class-1 + F-03..06; `02-adversarial/REVIEW-1.md`) |
| E2b+E3b consolidated reconcile (+ E3 Codex+advisor) | DONE (4-way convergence; `04-reconciliation/RECONCILE.md`) |
| E4 gate | LIGHT (orchestrator residual sweep + byte-confirms; full adversarial #2 waived — 4-way converged + decision is operator's by construction per advisor) |
| DELIVERABLE → operator ratification (the one meaningful gate) | **RATIFIED 2026-06-15: hand-rolled full ladder, I-6 preserved.** Build A now (U-RT-123); F-1 + F-2 + fenced bounded-synchrony auto-recovery lease = committed FULL-SPEC build arcs. C (relax I-6/vendor consensus) ELIMINATED as spec-violating (contradicts v1.33 + FULL-SPEC "HOW stays I-6 hand-roll"). |

## HIL posture

Autonomous council per standing operator directives (`[[feedback-gate-only-on-meaningful-architecture-change]]` + `[[feedback-autonomous-loop-dont-stop-to-ask]]`); ONE gate at the consolidated DELIVERABLE before BUILD. Genuine dedicated-agent invocation for every voice/reviewer.
