# Cross-Axis Composition Document (v2.5)

*Delta over v2.4. v2.5 lands the operator-ratified **HITL gate composer arc** Q3 ratification per `.harness/class_1_tension_cp_20_hitl_gate_composer_underspec.md` recommendation block + ratification: one new genuine-typed-seam edge (CP→OD) at the existing §2.3.7 CP→OD bucket — U-CP-46 → U-OD-00 carrying the HITL gate response audit-write seam. The bucket grows from 1 → 2 canonical edges; aggregate 93 → 94; genuine 23 → 24. Only the sections enumerated in §0.2 are revised; every other section is preserved verbatim from `Cross_Axis_Composition_Document_v2_4.md`.*

## §0 Change note (v2.4 → v2.5)

### §0.1 Revision context — HITL gate composer Q3 ratification

Per operator ratification 2026-05-20 at `.harness/class_1_tension_cp_20_hitl_gate_composer_underspec.md` "Operator ratification (2026-05-20, same session)" section, Q3 ("Audit-ledger F2 write — shared converter or parallel?") ratified the **shared converter** disposition: HITL gate audit-write at the gate-response site reuses the `cp_audit_to_od_audit` converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` (HITL-canonical at origin per CP spec v1.9 §13.5.1 NOTE 5; sub-agent dispatch was the reuse via `response="approve"` convention).

The CXA v2.4 §2.3.7 CP→OD bucket grows from 1 canonical edge (existing U-CP-28 → U-OD-00 sub-agent dispatch) to 2 canonical edges (new at v2.5: U-CP-46 → U-OD-00 HITL gate response audit-write). Both seams share the converter; the discriminator between source events at OD audit-trace consumers is the F2-entry action_id prefix (`dispatch:` vs `hitl:`) per `Spec_Harness_Runtime_v1.md` v1.9 §14.8.2 step 4h-HITL substep 8b.

### §0.2 Sections revised

§0 (this change note); §2.1 (matrix — CP→OD 1 → 2; aggregate 93 → 94; genuine 23 → 24); §2.3.7 (existing bucket grown 1 → 2 — new row appended for U-CP-46 → U-OD-00); §2.4 (posture summary — CP outbound 56 → 57, genuine 15 → 16; aggregate genuine 23 → 24). All other sections preserved verbatim from v2.4.

### §0.3 Precedent — second typed seam at the CP→OD bucket

The new edge U-CP-46 → U-OD-00 is the **second** CXA-enumerated edge at the CP→OD bucket. Per v2.4 §0.3, the first edge (U-CP-28 → U-OD-00) established the precedent that cross-axis-composition-seam converters homed at `harness-cxa/` are classified **G** (genuine-typed-seam) when the contract references a typed cross-axis output. v2.5 preserves that precedent: the new edge also classifies as **G** because:

- The contract at CP spec v1.9 §13.5.1 NOTE 5 explicitly names OD `AuditLedgerEntry` as the converter's output type (HITL-canonical at origin).
- The new edge reuses the SAME physical converter (`cp_audit_to_od_audit`) at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` — no new converter module; the existing module handles both source-event types via the field-projection table and `response` field semantics.
- Per Q3 ratification analysis, the converter was HITL-canonical at origin; sub-agent dispatch was the reuse-via-convention. v2.5 surfaces the original-use-case-seam alongside the reuse-case-seam.

**Classification.** Both edges are **G** (genuine-typed-seam). The bucket grows 1 G → 2 G; no edges of class C / R / S in the CP→OD bucket at v2.5.

### §0.4 Aggregate reclassification matrix (v2.5 delta)

Snapshot 4 — post-v2.5 (added one G edge in CP→OD bucket; v2.4 → v2.5 column added):

