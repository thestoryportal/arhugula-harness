# Revision R2 — Information-Substrate Plan: Materializability Conformance (IS plan v2.2 → v2.3 proposal)

**Status:** ✅ ABSORBED-INTO-CANONICAL-PLAN (status-line refreshed 2026-05-28 Phase 1 status-cascade sweep per workflow v1.12 §7.4.7.3.B) — R2 ratified + applied at `design-substrate/Implementation_Plan_Information_Substrate_v2_3.md` (canonical per workspace `CLAUDE.md` §2.4 IS row); revision proposal superseded by canonical plan. Species 3 stale-carry per workflow v1.12 §7.4.7.2.

**Status:** Proposed *(historical; predates 2026-05-15 ratification)*
**Revision pass:** R2 — IS-axis materializability conformance (second of the 5-pass carrier-map absorption sequence R1–R5; R1 = `harness-core` foundation, landed as `Implementation_Plan_Harness_Core_v1_0.md`).
**Authored:** 2026-05-15 by the `implementation-planner` role in revision-pass sub-mode (`implementation-planner` SKILL.md §8).
**Mode:** Revision-pass. This is a **revision proposal artifact**, not an applied plan edit. The operator ratifies before any `design-substrate/` plan is amended.

**HARD WALL.** This pass writes only `.harness/revision_R2_is_plan.md`. No `design-substrate/` file, no `CLAUDE.md`, no plan/spec/audit/carrier-map, no source code is edited. No git commit. On ratification, the operator emits `Implementation_Plan_Information_Substrate_v2_3.md` carrying the §5 revised unit bodies; the §4 source re-point is a separate R2-application action.

---

## §0 Change-note

### §0.1 Trigger

Three ratified / standing upstream inputs:

- `.harness/materializability_audit_is_plan.md` (Q4 IS materializability audit) — the IS-axis systemic materializability audit. Verdict tally: **11 CLEARED · 1 CONFORM (U-IS-17) · 5 FORK (U-IS-02, U-IS-05, U-IS-06, U-IS-12, U-IS-14)**. Systemic pattern **M-1-IS**: cross-axis types consumed at IS signature positions with no carrier.
- `.harness/shared_type_carrier_map.md` (Pipeline Pass T1) — the ratified carrier map. Disposition-1 places `WorkloadClass` (= IS `WorkflowClass`) at the landed `harness-core` U-CP-00 carrier; `DeploymentSurface` and the identity-alias module at the new `harness-core` U-CORE-01 carrier.
- `.harness/xal3_resolution_recommendations.md` (Pipeline Pass T2) — the X-AL-3 verdicts. **All M-1-IS types are FACTOR-OUT, decided** (`WorkflowEvent` / `WorkflowClass` / `DeploymentSurface`): the IS spec commits each concept in prose; declaring a `harness-core` carrier is faithful operationalization, **not** a design extension. **The two Class-1 halts the IS audit flagged are lifted** — IS importing `harness-core` is a shared-substrate import, not an outbound CXA edge, so the CXA §2.4 "IS = 0 outbound edges" invariant is untouched. **Zero IS-spec back-flow is required by R2.**
- `.harness/revision_R1_harness_core.md` §3.1 + §4 — the R1 hand-off: which IS units take a `[U-CORE-01 (cross-axis: core)]` and/or `[U-CP-00]` edge, and the U-IS-02 retrospective re-check flag. R1's U-CORE-01 body (now `Implementation_Plan_Harness_Core_v1_0.md` §2) declares `DeploymentSurface`, `PersonaTier`, the 9-alias identity module (incl. `ContractID`, `UnitId`), and `WorkflowEvent`/`WorkflowEventClass`.

R2 absorbs the IS materializability audit + the carrier map into the IS plan. R1 (the `harness-core` carrier) is the prerequisite and is already landed; R2 cites the U-CORE-01 / U-CP-00 carriers.

### §0.2 Scope of R2 (IS plan v2.2 → v2.3)

The IS plan v2.2 is a change-note-only delta; all 17 unit bodies carry forward verbatim from v2.1 (v2.2 §0.2). R2 therefore operates against the **v2.1 unit bodies** (the canonical bodies v2.2 preserves by reference) and proposes v2.3.

| In scope | Out of scope |
|---|---|
| Revised bodies for the 5 FORK units + 1 CONFORM unit: **U-IS-02, U-IS-05, U-IS-06, U-IS-12, U-IS-14, U-IS-17** (§5) | Editing any `design-substrate/` plan (operator emits v2.3 post-ratification) |
| `[U-CORE-01 (cross-axis: core)]` / `[U-CP-00]` dependency edges per the R1 §3.1 hand-off (§1, §6.2) | The 11 CLEARED units — preserved verbatim (§0.4) |
| `WorkflowClass` → `WorkloadClass` IS-internal spelling unification (§3) | U-CORE-01 itself — R1 scope, landed |
| U-IS-02 landed-source re-point action item (§4) | Source-code edits (HARD WALL — §4 is a hand-off to the R2-application step) |
| Coverage-matrix + dependency-graph delta (§6) | The U-IS-06 git-trio classification — surfaced as **open question Q-R2-1** (§7), not conformed |

### §0.3 Authority-chain note — the X-AL-3 risk was discharged upstream

The IS audit's M-1-IS finding listed reading (b) "X-AL-3 design extension → IS-spec back-flow" as a live possibility. **T2 closed that reading.** The IS spec §1 commits the concepts directly in prose (verified at this pass): line 134 — "a path identifier is **workflow-canonical** if it is stable across all runs of the same workflow class"; line 135 — "MAY vary across workflow classes"; line 136 — "MAY vary across deployment surfaces … canonical-path declaration commits only that *some* stable path exists per (workflow class, deployment surface) cell". The IS spec C-IS-04 §4 is titled "workflow-class-tunable shadow-Git checkpointing" (spec §28). The concepts are spec-committed; only the *declaration site* was missing. T2 verdict: FACTOR-OUT, decided. **R2 introduces no IS-spec revision, no CXA revision, no ADD revision.** `implementation-planner` SKILL.md §2 consequence 1 (the planner never extends a spec) is satisfied — R2 cites pre-existing carriers, it does not invent commitments.

### §0.4 Sections preserved verbatim from v2.1/v2.2

| Section | Status |
|---|---|
| §0 (v2.2 change-note) | Superseded by this §0 at v2.3 (the v2.2 F3-02 closure record is retained by reference) |
| §1 Spec inventory | Preserved verbatim |
| §2 U-IS-01, U-IS-03, U-IS-04, U-IS-07, U-IS-08, U-IS-09, U-IS-10, U-IS-11, U-IS-13, U-IS-15, U-IS-16 | **Preserved verbatim** — the 11 CLEARED units |
| §2 U-IS-02, U-IS-05, U-IS-06, U-IS-12, U-IS-14, U-IS-17 | **Revised** — see §5 |
| §3 Dependency graph | Revised at the delta nodes/edges only (§6.2); all other edges + the acyclicity proof preserved |
| §4 Coverage matrix | Revised at the delta only (§6.1); the 10-contract × 17-unit grid otherwise preserved |

