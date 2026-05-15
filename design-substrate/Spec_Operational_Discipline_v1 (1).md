# Spec — Operational Discipline v1

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1.md` |
| Status | **Proposed** (v1.1 pending P5-CK iteration 2 clearance per `Project_Workflow_v1_2.md` §3.1); revision-pass post-P5-CK iter-1 close per `Project_Workflow_v1_2.md` §4.1.2 modified path; coherence pass preserved verbatim as v1 historical record per Change-note §"Sections preserved verbatim" |
| Date | 2026-05-13 |
| Phase | 5 — specification authoring (session 4 of 4–6) per `Project_Workflow_v1_2.md` §2.5 |
| Skill | `spec-writer` SKILL.md in Stage-3 final-specification mode per skill description |
| Axis | Operational Discipline (per `Phase_5_Session_4_Session_Prompt.md` §2.2 OD-5-2.A re-application; handoff §3.1 sequencing recommendation followed) |
| Source-set | `PRD_v1.0.md` §4 (R-OD-01 through R-OD-08); `Architectural_Design_Document_v1.md` v1.2 §3.4.1 + §5.1.1 + §5.1.3 + §5.3.1 + §6.3.1 + Appendix B; `ADR-D6.md` v1.1 (§Decision + §1.1 + §1.2 + §1.2.1 + §1.3 + §1.4 + §1.5 + §1.6 + §1.7 + §1.8 + §1.9); secondary-axis ADRs by citation only at expected versions (F1 v1.2 / F2 v1.2 / F3 v1.1 / F4 v1.1 / F5 v1.1 / D1 v1.1 / D2 v1.1 / D3 v1.1 / D4 v1.1 / D5 v1.3); `Persona_Document_v1.md` §2 + §4 + §6 + §9 + §10.2 + §10.4 + §11.4 + §11.10 + §11.12; `Spec_Information_Substrate_v1.md` (C-IS-05 + C-IS-06 + C-IS-07 + C-IS-10); `Spec_Action_Surface_v1.md` (C-AS-14 + C-AS-15 + C-AS-16); `Spec_Control_Plane_v1.md` (C-CP-03 + C-CP-05 + C-CP-09 + C-CP-14 + C-CP-20 + C-CP-21 + C-CP-24) |
| Entry authorization | `Phase_5_Session_4_Session_Prompt.md` §4 entry-gate verified (9/9); session-1/2/3 specs filed and coherence-pass-passed |
| ODs applied | OD-5-1.A (per-axis multi-document) + OD-5-2.A (spec-writer judgment; Operational Discipline per handoff §3.1) + OD-5-3.A (as-needed council consultant; no escalation invoked at session 4) + OD-5-4.A (aggregate P5-CK at full close) |
| Exit gate | This spec filed at `/mnt/user-data/outputs/`; §[coherence pass] returns ✅ PASS at all five audit dimensions; per §2.4 OD menu at session 4 close: either `Phase_5_Session_5_Session_Prompt.md` (option A) or `Phase_5_Specification_Authoring_Close_Handoff.md` (option B) authored |
| Revision | v1 → v1.1 (P5-CK iter-1 close mechanical revision per modified `Project_Workflow_v1_2.md` §4.1.2 path — F-OD-01 OD-side propagation at cross-axis citation cell line 69 (`ten` → `eleven` per operator selection B); F-CP-02 OD-RP-3.A Reading 1 namespace rename at C-OD-05 §5.1 row 7 (`topology.fanout.*` → `topology.*` with events as sub-tree); Stage-3b forward-flag alignment at C-OD-09 §"Cross-axis citation" line 498 (`breaker.trip` → `breaker.tripped` matching CP spec v1.1 §3.5 + §5.4); all other contracts preserved verbatim) |
| Revision date | 2026-05-13 |

---

## Change-note (v1 → v1.1)

**Scope of revision.** Three-finding revision pass clearing `Adversarial_Review_5.md` F-OD-01 OD-side half (Class 1 — front-matter line 27 + line 69 CP namespace count narrative harmonization per operator selection B = 11 namespaces; line 27 already canonical "eleven", line 69 revised "ten" → "eleven"), F-CP-02 OD-RP-3.A Reading 1 (Class 2 — C-OD-05 §5.1 row 7 namespace rename `topology.fanout.*` → `topology.*` with events as sub-tree under broader namespace), and Stage-3b forward-flag alignment (C-OD-09 §"Cross-axis citation" line 498 `breaker.trip` → `breaker.tripped` aligning with CP spec v1.1 §3.5 + §5.4 canonical event name). All three resolved at this single axis-spec revision pass per `P5-CK_Iteration_1_Close_Handoff.md` §3.2 + §3.3 + Stage-3b §36.2 forward-flag closure.

**F-OD-01 OD-side propagation per operator selection B = 11.** Front-matter line 27 already declares "Control Plane spec (C-CP-24) exports eleven Control Plane span attribute namespaces" — canonical under selection B; no revision required. Front-matter line 69 cross-axis citation cell revised: `ingests ten Control Plane span attribute namespaces` → `ingests eleven Control Plane span attribute namespaces`. Cross-field alignment achieved across all four narrative sites: OD line 27 = "eleven", OD line 69 = "eleven", CP front-matter line 36 = 11-namespace enumeration (Stage 3b), CP §24.1 preamble = "eleven namespaces" (Stage 3b). Composition doc §2.6 line 318 = "eleven" (already canonical; Stage 4 verification only).

**F-CP-02 OD-RP-3.A Reading 1 namespace rename per operator selection.** C-OD-05 §5.1 row 7 namespace cell renamed `topology.fanout.*` → `topology.*` with a reconciliation parenthetical clarifying the Reading 1 interpretation: "(broader namespace under OD-RP-3.A Reading 1; events `topology.fanout.opened` / `topology.fanout.closed` live as a sub-tree under `topology.*` per F-CP-02 closure)". The reconciliation reading interprets D6 §1.2's `topology.fanout.*` row as cataloging events under the broader `topology.*` namespace, rather than as a separate namespace at the same level. Operator decision binds at OD-RP-3.A; downstream propagation at PRD R-OD-02 and composition doc §2.6 line 295 per handoff §3.2 routing.

**Stage-3b forward-flag alignment at C-OD-09 line 498.** Cross-axis citation prose updated: `Spec_Control_Plane_v1.md C-CP-03 §3.5 (..., breaker.trip always-sampled)` → `... breaker.tripped always-sampled`. CP spec v1.1 (Stage 3b filed) renamed the event at C-CP-03 §3.5 (line 341) + C-CP-05 §5.1 (line 436) + C-CP-05 §5.4 (line 469); this OD-side cross-axis citation aligns to the renamed event name.

**Forward-flagged out-of-scope discoveries (non-blocking iteration 2).** Three concerns inherited from Stage 3b §36.2 or surfaced during this revision:

1. **CP §24.1 export table ↔ D6 §1.2 ingest map substrate-level alignment drift** (inherited from Stage 3b §36.2). CP §24.1 enumerates 11 namespaces; D6 §1.2 specialization-layer map enumerates only six CP-source namespaces (`engine.*`, `topology.fanout.*`, `subagent.*`, `hitl.*`, `audit.*`, `validator.fail.*`). Remaining CP-claimed exports (`fallback.*`, `retry.*`, `lease.*`, `routing.*`) appear in D6 §1.2 only as F3 capability-floor lifecycle events or not at all. `harness.breaker.*` substrate-anchored at `c9-reliability-recovery` SKILL.md per F2-16 closure, not CP-anchored. Resolution path is operator decision at iteration 2 entry-gate or downstream D6 v1.2 revision.

2. **F-CP-02 OD-RP-3.A Reading 1 vs D6 §1.2 row naming.** D6 §1.2 declares `topology.fanout.*` directly as a namespace; Reading 1 interprets it as a sub-tree under broader `topology.*`. The reconciliation parenthetical at C-OD-05 §5.1 row 7 documents the interpretation but does not amend D6 §1.2's row naming. Substrate-level resolution may require D6 v1.2 rename `topology.fanout.*` → `topology.*` (with sub-tree clarification) for full cross-spec alignment.

3. **F-CP-01 attribute semantic-loss** (inherited from Stage 3b §36.2). `breaker.cause` and `breaker.cooldown_ms` dropped from CP under canonical replacement; re-introduction would require OD C-OD-07 §7.1 schema expansion. Operator-decision territory at iteration 2 entry-gate.

**Sections preserved verbatim.** §Front-matter Axis declaration line 27 narrative (already canonical "eleven" under selection B); §Front-matter Axis-grounding note; §Front-matter PRD requirement scope table; §Front-matter ADR scope table rows for D6/F1/F2/F3/F4/F5/D1/D2/D3/D5 (only D4 row at line 90 amended for Reading 1 alignment); §Front-matter Cross-axis citation substrate rows for `Spec_Information_Substrate_v1.md` C-IS-10 + `Spec_Action_Surface_v1.md` C-AS-14/15/16 (only the CP row at line 69 amended); §Front-matter Persona-linkage substrate table; §1 through §4 (D6 §1.1 9-cell matrix + cell-selection contract); §5 C-OD-05 §5.1 rows 1–6 + rows 8–15 (only row 7 amended for F-CP-02 OD-RP-3.A); §5.2 + §5.3 (ingestion-posture invariants; F2-12 forward-compatibility note); §6 C-OD-06 (F3 capability-floor lifecycle event-to-span-event mapping); §7 C-OD-07 + C-OD-08 (`harness.breaker.*` seven-attribute schema canonical); §8 C-OD-08 (cardinality-safe attributes); §9 C-OD-09 §"ADR commitment(s) honored" + §"Persona linkage" + §9.1 + §9.2 + §9.3 + §"Deferred to implementation discretion" (only the §"Cross-axis citation" prose at line 498 amended at the `breaker.trip` token); §10 through §22 (all redaction, cost-attribution, operator-burden, local-OTLP-collector, tenant-isolation, cell-selection, persona-tier-binding, cross-deployment-monotonicity contracts); §23 C-OD-23 (substrate seam exports surface); §[traceability] matrix; §[carry-forwards]; §[coherence pass] (preserved verbatim as v1 point-in-time historical audit per Stage 2 + Stage 3a + Stage 3b precedent).

**Status posture.** `Status: Proposed (v1.1 pending P5-CK iteration 2 clearance per Project_Workflow_v1_2.md §3.1)`. v1.1 enters P5-CK iteration 2 as input artifact alongside ADR-D3 v1.2, PRD v1.0.1, IS spec v1.1, CP spec v1.1, and the composition doc revision (Stage 4) per handoff §6.1 entry-gate checklist.

**Changes inline.** Status block (Status row revised; Revision row + Revision date row appended). This Change-note section (new). §Front-matter Cross-axis citation substrate table row for `Spec_Control_Plane_v1.md` at line 69 (`ten` → `eleven`). §Front-matter ADR scope table D4 row at line 90 (`topology.fanout.*` → `topology.*` with Reading 1 reconciliation parenthetical — within-spec drift surfaced during post-amendment grep audit, consistent with C-OD-05 §5.1 row 7 alignment). §5 C-OD-05 §5.1 row 7 namespace cell (`topology.fanout.*` → `topology.*` + reconciliation parenthetical). §9 C-OD-09 §"Cross-axis citation" prose at line 498 (`breaker.trip` → `breaker.tripped`). No other content modified.

**§[coherence pass] preservation discipline.** §[coherence pass] section is v1 point-in-time audit; v1.1 mechanical revision does not re-run the audit. Audit rows referencing v1 substrate state are accurate historical record. v1.1 → v1.2 (if needed at iteration 2 entry or post-iter-2) is the proper moment for fresh coherence pass.

---

## Front-matter

### Axis declaration

Per OD-5-2.A spec-writer judgment with handoff §3.1 recommendation followed: **Operational Discipline** is the session-4 axis. Rationale:

- **Cross-cutting axis with single primary ADR.** ADR-D6 v1.1 commits the 9-cell deployment-surface × persona-tier matrix, the unified span schema with 15 specialization-layer namespaces, sampling / redaction / trace-storage / cost-attribution / operator-burden / local-first-OTLP-collector / bridging-arc disciplines. Ten secondary-axis ADRs (F1 / F2 / F3 / F4 / F5 / D1 / D2 / D3 / D4 / D5) are cited only as namespace-declaration sources — no ADR Decision-text restatement.
- **Sequenced last so the unified span schema ingests all prior-session substrate seam exports.** Information Substrate spec (C-IS-10) exports the F2 state-ledger entry shape, hash-chain construction, JSONL event ledger, and `idempotency_key` join. Action Surface spec (C-AS-16) exports the sandbox-bounded span schema and six Anthropic-primitive attribute namespaces. Control Plane spec (C-CP-24) exports eleven Control Plane span attribute namespaces. D6 §1.2 unified span schema ingests all three by citation without re-declaration.
- **F2-12 D6 v1.1 → v1.2 closure half active at R-OD-05.** Per PRD §[carry-forwards] [CF-1] and session prompt §5.4 [CF-1] authoring approach (iii), the cost-attribution-per-span composition with F2 `idempotency_key` is the Operational Discipline surface where the D6-side closure half of the F2-12 carry-forward sits. Affected-contract notation discipline applies at C-OD-14.

### Axis-grounding note

The Operational Discipline axis hosts **one D-ADR primary** (D6 v1.1 — observability backend with unified span schema ingestion contract) per ADD §3.4.1. Secondary-axis surfaces from F1 / F2 / F3 / F4 / F5 / D1 / D2 / D3 / D4 / D5 per ADD Appendix B are cited as namespace-declaration source D-ADRs — D6 §1.2 ingests their attribute namespaces without re-declaration. Cross-axis composition with the information substrate (D6 ↔ F2 span schema composition per ADD §3.4.1), action surface (D6 ↔ D2 sandbox-bounded span schema + D6 ↔ D3 Anthropic-primitive namespaces), and control plane (D6 ↔ D1 engine.* + D6 ↔ D4 topology.* + D6 ↔ D5 hitl./audit./validator.fail.*) is captured at C-OD-23 (substrate seam exports surface) for downstream consumption by session 5 (cross-axis composition document, if elected) and Phase 6+ implementation planning.

### PRD requirement scope

| PRD requirement | Observer role | Primary ADR section citation |
|---|---|---|
| R-OD-01 — Per-cell observability backend committed at deployment-binding time | Design-time operator | ADR-D6 v1.1 §Decision + §1.1 + §1.9; ADD §3.4.1 Synthesis |
| R-OD-02 — Unified span schema with 15 specialization-layer namespaces | Production-time operator + Downstream maintainer | ADR-D6 v1.1 §1.2 + §1.2.1; ADD §3.4.1 Synthesis (lines 272 enumeration) |
| R-OD-03 — Sampling discipline with always-sampled exceptions | Production-time operator | ADR-D6 v1.1 §1.3; ADD §3.4.1 Synthesis |
| R-OD-04 — Redaction discipline per persona tier at content-attribute capture surface | Production-time operator + Downstream maintainer | ADR-D6 v1.1 §1.4; ADD §5.3.1 bridging-arc traversal preservation |
| R-OD-05 — Cost-attribution per span at run cost-attribution surface | Production-time operator | ADR-D6 v1.1 §1.5; ADD §3.4.1 Synthesis; ADD §5.3 cost attribution as cross-cutting architectural property |
| R-OD-06 — Operator-burden eval primitive at per-cell dashboard surface | Production-time operator | ADR-D6 v1.1 §1.6; composition with ADR-D5 v1.3 §1.10 + ADR-F1 v1.2 |
| R-OD-07 — Local-first OTLP collector at solo-developer × local-development | Design-time operator | ADR-D6 v1.1 §1.7 + §1.1 (solo-developer × local-development cell) |
| R-OD-08 — Bridging-arc traversal preservation across observability dimensions | Design-time operator + Production-time operator | ADR-D6 v1.1 §1.1 + §1.2 + §1.3 + §1.4; ADR-D5 v1.3 §1.5.2; ADR-D2 v1.1 §1.6; ADD §5.3.1 |

### ADR scope

| ADR | Version | Role in axis |
|---|---|---|
| D6 | v1.1 | **Sole primary D-ADR.** Commits 9-cell matrix + unified span schema ingestion contract + sampling discipline + redaction discipline + cost-attribution dashboarding + operator-burden eval dashboard binding + local-first OTLP collector + multi-tenant tenant-isolation + cell-selection contract |
| F1 | v1.2 | Secondary (citation only) — `provider_discriminator` composition context at cross-family fallback chain advancement seam |
| F2 | v1.2 | Secondary (citation only) — state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` joins D6 trace storage via `idempotency_key`; declared at C-IS-05 |
| F3 | v1.1 | Secondary (citation only) — capability-floor (iv) observable lifecycle event set declared at C-CP-05 |
| F4 | v1.1 | Secondary (citation only) — `sandbox.*` F4-canonical attribute naming; OTLP collector reachability per tier per §Consequences (b)(iv) |
| F5 | v1.1 | Secondary (citation only) — secret-fetch structure-not-content audit composition declared at C-AS-08 |
| D1 | v1.1 | Secondary (citation only) — `engine.*` namespace source per §1.1.1; declared at C-CP-09 |
| D2 | v1.1 | Secondary (citation only) — `sandbox.*` namespace source per §1.7.1; cross-deployment sandbox-tier monotonicity per §1.6; declared at C-AS-15 |
| D3 | v1.1 | Secondary (citation only) — six Anthropic-primitive namespaces source per §1.8.1; cache-hit-rate alignment-floor source per §1.5; declared at C-AS-14 |
| D4 | v1.1 | Secondary (citation only) — `topology.*` + `subagent.*` namespaces source per §1.9 (under OD-RP-3.A Reading 1 — `topology.*` is the broader namespace; events `topology.fanout.opened` / `topology.fanout.closed` are the sub-tree under it per C-OD-05 §5.1 row 7); declared at C-CP-14 |
| D5 | v1.3 | Secondary (citation only) — `hitl.*` four distinct events source per §1.8; `audit.*` seven attributes source per §1.4.1; `validator.fail.*` three attributes source per §1.10.1; cross-deployment HITL monotonicity per §1.5.2; declared at C-CP-20 + C-CP-21 |

### Cross-axis citation substrate

| Cross-axis spec | Substrate seam exports consumed at session 4 | Composition shape |
|---|---|---|
| `Spec_Information_Substrate_v1.md` C-IS-10 | §10.1 (state-ledger entry shape export — D5/D6 rows); §10.2 (`idempotency_key` join export); §10.3 (hash-chain construction discipline export — D5 audit-ledger rows); §10.5 (JSONL event ledger format export — D6 OTLP collector boundary row) | D6 cost-attribution-per-span joins F2 state-ledger via `idempotency_key`; D6 OTLP collector boundary composes at the F2 JSONL event ledger at the within-turn streaming + across-turn durable trace storage seam per T-perm-2 D6-layer commitment |
| `Spec_Action_Surface_v1.md` C-AS-14 + C-AS-15 + C-AS-16 | C-AS-14 §14.2–14.7 (six Anthropic-primitive namespaces); C-AS-15 §15.2 (sandbox-bounded seven `sandbox.*` attributes); C-AS-16 §16.1 + §16.4 (export surface declarations) | D6 §1.2 unified span schema ingests `anthropic.*` + `mcp.*` + `skill.*` + `managed_agents.*` + `files.*` + `memory.*` + `sandbox.*` from Action Surface source contracts without re-declaration |
| `Spec_Control_Plane_v1.md` C-CP-03 + C-CP-05 + C-CP-09 + C-CP-14 + C-CP-20 + C-CP-21 + C-CP-24 | C-CP-03 §3.5 (`fallback.*` / `breaker.*` / `retry.*` namespace attributes); C-CP-05 §5.1 + §5.3 (eight F3 lifecycle event classes + `lease.*` namespace); C-CP-09 §9.1 (`engine.*` namespace); C-CP-14 §14.2 (`topology.*` + `subagent.*` namespaces); C-CP-20 §20.4 + §20.6 (`audit.*` + `hitl.*` namespaces); C-CP-21 §21.5 (`validator.fail.*` namespace); C-CP-24 §24.1 (substrate seam exports surface declaration) | D6 §1.2 unified span schema ingests eleven Control Plane span attribute namespaces from Control Plane source contracts without re-declaration; D6 §1.5 cost-attribution-per-span joins on `idempotency_key`; per-cell sampling discipline per D6 §1.3 |

