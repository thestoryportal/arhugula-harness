# Spec-vs-Plan Cross-Check: U-CP-22 against C-CP-10 §10.1

**Verdict: NOT FAITHFUL. The plan unit U-CP-22 contradicts the spec contract it claims to implement on every substantive surface. This is a Class 1 fork (architectural defect — plan/spec divergence) and Phase 7 execution on U-CP-22 must halt and route to design-phase back-flow.**

---

## 1. Artifacts cross-checked

| Role | Artifact | Location |
|---|---|---|
| Plan unit | U-CP-22 — "Declare 6-pattern `TopologyPattern` enum + admissibility predicate" | `design-substrate/Implementation_Plan_Control_Plane_v2_1.md` §2, lines 1172–1212 |
| Spec contract | C-CP-10 — "Six-pattern multi-agent topology taxonomy" | `design-substrate/Spec_Control_Plane_v1_2.md` §10, lines 822–883 |

U-CP-22 declares `**Implements:** [C-CP-10 §10.1, §10.2, §10.3]`.

---

## 2. Finding F-1 (CRITICAL) — `TopologyPattern` enum values do not match the spec

U-CP-22 acceptance criterion 1 states: *"`TopologyPattern` declares exactly six values per C-CP-10 §10.1 **verbatim**."* The plan unit then declares:

```
SINGLE_AGENT, SEQUENTIAL_HANDOFF, PARENT_FANOUT_AGGREGATE,
RECONCILER_MESH, ROUTER_DELEGATE, PIPELINE_STAGES
```

C-CP-10 §10.1 (spec, line 838–845) declares a closed six-pattern taxonomy with these names:

```
single-threaded-linear, orchestrator-workers, decentralized-handoff,
hierarchical-delegation, evaluator-optimizer, parallelization
```

**Zero of the six names match.** Mapping the apparent intent:

| Spec §10.1 (canonical) | Plan U-CP-22 (declared) | Match? |
|---|---|---|
| `single-threaded-linear` | `SINGLE_AGENT` | NO |
| `orchestrator-workers` | `PARENT_FANOUT_AGGREGATE` (?) | NO |
| `decentralized-handoff` | `SEQUENTIAL_HANDOFF` (?) | NO |
| `hierarchical-delegation` | `ROUTER_DELEGATE` (?) | NO |
| `evaluator-optimizer` | `RECONCILER_MESH` (?) | NO |
| `parallelization` | `PIPELINE_STAGES` (?) | NO |

The mapping is not even reliably inferable — `RECONCILER_MESH` vs `evaluator-optimizer` and `PIPELINE_STAGES` vs `parallelization` are semantically unrelated. The acceptance criterion demands *verbatim* fidelity to §10.1; the plan unit fails its own criterion. The plan's enum names also collide conceptually with the root `CLAUDE.md` §1.1 table, which itself cites yet a third naming set (`ORCHESTRATOR_WORKERS / DECENTRALIZED_HANDOFF / EVALUATOR_OPTIMIZER / PARALLELIZATION / ROUTING / SEQUENTIAL_PIPELINE`) — three divergent name sets across three artifacts.

This is the worst failure mode named in root `CLAUDE.md` §4.3: silent absorption would propagate an invalid enum to every downstream consumer (U-CP-23, U-CP-24, U-CP-25, U-CP-43, U-CP-50, U-CP-52 plus cross-axis sub-agent dispatch — all cite `TopologyPattern` from U-CP-22).

## 3. Finding F-2 (CRITICAL) — `CascadePolicy` enum is not in C-CP-10 §10.1, §10.2, or §10.3

U-CP-22 declares `CascadePolicy` with values `COMPLETE_ALL / CANCEL_ON_FIRST_FAIL / PAUSE_ON_FIRST_FAIL` and acceptance criterion 2 cites *"C-CP-10 §10.3 verbatim."*

C-CP-10 §10.3 (spec, line 865–883) is titled **"Cross-pattern admissibility per workload class."** It contains no `CascadePolicy` enum. The only cascade-policy value set in C-CP-10 appears in §10.2's `TopologyDeclaration` schema (line 857): `cascade_policy : "pause" | "proceed" | "cascade-cancel"` — three values, but **different values and a different surface** from the plan's `COMPLETE_ALL / CANCEL_ON_FIRST_FAIL / PAUSE_ON_FIRST_FAIL`, and §10.2 explicitly attributes those to `C-CP-17 §17.1.1`, not to C-CP-10. The plan's claim that §10.3 declares a three-value `CascadePolicy` "verbatim" is false: §10.3 declares no enum at all.

## 4. Finding F-3 (CRITICAL) — section-citation mismatch; the "admissibility predicate" §10.2 reference is wrong

U-CP-22 claims it implements `§10.2 admissibility predicate` (signature comment line 1201; acceptance criterion 3 cites "§10.2 admissibility matrix").

