# Spec: Control Plane — v1.54 (delta over v1.53)

---

## Change-note (v1.53 → v1.54)

**Scope of revision.** One additive closed-enum member + one amended composition contract: the **§5.2 `step.kind` enum** (and its **§25.2 `StepKind` materialization**) gains **`post-join-synthesis` / `POST_JOIN_SYNTHESIS`**, extending the step-kind taxonomy from **6 → 7**; and **C-CP-25 §25.12** is amended so that an OPT-IN `POST_JOIN_SYNTHESIS` terminal step replaces the deterministic fan-out aggregate with an LLM-composed synthesis, sacrificing **§25.12 determinism-boundary Point 2 (aggregator purity)** ONLY. This is the **CP half** of the R-FS-1 standalone arc **`B-POSTJOIN-LLM-SYNTHESIS`** (registered at `.harness/beyond-mvp-capability-boundary-ledger.md`; design vetted at `.harness/r-fs-1-final-closure-plan.md` arc (a) — C1⊥C9 dyadic council + §10.9 probe-resolution + advisor red-team; arc-scoping finding `.harness/r-fs-1-arc-a-postjoin-14.23-hollow-finding.md`). The runtime-side consumer is a **`PostJoinSynthesisStepDispatcher`** bound to `StepKind.POST_JOIN_SYNTHESIS` (paired runtime-spec delta C-RT — the LLM dispatch composing the recorded siblings).

**Why a spec amendment — and why it carries an operator gate (the closed-enum Class-2 revision + a committed-invariant sacrifice).** The §25.2 `StepKind` materialization (`harness-cp/src/harness_cp/workflow_driver_types.py`) declares the enum **"Closed at cardinality 6 — extension is a Workflow §4.1.2 Class-2 revision of §5.2."** This delta **is** that Class-2 revision (the second additive step-kind after the v1.39 arc-M `managed-agents`), AND it sacrifices the committed §25.12 Point-2 deterministic-aggregation guarantee for the opt-in synthesis. Both are **meaningful architecture changes** (`[[feedback-gate-only-on-meaningful-architecture-change]]`) — surfaced at Phase-7 execution, routed to design-phase back-flow (X-AL-3), and **operator-AUTHORIZED** (full-spec closure, 2026-06-22) + **operator-RATIFIED** (the arc-a mechanism choice, AUQ 2026-06-23). NOT a silent absorption — co-published with a `.harness/clearance/` marker per workspace `CLAUDE.md` §11.4.

**The committed invariant being amended (§25.12 Point 2 — aggregator purity).** §25.12's determinism boundary states (Point 2): *"Aggregation is a pure function of the ordered result set — 'first to finish wins' is forbidden; 'lowest branch-index on tie' is the deterministic tiebreak."* An LLM-composed synthesis is **non-deterministic** → it is NOT a pure function of the inputs → it SACRIFICES Point 2 for the opt-in synthesis step. **Point 1 is PRESERVED VERBATIM** (append order is deterministic; the chain is not byte-identical across replay — non-determinism stays confined inside the step per ADD §5.3.3). **The branch-index ordering of the input set is PRESERVED** — the synthesis reads the SAME deterministically-ordered sibling set the fold reads (only the COMPOSE function becomes non-pure, not the input ordering). The default deterministic fold (`_aggregate_orchestrator_workers` / `_aggregate_parallelization`) stays the DEFAULT, byte-identical, for every workflow that does not opt into a `POST_JOIN_SYNTHESIS` terminal step.

**The bounded residual (stated honestly, operator consciously accepted at the arc-a `A` AUQ 2026-06-23).** Because the synthesis aggregate is non-deterministic, a future fan-out-crash-replay-rehydration arc could re-dispatch a synthesized run to a *different* aggregate. This residual is **forward-looking and the divergence window is EMPTY today**: the 5 non-linear strategies are resume-blind for every in-scope engine class (a crashed fan-out restarts fresh — no completed-synthesis replay exists), so in the currently-wired harness a synthesized run is always a fresh first-and-only dispatch with **no divergence**. The non-determinism is made **LOUD** — the synthesis step self-discloses via its own durable, hash-chained, synthesis-specific step ledger entry (`workflow:{wf}:post-join-synthesis:{N}`) + this §25.12 contract caveat (the OTel span/trace-attribute is the deferred D6-ingestion layer, the v1.59 RESUMPTION precedent) — so IF such a replay path is ever wired the non-reproducibility is already declared, never silent. **Reproducible cached-replay** (capture + replay the synthesized aggregate across a fan-out crash-resume) is the **registered sequenced follow-on `B-FANOUT-OUTPUT-REPLAY`** — it requires a NEW durable per-branch-completion substrate committing in completion order, a SECOND committed-invariant sacrifice (§25.12 **Point-1/D1** branch-index-order append) that gets its OWN C1⊥C9 council + operator gate when opened (per the arc-a §25.12-D1 materializability finding `.harness/r-fs-1-b-fanout-output-replay-impl-design.md`). It is NOT in this arc.

