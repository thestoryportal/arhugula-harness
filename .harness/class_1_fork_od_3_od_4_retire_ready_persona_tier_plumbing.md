# Class 1 Fork — OD-3 + OD-4 RETIRE-READY persona_tier plumbing gap

**Status:** ✅ APPLIED-AS-READING-(α) (operator AskUserQuestion 2026-05-28 ratified Q1=A + Q2=A + Q3=a + Q4=i + Q5=α; single bundled binding-lift arc). Runtime spec v1.36 → v1.37 + OD spec v1.25 → v1.26 + OD plan v2.24 → v2.25 + production binding at `harness-runtime/types.py` + `harness-runtime/lifecycle/tracer_provider.py` + `harness-runtime/lifecycle/span_processor.py` + `harness-od/redaction_span_processor.py` + 16 NEW tests at `tests/test_persona_tier_plumbing.py` + workspace `CLAUDE.md` §2.3 + §2.4 row bumps + this Status update co-published 2026-05-28. H_T-OD-3 + H_T-OD-4 PARTIAL → RETIRE-READY substrate-criterion-B MET at apply arc; full RETIRED gates on operator deployment-time-opt-in exercise per X-AL-2. 3367/3367 tests pass + 10 skipped.
**Filed:** 2026-05-28 at OD-3 + OD-4 PARTIAL → RETIRE-READY arc open (post batch-34 + batch-35 substrate retirements).
**Filing site:** `.harness/class_1_fork_od_3_od_4_retire_ready_persona_tier_plumbing.md`.
**Halt point:** OD-3 §10.3 base_rate envelope + OD-4 §13.1 per-persona override toggle. No impl started.

---

## §0. Summary

Both OD-3 + OD-4 RETIRE-READY gates per `harness-od/CLAUDE.md` §4.1 ladder require `persona_tier`-aware behavior at the OTel SpanProcessor + Sampler boundary. Empirical orientation surfaces a structural blocker: **runtime spec C-RT-03 (RuntimeConfig schema) is silent on `persona_tier`**, while OD spec §13.1 reads `persona_tier` as a **per-deployment classification** for redaction-discipline purposes (`solo-developer` / `team-binding` / `multi-tenant-compliance` are deployment classes, not per-workflow attributes). Adding `RuntimeConfig.persona_tier` IS silent H_T design extension per X-AL-3 — fork-doc routing required.

The cross-axis empirical state also forecloses the only alternative shape (per-span attribute read at `on_end`): `workflow.persona_tier` is set ONLY on the workflow root span at `harness-cp/.../workflow_driver.py:608` and is NOT propagated to child spans (LLM / tool / etc.) via baggage or per-span set. Per-span attribute resolution at the SpanProcessor boundary would return None for ~all non-root spans.

Two distinct findings consolidated into one fork doc per workspace precedent for paired Class 1 surfaces sharing substrate (see `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]`).

---

## §1. Finding A — OD-3 §10.3 persona-tier-aware base_rate envelope (Class 1)

### §1.1 Authority surface

| Artifact | §-cite | Verbatim claim |
|---|---|---|
| OD spec v1.2 (preserved verbatim through v1.25) | §10.3 | Per-persona-tier base_rate envelope at sampler decision time |
| OD spec v1.2 | §9.3 | "deferred-to-discretion" — sampler-time persona_tier resolution mechanism not specified |
| harness-od/CLAUDE.md | §4.1 OD-3 row | PARTIAL → RETIRE-READY gate: §9.1 tail-keep-on-classification + §10.3 base_rate envelope |
| Runtime spec v1.36 | C-RT-03 RuntimeConfig | **SILENT** on `persona_tier` field |

### §1.2 Empirical contradiction

