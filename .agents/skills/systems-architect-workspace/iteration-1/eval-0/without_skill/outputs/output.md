# Architectural Resolution — Class 1 Tension 002: TopologyPattern Enum Divergence

*Resolution recommendation for the U-CP-22 halt. Read against
`Phase_7_Class_1_Tension_002_Topology_Pattern_Enum.md`. This is an
architectural recommendation; the operator holds decision authority and must
authorize the artifact revisions before U-CP-22 implementation resumes.*

---

## §1 The architectural call

**Set 2 — the spec C-CP-10 §10.1 enumeration — is canonical.**

```
single-threaded-linear   orchestrator-workers   decentralized-handoff
hierarchical-delegation  evaluator-optimizer    parallelization
```

Set 1 (the U-CP-22 plan signature) and Set 3 (CLAUDE.md / CP-AL-1) are both
non-canonical and must be revised to Set 2. The tension record's recommended
direction (§4) is correct; this resolution confirms it against the primary
sources and discharges the tiebreaker the record left open.

## §2 Why Set 2 — and the tiebreaker is discharged

### 2.1 Authority chain

Per `CLAUDE.md` §1.3: ADR → ADD → PRD → spec → plan. Earlier artifacts are
canonical for later ones. The plan (Phase 6) cannot override the spec
(Phase 5), and the spec cannot override the ADR (Phase 3).

The decisive fact is not merely "spec beats plan." It is that **Set 2 is the
ADR-level commitment**, and the spec is a faithful transcription of it:

- `ADR-D4.md` §1.1 ("Six-pattern topology taxonomy") and §Decision item 1
  both enumerate exactly: *single-threaded linear / orchestrator-workers /
  decentralized-handoff / hierarchical-delegation / evaluator-optimizer /
  parallelization*, named "the harness-canonical pattern enumeration."
- `Spec_Control_Plane_v1_2.md` §10.1 reproduces this set verbatim as a table,
  with ADR-commitments-honored citing "ADR-D4 v1.1 §1.1 (six-pattern topology
  taxonomy table)." `Spec_Control_Plane_v1_3.md` §10 carries §10.1 forward
  verbatim ("All sub-sections preserved verbatim from v1.2").

So Set 2 is canonical at **two** levels of the authority chain (ADR-D4 §1.1
*and* C-CP-10 §10.1), not one. The plan's Set 1 and the governance docs'
Set 3 each contradict the ADR directly.

### 2.2 Tiebreaker discharged — no later ADR-D4 re-anchors the set

The tension record §4 item 4 flagged the binding open question: *does an
ADR-D4 version later than v1.1 exist that would re-anchor the canonical set
and invert this resolution?*

Verified against `design-substrate/`:

- The directory contains exactly one ADR-D4 file (`ADR-D4.md`). Unlike D1
  (`ADR-D1_v1_2.md`) and D6 (`ADR-D6_v1_2.md`), there is no versioned-suffix
  D4 artifact.
- `ADR-D4.md` §Status declares the revision history `v1 → v1.1` (dated
  2026-05-10), with `Status: Proposed`. The Change-note covers only the v1
  → v1.1 mechanical pass clearing F2-14 (the `parent_fanout_close_entry`
  ledger-shape clarification) — **the §1.1 taxonomy is in the explicit
  "Sections preserved verbatim" list and was not touched.**
- Both CLAUDE.md §2.2 and the CP spec's ADR-commitments-honored rows cite
  ADR-D4 at **v1.1**. v1.1 is the latest and the canonical version.

ADR-D4 v1.1 §1.1 is the highest-authority statement of the enum, and it is
Set 2. **The tiebreaker resolves in favor of Set 2; the resolution does not
invert.**

### 2.3 The divergence is semantic, not cosmetic — which makes the call load-bearing

The three sets are not case/format variants. Set 1 shares no member with
Set 2 or Set 3. Beyond names, the admissibility logic diverges:

- U-CP-22 acceptance #3 (Set-1 vocabulary): SEQUENTIAL_HANDOFF +
  PARENT_FANOUT_AGGREGATE admissible for all four workload classes;
  RECONCILER_MESH for content-creation + pipeline-automation; ROUTER_DELEGATE
  for software-engineering + research; PIPELINE_STAGES for pipeline-automation
  only.
- Spec C-CP-10 §10.3 (Set-2 vocabulary, traced to ADR-D4 §1.2):
  hierarchical-delegation admissible at software-engineering + research;
  decentralized-handoff at pipeline-automation; parallelization at research +
  content-creation. (Verified verbatim in `Spec_Control_Plane_v1_2.md`
  §10.3.)

These are different admissibility predicates. Adopting Set 2 means
U-CP-22's `is_admissible` function body must be rewritten to §10.3 logic, not
just its enum identifiers renamed. The CascadePolicy enum diverges the same
way: the plan declares `COMPLETE_ALL / CANCEL_ON_FIRST_FAIL /
PAUSE_ON_FIRST_FAIL`; spec §10.2/§10.3 (and ADR-D4 §1.3, inherited from
ADR-D5 §1.3.1) declare `pause / proceed / cascade-cancel`. CascadePolicy must
be reconciled to the spec set too.

## §3 What has to change

