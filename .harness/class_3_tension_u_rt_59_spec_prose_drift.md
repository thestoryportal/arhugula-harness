# Class 3 Tension: U-RT-59 spec-prose-plan-body drift (8 items rolled into one record)

**Class:** 3 — informational; non-blocking.
**Filed:** 2026-05-20, Phase 7 sub-phase 7b, U-RT-59 landing arc.
**Status:** ✅ 7-OF-8 CLOSED-via-runtime-spec-v1.30-bundled-absorption 2026-05-28 (status-line refreshed 2026-05-28) — items §§1-residual + 2 + 3 + 4 + 5 + 6 + 8 absorbed as canonical-reading amendments at runtime spec v1.29 → v1.30 §1 amendment-site table per delta-only-spec-file convention; v1 baseline body PRESERVED VERBATIM at all 7 sites; downstream readers MUST apply v1.30 §1 substitutions. Production state at HEAD already matches all 7 absorbed readings (spec catches up to production). **Item §7 (step_dispatch_timeout_seconds) CARVED OUT** per X-AL-3 silent-absorption discipline — §7 owes a NEW C-RT-03 RuntimeConfig field with NO current production binding (verified ZERO at all axis src/ trees this session; only a comment marker at `stage_5_loop_init.py:331`). Absorbing §7 into v1.30 as spec-only contract addition would be silent H_T design extension at Phase 7 per workspace `CLAUDE.md` §4.4. §7 routes separately as either (a) Class 1 fork for field addition + production binding arc, or (b) explicit "deferred to step_dispatch_timeout_seconds substantive arc" disposition — operator-discretion timing. Sub-species candidate at v1.30 §"Pattern catalogued": **bundled-absorption of multi-item spec-prose drift at delta-only-spec-file lineage** — distinct from species 3 (resolved-but-carry-stale-inherited); operates on carry-window-duration dimension (22 versions × 8 days carry).

---

## Context

U-RT-59 implementation surfaced 5 small drifts between `Spec_Harness_Runtime_v1.md` v1.6 §14.7 prose and the actual landed library code surfaces. Each is mechanical (no decision required); landed against the real names per `[[spec-prose-plan-body-drift-pattern]]`. Rolled into one Class 3 record so the next spec revision pass can absorb all five together.

**2026-05-20 update (U-RT-59 async/sync fork Path B wiring arc):** items 6 + 7 added per the Path B wiring landing (`d64d8cf`). Item 6 documents the `SyncDispatcherFacade` adapter at the INFERENCE_STEP binding site (transport-adapter detail invisible at the §14.7.7 contract level but worth documenting in a new subsection). Item 7 records the per-step-vs-whole-workflow timeout-budget conflation taken at v1.7 wiring to avoid spec-touching configuration change.

**2026-05-20 update (U-RT-59 topology-admissibility fork Path A arc):** item 8 added per the Path A strict-gate landing (`e52c2da`). Spec §14.7.2 step 4 names `is_admissible(topology, workload_class)` but the composer lands against the union predicate `is_topology_permitted(topology, workload)` (primary ∪ cross-pattern admissible) — the only semantic that accepts the common case of a workload's primary topology. Spec prose absorbs the rename at next revision pass.

---

## §1 `ctx.audit_writer` (not `ctx.audit_ledger_writer`) — **RESOLVED 2026-05-20 at runtime spec v1.7 §14.7.2 step 8d rewrite (partial)**

**Spec prose:** §14.7.2 step 8 + §14.7.6 reference `ctx.audit_ledger_writer.append(...)` (5 occurrences across §14.7).

**Real code:** `harness-runtime/src/harness_runtime/types.py:1055` declares `audit_writer: AuditLedgerWriter`. The mutable context at `harness-runtime/src/harness_runtime/bootstrap/mutable_context.py:183` is `audit_writer: AuditLedgerWriter | None`. The OD→IS wiring stage at `harness-runtime/src/harness_runtime/lifecycle/od_is_wiring.py:8` cites `ctx.audit_writer.append(tenant_id, audit_entry)`.

