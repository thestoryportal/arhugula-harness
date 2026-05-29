# Implementation Plan — Harness Runtime (v2.33)

*Delta over v2.32. v2.33 is a Phase 6 back-flow apply pass per `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` §"Path α AUTHORIZED (2026-05-29)" operator-ratified 2026-05-29. Authors NEW atomic unit U-RT-110 decomposing the runtime-side wiring of the 6 CP spec v1.26 §16.5 composers (U-CP-74..U-CP-79, all LANDED on main as of `35744ab`) onto `ctx.ledger_writer.append`. Scope (F) FULL-WIRE-paired per AskUserQuestion 2026-05-29: v2.33 lands the runtime-side binding surface; CP plan v2.29 → v2.30 paired revision owes the 6 CP-axis firing-site invocation units (the production callsites that invoke the runtime wiring methods). H_T-RT-35 PARTIAL → RETIRE-READY transit gated on BOTH plans landing per `[[verification-shape-sharpened-grep-vs-e2e]]` discipline. Gap C runtime spec §12.3 prose drift carried per (C-defer) ratification 2026-05-29 — NOT amended at v2.33 per FM-2; flagged at §3 adjacent observations as owed at next runtime-spec revision pass.*

## §0 Change note (v2.32 → v2.33)

### §0.1 Revision context — Path α authorization absorbs Phase 6 back-flow

Per `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` §"Path α AUTHORIZED (2026-05-29)" operator authorization at this session post-PR #45 fork doc closure-event publication. The fork's §"What remains — runtime-side wiring atomic unit ABSENT at runtime plan v2.32" empirical grep confirms ZERO occurrences of `ledger_writer`, `U-RT-35`, `16.5`, `resolve_step_binding`, `emit_*_state_ledger`, `append_ledger_entry` at v2.32; the runtime plan does not have an atomic unit decomposing the runtime-side wiring of the 6 §16.5 composers to `ctx.ledger_writer.append`. CP plan v2.28 §0 line 55 + line 72 explicitly defer this work to a "separate runtime-plan arc."

The 6 LANDED CP-axis composers all expose a uniform contract per CP spec v1.26 §16.5.7: async free function; kw-only parameters (workflow_id, step_id, per-composer disambiguators, actor); `ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]` kw-only; returns `WriteResult`. Empirical verification at HEAD (commit `35744ab` 2026-05-29) confirms all 6 composers do `return await ledger_writer(payload)` as the single-line composition consumption at the call-out boundary. Uniform signature shape forecloses the spec-line-2315 split-allowed authorization; single unit decomposition is the natural shape.

Architectural ratifications per `Q1=(F)` + `Q2=(C-defer)` AskUserQuestion 2026-05-29:
- **Unit shape**: single unit covering all 6 source-unit wirings (per uniform-signature argument above); mirrors U-CP-34 LANDED precedent at `harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py` (`RuntimeCpIsWiring` dataclass with method-per-source-unit shape).
- **Stage placement**: stage 6 CXA_WIRING per existing bootstrap at `harness-runtime/src/harness_runtime/bootstrap/stage_6_cxa_wiring.py:65` (`materialize_cp_is_wiring_stage(config, ctx.ledger_writer)` already integrated; extension shape preserves the established stage-6 binding contract).
- **Factory shape**: extend existing `RuntimeCpIsWiring` dataclass with 6 NEW methods (one per §16.5.2 composer); no parallel class authored; no new stage authored. The factory `materialize_cp_is_wiring_stage` signature PRESERVED VERBATIM (no new constructor param owed at v2.33 — the existing `ledger_writer: LedgerWriter` field carries all binding needs).
- **Scope (F) FULL-WIRE-paired**: v2.33 lands the runtime-side binding surface (this unit). H_T-RT-35 transit requires paired CP plan v2.29 → v2.30 revision authoring 6 firing-site invocation units that widen the 6 CP-axis production functions to invoke the runtime wiring methods at the canonical post-resolve-pre-return firing sites per CP spec v1.26 §16.5.7 firing-site discipline. The paired-cascade dependency is declared at §3 adjacent observations + at U-RT-110 cross-axis-dependency edges per implementation-planner §7 cross-axis-dependency-callout discipline.

### §0.2 Sections revised

§0 (this change note); §1 NEW unit U-RT-110 body; §2 DAG delta; §3 adjacent observations + carry-forward; §4 filing footer. All v2.32 unit bodies + v2.31 + v2.30 + ... + v1 lineage PRESERVED VERBATIM per delta-only-plan-chain convention. Cluster framing at v2.31 §1.1 + DAG at v2.31 §2 EXTENDED at v2.33 §2 with the single NEW node + 2 within-axis edges + 6 cross-axis-PENDING edges; v2.32 §2 DAG carries forward verbatim under v2.33's extension.