### Persona-linkage substrate

| Persona anchor | Inheriting requirement(s) |
|---|---|
| §2 (bridging-arc — solo-developer → team-binding → multi-tenant-compliance traversal) | R-OD-01, R-OD-04, R-OD-07, R-OD-08 |
| §4 (99.9%+ completion SLO at tens-concurrent scale) | R-OD-03, R-OD-06 |
| §6 (per-class cost ceiling) | R-OD-03, R-OD-05 |
| §9 (local-development as design-time deployment target) | R-OD-01, R-OD-07 |
| §10.2 (cost-attribution-per-span as foundational primitive; production-time deployment surface persona-constrained-but-not-picked) | R-OD-01, R-OD-02, R-OD-05, R-OD-06 |
| §10.4 (compliance-readiness foundational primitives — hash-chained audit ledger, comprehensive observability, tenant isolation, encryption-at-rest, retention controls, secrets rotation) | R-OD-01, R-OD-02, R-OD-03, R-OD-04, R-OD-06, R-OD-08 |
| §11.4 (throughput rough order-of-magnitude open item) | R-OD-03 (cardinality budget per cell) |
| §11.10 (multi-tenant tenant-isolation specifics open item) | R-OD-04, R-OD-08 |

### Scope and out-of-scope

| In scope | Out of scope |
|---|---|
| Specification-grade contract precision for R-OD-01 through R-OD-08 (9-cell matrix; unified span schema with 15-namespace ingestion contract; sampling discipline; redaction discipline; cost-attribution formula; operator-burden eval primitive set; local-first OTLP collector contract; bridging-arc traversal preservation) | New architectural commitments (Phase 3 territory; back-flow to ADR revision if surfaced) |
| Citation-by-section to PRD requirements + ADR-D6 commitments + ADD synthesis paragraphs + cross-axis Information Substrate spec + cross-axis Action Surface spec + cross-axis Control Plane spec | ADR revision; ADD revision; PRD revision; session-1/2/3 spec revision |
| Persona-linkage trace preservation from PRD requirements | F2-12 closure (parallel `council-orchestrator` C7+C9 session territory); D1 v1.2 closure half (Control Plane session-3 territory) |
| Substrate seam exports surface (C-OD-23) for session 5 composition document and Phase 6+ implementation planning | Cross-axis composition beyond session 5 entry surfaces (deferred to optional session 5 per §2.4 at session 4 close) |
| §[carry-forwards] inheritance from PRD §[carry-forwards] + session-1/2/3 spec §[carry-forwards] | Span re-emission semantics under engine replay (deferred per F2-12); trace-ingestion dedup composition at D6 v1.2 closure |
| **F2-12 active engagement at R-OD-05 satisfying contract (C-OD-14)** — affected-contract notation discipline applies per session prompt §5.4 [CF-1] authoring approach (iii) | Class-3 finding revision (P5-CK territory; aggregate P5-CK at full Phase 5 close per OD-5-4.A) |

---

## §1 C-OD-01 — 9-cell deployment-surface × persona-tier matrix

**Contract surface.** 2D matrix with one excluded cell; per-cell tuple of (backend class, provider candidates, trace storage tier, collector placement, redaction class, retention class).

**PRD requirement(s) satisfied.** R-OD-01 (per-cell observability backend committed at deployment-binding time).

**ADR commitment(s) honored.** ADR-D6 v1.1 §Decision (nine-component observability specification); ADR-D6 v1.1 §1.1 9-cell deployment-surface × persona-tier matrix.

**Persona linkage.** Persona §9 (design-time forced to local-development); §2 (bridging-arc traversal); §10.2 (production-time deployment surface persona-constrained-but-not-picked); §10.4 (compliance-readiness).

**Specification content.**

### §1.1 Matrix shape

```
                 │ local-development │ self-hosted-server │ managed-cloud
─────────────────┼───────────────────┼────────────────────┼──────────────
solo-developer   │       cell-1      │      cell-2        │     cell-3
team-binding     │       cell-4      │      cell-5        │     cell-6
multi-tenant-    │   ❌ EXCLUDED      │      cell-7        │     cell-8
compliance       │                   │                    │
```

Nine logical cells; one EXCLUDED (multi-tenant-compliance × local-development) per §1.4. Eight active cells.

### §1.2 Per-cell entry schema

Each active cell carries a six-field entry:

| Field | Value space | Bound by |
|---|---|---|
| **Backend class** | enum ∈ `{OTel-only, dedicated LLM-obs platform (single-node), dedicated LLM-obs platform (multi-node), cloud-native LLM-obs platform, OTel-to-vendor, self-hosted multi-tenant LLM-obs platform, vendor-managed multi-tenant LLM-obs OR cloud-native managed agent runtime}` | C-OD-02 |
| **Provider candidates** | enum (bounded per cell from candidate-witness column) | C-OD-02 + C-OD-03 |
| **Trace storage tier** | enum ∈ `{Tier-3 (sqlite ring-buffer), Tier-4 (backend-managed durable storage), Tier-4 + Tier-5 (audit ledger hash-chained), Tier-4 (vendor-bound durable storage)}` per C3 five-tier durability model | ADR-D5 v1.3 §1.4 per-persona-tier ledger cryptographic shape |
| **Collector placement** | enum ∈ `{in-process, sidecar, vendor-pipeline, sidecar with per-tenant routing, per-tenant collector instance, vendor-managed collector}` | C-OD-20 + ADR-F4 v1.1 §Consequences (b)(iv) |
| **Redaction class** | enum ∈ `{operator-self-redact, redaction-processor at OTLP collector boundary, pre-collector redaction (eval-grade pipeline)}` | C-OD-12 + C-OD-13 |
| **Retention class** | enum ∈ `{operator-tunable, 7–30 days typical, 30 days–1 year typical, compliance-attestation-bound, vendor-bound per agreement}` | Persona §10.4 |

### §1.3 Per-cell entries (eight active cells)

| persona-tier ↓ \ deployment-surface → | local-development | self-hosted-server | managed-cloud |
|---|---|---|---|
| **solo-developer** | (OTel-only, in-process otelcol-contrib + sqlite ring-buffer, Tier-3, in-process, operator-self-redact, operator-tunable) | (dedicated LLM-obs single-node, Tier-4, sidecar OR vendor-pipeline, operator-self-redact, operator-tunable) | (cloud-native LLM-obs, Tier-4, vendor-pipeline, operator-self-redact, vendor-bound) |
| **team-binding** | (OTel-only-or-single-node-LLM-obs, Tier-3 OR Tier-4, in-process OR sidecar, redaction-processor at OTLP collector boundary, 7–30 days typical) | (dedicated LLM-obs multi-node OR OTel-to-vendor, Tier-4 + Tier-5 audit ledger hash-chained, sidecar OR collector-as-DaemonSet, redaction-processor, 30 days–1 year typical) | (cloud-native LLM-obs, Tier-4, vendor-pipeline, redaction-processor at OTLP collector boundary, vendor-bound per agreement) |
| **multi-tenant-compliance** | ❌ **EXCLUDED** (see §1.4) | (self-hosted multi-tenant LLM-obs, Tier-4 partitioned + Tier-5 per-tenant audit ledger hash-chained + cryptographic signature, sidecar with per-tenant routing OR per-tenant collector instance, pre-collector redaction (eval-grade pipeline), compliance-attestation-bound) | (vendor-managed multi-tenant LLM-obs OR cloud-native managed agent runtime, Tier-4 vendor-bound + Tier-5 vendor-managed audit ledger, vendor-managed collector, pre-collector redaction at SDK / wrapper boundary, compliance-attestation-bound per vendor SLA) |

### §1.4 EXCLUDED cell rationale (multi-tenant-compliance × local-development)

The multi-tenant-compliance × local-development cell is **structurally excluded**, not configurationally absent. Per Persona §10.4 compliance-readiness foundational primitives (hash-chained audit ledger; granular access controls; encryption-at-rest; retention controls; tenant isolation; secrets rotation; comprehensive observability — *foundational, not bolt-on*), single-developer-machine deployment cannot foundationally satisfy multi-tenant tenant isolation (no second tenant exists), encryption-at-rest with vendor-managed key custody, or retention controls under attestation-bound retention policy. The exclusion is outside the harness's persona-traversal envelope; bridging-arc transitions skip this cell per C-OD-22.

### §1.5 Cell-identification invariant

| Invariant | Contract |
|---|---|
| **Active cell identifiability** | At deployment-binding time, exactly one cell is the active cell of the matrix; the six-field tuple is fully populated at the active cell |
| **Excluded-cell binding rejection** | A deployment-binding attempt targeting the excluded cell (multi-tenant-compliance × local-development) is structurally rejected at the bridging-arc transition surface per C-OD-22 |
| **Cell-transition observable** | When the operator transitions the harness across cells, the cell-transition is observable at the deployment-binding surface — both before-cell and after-cell tuples are recorded per C-OD-22 bridging-arc traversal preservation |

**Deferred to implementation discretion.** Specific cell-identification API surface (the manifest declaration shape, the configuration file format, the runtime cell-binding handshake); specific cell-transition state-machine implementation; specific cell-binding persistence mechanism beyond the harness manifest residence per `Spec_Information_Substrate_v1.md` C-IS-10 §10.4.

---

## §2 C-OD-02 — Per-cell observability backend class commitment + provider candidate witness columns

**Contract surface.** Per-cell backend class enumeration + per-cell provider candidate witness columns (deployment-binding-time-bounded candidate space).

**PRD requirement(s) satisfied.** R-OD-01 (per-cell observability backend committed at deployment-binding time).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.1 (per-cell backend class + provider candidates witness columns); ADR-D6 v1.1 §1.9 (cell-selection contract — backend class committed at D6 per cell).

**Persona linkage.** Persona §10.2 (production-time deployment surface persona-constrained-but-not-picked); §10.4 (compliance-readiness — comprehensive observability).

**Specification content.**

### §2.1 Per-cell backend class

The backend class field at each cell of C-OD-01 §1.3 commits the observability backend's architectural class. Eight cells; seven distinct classes (cell-4 admits a class disjunction at the design-time-flexible row):

| Cell | Backend class |
|---|---|
| solo-developer × local-development (cell-1) | OTel-only |
| solo-developer × self-hosted-server (cell-2) | Dedicated LLM-obs platform (single-node) |
| solo-developer × managed-cloud (cell-3) | Cloud-native LLM-obs platform |
| team-binding × local-development (cell-4) | OTel-only OR Dedicated LLM-obs platform (single-node) |
| team-binding × self-hosted-server (cell-5) | Dedicated LLM-obs platform (multi-node) OR OTel-to-vendor |
| team-binding × managed-cloud (cell-6) | Cloud-native LLM-obs platform |
| multi-tenant-compliance × self-hosted-server (cell-7) | Self-hosted multi-tenant LLM-obs platform |
| multi-tenant-compliance × managed-cloud (cell-8) | Vendor-managed multi-tenant LLM-obs OR cloud-native managed agent runtime |

### §2.2 Per-cell provider candidate witness columns

Each cell's backend class is paired with a candidate witness column — the bounded set of provider candidates committed at D6 v1.1 §1.1 cell-entry witness columns. Selection within the witness column is deferred per C-OD-03; selection outside the witness column is structurally rejected.

| Cell | Provider candidate witness column |
|---|---|
| cell-1 | otelcol-contrib + sqlite ring-buffer (in-process) |
| cell-2 | Langfuse self-hosted single-node, Arize Phoenix OSS PostgreSQL single-node, Helicone HTTP-proxy |
| cell-3 | Langfuse Cloud free-tier, Arize Phoenix OSS at managed-cloud, Datadog free-tier, Sentry/Seer hobbyist tier |
| cell-4 | otelcol-contrib + sqlite ring-buffer (in-process) OR Langfuse self-hosted single-node |
| cell-5 | Langfuse self-hosted multi-node ClickHouse, Arize AX self-hosted, Helicone self-hosted (ClickHouse + Kafka), Datadog self-hosted equivalent, Sentry self-hosted, Grafana stack (OTel-to-vendor) |
| cell-6 | Langfuse Cloud paid tier, Arize AX SaaS, LangSmith, Datadog LLM Observability, Sentry/Seer |
| cell-7 | Langfuse self-hosted multi-tenant + per-tenant ClickHouse partitioning, Arize AX self-hosted multi-tenant + per-tenant PostgreSQL schema separation |
| cell-8 | AWS Bedrock AgentCore Runtime, Google Vertex Agent Engine, LangSmith Enterprise (customer VPC), Langfuse Cloud Enterprise |

### §2.3 Cell-class commitment invariant

| Invariant | Contract |
|---|---|
| **Backend class committed at D6** | Per-cell backend class is committed at this contract; deployment-binding-time selection cannot select a backend class outside the per-cell commitment |
| **Provider candidate bounded by witness column** | Provider selection at deployment-binding time × persona-tier-binding time MUST select a candidate from the per-cell witness column per §2.2; out-of-witness selection is structurally rejected |
| **Disciplines inviolable by candidate selection** | Selection of any candidate within the per-cell witness column does NOT permit violation of sampling discipline (C-OD-09), redaction discipline (C-OD-12 + C-OD-13), trace storage tier commitment (C-OD-01 §1.3), or collector placement commitment (C-OD-20) |

**Deferred to implementation discretion.** Specific provider selection mechanism (operator-tunable configuration vs. environment binding vs. wizard); specific provider-API-binding implementation per candidate; specific per-tier reachability validation mechanism (mode-specific health-check); specific candidate-rotation cadence if cell-bound candidates are deprecated upstream.

---

## §3 C-OD-03 — Cell-selection contract — deferred candidate-within-class

**Contract surface.** Deferral signature — what is committed at D6 per cell vs what is deferred to deployment-binding time.

**PRD requirement(s) satisfied.** R-OD-01 (per-cell observability backend committed at deployment-binding time).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.9 (cell-selection contract); ADR-D6 v1.1 §Consequences (b) (per-cell deployment-surface-time × persona-tier-binding-time selection contract).

**Persona linkage.** Persona §10.2 (production-time deployment surface persona-constrained-but-not-picked at PRD time).

**Specification content.**

### §3.1 What is committed at D6 per cell

| Committed surface | Contract reference |
|---|---|
| Per-cell backend class | C-OD-02 §2.1 |
| Per-cell provider candidate witness column | C-OD-02 §2.2 |
| Per-cell trace storage tier (C3 five-tier durability) | C-OD-01 §1.3 |
| Per-cell collector placement | C-OD-20 |
| Per-cell redaction class | C-OD-12 + C-OD-13 |
| Per-cell retention class | C-OD-01 §1.3 |
| Sampling discipline (head-based-dev / tail-based-prod + always-sampled set + base-rate set + cardinality budget) | C-OD-09 + C-OD-10 + C-OD-11 |
| Redaction discipline (default-off content + default-on structure + per-persona-tier override gradient) | C-OD-12 + C-OD-13 |
| Cost-attribution-per-span formula | C-OD-14 |
| Operator-burden eval primitive set | C-OD-17 |
| Unified span schema (15 specialization-layer namespace ingestion contract) | C-OD-05 |
| Bridging-arc traversal preservation invariants | C-OD-22 |

### §3.2 What is deferred to deployment-binding time × persona-tier-binding time

| Deferred surface | Bound by |
|---|---|
| Specific provider candidate-within-class | Per-cell witness column per C-OD-02 §2.2 |
| Specific OTLP exporter configuration per candidate | Candidate-specific API binding |
| Specific retention policy parameters within retention-class envelope | Per-cell retention class per C-OD-01 §1.3 (e.g., "30 days–1 year typical" admits operator-tunable selection within range) |
| Specific cardinality budget numeric thresholds | Per-cell sampling discipline per C-OD-11; tightens downstream of Persona §11.4 closure |
| Specific multi-tenant tenant-isolation primitive (partition vs schema vs vendor-namespace) | Per-cell witness column per C-OD-02 §2.2; refined at Persona §11.10 closure |

### §3.3 Deferral boundary invariant

The deferred surface cannot violate any committed surface. Concretely:

| Boundary | Contract |
|---|---|
| **Backend class escape** | Deployment-binding-time selection cannot escape the per-cell committed class |
| **Witness column escape** | Deployment-binding-time provider selection cannot escape the per-cell witness column |
| **Discipline violation** | Selection cannot violate sampling / redaction / cost-attribution / cardinality / collector-placement / retention-class disciplines |
| **Tier downgrade** | Per-cell trace storage tier cannot be downgraded at deployment-binding time (e.g., a cell committed at Tier-4 + Tier-5 cannot be reduced to Tier-4-only) |

**Deferred to implementation discretion.** Specific deployment-binding-time configuration format (TOML / YAML / JSON / environment variables); specific operator-facing selection UX (config-file template vs. CLI flag vs. wizard); specific selection-validation mechanism (static schema vs. runtime probe vs. compile-time emission); specific candidate-deprecation handling protocol if a per-cell candidate is sunset upstream.

---

## §4 C-OD-04 — Unified span schema base layer (OTel GenAI semconv 1.41.0)

**Contract surface.** Base-layer span name format + operations enum + required / recommended / opt-in attribute tiers + base metric.

**PRD requirement(s) satisfied.** R-OD-02 (unified span schema with 15 specialization-layer namespaces — base layer half).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.2 base layer block (OTel GenAI semconv 1.41.0 [HIGH] as cross-vendor floor; preserved verbatim per v1.1 change-note).

**Persona linkage.** Persona §10.4 (compliance-readiness — comprehensive observability composed on a cross-vendor stable anchor).

**Specification content.**

### §4.1 Span name format

```
{gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}
```

Per OTel GenAI semconv 1.41.0 [HIGH] canonical span name format.

### §4.2 Operations enum

`gen_ai.operation.name` ∈ `{chat, text_completion, embeddings, generate_content, create_agent, invoke_agent, execute_tool}`

### §4.3 Attribute tiers

| Tier | Attributes | Emission posture |
|---|---|---|
| **Required (Stable)** | `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model` | Always emitted |
| **Recommended (Development)** | `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.response.finish_reasons`, `server.address`, `server.port`, `gen_ai.conversation.id` | Emitted unless cardinality-safe-attribute discipline excludes (per C-OD-11) |
| **Opt-In content** | `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.system_instructions`, `gen_ai.tool.definitions`, `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result`, `gen_ai.retrieval.documents`, `gen_ai.retrieval.query.text` | Default-off per C-OD-12 (redaction discipline); per-persona-tier override gradient per C-OD-13 |