**Landing decision:** Land against `ctx.audit_writer` (real name). The class is `RuntimeAuditLedgerWriter` (per the file path) but the HarnessContext attribute is `audit_writer`. Spec prose used the class-name-derived attribute name; reality uses the shorter form.

**Spec revision owed:** s/`ctx.audit_ledger_writer`/`ctx.audit_writer`/g across §14.7.2 step 8 + §14.7.6 (5 occurrences).

**Resolution status (2026-05-20).** Runtime spec v1.6 → v1.7 amendment (this session, Fork 2 implementation arc) replaced the §14.7.2 step 8 prose entirely with the Path D + B-revised-a 4-substep sequence (8a–8d). The new step 8d uses `ctx.audit_writer.append(tenant_id, od_entry)` per C-RT-04 canonical field name; the drifted §14.7.2 step 8 occurrences are removed. Remaining occurrences at §14.7.6 (estimated 3-4 of the original 5) are carried as residual; owed to a follow-on Form A patch when §14.7.6 next gets touched. Item 1 marked **RESOLVED for step 8; residual at §14.7.6 carried**.

---

## §2 `harness_cp.topology_subagent_namespace` (not `harness_cp.handoff_context`)

**Spec prose:** §14.7.5 says "v1.6 composer imports the canonical `subagent.*` attribute name set from `harness_cp.handoff_context` (existing; per C-CP-14 §14.2 v1.3 schema)."

**Real code:** The 7 `subagent.*` attribute name carriers live at `harness-cp/src/harness_cp/topology_subagent_namespace.py:106` as `SUBAGENT_NAMESPACE_SCHEMA`. The 2 narrow-subset `topology.*` carriers live at the same module as `TOPOLOGY_NAMESPACE_SCHEMA` (line 81). `harness_cp.handoff_context` holds the typed handoff schemas (`HandoffContext`, `ProposedAction`, `StateSummary`, etc.) — NOT the OTel attribute name carriers.

**Landing decision:** Import from `harness_cp.topology_subagent_namespace` (real carrier module). The composer's `__post_init__` reads `SUBAGENT_NAMESPACE_SCHEMA` + `TOPOLOGY_NAMESPACE_SCHEMA` to derive the frozen attribute-name tuples for downstream emission discipline verification.

**Spec revision owed:** s/`harness_cp.handoff_context`/`harness_cp.topology_subagent_namespace`/ at §14.7.5 "Producer-side attribute carrier reference" paragraph.

---

## §3 `ProposedAction` real shape (3 fields, not 1)

**Spec prose:** §14.7.3 v1.6 MVP composition table row `proposed_action`: "`ProposedAction(text=payload.brief.objective)`".

**Real code:** `harness-cp/src/harness_cp/handoff_context.py:79` declares `ProposedAction` with 3 fields: `action_kind: ActionKind`, `payload: ActionPayload` (= `Mapping[str, Any]`), `brief: SubAgentBrief | None`. There is NO `text` field.

**Landing decision:** Compose `ProposedAction(action_kind=ActionKind.SUB_AGENT_DISPATCH, payload={"objective": brief.objective}, brief=payload.brief)`. The `objective` lives under `payload` (the opaque action payload mapping). The `brief` is populated per ProposedAction's docstring ("Populated when `action_kind == SUB_AGENT_DISPATCH`").

**Spec revision owed:** Replace the `proposed_action` row in §14.7.3 v1.6 MVP composition table:

```
| `proposed_action` | `ProposedAction(action_kind=ActionKind.SUB_AGENT_DISPATCH, payload={"objective": payload.brief.objective}, brief=payload.brief)` | Richer ProposedAction shape per future C-CP-NN |
```

---

## §4 `ChildWorkflowRunner` additive `default_model_binding` kwarg

**Spec prose:** §14.7.4 declares the Protocol with 5 kwargs:

```python
class ChildWorkflowRunner(Protocol):
    async def __call__(
        self,
        *,
        workflow_id: WorkflowID,
        manifest_entry: WorkflowManifestEntry,
        steps: Sequence[WorkflowStep],
        handoff_context: HandoffContext,
        descent: SubAgentGateLevelDescent,
    ) -> RunResult: ...
```

