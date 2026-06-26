# Finding — `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT` is NOT a clean leaf-fenced single-level slice

*R-FS-1 forward-arc design finding. 2026-06-25. Mode-agnostic process-substrate (no design-substrate change). Records a design dead-end so the next session that opens this arc does not repeat it. The arc STAYS `registered` (not closed) in `.harness/arc-ledger.yaml`.*

---

## 0. TL;DR

A full build of the arc's "leaf-fenced single-level child slice" was authored (CP spec v1.67 delta + CP/runtime impl + 14 by-execution witnesses, all green: pyright 0/0/0, harness-cp 1321 + harness-runtime 2118) and then **REVERTED before merge** after the out-of-family Codex review found **two genuine [P1] crash-resume correctness gaps** that the advisor + I missed and that the by-execution witnesses did not catch (they used a **faked** child dispatcher). advisor reconciled toward Codex: the "leaf-fenced single-level slice" framing was wrong. The arc is a genuinely-larger mechanism than a thin slice. **Disposition: fail-closed-and-register-larger** (option (b) below) — honest under FULL-SPEC (`register ≠ defer`); shipping the unsound close was the failure mode avoided.

---

## 1. What the arc is

The v1.65 TOOL_STEP slice (`B-FANOUT-CRASH-RESUME-MAYBE-RAN-EFFECT-BEARING`) recovered a maybe-ran fan-out TOOL_STEP worker on a strict-tier (PAUSE / CASCADE_CANCEL) crash-resume, because re-dispatching it re-reaches the runtime effect fence keyed on the deterministic per-`(run, step, tool)` `idempotency_key` → at-most-once at the tool sink. It explicitly left `SUB_AGENT_DISPATCH` fail-closed: a sub-agent's own dispatch does not hit the fence directly — its non-idempotent effects are its CHILD sub-workflow's tool calls, fenced at the CHILD's tool sinks → "recursive child crash-resume, a larger, separately-verified mechanism" (v1.65 §3). This arc is that recursive mechanism.

## 2. The grounding that IS correct + reusable (verified by direct read, not subagent report)

- **The child run_id is non-deterministic today.** `child_workflow_runner._runner` (`harness-runtime/src/harness_runtime/lifecycle/child_workflow_runner.py:153-155`): `child_run_id = pause_snapshot_input.run_id if pause_snapshot_input is not None else uuid.uuid4().hex`. A fresh re-dispatch of a maybe-ran SUB_AGENT worker gets a fresh uuid → a DISJOINT child fence claim namespace (runtime spec §14.22.7: "a fresh run derives a different `run_idempotency_key` → a disjoint claim namespace") → it re-fires every child tool blind → DOUBLE-FIRE. So the TOOL_STEP pattern does NOT transfer verbatim.
- **The fence is durable + re-reachable by key.** The claim file = `sha256(idempotency_key)` under the fence dir (fsync'd, survives crash). On a re-run, a COMMITTED child tool's fence does `read_output(idempotency_key)` → **suppress-with-captured-output** (returns the captured output, `runtime_tool_dispatcher.py:1013-1037`); an output-lost-in-the-fire→capture-window tool → `EffectFenceAmbiguousUncommittedError` → §26.2 PAUSE (not corruption). So for a SIMPLE LINEAR leaf-fenced child the final_state DOES reconstruct correctly.
- **The fence auto-active set** is `_DURABLE_AUTO_FENCE_ENGINE_CLASSES = {SAVE_POINT_CHECKPOINT, EVENT_SOURCED_REPLAY, WAL_SEGMENT, RECONCILER_LOOP}` (`runtime_tool_dispatcher.py:112-119`); the fan-out crash-resume engine classes `{EVENT_SOURCED_REPLAY, WAL_SEGMENT}` are a subset.
- **The child engine_class is OPAQUE to CP.** `WorkflowStep.step_payload: Mapping[str, Any]` is "opaque to the driver" (`workflow_driver_types.py:110`); the child manifest is parsed runtime-side (`SubAgentDispatchPayload.model_validate`, `sub_agent_dispatch.py:550`). So CP cannot read the child fence-activeness at classification.
- **A child effect-fence-ambiguous propagates + the barrier catch is reachable on the SUB_AGENT path.** The generic by-name `except Exception` catch at `workflow_driver.py:8407`/`8325` (the v1.65 `EffectFenceAmbiguousUncommittedError` name-match) is generic over step_kind (the dispatch at `:8291` routes by kind internally), so a SUB_AGENT worker's child-propagated fence error composes through it.
- **`parent_idempotency_key` is the correct stable key** (advisor must-fix): it already keys the child dispatch (`sub_agent_dispatch.py:303/335`) and encodes run + branch + loop-iteration distinctness + is resume-stable (§14.22.7). Deriving the child run_id from it (NOT a hand-rolled `(run_id, branch_index, step_id)` tuple, which would silently suppress loop-iteration effects) + folding in `child_workflow_id` (so a child-SWAP fires fresh rather than silent-dropping) is the right E1 derivation.

## 3. The two [P1] gaps Codex found (the reason this is NOT a thin slice)

### [P1-a] Recursive RESULT-fidelity, not just at-most-once (`[[recovery-effect-fidelity-vs-result-fidelity]]`)

"Leaf-fenced" was scoped as "child engine ∈ auto-fence set AND no nested `SUB_AGENT_DISPATCH`/`MANAGED_AGENTS` child steps." **That does NOT exclude a fan-out-of-TOOL-steps child** (a PARALLELIZATION / ORCHESTRATOR_WORKERS child whose workers are all TOOL_STEP). With the deterministic child run_id, re-dispatching such a child engages the **child's OWN fan-out crash-resume reconstruction** (the child's prior `EngineOutputStore` journal is present under the same run_id) — a recursive path whose final_state reconstruction was NEVER witnessed. The authored CP witnesses used a **faked** `_SubAgentDispatcher` that echoes `{"branch": index}`, so they were structurally vacuous for exactly this path. A re-dispatched child that "skips a committed prefix but initializes `accumulated` empty and only adds newly-executed suffix steps" returns a **suffix-only / empty `final_state`**, which the parent then records + folds → corrupted aggregate. At-most-once (effect-fidelity) being preserved does NOT imply result-fidelity.

