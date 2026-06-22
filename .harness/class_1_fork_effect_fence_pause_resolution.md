# Class 1 (design) — Effect-fence ambiguous-PAUSE resume-side resolution (B-EFFECT-FENCE-PAUSE-RESOLUTION)

**Status:** 📐 DESIGN-VETTED 2026-06-22 (advisor-concurred; BUILD-not-gate; fresh-context BUILD owed). The resume-side completion of the operator-recoverability story `B-EFFECT-FENCE-HITL-ROUTE` (#702) opened: #702 ships the ambiguous-pause CAPTURE (a labeled, non-terminal, hash-valid `WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS` PAUSE); a naive `api.resume` re-pauses identically (INERT — pinned by `test_ambiguous_pause_resume_re_pauses_until_resolution_follow_on`). This arc wires the resume to actually RESOLVE the pause via an operator-supplied resolution.

**Disposition correction (the load-bearing call) — BUILD-not-gate, NOT operator-gated.** The arc was registered at #702 as "OPERATOR-GATED + SAFETY-SENSITIVE." Grounded against the spec + the advisor's decorrelated reframe, that label is a self-assigned registration-time hypothesis (the operator's only #702 input was choosing HITL-ROUTE at the AUQ; the gate-label was the advisor's/my reconciliation), and it FLIPS — exactly as the sibling family labels flipped (#697 / #699 / #700 each ground a "design-fork-first" label → BUILD-not-gate). The discriminator (`[[disposition-label-is-a-claim-verify-against-spec]]` + `[[grounding-reveals-claude-closeable-slice-close-honestly]]` tenth variant): a resolve/gate is licensed only by a **forbidding invariant** or a **net-new-primitive / committed-decision sacrifice** — NOT by a safety-sensitivity adjective.

**The reframe that dissolves the gate (advisor; the #529 `cascade-cancel` out-of-domain precedent).** The fence raises `EFFECT_FENCE_AMBIGUOUS` *specifically to ask the operator one question — "did the effect fire?"* — because the harness genuinely cannot tell (the crash fell in the fire→capture window). The three resolutions are the operator **answering** that question with ground-truth the harness lacks (e.g. checking whether the email was sent / the git push landed on the remote):

| Resolution | The operator asserts | Ground-truth case | Action |
|---|---|---|---|
| `SKIP_AS_FIRED` | "it fired" | A — prior attempt fired, then crashed pre-capture | proceed, the lost output is unrecoverable → **empty output** |
| `RE_FIRE` | "it did NOT fire" | B — prior attempt claimed, then crashed pre-fire | clear the claim → re-dispatch → fires **fresh** |
| `ABORT` | "can't determine / give up" | — | terminal **FAILED** |

Under this reading **`RE_FIRE` does NOT breach at-most-once.** When the operator has correctly determined case B (the effect did not fire), re-firing is the FIRST and ONLY execution — still at-most-once *from the true state of the world*. The operator is supplying the ambiguity-resolving information the fence explicitly requested, **completing** the at-most-once decision the harness couldn't compute, not overriding a safety floor. A mis-asserting operator (claiming B when it was A) is an operator-error risk, not a harness-design breach — the same posture as a `blast_radius_tier` / `idempotent` mis-declaration being the author's responsibility (the #700 PER-TOOL reasoning). The palette composes only **committed primitives** (`clear_claim` + re-dispatch + the existing empty-output accumulate path + the existing FAILED mapping) → §13.4 discriminator (a) → **complete honest semantic, no operator gate, build autonomously.** FULL-SPEC pre-authorizes the back-flow (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`); "registered" means *now build it*, not *now ask*.

**No council (the §10.9 + §13.4 nameable-tension discriminator, probe-resolved).** The candidate C10⊥C11 tension (action-safety/blast-radius ⊥ operator-loop/minimal-burden) is dissolved by the reframe (re-fire is in-domain) + two probes that resolve the residual sub-decisions to the **minimal spec'd semantic** (no over-build, SCOPE BOUNDARY 2 / #628):
- **skip-as-fired data-flow** → the lost output is genuinely unrecoverable; the `anticipated_scope` names exactly "skip-as-fired (no-output, proceed)" → **empty output**, not an operator-supplied-output feature (that's the symmetric over-build trap; the workflow fails honestly downstream if a consumer needs the lost data — correct, the data IS gone).
- **re-fire attestation** → the `RE_FIRE` resolution choice IS the attestation (the HITL-response-delivery precedent: the operator's input is the input; no separate attestation surface).

No nameable tension survives the probes → single-voice + advisor (done), NOT a council convening (which would be the over-machinery failure mode §10.9 amendment-1 guards against).

**Posture:** design-phase back-flow (additive resume-side semantic on the §14.22 C-RT-31 effect fence + an additive `ResumeContext` field + an additive `PauseSnapshot` carrier). Cross-axis: runtime spec §14.22 + CP spec C-CP-26 §26.8 (`ResumeContext`) / §26.2 (`PauseSnapshot`). Reliability primitive — the highest-asymmetry surface in the codebase (it touches the fence that prevents double-execution of non-idempotent effects), so: design-vet (this doc) → fresh-context BUILD + adversarial review.

---

## 1. Current state (post-#702) — verified at HEAD `65e6d44`

1. Effect fence loses a reserve + `read_output` returns `None` → `runtime_tool_dispatcher.py:965` raises `EffectFenceAmbiguousUncommittedError(idempotency_key=...)`.
2. `workflow_driver.py:2372-2409` name-matches it (harness-cp cannot import harness-runtime — the `HITLPauseRequestedSignal` precedent); when `ctx.pause_resume_protocol` is bound → `capture_pause_snapshot(pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS)` → `RunResult(status=PAUSED, pause_snapshot=...)` + a CP→IS `PAUSE_CAPTURED` ledger entry (`event_kind_index=3`). Unbound → generic FAILED.
3. The captured `PauseSnapshot` carries the position (`step_index`) but **NOT** the fence claim's `idempotency_key`. A naive `api.resume` re-enters the step → re-dispatch → `try_reserve` returns `False` (claim still held) + `read_output` still `None` → re-raises → identical re-PAUSE. **INERT** (not a busy-loop: resume is caller-initiated, no auto-resume daemon).

## 2. The vetted design — thread the claim key into the snapshot; deliver a resolution via `resume_context`; three dispatcher branches

**Channel (all committed-primitive composition; mirrors the `run_engine_class` hash-inert context channel from #689 DURABLE-AUTO + the HITL-response `resume_context` delivery from v1.16 §26.8):**

```
operator → api.resume(resume_context=ResumeContext(effect_fence_resolution=<R>))
  → driver reads resume_context, sets a hash-inert StepExecutionContext.effect_fence_resolution
  → dispatcher re-enters the fenced step → branches on the resolution at the fence gate
```

**(a) `PauseSnapshot` carries the claim key (additive carrier — the fan-out-carrier precedent).** Add `effect_fence_resume: EffectFenceResumeState | None = None` (default-None, `extra="forbid"`-safe, COVERED by `_compute_snapshot_hash` for integrity exactly like `fan_out_resume`/`handoff_resume`/etc.). `EffectFenceResumeState` carries the `idempotency_key` (already in hand at the driver branch as `exc.idempotency_key`). NEVER co-set with the four fan-out resume carriers (an effect-fence pause is a linear/TOOL_STEP pause). This is the linear analogue of the fan-out resume carriers.

**(b) `ResumeContext` carries the resolution directive (additive field — v1.16 §26.8.1 explicitly anticipated extension: "future arcs may extend").** Add `effect_fence_resolution: EffectFenceResolution | None = None` where `EffectFenceResolution` is a 3-value enum `SKIP_AS_FIRED` / `RE_FIRE` / `ABORT`. `None` → no resolution supplied → the current INERT re-pause is PRESERVED (the pinning test stays valid for the no-resolution case). The enum homes in **harness-cp** (CP owns `ResumeContext` + `PauseSnapshot`; harness-runtime imports harness-cp — the dependency direction that forces the driver name-match is `cp ↛ runtime`, so `runtime → cp` is allowed and the dispatcher imports the enum).

**(c) Delivery to the dispatcher.** `api.resume` already delivers `resume_context` one-shot to the resumed step (`api.py:917` `mcp_server._state["_resume_context"]`). The driver, on the resumed fenced step, reads `resume_context.effect_fence_resolution` and sets a NEW hash-inert `StepExecutionContext.effect_fence_resolution` field (the `run_engine_class` precedent — a hash-inert context field set by the driver, NOT a `StepDispatcher` Protocol-signature change). `None` on every non-resume / non-fence dispatch (safe default).

**(d) Dispatcher branches at the fence gate (`runtime_tool_dispatcher.py:927-965`, the `try_reserve`-False arm).** Read `step_context.effect_fence_resolution`. **Key-bound + consume-once (correctness-by-construction, advisor):** apply a resolution ONLY when the dispatch's recomputed `idempotency_key` matches `pause_snapshot.effect_fence_resume.idempotency_key` (the key already carried on the snapshot), then consume it (the resolution is one-shot — it does not bleed to a later fenced step). In today's linear/TOOL_STEP scope a stale resolution cannot reach a second fenced step (linear execution has one uncommitted step at a time), so this is NOT a live double-fire guard — it is nearly-free defense-in-depth using data already in hand, and it makes "one-shot" correct-by-construction rather than correct-because-execution-is-linear (the fan-out carriers share the same `PauseSnapshot`, so the moment the ambiguous route extends past linear a bare unbound enum becomes unsafe). Branches:
- **`RE_FIRE`** → BEFORE `try_reserve`: `self._effect_fence.clear_claim(idempotency_key)` (NEW — atomic `os.unlink` of the `<digest>.claim` + `<digest>.output` files, the inverse of `try_reserve`, missing-ok) → then `try_reserve` wins → fires fresh through the normal step-7 `call_tool` path (+ the normal post-fire `capture_output` + success-path emission).
- **`SKIP_AS_FIRED`** → on the lost-reserve + no-output arm, instead of raising: return a fired-no-output success wrapper (`response={}`) — byte-shaped like a normal success return (`tool_id` / `idempotency_key` / `trust_decision_reason` / `sandbox_tier` recomputed this dispatch) + the balancing `sandbox.exit` (the #702 suppress-path precedent). The step accumulates no output keys (the existing empty-output path).
- **`ABORT`** → raise a NEW terminal `EffectFenceAbortedError` (or reuse the ambiguous error with an abort marker) the driver maps to FAILED (the existing generic FAILED path). Composes the existing FAILED mapping — no new fail-class taxonomy needed beyond a distinct fail_class string.
- **No resolution (`None`)** → the existing `EffectFenceAmbiguousUncommittedError` raise (INERT re-pause preserved).

## 3. The invariant (the at-most-once guarantee, preserved)

The decline-mirror (#701) transferred: **auto-proceed ONLY on proof-of-completion; everything else fails to the operator.** This arc does NOT auto-proceed — every resolution is an explicit operator assertion delivered through `resume_context`:
- `RE_FIRE` fires exactly once *fresh* (the prior attempt provably did not commit — else the step would be prefix-skipped on resume and never re-reach the sink; the operator asserts it did not fire) → at-most-once from true state.
- `SKIP_AS_FIRED` never re-fires (the operator asserts it already fired; the lost output is gone).
- `ABORT` never re-fires.
- A naive resume (no resolution) still never auto-re-fires (INERT re-pause).
- A resolution is **key-bound + consumed once** (§2d): it acts only on the dispatch whose recomputed key matches the snapshot's `effect_fence_resume.idempotency_key`, so it can never mis-apply to a different fenced effect. 

**The one window to verify at build:** between `clear_claim` and the fresh `try_reserve`+fire, a concurrent same-key dispatch (cross-host) could double-claim. But resume is caller-initiated + single-run-at-a-time (`ConcurrentRunNotSupported`, `api.py:781-782`); the cross-host AUTO-recovery story (`F-CC` fenced lease) is a separate registered arc. Within the single-host single-run resume model, `clear_claim`→`try_reserve` is sequential. Document the cross-host residual; do not solve it here.

## 4. Impl surfaces (the build's file map)

| Surface | Change |
|---|---|
| `harness-cp/.../pause_resume_protocol_types.py` | NEW `EffectFenceResolution` enum (SKIP_AS_FIRED / RE_FIRE / ABORT); NEW `EffectFenceResumeState` (carries `idempotency_key`); `PauseSnapshot.effect_fence_resume: EffectFenceResumeState \| None = None` (additive, hash-covered); `ResumeContext.effect_fence_resolution: EffectFenceResolution \| None = None` (additive) |
| `harness-cp/.../workflow_driver.py` | at the §26.2 pause-capture branch (2372-2409): populate `effect_fence_resume` from `exc.idempotency_key`; on the resumed fenced step, set `StepExecutionContext.effect_fence_resolution` from `resume_context`; ABORT → FAILED mapping |
| `harness-runtime/.../lifecycle/effect_fence.py` | NEW `clear_claim(idempotency_key)` (atomic unlink of `<digest>.claim` + `<digest>.output`, missing-ok) on `EffectFenceProtocol` + `RuntimeEffectFence` |
| `harness-runtime/.../lifecycle/runtime_tool_dispatcher.py` | the three resolution branches at the fence gate (read `step_context.effect_fence_resolution`) |
| `harness-runtime/.../types.py` (or the StepExecutionContext home) | NEW hash-inert `StepExecutionContext.effect_fence_resolution` field |
| `harness-runtime/.../api.py` | thread `resume_context.effect_fence_resolution` to the resumed step (the existing `_resume_context` delivery already carries it; verify the driver reads it) |
| `design-substrate/Spec_Harness_Runtime_v1.md` | NEW §14.22.9 (resume-side resolution; the three branches + `clear_claim`) — a v1.72→v1.73 delta |
| `design-substrate/Spec_Control_Plane_v1_52.md` | §26.8 `ResumeContext.effect_fence_resolution` + `EffectFenceResolution` enum + §26.2 `PauseSnapshot.effect_fence_resume` carrier — a v1.51→v1.52 delta |
| clearance markers | runtime + CP, per §4.5 |

**Scope discipline (mirror #702):** **No new §5.2-hash change** (the resume resolution is operator input + the snapshot carrier rides `_compute_snapshot_hash`, not the IS state-ledger six-field hash → IS spec UNCHANGED). **No `StepDispatcher` Protocol widening** (the resolution rides a hash-inert `StepExecutionContext` field, the `run_engine_class` precedent). **No new CXA edge** (re-fire's fresh success re-uses the existing CP→IS success seam; the pause/resume seam is unchanged). **AS / OD / ADR specs UNCHANGED. CXA v2.20 UNCHANGED.** The one genuinely-new code is `clear_claim` + the three branches + the additive types.

## 5. Build plan + witnesses (fresh context) — `[[full-chain-witness-not-half-proofs]]`

By-execution witnesses (the safety-load-bearing set, no proxy — through the real `api.resume` + the real `RuntimeToolDispatcher`):
- **RE_FIRE fires fresh, exactly once:** a fenced step paused ambiguous → `api.resume(resume_context=RE_FIRE)` → the counting tool fires (the claim was cleared) AND fires ONLY once (a second resume without re-pause does not double-fire) → the step completes normally.
- **RE_FIRE's `clear_claim` removed the REAL held claim (not a fresh-key no-op):** assert the `<digest>.claim` file existed before resume and is absent after `clear_claim` — "fires fresh" alone would pass even if the resumed key diverged and the clear was a no-op (the #702 durable-restart suppress witness already implies key-preservation holds, but witness the removal explicitly).
- **ABORT leaves the claim untouched:** ABORT → terminal FAILED, the `<digest>.claim` file is NOT cleaned up (a future run derives a disjoint key namespace — the U-RT-123 run-scoping lesson — so clear-on-abort is unnecessary; pre-empt anyone adding it).
- **SKIP_AS_FIRED proceeds with empty output, NEVER re-fires:** paused ambiguous → `api.resume(resume_context=SKIP_AS_FIRED)` → the counting tool fires ZERO times → the step yields `{}` → the workflow proceeds → `sandbox.exit` balances (no `mcp.tool.call` span).
- **ABORT → FAILED:** paused ambiguous → `api.resume(resume_context=ABORT)` → `RunStatus.FAILED`, tool fires zero times.
- **No-resolution re-pause preserved (the #702 pinning test stays green):** `api.resume` with no `effect_fence_resolution` → identical re-PAUSE, tool fires zero times.
- **durable across restart:** `clear_claim` + the carrier survive a fresh-bootstrap resume (the durable-store `resume_handle` path).
- **carrier integrity:** the `effect_fence_resume` carrier is COVERED by `_compute_snapshot_hash` (a tampered carrier → corruption FAILED); NEVER co-set with the four fan-out carriers (cardinality/exclusivity test).
- advisor (the reframe + the at-most-once-preservation + the cross-host residual scoping) + out-of-family Codex pre-merge.

## 6. Authority chain

FULL-SPEC directive (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]` — registered → build, back-flow pre-authorized) + the §26.2 / §14.22.8 spec text naming this follow-on + the advisor's decorrelated reframe (the operator-answers-the-fence's-question in-domain reading; the #529 `cascade-cancel` out-of-domain precedent). NO operator gate (the reframe dissolved it; the palette composes committed primitives). Grounding verified at HEAD `65e6d44`: `effect_fence.py` (no `clear_claim` yet; `try_reserve`/`capture_output`/`read_output` @188-289); `runtime_tool_dispatcher.py` fence gate @923-965; `workflow_driver.py` §26.2 branch @2372-2409; `pause_resume_protocol_types.py` `PauseSnapshot` @403 + `ResumeContext` @565; `api.resume` @707 + `_resume_context` delivery @917; pinning test `test_ambiguous_pause_resume_re_pauses_until_resolution_follow_on`.

`[[durable-recovery-presence-validity-scope]]` · `[[gate-enforcement-site-and-timing-asymmetry]]` (decline-mirror) · `[[grounding-reveals-claude-closeable-slice-close-honestly]]` (label-flip; tenth variant) · `[[disposition-label-is-a-claim-verify-against-spec]]` · `[[full-chain-witness-not-half-proofs]]`.
