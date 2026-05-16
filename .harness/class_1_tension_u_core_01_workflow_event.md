# Class 1 Tension — U-CORE-01 `WorkflowEvent` payload model unmaterializable

*Phase 7 sub-phase 7b. Fork detected at U-CORE-01 execution-time. Routed per
`CLAUDE.md` §4.3 + `phase-7-implementation` SKILL.md §6. RESOLVED — operator
ruling 2026-05-15.*

---

## 1. Identification

| Field | Value |
|---|---|
| Tension ID | Class-1 / U-CORE-01 / `WorkflowEvent`-payload |
| Sub-phase | 7b (per-axis-stream implementation) |
| Surfaced at | Landing U-CORE-01 (`harness-core` shared-type carrier) |
| Class | **1** — architectural defect; plan signature cannot be materialized at target stack |
| Routing target | Phase 6 plan revision — `Implementation_Plan_Harness_Core` v1.0 → v1.1 (in-CLI) |
| Status | **RESOLVED** 2026-05-15 — carrier-thin reading ratified by operator |

## 2. The defect

`Implementation_Plan_Harness_Core_v1_0.md` §2 declared, in the U-CORE-01
signature block:

```
model WorkflowEvent { event_class: WorkflowEventClass; ... per C-CP-05 §5.2 ... }
```

This is an unmaterialized placeholder, not an implementation-grade signature.
v1.0 acceptance criterion #4 required "a payload model carrying the §5.2
per-class minimum attribute set." Faithful materialization is not possible as a
`harness-core` carrier type:

1. **Transitive CP-axis dependency.** C-CP-05 §5.2's per-class minimum
   attribute set references four CP-axis types U-CORE-01 does not own and the
   carrier map did not assign to `harness-core`:
   - `engine.class` — C-CP-09 5-value enum (CP-axis, U-CP-15 landed)
   - `step.kind` — 5-value enum (`declarative-step / inference-step /
     tool-step / HITL-step / sub-agent-dispatch`)
   - `resumption.kind` — C-CP-08 per-engine-class enum (CP-axis, U-CP-19)
   - `lease.*` namespace — C-CP-05 §5.3 (`lease.key`, `lease.holder`,
     `lease.ttl_ms`, `lease.mechanism` 6-value enum, `lease.release_cause`
     4-value enum)
2. **Partial §5.2 coverage.** C-CP-05 §5.2 declares per-class attribute rows
   for only 5 of the 8 event classes (`workflow.start`, `step.boundary`,
   `lease.acquired`, `lease.released`, `workflow.resumption`). The other three
   (`fallback-trigger`, `retry-attempt`, `breaker-trip`) draw attributes from
   C-CP-03 §3.5 namespaces, not §5.2.
3. **Collides with the R4 hand-off.** v1.0 §2's own reconciliation note hands
   the lifecycle-event surface to CP U-CP-10. CP plan v2.6 (R4, applied)
   confirms U-CP-10 owns the lifecycle-event span-name-metadata map and
   consumes `WorkflowEventClass`. A full `WorkflowEvent` payload in
   `harness-core` would leave U-CP-10 with nothing to own.

Materializing the payload in `harness-core` would therefore (a) pull four
CP-axis types across the package boundary against the carrier-map T2 verdicts,
and (b) break the carrier-thin intent of U-CORE-01 (cross-cutting *shared
types*, not axis domain models).

## 3. Halt + routing

Per `phase-7-implementation` SKILL.md §6 ("Plan signature cannot be
materialized at target stack → Class 1 → Phase 6 plan revision"), U-CORE-01
landing halted at the `WorkflowEvent` signature. The 11 other U-CORE-01
declarations (`DeploymentSurface`, `PersonaTier`, `WorkflowEventClass`, the 9
identity aliases) were verified materializable and verbatim-conformant — see §5.
Surfaced to operator.

## 4. Operator ruling — 2026-05-15

**Reading selected: carrier-thin.** Among three readings presented:

| Reading | Disposition |
|---|---|
| Carrier-thin | **SELECTED.** U-CORE-01 declares `WorkflowEventClass` (the cross-cutting enum) and no `WorkflowEvent` payload model. |
| Carrier-thick | Rejected — inlines 4 CP-axis enums into `harness-core`; collides with carrier-map T2; breaks the U-CP-10 hand-off. |
| Carrier-shell | Rejected — `dict[str, Any]` payload satisfies acc #4 only literally; loses `pyright` nominal precision; worst-of-both. |

**Consequence.** U-CORE-01 lands carrier-thin (the 11 clean declarations). The
C-CP-05 §5.2 per-class minimum attribute set is a span-emission-site contract
owned by the CP axis, not a `harness-core` carrier type.

## 5. Verbatim conformance of the 11 landed declarations

| Type | Spec basis | Verbatim values verified |
|---|---|---|
| `DeploymentSurface` | C-AS-09 §9.1 matrix | `local-development`, `self-hosted-server`, `managed-cloud` ✓ |
| `PersonaTier` | C-AS-09 §9.4 override-scope table | `solo-developer`, `team-binding`, `multi-tenant-compliance` ✓ |
| `WorkflowEventClass` | C-CP-05 §5.1 event class table (8 rows) | `workflow-start`, `step-boundary`, `fallback-trigger`, `retry-attempt`, `breaker-trip`, `lease-acquired`, `lease-released`, `resumption` ✓ |
| 9 identity aliases | C-IS-05 §5 / C-CP-05 §5 / C-CP-13 §13.4 / C-AS-03 §3 / C-CP-01 §1 + 2 plan-internal | `str`-newtypes; spec defers concrete format → `str` per acc #6 ✓ |

C-CP-05 §5.1 read from `Spec_Control_Plane_v1_2.md` lines 498–509 (§5.1
preserved verbatim into v1.3 per the v1.3 change-note).

## 6. Resolution applied

- `Implementation_Plan_Harness_Core_v1_1.md` filed — v1.0 §2 `WorkflowEvent`
  payload model struck; acc #4 reduced to the enum; test
  `test_workflow_event_payload_matches_spec_5_2` struck; §1/§4 updated. §0.4
  records the change.
- `CLAUDE.md` §2.4 pointer updated v1_0 → v1_1.
- U-CORE-01 landed carrier-thin in `harness-core`.

## 7. Flagged follow-ups

| ID | Item | Owed at |
|---|---|---|
| F-1 | C-CP-05 §5.2 per-class minimum attribute *schema* — coverage reverts to the CP plan. Verify §5.2 is covered at CP lifecycle-event span-emission units when they land. Not owed by `harness-core`. | CP emission-unit landings |
| F-2 | `Implementation_Plan_Control_Plane_v2_6.md` §0 spec-inventory line references "`WorkflowEventClass`/`WorkflowEvent`" as U-CORE-01-declared. The `WorkflowEvent` reference is now stale (mechanical back-reference fix). | Next CP plan touch |

## 8. Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_tension_u_core_01_workflow_event.md` |
| Authored | Phase 7 7b, 2026-05-15 |
| Resolution authority | Operator ruling 2026-05-15 (carrier-thin) |
| Status | RESOLVED — cleared for U-CORE-01 carrier-thin landing |
