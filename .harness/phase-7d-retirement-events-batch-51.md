# Phase 7d Retirement Events — Batch 51

| Field | Value |
|---|---|
| Batch number | 51 |
| Filed at | 2026-06-01 (roadmap R-007 + R-009 close arc; both unblocked once `R-100-mvp-real-workflow-execution` RESOLVED 2026-06-01) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–6 + workflow v1.12 §7.4.7.3.C retirement-tier-transit audit-template applied at `harness-od/CLAUDE.md` §4.1 OD-3 + OD-6 rows |
| Predecessor batch | `phase-7d-retirement-events-batch-50.md` (2026-05-31 — H_T-IS-2 PARTIAL → RETIRED; IS-axis 9/9 RETIRED = 100%) |

---

## §0 Batch context

**Status type: 2 RETIRE-READY → RETIRED transits (H_T-OD-3 + H_T-OD-6), via two distinct closure-event-classes.** This batch closes roadmap `R-007-od-3-sampler-retired` + `R-009-od-6-otlp-retired`, both of which flipped BLOCKED → eligible per `Project_Roadmap_v1.md` §4 step 3 once their sole hard dependency `R-100-mvp-real-workflow-execution` RESOLVED (2026-06-01, all 4 ACs PASS). The two are **NOT a uniform pair** — a per-substitution X-AL-2 condition-(B) audit (the load-bearing discriminator per `[[verification-shape-sharpened-grep-vs-e2e]]`) lands them on different shapes:

- **H_T-OD-3 → substantive RETIRED** via the `gate-text-stale-vs-production-landings` audit (workflow v1.12 §7.4.7.2 sub-species 10; mirror precedent OD-1 batch-37 + OD-7 batch-38).
- **H_T-OD-6 → RETIRED-AS-BOUNDED-RESIDUAL** per X-AL-2 §5.3 bounded-residual carry-forward — the **FIRST bounded-residual close in the ledger** (Surface VIII / Phase-8 disposition shape per `Project_Roadmap_v1.md` §1 Surface VIII).

**Cardinality delta.** Workspace RETIRED 46/54 → **48/54 = 88.9%** (+2; OD-3 substantive + OD-6 bounded-residual, the latter counted as accounted/closed per Surface VIII "RETIRED or RETIRED-AS-BOUNDED-RESIDUAL"); RETIRE-READY 2/54 → **0/54** (OD-axis RETIRE-READY bucket EMPTY); PARTIAL unchanged (OD-4 the sole OD-axis PARTIAL); pipeline-advanced UNCHANGED at **49/54 = 90.7%** (both are within-pipeline-advanced RETIRE-READY → RETIRED transits per X-AL-2). OD-axis: 5/8 RETIRED + 2/8 RETIRE-READY + 1/8 PARTIAL → **7/8 RETIRED (incl. OD-6 bounded-residual sub-disposition) + 0/8 RETIRE-READY + 1/8 PARTIAL (OD-4)**.

**Operator ratification.** Both dispositions ratified at AskUserQuestion 2026-06-01: OD-3 "Substantive RETIRED (Recommended)" over bounded-residual / keep-RETIRE-READY; OD-6 "Bounded-residual (Recommended)" over keep-RETIRE-READY / substantive-RETIRED. Class 2 in-execution operator decision per `phase-7-substitution-retirement` §5.3 + §7.

**Pre-substantive advisor pass (this arc).** Advisor caught that the initial framing pre-committed both substitutions to bounded-residual from gate-text alone, without running the X-AL-2 condition-(B) audit. The advisor named (not pre-judged) the discriminator: *what H_E surface does each substitute, and is it still invoked at MVP/LOCAL?* — and flagged the OD-1/OD-7 same-bucket substantive-RETIRED precedent. Running the audit produced the split below. `[[advisor-before-substantive-work-for-cross-axis-blockers]]` continues to validate.

---

## §1 H_T-OD-3 (Composite Sampler) — RETIRE-READY → RETIRED (substantive)

### §1.1 Condition-(B) audit (gate-text-stale-vs-production-landings)

