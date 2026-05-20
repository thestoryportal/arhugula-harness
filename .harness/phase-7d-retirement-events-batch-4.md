# Phase 7 sub-phase 7d — substitution retirement events, batch 4 (2 RETIRED + 1 PARTIAL)

**Filed:** 2026-05-20, Phase 7 sub-phase 7d, U-RT-59 landing arc.
**Skill:** `phase-7-substitution-retirement` §8.1 (workspace progress ledger).
**Authority:** U-RT-59 landing (sub-agent dispatch composer + StepKindDispatcherRegistry + ChildWorkflowRunner per `Spec_Harness_Runtime_v1.md` v1.6 §14.7 C-RT-17 + `Implementation_Plan_Harness_Runtime_v2_5.md` L9-ter ACs all green or halt-route-split per operator-ratified fork resolutions).

---

## §0 Batch context

**3 substitutions transition** in this batch (post U-RT-59 landing):

- **H_T-CP-10** (§1): TopologyPattern 6-class enum + admissibility predicate — STILL-BOUNDED → **RETIRED** at production execution path (composer step 4).
- **H_T-CP-13** (§2): HandoffContext + SubAgentBrief + StateSummary + LedgerEntryRef typed schemas — STILL-BOUNDED → **RETIRED** at production composer dispatch (composer steps 2-3).
- **H_T-CP-14** (§3): multi-agent span hierarchy + `topology.*` + `subagent.*` namespaces — STILL-BOUNDED → **PARTIAL** at production span hierarchy (single-sub-agent slice; fan-out arc deferred — strict X-AL-2 reading).

**Condition A** (cited unit IDs landed):
- CP-10: U-CP-22 (TopologyPattern enum + admissibility) + U-RT-40 (topology dispatcher materialization) landed at 7b; U-RT-59 landed this arc.
- CP-13: U-CP-28 (HandoffContext schema) + U-CP-29 (SubAgentBrief) + U-CP-30 (StateSummary + LedgerEntryRef + RetryHistory) + U-RT-26 (handoff registry materialization) landed at 7b; U-RT-59 landed this arc.
- CP-14: U-CP-31 (multi-agent span hierarchy declaration) + U-CP-32 (`subagent.*` + `topology.*` namespace carriers) landed at 7b; U-RT-59 landed this arc.

**Condition B** (H_E surface no longer invoked at substitution site): evaluated per substitution against H_T runtime at U-RT-59 landing head. The sub-agent dispatch composer at `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:RuntimeSubAgentDispatcher` is the production sub-agent dispatch site previously absent (the substitution-site B-condition blocker for all three primitives per Meta-Architecture §5.4); its presence discharges criterion B for CP-10 + CP-13 in full and for CP-14 in the bounded single-sub-agent slice.

Cumulative retirement count: **19 / 49 (post batch 3)** + **2 / 49 (this batch RETIRED — CP-10 + CP-13)** = **21 / 49 (42.9%)**.

PARTIAL count: 1 (AS-8) → 2 (AS-8 + CP-14 single-sub-agent slice). CP-14 PARTIAL transitions to RETIRED at the future fan-out-arc landing (parent topology expansion beyond SINGLE_THREADED_LINEAR).

§9 Class 2 multi-LLM commitment surface: **CLOSED** (U-RT-52 close, preserved through this batch).

---

## §1 H_T-CP-10 — TopologyPattern dispatcher + admissibility predicate

