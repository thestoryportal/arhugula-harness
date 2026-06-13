# C1 — Orchestration & Control Architect — `cascade-cancel` semantic fork

**Voice:** C1 (Orchestration & Control). **Fork:** R-FS-1 arc B1-spec-1 — the correct, complete semantic for `cascade-cancel` under fan-out. **Posture:** deliberated blind to C10; orchestration lens; C10 tension named honestly per part 4. **Grounded at HEAD `5d4166c` by direct read** (file:line below).

---

## Co-primary scan (SKILL.md §"Activation discipline")

The topic engages **C10** (action-safety / blast-radius on effectful steps) and touches **C11** (HITL gate placement). Under normal single-voice routing this would route to the orchestrator. But this is an *explicit, structured* council convening that asks for the **C1 orchestration-lens position** on a named fork, deliberated blind to C10. So I do **not** recuse — I give the orchestration position and **name the C10 seam without absorbing it** (parts 2 + 4), which is exactly the FM-A/FM-C mitigation the SKILL.md prescribes: *say where the gate slot sits, not what it enforces.*

---

## 1. Decision — Fork **A**, decisively (not "both have merits")

> **C1 selects the pre-dispatch-boundary cascade semantic (Fork A): `cascade-cancel` cancels only not-yet-dispatched sibling steps at a control-flow boundary; in-flight effectful steps run to their own completion/timeout and are recorded with a persisted per-branch `terminal_status`; high-blast-radius effectful steps gate BEFORE dispatch (C10 substrate). NO net-new primitive.** Fork B (compensation/saga) is rejected.

**The load-bearing argument is that the harness already owns this exact primitive — the DRAIN protocol — and `cascade-cancel` is its fan-out generalization.**

The committed `SINGLE_THREADED_LINEAR` driver already implements "cancel at a boundary, record a persisted terminal status, never reach inside a step":

- Drain is a **pre-step-entry boundary check** — `if ctx.drained_flag.is_set(): return RunResult(status=DRAINED, terminal_step_index=step_index-1, ...)` at `harness-cp/src/harness_cp/workflow_driver.py:766-781`; spec contract at `design-substrate/Spec_Control_Plane_v1_6.md:344` ("Drain check (pre-step) … do NOT enter step … return `RunResult(status=DRAINED …)`").
- The drain protocol is explicitly a **4-site check with NO mid-step interruption** (spec change-note line 43: "drain protocol (4-site check pattern: driver entry + per-step pre-entry + per-step post-exit + **NO mid-step interruption**)").
- The DRAINED status is itself the precedent for *"terminal-status-observable replaces a rollback/lifecycle-event"* — `workflow_driver_types.py:49`: "`DRAINED` is the terminal-status observable that replaces a `DRAINED` lifecycle-event class which does not exist." There is no rollback in drain; there is a recorded terminal state at a boundary.

`cascade-cancel` is structurally identical, lifted from the linear case to the fan-out case: **a sibling failure trips a control-flow boundary; not-yet-dispatched siblings are cancelled at that boundary (`asyncio.TaskGroup` structured cancellation, B1 design §5 commitment 1); each branch reaches a persisted terminal state; nothing reaches inside an already-dispatched step.** That is the named canonical orchestration pattern (Google SRE "request-cancellation propagation + deadline-bounded barriers," B1 design §5 commitment 5 corpus grounding) — `cancel-before-dispatch`, not `rollback-after`.

So Fork A is **"compose committed substrate"** (the drain primitive + the bounded barrier + the Route-Y `terminal_status` sidecar + branch-scoped idempotency keys, all already designed at B1 §2.4/§5/§7). Fork A introduces **no new primitive**. Fork B introduces one — and per I-6 a hand-rolled saga is still net-new, foreclosed.

## 2. Is Fork A complete, or a hole? — **Complete. Rollback-of-sent-effects is out of the orchestrator's domain — and a saga can't deliver it either.**

This is the crux of the fork, and the answer is a **reframe of what "complete" means**, not a defer.

**Rollback of an already-sent effect is not a coherent orchestration operation.** Cancelling an `asyncio` task aborts the *Python coroutine*; it cannot un-write a file, un-send an email, or un-bill an `INFERENCE_STEP` (B1 design §5 commitment 5). The orchestrator's domain is *control flow over steps* (SKILL.md §"What C1 owns" — topology, hand-off, termination); the *effect already left the boundary* the moment the step was dispatched. There is no orchestration op that reaches past dispatch.

**Critically — Fork B does not achieve completeness either.** A saga's "compensation" is a **new forward action** (a *delete* call, a *refund* call, a *retraction* email), per-tool-defined — that is C4's tool-contract domain, not topology, and it **still cannot un-send the original**; it issues a second world-effect that approximates undo. So Fork B fails on three independent counts:

