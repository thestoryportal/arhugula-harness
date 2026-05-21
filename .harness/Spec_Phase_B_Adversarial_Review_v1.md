# Adversarial Review — Phase A Spec Bundle (iteration 1)

## Summary

- **Checkpoint:** Phase B — Spec adversarial review loop (Remaining-Work Closure Arc)
- **Artifacts reviewed:** 5 spec deltas + 2 reconciliation records (per Phase A.0 → A.5 landings)
- **Date:** 2026-05-21
- **Iteration:** 1 (filed at `.harness/Spec_Phase_A_Iteration_1_Log.md` for traceability per plan file Phase B)
- **Finding count by §4.1 review-severity:** Class 3 (severe — phase re-opening): **0** · Class 2 (moderate — current-phase revision): **7** · Class 1 (minor — drift): **3**
- **Highest-severity finding:** F2-02 (Pattern-P1 byte-exact alignment defect at OD §C-OD-29 vs CP §25.5)
- **§2.7.6 Phase-7 fork classes induced:** 3 Class 2 (in-execution operator decision) — F2-04 / F2-05 / F2-06; 0 Class 1 (halt-execution); 4 Class 3 (informational — F2-01 / F2-02 / F2-03 / F2-07)
- **Disposition recommendation:** **Phase A revision pass (iteration 2)** for F2-01 / F2-02 / F2-03 spec-quality fixes; **operator-decision pass** for F2-04 / F2-05 / F2-06 markers; **Class 1 inline fixes** for F1-01 / F1-02 / F1-03. Advance to Phase C ONLY AFTER iteration 2 closes the Class 2 spec-quality items + operator dispositions the 3 §2.7.6 Class 2 markers.

---

## Class 3 findings (severe — phase re-opening)

**None.** Discriminator (b) and (c) walks did not fire. The Phase A bundle does not contradict any ADR commitment, does not pick a stack value the workspace `CLAUDE.md` framing does not commit, does not assume single-LLM or contradict ADR-F1 v1.2, and does not require upstream-phase artifact revision. Phase A.1's CONFIRMATION-OF-PRIOR-RATIFICATION verdict held; no design-phase back-flow is owed.

---

## Class 2 findings (moderate — current-phase revision)

### F2-01 — Runtime spec v1.13 §14.9 "subprocess" terminology leaks STDIO assumption to HTTP/SSE transports

