# Implementation Plan: Control Plane — v2.32 (delta over v2.31)

*v2.32 is the CP-axis leg of **R-FS-1 arc #6 (B1-plan)** — the atomic-unit decomposition of the B1 sub-program's CP-side amendment, **CP spec v1.32 §25.10–§25.18** (the C-CP-25 WorkflowDriver extension materializing the 5 non-`SINGLE_THREADED_LINEAR` topology patterns). ELEVEN NEW units (U-CP-80..U-CP-90): the driver-strategy dispatch table, the branch `StepExecutionContext` composition (causality + role field), the buffered/deferred-append drain, branch-scoped idempotency, the `branch_metadata.terminal_status` write-cadence (a tri-spec cross-cutting integration unit), `cascade_policy` consumption + cascade-cancel, and the 5 per-pattern strategy units. This delta is the **aggregate-graph home** for the B1 arc (the full cross-axis dependency graph + topological order over CP + runtime + IS units lives at §3). Co-published with runtime plan v2.43 (U-RT-113/114) + IS plan v2.6 (U-IS-19). ZERO spec amendment (CP spec canonical at v1.32). v2.31 + earlier PRESERVED VERBATIM per delta-only-plan-chain convention.*

**Status:** Proposed

---

## §0 Change-note (v2.31 → v2.32)

### §0.1 Predecessor

