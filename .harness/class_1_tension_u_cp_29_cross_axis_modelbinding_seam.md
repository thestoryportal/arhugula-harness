# Class 1 Tension — U-CP-29 `resolve_brief_authoring_model_binding` cross-axis ModelBinding seam

**Status:** 🟡 PARTIAL — U-CP-29 inheritance table LANDED; acc #3 delegator struck.
**Filed:** 2026-05-16 (Phase 7 7b, CP axis-stream).
**Unit:** U-CP-29 — brief-authoring model-binding inheritance table.
**Plan:** `Implementation_Plan_Control_Plane_v2_1.md` §2.5 U-CP-29.

## What landed

`InheritanceRule` (2-value enum), `BriefAuthoringInheritance` record,
`BRIEF_AUTHORING_INHERITANCE` (4-entry table, one per `WorkloadClass`),
`inheritance_for` accessor — at
`harness-cp/src/harness_cp/brief_authoring_inheritance.py`. Accs #1, #2, #4
fully covered.

## What is struck (halt-route-split-AC)

Acc #3 prescribes `resolve_brief_authoring_model_binding(workload_class,
stage_id) -> ModelBinding` "delegates to U-AS-29 catalog; this unit declares
inheritance rule only".

The delegator cannot be materialized at 7b because of a **cross-axis type
collision**:

- U-CP-29's signature return type `ModelBinding` is the **U-CP-00c**
  `ModelBinding` — fields `(provider, model)` — per CP plan v2.8 §11.1
  registry (homed at U-CP-00c, consumed by U-CP-13/14/29/50).
- U-AS-29's landed catalog (`harness_as/engine_class_composition.py`,
  `MODEL_BINDING_MATRIX` / `model_binding(...)`) returns an **AS-axis**
  `ModelBinding` — fields `(primary_model, qualifier, cap)` — a structurally
  distinct type that happens to share the name.

The delegator would have to convert the AS `ModelBinding` to the CP
`ModelBinding`. The two shapes are not field-compatible; the conversion rule
is nowhere specified. This is a cross-axis seam reconciliation, covered by
CXA v2.1 §2.3.3 (CP→AS composition bucket) — resolved at **sub-phase 7c**, not
a 7b unit-internal surface.

The plan itself scopes U-CP-29 to "declares inheritance rule only" (acc #3),
so striking the delegator body honors the plan's own scope statement. The
delegator + `test_delegates_to_u_as_29` are struck.

## Routing

Class 1 — cross-axis seam. Routes to sub-phase 7c CXA composition (CP→AS
bucket): the 7c pass reconciles the CP `ModelBinding` (U-CP-00c) and AS
`ModelBinding` (U-AS-29) shapes and instantiates `resolve_brief_authoring_model_binding`
as a CXA seam. No design-substrate revision implied — the type-shape
divergence is a known carrier-map item.

---

## Audit reconciliation (2026-05-20)

**Verified status:** DEFERRED-PARTITION

**Resolving artifact / evidence:** U-CP-29 inheritance table landed at brief_authoring_inheritance.py. AC #3 delegator struck (cross-axis CP ModelBinding vs AS ModelBinding shape collision) — routed to 7c CXA composition as bounded partition.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