The spec's section structure is:
- §10.1 — Six-pattern topology taxonomy
- §10.2 — **Workflow-definition surface declaration** (the `TopologyDeclaration` schema) — *not* an admissibility predicate
- §10.3 — **Cross-pattern admissibility per workload class** — this is where admissibility actually lives

The plan unit has §10.2 and §10.3 swapped: it sources the admissibility predicate from §10.2 (which is the manifest surface) and sources `CascadePolicy` from §10.3 (which is the admissibility section). Every section citation in U-CP-22 is misaligned by one.

## 5. Finding F-4 (MAJOR) — admissibility matrix in plan AC-3 is not derivable from §10.3

U-CP-22 acceptance criterion 3 asserts a specific admissibility matrix: *"SEQUENTIAL_HANDOFF and PARENT_FANOUT_AGGREGATE admissible for all four workload classes; RECONCILER_MESH admissible for content-creation + pipeline-automation; ROUTER_DELEGATE admissible for software-engineering + research; PIPELINE_STAGES admissible only for pipeline-automation."*

Spec §10.3 makes only three admissibility annotations (for `hierarchical-delegation`, `decentralized-handoff`, and `parallelization`), per ADR-D4 v1.1 §1.2:
- `hierarchical-delegation`: software-engineering + research
- `decentralized-handoff`: pipeline-automation
- `parallelization`: research + content-creation

§10.3 says nothing about the other three patterns (`single-threaded-linear`, `orchestrator-workers`, `evaluator-optimizer`) being "admissible for all four workload classes," and says nothing resembling "PIPELINE_STAGES admissible only for pipeline-automation." The plan's matrix is a fabricated specialization. Even attempting a charitable name-mapping, the plan's `ROUTER_DELEGATE → software-engineering + research` would correspond to spec `hierarchical-delegation → software-engineering + research` (plausible), but `RECONCILER_MESH → content-creation + pipeline-automation` does not correspond to spec `parallelization → research + content-creation`. The matrix cannot be reconciled.

## 6. Finding F-5 (MINOR) — `WorkloadClass` input dependency undeclared

`is_admissible(pattern: TopologyPattern, workload: WorkloadClass)` references a `WorkloadClass` type. U-CP-22 declares `**Depends on:** (none)` and `**Inputs:** None`. The four workload classes (`software-engineering / content-creation / pipeline-automation / research`) are a spec primitive (Persona §3.1, referenced throughout C-CP-11 §11.1). The unit either needs a dependency on whatever unit supplies `WorkloadClass`, or must declare the enum itself. As written, the signature references an undefined type.

---

## 7. What IS faithful

- The cardinality is correct: spec §10.1 declares a closed six-pattern taxonomy, and U-CP-22 declares six values. The *count* matches.
- The closure property is correctly carried: spec §10.1 line 836 ("closed... extension is a Workflow §4.1.2 Class-2 D4 revision") is faithfully reflected in plan AC-4 ("extension requires Workflow §4.1.2 Class-2 D4 revision").
- The intent — a foundational substrate-supplying enum unit with `Depends on: (none)` — is structurally consistent with the spec's role for C-CP-10 as a foundational taxonomy contract.

The faithfulness is purely structural. Every *content* surface (the six names, the cascade values, the section citations, the admissibility matrix) diverges.

---

## 8. Recommendation

**Halt U-CP-22 implementation. Route as a Class 1 fork** per root `CLAUDE.md` §4.3 and `Project_Workflow_v1_8.md` §2.7.6. The defect is plan/spec divergence — the plan unit cannot be implemented faithfully because implementing it "verbatim per §10.1" (as its own AC-1 demands) and implementing it "as written" produce contradictory artifacts.

Resolution requires a design-phase decision on the canonical name set, since three artifacts disagree:
1. Spec C-CP-10 §10.1: `single-threaded-linear / orchestrator-workers / decentralized-handoff / hierarchical-delegation / evaluator-optimizer / parallelization`
2. Root `CLAUDE.md` §1.1: `ORCHESTRATOR_WORKERS / DECENTRALIZED_HANDOFF / EVALUATOR_OPTIMIZER / PARALLELIZATION / ROUTING / SEQUENTIAL_PIPELINE`
3. Plan U-CP-22: `SINGLE_AGENT / SEQUENTIAL_HANDOFF / PARENT_FANOUT_AGGREGATE / RECONCILER_MESH / ROUTER_DELEGATE / PIPELINE_STAGES`

The spec (C-CP-10, P5-CK-cleared) sits above the plan in the authority chain (root `CLAUDE.md` §1.3), so the plan unit U-CP-22 — not the spec — is the artifact in error and must be revised: enum names corrected to §10.1 verbatim; `CascadePolicy` either removed (it is not a C-CP-10 surface) or re-sourced and re-cited to its actual home (`C-CP-17 §17.1.1` per spec §10.2 line 857); section citations §10.2/§10.3 de-swapped; AC-3 admissibility matrix rewritten to the three annotations actually present in §10.3; `WorkloadClass` input dependency declared.
