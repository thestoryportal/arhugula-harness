# Spec: Operational Discipline — v1.23 (delta over v1.22)

---

## Change-note (v1.22 → v1.23)

**Scope of revision.** Fidelity-pure citation-correction patch closing v1.22 §"Adjacent observations" finding (e) — `gen_ai.provider.name` stability tier divergence — via canonical-reading dimensional split at §C-OD-04 §4.3 tier-label vocabulary. Pre-v1.23 §4.3 tier labels (`Required (Stable)`, `Recommended (Development)`, `Conditionally Required`, `Opt-In content`) conflated two orthogonal OTel 1.41.0 dimensions — Requirement-Level (`Required` / `Conditionally Required` / `Recommended` / `Opt-In`) AND Stability (`Stable` / `Development` / `Experimental`). The v1.16 §1.2 amendment correctly split 3 → 4 tiers on the requirement-level axis but inherited the v1.2-lineage conflation in three of the four label strings. v1.23 separates the dimensions at the canonical-reading layer: tier labels become PURE requirement-level; stability is declared per-attribute at a NEW §4.3.1 stability-classification table cross-referenced from §4.3. v1.22 + earlier file bodies PRESERVED VERBATIM per delta-only-spec-file convention.

**Audit lineage.** v1.22 (e) carried verbatim across 7 versions (v1.16 finding (b) → v1.17 (c) → v1.18 (c) → v1.19 (f) → v1.20 (e) → v1.21 (f) → v1.22 (e)) awaiting operator-discretion stance routing. Operator-routed 2026-05-27 (this session) post-empirical-verification at OTel 1.41.0 archived text (WebFetch this session): all three §4.3 base-layer attributes citing `Stable` in their OD-side label (`gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`) actually ship at OTel stability=`Development`; the `Stable` half of the v1.2-lineage label was a v1.2-authoring drift, not a deliberate OD-stricter stance.

**Empirical verification.**

- OTel 1.41.0 archived text (WebFetch 2026-05-27 against `https://github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md`):
  - `gen_ai.operation.name` — Requirement: **Required**; Stability: **Development**
  - `gen_ai.provider.name` — Requirement: **Required**; Stability: **Development**
  - `gen_ai.request.model` — Requirement: **Conditionally Required**; Stability: **Development**
