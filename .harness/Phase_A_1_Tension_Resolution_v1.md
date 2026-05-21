# Phase A.1 — Class 1 Tension Resolution Record (Pattern-D Types + CP Unit Sequencing)

**Filed:** 2026-05-21 (Remaining-Work Closure Arc, Phase A sub-arc A.1)
**Skill:** `systems-architect` in **Phase-7 tension-resolution mode** (§4A)
**Resolution mode:** **CONFIRMATION-OF-PRIOR-RATIFICATION.** Both forks are materially RESOLVED at canonical artifact level; this record formalizes the confirmation and instructs Phase A.2 accordingly.
**Authority chain applied:** `CLAUDE.md` §1.3 (ADR → ADD → PRD → spec → plan → CXA).

---

## §1 Tension statements (precise)

### §1.1 Tension #1 — Pattern-D structured types

Phase 1 explore-agent report classified this as a BLOCKING Class 1 fork: 13 structured types lack spec field sets at `Spec_Control_Plane_v1_3.md`, blocking the 11-unit CP cluster.

Per `.harness/class_1_tension_cp_batch_blocked_units_2026_05_16.md` lines 1-22 (the original HALT header):

> **Status:** 🛑 HALT — 11 CP units in the v2.8 L1–L3 batch cannot be landed.
> **Filed:** 2026-05-16 (Phase 7 7b, CP axis-stream).
> ...
> Affected types: `ProposedAction`, `ActionKind`, `ActionPayload`, `FailedAttempt`, `Alternative`, `RetryHistory`, `RetryPolicy`, `RoleRoutingBinding`, `WorkloadRoutingOverride`, `InferenceRequest`, `AuditLedgerEntry` / `SignedAuditLedgerEntry`, `LeadAgentPlan`.

### §1.2 Tension #2 — CP unit sequencing for 11 blocked units

Phase 1 explore-agent report classified this as a BLOCKING Class 1 fork: U-CP-04/05/08/09/13/14/30/33/38/39/44 — 11 units halted via root causes A (Pattern-D), B (transitive on A), C (out-of-batch dep).

---

## §2 Authority-chain placement + verified resolution state

### §2.1 Pattern-D types — authority chain reading

| Artifact | Version | Treatment of Pattern-D types |
|---|---|---|
| ADR-D5 v1.4 (topology + cross-deployment monotonicity) | v1.4 (canonical) | Commits topology concepts; does NOT commit record-form field sets (faithful to F/D/I taxonomy: field-set commitment is derivative, not foundational) |
| `Spec_Control_Plane_v1_9.md` | v1.9 (canonical at HEAD) | Commits Pattern-D concepts at contract sections (C-CP-13 §13.1/§13.4 HandoffContext family; C-CP-16 §16.2 + C-CP-20 §20.4 CPAuditLedgerEntry / CPSignedAuditLedgerEntry; C-CP-03 §3.5 RetryPolicy; et al.) per faithful-FACTOR-OUT discriminator |
| `.harness/xal3_resolution_recommendations.md` | T2 verdict (operator-ratified 2026-05-16) | **27/27 X-AL-3 candidates → FACTOR-OUT verdict.** Class-1-halt framing dissolved into FACTOR-OUT. "Spec commits concept" is the discriminator: where the spec commits the concept, the plan may decompose into field sets without invoking X-AL-3 design extension. |
| `Implementation_Plan_Control_Plane_v2_9.md` | v2.9 (canonical Pattern-D landing) | **16 Pattern-D types specified** as faithful factor-outs of committing spec sections: `ProposedAction`, `ActionKind`, `ActionPayload`, `FailedAttempt`, `Alternative`, `RetryHistory`, `StateSummary`, `RetryPolicy`, `CPAuditLedgerEntry`, `CPSignedAuditLedgerEntry`, `LeadAgentPlan`, `VerifierResult`, `OverlayResolution`, `WebhookConfig`, `WebhookPayload`, `HITLInvocation`, `MaterialDiff`. `InferenceRequest` unified to `ProviderAgnosticPayload` (U-CP-00c carrier). 177 type references in 828 lines. |
| `.harness/class_1_tension_role_routing_binding_underspec.md` | RESOLVED 2026-05-16 | Operator ratified R-2/W-2 schemas for `RoleRoutingBinding` + `WorkloadRoutingOverride` (the 2 residual Pattern-D types not T2-covered); U-CP-04 `RoutingManifest` full-lands |
| `Implementation_Plan_Control_Plane_v2_10.md` | v2.10 (R-2/W-2 absorption) | 6 references absorbing the R-2/W-2 ratification |
| `Implementation_Plan_Control_Plane_v2_11.md – v2_14.md` | v2.11–v2.14 (deltas) | Multi-body deltas over v2.9 baseline; Pattern-D field sets compose through unchanged |
| `harness-cp/CLAUDE.md` §1.2 (canonical pointer) | v2.10 with v2.14 plan citations | `Implementation_Plan_Control_Plane_v2_10.md` pointer cites: *"`RoleRoutingBinding` / `WorkloadRoutingOverride` Class 1 RESOLVED — operator-ratified R-2/W-2 schemas; U-CP-04 `RoutingManifest` upgraded PARTIAL-LAND → FULL-LAND. No signature, contract, or DAG change since v2.6"* |
| `.harness/class_1_tension_cp_batch_blocked_units_2026_05_16.md` "Audit reconciliation 2026-05-20" footer | RESOLVED | *"33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN."* |

