# C10 — Action Safety & Blast Radius — contribution

**Fork:** R-FS-1 arc B1-spec-1 — the correct, complete semantic for `cascade-cancel` when a branch fails and siblings must be cancelled, *given that some sibling steps may have already hit the world*.

**Voice:** C10 (Action-Safety / Blast-Radius). Deliberated blind to C1. Grounded by direct read at HEAD `5d4166c`.

---

## VERDICT

**Fork (A) — restrict `cascade-cancel` to the pre-dispatch boundary + gate high-blast-radius effectful steps BEFORE dispatch + record in-flight completions with a discriminating persisted `terminal_status`. NO new primitive.**

This is not a "both have merits" call and it is not a deferral. **(A) is the *complete* action-safety semantic** — it leaves no silent-uncompensated-effect hole for the only blast-radius class where uncompensated effects are genuinely dangerous. **(B) compensation/saga is the wrong primitive on the merits** (not merely I-6-forbidden): you cannot contain an irreversible effect by promising to roll it back. You contain it by gating *before* it fires — which the committed design already does. From the action-safety lens, (B) is a category error dressed as completeness.

---

## 1. Is (A) acceptable from a blast-radius standpoint? — YES, and it is *complete*, not partial.

The discriminating question C10 always asks: **of the steps a `cascade-cancel` might race against, which class can leave an uncompensated side effect that actually matters?** Walk the committed four-tier blast-radius taxonomy (`harness-as/src/harness_as/sandbox_tier.py:45-51`, AS spec §2.4):

| Blast-radius tier | If in-flight at cancel | C10 disposition |
|---|---|---|
| `read-only` | No mutation. | Cancel freely; nothing to compensate. |
| `local-mutation` | In-sandbox FS/process/state. | Bounded to the sandbox; reversible via C3 rollback (`write-bounded-reversible` posture). Record it. |
| `external-reversible` | External write with a rollback API. | Record it; resume/operator can roll back via the documented API. Not silent. |
| `external-irreversible` | **email send / payment / computer-use** — the genuinely dangerous class. | **Already foreclosed from silent dispatch** — see below. |

The load-bearing finding: **`external-irreversible` cannot reach silent dispatch under the committed gate.** `BlastRadiusTier.EXTERNAL_IRREVERSIBLE → SandboxTier.TIER_4_FULL_VM` (`harness-as/src/harness_as/blast_radius_floor.py:30`; AS spec §2.4) feeds the multiplicative `gate_level` `max()` rule (`harness-cp/src/harness_cp/gate_level_rule.py:48-60`, `GateLevel ∈ {AUTO, ASK, DENY}`, C-CP-19 §19.1) → resolves to `ASK` or `DENY` → mandatory HITL via the closed 4-response palette (`harness-cp/src/harness_cp/hitl_response_palette.py:33-51`, C-CP-16 §16.1).

So at the instant `cascade-cancel` fires, any irreversible-effect step is in exactly one of two states:

- **(a) not-yet-approved → not-yet-dispatched → cleanly cancellable.** The HITL gate held it at the dispatch boundary. `TaskGroup` cancellation of a coroutine parked on the approval await is clean — no effect hit the world.
- **(b) operator-approved-and-in-flight → the operator already accepted that exact blast radius.** A landed irreversible effect here is *not a silent uncompensated effect* — it is an effect the operator authorized through the palette. The audit records it; nothing was hidden.

**There is no third state where an irreversible effect silently lands behind the operator's back.** That is why (A) is *complete*: the dangerous class is fully contained by the committed pre-dispatch gate, with no deferred remainder. Fork (A) "prevents silent uncompensated side effects" — not by promising rollback, but by ensuring the only effects that can land are ones the operator gated through, and every cancelled/in-flight branch is recorded.

This is exactly C10's committed posture — **reactive containment with strong audit + a tight pre-dispatch HITL escalation surface for blast-radius outliers** (the maximal-action-surface discipline; SKILL §"maximal-action-surface posture" (a)/(c)/(d)). `cascade-cancel` does not need a new defense; it composes with the one C10 already owns.

---

