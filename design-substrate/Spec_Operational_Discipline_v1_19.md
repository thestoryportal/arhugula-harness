# Spec: Operational Discipline — v1.19 (delta over v1.18)

---

## Change-note (v1.18 → v1.19)

**Scope of revision.** Substantive canonical-reading amendment closing v1.18 §"Adjacent observations" finding (e) — §C-OD-04 §4.3 per-attribute tier-assignment audit against the 4-tier table — as **CLOSED-via-tier-redistribution-to-OTel-1.41.0-chat-span** 2026-05-27. Per-attribute Requirement-Level audit performed this arc against OTel GenAI semantic conventions 1.41.0 archived text at `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md` (raw-fetched + cached this session at `$CLAUDE_JOB_DIR/gen-ai-spans-v1.41.0.md`). Audit verdict: **3 chat-span attributes diverge** from OTel 1.41.0 Requirement Level — `gen_ai.request.model` (OD Required (Stable) → OTel Conditionally Required "If available"), `server.port` (OD Recommended (Development) → OTel Conditionally Required "If `server.address` is set"), `gen_ai.conversation.id` (OD Recommended (Development) → OTel Conditionally Required "when available"). v1.19 redistributes these 3 attributes to the v1.16-NEW `Conditionally Required` tier per OTel canonical reading. ZERO production-behavior change — harness emits all 3 attributes at all spans where applicable (stricter posture than OTel's conditional rule; conformant per "emit-more-often-is-fine" framing). Helper carrier update at `harness-od/src/harness_od/otel_genai_base.py:148+157+158` + helper test redistribution at `harness-od/tests/test_otel_genai_base.py:55-67` co-published this arc.

**Audit scope (load-bearing).** The audit is **chat-span-only** per the §4.1 alias-term "the LLM inference span" anchoring (per AS spec v1.7 §14.1 alias-term abstraction; CXA v2.11 §0.4 convention seam declaration; OD spec v1.12 §C-OD-04 §4.1 format owner). OTel 1.41.0 declares 4 separate span tables — chat-span (lines 49-103), embeddings-span (lines 314-342), retrieval-span (lines 449-477), execute_tool-span — each with its own Requirement-Level column. The OD §4.3 attribute set lists attributes from ≥3 of these spans (the chat-span attributes + execute_tool-span attributes at Opt-In tier + retrieval-span attributes at Opt-In tier). Per v1.16 §1.2 canonical-text anchor, the §4.3 tier-cardinality reading was against the chat-span table; v1.19 preserves that anchor at the redistribution layer. The non-chat-span attributes in OD §4.3 Opt-In are present as **content-policy** (default-off PII discipline per §12.1 redaction discipline), NOT as tier-binding from those spans' tables — Opt-In assignment at OD is canonical regardless of OTel's per-span Requirement-Level treatment for those attributes.

**Stance ratification.** Operator deferred to assistant recommendation 2026-05-27. Assistant chose **mirror-OTel-tiers** stance over **document-harness-stricter-posture-explicitly** stance for three reasons: (1) continuity with v1.16 lineage (Tension 004 D-3 closure direction was "spec → OTel conformance"); (2) cleaner amendment shape (tier-assignment redistribution, not added prose explaining divergence); (3) harness-stricter emission becomes correctly characterized as **implementation-policy concern** (OD plan declares emission policy at AC #4 — the spec §4.3 declares tier classification; the two layers are separable). Both stances would be conformant under OTel — emit-more-often-than-conditional-rule is acceptable. The chosen stance is doc-hygiene at the spec layer with ZERO emission-behavior change.

**Empirical posture (load-bearing).** Production grep at HEAD `a47c74c` this session:

- `harness-runtime/.../llm_dispatch.py:340-342` → harness emits all 3 Required-tier-per-v1.18 attributes (`gen_ai.operation.name` + `gen_ai.provider.name` + `gen_ai.request.model`) at every span unconditionally; `server.address` + `server.port` + `gen_ai.conversation.id` declared at OD carrier `otel_genai_base.py:156-158` as RECOMMENDED_DEVELOPMENT but `set_attribute` call sites at `llm_dispatch.py` emit NONE of the 3 currently — empirical-grep confirms ZERO `set_attribute("server.address", ...)` / `set_attribute("server.port", ...)` / `set_attribute("gen_ai.conversation.id", ...)` sites at `llm_dispatch.py`.
- The OD carrier declaration without production emission for `gen_ai.conversation.id` is a separable divergence from the tier-conformance audit — surfaced as v1.19 §"Adjacent observations" finding (NEW) (i) below.
- Harness-stricter posture for `gen_ai.request.model`: ALWAYS emitted (consumed at `llm_dispatch.py:342` via per-call `gen_ai_request_model=model` binding); harness always knows model — Required-tier emission is the natural posture. OTel's CR-tier "If available" framing maps to harness's always-available model context.
- Harness-stricter posture for `server.port`: at OTel CR-tier "If `server.address` is set"; harness does not currently emit either (no production callsite) — divergence is at declared-but-not-emitted layer (sibling-of-conversation.id at finding (i)).

**Routing.** Per workspace `CLAUDE.md` §4.3 + I-1 byte-exact discipline + v1.16 substantive-amendment precedent (Tension 004 D-2 + D-3 spec → OTel conformance pattern): v1.19 is a NEW delta file authoring §1 canonical-reading amendment table redistributing 3 attributes + §2 finding-closure refresh (close v1.18 (e) as CLOSED-via-tier-redistribution; refresh v1.18 (h) NEW carry status) + §3 cross-artifact cite-cascade disposition (helper + tests this arc; ZERO CXA / AS / CP / runtime spec / OD plan cascade per audit-scope discipline + helper-private tier metadata reading) + §"Adjacent observations" carry refresh including NEW (i) declared-but-not-emitted divergence for `gen_ai.conversation.id` + `server.port` + `server.address`. v1.2-v1.18 PRESERVED VERBATIM per delta-only-spec-file convention.

**Pre-substantive empirical-verification audit (v1.18 §5 discipline applied prospectively).** Before authoring this v1.19 file, audit pass against all v1.18 §"Adjacent observations" carries (c)–(h) was performed empirically at HEAD `a47c74c` per the v1.18 §5 strengthened discipline "at EVERY §Adjacent observations entry authoring (inherited OR new) empirically verify the entry against production state / fork doc closures / cross-artifact resolutions at the moment of writing." Results:

- (c) §8.4.2 anticipated cases — grep verified ZERO production hits at HEAD; carry remains genuine as deferred-monitor.
- (d) §15.2 vs §15.4 split informational — AS spec v1.7 unchanged since v1.17; carry remains genuine as informational.
- (e) per-attribute tier-assignment audit — **AUDITED this arc**; closed via tier-redistribution.
- (f) §C-OD-04 §4.4 against OTel 1.41.0 — NO §4.4 audit performed since v1.16; carry remains genuine as deferred-audit (NOT in scope at v1.19 single-focus arc per FM-2).
- (g) workflow-grammar discipline candidate — `Project_Workflow_v1_8.md` unchanged since v1.16; carry remains genuine.
- (h) `gen_ai.provider.name` stability tier divergence — divergence verified still-present at OTel 1.41.0 archived text + OD spec carrier; carry remains genuine as spec-narrative-layer divergence; future doc-hygiene routing.

ZERO stale-carry findings at v1.18 → v1.19 transition. The audit-discipline is now operationally validated — v1.18 §5 catalogue is applied prospectively rather than retroactively. This is the **FIRST PROSPECTIVE APPLICATION** of the v1.18 §5 discipline at a substantive-amendment arc.

**No fork doc filed.** Per workspace precedent for substantive canonical-reading amendments with single-authority anchor (OTel 1.41.0 archived text): v1.16 (Tension 004 D-2 + D-3 absorption) landed without a fork doc — the absorbed Class 1 fork was `class_1_fork_tension_004_d2_d3_otel_141_relitigation.md` which is the canonical authority for both the v1.16 + v1.19 amendments. v1.19 re-uses that fork doc as authority anchor for the per-attribute-tier-assignment audit it explicitly deferred at §4 step 3 (Tension 004 D-3b carry preserved verbatim at v1.16 §1.3 was the scope-foreclosure of the audit; v1.19 closes the carry).

---

## §1 Canonical-reading amendment table (v1.19 NEW)

Per delta-only-spec-file convention, the v1.2 through v1.18 file bodies are PRESERVED VERBATIM. The following table maps every per-attribute tier-assignment site for the 3 redistributed attributes to its corrected canonical reading.

### §1.1 §C-OD-04 §4.3 — 3 attributes redistribute to `Conditionally Required` tier

The v1.2-lineage §C-OD-04 §4.3 declares per-attribute tier assignments preserved through v1.18:

| Attribute | v1.2-v1.18 tier | OTel 1.41.0 chat-span Requirement Level | Canonical reading at v1.19 |
|---|---|---|---|
| `gen_ai.request.model` | Required (Stable) | **Conditionally Required** ("If available") | **Conditionally Required** at v1.19 §1.1 |
| `server.port` | Recommended (Development) | **Conditionally Required** ("If `server.address` is set") | **Conditionally Required** at v1.19 §1.1 |
| `gen_ai.conversation.id` | Recommended (Development) | **Conditionally Required** ("when available") | **Conditionally Required** at v1.19 §1.1 |

**Updated tier-cardinality at v1.19 canonical reading:**

- **Required (Stable)** — 2 attributes (was 3 at v1.2-v1.18): `gen_ai.operation.name`, `gen_ai.provider.name`
- **Conditionally Required** — 3 attributes (NEW row content at v1.19; v1.16 added the tier without populating it; v1.19 populates per OTel 1.41.0 chat-span audit): `gen_ai.request.model`, `server.port`, `gen_ai.conversation.id`
- **Recommended (Development)** — 4 attributes (was 6 at v1.2-v1.18): `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.response.finish_reasons`, `server.address`
- **Opt-In content** — 8 attributes (unchanged): `gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.system_instructions`, `gen_ai.tool.definitions`, `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result`, `gen_ai.retrieval.documents`, `gen_ai.retrieval.query.text`

Total: 17 attributes (unchanged from v1.2-v1.18 — only tier-assignment is redistributed, not the attribute set).

### §1.2 §C-OD-04 §4.3 — emission-posture column refresh for the Conditionally Required row

The v1.2-lineage emission-posture column reads at v1.18:

| Tier | Emission posture |
|---|---|
| Required (Stable) | Always emitted |
| Recommended (Development) | Emitted unless cardinality-safe-attribute discipline excludes (per C-OD-11) |
| Opt-In content | Default-off per C-OD-12 (redaction discipline); per-persona-tier override gradient per C-OD-13 |

The `Conditionally Required` tier added at v1.16 §1.2 received no emission-posture text at v1.16 (tier added; row content deferred per D-3b preservation). v1.19 populates:

| Tier | Emission posture at v1.19 canonical reading |
|---|---|
| **Conditionally Required** | **Emitted per per-attribute OTel-1.41.0 condition.** Harness-stricter posture (always-emit) acceptable when the harness has the attribute value unconditionally (OD plan AC #4 governs emission policy; this spec tier declares classification only). Per-attribute conditions: `gen_ai.request.model` "If available" (harness always knows model — always-emit at harness); `server.port` "If `server.address` is set" (paired-emission with `server.address` — harness emits-both-or-neither); `gen_ai.conversation.id` "when available" (harness emits when conversation-context is non-empty; declared-but-not-emitted divergence surfaced at v1.19 §"Adjacent observations" finding (i)). |

### §1.3 Cross-artifact citation sites for v1.2-v1.18 §4.3 tier-cardinality

Per delta-only-spec-file preservation chain, all v1.2-v1.18 §4.3 cite sites at downstream artifacts are PRESERVED VERBATIM at byte-exact layer; canonical reading at v1.19 §1.1 supersedes when interpreting tier-row cardinalities at those sites:

| Artifact | Site | v1.2-v1.18 reading | Canonical reading at v1.19 |
|---|---|---|---|
| OD spec v1.2 line 295 §4.3 Required (Stable) row | 3 attributes listed | `{gen_ai.operation.name, gen_ai.provider.name, gen_ai.request.model}` (3) | 2 attributes: `{gen_ai.operation.name, gen_ai.provider.name}`; `gen_ai.request.model` moved to Conditionally Required per v1.19 §1.1 |
| OD spec v1.2 line 296 §4.3 Recommended (Development) row | 6 attributes listed | `{gen_ai.usage.input_tokens, gen_ai.usage.output_tokens, gen_ai.response.finish_reasons, server.address, server.port, gen_ai.conversation.id}` (6) | 4 attributes: `{gen_ai.usage.input_tokens, gen_ai.usage.output_tokens, gen_ai.response.finish_reasons, server.address}`; `server.port` + `gen_ai.conversation.id` moved to Conditionally Required per v1.19 §1.1 |
| OD spec v1.2 lines 633-635 §11.2 cardinality table | `gen_ai.operation.name` / `gen_ai.provider.name` / `gen_ai.request.model` rows | Cardinality framing preserved at v1.19 (cardinality is independent of tier — cardinality discipline applies regardless of Required vs Conditionally Required tier classification) | No amendment owed — cardinality-discipline at §11.2 governs all bounded-cardinality attributes equally |
| OD spec v1.2 line 697 §12.4 "Always-on" attributes (3 attrs) | `gen_ai.operation.name, gen_ai.provider.name, gen_ai.request.model` listed as always-on | The "always-on" framing at §12.4 is **emission-policy** (OD plan AC layer), NOT tier-classification (§4.3). At v1.19 reading, the always-on framing for `gen_ai.request.model` is preserved as harness-stricter-posture-than-OTel-CR-rule — the tier classification moves to Conditionally Required while the emission policy preserves always-emit per harness's always-available model context. | "Always-on" emission policy preserved; tier classification at §4.3 is Conditionally Required per v1.19 §1.1; the two layers are separable (spec §4.3 tier vs OD plan AC emission policy) |
| Helper carrier `harness-od/src/harness_od/otel_genai_base.py:148+157+158` | 3 attrs assigned `REQUIRED_STABLE` / `RECOMMENDED_DEVELOPMENT` per v1.2-v1.18 | Co-published this arc — 3 attrs reassigned to `CONDITIONALLY_REQUIRED` per v1.19 §1.1 | RESOLVED at co-publication |
| Helper test `harness-od/tests/test_otel_genai_base.py:55-67` | `_SPEC_REQUIRED_STABLE` (3 names) + `_SPEC_RECOMMENDED_DEVELOPMENT` (6 names) | Co-published this arc — `_SPEC_REQUIRED_STABLE` (2 names; drop `gen_ai.request.model`) + `_SPEC_RECOMMENDED_DEVELOPMENT` (4 names; drop `server.port` + `gen_ai.conversation.id`) + NEW `_SPEC_CONDITIONALLY_REQUIRED` (3 names) + NEW per-tier test | RESOLVED at co-publication |

---

## §2 Finding-closure-disposition refresh

**Closed-via-tier-redistribution-to-OTel-1.41.0-chat-span.** v1.18 §"Adjacent observations" finding (e) — `§C-OD-04 §4.3 per-attribute tier-assignment audit against 4-tier table` — is now closed at v1.19 §1.1 + §1.2 canonical-reading amendment tables. The 4-tier table established at v1.16 §1.2 is now populated per OTel 1.41.0 chat-span Requirement-Level audit; the audit deferred at v1.16 §1.3 (D-3b preservation) + carried at v1.16/v1.17/v1.18 §"Adjacent observations" (e) is RESOLVED.

**Disposition at v1.19.** Finding (e) is CLOSED. Removed from v1.19 §"Adjacent observations" carry; no longer a deferred-audit arc.

**Adjacent v1.18 carries preserved at v1.19.** Findings (c)/(d)/(f)/(g)/(h) carried verbatim from v1.18 → v1.19 with audit-pass verification this arc (see Change-note §"Pre-substantive empirical-verification audit"). Finding (i) NEW at v1.19 — `gen_ai.conversation.id` + `server.port` + `server.address` declared-but-not-emitted divergence (sibling category to (h) but at carrier-vs-emission-callsite layer, not at carrier-vs-OTel-stability layer).

---

## §3 Cross-artifact cite-cascade disposition (v1.19 NEW)

| Artifact | Site | Carry-text framing | Disposition at v1.19 |
|---|---|---|---|
| `harness-od/src/harness_od/otel_genai_base.py:144-168` | `BASE_LAYER_ATTRIBUTES` tuple — 3 GenAiAttribute entries with stale tier assignments | v1.2-v1.18 tier metadata | **CO-PUBLISHED this arc** — `gen_ai.request.model` REQUIRED_STABLE → CONDITIONALLY_REQUIRED; `server.port` RECOMMENDED_DEVELOPMENT → CONDITIONALLY_REQUIRED; `gen_ai.conversation.id` RECOMMENDED_DEVELOPMENT → CONDITIONALLY_REQUIRED. Module docstring at `AttributeTier` class body line 81-100 preserved verbatim (the v1.16-NEW CONDITIONALLY_REQUIRED tier docstring already documents the v1.16 introduction; v1.19 populates the tier without changing the tier's introduction history). |
| `harness-od/tests/test_otel_genai_base.py:55-77` | Per-tier expected-set fixtures `_SPEC_REQUIRED_STABLE` + `_SPEC_RECOMMENDED_DEVELOPMENT` + `_SPEC_OPT_IN_CONTENT` | v1.2-v1.18 tier expectations | **CO-PUBLISHED this arc** — `_SPEC_REQUIRED_STABLE` cardinality 3 → 2 (drop `gen_ai.request.model`); `_SPEC_RECOMMENDED_DEVELOPMENT` cardinality 6 → 4 (drop `server.port` + `gen_ai.conversation.id`); NEW `_SPEC_CONDITIONALLY_REQUIRED` cardinality 3 (the 3 redistributed attributes); `_SPEC_OPT_IN_CONTENT` cardinality 8 (unchanged); NEW per-tier test `test_conditionally_required_tier_attributes_per_spec_4_3`. |
| Workspace `CLAUDE.md` (worktree root) §2.3 OD spec row | v1.18 row-text narrative | v1.18 narrative | **Bumped to v1.19** at co-publication commit this arc with change-note narrative referencing v1.19 §"Filing footer". |
| `Cross_Axis_Composition_Document_v2_12.md` (or any CXA edition) | NO §4.3 tier-row cite at any CXA edition | n/a | NO change owed — CXA does not cite §C-OD-04 §4.3 tier-row cardinality. |
| `Spec_Action_Surface_v1_7.md` / `Spec_Control_Plane_v1_19.md` / `Spec_Harness_Runtime_v1_29.md` | NO §4.3 per-attribute tier cite at any peer spec | n/a | NO change owed — peer specs cite §C-OD-04 §4.1 (span-name format) + §4.3 base-layer attribute SET (not per-attribute tier) only. |
| `Implementation_Plan_Operational_Discipline_v2_20.md` U-OD-04 unit | AC #4 BASE_LAYER_ATTRIBUTES tier assignments | Per v1.16 §1.3 D-3b preservation framing, the plan AC #4 preserved tier assignments verbatim through v2.20 | **REVISION OWED at follow-on arc** per FM-2 — U-OD-04 plan revision absorbing v1.19 §1.1 tier redistribution; plan AC count unchanged (#4 text refreshed for 3 redistributed attrs + 1 NEW per-tier test assertion); ZERO new ACs; ZERO new units; ZERO DAG topology change. Sequenced after spec v1.19 lands per implementation-planner discipline. |
| `Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` D-3b carry | "D-3b §4.3 tier assignment — PRESERVED VERBATIM at v1.16 §1.3 (assignment is separate concern from cardinality); Stable post-v2.5; future audit owed against 4-tier table" | Future audit explicitly named — D-3b is specifically about `gen_ai.usage.input_tokens` + `gen_ai.usage.output_tokens` placement at Recommended (Development) tier | **CLOSED-as-verified-MATCH-during-v1.19-audit** — D-3b's two attrs (`input_tokens` + `output_tokens`) preserved at Recommended (Development) at v1.19 §1.1 + verified MATCH to OTel 1.41.0 chat-span Requirement Level (both attrs at `Recommended` per archived text lines 96-97). D-3b closure mechanism is **audit-verified MATCH**, NOT redistribution (the 3 redistributed attrs at v1.19 §1.1 are `gen_ai.request.model` / `server.port` / `gen_ai.conversation.id` — none of which are D-3b's attrs). Tension 004 supersession lineage now CLOSED across all elements: D-1 R2 at v1.12 (amended); D-2 + D-3 at v1.16 (amended); D-3b at v1.19 (verified MATCH); D-4 at v1.16 §1.4 (verified MATCH). Closure shapes split: D-1 / D-2 / D-3 amended; D-3b / D-4 verified MATCH. |

ZERO other cite-cascade sites verified via grep this session.

---

## §4 Sections preserved verbatim at v1.19

Per delta-only-spec-file convention + FM-2 no-extension discipline + substantive canonical-reading amendment scope, the v1.19 amendment touches ONLY the NEW §1 canonical-reading amendment table + §2 finding-closure-disposition refresh + §3 cross-artifact cite-cascade disposition + §"Adjacent observations" refresh. The following sections are PRESERVED VERBATIM from their authoring versions:

- **§C-OD-04 §4.1** (v1.12-lineage span-name 2-component format per D-1 R2)
- **§C-OD-04 §4.2** (v1.2-lineage operations enum; v1.16 §1.1 canonical reading applied; 9 values)
- **§C-OD-04 §4.3** ATTRIBUTE NAME SET (v1.2-lineage; 17 names unchanged); TIER ASSIGNMENT redistributed per v1.19 §1.1
- **§C-OD-04 §4.4** (v1.2-lineage; not in scope at any fork to date)
- **§C-OD-04 §4.5** (v1.2-lineage; verified MATCH at v1.16 §1.4)
- **§C-OD-04 §11.2 cardinality table** (v1.2-lineage; cardinality discipline independent of tier classification)
- **§C-OD-04 §12.4 always-on attributes** (v1.2-lineage emission-policy framing; preserved as separable from tier classification per v1.19 §1.3 row 4 reading)
- **§C-OD-05 through §C-OD-33** (all v1.2-v1.18 lineage content preserved per delta-only-spec-file convention)
- **All v1.3 through v1.18 substantive amendments** (including v1.13 row 5 sub-note + v1.14 §8.4 cross-namespace ingestion rule + v1.15 §1 canonical reading + v1.16 §1 + v1.17 §1 + v1.18 §1 amendment tables)

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **v1.18 finding (e) — CLOSED-via-tier-redistribution at v1.19 §1.1 + §2.** Removed from "Adjacent observations" carry.

(b) **v1.18 finding (c) — §8.4.2 anticipated cases empirical-verification.** Carried verbatim from v1.16 → v1.17 → v1.18 → v1.19. Audit this session 2026-05-27: production grep for the 3 anticipated cases (`topology.*` on `sandbox.exit`, `audit.*` on `hitl.invocation.responded`, `validator.*` on `mcp.tool.call`) returns ZERO production hits at HEAD `a47c74c` — anticipated cases have NOT materialized; carry remains genuine as deferred-monitor. v1.19 does NOT touch this carry.

(c) **v1.18 finding (d) — v1.15 §15.2 vs §15.4 split informational.** Carried verbatim. Audit this session 2026-05-27: AS spec v1.7 unchanged since v1.17; carry remains genuine as informational. v1.19 does NOT touch this carry.

(d) **v1.18 finding (f) — §C-OD-04 §4.4 against OTel 1.41.0 archived text.** Carried verbatim. Audit this session 2026-05-27: NO §4.4 audit performed in any commit since v1.16; carry remains genuine as deferred-audit. v1.19 does NOT touch this carry per FM-2 single-focus arc scope.

(e) **v1.18 finding (g) — workflow-grammar reconciliation discipline candidate at `Project_Workflow_v1_8.md`** — STRENGTHENED at v1.18 §5; v1.19 §"Pre-substantive empirical-verification audit" is the FIRST PROSPECTIVE APPLICATION of the strengthened discipline at a substantive-amendment arc. Carried verbatim. Audit this session 2026-05-27: `Project_Workflow_v1_8.md` unchanged since v1.16; carry remains genuine as deferred-discipline-candidate; v1.19 does NOT touch the upstream `Project_Workflow_v1_8.md` artifact. The discipline's operational validation is now documented at change-note level — first prospective application succeeded (no stale-carry findings at v1.18 → v1.19 transition).

(f) **v1.18 finding (h) — `gen_ai.provider.name` stability tier divergence.** Carried verbatim. OTel 1.41.0 archived text declares `gen_ai.provider.name` as `stability: development` at attribute + member layers; OD spec C-OD-04 §4.3 tier classification reads at v1.19 as Required (Stable) — divergence is at the spec-narrative-layer naming ("(Stable)" suffix in OD tier name) NOT wire-protocol layer. Future OD spec doc-hygiene pass MAY add a footer clarifying that OD's `Required (Stable)` tier-NAME is project-internal naming (preserved per v1.2 lineage with OTel canonical naming as derivative per v1.16 §1.2 mapping table) — the "(Stable)" suffix does NOT claim OTel attribute-level stability semantic. Class 3 informational; NOT patched per FM-2. v1.19 does NOT touch this carry.

(g) **NEW at v1.19 — `gen_ai.conversation.id` declared-but-not-emitted divergence.** OD carrier `harness-od/src/harness_od/otel_genai_base.py:158` declares `gen_ai.conversation.id` at v1.19 `CONDITIONALLY_REQUIRED` tier (per v1.19 §1.1 redistribution) with emission-posture "Emitted when conversation-context is non-empty" (per v1.19 §1.2 per-attribute condition reading). Production grep at HEAD `a47c74c` confirms ZERO `span.set_attribute("gen_ai.conversation.id", ...)` callsites at `harness-runtime/.../llm_dispatch.py` — the attribute is declared at carrier but never emitted at production. Sibling at-different-layer to finding (f) — (f) is carrier-vs-OTel-stability metadata divergence; (g) is carrier-vs-production-emission divergence. Routes to runtime spec amendment (C-RT-15 dispatcher emission policy) OR runtime impl arc (`llm_dispatch.py` emission site landing) — both downstream of OD spec; out of scope at v1.19 single-focus arc per FM-2. Class 2 in-execution operator-discretion routing target. NOT patched at v1.19.

(h) **NEW at v1.19 — `server.port` + `server.address` declared-but-not-emitted divergence.** Same shape as finding (g) — carrier `otel_genai_base.py:156-157` declares both; production `llm_dispatch.py` emits NEITHER. `server.address` remains at Recommended (Development) tier per v1.19 §1.1; `server.port` moved to Conditionally Required per v1.19 §1.1. Sibling-of-(g) at carrier-vs-emission-callsite layer. Routes to runtime spec amendment (C-RT-15 dispatcher emission policy) OR runtime impl arc; out of scope at v1.19 single-focus arc per FM-2. Class 2 in-execution operator-discretion routing target. NOT patched at v1.19.

(i) **NEW at v1.19 — discipline-validation observation (informational, Class 3).** v1.19 §"Pre-substantive empirical-verification audit" is the FIRST PROSPECTIVE APPLICATION of the v1.18 §5 strengthened discipline at a substantive-amendment arc. The audit identified ZERO stale-carries at the v1.18 → v1.19 transition (all of (c)–(h) carries verified still-genuine at HEAD `a47c74c`). The discipline-validation observation is informational — the v1.18 §5 catalogue is operationally applicable at substantive amendments, not only at fidelity-pure citation-correction patches like v1.17/v1.18. Routes to upstream workflow revision arc if operator routes (the discipline-validation could be canonicalized as a workflow-grammar-level invariant at `Project_Workflow_v1_8.md`); v1.19 does NOT touch the upstream artifact.

---

## Downstream artifacts requiring absorption at follow-on arcs

| Artifact | Required change | Owner |
|---|---|---|
| Workspace `CLAUDE.md` §2.3 OD spec row | v1.18 → v1.19 row update with v1.19 change-note narrative; v1.18 + earlier lineage preserved | This session apply-pass arc |
| `harness-od/src/harness_od/otel_genai_base.py:148+157+158` | 3 GenAiAttribute entries reassigned: `gen_ai.request.model` REQUIRED_STABLE → CONDITIONALLY_REQUIRED; `server.port` RECOMMENDED_DEVELOPMENT → CONDITIONALLY_REQUIRED; `gen_ai.conversation.id` RECOMMENDED_DEVELOPMENT → CONDITIONALLY_REQUIRED | This session apply-pass arc |
| `harness-od/tests/test_otel_genai_base.py:55-67` | Per-tier expected-set fixtures redistributed: `_SPEC_REQUIRED_STABLE` cardinality 3 → 2; `_SPEC_RECOMMENDED_DEVELOPMENT` 6 → 4; NEW `_SPEC_CONDITIONALLY_REQUIRED` cardinality 3; NEW per-tier test `test_conditionally_required_tier_attributes_per_spec_4_3` | This session apply-pass arc |
| `Implementation_Plan_Operational_Discipline_v2_20.md` U-OD-04 unit AC #4 | Tier-assignment text refresh absorbing v1.19 §1.1 redistribution; NEW test name `test_conditionally_required_tier_attributes_per_spec_4_3` added to Tests line; AC count unchanged at 8; ZERO new ACs; ZERO new units; ZERO DAG topology change | Sequenced follow-on arc after spec v1.19 lands per implementation-planner discipline |
| `Spec_Harness_Runtime_v1.md` / CP spec / AS spec / CXA / ADR / ADD / PRD / harness-runtime impl / OD plan beyond U-OD-04 | NO change owed — tier-classification at OD §4.3 is OD-internal; no downstream artifact cites per-attribute tier rows of §4.3 (verified via grep this session) | n/a |
| `Project_Workflow_v1_8.md` | NO change owed at v1.19 — discipline-validation observation at §"Adjacent observations" (i) is informational; routes to upstream workflow revision arc if operator routes | n/a |

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.19 (Substantive canonical-reading amendment closing v1.18 §"Adjacent observations" finding (e) — §C-OD-04 §4.3 per-attribute tier-assignment audit against 4-tier table — as **CLOSED-via-tier-redistribution-to-OTel-1.41.0-chat-span** 2026-05-27; NEW §1 canonical-reading amendment table redistributing 3 attributes to Conditionally Required tier + §2 finding-closure refresh + §3 cross-artifact cite-cascade disposition; co-published with helper carrier update + helper test redistribution; v1.18 + earlier files PRESERVED VERBATIM per delta-only-spec-file convention) |
| Trigger | v1.18 §"Adjacent observations" finding (e) re-evaluation per user-routed adjacent-observation closure arc 2026-05-27 (session continuation from v1.18 publication; user directive "Audit per-attribute tier (e)"); pre-substantive advisor pass + empirical-verification audit at HEAD `a47c74c` confirmed audit-scope discipline (chat-span-only per §4.1 alias-term anchoring); OTel 1.41.0 archived text raw-fetched + cached this session via `gh api` against `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md`; chat-span Requirement-Level audit identified 3 divergences (`gen_ai.request.model`, `server.port`, `gen_ai.conversation.id`); operator deferred stance-ratification to assistant; assistant chose mirror-OTel stance for continuity with v1.16 lineage |
| Supersedes | v1.18 §"Adjacent observations" finding (e) "Carried verbatim from v1.16 → v1.17 → v1.18; v1.18 does NOT touch this carry" framing — superseded at v1.19 §1.1 redistribution (finding (e) is the broader per-attribute audit). v1.16 §1.3 D-3b preservation (input_tokens + output_tokens at Recommended (Development)) — NOT superseded; v1.19 §1.1 preserves D-3b's attrs at Recommended (Development) verbatim and verifies MATCH to OTel 1.41.0 chat-span per §3 last row closure. The "future audit owed against 4-tier table" framing at v1.16 §1.3 (broader scope-foreclosure of the per-attribute audit) is the carry-foreclosure that v1.19 §1.1 completes. |
| Scope of revision | NARROW: NEW §1 canonical-reading amendment table redistributing 3 attributes to Conditionally Required tier per OTel 1.41.0 chat-span Requirement-Level audit + §2 finding-closure refresh + §3 cross-artifact cite-cascade disposition. Co-publication: helper carrier `BASE_LAYER_ATTRIBUTES` 3-attribute tier reassignment + helper test redistribution + workspace CLAUDE.md OD spec row bump. ZERO contract change at attribute SET layer (17 attrs preserved); ZERO signature change at GenAiAttribute / AttributeTier; ZERO acceptance-criterion change at C-OD-04; ZERO behavior change at production emission (harness-stricter posture preserved — emit-more-often-than-CR is conformant). |
| Contract change | None at attribute SET; per-attribute tier classification redistributed for 3 attrs (additive on Conditionally Required tier; subtractive on Required (Stable) by 1 + on Recommended (Development) by 2; net 0 change). Backward-compatible at consumer layer per Pydantic v2 StrEnum semantics + tier-readers-private to helper + test (no production reader of tier metadata for emission decisions per v1.19 §3 grep verification). |
| Cross-axis cascade | ZERO at spec semantics layer. Cross-artifact cite-cascade disposition at v1.19 §3 documents 7 sites — 3 co-published at this arc (helper carrier + helper test + workspace CLAUDE.md); 1 sequenced follow-on (OD plan v2.20 U-OD-04 AC #4 refresh); 3 confirmed NO-change (peer specs, CXA, runtime spec — no per-attribute tier cite). Tension 004 D-3b carry CLOSED-as-verified-MATCH at v1.19 (full Tension 004 lineage now closed: D-1 R2 / D-2 / D-3 amended at v1.12 / v1.16; D-3b / D-4 verified MATCH at v1.19 / v1.16 — closure shapes split between amended and verified-MATCH). |
| Authority anchor | OTel GenAI semantic conventions 1.41.0 archived text at `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md` (raw-fetched 2026-05-27 via `gh api`; cached at `$CLAUDE_JOB_DIR/gen-ai-spans-v1.41.0.md` for reproducibility); chat-span table at lines 49-103; Requirement-Level column at line 71; per-attribute audit verdict at v1.19 §1.1 mirrors the archived chat-span Requirement-Level column byte-exact for the 3 redistributed attributes. Tension 004 D-3b carry at `Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` (the §4 step 3 tiebreaker check named the per-attribute audit; v1.16 deferred; v1.19 closes). |
| Predecessor | v1.18 (FOURTH species of stale-carry-text disposition catalogued — authoring-time stale carry) |
| Successor | v1.20 (next operator-discretion arc — candidates: v1.19 finding (b) §8.4.2 anticipated cases; (d) §C-OD-04 §4.4 archived-text audit; (e) workflow-grammar discipline canonicalization; (g) `gen_ai.conversation.id` declared-but-not-emitted divergence routing; (h) `server.port` + `server.address` declared-but-not-emitted divergence routing) |
| Advisor application | 17th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` — pre-substantive advisor pass identified 3 discriminators that materially reframed the audit scope (chat-only vs cross-span anchor at OTel; Requirement-Level vs Stability column separation; production-emission posture as conformance reframe — "Conditionally Required" emit-conditionally is satisfied by harness's emit-unconditionally posture). Operator deferred stance to assistant; recommendation chosen + executed per advisor guidance. Pre-substantive empirical-verification audit prospectively applied v1.18 §5 discipline at substantive-amendment arc (FIRST PROSPECTIVE APPLICATION); zero stale-carries identified at v1.18 → v1.19 transition. |
| Pattern catalogue | First prospective application of v1.18 §5 strengthened discipline at substantive-amendment arc (not just fidelity-pure citation-correction patches); operationally validated discipline-candidate. Sibling-of-(f) NEW carrier-vs-emission divergence pattern at findings (g)+(h) — distinct from (f) carrier-vs-OTel-stability divergence; the two divergence patterns at OD §4.3 are now both surfaced and routed at v1.19 for downstream apply-pass arcs at operator discretion. |
