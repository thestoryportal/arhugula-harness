# Implementation Plan — Information Substrate (IS axis) — v2.3

*Revision-pass amendment to v2.2. Authored at Phase 7 sub-phase 7b — Revision Pass R2 (IS-axis materializability conformance). Skill: `implementation-planner` SKILL.md §8 revision-pass sub-mode.*

**Status:** Proposed

---

## §0 Change-note

### §0.1 Predecessor

`Implementation_Plan_Information_Substrate_v2_2.md` (v2.2 — F3-02 IS-side closure record; itself a change-note-only delta over `Implementation_Plan_Information_Substrate_v2_1.md`, the v2.1 baseline canonical at Phase 6 close).

v2.2 is a change-note-only delta — all 17 unit bodies carry forward verbatim from v2.1. R2 therefore operates against the **v2.1 unit bodies** (the canonical bodies v2.2 preserves by reference) and emits v2.3.

### §0.2 Revision scope (v2.2 → v2.3)

v2.3 absorbs **Revision Pass R2** — the IS-axis materializability-conformance amendment (second of the R1–R5 carrier-map absorption series; R1 = `harness-core` foundation, landed as `Implementation_Plan_Harness_Core_v1_0.md`). R2 absorbs three ratified / standing upstream inputs:

- `.harness/materializability_audit_is_plan.md` — the IS-axis systemic materializability audit. Verdict tally: **11 CLEARED · 1 CONFORM (U-IS-17) · 5 FORK (U-IS-02, U-IS-05, U-IS-06, U-IS-12, U-IS-14)**. Systemic pattern **M-1-IS**: cross-axis types consumed at IS signature positions with no carrier.
- `.harness/shared_type_carrier_map.md` (Pipeline Pass T1) — the ratified carrier map. Places `WorkloadClass` (= IS `WorkflowClass`) at the landed `harness-core` U-CP-00 carrier; `DeploymentSurface` and the identity-alias module at the `harness-core` U-CORE-01 carrier.
- `.harness/xal3_resolution_recommendations.md` (Pipeline Pass T2) — the X-AL-3 verdicts. All M-1-IS types (`WorkflowEvent` / `WorkflowClass` / `DeploymentSurface`) are **FACTOR-OUT, decided**: the IS spec commits each concept in prose, so declaring a `harness-core` carrier is faithful operationalization, **not** a design extension. The two Class-1 halts the IS audit flagged are lifted — IS importing `harness-core` is a shared-substrate import, not an outbound CXA edge, so the CXA §2.4 "IS = 0 outbound edges" invariant is untouched. **Zero IS-spec back-flow is required by R2; v2.3 introduces no IS-spec / CXA / ADD revision.**

R1 (the `harness-core` carrier) is the prerequisite and is already landed; v2.3 cites the U-CORE-01 / U-CP-00 carriers.

| In scope at v2.3 | Out of scope |
|---|---|
| Revised bodies for the 5 FORK units + 1 CONFORM unit: **U-IS-02, U-IS-05, U-IS-06, U-IS-12, U-IS-14, U-IS-17** (§2 below) | The 11 CLEARED units — preserved verbatim (§0.4) |
| `[U-CORE-01 (cross-axis: core)]` / `[U-CP-00]` dependency edges per the R1 hand-off (§3 delta) | U-CORE-01 itself — R1 scope, landed |
| `WorkflowClass` → `WorkloadClass` IS-internal type-spelling unification | Source-code edits (HARD WALL — AI-R2-1 §0.6 is a deferred coding-lane hand-off) |
| Coverage-matrix + dependency-graph delta (§3, §4) | U-IS-01 / U-IS-04 — landed-clean, not FORK units, deliberately untouched (§0.4) |
| New permanent §5 Auxiliary-type carrier audit section (per Q-R2-4) | — |

### §0.3 Operator ratification decisions folded into v2.3 (decided 2026-05-15)

The R2 proposal (`.harness/revision_R2_is_plan.md`) surfaced four open questions (proposal §7). The operator ratified as follows; v2.3 is authored to these decisions.

| ID | Question | Operator decision | Where applied |
|---|---|---|---|
| **Q-R2-1** | U-IS-06 git-domain trio (`GitRepository` / `CommitRange` / `CommitId`): classify **(A)** stack-primitive of a git library (exclude — no carrier) or **(B)** harness abstraction (IS-internal carrier). | **OVERRIDE of R2 default.** The trio are **IS-internal harness abstractions** — option (B). They are **declared as IS-internal types in U-IS-06's own Signatures block** (U-IS-06 is the git-tier sub-role unit — the natural carrier). Rationale: the harness performs git operations by shelling out to the `git` CLI (Meta-Architecture shell-out substitution), so no committed Python git library supplies these types; the harness defines its own thin git-domain types. NOT excluded stack-primitives. | U-IS-06 revised body (§2) — Signatures block declares the trio; Note (iii); §5 audit row |
| **Q-R2-2** | Cosmetic: should the IS plan unify the *parameter/field name* (`workflow_class` at U-IS-02/05 vs `workload_class` at U-IS-12) as well as the type name? | **R2 default accepted.** No — v2.3 unifies only the **type name** (`WorkflowClass` → `WorkloadClass`); parameter names are spec-prose-derived and left as-is. | U-IS-02 / U-IS-05 revised bodies — type name only |
| **Q-R2-3** | U-IS-04 is landed-clean with an inline/local `ContractID`; U-CORE-01 now declares a `ContractID` alias. Re-point U-IS-04's `ContractID`? | **R2 default accepted — deferred.** Leave U-IS-04 untouched at v2.3 (not a FORK unit; R2 scoped away from landed-clean re-litigation). The U-IS-04-local vs U-CORE-01 `ContractID` divergence is recorded as a future item; a later pass revising U-IS-04 for an unrelated reason re-points then. | §0.4 (non-touch record); future-item note below |
| **Q-R2-4** | Should v2.3 carry the carrier-resolution table as a permanent new plan section (`Auxiliary-type carrier audit`)? | **R2 default accepted — YES.** v2.3 carries a permanent §5 Auxiliary-type carrier audit section — the structural fix the audits recommended (the AS §5.4.1-equivalent the IS plan lacked). Future revisions inherit the structural check. | New §5 (this file) |

