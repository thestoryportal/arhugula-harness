# Spec: Control Plane — v1.32 (delta over v1.31)

---

## Change-note (v1.31 → v1.32)

**Scope of revision.** NEW §25.10–§25.18 — an **in-place additive extension of C-CP-25 WorkflowDriver** materializing the **5 non-`SINGLE_THREADED_LINEAR` topology patterns** (`PARALLELIZATION`, `ORCHESTRATOR_WORKERS`, `DECENTRALIZED_HANDOFF`, `HIERARCHICAL_DELEGATION`, `EVALUATOR_OPTIMIZER`). This **lifts the §25.1 deferral** ("Extension contract … authored when the first multi-worker workflow unit demands materialization") under the R-FS-1 full-spec build directive. The extension authors: the driver-strategy dispatch surface (§25.10), per-pattern orchestration contracts (§25.11), the buffered/deferred-append branch path + determinism boundary (§25.12), branch-causality persistence via the Route-Y IS sidecar seam (§25.13), the B1↔B4 role seam (§25.14), `cascade_policy` consumption + the cascade-cancel reach (§25.15), branch-scoped idempotency-key composition (§25.16), the failure-mode taxonomy extension (§25.17), and the implementation-discretion + recorded-forks list (§25.18).

**Authoring authority.** R-FS-1 arc #3 (B1-spec-1) per the cleared B1 design `.harness/r-fs-1-b1-topology-orchestration-design-v1.md` (arc #2, mode-agnostic, X-AL-3-clean) + `.harness/r-fs-1-arc-1-scoping-v1.md` (child-arc B1). Directive: `[[feedback-full-spec-beyond-mvp-nothing-deferred]]` (FULL-SPEC standing directive, roadmap §5.0).

**Contract-identity correction (forward-correction, NOT a history rewrite).** Per the v1.13 Class-1 fork resolution Reading A (`.harness/class_1_fork_cp_spec_section_25_contract_id_collision.md` §7, operator-ratified 2026-05-24), **§25 / C-CP-25 = WorkflowDriver** (v1.6-lineage; retains canonical-ID primacy) and **§28 / C-CP-28 = ValidatorFramework** (the v1.10-lineage body, renamed §25→§28 at v1.13). The v1.29–v1.31 `§-preserved-verbatim` tables (e.g. v1.31 line 108 "§25 C-CP-25 — ValidatorFramework"; line 9 inline note) **mislabel §25/C-CP-25 as ValidatorFramework** — a change-note labeling drift that crept in post-v1.13 (v1.18/v1.19 correctly honor the rename, citing "C-CP-28 §25.2" for ValidatorFramework). The contract **bodies were never affected**: the §25 body is and has always been WorkflowDriver (v1.6); the ValidatorFramework body lives at §28 (v1.10 body, renamed at v1.13). v1.32's `§-preserved-verbatim` table carries the **corrected** labels; per the delta-only-spec preservation discipline it does **not** edit the historical v1.29–31 change-notes (those stay verbatim as authored). Code corroborates the corrected identity: `harness-cp/src/harness_cp/workflow_driver.py` is C-CP-25 WorkflowDriver; `harness-cp/src/harness_cp/validator_framework_types.py` is C-CP-28 ValidatorFramework.

**v1.31 + prior body PRESERVED VERBATIM.** All v1.31 content — §29 / C-CP-29 `PromptSelectionManifest` + the v1.30 §1 canonical-reading lineage + §16.5.x + §25.1–§25.9 (the C-CP-25 WorkflowDriver core driver contract, v1.4 §25.1–§25.8 + v1.5 §25.9) + §26 / C-CP-26 PauseResumeProtocol + §27 / C-CP-27 PerServerTrustEvaluator + §28 / C-CP-28 ValidatorFramework (incl. its §28.x v1.24 post-evaluate hook) — is PRESERVED VERBATIM per the delta-only-spec-file convention. §25.10–§25.18 are **purely additive subsections of the existing C-CP-25 contract** (the same in-place-extension shape v1.5 used to add §25.9 cost-attribution to C-CP-25) — they do not amend, reinterpret, or supersede §25.1–§25.9 or any other section; the §25.1 deferral table is **honored-then-lifted** (its forward-pointer is now realized at §25.10, not contradicted).

