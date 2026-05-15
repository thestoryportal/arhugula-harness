# Specification — Control Plane v1.3

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_3.md` |
| Status | **Proposed** — F2-12 cascade Step 5a revision pass; promotion to Accepted at cascade close (post-Step 6 plan v2.2 filings) |
| Revision | v1 → v1.1 (P5-CK iter-1 close mechanical revision) → v1.2 (P5-CK iter-2 mechanical-alignment) → **v1.3 (F2-12 cascade Step 5a revision pass authored 2026-05-14 per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 + ADD v1.3 §6.3.1 cascade Step 5a row + PRD v1.1 R-CP-04 + R-CP-07 absorption)** |
| Revision date | 2026-05-14 (v1.3 revision pass) |
| Phase | 5 — Specification authoring (post-Phase-3 F2-12 cascade Step 5a per `Project_Workflow_v1_7.md` §4.1.2; cascade-driven revision pass under `spec-writer` SKILL.md spec-revision-pass discipline + Workflow v1.7 §7 fidelity-grammar) |
| Skill | `spec-writer` (spec-revision-pass sub-mode) at v1.3 |
| Promotion path | Accepted at F2-12 cascade close |
| Source-set | PRD v1.1 (cascade Step 4 output) + ADD v1.3 §3.1.1 (D1 v1.2 absorption) + ADR-D1 v1.2 §1.1.1 + §1.1.2 + §1.1.2.2 + ADR-D6 v1.2 §1.2 (engine.* row update) + ADR-D6 v1.2 §1.2.2 (retry.* namespace declaration) |
| Entry authorization | `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 cascade Step 5a row + ADD v1.3 §6.3.1 cascade execution path Step 5a row + `Project_Workflow_v1_7.md` §3.1 |
| Exit gate | F2-12 cascade Step 6a (CP plan v2.2 revision pass per `implementation-planner` SKILL.md revision-pass sub-mode) consuming this CP spec v1.3 as substrate |

## Change-note (v1.2 → v1.3)

**Scope of revision.** F2-12 cascade Step 5a revision pass per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 + ADD v1.3 §6.3.1 cascade execution path Step 5a row. The revision pass absorbs the ADR-D1 v1.2 + ADR-D6 v1.2 (engine.* + retry.* portions) substantive amendments + PRD v1.1 R-CP-04 + R-CP-07 observable-behavior surface into Control Plane spec contract surfaces and closes the §8.4 F2-12 affected-contract notation. Six amendment sites:

| Site | Amendment shape | Substrate source |
|---|---|---|
| §3.5 retry.* sub-tree (namespace table row) | retry.* attribute set extended from 4 attributes (retry.attempt, retry.cause, retry.backoff_ms, retry.policy) to 6 attributes per D6 v1.2 §1.2.2 retry-attempt child span schema (retry.attempt_number, retry.original_span_id, retry.delay_ms, retry.cause_attribution, retry.fail_class, engine.replay_disposition composition); parent-span retry.attempt event 3-field schema declared (parent.attempt_count, parent.attempts_remaining, parent.next_delay_ms) | ADR-D6 v1.2 §1.2.2.1 + §1.2.2.2 |
| §3.5 retry.attempt sampling row | Sampling discipline updated to apply to BOTH parent event AND child span per D6 v1.2 §1.2.2.4; retry-budget-exit boundary (parent.attempts_remaining == 0) always-sampled discipline added | ADR-D6 v1.2 §1.2.2.4 |
| §3.5 F2-12 carry-forward note | Transitioned from "deferred to D1 v1.2 + D6 v1.2 closure" to "✅ CLOSED at v1.3 absorbing D6 v1.2 §1.2.2 retry.* namespace declaration"; sibling-span terminology corrected to child-per-attempt per D6 v1.2 §1.2.2 council §6.3 topology authority | ADR-D6 v1.2 §1.2.2 + council §6.3 |
| §5.4 sampling table retry.attempt row | Sampling row updated to reference dual-emission discipline (parent event + child span); retry-budget-exit boundary always-sampled note added | ADR-D6 v1.2 §1.2.2.4 |
| §8 C-CP-08 — Replay-resumption semantics per engine class | ADR commitments honored row updated D1 v1.1 → v1.2; cross-axis composition with D6 v1.2 §1.5 dedup algorithm noted; F2-12 active engagement notation transitioned to closure | ADR-D1 v1.2 §1.1.1 + §1.1.2 |
| §8.4 F2-12 carry-forward affected-contract notation | Transitioned from "out of scope at this spec revision; routes to parallel council session" to "✅ CLOSED at this spec revision absorbing D1 v1.2 + D6 v1.2 cascade Steps 2a + 2b + 3 outputs"; closure execution path table recorded | ADD v1.3 §6.3.1 + F2-12 cascade Step 5a routing |
| §9 C-CP-09 — engine.* span attribute namespace declaration | Contract surface revised from 3 attributes to 4 attributes; ADR commitments honored row updated D1 v1.1 → v1.2 + ADR-D6 v1.2 §1.2 row engine.*; PRD requirement satisfied row extended to R-CP-07 (replay-resumption-engine.replay_disposition); §9.1 attribute declarations table extended with 4th row (engine.replay_disposition); §9.4 D6 ingestion contract updated to reference D6 v1.2 §1.2 engine.* row + §1.5 dedup algorithm consumption | ADR-D1 v1.2 §1.1.1 + ADR-D6 v1.2 §1.2 + §1.5 |

