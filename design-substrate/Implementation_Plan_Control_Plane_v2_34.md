# Implementation Plan: Control Plane — v2.34 (delta over v2.33)

*v2.34 is the CP-axis leg of **R-FS-1 — E-plan** — the atomic-unit decomposition of the E sub-program's two **impl-against-cleared-spec** engine classes (**E-1 EVENT_SOURCED_REPLAY + E-2 WAL_SEGMENT**) into three CP-package units: **U-CP-93** (EVENT_SOURCED_REPLAY engine materialization — deterministic event-history replay), **U-CP-94** (WAL_SEGMENT engine materialization — segment-replay resumption, CP/IS-only), **U-CP-95** (the WAL_SEGMENT engine-layer recovery-loop firing branch → C-CP-49/50 → R-CXA-2 go-live). The runtime substrate + R-CXA-2 activation + the Path-(i) `test_u_rt_95` durable e2e are runtime-homed (runtime plan v2.45 U-RT-121/122); §3.5 is the E aggregate cross-axis DAG home. Authority: `.harness/architect_recommendation_e_engine_fork_vs_impl.md` (E-1/E-2 = impl-against-cleared-spec, NO spec leg; only E-3 RECONCILER_LOOP = narrow fork, OUT of this plan). ZERO spec amendment, ZERO new contract ID, X-AL-3-clean (closed `EngineClass`/`ResumptionKind` enums consumed). v2.33 + earlier PRESERVED VERBATIM per delta-only-plan-chain convention.*

**Status:** Proposed

---

## §0 Change-note (v2.33 → v2.34)

### §0.1 Predecessor

`Implementation_Plan_Control_Plane_v2_33.md` (v2.33 — the R-FS-1 B3-plan CP leg; 2 NEW units U-CP-91/92 for the smart-HITL CP-package surfaces + the §6 O-CP-3 G2c registration).

### §0.2 Revision scope (v2.33 → v2.34)

v2.34 decomposes the **CP-package** surfaces of the E sub-program's two **impl-against-cleared-spec** engine classes (**E-1 EVENT_SOURCED_REPLAY + E-2 WAL_SEGMENT**) into THREE NEW atomic units. Authoritative on fork-vs-impl: `.harness/architect_recommendation_e_engine_fork_vs_impl.md` — E-1/E-2 are impl-against-cleared-spec (C-CP-07 §7.4 explicitly defers their substrate to impl-discretion; the U-CP-56 precedent materialized save-point-checkpoint into `_IN_SCOPE_ENGINE_CLASSES` as impl, "no spec bump required"); only E-3 RECONCILER_LOOP carries a narrow §7.4 fork (OUT of this plan, at its own operator-ratified E-spec-3 leg). The E keystone homing fact: the engine driver / `EngineClass` / consumers / C-CP-49/50 composers are `harness-cp`; the engine recovery loop + #475 Journal substrate + the R-CXA-2 factory are `harness-runtime` (runtime plan v2.45 U-RT-121/122). The CP package owns:

| CP surface | Unit | Authority |
|---|---|---|
| EVENT_SOURCED_REPLAY engine materialization — `_IN_SCOPE_ENGINE_CLASSES` widening (`workflow_driver.py:184`) + `:1445` driver dispatch fork (deterministic event-history replay → `resume_at`) + `resumption.kind=engine_replay` + F2 `idempotency_key` join + the no-re-fire determinism contract + F3 capability-floor verification + consumer updates | **U-CP-93** | C-CP-07 §7.1 row 1 + §7.4 (substrate impl-discretion) + C-CP-08 §8.1 `engine_replay` + §8.2 + §8.3; architect rec §0/§6; U-CP-56 precedent |
| WAL_SEGMENT engine materialization (CP/IS-only) — `_IN_SCOPE` widening + `:1445` dispatch fork (segment replay → `resume_at` via the F2 per-segment metadata) + `resumption.kind=segment_replay` + per-segment F2 join + F3 floors + consumer updates (the Path-(i) `test_u_rt_95` durable e2e is U-RT-122 — it needs the durable substrate + firing) | **U-CP-94** | C-CP-07 §7.1 row 5 + §7.4 ("specific WAL implementation" deferred) + C-CP-08 §8.1 `segment_replay` + §8.2 row 5 + §8.3 |
| WAL_SEGMENT engine-layer recovery-loop firing branch — fire `ctx.engine_recovery_loop.capture_pause`/`.attempt_resume` at the WAL_SEGMENT pause-trigger → C-CP-49/50 emit (duck-typed `ctx`, mirroring the workflow-layer `ctx.pause_resume_protocol` fire at `:1200` — no CP→runtime import) | **U-CP-95** | C-CP-22 §22.1 (engine-layer pause/resume free fns) + C-CP-49/50 (= U-CP-49/50 §16.5.2 composers) + R-CXA-2 (CXA §2.3.2) |

No spec amendment; no new contract ID. The `EngineClass` enum is closed at 5 (`engine_class.py:31-50`) + the `ResumptionKind` taxonomy is closed at 5 (C-CP-08 §8.1); E-1/E-2 **consume cleared closed enumerations** (X-AL-3-clean — no new primitive, architect rec §3). `_IN_SCOPE_ENGINE_CLASSES` is an impl-internal scoping frozenset; widening it is the U-CP-56 move.

| In scope at v2.34 | Out of scope |
|---|---|
| U-CP-93 (EVENT_SOURCED_REPLAY) + U-CP-94 (WAL_SEGMENT resumption, CP/IS-only) + U-CP-95 (WAL_SEGMENT recovery-loop firing branch) | All v2.33 + prior unit bodies — preserved verbatim per §0.3; the Path-(i) `test_u_rt_95` durable e2e is U-RT-122 (runtime v2.45) |
| The E aggregate cross-axis DAG + topological order (§3.5 — arc home) | The runtime substrate + R-CXA-2 activation (U-RT-121/122, runtime plan v2.45) — co-published, cited cross-axis |
| Coverage matrix: +3 CP rows (§4.3) | E-3 RECONCILER_LOOP (narrow §7.4 fork → E-spec-3, operator-ratified); the PathClass IS delta (STATE_LEDGER = existing closed-enum member → AC-level conditional in U-RT-121, NOT an IS amendment) |

### §0.3 Sections preserved verbatim from v2.33

| Section | Status at v2.34 |
|---|---|
| §0 (v2.33 change-note) | Superseded by this §0 (historical record preserved at v2.33) |
| §1 Spec inventory | Refreshed: +3 contract-surface rows (C-CP-07/08 engine resumption ×2; C-CP-22/49/50 recovery-loop firing); all prior rows (incl. the B3 C-CP-19/C-CP-21 + G2c rows) PRESERVED VERBATIM |
| §2 — U-CP-01..U-CP-92 (all prior units) | **PRESERVED VERBATIM** from v2.33 + lineage (delta-only-plan-chain convention) |
| §3 Dependency graph | Revised: +§3.5 E aggregate cross-axis graph; all prior B1 (§3.1–§3.3) + B3 (§3.4) graphs + acyclicity PRESERVED VERBATIM |
| §4 Coverage matrix | Revised: +§4.3 (3 E unit rows); §4.1/§4.2 + all prior PRESERVED VERBATIM |
| §5 Cross-cutting integration units | Unchanged (no new tri-spec unit at v2.34); all prior preserved verbatim |
| §6 Open items | Extended: +O-CP-4 (the §3.5/companion-§5 R-CXA-2-owned-by-E-2 finding, recorded-not-gated); O-CP-3 + prior PRESERVED VERBATIM |

### §0.4 Authority chain — no operator gate

v2.34 absorbs the **cleared** E-1/E-2 reading (architect rec §0/§6 — operator-set `next_action`=E-plan; E-1/E-2 are impl-against-cleared-spec, determined by C-CP-07 §7.4 byte-exact + the U-CP-56 precedent + I-6, all committed/cleared surfaces). No operator decision owed at this plan-layer arc; ZERO X-AL-3 risk for U-CP-93/94/95 (closed `EngineClass`/`ResumptionKind` enums consumed; no new primitive — architect rec §3). The one finding (R-CXA-2 engine-layer activation homes at E-2/WAL_SEGMENT, not E-1, per the design doc) is a within-impl-against-cleared-spec re-sequencing recorded at §6 O-CP-4, NOT a fork. The ONE genuine operator decision in the E sub-program — the E-3 §7.4 substrate-deferral reconciliation — is OUT of this plan (its own E-spec-3 leg).

### §0.5 Status posture

