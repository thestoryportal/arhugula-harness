# Landed-Unit Re-Check Inventory — carrier re-point worklist

*Pre-resume inspection pass. The R-series materializability conformance gave
several consumed types proper carriers AFTER the units that consume them had
already been landed (coded). This file inventories, per landed unit, the
now-carried types it consumes, how the landed source currently obtains each,
the re-point the conformed plan requires, and whether that re-point is
doable-now or gated on a not-yet-coded carrier unit.*

*INSPECTION ONLY. No source file edited. The re-pointing itself is coding-lane
work. Authored 2026-05-15.*

---

## Carrier-unit coding status (the gating discriminator)

| Carrier unit | Package | Status | Notes |
|---|---|---|---|
| U-CP-00 (`WorkloadClass`) | `harness-core` | **CODED** — `harness-core/src/harness_core/workload_class.py` | Re-points to this are doable-now. |
| U-CORE-01 (`DeploymentSurface`, `PersonaTier`, identity-alias module, `WorkflowEvent`/`WorkflowEventClass`) | `harness-core` | **NOT CODED** — new plan unit (`Implementation_Plan_Harness_Core_v1_0.md`) | Re-points to this are carrier-gated. |
| U-CP-00b (`AttributeValueType`, `Cardinality`, CP structured-type set) | `harness-cp` | **NOT CODED** — new plan unit (CP plan v2.6 §2.0b) | Re-points to this are carrier-gated. |
| U-OD-00 (`AuditPayload`, `AuditLedgerEntry`, `AuditLedger`, `AuditSignatureAttributes`) | `harness-od` | **NOT CODED** — new plan unit (OD plan v2.6) | Re-points to this are carrier-gated. |

A re-point whose target carrier is NOT CODED cannot be performed yet — the
import would dangle. The coding lane must land the carrier unit first.

---

## Per-unit inventory

### U-IS-02 — path-binding loader + path resolver

Landed source: `harness-is/src/harness_is/path_binding.py`,
`harness-is/src/harness_is/path_resolver.py`.

| Now-carried type | How landed source obtains it today | Conformed-plan re-point | Doable now? |
|---|---|---|---|
| `WorkflowClass` / `WorkloadClass` | Local `WorkflowClass = NewType("WorkflowClass", str)` declared in `path_binding.py` (line 31), re-exported and consumed by `path_resolver.py`. Inlined local declaration. | IS plan v2.3: re-point to `WorkloadClass` from `harness-core` U-CP-00 (`[U-CP-00]` edge); spelling unified `WorkflowClass`→`WorkloadClass` per R2. | **YES — doable now.** U-CP-00 is coded in `harness-core`. |
| `DeploymentSurface` | Local `DeploymentSurface = NewType("DeploymentSurface", str)` declared in `path_binding.py` (line 34). Inlined local declaration. | IS plan v2.3: re-point to `DeploymentSurface` from `harness-core` U-CORE-01 (`[U-CORE-01]` edge). | **NO — carrier-gated** on U-CORE-01. |

Note: the IS source models both types as opaque `str` newtypes and the
docstring explicitly defers the taxonomy ("IS does not own the taxonomy").
The conformed plan re-point swaps the local newtypes for the `harness-core`
carriers. The `WorkloadClass` re-point also entails the `WorkflowClass`→
`WorkloadClass` spelling unification.

Tracked as IS recheck residual **AI-R2-1**.

---

### U-AS-02 — forced-tier resolution

Landed source: `harness-as/src/harness_as/forced_tier_resolution.py`.

| Now-carried type | How landed source obtains it today | Conformed-plan re-point | Doable now? |
|---|---|---|---|
| `ToolContext` | Declared in-unit as a Pydantic `BaseModel` (`computer_use_bound: bool`, `code_execution_beta_invoked: bool`). Inlined local declaration. | AS plan v1.2: `ToolContext` STAYS in-unit (declared at its first-consuming AS unit per R3 — verbatim_audit Pattern B). | **N/A — no re-point owed.** |
| `SandboxTier` | Imported from sibling `harness_as.sandbox_tier` (U-AS-01). | No change — U-AS-01 is the canonical AS carrier. | **N/A — already correct.** |

U-AS-02 carries no carrier-gated re-point. `ToolContext` is a sanctioned
in-unit declaration; `SandboxTier` already imports from its landed carrier.

---

### U-AS-04 — foundational discriminator enums

Landed source: `harness-as/src/harness_as/discriminators.py`.

