# Implementation Plan — Operational Discipline v2.20

## Change-note (v2.19 → v2.20)

**Scope of revision.** Class 1 fork resolution absorption per `.harness/class_1_fork_tension_004_d2_d3_otel_141_relitigation.md` §4.1 (A) full-conformance + §4.2 (γ) single-focus operator-ratified 2026-05-26 + OD spec v1.15 → v1.16 §C-OD-04 §4.2 + §4.3 canonical-reading amendment (`Spec_Operational_Discipline_v1_16.md` co-published this session). Single-unit absorption at U-OD-04 (`§3.2.1` per Implementation_Plan_Operational_Discipline_v2_5.md authoring site). Re-litigates `Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` (2026-05-15) D-2 + D-3 ratifications — the §7 reconciliation pass closed D-2/D-3 as "RESOLVED at OD plan v2.5 plan-conforms-to-spec" without re-performing the §4 step 3 tiebreaker check against actual OTel 1.41.0 archived text; this arc performed the check; the check failed for D-2 + D-3 (MATCH for D-4); both spec + plan absorb the +2 enum values + +1 tier per fork doc §4.1 (A) full-conformance ratification.

**v2.19 substantive content preserved verbatim.** All v2.19 content (U-OD-00 through U-OD-54; clusters 1 through 4-OD-E; DAG topology; coverage matrix; cross-axis edge enumeration; all unit bodies other than U-OD-04 D-2 + D-3 amendments) preserved unchanged at v2.20. The v2.19 U-OD-04 D-1 absorption (2-component span-name format) preserved verbatim — D-1 was already corrected at v2.19 per the morning's R2 arc.

**Source of fix.** Class 1 fork resolution apply pass — D-2 operations enum 7 → 9 (add `invoke_workflow` + `retrieval`) + D-3 attribute tiers 3 → 4 (add `Conditionally Required`) per actual OTel GenAI semconv 1.41.0 archived text at `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md`. Companion artifacts at this session: OD spec v1.16 (NEW §1 canonical-reading amendment for §4.2 + §4.3); helper update at `harness-od/src/harness_od/otel_genai_base.py:58-86` (GenAiOperation StrEnum 7 → 9 members + AttributeTier StrEnum 3 → 4 members) + helper test update at `harness-od/tests/test_otel_genai_base.py` (cardinality assertions 7 → 9 + 3 → 4 + 3 new test names); workspace `CLAUDE.md` §2.3 OD spec row v1.15 → v1.16; Tension 004 §7.6 NEW supersession block.

**Narrow-scope framing.** §4.2 + §4.3 cardinality ONLY (D-2 + D-3). §4.1 span-name format (D-1) already corrected at v2.19. §4.4 + §4.5 + §C-OD-04 §4.3 per-attribute tier-assignment audit NOT touched at v2.20 per FM-2 + fork doc §4.2 (γ) single-focus scope. D-4 verified MATCH at this session (no amendment owed). D-3b tier-assignment preserved verbatim per OD spec v1.16 §1.3.

**Amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **U-OD-04 plan body** (authored at `Implementation_Plan_Operational_Discipline_v2_5.md` §3.2.1, preserved verbatim through v2.6/.../v2.19 outside D-1) | (a) **Inputs** line: append `+ OD spec v1.16 §C-OD-04 §4.2 + §4.3 canonical-reading amendment (operations enum 7 → 9 values: add invoke_workflow + retrieval; attribute tiers 3 → 4 tiers: add Conditionally Required — per actual OTel GenAI semconv 1.41.0 archived text; v1.2-v1.15 7-value + 3-tier readings SUPERSEDED at v1.16)`; (b) **Signatures** block: `GenAiOperation = 6 values` → `9 values` enumeration update — add `INVOKE_WORKFLOW = "invoke_workflow"` + `RETRIEVAL = "retrieval"` at canonical alphabetic positions (positions 7 + 8 per v1.16 §1.1 table); `AttributeTier = 4 values` (was struck to 3 at v2.5 plan-conforms-to-spec; restored to 4 at v2.20) — add `CONDITIONALLY_REQUIRED = "Conditionally Required"` at position 2; (c) **AC #2** (operations enum cardinality): `exactly 6 operations` → `exactly 9 operations per OD spec v1.16 §C-OD-04 §4.2 (OTel 1.41.0)`. NEW sub-criterion: `9 values include invoke_workflow + retrieval per v1.16 §1.1 NEW additions`; (d) **AC #3** (attribute tier cardinality): `exactly 4 tiers per §4.3 verbatim` (v2.1-v2.4 original) → `exactly 3 tiers (v2.5-v2.19 plan-conforms-to-spec)` → `exactly 4 tiers per OD spec v1.16 §C-OD-04 §4.3 (OTel 1.41.0)`. The v2.5 plan-conforms-to-spec strike of `CONDITIONAL` is SUPERSEDED — the v2.1-v2.4 original 4-tier shape conformed to OTel 1.41.0 (the spec was wrong, not the plan). NEW sub-criterion: `4 values include Conditionally Required per v1.16 §1.2 NEW addition`; (e) **AC #4** (Required (Stable) tier list — 3 attributes): PRESERVED VERBATIM at v2.20 per OD spec v1.16 §1.3 D-3b preservation framing. Tier-assignment audit against new 4-tier table deferred per FM-2 + fork doc §4.2 (γ); (f) **Tests** line: NEW test `test_genai_operation_cardinality_nine` (was `_seven` at v2.19; renamed) + NEW test `test_genai_operation_includes_invoke_workflow` + NEW test `test_genai_operation_includes_retrieval` + NEW test `test_attribute_tier_cardinality_four` (was `_three` at v2.19; renamed) + NEW test `test_attribute_tier_conditionally_required_present`; existing tests `test_genai_operation_includes_generate_content` + `test_span_name_format_byte_exact_two_component` + `test_span_name_resolves_at_span_emission_time` + `test_base_layer_attributes_byte_exact_per_semconv_1_41_0` + tier-membership-per-attribute tests preserved verbatim per D-3b preservation framing; (g) **Rollback boundary v2.5 revert appendix**: STRUCK in full at v2.20 — at v2.20 the original v2.1-v2.4 4-tier `AttributeTier` enum (with `CONDITIONAL`) is canonical (matches OTel 1.41.0 via v1.16); the v2.5 strike-of-CONDITIONAL was the WRONG direction. The v2.20 canonical state SUPERSEDES the v2.5 conformance pass for D-3 specifically. Revert appendix language rewritten: "Reverting v2.20 would restore the v2.5 3-tier `AttributeTier` state (without `CONDITIONAL`/`CONDITIONALLY_REQUIRED`) — i.e., the wrong-direction plan-conforms-to-spec resolution that v2.20 supersedes per OD spec v1.16 §1.2 + Tension 004 §7.6." | OD spec v1.16 §C-OD-04 §4.2 + §4.3 canonical-reading amendment + helper update at `otel_genai_base.py:58-86` + 25/25 helper tests pass |

**Plan shape preserved.** v2.19's 55-unit axis-led structure preserved verbatim. No new units; no DAG topology change; no cluster reorganization; no coverage matrix structural delta (U-OD-04 still covers C-OD-04 §4.1-§4.5; AC text changes do not affect contract coverage); no cross-axis edge addition; AC count at U-OD-04 unchanged at 8 ACs (#2 + #3 text amended; #1 + #4 + #5 + #6 + #7 + #8 PRESERVED VERBATIM).

**Coverage matrix delta.** None at structural level. U-OD-04's `Implements` line preserved: `[C-OD-04 §4.1, §4.2, §4.3, §4.4, §4.5]`. The §4.2 + §4.3 cardinality amendments are canonical-reading changes to those contracts, not contract-coverage changes. AC #2 + AC #3 text now cites OD spec v1.16 §C-OD-04 §4.2 + §4.3 (use-latest-version body-citation-alignment per `Project_Workflow_v1_8.md` §7.4); other spec citations at U-OD-04 (§4.1 cite at v1.12; §4.4 + §4.5 at v1.2-lineage) preserved per delta-only-spec convention.

