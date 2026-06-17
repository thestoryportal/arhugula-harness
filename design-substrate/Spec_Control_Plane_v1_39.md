# Spec: Control Plane — v1.39 (delta over v1.38)

---

## Change-note (v1.38 → v1.39)

**Scope of revision.** A single additive member on the **§5.2 `step.kind` enum** (and its **§25.2 `StepKind` materialization**) — NEW **`managed-agents` / `MANAGED_AGENTS`** — extending the step-kind taxonomy from **5 → 6**. This is the **R-FS-1 arc M** leg (managed-agents contract + production wiring): a workflow step whose body is executed by a **vendor-run Managed Agents session** (Anthropic's `beta.sessions.*`), as opposed to a harness-orchestrated step. Design authority: `.harness/class_1_fork_m_managed_agents_stepkind_c_rt_28.md` (filed + operator-ratified this arc, Option B). The runtime-side consumer contract is **C-RT-28** (`Spec_Harness_Runtime_v1.md` §14.20, paired delta) — a `ManagedAgentsStepDispatcher` bound to `StepKind.MANAGED_AGENTS` in the `StepKindDispatcherRegistry`, gated on `DeploymentSurface.MANAGED_CLOUD` + an operator config opt-in.

**Why a spec amendment — and why it carries an operator gate (the closed-enum Class-2 revision).** The §25.2 `StepKind` materialization (`harness-cp/src/harness_cp/workflow_driver_types.py`) declares the enum **"Closed at cardinality 5 — extension is a Workflow §4.1.2 Class-2 revision of §5.2."** This delta **is** that Class-2 revision: the first actual extension of the `step.kind` taxonomy. The v1.4 Change-note §D recorded the prior deliberation — §5.2 carries **no explicit closure marker in the spec** (unlike §5.1 closed-at-8 / §10.1 closed-at-6), so adding a 6th value is "interpretive … contestable as silent enum extension"; the 2026-05-20 Path-B decision deliberately preserved the 5-value enum for a *drain-boundary* event-kind (handled via `RunResult.status='drained'` instead). Arc M is the categorically different, legitimate case: an additive **execution-model** step kind, surfaced at Phase-7 execution, routed to design-phase back-flow (X-AL-3) and **operator-ratified** (AskUserQuestion 2026-06-17, **Option B**) per the arc-M fork doc. Adding a 6th member to the core dispatch enum is a meaningful change to the architecture (`[[feedback-gate-only-on-meaningful-architecture-change]]`) — the operator's call, not silently absorbed. FULL-SPEC (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`) pre-authorizes the *build* + the *back-flow*; the *closed-enum extension itself* is the ratified gate.

**Why Option B (new kind), not Option A (ride `SUB_AGENT_DISPATCH`) — the probe that foreclosed the alternative.** Body-grounding at HEAD `9e4d340`: (i) the CP **driver is StepKind-agnostic** — every dispatch site is `step_dispatchers.lookup(step.step_kind).dispatch(...)` (6 sites, zero `step.kind`-conditional code), so a new kind needs no driver change; but (ii) the dispatcher bound to `SUB_AGENT_DISPATCH` (`harness-runtime/.../lifecycle/sub_agent_dispatch.py`) **hard-requires harness-orchestration semantics a vendor session cannot honor** — it verifies topology-admissibility (raises `SubAgentDispatchTopologyInadmissibleError` per C-CP-11 §11.1 / C-CP-10 §10.3), recurses over a child manifest, and emits `subagent.*`/`topology.*` spans. Riding `SUB_AGENT_DISPATCH` would therefore overload its dispatcher to branch on payload — **widening the committed C-RT-17 dispatcher contract + collapsing the `step.kind` execution-model discriminator** (a vendor run mislabeled `sub-agent-dispatch`). Option B is purely **additive** — all 5 existing members + the C-RT-17 dispatcher contract + the `SUB_AGENT_DISPATCH` dispatcher stay byte-unchanged; the driver auto-handles the new kind; clean semantic + audit + `managed_agents.*` span separation. (advisor-affirmed; probe-resolved — no council.)

**No change to the §5.2 hash recipe; no IS-spec change.** `step.kind` is already a captured dimension of the §5.2 `step.boundary` attribute set (per §25.3.3 step 5 + C-IS-05); this delta adds a **value** to that dimension, not a new dimension. The C-IS-05 §5.2 hash recipe + §16.5 idempotency-key formula are **PRESERVED VERBATIM**. A `managed-agents` step's step-boundary entry simply carries `step.kind="managed-agents"`. The managed-agents session's own metadata (session_id / runtime_ms / billable_seconds) is captured at the `managed_agents.runtime` span per the AS §14.5 namespace + the C-RT-28 dispatch return, not at the §5.2 hash.

**No new CXA edge.** The `managed_agents.*` namespace (3 attrs) is already declared at **AS spec §14.5** (`anthropic_attribute_namespaces` SCHEMA) + its sampling posture at **OD `sampling_mode`** (the `managed_agents.runtime` always-sampled floor). The new StepKind consumes the already-landed namespace/ingestion seam; no new typed cross-axis composition edge is introduced. CXA v2.20 UNCHANGED.

**v1.38 + prior body PRESERVED VERBATIM.** All v1.38 content — the C-CP-06 §6.1/§6.2/§6.6 per-step role override + §2.5 + §19.1.2 + §27.8 + §7.4 + §25.10–§25.18 + §29 + the entire C-CP-01 … C-CP-29 body — is PRESERVED VERBATIM per the delta-only-spec-file convention. The **only** changes are the additive enum member at §5.2 and its §25.2 materialization below.

---

## §1 — Amended §5.2 `step.kind` enum (5 → 6; ADDS `managed-agents`)

The §5.2 `step.kind` taxonomy gains one additive member. The v1.4-cleared 5-value set is PRESERVED VERBATIM; `managed-agents` joins as the operator-ratified Class-2 revision of §5.2 (arc-M fork, Option B):

```
step.kind ∈ {
    declarative-step,
    inference-step,
    tool-step,
    HITL-step,
    sub-agent-dispatch,
    managed-agents        // NEW v1.39 — vendor-run Managed Agents session step (arc M)
}                          // cardinality 6 (was 5); this delta IS the §4.1.2 Class-2 revision
```

**`managed-agents` semantics.** A `managed-agents` step's body is executed by a **vendor-run Managed Agents session** — the vendor (Anthropic `beta.sessions.*`) runs the agent loop server-side; the harness creates the session, sends the step's event, polls to a terminal status, and emits the `managed_agents.runtime` span. This is **categorically distinct from `sub-agent-dispatch`**, whose dispatcher orchestrates a harness-run child loop (topology-admissibility gate + child-manifest recursion + `subagent.*`/`topology.*` spans). A `managed-agents` step has **no harness topology_pattern** and emits the `managed_agents.*` namespace, not `subagent.*`. The dispatch contract is C-RT-28 (`Spec_Harness_Runtime_v1.md` §14.20).

**Surface-gating.** The `MANAGED_AGENTS` step dispatcher is bound in the `StepKindDispatcherRegistry` only on `DeploymentSurface.MANAGED_CLOUD` + an operator config opt-in (C-RT-28; the H_T-AS-8f local-development exclusion remains TRUE). On local-development / self-hosted-server (or with no opt-in), `MANAGED_AGENTS` is **not bound** → a workflow using it fails closed with the existing `StepKindDispatcherNotBoundError` → `RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND` (no silent under-execution). The enum member exists on all surfaces; only its dispatcher binding is surface-gated.

## §2 — Amended §25.2 `StepKind` materialization (adds the 6th member)

The §25.2 in-session-amendment-§E `StepKind` enum materialization (the `WorkflowStep.step_kind` discriminator at `harness-cp/src/harness_cp/workflow_driver_types.py`) gains the matching member; the closed-enum docstring updates **5 → 6**:

```
enum StepKind {
  DECLARATIVE_STEP,                              // "declarative-step"   per §5.2
  INFERENCE_STEP,                                // "inference-step"     per §5.2
  TOOL_STEP,                                     // "tool-step"          per §5.2
  HITL_STEP,                                     // "HITL-step"          per §5.2
  SUB_AGENT_DISPATCH,                            // "sub-agent-dispatch" per §5.2
  MANAGED_AGENTS                                 // "managed-agents"     per §5.2 (NEW v1.39)
}
// Closed at cardinality 6 (was 5) — this v1.39 delta is the operator-ratified
// Workflow §4.1.2 Class-2 revision of §5.2; further extension requires another.
```

The driver's per-step dispatch is byte-unchanged (StepKind-agnostic): `step_dispatchers.lookup(step.step_kind).dispatch(...)` routes a `MANAGED_AGENTS` step to whatever dispatcher the registry binds for it (the C-RT-28 `ManagedAgentsStepDispatcher` when surface-gated on, else the registry's not-bound raise). `WorkflowStep.step_payload` carries the managed-agents dispatch inputs (agent_id / environment_id / the event), opaque to the driver per §25.3.3.4.

