# Spec: Operational Discipline — v1.16 (delta over v1.15)

---

## Change-note (v1.15 → v1.16)

**Scope of revision.** Class 1 fork resolution apply pass per `.harness/class_1_fork_tension_004_d2_d3_otel_141_relitigation.md` §4.1 operator-ratified 2026-05-26 option (A) full conformance + §4.2 option (γ) single-focus. Canonical-reading amendment at §C-OD-04 §4.2 (operations enum 7 → 9 values: add `invoke_workflow` + `retrieval`) + §4.3 (attribute tiers 3 → 4 tiers: add `Conditionally Required`) to conform with OTel GenAI semconv 1.41.0 archived text (cited at ADR-D6 v1.2 §1.2 [HIGH] cross-vendor floor). Re-litigates Tension 004 D-2 + D-3 elements per same shape as D-1 R2 (`.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.1 R2 apply-pass 2026-05-26). ZERO cross-axis cascade verified at production grep. Single-file delta-only-spec-file authoring per established convention.

**Empirical posture (load-bearing).** WebFetch verification 2026-05-26 against archived OTel 1.41.0 specifications:

- `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-spans.md` — operations enum + attribute tiers source-of-truth.
- `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/gen-ai-metrics.md` — base metric source-of-truth.

**§4.2 operations enum.** Archived text declares **9 values**: `chat`, `create_agent`, `embeddings`, `execute_tool`, `generate_content`, `invoke_agent`, `invoke_workflow`, `retrieval`, `text_completion`. OD spec v1.2 §C-OD-04 §4.2 (preserved verbatim through v1.15) declares **7 values** (missing `invoke_workflow` + `retrieval`).

**§4.3 attribute tiers.** Archived text declares **4 tiers**: `Required`, `Conditionally Required`, `Recommended`, `Opt-In`. OD spec v1.2 §C-OD-04 §4.3 (preserved verbatim through v1.15) declares **3 tiers** (`Required (Stable)`, `Recommended (Development)`, `Opt-In content`; missing `Conditionally Required`).

**§4.5 base metric.** Archived text declares `gen_ai.client.operation.duration` (Histogram). OD spec v1.2 §C-OD-04 §4.5 (preserved verbatim through v1.15) declares `gen_ai.client.operation.duration` (histogram). **MATCH byte-exact**; no amendment owed at v1.16 per fork doc §4.2 (γ) single-focus scope.

**Lineage finding (load-bearing).** Tension 004 §7 reconciliation pass (2026-05-26) closed D-2/D-3 as "RESOLVED at OD plan v2.5 plan-conforms-to-spec" without performing the §4 step 3 tiebreaker check named at the original 2026-05-15 filing. The plan-conforms-to-spec resolution at D-3 **removed the correct `CONDITIONAL` tier from the plan v2.1-v2.4** to match the wrong spec. Same deferred-not-performed failure mode as D-1 (re-litigated at this morning's R2 fork arc). v1.16 supersedes Tension 004 §7.1 D-2 + D-3 rows per the doc's own §4 step 3 framing (external authority preempts internal canonical reading when the internal reading contradicts the cited version).

**Routing.** Per workspace `CLAUDE.md` §4.3 + I-1 byte-exact discipline + D-1 R2 apply-pass precedent (OD spec v1.11 → v1.12 single-session 2026-05-26): the Class 1 fork resolution lands at OD spec v1.15 → v1.16 with NEW §1 canonical-reading amendment table + §2 finding-(b) closure (carry from v1.13/v1.14/v1.15) + §3 Tension 004 §7 reconciliation supersession documentation. v1.2-v1.15 PRESERVED VERBATIM per delta-only convention; downstream readers MUST apply v1.16 §1 substitutions when interpreting §C-OD-04 §4.2 + §4.3 from prior versions.

---

## §1 Canonical-reading amendment table (v1.16 NEW)

Per delta-only-spec-file convention, the v1.2 through v1.15 file bodies are PRESERVED VERBATIM. The following table maps every drift site for §C-OD-04 §4.2 + §4.3 to its corrected canonical reading. Readers of v1.2-v1.15 MUST apply these substitutions when interpreting operations-enum cardinality + tier-cardinality tokens at the listed sites.

### §1.1 §C-OD-04 §4.2 operations enum (7 → 9 values; add `invoke_workflow` + `retrieval`)

The v1.2-v1.15 §C-OD-04 §4.2 enumerates **7 values** for `gen_ai.operation.name`: `chat`, `text_completion`, `embeddings`, `generate_content`, `create_agent`, `invoke_agent`, `execute_tool`. The canonical reading at v1.16 conforms to the OTel 1.41.0 archived text **9-value** enumeration:

| Position | Value | Status at v1.16 |
|---|---|---|
| 1 | `chat` | PRESERVED (existed v1.2) |
| 2 | `create_agent` | PRESERVED (existed v1.2) |
| 3 | `embeddings` | PRESERVED (existed v1.2) |
| 4 | `execute_tool` | PRESERVED (existed v1.2) |
| 5 | `generate_content` | PRESERVED (existed v1.2) |
| 6 | `invoke_agent` | PRESERVED (existed v1.2) |
| 7 | `invoke_workflow` | **NEW at v1.16** (per OTel 1.41.0 archived text) |
| 8 | `retrieval` | **NEW at v1.16** (per OTel 1.41.0 archived text) |
| 9 | `text_completion` | PRESERVED (existed v1.2) |

Sites in v1.2-v1.15 referencing "7 operations" / "7 values" / "the 6 operations" (per v1.13/v1.14/v1.15 finding-text) all read **9 operations / 9 values** at v1.16. Specific drift sites:

| Site | Original token | Canonical reading at v1.16 |
|---|---|---|
| v1.2 §C-OD-04 §4.2 (preserved verbatim through v1.15) — operations enum table | "7 operations" / "the canonical 7 values" / enumeration list | "9 operations" / "the canonical 9 values per OTel 1.41.0" / 9-value enumeration per §1.1 table above |
| v1.13/v1.14/v1.15 §"Adjacent observations" finding (c)/(b) text — "Tension 004 D-2/D-3/D-4 carries" | "v1.X does NOT touch §C-OD-04 §4.2/§4.3/§4.5" — implied work was "amend §4.2/§4.3/§4.5 spec sections" | CLOSED-as-resolved at v1.16 §1.1 + §1.2 (D-2 + D-3); D-4 verified MATCH per change-note empirical posture |

### §1.2 §C-OD-04 §4.3 attribute tiers (3 → 4 tiers; add `Conditionally Required`)

The v1.2-v1.15 §C-OD-04 §4.3 declares **3 tiers** for attribute requirement levels: `Required (Stable)`, `Recommended (Development)`, `Opt-In content`. The canonical reading at v1.16 conforms to the OTel 1.41.0 archived text **4-tier** enumeration:

| Position | Tier | Status at v1.16 |
|---|---|---|
| 1 | `Required` (`Required (Stable)` at v1.2-v1.15 naming) | PRESERVED (existed v1.2; v1.2-v1.15 "Required (Stable)" reads as "Required" at v1.16 per OTel naming) |
| 2 | `Conditionally Required` | **NEW at v1.16** (per OTel 1.41.0 archived text; original v2.1-v2.4 plan included this tier as `CONDITIONAL` which was STRUCK at OD plan v2.5 plan-conforms-to-spec — that strike is now SUPERSEDED) |
| 3 | `Recommended` (`Recommended (Development)` at v1.2-v1.15 naming) | PRESERVED (existed v1.2; reads as "Recommended" at v1.16 per OTel naming) |
| 4 | `Opt-In` (`Opt-In content` at v1.2-v1.15 naming) | PRESERVED (existed v1.2; reads as "Opt-In" at v1.16 per OTel naming) |

Sites in v1.2-v1.15 referencing "3 tiers" / "exactly 3 tiers per §4.3" / "the 3-tier table" all read **4 tiers** at v1.16. Tier naming conformance is documented per the parenthetical mapping above; the v1.2 internal naming (`Required (Stable)` / `Recommended (Development)` / `Opt-In content`) is preserved as DERIVATIVE naming with the OTel canonical names (`Required` / `Recommended` / `Opt-In`) as the authoritative names at v1.16 per ADR-D6 v1.2 §1.2 cross-vendor-floor framing.

### §1.3 §C-OD-04 §4.3 tier-assignment preservation (D-3b)

D-3b (per Tension 004 §7.1) — placement of `input_tokens` / `output_tokens` at `Recommended (Development)` tier per OD plan v2.5 conformance — is **PRESERVED VERBATIM** at v1.16. The new `Conditionally Required` tier added at §1.2 does NOT auto-migrate existing attribute assignments. Tier-assignment for individual attributes against the 4-tier table is a separate audit owed at future operator-routed arc per FM-2 (out of scope at this single-focus fork resolution; surfaced as v1.16 §"Adjacent observations" finding (e)).

### §1.4 §C-OD-04 §4.5 base metric (verified MATCH; no amendment)

OTel 1.41.0 archived text base metric `gen_ai.client.operation.duration` (Histogram) is **byte-exact match** with OD spec v1.2 §C-OD-04 §4.5. No amendment owed at v1.16. Verification documented at change-note empirical posture; this §1.4 is a no-op declaration confirming D-4 is conformant at v1.16.

---

## §2 Finding-(b) closure (v1.13 + v1.14 + v1.15 §"Adjacent observations" finding (c)/(b))

**Closed-as-resolved-via-re-litigation.** v1.13/v1.14/v1.15 finding (c)/(b) ("Tension 004 D-2/D-3/D-4 carries; v1.X does NOT touch §C-OD-04 §4.2/§4.3/§4.5") is now resolved at v1.16 §1 canonical-reading amendment table. The carry-text framing implied the work was "amend §4.2/§4.3/§4.5 spec sections" — empirical verification at WebFetch against OTel 1.41.0 archived text (this session) confirmed:

- §4.2 needs amendment: 7 → 9 values (D-2 partial — spec was missing 2 values; plan-conforms-to-spec at v2.5 was right on `generate_content` add but wrong on cardinality completeness)
- §4.3 needs amendment: 3 → 4 tiers (D-3 — spec was missing `Conditionally Required`; the original v2.1-v2.4 plan was conformant on this tier and was wrongly conformed to the spec at v2.5)
- §4.5 verified MATCH: no amendment (D-4 — already conformant)

The framing was partially-correct: amendment was indeed owed to §4.2/§4.3 sections; the §4.5 part of the carry was unnecessary (verified MATCH at re-litigation). D-3b tier-assignment for individual attributes against the new 4-tier table is preserved verbatim per §1.3 and surfaced as a separate adjacent finding for future audit.

**Disposition at v1.16.** Finding (b) is **CLOSED-as-resolved-via-re-litigation**. Removed from v1.16 §"Adjacent observations" carry; no longer a deferred apply-pass arc.

---

## §3 Tension 004 §7 reconciliation pass supersession (D-2 + D-3 rows)

The 2026-05-26 reconciliation pass at `.harness/archive/root-historical/Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` §7 closed D-2/D-3/D-4 as "RESOLVED at OD plan v2.5 plan-conforms-to-spec." The reconciliation pass did NOT re-perform the §4 step 3 tiebreaker check against the cited external authority (OTel 1.41.0 archived text). This v1.16 re-litigation supersedes the §7.1 D-2 + D-3 rows per the doc's own §4 step 3 framing.

**Per-divergence post-v1.16 state:**

| Divergence | §7.1 closure framing | v1.16 post-re-litigation state | Resolution lineage |
|---|---|---|---|
| **D-1** §4.1 span name format | SUPERSEDED at OD spec v1.12 + plan v2.19 per `.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.1 R2 apply-pass 2026-05-26 (FIRST tension re-litigation) | UNCHANGED at v1.16 (already correctly superseded at v1.12) | Two-stage: plan-conforms-to-spec at v2.5 (3-component) → spec-conforms-to-external-authority at v1.12 (2-component per OTel 1.41.0) |
| **D-2** §4.2 operations enum | "7 values matching spec verbatim" — claimed RESOLVED at OD plan v2.5 (6 → 7 conformance) | **SUPERSEDED at v1.16 §1.1** — actually 9 values per OTel 1.41.0; plan v2.5 conformance was incomplete on cardinality; spec needs +2 (`invoke_workflow` + `retrieval`) | Three-stage: plan-conforms-to-spec at v2.5 (6 → 7) → spec-conforms-to-external-authority at v1.16 (7 → 9) → plan absorption at v2.20 |
| **D-3** §4.3 attribute tiers | "3 tiers matching spec verbatim" — claimed RESOLVED at OD plan v2.5 (4 → 3 tier-strike) | **SUPERSEDED at v1.16 §1.2** — actually 4 tiers per OTel 1.41.0; plan v2.5 strike of `CONDITIONAL` tier was wrong direction; spec needs +1 (`Conditionally Required`) | Three-stage: plan-strike-Conditional-conforms-to-spec at v2.5 → spec-conforms-to-external-authority at v1.16 (3 → 4) → plan-restore-Conditional at v2.20 |
| **D-3b** §4.3 tier assignment | input/output tokens at Recommended (Development); `gen_ai.response.id` absent from §4.3 base layer | PRESERVED VERBATIM at v1.16 §1.3 (assignment is separate concern from cardinality) | Stable post-v2.5; future audit owed against 4-tier table |
| **D-4** §4.5 base metric | `gen_ai.client.operation.duration` matching spec verbatim — RESOLVED at OD plan v2.5 | UNCHANGED at v1.16 (verified MATCH against OTel 1.41.0 archived text per change-note empirical posture) | Single-stage: plan-conforms-to-spec at v2.5; spec was already conformant to external authority |

**Tension 004 doc update owed.** The `.harness/archive/root-historical/Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` §7.1 D-2 + D-3 rows + §7.5 pattern catalogue are stale post-v1.16. Co-publication owed at apply-pass arc: append NEW §7.6 "D-2 + D-3 re-litigation supersession 2026-05-26" reflecting the v1.16 amendment. This is the **SECOND tension re-litigation** in workspace history (D-1 was the first at this morning's R2 arc). The §7.5 catalogued pattern `[[tension-record-status-field-reconciliation-discipline]]` is reinforced: reconciliation passes that close divergences against internal authority without re-performing named tiebreaker checks against external authority CAN silently absorb the same defect twice.

---

## §4 Sections preserved verbatim at v1.16

Per delta-only-spec-file convention + FM-2 no-extension discipline + single-focus arc scope per fork doc §4.2 (γ), the v1.16 amendment touches ONLY the NEW §1 canonical-reading amendment table + §2 finding-(b) closure + §3 Tension 004 §7 supersession (all within this v1.16 delta file). The following sections are PRESERVED VERBATIM from their authoring versions:

- **§C-OD-04 §4.1** (v1.12-lineage span-name 2-component format per D-1 R2)
- **§C-OD-04 §4.2** (v1.2-lineage operations enum; v1.16 §1.1 canonical reading applied)
- **§C-OD-04 §4.3** (v1.2-lineage attribute tiers; v1.16 §1.2 canonical reading applied)
- **§C-OD-04 §4.4** (v1.2-lineage; not in scope at this fork)
- **§C-OD-04 §4.5** (v1.2-lineage; verified MATCH at §1.4)
- **§C-OD-05 §5.1 rows 1-15** (v1.2-lineage; v1.13 row 5 sub-note + v1.15 §1 canonical reading preserved verbatim)
- **§C-OD-05 §5.2 + §5.3** (ingestion-posture invariants)
- **§C-OD-06 through §C-OD-33** (all v1.2-v1.15 lineage content preserved per delta-only-spec-file convention)
- **All v1.3 through v1.15 substantive amendments** (D-1 R2 absorption at v1.12; finding-(a) closure + canonical-reading at v1.15; all carry resolutions)

---

## Adjacent observations (surfaced as findings; NOT patched per FM-2)

(a) **OD spec v1.13/v1.14/v1.15 finding (c)/(b) — CLOSED-as-resolved-via-re-litigation at v1.16 §2.** Removed from "Adjacent observations" carry; no longer a deferred apply-pass arc.

(b) **OD spec v1.13/v1.14/v1.15 finding (d)/(c) — `gen_ai.system` vs `gen_ai.provider.name` divergence.** Carried verbatim from v1.13/v1.14/v1.15. v1.16 does NOT touch this carry. Candidate for next operator-routed arc if WebFetch verification surfaces a third divergence.

(c) **v1.14/v1.15 finding (d) — §8.4.2 anticipated cases empirical-verification.** Carried verbatim from v1.14/v1.15. v1.16 does NOT touch this carry.

(d) **v1.15 finding (e) — AS-spec v1 §15.4 footnote on always-sampled posture.** Carried verbatim from v1.15. v1.16 does NOT touch this carry (informational only).

(e) **NEW at v1.16 — §C-OD-04 §4.3 tier-assignment audit against 4-tier table.** v1.16 §1.3 preserves D-3b tier-assignment verbatim against the new 4-tier table. Individual attribute assignments (e.g., which attributes belong at `Conditionally Required` vs `Recommended` vs `Required` vs `Opt-In`) per OTel 1.41.0 archived text were NOT verified at this single-focus fork resolution. Future audit owed if operator routes: WebFetch against `gen-ai-spans.md` to extract per-attribute tier assignments and compare against v1.2 §C-OD-04 §4.3 base-layer attribute table. Scope flag for future operator-discretion arc.

(f) **NEW at v1.16 — §C-OD-04 §4.4 against OTel 1.41.0 archived text.** §4.4 was NOT in the original Tension 004 D-element set + NOT verified at this re-litigation arc per single-focus scope. Defensive audit owed if operator routes: confirm §4.4 content (semantic conventions for content/tool-calls/etc.) is conformant to archived text. Scope flag.

(g) **NEW at v1.16 — process finding on tension-doc reconciliation discipline.** The §7 reconciliation pass at Tension 004 closed D-2/D-3 without re-performing the §4 step 3 tiebreaker check; same failure-mode lineage as the original 2026-05-15 D-1 ratification. **Discipline candidate:** at Class 1 fork ratification arcs naming external-authority tiebreaker checks, the check MUST be performed at ratification time, not deferred to "operator confirms." Workflow-grammar-level finding; owed at `Project_Workflow_v1_8.md` revision arc if operator routes. (Surfaced at fork doc §5(c).)

---

## Downstream artifacts requiring absorption at follow-on arcs

| Artifact | Required change | Owner |
|---|---|---|
| Workspace `CLAUDE.md` §2.3 OD spec row | v1.15 → v1.16 row update with v1.16 change-note narrative; v1.15 + earlier lineage preserved | This session apply-pass arc |
| OD plan `Implementation_Plan_Operational_Discipline_v2_19.md` → v2.20 | U-OD-04 single-unit absorption: GenAiOperation 7 → 9; AttributeTier 3 → 4; AC text updates; test names. Mirrors v2.19 D-1 absorption shape. | This session apply-pass arc |
| OD helper `harness-od/src/harness_od/otel_genai_base.py` | `GenAiOperation` StrEnum 7 → 9 members (add `INVOKE_WORKFLOW` + `RETRIEVAL`); `AttributeTier` StrEnum 3 → 4 members (add `CONDITIONALLY_REQUIRED`); existing tests updated; new coverage added | This session apply-pass arc |
| OD helper tests | Update existing enum-membership assertions; add new coverage for `INVOKE_WORKFLOW`, `RETRIEVAL`, `CONDITIONALLY_REQUIRED` | This session apply-pass arc |
| Production callers (grep audit) | If any exhaustive `match` statement against `GenAiOperation` or `AttributeTier` exists, add cases for new members. Verified at apply-pass §6 production verification task. | This session apply-pass arc |
| Tension 004 doc `.harness/archive/root-historical/Phase_7_Class_1_Tension_004_OD04_Span_Schema_Divergence.md` | Append NEW §7.6 "D-2 + D-3 re-litigation supersession 2026-05-26" (SECOND tension re-litigation in workspace history) | This session apply-pass arc |
| `harness-od/CLAUDE.md` | NO change owed — v1.16 is helper-shape change at harness-od layer; no cross-axis citation table touched. Helper update absorbed at impl arc. | n/a |
| CXA v2.12 | NO change owed — §1 canonical-reading amendment is OD-internal cardinality refresh; no CXA cite affected. | n/a |
| AS spec v1.7 | NO change owed — AS spec is unrelated to OD §C-OD-04 GenAI semconv. | n/a |
| AS plan v1.4 | NO change owed. | n/a |
| ADR-D6 v1.2 | NO change owed per X-AL-3 — v1.16 conforms spec to ADR-D6 §1.2 [HIGH] anchor (OTel 1.41.0 archived text); ADR itself unchanged. | n/a |
| Runtime spec / plan | NO change owed — runtime spec does NOT cite §C-OD-04 enum or tier cardinality directly. | n/a |

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.16 (Class 1 fork resolution apply pass per `class_1_fork_tension_004_d2_d3_otel_141_relitigation.md` §4.1 (A) + §4.2 (γ) operator-ratified 2026-05-26; NEW §1 canonical-reading amendment table for §C-OD-04 §4.2 + §4.3 + §2 finding-(b) closure + §3 Tension 004 §7 supersession; v1.15 + earlier files PRESERVED VERBATIM per delta-only-spec-file convention) |
| Trigger | v1.13/v1.14/v1.15 §"Adjacent observations" finding (c)/(b) re-evaluation per operator-routed cluster-1 open-arc 2026-05-26 (session resumption from `20260526-223000-od-spec-v1-15-finding-a-phantom-close.md`); WebFetch verification of OTel 1.41.0 archived text confirmed D-2 + D-3 divergences |
| Supersedes | Tension 004 §7.1 D-2 + D-3 rows ("RESOLVED at OD plan v2.5 plan-conforms-to-spec") — superseded per the doc's own §4 step 3 framing (external authority preempts internal canonical reading) |
| Scope of revision | NARROW: NEW §1 canonical-reading amendment table for §4.2 enum (7 → 9 values) + §4.3 tiers (3 → 4 tiers) + §2 finding-(b) closure + §3 Tension 004 §7 supersession. Cross-axis cascade: ZERO at spec layer; helper + plan + production updates land in same bundled apply-pass arc per fork doc §4.1 (A) full-conformance scope. |
| Contract change | Additive on §4.2 enum (+2 values) + §4.3 tiers (+1 tier); ZERO removal; NO signature change; NO field removal; NO behavior change at existing consumers (additive on enums is backward-compatible at consumer layer per Pydantic v2 StrEnum semantics). |
| Cross-axis cascade | ZERO at spec layer (verified at fork doc §6 + this change-note Downstream artifacts table); helper + plan + production absorbed at same-arc apply pass |
| Authority anchor | ADR-D6 v1.2 §1.2 [HIGH] OTel GenAI semconv 1.41.0 as cross-vendor floor; empirical verification at `gen-ai-spans.md` archived text 2026-05-26 (WebFetch); D-1 R2 apply-pass precedent (`.harness/class_1_fork_genai_span_name_four_way_drift.md` §7.4.1 R2 operator-ratified 2026-05-26) |
| Predecessor | v1.15 (finding-(a) phantom closure + canonical-reading amendment for row-number + section-cite drift) |
| Successor | v1.17 (next operator-discretion arc — candidates: v1.16 finding (b) `gen_ai.system` vs `gen_ai.provider.name`; finding (c) §8.4.2 anticipated cases; finding (e) tier-assignment audit; finding (f) §4.4 audit; finding (g) workflow-grammar reconciliation discipline at `Project_Workflow_v1_8.md`) |
| Advisor application | 14th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` — pre-substantive advisor pass confirmed phantom-vs-real diagnosis + sharpened arc shape (verification + branched closure with strict stop-point on divergence) |
| Pattern catalogue | **SECOND tension re-litigation in workspace history** (D-1 was the first this morning); reinforces `[[tension-record-status-field-reconciliation-discipline]]` (Tension 004 §7.5) — reconciliation passes MUST re-perform named tiebreaker checks against external authority, not defer them |
