# Phase 7 — Class 1 Tension Record 004 — U-OD-04 plan signature diverges from spec C-OD-04

*Plan-vs-spec divergence tension record. Authored at tension detection during
Phase 7 sub-phase 7b atomic-unit execution. Class 1 — halt-execution; the
U-OD-04 plan signature contradicts the spec contract it claims to implement
"verbatim" at four points. Per the in-CLI fix regime (back-flow deprecated
2026-05-15), the fix is applied in Claude Code CLI once the operator selects a
resolution. Shape-identical to Tension 002.*

---

## §1 Detection state

| Field | Value |
|---|---|
| Tension class | **Class 1** (halt-execution; plan-vs-spec divergence — plan acceptance criteria internally contradictory) |
| Detected at | Phase 7 sub-phase 7b, atomic unit **U-OD-04** (OTel GenAI semconv 1.41.0 base-layer attributes) |
| Detected | 2026-05-15 |
| Halt point | U-OD-04 implementation — surfaced before code execution |
| Status | **CLOSED** 2026-05-26 — D-1 SUPERSEDED at OD spec v1.12 + plan v2.19 (re-litigation per §4 step 3 tiebreaker check; FIRST tension re-litigation in workspace history); **D-2 + D-3 SUPERSEDED at OD spec v1.16 + plan v2.20 same day** (SECOND tension re-litigation per same §4 step 3 tiebreaker check that §7.1 D-2/D-3 closure did NOT re-perform — see §7.6); D-3b PRESERVED VERBATIM per OD spec v1.16 §1.3; D-4 RESOLVED at OD plan v2.5 + verified MATCH at OTel 1.41.0 archived text 2026-05-26. See §7 + §7.6. |

## §2 Defect

U-OD-04 (`Implementation_Plan_Operational_Discipline_v2_1.md` §3.2.1, Cluster 2
preserved verbatim through v2.4) `Implements: [C-OD-04 §4.1, §4.2, §4.3, §4.4,
§4.5]`. Its acceptance criteria repeatedly claim the signatures are "per §4.x
verbatim" — but the plan signature diverges from spec C-OD-04
(`Spec_Operational_Discipline_v1_2.md` §4, preserved verbatim into v1.3) at
four points:

| # | Surface | Plan U-OD-04 signature | Spec C-OD-04 | Plan acceptance claim |
|---|---|---|---|---|
| D-1 | §4.1 span name format | `"{gen_ai.operation.name} {gen_ai.request.model}"` (2 components) | `{gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}` (3 components) | #1: "matches §4.1 verbatim" — **false** |
| D-2 | §4.2 operations enum | `GenAiOperation` = 6 values (`CHAT`, `EXECUTE_TOOL`, `EMBEDDINGS`, `TEXT_COMPLETION`, `CREATE_AGENT`, `INVOKE_AGENT`) | 7 values — `{chat, text_completion, embeddings, generate_content, create_agent, invoke_agent, execute_tool}` (plan omits `generate_content`) | #2: "the 6 operations ... verbatim" — **false** (spec has 7) |
| D-3 | §4.3 attribute tiers | `AttributeTier` = 4 values (`REQUIRED`, `CONDITIONAL`, `RECOMMENDED`, `OPT_IN`) | 3 tiers — Required (Stable) / Recommended (Development) / Opt-In content (no Conditional) | #3: "exactly 4 tiers per §4.3 verbatim" — **false** (spec has 3) |
| D-3b | §4.3 tier assignment | acceptance #4 places `input_tokens`/`output_tokens` in **Conditional**; introduces `gen_ai.response.id` (Recommended) | spec §4.3 places `input_tokens`/`output_tokens` in **Recommended**; `gen_ai.response.id` absent from §4.3 | #4 — diverges |
| D-4 | §4.5 base metric | `BASE_METRIC_NAME = "gen_ai.client.token.usage"` | `gen_ai.client.operation.duration` (histogram) | #6: "per §4.5 verbatim — the canonical token usage metric" — **false** |

The divergence is semantic, not casing/format: the plan and spec disagree on
the span-name component set, the operation cardinality, the tier cardinality,
the per-attribute tier assignment, and the base metric identity.

## §3 Why Class 1 (halt-execution)