### §0.3 Cross-axis cascade — (F) FULL-WIRE-paired

**Authoring correction (impl-time-grounding-pass 2026-05-29 pre-merge revision).** Initial draft of §0.3 named **CP plan v2.29 → v2.30** as the cascade target, framing the (F) second half as "widening 6 CP-axis production functions' signatures." Impl-time grounding pass against the v2.33 §1.2 Signatures block surfaced that **U-RT-110's methods ARE the firing-site orchestration surface at the runtime axis** — they take `(workflow_id, step_id, per-composer-args, actor)` as kw-only inputs, build the async adapter, await the CP-axis composer, and return `WriteResult`. The U-CP-34 LANDED precedent at `RuntimeCpIsWiring.emit_sibling_ledger_entry` is the structural ancestor: the CP-axis composer is pure (`construct_sibling_ledger_entry` → `EntryPayload`); the runtime wrapper orchestrates the dual-step. v2.33 §1.2 follows that precedent. **The cascade target is therefore runtime plan v2.34 (intra-runtime-axis), NOT CP plan v2.30 (cross-axis).** Per `[[impl-time-grounding-pass-pre-merge-revision]]` workspace discipline + the (S) sibling-variant architectural commitment at parent fork (hold the downstream axis pure; adapt the producer side at one layer up) — the firing-site invocation units belong at runtime axis. Authoring CP-axis production function signature widening + CP spec v1.27 typed-model extension (`WorkloadBindingSelectionInput` + `ResumeAttempt` + `capture_pause_snapshot` widening) to thread workflow context to the CP-axis function would be X-AL-3 silent H_T design extension at Phase 7 — exactly the shape the (S) commitment foreclosed. Operator-ratified (F) FULL-WIRE-paired scope holds; only the cascade target name was hasty at initial authoring. PR #52 force-pushed pre-merge to absorb the correction; mirrors PR #37 / PR #38 in-flight-revision-pre-merge precedent.

Per corrected (F) ratification 2026-05-29, v2.33 establishes a cross-axis cascade owed at **runtime plan v2.33 → v2.34** revision-pass arc:

| Element | Detail |
|---|---|
| Runtime plan v2.34 NEW units owed | 1-3 firing-site invocation units threading U-RT-110's 6 async methods into the production caller paths; cluster shape (single unit vs split) decided at v2.34 authoring per signature-uniformity analysis. Per advisor recommendation at v2.33 impl-time-grounding-pass: likely single unit if uniform; split if disambiguator-availability divergence surfaces at any caller |
| Per-composer caller-site target | (i) `resolve_step_binding(...)` immediate caller at `harness-cp/src/harness_cp/workflow_driver.py:777` + `harness-runtime/src/harness_runtime/lifecycle/override_evaluator.py:61` → calls `ctx.cxa_stages["cp_is_wiring"].wiring.emit_override_state_ledger_entry(workflow_id, step_id, override_id, policy_id, post_override_step_config, actor)` after override resolution; (ii) `select_engine_class(...)` immediate caller (workflow driver workload-binding-time site) → calls `emit_workload_class_selection_state_ledger_entry`; (iii) `PauseResumeProtocol` class method invocation sites at workflow_driver per workflow-layer transitions → calls `emit_pause_resume_state_ledger_entry`; (iv) `rewrite_tool_call_to_hitl(...)` immediate caller (HITL composer at runtime axis) → calls `emit_hitl_tool_call_rewriting_state_ledger_entry`; (v) `capture_pause_snapshot(...)` engine-layer free-function caller (pause-resume composer at runtime axis) → calls `emit_pause_captured_state_ledger_entry`; (vi) `attempt_resume(...)` engine-layer free-function caller → calls `emit_resume_attempted_state_ledger_entry`. CP-axis production function signatures + input types **PRESERVED VERBATIM** at v2.34 — orchestration lives at runtime axis only |
| Implementation-discretion at runtime plan v2.34 | (a) **disambiguator availability** — some composer args (`protocol_event_kind` + `event_sequence_id` at U-CP-30; `semantic_variant_binding_id` at U-CP-37; `pause_event_id` + `resume_event_id` at U-CP-49/50) may require minor return-type extension at the CP-axis production function (expose the disambiguator on the return value) — implementation-discretion at v2.34 per-unit AC, NOT spec extension; (b) **actor source** — verify `StepExecutionContext.parent_actor` (per `Spec_Control_Plane_v1_6.md` §25.2.1) is reachable at all 6 caller sites; engine-layer (pause-resume) may need separate actor-threading via the runtime composer-stage; (c) **caller-site cluster shape** — single L7-stage6-extension unit if signature-threading is uniform across all 6 callers; split into per-caller units if divergence surfaces (e.g., engine-layer pause-resume vs workflow-layer step boundaries differ in step_id availability) |
| CXA v2.16 §0.4 forward-tracking | 6 PENDING entries transit to 6 LANDED upon runtime plan v2.34 firing-site invocation units landing; CXA narrow-scope revision-pass at v2.16 → v2.17 absorbs the §2.3.2 CP→IS bucket canonical enumeration refresh per v2.9 / v2.15 / v2.16 narrow-scope-CXA-revision precedent |
| H_T-RT-35 transit gate | PARTIAL → RETIRE-READY transit eligible when BOTH U-RT-110 (v2.33) LANDED + runtime plan v2.34 firing-site invocation units LANDED + e2e verification per `[[verification-shape-sharpened-grep-vs-e2e]]` discipline shows production-callsite-fires-composer-fires-ledger-write at the full 6 source-unit surfaces. Retirement-event filing at workspace retirement-event ledger per `[[h-t-cp-19-default-gate-level-spec-extension]]` filing precedent |
| CP plan v2.29 → v2.30 status | **NOT OWED** at this cascade. CP spec v1.26 §16.5 + CP plan v2.29 §1 composer-body authoring PRESERVED VERBATIM at the (F) second half. ZERO cross-axis cascade owed at CP-axis under the corrected architectural framing — the 6 LANDED §16.5 composers are pure functions; orchestration is the runtime axis's job per (S) commitment |

