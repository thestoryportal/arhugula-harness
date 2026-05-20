# C-CP-25 — `WorkflowDriver` contract recommendation

**Mode:** `systems-architect` Phase-7 architectural-tension resolution (§4A)
**Source tension:** `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` (status OPEN-RESOLVING)
**Fork class:** Class 1 (halt-execution; design-substrate revision required before Phase 7 execution can proceed against the runtime ACs)
**Recommendation status:** DRAFT — awaiting operator ratification
**Author:** systems-architect (this session)
**Date:** 2026-05-20

---

## §1. Tension statement (precise)

CP spec v1.3 + CP plan v2.10 specify, between them, every component a workflow execution driver would touch — but no contract specifies the driver itself. Specifically:

- **`Spec_Control_Plane_v1_3.md`** declares the `WorkflowManifestEntry` shape (via `Spec_Control_Plane_v1_2.md` §6.1, preserved at v1.3), the 8 lifecycle event classes (§5.1, preserved at v1.3), the manifest's `engine_class` binding (§6.1 / §7), the per-step override syntax (§6.2), the resumption-kind enum and `idempotency_key` join discipline (§8.1 / §8.2), and the 6-pattern topology taxonomy (§10.1, preserved at v1.3) — but contains no contract specifying *the iterator that calls these per step in order while emitting the lifecycle events at their declared boundaries*.