The pre-batch-51 OD-3 gate text framed the RETIRED transit as gated on "operator deploys harness at production deployment surface + real OTel span emission against OTLP collector observing §10.2 preservation semantic." Empirical audit against the H_E substitution surface (Meta-Architecture §5.5 OD-axis row 3) + production wiring discriminates:

| Check | Finding | Authority |
|---|---|---|
| 1. H_E substitution surface (§5.5) | OD-3 substitution mechanism = *"project-authored `Sampler` subclass at MCP server per `opentelemetry.sdk.trace.sampling.Sampler` ABC; head-based at cell-1 (local-first); tail-based discipline not invoked during 7a."* The H_E-coverage classification is `✗ — No sampling-discipline surface`. | Meta-Architecture §5.5 OD row 3 + line 633 (H_E coverage) + line 735 (substitution mechanism) |
| 2. Production substrate (cond A) | `HarnessCompositeSampler(Sampler)` LANDED at `harness-od/src/harness_od/composite_sampler.py`; per-cell base_rate envelope `PER_CELL_BASE_RATE_ENVELOPE` resolved at `harness-runtime/src/harness_runtime/lifecycle/tracer_provider.py:materialize_tracer_provider_stage` (lines 194 + 231). Cited units U-OD-09 → U-OD-12 LANDED. | grep at HEAD; OD spec v1.27 §9/§10 |
| 3. Sampler live at MVP (cond B) | The production `HarnessCompositeSampler` IS the active root sampler at every TracerProvider build (`ParentBased(root=HarnessCompositeSampler(...))`). The R-100-mvp-real-workflow-execution e2e emitted real Anthropic-inference spans through this production tracer provider (R-100 RESOLVED 2026-06-01). The 7a-scaffold "project-authored Sampler subclass at MCP server" is **replaced** — no longer the active sampler. | grep + R-100 e2e (`test_r100_real_workflow_e2e.py`) |
| 4. "tail-keep at OTLP collector" reclassified | `TailKeepSpanProcessor` is **bypassed at LOCAL_DEVELOPMENT by design** (§9.1 head-based mandate; wraps BSP iff `deployment_surface != LOCAL_DEVELOPMENT`). Observing the §10.2 preservation semantic at a real collector is **production-feature-validation at SELF_HOSTED_SERVER / MANAGED_CLOUD surfaces** (roadmap R-430, infra-gated) — NOT an X-AL-2 retirement criterion. The X-AL-2 criterion is (A) units landed ∧ (B) H_E surface no longer invoked; neither references collector-side preservation observation. | OD spec v1.27 §9.1 + X-AL-2 (Meta-Arch §7.7) |

**Discriminator outcome.** The OD-3 sampler primitive is **live at MVP** (the production head-based sampler runs on every span decision at LOCAL); the H_E 7a-scaffold sampler is no longer invoked; the tail-keep gradient is wired and correctly deployment-surface-conditional by design. The gate text conflated production-feature-validation (R-430) with the X-AL-2 retirement criterion. Treating collector-side preservation observation as a retirement gate would import a feature-validation requirement X-AL-2 does not mandate — the same `gate-text-stale-vs-production-landings` shape that closed OD-1 (batch-37) and OD-7 (batch-38).

**Distinction from OD-1/OD-7 (authoring-only).** OD-1/OD-7 closed RETIRED-AS-AUTHORING-ONLY because their H_T contract was "the typed declaration itself" with no runtime behavior. OD-3 is a **stronger** close: the sampler is a real runtime behavior **exercised at MVP**, replacing the H_E scaffold sampler. This is substantive substitution-retirement (the OD-2 / OD-5 shape — production substrate live), not authoring-only.

### §1.2 Criterion verification

- **Criterion A** (cited unit IDs landed). MET. U-OD-09 → U-OD-12 landed; `HarnessCompositeSampler` + `PER_CELL_BASE_RATE_ENVELOPE` + `is_always_sampled` + `TailKeepSpanProcessor` substrate all at HEAD.
- **Criterion B** (substituted H_E surface no longer invoked at substitution site). MET. The 7a-scaffold "project-authored Sampler subclass at MCP server" is no longer the active sampler — `materialize_tracer_provider_stage` binds `HarnessCompositeSampler` as the root sampler at every TracerProvider, and the R-100 real-workflow e2e exercised that production path with real spans. The H_E scaffold sampler is not invoked at MVP.