U-OD-04's acceptance criteria are **internally contradictory**: each claims the
signature is "per §4.x verbatim" while the signature is not. The unit cannot be
materialized in a way that satisfies its own acceptance against the cited spec.
Resolution requires an operator decision on the canonical span-schema base
layer, then a plan revision-pass. Identical in shape to Tension 002 (U-CP-22
plan signature vs C-CP-10 §10.1).

## §4 Proposed resolution (operator decision required)

**Authority-chain reading.** Per `CLAUDE.md` §1.3, the spec (Phase 5) is
canonical over the plan (Phase 6). C-OD-04 traces to **ADR-D6 v1.1 §1.2 base
layer block** ("OTel GenAI semconv 1.41.0 [HIGH] as cross-vendor floor;
preserved verbatim per v1.1 change-note"). Spec C-OD-04 §4.1–§4.5 is the
authority-chain-canonical base layer. This mirrors the Tension 002 resolution
(spec canonical; conform the divergent plan).

**Recommended direction (pending operator confirmation):**
1. Adopt **spec C-OD-04 §4.1–§4.5** as canonical for U-OD-04:
   span name = 3-component `{gen_ai.operation.name} {gen_ai.provider.name}
   {gen_ai.request.model}`; operations enum = 7 values; attribute tiers = 3
   (Required / Recommended / Opt-In); base metric =
   `gen_ai.client.operation.duration`.
2. Revise the CP… (OD) plan U-OD-04 signature + acceptance #1–#6 to the spec
   §4.x content, in-CLI (`implementation-planner` revision-pass).
3. **Tiebreaker check the operator should make:** confirm ADR-D6 has no
   revision later than v1.2 that re-anchors the base layer, and confirm OTel
   GenAI semconv 1.41.0 itself (the cited external standard) matches the spec
   §4.x reading — the spec cites 1.41.0 as a [HIGH] external anchor; if the
   actual 1.41.0 convention differs from §4.x, that is a separate spec defect.
4. U-OD-04 then implements against the conformed spec.

This record does not apply a fix — the operator selects the resolution. Note
the systems-architect §4A tension-resolution mode can produce a full
authority-chain recommendation for this fork on request (as it did for
Tension 002).

## §5 Block-clearing decision

| Field | Value |
|---|---|
| Decision | **PENDING** — U-OD-04 implementation halted until the operator selects the canonical span-schema base layer and authorizes the plan revision. |
| Unblocked siblings | U-OD-01 already landed 2026-05-15 (commits `22e3bf0`). U-CP-15 landed (`a267f09`). U-CP-22 separately halted under Tension 003. |

## §6 Operational-minimum set status

Of the 12-unit operational-minimum set: **10 landed** (U-IS-01..04, U-AS-01..04,
U-CP-15, U-OD-01). **2 halted on Class 1 forks** — U-CP-22 (Tension 003,
`WorkloadClass` undeclared) and U-OD-04 (this record). Both are plan-defect
forks surfaced cleanly per the surface-don't-absorb discipline (X-AL-3); neither
was silently absorbed.

---

## §7 Closure 2026-05-26 — status-field reconciliation pass

All 5 divergences (D-1 + D-2 + D-3 + D-3b + D-4) are RESOLVED across the canonical artifacts. Tension 004 doc Status field (line 20) + §5 Decision field carried stale **OPEN** / **PENDING** values from the 2026-05-15 filing because the substantive resolutions landed at OD plan v2.5 (`Implementation_Plan_Operational_Discipline_v2_5.md` §0.2 — "folds in the already-filed Tension 004 = U-OD-04") and OD spec v1.12 + plan v2.19 (`.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.1 R2 apply-pass) without back-propagating to this record. This §7 reconciliation closes the doc-status drift.

### §7.1 Per-divergence resolution table

| Divergence | Pre-resolution state | Post-resolution state | Resolution arc + commit |
|---|---|---|---|
| **D-1** §4.1 span name format | Plan v2.1-v2.4 = 2-component; OD spec v1.2-v1.11 = 3-component (`{gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}`) | 2-component (`{gen_ai.operation.name} {gen_ai.request.model}`) — byte-exact to actual OTel 1.41.0 archived text | Two-stage: (i) plan-conforms-to-spec at OD plan v2.5 §3.2.1 (2-component → 3-component per Tension 004 §4 step 1 recommended direction); (ii) SUPERSEDED at OD spec v1.12 §C-OD-04 §4.1 canonical-reading amendment + OD plan v2.19 U-OD-04 absorption per `.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.1 R2 apply-pass 2026-05-26 (3-component → 2-component per actual OTel 1.41.0). The §4 step 3 tiebreaker check that was deferred-not-performed at 2026-05-15 was PERFORMED at the 2026-05-26 re-litigation; the check FAILED (1.41.0 archived text said 2-component); Tension 004 D-1 ratification SUPERSEDED per the doc's own framing. R1 follow-on: production rename at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:324` + runtime spec v1.27 line 2033 STRIKE. Helper at `harness-od/src/harness_od/otel_genai_base.py:104` `SPAN_NAME_FORMAT` byte-exact to 2-component form. Production span name post-arc: `chat gpt-4o-mini` (post-finding-(g) value-space conform). |
| **D-2** §4.2 operations enum | Plan v2.1-v2.4 = 6 values (omitted `generate_content`); OD spec v1.2 = 7 values | 7 values matching spec verbatim (`chat` / `text_completion` / `embeddings` / `generate_content` / `create_agent` / `invoke_agent` / `execute_tool`) | RESOLVED at OD plan v2.5 §3.2.1 (6 → 7 operations conformance); preserved verbatim through v2.6 - v2.19. Helper at `otel_genai_base.py:58-72` `GenAiOperation` StrEnum has 7 members. |
| **D-3** §4.3 attribute tiers | Plan v2.1-v2.4 = 4 values (`REQUIRED` + `CONDITIONAL` + `RECOMMENDED` + `OPT_IN`); OD spec v1.2 = 3 tiers (Required (Stable) / Recommended (Development) / Opt-In content; no Conditional) | 3 tiers matching spec verbatim | RESOLVED at OD plan v2.5 §3.2.1 (4 → 3 tiers conformance); preserved verbatim through v2.6 - v2.19. Helper at `otel_genai_base.py:75-86` `AttributeTier` StrEnum has 3 members. |
| **D-3b** §4.3 tier assignment | Plan v2.1-v2.4 acceptance #4 = `input_tokens`/`output_tokens` in Conditional; introduced `gen_ai.response.id` (Recommended); OD spec v1.2 §4.3 = `input_tokens`/`output_tokens` in Recommended; `gen_ai.response.id` absent from §4.3 base layer | input/output tokens at Recommended (Development); `gen_ai.response.id` absent from `BASE_LAYER_ATTRIBUTES` (still emitted at production line 400 as a per-call attribute, separate from the §4.3 base-layer enumeration) | RESOLVED at OD plan v2.5 §3.2.1 acc #4 conformance to §4.3 3-tier table. Helper at `otel_genai_base.py:131-132` (`gen_ai.usage.input_tokens` + `gen_ai.usage.output_tokens` at `RECOMMENDED_DEVELOPMENT`). |
| **D-4** §4.5 base metric | Plan v2.1-v2.4 = `BASE_METRIC_NAME = "gen_ai.client.token.usage"`; OD spec v1.2 = `gen_ai.client.operation.duration` (histogram) | `gen_ai.client.operation.duration` matching spec verbatim | RESOLVED at OD plan v2.5 §3.2.1 (base metric conformance); preserved verbatim through v2.6 - v2.19. Helper at `otel_genai_base.py:115` `BASE_METRIC_NAME` = `gen_ai.client.operation.duration`. |

### §7.2 Re-litigation lineage (D-1 only)

D-1's history is structurally different from D-2/D-3/D-3b/D-4. The other four were plan-vs-spec divergences resolved by plan-conforms-to-spec (spec was authority per `CLAUDE.md` §1.3); D-1 was a spec-vs-cited-external-authority divergence that surfaced only when the spec's own §4 tiebreaker check was performed. That check was named at Tension 004 §4 step 3 as a "tiebreaker check the operator should make" but was deferred-not-performed at 2026-05-15 ratification. The 2026-05-26 GenAI fork arc performed the check via WebFetch of the archived 1.41.0 spec; the check failed; both the spec (v1.11 → v1.12) and the plan (v2.18 → v2.19) absorbed the correction; the original Tension 004 D-1 ratification is now SUPERSEDED per its own framing.

This is the FIRST tension re-litigation in workspace history. Sibling pattern: `[[h-t-cp-21-batch-15-down-classification]]` (DOWN + corrective close) — both are corrections of prior decisions via formal re-evaluation against canonical authority.

### §7.3 §5 Decision update

§5 line "Decision: **PENDING**" reads CLOSED-RESOLVED as of this reconciliation pass. U-OD-04 implementation is no longer halted — landed at production helper `otel_genai_base.py` per the v2.5 conformance pass + v2.19 D-1 amendment. The operational-minimum set at §6 was completed beyond the original 12-unit scope; both Tension 003 (U-CP-22) and this fork's siblings have since landed RETIRED / PARTIAL per `.harness/phase-7d-retirement-ledger-v2.md`.

### §7.4 No artifact bump owed

This §7 reconciliation is a doc-status-field flip + closure pass. NO OD spec version bump owed (v1.12 is current; the D-1 amendment is already absorbed at the canonical-reading amendment + change-note). NO OD plan version bump owed (v2.19 is current; both v2.5 D-2/D-3/D-3b/D-4 absorption + v2.19 D-1 absorption are present at the canonical artifacts). NO cross-axis cascade. NO production code change (post-finding-(f)+(g) production state at `llm_dispatch.py:337-340` already emits the post-resolution shape end-to-end).

### §7.5 Pattern catalogued

**`[[tension-record-status-field-reconciliation-discipline]]`** — when a Class 1 tension is resolved via absorption at downstream artifacts (spec amendment / plan revision / production code), the tension-record itself does NOT auto-update unless an explicit reconciliation pass writes back to the doc. Tension 004 carried stale OPEN/PENDING status for 11 days (2026-05-15 filing → 2026-05-26 reconciliation) despite D-2/D-3/D-3b/D-4 having landed at OD plan v2.5 within the same week. Discipline: at tension-resolving arcs, append a status-update to the tension doc as part of the arc's bundled commit; OR run a periodic status-reconciliation pass against the open-tensions roster.

Reference patterns: `[[empirical-verification-supersedes-training-data-knowledge]]` (§7.2 D-1 re-litigation discipline — perform named tiebreaker checks AT ratification, not defer them). `[[advisor-before-substantive-work-for-cross-axis-blockers]]` (the 2026-05-26 GenAI fork arc applied advisor at every scope transition; the deferred tiebreaker check from 2026-05-15 was the historical counter-example that motivates the discipline).

**Commit anchor:** [filled at commit time]

---

## §7.6 D-2 + D-3 re-litigation supersession 2026-05-26 (SECOND tension re-litigation)

Filed: 2026-05-26 (same day as §7 reconciliation pass; same day as D-1 R2 re-litigation arc earlier in the morning).
Fork doc: `.harness/class_1_fork_tension_004_d2_d3_otel_141_relitigation.md` (filed + operator-ratified + applied this session — single-session arc, mirrors D-1 R2 shape).
Operator ratification: §4.1 (A) full conformance + §4.2 (γ) single-focus 2026-05-26.

### §7.6.1 Why §7.1 D-2 + D-3 closures are superseded

The §7.1 closure table closed D-2 + D-3 as "RESOLVED at OD plan v2.5 plan-conforms-to-spec." The §7.5 pattern catalogue named `[[tension-record-status-field-reconciliation-discipline]]` BUT the reconciliation pass itself did NOT re-perform the §4 step 3 tiebreaker check named at the original 2026-05-15 filing — the same deferred-not-performed failure mode that produced the D-1 R2 re-litigation earlier the same day.

This v1.16 + v2.20 re-litigation arc performed the check via WebFetch against archived OTel 1.41.0 specifications:

- `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md` — operations enum + attribute tiers
- `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-metrics.md` — base metric

The check FAILED for D-2 + D-3; PASSED (MATCH byte-exact) for D-4.

### §7.6.2 Per-divergence post-supersession state

| Divergence | §7.1 framing (pre-supersession) | §7.6 post-re-litigation state | Resolution lineage |
|---|---|---|---|
| **D-2** §4.2 operations enum | "7 values matching spec verbatim" (RESOLVED at OD plan v2.5 6 → 7) | **SUPERSEDED at OD spec v1.16 §1.1** — actually 9 values per OTel 1.41.0 (`{chat, create_agent, embeddings, execute_tool, generate_content, invoke_agent, invoke_workflow, retrieval, text_completion}`). Spec was missing `invoke_workflow` + `retrieval`. v1.16 amendment adds both; OD plan v2.20 U-OD-04 AC #2 cardinality 6 → 9. | Three-stage: plan-conforms-to-spec at v2.5 (6 → 7) → spec-conforms-to-external-authority at v1.16 (7 → 9) → plan absorption at v2.20 (6 → 9 against pre-v2.5 reference) |
| **D-3** §4.3 attribute tiers | "3 tiers matching spec verbatim" (RESOLVED at OD plan v2.5 4 → 3 tier-strike) | **SUPERSEDED at OD spec v1.16 §1.2** — actually 4 tiers per OTel 1.41.0 (`Required / Conditionally Required / Recommended / Opt-In`). Spec was missing `Conditionally Required`. **The original v2.1-v2.4 plan was conformant on tier cardinality (had `CONDITIONAL`); the v2.5 plan-conforms-to-spec strike was wrong-direction.** v1.16 amendment adds the missing tier; OD plan v2.20 U-OD-04 AC #3 cardinality 3 → 4 (restores the v2.1-v2.4 4-tier shape). | Three-stage: plan-strike-Conditional-conforms-to-spec at v2.5 (wrong-direction) → spec-conforms-to-external-authority at v1.16 (3 → 4) → plan-restore-Conditional at v2.20 |
| **D-3b** §4.3 tier assignment | input/output tokens at Recommended (Development); `gen_ai.response.id` absent | PRESERVED VERBATIM at v1.16 §1.3 — tier-assignment for individual attributes against the new 4-tier table is a SEPARATE audit owed at future operator-routed arc per FM-2 + fork doc §4.2 (γ) single-focus | Stable post-v2.5; per-attribute audit owed at future arc |
| **D-4** §4.5 base metric | `gen_ai.client.operation.duration` matching spec verbatim (RESOLVED at OD plan v2.5) | UNCHANGED — WebFetch verified MATCH byte-exact (`gen_ai.client.operation.duration` Histogram per `gen-ai-metrics.md`). No amendment owed. | Single-stage; verified MATCH against external authority at v1.16 |

### §7.6.3 Pattern reinforcement

`[[tension-record-status-field-reconciliation-discipline]]` (catalogued at §7.5) is REINFORCED + EXTENDED:

- Original §7.5 catalogue: tension-record status-field reconciliation passes should write back to the doc + perform named tiebreaker checks at reconciliation pass time.
- §7.6 extension: **the named tiebreaker check is load-bearing.** Reconciliation passes that flip status fields without re-performing named external-authority tiebreaker checks CAN silently absorb the same defect twice — Tension 004 is the empirical example, with the same defect (deferred-not-performed §4 step 3 check) producing two separate re-litigation events on the same day (D-1 R2 morning; D-2 + D-3 evening). The discipline is workflow-grammar-level; candidate for `Project_Workflow_v1_8.md` revision arc per fork doc §5(c).

### §7.6.4 Adjacent observations from v7.6 arc (not patched)

(a) **D-3b tier-assignment audit against 4-tier table owed.** v1.16 §1.3 preserves 17 attributes at v1.2-lineage tier assignments (3 Required + 6 Recommended + 8 Opt-In; none at new `Conditionally Required`). Future audit owed against per-attribute requirement levels at OTel 1.41.0 archived text. Surfaced at OD spec v1.16 §"Adjacent observations" (e).

(b) **§4.4 audit against archived text NOT performed.** §4.4 (semantic conventions for content/tool calls) was not in original D-element set + not verified at this single-focus arc. Defensive audit owed. Surfaced at OD spec v1.16 §"Adjacent observations" (f).

(c) **`harness_breaker_schema.py:21` docstring drift.** Docstring claims "AttributeTier enum has no `CONDITIONAL` members"; stale post-v1.16. NOT patched per fork doc §4.2 (γ) single-focus. Surfaced at OD plan v2.20 §"Adjacent observations" (e).

### §7.6.5 Commit anchor

[filled at commit time]