- All three attributes confirmed at Development stability tier across Inference, Embeddings, and Retrievals span types per the cited spec.
- Production emission posture at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:350` (`gen_ai.provider.name`) + companion sites: unconditional emission via `span.set_attribute(...)`. Stability tier does NOT gate emission; only Requirement-Level + cardinality-safe-attribute discipline (C-OD-11) gate emission. The dimensional split at v1.23 is therefore vocabulary-only at the canonical-reading layer; ZERO behavior change at production.

**Distinctive lineage finding.** v1.22 (e) closes via a closure event class catalogued at workflow v1.9 §7.4.7.2 row 3 (resolved-but-carry-stale-inherited) with sub-species refinement **3.empirical-verification-of-external-authority** — distinct from v1.22's sibling sub-species 3.workflow-grammar (closure via upstream workflow-doc canonicalization) and the existing 3.code-resolution / 3.fork-doc-closure sub-species. Closure event is "external-authority text empirically verified at WebFetch against archived URL; carry resolved at canonical-reading amendment that absorbs the verified text." NOT a new species at the 5-species enumeration; sub-species refinement at column "Sub-species". Future workflow-doc revision MAY catalogue the refinement at §7.4.7.2.

**No fork doc filed.** Per workspace precedent for fidelity-pure citation-correction patches anchored at conclusive empirical state (v1.15 phantom; v1.17 resolved-but-stale; v1.18 authoring-time-stale; v1.20 hierarchy narrowing; v1.21 post-authoring-stale; v1.22 upstream-workflow-canonicalization; v1.23 empirical-verification-of-external-authority). OTel 1.41.0 archived text IS canonical authority anchor; ADR-D6 v1.2 §1.2 [HIGH] cross-vendor floor cite already in place; no separate fork doc.

**Production-code co-publication.** Comment + docstring refresh at `harness-od/src/harness_od/otel_genai_base.py` (lines 82–105 AttributeTier docstring; lines 156–176 BASE_LAYER_ATTRIBUTES per-tier comments) for byte-exact alignment with v1.23 canonical reading. **Enum identifier names preserved verbatim as DERIVATIVE naming** per v1.16 §1.2 precedent ("v1.2 internal naming preserved as DERIVATIVE naming with the OTel canonical names as the authoritative names at v1.16"); `REQUIRED_STABLE` / `RECOMMENDED_DEVELOPMENT` / `OPT_IN_CONTENT` enum members + their 49 callsites across `harness-od/` preserved unchanged at this arc. Enum-rename pass deferred as v1.23 successor candidate (~3-file ~49-site arc; out of scope at this single-focus fidelity-pure patch per FM-2).

**Co-publication this session.** Workspace `CLAUDE.md` §2.3 OD spec row bumped to v1.23 with closure narrative. ZERO cross-axis cascade verified via grep (CXA v2.13 + AS spec v1.7 + CP spec v1.19 + plan files do NOT cite the v1.2-lineage tier labels at canonical-reading sites).

---

## §1 Finding-closure-disposition refresh

### §1.1 v1.22 §"Adjacent observations" finding (e) — CLOSED

**Carry-text at v1.22.** *"v1.21 finding (e) — `gen_ai.provider.name` stability tier divergence. Carried verbatim. OTel 1.41.0 archived text declares `gen_ai.provider.name` as `stability: development`; OD spec C-OD-04 §4.3 tier name reads `Required (Stable)`. GENUINE per sweep audit. Future operator-discretion stance routing (mirror-OTel-stability-tier vs document-OD-stricter-explicitly). v1.22 does NOT touch this carry."*

**Disposition at v1.23.** **CLOSED-by-empirical-verification-at-OTel-1.41.0-archived-text-and-canonical-reading-dimensional-split** 2026-05-27. Stance routed at operator AskUserQuestion this session: **separate the dimensions**. Tier labels at §C-OD-04 §4.3 carry PURE requirement-level vocabulary at v1.23; stability is declared per-attribute at NEW §4.3.1 cross-reference table. The carry was framed imprecisely at v1.16 (b) original authoring: the "Required" half of the `Required (Stable)` label IS correct (matches OTel requirement-level for `gen_ai.operation.name` + `gen_ai.provider.name`); the `(Stable)` half was a v1.2-authoring drift, NOT a deliberate OD-stricter stance (no anchor cite for stricter-than-OTel posture exists in v1.2 lineage). Sub-species: 3.empirical-verification-of-external-authority.

### §1.2 §C-OD-04 §4.3 tier-label canonical reading (v1.16 §1.2 amendment refined)

The v1.16 §1.2 canonical reading declared a 4-tier table mapping OTel canonical names to v1.2 internal names:

| Tier slot | Internal name (v1.16) | OTel canonical name |
|---|---|---|
| 1 | `Required (Stable)` | `Required` |
| 2 | `Conditionally Required` | `Conditionally Required` |
| 3 | `Recommended (Development)` | `Recommended` |
| 4 | `Opt-In content` | `Opt-In` |

The v1.23 canonical reading collapses the dimensional conflation in internal names 1, 3, and 4. Tier labels at §4.3 now read AS the OTel canonical names verbatim:

| Tier slot | Canonical reading at v1.23 (requirement-level only) |
|---|---|
| 1 | `Required` |
| 2 | `Conditionally Required` |
| 3 | `Recommended` |
| 4 | `Opt-In` |

Stability classification for each attribute in the §4.3 base-layer table is declared at the NEW §4.3.1 table below; cross-references at every prior-version site reading the v1.2-lineage label apply this substitution. Existing tier-assignments per v1.16 §1.3 PRESERVED VERBATIM (assignment is a separate concern from labeling).

### §1.3 §C-OD-04 §4.3.1 stability classification (NEW)

NEW section interleaved at canonical-reading layer between §4.3 attribute tiers and §4.4 hierarchy correlation; declared at v1.23 only (v1.2-v1.22 file bodies do not contain §4.3.1; readers of v1.2-v1.22 MUST apply the v1.23 canonical reading at this index):

**§4.3.1 OTel stability classification per base-layer attribute.** Per OTel 1.41.0 archived text (`https://github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md` empirically verified 2026-05-27), every attribute in the §4.3 base-layer table ships at OTel stability tier `Development`. The stability dimension is independent of the Requirement-Level dimension at §4.3; both dimensions are declared per OTel 1.41.0.