| Bucket | v2.3 canonical | v2.4 canonical | v2.5 canonical | v2.3 genuine | v2.4 genuine | v2.5 genuine | v2.3 convention | v2.4 convention | v2.5 convention | v2.3 phase-2-runtime | v2.4 phase-2-runtime | v2.5 phase-2-runtime |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AS → IS (§2.3.1) | 11 | 11 | 11 | 7 | 7 | 7 | 3 | 3 | 3 | 1 | 1 | 1 |
| CP → IS (§2.3.2) | 37 | 37 | 37 | 9 | 9 | 9 | 11 | 11 | 11 | 17 | 17 | 17 |
| CP → AS (§2.3.3) | 18 | 18 | 18 | 5 | 5 | 5 | 13 | 13 | 13 | 0 | 0 | 0 |
| OD → IS (§2.3.4) | 4 | 4 | 4 | 0 | 0 | 0 | 2 | 2 | 2 | 2 | 2 | 2 |
| OD → AS (§2.3.5) | 10 | 10 | 10 | 1 | 1 | 1 | 8 | 8 | 8 | 1 | 1 | 1 |
| OD → CP (§2.3.6) | 12 | 12 | 12 | 0 | 0 | 0 | 9 | 9 | 9 | 3 | 3 | 3 |
| **CP → OD (§2.3.7)** | 0 | 1 | **2** | 0 | 1 | **2** | 0 | 0 | 0 | 0 | 0 | 0 |
| **Total** | **92** | **93** | **94** | **22** | **23** | **24** | **46** | **46** | **46** | **24** | **24** | **24** |

24 + 46 + 24 = 94. The v2.4 axis-level back-edge statement (the CP→OD edge introduces a back-direction dependency at axis granularity) is preserved + extended at v2.5: the same bucket grows; no new axis-level back-edge direction added. Per-unit acyclicity within CP and within OD remains unaffected — both new edges target U-OD-00, which has no outbound cross-axis edges (per `harness-od/CLAUDE.md` §1.1 + §2.2 invariant).

### §0.5 Authoring discipline

