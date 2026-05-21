# Adversarial Review — U-RT-59 Fork 2 spec arc bundle

## Summary

| Field | Value |
|---|---|
| Checkpoint | Phase-7 pre-implementation review mode (applied post-landing per operator request) |
| Artifacts reviewed | `Spec_Harness_Runtime_v1.md` v1.7 (§14.7.2 step 8 amendment) + `Spec_Control_Plane_v1_7.md` §13.5.1 + `Spec_Control_Plane_v1_8.md` (NOTE-reference patch) + `ADR-D5.md` v1.4 (§1.4 + §1.4.1) + `Spec_Operational_Discipline_v1_5.md` C-OD-24 + `Cross_Axis_Composition_Document_v2_4.md` §2.3.7 |
| Date | 2026-05-20 |
| Finding count by class | Class 3: **0** · Class 2: **5** (all *proposing*; 4 latent at single-sub-agent slice) · Class 1: **3** |
| Highest-severity finding | F2-01 — `audit.cp.action_id` non-uniqueness across sub-agent siblings (verifiable in code; latent at v1.7 single-sub-agent slice; load-bearing at fan-out arc landing) |
| Disposition recommendation | **Cleared with current-phase spec revision** per §4.1.2 — 5 Class 2 *proposing* findings recommend a NOTE-form clarification patch over runtime spec v1.7 §14.7.2 step 8a + CP spec v1.7 §13.5.1 + OD spec v1.5 §24.5 + §24.6; OR operator may select the structural extension path (extend `CPAuditLedgerEntry` shape — would escalate to §4.1 Class 3 / §2.7.6 Class 1 fork). The 3 Class 1 drifts fix inline at the next spec touch. No §4.1 Class 3 findings; no §2.7.6 Class 1 halt-execution surfaced |

**Latent-vs-active framing for Class 2 findings.** F2-01 through F2-05 share the property that at v1.7 single-sub-agent slice (parent topology `SINGLE_THREADED_LINEAR`, fan-out emission foreclosed per spec §14.7 MVP invariant), they DO NOT manifest as runtime bugs — audit entries persist, the 4-substep composer chain executes, the 2283 workspace tests pass. They become observable defects when (a) the fan-out arc lands (multiple siblings of the same parent ⇒ `audit.cp.action_id` collision) OR (b) cross-side CP↔OD audit-trace join via `audit.cp.action_id` is exercised at an audit-consumption surface. These are **contract-layer findings against future-load scenarios**, not blocking defects at the v1.7 MVP slice. Surfacing now because v1.7 is the contract authority for both v1.7 MVP and post-v1.7 fan-out arcs.

---

## Class 3 findings (severe — phase re-opening)

*None.*

The U-RT-59 Fork 2 arc shipped under explicit operator ratification at each path (Path D + Path B-revised-a + runtime v1.7 + CP v1.8). The bundle's framing claims (storage-form reconciliation, namespace projection, canonical entry-hash recipe) all trace to operator-ratified discovery-report sub-questions (Q1 + Q2(a) + Q3 + Q4 + Q5). No project-commitment violation per discriminator (c); no upstream-phase artifact revision required to fix any surfaced defect.

---

## Class 2 findings (moderate — current-phase spec revision)

### F2-01 — `audit.cp.action_id` non-uniqueness across sub-agent siblings (verifiable; latent at v1.7 MVP slice)

- **Location:** `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:199-205` (`emit_sub_agent_dispatch_audit`); cross-references `Spec_Harness_Runtime_v1.md` v1.7 §14.7.2 step 8a; `Spec_Control_Plane_v1_7.md` §13.5.1 field-projection table row 1 (`action_id` → `audit.cp.action_id` "Anchor for CP↔OD cross-side join").
- **Defect:** Three identity patterns for the same dispatch event don't reconcile:
  1. The code constructs `CPAuditLedgerEntry.action_id = ActionID(f"{parent_action_id}||sub-agent")` — no `descent.child_index` and no `brief_hash`.
  2. The docstring at lines 188-194 promises `parent_action_id || sub_agent_idx` — child index is documented but not implemented.
  3. Runtime spec v1.7 §14.7.2 step 8a claims "audit entries are dispatch-fact records keyed by `(parent_action_id, descent, brief_hash)` per C-CP-12 §12.5" — neither descent nor brief_hash survives into the persisted CP entry.

  Consequence: at fan-out (multiple siblings of the same parent), all CP audit entries get an identical `audit.cp.action_id`. The CP spec v1.7 §13.5.1 field-projection table row 1 names `action_id` as "Anchor for CP↔OD cross-side join" — the join key is non-unique across siblings. Cross-side trace queries via `audit.cp.action_id` would coalesce N sibling events to one.
