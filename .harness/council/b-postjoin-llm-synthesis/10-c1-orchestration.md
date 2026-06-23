# C1 — Orchestration position: `B-POSTJOIN-LLM-SYNTHESIS`

*Voice C1 (Orchestration & Control Architect). Dyadic council C1 ⊥ C9. Written independently before reading `20-c9-reliability-recovery.md`. All cites ground byte-exact against the grounding table.*

---

## 1. Position

C1 selects the canonical **orchestrator-workers "orchestrator synthesizes" pattern** (research §2.1; the Anthropic named pattern this harness already claims via `TopologyPattern.ORCHESTRATOR_WORKERS`). The deterministic fold the driver ships today is a *structural* fold, not a synthesis: `_aggregate_orchestrator_workers` (`harness-cp/src/harness_cp/workflow_driver.py:5011-5035`) returns `{"orchestrator": ..., "worker_outputs": {step_id: output, ...}}` — it concatenates the branch-index-ordered worker set, it does not *compose* a result. Its own docstring names the gap verbatim (`workflow_driver.py:5021-5023`): *"there is NO second 'compose' dispatch (that would need the deferred inter-step DATA flow, B-INTERSTEP)."* The pattern's defining capability — an orchestrator that reads its workers' outputs and emits a synthesized result — is the post-join LLM dispatch that the cleared spec (`Spec_Control_Plane_v1_32.md:66`: *"orchestrator composes the final result"*) describes but the impl omits. C1's stake: **complete the named pattern.** A capability gap this central to a 6-class topology enum is not a polish item; it is the difference between `ORCHESTRATOR_WORKERS` and a fan-out-with-a-staple.

## 2. The tension, named from C1's side

C1 defends **synthesis-capability completeness**; C9 defends **replay/resume integrity**. We diverge on what a *replayed* synthesized run must reproduce.

C9's instinct will be the safe floor: cache the synthesis output durably (the `EngineOutputStore` RESERVE-before-COMMIT shape, runtime spec §14.23.5, `Spec_Harness_Runtime_v1.md:158`) and **cached-replay** it so a resumed run reproduces the original terminal `final_state` byte-identical, fail-closed on any store↔ledger skew. That accepts *zero* reproducibility cost — and it is exactly why C1 must not open there: a zero-cost floor leaves the operator gate empty (primary-collapse, §10.9).

**C1's floor is re-dispatch-with-disclosure, and it is grounded in already-cleared text.** §25.12 determinism-boundary point 1 (`Spec_Control_Plane_v1_32.md:82`) already concedes: *"the chain is NOT byte-identical across replay: a replay re-runs non-deterministic `INFERENCE_STEP`s → different `response_hash` → a different chain. Non-determinism stays confined inside the step."* A post-join synthesis **is just another `INFERENCE_STEP`.** So the synthesis introduces **no new class of non-determinism** — it *relocates* non-determinism from "forbidden in the fold" (§25.12-pt-2) to "confined in a step" (§25.12-pt-1, which the spec already sanctions). State the sacrifice precisely so it is LOUD, not a shrug:

| §25.12 guarantee | Disposition under post-join synthesis |
|---|---|
| **pt-2 *purity*** — "aggregation is a pure function of the ordered result set" | **SACRIFICED** (opt-in only). The synthesis is an LLM call; its output is not a pure function of the branch outputs. This is the committed-decision sacrifice the operator gate ratifies. |
| **pt-2 *order-invariance*** — "first to finish wins is forbidden; lowest branch-index on tie" | **PRESERVED.** The synthesis reads the **branch-index-ordered** sibling set (never completion order); a slower worker cannot reorder the synthesis input. |
| **pt-1 *step-confinement*** — "non-determinism stays confined inside the step" | **PRESERVED + EXTENDED** to a terminal synthesis step. |

The reproducibility cost C1 explicitly accepts: **a replayed synthesis may differ from the original** (the pt-1 precedent, extended to a terminal step). C1 argues that is *already the chain's posture* for every `INFERENCE_STEP`; mandating byte-reproducibility of the terminal step alone would be an asymmetric heavier bar than the harness applies to any other step. **That is the genuine divergence**: C1 says re-dispatch-and-disclose is consistent with the cleared determinism boundary; C9 will say a terminal aggregate deserves a stronger attestation than a mid-chain step. Both are defensible — which is why it is the operator's call, not ours.