### §4.4 Hierarchy correlation

`gen_ai.conversation.id` is the correlation key for `invoke_agent` / `chat` / `execute_tool` hierarchy per OTel GenAI Agent Spans. Cardinality-safe-attribute discipline (C-OD-11) restricts this attribute to span attributes only — NEVER metric dimension.

### §4.5 Base metric

`gen_ai.client.operation.duration` (histogram) with cardinality control per C-OD-11.

**Deferred to implementation discretion.** Specific OTel SDK binding per language ecosystem (opentelemetry-instrumentation-anthropic / openinference-instrumentation-* / vendor SDK); specific span exporter wiring; specific instrumentation library version pinning per language; specific cross-SDK conformance test harness.

---

## §5 C-OD-05 — 15 specialization-layer namespace ingestion contract

**Contract surface.** 15-row specialization namespace map; each row commits namespace, source declaration site, attribute count, ingestion posture.

**PRD requirement(s) satisfied.** R-OD-02 (unified span schema with 15 specialization-layer namespaces — specialization-layer half).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.2 specialization-layer namespace map (lines 104–120; 15 rows ingested verbatim from source D-ADRs and substrate).

**Cross-axis citation.** `Spec_Action_Surface_v1.md` C-AS-14 §14.1 (six Anthropic-primitive namespace declarations); C-AS-14 §14.2–§14.7 (per-namespace attribute tables); C-AS-15 §15.2 (`sandbox.*` seven attributes); C-AS-16 §16.1 + §16.4 (export surfaces). `Spec_Control_Plane_v1.md` C-CP-09 §9.1 (`engine.*` namespace); C-CP-14 §14.2 (`topology.*` + `subagent.*` namespaces); C-CP-20 §20.4 + §20.6 (`audit.*` + `hitl.*` namespaces); C-CP-21 §21.5 (`validator.fail.*` namespace); C-CP-24 §24.1 (substrate seam exports surface declaration). `Spec_Information_Substrate_v1.md` C-IS-05 (state-ledger entry shape — F2 `idempotency_key` join referenced at `engine.*` row).

**Persona linkage.** Persona §10.2 (cost-attribution-per-span composed on stable span schema); §10.4 (compliance-readiness — comprehensive observability requires stable cross-axis ingestion).

**Specification content.**

### §5.1 Namespace map (15 rows)

| # | Namespace | Source declaration site | Attribute count | Cross-axis spec citation | Ingestion posture |
|---|---|---|---|---|---|
| 1 | `anthropic.*` | ADR-D3 v1.1 §1.8.1; declared at `Spec_Action_Surface_v1.md` C-AS-14 §14.2 | 10 | C-AS-14 §14.2 | Ingest verbatim |
| 2 | `mcp.*` | ADR-D3 v1.1 §1.8.1; declared at C-AS-14 §14.3 | 7 | C-AS-14 §14.3 | Ingest verbatim |
| 3 | `skill.*` | ADR-D3 v1.1 §1.8.1; declared at C-AS-14 §14.4 | 6 | C-AS-14 §14.4 | Ingest verbatim |
| 4 | `managed_agents.*` | ADR-D3 v1.1 §1.8.1; declared at C-AS-14 §14.5 | 3 | C-AS-14 §14.5 | Ingest verbatim |
| 5 | `sandbox.*` | ADR-D2 v1.1 §1.7.1 + ADR-F4 v1.1 §Consequences (a); declared at C-AS-15 §15.2 | 7 | C-AS-15 §15.2 | Ingest verbatim under F4-canonical-naming-honored-at-source-D-ADR rule |
| 6 | `hitl.*` | ADR-D5 v1.3 §1.8 (four distinct events: `hitl.gate.evaluated`, `hitl.invocation.opened`, `hitl.invocation.responded`, `hitl.invocation.timed_out`); declared at C-CP-20 §20.6 | 11 attributes across 4 span names | C-CP-20 §20.6 | Ingest verbatim per F2-05 hitl.* sub-finding closure Option (i) — mirror source declaration |
| 7 | `topology.*` | ADR-D4 v1.1 §1.9; declared at C-CP-14 §14.2 (broader namespace under OD-RP-3.A Reading 1; events `topology.fanout.opened` / `topology.fanout.closed` live as a sub-tree under `topology.*` per F-CP-02 closure) | included in C-CP-14 §14.2 topology.* attribute set | C-CP-14 §14.2 | Ingest verbatim |
| 8 | `subagent.*` | ADR-D4 v1.1 §1.9; declared at C-CP-14 §14.2 | 7 | C-CP-14 §14.2 | Ingest verbatim |
| 9 | `engine.*` | ADR-D1 v1.1 §1.1.1; declared at C-CP-09 §9.1 | 3 (`engine.class`, `engine.event_history.tier`, `engine.event.id`) | C-CP-09 §9.1; F2 join via `idempotency_key` per C-IS-05 + C-IS-10 §10.2 | Ingest verbatim |
| 10 | `audit.*` | ADR-D5 v1.3 §1.4.1; declared at C-CP-20 §20.4 | 7 (per-persona-tier emission discipline per D5 v1.3 §1.4.1) | C-CP-20 §20.4 | Ingest verbatim |
| 11 | `validator.fail.*` | ADR-D5 v1.3 §1.10.1 + `c5-validation-contract` SKILL.md s14 §7.5(d) locked five-class taxonomy; declared at C-CP-21 §21.5 | 3 (`validator.fail.class`, `validator.fail.cause_attribution`, `validator.fail.permanence`) | C-CP-21 §21.5 | Ingest verbatim |
| 12 | `files.*` | ADR-D3 v1.1 §1.8.1; declared at C-AS-14 §14.6 | 8 | C-AS-14 §14.6 | Ingest verbatim |
| 13 | `memory.*` | ADR-D3 v1.1 §1.8.1; declared at C-AS-14 §14.7 | 6 | C-AS-14 §14.7 | Ingest verbatim |
| 14 | `harness.breaker.*` | `c9-reliability-recovery` SKILL.md (substrate-anchored citation per Workflow v1.3 §2.3.3.1 clause (iii) substrate-anchored citation discipline for synthesis-D-ADR-introduced namespace); declared at ADR-D6 v1.1 §1.2.1 | 7 | C-OD-07 (declared at this spec per F2-16 closure) | Declare-and-ingest (synthesis-D-ADR namespace; canonical at D6 §1.2.1) |
| 15 | `provider_discriminator` | `c7-observability` SKILL.md cross-family discipline (primary anchor per F2-10 closure); composition context at ADR-F1 v1.2 §Decision | 1 (single attribute — cross-family fallback chain family tag) | F1 v1.2 composition context | Ingest from substrate per F2-10 citation refinement |

### §5.2 Ingestion-posture invariants

| Invariant | Contract |
|---|---|
| **Source-as-authoritative-declarer** | For each namespace whose source row commits a cross-axis spec citation (rows 1–13), D6 ingestion at this spec MUST NOT re-declare attribute names — the source contract (C-AS-14 / C-AS-15 / C-CP-09 / C-CP-14 / C-CP-20 / C-CP-21) is canonical |
| **Verbatim attribute ingestion** | When the unified span schema emits attributes within a namespace, attribute names match the source declaration verbatim (no rename; no transformation) |
| **Pattern P1 mechanical-alignment discipline** | Per the P3c-CK Iteration 1 systemic Pattern P1 closure, attribute-name drift between this contract and source declarations is structurally rejected; namespace map mechanical alignment is verified at C-OD-23 substrate seam exports |
| **Forward-compatibility** | When a source D-ADR revises (e.g., D1 v1.2 closure at F2-12 expands the `engine.*` namespace), this contract's namespace map row is additive-forward-compatible — new attributes within an existing namespace are absorbed without namespace-map row restructure |

### §5.3 F2-12 forward-compatibility note

Per session prompt §5.4 [CF-1] and PRD §[carry-forwards] [CF-1], the `engine.*` namespace (row 9) is forward-compatible for the D1 v1.2 closure of F2-12 — span re-emission semantics under engine replay may extend the `engine.*` attribute set with additional attributes (e.g., `engine.replay.kind`, `engine.replay.idempotency_key_origin`). Forward compatibility is by structure (additive attribute discipline); the namespace map row at §5.1 is preserved at D6 v1.1 baseline and accepts forward additions without restructure.

**Deferred to implementation discretion.** Specific cross-SDK namespace conformance test harness; specific namespace-version-migration protocol if a source D-ADR introduces breaking changes (deemed out of scope at v1; assumed additive at source D-ADR revisions); specific runtime namespace-presence validation mechanism (static schema vs. runtime probe).

---

## §6 C-OD-06 — F3 capability-floor (iv) lifecycle event-to-span-event mapping

**Contract surface.** Eight-element lifecycle event class → span-event-or-attribute-name mapping with parent-span placement discipline.

**PRD requirement(s) satisfied.** R-OD-02 (unified span schema — F3 capability-floor (iv) lifecycle event base ingestion contract half).

**ADR commitment(s) honored.** ADR-F3 v1.1 capability-floor (iv) — observable lifecycle exposing eight event classes; ADR-D6 v1.1 §1.2 F3 capability-floor (iv) lifecycle event set mapping block (preserved verbatim per v1.1 change-note).

**Cross-axis citation.** `Spec_Control_Plane_v1.md` C-CP-05 §5.1 (eight F3 lifecycle event classes — primary declaration site); C-CP-05 §5.3 (`lease.*` namespace); C-CP-03 §3.5 (`fallback.*` / `breaker.*` / `retry.*` namespaces).

**Persona linkage.** Persona §4 (99.9% SLO — observable lifecycle is the substrate for reliability-eval primitives at C-OD-17); §10.4 (compliance-readiness — comprehensive observability requires complete lifecycle event coverage).

**Specification content.**

### §6.1 Lifecycle event mapping table

The F3 v1.1 capability-floor (iv) observable lifecycle (eight event classes — `workflow.start`, `step.boundary`, `fallback.triggered`, `retry.attempt`, `breaker.tripped`, `lease.acquired`, `lease.released`, `workflow.resumed`) maps to span-event or span-attribute placement within the parent span hierarchy:

| Lifecycle event class | Span-placement form | Attribute namespace | Sampling posture |
|---|---|---|---|
| `workflow.start` | Span attribute on root span | `engine.*` (per C-CP-09 §9.1) | Per root span sampling (inherits) |
| `step.boundary` | Span event on parent | (no dedicated namespace; inherits parent attribute set) | Per parent sampling |
| `fallback.triggered` | Span event on parent + new sibling fallback span | `fallback.*` (per C-CP-03 §3.5) | **Always-sampled** per C-OD-09 |
| `retry.attempt` | Span event on parent + new sibling retry span | `retry.*` (per C-CP-03 §3.5) | Base-rate at 1st attempt; always-sampled at 2nd onward per C-CP-03 §3.5 |
| `breaker.tripped` | Span event on parent | `harness.breaker.*` (per C-OD-07 §7.1) | **Always-sampled** per C-OD-09 |
| `lease.acquired` | Span event on parent | `lease.*` (per C-CP-05 §5.3) | Base-rate per C-CP-05 §5.4 |
| `lease.released` | Span event on parent | `lease.*` (per C-CP-05 §5.3) | Base-rate per C-CP-05 §5.4 |
| `workflow.resumed` | Span attribute on root span (post-resumption) | `engine.*` (per C-CP-09 §9.1) | Always-sampled per C-CP-05 §5.4 |

### §6.2 Additive composition with namespace specialization layers

A single span carries multiple event types from multiple namespaces without namespace collision. Example: a `chat` operation span that issues a `tool.call` to an MCP primitive in a sandbox-tier-3 environment carries `gen_ai.*`, `mcp.*`, `sandbox.*`, and F3 lifecycle attributes simultaneously without conflict.

| Composition property | Contract |
|---|---|
| **Event-class additivity** | Multiple lifecycle events MAY co-occur on a single span (e.g., `retry.attempt` + `fallback.triggered` on the same parent) |
| **Namespace independence** | Lifecycle event attributes (`fallback.*` / `breaker.*` / `retry.*` / `lease.*`) compose independently of specialization-layer namespaces (`anthropic.*` / `mcp.*` / `sandbox.*` / etc.) |
| **Parent-attachment discipline** | Span-event placement attaches to the parent span; sibling-span placement (`fallback.triggered` + sibling fallback span; `retry.attempt` + sibling retry span) preserves the parent's `gen_ai.conversation.id` correlation per C-OD-04 §4.4 |

### §6.3 F2-12 deferral acknowledgement at retry.attempt

Per session prompt §5.4 [CF-1], the `retry.attempt` sibling-span discipline is part of F2-12 deferred scope — specifically, whether `retry.attempt` emits AND a new sibling retry span (current commitment at this contract) or whether replay-trace-emission semantics under engine replay change the sibling-span emission posture. The v1 commitment is: `retry.attempt` event on parent + new sibling retry span per C-CP-03 §3.5; D1 v1.2 closure may revise.

**Deferred to implementation discretion.** Specific span-event emission API per OTel SDK; specific sibling-span parent-correlation mechanism (W3C trace context propagation vs. baggage); specific retry-span lifecycle (open on attempt; close on attempt resolution); specific replay-trace-emission semantics under engine replay (F2-12 deferred).

---

## §7 C-OD-07 — `harness.breaker.*` seven-attribute breaker-trip event schema

**Contract surface.** Seven-attribute schema declared at D6 §1.2.1 (synthesis-D-ADR-introduced namespace; substrate-anchored at `c9-reliability-recovery` SKILL.md).

**PRD requirement(s) satisfied.** R-OD-02 (unified span schema — `harness.breaker.*` namespace declaration half); R-OD-03 (sampling discipline — always-sampled at `breaker.tripped`).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.2.1 (seven-attribute breaker-trip event schema; substrate-anchored citation per Workflow v1.3 §2.3.3.1 clause (iii)); ADR-D6 v1.1 §1.3 (always-sampled `breaker.tripped` event).

**Cross-axis citation.** `Spec_Control_Plane_v1.md` C-CP-03 §3.5 (`breaker.*` namespace lifecycle event semantics; C9↔C10 breaker-trip subscription contract).

**Persona linkage.** Persona §4 (99.9% SLO — breaker-trip is reliability-critical); §10.4 (compliance-readiness — breaker-trip is tamper-evidence-relevant under C9↔C10 audit subscription contract).

**Specification content.**

### §7.1 Seven-attribute schema

| Attribute | Type | Source | Definition |
|---|---|---|---|
| `harness.breaker.scope` | enum string ∈ `{per_model, per_provider}` | `c9-reliability-recovery` SKILL.md (s12 §7.7) | The breaker scope |
| `harness.breaker.from_state` | enum string ∈ `{closed, open, half_open}` | `c9-reliability-recovery` SKILL.md (s12 §7.7) | Source state |
| `harness.breaker.to_state` | enum string ∈ `{closed, open, half_open}` | `c9-reliability-recovery` SKILL.md (s12 §7.7) | Destination state |
| `harness.breaker.trigger_count` | int | `c9-reliability-recovery` SKILL.md (s12 §7.7) | Consecutive failures that tripped the breaker (when `from=closed`, `to=open`) |
| `harness.breaker.permanent_fail_repeats` | bool | `c9-reliability-recovery` SKILL.md (s12 §7.7) | Whether this trip is from repeated C5 permanent-fail-exits — the C10 gating signal |
| `harness.breaker.tool_id` | string | `c9-reliability-recovery` SKILL.md (s13 §4.10 (e)) | Specific tool ID the failures correlate with (when scope is per-model and failures correlate with a specific tool) |
| `harness.breaker.model_version` | string | `c9-reliability-recovery` SKILL.md (s13 §4.10 (e)) | Specific model version (composes with judge-drift discipline per s11 §4.1) |

### §7.2 Quality-of-emission invariants

| Invariant | Contract |
|---|---|
| **Trip-time population** | All seven attributes populate at trip-time |
| **Immutability** | Attribute values are immutable post-emission per hash-chain ledger composition |
| **All-seven-required-on-emission** | Emitting `breaker.tripped` with any of the seven attributes missing is a quality failure (FM-Q per substrate) |
| **Always-sampled** | `breaker.tripped` event MUST be sampled at head=1.0 per C-OD-09 |

### §7.3 C9↔C10 breaker-trip subscription contract reference

The breaker-trip-as-gating-signal subscription is operator-tunable per-policy-opt-in via `breaker_subscription_per_gate` per `c10-action-safety` SKILL.md substrate. Four gating-response options: `gate_combination` / `escalate_to_hitl` / `informational` / `dynamic_tighten`. The subscription is NOT a span attribute (it is a C10-side policy); the seven-attribute schema at §7.1 is the C7-side substrate over which C10 subscribes.

**Deferred to implementation discretion.** Specific OTel/OTLP span emission implementation for the `breaker.tripped` event; specific attribute-validation mechanism at emission time (compile-time vs. runtime); specific breaker-state-machine implementation (in-process vs. distributed-state); specific subscription wiring between C10 gate policy and C7 span emission (composes at Phase 6+ implementation).

---

## §8 C-OD-08 — Namespace collision discipline

**Contract surface.** Cross-namespace attribute precedence rule — what happens when a harness-specific namespace concept overlaps with an OTel GenAI semconv 1.41.0 attribute.

**PRD requirement(s) satisfied.** R-OD-02 (unified span schema — namespace collision invariant half).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.2 Namespace collision discipline paragraph (preserved verbatim per v1.1 change-note).

**Persona linkage.** Persona §10.4 (compliance-readiness — cross-vendor stable anchor preserved via OTel-GenAI-precedence rule).

**Specification content.**

### §8.1 Collision precedence rule

| Rule | Contract |
|---|---|
| **No-override invariant** | No additive namespace layer overrides or shadows an OTel GenAI semconv 1.41.0 attribute |
| **OTel-canonical-value rule** | When a harness-specific concept overlaps with an OTel-defined concept, the OTel attribute carries the cross-vendor canonical value; the harness-specific attribute carries the specialization |
| **No-rename rule** | Specialization namespaces MUST NOT rename OTel-defined attributes; specialization namespaces extend additively under their own prefix |

### §8.2 Canonical example — input token attribution

| Attribute | Carrier semantic | Per |
|---|---|---|
| `gen_ai.usage.input_tokens` | Total input tokens for the inference call (cross-vendor canonical) | OTel GenAI semconv 1.41.0 |
| `anthropic.cache_creation_input_tokens` | Cache-tier breakdown — tokens charged at 1.25× rate (5-min TTL creation) | ADR-D3 v1.1 §1.8.1 per C-AS-14 §14.2 |
| `anthropic.cache_read_input_tokens` | Cache-tier breakdown — tokens charged at 0.10× rate (cache hit) | ADR-D3 v1.1 §1.8.1 per C-AS-14 §14.2 |

The cache-tier breakdown sums to `gen_ai.usage.input_tokens` minus uncached input tokens; the OTel total is canonical.

### §8.3 Cross-namespace cardinality discipline

Specialization-layer namespaces MUST respect the cardinality-safe-attribute discipline per C-OD-11. High-cardinality attributes within a specialization namespace (e.g., `mcp.primitive.signature.sha256` per-primitive hash; `skill.version_sha` per-Skill-version git hash) are span attributes only — NEVER metric dimensions.

**Deferred to implementation discretion.** Specific runtime cross-namespace validation mechanism; specific attribute-namespace prefix enforcement at OTel SDK boundary; specific OTel-attribute-set version-pinning convention per language ecosystem.

