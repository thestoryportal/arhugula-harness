# Phase 7 Class-N Tension Record — U-CP-22 `TopologyPattern` Enum Vocabulary Divergence

**Mode:** systems-architect — tension-resolution mode (§4A).
**Surfaced by:** Operator, mid-CP-axis implementation, U-CP-22.
**Artifacts read:** `design-substrate/Spec_Control_Plane_v1_2.md` §10 (C-CP-10), `design-substrate/Implementation_Plan_Control_Plane_v2_1.md` U-CP-22, `design-substrate/ADR-D4.md` §1.1, `design-substrate/Spec_Control_Plane_v1_3.md`, `design-substrate/Implementation_Plan_Control_Plane_v2_3.md`.

> **Role marker:** This skill recommends; it does not decide. The operator holds decision authority (`CLAUDE.md` I-2; SKILL §4A.4). The operator asked for a call "to move on" — the recommendation below is determinate and the tiebreaker is already confirmed, so the operator can adopt it directly. The recommendation is *conform the plan to the spec*; it does not re-decide which vocabulary is "better."

---

## 1. The tension, stated precisely

U-CP-22 declares the `TopologyPattern` enum. Its acceptance criterion #1 reads "declares exactly six values per C-CP-10 §10.1 **verbatim**" — but the plan's enum values are **not** the spec's values. Two divergent vocabularies, both six-valued:

**Spec — `Spec_Control_Plane_v1_2.md` §10.1, the C-CP-10 six-pattern taxonomy table:**

| # | Spec `Pattern` value |
|---|---|
| 1 | `single-threaded-linear` |
| 2 | `orchestrator-workers` |
| 3 | `decentralized-handoff` |
| 4 | `hierarchical-delegation` |
| 5 | `evaluator-optimizer` |
| 6 | `parallelization` |

(Spec §10.2 `TopologyDeclaration.pattern` repeats the same six string literals.)

**Plan — `Implementation_Plan_Control_Plane_v2_1.md` U-CP-22 signature block:**

```
enum TopologyPattern {
  SINGLE_AGENT,
  SEQUENTIAL_HANDOFF,
  PARENT_FANOUT_AGGREGATE,
  RECONCILER_MESH,
  ROUTER_DELEGATE,
  PIPELINE_STAGES
}
```

These are not stylistic variants (kebab vs SCREAMING_SNAKE). They are **different names for the topology concepts**: e.g. spec `orchestrator-workers` vs plan `PARENT_FANOUT_AGGREGATE`; spec `evaluator-optimizer` vs plan `RECONCILER_MESH`; spec `decentralized-handoff` vs plan `SEQUENTIAL_HANDOFF`; spec has no `PIPELINE_STAGES`/`ROUTER_DELEGATE` pattern at all (those map loosely onto spec `single-threaded-linear` / `hierarchical-delegation` but not by name). The plan's own acceptance criterion #1 is therefore **internally self-contradicting**: it cites "§10.1 verbatim" while listing values that do not appear in §10.1.

A parallel divergence exists on the co-declared `CascadePolicy` enum (spec §10.2/§10.3: `pause` | `proceed` | `cascade-cancel`; plan U-CP-22: `COMPLETE_ALL` | `CANCEL_ON_FIRST_FAIL` | `PAUSE_ON_FIRST_FAIL`). The resolution below covers it on the same reasoning.

The operator framed this as a topology divergence in `CLAUDE.md` §1 itself, which lists yet a **third** vocabulary for the 6-class enum (`ORCHESTRATOR_WORKERS / DECENTRALIZED_HANDOFF / EVALUATOR_OPTIMIZER / PARALLELIZATION / ROUTING / SEQUENTIAL_PIPELINE`, CP-AL-1). That CLAUDE.md list is the spec vocabulary in SCREAMING_SNAKE casing — it confirms the spec's *concept set*, not the plan's.

---

## 2. Authority-chain placement (`CLAUDE.md` §1.3)

Chain: **ADR (F1–F5 + D1–D6) → ADD v1.3 → PRD v1.1 → per-axis spec v1.x → per-axis plan v2.x**. Earlier is canonical for later.

| Artifact | Position | What it says about the topology vocabulary |
|---|---|---|
| **ADR-D4** (v1.1) | **Highest — foundational decision** | §Decision item 1 and §1.1 taxonomy table name the six patterns: *single-threaded linear / orchestrator-workers / decentralized-handoff / hierarchical-delegation / evaluator-optimizer / parallelization*. §1.5 `topology_pattern` axis lists the identical set. This is the **spec vocabulary**. |
| ADD v1.3 §3.1.2 | Below ADR | Cited by both C-CP-10 and ADR-D4 as the synthesis section; consistent with the ADR-D4 taxonomy. |
| PRD v1.1 | Below ADD | R-CP-08 ("multi-agent topology selectable at workflow definition") — concept-level, vocabulary-neutral. |
| **Spec C-CP-10 §10.1** (v1.2; preserved verbatim into v1.3 per the v1.3 change-note) | Per-axis spec | Six values = the spec vocabulary above. **Conforms to ADR-D4.** |
| **Plan U-CP-22** (v2.1; preserved verbatim into v2.3) | **Lowest — execution authority only** | `SINGLE_AGENT / SEQUENTIAL_HANDOFF / PARENT_FANOUT_AGGREGATE / RECONCILER_MESH / ROUTER_DELEGATE / PIPELINE_STAGES`. **Diverges from both the spec directly above it and the ADR at the top of the chain.** |

