# Class 1 fork — GenAI span-name four-way drift across AS spec / OD spec / OD helper / production

**Filed:** 2026-05-26 (AS-8 follow-on discriminator audit per checkpoint `20260526-175836-as-4-retired-as-8-partial-advance.md` §"Remaining Work" item 1)
**Status:** OPEN — awaiting operator routing decision
**Class:** 1 (halt-execution semantics — design-phase artifact requires revision; production span-name does not match any spec; cited external authority contradicts the OD-spec canonical reading from Tension 004)
**Predecessor:** Tension 004 (`Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md`, 2026-05-15) — this fork re-opens that resolution against the actual 1.41.0 text
**Adjacent:** `.harness/class_3_drift_c_od_04_gen_ai_binding_site_silence.md` (2026-05-25) — line 34 silently absorbed the divergence

---

## §1 Detection state

| Field | Value |
|---|---|
| Detection arc | AS-8 follow-on discriminator audit (this session) |
| Detection mode | Grep + external-authority verification per `[[verification-shape-sharpened-grep-vs-e2e]]` discipline |
| Halt point | No code execution — surfaced from documentation/contract layer |
| HEAD at filing | `0a3f234` (main, post AS-4 + AS-8 anthropic.* merges) |

## §2 Defect — five distinct span-name shapes in play

| # | Source | Shape | Status |
|---|---|---|---|
| S1 | OTel GenAI semconv **1.41.0** specifically (verified 2026-05-26 via archived spec at `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md`) | `{gen_ai.operation.name} {gen_ai.request.model}` — **2-token space** | External authority anchor cited at ADR-D6 v1.2 §1.2 [HIGH] |
| S2 | OD spec `Spec_Operational_Discipline_v1_11.md` §C-OD-04 §4.1 (canonical reading per Tension 004 ratification 2026-05-15) | `{gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}` — **3-token space** | Spec-canonical at HEAD; diverges from S1 |
| S3 | OD impl `harness-od/src/harness_od/otel_genai_base.py:104` `SPAN_NAME_FORMAT` + `span_name()` helper | matches S2 (3-token space) | **Dead code** — zero production callers (verified grep at filing) |
| S4 | AS spec `Spec_Action_Surface_v1.md` §14.1 row 1129 (parent-span anchor cite for `anthropic.*`) | literal string `llm.inference` | Spec-canonical at HEAD; never emitted at runtime |
| S5 | Production `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:324` | `f"gen_ai.{provider_name}.{operation}"` — **dot-joined 2-token** | Live in production; matches none of S1/S2/S3/S4 |

### §2.1 Test-side evidence

13 tests at `harness-runtime/tests/test_lifecycle_llm_dispatch.py` + 7 tests at `harness-runtime/tests/test_lifecycle_cost_attribution_llm_dispatch.py` exercise S5 (dot-joined production form) and pass. Test fixtures encode S5 as the authoritative span-name shape — tests have followed production into the divergence.

### §2.2 Docstring + cross-axis cite drift on S4 (parent-span anchor)

Sites citing parent span as `llm.inference` (literal string) — independent of which shape S1–S3 / S5 resolves to:

| Site | Form |
|---|---|
| `harness-cp/src/harness_cp/routing_namespace.py:6,10,47,51` | docstrings + `inherited_from` field |
| `harness-cp/src/harness_cp/cp_namespace_export_manifest.py:48` | docstring |
| `harness-cp/src/harness_cp/multi_agent_span_hierarchy.py:84` | data structure literal `"llm.inference[]"` |
| `harness-cp/src/harness_cp/workflow_driver.py:178` | docstring |
| `harness-od/src/harness_od/cp_source_namespace_verification.py:14` | docstring |
| `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:285` | docstring (in C-RT-15 surface) |
| `harness-runtime/src/harness_runtime/lifecycle/memory_tool_dispatch.py:108,112` | docstring |
| `harness-as/src/harness_as/anthropic_primitive_sampling.py:40` | data structure key |
| `harness-as/src/harness_as/anthropic_attribute_namespaces.py:109,110,291` | constants + docstrings (`_ANTHROPIC_SPAN = "llm.inference"`) |
| `harness-cp/tests/test_routing_namespace.py:6,35,37` | test assertions on `inherited_from` |

11 production source files + 1 test file. 8 of these use the literal string `"llm.inference"` as a data value (not just a docstring reference); a docstring-only patch is insufficient.

