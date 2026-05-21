# Adversarial Review — Phase C Plan Bundle (iteration 1)

## Summary

- **Checkpoint:** Phase D — Plan adversarial review loop (Remaining-Work Closure Arc)
- **Artifacts reviewed:** 4 Phase C plan deltas (43 atomic units) + Phase C authoring log
- **Date:** 2026-05-21
- **Iteration:** 1 (filed at `.harness/Plan_Phase_C_Iteration_1_Log.md` after disposition)
- **Finding count by §4.1 review-severity:** Class 3: **0** · Class 2: **5** · Class 1: **4**
- **Highest-severity finding:** F2-02 (U-OD-41 cross-axis converter dependency gap on `cost:` prefix not enumerated at U-CP-72)
- **§2.7.6 Phase-7 fork classes induced:** 0 Class 1 (halt-execution); 0 Class 2 (operator decision); 5 Class 3 (informational — plan-precision issues, non-blocking for Phase 7 execution itself)
- **Disposition recommendation:** **Phase C iteration-2 plan revision** for F2-01 through F2-05 (precision + coverage + cluster-sizing); F1-01 through F1-04 (drift) inline. Advance to Phase E ONLY AFTER iteration-2 closes the Class 2 items.

---

## Class 3 findings (severe — phase re-opening)

**None.** Discriminator (b) and (c) walks did not fire. The 4 plan deltas do not contradict any Phase A spec contract, do not pick a stack value the workspace `CLAUDE.md` framing does not commit, do not assume single-LLM, and do not require upstream Phase A/B revision. Phase A + B spec convergence held.

---

## Class 2 findings (moderate — current-phase plan revision)

### F2-01 — U-RT-67 transport-unit dependency reads as conjunction; should be disjunction-with-precondition

- **Location:** `design-substrate/Implementation_Plan_Harness_Runtime_v2_11.md` §1 U-RT-67 verbatim: `Depends on: [U-RT-64, U-RT-65, U-RT-66, U-CP-68 (cross-axis: CP), U-CP-69 (cross-axis: CP)]`
- **Defect:** The dependency declaration lists U-RT-64 + U-RT-65 + U-RT-66 (three transport-specific units) as if all three must land before U-RT-67. In actual runtime, **one MCP server per `MCPClientHost` runs ONE transport** (STDIO OR HTTP OR SSE — selected per per-server bootstrap config per runtime spec v1.13 §14.9.6 invariant 5). U-RT-67's dispatch body needs *at least one* transport implementation, not *all three*. Reading the declaration as conjunction constrains landing-order incorrectly — a coding agent could read "all three must land before U-RT-67" and over-block U-RT-67's arc.
- **Discriminator that classifies as Class 2 review-severity:** (a) — substantive content gap in dependency declaration; affects landing-order semantics at execution-time.
- **Evidence:** Runtime spec v1.13 §14.9.6 invariant 5: *"`MCPClientHost.start()` selects transport per per-server bootstrap config"* — singular transport per host. U-RT-67's `Depends on:` line treats them as conjunction by listing them comma-separated under a single Depends-on declaration.
- **Anti-fabrication attack engaged:** None directly.
- **Axis-domain attack engaged:** Runtime axis — dependency-graph precision. Hidden-coupling adjacency.
- **Resolution path:** Phase C iteration-2 plan revision — restructure U-RT-67 dependency declaration to clarify "at least one transport unit must be landed before U-RT-67 can be tested end-to-end; U-RT-67 itself only requires U-RT-63 (skeleton)". The exact declarative shape (multi-line "Depends on: U-RT-63" + "Requires at landing: at-least-one-of {U-RT-64, U-RT-65, U-RT-66}" OR enumerated alternative-syntax) is implementation-planner's choice; this skill flags the precision gap.
- **§2.7.6 fork class induced:** Class 3 (informational) — plan-precision improvement; does not halt execution.

### F2-02 — U-OD-41 cross-axis dep on U-CP-72 but `cost:` action_id prefix not enumerated at U-CP-72 (Phase C log §1 self-flagged but not closed at the unit)