`Implementation_Plan_Control_Plane_v2_31.md` (v2.31 — the R-PM-1 cascade PR #3 `PromptSelectionManifest` / C-CP-29 §29 decomposition).

### §0.2 Revision scope (v2.31 → v2.32)

v2.32 decomposes **CP spec v1.32 §25.10–§25.18** (cleared at `.harness/clearance/Spec_Control_Plane-v1_32-cleared-2026-06-13.md`, PR #529) into 11 NEW atomic units. All code lands in the CP `WorkflowDriver` carrier (`workflow_driver.py` + `workflow_driver_types.py`); the runtime spec §2.2 (b/c/d) buffered-drain / write-cadence / branch-context surfaces are **CP-driver-internal** and decomposed here (their runtime-spec contract home is satisfied CP-side, runtime plan v2.43 §0.2 cross-references this). No spec amendment; no new contract ID (the units realize the §25.10–§25.18 additive extension of the existing C-CP-25).

| In scope at v2.32 | Out of scope |
|---|---|
| U-CP-80..U-CP-90 (dispatch table / branch context+role / drain / idempotency / write-cadence / cascade_policy / 5 strategies) | All v2.31 + prior unit bodies — preserved verbatim per §0.3 |
| The B1 aggregate cross-axis dependency graph + topological order (§3 — arc home) | The IS carrier (U-IS-19, IS plan v2.6) + the runtime projection/read (U-RT-113/114, runtime plan v2.43) — co-published, cited cross-axis |
| Coverage matrix: +11 rows mapping CP §25.10–§25.17 (§25.18 → §6 Open-items) | CP §25.18 deferred-to-impl items + recorded forks → §6 Open-items (not units) |

### §0.3 Sections preserved verbatim from v2.31

| Section | Status at v2.32 |
|---|---|
| §0 (v2.31 change-note) | Superseded by this §0 (historical record preserved at v2.31) |
| §1 Spec inventory | Refreshed: CP spec → **v1.32** canonical at HEAD; +8 contract-subsection rows (§25.10–§25.17); all prior rows unchanged |
| §2 — U-CP-01..U-CP-79 (all prior units) | **PRESERVED VERBATIM** from v2.31 + lineage (delta-only-plan-chain convention) |
| §3 Dependency graph | Revised: +11 CP nodes + the B1 aggregate cross-axis graph (§3 below); all prior edges + acyclicity preserved verbatim |
| §4 Coverage matrix | Revised: +11 unit columns / +8 contract rows; all prior preserved verbatim |
| §5 Cross-cutting integration units | Extended: +1 (U-CP-84 write-cadence, tri-spec) |
| §6 Open items | Extended per below |

### §0.4 Authority chain — no operator gate

v2.32 absorbs a **cleared** spec amendment (CP v1.32, adversarial CLEAR + Codex + advisor at PR #529; the 3 forks already resolved at the spec). No operator decision owed; ZERO X-AL-3 risk (plan-layer decomposition of a cleared contract). The §25.18 deferred-to-impl items are implementer-discretion (recorded at §6, NOT planner-decided).

### §0.5 Status posture

`Status: Proposed`. Clearance marker filed at `.harness/clearance/Implementation_Plan_Control_Plane-v2_32-cleared-2026-06-13.md`. Sibling co-publications: runtime plan v2.43 + IS plan v2.6.

---

## §1 Spec inventory

PRESERVED VERBATIM from v2.31 §1, **plus** (CP spec v1.32):

| Contract subsection | Status at v2.32 |
|---|---|
| C-CP-25 §25.10 (driver-strategy dispatch table; lifts `_IN_SCOPE_TOPOLOGY`) | Covered at U-CP-80 |
| C-CP-25 §25.11 (per-pattern orchestration contracts + common substrate) | Covered at U-CP-81/82 (substrate) + U-CP-86..90 (5 strategies) |
| C-CP-25 §25.12 (buffered/deferred-append + determinism) | Covered at U-CP-81 (context) + U-CP-82 (drain) |
| C-CP-25 §25.13 (branch causality — Route-Y seam) | Covered at U-CP-81 (causality fields) + U-CP-84 (write-cadence) |
| C-CP-25 §25.14 (B1↔B4 role seam) | Covered at U-CP-81 (`AgentRole` field, CP-half) + U-RT-114 (read, runtime-half) |
| C-CP-25 §25.15 (`cascade_policy` + cascade-cancel, 8 obligations) | Covered at U-CP-85 |
| C-CP-25 §25.16 (branch-scoped idempotency-key) | Covered at U-CP-83 |
| C-CP-25 §25.17 (failure-mode taxonomy extension) | Covered at U-CP-80 (admissibility / no-longer-raises rows) + U-CP-85 (cascade-failure / barrier-deadline rows) |
| C-CP-25 §25.18 (deferred-to-impl + recorded forks) | §6 Open-items (no unit — implementer-discretion / already-resolved forks) |

---

## §2 Atomic-unit decomposition

### §2.1 Preserved-verbatim units

U-CP-01..U-CP-79 — PRESERVED VERBATIM from v2.31 + lineage (delta-only-plan-chain convention).

### §2.2 NEW units (11)

#### U-CP-80 — driver-strategy dispatch table (C-CP-25 §25.10)

**Scope.** Replace the driver's single `_IN_SCOPE_TOPOLOGY` materialization gate with a dispatch table keyed on `manifest_entry.topology` (the C-CP-10 `TopologyPattern` enum), routing each pattern to its strategy; the `SINGLE_THREADED_LINEAR` entry is the existing §25.3 loop verbatim (regression-safe). The 5 non-linear patterns no longer raise `TopologyPatternNotYetMaterializedError`.

**Spec linkage.** C-CP-25 §25.10, §25.10.1. C-CP-25 §25.17 (the failure-mode rows: admissibility-still-rejected-at-binding-time; the 5 patterns no-longer-raise-`NotYetMaterialized`; the typed error remains for any future non-enumerated topology). C-CP-10 §10.1 (`TopologyPattern` 6-class enum) / §10.3 (admissibility — unchanged precondition).

**Surfaces affected.** The driver's topology-materialization gate site (the `_IN_SCOPE_TOPOLOGY` check) → a `topology_pattern → strategy` dispatch table.

**Signatures introduced or modified** (transcribed from §25.10.1): a dispatch map `{TopologyPattern → DriverStrategy}` with the 6 entries (`SINGLE_THREADED_LINEAR` → existing loop; `PARALLELIZATION`/`ORCHESTRATOR_WORKERS`/`HIERARCHICAL_DELEGATION`/`DECENTRALIZED_HANDOFF`/`EVALUATOR_OPTIMIZER` → the §25.11 strategies). The concrete `DriverStrategy` shape (callable vs class) is §25.18 impl-discretion (§6).

**Depends on.** (none) — foundational dispatch surface. (Strategy bodies are separate units; the table routes to them.)

**Acceptance criterion (functional).** `manifest_entry.topology == SINGLE_THREADED_LINEAR` dispatches the existing §25.3 loop (a regression test asserts byte-identical linear behavior). A non-`SINGLE_THREADED_LINEAR` admissible pattern dispatches its strategy and no longer raises `TopologyPatternNotYetMaterializedError`. Admissibility (C-CP-10 §10.3 / C-CP-11 §11.1) is still rejected at workflow-binding time (the §25.10 lift removes only the materialization gate, not admissibility). The runtime §2.2(a) materialization-site invariant holds: no new stage-5 binding is required (O-RT-1, runtime plan v2.43 §6).

**Acceptance criterion (integration).** Each of the 5 strategy units (U-CP-86..90), once landed, is reachable through this table for its pattern (verified as each strategy lands at B1-impl-N).

**Notes.** Impl-order (design §8, simplest→hardest): land the table with `SINGLE_THREADED_LINEAR` + the strategies incrementally (`PARALLELIZATION` → `EVALUATOR_OPTIMIZER` → `ORCHESTRATOR_WORKERS` → `HIERARCHICAL_DELEGATION` → `DECENTRALIZED_HANDOFF`); the table tolerates a not-yet-landed strategy by raising the typed error until its unit lands.

#### U-CP-81 — branch `StepExecutionContext` composition (causality + role fields) (C-CP-25 §25.11/§25.12/§25.14)

**Scope.** Extend the driver's per-step `StepExecutionContext` composition to compose a **branch child context** at branch-spawn — adding the persisted-causality fields (`parent_action_id` = the spawning step's `action_id`; `branch_index` = the 0-based fan-out ordinal) and the branch `AgentRole` field (the CP-half of the §25.14 role seam), threading the descended gate-level via the existing C-CP-12 §12.2 `sub_agent_gate_level_descent`. One coherent `StepExecutionContext`-shape extension. (Split from the buffered-drain per the dependency discipline — the idempotency-key + role-read consumers need the *context*, not the *buffering*.)

**Spec linkage.** C-CP-25 §25.11 (the branch = a sub-sequence under a child `StepExecutionContext`; the common substrate). C-CP-25 §25.12 (the causality fields the buffered path + write-cadence consume). C-CP-25 §25.14 (the `AgentRole` carry, CP-half of the role seam). C-CP-12 §12.2 (descended gate-level, reused). Runtime spec v1.48 §2.2(d) (the branch `StepExecutionContext` composition deliverable — discharged CP-side here). CP spec v1.32 §25.2.1 Path A (the existing `StepExecutionContext` composition this extends).

**Surfaces affected.** The `StepExecutionContext` type (add `parent_action_id`, `branch_index`, `agent_role` fields) and the driver's branch-spawn context-composition point.

**Signatures introduced or modified** (transcribed from §25.11/§25.12/§25.14): `StepExecutionContext` gains `parent_action_id: Identifier`, `branch_index: int`, `agent_role: AgentRole` (branch-scoped; the `SINGLE_THREADED_LINEAR` path composes no branch child context). Gate-level descent via existing `sub_agent_gate_level_descent` (C-CP-12 §12.2). NO redesign of `StepExecutionContext`'s existing fields.

**Depends on.** (none) — foundational branch-substrate unit. (The `AgentRole` newtype + `RoutingManifest`/`PromptSelectionManifest` per-role bindings are pre-existing — R-PM-1 #509; this unit composes the context, it does not author the binding catalog.)

**Acceptance criterion (functional).** Spawning a branch composes a child `StepExecutionContext` with `parent_action_id` = the spawning step's `action_id`, `branch_index` = the 0-based ordinal, `agent_role` set per the strategy's per-worker role, and a gate-level descended per C-CP-12 §12.2 (monotonic). The `SINGLE_THREADED_LINEAR` path composes the existing per-step context verbatim (regression-safe — a test asserts no branch fields are set on the linear path). `(parent_action_id, branch_index)` uniquely identifies a branch even under nested fan-out.

**Acceptance criterion (integration).** The drain (U-CP-82) orders by `branch_index`; the idempotency-key (U-CP-83) reads the branch identity; the write-cadence (U-CP-84) reads `parent_action_id`+`branch_index` to compose `branch_metadata`; the runtime role-read (U-RT-114, cross-axis) reads `agent_role`. All four consume this context's fields (verified at B1-impl-N).

**Notes.** The `agent_role` field is the CP-half of the §25.14 seam; the runtime READ (U-RT-114) makes per-role model routing effective. Per-role *prompt* is B4 (runtime spec §14.5.3).

#### U-CP-82 — buffered/deferred-append drain path + bounded barriers + determinism (C-CP-25 §25.11/§25.12)

**Scope.** Implement the buffered/deferred-append branch-execution path: a branch executes its step bodies + emits telemetry but **buffers** its pending ledger entries (returns an ordered pending-entry list); the orchestrator **drains the buffers through the single `ctx.state_ledger_writer` in branch-index order at the barrier** — never the inline per-step append (which stays `SINGLE_THREADED_LINEAR`-only). Wrap every barrier (`TaskGroup`/`gather` join) in a wall-clock deadline (bounded barriers). Aggregation is a pure function of the ordered result set (determinism; "lowest branch-index on tie").

**Spec linkage.** C-CP-25 §25.12 (D1/D1.b — the buffered drain + the determinism boundary). C-CP-25 §25.11 (the bounded-barriers common-substrate). Runtime spec v1.48 §2.2(b) (the buffered/deferred-append drain through the single writer — discharged CP-side here; the runtime provides the single `ctx.state_ledger_writer`). ADR-F2 v1.2 §Consequences (the single-threaded-write boundary D1 realizes).

**Surfaces affected.** The branch-execution path in the driver (the buffered-append mechanism + the orchestrator barrier-drain); the determinism/tiebreak in aggregation.

**Signatures introduced or modified** (transcribed from §25.12): a branch returns an ordered pending-entry list (buffered); the orchestrator drains through the single `LedgerWriterLike` (`ctx.state_ledger_writer`) in branch-index order. Concrete async structure (`TaskGroup` nesting, buffer type) is §25.18 impl-discretion (§6).

**Depends on.** [U-CP-81] — the drain orders by `branch_index`, a U-CP-81 context field.

**Acceptance criterion (functional).** Running N branches concurrently and draining at the barrier persists their entries in **branch-index order**, NOT completion order — a deterministic-append regression test (with branches whose model calls return out of order) asserts the persisted order is a deterministic function of the ordered step-output set, independent of which branch finished first. The inline per-step append path is unused by the non-linear strategies (a test asserts the `SINGLE_THREADED_LINEAR` path still uses inline append). A stuck branch hitting the barrier deadline does not strand the parent indefinitely (bounded-barrier timeout).

**Acceptance criterion (integration).** A `PARALLELIZATION` workflow (U-CP-86) drains its branches in order; the chain stays single-parent linear (no second `prior_event_hash`).

#### U-CP-83 — branch-scoped idempotency-key composition (C-CP-25 §25.16)

**Scope.** Extend the driver's step idempotency-key composition to include the branch path: `idempotency_key = sha256(run_idempotency_key, step_index, branch_path)` — so N parallel branches at the same declared `step_index` do not collapse to one ledger entry under the IS writer's `idempotency_key`-only dedup (C-IS-07 §7.5).

**Spec linkage.** C-CP-25 §25.16 (the branch-scoped idempotency-key composition). C-IS-07 §7.5 (the keying tuple — the write-key components the dedup operates on; unchanged, the `idempotency_key` is driver-composed from write-args).

**Surfaces affected.** The driver's idempotency-key composition function (`sha256(run_idempotency_key, step_index)` → `+ branch_path`).

**Signatures introduced or modified** (transcribed from §25.16): `idempotency_key = sha256(run_idempotency_key, step_index, branch_path)` where `branch_path` derives from the U-CP-81 branch identity. CP-side write-key composition; NO six-field / hash-chain / ADR change (per §25.16).

**Depends on.** [U-CP-81] — `branch_path` derives from the branch child context's identity (`parent_action_id`/`branch_index`).

**Acceptance criterion (functional).** Two branches at the same `step_index` with distinct `branch_path` compose distinct `idempotency_key`s → both persist (no collapse). The `SINGLE_THREADED_LINEAR` path (no branch) composes the existing `sha256(run_idempotency_key, step_index)` key verbatim (regression-safe). On `api.resume` after a cancel, a branch's terminal entry is read by its branch-scoped key (the resume-terminality precondition, U-CP-85 obligation 7).

#### U-CP-84 — `branch_metadata.terminal_status` write-cadence (cross-cutting: CP §25.13 + IS §5.4 + runtime §2.2c)

*(Cross-cutting integration unit — plan §5; spans three specs.)*

**Scope.** Implement the write-cadence by which the CP `WorkflowDriver` (the **producer**) populates the IS `branch_metadata` sidecar: per-step branch entries carry `branch_metadata` with `terminal_status = None` (causality only — `parent_action_id`/`branch_index` from U-CP-81); a branch's terminal disposition (`cancelled`/`completed`/`timed_out`) is written at a **fresh terminal entry** appended at the barrier drain, **append-only** (never by mutating a prior entry → IS §6.3 chain intact). Single coherent producer-cadence change at the branch-drain site.

**Spec linkage.** C-CP-25 §25.13 (the Route-Y producer obligation — the CP driver composes `branch_metadata` at branch-spawn + termination). IS spec v1.8 §5.4 (the carrier shape + the append-only + dispatch-boundary-disposition invariants — the carrier this cadence populates; the spec defers the cadence here). Runtime spec v1.48 §2.2(c) (the write-cadence deliverable — discharged here). CP spec v1.32 §25.15.2 obl. 3/4 (the terminal_status discrimination: `cancelled` = not-yet-dispatched boundary; `completed`/`timed_out` = in-flight ran; step-outcome at the step's own entry, no `failed`).

**Surfaces affected.** The branch-drain write site in the driver (compose `branch_metadata` per entry; append the terminal entry carrying the disposition).

**Signatures introduced or modified** (transcribed from §25.13 / IS §5.4): the driver composes `BranchMetadata(parent_action_id, branch_index, terminal_status)` (the carrier from U-IS-19) and appends it via `ctx.state_ledger_writer`; per-step entries carry `terminal_status=None`; the terminal entry carries the disposition. NO carrier-shape redesign (that is U-IS-19).

**Depends on.** [U-IS-19 (cross-axis: IS) — the `BranchMetadata` carrier + the `branch_metadata` field], [U-CP-81 — the causality fields composed], [U-CP-82 — the terminal entry is appended at the barrier drain].

**Acceptance criterion (functional).** Each branch step entry persists with `branch_metadata.terminal_status == None` (causality only); at branch termination a fresh terminal entry persists with `terminal_status ∈ {cancelled, completed, timed_out}` — NEVER by mutating a prior entry (a test asserts no persisted entry is re-hashed; the §6.3 chain re-verifies). A ran-and-errored branch's terminal entry is `completed` (not `failed`) — its step failure is recorded at the step's own ordinary entry (§25.15.2 obl. 3).

**Acceptance criterion (integration).** A persisted-branch-causality assertion (CP §25.18): after a fan-out run, `(parent_action_id, branch_index)` reconstructs the branch tree from the ledger, and each branch's terminal disposition is read back discriminating (the audit-completeness invariant, runtime spec §2.2 invariant). Verified at B1-impl-N.

#### U-CP-85 — `cascade_policy` consumption + cascade-cancel (C-CP-25 §25.15)

**Scope.** Consume the declared-but-unconsumed `CascadePolicy` (`pause`/`proceed`/`cascade-cancel`) under fan-out, and implement cascade-cancel per the 8 §25.15.2 obligations: `asyncio.TaskGroup` structured cancellation of not-yet-dispatched siblings; in-flight steps run-to-completion/timeout; a persisted discriminating `terminal_status` per branch (via U-CP-84); branch-scoped idempotency + resume-terminality (via U-CP-83); high-blast-radius effectful steps gate **before** dispatch via the **already-landed** committed chain C-AS-02 → C-CP-19 → C-CP-16. Run-level status: `cascade-cancel`→`FAILED`, `proceed`→`PARTIAL`(+degraded), `pause`→`PAUSED`.

**Spec linkage.** C-CP-25 §25.15, §25.15.1 (the `cascade_policy` semantics table + the run-level status mapping), §25.15.2 (the 8 obligations). C-CP-25 §25.17 (the failure-mode rows: cascade-cancel branch failure → `FAILED` + persisted `terminal_status`; barrier-deadline-exceeded composes with `cascade_policy`). Composes **already-landed** C-AS-02 (sandbox_tier_floor) → C-CP-19 §19.1 (`gate_level` `max()`) → C-CP-16 (4-response palette HITL) — obligation 5; **cited as composed-existing, NO new dependency edge** (these contracts are landed, not B1 units).

**Surfaces affected.** The `CascadePolicy` consumption point under the barrier (the per-policy branch-failure handling) and the cascade-cancel `TaskGroup` cancellation path.

**Signatures introduced or modified** (transcribed from §25.15.1/§25.15.2): per-policy handling at the barrier; `cascade-cancel` = `TaskGroup` cancellation of not-yet-dispatched siblings; the run-level `RunStatus` per the §25.15.1 table (existing `FAILED`/`PARTIAL`/`PAUSED` members — no new value). `cascade_policy` propagation at `HIERARCHICAL_DELEGATION` recursion is §25.18 impl-discretion (§6).

**Depends on.** [U-CP-82 — the buffered/barrier path cascade-cancel operates over], [U-CP-83 — branch-scoped idempotency for resume-terminality], [U-CP-84 — the persisted discriminating `terminal_status`].

**Acceptance criterion (functional).** `cascade-cancel`: a branch failure cancels not-yet-dispatched siblings (`TaskGroup`); in-flight steps run to completion/timeout; each branch persists a discriminating `terminal_status`; run-level `RunStatus.FAILED`. A cascade-cancel idempotency test: on `api.resume`, a branch whose persisted `terminal_status` is `cancelled`/`completed`/`timed_out` is NOT re-dispatched (resume-terminality, obligation 7). `proceed`: ≥1 failed branch → the aggregator sees a partial set (`degraded=true`), run-level `RunStatus.PARTIAL`. `pause`: fan-out halts at the HITL/pause boundary, run-level `RunStatus.PAUSED`. No-gate-bypass-by-buffering: each branch evaluates the pre-dispatch gate before each effectful step (obligation 2) — a test asserts the gate fires before dispatch, not at the drain.

**Acceptance criterion (integration).** A high-blast-radius effectful step under cascade-cancel gates before dispatch via the C-AS-02→C-CP-19→C-CP-16 chain (obligation 5) — at cancel-time it is either not-yet-approved (cleanly cancellable) or operator-approved-and-in-flight (no silent uncompensated effect). The `proceed`→`PARTIAL` run-level outcome projects to `RunResult.status == 'partial'` (runtime U-RT-113, cross-axis). Verified at B1-impl-N.

#### U-CP-86 — `PARALLELIZATION` strategy (C-CP-25 §25.11)

**Scope.** Implement the fan-out-barrier-aggregate strategy: fan out N branches over varied inputs concurrently (cap per C-CP-10 §10.3 research/content-creation cells), hold at the barrier until all finish, fold structured outputs via a synthesis/voting aggregator (deterministic tiebreak = lowest branch-index).

**Spec linkage.** C-CP-25 §25.11 (the `PARALLELIZATION` row + common substrate). C-CP-10 §10.3 (the fan-out cap cells). Reuses U-CP-80 (dispatch), U-CP-82 (drain), U-CP-84 (branch_metadata causality).

**Surfaces affected.** The `PARALLELIZATION` driver strategy.

**Signatures introduced or modified** (transcribed from §25.11): the strategy spawns N branches (child contexts via U-CP-81), buffers + drains (U-CP-82), aggregates deterministically. Fan-out cardinality cap is §25.18 impl-discretion (§6).

**Depends on.** [U-CP-80, U-CP-81, U-CP-82, U-CP-84] — U-CP-81 is a **direct** dependency (the strategy itself composes branch child-contexts at fan-out), not merely transitive via the drain.

**Acceptance criterion (functional).** A `PARALLELIZATION` workflow fans out N branches over varied inputs, barriers until all finish, and aggregates a single result deterministically (lowest-branch-index tiebreak; "first to finish wins" is forbidden — a test with out-of-order completion asserts the aggregate is completion-order-independent). Branch entries persist in branch-index order with `branch_metadata` causality.

**Notes.** Non-degenerate at B1-alone (variation is in inputs, not agent specialization) — the first strategy landed (design §8 impl-order).

#### U-CP-87 — `EVALUATOR_OPTIMIZER` strategy (C-CP-25 §25.11)

**Scope.** Implement the generate→evaluate→(accept | regenerate-with-feedback) loop, bounded by a max-iteration cap; terminal on evaluator-accept or cap. The evaluator/optimizer roles are per-step prompts (R-PM-1 §29 selection — already landed), non-hollow at B1 without B4.

**Spec linkage.** C-CP-25 §25.11 (the `EVALUATOR_OPTIMIZER` row). Reuses U-CP-80 (dispatch), U-CP-82 (buffered-append per the §25.11 common substrate — all 5 non-linear strategies use the buffered path).

**Surfaces affected.** The `EVALUATOR_OPTIMIZER` driver strategy.

**Signatures introduced or modified** (transcribed from §25.11): generate-step → evaluate-step → branch on accept/regenerate, max-iteration cap. Per-step prompts via R-PM-1 §29 (existing). Max-iteration cap value is §25.18 impl-discretion (§6).

**Depends on.** [U-CP-80, U-CP-82].

**Acceptance criterion (functional).** A generate→evaluate loop accepts on evaluator-accept and terminates at the iteration cap otherwise; entries persist via the buffered path. The evaluator/optimizer are distinguished by per-step prompt (R-PM-1 §29) — non-hollow without B4. Sequential; no fan-out branch_metadata required.

**Notes.** Second strategy landed (design §8 impl-order); non-degenerate at B1-alone (roles by per-step prompt).

#### U-CP-88 — `ORCHESTRATOR_WORKERS` strategy (C-CP-25 §25.11/§25.14)

**Scope.** Implement the orchestrator-dispatch-collect strategy: an orchestrator step computes a dynamic worker set, dispatches workers concurrently (per-role specialization via the U-CP-81 `agent_role` field + the runtime role-read U-RT-114), collects at the barrier, composes the final result. Cascade-policy-aware (U-CP-85).

**Spec linkage.** C-CP-25 §25.11 (the `ORCHESTRATOR_WORKERS` row). C-CP-25 §25.14 (per-role specialization — the role seam this strategy exercises). Reuses U-CP-80/82/84/85.

**Surfaces affected.** The `ORCHESTRATOR_WORKERS` driver strategy.

**Signatures introduced or modified** (transcribed from §25.11): orchestrator computes worker set → concurrent dispatch (per-role child contexts) → barrier collect → compose. NO redesign.

**Depends on.** [U-CP-80, U-CP-81, U-CP-82, U-CP-84, U-CP-85].

**Acceptance criterion (functional).** An orchestrator dispatches a dynamic worker set concurrently, each worker under a per-role child context (`agent_role` set, U-CP-81); the barrier collects; the orchestrator composes a final result. With distinct per-role model bindings, workers dispatch against distinct models (non-hollow by per-role model specialization — the U-RT-114 read makes it effective). Cascade-policy applies at worker failure (U-CP-85).

**Notes.** Third strategy (design §8 impl-order); real value needs the role seam (U-CP-81 + U-RT-114) — folded into B1 per D2 so the pattern is non-hollow by construction.

#### U-CP-89 — `HIERARCHICAL_DELEGATION` strategy (C-CP-25 §25.11)

**Scope.** Implement recursive `ORCHESTRATOR_WORKERS` with depth: fan-out cap 3 per parent (C-CP-10 §10.3); gate-level descends per child (C-CP-12 §12.2, via U-CP-81); bottom-up composition (each parent barriers on its children, composes upward). Reuses the `ORCHESTRATOR_WORKERS` strategy recursively.

**Spec linkage.** C-CP-25 §25.11 (the `HIERARCHICAL_DELEGATION` row — "recursive `ORCHESTRATOR_WORKERS`"). C-CP-10 §10.3 (fan-out cap 3/parent). C-CP-12 §12.2 (gate-level descent per child).

**Surfaces affected.** The `HIERARCHICAL_DELEGATION` driver strategy (recursive over `ORCHESTRATOR_WORKERS`).

**Signatures introduced or modified** (transcribed from §25.11): recursive `ORCHESTRATOR_WORKERS` with a depth bound + per-parent fan-out cap 3; bottom-up barrier composition. `cascade_policy` default propagation at recursion is §25.18 impl-discretion (§6).

**Depends on.** [U-CP-88 (recursive `ORCHESTRATOR_WORKERS` — reuses the strategy), U-CP-85 (cascade-policy at recursion)].

**Acceptance criterion (functional).** A 2-level delegation fans out ≤3 children per parent; each child's gate-level is strictly descended (C-CP-12 §12.2 monotonic — a test asserts descent); parents barrier on children and compose bottom-up. Reuses `ORCHESTRATOR_WORKERS` (U-CP-88) at each level — NOT a parallel re-implementation.

**Notes.** Fourth strategy (design §8 impl-order); the `Depends on: [U-CP-88]` edge encodes the spec's "recursive `ORCHESTRATOR_WORKERS`" definition (advisor-flagged — it reuses, not parallels).

#### U-CP-90 — `DECENTRALIZED_HANDOFF` strategy (C-CP-25 §25.11/§25.13)

**Scope.** Implement single-owner-at-a-time sequential handoff: each stage-expert (per-role, via U-CP-81) hands the workflow to the next via a `HandoffContext` (C-CP-13); terminal when no further handoff; `cascade_policy` typically `cascade-cancel` (single-owner) via U-CP-85.

**Spec linkage.** C-CP-25 §25.11 (the `DECENTRALIZED_HANDOFF` row). C-CP-13 (the `HandoffContext` — existing). C-CP-25 §25.14 (per-role stage-experts).

**Surfaces affected.** The `DECENTRALIZED_HANDOFF` driver strategy.

**Signatures introduced or modified** (transcribed from §25.11): sequential ownership transfer via `HandoffContext` (C-CP-13, existing); per-role stage-experts (U-CP-81 `agent_role`); terminal on no-further-handoff.

**Depends on.** [U-CP-80, U-CP-81, U-CP-82, U-CP-84, U-CP-85].

**Acceptance criterion (functional).** A 3-stage pipeline hands ownership stage-to-stage via `HandoffContext` (C-CP-13); each stage-expert is a per-role context (U-CP-81); terminal when no further handoff. Single-owner-at-a-time (no concurrent owners — a test asserts serial ownership). `cascade-cancel` (U-CP-85) applies on stage failure.

**Notes.** Fifth strategy (design §8 impl-order, hardest); the stage-expert specialization leans on the role seam (U-CP-81 + U-RT-114).

---

## §3 Dependency graph (B1 ARC AGGREGATE — cross-axis home)

This delta is the aggregate-graph home for the B1 arc; the IS (v2.6 U-IS-19) + runtime (v2.43 U-RT-113/114) nodes are integrated here for the full cross-axis topological order.

### §3.1 Per-unit dependency lists (B1 nodes)

| Unit | Axis | Depends on |
|---|---|---|
| U-IS-19 | IS | (none) — foundational carrier; **0 outbound** |
| U-CP-80 | CP | (none) — foundational dispatch table |
| U-CP-81 | CP | (none) — foundational branch-context substrate |
| U-RT-113 | RT | (none) — runtime projection of a code-real CP enum member |
| U-CP-82 | CP | [U-CP-81] |
| U-CP-83 | CP | [U-CP-81] |
| U-CP-84 | CP | [U-IS-19 (cross-axis: IS), U-CP-81, U-CP-82] |
| U-CP-85 | CP | [U-CP-82, U-CP-83, U-CP-84] |
| U-CP-86 (PARALLELIZATION) | CP | [U-CP-80, U-CP-81, U-CP-82, U-CP-84] |
| U-CP-87 (EVALUATOR_OPTIMIZER) | CP | [U-CP-80, U-CP-82] |
| U-RT-114 | RT | [U-CP-81 (cross-axis: CP)] |
| U-CP-88 (ORCHESTRATOR_WORKERS) | CP | [U-CP-80, U-CP-81, U-CP-82, U-CP-84, U-CP-85] |
| U-CP-90 (DECENTRALIZED_HANDOFF) | CP | [U-CP-80, U-CP-81, U-CP-82, U-CP-84, U-CP-85] |
| U-CP-89 (HIERARCHICAL_DELEGATION) | CP | [U-CP-88, U-CP-85] |

**Composed-existing (cited, NOT dependency edges):** U-CP-85 composes the already-landed C-AS-02 → C-CP-19 → C-CP-16 gate chain (obligation 5); U-CP-87 reuses R-PM-1 §29 per-step prompt selection; U-CP-90 reuses C-CP-13 `HandoffContext`. These are landed contracts, not B1 units — no edge.

### §3.2 Topological order

`U-IS-19, U-CP-80, U-CP-81, U-RT-113` (foundational, no deps) → `U-CP-82, U-CP-83` → `U-CP-84` → `U-CP-85, U-CP-86, U-CP-87, U-RT-114` → `U-CP-88, U-CP-90` → `U-CP-89`. A valid linear extension exists ⟹ the graph is a DAG.

### §3.3 Acyclicity proof + cross-axis cycle guard

- **Cross-axis edges:** U-CP-84 → U-IS-19 (CP→IS) and U-RT-114 → U-CP-81 (RT→CP). Both run **downstream** in the package-dependency direction (`harness-runtime` → `harness-cp` → `harness-is`).
- **Cycle guard (IS 0-outbound):** no U-IS-* depends on any U-CP-*/U-RT-* (IS is consumer-most-upstream — the invariant that pinned the §5.4 carrier-home "NOT `harness-cp`"). So the inbound edge U-CP-84 → U-IS-19 cannot close a cycle.
- **CP↔RT:** the only CP↔RT edge is U-RT-114 → U-CP-81 (RT→CP); no CP unit depends on any U-RT-* (the CP strategies SET `agent_role` via U-CP-81; the runtime READS it via U-RT-114 — no CP→RT edge). So no CP↔RT cycle.
- **CP-internal:** every CP edge points to a strictly-lower unit in the §3.2 order (80/81 foundational; 82/83 → 81; 84 → 81/82; 85 → 82/83/84; strategies → 80/81/82/84/85; 89 → 88). No back-edge.

⟹ The aggregate B1 graph is acyclic. CP-axis prior-units DAG (U-CP-01..79) PRESERVED VERBATIM; the 11 new CP nodes attach without contesting it.

---

## §4 Coverage matrix

### §4.1 Coverage-matrix delta (v2.32) — CP §25.10–§25.18

| Spec contract subsection | Atomic unit(s) |
|---|---|
| CP §25.10 (driver-strategy dispatch table) | U-CP-80 |
| CP §25.11 (per-pattern + common substrate) | U-CP-81, U-CP-82 (substrate) + U-CP-86, U-CP-87, U-CP-88, U-CP-89, U-CP-90 (strategies) |
| CP §25.12 (buffered drain + determinism + context) | U-CP-81 (context), U-CP-82 (drain) |
| CP §25.13 (branch causality — Route-Y seam) | U-CP-81 (causality fields), U-CP-84 (write-cadence producer) |
| CP §25.14 (role seam) | U-CP-81 (`AgentRole` field, CP-half), U-RT-114 (read, runtime-half — runtime plan v2.43) |
| CP §25.15 (`cascade_policy` + cascade-cancel) | U-CP-85 |
| CP §25.16 (branch-scoped idempotency-key) | U-CP-83 |
| CP §25.17 (failure-mode taxonomy) | U-CP-80 (admissibility / no-longer-raises), U-CP-85 (cascade-failure / barrier-deadline) |
| CP §25.18 (deferred-to-impl + recorded forks) | §6 Open-items (no unit) |
| runtime §2.2(b) drain / §2.2(c) write-cadence / §2.2(d) context | U-CP-82 / U-CP-84 / U-CP-81 (CP-driver-internal code home) |
| IS §5.4 carrier (producer-side) | U-CP-84 (the producer; the carrier shape is U-IS-19, IS plan v2.6) |

Every CP §25.10–§25.17 subsection is covered; §25.18 is dispositioned to §6 (not an uncovered row). Every new unit cites ≥1 contract. All prior C-CP-* rows PRESERVED VERBATIM from v2.31 §4.

---

## §5 Cross-cutting integration units

**U-CP-84 (`branch_metadata.terminal_status` write-cadence)** — the one tri-spec cross-cutting integration unit this arc adds (CP §25.13 producer + IS §5.4 carrier + runtime §2.2c deliverable). Consolidation rationale: the write-cadence is a single producer-cadence change at the branch-drain site that discharges three coordinated spec surfaces; atomizing it per-spec would fragment one coherent change. Full body at §2.2 above.

All prior §5 cross-cutting units PRESERVED VERBATIM from v2.31.

---

## §6 Open items

**O-CP-1 — CP §25.18 deferred-to-implementation items (implementer-discretion; NOT units).** Per CP spec v1.32 §25.18, the following are deferred to B1-impl discretion and are NOT decomposed into units (the planner does not make spec-deferred decisions): (a) the concrete async runtime structure of each strategy (`TaskGroup` nesting, generator vs coroutine); (b) `cascade_policy` default propagation at `HIERARCHICAL_DELEGATION` recursion (ADR-D4 v1.1 §1.11 + C-CP-10 §10.3 deferral); (c) the fan-out cardinality cap per pattern (C-CP-10 §10.3 cells give research/content-creation caps; the exact per-cell number is impl-discretion); (d) the concrete `DriverStrategy` shape (callable vs class) at U-CP-80; (e) the buffer type at U-CP-82. The B1-impl-N executor resolves these at implementation; each is bounded by the cited contract's observable-behavior commitment.

**O-CP-2 — CP §25.18 recorded forks (already resolved at the spec; no plan action).** The three forks (contract-shape → in-place §25.10+ extension; branch-causality → Route Y; effectful-cancellation C10 → Fork A) were resolved at the CP spec v1.32 amendment (PR #529); no plan-layer fork action is owed. Recorded for traceability.

All prior §6 open items PRESERVED VERBATIM from v2.31.

---

## §7 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.32 (delta over v2.31) |
| Authored at | 2026-06-13 |
| Authoring authority | R-FS-1 arc #6 (B1-plan); CP spec v1.32 §25.10–§25.18 (cleared PR #529); design `.harness/r-fs-1-b1-topology-orchestration-design-v1.md` §8 |
| Net delta | +11 NEW units (U-CP-80..90); +1 cross-cutting unit (U-CP-84, tri-spec); +1 cross-axis edge (U-CP-84 → U-IS-19); +8 coverage rows (§25.10–§25.17); +2 §6 open-item groups (O-CP-1/2); ZERO spec amendment, ZERO new contract ID |
| Sibling co-publications | runtime plan v2.43 (U-RT-113 PARTIAL projection + U-RT-114 role-read) + IS plan v2.6 (U-IS-19 carrier); clearance markers; workspace `CLAUDE.md` §2.4 plan-head bumps |
| Aggregate B1 graph | 14 nodes (11 CP + 2 RT + 1 IS), acyclic, topological order at §3.2; cross-axis edges CP→IS + RT→CP (downstream); IS 0-outbound preserved |
| Impl-order (design §8) | foundational (U-CP-80/81, U-IS-19, U-RT-113) → substrate (U-CP-82/83/84/85, U-RT-114) → strategies simplest→hardest (U-CP-86 → U-CP-87 → U-CP-88 → U-CP-89 → U-CP-90), each with deterministic-append regression + persisted-branch-causality assertion + cascade-cancel idempotency test + live e2e per CP §25.18 |