**Authority chain verdict:** The Pattern-D Class 1 halt is RESOLVED by operator-ratified T2 X-AL-3 FACTOR-OUT (xal3_resolution_recommendations.md) + RoleRoutingBinding/WorkloadRoutingOverride R-2/W-2 ratification, absorbed at CP plan v2.9 + v2.10 with full byte-exact field-set decomposition.

### §2.2 11-unit cluster sequencing — authority chain reading

Per `.harness/class_1_tension_cp_batch_blocked_units_2026_05_16.md` §"RESOLUTION — CP plan v2.9 (2026-05-16)" lines 77-91 (the in-record resolution table):

| Unit | v2.9 verdict (verbatim from record) |
|---|---|
| U-CP-04 | ⚠️ PARTIALLY UNBLOCKED → UPGRADED to FULL-LAND at v2.10 per R-2/W-2 |
| U-CP-05 | ✅ UNBLOCKED (transitive) |
| U-CP-08 | ✅ UNBLOCKED (transitive) |
| U-CP-09 | ✅ UNBLOCKED (transitive) |
| U-CP-13 | ✅ UNBLOCKED |
| U-CP-14 | ✅ UNBLOCKED |
| U-CP-30 | ✅ UNBLOCKED |
| U-CP-33 | ✅ UNBLOCKED |
| U-CP-38 | ✅ UNBLOCKED |
| U-CP-39 | ✅ UNBLOCKED (transitive) |
| U-CP-44 | ✅ UNBLOCKED |

**Authority chain verdict:** 11 of 11 units UNBLOCKED. Topological sort already encoded in CP plan v2.9–v2.14 dependency graph (per CP plan §3.4 Kahn execution: DAG acyclic; 58 units consumed; remaining edge set ∅). No fresh sequencing recommendation owed.

---

## §3 §2-discipline analysis (five-axis + boundary + ordering)

### §3.1 Five-axis decomposition

| Axis | Tension touches | Resolution location |
|---|---|---|
| Control plane | YES — all 13 Pattern-D types live in CP axis (HandoffContext family, audit-ledger, retry/breaker policy types, HITL types) | CP spec v1.9 (concepts) + CP plan v2.9 (field-set factor-outs) |
| Information substrate | NO direct touch | n/a |
| Action surface | NO direct touch | n/a |
| Operational discipline | INDIRECT — `CPAuditLedgerEntry` joins `OD AuditLedgerEntry` via CP→OD converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` (CXA v2.4 §2.3.7) | CP spec v1.9 §16 (CP-side); OD spec v1.7 §24 (OD-side); CXA v2.5 converter contract |
| Deployment surface | NO direct touch | n/a |

### §3.2 Probabilistic-deterministic boundary

Pattern-D types are deterministic-layer artifacts (typed schemas + invariants + cross-axis converters). No LLM-judgment boundary at issue. Boundary placement is unambiguous: schemas + invariants live deterministic-side; resolution does NOT shift any element across the boundary.

### §3.3 F/D/I decision ordering

Operator-ratified T2 verdict at `xal3_resolution_recommendations.md` is itself a **derivative** decision (D-level): it derives from the foundational F1–F5 / D1–D6 ADR commitments via the "spec commits concept; plan decomposes record form" discriminator. The ratification did NOT touch any F-ADR; it applied the F/D/I taxonomy to classify each X-AL-3 candidate. Pattern-D type field-set commitments are therefore **D-level absorptions**, not new architectural commitments — exactly what the T2 verdict ratifies.

### §3.4 Cross-axis verification

- CP→OD cross-axis seam (`CPAuditLedgerEntry` → `AuditLedgerEntry` converter): verified at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` per Q5 ratification (U-RT-59 Fork 2 Path B-revised-a, 2026-05-20). Pattern P1 byte-exact alignment preserved.
- CP→IS cross-axis seam (`HandoffContext.StateSummary.LedgerEntryRef` → IS state-ledger composition): verified at CP→IS wiring composers per CXA v2.5 §2.3.2.
- No silent cross-axis tension surfaced.

