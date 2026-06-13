# R-FS-1 Arc #2 — B1 Topology Orchestration: Design

**Authored:** 2026-06-13 · **Posture:** mode-agnostic (process-substrate; grounds `harness-*/src` + canonical specs + ADRs at HEAD `5d4166c` by direct read; authors only this `.harness/` design artifact — **zero `design-substrate/**` or `harness-*/src` edit, X-AL-3 trivially clean**). **Arc:** R-FS-1 arc #2 (B1). **Spine:** `.harness/beyond-mvp-capability-boundary-ledger.md` (Bucket B row B1) + `.harness/r-fs-1-arc-1-scoping-v1.md` (Part 3 child-arc B1). **Directive:** `[[feedback-full-spec-beyond-mvp-nothing-deferred]]`.

**Precedent:** this is the design-first PR of the B1 sub-program, following the R-PM-1 shape (arc #2 opened with a `.harness/` design doc at #505, then cascaded spec→impl PRs #506–#511 each with a clearance marker). B1 is the largest R-FS-1 arc; this doc is **design-only** and authors no contract. The spec→plan→implement cascade is subsequent arc PRs (§8).

---

## §0 What B1 is, and what this PR is

**B1 = materialize real orchestration semantics for the 5 non-`SINGLE_THREADED_LINEAR` topology patterns** — `PARALLELIZATION`, `ORCHESTRATOR_WORKERS`, `DECENTRALIZED_HANDOFF`, `HIERARCHICAL_DELEGATION`, `EVALUATOR_OPTIMIZER`. It is the "multi-agent parallel + cross-agent communication" capability — the single biggest beyond-MVP gap (ledger B1: "HIGHEST"). The owning contract is **C-CP-25 WorkflowDriver** (v1.6-lineage; *not* C-CP-28 ValidatorFramework — that ID collision was renamed at CP spec v1.13).

**This PR** is the design artifact. Per X-AL-3 (no silent H_T design extension at Phase 7), the orchestration semantics must be designed and the design routed through back-flow *before* implementation. This doc:
1. Grounds the current state (§1).
2. Settles the one decision that could have changed the back-flow route — **does parallel execution force a change to the hash-chained state ledger?** (§2). It does not.
3. Designs the per-pattern orchestration semantics (§3), the B1↔B4 role seam (§4), cascade-cancel blast radius (§5), the CP-AL-1 boundary (§6), and the determinism boundary (§7).
4. Enumerates the cascade-fork list — which specs are amended in which subsequent PRs, and which design forks to file (§8).

**Default-if-silent:** proceed to the §8 cascade as enumerated. The one genuinely operator-open lever is surfaced at §4/§10 (the B1↔B4 sequencing nuance) — with a recommendation, not a hard gate.

---

## §1 Grounding (current state at HEAD `5d4166c`)

| Surface | State | Carrier |
|---|---|---|
| `TopologyPattern` enum | Closed at 6 (ADR-D4 §1.1 / C-CP-10 §10.1). All 6 values exist; extension is a Workflow §4.1.2 Class-2 D4 revision. | `harness-cp/src/harness_cp/topology_pattern.py` |
| `CascadePolicy` enum | `pause` / `proceed` / `cascade-cancel` (C-CP-10 §10.2 field domain). Declared but unconsumed by any non-linear driver. | `topology_pattern.py` |
| `is_admissible` | C-CP-10 §10.3 cross-pattern admissibility predicate (the §10.3 non-primary cells; primary-pattern-per-workload is C-CP-11 §11.1). | `topology_pattern.py` |
| **C-CP-25 WorkflowDriver** | `execute_workflow(manifest_entry, steps, run_id, ctx) -> RunResult`. **Only `SINGLE_THREADED_LINEAR` materialized** — a linear `for step in steps` iteration (`workflow_driver.py:756-766`). The other 5 patterns raise `TopologyPatternNotYetMaterializedError` (`workflow_driver_errors.py:27-36`; driver gate at `workflow_driver.py:710-712`). | `workflow_driver.py` (1362 lines) |
| C-CP-25 deferral table | The v1.4 spec §25.1 explicitly defers the 5 patterns: *"Extension contract (C-CP-25.b or C-CP-26) authored when the first multi-worker workflow unit demands materialization."* | `Spec_Control_Plane_v1_6.md` §25.1 |
| State ledger **persisted** entry | 6 F-layer fields `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` + the v1.3 `procedural_tier_snapshot_ref` D-derivative sidecar; **single** `prior_event_hash: Bytes32`. Per-workload-class extension records **subclass `StateLedgerEntry` and MAY add fields** (acceptance #5), but the **write contract `EntryPayload` is `extra="forbid"`** (`state_ledger_write.py:80`) — a caller cannot smuggle extra fields; persisting a new field requires the D-derivative-sidecar route (the `procedural_tier_snapshot_ref` precedent: field added to `StateLedgerEntry` **and** `EntryPayload` **and** `_serialize_entry`). | `state_ledger_entry_schema.py:62-89`; `state_ledger_write.py:80-208` |
| Hash chain | `entry[N].prior_event_hash = SHA-256(canonicalize(entry[N-1]))`; inception = all-zeros sentinel. **Single-parent linear chain.** | C-IS-06 §6 (`Spec_Information_Substrate_v1.md:486-487`); ADR-F2 §Rationale (a.1) |
| Parent-keying — **driver-transient, NOT persisted** | `StepExecutionContext` carries `parent_action_id`, `parent_entry_hash`, `parent_gate_level`, `parent_actor`, `workflow_id` — but these are **ephemeral driver-scope metadata**, *not* fields on the persisted `StateLedgerEntry`. The driver already composes `parent_action_id` by string interpolation; HITL composes `compose_hitl_action_id(parent_action_id, placement.position)` **into the `action_id`** (a persisted F-layer field). The §5 field-spec footer authorizes `action_id` MAY encode action class / sub-class metadata; IS spec v1.3 Amendment 3 ratified that *structured traceability* MUST flow via a **sidecar field**, not action_id-encoding (carriers kept separate to avoid conflation). | `workflow_driver_types.py:158-223`; `Spec_Information_Substrate_v1.md:342,376` |
| Sub-agent substrate (already present) | `sub_agent_brief.py`, `sub_agent_gate_level_descent.py`, `gate_level_rule.py` (C-CP-12 gate-level descent), `topology_subagent_namespace.py`. `SUB_AGENT_DISPATCH` is a closed `StepKind` value. | `harness-cp/src/harness_cp/` |
| CP-AL-1 boundary | H_E sub-agent topology (Claude Code `Agent` tool) **≠** H_T `TopologyPattern`. The 5 patterns are H_T primitives, hand-rolled (I-6), never delegated to the H_E orchestrator. | `Phase_7_Meta_Architecture_v1.md` §7.4 CP-AL-1 |

**The shape of the gap:** the 5 patterns are *admissible* (the manifest accepts them, telemetry emits) but execute as a **stateless passthrough** — there is no fan-out, no worker dispatch, no handoff, no evaluator loop. The driver's `_IN_SCOPE_TOPOLOGY` is `frozenset({SINGLE_THREADED_LINEAR})` (`workflow_driver.py:83`).

---

## §2 DECISION D1 — Parallel execution does NOT change the hash-chained ledger

This is the decision that governs the entire cascade-fork route. It was probed before the per-pattern design, because the wrong answer here would route B1 to a **foundational-ADR** back-flow (the heaviest route), and silently absorbing that as "just a spec change" is the §4.4 worst-failure-mode.

### §2.1 The reframe

**Parallel *execution* does not require parallel ledger *appends*.** The tractable model — and, as §2.3 shows, ADR-F2's *own* prescribed resolution — is:

> Run branch work concurrently (`asyncio.gather` over the fan-out), then **serialize the resulting ledger appends through the single writer in deterministic declaration order** (branch-index order, *not* completion order).

> **D1.b (mechanism — load-bearing; Codex-caught, §9).** This **requires a buffered/deferred-append branch-execution path** — the parallel strategies MUST NOT reuse the existing inline per-step append. Today `_execute_workflow_body` calls `ctx.ledger_writer.append` *immediately after each step* (`workflow_driver.py`), and the IS writer lock (`state_ledger_write.py:_WRITE_LOCK`) serializes by *whoever finishes first*; running that path inside `asyncio.gather` would persist entries in **completion order**, silently falsifying the deterministic-append guarantee (§7). So a branch executes its step bodies + emits telemetry but **buffers its pending entries** (returns an ordered list), and the **orchestrator drains the buffers through the single writer in branch-index order at the barrier**. The inline-append path stays the `SINGLE_THREADED_LINEAR` strategy verbatim; the buffered path is a new branch-execution mechanism (B1-spec-2 / impl scope, §8). This is what *makes D1's deterministic-append claim true against the current driver*, not just asserted.

The hash chain stays single-parent linear and untouched. The only thing that would *force* a chain change is a pattern requiring the ledger to record **multi-parent branch causality** — an entry with >1 `prior_event_hash`. The discriminating question is therefore: **does any of the 5 patterns need recorded multi-parent causality in the canonical entry, or does serialized-append-of-parallel-execution + causality-in-payload suffice?**

### §2.2 Per-pattern check — none needs DAG causality in the canonical entry

| Pattern | Execution shape | Needs multi-parent `prior_event_hash`? |
|---|---|---|
| `PARALLELIZATION` | N branches concurrent → barrier → aggregate | **No.** Each branch's steps append serialized in branch-index order; the fan-out join is recorded as payload (`parent_action_id` = the fan-out point, `branch_index`). |
| `ORCHESTRATOR_WORKERS` | Orchestrator dispatches workers, collects | **No.** Worker steps serialize under the orchestrator's `parent_action_id`; aggregation is one further linear entry. |
| `DECENTRALIZED_HANDOFF` | Single-owner-at-a-time, sequential handoff | **No** — inherently sequential; trivially linear (`cascade-cancel` single-owner). |
| `HIERARCHICAL_DELEGATION` | Recursive delegation (fan-out cap 3/parent) | **No.** A tree, but the *ledger* serializes in deterministic DFS/declaration order with `parent_action_id` capturing the tree edge. |
| `EVALUATOR_OPTIMIZER` | generate→evaluate→regenerate loop | **No** — sequential iterations; trivially linear. |

**Branch causality is a payload concern, not a chain-topology concern** — but it must be *persisted*, and the existing `parent_action_id` / `parent_entry_hash` fields on `StepExecutionContext` are **driver-transient, not written to the ledger** (the `EntryPayload` write contract is `extra="forbid"`; *Codex-caught correction*, §9). Recording branch causality **durably** therefore has two ADR-faithful routes — **neither touches the six-field shape, the hash-chain construction, or ADR-F2 §Decision** (resolved at §2.4). What does *not* change: no second `prior_event_hash`, no DAG entry, no multi-parent chain.

### §2.3 Authority-level finding — this is ADR-F2's prescribed resolution, not a fork against it

The single-parent linear chain is **ADR-anchored** (ADR-F2 v1.2 §Decision + §Rationale (a.1)), not merely C-IS-05 §5 spec; IS-AL-3 declares the 6-field shape "inviolate." So D1 had to be checked against ADR-F2 directly. It is *consonant*, not contradictory:

> ADR-F2 §Consequences: *"Concurrent writes to substrate. Filesystem doesn't provide distributed locking; concurrent sub-agents must coordinate via **worktree-isolation** or **single-threaded-write boundary (Cognition convergence** per Brainstorm synthesis §1). Multi-writer scale beyond worktree-isolation requires a downstream D-ADR on coordination shape."*

ADR-F2 already anticipated concurrent sub-agents and named the resolution: **single-threaded-write boundary**. D1's serialized-append model *is* that boundary. Worktree-isolation (C-IS-09 §9.1 per-sub-agent worktree opt-in) is the *read* fan-out side, also already specified. B1's concurrency lives at the **execution** layer (concurrent dispatch + concurrent reads via worktree-isolation), and converges to a **single-threaded ledger writer** at the audit layer.

> **D1 (decision):** B1 uses concurrent execution + single-threaded serialized ledger appends in deterministic declaration order; no second `prior_event_hash`, no DAG entry, no multi-parent chain. **Zero ADR-F2 §Decision change. Zero C-IS-05 §5 six-field-shape change. Zero hash-chain-construction change.** The cascade-fork route is CP/runtime + a *bounded* IS D-derivative sidecar (§2.4 / §8), **not** the foundational-ADR (heaviest) route.

This is the load-bearing simplification: it collapses what the ledger framed as B1's "biggest tension" (parallel fan-out ⊥ the inviolate hash chain) to a single-threaded-write boundary — *which is ADR-F2's own prescribed resolution* — plus a precedented sidecar field for branch causality (§2.4). B1 stays inside the CP/runtime back-flow the C-CP-25 §25.1 deferral table already anticipates ("Extension contract C-CP-25.b or C-CP-26"), coordinated with one bounded IS amendment.

### §2.4 Recording branch causality durably — the one IS touch (Route X vs Route Y)

The persisted entry does **not** carry parent linkage today, and `EntryPayload` forbids extras. Two ADR-faithful routes record it durably; the choice is a B1-spec-1 / IS-coordination fork (not a freebie — the §9 Codex correction):

| Route | Mechanism | IS-axis cost | Discipline fit |
|---|---|---|---|
| **X — `action_id` encoding** | Compose `parent_action_id` + `branch_index` **+ `terminal_status`** *into* the child entry's `action_id` (a persisted F-layer field), per the HITL `compose_*_action_id` precedent + the §5 footer "action_id MAY encode … sub-class metadata". | **Zero IS-schema change**, but **not zero-work**: D3's resume contract requires a *defined* terminal-status encoding **+ a resume-side parser** to read it back from `action_id` — a parsing convention the spec must specify. | **Disfavored.** IS spec v1.3 Amendment 3 ratified that *structured traceability* MUST flow via a **sidecar**, not action_id-encoding (carriers kept separate to avoid conflation); branch causality + status is structured traceability, not a class label. And a string-parsed `terminal_status` is a fragile read path vs a typed sidecar field. |
| **Y — D-derivative sidecar field** | Add a `branch_metadata` sidecar — `{parent_action_id, branch_index, terminal_status}` (causality **+** the §5-commitment-2 persisted cancellation marker) — to `StateLedgerEntry` **and** `EntryPayload` **and** `_serialize_entry`/deserialize, the exact `procedural_tier_snapshot_ref` template (ADR-F2 §Consequences (c); "ZERO change to six-field shape / §6 hash-chain / §7 read-write contracts"). | **Bounded IS amendment** (C-IS-05 §5.x new sidecar — additive at the D-derivative layer; *not* ADR-F2 §Decision). | **Recommended.** Follows the workspace's own ratified MAY/MUST separation; also carries the cancellation marker D3 needs. |

> **D1.a (recommended):** **Route Y** — a bounded D-derivative `branch_metadata` sidecar carrying both branch causality **and** the persisted `terminal_status` cancellation marker (§5 commitment 2), mirroring `procedural_tier_snapshot_ref`. One coordinated IS PR (§8), precedented and additive — *not* a foundational-ADR revision, *not* a six-field-shape change. (Note: branch identity in the **idempotency-key** composition is a *separate, CP-side* change, §5 commitment 3 — it is not part of this IS sidecar.) **D3 makes a *persisted, machine-readable* `terminal_status` a hard requirement** — Route Y satisfies it as a typed field; Route X remains viable only if B1-spec-1 *also* specifies the action_id terminal-status encoding **and** the resume-side parser (a string-parse read path, fragile vs a typed field). Either way the cancellation-marker read path is defined — no route may leave it implicit. The B1-spec-1 fork records both readings (recommend Y).

---

## §3 Per-pattern orchestration semantics (hand-rolled, I-6 / asyncio)

**Research grounding (§10.9 role-2; corpus = `.harness/01-planning/.../00-harness-research/`).** The 5 patterns are Anthropic's canonical "Building Effective Agents" workflow set (parallelization / orchestrator-workers / evaluator-optimizer + routing/chaining; cluster-4 §refs). Two corpus failure modes shape the designs below and the cascade-cancel fork: **sub-agent interrupt stranding** — "a parent times out waiting on a sub-agent itself stuck in interrupt; cascade requires careful timeout composition" (cluster-4 §2.4.6) → ORCHESTRATOR_WORKERS / HIERARCHICAL_DELEGATION need per-level timeout composition (a barrier must bound its wait, not block forever); **graceful degradation over retry-storm** — "tertiary failure → return partial result with `degraded=true`, NOT another retry" (cluster-4 §2.3.x, Google SRE) → the `proceed` cascade policy. This is a *targeted* consultation; the per-pattern designs below are intentionally terse — fuller corpus consultation (the cluster deep-dives' production failure modes for each pattern) continues at **B1-spec-1** where the strategy contracts are authored.

Each pattern is materialized as a **driver strategy** selected by `manifest_entry.topology_pattern`, replacing the `_IN_SCOPE_TOPOLOGY` gate. All strategies reuse the existing `StepDispatcher` registry (`workflow_driver.py:167-264`), the per-step **entry construction**, and the 8-class lifecycle event surface; they differ in *control flow over steps* and in *when the ledger write happens*. **The `SINGLE_THREADED_LINEAR` strategy keeps the inline per-step append verbatim; the 5 non-linear strategies use the buffered/deferred-append path (D1.b) — entry construction + telemetry inline, the ledger *write* deferred to the orchestrator's branch-index-ordered drain.** Reusing the inline append inside `gather` is the foreclosed anti-pattern (it would persist in completion order). Kept terse per the design-value discipline — the decisions are §2/§4/§5, the per-pattern flow is mechanical.

**Common substrate (all 5):**
- A **branch** = a sub-sequence of `WorkflowStep`s dispatched under a child `StepExecutionContext` (`parent_action_id` = the spawning step's action_id).
- **Concurrency** = `asyncio.gather` (or `asyncio.TaskGroup` for structured cancellation, §5) over branches; never the H_E `Agent` tool (§6).
- **Append discipline** = D1/D1.b: branches use the **buffered-append path** (execute + emit, defer the ledger write, return an ordered pending-entry list); the orchestrator drains buffers through the single `LedgerWriterLike` in branch-index order at the barrier. Never the inline per-step append of `_execute_workflow_body` (that stays `SINGLE_THREADED_LINEAR`-only).
- **Determinism** = aggregation is a pure function of the *set* of branch results, ordered deterministically (§7).
- **Bounded barriers** = every barrier (`gather`/`TaskGroup` join) is wrapped in a wall-clock deadline so a stuck branch cannot strand its parent indefinitely (the corpus "sub-agent interrupt stranding" failure mode, §3 grounding); deadline-exceeded composes with `cascade_policy` (timeout → cancel/degrade per the policy).

| Pattern | Orchestration semantics | Aggregation / barrier | Meaningful at B1-alone? |
|---|---|---|---|
| **`PARALLELIZATION`** | Fan-out N declarative/inference branches over varied inputs concurrently (cap 3–5 per C-CP-10 §10.3 research/content-creation cells). | **Barrier** — `gather` holds until all branches finish; a synthesis/voting aggregator step folds structured outputs into one result (corpus "fan-out-and-synthesize", `dynamic-workflows.md:90`). | **Yes** — non-degenerate with one role (variation is in *inputs*, not agent specialization). |
| **`EVALUATOR_OPTIMIZER`** | Loop: generate-step → evaluate-step → (accept | regenerate with feedback), bounded by a max-iteration cap. | Sequential; terminal on evaluator accept or cap. | **Yes** — the evaluator/optimizer are *roles by prompt*, expressible at B1 via per-step prompt (already landed, R-PM-1) without B4. |
| **`ORCHESTRATOR_WORKERS`** | An orchestrator step computes a dynamic worker set, dispatches workers concurrently, collects. | **Barrier** at collection; orchestrator composes the final result. | **Partial** — real value needs *specialized* workers (per-role model/prompt) → leans on B4 (§4). |
| **`HIERARCHICAL_DELEGATION`** | Recursive `ORCHESTRATOR_WORKERS` with depth; fan-out cap 3 per parent (C-CP-10 §10.3); gate-level **descends** per child (`sub_agent_gate_level_descent.py`, C-CP-12 §12.2). | Bottom-up: each parent barriers on its children, composes upward. | **Partial** — same role-specialization dependence as orchestrator-workers (§4). |
| **`DECENTRALIZED_HANDOFF`** | Single-owner-at-a-time; each stage-expert hands the workflow to the next via a `HandoffContext`; `cascade-policy = cascade-cancel` (pipeline-automation per-stage, C-CP-10 §10.3). | Sequential ownership transfer; terminal when no further handoff. | **Partial** — "stage-expert" = a specialized role; degenerate without B4 (§4). |

**Driver-strategy selection** replaces the single `_IN_SCOPE_TOPOLOGY` gate with a dispatch table `topology_pattern → strategy`. The `SINGLE_THREADED_LINEAR` strategy is the existing loop verbatim (regression-safe). This is the C-CP-25.b / C-CP-26 extension contract the §25.1 deferral table calls for.

---

## §4 The B1↔B4 role seam (advisor item #3 — pin it or B1 ships degenerate)

**The problem.** B4 (per-role / per-step dispatch) is sequenced 6th in the frozen child-arc list; today `AgentRole` is **discarded at dispatch** (`llm_dispatch.py:489`, per the PR #509 record). Of the 5 patterns, **3 lean on specialized agents** — `ORCHESTRATOR_WORKERS`, `HIERARCHICAL_DELEGATION`, `DECENTRALIZED_HANDOFF` are *hollow* with same-role workers (an "orchestrator dispatching workers" where every worker is the identical default agent is a parallel loop with extra ceremony). The 2 input-varied patterns (`PARALLELIZATION`, `EVALUATOR_OPTIMIZER`) are non-degenerate at B1-alone.

**The seam.** Both `RoutingManifest.per_role_bindings` and `PromptSelectionManifest.per_role_bindings` already carry per-role bindings *structurally* (landed R-PM-1 #509); the gap is purely the **runtime indexer** that threads `AgentRole` (+ per-step override) through dispatch so the per-role model + per-role prompt take effect. The ledger's own B4 row notes this is "small once B1 motivates it."

> **D2 (decision):** **Fold the role-threading mechanism into B1.** B1's branch-spawning composes a child `StepExecutionContext` that *carries* `AgentRole`, and threads it to dispatch (the indexer at the `llm_dispatch` seam). This is a reversible design call that does not sacrifice a committed decision — it makes the worker/delegation/handoff patterns non-hollow *by construction* and is the minimal mechanism B4's binding-application rides on. B1 pins the seam; B4 (the per-role binding *catalog* + per-step override surface) remains a distinct follow-on but is no longer a hard prerequisite for B1 to be meaningful.

**Surfaced (operator-open — sequencing only, not whether-to-build; §10).** If the operator prefers strict arc isolation over folding the role-seam into B1, the alternative is to **re-order B4 before B1** (the directive froze build-vs-defer, not sequence). My recommendation is D2 (fold the mechanism, keep B4's catalog as the follow-on) because it avoids shipping 3 hollow patterns *and* avoids a full B4 arc as a blocking prerequisite. Default-if-silent: D2.

---

## §5 Cascade-cancel semantics + blast radius (the remaining genuinely-contested surface — C10)

`CascadePolicy` (`pause` / `proceed` / `cascade-cancel`) is declared but unconsumed. Under fan-out it becomes load-bearing — this is the action-safety/blast-radius (C10) surface that the ledger flagged ("`cascade-cancelled` fan-out semantics" folds into B1).

**Semantics under a barrier (`PARALLELIZATION` / `ORCHESTRATOR_WORKERS` / `HIERARCHICAL_DELEGATION`):**

| `cascade_policy` | On a branch failure | Sibling branches | Ledger record |
|---|---|---|---|
| `proceed` | Record failure; aggregator sees a partial result set | Run to completion | All branches append; aggregator entry notes the partial set |
| `pause` | Halt the fan-out at a HITL/pause boundary (composes with the existing pause/resume, C-RT-30 `api.resume`) | Allowed to finish in-flight, then pause | Pause entry + in-flight branch entries |
| `cascade-cancel` | **Cancel in-flight siblings** (`asyncio.TaskGroup` cancellation), fail the fan-out | Cancelled | Each cancelled branch appends a terminal entry carrying a **persisted** cancellation marker (audit completeness — a cancelled branch is *not* a silent gap) |

**Five design commitments for `cascade-cancel`** (commitments 2–4 are Codex-caught implementation-contract requirements, §9; commitment 5 is the advisor-caught effectful-cancellation blast radius — naming them is what makes D3 *implementable* and *honest*, not merely asserted):
1. **Structured cancellation.** Use `asyncio.TaskGroup` (3.11+) so a failing branch's exception cancels siblings deterministically; a bare `gather(return_exceptions=False)` leaks orphaned tasks. (I-6: hand-rolled, stdlib only.)
2. **Cancellation is audit-visible via a *persisted* marker.** A cancelled branch appends a terminal entry before the fan-out fails — but `fail_class = cascade_cancelled` is a `RunResult` field, **not** a persisted `StateLedgerEntry` field, so the persisted entry needs an explicit cancellation encoding: **fold a `terminal_status` into the Route-Y branch-metadata sidecar** (the recommended route already adds a D-derivative sidecar; widen it from causality-only to `{parent_action_id, branch_index, terminal_status}`), or encode it in the action_id (Route X). Without a persisted marker, resume cannot tell a cancelled branch from any other entry. `[[feedback-verify-observation-layer-before-concluding-defect]]` in reverse: a cancelled branch with no *distinguishable* ledger entry reads as "never dispatched / still pending."
3. **Branch identity in the idempotency key.** The driver computes step idempotency as `sha256(run_idempotency_key, step_index)` and the IS writer deduplicates **solely on `idempotency_key`** — so N parallel branches at the *same declared step_index* would collapse to one entry (silent branch loss) unless the **branch path enters the idempotency-key composition**: `sha256(run_idempotency_key, step_index, branch_path)`. This is a **CP-side driver/write-key composition change** (`idempotency_key` is driver-composed; the C-IS-07 §7.5 keying tuple already treats write-key components as write-args) — bounded, **no six-field/ADR change**. It is load-bearing for *both* correct fan-out persistence *and* resume/cancel terminality.
4. **Idempotency-terminality across resume.** Given commitments 2+3, on `api.resume` after a `cascade-cancel` the resumed run reads each branch's terminal entry by its branch-scoped idempotency key and MUST NOT re-dispatch a branch whose persisted `terminal_status` is cancelled (composes with the §8.2 idempotency-key join at re-entry). Re-dispatch of a deliberately-cancelled branch is the correctness hazard foreclosed. (Corpus-grounded: "make every interrupt-resume path idempotent — any operation before the pause MUST be re-executable safely", cluster-4 §2.4.7.)
5. **Effectful cancellation has no clean rollback — this is an OPEN C10 fork, not resolved here.** `asyncio.TaskGroup` cancellation aborts the *Python task*, but it CANNOT roll back an already-dispatched **effectful** step: a `TOOL_STEP` whose sandbox call already hit the world (a file written, an email sent, an API mutated) or a billed `INFERENCE_STEP`. So `cascade-cancel` cleanly cancels only steps **not yet dispatched**; an in-flight effectful step either runs to its own completion/timeout (recorded) or is abandoned with its external side effect **uncompensated**. The production discipline (corpus) is *cancel-before-dispatch* — Google SRE "Addressing Cascading Failures" (request-cancellation propagation + RPC deadlines + graceful degradation, returning a partial result with `degraded=true` rather than a retry storm, cluster-4 §2.2/§2.3.x) + **dry-run-then-approve for high-blast-radius tools** (cluster-4 §2.4.7) — *not* rollback-after. Compensation/saga semantics or restricting `cascade-cancel` to pre-dispatch boundaries is the **C10 design fork for B1-spec-1** (it composes with the C-CP sandbox-tier/HITL gate — a high-blast-radius effectful step should gate *before* dispatch, where cancellation is clean).

> **D3 (decision):** `cascade-cancel` = `asyncio.TaskGroup` structured cancellation + a **persisted** cancellation marker per cancelled branch (sidecar `terminal_status`, Route Y) + **branch-scoped idempotency keys** (`branch_path` in the key composition, Stripe-form per cluster-4 §2.2.7) + idempotency-terminality across resume. `proceed` = graceful-degradation partial-aggregate (`degraded=true`, SRE-grounded); `pause` = HITL-pause. **This resolves the *audit/idempotency* half of the C1-orchestration ⊥ C10-action-safety tension** (audit-completeness + resume-terminality, reducing to one CP-driver key-composition change + the Route-Y sidecar — no ADR/six-field change). **The *effectful-cancellation blast radius* (commitment 5) is NOT resolved here — it is an open C10 fork for B1-spec-1.** (See §9; per CLAUDE.md §13.4, an advisor-only "resolved" on a C10 surface that covered only the auditable half would be the named failure mode — so this is honestly downgraded.)

---

## §6 CP-AL-1 boundary (do not collapse H_E sub-agents into H_T topology)

**Hard invariant.** The 5 patterns are **H_T Control-Plane primitives, hand-rolled in asyncio**. They MUST NOT be implemented by calling the Claude Code `Agent` tool or any H_E orchestration primitive (CP-AL-1, Meta-Architecture §7.4; I-4 substrate boundary at the MCP server process). The anti-pattern foreclosed: "we already have orchestrator-workers via the `Agent` tool, so C-CP-25 multi-worker is met" — false; that is H_E topology, not H_T's.

- `SUB_AGENT_DISPATCH` (`StepKind`) is H_T's *own* sub-agent primitive — it dispatches a child workflow branch under a descended gate-level (`sub_agent_gate_level_descent.py`), through H_T's dispatcher registry, recorded in H_T's ledger. It is not a call into H_E.
- Concurrency is `asyncio` within the H_T runtime process; "cross-agent communication" is H_T branches exchanging structured results through the H_T state ledger / `HandoffContext`, not H_E inter-agent messaging.

This boundary is why B1 is an I-6 hand-roll (no `langgraph` / `crewai` / `temporal`) — the committed HOW the FULL-SPEC directive explicitly preserves.

---

## §7 Determinism boundary (ADD §5.3.3 — the deterministic outer harness)

Production reliability lives in the deterministic outer harness; the probabilistic surface is the model call inside a step. B1 must not leak completion-order non-determinism into the audit:
- **Concurrent completion order is non-deterministic; ledger append order is not.** D1.b's buffered-then-branch-index-ordered drain makes the *append order* deterministic **given fixed step outputs** — it does NOT make the chain byte-identical across replay (a replay re-runs non-deterministic `INFERENCE_STEP`s → different `response_hash` → a different chain; non-determinism stays confined *inside* the step per ADD §5.3.3). The guarantee is: the chain is a deterministic function of the (ordered) step-output set, independent of which branch's model call returned first. (The inline per-step append path would leak completion order into that function; that is exactly why branches must buffer, §2.1.)
- **Aggregation is a pure function of the ordered result set** — no aggregator may depend on arrival order (e.g., "first to finish wins" is forbidden; "lowest branch-index on tie" is the deterministic tiebreak, mirroring the existing council/voting convention).
- **Branch-scoped idempotency keys** stay deterministic per branch — `branch_path` is part of the *idempotency-key* composition (`sha256(run_idempotency_key, step_index, branch_path)`, §5 commitment 3), **not** merely the action_id, because the IS writer dedups on `idempotency_key`. This is what makes resume exact *and* prevents same-step-index branches from collapsing.

---

## §8 Cascade-fork enumeration (the sequencing deliverable)

The subsequent B1 sub-program PRs, in order. Each large step is design→spec→plan→implement; each spec PR carries a clearance marker (§4.5). **No ADR-F2 §Decision revision; no six-field-shape change** (per D1) — but **one bounded IS D-derivative sidecar amendment** for branch causality (Route Y, §2.4).

| PR | Scope | Artifact(s) | Back-flow |
|---|---|---|---|
| **B1-design (this PR)** | The design above | `.harness/r-fs-1-b1-topology-orchestration-design-v1.md` | mode-agnostic; X-AL-3-clean |
| **B1-spec-1** | C-CP-25 extension contract (C-CP-25.b or new C-CP-26) — the driver-strategy surface + the 5 strategies' contracts + `cascade_policy` consumption + the role seam (D2) + cancellation (D3) + **branch-scoped idempotency-key composition** (`branch_path` in the key, §5 commitment 3 — CP-side, no IS-schema change). Records the Route-X-vs-Y branch-metadata fork (§2.4). | CP spec amendment (`Spec_Control_Plane` vNext §25 extension) + clearance marker | design-substrate edit → clearance marker (X-AL-3 satisfied) |
| **B1-spec-1b (IS, coordinated)** | *If Route Y:* the bounded D-derivative `branch_metadata` sidecar (`{parent_action_id, branch_index, terminal_status}` — causality + cancellation marker) on `StateLedgerEntry` + `EntryPayload` + serialize (the `procedural_tier_snapshot_ref` template; ADR-F2 §Consequences (c); zero six-field/hash-chain change). Skipped if B1-spec-1 ratifies Route X (zero-schema action_id encoding). | IS spec amendment (C-IS-05 §5.x sidecar) + clearance marker | design-substrate edit → clearance marker |
| **B1-spec-2** | Runtime spec: driver-strategy materialization at the runtime composition site; the **buffered/deferred-append branch-execution path** (D1.b — execute+emit, defer the ledger write, orchestrator drains in branch-index order); `RunStatus.PARTIAL` activation (reserved at §25.2); branch `StepExecutionContext` composition. | Runtime spec amendment + clearance marker | design-substrate edit → clearance marker |
| **B1-plan** | CP + runtime (+ IS if Route Y) plan atomic-unit decomposition for the strategies (implementation-planner). | Plan amendments (CP `Implementation_Plan` vNext + runtime + IS) | design-substrate edit → clearance marker |
| **B1-impl-N** | Implement per strategy, simplest→hardest: `PARALLELIZATION` → `EVALUATOR_OPTIMIZER` → `ORCHESTRATOR_WORKERS` → `HIERARCHICAL_DELEGATION` → `DECENTRALIZED_HANDOFF`. Each: driver strategy + tests (incl. a deterministic-append regression, a persisted-branch-causality assertion, + a cascade-cancel idempotency test) + live e2e where a provider step is involved. | `harness-cp/src` + `harness-runtime/src` (+ `harness-is/src` if Route Y) + tests | Phase 7 impl against cleared spec |

**Design forks to file** (Class 1, at B1-spec-1 authoring): (a) the C-CP-25 deferral table names "C-CP-25.b or C-CP-26" — the contract-vs-section-number choice is a Class-1 spec-shape fork; (b) **branch-causality Route X vs Route Y** (§2.4 — recommend Y); (c) **effectful-cancellation C10 fork** (§5 commitment 5) — compensation/saga semantics vs restricting `cascade-cancel` to pre-dispatch boundaries (gate high-blast-radius effectful steps *before* dispatch, where cancellation is clean); a dyadic C1⊥C10 council convening is warranted here (the one genuinely-contested design surface this doc carries open). These resolve at spec authoring, not here. No *defect* fork is owed — D1 confirms no spec contradiction; the IS sidecar is a precedented D-derivative *extension*, not a contradiction.

**Q1 cite-hygiene fold-in (not a build step):** tag the new strategy carriers with their C-CP-25.b/26 cites; no stale-cite created by this arc.

---

## §9 Nameable tensions + disposition (§10.9)

| Tension | Voices | Disposition |
|---|---|---|
| Parallel fan-out ⊥ hash-chained linear ledger | C1 orchestration ⊥ C2/C3 IS-integrity | **Surfaced + probe-resolved** (§2). The probe at ADR-F2 + `state_ledger_entry_schema.py`/`state_ledger_write.py` resolved it: serialized-append is ADR-F2's own prescribed single-threaded-write boundary → zero six-field/hash-chain/ADR-F2-§Decision change. **Codex correction (§9 below):** branch causality is not free-on-existing-fields — it needs Route X (zero-schema action_id encoding) or Route Y (bounded D-derivative sidecar, recommended); the heaviest-route (DAG / ADR-F2 §Decision) is still avoided. Per §10.9 amendment 5, no council convening needed — the primary source decided. |
| Cascade-cancel blast radius | C1 orchestration ⊥ C10 action-safety | **Audit/idempotency half resolved** (§5/D3) — persisted cancellation marker + branch-scoped idempotency + resume-terminality, determinate from the No-silent-failure + idempotency invariants. **The effectful-cancellation half is an OPEN C10 fork for B1-spec-1** (§5 commitment 5): `TaskGroup` cancellation can't roll back an already-dispatched effectful step; the production answer is cancel-before-dispatch / dry-run-then-approve (corpus), and compensation-vs-pre-dispatch-gating is a genuine design fork. Per CLAUDE.md §13.4, claiming the *whole* C10 tension "resolved" by advisor-only would be the named failure mode — so the effectful half is honestly carried open, and B1-spec-1 should convene a dyadic C1⊥C10 (or name the voices) on it. |
| Role degeneracy (hollow workers) | C1 orchestration ⊥ C4/B4 dispatch | **Resolved** (§4/D2): fold the role-threading seam into B1. Sequencing alternative surfaced to operator (§10). |
| Cross-agent comm ⊥ CP-AL-1 | — (invariant, not a tension) | **Hard boundary** (§6): hand-rolled asyncio, not H_E `Agent`. |

Per §13.2, the decorrelated review for this mode-agnostic design doc is **advisor (transcript-aware) + out-of-family Codex**; the adversarial reviewer fires at B1-spec-1 (the first design-substrate amendment), per the pre-merge-gate posture. Advisor was consulted pre-substantive (it produced the §2 reframe, the §2.3 authority-level check, the §4 role-seam pin, and the "keep per-pattern short" discipline). **Out-of-family Codex caught two load-bearing corrections** (`[[hooks-codex-pilots-decorrelation-validated]]`): (1) **§2.4** — the original draft claimed branch causality was already carried by existing persisted fields; Codex flagged that `parent_action_id`/`parent_entry_hash` are driver-transient `StepExecutionContext` fields and the persisted `EntryPayload` is `extra="forbid"` — corrected to the Route X / Route Y choice (heaviest-route safety conclusion held; the "zero IS work at all" over-claim did not). (2) **§2.1 D1.b** — the deterministic-append claim is false against the *current* driver, which appends inline per-step (completion-ordered under the writer lock); the design now requires an explicit buffered/deferred-append branch path so D1's byte-identical-hash-chain guarantee is *made true*, not merely asserted. (3) **§5 commitments 2–4** — `fail_class=cascade_cancelled` is a `RunResult` field not a persisted entry field (cancellation needs a persisted `terminal_status` marker, folded into the Route-Y sidecar), and step idempotency `sha256(run_idempotency_key, step_index)` dedups same-step-index branches into one entry unless `branch_path` enters the idempotency-key composition. (4) **§3** internal-contradiction (the §3 summary still said strategies "reuse the per-step ledger append" — reworded to entry-construction-reuse with inline-append excluded for non-linear strategies). (5) **§2.4 Route X / D3 consistency** — the persisted `terminal_status` read path was implicit for the Route-X fallback; D3 now makes a machine-readable terminal_status a *hard* requirement (Route Y satisfies natively; Route X must also specify the encoding + resume parser). All verified by direct read before applying; the heaviest-route (DAG / ADR-F2 §Decision) safety conclusion held across all five rounds — every correction reduced to a CP-driver composition change or the precedented bounded Route-Y sidecar. The Codex pass **converged at round 5** on internal-consistency + the roadmap-tracking obligation (handled in this PR), with no remaining *design* defect — the residual decisions (Route X/Y, C-CP-25.b/26) are correctly B1-spec-1 forks, not holes.

---

## §10 Verification, confidence, and open operator input

**Confidence.** D1 core (no second `prior_event_hash`, no six-field-shape/hash-chain/ADR-F2-§Decision change, single-threaded serialized append): **HIGH** — direct reads of ADR-F2 §Decision/§Consequences + `state_ledger_entry_schema.py`/`state_ledger_write.py` + the per-pattern causality check; ADR-F2 explicitly prescribes the single-threaded-write boundary D1 uses. Branch-causality recording mechanism (D1.a, Route X vs Y): **MEDIUM-HIGH** — both routes verified against precedent (Route Y mirrors `procedural_tier_snapshot_ref` exactly; Route X has the §5 footer authorization but the v1.3 MAY/MUST discipline disfavors it); the choice is a B1-spec-1 fork, recommend Y. Per-pattern semantics: **HIGH** (corpus-grounded; mechanical). Role seam (D2): **HIGH** on the mechanism, with the B1↔B4 *sequencing* being the one operator-open lever. Cascade-cancel (D3): **HIGH** on the audit/idempotency half; the **effectful-cancellation blast radius is an open C10 fork** (§5 commitment 5) for B1-spec-1 — not a hole in this design, but honestly carried open rather than asserted resolved. Residual uncertainty: the C-CP-25.b-vs-C-CP-26 contract-shape choice + the Route X/Y choice (both deferred to B1-spec-1, as the deferral table frames the former).

**What's next:** open **B1-spec-1** — author the C-CP-25 extension contract (driver-strategy surface + 5 strategies + cascade_policy consumption + role seam + cancellation), with a clearance marker and the adversarial reviewer firing pre-merge.

**Open operator input (sequencing only — build-vs-defer is settled by the directive):**
- **B1↔B4:** confirm D2 (fold the role-threading mechanism into B1; B4's binding-catalog stays a follow-on) **or** re-order B4 before B1. *Default if silent: D2.*

---

*Filing footer — Artifact: `.harness/r-fs-1-b1-topology-orchestration-design-v1.md`; Arc: R-FS-1 #2 (B1) design; Posture: mode-agnostic; X-AL-3: trivially clean (zero `design-substrate/**` or `harness-*/src` edit). Decisions: D1 (no second prior_event_hash / no six-field-shape / no ADR-F2 §Decision change — single-threaded serialized append), D1.a (branch causality via bounded D-derivative sidecar, Route Y recommended; B1-spec-1 fork), D2 (fold role-seam into B1), D3 (cascade-cancel = TaskGroup + persisted terminal_status + branch-scoped idempotency; audit half resolved, effectful-cancellation = open C10 fork for B1-spec-1). Decorrelated review: advisor (pre-substantive: §2 reframe + §2.3 authority check + §4 role-seam + brevity discipline; pre-done: §5 effectful-cancellation C10 honesty + research-leg grounding + §7 replay-determinism tightening) + out-of-family Codex (caught the §2.4 driver-transient-vs-persisted correction — `[[hooks-codex-pilots-decorrelation-validated]]`). Spine: `.harness/beyond-mvp-capability-boundary-ledger.md` + `.harness/r-fs-1-arc-1-scoping-v1.md`. Directive: `[[feedback-full-spec-beyond-mvp-nothing-deferred]]`.*
