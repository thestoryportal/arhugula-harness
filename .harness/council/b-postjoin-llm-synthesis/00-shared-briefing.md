# Council briefing — `B-POSTJOIN-LLM-SYNTHESIS` (R-FS-1 arc-a) design pass

*Shared grounding for the C1 ⊥ C9 dyadic council. Each voice writes its position INDEPENDENTLY (do not read the sibling's file before writing your own), then cross-reads. Probe-first per §10.9: ground every cite byte-exact against the files named below before asserting.*

## The decision

The operator AUTHORIZED (2026-06-22, PR #707) building `B-POSTJOIN-LLM-SYNTHESIS` — an **opt-in LLM-dispatched synthesis step that runs after a concurrent fan-out** (ORCHESTRATOR_WORKERS / PARALLELIZATION / HIERARCHICAL_DELEGATION) completes: it reads the sibling worker outputs and composes a synthesized result via a model call (the canonical orchestrator-workers "orchestrator synthesizes" shape the current deterministic fold omits). The council's job: **design the safest/cleanest amendment mechanism + surface the genuine cross-domain tension** for a focused operator ratification — NOT decide whether to build (already authorized).

## The committed invariant being amended

**C-CP-25 §25.12 deterministic composition** — the aggregation is a PURE function of the branch-index-ordered worker set (`_aggregate_orchestrator_workers` / `_aggregate_parallelization`; "first-to-finish-wins is forbidden"). An LLM synthesis makes the COMPOSITION **non-deterministic**. That is the committed decision being sacrificed (opt-in), and the reason this is an operator-gated amendment, not impl-to-cleared-spec.

## The genuine tension to force (do NOT collapse to "opt-in, default byte-identical")

Both voices will instantly agree the mechanism is opt-in and the default deterministic fold stays byte-identical. **That agreement is NOT the council's value — it is primary-collapse (§10.9).** The load-bearing, genuinely-contended question is:

> **What is the replay / hash-chain / audit / resume treatment of a NON-DETERMINISTIC aggregate?**

A synthesized fan-out output is no longer a pure function of branch-ordered inputs. So:
- What does a **RESUMED / replayed** run do when the terminal step was an LLM synthesis? (re-dispatch the model → a *different* synthesis? replay a cached output? fail-closed?)
- Is the synthesized output **hash-chained** into the C-IS-05 §5.2 state ledger, and if so what does the hash attest (the inputs? the output? both)?
- How is the non-determinism **disclosed** in the audit ledger so a replay/audit consumer is not silently misled into thinking the aggregate is reproducible?

C1 (orchestration / canonical-synthesis capability-completeness) and C9 (reliability-recovery / determinism / replay-integrity / resume) genuinely diverge HERE. Name your position on THIS, with a concrete mechanism, not a posture.

## Four hard constraints (from advisor red-team — treat as requirements, not suggestions)

1. **Recording + consumer MUST ship together (highest-risk trap).** #705 resolved `B-INTERSTEP-NONLINEAR` as HOLLOW *precisely because the §14.21 concurrent-fan-out recording had no non-vacuous consumer.* Arc-a IS that consumer. The design cannot be "add a synthesis step" — it must **re-open the §14.21 concurrent-fan-out sibling-output recording AND ship it together with the synthesis step that reads it**, with a full-chain witness (no proxy) proving the step actually consumes the recorded sibling outputs. Recording-only, or synthesis-on-a-recording-that-doesn't-exist, rebuilds the hollow trap or builds on sand.
2. **Over-excavation discipline (#705's other lesson).** Design ONLY the spec-deferred capability — the post-join LLM synthesis step — NOT every expressible variant (configurable reducers, synthesis-over-arbitrary-strategies, operator-supplied reducer DSLs, etc.). FULL-SPEC = build what the spec DEFERS, not every monotone extension.
3. **Default path byte-identical + monotone.** Absent the opt-in, the deterministic fold (`_aggregate_orchestrator_workers` / `_aggregate_parallelization`) stays verbatim — the negative control the closure plan demands.
4. **Make the non-determinism LOUD, never silent.** The replay/audit caveat (a synthesized aggregate is not a pure function of inputs) must be explicit in the contract + surfaced in replay/hash semantics, never an unstated side-effect.

## Grounding (read these byte-exact before asserting — cite file:line)

| Surface | Where |
|---|---|
| Deterministic fold (the invariant) | `harness-cp/src/harness_cp/workflow_driver.py` — `_aggregate_orchestrator_workers` (~:815-890), `_aggregate_parallelization`, fan-out+aggregation (~:1668), the B-INTERSTEP registered-build-arc comment (~:1799) |
| C-CP-25 §25.11/§25.12 contract | `design-substrate/Spec_Control_Plane_v1_52.md` (head; C-CP-25 §25.x — regenerate-with-feedback + deterministic composition) |
| §14.21 `InterStepOutputChannel` (C-RT-34) — BUILT, per-run isolated (v1.64) | `harness-runtime/src/harness_runtime/lifecycle/inter_step_output_channel.py`; `design-substrate/Spec_Harness_Runtime_v1.md` §14.21.1-.7 |
| §14.23 `EngineOutputStore` (C-RT-32) — durable replay store, RESERVE-before-COMMIT, fail-closed | `design-substrate/Spec_Harness_Runtime_v1.md` §14.23 (lineage v1.63/v1.65/v1.74) |
| #705 HOLLOW resolution + B-POSTJOIN registration | `design-substrate/Spec_Harness_Runtime_v1.md` §14.21.5 inv-4 / §14.21.7 (v1.74 status posture, lines ~5-9) |
| §5.2 hash-chain (6-field state-ledger entries) | IS spec `design-substrate/Spec_Information_Substrate_v1.md` §5.2 |
| Replay (§14.23) + resume | `design-substrate/Spec_Harness_Runtime_v1.md` §14.23.x |
| Closure plan arc-a | `.harness/r-fs-1-final-closure-plan.md` "Arc (a) — B-POSTJOIN-LLM-SYNTHESIS" |

## Output contract (each voice)

Write to your assigned file (`10-c1-orchestration.md` or `20-c9-reliability-recovery.md`). Structure:
1. **Position** (2-4 sentences) — your axis's stake in this amendment.
2. **The tension, named from your side** — what you defend, what you concede, where you genuinely diverge from the other voice on the replay/hash/audit question.
3. **Concrete mechanism proposal** — opt-in shape (new StepKind? post-join dispatch flag on the fan-out strategies?), what gets recorded, the replay/resume behavior, the hash-chain treatment, the audit disclosure. Cite file:line.
4. **Non-negotiables** — what the mechanism MUST guarantee for your axis (the floor you will not concede).
5. **Open questions for operator ratification** — the specific residual the operator must consciously accept.

### What BAD output looks like (avoid)
- Collapsing to "make it opt-in, default byte-identical, done" — that is the primary-collapse failure; the operator gate would have nothing real to ratify.
- Designing configurable reducers / synthesis-over-arbitrary-strategies / a reducer DSL — over-excavation.
- Hand-waving the replay/resume behavior ("replay will handle it") — name the concrete mechanism (re-dispatch vs cached-replay vs fail-closed) with the §14.23 `EngineOutputStore` precedent.
- Asserting a cite you did not open (phantom §-cite). Ground byte-exact.
- Recording-only design with no consumer wired (the #705 hollow trap).