The divergence runs **plan vs (spec ∧ ADD ∧ ADR)**. The plan is alone, and it is the lowest artifact on the chain. Treating the plan's vocabulary as canonical would be an authority-chain inversion (SKILL §5 anti-pattern; `CLAUDE.md` §1.3).

---

## 3. §2-discipline analysis

- **Five-axis decomposition:** Pure **control-plane** concern (orchestration topology / sub-agent fan-out / hand-off mechanics). Single-axis — no cross-axis tension; the divergence is contained.
- **Probabilistic-deterministic boundary:** `TopologyPattern` is a closed enum consumed by deterministic dispatch — the admissibility predicate `is_admissible`, the manifest validator, U-CP-23's permitted-pattern set, U-CP-25's 2D matrix, and sub-agent dispatch. It sits squarely on the **deterministic side**. An enum on the deterministic side must have **one canonical spelling**: every consumer string-matches or type-matches against it. Two vocabularies in the substrate is a latent defect that surfaces as silent mismatch at every U-CP-22-dependent unit (U-CP-23, U-CP-25, U-CP-32, U-CP-34-area, U-CP-43, U-CP-50, U-CP-52 — the plan lists U-CP-22 as an input to all of them).
- **Decision ordering:** The topology taxonomy is a **foundational (F-level)** commitment — ADR-D4 §Decision item 1, constraining all of CP Cluster 4 + Cluster 5. An F-level divergence is the severe class (SKILL §4A.2 step 3). It is not a free implementation choice the plan was entitled to make.
- **Closed-taxonomy clause:** Spec §10.1 states the taxonomy is "closed at D4 §1.1; extension is a Workflow §4.1.2 Class-2 D4 revision." The plan **renaming** the six values is functionally a taxonomy edit made outside that revision channel — i.e. a silent design drift at the plan layer (`CLAUDE.md` X-AL-3 / invariant I-2 territory: no H_T design extension at the execution/plan layer).

---

## 4. Recommendation

**Adopt the spec C-CP-10 §10.1 vocabulary for U-CP-22's `TopologyPattern` enum.** Discard the plan's `SINGLE_AGENT / SEQUENTIAL_HANDOFF / PARENT_FANOUT_AGGREGATE / RECONCILER_MESH / ROUTER_DELEGATE / PIPELINE_STAGES` vocabulary.

Canonical six values (concepts fixed by ADR-D4 §1.1 and Spec §10.1; casing per the implementation's enum convention):

```
SINGLE_THREADED_LINEAR
ORCHESTRATOR_WORKERS
DECENTRALIZED_HANDOFF
HIERARCHICAL_DELEGATION
EVALUATOR_OPTIMIZER
PARALLELIZATION
```

This matches the spec's six string literals one-to-one and matches the CLAUDE.md §1 / CP-AL-1 concept set. (CLAUDE.md §1's exact tokens — `ROUTING`, `SEQUENTIAL_PIPELINE` — differ in spelling from the spec; the **spec §10.1 string values are canonical for the enum**, since CLAUDE.md §1 is framing prose, not the contract. The spec sits above the plan and is the contract artifact for C-CP-10.)

Casing: the **concepts** are spec-bound and non-negotiable. Kebab-case vs SCREAMING_SNAKE is genuine implementation discretion (spec §10.2 uses kebab string literals; the plan and CLAUDE.md use SCREAMING_SNAKE for the enum identifiers). Pick one and apply it uniformly across the CP axis — recommend SCREAMING_SNAKE for the Python `enum` members with kebab-case `value` strings where the value is serialized into the manifest/`topology.*` OTel attribute, so the on-the-wire form stays spec-§10.2-exact. Whichever is chosen, the **six concepts and the spec's serialized strings** are the load-bearing part and must not be altered.

`CascadePolicy`: same resolution — adopt the spec §10.3 three-value taxonomy (`pause` / `proceed` / `cascade-cancel`); discard the plan's `COMPLETE_ALL / CANCEL_ON_FIRST_FAIL / PAUSE_ON_FIRST_FAIL`.

### Downstream artifacts that must absorb the resolution (not edited here — `implementation-planner` / `spec-writer` work, post-sign-off)

