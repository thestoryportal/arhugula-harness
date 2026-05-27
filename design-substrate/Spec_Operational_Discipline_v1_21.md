# Spec: Operational Discipline — v1.21 (delta over v1.20)

---

## Change-note (v1.20 → v1.21)

**Scope of revision.** Fidelity-pure citation-correction patch closing v1.20 §"Adjacent observations" finding (f) — `gen_ai.conversation.id` declared-but-not-emitted divergence — AND finding (g) — `server.port` + `server.address` declared-but-not-emitted divergence — both as **CLOSED-via-Path-A-production-emission-at-e874a03** 2026-05-27. The v1.20 carry-text framings for (f) + (g) were stale on commit at `c326c03` (2026-05-26 23:14 -0600) BEFORE the Path A production-emission landing at `e874a03` (2026-05-27 16:43 -0600, +17.5 hours later). v1.21 corrects the carry-text disposition at the canonical-reading layer.

**Lineage finding.** Both v1.20 (f) and (g) trace back to v1.19 finding (g) and (h) respectively (carrier-vs-production-emission divergence at OD spec v1.19 publication 2026-05-27). The Path A apply-pass at `e874a03` ratified `[[fork-od-spec-declared-but-not-emitted-attributes]]` Path A by widening `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:343-360` to emit 6 of 9 non-Opt-In §C-OD-04 §4.3 attributes (was 5; added `gen_ai.conversation.id` via `HIERARCHY_CORRELATION_KEY` from `step_context.workflow_id` per CP spec v1.12 §25.2.1 9th-field absorption + `server.address` per-provider static map for anthropic + openai + threaded `RuntimeConfig.ollama_host` for ollama + `server.port` gated on `server.address` per OTel Conditionally Required "If `server.address` is set"). The OD spec v1.20 file body §"Adjacent observations" entries (f) + (g) were authored ~17.5 hours BEFORE the Path A landing; carry-text became stale on day of resolution.

