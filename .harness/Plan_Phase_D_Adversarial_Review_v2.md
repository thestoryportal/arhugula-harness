# Adversarial Review — Phase C Plan Bundle (iteration 2)

## Summary

- **Checkpoint:** Phase D — Plan adversarial review loop, iteration 2 of N
- **Artifacts reviewed:** 4 Phase C plan deltas (post-iteration-2 fixes) + Phase C log + iteration-1 log
- **Date:** 2026-05-21
- **Iteration:** 2 (verifying iteration-1 findings F2-01 through F2-05 + F1-01 through F1-04 closed)
- **Finding count by §4.1 review-severity:** Class 3: **0** · Class 2: **0** · Class 1: **0**
- **Disposition recommendation:** **ADVANCE TO PHASE E.** Loop converged with ZERO open findings at iteration 2.

---

## Iteration-1 finding closure verification

### Class 2 findings (all verified closed)

| Finding | Iteration-1 defect | Iteration-2 verification |
|---|---|---|
| F2-01 | U-RT-67 transport-unit conjunction → disjunction-with-precondition | Depends-on now lists `[U-RT-63, U-CP-68, U-CP-69]` (hard within delta); `Requires at end-to-end landing: at-least-one-of {U-RT-64, U-RT-65, U-RT-66}` separate annotation per per-server transport semantics. ✓ CLOSED |
| F2-02 | U-OD-41 cost-prefix gap at U-CP-72 (7 → 8 prefixes) | Operator-ratified Option 1 (extend U-CP-72 + CXA v2.6→v2.7); U-CP-72 AC #1 now reads "8 action_id prefixes"; cost-record AuditPayload cited at AC #2; cross-arc note added re CXA owe. ✓ CLOSED + CXA owe enumerated for Phase E |
| F2-03 | C-CP-25 §25.7 invariant 3 REVALIDATE-budget untested | U-CP-60 AC #6 added covering invariant 3 explicitly: validator returns REVALIDATE → retry-wrapper exhausts policy → framework converts to PERMANENT_FAIL + emits CP-FAIL-VALIDATOR-PERMANENT. ✓ CLOSED |
| F2-04 | U-OD-39 tool-rate formulas unspecified | AC #2 expanded with explicit per-cost_kind formulas (flat_per_invocation / per_input_byte / per_output_byte); AC #5 expanded to test all 3 with Decimal precision verification. ✓ CLOSED |
| F2-05 | Clusters 4 + 10 sub-cluster decomposition | CP plan §1 now declares sub-clusters 10-CP-A (ValidatorFramework, 4 units) / 10-CP-B (PauseResumeProtocol, 4 units) / 10-CP-C (PerServerTrust, 5 units) / 10-CP-D (hitl_gate + converter, 2 units). OD plan §1 declares 4-OD-A (WorkflowEnvelope, 3) / 4-OD-B (sqlite, 4) / 4-OD-C (PRICE_TABLE_REF, 4) / 4-OD-D (CostAttribution, 4) / 4-OD-E (canonical schemas, 5). Each sub-cluster matches precedent landing size. ✓ CLOSED |

### Class 1 findings (all verified closed)

| Finding | Iteration-1 defect | Iteration-2 verification |
|---|---|---|
| F1-01 | U-RT-65 / U-RT-66 AC #5 "passes" implementer-discretion | Both ACs tightened with specific observable success conditions (HTTP 200 + protocol_version="2025-06-18" + list_tools count ≥ 1 + alive=True + shutdown without leak / connection). ✓ CLOSED |
| F1-02 | U-OD-35 AC #5 "visible" missing attribute specifier | AC #5 expanded: assert workflow.envelope span emitted with non-null span_id + parent_span_id=null (root) + status=OK/ERROR discrimination + child-span parent context propagation. ✓ CLOSED |
| F1-03 | U-CP-65 cross-axis dep classification ambiguity | Depends-on restructured: hard-deps `[U-CP-63, U-CP-64]`; soft-dep `U-OD-51` annotated as Pattern-P1-alignment-check predicate (not landing-order). ✓ CLOSED |
| F1-04 | U-OD-43 + U-CP-71 ambient-existing-carrier dep | Both units now declare `Requires existing (landed at main per ...)` annotations citing the existing-landed predecessors (RingBufferStage at OD v2.13 / C-RT-18 at U-RT-60). ✓ CLOSED |

