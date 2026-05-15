# Phase 7 — Class 1 Spec Tension Record 002 — TopologyPattern Enum Divergence

*Spec-tension record. Authored at tension detection during Phase 7 sub-phase
7b atomic-unit execution. Class 1 — halt-execution; non-determinate; requires
a design-authority decision and multi-artifact revision before U-CP-22 can be
implemented. Per the in-CLI fix regime (back-flow deprecated 2026-05-15), the
fix is applied in Claude Code CLI once the operator selects the resolution.*

---

## §1 Detection state

| Field | Value |
|---|---|
| Tension class | **Class 1** (halt-execution; non-determinate — design-authority decision required) |
| Detected at | Phase 7 Session, sub-phase 7b, atomic unit **U-CP-22** (TopologyPattern enum + admissibility predicate) |
| Detected | 2026-05-15 |
| Halt point | U-CP-22 implementation — surfaced before code execution |
| Status | **OPEN** — awaiting operator resolution decision |

## §2 Defect

U-CP-22 declares a 6-value `TopologyPattern` enum. Its acceptance #1 states
the enum is declared "per **C-CP-10 §10.1 verbatim**." But the plan signature,
the spec it cites, and the workspace governance docs give **three different
6-name enumerations** of the topology patterns.

**Set 1 — CP plan v2.1 U-CP-22 signature** (canonical plan; v2.1 body
preserved verbatim through v2.2 → v2.3):
`SINGLE_AGENT`, `SEQUENTIAL_HANDOFF`, `PARENT_FANOUT_AGGREGATE`,
`RECONCILER_MESH`, `ROUTER_DELEGATE`, `PIPELINE_STAGES`

**Set 2 — CP spec C-CP-10 §10.1** (canonical contract; `Spec_Control_Plane
_v1_3.md` preserves §10 verbatim from v1.2; traces to ADR-D4 v1.1 §1.1):
`single-threaded-linear`, `orchestrator-workers`, `decentralized-handoff`,
`hierarchical-delegation`, `evaluator-optimizer`, `parallelization`

**Set 3 — root `CLAUDE.md` §5 / CP-AL-1** (also at `harness-cp/CLAUDE.md`
§4.2 and `Sub_Agent_Boundary_Specification_v1.md` §5.1, all verbatim):
`ORCHESTRATOR_WORKERS`, `DECENTRALIZED_HANDOFF`, `EVALUATOR_OPTIMIZER`,
`PARALLELIZATION`, `ROUTING`, `SEQUENTIAL_PIPELINE`

The three sets are not reconcilable by case/format normalization — they are
genuinely different vocabularies. Set 2 ∩ Set 3 = {orchestrator-workers,
decentralized-handoff, evaluator-optimizer, parallelization}; Set 1 shares no
member with either.

**The divergence is also semantic, not just naming.** U-CP-22 acceptance #3
gives an admissibility matrix in Set-1 vocabulary ("SEQUENTIAL_HANDOFF and
PARENT_FANOUT_AGGREGATE admissible for all four workload classes;
RECONCILER_MESH admissible for content-creation + pipeline-automation;
ROUTER_DELEGATE admissible for software-engineering + research;
PIPELINE_STAGES admissible only for pipeline-automation"). Spec C-CP-10 §10.3
gives a different admissibility set ("hierarchical-delegation admissible at
software-engineering and research; decentralized-handoff admissible at
pipeline-automation; parallelization admissible at research + content-
creation"). The plan and spec disagree on **which patterns are admissible
where**, not only on names.

## §3 Why Class 1 (halt-execution)

U-CP-22 acceptance #1 requires the enum "per C-CP-10 §10.1 verbatim" — but the
plan's own signature is not verbatim from §10.1. The unit's plan signature
**cannot be materialized in a way that satisfies its own acceptance #1**
against the cited spec. Resolution requires choosing the canonical 6-pattern
vocabulary — a design-authority decision, not a determinate fix — and then
revising multiple artifacts. CP-AL-1 (which embeds Set 3) is named in
`CLAUDE.md` §5 as "the most load-bearing rule at the H_E ↔ H_T boundary," so
any change to the canonical enum touches a load-bearing anti-leakage rule.

## §4 Proposed resolution (operator decision required)

**Authority-chain reading.** Per `CLAUDE.md` §1.3, the spec (Phase 5) is
canonical over the plan (Phase 6). C-CP-10 §10.1 (Set 2) traces directly to
ADR-D4 v1.1 §1.1 "six-pattern topology taxonomy table" with cross-framework
equivalences cited. **Set 2 is the authority-chain-canonical enumeration.**

**Recommended direction (pending operator confirmation):**
1. Adopt Set 2 (spec C-CP-10 §10.1) as the canonical `TopologyPattern` enum.
2. Revise CP plan U-CP-22 signature + acceptance #1 + acceptance #3
   (admissibility matrix → align to spec §10.3) to Set-2 vocabulary, in-CLI.
3. Reconcile Set 3 — CP-AL-1 verbatim text at root `CLAUDE.md` §5,
   `harness-cp/CLAUDE.md` §4.2, `Sub_Agent_Boundary_Specification_v1.md`
   §5.1 — to Set-2 vocabulary.
4. **Tiebreaker check the operator should make:** confirm ADR-D4 has no
   version later than v1.1 that would re-anchor the canonical set. If a later
   ADR-D4 exists and matches Set 1 or Set 3, the resolution inverts.

This record does not apply any fix — the operator selects the resolution.

## §5 Block-clearing decision

| Field | Value |
|---|---|
| Decision | **PENDING** — U-CP-22 implementation is halted until the operator selects the canonical `TopologyPattern` enumeration and authorizes the artifact revisions. |
| Unblocked siblings | U-CP-15, U-OD-01, U-OD-04 are NOT affected by this tension and are independently implementable (see §6). |

## §6 Sibling assessment (this halt does not block these)

| Unit | Status |
|---|---|
| U-CP-15 (EngineClass enum) | ✅ Clean. Signature `EngineClass` matches C-CP-07 §7.1 five-element taxonomy verbatim. `Depends on: [U-CP-11]` is informational — U-CP-15 imports no U-CP-11 type; all acceptance criteria satisfiable from C-CP-07 §7.1/§7.4 standalone (consistent with Meta-Architecture §10.1 designating U-CP-15 a standalone operational-minimum unit). |
| U-OD-01 (9-cell observability matrix) | ✅ Clean. Well-specified against C-OD-01 §1.1-§1.5; `Depends on: []`. |
| U-OD-04 (OTel GenAI semconv base layer) | ✅ Clean. Well-specified against C-OD-04 §4.1-§4.5; `Depends on: []`. |
