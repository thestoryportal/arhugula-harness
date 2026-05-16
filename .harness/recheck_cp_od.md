# Review-Ahead Re-Check (RC-B) — CP v2.6 + OD v2.6 Materializability Conformance

*Pipeline pass RC-B. Pre-implementation re-clearance of the `Proposed`-status
conformed plans. Verifies the R4 (CP) + R5 (OD) revision passes closed every
materializability fork their audits found, and introduced no new defect.
Read-only — `.harness/recheck_cp_od.md` is the only file written.*

- Mode: Phase-7 pre-implementation review (`harness-adversarial-reviewer`)
- Date: 2026-05-15
- Scope: `Implementation_Plan_Control_Plane_v2_6.md` vs `materializability_audit_cp_plan.md` + `revision_R4_cp_plan.md`;
  `Implementation_Plan_Operational_Discipline_v2_6.md` vs `materializability_audit_od_plan.md` + `revision_R5_od_plan.md`

---

## CP plan — v2.6 re-check

**Verdict: CLEARED.**

Re-check of `Implementation_Plan_Control_Plane_v2_6.md` (57 units incl. new
U-CP-00b) against `materializability_audit_cp_plan.md` (24 FORK / 12 CONFORM /
20 CLEARED; Patterns C / D / E) and `revision_R4_cp_plan.md`.

### Forks closed — confirmed

- **Pattern C (`AttributeValueType`/`Cardinality` no-carrier, 7 units) — closed.**
  v2.6 §2.0b declares new foundational unit **U-CP-00b** (L0, `Depends on: (none)`)
  carrying both enums; the inline declarations are stripped from U-CP-01; the
  7 sideways consumers (U-CP-07/11/21/31/37/46/47) plus U-CP-01 each gain a
  `[U-CP-00b]` edge. §0.10 ledger confirms 8 edge-adds.
- **Pattern D (≥25 undeclared types, ≥20 units, ≥5 hidden-coupling edges) — closed.**
  Every undeclared type re-pointed to a ratified carrier: identity aliases +
  `WorkflowEventClass` → `harness-core` U-CORE-01 (~14 `[U-CORE-01]` edges);
  CP-owned structured types → U-CP-00b (~15 `[U-CP-00b]` edges); `MCPServerID`/
  `ToolName` → AS cross-axis edges; 9 inline-comment enums promoted to real
  `enum` declarations; 7 hidden-coupling edges added. §11 is a new permanent
  auxiliary-type registry — every type at a CP signature position has a carrier
  row. T2 verdict honored: 0 design extensions, 0 design-substrate revisions.
- **Pattern E (~10 deferred `[U-CP-00]` `WorkloadClass` edges) — materialized
  in-body.** §0.12 ledger confirms the edges are written into U-CP-05/06/09/13/
  17/21/23/25/29/53 `Depends on` lines, not carried as deferred pointers. v2.6
  §0.7 explicitly corrects the v2.5 §0.8 "deferred, not a fork" mis-disposition.
  This is exactly the Pattern-E in-body materialization the re-check mandate
  required.
- **U-CP-10 reconciliation — resolved correctly.** The duplicate
  `LifecycleEventClass` (U-CP-10) / `WorkflowEventClass` (U-CORE-01) is resolved
  to the single `harness-core` `WorkflowEventClass` (operator decision D9):
  U-CP-10's local enum is stripped, `LifecycleEventClassMetadata.class` re-typed
  to `WorkflowEventClass`, `[U-CORE-01]` edge added, former acc #1 struck
  (now covered at U-CORE-01). `ParentRelation` is promoted to a real `enum`
  with the operator-ratified value set `{ROOT, CHILD_OF, DELEGATED_TO}`
  (D5), cardinality 3, with tests. Both required reconciliations confirmed.

### Carrier reachability — confirmed

Every carrier edge points at a declared carrier. U-CP-00b and U-CP-00 are
self-consistent L0 units (`Depends on: (none)`, pure source nodes). U-CORE-01
is the `harness-core` root upstream of all axes. The U-CP-03↔U-CP-05 level
inversion the audit named is dissolved at its root: `RoutingDecisionTrace`
re-homed to U-CP-00b so both consumers take an L0→L0 edge — no forward edge,
no inversion.

### No new defect — confirmed

- No new undeclared type: §11.1 registry is exhaustive; §11.2 makes a
  signature-position type absent from the registry a defect by construction.
- No dependency cycle: §9.3 — U-CP-00b / U-CP-00 / U-CORE-01 are pure source
  nodes (inbound-only edges); no unit changes level; 9-level structure (L0–L8)
  preserved; Kahn sort terminates.
