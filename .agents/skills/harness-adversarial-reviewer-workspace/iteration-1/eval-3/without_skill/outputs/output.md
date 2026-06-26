# Review — Phase 7 Class 1 Tension Record 002 (TopologyPattern Enum Divergence)

## Verdict

**The Class 1 classification holds.** U-CP-22 cannot be implemented as written: its
plan signature contradicts its own acceptance criterion #1 ("enum per C-CP-10 §10.1
verbatim") because the plan signature is *not* verbatim from the cited spec section.
Resolving this requires a design-authority decision (pick the canonical vocabulary)
plus multi-artifact revision — that is the definition of a non-determinate,
halt-execution fork. The record's reasoning at §3 is correct.

The verification below confirms every load-bearing factual claim in the record against
primary sources, flags one overstatement that does not change the classification, and
surfaces one additional defect of the same class that the record missed.

---

## 1. Claims verified against primary sources

| Record claim | Verified | Source |
|---|---|---|
| Plan v2.1→v2.3 preserves U-CP-22 signature verbatim as Set 1 | ✅ | `Implementation_Plan_Control_Plane_v2_1.md` L1185–1192 declares `SINGLE_AGENT, SEQUENTIAL_HANDOFF, PARENT_FANOUT_AGGREGATE, RECONCILER_MESH, ROUTER_DELEGATE, PIPELINE_STAGES`. v2.2/v2.3 explicitly state "U-CP-22 through U-CP-55 preserved verbatim from v2.2" (v2.3 L364). |
| Spec v1.3 preserves §10 verbatim from v1.2 = Set 2 | ✅ | `Spec_Control_Plane_v1_3.md` L36 + L227–229 ("§10 C-CP-10 ... preserved verbatim from v1.2"). `Spec_Control_Plane_v1_2.md` §10.1 table declares `single-threaded-linear, orchestrator-workers, decentralized-handoff, hierarchical-delegation, evaluator-optimizer, parallelization`. |
| CP-AL-1 carries Set 3 in three workspace docs verbatim | ✅ | Root `CLAUDE.md` §5, `harness-cp/CLAUDE.md` L168, `Sub_Agent_Boundary_Specification_v1.md` L142 — all give `ORCHESTRATOR_WORKERS / DECENTRALIZED_HANDOFF / EVALUATOR_OPTIMIZER / PARALLELIZATION / ROUTING / SEQUENTIAL_PIPELINE`. |
| Acceptance #1 cites "C-CP-10 §10.1 verbatim"; plan signature is not verbatim from it | ✅ | Plan v2.1 L1205 acceptance #1; the cited §10.1 vocabulary (Set 2) does not match the plan's Set 1. The self-contradiction is real. |
| Semantic admissibility divergence (not just naming) | ✅ | Plan acceptance #3 (v2.1 L1207): `SEQUENTIAL_HANDOFF`/`PARENT_FANOUT_AGGREGATE` admissible for all four classes, etc. Spec §10.3 gives a different set: `hierarchical-delegation` at software-engineering+research, `decentralized-handoff` at pipeline-automation, `parallelization` at research+content-creation. Plan and spec disagree on which patterns are admissible where. |
| Authority chain: spec canonical over plan; Set 2 traces to ADR-D4 | ✅ | `CLAUDE.md` §1.3 authority chain. Spec §10 "ADR commitment(s) honored" cites ADR-D4 v1.1 §1.1; `ADR-D4.md` §1.1 "Six-pattern topology taxonomy" table is Set 2 vocabulary (single-threaded-linear, orchestrator-workers, ...). |
| Tiebreaker: confirm no ADR-D4 later than v1.1 | ✅ | `ADR-D4.md` is at v1.1 (Revision line: "v1 → v1.1", 2026-05-10). No later version filed in `design-substrate/`. The tiebreaker resolves to Set 2 — it does **not** invert the recommendation. |

The record's §4 authority-chain reading and recommended direction (adopt Set 2;
revise plan signature + acceptance #1 + acceptance #3; reconcile CP-AL-1) are sound.

---

## 2. One overstatement (does not change the classification)

§2 states the three sets "are not reconcilable by case/format normalization" and
"Set 1 shares no member with either." That is true at the literal-string level, but
it flattens an important relationship:

- **Set 3 (CP-AL-1) is a casing rewrite of Set 2, not an independent third design.**
  CP-AL-1's own text and `Sub_Agent_Boundary_Specification_v1.md` §5.2.2 explicitly
  anchor Set 3 to "the full 6-class enum + admissibility predicate + CascadePolicy
  **per C-CP-10 §10**." Set 3 is downstream of, and definitionally bound to, the spec.
  Its members (`ORCHESTRATOR_WORKERS`, `DECENTRALIZED_HANDOFF`, `EVALUATOR_OPTIMIZER`,
  `PARALLELIZATION`) are the SCREAMING_SNAKE_CASE form of Set 2 members; `ROUTING` and
  `SEQUENTIAL_PIPELINE` are loose renamings of `single-threaded-linear` and an F1-layer
  concept — sloppy, but derivative.

Consequence: the genuine reconciliation surface is **plan (Set 1) vs spec (Set 2)**.
The CLAUDE.md / Sub_Agent / harness-cp docs (Set 3) need only a casing-normalization
pass to Set-2 vocabulary, not a substantive design reconciliation. This tightens §4
step 3 but does not weaken the Class 1 classification — the plan-vs-spec contradiction
alone is sufficient to halt.

---

## 3. Additional defect the record missed (same class, same resolution event)

The record analyzes only `TopologyPattern`. U-CP-22's signature also declares
`CascadePolicy`, and it has the **same defect** — arguably worse:

- **Value divergence.** Plan U-CP-22 declares `CascadePolicy { COMPLETE_ALL,
  CANCEL_ON_FIRST_FAIL, PAUSE_ON_FIRST_FAIL }` (v2.1 L1194–1198). The spec's
  cascade-policy enum is `{ pause, proceed, cascade-cancel }` (`Spec_Control_Plane_v1_2.md`
  §10.2 L857; also TopologyDeclaration). These are entirely different vocabularies,
  with no overlap.
- **Citation defect.** Plan acceptance #2 requires `CascadePolicy` declared "per
  C-CP-10 §10.3 verbatim." But spec §10.3 is "Cross-pattern admissibility per workload
  class" and contains **no `CascadePolicy` enum at all**. The cascade-policy values live
  in spec §10.2 (TopologyDeclaration) and trace to ADR-D5 §1.3.1
  (`cascade_policy ∈ {pause, proceed, cascade-cancel}`). The acceptance criterion cites
  a section that does not contain the thing it claims to be verbatim from.

This is the same root cause (U-CP-22 signature non-verbatim against its cited spec
sections) and resolves through the same event. It does not create a separate fork —
it must be folded into Tension 002's resolution scope.

---

## 4. Recommended resolution scope (additions to record §4)

The record's §4 direction is sound. Augment it with:

1. **CascadePolicy**: adopt the spec vocabulary `{ pause, proceed, cascade-cancel }`
   (ADR-D5 §1.3.1 / spec §10.2) as canonical; revise the plan U-CP-22 `CascadePolicy`
   signature and acceptance #2 accordingly.
2. **Citation correction**: fix plan acceptance #2's citation from "C-CP-10 §10.3" to
   "C-CP-10 §10.2" (the section that actually carries cascade-policy).
3. **§4 step 3 scope note**: the CLAUDE.md / harness-cp/CLAUDE.md / Sub_Agent §5.1
   reconciliation is a casing-normalization to Set-2 vocabulary, not a substantive
   re-decision (per §2 above).

---

## 5. Summary table

| Aspect | Assessment |
|---|---|
| Class 1 classification | **Holds.** Self-contradicting acceptance #1; non-determinate; multi-artifact revision required. |
| Detection unit / halt point | Correct — U-CP-22, surfaced before code execution. |
| Three-set factual claims | All verified against primary sources. |
| Authority-chain reading (Set 2 canonical) | Correct; ADR-D4 v1.1 is latest, tiebreaker resolves to Set 2. |
| Semantic admissibility divergence | Verified — plan acceptance #3 vs spec §10.3 genuinely disagree. |
| Overstatement | "Set 1 shares no member" flattens that Set 3 is a casing rewrite of Set 2; reconciliation surface is plan-vs-spec only. |
| Missed defect | `CascadePolicy` value divergence + §10.3 citation error — same class, same resolution event. |
| Sibling assessment (§6) | Not re-verified in depth; out of scope for this review of the classification. |

The record correctly identifies and classifies the fork. It should be amended to add
the `CascadePolicy` defect before the operator resolution is authorized, so that one
resolution event closes the whole of U-CP-22 rather than leaving a second
verbatim-citation defect latent.
