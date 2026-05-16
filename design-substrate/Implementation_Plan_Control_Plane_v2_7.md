# Implementation Plan — Control Plane v2.7

**Status:** Proposed

**Date:** 2026-05-15

**Revision:** v2.7 — Phase 7 sub-phase 7b in-CLI micro-revision. **Splits the U-CP-00b carrier unit.** The v2.6 §2.0b U-CP-00b body bundled 2 fully-specified utility enums with 9 "CP-owned structured shared types" declared **name + kind + provenance only** — no member sets, no field schemas (a plan-grade incompleteness surfaced at U-CP-00b execution-time). v2.7 narrows U-CP-00b to the 2 utility enums (materializable now); the 9 structured types are deferred to a future CP plan revision that must specify each shape. v2.7 is a delta over v2.6: **only §2.0b U-CP-00b and the §11.1 registry are revised**; every other section is preserved verbatim from v2.6. Predecessor: v2.6 (R4 materializability conformance).

**Revision date:** 2026-05-15

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `CLAUDE.md` §4.3 back-flow routing (Class 1 fork resolution); `harness-cp/CLAUDE.md` §5 (CP plan atomic-unit signature defect → Phase 6 plan revision); `implementation-planner` SKILL.md §8 revision-pass sub-mode.

**Entry authorization:** Operator ratification 2026-05-15 of the U-CP-00b split (`.harness/class_1_tension_u_cp_00b_structured_types.md`).

---

## §0 Change-note

### §0.1 Trigger

At U-CP-00b execution-time (Phase 7 7b), the v2.6 §2.0b unit body was found to bundle two materializability classes:

- **Materializable now:** `AttributeValueType` (5 values) and `Cardinality` (4 values) — fully-specified byte-exact relocations of the enums previously inline at U-CP-01.
- **Under-specified:** 9 "CP-owned structured shared types" — `ActorIdentity`, `AgentRole`, `ModelBinding`, `TraceContext`, `ProviderAgnosticPayload`, `RoutingDecisionTrace`, `MCPTrustTier`, `Axis`, `TailKeepPredicate` — declared in the §2.0b Signatures block as a type *name* + kind + a one-line provenance comment only. No member sets for the enums, no field schemas for the records. The §11.1 registry even records `AgentRole` as "enum/newtype" — the plan itself has not decided its kind.

Authoring 9 type shapes (3 of them records — `ModelBinding`, `ProviderAgnosticPayload`, `RoutingDecisionTrace`) from 6+ scattered spec sections at execution-time discretion is genuine design surface — an X-AL-3 silent-design-extension risk if a shape is guessed. The 9 structured types are not at implementation-grade detail (`implementation-planner` SKILL.md §3.8 / §6).

### §0.2 Class + routing

Class 1 (plan signature not at implementation-grade detail) per `CLAUDE.md` §4.3. Halted at U-CP-00b; surfaced to operator.

### §0.3 Operator ruling — 2026-05-15 (split U-CP-00b)

U-CP-00b is **narrowed to the 2 utility enums** (`AttributeValueType`, `Cardinality`). These land now — they unblock the 7 Pattern-C `…AttributeSchema` consumer units (U-CP-01/07/11/21/31/37/46/47). The 9 structured shared types are **struck from U-CP-00b** and deferred: a future CP plan revision must specify each type's concrete shape (member sets / field schemas, traced to its committing contract) before any consuming unit lands. Recorded at `.harness/class_1_tension_u_cp_00b_structured_types.md`.

### §0.4 Changes at v2.7

| Site | v2.6 | v2.7 |
|---|---|---|
| §2.0b U-CP-00b title | "…utility enums + the CP-owned structured shared types" | "…utility enums" (structured types struck) |
| §2.0b Signatures | 2 enums + 9 name-only structured-type lines | 2 enums only |
| §2.0b Files affected | `…` + `cp-shared-types` | `attribute-value-type-enum`, `cardinality-enum` (the `cp-shared-types` logical file struck) |
| §2.0b acc #4 | the 9 structured types declared at U-CP-00b | **struck** — deferred (§0.3) |
| §2.0b acc #5 | "each shared type is a T2-confirmed FACTOR-OUT" | reworded — scoped to the 2 enums |
| §2.0b Tests | incl. `test_cp_shared_types_resolve_single_nominal_type` | that test struck |
| §11.1 registry | 9 structured-type rows carrier `U-CP-00b` | 9 rows carrier **DEFERRED** (see §11.1 delta) |

