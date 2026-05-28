# Class 1 Tension — U-CP-17 `EngineClassPreferences` carrier homed at a blocked unit

**Status:** ✅ PARTIALLY-CLOSED (verified workspace-wide audit 2026-05-20; status-line refreshed 2026-05-27) — partial-lands at `workload_binding_engine_class_selection.py` (4/5 steps of §7.3 procedure; step 4 'apply operator preferences' struck). `EngineClassPreferences` re-homing is DEFERRED-PARTITION resolving at future CP plan revision designating permanent home — not open architectural defect. Species 3 stale-carry per workflow v1.9 §7.4.7.2.

**Filed:** 2026-05-16
**Filer:** phase-7-implementation (CP axis-stream, 7b)
**Unit:** U-CP-17 — workload-binding-time engine-class selection (5-step procedure)
**Disposition:** PARTIAL LAND + AC-strike (halt-route-split-AC pattern)
**Fork class:** Class 1 (architectural — type carrier homed at an un-landable unit)

## Surface

U-CP-17 (`Implementation_Plan_Control_Plane_v2_1.md` §2 L959, preserved
verbatim through v2.6) declares:

```
record WorkloadBindingSelectionInput {
  workload_class      : WorkloadClass
  deployment_surface  : DeploymentSurface
  persona_tier        : PersonaTier
  operator_preferences: Optional<EngineClassPreferences>
}
```

and acceptance criterion #1 step 4 — "Apply operator preferences if declared."

`EngineClassPreferences` is NOT one of the 9 deferred structured types. It is a
**record homed at U-CP-27** per the v2.6 carrier-map (`Implementation_Plan_
Control_Plane_v2_6.md` L221 + L584): "`EngineClassPreferences` | record |
U-CP-27 | U-CP-27 internal | CP §7.4". The carrier-map column 3 marks it
"U-CP-27 internal" — it has no cross-unit consumer row, yet U-CP-17's v2.1
signature consumes it by type. This is a latent plan defect: the v2.6 carrier
homing did not reconcile the U-CP-17 hidden consumption.

U-CP-27 is a **blocked deferred-consumer root** (one of the 15 deferred-type
consumers per the 7b kickoff). U-CP-17 therefore transitively depends on a
blocked unit through the `EngineClassPreferences` type — a dependency NOT
present in U-CP-17's `Depends on:` line ([U-CP-15, U-CP-16]). It surfaced from
the unit body.

`EngineClassPreferences` cannot be stubbed at U-CP-17 — that would be an X-AL-3
silent H_T design extension (inventing a type the spec does not commit at this
site).

## Resolution applied (halt-route-split-AC)

The 5-step §7.3 procedure decomposes cleanly; step 4 ("apply operator
preferences") is the ONLY surface coupled to `EngineClassPreferences`. Per the
`halt-route-split-ac-pattern` memory:

1. `operator_preferences` field DROPPED from `WorkloadBindingSelectionInput`.
2. AC #1 step 4 STRUCK; the procedure lands as a 4-step procedure
   (steps 1, 2, 3, 5 renumbered 1-4 with step 5 "return selected class"
   preserved as step 4).
3. Test `test_step_4_operator_preference_filter` STRUCK.
4. Steps 1-3 + return + determinism (AC #2) + binding-time (AC #3) land
   verbatim against §7.3.

## Re-entry condition

**UPDATE 2026-05-16 (U-CP-27 landing):** U-CP-27 has landed. Its v2.1/v2.9
unit body does **NOT** declare or consume `EngineClassPreferences` — a literal
grep of `Implementation_Plan_Control_Plane_v2_1.md` + `_v2_9.md` finds
`EngineClassPreferences` only at U-CP-17 (L976 / L307). The v2.6 carrier-map's
"`EngineClassPreferences` | U-CP-27 | U-CP-27 internal | CP §7.4" homing is
spurious — spec §7.4 is the capability-floor table and commits no
operator-preferences record; §7.3 step 4 reads "Operator selects specific
engine candidate from the cell's recommended set" with no record. Declaring
`EngineClassPreferences` unilaterally at U-CP-27 would be an X-AL-3 silent
design extension (the plan v2.9 §0.4 carrier rule requires the unit body to
already consume the type name-only; U-CP-27 does not). U-CP-27 therefore
landed per its v2.1 body **without** `EngineClassPreferences`.

**This tension does NOT clear at U-CP-27 landing.** It stays OPEN pending the
operator decision under "Routing" — (a) U-CP-17 body amended to defer
`operator_preferences` with a forward-pointer, or (b) `EngineClassPreferences`
re-homed (e.g. to U-CP-00c) as a CP-owned shared type. Until that decision,
U-CP-17 remains partial-landed (4 of 5 §7.3 steps; step 4 + 1 test struck).

## Routing

Routed to design-substrate plan-revision channel (CP plan v2.8 candidate):
either (a) U-CP-17 body amended to defer the `operator_preferences` field
explicitly with a forward-pointer to U-CP-27, or (b) `EngineClassPreferences`
re-homed to U-CP-00b as a CP-owned shared type so U-CP-17 can consume it
ahead of U-CP-27. Operator decision owed.

---

## Audit reconciliation (2026-05-20)

**Verified status:** DEFERRED-PARTITION

**Resolving artifact / evidence:** U-CP-17 partial-lands at workload_binding_engine_class_selection.py (4/5 steps of §7.3 procedure; step 4 'apply operator preferences' struck). EngineClassPreferences re-homing is a deferred partition, not an open defect — resolves when a future CP plan revision designates the type's permanent home.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