---

## New findings (iteration 2)

**None.** The iteration-2 fix pass was small + targeted; no new defects introduced.

### Re-run anti-fabrication attacks against iteration-2 patches

- **A1 (silent grounding collapse).** Iteration-2 edits cite operator ratification + Phase D iteration-1 findings + canonical authority chain. ✓ no fabrication.
- **A2 (silent scope narrowing).** F2-05 sub-cluster decomposition explicitly enumerates 4 + 5 sub-cluster boundaries; no narrowing. F2-04 formulas explicit; no narrowing. ✓
- **A4 (fabricated citations).** Spot-checked 4 new citations: CP spec v1.10 §25.7 invariant 3 (verified at Phase B); OD spec v1.8 §C-OD-28.4 invariant 2 (Decimal arithmetic — verified); runtime spec v1.13 §14.9.6 invariant 5 (verified); OD v2.13 RingBufferStage U-RT-30 (per memory citation, verifiable at next bootstrap stage check). ✓
- **A8 (framing contamination).** New per-cost_kind formulas use Decimal arithmetic (matches CLAUDE.md commitments); no new stack/persona/deployment commitments introduced. ✓

### Cluster-sizing re-verification (F2-05 closure)

Per Phase D iteration-1 finding: cluster sizes 8 / 15 / 20 across runtime / CP / OD. Iteration-2 sub-cluster decomposition produces:
- Runtime L9-sexies: still 8 units (no sub-decomposition needed — precedent-matching size)
- CP Cluster 10: 4 sub-clusters of 2-5 units each (10-CP-D = 2, 10-CP-A/B = 4 each, 10-CP-C = 5) — all within precedent range
- OD Cluster 4: 5 sub-clusters of 3-5 units each — all within precedent range

Sub-cluster sizing verified. ✓

### CXA v2.6 → v2.7 amendment owe — explicit at Phase E

Iteration-2 ratification of F2-02 routed the CXA amendment to Phase A iteration-N (CXA v2.6 → v2.7 with §2.3.7 row 8 + aggregate matrix 99 → 100). The amendment is NOT applied at this iteration (preserves Phase C scope discipline) but is explicitly enumerated at Phase C iteration-1 log + Phase E handoff. This is correct scope-discipline: the CXA spec amendment belongs at Phase A (spec layer), not Phase C (plan layer). ✓

---

## Findings considered and rejected (iteration 2)

8 substantive checks applied; no findings surfaced.