**No new contract ID; no new ADR; no six-field / hash-chain / ADR-F2 §Decision change.**
- **Fork (a) — contract shape (RESOLVED):** the extension is authored **in-place on C-CP-25 as §25.10+ subsections**, NOT a new contract ID and NOT the deferral table's stale forward-guess "C-CP-25.b or **C-CP-26**" (C-CP-26 was subsequently occupied by `PauseResumeProtocol` at v1.10; and `.b` sub-IDs are not an established convention in this spec). Rationale: §25.1 deferred C-CP-25's **own** `execute_workflow` behavior for non-linear topologies — lifting it is an additive extension of the same contract surface (one source of truth: the WorkflowDriver owns workflow execution), mirroring the v1.5 §25.9 precedent exactly. Recorded at `.harness/class_2_fork_b1_spec_1_contract_shape.md`.
- **Fork (b) — branch-causality recording (RESOLVED → Route Y):** branch causality + the persisted cancellation marker flow via a **bounded IS D-derivative `branch_metadata` sidecar** (`{parent_action_id, branch_index, terminal_status}`) on `StateLedgerEntry`, **to be authored at the coordinated IS amendment B1-spec-1b** (mirrors the `procedural_tier_snapshot_ref` precedent; ADR-F2 §Consequences (c); zero six-field-shape / §6 hash-chain / ADR-F2 §Decision change). §25.13 below is a **forward-coordination reference** to that IS amendment, not a byte-resolvable cite — the IS section number is assigned at B1-spec-1b. Recorded at `.harness/class_1_fork_b1_branch_causality_route_x_vs_y.md`.
- **Fork (c) — effectful-cancellation C10 (RESOLVED → Fork A, council-resolved):** `cascade-cancel` is **dispatch-boundary-bounded** (cancel only not-yet-dispatched steps; in-flight steps run to completion/timeout + recorded; high-blast-radius effectful steps gate before dispatch via the committed chain). **No compensation/saga primitive** — rollback-of-an-already-sent-effect is not a coherent operation, so it is out of cascade-cancel's domain (a complete honest semantic), not a deferral. Resolved by a genuine dyadic **C1⊥C10 council** (`.harness/council/r-fs-1-b1-cascade-cancel/DELIVERABLE.md`; 3-way decorrelated convergence advisor + C1 + C10) under the §13.4 discriminator (composes committed primitives → not a meaningful-architecture gate). Recorded at `.harness/class_1_fork_b1_effectful_cancellation_c10.md`.

**Trigger.** R-FS-1 arc #3 opening 2026-06-13. The §25.1 deferral table's first multi-worker materialization demand under the full-spec directive. Empirical grounding at HEAD: the driver's `_IN_SCOPE_TOPOLOGY = frozenset({SINGLE_THREADED_LINEAR})` (`workflow_driver.py:83`) gates the 5 patterns to `TopologyPatternNotYetMaterializedError`; `CascadePolicy` (`topology_pattern.py:55-67`) is declared-but-unconsumed; `RunStatus.PARTIAL` is reserved at §25.2 ("reserved for future multi-step error modes").

**Committed HOW preserved (full-spec directive WHAT-vs-HOW).** All 5 strategies are **hand-rolled in `asyncio`** (I-6: NO `langgraph`/`crewai`/`temporal`/`prefect`). The patterns are **H_T Control-Plane primitives** — NEVER delegated to the H_E Claude Code `Agent` tool (CP-AL-1, Meta-Architecture §7.4; I-4 substrate boundary at the MCP server process).

---

## §25.10 (NEW) C-CP-25 extension — Non-linear topology driver-strategy surface

**Status posture.** `Status: Proposed` (parity with the §25 v1.4/v1.5 authoring posture) — promotion to `Accepted` blocked until the B1 plan units land (CP plan B1-plan revision) + the coordinated IS sidecar (B1-spec-1b) + runtime materialization (B1-spec-2) + impl (B1-impl-N).