---

## §9 C-OD-09 — Sampling discipline: head-based-dev / tail-based-prod + always-sampled set

**Contract surface.** Per-deployment-surface sampling mode + always-sampled exception set (head=1.0 across all cells).

**PRD requirement(s) satisfied.** R-OD-03 (sampling discipline with always-sampled exceptions).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.3 sampling discipline (head-based-dev / tail-based-prod with always-sampled exceptions; preserved per v1.1 change-note with `mcp.tool.call` carve-out added per F2-09 closure).

**Cross-axis citation.** `Spec_Action_Surface_v1.md` C-AS-14 §14.8 (audit-floor commitments — `mcp.tool.call` head=1.0 with tail-keep-on-trust-tier-floor-violations; `managed_agents.runtime` head=1.0; `files.operation` mutation head=1.0; `memory.operation` mutation head=1.0); C-AS-15 §15.4 (`sandbox.violation` + `sandbox.tier_escalation` always-sampled); `Spec_Control_Plane_v1.md` C-CP-03 §3.5 (`fallback.triggered` always-sampled; `breaker.tripped` always-sampled); C-CP-14 §14.3 (`topology.fanout.opened` / `topology.fanout.closed` / `subagent.span.closed` always-sampled); C-CP-20 §20.6 (all HITL spans always-sampled); C-CP-21 §21.6 (`validator.fail.*` always-sampled at `permanence=permanent`).

**Persona linkage.** Persona §4 (99.9% SLO — reliability-critical events must always sample); §10.4 (compliance-readiness — tamper-evidence-relevant events must always sample).

**Specification content.**

### §9.1 Per-deployment-surface sampling mode

| Deployment surface | Sampling mode |
|---|---|
| local-development (design-time) | **Head-based sampling** — sampling decision at span creation; cardinality budget tunable per session at the in-process collector |
| self-hosted-server + managed-cloud (production-time) | **Tail-based sampling** — sampling decision at trace completion; tail-keep-on-classification preserves failure-trees per C-OD-10 |

### §9.2 Always-sampled exception set (head=1.0 across all cells)

| Event class | Source declaration | Rationale |
|---|---|---|
| `sandbox.violation` | C-AS-15 §15.4 (D2 v1.1 §1.7.1) | Security-critical |
| `sandbox.tier_escalation` | C-AS-15 §15.4 (D2 v1.1 §1.7.1) | Security-critical |
| `hitl.gate.evaluated` | C-CP-20 §20.6 (D5 v1.3 §1.8) | Operator-burden eval primitive substrate |
| `hitl.invocation.opened` | C-CP-20 §20.6 (D5 v1.3 §1.8) | Tamper-evidence |
| `hitl.invocation.responded` | C-CP-20 §20.6 (D5 v1.3 §1.8) | Tamper-evidence (v1.1 split of v1 `closed`) |
| `hitl.invocation.timed_out` | C-CP-20 §20.6 (D5 v1.3 §1.8) | Tamper-evidence (v1.1 split of v1 `closed`) |
| `fallback.triggered` | C-CP-03 §3.5 (F1 / F3 capability-floor (iv)) | Reliability-critical |
| `breaker.tripped` | C-CP-03 §3.5 + C-OD-07 §7.2 (F1 / C9) | Reliability-critical (seven-attribute schema per C-OD-07) |
| `topology.fanout.opened` | C-CP-14 §14.3 (D4 v1.1 §1.9) | Tamper-evidence at fan-out |
| `topology.fanout.closed` | C-CP-14 §14.3 (D4 v1.1 §1.9) | Per-sibling cost rollup at fan-out close |
| `subagent.span` (root) | C-CP-14 §14.3 (D4 v1.1 §1.9) | Sub-agent privilege inheritance audit |
| `mcp.tool.call` | C-AS-14 §14.8 (D3 v1.1 §1.8.1 + F2-09 closure) | C10 audit requirement; head=1.0 with tail-keep-on-trust-tier-floor-violations |
| `audit.*` (any event with `audit.signature.*` attributes) | C-CP-20 §20.4 (D5 v1.3 §1.4) | Multi-tenant-compliance only; cryptographic anchor |
| `files.operation` at `kind ∈ {upload, delete}` | C-AS-14 §14.8 (D3 v1.1 §1.8.1) | Files API mutation operations |
| `memory.operation` at `kind ∈ {write, update, delete}` | C-AS-14 §14.8 (D3 v1.1 §1.8.1) | Memory tool mutation operations |
| `validator.fail.*` at `validator.fail.permanence=permanent` | C-CP-21 §21.6 (D5 v1.3 §1.10.1) | Tamper-evidence per `c7-observability` SKILL.md discipline |
| `managed_agents.runtime` | C-AS-14 §14.8 (D3 v1.1 §1.8.1) | Cost attribution ($0.08/hr non-trivial) |
| `skill.activation` | C-AS-14 §14.8 (D3 v1.1 §1.8.1) | head=1.0 design-time; base-rate at production |

### §9.3 Sampling-discipline invariants

| Invariant | Contract |
|---|---|
| **Always-sampled-set inviolable** | The set in §9.2 is a hard floor at the deployment-binding layer; not operator-tunable at base-rate |
| **Per-deployment-surface mode** | At design-time deployment surface (local-development), head-based sampling permits operator-tunable high-cardinality sampling against the sqlite ring-buffer (default 1.0; rotation handles volume); at production-time deployment surfaces, tail-based sampling with the always-sampled exceptions |
| **Per-cell sampling refinement** | Within the always-sampled set, per-cell sampling is uniform across all cells; within the base-rate set per C-OD-10, per-cell base-rate tuning admits operator choice within Persona §4 + §6 envelope |

**Deferred to implementation discretion.** Specific tail-based sampling decision algorithm (per-trace-completion-replay vs. eager-batch-sampling); specific tail-keep-on-classification filter implementation per OTel SDK; specific always-sampled-event detection at SDK boundary (compile-time annotation vs. runtime hook); specific cross-SDK sampling-decision conformance test.

---

## §10 C-OD-10 — Base-rate set + tail-keep-on-classification

**Contract surface.** Base-rate-sampled span set + tail-keep-on-classification span-tree preservation rules.

**PRD requirement(s) satisfied.** R-OD-03 (sampling discipline — base-rate half).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.3 base-rate-sampled list + tail-keep-on-classification list (preserved per v1.1 change-note with `tool.call` annotated to scope to non-MCP variants per F2-09 closure).

**Cross-axis citation.** `Spec_Action_Surface_v1.md` C-AS-15 §15.4 (`sandbox.enter` / `sandbox.exit` base-rate); C-AS-14 §14.8 (`llm.inference` head-based-dev / tail-based-prod; `files.operation` non-mutation base-rate; `memory.operation` non-mutation base-rate); `Spec_Control_Plane_v1.md` C-CP-03 §3.5 (`retry.attempt` 1st-attempt base-rate); C-CP-05 §5.4 (`lease.*` base-rate).

**Persona linkage.** Persona §6 (per-class cost ceiling — base-rate sampling enables cost-bounded telemetry).

**Specification content.**

### §10.1 Base-rate-sampled set (cell-tunable; default 1.0 at solo-developer; 0.05–0.5 typical at team-binding+; 0.1–0.5 at multi-tenant-compliance)

| Event class | Source declaration |
|---|---|
| `chat` (where `gen_ai.operation.name=chat`) | C-OD-04 §4.2 |
| `execute_tool` | C-OD-04 §4.2 |
| `sandbox.enter` | C-AS-15 §15.4 |
| `sandbox.exit` | C-AS-15 §15.4 |
| `tool.call` (non-MCP tool calls only; MCP variants always-sampled per C-OD-09 §9.2 / F2-09 closure) | C-AS-14 §14.8 |
| `retrieval` (where `gen_ai.operation.name=retrieval`) | C-OD-04 §4.2 |
| cache events (cache hit / cache miss / cache creation) | C-AS-14 §14.2 |
| `embeddings` | C-OD-04 §4.2 |
| `text_completion` | C-OD-04 §4.2 |
| `files.operation` at `kind ∈ {list, metadata, reference}` (non-mutation Files API operations) | C-AS-14 §14.8 |
| `memory.operation` at `kind ∈ {read, list}` (non-mutation Memory tool operations) | C-AS-14 §14.8 |
| `lease.acquired` / `lease.released` | C-CP-05 §5.4 |
| `retry.attempt` at 1st attempt (always-sampled at 2nd onward per C-CP-03 §3.5) | C-CP-03 §3.5 |

### §10.2 Tail-keep-on-classification (preserve span trees on classification trigger)

| Classification trigger | Span-tree preservation | Source declaration |
|---|---|---|
| `permanent-fail` span trees | Any span tree where classification == `permanent-fail` per ADR-D2 §1.8 fail-class taxonomy is preserved at tail-based sampling | C-AS-04 §4.1 + ADR-D6 v1.1 §1.3 |
| `sandbox-violation` propagation | Parent + sibling spans of any `sandbox.violation` event preserved | ADR-D6 v1.1 §1.3 |
| `breaker-trip` propagation | Parent + sibling spans of any `breaker.tripped` event preserved | ADR-D6 v1.1 §1.3 |

### §10.3 Per-cell base-rate tuning envelope

| Persona tier × deployment surface | Base-rate default | Base-rate envelope |
|---|---|---|
| solo-developer × local-development | 1.0 | Operator-tunable (sqlite ring-buffer rotation handles volume) |
| solo-developer × self-hosted-server | 1.0 | Operator-tunable |
| solo-developer × managed-cloud | 1.0 | Vendor-bound at free-tier; operator-tunable at paid tiers |
| team-binding × local-development | 0.5 | 0.1–1.0 envelope |
| team-binding × self-hosted-server | 0.1 | 0.05–0.5 envelope |
| team-binding × managed-cloud | 0.1 | 0.05–0.5 envelope |
| multi-tenant-compliance × self-hosted-server | 0.2 | 0.1–0.5 envelope; per-tenant cardinality isolation per C-OD-21 |
| multi-tenant-compliance × managed-cloud | 0.2 | 0.1–0.5 envelope; per-tenant cardinality isolation per C-OD-21 |

The envelope tightens monotonically along the persona-tier axis at fixed deployment surface (solo → team → multi-tenant); this is the sampling-discipline component of bridging-arc traversal preservation per C-OD-22.

**Deferred to implementation discretion.** Specific tail-based sampling filter implementation; specific base-rate numeric calibration at deployment-binding time per Persona §11.4 closure; specific per-cell sampling-decision algorithm (per-trace probabilistic vs. systematic-step); specific cross-SDK base-rate conformance.

---

## §11 C-OD-11 — Cardinality budget per cell + cardinality-safe-attribute discipline

**Contract surface.** Per-cell cardinality budget + cardinality-safe-attribute enumeration for metric dimensions.

**PRD requirement(s) satisfied.** R-OD-03 (sampling discipline — cardinality budget half).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.3 cardinality budget per cell paragraph + cardinality-safe-attribute paragraph (preserved verbatim per v1.1 change-note).

**Persona linkage.** Persona §11.4 (throughput rough order-of-magnitude open item — bounds the cardinality budget at team-binding+ cells); §10.4 (compliance-readiness — per-tenant cardinality isolation at multi-tenant-compliance cells).

**Specification content.**

### §11.1 Per-cell cardinality budget posture

| Cell class | Cardinality budget |
|---|---|
| solo-developer × * | Operator-tunable high-cardinality sampling against the sqlite ring-buffer (default 1.0; rotation handles volume) per C-OD-19 |
| team-binding × * | Per-cell cardinality budget bounded per Persona §11.4 throughput rough order-of-magnitude open item; envelope refines downstream of §11.4 closure |
| multi-tenant-compliance × * | Per-cell cardinality budget + per-tenant cardinality isolation (per-tenant rate limits at OTLP collector boundary or at backend ingestion per C-OD-21) |

### §11.2 Cardinality-safe-attribute discipline at metric dimensions

Metric dimensions MUST use cardinality-safe attributes only. Per Cluster 4 §2.1.5 [HIGH] cardinality blowup failure mode (most common in-the-field misuse), this is enforced as a runtime invariant.

**Cardinality-safe attributes (admissible as metric dimensions):**

| Attribute | Cardinality bound |
|---|---|
| `gen_ai.operation.name` | 7 (enum per C-OD-04 §4.2) |
| `gen_ai.provider.name` | bounded (per-provider enumeration; expected ≤20 across all providers) |
| `gen_ai.request.model` | bounded per provider |
| `gen_ai.response.finish_reasons` | bounded (enum per OTel GenAI semconv 1.41.0) |
| `sandbox.tier` | 4 (enum per C-AS-01 §1.1) |
| `sandbox.tech` | 5 (enum per C-AS-15 §15.2) |
| `sandbox.provider` | 17 (enum per C-AS-15 §15.3) |
| `hitl.gate.level` | bounded per C-CP-19 multiplicative gate-level rule |
| `hitl.response.class` | 4 (`approve` / `edit` / `reject` / `respond` per C-CP-20 §20.6 four-response palette) |
| `harness.breaker.scope` | 2 (`per_model` / `per_provider` per C-OD-07 §7.1) |
| `harness.breaker.from_state` / `to_state` | 3 each (`closed` / `open` / `half_open` per C-OD-07 §7.1) |
| `validator.fail.class` | 5 (locked five-class taxonomy per C-CP-21 §21.5) |

### §11.3 Cardinality-prohibited attributes (span-only; NEVER metric dimensions)

| Attribute | Cardinality | Reason for exclusion |
|---|---|---|
| `gen_ai.conversation.id` | unbounded (per-session) | Cluster 4 §2.1.5 [HIGH] silent-cardinality-blowup |
| Session IDs, user IDs, tenant IDs | unbounded | Cluster 4 §2.1.5 [HIGH] silent-cardinality-blowup |
| `idempotency_key` | unbounded (per-action) | Span-attribute join key only; metric-dimension use forbidden |
| `mcp.primitive.signature.sha256` | per-primitive content-addressable hash | Per-primitive unbounded |
| `skill.version_sha` | per-Skill-version git hash | Per-version unbounded |
| `audit.signature.sha256` / `audit.signature.prior_hash` | per-event hash | Per-event unbounded |

### §11.4 Pattern P1 cardinality discipline anchor

The cardinality-safe-attribute discipline is the §Consequences-level commitment derived from the Cluster 4 §2.1.5 [HIGH] cardinality blowup failure mode. Downstream dashboard authoring at Phase 6+ MUST respect this discipline; violation produces metric-emission cardinality blowup that defeats the alerting + dashboarding primitives at C-OD-16 + C-OD-17.

**Deferred to implementation discretion.** Specific cardinality-budget numeric thresholds per cell (refines downstream of Persona §11.4 closure); specific cardinality-blowup detection mechanism (per-collector rate-limit vs. backend-side alerting); specific metric-dimension static-schema validation at SDK boundary; specific per-tenant rate-limit implementation at multi-tenant-compliance cells (composes at Phase 6+).

---

## §12 C-OD-12 — Redaction discipline: default-off content + default-on structure

**Contract surface.** Content-attribute capture default posture + structure-attribute emission default posture.

**PRD requirement(s) satisfied.** R-OD-04 (redaction discipline per persona tier — content-attribute default half).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.4 redaction discipline default-off content attributes + default-on structure attributes paragraphs (preserved per v1.1 change-note with v1.1 row-by-row structure-attribute list per §1.4).

**Cross-axis citation.** `c7-observability` SKILL.md sole owner of Cross-cutting #2 observability hooks; structure-not-content discipline. `c10-action-safety` SKILL.md eval-grade redaction discipline.

**Persona linkage.** Persona §10.4 (compliance-readiness — content-attribute default-off per Opt-In classification).

**Specification content.**

### §12.1 Default-off content attributes (OTel GenAI semconv 1.41.0 Opt-In classification)

```
gen_ai.input.messages
gen_ai.output.messages
gen_ai.system_instructions
gen_ai.tool.definitions
gen_ai.tool.call.arguments
gen_ai.tool.call.result
gen_ai.retrieval.documents
gen_ai.retrieval.query.text
```

These attributes are content-bearing (PII-bearing per OTel GenAI semconv 1.41.0 Opt-In classification). Default-off at all cells; per-persona-tier override gradient per C-OD-13.

### §12.2 Default-on structure attributes

```
gen_ai.operation.name, gen_ai.provider.name, gen_ai.request.model
server.address, server.port
gen_ai.usage.input_tokens, gen_ai.usage.output_tokens
gen_ai.response.finish_reasons
gen_ai.conversation.id (span attribute only — NEVER metric dimension per C-OD-11)
sandbox.tier, sandbox.tech, sandbox.provider, sandbox.fail.class, sandbox.policy.assigned_tier_reason, sandbox.cost.tier_overhead_ms, sandbox.cost.tier_overhead_usd
hitl.gate.level, hitl.gate.persona_tier, hitl.gate.required, hitl.invocation.placement, hitl.invocation.handoff_context_size_bytes, hitl.invocation.audit_ledger_entry_id, hitl.response.class, hitl.response.latency_ms, hitl.response.summary_hash, hitl.timeout.duration_ms, hitl.timeout.degradation_mode_applied
anthropic.cache_creation_input_tokens, anthropic.cache_read_input_tokens, anthropic.cache_breakpoint_id, anthropic.cache_ttl_seconds, anthropic.thinking_mode, anthropic.thinking_budget_tokens, anthropic.thinking_effort, anthropic.batch_id (optional), anthropic.tokenizer_version, anthropic.inference_geo (optional)
mcp.server.name, mcp.server.trust_tier, mcp.protocol_version, mcp.transport, mcp.auth_present, mcp.primitive.kind, mcp.primitive.signature.sha256
skill.id, skill.name, skill.version_sha, skill.frontmatter.version, skill.body_tokens, skill.activation_mode
managed_agents.runtime_ms, managed_agents.session_id, managed_agents.billable_seconds
engine.class, engine.event_history.tier, engine.event.id
provider_discriminator
audit.signature.sha256, audit.signature.prior_hash, audit.actor.id, audit.signature.value, audit.signature.algorithm, audit.signature.key_id, audit.signature.key_period (multi-tenant-compliance always; team-binding optional subset per D5 v1.3 §1.4.1 persona-tier emission discipline)
validator.fail.class, validator.fail.cause_attribution, validator.fail.permanence
files.operation.kind, files.file_id, files.filename, files.mime_type, files.size_bytes, files.workspace_id, files.batch_composition (optional), files.code_execution_composition (optional)
memory.operation.kind, memory.path, memory.backend, memory.bytes_read (optional), memory.bytes_written (optional), memory.context_editing_active
harness.breaker.scope, harness.breaker.from_state, harness.breaker.to_state, harness.breaker.trigger_count, harness.breaker.permanent_fail_repeats, harness.breaker.tool_id, harness.breaker.model_version
```

### §12.3 Structure-not-content invariant

| Invariant | Contract |
|---|---|
| **Structure-bearing only** | Default-on attributes record observability semantics — operation name, provider, model, token counts, hash digests, IDs, enums, latency bounds, cost overheads — but never raw tool I/O content, raw message content, or raw retrieval-document content |
| **Hash-not-payload discipline** | Where a content surface must be auditable (e.g., HITL response summary), the attribute carries a hash digest (`hitl.response.summary_hash`) — not the payload |
| **Cross-namespace consistency** | All 15 specialization-layer namespaces per C-OD-05 respect the structure-not-content discipline; no namespace introduces content-bearing attributes by default |

