# Spec: Operational Discipline — v1.14 (delta over v1.13)

---

## Change-note (v1.13 → v1.14)

**Scope of revision.** `mcp.*` namespace cross-emission on non-`mcp.tool.call` spans — ingestion ownership ambiguity Class 2 fork resolution apply pass per `.harness/class_1_fork_mcp_namespace_cross_emission_ingestion_ownership.md` §6 (operator-ratified 2026-05-26 — Q0 = Class 2; Q1 = Reading A parent-span-class rule; Q2 = (α) single NEW §8.4; Q3 = (a) ratify-apply-now paired publication; Q4 = mixed (ii) empirical-state footer). NEW §C-OD-08 §8.4 sub-section canonicalizing the **parent-span-class ingestion routing rule** for cross-namespace attribute carriers on a single span.

**Narrow-scope framing (explicit).** The arc lands ONLY the NEW §C-OD-08 §8.4 sub-section. Per Q2 = (α) ratification: §C-OD-05 §5.1 rows 4 + 10 are NOT touched (no cross-row coordination note authored); §C-OD-06 lifecycle event mapping is NOT touched (no co-emission-event lifecycle note authored). The v1.13 §C-OD-05 row 10 sub-note (parent-span-class rule worked example for `mcp.fail.class` on `sandbox.violation`) is referenced from §8.4 as the canonical worked example, but the v1.13 sub-note text itself is PRESERVED VERBATIM at v1.14.

**Authority anchor.** ADR-D6 v1.2 §1.2 Namespace collision discipline (anchor for C-OD-08). The NEW §8.4 sub-section is an additive extension at the OD spec layer — NOT an ADR amendment — preserving X-AL-3 (Meta-Architecture §7.7) no-silent-design-extension discipline at Phase 7.

**Empirical-state inference (per Q4 mixed (ii) ratification).** As of 2026-05-26 at HEAD `0c22efc`: production emits both `mcp.fail.class` + `sandbox.fail.class` on `sandbox.violation` spans (`harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:261-282`); no OD-side consumer routes on attribute-prefix at ingestion (`namespace_map.py` is a structural reference table, not an ingestion router; `cp_source_namespace_verification.py` + `as_source_namespace_verification.py` are set-membership verifiers, not per-attribute routers). The §8.4 rule is therefore a **doc-canonicalization for future-proofing** — it does NOT govern current production behavior because no current consumer routes on the ambiguity. The empirical-state inference is documented at the §8.4 footer per Q4 ratification.

---

## §C-OD-08 §8.4 — Parent-span-class ingestion routing rule (v1.14 NEW)

### Authority chain

- v1.2 §C-OD-08 §8.1 (no-override invariant), §8.2 (canonical example — anthropic.* / gen_ai.* cross-namespace on inference span), §8.3 (cross-namespace cardinality discipline) — preserved verbatim through v1.13.
- v1.13 §C-OD-05 §5.1 row 10 sub-note authored the parent-span-class rule as a one-off precedent for `mcp.fail.class` on `sandbox.violation`.
- `.harness/class_1_fork_mcp_namespace_cross_emission_ingestion_ownership.md` §1.2 documented the residual canonicalization question; §6 Q1 ratified Reading A (parent-span-class rule canonicalized at §C-OD-08 §8.4).

### Amendment text

NEW sub-section at §C-OD-08, sibling to §8.1 / §8.2 / §8.3:

**§8.4 Parent-span-class ingestion routing rule (cross-namespace attribute carriers).**

When an attribute uses namespace-prefix-A (e.g., `mcp.fail.class` carries prefix `mcp.`) but is emitted on a span-class-B whose namespace pull is row-B (e.g., `sandbox.violation` span pulled under `sandbox.*` namespace at §C-OD-05 §5.1 row 10), the OD audit-ledger ingestion contract is owned by **row-B (the parent-span-class row)** — NOT by row-A (the attribute-prefix row).

**Scope of §8.4.** §8.4 applies to specialization-namespace co-emission across §C-OD-05 rows (the 15-row specialization-layer ingestion map). OTel canonical attributes at §C-OD-04 (e.g., `gen_ai.usage.input_tokens`, `gen_ai.request.model`) are out of scope — OTel base layer ingestion is governed independently at §C-OD-04 and the §8.1 no-override invariant continues to govern naming/precedence between OTel canonical and additive specialization layers (see §8.2 canonical example).

