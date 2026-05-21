# Phase 7 sub-phase 7d — substitution retirement events, batch 6 (U-RT-59 Fork 2 implementation-arc post-audit)

**Filed:** 2026-05-20, Phase 7 sub-phase 7d, U-RT-59 Fork 2 implementation-arc post-audit pass.
**Skill:** `phase-7-substitution-retirement` §3 (X-AL-2 audit) + §8.1 (workspace progress ledger).
**Authority:** U-RT-59 Fork 2 CP→OD audit-write Class 1 fork **RESOLVED** at implementation-arc landing `5407c0d` (4-substep audit composition: `compose_dispatch_audit` → `ledger_writer.append` → `cp_audit_to_od_audit` → `audit_writer.append` end-to-end at production sub-agent dispatch composer per `Spec_Harness_Runtime_v1.md` v1.7 §14.7.2 step 8 + CP spec v1.7/v1.8 §13.5.1 converter contract + OD spec v1.5 C-OD-24 audit-ledger payload + entry composition + ADR-D5 v1.4 §1.4 storage-form reconciliation + CXA v2.4 §2.3.7 CP→OD typed seam). AC #9 un-struck at atomic-decomp v2.6. Predecessor batches: 1-5 (closed; forward-only ledger discipline preserved).

---

## §0 Batch context

**Status type: criterion-B strengthening + Class 1 fork closure-pointer (NO new RETIRED transitions in this batch).**

Batch 4 (2026-05-20, pre-arc) filed H_T-CP-10 + H_T-CP-13 RETIRED with documented carry-forwards:

- **CP-10 §1 carry-forward** — strict-gate retirement criterion narrowed to "dispatcher operational + predicate callable advisorially" per `[[class_1_tension_u_rt_59_topology_admissibility_predicate]]`. Pointer-closed at batch 5 §2 to commit `e52c2da` (strict gate restored via `is_topology_permitted(topology, workload)` union predicate; composer step 4 raises `SubAgentDispatchTopologyInadmissibleError` before `subagent.span` opens).
- **CP-13 §2 carry-forward** — AC #9 write half (`ctx.audit_writer.append(tenant_id, audit_entry)`) STRUCK at v1.6 MVP per `[[class_1_tension_u_rt_59_cp_to_od_audit_write_gap]]`. Compose half (`CPAuditLedgerEntry` production) landed at U-RT-59; end-to-end audit-write composition was owed to a follow-on arc.

The U-RT-59 Fork 2 implementation arc (this session, commit `5407c0d`) lands the missing end-to-end composition. AC #9 un-struck at atomic-decomp v2.6. CP-13 criterion B strengthens from "compose-only at production callsite" to "compose + F2-write + CP→OD convert + IS-anchored audit-write end-to-end at production callsite." The Class 1 fork referenced at batch 4 §2 is RESOLVED.

CP-14 PARTIAL is unchanged at this audit — the Fork 2 arc addresses audit composition, not fan-out emission. The 8 fan-out-specific `topology.*` attributes remain unemitted at v1.6 MVP per spec §14.7 invariant; PARTIAL → RETIRED transition still gates on the post-v1.6 fan-out-arc landing.

**Substitutions affected (re-audited; NO status change):**

| Substitution | Prior retirement | Batch 6 effect |
|---|---|---|
| H_T-CP-10 (TopologyPattern dispatcher + admissibility predicate) | RETIRED batch 4 §1; advisory-gate-narrowing pointer-closed at batch 5 §2 to `e52c2da` | NO change. Already pointer-closed at batch 5 §2; preserved at this batch |
| H_T-CP-13 (HandoffContext + SubAgentBrief + StateSummary + LedgerEntryRef typed schemas) | RETIRED batch 4 §2; AC #9 write-half STRUCK + Class 1 fork carry-forward | Criterion B strengthened from "compose-only" to "compose + write end-to-end at production callsite." Class 1 fork `[[class_1_tension_u_rt_59_cp_to_od_audit_write_gap]]` flips OPEN-PARTIAL → RESOLVED at fork file's filing-footer update (companion commit, this arc) |
| H_T-CP-14 (multi-agent span hierarchy + `subagent.*` + `topology.*` namespaces) | PARTIAL batch 4 §3 (single-sub-agent slice; fan-out arc deferred) | NO change. Fork 2 arc addresses step 8 audit composition, not fan-out emission. PARTIAL → RETIRED transition continues to gate on post-v1.6 fan-out-arc landing |

Cumulative retirement count: **21 / 49 (42.9%)** — unchanged from batch 5 cumulative.

---

## §1 H_T-CP-13 — sub-agent dispatch audit composition end-to-end execution-path completion