### §2.3 Why Class 1 (not Class 3)

Per `Project_Workflow_v1_8.md` §2.7.6:

- **S5 production form matches NO spec.** This is a contract violation, not informational drift. Per X-AL-3 (no silent H_T design extension at Phase 7), production cannot canonically emit a span shape that exists in no design-phase artifact.
- **S2 spec cite is empirically wrong against its named external authority.** OD spec C-OD-04 §4.1 cites OTel GenAI semconv 1.41.0 as canonical; verification this session against the archived 1.41.0 text shows the 3-token form is not present at that version. Tension 004 (2026-05-15) ratified S2 without verifying against the cited version — re-litigation is required.
- **S4 parent-anchor cite is unfaithful to production.** A reader following AS spec §14.1 to find `anthropic.*` attributes on a parent named `llm.inference` finds nothing — the span is named per S5. Citation byte-exactness per `Project_Workflow_v1_8.md` §7.4.2 invariant I-1 is violated.

Three convergent Class 1 triggers. The existing Class 3 filing at `class_3_drift_c_od_04_gen_ai_binding_site_silence.md` understated this — its §1.3 "binding choice is architecturally unambiguous" claim is empirically false against the actual external authority text.

---

## §3 Four readings (operator decision required)

### §3.1 R1 — Production rename to spec form

**Defect surface:** S5 → conform to whichever shape becomes spec-canonical (post-R2).
**Scope:** ~2 commits — `llm_dispatch.py:324` span-name construction + 13 + 7 test fixture updates + cross-axis emission tests at `harness-as/tests/test_anthropic_attribute_namespaces.py` (verify `_ANTHROPIC_SPAN` literal alignment).
**Authority:** Production must match spec per X-AL-3 + I-1.
**Discriminator:** R1's rename target depends on R2's outcome — these are sequential, not independent.

### §3.2 R2 — OD spec correction (re-open Tension 004 reading)

**Defect surface:** S2 → 2-token per actual 1.41.0 text; S3 helper updated to match; Tension 004 (2026-05-15) ratification superseded.
**Scope:** ~4-6 commits — OD spec v1.11 → v1.12 §C-OD-04 §4.1 amendment + helper + 1 test file (`test_otel_genai_base.py:81-90`) + OD plan v2.18 → v2.19 U-OD-04 absorption + workspace `CLAUDE.md` row + meta-finding about Tension 004 incorrect-reading.
**Authority:** ADR-D6 v1.2 §1.2 cites "OTel GenAI semconv 1.41.0 [HIGH] as cross-vendor floor". External authority preempts internal canonical reading when the internal reading contradicts the cited version (per `Project_Workflow_v1_8.md` §7.4 fidelity-grammar).
**Tiebreaker check owed:** is there a 1.41.0 errata document or an ADR-D6 v1.3 re-anchor? Spec-writer apply-pass needs to verify.

### §3.3 R3 — AS spec parent-anchor cite (independent of R1/R2)

**Defect surface:** S4 → either (a) rename literal `llm.inference` to whatever S5/S1/S2 resolves to, OR (b) introduce a canonical "LLM inference parent span" alias term distinct from the runtime span-name, decoupling spec parent-anchor citations from runtime span-name resolution.
**Scope (option a):** ~3-4 commits — AS spec §14.1 + 11 source files + 1 test file + cross-axis tests verifying alignment. Mass rename across 8 data-value sites.
**Scope (option b):** ~5-7 commits — Introduce alias term at ADR-D6 or AS spec §14.1; refactor 11 source sites to cite alias not literal; co-resolve with R1/R2 outcome. Higher authoring cost; lower future maintenance cost when external semconv evolves.
**Authority:** AS spec §14.1 row 1129 is at C-AS-14 §14.1 declaration site — co-resolved with whichever shape becomes runtime-canonical post-R1.
**Discriminator:** This is the deferred reading from checkpoint framing. Independent of R1/R2 — option (b) lets R3 land without touching production span-name at all, but requires architectural decision on parent-anchor vs span-name disambiguation.

### §3.4 R4 — Existing class_3 filing STRIKE (concurrent doc hygiene)

**Defect surface:** `class_3_drift_c_od_04_gen_ai_binding_site_silence.md` line 34 false claim STRUCK.
**Scope:** ~1 commit — single-line patch + change-note appended documenting the 2026-05-26 discriminator audit superseding the 2026-05-25 absorption.
**Authority:** Co-resolved with whichever of R1/R2 lands; if neither lands at this arc, the filing's framing remains operative but with explicit acknowledgement of the discriminator gap.