U-CP-22 implements `[C-CP-10 §10.1, §10.2, §10.3]` and its acceptance #1
requires the enum "per C-CP-10 §10.1 verbatim." The spec is canonical and
correct; **the spec does not change.** Everything that diverges from it does.

| # | Artifact / site | Current (wrong) | Change |
|---|---|---|---|
| 1 | CP plan U-CP-22 `TopologyPattern` signature (`Implementation_Plan_Control_Plane_v2_1.md` §2, line ~1185; carried verbatim into v2_2 / v2_3) | Set 1: `SINGLE_AGENT / SEQUENTIAL_HANDOFF / PARENT_FANOUT_AGGREGATE / RECONCILER_MESH / ROUTER_DELEGATE / PIPELINE_STAGES` | Set 2: `single-threaded-linear / orchestrator-workers / decentralized-handoff / hierarchical-delegation / evaluator-optimizer / parallelization` (match C-CP-10 §10.1 + §10.2 `TopologyDeclaration.pattern` literals verbatim) |
| 2 | CP plan U-CP-22 `CascadePolicy` signature | `COMPLETE_ALL / CANCEL_ON_FIRST_FAIL / PAUSE_ON_FIRST_FAIL` | `pause / proceed / cascade-cancel` per C-CP-10 §10.2 (`TopologyDeclaration.cascade_policy`) / §10.3 / ADR-D4 §1.3 |
| 3 | CP plan U-CP-22 acceptance #3 (admissibility matrix) | Set-1 admissibility set | Rewrite to C-CP-10 §10.3: hierarchical-delegation @ software-engineering + research; decentralized-handoff @ pipeline-automation; parallelization @ research + content-creation; primary-pattern admissibility per §11.1 |
| 4 | Root `CLAUDE.md` §5 CP-AL-1 verbatim text | Set 3: `ORCHESTRATOR_WORKERS / DECENTRALIZED_HANDOFF / EVALUATOR_OPTIMIZER / PARALLELIZATION / ROUTING / SEQUENTIAL_PIPELINE` | Set 2 vocabulary |
| 5 | `harness-cp/CLAUDE.md` §4.2 CP-AL-1 restatement | Set 3 | Set 2 vocabulary |
| 6 | `Sub_Agent_Boundary_Specification_v1.md` §5.1 | Set 3 | Set 2 vocabulary |

Notes on scope:

- The CP plan exists at v2 / v2.1 / v2.2 / v2.3. The tension record states the
  v2.1 body is preserved verbatim through v2.3, so the canonical/live plan
  (`Implementation_Plan_Control_Plane_v2_3.md`) carries the same defective
  signature and is the file the revision must land in; whether the historical
  v2 / v2.1 / v2.2 copies are also corrected is a fidelity-grammar /
  change-note discipline decision for the operator (recommend: revise the
  live plan, append a change-note recording the Tension-002 resolution, leave
  superseded versions as historical record).
- Item 3 (admissibility) is a genuine semantic correction, not a rename. The
  reviewer/operator must confirm the §10.3 admissibility set is what U-CP-22's
  `is_admissible` should encode; U-CP-23 (per-workload-class commitment table,
  C-CP-11 §11.1) composes against this predicate and should be re-checked for
  consistency after the U-CP-22 fix lands.
- CP-AL-1's *function* — the H_E-subagent-topology ≠ H_T-TopologyPattern
  anti-leakage rule — is unaffected and stays load-bearing. Only the enum
  vocabulary it quotes is corrected so it cites the canonical set.

## §4 Process classification and the per-CLAUDE.md regime

This is correctly filed as **Class 1** (halt-execution): the unit's plan
signature cannot be materialized to satisfy its own acceptance #1 against the
cited spec, and resolution touches a load-bearing anti-leakage rule. Under
the back-flow-deprecated / in-CLI fix regime (auto-memory: design-phase
back-flow deprecated 2026-05-15; workspace `design-substrate/` is canonical;
spec edits applied in-CLI), the resolution path is:

1. Operator confirms adoption of Set 2 and authorizes the §3 revisions.
2. Items 1–3 (plan) applied in-CLI to the live CP plan with a change-note
   recording the Tension-002 resolution; items 4–6 (governance docs) updated
   in the same pass.
3. Tension-002 record §5 block-clearing decision transitioned PENDING →
   RESOLVED with the operator decision recorded; tracked per the Class-3
   tension-record pattern in auto-memory.
4. U-CP-22 implementation resumes against the corrected plan signature.

Sibling units U-CP-15, U-OD-01, U-OD-04 are unaffected (tension record §6)
and remain independently implementable while this resolution is pending.

## §5 One-line answer

Set 2 (`single-threaded-linear / orchestrator-workers / decentralized-handoff
/ hierarchical-delegation / evaluator-optimizer / parallelization`) is
canonical — it is ADR-D4 v1.1 §1.1 verbatim and C-CP-10 §10.1 verbatim, and
no later ADR-D4 exists to re-anchor it; the U-CP-22 plan signature (Set 1,
including its CascadePolicy enum and §10.3 admissibility matrix) and the
CP-AL-1 text in `CLAUDE.md` / `harness-cp/CLAUDE.md` /
`Sub_Agent_Boundary_Specification_v1.md` (Set 3) must all be revised to
Set 2; the spec does not change.
