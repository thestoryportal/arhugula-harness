# Cross-Axis Composition Document (v2.6)

*Delta over v2.5. v2.6 lands the operator-ratified **Phase A.2 composer arc** edges per `.harness/Phase_A_2_Contract_Drafts_v1.md` ratification + `.harness/Spec_Phase_A_2_Authoring_Log_v1.md` apply pass. Five new genuine-typed-seam edges land: 3 at the existing §2.3.7 CP→OD bucket (ValidatorFramework + PauseResumeProtocol + PerServerTrustEvaluator audit-writes) + 1 at the existing §2.3.7 CP→OD bucket (HITL webhook delivery — runtime-side composer, CP-axis-owned namespace) + 1 at the existing §2.3.7 CP→OD bucket (HITL operator-burden — runtime-side composer, CP-axis-owned namespace). The bucket grows 2 → 7 canonical edges; aggregate 94 → 99; genuine 24 → 29. Only the sections enumerated in §0.2 are revised; every other section is preserved verbatim from `Cross_Axis_Composition_Document_v2_5.md`.*

## §0 Change note (v2.5 → v2.6)

### §0.1 Revision context — Phase A.2 composer arc landings

Per operator ratification 2026-05-21 at `.harness/Phase_A_2_Contract_Drafts_v1.md` + apply pass `.harness/Spec_Phase_A_2_Authoring_Log_v1.md` (Remaining-Work Closure Arc, Phase A sub-arc A.2), five new composer contracts landed across runtime spec v1.13 + CP spec v1.10:

| Composer | Spec location | Namespace produced |
|---|---|---|
| C-RT-19 `RuntimeToolDispatcher` | Runtime spec v1.13 §14.9 | `sandbox.*` (per AS spec v1.4 §15) + `mcp.*` (per AS spec v1.4 §14.3 via MCPClientNamespaceEmitter) — these emit through existing AS→IS / AS→OD bucket entries; no new edge owed at AS→OD bucket (the producer-site reference notes added at AS spec v1.4 cover this) |
| C-RT-20 `WebhookDeliveryComposer` | Runtime spec v1.13 §14.10 | `hitl.webhook.*` (audit-write to OD audit ledger) — **NEW CP→OD edge** |
| C-RT-20 `OperatorBurdenEvaluator` | Runtime spec v1.13 §14.10 | `hitl.operator_burden.*` (audit-write to OD audit ledger) — **NEW CP→OD edge** |
| C-CP-25 `ValidatorFramework` | CP spec v1.10 §25 | `validator.*` (audit-write to OD audit ledger via escalation-brief flow) — **NEW CP→OD edge** |
| C-CP-26 `PauseResumeProtocol` | CP spec v1.10 §26 | `pause.*` + `resume.*` (audit-write to OD audit ledger) — **NEW CP→OD edge** |
| C-CP-27 `PerServerTrustEvaluator` | CP spec v1.10 §27 | `mcp.trust.*` (audit-write to OD audit ledger when `audit_required=true`) — **NEW CP→OD edge** |

