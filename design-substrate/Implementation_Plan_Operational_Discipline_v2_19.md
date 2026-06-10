# Implementation Plan — Operational Discipline v2.19

## Change-note (v2.18 → v2.19)

**Scope of revision.** GenAI span-name format Class 1 fork resolution absorption per `.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.1 (R2) operator-ratified 2026-05-26 + OD spec v1.11 → v1.12 §C-OD-04 §4.1 canonical-reading amendment (`Spec_Operational_Discipline_v1_12.md` co-published this session, commit `43f6199`). Single-unit absorption at U-OD-04 (`§3.2.1` per Implementation_Plan_Operational_Discipline_v2_5.md authoring site). Re-litigates `.harness/archive/root-historical/Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` (2026-05-15) D-1 ratification — that ratification's own §4 step 3 named the tiebreaker check against actual OTel 1.41.0 text that was deferred-not-performed; this arc performed the check; the check failed; ratification superseded per its own framing.

**v2.18 substantive content preserved verbatim.** All v2.18 content (U-OD-00 through U-OD-54; clusters 1 through 4-OD-E; DAG topology; coverage matrix; cross-axis edge enumeration; all unit bodies other than U-OD-04) preserved unchanged at v2.19. The v2.18 U-OD-51 pause/resume Sub-arc absorption (5→10 ACs) preserved verbatim. The v2.17 U-OD-41 cost-axis Sub-arc B absorption preserved verbatim. The v2.16 U-OD-51 cross-axis-block lift + Sub-arc A absorption preserved verbatim. The v2.15..v2 chain all preserved.

**Source of fix.** Class 1 fork resolution apply pass — span-name format 3-token → 2-token per actual OTel GenAI semconv 1.41.0 archived text. Companion artifacts at this session: OD spec v1.12 (NEW §C-OD-04 §4.1 canonical-reading amendment); R2 follow-on at `harness-od/src/harness_od/otel_genai_base.py:104` (SPAN_NAME_FORMAT + `span_name()` signature drops `provider` parameter) + `harness-od/tests/test_otel_genai_base.py:79-92` (test rename + 2-token assertion); R4 STRIKE at `.harness/class_3_drift_c_od_04_gen_ai_binding_site_silence.md`; workspace `CLAUDE.md` §2.3 OD spec row v1.11 → v1.12 (all landed at commit `5221264`).

**Narrow-scope framing (carried from spec).** §4.1 span-name format ONLY. The §4.2 operations enum (Tension 004 D-2: 6-vs-7 divergence), §4.3 attribute tiers (Tension 004 D-3: 4-vs-3 divergence), §4.5 base metric (Tension 004 D-4: `gen_ai.client.token.usage` vs `gen_ai.client.operation.duration` divergence) are ALL PRESERVED VERBATIM at v2.19 per FM-2 no-extension discipline + spec v1.12 narrow-scope framing. Separate apply-pass arcs owed at operator discretion.

**Amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **U-OD-04 plan body** (authored at `Implementation_Plan_Operational_Discipline_v2_5.md` §3.2.1, preserved verbatim through v2.6/.../v2.18) | (a) **Inputs** line: `OD spec v1.2 §4.1 span name format (`{gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}` — 3-component)` → `OD spec v1.12 §C-OD-04 §4.1 span name format (`{gen_ai.operation.name} {gen_ai.request.model}` — 2-component per actual OTel GenAI semconv 1.41.0 archived text; v1.2-lineage 3-component reading SUPERSEDED at v1.12)`; (b) **Signatures** block line `SPAN_NAME_FORMAT` v2.5 verbatim block: 3-component constant string → 2-component constant string + comment update `// §4.1 verbatim — 3-component span name format` → `// §4.1 verbatim — 2-component span name format per v1.12 canonical-reading amendment`; (c) **AC #1**: `\`SPAN_NAME_FORMAT\` matches §4.1 verbatim — the 3-component format \`{gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}\`.` → `\`SPAN_NAME_FORMAT\` matches §4.1 verbatim — the 2-component format \`{gen_ai.operation.name} {gen_ai.request.model}\` per OD spec v1.12 §C-OD-04 §4.1 canonical-reading amendment. \`gen_ai.provider.name\` is REMOVED from span-name format but PRESERVED at §4.3 Required (Stable) tier attribute per AC #4.`; (d) **AC #4 Required (Stable) tier list**: PRESERVED VERBATIM — `gen_ai.provider.name` remains a Required (Stable) attribute at AC #4 list (3 attributes total: `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`) per spec §4.3 PRESERVED VERBATIM at v1.12; (e) **Tests** line: `test_span_name_format_byte_exact_three_component` → `test_span_name_format_byte_exact_two_component` (renamed); all other test names preserved verbatim including `test_span_name_resolves_at_span_emission_time` (signature of `span_name()` carrier-conforms to v1.12 2-arg shape at impl arc `5221264`); (f) **Rollback boundary v2.5 revert appendix** STRUCK in part: `Reverting v2.5 restores the v2.1 divergent state (2-component span name; 6-operation enum; 4-tier AttributeTier; gen_ai.client.token.usage base metric) — i.e., the Tension 004 verbatim-divergence defect` SUPERSEDED — at v2.19 the 2-component span-name form IS canonical per v1.12; only the 6-operation enum + 4-tier `AttributeTier` + `gen_ai.client.token.usage` base metric remain Tension 004 carry-forward defects. Revert appendix rewritten to reflect post-v2.19 canonical state. | OD spec v1.12 §C-OD-04 §4.1 canonical-reading amendment + R2 follow-on landings at commit `5221264` |

