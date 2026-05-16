# Revision R5 — Operational Discipline Plan: Materializability Conformance (v2.5 → v2.6)

**Status:** Proposed
**Revision pass:** R5 — OD plan materializability conformance (the LAST of the 5-pass carrier-map absorption sequence R1–R5).
**Authored:** 2026-05-15 by the `implementation-planner` role in revision-pass sub-mode (`implementation-planner` SKILL.md §8).
**Mode:** Revision-pass. This is a **revision proposal artifact**, not an applied plan edit. The operator ratifies before any `design-substrate/` plan is amended.

**HARD WALL.** This pass writes only `.harness/revision_R5_od_plan.md`. No `design-substrate/` file, no `CLAUDE.md`, no plan/spec/audit/carrier-map, no source code is edited. No git commit.

---

## §0 Change-note

### §0.1 Predecessor

`Implementation_Plan_Operational_Discipline_v2_5.md` (v2.5 — absorption of the OD-plan **verbatim-divergence** cluster per `.harness/verbatim_audit_od_plan.md` §4A; nine full-revised unit bodies; 25 preserved-verbatim units carried from v2.1 via v2.2/v2.3/v2.4 pointers). v2.5 is a delta file; full unit bodies for the 25 unrevised units reside at `Implementation_Plan_Operational_Discipline_v2_1.md` §3.

### §0.2 Revision trigger

R5 absorbs **three operator-ratified upstream recommendations** into the OD plan:

