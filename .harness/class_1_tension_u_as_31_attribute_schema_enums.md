# Class 1 Tension — U-AS-31 cross-axis consumption of CP-homed schema enums

*Phase 7 sub-phase 7b. Fork detected at U-AS-31 execution-time (AS Level-2
cluster). Routed per `CLAUDE.md` §4.3 + `harness-as/CLAUDE.md` §5. **RESOLVED**
2026-05-16 — operator ruled re-home; applied; U-AS-31 landed.*

---

## 1. Identification

| Field | Value |
|---|---|
| Tension ID | Class-1 / U-AS-31 / attribute-schema-enum-carrier-home |
| Sub-phase | 7b (per-axis-stream implementation — AS Level-2 cluster) |
| Surfaced at | Landing U-AS-31 (AS-axis attribute-namespace declarations) |
| Class | **1** — carrier-home defect; a cross-axis shared type homed in the wrong axis package; halt-execution |
| Routing target | Phase 6 plan + carrier-map revision — re-home `AttributeValueType` / `Cardinality` to `harness-core`; cascade to the landed U-CP-00b and the CP consumer plan |
| Status | **RESOLVED** 2026-05-16 — operator ruled re-home; applied; U-AS-31 landed |

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

This is not only a carrier-map oversight. The landed
`harness-cp/src/harness_cp/schema_attribute_enums.py` module docstring records
an explicit **operator decision D3**: *"CP-axis-owned (operator decision D3 —
all consumers are CP-axis units; no cross-axis sharing, so it resides in
`harness-cp`, not `harness-core`)."* Operator decision D3 was made on the
false premise "no cross-axis sharing". U-AS-31 is the counter-evidence. The
resolution below is, in effect, a revisit of D3 on corrected information.

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

## 6. Resolution applied — 2026-05-16

Operator ruled **re-home now** (option A). Applied:

- `harness-core/src/harness_core/schema_attribute_enums.py` created — declares
  `AttributeValueType` (5 values) + `Cardinality` (4 values), member sets
  byte-exact with the U-CP-00b landing. `harness-core/__init__.py` re-exports.
- `harness-cp/src/harness_cp/schema_attribute_enums.py` re-pointed — now imports
  + re-exports the two enums from `harness-core` (CP-side
  `harness_cp.schema_attribute_enums` citations stay stable). No CP consumer of
  these enums has landed, so no consumer code dangled.
- `harness-cp/tests/test_schema_attribute_enums.py` — the
  `test_both_enums_reside_in_harness_cp` test (which asserted operator decision
  D3) re-pointed to `test_both_enums_re_homed_to_harness_core`.
- `.harness/shared_type_carrier_map.md` line 100 updated — carrier = `harness-core`;
  consumers = CP + AS; the stale "all consumers in-axis" rationale corrected.
- `harness-as` already depends on `harness-core`; U-AS-31 imports the two enums
  from `harness-core` and **landed** (`feat(as): land U-AS-31`), 13 tests green.

Commit: `refactor(core): re-home AttributeValueType/Cardinality to harness-core`.
Operator decision D3 is superseded — the enums are cross-axis (CP + AS) and
reside on `harness-core` per `CLAUDE.md` §3.3.

**Owed (non-blocking mechanical):** the design-substrate CP plan v2.7 §2.0b
U-CP-00b body + AS plan U-AS-31 `Depends on` still cite the CP-axis carrier
home; a doc-reconciliation pass should re-cite them to the `harness-core`
carrier. Flagged like AS plan A-3 — deferred mechanical re-cite, no code impact.

## 7. AS Level-2 cluster status

All 7 AS L2 units landed: U-AS-06, U-AS-10, U-AS-22, U-AS-24, U-AS-25, U-AS-29,
U-AS-31. L2 cluster closed; AS L0+L1+L2 complete (17/33).

## 8. Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_tension_u_as_31_attribute_schema_enums.md` |
| Authored | Phase 7 7b, 2026-05-16 |
| Resolution authority | Operator ruling 2026-05-16 (re-home to `harness-core`) |
| Status | **RESOLVED** — enums re-homed; U-AS-31 landed; doc re-cite owed (mechanical) |

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** Already labeled RESOLVED 2026-05-16 (operator-ratified re-home — AttributeValueType + Cardinality moved to harness-core v1.0; U-AS-31 lands). Audit confirms.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