---

## §4 Resolution recommendation

### §4.1 Verdict

**BOTH forks are RESOLVED.** Phase A.2 must NOT re-author Pattern-D type field sets and must NOT author a fresh CP unit sequencing recommendation. Doing either would be:

- A **role violation** (re-litigating ratified D-level decisions; §4A.4 anti-pattern).
- A **silent absorption risk** (treating a stale record header as an authoritative tension surface; workspace `CLAUDE.md` §4.3 "the worst failure mode").

### §4.2 What Phase A.2 inherits (citation-ready)

Phase A.2 spec-writer pass inherits the following canonical state, byte-exact citable:

**Pattern-D field-set authority (use these citations at every Phase A.2 spec contract that references Pattern-D types):**

| Pattern-D type | Canonical authority |
|---|---|
| `ProposedAction` | CP plan v2.9 + CP spec v1.9 C-CP-13 §13.1 |
| `ActionKind` | CP plan v2.9 + CP spec v1.9 C-CP-13 §13.1 |
| `ActionPayload` | CP plan v2.9 + CP spec v1.9 C-CP-13 §13.1 |
| `FailedAttempt` | CP plan v2.9 + CP spec v1.9 C-CP-13 §13.1 |
| `Alternative` | CP plan v2.9 + CP spec v1.9 C-CP-13 §13.1 |
| `RetryHistory` | CP plan v2.9 + CP spec v1.9 C-CP-03 §3.5 |
| `RetryPolicy` | CP plan v2.9 + CP spec v1.9 C-CP-03 §3.5 |
| `RoleRoutingBinding` | CP plan v2.10 + class_1_tension_role_routing_binding_underspec.md R-2 schema |
| `WorkloadRoutingOverride` | CP plan v2.10 + class_1_tension_role_routing_binding_underspec.md W-2 schema |
| `InferenceRequest` | Unified to `ProviderAgnosticPayload` at U-CP-00c (CP plan v2.8) |
| `AuditLedgerEntry` (OD form) | OD spec v1.7 §24 (canonical) |
| `CPAuditLedgerEntry` (CP form) | CP plan v2.9 + CP spec v1.9 C-CP-16 §16.2 |
| `CPSignedAuditLedgerEntry` (CP form) | CP plan v2.9 + CP spec v1.9 C-CP-20 §20.4 |
| `LeadAgentPlan` | CP plan v2.9 — opaque `Mapping[str, Any]` faithful factor-out |
| `HandoffContext` | CP plan v2.9 + CP spec v1.9 C-CP-13 §13.1/§13.4 |

**CP unit sequencing authority:** CP plan v2.14 §3 cluster table + §3.1 DAG topology + §3.2 coverage matrix (Kahn-acyclic at 58 units). No fresh sequencing owed.

### §4.3 Downstream artifacts affected (what Phase A.2 SHOULD do)

1. **No spec-writer authoring** for Pattern-D type field sets. Citations to existing CP plan v2.9 / v2.10 sections are the production-ready substrate.
2. **The operator-ratified Phase A scope item** *"Pattern-D types: FULL formalization for all 13 types"* (from plan file §"Operator-ratified Phase A scope (locked)") is HEREBY MARKED **inherited-from-prior-ratification**, not new authoring. The plan file should be amended to reflect this clarification (Phase A.2 does not duplicate work that ratified resolutions already absorbed).
3. **Phase A.2 IS still required** for the 3 absent composer contracts (tool-invocation per Path X; HITL delivery + timeout-degradation + validator framework; per-server-trust evaluator + `mcp.*` namespace; LLM-dispatch is closed per Phase A.0). These composer contracts will CONSUME the inherited Pattern-D type field sets, but do not re-author them.

### §4.4 Drift items surfaced (for Phase A.3)

The following drift items are surfaced for Phase A.3 drift-reconciliation absorption (these are NOT blockers; they are book-keeping):