| Now-carried type | How landed source obtains it today | Conformed-plan re-point | Doable now? |
|---|---|---|---|
| `DeploymentSurface` | Declared in-unit as a `StrEnum` (3 members: `local-development` / `self-hosted-server` / `managed-cloud`). Inlined local declaration. | AS plan v1.2: U-AS-04 converts from DECLARING to IMPORTING `DeploymentSurface` from `harness-core` U-CORE-01 (`[U-CORE-01]` edge); local enum deleted. | **NO — carrier-gated** on U-CORE-01. |
| `PersonaTier` | Declared in-unit as a `StrEnum` (3 members: `solo-developer` / `team-binding` / `multi-tenant-compliance`). Inlined local declaration. | AS plan v1.2: U-AS-04 converts from DECLARING to IMPORTING `PersonaTier` from `harness-core` U-CORE-01 (`[U-CORE-01]` edge); local enum deleted. | **NO — carrier-gated** on U-CORE-01. |
| `MCPTransport` | Declared in-unit as a `StrEnum`. Inlined local declaration. | No change — `MCPTransport` is AS-owned per the carrier map; remains declared at U-AS-04. | **N/A — no re-point owed.** |

U-AS-04 is the type-shape source that the carrier map cites as the basis for
the `harness-core` `DeploymentSurface`/`PersonaTier` enums — the U-CORE-01
declarations should be byte-identical to these landed enums. Re-point converts
U-AS-04 to an importer.

Tracked as AS recheck residual **A-1**.

---

### U-OD-01 — 9-cell observability matrix

Landed source: `harness-od/src/harness_od/observability_matrix.py`.

| Now-carried type | How landed source obtains it today | Conformed-plan re-point | Doable now? |
|---|---|---|---|
| `PersonaTier` | Declared in-unit as a `StrEnum` (3 members, C-OD-01 §1.1 verbatim). Inlined local declaration. | OD plan v2.6: U-OD-01 converts from DECLARING to IMPORTING `PersonaTier` from `harness-core` U-CORE-01 (`[U-CORE-01]` edge); local enum deleted. | **NO — carrier-gated** on U-CORE-01. |
| `DeploymentSurface` | Declared in-unit as a `StrEnum` (3 members, C-OD-01 §1.1 verbatim). Inlined local declaration. | OD plan v2.6: U-OD-01 converts from DECLARING to IMPORTING `DeploymentSurface` from `harness-core` U-CORE-01 (`[U-CORE-01]` edge); local enum deleted. | **NO — carrier-gated** on U-CORE-01. |

The landed `PersonaTier`/`DeploymentSurface` enums are independent
re-declarations of the same cross-cutting enums U-AS-04 declares — this
double-declaration is exactly the no-single-carrier defect U-CORE-01 closes.
`CellID`, `CellStatus`, `CellBindingViolation` are OD-internal and unaffected.

Tracked as OD recheck residual **A-R5-2**.

---

### U-OD-04 — OTel GenAI semconv 1.41.0 base layer

Landed source: `harness-od/src/harness_od/otel_genai_base.py`.