`Status: Proposed`. Clearance marker filed at `.harness/clearance/Implementation_Plan_Control_Plane-v2_34-cleared-2026-06-15.md`. Sibling co-publication: runtime plan v2.45 (U-RT-121/122). Companion: `.harness/r-fs-1-e-plan-decomposition.md`.

---

## §1 Spec inventory

PRESERVED VERBATIM from v2.32 §1 (incl. the v2.32 C-CP-25 §25.10–§25.18 rows), **plus** (B3 — CP-package surfaces):

| Contract surface | Status at v2.33 |
|---|---|
| C-CP-19 §19.1 (the `gate_level()` `max()` composition + `GateLevelInput`) — the floor-override carrier-shape so a lowered §19.1 floor cell reaches `gate_level()`; F-B3-1 §3.2 PLAN-carrier (U-CP-43), NOT a spec change | Covered at U-CP-91 (consumed cross-axis by runtime U-RT-116) |
| C-CP-21 §21.8 (the per-persona-tier timeout-degradation MODE table, vocab-A `{fail-closed, escalate-secondary-channel, fail-open}`) + ADR-D5 §1.6 — the `TimeoutDegradationKind` reconciliation target | Covered at U-CP-92 (consumed cross-axis by runtime U-RT-119) |
| design §8.2 G2c (`ToolContract.per_tool_gate_level` producer — the deny-row-reaching axis) | §6 O-CP-3 (REGISTERED owed-AS-spec-reconciliation; NOT a unit — AS spec C-AS-03 §3.1 typed schema does not declare the field) |

**Plus** (E — engine-class CP surfaces, v2.34; all rows above PRESERVED VERBATIM from v2.33 §1):

| Contract surface | Status at v2.34 |
|---|---|
| C-CP-07 §7.1 row 1 + §7.4 (event-sourced-replay; substrate deferred to impl-discretion) + C-CP-08 §8.1 `engine_replay` + §8.2 + §8.3 — deterministic event-history replay resumption | Covered at U-CP-93 (E-1; impl-against-cleared-spec, NO spec change) |
| C-CP-07 §7.1 row 5 + §7.4 ("specific WAL implementation" deferred) + C-CP-08 §8.1 `segment_replay` + §8.2 row 5 + §8.3 — append-only segment-log replay resumption | Covered at U-CP-94 (E-2; durable substrate at runtime U-RT-121, cross-axis) |
| C-CP-22 §22.1 (engine-layer pause/resume free fns) + C-CP-49/50 (§16.5.2 composers) + R-CXA-2 CP→IS engine-layer seam | Covered at U-CP-95 (firing branch) + runtime U-RT-122 (durable bind + go-live e2e), cross-axis |

---

## §2 Atomic-unit decomposition

### §2.1 Preserved-verbatim units

U-CP-01..U-CP-90 — PRESERVED VERBATIM from v2.32 + lineage (delta-only-plan-chain convention). The U-CP-80..U-CP-90 bodies (the v2.32 B1-plan NEW units) follow immediately below, PRESERVED VERBATIM as prior units (their bodies were the v2.32 `§2.2 NEW units (11)` block; at v2.33 they are prior units and are preserved unchanged).

### §2.2 NEW units (11) — R-FS-1 B1-plan *(PRESERVED VERBATIM from v2.32)*

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

### §2.3 NEW units (2) — R-FS-1 B3-plan (smart-HITL)

#### U-CP-91 — `GateLevelInput` floor-override carrier-shape (F-B3-1 §3.2 / U-CP-43 plan-carrier)

**Scope.** Extend the `GateLevelInput` carrier (`harness_cp.gate_level_rule`, `frozen, extra="forbid"`) so a §19.1 floor cell lowered by the `HITLAutoApprovePolicy` (the F-B3-1 in-`max()` floor-override) can reach `gate_level()`'s `max()` composition. The override is consumed by the runtime composer (U-RT-116, cross-axis); this CP unit provides the carrier-shape `gate_level()` reads. One coherent carrier-shape change. **This is a CP-PLAN carrier concern, NOT a C-CP-19 §19.1 SPEC change** (F-B3-1 §3.2: the `gate_level()` carrier-shape is a U-CP-43 plan-carrier decision, the override SEMANTICS are cleared at §19.5 + materialized at runtime spec §3.8) — so NO CP-spec fork is spawned.

**Spec linkage.** C-CP-19 §19.1 (the `gate_level(input: GateLevelInput) → GateLevelComputation` composition + the `max(per_tool_gate_level, blast_radius_floor, persona_tier_floor, mcp_server_trust_floor)` the lowered floor feeds; the `PERSONA_TIER_GATE_LEVEL_FLOOR` + `BLAST_RADIUS_GATE_LEVEL_FLOOR` tables the override lowers a cell of). `.harness/class_1_fork_b3_1_hitl_auto_approve_policy_field.md` §3.2 (PRIMARY — the carrier-shape touch is plan-layer, not a CP-spec fork; "a new optional param on `GateLevelInput`, or a separate override argument"). Runtime spec v1.49 §3.8 ("the exact `GateLevelInput` carrier-shape touch is a B3-plan concern (U-CP-43 plan-carrier)"). C-CP-19 §19.4 (the `_hitl_required` predicate the resulting `computed_gate_level` feeds).

**Surfaces affected.** The `GateLevelInput` model (`harness_cp.gate_level_rule`) — the carrier-shape that lets the runtime composer thread a lowered floor cell into `gate_level()`; the `gate_level()` body's per-axis floor materialization (so the lowered cell composes inside `max()` rather than reading the fixed table).

**Signatures introduced or modified** (the carrier-shape is plan-discretion per F-B3-1 §3.2 — two viable readings, NO new contract surface; both make the override an EXPLICIT signal `gate_level()` consults): EITHER (a) a new OPTIONAL override field on `GateLevelInput` (e.g. `persona_floor_override: GateLevel | None = None` / `blast_floor_override: GateLevel | None = None`, default `None` = no-op so existing callers are byte-unaffected) consumed at `gate_level()`'s `persona_floor`/`blast_floor` materialization; OR (b) a new OPTIONAL override **argument** to `gate_level(input, *, floor_overrides=None)` (default `None` = no-op) consulted at the same materialization site. **The "no-new-field, pass-the-already-adjusted-value" path is NOT viable and is explicitly foreclosed** (decorrelated-review catch): `persona_tier`/`blast_radius_tier` are tier ENUMS that `gate_level()` maps through the FIXED `PERSONA_TIER_GATE_LEVEL_FLOOR` / `BLAST_RADIUS_GATE_LEVEL_FLOOR` tables internally — NO `PersonaTier`/`BlastRadiusTier` value maps to `AUTO` for the persona/local-mutation cells, so a lowered floor CANNOT be expressed by substituting a different enum input without faking the enum or bypassing the table lookup. (This is why per-axis the only value-not-enum axis, `per_tool_gate_level`, is degenerate — `per_tool_floor = input.per_tool_gate_level` — but the F-B3-1 override targets the enum-mapped persona/blast cells, which REQUIRE an explicit override carrier.) The unit picks (a) or (b) at impl per F-B3-1 §3.2; both satisfy U-RT-116's solo-READ_ONLY-skip AC. **No new value, no new axis** — the override only lowers an existing floor cell within the existing `max()`.

**Depends on.** (none) — a foundational CP-package carrier-shape change on the existing `GateLevelInput`; the runtime consumer (U-RT-116) depends on THIS, not vice-versa.

**Acceptance criterion (functional).** With the floor-override carrier, a lowered `persona_tier_floor[SOLO]=AUTO` (or `blast_radius_floor[LOCAL_MUTATION]=AUTO`) composes through `gate_level()`'s `max()` to yield the lowered `computed_gate_level` (a test: lowered solo READ_ONLY → `AUTO` → `hitl_required==False`). **Existing callers are byte-unaffected** — a `GateLevelInput` with no override (the default) composes the existing all-table `max()` verbatim (regression test asserts no behavior change for the no-override path). The lowering NEVER lowers a non-targeted axis: `per_tool_gate_level` + `mcp_trust_tier` are never overridden (a `deny`-tier tool still composes `DENY` regardless of the override).

**Acceptance criterion (integration).** Runtime U-RT-116 (cross-axis) threads the `HITLAutoApprovePolicy`-lowered floor through this carrier; a solo READ_ONLY inference under the default policy skips the gate (the smart-HITL headline). Verified by execution at B3-impl-1.