| Attribute | Requirement-Level (§4.3) | OTel Stability |
|---|---|---|
| `gen_ai.operation.name` | Required | Development |
| `gen_ai.provider.name` | Required | Development |
| `gen_ai.request.model` | Conditionally Required | Development |
| `server.port` | Conditionally Required | Development |
| `gen_ai.conversation.id` | Conditionally Required | Development |
| `gen_ai.usage.input_tokens` | Recommended | Development |
| `gen_ai.usage.output_tokens` | Recommended | Development |
| `gen_ai.response.finish_reasons` | Recommended | Development |
| `server.address` | Recommended | Development |
| `gen_ai.input.messages` | Opt-In | Development |
| `gen_ai.output.messages` | Opt-In | Development |
| `gen_ai.system_instructions` | Opt-In | Development |
| `gen_ai.tool.definitions` | Opt-In | Development |
| `gen_ai.tool.call.arguments` | Opt-In | Development |
| `gen_ai.tool.call.result` | Opt-In | Development |
| `gen_ai.retrieval.documents` | Opt-In | Development |
| `gen_ai.retrieval.query.text` | Opt-In | Development |

**Emission-gating invariant.** Stability tier does NOT gate emission; only Requirement-Level (§4.3) + cardinality-safe-attribute discipline (C-OD-11) gate emission. Stability is metadata for downstream consumers tracking OTel semconv maturity; it is informational at the OD-side ingestion layer.

### §1.4 Disposition summary

| v1.22 carry | Closure event | Closure commit | Status at v1.23 |
|---|---|---|---|
| §"Adjacent observations" (e) | OTel 1.41.0 archived text empirical verification + v1.23 §1.2/§1.3 canonical-reading dimensional split | this session (filing commit on `worktree-od-spec-v1-23-provider-name-tier-split`) | **CLOSED** |

Carry removed from v1.23 §"Adjacent observations" carry-set. v1.22 file body PRESERVED VERBATIM per delta-only-spec-file convention; v1.23 §1 is the canonical-reading amendment for the disposition layer.

---

## §2 Cross-artifact cite-cascade disposition (v1.23 NEW)

| Artifact | Site | Disposition at v1.23 |
|---|---|---|
| `harness-od/src/harness_od/otel_genai_base.py` | AttributeTier docstring (lines 82–105) + BASE_LAYER_ATTRIBUTES per-tier comments (lines 156–176) | **CO-PUBLISHED this arc** — comment + docstring refresh for byte-exact alignment; enum identifiers PRESERVED VERBATIM as DERIVATIVE naming per v1.16 §1.2 precedent |
| `harness-od/src/harness_od/otel_genai_base.py` | `AttributeTier` enum member names (`REQUIRED_STABLE` / `RECOMMENDED_DEVELOPMENT` / `OPT_IN_CONTENT`) | NO change owed at this arc — DERIVATIVE naming preserved; enum-rename pass deferred as v1.23 successor candidate per v1.16 §1.2 precedent |
| `harness-od/tests/test_otel_genai_base.py` | 49-site enum-name reference set | NO change owed at this arc — derivative of the enum identifier preservation above |
| `harness-od/src/harness_od/harness_breaker_schema.py` | Enum-name cite | NO change owed at this arc — derivative of enum identifier preservation |
| `design-substrate/Cross_Axis_Composition_Document_v2_13.md` | Tier-label cites at canonical-reading sites | NO change owed — verified via grep this session; CXA does NOT cite the v1.2-lineage tier-label string |
| `design-substrate/Spec_Action_Surface_v1_7.md` | Tier-label cites | NO change owed — verified via grep this session |
| `design-substrate/Spec_Control_Plane_v1_19.md` | Tier-label cites | NO change owed — verified via grep this session |
| `Implementation_Plan_Operational_Discipline_v2_22.md` | U-OD-04 + tier-label narrative | NO change owed — plan-side does NOT cite the v1.2-lineage label at canonical-reading sites |
| Workspace `CLAUDE.md` §2.3 OD spec row narrative | v1.22 row narrative | **CO-PUBLISHED this arc** — bumped to v1.23 with closure narrative |
| `design-substrate/Project_Workflow_v1_9.md` §7.4.7.2 | Sub-species refinement (3.empirical-verification-of-external-authority) | NO change owed — surfaced as v1.23 §"Adjacent observations" (g) for future workflow-doc-revision discretion |