**Dependency graph delta.** None. U-OD-04 `Depends on: []` (foundational L0 unit) preserved verbatim. No new edges; no removed edges. Within-axis DAG acyclic; topological sort unchanged. 8 direct dependents preserved: U-OD-05 / U-OD-06 / U-OD-07 / U-OD-08 / U-OD-11 / U-OD-18 / U-OD-21 / U-OD-23. The §4.3 BASE_LAYER_ATTRIBUTES list consumed by these dependents is PRESERVED VERBATIM at v2.20 per D-3b preservation framing (tier-assignment for existing 17 attributes against new 4-tier table is deferred per OD spec v1.16 §1.3 + §"Adjacent observations" (e)).

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **Tension 004 D-2/D-3/D-4 carry-forwards from v2.19 — UPDATED at v2.20.** v2.19 §"Adjacent observations" (b) claimed "D-2/D-3/D-4 plan-layer resolutions remain operative" — that claim is SUPERSEDED at v2.20 for D-2 + D-3 (per re-litigation against OTel 1.41.0 archived text); the claim remains operative for D-4 only (verified MATCH this session). The v2.20 amendment closes D-2 + D-3 as re-litigated-and-resolved-at-spec-v1.16 + plan-v2.20.

(b) **U-OD-04 AC #4 `gen_ai.provider.name` Required-tier preservation vs production attribute-name divergence.** Carry from v2.19 §"Adjacent observations" (a). Preserved verbatim at v2.20. NOT patched per FM-2.

(c) **Test docstring drift at impl arc — verified at v2.20.** The renamed tests at `harness-od/tests/test_otel_genai_base.py` (this session) carry v1.16-citing docstrings; NEW tests cite OD spec v1.16 §1.1 + §1.2 directly; carrier-conform to canonical paper-trail. NO drift.

(d) **`Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` §7.1 D-2 + D-3 row staleness post-v2.20.** v2.20 supersedes the §7.1 D-2 + D-3 "RESOLVED at OD plan v2.5 plan-conforms-to-spec" framing. Co-publication owed at apply-pass arc: append NEW §7.6 reflecting the re-litigation per OD spec v1.16 §3 + this v2.20 amendment.

(e) **`harness-od/src/harness_od/harness_breaker_schema.py:21` docstring drift surfaced at production grep.** Docstring claims "AttributeTier enum (which has no `REQUIRED` / `CONDITIONAL` members)" — at v2.20 the enum has `REQUIRED_STABLE` (always had) AND `CONDITIONALLY_REQUIRED` (NEW). The "no `REQUIRED`" claim was always loose (REQUIRED_STABLE counts); the "no `CONDITIONAL`" claim is stale post-v1.16. NOT patched per FM-2 + fork doc §4.2 (γ) single-focus scope. Surfaced for follow-on doc-hygiene arc.

