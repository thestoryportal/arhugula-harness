# Phase 7 — Class 1 Tension 002 — TopologyPattern Enum Divergence — Architectural Resolution Recommendation

*Tension-resolution-mode output (systems-architect SKILL §4A). Produced for the
operator to decide. This skill recommends; it does not decide, does not edit the
spec/plan/ADR/CLAUDE.md, and does not extend the H_T design. Appendix-shape for
`Phase_7_Class_1_Tension_002_Topology_Pattern_Enum.md` — not written into that
record (task constraint: no repository file edits).*

---

## §A — Tension stated precisely (three divergent sources, quoted)

`U-CP-22` (Phase 7 sub-phase 7b atomic unit — "Declare 6-pattern `TopologyPattern`
enum + admissibility predicate") cannot be implemented: its own acceptance #1
requires the enum "per **C-CP-10 §10.1 verbatim**," but three canonical-corpus
artifacts give three mutually irreconcilable 6-name enumerations. All three quotes
are verified against the `design-substrate/` files directly.

**Set 1 — CP plan U-CP-22 signature.**
`design-substrate/Implementation_Plan_Control_Plane_v2_1.md` §2, U-CP-22
**Signatures** block (line 1186), body preserved verbatim through v2.2 → v2.3
(`Implementation_Plan_Control_Plane_v2_3.md` line 364: "U-CP-22 through U-CP-55
preserved verbatim from v2.2"):

> ```
> enum TopologyPattern {
>   SINGLE_AGENT,
>   SEQUENTIAL_HANDOFF,
>   PARENT_FANOUT_AGGREGATE,
>   RECONCILER_MESH,
>   ROUTER_DELEGATE,
>   PIPELINE_STAGES
> }
> ```

**Set 2 — CP spec C-CP-10 §10.1.**
`design-substrate/Spec_Control_Plane_v1_2.md` §10.1 "Six-pattern topology
taxonomy" (lines 834–847), preserved verbatim into `Spec_Control_Plane_v1_3.md`
(§10 line 229: "[All sub-sections preserved verbatim from v1.2.]"):

> | 1 | `single-threaded-linear` | ... |
> | 2 | `orchestrator-workers` | ... |
> | 3 | `decentralized-handoff` | ... |
> | 4 | `hierarchical-delegation` | ... |
> | 5 | `evaluator-optimizer` | ... |
> | 6 | `parallelization` | ... |

**Set 3 — root `CLAUDE.md` §5 / CP-AL-1.** Verbatim text sourced from
`design-substrate/Phase_7_Meta_Architecture_v1.md` §7.4 (line 530), mirrored at
root `CLAUDE.md` §5, `harness-cp/CLAUDE.md` §4.2, and
`Sub_Agent_Boundary_Specification_v1.md` §5.1:

> H_T TopologyPattern 6-class enum (ORCHESTRATOR_WORKERS / DECENTRALIZED_HANDOFF /
> EVALUATOR_OPTIMIZER / PARALLELIZATION / ROUTING / SEQUENTIAL_PIPELINE)

The three sets are **not reconcilable by case/format normalization** — they are
distinct vocabularies. Set 2 ∩ Set 3 (semantic, ignoring casing) =
{orchestrator-workers, decentralized-handoff, evaluator-optimizer,
parallelization}; Set 2 \ Set 3 = {single-threaded-linear, hierarchical-delegation};
Set 3 \ Set 2 = {ROUTING, SEQUENTIAL_PIPELINE}. Set 1 shares **no member** with
either Set 2 or Set 3.

The divergence is also **semantic, not only naming.** U-CP-22 acceptance #3 gives
an admissibility matrix in Set-1 vocabulary; spec C-CP-10 §10.3 (lines 865–887)
gives a different admissibility set in Set-2 vocabulary. They disagree on *which
patterns are admissible at which workload classes*, not only on names.

**Secondary defect surfaced in the same surface — `CascadePolicy`.** U-CP-22
acceptance #2 requires `CascadePolicy` "per C-CP-10 §10.3 verbatim." Two faults:
(a) §10.3 is the admissibility section — it contains no `CascadePolicy` enum; the
3-value `cascade_policy` set lives in §10.2's `TopologyDeclaration` schema
(`"pause" | "proceed" | "cascade-cancel"`); the citation is wrong. (b) The plan's
own values — `COMPLETE_ALL` / `CANCEL_ON_FIRST_FAIL` / `PAUSE_ON_FIRST_FAIL` —
diverge from the spec's `pause` / `proceed` / `cascade-cancel`. This is the same
class of plan-signature-vs-spec divergence and must be resolved with the primary
tension, or U-CP-22 cannot be conformed coherently.

---

## §B — Per-artifact placement on the canonical authority chain

`CLAUDE.md` §1.3 authority chain: **ADR (F1–F5 + D1–D6) → ADD v1.3 → PRD v1.1 →
per-axis spec v1.x → per-axis plan v2.x + CXA v2.1.** The earlier artifact is
canonical for the later. The highest artifact that speaks to the tension
determines the canonical reading.

| Source | Artifact | Chain position | Speaks to the tension? |
|---|---|---|---|
| **ADR-D4 v1.1** §1.1 "Six-pattern topology taxonomy" (line 58 + §1.1 table line 67) | `design-substrate/ADR-D4.md` | **Highest** — Foundational/Derivative ADR layer; Status: **Accepted**, P3c-CK final clearance 2026-05-11; **no version later than v1.1 exists** | **Yes** — D4 §1.1 commits "(single-threaded linear / orchestrator-workers / decentralized-handoff / hierarchical-delegation / evaluator-optimizer / parallelization) as the harness-canonical pattern enumeration." This is **Set 2.** |
| **CP spec C-CP-10 §10.1** | `Spec_Control_Plane_v1_2.md` / preserved verbatim in `_v1_3.md` | per-axis spec layer (below ADR) | **Yes** — names Set 2 verbatim; §10.1 states "closed at D4 §1.1"; §10.3 cites "ADR-D4 v1.1 §1.2 admissibility annotations." Spec **conforms to ADR-D4.** |
| **CP plan U-CP-22** (Set 1) | `Implementation_Plan_Control_Plane_v2_1.md` (verbatim → v2.3) | per-axis plan layer (lowest) | **Diverges from its own cited authority.** Acceptance #1 claims "C-CP-10 §10.1 verbatim"; the signature is not verbatim from §10.1, nor from ADR-D4 §1.1. |
| **CP-AL-1** (Set 3) | `Phase_7_Meta_Architecture_v1.md` §7.4; mirrored `CLAUDE.md` §5, `harness-cp/CLAUDE.md` §4.2, `Sub_Agent_Boundary_Specification_v1.md` §5.1 | **Off-chain** — Phase 7 *governance/anti-leakage* artifact, not a design-chain artifact. Governance conforms to the design chain, not vice versa. | **Diverges** — its parenthetical enumeration matches neither ADR-D4 §1.1 nor C-CP-10 §10.1. |

**Reading.** The authority chain is **clean and unanimous** at its top two layers:
ADR-D4 v1.1 §1.1 (the highest artifact that speaks to the tension) and CP spec
C-CP-10 §10.1 both name **Set 2**, and the spec explicitly cites D4 as its source.
Set 1 (plan) and Set 3 (CP-AL-1 governance) each diverge from the artifact they
are supposed to conform to. This is **not a design gap and not a re-decision** —
it is two downstream artifacts that drifted from a settled, Accepted ADR
commitment. Resolution = conform the divergent artifacts to the chain.

---

## §C — §2 cross-mode discipline analysis

**Five-axis decomposition.** This is a **Control-plane-axis** concern
(orchestration topology — the topology-pattern taxonomy that drives sub-agent
fan-out, cascade behaviour, and parallel-branch coordination). It touches the
**operational-discipline** axis only at the cross-axis seam already covered by
ADR-D4 §1.3/§1.6 (per-engine-class fault-handling) — that seam is not in tension
here; the tension is confined to the CP-axis enum vocabulary. No information-
substrate, action-surface, or deployment-surface axis is implicated.

**Probabilistic-deterministic boundary.** The `TopologyPattern` enum sits squarely
on the **deterministic side** — it is a closed schema/type, consumed by the
deterministic `is_admissible` predicate and by the C-CP-06 workflow-manifest
validation gate. Reliability here is delivered by the *enum being a single
canonical closed set* across spec, plan, and governance. Three divergent
vocabularies is a deterministic-layer defect: a manifest validator built against
Set 1 would reject a manifest authored against Set 2. The fix must produce one
byte-exact vocabulary across all three loci.

**Decision ordering (F / D / I).** The topology taxonomy is **Foundational-grade
within the CP axis** — ADR-D4 §1.1 explicitly names it "the harness-canonical
pattern enumeration," and §10.1 declares the taxonomy "closed at D4; extension is
a Workflow §4.1.2 Class-2 D4 revision." Downstream D4 units (CP plan Clusters 4–5,
U-CP-23 onward) and the C-CP-06 manifest schema all consume `TopologyPattern` as a
discriminator. An F-grade divergence is **more severe** than a derivative one: the
divergence cannot be absorbed locally at U-CP-22 — it propagates to every unit
that references the enum. This is what makes the fork Class 1 (halt-execution).

**Cross-axis verification.** No CP↔OD / CP↔IS / CP↔AS contradiction is introduced
by adopting Set 2 — Set 2 *is* the vocabulary the spec already uses at C-CP-11,
C-CP-13 §13.2 (brief object "for orchestrator-workers cells"), and C-CP-10 §13.5;
the rest of the CP spec is already internally consistent with Set 2. Conforming
the plan and CP-AL-1 to Set 2 *removes* cross-artifact drift rather than
introducing it.

---

## §D — Recommended reading (operator decides)

**Recommendation: adopt Set 2 — the CP spec C-CP-10 §10.1 six-pattern taxonomy —
as the canonical `TopologyPattern` enumeration.**

> `single-threaded-linear`, `orchestrator-workers`, `decentralized-handoff`,
> `hierarchical-delegation`, `evaluator-optimizer`, `parallelization`

**Chain citation.** `CLAUDE.md` §1.3 (ADR → ADD → PRD → spec → plan; earlier
canonical for later). The highest artifact speaking to the tension —
**ADR-D4 v1.1 §1.1**, Status Accepted, P3c-CK-cleared 2026-05-11 — names Set 2
verbatim ("six-pattern topology taxonomy ... as the harness-canonical pattern
enumeration"). **CP spec C-CP-10 §10.1** conforms to D4 and names Set 2 verbatim.
Set 1 (plan) and Set 3 (CP-AL-1) are both downstream/off-chain artifacts that
diverged from the Accepted ADR commitment; the canonical resolution is to conform
them, not to re-decide.

**`CascadePolicy` sub-recommendation.** Adopt the spec §10.2 `TopologyDeclaration`
3-value set — `pause` / `proceed` / `cascade-cancel` — as the canonical
`CascadePolicy` vocabulary, and correct U-CP-22 acceptance #2's citation from
"§10.3" to "§10.2". (`pause/proceed/cascade-cancel` also matches ADR-D4's
`cascade_policy` parameter and ADR-D5 §1.3.1 `cascade_policy ∈ {pause, proceed,
cascade-cancel}`.)

---

## §E — Tiebreaker check

The recommendation is determinate **iff** ADR-D4 has no version later than v1.1
that re-anchors the canonical taxonomy.

**Status: CONFIRMED determinate.** `design-substrate/ADR-D4.md` is at **v1.1**
(Status block: "Revision: v1 → v1.1"; closing footer: "Filed v1 2026-05-10 ...
Revised v1.1 2026-05-10"). It is **Accepted** (P3c-CK final clearance 2026-05-11).
No `ADR-D4_v1_2.md` or higher exists in `design-substrate/` (the directory holds
`ADR-D4.md` only; siblings `ADR-D1_v1_2.md` and `ADR-D6_v1_2.md` show the v1.2
naming convention is used when a v1.2 exists — D4 has none). ADR-D4 v1.1 §1.1
names Set 2. The tiebreaker resolves **in favour of Set 2**; there is no later D4
that would invert the resolution to Set 1 or Set 3.

**Load-bearing-artifact flag — requires explicit operator sign-off.** CP-AL-1 is
named in `CLAUDE.md` §5 as "the most load-bearing rule at the H_E ↔ H_T
boundary." The recommendation requires editing CP-AL-1's verbatim text at its
source (`Phase_7_Meta_Architecture_v1.md` §7.4) and at three mirror sites. Per
SKILL §4A.2 step 5, a resolution touching a load-bearing anti-leakage rule
**requires explicit operator sign-off** before any artifact is edited. Note: the
"load-bearing" status cuts toward *more cleanup*, not toward treating Set 3 as
canonical — CP-AL-1 is Phase 7 governance and conforms to the design chain, not
the reverse. CP-AL-1's *anti-leakage semantics* (H_E sub-agent topology ≠ H_T
TopologyPattern enum) are unaffected — only the parenthetical enumeration changes.

---

## §F — Fork classification (`Project_Workflow_v1_8.md` §2.7.6)

**Class 1 — halt-execution.** The defect is architectural: U-CP-22's plan
signature cannot be materialized in a way that satisfies its own acceptance #1
against the cited spec, and resolution requires multi-artifact revision (a design-
chain plan unit + an off-chain anti-leakage rule at four loci). Per `CLAUDE.md`
§4.3 and I-5, **Phase 7 sub-phase 7b execution for U-CP-22 is halted** until the
operator selects the canonical enumeration and authorizes the revisions.

Not Class 2 (the authority chain is determinate — this is not a choice between
substantive alternatives; it is conform-to-chain). Not Class 3 (it blocks a unit).
The "design-authority decision" framing in the tension record §3 is the operator's
**confirmation and revision-authorization** act, not an open architectural choice —
the chain has already decided; the operator ratifies and authorizes.

---

## §G — Artifact-revision inventory (for `spec-writer` / `implementation-planner`, after sign-off)

This skill does **not** edit these — listed so the operator can scope the
revision work. Revisions are sequenced *after* operator sign-off.

| # | Artifact | Locus | Revision | Owner role |
|---|---|---|---|---|
| 1 | `Implementation_Plan_Control_Plane_v2_3.md` (+ verbatim-source v2.1/v2.2) | U-CP-22 **Signatures** — `enum TopologyPattern` | Replace Set-1 6 values with Set-2: `single-threaded-linear`, `orchestrator-workers`, `decentralized-handoff`, `hierarchical-delegation`, `evaluator-optimizer`, `parallelization` | `implementation-planner` |
| 2 | same | U-CP-22 **Signatures** — `enum CascadePolicy` | Replace `COMPLETE_ALL` / `CANCEL_ON_FIRST_FAIL` / `PAUSE_ON_FIRST_FAIL` with spec §10.2 `pause` / `proceed` / `cascade-cancel` | `implementation-planner` |
| 3 | same | U-CP-22 **acceptance #1** | Now satisfiable — enum is genuinely "per C-CP-10 §10.1 verbatim" once #1 applied | `implementation-planner` |
| 4 | same | U-CP-22 **acceptance #2** | Correct citation `§10.3` → `§10.2` (the `cascade_policy` set lives in §10.2's `TopologyDeclaration`, not in §10.3); align values to §10.2 | `implementation-planner` |
| 5 | same | U-CP-22 **acceptance #3** + `test_admissibility_per_workload_class_match_spec` / `test_pipeline_stages_pipeline_only` | Rewrite admissibility matrix from Set-1 vocabulary to spec **C-CP-10 §10.3** (hierarchical-delegation @ software-engineering + research; decentralized-handoff @ pipeline-automation; parallelization @ research + content-creation). Plan and spec currently disagree on admissibility *content*, not only names | `implementation-planner` |
| 6 | `Phase_7_Meta_Architecture_v1.md` §7.4 | CP-AL-1 verbatim parenthetical (**Set-3 source of truth**) | Replace `(ORCHESTRATOR_WORKERS / DECENTRALIZED_HANDOFF / EVALUATOR_OPTIMIZER / PARALLELIZATION / ROUTING / SEQUENTIAL_PIPELINE)` with the Set-2 vocabulary. Anti-leakage *semantics* unchanged | `spec-writer` (governance-artifact revision) — **operator sign-off required** |
| 7 | root `CLAUDE.md` §5 | CP-AL-1 mirror | Conform parenthetical to Set 2 | `spec-writer` — operator sign-off required |
| 8 | `harness-cp/CLAUDE.md` §4.2 | CP-AL-1 mirror | Conform parenthetical to Set 2 | `spec-writer` — operator sign-off required |
| 9 | `Sub_Agent_Boundary_Specification_v1.md` §5.1 | CP-AL-1 mirror | Conform parenthetical to Set 2 | `spec-writer` — operator sign-off required |

**No spec revision required.** C-CP-10 §10.1/§10.2/§10.3 and ADR-D4 v1.1 §1.1
already name Set 2 and are mutually consistent — they are the canonical reading,
not divergent artifacts. Verify byte-exact citation discipline
(`Project_Workflow_v1_8.md` §7.4.2) at every edited locus during application.

**Downstream propagation note.** Units U-CP-23 onward (CP plan Clusters 4–5) and
any unit consuming `TopologyPattern` as a discriminator inherit the Set-2
vocabulary automatically once item 1 lands; `implementation-planner` should sweep
Clusters 4–5 for any other Set-1-vocabulary residue introduced alongside U-CP-22.

---

## §H — Operator decision marker

> **OPERATOR DECIDES.** This document is a *recommendation* produced under
> systems-architect SKILL §4A tension-resolution discipline. It does not decide
> and does not edit any artifact. The operator must (1) confirm Set 2 as the
> canonical `TopologyPattern` enumeration, (2) confirm `pause/proceed/cascade-cancel`
> as the canonical `CascadePolicy` set, (3) explicitly sign off on the CP-AL-1
> load-bearing-anti-leakage-rule revision (inventory items 6–9), and (4) authorize
> the §G revision sequence. U-CP-22 implementation remains **halted** (Class 1)
> until that decision and authorization are recorded in the
> `Phase_7_Class_1_Tension_002_*` record §5 block.

*Sibling units U-CP-15, U-OD-01, U-OD-04 are unaffected by this tension and remain
independently implementable per the tension record §6.*
