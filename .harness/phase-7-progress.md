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

## Operational-minimum set (7a exit-criterion #1 — 12 units)

U-IS-01 ✅ · U-IS-02 ✅ · U-IS-03 ✅ · U-IS-04 ✅ · U-AS-01 ✅ · U-AS-02 ✅ ·
U-AS-03 ✅ · U-AS-04 ✅ · U-CP-15 ✅ · U-CP-22 🛑 · U-OD-01 ✅ · U-OD-04 🛑

**10 of 12 operational-minimum units landed.** Remaining 2 both halted on
Class 1 plan-defect forks: U-CP-22 (Tension 003 — `WorkloadClass` undeclared);
U-OD-04 (Tension 004 — plan signature diverges from spec C-OD-04 at 4 points).
Both surfaced cleanly per X-AL-3; neither silently absorbed.

## Spec tensions

| Record | Tension | Status |
|---|---|---|
| `Phase_7_Class_3_Tension_001_Git_Tier_Sub_Role_Count.md` | C-IS-03 §3 "four" vs 5 rows | ✅ resolved — spec fixed in-CLI; block cleared |
| `Phase_7_Class_1_Tension_002_Topology_Pattern_Enum.md` | TopologyPattern enum 3-way divergence | ✅ resolved 2026-05-15 — operator signed off Set 2 (spec C-CP-10 §10.1); CP-AL-1 conformed at 4 loci; commit `45f104f` |
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
