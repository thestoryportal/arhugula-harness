# Class 1 Tension — U-OD-02 (cell-4 / cell-5 backend-class alternation un-materializable against single-value signature)

| Field | Value |
|---|---|
| Unit | U-OD-02 — Declare per-cell backend class + candidate witness columns |
| Sub-phase | 7b — OD axis-stream (Level 1) |
| Fork class | Class 1 (halt-execution — plan signature cannot be materialized; acceptance criterion incompatible with signature) |
| Filed | 2026-05-16 |
| Actor | phase-7-implementation |
| Disposition | **OPEN** — U-OD-02 halted, not landed; skipped, axis stream continued with U-OD-05 / U-OD-15 / U-OD-18 |

## Defect

The U-OD-02 body resolved through the delta chain is the **v2.5-revised body**
(`Implementation_Plan_Operational_Discipline_v2_5.md` §3.1.2; preserved verbatim
at v2.6 §3 — "18 units preserved verbatim"). Its `BackendClass` enum was
conformed at v2.5 from 3 → 7 values per the §4A verbatim-divergence cluster.

The v2.5 Signatures block declares (lines 183–189):

```
record PerCellBackendBinding {
  cell_id         : CellID
  backend_class   : BackendClass            // single-valued field
  candidates      : List<CandidateWitness>
}

const PER_CELL_BACKEND_BINDINGS : Map<CellID, PerCellBackendBinding>   // exactly 8 entries

fn select_backend_class(c : CellID) -> BackendClass                    // single-valued return
```

`PerCellBackendBinding.backend_class` is a **single** `BackendClass` value;
`select_backend_class` returns a **single** `BackendClass`;
`PER_CELL_BACKEND_BINDINGS` is keyed `Map<CellID, …>` and acc #2 requires
**"exactly 8 entries — one per ACTIVE cell"** (one binding per cell).

But the v2.5 acceptance criterion #3 requires two cells to carry a **2-value
disjunction**:

> - cell-4 (team-binding × local-development) → `OTEL_ONLY` **OR**
>   `DEDICATED_LLM_OBS_PLATFORM_SINGLE_NODE` ("OTel-only OR Dedicated LLM-obs
>   platform (single-node)" — the §2.1 design-time-flexible disjunction row)
> - cell-5 (team-binding × self-hosted-server) →
>   `DEDICATED_LLM_OBS_PLATFORM_MULTI_NODE` **OR** `OTEL_TO_VENDOR`
>   ("Dedicated LLM-obs platform (multi-node) OR OTel-to-vendor")

acc #7 reinforces this: *"cell-4 alternation, and cell-5 alternation, are the
rare/design-time-flexible-configuration witnesses per §2.1; both alternants are
class-committed shapes at the respective cell."*

The v2.5 tests `test_cell_4_alternation_otel_or_dedicated_single_node` and
`test_cell_5_alternation_dedicated_multi_node_or_otel_to_vendor` name the
alternation explicitly as a test target.

The cited spec section is the upstream source of the disjunction —
`Spec_Operational_Discipline_v1_2.md` C-OD-02 §2.1 (preserved verbatim into
v1.3), the per-cell backend-class table:

> | team-binding × local-development (cell-4) | OTel-only OR Dedicated LLM-obs platform (single-node) |
> | team-binding × self-hosted-server (cell-5) | Dedicated LLM-obs platform (multi-node) OR OTel-to-vendor |

§2.1 prose: *"Eight cells; seven distinct classes (cell-4 admits a class
disjunction at the design-time-flexible row)."* The spec genuinely commits a
disjunction at cells 4 and 5.

## The contradiction

A single-valued field `backend_class : BackendClass`, a single-valued return
`select_backend_class(c) -> BackendClass`, and an 8-entry `Map<CellID, …>`
**cannot represent a 2-value alternation** for cells 4 and 5. The signature and
acceptance criterion #3 are mutually incompatible. This is a Class 1 halt
trigger per the `phase-7-implementation` SKILL.md §6 halt table:

> | Plan signature cannot be materialized at target stack | 1 | Phase 6 plan revision |
> | Acceptance criterion incompatible with another criterion | 1 | Spec or plan revision |

Every available fix is a design choice Phase 7 execution may not make
(`CLAUDE.md` I-2 / X-AL-3 — no silent H_T design extension):

1. **Widen `backend_class`** to `frozenset[BackendClass]` /
   `tuple[BackendClass, ...]` / `BackendClass | tuple[BackendClass, BackendClass]`
   — a signature extension. The plan commits `backend_class : BackendClass`.
2. **Add an `alternates : List<BackendClass>` field** to `PerCellBackendBinding`
   — a signature extension; no spec or plan basis for the field.
