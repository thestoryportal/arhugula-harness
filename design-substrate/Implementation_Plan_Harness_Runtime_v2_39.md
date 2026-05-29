# Implementation Plan — Harness Runtime — v2.39

*Delta over v2.38. v2.39 is a Phase 7 → design-phase Class 1 fork-doc absorption pass for the AC #4 disambiguator-derivation gap (the HITL disambiguator at `RewrittenToolCall.semantic_variant_binding_id`). v2.35 STRUCK AC #4 framing the gap as "field missing on RewrittenToolCall"; v2.39 empirical orientation at HEAD `8012777` confirms Reading B derivation rule (`semantic_variant_binding_id = rewritten_call.variant.value`; the existing `variant` enum IS the discriminator) — operator-ratified via AskUserQuestion 2026-05-29 under advisor 43rd application. v2.39 also surfaces a SECOND-tier finding the v2.35 STRIKE framing missed: empirical grep at HEAD of `RuntimeHITLPlacementRegistry.rewrite_tool_call` shows ZERO production callers (6 test callers only), establishing AC #4 has a compounding **firing-site-absence gap** (same structural shape as U-CP-34 STRUCK at v2.37 AC #11). v2.39 CAPTURES Reading B derivation rule in plan body for future-applicability + PRESERVES AC #4 STRIKE on refined second-tier reason (firing-site-absence). Cumulative ACs STRUCK UNCHANGED at 7 of 12; RETAINED UNCHANGED at 5 of 12. Upstream-blocker count reduces from 5 to 4 (HITL disambiguator-field-extension arc CLOSES at v2.39 plan-doc per Reading B captured; HITL firing-site-absence arc REMAINS as sibling of U-CP-34 firing-site arc — operator-discretion at retirement-batch filing on whether to count as half-arc reduction or sibling-bundled). ZERO impl at v2.39; ZERO cross-axis cascade; ZERO spec change.*

## §0 Change note (v2.38 → v2.39)

### §0.1 What changed

