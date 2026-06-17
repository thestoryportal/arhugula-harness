# Class 1 Fork — arc M: `MANAGED_AGENTS` StepKind extension (closed-at-5 §5.2 enum) + C-RT-28 ManagedAgents executable-consumer contract

**Filed:** 2026-06-17 · R-FS-1 arc **M** (managed-agents contract + production wiring; build position 11/11). Class 1 (a NEW design-substrate contract C-RT-28 at runtime spec §14.20 + a **closed-enum extension** of the CP `StepKind` 5-value set at CP spec §5.2 — both X-AL-3 design extensions). **Architecture RESOLVED (probe-resolved + advisor-affirmed); OPERATOR-GATED on the closed-at-5 `StepKind` extension** (a meaningful change to the core dispatch enum — `[[feedback-gate-only-on-meaningful-architecture-change]]`). Design back-flow FULL-SPEC-pre-authorized (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`), but the *closed-enum extension* is the operator's ratified call, not silently absorbed — exactly the v1.52 (operator-gated) side of the live discriminator the v1.54 change-note draws ("impl-to-cleared-ADR … UNLIKE the operator-gated v1.52").

**Status:** ⏳ AWAITING OPERATOR RATIFICATION (AskUserQuestion at filing). On ratify → Slice 2+ author C-RT-28 (runtime spec §14.20, mirroring §14.17 C-RT-27) + the CP `StepKind` §5.2/§25.2 6th-member delta + plan units + impl (factory bootstrap-bind gated on `DeploymentSurface.MANAGED_CLOUD` + a managed-agents `StepDispatcher` bound in the registry) + cite-bind + the surfaced vendor-gate. Clearance markers filed for the CP + runtime spec bumps on merge.

---

## §1 The fork

Arc M makes the **already-built, live-proven** managed-agents capability reachable from a production workflow. The capability is real: `harness-runtime/src/harness_runtime/lifecycle/managed_agents.py` (251 lines) carries `AnthropicManagedAgentsClient` (SDK adapter over `client.beta.sessions.*`), `ManagedAgentsClientProtocol`, the 9-state `ManagedAgentSessionStatus`, and `managed_agents_runtime_span`; R-820 (`tools/r820_managed_agents_live_e2e.py`) drove a real Anthropic Managed Agents session to `session.status_idle` with `managed_agents.*` attrs in Cloud Trace, and `.harness/substitutions.yaml` records **H_T-AS-8f SUBSTANTIVE_RETIRED** (batch-52). Two gaps remain — exactly the *needs-contract-or-wiring* shape:

1. **No contract.** `grep "C-RT-28"` returns **exactly one** hit — the negative prose at `Spec_Harness_Runtime_v1.md:703` ("no §14.18 C-RT-28 sibling to v1.32 §14.17 C-RT-27"). No `## §` section defines a managed-agents executable-consumer contract.
2. **Zero production callers.** The only two repo-wide importers of `lifecycle.managed_agents` are the R-820 proof script + its unit test. The production path is `harness_runtime.api.run()` → `run_bootstrap` → in-process MCP `run_workflow` → `harness_cp.workflow_driver.execute_workflow`, which iterates `workflow.steps` dispatching by `StepKind` through a frozen `{StepKind → StepDispatcher}` registry. **None of the 5 StepKind values routes to managed_agents.**

**The closed-enum collision (the load-bearing arc-open decision).** To reach managed_agents from `execute_workflow`, a step must carry a `step_kind` the registry maps to a managed-agents-aware dispatcher. The CP `StepKind` enum is **closed at cardinality 5** (`harness-cp/src/harness_cp/workflow_driver_types.py:64-79`, verbatim CP spec §5.2):

> *"Closed at cardinality 5 — extension is a Workflow §4.1.2 Class-2 revision of §5.2."*
> `DECLARATIVE_STEP / INFERENCE_STEP / TOOL_STEP / HITL_STEP / SUB_AGENT_DISPATCH`

So the wiring forces a choice between **Option A** (ride/overload an existing kind — `SUB_AGENT_DISPATCH` is the only semantic neighbor) and **Option B** (add a 6th `MANAGED_AGENTS` kind, extending the closed enum). The dossier (`.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md` §"Arc M" + open_questions) framed this as *ride = runtime-thin/impl-discretion, new-kind = balloons/cross-axis-fork* — **grounding inverts that framing** (§2.1).

---

## §2 Resolution

### §2.1 Architecture — Option B (new `MANAGED_AGENTS` kind), not Option A (overload `SUB_AGENT_DISPATCH`)

Two facts were body-verified at HEAD `9e4d340` (the advisor flagged the prior pass had *inferred* the SUB_AGENT_DISPATCH incompatibility rather than verified it; both are now verified):

**(i) The driver is StepKind-agnostic at dispatch.** Every one of the 6 dispatch sites across all 6 topology strategies (`workflow_driver.py:1996, 3079, 3435, 3875, 3970, 4409`) is uniformly `step_dispatchers.lookup(step.step_kind).dispatch(...)`. There is **zero** `if step.kind == SUB_AGENT_DISPATCH` conditional code in the driver — the recursion/`subagent.*`/topology semantics are NOT driver-forced. (Module docstring line 23-27 + §25.3.3.4: *"Step body is opaque to the driver."*) This was necessary-but-not-sufficient for "Option A clean."

**(ii) The `SUB_AGENT_DISPATCH` *dispatcher* hard-requires harness-orchestration semantics a vendor session cannot honor.** The dispatcher bound to `SUB_AGENT_DISPATCH` (`harness-runtime/.../lifecycle/sub_agent_dispatch.py`) is a fixed harness-orchestration composer: step 4 (`:60`) *"Verify topology admissibility via `ctx.topology_dispatcher` + `is_topology_permitted`"* → **raises `SubAgentDispatchTopologyInadmissibleError`** (`:78, :152, :206`; C-CP-11 §11.1 / C-CP-10 §10.3 union predicate) if the child manifest's `topology_pattern × workload` is inadmissible; step 5 (`:61`) opens `subagent.span` + sets `subagent.*` + `topology.*`; it recurses over a **child manifest entry** (`:180`, engine_class + topology_pattern). A vendor-run managed session has **no harness topology_pattern and no harness-orchestrated child loop** — the vendor runs the loop server-side. It cannot satisfy the admissibility gate or the topology span set.

| Option | Mechanism | Assessment |
|---|---|---|
| **A — ride `SUB_AGENT_DISPATCH`** | Keep the enum closed-at-5; bind a managed-agents-aware dispatcher to `SUB_AGENT_DISPATCH` (1:1 registry ⟹ it *replaces* or *internally branches* the existing sub-agent dispatcher on `step_payload`). | **Rejected (probe-resolved).** The registry is a frozen 1:1 `{StepKind → StepDispatcher}`; riding ⟹ overloading the bound dispatcher to branch harness-recursion-vs-vendor-managed on payload. That **widens the committed C-RT-17 dispatcher contract** AND **collapses the `step.kind` execution-model discriminator** (makes "sub-agent-dispatch" mean two distinct execution models) AND forces the admissibility gate (ii) to be conditionally skipped for the managed branch. This is a **sacrifice of the committed `SUB_AGENT_DISPATCH` semantic** — the dossier's "thin/no-gate" reading is wrong; ride is the *more* invasive change to a cleared contract. |
| **B — new `MANAGED_AGENTS` StepKind** | Add a 6th member to `StepKind` (§5.2/§25.2) + bind a managed-agents `StepDispatcher` to it in the registry. | **CHOSEN.** Purely **additive** — all 5 existing members + the C-RT-17 dispatcher contract + the `SUB_AGENT_DISPATCH` dispatcher stay byte-unchanged. The driver auto-handles it (StepKind-agnostic per (i)); the only code is the enum member + a registry binding at bootstrap. Clean semantic + audit separation (a managed-cloud run is `managed-agents`, not mislabeled `sub-agent-dispatch`), and it emits its own `managed_agents.*` span family (already declared in AS §14.5 + OD `sampling_mode`). advisor-affirmed: *"Option B is the architecturally correct shape."* |

No council: there is no residual nameable cross-voice tension once the probe forecloses Option A (the apparent audit-cleanliness ⊥ scope-minimalism tension dissolves because *ride* is **both** dirtier *and* a committed-semantic sacrifice — it is dominated, not traded off). `[[probe-resolves-fork-prescribed-council]]`.

### §2.2 This IS a genuine operator gate (the probe did NOT dissolve it)

A "probe-resolves → dissolve the gate" reading was attempted: *Option B is purely additive, and `RunStatus.PAUSED` (the identical "closed-at-N — Workflow §4.1.2 Class-2 revision" enum shape) was extended as "additive minor-version evolution," so adding `MANAGED_AGENTS` is likewise un-gated.* **advisor caught this as the exact framing error reversed at B4-Slice-4** (`[[advisor-before-substantive-work-for-cross-axis-blockers]]`) — same move, same closest-structural-analog. Both load-bearing premises were unverified inferences; verified, both fail:

- **`Project_Workflow_v1_8.md` §4.1.2** is the adversarial-review **findings-severity** taxonomy (Class 1=Minor / Class 2=Moderate / Class 3=Severe — *inverted* from the §2.7.6 fork taxonomy). The "Moderate" class = *"document revision … version bump … re-run only the affected session"*; it is **silent** on operator ratification — it neither mandates nor waives a gate. **Not an affirmative "un-gated."**
- **`RunStatus.PAUSED`** does **NOT** show additive *enum* extension is un-gated. The carve-out the docstring cites — runtime spec **§14.14.5 invariant 4** — is *"RunResult shape additive evolution … `RunResult.pause_snapshot` is added as an additive optional **FIELD**"* (a dataclass field, not an enum member). The `PAUSED` enum member itself landed inside the **spec-ratified U-RT-87/88/89 arc** (runtime spec v1.20→v1.21, §14.14.6 step 1). So the "additive minor-version evolution" framing covers a *field*, not the enum-cardinality change.

The advisor's bar to dissolve the gate ("**both** §4.1.2 **and** the PAUSED landing affirmatively show additive enum extension is un-gated") **fails on both legs** → the gate stands.

Independent confirmation from the live discriminator: the v1.54 change-note (B6 Slice 1, this same day) states *"**No operator gate — impl-to-cleared-ADR (UNLIKE the operator-gated v1.52)** … sacrifices NO committed invariant."* B6 was un-gated because it *fulfilled* a cleared ADR-D2 §1.3 mandate and relaxed nothing. Arc M is the opposite: there is no cleared contract governing a managed-agents executable consumer (C-RT-28 is unauthored), and the choice **changes the core dispatch enum**. Per `[[feedback-gate-only-on-meaningful-architecture-change]]`, adding a 6th execution model to the dispatch enum (a new dispatcher + new span family + vendor-delegated execution model) is about as meaningful an architecture change as this system has — it clears the gate bar. The dossier Slice 1 ("operator-ratify"), the B4-Slice-4 precedent, and the explicit Class-2-revision routing all agree.

### §2.3 What the operator ratifies

**Gated:** extending the closed-at-5 CP `StepKind` enum (§5.2 + the §25.2 materialization in `workflow_driver_types.py`) to add a 6th member `MANAGED_AGENTS = "managed-agents"` (Option B). This is the `Project_Workflow` §4.1.2 Class-2 revision of §5.2 the enum docstring names.

**NOT gated (FULL-SPEC pre-authorized design back-flow, decided-and-noted):**
- **C-RT-28** authored at runtime spec **§14.20** (next free slot; §14.18=C-RT-29, §14.19=C-RT-30 verified), mirroring the §14.17 C-RT-27 precedent (a `RuntimeConfig.managed_agents_*_config` opt-in at §3 + a `HarnessContext` client/emitter field at §4 + a `materialize_*_stage` factory + a `RT-FAIL-MANAGED-AGENTS-*` class at §11). Contract-id: **honor the reserved `C-RT-28`** (the arc name, the as_8f fork, and the negative-prose all reference it; the §-headers jumped 27→29→30 leaving 28 reserved) rather than renumber to C-RT-31.
- **Surface-gating:** the factory binds only on `DeploymentSurface.MANAGED_CLOUD` + an operator-supplied config opt-in (the as_8f local-development exclusion remains TRUE); local-dev/self-hosted skip (no managed-agents step kind dispatcher bound ⟹ a manifest using it fails closed with the existing `StepKindDispatcherNotBoundError` → `RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND`, no silent under-execution).
- **Cite-bind:** tag `managed_agents.py` + carriers to C-RT-28 / H_T-AS-8f (overlay reports `carrier_files: []` today).

---

## §3 Decorrelated review

**advisor** (pre-substantive, full transcript) — **affirmed Option B** as architecturally correct + the driver-vs-dispatcher distinction as a real catch; **caught the probe-resolves gate-dissolution** as a repeat of the B4-Slice-4 error and directed verification of §4.1.2 + the PAUSED landing before treating the path as un-gated (both verified to fail the dissolve bar, §2.2); confirmed no council warranted (probe-resolved, no residual cross-voice tension). `[[red-team-operator-decision-without-backdooring]]` (inverted — advisor red-teamed *my* gate drift).

**Codex (out-of-family) — deferred to the post-ratification impl slices.** This fork doc is a pure design/strategy artifact with no diff yet; per the §13.2 division of labor, the out-of-family Codex reviewer is the default for a concrete *diff* and is not the right tool for a no-diff design fork (advisor is). `just codex-review` runs at the Slice-2+ spec/impl diff, pre-merge (`[[hooks-codex-pilots-decorrelation-validated]]`).

---

## §4 Slice plan (post-ratification) + spine registration

Arc M is already a registered R-FS-1 child arc (`.harness/r-fs-1-arc-and-unit-map.md` §R-FS-1·M, build position 11/11) + a SPINE Bucket-A managed-cloud row. On ratification:

1. **Slice 2 (spec):** C-RT-28 at runtime spec §14.20 (mirror §14.17) + the CP `StepKind` §5.2/§25.2 6th-member delta (CP spec head v1.38 → next). Bump both, file clearance markers, refresh the stale line-703 negative prose.
2. **Slice 3 (plan):** decompose C-RT-28 into U-RT-NN atomic units (precedent C-RT-27 → U-RT-99/100/101 linear chain); add the CP `StepKind` member to the plan + coverage matrix.
3. **Slice 4 (impl):** add the `MANAGED_AGENTS` enum member + bind a managed-agents `StepDispatcher` (over `AnthropicManagedAgentsClient` / `ManagedAgentsClientProtocol`) in the runtime registry at bootstrap, gated on `DeploymentSurface.MANAGED_CLOUD` + config opt-in. Provider-free unit tests + a skipif-gated **`@pytest.mark.e2e`** live test (`[[feedback-run-credential-gated-live-e2e-authorized]]`).
4. **Slice 5 (cite-bind):** tag carriers to C-RT-28 / H_T-AS-8f; `just overlay-check`.
5. **Slice 6 (vendor-gate, surface-only):** a live managed-cloud run re-touches `ANTHROPIC_API_KEY` (paid) + GCP IAM/Cloud-Run identity-token + Cloud-Trace — **drive to the dispatch boundary, surface for authorization, NEVER auto-fire** (`[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`).

**Cross-arc note (verified):** by the C-RT-27 precedent, C-RT-28 adds a `RuntimeConfig.managed_agents_*_config` opt-in + `HarnessContext` field → M is in contact with the same `RuntimeConfig` surface B3/B4/B6/B2 converged on; sequence M's impl serially against that surface, not in parallel.

Spine registration per `[[spine-ledger-forward-arc-registration]]`: the `MANAGED_AGENTS` StepKind extension + C-RT-28 are registered as the M-arc legs at `.harness/beyond-mvp-capability-boundary-ledger.md` on ratification.

---

*Filing footer — Artifact: `.harness/class_1_fork_m_managed_agents_stepkind_c_rt_28.md`; Arc: R-FS-1 arc M Slice 1; Posture: back-flow (X-AL-3-clean — this `.harness/` doc precedes, does not perform, the design-substrate edit); Method: HEAD body-grounding (`workflow_driver.py`, `workflow_driver_types.py`, `sub_agent_dispatch.py`, runtime spec §14.14.5/§14.17-20, `Project_Workflow_v1_8.md` §4.1.2) + advisor full-transcript review. Cites verified at HEAD `9e4d340`; runtime spec head v1.54.*
