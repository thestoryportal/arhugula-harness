# Class 1 fork — Tension 004 D-2 / D-3 re-litigation against OTel 1.41.0 archived text

**Filed:** 2026-05-26 (post OD spec v1.15 finding-(a) closure arc; arose from §"Adjacent observations" carry (b) re-evaluation per session resumption from checkpoint `20260526-223000-od-spec-v1-15-finding-a-phantom-close.md`)
**Status:** ✅ RATIFIED-AND-APPLIED 2026-05-26 (status-line refreshed 2026-05-27) — SECOND tension re-litigation in workspace history (after D-1 R2); OD spec v1.16 NEW §1.1 operations enum 7 → 9 values (add `invoke_workflow` + `retrieval` per OTel 1.41.0 archived text) + §1.2 attribute tiers 3 → 4 tiers (add `Conditionally Required`) + OD plan v2.20 U-OD-04 absorption + helper carrier conform (`otel_genai_base.py:58-86`) + 25/25 helper tests pass + 27/27 runtime LLM dispatch tests pass; Tension 004 D-1 ratification SUPERSEDED per §4 step 3 tiebreaker check now performed. Species 3 stale-carry per workflow v1.9 §7.4.7.2.

_Original filing footer:_ **Status:** OPEN — awaiting operator routing decision
**Class:** 1 (halt-execution semantics — design-phase artifact requires revision; spec contradicts named external authority for 2 of 3 D-elements; same failure-mode lineage as D-1 R2)
**Predecessor:** `Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` §7 reconciliation pass (2026-05-26) closed D-2/D-3/D-3b/D-4 as "RESOLVED at OD plan v2.5 plan-conforms-to-spec" **without** performing the §4 step 3 tiebreaker check for D-2/D-3 — same deferred-not-performed failure that produced the D-1 R2 re-litigation arc earlier this session
**Sibling fork:** `class_1_fork_genai_span_name_four_way_drift.md` (D-1 R2 — operator-ratified 2026-05-26; landed at OD spec v1.12 + plan v2.19)

---

## §1 Detection state