**Explicit non-touch of landed-clean units.** U-IS-01 (`ResidenceContract` undeclared) and U-IS-04 (`ContractID` undeclared) were audited **CLEARED** — the audit classified `ResidenceContract`/`ContractID` as M-1 *inline tails*, not blocking, and the verified recount over-forked nothing here. Both units are **landed** (`harness-is/CLAUDE.md` §3 names U-IS-01/04 as L0 anchors; MEMORY records the 7b operational-minimum landing). **R2 deliberately does NOT revise U-IS-01 or U-IS-04.** This is a real choice, surfaced not buried: `ContractID` now has a `harness-core` carrier (U-CORE-01, R1) and U-IS-04 *could* be re-pointed to import it; but (a) the audit did not fork U-IS-04, (b) the task scopes R2 to FORK/CONFORM units + the R1 hand-off and instructs no re-litigation of landed-clean units, and (c) `ContractID` was inline-materializable by the audit's own classification — a landed inline declaration is materializability-clean. **Recommendation: leave U-IS-01/U-IS-04 untouched at R2; if a future pass revises either for an unrelated reason, re-point `ResidenceContract`/`ContractID` then.** Logged as a standing Class-3 informational item (Q-R2-3, §7) so the divergence (U-IS-04's local-or-inline `ContractID` vs the U-CORE-01 `ContractID` alias) is on the record, not silently absorbed.

### §0.5 Status posture

`Status: Proposed` — preserved until the operator ratifies and (per `implementation-planner` SKILL.md §8) until any P6-CK-analog re-clearance. v2.3 emits on ratification.

---

## §1 Type re-pointing — the carrier resolution table

Every undeclared type the IS audit flagged at a FORK/CONFORM unit, mapped to its ratified carrier. Carriers per the T1 carrier map disposition rows + the R1 U-CORE-01 body.

| Undeclared type | Consuming IS unit(s) | Ratified carrier | Carrier source | Edge added to consumer | Disposition |
|---|---|---|---|---|---|
| `WorkflowClass` (= `WorkloadClass`) | U-IS-02, U-IS-05 (`WorkflowClass` spelling); U-IS-12 (`WorkloadClass` spelling) | `harness-core` — **landed U-CP-00** | T1 disposition-1 (`WorkloadClass` row); R1 §3.1 | `Depends on: [U-CP-00]` | re-point + spelling-unify (§3) |
| `DeploymentSurface` | U-IS-02, U-IS-05 | `harness-core` — **U-CORE-01** (R1, landed) | T1 disposition-1 (`DeploymentSurface` row) | `Depends on: [U-CORE-01 (cross-axis: core)]` | re-point |
| `WorkflowEvent` | U-IS-14 | `harness-core` — **U-CORE-01** (R1, landed; Q-R1-2 ratified `WorkflowEvent` into U-CORE-01) | T2 resolution table (`WorkflowEvent` row, decided); R1 §2 | `Depends on: [U-CORE-01 (cross-axis: core)]` | re-point |
| `UnitId` | U-IS-17 (`carrier_units : List[UnitId]`) | `harness-core` — **U-CORE-01** (R1, landed; Q-R1-5 ratified `UnitId` as plan-internal alias in U-CORE-01) | T1 disposition-1 (identity-alias module); R1 §2 | `Depends on: [U-CORE-01 (cross-axis: core)]` | re-point (CONFORM) |
| `GitRepository`, `CommitRange`, `CommitId` | U-IS-06 | **UNRESOLVED** — operator classification owed | T1 carrier map: "Open (git trio)"; IS audit §4A.6 Class 2 | none yet — see Q-R2-1 | open question (§7) |
| `ResidenceContract` | U-IS-01 (landed, CLEARED) | (would be IS-inline per T1) | T1 disposition-2 ("`ResidenceContract` inline — Decided") | n/a — U-IS-01 not revised at R2 | out of scope (§0.4) |
| `ContractID` | U-IS-04 (landed, CLEARED); also U-IS-06 `composes_with` | `harness-core` — U-CORE-01 (available) | T1 disposition-1 (identity-alias module) | n/a for U-IS-04 (§0.4); see §5 U-IS-06 note | partial — see §5 U-IS-06 |

**Edge-form discipline.** Two forms, matching R1 verbatim (R1 §3 "Edge form"):
- `[U-CORE-01 (cross-axis: core)]` — for U-CORE-01 imports. `harness-core` is shared substrate, not an axis; the `(cross-axis: core)` annotation makes the import explicit and reviewable per `implementation-planner` SKILL.md §7. **This is an import edge, not an outbound CXA edge** — per T2 it does not violate the CXA §2.4 "IS = 0 outbound" invariant.
- `[U-CP-00]` — for the `WorkloadClass` carrier. R1 §3.1 + §3.5 chose the **unannotated** `[U-CP-00]` form for `WorkloadClass` (U-CP-00 is the landed carrier; R1 Q-R1-3 ratified the edge to `[U-CP-00]`, not folded into U-CORE-01). R2 follows R1 exactly — no third edge form is invented.

`U-CP-00` and `U-CORE-01` both physically reside in the `harness-core` package; the two distinct edge spellings reflect the two distinct *carrier units*, per the R1-ratified convention.

---

## §2 M-1-IS pattern resolution

The IS audit's single systemic finding (`harness-adversarial-reviewer` SKILL.md §6 ≥3-occurrence threshold). Resolution, per-unit:

| M-1-IS occurrence | Type(s) | Resolution at R2 |
|---|---|---|
| U-IS-02 `resolve_path` params `workflow_class`, `deployment_surface` | `WorkflowClass`, `DeploymentSurface` | Re-point: `WorkflowClass` → `WorkloadClass` (U-CP-00, spelling-unified §3); `DeploymentSurface` → U-CORE-01. Edges: `[U-CP-00]`, `[U-CORE-01 (cross-axis: core)]`. |
| U-IS-05 `initialize_jsonl_event_ledger` params | `WorkflowClass`, `DeploymentSurface` | Same as U-IS-02 — identical signature pair. |
| U-IS-12 `BoundedWindow.workload_class` field | `WorkloadClass` | Re-point to U-CP-00. Edge: `[U-CP-00]`. (U-IS-12 already uses the `WorkloadClass` spelling — no spelling change needed here; see §3.) |
| U-IS-14 `on_workflow_event(event : WorkflowEvent)` param | `WorkflowEvent` | Re-point to U-CORE-01 (`WorkflowEvent` + `WorkflowEventClass` per R1 Q-R1-2). Edge: `[U-CORE-01 (cross-axis: core)]`. |

After R2, M-1-IS is fully resolved: every M-1-IS type at every M-1-IS consumer has a declared, in-`Depends on`-cone carrier. The IS audit's note "the graph is acyclic but **incomplete** at the cross-axis-input boundary" is closed — the missing nodes (`U-CORE-01`, `U-CP-00`) are now real Level-0 nodes (declared in `Implementation_Plan_Harness_Core_v1_0.md` §3 and the CP plan respectively), and the IS units declare inbound edges to them. **No new IS-plan node is created** — the carriers live in `harness-core`/CP, and IS only adds inbound edges (R1 §5.2: a source node with inbound-only edges cannot create a cycle; the IS DAG stays acyclic).