- No signature-vs-spec gap: every revised unit's `Implements:` preserved;
  U-CP-00b traced to the aggregate of 7 attribute-schema contracts
  (aggregate-citation form operator-ratified at D3); U-CP-10's `Implements:
  [C-CP-05 §5.1]` preserved with documented multi-unit coverage.

### Residual issues

None blocking. Operator-tracked follow-ups, none a Class 1 halt:

- **§4.1 Class 1 / §2.7.6 Class 3 (informational):** deferred coding-lane
  action items D-1 (U-CP-15 `CapabilityFloor` re-check — thin §7.4 basis,
  operator-accepted as faithful factor-out, non-blocking), D-2 (U-CP-10
  landed-source re-point at v2.6 application), D-3 (U-CP-12/U-CP-20 mechanical
  token re-anchor at transcription). All flagged in §0.13, none gates clearance.
- **§4.1 Class 1 / §2.7.6 Class 3 (informational), carried not introduced:**
  U-CP-23 `default_pattern` single-vs-dual structural mismatch and U-CP-43
  `MCP_TRUST`/`DEPLOYMENT_SURFACE` floor spec-silence — both are verbatim-axis
  items pre-dating R4, explicitly carried at §0.8 as separately-tracked, not
  R4-introduced and outside materializability scope.
- The §2.4 ellipsis-bearing inline enums (`OutputSchemaKind`, `OverrideKind`,
  etc.) need a value-set completion check against each declaring unit's spec
  section at v2.6 transcription — correctly flagged as a transcription-time
  check (R4 cannot invent elided values; not a silent absorption).

## OD plan — v2.6 re-check

**Verdict: CLEARED.**

Re-check of `Implementation_Plan_Operational_Discipline_v2_6.md` against
`materializability_audit_od_plan.md` (14 FORK / 1 CONFORM / 19 CLEARED;
Patterns M-1 / M-2 / M-3) and `revision_R5_od_plan.md`.

### Forks closed — confirmed

- **M-1 (≥11 undeclared auxiliary types, no carrier) — closed.** v2.6 §6.1
  is a new permanent carrier table; every type at a signature position across
  all 35 units has a carrier row. The fix is structural, not unit-by-unit:
  - 4 OTel-handle types (`SpanRef`/`ChildSpanRef`/`SpanAttributes`/`EventEmission`)
    → U-OD-04 carrier-growth (additive: new signature sub-block + acc #9 + tests;
    v2.5 verbatim surfaces untouched). T2 FACTOR-OUT verdict honored.
  - 4 OD-local audit types (`AuditPayload`/`AuditLedgerEntry`/`AuditLedger`/
    `AuditSignatureAttributes`) → new carrier unit **U-OD-00** (L0, `Depends on: []`).
  - 6 single-consumer primitives (`DashboardRef`/`DashboardQuery`/`SpanRow`/
    `EvictionAction`/`HusainLoopState`/`CardinalityCounters`) → declared in-unit
    at their sole consumer (over-decomposition discipline; carrier criterion
    ≥2 consumers not met).
  - `WorkloadClass` → `harness-core` U-CP-00 import (`[U-CP-00]` edge), not a CXA edge.
  - ≈24 error types → §0.8 inline-materialization discipline note.
  - U-OD-01 `DeploymentSurface`/`PersonaTier` → declaration-site conversion to
    `harness-core` U-CORE-01 import.
- **M-2 (hidden coupling) — closed, correctly scoped to 2 edges.** The audit
  named 3 M-2 edges; R5/v2.6 correctly identified the U-OD-33→U-OD-14 edge as
  *stale-from-v2.1* — v2.5 §3.8.2 dropped the `CARDINALITY_BUDGET`
  `PreservationDimension` that created the coupling. v2.6 surfaced this as
  Q-R5-1 rather than silently absorbing a stale finding (correct §4.3 discipline)
  and applied exactly 2 edges: U-OD-21→U-OD-20, U-OD-22→U-CP-00. This is the
  expected behaviour the re-check mandate flagged ("exactly 2, not 3").
- **M-3 (U-OD-34 stale edge count) — closed.** `cross_axis_edge_count` 28→26;
  `cross_axis_edge_breakdown` `{IS:6,…}`→`{IS:4,10,12}`; acc #3/#4 and the two
  tests conformed. U-OD-34 cross-axis edge count is **26** as required.

### Carrier reachability — confirmed

Every added carrier edge (11 total: 8×`[U-OD-04]`, 1×`[U-OD-00]`, 2 M-2)
points at a declared carrier. U-OD-00 is a self-consistent L0 unit
(`Depends on: []`, declares OD-local records only, no within-axis import).
U-OD-04 carrier-growth is additive. U-OD-23 correctly noted as already
carrying a `[U-OD-04]` edge in v2.1 — no double-count.

### No new defect — confirmed

- No new undeclared type: §6.1 carrier table is exhaustive over 35 units.
- No dependency cycle: §4.6.4 re-verifies — 9 of 11 new edges point into L0
  source nodes; the U-OD-21→U-OD-20 edge is L4→L3 (respects topo order). Kahn
  sort terminates; level depth unchanged at 10.
- No signature-vs-spec gap: every FORK/CONFORM unit's `Implements:` is
  unchanged; U-OD-00's new types are traced FACTOR-OUTs (C-OD-14 §14.5 +
  ADR-D5 v1.3 §1.4/§1.4.1), not spec extensions. 0 genuine design extensions
  (T2). The Q-R5-6 correction (trace `Span*` to ADR-F5/ADR-D6, not the
  mis-cited C-OD-09) was applied — a clean catch, not a defect.

### Residual issues

None blocking. Three follow-up items, all operator-tracked, none a Class 1 halt:

- **§4.1 Class 1 / §2.7.6 Class 3 (informational):** `harness-od/CLAUDE.md`
  §3.1/§1.1 invariant figures ("34 units", "28 cross-axis edges", L0 set) lag
  v2.6 — operator-applied `CLAUDE.md` edit owed per Q-R5-4 (§0.9 flags it).
- **§2.7.6 Class 3 (informational):** landed-source re-checks A-R5-1
  (U-OD-04), A-R5-2 (U-OD-01), A-R5-3 (landed FORK-unit sweep) — source
  reconciliation owed at the R5-application source pass; non-blocking for
  plan re-clearance.
- U-OD-04 / U-OD-01 are landed units the conversion touches; re-check is an
  application-time action, already enumerated in §8 of the revision.

## Re-clearance verdict

| Plan | Verdict | Basis |
|---|---|---|
| **CP — `Implementation_Plan_Control_Plane_v2_6.md`** | **CLEARED-for-coding** | All 24 FORK + 12 CONFORM units resolved via Patterns C/D/E carrier+edge work; new U-CP-00b L0 carrier; U-CP-10/`WorkflowEventClass` reconciliation correct; Pattern E edges materialized in-body; 7 operator questions ratified (D3–D9); §11 permanent auxiliary-type registry closes the structural blind spot; DAG acyclic; no new defect. |
| **OD — `Implementation_Plan_Operational_Discipline_v2_6.md`** | **CLEARED-for-coding** | All 14 FORK + 1 CONFORM units resolved; M-1 closed via U-OD-00 carrier + U-OD-04 carrier-growth + in-unit single-consumer declarations + `harness-core` imports; M-2 correctly scoped to 2 edges (the stale U-OD-33→U-OD-14 row dissolved, surfaced not absorbed); M-3 (U-OD-34) conformed to 26; 6 operator questions ratified; §6 permanent auxiliary-type audit; DAG acyclic; no new defect. |

**Both plans are CLEARED for the coding lane to resume.** RC-B is a clean
re-check — the expected outcome of a sound conformance pass. The R4 (CP) and
R5 (OD) revision passes closed every materializability fork their audits found
and introduced no new undeclared type, dependency cycle, or signature-vs-spec
gap. Two findings deserve explicit credit as evidence of conformance-pass
soundness rather than defects:

1. **OD R5/v2.6 caught a stale audit finding.** The materializability audit
   named 3 M-2 hidden-coupling edges; one (U-OD-33→U-OD-14) was grounded in a
   `PreservationDimension` the *intervening* v2.5 conformance had already
   deleted. R5 surfaced this as Q-R5-1 and applied exactly 2 edges rather than
   silently absorbing a stale finding — correct `CLAUDE.md` §4.3 anti-silent-
   absorption discipline.

2. **CP R4/v2.6 corrected an upstream mis-disposition.** v2.5 §0.8 had labelled
   the Pattern-E deferred edges "not a fork"; R4 §0.7 corrects this and
   materializes the edges in-body. The aggregate-citation form for the new
   carrier unit U-CP-00b, and the T2 mis-citation of C-OD-09 in the OD pass,
   were both surfaced as operator questions rather than silently re-routed.

### Residual items (all non-blocking, operator-tracked)

These are §4.1 Class 1 / §2.7.6 Class 3 (informational) — none halts coding:

- CP: deferred coding-lane re-checks D-1/D-2/D-3 (U-CP-15 `CapabilityFloor`,
  U-CP-10 landed-source re-point, U-CP-12/U-CP-20 token re-anchor); carried
  verbatim-axis items U-CP-23 `default_pattern` and U-CP-43 floor spec-silence;
  ellipsis-enum value-set completion at transcription.
- OD: `harness-od/CLAUDE.md` invariant figures lag v2.6 (operator-applied edit
  owed per Q-R5-4); landed-source re-checks A-R5-1/A-R5-2/A-R5-3.
- Both: the per-axis + root `CLAUDE.md` §2.4 plan-version pointers lag the
  R-series (a known carried cleanup bucket per `review-pipeline.md`).

None of these is a precondition for materializing a unit; they are
application-time / source-reconciliation actions already enumerated in the
revision artifacts. The RC pass clears.

---

*RC-B re-check, review-ahead pipeline. Phase-7 pre-implementation re-clearance
of the `Proposed`-status conformed plans. Read-only — only `.harness/recheck_cp_od.md`
written; no `design-substrate/` file, `CLAUDE.md`, plan, spec, audit, or source
modified (HARD WALL / X-AL-3). Findings classified, not absorbed. 2026-05-15.*
