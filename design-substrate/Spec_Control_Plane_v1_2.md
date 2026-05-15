# Spec — Control Plane v1

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1.md` |
| Status | **Proposed** (v1.2 pending Phase 6 entry per `Project_Workflow_v1_2.md` §3.1); final-revision-pass post-P5-CK iter-2 close per `Project_Workflow_v1_2.md` §4.1.2 modified path; coherence pass preserved verbatim as v1 + v1.1 historical record per Change-note §"§[coherence pass] preservation discipline" |
| Date | 2026-05-13 |
| Phase | 5 — specification authoring (session 3 of 4–6) per `Project_Workflow_v1_2.md` §2.5 |
| Skill | `spec-writer` SKILL.md in Stage-3 final-specification mode per skill description |
| Axis | Control Plane (per `Phase_5_Entry_Handoff.md` §3.1 axis sequencing; OD-5-2.A re-application at session 3 entry — recommendation followed) |
| Source-set | `PRD_v1.0.md` §1 (R-CP-01 through R-CP-12); `Architectural_Design_Document_v1.md` v1.2 §2.1 + §2.3 + §3.1.1 + §3.1.2 + §3.1.3 + §5.1 + §5.2.1 + §5.2.3 + §5.3.2 + §5.3.3 + §6.3.1; `ADR-F1.md` v1.2 (§Decision + §Rationale + §Consequences + §"Permanent tensions engaged"); `ADR-F3.md` v1.1 (§Decision + §Rationale + §Consequences); `ADR-D1.md` v1.1 (§Decision + §1.1 + §1.1.1 + §1.2 + §1.3 + §1.4); `ADR-D4.md` v1.1 (§Decision + §1.1 + §1.2 + §1.3 + §1.4 + §1.5 + §1.6 + §1.7 + §1.8 + §1.9 + §1.10 + §1.11); `ADR-D5.md` v1.3 (§Decision + §1.1 + §1.2 + §1.3 + §1.3.1 + §1.3.2 + §1.4 + §1.4.1 + §1.5 + §1.5.1 + §1.5.2 + §1.6 + §1.7 + §1.8 + §1.9 + §1.10 + §1.10.1 + §1.11); `Persona_Document_v1.md` §X.y anchors inherited from PRD requirements; `Spec_Information_Substrate_v1.md` (cross-axis substrate at C-IS-05 + C-IS-06 + C-IS-07 + C-IS-10); `Spec_Action_Surface_v1.md` (cross-axis substrate at C-AS-04 + C-AS-11 + C-AS-12 + C-AS-13 + C-AS-15 + C-AS-16) |
| Entry authorization | `Phase_5_Session_3_Session_Prompt.md` §4 entry-gate verified 8/8; session-1 + session-2 specs filed and coherence-pass-passed |
| ODs applied | OD-5-1.A (per-axis multi-document) + OD-5-2.A (Control Plane confirmed per handoff §3.1; no divergence) + OD-5-3.A (as-needed council consultant; no escalation invoked at session 3) + OD-5-4.A (aggregate P5-CK at full close) |
| Exit gate | This spec filed at `/mnt/user-data/outputs/`; §[coherence pass] returns ✅ PASS at all five audit dimensions; `Phase_5_Session_4_Session_Prompt.md` authored at session close |
| Revision | v1 → v1.1 (P5-CK iter-1 close mechanical revision per modified `Project_Workflow_v1_2.md` §4.1.2 path — F-CP-01 alignment to OD/D6 canonical schema across §3.5, §5.1, §5.4, §24.1 (`breaker.*` → `harness.breaker.*`; `breaker.trip` → `breaker.tripped`; 4-attr → 7-attr schema per OD C-OD-07 §7.1 — `breaker.cause` + `breaker.cooldown_ms` dropped under canonical replacement); F-CP-03 front-matter `validator.*` → `validator.fail.*` rename at §Axis-declaration bullet 3; F-OD-01 CP-side narrative count harmonization at §Axis-grounding note + §24.1 preamble — operator selection B (11 namespaces; `routing.*` included); all other contracts preserved verbatim) |
| Revision date | 2026-05-13 |
| Revision | v1.1 → v1.2 (P5-CK iter-2 close final-revision-pass per modified `Project_Workflow_v1_2.md` §4.1.2 path — F-iter2-01 Path A §24.1 export table restructure into Sub-table A (six specialization-layer namespace rows) + Sub-table B (four F3-capability-floor lifecycle-event-attribute rows) + inheritance-composition note (`routing.*`) per OD-iter2-RP-1.A operator selection; §"ADR commitment(s) honored" rewrite acknowledging two-category D6 ingestion model; §24.1 preamble narrative reframed to "6 + 4 + 1" framing preserving operator F-OD-01.B 11-namespace count; §Axis-grounding note bullet 3 narrative alignment to two-category framing preserving the eleven-namespace enumeration; F-iter2-03 C-CP-13 §13.3 line 1082 ADR-D3 v1.1 → v1.2 body-citation bump per Pattern P2-PHASE-5 use-latest-version discipline (cited content materially unchanged at v1.2); all other contracts preserved verbatim) |
| Revision date | 2026-05-13 |

---

## Change-note (v1.1 → v1.2)

**Scope of revision.** Two-finding final revision pass clearing `Adversarial_Review_5_iter2.md` F-iter2-01 (Class 2 — CP §24.1 export-claim ↔ D6 §1.2 ingest-reality structural conflation across three composition paths) under OD-iter2-RP-1.A Path A operator selection, and `Adversarial_Review_5_iter2.md` F-iter2-03 / Pattern P2-PHASE-5 (Class 1 mechanical — body-citation drift `ADR-D3 v1.1` → `v1.2` at C-CP-13 §13.3 line 1082; cited content materially unchanged at D3 v1.2 per `P5-CK_Iteration_2_Close_Handoff.md` §3.5). Both resolutions applied at this single revision pass per `P5-CK_Iteration_2_Final_Revision_Pass_Session_Prompt.md` §5.1 Stage 1.

**F-iter2-01 Path A applied per operator OD-iter2-RP-1.A selection and `Adversarial_Review_5_iter2.md` §3.1.6 resolution path shape.** The CP §24.1 export table at v1.1 made a flat categorical claim ("eleven namespaces declared at Control Plane source contracts and exported for session 4 (D6 unified span schema) ingestion") that conflated three structurally distinct composition paths by which D6 consumes CP namespace exports. Path A restructures the export-table layer to surface the three composition paths explicitly while preserving the operator F-OD-01.B eleven-namespace count under a "6 + 4 + 1" framing:

1. **Sub-table A — Six specialization-layer namespaces ingested at D6 §1.2.** `engine.*` (CP source: C-CP-09 §9.1; D6 row: §1.2 row 9), `topology.*` (CP source: C-CP-14 §14.2; D6 row: §1.2 row 7 named `topology.fanout.*` per Reading-1 sub-tree interpretation accepted under OD-iter2-RP-2.A), `subagent.*` (CP source: C-CP-14 §14.2; D6 row: §1.2 row 8), `hitl.*` (CP source: C-CP-20 §20.6; D6 row: §1.2 row 6), `audit.*` (CP source: C-CP-20 §20.4; D6 row: §1.2 row 10), `validator.fail.*` (CP source: C-CP-21 §21.5; D6 row: §1.2 row 11). These six namespaces are the CP-source-attributed subset of D6 §1.2's 15-row specialization-layer namespace map per `Adversarial_Review_5_iter2.md` §3.1 evidence cite (a).

2. **Sub-table B — Four F3-capability-floor lifecycle-event-attribute namespaces ingested at D6 §1.2 lines 124–133 (F3 lifecycle event sub-tree, not specialization namespaces).** `fallback.*` (as `fallback.triggered` span event), `retry.*` (as `retry.attempt` span event), `lease.*` (as `lease.acquired` / `lease.released` span events), `harness.breaker.*` (as `breaker.tripped` span event with seven-attribute schema declared at D6 §1.2.1; substrate-anchored at `c9-reliability-recovery` SKILL.md per F2-16 closure, NOT CP-anchored — CP §3.5 narrates the namespace's deployment-side composition; D6 §1.2.1 enumerates the canonical attribute set). The `harness.breaker.*` row carries an explicit "substrate-sourced" annotation distinguishing its source-authority posture from the other three F3-lifecycle namespaces.

3. **Inheritance-composition note — One namespace not ingested at D6 §1.2 at all.** `routing.*` (4 attributes declared at C-CP-01 §1.4) inherits sampling from parent `llm.inference` span per OTel GenAI semconv 1.41.0; it is neither in D6 §1.2 specialization-layer map nor in the F3 lifecycle event set. The inheritance-composition note documents this third composition path explicitly.

**§"ADR commitment(s) honored" rewrite (line 2083).** The v1.1 commitment text claimed D6 ingests all eleven namespaces "from Control Plane source declarations" — a framing now superseded by the three-composition-path structure. The v1.2 commitment text distinguishes (i) six specialization-layer namespaces ingested at D6 §1.2 from CP source declarations, (ii) four F3-lifecycle-event-attribute namespaces ingested at D6 §1.2 lines 124–133 via the F3 capability-floor (iv) lifecycle event set (with `harness.breaker.*` substrate-anchored at `c9-reliability-recovery` SKILL.md per F2-16 closure, NOT CP-anchored), (iii) `routing.*` as CP-axis-only inheritance-composition not ingested at D6.

**§24.1 preamble narrative reframing (line 2091).** The v1.1 preamble used the framing "The following eleven namespaces are declared at Control Plane source contracts and exported for session 4 (D6 unified span schema) ingestion without re-declaration" — a flat categorical claim that conflated the three composition paths. The v1.2 preamble restates the export contract as "six specialization-layer namespaces + four F3-lifecycle-event-attribute namespaces + one inheritance-composition namespace" (6 + 4 + 1 = 11). The operator-selected F-OD-01.B eleven-namespace count is preserved under the new framing; the three-composition-path structure is now explicit at the export-table preamble layer.

**§Axis-grounding note bullet 3 (line 72) narrative alignment.** The v1.1 bullet enumerated the eleven namespaces as a flat set ("`engine.*`, `topology.*`, `subagent.*`, `hitl.*`, `audit.*`, `fallback.*`, `harness.breaker.*`, `retry.*`, `lease.*`, `validator.fail.*`, `routing.*`"). The v1.2 bullet retains the eleven-namespace enumeration but groups them by composition-path category (specialization-layer / F3-lifecycle-event-attribute / inheritance-composition) consistent with the §24.1 sub-table restructure. The eleven-namespace count is preserved.

**F-iter2-03 / Pattern P2-PHASE-5 mechanical bump applied per `P5-CK_Iteration_2_Close_Handoff.md` §3.3.** C-CP-13 §13.3 line 1082 body-citation `Spec_Action_Surface_v1.md C-AS-13 §13.4 + ADR-D3 v1.1 §1.4 brief-authoring NOT-reducible-to-Haiku clause` → `Spec_Action_Surface_v1.md C-AS-13 §13.4 + ADR-D3 v1.2 §1.4 brief-authoring NOT-reducible-to-Haiku clause`. Cited content materially unchanged at ADR-D3 v1.2 §1.4 (preserved verbatim from v1.1 per D3 v1.1 → v1.2 Change-note §"Sections preserved verbatim"); token-level alignment only per use-latest-version discipline.

**Forward-flagged out-of-scope discoveries (status update at v1.2).** The three v1.1 forward-flagged concerns are re-evaluated at this revision pass:

1. **Concern #1 (OD C-OD-09 cross-axis citation drift)** — CLOSED at OD spec v1.1 Stage 3c revision pass (already resolved post-iter-1 close).
2. **Concern #2 (F-CP-01 attribute semantic-loss re-evaluation: `breaker.cause` + `breaker.cooldown_ms` re-introduction)** — REMAINS FORWARD-FLAGGED (operator-discretionary, not iter-3-pending). Adjudicated as NOT-FINDING at iter-2 review §5.1 per OD-iter2-1.A independent judgment; any future re-introduction is an OD-side architectural change tracked as forward concern, not a P5-CK-iter-2-resolution-pending item.
3. **Concern #3 (CP §24.1 export table ↔ D6 §1.2 ingest map substrate-level alignment drift)** — CLOSED at this v1.2 revision pass under F-iter2-01 Path A. The forward-flag at v1.1 anticipated exactly the F-iter2-01 surfacing; Path A resolution at the CP-spec layer is the operator-selected mechanical alignment.

No new forward-flagged concerns surfaced at v1.2 restructure scope.

**Sections preserved verbatim at v1.2.** §Front-matter (Axis-declaration; PRD requirement scope; ADR commitment scope; cross-axis citation table; Deferred to implementation discretion; Axis-grounding note bullets 1 + 2 + paragraph 1 — only bullet 3 narrative aligned to two-category framing preserving the eleven-namespace enumeration); §2 C-CP-02 (per-layer attribution); §3 C-CP-03 §3.1, §3.2, §3.3, §3.4, §3.5 (all chain-advancement contracts; F-iter2-01 does not touch §3.5 namespace declaration — only the §24.1 export table); §3 C-CP-13 §13.1, §13.2 (brief object schema; brief-authoring context — only §13.3 line 1082 body-citation bumped); §13.4 + §13.5 + §13.6 (subsequent C-CP-13 sub-sections); §4 C-CP-04 through C-CP-04.x (cross-family fallback contracts); §5 C-CP-05 (all sub-sections; per-class minimum attribute set; `lease.*` namespace; sampling sub-section; composition with downstream namespaces); §6 through §17 (all D1-anchored + D4-anchored contracts at pre-§18); §18 C-CP-19 (two-agent-observer trigger / composition / per-persona-tier-binding contract; audit-composition); §19 through §22 (all D5-anchored contracts); §23 C-CP-23 (T-perm-3 three-layer composition; deterministic-outer-harness composition); §24 C-CP-24 §24.2, §24.3, §24.4 (cross-axis composition exports; cross-axis composition with session 5; Deferred to implementation discretion) — only §24.1 + §"ADR commitment(s) honored" amended; §[traceability] matrix (CP-side rows; D3 row updated to v1.2 if present per use-latest-version discipline); §[carry-forwards]; §[coherence pass] (preserved verbatim as v1 + v1.1 historical record per Stage 3b + iter-1 revision pass precedent).

**Status posture.** `Status: Proposed (v1.2 pending Phase 6 entry per Project_Workflow_v1_2.md §3.1)`. v1.2 enters Phase 6 entry-gate as a fully-resolved final-revision-pass artifact alongside IS spec v1.2 (Stage 2 output), OD spec v1.2 (Stage 3 output), and Workflow §7 revision (Stage 4 parallel output) per `P5-CK_Iteration_2_Final_Revision_Pass_Session_Prompt.md` §7.1.

**Changes inline.** Status block (Status row revised; second pair of Revision row + Revision date row appended for v1.1 → v1.2). This Change-note section (new; appended between Status block and previous Change-note v1 → v1.1). §Axis-grounding note bullet 3 at line 72 (eleven-namespace enumeration re-grouped under two-category framing). §13 C-CP-13 §13.3 line 1082 (`ADR-D3 v1.1` → `ADR-D3 v1.2` body-citation bump per Pattern P2-PHASE-5). §24 C-CP-24 ADR-commitment(s)-honored block at line 2083 (rewritten to acknowledge two-category D6 ingestion model + `routing.*` inheritance-composition + `harness.breaker.*` substrate-anchored citation). §24.1 preamble at line 2091 (reframed to "six specialization-layer + four F3-lifecycle-event-attribute + one inheritance-composition" framing; eleven-namespace count preserved). §24.1 export table at lines 2093–2105 (restructured into Sub-table A (six specialization-layer rows) + Sub-table B (four F3-lifecycle-event-attribute rows) + inheritance-composition note for `routing.*`). Five amendment sites total: one F-iter2-03 mechanical body-citation bump + four F-iter2-01 Path A sites (table restructure + ADR-commitments rewrite + preamble reframe + axis-grounding bullet 3 alignment). No other content modified.

**§[coherence pass] preservation discipline.** §[coherence pass] section at v1.2 is preserved verbatim as the v1 + v1.1 point-in-time audit historical record. Audit rows referencing v1 namespace state (`breaker.*` vs `harness.breaker.*` count; `breaker.trip` vs `breaker.tripped` naming; "ten" vs "eleven" count) and v1.1 substrate state (flat eleven-namespace export framing) are accurate historical record of those audit passes; v1.2 final-revision-pass mechanical restructure does not re-run the audit. Per `P5-CK_Iteration_2_Final_Revision_Pass_Session_Prompt.md` §5.2 §[coherence pass] preservation discipline.

---

## Change-note (v1 → v1.1)

**Scope of revision.** Three-finding revision pass clearing `Adversarial_Review_5.md` F-CP-01 (Class 2 — three concurrent drifts between CP `breaker.*` declaration and OD/D6 `harness.breaker.*` canonical declaration: namespace prefix, event-name verb, and attribute-set divergence), F-CP-03 (Class 1 — front-matter `validator.*` → `validator.fail.*` inline rename), and F-OD-01 CP-side half (Class 1 — CP namespace count narrative harmonization across §Axis-grounding note + §24.1 preamble per operator selection B = 11 namespaces with `routing.*` included). All three findings resolved at this single axis-spec revision pass per `P5-CK_Iteration_1_Close_Handoff.md` §3.2 + §3.3.

**F-CP-01 alignment to OD/D6 canonical schema applied per operator OD-RP-3 selection and `Adversarial_Review_5.md` §F-CP-01 §"Resolution path shape".** Three drifts resolved at six sites:

1. **Namespace prefix rename** — `breaker.*` → `harness.breaker.*` at C-CP-03 §3.5 section heading (line 325), §3.5 namespace table row (line 332), §5.1 event class table row (line 436), §Axis-grounding note bullet 3 (line 36), C-CP-24 §24.1 substrate seam table row (line 2071). Source authority: D6 v1.1 §1.2.1 substrate-anchored citation per Workflow v1.3 §2.3.3.1 clause (iii); OD C-OD-05 §5.1 row 14 + C-OD-07 §7.1 declare-and-ingest. The CP-side `breaker.*` was spec-introduced architecture not anchored to D6 §1.2.1; canonical alignment supersedes per F-CP-01 review.

2. **Event-name verb rename** — `breaker.trip` → `breaker.tripped` at C-CP-03 §3.5 sampling table (line 341), C-CP-05 §5.1 event class table (line 436), C-CP-05 §5.4 sampling table (line 469), C-CP-24 §24.1 substrate seam table (line 2071). Source authority: OD C-OD-09 §9.2 line 522 + ADR-D6 v1.1 §1.3 always-sampled discipline + ADR-F3 v1.1 capability-floor (iv) eight-event-class lifecycle (which names `breaker.tripped` at OD §6.1 line 378).

3. **Attribute set reconciliation** — 4-attribute set (`breaker.key`, `breaker.cause` ∈ {rate_limit, auth_failure, 5xx_streak, capability_shortfall}, `breaker.cooldown_ms`, `breaker.state` ∈ {closed, open, half_open}) replaced with 7-attribute canonical set per OD C-OD-07 §7.1: `harness.breaker.scope`, `harness.breaker.from_state`, `harness.breaker.to_state`, `harness.breaker.trigger_count`, `harness.breaker.permanent_fail_repeats`, `harness.breaker.tool_id`, `harness.breaker.model_version` at C-CP-03 §3.5 namespace row (line 332); attribute-count token updated at C-CP-24 §24.1 substrate seam table row (line 2071). **Semantic-loss note:** `breaker.cause` (trip-cause enum) and `breaker.cooldown_ms` (cooldown duration) are dropped under canonical replacement; no direct OD-side equivalent. The CP-side 4-attribute set described ambient breaker state; the OD-side 7-attribute set describes breaker-trip events (from-state → to-state transition with trigger metadata). Operator-acknowledged at §33.2 of Stage 3b session record. Re-introduction of these attributes (if desired) is an out-of-F-CP-01-scope OD-side architectural change tracked as forward concern, not this revision pass.

**F-CP-03 inline rename applied per operator confirmation.** §Axis declaration bullet 3 narrative at line 28 renamed `validator.*` → `validator.fail.*`. Aligns with the §Axis-grounding note enumeration at line 36 which already uses the canonical `validator.fail.*` form (the bullet-3 narrative drift was the pre-existing defect). Source authority: C-CP-21 §21.5 three-attribute declaration; OD C-OD-09 §9.2 reference at line 498.

**F-OD-01 CP-side half applied per operator selection B (11 namespaces; routing.* included).** §Axis-grounding note bullet 3 enumeration at line 36 extended from 10 namespaces to 11 by adding `routing.*` (declared at C-CP-01 §1.4 per substrate seam exports at C-CP-24 §24.1); §24.1 preamble narrative at line 2061 updated from "ten namespaces" to "eleven namespaces" — consistent with the §24.1 table which already enumerates 11 namespaces (engine, topology, subagent, hitl, audit, fallback, harness.breaker, retry, lease, validator.fail, routing). The preamble-table count drift was the pre-existing defect; alignment to table content is the canonical reading.

**Forward-flagged out-of-scope discoveries (non-blocking iteration 2).** Three surfaces require attention beyond this revision pass:

1. **OD C-OD-09 cross-axis citation drift** — `Spec_Operational_Discipline_v1.md` line 498 reads `"Spec_Control_Plane_v1.md C-CP-03 §3.5 (fallback.triggered always-sampled; breaker.trip always-sampled)"`. The `breaker.trip` reference is now stale post-Stage-3b filing; OD revision pass at Stage 3c will align the cross-axis citation to `breaker.tripped`.

2. **F-CP-01 attribute semantic-loss re-evaluation** — re-introducing `breaker.cause` and `breaker.cooldown_ms` (if desired) would require OD C-OD-07 §7.1 schema expansion (currently fixed at 7 attributes). Out-of-F-CP-01-scope; surface to operator at iteration 2 entry-gate if attribute re-introduction is desired.

3. **CP §24.1 export table ↔ D6 §1.2 ingest map substrate-level alignment drift** — surfaced during Site D analysis at Stage 3b. CP §24.1 export table at lines 2087+ enumerates 11 namespaces (engine, topology, subagent, hitl, audit, fallback, harness.breaker, retry, lease, validator.fail, routing) claimed as exported for D6 ingest. ADR-D6 v1.1 §1.2 specialization-layer namespace map enumerates 15 namespaces; the CP-source-attributed subset is six (`engine.*`, `topology.fanout.*` [note D6 uses fanout-suffixed; not generic `topology.*`], `subagent.*`, `hitl.*`, `audit.*`, `validator.fail.*`). The remaining CP-claimed exports (`fallback.*`, `retry.*`, `lease.*`, `routing.*`) appear in D6 §1.2 only as F3 capability-floor lifecycle events (`fallback.triggered`, `retry.attempt`, `lease.acquired/released`) or not at all (`routing.*`). `harness.breaker.*` is substrate-anchored at `c9-reliability-recovery` SKILL.md per F2-16 closure, not CP-anchored. The CP §24.1 export table conflates F3-lifecycle-event-emitting and specialization-layer-namespace categories. Resolution requires either (a) CP §24.1 table restructure distinguishing F3-lifecycle-event-attributes from specialization-layer-namespace-exports, OR (b) ADR-D6 v1.2 revision adding the missing namespaces to §1.2 specialization map, OR (c) operator reconfirmation of F-OD-01 selection (B preserved this stage; A would have aligned the count to six CP-source namespaces actually enumerated at D6 §1.2). Out of F-CP-01 + F-OD-01 mechanical-alignment scope; iteration 2 review will surface this as a Class 2 substrate drift unless pre-emptively addressed.

**Sections preserved verbatim.** §Front-matter (Axis-grounding note bullets 1 + 2 + paragraph 1; PRD requirement scope; ADR commitment scope; cross-axis citation table; Deferred to implementation discretion); §2 C-CP-02 (per-layer attribution); §3 C-CP-03 §3.1, §3.2, §3.3 (chain advancement contracts); §3.5 paragraphs surrounding the three F-CP-01 sites (preamble, "Three namespaces declared..." narrative, retry sampling-rate row, F2-12 carry-forward note); §4 C-CP-04 through C-CP-04.x (cross-family fallback contracts); §5 C-CP-05 §5.2 + §5.3 (per-class minimum attribute set; `lease.*` namespace); §5.5 + §5.6 + §5.7 (composition with downstream namespaces; F2-12 active engagement; PRD requirement satisfaction); §6 through §17 (all D1-anchored + D4-anchored contracts at pre-§18); §18 C-CP-19 §18.1 + §18.2 + §18.3 + §18.5 (two-agent-observer trigger / composition / per-persona-tier-binding contract — §18.4 audit-composition row Site B amended); §19 through §22 (all D5-anchored contracts excluding the Site D ADR-commitments row at §24); §23 C-CP-23 (T-perm-3 three-layer composition; §23.4 deterministic-outer-harness composition row Site C amended at single token); §24 C-CP-24 §24.2 + §24.3 + §24.4 (cross-axis composition exports; cross-axis composition with session 5; F2-12 carry-forward export; Deferred to implementation discretion — §24 ADR-commitments-honored row at line 2081 Site D amended); §[traceability] matrix (CP-side rows; D3 etc. unchanged); §[carry-forwards]; §[coherence pass] (preserved verbatim as v1 point-in-time historical audit per Stage 2 + Stage 3a precedent). C-CP-03 §3.4 narrative + code block REWRITTEN per Site A under canonical-schema-pointer discipline; previously displayed dropped 4-attribute set.

**Status posture.** `Status: Proposed (v1.1 pending P5-CK iteration 2 clearance per Project_Workflow_v1_2.md §3.1)`. v1.1 enters P5-CK iteration 2 as input artifact alongside ADR-D3 v1.2, PRD v1.0.1, IS spec v1.1, and the two remaining Phase 5 spec revisions (OD spec at Stage 3c, composition doc at Stage 4) per handoff §6.1 entry-gate checklist.

**Changes inline.** Status block (Status row revised; Revision row + Revision date row appended). This Change-note section (new). §Axis declaration bullet 3 at line 28 (`validator.*` → `validator.fail.*`). §Axis-grounding note bullet 3 at line 36 (11-namespace enumeration with `harness.breaker.*` rename and `routing.*` addition). §3 C-CP-03 §3.4 narrative + code block (rewritten to remove duplicate-and-stale 4-attribute display; narrative aligned to `breaker.tripped` event + `harness.breaker.*` namespace; canonical schema pointer to §3.5). §3 C-CP-03 §3.5 section heading + namespace table row + sampling event row (three sites). §5 C-CP-05 §5.1 event class row + §5.4 sampling row (two sites). §18 C-CP-19 §18.4 verifier audit-composition row (`validator.*` → `validator.fail.*`). §23 C-CP-23 §23.4 deterministic-outer-harness composition row (`breaker.*` → `harness.breaker.*`). §24 C-CP-24 ADR-commitments-honored row (line 2081: `breaker.*` → `harness.breaker.*`; added `routing.*` per F-OD-01 selection B). §24 C-CP-24 §24.1 preamble + substrate seam table row (two sites). Thirteen sites total across two F-CP-01 amendments + one F-CP-03 amendment + two F-OD-01 propagation amendments + Sites A/B/C/D post-discovery within-spec drift alignment. No other content modified.

**§[coherence pass] preservation discipline.** §[coherence pass] section is v1 point-in-time audit; v1.1 mechanical revision does not re-run the audit. Audit rows referencing v1 namespace state (`breaker.*` vs `harness.breaker.*` count; `breaker.trip` vs `breaker.tripped` naming; "ten" vs "eleven" count) are accurate historical record of the v1 audit pass; v1.1 → v1.2 (if needed at iteration 2 entry or post-iter-2) is the proper moment for fresh coherence pass.

---

## Front-matter

### Axis declaration

Per OD-5-2.A spec-writer judgment with handoff §3.1 recommendation followed: **Control Plane** is the session-3 axis. Rationale:

- **Largest axis surface.** Five ADRs in scope (F1 v1.2 + F3 v1.1 + D1 v1.1 + D4 v1.1 + D5 v1.3); twelve PRD requirements (R-CP-01 through R-CP-12) — the densest axis in PRD scope. F1 and F3 are foundational substrate; D1, D4, and D5 specialize per deployment surface, workload class, and persona tier respectively.
- **Composition substrate posture.** Sequenced after Information Substrate (session 1) so that D1 engine event history × F2 state-ledger join on `idempotency_key` composes via C-IS-05 + C-IS-10 §10.2 citations. Sequenced after Action Surface (session 2) so that D5 gate-level composition × F4/D2 sandbox tier composes via C-AS-04 + C-AS-11 + C-AS-12 + C-AS-15 + C-AS-16 citations; D4 sub-agent privilege inheritance composes against C-AS-11 monotonic-ascension; D4 cross-sibling audit-ledger composes against C-IS-05 + C-IS-06 + C-IS-07.
- **Substrate seam priority for session 4.** Operational Discipline (session 4) consumes the Control Plane `hitl.*` / `audit.*` / `engine.*` / `topology.*` / `validator.fail.*` span attribute namespaces declared at this spec via the C-CP-24 substrate seam exports surface.

### Axis-grounding note

The Control Plane axis hosts **two foundational ADRs** (F1 v1.2 capability-aware multi-LLM provider abstraction with layered cheapest-deterministic-first routing; F3 v1.1 stateless-reducer / launch-pause-resume durable-execution pattern with capability-requirement floor) and **three derivative ADRs** (D1 v1.1 five-element engine-class taxonomy with per-deployment-surface candidate mapping; D4 v1.1 six-pattern multi-agent topology with workload-class × engine-class matrix; D5 v1.3 four-response HITL palette with synchrony class × persona-tier × engine-class matrix) per ADD §2.1 + §2.3 + §3.1.1 + §3.1.2 + §3.1.3. Cross-axis composition:

- **Information Substrate** (this spec consumes C-IS-05 entry shape + C-IS-06 hash-chain construction + C-IS-07 read/write contract pair + C-IS-10 §10.1 + §10.2 substrate seam exports at session-1 spec citations)
- **Action Surface** (this spec consumes C-AS-04 fail-class taxonomy + C-AS-11 sub-agent monotonic-ascension + C-AS-12 5-axis multiplicative tunable + C-AS-13 eleven-primitive matrix + C-AS-15 sandbox-bounded span schema + C-AS-16 substrate seam exports at session-2 spec citations)
- **Operational Discipline** (this spec exports CP namespaces to D6 unified span schema at session 4 ingestion across three composition paths: (i) six specialization-layer namespaces ingested at D6 §1.2 — `engine.*`, `topology.*`, `subagent.*`, `hitl.*`, `audit.*`, `validator.fail.*`; (ii) four F3-capability-floor lifecycle-event-attribute namespaces ingested at D6 §1.2 lines 124–133 — `fallback.*`, `retry.*`, `lease.*`, `harness.breaker.*` (substrate-anchored at `c9-reliability-recovery` SKILL.md per F2-16 closure); (iii) one inheritance-composition namespace not ingested at D6 — `routing.*` inherits sampling from parent `llm.inference` span per OTel GenAI semconv 1.41.0; eleven namespaces total = 6 + 4 + 1)

is captured at C-CP-24 (Control Plane substrate seam exports surface) for the downstream session 4 spec to consume by citation.

### PRD requirement scope

| PRD requirement | Observer role | Primary ADR section citation |
|---|---|---|
| R-CP-01 — Routing decision visible at LLM call surface | Production-time operator | ADR-F1 v1.2 §Decision + §Consequences (a); ADD §2.1 Synthesis |
| R-CP-02 — Cross-family fallback announced before error path | Production-time operator | ADR-F1 v1.2 §Decision (deterministic-fallback-on-budget-exceeded); §Consequences (a); ADD §2.1 Synthesis |
| R-CP-03 — Per-provider capability surface introspectable at authoring time | Design-time operator | ADR-F1 v1.2 §Decision (per-provider capability-introspection API); ADD §2.1 Synthesis |
| R-CP-04 — Workflow lifecycle event surface | Production-time operator | ADR-F3 v1.1 §Decision capability-floor (iv); ADD §2.3 Synthesis |
| R-CP-05 — Manifest-default invocation with per-step opt-in override | Design-time operator | ADR-F3 v1.1 §Decision (manifest-declaration default; per-step annotation opt-in); ADD §2.3 Synthesis |
| R-CP-06 — Engine class committed per deployment surface at design time | Design-time operator | ADR-D1 v1.1 §1.1 + §1.2; composition with ADR-F3 v1.1 §Decision; ADD §3.1.1 Synthesis |
| R-CP-07 — Replay-resumption semantics visible at run resumption | Production-time operator | ADR-D1 v1.1 §1.1; ADD §3.1.1 Synthesis (**F2-12 active engagement** — see §[carry-forwards] [CF-1]) |
| R-CP-08 — Multi-agent topology selectable at workflow definition | Design-time operator | ADR-D4 v1.1 §1.1 + §1.2; ADD §3.1.2 Synthesis |
| R-CP-09 — Sub-agent privilege inheritance with monotonic-only descent | Downstream maintainer | ADR-D4 v1.1 §1.5; ADR-D2 v1.1 §1.4 (Action Surface cross-axis); ADD §5.3.2 |
| R-CP-10 — HITL four-response palette at every gate | Production-time operator | ADR-D5 v1.3 §1.1 + §1.2; ADD §3.1.3 Synthesis |
| R-CP-11 — Three-placement HITL topology primitive at workflow definition | Design-time operator | ADR-D5 v1.3 §1.3; ADD §3.1.3 Synthesis |
| R-CP-12 — Audit-ledger cryptographic shape per persona tier | Downstream maintainer | ADR-D5 v1.3 §1.4 + §1.4.1; ADD §3.1.3 Synthesis |

### ADR scope

| ADR | Version | Role in axis |
|---|---|---|
| F1 | v1.2 | Foundational; commits capability-aware multi-LLM provider abstraction with thin core surface + per-provider capability-introspection API; layered cheapest-deterministic-first routing (declarative manifest / embedding classifier / LLM-as-router) with per-layer time budget and deterministic-fallback-on-budget-exceeded; manifest-as-auditable-default routing surface |
| F3 | v1.1 | Foundational; commits stateless-reducer / launch-pause-resume durable-execution pattern (P-CP-8); capability-floor of (i) durable replay, (ii) idempotency-keyed exactly-once semantics composed against ADR-F2 state-ledger entry shape, (iii) lease coordination preventing concurrent-resume corruption, (iv) observable lifecycle exposing eight event classes; manifest-declaration invocation-discipline default with per-step annotation opt-in |
| D1 | v1.1 | Derivative; commits five-element engine-class taxonomy (event-sourced-replay / save-point-checkpoint / pure-pattern-no-engine / reconciler-loop / WAL-segment); per-deployment-surface candidate mapping (local-development / self-hosted-server / managed-cloud); `topology_fault_handling ∈ {ABOVE_ENGINE, BELOW_ENGINE, RECONCILER}` D1-layer T-perm-3 resolution; `engine.*` span attribute namespace declaration |
| D4 | v1.1 | Derivative; commits six-pattern multi-agent topology taxonomy; per-workload-class topology + fan-out cap + cascade-policy default + writer-serialization stance; 2D matrix workload-class × D1-engine-class; sub-agent privilege inheritance contract with default-downgrade rule; HandoffContext + brief object structure; concurrent-prompt-cache warm-up protocol; multi-agent span hierarchy; cross-sibling audit-ledger discipline; T-perm-3 D4-layer multiplicative specialization |
| D5 | v1.3 | Derivative; commits four-response palette (`approve` / `edit` / `reject` / `respond`); three-placement HITL topology primitive (pre-action / sub-agent-boundary / validator-escalation); synchrony-class × HITL-primitive-shape 2D matrix per persona-tier × D1-engine-class; T-perm-1 D5-layer 4-axis multiplicative gate-level rule with cross-deployment monotonicity; per-persona-tier audit-ledger cryptographic shape with seven `audit.*` attributes; pre-HITL escalation order with five-class `validator.fail.*` taxonomy; context revalidation on HITL resume |

### Cross-axis citation substrate

| Source spec | Contracts consumed | Composition shape |
|---|---|---|
| `Spec_Information_Substrate_v1.md` | C-IS-05 (state-ledger entry shape) | C-CP-08 engine event history joins F2 state-ledger on `idempotency_key`; C-CP-15 per-sibling tool-call ledger entries honor F2 six-field shape; C-CP-20 audit-ledger entries compose against F2 entry shape with persona-tier-conditional cryptographic enrichment |
| `Spec_Information_Substrate_v1.md` | C-IS-06 (hash-chain integrity construction) | C-CP-20 team-binding+ audit-ledger uses F2 hash-chain construction; C-CP-15 cross-sibling merkle-root construction reads F2 entries via `action_id` join |
| `Spec_Information_Substrate_v1.md` | C-IS-07 (read/write contract pair) | C-CP-15 audit writes follow C3-pole append-only structured idempotent write contract; C-CP-20 audit-ledger writes follow same contract |
| `Spec_Information_Substrate_v1.md` | C-IS-10 §10.1 (state-ledger entry shape export — Control Plane row) | C-CP-08 engine event history joins F2 state-ledger via `idempotency_key`; resolves the cross-axis composition surface declared at session 1 |
| `Spec_Information_Substrate_v1.md` | C-IS-10 §10.2 (idempotency-key join export) | C-CP-08 + C-CP-15 inherit the harness-canonical `idempotency_key` as join key; F2-12 carry-forward note inherited at §[carry-forwards] |
| `Spec_Action_Surface_v1.md` | C-AS-04 (sandbox fail-class taxonomy) | C-CP-21 pre-HITL escalation order discriminates by validator.fail.* class precedent established at C-AS-04 sandbox-violation fail-class taxonomy (D2 §1.8 precedent applied at D5 §1.10 per F2-15) |
| `Spec_Action_Surface_v1.md` | C-AS-11 (sub-agent sandbox-tier monotonic-ascension) | C-CP-12 sub-agent privilege inheritance composes with sandbox-tier monotonic-ascension; gate-level + sandbox-tier + persona-tier all ascend jointly |
| `Spec_Action_Surface_v1.md` | C-AS-12 (T-perm-1 D2-layer 5-axis multiplicative tunable) | C-CP-19 T-perm-1 D5-layer 4-axis tunable specializes to 5-axis at D2 layer; D5 commits 4 axes (`per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier`); D2 adds `sandbox_tier` as fifth |
| `Spec_Action_Surface_v1.md` | C-AS-13 §13.4 (per-sub-agent-role × model-binding) | C-CP-13 brief-authoring model binding inherits lead/orchestrator binding per C-AS-13 §13.4; pre-HITL escalation 2nd-fail model-tier escalation per C-CP-21 reads C-AS-13 §13.4 |
| `Spec_Action_Surface_v1.md` | C-AS-15 (sandbox-bounded span schema) | C-CP-14 multi-agent span hierarchy + C-CP-20 HITL-event span hierarchy compose orthogonally with C-AS-15 sandbox span hierarchy; spans nest as `subagent.span[i] → sandbox.enter → tool.call → sandbox.exit` |
| `Spec_Action_Surface_v1.md` | C-AS-16 (Action Surface substrate seam exports) | All Action Surface cross-axis citations resolve to C-AS-16 §16.* export surfaces |

### Persona-linkage substrate

| Persona anchor | Inheriting requirement(s) |
|---|---|
| §3.1 (four primary workload classes — software engineering / content creation / pipeline automation / research) | R-CP-06, R-CP-08 |
| §3.1.1 + §8.1 (software engineering — F3 mixed; evaluator-optimizer / Reflexion natural fit) | R-CP-08 |
| §3.1.2 + §8.2 (content creation — F3 mostly ephemeral) | R-CP-08 |
| §3.1.3 + §8.3 (pipeline automation — F3 durable-execution-spine territory par excellence) | R-CP-04, R-CP-06, R-CP-08 |
| §3.1.4 + §8.4 (research — mixed F3 with Anthropic-canonical 3–5 fan-out) | R-CP-08 |
| §3.2 (workload-class extensibility flag) | R-CP-06, R-CP-08 |
| §4 (99.9%+ completion SLO at tens-concurrent; mathematically incompatible with operator-in-loop-on-every-failure HITL — selective HITL) | R-CP-04, R-CP-10 |
| §5 (integration surface — hosted majors + local/open-weight tier) | R-CP-01, R-CP-03 |
| §5.1 (computer-use at design-time AND production-time with stronger sandbox tier at production-time) | R-CP-09 |
| §6 (per-workload-class cost ceiling) | R-CP-01, R-CP-02 |
| §7 (pragmatic-mixed ecosystem affinity — Anthropic primitives where they fit; vendor-neutral abstraction otherwise) | R-CP-03, R-CP-05, R-CP-11 |
| §8.5 (cost × reliability × capability cross-class coupling) | R-CP-01, R-CP-02 |
| §9 (deployment-surface implications — local-development design-time forced; production-time option space narrowed but not picked) | R-CP-06 |
| §10.1 (durable-execution capability requirement persona-answered) | R-CP-04, R-CP-05 |
| §10.2 (selective HITL persona-constrained; cost-attribution-per-span foundational primitive; routing-strategy / durable-execution / production-time deployment-surface persona-constrained) | R-CP-01, R-CP-04, R-CP-06, R-CP-10, R-CP-11 |
| §10.4 (compliance-readiness foundational primitives — hash-chained audit ledger + cryptographic signature per persona tier) | R-CP-04, R-CP-09, R-CP-12 |
| §11.3 (long-tail duration of durable pole) | R-CP-06 |
| §11.4 (throughput rough order-of-magnitude per day) | R-CP-08 |
| §11.6 + §11.7 + §11.10 (compliance + vendor / IP-handling restrictions + multi-tenant tenant-isolation at multi-tenant binding) | R-CP-12 |

### Scope and out-of-scope

| In scope | Out of scope |
|---|---|
| Specification-grade contract precision for R-CP-01 through R-CP-12 (signatures, schemas, formulas, enums, surface contracts, matrices) | New architectural commitments (Phase 3 territory; back-flow to ADR revision if surfaced) |
| Citation-by-section to PRD requirements + ADR commitments + ADD synthesis paragraphs + cross-axis Information Substrate spec + Action Surface spec contracts | ADR revision; ADD revision; PRD revision; Information Substrate spec revision; Action Surface spec revision |
| Persona-linkage trace preservation from PRD requirements | Cross-axis spec coherence beyond Information Substrate + Action Surface seam consumption (deferred to session 5 composition document per handoff §3.1) |
| Substrate seam exports surface (C-CP-24) for session 4 Operational Discipline spec to consume by citation | Operational Discipline contracts; D6 unified span schema (session 4 territory) |
| §[carry-forwards] inheritance from PRD §[carry-forwards] + session-1 spec §[carry-forwards] + session-2 spec §[carry-forwards] | F2-12 mechanical closure (parallel `council-orchestrator` C7+C9 session territory; carry-forward only here with active engagement note at C-CP-08) |
| F2-12 active engagement notation at C-CP-08 (R-CP-07-satisfying contract) per `Phase_5_Session_3_Session_Prompt.md` §5.4 [CF-1] | Span re-emission semantics under engine replay; `retry.attempt` sibling-span discipline; trace-ingestion dedup composition with F2 `idempotency_key` at D6 cost-attribution |
| Deferred-to-implementation discretion notation per Workflow §2.5.1 exit criteria language | Implementation-grade choices beyond specification surface (specific provider candidates, specific engine candidates within class, specific library bindings, specific TUI / dashboard implementations) |

---

## §1 C-CP-01 — Capability-aware multi-LLM provider abstraction

**Contract surface.** Thin core surface (generation, streaming, tool-use) + per-provider capability-introspection API + manifest-as-auditable-default routing surface.

**PRD requirement(s) satisfied.** R-CP-01 (routing decision visible at LLM call surface — call-site attribution half); R-CP-03 (per-provider capability surface introspectable at authoring time).

**ADR commitment(s) honored.** ADR-F1 v1.2 §Decision (capability-aware abstraction with thin core surface + per-provider capability-introspection API at call sites); ADR-F1 v1.2 §Consequences (a) (manifest-layer model assignment per agent role / workflow class / step — declarative routing as auditable default); ADD §2.1 Synthesis.

**Persona linkage.** Persona §5 (integration surface — hosted majors + local/open-weight tier); §7 (pragmatic-mixed ecosystem affinity — Anthropic primitives where they fit, vendor-neutral abstraction otherwise); §10.2 (routing-strategy persona-constrained); §10.3 (F1 sub-aspects open at sub-aspect level but persona-constrained on shape).

**Specification content.**

### §1.1 Thin core surface

The provider abstraction's thin core MUST expose three operation classes (provider-neutral signatures):

```
generate(messages: List<Message>, params: GenerationParams) -> GenerationResult
stream(messages: List<Message>, params: GenerationParams) -> Stream<StreamEvent>
tool_use(messages: List<Message>, tools: List<ToolDef>,
         params: GenerationParams) -> ToolUseResult