- **Drift D-A.1-01 — Stale tension-record headers:** The original "🛑 HALT" status lines at top of `class_1_tension_cp_batch_blocked_units_2026_05_16.md` line 3 + `class_1_tension_role_routing_binding_underspec.md` line 3 contradict their resolution footers + audit reconciliation. **Recommended absorption:** Phase A.3 amends each record's top-status to RESOLVED with footer reference. NOT an architectural defect — a record-hygiene drift.
- **Drift D-A.1-02 — Phase A scope wording:** Plan file `/Users/robertrhu/.claude/plans/begin-comprehensive-and-sharded-bird.md` §"Operator-ratified Phase A scope (locked)" item 2 reads *"Pattern-D types: FULL formalization for all 13 types"* — this phrasing implies fresh authoring is owed. Per §4.3 above, the formalization already exists. **Recommended absorption:** Phase A.3 amends the plan file scope item to read *"Pattern-D types: cite ratified field sets at CP plan v2.9 + v2.10; no fresh authoring"*. Operator awareness preserved.

---

## §5 Tiebreaker check

**Single verifiable fact that, if confirmed, makes this recommendation determinate:**

> Confirm CP plan v2.9 lines 1-828 contain 16 Pattern-D type sections with field-set decompositions (verified: 177 type references at grep count) AND `.harness/class_1_tension_role_routing_binding_underspec.md` line 30 reads `**Verified status:** RESOLVED` (verified: matches verbatim).

Both halves confirmed at this audit. **Recommendation is determinate.**

---

## §6 Fork classification (`Project_Workflow_v1_8.md` §2.7.6)

Per workflow §2.7.6 fork-class taxonomy:

- **Class 1 (halt-execution; design-phase revision required):** ❌ NO — both forks materially resolved at CP plan v2.9/v2.10; no design-phase artifact revision needed.
- **Class 2 (in-execution operator decision):** ❌ NO — operator already ratified T2 (xal3_resolution_recommendations.md) + R-2/W-2 (class_1_tension_role_routing_binding_underspec.md).
- **Class 3 (informational):** ✅ YES — the drift items D-A.1-01 and D-A.1-02 surface in §4.4 as record-hygiene + scope-wording absorptions for Phase A.3, non-blocking, no spec/plan change owed.

**Implication for Phase 7 sub-phase execution:** Sub-phase 7b/7c/7d execution is NOT halted by these forks. Phase A.2 proceeds with the canonical inherited Pattern-D substrate. Phase A.3 absorbs the 2 drift items as part of its 20-item reconciliation scope.

---

## §7 Operator sign-off marker

This recommendation touches no F-ADR, no CLAUDE.md anti-leakage rule, no spec contract field-set commitment beyond what is already ratified. Per `systems-architect` §4A.2 step 5: this is a **non-load-bearing recommendation** (it merely confirms prior ratification). **Operator sign-off is not required to proceed to Phase A.2** — but operator awareness of the Phase A scope-wording amendment (D-A.1-02) is owed and is folded into Phase A.3 absorption.

---

## §8 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/Phase_A_1_Tension_Resolution_v1.md` |
| Authored at | Phase A sub-arc A.1, Remaining-Work Closure Arc, 2026-05-21 |
| Authoring authority | Plan file `/Users/robertrhu/.claude/plans/begin-comprehensive-and-sharded-bird.md` Phase A.1 + `systems-architect` skill §4A tension-resolution mode |
| Recommendation | CONFIRMATION-OF-PRIOR-RATIFICATION; both forks materially RESOLVED at CP plan v2.9 (T2 X-AL-3 FACTOR-OUT, 16 types) + v2.10 (R-2/W-2, 2 types) |
| Tiebreaker confirmed | Yes — `class_1_tension_role_routing_binding_underspec.md` line 30 + CP plan v2.9 byte-exact field-set decompositions verified |
| Fork class | Class 3 (informational; record-hygiene + scope-wording drift items for Phase A.3) |
| Operator sign-off required | NO (non-load-bearing; merely confirms prior ratification) |
| Phase A.2 implication | Phase A.2 INHERITS Pattern-D field sets via citation; does NOT re-author. Phase A.2 scope retained for 3 absent composer contracts (tool-invocation per Path X; HITL delivery + validator framework; per-server-trust + `mcp.*`) per A.0 closure of LLM-dispatch C.2 fork |
| Phase A.3 implication | 2 new drift items (D-A.1-01 stale headers; D-A.1-02 plan-file scope-wording) added to A.3 reconciliation scope (now 22 items total) |
| Next sub-arc | Phase A.2 (composer contract authoring) — proceeds immediately; no halt |