- **Discriminator that classifies as Class 2:** (a) — affects substantive content of current-phase runtime spec §14.7.2 step 8a + CP spec v1.7 §13.5.1 field-projection table + the code at `emit_sub_agent_dispatch_audit`. Discriminator (b) only fires under resolution path (b) below; *proposing* until operator selects.
- **Evidence:** Code at `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:199`:
  ```python
  return CPAuditLedgerEntry(
      action_id=ActionID(f"{parent_action_id}||sub-agent"),
      gate_level=ASGateLevel(descent.child_gate_level.value),
      response="approve",
      timestamp="",
      prior_event_hash="0" * 64,
  )
  ```
  Note: no `descent.child_index`, no `brief_hash`, no `timestamp` (see F2-03).
- **Anti-fabrication attack engaged:** A2 (silent scope narrowing) — the spec scopes the cross-side join discipline at C-CP-12 §12.5 + CP §13.5.1 row 1, but the implementation narrows the key by dropping descent + brief_hash; v1.7 amendment surfaced the cross-side join requirement without surfacing the non-uniqueness.
- **Axis-domain attack engaged:** CP-axis (cross-side join integrity at audit-trail-link composition per C-CP-13 §13.5).
- **Resolution path (operator selects one; classification per §"Decision-claim vocabulary" — *proposing* until selection):**
  - **(a) Documentation-level reconciliation (Class 2; current-phase NOTE patch).** Amend runtime spec §14.7.2 step 8a + CP spec v1.7 §13.5.1 to NOTE: "`audit.cp.action_id` is non-unique across sub-agent siblings of the same parent at v1.7 MVP and post-v1.7 fan-out arc; sibling-distinguishable cross-side join is via `entry_core: StateLedgerEntryRef` (per OD spec v1.5 C-OD-24.4) which carries the F2 dispatch-entry action_id pattern `dispatch:<parent_action_id>:<child_index>`." Fix code docstring at `sub_agent_gate_level_descent.py:188-194` to match implementation (drop `|| sub_agent_idx` promise). NO contract extension; preserves CPAuditLedgerEntry shape; documents the join-key reduction.
  - **(b) Structural extension (Class 3 §4.1 / §2.7.6 Class 1 — halt-execution back-flow).** Extend `CPAuditLedgerEntry` to carry `child_index: int | None` + `brief_hash: str | None` (or introduce a distinct `CPDispatchAuditLedgerEntry` carrier sum-typed against the HITL `CPAuditLedgerEntry`). Requires upstream CP spec contract revision at C-CP-16 §16.2 — discriminator (b) fires. Conditional escalation: **if operator selects path (b), this finding is a §4.1 Class 3 / §2.7.6 Class 1 fork** requiring CP spec re-clearance before downstream landing.

### F2-02 — CPAuditLedgerEntry shape carries HITL response palette, repurposed for dispatch via undocumented `response="approve"` convention