```

Per ADR-F1 v1.2 §Decision, the core is **convergent** across providers (per Pattern Reference Catalog §10.2 P-IS-10 with C-on-the-abstraction's-necessity). Provider-specific feature surfaces (Anthropic prompt caching, OpenAI structured outputs, extended-thinking budgets, Batch API, MCP-as-server-tool) are NOT lifted into this core; they are reached via the per-provider capability surface at §1.2.

### §1.2 Per-provider capability-introspection API

Each provider adapter MUST implement a capability-introspection API:

```
capabilities(provider_id: ProviderID) -> ProviderCapabilities

ProviderCapabilities {
    prompt_cache_support       : CacheCapability  // {none, breakpoint_count_N, ttl_set}
    structured_outputs         : StructuredOutputsCapability  // {none, schema_modes_set}
    extended_thinking          : ExtendedThinkingCapability  // {none, budget_range_or_efforts}
    batch_api                  : BatchAPICapability  // {none, max_batch_size}
    mcp_support                : MCPCapability  // {none, transport_classes_set}
    streaming_event_shape      : StreamingEventSchema  // normalized event types
    // ... additional capability fields per provider as documented at adapter
}
```

Per ADR-F1 v1.2 §Decision, capability-introspection at call sites enables manifest authoring to bind providers per per-feature requirement. Authoring-time tooling consumes this surface to compose declarative manifest bindings per ADR-F1 v1.2 §Consequences (a).

### §1.3 Manifest-as-auditable-default routing surface

Per ADR-F1 v1.2 §Consequences (a):

| Property | Contract |
|---|---|
| **Manifest residence** | Routing manifest resides at canonical filesystem path per `Spec_Information_Substrate_v1.md` C-IS-10 §10.4 filesystem-path-contract export; atomic prompt+code+eval+manifest deploys per `Spec_Information_Substrate_v1.md` C-IS-03 |
| **Manifest authoring grain** | Per agent role × per workflow class × per step; the manifest entry is the **declarative tier of the layered cheapest-deterministic-first routing strategy** at §2 below |
| **Audit surface** | Every LLM call carries provider + model + selecting-layer attribution per §1.4 below; manifest-bound calls carry `routing.layer = manifest` |

### §1.4 Run-event attribution at call surface

Per R-CP-01 acceptance criterion + ADR-F1 v1.2 §Consequences (a):

| Attribute | Type | Semantic | Source |
|---|---|---|---|
| `routing.provider` | enum string (provider catalog) | Provider identity bound at call | F1 §1.2 capability surface |
| `routing.model` | string | Model identifier within provider | F1 §1.2 capability surface |
| `routing.layer` | enum string ∈ `{manifest, embedding, llm_as_router, fallback}` | Layer that produced the binding | §2 layered routing strategy |
| `routing.binding_rationale` | string (optional) | Short token enumeration of which manifest entry / which classifier label / which fallback trigger drove the binding | Per-layer mechanism |

These attributes attach to the `llm.inference` span emitted per `Spec_Action_Surface_v1.md` C-AS-14 §14.2 `anthropic.*` namespace (and cross-family analogs) and are namespace-rooted at `routing.*` per the OTel GenAI semconv extension. The `routing.layer ∈ {manifest, embedding, llm_as_router}` enumeration is the harness-canonical three-tier discrimination per ADR-F1 v1.2 §Decision; `fallback` is the fourth value carried at C-CP-04 fallback events.

**Deferred to implementation discretion.** Specific provider catalog enumeration; specific provider-adapter binding library; specific manifest serialization format (YAML / TOML / JSON beyond the markdown-spec-driven authoring surface per Persona §7); specific capability-introspection cache lifetime; specific Anthropic SDK / cross-family adapter binding.

---

## §2 C-CP-02 — Layered cheapest-deterministic-first routing strategy

**Contract surface.** Three-tier routing layer ordering + per-layer resolution contract + per-layer attribution + layer-promotion + layer-fall-through semantics.

**PRD requirement(s) satisfied.** R-CP-01 (routing decision visible at LLM call surface — layer attribution half); R-CP-02 (cross-family fallback announced before error path — layer-fall-through trigger half).

**ADR commitment(s) honored.** ADR-F1 v1.2 §Decision (layered cheapest-deterministic-first strategy: declarative manifest as default, embedding-classifier dispatch as second tier, LLM-as-router as opt-in last-resort); ADR-F1 v1.2 §Rationale (a) + §Rationale (b) (single-strategy routing fails one of three axes by construction); ADD §2.1 Synthesis.

**Persona linkage.** Persona §3.2 (workload-class extensibility flag — pure-declarative cannot accommodate); §6 (per-workload-class cost ceiling — pure-LLM-as-router incompatible); §8.5 (cost × reliability × capability cross-class coupling); §10.4 (compliance-readiness — per-step manifest auditability).

**Specification content.**

### §2.1 Layer ordering and resolution contract

Routing proceeds top-down through three layers per call site:

```
on_llm_call(call_site_context: CallSiteContext) -> RoutingBinding:

  Layer 1 — Declarative manifest binding (cheapest, fully deterministic):
    Lookup manifest entry by (agent_role, workflow_class, step).
    If entry matches → return RoutingBinding(provider, model, layer="manifest",
                                              binding_rationale=manifest_entry_id)
    Else fall through to Layer 2.

  Layer 2 — Embedding-classifier dispatch (cheap, deterministic-modulo-classifier):
    Project call_site_context into embedding space.
    Run k-nearest classifier against trained corpus per workload class.
    If top-k confidence > threshold → return RoutingBinding(provider, model,
                                                            layer="embedding",
                                                            binding_rationale=classifier_label)
    Else fall through to Layer 3.

  Layer 3 — LLM-as-router (expensive, last-resort):
    Invoke router model with call_site_context + candidate-set summary.
    Router emits provider + model selection plus rationale.
    Return RoutingBinding(provider, model, layer="llm_as_router",
                          binding_rationale=router_rationale_summary)
```

### §2.2 Per-layer cost discipline (cheapest-deterministic-first principle)

| Layer | Cost shape | Determinism | When it resolves |
|---|---|---|---|
| **manifest** | Zero inference cost; one lookup per call | Fully deterministic | The manifest binds the (agent_role, workflow_class, step) tuple |
| **embedding** | One embedding call per (call_site_context shape); k-nearest is local | Deterministic modulo classifier corpus version | The manifest does not bind AND the classifier confidence exceeds threshold |
| **llm_as_router** | One full LLM call per dispatch; 50–200 ms latency per Cluster 1 V2 §2.2.4 [HIGH] (cited at ADR-F1 v1.2 §Rationale (b)) | Probabilistic (router-internal LLM call) | All prior layers fall through |

The ordering preserves the **cheapest-deterministic-first** invariant per ADR-F1 v1.2 §Decision: each call resolves at the cheapest layer that can resolve it, and every binding is auditable at the layer that produced it.

### §2.3 Per-layer attribution

Every routing binding carries `routing.layer ∈ {manifest, embedding, llm_as_router}` per C-CP-01 §1.4. Per-layer attribution discriminates how a call resolved at run-event inspection.

### §2.4 Per-layer time budget invariant (composition with C-CP-03)

Each routing layer carries a per-layer time-budget bound (C-CP-03 §3.1). Budget exceedance at any layer triggers deterministic fall-through to the next layer (not error). C-CP-03 details the budget contract.

**Deferred to implementation discretion.** Specific embedding model and dimensionality; specific classifier training-corpus construction (per-workload-class corpus authored at workload-binding-time); specific k for k-nearest; specific confidence threshold per workload class; specific LLM-as-router prompt content (per-call-site-context shape); specific router model binding (Haiku-class typical per cost discipline).

---

## §3 C-CP-03 — Per-layer time budget with deterministic-fallback-on-budget-exceeded

**Contract surface.** Per-layer time-budget bound + deterministic fall-through on exceedance + fallback-trigger event emission + composition with breaker placement.

**PRD requirement(s) satisfied.** R-CP-02 (cross-family fallback announced before error path — time-budget trigger half).

**ADR commitment(s) honored.** ADR-F1 v1.2 §Decision (per-layer time budget with deterministic-fallback-on-budget-exceeded); ADR-F1 v1.2 §Consequences (a) (capability-shortfall fallback triggering as distinguishing signal before error path); ADR-F1 v1.2 §"Permanent tensions engaged" (T-perm-3 F1-layer resolution shape: per-layer time-budget); ADD §2.1 Synthesis closing sentence.

**Persona linkage.** Persona §4 (99.9%+ completion SLO; deterministic outer harness absorbs most recovery); §8.5 (cost × reliability × capability cross-class coupling); §10.2 (cost-attribution-per-span foundational primitive).

**Specification content.**

### §3.1 Per-layer time-budget bound

```
LayerBudget {
    layer        : "manifest" | "embedding" | "llm_as_router"
    timeout_ms   : int  // hard upper bound; layer exceedance triggers fall-through
    soft_warn_ms : int (optional)  // emit soft-warning at warn-threshold (not fall-through)
}
```

Per-layer time-budget is **per-workload-class operator-tunable** at workflow definition (composition with C-CP-06 §6.1 manifest-declaration discipline). Tuning is per layer × per workload class × per persona tier (the higher-tier persona caps budget tighter on `llm_as_router` per per-class cost ceiling per Persona §6).

### §3.2 Deterministic fall-through on exceedance

Per ADR-F1 v1.2 §Decision:

```
on_layer_exceed_budget(layer, call_site_context, elapsed_ms):
  1. Emit fallback.triggered span event:
       attrs: fallback.from_layer = layer
              fallback.cause = "time_budget_exceeded"
              fallback.elapsed_ms = elapsed_ms
              fallback.budget_ms = LayerBudget.timeout_ms
  2. Advance to the next layer per C-CP-02 §2.1 layer ordering.
  3. If all layers exhausted → emit fallback.exhausted span event;
       route to error path per C9 retry-exit semantics.
```

The fall-through is **deterministic** in the sense that exceedance triggers an unconditional advance to the next layer; the routing-strategy chain does not adapt or skip layers based on inference at the budget-exceedance point.

### §3.3 Capability-shortfall fallback trigger

Per ADR-F1 v1.2 §Consequences (a):

```
on_capability_shortfall(provider, model, capability_required):
  1. Emit fallback.triggered span event:
       attrs: fallback.from_provider = provider
              fallback.from_model = model
              fallback.cause = "capability_shortfall"
              fallback.required_capability = capability_required
  2. Advance to next provider per C-CP-04 fallback chain composition.
  3. The advance happens BEFORE the error path — fallback-trigger announcement
     precedes any error emission per R-CP-02 acceptance criterion.
