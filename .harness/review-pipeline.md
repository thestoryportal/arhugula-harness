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

## 8. Files

| File | Role |
|---|---|
| `review-pipeline.md` | This file — pipeline design |
| `pipeline-cleared-queue.md` | Units cleared by the review-ahead lane; coding lane pulls from here |
| `pipeline-fork-queue.md` | Forks awaiting operator decision |
