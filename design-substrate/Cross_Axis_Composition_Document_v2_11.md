# Cross-Axis Composition Document (v2.11)

*Delta over v2.10. v2.11 declares a spec-level cross-axis citation convention seam: the AS spec v1.7 §14.1 alias-term "the LLM inference span" cross-references OD spec v1.12 §C-OD-04 §4.1 as the canonical format owner. This is a convention-level seam (spec ↔ spec citation discipline), NOT a typed runtime edge — no aggregate matrix change, no per-axis attribution change, no new cross-axis cascade at the runtime layer. The seam was previously implicit (literal `llm.inference` parent-anchor cite at AS §14.1 was never aligned with any spec ownership decision); v2.11 makes the ownership boundary explicit. All v2.10 + v2.9 + v2.8 + v2.7 + v2.6 substantive content preserved verbatim by reference.*

## §0 Change note (v2.10 → v2.11)

### §0.1 Revision context — AS §14.1 alias-term ↔ OD §4.1 format-owner spec-level seam

Per `.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.3 (R3) operator-ratified 2026-05-26 option (A) + option (b) alias-term abstraction:

- **AS spec v1.6 → v1.7** introduced an alias-term convention at §14.1: literal string `llm.inference` (phantom anchor; never emitted at production per fork §2.2) replaced with conceptual alias term **"the LLM inference span"** with cross-reference to OD spec v1.12 §C-OD-04 §4.1 for actual runtime span-name format.
- **OD spec v1.11 → v1.12** amended §C-OD-04 §4.1 from 3-token `{operation} {provider} {model}` to 2-token `{operation} {model}` per actual OTel GenAI semantic conventions 1.41.0 archived text.
- **Architectural ownership**: OD axis owns the runtime span-name format (§C-OD-04 §4.1); AS axis cites the parent-span anchor for namespace attributes via the alias term, decoupled from the literal runtime span name.

The R3 option (b) alias-term abstraction creates a spec-level cross-axis citation seam: AS spec uses the alias term, OD spec owns the format. Future OTel semconv version bumps (1.41.0 → 1.42.0 etc.) ripple only through OD §4.1 + production rename; AS spec parent-anchor cites are immune.

### §0.2 Scope of v2.11 amendment

v2.11 is a **convention-declaration amendment**, not a typed-edge amendment:

- **NEW §0.4 sub-section** — declares the spec-level seam at a documentation layer
- **Aggregate matrix at §2.1**: UNCHANGED (100 typed edges; 30 genuine; 24 phase-2-runtime; 46 convention-level — v2.10 cardinality preserved)
- **Per-axis attribution at §2.4**: UNCHANGED (no new runtime edge; convention-level citation seams are not counted at axis-attribution layer)
- **§2.3.x per-bucket enumerations**: UNCHANGED (no row added at any §2.3.x bucket — the seam is convention-level, not a typed runtime edge between atomic units)

All other v2.10 + v2.9 + v2.8 + v2.7 + v2.6 substantive content preserved verbatim by reference.

### §0.3 Why this is convention-level, not typed

A typed cross-axis seam in this document's enumeration carries (a) a producer atomic unit, (b) a consumer atomic unit, (c) a typed payload schema, and (d) a runtime data-flow direction. The AS §14.1 ↔ OD §4.1 seam has none of these — it is a **spec citation convention**: AS spec body cites OD spec body via an alias term. No atomic unit produces or consumes anything across this seam at runtime. The seam exists only at the design-substrate authoring layer.

Convention-level seams of this shape ARE counted at §2.1's "46 convention-level" sub-total (v2.10 baseline), but the count is held in aggregate at §2.1 rather than enumerated per-bucket at §2.3.x. v2.11 introduces a NEW convention-level seam — the §2.1 sub-total grows 46 → 47. Aggregate 100 → 100 (typed edges unchanged); genuine 30 → 30 (typed edges unchanged); convention-level 46 → 47.

Actually, on closer reading: the existing 46 convention-level sub-total at §2.1 is the v2.6-era count of convention-level seams already declared at this document; v2.11 adds the first NEW convention-level seam since that count was established. The growth pattern mirrors the §2.3.7 typed-seam growth (v2.4 = +1, v2.6 = +5, v2.9 = +1) — convention-level seams accrete additively over time as new spec-vs-spec citation disciplines emerge.

### §0.4 NEW spec-level seam declaration

| Producer side | Consumer side | Seam shape | Authority anchor |
|---|---|---|---|
| **AS spec v1.7 §14.1** (alias-term "the LLM inference span") | **OD spec v1.12 §C-OD-04 §4.1** (canonical span-name format `{operation} {model}`) | Spec-vs-spec citation convention. AS spec cites the parent-span anchor for `anthropic.*` namespace attributes via the alias term; OD spec owns the format. No runtime data flow. No atomic-unit consumer. | `.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.3 (R3) operator-ratified 2026-05-26 option (b) |