The audit's reading (c) (CXA inversion) and reading (b) (X-AL-3 extension) are both dead per T2 (§0.3). Only reading (a) — `harness-core` carrier — survives, and R2 applies it.

**`AuditPayload`/`AuditLedger` cross-reference (audit-mandated).** The IS audit and T1 both confirmed `AuditPayload`/`AuditLedger` are **not** IS-exported — IS exports `StateLedgerEntry` (the 6-field primitive, U-IS-07) + the hash-chain discipline. R2 makes **no change** to U-IS-17's export manifest on this account; the OD-side `AuditPayload`/`AuditLedger` carrier is R5 scope. Recorded here so the negative result is visible.

---

## §3 `WorkflowClass`-vs-`WorkloadClass` spelling unification

The carrier map flagged an IS-internal spelling divergence: the IS plan uses **two spellings of one type**. Verified against the v2.1 bodies:

- **U-IS-02** signature: `workflow_class : WorkflowClass` (line 215–216).
- **U-IS-05** signature: `workflow_class : WorkflowClass` (line 365).
- **U-IS-12** signature: `BoundedWindow.workload_class : WorkloadClass` (line 769).
- **U-IS-17** manifest: seam `WORKLOAD_CLASS_OPT_IN_MANIFEST_EXPORT` uses the `WORKLOAD`/`WorkloadClass` spelling already.

T1 carrier map ("`WorkloadClass` vs `WorkflowClass`" reconciliation): the two are the *same concept* — path stability "across runs of the same workflow class" is the C-CP-07 §7.3 routing enum. **Canonical spelling: `WorkloadClass`** (the spec-committed CP enum, landed in `harness-core` via U-CP-00). T2 confirms: `WorkflowClass`/`WorkloadClass` @ IS — FACTOR-OUT to the existing U-CP-00 `WorkloadClass`, decided.

**R2 unification action** (applied in the §5 revised bodies):

| Unit | Before | After |
|---|---|---|
| U-IS-02 | param `workflow_class : WorkflowClass` | param `workflow_class : WorkloadClass` |
| U-IS-05 | param `workflow_class : WorkloadClass` (renamed from `WorkflowClass`) | param `workflow_class : WorkloadClass` |
| U-IS-12 | `BoundedWindow.workload_class : WorkloadClass` | unchanged — already canonical |

The **parameter/field name** `workflow_class` (snake-case identifier) is left as-is — it is the spec's prose term ("workflow class") and is not the *type*; only the **type name** unifies to `WorkloadClass`. (`U-IS-12`'s field is already `workload_class : WorkloadClass`; a follow-on verbatim pass may consider whether the IS plan wants the parameter name unified too — that is a cosmetic naming question, NOT a materializability item, and R2 does not force it. Logged as Q-R2-2, §7.)

Acceptance-criteria prose mentioning "workflow-class" / "workflow class" is **spec prose** and is preserved verbatim — it refers to the concept, not the type identifier.

---

## §4 U-IS-02 retrospective — landed-source re-point action item

**U-IS-02 is LANDED** (`harness-is/CLAUDE.md` §3 L1 anchor; MEMORY `phase-7-bootstrap-status` — "7b: 12/12 operational-minimum units landed 2026-05-15"). Its `resolve_path` signature consumed `WorkflowClass` and `DeploymentSurface` **when neither type had a declaring carrier** (carrier map: "consumed undeclared at IS U-IS-02/05"; IS audit retrospective section). The landed coding lane therefore did one of three non-conformant things at landing time:

1. inlined a local `WorkflowClass`/`DeploymentSurface` enum declaration inside the U-IS-02 source module, or
2. used a bare `str` / `Any` placeholder at the `workflow_class` / `deployment_surface` parameter positions, or
3. imported from a sibling unit's declaration.

All three are **non-conformant once U-CORE-01 and U-CP-00 are the canonical carriers**. This is the exact U-AS-02 `ToolContext` / U-OD-04 retrospective shape the audit cross-references.

### §4.1 R2-application action item (AI-R2-1) — MANDATORY, source-level

> **Before the v2.3 IS plan lands and before U-IS-05 (the next M-1-IS consumer) lands, the landed U-IS-02 source MUST be re-checked and re-pointed.** Specifically:
>
> 1. **Inspect** the landed U-IS-02 implementation source (under `harness-is/`) — the `path-resolver` module — and determine which of the three non-conformant shapes (1)/(2)/(3) above is present at the `workflow_class` / `deployment_surface` parameter positions.
> 2. **Re-point** the parameter types to import from `harness-core`: `WorkloadClass` from the U-CP-00 module (`harness_core.workload_class`), `DeploymentSurface` from the U-CORE-01 module. Delete any inlined local enum declaration.
> 3. **Verify byte-exact agreement**: if the landed source inlined a local `WorkflowClass`/`DeploymentSurface` enum, its members and string values MUST match the U-CORE-01 `DeploymentSurface` (3 values: `local-development | self-hosted-server | managed-cloud`) and the U-CP-00 `WorkloadClass` byte-exact. If the landed shape diverges (e.g. a different cardinality, different member spelling), the landed U-IS-02 must be **revised to conform** — the carrier shape is canonical, not the landed inline.
> 4. **Record** the re-point in the v2.3 IS plan's change-note (the operator-applied artifact) and in the Phase 7 execution log as the discharge of this retrospective.

**HARD WALL note.** R2 (this proposal) does **not** touch U-IS-02 source — that is the R2-application step's responsibility, performed by the operator or a `phase-7-implementation` lane after ratification. R2 surfaces AI-R2-1 so the re-check is not missed; it is the load-bearing operator action this retrospective triggers.

### §4.2 Why this is not silent absorption

`CLAUDE.md` §4.3 names silent absorption of a design-phase defect as the worst failure mode. The U-IS-02 landed-source gap is **not** a design defect (T2 closed the X-AL-3 reading) — it is a *carrier-ordering* artifact: the unit landed before its carrier existed. AI-R2-1 makes the reconciliation explicit and auditable. The §2.7.6 fork class for the retrospective is **Class 3 (informational)** — non-blocking on the design substrate; the U-IS-02 re-check is the in-workspace action it triggers.

U-IS-02's *plan unit body* is also revised at R2 (§5) — it gains the carrier edges + the spelling unification. The plan-body revision and the source re-point are two halves of one reconciliation; both are required for U-IS-02 to be conformant.

---

## §5 Revised unit bodies

Filed in canonical per-unit plan format (`implementation-planner` SKILL.md §4.4). Changes from the v2.1 body are the carrier `Depends on` edges, the type re-points in `Signatures` / `Inputs`, and the spelling unification. All other content (acceptance criteria, tests, rollback boundary) is preserved verbatim from v2.1 unless a re-point forces a wording touch — such touches are flagged inline. The 11 CLEARED units are `[preserved verbatim from v2.1 §2]` and not reproduced here.

---

#### U-IS-02 — Implement path-resolver primitive  *(REVISED)*

**Implements:** [C-IS-01 §1]

**Depends on:** [U-IS-01, U-CP-00, U-CORE-01 (cross-axis: core)]