**Residual (feature-validation, NOT retirement gate).** Production tail-keep-on-classification behavior at a real OTLP collector (SELF_HOSTED_SERVER / MANAGED_CLOUD) is exercised at roadmap R-430 (infra-gated). This is feature-validation of a wired-and-deployment-conditional behavior, not an open retirement criterion.

---

## §2 H_T-OD-6 (Local-first OTLP ingestion) — RETIRE-READY → RETIRED-AS-BOUNDED-RESIDUAL

### §2.1 Condition-(B) audit (LANDED-substrate-pending-upstream-loop)

| Check | Finding | Authority |
|---|---|---|
| 1. H_E substitution surface (§5.5) | OD-6 substitution mechanism = *"user-launched OTel Collector subprocess via `Bash` (`otelcol --config ./otel-config.yaml &`); writes to local sqlite via OTLP→sqlite exporter; TUI deferred (CLI-only inspection via `Bash(sqlite3 ...)`) during 7a."* H_E-coverage = `✗ — No in-process OTLP collector exposed`. Mechanism category: SHELL-OUT. | Meta-Architecture §5.5 OD row 6 + line 636 + line 738 |
| 2. Production substrate (cond A) | 4-OD-B SqliteWritePath cluster LANDED (U-OD-23 → U-OD-27 / U-OD-42 → U-OD-45): `sqlite_span_store.py` 14-col schema + `insert_spans` + `RuntimeRingBuffer.flush_to_sqlite` + retention helper + reader module. | grep at HEAD; OD spec v1.25 §C-OD-27 |
| 3. Primitive dormant at MVP (cond B) | `flush_to_sqlite` has **ZERO production callers** — the only `src/` references are the method definition (`ring_buffer.py:300`), its docstrings (`ring_buffer.py:110`, `types.py:421`), and a comment in `sqlite_span_store.py`. No bootstrap stage, run-loop, or drain path invokes the in-process collector → sqlite flush. The primitive is built but **not wired into the MVP runtime path**. | grep at HEAD (non-test callers of `flush_to_sqlite`) |
| 4. Boundary has not moved | X-AL-1 retirement moves the boundary from "H_E owns the primitive" to "H_T owns the primitive." For OD-6 at MVP: the H_E `Bash(otelcol)` shell-out is not invoked (the harness uses the OTel SDK → BSP → exporter directly), **and** the H_T replacement (in-process collector → `flush_to_sqlite`) is not invoked either. Neither side is active at MVP; the boundary has not moved. The substantive RETIRED transit genuinely requires an operator deployment that wires + exercises the collector daemon → `flush_to_sqlite` loop (roadmap R-420 / R-421, infra-gated). | X-AL-1 (Meta-Arch §7.7) + `[[landed-substrate-pending-upstream-loop-substrate]]` |

**Discriminator outcome.** Substrate landed (criterion A MET) but the collector→sqlite primitive is **dormant at MVP** — recording substantive RETIRED would assert a wired surface that is actually un-invoked (the silent-X-AL-3-absorption risk: "substrate emitting into a void"). Per X-AL-2 §5.3, the honest disposition is **RETIRED-AS-BOUNDED-RESIDUAL**: closed for Phase-8 accounting with documented rationale + future-milestone pointer, not a substantive in-CLI retirement.

### §2.2 Bounded-residual log entry (X-AL-2 §5.3)

