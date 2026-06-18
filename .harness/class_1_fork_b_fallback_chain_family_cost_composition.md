# Class 1 Fork — B-FALLBACK-CHAIN-FAMILY-COST-COMPOSITION (populate the §15.3 cross-family family tag on production LLM cost records)

**Filed:** 2026-06-18 · R-FS-1 standalone `B-*` arc **B-FALLBACK-CHAIN-FAMILY-COST-COMPOSITION** (surfaced + registered at arc B-COST-DISCRIMINATOR-TAXONOMY; spine ledger `.harness/beyond-mvp-capability-boundary-ledger.md` line 120). Bundled-absorption posture: runtime spec **v1.57 → v1.58** (C-RT-09 §9 amendment — one new optional `RunResult` field + the v1.57 body-drift reconcile) + `harness-runtime/src`. Class 1 (X-AL-3 spec **surface extension** on a cleared spec — a new optional `RunResult` field + production population of the §15.3-reserved `provider_discriminator`). Design back-flow FULL-SPEC-pre-authorized (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`).

**Status:** ✅ RESOLVED + design decided — drives the impl. **NO operator gate.** The amendment is **additive** (a new optional `RunResult.cost_attribution_by_provider_discriminator` field + the production tagging that populates it) and sacrifices **no committed invariant** — OD spec v1.30 §15.1.2 already defines the field's `str | None` shape AND explicitly assigns its population to *this* arc (*"the field stays reserved for the §15.3 fallback-chain composition to populate"*), so this is **impl-to-cleared-spec**, runtime-only, no OD spec change. No nameable cross-domain tension (runtime-internal cost surfacing + a provider→family map) → advisor, **not council** (§10.9 discriminator applied explicitly). Adopt-and-note per workspace `CLAUDE.md` §12.4.1 + `[[feedback-gate-only-on-meaningful-architecture-change]]`; advisor-confirmed (advisor-not-council, no AUQ).

---

## §1 The fork — `RollupAxis.PER_PROVIDER_DISCRIMINATOR` is vacuous in production

The OD cross-family cost rollup `rollup_costs_by_axis(records, PER_PROVIDER_DISCRIMINATOR)` (`harness_od.cross_family_rollup:178`) keys on `SpanCostRecord.provider_discriminator` — the cross-family fallback-chain **family tag** (`frontier_managed` / `frontier_managed_alt` / `local_ollama`; C-OD-15 §15.1 / §15.3). After arc B-COST-DISCRIMINATOR-TAXONOMY (#644) corrected the dispatch-type-string defect, **every production LLM cost record writes `provider_discriminator = None`** (`cost_attribution_llm_dispatch.py:215`), so that axis is **defined + admissible but always empty** — there is no production producer of the family tag.

OD v1.30 §15.1.2 (the v1.30 change-note that registered this arc) is explicit: *"A per-dispatch cost record produced at the edge has no chain-level family context and carries `provider_discriminator = None`; the field is populated by the §15.3 fallback-chain composition (forward arc `B-FALLBACK-CHAIN-FAMILY-COST-COMPOSITION`)."* This arc is that population.

### §1.1 The apparent A/B fork — span-layer vs record-layer (false dichotomy, probe-resolved)

§15.3 (`Spec_Operational_Discipline_v1_2.md:891-898`, preserved verbatim) prescribes: *"Parent span retains `provider_discriminator` family tag; child retry spans carry per-attempt provider."* This read **against** §15.1's "Σ per-family cost (per-family cost visibility under fallback)" appeared to fork into:

- **Reading A (parent-record):** emit a *separate* parent-level family-tagged `SpanCostRecord` at the chain composer — but the existing `PER_PROVIDER_AND_MODEL` rollup sums **all** records, so a parent record risks double-counting dollars.
- **Reading B (tag-the-record):** stamp the existing per-dispatch record's `provider_discriminator` with its provider's family.

**The fork is a layer confusion, not a real fork (advisor-resolved).** §15.3 governs **OTel span attributes**; §15.1.2 governs the **`SpanCostRecord` field**. They are different artifacts. The discriminating sentence is §15.1.2: *"`SpanCostRecord.provider_discriminator`… **the field is populated** by the §15.3 fallback-chain composition"* — i.e. set the field **on the dispatch's existing record**, NOT emit a new parent record. That single reading:

- collapses A/B,
- kills the double-count worry **by construction** (one record per successful dispatch; the field is set, nothing is added to the accumulator),
- keeps the bare-edge default `None` (the OD `str | None` contract is unchanged; the *runtime* supplies the tag).

The optional honoring of §15.3 row 2 at the **span** layer (an outer-span family-tag attribute) is secondary and not the deliverable.

---

## §2 Resolution — tag the LLM cost record from the dispatched provider's family

### §2.1 Mechanism (runtime-internal, smallest blast radius)

The record is built inside `RuntimeLLMDispatcher.dispatch` → `_attribute_cost_best_effort` (`llm_dispatch.py`), which has `provider_name` in scope. The fix:

1. `attribute_llm_dispatch_cost` (`cost_attribution_llm_dispatch.py`) gains an **optional** `provider_discriminator: str | None = None` param, threaded into the `SpanCostRecord` (replacing the hard-coded `None`). The bare-edge default stays `None` (so any direct/test caller is unchanged).
2. `_attribute_cost_best_effort` derives the tag from `provider_name` via `cross_family_tag_for_provider` and passes it. Every production LLM dispatch flows through this path ⟹ every production LLM record is tagged.
3. NEW `harness_runtime/lifecycle/cross_family_cost_tag.py` homes the `ProviderFamily → CrossFamilyTag` map (+ the canonical provider→`ProviderFamily` map, now the **one source of truth** that `retry_breaker_fallback._provider_family` reuses).
4. `api.py` gains `_rollup_cost_attribution_by_provider_discriminator` + the new optional `RunResult.cost_attribution_by_provider_discriminator` field, wired at `_build_run_result`.

**No CP Protocol change, no OD spec change** — `StepExecutionContext`/`StepDispatcher` untouched; OD v1.30 §15.1.2 already owns the field semantics. Runtime spec v1.57 → v1.58 adds the one optional `RunResult` field (the v1.45 `pause_snapshot` / v1.57 `dispatch_kind` minor-bump precedent).

### §2.2 The mapping (provider-fixed, per the §15.1 example)

`ProviderFamily`(4) → `CrossFamilyTag`(3), following the §15.3 example chain "Anthropic → cross-family OpenAI/Gemini → local Ollama" (which groups **OpenAI/Gemini** as the cross-family middle tier):

| `ProviderFamily` | `CrossFamilyTag` |
|---|---|
| `ANTHROPIC` | `frontier_managed` |
| `OPENAI` | `frontier_managed_alt` |
| `GOOGLE` | `frontier_managed_alt` (grouped with OpenAI per §15.1 — **documented, not silent**) |
| `LOCAL_OPEN_WEIGHT` | `local_ollama` |

This is impl-to-cleared-**example**, not an invented taxonomy. `CrossFamilyTag` is deliberately **NOT extended** (the spec groups the two frontier-managed-alt families; a 4th member adds an OD surface for no rollup gain). The map is homed in `harness-runtime` because `CrossFamilyTag` is OD-homed + `ProviderFamily` is CP-homed ⟹ a map in either axis is a cross-axis cycle (`[[carrier-home-defect-pattern]]`).

### §2.3 The correctness invariant (LLM-subtotal partition — NOT full-run)

Unlike `cost_attribution` (PER_PROVIDER_AND_MODEL) and `cost_attribution_by_dispatch_kind` (PER_DISPATCH_KIND), which partition the **full** run dollar total, `PER_PROVIDER_DISCRIMINATOR` **skips `None`-tag records** (tool / validator / webhook dispatches have no provider family, §15.1.2). So:

> `Σ cost_attribution_by_provider_discriminator.total_cost == Σ(LLM-dispatch records).total_cost` (no LLM record double-counted), **NOT** `== total run cost`.

Asserting the full-run invariant here would be a false RED (the by-execution tests assert the LLM-subtotal invariant + that the other two axes' totals are unchanged → no regression / no double-count).

### §2.4 Scope honesty — `FallbackChainCostComposition` is NOT wired (hollow-producer trap avoided)

The arc registration names `FallbackChainCostComposition` (OD §15.3 carrier) as "the seam," but non-vacuity is met by `provider_discriminator` + the rollup field **alone**. `FallbackChainCostComposition` (per-attempt provider + cache-loss flag) has **no consumer** today — constructing it in production would be hollow (`[[r-cxa-seam-wiring-is-producer-discovery]]`). It is **not** built here; it stays a defined-but-unwired §15.3 carrier until a real consumer exists.

### §2.5 Sub-decision (consciously made, not gated) — tag every chain dispatch

Every LLM cost record is tagged with its resolved provider's family, **not only** when `cross_family_triggered`. This makes the axis non-vacuous in the common no-fallback case too (a single anthropic dispatch → `frontier_managed`) and matches §15.1's "per-family cost visibility under fallback." Documented; reversible.

---

## §3 Bundled changes (this arc)

| Surface | Change |
|---|---|
| `harness-runtime/src/.../lifecycle/cross_family_cost_tag.py` | **NEW** — provider→`ProviderFamily`→`CrossFamilyTag` map (one-source-of-truth provider→family) |
| `harness-runtime/src/.../lifecycle/retry_breaker_fallback.py` | `_provider_family` re-bound to the canonical `provider_family_for_provider` (dedup) |
| `harness-runtime/src/.../lifecycle/cost_attribution_llm_dispatch.py` | optional `provider_discriminator` param threaded into `SpanCostRecord` |
| `harness-runtime/src/.../lifecycle/llm_dispatch.py` | `_attribute_cost_best_effort` derives + passes the family tag |
| `harness-runtime/src/.../api.py` | `_rollup_cost_attribution_by_provider_discriminator` + `RunResult.cost_attribution_by_provider_discriminator` + `_build_run_result` wiring |
| `design-substrate/Spec_Harness_Runtime_v1.md` | v1.57 → **v1.58** §9 C-RT-09 (new field + invariant + **v1.57 `cost_attribution_by_dispatch_kind` §9-body-drift reconcile**, `[[spec-prose-plan-body-drift-pattern]]`) |
| `harness-runtime/tests/test_b_fallback_chain_family_cost_composition.py` | **NEW** — by-execution: map; LLM-subtotal rollup; real cost path tags the record; real `RetryBreakerFallbackDispatcher` cross-family fallback → `frontier_managed_alt` |
| `harness-runtime/tests/test_api.py` | `RunResult.model_fields` set extended with the new field |
| `.harness/clearance/Spec_Harness_Runtime-v1_58-cleared-2026-06-18.md` | clearance marker |
| `.harness/beyond-mvp-capability-boundary-ledger.md` + `.harness/r-fs-1-arc-and-unit-map.md` | spine BUILT + §5 status closed |

**Decorrelated review:** advisor (full-transcript — resolved the §15.3-span vs §15.1.2-record false dichotomy; flagged the LLM-subtotal invariant + the hollow-`FallbackChainCostComposition` trap) + out-of-family Codex (pre-merge, on the diff). Gates: pyright 0/0/0 · ruff · harness-runtime 1889 (non-e2e) · overlay 324/31-31 · substitution 54/54 · CXA-P1.