**ADR commitment(s) honored.** ADR-D4 v1.1 §1.2 (six-pattern topology taxonomy admissibility annotations — C-CP-25 now materializes all 6 rows, not 1) + ADR-D5 v1.3 (per-persona-tier composition) via C-CP-10 §10.1/§10.3; ADR-F2 v1.2 §Decision + §Consequences (single-threaded-write boundary — §25.12 D1); ADR-F3 v1.1 §Decision (iv) (workflow lifecycle event surface — the 5 strategies compose the same §5.1 closed-at-8 taxonomy, no new event class). NO new ADR (the extension lifts C-CP-25's own §25.1 deferral; it composes committed primitives).

### §25.10.1 Driver-strategy dispatch (lifts the §25.1 `_IN_SCOPE_TOPOLOGY` gate)

The single in-scope-topology gate (`workflow_driver.py:83` `_IN_SCOPE_TOPOLOGY = frozenset({SINGLE_THREADED_LINEAR})`; §25.3.1 validation step) is **replaced by a driver-strategy dispatch table** keyed on `manifest_entry.topology` (the C-CP-10 §10.1 `TopologyPattern` enum value):

```text
topology_pattern  →  driver strategy
  SINGLE_THREADED_LINEAR   →  the existing §25.3 iteration loop, VERBATIM (regression-safe; inline per-step append per §25.12)
  PARALLELIZATION          →  fan-out-barrier-aggregate strategy            (§25.11)
  ORCHESTRATOR_WORKERS     →  orchestrator-dispatch-collect strategy        (§25.11)
  HIERARCHICAL_DELEGATION  →  recursive bounded-fan-out strategy            (§25.11)
  DECENTRALIZED_HANDOFF    →  single-owner sequential handoff strategy      (§25.11)
  EVALUATOR_OPTIMIZER      →  generate-evaluate-regenerate loop strategy    (§25.11)
```

**Invariants.**
1. **Regression-safety.** The `SINGLE_THREADED_LINEAR` strategy is the existing §25.3 loop body unchanged — same inline per-step ledger append (§25.12), same §25.5 lifecycle emission filter, same §25.4 drain protocol, same §25.6 idempotency-key join, same §25.7 failure taxonomy, same §25.9 cost composition. The dispatch table is the only structural change at the gate site.
2. **Admissibility precondition (unchanged).** A `manifest_entry.topology` non-admissible for `manifest_entry.workload_class` per C-CP-10 §10.3 / C-CP-11 §11.1 is still rejected at workflow-binding time. The §25.10 lift removes only the *materialization* gate (the 5 patterns no longer raise `TopologyPatternNotYetMaterializedError`); it does not widen admissibility.
3. **Engine-class scope unchanged at B1.** The §25.1 engine-class scope (`pure-pattern-no-engine` / `save-point-checkpoint`) is **not** widened by B1. A non-in-scope engine class still raises `EngineClassNotYetMaterializedError` (§25.7). Engine-recovery materialization is the separate R-FS-1 child-arc E (engines).
4. **§25.1 deferral honored-then-lifted.** This subsection realizes the §25.1 deferral table's forward-pointer ("Extension contract … authored when the first multi-worker workflow unit demands materialization"); the deferral text is preserved verbatim (it recorded the intent now fulfilled).

---

## §25.11 (NEW) Per-pattern orchestration contracts (hand-rolled, I-6 / asyncio)

**Common substrate (all 5 non-linear strategies).**
- **Branch.** A branch = a sub-sequence of `WorkflowStep`s dispatched under a **child `StepExecutionContext`** (`parent_action_id` = the spawning step's `action_id`; child gate-level per C-CP-12 §12.2 monotonic descent; child `AgentRole` per §25.14). Reuses the existing `StepDispatcher` registry, per-step entry construction, and the §5.1 closed-at-8 lifecycle event surface — strategies differ only in *control flow over steps* and in *when the ledger write happens* (§25.12).
- **Concurrency.** `asyncio.TaskGroup` (3.11+; structured cancellation per §25.15) — or `asyncio.gather` where no cascade-cancel semantic is needed — over branches. NEVER the H_E `Agent` tool (CP-AL-1). `SUB_AGENT_DISPATCH` (`StepKind`, §5.2) is H_T's own sub-agent primitive — a child workflow branch under a descended gate-level through H_T's dispatcher registry, recorded in H_T's ledger; it is not a call into H_E.
- **Bounded barriers.** Every barrier (`TaskGroup`/`gather` join) is wrapped in a wall-clock deadline so a stuck branch cannot strand its parent indefinitely; deadline-exceeded composes with `cascade_policy` (§25.15). (Corpus: sub-agent-interrupt-stranding — a barrier must bound its wait.)
- **Append discipline.** The buffered/deferred-append path (§25.12), never the inline per-step append of the `SINGLE_THREADED_LINEAR` strategy.
- **Determinism.** Aggregation is a pure function of the **ordered** branch-result set; no aggregator may depend on completion order (§25.12).

| Pattern | Orchestration semantics | Barrier / aggregation |
|---|---|---|
| **`PARALLELIZATION`** | Fan-out N branches over varied inputs concurrently (cap per C-CP-10 §10.3 research/content-creation cells). | Barrier: hold until all branches finish; a synthesis/voting aggregator step folds structured outputs into one result (deterministic tiebreak = lowest branch-index). |
| **`ORCHESTRATOR_WORKERS`** | An orchestrator step computes a dynamic worker set, dispatches workers concurrently (per-role specialization via §25.14), collects. | Barrier at collection; orchestrator composes the final result. |
| **`HIERARCHICAL_DELEGATION`** | Recursive `ORCHESTRATOR_WORKERS` with depth; fan-out cap 3 per parent (C-CP-10 §10.3); gate-level **descends** per child (C-CP-12 §12.2 `sub_agent_gate_level_descent`). | Bottom-up: each parent barriers on its children, composes upward. `cascade_policy` default propagation at recursion per ADR-D4 v1.1 §1.11 / §10.3 deferral (impl discretion). |
| **`DECENTRALIZED_HANDOFF`** | Single-owner-at-a-time; each stage-expert (per-role, §25.14) hands the workflow to the next via a `HandoffContext` (C-CP-13). | Sequential ownership transfer; terminal when no further handoff (`cascade_policy` typically `cascade-cancel`, single-owner). |
| **`EVALUATOR_OPTIMIZER`** | Loop: generate-step → evaluate-step → (accept \| regenerate-with-feedback), bounded by a max-iteration cap. | Sequential; terminal on evaluator accept or cap. Roles (evaluator / optimizer) are per-step prompts (R-PM-1 §29 selection) — non-hollow at B1 without B4. |

**Pattern meaningfulness at B1.** `PARALLELIZATION` + `EVALUATOR_OPTIMIZER` are non-degenerate at B1-alone (variation is in *inputs* / *per-step prompt*, not agent specialization). `ORCHESTRATOR_WORKERS` / `HIERARCHICAL_DELEGATION` / `DECENTRALIZED_HANDOFF` depend on per-role specialization → §25.14 folds the role-threading **mechanism** into B1 so they are non-hollow by construction (the per-role binding *catalog* + per-step override remains the distinct R-FS-1 child-arc B4).

---

## §25.12 (NEW) Buffered/deferred-append branch path + determinism boundary (D1 / D1.b)

**D1 — single-threaded serialized append (no second `prior_event_hash`).** Parallel *execution* does NOT require parallel ledger *appends*. Branch work runs concurrently; the resulting ledger appends are **serialized through the single writer in deterministic declaration order** (branch-index order, NOT completion order). The hash chain stays **single-parent linear and untouched**: no second `prior_event_hash`, no DAG entry, no multi-parent chain, **zero C-IS-05 §5 six-field-shape change, zero §6 hash-chain-construction change, zero ADR-F2 §Decision change**. This is ADR-F2 v1.2 §Consequences's **own prescribed resolution** — "concurrent sub-agents must coordinate via worktree-isolation or single-threaded-write boundary"; D1's serialized append *is* that single-threaded-write boundary (worktree-isolation, C-IS-09 §9.1, is the read-fan-out side).

**D1.b — the buffered/deferred-append branch path (load-bearing mechanism).** The 5 non-linear strategies MUST use a **buffered/deferred-append** branch-execution path: a branch executes its step bodies + emits telemetry but **buffers its pending ledger entries** (returns an ordered pending-entry list); the orchestrator **drains the buffers through the single `LedgerWriterLike` in branch-index order at the barrier**. The inline per-step append of the existing `_execute_workflow_body` (which appends immediately after each step, serialized by the IS writer lock in *completion* order) is the foreclosed anti-pattern under `gather`/`TaskGroup` — it would persist entries in completion order, falsifying the deterministic-append guarantee. The inline-append path remains the `SINGLE_THREADED_LINEAR` strategy verbatim.

**Determinism boundary (ADD §5.3.3 — the deterministic outer harness).**
1. **Append order is deterministic given fixed step outputs; the chain is NOT byte-identical across replay.** D1.b makes *append order* a deterministic function of the (ordered) step-output set, independent of which branch's model call returned first. It does NOT make the chain byte-identical across replay: a replay re-runs non-deterministic `INFERENCE_STEP`s → different `response_hash` → a different chain. Non-determinism stays confined *inside* the step (ADD §5.3.3); the orchestration layer leaks none.
2. **Aggregation is a pure function of the ordered result set** — "first to finish wins" is forbidden; "lowest branch-index on tie" is the deterministic tiebreak (mirroring the existing voting/council convention).

---

## §25.13 (NEW) Branch causality + terminal_status persistence — Route-Y IS sidecar seam (D1.a) — FORWARD-COORDINATION REFERENCE

**Route Y (resolved fork (b)).** Branch causality (`parent_action_id`, `branch_index`) and the persisted cancellation marker (`terminal_status`, §25.15) are recorded durably via a **bounded IS D-derivative `branch_metadata` sidecar** on the persisted `StateLedgerEntry`. The `StepExecutionContext` fields `parent_action_id` / `parent_entry_hash` are **driver-transient** (not persisted; the `EntryPayload` write contract is `extra="forbid"`), so durable branch causality requires this sidecar — it cannot ride existing persisted fields.

> **FORWARD-COORDINATION REFERENCE (not a byte-resolvable cite).** The `branch_metadata` sidecar (`{parent_action_id, branch_index, terminal_status}`) is **authored at the coordinated IS amendment B1-spec-1b** (a new C-IS-05 §5.x subsection), following the `procedural_tier_snapshot_ref` D-derivative template exactly (added to `StateLedgerEntry` + `EntryPayload` + `_serialize_entry`/deserialize; ADR-F2 §Consequences (c); **zero six-field-shape / §6 hash-chain / §7 read-write-contract change**). Its IS section number is assigned at B1-spec-1b; this §25.13 names the seam and the field shape the CP driver composes, not a resolved IS section. The CP driver is the **producer** (composes branch metadata at branch-spawn + cancel); the IS sidecar is the **persisted carrier**. (Route X — `action_id` encoding — was rejected: IS spec v1.3 Amendment 3 ratifies that structured traceability flows via a sidecar, not action_id-encoding, and a string-parsed `terminal_status` is a fragile read path vs a typed field.)

---

## §25.14 (NEW) B1↔B4 role seam (D2)

`AgentRole` is discarded at dispatch today (the runtime dispatch seam `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py`; per the PR #509 record + §29 adjacent-observation (b)). Of the 5 patterns, 3 (`ORCHESTRATOR_WORKERS`, `HIERARCHICAL_DELEGATION`, `DECENTRALIZED_HANDOFF`) are hollow with same-role workers. Both `RoutingManifest.per_role_bindings` (C-CP-01 §1.3) and `PromptSelectionManifest.per_role_bindings` (§29) already carry per-role bindings structurally; the gap is the runtime indexer that threads `AgentRole` through dispatch.

> **D2 (decision):** **fold the role-threading mechanism into B1.** A branch's child `StepExecutionContext` **carries `AgentRole`** and threads it to the dispatch seam (the indexer at `llm_dispatch`) so the per-role model (C-CP-01 §1.3) + per-role prompt (§29.2) take effect. B1 **pins the seam** (the mechanism that makes worker/delegation/handoff non-hollow by construction); the per-role binding **catalog** + per-step override surface remains the distinct R-FS-1 child-arc **B4** (no longer a hard prerequisite for B1 to be meaningful). This is a reversible composition call sacrificing no committed decision (it materializes a structurally-present binding shape). The B1↔B4 *sequencing* is the one operator-open lever surfaced at the B1 design §10 (default-if-silent: D2, per the standing autonomous directive).

---

## §25.15 (NEW) `cascade_policy` consumption + cascade-cancel reach (D3 / Fork A — council-resolved)

`CascadePolicy` (C-CP-10 §10.2 field domain `"pause" | "proceed" | "cascade-cancel"`; `topology_pattern.py:55-67`) is declared-but-unconsumed today. Under fan-out it becomes load-bearing. The **effectful-cancellation C10 fork** is resolved to **Fork A** by the genuine dyadic C1⊥C10 council (`.harness/council/r-fs-1-b1-cascade-cancel/DELIVERABLE.md`): `cascade-cancel` is **dispatch-boundary-bounded**, composing committed primitives, with **no compensation/saga primitive** (rollback-of-an-already-sent-effect is not a coherent operation → out of cascade-cancel's domain, a complete semantic, not a deferral).

### §25.15.1 `cascade_policy` semantics under a barrier

| `cascade_policy` | On a branch failure | Sibling branches | Run-level `RunStatus` (§25.2) |
|---|---|---|---|
| `proceed` | Record the failure; the aggregator sees a partial result set (`degraded=true`, SRE graceful-degradation). | Run to completion. | **`PARTIAL`** (activates the §25.2 reserved value; runtime projection deferred to B1-spec-2, §25.18). |
| `pause` | Halt the fan-out at a HITL/pause boundary (composes with C-CP-26 PauseResumeProtocol + C-RT-35 `api.resume`). | Allowed to finish in-flight, then pause. | **`PAUSED`**. |
| `cascade-cancel` | Cancel in-flight not-yet-dispatched siblings (`asyncio.TaskGroup` cancellation); fail the fan-out. | Cancelled (not-yet-dispatched) / run-to-completion (in-flight) per §25.15.2. | **`FAILED`**. |

**The three run-level values are EXISTING `RunStatus` members — no new value is introduced.** `FAILED` + `PARTIAL` are §25.2 enum-body members (`PARTIAL` = the §25.2 "reserved for future multi-step error modes" value, now *activated* by `proceed`). `PAUSED` is a code-real `RunStatus` member that entered the enum at U-RT-89 / CP plan v2.20 via the C-CP-26 PauseResumeProtocol cascade (runtime-projected per runtime spec v1.45 C-RT-09); its CP §25.2 enum-*body* acknowledgement is the §-adjacent (c) Q1 doc-hygiene item — so this normative use is a **forward-consistent use of a code-real value**, NOT a new-value introduction and NOT a §25.2-body edit.

### §25.15.2 The eight cascade-cancel obligations (the explicit reach the spec states)

1. **Dispatch-boundary-bounded.** `cascade-cancel` cancels only **not-yet-dispatched** sibling steps (`TaskGroup` cancellation of pending branch tasks). An in-flight step at cancel-time is NOT cancelled — it runs to its own completion or barrier-deadline timeout.
2. **No-gate-bypass-by-buffering.** The §25.12 D1.b buffered path defers the ledger **write**, NEVER the **gate**: each branch evaluates the pre-dispatch HITL / sandbox-tier gate before each effectful step **exactly as the linear path does**. An implementation that deferred step machinery to the barrier drain would gate *after* the effect — foreclosed.
3. **Audit-completeness (no silent landed effect).** Every dispatched effectful step has its own recorded step ledger entry, regardless of the branch's terminal disposition. No landed effect is ever a silent gap.
4. **Discriminating `terminal_status`.** The Route-Y `branch_metadata.terminal_status` (§25.13) discriminates the branch disposition: `cancelled` ⟹ the branch terminated at a **not-yet-dispatched** boundary (no effectful dispatch at the termination point); `completed` / `timed_out` ⟹ the branch's in-flight step ran (effect may have landed) and is recorded. A non-discriminating "cancelled" would make audit-as-primary-defense hollow.
5. **High-blast-radius pre-dispatch gating (composes committed primitives).** Effectful steps gate **before** dispatch via the committed chain **C-AS-02 `sandbox_tier_floor`** (ADR-F4 four-tier graduated isolation; `EXTERNAL_IRREVERSIBLE → tier-4-full-vm`) → **C-CP-19 §19.1 `gate_level` multiplicative `max()`** → **C-CP-16 4-response palette** mandatory HITL. Consequence: at cancel-time an `external-irreversible` step is either not-yet-approved (cleanly cancellable) or operator-approved-and-in-flight (the operator already accepted that blast radius) — **no silent-uncompensated-effect hole for the dangerous class**. cascade-cancel composes this gate; it does not re-invent it. (No `dry_run`/`preview` primitive is introduced — §25.18.)
6. **Run-level status.** `cascade-cancel` → `RunStatus.FAILED`; `proceed` → `RunStatus.PARTIAL` (+ `degraded=true`); `pause` → `RunStatus.PAUSED`. (`PARTIAL` belongs to `proceed`, NOT cascade-cancel.)
7. **Resume-idempotency-terminality.** Branch-scoped idempotency keys (§25.16) so `api.resume` (C-RT-35) reads each branch's persisted `terminal_status` and MUST NOT re-dispatch a branch that is `cancelled` / `completed` / `timed_out`. (Corpus: make every interrupt-resume path idempotent.)
8. **Structured cancellation.** Use `asyncio.TaskGroup` so a failing branch's exception cancels not-yet-dispatched siblings deterministically; a bare `gather(return_exceptions=False)` would leak orphaned tasks. (I-6: hand-rolled, stdlib only.)

> **D3 (decision):** `cascade-cancel` = `TaskGroup` structured cancellation of not-yet-dispatched steps + in-flight steps run-to-completion/timeout + a **persisted discriminating** `terminal_status` per branch (Route-Y sidecar) + **branch-scoped idempotency keys** + resume-terminality + pre-dispatch gating of high-blast-radius effectful steps via the committed C-AS-02 → C-CP-19 → C-CP-16 chain. This resolves the **whole** C1⊥C10 tension (both the audit/idempotency half AND the effectful-cancellation half) — completeness = total persisted terminal-state coverage with no silent gap, NOT universal rollback. **Composes committed primitives only → no net-new primitive → not a meaningful-architecture gate** (§13.4 discriminator).

---

## §25.16 (NEW) Branch-scoped idempotency-key composition

The driver computes step idempotency as `sha256(run_idempotency_key, step_index)` and the IS writer deduplicates **solely on `idempotency_key`** (C-IS-07 §7.5 keying tuple). Under fan-out, N parallel branches at the *same declared `step_index`* would collapse to one entry (silent branch loss) unless the **branch path enters the idempotency-key composition**:

```text
idempotency_key = sha256(run_idempotency_key, step_index, branch_path)
```

This is a **CP-side driver write-key composition change** (`idempotency_key` is driver-composed; the C-IS-07 §7.5 keying tuple already treats write-key components as write-args) — **bounded, no six-field / hash-chain / ADR change**. It is load-bearing for both correct fan-out persistence (no same-step-index collapse) and resume/cancel terminality (§25.15 obligation 7). `branch_path` is part of the *idempotency-key* composition, not merely the `action_id`, because the IS writer dedups on `idempotency_key`.

---

## §25.17 (NEW) Failure-mode taxonomy extension

Extends §25.7 (preserved verbatim) for the non-linear strategies. No new `RunStatus` value is introduced (the §25.2 enum's `FAILED` / `PARTIAL` / `PAUSED` cover the run-level outcomes per §25.15.1).

| Condition | Surface | Posture |
|---|---|---|
| `manifest_entry.topology` non-admissible for `workload_class` | C-CP-10 §10.3 / C-CP-11 §11.1 binding-time rejection (unchanged) | Rejected at workflow-binding time (the §25.10 lift removes the *materialization* gate only, not admissibility). |
| Branch barrier deadline exceeded | bounded-barrier timeout (§25.11) → composes with `cascade_policy` (§25.15) | `cascade-cancel` → cancel not-yet-dispatched + record in-flight; `proceed` → `degraded=true` partial; `pause` → pause. |
| `cascade-cancel` branch failure | `TaskGroup` structured cancellation (§25.15) | Run-level `RunStatus.FAILED`; each branch's `terminal_status` persisted (Route-Y sidecar). |
| Engine class outside §25.1 scope | `EngineClassNotYetMaterializedError` (unchanged) | Raised (engine-recovery is R-FS-1 child-arc E). |

The 5 patterns **no longer raise `TopologyPatternNotYetMaterializedError`** (the §25.10 dispatch table replaces the gate). The typed error remains for any *future* non-enumerated topology (the enum is closed-at-6 per C-CP-10 §10.1 / ADR-D4 — extension is a Class-2 D4 revision).

---

## §25.18 (NEW) Deferred to implementation discretion (extension) + recorded forks

**Deferred to implementation discretion (B1-spec-2 / B1-impl, NOT design holes):**
- The concrete async runtime structure of each strategy (TaskGroup nesting, generator vs coroutine) — §25.7 already defers iteration shape; this contract specifies observable behavior.
- `cascade_policy` default propagation at `HIERARCHICAL_DELEGATION` recursion (per ADR-D4 v1.1 §1.11 + C-CP-10 §10.3 deferral).
- The fan-out cardinality cap per pattern (C-CP-10 §10.3 cells give research/content-creation caps; the exact per-cell number is impl discretion).

**Coordinated cascade (the B1 sub-program, per the design §8 enumeration):**
- **B1-spec-1b (IS, coordinated):** the Route-Y `branch_metadata` sidecar (§25.13) — C-IS-05 §5.x, the `procedural_tier_snapshot_ref` template.
- **B1-spec-2 (runtime):** the driver-strategy materialization site; the §25.12 buffered/deferred-append branch path; the **`RunStatus.PARTIAL` runtime projection** — `_CP_TO_RT_STATUS` gains a `PARTIAL → 'partial'` entry + the C-RT-09 `RunResult.status` `Literal` widens to include `'partial'` (exactly mirroring how runtime spec v1.45 added `'paused'` for `RunStatus.PAUSED`); branch `StepExecutionContext` composition.
- **B1-plan / B1-impl-N:** CP + runtime (+ IS) plan decomposition; implement per strategy simplest→hardest (`PARALLELIZATION` → `EVALUATOR_OPTIMIZER` → `ORCHESTRATOR_WORKERS` → `HIERARCHICAL_DELEGATION` → `DECENTRALIZED_HANDOFF`), each with a deterministic-append regression test + a persisted-branch-causality assertion + a cascade-cancel idempotency test + live e2e where a provider step is involved.

**Recorded forks (resolved at this amendment):** (a) contract-shape → in-place §25.10+ extension (`.harness/class_2_fork_b1_spec_1_contract_shape.md`); (b) branch-causality → Route Y (`.harness/class_1_fork_b1_branch_causality_route_x_vs_y.md`); (c) effectful-cancellation C10 → Fork A, council-resolved (`.harness/class_1_fork_b1_effectful_cancellation_c10.md`).

---

## §-preserved-verbatim

| Section | Identity (corrected per v1.13 Reading A) | v1.32 status |
|---|---|---|
| §1 — §16.5.12.X canonical-reading lineage | — | PRESERVED VERBATIM |
| §16.5.1 — §16.5.12.7 substantive content | — | PRESERVED VERBATIM |
| §25.1 — §25.9 | **C-CP-25 — WorkflowDriver** (v1.6 core driver §25.1–§25.8 + v1.5 §25.9 cost-attribution) | PRESERVED VERBATIM (§25.10–§25.18 are additive subsections of this same contract) |
| §26 | **C-CP-26 — PauseResumeProtocol** (+ §26.8 ResumeContext) | PRESERVED VERBATIM |
| §27 | **C-CP-27 — PerServerTrustEvaluator + MCPClientNamespaceEmitter** | PRESERVED VERBATIM |
| §28 | **C-CP-28 — ValidatorFramework** (v1.10 body renamed §25→§28 at v1.13 Reading A; incl. §28.x v1.24 validator post-evaluate hook) | PRESERVED VERBATIM |
| §29 | **C-CP-29 — PromptSelectionManifest** (v1.31) | PRESERVED VERBATIM |

**Label correction note.** This table's §25 and §28 identity labels **correct** the v1.29–v1.31 `§-preserved-verbatim` tables, which mislabeled §25/C-CP-25 as "ValidatorFramework" and labeled §28 by its v1.24 sub-addition ("validator post-evaluate hook") rather than its contract identity (ValidatorFramework). The correction is **forward-only** (the historical change-notes are preserved verbatim); the contract bodies were never affected (§-adjacent observation (a)).

§25.10–§25.18 are additive subsections of the existing C-CP-25 contract; no prior section is amended, reinterpreted, or superseded (the §25.1 deferral is honored-then-lifted, not contradicted).

---

## §-adjacent observations (NOT patched per FM-2)

- **(a) §25/§28 identity drift in v1.29–v1.31 change-note tables — CORRECTED forward at v1.32, Q1 doc-hygiene residual.** The v1.29–v1.31 `§-preserved-verbatim` tables + the v1.31 line-9 inline note labeled §25/C-CP-25 as "ValidatorFramework" (the pre-v1.13-collision label) and §28/C-CP-28 as "validator post-evaluate hook" (its v1.24 sub-addition, not its contract name). The **canonical identity** per v1.13 Reading A (operator-ratified) is §25/C-CP-25 = WorkflowDriver, §28/C-CP-28 = ValidatorFramework. v1.32's `§-preserved-verbatim` table carries the corrected labels; the drift's full back-catalog reconciliation (the historical v1.29–31 notes stay verbatim; any sibling-spec/CLAUDE.md cite-shapes referencing the mislabel) is a Q1 cite-hygiene fold-in, not a contract change. `harness-cp/CLAUDE.md` §1.2's "C-CP-25 ValidatorFramework / … / C-CP-28 validator-hook" parenthetical carries the same mislabel — flagged for the Q1 sweep.
- **(b) `RunStatus` "closed at cardinality 4" docstring is stale.** `workflow_driver_types.py:46` says "Closed at cardinality 4" but the enum now carries 5 values (`SUCCESS / DRAINED / FAILED / PARTIAL / PAUSED` — `PAUSED` added at U-RT-89 / plan v2.20). A Q1 docstring-hygiene nit (the spec §25.2 enum body itself listed 4 + reserved PARTIAL; PAUSED's CP-spec §25.2 acknowledgement is the adjacent (c) item). No behavior impact; B1 introduces no new value.
- **(c) `RunStatus.PAUSED` CP-spec §25.2 acknowledgement.** `PAUSED` exists in code + is projected by the runtime (`_CP_TO_RT_STATUS`, runtime spec v1.45 C-RT-09) but the CP spec §25.2 enum body (v1.6) lists 4 (no PAUSED). A spec/code lineage gap predating B1 (the PauseResumeProtocol cascade landed the value in code/plan/runtime-spec); B1 does not touch §25.2's enum body. Flagged for the Q1 sweep, not patched here (FM-2 narrow-scope).
- **(d) No `dry_run`/`preview` primitive.** The corpus "dry-run-then-approve" discipline (§25.15 obligation 5) is realized by the **committed** C-CP-16 EDIT/REJECT 4-response palette + the `_hitl_required` pre-dispatch ask — NOT a new preview primitive. §25.15 states the *obligation* (gate before dispatch); it invents no primitive (council honesty flag, DELIVERABLE.md).

---

## §-filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_32.md` |
| Authored at | Phase 7 / R-FS-1 arc #3 (B1-spec-1 — CP non-linear topology driver-strategy extension), 2026-06-13 |
| Authoring authority | `.harness/r-fs-1-b1-topology-orchestration-design-v1.md` (cleared B1 design, arc #2) + `.harness/r-fs-1-arc-1-scoping-v1.md` child-arc B1; R-FS-1 §5.0 full-spec directive |
| Predecessor | `Spec_Control_Plane_v1_31.md` (v1.31) |
| Co-published (this PR) | 3 fork docs (`.harness/class_2_fork_b1_spec_1_contract_shape.md`, `.harness/class_1_fork_b1_branch_causality_route_x_vs_y.md`, `.harness/class_1_fork_b1_effectful_cancellation_c10.md`) + council deliverable + adversarial review (`.harness/council/r-fs-1-b1-cascade-cancel/`) + clearance marker `.harness/clearance/Spec_Control_Plane-v1_32-cleared-2026-06-13.md` + `harness-cp/CLAUDE.md` §1.2 row bump. **Owed at post-merge:** the §12.2.1 roadmap fixed-point refresh (a terminating refresh PR, not part of this substantive PR). |
| Coordinated next arcs | B1-spec-1b (IS `branch_metadata` sidecar), B1-spec-2 (runtime driver-strategy materialization + `RunStatus.PARTIAL` projection), B1-plan, B1-impl-N |
| Revision policy | Delta-only spec file per workspace `CLAUDE.md` §2.3 convention; v1.31 body + §25.1–§25.9 + §26–§29 PRESERVED VERBATIM; §25.10–§25.18 are additive subsections of the existing C-CP-25 contract |

---

*End of `Spec_Control_Plane_v1_32.md`. Parent guidance at workspace root `CLAUDE.md`. B1 design at `.harness/r-fs-1-b1-topology-orchestration-design-v1.md`. C-CP-25 WorkflowDriver core at `Spec_Control_Plane_v1_6.md` §25.1–§25.8 + `Spec_Control_Plane_v1_5.md` §25.9. C-CP-10 topology taxonomy at `Spec_Control_Plane_v1_2.md` §10. Council deliverable at `.harness/council/r-fs-1-b1-cascade-cancel/DELIVERABLE.md`.*