| Code site | Verbatim | Implication |
|---|---|---|
| `harness-runtime/.../lifecycle/tracer_provider.py:22` | `binds ParentBased(root=HarnessCompositeSampler(base_rate=1.0))` | Sampler constructed ONCE at startup with fixed `base_rate` |
| `harness-runtime/.../lifecycle/tracer_provider.py:25` | `HEAD_BASED_DEV` MVP `base_rate=1.0` matches §10.3 | MVP elides per-persona envelope |
| `harness-runtime/src/harness_runtime/types.py` | NO `persona_tier` field in `RuntimeConfig` | Spec-silent at materializer config layer |
| `harness-cp/src/harness_cp/workflow_driver.py:608` | `span.set_attribute("workflow.persona_tier", manifest_entry.persona_tier.value)` | Single emission site; root span only |
| `harness-cp/src/harness_cp/per_step_override_evaluator.py:151` | `persona_tier: PersonaTier` kw-param | CP-axis carriage is per-step (CP spec v1.17 §6.5) |

### §1.3 Why §10.3 base_rate envelope is structurally unimplementable at HEAD

`HarnessCompositeSampler` is constructed at `materialize_tracer_provider_stage` with a fixed `base_rate: float` per `tracer_provider.py:22`. OTel's `Sampler.should_sample(parent_context, trace_id, name, kind, attributes, links)` is invoked at span **start**. At span start, `workflow.persona_tier` attribute is NOT yet set on the span (workflow_driver sets it after span construction at `:608` — already inside the workflow root span's body, not before its creation). Per-span attribute read at sample-time returns None.

Three mechanisms could close the gap, each with structural cost:

| Mechanism | Shape | Cost |
|---|---|---|
| **(a) Per-deployment base_rate** | Read `RuntimeConfig.persona_tier` at materializer; pass `base_rate_for(persona_tier)` to `HarnessCompositeSampler` ctor | X-AL-3 silent extension at RuntimeConfig + spec §13.1 reframe at OD spec |
| **(b) Baggage propagation** | OTel baggage carries `workflow.persona_tier` across span hierarchy; sampler reads from baggage at `should_sample` | NEW substrate: baggage propagator at workflow_driver + sampler `should_sample` reads `baggage.get_baggage()` from parent context |
| **(c) Per-workflow tracer provider** | One `TracerProvider` per workflow run, each constructed with workflow's persona_tier-resolved base_rate | Structural rewrite: bootstrap `tracer_provider` becomes per-workflow not per-harness; breaks singleton assumption at U-RT-XX |

### §1.4 Routing options for OD-3

| Branch | Shape | Routing target | Cascade |
|---|---|---|---|
| (α) Per-deployment RuntimeConfig.persona_tier | NEW `RuntimeConfig.persona_tier: PersonaTier` field per (a); sampler reads at materialize-time. Spec extension at runtime spec C-RT-03 + OD spec §10.3 canonical-reading amendment ("per-deployment-persona-tier base_rate envelope"). | Runtime spec v1.36 → v1.37 + OD spec v1.25 → v1.26 + plan revisions | NO cross-axis cascade (OD + Runtime axes only) |
| (β) Baggage-propagation mechanism | NEW substrate: baggage propagator at workflow_driver entry; sampler reads `workflow.persona_tier` from OTel baggage. Spec extension at OD spec §10.3 ("baggage-propagated persona_tier resolution") + runtime spec NEW C-RT-NN baggage-propagation contract. | OD spec + runtime spec extension; new baggage carrier at harness-runtime | Possibly CP→Runtime convention seam at CXA |
| (γ) Defer §10.3 envelope; close OD-3 RETIRE-READY on §9.1 alone | Reframe OD-3 RETIRE-READY gate at harness-od/CLAUDE.md to require §9.1 tail-keep-on-classification only; §10.3 base_rate envelope deferred to multi-tenant-compliance eval-grade arc | harness-od/CLAUDE.md §4.1 amendment + OD spec §10.3 deferred-to-discretion amplification | NO cross-axis cascade |
| (δ) Defer OD-3 RETIRE-READY entirely | OD-3 stays PARTIAL until §9.3 deferred-to-discretion is resolved at operator-discretion timing | NO artifact change | NONE |

**Architect-leaning recommendation:** (α) per-deployment RuntimeConfig.persona_tier — matches OD spec §13.1's reading of persona_tier as deployment-classification; minimal new substrate; aligns with existing `deployment_surface` field shape at RuntimeConfig. Spec extension scope is narrow + single-axis-bounded.

---

## §2. Finding B — OD-4 §13.1 per-persona override toggle (Class 1)