```

### §3.4 Composition with breaker placement

Per ADR-F1 v1.2 §Consequences (a) + Cluster 4 §2.2.7 [HIGH] (cited at ADR-F1 v1.2 References): circuit breakers attach per-`{provider, model}` pair. Breaker trip emits the `breaker.tripped` span event per the seven-attribute `harness.breaker.*` schema declared at §3.5 (canonical at OD C-OD-07 §7.1).

Breaker-trip events are a **distinguishing signal before error path** per R-CP-02 acceptance criterion and ADR-F1 v1.2 §Consequences (a). C9 mechanism owns breaker trip / cooldown / half-open / close transitions per the harness reliability-primitive composition site; D6 ingests `harness.breaker.*` namespace at session 4.

### §3.5 `fallback.*` and `harness.breaker.*` span attribute namespaces declared at this contract

Three namespaces declared at this contract are ingested by D6 §1.2 at session 4 (Operational Discipline spec):

| Namespace | Attributes |
|---|---|
| `fallback.*` | `fallback.from_layer`, `fallback.from_provider`, `fallback.from_model`, `fallback.cause` ∈ `{time_budget_exceeded, capability_shortfall, breaker_open, rate_limit_storm}`, `fallback.elapsed_ms`, `fallback.budget_ms`, `fallback.required_capability` (optional), `fallback.to_provider`, `fallback.to_model` |
| `harness.breaker.*` | `harness.breaker.scope` ∈ `{per_model, per_provider}`, `harness.breaker.from_state` ∈ `{closed, open, half_open}`, `harness.breaker.to_state` ∈ `{closed, open, half_open}`, `harness.breaker.trigger_count` (int), `harness.breaker.permanent_fail_repeats` (bool — C10 gating signal per OD C-OD-07 §7.1), `harness.breaker.tool_id` (string; per-model scope correlation), `harness.breaker.model_version` (string) |
| `retry.*` | `retry.attempt`, `retry.cause` (joins to `validator.fail.cause_attribution` per C-CP-21), `retry.backoff_ms`, `retry.policy` (full-jitter default per Cluster 4 §2.2.7 [HIGH]) |

Per `c7-observability` SKILL.md sampling discipline:

| Span event | Sampling rate |
|---|---|
| `fallback.triggered` | **Always-sampled (head=1.0, tail-keep-on-classification=true)** — fall-through is reliability-critical and tamper-evidence-relevant |
| `fallback.exhausted` | **Always-sampled (head=1.0)** — chain exhaustion is reliability-critical |
| `breaker.tripped` | **Always-sampled (head=1.0, tail-keep-on-classification=true)** |
| `retry.attempt` | Base-rate sampled at first attempt; **always-sampled (head=1.0) at 2nd attempt onward** (per Cluster 4 §2.2.3 [HIGH] staircase visibility) |

**F2-12 carry-forward note.** The `retry.attempt` sibling-span discipline (does `retry.attempt` emit a span event AND a new sibling span per D6 §1.2?) is part of the F2-12 deferred scope per `Phase_5_Session_3_Session_Prompt.md` §5.4 [CF-1]. C-CP-03 commits the attribute substrate and base-rate-then-always-sampled discipline; sibling-span vs span-event treatment is deferred to D1 v1.2 + D6 v1.2 closure per ADD §6.3.1.

**Deferred to implementation discretion.** Specific timeout values per cell of (workload-class × persona-tier × layer); specific embedding-classifier hot-path latency optimization; specific breaker trip-threshold values per `{provider, model}` pair; specific cooldown duration shape per cause class; specific OTel/OTLP emission timing for `fallback.triggered` events (before fall-through call vs concurrent with).

---

## §4 C-CP-04 — Cross-family fallback chain composition

**Contract surface.** Fallback chain shape + per-`{provider, model}` chain advancement + cross-family transition + prompt-cache invalidation semantics + chain-exhaustion error path.

**PRD requirement(s) satisfied.** R-CP-02 (cross-family fallback announced before error path — chain composition half).

**ADR commitment(s) honored.** ADR-F1 v1.2 §Decision (cross-family fallback with deterministic-fallback-on-budget-exceeded); ADR-F1 v1.2 §Consequences (a) (cross-provider sticky-routing within fallback chains; provider-sticky session keys per Cluster 1 V2 §2.2.5 [HIGH]); ADR-F1 v1.2 §Rationale (b) (LiteLLM-mediated fallback bypasses provider-specific prompt caching [MODERATE]); ADD §2.1 Synthesis.

**Persona linkage.** Persona §5 (integration surface — hosted majors + local/open-weight tier as fallback floor); §4 (99.9%+ SLO requires fallback floor); §10.2 (cost-attribution-per-span composes with fallback-cache-miss penalty).

**Specification content.**

### §4.1 Fallback chain shape

The fallback chain is a per-`(workload_class, agent_role, step)`-bound list of `{provider, model}` pairs in advancement order:

```
FallbackChain[workload_class][agent_role][step] = [
    (provider_0, model_0),  // primary; manifest-bound per C-CP-02 §2.1 Layer 1
    (provider_1, model_1),  // first fallback
    (provider_2, model_2),  // second fallback
    ...
    (provider_N, model_N)   // chain floor; typically local/open-weight per Persona §5
]
```

Chain advancement is **deterministic** at fall-through events (C-CP-03 §3.2 + §3.3); the chain does not skip entries based on inference.

### §4.2 Per-`{provider, model}` advancement triggers

| Trigger | Advancement contract | Span event emitted |
|---|---|---|
| Time-budget exceeded at current `{provider, model}` | Advance to next entry | `fallback.triggered` per C-CP-03 §3.2 |
| Breaker open for current `{provider, model}` | Advance to next entry (skip current until breaker closes per C-CP-03 §3.4) | `fallback.triggered` with `fallback.cause = breaker_open` |
| Capability shortfall at current `{provider, model}` | Advance to next entry meeting capability requirement | `fallback.triggered` per C-CP-03 §3.3 |
| Rate-limit-storm risk (per Cluster 4 §2.2.7 [HIGH]) | C9 mechanism may trigger preemptive advancement | `fallback.triggered` with `fallback.cause = rate_limit_storm` |

### §4.3 Cross-family transition shape

A transition from `(provider_i, model_i)` to `(provider_{i+1}, model_{i+1})` is **cross-family** when the two providers belong to distinct provider-family groupings (Anthropic / OpenAI-class / Google-class / local-open-weight). Cross-family transitions trigger additional events per `Spec_Action_Surface_v1.md` C-AS-13 §13.5 Anthropic-API graceful-degradation contract:

| Event | When emitted |
|---|---|
| `fallback.cross_family_triggered` | Emitted when the advancement crosses provider-family boundary |
| `prompt_cache.invalidated` | Cross-family fallback INVALIDATES the Anthropic prompt-cache state per Cluster 1 V2 §2.2.5 [HIGH] (cited at ADR-F1 v1.2 §Rationale (b)) |
| `routing.binding.degraded` | Capability set narrows per `Spec_Action_Surface_v1.md` C-AS-13 §13.5: extended-thinking unavailable cross-family from Anthropic; Batch API unavailable; cache state lost |

**Provider-sticky session keys** per ADR-F1 v1.2 §Consequences (a) (cited at Cluster 1 V2 §2.2.5 [HIGH]): once a chain advances cross-family, the session is sticky-bound to the new family for the remainder of the (agent_role, step) lifecycle until either (a) the next `lifecycle.event` per F3 v1.1 (workflow boundary), (b) operator-tunable session-key timeout, or (c) primary `{provider, model}` breaker closes AND a re-bind trigger fires per F1 §1.2 capability surface.

### §4.4 Chain-exhaustion error path

```
on_chain_exhausted(workload_class, agent_role, step):
  1. Emit fallback.exhausted span event (always-sampled per C-CP-03 §3.5).
  2. C9 mechanism owns the error-propagation behavior: per ADR-D5 v1.3 §1.10
     pre-HITL escalation order, `time_budget_exhaust` routes to
     permanent-fail-exit OR terminal-fail-exit (topology-context-dependent
     per C-CP-21 §21.1).
  3. The chain-exhaustion span emission PRECEDES any error path — R-CP-02
     acceptance criterion holds.
```

**Deferred to implementation discretion.** Specific provider-family enumeration (Anthropic / Bedrock-Anthropic / Vertex-Anthropic counted as same family per Anthropic-model-class per `Spec_Action_Surface_v1.md` C-AS-13 §13.5 cross-family contract); specific provider-sticky session-key serialization; specific re-bind cooldown duration; specific local/open-weight tier provider candidate selection; specific cross-family capability-narrowing-display surface at the operator UI.

---

## §5 C-CP-05 — F3 capability-floor lifecycle event surface

**Contract surface.** Eight lifecycle event classes + per-class span name + per-class minimum attribute set + always-sampled vs base-rate disposition per event class.

**PRD requirement(s) satisfied.** R-CP-04 (workflow lifecycle event surface visible at run-event surface as distinct event classes).

**ADR commitment(s) honored.** ADR-F3 v1.1 §Decision capability-requirement floor (iv) (observable lifecycle exposing workflow-start, step-boundary, fallback-trigger, retry-attempt, breaker-trip, lease-acquired, lease-released, resumption events); ADD §2.3 Synthesis; composition with ADR-D6 v1.1 §1.2 (operational discipline absorption — span ingestion at session 4).

**Persona linkage.** Persona §4 (99.9%+ SLO; deterministic outer harness absorbs most recovery); §10.4 (compliance-readiness — comprehensive observability foundational primitive); §8.3 (pipeline automation — F3 durable-execution-spine territory par excellence).

**Specification content.**

### §5.1 Eight lifecycle event classes (capability-floor (iv) substrate)

| Event class | Span name | Owning ADR section |
|---|---|---|
| `workflow-start` | `workflow.start` | ADR-F3 v1.1 §Decision (iv) |
| `step-boundary` | `step.boundary` | ADR-F3 v1.1 §Decision (iv); composes with F3 stateless-reducer pattern (event → next-step transition) |
| `fallback-trigger` | `fallback.triggered` | Declared at C-CP-03 §3.5 `fallback.*` namespace |
| `retry-attempt` | `retry.attempt` | Declared at C-CP-03 §3.5 `retry.*` namespace |
| `breaker-trip` | `breaker.tripped` | Declared at C-CP-03 §3.5 `harness.breaker.*` namespace |
| `lease-acquired` | `lease.acquired` | Declared at C-CP-05 §5.3 `lease.*` namespace |
| `lease-released` | `lease.released` | Declared at C-CP-05 §5.3 `lease.*` namespace |
| `resumption` | `workflow.resumption` | Declared at C-CP-05 §5.3; composes with C-CP-08 replay-resumption semantics |

### §5.2 Per-class minimum attribute set

| Span name | Minimum attributes |
|---|---|
| `workflow.start` | `workflow.id`, `workflow.class` ∈ Persona §3.1 four-class set + extension flag, `engine.class` per C-CP-09, `manifest.entry_id`, `idempotency_key` (root) |
| `step.boundary` | `workflow.id`, `step.index`, `step.kind` (declarative-step / inference-step / tool-step / HITL-step / sub-agent-dispatch), `idempotency_key` per `Spec_Information_Substrate_v1.md` C-IS-05 |
| `lease.acquired` | `lease.key`, `lease.holder`, `lease.ttl_ms`, `lease.mechanism` (per C-CP-09 §9.1 engine-class lookup) |
| `lease.released` | `lease.key`, `lease.holder`, `lease.release_cause` ∈ `{normal, ttl_expiry, holder_loss, lease_revoked}` |
| `workflow.resumption` | `workflow.id`, `engine.class`, `resumption.kind` per C-CP-08 §8.1 enum, `idempotency_key` (root) |

### §5.3 `lease.*` span attribute namespace declared at this contract

| Attribute | Type | Semantic | Cardinality |
|---|---|---|---|
| `lease.key` | string | Lease scope key (typical shape `{engine_class}_{workflow_id}_{step_index}` or engine-native scope) | per-active-lease |
| `lease.holder` | string | Lease-holder identity (worker id; pod name; process pid) | medium |
| `lease.ttl_ms` | int | Lease TTL in milliseconds | unbounded (metric) |
| `lease.mechanism` | enum string ∈ `{engine_native, redis_lease, db_unique_constraint, worktree_isolation, etcd_cas, per_segment}` | Per C-CP-09 §9.1 engine-class lookup | bounded (6) |
| `lease.release_cause` | enum string ∈ `{normal, ttl_expiry, holder_loss, lease_revoked}` | Per release event | bounded (4) |

### §5.4 Sampling discipline per event class

| Event class | Sampling rate | Rationale |
|---|---|---|
| `workflow.start` | **Always-sampled (head=1.0)** | Cost-attribution anchor; tamper-evidence baseline |
| `step.boundary` | head-based-dev base-rate / tail-based-prod default | Volume-bounded; tail-keep on failure classification |
| `fallback.triggered` / `fallback.exhausted` | **Always-sampled (head=1.0)** per C-CP-03 §3.5 | Reliability-critical |
| `retry.attempt` | base-rate at 1st attempt; **always-sampled at 2nd onward** per C-CP-03 §3.5 | Cluster 4 §2.2.3 [HIGH] staircase visibility |
| `breaker.tripped` | **Always-sampled (head=1.0)** per C-CP-03 §3.5 | Reliability-critical |
| `lease.acquired` / `lease.released` | base-rate | Volume-bounded; supports concurrent-resume corruption detection per ADR-F3 v1.1 capability-floor (iii) |
| `workflow.resumption` | **Always-sampled (head=1.0)** | Replay-resumption visibility per R-CP-07; tamper-evidence anchor |

### §5.5 Composition with downstream namespaces

| Namespace | Source contract | Composition shape |
|---|---|---|
| `engine.*` | C-CP-09 (D1 §1.1.1) | Every lifecycle event carries `engine.class` as stable discriminator |
| `topology.*` / `subagent.*` | C-CP-14 (D4 §1.9) | Multi-agent fan-out events extend the lifecycle envelope at sub-agent dispatch |
| `hitl.*` | C-CP-20 (D5 §1.8) | HITL events at HITL invocation extend the lifecycle envelope at `validator-escalation` placement per C-CP-17 |
| `audit.*` | C-CP-20 (D5 §1.4.1) | Audit-ledger-relevant events carry `audit.*` attributes per persona-tier emission discipline |
| `validator.fail.*` | C-CP-21 (D5 §1.10.1) | Validator-failure events carry `validator.fail.*` per discriminated five-class taxonomy |
| `sandbox.*` | `Spec_Action_Surface_v1.md` C-AS-15 | Tool-call-bounded sandbox events nest inside `step.boundary` |

**Deferred to implementation discretion.** Specific OTel/OTLP span emission implementation per cell; specific per-event-class span-vs-span-event treatment (some events MAY render as span events on a parent span rather than dedicated spans — the per-event-class disposition is a D6 v1.1 ingestion concern); specific tail-keep classification thresholds (rate-of-error vs absolute-count); specific `workflow.id` and `step.index` serialization format.

---

## §6 C-CP-06 — Manifest-declaration invocation discipline with per-step opt-in override

**Contract surface.** Manifest field schema for F3 invocation declaration + per-step annotation override syntax + per-step opt-in scope + audit-surface composition.

**PRD requirement(s) satisfied.** R-CP-05 (manifest-default invocation with per-step opt-in override).

**ADR commitment(s) honored.** ADR-F3 v1.1 §Decision (manifest-declaration as F3-invocation-discipline default; per-step annotation as opt-in for fine-grained durability cadence); ADD §2.3 Synthesis.

**Persona linkage.** Persona §7 (workflow-definition surface — both markdown-spec-driven and code-driven authoring); §10.2 (durable execution persona-constrained workload-dependent); §10.1 (durable-execution capability requirement persona-answered).

**Specification content.**

### §6.1 Manifest field schema for F3 invocation declaration

The routing manifest per C-CP-01 §1.3 is extended with F3 invocation fields. Per-workload manifest entry MUST carry:

```
WorkflowManifestEntry {
    workflow_class       : WorkflowClass  // Persona §3.1 four-class set + extension flag
    engine_class         : EngineClass    // C-CP-07 five-element taxonomy
    f3_invocation_default: InvocationDiscipline {
        durability_cadence : "per_workflow" | "per_step" | "per_inference"
        checkpoint_cadence : Duration | "every_step" | "every_inference" | "never"
        replay_semantics   : "engine_native" | "save_point" | "wal_segment" |
                             "filesystem_journal" | "reconciler_loop"
        // engine_class column at C-CP-07 §7.1 binds replay_semantics shape per class
    }
    routing_layer_budgets: [LayerBudget per C-CP-03 §3.1]
    fallback_chain       : [FallbackEntry per C-CP-04 §4.1]
    topology             : TopologyDeclaration  // per C-CP-10 + C-CP-11
    hitl_placements      : [HITLPlacement per C-CP-17 §17.1 three-placement primitive]
    // ... additional per-workload fields
}
```

The manifest entry is **the declarative tier of the C-CP-02 layered routing strategy** AND **the F3 invocation-discipline default** per ADR-F3 v1.1 §Decision.

### §6.2 Per-step annotation override syntax

Per-step annotations are scoped to a single workflow step and override the manifest defaults for that step:

```
@step("classify_intent")
@f3_invocation(durability_cadence="per_inference",
               checkpoint_cadence="every_inference",
               replay_semantics="save_point")
def classify_intent(...):
    ...
```

The annotation surface is **opt-in**: absence of `@f3_invocation` means inheritance of the manifest's `f3_invocation_default`. Per-step override does not propagate to sibling or child steps unless they also carry their own annotation.

### §6.3 Per-step opt-in scope

| Override field | Scope of override |
|---|---|
| `durability_cadence` | Per-step; affects which events emit `step.boundary` durable persistence calls |
| `checkpoint_cadence` | Per-step; affects checkpoint write frequency within the step |
| `replay_semantics` | Per-step (advisory at solo-developer; mandatory at team-binding+ unless cell admits the override per C-CP-07 §7.2) |

Per-step override is **bounded by the cell's engine-class** per C-CP-07 §7.2: a step cannot opt into `replay_semantics = "engine_native"` if the workflow's bound engine class is `pure-pattern-no-engine`. Out-of-cell overrides emit a manifest-validation error at workflow-binding time.

### §6.4 Audit-surface composition

Every per-step annotation override emits an audit-ledger entry at workflow-binding time per `Spec_Information_Substrate_v1.md` C-IS-05 entry shape:

```
audit_entry {
    action_id          : workflow_id || step_index || "f3_override"
    idempotency_key    : sha256(workflow_id, step_index, override_payload)
    actor              : workflow_definition_author
    response_hash      : sha256(canonicalize(override_payload))
    timestamp          : ISO-8601
    prior_event_hash   : <prior entry hash per C-IS-06 §6.1>
}
```

This composes with C-CP-20 audit-ledger cryptographic shape per persona tier.

**Deferred to implementation discretion.** Specific decorator vs configuration-file annotation syntax (`@f3_invocation` is illustrative; markdown-spec-driven authoring per Persona §7 may use a different declarative shape); specific manifest serialization format; specific workflow-binding-time validation library; specific override-conflict resolution at re-deploy (atomic prompt+code+manifest deploy per `Spec_Information_Substrate_v1.md` C-IS-03 composes here).

---

## §7 C-CP-07 — Five-element engine-class taxonomy with per-deployment-surface candidate mapping

**Contract surface.** Closed five-element engine-class enumeration + per-class lifecycle-ownership + per-class capability-floor mechanism + per-class C3-tier residence + per-class concurrent-resume mitigation + per-deployment-surface candidate mapping table + per-workload-class differentiation within cells.

**PRD requirement(s) satisfied.** R-CP-06 (engine class committed per deployment surface at design time).

**ADR commitment(s) honored.** ADR-D1 v1.1 §Decision (five-element engine-class taxonomy with parametric per-deployment-surface candidate selection); ADR-D1 v1.1 §1.1 (engine-class taxonomy table); ADR-D1 v1.1 §1.2 (per-deployment-surface candidate mapping); ADR-D1 v1.1 §1.4 (capability-floor preservation across classes); ADR-F3 v1.1 §Decision (capability-requirement floor non-negotiable); ADD §3.1.1 Synthesis.

**Persona linkage.** Persona §3 (workload classes including long-running-survives-restarts subset); §3.1.1 / §3.1.2 / §3.1.3 / §3.1.4 (four primary task classes); §3.2 (workload-class extensibility flag); §3.3 (work-unit shape distribution heterogeneous); §4 (99.9%+ SLO; pure-pattern-at-scale exclusion source); §6 (per-workload-class cost ceiling); §8.3 (pipeline automation — F3 durable-execution-spine territory par excellence); §9 (deployment-surface implications); §10.2 (F3 persona-constrained); §10.3 (F3-engine sub-aspect persona-open).

**Specification content.**

### §7.1 Five-element engine-class taxonomy

The taxonomy is **closed** at D1 §1.1; extension is a Workflow §4.1.2 Class-2 D1 revision.

| # | Class | Lifecycle ownership | Capability-floor mechanism | C3-tier residence | Concurrent-resume mitigation |
|---|---|---|---|---|---|
| 1 | `event-sourced-replay` | Engine | Engine-native: replay from Event History; activity outputs cached and replayed deterministically | Engine event history (Tier-3) + F2 state-ledger (Tier-5) joined on `idempotency_key` per `Spec_Information_Substrate_v1.md` C-IS-05 + C-IS-10 §10.2 | Engine-native lease (Temporal placement primitive; DBOS transaction boundary) |
| 2 | `save-point-checkpoint` | Application (composed atop engine save points) | Engine exposes per-super-step checkpoint; harness composes lease + dedup + resumption above | Checkpointer state (Tier-3) + F2 state-ledger (Tier-5) | Application-level lease (Redis lease; DB unique constraint; worktree isolation per `Spec_Information_Substrate_v1.md` C-IS-09) |
| 3 | `pure-pattern-no-engine` | Harness | Harness owns full durability contract over F2 substrate (filesystem-journal + state-ledger + idempotency-key) | F2 filesystem (Tier-3) + F2 state-ledger (Tier-5) per `Spec_Information_Substrate_v1.md` C-IS-01 + C-IS-05 | Harness-owned lease (worktree isolation per `Spec_Information_Substrate_v1.md` C-IS-09; DB unique constraint) |
| 4 | `reconciler-loop` | K8s controller | Reconciler-native: CRDs persist agent state across restarts | K8s etcd (Tier-3) + CRD events (Tier-5) | etcd compare-and-swap |
| 5 | `WAL-segment` | Harness | WAL-owned: append-only segment log with per-segment resume | WAL segments (Tier-3) + segment metadata (Tier-5) | Harness-owned per-segment lease |

### §7.2 Per-deployment-surface candidate mapping

Per ADR-D1 v1.1 §1.2:

| Deployment surface | Recommended engine classes | Per-workload-class differentiation within surface |
|---|---|---|
| `local-development` (design-time target per Persona §9 [HIGH]) | `save-point-checkpoint` OR `pure-pattern-no-engine` | Pipeline-automation pole → `save-point-checkpoint` with strict composition-discipline; software-engineering / content-creation / research → `pure-pattern-no-engine` acceptable per Persona §8.1, §8.2, §8.4 |
| `self-hosted-server` | `save-point-checkpoint` OR `event-sourced-replay` (workload-class-bound) OR `reconciler-loop` (K8s-resident) | Pipeline-automation per Persona §8.3 spine territory → `event-sourced-replay`; software-engineering / research mixed → `save-point-checkpoint` with composition-discipline; `pure-pattern-no-engine` **excluded** for durable pole at this surface per D1 §1.2 |
| `managed-cloud` | `event-sourced-replay` (dominant) | Engine-class commitment uniform across workload classes at this surface; Persona §8.3 most rigorous retry/breaker/idempotency requirements compose natively |

**Cell exclusions inherit from D1 §1.2.** D5 §1.2 + D4 §1.4 + this contract observe the exclusions without re-deriving them; `pure-pattern-no-engine` at `self-hosted-server` and `managed-cloud` durable poles is structurally rejected.

### §7.3 Workload-binding-time selection contract

```
At workload-binding-time downstream of Phase 3:

1. Operator declares deployment surface (local-development | self-hosted-server | managed-cloud).
2. Operator declares workload class (software-engineering | content-creation |
   pipeline-automation | research | extension-class per Persona §3.2).
3. Cell at (deployment-surface × workload-class) lookup at §7.2 yields the candidate
   engine-class set.
4. Operator selects specific engine candidate from the cell's recommended set meeting
   the F3 v1.1 capability-floor (i)-(iv) (preserved across classes per D1 §1.4).
5. The selected engine class is bound at workflow manifest per C-CP-06 §6.1
   `engine_class` field; per-step opt-in override is bounded by the cell per C-CP-06 §6.3.
```

### §7.4 Capability-floor preservation per class

Per ADR-D1 v1.1 §1.4 (preserved verbatim from substrate read):

| F3 capability-floor | event-sourced-replay | save-point-checkpoint | pure-pattern-no-engine | reconciler-loop | WAL-segment |
|---|---|---|---|---|---|
| (i) Durable replay across restart | Engine event history | Checkpointer state + harness composition | F2 filesystem-journal + state-ledger | etcd + CRD events | WAL segment replay |
| (ii) Idempotency-keyed exactly-once via F2 ledger | F2 ledger joined on `idempotency_key` | F2 ledger joined on `idempotency_key` | F2 ledger native | F2 ledger joined; reconciler reads ledger | F2 ledger joined per segment |
| (iii) Lease coordination | Engine-native (Temporal placement; DBOS transaction) | Application-level (Redis / DB unique constraint / worktree per `Spec_Information_Substrate_v1.md` C-IS-09) | Harness-owned (worktree isolation per C-IS-09) | etcd compare-and-swap | Per-segment harness-owned |
| (iv) Observable lifecycle | Eight events per C-CP-05 §5.1 — engine emits via engine-event-bridge to OTel | Eight events per C-CP-05 §5.1 — harness emits at save-point boundaries | Eight events per C-CP-05 §5.1 — harness emits at filesystem-journal cadence | Eight events per C-CP-05 §5.1 — CRD reconciler emits | Eight events per C-CP-05 §5.1 — WAL emits at segment boundaries |

**Deferred to implementation discretion.** Specific engine candidate within each cell (Temporal / DBOS / Restate at event-sourced-replay; LangGraph + SqliteSaver vs LangGraph + Postgres at save-point-checkpoint; specific WAL implementation at WAL-segment class); specific candidate enumeration update procedure under Workflow §4.1.2 Class-2 revision; specific F3-capability-floor verification at workload-binding time.

---

## §8 C-CP-08 — Replay-resumption semantics per engine class (R-CP-07 — F2-12 active engagement)

**Contract surface.** Per-engine-class resumption-kind enum + per-class resumption observable behavior + composition with F2 state-ledger via `idempotency_key`.

**PRD requirement(s) satisfied.** R-CP-07 (replay-resumption semantics visible at run resumption).

**ADR commitment(s) honored.** ADR-D1 v1.1 §1.1 engine-class taxonomy; ADD §3.1.1 Synthesis. **F2-12 active engagement** — per `Phase_5_Session_3_Session_Prompt.md` §5.4 [CF-1] authoring approach (iii), this contract authors at the current D1 v1.1 commitment level (replay semantics as currently committed at D1 §1.1 + engine-class taxonomy per §1.2) and flags the F2-12 carry-forward at the §[carry-forwards] [CF-1] with explicit forward-routing.

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-05 (state-ledger entry shape); C-IS-10 §10.2 (idempotency-key join export, with F2-12 carry-forward note in line).

**Persona linkage.** Persona §4 (99.9% SLO; durable replay across restart); §10.4 (compliance-readiness); §11.3 (long-tail duration of durable pole).

**Specification content.**

### §8.1 Per-engine-class resumption-kind enum

The `resumption.kind` attribute carried on the `workflow.resumption` span (declared at C-CP-05 §5.2) takes the following values, one per D1 §1.1 engine class:

| `resumption.kind` | Engine class | Observable behavior at run resumption |
|---|---|---|
| `engine_replay` | `event-sourced-replay` | Prior steps replay from Event History deterministically; activity outputs cached and replayed; no re-execution of activities |
| `save_point_resume` | `save-point-checkpoint` | Resume from save-point; harness composes lease + dedup against F2 state-ledger via `idempotency_key` per C-IS-10 §10.2 |
| `journal_resume` | `pure-pattern-no-engine` | Replay from F2 filesystem-journal + state-ledger; harness-owned dedup against `idempotency_key` |
| `reconciler_converge` | `reconciler-loop` | Re-derive state from declarative CRDs; reconciler-loop converges through compare-and-swap |
| `segment_replay` | `WAL-segment` | Replay from WAL segments; per-segment dedup |

The `resumption.kind` attribute is **always-emitted** on `workflow.resumption` spans (per C-CP-05 §5.4 always-sampled discipline). The production-time operator perceives the resumption-kind via run-event inspection per R-CP-07 acceptance criterion.

### §8.2 Composition with F2 state-ledger via `idempotency_key`

Per `Spec_Information_Substrate_v1.md` C-IS-05 + C-IS-10 §10.2:

| Engine class | F2 join discipline at resumption |
|---|---|
| `event-sourced-replay` | Engine event history joins F2 state-ledger on `idempotency_key` per C-IS-10 §10.2; engine-internal eventId (`engine.event.id` per C-CP-09 §9.1) is engine-naming; `idempotency_key` is harness-canonical join |
| `save-point-checkpoint` | Checkpointer state joins F2 state-ledger on `idempotency_key`; harness composition layer reads F2 entries by `action_id` and applies dedup per `prior_event_hash` chain integrity (C-IS-06) |
| `pure-pattern-no-engine` | F2 state-ledger native — `idempotency_key` is the primary dedup substrate; replay reads F2 entries chronologically per C-IS-07 read contract |
| `reconciler-loop` | CRD events join F2 state-ledger on `idempotency_key`; reconciler reads ledger to detect prior actions |
| `WAL-segment` | Per-segment ledger entries join F2 on `idempotency_key`; segment-resume reads per-segment metadata |

### §8.3 Resumption observable behavior

Per R-CP-07 acceptance criterion, at resumption the run-event surface reflects:

```
On workflow restart:
  1. F3 capability-floor (iv) emits workflow.resumption span (always-sampled per C-CP-05 §5.4)
       with attrs: workflow.id, engine.class, resumption.kind per §8.1
  2. Subsequent step.boundary spans carry attribute resumption.is_replay : bool
       (true if step is replaying from prior run; false if step is post-resumption new work)
  3. Per-event-class span emission discipline under replay scenarios is governed by F2-12
       carry-forward (see §[carry-forwards] [CF-1]); the v1 commitment is the resumption-kind
       enum + idempotency-key join; the v1.2 closure will commit span-re-emission semantics
       per engine class.