- **Location:** `design-substrate/Spec_Harness_Runtime_v1.md` §14.9.1 (architectural surfaces — "spawn subprocess; protocol handshake; populate ToolRegistry via list_tools") + §14.9.5 fail class `RT-FAIL-MCP-HOST-STARTUP` description ("subprocess termination") + §14.9.6 invariant 1 ("Subprocess started exactly once per bootstrap") + §14.9.6 invariant 5 ("STDIO + HTTP + SSE all supported at v1 ... `MCPClientHost.start()` selects transport per per-server bootstrap config; **all 3 implement subprocess/protocol lifecycle**")
- **Defect:** Decision 1.D4 RATIFIED expanded transport scope to STDIO + HTTP + SSE (per operator ratification 2026-05-21). The contract correctly enumerates 3 transports in §14.9.6 invariant 5, but §14.9.1 + §14.9.6 invariant 1 + the `MCPHostStartupError` semantics in §14.9.5 ALL leak STDIO-specific subprocess terminology. HTTP transports have no subprocess (they're TCP clients to a remote server); SSE transports have no subprocess. The spec is internally inconsistent: "STDIO + HTTP + SSE all supported" is contradicted by "all 3 implement subprocess/protocol lifecycle" — HTTP and SSE do NOT implement subprocess lifecycle.
- **Discriminator that classifies as Class 2 review-severity:** (a) — substantive content gap requiring spec revision. Does not require upstream-phase artifact change (discriminator (b) does not fire). Does not violate a `CLAUDE.md` project commitment (discriminator (c) does not fire).
- **Evidence:** §14.9.6 invariant 5 verbatim: *"`MCPClientHost.start()` selects transport per per-server bootstrap config; all 3 implement subprocess/protocol lifecycle, list_tools/call_tool, and health-check."* The "subprocess" word is invariant 1's main verb. HTTP/SSE contracts cannot satisfy "subprocess started exactly once per bootstrap" — they have HTTP-client lifecycle (connection pool open/close) instead.
- **Anti-fabrication attack engaged:** A2 (silent scope narrowing) — the spec narrows the operational semantics to STDIO even though the ratified scope includes HTTP + SSE.
- **Axis-domain attack engaged:** AS-axis (action surface) — the MCP host lifecycle contract is the AS-axis-adjacent surface; the substitution H_T-CP-18 hinges on this contract being correct for ALL 3 transports.
- **Resolution path:** Phase A iteration-2 spec revision. The shape: replace "subprocess" with transport-neutral terminology ("MCP host process" or "MCP client instance") at §14.9.1 + §14.9.6 invariants 1 + 5; differentiate "subprocess" (STDIO-only) from "HTTP client connection" (HTTP) from "SSE event stream" (SSE) in §14.9.5 fail-class language. No new contract; refinement of existing prose. The skill does NOT supply replacement text per FM-C author-mode-drift discipline.
- **§2.7.6 fork class induced:** Class 3 (informational) — does not halt Phase-7 execution; spec-quality fix only.

### F2-02 — OD spec v1.8 §C-OD-29 schema gap vs CP §25.5 (Pattern-P1 byte-exact alignment defect)

- **Location:** `design-substrate/Spec_Operational_Discipline_v1_8.md` §C-OD-29.1 canonical attribute set table vs `design-substrate/Spec_Control_Plane_v1_10.md` §25.5 span emission table
- **Defect:** The Pattern-P1 byte-exact alignment discipline (per CXA v2.6 §2.3.7 + workspace `CLAUDE.md` framing) requires the producer-side spec attribute list to match the consumer-side canonical schema list. Cross-check reveals two mismatches:
  1. CP §25.5 lists `step.id` as an attribute on `validator.evaluate` (outer envelope). OD §C-OD-29.1 canonical attribute set OMITS `step.id`.
  2. CP §25.5 lists `validator.escalation` as a span (links to subsequent `hitl.gate.evaluated` via parent-context). OD §C-OD-29.1 has NO attributes listed under a `validator.escalation` span site row — the span exists in the producer-side spec but has zero canonical attribute commitments in the OD-side schema.
- **Discriminator that classifies as Class 2 review-severity:** (a) — substantive content gap requiring OD spec §C-OD-29.1 revision. Does not require upstream change to CP spec v1.10 §25.5 (producer-side is authoritative; consumer-side schema is the one with the gap).
- **Evidence:** CP spec v1.10 §25.5 table row 1: *"`validator.evaluate` | Every evaluation (outer envelope) | `step.id`, `validator.outcome`, `validator.burden_count_cumulative`"*. OD spec v1.8 §C-OD-29.1 attribute table has rows for `validator.outcome` + `validator.burden_count_cumulative` but NO `step.id` row. CP §25.5 table row 4: *"`validator.escalation` | ESCALATE outcome | Links to subsequent `hitl.gate.evaluated` span via parent-context propagation"*. OD §C-OD-29.1 has no row for the `validator.escalation` span.
- **Anti-fabrication attack engaged:** None directly. This is a Pattern-P1 axis-domain finding.
- **Axis-domain attack engaged:** CXA-axis — byte-exact alignment failure at composition seam. Per CXA v2.6 §2.3.7 row 5 (ValidatorFramework → U-OD-00), the producer + consumer commit to a shared attribute set; the spec layer should declare them identically.
- **Resolution path:** Phase A iteration-2 OD spec §C-OD-29.1 revision. Add the missing rows (`step.id` on `validator.evaluate`; whatever attributes the `validator.escalation` span carries per its link-to-hitl semantics). Verify other span attribute lists in §C-OD-29.1 fully cover the CP §25.5 producer-side claims.
- **§2.7.6 fork class induced:** Class 3 (informational) — Pattern-P1 alignment defect surfaces; spec revision closes; no execution halt.

### F2-03 — CP spec v1.10 §25.2 ValidatorOutcome → ValidatorNextAction mapping unspecified

- **Location:** `design-substrate/Spec_Control_Plane_v1_10.md` §25.2 (`ValidatorOutcome` 5-class enum + `ValidatorEvaluation.next_action` field with `ValidatorNextAction` enum) + §25.8 "Deferred to implementation discretion" claim
- **Defect:** §25.2 declares two enums: `ValidatorOutcome` (5 values: PASS / REVALIDATE / ESCALATE / PERMANENT_FAIL / OPERATOR_BURDEN_EXCEEDED) and `ValidatorNextAction` (4 values: PROCEED / RETRY / ESCALATE_HITL / ABORT). The `ValidatorEvaluation.next_action` field commits to one ValidatorNextAction per evaluation. **The mapping function from ValidatorOutcome to ValidatorNextAction is NOT specified.** §25.8 punts: *"`ValidatorNextAction` enum value names — PROCEED | RETRY | ESCALATE_HITL | ABORT suggested; impl arc selects + documents at composer body."* This says the enum *value names* are deferred (already inconsistent with §25.2 which lists them definitively) — but the MAPPING is what's missing. PASS → PROCEED is obvious; REVALIDATE → RETRY is plausible; ESCALATE → ESCALATE_HITL is plausible; PERMANENT_FAIL → ABORT is plausible; **OPERATOR_BURDEN_EXCEEDED → ???** has no obvious mapping (ABORT? PROCEED with degradation? ESCALATE_HITL with an operator-notification variant?).
- **Discriminator that classifies as Class 2 review-severity:** (a) — substantive content gap. The materializability dimension (review dimension 4) reveals that a coding agent writing the ValidatorFramework would have to *pick* the mapping for OPERATOR_BURDEN_EXCEEDED without contract guidance — that's an architectural decision being silently delegated to implementation.
- **Evidence:** §25.2 verbatim: *"`ValidatorOutcome` (5-class enum): ... `OPERATOR_BURDEN_EXCEEDED = "operator_burden_exceeded"` # degrade per persona-tier (runtime spec v1.13 §14.10 `OperatorBurdenEvaluator`)"*. §25.2 verbatim: *"`ValidatorEvaluation` ... `next_action: ValidatorNextAction` # PROCEED | RETRY | ESCALATE_HITL | ABORT"*. §25.8 verbatim: *"`ValidatorNextAction` enum value names — PROCEED | RETRY | ESCALATE_HITL | ABORT suggested; impl arc selects + documents at composer body."* No mapping table.
- **Anti-fabrication attack engaged:** A5 (missing uncertainty signals) — the §25.8 defer-to-impl framing on a load-bearing mapping is over-confident; the actual mapping for OPERATOR_BURDEN_EXCEEDED is genuinely [SPECULATIVE] without operator decision.
- **Axis-domain attack engaged:** CP-axis. Per CP-AL-1 ("H_E sub-agent topology ≠ H_T TopologyPattern enum"), CP-axis discipline holds that enums + their semantics live at spec, not impl.
- **Resolution path:** Phase A iteration-2 CP spec §25.2 revision — add an explicit ValidatorOutcome → ValidatorNextAction mapping table. The shape: 5 rows (one per outcome) → 4 next_action values. Operator decides the OPERATOR_BURDEN_EXCEEDED row's mapping.
- **§2.7.6 fork class induced:** Class 2 (operator decision) — the OPERATOR_BURDEN_EXCEEDED mapping is the operator's call; the other 4 mappings are uncontroversial (assignable by the skill's *proposing* discipline but not at this skill, per FM-C). Phase B disposition routes this to operator.