### §0.5 Deferred-edge note

The v2.6 §0.11.2 Pattern-D `[U-CP-00b]` dependency edges for the 9 structured types' consumer units (U-CP-03/04/05/09/13/14/27/29/30/43/45/49/50/51/52) are **deferred with the types** — they become live when the deferred revision specifies the shapes. The Pattern-C `[U-CP-00b]` edges for the 2-enum consumers (U-CP-01/07/11/21/31/37/46/47) are **unaffected** — those land against this v2.7 U-CP-00b. No consuming unit of the 9 structured types is landed yet, so no edge dangles in landed code.

### §0.6 Sections preserved verbatim from v2.6

All of §0 (v2.6 change-note), §1, §2 except §2.0b, §3–§10, §11 except the §11.1 registry rows enumerated below.

---

## §2.0b U-CP-00b — Declare `AttributeValueType` + `Cardinality` schema-attribute utility enums [REVISED — v2.7: structured types split out]

[v2.6-introduced unit. v2.7 delta: the 9 "CP-owned structured shared types" are **struck** from U-CP-00b and deferred to a future CP plan revision (§0.3). U-CP-00b is narrowed to the 2 schema-attribute utility enums — `AttributeValueType` and `Cardinality` — the fully-specified, byte-exact relocations of the enums previously inline at U-CP-01. All retained content (the 2 enum signatures, acc #1/#2/#3, the aggregate-citation `Implements` form) preserved verbatim from v2.6 §2.0b.]

**Implements:** (carrier unit — no single spec contract). `AttributeValueType` and `Cardinality` are plan-introduced auxiliary enums — the value-type and cardinality discriminators the CP plan uses to type its `…AttributeSchema` records. Traced to the **aggregate** of the seven attribute-schema contracts they serve — `[C-CP-01 §1.4]`, `[C-CP-03 §3.5]`, `[C-CP-07]`, `[C-CP-10 §10]`, `[C-CP-18 §16]`, `[C-CP-20 §20.4]`, `[C-CP-21 §21.5]` — each of which characterizes attribute value-types and cardinality in prose. The aggregate-citation form is operator-ratified at D3 (Q-R4-1).

**Depends on:** (none) — foundational; L0, beside U-CP-00. Imports nothing; the seven `…AttributeSchema` units import it.

**Inputs:** None (foundational; substrate-supplying carrier unit — mirrors U-CP-00).

**Files affected:** CP-axis schema-attribute utility enums (logical: `attribute-value-type-enum`, `cardinality-enum`). **Residence: `harness-cp`** (CP-axis-owned per operator decision D3 — all consumers are CP-axis units, no cross-axis sharing).

**Signatures:**

```
enum AttributeValueType {
  STRING,                                             // attribute carries a string value
  INT,                                                // attribute carries an integer value
  FLOAT,                                              // attribute carries a float value
  BOOL,                                               // attribute carries a boolean value
  ENUM_REF                                            // attribute carries a reference into a named enum domain
}
// Closed at cardinality 5. Verbatim relocation of the enum declared at
// U-CP-01 v2.4-conformed body line 175 — no value added, no value dropped.

enum Cardinality {
  LOW,                                                // bounded small domain
  MEDIUM,                                             // bounded moderate domain
  HIGH,                                               // bounded large domain
  PER_REQUEST                                         // unbounded / per-request-distinct
}
// Closed at cardinality 4. Verbatim relocation of the enum declared at
// U-CP-01 v2.4-conformed body line 176 — no value added, no value dropped.
```

> **v2.7 — structured shared types deferred.** v2.6 §2.0b also declared 9 "CP-owned structured shared types" (`ActorIdentity`, `AgentRole`, `ModelBinding`, `TraceContext`, `ProviderAgnosticPayload`, `RoutingDecisionTrace`, `MCPTrustTier`, `Axis`, `TailKeepPredicate`) as name-only signatures. They are **not** declared at U-CP-00b — their shapes were under-specified at plan grade. They are deferred to a future CP plan revision per `.harness/class_1_tension_u_cp_00b_structured_types.md`. No consuming unit of these types may land until that revision specifies each shape.

**Acceptance criteria:**

1. `AttributeValueType` declares exactly five values `STRING | INT | FLOAT | BOOL | ENUM_REF` — byte-exact with the enum previously declared inline at U-CP-01 (v2.4-conformed body line 175). Closed at cardinality 5. No value added or removed by the relocation.
2. `Cardinality` declares exactly four values `LOW | MEDIUM | HIGH | PER_REQUEST` — byte-exact with the enum previously declared inline at U-CP-01 (v2.4-conformed body line 176). Closed at cardinality 4. No value added or removed.
3. Both enums reside in `harness-cp` and are exposed at the CP-axis package surface so the seven `…AttributeSchema` consuming units (U-CP-01/07/11/21/31/37/46/47) import from one path; `pyright` strict resolves a single nominal type for each across all eight units.
4. **(v2.7 — struck.)** The v2.6 acc #4 (the 9 CP-owned structured shared types declared at U-CP-00b) is struck — those types are deferred per §0.3.
5. No spec extension: the relocation introduces no new value; `AttributeValueType` and `Cardinality` are each a faithful factor-out of the value-type / cardinality vocabulary characterized in the seven attribute-schema contracts' prose.

**Tests:** `test_attribute_value_type_cardinality_five`; `test_attribute_value_type_values_byte_exact_with_relocated_enum`; `test_cardinality_cardinality_four`; `test_cardinality_values_byte_exact_with_relocated_enum`; `test_both_enums_reside_in_harness_cp`; `test_attribute_schema_units_resolve_single_nominal_type` (a `pyright`-strict cross-unit composition check). *(v2.7: `test_cp_shared_types_resolve_single_nominal_type` struck — the structured types are deferred.)*

**Rollback boundary:** Revert the U-CP-00b enum declarations from `harness-cp`. Downstream impact: the seven `…AttributeSchema` units lose their `value_type`/`cardinality` carrier (Pattern C reopens). If the relocation is reverted *without* restoring the inline U-CP-01 declarations, all eight attribute-schema units fail `pyright`. A single coherent revert.

---

## §11.1 CP auxiliary-type registry — v2.7 delta

The following 9 rows are revised — carrier `U-CP-00b` → **DEFERRED**:

| Type | Kind | Carrier | Consuming units | Trace |
|---|---|---|---|---|
| `ActorIdentity` | newtype | **DEFERRED** (Class 1 — `class_1_tension_u_cp_00b_structured_types.md`) | U-CP-14/27/30/49 | carrier-map "`ActorIdentity` vs IS `Actor`" |
| `AgentRole` | enum/newtype (undecided) | **DEFERRED** | U-CP-03/04/09/27/29 | C-CP-13 §13.4 |
| `ModelBinding` | record | **DEFERRED** | U-CP-13/14/29/50 | ADR-F1 v1.2 / C-CP-13 §13.4 |
| `TraceContext` | record | **DEFERRED** | U-CP-03 | OTel adoption / CP §8 |
| `ProviderAgnosticPayload` | record | **DEFERRED** | U-CP-03 | ADR-F1 v1.2 / C-CP-01/02 |
| `RoutingDecisionTrace` | record | **DEFERRED** | U-CP-03, U-CP-05 | CP §2 layered routing |
| `MCPTrustTier` | enum | **DEFERRED** | U-CP-43/45 | C-CP-43 gate-level |
| `Axis` | enum | **DEFERRED** | U-CP-43 | 5-axis gate enum (plan-introduced) |
| `TailKeepPredicate` | type | **DEFERRED** | U-CP-32/51 | CP §51 tail-keep |

The `AttributeValueType` / `Cardinality` rows (carrier `U-CP-00b`) and all other §11.1 rows are preserved verbatim from v2.6. Per §11.2 registry discipline, a type at a signature position with a DEFERRED carrier is a known-open Pattern-D item — the deferred CP plan revision resolves it before any consuming unit lands.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_7.md` |
| Authored at | Phase 7 sub-phase 7b, 2026-05-15 — v2.7 Class 1 micro-revision (U-CP-00b carrier split) |
| Authoring authority | Operator ratification 2026-05-15 (`.harness/class_1_tension_u_cp_00b_structured_types.md`) |
| Predecessor | `Implementation_Plan_Control_Plane_v2_6.md` (R4 materializability conformance) |
| Successor consumption | U-CP-00b (2 enums) lands against this file; the 9 deferred structured types await a future CP plan revision specifying their shapes |
| Revision policy | Canonical for the CP axis plan; revisions in-CLI per workspace discipline |

*End of Implementation Plan — Control Plane v2.7. Delta over v2.6 — only §2.0b U-CP-00b + the §11.1 registry revised. All other sections preserved verbatim from v2.6.*
