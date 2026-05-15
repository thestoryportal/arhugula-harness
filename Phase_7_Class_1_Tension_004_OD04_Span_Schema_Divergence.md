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
| Status | **OPEN** — awaiting operator resolution decision |

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
