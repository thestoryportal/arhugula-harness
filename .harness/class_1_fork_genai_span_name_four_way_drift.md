# Class 1 fork — GenAI span-name four-way drift across AS spec / OD spec / OD helper / production

**Filed:** 2026-05-26 (AS-8 follow-on discriminator audit per checkpoint `20260526-175836-as-4-retired-as-8-partial-advance.md` §"Remaining Work" item 1)
**Status:** ✅ FULLY-APPLIED 2026-05-26 (status-line refreshed 2026-05-27) — R1/R2/R3 all ratified-and-applied per §7.4.1/§7.4.2/§7.4.3 across AS spec v1.7 (alias-term `the LLM inference span` abstraction at §14.1) + OD spec v1.12 (§C-OD-04 §4.1 3-token → 2-token byte-exact to OTel 1.41.0) + runtime spec v1.27 (§14.5 deferral STRIKE) + 12-site production refactor at `llm_dispatch.py:324` + helper carrier + test alias-aware assertion; findings (f)/(g)/(h) RESOLVED at body §8/§9/§10. Species 3 stale-carry per workflow v1.9 §7.4.7.2.

_Original filing footer:_ **Status:** OPEN — awaiting operator routing decision
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

---

## §7 Systems-architect Mode-3 recommendation (appended 2026-05-26)

*Per `systems-architect` skill §4A.3 — resolution recommendation appended; operator decides.*

### §7.1 Precise tension statement (verbatim per artifact)

**ADR-D6 v1.2 §1.2** (`design-substrate/ADR-D6_v1_2.md` line 51 + 53):

> The unified ingestion contract assembles cleanly across the five upstream span-schema commitments via additive namespace separation, with OTel GenAI semantic conventions 1.41.0 [HIGH] as the cross-vendor floor.
>
> **Base layer — OTel GenAI semconv 1.41.0 [HIGH].** [Preserved verbatim from v1.1 §1.2 base-layer block.]

ADR-D6 makes a **cite, not an authoring**. The shape is owned by the external standard at the cited version; ADR-D6's commitment is *to that external standard at that version*.

**OD spec v1.2 §4.1** (`design-substrate/Spec_Operational_Discipline_v1_2.md` lines 279–285, preserved verbatim through v1.11):

> ### §4.1 Span name format
>
> ```
> {gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}
> ```
>
> Per OTel GenAI semconv 1.41.0 [HIGH] canonical span name format.

OD spec **claims** its 3-token form is "Per OTel GenAI semconv 1.41.0". The claim is empirically false against the archived 1.41.0 text (verified via WebFetch this session at `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md`):

> Span name SHOULD be `{gen_ai.operation.name} {gen_ai.request.model}`.

**2-token, not 3-token.** No `gen_ai.provider.name` component.

**AS spec v1.6 §14.1 row 1129** (`design-substrate/Spec_Action_Surface_v1.md`):

> | `anthropic.*` | 10 | `llm.inference` | ADR-D3 v1.2 §1.8.1 anthropic namespace block |

`llm.inference` is a literal-string parent-anchor cite. The same literal string appears at 8 production data-value sites (per fork §2.2) and 11 docstring sites. **No span named `llm.inference` is ever emitted at runtime.**

**Production `llm_dispatch.py:324`**:

```python
span_name = f"gen_ai.{provider_name}.{operation}"
```

Dot-joined 2-token form. Matches no design-phase artifact.

### §7.2 Per-artifact authority-chain placement

Per `CLAUDE.md` §1.3 chain: **ADR (F1–F5 + D1–D6) → ADD v1.3 → PRD v1.1 → per-axis spec v1.x → per-axis plan v2.x + CXA v2.1**.

| Artifact | Chain position | Authority over span-name shape |
|---|---|---|
| OTel semconv 1.41.0 archived text | **External anchor** cited by ADR-D6 at [HIGH] | Highest — ADR-D6 made the cite, not an authoring |
| ADR-D6 v1.2 §1.2 | F5-derivative (D6 cites F5 substrate commitment) | Defers to external anchor by construction |
| OD spec C-OD-04 §4.1 | Per-axis spec, derives from ADR-D6 | Canonical for spec-layer; subject to chain ancestor |
| AS spec §14.1 row 1129 | Per-axis spec, declares parent-anchor convention for `anthropic.*` | Independent of OD §4.1 — different architectural surface (parent-anchor citation vs span-name format) |
| Production `llm_dispatch.py:324` | Phase-7 implementation | Must conform to spec |