**Notes.** F-B3-1 §3.2 + advisor pre-substantive: "`GateLevelInput` is a U-CP-43 PLAN-carrier concern, not the C-CP-19 SPEC contract → no CP-spec fork." The carrier-shape touch is a real code change (the model is `frozen, extra="forbid"`) but a plan-layer one. No CP-spec file is edited by this unit.

#### U-CP-92 — `TimeoutDegradationKind` vocab reconciliation (vocab-B → vocab-A) + fail-open config-guard (F-B3-2 AC-1/AC-2)

**Scope.** Reconcile the drifted `TimeoutDegradationKind` enum + table from vocab-B `{continue-as-reject, escalate-to-review-board, abort-workflow}` to the canonical vocab-A `{fail-closed, escalate-secondary-channel, fail-open}` (CP §21.8 + ADR-D5 §1.6 + CP §20.6 span value-set); fix the per-persona-tier `TIMEOUT_DEGRADATION_TABLE` (multi → `fail-closed`, NOT `abort-workflow`; team → `escalate-secondary-channel`; solo → `fail-closed`); fix the wrong-section `"C-CP-21 §21.6"` docstring cite to **§21.8**; add the `fail-open`-refused-at-all-tiers config/bootstrap guard (detect-then-refuse); and update the OD-spec / CP-plan / test cross-references. One coherent code-reconciliation change in `harness_cp.hitl_timeout_degradation`. **Consumed cross-axis by runtime U-RT-119** (which dispatches on the reconciled vocab-A mode).

**Spec linkage.** `.harness/class_1_fork_b3_2_timeout_degradation_vocabulary_drift.md` (PRIMARY — RATIFIED reconcile-code→vocab-A 2026-06-14; §1.3 the semantic divergences; §2.2 the reconciliation; §2.5 the corrected dispatch scope). Runtime spec v1.50 §14.8.9 AC-2 (the vocabulary-reconciliation AC — reconcile the enum + fix the table multi→fail-closed + fix §21.6→§21.8 cite + cross-refs; verify by execution the reconciled enum matches CP §21.8 + ADR-D5 §1.6 + CP §20.6) + AC-1 (the `fail-open`-refused config-guard). CP spec v1.2 §21.8 (the canonical per-persona-tier MODE table, vocab-A). ADR-D5 §1.6 (foundational — the same table). CP spec v1.2 §20.6 (the `hitl.timeout.degradation_mode_applied` span value-set, vocab-A).

**Surfaces affected.** `harness_cp.hitl_timeout_degradation` — the `TimeoutDegradationKind` enum values + docstrings (vocab-B → vocab-A), the `TIMEOUT_DEGRADATION_TABLE` per-tier `default_kind`s (the multi `ABORT_WORKFLOW` → `fail-closed` fix; the team `ESCALATE_TO_REVIEW_BOARD` → `escalate-secondary-channel` fix; the solo `CONTINUE_AS_REJECT` → `fail-closed` rename), the wrong-section `§21.6` docstring cites → `§21.8`; a config/bootstrap validation guard refusing `fail-open` at any tier; the OD-spec / CP-plan / test cross-references that name the old vocab; **AND the `harness-runtime` residual vocab-B docstrings** — specifically `harness-runtime/src/harness_runtime/lifecycle/hitl_placement.py:167-171` (a delegation-only method whose docstring carries vocab-B value names + the wrong-section `§21.6` cite; behavior is correct — pure delegation to `on_hitl_timeout` — so it is stale-as-described doc-hygiene after the reconciliation, not a behavior fix). B3-impl-2 MUST sweep `harness-*/src` for residual vocab-B value-names + `§21.6` cites, not just the named OD/CP/test sites (adversarial cross-spec-drift-grep catch).

**Signatures introduced or modified** (transcribed from CP §21.8 + ADR-D5 §1.6 byte-exact — NO invented value; a reconciliation of the existing enum to the cleared vocabulary): `TimeoutDegradationKind = {FAIL_CLOSED="fail-closed", ESCALATE_SECONDARY_CHANNEL="escalate-secondary-channel", FAIL_OPEN="fail-open"}`; `TIMEOUT_DEGRADATION_TABLE` per-tier: solo→`FAIL_CLOSED`; team→`ESCALATE_SECONDARY_CHANNEL` (default) / `FAIL_CLOSED` (configurable); multi→`FAIL_CLOSED` + alerting (`fail-open` prohibited). `on_hitl_timeout(invocation, persona_tier) → TimeoutDegradationKind` signature unchanged (returns the reconciled vocab-A value). A config/bootstrap guard `if any tier's degradation_mode == FAIL_OPEN: raise <typed config error>` (detect-then-refuse; `fail-open` is in the value-set but ADR/CP-granted to NO tier).

**Depends on.** (none) — a foundational CP-package reconciliation of the existing `TimeoutDegradationKind`; the runtime dispatch consumer (U-RT-119) depends on THIS.

**Acceptance criterion (functional — AC-2 vocabulary reconciliation).** `TimeoutDegradationKind` is `{fail-closed, escalate-secondary-channel, fail-open}` (a test asserts the values match CP §21.8 + ADR-D5 §1.6 + the CP §20.6 span value-set, **by execution** — NOT a grep). `TIMEOUT_DEGRADATION_TABLE` maps solo→`fail-closed`, team→`escalate-secondary-channel`, **multi→`fail-closed`** (a contrasting-baseline test asserts multi is NOT `abort-workflow` — the materially-different compliance-tier disposition the drift carried). The `WebhookConfig.degradation_mode ∈ {fail-closed, escalate-secondary-channel}` (already vocab-A at HEAD) now agrees with the reconciled enum (no internal-to-code drift). The `§21.6` docstring cites are corrected to `§21.8`.

**Acceptance criterion (integration — AC-1 fail-open refused at ALL tiers, C10 + X-AL-3).** A deployment configuring `fail-open` at ANY tier is refused at config/bootstrap (the typed config-error raises; a contrasting-baseline test shows the refusal at multi — the explicit ADR/CP prohibition — AND at solo/team — not-yet-granted, a runtime extension beyond the cleared authorities). `fail-open` is NEVER silently honored at the timeout path. Mirrors the F-B3-1 register-don't-extend / multi structural-foreclosure. Runtime U-RT-119 (cross-axis) then dispatches on the reconciled vocab-A mode (the 2 granted modes route through existing surfaces; `fail-open` is unreachable). Verified by execution at B3-impl-2.

**Notes.** F-B3-2 §2.4: the design §6.2 vocab-B framing's heaviest sub-surface (`ESCALATE_TO_REVIEW_BOARD` "review-board re-invocation") DISSOLVES into the already-built `escalate-secondary-channel` webhook path, and `ABORT_WORKFLOW` has no vocab-A equivalent — so the reconciliation SHRINKS the F-B3-2 scope. This is a code-vs-foundational-ADR drift reconciliation in the canonical direction (ADR > spec > plan > code); NO ADR change. `fail-open` is registered-not-granted (granting it would owe ADR-D5 §1.6 + CP §21.8 ratification — a follow-on fork, register-don't-extend per FULL-SPEC).

### §2.4 NEW units (3) — R-FS-1 E-plan (durable-execution engine classes E-1 + E-2)

#### U-CP-93 — EVENT_SOURCED_REPLAY engine materialization (deterministic event-history replay)

**Scope.** Materialize the `EVENT_SOURCED_REPLAY` engine class as impl against the cleared C-CP-07/08 contracts: widen `_IN_SCOPE_ENGINE_CLASSES` (`workflow_driver.py:184`, currently `{PURE_PATTERN_NO_ENGINE, SAVE_POINT_CHECKPOINT}`) to include `EVENT_SOURCED_REPLAY` so the gate at `:1351-1352` no longer raises `EngineClassNotYetMaterializedError`; add a driver dispatch fork at the resume-path `:1445` (an `elif manifest_entry.engine_class is EngineClass.EVENT_SOURCED_REPLAY:` branch analogous to the SAVE_POINT_CHECKPOINT branch) computing `resume_at` by **deterministic replay from the persisted event history** + emit `WorkflowEventClass.RESUMPTION` (when `resume_at > 0`) carrying `resumption.kind = engine_replay` (C-CP-08 §8.1); join the F2 state-ledger on `idempotency_key` (§8.2 row 1); verify the 4 F3 capability-floors hold by behavior (§6.1); update the engine-class consumers. The hand-rolled event-history substrate is impl-discretion per §7.4. One coherent CP-package engine-materialization unit. **Does NOT fire the engine recovery loop** (R-CXA-2 activation homes at E-2 — §6 O-CP-4); **does NOT un-skip `test_u_rt_95`** (EVENT_SOURCED_REPLAY is not a §18.1 DURABLE_ASYNC cell, `test_u_rt_95:129-131`).