```

### §8.4 F2-12 carry-forward affected-contract notation

Per `Phase_5_Session_3_Session_Prompt.md` §5.4 [CF-1] authoring approach (iii):

> This contract is the R-CP-07-satisfying contract per PRD §[carry-forwards] [CF-1] active engagement. F2-12 (D1 v1.1 → v1.2 replay-trace-emission contract) covers (i) span re-emission semantics under engine replay (event-sourced-replay engines: do spans re-emit, or is replay a deterministic re-read without new span emission?); (ii) `retry.attempt` sibling-span discipline (does the retry emit `retry.attempt` event AND a new sibling span per D6 §1.2?); (iii) trace-ingestion dedup composition with F2 `idempotency_key` (cost-attribution-per-span at D6 §1.5 must avoid double-counting on replay). All three sub-scopes are **out of scope at this spec revision** and route to the parallel `council-orchestrator` C7+C9 session per ADD §6.3.1 active path. Closure expected as D1 v1.2 + D6 v1.2; absorbed into ADD v1.3; PRD revision pass produces `PRD_v1.1.md`; Control Plane spec revision pass at this contract (`Spec_Control_Plane_v1.1.md` C-CP-08) and Operational Discipline spec revision at the corresponding cost-attribution-per-span contract (session 4 territory).

**Deferred to implementation discretion.** Specific span-re-emission semantics under engine replay (F2-12 carry-forward); specific `resumption.kind` to engine-vendor-event mapping; specific replay-deterministic-re-read implementation per engine vendor; specific tail-keep-on-replay sampling policy at D6 ingestion (session 4 + F2-12 closure interaction).

---

## §9 C-CP-09 — `engine.*` span attribute namespace declaration

**Contract surface.** Three `engine.*` attribute names + per-attribute type + per-attribute cardinality + per-attribute always-emitted scope + composition with §1.1 taxonomy materialization at D6 §1.2.

**PRD requirement(s) satisfied.** R-CP-04 (workflow lifecycle event surface — `engine.class` attribute substrate); R-CP-06 (engine class committed per deployment surface — observability surface); R-CP-07 (replay-resumption semantics — `engine.event.id` join surface).

**ADR commitment(s) honored.** ADR-D1 v1.1 §1.1.1 (canonical declaration site for `engine.*` attribute names); ADR-D6 v1.1 §1.2 row `engine.*` (D6 ingests without re-declaration per F2-07 closure).

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-05 (`idempotency_key` field — harness-canonical join key); C-IS-10 §10.2 (idempotency-key join export — engine event history consuming surface).

**Persona linkage.** Persona §10.2 (cost-attribution-per-span foundational primitive); §10.4 (compliance-readiness — comprehensive observability).

**Specification content.**

### §9.1 Three `engine.*` attribute declarations

Per ADR-D1 v1.1 §1.1.1:

| Attribute | Type | Cardinality | Always-emitted on | Discriminator role |
|---|---|---|---|---|
| `engine.class` | enum string ∈ `{event-sourced-replay, save-point-checkpoint, pure-pattern-no-engine, reconciler-loop, WAL-segment}` | bounded (5) | Every span emitted under D1 §1.1's lifecycle envelope (the eight events per C-CP-05 §5.1) | Closed enumeration of D1 §1.1 rows; stable discriminator for engine-class-conditional sampling and dashboard binding |
| `engine.event_history.tier` | enum string ∈ `{Tier-3, Tier-5}` | bounded (2) | Span events that reference engine-internal durable state OR state-ledger join surface | `Tier-3` = engine-internal durable substrate per D1 §1.1 *C3-tier residence* column; `Tier-5` = F2 state-ledger join surface |
| `engine.event.id` | opaque string under each engine class's native ID convention (Temporal eventId; LangGraph checkpoint_id; ACP CRD event UID; Kode-Agent segment offset; pure-pattern harness-assigned UUID) | per-event | Span events referencing a specific engine-internal event | Engine-internal naming; cross-engine-class portability via `idempotency_key` join on F2 |

### §9.2 Per-row Tier-3 / Tier-5 mapping

Per ADR-D1 v1.1 §1.1.1 (inherited from §1.1 *C3-tier residence* column):

| Engine class | `engine.event_history.tier=Tier-3` surfaces | `engine.event_history.tier=Tier-5` surfaces |
|---|---|---|
| `event-sourced-replay` | Engine event history (Temporal Event History; DBOS transaction log) | F2 state-ledger entries joined on `idempotency_key` |
| `save-point-checkpoint` | Checkpointer state (LangGraph SqliteSaver / PostgresSaver / DynamoDBSaver) | F2 state-ledger entries |
| `pure-pattern-no-engine` | F2 filesystem-journal | F2 state-ledger entries |
| `reconciler-loop` | K8s etcd | CRD events |
| `WAL-segment` | WAL segments | Segment metadata |

### §9.3 Composition with C-IS-10 §10.2 idempotency-key join

Per `Spec_Information_Substrate_v1.md` C-IS-10 §10.2: `idempotency_key` is the harness-canonical cross-axis join key. `engine.event.id` is engine-internal naming; the join from engine event to F2 state-ledger entry is `engine.event.id × idempotency_key` lookup against the F2 state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` per C-IS-05.

### §9.4 D6 ingestion contract

Per ADR-D6 v1.1 §1.2 row `engine.*`: D6 ingests this attribute set verbatim without re-declaration. Session 4 Operational Discipline spec at C-OD-* (D6 unified span schema) consumes this contract by citation; the cell sampling discipline per D6 §1.3 applies.

**Deferred to implementation discretion.** Specific `engine.event.id` serialization format per engine candidate; specific cross-engine-class span correlation library at D6 ingestion (session 4 territory); specific tail-keep-on-engine-class-equals-X discipline at D6 sampling (session 4 territory).

---

## §10 C-CP-10 — Six-pattern multi-agent topology taxonomy

**Contract surface.** Closed six-pattern enumeration + per-pattern lifecycle-ownership + per-pattern primary candidates + workflow-definition surface declaration.

**PRD requirement(s) satisfied.** R-CP-08 (multi-agent topology selectable at workflow definition).

**ADR commitment(s) honored.** ADR-D4 v1.1 §Decision (six-component multi-agent topology specification — taxonomy half); ADR-D4 v1.1 §1.1 (six-pattern topology taxonomy table); ADD §3.1.2 Synthesis.

**Persona linkage.** Persona §3.1 (four primary workload classes); §3.2 (workload-class extensibility flag — topology-above-engine viability); §3.3 (work-unit shape distribution heterogeneous — multi-pattern accommodation within single class); §7 (workflow-definition surface).

**Specification content.**

### §10.1 Six-pattern topology taxonomy

The taxonomy is **closed** at D4 §1.1; extension is a Workflow §4.1.2 Class-2 D4 revision.

| # | Pattern | Lifecycle ownership | Cross-framework equivalences (Cluster 1 §3 [HIGH]) |
|---|---|---|---|
| 1 | `single-threaded-linear` | Sole agent owns full lifecycle | 12-Factor Factor 10 small-focused-agents; Cognition-canonical for write-heavy work |
| 2 | `orchestrator-workers` | Lead decomposes; workers execute concurrently; lead synthesizes | OpenAI manager pattern ≡ Anthropic orchestrator-workers ≡ revfactory/harness Supervisor (Cluster 1 §3 [HIGH]) |
| 3 | `decentralized-handoff` | Each agent owns until handoff; recipient owns post-handoff | OpenAI decentralized ≡ Microsoft handoff (Cluster 1 §3 [HIGH]) |
| 4 | `hierarchical-delegation` | Parent owns until delegation; child owns sub-task; recursion permitted | Cognition manager-Devin spawning child-Devins; revfactory/harness Hierarchical Delegation |
| 5 | `evaluator-optimizer` | Generator + evaluator(s) in loop until convergence | Anthropic Building Effective Agents evaluator-optimizer; revfactory/harness Producer-Reviewer |
| 6 | `parallelization` | Independent agents on independent sub-tasks; aggregator merges | Anthropic Building Effective Agents parallelization (sectioning + voting) |

### §10.2 Workflow-definition surface declaration

Per R-CP-08 acceptance criterion: each of the six topology patterns is **selectable at workflow definition** via the manifest entry per C-CP-06 §6.1 `topology` field:

```
TopologyDeclaration {
    pattern          : "single-threaded-linear" | "orchestrator-workers" |
                       "decentralized-handoff" | "hierarchical-delegation" |
                       "evaluator-optimizer" | "parallelization"
    fan_out_cap      : int  // per-pattern bound per C-CP-11 §11.1 per-workload-class commitment
    cascade_policy   : "pause" | "proceed" | "cascade-cancel"  // per C-CP-17 §17.1.1
    writer_serialization : "strict" | "relaxed"  // per C-CP-11 §11.1
    sub_agent_briefs : Optional<List<SubAgentBrief>>  // per C-CP-13 §13.2
}
```

The per-workload-class default applies when no operator override is declared (per C-CP-11 §11.1 mapping); operator override at the manifest entry takes precedence.

### §10.3 Cross-pattern admissibility per workload class

Per ADR-D4 v1.1 §1.2 admissibility annotations:

```
hierarchical-delegation : admissible at software-engineering and research workloads
                          when scope-bounded recursion is justified
                          (Cognition manager-Devin pattern); fan-out cap 3 per parent;
                          cascade-policy inherits parent cell
decentralized-handoff   : admissible at pipeline-automation per-stage-expert workflows
                          (mvschwarz/openrig RigSpec); cascade-policy `cascade-cancel`;
                          single-owner-at-a-time invariant
parallelization         : admissible at research breadth-search and content-creation
                          A/B-variant generation; cap 3–5; voting aggregator at synthesis
```

Non-primary patterns are admissible but not primary; the workflow-definition surface MUST accept them at the cells where they are admissible.

**Deferred to implementation discretion.** Specific candidate-within-pattern selection at workload-binding-time per ADR-D4 v1.1 §1.11; specific manifest-validation library for topology-pattern-vs-workload-class admissibility check; specific cascade-policy default propagation at hierarchical-delegation recursion.

---

## §11 C-CP-11 — Per-workload-class topology commitment + 2D matrix workload-class × engine-class

**Contract surface.** Per-workload-class commitment table (4 rows × 5 columns: topology pattern + fan-out cap + cascade-policy default + writer-serialization stance + per-engine-class implementation mechanism overlay) + 2D matrix workload-class × D1-engine-class committing T-perm-3 reading per cell.

**PRD requirement(s) satisfied.** R-CP-08 (multi-agent topology selectable at workflow definition — per-workload-class default half).

**ADR commitment(s) honored.** ADR-D4 v1.1 §1.2 (per-workload-class topology commitment table); ADR-D4 v1.1 §1.3 (per-engine-class implementation mechanism overlay); ADR-D4 v1.1 §1.4 (2D matrix workload-class × D1-engine-class); ADR-D4 v1.1 §1.6 (T-perm-3 D4-layer multiplicative tunable parameter specialization); ADD §3.1.2 Synthesis + §5.2.3 T-perm-3 multi-layer resolution.

**Cross-axis citation.** `Spec_Action_Surface_v1.md` C-AS-13 §13.4 (per-sub-agent-role × model-binding contract — lead/orchestrator binding inheritance at brief authoring).

**Persona linkage.** Persona §8.1 (software engineering: evaluator-optimizer + orchestrator-workers); §8.2 (content creation: evaluator-optimizer); §8.3 (pipeline automation: sequential default); §8.4 (research: orchestrator-workers); §3.2 (workload-class extensibility flag); §4 (99.9% SLO forces fan-out cap ceilings); §6 (per-class cost ceiling forces cap cost-tunability).

**Specification content.**

### §11.1 Per-workload-class topology commitment

Per ADR-D4 v1.1 §1.2:

| Workload class | Primary topology pattern | Sub-agent fan-out cap | Cascade-policy default | Writer-serialization stance |
|---|---|---|---|---|
| `software-engineering` (Persona §3.1.1, §8.1) | `evaluator-optimizer` (writes); `orchestrator-workers` (reads/review/eval) | writes: 1 generator + 1–3 evaluators; reads: 3 max | writes: `pause` (HITL escalation per C-CP-17 §17.1 validator-escalation); reads: `proceed` | **strict** — single-threaded writer per Cognition strong-convergence (Cluster 1 §1 [HIGH]); merge through generator only |
| `content-creation` (Persona §3.1.2, §8.2) | `evaluator-optimizer` (operator-as-reviewer dominant at design-time) | 1 generator + 1–2 evaluators | `pause` | **strict** — single-threaded author |
| `pipeline-automation` (Persona §3.1.3, §8.3) | sequential default; `orchestrator-workers` for idempotent parallel stages only | 3 max (deer-flow witness per Cluster 1 §[HIGH]) | `cascade-cancel` | **strict** — sequential durable spine; parallel only on idempotent stages |
| `research` (Persona §3.1.4, §8.4) | `orchestrator-workers` (Anthropic research system canonical per Cluster 1 §[HIGH]) | 3–5 (Anthropic [HIGH]) | `proceed` (lossy synthesis acceptable) | **relaxed** — parallel breadth-search; lead synthesizes |

### §11.2 Per-engine-class implementation mechanism overlay

Per ADR-D4 v1.1 §1.3:

| D1 engine class | Cascade-enforcement mechanism | Writer-serialization mechanism | Per-sibling lease coordination | T-perm-3 reading |
|---|---|---|---|---|
| `event-sourced-replay` | Engine-native: workflow timeout + child-workflow cancellation API | Engine-native task-queue partitioning by `thread_id`; activity-level mutex | Engine-native lease per C-CP-09 §9.2 row 1 | **`BELOW_ENGINE`** — engine owns lifecycle; harness authors topology atop |
| `save-point-checkpoint` | Application-level: harness-owned cascade timeout + node cancellation | Application-level: parent node's `interrupt_before_writers` checkpoint barrier | Application-level (Redis lease, DB unique constraint, worktree isolation per `Spec_Information_Substrate_v1.md` C-IS-09) | **`ABOVE_ENGINE`** — harness owns topology and durability composition |
| `pure-pattern-no-engine` | Harness-owned: filesystem-journal + state-ledger cascade marker | Harness-owned: F2 state-ledger entry serialization on writer slot per `Spec_Information_Substrate_v1.md` C-IS-05 | Harness-owned (worktree isolation per C-IS-09; DB unique constraint) | **`ABOVE_ENGINE`** — harness owns full durability contract |
| `reconciler-loop` | Reconciler-native: CRD status reconciliation + child-CRD cancellation events | etcd compare-and-swap on writer-CRD spec | etcd compare-and-swap | **`RECONCILER`** — control-loop owns reconvergence |
| `WAL-segment` | Per-segment harness-owned: cascade-marker segment + segment-resume on restart | Harness-owned: per-segment writer-slot lease | Harness-owned per-segment lease | **`ABOVE_ENGINE`** — harness owns WAL + topology |

### §11.3 2D matrix: workload-class × D1-engine-class with per-cell T-perm-3 reading

Per ADR-D4 v1.1 §1.4 (preserved verbatim):

| workload \ engine-class | event-sourced-replay | save-point-checkpoint | pure-pattern-no-engine | reconciler-loop | WAL-segment |
|---|---|---|---|---|---|
| **software-engineering** | `BELOW_ENGINE`; engine cancellation API; activity-level write-mutex | `ABOVE_ENGINE`; harness cascade timeout; checkpoint barrier on writes | `ABOVE_ENGINE`; F2-ledger writer-slot serialization | `RECONCILER`; CRD reconciliation; rare for SE | `ABOVE_ENGINE`; segment-resume EO loop |
| **content-creation** | `BELOW_ENGINE`; engine timeout; rare at this surface | `ABOVE_ENGINE`; harness-owned EO loop | `ABOVE_ENGINE`; filesystem-journal default | `RECONCILER`; rare | `ABOVE_ENGINE`; segment-resume |
| **pipeline-automation** | `BELOW_ENGINE`; engine-native fail-fast; idempotency-key engine-bound | `ABOVE_ENGINE`; **composition-discipline required** per C-CP-07 §7.2 self-hosted-server row | `ABOVE_ENGINE`; **excluded for durable pole at scale** per C-CP-07 §7.2 | `RECONCILER`; ACP CRD-native; hierarchical-delegation acceptable | `ABOVE_ENGINE`; per-segment fail-fast |
| **research** | `BELOW_ENGINE`; engine `wait_condition` natural fit for breadth-search | `ABOVE_ENGINE`; harness OW with checkpoint at synthesis barrier | `ABOVE_ENGINE`; lightweight; well-suited for solo-developer × research | `RECONCILER`; rare | `ABOVE_ENGINE`; per-segment OW |

Cells reading "rare" or "excluded" inherit C-CP-07 §7.2 candidate-set exclusions; this contract introduces no new exclusions.

### §11.4 T-perm-3 D4-layer multiplicative tunable specialization

Per ADR-D4 v1.1 §1.6, the tunable parameter is specialized to:

```
topology_fault_handling × workload_class × topology_pattern

where:
    topology_fault_handling ∈ {ABOVE_ENGINE, BELOW_ENGINE, RECONCILER}      (D1-layer, inherited)
    workload_class          ∈ {software-engineering, content-creation,
                               pipeline-automation, research}              (D4-layer, new)
    topology_pattern        ∈ {single-threaded-linear, orchestrator-workers,
                               decentralized-handoff, hierarchical-delegation,
                               evaluator-optimizer, parallelization}       (D4-layer, new)
```

Composition layering per ADD §5.2.3:

```
F1-layer resolution         per-layer time-budget shape (C-CP-03 §3.1)
       +
D1-layer resolution         topology_fault_handling per deployment surface
                            (C-CP-07 §7.2)
       +
D4-layer resolution         topology_fault_handling × workload_class × topology_pattern
                            (this contract §11.3)
       =
Concrete fault-handling     resolved at deployment-surface-time × workload-binding-time;
binding                     per-cell cascade-enforcement mechanism per §11.2
```

The tension is **structural to the slate** per ADD §5.2.3 and is not collapsed at any layer. C1's `ABOVE_ENGINE` reading is correct at save-point and pure-pattern cells; C9's `BELOW_ENGINE` reading is correct at event-sourced-replay cells; C9's `RECONCILER` reading is correct at K8s-resident reconciler-loop cells.

**Deferred to implementation discretion.** Specific cell-binding selection at workload-binding-time per C-CP-07 §7.3; specific cascade-enforcement library binding per engine class; specific `cascade-cancel` propagation timing per topology pattern; specific writer-slot serialization mechanism at pure-pattern-no-engine + pipeline-automation cells (excluded at scale per §11.3).

---

## §12 C-CP-12 — Sub-agent privilege inheritance contract with monotonic-only descent

**Contract surface.** Default-downgrade rule per blast-radius tier + sub-agent gate-level composition formula + monotonic-only sandbox-tier composition with C-AS-11 + per-class override surface.

**PRD requirement(s) satisfied.** R-CP-09 (sub-agent privilege inheritance with monotonic-only descent).

**ADR commitment(s) honored.** ADR-D4 v1.1 §1.5 (sub-agent privilege inheritance contract with default-downgrade rule per blast-radius tier); ADR-D2 v1.1 §1.4 (sub-agent sandbox-tier monotonic-ascension — Action Surface cross-axis); ADD §5.3.2 sub-agent boundary as monotonic-only descent.

**Cross-axis citation.** `Spec_Action_Surface_v1.md` C-AS-11 (sub-agent sandbox-tier monotonic-ascension); `Spec_Action_Surface_v1.md` C-AS-12 (T-perm-1 D2-layer 5-axis multiplicative tunable composition surface).

**Persona linkage.** Persona §5.1 (computer-use at production-time with stronger sandbox tier); §10.4 (compliance-readiness foundational primitives — multi-tenant override prohibition).

**Specification content.**

### §12.1 Default-downgrade rule per blast-radius tier

Per ADR-D4 v1.1 §1.5:

```
sub_agent_tool_registry(parent_registry, blast_radius) =
    {
        read-only             : INHERIT (sub-agent receives parent's read-only tools as-is)
        local-mutation        : INHERIT (sub-agent receives parent's local-mutation tools as-is)
        external-reversible   : DOWNGRADE_TO_ASK (parent's `auto` becomes `ask` at sub-agent;
                                                  operator approves per-sub-agent at gate)
        external-irreversible : REMOVE (sub-agent registry omits the tool;
                                        parent must invoke directly post-synthesis)
    }
```

### §12.2 Sub-agent gate-level composition formula

Per ADR-D4 v1.1 §1.5 (composition with C-CP-19 D5-layer multiplicative rule):

```
sub_agent_gate_level(tool, mcp_server, persona_tier, parent_gate_level) =
    max(
        parent_gate_level,                        // monotonic ascending per C-CP-19 §19.2
        per_tool_gate_level,                      // C4 contract per C-CP-19 §19.1
        blast_radius_floor(tool),                 // C10 four-tier taxonomy per C-CP-19 §19.1
        per_mcp_server_trust_floor(mcp_server),   // C10 five-tier framework per C-CP-19 §19.1
        persona_tier_floor                        // per C-CP-19 §19.1
    )
```

### §12.3 Monotonic-only descent (composition with C-AS-11)

Per ADD §5.3.2 sub-agent boundary as monotonic-only descent + `Spec_Action_Surface_v1.md` C-AS-11:

| Dimension | Monotonicity contract | Source contract |
|---|---|---|
| `gate_level` | Sub-agent gate-level ≥ parent gate-level (this contract §12.2) | C-CP-12 + C-CP-19 |
| `sandbox_tier` | Sub-agent sandbox-tier ≥ parent sandbox-tier (`Spec_Action_Surface_v1.md` C-AS-11 monotonic-ascension) | C-AS-11 |
| `persona_tier` | Sub-agent inherits parent persona-tier; cross-deployment monotonic-ascending only | C-CP-19 §19.2 |

All three dimensions ascend jointly at sub-agent dispatch; downgrade attempts at any dimension are **structurally rejected** per ADD §5.3.2 and emit `sandbox.fail.class = policy_override` per `Spec_Action_Surface_v1.md` C-AS-04 §4.1.

### §12.4 Per-class override surface

Per ADR-D4 v1.1 §1.5 override clause:

| Override scope | Permitted | Rationale |
|---|---|---|
| Child agents own `external-reversible` authority at `hierarchical-delegation` with explicit operator declaration | **Permitted** at solo-developer + team-binding (with audit ledger entry per C-CP-20); per-sub-agent-class declaration at workload-binding-time | Cognition manager-Devin pattern; child writes are part of the workload contract |
| Child agents own `external-irreversible` authority | **Structurally prohibited** at all persona tiers | C10 four-tier taxonomy: external-irreversible requires parent-mediated execution; no sub-agent override admitted |
| Sub-agent sandbox-tier downgrade | **Structurally prohibited** at all persona tiers per `Spec_Action_Surface_v1.md` C-AS-11 monotonic-ascension | Sandbox-tier ascension is unconditional per ADR-D2 v1.1 §1.4 |

### §12.5 Audit-ledger discipline at sub-agent dispatch

Per R-CP-09 acceptance criterion: audit-ledger entries for sub-agent dispatch carry:

```
sub_agent_dispatch_audit_entry {
    action_id            : parent_action_id || sub_agent_idx
    idempotency_key      : sha256(parent_action_id, sub_agent_idx, brief_hash)
    actor                : parent agent identity
    response_hash        : sha256(canonicalize(SubAgentBrief))  // brief per C-CP-13 §13.2
    timestamp            : ISO-8601
    prior_event_hash     : <prior entry per C-IS-06 §6.1>
    // sub-agent-dispatch-specific extension fields:
    sub_agent.parent_gate_level : ...
    sub_agent.resolved_gate_level : ... (per §12.2 max() output)
    sub_agent.parent_sandbox_tier : ...
    sub_agent.resolved_sandbox_tier : ... (per C-AS-11 monotonic-ascension)
}
```

The audit-ledger entry is written per the persona-tier cryptographic shape per C-CP-20 §20.1. Sub-agent boundary violations (downgrade attempt) emit `sandbox.violation` events per `Spec_Action_Surface_v1.md` C-AS-15 §15.1 with `sandbox.fail.class = policy_override`.

**Deferred to implementation discretion.** Specific operator override authoring schema for hierarchical-delegation child external-reversible; specific brief-hash canonicalization library binding (composes with C-CP-13 §13.2); specific sub-agent-dispatch span emission timing (pre-dispatch vs concurrent-with-dispatch); specific override-conflict resolution at runtime when parent and sub-agent gate-level computations diverge under operator policy change.

---

## §13 C-CP-13 — HandoffContext + brief object structure

**Contract surface.** HandoffContext payload schema + brief object schema for orchestrator-workers cells + brief-authoring model-binding inheritance.

**PRD requirement(s) satisfied.** R-CP-08 (multi-agent topology — sub-agent dispatch payload half); R-CP-09 (sub-agent privilege inheritance — HandoffContext audit composition).

**ADR commitment(s) honored.** ADR-D4 v1.1 §1.7 (HandoffContext serialization contract); ADR-D4 v1.1 §1.7 brief object structure for orchestrator-workers cells per Anthropic research system [HIGH].

**Cross-axis citation.** `Spec_Action_Surface_v1.md` C-AS-13 §13.4 (per-sub-agent-role × model-binding — lead/orchestrator binding inherited at brief authoring).

**Persona linkage.** Persona §8.1 (software engineering — sub-agent reads); §8.4 (research — orchestrator-workers Anthropic-canonical); §7 (workflow-definition surface — brief-authoring at lead-agent inference time).

**Specification content.**

### §13.1 HandoffContext payload schema

Per ADR-D4 v1.1 §1.7 (Cluster 4 §2.4.3 [HIGH] shape):

```
HandoffContext {
    proposed_action        : ProposedAction       // sub-agent's task scope statement
    agent_confidence       : Optional<Float>       // lead's prior estimate
    failed_attempts        : List<FailedAttempt>  // prior sub-agent failures on
                                                  //   the same task (cascade reattempt)
    alternatives_considered: List<Alternative>   // lead's deliberation context
    state_summary          : StateSummary         // F2 state-ledger entries relevant
                                                  //   to sub-agent's scope per
                                                  //   `Spec_Information_Substrate_v1.md` C-IS-05
    audit_trail_link       : LedgerEntryRef       // pointer to parent's audit ledger entry
                                                  //   per C-IS-10 §10.1 join surface
    retry_history          : RetryHistory         // C9 retry primitives state per `retry.*`
                                                  //   namespace at C-CP-03 §3.5
}
```

The HandoffContext is serialized at sub-agent dispatch (across-turn boundary; T-perm-2 adjacency per ADR-D4 v1.1 §1.7 — F2-layer resolution stands; HandoffContext crosses the seam without revising T-perm-2 commitments).

### §13.2 Brief object structure (orchestrator-workers cells)

Per ADR-D4 v1.1 §1.7 (Anthropic research system [HIGH]):

```
SubAgentBrief {
    objective       : String                      // single sentence; bounded scope
    output_format   : OutputSchema                // sub-agent's required output shape
    guidance        : String                      // approach hints; non-prescriptive
    task_boundaries : ClearTaskBoundaries         // explicit scope-limit declaration;
                                                  //   prevents sub-agent scope-creep
}
```

