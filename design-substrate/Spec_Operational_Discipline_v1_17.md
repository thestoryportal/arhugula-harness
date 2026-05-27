# Spec: Operational Discipline — v1.17 (delta over v1.16)

---

## Change-note (v1.16 → v1.17)

**Scope of revision.** Fidelity-pure citation-correction patch closing v1.13/v1.14/v1.15/v1.16 §"Adjacent observations" finding (d)/(c)/(c)/(b) — the `gen_ai.system` vs `gen_ai.provider.name` divergence — as **CLOSED-as-resolved-at-production-commit-115387b** 2026-05-26. Empirical verification at production grep this session confirms ZERO `gen_ai.system` literals remain at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` (only `gen_ai.system_instructions` Opt-In content attribute remains, which is a distinct attribute name semantically unrelated to the divergence). The divergence flagged at v1.12 §"Adjacent observations" (f) — production emitted `gen_ai.system` instead of `gen_ai.provider.name` — was resolved at commit `115387b` (2026-05-26 19:40 -0600) via producer-side conform: line 341 emits `gen_ai.provider.name` (renamed from `gen_ai.system`); line 340 NEW emits `gen_ai.operation.name`; line 342 preserves `gen_ai.request.model`. All 3 §C-OD-04 §4.3 Required (Stable) tier attributes now emit on every GenAI span. The v1.13/v1.14/v1.15/v1.16 carry-text was never refreshed when the resolution landed; v1.17 corrects the carry-text disposition + closes the finding at the canonical-reading layer.

**Empirical posture (load-bearing).** Production grep this session 2026-05-26:

- `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:341` → `span.set_attribute("gen_ai.provider.name", provider_name)` (post-115387b).
- `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:340` → `span.set_attribute("gen_ai.operation.name", operation.value)` (NEW at 115387b).
- `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:342` → `span.set_attribute("gen_ai.request.model", model)` (preserved verbatim).
- Recursive grep of `harness-{runtime,od,cp,as,core,cxa}/src/` for `gen_ai\.system` (excluding `gen_ai.system_instructions`) returns ZERO hits.
- Cross-axis attribute schemas at `harness-od/src/harness_od/attribute_class_enforcement.py:45` + `content_structure_discipline.py:84` + `otel_genai_base.py:147` + `cost_formula.py:83` + `idempotency_join_dedup.py:181` all cite `gen_ai.provider.name` (canonical name post-115387b; pre-existing at carrier-layer authoring).

The divergence no longer exists at production; the spec-side canonical reading at §C-OD-04 §4.3 (`gen_ai.provider.name` as Required (Stable) tier) was already correct at v1.2 authoring + preserved verbatim through v1.16; commit `115387b` conformed the producer to the already-canonical spec.

**Lineage finding (load-bearing).** The carry-text framing across v1.13/v1.14/v1.15/v1.16 implied the divergence was a live "separate spec defect" awaiting "separate apply-pass arc." Empirical verification confirms the divergence was resolved at producer-side conform on the same day as the v1.12 amendment (2026-05-26) but the carry-text disposition was never refreshed to reflect the resolution. Same failure-mode lineage as the v1.15 finding-(a) phantom closure pattern at one level of generality: the v1.15 case was "phantom-as-described" (the defect never existed in the framed shape); the v1.17 case is "resolved-but-carry-stale" (the defect existed at v1.12 authoring but was resolved at 115387b without carry-text refresh). Both are corrective re-litigation arcs against stale carry-text; the v1.17 arc names this pattern explicitly per §"Pattern catalogue" below.

**Routing.** Per workspace `CLAUDE.md` §4.3 + I-1 byte-exact discipline + v1.15 phantom-closure precedent: v1.17 is a NEW delta file authoring §1 canonical-reading amendment table for the v1.13/v1.14/v1.15/v1.16 carry-text + §2 finding closure + §3 cross-artifact cite-cascade disposition. v1.2-v1.16 PRESERVED VERBATIM per delta-only-spec-file convention. ZERO contract change; ZERO signature change; ZERO acceptance-criterion change; ZERO behavior change at any consumer. The amendment is canonical-reading + closure-disposition only.

**No fork doc filed.** Per workspace precedent (CP spec v1.14 §1.2 cite-shape correction 2026-05-24; runtime spec v1.16 phantom-cite resolution 2026-05-22; OD spec v1.15 finding-(a) phantom closure 2026-05-26): fidelity-pure citation-correction patches with conclusive empirical posture follow the inline-correction-without-fork-doc convention. The v1.17 arc has conclusive empirical posture (production grep zero-hits + commit `115387b` resolution verified). Fork doc filing would be over-cost-of-process per FM-2.

---

## §1 Canonical-reading amendment table (v1.17 NEW)

Per delta-only-spec-file convention, the v1.2 through v1.16 file bodies are PRESERVED VERBATIM. The following table maps every carry-text site for the `gen_ai.system` vs `gen_ai.provider.name` divergence to its corrected canonical reading. Readers of v1.12-v1.16 MUST apply these substitutions when interpreting the divergence-disposition tokens at the listed sites.

### §1.1 Carry-text disposition refresh

The v1.12 §"Adjacent observations" (f) authoring framing — "production currently emits `gen_ai.system` (NOT `gen_ai.provider.name`)" — was correct at v1.12 authoring time (2026-05-26 morning, pre-commit `115387b`). The same framing carried verbatim through v1.13 finding (d), v1.14 finding (c), v1.15 finding (c), v1.16 finding (b) — but the divergence was resolved at commit `115387b` (2026-05-26 evening, same day) without carry-text refresh. The canonical reading at v1.17 is:

| Site | v1.12-v1.16 carry-text | Canonical reading at v1.17 |
|---|---|---|
| v1.12 §"Adjacent observations" (f) — "production at `llm_dispatch.py:330` currently emits `gen_ai.system`" | "currently emits" + "separate spec defect surfaced this arc — not patched per FM-2; owed at a separate apply-pass arc" | **CLOSED-as-resolved-at-115387b** — line 330 references stale; post-115387b actual lines are 340 (operation.name NEW), 341 (provider.name renamed from system), 342 (request.model preserved). All 3 §4.3 Required (Stable) attributes emit on every GenAI span. ZERO further apply-pass arc owed. |
| v1.12 §"Amendment site" table row — "line 330" + "provider preserved at `gen_ai.system` attribute set" | "line 330" + "`gen_ai.system` attribute" | **CLOSED-as-resolved-at-115387b** — post-115387b actual line is 341 emitting `gen_ai.provider.name`. The "preserved at `gen_ai.system`" claim was R1-arc-time framing; superseded by the producer rename at 115387b. |
| v1.13 §"Adjacent observations" (d) — "`gen_ai.system` vs `gen_ai.provider.name` divergence... v1.13 does NOT touch this carry" | "divergence" + "does NOT touch this carry" | **CLOSED-as-resolved-at-115387b** — carry is stale; resolution was achieved at producer-side commit `115387b` (2026-05-26) without spec amendment. ZERO further apply-pass arc owed. |
| v1.14 §"Adjacent observations" (c) — "OD spec v1.13 finding (d)... Carried verbatim from v1.13. v1.14 does NOT touch this carry." | "Carried verbatim" | **CLOSED-as-resolved-at-115387b** per row 3 above. |
| v1.15 §"Adjacent observations" (c) — "OD spec v1.13 finding (d)... Carried verbatim from v1.13/v1.14. v1.15 does NOT touch this carry." | "Carried verbatim" | **CLOSED-as-resolved-at-115387b** per row 3 above. |
| v1.16 §"Adjacent observations" (b) — "OD spec v1.13/v1.14/v1.15 finding (d)/(c)/(c) — `gen_ai.system` vs `gen_ai.provider.name` divergence. Carried verbatim from v1.13/v1.14/v1.15. v1.16 does NOT touch this carry. Candidate for next operator-routed arc if WebFetch verification surfaces a third divergence." | "Carried verbatim" + "Candidate for next operator-routed arc if WebFetch verification surfaces a third divergence" | **CLOSED-as-resolved-at-115387b** per row 3 above. The "WebFetch verification surfaces a third divergence" framing was incorrect on the resolution mechanism — the resolution path was producer-side conform (115387b), NOT WebFetch-driven spec amendment. |
| v1.16 §"Filing footer" Successor row — "candidates: v1.16 finding (b) `gen_ai.system` vs `gen_ai.provider.name`" | "candidates" | Finding (b) **CLOSED-as-resolved-at-115387b** at v1.17. Removed from successor-arc candidate list. |

### §1.2 §C-OD-04 §4.3 Required (Stable) tier attribute set — empirical state at v1.17

Per §1.1 closure, the v1.2-lineage §C-OD-04 §4.3 Required (Stable) tier attribute set (`gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`) is fully conformant at production. The canonical reading at v1.17 confirms the v1.2 declaration was always correct; the v1.12-era divergence was a producer-side gap that has been closed.

| Attribute | §C-OD-04 §4.3 status | Production emission status (post-115387b) |
|---|---|---|
| `gen_ai.operation.name` | Required (Stable) — v1.2 declaration; per v1.16 §1.2 reads as `Required` per OTel naming | EMITTED at `llm_dispatch.py:340` (NEW at 115387b) |
| `gen_ai.provider.name` | Required (Stable) — v1.2 declaration; per v1.16 §1.2 reads as `Required` per OTel naming | EMITTED at `llm_dispatch.py:341` (renamed from `gen_ai.system` at 115387b) |
| `gen_ai.request.model` | Required (Stable) — v1.2 declaration; per v1.16 §1.2 reads as `Required` per OTel naming | EMITTED at `llm_dispatch.py:342` (preserved verbatim through 115387b) |

---

## §2 Finding closure (v1.12 + v1.13 + v1.14 + v1.15 + v1.16 §"Adjacent observations" finding (f)/(d)/(c)/(c)/(b))

**Closed-as-resolved-at-production-commit-115387b.** The v1.12-v1.16 carry of the `gen_ai.system` vs `gen_ai.provider.name` divergence is now closed at v1.17 §1 canonical-reading amendment table. The divergence existed at v1.12 authoring time, was resolved at producer-side commit `115387b` 2026-05-26 19:40 -0600, and the carry-text disposition was stale across v1.13/v1.14/v1.15/v1.16 because the resolution landed without spec carry-text refresh.

**Disposition at v1.17.** Finding (b) [v1.16 numbering; equivalently finding (c)/(c)/(d) at v1.15/v1.14/v1.13; equivalently finding (f) at v1.12] is **CLOSED-as-resolved-at-115387b**. Removed from v1.17 §"Adjacent observations" carry; no longer a deferred apply-pass arc.

**Distinction from v1.15 finding-(a) phantom closure.** The v1.15 finding-(a) closure was "CLOSED-as-phantom" — the defect never existed in the framed shape (cardinality + row-number + section-cite drift). The v1.17 finding-(b) closure is "CLOSED-as-resolved" — the defect existed at v1.12 authoring but was resolved at producer-side conform without carry-text refresh. The two patterns are sibling-but-distinct lineage finding types catalogued at §"Pattern catalogue" below.

---

## §3 Cross-artifact cite-cascade disposition (v1.17 NEW)

The `gen_ai.system` vs `gen_ai.provider.name` divergence is cited at multiple cross-artifact sites beyond the OD spec carry chain. Per delta-only-spec-file convention applied across the lineage chain, downstream readers of these artifacts MUST apply the v1.17 §1.1 canonical reading when interpreting the divergence-disposition tokens. The cross-artifact sites + their disposition at v1.17:

| Artifact | Site | Carry-text framing | Disposition at v1.17 |
|---|---|---|---|
| `Cross_Axis_Composition_Document_v2_11.md` | §0.5 (b) | "`gen_ai.system` vs `gen_ai.provider.name` attribute-name divergence at production... separate apply-pass arc owed at OD spec v1.13 or follow-on" | **CLOSED-as-resolved-at-115387b** per v1.17 §1.1. Cite-refresh deferred per FM-2 (downstream readers of CXA v2.11 apply v1.17 §1.1 mapping in-context). |
| `Cross_Axis_Composition_Document_v2_12.md` | §0.5 (c) | "Unchanged at v2.12; separate apply-pass arc owed" | **CLOSED-as-resolved-at-115387b** per v1.17 §1.1. Cite-refresh deferred per FM-2 (downstream readers of CXA v2.12 apply v1.17 §1.1 mapping in-context). |
| `Spec_Action_Surface_v1.md` (v1.7 lineage) | §3 (b) "Adjacent observations" | "`gen_ai.system` vs `gen_ai.provider.name` attribute-name divergence at production (OD v1.12 §"Adjacent observations" (f)). Unchanged; separate apply-pass arc." | **CLOSED-as-resolved-at-115387b** per v1.17 §1.1. Cite-refresh deferred per FM-2 (AS spec is delta-only; downstream readers apply v1.17 §1.1 mapping in-context). |
| `Implementation_Plan_Operational_Discipline_v2_19.md` | §"Adjacent observations" (a) | "U-OD-04 acceptance criterion #4 `gen_ai.provider.name` Required-tier preservation vs production attribute-name divergence... production at `harness-runtime/.../llm_dispatch.py:330` emits `gen_ai.system`... NOT patched at this v2.19 plan absorption per FM-2. Owed at separate apply-pass arc." | **CLOSED-as-resolved-at-115387b** per v1.17 §1.1. AC #4 was always correct at v2.19; the divergence was producer-side, not plan-side. Cite-refresh deferred per FM-2 (plan v2.19 is delta-only; downstream readers apply v1.17 §1.1 mapping in-context). |
| `Implementation_Plan_Operational_Discipline_v2_20.md` | §"Adjacent observations" (b) | "Carried forward from v2.19 (a); NOT patched per FM-2 single-focus scope" + Successor row "candidates: attribute-name `gen_ai.system` vs `gen_ai.provider.name` divergence per v2.19 (a) + v2.20 (b)" | **CLOSED-as-resolved-at-115387b** per v1.17 §1.1. Removed from v2.20 successor-arc candidate list. Cite-refresh deferred per FM-2 (plan v2.20 is delta-only; downstream readers apply v1.17 §1.1 mapping in-context). |
| `Spec_Harness_Runtime_v1.md` (v1.27 lineage) | Top change-note v1.27 "Adjacent observation (NOT patched per FM-2)" + body §14.5 line 1963 + §14.5 line 1993 | (1) top change-note: "sibling to OD spec v1.12 §"Adjacent observations" (f)... NOT patched per FM-2"; (2) body line 1963: "(`gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`...)"; (3) body line 1993: "(`gen_ai.system`, `gen_ai.request.model`, `gen_ai.response.id`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, etc.)" | (1) top change-note adjacent-observation **NOT closed at v1.17** — it flags `_PROVIDER_OPERATIONS` value-space non-conformance (`messages.create` / `chat.completions` / `chat` are API method names, NOT §4.2 enum values); sibling-but-distinct defect to the `gen_ai.system` → `gen_ai.provider.name` attribute-name divergence (the "sibling to OD v1.12 (f)" phrasing in v1.27 is a cross-reference, not equivalence); carried forward as v1.17 §"Adjacent observations" finding (g) for future operator-routed arc; (2)+(3) body cites refreshed at NEW runtime spec v1.28 delta per co-publication this arc — `gen_ai.system` → `gen_ai.provider.name` canonical-reading amendment table at runtime v1.28 §1. |
| `harness-od/CLAUDE.md` | §"Substitution surface" row H_T-OD-2 RETIRED entry | "Runtime emits `gen_ai.system` + `gen_ai.request.model` + `gen_ai.usage.{input,output}_tokens` + `gen_ai.response.id` per provider" | In-place edit at this arc: `gen_ai.system` → `gen_ai.provider.name`. Per-axis CLAUDE.md is not subject to delta-only convention; direct text edit applied at co-publication commit this arc. |
| Workspace `CLAUDE.md` (worktree root) | §2.3 OD spec + runtime spec rows | v1.16 + v1.27 row-text | Bumped to v1.17 + v1.28 at co-publication commit this arc with change-note narrative referencing v1.17 §"Filing footer" + runtime v1.28 §"Filing footer". |

---

## §4 Sections preserved verbatim at v1.17

Per delta-only-spec-file convention + FM-2 no-extension discipline + fidelity-pure citation-correction patch scope, the v1.17 amendment touches ONLY the NEW §1 canonical-reading amendment table + §2 finding closure + §3 cross-artifact cite-cascade disposition (all within this v1.17 delta file) + co-publication artifacts at runtime spec v1.28 + harness-od/CLAUDE.md in-place + workspace CLAUDE.md row bumps. The following sections are PRESERVED VERBATIM from their authoring versions:

- **§C-OD-04 §4.1** (v1.12-lineage span-name 2-component format per D-1 R2)
- **§C-OD-04 §4.2** (v1.2-lineage operations enum; v1.16 §1.1 canonical reading applied)
- **§C-OD-04 §4.3** (v1.2-lineage attribute tiers; v1.16 §1.2 canonical reading applied; v1.17 §1.2 confirms full conformance at production)
- **§C-OD-04 §4.4** (v1.2-lineage; not in scope at this fork)
- **§C-OD-04 §4.5** (v1.2-lineage; verified MATCH at v1.16 §1.4)
- **§C-OD-05 §5.1 rows 1-15** (v1.2-lineage; v1.13 row 5 sub-note + v1.15 §1 canonical reading preserved verbatim)
- **§C-OD-05 §5.2 + §5.3** (ingestion-posture invariants)
- **§C-OD-06 through §C-OD-33** (all v1.2-v1.16 lineage content preserved per delta-only-spec-file convention)
- **All v1.3 through v1.16 substantive amendments** (D-1 R2 absorption at v1.12; finding-(a) closure + canonical-reading at v1.15; D-2 + D-3 re-litigation at v1.16; all prior carry resolutions)

---

## §5 Pattern catalogue (v1.17 NEW)

**Pattern: resolved-but-carry-stale.** A finding flagged at version vN with disposition "NOT patched per FM-2; separate apply-pass arc owed" gets resolved at downstream code (production / impl / co-publication) at commit C in the lineage BEFORE the carry-text disposition is refreshed at versions vN+1, vN+2, etc. The carry-text becomes stale on the day of resolution but propagates verbatim across subsequent delta files. Discovery requires empirical-grep verification of the production state (or impl state) against the carry-text framing; on confirmation, a corrective re-litigation arc closes the carry-text as **CLOSED-as-resolved-at-{commit}** rather than the usual **CLOSED-as-resolved-at-{spec-version}** closure shape.

**Sibling pattern: phantom-as-described** (v1.15 finding-(a) precedent). A finding flagged at version vN with disposition "NOT patched per FM-2; separate apply-pass arc owed" turns out on empirical verification to have NEVER existed in the framed shape — the defect description was wrong (e.g., row-number drift, cardinality drift, section-cite drift). Corrective re-litigation closes the carry-text as **CLOSED-as-phantom**.

**Sibling pattern: stale-carry-with-real-but-different-shape** (v1.16 carry from v1.13/v1.14/v1.15 precedent). A finding flagged at version vN with disposition "NOT patched per FM-2; separate apply-pass arc owed" has a real defect lineage but the carry-text framing predicts the wrong corrective shape. Empirical re-litigation surfaces the actual defect shape; the corrective arc lands the real shape, NOT the framed shape.

**Common ancestor.** All three patterns are species of "stale carry-text disposition" — a defect-carry framing that has decayed against empirical state without refresh. Discovery discipline: at every fork-arc opening, empirically verify EVERY claim in the carried defect-framing BEFORE treating the carry as actionable in the framed shape. Catalogued precedent applications: v1.15 finding-(a) (phantom); v1.16 D-2/D-3 (different-shape); v1.17 finding-(b) (resolved-but-stale).

**Discipline candidate.** At fork-arc closure, the corrective spec delta MUST refresh the carry-text disposition at all downstream artifacts citing the resolved/phantom/different-shape finding (per cite-cascade discipline catalogued at workspace `CLAUDE.md` §4.3). v1.17 §3 cross-artifact cite-cascade disposition table is the v1.17-instance application of this discipline.

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **OD spec v1.13/v1.14/v1.15/v1.16 finding (d)/(c)/(c)/(b) — CLOSED-as-resolved-at-115387b at v1.17 §2.** Removed from "Adjacent observations" carry; no longer a deferred apply-pass arc.

(b) **v1.16 finding (c) — §8.4.2 anticipated cases empirical-verification.** Carried verbatim from v1.16. v1.17 does NOT touch this carry.

(c) **v1.16 finding (d) — v1.15 §15.2 vs §15.4 split informational.** Carried verbatim from v1.16. v1.17 does NOT touch this carry (informational only).

(d) **v1.16 finding (e) — §C-OD-04 §4.3 tier-assignment audit against 4-tier table.** Carried verbatim from v1.16. v1.17 does NOT touch this carry.

(e) **v1.16 finding (f) — §C-OD-04 §4.4 against OTel 1.41.0 archived text.** Carried verbatim from v1.16. v1.17 does NOT touch this carry.

(f) **v1.16 finding (g) — workflow-grammar reconciliation discipline candidate at `Project_Workflow_v1_8.md`.** Carried verbatim from v1.16. v1.17 does NOT touch this carry.

(g) **NEW at v1.17 — `_PROVIDER_OPERATIONS` value-space non-conformance to §4.2 operation enum.** Production at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:505-508` maps provider name to API method name (`messages.create` / `chat.completions` / `chat`) — NOT to OTel GenAI semconv §4.2 operation enum values (`chat` / `text_completion` / `embeddings` / etc.). This is the runtime spec v1.27 "Adjacent observation" finding (g) sibling to the now-closed v1.12 finding (f). Production span name post-115387b is e.g. `messages.create claude-opus-4-7` — conforms to v1.12 §4.1 2-token shape but the `operation` token is an API method name, not a §4.2 enum value (which now reads 9-value at v1.16 §1.1). Surfaced as v1.17 finding (g); NOT patched per FM-2 single-focus arc scope; candidate for future operator-routed arc.

