# harness-od/CLAUDE.md — Operational Discipline (OD) Axis

*Per-axis subdirectory guidance for the OD axis. Loaded by Claude Code at session startup alongside workspace root `CLAUDE.md`. Canonical pointer to design-phase OD-axis artifacts.*

---

## 1. Axis identity + scope boundary

### 1.1 Axis identity

The Operational Discipline (OD) axis owns **observability + cost + audit + HITL primitive**: HITL invocation primitive (4-response palette canonical schema), audit ledger schema (hash-chain integrity composition), cost attribution 5-step chain (per-attempt + idempotency-key join + hash-chain composition + replay-aware dedup + cause_attribution invariance), validator fail catalog (medium-cardinality cause_attribution + 5-class fail-class taxonomy), 15-namespace OTel observability ingestion map (`anthropic.*` / `mcp.*` / `skill.*` / `managed_agents.*` / `sandbox.*` / `hitl.*` / `topology.*` / `subagent.*` / `engine.*` / `audit.*` / `validator.fail.*` / `files.*` / `memory.*` / `harness.breaker.*` / `provider_discriminator.*`), F3 capability-floor lifecycle event mapping, in-process OTLP collector + sampling discipline.

OD posture per `Cross_Axis_Composition_Document_v2_1.md` §2.1 (baseline) + `Cross_Axis_Composition_Document_v2_9.md` §2.3.7 + §2.4 (v2.4 → v2.9 delta chain): **consumer-most-downstream axis** — 0 outbound cross-axis edges to other axes (preserved invariant); **27 outbound edges per §2.4 axis-attribution** (6 → IS at CXA v2.1 baseline / 4 at OD plan v2.6 per C3-15; 10 → AS; 12 → CP; +1 OD-axis-attributed seam at the §2.3.7 CP→OD bucket = row 8 cost-attribution audit-write seam, U-OD-41 producer + U-OD-00 consumer, NEW v2.9 per namespace-ownership convention because `cost.*` is OD-axis-owned); **8 inbound edges from CP at U-OD-00** per CXA v2.9 §2.3.7 (bucket-membership growth: row 1 U-CP-28 audit-ledger entry composition v2.4 + rows 2-7 v2.6 composer-arc absorption [ValidatorFramework + PauseResumeProtocol + PerServerTrustEvaluator + HITL webhook delivery + HITL operator-burden + one prior] + row 8 cost-attribution audit-write seam v2.9; first cross-axis back-edge family — `[[class_3_tension_cxa_v2_4_axis_back_edge]]`). OD terminates the axis-level *downstream* dependency graph (no edges to other axes); the v2.4 → v2.9 bucket growth is acknowledged at U-OD-00 carrier consumption (rows 1-7) + U-OD-41 producer (row 8) and does not alter the 0-outbound-to-other-axes invariant. §2.1-vs-§2.4 attribution divergence at row 8 (counted under CP→OD bucket-membership at §2.1 + §2.3.7 = 8 but attributed to OD outbound at §2.4 = 27) is the natural consequence of the established v2.6 §2.4 namespace-ownership convention preserved at v2.9 per CXA v2.9 §0.3 + §0.7(ii).

### 1.2 Spec + plan authority

| Artifact | Version | Role |
|---|---|---|
| `Spec_Operational_Discipline_v1_4.md` | v1.4 (delta over v1.3; v1.4 formalizes the C-OD-20 §20.1 `CollectorPlacement` 7-value enum + grows the §1.2 enum 6→7 — FF-2 resolution) | Contract authority — 23 contracts C-OD-01 through C-OD-23 |
| `Implementation_Plan_Operational_Discipline_v2_11.md` | v2.11 (delta chain over v2.10/v2.9/v2.8/v2.7/v2.6; v2.8 = five Class 1 defects + F3 pinning; v2.9 = FF-2 U-OD-28; v2.10 = FF-3 U-OD-29 `SandboxTier` conformance; v2.11 = 7c-prereq Form A — OD-outbound cross-axis placeholder carrier IDs resolved) | Execution authority — 35 atomic units across 8 clusters (+ U-OD-00 pre-cluster) and 10 topological levels (L0–L9) |

### 1.3 Scope inclusion