### §2.1 Authority surface

| Artifact | §-cite | Verbatim claim |
|---|---|---|
| OD spec v1.2 | §13.1 | Per-persona-tier override gradient (solo-developer / team-binding / multi-tenant-compliance) with deployment-classified content-capture posture |
| OD spec v1.25 (delta-only) | C-OD-13 §13.1 | Acceptance #3 (per-persona toggle binding) |
| harness-od/CLAUDE.md | §4.1 OD-4 row | PARTIAL → RETIRE-READY gate: §13.1 per-persona override toggle + §13.2 opaque-token tokenization |
| Runtime spec v1.36 | C-RT-03 RuntimeConfig | **SILENT** on `persona_tier` field |
| `harness-od/.../redaction_span_processor.py` | (post-PR-#22) | RedactionSpanProcessor at MVP scope = strip-not-tokenize + default-off at all 3 persona tiers |

### §2.2 Empirical contradiction

PR #22 (batch-35) landed `RedactionSpanProcessor` with **hard default-off at all 3 persona tiers** per advisor 29th application MVP scope-lock. The §13.1 acceptance #3 per-persona toggle requires the processor to read `persona_tier` at `on_end(span)` decision time and gate strip vs preserve.

| Code site | Verbatim | Implication |
|---|---|---|
| `harness-od/.../redaction_span_processor.py:__init__` | `redacted_attributes` ctor kwarg | NO `persona_tier` param at ctor |
| `harness-od/.../redaction_span_processor.py:on_end` | strips all `redacted_attributes` keys unconditionally | NO per-persona gating |
| `harness-runtime/.../lifecycle/span_processor.py:materialize_span_processor_stage` | constructs RedactionSpanProcessor + wires pre-BSP | NO `persona_tier` threaded |
| `harness-runtime/types.py` (RuntimeConfig) | NO `persona_tier` field | Spec-silent |

### §2.3 Why §13.1 per-persona toggle is structurally unimplementable at HEAD

Same root cause as Finding A: `persona_tier` is not at `RuntimeConfig`. Two attribute-driven alternatives:

| Mechanism | Shape | Empirical state |
|---|---|---|
| **Per-span `workflow.persona_tier` attribute read** | `RedactionSpanProcessor.on_end` reads `span.attributes.get("workflow.persona_tier")` and gates strip | INFEASIBLE — only workflow root span carries the attribute; child spans (LLM / tool / etc.) return None at HEAD |
| **OTel baggage read at `on_end`** | Read `workflow.persona_tier` from current context's baggage | INFEASIBLE — no baggage propagator at workflow_driver; context may not be active at on_end |

### §2.4 Routing options for OD-4

| Branch | Shape | Routing target | Cascade |
|---|---|---|---|
| (α) Per-deployment RuntimeConfig.persona_tier | NEW `RuntimeConfig.persona_tier` field; `materialize_span_processor_stage` reads + constructs `RedactionSpanProcessor(persona_tier=config.persona_tier, ...)`. Processor gates strip per §13.1 row for that tier. | Runtime spec extension + OD spec §13.1 canonical-reading amendment | NO cross-axis cascade |
| (β) Baggage-propagation mechanism | NEW baggage propagator at workflow_driver entry sets `workflow.persona_tier` baggage; processor reads at `on_end` from context | OD spec + runtime spec extension | Possibly CP→Runtime convention seam |
| (γ) Per-span attribute-set at every emission site | Mandate every span emission site set `workflow.persona_tier`; child spans inherit via OTel propagation OR each emitter calls `set_attribute` | Cross-axis cascade across CP / AS / OD emission sites; X-AL-3 risk for "every span emits persona_tier" mandate | HIGH — touches every span carrier |
| (δ) Defer §13.1 per-persona toggle; close OD-4 RETIRE-READY on §13.2 alone | Reframe OD-4 RETIRE-READY gate to require §13.2 opaque-token tokenization only; §13.1 per-persona toggle deferred to multi-tenant arc | harness-od/CLAUDE.md §4.1 amendment | NONE |
| (ε) Defer OD-4 RETIRE-READY entirely | OD-4 stays PARTIAL until persona_tier-plumbing arc is operator-routed | NONE | NONE |

**Architect-leaning recommendation:** (α) per-deployment RuntimeConfig.persona_tier — same shape as Finding A; the deployment-classification reading at §13.1 matches the RuntimeConfig surface; advisor 29th application's MVP scope-lock at "default-off at all 3 persona tiers" can lift to "default-off at solo-developer + team-binding; default-strip at multi-tenant-compliance" without spec extension beyond §13.1's existing gradient table.

---

## §3. Shared substrate — `RuntimeConfig.persona_tier` field

If (α) is selected for both findings (recommended), the shared substrate is:

```python
# harness-runtime/src/harness_runtime/types.py — RuntimeConfig
from harness_core.persona_tier import PersonaTier

class RuntimeConfig(BaseModel):
    # ... existing fields ...
    persona_tier: PersonaTier  # NEW per OD spec §13.1 deployment-classification
```

Source resolution per U-RT-103 `RuntimeConfigSource`: env var `HARNESS_PERSONA_TIER` / `harness.toml` `persona_tier` / CLI flag `--persona-tier` (lowest → highest priority); pydantic-settings precedence already in place.

Materializer consumers:
- `materialize_tracer_provider_stage` reads `config.persona_tier` → constructs `HarnessCompositeSampler(base_rate=base_rate_for(config.persona_tier))` (Finding A close)
- `materialize_span_processor_stage` reads `config.persona_tier` → constructs `RedactionSpanProcessor(persona_tier=config.persona_tier, ...)` (Finding B close)

OD spec §13.1 canonical-reading amendment shape: explicit statement that `persona_tier` at §13.1 refers to deployment-binding classification (read from `RuntimeConfig.persona_tier`), not per-workflow CP-axis `StepEffectiveBinding.persona_tier`. The two persona_tier surfaces co-exist by design: CP-axis carries per-step persona_tier for gate-level / engine-class / HITL-matrix purposes; OD-axis reads per-deployment persona_tier for sampling + redaction discipline purposes.

---

## §4. Cross-axis cascade analysis

| Axis | Touch under (α) | Touch under (β) | Touch under (γ) |
|---|---|---|---|
| Runtime spec | C-RT-03 NEW field | C-RT-NN NEW baggage-propagation contract | NONE |
| OD spec | §10.3 + §13.1 canonical-reading amendment | §10.3 + §13.1 baggage-mechanism amendment | NONE |
| CP spec | NONE (CP-axis per-step persona_tier preserved verbatim) | Possibly NEW baggage-emission contract at workflow_driver | Per-span emission cascade |
| CXA | NONE | Possibly NEW convention seam | NEW typed seam at every emission site |
| ADR-D6 | NONE (§1.4 per-persona override gradient preserved) | Possibly amendment | Possibly amendment |
| Production code | Runtime types.py + 2 materializers + RedactionSpanProcessor ctor | Workflow_driver baggage emission + 2 materializers + sampler/processor baggage read | Every span emission site |

(α) has the narrowest blast radius — single-axis spec extension at runtime + OD canonical-reading; intra-axis production binding.

---

## §5. Q-set for operator ratification

**Q1.** OD-3 RETIRE-READY arc shape:
- (A) Land (α) per-deployment RuntimeConfig.persona_tier for §10.3 base_rate envelope (recommended)
- (B) Land (β) baggage-propagation mechanism
- (C) Defer §10.3; close OD-3 on §9.1 alone (γ)
- (D) Defer OD-3 RETIRE-READY entirely (δ)

**Q2.** OD-4 RETIRE-READY arc shape:
- (A) Land (α) per-deployment RuntimeConfig.persona_tier for §13.1 per-persona toggle (recommended; pairs with Q1=A)
- (B) Land (β) baggage-propagation mechanism (pairs with Q1=B)
- (C) Defer §13.1; close OD-4 on §13.2 opaque-token tokenization alone (δ)
- (D) Defer OD-4 RETIRE-READY entirely (ε)

**Q3.** If Q1=A + Q2=A: arc bundle shape:
- (a) Single bundled arc: RuntimeConfig.persona_tier field + both materializer wirings + spec extensions + plan revisions co-published in one PR (recommended)
- (b) Sequenced: substrate arc (field + canonical-reading) first; OD-3 wiring arc; OD-4 wiring arc each in separate PR

**Q4.** Spec extension shape at runtime spec C-RT-03:
- (i) Single field-set extension at NEW §3.X sub-section authoring (mirrors `tenant_id` v1.22 binding-lift precedent)
- (ii) NEW §3.X sub-section + NEW §C-RT-NN persona-tier-aware-deployment-classification contract surface (heavier; treats persona_tier as 1st-class contract)

**Q5.** OD spec §13.1 amendment shape:
- (α) Canonical-reading amendment clarifying `persona_tier` at §13.1 is deployment-classification (read from RuntimeConfig); does NOT amend the per-persona gradient table (recommended)
- (β) Substantive amendment to §13.1 gradient table + explicit cross-axis CP↔OD persona_tier disambiguation sub-section

---

## §6. Recommended resolution (architect-leaning)

**Q1=A + Q2=A + Q3=a + Q4=i + Q5=α.** Single-arc bundled landing matching `tenant_id` v1.22 binding-lift precedent + `default_gate_level` v1.20 CP-spec extension precedent.

Estimated scope:
- NEW `RuntimeConfig.persona_tier: PersonaTier` field at `harness-runtime/types.py` (binding-fix shape with `PersonaTier.SOLO_DEVELOPER` default for backward-compat at existing 100+ test fixtures + 28-field RuntimeConfig construction sites)
- `RuntimeConfigSource` env / toml / CLI layered precedence already in place (U-RT-103); persona_tier picks up the same 3-source resolution at zero new wire-up cost
- Wire-up at `materialize_tracer_provider_stage` + `materialize_span_processor_stage`
- Runtime spec v1.36 → v1.37 NEW §3.X field declaration + canonical-reading amendment at §13.1 cross-cite
- OD spec v1.25 → v1.26 canonical-reading amendment at §10.3 + §13.1 (per-deployment-persona-tier reading)
- OD plan v2.24 → v2.25 NEW unit OR amendments at U-OD-04 / U-OD-05 (sampler + redactor wiring + tests)
- Production tests: RedactionSpanProcessor per-persona gating + HarnessCompositeSampler per-persona base_rate + RuntimeConfig field + 3-source resolution
- Closes OD-3 + OD-4 RETIRE-READY gates jointly under §13.1 deployment-classification reading

Estimated effort: human ~1 day / CC ~45 min.

---

## §7. Adjacent observations

- **Sub-species precedent**: `tenant_id` v1.22 CP spec binding-lift + `default_gate_level` v1.20 CP spec extension are both single-day fork-doc → ratify → apply arcs. `RuntimeConfig.persona_tier` matches the shape exactly.
- **§13.1 reading-classification ambiguity**: workspace carries a latent CP↔OD persona_tier semantic-axis disambiguation defect (CP-axis = per-step gate-resolution; OD-axis = per-deployment redaction discipline). Q5=α amendment surfaces + canonicalizes the disambiguation.
- **MVP scope-lock at PR #22 (RedactionSpanProcessor)**: "default-off at all 3 persona tiers" was advisor-ratified as MVP under the framing that per-persona toggle was deferred to a future arc. This fork doc IS that future arc.
- **No production behavior change at HEAD** for OD-3 — sampler MVP at `base_rate=1.0` already matches §10.3 deferred-to-discretion envelope; (α) landing extends behavior to honor per-deployment base_rate envelope without changing the MVP default.
- **PartialRetirement vs RetireReady gate semantics**: OD-3 + OD-4 currently PARTIAL because criterion B is structural-MET but per-persona behavior is hard-coded default. (α) landing closes criterion B at full §13.1 fidelity, advancing both rows to RETIRE-READY (terminal in-CLI; full RETIRED on deployment-time-exercise gate per X-AL-2).
- **Forward-looking-cite hygiene**: this fork doc cites runtime spec v1.36 + OD spec v1.25 + OD plan v2.24 as canonical at filing time; downstream readers verify against then-current spec/plan versions per delta-only-spec-file convention.

---

*End of fork doc.*