| Now-carried type | How landed source obtains it today | Conformed-plan re-point | Doable now? |
|---|---|---|---|
| `SpanRef` / `ChildSpanRef` / `SpanAttributes` / `EventEmission` | **Not present in the landed source.** U-OD-04 currently declares only the spec-verbatim OTel surface (`GenAiOperation`, `AttributeTier`, span-name/metric constants). The four span-handle types are absent. | OD plan v2.6 M-1: U-OD-04 is CARRIER-GROWN — it gains the 4 span-handle types (new signature sub-block + acc #9 + tests). This is authoring NET-NEW code, not a re-point of an existing consumption. | **N/A as a re-point.** This is a carrier-growth authoring task on the unit itself — doable whenever U-OD-04 is re-touched; it is not gated on any other unit. The landed v2.5-verbatim surfaces are preserved untouched. |

U-OD-04 consumes none of the now-carried types today. The conformance does not
require U-OD-04 to re-point an import; it requires U-OD-04 to GROW into the
carrier for the `SpanRef` family. Listed here for completeness — there is no
import re-point owed, only an additive authoring pass.

Tracked as OD recheck residual **A-R5-1**.

---

### U-CP-10 — F3 lifecycle event class enum

**No landed source found.** `harness-cp/src/harness_cp/` contains only
`engine_class.py` (U-CP-15), `resumption_kind.py` (U-CP-19),
`topology_pattern.py` (U-CP-22). The Phase 7 landing progress ledger
(`.harness/phase-7-progress.md` §"Sub-phase 7b") lists no U-CP-10 landing —
the landed CP units are U-CP-00 / U-CP-15 / U-CP-19 / U-CP-22.

**Verdict: task premise inconsistent with workspace state.** U-CP-10 is named
in the brief's 7-unit set, but it has not been coded. The RC-B recheck names a
"D-2 (U-CP-10 landed-source re-point at v2.6 application)" item — that
disposition appears to anticipate a landed U-CP-10 that does not yet exist in
this workspace.

No re-point is applicable until U-CP-10 is coded. When U-CP-10 IS landed, the
conformed CP plan v2.6 requires its `LifecycleEventClass` local enum to be
struck and re-typed to `harness-core` `WorkflowEventClass` (`[U-CORE-01]`
edge) per the U-CP-10 / `WorkflowEventClass` reconciliation (operator
decision D9). That future re-point would be **carrier-gated** on U-CORE-01.

Recommendation: the coding lane should treat U-CP-10 as a not-yet-landed unit
to be implemented directly against CP plan v2.6 (already reconciled), NOT as a
landed unit needing retrospective re-point. Carry forward as a separate
verification item.

---

### U-CP-15 — engine-class taxonomy + capability floors

Landed source: `harness-cp/src/harness_cp/engine_class.py`.

| Now-carried type | How landed source obtains it today | Conformed-plan re-point | Doable now? |
|---|---|---|---|
| (none) | U-CP-15 imports only `enum.StrEnum` + `pydantic`. `EngineClass`, `CapabilityFloor`, `CAPABILITY_FLOORS` are all self-declared; no cross-package type consumed. | CP plan v2.6: the RC-B recheck flags only a `CapabilityFloor` thin-§7.4-basis re-check (D-1), operator-accepted as a faithful factor-out — NOT a re-point. No now-carried type is consumed at any U-CP-15 signature position. | **N/A — no re-point owed.** |

U-CP-15 consumes no carrier-mapped shared type. It is self-contained against
CP spec C-CP-07. No re-point required.

Tracked CP recheck item **D-1** is a faithfulness re-check of `CapabilityFloor`
against §7.4, not a carrier re-point.

---

## Verdict summary

| Unit | Now-carried types consumed | Re-point owed? | Doable now / gated |
|---|---|---|---|
| U-IS-02 | `WorkflowClass`/`WorkloadClass`; `DeploymentSurface` | Yes (2) | `WorkloadClass`→U-CP-00 **doable now**; `DeploymentSurface`→U-CORE-01 **gated** |
| U-AS-02 | `ToolContext` (in-unit); `SandboxTier` (sibling) | No | — |
| U-AS-04 | `DeploymentSurface`; `PersonaTier`; `MCPTransport` (AS-owned) | Yes (2) | both →U-CORE-01 **gated** |
| U-OD-01 | `PersonaTier`; `DeploymentSurface` | Yes (2) | both →U-CORE-01 **gated** |
| U-OD-04 | none consumed (carrier-GROWN, not consumer) | No (additive authoring) | carrier-growth, ungated, not a re-point |
| U-CP-10 | n/a — not landed | n/a | no landed source; carry-forward |
| U-CP-15 | none | No | — |

**Re-point tally (per the brief's doable-now vs carrier-gated question):**

- **Doable-now re-points: 1** — U-IS-02 `WorkloadClass` (U-CP-00 is coded).
- **Carrier-gated re-points: 5** — U-IS-02 `DeploymentSurface`, U-AS-04
  `DeploymentSurface`, U-AS-04 `PersonaTier`, U-OD-01 `PersonaTier`, U-OD-01
  `DeploymentSurface` — all gated on U-CORE-01, which is a new, not-yet-coded
  plan unit.
- **No re-point owed: U-AS-02, U-CP-15** (no carrier-mapped type consumed),
  and U-OD-04 (carrier-growth authoring, not a re-point).
- **U-CP-10: no landed source** — task premise inconsistent with workspace
  state; carry forward as a verification item, not a re-point.

**Coding-lane consequence.** All 5 carrier-gated re-points share one gate:
**U-CORE-01 must be coded first** in `harness-core`. Once U-CORE-01 lands,
all 5 become doable in one sweep (U-IS-02, U-AS-04, U-OD-01). The single
doable-now re-point (U-IS-02 `WorkloadClass`) can proceed immediately and
should be folded into the same U-IS-02 source touch that later picks up
`DeploymentSurface`, to avoid touching `path_binding.py` twice.

---

## Re-point execution status (addendum — 2026-05-15)

The carrier-gated re-point sweep was executed after U-CORE-01 landed.

| Re-point | Unit | Status | Commit |
|---|---|---|---|
| `WorkloadClass` (U-CP-00) + `DeploymentSurface` (U-CORE-01) | U-IS-02 | ✅ done — AI-R2-1 cleared | `refactor(is): re-point U-IS-02 …` |
| `DeploymentSurface` + `PersonaTier` (U-CORE-01) | U-AS-04 | ✅ done — A-1 cleared | `refactor(as): re-point U-AS-04 …` |
| `DeploymentSurface` + `PersonaTier` (U-CORE-01) | U-OD-01 | ✅ done — R5 §3.1.1 conversion cleared | `refactor(od): re-point U-OD-01 …` |

All 5 carrier-gated re-points + the 1 doable-now re-point (U-IS-02 `WorkloadClass`)
are complete. Workspace pyright strict: 0 errors. Per-package pytest: all green.
**U-IS-02 note:** the closed enums rejected the landed test fixtures' arbitrary
`wf-alpha` / `local` strings — fixtures were rewritten to canonical enum values.
**U-CP-10** remains not-landed (carry-forward — implement fresh against CP v2.6).

*End of inventory. The original body above was INSPECTION ONLY; this addendum
records the executed coding-lane re-points. Authored 2026-05-15.*
