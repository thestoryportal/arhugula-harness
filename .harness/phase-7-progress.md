# Phase 7 — Atomic-Unit Landing Progress

Workspace-internal progress ledger (skill `phase-7-implementation` Step 7).
NOT a design-phase artifact. One row per landed atomic unit. Coverage-matrix
updates happen at cluster close, not per unit.

## Sub-phase 7b — per-axis-stream landings

| Unit | Surface | Spec | Status | Commit | Date |
|---|---|---|---|---|---|
| U-IS-01 | Path-class registry schema | C-IS-01 §1 | ✅ landed | `feat(is): land U-IS-01` | 2026-05-15 |
| U-IS-03 | Artifact-tier registry schema | C-IS-02 §2 | ✅ landed | `feat(is): land U-IS-03` | 2026-05-15 |
| U-IS-02 | Path-resolver primitive | C-IS-01 §1 | ✅ landed | `feat(is): land U-IS-02` | 2026-05-15 |
| U-IS-04 | Git tier sub-role taxonomy | C-IS-03 §3 | ✅ landed | `feat(is): land U-IS-04` | 2026-05-15 |
| U-AS-01 | Sandbox-tier type declaration | C-AS-01 §1.1-1.2 | ✅ landed | `feat(as): land U-AS-01` | 2026-05-15 |
| U-AS-02 | Forced-tier resolution | C-AS-01 §1.3 | ✅ landed | `feat(as): land U-AS-02` | 2026-05-15 |
| U-AS-03 | Sandbox-fail-class taxonomy | C-AS-04 §4 | ✅ landed | `feat(as): land U-AS-03` | 2026-05-15 |
| U-AS-04 | Foundational discriminator enums | C-AS-02 §2.3 | ✅ landed | `feat(as): land U-AS-04` | 2026-05-15 |
| U-CP-15 | EngineClass enum + capability floors | C-CP-07 §7.1+§7.4 | ✅ landed | `feat(cp): land U-CP-15` | 2026-05-15 |
| U-OD-01 | 9-cell observability matrix | C-OD-01 §1.1+§1.3-1.5 | ✅ landed | `feat(od): land U-OD-01` | 2026-05-15 |
| U-OD-04 | OTel GenAI semconv 1.41.0 base layer | C-OD-04 §4.1-§4.5 | ✅ landed | `feat(od): land U-OD-04` | 2026-05-15 |
| U-CP-00 | WorkloadClass closed 4-value enum | C-CP-07 §7.3 | ✅ landed | `feat(core): land U-CP-00` | 2026-05-15 |
| U-CP-22 | TopologyPattern enum + admissibility | C-CP-10 §10.1-§10.3 | ✅ landed | `feat(cp): land U-CP-22` | 2026-05-15 |
| U-AS-05 | `blast_radius_floor` default mapping | C-AS-02 §2.4 | ✅ landed | `feat(as): land U-AS-05` | 2026-05-15 |
| U-AS-11 | `SandboxProviderClass` enum + metadata | C-AS-09 §9.2 | ✅ landed | `feat(as): land U-AS-11` | 2026-05-15 |
| U-CP-19 | `ResumptionKind` taxonomy + bindings | C-CP-08 §8.1 | ✅ landed | `feat(cp): land U-CP-19` | 2026-05-15 |
| U-CORE-01 | Cross-cutting shared-type set (`DeploymentSurface`, `PersonaTier`, `WorkflowEventClass`, 9 identity aliases) — carrier-thin | C-AS-09 §9.1+§9.4, C-IS-05 §5, C-CP-05 §5.1-§5.2, C-CP-13 §13.4 | ✅ landed | `feat(core): land U-CORE-01` | 2026-05-15 |
| U-OD-00 | OD-local audit-ledger composition types (`AuditPayload`, `AuditLedgerEntry`, `AuditLedger`, `AuditSignatureAttributes`, `SignatureAlgorithm`) | C-OD-14 §14.5, ADR-D5 §1.4/§1.4.1, C-OD-21 §21.2 | ✅ landed | `feat(od): land U-OD-00` | 2026-05-15 |
| U-CP-00b | CP schema-attribute utility enums (`AttributeValueType`, `Cardinality`) — carrier-split (9 structured types deferred) | aggregate of 7 CP attribute-schema contracts | ✅ landed | `feat(cp): land U-CP-00b` | 2026-05-15 |
| U-IS-07 | State-ledger entry shape schema (`StateLedgerEntry`, `Actor`, `ActorClass`, `Bytes32`, `ALL_ZEROS_SENTINEL`) | C-IS-05 §5 | ✅ landed | `feat(is): land U-IS-07` | 2026-05-15 |
| U-IS-13 | Workload manifest opt-in schema (`WorkloadManifestOptIns`, `CheckpointCadence`) | C-IS-08 §8.1-§8.2, C-IS-09 §9.1 | ✅ landed | `feat(is): land U-IS-13` | 2026-05-15 |
| U-IS-05 | JSONL event ledger file lifecycle (`initialize_jsonl_event_ledger`, `validate_jsonl_event_ledger_format`, `JsonlLedgerHandle`) | C-IS-03 §3 | ✅ landed | `feat(is): land U-IS-05` | 2026-05-15 |
| U-IS-06 | Atomic deploy-event composition + `verify_deploy_atomicity` (git-shell-out split-deploy verification) | C-IS-04 §4 | ✅ landed | `feat(is): land U-IS-06` | 2026-05-15 |
| U-IS-08 | Entry canonicalization + per-entry SHA-256 hash (`canonicalize`, `compute_response_hash`) | C-IS-06 §6.1-§6.2 | ✅ landed | `feat(is): land U-IS-08` | 2026-05-15 |
| U-IS-14 | Shadow-Git checkpoint primitive (`create_shadow_git_checkpoint`, `should_checkpoint`) — `on_workflow_event` deferred (tension F-3) | C-IS-08 §8.2-§8.4 | ✅ landed | `feat(is): land U-IS-14` | 2026-05-16 |
| U-IS-16 | Worktree-isolation primitive (`WorktreeIsolationManager`: allocate/reclaim, concurrency cap) | C-IS-09 §9.2-§9.3 | ✅ landed | `feat(is): land U-IS-16` | 2026-05-16 |
| U-IS-09 | Chain-link construction primitive (`construct_prior_event_hash`) | C-IS-06 §6.3 | ✅ landed | `feat(is): land U-IS-09` | 2026-05-16 |
| U-IS-10 | Chain verification + tamper-evidence (`verify_chain`, `ChainVerificationResult`) | C-IS-06 §6.4-§6.5 | ✅ landed | `feat(is): land U-IS-10` | 2026-05-16 |
| U-IS-12 | C2-pole selective bounded read (`NavigationPrimitive`, 4 concrete primitives) | C-IS-07 §7.2-§7.3 | ✅ landed | `feat(is): land U-IS-12` | 2026-05-16 |
| U-IS-11 | C3-pole append-only write contract (`append_ledger_entry`, JSONL §7.3 format) | C-IS-07 §7.1-§7.3 | ✅ landed | `feat(is): land U-IS-11` | 2026-05-16 |
| U-IS-15 | Shadow-Git rollback primitive (`rollback_to_checkpoint`) | C-IS-08 §8.3 | ✅ landed | `feat(is): land U-IS-15` | 2026-05-16 |
| U-IS-17 | IS substrate seam exports manifest (terminal exporter — 6 seams) | C-IS-10 §10.1-§10.6 | ✅ landed | `feat(is): land U-IS-17` | 2026-05-16 |
| U-AS-12 | Operator-policy override scope per persona-tier (`override_scope`, `OverrideScopeResult`) | C-AS-09 §9.4 | ✅ landed | `feat(as): land U-AS-12` | 2026-05-16 |
| U-AS-20 | `fetch_secret` 3-param + `SecretRef` opaque + `SecretScope` + 4-row tier-resolution table | C-AS-05 §5.1-§5.2,§5.4 | ✅ landed | `feat(as): land U-AS-20` | 2026-05-16 |
| U-AS-28 | Eleven-primitive `AnthropicPrimitive` enum + 44-cell adoption-depth matrix + cross-axis IS path-contract binding | C-AS-13 §13.1-§13.2 | ✅ landed | `feat(as): land U-AS-28` | 2026-05-16 |
| U-AS-07 | `ToolContract` schema + `RawContractInput` + `SecretAllowlistEntry` carrier + registration validator | C-AS-03 §3.1-§3.3 | ✅ landed | `feat(as): land U-AS-07` | 2026-05-16 |
| U-AS-06 | `sandbox_tier_floor` 10-row 5-arg lookup + `ToolMetadata` + `MCPServer` carriers + REFUSE sentinel | C-AS-02 §2.3 | ✅ landed | `feat(as): land U-AS-06` | 2026-05-16 |