---

## §3 — Status

Additive §5.2 `step.kind` member (`managed-agents`) + §25.2 `StepKind` materialization, absorbing the operator-ratified (AskUserQuestion 2026-06-17, Option B) R-FS-1 arc-M managed-agents production-wiring decision. This delta **is** the Workflow §4.1.2 Class-2 revision of §5.2 the §25.2 closed-enum docstring names.

**Operator gate — RATIFIED.** The closed-at-5 `StepKind` extension was the operator's ratified call (arc-M fork doc §2.2; AskUserQuestion 2026-06-17 → Option B). FULL-SPEC pre-authorized the build + back-flow; the closed-enum extension itself is what the operator ratified. This delta is canonical on merge alongside the paired runtime C-RT-28 (§14.20) + the harness-cp/harness-runtime impl.

Apply pass: this delta co-published with the paired **runtime spec C-RT-28 §14.20** (the `ManagedAgentsStepDispatcher` + stage-5 factory + `RuntimeConfig.managed_agents_config` opt-in + `HarnessContext` field + `RT-FAIL-MANAGED-AGENTS-*` fail class) + harness-cp impl (`StepKind.MANAGED_AGENTS` member) + harness-runtime impl (dispatcher + factory + registry binding) + tests (provider-free unit + skipif-gated `@pytest.mark.e2e` live) + fork doc + clearance markers (CP v1.39 + runtime v1.55) + spine-ledger registration, per workspace `CLAUDE.md` §11.4 bundled-absorption.

v1.38 + v1.37 + earlier PRESERVED VERBATIM per delta-only-spec-file convention. The entire C-CP-01 … C-CP-29 body + §5.1 + §5.3 + §16.5.x + §25.x PRESERVED VERBATIM (only §5.2 enum + §25.2 materialization amended). IS spec UNCHANGED (no §5.2 hash-recipe change; step.kind is an existing captured dimension). CXA v2.20 UNCHANGED (the `managed_agents.*` namespace + ingestion already declared at AS §14.5 + OD `sampling_mode`; no new typed edge). ADR-F1/F2/F3/D1–D6 UNCHANGED. ADD v1.3 + PRD v1.1 UNCHANGED.

Clearance markers filed at `.harness/clearance/Spec_Control_Plane-v1_39-cleared-2026-06-17.md` + `.harness/clearance/Spec_Harness_Runtime-v1_55-cleared-2026-06-17.md`.

2026-06-17.