### [P1-b] The gate trusts the ORIGINAL fence-active fact but re-dispatches the RESUMED child

The classifier gate checked (a) marker-kind==SUB_AGENT, (b) resumed-kind==SUB_AGENT, (c) DISPATCH-TIME-recorded `child_fence_active`==True. It did NOT verify the **RESUMED** child is still leaf-fenced. An operator who keeps the outer kind `SUB_AGENT_DISPATCH` but edits the child PAYLOAD (engine non-durable, or adds nested sub-agents) between crash and resume passes the gate (recorded-original fact is True) → the re-dispatch runs the new NON-fence-active child whose tools fire unfenced while the original child's maybe-ran effects may already have fired → DOUBLE-FIRE. The changed-kind guard catches an outer-kind change but NOT a child-payload change (the child manifest is opaque to CP).

## 4. The constraints any future build MUST satisfy

1. **A genuinely-single-level slice must require `topology == SINGLE_THREADED_LINEAR`** for the child (add to the `child_fence_active_hint` leaf condition), excluding fan-out children entirely. "No nested sub-agents" ≠ "no recursion."
2. **The recovery gate must require BOTH** the DISPATCH-TIME-recorded original `child_fence_active`==True (the #742 changed-manifest lesson — can't trust the resumed manifest alone) **AND** a RESUMED-child fence-active check (query `child_fence_active_hint` on the resumed step at classification, require True) — closes [P1-b].
3. **A REAL recursive-child witness is the tiebreaker** (`[[full-chain-witness-not-half-proofs]]`): a SUB_AGENT worker dispatching a REAL (non-mocked) child sub-workflow (≥2 steps incl. a committed TOOL via the real `EngineOutputStore` + real effect fence), crash the parent mid-fan-out so the branch is maybe-ran, resume, and assert **recovered child `final_state` == no-crash child `final_state`** AND the child tool fired exactly once. This is the discriminator for whether `execute_workflow` re-runs the child from step 0 (no snapshot, reused run_id) correctly. **No such harness exists today** — every `sub_agent_dispatch` test mocks the child runner (`_MockChildWorkflowRunner`); the topology fixture suite runs topologies but not a real recursive child crash-resume. Building it is the load-bearing cost.
4. **E1 (deterministic child run_id) has NO consumer without the recovery** — landing it as scaffolding with recovery still fail-closed is a `[[wired-handler-unreachable]]` half-mechanism. Build E1 only together with a sound recovery.

## 5. The three options (for the next attempt)

- **(a) Narrow to LINEAR leaf-fenced child** — add `topology == SINGLE_THREADED_LINEAR` to the hint; gate on recorded-original AND resumed-child fence-active; land the **real linear recursive-child witness**; register the fan-out-child recursive case as a further follow-on. **Only if the real witness comes back clean.** The mechanism design from §2 (E1 from `parent_idempotency_key` + `child_workflow_id`; E2 dispatch-time `child_fence_active` marker; changed-kind guard) is reusable.
- **(b) Keep ALL maybe-ran SUB_AGENT fail-closed** (CURRENT disposition) — register the whole recursive-child mechanism as the larger arc. Honest under FULL-SPEC.
- **(c) Full fix-forward** (linear + fan-out child) — requires proving recursive fan-out-child result-fidelity end-to-end. The genuinely-large mechanism advisor originally named. Highest cost.

## 6. Why (b) this session

advisor's reconcile lean was (b) "unless the (a) witness is cheap AND clean on the first try." The real recursive-child harness does not exist (multi-hour build) and even a clean linear result still needs the resumed-fence gate + the narrowing — a multi-round fix+re-review cycle in an already-deep context, which `[[feedback-autonomous-loop-dont-stop-to-ask]]` names as the "loop-wants-progress / sunk-cost" trap. The authored code is sunk cost, not a reason to fix-forward. The honest, disciplined outcome is to NOT close, document the constraints (this file), and leave the arc cleanly registered for a fresh-context (a) attempt.

## 7. Reviewer chain

- **advisor** (full-transcript, ×4): the fence-persistence gating check → the deterministic-vs-persist fork (resolved deterministic, the ordering trap) → the opaque-boundary reconcile (gate basis must be dispatch-time-recorded, the #742 lesson one level down) → the **Codex reconcile** (conceded the leaf-fenced slice was wrong; lean (b); the loop-trap + sunk-cost + dead-scaffolding warnings).
- **out-of-family Codex (gpt-5.5)**, uncommitted-diff review: the two [P1]s above — the decorrelated catch the transcript-aware advisor + I missed (`[[hooks-codex-pilots-decorrelation-validated]]`).
- **direct grounding**: every §2 fact verified by direct read (presence-not-correctness).

---

## 8. HEAD-VERIFIED RE-SCOPE (2026-06-26, fresh-context `/loop continue`) — [P1-a] is NO LONGER a dead-end; the next attempt is BOUNDED + WITNESS-FIRST

*This §8 supersedes the §5 option framing's cost read. §1–§7 above are PRESERVED verbatim (frozen at 2026-06-25 write-time). Re-grounded against HEAD per the §12.5.4 "verify a frozen finding-doc against HEAD before acting on it" discipline + advisor full-transcript ×3. The §746 finding PREDATES the three arcs that landed specifically to unblock it.*

### 8.1 What changed under this doc since it was written

`#764` REGISTERED + `#766` BUILT + `#768` EXTENDED **`B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT`** — the arc whose close note states it "UNBLOCKED the 2 SUBAGENT arcs for LINEAR-ESR/WAL (result-fidelity blocker removed)." That removed blocker **IS [P1-a]** (§3) — the re-dispatched child returning a SUFFIX-ONLY / empty `final_state` because `accumulated` is empty. HEAD facts (direct read, 2026-06-26):
- `execute_workflow` / `_execute_workflow_body` now default `reconstruct_final_state=True` (`workflow_driver.py:1770/2038`; `:3314` "no production caller takes `=False`").
- `child_workflow_runner._runner` passes `reconstruct_final_state=True` EXPLICITLY into the same `execute_workflow` (`child_workflow_runner.py:187`).
- The `#766` CP witnesses (`test_workflow_driver.py:1322+`) prove `execute_workflow(reconstruct_final_state=True)` seeds the committed prefix → FULL `final_state` {step-0, step-1, step-2}, NOT suffix-only.

→ For a **LINEAR (`SINGLE_THREADED_LINEAR`) child**, [P1-a]'s result-fidelity is structurally addressed by the SAME mechanism #766/#768 proved. The FAN-OUT child (PARALLELIZATION / ORCHESTRATOR_WORKERS workers) recursive reconstruction is the larger case → KEEP the §4 constraint-1 LINEAR narrowing (excludes fan-out children).

### 8.2 The catch — [P1-a]-closed is a HYPOTHESIS the witness must confirm, NOT "closed by construction" (advisor)

"Same `execute_workflow`, same flag, proven reconstruct" is MECHANISM reasoning that skips the ONE unproven INTEGRATION fact: **does a REAL recursive child actually get an `engine_output_store` bound under its REUSED run_id with the committed prefix, and does that store present the prefix to the seeding on resume?** The `#766` witnesses use a `_FakeOutputStore` that **IGNORES `run_key`** (`test_workflow_driver.py:1100-1102` — returns ALL outputs regardless of run_key) → structurally CANNOT witness "store bound under the reused run_id." Asserting [P1-a]-closed "by construction" is the EXACT presence-not-correctness move that got the §0 full build REVERTED. Treat the re-scope as a hypothesis the witness TESTS.

### 8.3 The witness is the WORKSPACE'S OWN open coverage residual

`test_lifecycle_sub_agent_dispatch.py:752` (`test_child_workflow_runner_opts_into_final_state_reconstruct`) docstring, verbatim: *"The real-runner-THROUGH-execute_workflow integration remains the pre-existing AC #7 coverage residual (needs a fully-bootstrapped HarnessContext)."* That witness MOCKS `execute_workflow` (a spy) → proves the runner FORWARDS the flag (wiring), NOT that a real recursive child reconstructs. So the discriminator genuinely does not exist at HEAD — confirming §4 constraint 3. Feasibility, however, is GREEN (NOT a hard wall): the real `RuntimeSubAgentDispatcher` (`test_topology_fixture_suite.py:486`, sync + driver-callable), the real `compose_child_workflow_runner(ctx)`, and the `_bootstrap_ctx` (fully-bootstrapped HarnessContext, faked provider/OD stages, CI-runnable) ALL exist. The "frozen HarnessContext" the topology suite cites (`:25`) is moot for a crash-resume witness: use TWO fresh contexts sharing ONE on-disk store + fence dir (advisor).

### 8.4 The NON-VACUOUS witness recipe (the next attempt builds THIS first, before any spec/impl/E1)

Build the discriminator as a STANDALONE probe (the §746 revert happened because the 14 witnesses used a FAKED `_SubAgentDispatcher` → "structurally vacuous for exactly this path"). Components (all verified to exist at HEAD):
1. A **run_key-RESPECTING** store — a real on-disk `EngineOutputStore` (keyed by `run_idempotency_key`, `engine_output_store.py`; producer writes via `workflow_driver.py:694 _store.record(run_idempotency_key, …)`) OR a faithful mirror that keys outputs by `run_key`. A `run_key`-ignoring fake REPRODUCES the vacuity trap → forbidden.
2. A REAL child (≥2 steps incl. one COMMITTED `TOOL_STEP` writing to the store + fence) routed through the REAL `compose_child_workflow_runner(ctx)` — NOT a mocked runner, NOT a direct `execute_workflow` call.
3. **Pin the child run_id to simulate E1** — the runner derives `child_run_id = uuid.uuid4()` on a crash-resume (`pause_snapshot_input is None`, `child_workflow_runner.py:153-154`), so a fresh re-dispatch is NOT recognized as a resume (fresh key → ledger_reader returns 0 materialized → `resume_at=0` → full fresh run, no reconstruct). Monkeypatch `uuid.uuid4` (or thread a pinned id) so the re-dispatch REUSES the original run_id → the store + ledger_reader align → the reconstruct path fires. This ISOLATES [P1-a] from building E1.
4. Crash the parent mid-fan-out (branch maybe-ran) → resume → assert **recovered child `final_state` == no-crash child `final_state`** (FULL, not suffix-only) AND the committed tool fired EXACTLY ONCE (fence suppressed the re-fire).

### 8.5 Outcome-gated next steps

- **Witness GREEN ([P1-a] reconstructs):** the arc's remaining scope is BOUNDED — **E1** (deterministic child run_id from `parent_idempotency_key` + `child_workflow_id`, §2) **+ the [P1-b] resumed-child fence gate** (require BOTH the dispatch-time-recorded original `child_fence_active` AND a RESUMED-child fence-active check) **+ the LINEAR narrowing** (§4 constraints 1–2). E1 + recovery land TOGETHER (§4 constraint 4 — E1-alone is a `[[wired-handler-unreachable]]` half-mechanism). Then out-of-family Codex (the §0 revert was a Codex catch — expect ≥1 round).
- **Witness suffix-only / RED:** the re-scope hypothesis is wrong; stay fail-closed, register the larger recursive mechanism honestly. A real finding either way.

### 8.6 Loop posture (this session)

This iteration RE-GROUNDED + RE-SCOPED the arc (the durable deliverable above) + ran the feasibility probe (GREEN) + identified the vacuity trap + **BUILT the [P1-a] discriminator witness (§8.7).** Reviewer chain this pass: advisor full-transcript ×3 (the [P1-a]/#766 reconcile → build-the-witness → the build-now-vs-bank-and-reschedule reconcile, which advisor resolved DECISIVELY toward "build the witness now — you're at peak knowledge; the bootstrap exists; the wall is forecast not hit; bank a real win, not prose").

### 8.7 WITNESS BUILT + GREEN — [P1-a] EMPIRICALLY CONFIRMED CLOSED for the linear child (2026-06-26)

`harness-runtime/tests/integration/test_recursive_child_crash_resume_final_state_witness.py` — 2 tests, both GREEN:
- **`test_recursive_child_crash_resume_reconstructs_full_final_state`** — a REAL recursive child routed through the REAL `compose_child_workflow_runner` → `execute_workflow` (NOT a mocked runner / spied execute_workflow — the §0 vacuity trap AVOIDED), over a REAL on-disk `EngineOutputStore` (run_key-RESPECTING, unlike the #766 fake), child run_id PINNED via `uuid.uuid4` monkeypatch (simulating E1), `resume_at=2` over a committed prefix → reconstructs the COMPLETE `final_state` {step-0, step-1, step-2}, only step-2 re-dispatched.
- **`test_recursive_child_crash_resume_without_store_degrades_to_suffix_only`** (NEGATIVE CONTROL, RED-without-the-store) — the SAME resume with NO `engine_output_store` bound → suffix-only {step-2}.

The WITH/WITHOUT pair IS the integration discriminator the #766 run_key-ignoring fake could not witness. **Non-vacuity self-audit:** the WITH-store test PASSING also proves my `_run_key`/`_step_key` replication MATCHED the driver's actual derivation (`_compute_run_idempotency_key` extras=`(str(entry_version),)`, line 1970) — a wrong key → the store read finds nothing → suffix-only → the test would FAIL. Scope is honestly LINEAR-only (the in-scope case per §4 constraint 1); the FAN-OUT-child recursive reconstruction stays a registered follow-on. INFERENCE_STEP children suffice for the [P1-a] RESULT-fidelity question (the driver's `_record_engine_output` auto-commits regardless of kind; TOOL+fence is [P1-b]/at-most-once, a separate witness). **Decorrelated check (the §0 lesson — a GREEN witness was vacuous and only Codex caught it):** out-of-family Codex review (`just codex-review-uncommitted`) came back CLEAN on the witness — verbatim *"The added recursive-child witness test passes"*, ZERO findings against the witness or this addendum (all its [P2]/[P3]s were about UNRELATED pre-existing untracked `dashboard-design/` + `.agents/skills/` files, not in this commit). So the false-GREEN safeguard is satisfied: the witness is non-vacuous by both the WITH/WITHOUT discriminator + the decorrelated review.

**→ The arc's remaining scope is now BOUNDED + DE-RISKED (the next fresh-context build):** E1 (deterministic child run_id from `parent_idempotency_key` + `child_workflow_id`) + the [P1-b] resumed-child fence gate + the LINEAR narrowing, landed TOGETHER (§4 constraint 4) with their own at-most-once witnesses + Codex rounds. [P1-a] result-fidelity is no longer a blocker for the linear child.
