# Class 2 Fork — B-48: sync sub-agent dispatch executes on the event loop (U-RT-60 direct-call revision)

**Filed:** 2026-07-18 · autonomous-loop fork-first leg (after the B-51/B-52/B-54 filing, PR #1046).
**Hybrid classification (sharpened at filing codex round-8): the executor SELECTION is Class 2** (an
in-execution operator decision between substantive designs, revising a ratified reading) — **but options B
and C each carry Class 1 back-flow RIDERS** (§5: the C-RT-03 `RuntimeConfig` cap field and the C-IS-07
drain-timestamp write-contract change are committed-contract amendments per §4.3); the riders halt for the
same operator response and the spec-writer apply pass, exactly like the B-51/B-52/B-54 arc's riders.
**Status: FILED — awaiting operator selection.** No `design-substrate/**` file is
edited by this filing; B-48 flips to `design_substrate_gated` with this filing (round-9 P1 — a filed back-flow awaiting ratification is exactly that status; `registered_finding` would signal buildable-after-grounding and could route implementation before ratification). Surfaced by
out-of-family Codex round-2 P1 on B-47 PR B2a (#1036); register row `B-48`.

## §1 The defect

`RuntimeHITLGateComposer._dispatch_inner` (`harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py`,
`async def _dispatch_inner` — the sole inner-invocation site) calls `self.inner.dispatch(...)` DIRECTLY and
awaits only if the result is awaitable. For the async C-RT-15 LLM inner that is correct. For the **sync
C-RT-17 sub-agent dispatcher** (SUB_AGENT_BOUNDARY row of the §14.8.1 wrap-asymmetry table) the entire
dispatch — child workflow execution (seconds-long), its F2/ledger writes, and the B2a-threaded KMS signing
network calls — **runs synchronously ON the event loop**, blocking every concurrent workflow, the daemon
keep-alive, and all pending timers for the full child-workflow duration.

**Companion defect record superseded-for-routing (filing codex round-4 P2).** The same architectural
surface carries the OPEN loop-bridge deadlock record
`.harness/runtime_defect_sub_agent_inference_child_loop_bridge_deadlock.md` (a `SUB_AGENT_DISPATCH` worker
dispatching an INFERENCE child deadlocks the sync/async bridge — the direct call occupies the loop the
child's facade needs). That record classified the issue as an implementation defect with no fork required;
this filing is now the ROUTING AUTHORITY for the fix (the offload is the resolution for both the blocking
and the deadlock face), and the record's xfail anchor
(`test_u_cp_89_hierarchical_delegation_depth2_live_ollama`, strict=False → flips XPASS on fix) is carried
into §4 as an acceptance signal; the record is annotated rather than deleted (history preserved).

This is the **Q3-ratified direct-call reading** of the U-RT-60 wrap-asymmetry fork
(`.harness/class_1_tension_u_rt_60_wrap_asymmetry_sync_async_mismatch.md` §7.2 Q3, "RATIFIED implicitly with
Q1"; the composer docstring cites it). The blocking behavior is therefore NOT an implementation bug against
the ratified state — child workflows already ran on the loop through this path at ratification time; the B2a
audit-signing threading only ADDED KMS network latency to an already-blocking ratified surface. Changing it
is a **revision of a ratified reading** → this Class 2 filing, per the register's own routing (a plain patch
was explicitly NOT taken at B2a).

## §2 Why a naive offload deadlocks (the design constraint)

Wrapping the sync inner in an executor is not free:

- **Recursion re-entry.** A child workflow dispatched by the sync C-RT-17 inner re-enters the sync driver,
  whose facade bridges back onto the event loop; a `SUB_AGENT_DISPATCH` step inside the child dispatches a
  grandchild through the SAME offload path. Under a BOUNDED pool, `depth+1` concurrent dispatch chains can
  occupy every worker with parents blocked waiting on children that need a worker — classic recursive-offload
  deadlock.
- **The two existing pools are ineligible** (register close_out): the 4-worker audit-offload executor
  (deadlock-prone under recursion AND would couple sub-agent latency to audit throughput) and the loop's
  default `ThreadPoolExecutor` (bounded at `min(32, cpu+4)`; shared with `asyncio.to_thread` users and the
  daemon — exhaustion under recursion/daemon concurrency).

## §3 Options (the Class 2 selection)

| # | Executor design | Assessment |
|---|---|---|
| A | Keep the direct call (status quo) | Rejected — seconds-long loop stalls at every sub-agent gate, now plus KMS latency; single-workflow deployments mask it, MTC/daemon deployments do not |
| B | **Custom grow-on-demand dispatch executor with a CONFIGURABLE hard cap + fail-fast** — a thread is created when no free worker exists (idle workers reused), threads named; a RuntimeConfig ceiling (generous default) is a SAFETY VALVE: at the cap, dispatch fails FAST with a typed error — never queues (queueing re-creates the recursive deadlock). Lifecycle defined on its OWN terms (round-2 P2 — the B2a audit executor is NOT a join-on-shutdown precedent: `_DaemonThreadAuditExecutor` deliberately runs daemon workers with no shutdown API, and `run_audit_off_loop` joins per-job on cancellation only): daemon worker threads + bounded per-DISPATCH join on cancellation (the `run_audit_off_loop` per-job-join shape), and a drain-with-deadline at shutdown that must NOT block on workers currently bridged into the event loop | **RECOMMENDED** — deadlock-free under arbitrary `SUB_AGENT_DISPATCH` recursion below the cap, resource-exhaustion-bounded above it, loud at the boundary. Grounding (rounds 1/15/17, final): C-CP-25 §25.11's `HIERARCHICAL_DELEGATION` "with depth" phrase and the plan's "depth bound" define NO value and NO carrier (`sub_agent_descent` is a BOOLEAN; `compose_child_workflow_runner` explicitly permits unbounded recursive re-entry) — only the per-parent fan-out cap 3 is materialized. **The executor cap is therefore the ONLY effective recursion-capacity bound**, and the UNMATERIALIZED delegation depth bound is itself a CP contract/implementation gap registered in the §5 CP rider. Stock `ThreadPoolExecutor` has NO unbounded mode (`max_workers=None` = bounded default) — the executor must be custom |
| C | Depth-aware bounded executor (per-depth accounting; beyond-budget dispatch must FAIL FAST or draw on RESERVED per-depth capacity — round-2 P1: QUEUEING is disallowed in any variant, since a queued descendant whose parents hold every worker is exactly the §2 deadlock) | Heavier machinery for the same fail-fast boundary; per-depth accounting only pays off if a depth-shaped policy (deeper = scarcer) is actually wanted — the flat cap of B is simpler and equally loud |

**Council note (register: conditional — C1 orchestration ⊥ C9 reliability) — condition MET.** The filing's
first draft claimed a sufficient bound already existed; rounds 1/15/17 settled the honest picture: the
spec's delegation "depth bound" phrase is UNMATERIALIZED (no value, no carrier — a CP gap the §5 rider
registers), so the executor cap is the only effective recursion-capacity bound anywhere. A genuine
recursion-capacity question therefore EXISTS —
whose authority is the cap, what default, fail-fast semantics at the boundary. Per §13.4 the voices'
positions precede the operator decision (round-2 P2), so both are named HERE:

- **C1 (orchestration):** the cap must never silently starve legitimate descent below its ceiling; a cap
  breach must surface as a TYPED orchestration error the driver/topology machinery can attribute to the
  dispatch step (not a generic executor error), so the workflow fails at the step that overflowed, with
  the descent chain in the message.
- **C9 (reliability):** the host needs a hard ceiling with a conservative-but-generous default; a breach
  is a misconfigured workload or runaway recursion and must be LOUD and immediate — no queueing, no
  best-effort degradation; the ceiling belongs in RuntimeConfig where operators already own capacity.

The positions AGREE on fail-fast + typed error + RuntimeConfig ownership and differ only on default sizing.
**That one disagreement is settled HERE, not deferred (round-9 P1 — the default is part of the C-RT-03
contract the operator ratifies, so leaving it to the apply leg would make the spec-writer invent it without
authority): recommended default `sub_agent_dispatch_max_workers = 256`, sized in SHARED-BUDGET FRAMES
under the §4 two-layer accounting (rounds 12/17/18 — each parent worker stays BLOCKED while its
descendants run, and each active branch reserves TWO frames, one upstream CP + one inner dispatch: a
legitimate all-sync 3-wide × depth-4 hierarchy holds 3+9+27+81 = 120 active branches = 240 frames
under the N+S accounting (every branch sync ⇒ S = N); 128 would
fail-fast the very topology used to size it).** 256 accommodates that shape with headroom; deeper/wider
topologies size the field to their own frame arithmetic (the config exists precisely because legitimate
workloads vary), validated ≥ 1 at config load. The dyad's convening at the apply leg is thereby reduced to
CONFIRMING this pre-resolved position (or surfacing a reasoned deviation back to the operator), not
inventing the number.

## §4 Verification obligations (the apply arc's acceptance criteria)

1. **Construction-time dispatch-mode selection** (round-5 P2): `_dispatch_inner` today discovers
   sync-vs-async only AFTER `self.inner.dispatch(...)` returns — too late to offload a sync child, while
   moving EVERY invocation into a worker would break the documented Future/custom-awaitable support
   (shapes that may need the loop at creation). The apply arc adds an explicit construction-time
   mode/adapter (the composer knows its inner's wrap-asymmetry row when built at stage 5): sync inners
   are submitted to the executor, async inners keep the direct await path — witnessed for ALL THREE
   stage-5 composer constructions (round-6 P2): `hitl_inference` (async C-RT-15), `hitl_sub_agent` (sync
   C-RT-17 — the offloaded one), and `hitl_tool` (async `RetryBreakerToolDispatcher.dispatch`, which must
   stay on the direct await path).
2. **Dispatch-time cancellation semantics** (round-1 P1; policy completed at rounds 11/12): cancelling an
   executor FUTURE cannot stop a sync child already running in its worker. The policy has THREE mandatory
   parts (round-12 P1 — a bounded join alone cannot satisfy no-late-effects when the child is stuck in a
   provider/KMS call): (a) a cooperative CANCEL TOKEN the child driver checks at every step boundary;
   (b) an EFFECT FENCE the token trips — once tripped, the child driver performs no further F2/audit
   writes (in-flight step results are discarded at the fence, mirroring the at-most-once effect
   discipline); (c) a bounded JOIN to the fence acknowledgement before surfacing
   `StepDispatchTimeoutError` — and the token CASCADES through recursive dispatch (round-16 P1): a
   timed-out child blocked inside a nested `SUB_AGENT_DISPATCH` cannot reach its next token check while
   the grandchild runs as a SEPARATE executor job, so descendant jobs inherit/link the ancestor's cancel
   token and tripping it fences the whole descent chain; witnessed with a parent→child→grandchild
   cancellation chain. If the grace expires with the worker still inside a blocking call, the
   surfaced error carries an explicit `worker_draining_under_fence` disposition (never silent
   abandonment, never a pretended completion) and the fence guarantees the still-running call's result
   cannot produce post-failure effects. **The fence covers the ENTIRE offloaded job (round-13 P1), not
   only child-driver step boundaries: `RuntimeSubAgentDispatcher.dispatch` itself persists audit entries
   AFTER the child returns — on SUCCESS/DRAINED, and from its exception/FAILED/PAUSED paths — so a
   tripped fence must also suppress those post-child `_compose_and_persist_audit` writes (or the writers
   are wrapped job-wide), else entries land after `StepDispatchTimeoutError` despite the guarantee.**
   **Guarantee stated honestly (round-14 P1): the fence stops every operation NOT YET STARTED — it cannot
   abort a synchronous append or external call the worker is already inside, which may complete after the
   error surfaces. The `worker_draining_under_fence` disposition therefore means
   AMBIGUOUS-EFFECTS / PERMANENTLY TERMINAL for that dispatch (round-19 P1 — "non-retryable until drained"
   is unenforceable as prose: the driver reduces `StepDispatchTimeoutError` to a fail-class string, so
   nothing today stops a caller rerunning while the abandoned worker completes an in-flight effect; a
   TERMINAL disposition needs no new retry-gate carrier — the step fails permanently, and re-running the
   WORKFLOW after drain is an operator action informed by the drain report; the alternative, a
   CP/runtime retry gate keyed to the dispatch, is heavier machinery the apply arc may propose only via
   the CP rider).** Witness: no NEW child effects begin after
   the failure surfaces, and a drained-under-fence step is terminal (not retried by any automatic path).
3. **Child-workflow facade bridging** — the sync driver's loop-bridge (`run_coroutine_threadsafe` shape)
   must be exercised from a WORKER thread with the parent awaiting off-loop; witness the full
   parent→child→grandchild chain.
4. **Pause/resume** — the witness must exercise the REAL cross-executor carrier (round-7 P2): a child's
   nested durable-HITL gate pausing surfaces from the sync `RuntimeSubAgentDispatcher` as
   `SubAgentChildPausedError` carrying the child's pause SNAPSHOT — witness THAT error and its snapshot
   crossing the executor future into the parent's fan-out pause handling intact (a synthetic
   `HITLPauseRequestedSignal` or worker-set flag exercises a path production never takes and can miss
   snapshot loss). Durable-async pause flags set from the worker thread must be visible to the resume
   path (no thread-local state).
5. **OTel span context — and SELECTIVE contextvar carry** (round-10 P1×2): `contextvars` do NOT flow into
   pool threads automatically, so the offload carries `contextvars.copy_context()` for trace continuity
   (witness a parent-child span-id assertion) — but a WHOLESALE copy smuggles loop-affine state across
   threads: (a) `INTER_STEP_CHANNEL_VAR` — the copied parent channel is shared by concurrent sibling
   children (`compose_child_workflow_runner` binds no fresh channel), letting one child's step output
   enter another child's payload via `most_recent_output()`; the apply arc binds a PER-CHILD channel and
   witnesses sibling isolation; (b) `_BRANCH_INFLIGHT_DISPATCHES` — a child fan-out would register
   Futures owned by its worker-thread loop into the PARENT registry while the parent's cascade-cancel
   watchdog cancels them from another thread (not thread-safe; RuntimeError under asyncio debug, outer
   hard deadline can fail); the apply arc gives the registry a cross-thread-safe cancellation handle (or
   binds a fresh registry per child with parent-side aggregation) and witnesses a NESTED cascade-deadline
   cancel through an offloaded child. **And the parent-side abandonment path (round-12 P1):
   `_run_fanout_to_completion` cancels the `asyncio.to_thread` future on barrier deadline and abandons
   the thread via `shutdown(wait=False)` — nothing today carries that cancellation INTO the offloaded
   job, so the parent can report failure while the child keeps writing until its own step timeout. The
   apply arc wires an explicit parent→job cancellation channel (the same item-2 cancel token, tripped by
   the barrier deadline) and witnesses a parent-barrier-deadline cancel reaching the child's fence.**
6. **B-21 fan-out** — `PARALLELIZATION` branches dispatching sub-agents concurrently must not serialize on
   the offload — N branches (S of them sync sub-agent) run fully concurrent **when occupied + N + S ≤ cap (round-21
   P1 — stated in the same units as the shared-budget rule below; the earlier N ≤ cap phrasing admitted
   fan-outs the budget rejects); beyond that the next dispatch fail-fasts per the §3 no-queue invariant
   (round-11 P2 — full concurrency and the hard cap cannot both hold unqualified). And the cap must gate BOTH executor layers (round-13 P1):
   `_run_fanout_to_completion` creates `ThreadPoolExecutor(max_workers=len(branch_plan))` and enters
   `asyncio.to_thread` per branch BEFORE any dispatch reaches the capped executor — an unbounded manifest
   would spawn N upstream CP threads before the excess fail-fasts, defeating the host ceiling; the apply
   arc brings the upstream fan-out thread creation under the same capacity authority, with the
   ACCOUNTING MODEL defined (rounds 17/19): ONE shared frame budget covers BOTH layers, charged by what
   a branch actually uses — every active branch reserves an upstream CP frame, and ONLY sync/offloaded
   `SUB_AGENT_DISPATCH` branches reserve the additional inner-dispatch frame (async INFERENCE/TOOL
   inners stay on direct await and consume no inner worker — charging them would reject unrelated async
   work despite free executor capacity, round-19 P2). Reservation is ATOMIC per branch
   (all-frames-or-fail-fast, preventing partial-acquisition exhaustion); the guarantee: a fan-out of N
   branches with S sync sub-agent branches runs fully concurrent when occupied + N + S ≤ cap (round-22
   P2 — the budget is SHARED, so ancestors and concurrent workflows already holding frames count;
   admission is against AVAILABLE capacity, never the local fan-out alone), fail-fast beyond, witnessed
   at the boundary, past it, and under CONTENTION (a second workflow holding frames)** — and must keep
   the v1.97 paused-child-branch resume semantics; witness with a 2-branch fan-out. **Including pause-state ISOLATION (filing codex round-4
   P1): child runners share the parent `HarnessContext`, so one child's nested durable-HITL gate setting
   `ctx.pause_requested_flag` would be captured by a SIBLING branch with no gate (a false pause) once
   branches run genuinely parallel — the apply arc requires per-child/per-run pause state and a witness
   proving only the branch that raised the signal is recorded paused. Resume state equally (round-5 P1):
   stage 5 hands the SAME `ctx.resume_context_holder` to every HITL composer and `dispatch()` does an
   unkeyed `consume_and_clear()` with no cross-task atomicity — a re-dispatched sibling could consume an
   APPROVE/EDIT/REJECT intended for the paused child. Per-child/per-run resume-context isolation + a
   targeted concurrent-resume witness are required alongside the pause-flag isolation. This is exactly
   `B-39`'s still-gated CP design question (round-14 P1 — the branch-unique one-shot response threading
   through CP's `ResumeContext`/driver is UNDESIGNED per that register row): **B-39 is an explicit
   DEPENDENCY of this apply arc's fan-out-resume half, carrying its own CP spec/plan back-flow — B-48
   does not absorb that CP decision under Runtime authority.** Until B-39 resolves, concurrent siblings
   with durable-HITL gates remain restricted (the pre-offload serialization masked this; the apply arc
   may sequence gated siblings as an interim documented constraint).**
7. **Timestamp-ordering interaction** — the B2a append-lock discipline covers the audit append path, but
   NOT the branch-drain path (filing codex round-4 P1): `drain_branch_buffers` samples `drain_timestamp`
   BEFORE the IS `_WRITE_LOCK`, so two fan-out children draining concurrently can append in inverted
   order and raise `NonMonotonicTimestampError` — pinned by the strict xfail
   `test_concurrent_sibling_drains_invert_timestamp`, whose fix (writer-owned timestamp sampling inside
   the lock) is assigned to THIS arc. The apply arc lands that fix and REMOVES the xfail; B-48 cannot
   close over an accepted-failing concurrency witness. Then re-run the existing concurrency witnesses
   plus the r100 e2e.
8. **Loop-bridge deadlock resolution signal** — the superseded defect record's live anchor
   `test_u_cp_89_hierarchical_delegation_depth2_live_ollama` (xfail strict=False) must flip XPASS under
   the offload (a sub-agent INFERENCE child's facade bridge finds the loop free); promote it from xfail
   on flip.
8-bis. **Loop-responsiveness witness — the PRIMARY defect's own proof** (round-20 P2): with a slow sync
   child (or a stubbed slow KMS call) running through the offload, an UNRELATED concurrent workflow and a
   pending loop timer must demonstrably advance during the dispatch (the §1 defect is exactly their
   starvation); mutation probe: revert to the direct call → this witness must fail. The deadlock XPASS
   and capacity tests do not cover this — they prove bridge progress and admission, not loop liveness.
9. **Cap saturation + no-queue witness** (round-9 P2): a deterministic cap+1 scenario — every worker
   occupied, one more dispatch — must fail IMMEDIATELY with the typed error and provably enqueue nothing
   (the below-capacity witnesses pass even on a queueing bounded pool, leaving the target deadlock
   untested); plus shutdown drain-with-deadline coverage. The queue-vs-fail-fast branch is
   mutation-probed (swap fail-fast for enqueue → the saturation witness must hang/fail).
10. All new witnesses PD-8 mutation-probed (revert the offload → the loop-blocking witness must fail; drop
   the context-copy → the span witness must fail; etc.).

## §5 Spec surface

The §14.8.1 wrap-asymmetry table (Runtime spec, committed lineage) describes the sync/async inner shapes;
the Q3 reading lives in the ratified fork doc, and the composer's execution VENUE (on-loop vs offloaded) is
not pinned by any grep-verified spec sentence. But the Runtime spec delta is **UNCONDITIONAL for options B
and C regardless** (filing codex round-3 P1): the capacity cap is a NEW `RuntimeConfig` field, and
`RuntimeConfig` is the C-RT-03 contract — adding any field to it is an H_T design extension requiring
Class 1 spec back-flow (X-AL-3); landing it without the spec amendment would silently create an
undocumented configuration contract. The apply arc therefore carries: (a) this fork doc's resolution note,
(b) a Runtime spec delta amending C-RT-03 (the cap field + its typed fail-fast error) plus any §14.8.x
venue sentence found at apply time against the then-current head, and (c) a Runtime plan delta for the new
executor's acceptance criteria (the plan currently has none — same round-12 discipline as the B-51 filing),
and (d) an **IS spec + plan back-flow for the §4-item-7 drain-timestamp fix (round-5 P2)**: moving
timestamp authority inside the IS writer lock is a C-IS-07 write-contract change — the superseded defect
record's own §8.3 identifies it as such — so landing it under Runtime deltas alone would silently change
caller-supplied ledger timestamp semantics without the authoritative IS contract moving. And (f) a **CP spec/plan rider for the fan-out cap gating (round-15 P1)**: bringing
`_run_fanout_to_completion`'s branch-plan execution under the capacity authority changes CP-owned
concurrency/cardinality semantics (C-CP-25 §25.11) from unconditional concurrent execution to a typed
fail-fast outcome above the cap — that half rides an explicit CP amendment, never Runtime authority alone;
**the same rider resolves the UNMATERIALIZED §25.11 delegation depth bound (rounds 17/18 — "with depth"
names no value and no carrier; `compose_child_workflow_runner` permits unbounded re-entry) with the
policy DECIDED in this filing, not left to the apply pass: FORMALLY DELEGATE recursion capacity to the
executor cap (the rider retires the unmaterialized phrase in favor of the single capacity authority —
materializing a second, separate depth bound would recreate the two-authorities smell the filing rejects
at option C). The alternative (materialize a CP depth bound) is exposed at §6 for the operator to
override.**
And (e) **Runtime
riders for the §4 semantic changes themselves (round-9 P1)**: per-child pause/resume carrier isolation and
the dispatch-time cancellation/join/effect-fence policy alter committed Runtime surfaces (C-RT-04
resume-context plumbing, C-RT-17 dispatch semantics, the §14.8.8/§14.8.9 pause lineage, and
`RT-FAIL-STEP-DISPATCH-TIMEOUT`'s meaning under an abandoned worker) — those amendments ride the same
Runtime spec + plan deltas explicitly, never implementation-only authority.
This makes the selection's spec footprint identical in kind to the B-51/B-52/B-54 arc's Runtime rider — the
apply passes can share one Runtime version bump if the operator answers both gates together.

## §6 The operator selection (ONE decision)

Select the executor design: **B (custom grow-on-demand executor + configurable hard cap + fail-fast at the
cap — recommended)** vs C (depth-aware bounded pool) vs A (keep the ratified blocking direct-call). Under B or C
(round-22 P2 — the riders are meaningless under A), the selection carries the filing-settled riders:
default 256 shared-budget frames; recursion capacity FORMALLY DELEGATED to the executor cap (the §25.11
unmaterialized depth phrase retires — override available: direct the CP rider to materialize a separate
depth bound instead). Under A the filing stands as a REJECTED-fix record: no riders, the defect record's
OPEN status is restored as the routing authority, and the loop-blocking + deadlock defects remain accepted
operating posture (recorded explicitly, not silently). The
C1/C9 council dyad convenes at the apply leg under B or C (the cap is a genuinely new capacity authority);
the apply arc also defines the §4-item-2 cancellation semantics before any offload lands. May be answered
in the same batch as the B-51/B-52/B-54 ratification gate (PR #1046).
