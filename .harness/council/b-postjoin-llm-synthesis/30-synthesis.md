# Council synthesis — `B-POSTJOIN-LLM-SYNTHESIS` (R-FS-1 arc-a)

*Dyadic C1 ⊥ C9 council (genuine dedicated-agent voices, independent → cross-read) + §10.9 probe-first resolution. Inputs: `10-c1-orchestration.md`, `20-c9-reliability-recovery.md`, shared briefing `00-shared-briefing.md`. Probe by the orchestrator against `harness-cp/src/harness_cp/workflow_driver.py` + the arc-ledger.*

## CCR (slim)

**Touched:** orchestration/topology (C1 — canonical orchestrator-synthesizes completion), reliability/replay/determinism (C9 — §25.12 sacrifice + resume reproducibility + hash-chain honesty). **Not-touched (`n/a`):** security/blast-radius (C10), HITL-placement (C11), cost (one extra dispatch, pre-checked + bounded), eval-ability (C8), context-engineering (C2) — none gate the determinism-sacrifice decision.

## Convergence (both voices, independently)

1. **Model synthesis as a dedicated opt-in terminal STEP, never a "fold-mode."** C1: `StepKind.POST_JOIN_SYNTHESIS` "over a strategy flag, for clean non-determinism localization." C9: "a terminal `INFERENCE_STEP`-shaped activity, never a fold-mode" so it inherits the step entry + `response_hash` + audit/disclosure machinery. **Same shape from both axes.**
2. **Recording + consumer ship together** (constraint #1). Re-open the §14.21 concurrent-fan-out sibling-output recording at the barrier drain AND ship the synthesis step that consumes it (reads all siblings, branch-index-ordered) in the SAME arc — clearing the §14.21.5 non-vacuity bar that sank #705 (HOLLOW). Full-chain witness through the real provider, no proxy.
3. **Sacrifice bounded to §25.12 Point 2 (aggregator purity) only.** Point 1 (append order + branch-index ordering) is PRESERVED — the synthesis reads the SAME deterministically-ordered sibling set the fold reads. Order-invariance + step-confinement hold.
4. **Default byte-identical** — absent the opt-in synthesis step, `_aggregate_orchestrator_workers` / `_aggregate_parallelization` stay verbatim (the negative control).
5. **The hash chain never lied + no new hash-chained IS field.** C9 explicit: the §6/§5.2 chain never attested cross-replay reproducibility; tamper-evidence is fully preserved. Disclosure rides the self-disclosing step entry + an emitted trace event — NOT a new IS field (C3/IS territory; out of scope).

## The genuine tension (named, not collapsed)

> **Resume behavior of the synthesized terminal step: cached-replay (C9) vs re-dispatch-with-disclosure (C1).**

- **C1** — re-dispatch-with-disclosure: a post-join synthesis is just another step-confined `INFERENCE_STEP`; the chain is *already* non-byte-identical across replay (cleared §25.12-pt-1 precedent), so a resumed synthesis may differ — disclosed, store-less, lighter. Accepts divergent resume.
- **C9** — cached-replay floor: a *terminal aggregate* deserves stronger attestation than a mid-chain step; capture the synthesis output durably (§14.23 `EngineOutputStore` RESERVE-before-COMMIT) so a resumed run rehydrates the SAME synthesis, divergence foreclosed by the existing fail-closed-on-identity/skew gates. Will NOT accept *silent* divergence.

Both voices independently named THIS as the fault line (strong signal it is the real one, not a manufactured one).

## §10.9 probe → RESOLUTION (`surfaced + probe-resolved`)

Probe against `harness_cp.workflow_driver` + the arc-ledger (file:line in the briefing's grounding table):

1. **`EngineOutputStore` is opt-in AND engine-class-gated to `EVENT_SOURCED_REPLAY` + `WAL_SEGMENT`** (`workflow_driver.py:686-688`; `_IN_SCOPE` set `:221-232`). `ctx.engine_output_store is None` unless `engine_output_replay=True`. So C9's "cached-replay" is NOT free-where-available — it requires the operator to be on a replay-capable engine class AND opted in.
2. **The fan-out aggregate is a driver-level `DriverStrategy` fold producing `RunResult.final_state`** (`:138-158, :380`), NOT a step in the §25.3 inline loop. So a post-join synthesis does NOT auto-inherit the per-step `EngineOutputStore.record` call (that fires in the linear per-step path, `:688`). Capturing the *driver-level* synthesis output durably is a NEW producer site — a separate surface.
3. **B-FANOUT-PAUSE family is COMPLETE** (arc-ledger `:341-533`): fan-out resume **skips terminal branches + recovers their outputs** (`:1593-1594, :1690-1718`, `fan_out_resume` / `peer_fan_out_resume`). So on resume the synthesis CONSUMER already has its sibling-output inputs — but the **synthesis output itself is not cached**, so a re-reached synthesis **re-dispatches**.

**Resolution (advisor-corrected path analysis — the divergence window is currently EMPTY).** Walking every wired path against the code corrects the residual from "post-pause may differ" to a forward-looking concern:

- **Normal completion:** synthesis dispatches once at the barrier drain (`drain_branch_buffers:878`), terminal → `final_state:380`. No resume.
- **Pause-resume (B-FANOUT-PAUSE, all engine classes):** a pause during the fan-out resumes *before* the post-barrier synthesis — fan-out resume skips terminal branches + recovers their outputs (`:1593-1594,1690-1718`), completes the rest, THEN synthesis runs **fresh-once** (never committed pre-pause). **No divergence.**
- **Crash, any engine class:** the 5 non-linear strategies are **resume-blind for EVERY in-scope engine class** (`:215-218`); `_rehydrate_inter_step_channel_on_replay` is `SINGLE_THREADED_LINEAR`-only (`:818,1814,2001`). A crashed fan-out restarts fresh / fails — no completed-synthesis replay. **No divergence-from-prior.**

So **in the currently-wired harness there is NO divergence window** — synthesis is always a fresh first-and-only dispatch. The reproducibility concern is **forward-looking**: it materializes ONLY if a future arc lifts non-linear resume-blindness (wires fan-out crash-replay rehydration under `EVENT_SOURCED_REPLAY`/`WAL_SEGMENT`) AND that rehydration skips the branch prefix but re-dispatches the uncaptured driver-level synthesis. C9's floor is fully honored as the interim guarantee — **make it LOUD + replay-detectable**: the synthesis step self-discloses (own step entry, marked synthesis/non-reproducible) + an emitted trace event, so IF such a path is ever wired the non-reproducibility is already declared, never silent. C9's reproducible cached-replay (capture the driver-level synthesis output under replay-capable classes) is the **registered follow-on**, NOT arc-a (over-excavation, constraint #2 — closing a currently-empty window).

Two supporting facts (advisor): the synthesis is a **read-only compose** (model call, no external effect) ⇒ re-dispatch on any resume path is at-most-once-safe / no double-effect (the impl arc MUST keep it effect-free). Arc-a is **top-level-post-join-ONLY** — `HIERARCHICAL_DELEGATION` reuses ORCHESTRATOR_WORKERS per level (`:144-146`); synthesis-per-level (a child synthesis feeding the parent, no longer terminal) is a registered follow-on, not arc-a.

## Operator-ratifiable residual (the focused gate)

The operator consciously accepts **ONE bounded, forward-looking residual**: *the post-join LLM synthesis makes the §25.12-Point-2 aggregate non-deterministic, so should a future fan-out-crash-replay-rehydration arc ever land, a replayed synthesized run could re-dispatch to a different aggregate — disclosed (step entry + trace event + §25.12 contract caveat), replay-detectable, never silent — until the registered cached-replay follow-on lands.* In the CURRENTLY-wired harness there is no divergence window; the non-opted default fold is byte-identical + fully reproducible.

The AUQ choice: **(A)** accept the forward-looking residual with loud disclosure + register reproducible cached-replay as the follow-on — *recommended (the divergence window is currently empty; matches the existing non-linear resume-blind posture; minimal)*; vs **(B)** gate the synthesis step to replay-capable engine classes only AND build the cached-replay capture now (reproducible resume guaranteed, but larger scope + over-excavates the §14.23 fan-out extension into arc-a to close a currently-empty window).

## Scope discipline (over-excavation foreclosed)

In scope: the opt-in `POST_JOIN_SYNTHESIS` terminal step + re-opened §14.21 concurrent-fan-out recording + §25.12 Point-2 amendment + loud disclosure + default-byte-identical negative control. **Out of scope (registered, not built):** cached-replay reproducible-resume capture; configurable reducers / synthesis-over-arbitrary-strategies / reducer DSL; operator-supplied prompt templating beyond the minimal synthesis dispatch.