### F2-04 — `[Phase B review]` marker at OD §C-OD-25.5 — workflow.envelope alternative shape

- **Location:** `design-substrate/Spec_Operational_Discipline_v1_8.md` §C-OD-25.5 closing paragraph: *"`[Phase B review: workflow.envelope is the LOAD-BEARING span for compound-irrelevance unblock. Reviewers should verify per-attribute necessity + invariant completeness. Alternative shape: split workflow.envelope into workflow.entry + workflow.exit two-span pattern (rejected default; single-envelope simpler).]`"*
- **Defect:** The author (Phase A.5) embedded this marker as an explicit operator-decision handle. The single-envelope default is rational but the alternative (workflow.entry + workflow.exit two-span pattern) has a real argument — single-envelope spans that live for the entire workflow may be too long for some OTel exporters' buffering preferences (default OTel batch processor flushes on span END; a 30-minute workflow holds the span buffer for 30 minutes). The two-span pattern flushes on entry-close + opens fresh on exit. Operator decision needed.
- **Discriminator that classifies as Class 2 review-severity:** (a) — substantive content choice in current-phase artifact. Author flagged it; reviewer affirms.
- **Evidence:** The verbatim marker text above.
- **Anti-fabrication attack engaged:** None — the marker is honest about the open question.
- **Axis-domain attack engaged:** OD-axis observability discipline.
- **Resolution path:** Operator ratification at §2.7.6 Class 2 disposition (in-execution operator decision). The skill recommends the default (single-envelope) be retained absent operator preference for the two-span pattern, but the choice is operator-owned.
- **§2.7.6 fork class induced:** **Class 2 (in-execution operator decision)** — operator picks; spec amended per ratification at iteration-2.

