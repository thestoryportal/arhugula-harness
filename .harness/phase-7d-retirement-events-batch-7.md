# Phase 7d Retirement Events — Batch 7

| Field | Value |
|---|---|
| Batch number | 7 |
| Filed at | 2026-05-20 (post-batch-6 audit sweep — front (c) of post-U-RT-59 next-front menu) |
| Filed by | Phase 7d retirement audit sweep against post-batch-6 commits |
| Predecessor batch | `phase-7d-retirement-events-batch-6.md` (2026-05-20, post-U-RT-59-Fork-2 retirement audit; CP-13 criterion B strengthened end-to-end) |

---

## §0 Batch context

**Status type: contract-surface refinement event + criterion-B re-affirmation (NO new RETIRED transitions in this batch).**

Audit sweep covers 5 post-batch-6 commits (chronological):

1. `5cbdf97` — adversarial review of U-RT-59 Fork 2 spec arc bundle (0 Class 3 + 5 Class 2 + 3 Class 1 findings); no code change.
2. `47e1724` — path (i) NOTE-form absorption: runtime spec v1.8 + CP spec v1.9 + OD spec v1.6 + workspace CLAUDE.md; pure spec NOTE text, no code change.
3. `2543b92` — CXA v2.4 axis back-edge Class 3 absorption: workspace + per-axis CLAUDE.md Form A deltas; documentation only.
4. `1a90d1e` — **F2-04 follow-on arc closure**: `compute_entry_hash` materialized at `harness-od/src/harness_od/audit_ledger_types.py`; converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` refactored to import; OD spec v1.7 + plan v2.13 co-published; 4 new tests at `harness-od/tests/test_audit_ledger_types.py` (2287 workspace tests green, +4 net).
5. `da1bf74` — per-axis CLAUDE.md v2.1→v2.4 count-drift absorption: `harness-cp/CLAUDE.md` §1.1+§2.2+§2.3 citation precision; documentation only.

Of the 5 commits, only `1a90d1e` (F2-04 closure) touches production code. The other 4 are spec text + documentation absorption arcs (no behavioral change, no new H_T primitive landing).

**Conclusion (preview):** 0 new RETIRED transitions; cumulative 21/49 (42.9%) unchanged; F2-04 closure is a C-OD-24 contract-surface refinement event (NOT a substitution retirement); OD-2 retirement criterion B re-affirmed (structurally untouched by F2-04 surface).

---

## §1 F2-04 follow-on arc closure — contract-surface refinement event (NOT substitution retirement)

| Field | Value |
|---|---|
| Substitution ID (audited for impact) | None — F2-04 is a C-OD-24 §24.5 contract-surface event, not an H_T-OD-* substitution event |
| Event shape | OD spec v1.6 §24.5 NOTE "deferred to follow-on arc" → OD spec v1.7 §24.5 NOTE "RESOLVED at v1.7". Helper `compute_entry_hash` materialized at `harness-od/src/harness_od/audit_ledger_types.py`; production CP→OD converter at `harness-cxa/` refactored to import + delegate. Local `_compute_entry_hash` inline duplicate REMOVED. |
| Closes carry-forward | The only path-(i) drift-risk carry-forward filed at OD spec v1.6 + adversarial-review (F2-04 finding). |
| Why this is NOT a substitution retirement | The §24.5 `compute_entry_hash` helper is a C-OD-24 sub-surface — part of the OD-axis audit-ledger payload + entry composition contract — not a member of the 49-row H_T-OD-* substitution table at Meta-Architecture §5. C-OD-24 surfaces are spec-canonical contract obligations (typed shapes the OD axis package must materialize); H_T-OD-* substitutions are H_E surfaces bounded for not-yet-built H_T primitives. F2-04 retired an *inline-drift-risk* (recipe duplicated at converter callsite), not an H_E substitution. The relevant retirement-table entry would be H_T-OD-* — and none of the 8 OD substitutions trace to the §24.5 helper. |
| Substantive evidence | Spec v1.6 → v1.7 NOTE state-transition recorded at `design-substrate/Spec_Operational_Discipline_v1_7.md` change-note §17 + §24.5 RESOLVED body + filing-footer Successor row; plan v2.12 → v2.13 absorption at `design-substrate/Implementation_Plan_Operational_Discipline_v2_13.md` §0.1; byte-equivalence anchor at `harness-od/tests/test_audit_ledger_types.py::test_compute_entry_hash_byte_equivalent_to_canonical_recipe` crystallizes recipe with literal expected hex (`3567132e039dd0e6e47c9a3258ebddcdf56626ba5c0e06ef29256e6d25998490`). |
| Forward-only ledger discipline | F2-04 documented here for ledger completeness even though it is non-retirement. Future readers inspecting the 7d retirement timeline will see the OD spec v1.7 / plan v2.13 co-publication and may otherwise hunt for a substitution event — this §1 closes that hunt with an explicit-non-impact statement. |

---

## §2 H_T-OD-2 criterion-B re-affirmation (NO change)

| Substitution ID | H_T-OD-2 |
| Primitive | OTel SDK base + GenAI semconv 1.41.0 emission |
| Prior retirement | RETIRED 2026-05-20 (batch 2, U-RT-52 close arc); production callsite at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:RuntimeLLMDispatcher.dispatch`; criterion B re-affirmed at batch 5 §1 (strict X-AL-2 reading, driver-reachable by default). |
| Batch 7 surface | F2-04 closure (commit `1a90d1e`) touches `harness-od/src/harness_od/audit_ledger_types.py` (new `compute_entry_hash` helper) + `harness-cxa/src/harness_cxa/cp_audit_conversion.py` (refactor to import). Neither of these files is on OD-2's production callsite path (`harness-runtime/lifecycle/llm_dispatch.py` GenAI emission). The two surfaces are structurally unrelated — F2-04 = audit-ledger entry-hash recipe materialization; OD-2 = GenAI semantic-convention attribute emission at the LLM-dispatch span. |
| Verification anchor | `harness-runtime/tests/test_lifecycle_llm_dispatch.py` (13 tests covering Protocol satisfaction + per-provider GenAI emission + `anthropic.cache_*` 4-attr conditional + factory binding) — all passing at 2287-test workspace baseline. |
| Status post batch 7 | RETIRED (unchanged). Criterion B re-affirmed at strict X-AL-2 reading; F2-04 surface is non-overlapping. |

