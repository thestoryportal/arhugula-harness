# Class 3 Drift — C-OD-04 GenAI semconv binding-site silence vs `llm_dispatch.py:328` production emission

**Filed:** 2026-05-25 (surfaced during H_T-OD-2 retirement-state re-audit; OD-2 confirmed already RETIRED at batch-2 §4 from 2026-05-20 — this drift records the spec-side gap found during the re-audit, NOT a new retirement event)
**Status:** OPEN bounded — informational; non-blocking
**Routing target:** OD spec v1.11 future revision-pass — paired with next C-OD-04..C-OD-08 amendment
**Detection mode:** H_T-OD-2 retirement-state re-audit per `[[verification-shape-sharpened-grep-vs-e2e]]` — production binding chain verified MET at HEAD; spec-side binding-site silence surfaced as adjacent finding

---

## §1 — Defect surface

### §1.1 The asymmetry

`design-substrate/Spec_Operational_Discipline_v1_11.md` §C-OD-04 (per Implementation_Plan_Operational_Discipline_v2_18.md §3.2.1 U-OD-04) declares the **OTel GenAI semconv 1.41.0 base layer** as a cross-vendor floor:

- §4.1 span name format (3-component)
- §4.2 `gen_ai.operation.name` 7-value enum
- §4.3 4-tier `AttributeTier` classification (Required / Conditional / Recommended / Opt-In)
- §4.4 hierarchy correlation
- §4.5 base metric `gen_ai.client.token.usage`

`design-substrate/ADR-D6_v1_2.md` §1.2 names the base layer:

> Base layer — OTel GenAI semconv 1.41.0 [HIGH] as the cross-vendor floor.

**What the spec does NOT specify:** the production **binding site** — where in the runtime composer chain `gen_ai.*` attributes get set on a span. C-OD-04 through C-OD-08 specify attribute **shape** (which keys carry which values, which tier each attribute belongs to, which span-name format applies). The spec is **silent on WHO emits + WHERE in the runtime**.

### §1.2 The implicit binding (production state at HEAD)

`harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:328` opens the LLM dispatch span:

```python
with tracer.start_as_current_span(span_name) as span:
    # span_name = f"gen_ai.{provider_name}.{operation}" per C-OD-04 §4.1
    span.set_attribute("gen_ai.system", provider_name)
    span.set_attribute("gen_ai.request.model", model)
    # ... gen_ai.usage.input_tokens, gen_ai.usage.output_tokens, gen_ai.response.id
    # ... provider-specific anthropic cache attributes (read.tokens / creation.tokens / breakpoint.id / breakpoint.ttl)
```

This binding choice is **empirical** — verified at HEAD `d978612` via grep + 20 passing tests at:
- `harness-runtime/tests/test_lifecycle_llm_dispatch.py` (13 tests, including `test_genai_span_emits_required_attributes_for_openai` + `test_genai_span_handles_ollama_usage_shape` + `test_anthropic_cache_attributes_emitted_only_for_anthropic_provider`)
- `harness-runtime/tests/test_lifecycle_cost_attribution_llm_dispatch.py` (7 tests, including provider-coverage round-trips against `InMemorySpanExporter`)

The binding is correct under any reasonable reading of C-OD-04 (the LLM dispatch site is the natural emission point per §4.1 3-component span name format + §4.4 hierarchy correlation), but it is **implementation discovery**, not a spec-prescribed contract.

### §1.3 Why this is Class 3 (not Class 1)

Three convergent reasons:

1. **OD-2 is already RETIRED at batch-2 §4 (2026-05-20).** Verified via cumulative-count chain at batches 2/3/7 ("21/49 RETIRED post batch 6"), and explicit re-affirmation at batch-7 §2 ("H_T-OD-2 criterion-B re-affirmation (NO change)"). Ledger v2 §6 H_T-OD-2 PARTIAL row text is pre-batch-2 same-day stale (see `[[ledger-v2-section-6-od-2-row-stale-pre-batch-2]]`). Retirement is not gated on spec amendment; the binding chain has been live in production since 2026-05-20.
2. **The binding choice is architecturally unambiguous.** Per ADR-F1 v1.2 multi-LLM commitment + ADR-D6 §1.2 GenAI floor + C-OD-04 §4.1 span-name format, the LLM dispatch site is the only place the 3-component `gen_ai.{provider}.{operation}` name applies. No alternative binding site is structurally defensible at the abstraction level.
3. **The spec amendment is small and additive.** A new §C-OD-04.X sub-section (or addition to §C-OD-04 §4.4) naming the LLM dispatch span as the canonical binding site is ~15-25 lines + zero contract change at attribute layer. Parallel to the cost-axis Sub-arc B pattern: explicit-after-implicit absorbs production reality into design authority.

Halting H_T-OD-2 retirement at this drift is moot — OD-2 is already RETIRED per batch-2 §4. This drift is a pure spec-hygiene finding, independent of retirement status.

---

## §2 — Recommended routing

### §2.1 Spec-side amendment owed

Future OD spec revision-pass (likely v1.11 → v1.12) should add an explicit binding-site statement at C-OD-04. Recommended shape:

> **§4.6 Binding site.** `gen_ai.*` attributes per §4.3 are set at the **LLM dispatch span** (the 3-component span named per §4.1 opened by the runtime LLM dispatcher composer). The dispatch span is the unique architectural emission site for the GenAI base layer — no other composer in the runtime layer authors GenAI-semconv attributes. Implementation: `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py`.

Co-published with:
- OD plan v2.18 → v2.19 U-OD-04 absorption (1 NEW AC: "Production binding site is LLM dispatch span per §4.6")
- ZERO impl change owed (binding already in production at HEAD)
- ZERO test change owed (20 tests already exercise the binding)
- ZERO cross-axis cascade

### §2.2 Operator-discretion timing

Not gated on H_T-OD-2 retirement (OD-2 already RETIRED at batch-2). Folds into the next OD-axis spec-revision pass touching C-OD-04..C-OD-08 — or stands as a fidelity-only patch at operator discretion. Parallel folding precedent: `[[fork-cp-spec-section-25-contract-id-collision]]` retag-cascade folded into next CP-axis touching arc rather than firing standalone.

---

## §3 — Related forks + memory

- `[[verification-shape-sharpened-grep-vs-e2e]]` — discriminator audit followed the sharpening discipline (all 3 binding-chain stages verified empirically: carrier landed + span site exists + 20-test e2e exercise PASS). Without the sharpening, the May 20 ledger v2 cite "zero `gen_ai`/`gen_ai` references in tracer provider" would have been read as still-current and OD-2 would have remained PARTIAL.
- `[[h-t-cp-21-batch-15-down-classification]]` — parallel pattern: stale grep audit (looking at wrong file) → corrective close at next batch via empirical re-audit at the actual binding site.
- Cost-axis Sub-arc B at `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §6 — same explicit-after-implicit spec-hygiene pattern (production callsite preceded spec contract; spec catches up via narrow-scope amendment).

---

## §4 — Filing footer

| Field | Value |
|---|---|
| Class | 3 (informational; non-blocking) |
| Filed at | 2026-05-25, concurrent with batch-19 |
| Filing arc | H_T-OD-2 retirement-state re-audit (OD-2 confirmed RETIRED at batch-2; this drift is an adjacent spec-hygiene finding) |
| HEAD | `d978612` |
| Routing target | OD spec v1.11 → v1.12 future revision-pass (paired or standalone, operator discretion) |
| Blocks | NOTHING — OD-2 already RETIRED at batch-2 §4 (2026-05-20) |
| Co-published with | `.harness/class_3_drift_ledger_v2_section_6_od_2_row_stale_pre_batch_2.md` (separate finding from the same re-audit) |