**Definition of parent-span-class.** The parent-span-class is the §C-OD-05 specialization namespace row whose pull declares the span. Examples: `sandbox.violation` pulls under row 10 (`sandbox.*` per C-AS-15 §15.4); `mcp.tool.call` pulls under row 4 (`mcp.*` per C-AS-14 §14.3); `hitl.invocation.responded` pulls under row 6 (`hitl.*` per C-CP-20 §20.6); the LLM inference span pulls under row 1 (`anthropic.*` per C-AS-14 §14.2). The parent-span-class is determined at the §C-OD-05 declaration site, not at the span name token.

| Rule | Contract |
|---|---|
| **Parent-span-class primacy** | An attribute on a span of class-B ingests via §C-OD-05 row-B regardless of the attribute's prefix-namespace. The parent span's class-B namespace pull owns the ingestion contract for ALL attributes emitted on that span. |
| **Attribute-prefix nominal** | The attribute's prefix-namespace (e.g., `mcp.` in `mcp.fail.class`) carries the **declaration source** — i.e., the AS-spec or CP-spec section that defines the attribute's enum / cardinality / semantic. The prefix does NOT govern OD ingestion routing. |
| **No row duplication** | A cross-namespace attribute is ingested at exactly one §C-OD-05 row (the parent-span-class row). It is NOT also ingested at the attribute-prefix row. Cross-row coordination is not required because cross-row ingestion is foreclosed. |
| **Composition with §8.1** | The §8.1 no-override invariant continues to govern naming/precedence between additive namespaces and OTel canonical layer (e.g., `gen_ai.usage.input_tokens` vs `anthropic.cache_creation_input_tokens` on an inference span). §8.4 governs ingestion-row ownership at OD audit-ledger; §8.1 governs OTel-canonical primacy at attribute naming. The two rules are orthogonal and compose without conflict. |

### §8.4.1 Worked example — `mcp.fail.class` on `sandbox.violation`

The canonical worked example is `mcp.fail.class` (declaration source: AS spec v1.6 §15.8 — `MCPInvocationFailClass` 4-value enum) co-emitted with `sandbox.fail.class` (declaration source: AS spec v1.2 §15.2 row 3 — F4 process-execution taxonomy) on the `sandbox.violation` child span per AS spec v1.6 §15.9 dual-attribute discipline.

| Attribute | Declaration source (attribute-prefix nominal) | Ingestion row (parent-span-class primacy) |
|---|---|---|
| `mcp.fail.class` | AS spec v1.6 §15.8 (`MCPInvocationFailClass` enum) | §C-OD-05 row 10 (`sandbox.*` via C-AS-15 §15.4) — NOT row 4 (`mcp.*` via C-AS-14 §14.3) |
| `sandbox.fail.class` | AS spec v1.2 §15.2 row 3 (F4 enum) | §C-OD-05 row 10 (`sandbox.*` via C-AS-15 §15.4) |

Both attributes ingest at the same §C-OD-05 row 10 — the parent-span-class row for `sandbox.violation`. The `mcp.` prefix on the first attribute is nominal (it points at the AS spec v1.6 §15.8 enum declaration site); ingestion routing is owned by the parent-span-class.

The v1.13 §C-OD-05 §5.1 row 10 sub-note (preserved verbatim at v1.14) documents this specific case; §8.4 generalizes the rule for future cross-namespace co-emission cases.

### §8.4.2 Anticipated future cases (illustrative; NOT-YET-EMITTED)

The §8.4 rule canonicalizes the routing for cases not yet emitted at production:

| Potential cross-namespace co-emission | Parent-span-class | Ingestion row per §8.4 |
|---|---|---|
| `topology.*` attribute on `sandbox.exit` span | `sandbox.*` (row 10) | row 10 |
| `audit.*` attribute on `hitl.invocation.responded` span | `hitl.*` (row 6) | row 6 |
| `validator.*` attribute on `mcp.tool.call` span | `mcp.*` (row 4) | row 4 |

None of these cases are currently emitted at production (verified by grep across `harness-*/src/` 2026-05-26 at HEAD `0c22efc`). The §8.4 rule pre-empts per-case sub-note proliferation at §C-OD-05 if any of these surface. **OTel canonical attributes at §C-OD-04 (e.g., `gen_ai.*`) are out of scope per §8.4 scope statement; their ingestion is governed independently at §C-OD-04 and §8.1 no-override invariant.**

### §8.4.3 Empirical-state footer (per Q4 mixed (ii) ratification)

