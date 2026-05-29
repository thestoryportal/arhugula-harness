# Class 1 Fork — Topology admissibility check: load-time enforced, runtime non-uniform; MVP-scope matrix excludes the only materialized topology for the most common workload

**Status:** ✅ APPLIED-AS-READING-A (operator-ratified 2026-05-29; Q-set Q1=A + Q2=α + Q3=i + Q4=c + Q5=β)

**Ratification record (2026-05-29):**

| Q | Decision | Disposition at apply arc |
|---|---|---|
| Q1 (resolution path) | **A — Relax loader; defer to runtime sub-agent-dispatch-time check** | Production `_check_topology_admissibility` retired at `workflow_manifest_loader.py:212`; import dropped; method removed. Runtime sub-agent-dispatch site (`sub_agent_dispatch.py:585`) is sole enforcement authority. Spec v1.37 → v1.38 + plan v2.39 → v2.40 absorbed at apply PR. |
| Q2 (fixture treatment) | **α — Switch fixture to `pipeline-automation` + `single-threaded-linear`** | Handled at sibling PR #79 apply arc (fixture sits at `harness-runtime/tests/integration/fixtures/track_b/minimal.yaml`; coupled with the YAML scalar coercion fix). |
| Q3 (site #585 enforcement scope) | **i — Confirm site #585 is sufficient** | At MVP scope, sub-agent dispatch is the only fan-out surface and admissibility is fan-out-shape correctness. Sufficient. Future arcs introducing topology-dependent dispatch surfaces SHOULD add admissibility check at each new fan-out site OR add a central enforcement site (Q3=ii deferred to operator-discretion). |
| Q4 (design substrate amendment scope) | **c — Runtime spec §14.19.4 invariant 2 canonical-reading amendment + plan U-RT-104 AC #12 retirement** | Spec v1.37 → v1.38 published this arc; plan v2.39 → v2.40 published this arc. NO CP spec amendment (matrix design-intent at C-CP-22 §11.1 preserved verbatim). |
| Q5 (cross-axis cascade) | **β — Runtime spec + plan cascade only** | Runtime spec v1.38 + runtime plan v2.40 + production code + tests + workspace `CLAUDE.md` §2.3 + §2.4 row bumps + clearance marker at `.harness/clearance/Spec_Harness_Runtime-v1_38-cleared-2026-05-29.md`. NO CP / AS / OD / IS / CXA / ADR / ADD / PRD touch. |

**Apply arc:** separate apply PR landing alongside this filing PR per workspace precedent at PR #66 apply-after-filing-#65.

**Filed at:** 2026-05-29

**Filer:** use-the-product probe (post-PR-#78 session; sibling fork to PR #79 `class_1_fork_yaml_loader_step_payload_scalar_coercion_gap`)

**Surfaced by:** End-to-end `harness run` probe at HEAD. Probe attempted `minimal.yaml` modified to `(software-engineering, single-threaded-linear)` (the only MVP-materialized topology). Loader REJECTED with `RT-FAIL-CLI-MANIFEST-ADMISSIBILITY: topology_pattern 'single-threaded-linear' is not admissible for workload_class 'software-engineering' per U-CP-22 is_topology_permitted_for_workload`. Empirical follow-up: the canonical integration test `test_track_b_e2e.py::test_ac1_real_anthropic_single_step_succeeds` uses **EXACTLY** `(SOFTWARE_ENGINEERING, SINGLE_THREADED_LINEAR)` and SUCCEEDS — by constructing a Protocol-conformant workflow object directly and calling `_run(...)`, bypassing the YAML loader entirely.

**Classification:** Class 1 (halt-execution; structural inconsistency between load-time admissibility enforcement and runtime-path enforcement, compounded by MVP-scope materialization gap).

---

## §1 — The gap

### §1.1 — Two enforcement sites, not three

`is_topology_permitted_for_workload(topology, workload)` (per U-CP-22 at `harness-cp/src/harness_cp/per_workload_class_topology.py:174`) is invoked at exactly TWO sites workspace-wide:

| Site | File:line | Trigger |
|---|---|---|
| Load-time | `harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py:392` (`_check_topology_admissibility` per AC #12) | YAML/TOML manifest load via `WorkflowManifestLoader.load(path)` |
| Sub-agent dispatch | `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:585` (`if not self.topology_dispatcher.is_topology_permitted(topology, workload)`) | `propose_sub_agent_dispatch(...)` invocation during workflow step execution |

**NOT invoked at:**
- `workflow_driver.execute_workflow` (the main per-step dispatch loop) — verified via grep at `harness-cp/src/harness_cp/workflow_driver.py`
- `harness_runtime.api.run` (the operator-facing entrypoint)
- Any bootstrap stage (verified at `harness-runtime/src/harness_runtime/bootstrap/`)

Consequence: a workflow with `topology_pattern=SINGLE_THREADED_LINEAR` + `workload_class=SOFTWARE_ENGINEERING` + step kind that does NOT dispatch sub-agents (e.g., `INFERENCE_STEP`) is rejected at YAML load BUT executes successfully if reached through a Protocol-conformant workflow object that bypasses the loader.

### §1.2 — The integration test exploits the bypass

`harness-runtime/tests/integration/test_track_b_e2e.py:674-887` (`test_ac1_real_anthropic_single_step_succeeds`) uses the exact combo rejected by the loader:

```python
workload = WorkloadClass.SOFTWARE_ENGINEERING                # :770
# ...
class _Workflow:
    @property
    def workflow_id(self) -> str:
        return "wf-ac1-real-anthropic"
    @property
    def workload_class(self) -> WorkloadClass:
        return workload                                       # SOFTWARE_ENGINEERING
    @property
    def manifest_entry(self) -> WorkflowManifestEntry:
        return WorkflowManifestEntry(
            workflow_id="wf-ac1-real-anthropic",
            workload_class=workload,
            persona_tier=PersonaTier.TEAM_BINDING,
            engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
            topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,  # :844
            ...
        )
    # ...
# ---------------- exercise ----------------
result = await _run(_Workflow(), config=config)               # :879
```

Test passes (mechanism β green when `ANTHROPIC_API_KEY` set; probe confirmed reach-LLM-and-back at HEAD).

### §1.3 — Why the loader's matrix is what it is

`per_workload_class_topology.py:87-99`:

```python
PER_WORKLOAD_CLASS_TOPOLOGY: tuple[PerWorkloadClassTopologyCommitment, ...] = (
    PerWorkloadClassTopologyCommitment(
        workload_class=WorkloadClass.SOFTWARE_ENGINEERING,
        default_pattern=TopologyPattern.EVALUATOR_OPTIMIZER,
        permitted_patterns=_permitted(
            WorkloadClass.SOFTWARE_ENGINEERING,
            frozenset({
                TopologyPattern.EVALUATOR_OPTIMIZER,
                TopologyPattern.ORCHESTRATOR_WORKERS,
            }),
        ),
        rationale=(
            "§11.1 row 1 — evaluator-optimizer (writes); orchestrator-workers "
            "(reads/review/eval); strict single-threaded writer per Cognition "
            "strong-convergence."
        ),
    ),
    # ...
)
```

The CP spec C-CP-11 §11.1 row 1 declares SOFTWARE_ENGINEERING's permitted topologies as `{EVALUATOR_OPTIMIZER, ORCHESTRATOR_WORKERS}` — **explicitly excludes SINGLE_THREADED_LINEAR**. The exclusion is rationalized: software-engineering tasks benefit from evaluator-optimizer (review-iterate) or orchestrator-workers (delegate-aggregate); single-threaded-linear is not appropriate for the workload's design-intent shape.

### §1.4 — Why the MVP exposes the mismatch

Per C-CP-25 v1.4 MVP scope (validated empirically at the probe): **only `SINGLE_THREADED_LINEAR` is materialized** at the workflow_driver dispatch path. Per runtime spec v1.35 §14.18 + Phase 7 implementation arc, `EVALUATOR_OPTIMIZER` + `ORCHESTRATOR_WORKERS` + `DECENTRALIZED_HANDOFF` + `HIERARCHICAL_DELEGATION` + `PARALLELIZATION` are all declared at the enum but unmaterialized at the dispatch level.

Net result:
- SOFTWARE_ENGINEERING's matrix-permitted topologies: `{EVALUATOR_OPTIMIZER, ORCHESTRATOR_WORKERS}` — both UNMATERIALIZED at MVP
- MVP's materialized topologies: `{SINGLE_THREADED_LINEAR}` only
- Intersection: ∅
- **SOFTWARE_ENGINEERING workload is structurally unrunnable via the YAML manifest path at MVP scope**

At MVP, ONLY `PIPELINE_AUTOMATION` workload (which admits SINGLE_THREADED_LINEAR per matrix row 3) reaches the workflow_driver dispatch successfully via the YAML path.

### §1.5 — Net consequence at HEAD

The advertised operator-facing CLI (`harness run workflow.yaml`) has two structural restrictions at MVP that are not documented in spec or CLI help:

1. **YAML manifests with `step_payload` typed scalars cannot reach successful LLM dispatch** (per sibling PR #79 fork — `class_1_fork_yaml_loader_step_payload_scalar_coercion_gap`)
2. **Only `workload_class=pipeline-automation` workflows are runnable** via the YAML path at MVP scope

Both restrictions are absent from runtime spec §14.18 / §14.19 + Phase_7_Meta_Architecture_v1 §5 + workspace CLAUDE.md §3 stack-discipline section.

The integration test (`test_ac1_real_anthropic_single_step_succeeds`) demonstrates that the runtime accepts `(SOFTWARE_ENGINEERING, SINGLE_THREADED_LINEAR)` at the dispatch level — implying the loader's design-time guard is stricter than runtime's actual constraint for the simple-step case.

---

## §2 — Three readings

**Reading A — Relax the loader: drop the admissibility check at load-time; defer entirely to the runtime sub-agent-dispatch-time check.** Aligns load-time enforcement with runtime enforcement (both apply only when sub-agent dispatch is invoked).

Pros: closes the loader-vs-runtime asymmetry at the structural level. `(SOFTWARE_ENGINEERING, SINGLE_THREADED_LINEAR)` becomes runnable via YAML, matching the integration test's empirical runtime behavior. Per `Spec_Harness_Runtime_v1.md` v1.36 Reading β precedent (engine_class admissibility check moved from loader to U-RT-106 dispatch site — same shape of "defer to runtime where the constraint actually fires").

Cons: loses the design-time guard. Workflows can declare topologies they won't use; misleading at the manifest layer. A workflow with `topology_pattern=EVALUATOR_OPTIMIZER` ships fine at v1.4 MVP, then fails when it tries to dispatch sub-agents (runtime check at site #2 fires; unmaterialized topology error). The early-fail design-time guard is sometimes more useful than late-fail at execution.

**Reading B — Tighten the matrix or relax the matrix at MVP scope: amend `PER_WORKLOAD_CLASS_TOPOLOGY` at MVP to add `SINGLE_THREADED_LINEAR` to SOFTWARE_ENGINEERING's permitted set as a "v1.4 MVP carve-out" + restore the full matrix at v1.7+ when EVALUATOR_OPTIMIZER materializes.** Preserves the design-time guard; opens the MVP window.

Pros: closes the unrunnable-workload defect at MVP without losing the design-time guard at v1.7+. Aligns with sub-species 7a `operator-explicit-deferred-close-gate` pattern (CP spec §25.5 v1.4 carve-out precedent — batch-48 H_T-CP-9 RETIRED).

Cons: requires CP spec v1.28 + v1.x amendment authoring (C-CP-22 §11.1 row 1 carve-out clause) + CP plan v2.31 + production matrix amendment. Larger blast radius than Reading A. The "carve-out" rationale is "MVP scope reality" rather than design-intent — diverges from the spec's design-intent framing of the matrix.

**Reading C — Tighten the loader: surface the mismatch as a documented operator-actionable error.** Keep the load-time check; replace `RT-FAIL-CLI-MANIFEST-ADMISSIBILITY` with a richer error that names the MVP-scope materialization gap explicitly:

```
RT-FAIL-CLI-MANIFEST-ADMISSIBILITY: topology_pattern 'single-threaded-linear' is
not admissible for workload_class 'software-engineering' per U-CP-22 matrix
(permitted: {evaluator-optimizer, orchestrator-workers}).

  v1.4 MVP scope: only 'single-threaded-linear' is materialized; permitted
  topologies for software-engineering are not yet runnable. Use workload_class
  'pipeline-automation' (admits 'single-threaded-linear' per matrix) until
  evaluator-optimizer + orchestrator-workers materialize at v1.7+.
```

Pros: preserves the matrix, preserves the design-time guard, names the MVP-scope reality at the operator boundary. Operator can act on the error without consulting design substrate. Zero cross-axis cascade.

Cons: doesn't fix the structural gap; just documents it at the error message layer. Operators still cannot run `software-engineering` workloads via YAML at MVP. The integration test bypass continues to exist (Protocol-conformant workflow constructed directly).

**Reading D — Mark the integration test's bypass as a deliberate scaffolding choice; ratify the loader's strictness; document the operator-facing constraint at CLI help + workspace README + runtime spec §14.19.** The integration test is test-substrate; its bypass of the loader is allowed because it exercises post-loader runtime behavior. The loader's design-time guard is correct; the matrix is correct; the MVP scope reality is what it is.

Pros: discipline-pure. Test bypass is acknowledged as test-substrate; runtime asymmetry is acknowledged as scope-bounded. Zero code change.

Cons: cements the structural unrunnable-workload constraint at MVP. Operators cannot run SOFTWARE_ENGINEERING workloads via YAML until matrix-permitted topologies materialize. The "operator-facing CLI" advertised in runtime spec §14.18 ships with a load-bearing usability gap.

---

## §3 — Operator decisions

**Q1 — Resolution path.**

- (A) Relax loader: drop `_check_topology_admissibility`; defer to runtime sub-agent-dispatch-time check
- (B) Relax matrix at MVP: add SINGLE_THREADED_LINEAR to SOFTWARE_ENGINEERING's permitted set as a v1.4 carve-out
- (C) Tighten loader error message; keep behavior (RECOMMENDED — minimal blast radius; preserves matrix integrity; closes the operator-actionability gap without requiring design substrate amendment)
- (D) Ratify the loader's strictness + document the MVP constraint at CLI/README/spec

**Q2 — Test fixture treatment (independent of Q1).** `minimal.yaml` ships with `software-engineering` + `evaluator-optimizer` — fails on Q1=C/D and partially fails on Q1=A/B (still fails at runtime if a sub-agent dispatch is reached with unmaterialized topology). Possible fixes:

- (α) Switch fixture to `pipeline-automation` + `single-threaded-linear` (admissibility-OK at all Q1 readings; runs at MVP)
- (β) Switch fixture to a step_kind that doesn't reach LLM (smoke-test shape only); avoids the sibling PR #79 scalar coercion gap
- (γ) Retire `minimal.yaml`; ship `minimal.toml` as canonical (per PR #79 Q1=D precedent if both forks chose documentation-only)
- (δ) Author TWO fixtures — minimal.yaml (smoke) + minimal_inference.toml (real LLM exercise) — explicit about the YAML scalar coercion constraint

**Q3 — Sub-agent dispatch site #585 enforcement scope.** Currently the runtime check fires at `propose_sub_agent_dispatch`. If Q1=A is chosen (drop load-time check), site #585 becomes the sole enforcement site:

- (i) Confirm site #585 is sufficient for all runtime-time-fail scenarios (RECOMMENDED if Q1=A)
- (ii) Add additional runtime check at workflow_driver entry (uniform enforcement at every dispatch level)
- (iii) Defer Q3 to follow-on plan revision

**Q4 — CP plan / spec amendment scope.** Does this fork require:

- (a) NO design substrate amendment (Q1=C or D — error message refinement only OR doc-only)
- (b) CP spec C-CP-22 §11.1 amendment (Q1=B — matrix carve-out)
- (c) Runtime spec §14.19 + CP plan U-RT-104 amendment (Q1=A — loader behavior change)
- (d) Multiple of the above per chosen reading

**Q5 — Cross-axis cascade.** None at intra-runtime/loader scope per §1 empirical grep. If Q1=B chosen (matrix amendment), surfaces CP spec v1.28 cascade. If Q1=A chosen, surfaces runtime spec §14.19 amendment + CP plan U-RT-104/U-RT-106 cascade.

- (α) Q1=C/D → ZERO cross-axis cascade
- (β) Q1=A → runtime spec + CP plan cascade
- (γ) Q1=B → CP spec + CP plan cascade

---

## §4 — Adjacent observations

### (a) Sibling fork at PR #79 — `class_1_fork_yaml_loader_step_payload_scalar_coercion_gap`

PR #79 documents the strictyaml scalar coercion gap (`step_payload` integer scalars stringified at YAML load). This fork documents a DIFFERENT structural gap at the same loader: the topology admissibility check enforces at load-time but the runtime path does not enforce uniformly. The two forks are independent — PR #79's resolution does NOT close this fork; this fork's resolution does NOT close PR #79. Both must be resolved for the YAML loader to ship a runnable operator-facing CLI.

### (b) Probe finding #6 — SOFTWARE_ENGINEERING workload structurally unrunnable at MVP

The same MVP-scope materialization gap was catalogued at PR #79 §4 as adjacent finding #6. This fork (#79 sibling) anchors the gap at its load-time enforcement site. Q1=B at this fork would close finding #6 directly. Q1=A would close it via runtime acceptance (the integration test bypass becomes the canonical path).

### (c) C-RT-30 §14.19.4 invariant 12 (AC #12) consistency

The loader's `_check_topology_admissibility` is wired per spec v1.35 §14.19.4 AC #12 (U-CP-22 admissibility at load-time). The runtime sub-agent dispatch check at site #585 is wired per CP spec §11.1 + sub-agent-dispatch composition. The two contracts both reference U-CP-22 but their enforcement scopes differ. Q1=A would amend the AC #12 invariant; Q1=B preserves AC #12 + amends C-CP-22; Q1=C/D preserve both.

### (d) Engine-class admissibility precedent (Reading β at runtime spec v1.36)

The sibling fork `class_1_fork_u_rt_104_admissibility_keying_and_carrier_defaults` was ratified at Reading β (defer-to-runtime) per operator AskUserQuestion 2026-05-28. That fork's resolution moved engine_class admissibility from loader to U-RT-106 dispatch site (the runtime is the authority; loader doesn't have the config in scope). The Q1=A reading here follows the same shape: defer the topology admissibility check from loader to runtime, where the constraint actually fires.

If Q1=A is chosen here, this fork extends the Reading β precedent from engine_class to topology_pattern — the loader becomes purely a schema-validation surface; admissibility (both axes) is runtime-authoritative.

### (e) Test-bypass-as-runtime-truth pattern catalogue candidate

The integration test at `test_ac1_real_anthropic_single_step_succeeds` empirically demonstrates that the runtime accepts what the loader rejects. This is a distinct closure-event-class:

> **`test-bypass-as-runtime-truth`** — an integration test exercises a code path that the loader/CLI does not admit; the test passes because runtime acceptance differs from loader strictness. The test's success is genuine evidence the runtime works for the combo; the loader's rejection is genuine evidence the loader has its own constraint. Both can be correct; the asymmetry is the defect.

Per workspace pattern `[[verification-shape-sharpened-grep-vs-e2e]]`, integration tests are the higher authority for runtime correctness; the loader's stricter check is design-time hygiene that may or may not match runtime authority. This fork is the first explicit catalogue of the pattern at workspace `.harness/` scope.

### (f) Sub-agent-dispatch-time enforcement timing

If Q1=A is chosen, the only remaining enforcement is at `propose_sub_agent_dispatch` (site #585). Workflows that NEVER dispatch sub-agents (single-step inference workflows, simple linear pipelines) escape admissibility check entirely. This is fine for MVP scope where sub-agent dispatch is the only fan-out surface and admissibility is fan-out-shape correctness — but if future arcs introduce additional topology-dependent dispatch surfaces, each must add its own admissibility check OR a central enforcement site must be added (Q3=ii).

---

## §5 — Filing footer

| Field | Value |
|---|---|
| Artifact | `class_1_fork_topology_admissibility_check_load_time_vs_runtime_asymmetry.md` |
| Status | PROPOSING |
| Filed at | 2026-05-29 |
| Surfaced by | use-the-product probe finding #14 (post-PR-#78 session); 55th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` (advisor convened pre-probe to frame the use-the-product question; this fork extends the catalogue surfaced during that probe) |
| Authority anchors | runtime spec v1.35 §14.19.4 AC #12 (U-CP-22 admissibility at load-time); CP spec C-CP-22 §11.1 row 1 (SOFTWARE_ENGINEERING permitted topologies); runtime spec v1.36 Reading β precedent (engine_class admissibility deferred from loader to U-RT-106 dispatch); Phase 7 Meta-Architecture §7.7 X-AL-3 silent design extension rule |
| Empirical anchors | `harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py:386-402` (`_check_topology_admissibility`); `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:571-585` (runtime check site); `harness-cp/src/harness_cp/per_workload_class_topology.py:87-99` (matrix row 1); `harness-runtime/tests/integration/test_track_b_e2e.py:674-887` (integration test bypass); probe trace (YAML rejected; Protocol-bypass succeeded) |
| Resolution path | Per CLAUDE.md §4.3 Class 1 → halt-on-load only; route to design-phase back-flow at runtime spec / CP spec / plan amendment per chosen reading. Apply arc per ratified Q-set lands at follow-on PR with clearance marker per CLAUDE.md §4.5 |
| Cross-axis cascade | Per Q5 ratification: (α) Q1=C/D → ZERO; (β) Q1=A → runtime spec §14.19 + plan U-RT-104/U-RT-106; (γ) Q1=B → CP spec C-CP-22 §11.1 + CP plan |
| Sibling forks | PR #79 (`class_1_fork_yaml_loader_step_payload_scalar_coercion_gap`) — independent gap at same loader; both must be resolved for operator-facing YAML CLI to ship runnable |