(f) **§C-OD-04 §4.3 per-attribute tier-assignment audit against new 4-tier table.** NEW carry at v2.20 (per OD spec v1.16 §"Adjacent observations" (e)). BASE_LAYER_ATTRIBUTES 17 attributes preserved at their v1.2-lineage tier assignments (3 Required + 6 Recommended + 8 Opt-In); none currently assigned to NEW `CONDITIONALLY_REQUIRED` tier. Future WebFetch audit owed against OTel 1.41.0 archived text per-attribute requirement levels.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v2.20 (delta-only change-note for U-OD-04 absorption; v2.5 authoring site preserved verbatim per delta-only-plan-file convention; v2.19 D-1 absorption preserved verbatim outside D-2 + D-3 amendments) |
| Trigger | OD spec v1.15 → v1.16 §C-OD-04 §4.2 + §4.3 canonical-reading amendment (`Spec_Operational_Discipline_v1_16.md` co-published this session); `.harness/class_1_fork_tension_004_d2_d3_otel_141_relitigation.md` §4.1 operator-ratified 2026-05-26 option (A) full conformance + §4.2 option (γ) single-focus |
| Supersedes | Tension 004 (2026-05-15) D-2 + D-3 readings at plan layer (plan v2.5's 7-value enum + 3-tier conformance both SUPERSEDED for the cardinality dimensions; D-3 specifically reverses the v2.5 plan-strike-of-CONDITIONAL); v2.5 §3.2.1 rollback boundary appendix language re v2.1 divergent state (struck in full at v2.20 per change-note (g)) |
| Scope of revision | NARROW: U-OD-04 only; Inputs cite + Signatures block (2 enums) + AC #2 + AC #3 + Tests-line entries (2 renames + 3 NEW test names) + Rollback boundary v2.5 appendix |
| Units revised | U-OD-04 (1 unit) |
| Units preserved verbatim | U-OD-00, U-OD-01-U-OD-03, U-OD-05-U-OD-54 (54 units) |
| Coverage matrix delta | None at structural level — U-OD-04 still covers C-OD-04 §4.1-§4.5 |
| Dependency graph delta | None — U-OD-04 `Depends on: []` preserved; 8 dependents preserved |
| AC count change | None — U-OD-04 retains 8 ACs (#2 + #3 text amended; #1 + #4 + #5 + #6 + #7 + #8 preserved verbatim) |
| Test name change | 2 renames + 3 NEW: `test_genai_operation_cardinality_seven` → `_nine`; `test_attribute_tier_cardinality_three` → `_four`; NEW `test_genai_operation_includes_invoke_workflow` + `test_genai_operation_includes_retrieval` + `test_attribute_tier_conditionally_required_present`. All landed at impl arc this session (25/25 helper tests pass; 27/27 runtime LLM dispatch tests pass — no production regression on `GenAiOperation` caller backward compatibility). |
| Cross-axis edge delta | None |
| Cross-file absorption owed at follow-on arcs | Workspace `CLAUDE.md` §2.3 OD spec row bump (this session); Tension 004 doc NEW §7.6 (this session); v2.20 adjacent finding (e) doc-hygiene (`harness_breaker_schema.py:21` docstring); v2.20 adjacent finding (f) per-attribute tier-assignment audit (future arc) |
| Adjacent findings surfaced | 6 (per "Adjacent observations" section; (a) updates v2.19 (b); (b) carries v2.19 (a); (c)+(d)+(e)+(f) NEW); NOT patched per FM-2 |
| Authority anchor | OD spec v1.16 §C-OD-04 §4.2 + §4.3 canonical-reading amendment + ADR-D6 v1.2 §1.2 [HIGH] cite of OTel GenAI semantic conventions 1.41.0 archived text + WebFetch verification 2026-05-26 |
| Predecessor | v2.19 (D-1 span-name format Class 1 fork absorption; preserved verbatim outside U-OD-04 D-2 + D-3 amendments at v2.20) |
| Successor | v2.21 (next operator-discretion arc; candidates: attribute-name `gen_ai.system` vs `gen_ai.provider.name` divergence per v2.19 (a) + v2.20 (b); §C-OD-04 §4.4 audit against OTel 1.41.0 archived text per fork doc §5(d) + OD spec v1.16 §"Adjacent observations" (f); per-attribute tier-assignment audit against new 4-tier table per v2.20 (f)) |

---

## Audit checklist (per implementation-planner skill §4 + §5 step 9)

| Check | Status |
|---|---|
| Atomicity — single coherent change at single unit (U-OD-04) | ✓ |
| Spec-traceability — citation to OD spec v1.16 §C-OD-04 §4.2 + §4.3 by ID + section + version | ✓ |
| Dependency-awareness — no new edges; existing graph preserved acyclic | ✓ |
| Implementation-grade-detail — files affected (`otel_genai_base.py:58-86`) + signatures (GenAiOperation 9-member StrEnum + AttributeTier 4-member StrEnum) + testable acceptance (AC #2 + #3 cardinality + new test names) | ✓ |
| No-extension — only authorized fix applied (D-2 + D-3 cardinality refresh per operator-ratified fork doc §4.1 (A) + §4.2 (γ)); D-3b tier-assignment + D-4 base metric + §4.1 span-name format preserved verbatim | ✓ |
| Preservation — 54 units preserved verbatim; v2.19 D-1 absorption preserved verbatim | ✓ |
| Use-latest-version body-citation-alignment per §7.4 — U-OD-04's §C-OD-04 §4.2 + §4.3 citations bumped to v1.16 | ✓ |
| Coverage matrix completeness — every contract row marked; every unit column marked (preserved from v2.19) | ✓ |
| Acyclic invariant — DAG topological sort exists (preserved from v2.19) | ✓ |
| Coherence pass — all sub-disciplines satisfied at U-OD-04 + immediate dependency-graph neighbors (no neighbor amendments owed; D-3b BASE_LAYER_ATTRIBUTES list preserved verbatim per OD spec v1.16 §1.3 — 8 dependents continue consuming v1.2-lineage tier assignments unchanged) | ✓ |
| Tests-pass verification at apply-pass arc — 25/25 harness-od helper tests pass + 27/27 harness-runtime LLM dispatch tests pass at HEAD; pyright strict deferred to commit-time verification | ✓ |
