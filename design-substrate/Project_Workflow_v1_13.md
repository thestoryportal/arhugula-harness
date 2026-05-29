# Project Workflow — v1.13 (delta over v1.12)

---

## Change-note (v1.12 → v1.13)

**Scope of revision.** Single-focus substantive amendment at §7.4.7.2 species-2 sub-species enumeration per v1.10 §1.3 + v1.11 §1.3 + v1.12 §1.2 OPEN catalogue authority:

1. **§7.4.7.2 species-2 sub-species enumeration extension** — catalogue the FIRST species-2 sub-species: **`2.strike-revision-on-refined-second-tier-reason`** — empirically surfaced at U-RT-111 v2.38 → v2.39 AC #4 STRIKE refinement (PR #62 merged `ac802a6` 2026-05-29). v1.10 species-3 9-entry catalogue + v1.11 species-5 {5.1, 5.2} catalogue + v1.12 species-3 tenth entry collectively PRESERVED VERBATIM; v1.13 §1.1 below extends species 2 from EMPTY to {2.strike-revision-on-refined-second-tier-reason}.

v1.12 + v1.11 + v1.10 + v1.9 file bodies PRESERVED VERBATIM per delta-only convention.

**Empirical lineage that prompted v1.13 (operator-routed 2026-05-29).** PR #62 (`ac802a6`) shipped runtime plan v2.38 → v2.39 absorbing U-RT-111 AC #4 disambiguator-derivation closure per Reading B + firing-site-absence carry-on. v2.35 originally STRUCK AC #4 framing the gap as "`RewrittenToolCall.semantic_variant_binding_id` NOT a field on the class at HEAD" (forecast wrong defect shape); v2.39 mid-arc empirical orientation confirmed Reading B derivation rule (`rewritten_call.variant.value` from existing `HITLSemanticVariant` enum at `RewrittenToolCall.variant`) AND surfaced second-tier finding: `RuntimeHITLPlacementRegistry.rewrite_tool_call` at `harness-runtime/src/harness_runtime/lifecycle/hitl_placement.py:187` has 6 test callers + ZERO production callers — same firing-site-absence shape as U-CP-34 STRUCK at v2.37 AC #11. v2.39 CAPTURES Reading B derivation rule for future-applicability + PRESERVES AC #4 STRIKE on refined second-tier reason (firing-site-absence). FIRST plan-revision at U-RT-111 that does NOT change the cumulative STRUCK count (7/12 UNCHANGED).

Closure-event-class: a prior plan-arc STRIKE framing is empirically falsified at a subsequent plan-arc, AND the STRIKE is preserved at the subsequent plan-arc on a refined second-tier reason rather than un-STRUCK. Distinct from species 3 (resolved-but-carry-stale-inherited) because the carry is NOT inherited stale — it's actively refined at the subsequent arc. Distinct from species 1 (phantom-as-described) because the original framing was substantively wrong at face-value (the cited field genuinely does not exist; the cited derivation rule genuinely is canonical from existing types), not a phantom that doesn't resolve.

**No fork doc filed.** Per workspace precedent for substantive amendments at workflow-doc revisions where prior-version §7.4.7.5 + v1.10 §1.3 + v1.11 §1.3 + v1.12 §1.2 explicitly authorize the catalogue-extension shape. v1.13 IS that extension at species 2 (first sub-species).

**Self-application of §7.4.7.3 audit at v1.12 → v1.13 transition.** Empirical-verification audit performed pre-substantive-authoring at v1.13 arc opening per v1.10 §2.1 §7.4.7.3.A + §2.2 §7.4.7.3.B + v1.12 §2 §7.4.7.3.C:

| Inherited carry from v1.12 | Verification | Disposition |
|---|---|---|
| §7.4.7.2 species 3 sub-species 10-entry catalogue at v1.12 §1.1 | Empirical inventory at PR #62 closure: ZERO new species-3 sub-species refinements; all 10 anchors preserved as canonical | GENUINE; PRESERVED VERBATIM at v1.13 |
| §7.4.7.2 species 5 sub-species {5.1, 5.2} at v1.11 | Empirical inventory: ZERO new species-5 sub-species refinements at v1.12 → v1.13 transition | GENUINE; PRESERVED VERBATIM at v1.13 |
| §7.4.7.2 species 1 / 4 sub-species enumeration EMPTY at v1.12 | Empirical inventory shows no sub-species refinements yet for species 1 or 4 | GENUINE; PRESERVED VERBATIM at v1.13 |
| §7.4.7.2 species 2 sub-species enumeration EMPTY at v1.12 | Empirical inventory at U-RT-111 v2.38 → v2.39 AC #4 STRIKE refinement (PR #62): ONE new species-2 sub-species candidate surfaced — `2.strike-revision-on-refined-second-tier-reason` — at the U-RT-111 cumulative STRUCK 7/12-UNCHANGED arc shape | AMENDMENT-OWED at v1.13 per v1.10 §1.3 + v1.11 §1.3 + v1.12 §1.2 OPEN catalogue authority |
| §7.4.7.3.A + §7.4.7.3.B + §7.4.7.3.C audit-template at v1.12 | Empirical lineage at PR #62 mid-arc reframe shows §7.4.7.3.A (sibling-section audit at attribute/carrier/enum amendment) NOT applicable at this arc (no contract change); §7.4.7.3.B (session-resumption inherited-framing audit) applied at v1.13 arc opening (this session resumes from PR #62 checkpoint; checkpoint §"Remaining Work" item 5 named "Workflow doc revision — formalize 2 new pattern catalogues at §7.4.7.2"); audit at orientation discriminated the second candidate `plan-revision-explicit-derivation-rule-under-spec-composer-kwarg-silence` as NOT-§7.4.7.2-shape (catalogued at v1.13 §6); §7.4.7.3.C (retirement-tier-transit audit) NOT applicable at this arc (no retirement-event filing) | FIFTH empirical §7.4.7.3.B application; pattern continues to validate the session-resumption audit's role in catching cross-catalogue-misclassification at arc opening |

ZERO C-*-NN contract change; ZERO retirement event filing; ZERO production code change; ZERO cross-axis cascade. Pure workflow-grammar canonicalization. Co-publication: workspace `CLAUDE.md` §2.1 governance row bump to v1.13.

---

## §1 §7.4.7.2 species-2 sub-species enumeration extension (canonical-reading amendment)

The §7.4.7.2 species-2 sub-species enumeration at v1.12 (EMPTY per v1.10 §6 (a) + v1.11 §1.3 + v1.12 §"Adjacent observations" (d)) is amended at v1.13 to populate the first entry. v1.10 §1.1 + v1.10 §1.2 + v1.11 §1.1 + v1.12 §1.1 PRESERVED VERBATIM; v1.13 §1.1 below is the species-2 sub-species canonical reading going forward.

### §1.1 Species 2 sub-species extension (catalogued at v1.13; OPEN per v1.10 §1.3 + v1.11 §1.3 + v1.12 §1.2)

| Sub-species | Distinctive closure-event class | Empirical cataloguing arc | Common-ancestor relationship |
|---|---|---|---|
| **2.strike-revision-on-refined-second-tier-reason** | A prior plan-arc STRIKE on an atomic-unit AC cites a specific defect shape (e.g., "field X missing on type Y"). A subsequent plan-arc empirically verifies the STRIKE framing and finds it substantively wrong at face-value (the cited derivation rule IS canonical from existing types; ZERO field-extension needed) AND surfaces a second-tier finding that independently justifies preserving the STRIKE (e.g., firing-site-absence at the LANDED substrate; same structural shape as a sibling-unit STRIKE at a prior arc). The STRIKE is REFINED — preserved on the second-tier reason — rather than un-STRUCK. Distinct from species 3 because the carry is NOT inherited stale (the original framing was substantively wrong, not stale); distinct from species 1 because the original cited gap was substantively wrong, not phantom (the cited field genuinely does not exist on the cited type). | U-RT-111 v2.38 → v2.39 AC #4 STRIKE refinement at PR #62 merged `ac802a6` 2026-05-29. v2.35 originally STRUCK AC #4 framing the gap as "`RewrittenToolCall.semantic_variant_binding_id` NOT a field on the class at HEAD" (forecast wrong defect shape — the existing `RewrittenToolCall.variant: HITLSemanticVariant \| None` IS the discriminator; StrEnum `.value` IS the opaque composer-kwarg string per Reading B derivation rule). v2.39 mid-arc empirical orientation also surfaced second-tier finding: `RuntimeHITLPlacementRegistry.rewrite_tool_call` at `harness-runtime/.../hitl_placement.py:187` has 6 test callers + ZERO production callers — same firing-site-absence shape as U-CP-34 STRUCK at v2.37 AC #11. Operator AskUserQuestion 2026-05-29 mid-arc reframe option 1 "Document Reading B + keep AC #4 STRUCK" ratified the preserve-STRIKE-on-refined-reason disposition. v2.39 IS the closure event; FIRST plan-revision at U-RT-111 that does NOT change the cumulative STRUCK count (7/12 UNCHANGED). | Species 2 (stale-carry-with-real-but-different-shape) with closure at plan-revision-arc layer rather than spec-amendment-arc layer (where v1.18 OD spec catalogued species 2 empirically). Distinct from existing species 3 sub-species 3.intra-spec-sibling-supersession (which operates on inherited stale carries at spec lineage) by carry-substrate class: not a spec-file delta inheriting stale text, but a plan-revision arc actively refining the framing of a prior STRIKE. The closure shape preserves the STRIKE (does not un-STRIKE) — distinct from species 3 closures which typically refresh stale text in-place. |

