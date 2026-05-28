# Implementation Plan: Control Plane — v2.24 (delta over v2.23)

---

## Change-note (v2.23 → v2.24)

**Scope of revision.** Fidelity-pure citation-correction patch closing v2.23 §"Adjacent observations" finding (i) — `HITLEscalationBrief.fail_detail_hash` field-type follow-on consideration — as **CLOSED-at-self-version-v2.23** (per CP spec v1.19 §25.2.Y absorption at v2.23 U-CP-59 amendment) — AND finding (v) — workspace `CLAUDE.md` §2.4 CP plan row stale at v2.20 — as **CLOSED-at-workspace-CLAUDE.md-current-state** (per v2.23 row bump at workspace CLAUDE.md). Both v2.23 carries became stale at v2.23 own publication: (i) was inherited from v2.22 with "if (α) chosen at follow-on arc" framing, but v2.23 IS the arc that executed (α); (v) was inherited from v2.21/v2.22 with "row cites v2.20" framing, but workspace CLAUDE.md was already bumped at v2.23 publication. v2.24 corrects the carry-text disposition at the canonical-reading layer.

**Source of (i) closure.** CP spec v1.18 → v1.19 §25.2.Y NEW canonical-reading amendment widened `HITLEscalationBrief.fail_detail_hash: str` → `str | None = None` per operator-routed option (α) parallel widening (2026-05-25). CP plan v2.23 absorbed the (α) widening at U-CP-59 amendment per workspace CLAUDE.md narrative: *"v2.23 — Single-unit-body amendment at U-CP-59 absorbing CP spec v1.18 → v1.19 NEW §25.2.Y `HITLEscalationBrief.fail_detail_hash` Optional widening (option (α) parallel widening per operator routing decision 2026-05-25)."* Empirical verification at worktree HEAD: v2.23 U-CP-59 ACs include the field-type widening amendment.

**Source of (v) closure.** Workspace `CLAUDE.md` §2.4 CP plan row was bumped from v2.22 → v2.23 at the v2.23 publication arc 2026-05-25. Empirical verification at worktree HEAD via grep this session: `grep "Implementation_Plan_Control_Plane" CLAUDE.md` returns the v2.23 cite at the canonical row. The v2.23 carry framing "row cites v2.20 but canonical head is v2.21" is stale-as-described.

**Audit lineage.** v2.24 is the THIRD production application of workflow v1.9 §7.4.7.3 across the workspace carry-set sweep 2026-05-27 (operator-routed "run the sweep" arc post-workflow-v1.9 publication). v2.23 (i) + (v) surfaced as STALE per species 4 (authoring-time stale carry — both v2.23 carries inherited from v2.22 + carries that v2.23 itself resolved but did not refresh the carry-text disposition).

**Species classification.** Both (i) + (v) closures via species 4 (authoring-time stale carry) at workflow v1.9 §7.4.7.2. v2.23 was authored as an absorption arc executing the (α) widening at U-CP-59 + bumping the workspace CLAUDE.md row, but the inherited §"Adjacent observations" carries (i) + (v) were preserved verbatim without refresh.

**No fork doc filed.** Per workspace precedent for fidelity-pure citation-correction patches anchored at conclusive empirical state (CP spec v1.19 §25.2.Y closure + workspace CLAUDE.md current state both verify the closures).

**Co-publication this session.** Sibling closure deltas at OD spec v1.22 + CXA v2.13 + OD plan v2.22. Workspace `CLAUDE.md` §2.4 CP plan row co-bumped. ZERO contract change; ZERO unit re-decomposition; ZERO AC change; ZERO DAG topology change.

---

## §1 Finding-closure-disposition refresh

### §1.1 v2.23 §"Adjacent observations" finding (i) — CLOSED

**Carry-text at v2.23.** *"(i) `HITLEscalationBrief.fail_detail_hash` field-type follow-on consideration. Per CP spec v1.18 adjacent defect (i): `fail_detail_hash: str` at v1.10 §25.2 is non-Optional but at durable-async cell HITL pause-trigger callsite there is no fail reason (no validator outcome at construction site). Three resolution options enumerated at CP spec v1.18 adjacent defect (i) — (α) widen `fail_detail_hash: str | None = None` parallel to v1.18 `fail_class` amendment; (β) synthesize sentinel value at runtime-side per U-RT-93 fixture posture `"0"*64`; (γ) split HITLEscalationBrief into two carriers. v2.22 absorbs (β) at U-RT-93 fixture continuation ... If (α) is chosen at a follow-on spec-extension arc, plan absorption at U-CP-59 is structurally identical to the v2.22 U-CP-59 amendment shape. Surfaced; routed to follow-on operator-discretion arc."*