**Plan shape preserved.** v2.18's 55-unit axis-led structure preserved verbatim. No new units; no DAG topology change; no cluster reorganization; no coverage matrix structural delta (U-OD-04 still covers C-OD-04 §4.1–§4.5; AC text changes do not affect contract coverage); no cross-axis edge addition; no AC count change at any unit (U-OD-04 retains 8 ACs; #1 + #4 text amended; #2/#3/#5/#6/#7/#8 PRESERVED VERBATIM).

**Coverage matrix delta.** None at structural level. U-OD-04's `Implements` line preserved: `[C-OD-04 §4.1, §4.2, §4.3, §4.4, §4.5]` — the §4.1 amendment is a canonical-reading change to that contract, not a contract-coverage change. AC #1 text now cites OD spec v1.12 §C-OD-04 §4.1 (use-latest-version body-citation-alignment per `Project_Workflow_v1_8.md` §7.4); all other spec citations at U-OD-04 (§4.2/§4.3/§4.4/§4.5) preserved at v1.2-lineage authoring (per delta-only-spec convention — v1.12 amendment is §4.1 only; §4.2-§4.5 substantive content still lives at v1.2 file).

**Dependency graph delta.** None. U-OD-04 `Depends on: []` (foundational L0 unit) preserved verbatim. No new edges; no removed edges. Within-axis DAG acyclic; topological sort unchanged. 8 direct dependents preserved: U-OD-05 / U-OD-06 / U-OD-07 / U-OD-08 / U-OD-11 / U-OD-18 / U-OD-21 / U-OD-23 (per v2.5 rollback boundary enumeration, preserved verbatim).

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **U-OD-04 acceptance criterion #4 `gen_ai.provider.name` Required-tier preservation vs production attribute-name divergence.** AC #4 lists `gen_ai.provider.name` as a Required (Stable) tier attribute per OD spec §4.3 (preserved verbatim at v1.12). However, production at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:330` emits `gen_ai.system` (NOT `gen_ai.provider.name`) as the provider-carrying attribute. The attribute-name divergence (`gen_ai.system` vs `gen_ai.provider.name`) is a SEPARATE spec defect surfaced at v1.12 amendment §"Adjacent observations" (f); NOT patched at this v2.19 plan absorption per FM-2. Owed at separate apply-pass arc.

(b) **Tension 004 D-2/D-3/D-4 carry-forwards.** Three plan-vs-spec divergences from Tension 004 (2026-05-15) remain unresolved at U-OD-04: D-2 operations enum 6-vs-7 (plan has 7 per v2.5 conformance; check spec §4.2 — appears to match plan at 7 per spec v1.2 lines preserved through v1.12); D-3 attribute tiers 4-vs-3 (plan v2.5 conformed to 3-tier per §4.3); D-4 base metric `gen_ai.client.operation.duration` (plan v2.5 conformed). The D-2/D-3/D-4 divergences from the 2026-05-15 Tension 004 ratification were absorbed at v2.5 plan-conforms-to-spec — the divergences are RESOLVED at plan layer. The v1.12 amendment supersedes ONLY D-1 (span-name format); D-2/D-3/D-4 plan-layer resolutions remain operative.

(c) **`.harness/archive/root-historical/Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` status field staleness.** Currently labeled "OPEN — awaiting operator resolution decision". Empirically D-2/D-3/D-4 were absorbed at v2.5 (2026-05-15 era plan conformance pass); D-1 is superseded at v1.12 + v2.19 this session. The status field has been stale by ~12 months. Operator-discretion update; NOT patched at this v2.19 plan arc per FM-2.