Scope: ONE new edge added per HITL gate composer arc Q3 ratification — no other reclassification; no other edge added or removed; no other section content changed. The HITL audit-write seam reuses the existing converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` per Q3 ratification (no new converter module). Spurious strikes from v2.3 + producer-attribution corrections from v2.3 preserved at v2.4 + v2.5. Per-edge evidence at the contract (CP spec v1.9 §13.5.1 NOTE 5 + runtime spec v1.9 §14.8.2 step 4h-HITL + this v2.5 amendment).

---

## §2 Cross-axis adjacency matrix — REVISED

### §2.1 Aggregate 4×4 adjacency matrix — REVISED (CP→OD bucket grown 1 → 2)

Total cross-axis relationships per bucket (spurious struck):

| Source ↓ / Target → | IS | AS | CP | OD |
|---|---|---|---|---|
| **IS** | *(self)* | 0 | 0 | 0 |
| **AS** | 11 | *(self)* | 0 | 0 |
| **CP** | 37 | 18 | *(self)* | **2 (v2.5)** |
| **OD** | 4 | 10 | 12 | *(self)* |

**94 canonical cross-axis relationships** (93 at v2.4 + 1 new CP→OD genuine-typed-seam edge at v2.5). Genuine typed seams within that: **24** (23 at v2.4 + 1). Convention-level: **46** (unchanged from v2.4). Phase-2-runtime: **24** (unchanged from v2.4). 24 + 46 + 24 = 94.

### §2.2 Axis-level dependency graph — preserved verbatim from v2.4

The §2.2 ASCII graph at v2.4 (preserved from v2.3 with the v2.4 back-edge added — **CP → OD (1)**) is now updated only in the edge label: **CP → OD (2)**. The back-direction dependency at axis granularity established at v2.4 is extended (same direction, increased edge count); no new axis-level back-edge direction added at v2.5. Per-unit acyclicity within each axis is preserved; per-axis Kahn ordering within CP and within OD unaffected.

### §2.3 Per-bucket edge enumeration — §2.3.7 REVISED (new row appended); §2.3.1–§2.3.6 preserved verbatim from v2.4

§2.3.1 (AS→IS) — preserved verbatim from v2.4 (≡ verbatim from v2.3).
§2.3.2 (CP→IS) — preserved verbatim from v2.4 (≡ verbatim from v2.3).
§2.3.3 (CP→AS) — preserved verbatim from v2.4 (≡ verbatim from v2.3).
§2.3.4 (OD→IS) — preserved verbatim from v2.4 (≡ verbatim from v2.3).
§2.3.5 (OD→AS) — preserved verbatim from v2.4 (≡ verbatim from v2.3).
§2.3.6 (OD→CP) — preserved verbatim from v2.4 (≡ verbatim from v2.3).

#### §2.3.7 CP → OD (2 canonical) — REVISED v2.5 — evidence: `.harness/class_1_tension_cp_20_hitl_gate_composer_underspec.md`

| Consumer | Producer | Contract | Class |
|---|---|---|---|
| U-CP-28 | U-OD-00 | C-CP-13 §13.5.1 (v1.7+) | **G** — `AuditLedgerEntry` as converter output type at the CP-spec-anchored `cp_audit_to_od_audit` contract; sub-agent dispatch source event (CP→OD audit-write via `response="approve"` convention per CP spec v1.9 §13.5.1 NOTE 5). Physical import at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` per Q5 ratification (precedent — v2.4 §0.3). **(v2.4)** |
| **U-CP-46** | **U-OD-00** | **C-CP-16 §16.1–§16.4 + C-CP-20 §20.4/§20.5 + runtime spec v1.9 §14.8.2 step 4h-HITL** | **G — `AuditLedgerEntry` as converter output type at the same CP-spec-anchored `cp_audit_to_od_audit` contract (HITL gate response source event; the canonical use case per CP spec v1.9 §13.5.1 NOTE 5). Physical import at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` per Q3 ratification (shared converter). The HITL audit-write composes from C-CP-16 §16.2 4-row per-response audit-ledger entry table — operator response one of `{approve, edit, reject, respond}`; response-conditional optional hash fields populate per the operator's actual response. (NEW v2.5)** |

*Bucket note.* Both edges share the `cp_audit_to_od_audit` converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py`. The discriminator between source events at OD audit-trace consumers is the F2-entry `action_id` prefix: `dispatch:<parent_action_id>:<child_index>` for sub-agent dispatch source per `Spec_Harness_Runtime_v1.md` v1.9 §14.7.2 step 8b + `hitl:<parent_action_id>:<placement_position>` for HITL gate response source per `Spec_Harness_Runtime_v1.md` v1.9 §14.8.2 step 4h-HITL substep 8b. The `audit.cp.response` field value is NOT the discriminator — sub-agent dispatch populates `response="approve"` via convention; HITL gate populates `response` per the operator's actual response (one of `{approve, edit, reject, respond}`). The discriminator pattern is documented at CP spec v1.9 §13.5.1 NOTE 5 + runtime spec v1.9 §14.8.6.

*Edge note (v2.4 row).* The v2.4 row's runtime materialization (un-strike U-RT-59 AC #9 write half + composer step 8 F2-write + audit-write composition at the dispatch composer) landed at the U-RT-59 implementation arc (2026-05-20 per `[[fork-u-rt-59-cp-to-od-audit-write-gap]]`). The seam is operational at HEAD `2a15504`.

*Edge note (v2.5 row).* The v2.5 row's runtime materialization (composer step 4h-HITL F2-write + audit-write composition at the HITL gate composer) is owed to the U-RT-60 implementation arc (next session per `phase-7-implementation` skill discipline against `Spec_Harness_Runtime_v1.md` v1.9 §14.8 C-RT-18). The contract anchors at v2.5 same-session co-published with runtime spec v1.9 + the operator-ratified fork record.

### §2.4 Per-axis outbound posture summary — REVISED (CP outbound 56 → 57; genuine 15 → 16; aggregate genuine 23 → 24)