| Surface | Carrier units | Spec contract |
|---|---|---|
| Foundational cost-attribution + telemetry primitives | U-OD-01, U-OD-04 (L0 anchors) | C-OD-01 + C-OD-04 |
| HITL primitive — 4-response palette (4 canonical event names: `hitl.gate.evaluated` / `hitl.invocation.opened` / `hitl.invocation.responded` / `hitl.invocation.timed_out`) | U-OD-NN (Cluster 1) | C-OD-05 row 6 |
| 15-namespace ingestion map | U-OD-NN (Cluster 2–3) | C-OD-05 §5.1 |
| F3 capability-floor lifecycle event mapping (`workflow.start` / `step.boundary` / `fallback.triggered` / `retry.attempt` / `breaker.tripped` / `lease.acquired` / `lease.released` / `workflow.resumed` — the eight event classes per spec C-OD-06 §6.1, canonical; pinned at OD plan v2.8 §0.5) | U-OD-08 (Cluster 2) | C-OD-06 §6.1 |
| 7-attribute `harness.breaker.*` canonical schema | U-OD-NN (Cluster 3) | C-OD-07 §7.1 |
| Cost attribution 5-step chain | U-OD-14 through U-OD-17 | C-OD-12 + C-OD-13 |
| Audit-ledger schema + 8-field SHA-256 composition + field-ordering | U-OD-20 | C-OD-14 §14.5.1 |
| 8-row audit-ledger enumeration | U-OD-20 | C-OD-14 §14.5.2 |
| Validator fail catalog (cause_attribution) | U-OD-NN (Cluster 6) | C-OD-NN |
| In-process OTLP collector + sampling discipline | U-OD-NN (Cluster 7) | C-OD-NN |
| OD substrate seam exports manifest (terminal aggregate exporter) | U-OD-34 | C-OD-23 |

### 1.4 Scope exclusion

| NOT OD | Owning axis / source |
|---|---|
| Path-class registry, state ledger, hash-chain *implementation* (canonical at IS), JSONL composition | IS — `harness-is/CLAUDE.md`. OD consumes IS hash-chain primitives via U-IS-08/09/10 cross-axis edges |
| SandboxTier enum, tool contract schemas, sandbox observability emission (canonical at AS) | AS — `harness-as/CLAUDE.md`. OD ingests `sandbox.*` namespace per D6 §1.2 |
| Multi-LLM routing, retry mechanism implementation, fallback chain composition, workflow lifecycle, topology pattern, HITL placement decision logic, sub-agent handoff schemas | CP — `harness-cp/CLAUDE.md`. OD ingests CP-emitted namespaces (`routing.*` / `fallback.*` / `retry.*` / `engine.*` / `topology.*` / `subagent.*` / `hitl.*` / `harness.breaker.*`) |

**D6 ingestion pattern.** OD canonical authority for: (a) namespace map (C-OD-05 15-row enumeration); (b) lifecycle event mapping (C-OD-06); (c) `harness.breaker.*` 7-attribute schema (C-OD-07 §7.1); (d) cost attribution chain (C-OD-12 + C-OD-13). CP/AS emit per OD's canonical attribute set. Composition site at OD spec; emission site at CP/AS plans.

---

## 2. Per-axis canonical artifacts

### 2.1 Anchoring ADRs

| ADR | Version | Role |
|---|---|---|
| ADR-D1 | v1.2 | Engine + replay (replay-trace-emission contract; F2-12 closure) |
| ADR-D4 | v1.1 | Workload classes (per-workload sampling discipline) |
| ADR-D5 | v1.3 | HITL palette canonical (4-event-name set per §1.8) + cross-deployment monotonicity |
| ADR-D6 | v1.2 | Observability + cost-attribution (12-namespace span schema; canonical) |
| ADR-F2 | v1.2 | State ledger substrate (hash-chain integrity composition consumed at audit) |
| ADR-F3 | v1.1 | Engine event history (lifecycle event categorization) |

ADD attestation: `Architectural_Design_Document_v1_3.md` v1.3.

### 2.2 Cross-axis edge inventory (CXA v2.1 baseline + v2.4 → v2.9 CP→OD bucket growth)