---

## §4 Recommended routing

### §4.1 Recommended order (operator confirms)

1. **R2 first** (external-authority-driven; smallest blast radius). OD spec v1.11 → v1.12 amends §C-OD-04 §4.1 to 2-token per actual 1.41.0; OD helper at `otel_genai_base.py:104` becomes 2-token; one test file updates. Meta-finding logged about Tension 004 (2026-05-15) ratification being against an incorrect reading of the cited version. ~4-6 commits.
2. **R1 second** (follows R2). `llm_dispatch.py:324` rename to 2-token form per R2 outcome; runtime tests update; binding-site silence drift at class_3 filing absorbed via R2 spec amendment per the existing filing's own §2.1 recommendation. ~2 commits.
3. **R3 third** (independent doc hygiene). Operator chooses option (a) literal rename or (b) alias-term abstraction. ~3-7 commits depending on option.
4. **R4 concurrent** with whichever lands first.

### §4.2 Architect mode-3 recommendation owed

Per `systems-architect` skill §4A (Phase-7 architectural-tension resolution mode): a full authority-chain recommendation tracing OD spec C-OD-04 → ADR-D6 §1.2 → OTel GenAI semconv 1.41.0 archived text → Tension 004 ratification arc, with explicit recommendation on R3 option (a) vs (b), is owed before R1/R2/R3 apply-passes open. The architect mode-3 recommendation is **not** authored at this filing (per fork-writing discipline — the filer surfaces; the architect deliberates; the operator decides).

---

## §5 Adjacent observations (not patched)

(a) **Tension 004 was wrong at ratification, not at authoring.** The Tension 004 doc §4 recommended "tiebreaker check the operator should make: confirm OTel GenAI semconv 1.41.0 itself (the cited external standard) matches the spec §4.x reading — the spec cites 1.41.0 as a [HIGH] external anchor; if the actual 1.41.0 convention differs from §4.x, that is a separate spec defect." The tiebreaker check was not performed in 2026-05-15. This is a process finding, not a contract defect — fold into operational learnings.

(b) **OD `span_name()` helper as dead code is a soft signal.** Helpers authored speculatively for a contract that production never wires through are a leading indicator of contract-vs-production drift. Future spec amendments authoring helper APIs should be followed by an integration test ensuring at least one production caller exists, OR the helper should be marked deferred until a caller lands.

(c) **Test fixtures encoding the drift.** 13+7 tests at `test_lifecycle_llm_dispatch.py` + `test_lifecycle_cost_attribution_llm_dispatch.py` pass against S5 (dot-joined). Tests followed production into the divergence rather than catching it. Pattern catalogued: when production diverges from spec, test fixtures encode the divergence and become the deciding evidence — but only for grep-vs-e2e verification, not for spec conformance.

(d) **`Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` status field.** Currently labeled "OPEN — awaiting operator resolution decision". Empirically it was resolved at OD spec v1.2/v1.3 absorbing the 3-token reading + landing the helper. The status field is stale by ~12 months; not patched at this filing per FM-2.

---

## §6 Filing footer

| Field | Value |
|---|---|
| Class | 1 (halt-execution semantics on contract-vs-production divergence + external-authority contradiction) |
| Filed | 2026-05-26 |
| HEAD | `0a3f234` |
| Routing target | OD spec v1.11 → v1.12 (R2) + AS spec v1.6 → v1.7 (R3) + production rename (R1) + class_3 filing STRIKE (R4) |
| Blocks | NOT a hard block on AS-8 RETIRED close (AS-8's RETIRED gate is on Skills/Files/managed_agents producer-site authoring per per-namespace breakdown filing, not on span-name shape). Surfaces a Class 1 contract violation that should resolve before further AS-axis or OD-axis spec revisions touch C-OD-04 or C-AS-14 §14.1. |
| Predecessor | Tension 004 (2026-05-15); class_3_drift_c_od_04 (2026-05-25) |
| Adjacent | `[[verification-shape-sharpened-grep-vs-e2e]]` (5th application; first cross-spec-vs-external-authority application); `[[advisor-before-substantive-work-for-cross-axis-blockers]]` (11th application; advisor caught three-readings-not-two framing + helper-dead-code verification + 1.41.0 archived-spec fetch as load-bearing) |