- **Location:** `Spec_Control_Plane_v1_7.md` §13.5.1 field-projection table rows 2-3 + 4-6 (`gate_level`, `response`, conditional hash fields); `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:188-205` (`emit_sub_agent_dispatch_audit`); `Spec_Harness_Runtime_v1.md` v1.7 §14.7.2 step 8a ("Returns CPAuditLedgerEntry per C-CP-13 §13.5 + C-CP-16 §16.2 (8-field shape with response-conditional optional hash fields)").
- **Defect:** `CPAuditLedgerEntry` is defined at C-CP-16 §16.2 as the HITL per-response audit shape — `response ∈ {approve, edit, reject, respond}` per the 4-response palette at C-CP-16 §16.1 (operator response to a HITL gate). Sub-agent dispatch reuses this carrier via the convention `response="approve"` (per code docstring: "A sub-agent dispatch is recorded as an `approve` response (no operator edit/reject/respond)"). The convention is NOT documented at CP spec v1.7 §13.5.1 nor at runtime spec §14.7.2 step 8a. The CP spec v1.7 §13.5.1 projects `response` → `audit.cp.response` as a verbatim pass-through; an OD-side audit-trace reader sees `audit.cp.response="approve"` for what was a sub-agent dispatch event, semantically distinct from a HITL approve. The OD spec v1.5 §24.6 recognition table preserves the same projection — the source-axis discriminator is "audit.cp.* presence", not "this was dispatch vs HITL".
- **Discriminator that classifies as Class 2:** (a) — substantive content gap. Runtime spec §14.7.2 step 8a + CP spec v1.7 §13.5.1 + OD spec v1.5 §24.6 each describe the field-projection but none acknowledge the dispatch repurposing convention. A reader of the audit ledger cannot distinguish "operator approved at HITL" from "sub-agent dispatched" by `audit.cp.response` alone.
- **Evidence:** Runtime spec §14.7.2 step 8a verbatim: "Returns `CPAuditLedgerEntry` per C-CP-13 §13.5 + C-CP-16 §16.2 (8-field shape with response-conditional optional hash fields)" — no dispatch-repurposing caveat. Code at `sub_agent_gate_level_descent.py:194-201` docstring: "A sub-agent dispatch is recorded as an `approve` response (no operator edit/reject/respond), so the three response-specific hash fields are absent" — convention is in code, not in spec.
- **Anti-fabrication attack engaged:** A1 (silent grounding collapse) — the spec claim references C-CP-16 §16.2 (HITL contract) verbatim; the dispatch reuse via convention is a content gap between cited contract scope and actual usage.
- **Axis-domain attack engaged:** CP-axis (per-response audit-ledger entry shape semantic integrity).
- **Resolution path:** Add NOTE at CP spec v1.7 §13.5.1 + OD spec v1.5 §24.6: "Sub-agent dispatch entries use `response='approve'` as a structural convention; semantic source discrimination at the OD audit-trace consumer is by `audit.cp.*` namespace AND by checking whether `entry_core` resolves to a `dispatch:*` action_id pattern at IS (per OD spec C-OD-24.4 + runtime spec §14.7.2 step 8b)." Alternative: introduce an explicit `audit.cp.event_kind ∈ {hitl_response, sub_agent_dispatch}` projection field at CP spec v1.7 §13.5.1 to discriminate at the namespace layer.

### F2-03 — Empty `timestamp` pass-through through the converter; spec claim of downstream population not honored

- **Location:** `Spec_Harness_Runtime_v1.md` v1.7 §14.7.2 step 8a; `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:200` (`timestamp=""`); `harness-cxa/src/harness_cxa/cp_audit_conversion.py:_project_namespace_attrs` (`audit.cp.timestamp = cp_entry.timestamp` verbatim).
- **Defect:** Runtime spec v1.7 §14.7.2 step 8a claims "The CP entry carries placeholder `timestamp` + `prior_event_hash` populated downstream by the converter / writer chain." In reality:
  - `emit_sub_agent_dispatch_audit` constructs the CP entry with `timestamp=""` (empty string; Pydantic field is `timestamp: str` with no constraint per `per_step_override_evaluator.py:81-82`, so empty passes validation).
  - The converter at `cp_audit_to_od_audit` projects `cp_entry.timestamp` directly into `audit.cp.timestamp` without populating.
  - No site in the 4-substep chain (8a → 8b → 8c → 8d) sets a real timestamp.
  - The persisted OD audit entry's `audit.cp.timestamp` is `""`.

  The placeholder claim at §14.7.2 step 8a is not honored by the chain it cites.
