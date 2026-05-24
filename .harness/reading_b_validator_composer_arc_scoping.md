# Reading B — Validator-composer arc full-scope architectural scoping recommendation

**Filed:** 2026-05-24 at HEAD `0459a3d` (post Reading-A absorption batch-17; runtime spec v1.21; CP spec v1.13; OD spec v1.11; CXA v2.9).
**Mode:** Systems-architect Mode 3 — Phase-7 architectural-tension-resolution recommendation under skill §4A discipline.
**Scope:** Reading B at `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` §3.2 — the full validator-composer arc currently deferred at runtime spec v1.21 §14.8.2 steps 3 / 4c / 4d.
**Status:** RECOMMENDATION — operator decides per §6. Does NOT edit spec/plan/ADR. Does NOT extend H_T design (I-2 / X-AL-3).
**Filing trigger:** Operator authorization to proceed on prior-checkpoint Item #6 + advisor sanity-check confirming the fork doc's 8-15-commit estimate predates Reading A landing and warrants re-scoping against current canonical state.

---

## 1. Framing of Reading B scope at current baseline

### 1.1 What has changed since fork doc filing (2026-05-24 at HEAD `4479b07`)

| Surface | At fork filing | At HEAD `0459a3d` | Reading-B impact |
|---|---|---|---|
| Runtime spec | v1.17 | **v1.21** | All 6 §14.8.2 deferrals PRESERVED VERBATIM through v1.18 (Reading A) / v1.19 (cite-cascade) / v1.20 (AdvReview F1-01) / v1.21 (C-RT-24 pause/resume) — verified by direct grep. Reading-A scope discipline held end-to-end. |
| CP spec | v1.11 | **v1.13** | §28 / C-CP-28 ValidatorFramework renamed from v1.10 NEW §25 per `[[fork-cp-spec-section-25-contract-id-collision]]` Reading A. C-CP-28 §25.x sub-section structure preserved verbatim (delta-only-spec convention). |
| OD spec | v1.9 | **v1.11** | §C-OD-30.4 NEW PauseResumeAuditPayload helper-contract (orthogonal to validator arc). `validator.*` observability namespace at §C-OD-29 unchanged. |
| CXA | v2.6 | **v2.9** | §2.3.7 row 8 NEW cost-attribution audit-write seam (orthogonal). ValidatorFramework→OD edge at row 6 (C-CP-28 §25.5 producer spec cite bumps applied at v2.8 for cite-cascade — no semantic change). |
| `workflow_driver.py:668` | Stub branch unreachable in production (no factory) | **Reachable** via C-RT-23 stage-4 factory landed at v1.18. `ctx.validator_framework` ingested per operator-supplied `RuntimeConfig.validator_framework_config`. CP-21 RETIRED at batch-17. |
| C-RT-24 pause/resume | Not yet filed | **Landed** at v1.21 §14.14. Sibling stage-5 factory pattern + driver per-step pre-entry detection. Orthogonal to validator arc — confirmed no interaction. |

### 1.2 Already-authored canonical surfaces Reading B consumes (NOT re-authors)

| Surface | Site | Reading-B consumption role |
|---|---|---|
| **4-axis `_hitl_required` composition** | C-CP-19 §19.1 (CP spec v1.2 line 1618, preserved verbatim through v1.13) | Runtime spec step 4c replaces `placement.requires_hitl` shortcut with full `_hitl_required(persona_tier, blast_radius_tier, server_trust_tier, per_tool_gate_level)` evaluation. Composition rule already fully specified. |
| **`_hitl_required` runtime evaluation surface** | C-CP-19 §19.4 (line 1676) | Returns `gate_level ∈ {ask, deny}` → True. Palette restriction for `deny` outcome (`{reject, respond}` — removes `approve` AND `edit`). |
| **Cross-trust-boundary palette restriction** | C-CP-21 §21.3 (line 1880) | Fires when validator-escalation HITL composes with cross-family active / local-terminal active / untrusted-MCP. Palette restricted to `{approve, reject, respond}` (removes `edit` ONLY). |
| **5-class ValidatorOutcome enum** | C-CP-28 §25.2 (CP spec v1.10 NEW §25, renamed §28 at v1.13) | `PASS` / `REVALIDATE` / `ESCALATE` / `PERMANENT_FAIL` / `OPERATOR_BURDEN_EXCEEDED`. ValidatorOutcome → ValidatorNextAction mapping at §25.2 (operator-ratified 2026-05-21). |
| **HITLEscalationBrief typed payload** | C-CP-28 §25.2 (line 199-210) | `parent_step_id` + `parent_action_id` + `fail_class` + `fail_detail_hash` + `escalation_reason` + `proposed_response_palette: frozenset[HITLResponse]` (default = full palette per C-CP-16 §16.1). Validator can propose palette; composer consumes it. |
| **Validator post-dispatch hook lifecycle** | C-CP-28 §25.3 (line 212-216) | "At workflow_driver.py post-dispatch step, add pre-ledger-append validation hook: `evaluation = await ctx.validator_framework.evaluate(...); if evaluation.next_action != PROCEED: branch per-action`." Sync, post-dispatch, pre-ledger-append. |
| **ESCALATE invariant** | C-CP-28 §25.4 invariant 4 (line 225) + §25.7 invariant 4 (line 253) | **"ESCALATE always emits HITL gate. Escalation cannot be silently dropped."** |
| **validator.* span schema** | C-CP-28 §25.5 (line 230-237) | 4 spans: `validator.evaluate` + `validator.fail` + `validator.revalidation` + `validator.escalation`. `validator.escalation` links to subsequent `hitl.gate.evaluated` span via parent-context propagation. All head=1.0 always-sampled. |
| **OD-side validator namespace** | OD spec §C-OD-29 (declared) + ADR-D6 v1.2 §1.2 `validator.fail.*` namespace row | No OD-side authoring owed at Reading B. Existing observability surfaces consume the validator spans. |