**Deferred to implementation discretion.** Specific OTLP-collector default-off filter implementation per cell; specific content-attribute encryption-in-flight mechanism if content capture is enabled at operator override; specific structure-attribute serialization format; specific hash-digest algorithm at attribute level (SHA-256 baseline per `Spec_Information_Substrate_v1.md` C-IS-06 §6.2).

---

## §13 C-OD-13 — Per-persona-tier content-capture override gradient + cross-deployment monotonic-tightening

**Contract surface.** Three-tier content-capture posture matrix + cross-deployment monotonic-tightening invariant.

**PRD requirement(s) satisfied.** R-OD-04 (redaction discipline per persona tier — override gradient half); R-OD-08 (bridging-arc traversal preservation — redaction discipline component).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.4 per-persona-tier override gradient table (preserved per v1.1 change-note); ADR-D6 v1.1 §1.4 pre-collector redaction at multi-tenant-compliance paragraph (preserved per v1.1 change-note); ADD §5.3.1 bridging-arc traversal preservation (redaction class-tightened-not-relaxed).

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-06 (hash-chain construction discipline — audit-ledger entry composition for content-capture-enable events); `Spec_Control_Plane_v1.md` C-CP-20 §20.4 (audit-ledger cryptographic shape per persona-tier — content-capture-enable emits audit entry).

**Persona linkage.** Persona §2 (bridging-arc traversal commitment); §10.4 (compliance-readiness — pre-collector redaction at compliance cells); §11.6 + §11.7 (compliance + vendor / IP-handling restrictions at multi-tenant binding).

**Specification content.**

### §13.1 Per-persona-tier override gradient

| Persona tier | Content-capture posture | Override mechanism | Audit-trail discipline |
|---|---|---|---|
| **solo-developer** | Content capture toggleable per session (operator-self-redact discipline) | Per-session toggle at the in-process collector configuration; default-off | No compliance attestation required; ring-buffer is operator-local |
| **team-binding** | Content capture default-off; redaction processor at the OTLP collector boundary | Enabling content capture for a session emits an audit-ledger entry per the per-persona-tier ledger cryptographic shape per C-CP-20 §20.4 + C-IS-06 hash-chain construction | Audit-ledger entry MUST be hash-chained per C-IS-06 |
| **multi-tenant-compliance** | Content capture structurally prohibited OR routed through eval-grade redaction pipeline per `c10-action-safety` SKILL.md; redaction applied **pre-collector** at SDK / wrapper attribute-set time BEFORE the BatchSpanProcessor buffer | Operator cannot enable raw content capture; eval-grade pipeline produces opaque tokens (`[REDACTED:PII]`, `[REDACTED:MCP_ARG]`) | Per-tenant cryptographic-signed audit ledger per C-CP-20 §20.4 + C-IS-06 + C-IS-10 §10.3 |

### §13.2 Pre-collector redaction at multi-tenant-compliance

Per C10 propose-refinement at convening: at multi-tenant-compliance cells, the eval-grade redaction pipeline runs at the SDK / wrapper boundary that emits spans, applying redaction at attribute-set time. This is a per-cell implementation contract: any span emitted from the harness at a multi-tenant-compliance cell MUST have content attributes either omitted entirely OR redacted to opaque tokens BEFORE the span hands off to the BatchSpanProcessor.

**Rationale.** Running redaction at the collector boundary creates a window where un-redacted content sits in the BatchSpanProcessor buffer; that window is a compliance-readiness gap per Persona §10.4. Pre-collector redaction at SDK / wrapper time eliminates the window.

### §13.3 Cross-deployment monotonic-tightening invariant

The redaction class strictly tightens along the persona-tier axis at fixed deployment surface:

```
solo-developer (operator-self-redact)
    → team-binding (redaction-processor at OTLP collector boundary + audit-ledger entry)
        → multi-tenant-compliance (pre-collector eval-grade pipeline + cryptographic-signed audit ledger)
```

| Invariant | Contract |
|---|---|
| **Monotonic tightening** | Redaction class never relaxes across the bridging arc; class transitions are strictly tightening |
| **Downgrade rejection** | A bridging-arc transition that would relax redaction class (e.g., multi-tenant → team-binding) is structurally rejected at the cell-transition surface per C-OD-22 |
| **Per-axis cross-deployment monotonicity** | ADR-D5 v1.3 §1.5.2 + ADR-D2 v1.1 §1.6 cross-deployment monotonicity compose with this redaction-class monotonicity at the bridging-arc transition surface |

**Deferred to implementation discretion.** Specific eval-grade redaction pipeline implementation per `c10-action-safety` SKILL.md (composes at Phase 6+); specific redaction-token format (opaque-string vs. typed-marker vs. hash-digest); specific per-session content-capture toggle UX (config-file flag vs. CLI command); specific audit-ledger-entry emission API at the redaction boundary; specific SDK / wrapper boundary for pre-collector redaction injection.

---

## §14 C-OD-14 — Cost-attribution-per-span formula composing pricing + sandbox-tier + per-sibling rollup

**Contract surface.** Per-span cost formula + per-sibling rollup at fan-out close + idempotency-key join.

**PRD requirement(s) satisfied.** R-OD-05 (cost-attribution per span at run cost-attribution surface).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.5 cost-attribution-per-span dashboarding contract (per-Anthropic-pricing formula + sandbox-tier overhead + per-sibling rollup; preserved verbatim per v1.1 change-note except `reasoning.output_tokens` line dropped per F2-01).

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-05 (state-ledger entry shape — `idempotency_key` field); C-IS-10 §10.2 (`idempotency_key` join export — D6 cost-attribution-per-span consuming axis row); `Spec_Action_Surface_v1.md` C-AS-15 §15.6 (sandbox-violation events join on `idempotency_key`; `sandbox.cost.tier_overhead_*` attributes); `Spec_Control_Plane_v1.md` C-CP-14 §14.1 (fan-out boundary cost-attribution anchors); C-CP-24 §24.2 (cross-axis composition exports — fan-out cost-attribution row).

**Persona linkage.** Persona §6 (per-workload-class cost ceiling); §10.2 (cost-attribution-per-span as foundational primitive); §8.5 (cross-class cost × reliability × capability coupling).

**Specification content.**

### §14.1 Per-span cost formula (Anthropic-pricing canonical)

```
# Per-span model cost (Anthropic-pricing canonical formula)
cost = (input_tokens − cache_read − cache_creation) × BASE_INPUT
     + cache_creation × BASE_INPUT × 1.25                   # 5-min TTL cache creation surcharge
     + cache_read × BASE_INPUT × 0.10                       # cache hit discount
     + output_tokens × BASE_OUTPUT                          # v1.1 includes extended-thinking output
                                                            # tokens per Anthropic billing-as-output-
                                                            # tokens model [MODERATE; not verified
                                                            # against primary-source pricing
                                                            # documentation accessed this session]
```

Where `BASE_INPUT` and `BASE_OUTPUT` are per-`(gen_ai.provider.name, gen_ai.request.model, tokenizer_version)` rate values per C-OD-15 §15.2.

### §14.2 Sandbox-tier overhead addition

Per `Spec_Action_Surface_v1.md` C-AS-15 §15.6 (`sandbox.cost.tier_overhead_*` attributes per ADR-D2 v1.1 §1.7.1):

```
total_cost = cost
           + sandbox.cost.tier_overhead_usd                  # per-sandbox-instance cost overhead
total_latency = span.duration
              + sandbox.cost.tier_overhead_ms                # sandbox tier startup/teardown latency
```

### §14.3 Per-sibling rollup at fan-out close

Per `Spec_Control_Plane_v1.md` C-CP-14 §14.1 (per-sibling cost attribution rollup at `topology.fanout.closed`):

```
# At topology.fanout.closed event, parent span aggregates sum(child sibling total_cost)
parent.fanout.total_cost = Σ sibling.total_cost
parent.fanout.total_latency = max(sibling.total_latency)    # fan-out parallel; sequential uses Σ
```

### §14.4 Idempotency-key join

Per `Spec_Information_Substrate_v1.md` C-IS-10 §10.2 (idempotency-key join export; D6 cost-attribution-per-span consuming axis row):

| Property | Contract |
|---|---|
| **Join key** | Every per-span cost record carries the parent's `idempotency_key` per C-IS-05 |
| **Replay-safe composition** | Cost-attribution-per-span composes with F2 state-ledger via `idempotency_key` to avoid double-counting on replay |
| **Per-sub-agent inheritance** | Sub-agent dispatch propagates a derived `idempotency_key` per C-AS-15 §15.6 sub-agent boundary inheritance; per-sibling rollup at §14.3 composes against the derived keys |

### §14.5 [F2-12 ACTIVE engagement] — Deferred-to-implementation discretion at this contract per session prompt §5.4 [CF-1]

**F2-12 carry-forward affected-contract notation.** Per `Phase_5_Session_4_Session_Prompt.md` §5.4 [CF-1] authoring approach (iii), the cost-attribution-per-span composition with F2 `idempotency_key` is the D6-side closure half of the F2-12 carry-forward. The v1 commitment is the formula + idempotency-key join as specified at §14.1–§14.4 (the current D6 v1.1 commitment level).

**Open at F2-12 closure.** Three composition surfaces remain deferred to D1 v1.2 + D6 v1.2 (parallel `council-orchestrator` C7+C9 session per ADD §6.3.1 active path):

| F2-12 surface | Current v1 disposition | Forward closure at D1 v1.2 + D6 v1.2 |
|---|---|---|
| Span re-emission semantics under engine replay (event-sourced-replay engines: do spans re-emit, or is replay a deterministic re-read without new span emission?) | Open; v1 cost formula computes per-span cost regardless of replay status | D1 v1.2 commits engine-class re-emission semantics; D6 v1.2 extends `engine.*` namespace with replay discriminators |
| `retry.attempt` sibling-span discipline at D6 ingestion (does D6 ingest `retry.attempt` event AND a new sibling span?) | Open; v1 per C-CP-03 §3.5 commits event + new sibling span; revisable at D6 v1.2 | D6 v1.2 + Control Plane spec revision pass at C-CP-03 §3.5 |
| Trace-ingestion dedup composition with F2 `idempotency_key` at D6 cost-attribution-per-span (must avoid double-counting on replay) | Open; v1 commits idempotency-key join as the dedup primitive; the dedup ALGORITHM is deferred | D6 v1.2 commits dedup algorithm |

**Forward routing.** Parallel `council-orchestrator` C7+C9 session at operator discretion per ADD §6.3.1 active path. Closure expected as D1 v1.2 + D6 v1.2; absorbed into ADD v1.3; PRD revision pass produces `PRD_v1.1.md`; Operational Discipline spec revision pass at C-OD-14 (`Spec_Operational_Discipline_v1.1.md`); composition with Control Plane spec revision at C-CP-08 + C-CP-03 §3.5.

**Deferred to implementation discretion.** Specific cost-attribution-per-span emission mechanism per OTel SDK; specific per-cell cost-rollup query implementation at backend; specific replay-dedup algorithm at D6 v1.2 closure (out of v1 scope per F2-12); specific BASE_INPUT / BASE_OUTPUT rate-table refresh cadence (deployment-binding-time per C-OD-15 §15.2); specific cross-family `provider_discriminator` cost rollup query at backend per §C-OD-15 §15.1.

---

## §15 C-OD-15 — Cross-family pricing differential + tokenization-version anchor

**Contract surface.** Cross-family `provider_discriminator` cost rollup discipline + tokenization-version anchor for dashboard stability.

**PRD requirement(s) satisfied.** R-OD-05 (cost-attribution per span — cross-family pricing + tokenization-version half).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.5 cross-family pricing differential paragraph + tokenization-version anchor paragraph (preserved verbatim per v1.1 change-note).

**Cross-axis citation.** `c7-observability` SKILL.md `provider_discriminator` discipline (primary anchor per F2-10 closure); ADR-F1 v1.2 §Decision (composition context — chain-advancement seam).

**Persona linkage.** Persona §10.2 (cost-attribution-per-span as foundational primitive — cross-family visibility required under fallback chain advancement per ADR-F1 v1.2).

**Specification content.**

### §15.1 Cross-family `provider_discriminator` cost rollup

The `provider_discriminator` attribute per C-OD-05 §5.1 row 15 carries the cross-family fallback chain family tag (`frontier_managed`, `frontier_managed_alt`, `local_ollama`, etc.). The dashboard cost rollup at per-cell binding per C-OD-16 sums:

| Rollup axis | Aggregation |
|---|---|
| Per-`provider_discriminator` | Σ per-family cost (gives operator per-family cost visibility under fallback) |
| Per-`(gen_ai.provider.name, gen_ai.request.model)` | Σ per-provider-and-model cost (gives operator per-model visibility) |
| Per-fallback-event | Each retry's span carries the actual `gen_ai.provider.name`; the parent span carries the `provider_discriminator` family tag for cross-family rollup |

### §15.2 Tokenization-version anchor

Per Cluster 4 §2.1.5 [HIGH] silent-breakage failure mode (Opus 4.7 +35% tokens silently breaking dashboards built on Opus 4.6 token assumptions), the per-cell dashboard binding MUST include either:

| Option | Contract |
|---|---|
| **Option A** | `gen_ai.request.model.tokenizer_version` (or equivalent — `anthropic.tokenizer_version` per C-AS-14 §14.2) attribute on every span; dashboard queries filter on tokenizer_version |
| **Option B** | Versioned price table keyed on `(gen_ai.provider.name, gen_ai.request.model, tokenizer_version)`; dashboard joins on the keyed price table for accurate cost |

D6 commits this as a downstream dashboard-authoring discipline — a §Consequences-level anchor, not a D6 §Decision-level configuration. Phase 6+ dashboard authors MUST select Option A or Option B; failing to anchor on tokenizer_version produces silent cost-dashboard breakage on model version transitions.

### §15.3 Cross-family fallback chain composition reference

The cross-family fallback chain advancement per ADR-F1 v1.2 §Decision composes with this contract at the chain-advancement seam:

| Fallback transition | Cost-attribution impact |
|---|---|
| Anthropic → cross-family OpenAI/Gemini → local Ollama | Each fallback attempt's span carries its actual `gen_ai.provider.name` and updated `BASE_INPUT` / `BASE_OUTPUT` rates per C-OD-14 §14.1 |
| Parent span family-tag rollup | Parent span retains `provider_discriminator` family tag; child retry spans carry per-attempt provider |

**Deferred to implementation discretion.** Specific dashboard query implementation per backend (Langfuse cost dashboard / Arize AX cost panel / vendor LLM-obs cost view / Grafana panel); specific price-table refresh cadence and source-of-truth (vendor docs scrape / manual operator binding); specific tokenizer-version migration handling per provider; specific cross-family rollup query SQL/PromQL per backend.

---

## §16 C-OD-16 — Per-cell cost-attribution dashboard binding

**Contract surface.** Per-cell dashboard binding signature + alerting threshold composition with per-class cost ceiling.

**PRD requirement(s) satisfied.** R-OD-05 (cost-attribution per span — per-cell dashboard binding half).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.5 per-cell cost-attribution dashboard binding paragraph (preserved per v1.1 change-note).

**Persona linkage.** Persona §6 (per-workload-class cost ceiling); §10.2 (cost-attribution-per-span as foundational primitive).

**Specification content.**

### §16.1 Per-cell dashboard binding signature

Every active cell of the 9-cell matrix (per C-OD-01) MUST surface a cost-attribution dashboard binding the per-Anthropic-pricing formula per C-OD-14 §14.1 to the Persona §6 per-class cost ceiling alerting:

| Cell class | Dashboard binding form | Alerting hook |
|---|---|---|
| solo-developer × * | TUI trace browser scoped query against the sqlite ring-buffer per C-OD-19; no separate dashboard layer | Operator-self-inspection; alerting optional via TUI threshold annotation |
| team-binding × * | Named dashboard query against the cell-committed backend (Langfuse cost dashboard / Arize AX cost panel / Helicone analytics / vendor LLM-obs cost view / Grafana panel for OTel-to-vendor) | Backend-side alerting bound to per-class cost ceiling threshold |
| multi-tenant-compliance × * | Per-tenant dashboard separation; per-tenant cost-attribution view; cross-tenant aggregation forbidden per C-OD-21 | Per-tenant alerting; cross-tenant aggregation forbidden |

### §16.2 Alerting threshold composition

Per Persona §6 per-class cost ceiling, the alerting threshold is operator-tunable per workload class. The threshold composes with the per-cell base-rate sampling at C-OD-10 §10.3 — at sampled rates below 1.0, the dashboard cost rollup is scaled by `1/base_rate` for unbiased cost estimation; the alerting threshold operates against the scaled estimate.

### §16.3 Dashboard composition with operator-burden eval primitive

The cost-attribution dashboard per this contract is one of the per-cell dashboard surfaces; the operator-burden eval primitive dashboard per C-OD-17 is parallel. Both bind to the same per-cell backend (e.g., a Langfuse self-hosted instance carries both cost panels and operator-burden panels). The dashboards are conceptually separable; the implementation MAY consolidate them per backend's dashboarding model.

**Deferred to implementation discretion.** Specific dashboard authoring per backend (Langfuse dashboard JSON / Arize AX panel config / Datadog dashboard JSON / Grafana dashboard JSON); specific alerting backend integration (PagerDuty / Slack / email / on-call rotation); specific dashboard versioning protocol if dashboards migrate across backend versions; specific per-class-cost-ceiling threshold values per workload class per Persona §6 (operator-tunable at deployment-binding time).

---

## §17 C-OD-17 — Five operator-burden eval primitives + separate-child-span eval emission

**Contract surface.** Five-primitive set + emission shape (separate child span; never span-event-only).

**PRD requirement(s) satisfied.** R-OD-06 (operator-burden eval primitive at per-cell dashboard surface).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.6 operator-burden eval primitive dashboard binding (preserved per v1.1 change-note); ADR-D6 v1.1 §1.6 online vs offline eval pattern commitment paragraph (separate-child-span emission).

**Cross-axis citation.** `Spec_Control_Plane_v1.md` C-CP-24 §24.2 row 3 (per-cell operator-burden eval primitive export — `expected_hitl_invocations_per_session` computed from `hitl.invocation.responded` span counts per C-CP-20 §20.6); `Spec_Action_Surface_v1.md` C-AS-15 §15.4 (`sandbox.violation` always-sampled — `expected_sandbox_violations_per_session` substrate).

**Persona linkage.** Persona §4 (99.9% SLO; selective HITL — operator-burden eval primitives alert when SLO compatibility degrades); §10.2 (selective HITL persona-constrained); §10.4 (compliance-readiness — eval primitives bind dashboard surface).

**Specification content.**

### §17.1 Five-primitive set

| Primitive | Source declaration | Computation shape |
|---|---|---|
| `expected_hitl_invocations_per_session` | ADR-D5 v1.3 §1.8 (declared at C-CP-20 §20.6) | Counter rolled up per agent role and per workload class; computed from `hitl.invocation.responded` span counts |
| `expected_sandbox_violations_per_session` | ADR-D2 v1.1 §1.8 (declared at C-AS-15 §15.4) | Counter rolled up per sandbox tier and per blast-radius tier; computed from `sandbox.violation` span counts |
| `sandbox-tier-routing-accuracy` (meta-eval) | ADR-D2 v1.1 §1.5 | Holdout-evaluable meta-judge over the multiplicative tunable `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier × sandbox_tier`; ratio of correct sandbox-tier assignments to total assignments at holdout-set evaluation |
| `cache-hit-rate-alignment-floor` | ADR-D3 v1.1 §1.5 + §1.8 (declared at C-AS-14 §14.2) | Ratio `cache_read.input_tokens / (cache_read.input_tokens + cache_creation.input_tokens)` rolled up per agent role and per session; alignment-floor threshold operator-tunable |
| `routing-accuracy-holdout` | ADR-F1 v1.2 §Decision | Cross-family fallback judge-human alignment ratio at holdout-set evaluation; tracks fallback chain advancement decisions vs human ground truth |

