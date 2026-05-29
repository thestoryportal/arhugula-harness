# Phase 7d Retirement Events — Batch 36

| Field | Value |
|---|---|
| Batch number | 36 |
| Filed at | 2026-05-28 (post H_T-OD-3 gate (a) tail-keep-on-classification closure arc — `TailKeepSpanProcessor` substrate + materializer wiring landed) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5; PARTIAL → RETIRE-READY transit per harness-od/CLAUDE.md §4.1 H_T-OD-3 retirement-criterion ladder |
| Predecessor batch | `phase-7d-retirement-events-batch-35.md` (2026-05-28 — H_T-OD-4 STILL-BOUNDED → PARTIAL via PR #22; refined PARTIAL at PR #25; OD-3 gate (b) closed at PR #25) |

---

## §0 Batch context

**Status type: 1 PARTIAL → RETIRE-READY transit (H_T-OD-3). Cumulative RETIRED count unchanged at 37/54 (68.5%); RETIRE-READY count increments 1/54 → 2/54 (3.7%); PARTIAL count decrements 4/54 → 3/54 (5.6%); STILL-BOUNDED count unchanged at 10/54 (18.5%); STILL-BOUNDED-INDEFINITELY count unchanged at 2/54 (3.7%); pipeline-advanced 42/54 → 42/54 = 77.8% UNCHANGED (within-pipeline tier promotion — PARTIAL and RETIRE-READY both count as pipeline-advanced per X-AL-2). Cardinality check: 37 + 2 + 3 + 10 + 2 = 54 ✓.**

This batch records the **PARTIAL → RETIRE-READY transit** for H_T-OD-3 (Composite Sampler) closing the gate (a) §9.1 tail-keep-on-classification at OTLP collector boundary deferral inherited from OD spec v1.2 §9.3 implementer-discretion clause.

OD-3 had two PARTIAL → RETIRE-READY gates:
- Gate (a) §9.1 tail-keep-on-classification at OTLP collector boundary
- Gate (b) §10.3 persona-tier-aware base_rate envelope

Gate (b) CLOSED at PR #25 merge (`056d651`, 2026-05-28) via `materialize_tracer_provider_stage` reading `PER_CELL_BASE_RATE_ENVELOPE[CellID(persona_tier, deployment_surface)].default_rate`. Pre-PR-#25 row stayed at PARTIAL (refined) per X-AL-2 (one of two gates closed = no transit).

Gate (a) CLOSED at this arc via:

| Artifact | Authority |
|---|---|
| `harness-od/src/harness_od/tail_keep_classification.py` NEW — `is_classification_trigger(span)` per-span §10.2 trigger predicate + 4 carrier constants | OD spec v1.27 §1.3 carrier-level reading |
| `harness-od/src/harness_od/tail_keep_span_processor.py` NEW — `TailKeepSpanProcessor(SpanProcessor)` wrap-BSP processor with per-trace buffering + classification-trigger preservation + always-sampled passthrough + force_flush keep-all | OD spec v1.27 §1.1 (a)+(b) algorithm-lift |
| `harness-runtime/src/harness_runtime/lifecycle/span_processor.py` EXTEND — NEW `tail_keep_processor: TailKeepSpanProcessor \| None` field at `SpanProcessorStage` + per-deployment-surface gate at `materialize_span_processor_stage` (wrap BSP iff surface != LOCAL_DEVELOPMENT) + tail-keep-aware drain at `flush()` | OD spec v1.27 §1.4 head-based-at-local-development invariant preservation |
| `design-substrate/Spec_Operational_Discipline_v1_27.md` NEW — delta-only canonical-reading amendment at §C-OD-09 §9.3 closing the implementer-discretion clause on tail-keep algorithm + SDK binding | Workspace delta-only spec convention |
| `design-substrate/Implementation_Plan_Operational_Discipline_v2_26.md` NEW — delta-only single-unit canonical-reading amendment at U-OD-11 absorbing v1.27 §1.1 + §1.2 + §1.3 + §1.4 | Workspace delta-only plan convention |
| 21 NEW tests at `harness-od/tests/test_tail_keep_span_processor.py` (16) + `harness-runtime/tests/test_lifecycle_span_processor.py` (5) | Acceptance discipline per OD plan v2.26 §1.1 NEW ACs #N.1 through #N.13 |

Both OD-3 gates closed → PARTIAL → RETIRE-READY transit per X-AL-2 (structural-criterion-A: cited unit IDs landed; structural-criterion-B: substrate + production consumer-site lift binding chain MET via materializer wrap + downstream BSP forwarding).

---

## §1 Criterion verification

- **Criterion A** (cited unit IDs landed). MET. U-OD-11 absorbs the canonical-reading amendment at OD plan v2.26 §1.1 (NEW carriers + NEW consumer sites + 13 NEW acceptance criteria). U-OD-12 `TAIL_KEEP_RULES` substrate preserved verbatim per v2.26 §2 (a).

- **Criterion B** (substituted H_E surface no longer invoked at substitution site). MET at 3 binding-chain stages:
  - Stage 1 (carrier landed) — `TailKeepSpanProcessor` + `is_classification_trigger` exposed at `harness-od/src/harness_od/tail_keep_span_processor.py` + `tail_keep_classification.py`; 16 unit tests verify per-trace buffering + 3 §10.2 trigger predicates + always-sampled passthrough + per-trace isolation + force_flush keep-all + InMemoryExporter end-to-end.
  - Stage 2 (production consumer site) — `materialize_span_processor_stage` at `harness-runtime/src/harness_runtime/lifecycle/span_processor.py` wraps the BSP with `TailKeepSpanProcessor` iff `config.deployment_surface != LOCAL_DEVELOPMENT`; at LOCAL_DEVELOPMENT, BSP receives spans directly per §9.1 head-based mandate.
  - Stage 3 (e2e binding chain verified via TracerProvider) — 5 NEW tests at `test_lifecycle_span_processor.py` verify materializer wiring: `tail_keep_processor is None` at LOCAL_DEVELOPMENT; `is not None` at SELF_HOSTED_SERVER + MANAGED_CLOUD; `downstream is stage.processor`; production-surface trace drop without trigger; production-surface trace preserve with `sandbox.violation` child.

**RETIRE-READY → RETIRED gate remaining** (per H_T-OD-3 retirement-criterion ladder + workspace sub-species 7.deployment-time-opt-in-gate precedent at AS-8d batch-31 + OD-5 batch-32 + OD-6 batch-33):

- Operator deploys harness against real workload at production deployment surface (self-hosted-server OR managed-cloud);
- TracerProvider + materialize_span_processor_stage exercised at bootstrap;
- Real OTel span emission path produces traces with mixed always-sampled / non-always-sampled / classification-triggered spans;
- OTLP collector / `LocalOTLPCollectorDaemon` observes the §10.2 preservation semantic at production runtime — classified traces preserved across the batch-export boundary; unclassified traces dropped at root close.

Terminal in-CLI state at RETIRE-READY 2026-05-28 (batch-36). Fourth member of sub-species 7.deployment-time-opt-in-gate (sibling to AS-8d batch-31 + OD-5 batch-32 + OD-6 batch-33).

---

## §2 Sub-row substitution-status table

Pre-batch-36 OD-axis bucket (post-batch-35):

| Substitution | Status | Source |
|---|---|---|
| H_T-OD-1 (deferral envelope) | STILL-BOUNDED | No `deferral_envelope` import in `harness-runtime/` |
| H_T-OD-2 (OTel SDK base + GenAI semconv) | RETIRED batch-2 (2026-05-20) | LIVE at `lifecycle/llm_dispatch.py` |
| H_T-OD-3 (Composite Sampler) | **PARTIAL (refined) → RETIRE-READY at this batch (batch-36)** | gate (b) closed at PR #25 (v1.26); gate (a) closed at v1.27 + materializer wrap |
| H_T-OD-4 (Pre-Collector redaction SpanProcessor) | PARTIAL (refined) | gate (a) §13.1 partially closed at PR #25; per-session toggle + gate (b) §13.2 deferred |
| H_T-OD-5 (Cost-attribution 5-step chain) | RETIRED batch-32 (2026-05-28) | mech-β AC #8 green on main |
| H_T-OD-6 (Local-first OTLP ingestion) | RETIRE-READY (batch-33) | 4-OD-B cluster landed; deployment-time opt-in gates RETIRED |
| H_T-OD-7 (Preservation invariants 5-dimension) | STILL-BOUNDED | Library carrier only; no runtime enforcement loop |
| H_T-OD-8 (aggregate manifest + Stage 3b inversion) | RETIRED (v1 §1 authoring-only) | Authoring-close |

Post-batch-36 OD-axis bucket: 3 RETIRED + 2 RETIRE-READY + 1 PARTIAL + 2 STILL-BOUNDED + 0 STILL-BOUNDED-INDEFINITELY = 8.

Workspace-layer cumulative post-batch-36: **37/54 RETIRED (68.5%) + 2/54 RETIRE-READY (3.7%) + 3/54 PARTIAL (5.6%) + 10/54 STILL-BOUNDED (18.5%) + 2/54 STILL-BOUNDED-INDEFINITELY (3.7%)**. Pipeline-advanced (R+RR+P): **42/54 = 77.8%** (unchanged from batch-35; within-pipeline tier promotion).

---

## §3 Adjacent observations

(a) **SECOND PARTIAL → RETIRE-READY transit in OD-axis post-batch-2.** Batch-34 promoted OD-3 STILL-BOUNDED → PARTIAL (gate-b CLOSED at PR #25 = v1.26); batch-36 promotes OD-3 PARTIAL → RETIRE-READY (gate-a CLOSED at v1.27). Both OD-3 transit events landed in 1 calendar day across 4 commits (substrate at batch-34 + persona_tier plumbing at PR #25 + this arc). NEW species candidate `single-row-multi-arc-tier-laddering` at workflow v1.12 §7.4.7.2 — OD-3 traversed STILL-BOUNDED → PARTIAL → PARTIAL (refined) → RETIRE-READY across 3 arcs in 1 calendar day. Distinct from sub-species `substrate-pre-landed-consumer-deferred-multi-arc-lift` (catalogued at PR #25 checkpoint) — that species refers to substrate-vs-consumer arc decomposition; this species refers to tier-by-tier within-row ladder traversal.

(b) **RETIRE-READY bucket grows 1 → 2.** OD-6 (batch-33) + OD-3 (this batch) both at RETIRE-READY terminal in-CLI state with deployment-time-opt-in-gate close pathway. Mirror AS-8d (batch-31) + OD-5 (batch-32) pattern; all 4 are sub-species 7.deployment-time-opt-in-gate members.

(c) **OD-3 RETIRED gate text refined.** RETIRED gate now requires real OTel span emission against an OTLP collector observing the §10.2 preservation semantic — distinct from OD-6 RETIRED gate (sqlite spans table populated at deployment) + OD-5 RETIRED gate (`cost:`-prefixed audit-ledger entries observed at production audit substrate). Each OD-axis RETIRE-READY row has its own production observability gate — operator deployment at production surface is the common precondition.

(d) **§9.3 element (d) cross-SDK conformance test deferred indefinitely.** Single-SDK MVP at HEAD per Target Stack Commitment v1 §5.2 (`opentelemetry-api` + `opentelemetry-sdk` + `opentelemetry-exporter-otlp`). Cross-SDK conformance arc is out-of-scope; preserved verbatim as deferred-indefinitely at v1.27 §1.1 row (d).

(e) **Workflow v1.12 §7.4.7.3.C audit-template applied** at `harness-od/CLAUDE.md` §4.1 cumulative-counts line + OD-3 row transit. Pre-transit text was post-PR-#25 batch-35 refresh (PARTIAL refined); post-this-arc transit re-refreshes to (PARTIAL → RETIRE-READY at batch-36).

(f) **ZERO cross-axis cascade.** Intra-OD-axis canonical-reading amendment + intra-OD-axis substrate + intra-runtime-axis consumer-site lift. CP spec / AS spec / runtime spec / CXA / ADR / ADD / PRD all unchanged.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-36.md` |
| Filed at | 2026-05-28 |
| Phase | Phase 7 sub-phase 7d — substitution retirement |
| Predecessor batch | batch-35 (H_T-OD-4 STILL-BOUNDED → PARTIAL) |
| Co-published artifacts | OD spec v1.27 + OD plan v2.26 + workspace `CLAUDE.md` row bumps + `harness-od/CLAUDE.md` §4.1 row transit + memory entries |
| Cross-axis cascade | ZERO (intra-OD-axis only) |
| Test posture | 3388/3388 pass + 10 skipped (was 3367 + 10 pre-arc; +21 NEW) |
| Advisor application count this arc | 30th — pre-substantive consultation at arc opening caught X-AL-2 risk + sharpened scope to all-3-triggers (tier-transit shape) vs single-trigger (within-PARTIAL refinement) per AskUserQuestion ratification |