**Production refactor sites that follow the convention** (5 carrier sites + 4 docstring sites; per fork doc §2.2 enumeration; landed at R3 apply-pass this session in worktree `worktree-genai-span-name-discriminator-audit` commit `006a995`):

- `harness-as/src/harness_as/anthropic_attribute_namespaces.py:110` — `_ANTHROPIC_SPAN` constant carries the alias term
- `harness-as/src/harness_as/anthropic_primitive_sampling.py:40` — mapping key uses alias term
- `harness-cp/src/harness_cp/routing_namespace.py:50-52` — `_LLM_INFERENCE_PARENT` text uses alias term + cross-reference cite
- `harness-cp/src/harness_cp/multi_agent_span_hierarchy.py:84` — `"the LLM inference span[]"` data literal
- 5 additional docstring sites at `routing_namespace.py:6,10,47` + `cp_namespace_export_manifest.py:48` + `workflow_driver.py:178` + `cp_source_namespace_verification.py:14` + `llm_dispatch.py:285` + `memory_tool_dispatch.py:108,112`

**Test alias-aware assertion site** (1 site): `harness-cp/tests/test_routing_namespace.py:35-37` — asserts `"the LLM inference span" in attr.inherited_from` post-R3.

### §0.5 Adjacent observations (NOT patched per FM-2)

(a) **Other §14.1 parent-span literals at AS spec.** `mcp.tool.call` / `skill.activation` / `managed_agents.runtime` / `files.operation` / `memory.operation` literals at §14.1 PRESERVED VERBATIM at AS spec v1.7 — those names ARE actual emitted span names at production (verified empirically at R3 apply-pass). If future arcs introduce per-call-variable naming for any of these (unlikely per current design), the alias-term convention extends naturally — but no extension owed at v2.11.

(b) **`gen_ai.system` vs `gen_ai.provider.name` attribute-name divergence at production** (OD spec v1.12 §"Adjacent observations" (f)). Unchanged at v2.11; separate apply-pass arc owed at OD spec v1.13 or follow-on.

(c) **`_PROVIDER_OPERATIONS` non-§4.2-enum-conformance at production** (runtime spec v1.27 §"Adjacent observation"). Unchanged at v2.11; separate apply-pass arc owed.

### §0.6 Status

Proposed (v2.10) → **Proposed (v2.11)**. v2.11 is an additive convention-declaration amendment — one new convention-level seam at §0.4. No aggregate matrix change; no typed-edge change; no per-axis attribution change; no cross-axis cascade at runtime layer.

### §0.7 Downstream artifacts requiring absorption

Cross-file back-references — flagged for downstream absorption; not all owed at this v2.11 publication:

| Artifact | Required change | Owner |
|---|---|---|
| Workspace `CLAUDE.md` §2.3 CXA row | v2.10 → v2.11 row update | This session (sibling commit) |
| `harness-cxa/CLAUDE.md` (if it cites CXA version) | v2.10 → v2.11 cite refresh if applicable | Operator-discretion |
| Per-axis `harness-{as,cp,od}/CLAUDE.md` (if any cite CXA §2.x convention-level sub-total) | Cite refresh if applicable | Operator-discretion |

---

## §1 Filing footer

| Field | Value |
|---|---|
| Version | v2.11 (delta-only convention-declaration amendment; v2.10 file preserved verbatim per delta-only convention) |
| Trigger | `.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.3 (R3) operator-ratified 2026-05-26 option (A) + option (b); co-published with AS spec v1.6 → v1.7 amendment (`006a995` this session) + R3 production refactor (`006a995`) |
| Scope of revision | NARROW: NEW §0.4 spec-level seam declaration ONLY |
| Sections revised | NEW §0.4 |
| Sections preserved verbatim | All v2.10 + v2.9 + v2.8 + v2.7 + v2.6 substantive content |
| Aggregate matrix delta | None |
| Per-axis attribution delta | None |
| §2.3.x per-bucket enumeration delta | None |
| Convention-level sub-total delta | 46 → 47 (at §2.1 aggregate sub-total) |
| Cross-axis cascade | None at runtime layer; spec-level only |
| Authority anchor | AS spec v1.7 §14.1 + OD spec v1.12 §C-OD-04 §4.1 + fork §7.4.3 |
| Predecessor | `Cross_Axis_Composition_Document_v2_10.md` (preserved verbatim outside the §0.4 NEW declaration) |
| Successor | v2.12 (next operator-discretion arc; candidates: other adjacent findings absorption per §0.5 (a)/(b)/(c); other operator-ratified amendments) |