3. **Pick one alternant** for cells 4 and 5 (e.g. always `OTEL_ONLY` for cell-4)
   — silent absorption of a spec-committed disjunction; loses the second
   alternant; the worst failure mode per `CLAUDE.md` §4.3. Also fails the two
   `*_alternation_*` tests, which assert *both* alternants.
4. **Two `Map` entries** for cells 4 and 5 — violates acc #2 ("exactly 8
   entries") and the `Map<CellID, …>` keying (one binding per `CellID` key).

There is **no non-extending materialization**. Unlike a halt-route-split case,
there is no clean separable residue: `PerCellBackendBinding` is the unit's
central record and `select_backend_class` its central function; both are typed
on the single-valued `backend_class`. The whole unit is blocked.

## Why neither prior audit caught it

`.harness/materializability_audit_od_plan.md` verdicts U-OD-02 **CLEARED**, but
that audit is explicitly scoped (its Method §1–§3) to *type-carrier
reachability* — undeclared types / no-carrier shared types / hidden coupling. It
states for U-OD-02: *"`BackendClass`/`CandidateWitness`/`PerCellBackendBinding`
declared in-unit; `CellID` in-cone via U-OD-01. No undeclared structured type.
Verbatim 3→7 conformance is the §4A axis (out of scope here)."* It never checked
**signature-vs-acceptance-criterion consistency** — the axis this defect lives
on.

The §4A verbatim audit / v2.5 conformance pass widened `BackendClass` 3 → 7 to
match spec §2.1 vocabulary, but **inherited the disjunction structure unchanged**
from the v2.1 body — v2.1 acc #3 already carried the cell-4 disjunction
(`OTEL_ONLY` OR `DEDICATED_LLM_OBS_SINGLE_NODE`) against the same single-valued
`backend_class : BackendClass` signature; the v2.5 pass widened the enum and
*added* a cell-5 disjunction (cell-5 was a single `DEDICATED_LLM_OBS_SINGLE_NODE`
at v2.1, becomes a 2-value alternation at v2.5) without reconciling the
record/return signatures. The contradiction predates v2.5 for cell-4 and is
freshly introduced for cell-5; neither verbatim nor materializability audit was
scoped to detect it.

## Resolution

**HALT U-OD-02. Not landed. Skipped — OD axis stream continued with U-OD-05,
U-OD-15, U-OD-18.**

## Recommended back-flow

Design-phase channel — OD plan revision-pass (`Implementation_Plan_Operational_Discipline`,
next version bump); routes per `harness-od/CLAUDE.md` §5.1 row "OD plan v2.6
atomic unit signature defect → Phase 6 plan revision-pass":

1. **Option A — widen the signature (recommended).** The operator/`implementation-planner`
   re-specifies `PerCellBackendBinding.backend_class` and the
   `select_backend_class` return as a non-empty set/tuple of `BackendClass`
   (cardinality 1 for cells 1/2/3/6/7/8; cardinality 2 for cells 4/5). This
   matches the spec §2.1 disjunction faithfully and is plan-internal (no spec or
   ADR change — §2.1 already commits the disjunction). The two `*_alternation_*`
   tests and acc #3/#7 become materializable as written.

2. **Option B — split the binding into committed-class + design-time alternate.**
   Add an explicit `alternate_backend_class : Option<BackendClass>` field with
   recorded rationale, sanctioned as an intentional plan structure. Plan-internal.

3. **Option C — re-read the spec for a canonical single-value reading.** If the
   architect rules the §2.1 "OR" rows are *deployment-binding-time selections*
   (not a binding-time alternation the type must carry) — i.e. the binding
   commits the **disjunctive class set** as the witness column and the single
   `backend_class` is undefined/deferred at flexible cells — then acc #3/#7 and
   the signature must be conformed to that reading. This is the U-CP-08-style
   "don't under-read the spec" check: §2.1 prose says cell-4 *"admits a class
   disjunction"* — this reads as a genuine binding-time disjunction, not a
   deferred selection, which points back to Option A.

Until the operator decides, U-OD-02 stays unlanded.

## Downstream impact of the skip

U-OD-02's within-axis dependents per the OD plan dependency graph: U-OD-03
(`Depends on: [U-OD-01, U-OD-02]`), U-OD-28 (`Depends on: [U-OD-02, …]`),
U-OD-30 (`Depends on: [U-OD-01, U-OD-02, U-OD-28, …]`). None are in the Level-1
landing batch (U-OD-03 is L2; U-OD-28 is L6; U-OD-30 is L7). The U-OD-02 skip
blocks U-OD-03's L2 landing until resolved; it does not regress any landed unit.
The three other Level-1 units (U-OD-05, U-OD-15, U-OD-18) do not depend on
U-OD-02 and land unaffected.