(d) **Test docstring drift at impl arc.** The renamed test `test_span_name_format_byte_exact_two_component` at `harness-od/tests/test_otel_genai_base.py:79` (landed at commit `5221264`) has a fresh docstring authored at the rename arc citing v1.12 amendment. NO drift at impl layer. The plan v2.19's Tests-line rename is the canonical paper-trail; impl test name + docstring match.

---

## Filing footer

| Field | Value |
|---|---|
| Version | v2.19 (delta-only change-note for U-OD-04 absorption; v2.5 authoring site preserved verbatim per delta-only-plan-file convention) |
| Trigger | OD spec v1.11 → v1.12 §C-OD-04 §4.1 canonical-reading amendment (`Spec_Operational_Discipline_v1_12.md` commit `43f6199`); `.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.1 (R2) operator-ratified 2026-05-26 option (A) |
| Supersedes | Tension 004 (2026-05-15) D-1 reading at plan layer (plan v2.5's 3-component conformance superseded); v2.5 §3.2.1 rollback boundary appendix language re v1.2 divergent state |
| Scope of revision | NARROW: U-OD-04 only; Inputs cite + Signatures block + AC #1 + Tests-line entry + Rollback boundary v2.5 appendix |
| Units revised | U-OD-04 (1 unit) |
| Units preserved verbatim | U-OD-00, U-OD-01-U-OD-03, U-OD-05-U-OD-54 (54 units) |
| Coverage matrix delta | None at structural level — U-OD-04 still covers C-OD-04 §4.1-§4.5 |
| Dependency graph delta | None — U-OD-04 `Depends on: []` preserved; 8 dependents preserved |
| AC count change | None — U-OD-04 retains 8 ACs (#1 + #4 text amended; #2/#3/#5/#6/#7/#8 preserved verbatim) |
| Test name change | 1 rename: `test_span_name_format_byte_exact_three_component` → `_two_component` (carrier-conform to impl arc `5221264`) |
| Cross-axis edge delta | None |
| Cross-file absorption owed at follow-on arcs | R1 production rename at `harness-runtime/.../llm_dispatch.py:324` + runtime spec line 2033 deferral suggestion removal + 20 runtime tests (separate arc); R3 AS spec §14.1 alias-term abstraction (separate arc, fork §7.4.3 option (b)) |
| Adjacent findings surfaced | 4 (per "Adjacent observations" section); NOT patched per FM-2 |
| Authority anchor | OD spec v1.12 §C-OD-04 §4.1 canonical-reading amendment + ADR-D6 v1.2 §1.2 [HIGH] cite of OTel GenAI semantic conventions 1.41.0 archived text |
| Predecessor | v2.18 (Pause/resume Sub-arc U-OD-51 absorption; preserved verbatim outside U-OD-04 at v2.19) |
| Successor | v2.20 (next operator-discretion arc; candidates: Tension 004 D-2/D-3/D-4 status-field reconciliation; attribute-name `gen_ai.system` vs `gen_ai.provider.name` divergence absorption per adjacent finding (a)) |

---

## Audit checklist (per implementation-planner skill §4 + §5 step 9)

| Check | Status |
|---|---|
| Atomicity — single coherent change at single unit (U-OD-04) | ✓ |
| Spec-traceability — citation to OD spec v1.12 §C-OD-04 §4.1 by ID + section + version | ✓ |
| Dependency-awareness — no new edges; existing graph preserved acyclic | ✓ |
| Implementation-grade-detail — files affected (`otel_genai_base.py:104`) + signature (`SPAN_NAME_FORMAT` + `span_name(op, model)`) + testable acceptance (AC #1 byte-exact assertion + test name match) | ✓ |
| No-extension — only authorized fix applied (AC #1 text + Tests-line rename + Signatures block + Inputs cite); D-2/D-3/D-4 carry-forwards preserved verbatim | ✓ |
| Preservation — 54 units preserved verbatim; v2.18 substantive content unchanged | ✓ |
| Use-latest-version body-citation-alignment per §7.4 — U-OD-04's §C-OD-04 §4.1 citation bumped to v1.12 | ✓ |
| Coverage matrix completeness — every contract row marked; every unit column marked (preserved from v2.18) | ✓ |
| Acyclic invariant — DAG topological sort exists (preserved from v2.18) | ✓ |
| Coherence pass — all sub-disciplines satisfied at U-OD-04 + immediate dependency-graph neighbors (no neighbor amendments owed; U-OD-04 is L0 foundational with 8 dependents that consume the §4.3 BASE_LAYER_ATTRIBUTES list — preserved verbatim at v2.19, no rippling change) | ✓ |