**Real implementation requires 6 kwargs.** `execute_workflow(manifest_entry, steps, run_id, ctx, *, default_model_binding: ModelBinding, step_dispatchers: StepDispatcherRegistry)` (per C-CP-25 §25.2) requires `default_model_binding` for per-step binding resolution per C-CP-06 §6.2. The composer captures `binding.model_binding` at dispatch entry and forwards it to the runner.

**Landing decision:** ChildWorkflowRunner Protocol at `harness-runtime/src/harness_runtime/lifecycle/child_workflow_runner.py:62` carries 6 kwargs (the 5 spec-listed + additive `default_model_binding`). Composer passes `binding.model_binding` per C-CP-13 §13.3 brief-authoring inheritance MVP reading.

**Spec revision owed:** Add `default_model_binding: ModelBinding` to the §14.7.4 Protocol declaration. Document per-field semantics: "Forwarded by composer from parent `binding.model_binding` per C-CP-13 §13.3 brief-authoring inheritance MVP reading."

---

## §5 Sync end-to-end (vs spec-prose async)

**Spec prose:** §14.7.1 declares async `dispatch`; §14.7.4 declares `async def __call__` on the ChildWorkflowRunner Protocol; §14.7.2 step 6 says `await self.child_workflow_runner(...)`.

**Real code:** Stage 1 plumbing landing at `harness-cp/src/harness_cp/workflow_driver.py:175` froze `StepDispatcher` Protocol as **sync** `def dispatch(...)`; `execute_workflow` is sync. The Stage 1 freeze was the de-facto contract.

**Operator ratification:** 2026-05-20 (per AskUserQuestion: "Land sync; file Class 3 spec-prose drift"). Sync end-to-end:
- `RuntimeSubAgentDispatcher.dispatch` is sync.
- `ChildWorkflowRunner` Protocol is sync (`def __call__`).
- Composer step 6 invokes the child runner sync (no `await`).
- Recursive re-entry into `execute_workflow` happens in the same worker thread (the asyncio.to_thread thread that owns the parent driver loop).

**Rationale:** v1.6 scope is single-sub-agent within linear parent — no fan-out concurrency at the composer level. Recursive sync re-entry preserves the existing C-RT-08 worker-thread model unchanged. If post-v1.6 fan-out arc surfaces real async needs, the Protocol shape becomes a separate Class 1 / spec-revision event then (jointly with `[[class_1_tension_u_rt_59_async_sync_step_dispatcher]]`).

**Spec revision owed:** s/`async def`/`def`/g at §14.7.1 dispatcher declaration + §14.7.4 ChildWorkflowRunner Protocol + s/`await self.child_workflow_runner`/`self.child_workflow_runner`/g at §14.7.2 step 6.

---

## §6 `SyncDispatcherFacade` adapter at INFERENCE_STEP binding site (added 2026-05-20)

**Spec prose:** §14.7.7 line 1272 declares the binding as `step_dispatchers = StepKindDispatcherRegistry(dispatchers={StepKind.INFERENCE_STEP: ctx.llm_dispatcher, StepKind.SUB_AGENT_DISPATCH: ctx.sub_agent_dispatcher})` — i.e., `ctx.llm_dispatcher` bound directly. Line 1278 says "Integration with C-RT-15 + C-RT-16 (inner dispatchers). No protocol change to either. The C-RT-16 wrapper is reused verbatim as the `INFERENCE_STEP` dispatcher binding in the registry."

**Real code (v1.7 wiring, commit `d64d8cf`):** `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py:148-167` wraps `ctx.llm_dispatcher` through `SyncDispatcherFacade` via `materialize_sync_dispatcher_facade(result_timeout_seconds=config.drain_timeout_seconds)` and binds `INFERENCE_STEP → facade(llm_dispatcher)` (not `INFERENCE_STEP → ctx.llm_dispatcher`).