Workflow v1.7 §7 fidelity-grammar discipline applied across all amendment sites: no Pattern P1 cross-artifact name drift (engine.replay_disposition attribute name canonical at D1 v1.2 §1.1.1; inherited at CP §9.1 + §5.4 + §3.5 + §8.4 with Source column citation); no Pattern P2 verbatim-claim-contradicted (all "per ADR-X v1.2 §Y" claims verify against source files at `/mnt/user-data/outputs/`); citation anchors substrate-verified per Workflow v1.7 §2.3.3.1 clause (iii).

**Status posture.** `Status: Proposed` preserved per `Project_Workflow_v1_7.md` §3.1 — promotion to `Accepted` blocked until F2-12 cascade close. CP spec v1.3 enters cascade Step 6a (CP plan v2.2 revision pass) as substrate input.

**Sections preserved verbatim from v1.2.** §Front-matter (Axis declaration; Axis-grounding note; PRD requirement scope; Cross-axis citation substrate; Persona-linkage substrate; Scope and out-of-scope; [carry-forwards] inheritance — only the F2-12 line revised at v1.3 §8.4 + §3.5 + §[carry-forwards] sites); §1 C-CP-01 through §2 C-CP-02 (provider abstraction + routing strategy); §3 C-CP-03 §3.1 + §3.2 + §3.3 + §3.4 (chain-advancement contracts; only §3.5 retry.* sub-tree and F2-12 carry-forward note revised at v1.3); §4 C-CP-04 (cross-family fallback chain composition); §5 C-CP-05 §5.1 + §5.2 + §5.3 + §5.5 + §5.6 + §5.7 (lifecycle event class table; per-class minimum attribute set; lease.* namespace; downstream namespace composition; F2-12 active engagement note revised; PRD requirement satisfaction) — only §5.4 sampling table retry.attempt row revised at v1.3; §6 C-CP-06 through §7 C-CP-07 (manifest declaration + engine-class commitment); §8 C-CP-08 §8.1 + §8.2 + §8.3 (resumption-kind enum; F2 state-ledger composition; resumption observable behavior) — only §8 ADR-commitments-honored row + §8.4 F2-12 affected-contract notation revised at v1.3; §9 C-CP-09 §9.2 + §9.3 + §9.4 (per-row Tier-3/Tier-5 mapping; C-IS-10 composition) — only §9 contract surface + ADR-commitments-honored + PRD-requirement-satisfied rows + §9.1 attribute declarations table revised at v1.3 (4-attribute extension); §10 C-CP-10 through §22 C-CP-22 (multi-agent topology + HITL + audit + validator contracts); §23 C-CP-23 (T-perm-3 three-layer composition); §24 C-CP-24 §24.2 + §24.3 + §24.4 (cross-axis composition exports; cross-axis composition with session 5; F2-12 carry-forward export — closure status noted; Deferred to implementation discretion); §[traceability] matrix (preserved verbatim; D1 + D6 row labels updated at v1.3 to v1.2); §[carry-forwards] [CF-2] (Workflow §7 substrate-skill propagation; preserved verbatim) — [CF-1] F2-12 line revised at v1.3 to closure; §[coherence pass] (preserved as v1.2 point-in-time historical audit per Stage 2 + Stage 3a precedent; v1.3 amendment-site verification inline per Workflow v1.7 §7 fidelity-grammar).