The §8.4 rule is a **doc-canonicalization for future-proofing**. As of 2026-05-26 at HEAD `0c22efc`:

- Production EMITS the one cross-namespace co-emission case in scope at §8.4.1 (`mcp.fail.class` on `sandbox.violation`).
- NO consumer routes on attribute-prefix at OD ingestion (`namespace_map.py` is a structural reference; `*_namespace_verification.py` are set-membership verifiers).
- The §8.4 rule does NOT govern current production behavior because no current consumer routes on the ambiguity.

The rule's value is canonical-clarity at the OD spec contract layer + pre-emptive footprint reduction for future cross-namespace co-emission cases. The empirical-state inference is preserved at the §8.4 footer to document the rule's load-bearing posture (doc-canonicalization, not behavioral-routing).

### §8.4.4 Composition with §C-OD-05 ingestion-row attribute set

§C-OD-05 §5.1 declares per-row attribute sets (e.g., row 10 `sandbox.*` declares the 7-attribute `sandbox.*` set per C-AS-15 §15.2). When an attribute outside the per-row declared attribute set is ingested at that row per §8.4 (e.g., `mcp.fail.class` ingested at row 10 even though row 10's declared attribute set does NOT include `mcp.fail.class`), the row's attribute-set declaration is NOT re-counted or amended; the cross-namespace attribute is an additive carrier at the span layer, NOT a new row-attribute-set member.

Implication: §C-OD-05 row attribute counts (e.g., row 10 = 7 attrs per AS spec v1.6 §15.9 framing) remain canonical at the declared set; §8.4 cross-namespace ingestion does NOT increment row attribute counts.

**Deferred to implementation discretion.** Specific OD-side runtime ingestion-routing mechanism (if/when a consumer surfaces that routes per-attribute); specific attribute-set discrimination at the per-row consumer boundary (when the OD-side namespace_map.py grows from structural reference into an actual router).

---

## Sections preserved verbatim at v1.14

Per FM-2 no-extension discipline + Q2 = (α) narrow scope, the v1.14 amendment touches ONLY the NEW §C-OD-08 §8.4 sub-section. The following sections are PRESERVED VERBATIM from their authoring versions through v1.14:

- **§C-OD-04 §4.1/§4.2/§4.3/§4.4/§4.5** (v1.12-lineage GenAI span format)
- **§C-OD-05 §5.1 rows 1-15** (v1.2-lineage; v1.13 row 10 sub-note preserved verbatim — §8.4 references it as the canonical worked example)
- **§C-OD-05 §5.2 + §5.3** (ingestion-posture invariants; F2-12 forward-compatibility note)
- **§C-OD-06 (lifecycle event mapping)** — preserved verbatim through v1.13 → v1.14
- **§C-OD-07 (`harness.breaker.*` schema)** — preserved verbatim
- **§C-OD-08 §8.1 (no-override invariant), §8.2 (canonical example), §8.3 (cross-namespace cardinality discipline)** — preserved verbatim; §8.4 is additive sibling
- **§C-OD-09 through §C-OD-33** (all v1.2-v1.13 lineage content preserved per delta-only-spec-file convention)
- All v1.3 through v1.13 substantive amendments

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **OD spec v1.13 finding (a) — `sandbox.*` namespace cardinality drift.** AS spec v1.6 §15.9 extends `sandbox.*` to 7 attrs PLUS the co-emission of `mcp.fail.class`. OD spec v1.2 §C-OD-05 §5.1 row 10 cite-shape says "6-attribute" implicitly via AS §15.4 reference. Pre-existing at v1.2; carried verbatim from v1.13. NOT patched at v1.14 per FM-2 — owed at separate apply-pass arc if operator routes a §C-OD-05 row 10 cardinality refresh. §8.4.4 explicitly states cross-namespace ingestion does NOT increment row attribute counts; the cardinality-drift concern is independent of §8.4 (it is about row 10's own declared attribute set, not cross-namespace carriers).

(b) **OD spec v1.13 finding (c) — Tension 004 D-2/D-3/D-4 carries.** Carried verbatim from v1.13. v1.14 does NOT touch §C-OD-04 §4.2/§4.3/§4.5.

(c) **OD spec v1.13 finding (d) — `gen_ai.system` vs `gen_ai.provider.name` divergence.** Carried verbatim from v1.13. v1.14 does NOT touch this carry.

(d) **§8.4.2 anticipated cases empirical-verification.** The illustrative table at §8.4.2 names 3 not-yet-emitted cross-namespace co-emission cases. Whether any of these surface at future implementation arcs is unknown; the §8.4 rule pre-empts proliferation but does NOT mandate emission. NOT patched per FM-2 — empirical-verification at future arcs.

---

## Downstream artifacts requiring absorption at follow-on arcs

| Artifact | Required change | Owner |
|---|---|---|
| Workspace `CLAUDE.md` §2.3 OD spec row | v1.13 → v1.14 row update with v1.14 change-note narrative; v1.13 lineage preserved | This session apply-pass arc |
| OD spec v1.13 §"Adjacent observations" finding (b) | Status update: RESOLVED at v1.14 §C-OD-08 §8.4 publication. v1.13 file PRESERVED VERBATIM per delta-only convention; status update reflected at fork doc §8 + workspace `CLAUDE.md` row narrative. | This session apply-pass arc |
| `harness-od/CLAUDE.md` | NO change owed — §C-OD-08 §8.4 is OD-axis-internal canonicalization; no cross-axis citation table update required. | n/a |
| CXA v2.12 | NO change owed — §8.4 governs OD-internal ingestion-row routing; CXA convention-level seam at §0.4 (NEW at v2.12) already handles spec ↔ spec citation discipline for the AS §15.9 ↔ OD §C-OD-05 row 10 sub-note pair. | n/a |
| AS spec v1.6 / v1.7 | NO change owed — AS §15 footer item (i) framing (`mcp.fail.class` is at AS-axis sandbox.* namespace, not a new top-level namespace) is consistent with §8.4 parent-span-class rule. | n/a |
| ADR-D6 v1.2 | NO change owed per X-AL-3 (Meta-Architecture §7.7) — §8.4 is additive at spec layer, not an ADR §1.2 amendment. | n/a |

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.14 (additive substantive amendment authoring NEW §C-OD-08 §8.4; v1.13 file PRESERVED VERBATIM per delta-only-spec-file convention; §C-OD-08 §8.1-§8.3 preserved verbatim from v1.2 lineage) |
| Trigger | `.harness/class_1_fork_mcp_namespace_cross_emission_ingestion_ownership.md` §6 (operator-ratified 2026-05-26 — Q0 = Class 2; Q1 = Reading A; Q2 = (α); Q3 = (a); Q4 = mixed (ii)) |
| Supersedes | None — additive sub-section canonicalizing the v1.13 §C-OD-05 row 10 sub-note precedent at the §C-OD-08 namespace collision discipline contract layer |
| Scope of revision | NARROW: NEW §C-OD-08 §8.4 sub-section ONLY (per Q2 = (α) ratification) |
| Sections revised | §C-OD-08 (NEW §8.4 sub-section authoring parent-span-class ingestion routing rule + §8.4.1 worked example + §8.4.2 anticipated cases + §8.4.3 empirical-state footer + §8.4.4 row-attribute-set composition) |
| Sections preserved verbatim | §C-OD-04 §4.1/§4.2/§4.3/§4.4/§4.5; §C-OD-05 §5.1 rows 1-15 (v1.13 row 10 sub-note preserved); §C-OD-05 §5.2 + §5.3; §C-OD-06 (lifecycle); §C-OD-07 (harness.breaker.*); **§C-OD-08 §8.1 + §8.2 + §8.3** (preserved verbatim from v1.2 lineage); §C-OD-09..§C-OD-33; all v1.3-v1.13 substantive amendments |
| Adjacent findings surfaced | 4 (per "Adjacent observations" section above); NOT patched per FM-2 |
| Cross-file absorption owed | 1 artifact (workspace `CLAUDE.md` OD spec row) — owed at this session apply-pass arc |
| Authority anchor | ADR-D6 v1.2 §1.2 Namespace collision discipline (anchor for C-OD-08); fork `class_1_fork_mcp_namespace_cross_emission_ingestion_ownership.md` §6 (operator-ratified 2026-05-26) |
| Predecessor | v1.13 (AS-4 dual-attribute `sandbox.violation` OD/CXA ingestion cascade — §C-OD-05 §5.1 row 10 sub-note; preserved verbatim outside §C-OD-08 §8.4 NEW) |
| Successor | v1.15 (next operator-discretion arc — candidates: Tension 004 D-2/D-3/D-4 absorption per v1.13 carries; or `sandbox.*` namespace cardinality drift per v1.14 adjacent finding (a) + v1.13 finding (a)) |