OD is consumer-most-downstream. Pre-v2.4: all OD-direction cross-axis edges were **outbound consumer edges**. At v2.4 (per U-RT-59 Fork 2 Path D landing), the §2.3.7 CP→OD bucket opened with its first row (U-CP-28 → U-OD-00). At v2.6 (composer-arc absorption), rows 2-7 added (6 new typed seams sharing the `cp_audit_to_od_audit` converter via distinct F2 action_id prefixes). At v2.9 (cost-attribution audit-write seam landing per `.harness/Remaining_Work_Closure_Arc_Handoff_v1.md` §6), row 8 added (U-OD-41 producer + `cost:` action_id prefix discriminator). The 0-outbound-to-other-axes invariant is preserved across the v2.4 → v2.9 growth; row 8 is OD-axis-attributed at §2.4 per namespace-ownership convention but its endpoints are still both OD-internal (U-OD-41 → U-OD-00 routed through the shared CXA converter):

| Edge direction | Edges | Source artifact |
|---|---|---|
| OD → IS (outbound consumer) | 6 (CXA v2.1 baseline) / 4 (OD plan v2.6 §4.5.1 per C3-15 Path (i-refined) deletions) | `Cross_Axis_Composition_Document_v2_1.md` §2.3.5; `Implementation_Plan_Operational_Discipline_v2_6.md` §0.7 + §4.5.1 |
| OD → AS (outbound consumer) | 10 | `Cross_Axis_Composition_Document_v2_1.md` §2.3.6 |
| OD → CP (outbound consumer) | 12 | `Cross_Axis_Composition_Document_v2_1.md` §2.3.3 |
| **CP → OD (bucket-membership)** | **8** | `Cross_Axis_Composition_Document_v2_9.md` §2.3.7 — 8 genuine-typed-seams at the shared `cp_audit_to_od_audit` converter (homed at `harness-cxa/src/harness_cxa/cp_audit_conversion.py`). Row 1 (U-CP-28 → U-OD-00 audit-ledger entry composition, NEW v2.4) + rows 2-7 (composer-arc absorption: ValidatorFramework + PauseResumeProtocol + PerServerTrustEvaluator + HITL webhook delivery + HITL operator-burden + one prior, NEW v2.6) + row 8 (U-OD-41 → U-OD-00 cost-attribution audit-write seam via `cost:` action_id prefix, NEW v2.9; cite forward to OD spec v1.10 §C-OD-26.6 CostRecordAuditPayload). §2.4 axis-attribution: rows 1-7 CP-axis-attributed (CP outbound 62); row 8 OD-axis-attributed (OD outbound 27 per namespace-ownership convention because `cost.*` is OD-owned). Per-row F2 action_id prefix discriminator at OD audit-trace consumers per CXA v2.9 §0.3 (`dispatch:` / `hitl:` / `hitl_webhook:` / `operator_burden:` / `validator:` / `pause:` / `resume:` / `mcp_trust:` / `cost:`). `[[class_3_tension_cxa_v2_4_axis_back_edge]]` |
| **OD-axis-attributed share of CP→OD bucket** | **1 (row 8)** | Per §2.4 namespace-ownership convention preserved at v2.9 §0.3 + §0.7(ii); row 8 counts toward OD outbound = 27 (was 26 at v2.6); rows 1-7 count toward CP outbound = 62. §2.1-vs-§2.4 attribution divergence at row 8 is the natural consequence of the established convention, not a new exception. |
| **OD outbound to other axes (downstream)** | **0** | OD terminates the axis-level *downstream* dependency graph (invariant preserved at v2.4 → v2.9; all 8 CP→OD bucket rows are within OD endpoints — U-OD-00 or U-OD-41 — so no actual edge to another axis). |

CXA-OD-IS-EDGE-DRIFT Class 3 informational item: CXA v2.1 §2.3.5 enumerates 6 edges (baseline at OD plan v2.3); OD plan v2.6 §4.5.1 enumerates 4 (rows 2 + 3 deleted as OD-internal mis-routed; rows 4 + 5 remapped to canonical IS contracts). Routing: future composition-document revision pass; non-blocking.

### 2.3 OD-internal cross-cluster dependencies (NOT cross-axis)

Per `Implementation_Plan_Operational_Discipline_v2_6.md` §0.7 + §0.9: sqlite substrate residence + ring-buffer eviction are OD-internal concerns (NOT cross-axis edges). C3-15 closure formalized this distinction via Path (i-refined) deletions at v2.6 §4.5.1. OD-internal cross-cluster compositions are within-axis dependencies; cross-axis enumeration at §4.5 covers cross-axis only.