| Required field (skill §5.3) | Content |
|---|---|
| Substitution ID | H_T-OD-6 (Local-first OTLP ingestion: in-process collector + sqlite + TUI) |
| Documented rationale | Substrate (4-OD-B SqliteWritePath cluster) is LANDED, but the in-process collector → `RuntimeRingBuffer.flush_to_sqlite` loop has zero production callers at MVP — the primitive is dormant. The X-AL-2 second conjunct ("H_E surface no longer invoked") is technically true (no `Bash(otelcol)` shell-out at MVP) but the H_T replacement is not invoked either; the boundary has not moved. A substantive RETIRED is not honestly available at MVP. |
| Future milestone that unblocks | Operator deploys the harness with the collector daemon wired into the run loop (`flush_to_sqlite` invoked against a real sqlite span store, `.harness/observability/spans.db` observed populated) — roadmap R-420 (SELF_HOSTED_SERVER e2e) / R-421 (MANAGED_CLOUD e2e). Infra-gated; out of MVP scope. At that milestone OD-6 transits bounded-residual → substantive RETIRED. |
| Operator decision | Ratified at AskUserQuestion 2026-06-01 (Class 2 in-execution decision per skill §5.3). |

### §2.3 Criterion verification

- **Criterion A** (cited unit IDs landed). MET. U-OD-23 → U-OD-27 / U-OD-42 → U-OD-45 substrate at HEAD.
- **Criterion B** (substituted H_E surface no longer invoked at substitution site). **BOUNDED.** The `Bash(otelcol)` / `Bash(sqlite3)` shell-out is not invoked at MVP, but the H_T replacement loop is not invoked either — the primitive is dormant, boundary unmoved. Classified RETIRED-AS-BOUNDED-RESIDUAL rather than substantive RETIRED per the honest reading.

---

## §3 Sub-row substitution-status table

Post-batch-51 OD-axis bucket:

| Substitution | Status | Source |
|---|---|---|
| H_T-OD-1 (deferral envelope) | RETIRED batch-37 (authoring-only) | sub-species 10 |
| H_T-OD-2 (OTel SDK base + GenAI semconv) | RETIRED batch-2 | LIVE at `lifecycle/llm_dispatch.py` |
| H_T-OD-3 (Composite Sampler) | **RETIRE-READY → RETIRED at this batch (batch-51, substantive)** | sampler live at MVP via `materialize_tracer_provider_stage`; H_E 7a-scaffold sampler no longer invoked; gate-text-stale-vs-production-landings audit; tail-keep-at-collector reframed as R-430 feature-validation |
| H_T-OD-4 (Pre-Collector redaction SpanProcessor) | PARTIAL (refined) | gate (a) §13.1 partially closed at PR #25; per-session toggle + gate (b) §13.2 deferred |
| H_T-OD-5 (Cost-attribution 5-step chain) | RETIRED batch-32 | mech-β AC #8 green |
| H_T-OD-6 (Local-first OTLP ingestion) | **RETIRE-READY → RETIRED-AS-BOUNDED-RESIDUAL at this batch (batch-51)** | substrate landed; `flush_to_sqlite` dormant at MVP (zero callers); deployment-gated loop-wiring; FIRST bounded-residual close in ledger; future milestone R-420/R-421 |
| H_T-OD-7 (Preservation invariants 5-dimension) | RETIRED batch-38 (authoring-only) | sub-species 10 |
| H_T-OD-8 (aggregate manifest + Stage 3b inversion) | RETIRED (v1 §1 authoring-only) | Authoring-close |

Post-batch-51 OD-axis bucket: **7 RETIRED (incl. OD-6 bounded-residual sub-disposition) + 0 RETIRE-READY + 1 PARTIAL (OD-4) + 0 STILL-BOUNDED = 8**. OD-axis pipeline-advanced 8/8 = 100% (unchanged).

Workspace-layer cumulative post-batch-51: **48/54 RETIRED (88.9%, incl. 1 RETIRED-AS-BOUNDED-RESIDUAL = OD-6) + 0/54 RETIRE-READY + remaining PARTIAL / STILL-BOUNDED / STILL-BOUNDED-INDEFINITELY per ledger-v2 §11.5 baseline**. Pipeline-advanced (R+RR+P): **49/54 = 90.7%** (UNCHANGED — both transits are within-pipeline-advanced RETIRE-READY → RETIRED). Exact non-RETIRED cardinality reconciled at ledger-v2 §11.4i/§11.4j + the dashboard refresh.

