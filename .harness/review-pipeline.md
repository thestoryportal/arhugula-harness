# Phase 7 Review-Ahead Pipeline

*Workspace-internal coordination doc. NOT a design-phase artifact. Governs the
two-lane execution model for sub-phase 7b/7c atomic-unit landing. Authored
2026-05-15.*

---

## 1. Why this exists

The §4A verbatim-divergence arc (2026-05-15) demonstrated the cost of
inline alignment work: the coding agent halted mid-landing (U-CP-22 on Tension
003, U-OD-04 on Tension 004) while spec↔plan conformance ran serially in front
of it. 17 plan-vs-spec divergences across the CP + OD plans were P6-CK-cleared
yet carried into Phase 7.

The pipeline decouples **alignment verification** from **code landing** so the
coding lane never idles waiting for a unit to be cleared against its spec.

It is NOT compute parallelism. The state-ledger (`.harness/state.jsonl`) is
hash-chained and serial — exactly one coding lane appends. The pipeline hides
**operator fork-resolution latency**: forks surface units ahead of the coder
and the operator resolves them in parallel with landing, instead of
stop-the-world.

## 2. Two lanes

| Lane | Runs as | Constraint | Output |
|---|---|---|---|
| **Review-ahead** | H_E sub-agent (`Agent` tool), read-only | No dependency-graph constraint — may review any unit before its predecessors land | Clearance verdicts → `pipeline-cleared-queue.md`; forks → `pipeline-fork-queue.md` |
| **Coding** | Main agent (this session) | Topological-sort order per per-axis plan dependency graph; serial ledger append | Landed units → `state.jsonl` + `phase-7-progress.md` |

The coding lane pulls only from the **cleared queue**. The review-ahead lane
runs ahead in topo order, buffer depth **N = 5 units per axis** (advisor
guidance — small buffer keeps invalidation cheap when an operator spec
absorption invalidates downstream review work).

## 3. The hard wall — reviewer does NOT edit canonical artifacts

**Load-bearing rule, not a caveat.** A review-ahead agent that auto-edits a
spec or plan to "clear" a unit is X-AL-3 silent absorption (`CLAUDE.md` §4.4 /
I-2). The coding lane would then build against contaminated context. The
pipeline preserves back-flow (`CLAUDE.md` §4.3); it does not route around it.

The workspace's existing four-role separation is the wall:

| Role | Skill | Does | Does NOT |
|---|---|---|---|
| Detect + classify | `harness-adversarial-reviewer` | red-team unit spec+plan; emit finding-classified report | edit any artifact; propose replacement text |
| Propose resolution | `systems-architect` (§4A tension-resolution mode) | recommend a fix, traced to authority chain | decide; edit |
| **Decide** | **operator** | accept / reject / pick reading | — |
| Apply | `spec-writer` / `implementation-planner` | write the decided fix into the canonical file | decide; red-team |

A unit is **cleared** only when (a) the reviewer surfaced no blocking
(§2.7.6 Class 1) fork, OR (b) every such fork was operator-resolved and the fix
applied by `spec-writer` / `implementation-planner`.

## 4. Fork handling

Reviewer findings map to `CLAUDE.md` §4.3 fork classes:

- **§2.7.6 Class 1 (halt)** — blocks the unit. Goes to `pipeline-fork-queue.md`;
  unit does NOT enter the cleared queue. Operator resolves; applicator skill
  applies; reviewer re-checks.
- **§2.7.6 Class 2 (operator decision)** — non-halting choice point. Fork queue,
  flagged for operator; unit may still clear if the decision is not a
  precondition for materialization.
- **§2.7.6 Class 3 (informational)** — logged, non-blocking. Unit clears.

## 5. Cold-start / bootstrap

On cold start the cleared queue is empty. The coding lane bootstraps on an
axis NOT under review, using the existing per-unit cadence (read unit body +
cited spec directly — this self-read stays in cadence permanently as
defense-in-depth against a wrong clearance, advisor guidance). Once the
review-ahead lane produces its first clearances, the coding lane switches to
pulling from the cleared queue.

## 6. Sub-agent boundary (CP-AL-1)

The review-ahead lane uses H_E sub-agents — execution-time parallelism,
explicitly allowed by `CLAUDE.md` §5.1. This is NOT H_T's CP-axis topology.
"We have review-ahead sub-agents" never implies any H_T `TopologyPattern`
value is met (CP-AL-1 anti-pattern, `CLAUDE.md` §5).

## 7. Pilot — CP v2.5 + OD v2.5 re-clearance

