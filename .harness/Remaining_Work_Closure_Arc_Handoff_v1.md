# Remaining-Work Closure Arc — Handoff Artifact v1

**Filed:** 2026-05-21 (Phase E, final phase of Remaining-Work Closure Arc)
**Arc duration:** 1 session (Phase 1 → Phase E inclusive)
**Production-ready disposition:** Plan corpus converged at Phase D iteration 2; spec corpus converged at Phase B iteration 2.
**Next session opens:** First Phase 7-implementation cluster per §5 ROI-weighted landing sequence below.

---

## §1 Arc summary

**Mission:** Comprehensive code-review → specification authoring (with adversarial-review loop) → implementation-plan authoring (with adversarial-review loop) → handoff. The arc was orchestrated per the plan file at `/Users/robertrhu/.claude/plans/begin-comprehensive-and-sharded-bird.md` (operator-approved 2026-05-21).

**Phases completed (in order):**

| Phase | Sub-arcs | Output |
|---|---|---|
| **Phase 1** (Exploration) | 3 Explore agents | Reconciled inventory: 9 STILL-BOUNDED + 2 PARTIAL substitutions + 4 absent composers + 8 NotImplementedError sites + 12 spec NOTE-deferred + 8 Class 3 informational forks |
| **Phase A** (Spec authoring) | A.0 LLM-dispatch fork audit → A.5 OD compound-irrelevance unblock (6 sub-arcs) | 5 spec deltas + 14 new contracts + 1 extension |
| **Phase B** (Spec adversarial review) | 2 iterations to convergence | Spec corpus: 0 open findings |
| **Phase C** (Implementation plan authoring) | 1 pass (revision-pass mode) | 4 plan deltas + 43 new atomic units |
| **Phase D** (Plan adversarial review) | 2 iterations to convergence | Plan corpus: 0 open findings |
| **Phase E** (Handoff) | This artifact | Production-ready handoff |

---

## §2 Spec deltas (versions + change-notes)

All under `design-substrate/`:

| File | Version delta | Change scope |
|---|---|---|
| `Spec_Harness_Runtime_v1.md` | v1.12 → **v1.13** | NEW §14.9 C-RT-19 RuntimeToolDispatcher + MCPClientHost + §14.10 C-RT-20 WebhookDeliveryComposer + OperatorBurdenEvaluator; 11 new fail classes; 8 new spans; transport-neutral terminology block (STDIO + HTTP + SSE all v1) |
| `Spec_Control_Plane_v1_10.md` | v1.9 → **v1.10** (new delta-over file) | NEW §17.4 hitl_gate canonical signature materialization + §25 C-CP-25 ValidatorFramework (with bijective ValidatorOutcome→ValidatorNextAction mapping per F2-03 ratification) + §26 C-CP-26 PauseResumeProtocol + §27 C-CP-27 PerServerTrustEvaluator + MCPClientNamespaceEmitter (ALLOW-with-tier-floor unknown-server default per Decision 3.D1 ratification); 8 new CP fail classes; 7 new spans; 7 new enums; Pattern-D 15-type inheritance citation table |
| `Spec_Action_Surface_v1.md` | v1.3 → **v1.4** | Producer-site reference notes at C-AS-14 §14.3 + C-AS-15 §15 (annotation-only; no field-set / attribute / contract change) |
| `Cross_Axis_Composition_Document_v2_6.md` | v2.5 → **v2.6** (new delta-over file) | +5 new genuine-typed-seam edges at §2.3.7 CP→OD bucket (WebhookDelivery + OperatorBurden + Validator + Pause/Resume + PerServerTrust audit-writes); aggregate 94 → 99 canonical; 24 → 29 genuine; bucket 2 → 7 |
| `Spec_Operational_Discipline_v1_8.md` | v1.7 → **v1.8** (new delta-over file) | 9 new contracts (C-OD-25 WorkflowEnvelopeSpan + C-OD-26 CostAttributionInvocation + C-OD-27 SqliteWritePath + C-OD-28 PRICE_TABLE_REF + C-OD-29 through C-OD-33 canonical namespace schemas); Decimal string-serialization invariant at OTel boundary per F2-06 ratification; compound-irrelevance unblock for OD-3/4/5/6 + closes PRICE_TABLE_REF X-AL-2 carry-forward fork |

