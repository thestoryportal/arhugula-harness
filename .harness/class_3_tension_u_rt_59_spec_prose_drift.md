# Class 3 Tension: U-RT-59 spec-prose-plan-body drift (5 items rolled into one record)

**Class:** 3 — informational; non-blocking.
**Filed:** 2026-05-20, Phase 7 sub-phase 7b, U-RT-59 landing arc.
**Status:** OPEN — landed against actual code surfaces; spec revisions owed at next CP/runtime spec revision pass.

---

## Context

U-RT-59 implementation surfaced 5 small drifts between `Spec_Harness_Runtime_v1.md` v1.6 §14.7 prose and the actual landed library code surfaces. Each is mechanical (no decision required); landed against the real names per `[[spec-prose-plan-body-drift-pattern]]`. Rolled into one Class 3 record so the next spec revision pass can absorb all five together.

---

## §1 `ctx.audit_writer` (not `ctx.audit_ledger_writer`)

**Spec prose:** §14.7.2 step 8 + §14.7.6 reference `ctx.audit_ledger_writer.append(...)` (5 occurrences across §14.7).

**Real code:** `harness-runtime/src/harness_runtime/types.py:1055` declares `audit_writer: AuditLedgerWriter`. The mutable context at `harness-runtime/src/harness_runtime/bootstrap/mutable_context.py:183` is `audit_writer: AuditLedgerWriter | None`. The OD→IS wiring stage at `harness-runtime/src/harness_runtime/lifecycle/od_is_wiring.py:8` cites `ctx.audit_writer.append(tenant_id, audit_entry)`.

**Landing decision:** Land against `ctx.audit_writer` (real name). The class is `RuntimeAuditLedgerWriter` (per the file path) but the HarnessContext attribute is `audit_writer`. Spec prose used the class-name-derived attribute name; reality uses the shorter form.

**Spec revision owed:** s/`ctx.audit_ledger_writer`/`ctx.audit_writer`/g across §14.7.2 step 8 + §14.7.6 (5 occurrences).

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

## Cross-fork pairing

- `[[class_1_tension_u_rt_59_async_sync_step_dispatcher]]` — pairs with §5 above. The Class 1 fork covers the **production INFERENCE_STEP binding** async/sync mismatch (load-bearing, partial-land surfaced); this Class 3 §5 covers the **composer-side prose drift** (resolved by ratification — land sync).
- `[[class_1_tension_u_rt_59_cp_to_od_audit_write_gap]]` — pairs with §1 above. The Class 1 fork covers the **structural type mismatch** between CP `CPAuditLedgerEntry` and OD `AuditLedgerEntry` (load-bearing, halt-route-split STRUCK AC #9 write half); §1 here is the spelling drift (`ctx.audit_writer` not `ctx.audit_ledger_writer`).

---

## Filing footer

| Field | Value |
|---|---|
| Filed by | sub-agent dispatch composer landing arc (U-RT-59 implementation session) |
| Spec revision target | `Spec_Harness_Runtime_v1.md` v1.7 (next runtime spec revision pass) — absorb all 5 items |
| Resolution mode | In-CLI spec edit at next revision per `[[design-substrate-divergence]]` (workspace design-substrate/ is canonical; spec edits in-CLI) |
| Re-evaluation trigger | Next runtime spec revision pass OR when a downstream consumer needs to cite §14.7 byte-exact |