---

## §3 Sections preserved verbatim at v1.23

Per delta-only-spec-file convention + FM-2 no-extension discipline + fidelity-pure citation-correction scope, the v1.23 amendment touches ONLY the NEW §1 finding-closure-disposition refresh + §2 cross-artifact cite-cascade disposition + §"Adjacent observations" refresh. The following sections are PRESERVED VERBATIM from their authoring versions:

- **§C-OD-04 §4.1 / §4.2 / §4.4 / §4.5** (all v1.12+ amendments preserved; v1.16 §1.1 / §1.3 amendments preserved; v1.20 §1.1 §4.4 narrowing preserved)
- **§C-OD-04 §4.3 tier-assignment for individual attributes** (v1.16 §1.3 PRESERVED VERBATIM; only the tier-LABEL vocabulary is refined at v1.23 §1.2; per-attribute tier ASSIGNMENT is unchanged — `gen_ai.provider.name` remains at tier slot 1, `gen_ai.request.model` remains at tier slot 2 per v1.16 §1.2)
- **§C-OD-05 through §C-OD-33** (all v1.2-v1.22 lineage content)
- **All v1.3–v1.22 substantive amendments**

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **v1.22 finding (e) — CLOSED-by-empirical-verification-at-OTel-1.41.0-and-canonical-reading-dimensional-split at v1.23 §1.1–§1.3.** Removed from "Adjacent observations" carry.

(b) **v1.22 finding (c) — §8.4.2 anticipated cases empirical-verification.** Carried verbatim from v1.16 → v1.17 → v1.18 → v1.19 → v1.20 → v1.21 → v1.22 → v1.23. Sweep verification 2026-05-27: production grep for the 3 anticipated cases returns ZERO production hits at HEAD; deferred-monitor status preserved. v1.23 does NOT touch this carry.

(c) **v1.22 finding (d) — v1.15 §15.2 vs §15.4 split informational.** Carried verbatim. AS spec v1.7 unchanged since v1.17; carry remains genuine. v1.23 does NOT touch this carry.

(d) **v1.22 finding (f) — discipline-validation observation (informational, Class 3).** Carried verbatim with strengthening at v1.23 §"Change-note" — v1.23 is the FIRST PRODUCTION APPLICATION of the workflow v1.9 §7.4.7.3 audit discipline at the empirical-verification-of-external-authority sub-species (WebFetch against OTel archived text). The discipline empirically validates: external-authority WebFetch verification catches subtle v1.2-lineage drift that 7 prior delta arcs preserved without surfacing. v1.23 does NOT touch the upstream Project_Workflow_v1_9.md artifact.

(e) **v1.22 finding (g) — sub-species 3.workflow-grammar catalogued.** Carried verbatim. v1.23 adds a sibling sub-species 3.empirical-verification-of-external-authority at §"Change-note" Distinctive lineage finding; future workflow-doc revision MAY consolidate both sub-species under a §7.4.7.2 "Sub-species" column extension. v1.23 does NOT patch the upstream artifact per FM-2.