**Q-R2-3 future-item note.** `ContractID` now has a `harness-core` carrier (U-CORE-01, R1). U-IS-04's landed `ContractID` is local-or-inline (audit classified it an M-1 *inline tail*, CLEARED). The divergence is on record. **Deferred coding-lane / planning item:** if any future pass revises U-IS-04, re-point its `ContractID` to the U-CORE-01 carrier at that time. v2.3 takes no action on U-IS-04.

### §0.4 Sections preserved verbatim from v2.1/v2.2

| Section | Status at v2.3 |
|---|---|
| §0 (v2.2 change-note) | Superseded by this §0 (the v2.2 §0.7 F3-02 closure record is retained by reference) |
| §1 Spec inventory | Preserved verbatim from v2.1 §1 |
| §2 — U-IS-01, U-IS-03, U-IS-04, U-IS-07, U-IS-08, U-IS-09, U-IS-10, U-IS-11, U-IS-13, U-IS-15, U-IS-16 | **Preserved verbatim from v2.1 §2** — the 11 CLEARED units; `[preserved verbatim]` pointers in §2 below |
| §2 — U-IS-02, U-IS-05, U-IS-06, U-IS-12, U-IS-14, U-IS-17 | **Revised at v2.3** — full bodies in §2 below |
| §3 Dependency graph | Revised at the delta nodes/edges only (§3 below); all other within-axis edges + the acyclicity proof preserved verbatim from v2.1 §3 |
| §4 Coverage matrix | Preserved verbatim from v2.1 §4 — no contract → unit coverage change (§4 delta below) |

**Explicit non-touch of landed-clean units.** U-IS-01 (`ResidenceContract` undeclared) and U-IS-04 (`ContractID` undeclared) were audited **CLEARED** — the audit classified `ResidenceContract`/`ContractID` as M-1 *inline tails*, not blocking. Both units are **landed** (`harness-is/CLAUDE.md` §3 names U-IS-01/04 as L0/L1 anchors; MEMORY records the 7b operational-minimum landing). **v2.3 deliberately does NOT revise U-IS-01 or U-IS-04.** This is a real choice, surfaced not buried: (a) the audit did not fork either unit, (b) R2 is scoped to FORK/CONFORM units + the R1 hand-off with no re-litigation of landed-clean units, (c) `ResidenceContract`/`ContractID` were inline-materializable by the audit's own classification — a landed inline declaration is materializability-clean. The U-IS-04 `ContractID` divergence is logged as Q-R2-3 (deferred) so it is on the record, not silently absorbed.

### §0.5 Authority-chain note — the X-AL-3 risk was discharged upstream

The IS audit's M-1-IS finding listed reading (b) "X-AL-3 design extension → IS-spec back-flow" as a live possibility. **T2 closed that reading.** The IS spec §1 commits the concepts directly in prose: a path identifier is *workflow-canonical* if stable across all runs of the same workflow class; MAY vary across workflow classes; MAY vary across deployment surfaces (canonical-path declaration commits only that *some* stable path exists per (workflow class, deployment surface) cell). The IS spec C-IS-04 §4 is titled "workflow-class-tunable shadow-Git checkpointing". The concepts are spec-committed; only the *declaration site* was missing. T2 verdict: FACTOR-OUT, decided. **v2.3 introduces no IS-spec revision, no CXA revision, no ADD revision.** `implementation-planner` SKILL.md §2 consequence 1 (the planner never extends a spec) is satisfied — v2.3 cites pre-existing carriers, it does not invent commitments.

**Q-R2-1 git-trio note on this point.** The Q-R2-1 operator decision declares `GitRepository`/`CommitRange`/`CommitId` as IS-internal types in U-IS-06's own Signatures block. This is **not** a spec extension either: IS spec C-IS-04 §4 commits the deploy-event verification surface that operates over git history; a thin IS-internal git-domain type set is faithful operationalization of an IS-axis-owned surface (T1 disposition-2 classed the trio IS-internal — no other axis consumes them). No `harness-core` carrier and no IS-spec revision is required.

### §0.6 Action-item note — U-IS-02 landed-source retrospective (AI-R2-1) — DEFERRED, NOT PERFORMED