The brief object is authored by the lead agent and embedded in `HandoffContext.proposed_action` at orchestrator-workers cells. The brief is **authored at lead-agent inference time**; brief-authoring inference cost is absorbed by the lead agent at the workflow-class-bound model tier (per §13.3 below).

### §13.3 Brief-authoring model-binding inheritance

Per `Spec_Action_Surface_v1.md` C-AS-13 §13.4 + ADR-D3 v1.2 §1.4 brief-authoring NOT-reducible-to-Haiku clause:

| Workload class | Lead-agent model binding (cited from C-AS-13 §13.4) | Brief-authoring inheritance |
|---|---|---|
| `software-engineering` | Sonnet 4.6 default; Opus 4.6 at multi-tenant-compliance | Inherits lead binding (NOT reducible to Haiku) |
| `content-creation` | Sonnet 4.6 | Inherits lead binding |
| `pipeline-automation` | Sonnet 4.6 per-stage default; Haiku 4.5 high-volume idempotent | Inherits per-stage lead binding |
| `research` | Sonnet 4.6 default; Opus 4.6 multi-tenant-compliance high-fidelity | Inherits lead binding |

The brief-authoring binding is **not configurable independently** from lead-agent binding; brief authoring composes against the lead's model context to ensure brief specificity sufficient to prevent sub-agent scope-creep.

### §13.4 State summary composition with C-IS-05

Per `Spec_Information_Substrate_v1.md` C-IS-05 + C-IS-10 §10.1:

```
StateSummary {
    relevant_entries  : List<LedgerEntryRef>  // pointers to F2 state-ledger entries
                                              //   relevant to sub-agent scope
    summary_text      : String                 // human-readable summary
                                              //   (operator-readable at trace surface)
    summary_hash      : SHA-256                // canonicalize+hash of summary_text;
                                              //   composes with F2 entry's response_hash
    idempotency_key   : string                 // harness-canonical join key per C-IS-10 §10.2;
                                              //   propagated to sub-agent for replay-safe re-dispatch
}
```

### §13.5 Audit-trail-link composition with C-IS-10 §10.1

Per `Spec_Information_Substrate_v1.md` C-IS-10 §10.1 state-ledger entry shape export — Control Plane row:

```
LedgerEntryRef {
    action_id        : <parent action_id per F2 six-field shape>
    entry_hash       : SHA-256  // entry's response_hash per F2 entry shape
    actor            : <parent actor identity>
}
```

The audit-trail-link enables tracing sub-agent execution back to the parent ledger entry; merkle-root composition at fan-out close per C-CP-15 §15.2.

**Deferred to implementation discretion.** Specific HandoffContext serialization format (JSON / protobuf / engine-vendor-format); specific `StateSummary` summarization model invocation per persona tier (per C-CP-21 §21.4 summarization model table); specific `task_boundaries` declarative schema; specific `RetryHistory` cardinality cap at HandoffContext payload boundary.

---

## §14 C-CP-14 — Multi-agent span hierarchy + concurrent-prompt-cache warm-up

**Contract surface.** Span hierarchy schema for fan-out + topology.fanout.opened / subagent.span / topology.fanout.closed attribute schema + per-span sampling discipline + concurrent-prompt-cache warm-up protocol.

**PRD requirement(s) satisfied.** R-CP-08 (multi-agent topology — observability surface half).

**ADR commitment(s) honored.** ADR-D4 v1.1 §1.8 (concurrent-prompt-cache warm-up protocol); ADR-D4 v1.1 §1.9 (multi-agent span hierarchy schema); ADD §3.1.2 Synthesis.

**Cross-axis citation.** `Spec_Action_Surface_v1.md` C-AS-15 (sandbox-bounded span schema — composition shape: spans nest as `subagent.span[i] → sandbox.enter → tool.call → sandbox.exit`); `Spec_Action_Surface_v1.md` C-AS-14 §14.2 (anthropic.* namespace — `anthropic.cache_*` attributes on `llm.inference` spans inside `subagent.span[i]`).

**Persona linkage.** Persona §4 (99.9% SLO — fan-out cap ceilings); §10.2 (cost-attribution-per-span — fan-out boundaries for sibling rollup); §10.4 (compliance-readiness — multi-agent span hierarchy tamper-evidence anchor).

**Specification content.**

### §14.1 Multi-agent span hierarchy

Per ADR-D4 v1.1 §1.9:

```
parent_session                                   (root span — workflow.start per C-CP-05 §5.1)
├── topology.fanout.opened                       (attrs: topology.pattern, topology.fan_out_cap,
│                                                          topology.cascade_policy,
│                                                          topology.workload_class,
│                                                          engine.class per C-CP-09,
│                                                          topology.concurrent_token_budget_at_dispatch)
├── subagent.span[0]                             (child span; trace_id propagated;
│   │                                             parent_span_id = topology.fanout.opened)
│   ├── llm.inference[]                          (per-sibling inference; cost attribution
│   │                                             per Anthropic ~15× chat-token budget [HIGH];
│   │                                             carries anthropic.* per C-AS-14 §14.2)
│   ├── sandbox.enter                            (per `Spec_Action_Surface_v1.md` C-AS-15 §15.1)
│   ├── tool.call[]                              (per-sibling tool spans;
│   │                                             gate_level_computed per C-CP-12 §12.2)
│   ├── sandbox.exit                             (per C-AS-15 §15.1)
│   ├── hitl.gate.evaluated                      (per C-CP-20 §20.5 schema; if gate triggered)
│   └── subagent.span.closed                     (attrs: subagent.result_status,
│                                                          subagent.request_blocked_by_budget,
│                                                          subagent.tokens_in, subagent.tokens_out,
│                                                          subagent.cached_tokens_in)
├── subagent.span[1] ... [N-1]                   (siblings; concurrent or serialized
│                                                  per §14.3 warm-up protocol)
└── topology.fanout.closed                       (attrs: topology.results_collected,
                                                          topology.results_failed,
                                                          topology.cascade_applied,
                                                          topology.synthesis_token_budget,
                                                          topology.cascade_decision_audit_ledger_id)
```

### §14.2 `topology.*` + `subagent.*` span attribute namespaces

| Namespace | Attribute | Type | Cardinality |
|---|---|---|---|
| `topology.*` | `topology.pattern` | enum string per C-CP-10 §10.1 (six values) | bounded (6) |
| | `topology.fan_out_cap` | int | low (per cell) |
| | `topology.cascade_policy` | enum string ∈ `{pause, proceed, cascade-cancel}` | bounded (3) |
| | `topology.workload_class` | enum string per Persona §3.1 four-class set | bounded (4 + extension flag) |
| | `topology.concurrent_token_budget_at_dispatch` | int (tokens) | unbounded (metric) |
| | `topology.results_collected` | int | bounded (≤ fan_out_cap) |
| | `topology.results_failed` | int | bounded (≤ fan_out_cap) |
| | `topology.cascade_applied` | bool | binary |
| | `topology.synthesis_token_budget` | int | unbounded (metric) |
| | `topology.cascade_decision_audit_ledger_id` | string (entry id) | per-fanout |
| `subagent.*` | `subagent.span.id` | string | per-sibling |
| | `subagent.parent_span_id` | string | per-sibling |
| | `subagent.result_status` | enum string ∈ `{completed, failed, cascade-cancelled}` | bounded (3) |
| | `subagent.request_blocked_by_budget` | bool | binary |
| | `subagent.tokens_in` | int | unbounded (metric) |
| | `subagent.tokens_out` | int | unbounded (metric) |
| | `subagent.cached_tokens_in` | int | unbounded (metric; per anthropic.cache_read_input_tokens per C-AS-14 §14.2) |

### §14.3 Sampling discipline

Per ADR-D4 v1.1 §1.9 + `c7-observability` SKILL.md sampling discipline:

| Span | Sampling rate | Rationale |
|---|---|---|
| `topology.fanout.opened` / `topology.fanout.closed` | **Always-sampled (head=1.0)** | Tamper-evidence-relevant under Persona §10.4; cost attribution requires fan-out boundaries |
| `subagent.span` | head-based-dev base-rate; **tail-keep-on-result-status=failed (always-sampled)** | Per-sibling failure observability; volume-bounded at success |
| `subagent.span.closed` | **Always-sampled (head=1.0)** | Cost-attribution rollup at fan-out close requires complete sibling closures |

### §14.4 Concurrent-prompt-cache warm-up protocol

Per ADR-D4 v1.1 §1.8 + Cluster 1 §[HIGH] cache-miss-storm prevention:

```
on_fanout_dispatch(siblings: List<SubAgent>, cache_breakpoint_id: String):
    1. lead_agent.persist_plan_to_filesystem(plan)
                                                  # CoALA episodic memory residence
                                                  # per Anthropic research system [HIGH]
                                                  # composes with `Spec_Information_Substrate_v1.md`
                                                  # C-IS-01 (filesystem path contract)
    2. dispatch siblings[0] synchronously
                                                  # cache-write at breakpoint per
                                                  # `Spec_Action_Surface_v1.md` C-AS-14 §14.2
                                                  # `anthropic.cache_breakpoint_id`
    3. await siblings[0].cache_acknowledgement OR
       await siblings[0].first_token_emission
                                                  # cache write completion proxy
    4. dispatch siblings[1..N-1] concurrently
                                                  # cache-hit on shared prefix
                                                  # (anthropic.cache_read_input_tokens at 0.10× cost
                                                  # per Cluster 1 V2 §2.2.2 [HIGH] cited at F1 §Rationale (b))
```

The protocol applies to **all cells where fan-out cap > 1** (orchestrator-workers, parallelization, evaluator-optimizer with multi-evaluator). Step 1 (plan persistence) is C2-owned context-engineering primitive composing orthogonally with topology pattern; steps 2–4 (warm-up serialization) are harness-owned.

### §14.5 Composition with cross-family fallback

Per `Spec_Action_Surface_v1.md` C-AS-13 §13.5 + C-CP-04 §4.3:

| Property | Contract |
|---|---|
| Cross-family fallback during fan-out | If any sibling triggers cross-family fallback (per C-CP-04 §4.3), `prompt_cache.invalidated` event emits at the affected sibling; the remaining siblings continue with their warmed cache at the primary family |
| Cache state at synthesis | Lead synthesis at fan-out close MAY re-warm the cache if the synthesis prompt diverges from the warmed prefix; warm-up protocol §14.4 applies to the synthesis call only if subsequent calls follow within the same workflow boundary |

**Deferred to implementation discretion.** Specific cache acknowledgement signal protocol (vendor-specific); specific first-token-emission detection mechanism; specific synthesis-prompt cache-prefix optimization; specific `tools[]` array warm-up cycle at restart per Cluster 2 V2 §[HIGH] (composes with `Spec_Action_Surface_v1.md` C-AS-13 §13.6).

---

## §15 C-CP-15 — Cross-sibling audit-ledger discipline

**Contract surface.** Per-sibling F2 ledger entry composition + parent_fanout_close_entry separate-primitive shape + merkle-root construction read-side semantics + per-persona-tier cryptographic shape for both primitives.

**PRD requirement(s) satisfied.** R-CP-08 (multi-agent topology — audit composition surface); R-CP-09 (sub-agent privilege inheritance — audit composition at sub-agent dispatch); R-CP-12 (audit-ledger cryptographic shape per persona tier — multi-agent extension).

**ADR commitment(s) honored.** ADR-D4 v1.1 §1.10 (cross-sibling audit-ledger discipline; F2-14 Reading 1 disposition — `parent_fanout_close_entry` as separate ledger primitive joining F2 via `action_id`); ADD §3.1.2 Synthesis.

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-05 (state-ledger entry shape — sibling tool-call entries honor F2 six-field shape); `Spec_Information_Substrate_v1.md` C-IS-06 (hash-chain integrity construction — both primitives hash-chain at team-binding+); `Spec_Information_Substrate_v1.md` C-IS-07 (read/write contract pair — append-only structured idempotent write).

**Persona linkage.** Persona §10.4 (compliance-readiness — multi-agent span hierarchy + per-sibling audit-ledger discipline).

**Specification content.**

### §15.1 Per-sibling F2 ledger entry composition

Per ADR-D4 v1.1 §1.10 + `Spec_Information_Substrate_v1.md` C-IS-05:

Per-sibling tool calls produce ledger entries keyed on the sibling's `thread_id` and honoring F2's six-field entry shape:

```
sibling_ledger_entry = (
    action_id           : ParentActionID || sibling_thread_id || step_index,
    idempotency_key     : sha256(parent_action_id, sibling_thread_id, step_index,
                                  tool, canonical_args)
                                  // per Cluster 4 §2.2.7 [HIGH] Stripe-style construction
                                  // cited at C-IS-10 §10.2
    actor               : sibling_agent_identity,
    response_hash       : sha256(canonicalize(tool_output)),
    timestamp           : ISO-8601,
    prior_event_hash    : <prior entry per C-IS-06 §6.1>
)
```

These entries are F2 substrate primitives written via the C-IS-07 §7.1 C3-pole append-only structured idempotent write contract. This contract introduces **no F2 revision** at this surface.

### §15.2 `parent_fanout_close_entry` separate-primitive shape

Per ADR-D4 v1.1 §1.10 (F2-14 Reading 1 disposition) — `parent_fanout_close_entry` is a **separate ledger primitive** joining F2 state-ledger via `action_id` reference; it is NOT an F2 state-ledger entry:

```
parent_fanout_close_entry = (
    action_id           : ParentActionID,
    fanout_topology     : Pattern per C-CP-10 §10.1 (one of six),
    sibling_ledger_root : MerkleRoot[sibling_thread_ids → sibling_ledger_entry_hashes],
    cascade_decision    : "completed" | "cascade-cancelled" | "paused-on-failure",
    timestamp           : ISO-8601,
    prior_event_hash    : SHA-256
)
```

### §15.3 Missing F2 fields rationale (F2-14 Reading 1 closure)

Per ADR-D4 v1.1 §1.10 — the missing F2 fields are intentional, not under-specification:

| F2 field absent at `parent_fanout_close_entry` | Rationale |
|---|---|
| `idempotency_key` | F2's `idempotency_key` is per-action; fanout-close is per-topology, not per-action. The fanout-close primitive sits at topology boundary, not action boundary. |
| `actor` | The fanout-close writer is structurally the orchestrator agent; the topology context already disambiguates the writer, so `actor` would be redundant. |
| `response_hash` | A fanout aggregate has no single "response"; the response IS the merkle-root over siblings, carried in the fanout-specific field `sibling_ledger_root`. |

### §15.4 Merkle-root construction read-side semantics

Per ADR-D4 v1.1 §1.10:

```
sibling_ledger_root = merkle_tree_over(
    [
        H(sibling_ledger_entry_for_thread_t1),
        H(sibling_ledger_entry_for_thread_t2),
        ...,
        H(sibling_ledger_entry_for_thread_tN)
    ]
)
```

The construction:

| Step | Operation | F2 effect |
|---|---|---|
| 1 | Read per-sibling F2 entries via `action_id` join — each sibling's F2 entries reference the parent's `ParentActionID` as their conversation/topology root through F2's `action_id` field | **Read-only** on F2 substrate |
| 2 | Hash each sibling's chain via per-entry `response_hash` per F2 entry shape | **Read-only** on F2 substrate |
| 3 | Construct merkle tree over the read set | **No F2 entries written** at merkle construction |
| 4 | Write the separate `parent_fanout_close_entry` carrying the merkle-root | Writes a **separate ledger primitive**, not an F2 entry |

The construction does **NOT write F2 entries**; it reads them. T-perm-2 F2-layer resolution stands per ADR-D4 v1.1 §1.10 (Change-note T-perm-2 impact: None).

### §15.5 Per-persona-tier cryptographic shape

Per ADR-D4 v1.1 §1.10 + composition with C-CP-20 §20.1 (D5 §1.4):

| Persona tier | Sibling ledger entries (F2 substrate) | Parent fanout-close entry (separate primitive joining F2 via `action_id`) |
|---|---|---|
| `solo-developer` | Append-only SQLite per `Spec_Information_Substrate_v1.md` C-IS-05 | Append-only SQLite with merkle-root |
| `team-binding` | Hash-chained SQLite per C-IS-06 | Hash-chained SQLite with merkle-root |
| `multi-tenant-compliance` | Hash-chained SQLite + cryptographic signature per entry per C-CP-20 §20.2 | Hash-chained SQLite + signed merkle-root + tamper-evident trace proof |

### §15.6 Audit-ledger read at trace inspection

Per R-CP-08 + R-CP-09 + R-CP-12 acceptance criteria — the downstream maintainer inspects:

| Surface | Composition |
|---|---|
| `topology.cascade_decision_audit_ledger_id` attribute on `topology.fanout.closed` span (per C-CP-14 §14.2) | Resolves to the `parent_fanout_close_entry` action_id; trace correlation enables audit verification at trace inspection time |
| Per-sibling F2 entries | Resolvable via `action_id` join from the merkle-root; hash-chain verification per C-IS-06 holds across siblings |
| Multi-tenant-compliance signature | Per C-CP-20 §20.2 `audit.signature.*` attributes attached to ledger entries; signature verification per F2-iter2-03 two-row rotation pattern at C-CP-20 §20.3 |

**Deferred to implementation discretion.** Specific merkle tree library binding; specific SQLite schema for the separate `parent_fanout_close_entry` primitive (per F2-iter2-03 dual-signature schema extension at C-CP-20 §20.3 if multi-tenant-compliance + signing-key-rotation overlap); specific `cascade_decision_audit_ledger_id` serialization; specific merkle-root inclusion-proof generation for the multi-tenant-compliance tamper-evident trace proof.

---

## §16 C-CP-16 — Four-response palette + audit ledger entry shape

**Contract surface.** Closed four-value response palette + per-response audit-ledger entry shape + palette invariance contract across cells.

**PRD requirement(s) satisfied.** R-CP-10 (HITL four-response palette at every gate).

**ADR commitment(s) honored.** ADR-D5 v1.3 §1.1 (four-response palette as harness-canonical operator-response contract per `c11-operator-local` SKILL.md primitive ownership); ADD §3.1.3 Synthesis.

**Persona linkage.** Persona §10.2 (selective HITL persona-constrained); §4 (99.9% SLO; mathematically incompatible with operator-in-loop-on-every-failure HITL); §10.4 (compliance-readiness — audit-ledger composition with HITL events).

**Specification content.**

### §16.1 Closed four-value palette

Per ADR-D5 v1.3 §1.1 — the palette is **closed** at D5; palette extension is a Workflow §4.1.2 Class-2 D5 revision.

| Response | Semantics | Cell applicability |
|---|---|---|
| `approve` | Proceed with proposed action as-is | All cells of C-CP-18 matrix |
| `edit` | Proceed with operator-modified proposed action | All cells |
| `reject` | Cancel proposed action; agent receives rejection signal | All cells |
| `respond` | Continue dialogue with the agent without action commitment | All cells |

### §16.2 Per-response audit-ledger entry shape

Per ADR-D5 v1.3 §1.1 (composition with `Spec_Information_Substrate_v1.md` C-IS-05 entry shape per C-CP-20 §20.1):

| Response | Audit-ledger entry shape |
|---|---|
| `approve` | `(action_id, gate_level, response: approve, timestamp, prior_event_hash)` |
| `edit` | `(action_id, gate_level, response: edit, edited_proposal_hash, timestamp, prior_event_hash)` |
| `reject` | `(action_id, gate_level, response: reject, rejection_reason_hash?, timestamp, prior_event_hash)` |
| `respond` | `(action_id, gate_level, response: respond, response_text_hash, timestamp, prior_event_hash)` |

The `gate_level` field carries the per-action gate level computed at C-CP-19 §19.1 multiplicative rule (ranging `{auto, ask, deny}`); `prior_event_hash` chains per `Spec_Information_Substrate_v1.md` C-IS-06 hash-chain construction at team-binding+ persona tiers.

### §16.3 Palette completeness invariance

Per R-CP-10 acceptance criterion:

| Invariant | Contract |
|---|---|
| **Palette completeness** | Every HITL invocation surface presents **all four** response options at every cell of the C-CP-18 persona-tier × engine-class matrix |
| **Synchrony class does not narrow palette** | The synchrony class per cell (sync-blocking / durable-async / both-by-tier / two-agent-observer per C-CP-18) determines **how** the palette is delivered (in-process function return vs durable signal vs webhook callback) — **not what** the operator can express |
| **Pre-HITL escalation MAY narrow palette** | At `permanent-fail-exit` invocations under cross-trust-boundary actions, the palette is restricted to `{approve, reject, respond}` per C-CP-21 §21.2 (cross-family active, local-terminal active, untrusted-MCP). At `HITL-recoverable` invocations under validator-failure, the palette is `{approve, request-changes, reject}` per C-CP-21 §21.2 |

The `respond` semantic explicitly distinguishes "continue dialogue without action" from `reject` ("cancel action") — preserves the operator's option to negotiate without committing.

### §16.4 Response-class span attribute

Per ADR-D5 v1.3 §1.1 + §1.8 + C-CP-20 §20.5: the `hitl.response.class` span attribute carries the response per `hitl.invocation.responded` event:

```
hitl.response.class ∈ {approve, edit, reject, respond}
```

This is a **cardinality-safe metric dimension** (bounded enumeration per ADR-D5 v1.3 §1.4.1) — D6 §1.2 ingests at session 4. Operator-burden eval primitive `expected_hitl_invocations_per_session` per C-CP-21 §21.4 derives from `hitl.invocation.responded` span counts per session.

**Deferred to implementation discretion.** Specific operator UI surface (in-process function-return rendering at sync-blocking cells; chat / Slack / webhook rendering at durable-async cells); specific `edited_proposal_hash` canonicalization library binding (composes with `Spec_Information_Substrate_v1.md` C-IS-06 hash-chain construction discipline); specific `response_text_hash` summarization for long `respond` text; specific UI labelling per operator locale.

---

## §17 C-CP-17 — Three-placement HITL topology primitive + interface signature

**Contract surface.** Closed three-placement enumeration + per-placement trigger + topology primitive interface signature `hitl_gate(...)` + HITL-as-tool-call rewriting contract.

**PRD requirement(s) satisfied.** R-CP-11 (three-placement HITL topology primitive at workflow definition).

**ADR commitment(s) honored.** ADR-D5 v1.3 §1.3 (three-placement HITL topology primitive); ADR-D5 v1.3 §1.3.1 (topology primitive interface signature); ADR-D5 v1.3 §1.3.2 (HITL-as-tool-call rewriting contract); ADD §3.1.3 Synthesis.

**Persona linkage.** Persona §7 (workflow-definition surface — both markdown-spec-driven and code-driven authoring); §10.2 (HITL synchrony persona-constrained).

**Specification content.**

### §17.1 Closed three-placement enumeration

Per ADR-D5 v1.3 §1.3 — the placement set is **closed** at D5; placement extension is a Workflow §4.1.2 Class-2 D5 revision.

| Placement | Trigger | Cell applicability |
|---|---|---|
| `pre-action` | Before any tool call where `_hitl_required(tool, server, persona_tier) == true` per C-CP-19 §19.1 composition | All cells of C-CP-18 matrix |
| `sub-agent-boundary` | At parent-child handoff per Cluster 4 §2.4.4 [HIGH] (HandoffContext serialization point per C-CP-13 §13.1) | All cells; sub-agent interrupt stranding mitigated via cascade-timeout per C-CP-21 §21.3 |
| `validator-escalation` | After retry-budget exhaustion (3rd validator fail per Cluster 4 §2.2.3 [HIGH]) | All cells |

#### §17.1.1 Topology primitive interface signature

Per ADR-D5 v1.3 §1.3.1:

```
hitl_gate(
    placement       : "pre-action" | "sub-agent-boundary" | "validator-escalation",
    handoff_context : HandoffContext,           // per C-CP-13 §13.1 shape
    response_palette: { approve, edit, reject, respond },   // per C-CP-16 §16.1
    timeout         : Duration,                 // None for sync-blocking;
                                                //   bounded for durable-async per C-CP-21 §21.3
    cascade_policy  : "pause" | "proceed" | "cascade-cancel"  // per C-CP-10 §10.2 +
                                                              //   C-CP-11 §11.1 per-cell default
) → HITLResult {
    response                 : "approve" | "edit" | "reject" | "respond",
    edited_proposal          : Optional<ProposedAction>,
    response_text            : Optional<String>,
    timestamp                : ISO-8601,
    audit_ledger_entry_id    : EntryID,         // per C-CP-20 §20.1 entry shape
    response_summary_hash    : SHA-256          // canonicalize over response payload
}
```

### §17.2 HITL-as-tool-call rewriting contract

Per ADR-D5 v1.3 §1.3.2: every tool exposed to the agent declares `tier ∈ {auto, ask, deny}` and `blast_radius ∈ {read-only, local-mutation, external-reversible, external-irreversible}` in its SKILL.md frontmatter or MCP server manifest (C4 contract per `c4-tools-integration` SKILL.md). The runtime evaluates `_hitl_required(tool, server, persona_tier)` per C-CP-19 §19.1 against per-MCP-server trust and persona-tier floor before dispatching the tool call. If `_hitl_required` evaluates true, the tool call is **rewritten** by the harness into one of three semantic variants:

| Variant | Tool signature | Engine binding | Cell mapping |
|---|---|---|---|
| `request_human_input(prompt, options)` | Synchronous return | sync-blocking cells | C-CP-18 §18.1 sync-blocking rows |
| `await_human_approval(action, context, channel)` | Durable signal-and-wait | durable-async cells | C-CP-18 §18.1 durable-async rows |
| `escalate_to_human(severity, summary, retry_history)` | Triggered post retry-budget exhaustion | All cells | Composes with §17.1 `validator-escalation` placement |

### §17.3 Workflow-definition surface declaration

Per R-CP-11 acceptance criterion: at workflow definition time, HITL placements are declarable at the manifest entry per C-CP-06 §6.1 `hitl_placements` field:

```
hitl_placements : List<HITLPlacement> where
  HITLPlacement {
      position       : "pre-action" | "sub-agent-boundary" | "validator-escalation",
      tool_filter    : Optional<List<ToolName>>,    // pre-action — limits which tools trigger gate
      cascade_policy : "pause" | "proceed" | "cascade-cancel"  // overrides workload-class default
                                                               //   per C-CP-11 §11.1
      timeout        : Optional<Duration>            // overrides cell synchrony-class default
  }
```

Multiple placements per workflow are admitted; the workflow inspection surface presents all declared placements (R-CP-11 acceptance criterion).

**Deferred to implementation discretion.** Specific manifest-validation library for placement-vs-cell admissibility; specific decorator vs configuration-file annotation syntax for placements (markdown-spec-driven per Persona §7 may use a different declarative shape); specific `tool_filter` glob / regex semantics; specific `escalate_to_human` severity-class enumeration.

---

## §18 C-CP-18 — Synchrony-class × HITL-primitive-shape matrix per persona-tier × D1-engine-class

**Contract surface.** 2D matrix (persona-tier × D1-engine-class → synchrony-class + HITL primitive shape) + both-by-tier overlay + two-agent-observer meta-class + per-cell exclusion inheritance.

**PRD requirement(s) satisfied.** R-CP-10 (HITL four-response palette — synchrony-class delivery mechanism half); R-CP-11 (three-placement HITL topology primitive — cell applicability half).

**ADR commitment(s) honored.** ADR-D5 v1.3 §1.2 (synchrony-class × HITL-primitive-shape matrix); ADR-D5 v1.3 §1.7 (persona-tier-binding-time selection contract); ADD §3.1.3 Synthesis.

**Persona linkage.** Persona §3.1 (four workload classes — composition with HITL per cell); §8.1 (software engineering — sync-blocking PRIMARY at solo-developer); §8.2 (content creation — natural-synchronous at design-time); §8.3 (pipeline automation — durable-async PRIMARY at team-binding); §10.2 (selective HITL persona-constrained).

**Specification content.**

### §18.1 Synchrony-class × HITL-primitive-shape 2D matrix

Per ADR-D5 v1.3 §1.2 (preserved verbatim). Cell entries: `synchrony-class | HITL primitive shape | candidate evidence`.