**Critical authority-chain reading:** when an artifact makes a *cite* to an external authority, the canonical reading at that chain position is determined by the external authority's actual content, NOT by the spec's internal rendering of what the external authority says. ADR-D6 §1.2 cites 1.41.0 [HIGH] as the floor — the floor IS what 1.41.0 actually specifies. OD spec C-OD-04 §4.1's 3-token rendering is **a misreading of the cited authority**, not an authoring of an alternative shape.

This is structurally identical to the §2.4 citation-byte-exact discipline (`Project_Workflow_v1_8.md` §7.4.2 invariant I-1): when a citation claims to reproduce external content but does not, the external content is canonical and the citation is in error.

### §7.3 §2 discipline analysis

**Five-axis decomposition.**

| Axis | Concern |
|---|---|
| Action surface (AS) | Parent-anchor convention for `anthropic.*` / `mcp.*` / `memory.*` attribute namespaces (S4). Different architectural surface from span-name format — anchors what attributes hang on, not the name itself. |
| Operational discipline (OD) | Span-name format declaration (S1/S2/S3). Owns the format. |
| Information substrate (IS) | None. |
| Control plane (CP) | Routing-namespace cite to parent span (R3 cascade). |
| Deployment surface | None (span emission is deployment-neutral). |
| **Cross-axis seam** | **AS §14.1 parent-anchor convention ↔ OD §4.1 format.** This seam is **not currently declared at CXA v2.10**. That absence is itself a finding — the seam exists in production (the AS parent-anchor cite IS the OD-formatted span) but is unnamed at the cross-axis layer. |

**Probabilistic-deterministic boundary.** All elements on the deterministic side — span-name construction is a string template at dispatch time, deterministic. No prob/det concern.

