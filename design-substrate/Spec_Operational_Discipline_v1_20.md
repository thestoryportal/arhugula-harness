# Spec: Operational Discipline — v1.20 (delta over v1.19)

---

## Change-note (v1.19 → v1.20)

**Scope of revision.** Fidelity-pure canonical-reading amendment closing v1.19 §"Adjacent observations" finding (d) — `§C-OD-04 §4.4 against OTel 1.41.0 archived text` — as **CLOSED-via-narrowing-hierarchy-claim** 2026-05-27. §C-OD-04 §4.4 audit performed this arc against OTel GenAI semantic conventions 1.41.0 archived text at `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-agent-spans.md` (raw-fetched + cached this session at `$CLAUDE_JOB_DIR/gen-ai-agent-spans-v1.41.0.md`) + cross-referenced against gen-ai-spans.md execute_tool span attribute table (lines 612-621 at the v1.41.0 archived text cached at `$CLAUDE_JOB_DIR/gen-ai-spans-v1.41.0.md`).

**Audit verdict.** OD spec v1.2 §C-OD-04 §4.4 (preserved verbatim through v1.19) declares `gen_ai.conversation.id` as the "correlation key for `invoke_agent` / `chat` / `execute_tool` hierarchy per OTel GenAI Agent Spans." Audit findings:

- ✓ **`chat` carries `gen_ai.conversation.id` at OTel 1.41.0** — verified at chat-span attribute table (gen-ai-spans.md line 76); Conditionally Required "when available".
- ✓ **`invoke_agent` carries `gen_ai.conversation.id` at OTel 1.41.0** — verified at agent-spans.md invoke_agent client span (line 217) + invoke_agent internal span (line 478); both Conditionally Required "when available".
- ✗ **`execute_tool` does NOT carry `gen_ai.conversation.id` at OTel 1.41.0** — verified at gen-ai-spans.md execute_tool span attribute table (lines 612-621); 8 attributes declared (`gen_ai.operation.name`, `gen_ai.tool.name`, `error.type`, `gen_ai.tool.call.id`, `gen_ai.tool.description`, `gen_ai.tool.type`, `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result`); `gen_ai.conversation.id` is NOT among them.
- ✓ **OTel does NOT frame `gen_ai.conversation.id` as a cross-span "hierarchy correlation key"** — the OTel-derived framing is per-span attribute on chat + invoke_agent operations only; the "correlate messages within this conversation" language refers to messages within a single conversation context, not cross-span hierarchical linkage. The "hierarchy correlation key" framing at OD §4.4 is OD-authored synthesis layered atop the OTel per-span attribute declarations.

**OD-authored synthesis layer.** The "hierarchy correlation key" framing is OD-axis discipline (an OD-stricter posture beyond what OTel canonicalizes). v1.20 preserves the OD-authored synthesis layer for chat + invoke_agent operations (where OTel canonically supports the attribute) while narrowing the claim to exclude execute_tool (where OTel does NOT support the attribute). Trace-context (OTel-canonical parent-child span linking via trace_id + parent_span_id) is the canonical OTel mechanism for execute_tool ↔ invoke_agent linkage when execute_tool is a child span of an invoke_agent or chat parent.

**Stance.** Mirror-OTel — narrow §4.4 hierarchy claim to drop execute_tool, per v1.19 mirror-OTel-tiers stance precedent. Continuity with v1.16 lineage (spec → OTel conformance direction). Alternative stance (document-harness-stricter — preserve execute_tool in §4.4 with explicit "OD-stricter beyond OTel" prose) is plausible but NOT chosen because production grep this session confirms ZERO `set_attribute("gen_ai.conversation.id", ...)` callsites at any production span (verified at v1.19 §"Adjacent observations" finding (g)); there's no production posture to "stricter" mirror — the spec claim was forward-looking-only, and mirror-OTel removes a forward-looking claim that production does not currently make.

**Empirical posture (load-bearing).** Production grep at HEAD `4333bc7` this session:

- `harness-od/src/harness_od/otel_genai_base.py:136-139` → `HIERARCHY_CORRELATION_KEY` carrier docstring repeats the v1.2 §4.4 execute_tool inclusion verbatim ("the correlation attribute for the `invoke_agent` / `chat` / `execute_tool` span hierarchy"). Co-published this arc with docstring narrowing.
- `harness-od/tests/test_otel_genai_base.py:258-260` → `test_hierarchy_correlation_key_is_conversation_id` asserts only the constant value (`HIERARCHY_CORRELATION_KEY == "gen_ai.conversation.id"`); does NOT assert the operation hierarchy scope; test unchanged at v1.20.
- ZERO `set_attribute("gen_ai.conversation.id", ...)` at any `harness-runtime/*` or `harness-od/*` production callsite (verified at v1.19 §"Adjacent observations" finding (g); preserved at v1.20).

**Pre-substantive empirical-verification audit (v1.18 §5 discipline applied prospectively).** Before authoring this v1.20 file, audit pass against all v1.19 §"Adjacent observations" carries (b)–(i) was performed empirically at HEAD `4333bc7` per the v1.18 §5 strengthened discipline. Results:

- (b) v1.19 finding (c) §8.4.2 anticipated cases — grep verified ZERO production hits at HEAD; carry remains genuine as deferred-monitor.
- (c) v1.19 finding (d) §15.2 vs §15.4 split informational — AS spec v1.7 unchanged; carry remains genuine.
- (d) v1.19 finding (f) §C-OD-04 §4.4 audit — **AUDITED this arc**; closed via narrowing-hierarchy-claim.
- (e) v1.19 finding (g) workflow-grammar discipline candidate — `Project_Workflow_v1_8.md` unchanged; carry remains genuine.
- (f) v1.19 finding (f) `gen_ai.provider.name` stability tier divergence — divergence verified still-present at OTel 1.41.0 + OD carrier; carry remains genuine.
- (g) v1.19 finding (g) `gen_ai.conversation.id` declared-but-not-emitted divergence — verified still-present (ZERO production emission); carry remains genuine.
- (h) v1.19 finding (h) `server.port` + `server.address` declared-but-not-emitted divergence — verified still-present; carry remains genuine.
- (i) v1.19 finding (i) discipline-validation observation (informational) — v1.20 §"Pre-substantive empirical-verification audit" is the SECOND PROSPECTIVE APPLICATION of the v1.18 §5 strengthened discipline at a substantive amendment arc; the discipline continues to validate.

ZERO stale-carry findings at v1.19 → v1.20 transition. The audit-discipline continues to operate prospectively.

**Routing.** Per workspace `CLAUDE.md` §4.3 + I-1 byte-exact discipline + v1.19 substantive-amendment precedent (mirror-OTel-tiers stance + chat-span-only audit scope per §4.1 alias-term): v1.20 is a NEW delta file authoring §1 canonical-reading amendment narrowing the §4.4 hierarchy claim + §2 finding-closure refresh + §3 cross-artifact cite-cascade disposition. v1.2-v1.19 PRESERVED VERBATIM per delta-only-spec-file convention.

**No fork doc filed.** Per workspace precedent for fidelity-pure canonical-reading amendments (v1.15 phantom closure / v1.17 stale-carry closure / v1.18 stale-carry closure / v1.19 tier-redistribution audit) — single-authority-anchor amendments do not require fork doc filing. The upstream audit-anchor `class_1_fork_tension_004_d2_d3_otel_141_relitigation.md` §4 step 3 named the OTel 1.41.0 archived-text tiebreaker check generally; v1.16 / v1.19 / v1.20 are the per-section apply-pass arcs. No separate fork doc.

---

## §1 Canonical-reading amendment table (v1.20 NEW)

Per delta-only-spec-file convention, the v1.2 through v1.19 file bodies are PRESERVED VERBATIM. The following table maps every §4.4 hierarchy-claim site to its corrected canonical reading.

### §1.1 §C-OD-04 §4.4 — hierarchy claim narrowed to drop `execute_tool`

The v1.2-lineage §C-OD-04 §4.4 (line 301 of v1.2 file) reads:

> `gen_ai.conversation.id` is the correlation key for `invoke_agent` / `chat` / `execute_tool` hierarchy per OTel GenAI Agent Spans. Cardinality-safe-attribute discipline (C-OD-11) restricts this attribute to span attributes only — NEVER metric dimension.

The canonical reading at v1.20:

> `gen_ai.conversation.id` is the correlation key for `invoke_agent` / `chat` operations per OTel GenAI Agent Spans (`gen-ai-agent-spans.md` 1.41.0 lines 217 + 478) + OTel GenAI Spans (`gen-ai-spans.md` 1.41.0 line 76). The `execute_tool` span at OTel 1.41.0 does NOT declare `gen_ai.conversation.id` as an attribute (verified at `gen-ai-spans.md` 1.41.0 lines 612-621; 8 attributes — `gen_ai.operation.name`, `gen_ai.tool.name`, `error.type`, `gen_ai.tool.call.id`, `gen_ai.tool.description`, `gen_ai.tool.type`, `gen_ai.tool.call.arguments`, `gen_ai.tool.call.result` — none of which is `gen_ai.conversation.id`); cross-span linkage from `execute_tool` to its parent `invoke_agent` or `chat` span uses OTel-canonical trace context (trace_id + parent_span_id) rather than `gen_ai.conversation.id`. Cardinality-safe-attribute discipline (C-OD-11) restricts `gen_ai.conversation.id` to span attributes only — NEVER metric dimension (preserved verbatim from v1.2).

### §1.2 Cross-artifact citation sites for v1.2-v1.19 §4.4

Per delta-only-spec-file preservation chain, all v1.2-v1.19 §4.4 cite sites at downstream artifacts are PRESERVED VERBATIM at byte-exact layer; canonical reading at v1.20 §1.1 supersedes when interpreting the hierarchy scope at those sites:

| Artifact | Site | v1.2-v1.19 reading | Canonical reading at v1.20 |
|---|---|---|---|
| OD spec v1.2 line 301 §4.4 | Hierarchy claim sentence | `invoke_agent / chat / execute_tool hierarchy` | `invoke_agent / chat operations` (execute_tool dropped per v1.20 §1.1) |
| Helper carrier `harness-od/src/harness_od/otel_genai_base.py:136-139` | `HIERARCHY_CORRELATION_KEY` docstring | "the correlation attribute for the `invoke_agent` / `chat` / `execute_tool` span hierarchy" | **CO-PUBLISHED this arc** — docstring narrowed to `invoke_agent` / `chat`; note added re trace-context linkage for `execute_tool` |
| Helper test `harness-od/tests/test_otel_genai_base.py:258-260` | `test_hierarchy_correlation_key_is_conversation_id` | Asserts only the constant value (no hierarchy-scope assertion) | NO change owed — test asserts constant value only |
| Workspace `CLAUDE.md` (worktree root) §2.3 OD spec row | v1.19 row-text narrative | v1.19 narrative | **Bumped to v1.20** at co-publication commit this arc |
| Peer specs (AS / CP / runtime), CXA, ADR, ADD, PRD, OD plan | NO §4.4 hierarchy-scope cite | n/a | NO change owed — verified via grep this session |

---

## §2 Finding-closure-disposition refresh

**Closed-via-narrowing-hierarchy-claim.** v1.19 §"Adjacent observations" finding (d) — `§C-OD-04 §4.4 against OTel 1.41.0 archived text` — is now closed at v1.20 §1.1 canonical-reading amendment. The audit deferred at v1.16/v1.17/v1.18/v1.19 §"Adjacent observations" is RESOLVED.

**Disposition at v1.20.** Finding (d) is CLOSED. Removed from v1.20 §"Adjacent observations" carry; no longer a deferred-audit arc.

**Adjacent v1.19 carries preserved at v1.20.** Findings (b)/(c)/(e)/(f)/(g)/(h)/(i) carried verbatim from v1.19 → v1.20 with audit-pass verification this arc (see Change-note §"Pre-substantive empirical-verification audit").

---

## §3 Cross-artifact cite-cascade disposition (v1.20 NEW)

