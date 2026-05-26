# Class 3 Drift — Ledger v2 §6 H_T-OD-2 PARTIAL row text is pre-batch-2 same-day stale

**Filed:** 2026-05-25 (surfaced during H_T-OD-2 retirement-state re-audit)
**Status:** OPEN bounded — informational; pointer doc for future agents reading ledger v2 §6
**Routing target:** None — forward-only ledger discipline preserves ledger v2 byte-exact; this drift is a navigation aid, not an edit
**Detection mode:** retirement-state re-audit traced ledger v2 §6 PARTIAL claim against batch-2 §4 RETIRED filing (same day 2026-05-20)

---

## §1 — The drift

`design-substrate/`-side: N/A (this drift is `.harness/`-resident).

`.harness/phase-7d-retirement-ledger-v2.md` §6 row for H_T-OD-2:

> | H_T-OD-2 | OTel SDK base + GenAI semconv binding | **PARTIAL** | `materialize_tracer_provider_stage` constructs stock OTel `TracerProvider` globally registered. **GenAI semconv NOT bound**: zero `genai`/`gen_ai` references in `tracer_provider.py`. **Zero CP-driver span emission**: grep `get_tracer\|start_as_current_span` in `harness-cp/src` returns 0 hits — production execution path emits no spans. OTel SDK base present; GenAI binding absent; consumer path empty. **Blocks CXA-5 F-CP-01 Stage 3b inversion per §6.3.2** |

`.harness/phase-7d-retirement-events-batch-2.md` §4 (same day, 2026-05-20):

> ## §4 H_T-OD-2 — GenAI semconv 1.41.0 attribution at runtime
> | Substitution ID | H_T-OD-2 |
> | Condition B verification | `RuntimeLLMDispatcher.dispatch` Step 2 opens `with tracer.start_as_current_span(f"gen_ai.{provider_name}.{operation}")`; Steps 4-5 set `gen_ai.system` / `gen_ai.request.model` / `gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens` / `gen_ai.response.id` per provider-specific extraction. Tests at `tests/test_lifecycle_llm_dispatch.py::test_genai_span_emits_required_attributes_for_openai` + `test_genai_span_handles_ollama_usage_shape` verify attribute emission across all 3 providers.
> Status: **RETIRED**

**The inconsistency:** ledger v2 was authored before batch-2 fired on 2026-05-20; batch-2's RETIRED filing superseded ledger v2 §6's PARTIAL classification the same day. Ledger v2 §6 row text was never amended to reflect this — and the forward-only ledger discipline at every subsequent batch (§5 of every batch event) preserves the ledger v2 doc byte-exact.

The cumulative-count chain across batches 2/3/7/10/11/17/18 carries OD-2 as RETIRED:

- Batch-2: 15/49 RETIRED post (was 4 authoring-only pre; +11 transitions including OD-2)
- Batch-3 §1 cite: "H_T-OD-2 RETIRED batch 2 + H_T-CP-24 RETIRED authoring close"
- Batch-7 §2: "H_T-OD-2 criterion-B re-affirmation (NO change)"
- Batch-10/11 cumulative: 22/49 RETIRED (post additional transitions; OD-2 counted RETIRED)
- Batch-17/18 cumulative: 26/27/49 RETIRED (OD-2 still counted RETIRED)

The cumulative table is canonical per forward-only discipline. Ledger v2 §6 row text is a pre-batch-2 same-day artifact.

## §2 — Why this is Class 3 (not Class 1, not Class 2)

1. **Forward-only ledger discipline preserves ledger v2 byte-exact.** Editing ledger v2 §6 to mark OD-2 RETIRED would violate the discipline applied at every batch since batch-1.
2. **Cumulative table at every batch §3 is authoritative.** Future agents tracking retirement state must read batch event cumulative tables, not ledger v2 §6 row text.
3. **Class 3 because non-blocking + informational.** OD-2 is properly retired; the row drift only creates a navigation hazard for future agents reading ledger v2 §6 in isolation.

## §3 — Pattern catalogue: same-day-pre-batch-N stale ledger row

| Element | Specification |
|---|---|
| Trigger | A pre-batch-N audit document authored on day X classifies row R at status S; a batch-N event filed on the same day X re-classifies R at status S'; the audit document is not amended post-batch-N |
| Diagnosis | Audit document captures pre-batch-N world-state; batch-N supersedes specific row classifications same-day; cumulative ledger across batches is canonical |
| Resolution | Pointer doc (this filing) routes future agents reading the audit document to the canonical row classification at batch-N |
| Forward-only safety | Pointer doc is `.harness/`-resident, not a ledger edit; ledger v2 preserved byte-exact |
| Related memory | New memory entry owed for stale-grep PARTIAL re-audit pattern catalogue (parallels `[[verification-shape-sharpened-grep-vs-e2e]]`) |

## §4 — Recommended discriminator extension for future PARTIAL → RETIRED audits

When evaluating whether a row classified PARTIAL at any audit document is currently RETIRED:

1. Grep `H_T-{ROW}` across `.harness/phase-7d-retirement-events-batch-*.md` — find any prior retirement event filing.
2. If a prior RETIRED filing exists, cross-check the cumulative-count chain from that batch forward — the row should appear in every subsequent batch's cumulative table.
3. If the audit document's PARTIAL classification post-dates the prior RETIRED filing → audit may be wrong (re-check empirical state). If pre-dates → audit is superseded same-day or later.
4. Only proceed with a PARTIAL → RETIRED batch filing if no prior RETIRED event exists.

This 4th check joins the verification-shape 3-stage discipline at `[[verification-shape-sharpened-grep-vs-e2e]]` as a pre-pre-condition: **check the ledger before checking the binding chain**.

---

## §5 — Filing footer

| Field | Value |
|---|---|
| Class | 3 (informational; non-blocking; pointer doc) |
| Filed at | 2026-05-25 |
| Filing arc | H_T-OD-2 retirement-state re-audit (OD-2 confirmed RETIRED at batch-2 §4) |
| HEAD | `d978612` |
| Routing target | None — pointer doc; future agents reading ledger v2 §6 should cross-check batch-2 §4 + batch-event cumulative tables |
| Blocks | NOTHING |
| Co-published with | `.harness/class_3_drift_c_od_04_gen_ai_binding_site_silence.md` (separate spec-hygiene finding from the same re-audit) |
| Cumulative count canonical anchor | Batch-2 §4 RETIRED + every subsequent batch's §3 cumulative table including OD-2 in RETIRED count |
