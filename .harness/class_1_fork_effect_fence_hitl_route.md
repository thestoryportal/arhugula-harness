# Class 1 (design) — Effect-fence HITL route: fail-closed → §22.1 PAUSE + suppress-and-continue (B-EFFECT-FENCE-HITL-ROUTE)

**Status:** ✅ BUILT 2026-06-22 (runtime spec v1.72 §14.22.8 + CP spec v1.51 §26.2 + harness-runtime + harness-cp impl + by-execution witnesses + clearance markers; bundled-absorption PR). The operator AUTHORIZED the build (AskUserQuestion) over the other 2 gated arcs + R-CL-Q1. **CORRECTION at build (primary-source grounding + advisor):** the new pause-reason value homes in **C-CP-26 §26.2 `WorkflowPauseReason`** (the workflow-driver pause taxonomy the driver's `capture_pause_snapshot` is typed to), **NOT** the engine-layer §22.1 `PauseReason` this doc's §3 verification 1 claimed — the driver-routed pause path's type signature settled it (the §22.1 enum is the engine-native replay-pause substrate the driver never calls; the HITL precedent is exact: `WorkflowPauseReason.HITL_PENDING`, not the engine `HITL_INVOCATION_PENDING`). Everything else in this doc held: the crux (the arc MUST add its own post-fire output capture; replay can't supply it), the two-case split + the at-most-once invariant, and all 3 verifications. The two committed-behavior gates (a new `WorkflowPauseReason` value + the suppress-and-continue recovery semantic relaxing the fence's deliberate fail-closed) are operator-ratified by the authorization.

**Build record (what landed):** new `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS`; `RuntimeEffectFence.capture_output`/`read_output` (atomic, present ⟹ complete-and-valid); `EffectFenceReservedUncommittedError` → `EffectFenceAmbiguousUncommittedError` (the two-case split removed its sole raise site); dispatcher captures post-validation/post-cost as the last step before return + splits the lost reserve (present→suppress-and-continue, absent/corrupt→raise); `workflow_driver` name-matches the ambiguous error at the linear/TOOL_STEP boundary → §26.2 PAUSE (bound) / FAILED (unbound, behaviorally equivalent to pre-v1.72; only the fail_class string differs). Witnesses: dispatcher suppress + ambiguous-absent + ambiguous-corrupt + durable-suppress-across-restart; driver PAUSE/FAILED; retry-breaker verbatim re-raise; 6-class cardinality. No new fail-class/§5.2-hash/Protocol-widening/CXA edge.

**Scope correction at build (Codex pre-merge [P2]×2):** this arc ships suppress-and-continue + the ambiguous-pause CAPTURE — the §2 design's "operator resolves (it-fired-use-this / re-fire / abort)" RESOLUTION is a safety-sensitive surface (re-fire = a deliberate double-execution on operator assertion → clear the fence claim; skip-as-fired = a data-flow decision) registered as the follow-on **`B-EFFECT-FENCE-PAUSE-RESOLUTION`** (runtime §14.22.7). The captured PAUSE is a strict improvement over the v1.60 terminal FAILED (labeled, non-terminal, inspectable, hash-valid); a naive resume re-pauses identically until the resolution arc lands (INERT — resume is caller-initiated; verified no auto-resume daemon; pinned by a by-execution interim test). Codex also caught the suppress path skipping `sandbox.exit` (enter-without-exit telemetry gap) → FIXED + span-tested. advisor reconciled both: (B) partial-land honestly (don't bolt the resolution palette onto a large session) + fix the telemetry.