| Artifact | Site | Carry-text framing | Disposition at v1.20 |
|---|---|---|---|
| `harness-od/src/harness_od/otel_genai_base.py:136-139` | `HIERARCHY_CORRELATION_KEY` docstring — execute_tool inclusion in hierarchy | v1.2-lineage docstring | **CO-PUBLISHED this arc** — docstring narrowed to `invoke_agent` / `chat`; cross-reference note added re trace-context linkage for `execute_tool` per OTel-canonical parent-child span mechanism |
| `harness-od/tests/test_otel_genai_base.py:258-260` | `test_hierarchy_correlation_key_is_conversation_id` constant-value test | Asserts constant value only; no hierarchy-scope assertion | NO change owed — test scope is narrower than the v1.20 amendment |
| Workspace `CLAUDE.md` (worktree root) §2.3 OD spec row | v1.19 row-text narrative | v1.19 narrative | **Bumped to v1.20** at co-publication commit this arc |
| Peer specs / CXA / ADR / ADD / PRD / OD plan beyond §4.4 readers | NO §4.4 hierarchy-scope cite at any downstream artifact | n/a | NO change owed — verified via grep this session |
| `Implementation_Plan_Operational_Discipline_v2_20.md` U-OD-04 unit | U-OD-04 AC #5 covers §4.4 hierarchy correlation (acceptance #5 in helper test naming) | v2.20 AC text unchanged; the test it cites (`test_hierarchy_correlation_key_is_conversation_id`) is constant-value-only and remains valid | NO change owed at U-OD-04 plan — the AC is constant-value-only and unaffected by the §4.4 doc narrowing |

ZERO other cite-cascade sites verified via grep this session.

---

## §4 Sections preserved verbatim at v1.20

Per delta-only-spec-file convention + FM-2 no-extension discipline + fidelity-pure canonical-reading amendment scope, the v1.20 amendment touches ONLY the NEW §1 canonical-reading amendment table + §2 finding-closure-disposition refresh + §3 cross-artifact cite-cascade disposition + §"Adjacent observations" refresh. The following sections are PRESERVED VERBATIM from their authoring versions:

- **§C-OD-04 §4.1** (v1.12-lineage span-name 2-component format per D-1 R2)
- **§C-OD-04 §4.2** (v1.2-lineage operations enum; v1.16 §1.1 canonical reading applied; 9 values)
- **§C-OD-04 §4.3** (v1.2-lineage attribute SET; v1.19 §1.1 tier redistribution applied)
- **§C-OD-04 §4.4** HIERARCHY-SCOPE narrowed per v1.20 §1.1 (drop execute_tool); CARDINALITY-SAFE-RESTRICTION preserved verbatim
- **§C-OD-04 §4.5** (v1.2-lineage; verified MATCH at v1.16 §1.4)
- **§C-OD-05 through §C-OD-33** (all v1.2-v1.19 lineage content preserved per delta-only-spec-file convention)
- **All v1.3 through v1.19 substantive amendments** (including v1.13 row 5 sub-note + v1.14 §8.4 cross-namespace ingestion rule + v1.15 §1 canonical reading + v1.16 §1 + v1.17 §1 + v1.18 §1 + v1.19 §1 amendment tables)

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **v1.19 finding (d) — CLOSED-via-narrowing-hierarchy-claim at v1.20 §1.1 + §2.** Removed from "Adjacent observations" carry.

(b) **v1.19 finding (b) — §8.4.2 anticipated cases empirical-verification.** Carried verbatim from v1.16 → v1.17 → v1.18 → v1.19 → v1.20. Audit this session 2026-05-27: production grep for the 3 anticipated cases (`topology.*` on `sandbox.exit`, `audit.*` on `hitl.invocation.responded`, `validator.*` on `mcp.tool.call`) returns ZERO production hits at HEAD `4333bc7` — anticipated cases have NOT materialized; carry remains genuine as deferred-monitor. v1.20 does NOT touch this carry.

(c) **v1.19 finding (c) — v1.15 §15.2 vs §15.4 split informational.** Carried verbatim. AS spec v1.7 unchanged since v1.17; carry remains genuine. v1.20 does NOT touch this carry.

(d) **v1.19 finding (e) — workflow-grammar discipline candidate at `Project_Workflow_v1_8.md`** — STRENGTHENED at v1.18 §5; SECOND PROSPECTIVE APPLICATION at v1.20 §"Pre-substantive empirical-verification audit" (FIRST was at v1.19). Carried verbatim. `Project_Workflow_v1_8.md` unchanged since v1.16; carry remains genuine as deferred-discipline-candidate. v1.20 does NOT touch the upstream artifact.

(e) **v1.19 finding (f) — `gen_ai.provider.name` stability tier divergence.** Carried verbatim. OTel 1.41.0 archived text declares `gen_ai.provider.name` as `stability: development`; OD spec C-OD-04 §4.3 tier name reads `Required (Stable)`. Carry remains genuine. v1.20 does NOT touch this carry.

