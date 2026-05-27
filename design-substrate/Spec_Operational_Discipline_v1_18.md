# Spec: Operational Discipline — v1.18 (delta over v1.17)

---

## Change-note (v1.17 → v1.18)

**Scope of revision.** Fidelity-pure citation-correction patch closing v1.17 §"Adjacent observations" finding (g) — `_PROVIDER_OPERATIONS` value-space non-conformance to §4.2 operation enum — as **CLOSED-as-resolved-at-production-commit-ca5674b** 2026-05-26 + finding (h) — `provider_name` value-space partial-conformance to OTel 1.41.0 known-values enum — as **CLOSED-NOT-A-DEFECT-per-fork-doc-§10** (OTel `type: members:` declaration without `allow_custom_values: false` flag is open-known-values discipline; `ollama` emission is fully conformant; the prior framing was based on misreading OTel's `type: members:` shape as a closed enum).

**Distinctive lineage finding.** Both (g) and (h) were authored FRESH at v1.17 (this session, 2026-05-26 — same session as v1.17 publication) WITHOUT empirical verification at authoring time. The defects had been resolved at commits `ca5674b` (finding (g) — 2026-05-26 19:45 -0600) + fork doc `class_1_fork_genai_span_name_four_way_drift.md` §10 (finding (h) — same session) BEFORE the v1.17 amendment text was written. Empirical re-litigation this arc: production at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:502-504` carries inline closure note `# Finding (g) RESOLVED at this binding (was: API method names not in §4.2 enum — messages.create / chat.completions / chat)`; production grep at HEAD `a1215ba` confirms ZERO `dict[str, str]` typing of `_PROVIDER_OPERATIONS` (current type is `dict[str, GenAiOperation]` with all 3 providers mapped to `GenAiOperation.CHAT`). Fork doc §10 documents (h) closure via OTel `type: members:` open-known-values discipline + production `provider_name` cardinality 3 ≤ 20 within OD spec C-OD-04 line 664 bound.

**Authoring-time stale carry — NEW meta-pattern.** Distinct from prior catalogued stale-carry-text dispositions:

- v1.15 phantom-as-described — inherited carry; defect never existed in framed shape
- v1.16 stale-carry-with-real-but-different-shape — inherited carry; defect existed but framing predicted wrong shape
- v1.17 resolved-but-carry-stale — inherited carry; defect existed at vN authoring but resolved at downstream commit without carry-text refresh
- **v1.18 authoring-time stale carry (NEW)** — **self-authored carry**; carry-text was stale at the moment of writing because the underlying production state / fork doc closure was not empirically verified at authoring time. The carry was generated against an unverified framing of "this is a known carry-forward defect" without checking whether the defect had already been resolved before the arc opened.

**Lineage discriminator.** The first three patterns operate on INHERITED carries (carries propagated from prior versions). The fourth pattern operates on SELF-AUTHORED carries (carries generated NEW at the current version against an unverified framing). The fourth pattern is structurally more serious because the discipline gap is at the authoring layer, not the inheritance layer — strengthening the "at fork-arc opening empirically verify EVERY claim" discipline (v1.16/v1.17 candidate at OD v1.16 §"Adjacent observations" (g) carry / v1.17 §"Adjacent observations" (f) carry) to "at EVERY §Adjacent observations entry authoring (inherited OR new)" closes the fourth pattern's lineage source.

**Empirical posture (load-bearing).** Production grep at HEAD `a1215ba` this session:

- `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:497-509` → `_PROVIDER_OPERATIONS: dict[str, GenAiOperation]` typed enum binding; all 3 providers (`anthropic` / `openai` / `ollama`) mapped to `GenAiOperation.CHAT` per §4.2 enum.
- `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:502-504` → inline production comment `# Finding (g) RESOLVED at this binding (was: API method names not in §4.2 enum — messages.create / chat.completions / chat)`.
- Fork doc `.harness/class_1_fork_genai_span_name_four_way_drift.md` §9 → declares finding (g) RESOLVED at ca5674b (commit verified at git log; commit message documents pre-arc state `dict[str, str]` with API method names → post-arc state `dict[str, GenAiOperation]` with §4.2 enum members; 27/27 dispatch tests + 773/773 harness-od tests + pyright strict 0 errors at commit time).
- Fork doc `.harness/class_1_fork_genai_span_name_four_way_drift.md` §10 → declares finding (h) CLOSED-NOT-A-DEFECT via OTel `type: members:` open-known-values discipline + `gen_ai.provider.name` cardinality bound (3 ≤ 20 per OD spec C-OD-04 line 664).

The (g) defect no longer exists at production; the (h) defect was never a defect per OTel canonical-reading correction. Both stale-carry closures.

**Routing.** Per workspace `CLAUDE.md` §4.3 + I-1 byte-exact discipline + v1.17 phantom-closure precedent: v1.18 is a NEW delta file authoring §1 canonical-reading amendment table closing finding (g) + (h) + §2 finding-closure-disposition refresh + §3 cross-artifact cite-cascade disposition (lighter than v1.17 §3 — only runtime spec v1.27 top adjacent-observation refresh owed; workspace CLAUDE.md row bumps; no other artifacts cite (g)/(h) directly per session-scoped surfacing) + §5 NEW meta-pattern catalogue (authoring-time stale carry, sibling-but-stronger than v1.17 §5 resolved-but-carry-stale). v1.2-v1.17 PRESERVED VERBATIM per delta-only-spec-file convention.

**No fork doc filed.** Per workspace precedent + conclusive empirical posture (production self-documents (g) closure at inline comment; fork doc §10 self-documents (h) closure); the upstream class_1_fork_genai_span_name_four_way_drift.md fork doc IS the canonical authority for both closures — re-using it for the carry-text disposition refresh is the correct routing target (not a new fork doc).

---

## §1 Canonical-reading amendment table (v1.18 NEW)

Per delta-only-spec-file convention, the v1.2 through v1.17 file bodies are PRESERVED VERBATIM. The following table maps every carry-text site for findings (g) + (h) to its corrected canonical reading.

### §1.1 Finding (g) — `_PROVIDER_OPERATIONS` value-space non-conformance

The v1.17 §"Adjacent observations" finding (g) framing — `_PROVIDER_OPERATIONS` dict values `messages.create` / `chat.completions` / `chat` are API method names, NOT §4.2 operation enum values — was correct at v1.12 amendment authoring time (2026-05-26 morning; finding (f) of v1.12 sibling-flagged) but was resolved at producer-side commit `ca5674b` (2026-05-26 19:45 -0600). The v1.17 publication this session re-authored the finding as a fresh carry without empirical-grep verification of `_PROVIDER_OPERATIONS` typing at HEAD; this was a discipline gap (authoring-time stale carry). The canonical reading at v1.18:

| Site | v1.17 carry-text | Canonical reading at v1.18 |
|---|---|---|
| v1.17 §"Adjacent observations" (g) — "NEW at v1.17 — `_PROVIDER_OPERATIONS` value-space non-conformance to §4.2 operation enum... Surfaced as v1.17 finding (g); NOT patched per FM-2 single-focus arc scope; candidate for future operator-routed arc." | "Surfaced as v1.17 finding (g)" + "NOT patched per FM-2" + "candidate for future operator-routed arc" | **CLOSED-as-resolved-at-ca5674b** — empirical-grep at production confirms `_PROVIDER_OPERATIONS: dict[str, GenAiOperation]` typed enum binding at `harness-runtime/.../llm_dispatch.py:497-509`; all 3 providers map to `GenAiOperation.CHAT` per §4.2 enum; inline production comment at line 502-504 self-documents closure; fork doc `class_1_fork_genai_span_name_four_way_drift.md` §9 declares (g) RESOLVED. ZERO further apply-pass arc owed. |
| v1.17 §"Filing footer" Successor row — "candidates: v1.17 finding (g) `_PROVIDER_OPERATIONS` value-space non-conformance to §4.2 enum" | "candidate" | Finding (g) **CLOSED-as-resolved-at-ca5674b** at v1.18. Removed from successor-arc candidate list. |
| Runtime spec v1.27 top change-note "Adjacent observation (NOT patched per FM-2)" — "Production at `_PROVIDER_OPERATIONS` dict... maps provider name to API method name... NOT to OTel GenAI semconv §4.2 operation enum values... This is a pre-existing defect surfaced as adjacent finding (g)... NOT patched at this R1 arc; owed at separate apply-pass arc." | "currently maps to API method name" + "NOT patched at this R1 arc; owed at separate apply-pass arc" | **CLOSED-as-resolved-at-ca5674b** — same closure as v1.17 finding (g). Co-published this arc: runtime spec v1.29 change-note (NEW) refreshing the v1.27 top adjacent-observation carry-text disposition via canonical-reading amendment table. |

### §1.2 Finding (h) — `provider_name` value-space partial-conformance

The v1.17 §"Adjacent observations" finding (h) framing — `anthropic` + `openai` conformant to OTel 1.41.0 `gen_ai.provider.name` known-values enum; `ollama` not in 1.41.0 enum, hence "value-space partial-conformance" — was based on misreading OTel's `type: members:` declaration as a closed enum. Empirical verification at OTel 1.41.0 archived spec `model/gen-ai/registry.yaml` (verified 2026-05-26 via raw GitHub fetch per fork doc §10) confirms `type: members:` without `allow_custom_values: false` flag is open-known-values discipline; `ollama` is a valid custom value. The v1.17 publication this session re-authored the finding as a fresh carry without empirical-verification of the OTel canonical reading at the time; this was a discipline gap (authoring-time stale carry). The canonical reading at v1.18:

| Site | v1.17 carry-text | Canonical reading at v1.18 |
|---|---|---|
| v1.17 §"Adjacent observations" (h) — "NEW at v1.17 — `provider_name` value-space partial-conformance to OTel 1.41.0 `gen_ai.provider.name` known-values enum. Per commit `115387b` finding (h): `anthropic` + `openai` conformant; `ollama` not in 1.41.0 enum. Surfaced as v1.17 finding (h); NOT patched per FM-2 single-focus arc scope." | "partial-conformance" + "`ollama` not in 1.41.0 enum" + "NOT patched per FM-2" | **CLOSED-NOT-A-DEFECT-per-fork-doc-§10** — OTel 1.41.0 `type: members:` declaration without `allow_custom_values: false` flag is open-known-values discipline (custom values tolerated when no listed value applies); `note:` language is SHOULD + "instrumentation's best knowledge" (SHOULD-not-MUST + best-knowledge = open-known-values); OD spec C-OD-04 line 664 frames `gen_ai.provider.name` as "bounded (per-provider enumeration; expected ≤20 across all providers)" cardinality-bounded NOT closed-enum (conformant with OTel's open shape); production cardinality at HEAD = 3 ≤ 20 (within OD spec bound). ZERO further apply-pass arc owed. |

**Adjacent observation surfaced at fork doc §10 (i) NOT-patched-here.** OTel 1.41.0 declares `gen_ai.provider.name` as `stability: development` at both the attribute-level AND every member-level (including `anthropic` + `openai` which production also emits). OD spec C-OD-04 §4.3 classifies the same attribute as Required (Stable) tier (always-emit per OD emission-posture discipline). The OD-spec tier classification is OD's own emission-posture discipline (independent of OTel's stability metadata); the divergence is at the spec-narrative layer, not the wire-protocol layer. Routing: future OD spec doc-hygiene pass MAY add a footer clarifying that OD's Required (Stable) tier classification ≠ OTel attribute stability declaration. Surfaced as v1.18 §"Adjacent observations" finding (g) NEW (Class 3 informational); NOT patched per FM-2.

---

## §2 Finding-closure-disposition refresh

**Closed-as-resolved-at-production-commit-ca5674b.** v1.17 §"Adjacent observations" finding (g) is now closed at v1.18 §1.1 canonical-reading amendment table.

**Closed-not-a-defect-per-fork-doc-§10.** v1.17 §"Adjacent observations" finding (h) is now closed at v1.18 §1.2 canonical-reading amendment table.

**Disposition at v1.18.** Findings (g) + (h) are CLOSED. Removed from v1.18 §"Adjacent observations" carry; no longer deferred apply-pass arcs.

---

## §3 Cross-artifact cite-cascade disposition (v1.18 NEW)

| Artifact | Site | Carry-text framing | Disposition at v1.18 |
|---|---|---|---|
| `Spec_Harness_Runtime_v1.md` (v1.27 lineage) | Top change-note v1.27 "Adjacent observation (NOT patched per FM-2)" | "...sibling to OD spec v1.12 §"Adjacent observations" (f)... NOT patched at this R1 arc; owed at separate apply-pass arc" | **CLOSED-as-resolved-at-ca5674b** at v1.18 §1.1 row 3. Refreshed via runtime spec v1.29 NEW change-note + canonical-reading amendment table (co-publication this arc). |
| Workspace `CLAUDE.md` (worktree root) §2.3 OD spec + runtime spec rows | v1.17 + v1.28 row-text | v1.17/v1.28 narrative | Bumped to v1.18 + v1.29 at co-publication commit this arc with change-note narrative referencing v1.18 §"Filing footer" + runtime v1.29 §"Filing footer". |
| Fork doc `class_1_fork_genai_span_name_four_way_drift.md` | §9 (g) closure + §10 (h) closure | (g) "Commit anchor: [filled at commit time]" + §10 "Commit anchor: [filled at commit time]" | NO change owed at v1.18 — fork doc IS canonical authority for both closures; this OD spec v1.18 cites the fork doc as authority anchor without modifying the fork doc itself. |

ZERO other cite-cascade sites (the v1.17 (g)+(h) carry-text was session-scoped surfacing without propagation to CXA / AS spec / OD plan / harness-* CLAUDE.md / runtime spec body — verified via grep this session).

---

## §4 Sections preserved verbatim at v1.18

Per delta-only-spec-file convention + FM-2 no-extension discipline + fidelity-pure citation-correction patch scope, the v1.18 amendment touches ONLY the NEW §1 canonical-reading amendment table + §2 finding-closure-disposition refresh + §3 cross-artifact cite-cascade disposition + §5 meta-pattern catalogue. The following sections are PRESERVED VERBATIM from their authoring versions:

- **§C-OD-04 §4.1** (v1.12-lineage span-name 2-component format per D-1 R2)
- **§C-OD-04 §4.2** (v1.2-lineage operations enum; v1.16 §1.1 canonical reading applied)
- **§C-OD-04 §4.3** (v1.2-lineage attribute tiers; v1.16 §1.2 canonical reading applied; v1.17 §1.2 confirms full conformance at production)
- **§C-OD-04 §4.4** (v1.2-lineage; not in scope at any fork to date)
- **§C-OD-04 §4.5** (v1.2-lineage; verified MATCH at v1.16 §1.4)
- **§C-OD-05 §5.1 rows 1-15** (v1.2-lineage; v1.13 row 5 sub-note + v1.15 §1 canonical reading + v1.14 §8.4 cross-namespace ingestion rule preserved verbatim)
- **§C-OD-05 §5.2 + §5.3** (ingestion-posture invariants)
- **§C-OD-06 through §C-OD-33** (all v1.2-v1.17 lineage content preserved per delta-only-spec-file convention)
- **All v1.3 through v1.17 substantive amendments**

---

## §5 Meta-pattern catalogue: authoring-time stale carry (v1.18 NEW)

**Definition.** A self-authored §"Adjacent observations" entry whose carry-text disposition is stale at the moment of writing because the underlying production state / fork doc closure / cross-artifact resolution was not empirically verified at authoring time. The carry-text is generated against a presumed-correct framing (often inherited mental model from earlier in the same session or from an unverified commit message) without the empirical-grep verification that the discipline candidate enumerated at OD v1.16/v1.17 §"Adjacent observations" requires.

**Lineage discriminator from v1.17 §5 patterns.** The first three patterns operate on INHERITED carries; the fourth pattern operates on SELF-AUTHORED carries:

| Pattern | Source layer | Discovery vector | Closure shape |
|---|---|---|---|
| v1.15 phantom-as-described | Inherited carry | Empirical-grep contradicts framed defect description | CLOSED-as-phantom |
| v1.16 stale-carry-with-real-but-different-shape | Inherited carry | Empirical-grep surfaces defect at different shape than framed | CLOSED-as-resolved-via-re-litigation (corrective shape) |
| v1.17 resolved-but-carry-stale (inherited variant) | Inherited carry | Empirical-grep confirms defect resolved at commit C before carry-text refresh at vN+1/+2/etc. | CLOSED-as-resolved-at-{commit} |
| **v1.18 authoring-time stale carry (NEW)** | **Self-authored carry** | Empirical-grep at next-session re-litigation confirms carry was stale at the moment it was written | CLOSED-as-resolved-at-{commit} OR CLOSED-NOT-A-DEFECT-per-{source} (depending on closure lineage of the resolved defect) |

**Worked example: v1.17 (g) + (h).** Both findings were authored at v1.17 publication this session (2026-05-26) — surfaced as "NEW at v1.17" in the §"Adjacent observations" table. Empirical-grep at next-substantive-work re-litigation this session (same session, opened against user-routed "work on adjacent finding (g)" directive) immediately surfaced:

- (g) defect already resolved at commit `ca5674b` 5 minutes after the related (f) closure commit `115387b`; production carries inline closure note at `llm_dispatch.py:502-504` that I missed when authoring v1.17.
- (h) defect already closed-not-a-defect at fork doc `class_1_fork_genai_span_name_four_way_drift.md` §10 with OTel canonical-reading empirical verification (2026-05-26).

Both stale at the moment of v1.17 §"Adjacent observations" authoring.

**Common ancestor with v1.15/v1.16/v1.17 patterns.** All four patterns are species of "stale carry-text disposition" — a defect-carry framing that has decayed against empirical state without refresh. The v1.18 pattern strengthens the lineage by showing the decay can occur at the authoring moment, not just at the inheritance moment.

**Discipline strengthening (v1.18 NEW).** The discipline candidate enumerated at OD v1.16 §"Adjacent observations" (g) → v1.17 §"Adjacent observations" (f) — "at fork-arc opening, empirically verify EVERY claim in a carry-text BEFORE treating the carry as actionable in the framed shape" — is upgraded at v1.18 to:

> **At EVERY §Adjacent observations entry authoring (inherited OR new), empirically verify the entry against production state / fork doc closures / cross-artifact resolutions at the moment of writing. The verification step is load-bearing at authoring time, not just at fork-arc opening time. Apply to self-authored entries AND inherited carries equally.**

**Discipline-candidate routing.** The strengthened discipline is a workflow-grammar-level finding owed at `Project_Workflow_v1_8.md` revision arc if operator routes. Carried at v1.18 §"Adjacent observations" finding (f) refresh (sibling-strengthen to v1.17 finding (f) carry).

**Mechanism for closure-commit ↔ spec-carry-text propagation gap.** Both (g) at `ca5674b` and (h) at fork doc §10 documented their closures inline (production code comment + fork doc section). The v1.17 authoring missed both because the authoring discipline did not include "read the production code at the cited line numbers AND read the upstream fork doc closure sections BEFORE writing the carry-text." A future workflow revision could mandate empirical-verification steps as part of §"Adjacent observations" authoring (e.g., "grep production at the cited file:line for inline closure comments; grep fork doc for §"Finding XX RESOLVED" sections at the carrying defect's name").

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **v1.17 finding (g) — CLOSED-as-resolved-at-ca5674b at v1.18 §1.1 + §2.** Removed from "Adjacent observations" carry.

(b) **v1.17 finding (h) — CLOSED-NOT-A-DEFECT-per-fork-doc-§10 at v1.18 §1.2 + §2.** Removed from "Adjacent observations" carry.

(c) **v1.17 finding (b) — §8.4.2 anticipated cases empirical-verification.** Carried verbatim from v1.16 → v1.17. Audit this session 2026-05-26: production grep for the 3 anticipated cases (`topology.*` on `sandbox.exit`, `audit.*` on `hitl.invocation.responded`, `validator.*` on `mcp.tool.call`) returns ZERO production hits at HEAD `a1215ba` — anticipated cases have NOT materialized; carry remains genuine as deferred-monitor (verify these cases don't silently materialize). v1.18 does NOT touch this carry.

(d) **v1.17 finding (c) — v1.15 §15.2 vs §15.4 split informational.** Carried verbatim from v1.16 → v1.17. Audit this session 2026-05-26: AS spec v1.7 unchanged since v1.17 (no `git log --since="2026-05-26"` AS spec hits in audit grep); carry remains genuine as informational. v1.18 does NOT touch this carry.

(e) **v1.17 finding (d) — §C-OD-04 §4.3 per-attribute tier-assignment audit against 4-tier table.** Carried verbatim from v1.16 → v1.17. Audit this session 2026-05-26: NO tier-assignment audit performed in any commit since v1.16; carry remains genuine as deferred-audit. v1.18 does NOT touch this carry.

(f) **v1.17 finding (e) — §C-OD-04 §4.4 against OTel 1.41.0 archived text.** Carried verbatim from v1.16 → v1.17. Audit this session 2026-05-26: NO §4.4 audit performed in any commit since v1.16; carry remains genuine as deferred-audit. v1.18 does NOT touch this carry.

(g) **v1.17 finding (f) — workflow-grammar reconciliation discipline candidate at `Project_Workflow_v1_8.md`** — STRENGTHENED at v1.18 §5 to include authoring-time empirical-verification. Carried verbatim from v1.16 → v1.17. Audit this session 2026-05-26: `Project_Workflow_v1_8.md` unchanged since v1.16 (no `git log --since="2026-05-26"` hits); carry remains genuine as deferred-discipline-candidate; v1.18 §5 strengthens the candidate framing (authoring-time + inherited carries both subject to empirical-verification discipline). v1.18 does NOT touch the upstream `Project_Workflow_v1_8.md` artifact.

(h) **NEW at v1.18 — `gen_ai.provider.name` stability tier divergence at fork doc §10 sub-finding (i).** OTel 1.41.0 declares `gen_ai.provider.name` as `stability: development`; OD spec C-OD-04 §4.3 classifies same attribute as Required (Stable) tier. Spec-narrative-layer divergence (OD's emission-posture discipline ≠ OTel attribute-stability declaration); not a wire-protocol divergence. Future OD spec doc-hygiene pass MAY add footer clarifying the distinction. Class 3 informational; NOT patched per FM-2 single-focus arc scope.

---

## Downstream artifacts requiring absorption at follow-on arcs

| Artifact | Required change | Owner |
|---|---|---|
| Workspace `CLAUDE.md` §2.3 OD spec row | v1.17 → v1.18 row update with v1.18 change-note narrative; v1.17 + earlier lineage preserved | This session apply-pass arc |
| Workspace `CLAUDE.md` §2.3 runtime spec row | v1.28 → v1.29 row update with v1.29 change-note narrative; v1.28 + earlier lineage preserved | This session apply-pass arc |
| `Spec_Harness_Runtime_v1.md` | NEW v1.29 change-note prepended; canonical-reading amendment table refreshing v1.27 top adjacent-observation finding (g) carry-text disposition; body text PRESERVED VERBATIM per delta-only convention | This session apply-pass arc |
| OD plan / CP spec / CP plan / AS spec / AS plan / CXA / ADR / ADD / PRD / harness-* helper code | NO change owed — divergences were session-scoped surfacing at v1.17 + production self-documents closures; ZERO cross-axis cascade beyond the cite-cascade disposition documented at v1.18 §3. | n/a |
| `Project_Workflow_v1_8.md` | NO change owed at v1.18 — discipline-candidate strengthening at v1.18 §5 is informational; routes to upstream workflow revision arc if operator routes (preserved as v1.18 §"Adjacent observations" finding (g)). | n/a |

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.18 (Fidelity-pure citation-correction patch closing v1.17 §"Adjacent observations" finding (g) as **CLOSED-as-resolved-at-production-commit-ca5674b** 2026-05-26 + finding (h) as **CLOSED-NOT-A-DEFECT-per-fork-doc-§10** 2026-05-26; NEW §1 canonical-reading amendment table + §2 finding closure + §3 cross-artifact cite-cascade disposition + §5 NEW meta-pattern catalogue **authoring-time stale carry**; v1.17 + earlier files PRESERVED VERBATIM per delta-only-spec-file convention) |
| Trigger | v1.17 §"Adjacent observations" findings (g) + (h) re-evaluation per user-routed adjacent-observation closure arc 2026-05-26 (session continuation from v1.17 publication; user directive "work on adjacent finding (g) _PROVIDER_OPERATIONS value-space non-conformance"); empirical-grep at HEAD `a1215ba` immediately confirmed (g) resolved at `ca5674b` (production self-documents closure at inline comment `llm_dispatch.py:502-504`) + (h) closed at fork doc §10 (OTel `type: members:` open-known-values discipline + cardinality bound) |
| Supersedes | v1.17 §"Adjacent observations" (g) + (h) "NEW at v1.17... NOT patched per FM-2... candidate for future operator-routed arc" framing — superseded per empirical-verification at HEAD discovery |
| Scope of revision | NARROW: NEW §1 canonical-reading amendment table closing (g) + (h) + §2 finding-closure-disposition refresh + §3 cross-artifact cite-cascade disposition + §5 NEW meta-pattern catalogue (authoring-time stale carry). Co-publication: runtime spec v1.29 NEW change-note refreshing v1.27 top adjacent-observation (g) carry-text disposition; workspace CLAUDE.md OD spec + runtime spec row bumps. ZERO contract change; ZERO signature change; ZERO acceptance-criterion change; ZERO behavior change. |
| Contract change | None. Fidelity-pure citation-correction patch. |
| Cross-axis cascade | ZERO at spec semantics layer. Cross-artifact cite-cascade disposition at v1.18 §3 documents 3 sites — 2 refreshed at this arc (runtime spec v1.29 + workspace CLAUDE.md); fork doc preserved verbatim (it IS the canonical authority for both closures). |
| Authority anchor | Commit `ca5674b77cc9a27bf223d7b0955d8ec648ca954e` (2026-05-26 19:45 -0600) — producer-side conform at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:497-509` typing `_PROVIDER_OPERATIONS: dict[str, GenAiOperation]` with all 3 providers mapped to `GenAiOperation.CHAT` per §4.2 enum; fork doc `class_1_fork_genai_span_name_four_way_drift.md` §9 (g) closure + §10 (h) closure |
| Predecessor | v1.17 (gen_ai.system stale-carry close + THIRD species of stale-carry-text disposition catalogued) |
| Successor | v1.19 (next operator-discretion arc — candidates: v1.18 finding (c) §8.4.2 anticipated cases empirical-verification; (d) §15.2 vs §15.4 split informational; (e) tier-assignment audit; (f) §4.4 audit; (g) workflow-grammar discipline candidate STRENGTHENED at v1.18 §5; (h) NEW `gen_ai.provider.name` stability tier divergence) |
| Advisor application | 16th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` — pre-substantive advisor pass confirmed the meta-pattern (both v1.17 (g)+(h) authored fresh this session were stale at moment of writing) + flagged audit-discipline broadening (audit ALL of v1.17 §"Adjacent observations" (b–h) before authoring v1.18; one corrective delta, not multiple sequential closures); empirical-verification audit this session confirmed (b)–(f) carries still genuine; (g)+(h) stale-as-described |
| Pattern catalogue | FOURTH species of stale-carry-text disposition catalogued at v1.18 §5 — sibling to v1.15 phantom + v1.16 different-shape + v1.17 resolved-but-carry-stale-inherited; common ancestor "stale carry-text disposition"; distinctive feature: source layer is SELF-AUTHORED carry rather than INHERITED carry; discipline strengthening upgrades "at fork-arc opening empirically verify EVERY claim" to "at EVERY §Adjacent observations entry authoring (inherited OR new) empirically verify" |