### §1.2 Sub-species catalogue is OPEN at v1.13

Per v1.10 §1.3 + v1.11 §1.3 + v1.12 §1.2 catalogue-accumulation discipline + this v1.13 §1.1 species-2 extension, the sub-species enumeration at each species (10 catalogued under species 3 at v1.12; 2 catalogued under species 5 at v1.11; 1 catalogued under species 2 at v1.13; 0 under species 1 / 4) is OPEN at v1.13 publication. Future workflow-doc revisions (v1.14 / v1.15 / ...) MAY catalogue additional sub-species under any species per the v1.9 §7.4.7.5 §3 amendment-arc closure shape.

Naming convention note: per v1.12 §1.2 — species with descriptor-form precedent (species 3) continue descriptor-form; species with numbered-form precedent (species 5) continue numbered-form; species without precedent MAY adopt either form at first cataloguing arc. v1.13 adopts descriptor-form for `2.strike-revision-on-refined-second-tier-reason` (consistency with species 3 + alignment with v1.18 OD spec change-note empirical anchor which named species 2 in descriptor form).

---

## §2 Sections preserved verbatim at v1.13

Per delta-only convention + FM-2 no-extension discipline + workflow-grammar canonicalization scope, the v1.13 amendment touches ONLY the NEW §1 species-2 sub-species extension + this §2 sections-preserved-verbatim + §3 adjacent observations + §4 filing footer. The following sections are PRESERVED VERBATIM at file-body layer:

- **§7.4.7.1** carry-text disposition taxonomy (file body unchanged; canonical at v1.13)
- **§7.4.7.2** five-species enumeration (file body unchanged; v1.10 §1.1 + v1.10 §1.2 species-3 9-entry catalogue + v1.11 §1.1 species-5 catalogue + v1.12 §1.1 species-3 tenth entry + this v1.13 §1.1 species-2 first entry collectively form the canonical reading)
- **§7.4.7.3** pre-substantive empirical-verification audit (file body unchanged; v1.10 §2 §7.4.7.3.A + §7.4.7.3.B + v1.12 §2 §7.4.7.3.C collectively form the canonical strengthening)
- **§7.4.7.4** amendment-arc closure shape (file body unchanged)
- **§7.4.7.5** pattern-catalogue accumulation discipline (file body unchanged)
- **§7.4.7.6** out-of-scope artifact classes (file body unchanged)
- **v1.12 §1 + §2 + §3 + §4 + §5 + §6** (PRESERVED VERBATIM per delta-only convention)
- **v1.11 §1 + §2** (PRESERVED VERBATIM)
- **v1.10 §1.2 + §2.1 + §2.2** (PRESERVED VERBATIM)
- **All v1.8 + v1.9 lineage sections** (file body unchanged; canonical at v1.13 + earlier)

---

## §3 Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **Second candidate pattern `plan-revision-explicit-derivation-rule-under-spec-composer-kwarg-silence` is NOT a §7.4.7.2-shape pattern.** The checkpoint §"Remaining Work" item 5 named two new pattern catalogues for §7.4.7.2 formalization. Pre-substantive empirical-verification audit per §7.4.7.3.B at v1.13 arc opening discriminated the second candidate as NOT-stale-carry-text-shape: it is a plan-revision authoring-discipline pattern (when spec is silent on how a composer-kwarg's value gets derived from existing types, the plan-arc captures an explicit derivation rule at the AC body), not a stale-carry disposition pattern. §7.4.7.2 is specifically the stale-carry-text-disposition catalogue per §7.4.7.1 taxonomy + 5-species enumeration; shoehorning a plan-revision authoring-discipline pattern into the 5-species enumeration would pollute the catalogue and degrade taxonomy coherence. Empirical cardinality 2 (U-RT-111 v2.38 AC #3 `event_sequence_id` + `protocol_state_snapshot` pause-resume derivation captured at plan-doc + v2.39 AC #4 `semantic_variant_binding_id` HITL derivation captured at plan-doc) is genuine + load-bearing for catalogue-decisive cardinality, but the pattern needs a distinct catalogue surface. Routing recommendation: at a future workflow-doc revision (v1.14 / v1.15+), consider authoring a NEW §7.4.7.X plan-revision-authoring-discipline catalogue distinct from §7.4.7 stale-carry-text discipline; OR catalogue at the implementation-planner skill's own discipline corpus; OR catalogue at a NEW §plan-revision-discipline section under §7. Catalogued for observation; routes to future revision per operator-discretion timing.