---

## 3. Topological entry-points (Level 0)

Per `Implementation_Plan_Operational_Discipline_v1.md` §0.2 plan-level invariants (preserved at v2.6):

| L0 unit | Scope | Cluster |
|---|---|---|
| U-OD-00 | OD-local audit-ledger composition-type carrier (added at OD plan v2.6 per revision pass R5) | pre-cluster |
| U-OD-01 | Foundational cost-attribution primitive | 1 |
| U-OD-04 | Foundational telemetry primitive | 1 |

**3 L0 units; in-degree 0.** Phase 7 sub-phase 7b OD-axis-stream execution begins from these entry-points.

### 3.1 OD plan-level invariants (preserved at v2.6)

| Invariant | Value |
|---|---|
| Atomic units | 35 (U-OD-00, U-OD-01 through U-OD-34) — U-OD-00 added at v2.6 per R5 |
| Clusters | 8 (+ U-OD-00 pre-cluster) |
| Spec contracts covered | 23 of 23 (C-OD-01 through C-OD-23) |
| PRD requirements satisfied | 8 of 8 (R-OD-01 through R-OD-08) plus cross-axis surface |
| Within-axis directed edges | 102 (v2.6: +2 M-2 hidden-coupling edges) |
| Cross-axis directed edges | 26 (IS=4; AS=10; CP=12) per OD plan v2.6 §4.5.1 |
| Cross-axis-touching units | 16 of 35 |
| Foundational anchors (L0) | 3 (U-OD-00, U-OD-01, U-OD-04) |
| Terminal units (L9) | 2 (U-OD-31, U-OD-34) |
| Level depth | 10 (L0–L9) |
| F2-12 ACTIVE contract-bearing sites | 1 (U-OD-20) — CLOSED at v2.2 cascade |
| F2-12 carry-forward inheritance sites | 1 (U-OD-34) — CLOSED at v2.2 cascade |

### 3.2 Coverage matrix verification

Per OD plan §4 (preserved at v2.6): 23 of 23 contracts covered by ≥1 unit; no coverage gaps. Coverage matrix per-axis-only per OD-S4-2.A.

---

## 4. Substitution + anti-leakage surface

### 4.1 OD-axis substitutions (8 entries)

Per `Phase_7_Meta_Architecture_v1.md` §5.5. H_E classification per §4.4.4 — **OD is the most-absent axis**:

| H_T primitive class | Count | Representative primitives |
|---|---|---|
| ✗ absent | 7 | H_T-OD-1 (deferral envelope — `ToolSearch` ≠ deferral envelope, categorical mismatch); H_T-OD-2 (OTel SDK injection — H_E telemetry closed); H_T-OD-3 (sampling-discipline surface); H_T-OD-4 (SpanProcessor injection); H_T-OD-6 (in-process OTLP collector); H_T-OD-7 (preservation discipline); H_T-OD-8 (authoring artifact) |
| ~ partial | 1 | H_T-OD-5 (`/cost` + `--max-budget-usd` coarse; not 5-step chain) |
| ✓ native | 0 | None |

**OD is the most distinct H_E ↔ H_T boundary.** All OD substitutions retire at OD-axis unit landings; no native H_E carrier covers any OD primitive in full. The substrate-boundary discipline (X-AL-1: H_E ↔ H_T boundary at MCP server process) is canonical at OD axis per OD-AL-3.

Full per-substitution bounded-scope + retirement criterion at Meta-Architecture §5.5.

**Retirement status (post 7d batch 11 doc-hygiene-pass refresh, 2026-05-23).** Per v2 ledger `.harness/phase-7d-retirement-ledger-v2.md` §6 + cumulative batch records `.harness/phase-7d-retirement-events-batch-{1..11}.md` under operator-ratified runtime-only substitution-site reading + line-33 strict-reading discipline. Compound-irrelevance pattern from earlier OD-axis blockages (zero spans emitted → telemetry / cost / sampler / audit primitives starved of input) has materially shifted post-batch-2 with significant span-emission landings since 2026-05-20: cluster 4-OD-A (workflow.envelope) + cluster 4-OD-C (rate-table substrate) + cluster 4-OD-D (cost-attribution at LLM dispatch site) + cluster 10-CP-A/B/C/D span schemas (validator.*, mcp.trust.*, hitl.webhook.*, hitl.operator_burden.*) — see §"Span-emission substrate activity" below. Forward-only ledger discipline preserved.