- **`Implementation_Plan_Control_Plane_v2_10.md`** (inheriting unit bodies from v2 / v2.1) materializes the manifest schema (U-CP-13), the per-step override resolver (U-CP-14: `resolve_step_binding(manifest_entry, step_id) → StepEffectiveBinding`, AC #1 single-step semantics), the lifecycle event taxonomy declaration (U-CP-10), and the engine-class enum (U-CP-15) — but materializes no iterator. U-CP-14's signature is callee-only; no caller exists in any unit.

- **`Spec_Harness_Runtime_v1.md`** §11 C-RT-11 acknowledges this gap explicitly in its risk surface: "If CP later surfaces a native drain primitive (e.g., a CP-level `WorkflowDrainController` type), refactor `harness-runtime/` to delegate drain to CP. This contract becomes a thin adapter. Until then, drain ownership is runtime-axis-local." The runtime spec presumes a CP-side driver that polls `ctx.drained_flag` at lifecycle boundaries; no such driver is specified.

Result: U-RT-44 AC #2 (in-flight step bounded-wait) and U-RT-49 workflow-execution ACs (state-ledger workflow entries, collector spans per workflow step, cost-attribution chain) were STRUCK at Phase 2 close — no observable surface exists because no driver exists.

## §2. Authority-chain placement

Per `CLAUDE.md` §1.3 authority chain: ADR → ADD → PRD → per-axis spec → per-axis plan + CXA. Earlier is canonical.

| Artifact | Position | Statement on the workflow-execution driver |
|---|---|---|
| **ADR-F3 v1.1** | F-tier (foundational) | §Decision (iv): "F3 capability-floor (iv): workflow lifecycle event surface visible at run-event surface as distinct event classes" — this is the foundational commitment that the workflow lifecycle is observable. ADR-F3 owns the *what is observable* commitment, not the *what does the observing*. |
| **ADD v1.3 §3.1.1** | Consolidation tier | Absorbs ADR-D1 v1.2 (engine-class taxonomy + per-deployment-surface candidate mapping). Names the 5-element engine-class taxonomy as a parametric commitment per deployment surface. Does not specify a driver. |
| **PRD v1.1 R-CP-04** | Requirements tier | "Workflow lifecycle event surface visible at run-event surface as distinct event classes." Observable behavior is requirement-anchored at PRD. The *emitter of those events* is implicit, not requirement-named. |
| **CP spec v1.3** | Per-axis spec | Specifies the 8-class lifecycle event taxonomy (§5.1) including `workflow.start`, `step.boundary`, `workflow.resumption` + minimum attributes (§5.2) + sampling discipline (§5.4) + manifest schema (§6.1) + per-step override (§6.2) + audit composition (§6.4) + engine class (§7) + replay-resumption + idempotency-key join (§8.1 / §8.2) + engine.* namespace (§9) + 6-pattern topology (§10.1). **Specifies every emission boundary; specifies no emitter.** |
| **CP plan v2.10** | Per-axis plan | Materializes the manifest schema, the per-step resolver, the lifecycle taxonomy enum, and the engine class enum as separate units. **Materializes no iterator unit.** |

**Reading.** The authority chain is *silent* on the workflow-execution driver. ADR-F3 commits to a workflow lifecycle being observable; the spec commits to *what* is observable; nothing in the chain commits to *what does the observing*. This is **a design gap, not a contract drift** — per §4A.4: "if the tension cannot be resolved by reading the authority chain — because the chain is genuinely silent — that is a design gap, not a tension; surface it as such (a Class 1 fork) rather than inventing the missing commitment." Hence Class 1.

## §3. §2 discipline applied

### §3.1 Five-axis decomposition

| Axis | Implication for the driver |
|---|---|
| **Control plane** | Primary axis. The driver is the per-workflow iteration topology. At `SINGLE_THREADED_LINEAR`, the topology is one logical agent advancing through declared steps. The driver IS the control-flow at this pattern. |
| **Information substrate** | Secondary. Driver consumes `WorkflowManifestEntry` (U-CP-13 / C-IS-03 manifest-as-state), produces state-ledger entries per step (composes with C-IS-05 entry shape + C-IS-10 §10.1 export + C-IS-11 append discipline), produces a terminal `RunResult` (new type — declared in this contract). |
| **Action surface** | Tertiary. Driver dispatches step invocation through the cap-aware router (C-CP-01 / U-CP-01); does not itself bind to a tool surface. Tool calls happen *inside* a step, not at the driver layer. |
| **Operational discipline** | Cross-cutting. Driver is the emission site for `workflow.start` + per-step `step.boundary` + (on replay entry) `workflow.resumption` (§5.1) + the terminal exit. Sampling discipline per §5.4 applies. Cost-attribution-per-span (per OD plan) composes downstream. |
| **Deployment surface** | Engine-class binding (`event-sourced-replay / save-point-checkpoint / pure-pattern-no-engine / reconciler-loop / WAL-segment` per §7.1) selects the driver's resumption semantics. At v1.4 scope `SINGLE_THREADED_LINEAR` × `pure-pattern-no-engine` (or `save-point-checkpoint`) is the materialized cell; other engine cells emit the same events with different resumption shape per §8.1 / §8.2. |

### §3.2 Probabilistic-deterministic boundary

The driver lives entirely on the **deterministic** side. Step iteration order is declarative (from the manifest); step-effective-binding is deterministic (U-CP-14 AC #4: "Override evaluator is deterministic given inputs"); drain-flag check is deterministic; lifecycle event emission is deterministic. The probabilistic surface is *inside the step* (the LLM call, the tool selection if any), bracketed by the driver's deterministic event emission. This is the architecturally correct placement per `CLAUDE.md` framing: production reliability lives in the deterministic layer.

### §3.3 Decision ordering

| Class | Verdict |
|---|---|
| **F (foundational)** | NO. The driver does not commit a new foundational invariant. It materializes the F3 commitment ("workflow lifecycle is observable") that already exists. |
| **D (derivative)** | YES — this is the recommendation. The driver is the derivative materialization site for ADR-F3 §Decision (iv) + ADR-D1 v1.2 engine-class taxonomy + ADR-D5 v1.3 topology pattern enum. C-CP-25 sits alongside C-CP-08 (replay-resumption — which composes with the driver at re-entry) and C-CP-10 (6-pattern topology — which the driver dispatches under). |
| **I (independent)** | NO. The driver cannot be deferred. It is the precondition for *any* workflow being runnable, and currently blocks U-RT-44 AC #2 + U-RT-49 workflow-execution ACs. |

### §3.4 Cross-axis verification

- **CP ↔ IS:** driver emits per-step entries via C-IS-05 + C-IS-10 §10.1 export consumer. Per `[[fork-cp-is-wiring-gaps]]` (DEFERRED), 7 CP modules lack ledger composers. The driver is the seventh — once it lands, the missing-composer count drops to 6 (or the driver's composer absorbs several of them). No new IS-side gap.
- **CP ↔ AS:** driver dispatches through the cap-aware router (C-CP-01); no new AS-side gap.
- **CP ↔ OD:** driver emits to OTel per §5.1 + §5.4 sampling. Cost-attribution chain (5-step per OD axis) is a downstream concern; the driver's emission site is the start of that chain.
- **CP ↔ Runtime:** driver consumes `HarnessContext` per U-RT-44 (drained_flag). This is the seam this fork resolves.

No new cross-axis tension introduced.

## §4. Recommended contract — C-CP-25 `WorkflowDriver`

### §4.1 Contract surface (one-sentence)

A deterministic step iteration driver that consumes a `WorkflowManifestEntry` + `HarnessContext`, dispatches each step through the cap-aware router under the manifest's effective bindings, emits the 8-class lifecycle event surface at its declared boundaries (§5.1) including the `workflow.start` / per-step `step.boundary` / terminal exit, polls `ctx.drained_flag` at per-step boundaries, and returns a typed `RunResult` whose `status` enum admits `drained` (per `Spec_Harness_Runtime_v1.md` §11 C-RT-11 settlement).

### §4.2 Scope

**In scope at v1.4:** Topology pattern `SINGLE_THREADED_LINEAR` only (per `Spec_Control_Plane_v1_2.md` §10.1 6-pattern enum row 1).

**Explicitly deferred at v1.4** (per X-AL-3 — no silent design extension):

| Topology pattern | Deferral notation |
|---|---|
| `orchestrator-workers` | C-CP-25 §[deferred]: extension contract C-CP-25.b or C-CP-26 when the first multi-worker workflow unit demands it. |
| `decentralized-handoff` | Same. |
| `hierarchical-delegation` | Same. |
| `evaluator-optimizer` | Same. |
| `parallelization` | Same. |

Any attempt to drive a non-`SINGLE_THREADED_LINEAR` workflow under C-CP-25 v1.4 raises a typed `TopologyPatternNotYetMaterializedError`. Manifest validation at workflow-binding time (U-CP-13 / §6.4 composition) rejects manifests whose `topology` field is non-`SINGLE_THREADED_LINEAR` with this error.

### §4.3 Signatures

```text
record RunResult {
  workflow_id        : string
  run_id             : string
  status             : RunStatus
  terminal_step_index: Optional<int>            // present on drained/failed
  partial_state      : Optional<TerminalState>  // present on drained/failed
  final_state        : Optional<TerminalState>  // present on success
  fail_class         : Optional<FailClass>      // present on failed
}

enum RunStatus {
  SUCCESS,
  DRAINED,                                       // per Spec_Harness_Runtime_v1 §11 C-RT-11
  FAILED,
  PARTIAL                                        // reserved for future multi-step error modes
}

function execute_workflow(
    manifest_entry : WorkflowManifestEntry,     // U-CP-13 / §6.1
    run_id         : string,                     // harness-unique; root idempotency_key derives from this
    ctx            : HarnessContext              // U-RT-44 — carries drained_flag, ledger handle, OTel tracer
) -> RunResult
    // SINGLE_THREADED_LINEAR only at v1.4; rejects other topology patterns at entry.
```

### §4.4 Iteration discipline

The driver implements the following deterministic sequence:

1. **Validate.** Reject if `manifest_entry.topology` ≠ `SINGLE_THREADED_LINEAR` (raise `TopologyPatternNotYetMaterializedError`). Reject if `manifest_entry.engine_class` ∉ {`pure-pattern-no-engine`, `save-point-checkpoint`} at v1.4 (other engine classes deferred to engine-class-extension contracts; cited at §[deferred]).
2. **Emit `workflow.start`** per §5.1 with minimum attributes per §5.2 (`workflow.id`, `workflow.class`, `engine.class`, `manifest.entry_id`, `idempotency_key` root). Always-sampled per §5.4.
3. **Iterate steps in declaration order.** For each step `s` in `manifest_entry.steps` (declaration-order; SINGLE_THREADED_LINEAR has no parallel / fan-out branching):
   1. **Drain check (pre-step).** If `ctx.drained_flag.is_set()`: emit final `step.boundary` with `step.kind = 'drain-aborted-pre-entry'`, do NOT enter step, return `RunResult(status=DRAINED, terminal_step_index=s.index-1, partial_state=<accumulated>)`.
   2. **Resolve binding.** `binding = resolve_step_binding(manifest_entry, s.id)` per U-CP-14.
   3. **Acquire lease (if engine-class requires).** Per §5.1 / §5.3: if `binding.engine_class` requires a lease (per C-CP-09 §9.1 engine-class lookup), acquire and emit `lease.acquired`.
   4. **Dispatch.** Invoke the step body through the cap-aware router (`route_invocation(binding, s.payload, ctx)` per U-CP-01 / C-CP-01 §1.3). Step body is opaque to the driver; the router owns provider / model / engine dispatch.
   5. **Emit `step.boundary`.** Per §5.1 + §5.2 attribute set (`workflow.id`, `step.index`, `step.kind`, `idempotency_key` per C-IS-05). Sampling per §5.4 (head-base / tail-prod).
   6. **Release lease (if held).** Emit `lease.released` per §5.1.
   7. **State-ledger append.** Compose per C-IS-05 entry shape via C-IS-10 §10.1 export → C-IS-11 append. `idempotency_key` derives from `(run_id, step.index)` per §8.2 join discipline. (This is the missing CP-side composer flagged at `[[fork-cp-is-wiring-gaps]]` for the workflow-step site.)
   8. **Drain check (post-step).** If `ctx.drained_flag.is_set()`: return `RunResult(status=DRAINED, terminal_step_index=s.index, partial_state=<accumulated including this step>)`.
4. **Emit terminal.** No new event class — the absence of a further `step.boundary` plus the `RunResult.status` return is the terminal observable. (Per `Spec_Harness_Runtime_v1.md` §11 settlement — no `DRAINED` event class; terminal status is observable via return value, not via lifecycle event.)
5. **Return** `RunResult(status=SUCCESS, final_state=<accumulated>)`.

### §4.5 Drain protocol — composition with U-RT-44

| Site | Behavior |
|---|---|
| Driver entry | If `ctx.drained_flag.is_set()` at entry, return `RunResult(status=DRAINED, terminal_step_index=null, partial_state=null)` *before* emitting `workflow.start`. (Drain detected before any state mutation.) |
| Per-step pre-entry (§4.4.3.1) | Drain check before entering next step. On flag-set: emit `step.boundary` with `step.kind='drain-aborted-pre-entry'`, do NOT dispatch; return DRAINED. |
| Per-step post-exit (§4.4.3.8) | Drain check after step body completes. On flag-set: state-ledger append for the just-completed step *has* persisted; return DRAINED with that step counted. |
| Mid-step | NO drain check. Step bodies run to completion (or to their own internal failure). This matches `Spec_Harness_Runtime_v1.md` §11: "Completes the current in-flight step (no mid-step interruption)." |
| Bounded wait | The driver does not own the bounded-wait timeout itself; per C-RT-11 the timeout lives in `shutdown(ctx, timeout=...)` at C-RT-10. If the step body exceeds the wait, runtime force-shutdown proceeds; driver may not complete its post-step accounting. C-RT-14 `RT-FAIL-DRAIN-TIMEOUT` covers this. |

### §4.6 Lifecycle event emission boundaries (single-threaded-linear filter over §5.1)

| §5.1 event class | Emitted at SINGLE_THREADED_LINEAR? | Site |
|---|---|---|
| `workflow.start` | YES | §4.4.2 driver entry post-validation |
| `step.boundary` | YES | §4.4.3.5 every step exit (including drain-aborted-pre-entry per §4.4.3.1) |
| `fallback.triggered` | CONDITIONAL | Only if step body triggers fallback (per C-CP-03 §3.5). Driver does not synthesize; it propagates step body's emission. |
| `retry.attempt` | CONDITIONAL | Same — step body owns; driver propagates. |
| `breaker.tripped` | CONDITIONAL | Same. |
| `lease.acquired` / `lease.released` | CONDITIONAL | Per binding's engine class via C-CP-09 §9.1 `lease.mechanism` lookup row (per-engine-class mechanism enum). Specific per-engine-class lease requirement to be verified at `spec-writer` time against C-CP-09 §9.1 row contents; the driver contract states "emit per engine-class lookup," not a fixed assertion per engine. |
| `workflow.resumption` | CONDITIONAL | Only if driver entry is a re-entry per C-CP-08 §8 replay-resumption. v1.4 scope: emit on re-entry if `manifest_entry.engine_class == 'save-point-checkpoint'` AND `run_id` matches a prior F2 ledger entry. Always-sampled per §5.4. Composition with §8.2 idempotency-key join. |

No new event classes introduced — C-CP-25 strictly composes against the §5.1 closed-at-8 taxonomy. (This corrects an anti-finding surfaced during this session — see §6.)

### §4.7 Composition with C-CP-08 §8.2 idempotency-key join

Per §8.2 join discipline (`pure-pattern-no-engine` row): "F2 state-ledger native — `idempotency_key` is the primary dedup substrate; replay reads F2 entries chronologically per C-IS-07 read contract." At driver re-entry under `save-point-checkpoint`:

1. Driver computes `run_idempotency_key = sha256(run_id, manifest_entry.workflow_id, manifest_entry.entry_version)`.
2. Reads F2 state-ledger via C-IS-07 for entries matching `run_idempotency_key` prefix.
3. If matches exist, emits `workflow.resumption` per §5.1 + §5.2 (with `resumption.kind` per §8.1).
4. Skips already-replayed steps; resumes at first unmaterialized step.
5. Per-step `idempotency_key = sha256(run_idempotency_key, step.index)` per §8.2 dedup semantics.

`pure-pattern-no-engine` is the simpler case (no engine-internal replay state); `save-point-checkpoint` requires the resumption read above. Other engine classes deferred at v1.4 per §4.2 scope.

### §4.8 Failure-mode taxonomy

| Fail class | Trigger | Behavior |
|---|---|---|
| `CP-FAIL-DRIVER-TOPOLOGY-UNSUPPORTED` | Manifest declares non-`SINGLE_THREADED_LINEAR` topology at v1.4 | `TopologyPatternNotYetMaterializedError`; no events emitted; no ledger entries. |
| `CP-FAIL-DRIVER-ENGINE-CLASS-UNSUPPORTED` | Manifest declares engine class outside v1.4 scope | Typed error; no events emitted. |
| `CP-FAIL-DRIVER-STEP-FAILURE` | Step body raises uncaught exception | Emit `step.boundary` with failure attrs; return `RunResult(status=FAILED, fail_class=<step-specific>)`; drain-flag NOT auto-set (failure ≠ drain). |
| `CP-FAIL-DRIVER-LEDGER-APPEND-FAILURE` | C-IS-11 append fails | Fail-loud; return FAILED with `fail_class='ledger-append-failed'`. State-ledger fidelity is non-negotiable per ADR-F2 v1.2. |
| `RT-FAIL-DRAIN-TIMEOUT` | (Owned by runtime C-RT-14) | Driver may not complete post-step accounting; runtime force-shutdown. |

### §4.9 Deferred to implementation discretion

- Specific `TerminalState` record shape (workflow-class-dependent; downstream cell decision).
- Specific runtime structure of step iteration (async generator? coroutine? state machine?) — deferred to implementation; contract is on observable behavior, not implementation shape.
- Specific dispatch ordering for step body invocation when the step body is itself an LLM call vs. a tool call vs. a sub-routine — covered by U-CP-01 cap-aware router contract.
- Concurrency of `lease.acquired` / `step.boundary` emission — driver may emit them as separate spans or as one span with both attribute sets; sampling preserved per §5.4.

## §5. Required absorbing artifacts (if recommendation ratified)

Sequenced downstream effects:

| Artifact | Absorption shape | Lane |
|---|---|---|
| `Spec_Control_Plane_v1_3.md` → v1.4 | Add §25 C-CP-25 contract per §4 above; add §[traceability] row; revise change-note; revise filing footer; preserve §1–§24 verbatim. | `spec-writer` |
| `Implementation_Plan_Control_Plane_v2_10.md` → v2.11 | Add ~2 atomic units: (a) `U-CP-NN` driver core implementing §4.4 iteration loop + lifecycle emission; (b) `U-CP-NN+1` drain composition with HarnessContext per §4.5 + RunResult terminal type per §4.3. Dependency-graph delta: new units depend on U-CP-13 (manifest) + U-CP-14 (resolver) + U-CP-10 (event taxonomy) + U-CP-15 (engine class) + U-CP-01 (router) + U-IS-07 (ledger entry) + U-IS-10 (export) + U-IS-11 (append) + U-RT-44 (context). | `implementation-planner` |
| `harness-cp/` source | Land new units per `phase-7-implementation`. | `phase-7-implementation` |
| `harness-runtime/` U-RT-44 + U-RT-49 | Refactor to delegate drain to C-CP-25 driver per §11 C-RT-11 risk-surface guidance. Un-strike U-RT-44 AC #2 + U-RT-49 workflow-execution ACs. Re-run runtime test suite (651 tests + new compositional tests). | `phase-7-implementation` |
| `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` | Status OPEN-RESOLVING → CLOSED at land. | Operator/skill close |

No CXA v2.3 changes required at this contract — the driver is intra-CP-axis with existing typed seams (CP→IS via U-IS-07/10/11; CP→AS via U-CP-01 dispatch; CP→Runtime via HarnessContext) all already enumerated.

## §6. Tiebreaker check + load-bearing implications

**Tiebreaker (single verifiable fact):** Confirm that `Spec_Control_Plane_v1_2.md` §5.1 8-class enumeration (`workflow-start / step-boundary / fallback-trigger / retry-attempt / breaker-trip / lease-acquired / lease-released / resumption`) is preserved verbatim at v1.3 — meaning C-CP-25 v1.4 emits the spec's 8 events, NOT the plan's divergent 8 events (per anti-finding §6.1 below).

**Verified.** v1.3 change-note lists §5 C-CP-05 §5.1 as "preserved verbatim from v1.2." Confirmed at this session. Tiebreaker → spec-side enum.

### §6.1 Anti-finding A — NOT-A-FINDING (resolved at CP plan v2.6 via D9 / Q-R4-7)

**Initial concern.** This session's earlier audit cited an early CP plan v2 body passage enumerating workflow lifecycle events as `WORKFLOW_START / WORKFLOW_CHECKPOINT / WORKFLOW_RESUMPTION / WORKFLOW_FANOUT_OPEN / WORKFLOW_FANOUT_CLOSE / WORKFLOW_HITL_INVOCATION / WORKFLOW_FALLBACK_TRIGGERED / WORKFLOW_BREAKER_TRIPPED` — diverging from CP spec §5.1's `workflow-start / step-boundary / fallback-trigger / retry-attempt / breaker-trip / lease-acquired / lease-released / resumption`. Initial classification: Class 1 distinct fork.

**Verification (this session, post-advisor pushback).** The stale v2 body text was superseded at CP plan **v2.6** by operator-ratified decision **D9 / Q-R4-7** (`Implementation_Plan_Control_Plane_v2_6.md:65`, `:355`, `:370`): U-CP-10's local `LifecycleEventClass` enum was retired; `WorkflowEventClass` from `harness-core` (U-CORE-01) survives as the canonical 8-value type. The harness-core source (`harness-core/src/harness_core/workflow_event_class.py`) materializes the spec §5.1 values verbatim:

```python
WORKFLOW_START   = "workflow-start"
STEP_BOUNDARY    = "step-boundary"
FALLBACK_TRIGGER = "fallback-trigger"
RETRY_ATTEMPT    = "retry-attempt"
BREAKER_TRIP     = "breaker-trip"
LEASE_ACQUIRED   = "lease-acquired"
LEASE_RELEASED   = "lease-released"
RESUMPTION       = "resumption"
```

Runtime tests at `harness-runtime/tests/test_lifecycle_lifecycle_emitter.py` consume this enum directly. Runtime has shipped against the spec's enum (verified at 651 tests on main at `0b7a378`). **§4.6 emission boundaries as drafted are correct.**

**Reclassification.** Not a finding. The earlier-cited v2 body text was a pre-D9 draft, not a shipped contract. CP plan v2.6 → v2.10 declaration-site is fully reconciled to the spec. No separate fork needed.

### §6.2 Anti-finding B (Class 3 informational — pointer fix)

Workspace root `CLAUDE.md` §2.2 ADR table mislabels 4 of 5 F-ADR rows:

| ADR | `CLAUDE.md` §2.2 label | Actual title (verified from file) | Match? |
|---|---|---|---|
| ADR-F1 | Multi-LLM commitment | Multi-LLM provider abstraction | ✅ |
| ADR-F2 | State ledger primitive | Filesystem + git canonical state | ❌ (state-ledger lives ON F2's filesystem, but F2's title is the substrate, not the ledger) |
| ADR-F3 | Index primitive | Stateless-reducer / launch-pause-resume durable-execution | ❌ (F3 owns durable-execution + workflow lifecycle, NOT indexing) |
| ADR-F4 | Workflow lifecycle primitive | Four-tier sandbox isolation | ❌ (F4 owns sandbox, NOT workflow lifecycle) |
| ADR-F5 | Observability substrate primitive | Tier-aware secrets fetch | ❌ (F5 owns secrets, NOT observability) |

`CLAUDE.md` §2.2 D-ADR rows may also warrant verification under the same pattern (not audited this session).

This is Class 3 (informational; not blocking C-CP-25). Per workspace governance, the ADR file titles are authoritative; the `CLAUDE.md` table is a navigation index. Recommended action: pointer fix at next `CLAUDE.md` revision pass — re-label all 4 incorrect F-ADR rows + audit D-ADR rows. Non-blocking either way; the recommendation traces to actual ADR-F3 v1.1 §Decision content verbatim, not to the index label.

## §7. Fork classification per `Project_Workflow_v1_8.md` §2.7.6

| Class | Verdict |
|---|---|
| **Class 1 (halt-execution)** | YES — primary fork. The authority chain is silent on the driver; new contract authorship required before Phase 7 execution can un-strike U-RT-44 AC #2 + U-RT-49 ACs. C-CP-25 contract authoring is the resolution path. |
| **Class 2 (in-execution operator decision)** | NO. |
| **Class 3 (informational)** | YES — anti-finding §6.2 (CLAUDE.md §2.2 ADR table mislabels 4 F-ADR rows); file pointer fix at convenience. Anti-finding §6.1 reclassified to NOT-A-FINDING after verification. |

## §8. Operator decision required

**This recommendation is a DRAFT. The systems-architect role does not decide; the operator decides** (per skill §4A.4: "Does not decide. It recommends; the operator decides.").

Required operator sign-off points:

1. **Scope (§4.2).** Approve `SINGLE_THREADED_LINEAR`-only scope with explicit deferral notation for the 5 other topology patterns? (Recommended: yes — matches X-AL-3 discipline + un-blocks runtime ACs in minimum-blast-radius arc.)
2. **Engine-class scope (§4.4.1).** Approve `pure-pattern-no-engine` + `save-point-checkpoint` only at v1.4? (Recommended: yes — the simplest two engine cells; matches the runtime's filesystem-journal default.)
3. **Drain semantics (§4.5).** Approve the 4-site drain check pattern (entry / per-step-pre / per-step-post / no-mid-step) with terminal status via RunResult rather than via lifecycle event? (Recommended: yes — matches `Spec_Harness_Runtime_v1.md` §11 v1.2 settlement which already STRUCK the DRAINED event class.)
4. **Lifecycle event filter (§4.6).** Approve the per-event applicability table? (Recommended: yes — strictly composes against §5.1 closed-at-8.)
5. **Anti-finding A (§6.1).** No sign-off needed — reclassified to NOT-A-FINDING this session after verification. Runtime emits the spec §5.1 enum verbatim; CP plan v2.6 onward conforms.
6. **Anti-finding B (§6.2).** Approve queuing `CLAUDE.md` §2.2 ADR table pointer fix (4 F-ADR rows mislabeled; D-ADR rows may warrant audit too)? (Recommended: yes — low-effort cleanup, deferrable.)

On sign-off: open `spec-writer` skill against this recommendation to apply C-CP-25 into `Spec_Control_Plane_v1_3.md` → v1.4.

---

## §9. Provenance

| Source | Citation |
|---|---|
| Authority chain | `CLAUDE.md` §1.3 |
| F3 commitment | `ADR-F3.md` v1.1 §Decision (iv) "workflow lifecycle event surface visible at run-event surface as distinct event classes" |
| Workflow manifest schema | `Spec_Control_Plane_v1_2.md` §6.1 (preserved verbatim at v1.3) |
| Per-step override | `Spec_Control_Plane_v1_2.md` §6.2 + U-CP-14 (`Implementation_Plan_Control_Plane_v2.md` lines 795–840) |
| 8-class lifecycle event taxonomy | `Spec_Control_Plane_v1_2.md` §5.1 (preserved verbatim at v1.3) |
| Per-class minimum attribute set | `Spec_Control_Plane_v1_2.md` §5.2 |
| Sampling discipline | `Spec_Control_Plane_v1_2.md` §5.4 |
| 6-pattern topology | `Spec_Control_Plane_v1_2.md` §10.1 |
| Engine class taxonomy | `Spec_Control_Plane_v1_2.md` §7 + §8.1 |
| Idempotency-key join | `Spec_Control_Plane_v1_2.md` §8.2 |
| `engine.*` namespace | `Spec_Control_Plane_v1_2.md` §9.1 (extended to 4 attrs at v1.3) |
| Drain runtime-owned settlement | `Spec_Harness_Runtime_v1.md` §11 C-RT-11 (v1.2 amendment 2026-05-20) |
| HarnessContext shape | `Spec_Harness_Runtime_v1.md` §[U-RT-44 surfaces] |
| Source tension | `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` |
| Session entry-point lock | `~/.gstack/projects/arhugula-v2/checkpoints/20260520-035000-cp-workflow-driver-spec-gap-locked.md` |

---

*End of recommendation. STOP for operator ratification per `systems-architect` skill §4A.4. No spec edits performed.*