> *R2 delta:* added `U-CP-00` (carrier of `WorkloadClass`) and `U-CORE-01 (cross-axis: core)` (carrier of `DeploymentSurface`). `U-IS-01` edge preserved.

**Inputs:** `PathClass` enum + metadata from U-IS-01; `WorkloadClass` from `harness-core` (U-CP-00); `DeploymentSurface` from `harness-core` (U-CORE-01); implementation-time configuration supplying canonical path strings per (workload_class, deployment_surface) cell.

> *R2 delta:* "workflow class identifier" / "deployment surface identifier" (prose placeholders for undeclared types) replaced with the explicit `harness-core` carrier citations.

**Files affected:** Path-resolver implementation (logical name: `path-resolver`); path-binding configuration loader (logical name: `path-binding-loader`).

**Signatures:**
```
resolve_path(
  path_class          : PathClass,
  workflow_class      : WorkloadClass,        // harness-core, U-CP-00 (spelling unified from WorkflowClass per R2 §3)
  deployment_surface  : DeploymentSurface     // harness-core, U-CORE-01
) -> Path
```

**Acceptance criteria:** *(preserved verbatim from v2.1 — the criteria reference the concepts "workflow class" / "deployment surface" as spec prose, not the type identifier)*
1. Repeated calls within a single run on the same triple return identical `Path` values (stability invariant within run).
2. Same `(path_class, workflow_class, deployment_surface)` triple across run boundaries returns identical `Path` values (workflow-canonical per spec §1).
3. Same `path_class` and `deployment_surface` but differing `workflow_class` MAY return differing paths without violating any contract (workflow-class-varying flex).
4. Resolver does not hard-code path strings; all paths derive from path-binding configuration source.
5. Resolver does not produce paths violating C-IS-02 substrate-residence rule (cross-unit invariant verified once U-IS-03 lands).

**Tests:** *(preserved verbatim from v2.1)*
- `test_resolve_path_stability_within_run`; `test_resolve_path_workflow_canonical_across_runs`; `test_resolve_path_workflow_class_variance_permitted`; `test_resolve_path_no_hardcoded_paths`.

**Rollback boundary:** Revert path-resolver + path-binding loader. Downstream callers fail at runtime.

> **Landed-unit retrospective (R2 §4 / AI-R2-1).** U-IS-02 is a landed L1 anchor; it consumed `WorkflowClass`/`DeploymentSurface` before their carriers existed. The R2-application step MUST re-check and re-point the landed source per §4.1 AI-R2-1 before v2.3 lands.

---

#### U-IS-05 — Implement JSONL event ledger file lifecycle  *(REVISED)*

**Implements:** [C-IS-03 §3 (JSONL event ledger sub-role row)]

**Depends on:** [U-IS-01, U-IS-02, U-IS-04, U-CP-00, U-CORE-01 (cross-axis: core)]

> *R2 delta:* added `U-CP-00` (`WorkloadClass`) and `U-CORE-01 (cross-axis: core)` (`DeploymentSurface`). The three within-axis edges preserved.

**Inputs:** `PathClass.STATE_LEDGER` (U-IS-01); `resolve_path` (U-IS-02); `GitTierSubRole.JSONL_EVENT_LEDGER` (U-IS-04); `WorkloadClass` from `harness-core` (U-CP-00); `DeploymentSurface` from `harness-core` (U-CORE-01); workflow open / resume signal.

> *R2 delta:* added the two `harness-core` carrier citations (consumed at the `initialize_jsonl_event_ledger` signature).

**Files affected:** JSONL event ledger lifecycle (logical name: `jsonl-event-ledger-lifecycle`).

**Scope.** File existence + structural validation at workflow open / resume. Does NOT write or read entries (C-IS-07 territory) or compute hashes (C-IS-06 territory).

**Signatures:**
```
initialize_jsonl_event_ledger(
  workflow_class       : WorkloadClass,        // harness-core, U-CP-00 (spelling unified from WorkflowClass per R2 §3)
  deployment_surface   : DeploymentSurface     // harness-core, U-CORE-01
) -> JsonlLedgerHandle

validate_jsonl_event_ledger_format(
  handle  : JsonlLedgerHandle
) -> LedgerFormatValidationResult

record JsonlLedgerHandle {
  canonical_path  : Path
  exists          : bool
  entry_count     : Integer
}

enum LedgerFormatValidationResult {
  VALID,
  EMPTY,
  MALFORMED_LINE,
  IO_ERROR
}
```

> *R2 delta:* `workflow_class` parameter type re-pointed `WorkflowClass` → `WorkloadClass`; `deployment_surface` re-pointed to the U-CORE-01 carrier. `JsonlLedgerHandle` / `LedgerFormatValidationResult` are U-IS-05-declared (in-unit) — unchanged.

**Acceptance criteria:** *(preserved verbatim from v2.1)*
1. `initialize_jsonl_event_ledger` resolves canonical path via `resolve_path(PathClass.STATE_LEDGER, workflow_class, deployment_surface)`.
2. File absent ⇒ create empty file; return handle with `exists=true, entry_count=0`.
3. File present ⇒ return handle with `exists=true, entry_count=N` (line-counted); does not modify contents.
4. `validate_jsonl_event_ledger_format` returns `VALID` if every non-empty line parses as JSON; `EMPTY` if zero-length; `MALFORMED_LINE` if any line fails JSON parse; `IO_ERROR` on filesystem access failure.
5. Lifecycle MUST NOT append entries or modify existing entries.
6. Entry-shape validation (six-field shape) is NOT performed; only JSON-syntactic parseability.

**Tests:** *(preserved verbatim from v2.1)*
- `test_initialize_creates_file_if_absent`; `test_initialize_returns_handle_if_present`; `test_validate_returns_valid_for_well_formed_jsonl`; `test_validate_returns_malformed_line_for_bad_jsonl`; `test_validate_returns_empty_for_zero_length_file`; `test_lifecycle_does_not_append_entries`.

**Rollback boundary:** Revert lifecycle. Harness boot fails at ledger initialization.

> **Note.** U-IS-05 is FORK-blocked in the pipeline and (per the IS audit) NOT landed — no retrospective re-check applies; it materializes fresh against the v2.3 body.

---

#### U-IS-06 — Declare atomic deploy-event composition contract + verification primitive  *(REVISED — partial; one open question)*

**Implements:** [C-IS-04 §4]

**Depends on:** [U-IS-01, U-IS-04, U-CORE-01 (cross-axis: core)]

> *R2 delta:* added `U-CORE-01 (cross-axis: core)` — the carrier of `ContractID` (per note (i) below; R2 default). **Q-R2-1 (the git-domain trio) does NOT affect this edge** — its options are (A) exclude as git-library primitives or (B) IS-internal carrier, neither of which is `harness-core`. The two within-axis edges preserved.

**Inputs:** IS spec v1.2 §4 4-class deploy-unit composition; §4 atomicity contract; §4 verification surface; `PathClass` (U-IS-01); `GitTierSubRole.VERSIONING` + `GitTierSubRole.STATE_LEDGER_VIA_COMMIT_STREAM` (U-IS-04); `ContractID` (see note below); git-domain types `GitRepository` / `CommitRange` / `CommitId` (see Q-R2-1).