- **Discriminator that classifies as Class 2:** (a) — substantive: the chain doesn't honor the placeholder-population claim. Either the chain needs to populate (code fix at the dispatch composer using `ctx.time_source()`), or the spec claim needs to drop the "populated downstream" framing.
- **Evidence:** Code at `sub_agent_gate_level_descent.py:200`: `timestamp=""` literal. Converter at `cp_audit_conversion.py:72-80`: `attrs[f"{CP_AUDIT_NAMESPACE_PREFIX}.timestamp"] = cp_entry.timestamp` — direct pass-through with no population step.
- **Anti-fabrication attack engaged:** A5 (missing uncertainty signals — the spec asserts placeholder-population without source); A2 (silent scope narrowing — the chain step that would populate is absent from the cited 4-substep enumeration).
- **Axis-domain attack engaged:** CP-axis (audit-entry temporal anchoring per C-CP-13 §13.5).
- **Resolution path:** Either (i) populate timestamp at the composer — at step 8a, construct `cp_entry` with `timestamp=ctx.time_source().isoformat()`; OR (ii) amend runtime spec §14.7.2 step 8a to drop the "populated downstream by the converter / writer chain" claim and explicitly note the v1.7 MVP shape stores empty timestamp with downstream consumption via `entry_core → F2 entry.timestamp` (per OD spec v1.5 §24.4 opaque-marker resolution).

### F2-04 — OD spec v1.5 §24.5 canonical `compute_entry_hash` helper not materialized at the OD axis package; converter duplicates the recipe locally

- **Location:** `Spec_Operational_Discipline_v1_5.md` §24.5 (declares `compute_entry_hash(payload: AuditPayload) -> str` as the canonical OD-axis helper); `harness-od/src/harness_od/audit_ledger_types.py` + `multi_tenant_trace_separation_and_audit_ledger.py` (no `def compute_entry_hash` — verified via `grep -rn "def compute_entry_hash" harness-od/src/` returns empty); `harness-cxa/src/harness_cxa/cp_audit_conversion.py:_compute_entry_hash` (private duplicate with the same recipe).
- **Defect:** OD spec v1.5 §24.5 declares the canonical helper as the OD-axis spec authority for the entry-hash recipe per ADR-D5 v1.4 §1.4.1. The helper is not implemented in the `harness-od` package. The converter at `harness-cxa` defines its own private `_compute_entry_hash` with the recipe `hashlib.sha256(payload.model_dump_json().encode("utf-8")).hexdigest()` — byte-equivalent to the spec recipe, but not sourced from the canonical OD helper. Future drift risk: if the OD-axis recipe is amended (e.g., to a different canonicalization), the `harness-cxa` private helper would silently diverge.
- **Discriminator that classifies as Class 2:** (a) — substantive: spec promises a canonical OD-axis helper; helper doesn't exist at the OD package; recipe is duplicated at a sibling package without import dependency.
- **Evidence:** `grep -rn "def compute_entry_hash" harness-od/src/` returns no matches. `harness-cxa/src/harness_cxa/cp_audit_conversion.py:54-66` defines `_compute_entry_hash` privately.
- **Anti-fabrication attack engaged:** A4 (citation specificity — OD spec §24.5 cites a helper that exists in spec only).
- **Axis-domain attack engaged:** OD-axis (canonical entry-hash recipe ownership at the OD-axis package).
- **Resolution path:** Either (i) materialize `compute_entry_hash` at `harness-od/src/harness_od/audit_ledger_types.py` (or a sibling module) per the OD spec v1.5 §24.5 helper signature; refactor `harness-cxa/src/harness_cxa/cp_audit_conversion.py` to import from `harness_od` instead of defining `_compute_entry_hash` locally; OR (ii) amend OD spec §24.5 to NOTE "canonical recipe spec-anchored at v1.5; helper materialization at the OD package deferred to follow-on arc; converters MAY inline the recipe in the interim under the spec-canonical recipe constraint." Path (i) closes the drift risk; path (ii) preserves the current implementation and documents the gap.

### F2-05 — `brief_hash` computed at composer step 8a but discarded; spec dispatch-fact-key claim unmoored