| Element | v2.38 | v2.39 |
|---|---|---|
| U-RT-111 AC #4 STRIKE framing | "RewrittenToolCall.semantic_variant_binding_id NOT a field on the class at HEAD; synthesizing at runtime axis would be X-AL-3 silent design extension" (v2.35 framing PRESERVED through v2.38) | **REFINED at v2.39 on second-tier reason.** Disambiguator-derivation gap CLOSED per Reading B (`semantic_variant_binding_id = rewritten_call.variant.value`); STRIKE PRESERVED for empirically-surfaced firing-site-absence gap: `RuntimeHITLPlacementRegistry.rewrite_tool_call` has 6 test callers + ZERO production callers at HEAD `8012777`. Same structural shape as U-CP-34 STRUCK at v2.37 AC #11. |
| Cumulative STRUCK count | 7 of 12 | 7 of 12 (UNCHANGED — AC #4 STRIKE preserved on revised second-tier reason) |
| RETAINED count | 5 of 12 | 5 of 12 (UNCHANGED) |
| §0.4 upstream-blocker count | 5 arcs | **4 arcs** (HITL disambiguator-field-extension arc CLOSED at v2.39 plan-doc per Reading B captured; HITL firing-site-absence arc NEW as separate carry — sibling of U-CP-34 firing-site arc; operator-discretion on whether to count as net reduction or sibling-bundled at retirement-batch filing) |
| §1 unit count | 109 | 109 (UNCHANGED) |
| §2 DAG | UNCHANGED | UNCHANGED |
| H_T-RT-35 transit framing | STAYS PARTIAL post-v2.38 impl arc per AC #12 | UNCHANGED — STAYS PARTIAL. Upstream blocker count refined as above. |
| CXA v2.16 → v2.17 transit | 1 PENDING → 1 LANDED at v2.38 impl arc (U-CP-76); aggregate 6 PENDING → 1 LANDED + 5 carry | UNCHANGED — ZERO CXA transit at v2.39 (plan-doc only; no impl). |

### §0.2 Scope discipline

§0 (this change note); §1 U-RT-111 unit-body canonical-reading amendment refining AC #4 STRIKE framing on second-tier reason + capturing Reading B derivation rule for future-applicability; §2 DAG preservation (ZERO edge changes); §3 adjacent observations + carry-forward; §4 filing footer. All v2.38 + v2.37 + v2.36 + v2.35 + v2.34 + ... + v1 lineage PRESERVED VERBATIM per delta-only-plan-chain convention except: (a) the U-RT-111 AC #4 narrative entry which is REFINED at v2.39 (STRIKE preserved on revised second-tier reason + Reading B derivation rule captured); (b) §3 (b) HITL disambiguator surface reduced from full carrier-extension scope to firing-site-absence only; (c) §3 (i) extended with 43rd advisor application narrative; (d) NEW §3 (l) catalogue entry for `[[plan-revision-explicit-derivation-rule-under-spec-composer-kwarg-silence]]` pattern cardinality 1 → 2.

### §0.3 Authoring rationale + the v2.39 reframing

**Reading B derivation rule (CLOSED at v2.39 plan-doc):**

Operator-ratified via AskUserQuestion 2026-05-29 under advisor 43rd application + pre-substantive consultation discipline (Reading B option: "Reading B confirmed: derivation rule `semantic_variant_binding_id = rewritten_call.variant.value`. Narrow scope: plan-only un-STRIKE + derivation doc."). The existing `RewrittenToolCall.variant: HITLSemanticVariant | None` field at `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py:131` IS the discriminator. The composer `emit_hitl_tool_call_rewriting_state_ledger_entry` at `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py:249-291` takes `semantic_variant_binding_id: str` as opaque string; StrEnum `.value` IS a string; canonical-JSON canonicalization of `RewrittenToolCall` at §16.5.5 outcome semantic preserves the variant via the existing `variant` field. CP spec v1.26 §16.5.4 line 71 informal cite ("HITLSemanticVariantBinding discriminator at select_variant outcome") reads loosely — the actual discriminator is the `HITLSemanticVariant` enum returned by `select_variant()`. ZERO field-extension at `RewrittenToolCall`, `HITLSemanticVariantBinding`, or composer signature; ZERO spec extension.

**Same-shape precedent at v2.38 AC #3:** explicit-derivation-documented under spec composer-kwarg silence (`event_sequence_id` + `protocol_state_snapshot` derivation rules captured in plan body before impl). Reading B is the analogous derivation rule for `semantic_variant_binding_id` at U-CP-37. The pattern catalogues `[[plan-revision-explicit-derivation-rule-under-spec-composer-kwarg-silence]]` extending from v2.38 AC #3 single-instance precedent to v2.39 AC #4 plan-doc capture; cardinality 1 → 2 (across 2 atomic units, in 2-day window).

**SECOND-tier finding at v2.39 (firing-site-absence; PRESERVES STRIKE):**

Empirical grep at HEAD `8012777` for `\.rewrite_tool_call` and `HITLPlacementComposer`/`RuntimeHITLPlacementRegistry` returns:

- 1 method definition at `harness-runtime/src/harness_runtime/lifecycle/hitl_placement.py:187` (`RuntimeHITLPlacementRegistry.rewrite_tool_call`)
- 6 test callers at `harness-runtime/tests/test_lifecycle_hitl_placement.py:258, 278, 296, 313, 330, 349`
- ZERO production callers anywhere in `harness-*/src/`

Same structural shape as U-CP-34 `emit_sibling_ledger_entry` at v2.37 AC #11 STRIKE: composer exists at the lifecycle layer + U-RT-110 wiring method exists for it + ZERO production caller fires the composer. Catalogue candidate `firing-site-absence-at-LANDED-substrate` at workflow doc §7.4.7.2 sub-species enumeration (sibling to U-CP-34 instance).

Because no production caller exists at HEAD, AC #4's "wire the caller-site" contract cannot be satisfied at the runtime axis without authoring the production caller — which is a substantive design decision (which call path SHOULD invoke `rewrite_tool_call`?) that exceeds plan-revision scope per FM-2 single-focus arc discipline. The v2.35 STRIKE on the disambiguator-derivation surface DOES NOT resolve the firing-site-absence surface; the STRIKE is preserved at v2.39 with refined second-tier framing.

**Operator AskUserQuestion ratification 2026-05-29 (mid-arc reframe, option 1):**

After empirical orientation surfaced the second-tier finding, operator chose "Document Reading B + keep AC #4 STRUCK" via AskUserQuestion: capture Reading B derivation rule as future-applicable in plan-doc; preserve STRIKE pending firing-site-absence resolution at a separate arc; route firing-site-absence to design-phase (runtime-axis OR CP-axis) — sibling-bundle with U-CP-34 firing-site arc recommended.

### §0.4 Out-of-scope at v2.39 (refined from v2.38 §0.4)

| Owed arc | Routing target | Rationale |
|---|---|---|
| ~~CP spec v1.26 → v1.27 amendment for HITL `RewrittenToolCall.semantic_variant_binding_id` field extension~~ | ~~CP-axis design-phase routing~~ | **CLOSED at v2.39 plan-doc per Reading B captured.** No spec extension owed; `variant.value` derivation rule documented in plan body §1.2 (and below). CP spec §16.5.4 line 71 informal cite ("HITLSemanticVariantBinding discriminator at select_variant outcome") could optionally be cite-cleaned (clarify "variant returned by select_variant()") + line cite `:72` → `:79` corrected (the v1.26 cite to `hitl_as_tool_call_rewriting.py:72` lands at the `EngineBindingClass` docstring; `HITLSemanticVariantBinding` declaration is at line 79) at a follow-on CP spec revision pass — deferred per FM-2 single-focus arc scope. |
| **NEW at v2.39:** HITL `RuntimeHITLPlacementRegistry.rewrite_tool_call` firing-site-absence resolution | Runtime-axis design-phase routing OR CP-axis design-phase routing — sibling-bundle with U-CP-34 firing-site arc recommended | Empirical grep at HEAD `8012777` confirms ZERO production callers. Resolving requires substantive design decision (which call path SHOULD invoke the rewrite-and-emit chain). Possible call sites: (a) workflow_driver tool-dispatch pre-call hook (sibling to validator-escalation hook); (b) sub_agent_dispatch tool-dispatch wrap; (c) NEW dedicated HITL-rewrite stage at bootstrap. Sibling of U-CP-34 firing-site-absence arc at v2.37 §3 — both could route together. Operator-discretion at upstream arc; impl-axis routing recommended given the call-path-choice is implementation-discretion under spec §16.5.7 firing-site discipline silence on caller-side scope. |
| Runtime spec v1.7 → v1.N amendment AND/OR CP spec v1.26 → v1.27 amendment authorizing the bootstrap-time emission substrate for U-CP-75 workload-class-selection | Runtime-axis design-phase routing OR CP-axis design-phase routing | UNCHANGED carry from v2.38 §0.4 |
| CP spec v1.26 → v1.27 canonical-reading amendment for U-CP-34 firing-site scope | CP-axis design-phase routing | UNCHANGED carry from v2.37 §0.4 |
| CP plan v2.29 → v2.30 NEW units for engine-layer impl | CP-axis design-phase routing | UNCHANGED carry from v2.36/v2.37/v2.38 §0.4 |
| CP spec v1.26 → v1.27 amendments for override disambiguator field | CP-axis design-phase routing OR engine-layer impl arc absorption | UNCHANGED carry from v2.36/v2.37/v2.38 §0.4 (HITL disambiguator REMOVED from this row at v2.39 per Reading B closure) |
| CXA v2.16 → v2.17 §2.3.2 enumeration refresh — full 6 PENDING → 6 LANDED | Retirement-batch filing arc post-engine-layer-landing | UNCHANGED carry from v2.38 §0.4 |
| Runtime spec §12.3 prose alignment per v2.33 (C-defer) | Next runtime-spec revision pass | UNCHANGED carry |

---

## §1 U-RT-111 unit-body canonical-reading amendment (v2.39)

### §1.1 Site

PRESERVED VERBATIM from v2.38 §1.1.

### §1.2 U-RT-111 — Body (v2.39 canonical reading)

**Implements:** PRESERVED VERBATIM from v2.38 §1.2 (no caller-site count change; AC #4 STRIKE preserved on revised second-tier reason; v2.39 adds Reading B derivation rule capture for future-applicability without changing the unit's structural surface).

**Files:** PRESERVED VERBATIM from v2.38 §1.2.

**Signatures introduced:** PRESERVED VERBATIM from v2.38 §1.2 — NONE at U-RT-111.

**Per-caller-site invocation contract** (1 invocation surface at v2.39 unchanged from v2.38; 3 sites within `workflow_driver.execute_workflow` body):

PRESERVED VERBATIM from v2.38 §1.2 for retained sites. **AC #4 row REFINED at v2.39:**

| # | Caller site | Status at v2.39 | Reading B derivation rule (captured as future-applicable) |
|---|---|---|---|
| 4 | Hypothetical site at HITL-rewrite caller (no production caller exists at HEAD `8012777`) | **STRUCK at v2.35; STRIKE PRESERVED at v2.39 on refined second-tier reason.** Disambiguator-derivation gap CLOSED per Reading B captured below; firing-site-absence gap REMAINS — `RuntimeHITLPlacementRegistry.rewrite_tool_call` has ZERO production callers at HEAD. Routes to design-phase per v2.39 §0.4 NEW row (recommend sibling-bundle with U-CP-34 firing-site arc). | **Reading B (captured at v2.39 plan-doc for future-applicability when firing-site-absence resolves):** `semantic_variant_binding_id = rewritten_call.variant.value` when `rewritten_call.hitl_required is True` (emission conditional on rewrite-occurred semantic — when `hitl_required is False`, no rewrite happens and no §16.5 emission fires); `tool_call_id` from upstream caller context (opaque string per CP spec §16.5.4 row 4 — caller-provided, analogous to `workflow_id` + `step_id` opacity at sibling rows); `actor` from `ctx.ledger_writer.actor` per AC #9 firing-site convention. |

**Reading B derivation rule explicit framing (NEW at v2.39; explicit-derivation-documented under spec composer-kwarg silence — extending v2.38 AC #3 precedent):**

Per advisor 43rd application + operator AskUserQuestion ratification 2026-05-29 ("Narrow: plan-only un-STRIKE + derivation doc" → mid-arc reframed to "Document Reading B + keep AC #4 STRUCK" on second-tier firing-site-absence finding):

- **`semantic_variant_binding_id: str`** — derivation rule: `rewritten_call.variant.value` (the StrEnum string value of the `HITLSemanticVariant` enum returned by `select_variant()` and stored at `RewrittenToolCall.variant` per `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py:131`). NO field-extension at `RewrittenToolCall`, `HITLSemanticVariantBinding`, or composer signature; the existing `variant` enum IS the discriminator. The composer `emit_hitl_tool_call_rewriting_state_ledger_entry` at `:249-291` takes `semantic_variant_binding_id: str` as opaque string; StrEnum `.value` IS a string; canonical-JSON canonicalization of `RewrittenToolCall` at §16.5.5 outcome semantic preserves the variant via the existing `variant` field. ZERO synthesis at runtime axis; ZERO spec extension owed.

- **Emission conditional on `rewritten_call.hitl_required is True`** — when `hitl_required is False`, the `rewrite_tool_call_to_hitl(...)` short-circuit returns `variant=None` + `response_palette=None` (no rewrite happened); no §16.5 emission fires because there is no rewriting outcome to record. Pattern matches §16.5.7 spec authority semantic ("AFTER `rewrite_tool_call_to_hitl(...)` produces the `RewrittenToolCall`") — the rewriting OUTCOME is what gets recorded, and the outcome only exists when rewriting occurred.

- **`tool_call_id: str`** — caller-provided opaque string. CP spec §16.5.4 row 4 lists `tool_call_id` as an idempotency-key segment; spec silent on derivation. Convention precedent at sibling rows: `workflow_id` + `step_id` are similarly opaque strings provided by upstream caller. Implementation-discretion at firing-site arc per FM-2 carve-out.

- **`actor: ActorIdentity`** — sourced from `ctx.ledger_writer.actor` per AC #9 firing-site convention (same shape as AC #3 pause-resume sites where this resolves cleanly at workflow_driver scope).

**Future-applicability framing.** The Reading B derivation rule + emission-conditional semantic are captured at v2.39 plan-doc for future-applicable consumption when the firing-site-absence gap is resolved at a follow-on arc. No impl at v2.39 (AC #4 STRIKE preserved); the derivation rule landing in plan v2.39 ensures a future firing-site arc does NOT need to re-litigate the disambiguator-derivation question — Reading B is durable plan-doc anchor; future arcs cite "v2.39 §1.2 AC #4 Reading B derivation rule" as authority.

**Acceptance criteria (v2.39 — STRIKE PRESERVED at AC #4 with refined narrative):**

1-3. PRESERVED VERBATIM from v2.38 §1.2.

4. ~~**Caller-site (4) HITL-tool-call-rewriting.**~~ **STRUCK at v2.35; STRIKE PRESERVED at v2.39 on refined second-tier reason** per §0.3 above: disambiguator-derivation gap CLOSED at v2.39 plan-doc per Reading B `semantic_variant_binding_id = rewritten_call.variant.value` (captured as future-applicable derivation rule + emission-conditional semantic above); firing-site-absence gap REMAINS — `RuntimeHITLPlacementRegistry.rewrite_tool_call` has ZERO production callers at HEAD `8012777` (6 test callers only). AC #4 cannot un-STRIKE on disambiguator-derivation closure alone; firing-site-absence routes to runtime-axis OR CP-axis design-phase per §0.4 NEW row (sibling-bundle with U-CP-34 firing-site arc recommended).

5-12. PRESERVED VERBATIM from v2.38 §1.2.

**Tests:** PRESERVED VERBATIM from v2.38 §1.2 — ZERO test addition or removal at v2.39 (plan-doc only; AC #4 STRIKE preserved; impl arc not triggered).

**Rollback boundary:** UNCHANGED from v2.38 §1.2.

---

## §2 DAG delta

ZERO DAG edge changes at v2.39 (UNCHANGED from v2.38). The plan-doc refinement preserves the unit, its dependency edges, and its position in the topological sort. v2.34 + v2.35 + v2.36 + v2.37 + v2.38 §2 DAG declarations PRESERVED VERBATIM.

Unit count: 109 (UNCHANGED from v2.38).

---

## §3 Adjacent observations + carry-forward

(a) **CP plan v2.29 → v2.30 NEW units for engine-layer impl OWED at separate design-phase routing.** PRESERVED VERBATIM from v2.38 §3 (a).

(b) **CP spec v1.26 → v1.27 disambiguator-field amendments OWED at separate arc — REFINED at v2.39.** Now covers 5 disambiguator surfaces (was 6 at v2.38): `PauseEvent.pause_event_id` + `resume_attempt_count` (v2.35 carry) + `override_id` + `policy_id` derivation rule OR `StepOverride` model field-set extension (v2.36 carry) + U-CP-34 `emit_sibling_ledger_entry` firing-site canonical-reading clarification (v2.37 carry) + bootstrap-time emission substrate for U-CP-75 workload-class-selection (v2.38 carry). **REMOVED at v2.39:** HITL `RewrittenToolCall.semantic_variant_binding_id` CLOSED at v2.39 plan-doc per Reading B derivation rule. **NEW at v2.39 as separate carry:** HITL firing-site-absence at `RuntimeHITLPlacementRegistry.rewrite_tool_call` (per §0.4 NEW row).

(c) **CXA v2.16 §0.4 forward-tracking partial transit — UNCHANGED at v2.39.** ZERO impl at v2.39; v2.38 §3 (c) state preserved (1 of 6 LANDED at v2.38 impl arc PR #61 merge `8012777`; 5 PENDING).

(d) **H_T-RT-35 batch-filing precedent NOT applicable at v2.39.** PRESERVED VERBATIM from v2.38 §3 (d). Now requires **4-arc convergence** for HITL disambiguator-derivation portion CLOSED at v2.39, but **HITL firing-site-absence arc opens as NEW carry** — so effective convergence remains 5 arcs (override-disambiguator + engine-layer impl + sibling-ledger firing-site + bootstrap-emission-substrate + HITL firing-site-absence; HITL disambiguator-field-extension CLOSED). Operator-discretion at retirement-batch filing on whether to count v2.39 as net reduction or sibling-bundled. v2.39 closure event is partial — disambiguator-derivation portion CLOSED; firing-site-absence portion REMAINS.

(e) **U-CP-77 HITL composer LANDED-at-substrate UNCHANGED.** v2.39 captures Reading B derivation rule for future use; does NOT advance the U-CP-77 firing-site-absence transit (which requires a production caller — separate arc).

(f) **Workspace `CLAUDE.md` §2.4 runtime plan row bump owed.** Runtime plan row v2.38 → v2.39. Co-publication this arc. Unit count: 109 (UNCHANGED).

(g) **`harness-runtime/CLAUDE.md` plan-unit anchor refresh owed at follow-on impl arc.** PRESERVED VERBATIM from v2.38 §3 (g).

(h) **PR-shape recommendation.** v2.39 is a STANDALONE plan-revision PR (NOT bundled with the PR #61 v2.38 impl arc which already merged at main `8012777`). Single commit with plan v2.39 + fork doc §12 NEW closure entry + workspace CLAUDE.md §2.4 row bump. X-AL-3 CI guard satisfied via fork doc co-location in same PR (per CLAUDE.md §4.4 enforcement layer 3).

(i) **43rd application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`.** Pre-substantive advisor consultation at v2.39 authoring caught Reading B as the plain face-value reading PRE any spec-edit ("verify, don't escalate to fork"). Advisor also recommended grep-verification of consumer existence before treating as fidelity-pure cite-correction patch — that grep surfaced the SECOND-tier firing-site-absence finding that mid-arc reframed scope (Reading B captured for future-applicability, but AC #4 STRIKE preserved on refined second-tier reason). Discipline continues to validate: advisor consultation enabled the second-tier gap discovery BEFORE plan-revision authoring committed to "un-STRIKE AC #4" framing that would have been silent X-AL-3 extension on the firing-site axis.

(j) **NEW pattern catalogue at v2.39: `[[strike-revision-on-refined-second-tier-reason]]`.** v2.39 introduces a NEW closure-event-class at workflow doc §7.4.7.2 candidate — **STRIKE preserved across plan-revisions on refined second-tier reason after empirical orientation surfaces a deeper gap than the original STRIKE framing identified.** Distinct from prior `[[plan-revision-against-not-yet-built-substrate]]` sub-species (v2.35/v2.36/v2.37/v2.38 instances): those STRUCK on first-discovered substrate gap; v2.39 preserves STRIKE on a different gap than originally cited (original v2.35 framing was disambiguator-field-missing; v2.39 refined framing is firing-site-absence-at-LANDED-substrate). Workflow-doc revision candidate: when empirical orientation at a future plan-revision arc surfaces a deeper gap than the original STRIKE identified, the STRIKE narrative MUST be refined at the next plan-revision (not silently re-cited verbatim) — fidelity-pure narrative refresh discipline.

(k) **Plan-revision discipline preserved at v2.39.** UNCHANGED from v2.38 §3 (k). v2.39 cites runtime spec v1.7 (UNCHANGED) + CP spec v1.26 §16.5 (UNCHANGED); does NOT invent any commitment; does NOT amend any cited spec; preserves dependency edges; coverage matrix UNCHANGED.

(l) **NEW pattern catalogue at v2.39: `[[plan-revision-explicit-derivation-rule-under-spec-composer-kwarg-silence]]` cardinality 1 → 2.** v2.38 AC #3 introduced explicit-derivation-documented framing under spec composer-kwarg silence for `event_sequence_id` + `protocol_state_snapshot` derivation rules. v2.39 extends the pattern to AC #4 `semantic_variant_binding_id` derivation rule. Pattern catalogue cardinality 1 → 2 in 2 days (across 2 atomic units U-RT-111 ACs #3 + #4). Workflow-doc revision candidate.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.39 |
| Predecessor | v2.38 (runtime plan v2.37 → v2.38 fourth sequel-rescope at U-RT-111 STRIKE AC #2 + AC #3 + #10 impl shipped; PR #61 squash at main `8012777` 2026-05-29) |
| Successor consumption | NO impl arc at v2.39 (plan-doc only). Reading B derivation rule captured as future-applicable; firing-site-absence resolution at follow-on design-phase arc (runtime OR CP-axis routing; sibling-bundle with U-CP-34 firing-site arc recommended). |
| Cross-axis cascade | ZERO at v2.39 (plan-doc only). CP spec v1.26 §16.5 UNCHANGED; CP plan v2.29 UNCHANGED; CXA v2.16 UNCHANGED. |
| Authority anchors | `.harness/class_1_tension_u_rt_111_engine_layer_substrate_absence.md` §12 NEW (closure entry for AC #4 disambiguator-derivation per Reading B + firing-site-absence routing; co-authored this arc); `Spec_Control_Plane_v1_26.md` §16.5.4 row U-CP-37 + §16.5.5 row U-CP-37 + line 71 disambiguator note; `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py:131` (`RewrittenToolCall.variant` field declaration site); `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py:249-291` (composer signature site); `harness-runtime/src/harness_runtime/lifecycle/hitl_placement.py:187+205` (firing-site-absence empirical authority); `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-3 (silent extension foreclosed); `Project_Workflow_v1_12.md` §2.7.6 Class 1 back-flow; runtime plan v2.38 §1.2 (this v2.39 amends in-place at delta-only-plan-chain layer) |
| Co-publications | Fork doc §12 NEW filed at same PR (closure entry for AC #4 disambiguator-derivation per Reading B + sibling-bundle firing-site-absence with U-CP-34 routing); workspace `CLAUDE.md` §2.4 row bump (v2.38 → v2.39; unit count 109 UNCHANGED) |
| Date | 2026-05-29 |