### §17.2 Separate-child-span eval emission commitment

Per ADR-D6 v1.1 §1.6 online vs offline eval pattern commitment: **D6 commits to separate child span emission for eval scores at all cells**, NOT span-event-only emission.

| Property | Contract |
|---|---|
| **Child-span emission required** | Eval scores emit as a separate child span attached to the parent span being evaluated; span-event-only emission is non-conformant |
| **Rationale** | Span-event-only emission collapses meta-eval traceability — meta-eval (eval-of-eval) cannot run over a span event without re-emission. Child-span emission preserves per-eval span identity that meta-eval requires per `c8-eval-engineer` SKILL.md |
| **Span-volume tradeoff** | Separate-child-span emission costs slightly higher span volume than span-event-only; the meta-eval primitive is non-negotiable per `c8-eval-engineer` ownership |

### §17.3 Per-cell dashboard binding scaling

| Cell class | Dashboard binding form |
|---|---|
| solo-developer × * | TUI trace browser per C-OD-19 surfaces the five primitives as scoped queries against the sqlite ring-buffer; no separate dashboard layer; operator inspects ring-buffer directly. The Husain manual-review → categorize → automate → align loop runs against the ring-buffer with operator self-curation |
| team-binding × * | Dashboard layer is the cell-committed backend per C-OD-02 §2.2; the five primitives bind as named dashboard queries; the alignment-floor ratios bound to alerting per C-OD-18 |
| multi-tenant-compliance × * | Per-tenant dashboard separation; per-tenant alignment-floor binding; meta-eval runs per-tenant with cross-tenant aggregation forbidden per C-OD-21; alerting bound to compliance-attestation thresholds |

**Deferred to implementation discretion.** Specific child-span emission API per OTel SDK (separate child span vs. span event); specific holdout-set construction protocol per primitive per `c8-eval-engineer` SKILL.md; specific Husain manual-review → categorize → automate → align loop tooling; specific per-cell dashboard query authoring per backend; specific alignment-floor threshold values (operator-tunable per `c8-eval-engineer` SKILL.md).

---

## §18 C-OD-18 — Alignment-floor drift detection + eval-vs-runtime-gate distinction

**Contract surface.** Drift-detection emission shape + `gen_ai.eval.kind` discriminator + re-baselining trigger.

**PRD requirement(s) satisfied.** R-OD-06 (operator-burden eval primitive — drift detection + eval-vs-runtime-gate distinction half).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.6 alignment-floor drift detection paragraph (preserved per v1.1 change-note); ADR-D6 v1.1 §1.6 eval-vs-runtime-gate distinction paragraph.

**Cross-axis citation.** `Spec_Control_Plane_v1.md` C-CP-21 §21.5 (`validator.fail.*` namespace declaration — runtime-gate failure substrate); `c5-validation-contract` SKILL.md (in-loop deterministic gates); `c8-eval-engineer` SKILL.md (out-of-loop meta-eval).

**Persona linkage.** Persona §4 (99.9% SLO — alignment-floor drift detection is reliability-eval primitive).

**Specification content.**

### §18.1 Alignment-floor drift detection

Per `c8-eval-engineer` SKILL.md meta-eval discipline, drift in any alignment-floor ratio triggers a `*_floor` re-baselining cycle:

| Alignment-floor primitive | Drift threshold | Re-baselining trigger |
|---|---|---|
| Judge-human Cohen's κ | Operator-tunable | κ falling below threshold triggers re-baselining |
| Cache-hit-rate (`cache-hit-rate-alignment-floor` per C-OD-17 §17.1) | Operator-tunable | Ratio falling below threshold triggers re-baselining |
| Routing-accuracy (`routing-accuracy-holdout` per C-OD-17 §17.1) | Operator-tunable | Ratio falling below threshold triggers re-baselining |
| Sandbox-tier-routing-accuracy (`sandbox-tier-routing-accuracy` per C-OD-17 §17.1) | Operator-tunable | Ratio falling below threshold triggers re-baselining |

### §18.2 Drift-detection emission shape

Drift detection emits as a span event:

```
Event name:    gen_ai.eval.alignment_floor.drift_detected
Always-sampled per C-OD-09 §9.2 (rare, load-bearing for meta-eval correctness)
```

| Attribute | Contract |
|---|---|
| `gen_ai.eval.primitive` | Enum identifying which primitive drifted (one of the five at C-OD-17 §17.1) |
| `gen_ai.eval.alignment_floor.current` | Current ratio value |
| `gen_ai.eval.alignment_floor.threshold` | Threshold below which drift fires |
| `gen_ai.eval.alignment_floor.observation_window` | Time window or sample window over which drift was computed |

### §18.3 Eval-vs-runtime-gate distinction

Two span shapes coexist on the runtime path:

| Span shape | Sampling posture | Source declaration |
|---|---|---|
| **In-loop gate spans** (runtime; deterministic validation per `c5-validation-contract` SKILL.md) | Always-sampled if failure per C-CP-21 §21.6 (`validator.fail.permanence = permanent`); base-rate if pass per C-CP-21 §21.5 + `c5-validation-contract` SKILL.md | C-CP-21 §21.5 (`validator.fail.*` namespace) |
| **Out-of-loop eval child spans** (meta-eval; per `c8-eval-engineer` SKILL.md) | Per C-OD-17 §17.2 separate-child-span emission commitment | C-OD-17 §17.1 (five-primitive set) |

The distinction is enforceable via the `gen_ai.eval.kind` discriminator attribute:

```
gen_ai.eval.kind ∈ { "inline_gate", "offline_judge" }
```

| Discriminator value | Meaning |
|---|---|
| `inline_gate` | In-loop runtime gate; pass/fail outcome routes per C-CP-21 §21.5 + C-AS-04 §4.2 pre-HITL escalation order |
| `offline_judge` | Out-of-loop meta-eval; emission per C-OD-17 §17.2 separate-child-span discipline |

**Deferred to implementation discretion.** Specific drift-detection algorithm per primitive (sliding-window probabilistic vs. threshold-cross detector); specific re-baselining cycle workflow per `c8-eval-engineer` SKILL.md; specific dashboard alerting integration on drift event; specific eval-kind enforcement at SDK boundary.

---

## §19 C-OD-19 — Local-first OTLP collector at solo-developer × local-development

**Contract surface.** In-process collector signature + sqlite ring-buffer trace storage + TUI trace browser surfacing.

**PRD requirement(s) satisfied.** R-OD-07 (local-first OTLP collector at solo-developer × local-development).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.7 local-first OTLP collector commitment block (preserved per v1.1 change-note); ADR-D6 v1.1 §1.1 solo-developer × local-development cell row.

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-10 §10.5 (JSONL event ledger format export — D6 OTLP collector boundary composes at within-turn streaming + across-turn durable trace storage seam per T-perm-2 D6-layer commitment).

**Persona linkage.** Persona §9 (design-time forced to local-development environment); §2 (sole operator at design-time); §10.4 (compliance-readiness — operator-self-redact at solo tier).

**Specification content.**

### §19.1 In-process collector commitment

At the solo-developer × local-development cell (cell-1 per C-OD-01 §1.3):

| Property | Contract |
|---|---|
| **Collector placement** | In-process `otelcol-contrib` instance running within the harness process |
| **Buffer discipline** | `BatchSpanProcessor` with default 5s batching window OR 512 spans batch (whichever first) |
| **No separate daemon** | Operator does NOT run a separate collector daemon; collector lifecycle is bound to the harness lifecycle |
| **Trace residence** | Trace data stays on the developer machine until explicit export |

### §19.2 Sqlite ring-buffer trace storage

Per Persona §10.4 + `c11-operator-local` SKILL.md sqlite-backed ring-buffer primitive ownership:

| Property | Contract |
|---|---|
| **Storage backend** | sqlite ring-buffer at canonical filesystem path per `Spec_Information_Substrate_v1.md` C-IS-01 |
| **Tier classification** | Tier-3 per C3 five-tier durability model (per C-OD-01 §1.3 cell-1 trace storage tier) |
| **Rotation policy** | Default 24h ring-buffer rotation; operator-tunable per C-OD-01 §1.3 retention class |
| **Cardinality posture** | Operator-tunable high-cardinality sampling per C-OD-11 §11.1 (default 1.0; rotation handles volume) |

### §19.3 TUI trace browser primitive

Per `c11-operator-local` SKILL.md TUI trace browser primitive ownership:

| Property | Contract |
|---|---|
| **Direct ring-buffer surfacing** | TUI trace browser surfaces the sqlite ring-buffer directly; no external observability backend dependency |
| **Operator-burden eval primitive surfacing** | The five primitives per C-OD-17 §17.1 surface as scoped queries against the ring-buffer (operator self-curation per C-OD-17 §17.3 row 1) |
| **Cost-attribution dashboard surfacing** | Per-span cost per C-OD-14 surfaces as scoped TUI queries per C-OD-16 §16.1 cell-class row 1 |

### §19.4 Bridging-arc upgrade path

The local-first commitment at this cell does NOT preclude downstream bridging-arc traversal to other cells per C-OD-22. When the bridging-arc state transitions (solo → team or local → self-hosted), the in-process collector + sqlite ring-buffer at this cell are superseded by the destination cell's collector placement and trace storage tier per C-OD-20 + C-OD-22.

**Deferred to implementation discretion.** Specific `otelcol-contrib` configuration manifest (receivers / processors / exporters); specific sqlite schema for the ring-buffer; specific TUI trace browser implementation (terminal toolkit binding; query language); specific ring-buffer rotation mechanism (size-based vs. time-based vs. hybrid); specific cross-platform packaging of the in-process collector (Linux / macOS / Windows binary distribution).

---

## §20 C-OD-20 — Per-cell OTLP collector placement + F4 process-tier reachability

**Contract surface.** Per-cell collector placement matrix + per-sandbox-tier reachability requirements.

**PRD requirement(s) satisfied.** R-OD-07 (local-first OTLP collector — per-cell placement half); R-OD-01 (per-cell collector placement field at C-OD-01 §1.3).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.7 per-cell collector placement table (preserved per v1.1 change-note); ADR-D6 v1.1 §1.7 async emission discipline paragraph; ADR-D6 v1.1 §1.7 process-tier OTLP reachability per F4 v1.1 §Consequences (b)(iv) paragraph; ADR-F4 v1.1 §Consequences (b)(iv) (OTLP collector reachability per tier).

**Cross-axis citation.** `Spec_Action_Surface_v1.md` C-AS-01 §1.1 (four-tier sandbox-isolation tier-set — process / container / microVM / full-VM); C-AS-15 §15.2 (`sandbox.tech` namespace).

**Persona linkage.** Persona §9 (deployment-surface implications); §10.4 (compliance-readiness — collector placement supports tenant-isolation at multi-tenant-compliance cells).

**Specification content.**

### §20.1 Per-cell collector placement matrix

| Cell | Collector placement | Backing |
|---|---|---|
| solo-developer × local-development | In-process otelcol-contrib + BatchSpanProcessor; sqlite ring-buffer; TUI trace browser | C-OD-19 |
| solo-developer × self-hosted-server | In-process collector permitted as alt-route; cell-committed single-node backend's collector preferred (Langfuse self-hosted single-node OTLP endpoint / Arize Phoenix OSS OTLP endpoint / Helicone HTTP-proxy) | C-OD-02 §2.2 cell-2 candidates |
| solo-developer × managed-cloud | Vendor-pipeline (Langfuse Cloud SDK / Datadog Agent / Sentry SDK / Arize SaaS SDK) | C-OD-02 §2.2 cell-3 candidates |
| team-binding × local-development | In-process collector + sqlite ring-buffer for short-window traces, OR Langfuse self-hosted single-node OTLP endpoint at the shared instance | C-OD-02 §2.2 cell-4 candidates |
| team-binding × self-hosted-server | Sidecar OR collector-as-DaemonSet at K8s-resident deployments (humanlayer/agentcontrolplane class per ADR-D1 §1.2 row 4); collector-as-sidecar at non-K8s deployments | C-OD-02 §2.2 cell-5 candidates |
| team-binding × managed-cloud | Vendor-pipeline (collector-as-Lambda OR vendor SDK); per-vendor OTel ingestion path | C-OD-02 §2.2 cell-6 candidates |
| multi-tenant-compliance × self-hosted-server | Sidecar with per-tenant routing OR per-tenant collector instance; collector configuration is per-tenant-isolation-aware (per-tenant resource attributes; per-tenant rate limits at collector boundary) | C-OD-21 + C-OD-02 §2.2 cell-7 candidates |
| multi-tenant-compliance × managed-cloud | Vendor-managed collector (BedrockAgent / Vertex Agent Engine / LangSmith Enterprise SDK); pre-collector redaction at SDK / wrapper boundary applies per C-OD-13 §13.2 | C-OD-02 §2.2 cell-8 candidates |

### §20.2 Async emission discipline

`BatchSpanProcessor` at the collector buffers spans within a small time window and flushes asynchronously:

| Property | Contract |
|---|---|
| **Within-turn latency budget preserved** | Async emission preserves the within-turn execution latency budget; span emission MUST NOT block the within-turn execution path |
| **Solo-developer × local-development latency** | Sub-millisecond at in-process collector |
| **Team-binding+ latency** | Network hop adds latency to durable storage but MUST NOT block within-turn execution |
| **Collector buffer durability** | Buffered spans flush before operator queries trace; loss-on-crash within the buffer window is acceptable at solo-developer cells, structurally rejected at multi-tenant-compliance cells per per-tenant audit ledger durability per C-OD-21 |

### §20.3 Per-sandbox-tier OTLP reachability per F4 v1.1 §Consequences (b)(iv)

| Sandbox tier (per C-AS-01 §1.1) | OTLP reachability requirement |
|---|---|
| Tier-1 process / Tier-2 container (process-tier sandbox at D2 Tier-2) | In-process collector reaches via localhost socket |
| Tier-3 microVM (D2 Tier-3 container or D2 Tier-3 sandbox) | Explicit network-config (e.g., `host.docker.internal` mapping or sidecar collector) required |
| Tier-3 microVM (D2 Tier-3 microVM via Firecracker / E2B) | Per-microVM agent OR egress allow-list required |
| Tier-4 full-VM (D2 Tier-4 full VM for computer-use) | Vendor-managed collector is the typical placement |

### §20.4 Composition with C-OD-19 in-process commitment

At cells where in-process collector placement is committed (cell-1 solo-developer × local-development), C-OD-19 governs the in-process specifics. At cells where in-process is an alt-route (cell-2 solo-developer × self-hosted-server; cell-4 team-binding × local-development), C-OD-19 applies when the alt-route is selected; otherwise the cell-committed backend collector applies per §20.1.

**Duplicate-emission risk at cell-2.** Running both in-process collector and cell-committed backend collector simultaneously creates duplicate-emission risk per Cluster 4 §2.1.5 [HIGH]. The collector configuration MUST route OTLP either to the sqlite ring-buffer OR to the cell-committed backend — not both.

**Deferred to implementation discretion.** Specific collector configuration manifest per cell; specific K8s DaemonSet manifest at team-binding × self-hosted-server K8s deployments; specific vendor-pipeline SDK binding per managed-cloud candidate; specific cross-cell collector configuration migration mechanism (if a deployment moves cells); specific BatchSpanProcessor timeout / batch-size tuning per cell.

---

## §21 C-OD-21 — Multi-tenant tenant-isolation in observability surface

**Contract surface.** Per-tenant trace separation contract + per-tenant audit ledger storage + cryptographic-signed span attributes + pre-collector redaction at compliance cells.

**PRD requirement(s) satisfied.** R-OD-04 (redaction discipline — multi-tenant-compliance pre-collector composition); R-OD-08 (bridging-arc traversal preservation — tenant-isolation component at multi-tenant binding).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.8 multi-tenant tenant-isolation in observability surface (preserved per v1.1 change-note).

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-06 (hash-chain integrity construction discipline); C-IS-10 §10.3 (hash-chain construction discipline export — D5 audit-ledger rows); `Spec_Control_Plane_v1.md` C-CP-20 §20.4 (audit-ledger cryptographic shape per persona-tier).

**Persona linkage.** Persona §10.4 (compliance-readiness foundational primitives — tenant isolation); §11.10 (multi-tenant tenant-isolation specifics open item).

**Specification content.**

### §21.1 Per-tenant trace separation

At multi-tenant-compliance cells (cell-7 and cell-8 per C-OD-01 §1.3), traces MUST be separated per tenant at the OTLP collector boundary or at backend ingestion:

| Cell candidate | Per-tenant separation primitive |
|---|---|
| Langfuse self-hosted multi-tenant (cell-7) | Per-tenant ClickHouse partitioning; `langfuse.tenant_id` resource attribute on every span; tenant-scoped query API |
| Arize AX self-hosted multi-tenant (cell-7) | Per-tenant PostgreSQL schema separation; `arize.organization_id` resource attribute; per-tenant model registry |
| Vendor-managed (cell-8 — Bedrock AgentCore / Vertex Agent Engine / LangSmith Enterprise / Langfuse Cloud Enterprise) | Vendor-managed tenant isolation per vendor SLA; per-tenant resource attributes vendor-defined; cross-tenant query forbidden by vendor enforcement |

### §21.2 Per-tenant audit ledger storage

Per ADR-D5 v1.3 §1.4 + §1.4.1 per-persona-tier ledger cryptographic shape, multi-tenant-compliance cells require **hash-chained + cryptographic signature** audit ledger storage:

| Property | Contract |
|---|---|
| **Storage tier** | Tier-5 (per C3 five-tier durability) per-tenant audit ledger; joins to trace storage via `audit.signature.*` span attributes per C-OD-12 §12.2 |
| **Hash-chain construction** | Per `Spec_Information_Substrate_v1.md` C-IS-06 canonicalize → SHA-256 → prior-event-hash chaining |
| **Cryptographic signature** | Per ADR-D5 v1.3 §1.4.1 — `audit.signature.value` / `audit.signature.algorithm` ∈ `{ed25519, ecdsa-p256, rsa-pss-2048}` (Ed25519 default; operator-tunable `audit_signature_algorithm` axis) / `audit.signature.key_id` / `audit.signature.key_period` |
| **Always-sampled** | `audit.*` attributes always-sampled at multi-tenant-compliance per C-OD-09 §9.2 |
| **Tamper-evidence** | The cryptographic anchor enables tamper-evident audit trail reconstruction independent of the trace storage backend — even if the trace backend is compromised, the audit ledger hash chain validates per C-IS-06 §6.5 |

### §21.3 Pre-collector redaction at multi-tenant-compliance cells

Per C-OD-13 §13.2, the eval-grade redaction pipeline runs at the SDK / wrapper boundary that emits spans, applying redaction at attribute-set time **before** the BatchSpanProcessor buffer. This is the multi-tenant-compliance-mandatory shape; team-binding and solo-developer cells apply redaction at the OTLP collector boundary or via operator-self-redact, both of which permit a small window where un-redacted content sits in buffer.