| persona-tier ↓ \ D1-engine-class → | event-sourced-replay | save-point-checkpoint | pure-pattern-no-engine | reconciler-loop | WAL-segment |
|---|---|---|---|---|---|
| **solo-developer** | sync-blocking PRIMARY \| in-process function with synchronous return; durable-async available via DBOS-as-library MODERATE | sync-blocking PRIMARY \| LangGraph `interrupt()` + Command resume per LangGraph HITL doc [HIGH] | sync-blocking PRIMARY \| 12-Factor Factor 7 application-defined event-and-resume [HIGH] | durable-async PRIMARY (rare at solo; if K8s local — Kind/k3s) \| `ContactChannel` CR mesh-pattern | sync-blocking PRIMARY \| segment-resume on restart with approval-pending-segment marker |
| **team-binding** | durable-async PRIMARY \| Temporal `wait_condition` + signal-handler with `timeout=days` per Temporal HITL doc [HIGH] | both-by-tier PRIMARY \| LangGraph + Postgres + Redis-lease + per-tool tier annotation; Claude Code permission model `deny → ask → allow` | **EXCLUDED** (per C-CP-07 §7.2 self-hosted-server row excludes pure-pattern for durable pole) | durable-async PRIMARY \| `ContactChannel` CR mesh-pattern with K8s-resident operator | durable-async PRIMARY \| segment-resume + external trigger via webhook ingress |
| **multi-tenant-compliance** | durable-async PRIMARY \| Temporal Cloud / AWS Bedrock AgentCore / Google Vertex Agent Engine native HITL primitives | durable-async PRIMARY \| LangGraph + DynamoDBSaver + managed checkpointer with engine-bound HITL signal | **EXCLUDED** (analogous to team-binding; pure-pattern excluded for durable pole at managed-cloud surface) | durable-async PRIMARY \| ACP K8s-managed with multi-tenant `ContactChannel` namespace isolation | durable-async PRIMARY \| managed-WAL with cryptographic-signed audit ledger |

### §18.2 Cell exclusion inheritance

Cells reading `EXCLUDED` reflect C-CP-07 §7.2 candidate-set exclusions (pure-pattern excluded from durable pole at self-hosted-server and managed-cloud deployment surfaces); this contract inherits the exclusion without revisiting C-CP-07.

### §18.3 Both-by-tier per-tool overlay

Per ADR-D5 v1.3 §1.2 — the `both-by-tier` class is a **per-tool overlay** that operates at every cell rather than a competing synchrony class:

| Property | Contract |
|---|---|
| **Scope** | At any cell, per-tool `tier ∈ {auto, ask, deny}` annotation (C4 contract per `Spec_Action_Surface_v1.md` C-AS-03) determines which actions invoke HITL gate (synchrony class per the cell) and which fire `auto` without operator engagement |
| **Composition** | The cell's synchrony class still applies when the per-tool tier is `ask`; the overlay does NOT replace the cell's primitive shape |
| **Audit composition** | `auto`-tier tool invocations emit `tool.call` spans but NOT `hitl.gate.evaluated` spans per C-CP-20 §20.5 (gate is not invoked); `ask`-tier invocations emit both spans |

### §18.4 Two-agent-observer meta-class

Per ADR-D5 v1.3 §1.2 — the `two-agent-observer` class (disler/the-verifier-agent reference) is a **meta-class composable orthogonally** at any cell where Tier-3+ blast-radius actions per `c10-action-safety` require independent verification before HITL escalation:

| Property | Contract |
|---|---|
| **Trigger** | Tier-3+ (`external-reversible` and `external-irreversible` blast-radius per C-CP-19 §19.1) actions admit pre-HITL independent verification |
| **Composition** | The verifier agent's output composes with the primary HITL gate at validator-escalation placement per §17.1; verifier agreement and disagreement both surface as inputs to the operator response palette |
| **Audit composition** | Verifier agent dispatch emits `subagent.span[verifier]` per C-CP-14 §14.1; verifier output emits `validator.fail.*` span attributes per C-CP-21 §21.5 |

### §18.5 Persona-tier-binding-time selection contract

Per ADR-D5 v1.3 §1.7:

```
At persona-tier-binding-time downstream of Phase 3:

1. Operator declares persona tier (solo-developer | team-binding | multi-tenant-compliance).
2. Operator declares deployment surface (local-development | self-hosted-server | managed-cloud)
   per C-CP-07 §7.2.
3. Cell at (persona-tier × D1-engine-class) lookup yields synchrony class + HITL primitive shape.
4. Operator selects specific candidate from §18.1 cell evidence column meeting the cell's
   synchrony class and HITL primitive shape.
5. Composition with C-CP-19 gate-level rule, C-CP-20 ledger cryptographic shape, C-CP-21
   pre-HITL escalation order, and C-CP-22 context revalidation is enforced at runtime
   regardless of candidate choice.
```

**Deferred to implementation discretion.** Specific candidate-within-class selection at persona-tier-binding-time per ADR-D5 v1.3 §1.7; specific webhook ingress library binding at durable-async cells; specific signal-handler timeout calibration per workload class; specific verifier agent prompt content (composes with `Spec_Action_Surface_v1.md` C-AS-13 §13.4 model binding per workload class).

---

## §19 C-CP-19 — T-perm-1 D5-layer multiplicative gate-level composition rule with cross-deployment monotonicity

**Contract surface.** 4-axis multiplicative composition formula + per-axis floor enumeration + cross-deployment monotonicity invariant + composition with C-AS-12 5-axis specialization at D2 layer.

**PRD requirement(s) satisfied.** R-CP-09 (sub-agent privilege inheritance — gate-level composition surface); R-CP-12 (audit-ledger cryptographic shape per persona tier — multiplicative tunable surface).

**ADR commitment(s) honored.** ADR-D5 v1.3 §1.5 (T-perm-1 D5-layer multiplicative gate-level composition rule); ADR-D5 v1.3 §1.5.1 (composition rule formula); ADR-D5 v1.3 §1.5.2 (cross-deployment monotonicity); ADD §5.2.1 T-perm-1 multi-layer resolution.