**Operator-ratified decisions absorbed at spec layer (11 total):**
- F2-01 transport-neutral terminology / F2-02 Pattern-P1 alignment 11-attr / F2-03 OPERATOR_BURDEN_EXCEEDED→ESCALATE_HITL / F2-04 single-envelope default / F2-05 CPU-meter validator default / F2-06 Decimal string-serialization
- Decision 1.D4 STDIO+HTTP+SSE / Decision 2.D3 validators run every step / Decision 2.D6 PauseResume coexist with U-CP-56 / Decision 2.D7 STRICT MaterialDiffPolicy default / Decision 3.D1 ALLOW with tier-floor

---

## §3 Plan deltas (atomic unit IDs + topological order + cluster boundaries)

All under `design-substrate/`:

| Plan file | Version delta | New units | New cluster |
|---|---|---|---|
| `Implementation_Plan_Harness_Runtime_v2_11.md` | v2.10 → **v2.11** | 8 (U-RT-63 through U-RT-70) | L9-sexies (NEW) |
| `Implementation_Plan_Control_Plane_v2_15.md` | v2.14 → **v2.15** | 15 (U-CP-58 through U-CP-72) | Cluster 10 (NEW) with 4 sub-clusters |
| `Implementation_Plan_Operational_Discipline_v2_14.md` | v2.13 → **v2.14** | 20 (U-OD-35 through U-OD-54) | Cluster 4 (NEW) with 5 sub-clusters |
| `Implementation_Plan_Action_Surface_v1_3.md` | v1.2 → **v1.3** | 0 (thin revision-pass for traceability; AS spec v1.4 is annotation-only) | n/a |

**Total new atomic units:** 43

**Aggregate DAG:** Kahn-acyclic across all 43 units + 13 cross-axis edges (verified at Phase C log + Phase D iteration-2 cluster-sizing re-verification). 6 topological levels (L0–L6).

**Sub-cluster decomposition (per Phase D iteration-1 F2-05 absorption):**

| Sub-cluster | Units | Sub-cluster scope |
|---|---|---|
| **10-CP-A** | U-CP-58 / 59 / 60 / 61 (4) | ValidatorFramework — closes hitl_placement.py + operator_burden_eval.py NotImplementedError sites |
| **10-CP-B** | U-CP-62 / 63 / 64 / 65 (4) | PauseResumeProtocol — closes pause_resume_protocol.py NotImplementedError sites |
| **10-CP-C** | U-CP-66 / 67 / 68 / 69 / 70 (5) | PerServerTrustEvaluator + MCPClientNamespaceEmitter — closes Q5 disjointness pin from U-RT-62 |
| **10-CP-D** | U-CP-71 / 72 (2) | hitl_gate signature + cp_audit_to_od_audit converter extension (8 prefixes) |
| **4-OD-A** | U-OD-35 / 36 / 37 (3) | WorkflowEnvelopeSpan — unblocks compound-irrelevance for OD-3/4/5/6 |
| **4-OD-B** | U-OD-42 / 43 / 44 / 45 (4) | SqliteWritePath — closes H_T-OD-6 PARTIAL → RETIRED |
| **4-OD-C** | U-OD-46 / 47 / 48 / 49 (4) | PRICE_TABLE_REF + Decimal string-serialization — closes X-AL-2 carry-forward fork |
| **4-OD-D** | U-OD-38 / 39 / 40 / 41 (4) | CostAttribution invocations — closes H_T-OD-5 retirement |
| **4-OD-E** | U-OD-50 / 51 / 52 / 53 / 54 (5) | Canonical namespace schemas — consumer-side complement to CP composers |

Each sub-cluster size (2–8 units) matches precedent landing arcs (U-RT-58 / U-RT-59 / U-RT-60 / U-RT-62 ranged 4–8 commits).

---

## §4 H_T-substitution retirement projection