**Files affected:** Atomic deploy-event composition declaration (logical name: `atomic-deploy-event-contract`); deploy-event verification test suite (logical name: `atomic-deploy-event-verification`).

**Signatures:** *(structure preserved verbatim from v2.1; the undeclared types are annotated)*
```
enum DeployArtifactClass {
  PROMPTS,             // C-IS-01 PathClass.PROMPTS
  CODE,                // workflow implementation code; Python-first per Persona §7
  EVAL_SETS,           // eval-set artifacts co-located with code
  ROUTING_MANIFEST     // C-IS-01 PathClass.ROUTING_MANIFEST per ADR-F1 v1.2
}

record DeployEventComposition {
  artifact_classes        : Set[DeployArtifactClass]
  atomicity_property      : AtomicityProperty
  observability_property  : ObservabilityProperty
  composes_with           : Set[ContractID]            // ContractID — see note (i)
}

enum AtomicityProperty { ALL_OR_NOTHING_PER_COMMIT }
enum ObservabilityProperty { SINGLE_VERSION_OBSERVABILITY }

verify_deploy_atomicity(
  git_repository  : GitRepository,                     // git-domain type — see Q-R2-1
  commit_range    : CommitRange                        // git-domain type — see Q-R2-1
) -> DeployAtomicityVerificationReport

record DeployAtomicityVerificationReport {
  commits_inspected   : Integer
  violations          : List[DeployAtomicityViolation]
  bisection_isolated  : bool
}

record DeployAtomicityViolation {
  violation_type  : ViolationType
  commit_ids      : List[CommitId]                     // git-domain type — see Q-R2-1
  description     : string
}

enum ViolationType { SPLIT_DEPLOY, MISSING_COMMIT_STREAM_ENTRY }
```

**Note (i) — `ContractID`.** `DeployEventComposition.composes_with : Set[ContractID]` consumes `ContractID`. The IS audit classified `ContractID` as an M-1 *inline tail* (CLEARED). R1's U-CORE-01 declares `ContractID` in the identity-alias module. **R2 default: re-point `ContractID` to the U-CORE-01 carrier** — unlike U-IS-04 (landed, untouched per §0.4), U-IS-06 is being revised anyway (it is a FORK unit), so re-pointing `ContractID` here costs nothing and is the materializability-clean choice. The `[U-CORE-01 (cross-axis: core)]` edge in U-IS-06's `Depends on` is for `ContractID`. This decision is **independent of Q-R2-1** (the git-domain trio); the git trio adds no `harness-core` edge under either of its options.

**Note (ii) — `DeployArtifactClass` / `DeployEventComposition` / `AtomicityProperty` / `ObservabilityProperty` / `DeployAtomicityVerificationReport` / `DeployAtomicityViolation` / `ViolationType`** are all U-IS-06-declared (in-unit) — materializability-clean, unchanged.