- **Location:** `design-substrate/Implementation_Plan_Operational_Discipline_v2_14.md` §1 U-OD-41 AC #3 verbatim: *"Routes via `cp_audit_to_od_audit` converter (action_id prefix `cost:` added per U-CP-72 extension — **note: covered by `cost:` discriminator as the 8th pattern; reviewer to confirm bucket sizing or extend U-CP-72**)"*
- **Defect:** U-OD-41's cost-record audit-ledger write uses action_id prefix `cost:` and routes via U-CP-72's converter extension. However, **U-CP-72 explicitly enumerates only 7 prefixes** (dispatch / hitl / hitl_webhook / operator_burden / validator / pause+resume / mcp_trust — per CP plan v2.15 §1 U-CP-72 AC #1 + CXA v2.6 §0.3 discriminator table). The `cost:` prefix is an 8th pattern that U-CP-72 does NOT include. The author flagged this inline ("reviewer to confirm bucket sizing or extend U-CP-72") but did NOT close it — U-CP-72 stands at 7 prefixes; U-OD-41 silently assumes 8. This is a dependency-product mismatch.
- **Discriminator that classifies as Class 2 review-severity:** (a) — substantive content gap; either U-CP-72 needs the 8th prefix added (extending its AC #1) OR U-OD-41 needs a different routing path (e.g., direct write bypassing converter).
- **Evidence:** Phase C log §1 U-OD-41 verbatim flag ("reviewer to confirm bucket sizing or extend U-CP-72") + CP plan v2.15 U-CP-72 AC #1 lists "7 action_id prefixes" verbatim. CXA v2.6 §0.3 discriminator table lists 7 patterns (not 8). The cost-attribution audit-write surface is NOT in CXA v2.6 §2.3.7's row enumeration (no row for `cost:` prefix).
- **Anti-fabrication attack engaged:** None directly. Discipline issue: author surfaced the gap at the right place (inline flag) but did not route to the right fix.
- **Axis-domain attack engaged:** CXA-axis — composition seam declaration completeness.
- **Resolution path:** Phase C iteration-2 plan revision — operator-decision between (i) extending U-CP-72 to 8 prefixes + extending CXA v2.6 to add a row for the cost-attribution audit-write seam (this is the spec-extension route; routes back to Phase A iteration-N), OR (ii) restructuring U-OD-41 to write to OD audit ledger directly without the CP→OD converter (matches the "OD-internal cost audit" framing). The two readings have different scope implications; implementation-planner cannot pick without operator guidance.
- **§2.7.6 fork class induced:** Class 3 (informational) — the audit-write path exists in both readings; only the cross-axis-seam declaration is incomplete. Resolution clarifies plan + possibly CXA but no Phase 7 execution halt.
- **Decision-vocabulary label:** *proposing* — two readings supported by the artifact text; operator chooses.

### F2-03 — C-CP-25 §25.7 invariant 3 "REVALIDATE bounded by C-RT-16 retry policy" untested at U-CP-60

- **Location:** `design-substrate/Implementation_Plan_Control_Plane_v2_15.md` §1 U-CP-60 ACs (5 total)
- **Defect:** CP spec v1.10 §25.7 invariant 3: *"REVALIDATE bounded by C-RT-16 retry policy. A REVALIDATE outcome routes back through retry-wrapper; if retry budget exhausted, escalates to PERMANENT_FAIL."* This is a load-bearing invariant — REVALIDATE outcomes that exceed retry budget MUST escalate to PERMANENT_FAIL, not loop forever. U-CP-60's 5 ACs cover the outcome→next_action mapping (AC #1), burden count (AC #2), single-Validator invariant (AC #3), PERMANENT_FAIL fail-class emission (AC #4), and per-outcome unit test (AC #5). **None test the REVALIDATE-budget-exhausted-escalates-to-PERMANENT_FAIL invariant.** A coding agent could implement REVALIDATE → RETRY routing without the budget-exhaustion-handling logic and still pass all 5 ACs.
- **Discriminator that classifies as Class 2 review-severity:** (a) — substantive test-coverage gap on a spec invariant.
- **Evidence:** CP spec v1.10 §25.7 invariant 3 verbatim above. U-CP-60 AC list does not enumerate the budget-exhaustion test.
- **Anti-fabrication attack engaged:** A2 (silent scope narrowing) — the unit silently narrows test coverage by not enumerating invariant 3 testing.
- **Axis-domain attack engaged:** CP-axis — test coverage of contract invariants.
- **Resolution path:** Phase C iteration-2 plan revision — add an AC to U-CP-60 OR a new unit testing the REVALIDATE-budget-exhausted-escalates-to-PERMANENT_FAIL path explicitly. Implementation-planner's choice on whether to add to U-CP-60 (would push it to 6 ACs) OR split.
- **§2.7.6 fork class induced:** Class 3 (informational) — test gap is a plan-quality issue; no execution halt.

### F2-04 — U-OD-39 cost-attribution at tool dispatch: tool-rate formulas per cost_kind unspecified

- **Location:** `design-substrate/Implementation_Plan_Operational_Discipline_v2_14.md` §1 U-OD-39 AC #2 verbatim: *"Tool-rate resolution per `ToolRate.cost_kind` (flat / per-input-byte / per-output-byte)"*
- **Defect:** OD spec v1.8 §C-OD-28.1 declares `ToolRate.cost_kind: Literal["flat_per_invocation", "per_input_byte", "per_output_byte"]` and `ToolRate.rate: Decimal`. U-OD-39 AC #2 names the 3 enum values but **does not specify the cost-computation formula per enum value**. The formula for `flat_per_invocation` is presumably just `rate` (constant). The formula for `per_input_byte` is presumably `rate × input_bytes`; for `per_output_byte` is `rate × output_bytes`. None of this is stated explicitly. A coding agent implementing U-OD-39 must invent the formulas. This silently delegates an architectural micro-decision.
- **Discriminator that classifies as Class 2 review-severity:** (a) — substantive content gap; cost-attribution arithmetic is audit-load-bearing per §C-OD-28.4 invariant 2 (Decimal arithmetic) + invariant 3 (string-serialization preservation).
- **Evidence:** OD spec v1.8 §C-OD-28.1 verbatim ToolRate declaration; U-OD-39 AC #2 verbatim above.
- **Anti-fabrication attack engaged:** A5 (missing uncertainty signals) — the unit silently delegates the formulas without flagging them as implementer-discretion.
- **Axis-domain attack engaged:** OD-axis — cost-attribution arithmetic precision.
- **Resolution path:** Phase C iteration-2 plan revision — either (i) author 3 formulas in U-OD-39 explicitly as additional ACs, OR (ii) flag formulas as deferred-to-impl-discretion in U-OD-39 AC #2 wording + add a follow-up review item at Phase E handoff. Implementation-planner's discretion; the gap must be surfaced one way or the other.
- **§2.7.6 fork class induced:** Class 3 (informational) — formula gap; impl arc can pick reasonable defaults; surface for next review.

### F2-05 — Cluster 4 (OD 20 units) + Cluster 10 (CP 15 units) sub-cluster decomposition recommended

- **Location:** `design-substrate/Implementation_Plan_Control_Plane_v2_15.md` §1 (Cluster 10 — 15 units) + `design-substrate/Implementation_Plan_Operational_Discipline_v2_14.md` §1 (Cluster 4 — 20 units)
- **Defect:** Per the `phase-7-implementation` skill cluster-open discipline, an atomic-unit cluster opens for execution as a single-arc landing. Empirical pattern from prior arcs (U-RT-58 / U-RT-59 / U-RT-60 each landed 4-8 commits with mid-arc operator interaction at cluster sizes of ~6-10 units). **Cluster 4 (OD 20 units) is 2-3× the precedent landing size**; risk of mid-cluster re-design, scope drift, or context-window exhaustion. Cluster 10 (CP 15 units) is borderline (1.5-2× precedent). Sub-cluster decomposition would mitigate.
- **Discriminator that classifies as Class 2 review-severity:** (a) — substantive content choice in current-phase artifact (plan-structure decision). Affects Phase 7 execution-time arc-shaping decisions.
- **Evidence:** Phase C log §3 cluster boundary table verbatim shows cluster sizes (8 / 15 / 20 across the 3 axes). Prior arc landings (U-RT-58 / U-RT-59 / U-RT-60 / U-RT-62) per phase-7-bootstrap-status memory ranged 4-8 commits each. Cluster 4 spans 4 distinct compositional surfaces (workflow-envelope, cost-attribution, sqlite write, rate-table) + 5 canonical schemas — natural sub-cluster boundaries.
- **Anti-fabrication attack engaged:** A2 (silent scope narrowing) — applied to cluster-open discipline: the single-cluster framing may narrow operator's view of natural sub-arc boundaries.
- **Axis-domain attack engaged:** Cross-cutting — cluster-sizing discipline applies to all axes.
- **Resolution path:** Phase C iteration-2 plan revision — decompose Cluster 4 into sub-clusters (e.g., 4-OD-A: workflow-envelope + cost-attribution at LLM dispatch ~7 units; 4-OD-B: sqlite write-path ~4 units; 4-OD-C: rate-table + Decimal serialization ~4 units; 4-OD-D: 5 canonical schemas + cost-record audit-write ~5 units). Decompose Cluster 10 similarly (e.g., 10-CP-A: ValidatorFramework ~4; 10-CP-B: PauseResumeProtocol ~4; 10-CP-C: PerServerTrust+namespace ~5; 10-CP-D: hitl_gate + converter ~2). Implementation-planner picks the exact decomposition.
- **§2.7.6 fork class induced:** Class 3 (informational) — cluster-sizing recommendation; does not halt execution; operator may proceed with current single-cluster framing at the cost of higher arc-execution risk.

---

## Class 1 findings (minor — documentation drift)

### F1-01 — U-RT-65 + U-RT-66 AC #5 "Integration test... passes" implementer-discretion language

- **Location:** Runtime plan v2.11 §1 U-RT-65 AC #5 verbatim: *"Integration test against HTTP mock server passes"*; U-RT-66 AC #5 verbatim: *"Integration test against SSE mock server passes"*
- **Defect:** "Passes" is implementer-discretion — no defined success predicate. Compare U-RT-64 AC #5 which is more specific: *"Integration test against mock MCP server passes"* (also ambiguous, but matches U-RT-64's other ACs which enumerate specific success conditions). U-RT-65/66 lack the per-transport success specifics (e.g., U-RT-65 should specify "HTTP 200 + protocol_version returned + list_tools count > 0" rather than just "passes").
- **Resolution:** Inline fix at Phase C iteration-2; tighten AC #5 wording to enumerate observable success conditions.

### F1-02 — U-OD-35 AC #5 "span visible at OTel collector" missing attribute specifier

- **Location:** OD plan v2.14 §1 U-OD-35 AC #5 verbatim: *"Integration test: workflow.envelope span visible at OTel collector"*
- **Defect:** "Visible" is implementer-discretion — no defined predicate. The test needs to assert specific attribute presence (e.g., all 12 attributes per §C-OD-25.1) OR span name match OR both. U-OD-36 AC #5 is more specific ("assert all 12 attributes present on span at OTel collector"); U-OD-35 AC #5 should match similar precision.
- **Resolution:** Inline fix at Phase C iteration-2; tighten AC #5.

### F1-03 — U-CP-65 cross-axis dep on U-OD-51 may be soft-dep (schema-doc-vs-runtime-execution)

- **Location:** CP plan v2.15 §1 U-CP-65 Depends-on line: `Depends on: [U-CP-63, U-CP-64, U-OD-51 (cross-axis: OD)]`
- **Defect:** U-CP-65 emits `pause.captured` + `resume.attempted` spans with attributes whose canonical schema is at OD §C-OD-30 (U-OD-51's product). At runtime, the producer-side code sets attribute names by string literal — it does NOT import the OD canonical schema module. The dependency on U-OD-51 is a **documentation/Pattern-P1-alignment** dependency, not a runtime-code dependency. Strictly the producer can run before the consumer-side schema lands. Declaring U-OD-51 as a hard `Depends on:` may over-block CP-side landing.
- **Resolution:** Inline fix at Phase C iteration-2; either (i) annotate U-CP-65's dep as soft-dep / documentation-dep, OR (ii) downgrade to a Pattern-P1-alignment-check predicate rather than a landing-order dep. The skill flags the classification ambiguity; implementation-planner picks the convention.

### F1-04 — U-OD-43 + U-CP-71 hidden dep on existing v2.13/v2.14-and-earlier landed carriers

- **Location:** OD plan v2.14 §1 U-OD-43 Depends-on: `[U-OD-42]`; CP plan v2.15 §1 U-CP-71 Depends-on: `(none within this delta)`
- **Defect:** U-OD-43 (RingBufferStage → sqlite flush) needs the existing `RingBufferStage` from OD plan v2.13 (U-RT-30 PARTIAL-LAND per memory `[[fork-trace-storage-pathclass-gap]]`). U-CP-71 (hitl_gate signature) relies on the C-RT-18 HITL gate composer (U-RT-60 landed). Neither dep is declared — both treat the existing landed carriers as ambient. Per implementation-planner §7: "A unit declares its **direct** dependencies, not transitive ones... A unit's declared dependencies must be sufficient for its acceptance criterion." The convention "Depends on: (none within this delta)" silently relies on the existing carrier; spotting this requires reading external context.
- **Resolution:** Inline fix at Phase C iteration-2; either (i) declare existing-landed unit IDs in `Depends on:` (e.g., U-OD-43: `Depends on: [U-OD-42, U-OD-30 (existing v2.13)]`), OR (ii) add a `Requires existing:` annotation per implementation-planner convention. The skill flags the missing-precision; implementation-planner picks the convention.

---

## Findings considered and rejected (transparency)

10 substantive checks applied; the following did NOT surface findings.

1. **Topological sort acyclicity.** Spot-checked 8 dependency declarations: U-CP-72 → 7 predecessors (no return cycle); U-OD-41 → U-CP-72 (no return cycle to OD); U-RT-67 → U-RT-64/65/66 + U-CP-68/69 (no return cycle); U-OD-39 → U-RT-67 (no return cycle); U-OD-50 → U-CP-58 (no return cycle to OD). Aggregate DAG is acyclic. ✓
2. **Hidden coupling — direct.** No detected case where Unit B's AC silently requires Unit A's product within the delta. The 4 surfaced hidden-coupling-adjacent cases (F2-01 transport conjunction, F2-02 cost prefix gap, F1-03 soft-dep, F1-04 ambient carriers) are precision issues, not silent omissions.
3. **A1 silent grounding collapse.** Every unit cites its spec contract section verbatim (e.g., "Implements: Runtime spec v1.13 §14.9.1"). No paraphrased citations. ✓
4. **A4 fabricated citations.** Spot-checked 6 spec citations: C-RT-19 §14.9.1 (verified at Phase B); C-CP-25 §25.7 invariant 3 (verified); C-OD-28.1 ToolRate (verified); CXA v2.6 §2.3.7 (verified); ADR-F4 v1.1 (cited at U-RT-63); ADR-D5 v1.4 (cited at U-CP-71). No fabrication. ✓
5. **A8 framing contamination (highest-value).** No plan unit picks a stack value the `CLAUDE.md` framing does not commit. `mcp` Python SDK, `Pydantic v2`, `asyncio`, `httpx`-adjacent, `sqlite3` stdlib — all match CLAUDE.md §3.1 commitments or stdlib defaults. ✓
6. **Materializability sampling.** Traced 5 representative units (U-RT-64 STDIO startup; U-CP-60 ValidatorFramework.evaluate; U-OD-46 RateTable dataclasses; U-CP-72 converter extension; U-OD-43 sqlite flush). 4 of 5 materializable per spec; U-OD-39 surfaced gap captured at F2-04. ✓
7. **Per-unit ≤150 LOC budget.** Spot-checked 5 units; estimated LOC: U-RT-64 ~120, U-CP-60 ~80-100, U-OD-43 ~50-80, U-CP-72 ~75 (5 branches × ~15 LOC), U-OD-50 ~50. All within budget. ✓
8. **Cross-axis edge bidirectional consistency.** Verified 4 cross-axis edges: U-OD-50 ← U-CP-58 (declared at U-OD-50; U-CP-58 declares "none within delta" — no reverse cycle); U-CP-61 → U-OD-50 (declared at U-CP-61); U-CP-72 → U-RT-69, U-RT-70 (declared at U-CP-72); U-OD-41 → U-CP-72 (declared at U-OD-41). All 13 cross-axis edges per Phase C log §2 cross-checked; no reverse-direction cycles. ✓
9. **Operator-ratified decision absorption (Phase C log §7).** Verified 5 of 11 ratifications: F2-03 OPERATOR_BURDEN_EXCEEDED → ESCALATE_HITL at U-CP-60 AC #1 ✓; Decision 1.D4 STDIO+HTTP+SSE at U-RT-64/65/66 ✓; Decision 3.D1 ALLOW with tier-floor at U-CP-68 AC #2 ✓; Decision 2.D7 STRICT MaterialDiffPolicy at U-CP-62 AC #2 ✓; F2-06 Decimal string-serialization at U-OD-49 ✓. All spot-checked absorptions correct. ✓
10. **Pattern-D 15-type inheritance discipline.** Verified — no Phase C unit re-decomposes Pattern-D types; all cite CP plan v2.9 + v2.10 inheritance per Phase A.1. ✓

---

## Disposition

Per `Project_Workflow_v1_8.md` §4.1 + plan file Phase D loop discipline:

- **0 Class 3 findings** → no phase re-opening (no Phase A spec changes owed; no Phase B re-run).
- **5 Class 2 findings** → **Phase C iteration-2 plan revision required** before advancing to Phase E.
- **4 Class 1 findings** → inline drift fixes at the iteration-2 pass.

**Recommended sequencing:**

1. **Phase C iteration-2 fix pass** for F2-01 through F2-05 (precision + test coverage + cluster-sizing) + F1-01 through F1-04 (drift). All fixes are within the implementation-planner's apply scope (no architectural decisions; no operator ratifications owed except F2-02 which surfaces a Class 2 fork-class operator-decision between two readings — surface via AskUserQuestion before iteration-2 apply).
2. **Phase D iteration-2** (re-run this review against iteration-2 plan deltas). Expected outcome: zero open Class 2 findings → advance to Phase E.

**Operator-decision surfaces (1):**
- F2-02 — U-OD-41 cost-attribution audit-write path: (i) extend U-CP-72 + CXA v2.6 to add 8th `cost:` prefix + new CXA row, OR (ii) restructure U-OD-41 to write OD audit ledger directly without converter (OD-internal). Two valid readings; operator picks.

### §2.7.6 fork class summary (iteration 1)

- 0 Class 1 (halt-execution).
- 1 Class 2 (in-execution operator decision) — F2-02 cost-prefix routing.
- 4 Class 3 (informational) — F2-01 / F2-03 / F2-04 / F2-05 + 4 drift items.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/Plan_Phase_D_Adversarial_Review_v1.md` |
| Iteration | 1 of N (loop continues until ZERO open Class 2 + every Class 1 resolved or absorbed) |
| Date | 2026-05-21 |
| Mode | `harness-adversarial-reviewer` Phase-7 pre-implementation review mode (P6-CK plan-corpus pass) |
| Scope | 4 Phase C plan deltas + Phase C authoring log |
| Class 1 findings | 4 (drift; inline fix) |
| Class 2 findings | 5 (4 inline-fixable + 1 operator-decision marker at F2-02) |
| Class 3 findings | 0 |
| §2.7.6 Class 1 forks | 0 |
| §2.7.6 Class 2 forks (operator decision) | 1 (F2-02) |
| §2.7.6 Class 3 forks (informational) | 4 (F2-01 / F2-03 / F2-04 / F2-05) + 4 drift items |
| Author-mode-drift check | Cleared — no finding's Resolution path supplies replacement text |
| Empty rejected-findings check | Cleared — 10 substantive checks enumerated |
| Severity distribution sanity | Cleared — Class 3 = 0; Class 2 = 5; Class 1 = 4; balanced |
| Decision-vocabulary | 8 *decided* + 1 *proposing* (F2-02; two readings spelled out) |
| Next gate | Phase C iteration-2 (after operator-decision turn for F2-02); then Phase D iteration-2 |