**U-IS-02 is LANDED** (`harness-is/CLAUDE.md` §3 L1 anchor; MEMORY `phase-7-bootstrap-status` — "7b: 12/12 operational-minimum units landed 2026-05-15"). Its `resolve_path` signature consumed `WorkflowClass` and `DeploymentSurface` **when neither type had a declaring carrier**. The landed coding lane therefore did one of three non-conformant things at landing time: (1) inlined a local `WorkflowClass`/`DeploymentSurface` enum inside the U-IS-02 source module, or (2) used a bare `str`/`Any` placeholder at the parameter positions, or (3) imported from a sibling unit's declaration. All three are non-conformant once U-CORE-01 / U-CP-00 are the canonical carriers.

> **AI-R2-1 — MANDATORY deferred coding-lane action (source-level).** Before v2.3 is considered **fully consumed**, the landed `harness-is/` path-resolver source MUST be inspected and re-pointed:
> 1. **Inspect** the landed U-IS-02 implementation source (under `harness-is/`) — the `path-resolver` module — and determine which of the three non-conformant shapes is present at the `workflow_class` / `deployment_surface` parameter positions.
> 2. **Re-point** the parameter types to import from `harness-core`: `WorkloadClass` from the U-CP-00 module, `DeploymentSurface` from the U-CORE-01 module. Delete any inlined local enum declaration.
> 3. **Verify byte-exact agreement**: if the landed source inlined a local enum, its members and string values MUST match the U-CORE-01 `DeploymentSurface` (3 values: `local-development | self-hosted-server | managed-cloud`) and the U-CP-00 `WorkloadClass` byte-exact. If the landed shape diverges, the landed U-IS-02 must be revised to conform — the carrier shape is canonical, not the landed inline.
> 4. **Record** the re-point in the Phase 7 execution log as the discharge of this retrospective.
>
> **Status at v2.3: FLAGGED, NOT PERFORMED.** v2.3 (this plan file) revises only the U-IS-02 *plan unit body* (carrier edges + spelling unification). The landed-source re-point is a separate deferred coding-lane action under the HARD WALL — v2.3 surfaces AI-R2-1 so the re-check is not missed. The plan-body revision and the source re-point are two halves of one reconciliation; **both** are required for U-IS-02 to be fully conformant. The §2.7.6 fork class is **Class 3 (informational)** — this is a carrier-ordering artifact (the unit landed before its carrier existed), not a design defect; not silent absorption (`CLAUDE.md` §4.3), because AI-R2-1 makes the reconciliation explicit and auditable.

### §0.7 Status posture

`Status: Proposed` — preserved per `implementation-planner` SKILL.md §8 until any P6-CK-analog re-clearance.

---

## §1 Spec inventory

[Preserved verbatim from `Implementation_Plan_Information_Substrate_v2_1.md` §1 — C-IS-01 through C-IS-10 mapping; §1.2 cluster decomposition (17 units across 6 clusters); §1.3 substrate-version citation alignment (IS spec v1.2; ADR latest-version body-citations). Unchanged at v2.3.]

---

## §2 Atomic-unit decomposition

The 11 CLEARED units are preserved verbatim from v2.1 §2 (delta-file convention per v2.2 §0.3); `[preserved verbatim]` pointers below. The 6 revised units (U-IS-02, U-IS-05, U-IS-06, U-IS-12, U-IS-14, U-IS-17) carry full revised bodies.

### §2.1 Preserved-verbatim units (11 CLEARED)

| Unit | Status |
|---|---|
| U-IS-01 — Declare `PathClass` enum + filesystem-path classification | `[preserved verbatim from Implementation_Plan_Information_Substrate_v2_1.md §2]` |
| U-IS-03 — Implement substrate-residence rule enforcement | `[preserved verbatim from Implementation_Plan_Information_Substrate_v2_1.md §2]` |
| U-IS-04 — Declare `GitTierSubRole` enum | `[preserved verbatim from Implementation_Plan_Information_Substrate_v2_1.md §2]` |
| U-IS-07 — Declare `StateLedgerEntry` 6-field primitive | `[preserved verbatim from Implementation_Plan_Information_Substrate_v2_1.md §2]` |
| U-IS-08 — Implement idempotency-key construction + join | `[preserved verbatim from Implementation_Plan_Information_Substrate_v2_1.md §2]` |
| U-IS-09 — Implement hash-chain construction discipline | `[preserved verbatim from Implementation_Plan_Information_Substrate_v2_1.md §2]` |
| U-IS-10 — Implement content-addressed index | `[preserved verbatim from Implementation_Plan_Information_Substrate_v2_1.md §2]` |
| U-IS-11 — Implement semantic cache | `[preserved verbatim from Implementation_Plan_Information_Substrate_v2_1.md §2]` |
| U-IS-13 — Declare `WorkloadManifestOptIns` + `CheckpointCadence` | `[preserved verbatim from Implementation_Plan_Information_Substrate_v2_1.md §2]` |
| U-IS-15 — Implement shadow-Git rollback primitive | `[preserved verbatim from Implementation_Plan_Information_Substrate_v2_1.md §2]` |
| U-IS-16 — Implement state-ledger write path | `[preserved verbatim from Implementation_Plan_Information_Substrate_v2_1.md §2]` |

*Unit titles above are navigational pointers; the canonical bodies are the verbatim v2.1 §2 bodies. No content change at v2.3.*