---

## §4 Adjacent observations

(a) **FIRST RETIRED-AS-BOUNDED-RESIDUAL close in the ledger.** OD-6 is the first substitution closed under the X-AL-2 §5.3 bounded-residual carry-forward disposition (Surface VIII / Phase-8 shape per `Project_Roadmap_v1.md` §1). Prior closes were substantive RETIRED (OD-2 / OD-5 / OD-3-this-batch) or RETIRED-AS-AUTHORING-ONLY (OD-1 / OD-7 / OD-8). The bounded-residual disposition is the canonical Phase-8 accounting shape for a landed-but-deployment-gated primitive; recording it now (rather than deferring to R-700) drains an R-700 blocker with an honest, documented residual.

(b) **The two OD closes are NOT a uniform pair.** The discriminator is whether the primitive is live or dormant at MVP — OD-3's sampler runs on every span decision (live → substantive RETIRED); OD-6's collector→sqlite loop has zero callers (dormant → bounded-residual). A pre-committed uniform close (both bounded-residual, as initially framed) would have understated OD-3 and mis-shaped the operator AUQ. The per-substitution condition-(B) audit (advisor-prompted) is what produced the correct split.

(c) **`gate-text-stale-vs-production-landings` (sub-species 10) — THIRD closure.** OD-3 joins OD-1 (batch-37) + OD-7 (batch-38) as the third sub-species-10 closure. Distinctive at OD-3: it is the first sub-species-10 close where the primitive has **live runtime behavior** (sampler) rather than authoring-only typed-declaration — the stale gate-text conflated production-feature-validation (R-430) with the retirement criterion, rather than conflating a runtime-enforcement-loop with a static-contract.

(d) **R-007 + R-009 RESOLVED — 2 R-700 Phase-8 blockers drained.** Both roadmap entries declare `blocks: [R-700-phase-8-substitution-accounting]`. With OD-3 + OD-6 closed, the remaining non-RETIRED substitutions gating R-700 are OD-4 (PARTIAL; gate (b) §13.2 + per-session toggle) + AS-8e / AS-8f (DEFERRED-INDEFINITELY, R-005/R-006). Phase-8 full close (R-700) now has a substantially shorter blocker set.

(e) **ZERO production code change; ZERO test change; ZERO spec / plan amendment; ZERO cross-axis cascade.** This batch is retirement-event bookkeeping (batch-51 + harness-od/CLAUDE.md §4.1 + ledger-v2 §11 + roadmap §5 R-007/R-009 + dashboard). The production substrate for both substitutions was landed at prior batches; this batch records the tier transit + disposition.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-51.md` |
| Filed at | 2026-06-01 |
| Phase | Phase 7 sub-phase 7d — substitution retirement |
| Predecessor batch | batch-50 (H_T-IS-2 PARTIAL → RETIRED) |
| Transits | H_T-OD-3 RETIRE-READY → RETIRED (substantive); H_T-OD-6 RETIRE-READY → RETIRED-AS-BOUNDED-RESIDUAL (first in ledger) |
| Roadmap closures | R-007-od-3-sampler-retired RESOLVED; R-009-od-6-otlp-retired RESOLVED |
| Co-published artifacts | `harness-od/CLAUDE.md` §4.1 OD-3 + OD-6 rows + cumulative-counts line + gate sub-sections refresh; `.harness/phase-7d-retirement-ledger-v2.md` §11.4i + §11.4j + §11.5; `Project_Roadmap_v1.md` §5 R-007 + R-009; `.harness/roadmap_status.md` dashboard |
| Operator ratification | AskUserQuestion 2026-06-01 (OD-3 substantive RETIRED; OD-6 bounded-residual) — Class 2 in-execution decision per skill §5.3 |
| Cross-axis cascade | ZERO (intra-OD-axis retirement bookkeeping) |
| Production code change | ZERO |
| Test addition | ZERO |
| Spec / plan amendment | ZERO |
| Advisor application this arc | pre-substantive consultation caught the bounded-residual pre-commit + named the condition-(B) discriminator that produced the OD-3/OD-6 split |