**Rationale:** The async `RetryBreakerFallbackDispatcher.dispatch` cannot be bound directly to the sync `StepDispatcher` Protocol the driver consumes (per `[[class_1_tension_u_rt_59_async_sync_step_dispatcher]]` — provider clients are loop-bound via httpx `ConnectionPool`'s anyio.Semaphore; cross-loop reuse via naive `asyncio.run` inside the to_thread worker raises RuntimeError). The facade is a transport adapter that captures the api.py outer loop at construction time and schedules coroutines back via `asyncio.run_coroutine_threadsafe(...).result(timeout=...)` from the worker thread. The C-RT-16 wrapper IS reused verbatim — the facade does not modify or wrap any policy / behavior surface; it is purely a sync→async transport bridge.

**Spec revision owed (v1.7+):** Add a new §14.7.8 subsection "Async/sync transport seam at INFERENCE_STEP binding" documenting:
- The async/sync mismatch between `RetryBreakerFallbackDispatcher.dispatch` (async per §14.6) and the CP-side `StepDispatcher` Protocol (sync per `harness_cp/workflow_driver.py:175`).
- The `SyncDispatcherFacade` adapter pattern (loop capture at stage 5 + `asyncio.run_coroutine_threadsafe` from worker thread + bounded `future.result(timeout=...)`).
- The loop-capture-timing invariant (must construct on the loop that hosts the eventual `asyncio.to_thread`).
- The cancellation-interaction invariant (bounded result_timeout_seconds prevents worker-thread leak when drain timeout fires).
- The framing: the facade is a transport-adapter detail invisible at the C-RT-15/C-RT-16 contract level (those Protocols and behaviors are unchanged). The facade is documented at §14.7.8 (composition-seam discipline) rather than as a contract amendment to §14.6 / §14.7.

Discovery + wiring commits: `84edc30` (facade module + 6 D1-D6 discovery tests) + `d64d8cf` (stage 5 wiring + D7-D8 integration tests + AC #11 bootstrap-end-to-end verification).

---

## §7 Per-step-vs-whole-workflow timeout-budget conflation at v1.7 wiring (added 2026-05-20)

**Spec prose:** §11 declares `drain_timeout_seconds` as the **whole-workflow drain shutdown** bound. The spec does NOT (at v1.6) declare a per-step dispatch timeout budget separate from drain timeout.

**Real code (v1.7 wiring, commit `d64d8cf`):** `stage_5_loop_init.py:159-167` constructs the facade with `result_timeout_seconds=config.drain_timeout_seconds`. This **conflates** the per-step worker-thread blocking bound (`SyncDispatcherFacade.dispatch`'s `future.result(timeout=...)`) with the whole-workflow drain bound. A single hung dispatch can therefore consume the entire drain-timeout budget before the worker unblocks.

**Rationale for v1.7 conflation:** Avoiding a spec-touching `RuntimeConfig` addition at this arc keeps the wiring landing zero-spec-edit. The facade's `result_timeout_seconds` is constructor-supplied, so a future config split is mechanical (add `step_dispatch_timeout_seconds: float = <default>` to `RuntimeConfig` at C-RT-03, thread to stage 5 facade construction).

**Spec revision owed (v1.7+):** Add `step_dispatch_timeout_seconds: float = <default>` to the C-RT-03 `RuntimeConfig` schema with documented semantics:
- Default: smaller than `drain_timeout_seconds` (suggested 30s vs drain's 60s; operator-tunable).
- Bounds the per-step `SyncDispatcherFacade.dispatch` worker-thread wait for the inner coroutine to complete.
- On expiry: raises `TimeoutError` which the driver maps via the existing C-CP-25 §25.3.3.4 typed try/except path.
- Independent of `drain_timeout_seconds`: a single step's hang cannot consume the whole drain budget.

Update stage 5 wiring to thread `config.step_dispatch_timeout_seconds` (not `config.drain_timeout_seconds`) into `materialize_sync_dispatcher_facade(...)`.

Companion retirement-event reference: `.harness/phase-7d-retirement-events-batch-5.md` §0 documents the v1.7 wiring posture; the conflation is bounded and reversible.

---

## §8 Predicate name correction at composer step 4 (added 2026-05-20)

**Spec prose** (§14.7.2 step 4):

> "Verify topology admissibility. `topology = ctx.topology_dispatcher.dispatch(payload.child_manifest_entry)` (returns `TopologyPattern` enum value per C-CP-10 §10.1). `admissible = is_admissible(topology, payload.child_manifest_entry.workload_class)` (per C-CP-10 §10.3). If not admissible, raise typed `SubAgentDispatchTopologyInadmissibleError` mapping to a new fail class."

**Real code (post-fork-3 resolution, commit `e52c2da`):**

```python
topology = self.topology_dispatcher.dispatch(payload.child_manifest_entry)
workload = payload.child_manifest_entry.workload_class
if not self.topology_dispatcher.is_topology_permitted(topology, workload):
    raise SubAgentDispatchTopologyInadmissibleError(...)
```

**Predicate change:** `is_admissible(...)` → `is_topology_permitted(...)`.

**Rationale.** `is_admissible(pattern, workload)` per C-CP-10 §10.3 answers "is `pattern` an admissible *non-primary* cross-pattern alternative for `workload`?" — the §10.3 table annotates non-primary alternatives only. Naive use as the composer gate rejects every workload's primary topology (per `[[class_1_tension_u_rt_59_topology_admissibility_predicate]]`). The composer's intent at step 4 is "is `pattern` admissible at all for `workload`?" — primary OR cross-pattern. Path A resolution: add `is_topology_permitted_for_workload(pattern, workload)` at `harness_cp.per_workload_class_topology` (membership in the workload's `permitted_patterns` set, constructed as primary topologies ∪ admissibility-closed cross-patterns); add `is_topology_permitted(...)` delegate method to `RuntimeTopologyDispatcher` + `TopologyDispatcher` Protocol; composer step 4 gates on this predicate.

**Spec revision owed (v1.7+):** Update §14.7.2 step 4 to name `is_topology_permitted(topology, workload_class)` (or its CP-side equivalent `is_topology_permitted_for_workload(topology, workload_class)`) instead of `is_admissible(...)`. Update narrative: "Verify topology admissibility. `topology = ctx.topology_dispatcher.dispatch(payload.child_manifest_entry)`. `permitted = is_topology_permitted(topology, payload.child_manifest_entry.workload_class)` (per C-CP-11 §11.1 primary topologies ∪ C-CP-10 §10.3 cross-pattern admissibility union). If not permitted, raise typed `SubAgentDispatchTopologyInadmissibleError`." Reference the C-CP-11 §11.1 commitment row + the C-CP-10 §10.3 cross-pattern set as the union sources.

Optionally also amend the spec §14.7 narrative or add a §14.7.x subsection clarifying the union-predicate semantic so future composer authoring does not repeat the §10.3-only-reading defect.

Discovery + landing reference: `.harness/class_1_tension_u_rt_59_topology_admissibility_predicate.md` Path A resolution at commit `e52c2da`.

---

## Cross-fork pairing

- `[[class_1_tension_u_rt_59_async_sync_step_dispatcher]]` — pairs with §5 above. The Class 1 fork covers the **production INFERENCE_STEP binding** async/sync mismatch (load-bearing, partial-land surfaced); this Class 3 §5 covers the **composer-side prose drift** (resolved by ratification — land sync).
- `[[class_1_tension_u_rt_59_cp_to_od_audit_write_gap]]` — pairs with §1 above. The Class 1 fork covers the **structural type mismatch** between CP `CPAuditLedgerEntry` and OD `AuditLedgerEntry` (load-bearing, halt-route-split STRUCK AC #9 write half); §1 here is the spelling drift (`ctx.audit_writer` not `ctx.audit_ledger_writer`).

---

## Filing footer

| Field | Value |
|---|---|
| Filed by | sub-agent dispatch composer landing arc (U-RT-59 implementation session) |
| Spec revision target | `Spec_Harness_Runtime_v1.md` v1.7 (next runtime spec revision pass) — absorb all 8 items |
| Resolution mode | In-CLI spec edit at next revision per `[[design-substrate-divergence]]` (workspace design-substrate/ is canonical; spec edits in-CLI) |
| Re-evaluation trigger | Next runtime spec revision pass OR when a downstream consumer needs to cite §14.7 byte-exact |