**Changes inline.** Status block (Revision row extended with v1.3 entry; Revision date row appended; Source-set updated D1 v1.1 → v1.2 + D6 v1.1 → v1.2 + PRD v1.1 + ADD v1.3 entries; Entry authorization extended with F2-12 cascade Step 5a row). This Change-note (v1.2 → v1.3) section. §3.5 retry.* namespace table row (4-attribute extension to 6-attribute + parent-event-schema-row addition). §3.5 sampling-table retry.attempt row (dual-emission sampling note added). §3.5 F2-12 carry-forward note (transitioned to closure). §5.4 sampling-table retry.attempt row (dual-emission sampling note). §8 contract surface description (R-CP-07 satisfaction extended). §8 ADR-commitments-honored row (D1 v1.1 → v1.2; D6 v1.2 §1.5 composition). §8.4 F2-12 carry-forward affected-contract notation (transitioned to closure). §9 contract surface (3-attribute → 4-attribute extension). §9 ADR-commitments-honored row (D1 v1.1 → v1.2 + D6 v1.2 §1.2 engine.* row). §9 PRD-requirement-satisfied row (R-CP-07 added). §9.1 attribute declarations table (4th row added: engine.replay_disposition). §9.4 D6 ingestion contract row (D6 v1.1 → v1.2 + §1.5 dedup algorithm consumption note). §[traceability] matrix D1 + D6 row-label versions (v1.1 → v1.2). §[carry-forwards] [CF-1] F2-12 entry (transitioned to closure). Filing footer updated to v1.3.

**Cross-cascade-step coordination.** CP spec v1.3 produces one downstream effect at cascade Step 6a:

| Downstream cascade step | Substrate consumed from CP spec v1.3 |
|---|---|
| Step 6a — CP plan v2.2 revision pass | §3.5 retry.* 6-attribute namespace + parent-event 3-field schema → U-CP-20 acceptance criterion #5 carry-forward declaration revised to closure; §5.4 sampling discipline retry.attempt dual-emission row → U-CP-20 acceptance criterion sampling-binding revised; §8.4 F2-12 closure → U-CP-55 §24.4 export manifest update; §9.1 4-attribute engine.* declaration → U-CP-21 engine.* namespace 4-attribute |

**F2-12 status at CP spec v1.3.** ✅ CLOSED at this revision-pass filing per ADD v1.3 §6.3.1 cascade Step 5a row. The contract-level absorption at §3.5 + §5.4 + §8.4 + §9 surfaces the architectural amendments at the CP-specification layer. Formal `closure_pending false` declaration deferred to `F2-12_Closure_Declaration.md` at cascade close.

---

## Front-matter

[§Axis declaration + §Axis-grounding note + §PRD requirement scope + §ADR scope + §Cross-axis citation substrate + §Persona-linkage substrate + §Scope and out-of-scope preserved verbatim from v1.2 except [carry-forwards] line revised at v1.3 to closure (see §[carry-forwards] section below).]

---

## §1 C-CP-01 — Capability-aware multi-LLM provider abstraction

[Preserved verbatim from v1.2.]

## §2 C-CP-02 — Layered cheapest-deterministic-first routing strategy

[Preserved verbatim from v1.2.]

## §3 C-CP-03 — Per-layer time budget with deterministic-fallback-on-budget-exceeded

[§3.1 + §3.2 + §3.3 + §3.4 preserved verbatim from v1.2.]

### §3.5 `fallback.*` and `harness.breaker.*` and `retry.*` span attribute namespaces declared at this contract (v1.3 amendment absorbing D6 v1.2 §1.2.2)

Three namespaces declared at this contract are ingested by D6 §1.2 at session 4 (Operational Discipline spec):

