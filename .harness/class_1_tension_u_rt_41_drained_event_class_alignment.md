# Class 1 (halt-execution) — U-RT-41 `WorkflowEventClass.DRAINED` alignment

**Filed at:** U-RT-41 PARTIAL-LAND (2026-05-19)
**Locus:** `Spec_Harness_Runtime_v1.md` C-RT-11 §11 vs `harness_core.workflow_event_class.WorkflowEventClass`
**Status:** OPEN — operator decision pending
**Routing:** Phase 5 spec revision (CP spec C-CP-05 §5.1 + harness_core schema) OR Phase 5 runtime spec revision (C-RT-11 §11 strike) OR defer
**Spec authorization:** §16 open question #9 — "Surface as Class 1 fork at U-RT-41 landing if alignment fails"
**Precedent:** U-RT-30 trace-storage PathClass gap (same halt-route-split-AC pattern)

## Defect

C-RT-11 §11 step 2 commits the runtime to emit a `WorkflowEventClass.DRAINED`
event on drain detection. The canonical `WorkflowEventClass` enum at
`harness-core/src/harness_core/workflow_event_class.py:35` is "closed at
cardinality 8" per its docstring (mirroring C-CP-05 §5.1 verbatim):

| Value | String |
|---|---|
| WORKFLOW_START | `workflow-start` |
| STEP_BOUNDARY | `step-boundary` |
| FALLBACK_TRIGGER | `fallback-trigger` |
| RETRY_ATTEMPT | `retry-attempt` |
| BREAKER_TRIP | `breaker-trip` |
| LEASE_ACQUIRED | `lease-acquired` |
| LEASE_RELEASED | `lease-released` |
| RESUMPTION | `resumption` |

No `DRAINED` value. No semantic-near-neighbor among the 8 (all 8 are
workflow-lifecycle / breaker / lease / resumption events; none signals
drain-complete). Adding `DRAINED` would amend CP spec C-CP-05 §5.1 +
the harness_core enum (8 → 9) — a Phase 5 spec revision.

Spec §16 open question #9 explicitly authorizes split: "If landed
`harness_core.workflow_event_class` enum doesn't carry `DRAINED`,
U-RT-41 lands an aligned name. Surface as Class 1 fork at U-RT-41
landing if alignment fails." No alignment available among the 8.

## What was landed (PARTIAL-LAND scope)

- LANDED: `RuntimeLifecycleEventEmitter` for the 8 existing
  `WorkflowEventClass` values. The runtime can emit any of the 8
  canonical events; consumers (workflow execution at U-RT-42+) bind
  emit calls to the lifecycle loop's hook surfaces.
- STRUCK: C-RT-11 §11 step 2 `WorkflowEventClass.DRAINED` emit.
  Drain remains observable via the **two other** surfaces C-RT-11 §11
  already commits — `ctx.drained_flag` (asyncio.Event) at step 1 +
  `RunResult.status == 'drained'` at step 3. The third (DRAINED event
  emit) is the only unmaterialized step.

## Why drain observability survives this strike

C-RT-11 §11's drain sequence has three observable surfaces:

1. **`drained_flag.set()`** — primary drain signal. Polled at every
   lifecycle boundary by the CP loop. Already materialized
   (`HarnessContext.drained_flag: asyncio.Event` at stage 0).
2. **`WorkflowEventClass.DRAINED` emit** — observability event. **UNMATERIALIZED.**
3. **`RunResult.status='drained'`** — terminal-return signal. Already
   spec-committed at C-RT-09 §9; materializes at U-RT-42.

Surfaces (1) + (3) cover the operator-visible drain semantics; surface
(2) is a duplicative observability emit. Striking it preserves drain
visibility while avoiding the silent CP-spec amendment at runtime
landing (which would violate X-AL-3 — no silent H_T design extension
at Phase 7).

## Routing options (operator decision pending)

### Option A — Phase 5 CP spec + harness_core schema revision

Amend C-CP-05 §5.1 to add `DRAINED` (9th lifecycle event); amend the
landed `harness_core.workflow_event_class.WorkflowEventClass` enum (8 →
9). Cascade to every CP / OD / runtime site that references the enum
cardinality (count-based assertions). Spec-canonical alignment per
Pattern P1-PHASE-5.

- Blast radius: medium (CP spec + core enum + all cardinality-aware
  consumers); requires Phase 5 spec revision-pass
- Time: days
- Defect risk: medium (cardinality propagation must reach every
  consumer; cascade discipline required)

### Option B — Phase 5 runtime spec revision: strike DRAINED emit (recommended)

Amend C-RT-11 §11 step 2 to remove the
`WorkflowEventClass.DRAINED` emit. Drain remains observable via
`drained_flag` (surface 1) + `RunResult.status='drained'` (surface 3).
Add a sentence under "Invariants" noting that drain observability
lives at those two surfaces, not at the lifecycle-event emit.

- Blast radius: smallest (runtime spec only; no CP/core touch)
- Time: hours
- Defect risk: low (preserves existing drain surfaces; removes
  duplicative emit)
- Aligns with the spec's own framing ("event-name may need
  landed-axis alignment per Pattern P1-PHASE-5 discipline at U-RT-41
  landing")
- **Recommended**

### Option C — Defer the DRAINED emit to a future runtime unit

Land U-RT-41 with the 8-value emitter only; track the DRAINED emit as
a deferred sub-unit (U-RT-41.1) pending a future CP spec revision.

- Blast radius: smallest at this landing; defers the question
- Defect risk: keeps the gap open across L8 / L9; future workflow-
  execution units (U-RT-42+) may need to know whether the DRAINED
  emit is materialized or struck before they wire drain
  observability — increases coordination cost

## Acceptance criterion split applied

- AC #1 (LifecycleEventEmitter Protocol concretized; emits 8 canonical
  `WorkflowEventClass` values; satisfies Protocol type-check) — LANDED
- AC #2 (C-RT-11 §11 step 2 `WorkflowEventClass.DRAINED` emit) — STRUCK;
  routed to this Class 1 record

## See also

- `[[fork-trace-storage-pathclass-gap]]` (U-RT-30 — halt-route-split-AC precedent)
- `[[fork-cp-is-wiring-gaps]]` (U-RT-35 — halt-route-split-AC precedent)
- `[[halt-route-split-ac-pattern]]` (the workspace pattern)
- `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-3 (no silent design extension)
- `Spec_Harness_Runtime_v1.md` §16 #9 (explicit Class 1 authorization)
