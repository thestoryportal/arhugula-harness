# Spec: Control Plane — v1.27 (delta over v1.26)

---

## Change-note (v1.26 → v1.27)

**Scope of revision.** Surgical amendment at v1.26 §16.5.4 row U-CP-14 idempotency-key formula + §16.5.6 dual-emission discipline annotation absorbing operator-ratified Reading A resolution of `.harness/class_1_tension_u_cp_14_dual_emission_stubs_and_disambiguator_semantics_gap.md` (filed at PR #65 `d8d091e` 2026-05-29). Operator AskUserQuestion ratification 2026-05-29:

- **Q1 = (A)** Drop `override_id` + `policy_id` segments from §16.5.4 row U-CP-14 formula; collapse to `workflow_id || step_id || sha256(outcome_canonical_bytes).hex()`.
- **Q2 = (iii)** Audit-half stub remediation IN-SCOPE-BUT-MARK-DEFERRED — annotate `emit_override_audit_entry` stub functional gap at §16.5.6 + per-axis CLAUDE.md + plan body; close at follow-on apply-pass arc.
- **Q3 = (i)** Accept v1.25 + v1.26 formula re-ratification reversing prior `override_id` + `policy_id` naming decision. No fresh architect convening required — those segments were named-but-undefined placeholders at the v1.25 + v1.26 ratification arcs; empirical orientation at HEAD `d8d091e` falsified the naming (no semantic source exists at `StepOverride` field-set, `WorkflowManifestEntry` field-set, audit-composer body, or spec body).
- **Q5 = (i)** Apply-pass timing: co-publish spec amendment + plan amendment + impl + tests in single PR per workspace `CLAUDE.md` §11.4 bundled-absorption.
- **Q6 = (α)** Cross-axis cascade scope intra-CP only.

**Trigger.** Class 1 tension fork doc surfaced 3 distinct findings at empirical orientation: (1) §16.5.4 row U-CP-14 names `override_id` + `policy_id` segments without per-composer disambiguator note (rows U-CP-27/30/37/49/50 have notes at §16.5.4 lines 67-90 — U-CP-14 ABSENT); (2) U-CP-74 ratification arc cites `override_id` + `policy_id` as named placeholders without semantic definition; (3) `emit_override_audit_entry` (LANDED audit-half composer at `per_step_override_evaluator.py:208-231`) is a stub — `_ = (override, actor)` ignoring both inputs; hardcoded `gate_level=AUTO`, `response="approve"`, `timestamp=""`, `prior_event_hash="0"*64`. The §16.5.6 dual-emission discipline claim at v1.26 is empirically false at HEAD — neither half is functionally operational.

**Decisive structural constraint for Reading A.** The `per_step_overrides: dict[StepID, StepOverride]` field shape at `harness-cp/src/harness_cp/workflow_manifest_entry.py:109` enforces per-WorkflowManifestEntry step-id uniqueness on override identity at v1.6 MVP scope. The WorkflowManifestEntry IS the policy at v1.6 MVP scope (no multi-version policy semantic exists). `override_id` and `policy_id` carry no v1.6 MVP semantic basis beyond `step_id` + `workflow_id`. Reading A collapses the formula to the type-shape invariants empirically present at HEAD; ZERO StepOverride / WorkflowManifestEntry field-set extension; ZERO new types; ZERO X-AL-3 silent-extension concern.

**v1.26 substantive content preserved verbatim except for the scoped §16.5.4 + §16.5.6 amendments below.** v1.26 §16.5.3 (EntryPayload composition) + §16.5.5 (outcome-bytes recipe table) + §16.5.7 (greenfield firing-site discipline) + §16.5.8 (runtime wiring) + §16.5.9 invariants 1-7 + §16.5.10 (NOT-APPLICABLE reclassifications) + §16.5.11 (status posture) PRESERVED VERBATIM. v1.25 + v1.24 + earlier substantive content preserved verbatim per delta-only-spec-file convention.

**Co-publication this session.** CP plan v2.29 → v2.30 cascade (U-CP-74 unit-body amendment: AC #2 formula 5-tuple → 3-tuple + signatures drop `override_id` + `policy_id` kwargs + test names refresh) + harness-cp impl (`per_step_override_evaluator.py` composer + `_override_idempotency_key` helper signature trim) + harness-runtime impl (`lifecycle/cp_is_wiring.py` wiring-layer signature trim) + harness-cp tests + harness-runtime tests + workspace `CLAUDE.md` row bumps + fork doc Status PROPOSING → ✅ APPLIED-AS-READING-A + clearance marker.

**ZERO breaking change at signed-payload surfaces.** C-CP-16 §16.2 `CPAuditLedgerEntry` 8-field shape preserved verbatim. C-CP-20 §20.4 `CPSignedAuditLedgerEntry` signing contract preserved verbatim. `emit_override_audit_entry` at `per_step_override_evaluator.py:208-231` PRESERVED VERBATIM at signature surface (functional stub remediation deferred per Q2(iii)). The §16.5 sibling composer `emit_override_state_ledger_entry` signature trim drops 2 kwargs — Reading A apply.

**ZERO cross-axis cascade per Q6 = (α).** IS spec UNCHANGED. OD spec UNCHANGED. AS spec UNCHANGED. Runtime spec UNCHANGED. CXA v2.16 UNCHANGED. ADR-D1/D2/D3/D4/D5/D6 UNCHANGED. ADD v1.3 + PRD v1.1 UNCHANGED. Workflow v1.13 UNCHANGED.

---

## §1 — Amended §16.5 sub-sections

The amendments below REPLACE the cited v1.26 sub-section text verbatim. v1.26 sub-sections NOT listed below (§16.5.3 / §16.5.5 / §16.5.7 / §16.5.8 / §16.5.9 / §16.5.10 / §16.5.11) are PRESERVED VERBATIM at v1.27 by reference.

### §16.5.4 — Idempotency-key formulas (REPLACES v1.26 §16.5.4)

Per Q1(b) operator-ratified override-application-specific formula authoring discipline at v1.25: each composer declares an idempotency-key formula scoped to the composer's semantic action surface (NOT reusing C-IS-10 §10.1 step-dispatch formula). Per Q-β.i-1(a) operator-ratified outcome-bytes-relocation discipline at v1.26: each formula APPENDS `|| sha256(outcome_canonical_bytes).hex()` to the per-composer disambiguator, carrying the Q5(a) "hash-over-outcome-bytes" semantic at the dedup-key discriminator. Per Q1=(A) operator-ratified Reading A resolution at v1.27: U-CP-14 row drops the v1.25 / v1.26 `override_id` + `policy_id` placeholder segments (named-but-undefined; no v1.6 MVP semantic basis) and collapses to the base discriminator `workflow_id || step_id` per the `per_step_overrides: dict[StepID, StepOverride]` field uniqueness invariant at `workflow_manifest_entry.py:109`. Multiple invocations of the same composer at the same `(workflow_id, step_id)` with the same outcome MUST produce identical keys (IS-side `IDEMPOTENT_NOOP` on replay); same `(workflow_id, step_id)` + different outcome → different keys → both records persist (replay-safe for non-deterministic composers).

| Composer | idempotency_key canonical bytes (v1.27 row U-CP-14 collapsed per Reading A; other rows preserved verbatim from v1.26) |
|---|---|
| U-CP-14 | `workflow_id \|\| step_id \|\| sha256(outcome_canonical_bytes).hex()` |
| U-CP-27 | `workflow_id \|\| step_id \|\| engine_class_id \|\| binding_selection_result_canonical_bytes \|\| sha256(outcome_canonical_bytes).hex()` |
| U-CP-30 | `workflow_id \|\| step_id \|\| pause_resume_protocol_event_kind \|\| event_sequence_id \|\| sha256(outcome_canonical_bytes).hex()` |
| U-CP-37 | `workflow_id \|\| step_id \|\| tool_call_id \|\| semantic_variant_binding_id \|\| sha256(outcome_canonical_bytes).hex()` |
| U-CP-49 | `workflow_id \|\| step_id \|\| pause_event_id \|\| snapshot_hash \|\| sha256(outcome_canonical_bytes).hex()` |
| U-CP-50 | `workflow_id \|\| step_id \|\| resume_event_id \|\| resume_attempt_count \|\| sha256(outcome_canonical_bytes).hex()` |

Canonical-bytes representation: UTF-8 encode each `||`-separated segment; concatenate with single 0x1E (record-separator) byte between segments; SHA-256 hash the result; hex-64 encode. The 0x1E separator forecloses concatenation-ambiguity attacks (canonical-form rule for §16.5 composers established at v1.25 §16.5.4). At v1.27 row U-CP-14: 3 segments (2 disambiguator + outcome-hash); 2 0x1E separators; SHA-256 hash output unchanged at hex-64. Rows U-CP-27/30/37/49/50 preserve 5-segment shape from v1.26 verbatim.

Per-composer disambiguator fields (e.g., `pause_resume_protocol_event_kind`, `tool_call_id`, `snapshot_hash`) MUST be deterministic at composer-call site. Implementation MUST NOT use wall-clock timestamps or random nonces in idempotency-key composition — that would defeat the idempotency semantic at IS hash-chain replay. The outcome-hash suffix is computed at composer-call site over the outcome canonical bytes per §16.5.5 per-composer recipe.

**Per-composer disambiguator notes (v1.25 §16.5.4 PRESERVED VERBATIM at v1.26; v1.27 NO NEW NOTE for U-CP-14 — row's `workflow_id || step_id` discriminator carries no per-composer specialization beyond the structural invariant cited above):**

- **U-CP-27 `binding_selection_result_canonical_bytes`** — the `WorkloadBindingSelectionResult` (per impl `workload_binding_engine_class_selection.py:71`) canonical JSON bytes; selection rationale + chosen class together form the canonical disambiguator.
- **U-CP-30 `pause_resume_protocol_event_kind`** — `PauseResumeProtocol` class-method invocation discriminator (snapshot capture / resume attempt / classification entry at protocol layer; distinct from engine-layer free functions at U-CP-49/50).
- **U-CP-37 `semantic_variant_binding_id`** — the resolved `HITLSemanticVariantBinding` (per impl `hitl_as_tool_call_rewriting.py:72`) discriminator at `select_variant(...)` outcome consumed by `rewrite_tool_call_to_hitl(...)`.
- **U-CP-49 `snapshot_hash`** — the `PauseSnapshot.snapshot_hash` field per `PauseResumeProtocol` class spec at line 230 (sha256 hex over canonical JSON serialization of `(workflow_id + run_id + step_index + state_summary)`).
- **U-CP-50 `resume_attempt_count`** — discriminates retry attempts at the same `resume_event_id` per `ResumeAttempt` / `ResumeOutcome` model contract (per impl `pause_resume_protocol.py:63,91`).

**U-CP-14 row collapse rationale (NEW at v1.27 per Reading A):** the `per_step_overrides: dict[StepID, StepOverride]` field at `workflow_manifest_entry.py:109` enforces at-most-one StepOverride per `(workflow_id, step_id)` pair at v1.6 MVP scope. The WorkflowManifestEntry IS the policy at v1.6 MVP scope; no multi-version policy semantic exists at the spec layer. `override_id` and `policy_id` as separately-named segments (v1.25 + v1.26) had no semantic source at any LANDED type, composer body, or spec definition site. Reading A removes the placeholders; the `workflow_id || step_id` discriminator + outcome-hash carry the same dedup semantic at the type-shape invariants present at HEAD. If multi-version policy or multi-override-per-step semantics are introduced at a future spec extension (Workflow §4.1.2 Class-2 amendment), the row can be re-extended at that arc per X-AL-3 explicit-extension discipline.

### §16.5.6 — Dual-emission discipline (v1.25 PRESERVED VERBATIM at structural surface; NEW v1.27 audit-half stub annotation per Q2 = iii)

v1.25 §16.5.6 structural discipline PRESERVED VERBATIM: the §16.5 sibling composer `emit_override_state_ledger_entry` is ADDITIVE alongside the existing `emit_override_audit_entry` (LANDED at `per_step_override_evaluator.py:208-231` per v1.25 `[[impl-time-grounding-pass-pre-merge-revision]]`). The driver firing site at `resolve_step_binding(...):187` MUST invoke BOTH composers per §16.5.6 dual-emission discipline; the audit-half emits the CP-internal `CPAuditLedgerEntry` per §16.2 + §20.4 signing contract; the state-ledger-half emits the IS-anchored `EntryPayload` per §16.5.3.

**NEW v1.27 annotation (per Q2 = iii IN-SCOPE-BUT-MARK-DEFERRED audit-half stub remediation):** the audit-half composer `emit_override_audit_entry` at `per_step_override_evaluator.py:208-231` is empirically a **functional stub at HEAD `d8d091e`** — the function body ignores both `override` and `actor` inputs (`_ = (override, actor)` at line 224) and hardcodes placeholder field values (`gate_level=GateLevel.AUTO`, `response="approve"`, `timestamp=""`, `prior_event_hash="0" * 64`). The §16.5.6 dual-emission discipline claim holds at the **structural** layer (both composers exist; both are invoked at the firing site) but is empirically false at the **functional** layer (the audit-half produces a placeholder `CPAuditLedgerEntry`, not a functional override-application audit entry consuming the `override` + `actor` inputs).

This v1.27 annotation acknowledges the audit-half stub as a **known functional gap at HEAD** without closing it at this arc. Closure requires a separate apply-pass arc producing the audit-half functional body per C-CP-06 §6.2 + C-CP-16 §16.2 + §20.4 signing contract conformance. The state-ledger-half (U-CP-74 / `emit_override_state_ledger_entry`) is the focus of v1.27's Reading A apply; the audit-half stub remediation is owed at a follow-on arc.

State-ledger-half firing site at `resolve_step_binding(...)` is currently ABSENT at HEAD (`emit_override_state_ledger_entry` has no production caller; the runtime wiring layer at `harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py:164-194` exposes the wiring surface but the driver does not invoke it). Driver-side firing-site wiring is the **separate "override caller-site invocation" arc** at runtime plan v2.39 U-RT-111 (currently AC #1 STRUCK per `[[u-rt-111-ac-2-strike-fourth-rescope-substrate-lifecycle-mismatch]]` + sibling arcs); v1.27 does NOT close the firing-site gap at the spec layer.

---

## §2 — Adjacent observations (NOT patched per FM-2)

- **(a)** Audit-half stub at `emit_override_audit_entry` remains a known functional gap post-v1.27; closure owed at separate apply-pass arc (per Q2 = iii deferred closure). The stub's structural surface (signature + return type) is preserved at v1.27 verbatim per ZERO breaking change discipline; only the spec body annotates the functional gap.

- **(b)** U-CP-74 ratification arc cites at `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md:72` and `.harness/class_1_tension_u_cp_74_entrypayload_field_set_drift.md:106` reference `override_id` + `policy_id` as named placeholders in the v1.25 + v1.26 formula. v1.27 Q3 = (i) ratifies the reversal of those naming decisions per the empirical-orientation finding (no semantic source exists). The cited fork docs PRESERVED VERBATIM per delta-only-fork-doc convention; downstream readers MUST apply v1.27 §16.5.4 row U-CP-14 substitution when interpreting those references at v1.25 + v1.26 sites.

- **(c)** Reading B template from runtime plan v2.39 (HITL `RewrittenToolCall.variant.value` derivation rule per `[[u-rt-111-ac-4-reading-b-firing-site-absence-v2-39]]`) does NOT transfer to U-CP-14: `HITLSemanticVariant` exists as a `StrEnum` with `.value` providing the opaque kwarg at runtime axis; here `override_id` + `policy_id` have no analogous existing-types source. v1.27 Reading A is the structurally-coherent disposition for U-CP-14; Reading B (identity-collapse to `step_id` + `workflow_id`) was NOT-recommended per fork doc §6 (semantically vacuous; redundant bytes; misleading naming).

- **(d)** Reading C (StepOverride + WorkflowManifestEntry field extension; operator-supplied override_id + policy_id) remains the architecturally-canonical long-term path if multi-version policy semantics or multi-override-per-step semantics are introduced at a future spec extension arc. v1.27 does NOT foreclose Reading C — the row can be re-extended at that future arc per X-AL-3 explicit-extension discipline. Mirror precedent: v1.20 `default_gate_level` + v1.22 `tenant_id` + v1.34 webhook ctor params bundled binding-lift arcs.

- **(e)** Workspace pattern catalogue at v1.27 closure: this arc instantiates `[[strike-revision-on-refined-second-tier-reason]]` at the **spec layer** — the v1.25 + v1.26 §16.5.4 row U-CP-14 formula STRIKE is preserved on a refined second-tier reason (no semantic source for `override_id` + `policy_id`) rather than un-STRUCK at the original framing (multi-version policy roadmap). Mirror precedent at plan layer: runtime plan v2.39 AC #4 STRIKE refinement at U-RT-111 per Workflow v1.13 §7.4.7.2 species 2 sub-species catalogue (workspace v1.13 publication 2026-05-29 commit `9ddb9ba`).

---

## §3 — Status

Surgical amendment at v1.26 §16.5.4 row U-CP-14 + §16.5.6 audit-half stub annotation absorbing operator-ratified Reading A + Q2(iii) + Q3(i) + Q5(i) + Q6(α) at AskUserQuestion 2026-05-29. Apply pass: this arc (delta-only spec file co-published with CP plan v2.30 + harness-cp impl + harness-runtime impl + tests + fork doc closure + clearance marker per Q5(i) bundled-absorption per workspace `CLAUDE.md` §11.4).

v1.26 + v1.25 + earlier PRESERVED VERBATIM per delta-only-spec-file convention. v1.26 §16.5.3 / §16.5.5 / §16.5.7 / §16.5.8 / §16.5.9 / §16.5.10 / §16.5.11 PRESERVED VERBATIM. v1.24 NEW §28.10 `ValidatorPostEvaluateHook` Protocol + v1.7 §13.5.1 CP→OD converter + C-CP-16 §16.2 + C-CP-20 §20.4 PRESERVED VERBATIM.

CXA v2.16 UNCHANGED (intra-CP-axis only per Q6(α); CP→IS bucket cardinality + 6-PENDING + 2-NOT-APPLICABLE composition unchanged). H_T-RT-35 transit posture UNCHANGED at PARTIAL — this arc closes 1 of 5 upstream blockers at the FORK-DOC-FILED → APPLIED transit; 4 remaining upstream arcs gate RETIRE-READY transit.

Clearance marker filed at `.harness/clearance/Spec_Control_Plane-v1_27-cleared-2026-05-29.md`.

2026-05-29.