### 1.3 Architectural delta Reading B introduces (the actual new work)

Reading B authors at the **runtime-spec layer only**: the *consumption shape* of the already-authored CP+OD surfaces — i.e., runtime composer-body extensions at §14.8.2 + a new mid-step re-entrant HITL composition surface for validator-escalation. No new CP contract authoring. No new OD contract authoring. No new ADR. No new CXA seam (the C-CP-28 §25.5 → OD `validator.*` flow is an existing CXA edge).

The runtime composer at §14.8.2 today is **wrap-time** — composes a `HITLGatedDispatcher` around the inner `StepDispatcher` BEFORE step dispatch. Reading B introduces a **mid-step re-entrant** path: when `ctx.validator_framework.evaluate(...)` at workflow_driver post-dispatch returns `ValidatorOutcome ∈ {ESCALATE, OPERATOR_BURDEN_EXCEEDED}`, the HITL gate composer is re-invoked with a synthetic `VALIDATOR_ESCALATION` placement carrying the `HITLEscalationBrief` payload.

This is a NEW runtime-spec composition pattern but is fully determined by C-CP-28's existing lifecycle commitments (§25.3 + §25.4 invariant 4). Reading B authors the runtime-spec shape that consumes them.

---

## 2. Per-Q recommendation with confidence + tiebreaker chain

### Q1. VALIDATOR_ESCALATION emission timing — **(α) sync mid-step re-entry [HIGH]**

**Recommendation:** Sync mid-step re-entry. `ValidatorFramework.evaluate(...)` at workflow_driver post-dispatch returns; if `next_action == ESCALATE_HITL`, the HITL gate composer is re-invoked synchronously within the same step, before any state-ledger entry is appended.

**Authority-chain anchors (3 convergent):**

1. **C-CP-28 §25.3** (CP spec v1.10 line 213, preserved at v1.13): "**Workflow-driver integration:** At `workflow_driver.py` post-dispatch step (currently `_append_step_ledger_entry`), add pre-ledger-append validation hook: `evaluation = await ctx.validator_framework.evaluate(...); if evaluation.next_action != PROCEED: branch per-action`." — explicit *sync, post-dispatch, pre-ledger-append* ordering.

2. **C-CP-28 §25.4 invariant 2** (line 223): "**Validation runs after dispatch, before ledger append.** State-ledger entry is the canonical commit point per C-IS-05 §5." — async (β) would commit ledger before HITL fires, contradicting this invariant.

3. **C-CP-28 §25.4 + §25.7 invariant 4** (line 225 + line 253): "**ESCALATE always emits HITL gate. Escalation cannot be silently dropped.**" — async queueing at next-step boundary (β) creates a window in which the workflow could terminate or pause without firing the gate. Sync re-entry forecloses this.

**Why options (β) and (γ) are rejected:**
- **(β) async next-step boundary** contradicts C-CP-28 §25.4 invariant 2 ordering. Would require canonical-commit-then-gate, inverting the spec's commit-after-gate semantics.
- **(γ) typed-error-driven** conflates *mechanism* with *timing*. The spec already returns `ValidatorEvaluation` envelope via `await` (sync), not raises. (γ) is a mechanism choice within (α)'s sync timing; not a competing timing option.

**Tiebreaker check (single verifiable fact making this determinate):** Confirm `grep -n "after dispatch, before ledger append\|pre-ledger-append validation hook\|cannot be silently dropped" design-substrate/Spec_Control_Plane_v1_10.md` returns hits at §25.3 + §25.4. Verified empirically this session at lines 213, 223, 225.

**§2 discipline:** Control-plane axis (HITL composition timing); deterministic side of the prob-det boundary (the synchronous post-dispatch hook IS the deterministic gate); D-level decision (derivative of F-ADR-F2 state-ledger ordering + ADR-D1 v1.2 HITL primitive).

**Implication for runtime-spec amendment:** Reading B authors §14.8.2 step 4-bis (new sub-step): post-dispatch validator-escalation re-entry path. The wrap-time composer at step 4 is preserved; the mid-step composer is a SECOND invocation surface within the same step. The HITLEscalationBrief.proposed_response_palette flows through as the operator-presentation palette (composed with §21.3 cross-trust restriction + §19.4 deny-row restriction as union).