**Cross-axis citation.** `Spec_Action_Surface_v1.md` C-AS-12 (T-perm-1 D2-layer 5-axis multiplicative tunable — D2 specializes D5's 4-axis to 5-axis by adding `sandbox_tier` as the fifth axis).

**Persona linkage.** Persona §4 (selective HITL); §10.4 (compliance-readiness — multi-tenant override prohibition); §10.2 (HITL persona-constrained).

**Specification content.**

### §19.1 4-axis multiplicative composition rule

Per ADR-D5 v1.3 §1.5.1:

```
gate_level(tool, mcp_server, persona_tier) =
    max(
        per_tool_gate_level,                  // C4 contract: {auto, ask, deny}
        blast_radius_floor(tool),             // C10 four-tier taxonomy
        per_mcp_server_trust_floor(server),   // C10 five-tier framework
        persona_tier_floor                    // D5 introduces this axis
    )

where:
    blast_radius_floor:
        read-only                 → auto
        local-mutation            → ask  (configurable to auto at solo-developer)
        external-reversible       → ask
        external-irreversible     → ask  (with dual-control at multi-tenant-compliance)

    persona_tier_floor:
        solo-developer            → ask  (operator may override to auto for non-irreversible)
        team-binding              → ask  (audit ledger required; no auto override on external-*)
        multi-tenant-compliance   → ask  (audit ledger + cryptographic signature; dual-control on
                                          external-irreversible)
```

The composition is **multiplicative `max()`** per ADD §5.2.1: both axes (C4 capability via `per_tool_gate_level` and C10 gating via the three floor functions) express their concern; the higher floor always wins by construction; neither voice is suppressed. T-perm-1 closure is **structural composition**, not a choice between C4 and C10.

### §19.2 Cross-deployment monotonicity invariant

Per ADR-D5 v1.3 §1.5.2:

| Property | Contract |
|---|---|
| **Tier ascension** | When persona tier changes during bridging-arc traversal (solo-developer → team-binding → multi-tenant-compliance), `persona_tier_floor` is **monotonic ascending** |
| **Tier downgrade prohibited** | Tier downgrade is **structurally prohibited**; downgrade attempts emit a manifest-validation error at workflow-binding time and emit `sandbox.fail.class = policy_override` at runtime |
| **In-flight effective raise** | Tier upgrade is permitted at any time and **immediately raises the effective gate level** for in-flight workflows |

### §19.3 Composition with C-AS-12 D2-layer 5-axis specialization

Per `Spec_Action_Surface_v1.md` C-AS-12 §12.1 — D2 specializes this 4-axis tunable by adding `sandbox_tier` as the fifth axis:

```
gate_level_d2(tool, mcp_server, persona_tier, deployment_surface,
              blast_radius_tier, mcp_transport) =
    max(
        per_tool_gate_level,                                    # C4 contract
        blast_radius_floor(tool),                                # C10 four-tier
        per_mcp_server_trust_floor(mcp_server),                 # C10 five-tier
        persona_tier_floor,                                      # D5 §1.5
        sandbox_tier_floor(tool, deployment_surface,             # D2 NEW
                          blast_radius_tier, mcp_transport)
    )
```

D5's 4-axis rule is the Control Plane commitment; D2's 5-axis rule is the Action Surface specialization. Both compose without contradiction: the `sandbox_tier_floor` is one additional input to the same `max()` per ADD §5.2.1 multi-layer resolution.

### §19.4 `_hitl_required` runtime evaluation surface

Per ADR-D5 v1.3 §1.3.2:

```
_hitl_required(tool: ToolName, server: MCPServer, persona_tier: PersonaTier) -> bool {
    return gate_level(tool, server, persona_tier) ∈ {ask, deny}
}
```

| `gate_level` output | `_hitl_required` result | Runtime behavior |
|---|---|---|
| `auto` | `false` | Tool dispatches without HITL invocation |
| `ask` | `true` | Tool call is rewritten to one of the three HITL variants per C-CP-17 §17.2 |
| `deny` | `true` (with structural rejection) | Tool dispatch structurally rejected; emits `sandbox.fail.class = policy_override`; HITL invocation with palette restricted to `{reject, respond}` |

### §19.5 Operator-policy override surface composition

Per ADR-D5 v1.3 §1.5 + composition with `Spec_Action_Surface_v1.md` C-AS-12 §12.2:

| Persona tier | Operator-policy override of any `max()` floor |
|---|---|
| `solo-developer` | Permitted (operator IS the policy authority); each override emits audit-ledger entry per C-CP-20 §20.1 |
| `team-binding` | Permitted at non-`external-irreversible` cells; audit-ledger entry hash-chained per C-IS-06 |
| `multi-tenant-compliance` | **Structurally prohibited** per ADR-D5 v1.3 §1.5.2; override attempts emit an audit-ledger violation event per `Spec_Action_Surface_v1.md` C-AS-12 §12.3 |

**Deferred to implementation discretion.** Specific runtime evaluation engine for the 4-axis `max()` (per-call vs cached; cache invalidation on persona-tier change); specific `per_mcp_server_trust_floor` lookup table per ADR-D2 §1.10 (Action Surface territory); specific `per_tool_gate_level` parsing from SKILL.md frontmatter / MCP server manifest; specific operator-policy override authoring schema (manifest field / API call / TUI action — composes with `Spec_Action_Surface_v1.md` C-AS-12 §12.5).

---

## §20 C-CP-20 — Per-persona-tier audit-ledger cryptographic shape + `audit.*` attribute namespace

**Contract surface.** Per-persona-tier audit-ledger cryptographic shape table + signing-key resolution composing with F5 secrets bridge + signature-algorithm tunable + key-rotation two-row pattern + seven `audit.*` span attribute declarations + per-persona-tier emission discipline.

**PRD requirement(s) satisfied.** R-CP-12 (audit-ledger cryptographic shape per persona tier).

**ADR commitment(s) honored.** ADR-D5 v1.3 §1.4 (per-persona-tier ledger cryptographic shape table + signing-key resolution prose); ADR-D5 v1.3 §1.4.1 (seven `audit.*` attribute names declared at D5 source — F2-08 + F2-13 closure); ADR-D5 v1.3 §1.8 (`hitl.*` span attributes — composition with audit emission); ADD §3.1.3 Synthesis.

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-05 (state-ledger entry shape — audit-ledger entries compose against F2 six-field shape); `Spec_Information_Substrate_v1.md` C-IS-06 (hash-chain integrity construction — team-binding+ audit-ledger uses F2 hash-chain); `Spec_Information_Substrate_v1.md` C-IS-07 (read/write contract pair — audit writes follow C3-pole append-only structured idempotent write); `Spec_Action_Surface_v1.md` C-AS-05 (`fetch_secret` signature — signing-key resolution composes against F5 abstraction).

**Persona linkage.** Persona §10.4 (compliance-readiness — hash-chained audit ledger + cryptographic signature per persona tier); §11.6 + §11.7 + §11.10 (compliance + vendor / IP-handling restrictions + multi-tenant tenant-isolation at multi-tenant binding).

**Specification content.**

### §20.1 Per-persona-tier audit-ledger cryptographic shape

Per ADR-D5 v1.3 §1.4 (preserved verbatim):

| Persona tier | Audit-ledger storage shape | Cryptographic shape |
|---|---|---|
| `solo-developer` | Append-only SQLite per `Spec_Information_Substrate_v1.md` C-IS-05 | No cryptographic signature; `audit.actor.id` only |
| `team-binding` | Hash-chained SQLite per `Spec_Information_Substrate_v1.md` C-IS-06 | Hash chain via `audit.signature.prior_hash`; optional signature posture per operator opt-in |
| `multi-tenant-compliance` | Hash-chained SQLite + cryptographic signature per entry | Hash chain + signature: `audit.signature.value` produced under F5-resolved signing key per §20.2 |

### §20.2 Signing-key resolution composing with F5 secrets bridge

Per ADR-D5 v1.3 §1.4 (F2-13 closure) + `Spec_Action_Surface_v1.md` C-AS-05:

```
signing_key_ref = fetch_secret(
    name  = "harness.<deployment_id>.audit_signing_key.v<key_period>",
    scope = SecretScope.audit_signing
) -> SecretRef
```

| Property | Contract |
|---|---|
| **Signing-key residence per persona tier** | Solo-developer: not used; team-binding: F5 dev-tech OS keychain per `Spec_Action_Surface_v1.md` C-AS-05 §5.2 tier-1/tier-2 resolution; multi-tenant-compliance: F5 prod-tech vault per C-AS-05 §5.2 tier-3/tier-4 resolution (in-sandbox HTTP client over network using sandbox-identity bootstrap token) |
| **Signing-key scope** | Operator-tunable at multi-tenant-binding-time: `audit_signing_key_scope ∈ {deployment, tenant}` per Persona §11.10 (the v1 commitment is the tunable axis, not a default-binding pick) |
| **Signature algorithm** | Operator-tunable at deployment-binding-time: `audit_signature_algorithm ∈ {ed25519, ecdsa-p256, rsa-pss-2048}`. **Default: `ed25519`** |
| **Cross-deployment transition** | Mandatory-HITL trigger per `c11-operator-local` SKILL.md §4.11; chain preserved with verifier reading `audit.signature.key_period` to apply correct verification key |

### §20.3 Key-rotation two-row pattern (F2-iter2-03 Option (a) closure)

Per ADR-D5 v1.3 §1.4 (v1.3 closure):

| Property | Contract |
|---|---|
| **Key-period model** | Each ledger entry carries `audit.signature.key_period` per §20.5; chain continuous across rotations |
| **Non-audit-key rotation** | Single-signed under current key for all secret rotations OTHER than the audit-signing key itself |
| **Audit-signing-key rotation** | The `secret_rotation_event` entry is **counter-signed under outgoing + incoming keys** when the rotated secret IS the audit-signing key; rendered as TWO ledger entries (sibling-1 + sibling-2) sharing a `rotation_correlation_id` column |
| **SQLite schema extension** | Audit-ledger SQLite schema extended with `rotation_correlation_id` column (UUID) joining the two rotation-pair entries that together carry the dual signature |

#### §20.3.1 Two-row rotation verification semantics

Per ADR-D5 v1.3 §1.4 v1.3 external-auditor verification semantics:

```
verify_chain(entries: List<AuditEntry>) -> VerificationResult:
  1. Walk entries in entry_hash chain order.
  2. For each entry, recompute hashes per C-IS-06 §6.1 and verify
     audit.signature.value against the key valid at
     entry.audit.signature.key_period.
  3. On encountering non-NULL rotation_correlation_id, query for the
     sibling entry sharing the same correlation UUID.
  4. Verify the pair JOINTLY:
       - sibling-1: audit.signature.key_period = N
                    verified under outgoing key valid at period N
       - sibling-2: audit.signature.key_period = N+1
                    verified under incoming key valid at period N+1
  5. Chain hash continuity: sibling-2.audit.signature.prior_hash extends
     the chain from sibling-1.audit.signature.prior_hash (no chain break;
     sibling-2 is the rotation-anchor entry under the new key-period).
  6. Verification failure of either sibling under its appropriate key
     indicates either key compromise OR ledger tampering at the rotation
     boundary; both fail the audit.
```

Recovery from such a failure routes through `c11-operator-local` SKILL.md §4.1.28 audit-failure escalation. Non-rotation entries (`rotation_correlation_id IS NULL`) are verified one-at-a-time under their declared `audit.signature.key_period`.

### §20.4 Seven `audit.*` span attribute declarations

Per ADR-D5 v1.3 §1.4.1 — three v1.1 attributes + four v1.2 attributes:

| Attribute | Type | Cardinality | Always-emitted at | Discriminator role |
|---|---|---|---|---|
| `audit.signature.sha256` | hex-encoded 64-character string | per-entry | Multi-tenant-compliance (§20.1 row 3); structurally absent at solo-developer; opt-in at team-binding | Per-event SHA-256 hash over ledger entry payload (the hash that is **signed** by `audit.signature.value`) |
| `audit.signature.prior_hash` | hex-encoded 64-character string | per-entry | Team-binding (§20.1 row 2) and multi-tenant-compliance (row 3); structurally absent at solo-developer | Hash-chain link to prior event per C-IS-06; joins F2 entry's `prior_event_hash` field |
| `audit.actor.id` | opaque string under each persona tier's actor-identity discipline | bounded (registry) | All three persona tiers | Actor identity for the ledger entry; cardinality bounded by actor-identity registry (operator + named agents + system) |
| `audit.signature.value` | binary (64 bytes for ed25519/ecdsa-p256; 256 bytes for rsa-pss-2048) | per-entry | Team-binding (opt-in) + multi-tenant-compliance (always) | Per-entry cryptographic signature over `audit.signature.sha256` |
| `audit.signature.algorithm` | enum string ∈ `{ed25519, ecdsa-p256, rsa-pss-2048}` | low (deployment-bound) | When `audit.signature.value` emitted | Signature algorithm carried per entry |
| `audit.signature.key_id` | opaque string (typical: `harness.<deployment_id>.audit_signing_key.v<N>`) | low-medium | When `audit.signature.value` emitted | Signing-key identifier in F5 secrets backend |
| `audit.signature.key_period` | integer (non-negative, monotonic per deployment) | low | When `audit.signature.value` emitted | Monotonic period integer incremented on each signing-key rotation |

### §20.5 Per-persona-tier emission discipline

Per ADR-D5 v1.3 §1.4.1:

| Persona tier | Attributes emitted |
|---|---|
| `solo-developer` | `audit.actor.id` only |
| `team-binding` | `audit.actor.id` + `audit.signature.prior_hash` (and optionally `audit.signature.sha256` + `audit.signature.value` + `audit.signature.algorithm` + `audit.signature.key_id` + `audit.signature.key_period` if team-binding deployment opts into signature posture) |
| `multi-tenant-compliance` | All seven attributes |

Per `c7-observability` SKILL.md sampling discipline + ADR-D5 v1.3 §1.4.1: spans carrying `audit.signature.*` attributes are **always-sampled (head=1.0)** regardless of base sampling rate per cryptographic-anchor tamper-evidence relevance.

### §20.6 HITL-event span schema (composition with §20.4)

Per ADR-D5 v1.3 §1.8 (v1.3 — F2-iter2-02 Reading 1 canonical pass-through closure):

| Span name | Span attributes (structure-not-content per `c7-observability` SKILL.md) |
|---|---|
| `hitl.gate.evaluated` | `hitl.gate.level` (cardinality-safe metric dimension), `hitl.gate.persona_tier`, `hitl.gate.required: bool` (tool / mcp_server identities read from canonical parent-span attributes `gen_ai.tool.name` per OTel GenAI semconv 1.41.0 / `mcp.server.name` per `Spec_Action_Surface_v1.md` C-AS-14 §14.3 via trace correlation) |
| `hitl.invocation.opened` | `hitl.gate.level` (cross-event reference), `hitl.invocation.placement` ∈ `{pre-action, sub-agent-boundary, validator-escalation}`, `hitl.invocation.handoff_context_size_bytes`, `hitl.invocation.audit_ledger_entry_id` |
| `hitl.invocation.responded` | `hitl.response.class` per C-CP-16 §16.4 ∈ `{approve, edit, reject, respond}`, `hitl.response.latency_ms`, `hitl.response.summary_hash` |
| `hitl.invocation.timed_out` | `hitl.timeout.duration_ms`, `hitl.timeout.degradation_mode_applied` ∈ `{fail-closed, escalate-secondary-channel, fail-open}` |

HITL spans are **always-sampled (head=1.0, tail-keep-on-classification=true)** regardless of base sampling rate per `c7-observability` SKILL.md sampling discipline; HITL events are tamper-evidence-relevant under Persona §10.4 compliance posture.

**Deferred to implementation discretion.** Specific F5 secrets backend candidate per deployment surface (composes with `Spec_Action_Surface_v1.md` C-AS-05 §5.2 deferrals — `python-keyring` / `keytar` / vault / etc.); specific signature library binding (ed25519 / ecdsa-p256 / rsa-pss-2048 implementation library per language ecosystem); specific `audit_signing_key_scope` storage mechanism per tenant at multi-tenant-compliance; specific SQLite schema migration for the `rotation_correlation_id` column at deployment-binding time; specific operator-readable verifier UI for chain-verification output.

---

## §21 C-CP-21 — Pre-HITL escalation order + `validator.fail.*` taxonomy

**Contract surface.** Discriminated five-class fail taxonomy + per-class escalation path + transient-staircase code + palette-restriction rule at cross-trust-boundary actions + per-persona-tier summarization-model table + three `validator.fail.*` attribute declarations.

**PRD requirement(s) satisfied.** R-CP-10 (HITL four-response palette — palette-restriction rule half); R-CP-11 (three-placement HITL topology primitive — validator-escalation invocation half).

**ADR commitment(s) honored.** ADR-D5 v1.3 §1.10 (pre-HITL escalation order composition with model routing + discriminated five-class fail taxonomy per F2-15 closure); ADR-D5 v1.3 §1.10.1 (three `validator.fail.*` attribute declarations); ADR-D5 v1.3 §1.6 (composition with reliability primitives — timeout-degradation mode); ADR-D5 v1.3 §1.9 (composition with eval methodology — operator-burden eval primitive); ADD §3.1.3 Synthesis.

**Cross-axis citation.** `Spec_Action_Surface_v1.md` C-AS-04 (sandbox fail-class taxonomy — D2 precedent for permanent-fail-skip-staircase); `Spec_Action_Surface_v1.md` C-AS-13 §13.4 (per-sub-agent-role × model-binding — model-tier escalation candidates at 2nd-fail).

**Persona linkage.** Persona §4 (selective HITL); §6 (per-class cost ceiling — summarization-model tier per persona tier); §10.4 (compliance-readiness — escalation audit composition).

**Specification content.**

### §21.1 Discriminated five-class fail taxonomy

Per ADR-D5 v1.3 §1.10 (locked five-class retry-exit taxonomy per `c5-validation-contract` SKILL.md s14 §7.5(d) reconciliation):

| `validator.fail.class` | Routing | Recovery path |
|---|---|---|
| `transient-retry` | Transient staircase (§21.2) | C9 backoff + retry (full-jitter per Cluster 4 §2.2.7 [HIGH]); cause-attribution-conditioned policy per `c9-reliability-recovery` SKILL.md §4.1.1 |
| `Reflexion-recoverable` | Transient staircase (§21.2) | C5 reflect-step verbal feedback + C1 retry-loop (per `c5-validation-contract` SKILL.md Reflexion contract); C2 stitches feedback into next iteration's prompt |
| `HITL-recoverable` | C11 HITL primitive (validator-HITL placement per §17.1 `validator-escalation`); palette `{approve, request-changes, reject}`; `request-changes` routes back as `Reflexion-recoverable` | HITL invocation |
| `permanent-fail-exit` | **SKIP STAIRCASE**; route directly to C11 HITL (validator-escalation placement per §17.1); palette `{approve, edit, reject, respond}` per C-CP-16 §16.1; palette **restricted to `{approve, reject, respond}`** when composing with cross-trust-boundary actions (cross-family active, local-terminal active, untrusted-MCP) | Direct HITL |
| `terminal-fail-exit` | **SKIP STAIRCASE**; workflow halts; HITL escalation per `c11-operator-local` SKILL.md with no recovery path | Halt + HITL notification |

### §21.2 Transient staircase code (transient-retry + Reflexion-recoverable)

Per ADR-D5 v1.3 §1.10 (the v1 staircase, transient-only per Cluster 4 §2.2.3 [HIGH]):

```
When validator.fail.class ∈ {transient-retry, Reflexion-recoverable}:

  1st validator fail   → retry with backoff (C9 mechanism)
                          # emits retry.attempt span per C-CP-03 §3.5 base-rate sampled
  2nd validator fail   → cause-attribution-conditioned branch:
                          - cause ∈ {model_misfire, provider_outage,
                                     capability_shortfall_transient}
                            → escalate model tier per ADR-F1 chain composition
                              (subscribes to C9 trigger on_capability_shortfall or
                               on_per_model_breaker_trip);
                              candidates per `Spec_Action_Surface_v1.md` C-AS-13 §13.4
                              model-tier escalation chain: Haiku → Sonnet → Opus 4.6 → Opus 4.7
                          - cause ∈ {semantic_disagreement,
                                     contract_violation_not_yet_routed_to_Reflexion}
                            → re-prompt with different system prompt
                          # 2nd-fail retry.attempt span ALWAYS-SAMPLED per C-CP-03 §3.5
  3rd validator fail   → C5 emits permanent-fail-exit → routes to validator-escalation
                          HITL placement per §17.1 (skip-staircase branch above)
```

### §21.3 Palette-restriction rule at cross-trust-boundary actions

Per ADR-D5 v1.3 §1.10 + s14 §7.10(d): the palette is **restricted to `{approve, reject, respond}`** (no `edit`) when validator-escalation HITL composes with:

| Composition surface | Palette restriction trigger |
|---|---|
| Cross-family active | Current `{provider, model}` is in cross-family fallback state per C-CP-04 §4.3 — `fallback.cross_family_triggered` event emitted within current workflow boundary |
| Local-terminal active | Workflow has fallen through to the local/open-weight tier per C-CP-04 §4.1 chain floor |
| Untrusted-MCP active | Current tool dispatches against an MCP server with `per_mcp_server_trust_floor` ≥ `untrusted-floor` per C10 five-tier framework (Action Surface territory; `Spec_Action_Surface_v1.md` C-AS-10 §10.1) |

The restriction is **structural**: the rationale is that under cross-trust-boundary state, operator `edit` of the proposed action would re-introduce an action that cannot be safely dispatched without re-evaluation; `reject` (cancel) or `respond` (negotiate) are the safe options.

### §21.4 Per-persona-tier summarization-model table

Per ADR-D5 v1.3 §1.10 — HandoffContext summarization role is per-persona-tier model-bound:

| Persona tier | Summarization model | Rationale |
|---|---|---|
| `solo-developer` | Haiku 4.5 | Low-latency, low-cost; operator review-in-loop tolerates lower fidelity per Persona §6 |
| `team-binding` | Sonnet 4.6 | Balanced fidelity/cost |
| `multi-tenant-compliance` | Sonnet 4.6 with extended-thinking budget OR Opus 4.6 | Compliance-bound summaries require higher fidelity per Persona §10.4 |

The summarization model binding is **separate** from the lead-agent binding per C-CP-13 §13.3 (which inherits per workload class per `Spec_Action_Surface_v1.md` C-AS-13 §13.4).

### §21.5 Three `validator.fail.*` attribute declarations

Per ADR-D5 v1.3 §1.10.1:

| Attribute | Type | Cardinality | Always-emitted on | Ownership |
|---|---|---|---|---|
| `validator.fail.class` | enum string ∈ `{transient-retry, Reflexion-recoverable, HITL-recoverable, permanent-fail-exit, terminal-fail-exit}` | bounded (5) | Every validator-failure event | Emitted by C5 at fail-classification time |
| `validator.fail.cause_attribution` | enum string from open set (`network_timeout`, `provider_outage`, `model_misfire`, `contract_violation`, `schema_violation`, `semantic_disagreement`, `policy_denial`, `human_rejection`, `time_budget_exhaust`, `capability_shortfall`) plus F5-introduced refinements (`secret_unknown`, `secret_unavailable`, `secret_expired`, `secret_locked`, `secret_revoked` per `Spec_Action_Surface_v1.md` C-AS-05 §5.2 forward-reference) | medium (open set) | Every validator-failure event per s12 §7.5(a) standing pre-check | Emitted by C5 at fail-classification time |
| `validator.fail.permanence` | enum string ∈ `{transient, permanent}` — derived from `validator.fail.class` (`permanent` if class ∈ `{permanent-fail-exit, terminal-fail-exit}`; `transient` otherwise) | bounded (2) | Every validator-failure event | C7-instrumentable boolean discriminator for cross-attribute filtering and dashboard binding |

### §21.6 Sampling discipline for validator-failure spans

Per ADR-D5 v1.3 §1.10.1 + `c7-observability` SKILL.md head-based-dev / tail-based-prod default:

| Span attribute condition | Sampling rate |
|---|---|
| `validator.fail.permanence = permanent` | **Always-sampled (head=1.0, tail-keep-on-classification=true)** — tamper-evidence and operator-burden traceability relevance |
| `validator.fail.permanence = transient` | Base-rate sampling per cell (the per-attempt staircase emits `retry.attempt` spans per C-CP-03 §3.5; 2nd-fail onward always-sampled) |

### §21.7 Operator-burden eval primitive composition

Per ADR-D5 v1.3 §1.9:

| Persona tier | Target `expected_hitl_invocations_per_session` | Failure modes |
|---|---|---|
| `solo-developer` | 5–20 | < 2 → over-automated; > 40 → fatigue |
| `team-binding` | 1–5 | < 1 → over-automated; > 10 → fatigue |
| `multi-tenant-compliance` | 0.5–3 | < 0.5 → audit gap risk; > 5 → fatigue |

The primitive is computed from `hitl.invocation.responded` span counts per session (D6 §1.6 dashboard ingestion at session 4). Tool-tier annotation calibration eval (Husain manual-review → categorize → automate → align loop per `c8-eval-engineer` SKILL.md): `ask`-tier tools producing >95% approve responses across a holdout indicate mis-calibration toward `auto`; `auto`-tier tools producing operator overrides via post-action audit-ledger flagging indicate mis-calibration toward `ask`.

### §21.8 Timeout-degradation mode at durable-async cells

Per ADR-D5 v1.3 §1.6 + Cluster 4 §2.4 [HIGH] Temporal `wait_condition timeout=days` + Cluster 4 §2.4.5 [HIGH] webhook lost-update mitigation:

| Persona tier | Timeout-degradation mode | Rationale |
|---|---|---|
| `solo-developer` | `fail-closed` | Operator is the developer; no secondary channel |
| `team-binding` | `escalate-secondary-channel` (default); `fail-closed` (configurable) | On-call rotation typical; operator-tunable per workload |
| `multi-tenant-compliance` | `fail-closed` + alerting | Persona §10.4 compliance posture incompatible with `fail-open`; tamper-evident audit requires explicit operator action |

Webhook ingress for durable-async cells MUST use **idempotency-keyed signal delivery** composed against F2 state-ledger entry shape per `Spec_Information_Substrate_v1.md` C-IS-05: `(approval_id, idempotency_key)` checked against the ledger before signal application per Cluster 4 §2.4.5 [HIGH].

**Deferred to implementation discretion.** Specific cause-attribution enum extension procedure under Workflow §4.1.2 Class-2 D5 revision; specific Husain calibration eval holdout authoring (composes with session 4 C-OD-* operator-burden eval primitive); specific `expected_hitl_invocations_per_session` dashboard rendering (session 4 territory); specific secondary-channel mechanism at team-binding `escalate-secondary-channel` mode; specific webhook idempotency-key extraction from inbound signal payload.

---

## §22 C-CP-22 — Context revalidation on HITL resume

**Contract surface.** Resume protocol + per-external-reference snapshot capture + material-diff detection contract + composition with HandoffContext state_summary + T-perm-2 F2-layer composition.

**PRD requirement(s) satisfied.** R-CP-10 (HITL four-response palette — resume composition); R-CP-11 (three-placement HITL topology primitive — durable-async cell resume).

**ADR commitment(s) honored.** ADR-D5 v1.3 §1.11 (context revalidation on HITL resume); ADD §3.1.3 Synthesis.

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-07 (read/write contract pair — context-reconstruction read per C3-pole); `Spec_Information_Substrate_v1.md` C-IS-05 (state-ledger entry shape — state_summary external-reference snapshot composition).

**Persona linkage.** Persona §4 (99.9% SLO; durable-async cells with long pause durations); §10.2 (HITL persona-constrained).

**Specification content.**

### §22.1 Resume protocol

Per ADR-D5 v1.3 §1.11 — for durable-async cells, long pause durations (e.g., 5-day Temporal `wait_condition timeout`) introduce context-rot risk:

```
on_hitl_resume(handoff_context: HandoffContext, operator_response: HITLResult):
    1. Reconstruct active context from durable state per
       `Spec_Information_Substrate_v1.md` C-IS-07 §7.2 read contract
       (C3-pole reconstruction)
    2. Revalidate: for each external reference in handoff_context.state_summary
       per C-CP-13 §13.4 StateSummary.relevant_entries,
       refetch and diff against captured snapshot:
           current_value = refetch(external_reference)
           prior_snapshot = state_summary.snapshot_at_pause_time(external_reference)
           if material_diff(current_value, prior_snapshot):
               material_diff_detected = true
               diff_set.add((external_reference, prior_snapshot, current_value))
    3. If material_diff_detected → re-emit HITL with updated context
       (per Cluster 4 §2.4.6 / §2.4.7 [HIGH] approval-fatigue mitigation:
        only re-emit on material diff, not on every irrelevant change):
           new_handoff_context = handoff_context.with_diff(diff_set)
           hitl_gate(placement=current_placement,
                     handoff_context=new_handoff_context,
                     response_palette={approve, edit, reject, respond},
                     ...)
       # AUDIT: re-emit produces a NEW hitl.invocation.opened span per C-CP-20 §20.5,
       # plus an audit-ledger entry per C-CP-20 §20.1 recording the re-emit cause
    4. Else → apply operator response per C-CP-16 §16.1 four-response palette
       (approve / edit / reject / respond)
```

### §22.2 Material-diff detection contract

Per ADR-D5 v1.3 §1.11 — `material_diff` is the predicate that distinguishes diff-worth-re-emitting from irrelevant change:

| Reference class | Material-diff predicate |
|---|---|
| F2 state-ledger entries (per C-IS-05) | Material if `response_hash` changed AND the changed entry is within the sub-agent's scope per HandoffContext.state_summary.relevant_entries |
| External MCP-resource snapshots (per `Spec_Action_Surface_v1.md` C-AS-10) | Material per per-resource semantic predicate declared at the MCP server manifest (default: any value change is material; explicit `material_diff_predicate` declaration overrides) |
| Filesystem state per `Spec_Information_Substrate_v1.md` C-IS-01 | Material if file content `sha256` changed AND the changed file is within the workflow's worktree scope per C-IS-09 |
| Lead agent's failed_attempts / alternatives_considered history | Material if a new failed attempt or alternative was recorded by another sub-agent in the same workflow during the pause |

### §22.3 State_summary snapshot capture at pause-time

Per ADR-D5 v1.3 §1.11 + C-CP-13 §13.4 composition:

```
on_hitl_pause(handoff_context: HandoffContext):
    1. For each external_reference in handoff_context.state_summary.relevant_entries:
           snapshot_capture(external_reference) -> snapshot_value
           handoff_context.state_summary.snapshot_at_pause_time(
               external_reference, snapshot_value
           )
    2. Compute handoff_context.state_summary.summary_hash per C-CP-13 §13.4
       (canonicalize+sha256 over state_summary including snapshots)
    3. Persist HandoffContext to durable state per
       `Spec_Information_Substrate_v1.md` C-IS-07 §7.1 write contract
       (C3-pole append-only structured idempotent write)
    4. Emit hitl.invocation.opened span per C-CP-20 §20.5 with
       hitl.invocation.handoff_context_size_bytes attribute
```

### §22.4 T-perm-2 composition (F2-layer resolution stands)

Per ADR-D5 v1.3 §1.11 — T-perm-2 (C2 ↔ C3 — within-vs-across-turn) F2-layer resolution stands; context revalidation composes against the existing F2 read/write contract pair (`Spec_Information_Substrate_v1.md` C-IS-07) without D5-layer revision. The within-turn (C2) snapshot capture at pause-time and across-turn (C3) re-read at resume-time both cross the seam through the F2 read/write contract.

**Deferred to implementation discretion.** Specific `snapshot_capture` library binding per external-reference class; specific `material_diff_predicate` declarative authoring at MCP server manifest (composes with `Spec_Action_Surface_v1.md` C-AS-10 §10.3); specific diff-set serialization at re-emit; specific approval-fatigue threshold tuning per cell of C-CP-18 matrix; specific snapshot-storage TTL at very-long-pause cases.

---

## §23 C-CP-23 — T-perm-3 multi-layer resolution composition

**Contract surface.** Three-layer composition shape (F1 + D1 + D4) + per-layer tunable axes + per-cell concrete fault-handling binding + ADD §5.2.3 multi-layer-resolution citation surface.

**PRD requirement(s) satisfied.** R-CP-02 (cross-family fallback announced before error path — F1-layer resolution); R-CP-06 (engine class committed per deployment surface — D1-layer resolution); R-CP-08 (multi-agent topology selectable — D4-layer resolution).

**ADR commitment(s) honored.** ADR-F1 v1.2 §"Permanent tensions engaged" (T-perm-3 F1-layer resolution: per-layer time-budget shape); ADR-D1 v1.1 §1.3 (D1-layer resolution: `topology_fault_handling ∈ {ABOVE_ENGINE, BELOW_ENGINE, RECONCILER}` per deployment surface); ADR-D4 v1.1 §1.6 (D4-layer resolution: `topology_fault_handling × workload_class × topology_pattern` multiplicative specialization); ADD §5.2.3 T-perm-3 multi-layer resolution.

**Persona linkage.** Persona §4 (99.9% SLO — chain-advancement reliability composition); §8.3 (pipeline automation — `BELOW_ENGINE` reading at event-sourced-replay); §3.2 (workload-class extensibility — `ABOVE_ENGINE` reading at save-point + pure-pattern).

**Specification content.**

### §23.1 Three-layer composition shape

Per ADD §5.2.3:

```
F1-layer resolution         per-layer time-budget shape per C-CP-03 §3.1
                            (declarative manifest / embedding / LLM-as-router
                             each with own timeout_ms bound; deterministic
                             fall-through on exceedance per C-CP-03 §3.2)
       +
D1-layer resolution         topology_fault_handling per deployment surface
                            per C-CP-07 §7.2 candidate mapping
                            ∈ {ABOVE_ENGINE, BELOW_ENGINE, RECONCILER}
       +
D4-layer resolution         topology_fault_handling × workload_class × topology_pattern
                            per C-CP-11 §11.4 multiplicative tunable
       =
Concrete fault-handling     resolved at deployment-surface-time × workload-binding-time;
binding                     per-cell cascade-enforcement mechanism per C-CP-11 §11.2
```

### §23.2 Per-cell reading discipline

Per ADR-D4 v1.1 §1.4 + ADR-D1 v1.1 §1.3 + ADD §5.2.3:

| Reading | Cell condition | Cell expression |
|---|---|---|
| `ABOVE_ENGINE` | Save-point-checkpoint OR pure-pattern-no-engine OR WAL-segment engine class | Harness owns topology and durability composition; engine exposes save-points or per-segment substrate; harness composes lease + dedup + resumption above |
| `BELOW_ENGINE` | Event-sourced-replay engine class | Engine owns lifecycle; harness becomes topology-author; engine-native cascade-enforcement + writer-serialization (per C-CP-11 §11.2 row 1) |
| `RECONCILER` | Reconciler-loop engine class (K8s CRD-resident) | Control-loop owns reconvergence; CRD reconciliation drives cascade and writer-serialization (per C-CP-11 §11.2 row 4) |

The tension is **structural to the slate** per ADD §5.2.3 and is not collapsed at any layer. Each reading earns its keep at the cells where it dominates.

### §23.3 Compositional fault-handling resolution at runtime

Per ADD §5.2.3:

```
At workload-binding-time:

1. Operator declares workload class + deployment surface + persona tier
2. C-CP-07 §7.2 yields engine-class candidate set per deployment surface
3. Operator selects specific engine class within candidate set
4. C-CP-11 §11.3 2D matrix lookup at (workload-class × engine-class) yields:
       - topology_pattern (per C-CP-11 §11.1)
       - cascade-enforcement mechanism (per C-CP-11 §11.2)
       - T-perm-3 reading (per §23.2)
5. C-CP-03 §3.1 per-layer time-budget bounds set per workload-class × persona-tier
   tuning (the F1-layer resolution shape)
6. Concrete fault-handling binding is the composition of (4) and (5):
       - F1 layer: per-layer time-budget cascades through routing layers per C-CP-03 §3.2
       - D1 layer: topology_fault_handling reading per cell determines whose lifecycle owns
                   cascade
       - D4 layer: topology_pattern + cascade_policy default + writer-serialization stance
                   per C-CP-11 §11.1 determines fan-out behavior
```

### §23.4 Cross-axis composition with C-AS-12 (T-perm-1) + ADD §5.3.3 (deterministic outer-harness)

Per ADD §5.3.3:

| Property | Contract |
|---|---|
| **T-perm-1 + T-perm-3 orthogonal composition** | C-CP-19 4-axis gate-level (T-perm-1 D5-layer) operates orthogonally to C-CP-23 (T-perm-3) — gate-level is **per-action** (which calls invoke HITL); fault-handling is **per-failure** (what happens when a call fails) |
| **Deterministic outer-harness composition** | All chain-advancement (C-CP-04), cascade-enforcement (C-CP-11 §11.2), retry mechanics (C-CP-03 §3.5 `retry.*`), breaker mechanics (C-CP-03 §3.5 `harness.breaker.*`), and HITL escalation (C-CP-21) are deterministic outer-harness primitives per ADD §5.3.3 — the LLM call is the probabilistic core; everything around it is deterministic |

**Deferred to implementation discretion.** Specific per-cell cascade timeout calibration (composes with C-CP-03 §3.1 LayerBudget tuning); specific operator-tunable per-layer time-budget UI surface (composes with C-CP-06 §6.1 manifest authoring); specific cascade-cancellation propagation protocol per engine vendor (Temporal child-workflow cancellation API at event-sourced-replay; LangGraph node cancellation at save-point-checkpoint).

---

## §24 C-CP-24 — Control Plane substrate seam exports surface

**Contract surface.** Cross-axis exports from this spec for session 4 (Operational Discipline) and session 5 (cross-axis composition document) to consume by citation.

**PRD requirement(s) satisfied.** All twelve R-CP-* (cross-axis composition surface; this contract is the analog of C-IS-10 and C-AS-16 for the Control Plane axis).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.2 (unified span schema) ingests CP namespace exports across three structurally distinct composition paths:

1. **Specialization-layer ingestion at D6 §1.2 — six namespaces.** `engine.*` (D6 §1.2 row 9; CP source: C-CP-09 §9.1; ADR anchor: ADR-D1 v1.1 §1.1.1), `topology.*` (D6 §1.2 row 7 named `topology.fanout.*` per Reading-1 sub-tree interpretation accepted under OD-iter2-RP-2.A; CP source: C-CP-14 §14.2; ADR anchor: ADR-D4 v1.1 §1.9), `subagent.*` (D6 §1.2 row 8; CP source: C-CP-14 §14.2; ADR anchor: ADR-D4 v1.1 §1.9), `hitl.*` (D6 §1.2 row 6; CP source: C-CP-20 §20.6; ADR anchor: ADR-D5 v1.3 §1.8), `audit.*` (D6 §1.2 row 10; CP source: C-CP-20 §20.4; ADR anchor: ADR-D5 v1.3 §1.4.1), `validator.fail.*` (D6 §1.2 row 11; CP source: C-CP-21 §21.5; ADR anchor: ADR-D5 v1.3 §1.10.1).

2. **F3 capability-floor (iv) lifecycle event mapping at D6 §1.2 lines 124–133 — four namespaces.** `fallback.*` (as `fallback.triggered` span event), `retry.*` (as `retry.attempt` span event), `lease.*` (as `lease.acquired` / `lease.released` span events), `harness.breaker.*` (as `breaker.tripped` span event with seven-attribute schema declared at D6 §1.2.1; substrate-anchored at `c9-reliability-recovery` SKILL.md per F2-16 closure and Workflow v1.3 §2.3.3.1 clause (iii) substrate-anchored citation discipline — CP consumes the namespace at C-CP-03 §3.5 deployment-side composition but does NOT own its canonical declaration). ADR anchors: ADR-F3 v1.1 capability-floor (iv); per-namespace CP-side composition citations at C-CP-03 §3.5 (`fallback.*`, `retry.*`, `harness.breaker.*`) and C-CP-05 §5.3 (`lease.*`).

3. **Inheritance-composition (not ingested at D6 §1.2) — one namespace.** `routing.*` (4 attributes declared at C-CP-01 §1.4; ADR anchor: ADR-F1 v1.2 §Decision) inherits sampling from parent `llm.inference` span per OTel GenAI semconv 1.41.0; it appears neither in D6 §1.2 specialization-layer namespace map nor in the F3 lifecycle event set.

Eleven namespaces total: 6 specialization-layer + 4 F3-lifecycle-event-attribute + 1 inheritance-composition (per F-OD-01.B operator selection preserved under three-composition-path framing).

**Persona linkage.** Persona §10.2 (cost-attribution-per-span); §10.4 (compliance-readiness — cross-axis tamper-evidence composition).

**Specification content.**

### §24.1 Span attribute namespace exports

Eleven namespaces are declared at Control Plane source contracts and exported to session 4 (D6 unified span schema) across three structurally distinct composition paths. The total decomposes as **6 + 4 + 1 = 11**: six specialization-layer namespaces ingested at D6 §1.2; four F3-capability-floor (iv) lifecycle-event-attribute namespaces ingested at D6 §1.2 lines 124–133 (event sub-tree, not specialization rows); one inheritance-composition namespace inheriting sampling from the parent `llm.inference` span per OTel GenAI semconv 1.41.0 (not ingested at D6 §1.2 at all).

#### §24.1.A Specialization-layer namespace exports (six namespaces; D6 §1.2 direct ingest)

| Namespace | Source contract | Attribute count | Always-sampled discipline | D6 §1.2 ingest row |
|---|---|---|---|---|
| `engine.*` | C-CP-09 §9.1 | 3 (`engine.class`, `engine.event_history.tier`, `engine.event.id`) | Per parent span sampling discipline; `workflow.resumption` always-sampled per C-CP-05 §5.4 | D6 §1.2 row 9 (ADR-D1 v1.1 §1.1.1) |
| `topology.*` | C-CP-14 §14.2 | 10 attributes | `topology.fanout.opened` / `topology.fanout.closed` always-sampled per C-CP-14 §14.3 | D6 §1.2 row 7 (named `topology.fanout.*` per Reading-1 sub-tree interpretation accepted under OD-iter2-RP-2.A; ADR-D4 v1.1 §1.9) |
| `subagent.*` | C-CP-14 §14.2 | 7 attributes | `subagent.span` base-rate with tail-keep-on-failed; `subagent.span.closed` always-sampled per C-CP-14 §14.3 | D6 §1.2 row 8 (ADR-D4 v1.1 §1.9) |
| `hitl.*` | C-CP-20 §20.6 | per-event attributes across 4 span names | All HITL spans always-sampled per `c7-observability` SKILL.md | D6 §1.2 row 6 (ADR-D5 v1.3 §1.8) |
| `audit.*` | C-CP-20 §20.4 | 7 attributes per persona-tier emission discipline | Always-sampled when `audit.signature.*` attributes present per C-CP-20 §20.5 | D6 §1.2 row 10 (ADR-D5 v1.3 §1.4.1) |
| `validator.fail.*` | C-CP-21 §21.5 | 3 attributes | Always-sampled when `validator.fail.permanence = permanent` per C-CP-21 §21.6 | D6 §1.2 row 11 (ADR-D5 v1.3 §1.10.1) |

#### §24.1.B F3-capability-floor lifecycle-event-attribute exports (four namespaces; D6 §1.2 lines 124–133 lifecycle event sub-tree, not specialization rows)

| Namespace | Source contract | Attribute count | Always-sampled discipline | D6 lifecycle event mapping | Canonical anchor |
|---|---|---|---|---|---|
| `fallback.*` | C-CP-03 §3.5 | 9 attributes | `fallback.triggered` / `fallback.exhausted` always-sampled per C-CP-03 §3.5 | `fallback.triggered` span event on parent + new sibling fallback span (D6 §1.2 line 127) | ADR-F3 v1.1 capability-floor (iv) |
| `retry.*` | C-CP-03 §3.5 | 4 attributes | Base-rate at 1st attempt; always-sampled at 2nd onward per C-CP-03 §3.5 | `retry.attempt` span event on parent + new sibling retry span (D6 §1.2 line 128) | ADR-F3 v1.1 capability-floor (iv) |
| `lease.*` | C-CP-05 §5.3 | 5 attributes | Base-rate per C-CP-05 §5.4 | `lease.acquired` / `lease.released` span events on parent (D6 §1.2 lines 130–131) | ADR-F3 v1.1 capability-floor (iv) |
| `harness.breaker.*` | C-CP-03 §3.5 (CP-side deployment composition); `c9-reliability-recovery` SKILL.md (substrate-anchored canonical declaration per F2-16 closure and Workflow v1.3 §2.3.3.1 clause (iii)) | 7 attributes (per OD C-OD-07 §7.1 canonical schema; enumerated at D6 §1.2.1) | `breaker.tripped` always-sampled per C-CP-03 §3.5 + D6 §1.3 | `breaker.tripped` span event on parent (D6 §1.2 line 129); seven-attribute schema at D6 §1.2.1 | `c9-reliability-recovery` SKILL.md substrate (NOT CP-anchored); CP consumes but does not own the canonical declaration |

#### §24.1.C Inheritance-composition note (one namespace; NOT ingested at D6 §1.2)

| Namespace | Source contract | Attribute count | Sampling composition | D6 ingest posture |
|---|---|---|---|---|
| `routing.*` | C-CP-01 §1.4 | 4 attributes | Inherits sampling from parent `llm.inference` span per OTel GenAI semconv 1.41.0 [HIGH] | NOT ingested at D6 §1.2 specialization-layer namespace map; NOT in F3 capability-floor lifecycle event set. The four `routing.*` attributes attach to the parent `llm.inference` span and inherit that span's sampling decision; no independent D6 ingestion contract required. |

**Composition-path summary.** Six specialization-layer namespaces (§24.1.A) compose with D6's per-row attribute-set ingestion contract. Four F3-lifecycle-event-attribute namespaces (§24.1.B) compose with D6's F3 capability-floor (iv) lifecycle event sub-tree mapping; the `harness.breaker.*` row is structurally identical to the other three lifecycle namespaces except for source-authority posture (substrate-anchored at `c9-reliability-recovery` SKILL.md per F2-16 closure, not CP-anchored). One inheritance-composition namespace (§24.1.C) composes with OTel GenAI semconv 1.41.0 parent-span sampling discipline and is not ingested at D6 §1.2 at all. The three composition paths are surfaced explicitly at the export-table layer to prevent the export-claim ↔ ingest-reality structural conflation flagged at `Adversarial_Review_5_iter2.md` F-iter2-01.

### §24.2 Cross-axis composition exports

| Export surface | Consuming axis (session 4) | Composition reference |
|---|---|---|
| Eight F3 lifecycle event classes per C-CP-05 §5.1 | Operational Discipline (D6 v1.1 unified span schema) | D6 §1.2 unified span schema ingests these classes; per-cell sampling per D6 §1.3 |
| Cost-attribution-per-span anchors per C-CP-14 §14.1 (fan-out boundaries) | Operational Discipline (D6 v1.1 cost-attribution-per-span) | D6 §1.5 cost-attribution joins via `idempotency_key` per C-IS-10 §10.2; per-sibling rollup composes at `topology.fanout.closed` per C-CP-14 §14.1 |
| Per-cell operator-burden eval primitive per C-CP-21 §21.7 | Operational Discipline (D6 v1.1 operator-burden eval primitive) | D6 §1.6 per-cell dashboard binding; `expected_hitl_invocations_per_session` computed from `hitl.invocation.responded` span counts |
| Bridging-arc traversal preservation across HITL placement + audit-ledger cryptographic shape | Operational Discipline (D6 v1.1 bridging-arc traversal preservation) | D6 §1.1 9-cell matrix + ADD §5.3.1 bridging-arc traversal preservation |

### §24.3 Cross-axis composition with session 5 (cross-axis composition document)

| Surface | Cross-axis composition |
|---|---|
| T-perm-1 5-axis multiplicative tunable | C-CP-19 4-axis + `Spec_Action_Surface_v1.md` C-AS-12 5-axis specialization compose at ADD §5.2.1 multi-layer resolution |
| T-perm-3 multi-layer resolution | C-CP-23 three-layer composition (F1 + D1 + D4) at ADD §5.2.3 |
| Sub-agent boundary monotonic-only descent | C-CP-12 + `Spec_Action_Surface_v1.md` C-AS-11 compose at ADD §5.3.2 |
| Deterministic-outer-harness boundary | All Control Plane chain-advancement + cascade-enforcement + retry mechanics + breaker mechanics + HITL escalation contracts compose at ADD §5.3.3 |

### §24.4 F2-12 carry-forward export

The F2-12 carry-forward (D1 v1.1 → v1.2 replay-trace-emission contract) per `Phase_5_Session_3_Session_Prompt.md` §5.4 [CF-1] is **active at C-CP-08** (R-CP-07-satisfying contract). Closure expected as D1 v1.2 + D6 v1.2; absorbed into ADD v1.3; PRD revision pass produces `PRD_v1.1.md`; Control Plane spec revision pass at C-CP-08 (`Spec_Control_Plane_v1.1.md`); Operational Discipline spec revision at the corresponding cost-attribution-per-span contract (session 4 territory). Sessions 4 + 5 inherit this carry-forward at their respective §[carry-forwards] sections.

**Deferred to implementation discretion.** Specific cross-spec citation strings (resolved at session 4 + session 5 composition document); specific seam-versioning convention if F1 / F3 / D1 / D4 / D5 ever revise (out of scope at v1).

---

## §[carry-forwards]

This meta-section documents PRD-inherited carry-forward items per `Phase_5_Session_3_Session_Prompt.md` §5.4. Entries are **documentation, not contract-bearing** — they do not engage the §[coherence pass] §6.1 per-contract audit (except the affected-contract notation at C-CP-08, which IS contract-bearing per §6.1); they engage the spec's operator-visibility surface.

### [CF-1] F2-12 — D1 v1.1 → v1.2 replay-trace-emission contract (ACTIVE engagement at C-CP-08)

**Status.** 🔄 Deferred-acknowledged at ADD v1.2 §6.3.1 (inherited at PRD v1.0 §[carry-forwards] [CF-1] + session-1 spec §[carry-forwards] [CF-1] + session-2 spec §[carry-forwards] [CF-1]); not blocking session 3 entry; not blocking session 3 filing.

**Scope.** D1 v1.1 → v1.2 replay-trace-emission contract covering: (i) span re-emission semantics under engine replay (event-sourced-replay engines: do spans re-emit, or is replay a deterministic re-read without new span emission?); (ii) `retry.attempt` sibling-span discipline (does the retry emit `retry.attempt` event AND a new sibling span per D6 §1.2?); (iii) trace-ingestion dedup composition with F2 `idempotency_key` (cost-attribution-per-span at D6 §1.5 must avoid double-counting on replay).

**Control Plane spec impact.** **ACTIVE engagement at C-CP-08.** Per `Phase_5_Session_3_Session_Prompt.md` §5.4 [CF-1] authoring approach (iii):

- **C-CP-08** (R-CP-07-satisfying contract) authors at the current D1 v1.1 commitment level (replay semantics as currently committed at D1 §1.1 + engine-class taxonomy per §1.2). The five-element resumption-kind enum + idempotency-key join per C-CP-08 §8.1 + §8.2 are the v1 closure.
- **C-CP-08 §8.4** carries the explicit F2-12 carry-forward affected-contract notation per `Phase_5_Session_3_Session_Prompt.md` §5.4 [CF-1] authoring approach (iii).
- **C-CP-03 §3.5** notes that `retry.attempt` sibling-span vs span-event treatment is part of F2-12 deferred scope; the v1 commitment is the attribute substrate and base-rate-then-always-sampled discipline.
- D1 v1.2 + D6 v1.2 closure will trigger a Control Plane spec revision pass at C-CP-08 (and possibly C-CP-03 §3.5 if `retry.*` semantics expand at D6 v1.2 closure).

**Forward routing.** Parallel `council-orchestrator` C7+C9 session at operator discretion per ADD §6.3.1 active path. Closure expected as D1 v1.2 + D6 v1.2; absorbed into ADD v1.3; PRD revision pass produces `PRD_v1.1.md`; Control Plane spec revision pass at C-CP-08 (`Spec_Control_Plane_v1.1.md`); Operational Discipline spec revision at corresponding cost-attribution-per-span contract (session 4 territory).

### [CF-2] Workflow §7 substrate-skill propagation

**Status.** Open operator decision; outside P3-CK closure scope; outside PRD scope; outside Phase 5 scope.

**Origin.** `Project_Workflow_Revision_log.md` v1.4 entry line 297 footnote — `add-consolidation-protocol.md` §3.5 Step 5 substrate-skill update to reference Workflow v1.4 §2.3.5 clause (iv) is a separate skill-substrate revision not in v1.4 scope. Per `Phase_5_Session_3_Session_Prompt.md` §1.4, Workflow §7 session-prompt-template revision is also recommended, triggered by confirmed systemic Pattern P1 from P3c-CK Iteration 1; this is a parallel skill-substrate revision concern.

**Control Plane spec impact.** Not in spec scope (skill-substrate revision is neither architectural commitment nor observable behavior nor contract-bearing material). Documented here for operator-visibility continuity from PRD §[carry-forwards] [CF-2] + session-1 spec [CF-2] + session-2 spec [CF-2]; tracked outside the spec-driven Phase 5 workflow.

**Forward routing.** Operator decision at discretion. No Phase 5 spec revision is triggered by skill-substrate propagation.

---

## §[traceability]

PRD-requirement-to-spec-contract sub-matrix for the Control Plane axis. Rows = 12 PRD requirements (R-CP-01 through R-CP-12); columns = 24 spec contracts (C-CP-01 through C-CP-24). `✓` indicates the spec contract satisfies the PRD requirement (cited at the contract's "PRD requirement(s) satisfied" sub-section).

| PRD requirement | Satisfying spec contracts |
|---|---|
| **R-CP-01** — Routing decision visible at LLM call surface | C-CP-01 §1.4 (run-event attribution); C-CP-02 §2.3 (per-layer attribution); C-CP-24 (substrate seam exports) |
| **R-CP-02** — Cross-family fallback announced before error path | C-CP-02 §2.4; C-CP-03 (per-layer time budget with deterministic fall-through); C-CP-04 (cross-family fallback chain composition); C-CP-23 (T-perm-3 multi-layer F1-layer resolution); C-CP-24 |
| **R-CP-03** — Per-provider capability surface introspectable at authoring time | C-CP-01 §1.2 (capability-introspection API); C-CP-24 |
| **R-CP-04** — Workflow lifecycle event surface | C-CP-05 (F3 capability-floor lifecycle event surface); C-CP-09 (engine.* span attribute namespace); C-CP-24 |
| **R-CP-05** — Manifest-default invocation with per-step opt-in override | C-CP-06 (manifest-declaration invocation discipline with per-step opt-in override); C-CP-24 |
| **R-CP-06** — Engine class committed per deployment surface at design time | C-CP-07 (five-element engine-class taxonomy with per-deployment-surface candidate mapping); C-CP-23 (T-perm-3 multi-layer D1-layer resolution); C-CP-24 |
| **R-CP-07** — Replay-resumption semantics visible at run resumption | **C-CP-08** (replay-resumption semantics per engine class — F2-12 active engagement); C-CP-24 |
| **R-CP-08** — Multi-agent topology selectable at workflow definition | C-CP-10 (six-pattern multi-agent topology taxonomy); C-CP-11 (per-workload-class topology commitment + 2D matrix); C-CP-13 (HandoffContext + brief object structure); C-CP-14 (multi-agent span hierarchy + concurrent-prompt-cache warm-up); C-CP-15 (cross-sibling audit-ledger discipline); C-CP-23 (T-perm-3 multi-layer D4-layer resolution); C-CP-24 |
| **R-CP-09** — Sub-agent privilege inheritance with monotonic-only descent | C-CP-12 (sub-agent privilege inheritance contract); C-CP-15 (cross-sibling audit-ledger discipline); C-CP-19 (T-perm-1 D5-layer multiplicative gate-level rule with cross-deployment monotonicity); C-CP-24 |
| **R-CP-10** — HITL four-response palette at every gate | C-CP-16 (four-response palette + audit ledger entry shape); C-CP-18 (synchrony-class × HITL-primitive-shape matrix); C-CP-21 (pre-HITL escalation order + validator.fail.* taxonomy — palette-restriction rule); C-CP-22 (context revalidation on HITL resume); C-CP-24 |
| **R-CP-11** — Three-placement HITL topology primitive at workflow definition | C-CP-17 (three-placement HITL topology primitive + interface signature); C-CP-18 (synchrony-class × HITL-primitive-shape matrix — cell applicability); C-CP-21 (pre-HITL escalation order — validator-escalation invocation); C-CP-22 (context revalidation on HITL resume); C-CP-24 |
| **R-CP-12** — Audit-ledger cryptographic shape per persona tier | C-CP-15 (cross-sibling audit-ledger discipline — multi-agent extension); C-CP-19 (T-perm-1 D5-layer multiplicative gate-level rule — multiplicative tunable surface); C-CP-20 (per-persona-tier audit-ledger cryptographic shape + audit.* attribute namespace); C-CP-24 |

**Bidirectional verification.**

| Verification rule | Result |
|---|---|
| Every session-3 PRD requirement has ≥1 spec contract satisfying it | ✅ — R-CP-01 (3 contracts); R-CP-02 (5); R-CP-03 (2); R-CP-04 (3); R-CP-05 (2); R-CP-06 (3); R-CP-07 (2); R-CP-08 (7); R-CP-09 (4); R-CP-10 (5); R-CP-11 (5); R-CP-12 (4). 12 of 12 satisfied |
| Every session-3 spec contract has ≥1 PRD requirement it satisfies | ✅ — C-CP-01 through C-CP-24 each cite ≥1 R-CP-* requirement at their "PRD requirement(s) satisfied" sub-section; C-CP-24 cites all twelve as cross-axis composition surface |
| 12 PRD requirements present | ✅ (R-CP-01 through R-CP-12 enumerated) |
| 24 spec contracts present | ✅ (C-CP-01 through C-CP-24 enumerated) |

---

## §[coherence pass]

Pre-emission self-audit per `Phase_5_Session_3_Session_Prompt.md` §6. Five audit dimensions; spec does not file unless all five return ✅ PASS.

### Audit 6.1 — Per-contract audit (24 contracts × 10 sub-dimensions)

| Sub-dimension | Verification posture | Result |
|---|---|---|
| PRD requirement trace | Every spec contract cites ≥1 PRD R-ID; cited requirement is in session-3 axis scope (R-CP-01 through R-CP-12) | ✅ PASS — spot-check: C-CP-01 cites R-CP-01 + R-CP-03; C-CP-08 cites R-CP-07; C-CP-12 cites R-CP-09; C-CP-19 cites R-CP-09 + R-CP-12; C-CP-20 cites R-CP-12; C-CP-23 cites R-CP-02 + R-CP-06 + R-CP-08. 24 of 24 contracts carry PRD requirement citations |
| ADR commitment trace | Every spec contract cites ≥1 ADR by ID **and** section (per inversion-discipline analog) | ✅ PASS — spot-check: C-CP-01 cites `ADR-F1 v1.2 §Decision + §Consequences (a)`; C-CP-05 cites `ADR-F3 v1.1 §Decision capability-floor (iv)`; C-CP-07 cites `ADR-D1 v1.1 §Decision + §1.1 + §1.2 + §1.4`; C-CP-11 cites `ADR-D4 v1.1 §1.2 + §1.3 + §1.4 + §1.6`; C-CP-20 cites `ADR-D5 v1.3 §1.4 + §1.4.1 + §1.8`. 24 of 24 contracts carry section-level ADR citations |
| Cross-axis citation (Information Substrate) | Spec contracts that compose against the Information Substrate substrate seam cite `Spec_Information_Substrate_v1.md` C-IS-* by contract ID + section | ✅ PASS — C-CP-08 cites C-IS-05 + C-IS-10 §10.2; C-CP-13 cites C-IS-05 + C-IS-10 §10.1; C-CP-15 cites C-IS-05 + C-IS-06 + C-IS-07; C-CP-20 cites C-IS-05 + C-IS-06 + C-IS-07; C-CP-22 cites C-IS-05 + C-IS-07. All five contracts that compose against the F2 substrate seam carry section-level cross-axis citations |
| Cross-axis citation (Action Surface) | Spec contracts that compose against the Action Surface substrate seam cite `Spec_Action_Surface_v1.md` C-AS-* by contract ID + section | ✅ PASS — C-CP-11 cites C-AS-13 §13.4; C-CP-12 cites C-AS-11 + C-AS-12; C-CP-13 cites C-AS-13 §13.4; C-CP-14 cites C-AS-15 + C-AS-14 §14.2; C-CP-19 cites C-AS-12; C-CP-20 cites C-AS-05; C-CP-21 cites C-AS-04 + C-AS-13 §13.4 + C-AS-05; C-CP-22 cites C-AS-10. All eight contracts that compose against the F4/F5/D2/D3 substrate seams carry section-level cross-axis citations |
| No-architecture-introduction | No spec contract adds architectural commitment beyond ADR + ADD + Information Substrate spec + Action Surface spec content; contracts compose committed material into specification-grade precision | ✅ PASS — every contract derives directly from F1/F3/D1/D4/D5 ADR sections + ADD §2.1/§2.3/§3.1.1/§3.1.2/§3.1.3/§5.1/§5.2.1/§5.2.3/§5.3.2/§5.3.3/§6.3.1 + cross-axis spec citations. No contract asserts a property not committed at ADR/ADD level. §[carry-forwards] [CF-1] explicitly notes F2-12 active engagement at C-CP-08 with deferred sub-scope to D1 v1.2 + D6 v1.2 closure |
| Translate-not-restate | No spec contract restates PRD observable-behavior text, ADR Decision text, Information Substrate spec contract text, or Action Surface spec contract text verbatim; contracts translate via composition | ✅ PASS — every contract section provides specification-grade structure (signatures, schemas, formulas, enums, surface contracts, matrices) absent from PRD / ADR / cross-axis spec prose. ADR text cited by section, not restated. Spot-check: C-CP-19 §19.1 decomposes ADR-D5 v1.3 §1.5.1 multiplicative rule into per-axis floor enumeration + runtime evaluation surface; C-CP-21 §21.5 declares the three `validator.fail.*` attributes with types + cardinality + always-emitted scope beyond the ADR-D5 v1.3 §1.10.1 enumeration |
| Persona linkage preserved | Every spec contract preserves the persona §X.y anchor from its parent PRD requirement | ✅ PASS — spot-check: C-CP-01 carries Persona §5 + §7 + §10.2 + §10.3 inherited from R-CP-01 + R-CP-03; C-CP-05 carries Persona §4 + §10.4 + §8.3 inherited from R-CP-04; C-CP-08 carries Persona §4 + §10.4 + §11.3 inherited from R-CP-07; C-CP-19 carries Persona §4 + §10.4 + §10.2 inherited from R-CP-09 + R-CP-12; C-CP-20 carries Persona §10.4 + §11.6 + §11.7 + §11.10 inherited from R-CP-12. 24 of 24 contracts carry persona anchors |
| Contract grade | Every spec contract sits at specification grade (signature / schema / formula / enum / surface contract / matrix); no implementation-grade choices beyond what ADRs commit | ✅ PASS — contract surfaces are: C-CP-01 core operation signatures + capability-introspection API signature + manifest residence surface contract (signatures + surface contract); C-CP-02 layer ordering algorithm + per-layer attribution table (algorithm + table); C-CP-03 layer-budget schema + fall-through procedure + 3 namespace declarations (schema + procedure + tables); C-CP-04 chain shape schema + advancement-triggers table + cross-family transition events (schema + tables); C-CP-05 8-event enumeration + per-event attribute table + lease.* namespace declaration (enum + tables); C-CP-06 manifest field schema + annotation override syntax (schemas); C-CP-07 5-class taxonomy + per-surface candidate mapping + capability-floor preservation matrix (enum + matrices); C-CP-08 resumption-kind enum + F2 join discipline table (enum + table); C-CP-09 3-attribute declaration + per-row tier mapping (schema + table); C-CP-10 6-pattern enumeration + topology declaration signature (enum + schema); C-CP-11 per-workload-class commitment + per-engine overlay + 2D matrix + multiplicative tunable specialization (matrices + tables + tunable); C-CP-12 default-downgrade rule + gate-level formula + monotonicity contract (rules + formula + table); C-CP-13 HandoffContext schema + brief object schema + model-binding inheritance table (schemas + table); C-CP-14 span hierarchy + 17 attributes across 2 namespaces + sampling discipline + cache-warm-up protocol (schemas + tables + protocol); C-CP-15 sibling entry shape + parent_fanout_close_entry shape + merkle construction algorithm + per-tier table (schemas + algorithm + tables); C-CP-16 4-value palette + per-response audit shape + invariance contract (enum + schema + contract); C-CP-17 3-placement enumeration + hitl_gate signature + HITL-as-tool-call rewriting contract (enum + signature + contract); C-CP-18 2D matrix + overlay/meta-class contracts + selection contract (matrices + contracts); C-CP-19 4-axis multiplicative formula + monotonicity invariant + 5-axis D2-layer composition (formula + invariant); C-CP-20 per-tier cryptographic shape + signing-key resolution + rotation protocol + 7 attribute declarations (schemas + protocol + tables); C-CP-21 5-class fail taxonomy + transient staircase + palette restriction + 3 attribute declarations (enum + procedure + tables); C-CP-22 resume protocol + material-diff predicate (procedures + table); C-CP-23 three-layer composition + per-cell reading + runtime resolution (composition + tables); C-CP-24 10 namespace exports + cross-axis composition exports (tables). No implementation-grade commitments beyond ADR-declared |
| Deferred-to-implementation discretion documented | Contracts that defer detail to Phase 6 implementation discretion per Workflow §2.5.1 exit criteria language carry explicit "deferred to implementation discretion" notation | ✅ PASS — 23 of 24 contracts carry explicit "Deferred to implementation discretion" notation (C-CP-24 is a meta-contract referencing other contracts' implementation deferrals); deferrals include: specific provider catalog (C-CP-01); specific embedding model and classifier corpus (C-CP-02); specific timeout values per cell (C-CP-03); specific provider-family enumeration (C-CP-04); specific OTel/OTLP emission timing (C-CP-05); specific annotation syntax (C-CP-06); specific engine candidate within cells (C-CP-07); specific span-re-emission semantics (C-CP-08 — F2-12 carry-forward); specific event-id serialization (C-CP-09); specific candidate-within-pattern selection (C-CP-10); specific cell-binding selection timing (C-CP-11); specific operator override authoring schema (C-CP-12); specific HandoffContext serialization format (C-CP-13); specific cache acknowledgement protocol (C-CP-14); specific merkle library binding (C-CP-15); specific operator UI surface (C-CP-16); specific manifest-validation library (C-CP-17); specific candidate-within-class selection (C-CP-18); specific runtime evaluation engine (C-CP-19); specific signature library binding (C-CP-20); specific cause-attribution enum extension (C-CP-21); specific snapshot_capture library binding (C-CP-22); specific per-cell cascade timeout calibration (C-CP-23) |
| F2-12 carry-forward flagged at R-CP-07-satisfying contract | The C-CP-* contract that satisfies R-CP-07 carries explicit F2-12 carry-forward notation per §5.4 [CF-1] authoring approach (iii) | ✅ PASS — C-CP-08 §8.4 carries explicit F2-12 carry-forward affected-contract notation per session prompt §5.4 [CF-1] authoring approach (iii); the three deferred sub-scopes (span re-emission semantics, `retry.attempt` sibling-span discipline, trace-ingestion dedup composition with F2 `idempotency_key`) are explicitly named; forward-routing to parallel `council-orchestrator` C7+C9 session documented; spec revision-trigger at D1 v1.2 + D6 v1.2 closure documented; C-CP-03 §3.5 also notes the `retry.attempt` sibling-span sub-scope as part of F2-12 deferred material |

**Audit 6.1 aggregate: ✅ PASS (10/10 sub-dimensions across all 24 contracts).**

### Audit 6.2 — PRD-requirement-to-spec sub-matrix audit (Control Plane axis only)

| Sub-dimension | Result |
|---|---|
| Every session-3 PRD requirement has ≥1 spec contract satisfying it | ✅ PASS — per §[traceability] sub-matrix; 12 of 12 R-CP-* requirements have ≥1 satisfying contract |
| Every session-3 spec contract has ≥1 PRD requirement it satisfies | ✅ PASS — per §[traceability] sub-matrix; no orphan contracts; C-CP-01 through C-CP-24 each cite ≥1 R-CP-* requirement |
| ADR commitments cited at session-3 spec are at versions matching PRD substrate set | ✅ PASS — F1 cited at v1.2; F3 cited at v1.1; D1 cited at v1.1; D4 cited at v1.1; D5 cited at v1.3; matches `Phase_5_Session_3_Session_Prompt.md` §3.2 substrate version table; matches PRD §"ADR substrate set" table |
| Cross-axis citations resolve (Information Substrate) | ✅ PASS — every Information Substrate spec citation (C-IS-XX § Y.Z) verified to resolve to a section/contract present in `Spec_Information_Substrate_v1.md`: C-IS-05 (state-ledger entry shape, present at §5); C-IS-06 (hash-chain integrity construction, present at §6); C-IS-07 §7.1/§7.2 (read/write contract pair, present at §7); C-IS-09 (worktree-isolation, present at §9); C-IS-10 §10.1/§10.2/§10.4 (substrate seam exports, present at §10) |
| Cross-axis citations resolve (Action Surface) | ✅ PASS — every Action Surface spec citation (C-AS-XX § Y.Z) verified to resolve to a section/contract present in `Spec_Action_Surface_v1.md`: C-AS-03 (tool contract field signature, present at §3); C-AS-04 (sandbox fail-class taxonomy, present at §4); C-AS-05 §5.2 (tier-aware resolution, present at §5); C-AS-10 §10.1/§10.3 (per-MCP-server trust framework + material-diff predicate composition, present at §10); C-AS-11 (sub-agent sandbox-tier monotonic-ascension, present at §11); C-AS-12 (T-perm-1 D2-layer 5-axis multiplicative tunable, present at §12); C-AS-13 §13.4/§13.5/§13.6 (per-sub-agent-role model-binding + Anthropic-API graceful-degradation + workload-binding-time selection, present at §13); C-AS-14 §14.2/§14.3 (anthropic.* + mcp.* namespaces, present at §14); C-AS-15 (sandbox-bounded span schema, present at §15) |

**Audit 6.2 aggregate: ✅ PASS (5/5 rules).**

### Audit 6.3 — Front-matter audit (session-3 spec)

| Sub-dimension | Result |
|---|---|
| Session-3 axis declared at front-matter | ✅ PASS — Status block records "Axis: Control Plane (per `Phase_5_Entry_Handoff.md` §3.1 axis sequencing; OD-5-2.A re-application at session 3 entry — recommendation followed)"; Front-matter §"Axis declaration" + §"Axis-grounding note" carry rationale |
| PRD substrate reference | ✅ PASS — `PRD_v1.0.md` §1 cited at Status block Source-set + Front-matter §"PRD requirement scope" |
| ADR substrate reference | ✅ PASS — F1 v1.2 + F3 v1.1 + D1 v1.1 + D4 v1.1 + D5 v1.3 enumerated at Status block Source-set + Front-matter §"ADR scope" table |
| ADD substrate reference | ✅ PASS — ADD v1.2 §2.1 + §2.3 + §3.1.1 + §3.1.2 + §3.1.3 + §5.1 + §5.2.1 + §5.2.3 + §5.3.2 + §5.3.3 + §6.3.1 cited at Status block Source-set; specific ADD sub-sections cited at every contract that derives from F1/F3/D1/D4/D5 substrate |
| Information Substrate spec reference | ✅ PASS — `Spec_Information_Substrate_v1.md` cited at Status block Source-set; specific contracts (C-IS-05, C-IS-06, C-IS-07, C-IS-09, C-IS-10) cited at Front-matter §"Cross-axis citation substrate" table; C-CP-08 + C-CP-13 + C-CP-15 + C-CP-20 + C-CP-22 specifically cite Information Substrate contracts |
| Action Surface spec reference | ✅ PASS — `Spec_Action_Surface_v1.md` cited at Status block Source-set; specific contracts (C-AS-04, C-AS-05, C-AS-10, C-AS-11, C-AS-12, C-AS-13, C-AS-14, C-AS-15, C-AS-16) cited at Front-matter §"Cross-axis citation substrate" table; C-CP-11 + C-CP-12 + C-CP-13 + C-CP-14 + C-CP-19 + C-CP-20 + C-CP-21 + C-CP-22 specifically cite Action Surface contracts |
| Persona substrate reference | ✅ PASS — Persona Document anchors (§3.1, §3.1.1–§3.1.4, §3.2, §4, §5, §5.1, §6, §7, §8.1–§8.5, §9, §10.1, §10.2, §10.4, §11.3, §11.4, §11.6, §11.7, §11.10) enumerated at Front-matter §"Persona-linkage substrate" table; per-contract persona linkage inherited from PRD requirements |
| Status posture | ✅ PASS — `Status: Proposed` per `Project_Workflow_v1_2.md` §3.1 (no clearance until aggregate P5-CK per Workflow §2.5.1 + OD-5-4.A) |

**Audit 6.3 aggregate: ✅ PASS (8/8 sub-dimensions).**

### Audit 6.4 — §[carry-forwards] inheritance audit

| Sub-dimension | Result |
|---|---|
| F2-12 carry-forward documented at session-3 spec | ✅ PASS — [CF-1] entry inherits PRD v1.0 §[carry-forwards] [CF-1] + session-1 spec [CF-1] + session-2 spec [CF-1] verbatim; **active engagement at Control Plane** with explicit C-CP-08 affected-contract notation (and additional notation at C-CP-03 §3.5 `retry.attempt` sub-scope); forward routing documented |
| Workflow §7 substrate-skill propagation carry-forward documented | ✅ PASS — [CF-2] entry inherits PRD v1.0 §[carry-forwards] [CF-2] + session-1 spec [CF-2] + session-2 spec [CF-2] verbatim; explicit Control Plane spec engagement statement documents non-engagement; reference to session prompt §1.4 Workflow §7 session-prompt-template revision recommendation included |
| Carry-forward entries labeled as non-contract-bearing (except C-CP-08 affected-contract notation) | ✅ PASS — meta-section preamble explicitly states "Entries are documentation, not contract-bearing — they do not engage the §[coherence pass] §6.1 per-contract audit (except the affected-contract notation at C-CP-08, which IS contract-bearing per §6.1)" |

**Audit 6.4 aggregate: ✅ PASS (3/3 sub-dimensions).**

### Audit 6.5 — V3 deference audit

| Sub-dimension | Result |
|---|---|
| Confidence-tag schema | ✅ PASS — V3 `[HIGH]` / `[MODERATE]` / `[SPECULATIVE]` schema preserved; tags applied at the specification surfaces where uncertainty surfaces: Cluster 1 V2 §2.2.2 Anthropic Prompt Caching docs cited [HIGH] at C-CP-04 §4.3; LiteLLM-mediated fallback cited [MODERATE] at C-CP-04 §4.3 per F1 §Rationale (b); Cluster 1 §1 Cognition-Anthropic adjudication cited [HIGH] at C-CP-11 §11.1; Anthropic research system 3–5 fan-out cited [HIGH] at C-CP-11 §11.1; Diagrid Feb 25 2026 critique implicit at C-CP-07 §7.1 row distinctions; Cluster 4 §2.2.7 Stripe-style idempotency key cited [HIGH] at C-CP-15 §15.1; LangGraph HITL doc cited [HIGH] at C-CP-18 §18.1; Temporal HITL doc cited [HIGH] at C-CP-18 §18.1; Cluster 4 §2.4 HITL-as-checkpoint structural identity cited [HIGH] at C-CP-18 §18.4 indirectly. No fabricated [HIGH] tags |
| Citations resolve at section level | ✅ PASS — every ADR citation verified by reading the ADR section at the indicated location during substrate read (`view` calls on ADR-F1.md, ADR-F3.md, ADR-D1.md, ADR-D4.md, ADR-D5.md, PRD_v1.0.md, Spec_Information_Substrate_v1.md, Spec_Action_Surface_v1.md, Phase_5_Session_3_Session_Prompt.md at session entry); every persona §X.y anchor verifiable at the indicated section (anchors inherited from PRD §[coherence pass] which audited persona anchors at PRD filing); every Information Substrate spec contract ID + section verifiable; every Action Surface spec contract ID + section verifiable |
| Anti-fabrication discipline applied | ✅ PASS — no fabricated PRD requirements; no fabricated ADR sections; no fabricated Information Substrate spec contracts; no fabricated Action Surface spec contracts; no invented benchmarks / vendor capabilities; substrate retrieved via `view` against source files at session execution before emission; no novel primitives, providers, or mechanisms introduced beyond ADR substrate enumeration |
| Workflow v1.4 §2.3.5 clause (iv) analog | ✅ PASS — section-level citation discipline applied at contract granularity (analog to PRD requirement-granularity citation); every contract carries ADR-ID + section pair in its "ADR commitment(s) honored" sub-section; cross-axis citations carry spec-ID + contract-ID + section pair in their "Cross-axis citation" sub-sections |

**Audit 6.5 aggregate: ✅ PASS (4/4 sub-dimensions).**

### Coherence pass aggregate

| Audit dimension | Result |
|---|---|
| 6.1 Per-contract audit | ✅ PASS (10/10) |
| 6.2 PRD-requirement-to-spec sub-matrix audit | ✅ PASS (5/5) |
| 6.3 Front-matter audit | ✅ PASS (8/8) |
| 6.4 §[carry-forwards] inheritance audit | ✅ PASS (3/3) |
| 6.5 V3 deference audit | ✅ PASS (4/4) |

**Coherence pass: ✅ PASS at all five dimensions. Spec authorized for filing.**

---

*Filed 2026-05-13 at Phase 5 session 3 close → Phase 5 session 4 entry boundary. Session 3 scope: Control Plane axis specification per OD-5-2.A spec-writer judgment (handoff §3.1 recommendation followed; no divergence); output `Spec_Control_Plane_v1.md` per OD-5-1.A axis-led decomposition. Phase 5 arc continues to session 4 (Operational Discipline) per `Phase_5_Entry_Handoff.md` §3.1 axis sequencing; session 4 session prompt filed at `Phase_5_Session_4_Session_Prompt.md`. Aggregate P5-CK at full specification close per Workflow §2.5.1 + OD-5-4.A. F2-12 active engagement at C-CP-08 per PRD §[carry-forwards] [CF-1]; affected-contract notation discipline applied per §6.1 audit. Phase 5 session 4 entry-gate AUTHORIZED against `PRD_v1.0.md` + ADD v1.2 + Persona Document + D6 v1.1 + secondary-axis surfaces from F1/F2/F3/F4/F5/D1/D2/D3/D4/D5 by citation + `Spec_Information_Substrate_v1.md` + `Spec_Action_Surface_v1.md` + `Spec_Control_Plane_v1.md` as substrate.*