| Substitution | Status | Source |
|---|---|---|
| H_T-OD-1 (deferral envelope) | STILL-BOUNDED | No `deferral_envelope` import in `harness-runtime/`; scope deferrals remain `CLAUDE.md`-prose convention at runtime |
| H_T-OD-2 (OTel SDK base + GenAI semconv) | **RETIRED** 2026-05-20 (batch 2, U-RT-52 close arc) | OTel SDK base wired (`tracer_provider.py`); GenAI semconv 1.41.0 binding LIVE at `lifecycle/llm_dispatch.py:RuntimeLLMDispatcher.dispatch` per Spec v1.3 §14.5 C-RT-15. Runtime emits `gen_ai.system` + `gen_ai.request.model` + `gen_ai.usage.{input,output}_tokens` + `gen_ai.response.id` per provider. RETIRED status strengthened by post-batch-2 namespace activity: workflow.envelope (U-OD-35/36/37, cluster 4-OD-A) + validator.* (U-OD-50) + mcp.trust.* (U-OD-52) + hitl.webhook.* (U-OD-53) + hitl.operator_burden.* (U-OD-54) all emit through the same TracerProvider substrate. CXA-5 cascade closed at batch 3 (per workspace-CP CLAUDE.md §4.1 + ledger-v2 §7) |
| H_T-OD-3 (Composite Sampler) | STILL-BOUNDED | Stock `ParentBased(ALWAYS_ON)`, not project-authored composite head/tail. NOTE: compound-irrelevance lifted post-batch-2 (spans now actively emit per H_T-OD-2 namespace activity) — sampler-discipline gap now materially observable, no longer compound-inactive |
| H_T-OD-4 (Pre-Collector redaction SpanProcessor) | STILL-BOUNDED | Stock `BatchSpanProcessor`; zero redaction references. NOTE: compound-irrelevance lifted post-batch-2 (spans actively emit) — redaction-discipline gap now materially observable, no longer compound-inactive |
| H_T-OD-5 (Cost-attribution 5-step chain) | **PARTIAL** (batch 11 doc-hygiene transition) | Cost-attribution wired at LLM dispatch site via U-OD-38 landing (`7104fd7`, cluster 4-OD-D commit 1/2): production LLM-dispatch path invokes `resolve_for(RATE_TABLE_V1, provider, model)` per `[[fork-price-table-ref-substitution-retirement]]` (PRICE_TABLE_REF RETIRED). 5-step chain operational at 1 of 4 dispatch surfaces (LLM); **tool / validator / webhook dispatch sites cross-axis-blocked**: U-OD-39 on U-RT-67/U-RT-69 (tool-invocation composer); U-OD-40 on U-CP-60 (validator framework — landed, downstream wiring not yet routed); U-OD-41 on U-CP-72 (audit-write seam, PARTIAL-LAND 6/8 per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]`). Audit-ledger wiring residual per `[[fork-cost-record-audit-ledger-wiring-residual]]` (CXA v2.9 amendment owed) |
| H_T-OD-6 (Local-first OTLP ingestion) | PARTIAL | Collector daemon + ring buffer wired; sqlite write path deferred (U-RT-30 PARTIAL-LAND, AC #2 STRUCK); TUI absent. NOTE: compound-irrelevance lifted post-batch-2 (spans actively emit) — collector now has actual ingest pressure; sqlite write site + TUI gaps materially observable |
| H_T-OD-7 (Preservation invariants 5-dimension) | STILL-BOUNDED | Library carrier only; no runtime enforcement loop |
| H_T-OD-8 (aggregate manifest + Stage 3b inversion) | RETIRED (authoring close, v1 §1) | Authoring-only |

**OD-axis cumulative post-batch-11 (2026-05-23):** **2 / 8 RETIRED (25%, includes OD-8 authoring-close + OD-2 GenAI binding)** + **2 / 8 PARTIAL (25%, OD-5 cost-attribution LLM-only + OD-6 collector daemon)** + **4 / 8 STILL-BOUNDED (50%, OD-1 + OD-3 + OD-4 + OD-7)**. Pipeline advanced (R+RR+P): **4/8 = 50.0%** (up from 3/8 = 37.5% post-batch-2).

**Span-emission substrate activity since 2026-05-20 (cluster 4-OD-A/C/D + 10-CP-A/B/C/D landings):**

| Namespace | Carrier unit + commit | Status at HEAD |
|---|---|---|
| `workflow.envelope` (12 attrs) | U-OD-35 + U-OD-36 + U-OD-37 (cluster 4-OD-A: `1efc5ea` + `1dd098e` + `461ba5e`) | Span opened at workflow_driver entry post-drain-check; 12 attrs populated; deterministic close + exception handling + fresh-envelope-on-resumption per spec v1.8 §C-OD-25 |
| `validator.*` (11 attrs at C-OD-29) | U-OD-50 (cluster 10-CP-A: `b70e9a6`) | Schema + ValidatorEscalationAuditPayload landed; emission tied to ctx.validator_framework operator-opt-in branch at workflow_driver.py:670 (RETIRE-READY per H_T-CP-21 batch-11) |
| `mcp.trust.*` (5 attrs) | U-OD-52 (cluster 10-CP-C: `257273d`) | Schema + TrustEvaluationAuditPayload landed; emission tied to ctx.per_server_trust_evaluator at MCP-client production dispatch (RETIRE-READY per H_T-CP-18 batch-10) |
| `hitl.webhook.*` | U-OD-53 (cluster 4-OD-E: `0aed0ac`) | Schema + WebhookDeliveryAuditPayload landed; operator-config-gated (mirror of CP-18 / CP-21 operator-opt-in pattern) |
| `hitl.operator_burden.*` | U-OD-54 (cluster 4-OD-E: `128ab4f`) | Schema + OperatorBurdenAuditPayload landed |
| Rate-table substrate (4 frozen Pydantic v2 models + resolver + Decimal serialization) | U-OD-46 + U-OD-47 + U-OD-48 + U-OD-49 (cluster 4-OD-C: `1daeda0` + `2e025e1` + `4899792` + `404fef7`) | PRICE_TABLE_REF canonical schema + v1 default rate-table substrate (anthropic + openai + ollama) + provider-then-model resolver + CP-FAIL-RATE-TABLE-MISSING typed error + Decimal string-serialization at OTel attribute boundary |

**PARTIAL → RETIRE-READY gates (OD-5 + OD-6):**

- **OD-5 (cost-attribution):** gate on U-OD-39/40/41 unblocks (tool/validator/webhook cost-attribution at dispatch sites) — currently cross-axis-blocked on U-RT-67 / U-RT-69 (tool-invocation composer) + U-CP-72 audit-write seam un-STRIKE (PauseResumeAuditPayload + CostRecordAuditPayload). 3-arc cascade per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §6.
- **OD-6 (local-first OTLP ingestion):** gate on sqlite write site re-eligibility (U-RT-30 AC #2 un-STRIKE) + TUI substrate authoring. Operator-discretion timing.

**STILL-BOUNDED → PARTIAL gates (OD-1 + OD-3 + OD-4 + OD-7):**

- **OD-1 (deferral envelope):** gate on runtime composer importing `deferral_envelope` + scope-deferral typed primitive replacing `CLAUDE.md`-prose convention at runtime.
- **OD-3 (Composite Sampler):** gate on project-authored composite head/tail sampler subclass + integration at materialize_sampler_stage (post-batch-2 span-emission activity makes this materially relevant).
- **OD-4 (Pre-Collector redaction SpanProcessor):** gate on `RedactionSpanProcessor` authoring + integration at materialize_span_processor_stage upstream of OTLPSpanExporter (post-batch-2 span-emission activity makes this materially relevant).
- **OD-7 (Preservation invariants):** gate on runtime enforcement loop invoking `per_dimension_preservation_invariants` against runtime ledger entries.

### 4.2 OD-axis anti-leakage rules (3 entries)

Per `Phase_7_Meta_Architecture_v1.md` §7.5:

| Rule | Statement | Anti-pattern foreclosed |
|---|---|---|
| OD-AL-1 | H_E telemetry (internal Claude Code analytics, closed surface) ≠ harness observability substrate (instruments the harness for harness operators) | Assuming H_E telemetry covers H_T's `sandbox.*` / `mcp.*` / `skill.*` / `topology.*` / `subagent.*` / `engine.*` / `audit.*` / `validator.fail.*` / `harness.breaker.*` namespace emission |
| OD-AL-2 | H_E `/cost` (session-grain coarse cost) ≠ H_T cost-attribution 5-step chain (per-attempt + idempotency-key join + hash-chain integrity composition + replay-aware dedup + cause_attribution invariance) | Authoring U-OD-17 → U-OD-22 to delegate cost computation to `/cost`-derived data |
| OD-AL-3 | All OTel emission during 7a happens at MCP server boundary (H_T-authored code). H_E does not participate in OTel emission. Boundary is load-bearing — prevents H_E internal telemetry from contaminating H_T trace schemas | Attempting to inject OTel SpanProcessors into H_E's emission path; constructing H_T spans by parsing H_E session logs |

Cross-cutting rules X-AL-1 / X-AL-2 / X-AL-3 (Meta-Architecture §7.7) also bind OD-axis implementation. **OD-AL-3 is the canonical concretization of X-AL-1** — substrate-boundary at MCP server process is enforced at OD via "no H_E participation in OTel emission" rather than convention.

---

## 5. Back-flow channels

Axis-specific design defects route per `Project_Workflow_v1_8.md` §2.7.6 + workspace root `CLAUDE.md` §4.3.

### 5.1 Class 1 routing by defect locus

| Defect locus | Class 1 routing |
|---|---|
| OD plan v2.6 atomic unit signature defect | Phase 6 plan revision-pass at design-phase workspace |
| OD spec v1.3 contract defect (C-OD-NN under-specifies the surface; spec inconsistent with ADR) | Phase 5 spec revision-pass at design-phase workspace |
| ADR-D1 v1.2 / D4 v1.1 / D5 v1.3 / D6 v1.2 / F2 v1.2 / F3 v1.1 anchor decision defect | Phase 3a/3b ADR revision via council convening |
| ADD v1.3 attestation mismatch with OD spec v1.3 | Phase 3d ADD revision |
| CXA v2.1 §2.3.3 (OD→CP) / §2.3.5 (OD→IS) / §2.3.6 (OD→AS) edge defect | Phase 6 CXA revision-pass at design-phase workspace |
| OD substrate seam (U-OD-34 manifest) defect; cascade to consumer-side plans (none — OD is consumer-most-downstream) | Phase 6 OD plan revision-pass |

### 5.2 Open carry-forwards at OD axis entry

| Carry-forward | Status | Routing |
|---|---|---|
| F2-12 cascade Step 6b (OD plan layer) | CLOSED at v2.2; preserved through v2.6 per `F2-12_Closure_Declaration.md` | No action |
| F3-02 IS-axis revision (U-OD-20 acceptance #11 `Depends on` placeholder `U-IS-NN` → canonical `U-IS-12`) | CLOSED at v2.4 §0.7 (Form A — citation precision); preserved at v2.6 | No action |
| C3-15 Path (i-refined) deletions at §4.5.1 (OD-internal mis-routed cross-axis edges) | CLOSED at v2.4 §0.7; preserved at v2.6 | No action |
| CXA-OD-IS-EDGE-DRIFT (Class 3 informational) | CXA v2.1 §2.3.5 enumerates 6 edges; OD plan v2.6 §4.5.1 enumerates 4 | Non-blocking; future composition-document revision pass |
| OD-INTERNAL-FORMALIZATION (Class 3 informational) | OD plan lacks explicit "OD-internal cross-cluster dependency" section that canonicalizes sqlite substrate + ring-buffer eviction as within-axis (non-cross-axis) compositions | Non-blocking; future OD plan revision pass (formalization deferred) |

### 5.3 Filing footer

| Field | Value |
|---|---|
| Artifact | `harness-od/CLAUDE.md` |
| Authored at | Phase 6.5 Session 6 (ε), 2026-05-15 |
| Authoring authority | `Phase_6_5_Session_6_Kickoff.md` §2.1.2 |
| Predecessor | Design-phase workspace OD spec v1.3 + OD plan v2.6 |
| Revision policy | This file is canonical for the `harness-od/` subdirectory; revisions route to design-phase back-flow per §5.1 |

---

*End of `harness-od/CLAUDE.md`. Parent guidance at workspace root `CLAUDE.md`. OD spec + plan + CXA v2.1 §2.3.3 / §2.3.5 / §2.3.6 at design-phase workspace.*