1. **`Implementation_Plan_Control_Plane_v2_1.md` (and the verbatim-carried v2.2 / v2.3) — U-CP-22 signature block:** replace the `TopologyPattern` and `CascadePolicy` enum bodies with the spec vocabulary. The plan's acceptance criterion #1 ("six values per C-CP-10 §10.1 verbatim") then becomes *true* — currently it is false.
2. **U-CP-22 acceptance criterion #3** references the patterns by the plan's names (`SEQUENTIAL_HANDOFF`, `PARENT_FANOUT_AGGREGATE`, `RECONCILER_MESH`, `ROUTER_DELEGATE`, `PIPELINE_STAGES`) inside the admissibility-matrix description. Rewrite against the spec §10.3 admissibility text (`hierarchical-delegation` / `decentralized-handoff` / `parallelization` admissibility). Note: the plan's per-pattern admissibility assignment must also be reconciled against spec §10.3, which is keyed to *different* pattern names — the admissibility logic, not just the labels, needs a conforming re-derivation.
3. **U-CP-22 test names** (`test_topology_pattern_cardinality_six`, etc.) are cardinality/closure tests — unaffected by the rename, but `test_admissibility_per_workload_class_match_spec` must assert against spec §10.3.
4. **Every U-CP-22-dependent plan unit** that names `TopologyPattern` in its Inputs/Signatures — U-CP-23, U-CP-25, U-CP-32, U-CP-43, U-CP-50, the fanout-close unit, plus the §[traceability] map (plan lines ~3447-3449) — inherits the corrected vocabulary automatically once U-CP-22 is conformed, provided they reference the type symbolically (they do).
5. No spec edit required: **the spec is already correct.** No ADR edit required: **ADR-D4 is already correct.**

---

## 5. Tiebreaker check — CONFIRMED

The single verifiable fact that makes this recommendation determinate: *does any ADR-D4 / spec C-CP-10 revision postdating the plan adopt the plan's vocabulary?*

**Confirmed negative.** ADR-D4 is at v1.1 and uses the spec vocabulary. `Spec_Control_Plane_v1_3.md`'s change-note explicitly states "§10 C-CP-10 through §22 C-CP-22 ... preserved verbatim from v1.2" — so the latest spec still carries the spec vocabulary. `Implementation_Plan_Control_Plane_v2_3.md` states "U-CP-22 through U-CP-55 preserved verbatim from v2.2" — so the plan's divergent vocabulary persists unrevised into the latest plan and was never reconciled. No revision anywhere in the chain ratifies the plan's names. The recommendation is determinate.

(Note for the operator: `CLAUDE.md` §2.3/§2.4 cite **Spec v1.3** and **Plan v2.3** as the canonical versions, not the v1.2/v2.1 files named in the task prompt. Because v1.3 and v2.3 carry §10 / U-CP-22 *verbatim* from the earlier versions, the resolution is identical against either pair — but the fix should be applied to the **canonical v1.3 spec is already correct; the canonical v2.3 plan needs the U-CP-22 edit**, and the v2.1/v2.2 plan files should be treated as superseded per `Canonical_Substrate_Inventory.md` disambiguation.)

---

## 6. Fork classification (`Project_Workflow_v1_8.md` §2.7.6)

**Class 1 — halt-execution, design/plan artifact requires revision.** The Phase-6 plan artifact (U-CP-22) contradicts the Phase-5 spec and the Phase-3 ADR above it; the plan must be revised to conform before U-CP-22 can be correctly landed.

Scope of the halt is **narrow**: U-CP-22 and its dependent CP Cluster 4 / Cluster 5 units that consume `TopologyPattern` / `CascadePolicy`. CP-axis units that do not touch the topology enum are unaffected and may proceed. Per the workspace memory note "design-phase back-flow deprecated 2026-05-15; design-substrate/ is now canonical; spec edits in-CLI" — this is resolved **in-CLI**: no external design-phase round-trip. Track it as a `Phase_7_Class_N_Tension_NNN` record (Class 1 disposition), apply the plan edit via `implementation-planner`, record the clearing decision, then resume U-CP-22.

This is a plan-conforms-to-chain correction, **not** a re-decision of the topology taxonomy and **not** an H_T design extension — the design (ADR-D4 + spec C-CP-10) is unchanged and was always correct.

---

## 7. One-line answer for the operator

**Use the spec C-CP-10 §10.1 vocabulary.** The plan's enum is the lowest artifact on the authority chain and is alone in diverging — its own acceptance criterion #1 demands "§10.1 verbatim" yet lists non-§10.1 values, so conforming U-CP-22 to the spec makes the plan *self-consistent* as well as chain-consistent. The spec and ADR-D4 need no change; U-CP-22's enum bodies and acceptance criterion #3 do.

---

*operator decides — this is a recommendation per systems-architect SKILL §4A.4. No repository files were modified in producing this record.*