---

## §3 Cumulative retirement ledger (post batch 7)

Per `.harness/phase-7d-retirement-ledger-v2.md` §5 (workspace progress ledger) + batch 6 §4 (preserved):

| Status | Count | Substitutions |
|---|---|---|
| RETIRED (post batch 7) | 21 / 49 (unchanged) | (15 from batches 1-2) + CP-3 / CP-4 / CP-5 / CXA-5 (batch 3) + CP-10 / CP-13 (batch 4 — CP-13 criterion B strengthened at batch 6) |
| PARTIAL (post batch 7) | 2 / 49 (unchanged) | AS-8 (batch 2) + CP-14 single-sub-agent slice (batch 4; gates on fan-out arc) |
| STILL-BOUNDED (post batch 7) | 10 / 49 (unchanged) | Per `harness-cp/CLAUDE.md` §4.1 + per-axis CLAUDE.md inventories |

CP-axis post-batch-7: **9 / 22 retired (40.9%, unchanged)**. Cumulative 21/49 (42.9%, unchanged).

**Quality delta this batch:** Contract-surface refinement event (OD spec v1.7 §24.5 NOTE deferred → RESOLVED; helper materialized at OD axis package; converter refactored to import). No retirement-criterion change at any substitution. OD-2 criterion B explicitly re-affirmed at §2 above given the surface overlap question (F2-04 touches `harness-od/` but on a non-OD-2 path).

---

## §4 Cross-axis cascade impact

§6.3.1 H_T-CP-1 → H_T-AS-8 anthropic.* namespace emission: **DORMANT** (preserved at this batch — production callsite invocation gated on workflow override / future composer arc per batch 5 §1 strict-reading framing).

§6.3.2 F-CP-01 Stage 3b inversion cascade: **FULLY DISCHARGED at batch 3** (preserved at this batch).

§6.3.3 (no §6.3.3 declared at Meta-Architecture §6.3 — preserved).

**F2-04 closure cascade impact**: None. The C-OD-24 §24.5 helper materialization does not gate any pending H_T-OD-* substitution retirement; it closes an adversarial-review carry-forward (inline-drift-risk) rather than enabling a substitution criterion B condition.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-20 (front (c) of post-U-RT-59 next-front menu — Phase 7d retirement audit sweep) |
| Cumulative status | 21/49 RETIRED (42.9%, unchanged from batch 6); 2 PARTIAL (AS-8 + CP-14); 10 STILL-BOUNDED |
| Predecessor batch | `phase-7d-retirement-events-batch-6.md` (post-U-RT-59-Fork-2 retirement audit; CP-13 criterion B strengthened end-to-end) |
| Audit scope | 5 post-batch-6 commits (`5cbdf97` adversarial review + `47e1724` path (i) NOTE + `2543b92` CXA back-edge + `1a90d1e` F2-04 follow-on + `da1bf74` count-drift) |
| Substantive content | §1 F2-04 follow-on arc closure documented as contract-surface refinement event (NOT substitution retirement); §2 OD-2 criterion-B explicit re-affirmation against F2-04 surface overlap |
| Successor batch | TBD — gates on (a) future HITL/validator/tool-invocation/memory/files/mcp composer arcs (10 STILL-BOUNDED unblocks); (b) fan-out arc landing (CP-14 PARTIAL → RETIRED); (c) cost-attribution composer (OD-5 STILL-BOUNDED unblock — PRICE_TABLE_REF + audit-ledger wiring carry-forwards per `[[fork-price-table-ref-substitution-retirement]]` + `[[fork-cost-record-audit-ledger-wiring-residual]]`) |
| Revision policy | Forward-only ledger discipline per workspace `CLAUDE.md` §4.3 — batch 7 is a new filing referencing batches 1-6; no retroactive edits to prior batches. |

*Batch 7 retirement audit sweep filed per forward-only-ledger discipline post 5 post-batch-6 commits. NO new RETIRED transitions; cumulative 21/49 (42.9%) unchanged. Documents F2-04 follow-on arc closure (`1a90d1e`) as a C-OD-24 §24.5 contract-surface refinement event explicitly distinguished from substitution retirement; re-affirms OD-2 criterion B against F2-04 surface-overlap question. No Class 1 forks OPEN at the U-RT-59 surface; no remaining path-(i) drift-risk carry-forwards at the U-RT-59 adversarial-review surface.*