1. **I-6** — net-new primitive (hand-rolled saga is still a saga primitive); forbidden.
2. **Domain** — compensation is a per-tool forward action (C4), not a topology/control-flow semantic (C1). Adding it to `cascade-cancel` is silent absorption of C4's surface (FM-style boundary leak).
3. **It doesn't even reach completeness** — it cannot roll back the world; it can only issue more world-effects, which themselves can fail and need their own compensation (the recursion the production corpus warns against).

**The definition shift, stated plainly:**

> **Completeness for `cascade-cancel` = total persisted terminal-state coverage with no silent gap, NOT universal rollback.** Every branch reaches a *defined, persisted, machine-readable* terminal state; resume can discriminate every disposition; no branch reads as "never dispatched / still pending" when it was in fact cancelled or completed.

Under that (correct) definition, **Fork A is a COMPLETE honest semantic** — it satisfies the FULL-SPEC directive without deferral. The effectful side is not "carried open"; it is **assigned to its rightful owner (C10) by construction** (part 4). That distinction is the whole point: choosing A *is* the resolution.

## 3. What the spec MUST state about `cascade-cancel`'s reach (parts of D3 the contract encodes)

For the 3 barrier-bearing patterns (`PARALLELIZATION` / `ORCHESTRATOR_WORKERS` / `HIERARCHICAL_DELEGATION`; `DECENTRALIZED_HANDOFF` is single-owner-sequential so cancel is trivial; `EVALUATOR_OPTIMIZER` is sequential):

**(a) Reach — exactly what gets cancelled vs what runs to completion.** Two distinct branch dispositions when `cascade-cancel` fires, and the spec MUST name **both**:
   - **never-dispatched sibling step → `cancelled`** (clean `TaskGroup` cancellation; the world was never touched).
   - **in-flight effectful step → `ran-to-completion` OR `timed-out`** (it actually finished or hit its bound; it is **recorded, NOT cancelled** — cancellation cannot reach it). Its external side-effect stands, uncompensated, *by design* (part 2).
   - The failing branch itself → `failed`.

**(b) Ledger record — a persisted, machine-readable per-branch `terminal_status`.** Fold `terminal_status ∈ {cancelled, ran_to_completion, timed_out, failed, ...}` into the **Route-Y `branch_metadata` D-derivative sidecar** (B1 design §2.4 / §5 commitment 2 — `{parent_action_id, branch_index, terminal_status}`, the `procedural_tier_snapshot_ref` template; **zero six-field-shape change, zero hash-chain change, zero ADR-F2 §Decision change**). `fail_class=cascade_cancelled` is a `RunResult` field, **not** a persisted entry field (`workflow_driver_types.py`); without the sidecar marker a cancelled branch is indistinguishable from a pending one. A cancelled branch MUST NOT be a silent gap.