- **Location:** `Spec_Harness_Runtime_v1.md` v1.7 §14.7.2 step 8a ("audit entries are dispatch-fact records keyed by `(parent_action_id, descent, brief_hash)` per C-CP-12 §12.5"); `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:183-187` + line 198 (`_ = brief_hash` — discarded); `Spec_Control_Plane_v1_7.md` §13.5.1 field-projection table (no `brief_hash` row).
- **Defect:** Runtime spec §14.7.2 step 8a constructs the `cp_entry` via `compose_dispatch_audit(parent_action_id, descent, brief_hash=ctx.handoff_registry.dispatch_response_hash(payload.brief))`. The function signature accepts `brief_hash`. The function body explicitly discards it (`_ = brief_hash` at line 198). The resulting `CPAuditLedgerEntry` carries no brief_hash field; CP spec v1.7 §13.5.1 field-projection table has no `brief_hash → audit.cp.brief_hash` row. The dispatch-fact-key invariant claimed at §14.7.2 step 8a per C-CP-12 §12.5 is structurally non-recoverable from the persisted audit entry — there is no place where brief_hash survives.

  Note: this is closely related to F2-01 (the action_id key) and F2-02 (the HITL shape carrier). All three reflect the same root: the carrier was designed for HITL responses (where action_id + gate_level + response palette + conditional hashes are sufficient), and the dispatch repurposing didn't extend the carrier to preserve dispatch-specific keying fields.
- **Discriminator that classifies as Class 2:** (a) — substantive: spec asserts a dispatch-fact-key invariant; the cited function discards a key component.
- **Evidence:** Code at `sub_agent_gate_level_descent.py:198`: `_ = brief_hash` (the underscore-discard idiom). CP spec v1.7 §13.5.1 field-projection table rows 1-7 enumerate `action_id`, `gate_level`, `response`, `edited_proposal_hash`, `rejection_reason_hash`, `response_text_hash`, `timestamp` — no `brief_hash` row.
- **Anti-fabrication attack engaged:** A2 (silent scope narrowing — the dispatch-fact-key claim cites a 3-tuple but the carrier preserves only the first element).
- **Axis-domain attack engaged:** CP-axis (dispatch-fact key invariant at C-CP-12 §12.5).
- **Resolution path:** Either (i) NOTE-amend runtime spec §14.7.2 step 8a to clarify that v1.7 MVP audit-entry preservation is a 2-tuple `(parent_action_id, "approve")` plus IS-anchored `entry_core` for sibling distinguishability; the brief_hash is consumed at `dispatch_response_hash(payload.brief)` for in-memory deduplication at the runtime composer but is NOT persisted to the audit ledger at v1.7 (defer brief_hash persistence to fan-out arc); OR (ii) extend `CPAuditLedgerEntry` to carry `brief_hash: str | None` + add a `audit.cp.brief_hash` projection row at CP spec v1.7 §13.5.1 (couples with path (b) of F2-01 — discriminator (b) fires under this resolution; §4.1 Class 3 / §2.7.6 Class 1 halt-execution back-flow).

---

## Class 1 findings (minor — documentation drift)

### F1-01 — Actor field name drift at runtime spec §14.7.2 step 8b vs. implementation

- **Location:** `Spec_Harness_Runtime_v1.md` v1.7 §14.7.2 step 8b (cites `actor=ctx.runtime_actor`); `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:477` (uses `actor=step_context.parent_actor`).
- **Defect:** Spec narrative cites `ctx.runtime_actor` for the F2 entry's actor field; implementation uses `step_context.parent_actor` (the actor on whose behalf this dispatch occurs per the IS Actor surface plumbed through `StepExecutionContext`). Already documented as Class 3 drift item per `.harness/class_3_tension_u_rt_59_spec_prose_drift.md` (per checkpoint memory); the v1.7 amendment did not absorb the correction.
- **Resolution:** Inline fix at runtime spec §14.7.2 step 8b: replace `ctx.runtime_actor` with `step_context.parent_actor` at next spec touch.

### F1-02 — OD spec v1.5 §24.4 example action_id format diverges from runtime spec §14.7.2 step 8b actual format