C1 **defers to C9** (FM-B / T-perm-3, the permanent C1↔C9 seam — flagged explicitly): the replay *mechanics* (re-dispatch vs cached-replay vs fail-closed), and **what the §5.2 hash attests**. C1 owns *that* a terminal synthesis step and its ledger entry exist and that the entry is flagged non-deterministic; C9 + IS/C7 own the hash recipe and disclosure *schema*.

## 3. Concrete mechanism

**Opt-in shape — a new `StepKind.POST_JOIN_SYNTHESIS`, not a strategy-internal flag.** C1 selects the StepKind over a `synthesize: bool` dispatch flag on the fan-out strategies. Rationale: making the synthesis structurally a *step* makes "it's just a confined `INFERENCE_STEP`" (§2 above) *literally* true — the non-determinism localizes to **one flagged ledger entry + one span**, which is precisely what makes the disclosure auditable and the default fold provably untouched. Trade-off surfaced, not resolved (C1 does not pick the operating point unilaterally): a StepKind is a heavier contract surface than a flag (a new `StepKind` enum member + admissibility). C1's recommendation is the StepKind *because the LOUD-disclosure constraint #4 is worth the heavier surface*; the operator may down-scope to a flag.

**Scope floor (constraint #2 — no over-excavation):** the synthesis step composes **only** over the concurrent fan-out strategies the v1.74 note names — `ORCHESTRATOR_WORKERS` / `PARALLELIZATION` / `HIERARCHICAL_DELEGATION` (`Spec_Harness_Runtime_v1.md:7`). **NO** configurable reducers, **NO** synthesis-over-arbitrary-strategies, **NO** operator-supplied reducer DSL. One deferred capability, built.

**Recording + consumer ship together (constraint #1 — the #705 hollow trap). Two halves, one arc:**

1. **Recording (re-open `B-INTERSTEP-NONLINEAR`).** At the barrier drain, each completed sibling is recorded into the inter-step channel in **branch-index order**. The producer site is `_aggregate_orchestrator_workers`'s already-sorted `collected` set (`workflow_driver.py:5031`, `sorted_items = sorted(collected.items(), ...)`) — drained alongside `drain_branch_buffers` (`workflow_driver.py:878`). This is the concurrent-fan-out sibling recording that `inter_step_output_channel.py:54-58` registered as forward-but-unbuilt. The channel is already per-run isolated and crash-correct (v1.64, `RunScopedInterStepOutputChannel`), so recording rides built substrate.
2. **Consumer (the synthesis step).** The `POST_JOIN_SYNTHESIS` step reads **all** recorded siblings via `outputs_by_step_id()` (`inter_step_output_channel.py:126-132`) — **not** `most_recent_output()` (`:119`), which returns only the immediately-prior step and is the wrong contract for a fan-in. The step dispatches one LLM call over the branch-index-ordered sibling map and returns the synthesized terminal output.

**Full-chain witness (no proxy):** real workers fan out → each recorded into the channel at the drain → the synthesis step reads the recorded sibling map → a **real provider** `client.messages.create(...)` (the §14.21 v1.59 non-vacuity bar, `Spec_Harness_Runtime_v1.md:228`) → terminal `RunResult.final_state`. This clears the §14.21.5 invariant-6 non-vacuity bar that sank #705 — the recording has a non-vacuous consumer *in the same arc*.

**Handoff contract (C1 owns the contract shape; C5 owns payload validation):** the fan-in handoff payload is the **branch-index-ordered sibling-output map** (`Mapping[step_id, output]` from `outputs_by_step_id()`); control-transfer mode is **synchronous one-shot** (the synthesis is dispatched once at the barrier, post-drain). **Termination:** the synthesis step is terminal-by-construction — **one dispatch, no loop, no iteration cap needed** (it is not an evaluator-optimizer loop; it is a single fan-in compose). The fold output stops being the terminal `RunResult`; the synthesis output becomes it.

**Replay / resume behavior (C1's floor; mechanism deferred to C9):** on resume, the recorded siblings are durable inputs and the synthesis **re-dispatches** over them → a possibly-different terminal output, **disclosed via the flagged ledger entry**. C1 names the honest asymmetry so it survives adversarial review: re-dispatch is lighter on a fresh run but **requires fan-out sibling rehydration on resume** — a registered-forward residual (`inter_step_output_channel.py:59-66`; runtime §14.23.7 "non-linear resume-blind strategies", `Spec_Harness_Runtime_v1.md:159`). C9's alternative — also cache the **synthesis output** via the `EngineOutputStore` RESERVE-before-COMMIT discipline (`Spec_Harness_Runtime_v1.md:149`, store-write BEFORE ledger-append; fail-closed on store↔ledger skew / body-change identity, `:158`) — is more self-contained on resume but heavier and attests a `final_state` the operator may not need reproduced. **C1 does NOT hand-wave "replay will handle it"** — the concrete fork is named (re-dispatch vs cached-output-replay), grounded in the §14.23 precedent, and routed to C9 for the mechanism + to the operator for the floor.

**Hash-chain + audit disclosure (C1 owns existence; IS/C7 own schema):** the synthesis step's completion produces a ledger entry like any step (the existing CP→IS success seam, no new edge). C1's non-negotiable is that the entry/span is **explicitly flagged `non_deterministic_aggregate`** (or the IS/OD-canonical equivalent), so a replay/audit consumer is never silently misled into reading the terminal `final_state` as reproducible (constraint #4). The §5.2 four-component recipe (`Spec_Information_Substrate_v1.md:42`) feeding the six-field hash is IS-owned; C1 defers *what the hash attests* to C9 + IS, and surfaces only that the disclosure marker MUST exist on the entry the synthesis produces.

## 4. Non-negotiables (C1's orchestration floor)

1. **Default fold byte-identical (constraint #3, negative control).** Absent the opt-in, `_aggregate_orchestrator_workers` (`workflow_driver.py:5011`) and `_aggregate_parallelization` (`:3372`) stay **verbatim**. Pinned by an explicit negative-control test.
2. **Order-invariance preserved.** The synthesis reads the **branch-index-ordered** sibling set; "first to finish wins" stays forbidden (`Spec_Control_Plane_v1_32.md:83`). A synthesis that read completion-order siblings would re-introduce the exact non-determinism §25.12 forecloses — that is the one thing C1 will not concede even under opt-in.
3. **Recording + consumer in ONE arc.** No recording-only landing (rebuilds #705 hollow); no synthesis-on-a-recording-that-doesn't-exist (builds on sand). Full-chain witness through the real provider, no proxy.
4. **Disclosure marker mandatory.** The synthesized terminal entry/span carries an explicit non-determinism flag. No silent non-determinism.
5. **Scope = the spec-deferred capability only.** Post-join LLM synthesis over the named concurrent strategies. No reducer DSL, no arbitrary-strategy synthesis.

## 5. Open questions for operator ratification

1. **The ratifiable residual (the real gate):** must a post-join synthesis **mandate durable output capture** (C9's `EngineOutputStore` cached-replay — audit-reproducible terminal `final_state`, heavier, self-contained on resume), or may it run **store-less with re-dispatch-on-resume** (C1's floor — lighter, terminal output non-reproducible-but-disclosed, requires the registered fan-out sibling-rehydration arc to be resume-correct)? This is the C1⊥C9 divergence the operator consciously accepts.
2. **StepKind vs flag:** accept the heavier `StepKind.POST_JOIN_SYNTHESIS` contract surface (cleaner non-determinism localization + audit) or the lighter strategy-internal `synthesize` flag?
3. **Deferred to owner voices (named, not specified by C1):** the synthesis model binding/selection (C6); pre-output HITL placement on the synthesized terminal result (C1 owns *placement* — recommend a checkpoint slot pre-terminal-return; C11 owns the primitive); the §5.2 hash recipe + disclosure-marker schema (IS/C7/C9).

---

### Cross-cutting pre-check (C1 standing obligation)

- **Reliability & failure containment (C9, T-perm-3):** the synthesis is a single dispatch at the barrier; failure mode = the synthesis LLM call fails → the step FAILs like any `INFERENCE_STEP` (the fold result is NOT silently substituted — a failed synthesis is a failed run, with the salvaged sibling set available as `partial_state`, mirroring the B-FANOUT-PAUSE `partial_state` shape at `workflow_driver.py:5503`). Replay mechanics deferred to C9.
- **Token economy & cost (joint C2/C4/C6):** the synthesis adds **+1 LLM dispatch** per fan-out run (the orchestrator-synthesis call). Opt-in, so the cost is incurred only when the operator enables it. Surfaced, not optimized.
- **Observability (C7):** the synthesis creates **one new instrumentation point** — a terminal synthesis span carrying the non-determinism marker. C7 owns the span schema; C1 surfaces that the point exists so it is not reverse-engineered from prose.