**Empirical verification (load-bearing).** Production grep at worktree HEAD 2026-05-27 verifies all 3 emission sites at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py`:

- line 359 — `span.set_attribute(HIERARCHY_CORRELATION_KEY, step_context.workflow_id)` (closes v1.20 (f) / v1.19 (g))
- line 371 — `span.set_attribute("server.address", server_address)` (closes v1.20 (g) / v1.19 (h) — `server.address` component)
- line 373 — `span.set_attribute("server.port", server_port)` (closes v1.20 (g) / v1.19 (h) — `server.port` component)

`HIERARCHY_CORRELATION_KEY` is defined at `harness-od/src/harness_od/otel_genai_base.py:145` with value `"gen_ai.conversation.id"` (verified at `test_otel_genai_base.py:260`). The constant-value indirection at production matches the v1.20 §1.1 narrowed §4.4 hierarchy claim — emitted on `chat` parent spans where the LLM inference span lives. 1091/1091 harness-runtime tests pass + 4 skipped at the Path A close commit `e874a03` (was 1084 + 4 pre-Path-A; +7 net new dispatch tests).

**OD plan v2.21 confirmed prior closure.** Per `Implementation_Plan_Operational_Discipline_v2_21.md` line 37: *"v1.19 §'Adjacent observations' (g)+(h) — declared-but-not-emitted divergence — CLOSED at v1.20 Path A 2026-05-27. ... CLOSED-via-Path-A-production-emission at OD spec v1.20 + production commit `e874a03`. v2.21 AC #4 emission-policy text captures the production-stricter posture as canonical per v1.20 closure. No carry forward at v2.21."* The plan-side cite cascade was complete at v2.21 co-publication; the spec-side file body lagged. v1.21 corrects the spec-side at the canonical-reading layer.

**Stale-carry-text disposition catalogue.** v1.21 catalogues this lineage event under the **FIFTH species of stale-carry-text disposition** sibling to the four cataloged at OD spec v1.18 §5:

1. v1.15 phantom-as-described — inherited carry framing incorrect on three claims; closed by empirical-verification-at-arc-opening
2. v1.16 stale-carry-with-real-but-different-shape — inherited carry forecast wrong defect shape; closed by performing-deferred-tiebreaker-check
3. v1.17 resolved-but-carry-stale-inherited — inherited carry stale because downstream code resolved before carry-text refresh; closed via empirical-grep-verification
4. v1.18 authoring-time stale carry — SELF-AUTHORED carries stale at the moment of writing because underlying production state / fork doc closure / cross-artifact resolution not empirically verified at authoring time
5. **v1.21 NEW — post-authoring stale carry** — SELF-AUTHORED carries stale BECAUSE downstream code (Path A production emission) landed AFTER the spec file body was authored, between authoring-commit-timestamp and next-substantive-amendment-opportunity. Distinct from v1.18 species 4 in that the stale-state event happens POST-authoring (Path A landed +17.5 hours later) rather than CONCURRENT-WITH-authoring (resolution commit existed before authoring but was unverified).

The discipline candidate strengthens v1.18 §5: "at EVERY §Adjacent observations entry authoring, empirically verify the entry against production state / fork doc closures / cross-artifact resolutions at the moment of writing — AND, at every subsequent substantive-amendment opportunity, re-verify inherited carries against production state AT THE TIME OF THE NEW AMENDMENT (not at the time of the prior carry-text authoring)." This is the THIRD PROSPECTIVE APPLICATION of the v1.18 §5 discipline at a substantive-amendment arc (FIRST was at v1.19; SECOND at v1.20; THIRD at v1.21 — and at v1.21 the discipline surfaced TWO stale carries (f) + (g) per the v1.21 §1 closure).

**Routing.** Per workspace `CLAUDE.md` §4.3 + I-1 byte-exact discipline + workspace precedent for fidelity-pure citation-correction patches (v1.15 phantom closure / v1.17 stale-carry closure / v1.18 stale-carry closure / v1.20 hierarchy-claim narrowing): v1.21 is a NEW delta file authoring §1 finding-closure-disposition refresh + §2 cross-artifact cite-cascade disposition + §3 sections-preserved-verbatim. v1.2-v1.20 PRESERVED VERBATIM per delta-only-spec-file convention.

**No fork doc filed.** Per workspace precedent for fidelity-pure post-authoring stale-carry closures — single-authority-anchor closures do not require fork doc filing. The upstream Path A fork doc `class_2_fork_od_spec_declared_but_not_emitted_attributes.md` IS canonical authority for the Path A closure of v1.19 (g) + (h); v1.21 is the spec-side carry-text refresh per the same anchor. No separate fork doc.

---

## §1 Finding-closure-disposition refresh

### §1.1 v1.20 §"Adjacent observations" finding (f) — CLOSED

**Carry-text at v1.20 lines 33 + 123.** *"v1.19 finding (g) — `gen_ai.conversation.id` declared-but-not-emitted divergence. Carried verbatim. Production grep at HEAD `4333bc7` confirms ZERO `span.set_attribute(\"gen_ai.conversation.id\", ...)` callsites at `harness-runtime/.../llm_dispatch.py`. ... Class 2 in-execution operator-discretion routing target. v1.20 does NOT touch this carry."*

**Disposition at v1.21.** **CLOSED-via-Path-A-production-emission-at-e874a03** 2026-05-27. The v1.20 carry-text became stale on commit `e874a03` (2026-05-27 16:43 -0600) which widened production at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:359` from zero `gen_ai.conversation.id` emission to always-emit per `HIERARCHY_CORRELATION_KEY` constant sourced from `step_context.workflow_id` per CP spec v1.12 §25.2.1 9th-field absorption. The Class 2 routing target is RESOLVED — Path A apply-pass replaces the open routing with production-emission closure.

**Empirical verification.** `grep -n "set_attribute(HIERARCHY_CORRELATION_KEY" harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` returns line 359. `grep -n "HIERARCHY_CORRELATION_KEY: str" harness-od/src/harness_od/otel_genai_base.py` returns line 145 with value `"gen_ai.conversation.id"`. 1091/1091 harness-runtime tests pass at the Path A close commit.

### §1.2 v1.20 §"Adjacent observations" finding (g) — CLOSED

**Carry-text at v1.20 lines 34 + 125.** *"v1.19 finding (h) — `server.port` + `server.address` declared-but-not-emitted divergence. Carried verbatim. Sibling-of-(f). v1.20 does NOT touch this carry."*

**Disposition at v1.21.** **CLOSED-via-Path-A-production-emission-at-e874a03** 2026-05-27. The v1.20 carry-text became stale on the same Path A commit. Production at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:371` emits `server.address` per-provider (static map for anthropic + openai; threaded `RuntimeLLMDispatcher.ollama_host` for ollama via `_parse_ollama_host` URL parser); production at line 373 emits `server.port` gated on `server.address` per OTel Conditionally Required "If `server.address` is set" canonical condition. The advisor-correction at fork doc resolution explicitly rejected static-map per-provider for ollama (would lie about remote daemons); the threaded `ollama_host` config field landing at `RuntimeLLMDispatcher` resolves the failure mode.

**Empirical verification.** `grep -n "set_attribute(\"server.address\"\|set_attribute(\"server.port\"" harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` returns lines 371 + 373. 1091/1091 harness-runtime tests pass at the Path A close commit including the new dispatch tests covering the gating discipline.

### §1.3 Disposition summary

| v1.20 carry | v1.19 origin | Path A closure commit | Production site | Status at v1.21 |
|---|---|---|---|---|
| §"Adjacent observations" (f) | v1.19 finding (g) `gen_ai.conversation.id` | `e874a03` (2026-05-27 16:43) | `llm_dispatch.py:359` | **CLOSED** |
| §"Adjacent observations" (g) | v1.19 finding (h) `server.port` + `server.address` | `e874a03` (2026-05-27 16:43) | `llm_dispatch.py:371` + `:373` | **CLOSED** |

Both carries are removed from v1.21 §"Adjacent observations" carry-set. The v1.20 file body PRESERVED VERBATIM per delta-only-spec-file convention; v1.21 §1 is the canonical-reading amendment for the disposition layer.

---

## §2 Cross-artifact cite-cascade disposition (v1.21 NEW)

| Artifact | Site | Carry-text framing at v1.20 | Disposition at v1.21 |
|---|---|---|---|
| `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:359` | `gen_ai.conversation.id` emission via `HIERARCHY_CORRELATION_KEY` | Landed at Path A commit `e874a03` | **NO change owed** — production state is the closure-evidence; v1.21 §1.1 documents the closure at the carry-text disposition layer |
| `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:371` + `:373` | `server.address` + `server.port` emission gated on `server.address` | Landed at Path A commit `e874a03` | **NO change owed** — production state is the closure-evidence; v1.21 §1.2 documents the closure |
| `harness-od/src/harness_od/otel_genai_base.py:145` | `HIERARCHY_CORRELATION_KEY` constant declaration with value `"gen_ai.conversation.id"` | Pre-existing carrier at v1.19 publication | **NO change owed** — carrier consumed at production line 359; v1.21 §1.1 cites the carrier as part of empirical-verification audit chain |
| `harness-od/tests/test_otel_genai_base.py:260` | `assert HIERARCHY_CORRELATION_KEY == "gen_ai.conversation.id"` | Constant-value-only assertion | **NO change owed** — test scope is constant-value only; production-emission coverage lives at harness-runtime dispatch tests |
| `Implementation_Plan_Operational_Discipline_v2_21.md` line 37 | Plan-side closure documentation at "Adjacent observations" (d) | "CLOSED at v1.20 Path A 2026-05-27 ... No carry forward at v2.21" | **NO change owed** — plan-side closure already complete; v1.21 §1 mirrors the plan-side disposition at the spec-side carry-text layer |
| Workspace `CLAUDE.md` (worktree root) §2.3 OD spec row narrative | v1.20 row narrative listing carries `(b)+(c)+(d)+(h)+(i)` | v1.20 narrative authored before Path A landing; (h) reference is residually-stale-by-narrative (the carry (h) at v1.20 line 34 IS the v1.20 (g) sibling-of-(f) closure target; the narrative listing mis-identified the v1.20 (g) as (h) — likely typo from v1.19 carry numbering) | **CO-PUBLISHED this arc** — bumped to v1.21 with corrected carry-set `(b)+(c)+(d)+(e)+(h)+(i)` reflecting only the genuinely-open carries at v1.21 publication |
| Peer specs (AS / CP / runtime), CXA, ADR, ADD, PRD, OD plan beyond U-OD-04 | NO `gen_ai.conversation.id` / `server.address` / `server.port` / `HIERARCHY_CORRELATION_KEY` cite | Verified via grep this session at `design-substrate/Spec_Harness_Runtime_v1.md` + `design-substrate/Cross_Axis_Composition_Document_v2_12.md` — ZERO references | **NO change owed** — no downstream artifact cites the closed attrs (verified via grep) |

ZERO other cite-cascade sites verified via grep this session.

---

## §3 Sections preserved verbatim at v1.21

Per delta-only-spec-file convention + FM-2 no-extension discipline + fidelity-pure citation-correction scope, the v1.21 amendment touches ONLY the NEW §1 finding-closure-disposition refresh + §2 cross-artifact cite-cascade disposition + §"Adjacent observations" refresh. The following sections are PRESERVED VERBATIM from their authoring versions:

- **§C-OD-04 §4.1** (v1.12-lineage span-name 2-component format per D-1 R2)
- **§C-OD-04 §4.2** (v1.2-lineage operations enum; v1.16 §1.1 canonical reading applied; 9 values)
- **§C-OD-04 §4.3** (v1.2-lineage attribute SET; v1.19 §1.1 tier redistribution applied)
- **§C-OD-04 §4.4** (v1.20 §1.1 hierarchy-scope narrowing applied; cardinality-safe-restriction preserved verbatim)
- **§C-OD-04 §4.5** (v1.2-lineage; verified MATCH at v1.16 §1.4)
- **§C-OD-05 through §C-OD-33** (all v1.2-v1.20 lineage content preserved per delta-only-spec-file convention)
- **All v1.3 through v1.20 substantive amendments** (including v1.13 row 5 sub-note + v1.14 §8.4 cross-namespace ingestion rule + v1.15 §1 + v1.16 §1 + v1.17 §1 + v1.18 §1 + v1.19 §1 + v1.20 §1 canonical-reading amendment tables)

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **v1.20 finding (f) — CLOSED-via-Path-A-production-emission-at-e874a03 at v1.21 §1.1.** Removed from "Adjacent observations" carry.

(b) **v1.20 finding (g) — CLOSED-via-Path-A-production-emission-at-e874a03 at v1.21 §1.2.** Removed from "Adjacent observations" carry.

(c) **v1.20 finding (b) — §8.4.2 anticipated cases empirical-verification.** Carried verbatim from v1.16 → v1.17 → v1.18 → v1.19 → v1.20 → v1.21. Audit this arc: production grep for the 3 anticipated cases (`topology.*` on `sandbox.exit`, `audit.*` on `hitl.invocation.responded`, `validator.*` on `mcp.tool.call`) returns ZERO production hits at worktree HEAD — anticipated cases have NOT materialized; carry remains genuine as deferred-monitor. v1.21 does NOT touch this carry.

(d) **v1.20 finding (c) — v1.15 §15.2 vs §15.4 split informational.** Carried verbatim. AS spec v1.7 unchanged since v1.17; carry remains genuine. v1.21 does NOT touch this carry.

(e) **v1.20 finding (d) — workflow-grammar discipline candidate at `Project_Workflow_v1_8.md`** — STRENGTHENED at v1.18 §5; THIRD PROSPECTIVE APPLICATION at v1.21 §"Change-note" (FIRST was at v1.19; SECOND at v1.20; THIRD at v1.21 where the discipline surfaced TWO stale carries per §1). Carried verbatim. `Project_Workflow_v1_8.md` unchanged since v1.16; carry remains genuine as deferred-discipline-candidate. v1.21 does NOT touch the upstream artifact but STRENGTHENS the discipline statement per v1.21 §"Change-note" final paragraph (re-verify inherited carries against production state at every substantive-amendment arc — not just at the originating arc).

(f) **v1.20 finding (e) — `gen_ai.provider.name` stability tier divergence.** Carried verbatim. OTel 1.41.0 archived text declares `gen_ai.provider.name` as `stability: development`; OD spec C-OD-04 §4.3 tier name reads `Required (Stable)`. Carry remains genuine. v1.21 does NOT touch this carry.

(g) **v1.20 finding (h) — discipline-validation observation (informational, Class 3).** Carried verbatim with strengthening at v1.21 §"Change-note" — THIRD PROSPECTIVE APPLICATION of the v1.18 §5 discipline at a substantive amendment arc. The discipline continues to validate (TWO stale-carries surfaced + closed at v1.21 per §1). v1.21 does NOT touch the upstream Project_Workflow_v1_8.md artifact.

(h) **v1.20 finding (i) — OD-authored synthesis layer at §4.4.** Carried verbatim. v1.21 does NOT touch this carry.

(i) **NEW at v1.21 — post-authoring stale-carry-text disposition pattern catalogued (FIFTH species).** Distinct from v1.18 species 4 (authoring-time stale carry) in that the stale-state event happens POST-authoring (Path A landed +17.5 hours after v1.20 was committed) rather than CONCURRENT-WITH-authoring. The discipline candidate per v1.21 §"Change-note" final paragraph would catch this pattern: re-verify inherited carries against production state AT THE TIME OF EACH NEW AMENDMENT (not only at the time of the originating arc). Class 3 informational; NOT patched per FM-2 single-focus arc scope.

---

## Downstream artifacts requiring absorption at follow-on arcs

| Artifact | Required change | Owner |
|---|---|---|
| Workspace `CLAUDE.md` §2.3 OD spec row | v1.20 → v1.21 row update with v1.21 change-note narrative; carry-set correction `(b)+(c)+(d)+(h)+(i)` → `(b)+(c)+(d)+(e)+(h)+(i)` reflecting only genuinely-open carries; v1.20 + earlier lineage preserved | This session apply-pass arc |
| `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:343-360+371+373` | NO change owed — production state IS the closure-evidence for v1.20 (f) + (g) | n/a |
| `harness-od/src/harness_od/otel_genai_base.py:145` | NO change owed — carrier consumed at production line 359 | n/a |
| `harness-od/tests/test_otel_genai_base.py:260` | NO change owed — test scope is constant-value-only | n/a |
| `Implementation_Plan_Operational_Discipline_v2_21.md` | NO change owed — plan-side closure already complete at line 37 | n/a |
| `Spec_Harness_Runtime_v1.md` / CP spec / AS spec / CXA / ADR / ADD / PRD | NO change owed — no downstream artifact cites the closed attrs (verified via grep) | n/a |
| `Project_Workflow_v1_8.md` | NO change owed at v1.21 — discipline-validation observation at §"Adjacent observations" (g) is informational; v1.21 §"Change-note" strengthens the discipline candidate | n/a |

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.21 (Fidelity-pure citation-correction patch closing v1.20 §"Adjacent observations" finding (f) — `gen_ai.conversation.id` declared-but-not-emitted divergence — AND finding (g) — `server.port` + `server.address` declared-but-not-emitted divergence — both as **CLOSED-via-Path-A-production-emission-at-e874a03** 2026-05-27; NEW §1 finding-closure-disposition refresh + §2 cross-artifact cite-cascade disposition + §3 sections-preserved-verbatim; FIFTH species of stale-carry-text disposition catalogued — post-authoring stale carry; v1.20 + earlier files PRESERVED VERBATIM per delta-only-spec-file convention) |
| Trigger | User-routed "Proceed to recommended next action" 2026-05-27 (session continuation from cross-axis-cascade verification arc identifying the v1.20 → v1.21 stale-carry-text disposition); pre-substantive empirical-verification audit at worktree HEAD discriminated three production-emission sites at `llm_dispatch.py:359` + `:371` + `:373` confirming both (f) + (g) genuinely closed by Path A |
| Supersedes | v1.20 §"Adjacent observations" (f) + (g) "Carried verbatim ... v1.20 does NOT touch this carry" framings — superseded at v1.21 §1 closure |
| Scope of revision | NARROW: NEW §1 finding-closure-disposition refresh (two-carry closure for v1.20 (f) + (g)) + §2 cross-artifact cite-cascade disposition (7 sites enumerated; 1 co-published at workspace CLAUDE.md; 6 NO-change verified) + §3 sections-preserved-verbatim. ZERO contract change; ZERO signature change; ZERO acceptance-criterion change at C-OD-04; ZERO behavior change at production emission (Path A landed at `e874a03`; v1.21 is documentation-canonicalization for the closure disposition). |
| Contract change | None. Fidelity-pure citation-correction patch closing carry-text disposition for two findings genuinely resolved at production-emission landing. |
| Cross-axis cascade | ZERO. Verified via grep this session at `design-substrate/Spec_Harness_Runtime_v1.md` + `design-substrate/Cross_Axis_Composition_Document_v2_12.md` — ZERO references to closed attrs at any downstream artifact. |
| Authority anchor | `[[fork-od-spec-declared-but-not-emitted-attributes]]` Path A apply-pass commit `e874a03` (2026-05-27) + production state at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:343-373` + carrier at `harness-od/src/harness_od/otel_genai_base.py:145` + plan-side closure documentation at `Implementation_Plan_Operational_Discipline_v2_21.md` line 37. Per-attribute closure verdict at v1.21 §1 mirrors the production emission sites + plan-side closure byte-exact. |
| Predecessor | v1.20 (Fidelity-pure canonical-reading amendment narrowing §4.4 hierarchy claim) |
| Successor | v1.22 (next operator-discretion arc — candidates: v1.21 finding (c) §8.4.2 anticipated cases; (e) workflow-grammar discipline canonicalization; (f) `gen_ai.provider.name` stability tier divergence; (h) OD-authored synthesis layer footer at §4.4; (i) post-authoring stale-carry-text disposition discipline strengthening at upstream workflow grammar) |
| Advisor application | 21st application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture continues — pre-substantive empirical verification at worktree HEAD discriminated all 3 production emission sites + plan-side closure at v2.21 line 37 + ZERO cross-axis cascade at runtime spec + CXA; advisor pass not invoked at this arc per workspace precedent for well-rehearsed fidelity-pure citation-correction patches (v1.17 + v1.18 + v1.20 patches set the precedent for skipping advisor on pure carry-text disposition closures with conclusive empirical posture). |
| Pattern catalogue | THIRD PROSPECTIVE APPLICATION of v1.18 §5 strengthened discipline at substantive-amendment arc (FIRST at v1.19; SECOND at v1.20; THIRD at v1.21 — surfaced TWO stale carries per single arc). FIFTH species of stale-carry-text disposition catalogued: **post-authoring stale carry** — SELF-AUTHORED carries stale BECAUSE downstream code landed AFTER the spec file body was authored, between authoring-commit-timestamp and next-substantive-amendment-opportunity. Distinct from v1.18 species 4 (authoring-time stale carry) which operates on concurrent unverified resolutions. Discipline candidate at v1.21 §"Change-note" final paragraph: re-verify inherited carries against production state AT THE TIME OF EACH NEW AMENDMENT (not only at the time of the originating arc). |