The CXA v2.5 §2.3.7 CP→OD bucket grows from 2 canonical edges (existing U-CP-28 → U-OD-00 sub-agent dispatch + existing U-CP-46 → U-OD-00 HITL gate response) to 7 canonical edges (the 5 NEW above). All 5 NEW edges share the `cp_audit_to_od_audit` converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` via convention: each namespace populates `audit.cp.*` field-projection per the converter's input shape; OD-side canonical schemas at OD spec v1.8 §NN (owed at Phase A.5 sub-arc OD compound-irrelevance unblock — schemas authored co-publication-adjacent at the next sub-arc).

### §0.2 Sections revised

§0 (this change note); §2.1 (matrix — CP→OD 2 → 7; aggregate 94 → 99; genuine 24 → 29); §2.3.7 (existing bucket grown 2 → 7 — 5 new rows appended); §2.4 (posture summary — CP outbound 57 → 62, genuine 16 → 21; aggregate genuine 24 → 29). All other sections preserved verbatim from v2.5.

### §0.3 Edge classification — all 5 NEW edges are G (genuine-typed-seam)

Each new edge carries a typed CP-axis contract referencing OD `AuditLedgerEntry` as the converter output type. Per CXA v2.4 §0.3 + v2.5 §0.3 precedent, this classifies as **G** (genuine-typed-seam):

| New edge | CP-axis producer contract | OD-axis consumer | Classification rationale |
|---|---|---|---|
| WebhookDeliveryComposer → U-OD-00 | Runtime spec v1.13 §14.10 (HITL-webhook composer; CP-axis HITL surface per `harness-cp/CLAUDE.md` §1.4 "HITL primitive implementation = OD-axis owned schema; CP emits") | U-OD-00 AuditLedgerEntry | G — converter output type explicit in CP-axis HITL namespace |
| OperatorBurdenEvaluator → U-OD-00 | Runtime spec v1.13 §14.10 (operator-burden span aggregation; CP-axis HITL surface) | U-OD-00 AuditLedgerEntry | G — converter output type explicit in CP-axis HITL namespace |
| ValidatorFramework → U-OD-00 | CP spec v1.10 §25 (validator framework + escalation arc) | U-OD-00 AuditLedgerEntry | G — converter output type explicit at C-CP-25 §25.5 escalation span flow |
| PauseResumeProtocol → U-OD-00 | CP spec v1.10 §26 (pause snapshot + resume material-diff) | U-OD-00 AuditLedgerEntry | G — converter output type explicit at C-CP-26 §26.4 pause/resume audit emission |
| PerServerTrustEvaluator → U-OD-00 | CP spec v1.10 §27 (per-server-trust + mcp.trust.*) | U-OD-00 AuditLedgerEntry | G — converter output type explicit at C-CP-27 §27.4 (audit-required calls always emit `mcp.trust.evaluate` to audit) |

**Shared converter discipline.** All 5 new edges reuse the existing `cp_audit_to_od_audit` converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` per the v2.4 + v2.5 precedent (Q5 + Q3 ratifications). The discriminator between source events at OD audit-trace consumers is the F2-entry `action_id` prefix, extended to 7 patterns at v2.6:

| Source event | F2 action_id prefix | First introduced |
|---|---|---|
| Sub-agent dispatch | `dispatch:<parent_action_id>:<child_index>` | v2.4 §2.3.7 |
| HITL gate response | `hitl:<parent_action_id>:<placement_position>` | v2.5 §2.3.7 |
| Webhook delivery | `hitl_webhook:<parent_action_id>:<idempotency_key>` | **v2.6 §2.3.7** |
| Operator burden | `operator_burden:<workflow_id>:<window_end_epoch_ms>` | **v2.6 §2.3.7** |
| Validator escalation | `validator:<parent_action_id>:<fail_class>` | **v2.6 §2.3.7** |
| Pause/resume | `pause:<workflow_id>:<step_index>` and `resume:<workflow_id>:<step_index>` | **v2.6 §2.3.7** |
| Trust evaluation | `mcp_trust:<server_name>:<primitive_kind>` | **v2.6 §2.3.7** |

### §0.4 Aggregate reclassification matrix (v2.6 delta)

Snapshot 5 — post-v2.6 (added five G edges in CP→OD bucket):

| Bucket | v2.4 canonical | v2.5 canonical | v2.6 canonical | v2.4 genuine | v2.5 genuine | v2.6 genuine | convention | phase-2-runtime |
|---|---|---|---|---|---|---|---|---|
| AS → IS (§2.3.1) | 11 | 11 | 11 | 7 | 7 | 7 | 3 | 1 |
| CP → IS (§2.3.2) | 37 | 37 | 37 | 9 | 9 | 9 | 11 | 17 |
| CP → AS (§2.3.3) | 18 | 18 | 18 | 5 | 5 | 5 | 13 | 0 |
| OD → IS (§2.3.4) | 4 | 4 | 4 | 0 | 0 | 0 | 2 | 2 |
| OD → AS (§2.3.5) | 10 | 10 | 10 | 1 | 1 | 1 | 8 | 1 |
| OD → CP (§2.3.6) | 12 | 12 | 12 | 0 | 0 | 0 | 9 | 3 |
| **CP → OD (§2.3.7)** | 1 | 2 | **7** | 1 | 2 | **7** | 0 | 0 |
| **Total** | **93** | **94** | **99** | **23** | **24** | **29** | **46** | **24** |

29 + 46 + 24 = 99. The v2.4-introduced axis-level back-edge direction (CP→OD) is preserved + further extended at v2.6: same bucket grows; no new axis-level back-edge direction added. Per-unit acyclicity within CP and within OD remains unaffected — all five new edges target U-OD-00, which has no outbound cross-axis edges (per `harness-od/CLAUDE.md` §1.1 + §2.2 invariant). The OD-side canonical schemas for the new namespaces (`hitl.webhook.*`, `hitl.operator_burden.*`, `validator.*`, `pause.*`, `resume.*`, `mcp.trust.*`) are owed at Phase A.5 OD spec v1.8 sub-arc (`.harness/Phase_A_5_OD_Compound_Irrelevance_Unblock_v1.md` — owed at next sub-arc).