### §0.4 Gap C runtime spec §12.3 prose drift — DEFERRED

Per (C-defer) ratification 2026-05-29: Gap C drift at runtime spec §12.3 (`Callable[[StateLedgerEntry], EntryHash]` vs IS HEAD `Callable[[EntryPayload], Awaitable[WriteResult]]`) NOT patched at v2.33 per FM-2 + plan-revision-cannot-amend-spec discipline. Runtime spec prose alignment for §12.3 callable shape (single-arg async + EntryPayload + WriteResult per IS HEAD contract per CP spec v1.26 §16.5.8 Q4 ratification) + §12.3 17-vs-7 canonical-vs-materialized differential per CP spec v1.25 §16.5.10 NOT-APPLICABLE reclassifications (U-CP-12 declarative-only + U-CP-52 runtime-axis-composed) deferred to next runtime-spec revision pass. Flagged at §3 (a). U-RT-110's signature conformance to IS HEAD is the load-bearing impl-time semantic; the spec prose alignment is a doc-hygiene STRIKE-and-rewrite arc with ZERO production-code impact.

### §0.5 ZERO change at U-RT-104 / U-RT-106 / v2.32-affected units

v2.32's U-RT-104 AC #11 canonical-reading amendment + U-RT-106 NEW AC #4 absorption PRESERVED VERBATIM at v2.33. ZERO interaction between the Phase 2b CLI scaffolding cluster (U-RT-102..U-RT-109) and the new CP→IS wiring unit. The L9-sedecies cluster runs against the YAML/TOML manifest-loader + CLI dispatcher surfaces; U-RT-110 runs against the existing stage-6 CXA_WIRING substrate. DAG-edge-additions at v2.33 §2 are isolated to U-RT-110's incoming edges; ZERO U-RT-102..U-RT-109 edge modification.

---

## §1 NEW unit U-RT-110 — Runtime-side CP→IS state-ledger wiring (6 §16.5 composer bindings)

### §1.1 Site

NEW atomic unit at v2.33. Slots into the runtime plan at the L7-and-later wiring layer (cross-axis-wiring stage 6); structurally peer to U-RT-35 (the LANDED U-CP-34 → U-IS-11 PARTIAL wiring). No new cluster authored — U-RT-110 is a singleton extension of the existing stage-6 CP→IS wiring surface introduced at U-RT-35.

### §1.2 U-RT-110 — Body

**Implements:** CP spec v1.26 §16.5 (full sub-section — §16.5.1 scope; §16.5.2 6-composer surface enumeration; §16.5.3 EntryPayload composition contract per IS HEAD 4-field shape; §16.5.4 idempotency-key formulas with Q-β.i-1(a) outcome-hash suffix; §16.5.5 outcome-bytes recipes consumed by idempotency_key; §16.5.6 U-CP-14 dual-emission discipline; §16.5.7 greenfield composer firing-site discipline; §16.5.8 runtime wiring discipline; §16.5.9 invariants 1-7); runtime spec v1.7 §12.3 CP→IS edges (the 6 of 17 edges materializable at this arc per CP spec v1.25 §16.5.2 + §16.5.10 NOT-APPLICABLE reclassifications); cross-axis composition per CXA v2.16 §0.4 (6 PENDING entries transit to 6 LANDED at v2.33 + paired CP plan v2.30 landing).