**IS axis stream COMPLETE — 17/17 units landed 2026-05-16.** U-IS-17 is the terminal aggregate exporter.

## Operational-minimum set (7a exit-criterion #1 — 12 units)

U-IS-01 ✅ · U-IS-02 ✅ · U-IS-03 ✅ · U-IS-04 ✅ · U-AS-01 ✅ · U-AS-02 ✅ ·
U-AS-03 ✅ · U-AS-04 ✅ · U-CP-15 ✅ · U-CP-22 ✅ · U-OD-01 ✅ · U-OD-04 ✅

**✅ 12 of 12 operational-minimum units landed (2026-05-15).** 7a exit-criterion
#1 met. Final two: U-OD-04 (against conformed OD plan v2.5) and U-CP-22 (against
CP plan v2.5 — after Tension 002 vocabulary conformance + Tension 003 resolution).
Tension 003 resolved by adding foundational unit **U-CP-00** (`WorkloadClass` in
`harness-core`), landed as the unblocking dependency. Operator authorized
land-now without v2.4/v2.5 pre-implementation re-clearance.

## Spec tensions

| Record | Tension | Status |
|---|---|---|
| `Phase_7_Class_3_Tension_001_Git_Tier_Sub_Role_Count.md` | C-IS-03 §3 "four" vs 5 rows | ✅ resolved — spec fixed in-CLI; block cleared |
| `Phase_7_Class_1_Tension_002_Topology_Pattern_Enum.md` | TopologyPattern enum 3-way divergence | ✅ resolved 2026-05-15 — operator signed off Set 2 (spec C-CP-10 §10.1); CP-AL-1 conformed at 4 loci; commit `45f104f` |
| `class_1_tension_u_core_01_workflow_event.md` | U-CORE-01 `WorkflowEvent` payload model unmaterializable as a `harness-core` carrier type | ✅ resolved 2026-05-15 — operator ruled carrier-thin; payload model struck; harness-core plan v1.0→v1.1; U-CORE-01 landed without it |
| `class_1_tension_u_od_00_carrier_defects.md` | U-OD-00 §3.0 three carrier defects — SignatureAlgorithm cycle (D-1), missing CellID edge / false L0 (D-2), AuditSignatureAttributes un-spec'd field (D-3) | ✅ resolved 2026-05-15 — operator ruled micro-revise; OD plan v2.6→v2.7; U-OD-00 landed against v2.7 |
| `class_1_tension_u_cp_00b_structured_types.md` | U-CP-00b bundled 9 structured shared types declared name-only (no shapes at plan grade) | ⚠️ resolved-split 2026-05-15 — operator ruled split; CP plan v2.6→v2.7; U-CP-00b landed as the 2-enum carrier. **OPEN:** the 9 structured types await a future CP plan revision specifying each shape |
| `Phase_7_Class_1_Tension_003_WorkloadClass_Undeclared.md` | `WorkloadClass` type used by ~10 CP units, declared by none | 🛑 OPEN 2026-05-15 — U-CP-22 halted; plan-gap (missing declaring unit) |
| `Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` | U-OD-04 plan signature diverges from spec C-OD-04 at 4 points | 🛑 OPEN 2026-05-15 — U-OD-04 halted; subsumed into the OD-plan systemic audit below |