### §2.2 Revised units (6)

---

#### U-IS-02 — Implement path-resolver primitive  *(REVISED — R2)*

**Implements:** [C-IS-01 §1]

**Depends on:** [U-IS-01, U-CP-00, U-CORE-01 (cross-axis: core)]

> *R2 delta:* added `U-CP-00` (carrier of `WorkloadClass`) and `U-CORE-01 (cross-axis: core)` (carrier of `DeploymentSurface`). The `U-IS-01` edge is preserved.

**Inputs:** `PathClass` enum + metadata from U-IS-01; `WorkloadClass` from `harness-core` (U-CP-00); `DeploymentSurface` from `harness-core` (U-CORE-01); implementation-time configuration supplying canonical path strings per (workload_class, deployment_surface) cell.

> *R2 delta:* "workflow class identifier" / "deployment surface identifier" (prose placeholders for undeclared types in the v2.1 body) replaced with the explicit `harness-core` carrier citations.

**Files affected:** Path-resolver implementation (logical name: `path-resolver`); path-binding configuration loader (logical name: `path-binding-loader`).

**Signatures:**
```
resolve_path(
  path_class          : PathClass,
  workflow_class      : WorkloadClass,        // harness-core, U-CP-00 (type spelling unified from WorkflowClass per R2)
  deployment_surface  : DeploymentSurface     // harness-core, U-CORE-01
) -> Path
```

> *R2 delta:* parameter type `WorkflowClass` → `WorkloadClass` (type-name unification — see §5; the parameter *name* `workflow_class` is spec-prose-derived and left as-is per Q-R2-2). `deployment_surface` type re-pointed to the U-CORE-01 carrier.

**Acceptance criteria:** *(preserved verbatim from v2.1 — the criteria reference the concepts "workflow class" / "deployment surface" as spec prose, not the type identifier)*
1. Repeated calls within a single run on the same triple return identical `Path` values (stability invariant within run).
2. Same `(path_class, workflow_class, deployment_surface)` triple across run boundaries returns identical `Path` values (workflow-canonical per spec §1).
3. Same `path_class` and `deployment_surface` but differing `workflow_class` MAY return differing paths without violating any contract (workflow-class-varying flex).
4. Resolver does not hard-code path strings; all paths derive from path-binding configuration source.
5. Resolver does not produce paths violating C-IS-02 substrate-residence rule (cross-unit invariant verified once U-IS-03 lands).

**Tests:** *(preserved verbatim from v2.1)*
- `test_resolve_path_stability_within_run`; `test_resolve_path_workflow_canonical_across_runs`; `test_resolve_path_workflow_class_variance_permitted`; `test_resolve_path_no_hardcoded_paths`.

**Rollback boundary:** Revert path-resolver + path-binding loader. Downstream callers fail at runtime.

> **Landed-unit retrospective (§0.6 / AI-R2-1).** U-IS-02 is a landed L1 anchor; it consumed `WorkflowClass`/`DeploymentSurface` before their carriers existed. The deferred coding-lane action AI-R2-1 MUST re-check and re-point the landed `harness-is/` path-resolver source per §0.6 before v2.3 is fully consumed. **Flagged, not performed at v2.3.**

---

#### U-IS-05 — Implement JSONL event ledger file lifecycle  *(REVISED — R2)*

**Implements:** [C-IS-03 §3 (JSONL event ledger sub-role row)]

**Depends on:** [U-IS-01, U-IS-02, U-IS-04, U-CP-00, U-CORE-01 (cross-axis: core)]

> *R2 delta:* added `U-CP-00` (`WorkloadClass`) and `U-CORE-01 (cross-axis: core)` (`DeploymentSurface`). The three within-axis edges are preserved.

**Inputs:** `PathClass.STATE_LEDGER` (U-IS-01); `resolve_path` (U-IS-02); `GitTierSubRole.JSONL_EVENT_LEDGER` (U-IS-04); `WorkloadClass` from `harness-core` (U-CP-00); `DeploymentSurface` from `harness-core` (U-CORE-01); workflow open / resume signal.

> *R2 delta:* added the two `harness-core` carrier citations (consumed at the `initialize_jsonl_event_ledger` signature).

**Files affected:** JSONL event ledger lifecycle (logical name: `jsonl-event-ledger-lifecycle`).

**Scope.** File existence + structural validation at workflow open / resume. Does NOT write or read entries (C-IS-07 territory) or compute hashes (C-IS-06 territory).