- **Location:** `Spec_Operational_Discipline_v1_5.md` §24.4 (example: `cp-audit:<cp_action_id>`); `Spec_Harness_Runtime_v1.md` v1.7 §14.7.2 step 8b (canonical: `dispatch:<parent_action_id>:<child_index>`).
- **Defect:** OD spec §24.4 says "At v1.5 the marker holds a string reference (typically the F2 entry hash or a constructed action_id like `cp-audit:<cp_action_id>` per the CP-sourced sub-namespace recognition at §24.6)". The example format `cp-audit:<cp_action_id>` does not match the runtime spec §14.7.2 step 8b canonical pattern `dispatch:<parent_action_id>:<child_index>`. The "typically" qualifier makes the format non-binding, but the example is misleading.
- **Resolution:** Inline fix at OD spec §24.4: replace the example with the canonical pattern from runtime spec §14.7.2 step 8b, OR drop the example and let the runtime spec own the format authoritatively.

### F1-03 — `c11-operator-local` SKILL.md broken citation at ADR-D5 §1.4 row 1 (self-flagged carry-forward)

- **Location:** `ADR-D5.md` §1.4 row 1 cites `c11-operator-local` SKILL.md as source of the `audit_ledger.sqlite` schema; file does not exist in this workspace.
- **Defect:** Citation chain integrity issue — the ADR's row 1 cites a SKILL.md that is absent. The ADR-D5 v1.4 change-note itself flags this as a Class 3 carry-forward ("§1.4 row 1 cites `c11-operator-local` SKILL.md as the source of the `audit_ledger.sqlite` schema. That SKILL.md file is not present in this workspace (verified at v1.4 authoring via `find . -name "c11*"`). The citation chain is broken; the SQLite commitment at v1.4 is therefore unanchored from its cited substrate. Reframed at v1.4 as a deferred-persistence-model carry-forward."). Per the ADR self-flag, the row was preserved verbatim with the broken citation deliberately deferred to future C11-style D-ADR authoring.
- **Resolution:** Acknowledge the self-flagged carry-forward; no action required at this review beyond surfacing for operator visibility. Future C11-style D-ADR authoring (or operator-self-redact arc) closes this.

---

## Findings considered and rejected (transparency)

The skill applied the following attacks to the bundle. Each entry is a check that did not surface a finding — the artifact handles the concern cleanly.