(b) **Species 1 / 4 sub-species enumeration remains EMPTY at v1.13.** Per v1.10 §6 (a) + v1.11 §1.3 + v1.12 §"Adjacent observations" (d), no sub-species refinements have empirically surfaced for species 1 (phantom-as-described) or species 4 (authoring-time stale carry). v1.13 does not catalogue new refinements at these species. Catalogued for observation; future arcs MAY populate.

(c) **Empirical cardinality at species 2 sub-species is 1 at v1.13 publication.** A single-instance sub-species catalogue at first publication is consistent with v1.11 species-5 precedent ({5.1, 5.2} catalogued at first species-5 amendment per single-session empirical authority). Future arcs MAY surface additional species-2 sub-species per the OPEN catalogue at §1.2. Catalogued for observation.

(d) **U-CP-34 v2.37 AC #11 STRIKE candidate `2.strike-revision-on-refined-second-tier-reason` lineage at second instance.** U-CP-34 v2.37 STRIKE on AC #11 was the FIRST surfacing of firing-site-absence-at-LANDED-substrate (primitive-scope-mismatch §15.1 per-sibling vs dispatch-site). U-RT-111 v2.39 AC #4 STRIKE refinement IS the cataloguing arc at v1.13. The U-CP-34 STRIKE was NOT a STRIKE-refinement (it was a fresh first STRIKE); the v1.13 §1.1 sub-species applies specifically to STRIKE-refinement events (where a prior STRIKE framing is empirically falsified at face-value AND preserved on a refined second-tier reason). Future plan-revision arcs at sibling-unit firing-site-absence-at-LANDED-substrate gaps MAY surface additional `2.strike-revision-on-refined-second-tier-reason` instances. Catalogued for observation.

(e) **Cross-catalogue scope discipline preserved.** v1.11 §1.2 cross-catalogue discriminator separating workflow-doc catalogue from retirement-event-pattern catalogue is PRESERVED VERBATIM at v1.13. v1.13 does NOT touch the retirement-event-pattern catalogue. Catalogued for adjacent-routing-discipline at this v1.13 arc.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.13 (Substantive amendment per v1.10 §1.3 + v1.11 §1.3 + v1.12 §1.2 OPEN catalogue authority — NEW §1 §7.4.7.2 species-2 sub-species `2.strike-revision-on-refined-second-tier-reason` catalogue extension from EMPTY → {2.strike-revision-on-refined-second-tier-reason}; v1.12 + v1.11 + v1.10 + v1.9 file body PRESERVED VERBATIM per delta-only convention) |
| Trigger | Operator-routed checkpoint §"Remaining Work" item 5 (PR #62 closure checkpoint) 2026-05-29 — "Workflow doc revision — formalize 2 new pattern catalogues at §7.4.7.2". Pre-substantive empirical-verification audit per §7.4.7.3.B at v1.13 arc opening discriminated 1-of-2 candidates as §7.4.7.2-shape; second candidate routes separately per §3 (a) |
| Supersedes | v1.12 §7.4.7.2 species-2 sub-species enumeration (EMPTY → 1 entry); ALL other v1.12 + v1.11 + v1.10 + v1.9 sections PRESERVED VERBATIM |
| Scope of revision | SUBSTANTIVE: NEW §1 + §2 + §3 + §4. ZERO C-*-NN contract change; ZERO retirement event filing; ZERO production code change; ZERO cross-axis cascade. Pure workflow-grammar canonicalization. Co-publication: workspace `CLAUDE.md` §2.1 governance row bump |
| Cross-axis cascade | ZERO. v1.13 is workflow-grammar canonicalization; no per-axis spec / plan / CXA / production code touch |
| Authority anchor | v1.10 §1.3 + v1.11 §1.3 + v1.12 §1.2 OPEN catalogue authority + v1.9 §7.4.7.5 catalogue-accumulation discipline; U-RT-111 v2.38 → v2.39 AC #4 STRIKE refinement at PR #62 merged `ac802a6` 2026-05-29 empirical anchor |
| Predecessor | v1.12 (Species-3 sub-species 10th entry `3.gate-text-stale-vs-production-landings` + §7.4.7.3.C retirement-tier-transit audit-template strengthening) |
| Successor | (none — current canonical) |
| Date | 2026-05-29 |

---

*End of `Project_Workflow_v1_13.md` (delta over v1.12). v1.9 + v1.10 + v1.11 + v1.12 PRESERVED VERBATIM as historical anchors per delta-only-spec-file convention.*