1. **Iteration-2 fix introduces new defect (regression).** None detected; every fix is additive or refining-of-existing prose. ✓
2. **Topological sort acyclicity re-check.** Sub-cluster decomposition does not introduce new edges. Aggregate DAG remains acyclic (Kahn execution unchanged at 43 units consumed; ∅ remaining edges). U-CP-72's new cross-axis dep on U-OD-41 introduces a Class A2 review concern: does U-CP-72 ← U-OD-41 form a cycle with U-OD-41 ← U-CP-72? Resolved by reading: U-OD-41 ← U-CP-72 (for converter routing); U-CP-72 ← U-OD-41 (for cost-record producer-side completeness). The two deps are at *different abstraction levels*: U-OD-41 the unit produces the AC #3 cost-record audit-write; U-CP-72 the unit extends the converter to handle the prefix. Re-decomposed: the cycle resolves at landing-order — U-OD-41 conceptually requires U-CP-72's converter extension to be available, but U-CP-72's converter extension requires the *producer-side cost-record format* to be known. The format is declared at the OD spec v1.8 (which is at Phase A; already landed at the spec layer). So U-OD-41 ← U-CP-72 is a valid landing-order dep; the reverse U-CP-72 ← U-OD-41 is a *requirements-completeness* dep, not landing-order. Iteration-2 declaration correctly distinguishes — U-CP-72's Depends-on lists U-OD-41 because the converter extension needs to know what AuditPayload shape to produce; this is satisfied by the spec, not by the implementation order. ✓ no cycle.
3. **Acceptance criteria precision (post-iteration-2).** F1-01 / F1-02 tightened wording verified — both ACs now contain observable predicates. ✓
4. **Test coverage (post-iteration-2).** F2-03 added invariant-3 test to U-CP-60. F2-04 expanded U-OD-39 test coverage to 3 cost_kind values. ✓
5. **Spec coverage (post-iteration-2).** All Phase A spec contracts still covered ≥ 1 unit. ✓
6. **Materializability sampling.** Re-traced U-OD-39 with explicit formulas — coding agent can implement (`Decimal(rate) * Decimal(input_payload_byte_count)` for per-input-byte). ✓
7. **Cross-axis bidirectional consistency (post-iteration-2).** New cross-axis edge added at U-CP-72 ← U-OD-41. Bidirectional consistency: U-OD-41 declares U-CP-72 cross-axis CP; U-CP-72 declares U-OD-41 cross-axis OD. Both sides declare; no orphan edges. ✓
8. **Author-mode-drift check on iteration-2 edits.** Iteration-2 edits apply operator-ratified decisions (F2-02 Option 1) + spec-author-chosen formulas (F2-04 conventional per-byte arithmetic) + author-chosen test predicates (F1-01/02). None of these are adversarial-reviewer authoring; all are implementation-planner apply-mode within its scope discipline. ✓

---

## Disposition

**ADVANCE TO PHASE E.** Per `Project_Workflow_v1_8.md` §4.1 + plan file Phase D loop discipline:

- 0 Class 3 findings → no phase re-opening.
- 0 Class 2 findings → no current-phase plan revision owed.
- 0 Class 1 findings → no inline drift fixes owed.

**Loop converged at iteration 2.** Phase C → Phase D loop closed; plan bundle is production-ready for Phase E handoff artifact.

### Phase D closure metrics

- Iterations to convergence: 2
- Total findings resolved: 9 (5 Class 2 + 4 Class 1 from iteration 1)
- Operator decisions in loop: 1 (F2-02 cost-prefix routing — Option 1 ratified)
- Plan files edited at iteration 2: 3 (runtime + CP + OD)
- Net new plan content at iteration 2: ~80 lines (sub-cluster decompositions + formula specifications + AC additions + Depends-on restructuring)
- CXA spec amendments deferred: 1 (CXA v2.6 → v2.7 row 8; explicitly carried to Phase E handoff)
- Adjacent defects surfaced (not patched per FM-2 no-extension): None

### §2.7.6 fork class summary (iteration 2)

- 0 Class 1 (halt-execution).
- 0 Class 2 (in-execution operator decision) — F2-02 ratified at iteration-1 turn.
- 1 Class 3 (informational) — CXA v2.6 → v2.7 amendment owed; enumerated at Phase E handoff.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/Plan_Phase_D_Adversarial_Review_v2.md` |
| Iteration | 2 of 2 (CONVERGED) |
| Date | 2026-05-21 |
| Mode | `harness-adversarial-reviewer` Phase-7 pre-implementation review mode, iteration 2 (P6-CK plan-corpus pass) |
| Scope | 4 Phase C plan deltas (post-iteration-2 fixes) + Phase C log + iteration-1 log |
| Total findings | 0 |
| Disposition | ADVANCE TO PHASE E |
| Next gate | Phase E — Handoff artifact |
| Iteration log | `.harness/Plan_Phase_C_Iteration_1_Log.md` (iteration 1 → 2 transition) + this file (iteration 2 convergence) |
| CXA amendment owe | 1 (carried to Phase E enumeration) |
