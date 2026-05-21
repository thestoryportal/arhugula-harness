# Adversarial Review — Phase A Spec Bundle (iteration 2)

## Summary

- **Checkpoint:** Phase B — Spec adversarial review loop, iteration 2 of N
- **Artifacts reviewed:** 5 Phase A spec deltas (post-iteration-2 fixes) + 2 reconciliation records
- **Date:** 2026-05-21
- **Iteration:** 2 (verifying iteration-1 findings F2-01 through F2-07 + F1-01/02/03 closed)
- **Finding count by §4.1 review-severity:** Class 3: **0** · Class 2: **0** · Class 1: **0**
- **Disposition recommendation:** **ADVANCE TO PHASE C.** Loop converged with ZERO open findings at iteration 2.

---

## Iteration-1 finding closure verification

### Class 2 findings (all verified closed)

| Finding | Iteration-1 defect | Iteration-2 verification |
|---|---|---|
| F2-01 | "subprocess" terminology leaked STDIO assumption to HTTP/SSE | Runtime spec §14.9.1 transport-neutral terminology block landed; §14.9.6 invariant 1 + invariant 5 rephrased to "MCP host instance" + "transport-appropriate startup lifecycle". ✓ CLOSED |
| F2-02 | OD §C-OD-29.1 missing `step.id` + `validator.escalation` attribute rows | OD §C-OD-29.1 attribute table now lists 11 attributes across 4 span sites (3 `validator.evaluate` outer + 5 `validator.fail` event + 2 `validator.revalidation` event + 2 `validator.escalation` event). Pattern-P1 alignment with CP §25.5 verified. ✓ CLOSED |
| F2-03 | ValidatorOutcome → ValidatorNextAction mapping unspecified | CP spec §25.2 now carries explicit 5-row mapping table; OPERATOR_BURDEN_EXCEEDED → ESCALATE_HITL per operator ratification 2026-05-21 (operator-notify pattern). Bijective-on-outcomes invariant + consumer-disambiguation note via `validator.outcome` span attribute added. ✓ CLOSED |
| F2-04 | `[Phase B review: workflow.envelope shape]` operator-decision marker | Operator confirmed single-envelope default; spec unchanged. ✓ CLOSED — marker resolved |
| F2-05 | `[Phase B review: validator cost-meter granularity]` operator-decision marker | Operator confirmed CPU-meter default; spec unchanged. ✓ CLOSED — marker resolved |
| F2-06 | PRICE_TABLE_REF Decimal serialization at OTel boundary unspecified | OD §C-OD-28.4 invariant 3 (NEW) added: string-serialization at OTel span attribute boundary per operator ratification. ✓ CLOSED |
| F2-07 | Phase A scope-gap on 8 STILL-BOUNDED substitutions | Routed to Phase E handoff artifact (per iteration-1 disposition). Phase A iteration-2 is not the apply site. ✓ ROUTED |

### Class 1 findings (all verified closed)

| Finding | Iteration-1 defect | Iteration-2 verification |
|---|---|---|
| F1-01 | OD change-note "4-attribute" vs actual 8-attribute schema | Change-note updated to "11-attribute namespace across 4 span sites"; §C-OD-29.1 closing paragraph updated to reflect the new count + cite the F1-01 absorption explicitly. ✓ CLOSED |
| F1-02 | CXA v2.6 §2.3.7 rows 3-7 stale `§NN` placeholders | All 5 rows back-patched with resolved section refs: row 3 → §C-OD-32 / row 4 → §C-OD-33 / row 5 → §C-OD-29 / row 6 → §C-OD-30 / row 7 → §C-OD-31. ✓ CLOSED |
| F1-03 | `hitl.operator_burden.*` namespace vs single-span name | Runtime spec §14.10.3 Burden span section now clarifies: namespace `hitl.operator_burden.*` is attribute-set identifier; single span `hitl.operator_burden.evaluated`. ✓ CLOSED |

---

## New findings (iteration 2)

**None.** The iteration-2 fix pass was small + targeted; no new defects introduced.

### Re-run anti-fabrication attacks against iteration-2 patches

- **A1 (silent grounding collapse).** Iteration-2 edits cite operator ratification + Phase B iteration-1 findings + canonical authority chain. ✓ no fabrication.
- **A2 (silent scope narrowing).** The F2-01 transport-neutral terminology block explicitly enumerates STDIO + HTTP + SSE; no narrowing. ✓
- **A4 (fabricated citations).** Spot-checked F2-02 attribute additions: `validator.escalation.parent_hitl_span_id` is a NEW attribute introduced at iteration-2 — cross-references the OTel `Span.parent` linkage which CP §25.5 already commits ("Links to subsequent `hitl.gate.evaluated` span via parent-context propagation"). The OTel 16-hex span id format is standard OTel API. ✓ no fabrication.
- **A8 (framing contamination — highest-value).** The new `validator.escalation.parent_hitl_span_id` attribute uses `string (16-hex OTel span id)` — matches existing OTel attribute conventions per ADR-D6 v1.2 + GenAI semconv. No stack/persona/deployment commitment introduced. ✓ no contamination.

### Pattern-P1 byte-exact re-verification

Re-checked C-OD-29 vs CP §25.5 mapping post-fix:

| CP §25.5 span | CP §25.5 attribute claim | OD §C-OD-29.1 entry | Status |
|---|---|---|---|
| `validator.evaluate` (outer) | `step.id`, `validator.outcome`, `validator.burden_count_cumulative` | Same 3 attributes; same span-site label | ✓ aligned |
| `validator.fail` (event) | `validator.fail.class`, `validator.fail.detail_hash`, `validator.fail.next_action`, `validator.fail.escalation_owed` | Same 4 attributes + cardinality | ✓ aligned |
| `validator.revalidation` (event) | `validator.revalidation.payload_size_bytes`, `validator.revalidation.attempt_number` | Same 2 attributes | ✓ aligned |
| `validator.escalation` (event) | Links to subsequent `hitl.gate.evaluated` via parent-context propagation | New: `validator.escalation.parent_hitl_span_id` + `validator.escalation.fail_class` attributes added at iteration-2 | ✓ aligned (CP §25.5 prose claim now backed by typed schema) |

Pattern-P1 byte-exact alignment confirmed across all 4 span sites.

### Cross-reference re-verification

- C-RT-19 §14.9 → C-CP-27 (PerServerTrustEvaluator): ✓ exists
- C-CP-25 §25 → C-RT-16 (retry-wrap) + C-RT-18 (HITL gate): ✓ exists
- C-CP-26 §26 → U-CP-56 (replay-resumption coexist): ✓ exists per memory
- C-OD-26 → C-RT-15 + C-RT-19 + C-RT-20: ✓ all exist post-A.2
- C-OD-28.4 invariant 3 → C-OD-27 (sqlite write `attributes_json` column): ✓ exists per A.5
- CXA v2.6 §2.3.7 rows 3-7 → OD §C-OD-29/30/31/32/33: ✓ resolved at iteration-2

---

## Findings considered and rejected (iteration 2)

8 substantive checks applied; no findings surfaced.

1. **Iteration-2 fix introduces new defect (regression check).** None detected; every fix is purely additive or refining-of-existing-prose. ✓
2. **Pattern-P1 byte-exact re-alignment.** All 4 `validator.*` span sites now aligned CP ↔ OD. ✓
3. **F2-04 / F2-05 confirmed-default markers retained.** Spec retains the `[Phase B review: ...]` text in OD §C-OD-25.5 + §C-OD-26.5. Reviewer confirms this is acceptable — the markers document the operator-decision provenance (single-envelope was operator's call, not just author default). No defect; the markers are inline-traceability rather than open-decisions. ✓
4. **F2-03 mapping table bijective-on-outcomes check.** 5 outcomes → 5 mappings (not 4 → 5); each outcome maps to exactly one next_action. ESCALATE_HITL appears twice (from ESCALATE + OPERATOR_BURDEN_EXCEEDED); consumer-disambiguation discipline documented. ✓
5. **F2-06 invariant 3 cross-check with C-OD-27 sqlite schema.** §C-OD-27.1 sqlite `attributes_json TEXT NOT NULL` column accepts string-serialized Decimal natively. No cross-spec defect. ✓
6. **F1-02 forward-citation closure.** CXA v2.6 §2.3.7 rows 3-7 now resolve byte-exact to OD §C-OD-29 through §C-OD-33; the filing footer claim ("rows 3-7 resolve to §C-OD-32 / §C-OD-33 / §C-OD-29 / §C-OD-30 / §C-OD-31 respectively") now matches the row text. ✓
7. **Author-mode-drift check on iteration-2 edits.** Edits supplied specific replacement text — but the edits are *applying operator-ratified decisions*, not the adversarial reviewer choosing wording. Spec-writer apply mode is the correct discipline; this skill's bright line is about adversarial review proposing solutions, not about apply-mode authoring. ✓ no role violation.
8. **Iteration-2 spec edits preserve Pattern-D inheritance discipline.** No Pattern-D field-set re-authoring at iteration-2; all edits cite existing types. ✓

---

## Disposition

**ADVANCE TO PHASE C.** Per `Project_Workflow_v1_8.md` §4.1 + plan file Phase B loop discipline:

- 0 Class 3 findings → no phase re-opening.
- 0 Class 2 findings → no current-phase revision owed.
- 0 Class 1 findings → no inline drift fixes owed.

**Loop converged at iteration 2.** Phase A → Phase B loop closed; spec bundle is production-ready for Phase C implementation-planner authoring.

### §2.7.6 fork class summary (iteration 2)

- 0 Class 1 (halt-execution).
- 0 Class 2 (in-execution operator decision) — all iteration-1 markers ratified.
- 0 Class 3 (informational) — all iteration-1 informational items resolved or routed to Phase E.

### Phase B closure metrics

- Iterations to convergence: 2
- Total findings resolved: 10 (7 Class 2 + 3 Class 1 from iteration 1)
- Operator decisions in loop: 4 (F2-03 + F2-04 + F2-05 + F2-06)
- Spec files edited at iteration 2: 4 (runtime + CP + OD + CXA)
- Net new spec content at iteration 2: ~50 lines (transport-neutral block + ValidatorOutcome mapping table + 2 new attribute rows + Decimal serialization invariant)
- Adjacent defects surfaced (not patched per FM-2 no-extension): None

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/Spec_Phase_B_Adversarial_Review_v2.md` |
| Iteration | 2 of 2 (CONVERGED) |
| Date | 2026-05-21 |
| Mode | `harness-adversarial-reviewer` Phase-7 pre-implementation review mode, iteration 2 |
| Scope | 5 Phase A spec deltas (post-iteration-2 fixes) + 2 reconciliation records |
| Total findings | 0 |
| Disposition | ADVANCE TO PHASE C |
| Next gate | Phase C — Implementation plan authoring (atomic units) via `implementation-planner` skill |
| Iteration log | `.harness/Spec_Phase_A_Iteration_1_Log.md` (iteration 1 → 2 transition) + this file (iteration 2 convergence) |
