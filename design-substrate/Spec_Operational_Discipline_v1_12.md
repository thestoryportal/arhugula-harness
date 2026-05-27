# Specification — Operational Discipline v1.12

## Change-note (v1.11 → v1.12)

**Scope of revision.** GenAI span-name format Class 1 fork resolution apply pass per `.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.1 (operator-ratified 2026-05-26). NEW §C-OD-04 §4.1 canonical-reading amendment superseding the v1.2-lineage 3-token form preserved verbatim through v1.11. The v1.12 amendment conforms §4.1 byte-exact to the **actual OTel GenAI semantic conventions 1.41.0 text** cited at ADR-D6 v1.2 §1.2 [HIGH] as the cross-vendor floor. Re-litigates `Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` (2026-05-15) ratification — that ratification absorbed the v1.2 3-token reading without performing the §4 tiebreaker check against the actual 1.41.0 archived text. The fork performed the check (WebFetch 2026-05-26 of `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md`); the check failed; Tension 004 ratification is superseded.

**Narrow-scope framing (explicit).** The arc lands ONLY the §4.1 span-name format amendment. §4.2 operations enum (Tension 004 D-2: plan-vs-spec 6-vs-7 divergence) and §4.3 attribute tiers (Tension 004 D-3: 4-vs-3 divergence) are PRESERVED VERBATIM at v1.12 — those divergences are out-of-scope per FM-2 no-extension discipline. Separate apply-pass arcs owed at operator discretion.

---

## §C-OD-04 §4.1 Span name format — canonical-reading amendment (v1.12 NEW)

### Authority chain

- ADR-D6 v1.2 §1.2 (`design-substrate/ADR-D6_v1_2.md` lines 51 + 53) cites *"OTel GenAI semconv 1.41.0 [HIGH] as the cross-vendor floor"* and declares the base-layer block *"Preserved verbatim from v1.1 §1.2 base-layer block"*. The cited authority anchor IS the external standard at the cited version.
- The external standard at the cited version (OTel GenAI semantic conventions 1.41.0, archived spec `gen-ai/gen-ai-spans.md`) specifies verbatim: *"Span name SHOULD be `{gen_ai.operation.name} {gen_ai.request.model}`."*
- Per `CLAUDE.md` invariant I-1 (citation byte-exact) + `Project_Workflow_v1_8.md` §7.4.2 fidelity grammar: when a spec citation claims to reproduce external content but does not, the external content is canonical and the citation is in error.

### Amendment text

The v1.2 §4.1 declaration at `design-substrate/Spec_Operational_Discipline_v1_2.md` lines 279–285 reads:

```
{gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}
```

Per OTel GenAI semconv 1.41.0 [HIGH] canonical span name format.

**v1.12 canonical-reading amendment.** The v1.2-lineage 3-token form is SUPERSEDED. The canonical §4.1 span name format at v1.12 is:

```
{gen_ai.operation.name} {gen_ai.request.model}
```

Per OTel GenAI semantic conventions 1.41.0 [HIGH] canonical span name format — byte-exact to the cited authority at the cited version (`github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md`).

The `gen_ai.provider.name` component is REMOVED from the span name format. `gen_ai.provider.name` remains canonical as a Required (Stable) tier attribute at §4.3 (PRESERVED VERBATIM at v1.12 per narrow-scope framing) — it is carried as a span attribute, NOT as a span-name component. The 3-token form was a misreading of the cited 1.41.0 text at v1.2 authoring; the misreading was preserved verbatim through v1.10/v1.11 per delta-only convention; v1.12 corrects the misreading at the canonical-reading layer without rewriting the v1.2 file (delta-only-spec-file preservation discipline).

### Tension 004 supersedence

`Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` (filed 2026-05-15) §4 step 3 named the required tiebreaker check verbatim:

> Tiebreaker check the operator should make: confirm ADR-D6 has no revision later than v1.2 that re-anchors the base layer, and confirm OTel GenAI semconv 1.41.0 itself (the cited external standard) matches the spec §4.x reading — the spec cites 1.41.0 as a [HIGH] external anchor; if the actual 1.41.0 convention differs from §4.x, that is a separate spec defect.

The tiebreaker check was deferred-not-performed at the 2026-05-15 ratification arc. The v1.12 apply-pass arc performed the check (WebFetch 2026-05-26 — see `class_1_fork_genai_span_name_four_way_drift.md` §7.6 verification result + §7.5a S6 lineage finding). The actual 1.41.0 convention specifies 2-token. The §4.x reading at v1.2 differs from the actual 1.41.0 convention. Per Tension 004 §4 step 3's own framing, **this is a separate spec defect** — which v1.12 corrects.

Tension 004 ratification of the 3-token reading is hereby SUPERSEDED at v1.12. The supersedence is non-retroactive: artifacts authored against the v1.2-v1.11 3-token reading (OD impl helper at `harness-od/src/harness_od/otel_genai_base.py:104`, test at `harness-od/tests/test_otel_genai_base.py:81-90`, OD plan v2.18 U-OD-04, runtime spec v1.x line 2033 deferral suggestion, production at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:324`) require downstream conformance to the v1.12 reading at follow-on apply-pass arcs (R1 production rename + R3 AS spec parent-anchor + R4 class_3 filing STRIKE per fork doc §7.5).