**Signatures:**
```
initialize_jsonl_event_ledger(
  workflow_class       : WorkloadClass,        // harness-core, U-CP-00 (type spelling unified from WorkflowClass per R2)
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

> **Note.** U-IS-05 is FORK-blocked in the pipeline and (per the IS audit) NOT landed — no retrospective re-check applies; it materializes fresh against this v2.3 body.

---

#### U-IS-06 — Declare atomic deploy-event composition contract + verification primitive  *(REVISED — R2)*

**Implements:** [C-IS-04 §4]

**Depends on:** [U-IS-01, U-IS-04, U-CORE-01 (cross-axis: core)]

> *R2 delta:* added `U-CORE-01 (cross-axis: core)` — the carrier of `ContractID` (per Note (i) below). The two within-axis edges are preserved. **The git-domain trio (Q-R2-1) adds no `Depends on` edge** — per the operator's Q-R2-1 decision the trio are IS-internal types declared in this unit's own Signatures block (in-unit; no inbound edge).

**Inputs:** IS spec v1.2 §4 4-class deploy-unit composition; §4 atomicity contract; §4 verification surface; `PathClass` (U-IS-01); `GitTierSubRole.VERSIONING` + `GitTierSubRole.STATE_LEDGER_VIA_COMMIT_STREAM` (U-IS-04); `ContractID` from `harness-core` (U-CORE-01 — see Note (i)); the IS-internal git-domain types `GitRepository` / `CommitRange` / `CommitId` declared in this unit (see Note (iii)).

> *R2 delta:* prose placeholders for the undeclared types replaced with explicit citations — `ContractID` → U-CORE-01 carrier; the git-domain trio → IS-internal in-unit declaration per the Q-R2-1 operator decision.

**Files affected:** Atomic deploy-event composition declaration (logical name: `atomic-deploy-event-contract`); deploy-event verification test suite (logical name: `atomic-deploy-event-verification`).

**Signatures:** *(structure preserved verbatim from v2.1; the git-domain trio is declared in-unit per Q-R2-1; the `ContractID` consumption is annotated)*
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
  composes_with           : Set[ContractID]            // ContractID — harness-core, U-CORE-01 (see Note (i))
}

enum AtomicityProperty { ALL_OR_NOTHING_PER_COMMIT }
enum ObservabilityProperty { SINGLE_VERSION_OBSERVABILITY }

// --- IS-internal git-domain types (Q-R2-1 operator decision, 2026-05-15) ---
// These three types are IS-internal harness abstractions, NOT excluded
// stack-primitives and NOT harness-core carriers. The harness performs git
// operations by shelling out to the `git` CLI (Meta-Architecture shell-out
// substitution); no committed Python git library supplies these types, so the
// IS axis defines its own thin git-domain types. They are IS-axis-owned
// (T1 disposition-2: IS-internal — no other axis consumes them) and are
// declared here, in U-IS-06's own Signatures block, this being the git-tier
// sub-role unit and therefore their natural carrier. See Note (iii).
record GitRepository {
  repository_root  : Path                              // C-IS-01 PathClass-classified repo root
}

record CommitRange {
  from_commit  : CommitId
  to_commit    : CommitId
}

record CommitId {
  sha  : string                                        // git object SHA, opaque newtype
}
// --- end IS-internal git-domain types ---

verify_deploy_atomicity(
  git_repository  : GitRepository,                     // IS-internal, U-IS-06-declared (Q-R2-1)
  commit_range    : CommitRange                        // IS-internal, U-IS-06-declared (Q-R2-1)
) -> DeployAtomicityVerificationReport

record DeployAtomicityVerificationReport {
  commits_inspected   : Integer
  violations          : List[DeployAtomicityViolation]
  bisection_isolated  : bool
}

record DeployAtomicityViolation {
  violation_type  : ViolationType
  commit_ids      : List[CommitId]                     // IS-internal, U-IS-06-declared (Q-R2-1)
  description     : string
}

enum ViolationType { SPLIT_DEPLOY, MISSING_COMMIT_STREAM_ENTRY }
```

**Note (i) — `ContractID`.** `DeployEventComposition.composes_with : Set[ContractID]` consumes `ContractID`. The IS audit classified `ContractID` as an M-1 *inline tail* (CLEARED). R1's U-CORE-01 declares `ContractID` in the identity-alias module. **R2 re-points `ContractID` to the U-CORE-01 carrier** — unlike U-IS-04 (landed, untouched per §0.4 / Q-R2-3), U-IS-06 is being revised anyway (it is a FORK unit), so re-pointing `ContractID` here costs nothing and is the materializability-clean choice. The `[U-CORE-01 (cross-axis: core)]` edge in U-IS-06's `Depends on` is for `ContractID`. This decision is independent of Q-R2-1.

**Note (ii) — in-unit declared types.** `DeployArtifactClass` / `DeployEventComposition` / `AtomicityProperty` / `ObservabilityProperty` / `DeployAtomicityVerificationReport` / `DeployAtomicityViolation` / `ViolationType` are all U-IS-06-declared (in-unit) — materializability-clean, unchanged from v2.1.

**Note (iii) — git-domain trio (`GitRepository` / `CommitRange` / `CommitId`) — Q-R2-1 operator decision, 2026-05-15.** The R2 proposal carried the trio as an open question with a *default* of classification (A) — "git-library stack-primitives, excluded". **The operator OVERRODE that default.** The ratified classification is **(B) — IS-internal harness abstractions.** The trio are declared as IS-internal types in U-IS-06's own Signatures block above. Rationale recorded: the harness performs git operations by **shelling out to the `git` CLI** (Meta-Architecture shell-out substitution category), so no committed Python git library is in the stack to supply these types; the harness therefore defines its own thin git-domain types. The trio are **NOT** excluded stack-primitives (the R2 default reading) and **NOT** `harness-core` carriers — they are IS-axis-owned (T1 disposition-2: IS-internal; no other axis consumes them), and U-IS-06 — the git-tier sub-role unit — is their natural carrier. Consequence: U-IS-06's `Depends on` stays `[U-IS-01, U-IS-04, U-CORE-01 (cross-axis: core)]` (the `U-CORE-01` edge is for `ContractID` only); the trio add no inbound edge because they are declared in-unit. This decision introduces no IS-spec revision (see §0.5) and no framework pull — git operations remain a shell-out substitution per `CLAUDE.md` §3.2 framework-pull discipline.

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