**Read-only, effect-free, top-level-post-join only.** The synthesis is a model call with **NO external effect** (a pure read-of-siblings + compose) — re-dispatch on any resume path is at-most-once-safe; the step MUST stay effect-free (no effect-fence-carrying tool dispatch inside synthesis). Scope is the **top-level post-join only**: `HIERARCHICAL_DELEGATION` reuses `ORCHESTRATOR_WORKERS` per level, and synthesis-per-level (a child synthesis feeding the parent) is a registered follow-on, NOT this arc.

**No new hash field; no IS-spec change; no new CXA edge.** `step.kind` is already a captured dimension of the §5.2 `step.boundary` attribute set (per §25.3.3 step 5 + C-IS-05); this delta adds a **value** to that dimension, not a new dimension — the C-IS-05 §5.2 hash recipe + §16.5 idempotency-key formula are **PRESERVED VERBATIM**. The §6/§5.2 hash chain never attested cross-replay reproducibility; tamper-evidence is fully preserved; synthesis disclosure rides the self-disclosing step entry (the OTel span attribute is the deferred D6 layer), NOT a new IS field. The `POST_JOIN_SYNTHESIS` dispatcher consumes the already-landed runtime dispatch seam (the `StepKindDispatcherRegistry`); no new typed cross-axis composition edge. CXA v2.20 UNCHANGED; IS / OD / AS specs UNCHANGED.

**v1.53 + prior body PRESERVED VERBATIM.** All v1.53 content + the entire C-CP-01 … C-CP-29 body (incl. §5.2, §25.2, §25.10–§25.18, the §25.12 Point 1, the `_aggregate_*` folds) is PRESERVED VERBATIM per the delta-only-spec-file convention. The **only** changes are the additive enum member at §5.2 + its §25.2 materialization + the §25.12 Point-2 opt-in-synthesis amendment below.

---

## §1 — Amended §5.2 `step.kind` enum (6 → 7; ADDS `post-join-synthesis`)

The §5.2 `step.kind` taxonomy gains one additive member. The v1.39-cleared 6-value set is PRESERVED VERBATIM; `post-join-synthesis` joins as the operator-ratified Class-2 revision of §5.2 (arc-a):

```
step.kind ∈ {
    declarative-step,
    inference-step,
    tool-step,
    HITL-step,
    sub-agent-dispatch,
    managed-agents,
    post-join-synthesis    // NEW v1.54 — opt-in LLM-composed terminal synthesis after a concurrent fan-out (arc-a)
}                          // cardinality 7 (was 6); this delta IS the §4.1.2 Class-2 revision
```

**`post-join-synthesis` semantics.** A `post-join-synthesis` step's body is executed by an **LLM dispatch that composes the sibling worker outputs of a concurrent fan-out** (`ORCHESTRATOR_WORKERS` / `PARALLELIZATION` / `HIERARCHICAL_DELEGATION`) into a synthesized result. It is a **terminal post-barrier step** — dispatched ONCE after the fan-out barrier drain, reading all sibling outputs **branch-index-ordered** (the SAME deterministic order the §25.12 fold reads), producing the run's terminal `RunResult.final_state`. This is **categorically distinct from `sub-agent-dispatch`** (which orchestrates a harness-run child loop) and from a per-step `inference-step` (which runs in the inline §25.3 loop reading its own payload): a `post-join-synthesis` step runs at the driver-level post-barrier site and reads the N sibling outputs. Its non-determinism is the §25.12 Point-2 sacrifice (below). Dispatch contract: the runtime `PostJoinSynthesisStepDispatcher` (paired runtime-spec delta C-RT).

**Opt-in + surface.** A workflow opts in by declaring a terminal step with `step_kind = post-join-synthesis` as the LAST step of a concurrent-fan-out topology. Absent that terminal step, the deterministic §25.12 fold is the DEFAULT (byte-identical, fully reproducible). The `POST_JOIN_SYNTHESIS` dispatcher binding is available on all deployment surfaces (no surface-gate — unlike `managed-agents`); an unbound dispatcher fails closed with the existing `StepKindDispatcherNotBoundError` → `RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND` (no silent under-execution).

## §2 — Amended §25.2 `StepKind` materialization (adds the 7th member)

The §25.2 `StepKind` enum materialization (`WorkflowStep.step_kind` at `harness-cp/src/harness_cp/workflow_driver_types.py`) gains the matching member; the closed-enum docstring updates **6 → 7**:

```
enum StepKind {
  DECLARATIVE_STEP,                              // "declarative-step"     per §5.2
  INFERENCE_STEP,                                // "inference-step"       per §5.2
  TOOL_STEP,                                     // "tool-step"            per §5.2
  HITL_STEP,                                     // "HITL-step"            per §5.2
  SUB_AGENT_DISPATCH,                            // "sub-agent-dispatch"   per §5.2
  MANAGED_AGENTS,                                // "managed-agents"       per §5.2 (v1.39)
  POST_JOIN_SYNTHESIS                            // "post-join-synthesis"  per §5.2 (NEW v1.54)
}
// Closed at cardinality 7 (was 6) — this v1.54 delta is the operator-ratified
// Workflow §4.1.2 Class-2 revision of §5.2; further extension requires another.
```

The driver's per-step inline dispatch is byte-unchanged (StepKind-agnostic). A `POST_JOIN_SYNTHESIS` terminal step is NOT dispatched in the inline §25.3 loop — the concurrent-fan-out strategy carves it out as the terminal step and dispatches it post-barrier (§3). `WorkflowStep.step_payload` carries the synthesis dispatch inputs (the synthesis prompt/config), opaque to the driver per §25.3.3.4; the sibling worker outputs are supplied at dispatch time by the driver (the `StepExecutionContext` sibling-outputs carrier — branch-index-ordered, §3), NOT introspected from the step body.

## §3 — Post-barrier synthesis dispatch (C-CP-25 §25.12 — opt-in terminal step)

