# Phase A.2 — Spec-Writer Authoring Log

**Filed:** 2026-05-21 (Remaining-Work Closure Arc, Phase A sub-arc A.2)
**Mode:** Spec-writer apply pass (DECIDED FIXES)
**Source of fix:** `.harness/Phase_A_2_Contract_Drafts_v1.md` (operator-ratified 2026-05-21)

---

## Artifacts edited (3)

### 1. `design-substrate/Spec_Harness_Runtime_v1.md` — v1.12 → v1.13

**Change-note prepended:** Yes (v1.12 → v1.13)
**Sections added:**
- §14.9 — C-RT-19 `RuntimeToolDispatcher` + `MCPClientHost` (7 subsections: §14.9.1 architectural surfaces; §14.9.2 invocation discipline; §14.9.3 lifecycle stage placement; §14.9.4 span emission; §14.9.5 failure-mode taxonomy — 8 new fail classes; §14.9.6 invariants; §14.9.7 deferred to impl discretion)
- §14.10 — C-RT-20 `WebhookDeliveryComposer` + `OperatorBurdenEvaluator` (6 subsections: §14.10.1 architectural surfaces; §14.10.2 lifecycle stage placement; §14.10.3 span emission; §14.10.4 failure-mode taxonomy — 3 new fail classes; §14.10.5 invariants; §14.10.6 deferred to impl discretion)

**Sections preserved verbatim:**
- §1 through §14.8 (including §14.8.3 workflow-initiation topology pin, §14.8.5 HITL span emission per C-CP-20 §20.5, §14.8.7 path-(ii) deferred NOTEs, all v1.12-v1.11 chain content)
- §15 spec-to-plan traceability (preserved; new units owed at Phase C implementation-planner pass)
- §16 open questions
- §17 / §17.1 coherence-pass content
- v1.12 + v1.11 + v1.10 + v1.9 + v1.8 + v1.7 + v1.6 + v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 change-note chain