**Spec linkage.** C-CP-07 §7.1 row 1 (`event-sourced-replay`: lifecycle = Engine; replay from Event History; activity outputs cached + replayed deterministically) + §7.4 ("Deferred to implementation discretion. Specific engine candidate … Temporal / DBOS / Restate at event-sourced-replay" — the substrate slot E-1 fills hand-rolled per I-6). C-CP-08 §8.1 row `engine_replay` ("Prior steps replay from Event History deterministically; activity outputs cached and replayed; no re-execution of activities") + §8.2 row 1 (engine event history joins F2 on `idempotency_key`; `idempotency_key` is the harness-canonical join) + §8.3 (resumption observable behavior). `.harness/architect_recommendation_e_engine_fork_vs_impl.md` §0/§2/§6 (PRIMARY — impl-against-cleared-spec). U-CP-56 controlling precedent (`402a7ea`: SAVE_POINT_CHECKPOINT added to `_IN_SCOPE` as impl, "no spec bump required"). `engine_class.py:31-34` (the EVENT_SOURCED_REPLAY member; docstring "candidate enumeration deferred per §7.4").

**Surfaces affected.** `harness_cp.workflow_driver` — `_IN_SCOPE_ENGINE_CLASSES` (`:184`); the resume-path dispatch fork (`:1445` region) + a `_determine_resume_at`-analogous event-history replay helper; the `resumption.kind` emission (the `workflow.resumption` span per C-CP-05 §5.2). The hand-rolled event-history substrate (impl-discretion: reuse the F2 IS state-ledger read keyed on `idempotency_key` — the save-point `_determine_resume_at:1974` `read_by_idempotency_key` shape — OR a dedicated append-only event-history log; either satisfies §7.4). The engine-class consumers: `per_engine_class_topology_overlay.py`, `workload_engine_class_matrix.py`, `workload_binding_engine_class_selection.py`. The relevant CP substitution rows.

**Signatures introduced or modified** (impl against cleared closed enums — NO new contract surface): `_IN_SCOPE_ENGINE_CLASSES` gains `EngineClass.EVENT_SOURCED_REPLAY`; a driver dispatch branch routing EVENT_SOURCED_REPLAY to deterministic event-history replay; a replay helper `_determine_event_replay_resume_at(ctx, run_idempotency_key, step_count, …) -> int` (parallel to `_determine_resume_at`); `resumption.kind=engine_replay` on the resumption span. No new public type; the `ResumptionKind` value `engine_replay` is the cleared §8.1 member.

**Depends on.** (none) — a CP-package driver materialization consuming cleared closed enums + the F2 IS read primitive (downstream, CP→IS); no new carrier.

**Acceptance criterion (functional).** A workflow manifest with `engine_class=EVENT_SOURCED_REPLAY` no longer raises `EngineClassNotYetMaterializedError`; on re-entry over a prior run's event history, `resume_at` advances over the contiguous replayed prefix and `WorkflowEventClass.RESUMPTION` emits with `resumption.kind=engine_replay`; post-resumption `step.boundary` spans carry `resumption.is_replay: bool` (§8.3 item 2 — `true` while replaying the prefix, `false` for post-resumption new work; the per-engine-class span **re-emission** semantics under replay remain deferred under the F2-12 [CF-1] carry-forward per §8.3 item 3, so this AC asserts the `is_replay` flag value, not re-emission cadence). **The determinism contract holds by execution** (the explicit AC, now plan-owned since E-spec-1 was dropped — §8.4/`Spec_Control_Plane_v1_2.md:770` deferred span-re-emission to impl, but §8.1 commits "no re-execution of activities"): a replayed side-effecting activity does **NOT** re-fire on replay (a by-execution test with a side-effect counter — the counter is unchanged across a replay of an already-materialized prefix; cached activity outputs are replayed, not recomputed).

**Acceptance criterion (F3 capability-floors — §6.1, resolves design OQ-6).** Four sub-ACs verified by behavior, not enum-membership: (i) `durable_replay_across_restart` — a paused EVENT_SOURCED_REPLAY workflow resumes from the event history **across a simulated process restart** (e2e: a fresh driver instance over the same persisted history); (ii) `idempotency_keyed_exactly_once` — replay via the F2 `idempotency_key` does not double-apply; (iii) `lease_coordination` — lease semantics compose where required; (iv) `observable_lifecycle` — the 8 lifecycle events per C-CP-05 §5.1 emit (integration test).

**Acceptance criterion (integration / regression).** SINGLE_THREADED_LINEAR is **byte-unchanged** (CP §25.10 Invariant 1 — a regression test asserts no behavior change on the existing linear path; the new branch is reached only for `engine_class=EVENT_SOURCED_REPLAY`). The engine-class consumers recognize EVENT_SOURCED_REPLAY without orphaning. Verified by execution at E-impl-1.

**Notes.** Impl-against-cleared-spec per the architect rec — no CP-spec file is edited; the §7.4-deferred substrate slot is filled hand-rolled per I-6 (no Temporal/DBOS/Restate). The simplest honest substrate reuses the F2 IS state-ledger as the event history (each materialized step = a ledger entry read by `idempotency_key`, the save-point precedent), cached activity outputs being the entry payloads — but the exact store is impl-discretion (§7.4). EVENT_SOURCED_REPLAY does NOT activate R-CXA-2 (the recovery-loop snapshot surface is contrived for pure event-replay — §6 O-CP-4); if a natural engine-layer pause boundary surfaces at impl, it earns its own firing unit then.

#### U-CP-94 — WAL_SEGMENT engine materialization (segment replay + per-segment dedup; CP/IS-only)

**Scope.** Materialize the `WAL_SEGMENT` engine class as impl against cleared C-CP-07/08: widen `_IN_SCOPE_ENGINE_CLASSES` to include `WAL_SEGMENT`; add a driver dispatch fork at `:1445` computing `resume_at` by **replay from the last durably-written WAL segment** (reading the F2 per-segment metadata per §8.2 row 5) + emit `WorkflowEventClass.RESUMPTION` carrying `resumption.kind = segment_replay` (§8.1); per-segment idempotent dedup against the F2 ledger; verify the 4 F3 floors at the CP/IS level (§6.1); update the engine-class consumers. WAL_SEGMENT is the canonical DURABLE_ASYNC class (`test_u_rt_95:129-131` maps RECONCILER_LOOP / WAL_SEGMENT to §18.1 DURABLE_ASYNC cells) — **materializing the class here is what lets the Path-(i) `test_u_rt_95` e2e run downstream, but that e2e itself (authoring its currently-vacuous `:368-375` body into a real `execute_workflow` paused→resume cycle + un-skip + flip the Path-(i) fork `class_1_fork_path_i…` CLOSED-DEFERRED → CLOSED-BUILT) is U-RT-122's AC** — it needs the durable U-RT-121 substrate + the U-CP-95 firing branch, so homing it here would require a U-CP-94 → U-RT-121 cross-axis edge the DAG correctly denies (Codex pre-merge catch). One coherent CP-package engine-materialization unit (CP/IS-only; `(none)` dependency). The durable segment-log substrate is U-RT-121 (runtime, cross-axis); the recovery-loop firing is U-CP-95 (separate — §6 O-CP-4). **Does NOT fire the engine recovery loop** (that is U-CP-95).

**Spec linkage.** C-CP-07 §7.1 row 5 (`WAL-segment`: lifecycle = Harness; append-only segment log with per-segment resume; per-segment harness-owned lease) + §7.4 ("specific WAL implementation at WAL-segment class" deferred to impl-discretion). C-CP-08 §8.1 row `segment_replay` ("Replay from WAL segments; per-segment dedup") + §8.2 row 5 (per-segment ledger entries join F2 on `idempotency_key`; segment-resume reads per-segment metadata) + §8.3. `.harness/architect_recommendation_e_engine_fork_vs_impl.md` §0/§6. `.harness/r-fs-1-e-engine-classes-design-v1.md` §4 (WAL_SEGMENT design; the canonical DURABLE_ASYNC class). `test_u_rt_95...py:129-131,347-368` (the Path-(i) skip + DURABLE_ASYNC cell mapping). `engine_class.py:50-53` (the WAL_SEGMENT member; docstring "implementation deferred per §7.4").