## Systemic finding — Phase-6 plan "verbatim"-claim divergence (2026-05-15)

Plan-wide adversarial audit (`harness-adversarial-reviewer` Phase-7 mode) found
the Tension-002/004 shape — plan units claiming "per §X verbatim" against
signatures that diverge from the cited spec — is **systemic across the CP + OD
plans**. The two audit reports are the canonical systemic-tension records
(supersede the per-unit Tension 002/004 framing; no further per-unit records filed).

| Audit report | Divergent units | Resolution |
|---|---|---|
| `.harness/verbatim_audit_cp_plan.md` | 7: U-CP-01, U-CP-10, U-CP-19, U-CP-22, U-CP-43, U-CP-46, U-CP-47 (+ borderline U-CP-11) | one CP-plan revision-pass — conform to spec |
| `.harness/verbatim_audit_od_plan.md` | 10: U-OD-02, U-OD-04, U-OD-09, U-OD-11, U-OD-12, U-OD-14, U-OD-28, U-OD-30, U-OD-32, U-OD-33 | one OD-plan revision-pass — conform to spec |
| `.harness/adversarial_review_phase7_cp_od_preimpl.md` | U-CP-22 + U-OD-04 pre-impl review (F3-01, F1-02 CLAUDE.md §2.2 mislabel) | feeds the two passes above |