| Namespace | Attributes |
|---|---|
| `fallback.*` | `fallback.from_layer`, `fallback.from_provider`, `fallback.from_model`, `fallback.cause` ∈ `{time_budget_exceeded, capability_shortfall, breaker_open, rate_limit_storm}`, `fallback.elapsed_ms`, `fallback.budget_ms`, `fallback.required_capability` (optional), `fallback.to_provider`, `fallback.to_model` |
| `harness.breaker.*` | `harness.breaker.scope` ∈ `{per_model, per_provider}`, `harness.breaker.from_state` ∈ `{closed, open, half_open}`, `harness.breaker.to_state` ∈ `{closed, open, half_open}`, `harness.breaker.trigger_count` (int), `harness.breaker.permanent_fail_repeats` (bool — C10 gating signal per OD C-OD-07 §7.1), `harness.breaker.tool_id` (string; per-model scope correlation), `harness.breaker.model_version` (string) |
| **`retry.*` (v1.3 amendment; was 4 attributes at v1.2 — `retry.attempt`, `retry.cause`, `retry.backoff_ms`, `retry.policy`; now 6 retry-attempt child span attributes per D6 v1.2 §1.2.2.1)** | **`retry.attempt_number` (integer; 1-indexed), `retry.original_span_id` (string; 16-hex OTel W3C Trace Context format; recovered from F2 state-ledger entry filtered by `idempotency_key`), `retry.delay_ms` (integer; jittered delay per C9 full-jitter backoff), `retry.cause_attribution` (string; open-set enum from C5 cause_attribution catalog per C-CP-21), `retry.fail_class` (enum: `{transient-retry, Reflexion-recoverable, HITL-recoverable, permanent-fail-exit, terminal-fail-exit}`; from C5 5-class fail-class taxonomy), and `engine.replay_disposition` (composition with sub-scope (i); inherits parent operation's value per D1 v1.2 §1.1.1)** |

**Parent-span retry.attempt event schema (v1.3 amendment; new at v1.3 per D6 v1.2 §1.2.2.2).** The parent operation span carries a `retry.attempt` event at the retry-trigger point. The event schema:

| Event field | Type | Source | Definition |
|---|---|---|---|
| `parent.attempt_count` | integer | `c9-reliability-recovery` SKILL.md | Total attempts so far for this operation |
| `parent.attempts_remaining` | integer | `c9-reliability-recovery` SKILL.md | Remaining retry budget; zero means budget exhausted |
| `parent.next_delay_ms` | integer (optional; omitted when `parent.attempts_remaining == 0`) | `c9-reliability-recovery` SKILL.md | Delay (jittered) before next attempt |

**Dual-emission discipline (v1.3 amendment per D6 v1.2 §1.2.2.3).** The retry-attempt mechanism MUST emit BOTH the parent-span event AND the new child span at each retry. Per `F2-12_Council_Deliberation_Output.md` §6.4 (C7 schema authority): emission discipline forbids collapsing to event-only or span-only. Collapse to event-only loses per-attempt operation-level instrumentation; collapse to span-only loses parent-perspective retry-trigger marking.

Per `c7-observability` SKILL.md sampling discipline:

| Span event / span | Sampling rate |
|---|---|
| `fallback.triggered` | **Always-sampled (head=1.0, tail-keep-on-classification=true)** — fall-through is reliability-critical and tamper-evidence-relevant |
| `fallback.exhausted` | **Always-sampled (head=1.0)** — chain exhaustion is reliability-critical |
| `breaker.tripped` | **Always-sampled (head=1.0, tail-keep-on-classification=true)** |
| `retry.attempt` (parent event) | Base-rate sampled at first attempt; **always-sampled (head=1.0) at 2nd attempt onward** (per Cluster 4 §2.2.3 [HIGH] staircase visibility); **always-sampled when `parent.attempts_remaining == 0` (retry-budget-exit boundary; tamper-evidence-relevant per D6 v1.2 §1.2.2.4)** |
| **retry-attempt child span (v1.3)** | **Base-rate sampled at cell tunable per D6 §1.3 sampling discipline** |

**F2-12 carry-forward note (v1.3 amendment; transitioned to closure).** ✅ CLOSED at v1.3 absorbing ADR-D6 v1.2 §1.2.2 retry.* namespace declaration. The v1.2 question — "does `retry.attempt` emit a span event AND a new sibling span per D6 §1.2?" — is answered at v1.3: BOTH event AND span are emitted per dual-emission discipline; the v1.2 "sibling-span" terminology is corrected to "child-per-attempt" per `c1-orchestration-control` SKILL.md topology authority at council §6.3 (retry attempts are children of the parent operation; attempts are siblings to each other under that parent). The retry-attempt child span attribute substrate is declared at this §3.5 contract per D6 v1.2 §1.2.2.1 + §1.2.2.2 composition.

**Deferred to implementation discretion.** Specific timeout values per cell of (workload-class × persona-tier × layer); specific embedding-classifier hot-path latency optimization; specific breaker trip-threshold values per `{provider, model}` pair; specific cooldown duration shape per cause class; specific OTel/OTLP emission timing for `fallback.triggered` events (before fall-through call vs concurrent with).

---

## §4 C-CP-04 — Cross-family fallback chain composition

[Preserved verbatim from v1.2.]

## §5 C-CP-05 — F3 capability-floor lifecycle event surface

[§5.1 + §5.2 + §5.3 preserved verbatim from v1.2.]

### §5.4 Sampling discipline per event class (v1.3 amendment to retry.attempt row)

| Event class | Sampling rate | Rationale |
|---|---|---|
| `workflow.start` | **Always-sampled (head=1.0)** | Cost-attribution anchor; tamper-evidence baseline |
| `step.boundary` | head-based-dev base-rate / tail-based-prod default | Volume-bounded; tail-keep on failure classification |
| `fallback.triggered` / `fallback.exhausted` | **Always-sampled (head=1.0)** per C-CP-03 §3.5 | Reliability-critical |
| **`retry.attempt` (parent event)** | **base-rate at 1st attempt; always-sampled at 2nd onward per C-CP-03 §3.5; ALWAYS-SAMPLED at retry-budget-exit boundary (parent.attempts_remaining == 0) per D6 v1.2 §1.2.2.4 (v1.3 amendment)** | **Cluster 4 §2.2.3 [HIGH] staircase visibility + tamper-evidence-relevant at budget-exit (v1.3)** |
| **retry-attempt child span (v1.3 new row)** | **Base-rate sampled at cell tunable per D6 §1.3 sampling discipline; subject to tail-keep on retry.fail_class classification** | **Per-attempt operation-level instrumentation; cost-attribution per attempt anchor (D6 v1.2 §1.5.3)** |
| `breaker.tripped` | **Always-sampled (head=1.0)** per C-CP-03 §3.5 | Reliability-critical |
| `lease.acquired` / `lease.released` | base-rate | Volume-bounded; supports concurrent-resume corruption detection per ADR-F3 v1.1 capability-floor (iii) |
| `workflow.resumption` | **Always-sampled (head=1.0)** | Replay-resumption visibility per R-CP-07; tamper-evidence anchor |

[§5.5 + §5.6 + §5.7 preserved verbatim from v1.2.]

---

## §6 C-CP-06 — Manifest-declaration invocation discipline with per-step opt-in override

[Preserved verbatim from v1.2.]

## §7 C-CP-07 — Engine class committed per deployment surface

[Preserved verbatim from v1.2.]

## §8 C-CP-08 — Replay-resumption semantics per engine class (R-CP-07 — F2-12 ✅ CLOSED at v1.3)

**Contract surface (v1.3 amendment to header label).** Per-engine-class resumption-kind enum + composition with F2 state-ledger via `idempotency_key` + resumption observable behavior + F2-12 affected-contract notation transitioned to closure per ADD v1.3 §6.3.1 cascade Step 5a row.

**PRD requirement(s) satisfied (v1.3 amendment).** R-CP-07 (replay-resumption semantics visible at run resumption — `engine.replay_disposition` 5-value enum visibility per PRD v1.1 R-CP-07 amendment).

**ADR commitment(s) honored (v1.3 amendment).** **ADR-D1 v1.2 §1.1.1 (4-attribute `engine.*` namespace including `engine.replay_disposition`) + §1.1.2 (per-engine-class replay-emission discipline) + §1.1.2.2 (F2 state-ledger entry shape extension with `original_trace_id` + `original_span_id`)**; **ADR-D6 v1.2 §1.2 row `engine.*` (4-attribute ingestion) + §1.5 dedup algorithm consuming `engine.replay_disposition` as per-class discriminator + §1.5.1 replay-aware dedup orthogonality + §1.5.2 cause_attribution invariance check + §1.5.3 per-attempt cost-attribution discipline**; ADD v1.3 §3.1.1 D1 Synthesis + §6.3.1 F2-12 closure record.

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-05 (`idempotency_key` field — harness-canonical join key); C-IS-10 §10.2 (idempotency-key join export — engine event history consuming surface); `Spec_Operational_Discipline_v1_3.md` C-OD-14 (cost-attribution-per-span contract amended at cascade Step 5b absorbing D6 v1.2 §1.5 dedup algorithm + per-attempt cost discipline).

**Persona linkage.** Persona §4 (99.9%+ SLO; durable replay across restart); §10.4 (compliance-readiness); §11.3 (long-tail duration of durable pole).

**Specification content.**

### §8.1 Per-engine-class resumption-kind enum

[Preserved verbatim from v1.2.]

### §8.2 Composition with F2 state-ledger via `idempotency_key`

[Preserved verbatim from v1.2.]

### §8.3 Resumption observable behavior

[Preserved verbatim from v1.2.]

### §8.4 F2-12 affected-contract notation (✅ CLOSED at v1.3)

**Status (v1.3 amendment).** ✅ **CLOSED** at CP spec v1.3 filing per ADD v1.3 §6.3.1 cascade Step 5a row. The v1.2 status was "out of scope at this spec revision; routes to parallel `council-orchestrator` C7+C9 session per ADD §6.3.1 active path"; v1.3 transitions to ✅ CLOSED with F2-12 closure execution path:

| Cascade step | Artifact | Sub-scope closed |
|---|---|---|
| 1 — Council deliberation | `F2-12_Council_Deliberation_Output.md` (filed 2026-05-14) | Substantive resolution substrate for all three sub-scopes |
| 2a — ADR-D1 revision | `ADR-D1_v1_2.md` (filed 2026-05-14) | (i) span re-emission semantics |
| 2b — ADR-D6 revision | `ADR-D6_v1_2.md` (filed 2026-05-14) | (ii) retry.attempt sibling-span (corrected to child-per-attempt) + (iii) trace-ingestion dedup |
| 3 — ADD consolidation | `Architectural_Design_Document_v1_3.md` (filed 2026-05-14) | Cross-axis consolidation |
| 4 — PRD revision | `PRD_v1_1.md` (filed 2026-05-14) | R-CP-04 + R-CP-07 + R-OD-05 observable-behavior absorption |
| **5a — CP spec revision** | **`Spec_Control_Plane_v1_3.md` (this artifact)** | **C-CP-08 + C-CP-09 + §3.5 + §5.4 contract-surface absorption** |
| 5b — OD spec revision (pending) | `Spec_Operational_Discipline_v1_3.md` | C-OD-14 cost-attribution-per-span contract amendment |
| 6a — CP plan revision (pending) | `Implementation_Plan_Control_Plane_v2_2.md` | U-CP-20 + U-CP-21 + U-CP-55 plan-level absorption |
| 6b — OD plan revision (pending) | `Implementation_Plan_Operational_Discipline_v2_2.md` | U-OD-20 + U-OD-14 plan-level absorption |
| Close | `F2-12_Closure_Declaration.md` (pending) | Formal `closure_pending false` declaration |

**Contract-level absorption at this spec revision.** F2-12 sub-scope (i) span re-emission semantics absorbed at §9.1 4-attribute engine.* namespace declaration including `engine.replay_disposition`. F2-12 sub-scope (ii) retry.attempt sibling-span discipline (corrected to child-per-attempt) absorbed at §3.5 retry.* 6-attribute namespace + §3.5 + §5.4 dual-emission sampling discipline. F2-12 sub-scope (iii) trace-ingestion dedup composition with F2 `idempotency_key` absorbed at §9 ADR commitments honored row (D6 v1.2 §1.5 dedup algorithm consumed by this contract; full dedup-algorithm specification at OD spec v1.3 C-OD-14 amendment at cascade Step 5b).

**Deferred to implementation discretion.** Specific span-re-emission engine-vendor mapping (Temporal SDK; LangGraph SqliteSaver; DBOS); specific `resumption.kind` to engine-vendor-event mapping; specific tail-keep-on-replay sampling policy at D6 ingestion (per-cell tunable per OD spec v1.3 amendment); specific cross-engine-class span correlation library at D6 ingestion (session 4 spec territory; closed at cascade Step 5b).

---

## §9 C-CP-09 — `engine.*` span attribute namespace declaration (v1.3 amendment absorbing D1 v1.2)

**Contract surface (v1.3 amendment).** **Four `engine.*` attribute names** (was three at v1.2) + per-attribute type + per-attribute cardinality + per-attribute always-emitted scope + composition with §1.1 taxonomy materialization at D6 §1.2. The 4-attribute namespace absorbs the F2-12 sub-scope (i) closure per ADR-D1 v1.2 §1.1.1.

**PRD requirement(s) satisfied (v1.3 amendment).** R-CP-04 (workflow lifecycle event surface — 4-attribute `engine.*` substrate); R-CP-06 (engine class committed per deployment surface — observability surface); **R-CP-07 (replay-resumption semantics — `engine.replay_disposition` 5-value enum visibility per PRD v1.1 R-CP-07 amendment — added at v1.3)**.

**ADR commitment(s) honored (v1.3 amendment).** **ADR-D1 v1.2 §1.1.1 (canonical declaration site for 4-attribute `engine.*` namespace; was 3 attributes at v1.1)**; **ADR-D6 v1.2 §1.2 row `engine.*` (4-attribute ingestion at D6; was 3 attributes at v1.1; Source column cites D1 v1.2 §1.1.1)**.

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-05 (`idempotency_key` field — harness-canonical join key); C-IS-10 §10.2 (idempotency-key join export — engine event history consuming surface); `Spec_Operational_Discipline_v1_3.md` C-OD-14 (cost-attribution-per-span contract amended at cascade Step 5b consuming `engine.replay_disposition` as dedup discriminator).

**Persona linkage.** Persona §10.2 (cost-attribution-per-span foundational primitive); §10.4 (compliance-readiness — comprehensive observability).

**Specification content.**

### §9.1 Four `engine.*` attribute declarations (v1.3 amendment; was three at v1.2)

Per ADR-D1 v1.2 §1.1.1:

| Attribute | Type | Cardinality | Always-emitted on | Discriminator role |
|---|---|---|---|---|
| `engine.class` | enum string ∈ `{event-sourced-replay, save-point-checkpoint, pure-pattern-no-engine, reconciler-loop, WAL-segment}` | bounded (5) | Every span emitted under D1 §1.1's lifecycle envelope (the eight events per C-CP-05 §5.1) | Closed enumeration of D1 §1.1 rows; stable discriminator for engine-class-conditional sampling and dashboard binding |
| `engine.event_history.tier` | enum string ∈ `{Tier-3, Tier-5}` | bounded (2) | Span events that reference engine-internal durable state OR state-ledger join surface | `Tier-3` = engine-internal durable substrate per D1 §1.1 *C3-tier residence* column; `Tier-5` = F2 state-ledger join surface |
| `engine.event.id` | opaque string under each engine class's native ID convention (Temporal eventId; LangGraph checkpoint_id; ACP CRD event UID; Kode-Agent segment offset; pure-pattern harness-assigned UUID) | per-event | Span events referencing a specific engine-internal event | Engine-internal naming; cross-engine-class portability via `idempotency_key` join on F2 |
| **`engine.replay_disposition` (v1.3 amendment; new at v1.3 per ADR-D1 v1.2 §1.1.1)** | **enum string ∈ `{deterministic_replay, checkpoint_resume, no_replay, reconciler_iteration, wal_consume}` closed-mapped to `engine.class`** | **bounded (5)** | **Every span emitted under D1 §1.1's lifecycle envelope (same scope as `engine.class`)** | **Per-class replay-emission discriminator per ADR-D1 v1.2 §1.1.2 + ADR-D6 v1.2 §1.5 dedup algorithm per-class consumption** |

### §9.2 Per-row Tier-3 / Tier-5 mapping

[Preserved verbatim from v1.2.]

### §9.3 Composition with C-IS-10 §10.2 idempotency-key join

[Preserved verbatim from v1.2.]

### §9.4 D6 ingestion contract (v1.3 amendment)

Per **ADR-D6 v1.2 §1.2 row `engine.*` (4-attribute ingestion; was 3 at v1.1)**: D6 ingests this attribute set verbatim without re-declaration. Session 4 Operational Discipline spec at C-OD-14 (D6 cost-attribution-per-span contract amended at cascade Step 5b) consumes this contract by citation; the cell sampling discipline per D6 §1.3 applies. **At v1.3, D6 v1.2 §1.5 trace-ingestion dedup algorithm consumes `engine.replay_disposition` as the per-class discriminator: `deterministic_replay` DROPs idempotent re-reads; `checkpoint_resume` / `reconciler_iteration` / `wal_consume` RECORD new replay-derived spans; `no_replay` ERRORs on unexpected re-ingestion. Per D6 v1.2 §1.5.3, per-attempt cost-attribution accrues per attempt for re-emitting dispositions; zero additional accrual for `deterministic_replay`.**

**Deferred to implementation discretion.** Specific `engine.event.id` serialization format per engine candidate; specific cross-engine-class span correlation library at D6 ingestion (closed at cascade Step 5b OD spec v1.3); specific tail-keep-on-engine-class-equals-X discipline at D6 sampling (closed at cascade Step 5b OD spec v1.3).

---

## §10 C-CP-10 through §24 C-CP-24

[All sub-sections preserved verbatim from v1.2.]

---

## §[carry-forwards]

### [CF-1] F2-12 — D1 v1.1 → v1.2 + D6 v1.1 → v1.2 replay-trace-emission contract (✅ CLOSED at v1.3)

**Status (v1.3 amendment).** ✅ **CLOSED** at CP spec v1.3 filing per ADD v1.3 §6.3.1 cascade Step 5a row. Contract-level absorption at §3.5 retry.* namespace + §5.4 sampling table dual-emission discipline + §8.4 F2-12 affected-contract notation closure + §9 C-CP-09 4-attribute engine.* declaration. Closure execution path table recorded at §8.4. Formal `closure_pending false` declaration deferred to `F2-12_Closure_Declaration.md` at cascade close.

### [CF-2] Workflow §7 substrate-skill propagation

[Preserved verbatim from v1.2.]

---

## §[traceability]

[Preserved verbatim from v1.2 except D1 + D6 row-label versions updated v1.1 → v1.2; cell marks preserved (v1.3 amendments at existing C-CP-08 + C-CP-09 + §3.5 + §5.4 contract sites; no new contracts added).]

---

## §[coherence pass]

[Audits preserved verbatim from v1.2 as v1.2 point-in-time historical audit; v1.3 amendment-site verification inline per Workflow v1.7 §7 fidelity-grammar discipline. The four `spec-writer` SKILL.md §"Workflow at runtime" disciplines verify at each v1.3 amendment site: inputs read (PRD v1.1 + ADD v1.3 + ADR-D1 v1.2 + ADR-D6 v1.2); ingestion contract per layer (council deliberation substrate + ADR substrate); tensions surfaced (T-perm-2 + T-perm-3 ENGAGED at council §7; preserved at v1.3); self-audit (no Pattern P1 cross-artifact name drift; no Pattern P2 verbatim-claim-contradicted).]

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_3.md` |
| Filing destination | `/mnt/user-data/outputs/Spec_Control_Plane_v1_3.md` |
| Status | Proposed (pending F2-12 cascade close per cascade Step 6 plan v2.2 filings) |
| Predecessor | `Spec_Control_Plane_v1.md` (v1.0 → v1.1 → v1.2 baseline) |
| Substrate consumed | PRD v1.1 + ADD v1.3 + ADR-D1 v1.2 + ADR-D6 v1.2 (cascade Steps 2 + 3 + 4 outputs) |
| Successor | `Implementation_Plan_Control_Plane_v2_2.md` (F2-12 cascade Step 6a) |
| F2-12 closure status | ✅ CLOSED at cascade Step 5a (this artifact) |
| Workflow discipline | `Project_Workflow_v1_7.md` §7 fidelity-grammar |
| Date | 2026-05-14 |

*Filed at F2-12 cascade Step 5a close. C-CP-08 ADR-commitments-honored updated to D1 v1.2 + D6 v1.2; §8.4 F2-12 affected-contract notation transitioned to ✅ CLOSED with closure execution path table; §9 C-CP-09 §9.1 engine.* declaration extended 3 → 4 attributes with new engine.replay_disposition row; §3.5 retry.* namespace extended 4 → 6 attributes with parent-event 3-field schema declaration; §5.4 sampling table retry.attempt row updated for dual-emission discipline. Cascade segment boundary per OD-F212-4.A. Recommended next cascade step: Step 5b (OD spec v1.3 revision pass) per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 — C-OD-14 cost-attribution-per-span contract amendment absorbing D6 v1.2 §1.5 dedup algorithm + §1.5.3 per-attempt cost-attribution discipline.*