---

### Q2. Cross-trust-boundary palette restriction cite-shape — **(c) verify UNION surface [HIGH] with caveat**

**Recommendation:** The two palette-restriction surfaces (C-CP-19 §19.4 `deny`-row + C-CP-21 §21.3 cross-trust-boundary) are **structurally distinct restrictions that compose in union direction at step 4d**. The runtime spec §14.8.2 step 4d cite to "C-CP-19 §19.4" is **partially correct but incomplete** — it cites the right canonical for the `deny`-row restriction but omits §21.3 for the cross-trust-boundary restriction.

**Empirical reading of both surfaces:**

| Surface | Palette restriction | Trigger condition |
|---|---|---|
| C-CP-19 §19.4 `deny` row | `{reject, respond}` (removes `approve` AND `edit`) | `gate_level(tool, server, persona_tier) == deny` per §19.1 4-axis `max()` |
| C-CP-21 §21.3 cross-trust-boundary | `{approve, reject, respond}` (removes `edit` ONLY) | Validator-escalation HITL + (cross-family active OR local-terminal active OR untrusted-MCP active) |

These are **two distinct restrictions that fire under different conditions**. They are NOT in conflict — they compose in the most-restrictive direction:

- If `gate_level == deny` AND cross-trust-boundary active → palette = `{reject, respond}` (intersection: `{reject, respond}` ∩ `{approve, reject, respond}` = `{reject, respond}`).
- If `gate_level == deny` AND no cross-trust-boundary → palette = `{reject, respond}` (§19.4 alone).
- If `gate_level == ask` AND cross-trust-boundary active → palette = `{approve, reject, respond}` (§21.3 alone).
- If `gate_level == ask` AND no cross-trust-boundary → palette = `{approve, edit, reject, respond}` (full palette per C-CP-16 §16.1).

**Authority-chain anchor:** C-CP-21 §21.3 (CP spec v1.2 line 1880, preserved verbatim through v1.13) is the canonical home for cross-trust-boundary restriction. C-CP-19 §19.4 (line 1676) is the canonical home for the `deny`-row palette restriction. The runtime spec cite at v1.21 §14.8.2 step 4d ("per C-CP-19 §19.4") is **cite-incomplete** under the empirical surface inventory.

**Tiebreaker check:** Confirm `grep -n "{reject, respond}\|{approve, reject, respond}" design-substrate/Spec_Control_Plane_v1_2.md` returns hits at line 1690 (§19.4 deny) AND line 1882 (§21.3 cross-trust). Verified empirically this session.

**§2 discipline:** Control-plane axis (HITL response-palette composition); deterministic side (palette is a deterministic function of gate-level + cross-trust state); D-level (derivative of C-CP-16 §16.1 palette enumeration + C-CP-19 / C-CP-21 restriction surfaces).

**Caveat (sub-finding for §6 operator decision):** The runtime spec §14.8.2 step 4d cite is a CITE-COMPLETENESS bug that predates Reading A. Two routing options:
- **(c-i)** Absorb the cite-completeness fix into Reading B's broader runtime-spec amendment with explicit change-note line. Recommended — single arc, fewer doc transits, semantics identical at landing.
- **(c-ii)** File as separate Class 1 cite-correction fork (analogous to `[[fork-cp-spec-section-25-contract-id-collision]]` shape). Adds bookkeeping overhead for what is fundamentally a cite-completeness patch absorbed naturally into the Reading B scope.

**Recommendation: (c-i)** — absorb into Reading B's amendment with change-note line at v1.21 → v1.22.

**Implication for runtime-spec amendment:** §14.8.2 step 4d re-authored to consume BOTH §19.4 deny-row + §21.3 cross-trust-boundary in union order. Cite-shape corrected at the same amendment. New runtime-spec helper: `compute_effective_palette(gate_level, cross_trust_state, validator_escalation_brief) → frozenset[HITLResponse]`.

---

### Q3. Reading B scope envelope — **(i) runtime-spec-only amendment v1.21 → v1.22 [HIGH]**

**Recommendation:** Runtime-spec-only amendment. All required canonical surfaces (C-CP-19 §19.1 + §19.4 + C-CP-21 §21.3 + C-CP-28 §25.2/§25.3/§25.4/§25.5/§25.7 + OD §C-OD-29 + ADR-D6 v1.2 `validator.*` namespace) are already authored. Reading B authors the *consumption shape* at runtime spec — composer body extension + new mid-step re-entrant composition surface + fail-class taxonomy update.

**Authority-chain anchors (per §1.2 surface inventory):**