| Attack / check | Outcome |
|---|---|
| **A1 (silent grounding collapse)** | Bundle artifacts cite spec sections, ADR sections, and landed code paths throughout. No paraphrase-from-training-data; no unsourced claims. Rejected. |
| **A2 (silent scope narrowing on the arc scope)** | Operator ratified Path D + Path B-revised-a + runtime v1.7 + CP v1.8 each independently per `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` §10. The 5-artifact bundle covers exactly the surfaces ratified; no scope narrowing relative to the ratification chain. (Substantive narrowing within individual claims surfaced as F2-01 / F2-03 / F2-05; the arc-scope was correct.) |
| **A4 (fabricated citations)** | Spot-checked: CP spec v1.8 cites `b3d9368` for Path B-revised-a landing → commit resolves. CXA v2.4 §2.3.7 cites the discovery report at `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` → file exists. OD spec v1.5 §24 cites HEAD code at `harness-od/src/harness_od/audit_ledger_types.py` → code matches the lifted schema. Runtime spec v1.7 §14.7.2 step 8 cites CP spec v1.7 §13.5.1 + OD spec v1.5 C-OD-24 → both files resolve. ADR-D5 §1.4.1 cites OD spec v1.5 §24.5 → helper declared in spec (though not materialized at OD package per F2-04). Only the `c11-operator-local` SKILL.md citation breaks (F1-03), self-flagged. |
| **A5 (missing uncertainty signals)** | Phase-7 in-CLI specs do not tag claims with `[HIGH] / [MODERATE] / [SPECULATIVE]` per spec-writer skill convention (corpus discipline). The bundle uses *decided* prose with operator-ratification anchors; appropriate for landed work. The placeholder-population claim at F2-03 was the one substantive case where uncertainty was warranted but not surfaced — that's part of the F2-03 finding, not an A5-only gap. |
| **A7 (weak-source escalation)** | No `[HIGH]` confidence claims in the bundle to challenge. Rejected — not applicable. |
| **A8 (framing contamination — FM #8, highest-value attack vector)** | Bundle is internal harness work; no persona/stack/deployment overcommitment beyond `CLAUDE.md` framing. ADR-D5 §1.4 *removes* a prior SQLite architectural commitment in favor of JSONL-canonical — this is operator-ratified de-commitment, not contamination. Multi-LLM commitment unchanged. Stack commitments (Pydantic v2, hashlib stdlib) within CLAUDE.md §3.1. Rejected. |
| **A9 (cross-project context bleed)** | All citations resolve within this project's design-substrate + .harness substrate. No out-of-project framings; no "general best practice" claims without session-accessed source. Rejected. |
| **CXA edge classification check (CP→OD typed seam)** | v2.4 §2.3.7 classifies U-CP-28 → U-OD-00 as class G (genuine-typed-seam). Verified: CP spec v1.7 §13.5.1 names OD `AuditLedgerEntry` as converter output type; typed import physically resides at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` per Q5 ratification; G classification is correct per §0.3 taxonomy. |
| **CXA aggregate arithmetic check** | v2.4 §2.1: 22 → 23 genuine + 46 convention + 24 phase-2-runtime = 93 total. v2.3 was 92 + 1 new G = 93 ✓. CP outbound 55 → 56 (+1 to OD) ✓. v2.4 §2.2 acknowledges axis-level partial-order acyclicity (IS<AS<CP<OD) no longer holds; per-unit acyclicity preserved. Acknowledgment is correct; no arithmetic drift. |
| **ADR-D5 storage-form reconciliation logical consistency** | v1.4 §1.4 reclassifies SQLite as deferred-persistence-model (C11-style D-ADR); JSONL via IS state-ledger composition is v1.4 canonical. ADR-F2 §Decision + IS spec v1.3 §3 + OD spec v1.5 C-OD-24 all align. Per-persona-tier table preserved verbatim; only storage-form prose amended. The §1.4 SQLite schema extension table (4-column) is preserved verbatim as a Class-3-flagged carry-forward — self-flagged at change-note; not a new defect. |
| **OD spec v1.5 §24 contract count** | OD axis contract count grows 23 → 24 per the v1.5 change-note. Workspace `CLAUDE.md` §2.3 + OD plan v2.12 absorbed (per checkpoint memory). Counting discipline preserved. |
| **CP spec v1.7 NOTE 3 (cryptographic-payload-mismatch foreclosure)** | The converter signs the OD `AuditPayload` directly via `sign_audit_entry`; CP-side signatures are NOT re-projected. Verified at converter code: NOTE 3 commitment honored. |
| **Hash-chain integrity preservation (Q1 ratification)** | `CP prior_event_hash ≡ OD prior_entry_hash` per C-IS-06 + C-IS-13 §13.5. Converter pass-through verified at code line `attrs` projection; OD's hash-chain verification at `verify_hash_chain_integrity` consumes the CP-sourced value identically. Q1 honored. |
| **Entry_core source semantic (Q2(a) ratification)** | Runtime spec §14.7.2 step 8b writes F2 entry BEFORE composing audit entry; step 8c passes the resulting `StateLedgerEntryRef` to the converter. Implementation at `_compose_and_persist_audit` materializes the sequence. Q2(a) honored. |
| **Namespace prefix (Q4 ratification)** | All CP-sourced fields land under `audit.cp.*` per CP spec v1.7 §13.5.1 + OD spec v1.5 §24.6. Converter projects exactly the 7 enumerated fields (action_id, gate_level, response, conditional hashes, timestamp). Q4 honored. (The F2-02 finding is that the field projection inherits the HITL palette without dispatch-repurposing acknowledgment, not that the namespace prefix is wrong.) |
| **Decision-claim vocabulary** | Bundle uses *decided* throughout for landed work. F1 / F2 findings classified per the vocabulary — F2-01 / F2-02 / F2-03 / F2-04 / F2-05 are *proposing* (resolution path admits two readings; operator selects). F1-01 / F1-02 / F1-03 are *decided* (textual drift, no resolution ambiguity). |

---

## Disposition

**Cleared with current-phase spec revision per §4.1.2.**

The 5 Class 2 *proposing* findings (F2-01 through F2-05) cluster around a shared root cause: the `CPAuditLedgerEntry` carrier was designed for HITL response audits (C-CP-16 §16.2) and reused for sub-agent dispatch via convention (`response="approve"`, action_id repurposed, brief_hash discarded, timestamp left empty). The v1.7 amendment added the CP→OD converter on top of the existing carrier without surfacing the dispatch-repurposing semantic.

At v1.7 single-sub-agent MVP slice (per spec §14.7 invariant — fan-out emission foreclosed), the defects are latent: audit entries persist, the 4-substep chain executes end-to-end, and the 2283 workspace tests pass. The defects become observable at (a) fan-out arc landing (`audit.cp.action_id` collision across siblings; F2-01) or (b) cross-side CP↔OD audit-trace join exercise (`audit.cp.timestamp=""`; F2-03; brief_hash absent at audit consumer; F2-05).

**Recommended resolution path (operator selects):**

- **Path (i) — NOTE-form clarification patch (Class 2 inline).** Author a runtime spec v1.8 + CP spec v1.9 (Form A NOTE-reference patch) + OD spec v1.6 §24.5 helper materialization. Documents the dispatch-repurposing convention; clarifies that sibling distinguishability is via `entry_core` (not `audit.cp.action_id`); drops the placeholder-population claim OR populates timestamp at the composer; materializes the OD canonical helper and refactors the converter to import. Preserves `CPAuditLedgerEntry` shape; no upstream-phase revision; no §2.7.6 halt-execution.
- **Path (ii) — Structural extension (Class 3 §4.1 / §2.7.6 Class 1).** Extend `CPAuditLedgerEntry` to carry `brief_hash: str | None` + `child_index: int | None` OR introduce a distinct `CPDispatchAuditLedgerEntry` carrier sum-typed against the HITL shape. Requires CP spec C-CP-16 §16.2 contract revision (upstream phase) → §2.7.6 Class 1 halt-execution back-flow per workspace `CLAUDE.md` §4.3.

The 3 Class 1 drifts (F1-01 actor field; F1-02 OD §24.4 example format; F1-03 self-flagged broken citation) absorb inline at the next spec touch.

**No systemic pattern surfacing for workflow §7 session-prompt-template revision.** The defect cluster (F2-01/02/05) shares a root cause but is contained within a single arc's contract surface. Resolution is a focused spec patch, not a workflow-level repair.

**No §2.7.6 Class 1 halt-execution surfaced at path (i).** No §4.1 Class 3 findings. The arc's implementation landing at `5407c0d` and the batch 6 retirement audit at `55a93da` both stand. The findings recommend a follow-on spec-revision arc against the bundle, not a Phase-7 halt or rollback.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/adversarial_review_u_rt_59_fork_2_spec_bundle.md` |
| Authored at | Phase 7 sub-phase 7b/7c, 2026-05-20 (post-implementation-arc-landing pre-retirement-audit-batch-6) |
| Authoring authority | `harness-adversarial-reviewer` skill (Phase-7 pre-implementation review mode applied post-landing per operator request) |
| Scope | U-RT-59 Fork 2 spec arc bundle: runtime spec v1.7 + CP spec v1.7/v1.8 + ADR-D5 v1.4 + OD spec v1.5 (C-OD-24) + CXA v2.4 (§2.3.7) |
| Artifacts NOT reviewed | Workspace `CLAUDE.md` (root + per-axis); the implementation arc commit `5407c0d` (reviewed only for spec-vs-code reconciliation evidence); the Phase-7d retirement event batches 1-6 (reviewed only for finding-corroboration context) |
| Disposition | Cleared with current-phase spec revision per §4.1.2 — Class 2 *proposing* findings recommend a NOTE-form patch (path (i)) or structural extension (path (ii) — conditional Class 3); Class 1 drifts fix inline |
| Successor consumption | Operator selects resolution path; if path (i), a runtime spec v1.8 + CP spec v1.9 + OD spec v1.6 patch arc opens; if path (ii), a §2.7.6 Class 1 fork files against CP spec C-CP-16 §16.2 contract |
| Forward-only ledger discipline | Preserved — this review does not modify the artifacts under review; it produces a finding-classified report only |

---

*End of adversarial review of the U-RT-59 Fork 2 spec arc bundle. 0 Class 3 + 5 Class 2 (*proposing*) + 3 Class 1 findings; 14 rejected-finding transparency entries; cleared with current-phase spec revision recommendation.*