**F/D/I classification.** ADR-D6 is F5-derivative; OD spec C-OD-04 is D-level (derived from D6's cited external anchor). Span-name format is D-level. AS parent-anchor convention is D-level. This is a **D-level divergence cluster** — lower severity than touching F5 substrate commitment itself; resolvable without ADR revision (the external authority anchor at D6 is preserved; the spec's internal misreading is what's amended).

### §7.4 Recommended reading

#### §7.4.1 R2 (OD spec correction) — RECOMMENDED conform to 2-token

**Reading.** OD spec C-OD-04 §4.1 amends to:

```
{gen_ai.operation.name} {gen_ai.request.model}
```

Per OTel GenAI semconv 1.41.0 [HIGH] canonical span name format — *byte-exact to the cited authority at the cited version*.

**Authority-chain citation.** ADR-D6 v1.2 §1.2 cites 1.41.0 [HIGH] as the cross-vendor floor (line 53). The actual 1.41.0 text specifies 2-token. The spec internal rendering is in error vs the cited authority; the cited authority wins per the citation-byte-exact discipline.

**Tension 004 status.** This re-litigates the 2026-05-15 Tension 004 ratification. The ratification recommendation at §4 step 3 explicitly named the required tiebreaker: *"confirm OTel GenAI semconv 1.41.0 itself (the cited external standard) matches the spec §4.x reading — if the actual 1.41.0 convention differs from §4.x, that is a separate spec defect."* That tiebreaker check was deferred-not-performed. This fork performs the check; the check fails; the Tension 004 ratification is superseded.

**Downstream artifacts to absorb (sequenced for spec-writer / implementation-planner):**

1. OD spec v1.11 → v1.12 — §C-OD-04 §4.1 2-token form per actual 1.41.0; §4.2 + §4.3 unchanged at this arc (separate question — Tension 004 also flagged D-2 operations enum 6-vs-7 + D-3 tiers 4-vs-3 divergences; out-of-scope here per FM-2).
2. OD impl `harness-od/src/harness_od/otel_genai_base.py:104` — `SPAN_NAME_FORMAT` becomes 2-token; `span_name(operation, model)` signature drops `provider` parameter.
3. OD test `harness-od/tests/test_otel_genai_base.py:81-90` — 2-token assertion.
4. OD plan v2.18 → v2.19 — U-OD-04 absorption (1-line AC text update + 2-token assertion).
5. Workspace `CLAUDE.md` row + OD spec row + OD plan row updates.
6. Meta-finding logged: Tension 004 ratification deferred-not-performed the §4 tiebreaker check; pattern catalogued for future tension-resolution ratifications.

#### §7.4.2 R1 (production rename) — RECOMMENDED follow R2

**Reading.** `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:324`:

```python
span_name = f"{operation} {model}"  # per OD spec v1.12 §C-OD-04 §4.1
```

`provider_name` reference at line 324 is dropped from the span-name; preserved as `gen_ai.provider.name` attribute set on the span (already at line 330 — `span.set_attribute("gen_ai.system", provider_name)` — note `gen_ai.system` vs `gen_ai.provider.name`; that attribute-name divergence is a separate Tension-004-D-3 carry-forward not patched here per FM-2).

**Downstream artifacts:**

1. Production rename at `llm_dispatch.py:324`.
2. Test fixtures at `harness-runtime/tests/test_lifecycle_llm_dispatch.py` (13 tests) + `test_lifecycle_cost_attribution_llm_dispatch.py` (7 tests) updated to expect 2-token form.
3. R4 STRIKE on `class_3_drift_c_od_04_gen_ai_binding_site_silence.md` line 34 (absorb via R2 spec amendment per existing filing's §2.1 self-recommendation).

#### §7.4.3 R3 (AS spec parent-anchor) — RECOMMENDED option (b) alias-term abstraction

**Architectural finding: option (a) literal rename is structurally impossible.** Post-R2 span-name is template-instantiated per-call (`{operation} {model}` resolves to e.g. `chat claude-opus-4-7` at one dispatch and `embeddings text-embedding-3` at another). A *literal string* parent-anchor cite cannot point at a per-call-variable name. The current `llm.inference` literal works only because it's never emitted — it's a phantom anchor.

**Reading.** Introduce a canonical alias term at AS spec §14.1 (or co-published at ADR-D6 §1.2 — operator-discretion on authoring site):

> **The LLM inference span** — the span opened by the runtime LLM dispatcher composer per OD C-OD-04 §4.1 (span name = `{gen_ai.operation.name} {gen_ai.request.model}` per actual emission). Cited at this spec as "the LLM inference span"; the literal span-name format is owned by OD §4.1.

AS spec §14.1 row 1129 then reads: `anthropic.*` parent-anchor = **the LLM inference span** (alias term, not literal).

**Downstream artifacts:**

1. AS spec v1.6 → v1.7 — §14.1 row 1129 + table-header note introducing alias term; row text becomes "the LLM inference span" (alias) with footer note cite to OD §4.1 format owner.
2. AS impl `harness-as/src/harness_as/anthropic_attribute_namespaces.py:110` — `_ANTHROPIC_SPAN = "llm.inference"` constant either (i) removed (anchor is conceptual at spec-layer, not enforced at runtime) OR (ii) refactored to a per-call resolver `def parent_inference_span_name(operation, model) -> str:` aligned with OD helper. Recommend (i) — the constant is unused at any assertion site that checks the actual emitted name.
3. 11 source-file docstring sites at fork §2.2 — replace literal `llm.inference` with alias term phrasing.
4. 8 data-value sites at fork §2.2 — case-by-case: most are docstring data structures (low-stakes); the `multi_agent_span_hierarchy.py:84` literal `"llm.inference[]"` and `routing_namespace.py:51` `inherited_from` constant need refactor to alias-resolver or removal.
5. Test `test_routing_namespace.py:6,35,37` — alias-aware assertion.

**Why option (b) over option (a).** Option (a)'s scope is ~3-4 commits but produces a STILL-WRONG cite — the new literal would be e.g. `"chat claude-opus-4-7"` which is itself a per-call-variable masquerading as a literal. Option (b)'s scope is ~5-7 commits but produces a STRUCTURALLY-CORRECT cite — a stable alias term that decouples spec parent-anchor citations from runtime span-name resolution. Future semconv version bumps (1.41.0 → 1.42.0 etc.) ripple only through OD §4.1 + production rename; AS spec parent-anchor cites are immune.

**Cross-axis seam declaration owed at CXA v2.10.** Per §7.3 finding — the AS §14.1 parent-anchor convention ↔ OD §4.1 format seam is not currently declared at CXA. The R3 option (b) landing should co-declare this seam at CXA v2.10 → v2.11 (new row at §2.3.x convention-level bucket; not a typed seam since both sides are spec-only at this layer).

#### §7.4.4 R4 (class_3 filing STRIKE) — RECOMMENDED concurrent with R2

Single-line patch at `class_3_drift_c_od_04_gen_ai_binding_site_silence.md` line 34. Co-published with R2.

### §7.5 Recommended sequencing

| Step | Arc | Scope | Authority anchor |
|---|---|---|---|
| 1 | **R2** OD spec correction + R4 STRIKE | ~4-6 commits | ADR-D6 §1.2 cited 1.41.0 actual text |
| 2 | **R1** production rename | ~2 commits | OD spec v1.12 §4.1 post-R2 |
| 3 | **R3 option (b)** AS spec alias-term + CXA seam declaration | ~5-7 commits | Decouples parent-anchor cite from runtime span-name format |

Total: ~11-15 commits across 2-3 sessions. R1 may be folded into R2's apply-pass arc if scope-narrowing is operator-preferred.

### §7.5a Runtime-spec deferral suggestion (S6 lineage finding) — surfaced during tiebreaker check

**Finding from §7.6 tiebreaker grep.** `design-substrate/Spec_Harness_Runtime_v1.md` line 2033 (within a deferrals / non-canonical section):

> Span name convention (suggest `gen_ai.{provider}.{model_or_method}` per OTel GenAI semconv guidance, e.g., `gen_ai.anthropic.messages.create`).

This is **S6** — a sixth span-name shape, framed as an informal suggestion at runtime spec's deferral layer. **Production at `llm_dispatch.py:324` implements S6**, not OD spec §4.1's authoritative S2. The runtime-spec suggestion is at lower chain authority than OD spec §4.1 — per `CLAUDE.md` §1.3 axis-ownership convention, OD spec owns C-OD-04 GenAI span-name format; runtime spec defers to OD on cross-axis attribute schemas (line 1930 explicitly: *"ADR-F5 v1.1 §Decision (observability substrate carries GenAI-semconv attribution per OD spec C-OD-04..08)"*).

**Authority-chain implication.** S6 was an unsigned informal suggestion that production silently followed. The suggestion does not override OD spec §4.1 authority. Production's lineage from S6 — rather than from S2 — is **the load-bearing finding** for understanding HOW the divergence persisted: production followed the wrong authority at the runtime-spec deferral layer.

**Additional downstream artifact for R1 apply-pass.** Runtime spec v1.x line 2033 deferral suggestion amendment — either (i) **remove** the suggestion (preferred; the format is OD's to declare, not runtime's to suggest), or (ii) **restate as cross-reference** "see OD spec C-OD-04 §4.1 (post-R2 v1.12)" with no inline format suggestion. Adds ~1 commit to the R1 apply-pass arc.

This finding strengthens the §7.4.1 R2 recommendation — production divergence is now traceably attributed to a documented suggestion, not unsigned implementer-discretion drift.

### §7.6 Tiebreaker check

**The single verifiable fact:** Confirm no artifact at the design-phase substrate later than ADR-D6 v1.2 (2026-05-15 era) re-anchors the GenAI base layer to a semconv version OTHER than 1.41.0.

Verification command:

```bash
grep -rn "semconv\|GenAI" design-substrate/ | grep -v "1.41.0" | head -30
```

**Verification result (executed 2026-05-26 at this filing):** Tiebreaker HOLDS. No artifact re-anchors to a non-1.41.0 version. Other non-1.41.0 matches resolve as:

- `Target_Stack_Commitment_v1.md` A3 row cites semconv 1.36.0 as a JS-instrumentation capability observation (not an authoring anchor; Python tooling cited at 1.41.0)
- `ADR-D4.md` references "OTel GenAI semconv" without version (inherits 1.41.0 via D6)
- `ADR-F5.md` references "OTel GenAI semconv extensions" without version
- `Spec_Control_Plane_v1_2.md` references "OTel GenAI semconv extension" without version
- Plan v2.5 + v2.1 tests cite `_per_semconv_1_41_0` consistent with the anchor
- `Spec_Harness_Runtime_v1.md` line 2033 deferral suggestion uses "OTel GenAI semconv guidance" without version anchor — see §7.5a finding

1.41.0 is the unambiguous canonical version anchor. The 2-token target shape per §7.4.1 is determinate.

**Sub-tiebreaker (R3 option b).** Confirm CXA v2.10 §2.3 conventions bucket can absorb a new row declaring the AS §14.1 parent-anchor ↔ OD §4.1 format seam without architectural conflict. If CXA v2.10 §0 or §2 explicitly forecloses convention-level seam additions (it does not at v2.10 read), R3 option (b)'s CXA co-declaration owes a separate scoping arc.

### §7.7 Fork classification per Project_Workflow_v1_8.md §2.7.6

**Class 1 (halt-execution).** Three independent Class 1 triggers per fork §2.3 — production matches no spec (X-AL-3 + I-1 violation); OD spec contradicts cited external authority (citation byte-exact discipline failure); AS spec parent-anchor cite unfaithful to production.

Halt scope: **R2 + R1 should land before any further OD-axis or AS-axis spec revision touches C-OD-04 or C-AS-14 §14.1.** R3 may land in parallel or after — independent. AS-8 RETIRED close is NOT halted on this fork (per fork §6 — AS-8 gates on Skills/Files/managed_agents producer-site authoring, not span-name shape).

### §7.8 Operator decides

The systems-architect skill produces this recommendation per §4A.4 — *does not decide*. The operator chooses among:

| Choice | What it commits to |
|---|---|
| **(A) Accept §7.4 + §7.5 in full** | Open R2 + R4 apply-pass arc this session; R1 follows; R3 option (b) sequenced after |
| **(B) Accept R2 + R1 only; defer R3** | Open R2 + R1 + R4 apply-pass arc this session; R3 deferred to operator-discretion follow-on |
| **(C) Accept R2 only (narrow scope)** | OD spec v1.11 → v1.12 + helper + tests this session; R1/R3/R4 deferred |
| **(D) Reject recommendation; preserve Tension 004 reading** | Requires explicit operator authoring of (i) why the 3-token form is preserved despite contradicting cited 1.41.0 text, (ii) whether ADR-D6 v1.2 §1.2 cite is amended to a different version anchor that matches the 3-token form, or (iii) whether the 3-token form is canonicalized as a harness-specific extension above the 1.41.0 floor (in which case ADR-D6 wording change owed) |
| **(E) File-only; defer all apply** | Fork doc stands as durable record; apply timing operator-discretion |

**Architect's explicit recommendation: (A) full acceptance with R2 + R4 first.** Rationale: the external-authority contradiction (§7.4.1) is the load-bearing finding; R1 cannot land coherently before R2 (R1's target shape is post-R2); R3 option (b) is structurally necessary independent of R1/R2 timing; sequencing in order R2 → R1 → R3 minimizes within-arc rework.

**Tension 004 ratification (2026-05-15) is superseded** by the §7.4.1 reading at this fork's operator ratification, whichever option (A)–(D) is selected — even (D) requires explicit operator authoring of the chain-reading defense, which is itself a ratification superseding the 2026-05-15 reading.

---

*End §7 architect Mode-3 recommendation. Operator decides per §7.8.*

---

## §8 Finding (f) RESOLVED 2026-05-26 — §4.3 Required (Stable) tier full conform arc

Producer-side conform to OD spec v1.12 §C-OD-04 §4.3 Required (Stable) tier landed at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:337-340`. Three attributes now emitted on every GenAI span (previously: 1-of-3 + 1 wrong-named):

| §4.3 attribute | Pre-arc state | Post-arc state |
|---|---|---|
| `gen_ai.operation.name` | Not emitted as a span attribute (only in span name) | `span.set_attribute("gen_ai.operation.name", operation)` — value = `_PROVIDER_OPERATIONS[provider_name]` (same as operation-token in span name) |
| `gen_ai.provider.name` | Emitted under the old OTel name `gen_ai.system` | Renamed to `gen_ai.provider.name`; value unchanged (`provider_name`) |
| `gen_ai.request.model` | Emitted correctly | Preserved verbatim |

**Scope:** narrow producer-side conform; OD spec already declared the canonical names at v1.12 (no spec amendment owed). Single production site + single test file; 27/27 `test_lifecycle_llm_dispatch.py` PASS; 773/773 harness-od tests PASS; pyright strict 0 errors.

**Finding (g) refined.** Pre-arc framing: "`_PROVIDER_OPERATIONS` values are non-§4.2-enum-conformant in the span-name operation token." Post-arc framing: same non-conformance now visible **at both** the span-name operation-token **and** the `gen_ai.operation.name` attribute value (both share the same `_PROVIDER_OPERATIONS` lookup at `llm_dispatch.py:327`). Value-space conform of `_PROVIDER_OPERATIONS` to §4.2 enum + emission of `gen_ai.operation.name` with the conformed value is a separate arc per FM-2.

**Adjacent: `provider_name` value-space.** OTel 1.41.0 `gen_ai.provider.name` known-values enum includes `anthropic`, `openai`, `gcp.gemini`, `azure.ai.openai`. Current production values (`anthropic`, `openai`, `ollama`) — first two conformant; `ollama` is NOT in the 1.41.0 known-values enum. NOT patched at this arc; surfaces as adjacent finding (h) — value-space conform of `provider_name` to §4.3 known-values enum (likely requires either an `ollama` ratification at OTel semconv upstream OR a harness-specific extension declared at OD spec).

**Commit anchor:** [filled at commit time]

---

## §9 Finding (g) RESOLVED 2026-05-26 — §4.2 operation enum value-space conform at `_PROVIDER_OPERATIONS`

Producer-side conform to OD spec v1.12 §C-OD-04 §4.2 operation enum at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:497-509`. Dict re-typed from `dict[str, str]` (with API method-name string values) → `dict[str, GenAiOperation]` (with canonical §4.2 enum members). All 3 providers dispatch chat-style completions, so all 3 map to `GenAiOperation.CHAT`:

| Provider | Pre-arc value | Post-arc value | Provider-side method |
|---|---|---|---|
| `anthropic` | `"messages.create"` | `GenAiOperation.CHAT` (= `"chat"`) | `client.messages.create` |
| `openai` | `"chat.completions"` | `GenAiOperation.CHAT` (= `"chat"`) | `client.chat.completions.create` |
| `ollama` | `"chat"` | `GenAiOperation.CHAT` (= `"chat"`) | `client.chat` |

Span name + `gen_ai.operation.name` attribute value shift in lockstep (both source from the same lookup):

| Surface | Pre-arc | Post-arc |
|---|---|---|
| Span name (openai example) | `"chat.completions gpt-4o-mini"` | `"chat gpt-4o-mini"` |
| `gen_ai.operation.name` attribute (openai example) | `"chat.completions"` | `"chat"` |
| `gen_ai.operation.name` attribute (anthropic example) | `"messages.create"` | `"chat"` |

**Scope:** narrow producer-side value-space conform; typed enum import binds production to canonical §4.2 declaration (`harness_od.otel_genai_base.GenAiOperation`). OD spec already declared the canonical enum at v1.2 (no spec amendment owed). Single production site + single test assertion update; 27/27 `test_lifecycle_llm_dispatch.py` PASS; 1077/1084 harness-runtime tests PASS (7 pre-existing cwd-sensitive failures unrelated); 773/773 harness-od tests PASS; pyright strict 0 errors.

**Type-discipline upgrade.** `_PROVIDER_OPERATIONS: dict[str, GenAiOperation]` (was `dict[str, str]`) — future-proofs against §4.2 enum drift; if OD spec amends the enum (e.g., reverts to a different operation per-provider), pyright will catch consumer-side drift.

**Finding (h) preserved.** OTel 1.41.0 `gen_ai.provider.name` known-values enum includes `anthropic` + `openai` + `gcp.gemini` + `azure.ai.openai` etc.; `ollama` is NOT in the 1.41.0 known-values enum. NOT patched at this arc; carries forward per FM-2.

**Commit anchor:** [filled at commit time]

---

## §10 Finding (h) CLOSED-NOT-A-DEFECT 2026-05-26 — `ollama` is OTel-conformant under open-known-values discipline

Finding (h) was surfaced at fork §8 + §9 closure notes as "value-space conform of `provider_name` to OTel 1.41.0 `gen_ai.provider.name` known-values enum" with the framing that `ollama` is not in OTel's 15-member list. Empirical verification at OTel 1.41.0 archived spec yields the opposite conclusion: **`ollama` emission is fully conformant**; the prior framing was based on misreading OTel's `type: members:` shape as a closed enum.

### Empirical evidence (verified 2026-05-26 via raw GitHub fetch)

Source: `https://raw.githubusercontent.com/open-telemetry/semantic-conventions/v1.41.0/model/gen-ai/registry.yaml`

The `gen_ai.provider.name` attribute is declared as:

```yaml
- id: gen_ai.provider.name
  stability: development
  type:
    members:
      - id: openai
        stability: development
        value: "openai"
        # ... 14 more members ...
  brief: The Generative AI provider as identified by the client
    or server instrumentation.
  note: |
    The attribute SHOULD be set based on the instrumentation's best
    knowledge and may differ from the actual model provider.
```

The 15 named members are: `openai` / `gcp.gen_ai` / `gcp.vertex_ai` / `gcp.gemini` / `anthropic` / `cohere` / `azure.ai.inference` / `azure.ai.openai` / `ibm.watsonx.ai` / `aws.bedrock` / `perplexity` / `x_ai` / `deepseek` / `groq` / `mistral_ai`. `ollama` is NOT in this list.

### Why this is NOT a defect

| Discriminating fact | Source | Implication |
|---|---|---|
| **OTel `type: members:` is open known-values, not closed enum** | OTel semconv convention: `type: members:` without `allow_custom_values: false` flag = "well-known values with custom value support" by default | Custom values (`ollama`) are tolerated when no listed value applies |
| **`note:` language is SHOULD + "instrumentation's best knowledge"** | OTel 1.41.0 registry.yaml verbatim | SHOULD-not-MUST + best-knowledge framing = open-known-values discipline |
| **OD spec C-OD-04 cardinality table line 664 framing** | `gen_ai.provider.name` is "bounded (per-provider enumeration; expected ≤20 across all providers)" | OD spec explicitly frames as cardinality-bounded, NOT closed enum; conformant with OTel's open shape |
| **Production `provider_name` value-space at HEAD** | `llm_dispatch.py:339` emits `binding.model_binding.provider` ∈ `{anthropic, openai, ollama}` (per `_PROVIDER_OPERATIONS` dict at line 497) | Cardinality = 3 ≤ 20 (within OD spec bound); 2 of 3 in OTel known-values list; `ollama` is a valid custom value per open-known-values discipline |

### Adjacent observation (NOT patched per FM-2)

(i) **`gen_ai.provider.name` stability divergence — Class 3 informational.** OTel 1.41.0 declares this attribute as `stability: development` at both the attribute-level AND every member-level (including `anthropic` + `openai` which production also emits). OD spec C-OD-04 §4.3 classifies the same attribute as **Required (Stable)** tier (always-emit per OD discipline). The OD-spec tier classification is OD's own emission-posture discipline (independent of OTel's stability metadata); the divergence is at the spec-narrative layer, not the wire-protocol layer. Routing: future OD spec doc-hygiene pass MAY add a footer clarifying that OD's Required (Stable) tier classification ≠ OTel attribute stability declaration. Non-blocking; surfaces no production-side action.