**Disposition at v2.24.** **CLOSED-at-self-version-v2.23** (per CP spec v1.19 §25.2.Y absorption). The (α) widening was chosen at CP spec v1.19 publication 2026-05-25 (operator-routed). CP plan v2.23 IS the absorption arc that executed (α) at U-CP-59 — workspace CLAUDE.md narrative explicitly states: *"v2.23 — Single-unit-body amendment at U-CP-59 absorbing CP spec v1.18 → v1.19 NEW §25.2.Y `HITLEscalationBrief.fail_detail_hash` Optional widening (option (α) parallel widening per operator routing decision 2026-05-25)."* The v2.23 carry framing "if (α) is chosen at a follow-on spec-extension arc, plan absorption at U-CP-59 is structurally identical" describes a future-conditional state that became unconditional at v2.23 publication. The sentinel value (β) at runtime composer is dropped post-v2.23.

### §1.2 v2.23 §"Adjacent observations" finding (v) — CLOSED

**Carry-text at v2.23.** *"(v) Workspace `CLAUDE.md` §2.4 CP plan row stale at v2.20. Empirical-verification at session resume: workspace `CLAUDE.md` §2.4 CP plan row cites v2.20 but the canonical head is v2.21 (this session's predecessor `Implementation_Plan_Control_Plane_v2_21.md`). v2.22 absorption at this session creates a 2-version-bump stale at the workspace `CLAUDE.md` row. Surfaced; routed to bookkeeping commit per Phase 4 step 11 of checkpoint plan. NOT patched at this implementation-planner revision-pass arc per FM-2 — workspace `CLAUDE.md` row maintenance is bookkeeping discipline, not plan-authoring scope."*

**Disposition at v2.24.** **CLOSED-at-workspace-CLAUDE.md-current-state** 2026-05-25 (v2.23 row bump arc). Empirical verification at worktree HEAD via grep this session: `grep "Implementation_Plan_Control_Plane" CLAUDE.md` returns the v2.23 cite at the canonical row. The v2.23 carry framing "row cites v2.20 but canonical head is v2.21; v2.22 absorption creates 2-version-bump stale" describes a pre-v2.23 state. v2.23 publication included the workspace CLAUDE.md row bump as bookkeeping co-publication; the stale-row condition was resolved at the same arc.

### §1.3 Disposition summary

| v2.23 carry | Closure event | Closure commit | Status at v2.24 |
|---|---|---|---|
| §"Adjacent observations" (i) | CP spec v1.19 §25.2.Y + v2.23 U-CP-59 absorption | v2.23 publication arc | **CLOSED** |
| §"Adjacent observations" (v) | Workspace CLAUDE.md §2.4 CP plan row bump | v2.23 publication arc | **CLOSED** |

Both carries removed from v2.24 §"Adjacent observations" carry-set. v2.23 file body PRESERVED VERBATIM per delta-only-plan-file convention; v2.24 §1 is the canonical-reading amendment for the disposition layer.

---

## §2 Cross-artifact cite-cascade disposition (v2.24 NEW)

| Artifact | Site | Disposition at v2.24 |
|---|---|---|
| `Spec_Control_Plane_v1_19.md` §25.2.Y | Canonical anchor for (α) widening | **NO change owed** — spec v1.19 IS the closure-evidence; v2.24 §1.1 cites it |
| `harness-cp/src/harness_cp/validator_framework_types.py:148` | Production `fail_detail_hash` annotation | **NO change owed** — production state already widened per CP spec v1.19 + v2.23 absorption |
| `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:985` | Production composer construction | **NO change owed** — runtime composer drops sentinel post-v2.23 absorption |
| Workspace `CLAUDE.md` §2.4 CP plan row narrative | v2.23 row narrative | **CO-PUBLISHED this arc** — bumped to v2.24 with closure narrative |
| Peer artifacts at design-substrate/ | NO closed-carry cite | NO change owed — verified via grep this session |

---

## §3 Sections preserved verbatim at v2.24