### §0.5 Authoring discipline

Scope: FIVE new edges added per Phase A.2 composer arc apply pass — no other reclassification; no other edge added or removed; no other section content changed. All five new edges reuse the existing `cp_audit_to_od_audit` converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` (no new converter module). Spurious strikes from v2.3 + producer-attribution corrections from v2.3 preserved at v2.4 + v2.5 + v2.6. Per-edge evidence at the contract (runtime spec v1.13 §14.9 + §14.10; CP spec v1.10 §25 + §26 + §27 + this v2.6 amendment).

**Forward-cite hygiene.** Each new edge cites the owed OD spec v1.8 section at the "OD canonical schema" column. These citations resolve byte-exact when Phase A.5 lands OD spec v1.8 §NN amendments. If A.5 changes the section numbering, this CXA v2.6 file requires a follow-on amendment row in §2.3.7 to update the citations.

---

## §2 Cross-axis adjacency matrix — REVISED

### §2.1 Aggregate 4×4 adjacency matrix — REVISED (CP→OD bucket grown 2 → 7)

Total cross-axis relationships per bucket (spurious struck):

| Source ↓ / Target → | IS | AS | CP | OD |
|---|---|---|---|---|
| **IS** | *(self)* | 0 | 0 | 0 |
| **AS** | 11 | *(self)* | 0 | 0 |
| **CP** | 37 | 18 | *(self)* | **7 (v2.6)** |
| **OD** | 4 | 10 | 12 | *(self)* |

**99 canonical cross-axis relationships** (94 at v2.5 + 5 new CP→OD genuine-typed-seam edges at v2.6). Genuine typed seams within that: **29** (24 at v2.5 + 5). Convention-level: **46** (unchanged). Phase-2-runtime: **24** (unchanged). 29 + 46 + 24 = 99.

### §2.2 Axis-level dependency graph — preserved verbatim from v2.5

The §2.2 ASCII graph at v2.5 (CP → OD (2)) is now updated only in the edge label: **CP → OD (7)**. The back-direction dependency at axis granularity established at v2.4 is further extended (same direction, increased edge count); no new axis-level back-edge direction added at v2.6.

### §2.3 Per-bucket edge enumeration — §2.3.7 REVISED (5 new rows appended); §2.3.1–§2.3.6 preserved verbatim from v2.5

§2.3.1 (AS→IS) — preserved verbatim from v2.5 (≡ verbatim from v2.4).
§2.3.2 (CP→IS) — preserved verbatim from v2.5.
§2.3.3 (CP→AS) — preserved verbatim from v2.5.
§2.3.4 (OD→IS) — preserved verbatim from v2.5.
§2.3.5 (OD→AS) — preserved verbatim from v2.5.
§2.3.6 (OD→CP) — preserved verbatim from v2.5.

#### §2.3.7 CP → OD (7 canonical) — REVISED v2.6 — evidence: `.harness/Spec_Phase_A_2_Authoring_Log_v1.md`

| Producer (CP-side) | Consumer (OD-side) | Contract | Class |
|---|---|---|---|
| U-CP-28 | U-OD-00 | C-CP-13 §13.5.1 (v1.7+) | **G** — `AuditLedgerEntry` as converter output type at the CP-spec-anchored `cp_audit_to_od_audit` contract; sub-agent dispatch source event. **(v2.4)** |
| U-CP-46 | U-OD-00 | C-CP-16 §16.1–§16.4 + C-CP-20 §20.4/§20.5 + runtime spec v1.9 §14.8.2 step 4h-HITL | **G** — `AuditLedgerEntry` as converter output type at the same CP-spec-anchored `cp_audit_to_od_audit` contract (HITL gate response source event; canonical use case). **(v2.5)** |
| **C-RT-20 §14.10 (WebhookDeliveryComposer)** | **U-OD-00** | **Runtime spec v1.13 §14.10.3 (hitl.webhook.deliver + hitl.webhook.attempt spans) + OD spec v1.8 §C-OD-32 (`hitl.webhook.*` 6-attribute namespace + WebhookDeliveryAuditPayload)** | **G — `AuditLedgerEntry` as converter output type at HITL-webhook delivery audit-write; share `cp_audit_to_od_audit` converter via `hitl_webhook:` action_id prefix discriminator; 1-row per-attempt audit shape includes `delivery_attempts` + `status_code` + `idempotency_key`. (NEW v2.6)** |
| **C-RT-20 §14.10 (OperatorBurdenEvaluator)** | **U-OD-00** | **Runtime spec v1.13 §14.10.3 (hitl.operator_burden.evaluated span) + OD spec v1.8 §C-OD-33 (`hitl.operator_burden.*` 4-attribute namespace + OperatorBurdenAuditPayload)** | **G — `AuditLedgerEntry` as converter output type at operator-burden audit-write (when `degrade=true`); share converter via `operator_burden:` action_id prefix discriminator; 1-row audit shape includes `cumulative_invocations` + `window_ms` + `persona_tier` + `degrade`. (NEW v2.6)** |
| **C-CP-25 §25 (ValidatorFramework)** | **U-OD-00** | **CP spec v1.10 §25.5 (validator.escalation span) + OD spec v1.8 §C-OD-29 (`validator.*` 11-attribute namespace across 4 span sites + ValidatorEscalationAuditPayload)** | **G — `AuditLedgerEntry` as converter output type at validator-escalation audit-write; share converter via `validator:` action_id prefix discriminator; 1-row audit shape includes `fail_class` + `fail_detail_hash` + `next_action` + `escalation_owed`. Linked to subsequent `hitl.gate.evaluated` span via parent-context propagation when escalation triggers HITL. (NEW v2.6)** |
| **C-CP-26 §26 (PauseResumeProtocol)** | **U-OD-00** | **CP spec v1.10 §26.4 (pause.captured + resume.attempted spans) + OD spec v1.8 §C-OD-30 (`pause.*` + `resume.*` 8-attribute namespace + PauseResumeAuditPayload)** | **G — `AuditLedgerEntry` as converter output type at pause/resume audit-write; share converter via `pause:` and `resume:` action_id prefix discriminators (two action_id patterns share the bucket row — one converter, two distinct audit-trail patterns at OD-side); 1-row audit shape includes `pause_reason` + `snapshot_hash` + `step_index` + `state_ledger_anchor` (pause path) OR `diff_detected` + `diff_summary_hash` + `diff_policy` + `outcome` (resume path). (NEW v2.6)** |
| **C-CP-27 §27 (PerServerTrustEvaluator)** | **U-OD-00** | **CP spec v1.10 §27.4 (mcp.trust.evaluate span; audit-required calls always tail-keep) + OD spec v1.8 §C-OD-31 (`mcp.trust.*` 5-attribute namespace + TrustEvaluationAuditPayload)** | **G — `AuditLedgerEntry` as converter output type at per-server-trust audit-write (always-emit when `audit_required=true`; per Decision 3.D1 RATIFIED, UNKNOWN_SERVER decisions always audit-required); share converter via `mcp_trust:` action_id prefix discriminator; 1-row audit shape includes `server_name` + `primitive_kind` + `decision_reason` + `audit_required` + `tier_evaluated`. (NEW v2.6)** |

*Bucket note.* All 7 edges share the `cp_audit_to_od_audit` converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py`. Discriminator at OD audit-trace consumers is the F2-entry `action_id` prefix (7 patterns per §0.3 table); the `audit.cp.response` field is NOT the discriminator (sub-agent dispatch populates `response="approve"` via convention; HITL gate populates per operator's actual response; the 5 new edges populate `response` per their domain-specific value semantics — webhook delivery sets `response="delivered"` or `response="failed"`; validator sets `response="permanent_fail"` or `response="operator_burden_exceeded"`; pause sets `response="paused"`; resume sets `response="resumed"` or `response="diff_detected"`; trust sets `response="permitted"` or `response="denied"`).

*Edge note (rows 3-7).* Runtime materialization of these 5 edges is owed to the Phase C implementation-planner pass + subsequent atomic-unit landings (anticipated ~6-10 runtime + ~12-18 CP atomic units per Phase A.2 authoring log). The contract anchors at v2.6 same-arc co-published with runtime spec v1.13 + CP spec v1.10 + AS spec v1.4. OD-side canonical schemas (`hitl.webhook.*`, `hitl.operator_burden.*`, `validator.*`, `pause.*`, `resume.*`, `mcp.trust.*` attribute sets + audit-row shapes) are owed at Phase A.5 OD spec v1.8.

### §2.4 Per-axis outbound posture summary — REVISED (CP outbound 57 → 62; genuine 16 → 21; aggregate genuine 24 → 29)

| Axis | Canonical outbound relationships | Genuine typed seams | Posture |
|---|---|---|---|
| IS | 0 | 0 | Pure foundational substrate |
| AS | 11 | 7 | Consumes IS; the 4 non-genuine are scheme-inheritance / descriptors / 1 runtime |
| CP | **62 (v2.6: +5 CP→OD)** | **21 (v2.6: +5 CP→OD)** | Largest consumer; v2.4-introduced CP→OD bucket grows to 7 typed seams at v2.6 — all 7 target U-OD-00 audit ledger; all classified G per the converter-output-type precedent. **Note:** 2 of the 5 new edges (rows 3-4 — WebhookDeliveryComposer + OperatorBurdenEvaluator) are runtime-spec composer surfaces emitting CP-axis-owned namespaces (`hitl.*` per `harness-cp/CLAUDE.md` §1.4); they are CP-axis-attributed by virtue of their canonical namespace ownership, not by source-file location |
| OD | 26 | 1 | Consumer-most axis; built almost entirely as Pattern-P1 convention surfaces by design; the v2.6 expansion at CP→OD bucket targets U-OD-00 (audit ledger) which has 0 outbound cross-axis edges (invariant preserved) |
| **Aggregate** | **99** | **29** | — |

### §0.11 Promotion candidates (operator decision — preserved at v2.6)

Two convention-level edges (preserved from v2.3 at v2.4 + v2.5 + v2.6) — non-Fork-2 + non-HITL surface, unchanged at v2.6:
- U-OD-26 → U-CP-47 (§2.3.6): could import `harness_cp...ValidatorFailClass`. **Note v2.6:** ValidatorFailClass is now formalized at CP spec v1.10 §25.2 — promotion candidate now has explicit type to import; promotion remains operator-decision.
- U-OD-29 → U-AS-15 §12.4 arm (§2.3.5): could import `harness_as.cross_deployment_monotonicity`.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Cross_Axis_Composition_Document_v2_6.md` |
| Status | Canonical — Phase 7 sub-phase 7b/7c, Phase A.2 composer arc apply pass + Phase A.4 CXA edge instantiation |
| Predecessor | `Cross_Axis_Composition_Document_v2_5.md` (preserved verbatim except §0, §2.1, §2.3.7 5-row-append, §2.4) |
| Authored at | Phase 7 sub-phase 7b/7c, Remaining-Work Closure Arc Phase A.4, 2026-05-21 (in-CLI) |
| Co-published with | `Spec_Harness_Runtime_v1.md` v1.13 (§14.9 + §14.10) + `Spec_Control_Plane_v1_10.md` (§25 + §26 + §27 + §17.4) + `Spec_Action_Surface_v1.md` v1.4 + `Spec_Phase_A_2_Authoring_Log_v1.md` |
| Evidence base | `.harness/Phase_A_2_Contract_Drafts_v1.md` (operator-ratified drafts) + `.harness/Spec_Phase_A_2_Authoring_Log_v1.md` (apply pass) |
| Net effect | 94 → 99 canonical cross-axis relationships (+5 G); 24 → 29 genuine typed seams (+5); 46 convention-level + 24 phase-2-runtime unchanged. Existing bucket CP→OD = 7 G (grown from 2 G at v2.5). |
| Deferred | (a) Phase A.5 OD spec v1.8 amendments — canonical schemas for `hitl.webhook.*`, `hitl.operator_burden.*`, `validator.*`, `pause.*`, `resume.*`, `mcp.trust.*` attribute sets; (b) `harness-cp/CLAUDE.md` §2.3 CP→OD outbound edge-count update (2 → 7); (c) `harness-od/CLAUDE.md` §2.2 inbound row update (2 → 7 inbound from CP); (d) workspace `CLAUDE.md` §2.4 CXA row update (v2.5 → v2.6); (e) implementation-planner skill arc for new runtime + CP atomic units at Phase C |
| Next gate | Phase A.5 OD compound-irrelevance unblock — lands OD spec v1.8 canonical schemas for the 6 new namespaces referenced at §2.3.7 rows 3-7 |
| Authority chain compliance | ADR-F1 v1.2 + ADR-F4 v1.1 + ADR-D2 v1.2 + ADR-D5 v1.4 + ADR-D6 v1.2 → ADD v1.3 → CP spec v1.10 §25/§26/§27 + runtime spec v1.13 §14.9/§14.10 + AS spec v1.4 §14.3/§15 producer-site notes → CXA v2.6 (this seam declaration) → OD spec v1.8 (Phase A.5 owed) + plan absorption (downstream at Phase C). |

---

*End of CXA v2.6. v2.6 absorbs the Phase A.2 composer arc apply pass; existing CP→OD bucket grown from 2 → 7 typed seams; all 7 seams share the `cp_audit_to_od_audit` converter; per-edge contract anchors at runtime spec v1.13 + CP spec v1.10 + OD spec v1.8 (owed at Phase A.5).*