#### U-IS-12 — Implement C2-pole selective bounded read contract via NavigationPrimitive interface  *(REVISED — R2)*

**Implements:** [C-IS-07 §7.2, §7.3]

**Depends on:** [U-IS-05, U-IS-07, U-CP-00]

> *R2 delta:* added `U-CP-00` (carrier of `WorkloadClass`, consumed at `BoundedWindow.workload_class`). The two within-axis edges are preserved.

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

> *R2 delta:* `BoundedWindow.workload_class` type re-pointed to the U-CP-00 `harness-core` carrier. The field already used the canonical `WorkloadClass` spelling — no spelling change (see §5). `NavigationPrimitive` / `NavigationQuery` / `PositionRange` / `BoundedWindow` / `ReadResult` are U-IS-12-declared (in-unit) — unchanged. `Identifier` is U-IS-07-declared `opaque` (in-cone) — unchanged.

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

#### U-IS-14 — Implement shadow-Git checkpoint primitive (cadence-driven snapshot creation)  *(REVISED — R2)*

**Implements:** [C-IS-08 §8.2, §8.4]

**Depends on:** [U-IS-04, U-IS-13, U-CORE-01 (cross-axis: core)]

> *R2 delta:* added `U-CORE-01 (cross-axis: core)` (carrier of `WorkflowEvent` + `WorkflowEventClass`, per R1 Q-R1-2 ratification). The two within-axis edges are preserved.

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

#### U-IS-17 — Declare substrate seam exports manifest  *(REVISED — R2 CONFORM)*

**Implements:** [C-IS-10 §10.1, §10.2, §10.3, §10.4, §10.5, §10.6]

**Depends on:** [U-IS-01, U-IS-02, U-IS-05, U-IS-07, U-IS-08, U-IS-09, U-IS-10, U-IS-11, U-IS-12, U-IS-13, U-CORE-01 (cross-axis: core)]

> *R2 delta:* added `U-CORE-01 (cross-axis: core)` (carrier of `UnitId`, consumed at `SubstrateSeamExport.carrier_units : List[UnitId]`). The 10 within-axis carrier edges are preserved verbatim.

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

**Acceptance criteria:** *(preserved verbatim from v2.1 — all 8 criteria)*
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

> **Verdict note.** U-IS-17 is the audit's single **CONFORM** unit — an authority-chain-determinate plan-internal fix (no operator decision). The `UnitId` carrier exists (U-CORE-01, landed via R1); R2 simply cites it. The latent C-IS-10 11-vs-6 spec-internal phrasing note (audit Class-1 informational) is **NOT** a plan defect and is **NOT** touched by R2 — it is logged for an eventual IS-spec pass.

---

## §3 Dependency graph

[Within-axis DAG topology, cluster ordering, acyclicity verification, and backref reconciliations preserved verbatim from `Implementation_Plan_Information_Substrate_v2_1.md` §3, except the delta nodes/edges below.]

### §3.1 Dependency-graph delta (R2)

New **inbound** edges only — the IS plan adds no node; the carriers `U-CORE-01` and `U-CP-00` physically reside in `harness-core` / CP and are declared in their own plans (`Implementation_Plan_Harness_Core_v1_0.md`; the CP plan).

| Unit | New edge(s) | Carrier / target | Type(s) carried |
|---|---|---|---|
| U-IS-02 | `[U-CP-00]`, `[U-CORE-01 (cross-axis: core)]` | `harness-core` (U-CP-00 / U-CORE-01) | `WorkloadClass`, `DeploymentSurface` |
| U-IS-05 | `[U-CP-00]`, `[U-CORE-01 (cross-axis: core)]` | `harness-core` (U-CP-00 / U-CORE-01) | `WorkloadClass`, `DeploymentSurface` |
| U-IS-06 | `[U-CORE-01 (cross-axis: core)]` | `harness-core` (U-CORE-01) | `ContractID` *(git trio adds no edge — IS-internal per Q-R2-1)* |
| U-IS-12 | `[U-CP-00]` | `harness-core` (U-CP-00) | `WorkloadClass` |
| U-IS-14 | `[U-CORE-01 (cross-axis: core)]` | `harness-core` (U-CORE-01) | `WorkflowEvent` |
| U-IS-17 | `[U-CORE-01 (cross-axis: core)]` | `harness-core` (U-CORE-01) | `UnitId` |

**Edge-form discipline.** Two forms, matching R1 verbatim:
- `[U-CORE-01 (cross-axis: core)]` — for U-CORE-01 imports. `harness-core` is shared substrate, not an axis; the `(cross-axis: core)` annotation makes the import explicit and reviewable per `implementation-planner` SKILL.md §7. This is an **import edge, not an outbound CXA edge** — per T2 it does not violate the CXA §2.4 "IS = 0 outbound" invariant.
- `[U-CP-00]` — for the `WorkloadClass` carrier. R1 chose the **unannotated** `[U-CP-00]` form (U-CP-00 is the landed carrier; R1 Q-R1-3 ratified the edge to `[U-CP-00]`, not folded into U-CORE-01). v2.3 follows R1 exactly — no third edge form is invented.