(h) **NEW at v1.17 — `provider_name` value-space partial-conformance to OTel 1.41.0 `gen_ai.provider.name` known-values enum.** Per commit `115387b` finding (h): `anthropic` + `openai` conformant; `ollama` not in 1.41.0 enum. Surfaced as v1.17 finding (h); NOT patched per FM-2 single-focus arc scope.

---

## Downstream artifacts requiring absorption at follow-on arcs

| Artifact | Required change | Owner |
|---|---|---|
| Workspace `CLAUDE.md` §2.3 OD spec row | v1.16 → v1.17 row update with v1.17 change-note narrative; v1.16 + earlier lineage preserved | This session apply-pass arc |
| Workspace `CLAUDE.md` §2.3 runtime spec row | v1.27 → v1.28 row update with v1.28 change-note narrative; v1.27 + earlier lineage preserved | This session apply-pass arc |
| `Spec_Harness_Runtime_v1.md` | NEW v1.28 change-note prepended; canonical-reading amendment table refreshing body lines 1963 + 1993 `gen_ai.system` → `gen_ai.provider.name`; body text PRESERVED VERBATIM per delta-only convention | This session apply-pass arc |
| `harness-od/CLAUDE.md` H_T-OD-2 retirement entry | In-place text edit: `gen_ai.system` → `gen_ai.provider.name` (per-axis CLAUDE.md is not subject to delta-only convention) | This session apply-pass arc |
| OD plan `Implementation_Plan_Operational_Discipline_v2_20.md` | NO change owed — plan §"Adjacent observations" (b) carry disposition refreshes in-context per v1.17 §1.1 canonical reading; delta-only-plan convention preserves v2.20 verbatim. Removal from successor-arc candidate list is informational, not contract-affecting. | n/a |
| `Cross_Axis_Composition_Document_v2_12.md` | NO change owed — CXA §0.5 (c) carry disposition refreshes in-context per v1.17 §1.1 canonical reading; delta-only convention preserves v2.12 verbatim. | n/a |
| `Spec_Action_Surface_v1.md` (v1.7 lineage) | NO change owed — AS spec §3 (b) carry disposition refreshes in-context per v1.17 §1.1 canonical reading; delta-only convention preserves v1.7 verbatim. | n/a |
| CP spec / CP plan / AS plan / ADR / ADD / PRD / harness-* helper code | NO change owed — divergence was OD-axis carry + runtime-axis spec body + per-axis CLAUDE.md only; ZERO cross-axis cascade beyond the cite-cascade disposition documented at v1.17 §3. | n/a |

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.17 (Fidelity-pure citation-correction patch closing v1.13/v1.14/v1.15/v1.16 §"Adjacent observations" finding (d)/(c)/(c)/(b) — `gen_ai.system` vs `gen_ai.provider.name` divergence — as **CLOSED-as-resolved-at-production-commit-115387b** 2026-05-26; NEW §1 canonical-reading amendment table + §2 finding closure + §3 cross-artifact cite-cascade disposition + §5 pattern catalogue; v1.16 + earlier files PRESERVED VERBATIM per delta-only-spec-file convention) |
| Trigger | v1.16 §"Adjacent observations" finding (b) re-evaluation per operator-routed adjacent-observation closure arc 2026-05-26 (session resumption from `20260526-234500-tension-004-d2-d3-second-relitigation.md`); empirical grep at production confirmed ZERO `gen_ai.system` literals remain (only `gen_ai.system_instructions` Opt-In content attribute, which is a distinct semantically-unrelated attribute) |
| Supersedes | v1.12 §"Adjacent observations" (f) + v1.13/v1.14/v1.15/v1.16 finding (d)/(c)/(c)/(b) "separate apply-pass arc owed" framing — superseded per empirical-verification-at-115387b discovery |
| Scope of revision | NARROW: NEW §1 canonical-reading amendment table refreshing carry-text disposition + §2 finding closure + §3 cross-artifact cite-cascade disposition + §5 pattern catalogue. Co-publication: runtime spec v1.28 NEW change-note + canonical-reading amendment table; harness-od/CLAUDE.md in-place edit; workspace CLAUDE.md row bumps. ZERO contract change; ZERO signature change; ZERO acceptance-criterion change; ZERO behavior change. |
| Contract change | None. Fidelity-pure citation-correction patch. |
| Cross-axis cascade | ZERO at spec semantics layer. Cross-artifact cite-cascade disposition at v1.17 §3 documents 8 sites with stale carry-text; 2 sites (runtime spec body + harness-od/CLAUDE.md) refreshed at this arc; 6 sites (CXA v2.11, CXA v2.12, AS spec v1.7, OD plan v2.19, OD plan v2.20, runtime spec v1.27 top adjacent-observation) carry per FM-2 with downstream readers applying v1.17 §1.1 mapping in-context. |
| Authority anchor | Commit `115387b6e32d61664ebc3d855583dfd09cd5862a` (2026-05-26 19:40 -0600) — producer-side conform at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:340-342` emitting all 3 §C-OD-04 §4.3 Required (Stable) tier attributes; OD spec v1.2 §C-OD-04 §4.3 canonical declaration (preserved verbatim through v1.16); ADR-D6 v1.2 §1.2 [HIGH] OTel GenAI semconv 1.41.0 as cross-vendor floor |
| Predecessor | v1.16 (Tension 004 D-2 + D-3 re-litigation; SECOND tension re-litigation in workspace history) |
| Successor | v1.18 (next operator-discretion arc — candidates: v1.17 finding (b) §8.4.2 anticipated cases empirical-verification; v1.17 finding (d) tier-assignment audit; v1.17 finding (e) §4.4 audit; v1.17 finding (f) workflow-grammar reconciliation discipline at `Project_Workflow_v1_8.md`; v1.17 finding (g) `_PROVIDER_OPERATIONS` value-space non-conformance to §4.2 enum) |
| Advisor application | 15th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` — pre-substantive advisor pass confirmed resolved-but-carry-stale diagnosis (distinct from v1.15 phantom + v1.16 different-shape lineage patterns) + sharpened scope selection (A/B/C ladder; operator ratified C = wider) + flagged downstream sites my initial sketch undercounted (runtime spec body + harness-od CLAUDE.md not in OD-only sketch) |
| Pattern catalogue | THIRD species of stale-carry-text disposition catalogued at v1.17 §5 — sibling to v1.15 phantom-as-described + v1.16 stale-carry-with-real-but-different-shape; common ancestor "stale carry-text disposition"; discipline candidate "at fork-arc opening empirically verify EVERY claim BEFORE treating the carry as actionable" |