### F2-05 — `[Phase B review]` marker at OD §C-OD-26.5 — validator cost-meter granularity

- **Location:** `design-substrate/Spec_Operational_Discipline_v1_8.md` §C-OD-26.5: *"`[Phase B review: validator cost-meter is LOW-CONFIDENCE default; some validators are heavy (semantic-inconsistency check may invoke another LLM). Reviewers may prefer marking validator NON-BILLABLE or distinguishing validator.simple vs validator.llm_check.]`"*
- **Defect:** §C-OD-26.2 billable-span enumeration lists `validator.evaluate` as YES (billable) with cost-meter "execution_time_ms × $/CPU_ms". This treats every validator as CPU-bound. Real-world validators may invoke another LLM (semantic-inconsistency check; safety-policy check via judge model) — these have token-meter cost, not CPU cost. The single-cost-meter framing is brittle.
- **Discriminator that classifies as Class 2 review-severity:** (a) — substantive content gap; operator may prefer to either mark validator NON-BILLABLE (defer to operator-installed validator's own cost-attribution) or split into `validator.simple` (CPU-meter) + `validator.llm_check` (token-meter) sub-classes.
- **Evidence:** §C-OD-26.5 verbatim above.
- **Anti-fabrication attack engaged:** A5 (missing uncertainty signals) — author flagged "LOW-CONFIDENCE default" inline.
- **Axis-domain attack engaged:** OD-axis cost-attribution discipline.
- **Resolution path:** Operator decision at §2.7.6 Class 2 disposition. Three plausible options surfaced by author: (a) keep CPU-meter default; (b) mark validator NON-BILLABLE; (c) split into validator.simple + validator.llm_check sub-classes.
- **§2.7.6 fork class induced:** **Class 2 (in-execution operator decision)**.

### F2-06 — `[Phase B review]` marker at OD §C-OD-28.5 — PRICE_TABLE_REF Decimal invariant sufficiency

- **Location:** `design-substrate/Spec_Operational_Discipline_v1_8.md` §C-OD-28.5: *"`[Phase B review: PRICE_TABLE_REF was operator-flagged ~100-200 LOC of rate-table authoring as bounded X-AL-2 residual. Reviewers should confirm Decimal vs float invariant + version-immutability is sufficient.]`"*
- **Defect:** §C-OD-28.4 invariant 2 declares: *"All rate computations use Python `Decimal` (not float) for cost-attribution audit precision."* Reviewer agrees this is correct discipline. **But** the §C-OD-28.1 schema declares rate fields as `Decimal` — which is fine in Python — except OTel exporters typically serialize attribute values as JSON-native types (string / int / float / bool). When `cost_attribution.cost_decimal` is emitted as a span attribute, it must round-trip through float (lossy) OR be carried as a string. The spec does NOT specify which. If float, the Decimal invariant at §C-OD-28.4 is defeated at the observability boundary; if string, the spec needs to commit that.
- **Discriminator that classifies as Class 2 review-severity:** (a) — substantive content gap; invariant 2 needs an additional clause on serialization-boundary preservation.
- **Evidence:** §C-OD-28.5 verbatim above; §C-OD-28.1 RateTable schema; §C-OD-28.4 invariant 2; no §C-OD-28 mention of OTel attribute serialization.
- **Anti-fabrication attack engaged:** A5 (missing uncertainty signals) — author flagged this inline as needing operator confirmation.
- **Axis-domain attack engaged:** OD-axis. Cross-axis to AS-axis (OTel attribute serialization is at the producer→consumer boundary).
- **Resolution path:** Operator decision at §2.7.6 Class 2 disposition. The two readings: (a) commit string-serialization of Decimal at span attribute boundary (preserves precision; non-standard OTel pattern); (b) commit float-serialization (standard but loses precision; audit-ledger may keep separate Decimal authoritative copy).
- **§2.7.6 fork class induced:** **Class 2 (in-execution operator decision)**.

### F2-07 — Phase A composer scope did NOT address 9 STILL-BOUNDED substitutions surfaced at Phase 1

- **Location:** `.harness/Phase_A_2_Contract_Drafts_v1.md` operator-ratified scope ("ALL 4 absent composers (full closure path)") vs Phase 1 Explore Agent 1 retirement-frontier inventory (CP STILL-BOUNDED: CP-12 / CP-16 / CP-17 / CP-19 / CP-23; OD STILL-BOUNDED: OD-1 / OD-3 / OD-4 / OD-7)
- **Defect:** Phase 1 Agent 1's STILL-BOUNDED inventory (verified against `harness-cp/CLAUDE.md` §4.1 retirement table) lists 8 CP + 5 OD primitives still bounded. Phase A.2 + A.5 contracts substantively touch: CP-18 (via §27 PerServerTrustEvaluator), CP-21 (via §25 ValidatorFramework), CP-22 (via §26 PauseResumeProtocol), OD-5 (via §C-OD-26 cost-attribution), OD-6 (via §C-OD-27 sqlite write). That's 5 of 13 (8 CP + 5 OD = 13) STILL-BOUNDED primitives addressed. **8 of 13 NOT addressed by Phase A:** CP-12 (sandbox-tier dispatch — touched by §14.9 but no full composer authored), CP-16 (memory primitive consumption), CP-17 (files primitive consumption), CP-19 (cross-deployment monotonicity), CP-23 (bridging-arc traversal), OD-1 (deferral envelope), OD-3 (composite sampler), OD-4 (pre-collector redaction processor), OD-7 (preservation invariants). The Phase A scope was operator-ratified per plan file; the gap is not a defect-of-scope but an awareness item.
- **Discriminator that classifies as Class 2 review-severity:** (a) — substantive content gap in the Phase E handoff artifact's scope-enumeration. The PRESENT-arc scope-gap is not a Phase A defect; the FUTURE-arc planning enumeration is owed at Phase E.
- **Evidence:** Phase 1 Explore Agent 1 final inventory + `harness-cp/CLAUDE.md` §4.1 verbatim retirement table cross-check.
- **Anti-fabrication attack engaged:** A2 (silent scope narrowing) — applied to the Phase E handoff: if the handoff doesn't enumerate this 8-primitive frontier, downstream sessions will lack visibility on remaining work.
- **Axis-domain attack engaged:** Cross-axis (the gap spans CP + OD axes).
- **Resolution path:** Phase E handoff artifact MUST enumerate the 8 still-unretired substitutions + their respective blockers (memory-invocation composer / files-invocation composer / cross-deployment runtime / bridging-arc composer / deferral-gate composer / composite sampler / redaction processor / preservation enforcement loop). Existing artifact reference: per Phase A.1 §3 disposition matrix (already classifies each blocker per Class).
- **§2.7.6 fork class induced:** Class 3 (informational) — Phase E handoff documentation; no execution halt.

---

## Class 1 findings (minor — documentation drift)

### F1-01 — OD §C-OD-29 framing-vs-actual count drift ("4-attribute" vs 8-attribute schema)

- **Location:** `design-substrate/Spec_Operational_Discipline_v1_8.md` change-note (top): *"C-OD-29 (NEW) — `validator.*` 4-attribute namespace + ValidatorEscalationAuditPayload row shape"*. §C-OD-29.1 closing paragraph: *"(Attribute count: 8 — the change-note's "4-attribute" framing referenced the *minimum-emit* set; actual schema = 8 attributes across span sites. Reviewers may amend the change-note count framing at v1.9.)"*
- **Defect:** Change-note says "4-attribute namespace" but §C-OD-29.1 table has 8 attributes. Author self-flagged the drift at §C-OD-29.1 closing paragraph. Pure documentation drift; no semantic impact.
- **Resolution:** Inline fix at Phase A iteration-2 — change "4-attribute" to "8-attribute" in change-note + remove the reconciliation paragraph at §C-OD-29.1 (no longer needed).

### F1-02 — CXA v2.6 §2.3.7 rows 3-7 retain `§NN` placeholders after OD v1.8 landed in same arc

- **Location:** `design-substrate/Cross_Axis_Composition_Document_v2_6.md` §2.3.7 rows 3-7 verbatim show `"OD spec v1.8 §NN (owed at Phase A.5)"` in the Contract column. The CXA v2.6 filing footer claims *"rows 3-7 resolve to §C-OD-32 / §C-OD-33 / §C-OD-29 / §C-OD-30 / §C-OD-31 respectively"*. The row contents themselves were not back-patched after OD v1.8 was authored.
- **Defect:** Row-content drift; the citations resolve in spirit (per filing footer) but not byte-exact (per the row text). FM-K-adjacent: disposition-without-evidence shape — the footer claims resolution; the rows still say "owed at Phase A.5".
- **Resolution:** Inline fix at Phase A iteration-2 — back-patch CXA v2.6 §2.3.7 rows 3-7 to replace `§NN (owed at Phase A.5)` with the resolved section refs (§C-OD-32 / §C-OD-33 / §C-OD-29 / §C-OD-30 / §C-OD-31).

### F1-03 — Runtime spec v1.13 §14.10 `hitl.operator_burden.*` namespace vs single-span name minor inconsistency

- **Location:** `design-substrate/Spec_Harness_Runtime_v1.md` §14.10.3 Spans (burden) section + change-note §14.10 description (refers to `hitl.operator_burden.*` namespace) vs §14.10.3 table (single span `hitl.operator_burden.evaluated`)
- **Defect:** The namespace label `hitl.operator_burden.*` suggests multiple spans; the actual emission is one span (`hitl.operator_burden.evaluated`). Minor framing inconsistency.
- **Resolution:** Inline at Phase A iteration-2 — pick one framing convention (either "the `hitl.operator_burden.*` namespace [with one span `hitl.operator_burden.evaluated`]" or just call it the single-span name throughout).

---

## Findings considered and rejected (transparency)

11 substantive attack vectors were applied that did NOT surface a finding. Format: attack name + brief note on why the artifact handles it.

1. **A1 (silent grounding collapse).** Every substantive claim in the 5 spec deltas cites a primary source (ADR-FN / ADR-DN, CP plan v2.9 + v2.10, existing CP spec v1.9, AS spec C-AS-14/15, runtime spec internal cross-refs, CXA v2.5). No "engineering posts" or "the X working group" citations. ✓ handled.
2. **A4 (fabricated citations).** Spot-checked 5 citations: CP plan v2.9 Pattern-D type sections (verified by Phase A.1 §5 tiebreaker); CP spec v1.9 §13.5.1 NOTE 5 (existed verbatim per Phase 1 substrate); ADR-D5 v1.4 (referenced in workspace CLAUDE.md §2.2); ADR-D6 v1.2 §1.3 (referenced consistently); OTel GenAI semconv 1.41.0 (existing runtime spec reference, not novel). No fabricated citations detected. ✓ handled.
3. **A7 (weak-source escalation).** No [HIGH]/[MODERATE]/[SPECULATIVE] tags in the spec layer (specs are authoritative contracts, not opinion documents — convention preserved from existing v1.12). No weak-source escalation possible. ✓ handled.
4. **A8 (framing contamination) — HIGHEST-VALUE ATTACK.** Checked every spec against workspace `CLAUDE.md` §3.1 stack commitments: Python 3.12+, Pydantic v2, asyncio, uv, pyright, ruff, pytest+asyncio, per-provider SDKs, modelcontextprotocol/python-sdk (FastMCP), python-keyring, hand-rolled retry/breaker. Specs reference `asyncio`, `Pydantic v2`, FastMCP — all match commitments. NO framework-pull discipline violation (no tenacity/pybreaker/langgraph/crewai/langchain references). NO single-LLM assumption (multi-LLM commitment per ADR-F1 v1.2 preserved). NO persona assumption (specs are persona-neutral). NO deployment-surface commitment (specs don't pick cloud/local/hybrid). ✓ handled.
5. **A9 (cross-project context bleed).** All claims trace to either the design-substrate/ filesystem or to the operator-ratified drafts file at `.harness/Phase_A_2_Contract_Drafts_v1.md`. No "general framework knowledge" claims. ✓ handled.
6. **CP-AL-1 anti-leakage.** Spec deltas do NOT conflate H_E sub-agent topology with H_T TopologyPattern enum. C-CP-25/26/27 are CP-axis contracts at H_T level; no H_E sub-agent-tool framing leakage. ✓ handled.
7. **X-AL-1 boundary at MCP server process.** §14.9 C-RT-19 RuntimeToolDispatcher correctly homes the H_E ↔ H_T substrate boundary at the MCP server process (per `MCPClientHost` invocation via FastMCP `call_tool` — process isolation, not convention). ✓ handled.
8. **X-AL-3 no silent design extension.** All 5 new contracts were operator-ratified at `.harness/Phase_A_2_Contract_Drafts_v1.md`. No silent H_T design extension at execution-time. The §27 PerServerTrustEvaluator is NOT a new H_T primitive (`MCPTrustTier` carrier exists at CP plan v2.8 U-CP-00c); the contract materializes the existing primitive's runtime evaluator. ✓ handled.
9. **Materializability of representative atomic units.** Traced 3 anticipated Phase C units: (i) MCPClientHost.start() — materializable for STDIO (clear contract); F2-01 surfaces the HTTP/SSE gap. (ii) ValidatorFramework.evaluate() — materializable except for the OPERATOR_BURDEN_EXCEEDED next_action mapping (F2-03). (iii) WorkflowEnvelopeSpan — materializable (clear attribute list + lifecycle). 3 of 3 are materializable post-F2-01/F2-03 fix. ✓ handled with the two findings.
10. **CP plan v2.9 + v2.10 invalidation check.** Phase A.2 + A.5 contracts inherit Pattern-D field sets per Phase A.1 §4.2 citation table; do NOT re-author. CP plan v2.9 T2 X-AL-3 FACTOR-OUT preserved. CP plan v2.10 R-2/W-2 ratification preserved. ✓ handled.
11. **Pattern-D citation hygiene (review dimension 8).** Phase A.1 §5 tiebreaker (CP plan v2.9 lines 1-828 contain 16 Pattern-D type sections with 177 type references) established the substrate. Spot-checked 3 citations at CP spec v1.10 inheritance table: `ProposedAction` → C-CP-13 §13.1 (✓); `RetryPolicy` → C-CP-03 §3.5 (✓); `LeadAgentPlan` → CP plan v2.9 opaque Mapping (✓ — Phase A.1 record verified verbatim). ✓ handled.

---

## Disposition

Per `Project_Workflow_v1_8.md` §4.1:

- **0 Class 3 findings** → NO phase re-opening (no design-phase back-flow owed).
- **7 Class 2 findings** → **current-phase revision required** before advancing to Phase C.
- **3 Class 1 findings** → inline drift fixes at the same iteration-2 pass.

**Recommended sequencing:**

1. **Phase A iteration-2 fix pass** addressing F2-01 (terminology leak) + F2-02 (Pattern-P1 alignment) + F2-03 (mapping table) + F1-01 / F1-02 / F1-03 (drift). Routed back to spec-writer in apply mode (these are decided fixes for F2-01 + F2-02 + F1-01/02/03; F2-03 requires operator decision first for the OPERATOR_BURDEN_EXCEEDED → next_action mapping row).
2. **Operator-decision pass** for F2-04 (workflow.envelope shape) + F2-05 (validator cost-meter granularity) + F2-06 (PRICE_TABLE_REF serialization invariant) + F2-03 (OPERATOR_BURDEN_EXCEEDED mapping) + F2-07 (Phase E scope-enumeration confirmation). Surfaced via `AskUserQuestion` at the next session-turn before iteration-2 spec-writer apply.
3. **Phase B iteration-2** (re-run this review against the iteration-2 spec deltas). Expected outcome: zero open Class 2 findings → advance to Phase C.

**§2.7.6 fork class summary:**
- 0 Class 1 (halt-execution).
- 4 Class 2 (in-execution operator decision): F2-03 + F2-04 + F2-05 + F2-06.
- 4 Class 3 (informational): F2-01 + F2-02 + F2-07 + F1-01/02/03 (drift).

**Recommendation:** Operator surfaces the 4 Class 2 disposition decisions; spec-writer re-applies for the 4 informational + 3 drift items; this skill re-runs as iteration-2 adversarial review. Estimated cycle: 1 operator-decision turn + 1 spec-writer apply turn + 1 adversarial-review iteration-2 turn. Phase C opens at iteration-2 closure.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/Spec_Phase_B_Adversarial_Review_v1.md` |
| Iteration | 1 of N (loop continues until ZERO open Class 2 findings + every Class 1 finding resolved or absorbed per plan file Phase B loop discipline) |
| Date | 2026-05-21 |
| Mode | `harness-adversarial-reviewer` Phase-7 pre-implementation review mode |
| Scope | 5 Phase A spec deltas + 2 reconciliation records |
| Class 1 findings | 3 (drift; inline fix) |
| Class 2 findings | 7 (4 inline-fixable + 3 operator-decision markers + 1 scope-enumeration item) |
| Class 3 findings | 0 |
| §2.7.6 Class 1 forks | 0 |
| §2.7.6 Class 2 forks (operator decision) | 4 |
| §2.7.6 Class 3 forks (informational) | 4 |
| Author-mode-drift check | Cleared — no finding's Resolution path supplies replacement text |
| Empty rejected-findings check | Cleared — 11 substantive checks enumerated |
| Severity distribution sanity | Cleared — no all-Class-3 / no all-Class-1 escalation pattern |
| Decision-vocabulary | All findings *decided*; no *proposing* or *open* required |
| Next gate | Phase A iteration-2 spec-writer apply pass (after operator-decision turn for 4 Class 2 markers); then Phase B iteration-2 |