**Acyclic invariant — holds.** `U-CORE-01` and `U-CP-00` are both Level-0 source nodes (`Depends on: (none)`) residing in `harness-core` / CP. The IS units add **inbound-only** edges to them; a source node receiving inbound edges cannot create a cycle. The IS plan's within-axis DAG (17 nodes, levels per v2.1 §3, the Kahn proof) is unchanged at the within-axis edge set — the new edges point *out of the IS axis into already-landed Level-0 carriers*, adding no IS-internal edge. The aggregate graph (IS ∪ harness-core ∪ CP) remains a DAG: `harness-core`/`U-CP-00` → IS is the topological direction (CXA §2.2: `harness-core` anchors, IS < AS < CP < OD). **No re-leveling of the IS within-axis topology is required.** The Q-R2-1 git-trio decision adds **no** edge (the trio are IS-internal, in-unit at U-IS-06) — the within-axis DAG is wholly unaffected by it.

The IS audit's observation "the graph is acyclic but **incomplete** at the cross-axis-input boundary" is closed by R2: the previously-missing carrier nodes are now declared (R1 / CP plan) and the IS units declare the inbound edges.

---

## §4 Coverage matrix

[10-contract × 17-unit coverage grid preserved verbatim from `Implementation_Plan_Information_Substrate_v2_1.md` §4.]

### §4.1 Coverage-matrix delta (R2)

**None.** R2 changes no contract → unit coverage. Every revised unit still implements the same C-IS-NN contract(s) it implemented at v2.1:

| Unit | Contract(s) implemented — unchanged at v2.3 |
|---|---|
| U-IS-02 | C-IS-01 §1 |
| U-IS-05 | C-IS-03 §3 |
| U-IS-06 | C-IS-04 §4 |
| U-IS-12 | C-IS-07 §7.2, §7.3 |
| U-IS-14 | C-IS-08 §8.2, §8.4 |
| U-IS-17 | C-IS-10 §10.1–§10.6 |

The `harness-core` carriers (`DeploymentSurface`, `WorkloadClass`, `WorkflowEvent`, `UnitId`) are covered by **U-CORE-01 / U-CP-00 in their own plans** (`Implementation_Plan_Harness_Core_v1_0.md`; the CP plan) — the IS plan's coverage matrix does **not** acquire rows for them. The Q-R2-1 git-domain trio is covered by U-IS-06 itself (IS-internal in-unit declaration) — and C-IS-04 §4 is already a U-IS-06 coverage row, so no new row is created. The IS plan's 10-contract × 17-unit grid is preserved verbatim from v2.1/v2.2.

---

## §5 Auxiliary-type carrier audit  *(NEW — permanent plan section, per Q-R2-4)*

*This section is new at v2.3, added per the operator's ratification of Q-R2-4. The IS materializability audit recommended the IS plan acquire an explicit auxiliary-type audit (the AS §5.4.1-equivalent the IS plan lacked) "so the gap closes structurally". This section is permanent — future revision passes inherit and maintain it as the IS plan's standing materializability self-check.*

### §5.1 Purpose

Every type consumed at an IS-unit signature position that is **not** declared in that unit's own body must resolve to a declared carrier inside that unit's `Depends on` cone (a within-axis unit, a `harness-core` carrier, or an excluded stack-primitive). This section is the per-type ledger of that resolution. A new type introduced at any future IS-unit signature triggers a new row here.

### §5.2 Carrier resolution table

