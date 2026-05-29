# Class 1 Tension — U-CP-14 dual-emission both-halves-stub + §16.5.4 disambiguator semantics gap

| Field | Value |
|---|---|
| Status | ✅ APPLIED-AS-READING-A + Q2=iii + Q3=i + Q5=i + Q6=α (operator-ratified 2026-05-29; apply pass this PR) |
| Filed | 2026-05-29 |
| Closed | 2026-05-29 — Apply pass: CP spec v1.26 → v1.27 §16.5.4 row U-CP-14 formula collapse to `workflow_id \|\| step_id \|\| sha256(outcome_canonical_bytes).hex()` + §16.5.6 audit-half stub annotation per Q2=iii; CP plan v2.29 → v2.30 U-CP-74 single-unit-body amendment (AC #2 + Signatures + test names); harness-cp + harness-runtime impl signature trim; 2090 / 10 skipped tests pass; clearance marker filed at `.harness/clearance/Spec_Control_Plane-v1_27-cleared-2026-05-29.md`. Audit-half stub remediation + state-ledger-half firing-site wiring DEFERRED per Q2=iii + upstream `[[u-rt-111-ac-2-strike-fourth-rescope-substrate-lifecycle-mismatch]]`. |
| Filed by | Operator + Claude (post-PR-#64 close, design-phase posture) |
| Class | 1 (architectural; CP spec named-but-undefined disambiguator surface + audit-composer-stub finding + state-ledger composer firing-site absence — composite blocker) |
| Triggers | Upstream blocker (2) for H_T-RT-35 RETIRE-READY per checkpoint 2026-05-29; advisor 45th application pre-substantive consultation surfaced 3 distinct findings the checkpoint framing missed |
| Halt scope | None at execution-time (both composer halves are LANDED stubs; ZERO production functional consumption); back-flow scope for CP-axis spec-writer + plan revision arc |

---

## §1 Finding

CP spec v1.26 §16.5.4 row U-CP-14 declares the idempotency-key formula `workflow_id || step_id || override_id || policy_id || sha256(outcome_canonical_bytes).hex()` but names `override_id` and `policy_id` as canonical disambiguator segments **without defining what they semantically are**. The per-composer disambiguator notes block at §16.5.4 lines 67-90 enumerates rows for U-CP-27 / U-CP-30 / U-CP-37 / U-CP-49 / U-CP-50; **U-CP-14 is the one row missing its disambiguator note**.

The U-CP-74 ratification arc at `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md:72` and `.harness/class_1_tension_u_cp_74_entrypayload_field_set_drift.md:106` references `override_id` + `policy_id` as named placeholders in the formula but does NOT define what they semantically are.

Empirical orientation at `harness-cp/src/harness_cp/per_step_override_evaluator.py`:
- `emit_override_audit_entry` (LANDED audit-half composer, lines 208-231) takes `(workflow_id, step_id, override: StepOverride, actor: ActorIdentity)` — and **ignores override + actor** (`_ = (override, actor)` at line 228). Hardcodes `gate_level=GateLevel.AUTO`, `response="approve"`, `timestamp=""`, `prior_event_hash="0" * 64`. The returned `CPAuditLedgerEntry` is a structural placeholder, not a functional audit entry.
- `emit_override_state_ledger_entry` (NEW v1.26 state-ledger half, lines 282-315) takes `override_id: str` + `policy_id: str` as REQUIRED kwargs with no production source (`StepOverride` field-set at `workflow_manifest_entry.py:51-65` has no `override_id` / `policy_id` fields).
- `resolve_step_binding` at lines 154-187 invokes `emit_override_audit_entry(...)` (the stub) at line 187. Does NOT invoke `emit_override_state_ledger_entry`. CP spec §16.5.6 dual-emission discipline claim is empirically false at HEAD — there is no functional audit half to dual-emit with.

The composite finding: **neither half of §16.5.6 dual-emission is operational**. Both composer surfaces are LANDED-but-stub-or-unfireable. The §16.5.4 named-but-undefined disambiguator is the visible symptom of a deeper design gap on override identity semantics that the U-CP-74 ratification arc did not resolve.

---

## §2 Empirical orientation (HEAD `ff9eb0f`)

| Surface | Path | State |
|---|---|---|
| `StepOverride` Pydantic model | `harness-cp/src/harness_cp/workflow_manifest_entry.py:51-65` | LANDED; field set `{step_id, model_binding\|None, engine_class\|None, hitl_placement\|None}` — NO override_id / NO policy_id |
| `WorkflowManifestEntry` Pydantic model | `harness-cp/src/harness_cp/workflow_manifest_entry.py:88-127` | LANDED; field set includes `workflow_id`, `entry_version`, `per_step_overrides: dict[StepID, StepOverride]` — NO policy_id |
| `emit_override_audit_entry` | `per_step_override_evaluator.py:208-231` | LANDED STUB — ignores override + actor; hardcodes placeholder fields |
| `emit_override_state_ledger_entry` | `per_step_override_evaluator.py:282-315` | LANDED; signature requires `override_id: str + policy_id: str` kwargs with no production source |
| `resolve_step_binding` firing-site | `per_step_override_evaluator.py:154-187` | Invokes audit composer at `:187`; does NOT invoke state-ledger composer; §16.5.6 dual-emission empirically false |
| CP spec v1.26 §16.5.4 row U-CP-14 formula | `design-substrate/Spec_Control_Plane_v1_26.md:56` | LANDED but names `override_id` + `policy_id` without semantic definition |
| CP spec v1.26 §16.5.4 per-composer disambiguator notes | `Spec_Control_Plane_v1_26.md:67-90` | Enumerates U-CP-27/30/37/49/50 — **U-CP-14 ABSENT** |
| CP spec v1.26 §16.5.5 outcome-bytes recipe (U-CP-14 row) | `Spec_Control_Plane_v1_26.md` table | LANDED — `post-override step-config canonical JSON bytes` |
| U-CP-74 ratification arc | `.harness/architect_recommendation_u_rt_35_gap_b_within_path_a.md`; `.harness/class_1_tension_u_cp_74_entrypayload_field_set_drift.md` | Cites override_id + policy_id as named formula placeholders; ZERO semantic definition |

---

## §3 Readings

### Reading A — Drop separate `override_id` + `policy_id`; collapse formula to `(workflow_id, step_id, outcome_hash)`

Reframe the U-CP-14 disambiguator: the override is uniquely identified by `(workflow_id, step_id)` because each step has at most one StepOverride per WorkflowManifestEntry (per `per_step_overrides: dict[StepID, StepOverride]` field shape at `workflow_manifest_entry.py:109`). The outcome-hash carries the "what HAPPENED" semantic. Drop `override_id` + `policy_id` from the §16.5.4 row 1 formula; collapse to `workflow_id || step_id || sha256(outcome_canonical_bytes).hex()`.

**Pros:** smallest spec amendment; closes the named-but-undefined gap by removing the names; matches `per_step_overrides: dict[StepID, StepOverride]` field uniqueness invariant; ZERO StepOverride field-set extension; ZERO new types.

**Cons:** loses ability to discriminate multi-version policy applications at the same step (if policy versioning is added later, this row would need re-extension). Defeats the v1.25 / v1.26 ratification arc's explicit naming of these segments (would require Q-set re-ratification reversing prior decision).

### Reading B — `override_id = step_id`; `policy_id = workflow_id`; document as identity-collapse

Spec amendment at §16.5.4 NEW row U-CP-14 disambiguator note: explicitly document that `override_id` IS `step_id` (no separate override identity at v1.6 MVP scope; one StepOverride per step) AND `policy_id` IS `workflow_id` (no separate policy identity at v1.6 MVP scope; the WorkflowManifestEntry IS the policy). The formula then reduces semantically to `workflow_id || step_id || workflow_id || step_id || outcome_hash` which is redundant but preserves the v1.26 formula shape verbatim.

**Pros:** preserves v1.26 formula verbatim; closes the named-but-undefined gap without amendment to the formula itself; documents the v1.6 MVP identity-collapse explicitly.

**Cons:** redundant disambiguator bytes (workflow_id + step_id twice); semantically vacuous identity-collapse; doesn't address the operator-supplied-identifier or content-hash motivations behind naming them separately; gives the impression these are distinct identifiers when they're collapsed.

### Reading C — Extend StepOverride field-set with operator-supplied `override_id: str`; extend WorkflowManifestEntry with `policy_id: str`

Plan revision absorbing CP spec amendment NEW §6.X StepOverride field extension (`override_id: str`) + NEW §6.Y WorkflowManifestEntry field extension (`policy_id: str`). Both fields required, no default. Manifest-author supplies stable identifiers at manifest authoring time. §16.5.4 row U-CP-14 disambiguator note: "`override_id`: operator-supplied per-StepOverride identifier; `policy_id`: operator-supplied per-WorkflowManifestEntry identifier."

**Pros:** preserves v1.26 formula verbatim; semantically aligned with §16.5.4's intent (distinct disambiguator segments); operator-explicit per X-AL-3 (no silent extension or derivation); supports future multi-version policy + multi-override-per-step semantics.

**Cons:** largest surface change (NEW field at 2 Pydantic models + manifest-authoring discipline requirement); breaking change at existing test fixtures (need to supply identifiers); X-AL-3 silent-absorption concern if applied without operator ratification of "field extension" disposition; mirror precedent at v1.20 `default_gate_level` + v1.22 `tenant_id` + v1.34 webhook ctor params (all bundled binding-lift arcs).

### Reading D — Content-derived `override_id` + `policy_id` per §16.5.4 NEW disambiguator note

Spec amendment at §16.5.4 NEW row U-CP-14 disambiguator note: `override_id = sha256(canonical_bytes(StepOverride))[:16].hex()` (16-hex-char content-address of the StepOverride); `policy_id = sha256(canonical_bytes(WorkflowManifestEntry-identity-subset))[:16].hex()` (16-hex-char content-address of the manifest's identity-defining fields). Requires defining what "identity subset" means at WorkflowManifestEntry.

**Pros:** preserves v1.26 formula verbatim; ZERO StepOverride / WorkflowManifestEntry field-set extension; content-addressing means same StepOverride content → same override_id deterministically (replay-safe).

**Cons:** X-AL-3 silent-extension concern (advisor 45th application flagged this explicitly — derivation from existing types requires existing types to carry the semantic; here the derivation IS the semantic synthesis); requires defining "identity subset" of WorkflowManifestEntry which is itself a design decision; content-address loses operator-supplied stability (content changes between revisions → identifier changes); discriminator is over content, not over identity, which conflates two concepts.

### Reading E — Bounded-defer per sibling-fork pattern (mirror PR #64)

File this fork doc as PROPOSING; defer ratification + closure to follow-on session. Maintain U-CP-14 LANDED-but-never-fired-state-ledger-half + LANDED-stub-audit-half. Document the both-halves-stub finding as the load-bearing observation; surface it as evidence that the §16.5.4 named-but-undefined gap is the visible symptom of a deeper override identity design gap requiring fresh deliberation.

**Pros:** preserves catalogue coherence; matches HITL + sibling-ledger defer disposition at PR #64; avoids premature semantic decision that may be reversed at architect deliberation; closes the upstream blocker to FORK-DOC-FILED state.

**Cons:** does not advance H_T-RT-35 toward RETIRE-READY at this arc; carries the both-halves-stub finding without closure; the audit-stub remains a load-bearing functional gap unaddressed.

---

## §4 Q-set for operator ratification

| Q | Decision space |
|---|---|
| Q1 | Disambiguator semantic Reading: A (drop override_id + policy_id) / B (identity-collapse to step_id + workflow_id) / C (StepOverride + WorkflowManifestEntry field extension; operator-supplied) / D (content-derived) / E (bounded-defer) |
| Q2 | Audit-half stub remediation scope: (i) IN-SCOPE this arc — fix `emit_override_audit_entry` to consume override + actor properly; (ii) OUT-OF-SCOPE this arc — defer audit-stub closure to separate arc; (iii) IN-SCOPE-BUT-MARK-DEFERRED — annotate audit-stub in spec body + fork doc; close at follow-on |
| Q3 (if A) | Re-ratification of U-CP-74 Q-set: (i) accept v1.25 + v1.26 formula re-ratification reversing prior naming decision; (ii) require fresh architect convening before reversing |
| Q4 (if C) | Existing test-fixture migration: (i) extend all existing StepOverride fixtures with operator-supplied override_id (breaking change); (ii) add Optional default to both fields preserving backward compatibility (mirror v1.20 default_gate_level shape); (iii) require fresh fixture authoring per fork-doc apply pass |
| Q5 (any non-E) | Apply-pass timing: (i) co-publish spec amendment + plan amendment + impl in single PR (bundled-absorption per CLAUDE.md §11.4); (ii) spec amendment only at this arc; plan + impl at follow-on |
| Q6 (any) | Cross-axis cascade scope: (α) intra-CP only; (β) CP + plan revision; (γ) full CP + IS spec re-citation (if outcome_canonical_bytes shape changes) |

---

## §5 Cross-axis cascade analysis

| Axis | Touch under each Reading |
|---|---|
| IS | Reading A: NONE. Reading B: NONE. Reading C: NONE. Reading D: NONE. Reading E: NONE. (idempotency_key is composer-internal; IS sees opaque string per C-IS-10 §10.1) |
| AS | NONE under any Reading |
| CP | Reading A: §16.5.4 row 1 formula amendment. Reading B: §16.5.4 NEW disambiguator note. Reading C: NEW §6.X + §6.Y field extensions + §16.5.4 NEW disambiguator note. Reading D: §16.5.4 NEW disambiguator note + WorkflowManifestEntry identity-subset definition. Reading E: NONE at this arc. |
| OD | NONE (audit-ledger writes downstream; idempotency_key is opaque at OD layer) |
| CXA | NONE under any Reading (no new typed edge; existing U-CP-74 → U-RT-110 chain unchanged) |
| Runtime spec | NONE under any Reading (intra-CP composer concern) |
| Runtime plan | Reading C: U-CP-78 / U-CP-79 (NEW StepOverride + WorkflowManifestEntry field carriers) revision. Other Readings: NONE direct (U-CP-78 ACs that exercise the composer will need to provide override_id + policy_id sources matching the ratified Reading). |
| Existing tests | Reading C: breaking change at all StepOverride / WorkflowManifestEntry fixture construction sites (must supply identifiers). Reading A: existing test signatures simplify. Reading B / D: test fixtures unchanged. Reading E: NONE. |

---

## §6 Recommendation

**Pre-substantive recommendation:** Reading A (drop override_id + policy_id; collapse formula) is the structurally-coherent disposition at v1.6 MVP scope. The `per_step_overrides: dict[StepID, StepOverride]` field shape at `workflow_manifest_entry.py:109` already enforces step-id uniqueness as the override identity at MVP; `policy_id` semantic has no v1.6 MVP basis (the WorkflowManifestEntry IS the policy; no multi-version policy semantic exists). Reading A closes the named-but-undefined gap by removing the redundant naming, matches the empirical type-shape invariant, and avoids the X-AL-3 silent-extension concern.

Reading C (StepOverride + WorkflowManifestEntry field extension) is the architecturally-canonical long-term path if multi-version policy semantics or multi-override-per-step semantics are anticipated. If operator has near-term roadmap for those semantics, Reading C is preferable; otherwise Reading A is preferable.

Reading B (identity-collapse) is NOT recommended — semantically vacuous; preserves formula shape at the cost of redundant bytes + misleading naming.

Reading D (content-derived) is NOT recommended — X-AL-3 silent-extension concern (advisor 45th application flagged this); conflates content with identity.

Reading E (bounded-defer) is the safe fallback if operator wants more time for the semantic decision OR wants architect convening before closure.

**Audit-half stub remediation (Q2):** Recommend Q2(iii) IN-SCOPE-BUT-MARK-DEFERRED at this arc — the audit-stub is a separate functional gap that should be acknowledged in spec body + plan; closing it requires a separate apply-pass arc on the audit-half composer body. Co-publishing both fixes at this arc risks over-scope and conflates two distinct findings.

---

## §7 Status posture

| Element | Status |
|---|---|
| §16.5.4 row U-CP-14 named-but-undefined disambiguator | ❌ GAP confirmed |
| §16.5.6 dual-emission discipline at HEAD | ❌ EMPIRICALLY FALSE (audit-stub + state-ledger no firing-site) |
| `emit_override_audit_entry` functional content | ❌ STUB (ignores override + actor) |
| `emit_override_state_ledger_entry` production callsite | ❌ ABSENT |
| H_T-RT-35 RETIRE-READY transit | GATED on this arc (1 of 5 upstream blockers) + sibling arcs at PR #64 + 2 others |
| Recommended Q1 | (A) drop override_id + policy_id; collapse formula; OR (C) field extension if multi-version policy roadmap exists |
| Recommended Q2 | (iii) IN-SCOPE-BUT-MARK-DEFERRED for audit-half stub at this arc |
| Sibling arcs | PR #64 fork docs (HITL + sibling-ledger firing-site absences) + bootstrap-emission-substrate arc + engine-layer impl arc — composite blocker set for H_T-RT-35 |

---

## §8 Advisor lineage

**45th application** of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture caught:
- (1) audit-half stub as load-bearing finding (would have been missed if I'd authored a disambiguator-only fork doc per checkpoint framing)
- (2) Reading-B template from v2.39 does NOT transfer (no existing types carry override_id/policy_id semantics; v2.39 had `HITLSemanticVariant.value` ready)
- (3) §16.5.4 verification grep recommendation (confirmed U-CP-14 row is THE missing one)
- (4) U-CP-74 ratification arc verification (confirmed override_id + policy_id named-as-placeholders without semantic definition)
- (5) Distinct routing path (CP spec back-flow + spec-writer; not plan revision)

Pre-substantive empirical verification + advisor consultation reframed the checkpoint item from "Override disambiguator extension arc" (narrow) to "both-halves-stub + named-but-undefined disambiguator composite blocker" (proper scope).

---

*End of fork doc.*