**First pipeline pass.** Scope: the deferred pre-implementation re-clearance of
the §4A conformance delta plans (`CLAUDE.md` remaining-work item #1).

- **Review-ahead lane:** one `harness-adversarial-reviewer` sub-agent,
  Phase-7 pre-implementation review mode, against `Implementation_Plan_Control_Plane_v2_5.md`
  + `Implementation_Plan_Operational_Discipline_v2_5.md` (delta files) vs their
  cited `Spec_Control_Plane_v1_3.md` / `Spec_Operational_Discipline_v1_3.md`
  contracts. Catches any verbatim defect the conformance pass re-introduced;
  dispositions the 4 carried findings + 5 flagged items.
- **Coding lane (concurrent):** lands AS-axis units (independent axis, not in
  pilot scope) on the existing per-unit cadence.
- **Success criterion:** reviewer produces a clearance verdict for the CP/OD
  v2.5 cluster while ≥1 AS unit lands; the cluster's cleared units flow into
  `pipeline-cleared-queue.md` as the coding lane's next batch.

If the reviewer surfaces forks faster than the operator can resolve them, that
empirically sizes the buffer before scaling the pipeline to the full
~140-unit runway.

## 8. Queued review-ahead passes

| # | Pass | Trigger | Rationale |
|---|---|---|---|
| Q1 | **Systemic AS-plan verbatim audit** — output `.harness/verbatim_audit_as_plan.md` | ✅ **COMPLETE** 2026-05-15 | All 33 AS units audited: 18 CLEARED · 3 CONFORM · 12 FORK. 2 systemic patterns — Pattern A (verbatim divergence, 7 units), Pattern B (undeclared auxiliary types, ≥7 units / ≥11 types). U-AS-02 retrospective Class-3. Resolution: one `implementation-planner` 2-sub-pass revision + a `spec-writer` C-AS-02 §2.2/§2.3/§11.1 reconciliation. The report is the canonical AS systemic-tension record. |
| Q2 | **Systemic CP-plan materializability audit** — output `.harness/materializability_audit_cp_plan.md` | ✅ **COMPLETE** 2026-05-15 | All 56 CP units: 20 CLEARED · 12 CONFORM · 24 FORK. 3 systemic patterns — C (`AttributeValueType`/`Cardinality` no-carrier, 7 units), D (≥25 undeclared auxiliary types across ≥20 units + ≥5 hidden-coupling edges), E (`[U-CP-00]` edges recorded but not materialized — supersedes v2.5 §0.8 "not a fork"). U-CP-15 retrospective Class-3. Supersedes fork-queue items 16/17/18. |
| Q3 | **Systemic OD-plan materializability audit** — output `.harness/materializability_audit_od_plan.md` | ✅ **COMPLETE** 2026-05-15 | All 34 OD units: 19 CLEARED · 1 CONFORM · 14 FORK. 3 patterns — M-1 (≥11 undeclared auxiliary types across ≥10 units; load-bearing `SpanRef`/`SpanAttributes`/`EventEmission`), M-2 (hidden coupling, 3 units), M-3 (U-OD-34 hardcodes stale 28/IS:6 edge count vs canonical 26/IS:4). U-OD-04 retrospective Class-3 (proposed M-1 carrier site). |

| Q4 | **Systemic IS-plan materializability audit** — output `.harness/materializability_audit_is_plan.md` | ✅ **COMPLETE** 2026-05-15 | All 17 IS units: 11 CLEARED · 1 CONFORM · 5 FORK. 1 pattern — M-1-IS (`WorkflowClass`/`DeploymentSurface`/`WorkflowEvent`/`WorkloadClass` no carrier, 5 units). IS is the cleanest plan — no verbatim disease, dependency graph complete. U-IS-02 retrospective concern. **Correction:** `AuditPayload`/`AuditLedger` are NOT IS-exported (OD M-1 hypothesis wrong) — they are OD-local; the U-OD-30 cross-axis IS edge is to the entry shape + hash-chain discipline only. |
| T1 | **`systems-architect` shared-type triage** — output `.harness/shared_type_carrier_map.md` | ✅ **COMPLETE** 2026-05-15 — **AWAITING OPERATOR RATIFICATION** | ~62 types triaged: ~9 `harness-core` · ~27 per-axis · 2 CXA seam · ~24 X-AL-3 design-extension candidates (2 are Class-1 halts). New carriers: U-CORE-01, U-CP-00b, 1–2 OD carriers. Recommended revision order: harness-core → IS → AS → CP → OD. |

| T2 | **`systems-architect` X-AL-3 tension resolution** — output `.harness/xal3_resolution_recommendations.md` | ✅ **COMPLETE** 2026-05-15 | **27 of 27 X-AL-3 candidates = FACTOR-OUT; 0 genuine design extensions.** Both Class-1 halts dissolve (`WorkflowEvent`/`WorkflowClass`/`DeploymentSurface` → `harness-core`, IS imports core ≠ cross-axis edge; `AuditLedgerEntry` is CP-spec-owned per CP §16.2, not an OD seam). **NO design-substrate revision owed; `spec-writer` not engaged.** All 27 re-route into the 4 per-axis revision passes. |

**⛔ RATIFICATION GATE.** The X-AL-3 blocker is cleared (T2: no design
extensions). Per-axis revision passes start once the operator ratifies
`.harness/shared_type_carrier_map.md` (as amended by T2 — all 27 X-AL-3 rows
become disposition-1/2). No design-phase back-flow; the conformance is purely
`implementation-planner` work.

**Conformance sequence (operator-ratified path, decided 2026-05-15):**

1. Q4 IS audit completes → all 4 plans have a materializability record.
2. **`systems-architect` shared-type triage** — one pass over every undeclared
   auxiliary type across the 4 audits; classify each: `harness-core` resident /
   per-axis-owned / cross-axis seam. Produces a carrier map. Operator ratifies.
3. **Per-axis `implementation-planner` revision passes (×4)** — each absorbs its
   audit + the ratified carrier map. Operator ratifies each. Plus a
   `spec-writer` C-AS-02 §2.2/§2.3/§11.1 reconciliation (Q1's one genuine spec
   under-spec).
4. Review-ahead lane re-checks the conformed plans.
5. Coding lane resumes from the genuinely-cleared queue.

The coding lane is **PAUSED** until the conformed plans land.

## 9. Files

| File | Role |
|---|---|
| `review-pipeline.md` | This file — pipeline design |
| `pipeline-cleared-queue.md` | Units cleared by the review-ahead lane; coding lane pulls from here |
| `pipeline-fork-queue.md` | Forks awaiting operator decision |