### §21.4 Cross-tenant aggregation prohibition

| Invariant | Contract |
|---|---|
| **Per-tenant dashboard separation** | Per-tenant dashboard binding per C-OD-16 §16.1 row 3 + C-OD-17 §17.3 row 3 |
| **Per-tenant alignment-floor binding** | Per-tenant alignment-floor binding per C-OD-18 §18.1 — drift detection scoped per tenant |
| **Cross-tenant query forbidden** | Meta-eval runs per-tenant with cross-tenant aggregation forbidden; alerting bound to compliance-attestation thresholds per cell per C-OD-16 §16.1 row 3 |
| **Per-tenant cardinality isolation** | Per C-OD-11 §11.1 — per-tenant rate limits at OTLP collector boundary or at backend ingestion |

**Deferred to implementation discretion.** Specific per-tenant routing mechanism at the OTLP collector (per-tenant collector instance vs. sidecar with routing logic); specific cryptographic key custody mechanism per `audit.signature.key_id` (HSM / cloud KMS / operator-supplied keystore); specific tenant-isolation primitive selection within candidate witness column (partition vs. schema vs. vendor-namespace — refined at Persona §11.10 closure); specific cross-tenant aggregation prohibition enforcement (compile-time vs. runtime vs. operator-policy).

---

## §22 C-OD-22 — Bridging-arc traversal preservation across observability dimensions

**Contract surface.** Eight-transition invariant table + per-dimension preservation contract.

**PRD requirement(s) satisfied.** R-OD-08 (bridging-arc traversal preservation across observability dimensions).

**ADR commitment(s) honored.** ADR-D6 v1.1 §1.1 9-cell matrix + §1.2 unified span schema + §1.3 sampling + §1.4 redaction; ADR-D5 v1.3 §1.5.2 cross-deployment monotonicity; ADR-D2 v1.1 §1.6 cross-deployment sandbox-tier monotonicity; ADD §5.3.1 bridging-arc traversal preservation; ADD §5.1.1 cross-deployment trace continuity at bridging-arc transitions.

**Cross-axis citation.** `Spec_Action_Surface_v1.md` C-AS-12 §12.1 (5-axis multiplicative tunable); C-AS-15 §15.4 (sandbox-tier monotonicity); `Spec_Control_Plane_v1.md` C-CP-19 (T-perm-1 D5-layer multiplicative gate-level rule with cross-deployment monotonicity); C-CP-24 §24.2 row 4 (bridging-arc traversal preservation export).

**Persona linkage.** Persona §2 (bridging-arc traversal commitment); §10.4 (compliance-readiness across the arc); §11.10 (tenant isolation specifics at multi-tenant binding).

**Specification content.**

### §22.1 Eight bridging-arc transitions in scope

Per `Integration_Verification_Report.md` §5.1 — eight in-scope bridging-arc transitions (5 within-column + 3 diagonal; multi-tenant × local-development cell EXCLUDED per C-OD-01 §1.4):

| # | Transition | Type |
|---|---|---|
| 1 | solo-developer × local-development → team-binding × local-development | within-column |
| 2 | solo-developer × self-hosted-server → team-binding × self-hosted-server | within-column |
| 3 | team-binding × self-hosted-server → multi-tenant-compliance × self-hosted-server | within-column |
| 4 | solo-developer × managed-cloud → team-binding × managed-cloud | within-column |
| 5 | team-binding × managed-cloud → multi-tenant-compliance × managed-cloud | within-column |
| 6 | solo-developer × local-development → team-binding × self-hosted-server | diagonal |
| 7 | team-binding × local-development → multi-tenant-compliance × self-hosted-server | diagonal |
| 8 | team-binding × self-hosted-server → multi-tenant-compliance × managed-cloud | diagonal |

### §22.2 Per-dimension preservation invariants

| Observability dimension | Preservation invariant |
|---|---|
| **Span schema ingestion contract** | 15 specialization-layer namespaces per C-OD-05 §5.1 are stable across all 8 transitions; collector placement changes (per C-OD-20) do not drop namespace ingestion |
| **Sampling discipline** | Always-sampled set per C-OD-09 §9.2 preserved across all transitions; base-rate set per C-OD-10 §10.1 tightens monotonically along persona-tier axis per C-OD-10 §10.3 envelope |
| **Redaction discipline** | Strict monotonic tightening per C-OD-13 §13.3 (solo operator-self-redact → team redaction-processor at OTLP collector boundary → multi-tenant pre-collector eval-grade pipeline); downgrade structurally rejected |
| **Trace storage tier** | Monotonic-or-tightened per C-OD-01 §1.3 (Tier-3 sqlite ring-buffer → Tier-4 backend-managed → Tier-4 partitioned + Tier-5 per-tenant audit ledger with cryptographic signature); downgrade structurally rejected |
| **Gate-level multiplicative tunable** | ADR-D5 v1.3 §1.5.2 + ADR-D2 v1.1 §1.6 cross-deployment monotonicity preserved across all transitions; gate-level monotonic-or-tightened across the persona-tier axis at fixed deployment surface; the 5-axis multiplicative tunable per `Spec_Action_Surface_v1.md` C-AS-12 §12.1 composes at every cell |

### §22.3 Transition planning verification surface

At the design-time operator surface, bridging-arc transition planning verifies:

| Verification | Contract |
|---|---|
| **Span-schema preservation** | Destination cell's namespace ingestion is a superset of source cell's (no namespace dropped) |
| **Sampling-discipline monotonic tightening** | Destination cell's always-sampled set ⊇ source cell's; base-rate envelope ⊆ source cell's per C-OD-10 §10.3 |
| **Redaction-discipline monotonic tightening** | Destination cell's redaction class ≥ source cell's (along the operator-self-redact < redaction-processor < pre-collector eval-grade pipeline ordering) |
| **Trace-storage-tier monotonic-or-tightened** | Destination cell's trace storage tier ≥ source cell's tier per C-OD-01 §1.3 |
| **Gate-level monotonic ascension** | Destination cell's gate-level multiplicative tunable evaluation ≥ source cell's per `Spec_Action_Surface_v1.md` C-AS-12 §12.1 and `Spec_Control_Plane_v1.md` C-CP-19 |

### §22.4 Excluded-transition rejection

| Excluded transition | Rejection rationale |
|---|---|
| Any transition targeting multi-tenant-compliance × local-development | Cell structurally excluded per C-OD-01 §1.4 (compliance-readiness foundational primitives incompatible with single-developer-machine deployment) |
| Reverse transitions (e.g., team-binding → solo-developer) | Redaction-class downgrade and trace-storage-tier downgrade structurally rejected per §22.2; reverse transitions are out of bridging-arc traversal scope (the bridging arc is forward-only per Persona §2) |

**Deferred to implementation discretion.** Specific transition-planning UX (configuration migration wizard vs. manual operator review); specific cross-cell observability-config migration mechanism (backend-export-import vs. dual-emission cutover); specific transition-validation enforcement (compile-time schema-check vs. runtime probe at first emission post-transition); specific bridging-arc-binding state machine.

---

## §23 C-OD-23 — Operational Discipline substrate seam exports surface

**Contract surface.** Cross-axis exports from this spec for session 5 (cross-axis composition document, if elected per session prompt §2.4) and Phase 6+ implementation planning to consume by citation.

**PRD requirement(s) satisfied.** All eight R-OD-* (cross-axis composition surface; this contract is the analog of C-IS-10, C-AS-16, C-CP-24 for the Operational Discipline axis).

**ADR commitment(s) honored.** ADR-D6 v1.1 §Consequences (a) (span schema ingestion contract delivers the contract surface for downstream binding); §Consequences (f) (bridging-arc trace continuity discipline); §Consequences (g) (object-storage-tier composition deferred).

**Persona linkage.** Persona §10.2 (cost-attribution-per-span as foundational primitive); §10.4 (compliance-readiness — cross-axis tamper-evidence composition).

**Specification content.**

### §23.1 Span schema ingestion contract export

**Export surface.** C-OD-05 §5.1 — 15-row namespace map with source-as-authoritative-declarer rule per §5.2.

| Consuming axis (session 5 OR Phase 6+) | Composition reference |
|---|---|
| Session 5 cross-axis composition document (if elected per session prompt §2.4) | T-perm-1 5-axis multiplicative tunable: C-OD-05 row 5 (`sandbox.*`) + C-OD-12 §12.2 + C-AS-12 §12.1 + C-CP-19 compose at ADD §5.2.1 multi-layer resolution |
| Session 5 (T-perm-2) | C-OD-19 §19.1 in-process collector + C-OD-20 §20.2 async emission discipline + C-IS-10 §10.5 JSONL event ledger export compose at within-turn / across-turn seam per ADD §5.2.2 D6-layer commitment |
| Session 5 (T-perm-3) | C-OD-05 row 9 (`engine.*`) + C-OD-06 §6.1 lifecycle event mapping + C-OD-07 §7.1 breaker-trip schema + C-CP-23 + ADD §5.2.3 three-layer composition |
| Phase 6+ implementation | All 15 namespaces and their cross-axis source contracts (C-AS-14 / C-AS-15 / C-CP-09 / C-CP-14 / C-CP-20 / C-CP-21) for OTel SDK binding per language ecosystem |

### §23.2 Cost-attribution-per-span export

**Export surface.** C-OD-14 §14.1 formula + §14.2 sandbox-tier overhead + §14.3 per-sibling rollup + §14.4 idempotency-key join.

| Consuming axis | Composition reference |
|---|---|
| Session 5 (cost-attribution as cross-cutting architectural property per ADD §5.3) | Compose with C-IS-10 §10.2 idempotency-key join + C-CP-14 §14.1 fan-out boundary cost-attribution + C-AS-15 §15.6 sandbox-tier cost overhead |
| Phase 6+ dashboard implementation | Per-cell dashboard binding per C-OD-16 §16.1; per-cell candidate-bound dashboard authoring per C-OD-02 §2.2 |
| **F2-12 active engagement (D6 closure half)** | At D1 v1.2 + D6 v1.2 closure, C-OD-14 §14.5 deferred surfaces close; Operational Discipline spec revision pass at C-OD-14 |

### §23.3 Operator-burden eval primitive export

**Export surface.** C-OD-17 §17.1 five-primitive set + §17.2 separate-child-span emission + C-OD-18 §18.1 alignment-floor drift detection.

| Consuming axis | Composition reference |
|---|---|
| Phase 6+ eval implementation per `c8-eval-engineer` SKILL.md | Per-cell holdout-set construction; per-primitive judge-human alignment evaluation; Husain manual-review → categorize → automate → align loop |
| Session 5 (if elected) | Compose with C-CP-21 §21.5 in-loop validator + C-AS-13 §13.6 Memory tool storage backend (operator-burden surface) |

### §23.4 Bridging-arc traversal preservation export

**Export surface.** C-OD-22 §22.1 eight-transition table + §22.2 per-dimension preservation invariants.

| Consuming axis | Composition reference |
|---|---|
| Session 5 (bridging-arc traversal as cross-cutting architectural property per ADD §5.3.1) | Compose with `Spec_Action_Surface_v1.md` C-AS-11 sub-agent monotonic ascension + `Spec_Control_Plane_v1.md` C-CP-19 T-perm-1 D5-layer multiplicative gate-level rule at ADD §5.3.1 |
| Phase 6+ deployment-binding implementation | Bridging-arc transition planning state machine + per-transition validation enforcement |

### §23.5 Object-storage-tier composition (deferred)

Per ADR-D6 v1.1 §Consequences (g): Persona §11.12 (object-storage-tier need for non-text media open item) is **not yet engaged** at this spec. Observability of non-text media (screenshots from computer-use sandbox per Persona §5 [HIGH]) involves both span attributes (e.g., `gen_ai.input.messages` containing image references) and object-storage retrieval. When §11.12 closes downstream, the object-storage-tier composes against the span schema via `gen_ai.input.messages` content references per C-OD-12 §12.1; the composition is **deferred to Phase 4 PRD revision OR Phase 6+ implementation** per ADD §6.1.

**Deferred to implementation discretion.** Specific cross-spec citation strings (resolved at session 5 composition document, if elected); specific seam-versioning convention if D6 ever revises beyond v1.2 closure of F2-12 (out of scope at v1); specific Phase 6+ implementation-planning surface (composes at ADD v1.x → PRD v1.1 → spec revision).

---

## §[carry-forwards]

This meta-section documents PRD-inherited carry-forward items per `Phase_5_Session_4_Session_Prompt.md` §5.4. Entries are **documentation, not contract-bearing** — they do not engage the §[coherence pass] §6.1 per-contract audit (except the affected-contract notation at C-OD-14, which IS contract-bearing per §6.1); they engage the spec's operator-visibility surface.

### [CF-1] F2-12 — D1 v1.1 → v1.2 replay-trace-emission contract (ACTIVE engagement at C-OD-14)

**Status.** 🔄 Deferred-acknowledged at ADD v1.2 §6.3.1 (inherited at PRD v1.0 §[carry-forwards] [CF-1] + session-1 spec §[carry-forwards] [CF-1] + session-2 spec §[carry-forwards] [CF-1] + session-3 spec §[carry-forwards] [CF-1]); not blocking session 4 entry; not blocking session 4 filing.

**Scope.** D1 v1.1 → v1.2 + **D6 v1.1 → v1.2** replay-trace-emission contract covering: (i) span re-emission semantics under engine replay (event-sourced-replay engines: do spans re-emit, or is replay a deterministic re-read without new span emission at D6?); (ii) `retry.attempt` sibling-span discipline at D6 ingestion (does D6 ingest `retry.attempt` event AND a new sibling span?); (iii) trace-ingestion dedup composition with F2 `idempotency_key` at D6 cost-attribution-per-span (must avoid double-counting on replay).

**Operational Discipline spec impact.** **ACTIVE engagement at C-OD-14** (R-OD-05-satisfying contract). Per `Phase_5_Session_4_Session_Prompt.md` §5.4 [CF-1] authoring approach (iii):

- **C-OD-14** authors at the current D6 v1.1 commitment level (cost-attribution-per-span formula + sandbox-tier overhead + per-sibling rollup + idempotency-key join as currently committed at D6 §1.5).
- **C-OD-14 §14.5** carries the explicit F2-12 carry-forward affected-contract notation per `Phase_5_Session_4_Session_Prompt.md` §5.4 [CF-1] authoring approach (iii) — enumerates the three open surfaces (span re-emission semantics; retry sibling-span discipline at D6; trace-ingestion dedup algorithm) deferred to D1 v1.2 + D6 v1.2 closure.
- **C-OD-05 §5.3** notes forward-compatibility at the `engine.*` namespace row — additive attributes permitted at D1 v1.2 closure without namespace-map row restructure.
- **C-OD-06 §6.3** notes F2-12 deferral acknowledgement at the `retry.attempt` sibling-span discipline.
- D1 v1.2 + D6 v1.2 closure will trigger an Operational Discipline spec revision pass at C-OD-14 (and possibly C-OD-05 + C-OD-06 if `engine.*` namespace or lifecycle event mapping expands at D6 v1.2 closure).

**Forward routing.** Parallel `council-orchestrator` C7+C9 session at operator discretion per ADD §6.3.1 active path. Closure expected as D1 v1.2 + D6 v1.2; absorbed into ADD v1.3; PRD revision pass produces `PRD_v1.1.md`; Operational Discipline spec revision pass at C-OD-14 + composition with Control Plane spec revision at C-CP-08 + C-CP-03 §3.5 per session-3 spec §[carry-forwards] [CF-1].

### [CF-2] Workflow §7 substrate-skill propagation

**Status.** Open operator decision; outside P5-CK closure scope; outside Phase 5 scope.

**Origin.** `Project_Workflow_Revision_log.md` v1.4 entry line 297 footnote — `add-consolidation-protocol.md` §3.5 Step 5 substrate-skill update to reference Workflow v1.4 §2.3.5 clause (iv) is a separate skill-substrate revision not in v1.4 scope. Per `Phase_5_Session_3_Session_Prompt.md` §1.4 + `Phase_5_Session_4_Session_Prompt.md` §1.4, Workflow §7 session-prompt-template revision is also recommended, triggered by confirmed systemic Pattern P1 from P3c-CK Iteration 1; this is a parallel skill-substrate revision concern.

**Operational Discipline spec impact.** Not in spec scope (skill-substrate revision is neither architectural commitment nor observable behavior nor contract-bearing material). Documented here for operator-visibility continuity from PRD §[carry-forwards] [CF-2] + session-1/2/3 spec [CF-2]; tracked outside the spec-driven Phase 5 workflow.

**Forward routing.** Operator decision at discretion. No Phase 5 spec revision is triggered by skill-substrate propagation.

---

## §[traceability]

This meta-section establishes bidirectional traceability between R-OD-* PRD requirements and C-OD-* spec contracts per `Phase_5_Session_4_Session_Prompt.md` §5.5.

### Forward trace: PRD requirement → spec contracts

| PRD requirement | Satisfying contract(s) | Composition note |
|---|---|---|
| R-OD-01 | C-OD-01, C-OD-02, C-OD-03 | C-OD-01 = matrix shape; C-OD-02 = per-cell backend class + provider candidate witness columns; C-OD-03 = deferral signature (committed at D6 / deferred to deployment-binding time) |
| R-OD-02 | C-OD-04, C-OD-05, C-OD-06, C-OD-07, C-OD-08 | C-OD-04 = base layer (OTel GenAI semconv 1.41.0); C-OD-05 = 15-namespace ingestion; C-OD-06 = F3 capability-floor (iv) lifecycle event mapping; C-OD-07 = `harness.breaker.*` seven-attribute schema; C-OD-08 = namespace collision discipline |
| R-OD-03 | C-OD-09, C-OD-10, C-OD-11 | C-OD-09 = head/tail mode + always-sampled exception set; C-OD-10 = base-rate set + tail-keep-on-classification; C-OD-11 = cardinality budget + cardinality-safe-attribute discipline |
| R-OD-04 | C-OD-12, C-OD-13, C-OD-21 (composition) | C-OD-12 = default-off content + default-on structure; C-OD-13 = per-persona-tier override gradient + cross-deployment monotonic-tightening; C-OD-21 = multi-tenant pre-collector eval-grade pipeline composition |
| R-OD-05 | C-OD-14, C-OD-15, C-OD-16 | C-OD-14 = cost formula + sandbox-tier overhead + per-sibling rollup + idempotency-key join (**F2-12 active engagement**); C-OD-15 = cross-family `provider_discriminator` + tokenization-version anchor; C-OD-16 = per-cell dashboard binding + alerting threshold composition |
| R-OD-06 | C-OD-17, C-OD-18 | C-OD-17 = five-primitive set + separate-child-span emission; C-OD-18 = alignment-floor drift detection + eval-vs-runtime-gate distinction |
| R-OD-07 | C-OD-19, C-OD-20 | C-OD-19 = local-first OTLP collector at solo-developer × local-development; C-OD-20 = per-cell collector placement + F4 process-tier reachability |
| R-OD-08 | C-OD-21, C-OD-22 | C-OD-21 = multi-tenant tenant-isolation in observability surface; C-OD-22 = bridging-arc traversal preservation across observability dimensions |
| All R-OD-* (cross-axis surface) | C-OD-23 | Substrate seam exports for session 5 (if elected) and Phase 6+ implementation |

### Reverse trace: spec contract → PRD requirement(s)