Phase 7d substitution retirement (per `harness-cp/CLAUDE.md` §4.1 retirement table baseline at 22/49 = 44.9% RETIRED at arc start):

| Sub-cluster | Substitutions retired upon landing |
|---|---|
| L9-sexies (runtime, 8 units) | AS-2 / AS-4 / AS-5 / AS-8 PARTIAL→full / CXA-1 (5 retirements) |
| 10-CP-A (ValidatorFramework) | CP-21 (1 retirement) |
| 10-CP-B (PauseResumeProtocol) | CP-22 (1 retirement) |
| 10-CP-C (PerServerTrust) | CP-18 (1 retirement) |
| 10-CP-D (hitl_gate + converter) | none direct (enables 5 CP→OD seams) |
| 4-OD-A (WorkflowEnvelope) | none direct (enables OD-3/4/5/6 compound-irrelevance unblock) |
| 4-OD-B (sqlite) | OD-6 PARTIAL→full (1 retirement) |
| 4-OD-C (PRICE_TABLE_REF) | PRICE_TABLE_REF X-AL-2 carry-forward CLOSED (1 fork closure) |
| 4-OD-D (CostAttribution) | OD-5 (1 retirement) |
| 4-OD-E (canonical schemas) | none direct (consumer-side schemas) |

**Direct retirements on full arc landing: 10 substitutions.**
- CP retirements: 3 (CP-18, CP-21, CP-22)
- AS retirements: 4 (AS-2, AS-4, AS-5, AS-8)
- OD retirements: 2 (OD-5, OD-6)
- CXA retirements: 1 (CXA-1)

Plus compound-irrelevance unblock for OD-3 + OD-4 (samplers + redactors) which require additional follow-on arcs to fully retire.

**Cumulative projection (full arc landing):** 22 → 32 RETIRED (65.3%). Plus 2 enabled (OD-3, OD-4) pending follow-on.

---

## §5 ROI-weighted landing sequence (per-cluster recommended sequence)

### Recommended first cluster: **4-OD-A (WorkflowEnvelope)**