**(c) Run-level status mapping — keep the two levels separate (advisor-caught correction).** Run-level `RunStatus` (`workflow_driver_types.py:43-58`) is distinct from per-branch `terminal_status` (the sidecar):
   - `cascade-cancel` (a branch failed → fan-out aborted) → **run terminates `FAILED`** (`fail_class` populated; per-branch `cancelled`/`ran_to_completion` markers in the sidecar).
   - `proceed` (degraded partial aggregate, `degraded=true`, D3) → maps to **`PARTIAL`** (`workflow_driver_types.py:57`, "reserved for future multi-step error modes" — this is its slot, NOT cascade-cancel's). *Earlier in my own reasoning I crossed these — `PARTIAL` belongs to `proceed`'s degraded aggregate, not to cascade-cancel.*
   - `pause` → **`PAUSED`** (`workflow_driver_types.py:58`, existing U-RT-89 PauseResumeProtocol).

**(d) Composition with `pause` / `proceed`.** All three are `CascadePolicy` values (`topology_pattern.py:65-67`) selecting one branch-failure disposition at the barrier — a clean discriminated union over one decision point, not three control-flow forks (type-driven: variability in the policy *value*, not in *whether* code runs). `pause` = halt fan-out at the HITL/pause boundary, in-flight allowed to finish, then `PAUSED`; `proceed` = aggregator sees the partial set, `PARTIAL`+`degraded=true`; `cascade-cancel` = abort + `FAILED` + per-branch sidecar markers.

**(e) Composition with resume-idempotency.** Branch-scoped idempotency keys — `sha256(run_idempotency_key, step_index, branch_path)` (B1 design §5 commitment 3; CP-side driver key composition, no IS-schema change) — make resume exact AND prevent same-`step_index` branches collapsing into one entry. On `api.resume` after a cascade-cancel, the resumed run reads each branch's sidecar `terminal_status` by its branch-scoped key and **MUST NOT re-dispatch** any branch whose `terminal_status` is `cancelled`, `ran_to_completion`, `timed_out`, or `failed`. Re-dispatching a deliberately-cancelled branch — or re-dispatching a completed effectful step — is the correctness hazard A forecloses (corpus: "make every interrupt-resume path idempotent," cluster-4 §2.4.7). **This is why the per-branch `terminal_status` MUST be persisted and machine-readable, not string-parsed** — resume-idempotency depends on discriminating "deliberately cancelled" from "completed-then-fan-out-failed."

## 4. Where my position creates tension with C10 — named honestly (SKILL.md §"Boundary voices acknowledged")

**The genuine C1 ⊥ C10 seam: A bounds the tension by placing the gate where cancellation is clean — it does not resolve gate-tiering policy, and it must not.**

- **C1 owns WHERE the gate slot sits; C10 owns WHAT it enforces.** Fork A's load-bearing composition is: a high-blast-radius effectful step gates **pre-dispatch** (compose with the committed sandbox 4-tier blast-radius + HITL 4-response palette), because pre-dispatch is the *only* boundary where cancellation is clean (post-dispatch, the effect is gone). C1 specifies the gate **slot location** (pre-dispatch boundary). C1 does **NOT** specify the **tiering policy** — which tiers gate, what the HITL palette enforces, what counts as "high-blast-radius." That is **C10's permanent domain, not deferred B1 scope.**
- **This is the honest line that keeps both directives satisfied at once:** choosing A *is* the complete orchestration resolution (FULL-SPEC: no defer). What "remains" for C10 is **not deferred work** — it is **C10's standing ownership by construction**. I am not parking the effectful half; I am correctly assigning the residual to the voice that owns it. (Per CLAUDE.md §13.4, claiming the *whole* C10 tension "resolved" from the C1 lens alone would be the named failure mode — so I scope my close to the orchestration semantic and hand C10 its domain intact.)
- **Two boundary guards I must NOT absorb (FM-B / T-perm-3):**
   - **Barrier-deadline (C1) ≠ step-timeout (C9).** "In-flight effectful step runs to its own completion/timeout" — the **barrier** deadline (bounded barrier, B1 design §3, so a stuck branch can't strand its parent) is C1's. The **step-level** timeout / retry posture is **C9** (T-perm-3, the permanent C1⊥C9 tension). I name the seam; I do not set retry mechanics.
   - The C10 fork B1-spec-1 must still convene (a dyadic C1⊥C10) to settle **which tiers gate pre-dispatch** — but that is gate *policy*, which A's structure makes *answerable* (the slot exists, pre-dispatch) rather than leaving the architecture undecided.

---

## Standing pre-check obligations (SKILL.md §"Cross-cutting concern obligations")

- **Reliability & failure containment (C9).** Failure surface: a branch raises → `TaskGroup` cancels not-yet-dispatched siblings; in-flight effectful steps complete/timeout (recorded). Topology-level recovery affordance: `proceed` = graceful-degradation partial aggregate (`degraded=true`) over a retry-storm (corpus, Google SRE). Seam to C9: barrier-deadline is C1; per-step timeout/retry is C9 (T-perm-3).
- **Token economy & cost (C2/C4/C6).** Fan-out is ~4× single-stream cost (research §2.7); `cascade-cancel` *reduces* wasted spend by aborting not-yet-dispatched siblings on first failure — but an in-flight billed `INFERENCE_STEP` still bills (it ran to completion). Cost-optimization is C2/C4/C6; C1 surfaces the implication.
- **Observability hooks (C7).** New instrumentation points: each barrier = a fan-in span boundary; each cancelled branch = a distinct terminal trace event carrying the sidecar `terminal_status`. C7 specifies the span schema; C1 surfaces that the points exist.

## Self-audit (SKILL.md §9.2)
1. **Named canonical pattern** ✓ — drain-protocol generalization + Google SRE cancel-before-dispatch / deadline-bounded barriers (corpus, B1 §5). 2. **Termination** ✓ — every branch reaches a persisted terminal state; barrier is deadline-bounded. 3. **Hand-off contract** ✓ — branch results via state-ledger sidecar + branch-scoped idempotency key. 4. **HITL placement** ✓ — pre-dispatch gate slot for high-blast-radius effectful steps (placement only; C11/C10 own the primitive/policy). 5. **Boundary voices acknowledged** ✓ — C10 (gate policy), C9 (step timeout/T-perm-3), C4 (compensation-as-forward-action), C11 (HITL primitive) all named, none absorbed. 6. **Sources cited** ✓ — file:line throughout.

---

**C1 position in one line:** Fork **A** — `cascade-cancel` = `TaskGroup` cancellation of not-yet-dispatched siblings at a control-flow boundary + in-flight effectful steps run to completion/timeout and are recorded + persisted per-branch `terminal_status` (Route-Y sidecar) + branch-scoped idempotency keys + pre-dispatch gate-slot for high-blast-radius effectful steps; run-level `FAILED`. It is the fan-out generalization of the committed drain primitive, introduces **no new primitive**, and is a **complete** semantic because completeness = total persisted terminal-state coverage, not universal rollback — which is out of the orchestrator's domain and which a saga (Fork B) cannot deliver anyway.