> **The concurrent-fan-out strategies recognize a terminal `POST_JOIN_SYNTHESIS` step.** When the last `WorkflowStep` of a `ORCHESTRATOR_WORKERS` / `PARALLELIZATION` / `HIERARCHICAL_DELEGATION` step sequence has `step_kind == POST_JOIN_SYNTHESIS`, the strategy carves it out of the branch set (it is NOT executed as a worker branch): for `ORCHESTRATOR_WORKERS`, `steps[0]` = orchestrator, `steps[1:-1]` = workers, `steps[-1]` = synthesis; for `PARALLELIZATION`, `steps[:-1]` = branches, `steps[-1]` = synthesis; for `HIERARCHICAL_DELEGATION`, the synthesis is at the TOP level only (per-level synthesis is the registered follow-on). Absent a `POST_JOIN_SYNTHESIS` terminal step, the strategy's branch set + the deterministic §25.12 fold are byte-identical to pre-v1.54.
>
> At the barrier drain (`drain_branch_buffers` / `_finish`), after the sibling outputs are `collected` branch-index-ordered, the strategy dispatches the synthesis step via `step_dispatchers.lookup(POST_JOIN_SYNTHESIS).dispatch(binding, synthesis_step, step_context=...)`, supplying the branch-index-ordered sibling outputs on the `StepExecutionContext` (a driver-supplied sibling-outputs carrier — the synthesis reads `collected` DIRECTLY; the §14.21 inter-step channel is NOT re-opened for this — it correctly stays #705-resolved, the synthesis being a direct `collected` consumer). The synthesis dispatch output becomes the run's terminal `RunResult.final_state` (REPLACING the deterministic fold output for that run). The synthesis is **read-only / effect-free**.
>
> **Fail-closed placement validation (impl-to-spec trace).** An invalid synthesis placement terminates the run FAILED with no synthesis LLM call, via two guards: (a) a STATIC placement guard (before any branch dispatch / side effect) rejects a non-terminal, multiple, or non-concurrent-topology synthesis, or a lone synthesis with no fan-out step — `fail_class` `post-join-synthesis-misplaced: …`; (b) a DISPATCH-TIME zero-sibling guard rejects a synthesis whose concurrent fan-out drained ZERO siblings (e.g. an `ORCHESTRATOR_WORKERS` / `HIERARCHICAL_DELEGATION` `[orchestrator, synthesis]` carving to zero workers — invisible to the static `len`-guard since the orchestrator is `steps[0]`, and dispatch-time is the only point a DYNAMIC worker count is known) — `fail_class` `post-join-synthesis-no-siblings: …`. The enforced precondition is "a synthesis FOLLOWS a concurrent fan-out with ≥1 sibling." Both `fail_class` strings are free-text descriptive (NOT a closed-enum extension; the closed `StepKind` enum is the gated surface — §1/§2).
>
> **Loud disclosure (the §25.12 Point-2 sacrifice made non-silent).** The synthesis dispatch emits its OWN post-barrier step ledger entry (mirroring `_append_step_ledger_entry`, with the synthesis-specific `action_id` `workflow:{wf}:post-join-synthesis:{N}`) — a **durable, hash-chained, synthesis-specific** disclosure that the run's terminal aggregate is synthesis-composed / non-deterministic. That ledger entry IS the loud disclosure (stronger than a transient span — it survives in the audit ledger). The OTel span/trace-attribute layer is the **standard deferred D6-ingestion layer** (CP emits the typed disclosure; OD/runtime populates the span attribute downstream — the v1.59 RESUMPTION precedent), NOT emitted at the CP driver here. The §25.12 contract caveat (this §3 + §4) is the standing declaration.

## §4 — §25.12 determinism boundary — amended Point 2 (aggregator purity, opt-in sacrifice)

> §25.12 "Determinism boundary (ADD §5.3.3)" is amended. **Point 1 is PRESERVED VERBATIM** (append order is deterministic given fixed step outputs; the chain is NOT byte-identical across replay; non-determinism stays confined inside the step). **Point 2 is amended:**
>
> > 2. **Aggregation is a pure function of the ordered result set** — "first to finish wins" is forbidden; "lowest branch-index on tie" is the deterministic tiebreak (mirroring the existing voting/council convention). **(v1.54 amendment — opt-in exception.)** When a workflow opts into a terminal `POST_JOIN_SYNTHESIS` step (§3), the aggregation for that run is an **LLM-composed synthesis** over the branch-index-ordered sibling set — which is **NON-deterministic** (NOT a pure function of the inputs). The branch-index **ordering** of the input set is preserved (the synthesis reads the same deterministically-ordered set the fold reads); only the COMPOSE function becomes non-pure. The default deterministic fold remains the aggregation for every run that does NOT opt in (byte-identical, fully reproducible). The non-determinism is LOUD (§3 disclosure) and the divergence window is empty in the currently-wired harness (the 5 non-linear strategies are crash-resume-blind); reproducible cached-replay of the synthesized aggregate is the registered follow-on `B-FANOUT-OUTPUT-REPLAY` (a separate §25.12-Point-1/D1 reckoning, NOT this arc).

---

## §5 — Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_54.md` (delta over v1.53) |
| Authority | R-FS-1 `B-POSTJOIN-LLM-SYNTHESIS` (closed-enum Class-2 revision + §25.12 Point-2 committed-invariant sacrifice; operator-AUTHORIZED 2026-06-22 + arc-a mechanism RATIFIED 2026-06-23; design `.harness/r-fs-1-final-closure-plan.md` arc (a) — C1⊥C9 dyadic council + §10.9 probe-resolution + advisor; arc-scoping `.harness/r-fs-1-arc-a-postjoin-14.23-hollow-finding.md`); FULL-SPEC directive (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`) |
| Paired runtime delta | `Spec_Harness_Runtime_v1.md` C-RT — the `PostJoinSynthesisStepDispatcher` bound to `StepKind.POST_JOIN_SYNTHESIS` (the LLM dispatch composing the branch-index-ordered siblings; read-only / effect-free) |
| Committed invariant amended | C-CP-25 §25.12 determinism boundary **Point 2 (aggregator purity)** — relaxed for the opt-in `POST_JOIN_SYNTHESIS` terminal step (LLM-composed, non-deterministic); Point 1 + branch-index ordering PRESERVED; default fold byte-identical (operator-ratified; forward-looking empty-window residual consciously accepted) |
| Explicitly NOT in this arc | §14.23 cached-replay capture; fan-out crash-resume output replay; per-level HIERARCHICAL synthesis — all the registered follow-on `B-FANOUT-OUTPUT-REPLAY` (its own §25.12-Point-1/D1 council + gate) |
| Preserved | v1.53 + entire C-CP-01 … C-CP-29 body (incl. §5.2 6-value set, §25.2, §25.10–§25.18, §25.12 Point 1, the `_aggregate_*` folds) PRESERVED VERBATIM; IS / OD / AS / ADR specs UNCHANGED; CXA v2.20 UNCHANGED; no §5.2 hash / §16.5 key change |
| Apply pass | Co-published with `harness-cp` impl (`StepKind.POST_JOIN_SYNTHESIS` + the terminal-step carve + post-barrier dispatch at `_finish` across the 3 concurrent strategies + the post-barrier synthesis ledger entry + disclosure + default-byte-identical) + `harness-runtime` impl (the `PostJoinSynthesisStepDispatcher`) + by-execution witnesses (full-chain through the REAL provider: synthesis composes actual recorded siblings; default-fold byte-identical negative control; effect-free; loud-disclosure audit; top-level-only) + a `.harness/clearance/` marker + spine-ledger transit + arc-ledger registration of the `B-FANOUT-OUTPUT-REPLAY` follow-on, per workspace `CLAUDE.md` §11.4 bundled-absorption |