**OPEN QUESTION Q-R2-1 — git-domain trio (`GitRepository`, `CommitRange`, `CommitId`).** These three types have **no carrier** and R2 cannot resolve them from the authority chain (IS audit §4A.6: §2.7.6 **Class 2 — operator-decision**; T1 carrier map: "Open (git trio)"). The operator must classify:
- **(A) Stack-primitive of a git library** (e.g. a `pygit2` / `GitPython` repo handle, a commit-range expression, a commit SHA `str`-newtype) → **exclude** from carrier work, same as `Path`/`Bytes`. U-IS-06 then needs **no** edge for the trio; the signature is materialized directly against the chosen git library's types.
- **(B) Harness abstraction** (a thin H_T wrapper over the git library) → an **IS in-place carrier** is needed (declare `GitRepository`/`CommitRange`/`CommitId` in U-IS-06's own Signatures block, or a small IS foundational unit). They are IS-axis-owned either way (T1 disposition-2, IS-internal) — **not** `harness-core` (no other axis consumes them).
- **R2 default (pending ratification):** classification (A) — git-library primitives, excluded. Rationale: `verify_deploy_atomicity` is an *offline / on-demand* verification primitive (acc #5) operating directly on git history; a thin direct binding to the committed git library is the framework-pull-disciplined choice (`CLAUDE.md` §3.2) and introduces no new harness type. Under default (A), U-IS-06's `Depends on` stays `[U-IS-01, U-IS-04, U-CORE-01 (cross-axis: core)]` (the `U-CORE-01` edge is for `ContractID` per note (i)) and the git types are materialized against the git library. **If the operator rules (B)**, add the IS-internal git-type carrier declaration to U-IS-06's Signatures block and no `Depends on` change (IS-internal, in-unit).

**Acceptance criteria:** *(preserved verbatim from v2.1)*
1. `DeployArtifactClass` enum: exactly 4 values matching spec §4 verbatim.
2. `DeployEventComposition.composes_with` includes `C-IS-03 commit-stream sub-role` and `C-IS-08` (orthogonal).
3. `verify_deploy_atomicity` over well-formed commit range returns `violations == []`.
4. `verify_deploy_atomicity` over split-deploy range returns `SPLIT_DEPLOY` violation with relevant commit IDs.
5. Verification is offline / on-demand; does not block deploy commits at write-time.
6. Bisection invariant: violation in commit range ⇒ bisection isolates violating commit in O(log N).

**Tests:** *(preserved verbatim from v2.1)*
- `test_deploy_artifact_class_completeness`; `test_verify_well_formed_commits_returns_no_violations`; `test_verify_split_deploy_returns_violation`; `test_verify_composes_with_commit_stream`; `test_verify_bisection_isolates_violating_commit`.

**Rollback boundary:** Revert composition declaration + verification test suite.

---

#### U-IS-12 — Implement C2-pole selective bounded read contract via NavigationPrimitive interface  *(REVISED)*

**Implements:** [C-IS-07 §7.2, §7.3]

**Depends on:** [U-IS-05, U-IS-07, U-CP-00]

> *R2 delta:* added `U-CP-00` (carrier of `WorkloadClass`, consumed at `BoundedWindow.workload_class`). The two within-axis edges preserved.

**Inputs:** `JsonlLedgerHandle` (U-IS-05); `StateLedgerEntry` (U-IS-07); `WorkloadClass` from `harness-core` (U-CP-00); IS spec v1.2 §7.2 + §7.3 + §7.4 deferred-list naming.

> *R2 delta:* added the `WorkloadClass` carrier citation.

**Files affected:** C2-pole read contract (logical name: `state-ledger-read-contract`); NavigationPrimitive interface declaration (logical name: `navigation-primitive-interface`); four minimum-viable concrete primitives (`nav-read-entry`, `nav-read-range`, `nav-read-recent`, `nav-read-by-idempotency-key`).

**Scope.** Returns `List[StateLedgerEntry]` to caller; dynamic-suffix placement is CP-axis context-engineering territory (Session 3).

**Signatures:**
```
interface NavigationPrimitive {
  read(query: NavigationQuery, bounded_window: BoundedWindow) -> ReadResult
}

record NavigationQuery {
  by_action_id          : Optional[Identifier]
  by_idempotency_key    : Optional[Identifier]
  by_position_range     : Optional[PositionRange]
  most_recent_n         : Optional[Integer]
}

record PositionRange {
  start_position  : Integer
  end_position    : Integer
}

record BoundedWindow {
  max_entries     : Integer
  workload_class  : WorkloadClass             // harness-core, U-CP-00
}

record ReadResult {
  entries        : List[StateLedgerEntry]
  truncated      : bool
  next_position  : Optional[Integer]
}
```

> *R2 delta:* `BoundedWindow.workload_class` type re-pointed to the U-CP-00 `harness-core` carrier. The field already used the canonical `WorkloadClass` spelling (no spelling change — see §3). `NavigationPrimitive` / `NavigationQuery` / `PositionRange` / `BoundedWindow` / `ReadResult` are U-IS-12-declared (in-unit) — unchanged. `Identifier` is U-IS-07-declared `opaque` (in-cone) — unchanged.

Four minimum-viable concrete primitives wrap `NavigationPrimitive.read`: `read_entry(action_id, …)`, `read_range(start, end, …)`, `read_recent(n, …)`, `read_by_idempotency_key(key, …)`.

**Acceptance criteria:** *(preserved verbatim from v2.1)*

| # | Property | Criterion | Spec ref |
|---|---|---|---|
| 1 | Selective | No public API returns ledger without NavigationQuery + BoundedWindow | §7.2 row 1 |
| 2 | Bounded | Truncates at max_entries; next_position surfaced for continuation | §7.2 row 2 |
| 3 | Navigation-primitive-mediated | All reads pass through interface | §7.2 row 3 |
| 4 | Read-into-dynamic-suffix boundary | Returns List[StateLedgerEntry]; placement is CP-axis | §7.2 row 4 + ADR-F2 §Rationale (b)(ii) |
| 5 | Four minimum-viable primitives | All four implemented per spec §7.4 naming | §7.4 |
| 6 | Concurrent reads non-blocking | Reads do not block reads or writes | §7.3 |
| 7 | Read does not modify ledger | Byte-identity preserved | C2-pole property |

**Out-of-unit scope:** Per IS spec v1.2 §7.4 deferral — bounding-window-size defaults per workload class are configuration-supplied at execution time; not asserted at this unit's tests.

**Tests:** *(preserved verbatim from v2.1)*
- `test_read_entry_by_action_id_match`, `test_read_entry_by_action_id_no_match`, `test_read_range_returns_correct_window`, `test_read_recent_returns_last_n_chronological`, `test_read_by_idempotency_key_match`, `test_read_bounded_window_truncates`, `test_read_paginated_continuation`, `test_read_full_file_cat_precluded`, `test_read_concurrent_non_blocking_reads`, `test_read_concurrent_with_write_non_blocking`, `test_read_does_not_modify_ledger`, `test_read_returns_dynamic_suffix_boundary_not_crossed`.

**Rollback boundary:** Revert read contract + NavigationPrimitive interface + four concrete primitives. CP-axis context engineering, resume-time replay, audit-ledger inspection, cross-axis idempotency-key join queries all fail at runtime.

---

#### U-IS-14 — Implement shadow-Git checkpoint primitive (cadence-driven snapshot creation)  *(REVISED)*

**Implements:** [C-IS-08 §8.2, §8.4]

**Depends on:** [U-IS-04, U-IS-13, U-CORE-01 (cross-axis: core)]

> *R2 delta:* added `U-CORE-01 (cross-axis: core)` (carrier of `WorkflowEvent` + `WorkflowEventClass`, per R1 Q-R1-2 ratification). The two within-axis edges preserved.

**Inputs:** `GitTierSubRole.SHADOW_GIT_CHECKPOINTING` (U-IS-04); `WorkloadManifestOptIns` + `CheckpointCadence` (U-IS-13); `WorkflowEvent` from `harness-core` (U-CORE-01); IS spec v1.2 §8.2 + §8.4.

> *R2 delta:* added the `WorkflowEvent` carrier citation.

**Files affected:** Shadow-Git checkpoint primitive (logical name: `shadow-git-checkpoint`); cadence-trigger driver (logical name: `shadow-git-cadence-driver`).

**Scope.** Snapshot creation only. Rollback at U-IS-15.

**Signatures:**
```
create_shadow_git_checkpoint(
  workflow_run_id  : Identifier,
  trigger_context  : CheckpointTriggerContext
) -> CheckpointResult

record CheckpointTriggerContext {
  cadence                    : CheckpointCadence
  workflow_step_id           : Optional[Identifier]
  tool_call_id               : Optional[Identifier]
  significant_change_marker  : Optional[string]
  explicit_marker            : Optional[string]
}

record CheckpointResult {
  checkpoint_id  : Identifier
  shadow_ref     : string
  created_at     : Timestamp
  triggered_by   : CheckpointCadence
}

on_workflow_event(event: WorkflowEvent) -> Optional[CheckpointResult]   // WorkflowEvent — harness-core, U-CORE-01
```

> *R2 delta:* `on_workflow_event` parameter type `WorkflowEvent` re-pointed to the U-CORE-01 `harness-core` carrier. `CheckpointTriggerContext` / `CheckpointResult` are U-IS-14-declared (in-unit) — unchanged. `Identifier` / `Timestamp` are U-IS-07-declared `opaque` (in-cone) — unchanged. `CheckpointCadence` is U-IS-13-declared (in-cone) — unchanged.

**Acceptance criteria:** *(preserved verbatim from v2.1; rows 7+ continue per v2.1 §2.5 — preserved by reference)*

| # | Property | Criterion | Spec ref |
|---|---|---|---|
| 1 | Snapshot creation | Shadow ref/branch in same git repo as versioning sub-role | §8.4 |
| 2 | Non-pollution of main branch | Shadow refs absent from main commit history | §8.4 |
| 3–6 | Cadence-driven firing | PER_STEP, PER_TOOL_CALL, PER_SIGNIFICANT_CHANGE, PER_EXPLICIT_MARKER each fire per spec semantics | §8.2 |
| 7+ | *(remaining acceptance rows preserved verbatim from v2.1 §2.5)* | | |

> **Spec-traceability note on `on_workflow_event`.** `WorkflowEvent` carries the C-CP-05 §5.1 8-class lifecycle taxonomy. U-IS-14 consuming it is faithful: IS spec C-IS-08 §8.2 commits *cadence-driven* checkpoint firing, and `on_workflow_event` is the event-hook surface a cadence driver subscribes to. The `WorkflowEvent` *type* is FACTOR-OUT (T2, decided) and now lives in `harness-core` (U-CORE-01) — U-IS-14 imports it; this is a `harness-core` import, **not** an IS→CP outbound CXA edge. The CXA §2.4 "IS = 0 outbound" invariant holds.

**Tests:** *(preserved verbatim from v2.1)* — including the `on_workflow_event` cadence-firing tests per v2.1 §2.5.

**Rollback boundary:** *(preserved verbatim from v2.1)* — Revert shadow-Git checkpoint primitive + cadence-trigger driver.

---

#### U-IS-17 — Declare substrate seam exports manifest  *(REVISED — CONFORM)*

**Implements:** [C-IS-10 §10.1, §10.2, §10.3, §10.4, §10.5, §10.6]

**Depends on:** [U-IS-01, U-IS-02, U-IS-05, U-IS-07, U-IS-08, U-IS-09, U-IS-10, U-IS-11, U-IS-12, U-IS-13, U-CORE-01 (cross-axis: core)]

> *R2 delta:* added `U-CORE-01 (cross-axis: core)` (carrier of `UnitId`, consumed at `SubstrateSeamExport.carrier_units : List[UnitId]`). The 10 within-axis carrier edges preserved verbatim.

**Inputs:** IS spec v1.2 §10.1 through §10.6 export sub-sections; `UnitId` from `harness-core` (U-CORE-01).

> *R2 delta:* added the `UnitId` carrier citation. `UnitId` is the only undeclared type the audit flagged at U-IS-17 (audit verdict: CONFORM on the `UnitId` tail). Per R1 Q-R1-5, `UnitId` is a ratified plan-internal `str`-newtype declared in U-CORE-01's identity-alias module.

**Files affected:** Substrate seam exports manifest (logical name: `is-axis-substrate-seam-exports-manifest`).

**Scope.** Declarative manifest only; no executable behavior. Per OD-S1-3.A, consumer-axis dependency declarations NOT authored at this unit.

**Signatures:** *(preserved verbatim from v2.1; the `UnitId` consumption is annotated)*
```
enum SeamId {
  STATE_LEDGER_ENTRY_SHAPE_EXPORT,             // §10.1
  IDEMPOTENCY_KEY_JOIN_EXPORT,                 // §10.2
  HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT,   // §10.3
  FILESYSTEM_PATH_CONTRACT_EXPORT,             // §10.4
  JSONL_EVENT_LEDGER_FORMAT_EXPORT,            // §10.5
  WORKLOAD_CLASS_OPT_IN_MANIFEST_EXPORT        // §10.6
}

enum ConsumingAxis { ACTION_SURFACE, CONTROL_PLANE, OPERATIONAL_DISCIPLINE }

record SubstrateSeamExport {
  seam_id                : SeamId
  spec_citation          : string
  export_surface         : string
  carrier_units          : List[UnitId]        // UnitId — harness-core, U-CORE-01 (plan-internal alias, R1 Q-R1-5)
  consuming_axes         : List[ConsumingAxis]
  composition_references : List[string]
}
```

> *R2 delta:* `SubstrateSeamExport.carrier_units : List[UnitId]` — `UnitId` re-pointed to the U-CORE-01 carrier. `SeamId` / `ConsumingAxis` / `SubstrateSeamExport` are U-IS-17-declared (in-unit) — unchanged. The manifest's 6-seam structure, `carrier_units` membership lists, `consuming_axes`, and all composition references are **preserved verbatim from v2.1** — R2's only U-IS-17 change is the `UnitId` carrier re-point + the corresponding `Depends on` edge.

> **Note — `carrier_units` is the carrier-of-the-carrier.** `SubstrateSeamExport.carrier_units` is a manifest field listing IS-plan unit IDs (`"U-IS-07"` etc.); it consumes the `UnitId` alias as its element type. U-IS-17 importing `UnitId` from `harness-core` is consistent — the alias is the nominal type for a plan-unit identifier; the manifest's *values* (the unit-ID strings) are unchanged.

**Manifest content:** *[preserved verbatim from v2.1 §2.6 — the 6-row table; M-1-IS taint on cited carriers U-IS-02/05/12 is resolved by their R2 revisions above, no manifest-content change]*

**Composition references:** *[preserved verbatim from v2.1 §2.6 — §10.1 through §10.6, including the F2-12 carry-forward note]*

**Acceptance criteria:** *(preserved verbatim from v2.1 — all 8 criteria; the 6-seam-count claim at #1 holds per the audit's verification that spec §10 enumerates exactly §10.1–§10.6)*
1. Manifest enumerates exactly 6 substrate seam exports matching spec §10.1 through §10.6 verbatim.
2. Each `carrier_units` cites ≥1 IS-plan unit; every cited carrier resolves to a unit in U-IS-01 through U-IS-16.
3. Each `consuming_axes` matches spec §10.X "Consuming axes" column verbatim.
4. Each `spec_citation` is of the form `C-IS-10 §10.X` where X ∈ {1, 2, 3, 4, 5, 6}.
5. Manifest introduces NO executable behavior — declarative records only.
6. F2-12 carry-forward note preserved verbatim at IDEMPOTENCY_KEY_JOIN_EXPORT composition reference.
7. ADR body-citation versions: F1 v1.2, F2 v1.2, F3 v1.1, D1 v1.1, D2 v1.1, D3 v1.2, D4 v1.1, D5 v1.3, D6 v1.1 (latest filed per Workflow v1.6 §7).
8. Per OD-S1-3.A: consumer-axis dependency declarations NOT authored here; Session 5 retroactive verification.

**Tests:** *(preserved verbatim from v2.1)*
- `test_substrate_seam_exports_completeness`, `test_carrier_units_resolve`, `test_carrier_units_cover_export_surface`, `test_consuming_axes_match_spec`, `test_spec_citation_stable_anchor`, `test_f2_12_carry_forward_preserved`, `test_adr_body_citation_versions_aligned`, `test_manifest_no_executable_behavior`.

**Rollback boundary:** Revert substrate seam exports manifest. Consumer-axis plans (Sessions 2–4) lose stable citation target; Session 5 cross-axis composition cannot verify consumer-axis declarations against IS export surface.

> **Verdict note.** U-IS-17 is the audit's single **CONFORM** unit — an authority-chain-determinate plan-internal fix (no operator decision). The `UnitId` carrier exists (U-CORE-01, landed via R1); R2 simply cites it. The latent C-IS-10 11-vs-6 spec-internal phrasing note (audit §4.1 Class-1 informational) is **NOT** a plan defect and is **NOT** touched by R2 — it is logged for an eventual IS-spec pass.

---

## §6 Coverage matrix + dependency-graph delta

### §6.1 Coverage matrix delta

**None.** R2 changes no contract → unit coverage. Every revised unit still implements the same C-IS-NN contract(s) it implemented at v2.1 (U-IS-02 → C-IS-01 §1; U-IS-05 → C-IS-03 §3; U-IS-06 → C-IS-04 §4; U-IS-12 → C-IS-07 §7.2/§7.3; U-IS-14 → C-IS-08 §8.2/§8.4; U-IS-17 → C-IS-10). The `harness-core` carriers (`DeploymentSurface`, `WorkloadClass`, `WorkflowEvent`, `UnitId`) are covered by **U-CORE-01 / U-CP-00 in their own plans** (`Implementation_Plan_Harness_Core_v1_0.md` §4; CP plan §2.0) — the IS plan's coverage matrix does **not** acquire rows for them. The IS plan's 10-contract × 17-unit grid is preserved verbatim from v2.1/v2.2.

### §6.2 Dependency-graph delta

New **inbound** edges only (the IS plan adds no node — the carriers live in `harness-core`/CP):

| Unit | New edge(s) | Carrier / target |
|---|---|---|
| U-IS-02 | `[U-CP-00]`, `[U-CORE-01 (cross-axis: core)]` | `WorkloadClass`, `DeploymentSurface` |
| U-IS-05 | `[U-CP-00]`, `[U-CORE-01 (cross-axis: core)]` | `WorkloadClass`, `DeploymentSurface` |
| U-IS-06 | `[U-CORE-01 (cross-axis: core)]` (R2 default — for `ContractID`; see §5 note (i) / Q-R2-1) | `ContractID` |
| U-IS-12 | `[U-CP-00]` | `WorkloadClass` |
| U-IS-14 | `[U-CORE-01 (cross-axis: core)]` | `WorkflowEvent` |
| U-IS-17 | `[U-CORE-01 (cross-axis: core)]` | `UnitId` |

**Acyclic invariant — holds.** `U-CORE-01` and `U-CP-00` are both Level-0 source nodes (`Depends on: (none)`) residing in `harness-core` / CP. The IS units add **inbound-only** edges to them. A source node receiving inbound edges cannot create a cycle (R1 §5.2). The IS plan's within-axis DAG (17 nodes, 6 levels per v2.1 §3.1, the Kahn proof) is unchanged at the within-axis edge set; the new edges point *out of the IS axis into already-landed Level-0 carriers*, adding no IS-internal edge. The aggregate graph (IS ∪ harness-core ∪ CP) remains a DAG: `harness-core`/`U-CP-00` → IS is the topological direction (CXA §2.2: `harness-core` anchors, IS < AS < CP < OD). **No re-leveling of the IS within-axis topology is required.**

The IS audit's observation "the graph is acyclic but **incomplete** at the cross-axis-input boundary" is closed by R2: the previously-missing carrier nodes are now declared (R1 / CP plan) and the IS units declare the inbound edges.

### §6.3 New auxiliary-type audit (audit §4A.4 recommendation)

The IS audit recommended the IS plan acquire an explicit auxiliary-type audit (the AS §5.4.1-equivalent the IS plan lacks) "so the gap closes structurally". R2 discharges the *materializability* content of that recommendation via §1 (the carrier resolution table is the per-type audit). A standing recommendation: the v2.3 IS plan should carry §1 of this proposal as a new plan section (`§5 Auxiliary-type carrier audit`) so future revisions inherit the structural check. Logged as Q-R2-4 (§7) — a plan-structure question for the operator, not a materializability blocker.

---

## §7 Open questions for the operator

| ID | Question | Class | R2 default taken |
|---|---|---|---|
| **Q-R2-1** | U-IS-06 git-domain trio (`GitRepository` / `CommitRange` / `CommitId`): classify **(A)** stack-primitive of a git library (exclude — no carrier) or **(B)** harness abstraction (IS in-place carrier, IS-owned). §2.7.6 Class 2 (operator-decision) per the IS audit §4A.6 + carrier map "Open (git trio)". | §2.7.6 Class 2 | **(A)** — git-library primitives, excluded; framework-pull-disciplined (`CLAUDE.md` §3.2); `verify_deploy_atomicity` is offline/on-demand. U-IS-06 `Depends on` = `[U-IS-01, U-IS-04, U-CORE-01 (cross-axis: core)]` (the U-CORE-01 edge is for `ContractID`). If operator rules **(B)**, add an IS-internal git-type carrier declaration to U-IS-06's Signatures block (no `Depends on` change — IS-internal). |
| **Q-R2-2** | Cosmetic: should the IS plan unify the *parameter/field name* (`workflow_class` at U-IS-02/05 vs `workload_class` at U-IS-12) as well as the type name? | non-materiality (verbatim-pass item) | No — R2 unifies only the **type name** (`WorkflowClass` → `WorkloadClass`); parameter names are spec-prose-derived and left as-is. Operator may direct a follow-on cosmetic unification. |
| **Q-R2-3** | U-IS-04 is landed-clean with an inline/local `ContractID`; U-CORE-01 now declares a `ContractID` alias. Leave U-IS-04 untouched (R2 default per §0.4), or re-point its `ContractID` to U-CORE-01 in a future pass? | §2.7.6 Class 3 (informational) | Leave U-IS-04 untouched at R2 (not a FORK unit; task scopes R2 away from landed-clean re-litigation). Logged so the U-IS-04-local vs U-CORE-01 `ContractID` divergence is on record. |
| **Q-R2-4** | Should the v2.3 IS plan carry §1 of this proposal as a permanent new plan section (`Auxiliary-type carrier audit`), per the IS audit §4A.4 structural-closure recommendation? | plan-structure | Recommend yes — it closes the audit's "no auxiliary-type audit at all" structural gap. Operator confirms at v2.3 emission. |

**No Class-1 fork.** R2 surfaces no Class-1 (halt-execution) fork. The IS audit's two Class-1-halt candidates (the M-1-IS cluster and `WorkflowEvent`) were both lifted by T2 (FACTOR-OUT, decided — §0.3). Q-R2-1 is the only Class-2 item; it is determinate-once-classified and does not block the other 5 revised units. The U-IS-02 retrospective (§4) is Class-3 informational.

---

## §8 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/revision_R2_is_plan.md` |
| Role | `implementation-planner`, revision-pass sub-mode (SKILL.md §8) |
| Authored | 2026-05-15, Phase 7 sub-phase 7b — revision pass R2 of the R1–R5 materializability-conformance series |
| Inputs | `.harness/materializability_audit_is_plan.md` (Q4 IS audit); `.harness/shared_type_carrier_map.md` (T1); `.harness/xal3_resolution_recommendations.md` (T2); `.harness/revision_R1_harness_core.md` §3.1 + §4; `design-substrate/Implementation_Plan_Harness_Core_v1_0.md` (U-CORE-01); `design-substrate/Implementation_Plan_Information_Substrate_v2_2.md` + `_v2_1.md` (the canonical unit bodies); `design-substrate/Spec_Information_Substrate_v1.md` §1 (workflow-class / deployment-surface prose commitment) |
| Scope | IS plan v2.2 → v2.3 materializability-conformance amendment: M-1-IS resolution (U-IS-02/05/12/14), `UnitId` carrier (U-IS-17), `WorkflowClass`→`WorkloadClass` spelling unification, U-IS-02 landed-source retrospective (AI-R2-1). 6 revised unit bodies; 11 units preserved verbatim. |
| Status | `Proposed` — pending operator ratification of Q-R2-1 through Q-R2-4. On ratification: `Implementation_Plan_Information_Substrate_v2_3.md` carries the §5 bodies + §6 graph delta; AI-R2-1 (U-IS-02 source re-point) is a separate R2-application action. |
| Successor | v2.3 IS plan; R3 (AS) / R4 (CP) / R5 (OD) per-axis passes continue the series |
| HARD WALL attested | This pass wrote only `.harness/revision_R2_is_plan.md`. No `design-substrate/`, `CLAUDE.md`, plan, spec, audit, carrier-map, or source edit. No git commit. |

*End of Revision R2 — Information-Substrate Plan Materializability Conformance. The operator ratifies. R2 is the second of the R1–R5 series; R3 (AS) follows.*