### Resolution + fork doc closure cascade

Finding (h) framing across this fork doc updated to NOT-A-DEFECT:

- §8 (finding (f) closure) — "Adjacent: `provider_name` value-space" paragraph PRESERVED VERBATIM as historical record of the surfacing observation; this §10 supersedes the framing
- §9 (finding (g) closure) — "Finding (h) preserved per FM-2" paragraph PRESERVED VERBATIM as historical record; this §10 supersedes
- This §10 is the canonical resolution

**No code change. No spec amendment. No worktree commits beyond this doc append.**

**Commit anchor:** [filled at commit time]

### Pattern catalogued

**`[[empirical-verification-supersedes-training-data-knowledge]]`** — finding (h) was framed based on training-data knowledge of OTel known-values lists ("`anthropic` + `openai` conformant; `ollama` is NOT in the 1.41.0 known-values enum"). Empirical fetch of the authoritative YAML disambiguated `members:` shape semantics (open vs closed) which training-data summarization had collapsed. Sibling pattern to fork §7.4.1 (R2) where empirical fetch of 1.41.0 §4.1 span-name text superseded Tension 004 D-1 ratification (also a training-data-collapse: the spec text said 2-token but was paraphrased as 3-token at v1.2 authoring). Discipline: when a finding cites an external authority, perform the empirical fetch BEFORE opening the apply arc — the fetch may dissolve the finding.