1. **No CP spec amendment owed.** The validator framework's HITL-emission contract is fully specified at C-CP-28 §25.2 + §25.3 + §25.4 invariant 4 + §25.7 invariant 4. The 4-axis composition + palette restriction surfaces at C-CP-19 §19.1 / §19.4 / C-CP-21 §21.3 are fully specified. Reading B consumes; does NOT extend.
2. **No OD spec amendment owed.** §C-OD-29 namespace + ADR-D6 v1.2 `validator.fail.*` + `hitl.*` rows already cover all observability surfaces Reading B introduces.
3. **No ADR amendment owed.** ADR-D5 v1.3 §1.5 (4-axis composition) + §1.10 (5-class fail taxonomy + cross-trust palette) anchor C-CP-19/21. ADR-D1 v1.2 (HITL primitive) + ADR-D6 v1.2 (observability) anchor the runtime surfaces. No F-level commitment touched.
4. **No CXA amendment owed.** The ValidatorFramework→OD edge at CXA v2.9 §2.3.7 (row 6 per v2.6 enumeration) is existing seam; Reading B's spans flow through unchanged.

**Tiebreaker check:** Confirm `grep -rn "ESCALATE\|HITLEscalationBrief\|ValidatorOutcome" design-substrate/Spec_Operational_Discipline_v1_11.md design-substrate/Cross_Axis_Composition_Document_v2_9.md design-substrate/ADR-D*.md` returns ONLY downstream consumption sites (OD validator.* attribute schema, CXA edge declaration, ADR-D5 escalation order text) — no contract authoring gaps. Recommended to verify before spec-writer arc opens.

**§2 discipline:** Cross-axis verification (§2.5) — Action surface ↔ Operational discipline tension: Reading B's mid-step re-entry could create span-parent-context inconsistency between `validator.escalation` (CP-axis emitter) and `hitl.gate.evaluated` (CP-axis emitter, OD-axis namespace ownership per ADR-D6 v1.2). Resolution: C-CP-28 §25.5 already commits "Links to subsequent `hitl.gate.evaluated` span via parent-context propagation". Tension resolved at canonical spec.