**Files:**
- `harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py` (EXTEND — extends the existing `RuntimeCpIsWiring` frozen dataclass with 6 NEW async methods; the existing U-CP-34 `emit_sibling_ledger_entry` synchronous method PRESERVED VERBATIM; preserves `materialize_cp_is_wiring_stage` factory signature unchanged)
- `harness-runtime/tests/test_cp_is_wiring.py` (EXTEND — adds 6 new unit tests + 1 integration test; the existing U-RT-35 test suite PRESERVED VERBATIM; sibling test module home per `harness-runtime/CLAUDE.md` test-locality convention)

**Signatures introduced:**

6 NEW async instance methods on `RuntimeCpIsWiring` (mirrors the per-composer kw-only shape exposed at the CP-axis `harness_cp.*` composer free functions, with workflow context arriving via the runtime method's kw-only parameters):

```python
async def emit_override_state_ledger_entry(
    self,
    *,
    workflow_id: str,
    step_id: str,
    override_id: str,
    policy_id: str,
    post_override_step_config: Mapping[str, Any],
    actor: ActorIdentity,
) -> WriteResult: ...

async def emit_workload_class_selection_state_ledger_entry(
    self,
    *,
    workflow_id: str,
    step_id: str,
    selection_result: WorkloadBindingSelectionResult,
    actor: ActorIdentity,
) -> WriteResult: ...

async def emit_pause_resume_state_ledger_entry(
    self,
    *,
    workflow_id: str,
    step_id: str,
    protocol_event_kind: PauseResumeProtocolEventKind,
    event_sequence_id: int,
    protocol_state_snapshot: Mapping[str, Any],
    actor: ActorIdentity,
) -> WriteResult: ...

async def emit_hitl_tool_call_rewriting_state_ledger_entry(
    self,
    *,
    workflow_id: str,
    step_id: str,
    tool_call_id: str,
    semantic_variant_binding_id: str,
    rewritten_tool_call: RewrittenToolCall,
    actor: ActorIdentity,
) -> WriteResult: ...

async def emit_pause_captured_state_ledger_entry(
    self,
    *,
    workflow_id: str,
    step_id: str,
    pause_event_id: str,
    pause_snapshot: PauseSnapshot,
    actor: ActorIdentity,
) -> WriteResult: ...

async def emit_resume_attempted_state_ledger_entry(
    self,
    *,
    workflow_id: str,
    step_id: str,
    resume_event_id: str,
    resume_attempt_count: int,
    resume_outcome: ResumeOutcome,
    actor: ActorIdentity,
) -> WriteResult: ...
```

Each method's body internally constructs an `async _adapter(payload: EntryPayload) -> WriteResult` closure capturing `(workflow_id, step_id)`, builds `WriteKey(thread_id=Identifier(workflow_id), step_id=Identifier(step_id), idempotency_key=payload.idempotency_key)`, and delegates synchronously to `self.ledger_writer.append(payload, write_key)`. The method then awaits the CP-axis composer with `ledger_writer=_adapter` kw-only-arg + the method's composer-specific args; the composer constructs `EntryPayload`, awaits `_adapter(payload)`, and returns the resulting `WriteResult`. Method returns the composer's return.

`materialize_cp_is_wiring_stage(config, ledger_writer)` signature PRESERVED VERBATIM — the v2.33 extension is additive at the dataclass body; the factory and the bootstrap-stage-6 call site at `stage_6_cxa_wiring.py:65` are UNCHANGED.

**Depends on:**
- `U-RT-12` (`LedgerWriter` substrate at `harness-runtime/src/harness_runtime/lifecycle/state_ledger.py` — LANDED; provides `.append(payload, write_key) -> WriteResult` sync contract)
- `U-RT-35` (existing `RuntimeCpIsWiring` dataclass + `materialize_cp_is_wiring_stage` factory at `cp_is_wiring.py` — LANDED PARTIAL; being extended)
- `U-CP-74` (cross-axis: CP — `emit_override_state_ledger_entry` at `per_step_override_evaluator.py:282`; LANDED at PR #39 merge `e63a600`)
- `U-CP-75` (cross-axis: CP — `emit_workload_class_selection_state_ledger_entry` at `workload_binding_engine_class_selection.py:302`; LANDED at PR #40 merge `332edac`)
- `U-CP-76` (cross-axis: CP — `emit_pause_resume_state_ledger_entry` at `pause_resume_protocol.py:637`; LANDED at PR #41 merge `d745450`)
- `U-CP-77` (cross-axis: CP — `emit_hitl_tool_call_rewriting_state_ledger_entry` at `hitl_as_tool_call_rewriting.py:249`; LANDED at PR #42 merge `4765aaf`)
- `U-CP-78` (cross-axis: CP — `emit_pause_captured_state_ledger_entry` at `pause_resume_protocol.py:750`; LANDED at PR #43 merge `a815ac9`)
- `U-CP-79` (cross-axis: CP — `emit_resume_attempted_state_ledger_entry` at `pause_resume_protocol.py:868`; LANDED at PR #44 merge `35744ab`)

All 6 cross-axis CP dependencies are LANDED on main as of `35744ab` 2026-05-29 per fork doc §"Cluster A library-side COMPLETE" PR ledger; U-RT-110 unblocks at runtime plan v2.33 publication.

**Acceptance criteria:**

1. `RuntimeCpIsWiring` extended at `cp_is_wiring.py` with the 6 async methods declared at §1.2 Signatures; existing `emit_sibling_ledger_entry` synchronous method PRESERVED VERBATIM at the dataclass body; dataclass remains `frozen=True, slots=True` per established pattern.

2. Each method constructs the per-call adapter as an `async def _adapter(payload: EntryPayload) -> WriteResult` closure (NOT a sync function returning `WriteResult` — the composer types `ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]`; a sync function does not satisfy `Awaitable[...]` at the type-checker per pyright strict). The adapter closes over the method's `workflow_id` + `step_id` parameters and constructs `WriteKey(thread_id=Identifier(workflow_id), step_id=Identifier(step_id), idempotency_key=payload.idempotency_key)` then returns `self.ledger_writer.append(payload, write_key)` synchronously (the inner `LedgerWriter.append` is sync per `state_ledger.py:83`).

3. Each method awaits the corresponding `harness_cp.*` composer with `ledger_writer=_adapter` + the method's composer-specific kw-only arguments passed through; method returns the composer's return value (`WriteResult`). Method body is 3 lines (adapter def + composer await + return) per per-method symmetric shape.

4. Cross-method invariants: ZERO mutation of `RuntimeCpIsWiring` state (instance is `frozen=True`); ZERO global state mutation; ZERO catch-and-swallow of composer-raised typed errors (raised typed errors propagate to caller per implementation-planner anti-pattern §10 "no spec extension").

5. Imports added at `cp_is_wiring.py`: `from harness_cp.per_step_override_evaluator import emit_override_state_ledger_entry`; `from harness_cp.workload_binding_engine_class_selection import emit_workload_class_selection_state_ledger_entry, WorkloadBindingSelectionResult`; `from harness_cp.pause_resume_protocol import emit_pause_resume_state_ledger_entry, emit_pause_captured_state_ledger_entry, emit_resume_attempted_state_ledger_entry, PauseResumeProtocolEventKind, PauseSnapshot, ResumeOutcome`; `from harness_cp.hitl_as_tool_call_rewriting import emit_hitl_tool_call_rewriting_state_ledger_entry, RewrittenToolCall`; `from harness_is.state_ledger_write import EntryPayload`. No new external library dependencies introduced.

6. 6 NEW per-method unit tests at `test_cp_is_wiring.py` (one per emit-method): each test constructs an in-process `LedgerWriter` against a temp JSONL handle, materializes `RuntimeCpIsWiring`, awaits the corresponding `emit_*_state_ledger_entry` method with deterministic test fixture inputs, asserts return is `WriteResult.APPENDED`, reads the ledger, asserts exactly 1 entry exists, asserts the entry's `action_id` equals the per-composer canonical kebab-case identifier per CP spec v1.26 §16.5.3 table (`cp.per-step-override-application` / `cp.workload-binding-class-selection` / `cp.pause-resume-protocol` / `cp.hitl-tool-call-rewriting` / `cp.pause-captured` / `cp.resume-attempted`).

7. 1 NEW integration test: invokes all 6 methods in sequence against a single in-process ledger with distinct deterministic fixture inputs (distinct `workflow_id` per invocation to vary thread_id); asserts post-emission `chain_verification` per C-IS-06 §6 passes for the full 6-entry chain; asserts each per-method idempotency-key formula per CP spec v1.26 §16.5.4 is deterministic-on-replay (re-invoke each method with identical fixture inputs; assert second invocation returns `WriteResult.IDEMPOTENT_NOOP`).

8. ZERO modification to `materialize_cp_is_wiring_stage` factory signature; ZERO modification to `stage_6_cxa_wiring.py:65` call site; the factory's existing return shape `CpIsWiringStage(wiring=RuntimeCpIsWiring(ledger_writer=ledger_writer))` carries the v2.33 extension transparently because `RuntimeCpIsWiring`'s 6 NEW methods read only `self.ledger_writer` (already-bound at construction).

9. `chain_verification` (C-IS-06 §6) MUST pass over the full sequence of state-ledger entries written by U-RT-110 methods at any test invocation; failure surfaces as a test failure with the C-IS-06 §6.4 failure-position / failure-type annotation per `TamperedChainError`.

10. Per (F) FULL-WIRE-paired ratification 2026-05-29: U-RT-110 LANDED at v2.33 publication is the runtime-side half; H_T-RT-35 PARTIAL → RETIRE-READY transit requires the paired CP plan v2.29 → v2.30 6 firing-site invocation units LANDED + e2e verification per `[[verification-shape-sharpened-grep-vs-e2e]]` discipline. Filing the retirement-event-tier transit at U-RT-110 landing alone WITHOUT the paired CP-axis landings is structurally an X-AL-2 second-conjunct violation (substituted H_E surface still invoked at substitution site — the CP-axis production functions do NOT invoke the runtime wiring methods until CP plan v2.30 lands).

**Tests:** `test_emit_override_state_ledger_entry_writes_canonical_entry`; `test_emit_workload_class_selection_state_ledger_entry_writes_canonical_entry`; `test_emit_pause_resume_state_ledger_entry_writes_canonical_entry`; `test_emit_hitl_tool_call_rewriting_state_ledger_entry_writes_canonical_entry`; `test_emit_pause_captured_state_ledger_entry_writes_canonical_entry`; `test_emit_resume_attempted_state_ledger_entry_writes_canonical_entry`; `test_six_emit_methods_full_chain_verification_passes`; `test_six_emit_methods_idempotent_on_replay`.

---

## §2 DAG delta

### §2.1 NEW node + edges at v2.33

| Element | Detail |
|---|---|
| NEW node | U-RT-110 |
| NEW within-axis edges (LANDED dependencies) | U-RT-110 → U-RT-12; U-RT-110 → U-RT-35 (2 edges) |
| NEW cross-axis edges (LANDED dependencies) | U-RT-110 → U-CP-74; U-RT-110 → U-CP-75; U-RT-110 → U-CP-76; U-RT-110 → U-CP-77; U-RT-110 → U-CP-78; U-RT-110 → U-CP-79 (6 edges per implementation-planner §7 cross-axis-callout discipline; all 6 LANDED on main as of `35744ab` 2026-05-29 — dependencies satisfied at v2.33 publication) |
| Cross-axis cascade declarations (NOT-yet-LANDED firing-site units owed at paired CP plan v2.30) | U-RT-110 is consumed at CP-axis-production-firing-sites at the 6 production functions named at §0.3; the 6 CP-axis firing-site units are CP plan v2.30 NEW units (IDs assigned at CP plan v2.30 authoring per CP-axis numbering authority — runtime plan does NOT pre-commit CP-axis unit IDs). H_T-RT-35 transit gate per §0.3 |

### §2.2 Acyclic invariant

DAG verified acyclic at v2.33 publication: U-RT-110 is a leaf at the runtime-axis DAG (depends on 2 LANDED runtime-axis predecessors + 6 LANDED cross-axis predecessors; ZERO incoming dependencies from any not-yet-LANDED runtime-axis unit; ZERO outgoing dependencies introduced at v2.33 within the runtime-axis DAG). Topological sort exists; U-RT-110 ships at any topological-sort position after U-RT-12 + U-RT-35 + U-CP-74..U-CP-79 satisfied. v2.32 DAG PRESERVED VERBATIM (no edge modifications at any v2.32-known node).

### §2.3 Unit count

v2.32 unit count 107 → v2.33 unit count 108 (+1 — U-RT-110). NO unit removal; NO unit re-identification; v2.32 lineage U-RT-00 through U-RT-109 PRESERVED VERBATIM at v2.33 by reference.

---

## §3 Adjacent observations + carry-forward

(a) **Gap C runtime spec §12.3 prose drift carried per (C-defer) ratification 2026-05-29.** The runtime spec v1.7 §12.3 declared callable shape `Callable[[StateLedgerEntry], EntryHash]` remains stale against the IS HEAD `Callable[[EntryPayload], Awaitable[WriteResult]]` shape that U-RT-110 implements per CP spec v1.26 §16.5.8 Q4 ratification. The 17-vs-7 §12.3 canonical-vs-materialized differential per CP spec v1.25 §16.5.10 NOT-APPLICABLE reclassifications (U-CP-12 declarative-only + U-CP-52 runtime-axis-composed) likewise remains stale at runtime spec. Both deferred to next runtime-spec revision pass per FM-2 + plan-revision-cannot-amend-spec discipline. Owed at separate spec-revision arc; NOT blocking U-RT-110 impl (the impl conforms to IS HEAD shape directly per Q4 ratification anchor at CP spec v1.26 §16.5.8 — the runtime spec prose alignment is doc-hygiene with ZERO production-code impact).

(b) **Runtime plan v2.33 → v2.34 paired revision-pass arc owed per (F) ratification 2026-05-29 (corrected per §0.3 authoring correction).** Per §0.3 cross-axis cascade (corrected): 1-3 NEW runtime plan v2.34 firing-site invocation units thread U-RT-110's 6 async methods into the production caller paths (workflow_driver post-resolve hook + workload-binding-time site + HITL composer + pause-resume composer + engine-layer free-function callers). CP-axis production function signatures + input types PRESERVED VERBATIM at v2.34. Authoring is `implementation-planner` skill scope at the runtime-axis stream (sa-rt sub-agent at Phase 7 7b cluster open). The paired revision is the LOAD-BEARING half for H_T-RT-35 transit; U-RT-110 LANDED at v2.33 + runtime v2.34 caller-site units LANDED + e2e verification COMPLETE = H_T-RT-35 PARTIAL → RETIRE-READY transit-eligible per `[[verification-shape-sharpened-grep-vs-e2e]]` discipline.

(c) **CXA v2.16 §0.4 forward-tracking 6 PENDING → 6 LANDED at paired-cascade-completion.** Per §0.3 cross-axis cascade row: CXA narrow-scope revision-pass at v2.16 → v2.17 absorbs the §2.3.2 CP→IS bucket canonical enumeration refresh at the same arc that retires H_T-RT-35. NOT owed at v2.33 publication (U-RT-110 is the runtime-side binding half only). Owed at runtime plan v2.34 caller-site landings + retirement-batch filing arc.

(d) **H_T-RT-35 batch-filing precedent.** Per `[[h-t-cp-19-default-gate-level-spec-extension]]` filing precedent: when both halves of a paired-cascade transit-arc land, the retirement-event filing collapses the dual-arc into a single retirement-batch entry (e.g., "batch-46: H_T-RT-35 PARTIAL → RETIRE-READY via U-RT-110 binding + runtime v2.34 caller-site units + CXA v2.17 §2.3.2 enumeration refresh"). v2.33 publication is the FIRST half (binding surface); batch filing awaits the SECOND half (runtime plan v2.34 caller-site units + impl arc closures).

(e) **`materialize_cp_is_wiring_stage` factory signature ZERO change.** v2.33 extends `RuntimeCpIsWiring` at the body (6 new methods) without modifying the factory's signature or the bootstrap-stage-6 call site. This is by design: the existing `ledger_writer: LedgerWriter` field carries all binding state needed by the 6 new methods. ZERO modification to `harness-runtime/src/harness_runtime/bootstrap/stage_6_cxa_wiring.py:65` at v2.33 impl arc. Test fixtures that construct `RuntimeCpIsWiring(ledger_writer=...)` directly continue to work; backward-compat at the construction boundary.

(f) **Workspace `CLAUDE.md` §2.4 runtime plan row bump owed.** Runtime plan row v2.32 → v2.33 at workspace root `CLAUDE.md` §2.4. Co-publication this arc. Unit count: 107 → 108 at the row metadata.

(g) **`harness-runtime/CLAUDE.md` row + plan-unit-anchor refresh owed.** Per-axis `harness-runtime/CLAUDE.md` plan-unit anchors may carry "U-RT-110 NEW (v2.33)" entry per the established per-axis-CLAUDE.md plan-anchor discipline; specific row shape per `harness-runtime/CLAUDE.md` §4.1 conventions at the impl arc.

(h) **U-CP-34 LANDED-but-never-fired precedent.** The existing U-RT-35 PARTIAL-LAND at `cp_is_wiring.py:92` (the `emit_sibling_ledger_entry` synchronous method) is exposed at `ctx.cxa_stages["cp_is_wiring"].emit_sibling_ledger_entry` but is NOT invoked at any production callsite at HEAD (empirical grep at `35744ab` 2026-05-29). v2.33 + paired CP plan v2.30 firing-site units close the U-CP-34 LANDED-but-never-fired residual at the same arc — the CP plan v2.30 sub_agent_dispatch firing-site unit author the `emit_sibling_ledger_entry` invocation at the canonical `sub_agent_dispatch.py` callsite (separate from the 6 §16.5 firing-site units but coupling at the same arc-shape).

(i) **NO retirement event filing at v2.33 publication.** v2.33 is the binding-surface authoring half of the paired (F) arc; retirement-tier transit at H_T-RT-35 awaits BOTH halves LANDED (U-RT-110 binding + runtime v2.34 caller-site units) + e2e verification COMPLETE per `[[verification-shape-sharpened-grep-vs-e2e]]` discipline. Filing transit at v2.33 alone would be X-AL-2 second-conjunct violation (substituted H_E surface still invoked: the 6 production callers still bypass U-RT-110's wiring methods until runtime v2.34 lands).

(j) **PR-shape recommendation.** U-RT-110 impl arc lands at a single PR per implementation-planner §10 PR-per-cluster-recommendation precedent (mirrors the L9-decies through L9-quindecies cluster-shaped PRs). NEW tests (6 unit + 1 integration + 1 idempotent-on-replay) land in the same PR. PR title shape: `feat(runtime): U-RT-110 wire 6 §16.5 composers to ledger_writer.append`. Branching: off main (post-merge of any in-flight v2.33 publication PR).

(k) **36th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`.** Pre-substantive advisor consultation at v2.33 authoring caught the (P) vs (F) scope ambiguity at fork doc §"Estimated in-CLI work post-design" vs §"Pending post-Phase-6-design-arc closure" lines pre-AskUserQuestion. Memory posture continues to validate operationally; advisor's discriminator-naming at the pre-authoring orientation pass is the workspace-canonical discipline for Phase 6 plan-revision arcs surfacing cross-axis cascade.

(l) **Plan-revision discipline preserved.** U-RT-110 cites CP spec v1.26 §16.5 + runtime spec v1.7 §12.3 + CXA v2.16 §0.4 at the spec-traceability surface; does NOT invent any commitment absent from the cited specs; does NOT amend any cited spec; declares dependencies explicitly (8 edges per §2.1; 2 within-axis + 6 cross-axis); coverage matrix at runtime-axis aggregate gains 1 row (CP spec v1.26 §16.5 — newly covered surface at v2.33). Per implementation-planner §4 four-sub-discipline checklist: atomicity ✓ (single coherent change — extend one class with 6 symmetric methods); spec-traceability ✓ (cites CP spec v1.26 §16.5 by ID + section + per-sub-section breakdown); dependency-awareness ✓ (8 edges declared; cross-axis flagged); implementation-grade-detail ✓ (files, signatures, ACs, tests named at logical level per §10 anti-pattern guidance).

---

## §4 Filing footer

| State | Value |
|---|---|
| Document | `Implementation_Plan_Harness_Runtime_v2_33.md` (this file) |
| Authored | 2026-05-29, Phase 6 back-flow apply pass per Path α authorization |
| Authority | Operator Path α AUTHORIZED 2026-05-29 at `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` §"Path α AUTHORIZED" + AskUserQuestion 2026-05-29 ratifications Q1=(F) FULL-WIRE-paired + Q2=(C-defer) Gap C deferred |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_32.md` (v2.32 — Class 1 fork U-RT-104 Reading β apply pass) |
| Successor consumption | U-RT-110 implementation arc against runtime plan v2.33; paired runtime plan v2.33 → v2.34 caller-site authoring arc (`implementation-planner` skill at runtime-axis; sa-rt sub-agent at Phase 7 7b cluster open) per §0.3 authoring correction; CXA v2.16 → v2.17 narrow-scope revision at paired-cascade-completion |
| Cross-axis cascade | INTRA-RUNTIME-AXIS at the (F) second half per §0.3 authoring correction. 6 cross-axis dependency edges declared at §2.1 (U-RT-110 → U-CP-74..U-CP-79 — all LANDED); 1-3 runtime plan v2.34 caller-site units owed per §0.3 (cascade-OWED, not cascade-LANDED); CXA v2.17 §2.3.2 enumeration refresh owed at retirement-batch filing arc. CP plan v2.30 NOT OWED (corrected from initial draft) |
| Unit count | 107 → 108 (+1 — U-RT-110) |
| DAG | EXTENDED at §2.1 (+1 node, +2 within-axis edges, +6 cross-axis edges); acyclic invariant verified |
| Test cardinality | NET +8 at U-RT-110 (6 per-method unit + 1 integration + 1 idempotent-on-replay) |
| Status posture | `Status: Proposed` per implementation-planner §8 revision-pass mode discipline; clears at P6-CK adversarial review per workspace `harness-adversarial-reviewer` skill if invoked; absent P6-CK clearance, status carries until operator ratification at impl-arc PR merge per workspace `[[fork-h-t-cp-19-default-gate-level-spec-extension]]` apply-pass precedent |
| Sibling co-publication this arc | NONE at design-substrate scope (CP spec v1.26 + runtime spec v1.7 + CXA v2.16 PRESERVED VERBATIM at v2.33 publication; v2.33 is plan-revision-pass scope only); workspace `CLAUDE.md` §2.4 row bump + `harness-runtime/CLAUDE.md` plan-unit anchor refresh owed at follow-on docs commit |