Per delta-only-plan-file convention + FM-2 no-extension discipline + fidelity-pure citation-correction scope, the v2.24 amendment touches ONLY §1 + §2 + §"Adjacent observations" refresh. The following sections are PRESERVED VERBATIM from v2.23:

- **U-CP-59 unit body** (authored at original v2.5 plan; v2.23 amendment for `fail_detail_hash` Optional widening preserved)
- **All v2.22 + earlier substantive content**
- **DAG topology + dependency edges** (preserved verbatim)

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **v2.23 finding (i) — CLOSED-at-self-version-v2.23 at v2.24 §1.1.** Removed from "Adjacent observations" carry.

(b) **v2.23 finding (v) — CLOSED-at-workspace-CLAUDE.md-current-state at v2.24 §1.2.** Removed from "Adjacent observations" carry.

(c) **v2.23 finding (ii) — Persona-tier sourcing mechanism at the resolver caller site.** Carried verbatim from v2.23. Implementer-discretion at the impl arc per FM-2. GENUINE per sweep audit. v2.24 does NOT touch this carry.

(d) **v2.23 finding (iii) — Backward-INcompatible signature change at `resolve_step_binding`.** Carried verbatim. AUTHORIZED at CP spec v1.17 (iv); plan-level AC #6 covers caller-site obligation generically. GENUINE per sweep audit. v2.24 does NOT touch this carry.

(e) **v2.23 finding (iv) — Cluster 10-CP-A consumer-side construction discipline (NEW post-v1.18 widening).** Carried verbatim. Consumer-side disambiguation pattern at U-CP-60/61 plan bodies routed to follow-on operator-discretion arc OR runtime-side U-RT-94 composer body landing per Phase 3 step 9. GENUINE per sweep audit. v2.24 does NOT touch this carry.

(f) **NEW at v2.24 — authoring-time-stale-carry-text-disposition pattern observation at the plan layer.** v2.23 (i) + (v) are textbook examples of workflow v1.9 §7.4.7.2 species 4 (authoring-time stale carry) at the CP plan layer: both carries inherited from v2.22 with carry-text framing describing pre-v2.23 state; v2.23 publication included the resolution (v2.23 (i) absorption at U-CP-59 + (v) workspace CLAUDE.md row bump) but did NOT refresh the carry-text disposition. The carry-text propagated unrefreshed because v2.23 was authored as a separate-arc absorption (CP spec v1.19 §25.2.Y absorption) without §"Adjacent observations" carry-set audit. Class 3 informational; NOT patched per FM-2; validates the v1.9 §7.4.7.3 audit discipline operationally at the plan-layer in addition to the spec-layer + CXA-layer + OD-plan-layer.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v2.24 (Fidelity-pure citation-correction patch closing v2.23 §"Adjacent observations" finding (i) `HITLEscalationBrief.fail_detail_hash` follow-on + finding (v) workspace CLAUDE.md §2.4 CP plan row stale — both as **CLOSED-at-self-version-v2.23** 2026-05-25; NEW §1 + §2 + §3; v2.23 + earlier files PRESERVED VERBATIM) |
| Trigger | Workflow v1.9 §7.4.7.3 sweep audit 2026-05-27 (operator-routed "run the sweep") |
| Supersedes | v2.23 §"Adjacent observations" (i) + (v) carry framings — superseded at v2.24 §1 closure |
| Scope of revision | NARROW: §1 finding-closure-disposition refresh + §2 cross-artifact cite-cascade. ZERO contract / signature / AC / DAG change. Co-publication: workspace CLAUDE.md CP plan row bump. |
| Cross-axis cascade | ZERO. |
| Authority anchor | CP spec v1.19 §25.2.Y publication + v2.23 U-CP-59 absorption + workspace CLAUDE.md §2.4 CP plan row state at HEAD |
| Predecessor | v2.23 (Single-unit-body amendment at U-CP-59 absorbing CP spec v1.18 → v1.19 §25.2.Y) |
| Successor | v2.25 (next operator-discretion arc — candidates: (c) persona-tier sourcing; (d) backward-INcompatible signature; (e) cluster 10-CP-A consumer-side construction discipline) |
| Sweep cohort | 4 of 4 closure deltas in 2026-05-27 sweep batch (siblings: OD spec v1.22 [authored], CXA v2.13 [authored], OD plan v2.22 [authored]) — SWEEP BATCH COMPLETE |
