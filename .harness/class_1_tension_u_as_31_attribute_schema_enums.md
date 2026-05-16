# Class 1 Tension — U-AS-31 cross-axis consumption of CP-homed schema enums

*Phase 7 sub-phase 7b. Fork detected at U-AS-31 execution-time (AS Level-2
cluster). Routed per `CLAUDE.md` §4.3 + `harness-as/CLAUDE.md` §5. **OPEN** —
awaiting operator ruling.*

---

## 1. Identification

| Field | Value |
|---|---|
| Tension ID | Class-1 / U-AS-31 / attribute-schema-enum-carrier-home |
| Sub-phase | 7b (per-axis-stream implementation — AS Level-2 cluster) |
| Surfaced at | Landing U-AS-31 (AS-axis attribute-namespace declarations) |
| Class | **1** — carrier-home defect; a cross-axis shared type homed in the wrong axis package; halt-execution |
| Routing target | Phase 6 plan + carrier-map revision — re-home `AttributeValueType` / `Cardinality` to `harness-core`; cascade to the landed U-CP-00b and the CP consumer plan |
| Status | **OPEN** 2026-05-16 — U-AS-31 HALTED; awaiting operator ruling |

## 2. The defect

U-AS-31 ("Declare six Anthropic-primitive attribute namespaces", C-AS-14) declares
the `AttributeSchema` record:

```
record AttributeSchema {
  attribute_name : string
  value_type     : AttributeValueType   # <-- cross-axis enum
  semantic       : string
  cardinality    : Cardinality          # <-- cross-axis enum
  parent_span    : string
  required       : bool
}
```

`AttributeValueType` and `Cardinality` are **landed in `harness-cp`**
(`harness-cp/src/harness_cp/schema_attribute_enums.py`, landed by U-CP-00b). For
U-AS-31 (AS axis) to consume them, `harness-as` would have to depend on
`harness-cp`. That is foreclosed:

- **CXA v2.1 §2.1 / §2.3.4** declares **24 CP→AS cross-axis edges** — `harness-cp`
  will depend on `harness-as` (CP consumes the AS substrate seam). Adding an
  AS→CP package edge now creates a **true `uv` workspace dependency cycle**
  (`harness-as` ↔ `harness-cp`).
- `harness-as/CLAUDE.md` §1.1 + §2.3: AS declares **0 outbound edges to CP**.
- U-AS-31's plan `Depends on: [U-AS-04, U-AS-28]` declares **no** edge to CP or
  core for these enums — the consumption is undeclared.

The shared-type carrier map (`.harness/shared_type_carrier_map.md` line 100)
recorded `AttributeValueType` / `Cardinality` as **"Decided: CP — all consumers
in-axis → per-axis, not core"**. That determination enumerated only the CP
consumers (U-CP-07/11/21/31/37/46/47) and **missed U-AS-31** — an out-of-axis
(AS) consumer. The "all consumers in-axis" premise is contradicted by direct
evidence: U-AS-31's `AttributeSchema` is a cross-axis consumer.

The two enums are genuinely cross-axis: the OTel attribute value-type + cardinality
vocabulary is shared by the CP attribute schemas (C-CP-*) **and** the AS
namespace schemas (C-AS-14). A future OD consumer (C-OD-* attribute schemas) is
likely a third.

## 3. Why this is a halt (not silent absorption)

Three non-options:

1. **AS→CP package edge** — forecloses: creates the `harness-as` ↔ `harness-cp`
   cycle against the 24 declared CP→AS edges. `uv` would reject it.
2. **U-AS-31 declares its own `AttributeValueType` / `Cardinality`** — type
   duplication: two definitions of the same OTel vocabulary in `harness-cp` and
   `harness-as`; the AS `AttributeSchema` would be structurally incompatible with
   the CP `…AttributeSchema` records at the C-AS-14 → C-OD-* / D6 ingestion seam.
   Forecloses a clean cross-axis composition at 7c.
3. **Silent absorption** — `CLAUDE.md` §4.3: the worst failure mode.

## 4. Proposed resolution (operator decision)

Re-home `AttributeValueType` + `Cardinality` to **`harness-core`** — they are
cross-axis shared types (the U-CORE-01 pattern). Concretely:

- Move `AttributeValueType` / `Cardinality` from `harness-cp/.../schema_attribute_enums.py`
  to `harness-core` (new module or appended to an existing one).
- Re-point the landed U-CP-00b source: `harness-cp` imports the two enums from
  `harness-core` instead of declaring them. (U-CP-00b's other content is
  unaffected; no CP consumer of these enums has landed yet — `harness-cp`
  re-export keeps CP-side citations stable.)
- Update the carrier map line 100: carrier = **core**, consumers = CP + AS
  (+ likely OD).
- Revise the CP plan (U-CP-00b carrier-home) and U-AS-31's plan `Depends on` to
  declare a `[U-CORE-NN (cross-axis: core)]` edge.
- Then U-AS-31 lands consuming the enums from `harness-core`.

This is the same shape as the U-CORE-01 cross-cutting shared-type carrier and the
sibling `[[class_1_tension_u_cp_00b_structured_types]]` record.

## 5. Affected landed code

| Artifact | Effect |
|---|---|
| `harness-cp/src/harness_cp/schema_attribute_enums.py` | The two enum *declarations* move to `harness-core`; module re-imports them (or is removed if empty). U-CP-00b landed source re-pointed. |
| `harness-cp` `pyproject.toml` | Already depends on `harness-core` — no new edge. |
| `harness-as` `pyproject.toml` | Already depends on `harness-core` (added at U-AS-28) — no new edge. |
| `state.jsonl` | U-CP-00b landing entry stands; a re-point is a fresh edit, not a retraction. |

No CP consumer of `AttributeValueType` / `Cardinality` has landed — the re-home
dangles no landed consumer code.

## 6. AS Level-2 cluster status

The other 6 AS L2 units landed clean: U-AS-06, U-AS-10, U-AS-22, U-AS-24,
U-AS-25, U-AS-29. U-AS-31 is the **only** L2 unit blocked. The L2 cluster closes
at 6/7; U-AS-31 lands after this tension resolves.

## 7. Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_tension_u_as_31_attribute_schema_enums.md` |
| Authored | Phase 7 7b, 2026-05-16 |
| Resolution authority | Operator ruling owed |
| Status | **OPEN** — U-AS-31 HALTED; re-home `AttributeValueType` / `Cardinality` to `harness-core` proposed |