**Estimate:** **3-5 commits** (down from fork doc's 8-15-commit estimate):
- 1 spec commit — runtime spec v1.21 → v1.22 with §14.8.2 step 3 + step 4c + step 4d amendments + NEW C-RT-NN ValidatorEscalationGateComposer contract surface
- 1 plan commit — runtime plan v2.20 → v2.21 NEW cluster L9-duodecies (2-3 units)
- 2-3 impl commits — per-unit landing
- (Optional 1 retirement-event filing — no RETIRE-READY transitions forced by Reading B per §5 cascade analysis)

---

### Q4. OD-side amendment — **(NO amendment) [HIGH]**

**Recommendation:** No OD spec amendment owed. C-CP-28 §25.5 already commits the 4 validator spans + parent-context propagation to `hitl.gate.evaluated`. ADR-D6 v1.2 §1.2 namespace map declares `validator.fail.*` + `hitl.*` rows. OD spec §C-OD-29 declares the namespace consumption surface.

**Could OD widening be valuable?** Possibly — a new `gate.composition.evaluated` span recording each axis floor + final gate level would provide deeper observability into the 4-axis composition. However:
1. This is **observability convenience**, not Reading B's load-bearing scope.
2. C-CP-19 §19.4 doesn't currently commit such a span at the spec layer; introducing it is X-AL-3-adjacent (new H_T primitive at execution time).
3. If valuable, it's a separate post-Reading-B arc routed through proper Phase 5/6 channels.

**Recommendation: NO OD amendment at Reading B scope.** Surface gate-composition observability as a possible adjacent finding for future scoping.

**Tiebreaker check:** Confirm `grep -n "validator\\|hitl\\|gate" design-substrate/Spec_Operational_Discipline_v1_11.md` returns the existing §C-OD-29 / §C-OD-30 sections sufficient for current Reading-B span emission. Owed at spec-writer arc opening if not pre-verified here.

**§2 discipline:** Operational discipline axis (observability); deterministic side; I-level (independent — does not constrain or block other axes; can be added later without rework).

---

### Q5. `RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19` retirement — **(replace with explicit support, no retirement footer) [HIGH]**

**Recommendation:** At runtime spec v1.21 → v1.22, the `RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19` fail class entry (line 2070) is **replaced** with an entry documenting VALIDATOR_ESCALATION is now supported (no permanent fail class needed — VALIDATOR_ESCALATION emission is a success path, not a failure). Old fail class is REMOVED from the active taxonomy; v1.21 → v1.22 change-note records the removal with explicit "retired-at-spec-text per Reading B landing".

**Why not preserve as historical footer:** The fail class describes a v1.9-MVP foreclosure that no longer applies post-Reading-B. Preserving it would require a "retired-but-documented" note that adds maintenance burden without informational value (the change-note already records what changed). The runtime spec's delta-only convention handles historical preservation via the version chain.

**Authority-chain anchor:** Per `spec-writer` skill §3.2 discipline (fail-class retirement at spec amendment), a fail class that describes a foreclosed surface is removed at the amendment that removes the foreclosure. Reading B IS the amendment that removes the foreclosure.

**Tiebreaker check:** Confirm `grep -n "RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19" design-substrate/Spec_Harness_Runtime_v1.md` returns only the single failure-mode taxonomy row at line 2070 (no other internal cite-dependents). Verified — single site.

**Implication for spec-writer + plan absorption:**
- spec-writer arc: remove fail class at §14.8 failure-mode taxonomy; record removal in v1.21 → v1.22 change-note.
- implementation-planner arc: U-RT-60 (HITL gate composer) AC #N referencing the fail class (if any) STRUCK; new ACs covering VALIDATOR_ESCALATION emission path.

**§2 discipline:** Operational discipline axis (failure-mode taxonomy); deterministic side; D-level.

---

## 3. Design-substrate amendment shape

| Artifact | Current version | Reading-B version | Amendment shape |
|---|---|---|---|
| `Spec_Harness_Runtime_v1.md` | v1.21 | **v1.22** | §14.8.2 step 3 — un-foreclose VALIDATOR_ESCALATION (raise removed; placement-trigger evaluator returns match for VALIDATOR_ESCALATION). §14.8.2 step 4c — replace `placement.requires_hitl` shortcut with full 4-axis `_hitl_required(persona_tier, blast_radius_tier, mcp_server_trust_tier, per_tool_gate_level)` evaluation per C-CP-19 §19.1. §14.8.2 step 4d — replace `DEFAULT_FULL_PALETTE` with `compute_effective_palette(gate_level, cross_trust_state, validator_escalation_brief)` consuming UNION of C-CP-19 §19.4 deny-row + C-CP-21 §21.3 cross-trust-boundary per Q2(c-i) recommendation; cite-shape corrected from "per C-CP-19 §19.4" to "per C-CP-19 §19.4 + C-CP-21 §21.3 union". NEW §14.8.NN (or §14.13.NN as sibling to ValidatorFramework binding-chain factory) — C-RT-NN ValidatorEscalationGateComposer contract surface: post-dispatch re-entrant composer fired at workflow_driver post-dispatch hook when `ValidatorEvaluation.next_action == ESCALATE_HITL`; consumes `HITLEscalationBrief.proposed_response_palette` + composes with effective-palette computation. §14.8 failure-mode taxonomy — REMOVE `RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19` fail class. §0.6 Q5 ratification — REVERSE per Q1 recommendation. v1.21 → v1.22 change-note documents all 5 amendment sites + Reading B operator authorization at fork doc §3.2 + this scoping doc cite. |
| `Implementation_Plan_Harness_Runtime_v2_20.md` | v2.20 | **v2.21** | NEW L9-duodecies cluster (2-3 units, per §4 below). |
| `Spec_Control_Plane_v1_13.md` | v1.13 | (unchanged) | NO amendment owed. All surfaces consumed by Reading B already authored. |
| `Spec_Operational_Discipline_v1_11.md` | v1.11 | (unchanged) | NO amendment owed per Q4. |
| `Cross_Axis_Composition_Document_v2_9.md` | v2.9 | (unchanged) | NO amendment owed per §5 cascade analysis — existing ValidatorFramework→OD edge consumes Reading B spans unchanged. |
| ADR-D1 v1.2 / D5 v1.4 / D6 v1.2 | (current) | (unchanged) | NO ADR amendment owed — F-level commitments preserved. |

**Single-axis amendment scope.** This is the materially smaller envelope vs fork doc's worst-case multi-axis 8-15-commit estimate.

---

## 4. Implementation-plan cluster shape

**Cluster name:** L9-duodecies (12th L9-N cluster in runtime plan v2.21).

**Unit decomposition (3 atomic units recommended):**

### U-RT-NN-A — Effective-palette computation + 4-axis `_hitl_required` consumption

| Field | Value |
|---|---|
| Implements | Runtime spec v1.22 §14.8.2 step 4c (full 4-axis consumption) + step 4d (UNION palette computation per Q2(c-i)) |
| Files | `harness-runtime/src/harness_runtime/hitl/effective_palette.py` NEW + `harness-runtime/src/harness_runtime/hitl/hitl_required_consumption.py` NEW (4-axis helper consuming CP carriers) |
| Signatures | `compute_effective_palette(gate_level: GateLevel, cross_trust_state: CrossTrustState, validator_escalation_brief: HITLEscalationBrief | None) → frozenset[HITLResponse]` + `evaluate_hitl_required(persona_tier: PersonaTier, blast_radius_tier: BlastRadiusTier, server_trust_tier: McpServerTrustTier, per_tool_gate_level: GateLevel) → bool` |
| Depends on | C-CP-19 §19.1/§19.4 carriers + C-CP-21 §21.3 carriers + C-CP-16 §16.1 HITLResponse enum + C-CP-17 §17.x placement carrier (already landed at U-CP-43+ at HEAD) |
| ACs | (1) `compute_effective_palette` returns correct UNION-intersection per truth table at §2 Q2 (4-case test matrix). (2) `evaluate_hitl_required` returns `True` iff `max(4 axes) ∈ {ask, deny}` per §19.4. (3) Both helpers are pure functions (no I/O, no side effects). (4) Pyright strict 0 errors. |

### U-RT-NN-B — ValidatorEscalationGateComposer + post-dispatch re-entry

| Field | Value |
|---|---|
| Implements | Runtime spec v1.22 NEW C-RT-NN ValidatorEscalationGateComposer contract; §14.8.2 step 3 un-foreclosure |
| Files | `harness-runtime/src/harness_runtime/hitl/validator_escalation_composer.py` NEW + `harness-cp/src/harness_cp/workflow_driver.py` AMEND (post-dispatch hook branches `ValidatorEvaluation.next_action == ESCALATE_HITL` → invoke composer) |
| Signatures | `async def compose_validator_escalation_gate(ctx: HarnessContext, brief: HITLEscalationBrief, step_action_id: str) → HITLResponse` |
| Depends on | U-RT-NN-A (effective-palette + `_hitl_required`); C-CP-28 §25.2 HITLEscalationBrief carrier (already landed); existing §14.8 HITL gate composer surface (C-RT-18 — partial re-use of `RuntimeHITLGateComposer.compose_gate(...)` mechanics with VALIDATOR_ESCALATION placement injection); REMOVE `HITLPlacementForeclosedAtV19Error` raise path at §14.8.2 step 3. |
| ACs | (1) Composer fires synchronously within step on `ValidatorOutcome ∈ {ESCALATE, OPERATOR_BURDEN_EXCEEDED}` per C-CP-28 §25.2 mapping. (2) `HITLEscalationBrief.proposed_response_palette` is composed with `compute_effective_palette` per Q2 UNION-intersection. (3) `validator.escalation` span emitted per C-CP-28 §25.5; parent-context links to subsequent `hitl.gate.evaluated` span. (4) C-CP-28 §25.4 invariant 4 ("ESCALATE always emits HITL gate") empirically verified — no execution path silently drops escalation. (5) `RT-FAIL-HITL-PLACEMENT-FORECLOSED-AT-V19` fail class REMOVED from §14.8 failure-mode taxonomy + no raise sites in code. |

### U-RT-NN-C — End-to-end VALIDATOR_ESCALATION cycle test

| Field | Value |
|---|---|
| Implements | Runtime spec v1.22 §14.8.2 + C-RT-NN composer e2e exercise through `harness_runtime.api.run(...)` production bootstrap |
| Files | `harness-runtime/tests/test_validator_escalation_e2e.py` NEW |
| Test shape | Operator-supplied `ValidatorFrameworkConfig` + concrete validator returning `ValidatorOutcome.ESCALATE` + ESCALATION palette assertion (UNION-intersected per cross-trust + gate-level state) + HITL surface stub capturing `proposed_response_palette` + validator-escalation span emission verified via in-process OTel exporter. Mechanism α default (in-process deterministic ESCALATE fixture; no LLM in loop) per U-RT-85 + U-RT-89 precedent. |
| Depends on | U-RT-NN-A + U-RT-NN-B; existing C-RT-23 stage-4 factory (U-RT-83/84/85 landed); existing HITL gate composer (U-RT-60 landed) |
| ACs | (1) Validator returning `ESCALATE` triggers HITL gate composer mid-step. (2) HITL surface receives correct UNION-intersected palette under 4 test cases (gate_level × cross_trust 2x2 matrix). (3) `validator.escalation` span emitted with `step.id` + `validator.outcome` attributes + parent-context to `hitl.gate.evaluated`. (4) State-ledger entry append blocked until HITL gate resolves (per C-CP-28 §25.4 invariant 2). (5) All 4 validator spans (`validator.evaluate` + `validator.fail` + `validator.escalation` + `hitl.gate.evaluated`) emitted with head=1.0 sampling per C-CP-28 §25.5. |

**Within-cluster edges (3):** A → B → C (B depends on A; C depends on B; A independent).

**Cluster-boundary edges (multiple) to already-landed substrate:**
- C-RT-23 stage-4 factory (U-RT-83/84/85 at L9-decies — already landed at `3005643`/`d55fbd7`/`37e9d67`)
- C-CP-28 ValidatorFramework body (U-CP-58/59/60/61 cluster 10-CP-A — already landed at `16cf6d7`/`cdf83b1`/`5ca86aa`/`9b009d3`)
- HITL gate composer C-RT-18 (U-RT-60 — already landed at `e9b9c49`)
- 4-axis `_hitl_required` declarative library (C-CP-19 §19.1 + U-CP-43 declarative library — already landed at HEAD; verify before spec-writer arc opens)
- C-CP-21 §21.3 palette-restriction carrier (verify if CP-axis impl exposes a typed `cross_trust_state` carrier or whether runtime layer composes it)

**Estimate within plan cluster:** 2-3 commits within cluster + 1 plan commit + 1 spec commit = **3-5 commits total** for Reading B.

**Adjacent unit considerations:**
- U-RT-60 (HITL gate composer L9-quinquies) — possibly AC amendments if VALIDATOR_ESCALATION foreclosure removal affects its ACs. Likely 1 AC re-decomposition; absorbed at plan revision.

---

## 5. Cross-axis cascade analysis

Per skill §2.5 cross-axis integration verification:

| Cascade endpoint | Cascade trigger | Resolution |
|---|---|---|
| CXA v2.9 §2.3.7 ValidatorFramework→OD edge | NO change — existing edge consumes Reading B spans. Per CXA v2.6 enumeration row 6: `C-CP-28 §25.5` → OD `validator.*` namespace. Reading B emits the canonical spans the edge already enumerates. | NO CXA amendment owed. |
| Other RETIRE-READY rows | NO Reading B-forced retirement transitions per fork doc §5. CP-21 already RETIRED at batch-17 via Reading A. | No retirement-event filing forced by Reading B landing. (Operator may file an opt-in retirement event re: VALIDATOR_ESCALATION support if a substitution row covers it.) |
| Other PARTIAL rows | NO cascade — CP-22 (PauseResumeProtocol) already RETIRED at batch-18. Other CP-PARTIAL rows (CP-8/9/11/14/17/19) on independent carrier-gates. | No retirement-state intersection. |
| Action-surface axis | NO cascade — AS-axis touches sandbox/MCP-trust at C-AS-10/12; Reading B consumes these surfaces (cross-trust state evaluation) but does not author new AS-axis primitives. | NO AS spec or plan amendment owed. |
| Information-substrate axis | NO cascade — IS-axis owns state-ledger; Reading B consumes `ctx.state_ledger_writer` (existing) for post-HITL-gate ledger append per C-CP-28 §25.4 invariant 2. | NO IS spec or plan amendment owed. |
| Operational discipline axis | NO cascade per Q4. Existing namespaces sufficient. | NO OD spec or plan amendment owed. |

**Aggregate cascade: ZERO genuine seams added; ZERO cross-axis amendments owed.**

---

## 6. Operator-decision surface

Per `phase-7-back-flow-routing` skill §4.4 format + fork doc §6 operator-decision pattern:

```
READING B SCOPING RECOMMENDATION — OPERATOR-DECISION POINT

Reading B scope at current canonical state has materially shrunk from
fork doc's 8-15-commit worst-case estimate to a 3-5-commit single-axis
runtime-spec-only amendment per §3 + §4 above.

Architectural calls determined by canonical authority chain (NOT
operator-discretion):
  Q1 — VALIDATOR_ESCALATION emission timing: sync mid-step (α) per
       C-CP-28 §25.3 + §25.4 invariant 2 + §25.7 invariant 4 [HIGH]
  Q3 — Scope envelope: runtime-spec-only amendment (i) per §1.2
       surface inventory [HIGH]
  Q4 — OD-side amendment: NO amendment per existing surfaces [HIGH]
  Q5 — Fail class disposition: REMOVE per spec-writer §3.2 [HIGH]

Operator-decision sub-questions remain:
  (D1) Q2 absorption path: (c-i) absorb cite-completeness fix into
       Reading B's runtime-spec amendment OR (c-ii) file separate
       Class 1 cite-correction fork. Recommended: (c-i) per §2 Q2.
  (D2) Open Reading B arc NOW vs DEFER. The scoping doc establishes
       sharp scope + reduced commit envelope. Retirement-gate forcing
       function is ZERO (CP-21 already RETIRED via Reading A). The
       only architectural value is: validator framework gains
       operationally-MET surface (operator can supply validators that
       emit ESCALATE → HITL gate fires). Operator-discretion timing.
  (D3) Cluster naming: L9-duodecies vs alternate naming per
       implementation-planner discretion. Cosmetic.
  (D4) Whether U-RT-60 (HITL gate composer L9-quinquies) AC
       amendments needed — possibly absorbed at plan-revision arc.

Routing target if (D2) = OPEN NOW:
  1. spec-writer skill arc: runtime spec v1.21 → v1.22 with 5
     amendment sites (§3 above). Estimate 1 commit.
  2. implementation-planner skill arc: runtime plan v2.20 → v2.21 NEW
     L9-duodecies cluster (3 units). Estimate 1 commit.
  3. phase-7-implementation skill arc: U-RT-NN-A → U-RT-NN-B → U-RT-NN-C
     traversal. Estimate 2-3 commits.

  TOTAL: 4-5 commits across 3-4 spec/plan/impl skill arc invocations.

Routing target if (D2) = DEFER:
  1. This scoping doc preserved as RECOMMENDATION-READY at filing.
  2. Reading B continues to be OPEN at fork doc §3.2 with the sharp
     scope this doc documents.
  3. No spec / plan / impl commits until operator authorizes (D2) = OPEN.

This recommendation does NOT halt any current execution arc.
Reading B is operator-discretion timing per fork doc §3.2 explicit
disposition (no retirement gate forces it; CP-21 closed via Reading A).
```

---

## 7. Trade-offs vs Reading C / Reading D

### 7.1 Reading C — Defer; mark CP-21 RETIRED-BLOCKED-ON-DESIGN-ARC

**Status:** Foreclosed at fork doc §3.3 — Reading C re-classification would have applied at batch-15 had CP-21 NOT been restored to RETIRED via Reading A at batch-17. Reading C is preserved for record only.

**Trade-off:** Reading C foreclosed at the moment Reading A landed at batch-17. No path to re-open Reading C — CP-21 is already RETIRED.

### 7.2 Reading D — Gate-redefinition

**Status:** APPLIED at batch-17 via Reading A pathway. CP-21 RETIRED at batch-17 via U-RT-85 e2e against operator-supplied ValidatorFramework PASS fixture per Reading A operator-opt-in pattern. The gate-redefinition Reading D contemplated (lib-completion gate vs external-substrate gate vs runtime-wiring gate) was implicit in Reading A's choice — the gate is "operator-supplied validator_framework non-None at HarnessContext + e2e exercise" per batch-14 §6(a) close pattern, NOT "lib-completion at HEAD".

**Trade-off:** Reading D foreclosed at the moment Reading A clarified the gate semantics through application. No path to re-open Reading D — the gate is now empirically clear.

### 7.3 Reading B vs current OPEN state (no action)

| Dimension | Reading B (open arc) | Current OPEN (no action) |
|---|---|---|
| CP-21 retirement state | UNCHANGED (already RETIRED at batch-17) | UNCHANGED |
| Validator framework operability | Operator-supplied validators can emit ESCALATE → HITL gate fires → operator decides per-case | Operator-supplied validators can emit ESCALATE → composer raises HITLPlacementForeclosedAtV19Error → workflow step fails with permanent error |
| §14.8.2 deferral closure | 3 deferrals CLOSED (step 3 VALIDATOR_ESCALATION + step 4c 4-axis + step 4d cross-trust palette) | 3 deferrals OPEN indefinitely |
| `_hitl_required` correctness | Full 4-axis composition per C-CP-19 §19.1 | `placement.requires_hitl` shortcut (likely correct for MVP but loses C-CP-19 §19.1 multi-axis composition value) |
| Cross-trust palette correctness | Full UNION-intersection per §19.4 + §21.3 | Full palette unconditionally (incorrect under cross-trust state) |
| Cite-shape completeness | §14.8.2 step 4d cite corrected per Q2(c-i) | Cite-incomplete (`§19.4` only, omitting `§21.3`) |
| Engineering cost | 4-5 commits across 3-4 skill arcs | ZERO |
| Operator value | Validator framework becomes fully production-usable per ADR-D5 v1.3 §1.10 commitments | Validator framework is binding-chain-complete but emission-path-foreclosed |

**Net trade-off:** Reading B converts a deferred architectural promise into operational reality at 4-5 commits cost. No retirement gate forces it; operator-discretion timing per fork doc §3.2.

---

## 8. Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/reading_b_validator_composer_arc_scoping.md` |
| Filing class | Mode 3 architectural-tension-resolution recommendation (`systems-architect` skill §4A.3) |
| Filed at | 2026-05-24 at HEAD `0459a3d` (post-Reading-A absorption batch-17; runtime spec v1.21; CP spec v1.13; OD spec v1.11; CXA v2.9) |
| Filing trigger | Operator authorization on prior-checkpoint Item #6 + advisor sanity-check confirming fork doc estimate predates Reading A landing + empirical sweep of v1.21 baseline |
| Fork doc reference | `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` §3.2 (Reading B disposition) |
| Recommendation confidence | [HIGH] on Q1/Q3/Q4/Q5; [HIGH-with-caveat] on Q2 (cite-shape sub-routing operator-decision) |
| Operator decision required | (D1) Q2 absorption path; (D2) open Reading B now vs defer; (D3) cluster naming; (D4) U-RT-60 AC amendment scope |
| Successor | At operator (D2) = OPEN: routes to `spec-writer` skill arc → `implementation-planner` skill arc → `phase-7-implementation` skill arc. At (D2) = DEFER: this doc preserved as recommendation; Reading B continues OPEN at fork doc §3.2 with sharp scope this doc documents. |
| Related memory | `[[fork-validator-composer-arc-stage-4-absence]]` (parent fork doc); `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` (close-pattern precedent); `[[advisor-before-substantive-work-for-cross-axis-blockers]]` (14th application — re-scoping pattern this session); `[[verification-shape-sharpened-grep-vs-e2e]]` (verification discipline for any retirement-event filing); `[[halt-route-split-AC-pattern]]` (potential precedent if any unit AC bundles materializable + unmaterializable surface) |
| §2 discipline summary | Five-axis: control-plane (HITL composition) + operational-discipline (failure-mode taxonomy) + (no other axes touched). Prob-det boundary: deterministic side (sync gate, deterministic palette computation, deterministic span schema). F/D/I: D-level (derivative of F-ADR-F2 state-ledger ordering + ADR-D1 v1.2 HITL primitive + ADR-D5 v1.3 §1.5/§1.10 commitments). |

---

*End of Mode 3 architectural recommendation. Operator decides per §6. No spec / plan / ADR edits at this filing. No H_T design extension (I-2 / X-AL-3 preserved).*