(f) **NEW at v1.23 — `harness-od/` enum-rename arc deferred.** Production code at `harness-od/src/harness_od/otel_genai_base.py:102–104` carries enum member names (`REQUIRED_STABLE` / `RECOMMENDED_DEVELOPMENT` / `OPT_IN_CONTENT`) that conflate the requirement-level + stability dimensions per v1.2-lineage label naming. Per v1.16 §1.2 precedent (DERIVATIVE-naming preservation), enum identifiers are PRESERVED at this arc; rename pass is a separate ~3-file ~49-site arc owed at future operator-discretion routing. Class 3 informational. The DERIVATIVE-naming framing is documented at this v1.23 arc (production comments refreshed to cite canonical names alongside derivative names).

(g) **NEW at v1.23 — workflow v1.9 §7.4.7.2 sub-species column extension candidate.** Two sibling sub-species of species 3 (resolved-but-carry-stale-inherited) catalogued in 2 consecutive arcs: v1.22 introduced 3.workflow-grammar; v1.23 introduces 3.empirical-verification-of-external-authority. The existing 3.code-resolution + 3.fork-doc-closure sub-species form a 4-element set with distinct closure-event-classes. Future workflow-doc revision MAY add a "Sub-species" column to §7.4.7.2 enumerating the 4 sub-species per species 3 (and similar potential refinements at species 1/2/4/5). Class 3 informational; NOT patched per FM-2 single-focus arc scope.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.23 (Fidelity-pure citation-correction patch closing v1.22 §"Adjacent observations" finding (e) `gen_ai.provider.name` stability tier divergence — via canonical-reading dimensional split at §C-OD-04 §4.3 tier-label vocabulary + NEW §4.3.1 stability classification table; v1.22 + earlier files PRESERVED VERBATIM per delta-only-spec-file convention) |
| Trigger | Operator-discretion routing 2026-05-27 of v1.22 (e) carry preserved across 7 versions (v1.16 → v1.22) post-empirical-verification at OTel 1.41.0 archived text (WebFetch this session) |
| Supersedes | v1.22 §"Adjacent observations" (e) "Carried verbatim" framing — superseded at v1.23 §1 closure. v1.16 §1.2 tier-label internal-name framing for tier slots 1/3/4 (3 of 4 labels refined to pure requirement-level vocabulary; tier slot 2 `Conditionally Required` unchanged). |
| Scope of revision | NARROW: NEW §1 + §2 + §3 + §"Adjacent observations" refresh. ZERO contract / signature / AC / behavior change at runtime. Co-publication: production code comment + docstring refresh at `harness-od/src/harness_od/otel_genai_base.py` (enum identifiers PRESERVED VERBATIM as DERIVATIVE naming per v1.16 §1.2 precedent); workspace CLAUDE.md OD spec row bump. |
| Cross-axis cascade | ZERO. Verified via grep at design-substrate/ (CXA v2.13 + AS spec v1.7 + CP spec v1.19 + plan files) and at production layer (the dimensional split is vocabulary-only at the canonical-reading layer; emission posture unchanged). |
| Authority anchor | OTel 1.41.0 archived text `gen-ai-spans.md` (WebFetch 2026-05-27); ADR-D6 v1.2 §1.2 [HIGH] cross-vendor floor cite already in place; D-1 R2 + D-2/D-3 v1.16 §1.2 apply-pass precedent |
| Predecessor | v1.22 (Fidelity-pure citation-correction patch closing post-authoring stale carries (d) workflow-grammar discipline + (i) FIFTH species via upstream-workflow-grammar-canonicalization) |
| Successor | v1.24 (next operator-discretion arc — candidates: v1.23 (b) §8.4.2 anticipated cases; (c) v1.15 §15.2 vs §15.4 split; (e) sub-species refinement at workflow-doc; (f) `harness-od/` enum-rename pass; (g) workflow v1.9 §7.4.7.2 "Sub-species" column extension) |
| Audit lineage | v1.22 (e) carry preserved 7 versions (v1.16 → v1.17 → v1.18 → v1.19 → v1.20 → v1.21 → v1.22) awaiting operator-discretion stance routing. Routed 2026-05-27 post-empirical-verification at OTel 1.41.0 archived text. |