| Auxiliary type | Consuming IS unit(s) | Carrier / disposition | Carrier source | `Depends on` edge | Status |
|---|---|---|---|---|---|
| `WorkloadClass` (canonical spelling; was `WorkflowClass` at U-IS-02/05) | U-IS-02, U-IS-05, U-IS-12 | `harness-core` — **landed U-CP-00** | T1 carrier map disposition-1; R1 hand-off | `[U-CP-00]` | Resolved (R2) |
| `DeploymentSurface` | U-IS-02, U-IS-05 | `harness-core` — **U-CORE-01** (R1, landed) | T1 carrier map disposition-1 | `[U-CORE-01 (cross-axis: core)]` | Resolved (R2) |
| `WorkflowEvent` (+ `WorkflowEventClass`) | U-IS-14 | `harness-core` — **U-CORE-01** (R1, landed; Q-R1-2) | T2 resolution table (decided); R1 | `[U-CORE-01 (cross-axis: core)]` | Resolved (R2) |
| `UnitId` | U-IS-17 | `harness-core` — **U-CORE-01** (R1, landed; Q-R1-5 — plan-internal `str`-newtype alias) | T1 carrier map disposition-1 (identity-alias module); R1 | `[U-CORE-01 (cross-axis: core)]` | Resolved (R2) |
| `ContractID` | U-IS-06 (`composes_with`); U-IS-04 (landed, untouched) | `harness-core` — **U-CORE-01** for U-IS-06; U-IS-04's landed inline left in place | T1 carrier map disposition-1 (identity-alias module) | `[U-CORE-01 (cross-axis: core)]` at U-IS-06; **none** at U-IS-04 (Q-R2-3 deferred) | Resolved at U-IS-06 (R2); **U-IS-04 deferred — Q-R2-3** |
| `GitRepository`, `CommitRange`, `CommitId` | U-IS-06 | **IS-internal harness abstractions** — declared in U-IS-06's own Signatures block | Q-R2-1 operator decision (2026-05-15) — OVERRIDE of R2 default; T1 disposition-2 (IS-internal) | **none** — in-unit declaration, no inbound edge | Resolved (Q-R2-1) — IS-internal, in-unit |
| `ResidenceContract` | U-IS-01 (landed, CLEARED) | IS-inline at U-IS-01 (audit M-1 inline tail; landed) | T1 carrier map disposition-2 | n/a — U-IS-01 not revised at R2 | Out of scope (§0.4) — landed-clean inline |
| `PathClass`, `GitTierSubRole`, `StateLedgerEntry`, `Identifier`, `Timestamp`, `CheckpointCadence`, `WorkloadManifestOptIns`, etc. | various | IS-axis in-unit declarations (U-IS-01 / U-IS-04 / U-IS-07 / U-IS-13 …), all within-axis `Depends on`-cone | v2.1 §2 unit bodies | within-axis edges (preserved verbatim) | Clean — never forked |
| `Path`, `Bytes`, `Integer`, `string`, `bool` | various | Excluded stack-primitives — Python / Pydantic v2 builtins | `CLAUDE.md` §3.1 stack commitment | n/a — no carrier needed | Clean — stack-primitive |

### §5.3 Standing maintenance rule

A future IS revision pass that introduces a new type at any IS-unit signature MUST add a row to §5.2 and resolve it to one of: (a) a within-axis in-unit declaration, (b) a `harness-core` carrier with the corresponding `Depends on` edge, (c) an IS-internal in-unit declaration (the Q-R2-1 pattern, for IS-axis-owned domain types no other axis consumes), or (d) an excluded stack-primitive. A type with no resolution is a materializability FORK and is surfaced as a finding — never silently consumed. `AuditPayload` / `AuditLedger` are explicitly **not** IS-exported (IS exports `StateLedgerEntry` + the hash-chain discipline; the OD-side `AuditPayload`/`AuditLedger` carrier is R5 scope) — recorded so the negative result stays visible.

---

## §6 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Information_Substrate_v2_3.md` |
| Version | v2.3 |
| Status | **Proposed** |
| Date | 2026-05-15 |
| Predecessor | `Implementation_Plan_Information_Substrate_v2_2.md` (v2.2 — F3-02 IS-side closure record; itself a delta over v2.1, the v2.1 baseline canonical at Phase 6 close) |
| Authoring discipline | `implementation-planner` SKILL.md §8 revision-pass sub-mode |
| Revision scope | IS plan v2.2 → v2.3 materializability-conformance amendment — Revision Pass R2. M-1-IS resolution (U-IS-02/05/12/14); `UnitId` carrier (U-IS-17); `WorkflowClass` → `WorkloadClass` type-spelling unification; U-IS-06 git-domain trio declared IS-internal per Q-R2-1 operator override; new permanent §5 Auxiliary-type carrier audit per Q-R2-4. 6 revised unit bodies; 11 units preserved verbatim. |
| Operator ratification | Q-R2-1 through Q-R2-4 ratified 2026-05-15. Q-R2-1: OVERRIDE — git trio is IS-internal (declared in U-IS-06). Q-R2-2: R2 default — type-name unification only. Q-R2-3: R2 default — U-IS-04 `ContractID` re-point deferred. Q-R2-4: R2 default — permanent §5 audit section carried. |
| Inputs absorbed | `.harness/revision_R2_is_plan.md` (the ratified R2 proposal); `.harness/materializability_audit_is_plan.md` (IS audit); `.harness/shared_type_carrier_map.md` (T1); `.harness/xal3_resolution_recommendations.md` (T2); `.harness/revision_R1_harness_core.md`; `design-substrate/Implementation_Plan_Harness_Core_v1_0.md` (U-CORE-01); `design-substrate/Implementation_Plan_Information_Substrate_v2_2.md` + `_v2_1.md` (canonical unit bodies) |
| Deferred action items | **AI-R2-1** (§0.6) — U-IS-02 landed-source retrospective: the landed `harness-is/` path-resolver source MUST be inspected and re-pointed to `harness-core` imports before v2.3 is fully consumed. **FLAGGED, NOT PERFORMED** — separate deferred coding-lane action under the HARD WALL. **Q-R2-3** — U-IS-04 `ContractID` re-point to U-CORE-01, deferred to a future pass. |
| No Class-1 fork | R2 surfaces no Class-1 (halt-execution) fork. The IS audit's two Class-1-halt candidates were lifted by T2 (FACTOR-OUT, decided — §0.5). Q-R2-1 was the only Class-2 item — resolved by operator decision. The U-IS-02 retrospective (§0.6) is Class-3 informational. |
| Successor | R3 (AS) / R4 (CP) / R5 (OD) per-axis materializability-conformance passes continue the R1–R5 series. |

---

*End of Implementation Plan — Information Substrate (IS axis) — v2.3.*