(f) **v1.19 finding (g) — `gen_ai.conversation.id` declared-but-not-emitted divergence.** Carried verbatim. Production grep at HEAD `4333bc7` confirms ZERO `span.set_attribute("gen_ai.conversation.id", ...)` callsites at `harness-runtime/.../llm_dispatch.py`. The v1.20 §1.1 amendment to drop execute_tool from §4.4 hierarchy narrows but does NOT close this finding — the carrier-vs-production-emission divergence is separable from the §4.4 hierarchy-scope claim. Class 2 in-execution operator-discretion routing target. v1.20 does NOT touch this carry.

(g) **v1.19 finding (h) — `server.port` + `server.address` declared-but-not-emitted divergence.** Carried verbatim. Sibling-of-(f). v1.20 does NOT touch this carry.

(h) **v1.19 finding (i) — discipline-validation observation (informational, Class 3).** Carried verbatim with strengthening at v1.20 §"Pre-substantive empirical-verification audit" — SECOND PROSPECTIVE APPLICATION of the v1.18 §5 discipline at a substantive amendment arc. The discipline continues to validate (zero stale-carries at v1.19 → v1.20 transition). v1.20 does NOT touch the upstream Project_Workflow_v1_8.md artifact.

(i) **NEW at v1.20 — OD-authored synthesis layer at §4.4.** The v1.2-v1.19 §4.4 "hierarchy correlation key" framing is OD-axis discipline (an OD-axis synthesis layered atop OTel's per-span `gen_ai.conversation.id` attribute declarations). OTel 1.41.0 does NOT canonicalize a cross-span "hierarchy correlation key" mechanism; it declares `gen_ai.conversation.id` as a per-span Conditionally Required attribute on operations where the attribute applies, leaving cross-span linkage to OTel-canonical trace-context (parent-child span linking via trace_id + parent_span_id). The OD-authored synthesis layer is preserved at v1.20 §1.1 for chat + invoke_agent (where OTel canonically supports the attribute), but the synthesis layer's distinctness from OTel canonicalization is itself a documentable axis-discipline finding. Routing: future OD spec doc-hygiene pass MAY add a footer at §4.4 documenting the OD-authored-synthesis vs OTel-derived split explicitly. Class 3 informational; NOT patched per FM-2 single-focus arc scope.

---

## Downstream artifacts requiring absorption at follow-on arcs

| Artifact | Required change | Owner |
|---|---|---|
| Workspace `CLAUDE.md` §2.3 OD spec row | v1.19 → v1.20 row update with v1.20 change-note narrative; v1.19 + earlier lineage preserved | This session apply-pass arc |
| `harness-od/src/harness_od/otel_genai_base.py:136-139` | `HIERARCHY_CORRELATION_KEY` docstring narrowed to `invoke_agent` / `chat`; trace-context cross-reference note added for `execute_tool` linkage | This session apply-pass arc |
| `harness-od/tests/test_otel_genai_base.py:258-260` | NO change owed — test asserts constant value only | n/a |
| `Implementation_Plan_Operational_Discipline_v2_20.md` U-OD-04 unit | NO change owed — AC #5 covers constant-value test which is unaffected by the §4.4 doc narrowing | n/a |
| `Spec_Harness_Runtime_v1.md` / CP spec / AS spec / CXA / ADR / ADD / PRD / harness-runtime impl / OD plan beyond U-OD-04 | NO change owed — no downstream artifact cites §4.4 hierarchy scope (verified via grep this session) | n/a |
| `Project_Workflow_v1_8.md` | NO change owed at v1.20 — discipline-validation observation at §"Adjacent observations" (h) is informational | n/a |

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.20 (Fidelity-pure canonical-reading amendment closing v1.19 §"Adjacent observations" finding (d) — §C-OD-04 §4.4 against OTel 1.41.0 archived text — as **CLOSED-via-narrowing-hierarchy-claim** 2026-05-27; NEW §1 canonical-reading amendment table dropping `execute_tool` from the §4.4 hierarchy claim + §2 finding-closure refresh + §3 cross-artifact cite-cascade disposition; co-published with helper docstring narrowing; v1.19 + earlier files PRESERVED VERBATIM per delta-only-spec-file convention) |
| Trigger | v1.19 §"Adjacent observations" finding (d) re-evaluation per user-routed "Proceed to next recommended action" 2026-05-27 (session continuation from v1.19 publication); pre-substantive advisor pass discriminated audit-scope discipline (verify §4.4 is sole site of execute_tool inclusion + verify OTel-derived vs OD-authored framing) BEFORE classifying as stance question; both discriminators verified — §4.4 line 301 is sole site; OTel does NOT canonicalize "hierarchy correlation key" framing — amendment is doc-hygiene under mirror-OTel stance |
| Supersedes | v1.19 §"Adjacent observations" finding (d) "Carried verbatim from v1.16 → v1.17 → v1.18 → v1.19; v1.19 does NOT touch this carry per FM-2 single-focus arc scope" framing — superseded at v1.20 §1.1 narrowing |
| Scope of revision | NARROW: NEW §1 canonical-reading amendment table narrowing §4.4 hierarchy claim from `{invoke_agent, chat, execute_tool}` to `{invoke_agent, chat}` per OTel 1.41.0 execute_tool span attribute table audit + §2 finding-closure refresh + §3 cross-artifact cite-cascade disposition. Co-publication: helper docstring at `HIERARCHY_CORRELATION_KEY` narrowed + workspace CLAUDE.md OD spec row bump. ZERO contract change; ZERO signature change; ZERO acceptance-criterion change at C-OD-04 (AC #5 is constant-value test only); ZERO behavior change at production emission (harness emits ZERO `gen_ai.conversation.id` at any span per v1.19 finding (g)). |
| Contract change | None. Fidelity-pure canonical-reading amendment narrowing a doc-level hierarchy claim. The cardinality-safe-restriction at §4.4 is PRESERVED VERBATIM. |
| Cross-axis cascade | ZERO at spec semantics layer. Cross-artifact cite-cascade disposition at v1.20 §3 documents 5 sites — 2 co-published at this arc (helper docstring + workspace CLAUDE.md); 3 confirmed NO-change (helper test constant-value-only, OD plan AC #5 constant-value-only, downstream artifacts no §4.4 hierarchy-scope cite). |
| Authority anchor | OTel GenAI semantic conventions 1.41.0 archived text at `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-agent-spans.md` (raw-fetched 2026-05-27 via `gh api`; cached at `$CLAUDE_JOB_DIR/gen-ai-agent-spans-v1.41.0.md`) + `gen-ai-spans.md` execute_tool span attribute table (lines 612-621 at v1.41.0; cached at `$CLAUDE_JOB_DIR/gen-ai-spans-v1.41.0.md`). Per-attribute audit verdict at v1.20 §1.1 mirrors the archived per-span attribute tables byte-exact. |
| Predecessor | v1.19 (Substantive canonical-reading amendment — per-attribute tier-assignment audit; Tension 004 D-3b CLOSED-as-verified-MATCH) |
| Successor | v1.21 (next operator-discretion arc — candidates: v1.20 finding (b) §8.4.2 anticipated cases; (d) workflow-grammar discipline canonicalization; (e) `gen_ai.provider.name` stability tier divergence; (f) `gen_ai.conversation.id` declared-but-not-emitted divergence routing; (g) `server.port` + `server.address` declared-but-not-emitted divergence routing; (i) OD-authored synthesis layer footer at §4.4) |
| Advisor application | 18th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` — pre-substantive advisor pass redirected from premature stance-question framing to two verification steps (§4.4 sole-site grep + OTel-derived-vs-OD-authored framing check). Both checks discriminated cleanly: §4.4 line 301 is sole site (doc-hygiene scope); OTel does NOT canonicalize "hierarchy correlation key" framing (OD-authored synthesis layer); mirror-OTel narrowing is unambiguous. Advisor declined further calls on this audit ("Don't call advisor again on this audit unless step 1 or 2 surfaces a real surprise. You have the v1.18 §5 discipline; use it on yourself.") — discipline-self-application succeeded. |
| Pattern catalogue | Second prospective application of v1.18 §5 strengthened discipline at substantive-amendment arc (FIRST was at v1.19); operationally validated continues. NEW pattern surfaced at v1.20 §"Adjacent observations" (i): OD-authored synthesis layer atop OTel per-span attribute declarations; documentable axis-discipline finding distinct from per-attribute audit findings. |