**Surfaces affected.** `harness_cp.workflow_driver` — `_IN_SCOPE_ENGINE_CLASSES`; the `:1445` dispatch fork + a segment-replay resume_at helper (reads the F2 per-segment metadata, §8.2 row 5 — a CP→IS read, NOT a read of the runtime substrate, so no CP→RT edge); `resumption.kind=segment_replay`. The engine-class consumers (overlay/matrix/selection). The relevant CP substitution rows. (`harness-runtime/tests/integration/test_u_rt_95_…py` un-skip + skip-reason correction + the `.harness/class_1_fork_path_i_durable_async_engine_class_materialization.md` status flip are **U-RT-122's surfaces** — they need the durable substrate + firing.)

**Signatures introduced or modified** (impl against cleared closed enums — NO new contract surface): `_IN_SCOPE_ENGINE_CLASSES` gains `EngineClass.WAL_SEGMENT`; a driver dispatch branch routing WAL_SEGMENT to segment replay; a `_determine_segment_replay_resume_at(...) -> int` helper (parallel to `_determine_resume_at`, reading per-segment F2 metadata); `resumption.kind=segment_replay`. No new public type; `segment_replay` is the cleared §8.1 member.

**Depends on.** (none) — CP-package driver materialization consuming cleared closed enums + the F2 IS read (CP→IS, downstream). The durable segment-log substrate (U-RT-121) + the firing branch (U-CP-95) compose downstream; U-CP-94 does NOT depend on them (its resume_at reads the F2 ledger, not the runtime substrate).

**Acceptance criterion (functional).** A workflow with `engine_class=WAL_SEGMENT` no longer raises `EngineClassNotYetMaterializedError`; on re-entry the driver's segment-replay dispatch (`:1445`) advances `resume_at` over the materialized segment prefix and emits `WorkflowEventClass.RESUMPTION` with `resumption.kind=segment_replay`; post-resumption `step.boundary` spans carry `resumption.is_replay: bool` (§8.3 item 2 — span re-emission cadence deferred under F2-12 [CF-1] per §8.3 item 3, so the AC asserts the flag value); per-segment dedup against the F2 `idempotency_key` does not double-apply a segment. **U-CP-94 unconditionally owns the CP-clear parts** — the `_IN_SCOPE_ENGINE_CLASSES` widening, the `elif WAL_SEGMENT:` dispatch branch, and the `resumption.kind=segment_replay` emission — which are provable at the CP/IS level alone (a driver test with a fixture F2 ledger). **The `resume_at` substrate SOURCE is impl-discretion per §7.4**: the RECOMMENDED reading derives it from the **F2 IS state-ledger per-segment entries** (§8.2 row 5 clause 1, "per-segment ledger entries join F2 on `idempotency_key`", + the U-CP-56 save-point `_determine_resume_at`→`read_by_idempotency_key` precedent) — a CP→IS read that keeps U-CP-94 foundational `(none)`; this is **also the only reading that avoids a CP→RT cycle** (the CP driver cannot import `harness-runtime`, so it cannot read the U-RT-121 segment-log substrate directly). IF impl finds `resume_at` genuinely needs the runtime segment-log (not F2-derivable per §8.2 row 5 clause 2's "reads per-segment metadata"), that read MUST move to the runtime layer (folded into U-RT-122) — flagged at impl, not pre-asserted here. The cross-axis cycle constraint is what forces the resolution, so no clean CP/IS separation is *claimed* beyond what X-AL-1 guarantees. **The full DURABLE_ASYNC pause-trigger e2e — materializing the vacuous `test_u_rt_95` body into a real `execute_workflow` paused→resume cycle, the un-skip, and the Path-(i) fork flip — is relocated to U-RT-122's AC** (runtime v2.45), because that e2e needs the durable U-RT-121 substrate + the U-CP-95 firing branch; homing it on U-CP-94 would require a U-CP-94 → U-RT-121 cross-axis edge the DAG correctly denies (Codex pre-merge catch). U-CP-94 materializes the class so that full e2e *can* run downstream; it does not own the e2e.

**Acceptance criterion (F3 capability-floors — §6.1).** Four sub-ACs against WAL_SEGMENT for this unit's CP-clear surface: (i) durable-replay-across-restart — a fresh driver instance recomputes `resume_at` over the same prefix under the recommended F2-ledger reading (§8.2 row 5 clause 1); the **full capture→durable-segment→resume-across-process-restart** proof (which exercises the U-RT-121 substrate) is U-RT-122's AC; (ii)-(iv) idempotency / lease / 8-lifecycle-events by integration test. (Per the functional AC, the `resume_at` substrate source is §7.4 impl-discretion; this floor verifies the recommended F2-ledger reading, with the runtime-substrate path deferred to U-RT-122 if impl couples there.)

**Acceptance criterion (integration / regression).** SINGLE_THREADED_LINEAR byte-unchanged (CP §25.10 Invariant 1). Consumers recognize WAL_SEGMENT. Verified by execution at E-impl-2.

