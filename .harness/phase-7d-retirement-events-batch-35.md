# Phase 7d Retirement Events — Batch 35

| Field | Value |
|---|---|
| Batch number | 35 |
| Filed at | 2026-05-28 (post PR #22 `OD-4 RedactionSpanProcessor` merge to main at `18d07e9` — substrate retired + runtime wiring at `materialize_span_processor_stage` BEFORE the BatchSpanProcessor) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5; STILL-BOUNDED → PARTIAL transit per harness-od/CLAUDE.md §4.1 H_T-OD-4 retirement-criterion ladder |
| Predecessor batch | `phase-7d-retirement-events-batch-34.md` (2026-05-28 — H_T-OD-3 STILL-BOUNDED → PARTIAL transit via PR #19 HarnessCompositeSampler merge; OD-4 batch-35 is the next-natural-gate sequel mirror-shape to OD-3 batch-34) |

---

## §0 Batch context

**Status type: 1 STILL-BOUNDED → PARTIAL transit (H_T-OD-4). Cumulative RETIRED count unchanged at 37/54 (68.5%); RETIRE-READY count unchanged at 1/54 (1.9%); PARTIAL count increments 4/54 → 5/54 (9.3%); STILL-BOUNDED count decrements 10/54 → 9/54 (16.7%); STILL-BOUNDED-INDEFINITELY count unchanged at 2/54 (3.7%); pipeline-advanced 42/54 → 43/54 = 79.6% (+1 net advancement — STILL-BOUNDED → PARTIAL is a tier promotion into the pipeline). Cardinality check: 37 + 1 + 5 + 9 + 2 = 54 ✓.**

This batch records the substrate-retirement transit for **H_T-OD-4** (Pre-Collector redaction SpanProcessor per OD spec v1.2 C-OD-12 §12.1 default-off content + default-on structure + C-OD-13 §13.2 pre-collector redaction at SDK / wrapper boundary BEFORE the BatchSpanProcessor buffer; carriers `harness-od/src/harness_od/redaction_span_processor.py` NEW + `harness-od/src/harness_od/content_structure_discipline.py` `DEFAULT_OFF_CONTENT_ATTRIBUTES` 13-attribute frozenset preserved; Meta-Architecture §5.4 row OD-4 Pre-Collector redaction SpanProcessor) from STILL-BOUNDED → PARTIAL via PR #22 merge:

| Commit | Artifact | Authority |
|---|---|---|
| `18d07e9` | `harness-od/src/harness_od/redaction_span_processor.py` NEW — `RedactionSpanProcessor(SpanProcessor)` ABC subclass with `on_end(span)` strip discipline + `on_start` / `force_flush` / `shutdown` no-ops + operator-injectable `redacted_attributes=` ctor kwarg; `harness-runtime/src/harness_runtime/lifecycle/span_processor.py` EXTEND — `materialize_span_processor_stage` constructs `RedactionSpanProcessor()` and registers it on the TracerProvider BEFORE the BSP per C-OD-13 §13.2 mandate; `SpanProcessorStage` extended with `redaction_processor` handle | PR #22 squash-merge to main 2026-05-28 |
| (this commit) | `.harness/phase-7d-retirement-events-batch-35.md` (this file) — retirement event filing documenting Criterion A + B structural transit at substrate layer | X-AL-2 first conjunct + harness-od/CLAUDE.md §4.1 H_T-OD-4 retirement ladder |
| (this commit) | `harness-od/CLAUDE.md` §4.1 row STILL-BOUNDED → PARTIAL transition for H_T-OD-4 + cumulative-counts line refresh + STILL-BOUNDED → PARTIAL + PARTIAL → RETIRE-READY gate ladder refresh per workflow v1.12 §7.4.7.3.C retirement-tier-transit audit | LANDED PRE-FILING at PR #22 (eager harness-od/CLAUDE.md amendment co-published with substantive arc; this batch acknowledges) |
| (this commit) | Memory entry `h-t-od-4-partial-batch-35.md` documenting the STILL-BOUNDED → PARTIAL transit + defense-in-depth empirical posture pattern | Workspace memory discipline |

Per the operator-ratified runtime-only substitution-site reading at `.harness/phase-7d-retirement-ledger-v2.md` §2.1 + line-33 strict-reading discipline + harness-od/CLAUDE.md §4.1 retirement-ladder:

> H_T-OD-4 (Pre-Collector redaction SpanProcessor): STILL-BOUNDED gate on `RedactionSpanProcessor` authoring + integration at materialize_span_processor_stage upstream of OTLPSpanExporter. (post-batch-2 span-emission activity makes this materially relevant)
> PARTIAL transit closes the STILL-BOUNDED gate at substrate authoring + runtime wiring integration.
> RETIRE-READY transit gates on (a) per-persona-tier override toggle at solo-developer per C-OD-13 §13.1 acceptance #3 (`persona_tier` + per-session override flag deferred at HEAD) + (b) opaque-token tokenization mode per C-OD-13 §13.2 multi-tenant-compliance eval-grade pipeline (strip-not-tokenize MVP scope-lock).
> RETIRED transit gates on operator deployment exercising the redaction surface against real workload + verifying §12.1 default-off content keys absent from collector-observed spans.

Under that discipline, H_T-OD-4 transitions STILL-BOUNDED → **PARTIAL** via PR #22:

- **Criterion A** (cited unit IDs landed). MET at this batch. `RedactionSpanProcessor` class subclasses `opentelemetry.sdk.trace.SpanProcessor` with `on_end(span: ReadableSpan) -> None` iterating `span._attributes` and stripping any key in `DEFAULT_OFF_CONTENT_ATTRIBUTES` via `del span._attributes[key]` (OTel-Python `BoundedAttributes` mutation idiom; mutable while span non-immutable per empirical verification). `on_start` / `force_flush` / `shutdown` no-ops per spec absence of buffer at this processor. Operator override via ctor `redacted_attributes=frozenset[str]` kwarg.

- **Criterion B structural-MET at this batch.** Three binding-chain stages empirically verified for the SDK-boundary substrate:
  - Stage 1 (carrier landed) — `RedactionSpanProcessor` exposed at `harness-od/src/harness_od/redaction_span_processor.py`; 14 unit tests at `harness-od/tests/test_redaction_span_processor.py` verify default strip-set cardinality (= 13) + OTel GenAI semconv 1.41.0 Opt-In subset (8 keys) + cross-namespace content surfaces (5 keys: `mcp.tool.call.{arguments,result}` + `skill.body_content` + `memory.content` + `files.content`) + on_end strip discipline + §12.2 structure-attribute preservation + zero-attribute span tolerance + lifecycle no-ops + operator-injected custom strip-set.
  - Stage 2 (production consumer site) — `harness-runtime/src/harness_runtime/lifecycle/span_processor.py:materialize_span_processor_stage` constructs `RedactionSpanProcessor()` at composer time alongside BSP and registers redaction FIRST on the TracerProvider via `provider.add_span_processor(redaction_processor)` BEFORE `provider.add_span_processor(bsp)`. `SpanProcessorStage` (frozen dataclass) extended with `redaction_processor: RedactionSpanProcessor` handle. 2 NEW wiring tests at `harness-runtime/tests/test_lifecycle_span_processor.py` verify the full §12.1 13-attribute set stripped at export time through full composition.
  - **Stage 3 (e2e exercise PASS against real substrate) — NOT MET at this batch.** Production workflow has not yet executed a real OTel span emission path against an OTLP collector observing absence of §12.1 default-off content keys at production runtime; the deployment-time exercise that confirms the substrate's contract semantic against real ingest is owed at a follow-on operator-bound deployment. Note: ZERO production `span.set_attribute(...)` calls against the 13 redaction-set keys at HEAD (grep verified pre-substantive at advisor 29th application) — PR is **defense-in-depth at HEAD**; any future producer setting a content-bearing key will be silently stripped before reaching BSP.

- **PARTIAL → RETIRE-READY gates remaining** (per C-OD-13 §13.1 + §13.2 + advisor 29th application MVP scope-lock):
  - Per-persona-tier override toggle at solo-developer per C-OD-13 §13.1 acceptance #3 — `persona_tier` not plumbed at the materializer at HEAD; MVP enforces hard default-off at all 3 tiers. Future arc threads `persona_tier` + per-session override flag through `RuntimeConfig` to `RedactionSpanProcessor` ctor.
  - Opaque-token tokenization mode per C-OD-13 §13.2 multi-tenant-compliance eval-grade pipeline — MVP implements the "omitted entirely" arm; the "redacted to opaque tokens" arm (e.g., `[REDACTED:PII]` / `[REDACTED:MCP_ARG]`) is the eval-grade pipeline shape at multi-tenant-compliance cells; deferred to multi-tenant-compliance deployment arc.

## §1 Substrate-only-retired-arc empirical posture

PR #22 is a **defense-in-depth substrate** at HEAD — ZERO production `span.set_attribute(...)` callsites at any of the 13 `DEFAULT_OFF_CONTENT_ATTRIBUTES` keys across `harness-{runtime,cp,as,od}/src` per advisor 29th application empirical orientation grep. The redaction discipline is wired but never exercised against real producer output at HEAD; tests demonstrate the strip discipline by manually calling `span.set_attribute(...)` on the redacted keys.

This is the **expected posture** for the substrate-only-retired-arc sub-species (sibling to OD-3 batch-34's substrate-only-retired-arc + latent-substrate-bug-closure pattern). The retirement transit is real at the substrate criterion-B layer; full RETIRED gates on operator deployment exercising the redaction surface against real workload where a future producer (e.g., a new GenAI integration that opts into content capture per C-OD-13 §13.1 solo-developer toggle, or a managed-agents.* producer setting `gen_ai.tool.call.arguments`) emits content-bearing attributes that the processor then strips.

## §2 Sub-row substitution-status table

Pre-batch-35 OD-axis bucket (post-batch-34):

| Substitution | Status | Source |
|---|---|---|
| H_T-OD-1 (deferral envelope) | STILL-BOUNDED | No `deferral_envelope` import in `harness-runtime/` |
| H_T-OD-2 (OTel SDK base + GenAI semconv) | RETIRED batch-2 (2026-05-20) | LIVE at `lifecycle/llm_dispatch.py` |
| H_T-OD-3 (Composite Sampler) | PARTIAL batch-34 (2026-05-28) | `HarnessCompositeSampler` + SDK-boundary wiring at `_DEFAULT_SAMPLER` |
| H_T-OD-4 (Pre-Collector redaction SpanProcessor) | **STILL-BOUNDED → PARTIAL at this batch (batch-35)** | `RedactionSpanProcessor` + runtime wiring at `materialize_span_processor_stage` BEFORE BSP; per-tier toggle + tokenization-mode gate RETIRE-READY |
| H_T-OD-5 (Cost-attribution 5-step chain) | RETIRED batch-32 (2026-05-28) | mech-β AC #8 green on main |
| H_T-OD-6 (Local-first OTLP ingestion) | RETIRE-READY batch-33 (2026-05-28) | 4-OD-B cluster landed; deployment-time opt-in gates RETIRED |
| H_T-OD-7 (Preservation invariants 5-dimension) | STILL-BOUNDED | Library carrier only; no runtime enforcement loop |
| H_T-OD-8 (aggregate manifest + Stage 3b inversion) | RETIRED (v1 §1 authoring-only) | Authoring-close |

Post-batch-35 OD-axis bucket: 2 RETIRED + 1 RETIRE-READY + 2 PARTIAL + 2 STILL-BOUNDED + 1 (OD-8 authoring-close) = 8.

Workspace-layer cumulative post-batch-35: **37/54 RETIRED (68.5%) + 1/54 RETIRE-READY (1.9%) + 5/54 PARTIAL (9.3%) + 9/54 STILL-BOUNDED (16.7%) + 2/54 STILL-BOUNDED-INDEFINITELY (3.7%)**. Pipeline-advanced (R+RR+P): 43/54 = 79.6% (+1 from batch-34; STILL-BOUNDED → PARTIAL is a tier promotion into the pipeline-advanced bucket per X-AL-2).

OD-axis pipeline-advanced: **6/8 = 75.0%** (3 RETIRED + 1 RETIRE-READY + 2 PARTIAL; was 5/8 = 62.5% at batch-34).

## §3 Adjacent observations

(a) **Second consecutive STILL-BOUNDED → PARTIAL transit in OD-axis.** Batch-34 OD-3 + batch-35 OD-4 form a **consecutive same-natural-gate-sequel pair** — both substrate-retirement-event mirror-shapes; both same-axis (OD); same calendar day (2026-05-28); both via single-session PR-merge-then-batch-filing arc. Pattern strengthens the "next-natural-OD-axis-gate" navigation precedent established in batch-34 §3 (a) note flagging OD-4 as natural sequel. OD-axis STILL-BOUNDED bucket now 2/8 (OD-1 + OD-7) — both library-carrier-only with explicit runtime-composer-loop gates remaining.

(b) **Defense-in-depth substrate-only-retired-arc pattern.** OD-4 batch-35 carries the same substrate-only-retired-arc shape as OD-3 batch-34 (substrate landed + wired; no production consumer yet emits content-bearing attributes that the substrate would strip). Distinct from OD-3's substrate-latent-bug-closure dimension — OD-4 has no latent bug; the discipline simply has no real producer to exercise at HEAD. Sub-species candidate at next workflow-doc revision: "substrate-defense-in-depth-no-current-producer" pattern, distinct from the OD-3 batch-34 "substrate-latent-bug-closure" sub-species but sibling-class via shared "substrate-only-retired-arc" parent.

(c) **No CXA cascade.** PR #22 ZERO cross-axis cascade verified at PR description; `redaction_span_processor.py` NEW + `span_processor.py` EXTEND + `SpanProcessorStage` field-set extension all intra-OD-axis substrate + intra-runtime-composition; no edge change at CXA v2.15.

(d) **MVP scope-lock at advisor 29th application.** Pre-substantive advisor consultation locked MVP at strip-not-tokenize + default-off-at-all-tiers (no per-persona-tier override) + persona_tier-not-plumbed + opaque-token-mode-deferred. Mirror-pattern to OD-3 batch-34 advisor 28th application MVP-scope-lock (`base_rate=1.0` hardcoded + over-sample-conservatively at conditional-by-attribute rows). Advisor-before-substantive-work discipline application count: **29** since pattern catalogued at `[[advisor-before-substantive-work-for-cross-axis-blockers]]`.

(e) **C-RT-06 step 3 wording empirically verified non-prohibitive.** Pre-substantive advisor priority-1 check resolved cleanly — runtime spec §6 (lines 1953-1979 at canonical v1 baseline) declares "Attach `BatchSpanProcessor(OTLPSpanExporter(...))` per OD spec C-OD-20 §20.1 collector-placement matrix" as the canonical step-3 contract but is **silent on processor count**. C-OD-12 §12.1 + C-OD-13 §13.2 explicitly mandate pre-collector redaction at "SDK / wrapper boundary BEFORE the BatchSpanProcessor buffer" — adding `RedactionSpanProcessor` before BSP IS implementing a spec-explicit discipline, NOT silent H_T design extension per X-AL-3. No Class 1 fork needed; PR landed via direct apply-pass.

(f) **`SpanProcessorStage` field-set extension.** Frozen dataclass extended with NEW field `redaction_processor: RedactionSpanProcessor` for shutdown-chain handle parity with existing `processor` + `exporter` fields. Field-set extension is intra-runtime-axis additive (no new contract); existing 11 test sites at `test_lifecycle_span_processor.py` preserved verbatim; 1 existing test (`test_materialize_returns_stage_with_processor_and_exporter`) extended in-place to assert the NEW field. NEW tests: 2 wiring tests covering single-key + full-13-key redaction at export.

(g) **Cumulative advisor + sub-species pattern progression.** This session (2026-05-28) sub-species catalogue progression:
- `3.forward-looking-code-comment-becomes-phantom-ledger-cite` catalogued at OD spec v1.25 + PR #17 + PR #18 + plan v2.24 (3 instances in 8 days);
- `substrate-only-retired-arc` parent pattern with 2 sub-species: `substrate-latent-bug-closure` (OD-3 batch-34) + `substrate-defense-in-depth-no-current-producer` (OD-4 batch-35; THIS batch).

Both sub-species are workflow-doc revision candidates at species-3 column extension or as NEW species at §7.4.7.2 retirement-event-pattern sub-species enumeration.

## §4 Filing footer

| Field | Value |
|---|---|
| Authored at | 2026-05-28 (this commit) |
| Authoring authority | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 |
| Predecessor | `phase-7d-retirement-events-batch-34.md` (next-natural-gate sequel; H_T-OD-3 PARTIAL was the precedent shape) |
| Successor | (TBD — next batch on next retirement-shape event) |