**Intra-file back-references updated:** None required — new sections do not modify existing intra-file cross-references (§14.9 / §14.10 are leaves; §15 / §16 / §17 do not yet enumerate them — that's Phase C plan-writer absorption).

**Cross-file back-references flagged (NOT edited per spec-writer scope discipline):**
- `harness-runtime/CLAUDE.md` (if exists) — runtime spec version bump
- Workspace `CLAUDE.md` §2.3 runtime row version bump
- `Implementation_Plan_Harness_Runtime_v2.md` — new atomic units U-RT-63+ for §14.9 + §14.10 materialization (Phase C work)
- Memory `phase-7-bootstrap-status.md` — runtime spec version cite update

**Audit-checklist results:**
- Decided-fix check: ✅ exact draft content transcribed
- No-extension check: ✅ no commitments added beyond drafts; no "while we're here" fixes
- Verbatim round-trip: ✅ every fail-class name, attribute name, enum value matches drafts byte-exact
- Preservation: ✅ §1-§14.8 + §15-§17 preserved verbatim
- Version + change-note: ✅ v1.13 + change-note prepended
- Citation byte-exact: ✅ all citations resolve

---

### 2. `design-substrate/Spec_Control_Plane_v1_10.md` — NEW (v1.9 → v1.10)

**File pattern:** Delta-over-predecessor (matches v1.3 through v1.9 convention; full v1.9 substantive content NOT duplicated)

**Change-note:** Comprehensive v1.9 → v1.10 (top of file)

**Sections added (four amendment sites):**
- §17.4 — `hitl_gate` canonical signature materialization (extends existing C-CP-17 §17 surface; closes `harness-cp/src/harness_cp/hitl_placement.py:178` `NotImplementedError`)
- §25 — C-CP-25 `ValidatorFramework` (8 subsections: §25.1 canonical signatures; §25.2 field sets — `ValidatorOutcome` 5-class, `ValidatorFailClass` 5-class, `ValidatorResult`, `ValidatorEvaluation`, `HITLEscalationBrief`; §25.3 lifecycle stage placement; §25.4 invocation discipline — Decision 2.D3 RATIFIED "run every step (opt-out via no-op)"; §25.5 span emission; §25.6 failure-mode taxonomy — 2 new CP fail classes; §25.7 invariants; §25.8 deferred to impl discretion)
- §26 — C-CP-26 `PauseResumeProtocol` (7 subsections: §26.1 canonical signatures; §26.2 field sets — `PauseReason` 5-class, `PauseSnapshot`, `MaterialDiffPolicy` 3-class STRICT default per Decision 2.D7, `ResumeResult`; §26.3 lifecycle stage placement; §26.4 span emission; §26.5 failure-mode taxonomy — 3 new CP fail classes; §26.6 invariants — coexist with U-CP-56 per Decision 2.D6; §26.7 deferred to impl discretion)
- §27 — C-CP-27 `PerServerTrustEvaluator` + `MCPClientNamespaceEmitter` (7 subsections: §27.1 canonical signatures; §27.2 field sets — `MCPPrimitive` 4-class, `TrustEvaluation`, `TrustPolicy`, `TierDerivationRule` 3-class, `TrustDecisionReason` 6-class; §27.3 lifecycle stage placement; §27.4 span emission; §27.5 failure-mode taxonomy — 3 new CP fail classes; §27.6 invariants — ALLOW-with-tier-floor per Decision 3.D1 RATIFIED-WITH-EDIT; §27.7 deferred to impl discretion)

**Pattern-D inheritance change-note:** Yes — explicit citation table at change-note for all 15 Pattern-D types per Phase A.1 §4.2. NO re-authoring of field sets.

**Sections preserved verbatim from v1.9:**
- All C-CP-01 through C-CP-24 contract content (v1.9 path-(i) NOTE-form absorption preserved including §13.5.1 NEW NOTE 4 + NOTE 5 + NOTE 6)
- v1.9 + v1.8 + v1.7 + v1.6 + v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 change-note chain
- Field-projection table at §13.5.1 (no change)

**Intra-file back-references:**
- §27 cites C-CP-17 §17 + C-AS-12 + C-AS-14 §14.3 ✅
- §26 cites U-CP-56 (Path A-modified coexist) ✅
- §25 cites C-CP-16 §16.1 (4-response palette) + C-CP-19 §19.1 + C-RT-16 + C-RT-18 ✅
- §17.4 cites C-CP-16 §16.1 + C-RT-18 §14.8 (runtime spec composer body) ✅

**Cross-file back-references flagged:**
- Workspace `CLAUDE.md` §2.3 CP row version bump (v1.9 → v1.10)
- `harness-cp/CLAUDE.md` §1.2 + §4.1 retirement-table extensions (H_T-CP-18 / H_T-CP-21 / H_T-CP-22)
- `Implementation_Plan_Control_Plane_v2_14.md` (or successor) — new atomic units for §25 + §26 + §27 + §17.4
- Runtime spec v1.13 §14.9 cross-cite (§14.9.1 step 2 + step 7 ↔ §27)
- AS spec v1.4 cross-cite (§14.3 + §15 ↔ §27 + §14.9)
- CXA v2.5 → v2.6 (Phase A.4 deferred)
- Memory `phase-7-bootstrap-status.md` — CP spec version cite update

**Audit-checklist results:**
- Decided-fix check: ✅ exact draft content transcribed; ratified-with-edits (3.D1, 1.D4, 2.D3) all applied
- No-extension check: ✅ Pattern-D types cited by inheritance, not re-authored
- Verbatim round-trip: ✅ all enum values, fail-class names, attribute names match drafts byte-exact
- Preservation: ✅ v1.9 content untouched
- Version + change-note: ✅ v1.10 + comprehensive change-note
- Citation byte-exact: ✅

---

### 3. `design-substrate/Spec_Action_Surface_v1.md` — v1.3 → v1.4

**Change-note prepended:** Yes (v1.3 → v1.4)

**Sections added (two annotation-only sites):**
- C-AS-14 §14.3 producer-site reference note (documents CP spec v1.10 §27 `MCPClientNamespaceEmitter` ownership at H_T-as-MCP-client tool-invocation site)
- C-AS-15 §15 producer-site reference note (documents runtime spec v1.13 §14.9 C-RT-19 `RuntimeToolDispatcher` ownership at tool-invocation site)

**Scope discipline:** Pure annotation-only patch. NO field-set change. NO attribute-list change. NO new AS-AL rule. NO contract signature change.

**Sections preserved verbatim from v1.3:**
- C-AS-01 through C-AS-16 (all 16 contracts, v1.3 numbering)
- v1.3 + v1.2 + v1.1 + v1 change-note chain
- All status block fields except the new v1.3 → v1.4 row

**Header update:** `# Spec — Action Surface v1` → `# Spec — Action Surface v1.4` (line 1)

**Cross-file back-references flagged:**
- Workspace `CLAUDE.md` §2.3 AS row version bump (v1.3 → v1.4)
- `harness-as/CLAUDE.md` §1.2 + §4.1 retirement-table extensions (H_T-AS-2 / H_T-AS-4 / H_T-AS-5 / H_T-AS-8 transitions pending runtime spec v1.13 §14.9 implementation arc)
- Memory `phase-7-bootstrap-status.md` — AS spec version cite update

**Audit-checklist results:**
- Decided-fix check: ✅ documentary-only NOTEs as specified in drafts cross-draft section
- No-extension check: ✅ no AS-AL rule added; no field-set / attribute change
- Verbatim round-trip: ✅ producer-site reference notes match cross-draft X.D1 substrate
- Preservation: ✅ AS contract content untouched
- Version + change-note: ✅ v1.4 + change-note + status-block row + header
- Citation byte-exact: ✅

---

## Summary — fail classes added (14 total)

**Runtime spec (11):**
- §14.9 (8): `RT-FAIL-TOOL-CONTRACT-UNKNOWN`, `RT-FAIL-TOOL-INVOCATION-TRUST-VIOLATION`, `RT-FAIL-TOOL-INVOCATION-TIMEOUT`, `RT-FAIL-TOOL-INVOCATION-PROTOCOL-ERROR`, `RT-FAIL-TOOL-INVOCATION-SCHEMA-VIOLATION`, `RT-FAIL-MCP-HOST-STARTUP`, `RT-FAIL-MCP-HOST-UNREACHABLE`, `RT-FAIL-SANDBOX-TIER-FLOOR-VIOLATION`
- §14.10 (3): `RT-FAIL-HITL-WEBHOOK-DELIVERY-EXHAUSTED`, `RT-FAIL-HITL-WEBHOOK-SCHEMA-VIOLATION`, `RT-FAIL-HITL-OPERATOR-BURDEN-DEGRADATION-CONFLICT`

**CP spec (8):**
- §25 (2): `CP-FAIL-VALIDATOR-PERMANENT`, `CP-FAIL-VALIDATOR-OPERATOR-BURDEN-EXCEEDED`
- §26 (3): `CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION`, `CP-FAIL-RESUME-MATERIAL-DIFF-DETECTED`, `CP-FAIL-RESUME-OPERATOR-ARBITRATION-OWED`
- §27 (3): `CP-FAIL-TRUST-EVALUATION-EXPLICIT-DENY`, `CP-FAIL-TRUST-EVALUATION-TIER-FLOOR-VIOLATION`, `CP-FAIL-TRUST-EVALUATION-UNKNOWN-SERVER-TIER-FLOOR-VIOLATION`

**Total fail classes added:** 19 (runtime 11 + CP 8; spec-writer note said 19, draft prose said 11+8=19 — matches).

---

## Summary — spans added

**Runtime spec (9):**
- §14.9 (5): `tool.dispatch`, `sandbox.enter`, `mcp.tool.call`, `sandbox.violation`, `sandbox.exit`
- §14.10 (3): `hitl.webhook.deliver`, `hitl.webhook.attempt`, `hitl.operator_burden.evaluated`

**CP spec (7):**
- §25 (4): `validator.evaluate`, `validator.fail`, `validator.revalidation`, `validator.escalation`
- §26 (2): `pause.captured`, `resume.attempted`
- §27 (1): `mcp.trust.evaluate` (plus mutation of existing `mcp.tool.call` from §14.9.4)

**Total spans added:** 16

---

## Summary — enums added

| Spec | Enum | Members |
|---|---|---|
| Runtime | (no new enums; reuses `MCPTrustTier` from CP plan v2.8) | — |
| CP §25 | `ValidatorOutcome` | 5 (PASS, REVALIDATE, ESCALATE, PERMANENT_FAIL, OPERATOR_BURDEN_EXCEEDED) |
| CP §25 | `ValidatorFailClass` | 5 (SCHEMA_VIOLATION, SEMANTIC_INCONSISTENCY, SAFETY_POLICY, RESOURCE_CONSTRAINT, EXTERNAL_REJECTION) |
| CP §25 | `ValidatorNextAction` (deferred to impl) | 4 (PROCEED, RETRY, ESCALATE_HITL, ABORT) |
| CP §26 | `PauseReason` | 5 (EXPLICIT_OPERATOR, HITL_PENDING, VALIDATOR_ESCALATION, TIMEOUT_BOUNDARY, EXTERNAL_DEPENDENCY) |
| CP §26 | `MaterialDiffPolicy` | 3 (STRICT default, LENIENT, OPERATOR_ARBITRATE) |
| CP §27 | `MCPPrimitive` | 4 (TOOL, RESOURCE, PROMPT, SAMPLING) |
| CP §27 | `TierDerivationRule` | 3 (CONSERVATIVE, PROTOCOL_VERSION_TABLE, OPERATOR_HOOK) |
| CP §27 | `TrustDecisionReason` | 6 |

---

## Cross-file back-references flagged for Phase C implementation-planner

The spec-writer scope does NOT include plan-file edits. The following downstream absorptions are owed at Phase C:

| Plan file | Absorption owed |
|---|---|
| `Implementation_Plan_Harness_Runtime_v2.md` (or successor) | New atomic units U-RT-63+ materializing §14.9 (C-RT-19) + §14.10 (C-RT-20) — anticipated ~6-10 new units across `MCPClientHost` lifecycle, `RuntimeToolDispatcher` dispatch body, sandbox span emission integration, webhook composer, burden evaluator |
| `Implementation_Plan_Control_Plane_v2_14.md` (or successor) | New atomic units materializing §25 (C-CP-25 ValidatorFramework) + §26 (C-CP-26 PauseResumeProtocol) + §27 (C-CP-27 PerServerTrustEvaluator) + §17.4 (hitl_gate signature materialization) — anticipated ~12-18 new units |
| `Implementation_Plan_Action_Surface_v1_2.md` | NONE — AS spec v1.4 is annotation-only; producer-site is owned by runtime + CP spec contracts |
| `Cross_Axis_Composition_Document_v2_5.md` → v2.6 | Phase A.4 absorption: new CXA edges (tool-invocation → IS audit secret-fetch; tool-invocation → OD sandbox observability; ValidatorFramework → OD validator.* audit; PerServerTrust → OD mcp.trust audit) |
| Memory `phase-7-bootstrap-status.md` | Spec version cite updates: runtime v1.12 → v1.13; CP v1.9 → v1.10; AS v1.3 → v1.4 |
| Workspace `CLAUDE.md` §2.3 + §2.4 | Runtime/CP/AS row version bumps |
| `harness-cp/CLAUDE.md` §4.1 retirement table | H_T-CP-18 / H_T-CP-21 / H_T-CP-22 transition cells pending implementation arc landing |
| `harness-as/CLAUDE.md` §4.1 retirement table | H_T-AS-2 / H_T-AS-4 / H_T-AS-5 / H_T-AS-8 transition cells pending runtime spec v1.13 §14.9 implementation arc landing |

---

## Adjacent defects surfaced (not patched per FM-2 no-extension discipline)

None surfaced during the apply pass. The drafts file was internally consistent; the substrate-context Explore agent finding was citation-ready.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/Spec_Phase_A_2_Authoring_Log_v1.md` |
| Apply pass at | Phase A sub-arc A.2, Remaining-Work Closure Arc, 2026-05-21 |
| Mode | spec-writer apply pass (DECIDED FIXES) |
| Files edited | 3 (runtime / CP / AS specs) + this log |
| Version bumps | runtime v1.12 → v1.13; CP v1.9 → v1.10 (new file); AS v1.3 → v1.4 |
| Contracts added | 4 new (C-RT-19 + C-RT-20 + C-CP-25 + C-CP-26 + C-CP-27) + 1 extension (C-CP-17 §17.4) = 5 surfaces |
| Wait, count again | C-RT-19, C-RT-20, C-CP-25, C-CP-26, C-CP-27 = **5 NEW contracts** + 1 extension (C-CP-17 §17.4) = 6 surfaces |
| Fail classes added | 19 (11 runtime + 8 CP) |
| Spans added | 16 (9 runtime + 7 CP) |
| Enums added | 8 (1 reused from CP plan + 7 new across CP §25/§26/§27) |
| Pattern-D types | INHERITED by citation (15 types per Phase A.1 §4.2); 0 re-authored |
| Next sub-arc | Phase A.3 — drift reconciliation (22 items per Phase A.1 §4.4 + prior list) |
| Phase B readiness | Specs ready for adversarial review once Phase A.3 + A.4 + A.5 complete; OR adversarial review can run per-phase if operator prefers smaller batches |