| Axis | Canonical outbound relationships | Genuine typed seams | Posture |
|---|---|---|---|
| IS | 0 | 0 | Pure foundational substrate |
| AS | 11 | 7 | Consumes IS; the 4 non-genuine are scheme-inheritance / descriptors / 1 runtime |
| CP | **57 (v2.5: +1 CP→OD HITL audit-write)** | **16 (v2.5: +1 CP→OD HITL audit-write)** | Largest consumer; v2.4-introduced CP→OD bucket grows to 2 typed seams at v2.5 — both target U-OD-00 audit ledger; both classified G per the converter-output-type precedent |
| OD | 26 | 1 | Consumer-most axis; built almost entirely as Pattern-P1 convention surfaces by design; the v2.5 expansion at CP→OD bucket targets U-OD-00 (audit ledger) which has 0 outbound cross-axis edges (invariant preserved) |
| **Aggregate** | **94** | **24** | — |

### §0.11 Promotion candidates (operator decision — NOT applied at v2.3, preserved at v2.4 + v2.5)

Two convention-level edges (preserved from v2.3 at v2.4 at v2.5) — non-Fork-2 + non-HITL surface, unchanged at v2.5:
- U-OD-26 → U-CP-47 (§2.3.6): could import `harness_cp...ValidatorFailClass`.
- U-OD-29 → U-AS-15 §12.4 arm (§2.3.5): could import `harness_as.cross_deployment_monotonicity`.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Cross_Axis_Composition_Document_v2_5.md` |
| Status | Canonical — Phase 7 sub-phase 7b/7c, HITL gate composer arc Q3 ratification landing |
| Predecessor | `Cross_Axis_Composition_Document_v2_4.md` (preserved verbatim except §0, §2.1, §2.3.7 row-append, §2.4) |
| Authored at | Phase 7 sub-phase 7b/7c, 2026-05-20 (in-CLI) |
| Co-published with | `Spec_Harness_Runtime_v1.md` v1.9 (§14.8 C-RT-18 — HITL gate composer contract) |
| Evidence base | `.harness/class_1_tension_cp_20_hitl_gate_composer_underspec.md` (Class 1 fork + systems-architect mode 3 recommendation + operator ratification); CP spec v1.9 §13.5.1 NOTE 5 (HITL-canonical at origin); `harness-cxa/src/harness_cxa/cp_audit_conversion.py` (shared converter implementation) |
| Net effect | 93 → 94 canonical cross-axis relationships (+1 G); 23 → 24 genuine typed seams (+1); 46 convention-level + 24 phase-2-runtime unchanged. Existing bucket CP→OD = 2 G (grown from 1 G at v2.4). |
| Deferred | (a) U-RT-60 implementation arc (next session per `phase-7-implementation` discipline against runtime spec v1.9 §14.8); (b) `harness-cp/CLAUDE.md` §2.3 CP→OD outbound edge-count update (0 → 1 → 2; current row cites v2.4 — needs v2.5 absorption); (c) `harness-od/CLAUDE.md` §2.2 inbound row update (1 → 2 inbound from CP); (d) workspace `CLAUDE.md` §2.4 CXA row update (`Cross_Axis_Composition_Document_v2_4.md` → `_v2_5.md`); (e) implementation-planner skill arc for U-RT-60 (runtime plan v2.6 → v2.7) |
| Next gate | (a) implementation-planner skill opens U-RT-60 at runtime plan v2.6 → v2.7; (b) phase-7-implementation skill lands U-RT-60 per the C-RT-18 acceptance criteria; (c) phase-7-substitution-retirement skill files Phase 7d batch 8 retirement event (H_T-CP-20 RETIRED) at landing |
| Authority chain compliance | ADR (D1 v1.2 HITL primitive + D5 v1.3 placement) → ADD §3.1.4 → CP spec v1.9 §13.5.1 NOTE 5 (HITL-canonical at origin) + §16/17/18/20 (HITL palette + placement + matrix + audit/hitl-span schemas) → runtime spec v1.9 §14.8 (composer contract) → CXA v2.5 (this seam declaration) → runtime plan v2.7 + per-axis CLAUDE.md absorption (downstream). |

---

*End of CXA v2.5. v2.5 absorbs the HITL gate composer arc Q3 ratification; existing CP→OD bucket grown from 1 → 2 typed seams; both seams share the `cp_audit_to_od_audit` converter; the per-edge contract anchors at runtime spec v1.9 + CP spec v1.9.*