**Posture:** design-phase back-flow (a committed-behavior change to the §14.22 C-RT-31 effect fence's failure semantic + a new §22.1 PauseReason + NEW output-capture substrate). FULL-SPEC pre-authorizes the back-flow; the precise recovery semantic is operator-ratified (the authorization). Cross-axis: runtime spec §14.22 + CP spec C-CP-22 §22.1. Reliability primitive — **the highest-asymmetry change in the codebase** (relaxing a load-bearing fail-closed that prevents double-execution of non-idempotent effects). Build under fresh context + adversarial review.

---

## 1. The crux (advisor-sharpened) — "the prior output" was NEVER persisted

The §14.22 fence (`effect_fence.py`) writes a RESERVE claim **before** the effect fires; the tool output exists only **after** `call_tool` returns; the step **never committed** (the crash is in the fire→commit window). So "suppress-and-continue = return the prior output" requires output **that was never persisted**. The fence docstring (lines 38-41) waves at `B-ENGINE-OUTPUT-REPLAY` for it — but the **2026-06-22 probe found replay CANNOT supply it** (its resume-rehydrate is `resume_at`-driven and DELIBERATELY ignores the suppressed step's own uncommitted output, exposes only `most_recent_output()` [predecessor data-flow], covers a SUBSET of the fence's durable-set). **So the output substrate is NOT borrowable — this arc MUST add it.**

## 2. The vetted design — capture output at the sink; two-case split (the decline-mirror invariant transferred)

Add **post-fire / pre-commit durable output capture** at the fence, and split the re-dispatch into two cases. The invariant (the #701 decline-mirror transferred): **define the ONE condition under which the relaxation is safe (captured-output present + valid = PROOF the effect completed) and fail-to-operator outside it. NEVER auto-proceed on the ambiguous case** — that IS the at-most-once guarantee.

**Sink ordering (verified at `runtime_tool_dispatcher.py` step 6b @930 → step 7 @958):**
```
reserve(idempotency_key)        # pre-fire claim (EXISTING, line 930)
  → call_tool(...) [EFFECT FIRES]   # line 958; `response` available @964
  → capture_output(key, response)   # NEW: atomic fsync'd OUTPUT file, same key, BEFORE returning
  → [up to driver] → _append_step_ledger_entry()   # COMMIT (existing)
```

**Re-dispatch (lost `try_reserve`, today an unconditional raise @932) → two cases:**
- **OUTPUT file present + valid** → the effect demonstrably completed AND we have its result → **return the captured output (auto suppress-and-continue)**. The step proceeds as if it ran; NO re-fire. This never reaches the driver as an exception — the sink just returns. **This is the value of the arc** (the PAUSE-only slice the probe called low-value is the residual, not the deliverable).
- **OUTPUT file absent OR corrupt** → crash between fire and output-fsync → genuinely ambiguous → **§22.1 operator-resolvable PAUSE**. Operator resolves (it-fired-use-this / re-fire / abort).

**Atomic output capture** (mirror the claim's `O_EXCL`/`os.link` crash-atomicity): write the output to a uuid temp, fsync, `os.link` into `<key>.output`, fsync dir. So **present ⟹ complete-and-valid** (a torn write can only leave an orphan temp, never a half-published output). A present-but-corrupt output (defensive — should be impossible via atomic link) fail-closes to PAUSE, NOT treated as a valid suppress-and-continue source (`[[durable-recovery-presence-validity-scope]]` — fail-closed on corrupt).

## 3. The three verifications (RESOLVED this session)

1. **Pause taxonomy = C-CP-22 §22.1 `PauseReason` (engine-layer), NOT C-CP-26 `WorkflowPauseReason`.** ✅ Confirmed: `harness_cp/pause_resume_protocol.py:53` `PauseReason` has 4 values (HITL_INVOCATION_PENDING / CROSS_DEPLOYMENT_BRIDGING_ARC_PAUSE / OPERATOR_INITIATED_PAUSE / ENGINE_NATIVE_PAUSE). The new value (e.g. `EFFECT_FENCE_AMBIGUOUS` / `"effect-fence-ambiguous-uncommitted"`) homes HERE. (The spine-ledger/dashboard framing said "§22.1" — correct; my early notes mislabeled it `WorkflowPauseReason` — the advisor caught it.)
2. **Propagation path (sink-signal → resumable `RunStatus.PAUSED`).** ✅ Pattern exists: the driver produces PAUSED via `protocol.capture_pause_snapshot(...)` (`workflow_driver.py:488-489` flag-path; the cascade=pause executors capture per-strategy). The fence's ambiguous case raises a **NEW distinct exception** (e.g. `EffectFenceAmbiguousUncommittedError`, separate from `EffectFenceReservedUncommittedError`) that the driver's step-dispatch handler catches **separately from the RT-FAIL-mapping `except` blocks** (`workflow_driver.py` ~2295-2469) and routes to `capture_pause_snapshot(pause_reason=<new>) → RunStatus.PAUSED`. **Gated on a bound `ctx.pause_resume_protocol`** (mirrors the cascade=pause requirement): unbound → fall back to the EXISTING raise → FAILED (byte-identical to today; the safe opt-in default). The auto-recover case never reaches the driver. **Build-open: confirm the linear/TOOL_STEP single-step dispatch path reaches a `capture_pause_snapshot` boundary** (the cascade arcs hook it in the fan-out/handoff/EO executors; the linear tool-step path needs the new pause-capture branch added to the step-dispatch except — this is the real impl complexity, NOT the enum add).
3. **Output durability ordering + crash windows.** ✅ Confirmed safe: (a) crash after-fire-before-output-fsync → reserve present + output ABSENT → PAUSE (cannot auto-re-fire); (b) crash after-output-fsync-before-commit → reserve present + output PRESENT → suppress-and-continue (recover, cannot re-fire). Both windows fail safe; neither auto-re-fires. The at-most-once guarantee is preserved (auto-proceed ONLY on proof-of-completion).

## 4. Impl surfaces (the build's file map)

| Surface | Change |
|---|---|
| `harness-runtime/.../lifecycle/effect_fence.py` | NEW `capture_output(key, payload)` + `read_output(key) -> payload\|None` (atomic O_EXCL/link, fsync, same `<digest>` keying as the claim); a `EffectFenceAmbiguousUncommittedError` (or extend the protocol) |
| `harness-runtime/.../lifecycle/runtime_tool_dispatcher.py` | step 6b two-case split (lost reserve → `read_output`: present→return; absent→raise the new ambiguous signal); post-`call_tool` `capture_output(key, response)` before return (gated on the same `_fence_gate_open`) |
| `harness-cp/.../pause_resume_protocol.py` | NEW `PauseReason` value (§22.1) |
| `harness-cp/.../workflow_driver.py` | NEW except branch at the step-dispatch boundary: catch the ambiguous signal → `capture_pause_snapshot(new reason)` → `RunStatus.PAUSED`, gated on bound `pause_resume_protocol`; unbound → existing FAILED |
| `design-substrate/Spec_Harness_Runtime_v1.md` §14.22 | the fail-closed → PAUSE+suppress-and-continue semantic + the output-capture substrate + the two-case invariant (a v1.71→v1.72 delta) |
| `design-substrate/Spec_Control_Plane_v1_NN.md` §22.1 | the NEW `PauseReason` value (a CP delta) |
| clearance markers | runtime + CP, per §4.5 |

## 5. Build plan + witnesses (fresh context)

By-execution witnesses (the safety-load-bearing set — `[[full-chain-witness-not-half-proofs]]`):
- **auto suppress-and-continue:** reserve taken + output captured + re-dispatch (lost reserve) → the captured output is returned, `call_tool` NOT re-invoked (a recording driver proves no second fire). THE deliverable.
- **ambiguous → PAUSE:** reserve taken + NO output captured (simulate fire-then-crash) + re-dispatch → `RunStatus.PAUSED` with the new §22.1 reason (NOT FAILED, NOT a second fire).
- **opt-out byte-identical:** no `pause_resume_protocol` bound → the ambiguous case raises → FAILED (the existing v1.71 behavior).
- **crash-window safety:** both windows (output-absent / output-present) resolve to their case; neither re-fires (the at-most-once invariant).
- **corrupt output → PAUSE** (defensive negative control: a torn output is not a valid suppress source).
- advisor (the at-most-once-preservation + the propagation path) + out-of-family Codex pre-merge.

## 6. Ratification points already settled (the operator authorization)

1. **Relax the fail-closed → PAUSE + suppress-and-continue** — AUTHORIZED (the AskUserQuestion choice).
2. **The two-case invariant** (auto-recover ONLY on captured-output-present; PAUSE otherwise; never auto-re-fire) — the safety contract; non-negotiable.
3. **New §22.1 `PauseReason` value** — AUTHORIZED (the committed-behavior gate the choice ratified).
4. **New output-capture substrate at the fence** — AUTHORIZED (the substrate-partial gate the choice ratified; replay can't supply it).

**Authority chain:** operator AskUserQuestion 2026-06-22 (B-EFFECT-FENCE-HITL-ROUTE authorized) + FULL-SPEC directive (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`) + advisor design-vet (the crux + the two-case invariant + the 3 verifications). Grounding leads verified at HEAD `0092060` (effect_fence.py lines 38-41/72-90; runtime_tool_dispatcher.py 6b @923-932 / call_tool @958; pause_resume_protocol.py:53 PauseReason; workflow_driver.py:488-489 capture_pause_snapshot).