## 2. Does the harness already have the primitives to make (A) safe? — YES. Is (B) needed for safety? — NO; it is out of cascade-cancel's coherent domain.

**Committed primitives that make (A) safe (cited, landed):**

1. **Four-tier blast-radius classification** — `harness-as/src/harness_as/sandbox_tier.py:45` (`BlastRadiusTier`), `blast_radius_floor.py:30` (the `EXTERNAL_IRREVERSIBLE → tier-4-full-vm` floor). The classification axis is C10's structural lever; it is what lets the gate fire *per blast radius* rather than uniformly.
2. **Multiplicative gate-level rule** — `harness-cp/src/harness_cp/gate_level_rule.py:48-60` (`GateLevel = {AUTO, ASK, DENY}`, `max()`-composed over `BLAST_RADIUS × PERSONA_TIER × per_tool_gate_level`), C-CP-19 §19.1. Deny-wins precedence; escalation-monotonic `AUTO < ASK < DENY`.
3. **Pre-dispatch gate evaluation** — `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py:8-12` (C-CP-17 §17.2): a tool call is evaluated against `_hitl_required` (U-CP-43) *before dispatch* (acceptance #7); if required, it is rewritten into an HITL-gated variant. **(Honesty flag — verification-shape: this is the committed *contract* and its carrier docstring; `cascade_policy` itself is "declared but unconsumed" per the design §1 grounding, so I assume the fan-out gate path is similarly under-wired. My claim is "the gate is a committed primitive that B1-spec-1 MUST compose into the fan-out path," NOT "every call is provably gated at HEAD today." `[[verification-shape-sharpened-grep-vs-e2e]]`.)**
4. **The 4-response HITL palette** — `harness-cp/src/harness_cp/hitl_response_palette.py:33-51` (`APPROVE / EDIT / REJECT / RESPOND`), C-CP-16 §16.1. **This is the committed realization of "dry-run-then-approve" for a high-blast-radius effectful step** — the operator sees the proposed action pre-dispatch and `EDIT`s or `REJECT`s it before any effect fires. (I do **not** cite a `dry_run`/`preview` primitive: a grep for `dry_run`/`preview` across `harness-as/src`, `harness-cp/src`, and the AS spec returned empty. Dry-run-then-approve is a corpus *pattern*; its committed form here is `_hitl_required`-ask + `EDIT`/`REJECT`. I will not assert a phantom primitive.)
5. **C3 rollback / single-threaded ledger writer (ADR-F2)** — covers the `local-mutation` / `external-reversible` recorded-and-recoverable path.

**Is a saga/compensation primitive (B) needed for safety?** No, and it is out of `cascade-cancel`'s coherent domain:

- For `external-irreversible` — the dangerous class — **compensation is impossible by definition** (you cannot un-send an email, un-charge a payment, un-type a computer-use keystroke). A saga that "rolls back" here would be a *lie in the audit trail*. Containment for this class is pre-dispatch gating, which is already committed. (B) adds nothing C10 would trust.
- For `external-reversible` — rollback already exists via the per-step rollback API (the tier's defining property); the audit record + resume path invoke it. No saga orchestrator needed.
- For `local-mutation` — C3 rollback already owns this.
- (B) is additionally an **X-AL-3 net-new H_T primitive** (hand-rolled saga is still net-new) requiring ADR back-flow, and **I-6 forbids the framework form**. But the decisive point is the *first* one: even if I-6 and X-AL-3 did not exist, (B) is the wrong tool, because the one class it would nominally serve cannot be compensated and the classes it could serve are already served.

**FULL-SPEC does not pull toward (B).** The irreversible hazard is *fully* contained by the committed gate — there is no deferred remainder for FULL-SPEC to demand we build. FULL-SPEC's "HOW stays committed" explicitly preserves the no-saga / hand-roll commitment. (A) resolves the open fork completely; it does not re-defer it.

---

## 3. EXACTLY what the spec MUST state (the C10 safety obligations for `cascade-cancel`)

Four obligations. They are what make D3 *implementable and honest* rather than asserted. B1-spec-1 MUST encode all four:

### Obligation 1 — `cascade-cancel` is bounded at the dispatch boundary (the semantic itself).
`cascade-cancel` cancels **not-yet-dispatched** sibling steps. An **already-dispatched** effectful step (a `TOOL_STEP` whose sandbox call hit the world, or a billed `INFERENCE_STEP`) runs to its **own completion or timeout** and is recorded with a persisted `terminal_status`. The spec MUST state explicitly: *"`cascade-cancel` is not an instantaneous total abort. It is best-effort cancellation at the pre-dispatch boundary; an in-flight effectful step is allowed to complete and is recorded, never silently dropped."* (Composes with the corpus production discipline: cancel-before-dispatch + RPC-deadline-bounded barriers, cluster-4 §2.2/§2.3.x.)

### Obligation 2 — fan-out introduces NO concurrency gate-bypass (the obligation the design will otherwise miss).
D1.b's buffered-append branch path defers the **ledger WRITE**, not the **pre-dispatch GATE** — these are two distinct points in the step lifecycle. The spec MUST pin: **each fan-out branch coroutine evaluates `_hitl_required` (U-CP-43 / C-CP-17 §17.2) BEFORE each effectful step dispatches, inside the branch, exactly as the `SINGLE_THREADED_LINEAR` path does** — only the *audit append* is buffered to the barrier drain. A naive implementation that "defers the step machinery to the drain" would gate *after* the effect — catastrophic. State as an invariant: *"parallel execution composes the committed pre-dispatch gate per-branch; concurrency MUST NOT bypass, batch-past, or post-pone the blast-radius gate. The buffered path defers only the append, never the gate."* This is the seam between D3 (cancel) and D1.b (buffered append), and it is the single highest-value C10 contribution to this fork.

### Obligation 3 — the persisted `terminal_status` must DISCRIMINATE effect-landed from effect-clean (not merely "mark cancelled").
A single flat `cascade_cancelled` marker applied to both not-dispatched and ran-to-completion branches **loses whether an effect hit the world** — which is the entire basis of C10's reactive-containment-via-audit posture (the audit trail IS the primary defense; SKILL §"maximal-action-surface posture" (b)). The persisted `terminal_status` (Route-Y `branch_metadata` sidecar, per design §2.4 / §5 commitment 2) MUST distinguish at minimum:

- `cancelled-clean` — step was not yet dispatched; no external effect; cleanly aborted.
- `cancelled-effect-landed` — an in-flight effectful step ran to completion/timeout despite the cancel; an external effect landed (and, if `external-reversible`, a rollback action is owed / available via the step's rollback API).

Without this discrimination, resume/operator cannot tell "nothing happened" from "an effect happened that you must reconcile." A cancelled branch with no *distinguishable* ledger entry reads as "never dispatched / still pending" — `[[feedback-verify-observation-layer-before-concluding-defect]]` in reverse. The audit must carry "an effect landed despite cancel," or the reactive-containment posture is hollow.

### Obligation 4 — high-blast-radius effectful steps are gated BEFORE dispatch (compose, don't re-invent).
The spec MUST state that the pre-dispatch gate for an effectful step is the *committed* `gate_level` `max()` (C-CP-19 §19.1) composing `BlastRadiusTier` (`external-irreversible → tier-4-full-vm → ASK/DENY`) with persona tier and `per_tool_gate_level` — resolving to the 4-response HITL palette. `cascade-cancel` does NOT introduce its own gate; it relies on the fact that the dangerous class was already gated at the dispatch boundary (Obligation 2 ensures fan-out preserves this). This is the formal statement that "(A) gates high-blast-radius effectful steps before dispatch, where cancellation is clean."

---

## 4. Tension with orchestration (C1) — named honestly.

The genuine, non-formulaic tension:

**C1-orchestration wants `cascade-cancel` to read as "all siblings stop NOW — a total, clean abort."** That is the natural orchestration mental model: a barrier fails, the `TaskGroup` cancels, everything unwinds, the fan-out is as-if-never-run. It is clean, symmetric, and easy to reason about for control flow.

**C10 insists `cascade-cancel` is bounded at the dispatch boundary.** Pending steps cancel cleanly; an **already-dispatched effectful step runs to its own completion/timeout and is recorded**. "Cancel" is NOT instant total abort. The action-safety lens cannot accept the C1 model as stated, because **pretending an in-flight `send_email` got cancelled when it actually sent IS the silent-uncompensated-effect failure mode** — the exact thing this fork exists to prevent. `asyncio.TaskGroup` cancellation aborts the *Python task*; it cannot un-ring the bell of an effect already dispatched to the world.

The reconciliation (and it is a genuine reconciliation, not a fudge): the two models agree on every step that has *not* hit the world (cancel it — C1's clean abort holds there) and differ only on the in-flight effectful step. For that step, C10's bound is non-negotiable: **let it complete, record it with a discriminating `terminal_status`, surface it to the operator/resume.** C1 gets its clean abort for the not-dispatched majority; C10 gets honesty for the in-flight minority. The word "cancel" in `cascade-cancel` must be spec-defined as *"cancel-before-dispatch + record-after-dispatch,"* not *"abort-everything-instantly,"* or the abstraction lies.

A dyadic C1⊥C10 convening (or at minimum naming both positions in B1-spec-1) is warranted precisely here — this is the one genuinely-contested surface, and the spec wording of "cancel" is where the tension either resolves cleanly or hides a safety hole.

---

## Summary (action-safety position, decisive)

- **Choose (A).** Restrict `cascade-cancel` to the pre-dispatch boundary; gate high-blast-radius effectful steps before dispatch (committed gate); record in-flight completions with a discriminating persisted `terminal_status`. NO new primitive.
- **(A) is complete, not a defer.** The only dangerous class (`external-irreversible`) cannot reach silent dispatch — it is foreclosed by the committed `blast_radius_floor → gate_level max() → HITL palette` chain. No deferred remainder.
- **(B) is the wrong primitive on the merits** (independent of I-6/X-AL-3): an irreversible effect cannot be rolled back; it must be gated before it fires, which the committed design already does. A "rollback" of an irreversible effect would be a lie in the audit.
- **Four spec obligations** (§3): (1) dispatch-boundary-bounded semantic; (2) **fan-out introduces no concurrency gate-bypass — the buffered path defers the append, never the gate**; (3) **discriminating `terminal_status`** (effect-landed vs clean); (4) compose the committed pre-dispatch gate, don't re-invent.
- **Honesty flags:** no `dry_run`/`preview` primitive exists (grep empty) — cite `EDIT`/`REJECT` palette + `_hitl_required`-ask instead; the pre-dispatch-gate claim is a committed *contract*, and B1-spec-1's obligation is to *wire* the fan-out path to it (`cascade_policy` is currently declared-but-unconsumed).
- **C1 tension:** "cancel" ≠ instant total abort; it is cancel-before-dispatch + record-after-dispatch. Reconcilable, but the spec wording of "cancel" is load-bearing.

---

*Grounding (file:line, verified this session): `harness-as/src/harness_as/sandbox_tier.py:45-51`; `harness-as/src/harness_as/blast_radius_floor.py:30`; AS spec §2.4 (`design-substrate/Spec_Action_Surface_v1.md`); `harness-cp/src/harness_cp/gate_level_rule.py:48-60` (C-CP-19 §19.1, GateLevel {AUTO,ASK,DENY}); `harness-cp/src/harness_cp/hitl_response_palette.py:33-51` (C-CP-16 §16.1, APPROVE/EDIT/REJECT/RESPOND); `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py:8-12` (C-CP-17 §17.2, `_hitl_required` pre-dispatch eval); `harness-cp/src/harness_cp/topology_pattern.py:55-67` (CascadePolicy); design doc §5 commitments 2/5 + §2.4 Route-Y sidecar. Negative grounding: `dry_run`/`preview` grep across harness-as/src + harness-cp/src + AS spec = empty (no such primitive — cited the palette instead). Voice: C10, SKILL.md maximal-action-surface + four-tier blast-radius + reactive-containment-via-audit. Advisor consulted pre-write (sharpened obligations 2/3 + the two honesty flags).*