---

## Sections preserved verbatim at v1.12

Per FM-2 no-extension discipline, the v1.12 amendment touches ONLY §4.1 span-name format. The following sections are PRESERVED VERBATIM from their authoring versions through v1.12:

- §C-OD-04 §4.2 operations enum (v1.2 — 7-value `{chat, text_completion, embeddings, generate_content, create_agent, invoke_agent, execute_tool}`)
- §C-OD-04 §4.3 attribute tiers (v1.2 — 3-tier Required (Stable) / Recommended (Development) / Opt-In content)
- §C-OD-04 §4.4 hierarchy correlation (v1.2)
- §C-OD-04 §4.5 base metric (v1.2 — `gen_ai.client.operation.duration` histogram)
- §C-OD-05 through §C-OD-33 (all v1.2-v1.11 lineage content preserved per delta-only-spec-file convention)
- All v1.3 through v1.11 substantive amendments (preserved per delta-only-spec-file convention; each version file is the change-note for that version's delta only)

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **§C-OD-04 §4.2 operations enum cardinality.** Tension 004 §2 D-2 surfaced a plan-vs-spec divergence at the operations enum (plan U-OD-04 had 6 values omitting `generate_content`; spec C-OD-04 §4.2 has 7). The divergence persists at v1.12; this v1.12 amendment does NOT touch §4.2. If the plan-side fix has landed (operator should confirm via OD plan v2.18 U-OD-04 inspection), the spec-vs-plan divergence resolves; if not, it remains an OPEN Class 1 carry from Tension 004. Owed at a separate apply-pass arc per FM-2.

(b) **§C-OD-04 §4.3 attribute tiers cardinality.** Tension 004 §2 D-3 surfaced a plan-vs-spec divergence at attribute tiers (plan U-OD-04 had 4 tiers including a `CONDITIONAL` member; spec C-OD-04 §4.3 has 3 tiers — Required (Stable) / Recommended (Development) / Opt-In content). The divergence persists at v1.12; this v1.12 amendment does NOT touch §4.3. Owed at a separate apply-pass arc per FM-2.

(c) **§C-OD-04 §4.5 base metric cite-shape.** Tension 004 §2 D-4 surfaced a plan-vs-spec divergence at base metric (plan U-OD-04 had `gen_ai.client.token.usage`; spec C-OD-04 §4.5 has `gen_ai.client.operation.duration` histogram). The divergence persists at v1.12; this v1.12 amendment does NOT touch §4.5. Owed at a separate apply-pass arc per FM-2.

(d) **`Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` status field.** Currently labeled *"OPEN — awaiting operator resolution decision"*. Empirically the v1.2/v1.3 absorption arc resolved the 2026-05-15 reading (against the unverified citation per (a)–(c) above); the status field has been stale by ~12 months. The v1.12 amendment supersedes the 2026-05-15 reading of D-1 span-name format only — (a)/(b)/(c) above remain unsuperseded. The status-field update is OPERATOR DISCRETION; not patched at this arc per FM-2.

(e) **Runtime spec v1.x line 2033 deferral suggestion.** Per fork doc §7.5a — runtime spec contains an informal deferral-section suggestion `gen_ai.{provider}.{model_or_method}` that production followed. This is the lineage of production divergence. Runtime spec amendment owed at the R1 apply-pass arc (separate scope per fork §7.4.2).

(f) **OD spec C-OD-04 §4.3 `gen_ai.provider.name` Required-tier attribute.** Per v1.12 amendment text — `gen_ai.provider.name` is REMOVED from the span-name format but PRESERVED at §4.3 as a Required (Stable) tier attribute. Cross-axis seam: production at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:330` currently emits `gen_ai.system` (NOT `gen_ai.provider.name`) as the provider attribute. The attribute-name divergence (`gen_ai.system` vs `gen_ai.provider.name`) is a SEPARATE spec defect surfaced this arc — not patched per FM-2; owed at a separate apply-pass arc.

---

## Downstream artifacts requiring absorption at follow-on arcs

Cross-file back-references (per spec-writer skill §5) — flagged for downstream absorption; NOT touched at this v1.12 spec arc:

| Artifact | Required change | Owner |
|---|---|---|
| `harness-od/src/harness_od/otel_genai_base.py:104` | `SPAN_NAME_FORMAT` constant + `span_name()` signature drops `provider` parameter — conforms to v1.12 §4.1 2-token form | Direct impl edit (R2 follow-on, this session apply-pass arc) |
| `harness-od/tests/test_otel_genai_base.py:81-90` | Assertions update to 2-token form | Direct test edit (R2 follow-on, this session apply-pass arc) |
| `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:324` | `span_name = f"{operation} {model}"` per v1.12 §4.1 (provider preserved at `gen_ai.system` attribute set at line 330) | R1 apply-pass arc (separate, follow-on) |
| `harness-runtime/tests/test_lifecycle_llm_dispatch.py` + `test_lifecycle_cost_attribution_llm_dispatch.py` (20 tests) | Fixtures update to expect 2-token form | R1 apply-pass arc (separate, follow-on) |
| `design-substrate/Spec_Harness_Runtime_v1.md` line 2033 | Deferral suggestion removal OR cross-reference to OD §4.1 v1.12 | R1 apply-pass arc — see fork §7.5a |
| OD plan v2.18 → v2.19 `Implementation_Plan_Operational_Discipline_v2_19.md` | U-OD-04 absorption (1-AC text update + 2-token assertion test name) | `implementation-planner` revision-pass (sequenced after v1.12 spec lands) |
| AS spec v1.6 + 11 source-file docstring sites | `llm.inference` literal → alias-term abstraction | R3 apply-pass arc (separate, follow-on per fork §7.4.3 option (b)) |
| `.harness/class_3_drift_c_od_04_gen_ai_binding_site_silence.md` line 34 | STRIKE false claim `"per C-OD-04 §4.1"` (production form was per runtime spec line 2033 deferral suggestion, NOT per OD §4.1 which was 3-token; v1.12 corrects §4.1 and class_3 filing's claim becomes superseded) | R4 concurrent with this v1.12 arc (this session) |
| Workspace `CLAUDE.md` §2.3 OD spec row | v1.11 → v1.12 row update | This session apply-pass arc |

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.12 (canonical-reading amendment to v1.2 §C-OD-04 §4.1; v1.2 file PRESERVED VERBATIM per delta-only-spec-file convention) |
| Trigger | `.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.1 (operator-ratified 2026-05-26 option (A) full acceptance) |
| Supersedes | `Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` D-1 reading (2026-05-15); 3-token form preserved at v1.2-v1.11 |
| Scope of revision | NARROW: §C-OD-04 §4.1 span-name format ONLY |
| Sections revised | §C-OD-04 §4.1 (canonical-reading amendment — 3-token → 2-token byte-exact to OTel 1.41.0 archived text) |
| Sections preserved verbatim | §C-OD-04 §4.2 / §4.3 / §4.4 / §4.5; §C-OD-05..§C-OD-33; all v1.3-v1.11 substantive amendments |
| Adjacent findings surfaced | 6 (per "Adjacent observations" section above); NOT patched per FM-2 |
| Cross-file absorption owed | 8 artifacts (per "Downstream artifacts" table above) |
| Authority anchor | ADR-D6 v1.2 §1.2 [HIGH] cite of OTel GenAI semantic conventions 1.41.0; verified byte-exact 2026-05-26 against archived spec at `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md` |
| Predecessor | v1.11 (Pause/resume back-flow arc — preserved verbatim outside §4.1) |
| Successor | v1.13 (next operator-discretion arc — likely Tension 004 D-2/D-3/D-4 absorption per (a)/(b)/(c) findings; or R3 cross-axis if AS spec §14.1 alias-term lands first) |