| Field | Content |
|---|---|
| Substitution ID | H_T-CP-10 |
| Primitive | TopologyPattern 6-class enum (`single-threaded-linear / orchestrator-workers / decentralized-handoff / hierarchical-delegation / evaluator-optimizer / parallelization`) + `is_admissible` cross-pattern admissibility predicate (per C-CP-10 §10.1 + §10.3) |
| Spec contract | C-CP-10 + C-RT-17 §14.7.2 step 4 |
| Retirement event timestamp | Phase 7 sub-phase 7d U-RT-59 landing arc, 2026-05-20 |
| Condition A verification | Cited carriers U-CP-22 (TopologyPattern enum + `is_admissible` predicate) + U-RT-40 (RuntimeTopologyDispatcher materialization at stage 5) landed at 7b. New runtime composer U-RT-59 landed this arc; production composer invokes `ctx.topology_dispatcher.dispatch(...)` + `is_admissible(...)` at every sub-agent dispatch step per §14.7.2 step 4 |
| Condition B verification | `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:RuntimeSubAgentDispatcher.dispatch` (composer body steps 3-4) calls `topology = self.topology_dispatcher.dispatch(payload.child_manifest_entry)` → returns `TopologyPattern` per C-CP-10 §10.1 → calls `self.topology_dispatcher.is_admissible(topology, payload.child_manifest_entry.workload_class)` → enforces gate (raises typed `SubAgentDispatchTopologyInadmissibleError` mapping to `RT-FAIL-SUB-AGENT-TOPOLOGY-INADMISSIBLE` on False). Substitution mechanism (`CLAUDE.md`-prose annotation: "you are working as orchestrator-workers" convention) no longer reachable from runtime composer — runtime owns the dispatch + admissibility predicate at production execution path. Test coverage: `test_lifecycle_sub_agent_dispatch.py::test_topology_inadmissible_raises_typed_error_pre_span` |
| Cross-axis dependency cascade | None (CP-10 retirement does not gate other primitives per Meta-Architecture §6.3) |
| Evidence anchor | `sub_agent_dispatch.py` composer steps 3-4 (topology dispatch + admissibility gate) + 19-test suite at `test_lifecycle_sub_agent_dispatch.py` (all green; ACs #5 + #6 verify dispatch + admissibility surfaces) |

---

## §2 H_T-CP-13 — HandoffContext + SubAgentBrief + StateSummary + LedgerEntryRef typed schemas

| Field | Content |
|---|---|
| Substitution ID | H_T-CP-13 |
| Primitive | HandoffContext 7-field payload + SubAgentBrief 5-field + StateSummary 5-field + LedgerEntryRef 3-field + RetryHistory typed schemas at production sub-agent dispatch (per C-CP-13 §13.1-§13.5) |
| Spec contract | C-CP-13 + C-RT-17 §14.7.2 steps 2-3 + §14.7.3 + §14.7.6 |
| Retirement event timestamp | Phase 7 sub-phase 7d U-RT-59 landing arc, 2026-05-20 |
| Condition A verification | Cited carriers U-CP-28 (HandoffContext schema) + U-CP-29 (SubAgentBrief) + U-CP-30 (StateSummary + LedgerEntryRef + RetryHistory) + U-RT-26 (RuntimeHandoffRegistry materialization at stage 3b) landed at 7b. New runtime composer U-RT-59 landed this arc; production composer composes the 7-field HandoffContext at every sub-agent dispatch step per §14.7.2 step 2 + §14.7.3 v1.6 MVP composition table |
| Condition B verification | `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:_compose_handoff_context` composes `HandoffContext` from `step_context: StepExecutionContext` + `SubAgentDispatchPayload` per the §14.7.3 v1.6 MVP table — Pydantic v2 validation at construction (`extra="forbid"`, `frozen=True`) enforces the typed schema at production callsite. `ctx.handoff_registry.dispatch(...)` invoked at composer step 3 with full type discipline (parent_action_id / parent_gate_level / parent_sandbox_tier / sub_agent_brief / operator_override). Audit composition via `ctx.handoff_registry.compose_dispatch_audit(...)` at composer step 8 produces `CPAuditLedgerEntry` per C-CP-13 §13.5 dispatch-response-hash join key. Substitution mechanism (`Agent` free-text prompt + tool list — typed-schema-by-convention only) no longer reachable from runtime composer — runtime owns typed schema composition at production execution path. Test coverage: `test_lifecycle_sub_agent_dispatch.py` ACs #4 + #5 verify HandoffContext composition + descent computation |
| Cross-axis dependency cascade | None (CP-13 retirement does not gate other primitives per Meta-Architecture §6.3) |
| Class 1 fork carry-forward | AC #9 write half (`ctx.audit_writer.append(tenant_id, audit_entry)`) is STRUCK at v1.6 MVP per the Class 1 fork on CP→OD audit-write composition (joins `[[fork-cp-is-wiring-gaps]]`). Compose half (CPAuditLedgerEntry production) lands here and satisfies condition B for the schema retirement. End-to-end audit-write composition is owed to a follow-on Phase 6 CP-composer-authoring arc; downstream retirement event will close that surface. See `.harness/class_1_tension_u_rt_59_cp_to_od_audit_write_gap.md` |
| Evidence anchor | `sub_agent_dispatch.py` composer steps 2-3 + 8 (HandoffContext composition + descent + audit composition) + 19-test suite at `test_lifecycle_sub_agent_dispatch.py` ACs #4 + #5 + #9 partial |

---

## §3 H_T-CP-14 — Multi-agent span hierarchy + `subagent.*` + `topology.*` namespaces (PARTIAL)

| Field | Content |
|---|---|
| Substitution ID | H_T-CP-14 |
| Primitive | Multi-agent span hierarchy (parent step → `subagent.span` → child workflow spans) + `subagent.*` 7-attribute namespace + `topology.*` 10-attribute namespace emitted at production span hierarchy (per C-CP-14 §14.1 + §14.2) |
| Spec contract | C-CP-14 + C-RT-17 §14.7.2 step 5 + §14.7.5 |
| Retirement event timestamp | Phase 7 sub-phase 7d U-RT-59 landing arc, 2026-05-20 |
| Prior status | STILL-BOUNDED |
| New status | **PARTIAL** (single-sub-agent slice; fan-out arc deferred — strict X-AL-2 reading per spec §14.7 "PARTIAL retirement is non-retirement") |
| Condition A verification | Cited carriers U-CP-31 (multi-agent span hierarchy declaration) + U-CP-32 (`subagent.*` + `topology.*` namespace carriers at `harness_cp.topology_subagent_namespace`) landed at 7b. New runtime composer U-RT-59 landed this arc; production composer opens `subagent.span` + sets the 7 `subagent.*` attributes + narrow-subset 2 `topology.*` attributes per §14.7.2 step 5 + §14.7.5 narrow-scope subset shape |
| Condition B (PARTIAL) verification | `sub_agent_dispatch.py` composer step 5 opens `subagent.span` via `tracer.start_as_current_span("subagent.span")`; sets `subagent.span.id` (16-hex) + `subagent.parent_span_id` (16-hex) + `subagent.result_status` (close-time) + `subagent.request_blocked_by_budget` + `subagent.tokens_in` / `subagent.tokens_out` / `subagent.cached_tokens_in` (all 7 verbatim per `SUBAGENT_NAMESPACE_SCHEMA` carrier) + `topology.pattern` + `topology.workload_class` (narrow-subset 2 per `TOPOLOGY_NAMESPACE_SCHEMA` carrier). Attribute names imported from the canonical CP-side carrier (`harness_cp.topology_subagent_namespace.SUBAGENT_NAMESPACE_SCHEMA` + `TOPOLOGY_NAMESPACE_SCHEMA`) — no hand-coded attribute strings per §14.7.5 producer-side carrier reference. Substitution mechanism (`CLAUDE.md`-prose "emit subagent.* attributes as below" convention) no longer reachable from runtime composer at the single-sub-agent slice |
| Bounded scope (NOT yet RETIRED) | The 8 fan-out-specific `topology.*` attributes (`fan_out_cap`, `cascade_policy`, `results_collected`, `results_failed`, `cascade_applied`, `synthesis_token_budget`, `cascade_decision_audit_ledger_id`, `concurrent_token_budget_at_dispatch`) are NOT emitted at v1.6 (out of scope — single-sub-agent within linear parent per spec §14.7 change-note). The composer explicitly does not emit these per §14.7 invariant "v1.6 MVP fan-out emission is foreclosed". Test verification: `test_lifecycle_sub_agent_dispatch.py::test_subagent_span_does_not_carry_8_fanout_topology_attributes`. PARTIAL → RETIRED transition gates on the post-v1.6 fan-out-arc landing (parent topology expansion beyond SINGLE_THREADED_LINEAR) which will wrap the existing `subagent.span` emission inside the fan-out envelope without rewriting per-sibling emission per §14.7.5 narrative |
| Operator ratification anchor | Operator may re-ratify PARTIAL → RETIRED at retirement audit if the bounded-scope deferral is acceptable as a documented follow-on arc. Strict X-AL-2 reading at this batch: PARTIAL stands until fan-out arc lands per spec §14.7 "PARTIAL retirement is non-retirement". At this filing: PARTIAL marked (operator may re-ratify to RETIRED) |
| Cross-axis dependency cascade | None (CP-14 PARTIAL does not gate other primitives at this slice) |
| Evidence anchor | `sub_agent_dispatch.py` composer step 5 (span open + attribute emission) + 19-test suite at `test_lifecycle_sub_agent_dispatch.py` ACs #6 (4 sub-tests: exactly-one span + 7 subagent.* + 2 narrow topology.* + 0 fan-out topology.*) + carrier-source verification (`test_attribute_names_come_from_canonical_carrier`) |

---

## §4 Cumulative retirement ledger (post batch 4)

Per `.harness/phase-7d-retirement-ledger-v2.md` §5 (workspace progress ledger):

| Status | Count | Substitutions |
|---|---|---|
| RETIRED (post batch 4) | 21 / 49 | (15 from batches 1-2) + CP-3 / CP-4 / CP-5 / CXA-5 (batch 3) + **CP-10 / CP-13 (batch 4 — this filing)** |
| PARTIAL (post batch 4) | 2 / 49 | AS-8 (batch 2) + **CP-14 single-sub-agent slice (batch 4 — this filing; gates on fan-out arc)** |
| STILL-BOUNDED (post batch 4) | 10 / 49 | CP axis: CP-12 / CP-16 / CP-17 / CP-18 / CP-19 / CP-20 / CP-21 / CP-22 / CP-23 (per `harness-cp/CLAUDE.md` §4.1 enumeration; STILL-BOUNDED on absent HITL / validator / tool-invocation / memory / files / mcp composers). Plus other-axis STILL-BOUNDED per per-axis CLAUDE.md inventories |

CP-axis post-batch-4: **9 / 22 retired (40.9%, including CP-24 authoring-retired)**. 2 PARTIAL (CP-11 + CP-14) + 11 STILL-BOUNDED. Remaining STILL-BOUNDED retirements gate on HITL / validator / tool-invocation / memory / files / mcp composers landing (next arcs).

---

## §5 Cross-axis cascade impact

§6.3.2 F-CP-01 Stage 3b inversion cascade: **FULLY DISCHARGED at batch 3** (preserved at this batch). No new inversion-seam activations from this batch.

CP→IS audit-write composition (the Class 1 fork on AC #9 write half — `[[fork-cp-is-wiring-gaps]]` family): NOT discharged at this batch. The CPAuditLedgerEntry compose half lands at U-RT-59; the OD-side write composition is owed to a follow-on Phase 6 CP-composer-authoring arc. Future retirement event will close that surface end-to-end.

§14.7.7 INFERENCE_STEP routing-registry binding (the Class 1 fork on async/sync dispatcher mismatch — see `.harness/class_1_tension_u_rt_59_async_sync_step_dispatcher.md`): NOT discharged at this batch. Plan AC #11 INFERENCE_STEP clause STRUCK; registry binds only SUB_AGENT_DISPATCH at v1.6 MVP. Resolution (sync facade vs async driver vs Protocol revision) is owed to a follow-on arc.

---

*Batch 4 retirement event records filed per X-AL-2 condition A ∧ condition B at U-RT-59 landing. 2 RETIRED + 1 PARTIAL (operator may re-ratify CP-14 → RETIRED at retirement audit). Cumulative 21/49 (42.9%).*