**Rationale:**
- **Size:** 3 units — smallest sub-cluster; comfortable single-session landing
- **Leverage:** Unblocks 4 OD primitives (OD-3 / OD-4 / OD-5 / OD-6) via compound-irrelevance pattern closure
- **Cross-axis deps:** ZERO (pure within-OD arc)
- **Precedent match:** 3-unit landings match the smaller end of recent arcs
- **Test impact:** Minimal — adds workflow.envelope OTel span emission at workflow_driver entry; existing 2287+ test suite unaffected (new tests added per AC #5 expansion at iteration-2)

### Recommended second cluster: **L9-sexies (Runtime tool-invocation)**

**Rationale:**
- **Size:** 8 units — largest single-arc landing in the queue but still within precedent
- **Leverage:** Directly retires 5 substitutions (AS-2/4/5/8 + CXA-1)
- **Cross-axis deps:** Light (U-RT-67 ← U-CP-68 + U-CP-69; can mock OR land 10-CP-C first)
- **Decision impact:** Closes the Class 2 C.1 fork that was deferred for ~5 months
- **Prerequisite:** Decide STDIO-only vs HTTP+SSE landing scope per per-server config (operator-decided; spec supports all 3)

### Subsequent cluster order (ROI-ranked):

| Order | Sub-cluster | Units | Direct retirements | Notes |
|---|---|---|---|---|
| 3 | 4-OD-C (PRICE_TABLE_REF + Decimal) | 4 | 1 fork closure | Prerequisite for 4-OD-D; closes X-AL-2 carry-forward |
| 4 | 4-OD-D (CostAttribution) | 4 | 1 (OD-5) | Depends on 4-OD-A + 4-OD-C |
| 5 | 10-CP-A (ValidatorFramework) | 4 | 1 (CP-21) | Cross-axis dep on 4-OD-E (soft, see F1-03 absorption) |
| 6 | 4-OD-E (canonical schemas) | 5 | 0 direct | Can land in parallel with 10-CP-A/B/C; consumer-side complement |
| 7 | 10-CP-C (PerServerTrust) | 5 | 1 (CP-18) | Closes Q5 disjointness pin from U-RT-62 |
| 8 | 10-CP-B (PauseResumeProtocol) | 4 | 1 (CP-22) | Coexists with U-CP-56 replay-resumption |
| 9 | 4-OD-B (sqlite) | 4 | 1 (OD-6 PARTIAL→full) | Depends on existing RingBufferStage at v2.13 |
| 10 | 10-CP-D (hitl_gate + converter) | 2 | 0 direct | Cross-axis integration; depends on 10-CP-A/B/C + L9-sexies + 4-OD-D for converter completeness |

**Alternative first cluster: L9-sexies first (if operator prefers direct retirements over enabler).** Trade-off: 8 units vs 3 units; 5 retirements vs 4-primitive enablement. Operator picks.

---

## §6 Deferred items + carry-forwards

### CXA v2.6 → v2.7 amendment owed

Per Phase D iteration-2 F2-02 absorption (operator-ratified Option 1):

- **Scope:** Add §2.3.7 row 8 for cost-attribution audit-write seam (U-OD-41 → U-OD-00 via `cost:` action_id prefix); aggregate matrix update (CP→OD 7 → 8; aggregate 99 → 100; genuine 29 → 30).
- **Estimated effort:** ~30 lines of delta-over file.
- **Routing:** Phase A iteration-N (CXA spec amendment is spec-layer scope; not plan-layer). Should land before U-CP-72 implementation.
- **Trigger:** When 10-CP-D opens (or earlier if operator prefers single CXA amendment session).

### Phase A scope-gap items (per Phase B iteration-1 F2-07)

The Phase A composer scope explicitly did NOT address these 8 STILL-BOUNDED substitutions (operator-ratified scope per plan file; not a defect — explicit future-arc routing):

| Substitution | Blocker (composer required) |
|---|---|
| **CP-12** (sandbox-tier dispatch) | Touched by §14.9 but no full composer; sub-agent dispatch composer (already wired post-U-RT-59 single-slice) needs fan-out arc |
| **CP-16** (memory primitive consumption) | Memory-invocation composer |
| **CP-17** (files primitive consumption) | Files-invocation composer |
| **CP-19** (cross-deployment monotonicity) | Multi-deployment runtime path |
| **CP-23** (bridging-arc traversal) | Multi-topology cascade composer |
| **OD-1** (deferral envelope) | Runtime deferral-gate composer |
| **OD-3** (composite sampler) | Sampler implementation (4-OD-A unblocks this) |
| **OD-4** (pre-collector redaction processor) | Redaction processor implementation (4-OD-A unblocks this) |
| **OD-7** (preservation invariants) | Runtime enforcement loop |

After full arc landing: 32 / 49 retired (65.3%). Remaining 17 = 8 above + 9 still-bounded primitives requiring additional composer arcs. Estimated 4–6 future Closure Arcs to reach 100% retirement (if pursued).

### Bounded carry-forwards documented (X-AL-2 + Class 3)

- **SpanCostRecord audit-ledger wiring residual** (`[[fork-cost-record-audit-ledger-wiring-residual]]`) — OD spec v1.5 §25.9 specifies carrier production; downstream audit-ledger wiring partly addressed at Phase A.5 §C-OD-26 (cost-attribution invocation contract) + Phase D iteration-2 §C-OD-26.3 audit-ledger write per cost-record; may now be closeable at next workspace tension-record audit.
- **FastMCP transport-level handler registration** — narrowed by Phase A.2 (STDIO + HTTP + SSE all v1); remaining scope is transport-level handler binding details deferred to per-server implementation arcs.
- **Per-axis CLAUDE.md v2.1→v2.4 citation drift** — non-blocking; routed to next CP plan revision touching edge counts.

---

## §7 Next-session opening instructions

### Option A — RECOMMENDED: open 4-OD-A WorkflowEnvelopeSpan cluster

**Cluster:** 4-OD-A (3 units: U-OD-35, U-OD-36, U-OD-37)
**Spec authority:** OD spec v1.8 §C-OD-25
**Prerequisite checks:**
1. Workspace at `main` HEAD with v1.13 runtime spec + v1.10 CP spec + v1.4 AS spec + v2.6 CXA + v1.8 OD spec + v2.11/15/14/1.3 plans merged from this arc's worktree
2. 2287+ workspace tests green
3. No pending operator decisions

**Skill activation:** `phase-7-implementation` skill at next session start with:
> Open cluster 4-OD-A (3 units U-OD-35 / U-OD-36 / U-OD-37) materializing OD spec v1.8 §C-OD-25 WorkflowEnvelopeSpan. Authority chain ratified at Phase E handoff `.harness/Remaining_Work_Closure_Arc_Handoff_v1.md` §5. Land in topological order; verify aggregate test suite remains green at each commit.

### Option B — operator preference for direct-retirement velocity: open L9-sexies runtime cluster

**Cluster:** L9-sexies (8 units: U-RT-63 through U-RT-70)
**Spec authority:** Runtime spec v1.13 §14.9 + §14.10
**Direct retirements:** 5 substitutions (AS-2, AS-4, AS-5, AS-8, CXA-1)
**Trade-off:** Larger arc; 8 units vs 3 in Option A.

### Option C — operator preference: simultaneous parallel arcs

Open BOTH 4-OD-A + L9-sexies in parallel axis-stream execution (per workspace `CLAUDE.md` §1.1 axis-stream parallelism). Requires 2 session contexts or sequential interleaving. Highest velocity but tightest cognitive load.

---

## §8 Arc artifact inventory

### `.harness/` (Phase A + B + C + D records)

| Artifact | Phase | Status |
|---|---|---|
| `Phase_A_0_LLM_Dispatch_Fork_Audit_v1.md` | A.0 | CLOSURE record (Option-A-taken ratification) |
| `Phase_A_1_Tension_Resolution_v1.md` | A.1 | CONFIRMATION-OF-PRIOR-RATIFICATION |
| `Phase_A_2_Contract_Drafts_v1.md` | A.2 | Operator-ratified contract drafts (architect mode) |
| `Spec_Phase_A_2_Authoring_Log_v1.md` | A.2 | spec-writer apply-pass change-note ledger |
| `Spec_Drift_Reconciliation_v1.md` | A.3 | 23-item disposition ledger (3 ABSORBED + 5 STALE-SUPERSEDED + 15 DEFERRED-WITH-RATIONALE) |
| `Spec_Phase_B_Adversarial_Review_v1.md` | B iteration 1 | 10 findings (7 Class 2 + 3 Class 1) |
| `Spec_Phase_A_Iteration_1_Log.md` | B iteration 1→2 transition | iteration-2 disposition log |
| `Spec_Phase_B_Adversarial_Review_v2.md` | B iteration 2 | CONVERGED — 0 findings |
| `Phase_C_Implementation_Plan_Authoring_Log_v1.md` | C | 43-unit decomposition + DAG verification |
| `Plan_Phase_D_Adversarial_Review_v1.md` | D iteration 1 | 9 findings (5 Class 2 + 4 Class 1) |
| `Plan_Phase_C_Iteration_1_Log.md` | D iteration 1→2 transition | iteration-2 disposition log |
| `Plan_Phase_D_Adversarial_Review_v2.md` | D iteration 2 | CONVERGED — 0 findings |
| `Remaining_Work_Closure_Arc_Handoff_v1.md` | E | This file |

### `design-substrate/` (Phase A spec deltas + Phase C plan deltas)

| Artifact | Phase | Status |
|---|---|---|
| `Spec_Harness_Runtime_v1.md` (v1.13) | A.2 + B iter 2 | Spec corpus |
| `Spec_Control_Plane_v1_10.md` (v1.10) | A.2 + B iter 2 | Spec corpus |
| `Spec_Action_Surface_v1.md` (v1.4) | A.2 + B iter 2 | Spec corpus |
| `Cross_Axis_Composition_Document_v2_6.md` (v2.6) | A.4 + B iter 2 | Spec corpus |
| `Spec_Operational_Discipline_v1_8.md` (v1.8) | A.5 + B iter 2 | Spec corpus |
| `Implementation_Plan_Harness_Runtime_v2_11.md` (v2.11) | C + D iter 2 | Plan corpus |
| `Implementation_Plan_Control_Plane_v2_15.md` (v2.15) | C + D iter 2 | Plan corpus |
| `Implementation_Plan_Operational_Discipline_v2_14.md` (v2.14) | C + D iter 2 | Plan corpus |
| `Implementation_Plan_Action_Surface_v1_3.md` (v1.3) | C | Plan corpus (thin revision-pass) |

### Modified existing artifacts

- `.harness/class_1_tension_cp_batch_blocked_units_2026_05_16.md` — header amended per F1-03 of Phase A.3 (D-A.1-01 absorption); RESOLVED status added; original HALT framing preserved for traceability

---

## §9 Verification checklist (operator pre-merge)

Before merging the arc's worktree branch to `main`:

- [ ] All 5 spec deltas readable + version-bumped + change-notes present
- [ ] All 4 plan deltas readable + atomic units enumerated + Depends-on lines verified
- [ ] CXA v2.6 byte-exact reads as 99 canonical edges (24 genuine + 46 convention + 24 phase-2-runtime + 5 spurious-struck-from-v2.3)
- [ ] OD v1.8 §C-OD-29.1 attribute table reads 11 attributes across 4 span sites (Pattern-P1 alignment with CP §25.5)
- [ ] CP v1.10 §25.2 ValidatorOutcome → ValidatorNextAction mapping table present (5 rows; OPERATOR_BURDEN_EXCEEDED → ESCALATE_HITL row visible)
- [ ] Runtime spec v1.13 §14.9.1 transport-neutral terminology block present
- [ ] CXA v2.6 → v2.7 amendment owe surfaced + routing target identified (Phase A iteration-N before U-CP-72 implementation)
- [ ] No production code touched (only `design-substrate/` + `.harness/`)
- [ ] Existing 2287+ workspace test suite green (this arc adds NO production-side code)

---

## §10 Workspace state at arc close

- **Worktree:** `worktree-remaining-work-closure-arc-phase-a` at HEAD (rebased onto local `main` at Phase A.2 to absorb 11 commits including v1.12 spec bump from U-RT-62 landing)
- **Untracked files:** 13 `.harness/` records + 4 plan deltas + 4 spec deltas + 1 modified tension record
- **Production code changes:** ZERO (this arc is design-layer only)
- **Test suite invariant:** preserved (no source-tree touches)
- **CXA invariant:** preserved (DAG-acyclic; per-axis acyclic; back-edge introduced at v2.4 extended at v2.5 + v2.6 to CP→OD bucket of 7 typed seams)
- **Substitution retirement at arc close:** 22 / 49 RETIRED (44.9%) — unchanged (arc adds spec + plan; retirements happen at implementation arc landings)

---

## §11 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/Remaining_Work_Closure_Arc_Handoff_v1.md` |
| Arc duration | 1 session, Phases 1 → E |
| Artifacts produced | 13 `.harness/` records + 4 plan deltas + 4 spec deltas + 1 amended tension record |
| Total new contracts | 14 (C-RT-19 + C-RT-20 + C-CP-25 + C-CP-26 + C-CP-27 + C-OD-25 through C-OD-33) + 1 extension (C-CP-17 §17.4) |
| Total new atomic units | 43 |
| Total new fail classes | 19 |
| Total new spans | 16 |
| Total new enums | 8 |
| Total new CXA edges | 5 (with 1 more owed at CXA v2.7 amendment) |
| Operator decisions ratified | 15 (11 spec-layer + 1 CXA-routing + 3 other) |
| Adversarial-review iterations | 4 (B iter 1+2; D iter 1+2) |
| Findings resolved (B + D total) | 19 (7+4 at B + 5+4 at D, minus 1 cross-counted operator-decision) |
| Phase E disposition | PRODUCTION-READY HANDOFF |
| Next gate | Next session opens cluster per §7 (Option A recommended: 4-OD-A WorkflowEnvelope) |