| Contract | Satisfies | Verification anchor |
|---|---|---|
| C-OD-01 | R-OD-01 | §1.1 matrix shape + §1.3 per-cell entries + §1.4 EXCLUDED cell rationale + §1.5 cell-identification invariant |
| C-OD-02 | R-OD-01 | §2.1 per-cell backend class + §2.2 per-cell candidate witness columns + §2.3 cell-class commitment invariant |
| C-OD-03 | R-OD-01 | §3.1 committed-at-D6 surfaces + §3.2 deferred surfaces + §3.3 deferral boundary invariant |
| C-OD-04 | R-OD-02 | §4.1 span name format + §4.2 operations enum + §4.3 attribute tiers + §4.4 hierarchy correlation + §4.5 base metric |
| C-OD-05 | R-OD-02 | §5.1 namespace map (15 rows) + §5.2 ingestion-posture invariants + §5.3 F2-12 forward-compatibility note |
| C-OD-06 | R-OD-02 | §6.1 lifecycle event mapping table + §6.2 additive composition + §6.3 F2-12 deferral acknowledgement at retry.attempt |
| C-OD-07 | R-OD-02, R-OD-03 | §7.1 seven-attribute schema + §7.2 quality-of-emission invariants + §7.3 C9↔C10 subscription contract reference |
| C-OD-08 | R-OD-02 | §8.1 collision precedence rule + §8.2 canonical example + §8.3 cross-namespace cardinality discipline |
| C-OD-09 | R-OD-03 | §9.1 per-deployment-surface sampling mode + §9.2 always-sampled exception set + §9.3 sampling-discipline invariants |
| C-OD-10 | R-OD-03 | §10.1 base-rate-sampled set + §10.2 tail-keep-on-classification + §10.3 per-cell base-rate tuning envelope |
| C-OD-11 | R-OD-03 | §11.1 per-cell budget posture + §11.2 cardinality-safe attributes + §11.3 cardinality-prohibited attributes + §11.4 Pattern P1 discipline anchor |
| C-OD-12 | R-OD-04 | §12.1 default-off content attributes + §12.2 default-on structure attributes + §12.3 structure-not-content invariant |
| C-OD-13 | R-OD-04, R-OD-08 | §13.1 per-persona-tier override gradient + §13.2 pre-collector redaction at multi-tenant-compliance + §13.3 cross-deployment monotonic-tightening invariant |
| C-OD-14 | R-OD-05 | §14.1 per-span cost formula + §14.2 sandbox-tier overhead + §14.3 per-sibling rollup at fan-out close + §14.4 idempotency-key join + §14.5 **F2-12 ACTIVE engagement** affected-contract notation |
| C-OD-15 | R-OD-05 | §15.1 cross-family rollup + §15.2 tokenization-version anchor + §15.3 cross-family fallback chain composition reference |
| C-OD-16 | R-OD-05 | §16.1 per-cell dashboard binding signature + §16.2 alerting threshold composition + §16.3 composition with operator-burden eval primitive |
| C-OD-17 | R-OD-06 | §17.1 five-primitive set + §17.2 separate-child-span emission commitment + §17.3 per-cell dashboard binding scaling |
| C-OD-18 | R-OD-06 | §18.1 alignment-floor drift detection + §18.2 drift-detection emission shape + §18.3 eval-vs-runtime-gate distinction |
| C-OD-19 | R-OD-07 | §19.1 in-process collector + §19.2 sqlite ring-buffer + §19.3 TUI trace browser + §19.4 bridging-arc upgrade path |
| C-OD-20 | R-OD-07, R-OD-01 | §20.1 per-cell collector placement matrix + §20.2 async emission + §20.3 per-sandbox-tier reachability + §20.4 composition with C-OD-19 |
| C-OD-21 | R-OD-04, R-OD-08 | §21.1 per-tenant trace separation + §21.2 per-tenant audit ledger storage + §21.3 pre-collector redaction composition + §21.4 cross-tenant aggregation prohibition |
| C-OD-22 | R-OD-08 | §22.1 eight-transition table + §22.2 per-dimension preservation invariants + §22.3 transition planning verification surface + §22.4 excluded-transition rejection |
| C-OD-23 | Cross-axis (all R-OD-*) | §23.1 span schema export + §23.2 cost-attribution export + §23.3 operator-burden eval export + §23.4 bridging-arc traversal export + §23.5 object-storage-tier deferral |

### Bidirectional verification

| Verification check | Result |
|---|---|
| Every R-OD-01 through R-OD-08 has at least one C-OD-* satisfying contract | ✅ PASS (8/8) |
| Every C-OD-01 through C-OD-23 satisfies at least one R-OD-* | ✅ PASS (23/23) |
| No C-OD-* satisfies a phantom PRD requirement | ✅ PASS (every reverse-trace row resolves to R-OD-01 through R-OD-08 or "cross-axis") |
| F2-12 active engagement is contract-bearing at exactly one location (C-OD-14 §14.5) | ✅ PASS |
| Forward-compatibility carry-forward notes at C-OD-05 §5.3 and C-OD-06 §6.3 are non-contract-bearing | ✅ PASS (acknowledgement only; no F2-12 closure-dependent contract authored at those locations) |

---

## §[coherence pass]

Per `Phase_5_Session_4_Session_Prompt.md` §6, pre-emission self-audit pass across five dimensions. All five MUST return ✅ PASS before filing.

### §6.1 Per-contract audit

Each C-OD-* contract audited against eight dimensions: (a) PRD requirement trace; (b) ADR commitment trace; (c) cross-axis citation resolution; (d) no-architecture-introduction; (e) translate-not-restate posture; (f) persona linkage preservation; (g) contract grade (specification-grade precision); (h) deferred-to-implementation discretion enumerated.

| Contract | (a) PRD trace | (b) ADR trace | (c) Cross-axis citation | (d) No-arch-intro | (e) Translate-not-restate | (f) Persona linkage | (g) Grade | (h) Deferred-impl | F2-12 flag |
|---|---|---|---|---|---|---|---|---|---|
| C-OD-01 | R-OD-01 ✓ | D6 §1.1 ✓ | C3 (durability tier) ✓ | ✓ | ✓ | §9, §2, §10.2, §10.4 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-02 | R-OD-01 ✓ | D6 §1.1, §1.9 ✓ | C-OD-01, C-OD-03, C-OD-20 ✓ | ✓ | ✓ | §10.2, §10.4 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-03 | R-OD-01 ✓ | D6 §1.9, §Consequences (b) ✓ | C-OD-02, C-OD-20, C-IS, C-AS, C-CP ✓ | ✓ | ✓ | §10.2 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-04 | R-OD-02 ✓ | D6 §1.2 base layer ✓ | n/a (base layer at D6) | ✓ | ✓ | §10.4 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-05 | R-OD-02 ✓ | D6 §1.2 specialization map ✓ | C-AS-14, C-AS-15, C-AS-16, C-CP-09, C-CP-14, C-CP-20, C-CP-21, C-CP-24, C-IS-05, C-IS-10 ✓ | ✓ | ✓ | §10.2, §10.4 ✓ | Specification ✓ | ✓ | §5.3 forward-compat note |
| C-OD-06 | R-OD-02 ✓ | F3 capability-floor (iv), D6 §1.2 ✓ | C-CP-05, C-CP-09, C-CP-03 ✓ | ✓ | ✓ | §4, §10.4 ✓ | Specification ✓ | ✓ | §6.3 deferral note |
| C-OD-07 | R-OD-02, R-OD-03 ✓ | D6 §1.2.1, §1.3, c9 SKILL.md ✓ | C-CP-03 ✓ | ✓ | ✓ | §4, §10.4 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-08 | R-OD-02 ✓ | D6 §1.2 collision discipline ✓ | OTel GenAI semconv 1.41.0 ✓ | ✓ | ✓ | §10.4 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-09 | R-OD-03 ✓ | D6 §1.3 always-sampled ✓ | C-AS-14, C-AS-15, C-CP-03, C-CP-14, C-CP-20, C-CP-21 ✓ | ✓ | ✓ | §4, §10.4 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-10 | R-OD-03 ✓ | D6 §1.3 base-rate + tail-keep ✓ | C-AS-15, C-AS-14, C-CP-03, C-CP-05, C-AS-04 ✓ | ✓ | ✓ | §6 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-11 | R-OD-03 ✓ | D6 §1.3 cardinality ✓ | Cluster 4 §2.1.5 [HIGH] ✓ | ✓ | ✓ | §11.4, §10.4 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-12 | R-OD-04 ✓ | D6 §1.4 default-off + default-on ✓ | OTel GenAI semconv 1.41.0 Opt-In; c7 SKILL.md ✓ | ✓ | ✓ | §10.4 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-13 | R-OD-04, R-OD-08 ✓ | D6 §1.4 override gradient + pre-collector redaction ✓ | C-IS-06, C-CP-20 ✓ | ✓ | ✓ | §2, §10.4, §11.6/7 ✓ | Specification ✓ | ✓ | n/a |
| **C-OD-14** | **R-OD-05 ✓** | **D6 §1.5 cost-attribution ✓** | **C-IS-05, C-IS-10, C-AS-15, C-CP-14, C-CP-24 ✓** | **✓** | **✓** | **§6, §10.2, §8.5 ✓** | **Specification ✓** | **✓** | **§14.5 F2-12 ACTIVE engagement affected-contract notation** |
| C-OD-15 | R-OD-05 ✓ | D6 §1.5 cross-family + tokenizer ✓ | c7 SKILL.md, F1 v1.2 ✓ | ✓ | ✓ | §10.2 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-16 | R-OD-05 ✓ | D6 §1.5 per-cell dashboard binding ✓ | n/a (composition with C-OD-14, C-OD-10) | ✓ | ✓ | §6, §10.2 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-17 | R-OD-06 ✓ | D6 §1.6 operator-burden eval primitive ✓ | C-CP-24, C-CP-20, C-AS-15 ✓ | ✓ | ✓ | §4, §10.2, §10.4 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-18 | R-OD-06 ✓ | D6 §1.6 drift detection + eval-vs-runtime-gate ✓ | C-CP-21, c5 SKILL.md, c8 SKILL.md ✓ | ✓ | ✓ | §4 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-19 | R-OD-07 ✓ | D6 §1.7 local-first OTLP collector ✓ | C-IS-10 §10.5 ✓ | ✓ | ✓ | §9, §2, §10.4 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-20 | R-OD-07, R-OD-01 ✓ | D6 §1.7 + F4 §Consequences (b)(iv) ✓ | C-AS-01, C-AS-15 ✓ | ✓ | ✓ | §9, §10.4 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-21 | R-OD-04, R-OD-08 ✓ | D6 §1.8 multi-tenant tenant-isolation ✓ | C-IS-06, C-IS-10 §10.3, C-CP-20 ✓ | ✓ | ✓ | §10.4, §11.10 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-22 | R-OD-08 ✓ | D6 §1.1 + §1.2 + §1.3 + §1.4; D5 §1.5.2; D2 §1.6; ADD §5.3.1 ✓ | C-AS-12, C-AS-15, C-CP-19, C-CP-24 ✓ | ✓ | ✓ | §2, §10.4, §11.10 ✓ | Specification ✓ | ✓ | n/a |
| C-OD-23 | All R-OD-* (cross-axis surface) ✓ | D6 §Consequences (a), (f), (g) ✓ | C-AS-12, C-AS-14, C-AS-15, C-CP-09, C-CP-14, C-CP-19, C-CP-20, C-CP-21, C-CP-24, C-IS-05, C-IS-10, ADD §5.2.1, §5.2.2, §5.2.3, §5.3, §5.3.1 ✓ | ✓ | ✓ | §10.2, §10.4 ✓ | Specification ✓ | ✓ | §23.2 F2-12 active engagement export (D6 closure half) |

**§6.1 Per-contract audit result: ✅ PASS** — 23/23 contracts pass all eight audit dimensions; F2-12 active engagement contract-bearing at exactly one location (C-OD-14 §14.5); forward-compatibility / deferral acknowledgements at C-OD-05 §5.3, C-OD-06 §6.3 are non-contract-bearing notes.

### §6.2 PRD-requirement-to-spec sub-matrix audit

Per §[traceability] forward + reverse trace verification:

| Audit check | Result |
|---|---|
| Every R-OD-01 through R-OD-08 has at least one C-OD-* satisfying contract | ✅ PASS (8/8) |
| Every C-OD-01 through C-OD-23 satisfies at least one R-OD-* | ✅ PASS (23/23) |
| No phantom PRD requirements introduced | ✅ PASS |
| Composition note granularity is contract-precise | ✅ PASS |
| Bidirectional trace verification confirms zero gaps | ✅ PASS |

**§6.2 PRD-requirement-to-spec sub-matrix audit result: ✅ PASS**

### §6.3 Front-matter audit

| Audit check | Result |
|---|---|
| Status block populated (8 fields) | ✅ PASS |
| Axis declaration with rationale (3 bullets) | ✅ PASS |
| Axis-grounding note (1 D-ADR primary + 10 secondary axes named) | ✅ PASS |
| PRD requirement scope table (8 rows for R-OD-01 through R-OD-08) | ✅ PASS |
| ADR scope table (D6 v1.1 primary + 10 secondary at expected versions) | ✅ PASS |
| Cross-axis citation substrate table (3 cross-axis specs with specific contract numbers) | ✅ PASS |
| Persona-linkage substrate table (8 persona anchor sections mapped) | ✅ PASS |
| Scope and out-of-scope table (12 rows total covering in-scope / out-of-scope split with F2-12 explicit in-scope row) | ✅ PASS |

**§6.3 Front-matter audit result: ✅ PASS**

### §6.4 Carry-forward inheritance audit

| Audit check | Result |
|---|---|
| All PRD §[carry-forwards] entries (2: F2-12 + Workflow §7) inherited to spec §[carry-forwards] | ✅ PASS (2/2) |
| Session-1/2/3 spec §[carry-forwards] inheritance preserved | ✅ PASS |
| F2-12 active engagement marker on [CF-1] | ✅ PASS (per session prompt §5.4 [CF-1] authoring approach (iii)) |
| F2-12 affected-contract notation at C-OD-14 §14.5 | ✅ PASS |
| Workflow §7 propagation [CF-2] marked deferred-acknowledged not blocking | ✅ PASS |
| No carry-forwards dropped vs PRD list | ✅ PASS (2/2 inherited) |

**§6.4 Carry-forward inheritance audit result: ✅ PASS**

### §6.5 V3 deference audit

Per `Phase_5_Session_4_Session_Prompt.md` §6.5 — five V3 attack vocabulary patterns:

| V3 attack pattern | Defense | Result |
|---|---|---|
| **Silent grounding collapse** | Every contract anchored to specific PRD requirement row + specific ADR section + specific cross-axis citation row (verified at §6.1 per-contract audit dimensions (a), (b), (c)) | ✅ PASS |
| **Silent scope narrowing** | Every R-OD-* covered by at least one C-OD-*; every C-OD-* maps to at least one R-OD-* (verified at §6.2 PRD-requirement-to-spec sub-matrix audit) | ✅ PASS |
| **Fabricated citations** | All cross-axis citations resolve to actual session-1/2/3 spec contract numbers (C-IS-05, C-IS-06, C-IS-07, C-IS-10 / C-AS-01, C-AS-04, C-AS-08, C-AS-11, C-AS-12, C-AS-14, C-AS-15, C-AS-16 / C-CP-03, C-CP-05, C-CP-09, C-CP-14, C-CP-19, C-CP-20, C-CP-21, C-CP-24); ADR citations resolve to actual ADR section numbers (D6 §1.1 through §1.9 + §Consequences (a)/(b)/(f)/(g); D5 v1.3 §1.4.1, §1.5.2, §1.8, §1.10.1; D4 v1.1 §1.9; D3 v1.1 §1.5, §1.8.1; D2 v1.1 §1.6, §1.7.1, §1.8; D1 v1.1 §1.1.1; F4 v1.1 §Consequences (b)(iv); F3 v1.1 capability-floor (iv); F1 v1.2 §Decision; F2 v1.2 state-ledger; F5 v1.1) | ✅ PASS |
| **Missing uncertainty** | F2-12 active engagement explicitly flagged at C-OD-14 §14.5 as the affected contract; three deferred surfaces enumerated; MODERATE-tag annotation on the extended-thinking output token pricing line at §14.1 per primary-source non-verification | ✅ PASS |
| **Framing contamination** | Spec authors at the current D6 v1.1 commitment level (no PRD revision; no ADR revision; no ADD revision); architecture not introduced (all contracts translate not restate); persona linkage preserved (every contract maps to ≥1 persona section); cross-axis citations resolve at exactly the source declaration sites | ✅ PASS |
| **Context bleed** | Specification authoring discipline preserves source-as-authoritative-declarer rule per C-OD-05 §5.2 (Pattern P1 mechanical-alignment discipline anchor); no namespace re-declaration at this spec; no rename of source-axis attribute names | ✅ PASS |

**§6.5 V3 deference audit result: ✅ PASS**

### §6 Coherence pass result summary

| Audit dimension | Result |
|---|---|
| §6.1 Per-contract audit | ✅ PASS (23/23) |
| §6.2 PRD-requirement-to-spec sub-matrix audit | ✅ PASS |
| §6.3 Front-matter audit | ✅ PASS |
| §6.4 Carry-forward inheritance audit | ✅ PASS |
| §6.5 V3 deference audit | ✅ PASS |

**§6 Coherence pass overall result: ✅ PASS** — all five audit dimensions clear; spec ready for filing.

---

## Filing footer

| Field | Value |
|---|---|
| Spec name | `Spec_Operational_Discipline_v1.md` |
| Phase | 5 — specification authoring (session 4 of 4–6) |
| Axis | Operational Discipline |
| ADR primary | D6 v1.1 |
| ADR secondary (citation only) | F1 v1.2, F2 v1.2, F3 v1.1, F4 v1.1, F5 v1.1, D1 v1.1, D2 v1.1, D3 v1.1, D4 v1.1, D5 v1.3 |
| Contracts authored | C-OD-01 through C-OD-23 (23 contracts) |
| PRD requirements satisfied | R-OD-01 through R-OD-08 (8 requirements) |
| Cross-axis citations | C-IS-05, C-IS-06, C-IS-07, C-IS-10; C-AS-01, C-AS-04, C-AS-08, C-AS-11, C-AS-12, C-AS-14, C-AS-15, C-AS-16; C-CP-03, C-CP-05, C-CP-09, C-CP-14, C-CP-19, C-CP-20, C-CP-21, C-CP-24 |
| Carry-forwards | [CF-1] F2-12 (ACTIVE engagement at C-OD-14 §14.5) + [CF-2] Workflow §7 (deferred-acknowledged, not blocking) |
| Coherence pass | ✅ PASS (all 5 audit dimensions) |
| ODs applied | OD-5-1.A + OD-5-2.A (Operational Discipline axis selected per handoff §3.1 recommendation) + OD-5-3.A + OD-5-4.A |
| Filing destination | `/mnt/user-data/outputs/Spec_Operational_Discipline_v1.md` |
| P5-CK status | Pre-aggregate; aggregate P5-CK at Phase 5 close per OD-5-4.A |
| Date | 2026-05-13 |

**Filing authorized.** Coherence pass returns ✅ PASS at all five audit dimensions; spec ready for `/mnt/user-data/outputs/` deposition.

---

[END `Spec_Operational_Discipline_v1.md`]