- `.harness/materializability_audit_od_plan.md` (Q3 review-ahead pass) — the canonical OD-plan **materializability** systemic-tension record (distinct from the v2.5 verbatim cluster). 19 CLEARED / 1 CONFORM / 14 FORK. Three patterns: **M-1** (≥11 undeclared auxiliary types consumed at signature positions with no carrier), **M-2** (hidden dependency coupling — carrier exists but unreachable in the consuming unit's `Depends on` cone), **M-3** (U-OD-34 hardcodes a stale 28 / IS:6 cross-axis edge count).
- `.harness/shared_type_carrier_map.md` (Pipeline Pass T1) — ratified carrier map. Disposition-2 assigns the OD-owned undeclared types to OD carrier units; the "Carrier-unit gap section" flags "1–2 new OD carrier units."
- `.harness/xal3_resolution_recommendations.md` (Pipeline Pass T2) — every X-AL-3 candidate, including the OD-owned `SpanRef`/`SpanAttributes`/`EventEmission`/`ChildSpanRef`, resolved **FACTOR-OUT** (concept spec-committed; declaration site missing). **0 genuine design extensions. 0 design-substrate revisions required.**

R5 is the **last** of the R-series. R1 (`harness-core` foundation — U-CORE-01) is the prerequisite; R5 cites the R1-introduced U-CORE-01 carrier. R1 §3.4 is the hand-off list for OD: U-OD-01 is a declaration-site conversion; U-OD-22 needs a `WorkloadClass` edge; U-OD-04 carries a retrospective flag.

### §0.3 Revision scope

| In scope | Out of scope |
|---|---|
| **M-1** — re-point every undeclared auxiliary type to its ratified carrier (§§1, 2, 6, 7) | Editing any `design-substrate/` plan (operator applies post-ratification) |
| **M-2** — add missing hidden-coupling dependency edges (§4) | The v2.5 verbatim-divergence cluster (already absorbed at v2.5) |
| **M-3** — conform U-OD-34's stale cross-axis edge count (§2, U-OD-34) | FF-1 / FF-2 / FF-3 carry-forwards (v2.5 §0.6) — unchanged; not in R5 scope |
| New OD carrier unit **U-OD-00** + the U-OD-04 carrier-growth (§1) | The X-AL-3 design-extension question — T2 resolved it FACTOR-OUT; no spec back-flow |
| U-OD-01 declaration-site conversion (§7) | Source-code edits — HARD WALL; landed-source re-checks are R5-application action items |
| Permanent auxiliary-type audit section (§6) | |

### §0.4 Vocabulary (decided / proposing / open)

Per `implementation-planner` SKILL.md cross-mode discipline + the carrier-map vocabulary. **decided** = authority-chain-determinate; **proposing** = recommendation, operator confirms; **open** = genuinely owed to the operator. Non-determinate items are surfaced as numbered operator questions Q-R5-N at §9.

### §0.5 Reconciliation correction — audit M-2 row 1 dissolved by v2.5 (load-bearing)

The materializability audit's Pattern M-2 table names **three** hidden-coupling edges: U-OD-21→U-OD-20, U-OD-33→U-OD-14, U-OD-22→`WorkloadClass`/U-CP-00. The task framing carried all three.

**The U-OD-33→U-OD-14 edge is dissolved by v2.5 and is NOT added by R5.** The audit's M-2 row for U-OD-33 is grounded in the **v2.1** `PreservationDimension` enum, which carried a `CARDINALITY_BUDGET` dimension annotated `// U-OD-13 + U-OD-14` — the `CARDINALITY_BUDGET` preservation invariant was computed over U-OD-14's cardinality-safe/-prohibited sets, hence the coupling. But **v2.5 §3.8.2 full-revised U-OD-33**: the `PreservationDimension` enum was conformed to the OD spec §22.2 5-dimension table — `CARDINALITY_BUDGET` (and `SANDBOX_TIER`) were **dropped**, replaced by `SPAN_SCHEMA_INGESTION_CONTRACT` and `TRACE_STORAGE_TIER`. The v2.5 conformed dimension set is `{SPAN_SCHEMA_INGESTION_CONTRACT, SAMPLING_DISCIPLINE, REDACTION_DISCIPLINE, TRACE_STORAGE_TIER, GATE_LEVEL_MULTIPLICATIVE_TUNABLE}`. R5 read v2.5 §3.8.2 acceptance criterion #2 line-by-line: **none of the five conformed dimensions references U-OD-14's `CARDINALITY_SAFE_ATTRIBUTES` / `CARDINALITY_PROHIBITED_ATTRIBUTES`** (`SAMPLING_DISCIPLINE` composes the always-sampled set per C-OD-09 §9.2 (U-OD-11) + base-rate envelope per C-OD-10 §10.1/§10.3 (U-OD-12) — not U-OD-14's sets). The carrier U-OD-33 consumed at the audit's M-2 finding-time **no longer exists in the v2.5 unit body.**

The audit (Q3) ran the materializability pass against the v2.5 *delta* file plus v2.1 bodies; its M-2 row for U-OD-33 transcribed the v2.1 dimension annotations and did not re-check them against v2.5's full-revised U-OD-33. **Silent absorption of this stale finding — adding a U-OD-33→U-OD-14 edge for a dimension that v2.5 deleted — is the worst failure mode** (`CLAUDE.md` §4.3). R5 surfaces it as **Q-R5-1** rather than absorbing it.

**Net M-2 scope at R5: 2 edges** (U-OD-21→U-OD-20; U-OD-22→U-CP-00), not 3. See §4.

### §0.6 Sections preserved verbatim from v2.5

| Section | Status |
|---|---|
| §0 (v2.5 change-note) | Superseded by this §0; v2.5 closure records preserved as predecessor history |
| §1 Spec inventory | Preserved verbatim |
| §2 Cluster topology | Preserved verbatim |
| §3.1.3 U-OD-03; §3.2.2–§3.2.5 U-OD-05–08; §3.3.2 U-OD-10 [body — see §0.8 carve-out] | See per-unit notes |
| §3.4.3 U-OD-13; §3.4.5–§3.4.7 U-OD-15–17 | Preserved verbatim |
| §3.1.2 U-OD-02; §3.4.1 U-OD-11; §3.4.2 U-OD-12; §3.4.4 U-OD-14; §3.8.1 U-OD-32 | Preserved verbatim from v2.5 (CLEARED; v2.5-revised, no R5 delta) |
| §3.5.1 U-OD-18; §3.7.2 U-OD-28; §3.7.3 U-OD-29 | Preserved verbatim (CLEARED) |
| §4.5.2 AS-consuming edges (10 edges) | Preserved verbatim |
| §4.5.3 CP-consuming edges (12 edges) | Preserved verbatim |
| §5 Spec-traceability matrix | Preserved verbatim (R5 coverage-matrix delta is additive — see §5) |

### §0.7 Sections revised at R5

| § | Unit / section | Pattern | Substantive surface revised |
|---|---|---|---|
| §1.0 | **U-OD-00 (NEW)** | M-1 | New OD carrier unit — OD-local audit-ledger composition types `AuditPayload` / `AuditLedger` |
| §3.1.1 | U-OD-01 | R1 §3.4 | Declaration-site conversion — strip local `DeploymentSurface` / `PersonaTier`; import from `harness-core` U-CORE-01; add `[U-CORE-01]` edge |
| §3.2.1 | U-OD-04 | M-1 | Carrier growth — declare the OTel-handle alias family `SpanRef` / `ChildSpanRef` / `SpanAttributes` / `EventEmission` (T2 FACTOR-OUT, "at U-OD-04" verdict) |
| §3.3.1 | U-OD-09 | M-1 | `SpanRef` + `EventEmission` re-pointed to U-OD-04; `[U-OD-04]` edge added |
| §3.3.2 | U-OD-10 | M-1 | `SpanAttributes` re-pointed to U-OD-04; `[U-OD-04]` edge added |
| §3.5.2 | U-OD-19 | M-1 | `SpanRef` re-pointed to U-OD-04; `[U-OD-04]` edge added |
| §3.5.3 | U-OD-20 | M-1 | `SpanRef` re-pointed to U-OD-04; `[U-OD-04]` edge added |
| §3.5.4 | U-OD-21 | M-1 + M-2 | `SpanCostRecord` carrier U-OD-20 — `[U-OD-20]` edge added (M-2); `SpanRef` n/a |
| §3.5.5 | U-OD-22 | M-1 + M-2 | `WorkloadClass` → U-CP-00 (`[U-CP-00]` edge, M-2); `DashboardRef` declared in-unit; `SpanRef` n/a |
| §3.6.1 | U-OD-23 | M-1 | `ChildSpanRef` re-pointed to U-OD-04; `[U-OD-04]` edge added |
| §3.6.2 | U-OD-24 | M-1 | `HusainLoopState` declared in-unit |
| §3.6.3 | U-OD-25 | M-1 | `SpanRef` + `EventEmission` re-pointed to U-OD-04; `[U-OD-04]` edge added |
| §3.6.4 | U-OD-26 | M-1 | `SpanAttributes` re-pointed to U-OD-04; `[U-OD-04]` edge added |
| §3.7.1 | U-OD-27 | M-1 | `SpanRow` + `EvictionAction` declared in-unit |
| §3.7.4 | U-OD-30 | M-1 | `SpanRef` re-pointed to U-OD-04 (`[U-OD-04]` edge); `AuditPayload` / `AuditLedger` re-pointed to U-OD-00 (`[U-OD-00]` edge) |
| §3.7.5 | U-OD-31 | M-1 | `SpanAttributes` re-pointed to U-OD-04 (`[U-OD-04]` edge); `DashboardQuery` + `CardinalityCounters` declared in-unit |
| §3.8.2 | U-OD-33 | M-2 | **No M-2 edit** — see §0.5; row dissolved by v2.5. Preserved verbatim from v2.5. |
| §3.8.3 | U-OD-34 | M-3 | `cross_axis_edge_count` 28→26; `cross_axis_edge_breakdown` {IS:6,…}→{IS:4,…}; acc #3/#4 + 2 tests conformed |
| §4 | Dependency graph | M-1 + M-2 | Edge delta — see §4 |
| §5 | Spec-traceability | M-1 | Coverage-matrix delta — new unit U-OD-00 row; additive only |
| §6 | Auxiliary-type audit | M-1 | **NEW permanent section** — closes the M-1 gap structurally |

### §0.8 Error-type tail — inline-materialization discipline (M-1 tail)

The materializability audit's Pattern M-1 names ≈24 thin `Result<_, E>` error types (`BreakerEmissionError`, `CardinalityViolation`, `HashChainBreach`, `PreCollectorRedactionViolation`, …) with no declaration site. Per the audit's own classification and the carrier map (disposition row "Error types — per-axis — inline at first-consuming unit, sanctioned by a one-line plan note") these are **conventionally thin** (`class XViolation(HarnessError): ...`) with no shape ambiguity. R5 sanctions them by a single plan note rather than per-type carriers:

> **OD plan inline-auxiliary-type discipline (R5 note).** OD-axis `Result` error types (the `*Violation` / `*Error` / `*Breach` / `*Mismatch` / `*Pending` family) are materialized **inline at their first-consuming unit** as thin subclasses of a shared `HarnessError` base. They require no carrier unit and no `Depends on` edge. This sanctions the ≈24-type error tail named in `.harness/materializability_audit_od_plan.md` Pattern M-1. The §6 auxiliary-type audit enumerates them for visibility; their materialization is not a fork.

This note is appended to the v2.6 §3 preamble. It is not a per-unit revision.

---

## §1 New OD carrier unit — U-OD-00

### §1.0 Carrier-unit count decision (Q-R5-2)

The T1 carrier map's "Carrier-unit gap section" flagged "**1–2 new OD carrier unit(s)**" for the OD-owned undeclared types, naming three type clusters:

1. **The OTel-handle alias family** — `SpanRef` / `ChildSpanRef` / `SpanAttributes` / `EventEmission`. T2 resolved these FACTOR-OUT with the explicit verdict "**OD-owned — type-alias at U-OD-04 (OTel base-layer anchor)**." R1 §4 independently flagged U-OD-04 as "the candidate M-1 alias-carrier."
2. **OD-local audit-ledger composition types** — `AuditPayload` / `AuditLedger`. T1 cross-audit reconciliation **verified (Q4)** these are **NOT IS-exported**: IS exports `StateLedgerEntry` (the F2 6-field primitive) + the hash-chain *discipline*; the ADR-D5 audit-ledger *inherits* the IS entry shape and *adds* an `audit.*` namespace — it is an **OD-axis-owned** type that *composes against* the IS export. T2 confirms: `AuditPayload`/`AuditLedger` are OD-local; CP's `AuditLedgerEntry` is a parallel CP-spec-owned sibling family, not the same type. The U-OD-30 cross-axis IS edge resolves to `STATE_LEDGER_ENTRY_SHAPE_EXPORT` + the hash-chain discipline (C-IS-14 §14.2 / C-IS-13 §13.5), **not** to an `AuditLedger` type.
3. **Single-consumer OD observability primitives** — `DashboardRef` (U-OD-22 only), `DashboardQuery` (U-OD-31 only), `SpanRow` (U-OD-27 only), `EvictionAction` (U-OD-27 only), `HusainLoopState` (U-OD-24 only), `CardinalityCounters` (U-OD-31 only). The carrier map per-row note for these: "declare at first-consuming OD unit."

**R5 proposes the following resolution of "1–2 new OD carrier units" — decision: proposing (Q-R5-2):**

- **Cluster 1 — declared at U-OD-04, NO new unit.** Per the T2 "at U-OD-04" verdict. U-OD-04 is the OD OTel base-layer anchor (L0); the `Span*` family is the OTel span/attribute handle substrate. U-OD-04's body grows (§3.2.1 below). Every consuming unit gains a `[U-OD-04]` edge. This is carrier-growth of an existing L0 unit, not a new unit.
- **Cluster 2 — ONE new carrier unit U-OD-00.** `AuditPayload` / `AuditLedger` are the *load-bearing* OD-local audit-ledger composition types — consumed by U-OD-30's `sign_audit_entry` / `verify_hash_chain_integrity`, name-shared across the audit-ledger surface, and composing against the IS `StateLedgerEntry` export. They warrant a dedicated foundational carrier so the OD audit-ledger schema has one declaration site (the carrier-map "single carrier prevents N distinct pyright types" criterion). Named **U-OD-00** in the U-CP-00b / U-CORE-01 foundational-unit pattern (a `00`-suffixed pre-cluster anchor).
- **Cluster 3 — declared in-unit at the single consuming unit, NO new unit.** `DashboardRef`/`DashboardQuery`/`SpanRow`/`EvictionAction`/`HusainLoopState`/`CardinalityCounters` each have exactly one OD consumer. The carrier-map criterion for a *shared* carrier (≥2 consumers) is not met; a carrier unit for a single-consumer type is over-decomposition (`implementation-planner` SKILL.md §10). Each is declared in-unit at U-OD-22 / U-OD-31 / U-OD-27 / U-OD-24 respectively, with an explicit in-unit declaration note (§§3.5.5, 3.6.2, 3.7.1, 3.7.5 below).

This yields **exactly 1 new OD carrier unit (U-OD-00)** + carrier-growth at U-OD-04. The "1–2" range resolves to 1. Q-R5-2 invites the operator to instead split `AuditPayload`/`AuditLedger` apart, or to fold the Cluster-3 primitives into a second carrier U-OD-00b — R5 default is the single-unit reading above.

> **Naming note.** The new unit is **U-OD-00**, not a high-numbered unit, so it sorts as a pre-cluster L0 foundational anchor (alongside U-OD-01, U-OD-04). This mirrors the U-CP-00 / U-CP-00b / U-CORE-01 precedent: a `00`-suffixed foundational shared-types unit. The OD plan invariant count moves from 34 units to **35** (U-OD-00 + U-OD-01…U-OD-34); see §4 + §5.

---

### §1.1 U-OD-00 — unit body

Filed in the canonical per-unit plan format (`implementation-planner` SKILL.md §4.4). On ratification this body is transcribed into `Implementation_Plan_Operational_Discipline_v2_6.md` §3.0 (a new §3.0 pre-cluster sub-section).

---

#### U-OD-00 — Declare the OD-local audit-ledger composition types (`AuditPayload`, `AuditLedger`)

**Implements:** [C-OD-14 §14.5] (audit-ledger schema + 8-field SHA-256 composition surface — the cost-attribution / hash-chain composition the audit ledger inherits); [ADR-D5 v1.3 §1.4] + [ADR-D5 v1.3 §1.4.1] (audit-ledger cryptographic shape — the `audit.*` namespace the OD audit ledger adds over the IS `StateLedgerEntry` entry shape).

> **Spec-traceability note.** `AuditPayload` and `AuditLedger` are FACTOR-OUTs (T2 verdict, decided): the OD spec C-OD-14 §14.5 audit-ledger schema + ADR-D5 §1.4 audit-ledger cryptographic shape commit the audit-ledger *concept* and its field composition; the plan consumed a structured `AuditPayload` / `AuditLedger` type at U-OD-30's signature positions with no declaration site. R5 supplies the carrier. The record *shapes* are a faithful operationalization of the §14.5 8-field SHA-256 composition + the ADR-D5 §1.4.1 4-attribute `audit.signature.*` set — not a spec extension.
>
> **OD-local, NOT IS-exported (Q4-verified).** `AuditPayload`/`AuditLedger` are **OD-axis-owned**. The IS axis exports `StateLedgerEntry` (the F2 6-field primitive, C-IS-10 §10.1 / U-IS-17 manifest) and the hash-chain discipline (C-IS-13 §13.5) — there is no `AuditLedger`/`AuditPayload` record in any IS unit. The OD audit ledger *composes against* the IS export: an `AuditLedger` is a sequence of audit entries, each entry hash-chained per the IS C-IS-13 §13.5 discipline and carrying a `StateLedgerEntry`-shaped core. The U-OD-30 cross-axis IS edges (`C-IS-14 §14.2`, `C-IS-13 §13.5`) resolve to the IS-exported entry shape + hash-chain discipline — **not** to an `AuditLedger` type. No new cross-axis edge is required for `AuditPayload`/`AuditLedger`; they are within-OD-axis types.

**Depends on:** (none) — foundational; an L0 pre-cluster anchor alongside U-OD-01 and U-OD-04. U-OD-00 declares OD-local record types and imports nothing within the OD axis. *(The IS `StateLedgerEntry` shape is composed against by U-OD-30, not by U-OD-00; U-OD-00 declares the OD-local container types only.)*

**Inputs:** OD spec v1.2 §14.5 audit-ledger 8-field SHA-256 composition + field-ordering; ADR-D5 v1.3 §1.4 / §1.4.1 audit-ledger cryptographic shape (`audit.signature.*` 4-attribute set).

**Files affected:** OD-local audit-ledger composition type declaration (logical name: `od-audit-ledger-composition-types`).

**Persona linkage.** Persona §10.4 (compliance-readiness — tamper-evident audit ledger at multi-tenant cells).

**Signatures:**

```
// AuditPayload — the signable core of one audit-ledger entry.
// Composes against the IS-exported StateLedgerEntry shape (C-IS-10 §10.1):
// the audit entry inherits the F2 6-field entry core and adds the
// audit.* namespace per ADR-D5 v1.3 §1.4. AuditPayload is the pre-signature
// content over which sign_audit_entry (U-OD-30) computes the signature.
record AuditPayload {
  entry_core            : StateLedgerEntryRef   // F2 6-field entry shape, IS-exported (C-IS-10 §10.1)
  audit_namespace_attrs : Map<string, string>   // audit.* attributes per C-OD-14 §14.5
  prior_entry_hash      : string                // SHA-256 hash-chain link per C-IS-13 §13.5 discipline
}

// AuditLedger — an ordered, hash-chained sequence of signed audit entries.
// verify_hash_chain_integrity (U-OD-30) walks this sequence.
record AuditLedgerEntry {
  payload               : AuditPayload
  signature_attrs       : AuditSignatureAttributes   // 4-attribute audit.signature.* set (U-OD-30)
  entry_hash            : string                     // SHA-256 over payload, per C-OD-14 §14.5 field-ordering
}

record AuditLedger {
  entries               : List<AuditLedgerEntry>     // ordered; entries[i].payload.prior_entry_hash == entries[i-1].entry_hash
  cell_id               : CellID                     // ∈ {cell-7, cell-8} — multi-tenant cells only
}

// StateLedgerEntryRef — a thin reference to the IS-exported F2 entry shape.
// Declared here as an opaque marker; the concrete IS StateLedgerEntry type is
// resolved at the U-OD-30 cross-axis IS edge (C-IS-10 §10.1). Materialized as
// the imported IS type at execution-time; this carrier names the position.
opaque StateLedgerEntryRef : Reference
```

**Acceptance criteria:**

1. `AuditPayload` declares exactly three fields — `entry_core` (IS-exported F2 entry shape, composed-against), `audit_namespace_attrs` (the `audit.*` namespace map per C-OD-14 §14.5), `prior_entry_hash` (SHA-256 hash-chain link per the C-IS-13 §13.5 discipline).
2. `AuditLedgerEntry` declares exactly three fields — `payload : AuditPayload`, `signature_attrs : AuditSignatureAttributes` (the U-OD-30 4-attribute `audit.signature.*` set), `entry_hash` (SHA-256 over `payload` per the C-OD-14 §14.5 8-field field-ordering).
3. `AuditLedger` declares exactly two fields — `entries : List<AuditLedgerEntry>` and `cell_id : CellID`; the ledger is well-formed iff `entries[i].payload.prior_entry_hash == entries[i-1].entry_hash` for all `i > 0`.
4. `AuditPayload` / `AuditLedger` / `AuditLedgerEntry` are OD-axis-local types — they reside in the OD-axis package, NOT in `harness-core` and NOT imported from the IS axis. The IS composition surface is the `StateLedgerEntryRef` opaque marker (resolved at the U-OD-30 cross-axis IS edge), not an IS-exported `AuditLedger`.
5. No spec extension: every field is a faithful operationalization of C-OD-14 §14.5 (8-field SHA-256 composition) + ADR-D5 v1.3 §1.4 / §1.4.1 (cryptographic shape). No field is introduced that the cited contract does not commit.
6. `AuditSignatureAttributes` is consumed from U-OD-30 (the carrier of the 4-attribute `audit.signature.*` set); U-OD-00 declares `AuditLedgerEntry` referencing it. Per §4 the dependency edge is directional U-OD-30 → U-OD-00? **No** — see Q-R5-3: the `AuditSignatureAttributes` ↔ `AuditLedgerEntry` mutual reference is resolved by hosting `AuditSignatureAttributes` at U-OD-00 (moved from U-OD-30) so U-OD-00 is the single audit-type carrier and U-OD-30 consumes it via a `[U-OD-00]` edge. R5 default: **move `AuditSignatureAttributes` into U-OD-00.** See Q-R5-3.

**Tests:** `test_audit_payload_three_fields`, `test_audit_ledger_entry_three_fields`, `test_audit_ledger_two_fields`, `test_audit_ledger_hash_chain_link_invariant`, `test_audit_types_od_local_not_harness_core`, `test_audit_types_not_imported_from_is_axis`, `test_state_ledger_entry_ref_is_opaque_marker`, `test_audit_payload_no_field_beyond_c_od_14_section_14_5`.

**Rollback boundary:** Revert the OD-local audit-ledger composition type declarations. U-OD-30 `sign_audit_entry` / `verify_hash_chain_integrity` lose their typed `payload` / `ledger` parameter carrier; the M-1 undeclared-type defect at U-OD-30 reopens. A single coherent revert (one logical change). Downstream impact: U-OD-30's `[U-OD-00]` edge loses its carrier.

---

## §2 Revised FORK / CONFORM unit bodies

The 14 FORK units + 1 CONFORM unit. Each revision is the **minimum delta** required to materialize the unit pyright-strict-clean at its topological position: a type re-point + the carrier `Depends on` edge. All other surfaces of each unit are `[preserved verbatim]` from the cited predecessor (v2.5-revised units from v2.5; v2.1-preserved units from v2.1 via the v2.5 pointer chain). Per `implementation-planner` SKILL.md §8.4, substantive revisions are applied **only** at the affected surface.

> **R5 revision discipline.** No FORK-unit revision adds, drops, or re-targets a spec contract (`Implements:` unchanged at every unit). No FORK-unit revision changes an enum value set, a function body, or an acceptance criterion's substance — the M-1/M-2 fix is purely type-carrier resolution + dependency-edge completion. The M-3 fix (U-OD-34) is a determinate count conformance to the already-ratified C3-15 / v2.4 §4.5.1 edge delta.

---

### §3.2.1 U-OD-04 — Implement OTel GenAI semconv 1.41.0 base-layer attributes (R5 carrier-growth revision)

[Full-revised at R5 per §0.7 — U-OD-04 grows to declare the OTel-handle alias family `SpanRef` / `ChildSpanRef` / `SpanAttributes` / `EventEmission` (M-1 carrier; T2 FACTOR-OUT verdict "OD-owned — type-alias at U-OD-04"). **All v2.5 surfaces are preserved verbatim** — `SPAN_NAME_FORMAT`, `GenAiOperation`, `AttributeTier`, `GenAiAttribute`, `BASE_LAYER_ATTRIBUTES`, `BASE_METRIC_NAME`, acc #1–#8, tests, rollback boundary — the R5 delta is **additive only**: a new signature sub-block + a new acceptance criterion #9 + new tests. R5 does **not** touch the v2.5 verbatim-conformance surfaces.]

**Implements:** [C-OD-04 §4.1, §4.2, §4.3, §4.4, §4.5] *(unchanged from v2.5)*. **R5 addition:** [ADR-F5] (observability substrate primitive) + [ADR-D6 v1.2] (12-namespace OTel schema) — the contracts that commit the OTel span/attribute handle concept the `Span*` aliases name; plus the `Target_Stack_Commitment_v1.md` §5.2 OTel-libraries adoption (`opentelemetry-api`/`opentelemetry-sdk`).

> **Trace-target caveat (Q-R5-6).** The T2 resolution table's `SpanRef`/`SpanAttributes` rows cite "OD spec C-OD-09" as part of the FACTOR-OUT basis. But the OD plan unit assignment (v2.1 §3.4.1) shows **C-OD-09 is the per-deployment-surface sampling-mode contract — implemented by U-OD-11**, not the OTel span substrate. R5 does NOT cite C-OD-09 §9.1 on U-OD-04's `Implements` line; it traces the `Span*` family to ADR-F5 + ADR-D6 + the `Target_Stack_Commitment` OTel adoption (which T2 also cites and which is the faithful trace). The C-OD-09 mismatch in the T2 row text is surfaced as Q-R5-6 for operator confirmation — R5 does not silently re-route a cited section. The FACTOR-OUT verdict is unaffected: ADR-F5 + ADR-D6 commit the span/attribute handle concept either way.

**Depends on:** [] *(unchanged — U-OD-04 remains an L0 anchor; the `Span*` aliases are aliases of the OTel-SDK span data model, a `Target_Stack_Commitment` adoption, requiring no within-axis carrier).*

**Inputs:** *(v2.5 inputs preserved verbatim)*. **R5 addition:** OTel-SDK span/attribute data model (`opentelemetry-api` / `opentelemetry-sdk` — `Target_Stack_Commitment_v1.md` §5.2 OTel-libraries adoption) — the substrate the `SpanRef` / `ChildSpanRef` / `SpanAttributes` aliases name; `EventEmission` is the harness emission return-record over the OTel event model.

**Files affected:** *(v2.5 logical name `od-otel-genai-base-layer` preserved)*. **R5 addition:** OTel-handle alias family declaration (logical name: `od-otel-span-handle-aliases`).

**Signatures (R5 — additive `Span*` alias sub-block; all v2.5 signatures preserved verbatim):**

```
[v2.5 signature block preserved verbatim — SPAN_NAME_FORMAT, GenAiOperation,
 AttributeTier, GenAiAttribute, BASE_LAYER_ATTRIBUTES, BASE_METRIC_NAME.]

# --- R5 addition: OTel-handle alias family (M-1 carrier) ---
# Per T2 FACTOR-OUT verdict: these are harness aliases for the OTel-SDK span
# data model (Target_Stack_Commitment OTel-libraries adoption). ADR-F5
# observability substrate + ADR-D6 12-namespace OTel schema commit the
# span/attribute handle concept. NOT a harness design extension (X-AL-3
# cleared by T2).

// SpanRef — an opaque handle to an OTel span (the parent-span handle the
// harness threads through emission functions). Aliases the OTel-SDK span
// handle; the harness does not redefine the OTel span data model.
type SpanRef = OTelSpanHandle              // OTel-SDK span (opentelemetry-sdk)

// ChildSpanRef — a SpanRef known to be a child span (eval child-span
// emission per C-OD-17 §17.2). Same OTel-SDK substrate; a nominal
// distinction marking child-span emission positions.
type ChildSpanRef = OTelSpanHandle

// SpanAttributes — the OTel attribute bag (the typed attribute map a span
// carries). Aliases the OTel-SDK attribute model.
type SpanAttributes = OTelAttributeMap     // OTel-SDK attribute bag

// EventEmission — the harness return-record for a span-event emission. Per
// T2, the OD emission contracts (C-OD-09 breaker-event, C-OD-25 drift-event)
// commit the event-emission concept; EventEmission is the faithful
// factor-out return-record (NOT an OTel-SDK type — a harness record).
record EventEmission {
  emitted_at_span   : SpanRef            // the span the event was emitted at
  event_name        : string            // the OTel event name
  attribute_count   : int                // count of attributes on the emitted event
  sampled           : bool               // whether the event was sampled (head=1.0 for always-sampled classes)
}
```

**Acceptance criteria (R5 — #1–#8 preserved verbatim from v2.5; #9 added):**

1.–8. [Preserved verbatim from v2.5 §3.2.1.]

9. **(R5 — M-1 carrier criterion.)** U-OD-04 declares the OTel-handle alias family: `SpanRef` and `ChildSpanRef` are type-aliases of the OTel-SDK span handle; `SpanAttributes` is a type-alias of the OTel-SDK attribute map; `EventEmission` is a harness return-record with exactly four fields (`emitted_at_span : SpanRef`, `event_name : string`, `attribute_count : int`, `sampled : bool`). These four are the single declaration site for the `Span*` family consumed at U-OD-09 / U-OD-10 / U-OD-19 / U-OD-20 / U-OD-23 / U-OD-25 / U-OD-26 / U-OD-30 / U-OD-31. No `Span*` family member is a harness design extension — each is a faithful factor-out of the OTel-SDK substrate (`SpanRef`/`ChildSpanRef`/`SpanAttributes`) or the OD emission contracts C-OD-09/C-OD-25 (`EventEmission`) per the T2 FACTOR-OUT verdict.

**Tests (R5 — v2.5 tests preserved verbatim; R5 additions):** *(v2.5 test list preserved verbatim)*, plus: `test_span_ref_aliases_otel_sdk_span_handle`, `test_child_span_ref_aliases_otel_sdk_span_handle`, `test_span_attributes_aliases_otel_sdk_attribute_map`, `test_event_emission_four_fields`, `test_event_emission_is_harness_record_not_otel_sdk_type`, `test_span_handle_family_single_declaration_site_at_u_od_04`.

**Rollback boundary:** [v2.5 rollback boundary preserved verbatim.] **R5 addition:** Reverting the R5 carrier-growth removes the `Span*` alias family declaration; every U-OD-04 dependent that took a `[U-OD-04]` edge for the `Span*` family (U-OD-09/10/19/20/23/25/26/30/31 — see §4) loses its M-1 carrier and the undeclared-type defect reopens at those nine units. The R5 carrier-growth is a single coherent additive change.

---

### §3.3.1 U-OD-09 — Declare `harness.breaker.*` 7-attribute canonical schema (R5 M-1 revision)

[v2.5-revised unit (`BreakerScope` conformance + FF-1 carry). R5 delta: **M-1 type re-point only** — `SpanRef` and `EventEmission` at `emit_breaker_trip_span_event` are re-pointed to the U-OD-04 carrier; a `[U-OD-04]` `Depends on` edge is added. All v2.5 surfaces — `HARNESS_BREAKER_ATTRIBUTES`, `BreakerScope`, `BreakerState`, `HarnessBreakerEvent`, the FF-1 carry, acc #1–#9, tests, rollback boundary — preserved verbatim from v2.5 §3.3.1.]

**Implements:** [C-OD-07 §7.1, §7.2, §7.3] *(unchanged)*

**Depends on:** [U-OD-07, **U-OD-04**] — **R5: `[U-OD-04]` added.** `emit_breaker_trip_span_event` consumes `SpanRef` (param `parent_span_ref`) and `EventEmission` (return) — both carried at U-OD-04 per §3.2.1. v2.5 declared `Depends on: [U-OD-07]`; U-OD-07's cone reaches U-OD-04 transitively (U-OD-07 → U-OD-04) — so `GenAiAttribute` resolved transitively (audit Findings-rejected #2). But the M-1 carrier-resolution discipline (`implementation-planner` SKILL.md §7 coverage discipline) requires the **direct** edge to the carrier whose type the unit consumes at a signature position: `SpanRef`/`EventEmission` are consumed directly at U-OD-09's function signature, so a direct `[U-OD-04]` edge is declared. (Acyclic: U-OD-04 is L0; adding an inbound edge to an L0 source node creates no cycle.)

**Signatures:** [Preserved verbatim from v2.5 §3.3.1.] `emit_breaker_trip_span_event(parent_span_ref : SpanRef, event : HarnessBreakerEvent) -> Result<EventEmission, BreakerEmissionError>` — `SpanRef` and `EventEmission` now resolve to the U-OD-04 carrier (§3.2.1); `BreakerEmissionError` is inline-materialized per the §0.8 error-type discipline.

**Acceptance criteria:** [Preserved verbatim from v2.5 §3.3.1 — including the FF-1 carry at acc #2.] **R5 addition (acc #10):** `emit_breaker_trip_span_event`'s `parent_span_ref : SpanRef` and `Result<EventEmission, …>` resolve to the U-OD-04 OTel-handle alias family (`[U-OD-04]` edge declared); no `Span*` type is materialized inside U-OD-09.

**Tests:** [Preserved verbatim from v2.5.] **R5 addition:** `test_span_ref_param_resolves_to_u_od_04_carrier`, `test_event_emission_return_resolves_to_u_od_04_carrier`.

**Rollback boundary:** [Preserved verbatim from v2.5 §3.3.1.] **R5 addition:** reverting the R5 delta removes the `[U-OD-04]` edge; `SpanRef`/`EventEmission` lose their carrier reachability and the M-1 defect reopens.

---

### §3.3.2 U-OD-10 — Declare namespace collision precedence rule + cross-namespace cardinality discipline (R5 M-1 revision)

[v2.1-preserved unit (preserved verbatim into v2.5 §0.3). R5 delta: **M-1 type re-point only** — `SpanAttributes` at `enforce_otel_canonical_value` re-pointed to the U-OD-04 carrier; `[U-OD-04]` edge added. All v2.1 surfaces — `NamespacePrecedenceRule`, `NamespaceCollisionResolution`, `NAMESPACE_COLLISIONS`, `CacheTierSubsetInvariant`, acc #1–#6, tests, rollback boundary — preserved verbatim from v2.1 §3.3.2.]

**Implements:** [C-OD-08 §8.1, §8.2, §8.3] *(unchanged)*

**Depends on:** [U-OD-05, U-OD-08, U-OD-09, **U-OD-04**] — **R5: `[U-OD-04]` added.** `enforce_otel_canonical_value(span_attrs : SpanAttributes)` consumes `SpanAttributes`, carried at U-OD-04. (U-OD-04 is transitively in-cone via U-OD-05 → U-OD-04 and via U-OD-09 → U-OD-04; the direct edge is declared per the §3.3.1 carrier-resolution discipline. Acyclic — U-OD-04 L0.)

**Signatures:** [Preserved verbatim from v2.1 §3.3.2.] `enforce_otel_canonical_value(span_attrs : SpanAttributes) -> Result<(), CanonicalValueViolation>` — `SpanAttributes` resolves to the U-OD-04 carrier; `CanonicalValueViolation` inline per §0.8.

**Acceptance criteria:** [Preserved verbatim from v2.1 §3.3.2.] **R5 addition (acc #7):** `enforce_otel_canonical_value`'s `span_attrs : SpanAttributes` resolves to the U-OD-04 OTel-handle alias family (`[U-OD-04]` edge declared).

**Tests:** [Preserved verbatim from v2.1.] **R5 addition:** `test_span_attributes_param_resolves_to_u_od_04_carrier`.

**Rollback boundary:** [Preserved verbatim from v2.1 §3.3.2.] **R5 addition:** reverting removes the `[U-OD-04]` edge; the M-1 defect reopens.

---

### §3.5.2 U-OD-19 — Compose sandbox-tier overhead + per-sibling rollup at fan-out close (R5 M-1 revision)

[v2.1-preserved unit. R5 delta: **M-1 type re-point only** — `SpanRef` at `rollup_fanout_at_close` (param `parent_span_ref`) re-pointed to the U-OD-04 carrier; `[U-OD-04]` edge added. All v2.1 surfaces — `SandboxOverhead`, `SpanTotalCost`, `compose_span_total_cost`, `FanOutPattern`, `FanOutRollupResult`, acc #1–#8, tests, rollback boundary — preserved verbatim from v2.1 §3.5.2.]

**Implements:** [C-OD-14 §14.2, §14.3] *(unchanged)*

**Depends on:** [U-OD-18, U-OD-04 (cross-axis: — see note), U-AS-NN (cross-axis: AS — C-AS-15 §15.6), U-CP-NN (cross-axis: CP — C-CP-14 §14.1)] — **R5: `[U-OD-04]` added** (within-axis OD edge). `rollup_fanout_at_close(parent_span_ref : SpanRef, …)` consumes `SpanRef`, carried at U-OD-04. v2.1 declared `Depends on: [U-OD-18, +cross-axis]`; U-OD-18's cone does not reach U-OD-04 (U-OD-18 `Depends on: [U-OD-04]`? — U-OD-18 is L1 with `Depends on` reaching U-OD-04). The direct `[U-OD-04]` edge is declared regardless per the carrier-resolution discipline. (Acyclic — U-OD-04 L0.)

**Signatures:** [Preserved verbatim from v2.1 §3.5.2.] `rollup_fanout_at_close(parent_span_ref : SpanRef, sibling_costs : List<SpanTotalCost>, pattern : FanOutPattern) -> FanOutRollupResult` — `SpanRef` resolves to the U-OD-04 carrier.

**Acceptance criteria:** [Preserved verbatim from v2.1 §3.5.2.] **R5 addition (acc #9):** `rollup_fanout_at_close`'s `parent_span_ref : SpanRef` resolves to the U-OD-04 OTel-handle alias family (`[U-OD-04]` edge declared).

**Tests:** [Preserved verbatim from v2.1.] **R5 addition:** `test_parent_span_ref_param_resolves_to_u_od_04_carrier`.

**Rollback boundary:** [Preserved verbatim from v2.1 §3.5.2.] **R5 addition:** reverting removes the `[U-OD-04]` edge; the M-1 defect reopens.

---

### §3.5.3 U-OD-20 — Compose idempotency-key join + F2-12 ACTIVE affected-contract notation (R5 M-1 revision)

[v2.1/v2.2/v2.4-amended unit (v2.2 cascade Step 6b; v2.4 Form A — preserved verbatim into v2.5). R5 delta: **M-1 type re-point only** — `SpanRef` at `attach_idempotency_key_to_cost_record` (param `span`) re-pointed to the U-OD-04 carrier; `[U-OD-04]` edge added. All other surfaces — `SpanCostRecord`, the F2-12 ACTIVE notation block, `F2_12_DeferredSurface`, `F2_12_AffectedContractNotation`, `RevisionStep`, `dedupe_on_replay`, `propagate_to_subagent`, acc #1–#11, tests, rollback boundary — preserved verbatim from the v2.4-amended body carried at v2.5.]

**Implements:** [C-OD-14 §14.4, §14.5] *(unchanged)*

**Depends on:** [U-OD-18, U-OD-19, U-OD-04, U-IS-NN (cross-axis: IS — C-IS-10 §10.2)] — **R5: `[U-OD-04]` added** (within-axis OD edge). `attach_idempotency_key_to_cost_record(span : SpanRef, …)` consumes `SpanRef`, carried at U-OD-04. (Acyclic — U-OD-04 L0; the F2-12 ACTIVE notation surface is unaffected.)

**Signatures:** [Preserved verbatim.] `attach_idempotency_key_to_cost_record(span : SpanRef, parent_idempotency : string, cost_record : SpanCostRecord) -> SpanCostRecord` — `SpanRef` resolves to the U-OD-04 carrier. `SpanCostRecord` remains U-OD-20's own declared type (it is the carrier U-OD-21 depends on — see §3.5.4).

**Acceptance criteria:** [Preserved verbatim.] **R5 addition (acc #12):** `attach_idempotency_key_to_cost_record`'s `span : SpanRef` resolves to the U-OD-04 OTel-handle alias family (`[U-OD-04]` edge declared).

**Tests:** [Preserved verbatim.] **R5 addition:** `test_span_param_resolves_to_u_od_04_carrier`.

**Rollback boundary:** [Preserved verbatim.] **R5 addition:** reverting removes the `[U-OD-04]` edge; the M-1 defect reopens. (The F2-12 ACTIVE carry-forward is unaffected by the R5 delta.)

---

### §3.5.4 U-OD-21 — Compose cross-family `provider_discriminator` rollup + tokenization-version anchor (R5 M-2 revision)

[v2.1-preserved unit. R5 delta: **M-2 dependency-edge completion only** — `rollup_costs_by_axis` consumes `SpanCostRecord` (`param span_records : List<SpanCostRecord>`), declared by U-OD-20; U-OD-20 was absent from U-OD-21's `Depends on` cone and unreachable by any path. R5 adds the `[U-OD-20]` edge. All v2.1 surfaces — `CrossFamilyTag`, `RollupAxis`, `CrossFamilyCostRollup`, `rollup_costs_by_axis`, `TokenizerVersionAnchor`, `FallbackChainCostComposition`, acc #1–#8, tests, rollback boundary — preserved verbatim from v2.1 §3.5.4.]

**Implements:** [C-OD-15 §15.1, §15.2, §15.3] *(unchanged)*

**Depends on:** [U-OD-04, U-OD-18, **U-OD-20**, U-CP-NN (cross-axis: CP — C-CP-04 cross-family fallback chain)] — **R5: `[U-OD-20]` added** (within-axis OD edge; M-2 fix). `rollup_costs_by_axis(span_records : List<SpanCostRecord>, …)` consumes `SpanCostRecord`, the carrier of which is U-OD-20 (`record SpanCostRecord` at U-OD-20's Signatures block). v2.1 declared `Depends on: [U-OD-04, U-OD-18, U-CP-NN]` — U-OD-20 absent and unreachable by any dependency path (U-OD-20's deps are U-OD-18/19; U-OD-21's cone reaches U-OD-18 but not U-OD-20 — U-OD-20 is a *consumer* of U-OD-18/19, not on a path *to* U-OD-21). The M-2 fix declares the direct `[U-OD-20]` edge.

> **Acyclicity (R5 verification).** U-OD-20 sits at L3 (`Depends on: [U-OD-18, U-OD-19, +cross-axis]`); U-OD-21 sat at L4 in v2.1 §4.2. The new `U-OD-21 → U-OD-20` edge points from a higher level to a lower level — **no cycle introduced** (a consumer at L4+ depending on a carrier at L3 respects the topological order). U-OD-21 stays at L4 (it already depends on U-OD-18 at L1; adding a U-OD-20-at-L3 dependency does not raise U-OD-21's level beyond L4). §4 re-verifies the Kahn sort.

**Signatures:** [Preserved verbatim from v2.1 §3.5.4.] `rollup_costs_by_axis(span_records : List<SpanCostRecord>, axis : RollupAxis) -> List<CrossFamilyCostRollup>` — `SpanCostRecord` now resolves to the in-cone U-OD-20 carrier.

**Acceptance criteria:** [Preserved verbatim from v2.1 §3.5.4.] **R5 addition (acc #9):** `rollup_costs_by_axis`'s `span_records : List<SpanCostRecord>` consumes the U-OD-20-declared `SpanCostRecord`; the `[U-OD-20]` `Depends on` edge is declared (M-2 hidden-coupling fix).

**Tests:** [Preserved verbatim from v2.1.] **R5 addition:** `test_span_cost_record_param_carrier_u_od_20_in_cone`, `test_depends_on_u_od_20_edge_declared`.

**Rollback boundary:** [Preserved verbatim from v2.1 §3.5.4.] **R5 addition:** reverting removes the `[U-OD-20]` edge; `SpanCostRecord` loses carrier reachability and the M-2 hidden-coupling defect reopens.

---

### §3.5.5 U-OD-22 — Declare per-cell cost-attribution dashboard binding + alerting threshold composition (R5 M-1 + M-2 revision)

[v2.1-preserved unit. R5 delta: **(a) M-2** — `WorkloadClass` (CP-axis type; consumed at `AlertingThresholdComposition.per_class_cost_ceiling : Map<WorkloadClass, float>` and `compute_alerting_signal` param `workload_class : WorkloadClass`) is re-pointed to the landed `harness-core` U-CP-00 carrier; a `[U-CP-00]` edge is added. **(b) M-1** — `DashboardRef` (consumed at `DashboardBackendConsolidation` fields) has exactly one OD consumer (U-OD-22); per §1.0 Cluster-3 it is declared **in-unit**. All v2.1 surfaces — `DashboardBindingForm`, `AlertingHook`, `CellDashboardBinding`, `PER_CELL_DASHBOARD_BINDINGS`, `AlertingThresholdComposition`, `compute_alerting_signal`, `AlertingSignal`, `DashboardBackendConsolidation`, acc #1–#10, tests, rollback boundary — preserved verbatim from v2.1 §3.5.5, except the in-unit `DashboardRef` declaration is added to the Signatures block.]

**Implements:** [C-OD-16 §16.1, §16.2, §16.3] *(unchanged)*

**Depends on:** [U-OD-01, U-OD-12, U-OD-18, U-OD-19, U-OD-21, **U-CP-00 (cross-axis: core — `WorkloadClass`)**] — **R5: `[U-CP-00]` added** (cross-axis edge to the landed `harness-core` `WorkloadClass` carrier; M-2 fix). Per the carrier map disposition-3 row + R1 §3.4: `WorkloadClass` resolves via the landed U-CP-00 `harness-core` resident; the consuming unit takes a `[U-CP-00]` edge. Per T2, this is a `harness-core` *import* edge — it does **not** invert the CXA axis topology (OD consuming a `harness-core` resident is shared-substrate import, not an outbound CXA `Depends on` edge to the CP axis). The edge is annotated `(cross-axis: core)` per the R1 §3 edge-form discipline.

> **Why not a CXA OD→CP edge.** `WorkloadClass` is the spec-committed CP routing enum (C-CP-07 §7.3), promoted to `harness-core` via the landed U-CP-00 (CP plan v2.5 §2.0). The carrier map disposition-3 row for `WorkloadClass`@U-OD-22 is explicit: "if `WorkloadClass` lands in `harness-core` no CXA edge is needed (core import, not a cross-axis `Depends on`). **Recommended: core import.**" R5 takes the core-import reading. **No CXA v2.1 §2.3 edge is added; the OD→CP edge count is unchanged** (this is relevant to M-3 — see U-OD-34: the `WorkloadClass` resolution does NOT add a 13th OD→CP edge).

**Signatures (R5 — in-unit `DashboardRef` declaration added; all v2.1 signatures preserved verbatim):**

```
[v2.1 signature block preserved verbatim — DashboardBindingForm, AlertingHook,
 CellDashboardBinding, PER_CELL_DASHBOARD_BINDINGS, AlertingThresholdComposition,
 compute_alerting_signal, AlertingSignal, DashboardBackendConsolidation.]

# --- R5 addition: in-unit DashboardRef declaration (M-1, §1.0 Cluster-3) ---
# DashboardRef has exactly one OD consumer (U-OD-22 — DashboardBackendConsolidation
# fields cost_attribution_dashboard / operator_burden_eval_dashboard /
# consolidated_view). Single-consumer → declared in-unit, not a carrier unit.
// DashboardRef — an opaque handle to a per-cell dashboard surface (TUI ring-buffer
// query view, or named backend dashboard, per DashboardBindingForm). Resolved to
// the per-cell backend's dashboarding model at deployment-binding time.
opaque DashboardRef : Reference

# WorkloadClass is NOT declared here — it is the harness-core U-CP-00 resident,
# imported via the [U-CP-00] edge. The Map<WorkloadClass, float> at
# AlertingThresholdComposition.per_class_cost_ceiling and the workload_class
# param of compute_alerting_signal resolve to the imported harness-core type.
```

**Acceptance criteria:** [Preserved verbatim from v2.1 §3.5.5.] **R5 additions:**

11. **(M-2.)** `AlertingThresholdComposition.per_class_cost_ceiling : Map<WorkloadClass, float>` and `compute_alerting_signal`'s `workload_class : WorkloadClass` parameter resolve to the `harness-core` `WorkloadClass` enum (landed U-CP-00); the `[U-CP-00 (cross-axis: core)]` edge is declared. No `WorkloadClass` type is materialized inside U-OD-22.
12. **(M-1.)** `DashboardRef` is declared in-unit as an opaque marker (single-consumer type per §1.0 Cluster-3); `DashboardBackendConsolidation`'s three `DashboardRef`-typed fields resolve to this in-unit declaration. No carrier unit and no carrier edge for `DashboardRef`.

**Tests:** [Preserved verbatim from v2.1.] **R5 additions:** `test_workload_class_resolves_to_harness_core_u_cp_00`, `test_depends_on_u_cp_00_core_edge_declared`, `test_dashboard_ref_declared_in_unit_opaque_marker`, `test_no_workload_class_materialized_in_unit`.

**Rollback boundary:** [Preserved verbatim from v2.1 §3.5.5.] **R5 addition:** reverting removes the `[U-CP-00]` edge and the in-unit `DashboardRef` declaration; the M-1 + M-2 defects reopen.

---

### §3.6.1 U-OD-23 — Declare five operator-burden eval primitives + separate-child-span emission commitment (R5 M-1 revision)

[v2.1-preserved unit. R5 delta: **M-1 type re-point only** — `ChildSpanRef` at `emit_eval_as_child_span` (return type) re-pointed to the U-OD-04 carrier; `[U-OD-04]` edge added. `ChildSpanRef` is in the `SpanRef` family — same T2 FACTOR-OUT verdict (OTel-handle alias at U-OD-04). All v2.1 surfaces — `OperatorBurdenEvalPrimitive`, `ComputationKind`, `EvalPrimitiveDeclaration`, `EVAL_PRIMITIVE_DECLARATIONS`, `EvalEmissionContract`, both function signatures, acc #1–#10, tests, rollback boundary — preserved verbatim from v2.1 §3.6.1.]

**Implements:** [C-OD-17 §17.1, §17.2] *(unchanged)*

**Depends on:** [U-OD-04, U-AS-NN (cross-axis: AS — C-AS-15 §15.4 + C-AS-14 §14.2), U-CP-NN (cross-axis: CP — C-CP-20 §20.6)] — **U-OD-04 already present** (v2.1 declared `Depends on: [U-OD-04, +cross-axis]`). **R5: no new edge** — the M-1 fix at U-OD-23 is purely the `ChildSpanRef` carrier re-point; the `[U-OD-04]` edge already exists. (This is the cleanest FORK unit — only a type-resolution annotation is needed.)

**Signatures:** [Preserved verbatim from v2.1 §3.6.1.] `emit_eval_as_child_span(parent_span_ref, primitive, value) -> Result<ChildSpanRef, EmissionContractViolation>` — `ChildSpanRef` now resolves to the U-OD-04 carrier (§3.2.1); `parent_span_ref` is `SpanRef` (also U-OD-04); `EmissionContractViolation` inline per §0.8.

**Acceptance criteria:** [Preserved verbatim from v2.1 §3.6.1.] **R5 addition (acc #11):** `emit_eval_as_child_span`'s `Result<ChildSpanRef, …>` return and `parent_span_ref : SpanRef` resolve to the U-OD-04 OTel-handle alias family; the `[U-OD-04]` edge (already declared in v2.1) is the carrier edge — no new edge needed.

**Tests:** [Preserved verbatim from v2.1.] **R5 addition:** `test_child_span_ref_return_resolves_to_u_od_04_carrier`.

**Rollback boundary:** [Preserved verbatim from v2.1 §3.6.1.] **R5 note:** the R5 delta adds no edge; reverting R5 is a no-op at the dependency-graph level for U-OD-23 (the type-resolution annotation is the only change).

---

### §3.6.2 U-OD-24 — Declare per-cell dashboard binding scaling for operator-burden eval primitives (R5 M-1 revision)

[v2.1-preserved unit. R5 delta: **M-1 type re-point only** — `HusainLoopState` at `run_husain_loop_at_cell` (return type) has exactly one OD consumer (U-OD-24); per §1.0 Cluster-3 it is declared **in-unit**. All v2.1 surfaces — `EvalDashboardForm`, `AlignmentFloorAlertingPosture`, `HusainLoopBinding`, `CellEvalDashboardBinding`, `PER_CELL_EVAL_DASHBOARD_BINDINGS`, `run_husain_loop_at_cell`, acc #1–#7, tests, rollback boundary — preserved verbatim from v2.1 §3.6.2, except the in-unit `HusainLoopState` declaration is added.]

**Implements:** [C-OD-17 §17.3] *(unchanged)*

**Depends on:** [U-OD-01, U-OD-22, U-OD-23, U-OD-27] — **R5: no new edge.** `HusainLoopState` is declared in-unit (single-consumer per §1.0 Cluster-3); no carrier unit, no carrier edge.

**Signatures (R5 — in-unit `HusainLoopState` declaration added):**

```
[v2.1 signature block preserved verbatim — EvalDashboardForm,
 AlignmentFloorAlertingPosture, HusainLoopBinding, CellEvalDashboardBinding,
 PER_CELL_EVAL_DASHBOARD_BINDINGS.]

# --- R5 addition: in-unit HusainLoopState declaration (M-1, §1.0 Cluster-3) ---
# HusainLoopState has exactly one OD consumer (U-OD-24 — run_husain_loop_at_cell
# return). Single-consumer → declared in-unit.
// HusainLoopState — the state of one Husain manual-review → categorize →
// automate → align loop iteration at a cell (per c8-eval-engineer SKILL.md
// loop discipline; C-OD-17 §17.3 husain-loop binding). Faithful factor-out of
// the §17.3 husain-loop binding concept.
record HusainLoopState {
  cell_id            : CellID
  loop_binding       : HusainLoopBinding        // RING_BUFFER / BACKEND_HOSTED / PER_TENANT_BACKEND_HOSTED
  primitive          : OperatorBurdenEvalPrimitive   // the primitive under review (from U-OD-23)
  iteration_phase    : string                   // "manual-review" | "categorize" | "automate" | "align"
}
```

**Acceptance criteria:** [Preserved verbatim from v2.1 §3.6.2.] **R5 addition (acc #8):** `run_husain_loop_at_cell`'s `-> HusainLoopState` return resolves to the in-unit `HusainLoopState` record (single-consumer type per §1.0 Cluster-3); no carrier unit. `HusainLoopState` is a faithful factor-out of the C-OD-17 §17.3 husain-loop binding — not a design extension.

**Tests:** [Preserved verbatim from v2.1.] **R5 addition:** `test_husain_loop_state_declared_in_unit`, `test_run_husain_loop_returns_husain_loop_state`.

**Rollback boundary:** [Preserved verbatim from v2.1 §3.6.2.] **R5 addition:** reverting removes the in-unit `HusainLoopState` declaration; the M-1 defect reopens.

---

### §3.6.3 U-OD-25 — Declare alignment-floor drift detection + drift-detection emission shape (R5 M-1 revision)

[v2.1-preserved unit. R5 delta: **M-1 type re-point only** — `SpanRef` and `EventEmission` at `emit_drift_event` re-pointed to the U-OD-04 carrier; `[U-OD-04]` edge added. All v2.1 surfaces — `AlignmentFloorPrimitive`, `AlignmentFloorThreshold`, `ObservationWindow`, `DRIFT_DETECTED_EVENT_NAME`, `DriftDetectedEventAttributes`, `detect_drift`, `emit_drift_event`, acc #1–#9, tests, rollback boundary — preserved verbatim from v2.1 §3.6.3.]

**Implements:** [C-OD-18 §18.1, §18.2] *(unchanged)*

**Depends on:** [U-OD-11, U-OD-23, U-OD-24, **U-OD-04**] — **R5: `[U-OD-04]` added** (within-axis OD edge). `emit_drift_event(parent_span_ref : SpanRef, attrs) -> Result<EventEmission, DriftEmissionError>` consumes `SpanRef` + `EventEmission`, carried at U-OD-04. (Acyclic — U-OD-04 L0.)

**Signatures:** [Preserved verbatim from v2.1 §3.6.3.] `emit_drift_event(parent_span_ref : SpanRef, attrs : DriftDetectedEventAttributes) -> Result<EventEmission, DriftEmissionError>` — `SpanRef`/`EventEmission` resolve to the U-OD-04 carrier; `DriftEmissionError` inline per §0.8.

**Acceptance criteria:** [Preserved verbatim from v2.1 §3.6.3.] **R5 addition (acc #10):** `emit_drift_event`'s `parent_span_ref : SpanRef` and `Result<EventEmission, …>` resolve to the U-OD-04 OTel-handle alias family (`[U-OD-04]` edge declared).

**Tests:** [Preserved verbatim from v2.1.] **R5 addition:** `test_span_ref_param_resolves_to_u_od_04_carrier`, `test_event_emission_return_resolves_to_u_od_04_carrier`.

**Rollback boundary:** [Preserved verbatim from v2.1 §3.6.3.] **R5 addition:** reverting removes the `[U-OD-04]` edge; the M-1 defect reopens.

---

### §3.6.4 U-OD-26 — Declare eval-vs-runtime-gate distinction via `gen_ai.eval.kind` discriminator (R5 M-1 revision)

[v2.1-preserved unit. R5 delta: **M-1 type re-point only** — `SpanAttributes` at `classify_eval_span` re-pointed to the U-OD-04 carrier; `[U-OD-04]` edge added. All v2.1 surfaces — `EvalKindDiscriminator`, `EVAL_KIND_ATTRIBUTE_NAME`, `EvalSpanShape`, `SamplingPostureF18`, `EVAL_SPAN_SHAPES`, `classify_eval_span`, `validate_eval_span_routing`, acc #1–#9, tests, rollback boundary — preserved verbatim from v2.1 §3.6.4.]

**Implements:** [C-OD-18 §18.3] *(unchanged)*

**Depends on:** [U-OD-23, U-OD-04, U-CP-NN (cross-axis: CP — C-CP-21 §21.5)] — **R5: `[U-OD-04]` added** (within-axis OD edge). `classify_eval_span(attrs : SpanAttributes)` consumes `SpanAttributes`, carried at U-OD-04. (U-OD-23 is in U-OD-26's cone and U-OD-23 → U-OD-04 — `SpanAttributes` resolves transitively; the direct edge is declared per the carrier-resolution discipline. Acyclic — U-OD-04 L0.)

**Signatures:** [Preserved verbatim from v2.1 §3.6.4.] `classify_eval_span(attrs : SpanAttributes) -> Option<EvalKindDiscriminator>` — `SpanAttributes` resolves to the U-OD-04 carrier; `EvalShapeViolation` inline per §0.8.

**Acceptance criteria:** [Preserved verbatim from v2.1 §3.6.4.] **R5 addition (acc #10):** `classify_eval_span`'s `attrs : SpanAttributes` resolves to the U-OD-04 OTel-handle alias family (`[U-OD-04]` edge declared).

**Tests:** [Preserved verbatim from v2.1.] **R5 addition:** `test_span_attributes_param_resolves_to_u_od_04_carrier`.

**Rollback boundary:** [Preserved verbatim from v2.1 §3.6.4.] **R5 addition:** reverting removes the `[U-OD-04]` edge; the M-1 defect reopens.

---

### §3.7.1 U-OD-27 — Implement local-first OTLP collector at solo-developer × local-development cell (R5 M-1 revision)

[v2.1-preserved unit. R5 delta: **M-1 type re-point only** — `SpanRow` (at `query_ring_buffer_via_tui` return) and `EvictionAction` (at `evict_oldest_per_ring_buffer_policy` return) each have exactly one OD consumer (U-OD-27); per §1.0 Cluster-3 both are declared **in-unit**. All v2.1 surfaces — `CollectorTopology`, `InProcessCollectorBinding`, `RingBufferTraceStoragePolicy`, `TuiTraceBrowserSurface`, `TuiQuery`, `BATCH_SPAN_PROCESSOR_*` consts, `bind_in_process_collector`, acc #1–#13, tests, rollback boundary — preserved verbatim from v2.1 §3.7.1, except the in-unit `SpanRow` + `EvictionAction` declarations are added.]

**Implements:** [C-OD-19 §19.1, §19.2, §19.3] *(unchanged)*

**Depends on:** [U-OD-01, U-OD-23, U-IS-NN (cross-axis: IS — C-IS-13 §13.2), U-IS-NN (cross-axis: IS — C-IS-08 §8.4)] — **R5: no new edge.** `SpanRow` and `EvictionAction` are declared in-unit (single-consumer per §1.0 Cluster-3).

**Signatures (R5 — in-unit `SpanRow` + `EvictionAction` declarations added):**

```
[v2.1 signature block preserved verbatim — CELL_1, CollectorTopology,
 InProcessCollectorBinding, RingBufferTraceStoragePolicy, TuiTraceBrowserSurface,
 TuiQuery, BATCH_SPAN_PROCESSOR_WINDOW, BATCH_SPAN_PROCESSOR_BATCH_SIZE,
 bind_in_process_collector.]

# --- R5 addition: in-unit SpanRow + EvictionAction declarations (M-1, §1.0 Cluster-3) ---
# Both have exactly one OD consumer (U-OD-27 — query_ring_buffer_via_tui /
# evict_oldest_per_ring_buffer_policy returns). Single-consumer → declared in-unit.

// SpanRow — one row of the sqlite ring-buffer trace store (a span persisted
// to the C-IS-13 §13.2 sqlite substrate). Faithful factor-out of the §19.2
// ring-buffer trace storage concept.
record SpanRow {
  span_id            : string
  trace_id           : string
  span_name          : string
  start_time_unix_ns : int
  duration_ns        : int
  attributes_json    : string         // serialized SpanAttributes for sqlite storage
}

// EvictionAction — the outcome of one ring-buffer eviction per the §19.2
// FIFO-by-age policy. Faithful factor-out of the §19.2 eviction concept.
record EvictionAction {
  evicted_span_count : int
  evicted_bytes      : int
  eviction_reason    : string         // "MAX_AGE_EXCEEDED" | "MAX_BYTES_EXCEEDED"
}
```

**Acceptance criteria:** [Preserved verbatim from v2.1 §3.7.1.] **R5 addition (acc #14):** `query_ring_buffer_via_tui`'s `-> List<SpanRow>` and `evict_oldest_per_ring_buffer_policy`'s `-> Result<EvictionAction, RingBufferError>` resolve to the in-unit `SpanRow` / `EvictionAction` records (single-consumer types per §1.0 Cluster-3); no carrier unit. Both are faithful factor-outs of the C-OD-19 §19.2 ring-buffer trace storage — not design extensions. `RingBufferError` inline per §0.8.

**Tests:** [Preserved verbatim from v2.1.] **R5 additions:** `test_span_row_declared_in_unit`, `test_eviction_action_declared_in_unit`, `test_query_ring_buffer_returns_list_of_span_row`, `test_evict_oldest_returns_eviction_action`.

**Rollback boundary:** [Preserved verbatim from v2.1 §3.7.1.] **R5 addition:** reverting removes the in-unit `SpanRow` + `EvictionAction` declarations; the M-1 defect reopens.

---

### §3.7.4 U-OD-30 — Declare per-tenant trace separation + cryptographic audit ledger composition (R5 M-1 revision)

[v2.5-revised unit (`SignatureAlgorithm` conformance). R5 delta: **M-1 type re-point** — (a) `SpanRef` at `assert_tenant_id_on_every_span_at_multi_tenant_cells` (param `span`) re-pointed to the U-OD-04 carrier; (b) `AuditPayload` (at `sign_audit_entry` param `payload`) and `AuditLedger` (at `verify_hash_chain_integrity` param `ledger`) re-pointed to the new U-OD-00 carrier (§1.1); `[U-OD-04]` and `[U-OD-00]` edges added. **Per Q-R5-3 default, `AuditSignatureAttributes` is MOVED from U-OD-30 to U-OD-00** so U-OD-00 is the single audit-type carrier — see Q-R5-3. All other v2.5 surfaces — `TenantSeparationStrategy`, `PerTenantSeparation`, `PER_TENANT_SEPARATION_BINDINGS`, `SignatureAlgorithm`, the three function signatures, acc #1–#14, Cross-axis dependency resolution, Persona linkage, tests, rollback boundary — preserved verbatim from v2.5 §3.7.4.]

**Implements:** [C-OD-21 §21.1, §21.2, §21.3] *(unchanged)*

**Depends on:** [U-OD-01, U-OD-02, U-OD-28, **U-OD-04**, **U-OD-00**, U-IS-NN (cross-axis: IS — C-IS-14 §14.2), U-IS-NN (cross-axis: IS — C-IS-13 §13.5), U-CP-NN (cross-axis: CP — C-CP-20 §20.4)] — **R5: `[U-OD-04]` + `[U-OD-00]` added** (both within-axis OD edges). `assert_tenant_id_on_every_span_at_multi_tenant_cells(span : SpanRef, …)` consumes `SpanRef` (U-OD-04 carrier); `sign_audit_entry(payload : AuditPayload, …)` and `verify_hash_chain_integrity(ledger : AuditLedger)` consume the U-OD-00 audit-ledger composition types. (Acyclic — both U-OD-00 and U-OD-04 are L0 source nodes; inbound edges to L0 nodes create no cycle. The cross-axis IS edges resolve to `StateLedgerEntry` + the hash-chain discipline, NOT to `AuditLedger` — see §1.0.)

**Signatures (R5 — `SpanRef`/`AuditPayload`/`AuditLedger` carrier-resolved; `AuditSignatureAttributes` moved to U-OD-00 per Q-R5-3):**

```
[v2.5 signature block preserved verbatim — TenantSeparationStrategy,
 PerTenantSeparation, PER_TENANT_SEPARATION_BINDINGS, SignatureAlgorithm,
 AUDIT_SIGNATURE_REQUIRED_AT_TIER_5_LEDGER.]

# R5 NOTE: AuditSignatureAttributes (the 4-attribute audit.signature.* record)
# is MOVED to U-OD-00 (§1.1) so the OD audit-ledger types have a single carrier
# (Q-R5-3 default). U-OD-30 consumes it via the [U-OD-00] edge. If the operator
# rejects the move (Q-R5-3 alternative), AuditSignatureAttributes stays declared
# here and U-OD-00 takes a [U-OD-30] edge instead — see Q-R5-3.

fn sign_audit_entry(payload : AuditPayload, key_id : string, algo : SignatureAlgorithm)
  -> AuditSignatureAttributes
  // payload : AuditPayload          -> U-OD-00 carrier ([U-OD-00] edge)
  // AuditSignatureAttributes        -> U-OD-00 carrier (moved per Q-R5-3)

fn verify_hash_chain_integrity(ledger : AuditLedger) -> Result<(), HashChainBreach>
  // ledger : AuditLedger            -> U-OD-00 carrier ([U-OD-00] edge)
  // HashChainBreach                 -> inline per §0.8

fn assert_tenant_id_on_every_span_at_multi_tenant_cells(span : SpanRef, cell_id : CellID)
  -> Result<(), TenantIdMissingViolation>
  // span : SpanRef                  -> U-OD-04 carrier ([U-OD-04] edge)
  // TenantIdMissingViolation        -> inline per §0.8
```

**Acceptance criteria:** [Preserved verbatim from v2.5 §3.7.4 — including the v2.5-conformed acc #6/#7 `SignatureAlgorithm` surfaces.] **R5 additions:**

15. **(M-1.)** `assert_tenant_id_on_every_span_at_multi_tenant_cells`'s `span : SpanRef` resolves to the U-OD-04 OTel-handle alias family (`[U-OD-04]` edge declared).
16. **(M-1.)** `sign_audit_entry`'s `payload : AuditPayload` and `verify_hash_chain_integrity`'s `ledger : AuditLedger` resolve to the U-OD-00 OD-local audit-ledger composition types (`[U-OD-00]` edge declared). `AuditPayload`/`AuditLedger` are OD-axis-local — NOT IS-exported (the cross-axis IS edges resolve to `StateLedgerEntry` + the hash-chain discipline only). Per Q-R5-3 default, `AuditSignatureAttributes` is carried at U-OD-00.

**Tests:** [Preserved verbatim from v2.5.] **R5 additions:** `test_span_param_resolves_to_u_od_04_carrier`, `test_audit_payload_param_resolves_to_u_od_00_carrier`, `test_audit_ledger_param_resolves_to_u_od_00_carrier`, `test_audit_types_not_resolved_via_is_cross_axis_edge`, `test_depends_on_u_od_00_and_u_od_04_edges_declared`.

**Rollback boundary:** [Preserved verbatim from v2.5 §3.7.4.] **R5 addition:** reverting removes the `[U-OD-04]` + `[U-OD-00]` edges; `SpanRef` and the audit-ledger composition types lose carrier reachability and the M-1 defect reopens.

---

### §3.7.5 U-OD-31 — Compose pre-collector redaction + cross-tenant aggregation prohibition at multi-tenant cells (R5 M-1 revision)

[v2.1-preserved unit. R5 delta: **M-1 type re-point** — (a) `SpanAttributes` at `assert_pre_collector_redaction_applied` (param `span_attrs`) re-pointed to the U-OD-04 carrier; `[U-OD-04]` edge added. (b) `DashboardQuery` (at `reject_cross_tenant_query` param `query`) and `CardinalityCounters` (at `assert_per_tenant_cardinality_isolation` param `observed`) each have exactly one OD consumer (U-OD-31); per §1.0 Cluster-3 both are declared **in-unit**. All v2.1 surfaces — `CrossTenantAggregationProhibition`, `CROSS_TENANT_AGGREGATION_PROHIBITION`, the four function signatures, acc #1–#9, tests, rollback boundary — preserved verbatim from v2.1 §3.7.5, except the in-unit `DashboardQuery` + `CardinalityCounters` declarations are added.]

**Implements:** [C-OD-21 §21.4, §21.5] *(unchanged)*

**Depends on:** [U-OD-13, U-OD-14, U-OD-15, U-OD-16, U-OD-22, U-OD-24, U-OD-25, U-OD-30, **U-OD-04**] — **R5: `[U-OD-04]` added** (within-axis OD edge). `assert_pre_collector_redaction_applied(span_attrs : SpanAttributes, …)` consumes `SpanAttributes`, carried at U-OD-04. (U-OD-04 is transitively in-cone via several deps; the direct edge is declared per the carrier-resolution discipline. Acyclic — U-OD-04 L0. `DashboardQuery` + `CardinalityCounters` are declared in-unit — no carrier edge.)

**Signatures (R5 — in-unit `DashboardQuery` + `CardinalityCounters` declarations added):**

```
[v2.1 signature block preserved verbatim — CrossTenantAggregationProhibition,
 CROSS_TENANT_AGGREGATION_PROHIBITION, assert_pre_collector_redaction_applied,
 reject_cross_tenant_query, assert_per_tenant_cardinality_isolation,
 assert_per_tenant_alerting_isolation.]

# --- R5 addition: in-unit DashboardQuery + CardinalityCounters declarations
#     (M-1, §1.0 Cluster-3) ---
# Both have exactly one OD consumer (U-OD-31). Single-consumer → declared in-unit.

// DashboardQuery — a query constructed against the per-cell dashboard surface,
// inspected at construction time for cross-tenant scope violations per §21.5.
// Faithful factor-out of the §21.5 dashboard-query-construction-time
// enforcement concept.
record DashboardQuery {
  cell_id            : CellID
  tenant_id_scope    : Option<string>     // None == unscoped (rejected at multi-tenant cells)
  aggregation_dims   : Set<string>        // dimensions the query aggregates over
  queried_attributes : Set<string>        // attribute names referenced (cardinality-safe per U-OD-14)
}

// CardinalityCounters — observed per-tenant cardinality counts, checked against
// the U-OD-13 tenant_rate_limit per §21.4. Faithful factor-out of the §21.4
// per-tenant cardinality isolation concept.
record CardinalityCounters {
  tenant_id          : string
  observed_series    : int                // observed distinct attribute-value series for this tenant
  observation_window : string             // the window over which the count was taken
}
```

**Acceptance criteria:** [Preserved verbatim from v2.1 §3.7.5.] **R5 additions:**

10. **(M-1.)** `assert_pre_collector_redaction_applied`'s `span_attrs : SpanAttributes` resolves to the U-OD-04 OTel-handle alias family (`[U-OD-04]` edge declared).
11. **(M-1.)** `reject_cross_tenant_query`'s `query : DashboardQuery` and `assert_per_tenant_cardinality_isolation`'s `observed : CardinalityCounters` resolve to the in-unit `DashboardQuery` / `CardinalityCounters` records (single-consumer types per §1.0 Cluster-3); no carrier unit. Both are faithful factor-outs of C-OD-21 §21.4 / §21.5 — not design extensions.

**Tests:** [Preserved verbatim from v2.1.] **R5 additions:** `test_span_attributes_param_resolves_to_u_od_04_carrier`, `test_dashboard_query_declared_in_unit`, `test_cardinality_counters_declared_in_unit`.

**Rollback boundary:** [Preserved verbatim from v2.1 §3.7.5.] **R5 addition:** reverting removes the `[U-OD-04]` edge and the in-unit `DashboardQuery` + `CardinalityCounters` declarations; the M-1 defect reopens.

---

### §3.8.3 U-OD-34 — Author substrate seam exports aggregate manifest + F2-12 carry-forward inheritance declaration (R5 M-3 CONFORM revision)

[v2.1-preserved unit (preserved verbatim into v2.5 §0.3). R5 delta: **M-3 count conformance only** — the hardcoded `cross_axis_edge_count = 28` and `cross_axis_edge_breakdown = {IS: 6, AS: 10, CP: 12}` are conformed to the v2.4 §4.5.1-canonical **26 total / {IS: 4, AS: 10, CP: 12}**; acceptance criteria #3 and #4 and the two tests `test_cross_axis_edge_count_twenty_eight` / `test_cross_axis_edge_breakdown_6_10_12` are conformed. This is a **determinate** propagation of the already-operator-ratified C3-15 Path (i-refined) IS-consuming-edge delete/remap (v2.4 §4.5.1) — the v2.5 verbatim pass missed it by preserving U-OD-34 verbatim. All other U-OD-34 surfaces — `SubstrateSeamExport`, `SubstrateSeamExportsManifest` (except the two count fields), `F2_12_CarryForwardInheritance`, `ManifestScope`, `ConsumerAxis`, the 8-export manifest content table, acc #1/#2/#5–#12, the F2-12 tests, rollback boundary — preserved verbatim from v2.1 §3.8.3.]

**Implements:** [C-OD-23 §23.1, §23.2, §23.3, §23.4] *(unchanged)*

**Depends on:** [Preserved verbatim from v2.1 §3.8.3 — 19 within-OD edges + 4 cross-axis terminal-exporter references (U-IS-17, U-AS-33, U-CP-54, U-CP-55).] **R5: no `Depends on` delta** — U-OD-34 aggregates the OD axis; the M-3 fix is a count-value conformance, not a graph edit. *(Note: U-OD-00 is a new L0 unit but is NOT a U-OD-34 dependency — U-OD-00 declares OD-local audit types consumed only by U-OD-30; it does not contribute a substrate seam export. U-OD-34's `Depends on` list is unchanged. See §4.)*

**Signatures (R5 — `cross_axis_edge_count` + `cross_axis_edge_breakdown` conformed; all else preserved verbatim from v2.1):**

```
[v2.1 signature block preserved verbatim — SubstrateSeamExport, ConsumerAxis,
 F2_12_CarryForwardInheritance, ManifestScope, OD_SUBSTRATE_SEAM_EXPORTS_MANIFEST.]

record SubstrateSeamExportsManifest {
  exports                          : List<SubstrateSeamExport>   // 8 export sub-sections per §23.1
  cross_axis_edge_count            : int                         // R5 M-3: = 26 (was 28)
  cross_axis_edge_breakdown        : Map<ConsumerAxis, int>     // R5 M-3: {IS: 4, AS: 10, CP: 12} (was {IS: 6, …})
  f2_12_carry_forward_inheritance  : F2_12_CarryForwardInheritance
  manifest_scope                   : ManifestScope
}
// R5 M-3 conformance: the IS-consuming edge count is 4, not 6 — per
// Implementation_Plan_Operational_Discipline_v2_4.md §4.5.1 (C3-15 Path
// (i-refined): rows 2+3 of the v2.3 6-edge IS enumeration deleted as
// OD-internal mis-routed; rows 4+5 remapped to canonical IS contracts).
// Total = 4 + 10 + 12 = 26. The v2.4 §4.5.1 4-edge enumeration is canonical
// and is preserved verbatim at v2.5 §0.3 — this unit's signature must agree.
```

**Acceptance criteria (R5 — #3, #4 conformed to v2.4 §4.5.1; #1/#2/#5–#12 preserved verbatim from v2.1):**

1.–2. [Preserved verbatim from v2.1 §3.8.3.]

3. **(R5 M-3 conformance.)** `cross_axis_edge_count == 26` per `Implementation_Plan_Operational_Discipline_v2_4.md` §4.5.1 (C3-15 Path (i-refined) IS-consuming-edge delete/remap). *Note: the v2.1 body cited "per Stage 4 §4.6" with value 28 — that citation predates the C3-15 delta; the canonical count is the v2.4 §4.5.1 enumeration, 4 IS + 10 AS + 12 CP = 26.*

4. **(R5 M-3 conformance.)** `cross_axis_edge_breakdown == {IS: 4, AS: 10, CP: 12}` per v2.4 §4.5.1. The IS count is **4** (the v2.4 §4.5.1 enumeration: rows 2+3 of the prior 6-edge IS set deleted as OD-internal mis-routed; rows 4+5 remapped). AS (10) and CP (12) are unchanged from v2.1.

5.–12. [Preserved verbatim from v2.1 §3.8.3 — the F2-12 carry-forward inheritance criteria, manifest-scope criterion, and terminal-exporter-reference criterion.]

> **Manifest content table — §23.1 8-export sub-sections.** [Preserved verbatim from v2.1 §3.8.3.] The 8-export manifest content table is **unaffected** by the M-3 conformance — the table enumerates *exports* (8 sub-sections), not cross-axis *edge counts*. The `cross_axis_edge_targets` column entries (`U-IS-17`, `U-AS-33`, `U-CP-54`, `U-CP-55`) are unchanged; the M-3 fix corrects only the aggregate `cross_axis_edge_count` / `cross_axis_edge_breakdown` scalar fields, not the per-export target lists.

**Tests (R5 — two stale tests conformed; all else preserved verbatim from v2.1):**

The v2.1 test list named `test_cross_axis_edge_count_twenty_eight` and `test_cross_axis_edge_breakdown_6_10_12` — both assert the pre-C3-15 values and **would fail against the v2.4-canonical edge graph**. R5 conforms them:

- `test_cross_axis_edge_count_twenty_eight` → **`test_cross_axis_edge_count_twenty_six`** (asserts `cross_axis_edge_count == 26`).
- `test_cross_axis_edge_breakdown_6_10_12` → **`test_cross_axis_edge_breakdown_4_10_12`** (asserts `cross_axis_edge_breakdown == {IS: 4, AS: 10, CP: 12}`).

All other U-OD-34 tests (`test_exports_cardinality_eight`, the F2-12 test family, `test_manifest_references_*`, etc.) preserved verbatim from v2.1 §3.8.3.

**Rollback boundary:** [Preserved verbatim from v2.1 §3.8.3.] **R5 M-3 revert appendix:** Reverting the R5 M-3 conformance restores the stale `28` / `{IS: 6, …}` count + the two pre-C3-15 tests — i.e., a regression to the `CXA-OD-IS-EDGE-DRIFT` defect contradicting the operator-ratified v2.4 §4.5.1 edge delta; the revert MUST NOT be performed absent a re-disposition of C3-15.

---

## §3 Preserved-verbatim units

The following 19 units carry **no R5 delta** and are `[preserved verbatim]` from their cited predecessor body. Per `implementation-planner` SKILL.md §8.4, the preserved-verbatim list and the actual v2.6 file must agree.

| Unit | Verdict (materializability audit) | Preserved from | Note |
|---|---|---|---|
| U-OD-01 | CLEARED | **v2.1 §3.1.1 — see §7** | NOT a no-delta unit — U-OD-01 is the R1 §3.4 declaration-site conversion, revised at §7 below. Listed here for completeness; its R5 revision is at §7. |
| U-OD-02 | CLEARED | v2.5 §3.1.2 | v2.5-revised (BackendClass conformance); no M-1/M-2/M-3 finding |
| U-OD-03 | CLEARED | v2.1 §3.1.3 | All types in-unit-declared |
| U-OD-05 | CLEARED | v2.1 §3.2.2 | `NamespaceSourceAxis`/`NamespaceMapRow` in-unit; error-type tail inline per §0.8 |
| U-OD-06 | CLEARED | v2.1 §3.2.3 | `Set<string>` const; cross-axis U-AS-33 edge declared |
| U-OD-07 | CLEARED | v2.1 §3.2.4 | `Set<string>` const; cross-axis U-CP-54 edge declared |
| U-OD-08 | CLEARED | v2.1 §3.2.5 | `F3LifecycleEventClass`/`LifecycleEventMapping` in-unit |
| U-OD-11 | CLEARED | v2.5 §3.4.1 | v2.5-revised (always-sampled set conformance); `SamplingDecision` inline per §0.8 |
| U-OD-12 | CLEARED | v2.5 §3.4.2 | v2.5-revised (base-rate set conformance) |
| U-OD-13 | CLEARED | v2.1 §3.4.3 | `PerCellCardinalityBudget` in-unit; the M-2 carrier — unaffected |
| U-OD-14 | CLEARED | v2.5 §3.4.4 | v2.5-revised (cardinality attribute sets conformance); error-type tail inline per §0.8 |
| U-OD-15 | CLEARED | v2.1 §3.4.5 | `AttributeClassification` in-unit |
| U-OD-16 | CLEARED | v2.1 §3.4.6 | `ContentCapturePosture`/`PerPersonaTierRedactionPosture` in-unit |
| U-OD-17 | CLEARED | v2.1 §3.4.7 | Consumes `ContentCapturePosture` (U-OD-16, in-cone); error-type tail inline |
| U-OD-18 | CLEARED | v2.1 §3.5.1 | `PriceRateKey`/`SpanCostInputs` in-unit; `opaque Reference` declared |
| U-OD-28 | CLEARED | v2.1 §3.7.2 | `CollectorPlacement`/`PerCellPlacement` in-unit; U-OD-27 constant consumption edge present (clean) |
| U-OD-29 | CLEARED | v2.1 §3.7.3 | `SandboxTier`/`OtlpReachabilityClass` in-unit; consumes `CollectorPlacement` (U-OD-28, in-cone) |
| U-OD-32 | CLEARED | v2.5 §3.8.1 | v2.5-revised (bridging-arc transitions conformance); U-OD-13 transitively in-cone — no M-2 finding |
| U-OD-33 | CLEARED | **v2.5 §3.8.2** | **See §0.5 — the audit's M-2 row for U-OD-33 is dissolved by v2.5's `PreservationDimension` conformance (`CARDINALITY_BUDGET` dropped). NO M-2 edge added. Preserved verbatim from v2.5. Subject to Q-R5-1 operator confirmation.** |

**Preserved-verbatim count: 18 units** (U-OD-02/03/05/06/07/08/11/12/13/14/15/16/17/18/28/29/32/33). U-OD-01 is listed above for completeness but is **revised at §7** (declaration-site conversion) — it is not a no-delta unit.

---

## §4 Dependency-graph delta

### §4.1 Node delta

| Change | Detail |
|---|---|
| **New node** | **U-OD-00** — `Depends on: (none)`; L0 pre-cluster foundational anchor (alongside U-OD-01, U-OD-04). A pure source node. |
| Node count | v2.5: 34 nodes (U-OD-01…U-OD-34). **v2.6: 35 nodes** (U-OD-00 + U-OD-01…U-OD-34). |

### §4.2 Edge delta

| New edge | Pattern | Type carried | Acyclicity |
|---|---|---|---|
| U-OD-09 → U-OD-04 | M-1 | `SpanRef`, `EventEmission` | U-OD-04 L0 — inbound edge to source node; no cycle |
| U-OD-10 → U-OD-04 | M-1 | `SpanAttributes` | U-OD-04 L0; no cycle |
| U-OD-19 → U-OD-04 | M-1 | `SpanRef` | U-OD-04 L0; no cycle |
| U-OD-20 → U-OD-04 | M-1 | `SpanRef` | U-OD-04 L0; no cycle |
| U-OD-21 → U-OD-20 | **M-2** | `SpanCostRecord` | U-OD-20 L3, U-OD-21 L4 — higher→lower level; no cycle |
| U-OD-22 → U-CP-00 | **M-2** | `WorkloadClass` | U-CP-00 is a landed `harness-core` L0 resident; `(cross-axis: core)` import edge; no cycle |
| U-OD-25 → U-OD-04 | M-1 | `SpanRef`, `EventEmission` | U-OD-04 L0; no cycle |
| U-OD-26 → U-OD-04 | M-1 | `SpanAttributes` | U-OD-04 L0; no cycle |
| U-OD-30 → U-OD-04 | M-1 | `SpanRef` | U-OD-04 L0; no cycle |
| U-OD-30 → U-OD-00 | M-1 | `AuditPayload`, `AuditLedger`, `AuditSignatureAttributes` (per Q-R5-3) | U-OD-00 L0; no cycle |
| U-OD-31 → U-OD-04 | M-1 | `SpanAttributes` | U-OD-04 L0; no cycle |

**Edges added: 11.** Eight M-1 carrier edges to U-OD-04 (U-OD-09/10/19/20/25/26/30/31 — note U-OD-23 already had a `[U-OD-04]` edge in v2.1, so it is NOT in this list); one M-1 carrier edge to U-OD-00 (U-OD-30); two M-2 edges (U-OD-21→U-OD-20; U-OD-22→U-CP-00). *(Count: 8 U-OD-04 edges + 1 U-OD-00 edge + 2 M-2 edges = 11.)*

**No edge removed.** No M-2 edge for U-OD-33 (§0.5 — dissolved by v2.5).

### §4.3 Edges NOT added (with rationale)

| Non-edge | Rationale |
|---|---|
| U-OD-23 → U-OD-04 | Already declared in v2.1 §3.6.1 (`Depends on: [U-OD-04, +cross-axis]`). U-OD-23's M-1 fix is a `ChildSpanRef` carrier re-point only — no new edge. |
| U-OD-33 → U-OD-14 | **Dissolved by v2.5** — the `CARDINALITY_BUDGET` dimension that coupled U-OD-33 to U-OD-14's cardinality sets was dropped at v2.5 §3.8.2 `PreservationDimension` conformance. See §0.5; Q-R5-1. |
| U-OD-24 / U-OD-27 / U-OD-31 / U-OD-22 → carrier for `HusainLoopState`/`SpanRow`/`EvictionAction`/`DashboardQuery`/`CardinalityCounters`/`DashboardRef` | These six are single-consumer types declared in-unit per §1.0 Cluster-3 — no carrier unit, no carrier edge. |
| Any U-OD-NN → U-OD-00 except U-OD-30 | `AuditPayload`/`AuditLedger`/`AuditSignatureAttributes` are consumed only by U-OD-30. U-OD-00 has exactly one OD consumer. |
| Any new CXA OD→CP edge | The `WorkloadClass`@U-OD-22 resolution is a `harness-core` import (disposition 3 / T2), NOT a CXA OD→CP `Depends on` edge. The CXA §2.3 OD→CP edge count (12) is unchanged — load-bearing for M-3 (U-OD-34's CP count stays 12). |

### §4.4 Acyclicity + level decomposition (re-verified)

- **Acyclic invariant: holds.** All 11 new edges either point *into* an L0 source node (U-OD-00, U-OD-04, U-CP-00 — 9 of the 11 edges) or point from a higher topological level to a lower one (U-OD-21→U-OD-20: L4→L3). A source node accumulating inbound edges cannot create a cycle; a higher→lower edge respects the existing topological order. **Kahn sort still terminates.**
- **Level decomposition delta.** U-OD-00 joins **L0** (with U-OD-01, U-OD-04) — L0 grows from 2 to 3 units. No other unit changes level: every M-1 carrier edge targets an L0 node (does not raise the consumer's level); the U-OD-21→U-OD-20 edge does not raise U-OD-21 above L4 (U-OD-21 already depends on U-OD-18 at L1 and U-OD-20 sits at L3 < L4). The U-OD-22→U-CP-00 edge targets a `harness-core` L0 resident, not an OD-axis node — it does not affect OD-axis level decomposition. **Level depth unchanged: 10 (L0–L9).**
- **Within-axis directed edges.** v2.5: 100 within-axis OD edges. R5 adds 9 within-OD edges (8 to U-OD-04 + 1 to U-OD-00) + 1 within-OD M-2 edge (U-OD-21→U-OD-20) = **10 new within-axis edges → 110**. The U-OD-22→U-CP-00 edge is a `harness-core` import edge, counted separately (it is neither a within-OD-axis edge nor a CXA OD→CP edge — it is a shared-substrate import; 1 such edge).
- **Cross-axis directed edges.** **Unchanged at the v2.4 §4.5.1-canonical 26** (IS:4 / AS:10 / CP:12). R5 adds **zero** CXA edges — the `WorkloadClass` resolution is a core import, not a CXA edge. (M-3 conforms U-OD-34's *stated* count to this already-canonical 26.)

---

## §5 Coverage-matrix delta

Per `implementation-planner` SKILL.md §8.5 + §4.2 (multi-unit coverage of a contract is permitted; a revision pass *adds* marks, does not move them).

| Contract | v2.5 coverage | R5 delta |
|---|---|---|
| C-OD-14 §14.5 | U-OD-20 (F2-12 ACTIVE notation + idempotency join) | **+U-OD-00** — U-OD-00 covers the audit-ledger composition-type factor-out of §14.5; U-OD-20's existing coverage of §14.5 is **not moved**. Multi-unit coverage. |
| ADR-D5 v1.3 §1.4 / §1.4.1 | U-OD-30 (audit-signature attributes) | **+U-OD-00** — U-OD-00 covers the audit-ledger cryptographic-shape factor-out; per Q-R5-3 default `AuditSignatureAttributes` moves to U-OD-00. U-OD-30's coverage of C-OD-21 §21.1–§21.3 is unchanged. |
| C-OD-09 §9.1 | U-OD-11 (sampling mode) | **+U-OD-04** — R5 adds C-OD-09 §9.1 to U-OD-04's `Implements` for the OTel span/attribute handle substrate the `Span*` aliases name (§3.2.1). Additive; U-OD-11's coverage of C-OD-09 is not moved. |

**No contract loses a coverage mark.** Every M-1/M-2/M-3 unit's `Implements:` field is otherwise unchanged. The aggregate coverage remains: **23 of 23 OD contracts (C-OD-01…C-OD-23) covered by ≥1 unit** — U-OD-00 adds a factor-out mark on C-OD-14 §14.5 + ADR-D5 §1.4, both already covered. No coverage gap is introduced or closed.

> **Plan-level invariant delta (for `harness-od/CLAUDE.md` §3.1 — operator-applied).** OD plan unit count **34 → 35** (U-OD-00 added). Foundational anchors (L0) **2 → 3** (U-OD-00 added alongside U-OD-01, U-OD-04). Within-axis directed edges **100 → 110**. Cross-axis directed edges **unchanged at 26** (M-3 conforms the *stated* count; the edge graph itself was already 26 per v2.4 §4.5.1). The `harness-od/CLAUDE.md` §3.1 invariant table and the §1.1 plan/spec authority row cite "34 units" / "28 cross-axis edges" — both require an operator-applied update on ratification (a `CLAUDE.md` edit, routed through ratification per `CLAUDE.md` §9.1; see Q-R5-4).

---

## §6 Auxiliary-type audit (permanent section)

*This section is **new at R5** and is a permanent §6 of the OD plan from v2.6 onward. It closes the M-1 gap **structurally**, not unit-by-unit: the materializability audit found the OD plan "has no §5.4.1-style auxiliary-type audit at all" — the gap was never even nominally checked. This section is the audit. Every type at a typed signature position across all 35 OD units is enumerated with its carrier. A type with no carrier row is a defect.*

### §6.1 Carrier table — every OD auxiliary type at a signature position

| Type | Consumed at | Carrier | Carrier kind | Edge required |
|---|---|---|---|---|
| `SpanRef` | U-OD-09/19/20/30 (params), U-OD-23 (param) | **U-OD-04** | OTel-handle type-alias (T2 FACTOR-OUT) | `[U-OD-04]` |
| `ChildSpanRef` | U-OD-23 (return) | **U-OD-04** | OTel-handle type-alias | `[U-OD-04]` (U-OD-23 already has it) |
| `SpanAttributes` | U-OD-10/26/31 (params) | **U-OD-04** | OTel-handle type-alias | `[U-OD-04]` |
| `EventEmission` | U-OD-09/25 (returns) | **U-OD-04** | harness return-record (factor-out of C-OD-09/C-OD-25 emission contracts) | `[U-OD-04]` |
| `AuditPayload` | U-OD-30 (`sign_audit_entry` param) | **U-OD-00** | OD-local record (factor-out of C-OD-14 §14.5) | `[U-OD-00]` |
| `AuditLedger` | U-OD-30 (`verify_hash_chain_integrity` param) | **U-OD-00** | OD-local record | `[U-OD-00]` |
| `AuditLedgerEntry` | U-OD-00-internal (`AuditLedger.entries`) | **U-OD-00** | OD-local record | (within U-OD-00) |
| `AuditSignatureAttributes` | U-OD-00 (`AuditLedgerEntry`), U-OD-30 (`sign_audit_entry` return) | **U-OD-00** (moved from U-OD-30 per Q-R5-3) | OD-local record (4-attribute `audit.signature.*` set, ADR-D5 §1.4.1) | `[U-OD-00]` (U-OD-30→U-OD-00) |
| `StateLedgerEntryRef` | U-OD-00 (`AuditPayload.entry_core`) | **U-OD-00** | opaque marker; resolves to IS `StateLedgerEntry` at U-OD-30 cross-axis IS edge | (opaque) |
| `WorkloadClass` | U-OD-22 (`AlertingThresholdComposition`, `compute_alerting_signal`) | **U-CP-00** (`harness-core`, landed) | `harness-core` resident enum | `[U-CP-00 (cross-axis: core)]` |
| `DashboardRef` | U-OD-22 (`DashboardBackendConsolidation` fields) | **U-OD-22 (in-unit)** | single-consumer opaque marker (§1.0 Cluster-3) | none |
| `DashboardQuery` | U-OD-31 (`reject_cross_tenant_query` param) | **U-OD-31 (in-unit)** | single-consumer record (§1.0 Cluster-3) | none |
| `CardinalityCounters` | U-OD-31 (`assert_per_tenant_cardinality_isolation` param) | **U-OD-31 (in-unit)** | single-consumer record (§1.0 Cluster-3) | none |
| `SpanRow` | U-OD-27 (`query_ring_buffer_via_tui` return) | **U-OD-27 (in-unit)** | single-consumer record (§1.0 Cluster-3) | none |
| `EvictionAction` | U-OD-27 (`evict_oldest_per_ring_buffer_policy` return) | **U-OD-27 (in-unit)** | single-consumer record (§1.0 Cluster-3) | none |
| `HusainLoopState` | U-OD-24 (`run_husain_loop_at_cell` return) | **U-OD-24 (in-unit)** | single-consumer record (§1.0 Cluster-3) | none |
| `DeploymentSurface` | U-OD-01/11/16/+ (cross-cutting) | **`harness-core` U-CORE-01** (R1) | `harness-core` resident enum | `[U-CORE-01 (cross-axis: core)]` (U-OD-01 — see §7) |
| `PersonaTier` | U-OD-01/16/+ (cross-cutting) | **`harness-core` U-CORE-01** (R1) | `harness-core` resident enum | `[U-CORE-01 (cross-axis: core)]` (U-OD-01 — see §7) |
| `CellID` | U-OD-02/03/12/13/16/17/22/24/27/28/30/32 | **U-OD-01** | OD-axis record (clean — audit Findings-rejected #1) | `[U-OD-01]` (all declared) |
| `GenAiAttribute` | U-OD-09 (`HARNESS_BREAKER_ATTRIBUTES`) | **U-OD-04** | OD-axis record (clean — audit Findings-rejected #2) | transitively in-cone; `[U-OD-04]` now direct |
| `SandboxTier` | U-OD-29 | **AS axis** (cross-axis AS edge — clean) | AS-owned enum | declared cross-axis AS edge |
| `Reference` (opaque) | U-OD-18 (`PRICE_TABLE_REF`), U-OD-00/22 (`opaque` markers) | declared `opaque` in-unit | opaque marker | none |
| Error-type tail (≈24: `*Violation`/`*Error`/`*Breach`/`*Mismatch`/`*Pending`) | every unit with `Result<_, E>` | **inline at first-consuming unit** (§0.8 discipline) | thin `HarnessError` subclasses | none |

### §6.2 Audit result

**Every type at a typed signature position across the 35 OD units has a carrier row.** No undeclared-type defect remains. The M-1 systemic pattern is closed:

- 4 OTel-handle types → U-OD-04 carrier (T2 FACTOR-OUT, "at U-OD-04").
- 4 OD-local audit types → U-OD-00 carrier (new unit; T1 disposition-2 / Q4-verified OD-local).
- 6 single-consumer observability primitives → in-unit declarations (§1.0 Cluster-3).
- 2 cross-cutting enums → `harness-core` U-CORE-01 (R1).
- 1 CP routing enum (`WorkloadClass`) → `harness-core` U-CP-00 (landed, R1-cited).
- ≈24 error types → inline-materialization discipline (§0.8).
- The remaining types (`CellID`, `GenAiAttribute`, `SandboxTier`, `Reference`, the in-unit-declared structured types per the audit's per-unit table) already had carriers.

**0 genuine design extensions** (T2: 27 of 27 X-AL-3 candidates FACTOR-OUT; the OD-relevant subset — `SpanRef`/`ChildSpanRef`/`SpanAttributes`/`EventEmission` — all FACTOR-OUT). No OD-spec back-flow. No `CLAUDE.md` anti-leakage rule touched.

### §6.3 Maintenance discipline (forward)

From v2.6 onward, **every new or revised OD unit MUST add its signature-position types to §6.1** before the unit is considered materializable. A unit whose signature carries a type with no §6.1 carrier row is a Pattern-M-1 defect and does not clear. This section is the structural closure the materializability audit found absent.

---

## §7 U-OD-01 declaration-site conversion

Per `.harness/revision_R1_harness_core.md` §3.4 hand-off: **U-OD-01 currently re-declares `DeploymentSurface` and `PersonaTier`** in its own Signatures block (v2.1 §3.1.1 line 290, per the materializability audit per-unit table). The carrier map ("declared independently twice (AS+OD)") and R1 disposition-1 promote both enums to `harness-core` U-CORE-01. R5 converts U-OD-01 from a *declaring* site to a *consuming* site for both.

> **Note.** U-OD-01 is **landed** (Phase 7 7b operational-minimum set, per the `.harness` memory + the materializability audit retrospective). This §7 conversion is therefore both a plan-unit revision **and** a landed-source re-check action item — see §8.

---

### §3.1.1 U-OD-01 — Declare 9-cell observability matrix (R5 declaration-site conversion)

[v2.1-preserved unit. R5 delta: **declaration-site conversion** — the in-unit `DeploymentSurface` and `PersonaTier` enum declarations are **stripped**; both are imported from `harness-core` U-CORE-01 (R1); a `[U-CORE-01 (cross-axis: core)]` edge is added. `CellID` (which has fields `persona_tier : PersonaTier` and `deployment_surface : DeploymentSurface`) is **unaffected as a type** — it remains declared in-unit at U-OD-01; only the *enums it composes* move to `harness-core`. All other v2.1 surfaces — the 9-cell matrix, `CellStatus`, `CellBindingViolation` (inline per §0.8), `reject_excluded_cell`, the matrix constants, acc, tests, rollback boundary — preserved verbatim from v2.1 §3.1.1.]

**Implements:** [C-OD-01 §1.1, §1.2, §1.3] *(unchanged)*. **R5 note:** the `DeploymentSurface`/`PersonaTier` enum *concepts* trace to C-AS-09 §9.1 / §9.4 + ADR-D5 v1.3 §1.5 (the contracts U-CORE-01 cites); U-OD-01 *consumes* them — it does not re-commit them. U-OD-01's `Implements` is unchanged (the 9-cell matrix is the C-OD-01 surface; the cross-cutting enums are imported substrate).

**Depends on:** [**U-CORE-01 (cross-axis: core)**] — **R5: changed from `[]` to `[U-CORE-01 (cross-axis: core)]`.** v2.1 declared `Depends on: []` (L0 anchor — U-OD-01 declared everything in-unit). Post-conversion, U-OD-01 imports `DeploymentSurface`/`PersonaTier` from `harness-core` U-CORE-01, so it takes a `[U-CORE-01]` edge.

> **L0-status note.** U-OD-01 was an L0 anchor (in-degree 0) in v2.1. After the conversion it depends on U-CORE-01 — a `harness-core` resident at the `harness-core` plan's L0. Per the R1 §3 edge-form discipline, a `harness-core` import edge is annotated `(cross-axis: core)` and is **not** an outbound CXA edge. U-OD-01 is **no longer an OD-axis L0 anchor** in the strict in-degree-0 sense — but `harness-core` is the topological root *upstream of all four axes* (R1 §1.3), so U-OD-01 remains the OD-axis's effective entry-point: its only dependency is the shared substrate, which is built before any axis. The OD plan's L0 set (for OD-axis-internal topological purposes) is **U-OD-00, U-OD-01, U-OD-04** — all three depend only on `harness-core` residents or nothing. *(harness-od/CLAUDE.md §3 names U-OD-01 + U-OD-04 as the L0 anchors; this is an operator-applied update item — see Q-R5-4.)*

**Signatures (R5 — `DeploymentSurface`/`PersonaTier` declarations stripped; imported from U-CORE-01):**

```
# --- R5: DeploymentSurface and PersonaTier are NO LONGER declared here. ---
# v2.1 declared `enum DeploymentSurface { ... }` and `enum PersonaTier { ... }`
# in this block. Both are STRIPPED — they are imported from harness-core
# U-CORE-01 (R1). The import is via the [U-CORE-01 (cross-axis: core)] edge.
#
#   from harness_core import DeploymentSurface, PersonaTier
#
# The enum value sets (LOCAL_DEVELOPMENT/SELF_HOSTED_SERVER/MANAGED_CLOUD;
# SOLO_DEVELOPER/TEAM_BINDING/MULTI_TENANT_COMPLIANCE) are U-CORE-01's
# acceptance criteria — U-OD-01 no longer re-states them.

# CellID is RETAINED in-unit — it is an OD-axis type. Its fields compose the
# imported harness-core enums:
record CellID {
  persona_tier        : PersonaTier         // imported from harness-core U-CORE-01
  deployment_surface  : DeploymentSurface   // imported from harness-core U-CORE-01
}

[Remainder of the v2.1 signature block preserved verbatim — CellStatus, the
 9-cell matrix constant, reject_excluded_cell, etc.]
```

**Acceptance criteria (R5 — declaration-site-conversion criteria added; v2.1 criteria preserved verbatim except where they asserted in-unit `DeploymentSurface`/`PersonaTier` declaration):**

[The v2.1 §3.1.1 acceptance criteria are preserved verbatim **except**: any v2.1 criterion asserting that U-OD-01 *declares* `DeploymentSurface`/`PersonaTier` (e.g. "the persona-tier / deployment-surface enums are declared in-unit at cardinality 3") is **struck** — that property now belongs to U-CORE-01's acceptance criteria. The 9-cell matrix criteria, `CellStatus` criteria, `reject_excluded_cell` criteria, and the `EXCLUDED` cell criteria are all preserved verbatim.]

**R5 additions:**

- **(Conversion.)** U-OD-01 does NOT declare `DeploymentSurface` or `PersonaTier`; both are imported from `harness-core` U-CORE-01 via the `[U-CORE-01 (cross-axis: core)]` edge. `CellID`'s `persona_tier` and `deployment_surface` fields resolve to the imported `harness-core` enums.
- **(Carrier.)** The `[U-CORE-01 (cross-axis: core)]` edge is declared; it is a `harness-core` import edge, not an outbound CXA edge (it does not affect the OD→IS/AS/CP cross-axis edge count — M-3-relevant: U-OD-34's count stays 26).
- `CellBindingViolation` is inline-materialized per the §0.8 error-type discipline.

**Tests (R5 — `DeploymentSurface`/`PersonaTier` declaration tests removed; conversion tests added):**

[v2.1 §3.1.1 tests preserved verbatim **except** any `test_deployment_surface_*` / `test_persona_tier_*` tests asserting *in-unit declaration* — those move to U-CORE-01's test list. The 9-cell matrix tests, `CellID` composition tests, `reject_excluded_cell` tests, and `EXCLUDED`-cell tests are preserved verbatim.] **R5 additions:** `test_deployment_surface_imported_from_harness_core`, `test_persona_tier_imported_from_harness_core`, `test_cell_id_fields_resolve_to_harness_core_enums`, `test_depends_on_u_core_01_core_edge_declared`, `test_no_local_deployment_surface_or_persona_tier_declaration`.

**Rollback boundary:** [v2.1 §3.1.1 rollback boundary preserved verbatim.] **R5 conversion revert appendix:** Reverting the R5 conversion restores the in-unit `DeploymentSurface`/`PersonaTier` declarations and removes the `[U-CORE-01]` edge — i.e., a regression to the independent-double-declaration defect the carrier map identified (`DeploymentSurface` "declared independently twice (AS+OD)"). The revert MUST NOT be performed absent a re-disposition of the R1 `harness-core` carrier-map ratification.

---

## §8 U-OD-04 retrospective + landed-source re-check action items

The materializability audit's retrospective section + R1 §4 flag landed OD units that consume now-re-pointed types. R5 carries these as **R5-application action items** — source-vs-plan reconciliation the operator authorizes at ratification (HARD WALL: R5 itself does not touch source).

### §8.1 U-OD-04 — the load-bearing retrospective (dual-flagged)

U-OD-04 is **landed** (Phase 7 7b operational-minimum set). R5 grows U-OD-04 to declare the `SpanRef`/`ChildSpanRef`/`SpanAttributes`/`EventEmission` carrier family (§3.2.1). The materializability audit's retrospective section explicitly flagged U-OD-04 as "the candidate M-1 alias-carrier and a landed unit — both retrospectives converge on 'U-OD-04's landed materialization must be re-checked before/at the revision-pass.'"

**U-OD-04 is dual-flagged:**

1. **Verbatim retrospective (carried from v2.5 / Tension 004).** U-OD-04 was the subject of Tension 004 (span name format / `GenAiOperation` / `AttributeTier` / `BASE_METRIC_NAME` verbatim divergence), absorbed at v2.5 §3.2.1. If U-OD-04 landed against the *v2.1* body, it landed against the verbatim-divergent state — the landed source must be re-checked against the v2.5-conformed values (3-component span name; 7 operations; 3 tiers; `gen_ai.client.operation.duration`). This retrospective is owned by the v2.5 verbatim pass; R5 records it for completeness.
2. **Materializability retrospective (R5).** R5's §3.2.1 carrier-growth adds the `Span*` alias family to U-OD-04. **The landed U-OD-04 source must be revised** to declare `SpanRef`/`ChildSpanRef`/`SpanAttributes`/`EventEmission` — the landed unit predates the carrier-growth. This is an R5-application action item.

**Action item A-R5-1 (U-OD-04 landed-source re-check).** Before the v2.6 plan lands, the operator authorizes a re-check of the landed U-OD-04 source: (a) verify the landed source carries the v2.5-conformed verbatim values (retrospective 1); (b) revise the landed source to declare the R5 `Span*` alias family (retrospective 2). Both must be reconciled in the same source pass. The materializability audit logged this as a §2.7.6 **Class 3 (informational)** retrospective; R5 carries it as an action item, not a blocker.

### §8.2 U-OD-01 — landed-source re-check (declaration-site conversion)

**Action item A-R5-2 (U-OD-01 landed-source re-check).** U-OD-01 is landed (§7 note). The §7 declaration-site conversion strips the in-unit `DeploymentSurface`/`PersonaTier` declarations and imports from `harness-core` U-CORE-01. The landed U-OD-01 source must be re-pointed: delete the local enum declarations; import from `harness-core`; verify `CellID`'s field types resolve to the imported enums. Per R1 §4's discipline flag — a landed unit that declared a type *before* its `harness-core` carrier existed must be inspected at the source level (it may have inlined a local declaration). R5 default: re-point at the R5-application source pass; record the re-point in the v2.6 application change-note. **Prerequisite:** R1's U-CORE-01 must be landed first (R1 is the R-series prerequisite per R1 §0.1).

### §8.3 Other landed OD units — re-check sweep

The materializability audit notes the 7b operational-minimum set as "12/12 units landed." Any landed OD unit among the 14 FORK units (or U-OD-01) consumed a now-re-pointed type before its carrier existed. **Action item A-R5-3:** at the R5-application source pass, sweep the landed OD units; for each landed FORK unit, verify the landed source either (a) used a bare `Any`/placeholder for the undeclared type (re-point to the carrier), or (b) inlined a local declaration (delete; import the carrier). Record each re-point in the v2.6 application change-note. R5 (HARD WALL) does not perform the sweep — it flags it.

---

## §9 Operator questions

| ID | Question | R5 default |
|---|---|---|
| **Q-R5-1** | The materializability audit's Pattern M-2 names a U-OD-33→U-OD-14 hidden-coupling edge, grounded in v2.1's `PreservationDimension` enum carrying a `CARDINALITY_BUDGET` dimension computed over U-OD-14's cardinality sets. **v2.5 §3.8.2 conformed `PreservationDimension` to the §22.2 5-dimension table and DROPPED `CARDINALITY_BUDGET`** — the coupling no longer exists in the v2.5 U-OD-33 body (§0.5). Confirm: the U-OD-33→U-OD-14 M-2 edge is **dissolved by v2.5 and NOT added by R5**; M-2 scope is 2 edges, not 3. | **Dissolved — not added.** R5 surfaces this rather than silently absorbing a stale finding. Operator confirms the audit/v2.5 reconciliation. |
| **Q-R5-2** | The T1 carrier map flagged "1–2 new OD carrier units." R5 resolves this to **exactly 1** (U-OD-00, for `AuditPayload`/`AuditLedger`), with the `Span*` family declared at the existing U-OD-04 (T2 verdict) and the 6 single-consumer primitives declared in-unit (§1.0). Confirm the single-carrier-unit reading, or instead split off a U-OD-00b for the Cluster-3 primitives? | **One new unit (U-OD-00).** Single-consumer types declared in-unit per the over-decomposition discipline (`implementation-planner` SKILL.md §10). |
| **Q-R5-3** | `AuditSignatureAttributes` (the 4-attribute `audit.signature.*` record) is declared at U-OD-30 (v2.5) but referenced by U-OD-00's `AuditLedgerEntry`. To give the OD audit-ledger types a single carrier, R5 default **moves `AuditSignatureAttributes` into U-OD-00** (U-OD-30 then consumes it via `[U-OD-00]`). Alternative: keep it at U-OD-30 and give U-OD-00 a `[U-OD-30]` edge — but that makes U-OD-00 non-L0 and inverts the natural carrier→consumer direction. Confirm the move. | **Move `AuditSignatureAttributes` to U-OD-00.** Keeps U-OD-00 the single audit-type carrier and an L0 source node. |
| **Q-R5-4** | R5 changes OD plan-level invariants: unit count 34→35; L0 anchors 2→3; within-axis edges 100→110. `harness-od/CLAUDE.md` §3.1 invariant table + §1.1 authority row cite "34 units" / "28 cross-axis edges" / "L0 = U-OD-01, U-OD-04". These require an operator-applied `CLAUDE.md` edit on ratification (routed per `CLAUDE.md` §9.1). Authorize the `harness-od/CLAUDE.md` update? | Authorize — the `CLAUDE.md` figures must agree with the v2.6 plan. R5 cannot edit `CLAUDE.md` (HARD WALL); flagged for operator action. |
| **Q-R5-5** | U-OD-01 ceases to be a strict in-degree-0 L0 anchor after the §7 conversion (it gains `[U-CORE-01]`). R5 treats `harness-core` as the topological root upstream of all axes, so U-OD-01 remains the OD-axis effective entry-point. Confirm the OD-axis-internal L0 set is `{U-OD-00, U-OD-01, U-OD-04}` (all depend only on `harness-core` residents or nothing). | Confirm — consistent with the R1 `harness-core`-as-root framing. |
| **Q-R5-6** | The T2 resolution table cites "OD spec C-OD-09" in the `SpanRef`/`SpanAttributes` FACTOR-OUT rows. But the OD plan unit assignment shows **C-OD-09 is U-OD-11's sampling-mode contract**, not the OTel span substrate. R5 does NOT cite C-OD-09 §9.1 on U-OD-04's `Implements` line; it traces the `Span*` family to ADR-F5 + ADR-D6 v1.2 + the `Target_Stack_Commitment` OTel adoption. Confirm the corrected trace target. | **Trace to ADR-F5 + ADR-D6, not C-OD-09.** R5 surfaces the T2-row mismatch rather than silently re-routing a cited section; the FACTOR-OUT verdict is unaffected. |

All six are **proposing** or **decided-pending-confirmation** — none is genuinely **open** (no operator input is needed even to classify; each has an authority-chain-supported R5 default). **Q-R5-1 is the load-bearing one** — it changes the M-2 fix scope from 3 edges to 2 (it prevents silent absorption of a stale audit finding against a v2.5-deleted dimension); the operator must rule on the audit/v2.5 reconciliation before v2.6 lands.

---

## §10 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/revision_R5_od_plan.md` |
| Role | `implementation-planner`, revision-pass sub-mode (SKILL.md §8) |
| Revision pass | R5 — OD plan materializability conformance; the LAST of the R1–R5 carrier-map absorption sequence |
| Authored | 2026-05-15, Phase 7 sub-phase 7b |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_5.md` (v2.5 — verbatim-divergence cluster) |
| Successor | On ratification: `Implementation_Plan_Operational_Discipline_v2_6.md` carries the U-OD-00 body + the 14 FORK / 1 CONFORM revisions + the new §6 auxiliary-type audit + the §7 U-OD-01 conversion; the §8 action items A-R5-1/2/3 are the R5-application source-reconciliation worklist |
| Inputs | `materializability_audit_od_plan.md` (Q3); `shared_type_carrier_map.md` (T1); `xal3_resolution_recommendations.md` (T2); `revision_R1_harness_core.md` §3.4; `Implementation_Plan_Harness_Core_v1_0.md` (U-CORE-01); `Implementation_Plan_Operational_Discipline_v2_5.md` → v2_4 → v2_1; `Spec_Operational_Discipline_v1_3.md` (delta over v1_2); `harness-od/CLAUDE.md`; workspace `CLAUDE.md` |
| Status | `Proposed` — pending operator ratification of §9 Q-R5-1…Q-R5-5 + the M-1/M-2/M-3 direction. Per SKILL.md §8, `Status: Proposed` is preserved until P6-CK / Phase-7 pre-implementation re-clearance. |
| Coverage / dependency-graph re-verification | §4 (acyclic; 11 edges added; node count 34→35; level depth unchanged at 10); §5 (coverage additive; 23/23 OD contracts still covered; no gap) |
| HARD WALL attested | This pass wrote **only** `.harness/revision_R5_od_plan.md`. No `design-substrate/` file, no `CLAUDE.md`, no plan, spec, audit, carrier-map, or source code edited. No git commit. |

*End of Revision R5 — Operational Discipline Plan Materializability Conformance. The operator ratifies. R5 is the last of the R1–R5 carrier-map absorption sequence; on ratification the OD plan v2.6 closes the M-1 / M-2 / M-3 materializability cluster and the OD axis is materializable pyright-strict-clean at every topological position.*
