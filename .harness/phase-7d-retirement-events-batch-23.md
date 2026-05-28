# Phase 7d Retirement Events — Batch 23

| Field | Value |
|---|---|
| Batch number | 23 |
| Filed at | 2026-05-28 (post H_T-AS-5 STILL-BOUNDED → RETIRED direct transit via AS spec v1.6 §15.6 row 1 idempotency-key attribute attachment at `sandbox.violation` span emission. 1092/1092 harness-runtime tests pass + 4 skipped — +1 new dedicated AS-5 join-contract test; ZERO behavior change at other spans / cross-axis surfaces.) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 + gate-text reframe per `[[batch-22 §2]]` sub-species 7.operator-explicit-deferred-close-gate precedent shape |
| Predecessor batch | `phase-7d-retirement-events-batch-22.md` (2026-05-27, 1 RETIRE-READY → RETIRED transit for H_T-CP-19; cumulative 29/49 RETIRED + 0/49 RETIRE-READY + 6/49 PARTIAL + 14/49 STILL-BOUNDED = 35/49 advanced) |

---

## §0 Batch context

**Status type: 1 STILL-BOUNDED → RETIRED direct transit (H_T-AS-5).** Cumulative RETIRED count advances 29/49 → 30/49 (59.2% → 61.2%); RETIRE-READY count unchanged at 0 (bucket REMAINS EMPTY); PARTIAL count unchanged at 6/49; STILL-BOUNDED count decrements 14 → 13; pipeline-advanced advances 35/49 → 36/49 (71.4% → 73.5%). **SIXTH RETIRE-READY-equivalent → RETIRED close in ledger history** counting direct transits — joins CP-16 batch-14, joint CP-18+AS-2 batch-16, CP-21 batch-17 corrective, joint CP-22 batch-18, CP-19 batch-22. AS-axis advances 4/6 → 5/6 RETIRED (66.7% → 83.3%); STILL-BOUNDED bucket 1 → 0 (AS-axis bucket NOW EMPTY for STILL-BOUNDED tier; only AS-8 PARTIAL remains pre-final). **AS-axis crosses 83.3% RETIRED threshold at this batch.**

This batch records the gate-text-reframed STILL-BOUNDED → RETIRED transit for **H_T-AS-5** (sandbox-event idempotency-key composition per C-AS-15 §15.6) via direct span-attribute attachment at the production `sandbox.violation` emission site:

| Commit | Artifact | Authority |
|---|---|---|
| (this commit) | `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py` — NEW `ATTR_IDEMPOTENCY_KEY = "idempotency_key"` constant; `_emit_sandbox_violation` signature widened to take `idempotency_key: str` 3rd parameter; 4 callsites (TIMEOUT / PROTOCOL_ERROR / TRANSPORT / SCHEMA_VIOLATION) pass `idempotency_key` from composed dispatch-step value | AS spec v1.6 §15.6 row 1 idempotency-key join contract (sandbox.violation events on a given tool.call parent span carry the same idempotency_key as the parent) |
| (this commit) | `harness-runtime/tests/test_lifecycle_runtime_tool_dispatcher.py` — 4 existing dual-attrs tests extended with `idempotency_key` 64-char sha256-hex assertion; +1 NEW dedicated test `test_dispatch_sandbox_violation_idempotency_key_matches_parent_dispatch` verifying the §15.6 row 1 join (sandbox.violation's idempotency_key equals the value passed to host.call_tool) | AS spec v1.6 §15.6 row 1 cross-axis correlation surface for cost-attribution-per-span (D6) + engine event history (D1) |
| (this commit) | Co-published bookkeeping: workspace `CLAUDE.md` §2.3 AS spec row + §2.4 AS plan row retirement-status notes | Workspace bookkeeping discipline per `.harness/phase-7d-retirement-ledger-v2.md` |

Per the operator-ratified runtime-only substitution-site reading at `.harness/phase-7d-retirement-ledger-v2.md` §2.1 + line-33 strict-reading discipline + the batch-16 §6 verification-shape sharpening discipline (seventh prospective application at batch-23):

> RETIRED = (criterion A MET) ∧ (criterion B structural-MET) ∧ (criterion B operational-MET) — where operational-MET requires all 3 binding-chain stages empirically verified: (1) carrier landed; (2) production span site / consumer site exists; (3) e2e exercise PASS against a real substrate exercising the contract semantic.

Under that discipline, H_T-AS-5 transitions STILL-BOUNDED → **RETIRED** directly:

- **Criterion A** (cited unit IDs landed). U-AS-16 → U-AS-19 cited at Meta-Arch §2.2 row 420 — `harness-as/src/harness_as/sandbox_event_idempotency.py` carries the 3 helpers (`attach_idempotency_key_to_sandbox_event`, `derive_sub_agent_idempotency_key`, `join_cost_attribution_by_idempotency_key`) per AS spec C-AS-15 §15.6. MET.
- **Criterion B structural-MET.** `sandbox.violation` child span at `_emit_sandbox_violation` sets `idempotency_key` attribute on the span at all 4 exception-path callsites; ATTR_IDEMPOTENCY_KEY constant declared.
- **Criterion B operational-MET.** Three stages all empirically verified:
  - Stage 1 (carrier landed) — AS-axis helpers exist at `harness-as/src/harness_as/sandbox_event_idempotency.py`
  - Stage 2 (production consumer site) — `_emit_sandbox_violation` invocation at dispatcher; `idempotency_key` in scope at all 4 callsites via composed dispatch-step value at `_compose_idempotency_key`
  - Stage 3 (e2e exercise PASS against real fastmcp substrate) — 4 existing dual-attrs tests + 1 new dedicated join-contract test all pass against a real `fastmcp.FastMCP` in-memory server (`_build_started_host` + `_dispatch_with_failing_call_tool` patches); 1092/1092 harness-runtime tests pass + 4 skipped

**Reframing closure note.** The batch-19 H_T-AS-5 row gate-text cited "production tool-dispatch invoking `sandbox_event_idempotency` composition function" as the criterion. Advisor reframing 2026-05-28 surfaced that the `harness-as` helpers (`attach_idempotency_key_to_sandbox_event` / `derive_sub_agent_idempotency_key` / `join_cost_attribution_by_idempotency_key`) operate on Pydantic `SandboxSpanEvent` models — a layer that production never constructs (production uses OTel `tracer.start_as_current_span` + `_set(span, attr, value)` directly). Literal "invoke the helper" reading is structurally impossible against the production OTel-span architecture. The satisfiable reading per AS spec C-AS-15 §15.6 row 1 contract is `sandbox.violation` events carry the parent `tool.call`'s `idempotency_key` as a span attribute — which is observable at the OTel layer regardless of which Python helper produces it. Operator ratified the reframe via AskUserQuestion 2026-05-28 (Option A "Reframe per batch-22 precedent + §15.6 row 1 only"). Same sub-species shape as batch-22 §2 sub-species 7.operator-explicit-deferred-close-gate — gate-text scope was structurally stale against the production architecture; the contract surface IS in-process and satisfiable; same-session reframe + close.

**Conclusion (preview):** **1 new RETIRED transition** (H_T-AS-5) — cumulative **30/49 RETIRED** (61.2%, +1 from batch-22). STILL-BOUNDED count **14 → 13**. RETIRE-READY count unchanged at 0. PARTIAL count unchanged at 6/49. Pipeline advanced (R+RR+P): **36/49 = 73.5%** (+1 from batch-22 71.4%). **AS-axis crosses 5/6 = 83.3% RETIRED**; AS-axis STILL-BOUNDED bucket NOW EMPTY (only AS-8 PARTIAL remains pre-final). ZERO cross-axis cascade verified (intra-runtime-axis impl only; AS spec UNCHANGED; OD/CP/IS specs UNCHANGED).

---

## §1 H_T-AS-5 STILL-BOUNDED → RETIRED

### §1.1 Pre-transition state (batch 22 close, 2026-05-27)

Per `phase-7d-retirement-events-batch-19.md` H_T-AS-5 row (last AS-touching batch; batch-22 was CP-axis only):

> H_T-AS-5 | STILL-BOUNDED | STILL-BOUNDED | Unchanged — gates on production tool-dispatch invoking `sandbox_event_idempotency` composition (independent gate from AS-4 sandbox.violation span emission)

### §1.2 Reframed gate close path (2026-05-28)

Pre-substantive empirical orientation at HEAD `36a7f91`:

1. `harness_as.sandbox_event_idempotency` exports 3 helpers operating on Pydantic `SandboxSpanEvent` model — `model_copy(update={...})` shape.
2. Production `_emit_sandbox_violation` at `runtime_tool_dispatcher.py:260-281` opens an OTel `sandbox.violation` span via `tracer.start_as_current_span(...)` and emits 2 attributes (`mcp.fail.class` + `sandbox.fail.class`) via `_set(span, attr, value)`. NO Pydantic event constructed.
3. Grep across `harness-runtime/src` shows ZERO callsites of all 3 harness-as helpers; the helpers are import-able but production never invokes them.
4. AS spec §15.6 row 1 contract reads: "sandbox.violation events on a given tool.call parent span carry the same idempotency_key as the parent." This is a span-attribute presence assertion, NOT a Python-helper invocation requirement.

Advisor 2026-05-28 confirmed the gate-text framing was stale against production OTel-span architecture. Operator ratified Option A via AskUserQuestion 2026-05-28: "Reframe per batch-22 precedent + §15.6 row 1 only — gate close via OTel span attribute satisfaction, not Pydantic helper invocation."

Implementation arc landed in single bundled commit:

1. **Constant declaration**: `ATTR_IDEMPOTENCY_KEY = "idempotency_key"` at module attribute-constant block in `runtime_tool_dispatcher.py`.

2. **Signature widening**: `_emit_sandbox_violation(tracer, mcp_fail_class)` → `_emit_sandbox_violation(tracer, mcp_fail_class, idempotency_key)`. Docstring updated to cite §15.6 row 1 contract.

3. **Attribute attachment**: `_set(span, ATTR_IDEMPOTENCY_KEY, idempotency_key)` added inside the `sandbox.violation` with-block alongside the 2 existing fail-class attrs.

4. **Callsite update**: 4 callsites (TIMEOUT line 432, PROTOCOL_ERROR line 435, TRANSPORT line 440, SCHEMA_VIOLATION line 446) pass `idempotency_key` from the composed dispatch-step value (`_compose_idempotency_key` at line 399). The local variable is in scope at all 4 callsites.

5. **Test extension**: 4 existing dual-attrs tests (`test_dispatch_*_emits_sandbox_violation_dual_attrs`) extended with `idempotency_key` 64-char sha256-hex assertion. +1 NEW dedicated test `test_dispatch_sandbox_violation_idempotency_key_matches_parent_dispatch` verifying the §15.6 row 1 join — patches `host.call_tool` to capture the `idempotency_key` argument; asserts the captured value equals the `idempotency_key` attribute on the `sandbox.violation` span.

6. **Bookkeeping**: workspace `CLAUDE.md` §2.3 AS spec row + §2.4 AS plan row retirement-status notes.

### §1.3 Binding-chain stage verification (batch-23 close)

| Stage | Required evidence | Verified at | Verification shape |
|---|---|---|---|
| 1. Carrier landed | `sandbox_event_idempotency` module + 3 helpers + `SandboxSpanEvent` Pydantic model | Pre-existing at `harness-as/src/harness_as/sandbox_event_idempotency.py` | AS-axis U-AS-16 → U-AS-19 close (cited Meta-Arch §2.2) |
| 2. Production consumer site | `sandbox.violation` span carries `idempotency_key` attribute | this commit | `_emit_sandbox_violation` sets ATTR_IDEMPOTENCY_KEY at 4 exception-path callsites; pyright clean (0 errors); 1091/1091 pre-existing runtime tests preserved |
| 3. E2E exercise PASS against real substrate | sandbox.violation.idempotency_key matches parent dispatch's idempotency_key end-to-end | this commit | 5 tests against real `fastmcp.FastMCP` in-memory server: 4 existing dual-attrs tests assert attribute presence + format (64-char sha256 hex); 1 new test asserts attribute VALUE matches the captured `host.call_tool` 3rd-arg value (the §15.6 row 1 join contract) |

**All 3 stages empirically MET.** Per [[verification-shape-sharpened-grep-vs-e2e]] discipline this is RETIRED — binding chain structurally + operationally complete via reframed in-architecture-layer scope.

### §1.4 Cross-axis cascade verification

ZERO cross-axis cascade verified empirically at the close arc:

- **Impl scope**: Intra-runtime-axis only (`harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py` + sibling test file).
- **AS spec UNCHANGED**: AS spec v1.7 §C-AS-15 §15.6 row 1 contract is the authority anchor; production caught up to spec; spec text not modified.
- **OD / CP / IS specs UNCHANGED**: §15.6 row 1 join is a span-attribute discipline at AS-axis; D6 cost-attribution + D1 engine event history are downstream consumers that read the attribute; their schemas are unchanged.
- **CXA v2.15 UNCHANGED**: no new typed seam; the existing AS spec ↔ runtime span-emission convention is satisfied by production catching up.
- **Sub-agent boundary inheritance (§15.6 row 2) NOT in scope at this batch**: `sub_agent_dispatch.py` propagates `idempotency_key` directly without invoking `derive_sub_agent_idempotency_key`; whether row 2 conjunctively gates AS-5 retirement is foreclosed at this batch per AskUserQuestion Option A "§15.6 row 1 only" scope. If a future arc reads §15.6 as conjunctive across 3 rows, AS-5 RETIRED may need re-examination — but the current contract authority (§15.6 row 1) is sufficient for span-attribute presence at the parent `tool.call` parent of `sandbox.violation`.

### §1.5 Sibling row impact

| Row | Status (post batch-22) | Status (post batch-23) | Reason |
|---|---|---|---|
| H_T-AS-1 | RETIRED | Unchanged | — |
| H_T-AS-2 | RETIRED | Unchanged | — |
| H_T-AS-4 | RETIRED | Unchanged | — |
| H_T-AS-5 | **STILL-BOUNDED** | **RETIRED** | **This batch — §15.6 row 1 attribute attachment at sandbox.violation** |
| H_T-AS-8 | PARTIAL | Unchanged | — |
| H_T-AS-9 | RETIRED (authoring) | Unchanged | — |

**AS-axis cumulative post-batch-23: 5 / 6 RETIRED (83.3%, +1 from batch-22) + 0 / 6 RETIRE-READY (bucket EMPTY) + 1 / 6 PARTIAL (16.7%, AS-8) + 0 / 6 STILL-BOUNDED (bucket EMPTY). Pipeline advanced (R+RR+P): 6/6 = 100% (+1 from batch-22 5/6=83.3%; AS-axis pipeline-advanced now COMPLETE).** AS-axis is one step away from full RETIRED (AS-8 PARTIAL gates on remaining `anthropic.*` attrs + cross-namespace consumer-side wiring).

---

## §2 Operator-opt-in RETIRE-READY pattern (post-batch-23)

Pattern members across batches 10–23: **7 historical members** (CP-16, CP-18, AS-2, CP-21, CP-22, AS-4, CP-19); **all 7 RETIRED**. **Operator-opt-in RETIRE-READY bucket REMAINS EMPTY post-batch-23** (no new entrants at batch-23 — H_T-AS-5 is a direct STILL-BOUNDED → RETIRED transit, not a RETIRE-READY transit).

**Pattern sub-species 7.operator-explicit-deferred-close-gate SECOND CLOSURE-equivalent.** Batch-22 §2 catalogued the sub-species at CP-19's close. Batch-23 generalizes: H_T-AS-5's close shape (gate-text structurally stale against production architecture; advisor reframe; operator ratify; same-session close) IS the same sub-species 7 shape — except H_T-AS-5 never entered RETIRE-READY tier explicitly. The gate-text in batch-19 cited a literal Python-helper invocation requirement; the contract authority (AS spec §15.6 row 1) actually requires only a span-attribute presence assertion. Same lineage as batch-22 — gate-text-stale-vs-production sub-species — but at STILL-BOUNDED rather than RETIRE-READY tier.

**Sub-species set at species 3 (resolved-but-carry-stale-inherited) remains at 9 per workflow v1.10 §7.4.7.2 sub-species column** — no new species 3 entrant at this batch (the closure-event-class is **sub-species 7.gate-text-stale-vs-production-architecture** which generalizes batch-22's sub-species 7 to STILL-BOUNDED tier). Future workflow-doc revision MAY refine sub-species 7 into 2 sub-sub-species: 7a operator-explicit-deferred-close-gate (CP-19 batch-22 shape) + 7b gate-text-stale-vs-production-architecture (AS-5 batch-23 shape).

---

## §3 Adjacent observations

(a) **`_compose_idempotency_key` formula vs AS spec line 1093 drift NOT closed at this batch.** Dispatcher uses `sha256(parent_idempotency_key || step_id || tool_id)` per runtime spec §14.9.7 suggested recipe. AS spec line 1093 cites `sha256(conversation_id || step_index || tool || canonical_args)` per Cluster 4 §2.2.7. The two formulas are at different anchor levels (runtime-spec suggested recipe vs AS-spec Cluster 4 informational reference); neither is C-AS-15 §15.6 contract authority for the composition formula. Class 3 informational drift candidate; NOT patched per FM-2 single-focus-arc scope. Future arc may reconcile.

(b) **AS spec §15.6 row 2 sub-agent boundary inheritance NOT in scope at this batch.** `sub_agent_dispatch.py` propagates `idempotency_key` directly (lines 302/334/476/483) without invoking `derive_sub_agent_idempotency_key`. Same architectural pattern as the main dispatcher — production has its own propagation; harness-as helper is unused. AskUserQuestion 2026-05-28 Option A scoped to §15.6 row 1 only. If a future read of §15.6 is conjunctive across all 3 rows, AS-5 RETIRED may need re-examination. NOT patched per FM-2.

(c) **AS spec §15.6 row 3 cost-attribution joining NOT in scope at this batch.** `sandbox.cost.tier_overhead_*` attributes join on `idempotency_key` at D6 cost-attribution-per-span dashboarding. Production already emits `sandbox.cost.tier_overhead_ms` at `sandbox.enter` span (line 393); production does NOT emit `idempotency_key` on `sandbox.enter` (only on `sandbox.violation` at this batch). If D6 cost-attribution reads from `sandbox.enter` rather than `sandbox.violation`, row 3 join contract may be only partially satisfied. NOT patched per FM-2 — AskUserQuestion scoped to row 1 only.

(d) **Workspace CLAUDE.md §2.3 AS spec v1.7 row carries a v1.6-vs-v1.7 amendment history note unchanged at this batch** (the v1.7 alias-term abstraction at GenAI span-name format Class 1 fork R3 follow-on is invariant of AS-5 close). Workspace row needs only the AS plan + retirement-state-machine pointer refresh.

(e) **Adversarial review not run.** This batch lands the close in single-session arc with the empirical-verification surface at +1 new test + 4 extended tests + 1087 pre-existing tests preserved green. Adversarial review pass deferred to operator-discretion follow-on arc.

(f) **Memory anchor write owed.** New entry `[[as-5-sandbox-violation-idempotency-key-attribute-attachment]]` companion entry for the batch-23 close shape; sub-species 7 split candidate (7a vs 7b) for future workflow-doc revision. Blocked at MEMORY.md size limit (per batch-22 §3(e) precedent).

(g) **Pattern catalogued — gate-text-stale-vs-production-architecture STILL-BOUNDED close.** Batch-23 generalizes batch-22's sub-species 7 shape from RETIRE-READY to STILL-BOUNDED tier. Future operator-deferred gate-text entries at any tier (STILL-BOUNDED / PARTIAL / RETIRE-READY) should include same-session advisor reframe check before committing to a multi-arc deferral path. Empirically validated at 2 consecutive batches now (batch-22 CP-19 + batch-23 AS-5).

(h) **harness-as helper unused-but-import-able state preserved at batch-23.** The 3 helpers at `sandbox_event_idempotency.py` remain import-able and untested-at-invocation-layer post-batch-23. Future arc MAY either (i) remove the helpers as authoring-only-substitution-retirement; or (ii) wire them at a sub-agent dispatch composer if §15.6 row 2 is read conjunctively. Bounded residual; NOT a defect — the contract satisfaction is at the OTel-span layer, not the Pydantic-event layer.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Batch | 23 |
| Cumulative RETIRED | 30/49 (61.2%) |
| Cumulative RETIRE-READY | 0/49 (bucket EMPTY) |
| Cumulative PARTIAL | 6/49 (12.2%) |
| Cumulative STILL-BOUNDED | 13/49 (26.5%) |
| Cumulative pipeline-advanced | 36/49 (73.5%) |
| New RETIRED transitions | 1 (H_T-AS-5 STILL-BOUNDED → RETIRED direct transit) |
| New RETIRE-READY transitions | 0 |
| Filed as | `phase-7d-retirement-events-batch-23.md` |
| Co-published bookkeeping | workspace `CLAUDE.md` §2.3 AS spec row + §2.4 AS plan row retirement-status notes |
| Predecessor | `phase-7d-retirement-events-batch-22.md` |
| Date | 2026-05-28 |
