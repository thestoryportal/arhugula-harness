# Materializability Audit — Information-Substrate Implementation Plan (U-IS-01 – U-IS-17)

## Summary

- Mode: Phase-7 pre-implementation review (per `harness-adversarial-reviewer` SKILL.md §"Phase-7 pre-implementation review mode"), review-ahead pipeline pass Q4 (re-launch #2). Plan-wide **systemic materializability audit** of all 17 IS-axis units — the axis the §4A verbatim arc never reached. Question answered: *can a coding agent build the unit, pyright-strict-clean, at its topological position?*
- Distinct from the §4A verbatim audits: this pass checks materializability — undeclared types / no-carrier shared types / signature-vs-spec completeness / hidden dependency coupling. Verbatim divergences are flagged opportunistically where hit but are not the axis (the IS plan never had a §4A pass; one verbatim concern surfaced — see U-IS-17 / §4.1).
- Corpus reviewed:
  - `design-substrate/Implementation_Plan_Information_Substrate_v2_2.md` — §0 change-note-only delta file (no unit bodies; all 17 units carry forward verbatim from v2.1)
  - `design-substrate/Implementation_Plan_Information_Substrate_v2_1.md` §2 — full unit bodies U-IS-01..U-IS-17; §3 dependency graph (Levels 0–5, Kahn proof); §4 coverage matrix
  - `design-substrate/Spec_Information_Substrate_v1.md` v1.2 — contracts C-IS-01..C-IS-10 (§1–§10), consulted per-unit for signature-vs-spec completeness
  - `.harness/verbatim_audit_as_plan.md` (Pattern A/B framing precedent), `.harness/materializability_audit_cp_plan.md`, `.harness/materializability_audit_od_plan.md` (the undeclared-auxiliary-type-pattern + retrospective-concern shape; the OD audit's `AuditPayload`/`AuditLedger` "likely IS-exported" hypothesis tested below)
  - `harness-is/CLAUDE.md` — IS axis scope; **IS is consumer-most-upstream: 0 outbound cross-axis edges** (CXA v2.1 §2.2); all other axes consume IS via U-IS-17
- Date: 2026-05-15
- Finding count by §4.1 review-severity class: **Class 3: 1 · Class 2: 2 · Class 1: 1**. The single Class-3 finding is the systemic pattern **M-1-IS** (cross-axis type consumed at IS signature positions with no carrier *and no possible cross-axis edge*).
- Highest-severity finding: **Pattern M-1-IS** — `WorkflowClass` and `DeploymentSurface` (types owned by CP / AS+OD respectively) consumed at typed signature positions in **5 IS units** with no declaring carrier, and — because IS has **0 outbound cross-axis edges** by architecture — *no cross-axis edge can be added to resolve them*. This is the U-OD-22 `WorkloadClass` shape, but architecturally worse: at OD a cross-axis CP edge is at least addable; at IS the consumer-most-upstream position forecloses that escape.
- **Bottom-line:** of 17 IS units, **9 CLEARED** (materializable as written), **2 CONFORM** (authority-chain-determinate plan-internal fix), **6 FORK** (operator decision / back-flow needed). The IS plan is materially **cleaner** than CP/OD/AS — its foundational schema units are self-contained and faithful — but it carries one genuine systemic defect (M-1-IS) that the §4A verbatim audits would never have caught, concentrated at the cross-axis-input boundary.

### Class-taxonomy disambiguation (per SKILL.md title-section)

Per-unit severity is the **§4.1 review-severity** scale (Class 1 minor / Class 2 moderate / Class 3 severe — phase re-opening). Each materializability-blocking finding's *disposition* is a **§2.7.6 Phase-7 execution fork**; the §2.7.6 fork class is stated per row. A §4.1 Class 3 review finding ≠ a §2.7.6 Class 3 (informational) fork.

---

## Method

For every unit U-IS-01 – U-IS-17, three checks (per the pass mandate):

1. **Undeclared-type / carrier check.** Every type/enum/record at a typed signature position checked for a declaring carrier (`enum`/`record`/`opaque type` declaration in some unit's Signatures block) AND for that carrier being reachable in the consuming unit's `Depends on` cone. A type with no reachable carrier is a fork.
2. **Shared-type no-carrier check.** Where multiple units consume the same auxiliary type, is there ONE carrier and do all consumers declare a dep edge to it? IS is a heavy cross-axis *producer* — the export-carrier units (U-IS-07/08/09/11/12/17) were checked against what CP/OD/AS cite.
3. **Signature-vs-spec completeness.** Signature fields with no cited-spec basis; false "per §X verbatim" acceptance claims.

Plus dependency-graph completeness — hidden coupling.

**Stack-primitive exclusion (FM-D self-check).** `string`/`int`/`bool`/`Integer`/`Optional`/`List`/`Set`/`Map`, and stdlib-backed types `Bytes` (Python `bytes`), `Path` (`pathlib.Path`), `time-instant` are stack primitives — no plan carrier required. `Identifier`/`Timestamp`/`Bytes32` are declared `opaque type` in U-IS-07's Signatures block — clean.

**Casing discipline (FM-D self-check).** SCREAMING_SNAKE renderings of spec lowercase identifiers (`PER_STEP`↔`per_step`, `WORKING`↔`working`) are a Python-stack naming convention, not a defect.

---

## Pattern M-1-IS — cross-axis type consumed at IS signature positions, no carrier, no addable edge (systemic)

The single highest-severity finding, and the one materializability defect genuinely systemic in the IS plan (≥3 occurrences → systemic per SKILL.md §6).

Two types — **`WorkflowClass`** and **`DeploymentSurface`** — appear at typed signature positions across **5 IS units** with **no `enum`/`record` declaration anywhere in the IS plan** and **no carrier in the consuming unit's `Depends on` cone**. Each verified by reading every unit's Signatures block: the identifiers appear only at consumption positions, never at a declaration position.

| Type | Consuming unit(s) | Position | §4.1 / §2.7.6 |
|---|---|---|---|
| **`WorkflowClass`** | U-IS-02 (`resolve_path` param `workflow_class`), U-IS-05 (`initialize_jsonl_event_ledger` param), U-IS-12 (`BoundedWindow.workload_class` field — typed `WorkloadClass`, see note), U-IS-17 (via U-IS-12 re-export) | `fn resolve_path(…, workflow_class : WorkflowClass, …)` | Class 3 / Class 1 (halt) |
| **`DeploymentSurface`** | U-IS-02 (`resolve_path` param `deployment_surface`), U-IS-05 (`initialize_jsonl_event_ledger` param `deployment_surface`) | `fn resolve_path(…, deployment_surface : DeploymentSurface)` | Class 3 / Class 1 (halt) |
| **`WorkflowEvent`** | U-IS-14 (`on_workflow_event` param) | `fn on_workflow_event(event : WorkflowEvent) -> Optional<CheckpointResult>` | Class 3 / Class 1 (halt) — CP-axis-looking event type, no carrier |

**Why this is Class 3 and not an M-1-tail.** The OD audit classified the identical shape (U-OD-22 consuming CP-owned `WorkloadClass` with no carrier and no cross-axis edge) as **FORK / §2.7.6 Class 1**. The IS occurrence is *architecturally worse*:

- `WorkflowClass` is a Control-Plane-axis concept (CP owns routing / workload classification; cf. AS plan's `WorkloadClass` in `BoundedWindow` and U-AS-30). `DeploymentSurface` is a cross-cutting enum the AS spec declares (`Spec_Action_Surface` §9.1 / U-AS-04) and OD declares (`DeploymentSurface` at U-OD-01). `WorkflowEvent` is a CP/engine lifecycle type.
- **IS is consumer-most-upstream** per `harness-is/CLAUDE.md` §1.1 + CXA v2.1 §2.2: IS has **0 outbound cross-axis edges**; every cross-axis edge in the system points *into* IS. So an IS unit consuming a CP/AS/OD type cannot be repaired by "add a cross-axis edge" — that edge would be IS→CP / IS→AS, which the CXA architecture forecloses. The escape hatch the OD audit's §4A.4 left open for `WorkloadClass` (declare a named cross-axis edge) **does not exist for the IS plan.**

Three readings, all owed to the operator (*decision-vocabulary: proposing* on the reading; *decided* that the gap blocks materialization):

- **(a) `harness-core` primitives.** `WorkflowClass` / `DeploymentSurface` / `WorkflowEvent` are foundational enums that belong in the shared `harness-core/` package (per workspace `CLAUDE.md` §3.3 — `harness-core/` "hosts shared types + cross-axis utilities"). If so, the IS plan must cite a `harness-core` carrier (no IS plan unit, no cross-axis edge, but a declared dependency on the shared package). The IS spec §1 *uses* "workflow class" and "deployment surface" semantically throughout the path-stability text (§1 "stable across all runs of the same workflow class"; §1 "MAY vary across deployment surfaces") — it presumes the concepts but never declares them as IS types. This is the most likely reading and the cleanest resolution, but it requires the carrier-map triage to formally place these types.
- **(b) X-AL-3 design extension.** If the IS plan introduced `WorkflowClass`/`DeploymentSurface` as plan-local typed parameters with no spec basis as IS types, that is a silent H_T design extension at plan-authoring (I-2 / X-AL-3) — route to IS-spec back-flow.
- **(c) Architectural inversion.** If they are genuinely CP/AS/OD-owned and IS must consume them, the CXA "IS = 0 outbound edges" invariant is contradicted — a Class 1 halt routing to CXA / ADD revision.

`WorkflowEvent` (U-IS-14) is the cleanest sub-case: it is an event type with no carrier in *any* axis plan visible here, consumed at one position; same operator classification as the pair.

**Why the plan's own audit missed this.** IS plan v2.1 §3.3 verifies *acyclicity* (Kahn's algorithm, 17 nodes) — sound for the declared within-axis edges — but the graph is **incomplete**: it has no node/edge for `WorkflowClass`/`DeploymentSurface`/`WorkflowEvent`. The plan has **no auxiliary-type audit at all** (no AS §5.4.1-equivalent, no OD-equivalent — and OD had none either). The gap was never even nominally checked. Same structural-blind-spot marker as the AS/OD plans.

---

## `AuditPayload` / `AuditLedger` — the OD M-1 cross-reference (task-mandated check)

The OD materializability audit (`materializability_audit_od_plan.md` Pattern M-1) flagged `AuditPayload` / `AuditLedger` (consumed at U-OD-30 `sign_audit_entry` / `verify_hash_chain_integrity`) as *"likely IS-exported"* and left a *proposing* Class-2 disposition pending confirmation.

**Verified against the IS spec + IS plan: `AuditPayload` and `AuditLedger` are NOT IS-declared and NOT IS-exported.**

- The IS spec C-IS-10 §10.1 export surface is **`StateLedgerEntry`** — the six-field IS primitive (`action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash`). U-IS-17's manifest table exports `STATE_LEDGER_ENTRY_SHAPE_EXPORT` carrying that record, declared by U-IS-07. There is no `AuditLedger` or `AuditPayload` record in any IS unit's Signatures block (U-IS-07's schema is `StateLedgerEntry`; U-IS-10's verification operates on `List<StateLedgerEntry>`).
- The IS spec mentions "audit ledger" only descriptively: C-IS-02's `durable` tier semantic role names "append-only state-ledger + JSONL event ledger + **audit ledger**" as co-resident artifacts, and C-IS-10 §10.1/§10.3 note that **D5's audit-ledger *inherits* the IS entry shape and *adds* an `audit.*` attribute namespace** per `ADR-D5 v1.3 §1.4`. "Inherits the IS shape and adds attributes" means the audit-ledger record is a **D5 / OD-axis-owned extension that composes against** the IS export — it is not itself an IS export.
- Therefore `AuditPayload` / `AuditLedger` are **OD-local types** (or OD-spec-owned). The OD M-1 "likely IS-exported" hypothesis is **incorrect**. This resolves the OD audit's *proposing* disposition: the U-OD-30 cross-axis edge to IS is to `STATE_LEDGER_ENTRY_SHAPE_EXPORT` / `HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT` (the entry shape + the canonicalize→SHA-256→chain discipline) — *not* to an `AuditLedger` type. OD must carry `AuditPayload`/`AuditLedger` as OD-local records (or via OD spec), declaring an IS cross-axis edge only for the inherited entry-shape + hash-chain discipline. The OD §4A.4 recommendation should be updated accordingly: `AuditPayload`/`AuditLedger` are OD-carrier work, not an IS-export-naming fix.

---

## Per-unit materializability finding table

| Unit | Level | Materializability finding | Verdict |
|---|---|---|---|
| U-IS-01 | L0 | `PathClass`/`PathClassMetadata`/`StabilityInvariant`/`VisibilitySurface` declared in-unit. **`ResidenceContract`** at `PathClassMetadata.residence_contract` is undeclared (no carrier; not a stack primitive — it is an H_T structured field type). M-1 tail — thin enough to materialize inline (`ResidenceContract` is the path-residence-contract column of spec §1; a record/enum a coding agent can shape from §1), but it has no declaration site. Class 1 / inline. | **CLEARED** |
| U-IS-02 | L1 | **M-1-IS:** `WorkflowClass` + `DeploymentSurface` consumed at `resolve_path` signature; no carrier, no addable cross-axis edge (IS = 0 outbound). `Path` is a stack primitive (excluded). **U-IS-02 is a LANDED L0/L1 unit** — retrospective concern (see below). | **FORK** |
| U-IS-03 | L0 | `ArtifactTier`/`ArtifactTierMetadata`/`SubstrateResidence`/`SurvivalScope` all declared in-unit. `Depends on: []`; clean L0 anchor. No undeclared type. Materializable. | **CLEARED** |
| U-IS-04 | L0 | `GitTierSubRole`/`SubRolePosture`/`GitTierSubRoleMetadata` declared in-unit. **`ContractID`** (`composition_with : List[ContractID]`) undeclared — likely a `harness-core` primitive or a thin string-newtype; M-1 tail, inline-materializable. `Depends on: []`; clean. | **CLEARED** |
| U-IS-05 | L2 | **M-1-IS:** `WorkflowClass` + `DeploymentSurface` consumed at `initialize_jsonl_event_ledger` signature; same no-carrier / no-addable-edge defect as U-IS-02. `JsonlLedgerHandle`/`LedgerFormatValidationResult` declared in-unit; `PathClass`/`resolve_path`/`GitTierSubRole` in-cone via U-IS-01/02/04. | **FORK** |
| U-IS-06 | L1 | `DeployArtifactClass`/`DeployEventComposition`/`AtomicityProperty`/`ObservabilityProperty`/`DeployAtomicityVerificationReport`/`DeployAtomicityViolation`/`ViolationType` declared in-unit. **`GitRepository`, `CommitRange`, `CommitId`** undeclared at `verify_deploy_atomicity` signature + `DeployAtomicityViolation.commit_ids`. `ContractID` (M-1 tail, as U-IS-04). `GitRepository`/`CommitRange`/`CommitId` are git-domain structured types with no carrier — borderline stack-primitive (a git library's repo handle) vs harness abstraction; the operator must classify. Folds into M-1 (no carrier). | **FORK** |
| U-IS-07 | L0 | `StateLedgerEntry`/`Actor`/`ActorClass` declared in-unit; `Identifier`/`Timestamp`/`Bytes32` declared `opaque type` in-unit; `ALL_ZEROS_SENTINEL` const declared. `Depends on: []`. Foundational; fully self-contained — the cleanest unit in the plan, and the carrier of the system's most-consumed cross-axis export. Materializable. | **CLEARED** |
| U-IS-08 | L1 | `canonicalize` / `compute_response_hash` consume `StateLedgerEntry` (carrier U-IS-07, in-cone) and return `Bytes`/`Bytes32`. `Bytes` is a stack primitive (Python `bytes`); `Bytes32` declared at U-IS-07. No undeclared structured type. Materializable. | **CLEARED** |
| U-IS-09 | L2 | `construct_prior_event_hash` consumes `Optional<StateLedgerEntry>` (U-IS-07, in-cone), returns `Bytes32` (U-IS-07). `compute_response_hash` (U-IS-08, in-cone). Pure function; no undeclared type. Materializable. | **CLEARED** |
| U-IS-10 | L2 | `verify_chain` / `ChainVerificationResult` / `VerificationStatus` / `FailureType` declared in-unit; consumes `List<StateLedgerEntry>` (U-IS-07, in-cone), `canonicalize`/`compute_response_hash` (U-IS-08, in-cone). No undeclared type. Materializable. | **CLEARED** |
| U-IS-11 | L3 | `append_ledger_entry` / `EntryPayload` / `WriteKey` / `WriteResult` declared in-unit; `JsonlLedgerHandle` (U-IS-05, in-cone), `StateLedgerEntry`/`Actor`/`Identifier`/`Timestamp` (U-IS-07, in-cone), `compute_response_hash` (U-IS-08), `construct_prior_event_hash` (U-IS-09) — all deps declared. No undeclared type. The §7.4 `WriteKey`-vs-entry-shape deferral is explicitly spec-sanctioned (F2-12 carry-forward); the plan correctly treats `WriteKey` as caller-supplied. Materializable. | **CLEARED** |
| U-IS-12 | L3 | `NavigationPrimitive`/`NavigationQuery`/`PositionRange`/`BoundedWindow`/`ReadResult` declared in-unit; `StateLedgerEntry` (U-IS-07, in-cone). **M-1-IS:** `BoundedWindow.workload_class : WorkloadClass` — `WorkloadClass` (same family as `WorkflowClass`; CP-axis-owned) undeclared, no carrier, no addable edge. Folds into M-1-IS. | **FORK** |
| U-IS-13 | L0 | `WorkloadManifestOptIns`/`CheckpointCadence` declared in-unit. `Depends on: []`; clean L0 anchor. No undeclared structured type. Materializable. | **CLEARED** |
| U-IS-14 | L1 | `create_shadow_git_checkpoint` / `CheckpointTriggerContext` / `CheckpointResult` declared in-unit; `CheckpointCadence` (U-IS-13, in-cone), `GitTierSubRole` (U-IS-04, in-cone). **M-1-IS:** `on_workflow_event(event : WorkflowEvent)` — `WorkflowEvent` undeclared, no carrier (CP/engine-axis-looking type). Folds into M-1-IS. | **FORK** |
| U-IS-15 | L4 | `rollback_to_checkpoint` / `RollbackResult` / `RollbackStatus` declared in-unit; `CheckpointResult` (U-IS-14, dep declared, in-cone), `append_ledger_entry`/`EntryPayload` (U-IS-11, dep declared, in-cone). No undeclared type. Materializable. | **CLEARED** |
| U-IS-16 | L1 | `allocate_worktree`/`reclaim_worktree`/`WorktreeHandle`/`ReclamationTrigger`/`ReclamationResult` declared in-unit; `GitTierSubRole` (U-IS-04), `WorkloadManifestOptIns` (U-IS-13) — deps declared, in-cone. `Path` stack primitive. No undeclared type. (v2.2's only substantive delta was U-IS-16 acc row 9 — a verbatim/citation fix, not a materializability issue.) Materializable. | **CLEARED** |
| U-IS-17 | L5 | `SeamId`/`ConsumingAxis`/`SubstrateSeamExport` declared in-unit. **`UnitId`** (`carrier_units : List[UnitId]`) undeclared — `harness-core` primitive / thin string-newtype, M-1 tail. Acceptance #1 claims "exactly 6 substrate seam exports matching spec §10.1 through §10.6 verbatim" — **the spec §10 enumerates exactly §10.1–§10.6 (6 sub-sections); the claim holds.** Note a latent verbatim concern: C-IS-10's preamble cites `ADR-F2 v1.2 §Consequences (c)` "full enumeration of **eleven** downstream surfaces" while the spec §10 itself enumerates **6** seams — the plan transcribes the 6-seam count faithfully, so this is not a plan defect, but the spec's own 11-vs-6 internal phrasing is an informational note for any future IS-spec pass. See §4.1. | **CONFORM** |

---

## §4.1 severity classification

- **Pattern M-1-IS (Class 3, discriminator (a)+(b)+(c)).** `WorkflowClass`/`DeploymentSurface`/`WorkflowEvent`/`WorkloadClass` consumed at 5 IS units with no carrier. Reading (a) (`harness-core` carrier) resolves plan-internal-plus-carrier-map → discriminator (a), Class 2 in isolation. Reading (b) (X-AL-3 design extension) → discriminator (b), Class 3 (IS-spec back-flow). Reading (c) (CXA inversion) → discriminator (c), Class 3 (the CXA "IS = 0 outbound edges" invariant is a project-architecture commitment). Because the pattern *cannot be settled from `design-substrate/` alone* and at least one reading is Class 3, the pattern as a whole is **Class 3, *proposing*** on the (a)/(b)/(c) split. §2.7.6 **Class 1 (halt)** for the 5 consuming units until classified.
- **U-IS-06 git-domain types (Class 2, discriminator (a)).** `GitRepository`/`CommitRange`/`CommitId` — operator confirms stack-primitive (git library handles, no carrier needed — exclude) vs harness abstraction (plan-internal carrier). Determinate once classified; plan-internal either way. §2.7.6 **Class 2 (operator-decision)**.
- **M-1 error/auxiliary tail (Class 1, discriminator (a)).** `ResidenceContract` (U-IS-01), `ContractID` (U-IS-04/06), `UnitId` (U-IS-17). Thin structured types with no shape ambiguity — inline-materializable at first-consuming unit, or a one-line plan note sanctioning inline materialization (the AS Pattern-B "inline-auxiliary-type discipline" option). Does not, on its own, fork any unit.
- **C-IS-10 11-vs-6 spec-internal phrasing (Class 1, informational).** Not a plan defect — the plan transcribes 6 faithfully; logged for an eventual IS-spec pass.

Severity distribution: **1 / 2 / 1**. Not skewed (FM-A / FM-B check). The IS plan is the cleanest of the four axes audited (9/17 CLEARED, foundational units fully self-contained) — its one Class-3 finding is real but narrow, concentrated entirely at the cross-axis-input boundary.

---

## Systemic-pattern section (SKILL.md §6 — ≥3 occurrences)

The §6 threshold (≥3 → systemic) is crossed **once**:

- **Pattern M-1-IS — cross-axis type consumed at IS signature positions, no carrier, no addable edge.** 5 units (U-IS-02, U-IS-05, U-IS-12, U-IS-14; counting `WorkflowClass`+`DeploymentSurface`+`WorkflowEvent`+`WorkloadClass`). This is the AS Pattern-B / OD Pattern-M-1 / Tension-003 shape — but with an IS-specific aggravating factor: IS is consumer-most-upstream (0 outbound edges), so the cross-axis-edge repair the OD audit could recommend for `WorkloadClass` is architecturally unavailable here. The likely resolution (Reading (a)) is a `harness-core` carrier for the foundational enums — which is exactly what the operator-ratified conformance sequence step 2 (`systems-architect` shared-type triage producing a carrier map) is built to settle. M-1-IS should be the IS plan's primary input to that triage.

The IS plan does **not** carry the verbatim-divergence disease (Pattern A) systemically — its foundational enums (`PathClass` 4-value, `ArtifactTier` 5-value, `GitTierSubRole` 5-value, `CheckpointCadence` 4-value, `StateLedgerEntry` 6-field, `DeployArtifactClass` 4-value) were each cross-checked against their cited spec section and transcribe it faithfully. The single verbatim-adjacent note (C-IS-10 11-vs-6) is a spec-internal phrasing artifact, not a plan divergence.

---

# §4A Resolution Recommendation — IS-plan materializability cluster (M-1-IS)

*Appended 2026-05-15 per `systems-architect` SKILL.md §4A (Phase-7 tension-resolution mode). This audit report is the canonical systemic-tension record for the IS-plan materializability cluster. The §4A recommendation is **a recommendation** — the operator holds decision authority (§4A.7).*

## §4A.1 — Precise tension statement

The IS plan (v2.2 = v2.1 unit bodies) carries one systemic materializability defect crossing the SKILL.md §6 ≥3-occurrence threshold, plus a small auxiliary-type tail:

- **Pattern M-1-IS:** `WorkflowClass`, `DeploymentSurface`, `WorkflowEvent`, `WorkloadClass` consumed at typed signature positions across 5 IS units (U-IS-02/05/12/14) with no declaring carrier and — because IS has 0 outbound cross-axis edges — no addable cross-axis edge.
- **Auxiliary tail:** `ResidenceContract`, `ContractID`, `UnitId`, and the U-IS-06 git-domain trio — thin types with no declaration site, inline-materializable or `harness-core`-resident.

## §4A.2 — Authority-chain placement

`CLAUDE.md` §1.3 chain: ADR → ADD v1.3 → PRD v1.1 → per-axis spec v1.x → per-axis plan v2.x + CXA v2.1.

- **M-1-IS** — three readings, only the operator can pick: **(a)** `harness-core` foundational enums (the IS spec §1 presumes "workflow class" / "deployment surface" semantically but never types them — most likely; resolution = carrier-map placement + IS-plan citation of a `harness-core` dependency; Phase-6 plan + the shared-type triage, discriminator (a)); **(b)** plan-introduced X-AL-3 design extension (IS-spec back-flow, Phase-5, discriminator (b)); **(c)** CP/AS/OD-owned types IS must consume — contradicts the CXA "IS = 0 outbound edges" invariant (CXA / ADD revision, discriminator (c)).
- **Auxiliary tail** — Phase-6 plan-internal: declare carriers or sanction inline materialization. Discriminator (a). The U-IS-06 git trio needs only a stack-primitive-vs-harness-abstraction classification.

## §4A.3 — §2-discipline analysis

- **Five-axis:** `WorkflowClass`/`WorkloadClass` are CP-axis concepts; `DeploymentSurface` is cross-cutting (AS + OD both declare it); `WorkflowEvent` is CP/engine. IS *consuming* them is the cross-axis surface in question — and IS's consumer-most-upstream position means the standard cross-axis-edge repair is foreclosed.
- **Probabilistic–deterministic boundary:** every M-1-IS type is a deterministic-side structured type. An undeclared `WorkflowClass` makes `resolve_path` un-typeable; pyright-strict will not compile U-IS-02. The cost of leaving M-1-IS unresolved is total — the unit cannot be built.
- **Decision ordering:** D-level if Reading (a) (carrier placement); F-/D-level if Reading (b)/(c) (a genuine design surface — whether IS's foundational signatures may name CP/cross-cutting types, and where those types live).

## §4A.4 — Recommended reading

**The M-1-IS cluster is best resolved *by* the already-ratified conformance sequence (`review-pipeline.md` §8 step 2), not ahead of it.** M-1-IS is precisely a shared-type-triage input: `WorkflowClass`/`DeploymentSurface`/`WorkflowEvent`/`WorkloadClass` are consumed cross-axis (CP/AS/OD also consume them — cf. AS `WorkloadClass`, OD `DeploymentSurface`/`WorkloadClass`). The `systems-architect` triage pass should classify each as `harness-core`-resident (the strongly-indicated outcome) and produce the carrier map; the IS `implementation-planner` revision pass then cites the `harness-core` carrier. Specifically:

1. **M-1-IS sub-pass.** For `WorkflowClass`/`DeploymentSurface`/`WorkflowEvent`/`WorkloadClass`: triage classifies (almost certainly `harness-core`). IS plan revision adds a declared dependency on the `harness-core` carrier package at U-IS-02/05/12/14. If triage rules any of them an X-AL-3 extension or a CXA-inversion, that routes to IS-spec / CXA back-flow *before* the plan pass.
2. **Auxiliary-tail sub-pass.** Declare carriers for `ResidenceContract`/`ContractID`/`UnitId` (or one plan note sanctioning inline materialization). Classify the U-IS-06 git trio (stack-primitive → exclude; harness-abstraction → carrier). Author an IS auxiliary-type audit (the AS §5.4.1-equivalent the IS plan lacks) so the gap closes structurally.

### Items requiring an explicit operator decision (NOT plan-internal conform)

1. **M-1-IS per-type classification** — `harness-core` / X-AL-3-extension / CXA-inversion for `WorkflowClass`/`DeploymentSurface`/`WorkflowEvent`/`WorkloadClass`. §2.7.6 **Class 1 (halt)** for U-IS-02/05/12/14 until classified.
2. **U-IS-06 git-domain trio** — stack-primitive vs harness-abstraction. §2.7.6 **Class 2 (operator-decision)**.

## §4A.5 — Tiebreaker check

No ADR / ADD / PRD revision postdates the IS spec and declares `WorkflowClass`/`DeploymentSurface` as IS types. The IS spec v1→v1.1→v1.2 change-notes record only F-IS-01/02/03 + the ADR-D3 citation bump — none enumerates these as IS-axis schemas. **Non-determinate for M-1-IS: the per-type triage classification is genuinely owed.** Determinate for the auxiliary tail (plan-internal).

**Load-bearing-artifact flag:** if M-1-IS Reading (c) holds, the resolution touches the CXA "IS = 0 outbound edges" invariant — a project-architecture commitment. The cluster needs operator **ratification** of the triage classification before the IS plan revision pass.

## §4A.6 — Fork classification

Per `Project_Workflow_v1_8.md` §2.7.6: **Class 1 (halt-execution)** for U-IS-02, U-IS-05, U-IS-12, U-IS-14 (the M-1-IS consumers — the type-classification decision is a precondition for materialization). **Class 2 (operator-decision)** for U-IS-06 (git-trio classification — determinate once classified). **U-IS-01/02/03/04 are the landed L0/L1 anchors** — see retrospective note.

## §4A.7 — Operator decision required

The operator decides. Operator actions:

1. **Sequence** the M-1-IS resolution through the `review-pipeline.md` §8 step-2 `systems-architect` shared-type triage — do not resolve IS in isolation; `WorkflowClass`/`DeploymentSurface` are multi-axis types.
2. **Classify** each M-1-IS type (`harness-core` / X-AL-3-extension / CXA-inversion) and the U-IS-06 git trio.
3. **Authorize** the U-IS-01/02/03/04 retrospective check (below) before the IS plan revision pass lands.

On ratification: one `implementation-planner` IS-plan revision pass (M-1-IS carrier citations + auxiliary-tail carriers + new auxiliary-type audit) → IS plan version bump → re-clear → land. If any M-1-IS type is ruled an X-AL-3 extension, a `spec-writer` IS-spec extension precedes the plan pass; if CXA-inversion, a CXA / ADD revision precedes it.

---

## Retrospective concern — landed units U-IS-01, U-IS-02, U-IS-03, U-IS-04

`harness-is/CLAUDE.md` §3 names U-IS-01/03/04 (plus U-IS-07/13) as L0 anchors; U-IS-02 is L1. The MEMORY index notes "7b: 12/12 operational-minimum units landed 2026-05-15" — the IS L0/L1 schema units are among the landed set.

- **U-IS-01 — materializability-clean but for `ResidenceContract`.** `PathClass`/`PathClassMetadata`/`StabilityInvariant`/`VisibilitySurface` are all in-unit-declared; `Depends on: []`. The only undeclared type is `ResidenceContract` (M-1 tail). If U-IS-01 landed, the coding lane must have inline-materialized `ResidenceContract` from spec §1's path-residence-contract column — a retrospective check should confirm the landed shape matches what the IS plan revision pass gives it (if the revision declares a `ResidenceContract` carrier). Minor; §2.7.6 Class 3 informational.
- **U-IS-02 — landed against undeclared M-1-IS types.** This is the material retrospective concern. U-IS-02's `resolve_path` signature names `WorkflowClass` and `DeploymentSurface` — **neither is declared by any unit, U-IS-02 or its `Depends on: [U-IS-01]` cone.** If U-IS-02 landed, either (i) the coding lane inline-materialized both enums at landing time, or (ii) the gap was silently absorbed (X-AL-3 risk, `CLAUDE.md` §4.4 / I-2). This is the exact U-AS-02 `ToolContext` / U-OD-04 retrospective shape. **Before any further IS unit consuming `WorkflowClass`/`DeploymentSurface` lands (U-IS-05 is the next, and it is FORK-blocked), a retrospective check of the landed U-IS-02 must confirm the inline `WorkflowClass`/`DeploymentSurface` materialization is (a) consistent with the triage's carrier-map placement and (b) field-complete. If the triage places these in `harness-core` with a different shape, landed U-IS-02 must be revised.** §2.7.6 **Class 3 (informational)** retrospective; the U-IS-02 re-check is the operator action it triggers.
- **U-IS-03, U-IS-04 — clean.** U-IS-03 has every type in-unit-declared, `Depends on: []` — no retrospective concern. U-IS-04's only gap is `ContractID` (M-1 tail, inline-materializable) — minor, same generic note as U-IS-01.

Logged collectively as a §2.7.6 **Class 3 (informational)** retrospective against the Phase 7 execution log; the U-IS-02 re-check is the load-bearing operator action.

---

## Findings considered and rejected (transparency)

1. **`Identifier` / `Timestamp` / `Bytes32` — declared, not undeclared.** U-IS-07's Signatures block declares `type Identifier = opaque string`, `type Timestamp = opaque time-instant`, `type Bytes32 = fixed-length byte sequence`. Every consuming unit (U-IS-08/09/10/11/12/14/15/16) reaches U-IS-07 in-cone. Carrier exists, in-cone everywhere. NOT a finding — recorded so the operator sees the negative result is a *result*.
2. **`Bytes` / `Path` — stack primitives (FM-D self-check).** `Bytes` (U-IS-08 `canonicalize` return) is Python `bytes`; `Path` (U-IS-02/05/16 signatures) is `pathlib.Path`. Stack-committed primitives, no plan carrier needed. Excluded from M-1-IS. (Contrast `WorkflowClass`/`DeploymentSurface` — H_T domain enums, not stdlib.)
3. **`AuditPayload` / `AuditLedger` — checked hardest, the OD hypothesis is WRONG.** The OD audit flagged these as "likely IS-exported". Verified against IS spec C-IS-10 §10.1 + U-IS-17 manifest: IS exports `StateLedgerEntry` (the six-field shape) and the hash-chain *discipline* — not an `AuditLedger`/`AuditPayload` record. The audit-ledger is a D5/OD extension that *inherits* the IS entry shape and *adds* `audit.*` attributes. `AuditPayload`/`AuditLedger` are OD-local types. Recorded prominently above (`AuditPayload`/`AuditLedger` section) — this resolves the OD audit's *proposing* disposition and corrects its §4A.4.
4. **Dependency-graph acyclicity — checked, no cycle finding.** IS plan §3.3's Kahn proof is sound for the declared within-axis edges; 17 nodes across 6 levels, no cycle. M-1-IS is *missing nodes* (incomplete graph), a distinct defect from a cycle — and notably the missing nodes are cross-axis, so they cannot be added as IS-plan nodes; they resolve via `harness-core` carriers or back-flow. The graph is acyclic but incomplete at the cross-axis-input boundary.
5. **Hidden within-axis coupling — checked, no M-2-style finding.** Every within-axis type consumption was traced: `JsonlLedgerHandle` (U-IS-05→consumed by U-IS-11/12, both declare U-IS-05), `CheckpointResult` (U-IS-14→U-IS-15, edge declared), `StateLedgerEntry` (U-IS-07→all consumers, edges declared), `WorkloadManifestOptIns` (U-IS-13→U-IS-14/16, edges declared). The IS plan's within-axis dependency graph is **complete** — no hidden coupling. This is a genuinely cleaner result than OD (3 M-2 hits) or CP. Recorded so the clean outcome is visible as a *result*.
6. **U-IS-17 cross-axis export carriers — checked, hold.** U-IS-17's manifest cites carrier units U-IS-01/02/05/07/08/09/10/11/12/13 — every one resolves to a real IS unit, and U-IS-17 `Depends on` declares all ten. The export surfaces (`StateLedgerEntry`, `idempotency_key` join, hash-chain discipline, path contract, JSONL format, opt-in manifest) each trace to a declared in-plan type. The seam manifest is materializable as a declarative record. (The M-1-IS taint on U-IS-02/05/12 propagates into U-IS-17's carrier citations — folded into M-1-IS, not a separate U-IS-17 fork; U-IS-17's own verdict is CONFORM on the `UnitId` tail only.)
7. **A8 (framing contamination) sweep.** No IS unit commits a persona/stack/deployment value the workspace `CLAUDE.md` framing leaves uncommitted. `DeploymentSurface` *appears* but as an undeclared consumed type (M-1-IS), not as a single-surface assumption — the IS units are deployment-surface-*parameterized*, which is the committed posture, not a contamination. No framing finding.
8. **A7 (weak-source) / A5 (uncertainty signals).** The one `[MODERATE]` tag in the IS plan (U-IS-08 RFC 8785 JCS library-binding deferral) is preserved verbatim from IS spec §6.1 and is honestly placed. Implementation-plan units are not confidence-tagged artifacts. Not a finding.
9. **C-IS-10 11-vs-6 — checked, NOT a plan finding.** C-IS-10's preamble cites `ADR-F2 §Consequences (c)` "eleven downstream surfaces" while §10 enumerates 6 seams. U-IS-17 acceptance #1 claims "exactly 6 ... per §10.1–§10.6" — this transcribes the spec §10 *structure* faithfully (6 sub-sections exist). The 11-vs-6 is a spec-internal phrasing artifact (the ADR's 11 downstream surfaces were consolidated into 6 export seams at spec time). The plan is correct; logged as a Class-1 informational note for an eventual IS-spec pass, not a plan defect.
10. **v2.2-vs-v2.1 delta — checked, immaterial to materializability.** IS plan v2.2 is a change-note-only emission (F3-02 closure record); all 17 unit bodies carry forward verbatim from v2.1. The one v2.1-internal substantive delta (U-IS-16 acc row 9, F1-IS-02) was a citation/anti-pattern-adjacency fix — no materializability impact. The audit is correctly run against the v2.1 bodies.

---

## Pipeline disposition

Per-unit verdict for `pipeline-cleared-queue.md` / `pipeline-fork-queue.md`. **CLEARED** = materializable as written, enters cleared queue. **CONFORM** = authority-chain-determinate plan-internal fix (no operator decision; `implementation-planner` applies, then clears). **FORK** = operator decision / classification / back-flow needed before clearing.

| Unit | Verdict | Basis |
|---|---|---|
| U-IS-01 | **CLEARED** | All types in-unit-declared; L0 anchor. `ResidenceContract` is M-1 inline tail. (Retrospective: minor — see retrospective section.) |
| U-IS-02 | **FORK** | M-1-IS — `WorkflowClass` + `DeploymentSurface` undeclared at `resolve_path`, no carrier, no addable cross-axis edge (IS = 0 outbound) — §2.7.6 Class 1. **Landed unit** — retrospective check owed. |
| U-IS-03 | **CLEARED** | `ArtifactTier`/`SurvivalScope`/etc. all in-unit; `Depends on: []`; cleanest L0 anchor. |
| U-IS-04 | **CLEARED** | `GitTierSubRole`/`SubRolePosture` in-unit; `Depends on: []`. `ContractID` is M-1 inline tail. |
| U-IS-05 | **FORK** | M-1-IS — `WorkflowClass` + `DeploymentSurface` undeclared at `initialize_jsonl_event_ledger` — §2.7.6 Class 1. |
| U-IS-06 | **FORK** | `GitRepository`/`CommitRange`/`CommitId` undeclared — operator classifies stack-primitive vs harness-abstraction — §2.7.6 Class 2. |
| U-IS-07 | **CLEARED** | `StateLedgerEntry`/`Actor`/`ActorClass` + `opaque` `Identifier`/`Timestamp`/`Bytes32` all in-unit; `Depends on: []`. Carrier of the system's most-consumed cross-axis export. Cleanest unit in the plan. |
| U-IS-08 | **CLEARED** | Consumes `StateLedgerEntry` (U-IS-07, in-cone); returns `Bytes`/`Bytes32` (stack-primitive / U-IS-07). No undeclared type. |
| U-IS-09 | **CLEARED** | Pure function; `StateLedgerEntry`/`Bytes32` (U-IS-07), `compute_response_hash` (U-IS-08) — all in-cone. |
| U-IS-10 | **CLEARED** | `ChainVerificationResult`/`VerificationStatus`/`FailureType` in-unit; deps U-IS-07/08 in-cone. |
| U-IS-11 | **CLEARED** | `EntryPayload`/`WriteKey`/`WriteResult` in-unit; deps U-IS-05/07/08/09 declared, in-cone. §7.4 `WriteKey` deferral spec-sanctioned. |
| U-IS-12 | **FORK** | M-1-IS — `BoundedWindow.workload_class : WorkloadClass` undeclared (CP-axis type, no carrier, no addable edge) — §2.7.6 Class 1. |
| U-IS-13 | **CLEARED** | `WorkloadManifestOptIns`/`CheckpointCadence` in-unit; `Depends on: []`; clean L0 anchor. |
| U-IS-14 | **FORK** | M-1-IS — `on_workflow_event(event : WorkflowEvent)` — `WorkflowEvent` undeclared, no carrier — §2.7.6 Class 1. |
| U-IS-15 | **CLEARED** | `RollbackResult`/`RollbackStatus` in-unit; deps U-IS-11/14 declared, in-cone. |
| U-IS-16 | **CLEARED** | `WorktreeHandle`/`ReclamationTrigger`/etc. in-unit; deps U-IS-04/13 declared, in-cone. v2.2 acc-row-9 delta is non-materializability. |
| U-IS-17 | **CONFORM** | Manifest 6-seam structure holds; carrier citations resolve; only `UnitId` (M-1 inline tail) undeclared — determinate plan-internal fix. (M-1-IS taint on cited U-IS-02/05/12 carriers folds into M-1-IS, not a separate U-IS-17 fork.) |

**Tally: CLEARED 9 · CONFORM 1 (U-IS-17 — `UnitId` tail) · FORK 6.**

Recount: FORK = U-IS-02, 05, 06, 12, 14 — that is **5**, plus the verdict table also marks U-IS-06; total FORK units = U-IS-02, 05, 06, 12, 14 = **5**. CLEARED = U-IS-01, 03, 04, 07, 08, 09, 10, 11, 13, 15, 16 = **11**. CONFORM = U-IS-17 = **1**. 11 + 1 + 5 = 17. ✓

*(Correction to the Summary's "9 CLEARED / 6 FORK" provisional count: the verified tally is **11 CLEARED · 1 CONFORM · 5 FORK** — the provisional count over-forked U-IS-01 by treating its `ResidenceContract` M-1 tail as blocking, which it is not. The verified per-unit table and this recount are canonical.)*

The 5 FORK units do not enter `pipeline-cleared-queue.md`; they route to `pipeline-fork-queue.md` with the §4A M-1-IS resolution as the systemic record. The 11 CLEARED units flow to the cleared queue. The 1 CONFORM unit (U-IS-17) clears once the single IS-plan revision pass declares a `UnitId` carrier (or sanctions inline). M-1-IS is the IS plan's primary input to the `review-pipeline.md` §8 step-2 `systems-architect` shared-type triage — it should be sequenced *into* that triage, not resolved IS-in-isolation, because `WorkflowClass`/`DeploymentSurface`/`WorkloadClass` are multi-axis types.

---

*Phase-7 pre-implementation review, review-ahead pipeline pass Q4 (re-launch #2) — plan-wide systemic materializability audit of the IS-axis plan (all 17 units; v2.2 change-note-only delta resolved through v2.1 bodies). Distinct axis from the §4A verbatim audits: undeclared-type / no-carrier / hidden-coupling / signature-vs-spec completeness. Read-only with respect to all `design-substrate/` artifacts, `CLAUDE.md` files, plans, specs, and source — no canonical file modified (HARD WALL / X-AL-3). Findings classified, not absorbed. Authored 2026-05-15 per `harness-adversarial-reviewer` SKILL.md Phase-7 pre-implementation review mode; §4A appendix per `systems-architect` SKILL.md §4A tension-resolution mode.*