| Field | Content |
|---|---|
| Substitution ID (re-audited) | H_T-CP-13 |
| Primitive | HandoffContext 7-field payload + SubAgentBrief 5-field + StateSummary 5-field + LedgerEntryRef 3-field + RetryHistory typed schemas + **dispatch audit ledger entry composition** at production sub-agent dispatch (per C-CP-13 §13.1–§13.5 + §13.5.1 converter contract) |
| Spec contract | C-CP-13 + C-RT-17 §14.7.2 step 8 (4-substep audit composition) + §14.7.6 (audit ledger reference) + CP spec v1.7 §13.5.1 (`cp_audit_to_od_audit` converter) + OD spec v1.5 C-OD-24 (`AuditLedgerEntry` payload + entry composition + `compute_entry_hash` canonical helper) |
| Re-audit event timestamp | Phase 7 sub-phase 7d U-RT-59 Fork 2 implementation-arc post-audit, 2026-05-20 |
| Implementation-arc landing commit | `5407c0d` (Fork 2 implementation arc — 14 files changed, +918/-269; 8 spec/plan/CLAUDE.md absorption + composer wiring + converter move + 2 ledger hygiene deltas) |
| Pre-arc posture (batch 4 §2) | Compose half landed: `handoff_registry.compose_dispatch_audit(...)` produced `CPAuditLedgerEntry` at composer step 8 with full Pydantic v2 type discipline. **Write half STRUCK at AC #9** per Class 1 fork on CP→OD shape mismatch (CP-shape `CPAuditLedgerEntry` ≠ OD-shape `AuditLedgerEntry`; converter contract owed to a follow-on Phase 6 CP-composer-authoring arc). End-to-end audit-write composition was owed |
| Post-arc posture (v1.7) | `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:_compose_and_persist_audit` materializes the 4-substep sequence: (8a) `handoff_registry.compose_dispatch_audit(...)` → `CPAuditLedgerEntry`; (8b) `ledger_writer.append(f2_payload, f2_key)` → F2 dispatch-action entry with action_id `dispatch:<parent_action_id>:<child_index>` (action_id IS the `StateLedgerEntryRef` per OD spec v1.5 C-OD-24.4 opaque-str discipline); (8c) `cp_audit_to_od_audit(cp_entry, key_id=..., algo=..., entry_core=entry_core)` → signed `AuditLedgerEntry` (converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` — production seam home per Q5); (8d) `audit_writer.append(tenant_id=step_context.tenant_id, audit_entry=od_entry)` → IS-anchored audit-ledger persistence per C-RT-04. Failure semantics: SUCCESS/DRAINED paths raise `SubAgentDispatchAuditComposeError` → driver maps to `RT-FAIL-SUB-AGENT-AUDIT-COMPOSE` fail class (runtime spec v1.7 §14); FAILED/exception-bubble paths swallow 8b/8c/8d failures so primary fault is preserved (`raise_on_failure: bool` flag) |
| Condition A verification (re-audit) | Cited carriers U-CP-28 (HandoffContext schema) + U-CP-29 (SubAgentBrief) + U-CP-30 (StateSummary + LedgerEntryRef + RetryHistory) + U-RT-26 (RuntimeHandoffRegistry materialization at stage 3b) preserved from batch 4. U-CP-28 plan body extended at v2.14 with `Implements:` citation for C-CP-13 §13.5.1 converter contract; U-OD-00 plan body extended at v2.12 with `Implements:` citation for C-OD-24 audit-ledger payload + entry composition. New CP→OD CXA edge filed at CXA v2.4 §2.3.7 (first cross-axis back-edge in project history) |
| Condition B verification (re-audit, strengthened) | The "H_E surface no longer invoked at substitution site" condition was met at batch 4 §2 against compose-only production callsite (with AC #9 write half STRUCK as documented carry-forward). At this batch, criterion B strengthens to **compose + write end-to-end at production callsite**: 8b F2-write + 8c CP→OD convert + 8d IS-anchored audit-write all invoked at SUCCESS / DRAINED paths from the runtime composer with no `Bash(python -c)` / `Bash(jq)` / CLAUDE.md-prose substitution surface reachable. The Class 1 fork carry-forward documented at batch 4 §2 ("end-to-end audit-write composition owed to a follow-on Phase 6 CP-composer-authoring arc; downstream retirement event will close that surface") is **discharged at this filing** |
| Class 1 fork closure-pointer | `.harness/class_1_tension_u_rt_59_cp_to_od_audit_write_gap.md` flips OPEN-PARTIAL → RESOLVED at fork file's filing-footer update (companion commit `5407c0d`, this arc). Full Fork 2 arc closed across 9 commits (8 spec commits 2b56629 etc. + 1 implementation commit `5407c0d`) — see fork file §12 closure record |
| Cross-axis dependency cascade | New CP→OD typed seam at CXA v2.4 §2.3.7 (class G Pattern P1) — first cross-axis back-edge in project history; per-unit acyclicity preserved (pre-v2.4 IS<AS<CP<OD axis partial-order no longer total at axis granularity; see `[[class_3_tension_cxa_v2_4_axis_back_edge]]`). Discharge does not gate any unretired substitution at this slice |
| Evidence anchor | `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:415-509` (`_compose_and_persist_audit` 4-substep helper) + composer body invocations at lines 640, 673, 706 (SUCCESS / DRAINED / FAILED paths); converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py:cp_audit_to_od_audit`; 2283 workspace tests green (+5 net step-8 tests + integration test; -2 stale v1.6 partial-landing tests) |

---

## §2 H_T-CP-10 advisory-gate carry-forward — pointer-close preservation (NO change)

| Field | Content |
|---|---|
| Substitution ID | H_T-CP-10 |
| Prior retirement | RETIRED batch 4 §1; advisory-gate narrowing pointer-closed at batch 5 §2 to commit `e52c2da` |
| Batch 6 effect | NO change. CP-10 strict-gate retirement criterion was already pointer-closed at batch 5 §2 (strict gate restored via `is_topology_permitted(topology, workload)` union predicate at `sub_agent_dispatch.py:585`; composer step 4 raises `SubAgentDispatchTopologyInadmissibleError` before `subagent.span` opens for inadmissible workload/topology pairs). The Fork 2 implementation arc preserves the strict gate — Fork 2 addresses step 8 audit composition, not step 4 admissibility |
| Preserved evidence | `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:585` (`if not self.topology_dispatcher.is_topology_permitted(topology, workload): raise ...`); 3 strict-gate tests at `test_lifecycle_sub_agent_dispatch.py` (replaces the v1.6 advisory-gate test); spec §14.7.2 step 4 predicate-name correction (`is_admissible` → `is_topology_permitted`) owed at Class 3 drift item 8 |

---

## §3 H_T-CP-14 PARTIAL preservation (NO change)

| Field | Content |
|---|---|
| Substitution ID | H_T-CP-14 |
| Prior status | PARTIAL batch 4 §3 (single-sub-agent slice; fan-out arc deferred — strict X-AL-2 reading per spec §14.7 "PARTIAL retirement is non-retirement") |
| Batch 6 effect | NO change. The Fork 2 implementation arc addresses C-RT-17 §14.7.2 step 8 audit composition (4-substep sequence), not §14.7.5 fan-out span emission. The 8 fan-out-specific `topology.*` attributes (`fan_out_cap`, `cascade_policy`, `results_collected`, `results_failed`, `cascade_applied`, `synthesis_token_budget`, `cascade_decision_audit_ledger_id`, `concurrent_token_budget_at_dispatch`) remain unemitted at v1.6/v1.7 MVP per spec §14.7 invariant; the composer continues to NOT emit these (verified at `test_subagent_span_does_not_carry_8_fanout_topology_attributes`). PARTIAL → RETIRED transition continues to gate on the post-v1.7 fan-out-arc landing (parent topology expansion beyond `SINGLE_THREADED_LINEAR`) |
| Re-evaluation trigger | When fan-out arc lands (parent topology expansion beyond `SINGLE_THREADED_LINEAR`); the existing `subagent.span` emission will wrap inside the fan-out envelope without rewriting per-sibling emission per spec §14.7.5 narrative |
| Cross-axis dependency cascade | None at this audit (CP-14 PARTIAL does not gate other primitives at the single-sub-agent slice) |

---

## §4 Cumulative retirement ledger (post batch 6)

Per `.harness/phase-7d-retirement-ledger-v2.md` §5 (workspace progress ledger):

| Status | Count | Substitutions |
|---|---|---|
| RETIRED (post batch 6) | 21 / 49 (unchanged) | (15 from batches 1-2) + CP-3 / CP-4 / CP-5 / CXA-5 (batch 3) + CP-10 / CP-13 (batch 4 — CP-13 criterion B strengthened this batch) |
| PARTIAL (post batch 6) | 2 / 49 (unchanged) | AS-8 (batch 2) + CP-14 single-sub-agent slice (batch 4; gates on fan-out arc) |
| STILL-BOUNDED (post batch 6) | 10 / 49 (unchanged) | Per `harness-cp/CLAUDE.md` §4.1 + per-axis CLAUDE.md inventories |

CP-axis post-batch-6: **9 / 22 retired (40.9%, unchanged)**. Cumulative 21/49 (42.9%, unchanged).

**Quality delta this batch:** CP-13 criterion B evidence strength upgraded from "compose-only at production callsite (write half STRUCK)" to "compose + F2-write + CP→OD convert + IS-anchored audit-write end-to-end at production callsite (AC #9 un-struck)." The previously documented Class 1 fork carry-forward at batch 4 §2 is discharged at this filing.

---

## §5 Cross-axis cascade impact

§6.3.1 H_T-CP-1 → H_T-AS-8 anthropic.* namespace emission: **DORMANT** (preserved at this batch — CP-1 still STILL-BOUNDED per ledger v2 §8.1; multi-LLM call site absent).

§6.3.2 F-CP-01 Stage 3b inversion cascade: **FULLY DISCHARGED at batch 3** (preserved at this batch).

§14.7.7 INFERENCE_STEP routing-registry binding Class 1 fork (`[[class_1_tension_u_rt_59_async_sync_step_dispatcher]]`): **RESOLVED at batch 5** (preserved at this batch — wiring landing `d64d8cf`).

§14.7.2 step 4 strict-admissibility Class 1 fork (`[[class_1_tension_u_rt_59_topology_admissibility_predicate]]`): **RESOLVED at `e52c2da`** (pointer-closed at batch 5 §2; preserved at this batch).

**§14.7.2 step 8 audit-composition Class 1 fork (`[[class_1_tension_u_rt_59_cp_to_od_audit_write_gap]]`): RESOLVED at this batch** — implementation-arc landing commit `5407c0d`. Fork file's status flips OPEN-PARTIAL → RESOLVED at filing-footer update (companion commit `5407c0d`, this arc). All 3 U-RT-59 sibling Class 1 forks now RESOLVED (async/sync + topology admissibility + CP→OD audit-write). No Class 1 forks remain OPEN at the U-RT-59 surface.

**New cross-axis structural posture:** First cross-axis axis back-edge in project history (CP→OD per CXA v2.4 §2.3.7). Pre-v2.4 IS<AS<CP<OD partial-order no longer total at axis granularity; per-unit acyclicity preserved. Class 3 drift carry-forward at `[[class_3_tension_cxa_v2_4_axis_back_edge]]` owed to per-axis-CLAUDE.md Form A deltas (`harness-cp/CLAUDE.md` §2.3 + `harness-od/CLAUDE.md` §2.2 + workspace `CLAUDE.md` §2.1.4).

---

## §6 Filing footer

| Field | Value |
|---|---|
| Filed by | U-RT-59 Fork 2 implementation-arc post-audit pass |
| Operator ratification | Operator-ratified Fork 2 implementation-arc landing 2026-05-20 (commit `5407c0d`); this audit re-confirms criterion A ∧ criterion B for CP-13 at strengthened end-to-end production callsite scope |
| Predecessor batch | `.harness/phase-7d-retirement-events-batch-5.md` (closed; LLM-dispatch end-to-end wiring re-affirmation) |
| Successor batch | TBD (CP-14 fan-out arc landing → PARTIAL → RETIRED transition; HITL / validator / tool-invocation / memory / files / mcp composer arcs → STILL-BOUNDED unblocks) |
| Test posture at filing | 2283 workspace tests green (+5 net step-8 tests + integration test; -2 stale v1.6 partial-landing tests); ruff clean; pre-existing 2 pyright errors at U-RT-58 wrapping site (lines 113-114 of stage_5_loop_init.py — `RetryBreakerFallbackDispatcher` Protocol mismatch) unchanged — not introduced by this arc |
| Class 3 drift items added | CXA v2.4 axis back-edge per-axis-CLAUDE.md Form A deltas (`[[class_3_tension_cxa_v2_4_axis_back_edge]]`); action_id-as-StateLedgerEntryRef prose drift (spec narrative cites "entry_hash"; `LedgerWriter.append` does not expose forward chain hash); §14.7.6 residual `audit_ledger_writer` field-name occurrences (4 of 5; step 8 site resolved at v1.7 step 8d rewrite); c11-operator-local SKILL.md missing (broken citation chain at ADR-D5 v1.4 row 1) |
| Forward-only ledger discipline | Preserved. Batches 1-5 untouched at this filing per batch 5 §2 precedent (forward-only; new pointer-closes + criterion-B strengthening recorded in new document referencing prior batches) |

---

*Batch 6 retirement re-audit events filed per X-AL-2 condition A ∧ condition B (strengthened) at U-RT-59 Fork 2 implementation-arc landing. NO new RETIRED transitions; cumulative 21/49 (42.9%) unchanged. Strengthens CP-13 criterion B from "compose-only" to "compose + write end-to-end at production callsite"; discharges the Class 1 fork carry-forward at batch 4 §2. Preserves CP-10 strict-gate pointer-close from batch 5 §2 and CP-14 PARTIAL fan-out-deferred status from batch 4 §3.*