**Notes.** Impl-against-cleared-spec — no CP-spec edit. The §7.4-deferred "specific WAL implementation" slot is filled hand-rolled per I-6 (U-RT-121 extends the #475 `JournalEnginePauseResumeSubstrate`). The resume_at read is CP→IS (F2 per-segment metadata, §8.2 row 5), keeping the CP driver free of any `harness_runtime` import. The R-CXA-2 engine-layer activation (firing the recovery loop) is U-CP-95 + U-RT-122 — kept separate to avoid the built-but-vacuous trap (materializing resumption ≠ firing the dormant loop).

#### U-CP-95 — WAL_SEGMENT engine-layer recovery-loop firing branch (`ctx.engine_recovery_loop` → C-CP-49/50)

**Scope.** Wire a genuine production call site that fires the **engine-layer** recovery loop for WAL_SEGMENT: at the WAL_SEGMENT pause-trigger (the per-step pre-entry pause-trigger path, `workflow_driver.py:1493` region — the engine-layer analogue of the workflow-layer `ctx.pause_resume_protocol` fire at `:1200`), invoke `ctx.engine_recovery_loop.capture_pause(...)` on pause and `ctx.engine_recovery_loop.attempt_resume(...)` on resume — which emit `cp.pause-captured` (C-CP-49) + `cp.resume-attempted` (C-CP-50) through the CP→IS wiring, **activating the R-CXA-2 CP→IS engine-layer seam in production**. `ctx.engine_recovery_loop` is consumed **duck-typed** (`Any` on the runtime ctx, exactly as `ctx.pause_resume_protocol`) — NO `harness_cp` → `harness_runtime` import, no cycle. This is the **Unit-B CP-half**: the firing mechanism. The durable substrate it fires against + the durable go-live e2e are U-RT-121 + U-RT-122 (runtime, cross-axis).

**Spec linkage.** C-CP-22 §22.1 (engine-layer pause/resume free functions `capture_pause_snapshot` / `attempt_resume`). C-CP-49 / C-CP-50 (= U-CP-49 / U-CP-50, the §16.5.2 `emit_pause_captured_state_ledger_entry` / `emit_resume_attempted_state_ledger_entry` composers — cleared + built at CP spec §16.5; `pause_resume_protocol.py:856/:951`). CXA §2.3.2 R-CXA-2 (CP→IS engine-layer producer seam). `engine_recovery_loop.py:52/:74` (`RuntimeEngineRecoveryLoop.capture_pause` / `.attempt_resume` — built-but-dormant). `.harness/architect_recommendation_e_engine_fork_vs_impl.md` §5 (C-CP-49/50 + R-CXA-2 go-live = impl-against-cleared-spec, "this leg of the design doc is correct"). `.harness/r-fs-1-e-plan-decomposition.md` §5 (R-CXA-2 owned by E-2).

**Surfaces affected.** `harness_cp.workflow_driver` — a new engine-layer firing branch at the WAL_SEGMENT pause-trigger path (gated on `engine_class == WAL_SEGMENT`), reading `ctx.engine_recovery_loop` duck-typed. No CP-package type change; no CP→runtime import.

**Signatures introduced or modified** (impl — NO new contract surface): a driver branch invoking the existing `ctx.engine_recovery_loop.capture_pause(workflow_id=…, step_id=…, pause_reason=…)` / `.attempt_resume(workflow_id=…, step_id=…, resume_event_id=…, resume_attempt_count=…, resume_at=…)` (the `engine_recovery_loop.py:52/:74` signatures, unchanged). No new public type.

**Depends on.** [U-CP-94] — the firing branch is reachable only once WAL_SEGMENT is materialized + in `_IN_SCOPE` (U-CP-94). (Consumes `ctx.engine_recovery_loop` duck-typed; the durable substrate bind is U-RT-122, cross-axis downstream — U-CP-95 does not import it.)

**Acceptance criterion (functional).** At a WAL_SEGMENT pause-trigger, the driver fires `ctx.engine_recovery_loop.capture_pause` → a `cp.pause-captured` (C-CP-49) state-ledger entry is written; at resume, `.attempt_resume` → a `cp.resume-attempted` (C-CP-50) entry. The emitted entries carry the engine-layer `action_id`s (`cp.pause-captured` / `cp.resume-attempted`), **distinct from** the workflow-layer `cp.pause-resume-protocol` (CP §16.5 / CXA discriminator). Verified by execution (not grep) — the entries land with the correct shape against whatever substrate `ctx.engine_recovery_loop` is bound with.

**Acceptance criterion (integration / regression).** SINGLE_THREADED_LINEAR byte-unchanged (the firing branch is reached only for WAL_SEGMENT). The durable, end-to-end R-CXA-2 go-live proof (against the real segment-log substrate) is U-RT-122's e2e AC. Verified by execution at E-impl-2.

**Notes.** This is the unit that gives `RuntimeEngineRecoveryLoop` its first production caller (its `.capture_pause`/`.attempt_resume` currently fire only in tests — `[[built-but-vacuous-reground-ledger-asis]]`). Kept distinct from U-CP-94 (resumption semantics) per the advisor decomposition: folding the firing into U-CP-94 would let "class in `_IN_SCOPE` + tests green" read as done while the loop stays dormant. The firing call site mirrors the existing workflow-layer `ctx.pause_resume_protocol` fire at `:1200` exactly (duck-typed ctx object) — so no CP→runtime import is introduced.

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

### §3.4 B3 ARC AGGREGATE — cross-axis home (v2.33)

This delta is ALSO the aggregate-graph home for the **B3 arc**; the runtime (v2.44 U-RT-115..120) nodes are integrated here for the full cross-axis topological order. (The §3.1–§3.3 B1 aggregate above is PRESERVED VERBATIM; this §3.4 is the additive B3 aggregate.)

#### §3.4.1 Per-unit dependency lists (B3 nodes)

| Unit | Axis | Depends on |
|---|---|---|
| U-CP-91 (GateLevelInput floor-override carrier) | CP | (none) — foundational CP-package carrier-shape; **runtime consumer depends on this** |
| U-CP-92 (TimeoutDegradationKind vocab reconciliation + fail-open guard) | CP | (none) — foundational CP-package reconciliation; **runtime consumer depends on this** |
| U-RT-115 (resolve_step_blast_radius) | RT | (none) — foundational gate-site blast resolver |
| U-RT-118 (degradation-mode attribute) | RT | (none) — `on_hitl_timeout` persona_tier-only, exists at HEAD |
| U-RT-120 (EDIT replace-not-merge) | RT | (none) — local EDIT-branch change |
| U-RT-116 (HITLAutoApprovePolicy stage-5 + in-`max()` override) | RT | [U-RT-115, U-CP-91 (cross-axis: CP)] |
| U-RT-117 (gate_level-once + palette-thread) | RT | [U-RT-115, U-RT-116] |
| U-RT-119 (timeout-degradation dispatch-on-mode) | RT | [U-RT-118, U-CP-92 (cross-axis: CP)] |

**Composed-existing / registered (cited, NOT dependency edges):** U-RT-119's `escalate-secondary-channel` routes through the already-built §14.8.8 webhook surface (`WebhookDeliveryComposer` C-RT-20 / C-RT-26 + `PauseResumeProtocol`) — landed, no edge. The **G2c `ToolContract.per_tool_gate_level` producer is REGISTERED at §6 O-CP-3** (owed AS-spec reconciliation; NOT a B3 unit, NOT an edge — its impl-vs-fork class belongs to the AS-leg gate). G5 summarization is out of scope (B3-impl-handoff).

#### §3.4.2 B3 topological order

`U-CP-91, U-CP-92, U-RT-115, U-RT-118, U-RT-120` (foundational, no deps) → `U-RT-116` (after U-RT-115 + U-CP-91), `U-RT-119` (after U-RT-118 + U-CP-92) → `U-RT-117` (after U-RT-115 + U-RT-116). A valid linear extension exists ⟹ the B3 graph is a DAG.

#### §3.4.3 B3 acyclicity proof + cross-axis cycle guard

- **Cross-axis edges:** U-RT-116 → U-CP-91 (RT→CP) and U-RT-119 → U-CP-92 (RT→CP). Both run **downstream** in the package-dependency direction (`harness-runtime` → `harness-cp`).
- **CP↔RT cycle guard:** no CP unit (U-CP-91/92) depends on any U-RT-* — both CP units are foundational leaves; the runtime composer READS the CP carrier/enum (RT→CP), the CP package never reads back into runtime. So no CP↔RT cycle.
- **RT-internal:** every RT edge points to a strictly-earlier node (115/118/120 foundational; 116→115; 117→115/116; 119→118). No back-edge.
- **CP-internal:** U-CP-91 + U-CP-92 are independent leaves (no edge between them; no edge to any prior U-CP-*). No back-edge.

⟹ The aggregate B3 graph (8 nodes — 2 CP + 6 RT) is acyclic. The B1 aggregate (§3.1–§3.3) + the CP-axis prior-units DAG (U-CP-01..90) are PRESERVED VERBATIM; the B3 nodes attach without contesting them.

### §3.5 E ARC AGGREGATE — cross-axis home (v2.34)

This delta is ALSO the aggregate-graph home for the **E arc** (E-1/E-2); the runtime (v2.45 U-RT-121/122) nodes are integrated here for the full cross-axis topological order. (The §3.1–§3.4 B1+B3 aggregates above are PRESERVED VERBATIM; this §3.5 is the additive E aggregate.)

#### §3.5.1 Per-unit dependency lists (E nodes)

| Unit | Axis | Depends on |
|---|---|---|
| U-CP-93 (EVENT_SOURCED_REPLAY materialization) | CP | (none) — foundational CP-package driver materialization |
| U-CP-94 (WAL_SEGMENT materialization, CP/IS-only) | CP | (none) — foundational CP-package driver materialization |
| U-RT-121 (WAL segment-log substrate, extend #475) | RT | (none) — implements the existing `EnginePauseResumeSubstrate` Protocol |
| U-CP-95 (WAL_SEGMENT recovery-loop firing branch) | CP | [U-CP-94] |
| U-RT-122 (R-CXA-2 activation: factory bind + go-live e2e) | RT | [U-RT-121, U-CP-95 (cross-axis: CP)] |

**Composed-existing (cited, NOT dependency edges):** U-CP-93/94's event-history / segment resume_at read the already-landed F2 IS `read_by_idempotency_key` primitive (the U-CP-56 `_determine_resume_at:1974` shape) — CP→IS read, no E-unit edge. U-CP-95 consumes the already-built `RuntimeEngineRecoveryLoop` + the C-CP-49/50 §16.5.2 composers (`pause_resume_protocol.py:856/:951`) — landed contracts, no edge. The PathClass placement (`STATE_LEDGER`) is an existing closed-enum member — no IS unit (AC-level conditional in U-RT-121).

#### §3.5.2 E topological order

`U-CP-93, U-CP-94, U-RT-121` (foundational, no deps) → `U-CP-95` (after U-CP-94) → `U-RT-122` (after U-RT-121 + U-CP-95). A valid linear extension exists ⟹ the E graph is a DAG. (E-impl-1 = U-CP-93 alone; E-impl-2 = U-CP-94 → U-RT-121 → U-CP-95 → U-RT-122.)

#### §3.5.3 E acyclicity proof + cross-axis cycle guard

- **Cross-axis edges:** U-RT-122 → U-CP-95 (RT→CP). Runs **downstream** in the package-dependency direction (`harness-runtime` → `harness-cp`).
- **CP↔RT cycle guard:** no CP unit (U-CP-93/94/95) depends on any U-RT-* — U-CP-95 consumes `ctx.engine_recovery_loop` **duck-typed** (`Any` on the runtime ctx, exactly as the workflow-layer `ctx.pause_resume_protocol` at `:1200`); no `harness_cp` → `harness_runtime` import. U-CP-93/94's resume_at reads the F2 IS ledger (CP→IS, downstream), not the runtime substrate. So no CP↔RT cycle.
- **RT-internal:** U-RT-122 → U-RT-121 points to a strictly-earlier node. No back-edge.
- **CP-internal:** U-CP-93 + U-CP-94 are independent leaves; U-CP-95 → U-CP-94 (strictly-lower). No back-edge.

⟹ The aggregate E graph (5 nodes — 3 CP + 2 RT) is acyclic. The B1 (§3.1–§3.3) + B3 (§3.4) aggregates + the CP-axis prior-units DAG (U-CP-01..92) are PRESERVED VERBATIM; the E nodes attach without contesting them.

---

## §4 Coverage matrix

### §4.1 Coverage-matrix delta (v2.32) — CP §25.10–§25.18 *(PRESERVED VERBATIM from v2.32)*

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

### §4.2 Coverage-matrix delta (v2.33) — B3 CP-package surfaces

| Spec contract / design gap | Atomic unit(s) |
|---|---|
| C-CP-19 §19.1 `GateLevelInput` floor-override carrier-shape (F-B3-1 §3.2 PLAN-carrier; runtime spec v1.49 §3.8 "B3-plan concern") | U-CP-91 (consumed cross-axis by runtime U-RT-116) |
| C-CP-21 §21.8 + ADR-D5 §1.6 `TimeoutDegradationKind` vocab reconciliation + CP §20.6 span value-set + fail-open config-guard (F-B3-2 AC-1/AC-2; runtime spec v1.50 §14.8.9) | U-CP-92 (consumed cross-axis by runtime U-RT-119) |
| design §8.2 G2c `ToolContract.per_tool_gate_level` producer | NO unit — §6 O-CP-3 (REGISTERED owed-AS-spec-reconciliation; classification deferred to the AS-leg gate) |

Both new CP units cite ≥1 contract. The B3 runtime-package surfaces (the §3.8 + §14.8.9 spec legs + G1-blast + G2 + G4a + G3 gaps) are covered at **runtime plan v2.44 §4.1a**. All prior C-CP-* rows PRESERVED VERBATIM from v2.32 §4.

### §4.3 Coverage-matrix delta (v2.34) — E engine-class CP surfaces

| Spec contract subsection | Atomic unit(s) |
|---|---|
| C-CP-07 §7.1 row 1 + §7.4 (event-sourced-replay; substrate impl-discretion) + C-CP-08 §8.1 `engine_replay` + §8.2 row 1 + §8.3 | U-CP-93 |
| C-CP-07 §7.1 row 5 + §7.4 ("specific WAL implementation" deferred) + C-CP-08 §8.1 `segment_replay` + §8.2 row 5 + §8.3 | U-CP-94 (durable substrate at runtime U-RT-121, cross-axis) |
| C-CP-22 §22.1 + C-CP-49/50 (§16.5.2 composers) + R-CXA-2 CP→IS engine-layer seam go-live | U-CP-95 (firing branch) + runtime U-RT-122 (durable bind + e2e), cross-axis |
| C-CP-07 §7.4 F3 capability-floors (i)-(iv) per class (design §6.1) | AC-level in U-CP-93 + U-CP-94 (4 sub-ACs each; resolves design OQ-6) |
| design §6.2 PathClass placement (closed 4-class enum; IS-AL-1) | AC-level conditional in runtime U-RT-121 (recommend `STATE_LEDGER` = existing member; F-E-IS sub-fork only if no honest mapping — resolves OQ-3) |
| CP §25.10 Invariant 1 (SINGLE_THREADED_LINEAR byte-unchanged) | AC-level in U-CP-93 + U-CP-94 + U-CP-95 |
| EVENT_SOURCED_REPLAY → §18.1 DURABLE_ASYNC cell? (design OQ-2) | RESOLVED — NO (`test_u_rt_95:129-131`); the `test_u_rt_95` durable e2e lands at E-2 (U-RT-122, runtime v2.45 — needs the durable substrate + firing), gated on WAL_SEGMENT materialization (U-CP-94); U-CP-93 (E-1) is unrelated to `test_u_rt_95` |
| E-3 RECONCILER_LOOP semantics + §7.4 reconciliation | OUT of scope — narrow Class-1 fork at E-spec-3 (operator-ratified; architect rec §6) |

**No silent gap (E scope).** Every E-1/E-2-scope cleared subsection + every design §6 cross-cutting surface → a unit OR an explicit AC-level / out-of-scope disposition. The one surfaced finding (R-CXA-2 owned by E-2, not E-1) is §6 O-CP-4. §4.1/§4.2 + all prior coverage PRESERVED VERBATIM.

---

## §5 Cross-cutting integration units

**U-CP-84 (`branch_metadata.terminal_status` write-cadence)** — the one tri-spec cross-cutting integration unit the B1 arc adds (CP §25.13 producer + IS §5.4 carrier + runtime §2.2c deliverable). Consolidation rationale: the write-cadence is a single producer-cadence change at the branch-drain site that discharges three coordinated spec surfaces; atomizing it per-spec would fragment one coherent change. Full body at §2.2 above.

**No new cross-cutting integration unit at v2.33 (B3).** The two B3 CP units (U-CP-91 carrier-shape; U-CP-92 vocab reconciliation) are single-package surfaces consumed cross-axis by simple consumer→carrier reads (U-RT-116 / U-RT-119), not multi-spec coordinated producer-cadence changes — so neither is a cross-cutting integration unit.

All prior §5 cross-cutting units PRESERVED VERBATIM from v2.31/v2.32.

---

## §6 Open items

**O-CP-1 — CP §25.18 deferred-to-implementation items (implementer-discretion; NOT units).** Per CP spec v1.32 §25.18, the following are deferred to B1-impl discretion and are NOT decomposed into units (the planner does not make spec-deferred decisions): (a) the concrete async runtime structure of each strategy (`TaskGroup` nesting, generator vs coroutine); (b) `cascade_policy` default propagation at `HIERARCHICAL_DELEGATION` recursion (ADR-D4 v1.1 §1.11 + C-CP-10 §10.3 deferral); (c) the fan-out cardinality cap per pattern (C-CP-10 §10.3 cells give research/content-creation caps; the exact per-cell number is impl-discretion); (d) the concrete `DriverStrategy` shape (callable vs class) at U-CP-80; (e) the buffer type at U-CP-82. The B1-impl-N executor resolves these at implementation; each is bounded by the cited contract's observable-behavior commitment.

**O-CP-2 — CP §25.18 recorded forks (already resolved at the spec; no plan action).** The three forks (contract-shape → in-place §25.10+ extension; branch-causality → Route Y; effectful-cancellation C10 → Fork A) were resolved at the CP spec v1.32 amendment (PR #529); no plan-layer fork action is owed. Recorded for traceability.

**O-CP-3 — G2c `ToolContract.per_tool_gate_level` producer (REGISTERED owed-AS-spec-reconciliation; NOT a unit; classification deferred to the AS-leg gate).** The B3 design §4.1 (G2c) framed the `per_tool_gate_level` producer as a "faithful carrier factor-out (the U-CP-00c precedent)" — pure impl. **Direct read of the AS spec at HEAD `a356929` partially falsifies that framing and the disposition is therefore REGISTERED-not-decided here:**

- AS spec **C-AS-03 §3.1** (the TYPED `ToolContract` field schema) declares only `name` / `description` / `input_schema` / `output_schema` / `minimum_tier` / `blast_radius_tier` / `required_secrets` — there is **NO `per_tool_gate_level` typed field** on the `ToolContract` contract (the landed `harness_as.tool_contract.ToolContract` matches this).
- `per_tool_gate_level` appears in the AS spec ONLY as (i) a `gate_level(...)` **formula axis** at C-AS-12 §12.1 (`# C4 contract: {auto, ask, deny}`) and (ii) a SKILL.md/MCP-manifest **authoring-prose token** at C-AS-03 §3-frontmatter (`tier ∈ {auto, ask, deny}`, AS spec line 1155) — NOT a typed field on the §3.1 contract schema.

So materializing `ToolContract.per_tool_gate_level` as a typed field is the **missing-declaration-site shape** (concept spec-committed at §12.1 axis + §3-frontmatter token; declaration site absent on the §3.1 typed schema). Whether that is a **faithful factor-out** (impl-against-cleared-spec, the U-CP-00c precedent shape, which the workspace ratified as a faithful factor-out under an X-AL-2 resolution) **or a contract-surface extension** (FORK) is a **ratification-gate call, NOT the planner's** — and the B3 design §4.1 EXPLICITLY deferred it ("verify at B3-spec whether a thin AS-spec reconciliation is owed vs a pure impl factor-out"). **The completed B3-spec-1/2 arcs touched ZERO AS spec** (F-B3-1 cascade: "AS spec / IS spec / ADR / ADD / PRD ZERO"; F-B3-2 is CP/ADR-only) — so that verification never happened. **The honest disposition: G2c owes an AS-spec reconciliation (an AS-leg of B3-spec that was skipped); its impl-vs-fork classification belongs to that gate.** This open-item:

1. **REGISTERS the owed AS-spec reconciliation** (per the FULL-SPEC directive — nothing dropped; an un-built spec capability is a registered BUILD arc, design back-flow pre-authorized).
2. **Does NOT pre-stamp "fork"** (pre-selecting a fork when the gate might rule impl is the inverse of the Codex-[P2] error the design already corrected).
3. **Does NOT author the G2c carrier body as cleared impl** (the forbidden move — silently impl'ing an un-cleared AS-package contract surface would be the X-AL-3 silent-absorption failure).
4. **Confirms G2c is behaviorally inert-but-harmless until it lands:** the G2 palette-thread (runtime U-RT-117) is cleared impl and lands independently; its deny-row narrowing is inert in production until `per_tool_gate_level` reaches DENY, which requires this carrier — by the design §4.1 arithmetic, wrap-time `gate_level ∈ {AUTO, ASK}` only (persona + blast top at ASK; `per_tool` defaults AUTO), so threading the real `gate_level` (G2) is correct-but-its-deny-payoff-dormant, NO harm. **The smart-HITL headline (G1, runtime U-RT-115/116) does NOT need G2c** — conditional skip lands at B3-impl-1 regardless.

**Routing:** when the AS-leg of B3-spec opens, ground AS spec C-AS-03 §3.1 + C-AS-12 §12.1 + the AS plan, classify impl-vs-fork at that gate, and (if impl) co-publish a thin AS plan amendment (the B1 precedent co-published three plans incl. IS for U-IS-19; G2c mirrors that with AS) OR (if fork) file the AS-spec back-flow. **Surfaced to the operator in the B3-plan deliverable.**

All prior §6 open items (incl. O-CP-3) PRESERVED VERBATIM from v2.31/v2.32/v2.33.

**O-CP-4 — R-CXA-2 engine-layer activation homes at E-2 (WAL_SEGMENT), NOT E-1 (recorded-not-gated; a within-impl-against-cleared-spec re-sequencing, NOT a fork).** Both the E-DESIGN doc (`r-fs-1-e-engine-classes-design-v1.md` §0/§2/§3.3) **AND the architect recommendation §5** (`architect_recommendation_e_engine_fork_vs_impl.md:89` — "the R-CXA-2 CP→IS engine-layer seam goes live at the first real producer (E-1). No fork") attributed the R-CXA-2 CP→IS engine-layer go-live (firing `RuntimeEngineRecoveryLoop` → C-CP-49/50) to **E-1** ("first slice"). **This O-CP-4 therefore OVERRIDES the architect rec §5's E-1 attribution, not merely the design doc** — the architect rec has been annotated at `:89` accordingly. The architect rec's **core verdict survives** (firing C-CP-49/50 from a real driver is impl-not-fork; E-1/E-2 are impl-against-cleared-spec); only the which-class attribution moves. Empirical re-grounding at HEAD `d7102a6` relocates the activation to **E-2 (WAL_SEGMENT)** — three corroborating facts: (1) the recovery loop is a C-CP-22 pause/resume-**SNAPSHOT** surface (`capture_pause_snapshot` captures one `PauseEvent`; `attempt_resume` reads the latest — `pause_resume_protocol.py:131-135`), whereas EVENT_SOURCED_REPLAY's §8.1 semantic is **deterministic replay-from-event-history (no re-execution)** — no discrete snapshot-pause boundary, so forcing the snapshot-loop into pure event-replay is the design-doc-foreclosed "fake producer"; (2) EVENT_SOURCED_REPLAY does **not** map to a §18.1 DURABLE_ASYNC cell (`test_u_rt_95:129-131`); (3) WAL_SEGMENT **is** the canonical DURABLE_ASYNC class whose pause-trigger cycle (`test_u_rt_95`) is the natural engine-layer pause boundary, and its append-then-resume maps cleanly onto the snapshot Protocol (#475's append-JSONL / read-latest is exactly this shape). **Disposition:** Unit B (U-CP-95 firing branch + runtime U-RT-121 substrate + U-RT-122 durable go-live e2e) homes at E-2; U-CP-93 (E-1) delivers event-replay resumption only and does NOT fire the recovery loop. IF a natural engine-layer pause boundary for event-sourced surfaces at E-impl-1, it earns its own firing unit then. This is a plan-level decomposition refinement within impl-against-cleared-spec — no spec touch, no committed-decision sacrifice — driven autonomously per `[[feedback-gate-only-on-meaningful-architecture-change]]`; the design doc's engine-semantics + anti-pattern foreclosures survive unchanged. Full record: `.harness/r-fs-1-e-plan-decomposition.md` §5.

---

## §7 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.34 (delta over v2.33) |
| Authored at | 2026-06-15 |
| Authoring authority | R-FS-1 E-plan; `.harness/architect_recommendation_e_engine_fork_vs_impl.md` (E-1/E-2 impl-against-cleared-spec; cleared reading; operator-set `next_action`=E-plan); C-CP-07 §7.1/§7.4 + C-CP-08 §8.1/§8.2/§8.3 (cleared); design `.harness/r-fs-1-e-engine-classes-design-v1.md` §2-§6 |
| Net delta | +3 NEW units (U-CP-93 EVENT_SOURCED_REPLAY `(none)`; U-CP-94 WAL_SEGMENT resumption, CP/IS-only `(none)`; U-CP-95 WAL_SEGMENT recovery-loop firing branch `[U-CP-94]`) — the Path-(i) `test_u_rt_95` durable e2e is U-RT-122 (runtime v2.45), NOT a CP unit; +1 cross-axis edge (U-RT-122 → U-CP-95, RT→CP downstream — recorded at the E aggregate §3.5); +§4.3 (8 coverage rows); +1 §6 open-item (O-CP-4, R-CXA-2-owned-by-E-2, recorded-not-gated); ZERO spec amendment, ZERO new contract ID, ZERO CP-spec fork (closed `EngineClass`/`ResumptionKind` enums consumed; architect rec §3 X-AL-3-clean) |
| Sibling co-publication | runtime plan v2.45 (U-RT-121 WAL segment-log substrate + U-RT-122 R-CXA-2 activation); clearance markers; workspace `CLAUDE.md` §2.4 + `.harness/claude-artifact-pointers.md` §2.4 plan-head bumps |
| Aggregate E graph | 5 nodes (3 CP + 2 RT), acyclic, topological order at §3.5.2; single cross-axis edge U-RT-122 → U-CP-95 (RT→CP downstream); no CP→RT back-edge (U-CP-95 consumes `ctx.engine_recovery_loop` duck-typed; CP resume_at reads F2 IS). B1 (§3.1–§3.3) + B3 (§3.4) aggregates PRESERVED VERBATIM |
| Forks | ZERO fork in this plan delta. E-1/E-2 are impl-against-cleared-spec (architect rec §0/§6). The ONE genuine operator decision in the E sub-program — the E-3 §7.4 substrate-deferral reconciliation — is OUT of this plan (its own E-spec-3 leg, operator-ratified). O-CP-4 (R-CXA-2 owned by E-2) is a within-impl re-sequencing, NOT a fork. The conditional F-E-IS PathClass sub-fork is owed ONLY if a substrate cannot honestly map to an existing closed `PathClass` member (default: `STATE_LEDGER`). |
| Homing decision | engine driver / `EngineClass` / consumers / C-CP-49/50 composers = `harness-cp` (U-CP-93/94/95); engine recovery loop + #475 Journal substrate + R-CXA-2 factory = `harness-runtime` (U-RT-121/122). The recovery-loop firing branch (U-CP-95) is CP (mirrors the workflow-layer `ctx.pause_resume_protocol` fire at `:1200`, duck-typed — no CP→RT import) |
| E-impl sequence (companion §6) | E-impl-1 = U-CP-93 (EVENT_SOURCED_REPLAY deterministic event-replay; no recovery-loop firing; unrelated to `test_u_rt_95`) → E-impl-2 = U-CP-94 (WAL_SEGMENT segment-replay, CP/IS) + U-RT-121 (durable segment-log substrate) + U-CP-95 (firing branch) + U-RT-122 (durable factory bind + R-CXA-2 go-live e2e **= the `test_u_rt_95` materialization + un-skip + Path-(i) fork flip**) → (separate) E-spec-3 → E-impl-3 = RECONCILER_LOOP |