**17 units total**, all §4.1 Class 3 / §2.7.6 Class 1. All authority-chain-
determinate (spec canonical per CLAUDE.md §1.3 — conform the plan) **except**
Tension 003 (`WorkloadClass` residence — genuinely non-determinate, needs operator).
Meta-finding: the Phase-6 plans were P6-CK-cleared yet carry 17 plan-vs-spec
divergences → P6-CK process gap (verbatim-claim check was not run at checkpoint).
Filed: `.harness/finding_p6ck_verbatim_check_gap.md`.

## §4A conformance — systems-architect recommendations + implementation-planner revision-pass (2026-05-15)

- `systems-architect` §4A: two per-axis resolution recommendations appended to
  the audit reports (conform plan to spec — authority-chain-determinate).
  **Operator-accepted.**
- `implementation-planner` revision-pass: **CP v2.4** + **OD v2.5** authored
  (commit after `3209254`). Determinate cluster conformed — 7 CP units + 3
  consumers, 9 OD units. U-CP-22 + U-OD-04 cleanly conformed (verified vs spec).
- **New findings surfaced during conformance** (not in the original audit;
  carried, not absorbed): U-CP-43 input-set divergence + `MCP_TRUST` under-spec
  (extends carry list to 4); U-CP-46 coverage shrink (plan-invented `audit.gate.*`
  dissolved — orphans `composition_winner`); U-CP-23 pre-existing structural
  mismatch; OD compound-spec-row rendering judgment call.
- **Owed:** pre-implementation re-clearance of v2.4/v2.5 before U-CP-22 + U-OD-04
  land; disposition of the new findings + the 5 original flagged items
  (U-CP-08, U-CP-11, U-OD-09 acc#2, U-OD-28, U-OD-29).

## §5 AS axis-stream — Cluster L1 close (2026-05-16)

AS Level-1 cluster complete — U-AS-07, U-AS-12, U-AS-20, U-AS-28 landed; the
AS plan's entire L0+L1 is now covered (10/33 AS units). 5-dimension coherence
pass clean (atomicity / spec-traceability / dependency-awareness / impl-grade
detail / anti-pattern audit). 70/70 harness-as tests green; ruff + pyright
clean. state.jsonl hash-chain length 36.

**Class 3 informational observations (non-blocking, not filed as records):**
- **U-AS-12 plan dependency-declaration gap.** Plan `Depends on [U-AS-04]`
  omits `[U-AS-01]`, yet `BlastRadiusTier` (carried by U-AS-01) is the second
  component of the `proposed_cell` tuple input. U-AS-01 is an L0 unit
  transitively in-cone of every AS unit; the edge is trivially satisfied.
  Documented in the `operator_policy_override_scope.py` docstring.
- **U-AS-28 surface-conditioned-cell materialization discretion.** §13.2 has 8
  surface-conditioned cells (Managed Agents + Files API rows) whose adoption
  depth varies by deployment surface; `AdoptionDepthBinding` carries one
  `depth`. Materialized as `depth` = managed-cloud reference-surface value,
  `notes` = verbatim §13.2 cell text, `surface_qualifier` = divergent surface.
  Full §13.2 content preserved in `notes`. Uses the binding's provided
  `notes` / `surface_qualifier` fields as intended — not a fork.
- **AS→IS package edge.** `harness-is` added to `harness-as` pyproject deps —
  first AS→IS package dependency (materializes the U-AS-28 plan-declared
  cross-axis IS edges; read-only consumption of the IS SKILLS path contract).

**Spec divergence checked + cleared:** AS plan v1.2 §0.6 action items A-1
(U-AS-04 re-point to harness-core) and A-5 (C-AS-05 §5.1 3-param `fetch_secret`
spec revision) are both already discharged — A-1 in the landed
`discriminators.py`, A-5 in AS spec v1.3 §5.1. The plan's stale caveats do not
block; no tension.