| Field | Value |
|---|---|
| Detection arc | OD spec v1.15 §"Adjacent observations" carry-(b) re-evaluation (this session) |
| Detection mode | WebFetch verification of OTel 1.41.0 archived text against OD spec §C-OD-04 §4.2/§4.3/§4.5 (D-1 R2 discipline applied to D-2/D-3/D-4) |
| Discriminating tools | WebFetch against `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md` (operations enum + attribute tiers) + `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-metrics.md` (base metric) |
| Halt point | No code execution — surfaced from documentation/contract layer against external authority |
| HEAD at filing | `e812003` (main, post OD spec v1.15 merge) |
| Advisor pass | Applied pre-substantive — 14th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`; advisor confirmed diagnosis + sharpened arc shape (verification + outcome-branched-closure; strict stop-point on divergence; do not author fork doc until divergence confirmed) |

## §2 Defect — three D-elements verified against OTel 1.41.0 archived text

### §2.1 D-2 §4.2 operations enum — **DIVERGENCE**

| Source | Value |
|---|---|
| OD spec v1.2 §C-OD-04 §4.2 (preserved verbatim through v1.15) | **7 values** — `{chat, text_completion, embeddings, generate_content, create_agent, invoke_agent, execute_tool}` |
| OD plan v2.5 §3.2.1 helper conformance (preserved through v2.19) | matches spec (7 values) |
| OD impl `harness-od/src/harness_od/otel_genai_base.py:58-72` `GenAiOperation` StrEnum | matches spec (7 members) |
| **OTel 1.41.0 archived text** (`gen-ai-spans.md`) | **9 values** — `{chat, create_agent, embeddings, execute_tool, generate_content, invoke_agent, invoke_workflow, retrieval, text_completion}` |
| **Spec is missing** | `invoke_workflow` + `retrieval` (2 values short of cited external authority) |

### §2.2 D-3 §4.3 attribute tiers — **DIVERGENCE**

| Source | Value |
|---|---|
| OD spec v1.2 §C-OD-04 §4.3 (preserved verbatim through v1.15) | **3 tiers** — `Required (Stable) / Recommended (Development) / Opt-In content` (no Conditional) |
| OD plan v2.5 §3.2.1 helper conformance (preserved through v2.19) | matches spec (3 tiers; original v2.1-v2.4 plan had 4 tiers including `CONDITIONAL` which was struck via plan-conforms-to-spec) |
| OD impl `harness-od/src/harness_od/otel_genai_base.py:75-86` `AttributeTier` StrEnum | matches spec (3 members) |
| **OTel 1.41.0 archived text** (`gen-ai-spans.md`) | **4 tiers** — `Required, Conditionally Required, Recommended, Opt-In` |
| **Spec is missing** | `Conditionally Required` (1 tier short of cited external authority) |

### §2.3 D-4 §4.5 base metric — **MATCH (byte-exact)**

| Source | Value |
|---|---|
| OD spec v1.2 §C-OD-04 §4.5 (preserved verbatim through v1.15) | `gen_ai.client.operation.duration` (histogram) |
| OD plan v2.5 §3.2.1 helper conformance (preserved through v2.19) | matches spec |
| OD impl `harness-od/src/harness_od/otel_genai_base.py:115` `BASE_METRIC_NAME` | matches spec |
| **OTel 1.41.0 archived text** (`gen-ai-metrics.md`) | `gen_ai.client.operation.duration` (Histogram) |
| **Conformance** | byte-exact — no defect on D-4 |

### §2.4 D-3 lineage finding (load-bearing)

The original D-3 divergence at Tension 004 §2 line 35 said:

> D-3 §4.3 attribute tiers — plan = 4 values (`REQUIRED`, `CONDITIONAL`, `RECOMMENDED`, `OPT_IN`); spec = 3 tiers (Required (Stable) / Recommended (Development) / Opt-In content; no Conditional)

The OD plan v2.5 plan-conforms-to-spec resolution **removed the correct `CONDITIONAL` tier from the plan** to match the wrong spec. Empirical verification against OTel 1.41.0 archived text (this session) confirms the original v2.1-v2.4 plan was conformant on tier cardinality and the spec was missing one tier. Same failure-mode lineage as D-1: deferred-not-performed tiebreaker check let an incorrect spec override a correct plan element. The §7 reconciliation pass closure of D-3 as "RESOLVED at OD plan v2.5" is now superseded by this re-litigation.

### §2.5 D-2 lineage note

The original D-2 divergence at Tension 004 §2 line 34 said plan = 6 values (omitted `generate_content`); spec = 7 values (included `generate_content`). The plan-conforms-to-spec resolution at OD plan v2.5 correctly added `generate_content` to the plan — that part of the resolution was right. The defect at re-litigation is that the spec itself was already 2 values short of OTel 1.41.0 (`invoke_workflow` + `retrieval`); neither the plan nor the spec captured those. So D-2 needs additive amendment to BOTH spec + plan (add `invoke_workflow` + `retrieval`), not a reversion of the plan v2.5 conformance.

---

## §3 Why Class 1 (halt-execution)

Per `Project_Workflow_v1_8.md` §2.7.6:

- **Spec contradicts named external authority.** OD spec C-OD-04 §4.2/§4.3 cite OTel GenAI semconv 1.41.0 as canonical (per ADR-D6 v1.2 §1.2 [HIGH] cross-vendor floor); empirical verification this session against archived 1.41.0 text shows the spec is missing 2 values from §4.2 and 1 tier from §4.3. Citation byte-exactness per `Project_Workflow_v1_8.md` §7.4.2 invariant I-1 is violated.
- **Same failure mode as D-1 R2.** The D-1 R2 arc earlier this session was Class 1 on the same authority-chain grounds (spec contradicts cited 1.41.0 archived text); D-2/D-3 are structurally identical and warrant the same classification.
- **§7 reconciliation pass was incomplete.** The 2026-05-26 reconciliation pass at Tension 004 §7 closed D-2/D-3/D-4 as RESOLVED-via-plan-conforms-to-spec without performing the §4 step 3 tiebreaker check named at the original 2026-05-15 filing. This is the SECOND deferred-not-performed-then-re-litigated event in the same tension doc.

Per X-AL-3 (Meta-Architecture §7.7) — silent absorption of design-phase defects is the worst failure mode. The §7 reconciliation pass silently absorbed D-2/D-3 against an unverified spec reading; this fork surfaces the silent absorption per X-AL-3 + the surface-don't-absorb discipline.

---

## §4 Resolution options (operator decision required)

### §4.1 Q1 — Resolution shape

**(A) Full conformance to OTel 1.41.0 archived text (recommended — mirrors D-1 R2 shape):**

- OD spec v1.15 → v1.16 NEW §1 canonical-reading amendment table superseding §C-OD-04 §4.2 (7 → 9 values: add `invoke_workflow` + `retrieval`) + §4.3 (3 → 4 tiers: add `Conditionally Required`); v1.2-v1.15 base text PRESERVED VERBATIM per delta-only-spec-file convention.
- OD plan v2.19 → v2.20 U-OD-04 absorption (enum 7 → 9, tiers 3 → 4, AC text updates).
- OD helper `otel_genai_base.py` `GenAiOperation` StrEnum 7 → 9 members; `AttributeTier` StrEnum 3 → 4 members; test updates.
- Production verification (grep for callers; any exhaustive match on the 7-value enum or 3-tier table needs updating).
- Workspace `CLAUDE.md` OD spec row v1.15 → v1.16 narrative.
- Tension 004 doc NEW §7.6 documenting D-2/D-3 re-litigation supersession (mirrors §7.2 D-1 lineage).

Estimated scope: ~5-8 commits bundled as multi-file arc per D-1 R2 precedent.

**(B) Narrow spec-only canonical-reading patch (defer plan/helper/production):**

- OD spec v1.15 → v1.16 NEW §1 canonical-reading amendment only (same as (A) §1 entry).
- Plan / helper / production deferred per FM-2 to follow-on operator-discretion arc.
- Smaller arc (~2 commits).
- Risk: helper + plan + production still encode the wrong cardinality; downstream readers must apply v1.16 §1 in-context until follow-on arc.

**(C) Defer fully (fork doc only — no spec amendment this session):**

- This fork doc filed and ratified; no spec/plan/helper edit.
- Tension 004 doc NEW §7.6 added documenting the re-litigation discovery + deferred-resolution status.
- All downstream artifacts remain on current (wrong) cardinality; carry deferred to next operator-routed arc.

### §4.2 Q2 — Adjacency scope

Whichever option above, should we also:

- **(α) Audit §C-OD-04 §4.4 + §4.5 against archived text now** (defensive — preempt a future Tension 004 §7.7 re-re-litigation on a third D-element). §4.5 already verified MATCH this session. §4.4 not in original Tension 004 D-element set — would be scope-creep.
- **(β) Audit OTel `gen_ai.system` vs `gen_ai.provider.name` divergence** (carry (c) from v1.15 §"Adjacent observations") — separate concern but shares the OTel 1.41.0 archived-text verification surface. Scope-creep risk vs efficient batching.
- **(γ) Skip adjacency** — single-focus arc on D-2/D-3 only; (α) and (β) remain on carry per FM-2.

### §4.3 Recommended routing (advisor + filer pre-recommendation)

- **Q1 → (A) full conformance.** Same shape as the D-1 R2 arc this morning (single-session multi-file bundled). The partial-fix shapes (B) and (C) leave the helper / plan / production encoded against an unverified spec — same trap that produced this re-litigation. (B)/(C) defer the same work to a future session with worse context.
- **Q2 → (γ) skip adjacency.** Per advisor sharpening: "Don't scope-creep into 'while I'm here.'" The named arc is Tension 004 D-2/D-3 re-litigation; (α) and (β) are separate forks.

Operator selects.

---

## §5 Adjacent observations (surfaced; not patched per FM-2)

(a) **Tension 004 §7 reconciliation pass was incomplete.** The §7 reconciliation closed D-2/D-3 as RESOLVED-via-plan-conforms-to-spec without performing the §4 step 3 tiebreaker check. Identical failure mode to the original 2026-05-15 D-1 ratification. Pattern catalogued: **status-field reconciliation passes that close divergences against internal authority without re-performing named tiebreaker checks against external authority can silently absorb the same defect twice.** Operational learning surfaced for `[[tension-record-status-field-reconciliation-discipline]]` (catalogued at Tension 004 §7.5) — discipline should be extended to mandate re-performing all named tiebreaker checks at reconciliation pass time, not just status-field flips.

(b) **OD spec v1.15 finding-(b) carry-text framing was misleading.** The v1.13/v1.14/v1.15 §"Adjacent observations" finding (c)/(b) text said "Tension 004 D-2/D-3/D-4 carries... v1.X does NOT touch §C-OD-04 §4.2/§4.3/§4.5." The implied work was "amend §4.2/§4.3/§4.5 spec sections." The actual work surfaced at empirical verification is "perform deferred tiebreaker check; spec amendment owed at 2 of 3 D-elements (D-2 + D-3); D-4 verified MATCH." The carry-text framing forecasted the wrong shape (similar to v1.13/v1.14 finding (a) which forecast "cardinality drift" but actual defect was "row + section cite drift"). Pattern reinforces `[[advisor-before-substantive-work-for-cross-axis-blockers]]` — empirically verify EVERY claim in a carry-text BEFORE treating the carry as actionable in the framed shape.

(c) **Pattern: SECOND tension re-litigation in workspace history.** First was D-1 R2 (this morning). Second is D-2/D-3 (this fork). Both surfaced because external-authority WebFetch verification was performed at re-litigation but had been deferred at original ratification. Discipline candidate: **at every Class 1 fork ratification that names an external-authority tiebreaker check, the check MUST be performed at the ratification arc, not deferred to "operator confirms."** This is a workflow-grammar-level finding — owed at `Project_Workflow_v1_8.md` revision arc if operator routes.

(d) **OTel 1.41.0 archived text may have additional adjacent divergences.** This fork verified only the 3 named D-elements. §C-OD-04 §4.4 (semantic conventions for content/tool calls?) + §C-OD-04 §4.3 attribute-tier ASSIGNMENT (which attributes are at which tier — not just tier cardinality) + base-layer attribute SET enumeration (line 131-132 of D-3b resolution at helper) were not verified at this arc. NOT patched per FM-2 — single-focus arc on D-2/D-3 cardinality only. Scope flag for future audit.

---

## §6 Routing target

| Field | Value |
|---|---|
| Routing target | This-CLI apply-pass arc (single-session, multi-file bundled) at operator ratification of §4.1 Q1 + §4.2 Q2 selections |
| Authority anchor | ADR-D6 v1.2 §1.2 [HIGH] OTel GenAI semconv 1.41.0 as cross-vendor floor; empirical verification at archived text 2026-05-26 |
| Predecessor arc | `class_1_fork_genai_span_name_four_way_drift.md` (D-1 R2; operator-ratified + applied 2026-05-26 same session) |
| Successor arc | Apply-pass per operator ratification — OD spec v1.16 + OD plan v2.20 + helper update + workspace CLAUDE.md + Tension 004 §7.6 |
| Cross-axis cascade | UNKNOWN at filing — depends on production callers of `GenAiOperation` / `AttributeTier`. To be verified at apply-pass §6 production verification task. Most likely: ZERO cascade (helper is locally-scoped at harness-od; no cross-axis spec citation). |
| Estimated commits | (A) 5-8; (B) 2; (C) 1 (fork doc only) |

---

## §7 Filing footer

| Field | Value |
|---|---|
| Filer | Claude Code (resumed session from checkpoint `20260526-223000-od-spec-v1-15-finding-a-phantom-close.md`) |
| Adversarial-review cleared | n/a (filing not artifact) |
| Architect mode-3 owed | NO — re-litigation of a previously-ratified tension against same external-authority anchor; arc shape mirrors D-1 R2 precedent; architect deliberation not load-bearing |
| Advisor application | 14th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` — confirmed phantom-vs-real diagnosis + sharpened arc shape (verification + branched closure) |
| Commit anchor | [filled at commit time] |
